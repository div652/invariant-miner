# Refinement notes — management_analysts/task2

## Instruction-supported requirements

The task requires an exactly four-tab workbook and a maximum-five-page Word brief. The model must rank all 19 plants using the five named factors, show raw values, normalized scores, weights, order count, order share, score, rank, and rationale. Scenario analysis must respect shared-port topology, calculate before/after capacity use, and calculate net annual cost impact. Complaint risk uses a precise High-severity plus sub-70% resolution rule. Reconciliation must verify memo claims and code coverage across all six named datasets. The brief must contain the specified sections, three to five candidates, source-grounded metrics, counterarguments, implementation risks, a three-action matrix, and discussion of COO/board alignment and conflict.

The instructions explicitly allow utilization based on orders or Unit_Quant if the submission states the basis and day convention. They do not require a particular candidate, a particular receiving plant, a hidden concentration percentage, or a predetermined close/retain conclusion.

## Original rubric disposition

- **R1 — retained and expanded as new R1.** All five factors remain. The required all-19 coverage, raw/normalized/weight columns, order share, rank, rationale, and declared utilization basis are now explicit.
- **R2 — rewritten as new R4.** The late-rate and coverage checks remain, but hard-coded numerators, denominators, and “seven active plants” are replaced by accurate source-derived results.
- **R3 and R5 — merged and expanded as new R2.** Capacity feasibility and net economics belong to the same scenario analysis. The original example's preferred plant and volume interpretation were removed.
- **R4 — retained and clarified as new R3.** The exact instructed attrition rule remains. Complaint absence is distinguished from observed low risk.
- **R6 — retained and expanded as new R5.** The page limit and all methodology elements are included without embedding hidden coverage counts.
- **R7 — retained and rewritten as new R6.** All candidate metrics and counterarguments remain, while specific plant identities and expected conclusions are removed.
- **R8 — retained as new R8.**
- **R9 — merged into new R1 and new R7.** Order share and data-revealed concentration risk remain assessable, but the hidden PLANT03 percentage and mandatory strategic conclusion are removed.
- **New R7 — added.** The original rubric did not directly score the required implementation risk section or COO/board alignment and conflict.

## Material changes and reasons

1. Hard-coded source results were replaced with source-derived accuracy checks.
2. Order count and Unit_Quant are both accepted utilization bases because the instructions expressly allow either when documented.
3. A candidate may be marked infeasible when topology or capacity prevents redistribution; the rubric does not force an unsafe receiver.
4. Missing freight route mapping may be documented rather than replaced with invented rates.
5. Zero observed orders are not treated as proof that a plant has no activity because the supplied order extract and memo may cover different periods.
6. The complaint flag now exactly follows “Severity High” rather than an undefined “severity at least High.”
7. The hard-coded concentration answer was replaced with a requirement to analyze any material concentration or resilience risk actually revealed by the data.
8. Brief structure, alignment/conflict analysis, and the five-page cap receive direct coverage.

## Score and trajectory evidence examined

Representative reports, outputs, and trajectories:

- **Refined Luna landlock:** 62/80 high and 52/80 low. It delivered the exact four workbook tabs and a Word brief. The high judge failed R3 for using order counts rather than Unit_Quant and failed R9 for not giving the prescribed PLANT03 concentration narrative. The workbook itself documented its basis and disclosed the single-date limitations.
- **Sol rubric-gold:** 70/80 high and 80/80 low. It delivered four tabs and a five-page brief. The high judge's only failure was the scenario row tied to the preferred capacity interpretation/example.
- **Qwen 3.5 reasoning:** 0/80. It produced the two files, but its model substituted order volume for the required port-connectivity factor, used survey data instead of Complaint_Log in the risk matrix, lacked capacity calculations, relied on rough cost estimates, and used an invalid Go/No-Go action. These are genuine failures.

The COO memo, OrderList, PlantPorts, WhCapacities, WhCosts, FreightRates, Survey_Results, Complaint_Log, representative workbook rows, brief text, and trajectory summaries were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include rejecting a documented order-count utilization method, requiring a particular PLANT03 calculation, requiring exact hidden complaint counts in rubric text, or forcing a specific candidate/action. The instruction permits equivalent formulas and expects the analyst to operationalize structural viability.

Genuine failures include omitting a required factor, failing to rank all 19 plants, using the wrong source for complaint risk, not checking receiver capacity or port sharing, inventing freight economics, failing to calculate net impact, omitting coverage reconciliation, missing required brief sections, exceeding five pages, or using actions outside the allowed vocabulary.

## Weight accounting

- Original total: **80**
- Variant total: **80**
- Weight was redistributed from the hard-coded concentration row to comprehensive scenario feasibility, reconciliation, implementation risk, and strategic alignment.

## Second-pass validation

- Added a four-point deliverable-structure row requiring one XLSX with exactly the four instructed tabs and one ordered, maximum-five-page DOCX brief.
- Split the former 14-point composite row into factor construction and score reporting.
- Split the former 14-point scenario row into topology/capacity feasibility and cost-impact arithmetic.
- Preserved all original criteria and the **80-point** total while reducing all-or-nothing score concentration.
- Deferred evaluator-infrastructure work: judges need the canonical local and external datasets to verify source-derived calculations, and rendered DOCX pages are needed to verify the five-page brief and single-page Go/No-Go matrix.
