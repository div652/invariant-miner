# Refinement notes — data_entry_keyers/task2

## Instruction-supported requirements

The instructions require a field-by-field comparison of 75 entered records with the source forms, validation of code-description pairs in both sources against the official FY2025 ICD-10-CM descriptions, date-aware application of the memo's ICD and fee-schedule rules, immediate application of its insurance-name standardization, and a semantic split between clear errors and review items. They also require an error log in the provided template, a review CSV with specific reasons, a selectively corrected copy of the entered data, and an overall/provider/facility/flagged-item reconciliation workbook.

Exact source-backed discrepancies may be checked because they are necessarily derived from the named files. Exact review-category wording is not uniquely required: the instructions give examples, so a semantically correct “source conflict” label must receive the same credit as “Source Inconsistency.”

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 insurance-provider errors (10) | Merged into clear-error classification | Retains source-versus-entered carrier validation and correction. |
| R2 fee-schedule discrepancies (6) | Merged into review classification | Retains the effective-date, facility, CPT, and entered-rate logic without making two examples the whole criterion. |
| R3 post-policy R05.9 item (6) | Merged into review classification | Retains the memo-trigger distinction between a source-consistent policy issue and a transcription error. |
| R4 source R05.9 inconsistencies (8) | Rewritten semantically | Retains provider clarification and no silent correction. Removes the requirement for the exact label `Source Inconsistency` when the reason clearly identifies the same conflict. |
| R5 name misspellings (6) | Merged into clear-error classification | Retains source-backed name corrections as part of comprehensive field validation. |
| R6 service-date errors (8) | Merged into clear-error classification | Retains date correction and the significance of the policy effective date. |
| R7 selective corrected file (8) | Retained as a dedicated 10-point row | Expands from five disclosed review examples to every classified finding and cross-deliverable consistency. |
| R8 duplicate BF-2025-0020 provider logic (8) | Merged with R1 | This row duplicated the first provider error and overweighted one form. The source-before-standardization reasoning remains required for all records. |
| Reconciliation deliverable | Added as a dedicated 10-point row | The original rubric did not directly score the required overall, provider, facility, and flagged-item workbook. |

The variant uses six 10-point task-level rows: source validation, classification, error log, review CSV, corrected data, and reconciliation. This avoids double-scoring the same provider field while preserving the original total.

## Evidence examined

- Refined Luna: `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, two 52/60 reports, all four outputs, and trajectory. It found the principal fee and cough issues but labeled the two source code-description conflicts as policy flags and produced a much larger review set.
- Sol rubric-gold: `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, four 60/60 reports, five-row review file, complete output set, and source-validation trajectory.
- Qwen 3.8 reasoning: `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`, two 54/60 reports, outputs, and trajectory. Its genuine miss was the unflagged post-policy unspecified-cough record.
- Inputs inspected included the memo, all 75 entered and source rows, the 22 direct field differences, 13-row fee schedule, provider/facility directory, error-log template, and official code file.

## Likely judge artifacts versus genuine task failures

The refined Luna deduction for using `Policy Compliance Flag` rather than `Source Inconsistency` is partly a label artifact: its reasons identified acute/subacute source conflicts and it left the values unchanged. The revised rubric grades the semantic distinction and actionable reason, not one exact label. Missing a post-policy code entirely, correcting a fee-match review item, failing to check a source code-description pair, or changing a review item in the corrected CSV are genuine failures. Over-flagging source-valid records without a memo, source, or fee trigger is also a genuine quality problem and is now covered.

## Weight check

Original total: **60**. Variant total: **60**.

## Second-pass validation

- Separated the memo's service-date-dependent ICD and fee-schedule rules from its immediately effective insurance-name standardization.
- Added the error-log template's required sequential numbering, identification date format, and reviewer identifier.
- Preserved semantic acceptance of equivalent review-category wording and selective correction of only clear errors.
- Deferred absent row-level source context and ICD-10 reference extraction in the judge prompt to evaluator infrastructure; no hidden error list or expected counts were added.
