# Refinement notes — court_clerks/task1

## Instruction-supported requirements

The refined instructions require a comprehensive pre-entry audit, six official-form sentencing orders, a fee reconciliation, a fully updated CMS database, and a sentencing register. The audit must compare every available defendant-identifying and case field, document one row per discrepancy, evaluate the Simmons memorandum on its merits, and state a verification source, order value, and downstream effect for each resolution. The fee file must use the specified columns and status vocabulary, include omitted mandatory assessments, cite the fee schedule, and distinguish mandatory assessments from conditional or discretionary items. The database requirements explicitly fix the case status, dates, clerk name, payment status, and balance calculation. The register requirements explicitly fix its title, table columns, six-case coverage, totals, and annotation topics.

The instructions do not establish a universal hierarchy in which the Judge's notes automatically override the CMS or corroborating case materials. They also do not require the audit to use phrases such as “transposed digits,” prescribe a particular verification source for every discrepancy, or require an undocumented legal conclusion merely because it appeared in an original rubric answer key.

## Original rubric disposition

- **R1, R2, R3, and R9 — merged and rewritten as new R1.** The underlying discrepancies remain valid evidence to detect when supported by the files, but four rows separately rewarded selected discrepancies and prescribed wording, source hierarchy, and resolution details. The merged row evaluates comprehensive source reconciliation and the required resolution fields without forcing one hidden answer.
- **R4 — rewritten as new R3.** The current schedule, conditional-fee treatment, statutory citation, and corrective action remain assessable. The variant does not make a particular dollar amount or automatic correction the rubric question; it checks the submitted values against the named source files.
- **R5 — retained and generalized as new R4.** The explicit database values remain because the instructions require them. Per-case disposition descriptions are checked against the source materials instead of being embedded as a hidden list in the rubric.
- **R6 — rewritten and merged with part of R7 as new R7.** The required register columns, six cases, totals, and annotations remain. The original hard-coded fee totals were removed because the task also requires current-schedule corrections, so the register must agree with the reconciliation rather than reproduce unreconciled Judge totals.
- **R7 — merged into new R1 and new R7.** Audit, fee, and Simmons content is assessed in the deliverable where it belongs and then checked for faithful register annotation. The original minimum list and forced legal conclusion were removed.
- **R8 — retained as new R5.** Its date, clerk, entry type, and case-specific description are explicit instruction requirements.
- **R10 — retained as new R6.** Its payment status and balance rules are explicit instruction requirements.
- **New R2 — added.** The original rubric had no direct row for the six official-form sentencing orders even though they are a central deliverable.

## Material changes and reasons

1. Selected-discrepancy rows were replaced with a comprehensive audit row because the instructions require every discrepancy, not only four answer-key examples.
2. The requirement to presume the Judge's Barnett DOB as authoritative was removed because the instructions require a documented resolution but do not define that source hierarchy.
3. The requirement to describe the Morales SID issue specifically as “transposed digits” was removed because exact wording is not required.
4. Prescribed verification sources were replaced with an appropriate-source standard because the instructions allow equivalent defensible verification.
5. The Simmons criteria now require statutory analysis, effect, and recommendation while accepting a supported conclusion or documented uncertainty.
6. Hard-coded register fee totals were removed because they reproduce the Judge's unreconciled figures and conflict with applying the current fee schedule. For example, the source notes use the former drug assessment while the supplied schedule identifies a later effective amount.
7. The Henderson filing-date example is no longer a hidden mandatory answer. It remains scoreable when the comprehensive source comparison shows it is a discrepancy.
8. Duplicate scoring of the same discrepancy in audit rows and the register-annotation row was reduced.
9. Weight was added for the sentencing-order PDFs, which the original rubric omitted.

## Score and trajectory evidence examined

All **26 available high/low judge reports across 15 runs** were examined. Scores ranged from **0/76 to 44/76**, and no report awarded full credit. Per-row pass counts were: R1 8/26, R2 3/26, R3 7/26, R4 8/26, R5 14/26, R6 0/26, R7 4/26, R8 22/26, R9 14/26, and R10 4/26.

Representative outputs and trajectories inspected:

- **Refined Luna landlock:** 44/76 in both judge reports. It produced all requested file types and updated all four database areas. It lost R1 for choosing the CMS Barnett DOB pending certified verification, R2 for omitting the phrase “transposed digits” and the prescribed verification sources, R6 for using reconciled fee totals, and R7 for omitting the hidden Henderson filing-date example.
- **GPT-5.4 high Exa:** 30/76. It produced six PDF orders, CSVs, a register, and a database under a non-exact database filename. Genuine omissions included incomplete financial updates and register content; several failures also arose from the selected-answer wording.
- **Qwen 3.5 reasoning:** 10/76. Its trajectory claimed completion, but the outputs used text files rather than official-form sentencing-order PDFs and omitted the required updated database. Those are genuine task failures independent of rubric wording.

The Judge notes, fee schedule, CMS tables, Simmons memorandum, representative CSVs, database rows, register text, and trajectory completion messages were also inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include failures caused only by choosing a defensible CMS value rather than the Judge's value, not saying “transposed digits,” not naming one prescribed verification source, omitting hidden attorney-firm wording, or using corrected register totals instead of unreconciled totals. R6's 0/26 record is especially distorted because its embedded fee totals conflict with the reconciliation requirement.

Genuine failures include missing discrepancies after a comprehensive comparison, missing official-form orders, incomplete required register columns, absent or incorrect CMS updates, missing docket entries, wrong fixed status values, omitted financial obligations, unsupported fee treatment, and failure to analyze the Simmons challenge.

## Never-full analysis

No available report could score full because the rubric combined legitimate deliverable checks with brittle answer-key requirements and at least one internal conflict. The best runs repeatedly failed R1 and R2 despite detecting the underlying discrepancies, because the rows demanded a preferred source and exact descriptive language. R6 never passed in any of 26 reports: runs that followed the current fee schedule changed the register totals and therefore failed the rubric's unreconciled hard-coded totals, while lower-quality runs failed the required table content. R7 duplicated audit content and imposed a hidden minimum list, so otherwise complete registers failed for one omitted example. The result was a ceiling unrelated to whether the refined task was completed correctly. The variant removes that ceiling while preserving strict checks on completeness, source accuracy, database state, official forms, reconciliation, and the required legal issue analysis.

## Weight accounting

- Original total: **76**
- Variant total: **76**
- Weight was reallocated from duplicate selected-discrepancy rows and hard-coded register answers to the omitted sentencing-order deliverable and comprehensive cross-deliverable consistency.

## Second-pass validation

- Limited `fees_payments` completeness to verified fees, fines, and assessments.
- Added explicit acceptance for conditional assessments that remain pending verification, provided the uncertainty is documented and no definitive assessed obligation is invented.
- Preserved the 76-point total.
- Deferred the judge's missing-source-context and PDF-form extraction findings to evaluator infrastructure; the rubric does not embed hidden case answers or alter official-form requirements to compensate for unavailable source or AcroForm evidence.
