# Task-instruction-aligned JobBench rubrics

This directory contains a separate rubric variant for all 65 JobBench `main` tasks. It does not replace or modify any `RUBRICS.json` in the source datasets or existing runs.

## Source and purpose

The variant is aligned to the refined task instructions in:

`runs/gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z/dataset/main`

Each rubric checks the work requested by that task's `task_folder/TASK_INSTRUCTIONS.txt`. A criterion may verify source-grounded correctness, calculations, consistency, or required deliverables, but it must not require a hidden conclusion, an arbitrary method, exact wording, an unrequested section, or a hard-coded answer that the instructions do not require.

The review used the original rubrics, task inputs, 2,417 available judge reports, and representative outputs and trajectories. Thirteen tasks that had never received a full weighted score were assigned a dedicated all-report analysis.

## Layout

```text
task-instruction-aligned-v1/
├── README.md
├── MANIFEST.json
├── NEVER_FULL_ANALYSIS.md
├── SECOND_PASS_AUDIT.md
├── audits/
│   └── second-pass/
├── validation-report.json
└── main/
    └── <occupation>/
        └── taskN/
            ├── RUBRICS.json
            └── REFINEMENT_NOTES.md
```

`RUBRICS.json` retains JobBench's `{"rubrics": [...]}` structure. Every task preserves its original total rubric weight. `REFINEMENT_NOTES.md` records instruction support, material changes, judge and trajectory evidence, and the distinction between likely judge artifacts and genuine task failures.

`NEVER_FULL_ANALYSIS.md` consolidates the special review of the 13 tasks that had no perfect score in the available judge reports.

`SECOND_PASS_AUDIT.md` records the independent 65-task adversarial review, applied fixes, evaluator-infrastructure limitations, regression checks, and final zero-issue re-lint. The supporting structured reports are under `audits/second-pass/`.

## Review rules

- Assess every explicit deliverable and substantive analysis requested by the refined instructions.
- Accept equivalent correct methods unless the instructions prescribe one.
- Accept documented uncertainty when the provided sources do not determine a unique answer.
- Use named task inputs to verify calculations and factual consistency.
- Remove hidden expected conclusions, unsupported assumptions, exact-phrase checks, duplicated penalties, and requirements found only in the old rubric.
- Preserve the original total weight while reallocating weight from removed or merged requirements.

## Validation

Run:

```bash
python eval/validate_task_aligned_rubrics.py \
  --source runs/gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z/dataset/main \
  --variant rubric_variants/task-instruction-aligned-v1/main \
  --report rubric_variants/task-instruction-aligned-v1/validation-report.json
```

The validator requires all 65 relative task paths, exact rubric schema, positive integer weights, non-empty criteria, review notes, unique rows and criteria, and per-task weight equality with the source rubric.

## Using the variant

Use the variant only with a copied dataset or a runner that accepts a separate rubric root. Do not overlay it onto the source run. When materializing a copied dataset, replace only each copy's relative `RUBRICS.json` with the corresponding file under `main/`; task instructions, task inputs, outputs, and trajectories remain unchanged.

This variant has structural validation, two human-review passes, and a final independent corpus re-lint with no remaining actionable rubric issue. It has not yet been used for a new judge pass, so score changes remain unmeasured.
