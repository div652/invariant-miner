# Refinement notes — computer_and_information_systems_managers/task1

## Evidence reviewed

- Refined instructions, original rubric, source refinement notes, and task card.
- Inputs: all four sheets in the budget workbook, 2,000 ITSM records, all four SQLite tables, 621 AWS instance rows, and 216 NIST questionnaire rows.
- All 36 available judge reports. Scores ranged from 0/56 to 56/56.
- Representative outputs and trajectories:
  - Refined Luna: 28/56 and 40/56; 78 tool calls across three session files. It produced all deliverables but recommended AWS names that the judges could not validate against the supplied instance file.
  - Sol rubric-gold: 50/56 and 56/56; 50 tool calls in one session. One judge rejected blank average-handle-time and DR fields for zero-incident risks while the other awarded full credit.
  - Qwen reasoning-on: 26/56 in both reports; 80 tool calls. It produced all deliverables, but `reconciliation_flags.csv` used an entirely different header schema.

## Instruction-supported requirements

The instructions support exact deliverable structures, sequential server tiers, source-file AWS right-sizing, a documented risk-to-ITSM category mapping, DR status rules, two-level budget variance, server-cost reconciliation, NIST question mapping, proposal-based vendor sensitivity, compliance gap linkage, and systematic discrepancy flags. They do not prescribe a particular cloud vendor, a hidden risk-category crosswalk, fixed tier counts, fixed deviations, or specific control-to-risk pairs beyond what the source data and submitted mapping support.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — AWS replacements | Retained and rewritten | Removed the leaked Tier 1 count and example answers. Kept source-file membership and CPU/RAM constraints. Added a documented tie-break because “smallest” is otherwise ambiguous among different instance families. |
| R2 — risk/incident correlation | Retained and rewritten | Removed fixed risk IDs and hidden category assignments. Requires every source Critical/High risk, a disclosed mapping, incident statistics, DR status, and frameworks. Explicitly permits `0`/not-applicable averages for zero-incident rows, resolving a judge-only formatting dispute. |
| R3 — server matrix | Retained and rewritten | Removed fixed server and tier counts while retaining complete source coverage, sequential classification, required fields, costs, and `N/A` behavior. |
| R4 — reconciliation flags | Retained and rewritten | Removed the single hard-coded budget comparison and fixed expected gaps. Requires all instructed discrepancy domains, exact columns, source traceability, and scope-aware classification. |
| R5 — vendor recommendation | Retained and rewritten | Removed hard-coded proposal figures and any implied preferred vendor. Added the explicitly instructed 10% and 20% sensitivity tests. |
| R6 — compliance controls | Retained and broadened | Removed named controls and forced risk pairs. Retained counts and related-risk linkage, and added the otherwise underweighted NIST CSF row-level requirements and migration-impact rule. |
| R7 — budget deviations | Retained and rewritten | Removed the hidden conclusion that no category exceeds 15% and the named expected outliers. Grades both calculation levels, flags, server-cost reconciliation, and the dashboard's 5% bottom-up discrepancies. |
| R8 — deliverables | Retained | Kept the exact title, ordered sections, four sheet names, CSV filename, and mutual consistency. Criteria were split into atomic file-level checks. |

## Score and trajectory findings

The full-scoring Sol report shows that the task is achievable. Its 50/56 companion judgment failed only because zero-incident rows used blank averages or DR values; the instructions allow a truthful not-applicable representation, so the variant states that explicitly. The refined Luna output's invalid or unverified AWS types are a genuine failure because the instructions require types from `aws-instances.csv`. Its missing exact `$2,013,000` comparison was largely an original-rubric artifact: it did identify a server-budget mismatch, but against a different interpreted budget line. The revised criterion requires the relevant source line and an explanation of scope, not a hidden number.

Qwen's nonstandard flags header is a genuine failure under the exact CSV specification. Judge disagreement over specific category mappings or a mandated vendor is diagnostic only; the revised rubric grades reproducibility and source support instead.

## Likely judge artifacts versus genuine task failures

- **Artifacts:** fixed counts and IDs, mandatory CTL-007/RSK-006 and CTL-010/RSK-016 pairings, a hidden risk-to-CI crosswalk, rejection of not-applicable averages, and requiring all three vendors' exact figures inside the Executive Summary rather than in the report analysis.
- **Genuine:** fabricated AWS instance types, incomplete server coverage, undocumented category mappings, incorrect tier order, missing sensitivity cases, wrong CSV headers, or missing NIST/question rows.

## Weight accounting

- Original total: **56**
- New total: **56**
- The second-pass row weights are **8, 4, 2, 6, 6, 6, 8, 6, 10**.
- The prior 6-point risk/DR row was split into a 4-point risk-incident row and a 2-point plan-level DR audit row.

## Second-pass validation

- Added complete report coverage for every DR plan with `test_result = Fail` or RTO above 24 hours, rather than allowing one generic risk status to stand in for the plan population.
- Required disclosure of how other non-Pass test results are treated and explicit handling when a deficient plan has no defensible Critical/High-risk relationship.
- Preserved the 56-point total.
- Deferred the judge's missing-source-context finding to evaluator infrastructure; no server, risk, budget, proposal, AWS, or NIST answer tables were embedded in the rubric.
