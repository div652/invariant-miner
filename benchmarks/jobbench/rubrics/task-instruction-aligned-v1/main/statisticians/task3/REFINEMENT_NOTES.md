# Refinement notes — statisticians/task3

## Instruction-supported requirements

The task requires a normalized SQLite database, a three-sheet workbook, an executed notebook, and a two-to-three-page PDF memo. The database requirements cover six named tables, specific source fields and formulas, all 15 PLACES measures, exclusions, numeric storage, and FIPS indexes. The workbook requires unemployment-change terciles with omnibus tests, pooled-coefficient Blinder-Oaxaca decompositions, and greater-than-two-standard-deviation outliers. The notebook requires paired static/dynamic models, RUCC controls, LR/AIC/BIC comparisons, multicollinearity assessment, state-level Moran's I, mediation with bootstrap uncertainty, and three figure types. The memo requires five ordered sections, formal numeric results, limitations, recommendations, and three embedded figures.

The instructions require the earliest and latest income years available across the source files and require those years to be labeled. They do not prescribe 2022 as the baseline, require a particular implementation such as a long-to-wide pivot, or reveal the expected model, spatial, mediation, or outlier results.

## Original rubric disposition

- **R1, R2, and R3 — merged and expanded as new R1.** Current, historical, demographic, and exclusions requirements remain. County identifiers, all 15 health outcomes, numeric storage, all-table indexing, and FIPS integrity omitted by the original rows are added.
- **R4 — retained as new R2.** The required terciles, means, test statistics, and p-values remain.
- **R5 — merged into new R5.** Moran's I remains but is assessed alongside model selection, isolate handling, mediation, and required figures.
- **R6 — retained and strengthened as new R6.** The exact section order, formal results, word/page guidance, limitations, recommendations, figures, and cross-deliverable consistency are included.
- **R7 — expanded as new R4.** Model definitions, full reporting, LR tests, information criteria, notebook execution, and VIF handling are all explicit.
- **R8 — removed as an implementation-specific row.** Correct source-field extraction and numeric results are assessed through database contents; a submission is not required to use a particular pivot procedure.
- **New R3 — added.** The original rubric omitted both Metro Decomposition and Outlier Flag Sheet.

## Material changes and reasons

1. The fixed 2022 income baseline was removed because the refined instructions require the earliest and latest available years across the files.
2. Long-format pivot mechanics were removed as a scoring requirement because equivalent correct data-loading methods are allowed.
3. Database scoring now covers all six required tables and all 15 health measures.
4. The exact workbook sheet names and outlier columns are retained because they are explicit.
5. Metro decomposition receives direct coverage.
6. Notebook execution is explicit; code-only or sidecar-result submissions do not satisfy the notebook deliverable.
7. Static/dynamic model reporting, LR/AIC/BIC comparisons, and multicollinearity are assessed for all three outcomes.
8. Spatial, mediation, and figure requirements are grouped by analytic purpose without prescribing numeric conclusions.
9. Memo values must agree with the notebook and workbook rather than match a hidden expected result.

## Score and trajectory evidence examined

Representative reports, outputs, and trajectories:

- **Refined Luna landlock:** 48/54 in both reports. It produced the six required database tables, exact three workbook sheets, an executed notebook, three standalone figures, and a PDF memo. The sole judge failure was an implementation-specific source-attribute expectation even though the population-change result was present.
- **Sol rubric-gold:** 54/54 in both reports. It produced the four required deliverables, an executed 13-code-cell notebook, a three-page memo, and the exact workbook sheets.
- **Qwen 3.5 reasoning:** 14/54. Its database used different required table names, the workbook had four incorrectly named sheets, ANOVA results were separated from the required matrix, the notebook had zero executed code cells, and the memo omitted required formal results and section structure. Those are genuine failures.

The five source CSV schemas, representative database schemas and row counts, workbook headers, notebook execution metadata, output file sets, judge reasons, and trajectory summaries were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include insisting on a particular pivot implementation, a fixed income baseline year, a specific internal source attribute after the required result is correctly derived, or any hidden expected LR, Moran, mediation, or outlier value.

Genuine failures include missing or misnamed required tables/sheets, text-typed measures, absent indexes, incomplete joins without exclusions, fewer than 15 outcomes, wrong change formulas, missing decomposition contributions, wrong outlier threshold, an unexecuted notebook, omitted model comparisons, no multicollinearity assessment, incomplete Moran's I reporting, missing mediation uncertainty, missing figures, or a memo lacking required sections and formal results.

## Weight accounting

- Original total: **54**
- Variant total: **54**
- Weight moved from implementation-specific source handling to the omitted database, workbook, model-comparison, mediation, figure, and consistency requirements.
## Second-pass validation
- Split the 14-point database row into independently weighted source-field coverage, derived-value correctness, exclusions, and SQLite/FIPS integrity rows.
- Added a separate workbook-structure row requiring the exact disparity_profile.xlsx filename and exact three-sheet set; reallocated integer weights without changing the 54-point total.
- Deferred full source snapshots, complete SQLite validation, notebook MIME extraction, and PDF figure rendering to evaluator infrastructure; no hidden county results, model outputs, or figure conclusions were added.
