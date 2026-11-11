# Refinement notes — social_science_research_assistants/task1

## Instruction-supported requirements

The refined instructions require a three-sheet validation workbook with one row per flagged cell, a coding-scheme table, and an error-type-by-variable-category matrix; an executed notebook that merges the three 3,019-row reference datasets, reports merge validation, calculates the three-category productivity distribution, explains the published gap, runs three chi-square tests, and generates a grouped comparison chart; and a four-section briefing document with a ≤200-word quality summary, benchmark table, plain-language test interpretation, three to five caveats, and an embedded notebook chart.

The instructions require validation against both the codebook and matching reference records. They explicitly distinguish entry errors from legitimate outliers. They do not prescribe that every occurrence of one invalid value must receive one fixed label regardless of whether the same value appears in the official reference data.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — nine fixed birth-year findings and labels | Rewritten into new R1 and R2 | Birth-year findings remain part of exhaustive validation. Fixed labels were removed because reference agreement can distinguish a raw-entry error from a source-consistent codebook outlier. |
| R2 — one fixed organization_size missing cell | Merged into new R1 and R2 | Every missing cell and handling action is now assessed, not only one answer-key row. |
| R3 — Summary_Matrix | Retained and expanded as new R3 | The matrix, category membership, and reconciliation to cell-level findings remain explicit. |
| R4 — explanations for 64% gap | Retained as new R5 | At least two substantive explanations remain, without prescribing which explanations must be chosen. |
| R5 — merge | Retained and expanded as new R4 | Before/after counts, unmatched keys, duplicates, cleaning decisions, and execution are now explicit. |
| R6 — visualization | Retained across new R5 and R8 | The chart must exist in the executed notebook and be embedded in the briefing. |
| R7 — Section 1 | Retained as new R7 | The word limit and concrete patterns remain. |
| R8 — benchmark table | Retained across new R5 and R7 | The table values must follow the notebook rather than a hard-coded approximate result. |
| R9 — embedded visualization | Retained as new R8 | The document must contain a notebook-generated image. |
| R10 — deliverable presence | Retained and distributed across new R1, R4, R7, and R8 | Structure and execution are checked in the relevant deliverable rows. |
| No original row — chi-square tests | Added as new R6 | All three tests, statistics, degrees of freedom, p-values, and limitations are explicit instructions but were previously unscored. |

## Material changes and reasons

1. The validation rubric now checks every flagged cell rather than selected birth-year examples.
2. Classification must use both codebook validity and reference agreement, allowing a documented source-consistent outlier or source issue instead of forcing an entry-error label.
3. The fixed 58–59% survey result was removed; the notebook's cleaned denominator determines the correct value.
4. Merge cardinality, duplicate handling, and cleaning decisions are directly scored.
5. All three chi-square analyses received a dedicated row.
6. A chart mentioned only in prose or embedded only in Word does not satisfy the executed-notebook requirement.
7. Workbook totals, notebook cleaning, and briefing values must reconcile.

## Score, output, and trajectory evidence examined

All **37 available judge reports across 17 runs** were examined. Scores ranged from **18/66 to 66/66**, with a median of **48/66**. Original-row failure counts were R1 30/37, R2 2/37, R3 11/37, R4 5/37, R5 20/37, R6 7/37, R7 3/37, R8 11/37, R9 5/37, and R10 7/37.

Representative outputs and trajectories inspected:

- **Refined Luna landlock:** 60/66 low and 54/66 high. It produced 164 cell-level findings, coding and summary sheets, an executed notebook, and a briefing with an embedded chart. It was penalized for birth-year label choices. Its genuine failure was that the notebook contained no plotting code or chart output even though the Word file had an image.
- **Sol rubric-gold:** 66/66 in both reports. It produced 32 consolidated cell or record findings, an executed notebook with visible chi-square and chart outputs, and an embedded briefing chart. It treated the source-consistent 1937 value as a codebook-invalid item requiring follow-up rather than silently changing it.
- **Qwen reasoning:** 60/66 in both reports. It produced 144 detailed findings, visible plots and chi-square outputs, and two embedded briefing images. It lost the birth-year row because 1920 and 1937 received source-aware labels different from the hard-coded answer key.

The codebook, all four CSVs, published PDF benchmark, validation workbooks, notebooks, briefing documents, and trajectories that analyzed source datasets and benchmark evidence were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include requiring every 1890 to be Typo and every 1937 or 1920 to be Impossible Value without considering the matched official record, and requiring one approximate survey percentage regardless of documented cleaning and duplicate treatment.

Genuine failures include missing flagged cells, failure to identify coding-scheme differences, totals that do not reconcile, unreported merge losses or duplicates, unexecuted cells, missing or incorrect productivity collapse, absent methodological explanations, missing chi-square tests or statistics, causal interpretations, no notebook chart, briefing sections out of order, exceeding 200 words, or a linked rather than embedded image.

## Weight accounting

- Original total weight: **66**
- Variant total weight: **66**
- Weight was reallocated from selected birth-year answers and duplicate deliverable checks to exhaustive validation, source-aware classification, merge validation, all three chi-square tests, and notebook-to-brief integration.

## Second-pass validation

- Required separate memo-table rows for all three published productivity categories, with values, variances, and plausible explanations.
- Preserved alternative cleaning, recoding, outlier, and sparse-table treatments when they are documented and source-consistent.
- Deferred missing judge access to the raw/reference files and incomplete notebook-output extraction as evaluator infrastructure; no expected error set, distribution, or test result was embedded.
