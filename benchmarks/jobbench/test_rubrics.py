"""Check the rubric sets kept in this repository (benchmarks/jobbench/rubrics/, see its README.md).

    python3 benchmarks/jobbench/test_rubrics.py [--dataset ~/job-bench-eval/dataset/main]

task-instruction-aligned-v1: 65 tasks, each RUBRICS.json {"rubrics": [{"rubric", "weight", "criterion"}]} with a
positive integer weight and a non-empty criterion list, and a REFINEMENT_NOTES.md next to it; the totals of its
MANIFEST.json (rows, criteria, total weight 4,500). With the dataset present: the same 65 task ids as dataset/main and,
per task, the same total weight as the original RUBRICS.json (the set reallocates weight, never changes the total).
The dataset part is skipped, with a note, when the dataset directory does not exist.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE / "rubrics/task-instruction-aligned-v1"


def rubric_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or set(data) != {"rubrics"} or not isinstance(data["rubrics"], list):
        raise ValueError(f"{path}: not {{\"rubrics\": [...]}}")
    return data["rubrics"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path.home() / "job-bench-eval/dataset/main")
    args = parser.parse_args()
    problems = []
    tasks = sorted(str(p.parent.relative_to(V1 / "main")) for p in (V1 / "main").glob("*/task*/RUBRICS.json"))
    rows = criteria = weight = 0
    totals = {}
    for task in tasks:
        folder = V1 / "main" / task
        try:
            items = rubric_rows(folder / "RUBRICS.json")
        except (ValueError, json.JSONDecodeError) as error:
            problems.append(str(error))
            continue
        if not (folder / "REFINEMENT_NOTES.md").is_file():
            problems.append(f"{task}: no REFINEMENT_NOTES.md")
        for i, item in enumerate(items):
            if set(item) != {"rubric", "weight", "criterion"}:
                problems.append(f"{task} R{i}: keys {sorted(item)}")
            elif not (isinstance(item["weight"], int) and item["weight"] > 0):
                problems.append(f"{task} R{i}: weight {item['weight']!r}")
            elif not (isinstance(item["criterion"], list) and item["criterion"]
                      and all(isinstance(c, str) and c.strip() for c in item["criterion"])):
                problems.append(f"{task} R{i}: empty criterion list")
        rows += len(items)
        criteria += sum(len(item.get("criterion", [])) for item in items)
        totals[task] = sum(item.get("weight", 0) for item in items)
        weight += totals[task]
    manifest = json.loads((V1 / "MANIFEST.json").read_text())
    expected = {"tasks": manifest["taskCount"], "rows": manifest["finalRubricRowCount"],
                "criteria": manifest["finalCriterionCount"], "weight": manifest["totalWeight"]}
    found = {"tasks": len(tasks), "rows": rows, "criteria": criteria, "weight": weight}
    if found != expected:
        problems.append(f"totals {found} != MANIFEST.json {expected}")
    print(f"v1: {len(tasks)} tasks, {rows} rubric items, {criteria} criteria, total weight {weight}")

    dataset = args.dataset.expanduser()
    if dataset.is_dir():
        originals = sorted(str(p.parent.relative_to(dataset)) for p in dataset.glob("*/task*/RUBRICS.json"))
        if originals != tasks:
            problems.append(f"task ids differ from {dataset}: only in v1 {sorted(set(tasks) - set(originals))}, "
                            f"only in the dataset {sorted(set(originals) - set(tasks))}")
        for task in set(tasks) & set(originals):
            original = sum(item["weight"] for item in rubric_rows(dataset / task / "RUBRICS.json"))
            if original != totals.get(task):
                problems.append(f"{task}: total weight {totals.get(task)} vs original {original}")
        print(f"dataset {dataset}: {len(originals)} tasks, per-task total weights compared")
    else:
        print(f"dataset {dataset} not found: task ids and weights against the original rubrics not checked")

    for problem in problems:
        print("FAIL ", problem)
    print("PASS  rubric set task-instruction-aligned-v1" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
