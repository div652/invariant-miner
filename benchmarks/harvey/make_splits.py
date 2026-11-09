"""Write benchmarks/harvey/splits.json: the train / val / test split (60/20/20) of Harvey LAB's firm-knowledge tasks.

    python3 benchmarks/harvey/make_splits.py            # rewrites splits.json (maintainers only; it is committed)

Firm knowledge only (user, 2026-11-09: Harvey work here is on firm knowledge exclusively): the 250 tasks under
tasks/firm-knowledge, ids sorted, shuffled with random.Random(SEED) and cut 150/50/50 (dsh_bench.splits.stratified_split;
the tasks have no sub-category to stratify on). The rest of Harvey LAB (1,760 tasks in 26 other areas) is not split.
Each entry keeps the task.json's sha256 at the pinned harvey-labs (make_specs.py checks it), so a split can only run
the tasks it was made from.

Use: `make_specs.py --tasks benchmarks/harvey/splits.json:train` (or val, test, trainval = train + val).
"""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.splits import DEFAULT_RATIOS, NAMES, stratified_split  # noqa: E402

LAB = REPO / "work/harvey-labs"
PIN = "4743403"  # harvey-labs commit (CHECKLIST.md)
SEED = 20261109
AREA = "firm-knowledge"


def main() -> None:
    tasks = {}
    for path in sorted((LAB / "tasks").rglob("task.json")):
        task_id = str(path.parent.relative_to(LAB / "tasks"))
        if not task_id.startswith(AREA + "/"):
            continue
        tasks[task_id] = {"task_id": task_id, "area": task_id.split("/")[0],
                          "task_json_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    assignment = stratified_split({t: e["area"] for t, e in tasks.items()}, SEED)
    splits = {name: [tasks[t] for t in sorted(tasks) if assignment[t] == name] for name in NAMES}
    data = {
        "benchmark": "harvey",
        "description": f"Harvey LAB @ {PIN}: the {len(tasks)} {AREA} tasks, 60/20/20",
        "seed": SEED, "ratios": DEFAULT_RATIOS, "group_by": "area",
        "method": "dsh_bench.splits.stratified_split over the firm-knowledge task ids (benchmarks/harvey/make_splits.py)",
        "counts": {"total": len(tasks), **{name: len(splits[name]) for name in NAMES},
                   "areas": {a: dict(Counter(assignment[t] for t in tasks if tasks[t]["area"] == a))
                             for a in sorted({e["area"] for e in tasks.values()})}},
        "splits": splits,
    }
    (HERE / "splits.json").write_text(json.dumps(data, indent=1) + "\n")
    print({name: len(splits[name]) for name in NAMES})


if __name__ == "__main__":
    main()
