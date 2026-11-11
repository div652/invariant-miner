# Refinement notes — statisticians/task1

## Instruction-supported requirements

- Deliver an executed, reproducible notebook; a workbook with exactly five named sheets; and a two-to-three-page DOCX or PDF memo.
- Use one justified adult obesity survey year, 2023 ERS poverty, income, and unemployment, the December 2021 vaccination snapshot, and correct Census geography.
- Document identifier harmonization, source-specific missingness, duplicates, implausible values, exclusions, and final sample size.
- Report regional and overall descriptives, Pearson correlations with 95 percent intervals, the exact Models (a), (b), and (c), standardized effects, VIF, likelihood-ratio tests, ICC, diagnostics, and three-highest-leverage sensitivity analysis.
- Answer the primary-driver question with a DAG, limitations, sensitivity evidence, and an actionable non-causal policy recommendation.

The local CSVs, ERS long-format files, CDC snapshot, Census geography reference, refined instructions, source rubric, and source notes were inspected.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 2021 obesity filter | Rewritten | Removed the hidden requirement to use 2021 and exclude Florida. The refined instructions explicitly allow one stated survey year justified by temporal alignment. |
| R2 identifier harmonization | Merged into reproducibility/data quality | Retained programmatic names, abbreviations, and state-FIPS harmonization. |
| R3 ICC | Retained | Preserved the four-region ICC and interpretation. |
| R4 VIF | Retained | Preserved variables and thresholds while requiring reproducibility from the displayed design matrix. |
| R5 likelihood-ratio tests | Retained | Strengthened to both instructed nested comparisons and the exact model definitions. |
| R6 sensitivity | Retained | Preserved before/after coefficients, confidence intervals, three highest-leverage observations, and the substantive-change rule. |
| R7 diagnostics | Retained | Preserved all three plots and added explicit observation-specific interpretation. |
| R8 correlation intervals | Retained | Preserved the five variables and interval methods. |
| R9 exact poverty field | Rewritten | The 2023 all-ages state poverty estimate remains required, but the variant scores correct source extraction rather than exact column-name recitation. |
| R10 workbook sheets | Rewritten | Enforces the instruction's exactly-five-sheet requirement and the exact model content, not merely presence of five named sheets among extras. |
| R11 memo conclusion | Retained | Preserves direct answer, standardized comparison, sensitivity, and causal caution without requiring a predetermined substantive winner. |
| R12 data quality | Merged into reproducibility/data quality | Removed the hidden Florida and expected-N assumptions; retained source-specific missingness, duplicates, plausibility checks, exclusions, and justified N. |

The variant adds direct checks for clean notebook execution and the exact Model (b)/(c) specifications because the original rubric could award full credit to analyses that used different models or precomputed state.

## Score and trajectory evidence examined

All 36 available judge reports were summarized. Source-row pass counts were R1 5/36, R2 9/36, R3 6/36, R4 7/36, R5 6/36, R6 4/36, R7 4/36, R8 6/36, R9 20/36, R10 2/36, R11 31/36, and R12 2/36.

Representative outputs and trajectories examined:

- Refined Luna scored 66/116 and 76/116. It used a justified 2022 obesity year and a complete 51-jurisdiction dataset, included the five exact workbook sheets, three embedded diagnostic SVG outputs, model comparisons, ICC, VIF, correlations, and sensitivity. Its notebook was not cleanly reproducible: visible cells referenced undefined objects such as `D`, `model_table`, and `sensitivity_table`, and attempted to read intermediate files not delivered under those names. Written plot interpretation was also incomplete.
- Sol rubric-gold scored 116/116 and 106/116. Despite the full score, its workbook contained seven sheets rather than exactly five. Its Model (b) omitted unemployment, and Model (c) added unemployment and vaccination instead of adding regional structure. The notebook delegated all work to an external build script and documented those nonconforming model definitions. This exposed major coverage gaps in the source rubric and judge.
- Qwen reasoning scored 6/116 in both reports. Its notebook was invalid JSON, it used direct state-name merges rather than the required harmonization, omitted ICC, VIF, likelihood-ratio tests, correlation intervals, diagnostics, regional summaries, and Model (c), and used the demographics file instead of the ERS poverty extraction.

## Likely judge artifacts versus genuine task failures

- **Likely artifacts:** failing any year other than 2021; requiring Florida to be missing and a fixed sample size; treating a complete 2022 or 2023 state set as wrong; failing to recognize embedded SVG diagnostics solely because a text extractor did not expose them.
- **Genuine failures:** invalid or non-runnable notebook, undefined precomputed objects, missing source transformations, wrong Model (b) or Model (c), workbook with extra sheets, absent ICC/VIF/LR tests/correlation intervals, absent diagnostic interpretation, unjustified exclusions, and memo conclusions unsupported by the displayed models.

The Sol full-score result was treated as diagnostic evidence that the source rubric did not enforce central instructions, not as authority that the output was compliant.

## Weight preservation

- Original total weight: **116**
- Variant total weight: **116**
- Weight was reallocated from hidden year, Florida, and value-range expectations to reproducibility, exact model specification, exact workbook structure, source extraction, and complete uncertainty reporting.
