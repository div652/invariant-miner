# Second-pass rubric audit

This report records the independent adversarial validation of all 65 task-instruction-aligned rubrics. Ten reshuffled reviewers audited disjoint task groups, one reviewer tested corpus-wide patterns, and one reviewer tested whether the JobBench judge can observe and verify each requirement.

## Method

Each task reviewer compared the variant rubric with the refined instructions, task inputs, original rubric, refinement notes, and representative outputs or judge evidence when needed. Reviewers challenged every criterion with plausible alternative correct submissions and checked instruction coverage, hidden answers, arbitrary methods or formats, source consistency, atomicity, overlap, contradictions, weight allocation, and judgeability.

The corpus reviewer measured and manually verified duplication, compound criteria, all-or-nothing score concentration, undefined thresholds, circular rules, and verbosity bias. The judgeability reviewer checked all 484 pre-fix rows and 3,235 pre-fix criteria against the actual JobBench extraction and judging path.

Reviewers filed findings before editing. Ten fix passes then changed only their assigned variant files, preserved every task's total weight, updated the task notes, and recorded an explicit disposition for every finding.

## Initial findings

The independent task reviews produced:

| Verdict | Tasks |
|---|---:|
| Pass | 18 |
| Pass with changes | 42 |
| Fail | 5 |

The task reviews recorded 83 issues: 19 high, 55 medium, and 9 low. The corpus lint added 15 manually verified issues: 3 high, 11 medium, and 1 low.

Examples included omitted explicit objectives, hidden named outcomes, undefined populations and aggregation rules, contradictory status vocabularies, double-counted commissions, circular self-defined risk rules, missing deliverable structures, all-or-nothing score concentration, and duplicated penalties.

## Judgeability findings

The judgeability audit recorded 105 findings. Ten could be corrected in rubric content. Ninety-five require evaluator infrastructure because the current judge receives rubric text and extracted deliverables but not task instructions, task inputs, external references, or trajectories.

The deferred infrastructure findings include source-correctness checks that lack reference context, spreadsheet charts and formatting omitted by extraction, PDF and DOCX pagination or visual layout, PPTX images, notebook rich output, database truncation, and SQL behavior that requires execution rather than text inspection.

These limitations were not addressed by adding hidden expected answers to the rubrics. Recommended evaluator work is to pass canonical source extracts or deterministic check results to the judge, render visual artifacts, inspect spreadsheet structures directly, and execute database or SQL deliverables in controlled copies.

## Dispositions and repairs

Across the task reviews, corpus lint, judgeability audit, and regression checks:

| Disposition | Findings |
|---|---:|
| Applied rubric fix | 109 |
| Deferred evaluator infrastructure | 97 |
| Rejected | 0 |

The fixes changed 52 task rubrics; 13 required no content change. They split concentrated rows, added missing instruction requirements, removed hidden conclusions and arbitrary prescriptions, defined source-grounded populations and uncertainty treatment, accepted valid alternatives, and separated structural checks from substantive calculations.

The first post-fix re-lint found three medium regressions. Those affected purchasing estimates, sociology filename weighting, and online-merchant risk selection. All three were corrected. The final re-lint resolved all 15 original corpus issues and all three regressions, with no new actionable issue.

## Final result

**Status: PASS**

- Tasks: 65
- Rubric rows: 521
- Criteria: 3,288
- Total weight: 4,500
- Per-task source weight preserved: yes
- Original corpus-lint issues unresolved: 0
- Regression issues unresolved: 0
- New actionable issues: 0
- Source-run files changed: no

The source-integrity check detected nine review-note edits written to source-run paths during integration. The affected sections were moved to the variant, the source copies were restored from hash-matching copies, and the full 260-file source hash set passed afterward.

## Artifacts

- `group-01.json` through `group-10.json`: independent per-task findings.
- `corpus-lint.json`: cross-corpus findings and pre-fix metrics.
- `judgeability.json`: observation and evaluator limitations.
- `judgeability-disposition.json`: rubric-content versus infrastructure classification.
- `fixes/group-01.json` through `fixes/group-10.json`: applied and deferred dispositions.
- `post-fix-validation.json`: final zero-issue re-lint.
- `validation-report.json`: final structural and weight validation.
