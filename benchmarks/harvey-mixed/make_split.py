"""Split the harvey-mixed sample into 150 train and 50 test tasks (user, 2026-11-15).

    python3 benchmarks/harvey-mixed/make_split.py [--test 50] [--seed 20261115]

Stratified by practice area, like the sample: each area's share of the 50 test tasks by largest remainder over its
size in the sample, drawn from the area's sorted task ids with random.Random(seed); the rest are train. No val split.
Writes splits-150-50.json in dsh_bench.splits format (group_by area); `make_specs.py --tasks mixed:train` (or :test).
"""

import argparse
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20261115)
    args = parser.parse_args()
    sample = json.loads((HERE / "sample-200.json").read_text())
    entries = sample["tasks"]
    n = len(entries)
    by_area: dict[str, list[dict]] = {}
    for e in entries:
        by_area.setdefault(e["area"], []).append(e)
    share = {a: args.test * len(v) / n for a, v in by_area.items()}
    quota = {a: int(s) for a, s in share.items()}
    for a in sorted(share, key=lambda a: (-(share[a] - quota[a]), a))[:args.test - sum(quota.values())]:
        quota[a] += 1
    rng = random.Random(args.seed)
    test_ids = set()
    for a in sorted(by_area):
        ids = sorted(e["task_id"] for e in by_area[a])
        rng.shuffle(ids)
        test_ids |= set(ids[:quota[a]])
    keep = ("task_id", "area", "n_criteria", "task_json_sha256")
    split = {"train": [{k: e[k] for k in keep} for e in entries if e["task_id"] not in test_ids],
             "val": [],
             "test": [{k: e[k] for k in keep} for e in entries if e["task_id"] in test_ids]}
    data = {
        "benchmark": "harvey-mixed",
        "description": f"The {n}-task harvey-mixed sample split {n - args.test} train / {args.test} test, stratified by "
                       "practice area (largest remainder); no val. Train and test both cover the areas in proportion.",
        "seed": args.seed,
        "ratios": {"train": (n - args.test) / n, "val": 0.0, "test": args.test / n},
        "group_by": "area",
        "method": "benchmarks/harvey-mixed/make_split.py",
        "source": "benchmarks/harvey-mixed/sample-200.json",
        "counts": {"total": n, **{k: len(v) for k, v in split.items()},
                   "test_by_area": dict(sorted(Counter(e["area"] for e in split["test"]).items())),
                   "criteria": {k: sum(e["n_criteria"] for e in v) for k, v in split.items()}},
        "splits": split,
    }
    (HERE / f"splits-{n - args.test}-{args.test}.json").write_text(json.dumps(data, indent=1) + "\n")
    print({k: len(v) for k, v in split.items()}, "criteria", data["counts"]["criteria"])
    print("test by area:", data["counts"]["test_by_area"])


if __name__ == "__main__":
    main()
