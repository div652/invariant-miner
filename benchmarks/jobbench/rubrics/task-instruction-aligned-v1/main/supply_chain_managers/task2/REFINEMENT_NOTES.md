# Refinement notes — supply_chain_managers/task2

## Instruction-supported requirements

- Produce one four-sheet workbook with the exact names and one revised SOP.
- Model each DC's theoretical monthly throughput using the instructed formula, derive actual monthly volume from orders and shipments, show modeled and reported utilization side by side, and quantify recoverable capacity.
- Report warehouse-region volume in all three years and compare target versus current OTD for every mapped region.
- Evaluate every department-warehouse reorder policy, use the supplementary inventory and fulfillment files where they can be joined, identify over-stocking, and quantify capacity or cost recovery.
- Compare approving the stated expansion with a 90-day operational-improvement deferral using impact and payback analysis.
- Revise the SOP around measured failures, replace Section 3.2, provide capacity-recovery and KPI-governance tables, and include dependent 30/60/90-day phases.

## Original rubric disposition

- **Original R1 retained and rewritten as new R1.** Removed hard-coded theoretical-capacity answers. The formula, inputs, intermediate steps, actual volume, utilization, reported comparison, and recoverable-capacity logic remain required. Exact workbook structure was added.
- **Original R2 retained and rewritten as new R2.** Removed the hidden conclusion that all 23 regions must underperform. The revised row requires every mapping row, yearly warehouse-region volume, OTD gaps, and source-supported conclusions.
- **Original R3 retained and rewritten as new R5.** Removed mandatory named department examples. Every revised section must cite a relevant source metric, and the current-SOP gap, capacity table, and KPI governance remain required.
- **Original R4 narrowed into new R7.** Removed the prescribed allocation of cycle counting to Phase 1, automation to Phase 2, and continuous improvement to Phase 3. The instructions require 30/60/90 phases, roles, and explicit dependencies, not those exact contents.
- **Original R5 retained and rewritten as new R6.** The source-data parameter ranges and operational reorder workflow remain explicit requirements.
- **Original R6 removed.** The refined instructions do not require comparison of actual routes with assigned routes or the conclusion that both warehouses serve all regions. Its six points were reallocated to instruction-required Reorder_Optimization and Investment_Recommendation analysis that the original rubric underweighted.
- **New R3 and R4 added.** They score the required reorder scenario, use of supplementary files, recoverable capacity, two capital scenarios, and payback comparison.

## Evidence examined

- Read the refined instructions, original rubric and notes, all four master-data sheets, the current SOP, the 30,870-row orders file, and the supplied inventory and fulfillment files.
- Across 36 available judge reports, original-row pass counts were R1 2/36, R2 24/36, R3 7/36, R4 18/36, R5 10/36, and R6 9/36.
- Refined Luna scored 18/40 in the selected high report and 24/40 in another available report. Direct inspection found all four sheets, the required capacity formula text, demand and reorder tables, two capital scenarios, and a detailed revised SOP. Its trajectory analyzed local sources and obtained the supplementary dataset.
- Sol rubric-gold scored 40/40. Its workbook showed explicit formula steps, three-year demand, reorder recovery, and scenario payback; its SOP cited current-versus-target metrics and supplied 30/60/90 governance.
- Qwen 3.5 reasoning scored 0/40. It substituted pallet counts for theoretical throughput, omitted mapping data and reorder parameters, used wrong phase timing, and supplied generic rather than source-linked SOP changes.

## Likely judge artifacts versus genuine task failures

- Original R6 is a rubric artifact because its route-assignment analysis is absent from the refined task instructions.
- Original R2's all-regions-underperform conclusion and original R3's named metric examples are hidden results. Correct source calculations should determine the conclusion and examples.
- Original R4 overprescribed which changes belong in each phase. A different defensible dependency sequence can satisfy the instructions.
- The refined Luna workbook contains formulas whose cached `data_only` values were blank in one inspection path; a judge that reads only cached values may report missing calculations even when formulas are present. The revised rubric asks whether calculations are present and correct.
- Wrong sheet names, failure to apply the 22 × 1.5 formula, missing actual monthly volume, omitted mapping rows, unused reorder parameters, absent investment scenarios, and generic unsupported SOP changes are genuine failures.

## Weight accounting

- Original total: **40**
- Revised total: **40**
- The six points from unsupported original R6 were redistributed to the required reorder scenario and capital recommendation. The timeline and reorder-process rows were separated and reweighted accordingly.

## Second-pass validation

- Added explicit unit analysis for the capacity model: product-unit volume may be treated as physical utilization only after a documented pallet-day conversion and otherwise must remain a labeled proxy that is not compared directly with reported utilization.
- Anchored over-stocking and reorder-miscalibration rules to demand, lead time, `Reorder_Parameters`, `Department_Targets`, and sensitivity analysis rather than a submission-defined threshold.
- Required the expansion scenario and payback model to reconcile to the stated $1.2M request and disclose treatment of the 12 hires.
- Preserved the rubric's 40-point total.
- Deferred source-record verification to evaluator infrastructure; no hidden capacity totals, routing conclusions, OTD gaps, or reorder answers were added.
