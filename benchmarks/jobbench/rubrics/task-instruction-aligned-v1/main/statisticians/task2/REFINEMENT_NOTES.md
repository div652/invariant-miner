# Statisticians Task 2 — Task-Instruction-Aligned Rubric Notes

## Instruction-supported requirements

The refined task requires an executed notebook, an exact four-sheet workbook, and an exact two-page PDF. The requested work spans a U.S.-to-Cleveland analytical memo, PCA and clustering, complete country-name reconciliation, a duplicate-free WHO–World Bank panel, an income-group random-intercept model versus pooled OLS, a constrained state obesity adjustment and ranking analysis, an inferential crude-versus-adjusted rank comparison, WLS with sample-size weights and robust standard errors, required plots, and consistent executive communication.

The source files directly support checking the U.S. BMI and Adult Mortality discontinuities, CDC's empty demographic fields, 2024 as the latest CDC year, Tennessee's missing 2024 obesity value, and exclusion of territories from the 50-state-plus-DC analysis. The rubric accepts any statistically defensible adjustment or comparison method that documents its assumptions and uncertainty. It does not require fabricated demographic strata, a specific cluster solution, a fixed set of predictors, or a hidden expected policy conclusion.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1, U.S. BMI anomaly (10) | Generalized and merged into new row 1 | Replaces the mandatory exact source discovery with a requirement to screen and handle any implausible variable actually used, while preserving aggregate-versus-individual interpretation. |
| R2, PCA (8) | Retained and expanded in new row 2 | Preserves indicator selection, missingness, standardization, component justification, and biplot and joins them with the required downstream clustering workflow. |
| R3, clustering (10) | Retained and merged into new row 2 | Preserves algorithm rationale, quantitative k selection, silhouette plot, and descriptive labels without forcing a particular k or label wording. |
| R4, merged panel (6) | Retained and expanded in new row 3 | Preserves the 2000–2015 join and duplicate-free panel and adds the instruction-required complete mapping/drop log and merge counts. |
| R5, unavailable CDC stratification (10) | Retained and merged into new row 5 | Preserves the prohibition on fabricated direct standardization and accepts a documented alternative using external proxy data or a caveated crude analysis. |
| R6, 2024 rankings (8) | Retained and merged into new row 5 | Preserves the latest-year measure, Tennessee gap, and state/territory distinction and adds required adjusted ranks, shift flags, inference, and plot. |
| R7, forest plot (6) | Retained and merged into new row 4 | Preserves the complete coefficient-and-CI plot and adds the model results, random variance, comparable OLS fit, model statistics, and likelihood-ratio comparison required by the instructions. |
| R8, U.S. Adult Mortality anomaly (8) | Generalized and merged into new row 1 | Removes the mandatory exact discontinuity and requires documented handling of material scale, coding, or year-to-year anomalies encountered in the submitted analysis. |

The variant adds dedicated coverage for WLS, robust standard errors, Spearman inference, reconciliation completeness, the full mixed-model comparison, notebook execution, exact workbook sheets, PDF length/topics, and cross-deliverable consistency. These explicit instruction requirements were absent or materially underweighted in the original rubric.

## Evidence examined

Reviewed the refined instructions, original rubric, source refinement notes, WHO and CDC files, UCI Cleveland data, World Bank life-expectancy and metadata files, and representative supplemental income sources used by outputs. Representative outputs and root trajectories were examined from `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, and `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`.

Across 36 judge reports, original-row pass counts were R1 12/36, R2 12/36, R3 4/36, R4 27/36, R5 32/36, R6 16/36, R7 20/36, and R8 12/36. Refined Luna scored 38/66, Sol rubric-gold scored 66/66, and Qwen reasoning scored 48/66.

The inspected Luna notebook was executed without cell errors and produced the required three deliverables, but its analysis used a proxy adjustment and compact generated graphics that required careful method review beyond the original rows. Sol used a single executed analysis cell, documented the U.S. anomalies, produced complete model-comparison fields, retained Tennessee as a missing ranking record, and received full credit. Qwen produced an executed multi-cell notebook, documented an income-proxy alternative and robust WLS, and included ranking notes and inference in the workbook.

## Judge artifacts versus genuine task failures

The original rubric could award all 66 points without directly checking WLS, sample-size weights, robust standard errors, the requested rank-correlation inference, complete name-log decisions, likelihood-ratio fields, notebook execution, exact workbook structure, or the PDF's required topics. Conversely, 18 points were tied to two U.S. source anomalies even though they are only part of the analytical memo. Row-level judge results are therefore incomplete evidence of task completion.

Likely judge artifacts include inconsistent treatment of equivalent documented responses to the impossible direct-standardization request and brittle expectations around exact anomaly wording. A proxy adjustment is not itself a failure when the empty demographic fields, external source, assumptions, and limitations are disclosed.

Genuine failures include treating the WHO BMI field as ordinary individual BMI, using the U.S. mortality break uncritically, performing PCA without scaling or missing-data handling, selecting clusters without quantitative support, omitting mappings or creating duplicate country-year rows, comparing mixed and pooled models on incompatible samples without disclosure, fabricating CDC strata, including territories in state rankings, silently dropping Tennessee, omitting robust WLS inference, or submitting an unexecuted or inconsistent deliverable set.

## Weight preservation

Original total: **66**. Variant total: **66**.

Weight was redistributed from duplicated anomaly checks and isolated plot checks to the complete model, reconciliation, obesity, WLS, and deliverable requirements stated in the refined instructions.

## Second-pass validation

- Removed mandatory exact BMI and Adult Mortality discoveries from the analytical-memo row.
- The rubric now accepts any two defensible macro-versus-clinical discrepancies while requiring every implausible variable actually used to be screened, qualified, corrected, or excluded with downstream effects documented.
- Preserved the rubric's 66-point total.
- Deferred source-data validation and Jupyter MIME-output extraction to evaluator infrastructure; no hidden anomaly values, cluster results, model coefficients, or rankings were added.
