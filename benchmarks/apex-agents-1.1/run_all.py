"""Run many APEX-Agents 1.1 tasks in parallel and grade each as it finishes.

    python3 benchmarks/apex-agents-1.1/run_all.py --tasks all|FILE --out runs/<run> [--jobs 12] [--grade-jobs 6]
        [--setup-slots 4] [--endpoint cao | --model models/x.json] [--tasks-dir DIR]

FILE: task slugs (Hub task directory names), one per line. Each task runs with run_task.py into <run>/tasks/<slug>/
and is then graded with grade.py (grading/grades.json). Re-running the same command resumes: tasks with run.json are
not run again; a task directory without run.json (killed) is moved to <run>/aborted/ and run again. A run that failed
outside the agent (world boot, DSH never started, the final snapshot: run.json infra_error or no agent session) is
retried once in a fresh world (the first attempt moved to <run>/retried/). At the end, <run>/summary.json and
summary.md: Pass@1 (share of tasks whose run met every criterion; one run per task), mean score, by job and by output
type, finish reasons, grading errors.
"""

import argparse
import concurrent.futures
import json
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import grade  # noqa: E402
import run_task  # noqa: E402
from dsh_bench.endpoints import load_local_env  # noqa: E402

LOCK = threading.Lock()
ABORT_AFTER = 6


def log(run_dir: Path, message: str) -> None:
    line = f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')} {message}"
    with LOCK, (run_dir / "progress.log").open("a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def summarize(run_dir: Path, slugs: list[str]) -> dict:
    rows = []
    for slug in slugs:
        g = run_dir / "tasks" / slug / "grading/grades.json"
        r = run_dir / "tasks" / slug / "run.json"
        grades = json.loads(g.read_text()) if g.exists() else None
        record = json.loads(r.read_text()) if r.exists() else {}
        rows.append({"task": slug, "domain": record.get("domain"), "expected_output": record.get("expected_output"),
                     "finish_reason": record.get("finish_reason"), "infra_error": bool(record.get("infra_error")),
                     "graded_ending": bool(record.get("graded_ending")), "graded": bool(grades and grades.get("graded")),
                     "score": (grades or {}).get("score"), "all_pass": bool((grades or {}).get("all_pass")),
                     "error": (grades or {}).get("error"), "reason": (grades or {}).get("reason")})
    done = [x for x in rows if x["finish_reason"] is not None or x["infra_error"]]

    def stats(items):
        return {"tasks": len(items), "pass_at_1": round(sum(x["all_pass"] for x in items) / len(items), 4) if items else None,
                "mean_score": round(sum((x["score"] or 0.0) for x in items) / len(items), 4) if items else None}

    by = {}
    for key in ("domain", "expected_output"):
        groups = defaultdict(list)
        for x in done:
            groups[x[key]].append(x)
        by[key] = {k: stats(v) for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))}
    summary = {"run_dir": str(run_dir), "tasks_requested": len(slugs), "tasks_finished": len(done),
               "overall": stats(done), "by_domain": by["domain"], "by_output": by["expected_output"],
               "finish_reasons": dict(Counter(x["finish_reason"] for x in done)),
               "infra_errors": [x["task"] for x in done if x["infra_error"]],
               "grading_errors": [x["task"] for x in done if x["graded_ending"] and not x["infra_error"] and not x["graded"]],
               "rows": rows}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [f"# APEX-Agents 1.1 run {run_dir.name}", "",
             f"Finished {len(done)}/{len(slugs)} tasks.", "",
             f"**Pass@1 {summary['overall']['pass_at_1']}**, mean score {summary['overall']['mean_score']} "
             "(a run stopped by the 3 h timeout or an error scores 0; a run at the step limit is graded, as Mercor's)",
             "", "| Group | Tasks | Pass@1 | Mean score |", "|---|---|---|---|"]
    for key in ("by_domain", "by_output"):
        for k, v in summary[key].items():
            lines.append(f"| {k} | {v['tasks']} | {v['pass_at_1']} | {v['mean_score']} |")
    lines += ["", f"Finish reasons: {summary['finish_reasons']}",
              f"Infrastructure errors: {summary['infra_errors'] or 'none'}",
              f"Grading errors: {summary['grading_errors'] or 'none'}"]
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tasks-dir", type=Path, default=run_task.TASKS_DIR)
    parser.add_argument("--jobs", type=int, default=12)
    parser.add_argument("--grade-jobs", type=int, default=6)
    parser.add_argument("--setup-slots", type=int, default=4, help="worlds booting at the same time")
    parser.add_argument("--retries", type=int, default=1, help="reruns of a task that failed outside the agent")
    parser.add_argument("--endpoint")
    parser.add_argument("--model")
    parser.add_argument("--no-subagents", action="store_true", help="DSH's subagent tools and their guidance off")
    parser.add_argument("--judge", default=grade.JUDGE_MODEL)
    parser.add_argument("--effort", default=grade.JUDGE_EFFORT)
    args = parser.parse_args()
    load_local_env()
    if args.model and not args.model.startswith("{repo}"):
        args.model = str(Path(args.model).resolve())  # run_task.py runs from the repo root
        if not Path(args.model).exists():
            raise SystemExit(f"--model {args.model}: no such file")
    tasks_dir = args.tasks_dir.expanduser().resolve()
    slugs = sorted(d.name for d in tasks_dir.iterdir() if d.is_dir()) if args.tasks == "all" else \
        [line.strip() for line in Path(args.tasks).read_text().splitlines() if line.strip()]
    unknown = [s for s in slugs if not (tasks_dir / s).is_dir()]
    if unknown:
        raise SystemExit(f"not in {tasks_dir}: {unknown[:5]}")
    run_dir = args.out.resolve()
    (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
    (run_dir / "tasks.txt").write_text("\n".join(slugs) + "\n")
    for slug in slugs:  # a directory without run.json is a run that was killed: set it aside, run again
        out = run_dir / "tasks" / slug
        if out.exists() and not (out / "run.json").exists():
            (run_dir / "aborted").mkdir(exist_ok=True)
            out.rename(run_dir / "aborted" / f"{slug}-{int(time.time())}")
    todo = [s for s in slugs if not (run_dir / "tasks" / s / "run.json").exists()]
    log(run_dir, f"start: {len(slugs)} tasks, {len(todo)} to run, jobs {args.jobs}, "
                 f"model {args.model or args.endpoint or 'default (luna-cao)'}, judge {args.judge} {args.effort}, "
                 f"subagents {'off' if args.no_subagents else 'on'}")
    grade.judge_key()  # fail now, not after the first run, if the judge key is missing
    graders = concurrent.futures.ThreadPoolExecutor(args.grade_jobs)
    grading = []
    # Circuit breaker: after ABORT_AFTER tasks in a row that failed outside the agent (even after their retry), start no
    # more tasks; they stay unrun, so re-running the command resumes once the cause is fixed.
    breaker = {"streak": 0, "open": False}

    def run_one(slug: str) -> None:
        if breaker["open"]:
            return
        out = run_dir / "tasks" / slug
        argv = [sys.executable, str(HERE / "run_task.py"), "--task", slug, "--out", str(out), "--tasks-dir", str(tasks_dir),
                "--lock-dir", str(run_dir / ".locks"), "--setup-slots", str(args.setup_slots)]
        argv += ["--endpoint", args.endpoint] if args.endpoint else []
        argv += ["--model", args.model] if args.model else []
        argv += ["--no-subagents"] if args.no_subagents else []
        for attempt in range(args.retries + 1):
            t0 = time.monotonic()
            proc = subprocess.run(argv, cwd=REPO, capture_output=True, text=True)
            out.mkdir(parents=True, exist_ok=True)
            (out / "run_task.log").write_text(proc.stdout + proc.stderr)
            record = json.loads((out / "run.json").read_text()) if (out / "run.json").exists() else {}
            infra = record.get("infra_error")
            log(run_dir, f"ran {slug}: {record.get('finish_reason')} in {time.monotonic() - t0:.0f}s (exit {proc.returncode})"
                         f"{' attempt ' + str(attempt + 1) if attempt else ''}{' INFRA: ' + infra[:300] if infra else ''}")
            if (infra or record.get("finish_reason") in (None, "no_session")) and attempt < args.retries:
                (run_dir / "retried").mkdir(exist_ok=True)
                out.rename(run_dir / "retried" / f"{slug}-{attempt + 1}-{int(time.time())}")
                continue
            break
        with LOCK:
            if record.get("infra_error"):
                breaker["streak"] += 1
                if breaker["streak"] >= ABORT_AFTER and not breaker["open"]:
                    breaker["open"] = True
                    print(f"ABORT: {ABORT_AFTER} tasks in a row failed outside the agent; starting no more", flush=True)
            else:
                breaker["streak"] = 0
        if (out / "run.json").exists():
            def grade_one() -> None:
                try:
                    result = grade.grade_task(out, args.judge, args.effort, tasks_dir=tasks_dir)
                except Exception as error:  # a grading crash must not stop the run or hide the rest
                    log(run_dir, f"graded {slug}: errored (grading crashed: {type(error).__name__}: {str(error)[:300]})")
                    return
                log(run_dir, f"graded {slug}: score {result.get('score')} all_pass {result.get('all_pass')} "
                             f"{result.get('error') or result.get('reason') or ''}")
            grading.append(graders.submit(grade_one))

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(run_one, todo))
    for future in grading:
        future.result()
    graders.shutdown()
    if breaker["open"]:
        log(run_dir, f"ABORTED after {ABORT_AFTER} infrastructure failures in a row; fix the cause and re-run to resume")
    summary = summarize(run_dir, slugs)
    log(run_dir, f"done: Pass@1 {summary['overall']['pass_at_1']} mean {summary['overall']['mean_score']} over "
                 f"{summary['overall']['tasks']} tasks; infra errors {len(summary['infra_errors'])}, "
                 f"grading errors {len(summary['grading_errors'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
