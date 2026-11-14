"""Write the named subset `flip` into the AHE split files: the train tasks whose all-pass flips across main's three
Luna-high base runs (user, 2026-11-13: "ahe:flip").

    python3 benchmarks/harvey/make_flip_subset.py

Train is the 160 of splits-ahe-160-20-70.json (the AHE 80 train tasks + the 80 the AHE split left unused); a task is
in `flip` when it passed all-pass in exactly 1 or 2 of the three runs recorded in
baselines/luna-high-3runs-20261112.json. Those are the 32 tasks of analysis/hv-lunahigh-train80-flip14 (14 from the
AHE train set, 18 added). Val and test tasks can never enter it (dsh_bench.splits --check refuses them).

The subset is written to both files, so `make_specs.py --tasks ahe:flip` and `--tasks ahe160:flip` give the same 32
tasks. Each entry is the task's train entry plus `base_all_pass` (run1, run2, run3) and `base_passes` (1 or 2).
import_ahe_splits.py and make_train160_split.py keep the subsets of the files they rewrite.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE / "baselines/luna-high-3runs-20261112.json"
FILES = [HERE / "splits-ahe-80-20-70.json", HERE / "splits-ahe-160-20-70.json"]


def main() -> None:
    base = json.loads(BASELINE.read_text())["tasks"]
    train = json.loads(FILES[1].read_text())["splits"]["train"]
    entries = []
    for e in train:
        runs = [base[e["task_id"]][r]["all_pass"] for r in ("run1", "run2", "run3")]
        if 0 < sum(runs) < 3:
            entries.append(e | {"base_all_pass": runs, "base_passes": sum(runs)})
    subset = {
        "description": "Train tasks (train 160) whose all-pass flips across the three Luna-high base runs: passed in "
                       "exactly 1 or 2 of 3. Traces and per-task analysis: benchmarks/harvey/analysis/"
                       "hv-lunahigh-train80-flip14/. Derived by make_flip_subset.py (user, 2026-11-13).",
        "derived_from": {"baseline": str(BASELINE.relative_to(HERE.parents[1])), "train": "splits-ahe-160-20-70.json"},
        "counts": {"tasks": len(entries), "pass_once": sum(e["base_passes"] == 1 for e in entries),
                   "pass_twice": sum(e["base_passes"] == 2 for e in entries),
                   "ahe_train": sum(e["train_origin"] == "ahe-train" for e in entries),
                   "ahe_unused": sum(e["train_origin"] == "ahe-unused" for e in entries)},
        "entries": entries,
    }
    for path in FILES:
        data = json.loads(path.read_text())
        data["subsets"] = data.get("subsets", {}) | {"flip": subset}
        path.write_text(json.dumps(data, indent=1) + "\n")
    print(subset["counts"])


if __name__ == "__main__":
    main()
