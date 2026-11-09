"""Train / val / test splits of a benchmark's tasks, shared by everyone working on the harness.

A benchmark keeps its split in `benchmarks/<name>/splits.json`; the task ids written there are the split (a seed is
recorded only to say how the file was made). Format:

    {"benchmark": ..., "description": ..., "seed": int, "ratios": {"train": 0.6, "val": 0.2, "test": 0.2},
     "group_by": "the field the split is stratified on", "counts": {...},
     "splits": {"train": [{"task_id": ..., <group field>: ..., ...}], "val": [...], "test": [...]}}

Split names: train, val, test, and trainval = train + val (for work with only a train and a test set: train on
trainval, report on test).

    python3 -m dsh_bench.splits benchmarks/<name>/splits.json test        # task ids, one per line
    python3 -m dsh_bench.splits benchmarks/<name>/splits.json --check     # disjoint, counts by group

`stratified_split` makes such a split: within each group (e.g. a job or practice area) the tasks, in sorted order, are
shuffled with random.Random(seed) and cut 60/20/20 (val and test rounded, train the rest); `fixed` pins some tasks to a
split beforehand (to align with another version of the same benchmark) and the rest fill each group's quotas.
"""

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

NAMES = ("train", "val", "test")
DEFAULT_RATIOS = {"train": 0.6, "val": 0.2, "test": 0.2}


def entries(path: Path, name: str) -> list[dict]:
    """The split's entries (dicts with at least task_id); `trainval` is train followed by val."""
    data = json.loads(Path(path).read_text())
    if name == "trainval":
        return data["splits"]["train"] + data["splits"]["val"]
    if name not in NAMES:
        raise SystemExit(f"split {name!r}: choose one of {', '.join(NAMES)}, trainval")
    return data["splits"][name]


def task_ids(path: Path, name: str) -> list[str]:
    return [e["task_id"] for e in entries(path, name)]


def quotas(n: int, ratios: dict) -> dict[str, int]:
    val, test = round(n * ratios["val"]), round(n * ratios["test"])
    return {"train": n - val - test, "val": val, "test": test}


def stratified_split(groups: dict[str, str], seed: int, ratios: dict = DEFAULT_RATIOS,
                     fixed: dict[str, str] | None = None) -> dict[str, str]:
    """task id -> split. groups: task id -> group. fixed: task id -> split, kept as given."""
    fixed = fixed or {}
    rng = random.Random(seed)
    by_group = defaultdict(list)
    for task, group in groups.items():
        by_group[group].append(task)
    out = {}
    for group in sorted(by_group):
        tasks = sorted(by_group[group])
        want = quotas(len(tasks), ratios)
        for task in tasks:
            if task in fixed:
                out[task] = fixed[task]
                want[fixed[task]] -= 1
        free = [t for t in tasks if t not in fixed]
        rng.shuffle(free)
        if any(v < 0 for v in want.values()):  # pinned tasks overfill a split: the rest go where room is left
            want = {k: max(v, 0) for k, v in want.items()}
            extra = len(free) - sum(want.values())
            want["train"] += extra
        cursor = 0
        for name in ("val", "test", "train"):
            for task in free[cursor:cursor + want[name]]:
                out[task] = name
            cursor += want[name]
        for task in free[cursor:]:
            out[task] = "train"
    return out


def check(path: Path) -> list[str]:
    """Problems with a split file (empty list: fine): duplicates, overlaps, and the counts by group."""
    data = json.loads(Path(path).read_text())
    problems, seen = [], Counter()
    for name in NAMES:
        for e in data["splits"][name]:
            seen[e["task_id"]] += 1
    problems += [f"task in more than one split or twice: {t}" for t, c in seen.items() if c > 1]
    counts = {name: len(data["splits"][name]) for name in NAMES}
    if data.get("counts", {}).get("total") not in (None, sum(counts.values())):
        problems.append(f"counts.total {data['counts']['total']} != {sum(counts.values())}")
    return problems


def summary(path: Path) -> str:
    data = json.loads(Path(path).read_text())
    field = data.get("group_by")
    lines = [f"{data.get('benchmark')}: " + ", ".join(f"{n} {len(data['splits'][n])}" for n in NAMES)
             + f" (total {sum(len(data['splits'][n]) for n in NAMES)})"]
    if field:
        table = defaultdict(Counter)
        for name in NAMES:
            for e in data["splits"][name]:
                table[e.get(field)][name] += 1
        for group in sorted(table, key=str):
            c = table[group]
            lines.append(f"  {group}: " + " / ".join(str(c[n]) for n in NAMES))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path)
    parser.add_argument("name", nargs="?", help="train, val, test or trainval: print its task ids")
    parser.add_argument("--check", action="store_true", help="check the file and print the counts by group")
    args = parser.parse_args()
    if args.check or not args.name:
        problems = check(args.path)
        print(summary(args.path))
        for p in problems:
            print("PROBLEM:", p)
        return 1 if problems else 0
    print("\n".join(task_ids(args.path, args.name)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
