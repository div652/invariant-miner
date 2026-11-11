# Refinement notes — personal_financial_advisors/task1

## Instruction-supported requirements

The refined instructions require three exact deliverables: a five-column data-quality CSV, a four-sheet rebalancing workbook, and a client memo of at most four pages. The workbook must audit and clean the named inputs; calculate monthly Treasury, policy-rate, inflation, and S&P 500 measures; fund a $150,000 taxable-account gift; calculate a post-gift target-allocation trade plan; evaluate losses by account type; and compare no-conversion and $100,000 annual conversion scenarios from 2025 through 2040. The memo must use concrete figures, address concentration, recommend a scenario, and integrate the gift, tax, conversion, and rebalancing decisions into Q2-Q4 2025.

The variant assesses numerical values when they are direct source values or necessary calculations from the named inputs. It accepts reasonable rounding, equivalent formulas, explicit daily-versus-monthly definitions, and documented uncertainty. It does not require an unstated investment conclusion, a favorable Roth result, a particular set of trades, or exact prose.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 — Scenario B mechanics and tax | Merged and rewritten into new R6 and R7 | Retained the conversion years, IRA reduction, lower-RMD mechanism, Roth growth, and net comparison. Removed the embedded hard-coded income result and separated balance mechanics from tax correctness so one tax-component error does not erase otherwise correct scenario modeling. |
| R2 — concentration | Rewritten into new R4 | Retained quantification and specific account/ticker/amount trades. Removed mandatory exact holding totals and named replacement funds as scoring targets; the instructions require source-grounded concentration analysis and specific trades, not one hidden trade list or one sector taxonomy. |
| R3 — tax-loss harvesting | Rewritten into new R5 | Retained complete loss-position coverage and account-aware tax treatment. Removed the unsupported requirement to identify newly purchased positions as future harvesting candidates. Removed the hard-coded loss list from the criterion wording while still requiring every source loss to be captured. |
| R4 — yield curve and bonds | Merged into new R2 | Retained correct yield-curve analysis and portfolio-specific bond advice. Removed the mandated “late September” wording, exact year-end yields, a required VGIT-to-BND/AGG trade, and the hidden conclusion that duration must be extended. The instructions allow a defensible recommendation tied to the calculated data. |
| R5 — action timeline | Rewritten into new R8 | Retained gift, filing, conversion, rebalancing, and interdependency coverage. Removed the arbitrary requirement that each action occur in a particular sub-quarter and removed a predetermined Form 709 outcome; the applicable filing treatment must be calculated and sequenced correctly. |
| R6 — S&P 500 return | Merged into new R2 | Retained the required monthly-average calculation, latest 12-month return, and period high. Removed exact-value matching and the claim that the source dataset contains only 13 months; the supplied CSV contains a longer daily history even though the requested analysis window is January 2024-January 2025. |
| R7 — Social Security | Merged into new R7 | Retained provisional-income calculation, both-scenario treatment, and inclusion in total taxable income. Rephrased exact expected figures as source-grounded calculations with reasonable rounding. |
| R8 — balance discrepancy | Merged into new R1 | Retained explicit reconciliation and downstream treatment. Removed the requirement to offer a prescribed list of possible explanations; the required action is to identify, resolve or preserve, and consistently use the discrepancy. |
| R9 — Roth recommendation | Merged into new R7 | Retained cumulative taxes, net savings, and a definitive recommendation. Removed the required conclusion that Scenario B is preferred and the requirement to rely on a TCJA sunset. The memo may recommend either scenario if the model supports it and must document legislative uncertainty. |

New R3 adds meaningful coverage of the gift liquidation, which is a major instructed deliverable but had no dedicated original row. New R6 requires the complete 2025-2040 table rather than checking only selected Scenario B outcomes. New R8 also checks the memo's explicit page and section requirements.

## Evidence examined

All 37 available judge reports for this task were examined across 17 judged run directories. Scores ranged from 0/78 to 68/78. The best-scoring output was the Sol rubric-gold run, which received 68/78 in four reports. Representative lower-scoring outputs and trajectories were inspected from:

- refined Luna landlock: 10/78 and 18/78;
- Qwen 3.5 reasoning: 16/78 in both reports;
- GPT-5.4: 14/78 in both reports;
- Sol rubric-gold: 68/78 in all four reports.

The generated PDFs, CSVs, workbooks, and session trajectories were inspected for those four materially different runs. The best Sol output used monthly S&P averages, a complete gift plan, explicit provisional-income calculations, full loss-position coverage, and a coherent four-page memo. The refined Luna output was operationally strong but calculated taxable Social Security inconsistently in the workbook. Qwen used end-of-month rather than monthly-average market values, used a flat conversion-tax approximation, and contained contradictory gift-sale rationale. GPT-5.4 produced a coherent lower-scoring alternative that recommended against automatic conversions based on its modeled result.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts included all-or-nothing row scoring when one exact-value subcriterion failed; high/low reports assigning different totals to the same output; one report containing a judge-response JSON extraction failure; penalties for omitting exact hard-coded values despite equivalent calculations; and penalties for declining unsupported conclusions such as automatic duration extension or a mandatory Scenario B recommendation.

Genuine failures included missing required workbook fields, using month-end S&P values instead of the instructed monthly average, incomplete provisional-income calculations, treating all Social Security benefits as taxable rather than applying the statutory formula, flat-rate tax approximations instead of the stated brackets, omitting loss positions, and failing to connect the action timeline to gift gains and portfolio composition.

## Never-full analysis

No available report awarded 78/78. The persistent ceiling was produced primarily by rubric design rather than one universal task failure:

| Original row | Reports passing row | Reports failing row |
|---|---:|---:|
| R1 — Scenario B mechanics and tax | 24 | 13 |
| R2 — concentration | 7 | 30 |
| R3 — tax-loss harvesting | 7 | 30 |
| R4 — yield curve and bonds | 4 | 33 |
| R5 — action timeline | 10 | 27 |
| R6 — S&P 500 return | 7 | 30 |
| R7 — Social Security | 8 | 29 |
| R8 — balance discrepancy | 25 | 12 |
| R9 — Roth recommendation | 6 | 31 |

1. **The best output was forced to lose R9.** The Sol rubric-gold output calculated that the four-year conversion ladder increased modeled tax through 2040 and responsibly warned against relying on a presumed TCJA sunset. Original R9 nevertheless required a favorable Scenario B recommendation and a specific TCJA-sunset rationale. Because the row was scored all-or-nothing, this unsupported conclusion cost the full 10 points in every Sol report.
2. **Roth-tax content was triply scored.** Original R1, R7, and R9 overlapped on income components, Social Security, tax totals, savings, and recommendation for 28 of 78 points. A single modeling difference could fail several rows.
3. **Several rows encoded a hidden answer rather than the instruction.** Examples include mandatory duration extension, exact bond trades, a specific daily un-inversion narrative, exact concentration totals, and an exact favorable Roth conclusion.
4. **R6 contained a false data-coverage premise.** It required a statement that the S&P source spans only 13 months, although the supplied daily CSV contains a longer series. The requested calculation window is 13 months; the file itself is not.
5. **R3 added an unsupported future-analysis requirement.** Identifying hypothetical future tax-loss candidates after rebalancing is not required.
6. **Exact-value checks obscured method quality.** Reports repeatedly failed complete analyses for not reproducing one exact memo number or label even when the workbook showed the correct source-grounded method.

The revised rubric removes these ceilings, consolidates overlapping tax checks, adds the omitted gift-plan requirement, and permits either defensible scenario recommendation.

## Weight reconciliation

Original total weight: **78**.

Revised total weight: **78**.

Weight was reallocated from duplicated Roth, hard-coded conclusion, and unsupported future-loss criteria to the previously underweighted gift plan, complete scenario table, data-basis consistency, and memo deliverable requirements.

## Second-pass validation

- Clarified that rolling-return cells may be N/A when the required source window lacks a t-12 observation and required a latest-values summary row.
- Enumerated the market figures required in the memo and added exact filename checks for all three deliverables.
- Deferred missing judge access to portfolio, market, and tax source records as evaluator infrastructure; no expected trades, market values, or scenario totals were embedded.
