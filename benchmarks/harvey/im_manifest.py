"""Build an invariant_mining manifest from Harvey runs graded in a baseline file (benchmarks/*/baselines/*.json).

    python3 benchmarks/harvey/im_manifest.py --baseline B.json --splits S.json --subset flip --out manifest.json

For every task of the subset: one trajectory per baseline run (label pass = all-pass in that run), P1/P2 = the first two
passing runs in run order; the other passing runs earn support points, the failing runs importance points
(docs/2same-invariant-algo/DESIGN.md). Tasks with fewer than two passing runs are skipped (and listed).
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True, help="baseline JSON with 'runs' (run dirs) and per-task 'runN' verdicts")
    ap.add_argument("--splits", type=Path, help="splits JSON holding the subset")
    ap.add_argument("--subset", help="named subset in the splits file (subsets.<name>)")
    ap.add_argument("--tasks", nargs="*", help="task ids instead of a subset")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    base = json.loads(a.baseline.read_text())
    if a.subset:
        sub = json.loads(a.splits.read_text())["subsets"][a.subset]
        task_ids = [e["task_id"] for e in sub.get("entries") or sub.get("tasks")]
    else:
        task_ids = a.tasks
    runs = base["runs"]
    trajectories, tasks, skipped = [], [], []
    for tid in task_ids:
        row = base["tasks"][tid]
        ids = []
        for n, run in enumerate(runs, 1):
            verdict = row[f"run{n}"]["all_pass"]
            logs = sorted((Path(run) / "tasks" / tid.replace("/", "__") / "dsh-home").rglob("session.v2.jsonl"))
            if len(logs) != 1:
                raise SystemExit(f"{tid} run {n}: expected one session log, found {len(logs)}")
            traj_id = f"{tid}#run{n}"
            trajectories.append({"id": traj_id, "task_id": tid, "label": "pass" if verdict else "fail",
                                 "session_log": str(logs[0]), "run": run})
            if verdict:
                ids.append(traj_id)
        if len(ids) < 2:
            skipped.append(tid)
            continue
        tasks.append({"task_id": tid, "p1": ids[0], "p2": ids[1]})
    manifest = {"source": {"baseline": str(a.baseline), "splits": str(a.splits) if a.splits else None, "subset": a.subset},
                "trajectories": [t for t in trajectories if t["task_id"] not in skipped], "tasks": tasks}
    a.out.write_text(json.dumps(manifest, indent=1))
    print(f"{a.out}: {len(tasks)} tasks, {len(manifest['trajectories'])} trajectories" + (f"; skipped (fewer than two passes): {skipped}" if skipped else ""))


if __name__ == "__main__":
    main()
