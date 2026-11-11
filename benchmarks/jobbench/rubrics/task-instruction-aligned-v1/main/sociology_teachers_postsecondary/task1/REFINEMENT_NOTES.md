# Refinement notes — sociology_teachers_postsecondary/task1

## Instruction-supported requirements

The refined instructions require an as-of October 21, 2024 workbook for every rostered student, with all eight grade components and Completed/Pending status; validation of every attendance and assignment record; a complete student-by-eight-indicator at-risk matrix; visible priority-weighted risk scores; a monitoring list using the defined buffers; and a plan containing data-quality findings, individual summaries, UCI family-background analysis, WWC-cited strategies, at least three intervention tiers, and differentiated outreach templates.

The grading workbook defines eight components totaling 100%, the Midterm Exam date, and all eight risk thresholds. The database contains 45 students, attendance through November 28, graded and ungraded assignment states, exams, participation, and office-hours visits. Because the deliverable is a Week 10 projection, post-report records must be validated and logged but must not leak into the October 21 calculations.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — projected-grade components | Rewritten as new R1 | The question text assumed a fixed list of completed components even though the instructions say the Midterm Paper is completed when due by the report date and graded. The variant applies the due-date-plus-grade rule directly and accepts the resulting status. |
| R2 — Thanksgiving anomaly | Rewritten and merged into new R2 | The task requires validation of every attendance record, but it does not name Thanksgiving or provide an institutional calendar. The variant checks all material anomalies, post-report leakage, resolutions, and calculation effects without requiring an external holiday conclusion. |
| R3 — eight at-risk thresholds | Retained and expanded as new R3 | Exact source thresholds and complete roster coverage are explicit. Each indicator is made separately checkable. |
| R4 — watch-list buffers | Retained as new R5 | The explicit percentage and participation buffers remain. The variant does not invent monitoring bands for count or binary indicators that the instructions do not define. |
| R5 — first-generation operationalization | Retained and merged into new R6 | The exact proxy definition and coding are instruction-supported. |
| R6 — methodological caveats | Retained and merged into new R6 | UCI source, country, educational level, variable meaning, and non-predictive framing remain explicit. |
| R7 — workbook content areas | Retained and merged into new R8 | The instructions require content areas, not an exact sheet count or order. |
| R8 — assignment date validation | Retained and merged into new R2 | All assignment rows, not only three named examples, must be cross-validated against their source due dates. |
| No original row — composite-score method and tiers | Added as new R4 | Priority weighting, visible calculations, and at least three score ranges are central requirements that were previously unscored. |
| No original row — WWC evidence and individualized interventions | Added as new R7 | The plan's principal evidence-based advising requirement previously had no direct rubric weight. |
| No original row — differentiated outreach templates | Added to new R8 | These are an explicit deliverable section. |

## Score, output, and trajectory evidence examined

All 35 distinct judge reports across main runs were inspected. Scores ranged from 10/68 to 68/68, with a median of 36/68. Original R2 failed in 31/35 reports, R5 in 29/35, R8 in 21/35, and R1 in 19/35. The complete at-risk row failed only 3/35, showing that the original rubric concentrated much of its discrimination on the holiday answer and first-generation wording.

Representative outputs and trajectories examined:

- Refined Luna: 52/68 in both reports. It produced a nine-sheet workbook with all 45 students, all eight indicators, 1,170 attendance audit rows, 225 assignment audit rows, risk contributions, and a watch list. It excluded records after the report date and logged the November 28 record, but judges withheld R2 because it did not label that date “Thanksgiving.” It included the Midterm Paper because the database contains scores for it; the judge nevertheless treated inclusion as failure.
- Sol rubric-gold: 68/68 in both reports. It produced all required analyses and explicitly reasoned about report-date filtering, future records, and the absence of an institutional calendar before labeling the holiday issue.
- Qwen reasoning: 10/68 and 16/68. It produced both files, but only three of the eight indicator names were visible in the matrix, the monitoring logic did not follow the stated buffers, first-generation status was not operationalized, and assignment lateness was not traceable to dates.

The grading workbook, database schemas and record counts, every distinct attendance date, student-por.csv columns, and the four WWC recommendation headings were inspected directly.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts or unsupported expectations:

- Requiring the November 28 record to be identified specifically as Thanksgiving even though it occurs after the report date and no academic calendar is a named input.
- Penalizing a Midterm Paper marked Completed when its due date precedes the report date and a numeric grade is present in the database.
- Treating example watch-list ranges as a requirement to create bands for indicators whose thresholds are counts or binary states.

Genuine failures observed:

- Including post-report records in Week 10 calculations without an as-of filter.
- Omitting rostered students or indicators from the matrix.
- Hiding the priority weights or composite calculation.
- Using the wrong first-generation definition or failing to describe it as a proxy.
- Failing to compare submitted dates with due dates.
- Citing no specific WWC recommendation or offering generic interventions disconnected from student risk evidence.

## Weight preservation

- Original total weight: 68
- Variant total weight: 68
- Reallocation: weight was moved from the unsupported named-holiday answer and overlapping workbook checks to complete data validation, visible risk scoring, WWC-cited intervention design, individual summaries, and outreach templates.

## Second-pass validation

- Added an explicit exception for the `Attendance & Participation` component, whose source due-period is `Ongoing` rather than a dated deadline.
- The interim component is Completed only when it can be calculated from valid records through October 21; the due-date-plus-grade rule continues to govern the other seven components.
- Preserved the 68-point total.
- Deferred the judge's missing course-database, UCI, grading-rubric, and WWC context finding to evaluator infrastructure rather than embedding student answers or citation excerpts in the rubric.
