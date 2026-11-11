# Refinement notes — management_analysts/task1

## Evidence reviewed

- Refined `TASK_INSTRUCTIONS.txt`, original `RUBRICS.json`, source `REFINEMENT_NOTES.md`, and `task_card.md`.
- Local inputs: the three sheets in `Meridian_Plant_Operations_Q1Q2_2024.xlsx`, all 61 complaint records, the 3,240-row manufacturing benchmark, the FRED MCUMFN extract, and the complete VP memo.
- All 35 available judge reports across the recorded runs. Scores ranged from 0/88 to 78/88; no report awarded 88/88.
- Representative outputs and trajectories:
  - Refined Luna landlock: 42/88 in both reports; three deliverables present. Its trajectory used 177 tool calls across 12 session files, including delegated analyses.
  - Sol rubric-gold: 78/88 in both reports and the best available output. Its trajectory used 44 tool calls in one session and produced a five-sheet workbook, memo, and COPQ CSV.
  - Qwen reasoning-on: 8/88 and 20/88; its trajectory used 82 tool calls and produced all three deliverables but used several differing calculation conventions.
  - GPT-5.4: 16/88 and 32/88; inspected as a lower-scoring comparison, including its workbook, memo, COPQ CSV, and trajectory.

## Instruction-supported requirements

The refined instructions support grading the five requested workbook analyses, the stated rate and COPQ formulas, the public MCUMFN benchmark, the supplied defect-distribution benchmark, source-grounded complaint and equipment joins, memo-claim verification, quantified intervention priorities, and a direct consolidation recommendation supported by cost, capacity, equipment, and workforce evidence. They do not prescribe which plant must be worst, which recommendation must be selected, an exact narrative interpretation, or a single numerical result when a documented equivalent method is valid.

The literal complaint worksheet title exceeds Excel's 31-character sheet-name limit. The variant therefore accepts an unambiguous Excel-safe abbreviation when the full requested title is displayed inside the worksheet. This avoids penalizing compliance with an impossible file-format requirement while still requiring exactly five analyses.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — FRED capacity benchmark | Merged into new R1 | Retained the MCUMFN source, six-month mean, plant utilization formula, and comparison. Removed the hard-coded values and the required Phoenix narrative because the instructions require correct comparison, not exact prose or a predetermined interpretation. |
| R2 — defect and downtime quartiles | Merged into new R1 | Retained both percentile distributions, plant defect-rate conversion, and explicit positioning. Removed hard-coded percentile and plant values. Removed the false requirement that Phoenix downtime be above the 75th percentile; source-derived Phoenix downtime is below that cutoff in the inspected outputs. |
| R3 — highest complaint rate | Merged into new R3 | Retained plant/month joining, rates, and severity. Removed the forced Portland conclusion and hard-coded counts; correct source-derived rankings remain gradable without leaking them. |
| R4 — Portland OTD watch item | Merged into new R2 | Replaced the exact Portland sequence and forced memo-alignment narrative with the instructed aggregate monthly series, six-month slope, and characterization. The instruction applies the Watch Item rule to plant–product month-over-month deterioration, not automatically to an aggregate plant trend. |
| R5 — consolidation recommendation | Rewritten as new R4 | Retained the direct board recommendation and four evidence areas. Removed the mandatory anti-consolidation answer, the required Phoenix strategic-capability argument, and the unsupported assertion that workforce issues are ramp-up rather than structural. Either recommendation now passes when the submitted analysis supports it. |
| R6 — VP memo verification | Retained as new R5 | Kept the required verification section and statuses. Replaced the three leaked expected findings with a requirement to test every material memo claim and explain unavailable evidence. |
| R7 — Phoenix workforce causal claim | Rewritten as new R6 | Retained all instruction-required workforce fields and documented averaging. Removed the mandatory causal conclusion about training loss and Phoenix's defects. Expanded the row to cover the otherwise unscored Plant Scorecard and Equipment Risk Matrix requirements. |
| R8 — product-line watch items | Merged into new R2 | Retained all 12 combinations, monthly values, changes, and the two-of-three deterioration rule. Removed the named expected watch items and exact endpoint values. |
| R9 — complaint categories | Merged into new R3 | Retained company/plant category counts and Systemic versus Plant-Specific classification. Removed fixed category totals and required interventions. This also removes overlap with R3. |
| R10 — COPQ summary | Retained as new R7 | Retained the plant rows, `All Plants` summary, formulas, columns, and arithmetic reconciliation. Removed hard-coded totals and added the instruction-supported requirement that the production-cost denominator use monetary inputs consistently. |

## Never-full analysis

No available report scored full credit. The best result, Sol rubric-gold at 78/88, lost the entire 10-point original R3 because it correctly reported Dimensional Tolerance as the largest category at 15 while original R3 criterion 4 incorrectly required Late Delivery, at 13, to be called the most prevalent. The same output passed the other nine rows in both judge reports. This is the clearest persistent ceiling and a rubric contradiction, not a task failure.

Other recurrent failure causes also mixed artifacts with genuine omissions:

- Original R2 criterion 3 required Phoenix downtime to exceed the 75th percentile, while the inspected refined output reported approximately 3.735 against an approximately 3.775 cutoff. Correct positioning was scored wrong.
- Original R4 combined a hard-coded Portland series, an aggregate Watch Item label, a specific VP-memo interpretation, and a systemic-cause conclusion. Only 2 of 35 reports passed the row. The instructions require the series, slope, and characterization but reserve the Watch Item rule for plant–product month-over-month changes.
- Original R5 forced a no-consolidation answer and two hidden arguments. All 35 reports directly addressed consolidation, but only 6 passed the full row.
- Original R7 required exact Phoenix workforce values plus a causal conclusion that turnover wastes training and drives quality. Only 4 of 35 reports passed. The source supports reporting and comparing the metrics; causation remains an analytical judgment.
- Original rows were all-or-nothing: one unsupported or contradictory criterion zeroed the row even when the requested analysis was otherwise complete.

Persistent genuine failures included incomplete month-level trend detail, omitted workforce fields, absent complaint-category breakouts, weak method disclosure, and COPQ files that changed required columns or the `All Plants` label. The revised rubric preserves those substantive checks while removing the hidden answer key.

## Likely judge artifacts versus genuine task failures

Likely artifacts include the Late Delivery contradiction, the Phoenix downtime quartile error, rejecting an explicitly documented 2020/2024 averaging method in favor of a hidden endpoint, requiring an aggregate trend to use the product-level Watch Item label, and forcing a particular consolidation conclusion. Genuine failures remain failures when a deliverable omits required rows, fields, periods, formulas, joins, memo statuses, or arithmetic reconciliation. The refined Luna output, for example, had a strong five-sheet workbook and correct COPQ summary but did not fully report the original rubric's demanded workforce narrative; the variant grades the required workforce fields without requiring that narrative.

## Weight accounting

- Original total: **88**
- New total: **88**
- The second-pass row weights are **14, 16, 18, 10, 8, 10, 12**.
- Six points were moved from the three heaviest workbook-analysis rows to the standalone COPQ deliverable.

## Second-pass validation

- Increased the COPQ row from 6 to 12 points so omission of a primary deliverable cannot retain a near-perfect score.
- Reduced Industry Benchmark, Trend Diagnostics, and Complaint-Production Cross-Reference by 2 points each; the task total remains 88.
- Split the combined method-documentation criterion into separate OEE, composite-ranking, downtime-share, and workforce-aggregation checks.
- Deferred missing-source-context and DOCX-pagination findings to evaluator infrastructure; the rubric retains source-derived and 2–3-page requirements without embedding hidden controls or substituting an extractor-driven word limit.
