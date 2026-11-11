# Refinement notes — computer_and_information_research_scientists/task2

## Instruction-supported requirements

The refined task requires four coordinated deliverables: a seven-column discrepancy audit, a comparative strategy analysis, a four-sheet budget, and a corrected schedule. It explicitly requires quote roll-up checks, lead-time/dependency reconciliation, workload-to-node capacity checks, a corrected component-level electrical baseline, workload and wait-time profiling, existing-capacity analysis, the specified cloud pricing and memory tier, the exact hybrid threshold, the six-factor weighted matrix, LBNL facility evidence, an NSF HERD benchmark, cash-basis discount and contingency treatment, single counting of prepaid support, the instructed power formula, three-strategy TCO and break-even analysis, and completion within nine months.

The instructions do not require particular researcher names, a hidden count of sustained workloads, a preselected corrected kW value, a preselected installed-GPU count, or a specific answer to whether break-even is possible. Those results must instead be derived consistently from the named files and the audit's documented resolutions.

## Original rubric disposition

- **R1 and R9 — merged and broadened into new R1.** The Dell power discrepancy and discrepancy-table schema remain examples of the required audit, but the task calls for every roll-up, total, lead time, and dependency conflict.
- **R4 — rewritten as new R2.** Capacity checks now cover every workload's source-defined GPU-memory demand plus aggregate and individual storage without inventing a separate system-memory requirement or hard-coding researchers.
- **R8 and R10 — merged and expanded into new R3.** Workload mix, wait times, and existing infrastructure remain, while cloud-only tiering, cost, peak-to-average demand, and the deficit calculation omitted by the original rows are added.
- **R2 — retained and generalized as new R4.** The exact >500/≤500 split remains because it is explicit, but hidden names, counts, and a predetermined configuration are removed.
- **R3 — retained and expanded as new R5.** Specific LBNL values are still required from the named report, while the omitted NSF HERD benchmark and full weighted-matrix mechanics are added.
- **R5, R6, and R7 — expanded across new R6–R9.** Workbook structure and funding, capital costs, operating costs, and dashboard economics are scored separately. Hard-coded intermediate totals are removed.
- **New R10 — added.** The original rubric did not directly score revised_schedule.csv despite its detailed requirements.

## Material changes and reasons

1. Single-answer power criteria were replaced with an audit-established baseline requirement because the quote contains contradictory component and aggregate values.
2. Named researcher examples and exact workload counts were removed because the instructions require a correct query and classification, not recital of an answer key.
3. The required cloud-only analysis, peak-to-average demand, and wait-time distributions are now explicitly scored.
4. The exact hybrid threshold is retained, while right-sizing is accepted when traceable to workload demand and identified quote removals.
5. LBNL criteria require source-specific numeric evidence but do not embed the expected values in the rubric.
6. The NSF HERD comparison is added because it was absent from the original rubric.
7. Budget criteria now enforce cash-basis treatment and cross-sheet consistency rather than a single hard-coded TCO, while keeping structure, capital, operating, and dashboard checks independently scorable.
8. Funding-source entries must reconcile to funding needs and distinguish sourced amounts from assumptions or unavailable information.
9. The schedule receives dedicated weight because it is a full deliverable, not ancillary evidence, and its critical-path and risk columns must contain defensible values.

## Score and trajectory evidence examined

Representative judge reports, outputs, and trajectories were inspected from:

- **Refined Luna landlock:** 38/82 high and 46/82 low. It produced all four deliverables. High-judge failures included omitted answer-key researcher names, incomplete capacity detail, use of a 76.74 kW baseline rather than the rubric's fixed 86.22 kW, omission of a required BTU example, and incomplete current-infrastructure naming.
- **Sol rubric-gold:** 82/82 in both reports. Its trajectory reported all 45 original schedule rows, valid dependencies, consistent durations, and all four final deliverables.
- **Qwen 3.5 reasoning:** 0/82. It produced the four filenames, but used an aggregate 80/20 hybrid assumption, a 37 kW baseline, an incomplete discrepancy format, and an inconsistent break-even calculation. Its trajectory also relied on an expedited lead-time assumption.

The vendor workbook, project schedule, survey database, HERD workbook, markdown analyses, budget sheet structures, and revised schedules were sampled. The source database contains 45 workloads and ten infrastructure systems; those facts were used diagnostically, not embedded as required wording.

## Likely judge artifacts versus genuine task failures

Likely artifacts include failures solely for omitting named researchers, exact example counts, a preselected corrected power total, a preselected GPU aggregate, or a BTU discrepancy not independently required by the instructions. A submission may resolve contradictory source values differently if the resolution is documented and propagated consistently.

Genuine failures include omitting required discrepancy columns, failing to audit roll-ups or lead times, not comparing workloads with node capacity, using an electrical figure without reconciling the quote, applying the wrong cloud tier or hybrid threshold, failing to right-size hybrid, omitting specific LBNL or HERD evidence, double-counting support, misordering discount and contingency, using the wrong power formula, omitting dashboard metrics, or leaving schedule conflicts unresolved.

## Weight accounting

- Original total: **82**
- Variant total: **82**
- Weight moved from hidden numeric-answer checks to the omitted cloud analysis, HERD benchmark, complete budget integration, and corrected schedule.

## Second-pass validation

- Removed the unsupported requirement to infer a separate system-memory demand from `memory_gb_required`; the rubric now follows the task's GPU-memory use of that field.
- Replaced the undefined “nearly exhausts” test with submission-defined, consistently applied headroom.
- Split the 16-point budget block into workbook/funding, capital, operating, and dashboard rows while preserving all 16 points.
- Added source-aware Funding Sources criteria and strategy-appropriate cost-per-GPU-hour denominators.
- Added substantive validation of `critical_path` and `risk_level`, not only column presence.
- Deferred missing judge reference files and deterministic source checks to evaluator infrastructure; no hidden control totals or expected answers were added.
