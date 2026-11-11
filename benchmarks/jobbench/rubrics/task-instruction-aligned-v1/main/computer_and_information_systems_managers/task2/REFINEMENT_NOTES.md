# Refinement notes — computer_and_information_systems_managers/task2

## Instruction-supported requirements

- Reconcile ITSM configuration items with inventory assets, annotate discrepancies and probable causes, identify the top 10 incident drivers, and surface high-reassignment process gaps.
- Apply the instructed on-premise, CPU, warranty, and Critical-asset exception rules using a calculated fleet incident median.
- Produce comparable on-demand, one-year-reserved, and three-year-reserved AWS monthly and three-year costs, including upfront fees and documented sizing and pricing assumptions.
- Sequence security-sensitive candidates after PRJ-2024-042 where network segmentation is a dependency.
- Map reassignment gaps to official NIST CSF 2.0 subcategories, test coverage against every pending project, estimate unsupported gaps, and distinguish project-specific remaining funds from broader budget headroom.
- Deliver the exact four-sheet workbook and seven-field CSV, with the instructed action vocabulary, flags, conditional formatting, and 5–7 quantified board recommendations.

## Original rubric disposition

- **Original R1 rewritten as new R1.** Removed the hard-coded fleet size, median, asset examples, exclusions, and approximate candidate count. Those values are derivable from the inputs, but the fair criterion is correct application of the rule. Reconciliation quality, top incident drivers, and reassignment analysis were added because the instructions require them.
- **Original R2 rewritten as new R2.** Removed the fixed seven legacy calculator labels and embedded example prices. The revised row accepts equivalent instance mappings but still requires all three pricing modes, upfront fees, three-year TCO, cost flags, and enough pricing context to reproduce the estimate.
- **Original R3 rewritten as new R3.** Removed the fixed expected asset IDs. The revised row derives security sensitivity from `Associated_Service` and `Asset_Type`, then checks only final candidates. PRJ-2024-042 values must come from the local portfolio.
- **Original R4 retained and atomized as new R4.** The 5–7 recommendation count, quantified support, dollars, and quarter are explicit instructions.
- **Original R5 retained and clarified as new R5.** The workbook and CSV structure remains directly required. Substantive data and red formatting remain checkable.
- **Original R6 retained and atomized as new R6.** The action vocabulary and decision framework are explicit. Fixed asset outcomes were not added.
- **Original R7 expanded as new R7.** Removed hard-coded portfolio totals and quarterly budget values. Added the required NIST mapping, all-project coverage check, PRJ-2024-041 remaining-budget analysis, matching-period budget comparison, and separation of project funds from general headroom.

## Evidence examined

- Read the refined instructions, source rubric and notes, ITSM CSV, infrastructure and budget workbooks, supplied NIST workbook, and the AWS calculator file metadata and pricing model text.
- Across 36 available judge reports, original-row pass counts were R1 9/36, R2 2/36, R3 14/36, R4 28/36, R5 26/36, R6 2/36, and R7 4/36.
- Refined Luna scored 0/62 in the selected high report, but direct inspection showed a four-sheet workbook with 51 rule-derived candidates, a stated fleet median, AWS pricing columns, Zero Trust flags, a populated gap register, and an executive summary. Its trajectory inspected the three local sources and researched NIST and AWS.
- Sol rubric-gold scored 62/62. Its workbook contained the required sheets, 51 candidates from 84 on-premise assets, three pricing modes, action rationales, NIST mappings, and quantified recommendations; its trajectory retrieved external sources and analyzed the local files.
- Qwen 3.5 reasoning scored 0/62. It used 84 unfiltered rows, non-instructed action labels, no full AWS TCO, no meaningful project-budget reconciliation, and unsupported multi-million-dollar gap estimates. Its trajectory did not obtain the required external workbooks.

## Likely judge artifacts versus genuine task failures

- The refined Luna report claimed the workbook had only a Reconciliation sheet and no Migration_Plan, Gap_Register, or Executive_Summary. Direct workbook inspection found all four sheets with substantive data. This is a judge extraction/truncation artifact.
- Fixed candidate IDs, a fixed final count, and fixed pricing examples can reject a correct equivalent implementation and were removed.
- Very low R2 and R6 pass rates partly reflect genuine difficulty: many outputs omitted reserved pricing, upfront fees, three-year TCO, or the exact Migrate/Defer/Decommission vocabulary.
- Missing NIST mappings, failure to test every pending project, unsupported remediation estimates, conflation of business-as-usual cloud spend with migration spend, and mismatched annual-versus-quarterly budget comparisons are genuine failures.
- Red conditional formatting, required sheet names, CSV fields, and explicit risk flags are genuine deliverable requirements, not formatting preferences.

## Weight accounting

- Original total: **62**
- Revised total: **62**
- Original row weights were retained. Criteria were broadened or added only to cover requirements already present in the refined instructions.
