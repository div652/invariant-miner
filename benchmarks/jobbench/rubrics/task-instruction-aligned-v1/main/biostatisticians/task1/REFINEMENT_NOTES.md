# Refinement notes — biostatisticians/task1

## Instruction-supported requirements

The refined instructions require three exact Excel deliverables. Eligibility_Analysis.xlsx must apply the observable eligibility filters in a fixed order, show remaining and excluded counts, disclose the unavailable chronic-kidney-disease and broader prior-CVD fields, and compare the final TenYearCHD events/N rate with the proposal assumption. Sample_Size_Justification.xlsx must show the protocol calculation, an empirical-rate recalculation preserving the proposal absolute risk reduction, exactly eight sensitivity scenarios, an adjustment for two interim looks, a recommendation with ICH E9 section citations, and cross-validation with Wan Nor Arifin's calculator. Baseline_Subgroup_Analysis.xlsx must characterize four subgroup dimensions, report events/N and continuous-risk-factor mean/SD per stratum, flag potential effect-modification signals, apply the fewer-than-30 rule conditionally, and complete the specified missing-data assessment.

Direct inspection of the inputs reproduced the sequential population counts and final event rate from framingham.csv, confirmed the proposal parameters and two planned O'Brien-Fleming interim looks, and confirmed that the sample-size spreadsheet is Wan Nor Arifin's Version 2.0 calculator. These values are source checks, not required literal wording; equivalent correct calculations and documented rounding are accepted.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — fixed empirical event-rate result | Rewritten and merged into new R1 | The event-rate calculation and proposal comparison remain. The variant checks the required filters and source-derived events/N rather than making a hard-coded result the question. Population flow and unavailable-field limitations are included to avoid overlap with original R8. |
| R2 — empirical sample-size recalculation | Retained as new R3 | The empirical rate, preserved protocol absolute risk reduction, per-group/total results, and change from primary remain. The wording accepts equivalent correct methods and requires the external-cohort limitation. |
| R3 — eight-scenario sensitivity matrix | Retained as new R4 | The exact 2×2×2 scenario count is explicit in the instructions. Hard-coded treatment rates are replaced with the instructed absolute reductions from the protocol control rate. |
| R4 — four subgroup stratifications | Rewritten and merged into new R5 | The four dimensions and stratum N remain. The required events/N and continuous-variable summaries from original R6 are consolidated into one non-overlapping subgroup-characterization row. |
| R5 — fewer-than-30 flags | Rewritten as new R6 | The original row incorrectly required an undersized stratum to exist. The variant applies the rule conditionally: flag every qualifying stratum, or state that none qualifies. It also removes the claim that ICH E9 itself defines the numerical threshold. |
| R6 — mean/SD per stratum | Merged into new R5 | These statistics are part of the same subgroup table and are no longer scored twice. |
| R7 — fixed highest-missingness result | Rewritten as new R7 | Complete per-variable missingness, source-derived highest missingness, the outcome-association test, interpretation limits, and handling recommendation remain without hard-coding the winning variable or value. |
| R8 — fixed population-flow counts | Rewritten and merged into new R1 | Required filter order, counts, exclusions, and unavailable-field notes remain. Fixed counts are evidence for correctness rather than mandatory rubric prose. |
| No original row — primary calculation and calculator cross-validation | Added as new R2 | The instructions expressly require protocol parameters, per-group/total N, group-sequential handling, and Wan Nor Arifin cross-validation, but the original rubric did not score the complete primary calculation. |
| No original row — regulatory recommendation | Added as new R8 | The instructions require section-numbered ICH E9 treatment of empirical assumptions and interim analyses. |

## Material changes and reasons

1. Eligibility flow and event-rate checks are combined because they use the same final population and workbook.
2. The primary sample-size calculation receives direct weight instead of being inferred from the empirical and sensitivity rows.
3. Group-sequential scoring requires the proposal-specified O'Brien-Fleming method and information times while accepting mathematically equivalent implementations and documented rounding.
4. The risk-tertile method may be calculated or approximated, but its inputs and limitations must be stated.
5. Potential effect modification is treated as an exploratory event-rate signal because the reference cohort contains no randomized treatment comparison.
6. The small-stratum criterion is conditional, so a correct finding that all strata have at least 30 subjects can pass.
7. Missingness scoring distinguishes an association test from proof of MCAR or MAR.
8. ICH E9 section citations are required where the instructions require them, without prescribing exact wording or a hidden recommendation.

## Score, output, and trajectory evidence examined

All 37 available judge reports for this task were inspected. Scores ranged from 10/72 to 62/72. Rubric failure frequencies were R1 2/37, R2 6/37, R3 27/37, R4 22/37, R5 37/37, R6 12/37, R7 7/37, and R8 10/37.

Representative outputs and trajectories:

- Refined Luna landlock: 62/72 in both reports. Its workbooks correctly showed the five-step flow, events/N comparison, primary and empirical calculations, eight scenarios, all subgroup statistics, a smallest stratum of 68, complete missingness analysis, and ICH E9 recommendations. The trajectory separately analyzed Framingham data, sample-size methods, and E9 guidance. Both reports failed only original R5.
- Sol rubric-gold: 62/72 in all four available reports. It produced the complete three-workbook package, eight scenarios, documented subgroup and missingness methods, and explicit data limitations. It also failed only original R5.
- Qwen 3.5 reasoning: 18/72 and 28/72. Its output did not contain the exact eight-scenario matrix, used inconsistent subgroup populations, and omitted substantial per-stratum or missingness detail. Its trajectory used a short direct generation path without the separate validation seen in the stronger runs.
- GPT-5.4: 36/72 and 52/72. It recovered the source event and missingness calculations, but one sensitivity sheet contained 20 scenarios rather than the instructed eight and subgroup presentation was incomplete or inconsistent across the two judgments.

The proposal CSV, framingham.csv, FDA E9 file metadata/content evidence, sample-size calculator metadata, workbook sheets, output formulas and values, trajectory summaries, and every judge failure were cross-checked. Judge evidence was treated as diagnostic rather than authoritative.

## Never-full analysis

No available report scored 72/72. Original R5 failed in all 37 reports. Its three criteria failed 29, 28, and 33 times respectively.

The persistent cause is primarily a rubric logic defect. The correctly filtered data have no stratum below 30; the smallest required subgroup stratum in the strongest outputs is 68. Refined Luna and Sol explicitly stated that no stratum had fewer than 30, yet the judge marked them wrong because the rubric demanded that the analysis “identify” such a stratum and flag it. A correct negative finding was therefore unable to satisfy the row. The row also attributed the task's numerical threshold to ICH E9 Section 5.7, although the refined instructions supply the threshold and E9 supplies broader caution about subgroup interpretation.

Lower-scoring runs also showed genuine failures, including missing subgroup dimensions, incorrect denominators, absent mean/SD fields, no eight-scenario matrix, and missing E9 discussion. Those failures do not explain the ceiling: the best outputs completed the instructed work and still lost all 10 points on R5. New R6 resolves the ceiling by accepting either correctly flagged qualifying strata or an explicit source-correct statement that none qualifies.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts:

- Requiring at least one fewer-than-30 stratum when none exists.
- Treating the absence of an underpowered flag as failure after the workbook explicitly reports that the condition is false.
- Requiring exact hard-coded counts or results instead of an equivalent reproducible calculation.
- Treating one numerical O'Brien-Fleming implementation or rounding convention as the only acceptable method.
- Attributing the task-authored 30-subject threshold directly to ICH E9.

Genuine failures:

- Applying the eligibility filters in the wrong order or on the wrong denominator.
- Omitting unavailable-field limitations.
- Omitting the primary calculation, empirical recalculation, or change from primary.
- Producing other than the instructed eight sensitivity scenarios.
- Omitting a subgroup dimension, events/N, or required mean/SD statistics.
- Claiming treatment-effect modification from an untreated cohort.
- Omitting per-variable missingness, the outcome-association test, or a handling recommendation.
- Omitting the required calculator cross-validation or ICH E9 section citations.

## Weight accounting

- Original total: **72**
- Variant total: **72**
- Reallocation: weight was moved from the impossible unconditional small-stratum row and duplicated subgroup checks to the unscored primary calculation, calculator cross-validation, regulatory recommendation, and conditional subgroup interpretation.

## Second-pass validation

- Applied the source-consistency fix: the primary and sensitivity calculations now require the proposal-specified O'Brien-Fleming method at the proposal's 50% and 75% information times while accepting mathematically equivalent implementations.
- Replaced unverifiable calculator-use wording with a deliverable-visible independent cross-check that displays calculator inputs, outputs, and differences.
- Preserved the rubric's 72-point total.
- Deferred source-record verification to evaluator infrastructure; no expected cohort counts, event rates, subgroup results, or missingness answers were added to the rubric.
