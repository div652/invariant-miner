# Civil Engineers Task 3 — Task-Instruction-Aligned Rubric Notes

## Instruction-supported requirements

The refined task requires three deliverables: a four-tab estimate workbook, a value-engineering CSV, and a one-page summary memo. The workbook must independently verify every computed CSV quantity, show reproducible inputs and assumptions, apply the stated percent-difference rule and Alaska DOT rounding conventions, use actual CDOT item codes, follow the CDOT-first price hierarchy, total only the authorized base scope, and apply the specified markups. The value-engineering comparison must compare full replacement with an HPC overlay over 30 years, use the Michigan LAP Deep Overlay price with a stated Region 1 adjustment, and make a supported recommendation. The memo must cover total cost, cost drivers, data findings, and at least three specific design risks including environmental and timing concerns.

The rubric may check values necessarily derived from the named inputs. Examples include approximately 221.5 CY for removal of the 7.5-inch existing slab over 9,567.5 SF, approximately 236.2 CY for an 8-inch new slab over the same area, approximately 92.1 LF of skew-adjusted joint length, and approximately 57,400 lb of rebar under the CSV's stated 6-percent slab-weight method. The rubric does not treat an unsupported girder-flange width or an unprovided repair quantity as a known fact.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1, deck-area reconciliation (6) | Rewritten and merged into new rows 1 and 2 | Retains the source-derived slab check, but evaluates it within the instruction-required reconciliation of every quantity rather than as an isolated hidden target. |
| R2, skew-adjusted joints (10) | Rewritten and merged into new row 2 | Retains the necessary skew calculation and expected range because both dimensions and skew are supplied. The separate large weight is removed to reduce overlap with the complete takeoff review. |
| R3, mandatory pier-cap add-alternate (10) | Removed | The refined instructions require the base scope to match the authorization memo. They do not require pier-cap patching, a $360/CFT add-alternate, or a particular judgment about bearing-seat repairs. New row 4 allows optional work only when clearly separated from the base estimate. |
| R4, CDOT item codes (8) | Retained and broadened in new row 3 | Keeps actual CDOT codes and required estimate fields, while also checking adopted quantities, source traceability, and arithmetic. It does not require example code families when another applicable code is correctly supported. |
| R5, overlay cost and forced replacement recommendation (10) | Rewritten in new row 5 | Keeps the required Michigan Deep Overlay price, Region 1 adjustment, service-life assumptions, lifecycle calculation, and recommendation. Removes the hidden requirement that full replacement must win and the unsupported fixed 50–75/20–30-year ranges; an equivalent documented lifecycle analysis may support either conclusion. |
| R6, 42-inch BT-54 flange and approximately 20.9 CY haunch (8) | Rewritten in new rows 1 and 2 | The named inputs do not provide the asserted 42-inch top-flange width. The variant rewards a reproducible source-supported check or an explicit provisional quantity instead of forcing an invented dimension and numeric result. |
| R7, reconciliation table (10) | Retained and expanded in new row 1 | Preserves the required columns, formula, and flagging rule, while enforcing the instruction's broader requirement to verify every computed CSV quantity and disclose unresolved inputs. |
| R8, pricing hierarchy and at least two sources (6) | Rewritten in new row 3 | Preserves CDOT as primary and secondary sources only for uncovered items. Removes the unsupported requirement to use at least two sources even if CDOT covers all estimate items, and removes hard-coded example prices as scoring targets. |
| R9, memo risks (8) | Retained in new row 6 | Preserves three distinct risks plus environmental and timing coverage. It accepts source-grounded equivalent risks rather than requiring a fixed list or exact wording. |

The new six-row structure removes overlap among isolated quantity checks, reconciliation, estimate construction, cost summary, lifecycle analysis, and memo communication.

## Evidence examined

Reviewed the refined `TASK_INSTRUCTIONS.txt`, original `RUBRICS.json`, source `REFINEMENT_NOTES.md`, the bridge quantity CSV, project memo, Alaska guide, CDOT item and cost books, and Michigan worksheet. Representative outputs and root trajectories were examined from `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, and `gpt54-high-exa-main-20260914T032904Z`.

All 36 available judge reports were analyzed. Original-row pass counts were R1 25/36, R2 12/36, R3 2/36, R4 3/36, R5 4/36, R6 2/36, R7 6/36, R8 3/36, and R9 5/36. The refined Luna output scored 6/76 and passed only R1. GPT-5.4 scored 26/76 and passed R1, R2, and R7. Sol rubric-gold was the strongest inspected output, scoring 62/76 under one judge and 68/76 under another; it failed R4 under both and R8 under one.

## Never-full analysis

No report awarded all 76 points. The persistent genuine failures were incomplete quantity-by-quantity reconciliation, reused CSV assumptions instead of independent checks, omission of the skew correction, incorrect or unsupported removal/rebar/haunch calculations, incomplete item-code and price-source traceability, lifecycle comparisons with undocumented scope or renewal assumptions, and memos that did not cover specific environmental and timing risks.

The best-scoring Sol output performed a substantially complete reconciliation and used actual CDOT item codes and source fields, but the judges still denied the item-code row. Its remaining weaknesses centered on source handling and lifecycle presentation rather than a wholesale failure to complete the task. GPT-5.4 correctly found several major quantity discrepancies but left estimate and lifecycle requirements incomplete. Refined Luna adopted too many preliminary quantities and did not establish independent checks.

Three original requirements also made a full score artificially difficult. R3 forced pier-cap patching as an add-alternate even though it is outside the authorized base scope and not required by the refined instructions. R6 forced a 42-inch flange width and approximately 20.9 CY of haunch concrete even though that width is absent from the named inputs. R8 forced use of at least two pricing sources even when the prescribed CDOT source could cover the estimate. Those constraints are removed or rewritten rather than preserved as hidden expected conclusions.

## Judge artifacts versus genuine task failures

Likely judge artifacts include the failure of Sol's item-code row despite actual CDOT codes and required estimate fields, disagreement over its price-source row, and scoring tied to the unsupported pier-patching and flange assumptions. These results are diagnostic evidence that the original criteria were brittle, not proof that the task instructions required those conclusions.

Genuine failures include using 597.3 CY for existing deck removal, omitting skew adjustment, carrying unreconciled preliminary values into the estimate, failing to document assumptions, using secondary price sources before CDOT without justification, mixing optional repairs into the base authorization, or providing an unreproducible lifecycle comparison.

## Weight preservation

Original total: **76**. Variant total: **76**.

Weight was reallocated from the removed pier-cap mandate and unsupported haunch target to complete reconciliation, source-grounded quantity accuracy, authorized-scope control, and reproducible estimate construction.
