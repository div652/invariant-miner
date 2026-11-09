"""Import the AHE campaigns' Harvey split (80 train / 20 val / 70 test) and its difficulty strata. Maintainers only:
both outputs are committed.

    python3 benchmarks/harvey/import_ahe_splits.py [--ahe ~/AHE_Harvey_cao]

Source: the AHE Harvey project (github.com/div652/evo-harness, harvey-ahe-project/), file
splits-firm-knowledge-c34-80-20-70.json, the split of campaigns 12, 15, 23-27 and 34 (c34: the reference Luna C0).
How AHE made it (scripts/make_splits_firm_knowledge_c12.py and _c15.py there):

1. Difficulty = campaign 9b's result per task (gpt-5.6-sol high, Harvey's own harness, one trial per task): the 250
   firm-knowledge tasks sorted hardest first by (9b all-pass, 9b criterion pass rate, sha256 tie-break), cut into 10
   blocks of 25 (block 0 hardest).
2. Within each block the tasks are ordered by sha256('harvey-lab-campaign-12:assign:' + task id): positions 1-2 test,
   3-4 val, 5-12 train (campaign 12's 80/20/20), 13-17 the 50 extra test tasks of campaign 15, 18-25 unused.
   So every block gives 8 train, 2 val, 7 test, and 8 tasks are left out (80 unused in all).

Writes, with every task.json checked byte-identical at our Harvey pin (work/harvey-labs):
- splits-ahe-80-20-70.json: the split in dsh_bench.splits format, grouped by difficulty_block. Run it with
  `make_specs.py --tasks ahe:train` (val, test; trainval = the 100 train + val tasks, campaign 34's c34-c0-100.txt).
- difficulty-9b.json: the strata for reference, all 250 tasks: 9b values, block, AHE split (or unused), and the
  task's split in our own splits.json.
"""

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.splits import NAMES  # noqa: E402

LAB = REPO / "work/harvey-labs"
SOURCE = "harvey-ahe-project/splits-firm-knowledge-c34-80-20-70.json"
PER_BLOCK = {"train": 8, "val": 2, "test": 7}  # of each block of 25; the other 8 are unused


def ordered(counts: Counter) -> dict:
    return {n: counts[n] for n in (*NAMES, "unused") if counts[n]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ahe", type=Path, default=Path.home() / "AHE_Harvey_cao", help="AHE Harvey checkout")
    args = parser.parse_args()
    src = args.ahe / SOURCE
    raw = src.read_bytes()
    ahe = json.loads(raw)
    commit = subprocess.run(["git", "-C", str(args.ahe), "log", "-1", "--format=%h", "--", SOURCE],
                            capture_output=True, text=True, check=True).stdout.strip()
    strata = ahe["stratification"]["tasks"]
    if len(strata) != 250:
        raise SystemExit(f"expected 250 tasks in the strata, found {len(strata)}")

    split_of, pins = {}, {}
    for ahe_name, name in (("train", "train"), ("validation", "val"), ("test", "test")):
        for e in ahe["splits"][ahe_name]:
            split_of[e["task_id"]] = name
            pins[e["task_id"]] = e
    for task_id, e in pins.items():
        ours = hashlib.sha256((LAB / "tasks" / task_id / "task.json").read_bytes()).hexdigest()
        if ours != e["task_json_sha256"]:
            raise SystemExit(f"{task_id}: task.json at our pin differs from the AHE split's")
    for block in range(10):
        got = Counter(split_of[t] for t, s in strata.items() if s["block"] == block and t in split_of)
        if got != Counter(PER_BLOCK):
            raise SystemExit(f"block {block}: {dict(got)}, expected {PER_BLOCK}")

    def row(task_id: str) -> dict:
        s = strata[task_id]
        return {"task_id": task_id, "difficulty_block": s["block"],
                "nine_b_all_pass": s["dual_all_pass_rate"], "nine_b_criterion_pass_rate": round(s["criterion_pass_rate"], 4)}

    def means(ids: list[str]) -> dict:
        return {"tasks": len(ids),
                "nine_b_all_pass": round(statistics.mean(strata[t]["dual_all_pass_rate"] for t in ids), 4),
                "nine_b_criterion_pass_rate": round(statistics.mean(strata[t]["criterion_pass_rate"] for t in ids), 4)}

    total = sum(PER_BLOCK.values())
    splits = {name: [{**row(t), "task_json_sha256": pins[t]["task_json_sha256"]}
                     for t in sorted(split_of) if split_of[t] == name] for name in NAMES}
    unused = sorted(t for t in strata if t not in split_of)
    provenance = {"repo": "github.com/div652/evo-harness (AHE Harvey project)", "file": SOURCE, "commit": commit,
                  "file_sha256": hashlib.sha256(raw).hexdigest(), "ahe_identity": ahe["identity"],
                  "lab_commit": ahe["lab_commit"]}
    data = {
        "benchmark": "harvey",
        "description": "The AHE campaigns' Harvey split (campaigns 12/15/23-27/34): 80 train, 20 val, 70 test of the 250 "
                       "firm-knowledge tasks, stratified by 9b difficulty (10 blocks of 25: 8 train, 2 val, 7 test, 8 unused "
                       "each). trainval = the 100 tasks AHE evolved on; test = the 70 tasks AHE reported on. Not compatible "
                       "with splits.json (the 60/20/20 split): use one or the other for a study.",
        "source": provenance,
        "seed": None,
        "ratios": {name: PER_BLOCK[name] / total for name in NAMES},
        "group_by": "difficulty_block",
        "method": "benchmarks/harvey/import_ahe_splits.py (AHE's make_splits_firm_knowledge_c12.py and _c15.py: sha256 "
                  "order within each difficulty block, no random seed)",
        "counts": {"total": len(split_of), **{n: len(splits[n]) for n in NAMES}, "unused": len(unused),
                   "difficulty_blocks": {b: ordered(Counter(split_of[t] for t in split_of if strata[t]["block"] == b))
                                         for b in range(10)}},
        "nine_b_means": {n: means([e["task_id"] for e in splits[n]]) for n in NAMES}
                        | {"trainval": means([e["task_id"] for e in splits["train"] + splits["val"]]),
                           "unused": means(unused), "all 250": means(sorted(strata))},
        "unused": unused,
        "splits": splits,
    }
    (HERE / "splits-ahe-80-20-70.json").write_text(json.dumps(data, indent=1) + "\n")

    ours = {e["task_id"]: n for n in NAMES for e in json.loads((HERE / "splits.json").read_text())["splits"][n]}
    blocks = {b: sorted(t for t in strata if strata[t]["block"] == b) for b in range(10)}
    ref = {
        "benchmark": "harvey",
        "description": "Difficulty strata of the 250 firm-knowledge tasks, as AHE made them (reference). Difficulty is AHE "
                       "campaign 9b's result per task: gpt-5.6-sol, reasoning high, Harvey's own harness (LAB-exact), one "
                       "trial per task, judged by Harvey's grader. Tasks sorted hardest first by (9b all-pass, 9b criterion "
                       "pass rate, sha256('harvey-lab-campaign-12:order:' + task_id)) and cut into 10 blocks of 25: block 0 "
                       "is the hardest, block 9 the easiest. With one trial per task the all-pass value is 0 or 1, so a "
                       "block is a coarse difficulty band, not a precise rank.",
        "source": provenance | {"nine_b_source": ahe["stratification"]["source"]},
        "blocks": {b: means(ids) | {"ahe_split": ordered(Counter(split_of.get(t, "unused") for t in ids)),
                                    "our_split": ordered(Counter(ours.get(t) for t in ids))} for b, ids in blocks.items()},
        "tasks": {t: row(t) | {"ahe_split": split_of.get(t, "unused"), "our_split": ours.get(t)} for t in sorted(strata)},
    }
    for r in ref["tasks"].values():
        del r["task_id"]
    (HERE / "difficulty-9b.json").write_text(json.dumps(ref, indent=1) + "\n")
    print({n: len(splits[n]) for n in NAMES}, "unused", len(unused), "source commit", commit)
    for k, v in data["nine_b_means"].items():
        print(f"  9b means {k}: {v}")


if __name__ == "__main__":
    main()
