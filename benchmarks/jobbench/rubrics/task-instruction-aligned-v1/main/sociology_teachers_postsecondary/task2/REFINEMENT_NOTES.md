# Refinement notes — sociology_teachers_postsecondary/task2

## Instruction-supported requirements

The task requires an updated gradebook, a two-row dispute CSV, and an accreditation-ready assessment report. Grades must normalize seven differently scaled components, apply the stated weights, count blanks as zero, and use the five-letter scale without plus/minus grades. The disputes must use the gradebook, attendance, office-hours log, and essay rubric. The report must contain six sections in the stated order, complete grade distributions, normalized descriptive statistics, all ten evaluation comparisons with the OpenIntro baseline, every at-risk student with attendance and office-hours detail, all six essay-rubric categories, a specific Spring 2025 modification, and a two-to-three-paragraph evidence-based reflection.

Direct inspection confirmed 35 students, the assignment and attendance sheets, ten Course_Eval_Summary items, appeal-related office-hours visits, and 463 external evaluation rows with a score field. The rubric PDF supplies six named categories. Source-derived grade counts, final percentages, appeal facts, and the external mean are correctness checks rather than required literal wording.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — fixed grade-distribution counts | Retained and generalized as new R4 | Counts, percentages, section Ns, and the five-letter scale remain. The expected distribution is checked against the updated gradebook instead of embedded in the rubric. |
| R2 — statistics plus named extreme students | Retained and rewritten as new R5 | All seven normalized mean/median/SD comparisons and the largest gap remain. The unsupported requirement to mention specific students and a predetermined variance explanation is removed. |
| R3 — fixed external mean and item conclusions | Retained and generalized as new R6 | The evals score mean, ten item comparisons, differences, and above/below classification remain without hard-coded values. Comparability limitations are added. |
| R4 — six categories and modification | Retained as new R8 | All categories, both essay distributions, and a specific actionable modification remain. The variant prevents unsupported category-level diagnosis from aggregate essay totals. |
| R5 — reflection | Retained and merged into new R9 | The required length, strengths, weaknesses, and evidence-tied pedagogical change remain. |
| R6 — audience, signature, and format | Retained and merged into new R9 | Audience, signature, title/header, ordered sections, and readable required tables remain. |
| R7 — predetermined Caleb Mitchell result | Removed as a student-specific answer row and generalized into new R7 | Caleb must be included if he meets the published at-risk rule, but one student's hidden values should not substitute for complete at-risk coverage. |
| R8 — gradebook columns and expected individuals | Retained and generalized into new R2 | Required columns, calculations, blank handling, scale, and boundaries remain without naming expected top or failing students. |
| No original row — exact deliverable structure | Added as new R1 | Exact filenames are checked in a small structural row rather than consuming weight in the grade-calculation row. |
| No original row — two appeal adjudications | Added as new R3 | The dispute CSV is a full required deliverable and the instructions allow a reasoned Incomplete or estimated-score decision for Sullivan rather than one hidden outcome. |

## Material changes and reasons

1. Grade correctness is judged from the source rows and published formula, not hard-coded distributions or named students.
2. Only A, B, C, D, and F are accepted in the gradebook because the instructions specify that scale.
3. Sullivan's appeal can result in an Incomplete, estimated scores, or no adjustment if the source evidence and uncertainty are addressed.
4. Xu's attendance is contextual only because it is absent from the course weights.
5. At-risk coverage uses the union of all three instructed triggers and requires office-hours dates and topics.
6. Assignment-gap interpretation must discuss central tendency and spread, but no named-student anecdote is required.
7. The OpenIntro mean is a directional benchmark; the report must not imply a matched institutional item-level comparison.
8. Aggregate essay scores may inform overall quality discussion but cannot prove which rubric category caused the distribution.

## Score, output, and trajectory evidence examined

Representative judge reports, outputs, and trajectories:

- Refined Luna landlock: 56/66 in both reports. It produced the correct five-letter distribution, both reasoned appeal decisions, all ten evaluation comparisons, complete rubric-category discussion, ordered report sections, and a detailed at-risk rule. The only failed row was original R2 because the report did not mention the rubric's preferred named high and low performers. Its trajectory separately analyzed grades/appeals and the external baseline.
- Sol rubric-gold: 66/66 in all four reports. It produced correct gradebook columns and distributions, source-grounded disputes, normalized statistics, an explicit benchmark limitation, complete at-risk details, all six essay categories, and a specific rubric redesign.
- Qwen 3.5 reasoning: 22/66 in both reports. It used plus/minus grades and Incomplete values in the gradebook, miscounted absences, reported unsupported grade-boundary claims, used an altered at-risk definition, and omitted or weakened required benchmarking and reflection evidence. Its trajectory was a short direct pass with little validation.

The gradebook sheets, office-hours CSV, evals.csv, essay-rubric evidence, representative output workbooks/CSVs/DOCX text, trajectory summaries, and judge failure reasons were inspected directly.

## Likely judge artifacts versus genuine task failures

Likely artifacts or over-prescriptive expectations:

- Requiring the assignment-gap narrative to cite particular named students and exact scores.
- Requiring a predetermined explanation that Section A has greater variance.
- Hard-coding grade distributions, the institutional mean, individual final grades, or above/below items instead of checking calculations.
- Treating one Sullivan appeal outcome as mandatory when the instructions expressly ask for adjudication between alternatives.

Genuine failures:

- Using plus/minus grades, Incomplete, or any scale other than A/B/C/D/F in Letter_Grade.
- Failing to normalize components or treating blanks contrary to the instructions.
- Omitting either appeal or using attendance as a grade deduction.
- Incorrect section distributions or incomplete seven-component statistics.
- Comparing fewer than all ten evaluation items.
- Missing students who meet any at-risk trigger or omitting office-hours dates/topics.
- Omitting rubric categories, making unsupported category-level claims, or proposing a vague modification.
- Missing the required section order, audience, signature, or two-to-three-paragraph reflection.

## Weight accounting

- Original total: **66**
- Variant total: **66**
- Reallocation: weight was moved from hard-coded student outcomes and the named-example variance artifact to complete appeal adjudication, full at-risk coverage, calculation integrity, benchmark limitations, and a 2-point structural-deliverables row.

## Second-pass validation

- Moved exact filename checks for all three deliverables into a 2-point structural-deliverables row and reduced the grade-calculation row from 10 to 8 points so filename compliance cannot dominate calculation quality.
- Accepted either population or sample standard deviation when one convention is applied consistently across both sections and all seven components.
- Replaced subjective accreditation presentation and professional-format judgments with observable title/header and table-readability checks.
- Deferred missing gradebook, attendance, office-hours, rubric, and external-baseline context to evaluator infrastructure rather than embedding fixed grades or statistics.
- Post-fix re-lint confirmed that exact filename checking is isolated from the grade-calculation row while the total remains 66.
