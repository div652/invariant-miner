# Refinement notes — social_science_research_assistants/task3

## Instruction-supported requirements

The refined instructions require three named deliverables: a SQLite database with `cleaned_responses`, `variable_crosswalk`, and unchanged `country_metadata`; an Excel workbook with the five named sheets and specified country-benchmark, descriptive, correlation, regression, and divergence content; and a memo with the three named sections. The instructions directly support checking exact workbook columns, source-grounded percentage calculations, exact Meta/Yale codebook varnames for claimed mappings, ESS Table 1 values for defensibly comparable constructs, the two stated model specifications, the greater-than-15-point divergence rule, and auditable data-quality flags.

The instructions do not require an ESS value for a local construct that is not comparable, a prescribed confidence-interval example, a fixed ranking of variable trustworthiness, or the exact phrase “historical context.” Equivalent correct calculations, defensible `N/A` decisions, and source-specific qualification language must receive credit.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 Country_Benchmarks (10) | Rewritten, weight retained | Retains the required long columns, local and Meta/Yale derivations, ESS accuracy, `N/A`, and difference formulas. Removes the requirement to force ESS “bad impacts” percentages into `cc_worry`; the task requires construct alignment and explicitly asks the analyst to flag imperfect mappings. The revised row grades every ESS value that is actually claimed and accepts `N/A` for a non-equivalent construct. |
| R2 Divergence_Flags (6) | Retained and clarified | Keeps complete threshold detection and specific explanations. Clarifies absolute thresholding, signed differences, one row per benchmark source, and exclusion of missing benchmarks. |
| R3 country_metadata (6) | Merged into database row | The unchanged metadata requirement remains atomic, but it is evaluated with `cleaned_responses` because both are integrity requirements for the same database deliverable. |
| R4 country corrections (10) | Merged into database row | Keeps source-grounded spelling correction, explicit handling of missing countries, joinability, and record-level flags. It no longer requires only the four disclosed examples; all actual corrections and unresolved records are graded. |
| R5 exact Meta/Yale names (10) | Rewritten as crosswalk row (8) | Requires exact codebook varnames for every claimed mapping and `N/A` where no equivalent exists. Removes the unsupported implication that all listed Meta/Yale variables must appear even when no local variable maps to them. |
| R6 memo recommendations (8) | Rewritten, weight retained | Requires concrete named-variable, named-country, and named-source recommendations tied to evidenced limitations. Removes mandatory confidence intervals, a fixed strongest/weakest ranking, exact “historical context” wording, and a prescribed hedge. Those are valid options, not uniquely required outputs. |
| Missing workbook analyses | Added as an 8-point row | The original rubric omitted Descriptive_Stats, Correlation_Matrix, and both instructed regressions. These are major explicit deliverables and now receive direct weight. |

The database requirements receive 10 points, the crosswalk 8, country benchmarks 10, remaining workbook analyses 8, divergences 6, and the memo 8.

## Evidence examined

- Refined Luna run: `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, including both 32/50 and 42/50 judge reports, the SQLite/Excel/DOCX deliverables, and the trajectory that inspected the raw database and aggregate CSV, searched for both external references, and built the three outputs.
- Sol rubric-gold run: `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, four 40/50 reports, output tables, memo, and trajectory. Its workbook included source definitions and comparability columns, but the original judge still zeroed R1 for blank-versus-literal-`N/A` handling.
- Qwen 3.8 reasoning run: `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`, two 40/50 reports, a detailed crosswalk and memo, and a trajectory with extensive source and workbook processing.
- Qwen 3.5 reasoning run: `qwen35-main-256k-32k-reasoning-on-20260928T132706Z`, 6/50 and 16/50 reports and lower-scoring outputs. Its wide benchmark layout, sparse divergence sheet, nonconforming crosswalk columns, and invalid memo artifact are representative genuine failures.
- Source inputs: the 802-row respondent/response database, 15-row metadata table, 4,705-row Meta/Yale aggregate, supplied Meta/Yale codebook, and supplied ESS report.

## Never-full analysis

Across all 38 available judge reports, no report scored 50/50. R1 failed in 35 reports and R6 failed in 28; R5 failed in 10, R2 in 6, and R4 in 5, while the metadata row did not fail. The best observed score was 42/50, reached by refined Luna and other Luna variants. Sol rubric-gold and Qwen 3.8 reasoning topped out at 40/50.

The dominant persistent cause was an all-or-nothing Country_Benchmarks row that mixed genuine structural requirements with two brittle expectations: literal `N/A` rather than an empty spreadsheet cell, and extraction of ESS “bad impacts” figures into a local worry comparison even when the output documented that the constructs were not equivalent. High and low judges disagreed on the same refined Luna workbook: one accepted blank cells as `N/A` and accepted the defensible omission of bad-impact values, while another failed both criteria. Because one criterion failure zeroed the entire 10-point row, otherwise strong outputs could not recover.

The second persistent cause was the memo row. Twenty-eight reports failed the mandatory confidence-interval recommendation, and many also failed a prescribed trustworthiness ranking, exact historical-context framing, or prescribed hedging. Those recommendations are sensible, but the task only requires concrete, source-specific qualifications. Treating one particular recommendation set as mandatory repeatedly removed all 8 points from memos that did discuss wording, temporal, sampling, and construct limitations.

Some recurring failures were genuine: wide rather than instructed long benchmark layouts, missing required columns, incorrect response-level aggregation, incomplete divergence enumeration, vague repeated explanations, missing blank-country handling, and invented or malformed codebook variable names. The revised rubric keeps those failures scoreable while separating them from judge-dependent formatting and memo-preference artifacts.

## Likely judge artifacts versus genuine task failures

Likely artifacts include disagreement over blank cells versus literal `N/A`, disagreement over whether ESS bad-impact percentages had to be forced into a non-equivalent worry row, and zeroing a memo for omitting one preferred statistical recommendation. Genuine failures include incorrect calculations, nonconforming columns, unsupported mappings, omitted threshold crossings, unhandled source anomalies, and missing requested regression or descriptive analyses.

## Weight check

Original total: **50**. Variant total: **50**.
## Second-pass validation
- Added a separate 4-point structural row for the three exact filenames and the workbook's exact five-sheet set.
- Reallocated one point from database cleaning, one from Country_Benchmarks, and two from the memo; the rubric total remains 50.
- Kept exact mappings, country corrections, benchmark values, and divergence answers out of the rubric. Full-table SQLite inspection and source-reference validation remain evaluator-infrastructure requirements.
