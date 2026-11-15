"""Draw the harvey-mixed task sample: 200 Harvey LAB tasks across all practice areas (user, 2026-11-15).

    python3 benchmarks/harvey-mixed/make_sample.py [--n 200] [--seed 20261115]

Pool: every task of the pinned Harvey LAB checkout (work/harvey-labs, 2,010 tasks in 27 practice areas), minus the
firm-knowledge tasks that are held out in the AHE split (its 20 val + 70 test, benchmarks/harvey/splits-ahe-80-20-70.json),
so this set never overlaps the firm-knowledge evaluation tasks. 1,920 tasks.

Draw: random, stratified by practice area (the top folder under tasks/): each area gets its share of the 200 by
largest remainder over the pool sizes, then that many tasks are drawn from the area's sorted task ids with
random.Random(seed). So every area appears, in proportion to its size, and the draw is reproducible.

Writes sample-200.json: per task its id, area, number of criteria, deliverables, number of documents, and the
task.json sha256 (checked by make_specs.py). Plus tasks-200.txt (the ids, one per line).
"""

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAB = REPO / "work/harvey-labs"
AHE = REPO / "benchmarks/harvey/splits-ahe-80-20-70.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20261115)
    args = parser.parse_args()
    held = {e["task_id"] for n in ("val", "test") for e in json.loads(AHE.read_text())["splits"][n]}
    tasks = sorted(str(p.parent.relative_to(LAB / "tasks")) for p in (LAB / "tasks").rglob("task.json"))
    pool = [t for t in tasks if t not in held]
    by_area: dict[str, list[str]] = {}
    for t in pool:
        by_area.setdefault(t.split("/")[0], []).append(t)
    share = {a: args.n * len(ts) / len(pool) for a, ts in by_area.items()}
    quota = {a: int(s) for a, s in share.items()}
    for a in sorted(share, key=lambda a: (-(share[a] - quota[a]), a))[:args.n - sum(quota.values())]:
        quota[a] += 1
    rng = random.Random(args.seed)
    chosen = sorted(t for a in sorted(by_area) for t in rng.sample(sorted(by_area[a]), quota[a]))

    entries = []
    for t in chosen:
        raw = (LAB / "tasks" / t / "task.json").read_bytes()
        task = json.loads(raw)
        docs = (LAB / "tasks" / t / task["docs_dir"]).resolve() if task.get("docs_dir") else LAB / "tasks" / t / "documents"
        entries.append({"task_id": t, "area": t.split("/")[0], "n_criteria": len(task["criteria"]),
                        "deliverables": task.get("deliverables") or [],
                        "n_documents": sum(1 for p in docs.rglob("*") if p.is_file()),
                        "task_json_sha256": hashlib.sha256(raw).hexdigest()})
    commit = (LAB / ".git").exists() and __import__("subprocess").run(
        ["git", "-C", str(LAB), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    data = {
        "benchmark": "harvey-mixed",
        "description": f"{args.n} Harvey LAB tasks drawn at random across all practice areas, stratified by area "
                       "(proportional, largest remainder), from the pinned checkout minus the AHE-held-out "
                       "firm-knowledge tasks (val + test).",
        "lab_commit": commit,
        "seed": args.seed,
        "method": "benchmarks/harvey-mixed/make_sample.py",
        "pool": {"tasks": len(pool), "all_tasks": len(tasks), "excluded_ahe_val_test": len(held)},
        "counts": {"tasks": len(entries), "by_area": dict(sorted(Counter(e["area"] for e in entries).items())),
                   "criteria": sum(e["n_criteria"] for e in entries),
                   "deliverable_types": dict(Counter(Path(str(d)).suffix or str(d) for e in entries
                                                     for d in e["deliverables"]).most_common())},
        "tasks": entries,
    }
    (HERE / f"sample-{args.n}.json").write_text(json.dumps(data, indent=1) + "\n")
    (HERE / f"tasks-{args.n}.txt").write_text("".join(t + "\n" for t in chosen))
    print(f"{len(entries)} tasks from a pool of {len(pool)}; {data['counts']['criteria']} criteria")
    print(data["counts"]["by_area"])
    print(data["counts"]["deliverable_types"])


if __name__ == "__main__":
    main()
