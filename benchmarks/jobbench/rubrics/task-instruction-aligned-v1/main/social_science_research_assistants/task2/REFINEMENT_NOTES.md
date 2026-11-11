# Refinement notes — social_science_research_assistants/task2

## Instruction-supported requirements

The instructions require comprehensive survey cleaning with an auditable log, OWID per-variable latest-year extraction using the codebook, numeric UNDP annex extraction, conditional imputation from named annex averages, a 30-country GIS file, a sample-median 2x2 typology, all listed descriptive tables, two exactly specified OLS models, and a 4-6 sentence interpretation. Calendar-invalid dates and invalid categories or ranges must be handled; no fieldwork window is stated that makes every valid 2022 or 2025 date erroneous.

Equivalent documented mappings for ambiguous category text are acceptable. Imputation is required only when the source value is genuinely unavailable, and every actual imputation must be traceable.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 duplicates (8) | Merged into comprehensive cleaning row | Retains identification, retained/removed record, and rationale for every duplicate. |
| R2 categorical standardization (6) | Merged into cleaning row | Retains valid categories but accepts any reasonable documented mapping or a documented flag/removal for ambiguous text instead of mandating one arbitrary mapping. |
| R3 invalid/outlier dates (6) | Rewritten | Retains structurally invalid and missing-date handling. Removes mandatory treatment of calendar-valid 2022 and 2025 dates as errors because the instructions specify no survey fieldwork window. |
| R4 typology (8) | Retained and expanded to 10 | Keeps sample medians, exact labels, tie rule, and one row per country. |
| R5 and R6 descriptives (8, 8) | Merged into one 10-point row | Removes overlap and directly covers every descriptive table in the instructions, including gender, education, and stronger-action tables omitted by the original rubric. |
| R7 models (8) | Retained and expanded to 10 | Keeps exact predictors, interactions, coding, side-by-side layout, and all fit metrics. |
| R8 interpretation (8) | Retained as 6 | Keeps length, interaction significance, metric-based fit comparison, and substantive interpretation. |
| R9 imputation (8) | Rewritten within source-indicator row | Makes the requirement conditional on genuine source missingness and retains named annex average, numeric completeness, and logging. |
| Deliverable and cross-output consistency | Added as two 6-point rows | Directly scores exact sheets, GIS schema, numeric/no-blank requirements, cleaned-data-only analysis, and consistency across workbook and CSV. |

## Evidence examined

- Refined Luna: `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, 46/68 and 54/68 reports, workbook/CSV, and trajectory. It produced all requested sheets and complete GIS data, but omitted malformed-date logging and gave an interpretation that did not compare actual fit values or provide enough substantive meaning.
- Sol rubric-gold: `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, four 68/68 reports, detailed workbook/CSV, and trajectory.
- Terra: `gpt56-terra-high-exa-main-20260915T074122Z`, 38/68 and 46/68 reports, workbook/CSV, and trajectory. Genuine issues included aggregate-only typology reporting, dummy rather than ordinal education, and missing AIC/BIC.
- Qwen 3.8 reasoning: `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`, two 28/68 reports plus current outputs and trajectory. The reports claimed entire sheets were missing, while direct inspection of the materialized workbook found Typology_Summary, Descriptive_Stats, and Regression_Results, indicating report/output-version mismatch.
- Inputs inspected included all 508 raw rows, eight duplicate IDs, nonstandard categories, missing/out-of-range worry values, malformed dates, 37 raw country strings mapping to 30 study countries, the HDI annex, and both OWID files.

## Likely judge artifacts versus genuine task failures

Mandatory removal or correction of calendar-valid dates solely because they lie outside an inferred 2023-2024 cluster is an unsupported rubric artifact. The Qwen reports that could not see sheets present in the current workbook are extraction or materialization artifacts. Missing malformed-date handling, wrong typology layout, nonnumeric GIS fields, missing fit metrics, or an interpretation inconsistent with reported results are genuine failures.

## Weight check

Original total: **68**. Variant total: **68**.
## Second-pass validation
- Replaced the hidden per-indicator latest-year requirement with a method-neutral temporal-selection criterion.
- Either latest non-missing values by indicator or the latest complete common year is accepted when the policy is stated, consistently applied, and any fallback is documented.
- The rubric total remains 68. Source-row validation, UNDP parsing checks, and regression recomputation remain evaluator-infrastructure requirements.
