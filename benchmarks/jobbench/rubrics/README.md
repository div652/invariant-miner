# JobBench rubric sets kept in this repository

`grade.sh --rubrics v1` grades against `task-instruction-aligned-v1/main/<profession>/<taskN>/RUBRICS.json` here, so a
clone of this repository can grade on v1 without any other checkout. The **original** rubrics are not copied: they are
the dataset's own `RUBRICS.json` (`job-bench-eval/dataset/main`, which grading needs anyway).

## task-instruction-aligned-v1

- **Source**: [microsoft/agentic-evolution](https://github.com/microsoft/agentic-evolution), directory
  `attribution/jobbench_rubric_variants/task-instruction-aligned-v1/`, last changed in commit `1ac7339e` (2026-10-20),
  unchanged at its `main` `54a1e710` (2026-11-03), the commit copied from.
- **Authors**: Yash and Akshya (agentic-evolution). Used in this repository with their permission (2026-11-11).
- **Copied verbatim** (2026-11-11): all 159 files the source tracks, unchanged: the 65 `RUBRICS.json`, a
  `REFINEMENT_NOTES.md` per task (what changed and why), the review documents (`README.md`, `MANIFEST.json`,
  `NEVER_FULL_ANALYSIS.md`, `SECOND_PASS_AUDIT.md`, `audits/`, `validation-report.json`). Paths named inside those
  documents (`runs/...`, `eval/validate_task_aligned_rubrics.py`) are agentic-evolution's, not this repository's.
- **What it is** (its `README.md`): every one of the 65 `main` tasks re-reviewed against the task instructions; each
  rubric checks only what the instructions ask for (no hidden expected conclusions, exact phrases, unrequested
  sections or duplicated penalties), equivalent correct methods are accepted, and every task keeps its original total
  weight (4,500 over the 65 tasks). It was written against the task instructions of agentic-evolution's refined
  dataset.
- **Same files as used before**: the JobBench runs in `../RESULTS.md` graded on v1 used this exact tree (65/65
  `RUBRICS.json` byte-identical).

Check the copy (all 65 tasks present, schema, weights equal to the original rubrics):
`python3 benchmarks/jobbench/test_rubrics.py [--dataset ~/job-bench-eval/dataset/main]`.

Do not edit these files in place: a changed rubric set is a new set. Put it in a new directory here and grade with
`grade.sh --rubrics <dir> ` plus `GRADING_DIR`, or add it as a named set in `grade.sh`.
