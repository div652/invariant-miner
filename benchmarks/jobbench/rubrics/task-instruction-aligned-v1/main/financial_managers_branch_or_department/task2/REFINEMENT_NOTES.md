# Refinement notes — financial_managers_branch_or_department/task2

## Instruction-supported requirements

The task requires an Excel risk report and one PDF containing a one-to-two-page executive summary plus six credit memoranda. The workbook must cover portfolio and sector summaries, weighted rates and yield, a count-and-dollar asset-quality cross-tab, NPA benchmarking against the FDIC Q4 2024 total-loans-and-leases noncurrent rate, sector concentrations and grandfathering, top-five exposures, every adversely rated loan, CDFI objective and subjective scoring, OCC-grounded actions, and a +200 basis-point DSCR stress. The memoranda must show recommendations, scoring detail, source metrics, policy thresholds, OCC alignment, sector impact, remaining capacity, and conditions. Aggregate approvals must stay within $3.0 million without creating new sector breaches.

Direct inspection confirmed 88 portfolio rows, six applications, the source category fields, the CDFI worksheet labels and rating bands, and the FDIC time-series workbook. The application file does not provide an explicit Industry_Sector field, and neither the portfolio nor application files provide all debt-to-asset or liquidity inputs required by the CDFI worksheet. Correct submissions must disclose those gaps or label assumptions instead of presenting invented values as source facts.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — fixed NPA and FDIC result | Retained and generalized as new R2 | The instructed formula, Q4 benchmark, basis-point variance, and commentary remain. Exact source results are validation evidence rather than required wording. |
| R2 — fixed 14-loan watch list and scores | Rewritten as new R4 | Complete adversely rated coverage, CDFI factors, adjustments, scale mapping, and OCC actions remain. Hidden loan lists and predetermined factor scores are removed; missing inputs must be disclosed. |
| R3 — mandatory decline of APP-2025-006 | Merged into new R6 and R7 | The application facts and bank thresholds must be analyzed, but the instructions do not prescribe the decision. Any supported decision consistent with the cap and constraints can pass. |
| R4 — mandatory approval of APP-2025-001 | Merged into new R6 and R7 | The original row forced a hidden outcome and specific waiver options. The variant checks whether the recommendation addresses strong credit facts, the existing concentration breach, grandfathering, and the Board constraint. |
| R5 — fixed cross-tab pattern | Retained and generalized as new R2 | Counts, dollars, totals, and observed rating/delinquency patterns remain without hard-coded cells. |
| R6 — APP-2025-003 expected scoring and outcome | Merged into new R6 | Startup risk and mitigants must be analyzed from the source, but no particular adjustment or recommendation is mandated. |
| R7 — APP-2025-004 expected decision details | Merged into new R6 | Source metrics, policy analysis, capacity, and concentration remain required without a predetermined approval result. |
| R8 — Ironbridge expected classification and action list | Rewritten and merged into new R4 and R8 | Largest-problem-credit collateral and workout analysis remain. A fixed category and checklist are replaced by source-responsive CDFI and OCC treatment. |
| R9 — APP-2025-002 expected outcome and sector | Merged into new R6 and R7 | The application must be analyzed, but the input lacks an explicit sector field. The variant requires transparent sector mapping rather than the hidden Retail answer. |
| No original row — complete dashboard | Added as new R1 | Loan-type balances, sector balances, weighted rates, and total yield are explicit but were not directly scored. |
| No original row — +200 basis-point stress | Added as new R5 | This required watch-list analysis had no independent original row. |
| No original row — aggregate allocation and executive summary | Added as new R7 and R8 | The cap, post-lending effects, top-three risks, and Board-facing summary are central deliverables. |

## Material changes and reasons

1. Credit recommendations are evaluated for consistency with displayed facts and constraints, not against hidden expected outcomes.
2. Any objective CDFI factor missing from the inputs must be marked missing; a substituted score must be labeled as an assumption and any resulting category as provisional.
3. Application sector mapping must be explained because pending_loan_applications.csv has no Industry_Sector column.
4. Grandfathering applies only to existing exposure. New funding in a breached sector must be offset by a binding contemporaneous reduction that leaves the post-closing sector at or below 20%.
5. The stress method may use an equivalent sound debt-service calculation if all assumptions are reproducible.
6. Largest problem credits are assessed through a disclosed materiality rule that must include the largest adversely rated exposure, with collateral coverage and OCC-consistent workout actions but no hidden named-loan answer.
7. Portfolio, memo, cap, and executive-summary requirements are separated to avoid double-scoring individual applications.

## Score, output, and trajectory evidence examined

Representative judge reports, outputs, and trajectories:

- Refined Luna landlock: 16/66 in both reports. The workbook contained seven sheets, a correct NPA/FDIC comparison, concentration analysis, watch list, rate shock, and six application rows. Its trajectory separately researched the CDFI sheet, FDIC benchmark, and OCC handbook. It assigned conservative scores to unavailable debt-to-asset and liquidity inputs and declined the strongest healthcare application; the original rubric treated that decision itself as failure. Genuine omissions remained in the PDF's loan-specific detail and largest-problem-credit narrative.
- Sol rubric-gold: 66/66 in all four reports. It produced the full dashboard, cross-tab, watch list, concentration analysis, stress, two-part PDF, and explicit methodology/data-quality discussion. The trajectory used the named external sources and disclosed evidence limits.
- Qwen 3.5 reasoning: 8/66 and 18/66. Its four-sheet workbook omitted a dedicated rate-shock section and did not expose the complete scoring, memo, capacity, or executive-summary logic. The trajectory was substantially shorter and the output contained unsupported or incomplete factor treatment.

The portfolio and application CSVs, CDFI worksheet metadata/content, FDIC workbook structure, OCC reference evidence, output sheets, application rows, trajectory summaries, and judge reasons were inspected directly.

## Likely judge artifacts versus genuine task failures

Likely artifacts or unsupported expectations:

- Mandating approve, conditional-approve, or decline outcomes for named applicants.
- Requiring one specific waiver, participation, or condition package.
- Treating hidden sector classification as source fact when the application file lacks a sector field.
- Requiring debt-to-asset and liquidity values that the named inputs do not supply.
- Requiring every favorable or adverse narrative fact to be repeated verbatim after the analysis already uses the relevant metrics.
- Hard-coding NPA, watch-list membership, cross-tab cells, and portfolio percentages rather than checking the source calculations.

Genuine failures:

- Missing portfolio totals, weighted rates, cross-tab counts or dollars, or FDIC variance.
- Omitting adversely rated loans or using CDFI bands incorrectly.
- Hiding assumptions for missing scoring inputs.
- Missing loan-specific subjective-adjustment explanations or OCC actions.
- Omitting the +200 basis-point stressed debt service and DSCR.
- Missing any of the six memoranda, cap calculations, concentration effects, or conditional terms.
- Exceeding the $3.0 million cap, creating a new concentration breach, or adding unoffset exposure to a grandfathered breach.
- Omitting the Board-facing executive summary or largest-problem-credit workout analysis.

## Weight accounting

- Original total: **66**
- Variant total: **66**
- Reallocation: weight was moved from predetermined application outcomes and hidden source values to the complete dashboard, reproducible rate shock, missing-input handling, aggregate capital allocation, and executive summary.

## Second-pass validation

- Tightened the 20% Board ceiling so grandfathering never authorizes incremental exposure; only a quantified, binding contemporaneous reduction can support funding in an already-breached sector.
- Replaced the undefined “largest problem credits” scope with a disclosed materiality rule that must include the largest adversely rated exposure.
- Removed a standalone benchmark-limitations requirement that was not an explicit deliverable; variance commentary remains required.
- Preserved flexible, evidence-based credit recommendations and provisional CDFI treatment where source factors are missing.
- Deferred missing portfolio, worksheet, FDIC, and OCC reference context in the judge prompt to evaluator infrastructure; no hidden applicant outcomes or control totals were added.
