# Refinement notes — supply_chain_managers/task1

## Evidence reviewed

- Refined instructions, original rubric, source refinement notes, task card, the complete six-section SOP, the 233-row inventory snapshot, 5,000 sales rows, and all supplier database tables.
- All 35 available judge reports. Scores ranged from 0/64 to 64/64.
- Representative outputs and trajectories:
  - Refined Luna: 20/64 in both reports; 78 tool calls across three session files. It scoped ABC analysis to the inventory snapshot and did not fully reconcile that scope to the broader sales universe.
  - Sol rubric-gold: 64/64 and 58/64; 58 tool calls. One judge treated an added seventh top-level SOP section as a structure failure while the other accepted the same redline.
  - Qwen reasoning-on: 16/64 in both reports; 72 tool calls. Its workbook used prefixed sheet names, included A and B items in the reorder sheet, and selected different contract conclusions.

## Instruction-supported requirements

The instructions support a documented ABC method using `whs_sales`, every supplier's mix, dead stock based on positive on-hand quantity and zero sales in the last six available months, one reorder row per A item, CV and sparse-data limitations, lead-time-driven reorder points, exact scorecard weights, transparent component scores, recommendations for both expiring suppliers, migration scope only when an exit is recommended, a six-section reviewable SOP redline, numbered inefficiencies, performance targets, and visible workbook integration. They do not prescribe supplier rankings, exact SKU counts, named dead-stock or volatile items, a particular normalization method, or a renewal outcome.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — ABC supplier mix | Retained and rewritten | Removed hard-coded supplier shares, counts, class counts, and expected characterizations. Retained every supplier/class cell, totals, dominant A supplier, most-SKU supplier, and added scope/item-normalization disclosure because the two source files cover different SKU universes. |
| R2 — dead stock | Retained and rewritten | Replaced the original rubric's `ANNUAL_COGS_2020 = 0` shortcut with the task's explicit last-six-available-months sales definition. Removed named expected items and suppliers while retaining the item list, supplier concentration, value, space, and working-capital analysis. |
| R3 — CV analysis | Retained and rewritten | Removed hard-coded item examples, count of volatile items, and the assumption that most items must be stable. Retained the formula, all A items, the `CV > 1.0` flag, missing-month treatment, and single-observation limitations. |
| R4 — supplier scorecard | Retained and rewritten | Retained exact weights and source metrics. Removed the fixed ranking because the instructions do not define component normalization. Added a transparent, consistent scoring-method requirement and limitation handling for spend trend. |
| R5 — Winebow recommendation | Expanded | Removed the forced Winebow facts, conclusion, and migration count. The instructions require equally complete recommendations for both Republic National and Winebow, so the row now grades both using the specified evidence fields. |
| R6 — dynamic SOP reorder points | Retained and rewritten | Removed hard-coded supplier lead times and the requirement to use one hidden source. Retained a reproducible demand/lead-time/safety-stock method, required source choice and rationale, seasonality, ownership, cadence, and exceptions. |
| R7 — redline structure | Retained and rewritten | Added the sixth top-level section and all nine steps explicitly, preserved visible original text, numbered inefficiencies, and included the instructed performance targets and escalation cadence. |
| R8 — workbook integration | Retained and rewritten | Retained A-list flow, dead-stock and misalignment references, and inventory-turn linkage. Added exact three-sheet order, while accepting an Excel-safe abbreviation for the overlength second sheet name when its full title is displayed in-sheet. |

## Score and trajectory findings

Original R1, R3, and R5 each passed only 2 of 35 reports because they encoded one hidden classification universe, one missing-month convention, fixed supplier outcomes, and exact examples. The refined Luna output's use of only 233 snapshot SKUs may be defensible for managed inventory, but it claimed portfolio conclusions without fully documenting exclusions from the 5,000-row sales file; that is a genuine traceability problem. Its all-high-CV result may follow from treating absent months as missing rather than zero, which is a method choice that should be disclosed rather than rejected solely because it differs from the hidden answer.

Sol's two judgments disagreed only on whether a change-summary section counted as a prohibited seventh top-level SOP section. The task says to keep the original six top-level sections, so adding a peer seventh section is a real but narrow structural concern; a preface or unnumbered legend should not fail the redline. Qwen's prefixed sheet names and A/B reorder scope are genuine deviations from the requested workbook.

## Likely judge artifacts versus genuine task failures

- **Artifacts:** fixed 2,800-SKU-derived counts, named dead-stock examples, an `ANNUAL_COGS` dead-stock proxy contrary to the refined definition, fixed CV examples, forced supplier rank, hard-coded lead times, and a mandatory Winebow conclusion.
- **Genuine:** undocumented SKU scope, incorrect revenue basis, missing suppliers, failure to apply the six-month dead-stock definition, missing A items, opaque score normalization, incomplete evidence for either expiring supplier, wrong sheet order/scope, or a rewritten SOP that hides the original procedure.

## Weight accounting

- Original total: **64**
- New total: **64**
- All eight original row weights remain **10, 8, 10, 10, 8, 6, 6, 6**.
- R5's existing 8 points now cover both expiring suppliers rather than overfitting only Winebow.

## Second-pass validation

- Removed duplicate scoring of dead-stock and reorder-misalignment linkage from the supplier-scorecard row; the requirement remains in the workbook-integration row.
- Tightened negotiation targets so they must be tied to displayed metrics, contract terms, task targets, or cited benchmarks; data-gap assumptions require quantitative justification.
- Preserved the rubric's 64-point total.
- Deferred source-record checks, formula/dependency inspection, and DOCX tracked-change extraction to evaluator infrastructure; the rubric continues to accept every redline method allowed by the task.
