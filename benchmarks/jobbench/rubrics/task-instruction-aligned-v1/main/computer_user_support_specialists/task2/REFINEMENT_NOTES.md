# Refinement notes — computer_user_support_specialists/task2

## Instruction-supported requirements

The refined instructions require a migration plan covering every device and every manager constraint, an incident analysis covering the full pilot dataset and every not-yet-migrated device, and a 12-15-slide CTO deck. Hardware eligibility must be reconciled against authoritative Windows 11 requirements, not copied from the inventory's recorded compatibility field. The manager's email controls budget, deadlines, procurement lead times, staffing, flagged-device investigation, the Sales freeze, Executive verification, and VPN scheduling.

The variant accepts any source-supported device classification, burden model, staffing projection, or deferral plan that is internally consistent and documents uncertainty. It does not require the inventory's stated compatibility conclusion, a hidden exact device count, a fixed minimum cost, or a specific classification for a device whose firmware or vendor support requires investigation.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 — MFS-PC-049 | Rewritten into new R1 | Retained investigation and ticket cross-reference. Removed the false mandatory assertion that Intel Core i5-9500 is unsupported; it is a 9th-generation processor family that appears on Microsoft's supported Windows 11 processor lists. Ticket 1054 establishes a post-upgrade VPN problem, not CPU ineligibility. |
| R2 — Finance and Legal | Merged into new R1-R3 | Retained complete department counts, cost, procurement, and March 31 completion. Removed hard-coded classifications and totals that depend on the disputed CPU and TPM conclusions. |
| R3 — Sales | Rewritten into new R2 | Retained the freeze middle ground, Q2 deployment planning, and VPN concern. Replaced one prescribed wave pattern with an outcome-based requirement that resolves the conflict. |
| R4 — tickets and workload | Rewritten into new R4 | Retained ranked subcategories and per-staff workload. Removed hard-coded answers from the wording and added the instructed requirement to analyze hardware patterns. |
| R5 — staffing impact | Rewritten into new R5 | Retained departed-staff handling, active staff, rollout projection, bottlenecks, and redistribution. Required a visible scaling method instead of one hidden expected weekly result. |
| R6 — executive risk | Merged into new R8 | Retained compliance, insurance, and security-patch exposure and added the remaining required deck content. |
| R7 — decision tree | Rewritten into new R7 | Retained actual top-five coverage, first-level steps, diagnostics, and named specialist escalation. Removed the hard-coded subcategory list from the criterion text because it must be derived from the database. |
| R8 — budget | Rewritten into new R3 | Retained the cap, reserve, itemization, and deferrals. Removed the fixed $27,785 “minimum,” which depends on disputed classifications and excludes unresolved workstation pricing and other plan choices. |
| R9 — burden scores | Rewritten into new R6 | Retained complete device scoring and required factors. Added reproducibility and limitations so an evidence-based alternative model is accepted. |
| R10 — MFS-PC-054 | Merged into new R1 and R3 | Retained the need to investigate a TPM-only incompatibility and its budget or schedule effect. Removed the hidden conclusion that a firmware upgrade definitely exists and saves exactly $1,400; vendor support must be verified rather than inferred from other models. |

The original rubric did not adequately score the complete per-device table, all seven manager constraints, the full sprint schedule, cost reconciliation, hardware-correlation analysis, or most of the required deck. The revised rows add those instructed deliverables without increasing total weight.

## Evidence examined

Judge reports and generated deliverables were examined from the refined Luna, Sol rubric-gold, Qwen 3.5 reasoning, and GPT-5.4 runs. Their report totals were respectively 48/82 and 64/82; four reports at 82/82; two reports at 6/82; and 12/82 and 20/82. Slide text, DOCX content, output inventories, and trajectories were reviewed for all four.

The refined Luna output contained a comprehensive 75-device table, sprint plan, support model, decision tree, and CTO deck, but it repeated the original rubric's unsupported i5-9500 conclusion and made inconsistent budget totals in two adjacent tables. Sol's full-score output closely followed the hidden device conclusions. Qwen produced incomplete or unusable deliverables. GPT-5.4 covered portions of the analysis but omitted substantial required detail and received materially different row results depending on the judge.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts were penalties for correctly questioning inventory labels; mandatory classification of i5-9500 as unsupported; mandatory firmware availability and exact savings for MFS-PC-054; exact replacement counts and a fixed minimum budget derived from those assumptions; and report-to-report score variation for the same files.

Genuine failures included missing devices, incomplete department summaries, failure to reconcile budget tables, omission of numbered manager constraints, unsupported cost assumptions, no reproducible burden method, missing per-staff workload fields, incomplete top-five triage branches, missing procurement timing, and decks outside the required scope or slide count.

## Weight reconciliation

Original total weight: **82**.

Revised total weight: **82**.

Weight was moved from two device-specific hidden-answer rows to complete classification, constraint resolution, budget reconciliation, the required incident analyses, and the full executive-deck specification.

## Second-pass validation

- Added a four-point deliverable row requiring two DOCX files and one PPTX file and checking cross-deliverable consistency.
- Reworded the support-burden method so the listed hardware factors remain examples; a reproducible evidence-based subset is accepted.
- Removed the rubric-only requirement for extra hardware-eligibility and remote-network decision-tree branches beyond the derived top five subcategories.
- Reallocated integer weights across classification, timeline, budget, and deck rows while preserving the **82-point** total.
- Deferred evaluator-infrastructure work: judges need normalized inventory, ticket, budget, manager-email, hardware-requirement, and external-guide context, and PPTX slide rendering is needed to judge visual charts and timelines.
