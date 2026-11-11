# Computer and Information Research Scientists Task 1 — Task-Instruction-Aligned Rubric Notes

## Instruction-supported requirements

The refined task requires four exact deliverables: a feasibility report, a four-sheet allocation workbook, a three-query SQLite script, and an executive memo. Supported requirements include like-for-like GPU performance verification, repricing and facility assessment for Options A–C, a fully constrained Option D with annual cash flows, a 36-month project schedule and general-access reservation, legacy migration and seasonal utilization analysis, a verified cost-per-PFLOPS-hour comparison, source-derived delay and capacity SQL, and an Option D memo covering sustainability, access, procurement lead times, and at least three Epoch AI peers.

Values directly supported by the named inputs may be checked. The H100 dense Tensor FP16/BF16 value is 989.4 TFLOPS; 1,979 is the INT8 figure. The A100 dense Tensor FP16/BF16 value is 312 TFLOPS and the structured-sparsity value is 624 TFLOPS; 780 is not a matching value in the hardware file. The current vendor file gives six weeks for A100 systems, not four. An 18-week H100 lead may be converted to months by a documented consistent convention; the instructions do not prescribe a three-month delay.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1, H100/A100 verification (10) | Retained and merged into new row 1 | Preserves the source-grounded precision corrections and their consequence, while tying them to the required performance table and all original-option calculations. |
| R2, Option D constraints (6) | Retained and expanded in new row 2 | Keeps the $10.8M ceiling, annual caps, vendor limit, and contingency, and adds the facility, sustainability, and access constraints that the instructions say Option D must satisfy. |
| R3, 36-month schedule (8) | Retained and expanded in new row 3 | Preserves all projects, capacity, scheduling constraints, and the Month-13 reservation. The criterion evaluates database projects rather than relying only on a hard-coded name list. |
| R4, migration plan (10) | Retained and merged into new row 4 | Preserves historical utilization and workload transition, but evaluates the full required Migration Plan, Utilization Forecast, and Cost Comparison rather than one fixed utilization record. |
| R5, fixed three-month delay (8) | Rewritten and merged into new row 5 | Removes the unsupported assertion that 18 weeks equals exactly three months. The SQL must state and consistently use a source-derived conversion and assess whether remaining GPU-hours fit before each deadline. |
| R6, urgency formula (6) | Retained and merged into new row 5 | Preserves the exact formula, components, ordering, and zero-denominator handling as one of the three required SQL analyses. |
| R7, memo and peers (6) | Retained and expanded in new row 6 | Keeps Option D, net-zero by Year 2, access, and three peer comparisons. It now requires the publicly specified Epoch AI source and relevant comparison dimensions without forcing named peers. |
| R8, procurement timeline (6) | Corrected and merged into new row 6 | Retains critical-path and parallel-ordering analysis. Corrects the original row's unsupported four-week A100 value to the six-week value in vendor_quote_update.csv and accepts later source-grounded updates. |
| R9, Options A–C facility assessment (6) | Retained and merged into new row 1 | Preserves assessment against power, summer cooling, and floor space and requires quantified throttling. Values are derived from the current proposal and memos rather than treated as freestanding hidden answers. |

No instruction-supported original row was discarded. The material removals are the fixed three-month conversion, the incorrect four-week A100 lead, and brittle hard-coded examples where the refined instructions call for database- or source-derived analysis.

## Evidence examined

Reviewed the refined instructions, original rubric, source refinement notes, proposal, provost memo, budget and vendor files, hardware specifications, workload SQLite database, and available Epoch dataset material. Representative outputs and root trajectories were examined from `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, and `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`.

Across 34 judge reports, original-row pass counts were R1 4/34, R2 29/34, R3 15/34, R4 2/34, R5 3/34, R6 16/34, R7 24/34, R8 8/34, and R9 2/34. Refined Luna scored 26/66, Sol rubric-gold scored 66/66, and Qwen reasoning scored 18/66.

## Judge artifacts versus genuine task failures

Likely judge artifacts include full credit to the Sol memo's peer-benchmark row even though the memo named only two peers, credit to refined Luna's schedule despite mislabeled database scheduling fields, and failures tied to treating a documented five-month conversion of 18 weeks as wrong solely because the original row demanded three months. The original timeline row's four-week A100 statement conflicts with the source vendor file.

Genuine failures include mixing dense and sparse GPU figures, propagating overstated PFLOPS, omitting updated A/B/C costs or facility throttling, exceeding Option D cash-flow or capacity constraints, producing duplicate or infeasible schedule months, failing to reserve general access, omitting historical-utilization analysis, writing SQL against nonexistent fields, or benchmarking fewer than three qualifying peers. Qwen's inspected output showed duplicate schedule months and inconsistent performance bases; these remain scoreable failures under the variant.

## Weight preservation

Original total: **66**. Variant total: **66**.

Weights were consolidated around the six complete instruction-defined analyses. SQL and memo weights now cover the full requested deliverables, while unsupported fixed conversions and incorrect source values carry no independent weight.
## Second-pass validation
- Added a source-grounded Option D optimization criterion requiring a reproducible throughput objective and comparison of feasible configurations while accepting equivalent optimization methods and stated tie-breaks.
- Preserved the rubric's 66-point total.
- Deferred source-file availability, Epoch dataset context, and deterministic SQL execution to evaluator infrastructure; no hidden expected configuration, query result, or benchmark answer was added.
