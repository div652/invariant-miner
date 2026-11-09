"""Write the train / val / test splits (60/20/20) of APEX-Agents 1.0 and 1.1, aligned with each other.

    python3 benchmarks/apex-agents/make_splits.py [--dataset ~/apex-agents-data]
        [--v11-tasks ~/apex-agents-1.1-hub/apex-agents-1-1] [--v11-out benchmarks/apex-agents-1.1/splits.json]

Maintainers only: the files are committed. Writes benchmarks/apex-agents/splits.json (1.0, 480 tasks) and, with
--v11-out, the 1.1 split (240 tasks, its benchmark directory is on the 1.1 branch).

- 1.1: stratified by job (Investment Banking, Law, Management Consulting: 80 each): within each job the task slugs,
  sorted, are shuffled with random.Random(SEED) and cut 48/16/16 (dsh_bench.splits.stratified_split).
- 1.0: aligned with 1.1. 239 of the 240 1.1 tasks are 1.0 tasks under new ids (matched by task name; prompts and
  rubrics often edited), and each of those 1.0 tasks gets its 1.1 task's split, so a task tuned on in one version is
  never tested on in the other. The other 241 1.0 tasks are shuffled the same way and fill each job to 96/32/32.

Use: `run_all.py --tasks split:train` (or val, test, trainval = train + val) in either benchmark directory.
"""

import argparse
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.splits import DEFAULT_RATIOS, NAMES, stratified_split  # noqa: E402

SEED = 20261109


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def counts(rows: dict, assignment: dict) -> dict:
    return {"total": len(rows), **{n: sum(1 for t in rows if assignment[t] == n) for n in NAMES},
            "domains": {d: dict(Counter(assignment[t] for t in rows if rows[t]["domain"] == d))
                        for d in sorted({r["domain"] for r in rows.values()})}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", type=Path, default=Path.home() / "apex-agents-data")
    parser.add_argument("--v11-tasks", type=Path, default=Path.home() / "apex-agents-1.1-hub/apex-agents-1-1")
    parser.add_argument("--v11-out", type=Path, default=None)
    args = parser.parse_args()

    v1 = {t["task_id"]: {"task_id": t["task_id"], "task_name": t["task_name"], "domain": t["domain"],
                         "world_id": t["world_id"], "expected_output": t["expected_output"], "in_v11": None}
          for t in json.loads((args.dataset / "tasks_and_rubrics.json").read_text())}
    v11 = {}
    for d in sorted(p for p in args.v11_tasks.iterdir() if p.is_dir()):
        meta = tomllib.loads((d / "task.toml").read_text())["metadata"]
        name = json.loads((d / "tests/grading_config.json").read_text())["metadata"]["task_name"]
        v11[d.name] = {"task_id": d.name, "mercor_task_id": meta["task_id"], "task_name": name,
                       "domain": meta["domain"], "expected_output": meta["expected_output"], "v1_task_id": None}
    if len(v1) != 480 or len(v11) != 240:
        raise SystemExit(f"expected 480 and 240 tasks, found {len(v1)} and {len(v11)}")

    by_name = {}
    for t, row in v1.items():
        by_name.setdefault(norm(row["task_name"]), []).append(t)
    for slug, row in v11.items():
        match = by_name.get(norm(row["task_name"]), [])
        if len(match) == 1:
            if v1[match[0]]["domain"] != row["domain"]:
                raise SystemExit(f"{slug}: domain differs from its 1.0 task {match[0]}")
            row["v1_task_id"] = match[0]
            v1[match[0]]["in_v11"] = slug

    a11 = stratified_split({s: r["domain"] for s, r in v11.items()}, SEED)
    fixed = {r["v1_task_id"]: a11[s] for s, r in v11.items() if r["v1_task_id"]}
    a1 = stratified_split({t: r["domain"] for t, r in v1.items()}, SEED, fixed=fixed)

    common = {"seed": SEED, "ratios": DEFAULT_RATIOS, "group_by": "domain"}
    data1 = {"benchmark": "apex-agents",
             "description": "APEX-Agents 1.0 (HF mercor/apex-agents, 480 tasks), 60/20/20 by job; aligned with the 1.1 "
                            "split: a 1.0 task kept in 1.1 (in_v11) is in the same split there",
             **common, "method": "benchmarks/apex-agents/make_splits.py", "counts": counts(v1, a1),
             "splits": {n: [v1[t] for t in sorted(v1) if a1[t] == n] for n in NAMES}}
    (HERE / "splits.json").write_text(json.dumps(data1, indent=1) + "\n")
    print("1.0:", {n: data1["counts"][n] for n in NAMES}, data1["counts"]["domains"])
    if args.v11_out:
        data11 = {"benchmark": "apex-agents-1.1",
                  "description": "APEX-Agents 1.1.1 (Harbor Hub mercor/apex-agents-1-1@1.1.1, 240 tasks; task_id is "
                                 "the task directory), 60/20/20 by job; the 1.0 split follows this one (v1_task_id)",
                  **common, "method": "benchmarks/apex-agents/make_splits.py", "counts": counts(v11, a11),
                  "splits": {n: [v11[s] for s in sorted(v11) if a11[s] == n] for n in NAMES}}
        args.v11_out.write_text(json.dumps(data11, indent=1) + "\n")
        print("1.1:", {n: data11["counts"][n] for n in NAMES}, data11["counts"]["domains"])
    moved = sum(1 for s, r in v11.items() if r["v1_task_id"] and a1[r["v1_task_id"]] != a11[s])
    print(f"aligned: {len(fixed)} task pairs, {moved} in different splits")


if __name__ == "__main__":
    main()
