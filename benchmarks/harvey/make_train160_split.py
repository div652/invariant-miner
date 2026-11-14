"""Make splits-ahe-160-20-70.json: the AHE split with its 80 unused tasks moved into train (user, 2026-11-13).

    python3 benchmarks/harvey/make_train160_split.py

train = the AHE train 80 + the 80 tasks the AHE split left unused (160); val (20) and test (70) are AHE's, unchanged.
Every entry keeps the AHE file's fields (difficulty block and 9b values from difficulty-9b.json; task.json sha256 checked
at our Harvey pin, work/harvey-labs) plus `train_origin`: "ahe-train" or "ahe-unused". Use it with
`make_specs.py --tasks ahe160:train` (val, test). Not compatible with splits.json (the 60/20/20 split).
"""

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1] / "work/harvey-labs"


def main() -> None:
    ahe = json.loads((HERE / "splits-ahe-80-20-70.json").read_text())
    strata = json.loads((HERE / "difficulty-9b.json").read_text())["tasks"]
    sha = {t: hashlib.sha256((LAB / "tasks" / t / "task.json").read_bytes()).hexdigest() for t in strata}
    for name in ("train", "val", "test"):
        for e in ahe["splits"][name]:
            if sha[e["task_id"]] != e["task_json_sha256"]:
                raise SystemExit(f"{e['task_id']}: task.json differs from the AHE split's sha256")

    def row(task_id: str, origin: str) -> dict:
        s = strata[task_id]
        return {"task_id": task_id, "difficulty_block": s["difficulty_block"], "nine_b_all_pass": s["nine_b_all_pass"],
                "nine_b_criterion_pass_rate": s["nine_b_criterion_pass_rate"], "task_json_sha256": sha[task_id],
                "train_origin": origin}

    train = sorted([row(e["task_id"], "ahe-train") for e in ahe["splits"]["train"]]
                   + [row(t, "ahe-unused") for t in ahe["unused"]], key=lambda e: e["task_id"])
    splits = {"train": train, "val": ahe["splits"]["val"], "test": ahe["splits"]["test"]}
    ids = [e["task_id"] for n in splits for e in splits[n]]
    if len(ids) != 250 or len(set(ids)) != 250:
        raise SystemExit(f"expected 250 distinct tasks, got {len(ids)} ({len(set(ids))} distinct)")

    def means(entries: list[dict]) -> dict:
        return {"tasks": len(entries),
                "nine_b_all_pass": round(statistics.mean(e["nine_b_all_pass"] for e in entries), 4),
                "nine_b_criterion_pass_rate": round(statistics.mean(e["nine_b_criterion_pass_rate"] for e in entries), 4)}

    data = {
        "benchmark": "harvey",
        "description": "The AHE split with a larger train set: train = AHE's 80 train tasks + the 80 tasks AHE left "
                       "unused (160, field train_origin), val = AHE's 20, test = AHE's 70 (both unchanged). All 250 "
                       "firm-knowledge tasks; 10 difficulty blocks of 25 = 16 train, 2 val, 7 test each. Not compatible "
                       "with splits.json (the 60/20/20 split).",
        "source": {"derived_from": "benchmarks/harvey/splits-ahe-80-20-70.json", "decided": "user, 2026-11-13"},
        "seed": None,
        "ratios": {"train": 160 / 250, "val": 20 / 250, "test": 70 / 250},
        "group_by": "difficulty_block",
        "method": "benchmarks/harvey/make_train160_split.py",
        "counts": {"total": 250, **{n: len(v) for n, v in splits.items()},
                   "train_origin": dict(Counter(e["train_origin"] for e in train)),
                   "difficulty_blocks": {b: {n: sum(e["difficulty_block"] == b for e in v) for n, v in splits.items()}
                                         for b in range(10)}},
        "nine_b_means": {n: means(v) for n, v in splits.items()}
                        | {"train ahe-train": means([e for e in train if e["train_origin"] == "ahe-train"]),
                           "train ahe-unused": means([e for e in train if e["train_origin"] == "ahe-unused"])},
        "splits": splits,
        **({"subsets": ahe["subsets"]} if "subsets" in ahe else {}),  # named subsets (make_flip_subset.py)
    }
    (HERE / "splits-ahe-160-20-70.json").write_text(json.dumps(data, indent=1) + "\n")
    print(data["counts"]["train"], data["counts"]["val"], data["counts"]["test"], data["counts"]["train_origin"])
    for k, v in data["nine_b_means"].items():
        print(f"  9b means {k}: {v}")


if __name__ == "__main__":
    main()
