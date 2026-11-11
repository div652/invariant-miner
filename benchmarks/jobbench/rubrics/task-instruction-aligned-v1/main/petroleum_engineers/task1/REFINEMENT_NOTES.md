# Refinement notes — petroleum_engineers/task1

## Instruction-supported requirements

The task requires an integrated Excel workbook and a technical memo. Required analyses include interval-specific Utah FORGE ROP regression and cross-validation, a full-dataset 75th-percentile operating envelope, two-sigma anomaly assessment, BOEM well-level Arps decline fits, a normalized four-factor top-15 intervention score, conditional drilling-problem cross-reference, Oklahoma mud-log/core API matching and depth checks, gas/core comparison, formation tops, a formation-linked risk matrix, crew competency gaps, overall program risk, source lineage, data-quality mitigations, and recommendation confidence levels.

Direct inspection confirmed 7,311 drilling rows and the required ROP/regressor columns, a drilling database containing operations, equipment, personnel, assignments, and reports, a 2024 BOEM extract, 10-digit mud-log APIs, 14-digit core APIs, and limited personnel certification detail. The BOEM file and local drilling database do not provide a guaranteed common well identifier. The core export provides formation/lithology-style fields but does not guarantee a hydrocarbon-bearing indicator. The rubric therefore checks documented attempted matching and gaps rather than forcing nonexistent joins or descriptors.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — fixed ROP threshold and envelope | Retained as the operating-envelope row | The full-dataset percentile and numeric WOB/RPM/pump ranges remain. The exact threshold is source evidence, not required literal rubric wording. |
| R2 — Arps parameters and 1971–2024 range | Split across decline-population, fit-result, and cross-reference rows | qi, Di, time unit, constrained b, history rule, and fit quality remain. The hidden first-production-year range is removed; the instruction requires considering wells by sufficient history, not reproducing a dataset range. |
| R3 — four-factor intervention score and water-cut distribution | Split across factor, weighting, and ranking rows | All four normalized factors, decline's highest weight, rationale, and top 15 remain. The hidden mean and standard deviation of water cut are removed. |
| R4 — greater-than-50-foot depth flags | Split across Oklahoma depth-quality and gas/formation rows | Endpoint comparison and flags remain, together with the separately required matching counts, gas/core review, and formation-tops table. |
| R5 — memo content and confidence | Split across memo-structure and memo-evidence rows | Required sections, quantified findings, all data-quality topics, confidence criteria, and source appendix are assessed. |
| R6 — API formats and mandatory cross-dataset matching | Rewritten into decline cross-reference and Oklahoma API/depth rows | Normalization methodology remains. A documented no-match result can pass where the sources lack a supported crosswalk; forced BOEM-to-OGS or BOEM-to-local matches cannot. |
| No original row — interval regression, CV, and anomalies | Added as separate ROP-model and ROP-validation rows | This is the central Utah FORGE analysis and was largely unscored. |
| No original row — integrated risk, lineage, and crew gaps | Added as separate risk-matrix, program-risk, lineage, and crew rows | These are explicit workbook and memo requirements omitted by the original rubric. |

## Material changes and reasons

1. ROP segmentation is evaluated by documented observed discontinuities, not a hidden set of depth boundaries.
2. Cross-validation may use an equivalent defensible scheme if it reports reproducible errors for each interval.
3. BOEM wells need sufficient monthly history; they are not rejected merely because first production predates 2024.
4. Failed identifier joins are valid findings when matched/unmatched counts and limitations are reported.
5. Gas-show versus hydrocarbon-bearing-core conclusions are not required when the core export lacks the needed descriptor.
6. Formation analogs from Oklahoma must be presented as uncertain analogs for Utah rather than exact stratigraphic equivalence.
7. The personnel database's generic certification levels cannot support invented named credentials or expiry dates.
8. Overall program risk must be quantified, but no hidden score or weighting formula is prescribed.

## Score, output, and trajectory evidence examined

Representative judge reports, outputs, and trajectories:

- Refined Luna landlock: 22/50 and 32/50. It produced a 23-sheet workbook with the full drilling data, four ROP intervals, regression and CV diagnostics, 1,092 decline-fit rows, a top-15 list, OGS matching QA, formation correlation, personnel capacity, and lineage. Its memo reported the source-derived ROP threshold, interval R-squared values, anomaly count, and data limitations. Original R6 failed because it documented that no BOEM/local/OGS crosswalk existed rather than forcing a match; original R2 also produced inconsistent judge interpretations of the large workbook.
- Sol rubric-gold: 50/50 in all four reports. It produced an integrated workbook, a top-15 CSV, and a memo with quantified overall risk, explicit confidence criteria, 1,731 decline fits, documented API normalization, depth flags, crew gaps, and lineage. Its trajectory systematically inspected the three source domains.
- Qwen 3.5 reasoning: 0/50 in both reports. It produced only five workbook sheets, analyzed a truncated 85–405 foot drilling range in the memo, omitted exposed Arps parameter results and normalization detail, and replaced required formation and risk outputs with high-level notes.

The drilling CSV, SQLite schema and samples, BOEM extract structure, mud-log and core workbook sheets, output workbook sheets, memo text, trajectory summaries, and judge reasons were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts or unsupported expectations:

- Requiring first-production dates to span a hidden 1971–2024 range.
- Requiring water-cut mean and standard deviation that the instructions never request.
- Failing a correctly documented absent identifier crosswalk because no match was fabricated.
- Requiring exact API digit handling beyond a documented normalization that preserves the relevant identifier components.
- Treating a large workbook as missing Arps results when the fit table is present and traceable.

Genuine failures:

- Segmenting only a small fraction of the drilling record or not documenting discontinuities.
- Omitting coefficients, R-squared, cross-validated errors, anomaly rules, or numeric operating ranges.
- Reporting no qi, Di, b, time unit, history rule, or fit-quality metric.
- Scoring interventions without all four normalized factors or without decline severity as the highest weight.
- Omitting matched/unmatched counts, endpoint depth checks, formation columns, or unavailable-data limitations.
- Forcing unsupported well matches or hydrocarbon interpretations.
- Omitting crew gaps, overall risk, lineage, memo sections, mitigations, or confidence levels.

## Weight accounting

- Original total: **50**
- Variant total: **50**
- Reallocation: weight was moved from hidden dataset characteristics and mandatory cross-source matches to interval modeling, reproducible decline fits, complete Oklahoma analysis, integrated risk, lineage, and personnel readiness.

## Second-pass validation

- Split the eight coarse all-or-nothing rows into separately weighted analytical stages for ROP modeling, validation, decline fitting, cross-referencing, intervention scoring, Oklahoma data quality, integrated risk, lineage, crew capability, and memo evidence.
- Retained every prior content check while reducing the score lost for one omitted reporting field.
- Preserved the rubric's 50-point total.
- Deferred source-record/model verification and workbook-extraction limits to evaluator infrastructure; no hidden fitted parameters, match counts, rankings, or formation results were added.
