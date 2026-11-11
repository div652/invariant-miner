# Refinement notes — training_and_development_specialists/task1

## Instruction-supported requirements

The refined instructions require five exact deliverables: a completed OSHA checklist gap analysis; a feasible Q2 schedule covering 180 production employees in Safety Orientation and reinforcing programs with declining Level 3 outcomes; a manufacturing-adapted Kirkpatrick evaluation plan; a program-level cost-effectiveness, budget, and break-even workbook; and an instructor risk matrix covering every instructor. The instructions define the Level 3 and cost-effectiveness fields, the 180-day certification window from April 1, 2025, the 200-employee budget population, the fixed 180-person Safety Orientation constraint, required schedule and risk-matrix fields, room-equipment matching, delayed-survey timing, and the exact output filenames.

The variant assesses those requirements through source-grounded calculations and documented assumptions. It does not require a predetermined backup instructor, program ranking, capacity finding, or diagnostic conclusion.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — David Lee recertification and Robert Johnson backup | Rewritten and merged into new R3 | Recertification and named continuity coverage are required. Robert Johnson is not identified in the instructions or instructor CSV as Emergency Response/First Aid-qualified, so forcing him as the backup rewards an unsupported assumption. The new row accepts any named backup whose qualification is demonstrated or whose cross-training is scheduled. |
| R2 — participant-survey adaptations | Retained and rewritten as new R4 | The literacy and shift adaptations are explicit requirements. The new criteria separate plain language, visual scale, oral administration, duration, timing, and distribution so a judge need not infer an exact presentation. |
| R3 — Software/ERP diagnostic questions | Rewritten as new R5 | The instructions require diagnostics for the program derived as lowest on `Level3_Behavior_Change_Pct`; they do not permit selecting a program by a different column or require fixed wording. The row now checks the derivation and at least five relevant barrier areas. |
| R4 — Equipment Operation as highest ROI | Rewritten as new R6 | The prescribed conclusion is numerically inconsistent with the required cost-effectiveness definition. The new row checks the calculation and lets the displayed values determine the ranking. The allocation-percentage requirement remains because it is instruction-supported. |
| R5 — 200-person Q2 projection | Retained and expanded as new R7 | Exact source costs, scenario participant counts, totals, the 180-person Safety constraint, and break-even analysis are required. They are separated from program ranking to avoid an all-or-nothing overlap with R4. |
| R6 — David Lee single point of failure | Rewritten and merged into new R3 and R8 | Expiry, single-point-of-failure, urgency, and source notes are required, but the rubric now derives them from the full instructor roster and qualification data rather than naming the expected row. |
| R7 — capacity analysis and mandatory Martinez constraint | Rewritten as new R8 | The instructions require a comparison of demand with capacity and identification of actual constraints. They do not require Maria Martinez to be called constrained when the submitted schedule remains within her capacity. The lowest-capacity instructor remains a source-derived check. |
| R8 — fixed room assignments | Retained and generalized in new R2 | Equipment-compatible rooms and explanatory notes are required. Equivalent correct assignments are accepted when the room inventory supports them. |
| R9 — delayed survey timing | Retained and merged into new R4 | The 60–90 day timing, application rationale, and shift-aware distribution are explicit requirements. |
| No original row — OSHA gap analysis | Added as new R1 | An entire required deliverable was previously unscored. |
| No original row — observation rubric | Added to new R5 | The supervisor observation rubric is a named required section but was previously unscored. |
| No original row — file, template, and cross-deliverable integration | Added as new R9 | Exact filenames, Smartsheet reference formatting, source traceability, and integrated recommendations are explicit instructions. |

## Score, output, and trajectory evidence examined

All 36 available judge files for this task were inspected, representing 34 distinct reports across main runs. Scores ranged from 0/54 to 48/54; the median was 18/54. Failure counts were R1 15/34, R2 22/34, R3 16/34, R4 34/34, R5 23/34, R6 15/34, R7 25/34, R8 18/34, and R9 24/34.

Representative outputs and `session.v2.jsonl` trajectories were inspected for:

- Refined Luna: 30/54 and 36/54 judge reports. It produced all five files, a nine-page OSHA analysis, a schedule with recertification and backup coverage, and a risk matrix covering all instructors. Its ROI sheet correctly ranked Safety Orientation at 10.78 impact points per $100 above Equipment Operation at 5.77. It misread Leadership Development's 16.3 Level 2 learning gain as a Level 3 value and therefore diagnosed the wrong program. It also reported Martinez below capacity, contrary to the original row's mandatory constraint conclusion.
- Sol rubric-gold: 48/54 in both reports, the best score available. It produced all five files and explicitly documented that Equipment Operation had the highest raw Level 4 impact while Safety Orientation had the highest cost-normalized result. Its trajectory also considered multiple 200-person budget scenarios and the conflict between raw impact and cost-effectiveness.
- Qwen reasoning: 12/54 and 18/54. It produced all five files and selected Software/ERP as the low Level 3 program, but its evaluation plan did not establish the required 60–90 day delay and its continuity and capacity documentation was incomplete.
- GPT-5.4 and Terra outputs were also sampled as lower-scoring contrasts. They commonly omitted recertification, survey accommodations, calculation details, allocation percentages, or equipment-compatible scheduling.

Judge evidence was treated as diagnostic. Workbook cells, document text, source CSVs, and trajectory decisions were checked directly before classifying a failure.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts or unsupported expectations:

- R4 required Equipment Operation to be the highest ROI even though the instruction-defined calculation gives Safety Orientation the higher cost-normalized result.
- R1 required Robert Johnson as the backup solely from department, room, and general safety overlap, without evidence that he already held the Emergency Response/First Aid qualification.
- R7 required Maria Martinez to be called capacity-constrained even when a schedule's documented demand remained below her 12-hour weekly limit.
- Several rows bundled otherwise correct work with a single hard-coded conclusion, causing a zero-weight row score despite mostly correct criteria.

Genuine task failures seen in outputs:

- Misreading Level 2 as Level 3 when selecting the diagnostic program.
- Omitting scenario total costs, formulas, allocation percentages, or break-even assumptions.
- Omitting delayed-survey timing, oral or visual survey accommodations, recertification scheduling, qualified backup coverage, or source traceability.
- Producing incomplete schedule, risk-matrix, or OSHA-checklist coverage.

## Never-full analysis

No available report awarded 54/54. The maximum was 48/54, achieved by both Sol rubric-gold judge reports, and every one of the 34 distinct reports failed original R4.

The persistent blocker is a false expected conclusion inside R4. From `Historical_Training_Effectiveness_Data.csv`:

- Safety Orientation average Level 4 impact is 13.475%; at $125 per participant, its cost-effectiveness is `13.475 / 125 × 100 = 10.78` impact points per $100.
- Equipment Operation average Level 4 impact is 20.2%; at $350 per participant, its cost-effectiveness is `20.2 / 350 × 100 = 5.77` impact points per $100.

Equipment Operation has the higher raw productivity impact, but Safety Orientation has the higher value under the definition the instructions require. The best-scoring Sol output stated this distinction explicitly and still lost all six R4 points because it would not report Equipment Operation as the highest cost-normalized ROI. Refined Luna reached the same correct ranking and was penalized for it. Lower-scoring outputs sometimes failed R4 for genuine omissions such as absent ratios or allocation percentages, but even a complete and mathematically correct submission could not receive full credit under the original row.

The variant removes the predetermined winner, separates ROI ranking from budget and break-even completeness, and checks reproducible calculations instead.

## Weight preservation

- Original total weight: 54
- Variant total weight: 54
- Reallocation: nine rows remain at six points each. Weight was redirected from unsupported named conclusions and overlapping checks to the previously unscored OSHA deliverable, observation rubric, break-even work, exact deliverables, and integration requirements.

## Second-pass validation

- Required documented program-level methods for lowest-performance and declining-trend decisions, accepting defensible full-year alternatives while rejecting unexplained single-row or single-dip shortcuts.
- Required capacity comparisons on a weekly or explicitly normalized basis and explicit identification of the lowest-capacity instructor.
- Replaced visual template-use wording with observable attendance fields derived from the reference template.
- Deferred missing judge access to the source files, PDF form or annotation extraction, and rendered checklist pages as evaluator infrastructure; no instructor, program, room, cost, or checklist answer was embedded.
