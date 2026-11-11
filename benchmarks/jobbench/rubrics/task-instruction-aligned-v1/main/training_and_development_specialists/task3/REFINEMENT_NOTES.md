# Refinement notes — training_and_development_specialists/task3

## Instruction-supported requirements

The instructions require a 45-employee by OSHA-course compliance matrix with exactly five statuses, a documented composite employee-risk score, a complete eight-department dashboard, a resource-feasible 13-week plan under the cap, first-four-week remediation, monthly incident-linked-course coverage, and a 6-10 page evaluation framework with evidence-based Level 1 redesign, two course-specific Levels 2-4 plans, KPIs, and ROI.

The instructions do not prescribe which employees or departments must appear in the top 10, nor do they prescribe the identities of the two highest-risk courses. Those results must follow a documented formula applied to the source data. The budget is a cap; ROI should use the actual scheduled investment while relating it to the cap, rather than being forced to pretend the entire cap was spent.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 redesigned Level 1 instrument (10) | Retained as Section 1-2 row (6) | Keeps evidence-linked format and feedback items plus Tool-1A retrospective pre/post. Weight is shared with the required retrospective analysis. |
| R2 knowledge assessments (6) | Merged into Levels 2-4 row (8) | Keeps two courses, 8-10 items, specific OSHA content, and citations. Removes the hidden restriction that the courses must come from a disclosed four-course list; selection follows a documented risk method. |
| R3 observation checklist (10) | Merged into Levels 2-4 row | Keeps observable behavior and subsection citations, now scored with assessments and KPIs as one integrated section. |
| R4 monthly coverage (6) | Retained | Adds direct verification of first-four-week employee remediation and dated monthly rows. |
| R5 ROI (6) | Rewritten, weight retained | Keeps the actual 52/23/129 baseline, benchmark citation, reduction assumption, and Q3 targets. Accepts actual planned cost and an optional clearly labeled full-cap scenario rather than requiring the cap to equal spend. |
| R6 compliance statuses (10) | Retained, weight retained | Keeps 45 employees, OSHA-required courses, exact five statuses, 60-day rule, dates, and mapping documentation. |
| R7 expected top-10 identities/departments (6) | Rewritten as risk/dashboard row (8) | Removes expected concentration and EMP-1001 identity, which are outputs of one assumed weighting rather than task requirements. Requires consistent formula application, actual highest scores, explanations, and all dashboard fields. |
| Training plan resource and cost details | Added direct 10-point row | The original rubric did not directly score instructor/facility constraints, participant rosters, session costs, or running budget. |

## Evidence examined

- Refined Luna: `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, 42/54 and 54/54 reports, both workbooks, eight-page PDF, and trajectory. One judge failed ROI for not monetizing lost days and failed the top-10 row because its calculated employees were not concentrated in the rubric's preferred departments; another judge passed the same deliverables fully.
- Sol rubric-gold: `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, four 54/54 reports, detailed workbooks/PDF, and trajectory.
- Terra: `gpt56-terra-high-exa-main-20260915T074122Z`, two 38/54 reports, outputs, and trajectory. Genuine status failures included a 90-day window and six labels rather than the instructed five; the judge also required full-cap ROI instead of the actual plan spend.
- Qwen 3.8 reasoning: `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`, two 38/54 reports, outputs, and trajectory. It likewise used a 90-day/six-status system and was penalized for not selecting the rubric's expected employee.
- Inputs inspected included 308 training records for 45 employees, 52 incidents with 23 recordables and 129 lost days, 24 training-related incidents across six course codes, 338 surveys, all eight departments, and the Q2 resource schedule.

## Likely judge artifacts versus genuine task failures

Requiring top-10 employees to come from predetermined departments or to include EMP-1001 is a hidden-conclusion artifact because the task leaves risk-score weights to the analyst. Requiring ROI to use the full $38,000 cap even when the executable plan spends less is also misleading. Genuine failures include using a 90-day window instead of 60 days, adding an `Incomplete` sixth status, omitting source-status mapping, violating instructor or room constraints, lacking dated monthly coverage, or providing generic assessments and observation items.

## Weight check

Original total: **54**. Variant total: **54**.

## Second-pass validation

- The ROI baseline now requires the incident-log observation period as well as the incident, recordable, and lost-work-day totals.
- Source/reference attachment and workbook-style inspection for top-ten highlighting remain evaluator-infrastructure requirements; no hidden employee or course identities were added.
