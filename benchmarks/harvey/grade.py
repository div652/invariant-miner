"""Grade a dsh-bench Harvey run with Harvey's own grader (lab_core.evaluation, pinned), C0's judge settings.

    work/harvey-labs/.venv/bin/python benchmarks/harvey/grade.py RUN_DIR [--only <task dir name> ...]

For every finished task (RUN_DIR/tasks/<name>/run.json), the regular files of workspace/output are copied to
RUN_DIR/grading/results/<name>/output (symlinks are skipped and listed: an agent could point one at a host file),
then `lab_core.evaluation.run_eval.evaluate_run` grades them against the task's rubric with one judge, exactly as
`python -m lab_core.evaluation.run_eval --judges <judge>` would. Scores: RUN_DIR/grading/scores.json and scores.txt.

Settings to match the reference (C0 in the AHE c23/c24 campaigns), all through CAO (127.0.0.1:4141):
- judge gpt-5.6-sol (Responses API) at reasoning effort high: the upstream judge sends no effort, so the client's
  responses.create gets `reasoning={"effort": ...}` added here;
- deliverable-filename helper claude-sonnet-5 (upstream hard-codes claude-sonnet-4-6 in scoring._LLM_MATCH_MODEL);
- criteria graded 10 at a time; a task with grading errors is graded again (2 attempts).
"""

import argparse
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "work/harvey-labs"
CAO = "http://127.0.0.1:4141"


def stage_outputs(task_dir: Path, results: Path) -> list[str]:
    src, dest = task_dir / "workspace/output", results / "output"
    dest.mkdir(parents=True)
    skipped = []
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if path.is_symlink():
            skipped.append(str(rel))
        elif path.is_dir():
            (dest / rel).mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest / rel)
    return skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--judge", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--helper", default="claude-sonnet-5")
    parser.add_argument("--parallel", type=int, default=10, help="criteria graded at once per task")
    parser.add_argument("--task-workers", type=int, default=2, help="tasks graded at once")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--grading-dir", type=Path)
    args = parser.parse_args()

    run = args.run_dir.resolve()
    grading = (args.grading_dir or run / "grading").resolve()
    if grading.is_relative_to(run / "tasks"):
        raise SystemExit("the grading dir must not be inside a task dir")
    lab_root = grading / "lab-root"
    (lab_root / "results").mkdir(parents=True, exist_ok=True)
    if not (lab_root / "tasks").exists():
        (lab_root / "tasks").symlink_to(LAB / "tasks")
    sys.path.insert(0, str(REPO))
    from dsh_bench.endpoints import setting_path
    key = Path(setting_path("$DSH_BENCH_CAO_KEY_FILE")).read_text().strip()
    os.environ.update(LAB_ROOT=str(lab_root), OPENAI_BASE_URL=f"{CAO}/v1", OPENAI_API_KEY=key,
                      ANTHROPIC_BASE_URL=CAO, ANTHROPIC_API_KEY=key)

    sys.path.insert(0, str(LAB))
    from lab_core.evaluation import run_eval, scoring
    from lab_core.evaluation.judge import Judge

    scoring._LLM_MATCH_MODEL = args.helper

    def make_judge() -> Judge:
        judge = Judge(model=args.judge)
        if judge.provider == "openai" and args.effort:
            create = judge.client.responses.create
            judge.client.responses.create = lambda **kw: create(**kw, reasoning={"effort": args.effort})
        return judge

    tasks, infra = [], []
    for task_dir in sorted((run / "tasks").iterdir()):
        if args.only and task_dir.name not in args.only:
            continue
        if not (task_dir / "run.json").exists():
            print(f"skip (unfinished): {task_dir.name}")
            continue
        finish = json.loads((task_dir / "answer.json").read_text()).get("finish_reason")
        if finish in ("no_session", "incomplete"):
            # DSH never started or never ended a turn: an infrastructure failure, not the agent's 0. Re-run the task.
            infra.append(task_dir.name)
            continue
        tasks.append((task_dir.name, json.loads((task_dir / "spec.json").read_text())["task_id"], task_dir))

    def grade(item: tuple[str, str, Path]) -> dict:
        name, task_id, task_dir = item
        results = lab_root / "results" / name
        if results.exists():
            shutil.rmtree(results)
        skipped = stage_outputs(task_dir, results)
        for attempt in range(1, args.attempts + 1):
            scores = run_eval.evaluate_run(run_id=name, task=task_id, judge=make_judge(), parallel=args.parallel)
            if not scores["n_grading_errors"]:
                break
        row = {k: scores[k] for k in ("task", "all_pass", "n_passed", "n_criteria", "n_grading_errors")}
        row |= {"criterion_pass_rate": scores["n_passed"] / scores["n_criteria"] if scores["n_criteria"] else 0.0,
                "attempts": attempt, "skipped_symlinks": skipped}
        print(f"{task_id:50s} {row['n_passed']:>3}/{row['n_criteria']:<3} all-pass {row['all_pass']}"
              + (f"  grading errors {row['n_grading_errors']}" if row["n_grading_errors"] else ""), flush=True)
        return row

    if infra:
        print(f"NOT GRADED: {len(infra)} tasks where DSH never ran a turn (infrastructure): {', '.join(infra[:10])}")
        if not tasks or len(infra) > len(tasks):
            raise SystemExit("most tasks never ran: fix the run (dsh.stderr) instead of grading it")
    with ThreadPoolExecutor(max_workers=args.task_workers) as pool:
        rows = list(pool.map(grade, tasks))
    rows.sort(key=lambda r: r["task"])
    n = len(rows)
    summary = {
        "tasks": n,
        "all_pass_rate": sum(r["all_pass"] for r in rows) / n if n else 0.0,
        "criterion_pass_rate": sum(r["criterion_pass_rate"] for r in rows) / n if n else 0.0,
        "tasks_with_grading_errors": sum(bool(r["n_grading_errors"]) for r in rows),
        "not_graded_infrastructure": infra,
        "judge": args.judge, "effort": args.effort, "helper": args.helper,
    }
    (grading / "scores.json").write_text(json.dumps({"summary": summary, "tasks": rows}, indent=2) + "\n")
    text = "\n".join(f"{r['task']:50s} {r['n_passed']:>3}/{r['n_criteria']:<3} {'ALL-PASS' if r['all_pass'] else ''}"
                     for r in rows)
    text += (f"\n\n{n} tasks: all-pass {summary['all_pass_rate']:.3f}, mean criterion pass rate "
             f"{summary['criterion_pass_rate']:.3f}, tasks with grading errors {summary['tasks_with_grading_errors']}\n")
    (grading / "scores.txt").write_text(text)
    print(text.split("\n\n")[-1].strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
