# Refinement notes — civil_engineers/task1

## Instruction-supported requirements

- Deliver `Miller_Creek_Culvert_Estimate.xlsx` with the six requested worksheets.
- Show every takeoff quantity, unit, and calculation, including a parallelogram excavation footprint and four individually adjusted wing walls.
- Verify every cast-in-place reinforcement bar mark against published unit weights, report discrepancies and subtotals, add waste, and exclude precast reinforcement from the priced steel.
- Compare every defensibly comparable local item with WSDOT Contract 24Z011 using the required eight columns and variance formula.
- Apply the prescribed 8%, 12%, and 15% confidence-based contingency tiers to every detailed-estimate line and calculate a cost-weighted average.
- Select the mobilization tier from the local cost table based on the calculated subtotal.
- Document assumptions, price-selection rationales, and risks.

## Original rubric disposition

| Original row | Disposition | Exact reason |
| --- | --- | --- |
| R1 parallelogram excavation | Retained and broadened. | The geometry is explicit, but the revised row accepts `72/cos(15°)` or an equivalent geometric derivation and also grades the complete takeoff and perpendicular dimensions. |
| R2 WW-1/WW-2 weights | Retained and generalized. | The source-derived values remain checkable, but the instructions require verification of every bar mark, subtotals, discrepancies, waste, and final carry-through, not only two selected bars. |
| R3 contingency tiers | Retained. | The 8/12/15 rates and weighted average are explicit. The revised criteria grade every line item and do not add example classifications that the instructions do not prescribe. |
| R4 epoxy rebar | Retained and merged into reinforcement and detailed-estimate rows. | Matching the specified epoxy-coated bar type and avoiding precast double counting are explicit. The approximate hard-coded total cost was removed because the rubric should evaluate the source quantity and multiplication, not one rounded expected answer. |
| R5 wing-wall skew | Retained and merged into the quantity row. | Four individual walls and the acute/obtuse geometry explanation are explicit deliverables. |
| R6 mobilization | Retained and expanded into executive-summary arithmetic. | The tier is source-driven and must reconcile with subtotal, contingency, and total estimate. |
| R7 WSDOT comparison table | Retained and strengthened. | The revised row accepts either displayed values or formulas that evaluate correctly, requires compatible units, and retains every required column and rationale. |
| Missing original coverage | Added. | The original rubric did not score workbook completeness, all takeoff lines, all reinforcement marks, assumptions/risks, or cross-sheet consistency. |

## Score and trajectory evidence examined

- Aggregated 36 judge reports across 17 runs.
- The refined Luna workbook scored 50/50 with the low judge and 44/50 with the high judge. The high judge treated formula cells in the variance column as blank, while the low judge accepted the same workbook.
- Sol rubric-gold scored 50/50 with both judges and provided the most complete six-sheet workbook.
- Qwen 3.8 reasoning scored 34/50 and 40/50. Its trajectory used noncompliant 5/10/15/20 contingency bands despite otherwise detailed geometry and pricing work.
- GPT-5.4 scored 22/50 and 28/50 and produced a structurally complete but less instruction-aligned workbook.
- Detailed trajectories and workbook contents were inspected for those four runs. The refined, Sol, and Qwen runs showed materially different calculation and contingency approaches.
- Source inputs examined included the specifications, local cost table, takeoff template, reinforcement schedule, and the WSDOT 24Z011 bid tabulation. The WSDOT document contains usable comparators such as pavement removal, crushed surfacing, and cement concrete pavement.

## Likely judge artifacts versus genuine task failures

### Likely judge artifacts

- The 44/50 versus 50/50 refined-Luna split arose because one judge evaluated uncached formula cells as missing variance values. A correct formula is valid evidence when it evaluates to the instructed variance.
- Original rows used hard-coded rounded bar weights and costs. Minor rounding differences or an equivalent subtotal convention should not fail otherwise correct verification.

### Genuine task failures

- Several runs used contingency rates other than the explicitly required 8%, 12%, and 15%.
- Many runs omitted some comparable WSDOT items or did not provide a rationale on every comparison row.
- Some workbooks used generic sheet names with spaces and omitted the exact six requested sheets.
- Some outputs verified only selected rebar rows rather than every bar mark and subtotal.
- Mobilization was sometimes added to the wrong cost base or not tied to the source tier.

## Weight accounting

- Original total weight: **50**
- Variant total weight: **50**
- Weight moved from two hard-coded wing-wall answers and one approximate rebar total to complete quantity, reinforcement, pricing, contingency, assumptions, and workbook-consistency coverage.

## Second-pass validation

- Replaced undefined "material discrepancy" and "ordinary rounding" language with displayed-precision rules that keep every difference visible.
- Made comparison completeness auditable through a stated scope-and-unit matching rule and documented exclusions, without prescribing which WSDOT rows must match.
- Deferred missing judge access to the local inputs and Contract 24Z011 as evaluator infrastructure; no hidden quantities, prices, or mappings were added.
