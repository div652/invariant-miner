# Refinement notes — data_entry_keyers/task1

## Instruction-supported requirements

The refined instructions require four deliverables: a completed error-log template with one row per discrepant field; a one-row-per-order reconciled dataset with every reconciled field, verification status, conflicts, and registration flag; an executive report with reproducible metrics, error counts, recurring patterns, and recommendations; and a fully completed checklist and summary. The source priority is scanned form over CRM over ERP. Revenue must be tested as units multiplied by price within ±$0.01, and every revenue discrepancy must show the formula, actual numbers, and variance. Every order must be validated against the 35-customer master and unregistered entities flagged.

The instructions do not prescribe a hidden finite list of discrepancies, require one exact error label when two allowed labels are defensible, or establish one fixed clean-record denominator. The supplied compliance checklist audits the original source records; corrected reconciled values may be reported separately but do not change source-quality pass/fail results.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1–R10 — ten selected discrepancies | Merged and rewritten as new R1–R4 | The underlying records remain source-grounded checks, but the task requires all discrepancies. The variant scores comprehensive discovery, source priority, revenue work, customer-master validation, and reasonable classification instead of ten answer-key examples. |
| R3, R4, R5, R7, and R9 — prescribed Transposition/Format/Typo labels | Generalized in new R2 | The allowed vocabulary remains mandatory. A defensible label with clear notes is accepted when the instructions do not uniquely distinguish alternatives such as Typo versus Format or Typo versus Transposition. |
| R11 — fixed clean-record metric | Rewritten as new R6 | A reproducible metric remains explicit. The hard-coded 13/30 result was removed because submissions may use record-, field-, or reconciliation-level metrics if the numerator, denominator, and unit are correct. |
| R12 — CRT-005 must be Fail with two fixed examples | Rewritten as new R7 | The two hidden example orders were removed. The checklist must apply its threshold to the original source records, so source calculation failures remain failures even when the reconciled master corrects them. |
| No original row — reconciled master completeness | Added as new R5 | A central deliverable was previously represented only indirectly. |
| No original row — full report counts and recommendations | Expanded in new R6 | The instructions explicitly require error counts by type/source, recurring frequencies, and process improvements. |
| No original row — cross-deliverable consistency | Added as new R8 | Counts, values, patterns, and registration findings must agree or explain their units of analysis. |

## Material changes and reasons

1. Ten selected-error rows were replaced by comprehensive discrepancy coverage so an output cannot earn most of the score while missing unlisted errors.
2. Exact labels were removed where the allowed vocabulary permits more than one reasonable classification supported by notes.
3. Source priority, source attribution, pattern definition, and revenue formulas remain directly scored.
4. The fixed clean-record rate was removed; reproducibility and correct labeling now control the metric.
5. Checklist criteria are assessed against the original source evidence. Reconciled-output quality may be reported separately but cannot convert a source-data failure into a pass.
6. The reconciled dataset, unregistered-customer handling, checklist summary, and cross-file consistency received direct weight.

## Score, output, and trajectory evidence examined

All **37 available judge reports across 17 runs** were inspected. Scores ranged from **0/92 to 92/92**, with a median of **50/92**. Original-row failure counts were R1 4/37, R2 7/37, R3 18/37, R4 32/37, R5 16/37, R6 16/37, R7 31/37, R8 4/37, R9 23/37, R10 11/37, R11 9/37, and R12 26/37.

Representative outputs and trajectories inspected:

- **Refined Luna landlock:** 44/92 in both reports. It produced four files, a 23-row error log, a 30-order master, and a completed checklist. It was penalized for classifying several values differently from the answer key and for marking CRT-005 Pass after reconciliation. Genuine issues included inconsistent error counts and a metric basis that did not match the original row's expected count.
- **Sol rubric-gold:** 92/92 in both reports. It produced a 17-row error log, a complete master, reproducible report metrics, and a raw-source checklist basis that made CRT-005 Fail. Its trajectory inspected all ten scans and reconciled source fields directly.
- **Qwen reasoning:** 72/92 low and 62/92 high. It produced all four analytical deliverables, identified 17 CRM–ERP field mismatches plus unregistered entities, and documented formulas. It lost points largely for exact label and evidence-wording expectations, although some checklist evidence omitted exact values requested by the original row.

The CRM and ERP workbooks, all ten scanned order forms, customer master, error-log and checklist templates, representative output workbooks/reports, and trajectory scan-inspection paths were examined directly.

## Likely judge artifacts versus genuine task failures

Likely artifacts include requiring Italia to be Format rather than a documented Typo, requiring $5.05 versus $5.50 or $108 versus $180 to be Transposition rather than another allowed keying label, requiring an explicit file name when the customer ID and master value are already cited, fixing the clean-record rate to one denominator, and forcing CRT-005 to Fail without considering the declared checklist basis.

Genuine failures include omitted discrepancies, incorrect source priority, wrong reconciled values, missing formula or variance details, unsupported source attribution, declaring a one-off issue systematic, missing unregistered customers, incomplete master fields, mislabeled metrics, incomplete checklist fields, or inconsistent counts across deliverables.

## Weight accounting

- Original total weight: **92**
- Variant total weight: **92**
- Weight was reallocated from ten selected answer-key records to comprehensive reconciliation, the previously underweighted master dataset, reproducible reporting, checklist basis, and cross-deliverable consistency.

## Second-pass validation

- Compliance checklist statuses now use the original CRM, ERP, scan, and customer-master evidence rather than repaired values in the reconciled master.
- Reconciled-output quality may be reported separately but cannot convert a source-data failure into a pass.
- Source-table and scanned-form reference access remains an evaluator-infrastructure requirement; no hidden discrepancy list was added.
