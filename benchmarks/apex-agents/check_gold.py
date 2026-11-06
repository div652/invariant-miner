"""Gold check for the grading pipeline: grade the experts' gold outputs as if an agent had produced them.

    python3 benchmarks/apex-agents/check_gold.py --out runs/gold-check [--per-type 2] [--seed 0] [--jobs 8]

For a sample of tasks (per domain for console answers, per file type for file outputs), builds run directories like
run_task.py's: "before" = the world zip + the task's input files (filesystem/ and .apps_data/), "after" = before plus
the gold files (file tasks), the gold response as the final answer (console tasks; file tasks answer "Done."). Then
grades them with grade.py. The paper reports its judge graded every gold criterion as met; failures here point at the
judge, the grading target or local document extraction (CHECKLIST.md: "check local extraction for errors").
"""

import argparse
import io
import json
import random
import sys
import tarfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grade  # noqa: E402
from run_task import trajectory  # noqa: E402


def snapshot(path: Path, world_zip: Path, overlays: list[Path]) -> None:
    """tar.gz with filesystem/ and .apps_data/ at the top, later overlays replacing earlier files."""
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(world_zip) as zf:
        for name in zf.namelist():
            if not name.endswith("/") and name.split("/")[0] in ("filesystem", ".apps_data"):
                files[name] = zf.read(name)
    for overlay in overlays:
        for source in sorted(overlay.rglob("*")):
            rel = str(source.relative_to(overlay))
            if source.is_file() and rel.split("/")[0] in ("filesystem", ".apps_data"):
                files[rel] = source.read_bytes()
    with tarfile.open(path, "w:gz") as tar:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("~/apex-agents-data"))
    parser.add_argument("--per-type", type=int, default=2)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    dataset = args.dataset.expanduser().resolve()
    tasks = json.loads((dataset / "tasks_and_rubrics.json").read_text())
    worlds = {w["world_id"]: w for w in json.loads((dataset / "world_descriptions.json").read_text())}
    rng = random.Random(args.seed)
    groups: dict[str, list[dict]] = {}
    for t in tasks:
        key = t["domain"] if t["expected_output"] == "message_in_console" else grade.GRADING_TARGET[t["expected_output"]]
        groups.setdefault(key, []).append(t)
    sample = [t for key in sorted(groups) for t in rng.sample(groups[key], min(args.per_type, len(groups[key])))]
    out = args.out.resolve()
    for t in sample:
        run_dir = out / t["task_id"]
        if (run_dir / "run.json").exists():
            continue
        (run_dir / "snapshots").mkdir(parents=True, exist_ok=True)
        (run_dir / "task.json").write_text(json.dumps(t | {"world": worlds[t["world_id"]]}, indent=2) + "\n")
        (run_dir / "run.json").write_text(json.dumps({"task_id": t["task_id"], "finish_reason": "final_answer",
                                                      "gold_check": True}) + "\n")
        world_zip = dataset / "world_files_zipped" / f"{t['world_id']}.zip"
        task_files = dataset / "task_files" / t["task_id"]
        overlays = [task_files] if task_files.is_dir() else []
        snapshot(run_dir / "snapshots/before.tar.gz", world_zip, overlays)
        gold = dataset / "gold_files" / t["task_id"]
        snapshot(run_dir / "snapshots/after.tar.gz", world_zip, overlays + ([gold] if gold.is_dir() else []))
        answer = t["gold_response"] if t["gold_response_type"] == "text" else "Done."
        (run_dir / "trajectory.json").write_text(json.dumps(
            trajectory(t["prompt"], {"finish_reason": "final_answer", "answer": answer}), indent=2) + "\n")
    sys.argv = ["grade.py", str(out), "--jobs", str(args.jobs), "--regrade"]
    grade.main()
    results = [json.loads((out / t["task_id"] / "grading/grades.json").read_text()) for t in sample]
    print()
    for r in results:
        failed = [c["criteria"][:90] for c in r.get("criteria", []) if c["score"] != 1.0]
        print(f"{'PASS' if r.get('all_pass') else 'FAIL'}  {r['task_id']}  {r['expected_output']:<22} "
              f"{r['criteria_count']} criteria  {'; '.join(failed)[:160] or r.get('error', '')}")
    print(f"\ngold all-pass: {sum(bool(r.get('all_pass')) for r in results)}/{len(results)}; "
          f"criteria met: {sum(c['score'] == 1.0 for r in results for c in r.get('criteria', []))}/"
          f"{sum(r['criteria_count'] for r in results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
