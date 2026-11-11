# Refinement notes — management_analysts/task3

## Evidence reviewed

- Refined instructions, original rubric, source refinement notes, and task card.
- Inputs: 500 Greenfield 311 records, all staffing/overtime/process sheets, the NYC expense extract, the 1,000-row selected MMR extract, and the supplied staffing-report evidence referenced by the task materials and outputs.
- All 34 available judge reports. Scores ranged from 6/72 to 72/72.
- Representative outputs and trajectories:
  - Refined Luna: 22/72 in both reports; 79 tool calls across three session files. It produced a 10-slide deck, four-sheet workbook, and memo recommending Proposal B with a limited pilot.
  - Sol rubric-gold: 62/72 and 72/72; 47 tool calls. One judge rejected its MMR figures because they differed from the original rubric's hidden examples; the other accepted the same deliverables in full.
  - Qwen reasoning-on: 12/72 and 30/72; 99 tool calls. It produced 12 slides and a detailed hybrid recommendation but omitted or reframed several threshold analyses.

## Instruction-supported requirements

The instructions require an explicit five-code mapping, a department baseline, threshold-based Proposal B interventions, department overtime cost structure, every process below 70%, high-risk treatment below 65%, division-level turnover feasibility, at least three MMR analogs, at least two Comptroller data points, source-grounded Proposal A totals, a five-dimension comparison, and consistent memo/workbook/presentation figures. They permit Proposal A, Proposal B, or a defined hybrid and do not prescribe specific MMR indicators, a particular recommendation, or a hidden decision-score formula.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — agency mapping | Retained as new R1 | Kept all five mappings and consistent application. Removed the requirement to prove the DHS meaning through four named service categories; the instruction asks for the mapping, not that exact explanation. Added the instruction-required baseline fields and conditional formatting. |
| R2 — Fire overtime | Merged into new R2 | Removed the hard-coded Fire result and “structural dependency” conclusion. Retained department OT ratios, annual costs, city share, and proposal effects. |
| R3 — eight hiring divisions | Merged into new R3 | Removed the leaked count, names, and values. Retained every source division over 12%, hiring targets, and specialized-role feasibility. |
| R4 — MMR benchmarks | Retained as new R4 | Removed the three named expected indicators. Any relevant indicators for at least three analogs now pass when values, targets, corresponding Greenfield metrics, and limitations are shown. |
| R5 — Comptroller report | Retained as new R5 | Removed the hidden menu of acceptable facts. Retained at least two specific, contextualized data points. |
| R6 — service risk | Retained as new R6 | Removed the leaked list and counts. Retained every source process below 70%, the below-65% high-risk rule, and proposal-specific benefit and transition-risk analysis. |
| R7 — turnover feasibility | Merged into new R3 | Removed hard-coded ranges and the required “one in four leaves” wording. Retained division-level turnover and feasibility for cross-training, centralized hiring, and specialized roles. |
| R8 — Proposal A totals | Expanded and split into new R7–R13 | Removed hard-coded totals while retaining source-derived component and merged totals. Proposal A numerical outputs and assumptions, Comparison Summary, memo structure, workbook structure, presentation structure, and cross-file consistency now receive separate rows. |
| R9 — Sanitation seasonality | Merged into new R2 | Removed the hidden expected months and percentages. Retained detection of material seasonal patterns, disclosure of the 10% trigger aggregation, and effects under both proposals. |

## Score and trajectory findings

Original R2, R7, and R9 each passed only 2 of 34 reports, largely because they bundled exact values with required interpretations. The refined Luna output genuinely omitted monthly Fire ratios and detailed turnover evidence, but it was also penalized for not repeating four DHS service categories and for choosing different valid MMR indicators. Sol's identical package received 62/72 and 72/72 solely because one judge required the original rubric's hidden MMR examples. This is a judge/rubric artifact, not a difference in task completion.

Qwen's workbook and presentation were substantial, but its Proposal B sheet and memo did not cleanly enumerate every required trigger and its recommendation model introduced many assumptions. Those are genuine completeness and traceability concerns; the revised rubric checks the required trigger rows and assumptions without penalizing the direction of the hybrid recommendation.

## Likely judge artifacts versus genuine task failures

- **Artifacts:** demanding named MMR indicators when the instruction allows relevant indicators, requiring DHS disambiguation through exact category examples, hard-coded department conclusions, and fixed seasonal months.
- **Genuine:** missing monthly/annual trigger methodology, omitted divisions, absent turnover ranges, incomplete sub-70% process lists, missing proposal transition-risk discussion, inconsistent figures across files, or incorrect deliverable dimensions.

## Weight accounting

- Original total: **72**
- New total: **72**
- R2+R9 originally totaled 18 points and became a 14-point integrated overtime row.
- R3+R7 originally totaled 14 points and became a 12-point workforce/intervention row.
- The 6 released points moved to the proposal-model and deliverable-completeness block, whose seven atomic rows total 12.
- Other rows retain their original 8, 10, 6, and 10-point allocations.

## Second-pass validation

- The former compound completion row was split into separately weighted Proposal A outputs, assumptions, comparison, memo, workbook, presentation, and cross-deliverable consistency rubrics.
- Proposal A now requires numeric projected cycle-time results while accepting any documented source-grounded calculation or scenario method.
- The task's total rubric weight remains unchanged.
- Source-reference access, workbook-style inspection, document pagination, and rendered-slide inspection remain evaluator-infrastructure requirements.
