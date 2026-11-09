"""Gold check for APEX-Agents 1.1: the experts' own outputs must pass, graded exactly like an agent run.

    python3 benchmarks/apex-agents/check_gold.py --out runs/apex11-gold [--per-type 1] [--tasks SLUG ...]

Per task: Mercor's world boots as in run_task.py (same image, mounts, initial snapshot); the task's golden files
(tests/golden/filesystem/...) are copied into /filesystem as an agent would leave them (then Mercor's
fix_permissions.sh); Mercor's collect script takes the final snapshot; the trajectory's final answer is the expert's
(solution/answer.txt). Then grade.py grades it (snapshots kept). Every criterion should be met: a failure points at
the grading path (judge, relay, extraction, snapshots) or at the judge's own error rate. --per-type N picks N tasks of
each expected output type (default 1: 6 tasks); --tasks names them.
"""

import argparse
import collections
import json
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import grade  # noqa: E402
import run_task  # noqa: E402
from dsh_bench.endpoints import load_local_env  # noqa: E402


def pick(tasks_dir: Path, per_type: int) -> list[str]:
    by_type = collections.defaultdict(list)
    for d in sorted(tasks_dir.iterdir()):
        by_type[tomllib.loads((d / "task.toml").read_text())["metadata"]["expected_output"]].append(d.name)
    return [slug for _, slugs in sorted(by_type.items()) for slug in slugs[:per_type]]


def gold_run(tasks_dir: Path, slug: str, out: Path) -> dict:
    task = run_task.load_task(tasks_dir, slug)
    out.mkdir(parents=True)
    logs = out / "world-logs"
    logs.mkdir()
    container = f"apex11-gold-{slug[:24]}-{uuid.uuid4().hex[:6]}"
    meta = task["meta"]
    record = {"task": slug, "tasks_dir": str(tasks_dir), "task_id": meta["task_id"], "domain": meta["domain"],
              "expected_output": meta["expected_output"], "container": container, "gold": True,
              "finish_reason": "completed", "graded_ending": True}
    try:
        run_task.sh(run_task.world_argv(task, container, logs), timeout=300)
        record["boot_s"] = run_task.wait_ready(task, container)
        golden = task["dir"] / "tests/golden/filesystem"
        if golden.is_dir():
            files = sorted(str(p.relative_to(golden)) for p in golden.rglob("*") if p.is_file())
            pack = subprocess.run(["tar", "-C", str(golden), "-cf", "-", *files], capture_output=True, check=True).stdout
            run_task.sh([run_task.RUNTIME, "exec", "-i", container, "tar", "--no-same-owner", "-C", "/filesystem", "-xf", "-"], input=pack)
            run_task.sh([run_task.RUNTIME, "exec", container, "/app/tools/fix_permissions.sh"])
            record["golden_files"] = files
        run_task.final_snapshot(container)
        answer = (task["dir"] / "solution/answer.txt").read_text().strip()
        trajectory = {"schema_version": "ATIF-v1.5", "session_id": "gold", "agent": {"name": "gold", "version": "1"},
                      "steps": [{"step_id": 1, "source": "system", "message": run_task.SYSTEM_PROMPT},
                                {"step_id": 2, "source": "user", "message": task["instruction"]},
                                {"step_id": 3, "source": "agent", "message": answer}],
                      "final_metrics": {"total_steps": 3}, "extra": {"native_status": "completed"}}
        (out / "trajectory.json").write_text(json.dumps(trajectory, indent=2) + "\n")
    except run_task.InfraError as error:
        record["infra_error"] = str(error)
    finally:
        subprocess.run([run_task.RUNTIME, "rm", "-f", "-t", "5", container], capture_output=True)
        (out / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tasks-dir", type=Path, default=run_task.TASKS_DIR)
    parser.add_argument("--per-type", type=int, default=1)
    parser.add_argument("--tasks", nargs="*")
    args = parser.parse_args()
    load_local_env()
    slugs = args.tasks or pick(args.tasks_dir, args.per_type)
    results = []
    for slug in slugs:
        record = gold_run(args.tasks_dir.resolve(), slug, args.out.resolve() / slug)
        g = grade.grade_task(args.out.resolve() / slug, keep_snapshots=True)
        met = sum((c.get("score") or 0) >= 1.0 for c in g.get("criteria") or [])
        results.append((slug, record["expected_output"], met, len(g.get("criteria") or []), g.get("error")))
        print(f"{slug}: {record['expected_output']}: {met}/{len(g.get('criteria') or [])} criteria met"
              f"{'; error: ' + str(g.get('error')) if g.get('error') else ''}", flush=True)
    total_met = sum(r[2] for r in results)
    total = sum(r[3] for r in results)
    print(f"gold: {sum(r[2] == r[3] and r[3] > 0 for r in results)}/{len(results)} tasks all met, "
          f"{total_met}/{total} criteria met")
    return 0 if total_met == total and total > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
