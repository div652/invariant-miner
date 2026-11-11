# Refinement notes — civil_engineers/task2

## Instruction-supported requirements

- Reconcile scope-memo quantities against independent calculations and document memo, independent, difference, adopted, and justification values.
- Estimate Option A as the written full-deck scope and Option B as 40 percent full-depth repair, 60 percent two-inch hydrodemolition and patching, and full-deck overlay, with identical non-deck work.
- Use CDOT as the primary published pricing source, validate against WisDOT and FDOT or local references, and avoid unsourced prices.
- Provide six exact workbook tabs, including a four-layer rebar takeoff, first-principles paint crew-day buildup, and an at-least-eight-item price comparison.
- Apply the stated 8 percent mobilization and 15 percent contingency and account for two-phase, single-lane construction.
- Provide both totals, three largest drivers per option, uncertainty above 20 percent, budget comparison, life-cycle analysis using the stated service lives, assumptions, and one recommendation.

The scope memo, local labor/equipment schedule, FDOT workbook, CDOT and WisDOT references, refined instructions, source rubric, and source notes were inspected.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 paint-area verification | Rewritten | Retained arithmetic verification and reasonableness review. Removed the unsupported requirement to assert a specific “typical” 10–14 foot perimeter range. |
| R2 Option B quantities | Retained and generalized | The 40/60 split, depths, and full overlay remain required. Exact values are evaluated as derived quantities, while equivalent rounding and transparent geometry are accepted. |
| R3 sourced prices | Merged into the pricing row | Removed hard-coded unit-price selections. The instructions require traceable and comparable pricing, not predetermined selection of one listed value. |
| R4 price comparison | Retained in the pricing row | Preserved at least eight items, at least two comparable sources, selection, and rationale. |
| R5 rebar takeoff | Retained and rewritten | Preserved four separate layers and required fields. Removed exact bar counts and full-length assumptions so cover-adjusted lengths, end-bar conventions, laps, and waste can be accepted when documented. |
| R6 Option A concrete | Merged into the option-modeling row | Preserved scope thickness, performance class, volume derivation, and installed-cost completeness. Removed a mandated single unit-price methodology. |
| R7 recommendation | Retained | Expanded to all memo requirements and accepts either option when the quantitative case is coherent. |
| R8 phased premium | Rewritten | The task requires two-phase construction to be priced, but it does not require only the FDOT 20 percent premium. The variant accepts a documented, non-duplicative source-grounded method. |
| R9 workbook tabs | Retained | Strengthened to the instruction's exact six-tab requirement and valid memo format. |

The variant adds explicit summary-arithmetic and quantity-reconciliation coverage that the original rubric only sampled through isolated expected answers.

## Score and trajectory evidence examined

All 37 available judge reports were summarized. Source-row pass counts were R1 4/37, R2 15/37, R3 28/37, R4 28/37, R5 13/37, R6 8/37, R7 27/37, R8 31/37, and R9 27/37.

Representative outputs and trajectories examined:

- Refined Luna scored 34/68 and 42/68. It delivered all six tabs and a valid memo, derived the principal Option B quantities, used a cover-adjusted four-layer rebar takeoff, and included a paint buildup. Material issues included labeling deck concrete as Class H while selecting a CDOT Class D bridge-concrete item, incomplete justification of the girder perimeter, and contradictory memo language about whether Option B was under budget.
- Sol rubric-gold scored 68/68 in both reports. It included the instructed local Class H material plus separate installed components, a transparent 20 percent phasing column, a four-layer takeoff with allowances, 13 multi-source comparisons, and a discounted life-cycle recommendation.
- Qwen reasoning scored 28/68 and 36/68. Its supposed DOCX memo was Markdown text saved with a `.docx` extension, and the workbook used `Painting Buildup` and `DOT Price Comparison` instead of the exact required tab names. The trajectory nevertheless reported successful verification.

## Likely judge artifacts versus genuine task failures

- **Likely artifacts:** requiring a particular typical girder-perimeter range; failing cover-adjusted rebar counts because they did not equal hidden full-dimension counts; requiring the local material-only price rather than accepting a complete comparable installed price; requiring exactly a 20 percent premium instead of another documented phase-cost method.
- **Genuine failures:** invalid memo file format, wrong tab names, missing source consistency between concrete class and selected price, incomplete installed-cost components, absent quantity reconciliation, unpriced phasing, arithmetic inconsistencies, and recommendation text that contradicts the displayed budget comparison.

The high and low judges also disagreed on some method choices in the refined Luna workbook. The variant therefore scores traceability, completeness, and internal consistency rather than one preferred estimating technique.

## Weight preservation

- Original total weight: **68**
- Variant total weight: **68**
- Weight was redistributed from hidden numeric and methodology expectations to complete quantity reconciliation, option scope, source traceability, summary arithmetic, and the instructed memo analysis.
