"""Splits test: dsh_bench.splits and every benchmarks/*/splits*.json.

1. stratified_split on made-up groups: deterministic for a seed, every group cut 60/20/20 (val and test rounded),
   pinned tasks kept where they were pinned, a different seed gives a different split.
2. Each committed split file (benchmarks/*/splits*.json): no task in two splits or twice, counts match, each group
   within one task of the file's ratios, trainval = train + val, and `python3 -m dsh_bench.splits FILE --check` passes;
   each named subset resolves by name and holds no val/test task, and --check refuses one that does.

    python3 tests/test_splits.py
"""

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.splits import NAMES, entries, quotas, stratified_split  # noqa: E402


def main() -> int:
    checks = []
    groups = {f"g{g}-t{i:03d}": f"g{g}" for g, n in ((1, 160), (2, 37), (3, 11)) for i in range(n)}
    a, b = stratified_split(groups, 7), stratified_split(groups, 7)
    c = stratified_split(groups, 8)
    per = defaultdict(Counter)
    for task, split in a.items():
        per[groups[task]][split] += 1
    checks += [
        ("same seed, same split", a == b),
        ("other seed, other split", a != c),
        ("every task assigned once", set(a) == set(groups)),
        ("each group cut at its 60/20/20 quotas",
         all(per[g] == Counter(quotas(sum(per[g].values()), {"train": .6, "val": .2, "test": .2})) for g in per)),
    ]
    pinned = {"g1-t000": "test", "g1-t001": "test", "g2-t005": "val"}
    d = stratified_split(groups, 7, fixed=pinned)
    per_d = defaultdict(Counter)
    for task, split in d.items():
        per_d[groups[task]][split] += 1
    checks += [("pinned tasks keep their split", all(d[t] == s for t, s in pinned.items())),
               ("quotas still met with pinned tasks", per_d == per)]

    files = sorted(REPO.glob("benchmarks/*/splits*.json"))
    checks.append(("at least one benchmark has a split file", bool(files)))
    for path in files:
        data = json.loads(path.read_text())
        name = f"{path.parent.name}/{path.name}"
        seen = Counter(e["task_id"] for n in NAMES for e in data["splits"][n])
        field = data.get("group_by")
        by_group = defaultdict(Counter)
        for n in NAMES:
            for e in data["splits"][n]:
                by_group[e.get(field)][n] += 1
        balanced = all(abs(by_group[g][n] - quotas(sum(by_group[g].values()), data["ratios"])[n]) <= 1
                       for g in by_group for n in NAMES)
        cli = subprocess.run([sys.executable, "-m", "dsh_bench.splits", str(path), "--check"], cwd=REPO,
                             capture_output=True, text=True)
        checks += [
            (f"{name}: no task twice or in two splits", all(v == 1 for v in seen.values())),
            (f"{name}: counts match ({len(seen)} tasks)", data["counts"]["total"] == len(seen)
             and all(data["counts"][n] == len(data["splits"][n]) for n in NAMES)),
            (f"{name}: every {field} within one task of its ratios", balanced),
            (f"{name}: trainval = train + val", [e["task_id"] for e in entries(path, "trainval")]
             == [e["task_id"] for e in data["splits"]["train"] + data["splits"]["val"]]),
            (f"{name}: --check passes", cli.returncode == 0),
        ]
        for sub, body in data.get("subsets", {}).items():
            held = {e["task_id"] for n in ("val", "test") for e in data["splits"][n]}
            checks += [(f"{name}: subset {sub} resolves by name, no val/test task",
                        [e["task_id"] for e in entries(path, sub)] == [e["task_id"] for e in body["entries"]]
                        and not held & {e["task_id"] for e in body["entries"]})]
    # --check refuses a subset that holds a held-out task
    import tempfile
    sample = json.loads((REPO / "benchmarks/harvey/splits-ahe-80-20-70.json").read_text())
    sample["subsets"] = {"bad": {"entries": [sample["splits"]["test"][0]]}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(sample, f)
    bad = subprocess.run([sys.executable, "-m", "dsh_bench.splits", f.name, "--check"], cwd=REPO, capture_output=True, text=True)
    checks.append(("--check refuses a subset holding a test task", bad.returncode == 1 and "is a test task" in bad.stdout))
    width = max(len(n) for n, _ in checks)
    for n, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{width}}")
    failed = [n for n, ok in checks if not ok]
    print(f"{len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
