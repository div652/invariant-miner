"""Run many APEX-Agents tasks in parallel and grade each as it finishes.

    python3 benchmarks/apex-agents/run_all.py --tasks all|FILE --out runs/<run> [--jobs 20] [--grade-jobs 6]
        [--endpoint cao | --model models/x.json]

FILE: task ids, one per line. Each task runs with run_task.py into <run>/tasks/<task_id>/ and is then graded with
grade.py (grading/grades.json). A task whose directory already has run.json is not run again (resume after a stop by
re-running the same command; move a broken task directory away to redo it). Tasks of the two banking worlds (Edgar SEC,
FMP) need DSH_BENCH_EDGAR_USER_AGENT and DSH_BENCH_FMP_KEY_FILE in local.env; without them they are skipped and listed
as deferred. At the end, <run>/summary.json and summary.md: Pass@1 (share of tasks whose run met every criterion; one
run per task), mean score, by job and by output type, finish reasons.
"""

import argparse
import concurrent.futures
import json
import os
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
from dsh_bench.endpoints import load_local_env, setting_path  # noqa: E402

BANKING_APPS = {"Edgar SEC", "FMP"}
LOCK = threading.Lock()


def log(run_dir: Path, message: str) -> None:
    line = f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')} {message}"
    with LOCK, (run_dir / "progress.log").open("a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def summarize(run_dir: Path, task_ids: list[str], deferred: list[str]) -> dict:
    rows = []
    for tid in task_ids:
        g = run_dir / "tasks" / tid / "grading/grades.json"
        r = run_dir / "tasks" / tid / "run.json"
        grades = json.loads(g.read_text()) if g.exists() else None
        record = json.loads(r.read_text()) if r.exists() else {}
        rows.append({"task_id": tid, "domain": record.get("domain"), "expected_output": record.get("expected_output"),
                     "finish_reason": record.get("finish_reason"), "graded": bool(grades and grades.get("graded")),
                     "score": (grades or {}).get("score"), "all_pass": bool((grades or {}).get("all_pass")),
                     "error": (grades or {}).get("error") or (grades or {}).get("reason")})
    done = [x for x in rows if x["finish_reason"] is not None]
    scored = [x for x in done if x["score"] is not None]

    def stats(items):
        return {"tasks": len(items), "pass_at_1": round(sum(x["all_pass"] for x in items) / len(items), 4) if items else None,
                "mean_score": round(sum((x["score"] or 0.0) for x in items) / len(items), 4) if items else None}

    by = defaultdict(dict)
    for key in ("domain", "expected_output"):
        groups = defaultdict(list)
        for x in done:
            groups[x[key]].append(x)
        by[key] = {k: stats(v) for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))}
    summary = {"run_dir": str(run_dir), "tasks_requested": len(task_ids), "tasks_finished": len(done),
               "tasks_with_score": len(scored), "deferred": deferred, "overall": stats(done),
               "by_domain": by["domain"], "by_output": by["expected_output"],
               "finish_reasons": dict(Counter(x["finish_reason"] for x in done)),
               "grading_errors": [x["task_id"] for x in done if x["finish_reason"] == "final_answer" and not x["graded"]],
               "rows": rows}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [f"# APEX-Agents run {run_dir.name}", "",
             f"Finished {len(done)}/{len(task_ids)} tasks; deferred {len(deferred)}.", "",
             f"**Pass@1 {summary['overall']['pass_at_1']}**, mean score {summary['overall']['mean_score']} "
             f"(runs that hit a limit count as 0, as in the paper)", "", "| Group | Tasks | Pass@1 | Mean score |",
             "|---|---|---|---|"]
    for key in ("by_domain", "by_output"):
        for k, v in summary[key].items():
            lines.append(f"| {k} | {v['tasks']} | {v['pass_at_1']} | {v['mean_score']} |")
    lines += ["", f"Finish reasons: {summary['finish_reasons']}",
              f"Grading errors: {summary['grading_errors'] or 'none'}"]
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("~/apex-agents-data"))
    parser.add_argument("--jobs", type=int, default=20)
    parser.add_argument("--grade-jobs", type=int, default=6)
    parser.add_argument("--setup-slots", type=int, default=4, help="tasks populating/snapshotting at the same time")
    parser.add_argument("--retries", type=int, default=1, help="reruns of a task that ended without an agent session")
    parser.add_argument("--endpoint")
    parser.add_argument("--model")
    parser.add_argument("--judge", default="gemini-3.8-flash")
    parser.add_argument("--effort", default="low")
    args = parser.parse_args()
    load_local_env()
    dataset = args.dataset.expanduser().resolve()
    tasks = json.loads((dataset / "tasks_and_rubrics.json").read_text())
    worlds = {w["world_id"]: w for w in json.loads((dataset / "world_descriptions.json").read_text())}
    ids = [t["task_id"] for t in tasks] if args.tasks == "all" else \
        [line.strip() for line in Path(args.tasks).read_text().splitlines() if line.strip()]
    by_id = {t["task_id"]: t for t in tasks}
    banking_ready = bool(os.environ.get("DSH_BENCH_EDGAR_USER_AGENT")) and bool(os.environ.get("DSH_BENCH_FMP_KEY_FILE"))
    deferred = [] if banking_ready else [
        tid for tid in ids if BANKING_APPS & {a["service_name"] for a in worlds[by_id[tid]["world_id"]]["apps"]}]
    run_dir = args.out.resolve()
    (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
    (run_dir / "tasks.txt").write_text("\n".join(ids) + "\n")
    # A task directory without run.json is a run that was killed: move it aside and run the task again.
    for tid in ids:
        out = run_dir / "tasks" / tid
        if out.exists() and not (out / "run.json").exists():
            (run_dir / "aborted").mkdir(exist_ok=True)
            out.rename(run_dir / "aborted" / f"{tid}-{int(time.time())}")
    todo = [tid for tid in ids if tid not in deferred and not (run_dir / "tasks" / tid / "run.json").exists()]
    log(run_dir, f"start: {len(ids)} tasks, {len(todo)} to run, {len(deferred)} deferred (banking setup missing), "
                 f"jobs {args.jobs}, model {args.model or args.endpoint or 'default (luna-cao)'}")
    key = Path(setting_path("$DSH_BENCH_CAO_KEY_FILE")).read_text().strip()
    grade_env = grade.judge_env(key)
    graders = concurrent.futures.ThreadPoolExecutor(args.grade_jobs)
    grading = []

    def run_one(tid: str) -> None:
        out = run_dir / "tasks" / tid
        argv = [sys.executable, str(HERE / "run_task.py"), "--task", tid, "--out", str(out), "--dataset", str(dataset),
                "--lock-dir", str(run_dir / ".locks"), "--setup-slots", str(args.setup_slots)]
        argv += ["--endpoint", args.endpoint] if args.endpoint else []
        argv += ["--model", args.model] if args.model else []
        for attempt in range(args.retries + 1):
            t0 = time.monotonic()
            proc = subprocess.run(argv, cwd=REPO, capture_output=True, text=True)
            out.mkdir(parents=True, exist_ok=True)
            (out / "run_task.log").write_text(proc.stdout + proc.stderr)
            record = json.loads((out / "run.json").read_text()) if (out / "run.json").exists() else {}
            log(run_dir, f"ran {tid}: {record.get('finish_reason')} in {time.monotonic() - t0:.0f}s (exit {proc.returncode})"
                         f"{' attempt ' + str(attempt + 1) if attempt else ''}")
            # No agent session (setup or MCP startup failed): infrastructure, not the agent; retry in a fresh directory.
            if record.get("finish_reason") in (None, "no_session") and attempt < args.retries:
                (run_dir / "retried").mkdir(exist_ok=True)
                out.rename(run_dir / "retried" / f"{tid}-{attempt + 1}")
                continue
            break
        if (out / "run.json").exists():
            def grade_one() -> None:
                result = grade.grade_task(out, args.judge, args.effort, grade_env)
                log(run_dir, f"graded {tid}: score {result.get('score')} all_pass {result.get('all_pass')} "
                             f"{result.get('error') or ''}")
            grading.append(graders.submit(grade_one))

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(run_one, todo))
    for future in grading:
        future.result()
    graders.shutdown()
    summary = summarize(run_dir, [tid for tid in ids if tid not in deferred], deferred)
    log(run_dir, f"done: Pass@1 {summary['overall']['pass_at_1']} mean {summary['overall']['mean_score']} "
                 f"over {summary['overall']['tasks']} tasks; grading errors {len(summary['grading_errors'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
