# Refinement notes — secretaries_and_administrative_assistants_except_legal_medical_and_executive/task1

## Instruction-supported requirements

The refined instructions require three exact-filename deliverables built from the supplied templates: a reconciled donor database, a December attendance workbook, and tiered acknowledgment letters. Every donation and registration must be represented exactly once. Donor records must be deduplicated, typed, totaled, annotated with special circumstances, and matched to volunteers through stated contact keys. Attendance notes must show Q4 support and qualifying professional backgrounds. Letters are limited to $500-and-above gifts, with Major letters first and Mid-level letters second.

Special-circumstance customization is conditional on letter eligibility. The explicit “donations under $500 get no letter” rule controls when a memorial or volunteer-donor gift is below threshold. The variant therefore does not require an otherwise prohibited letter merely to demonstrate customization.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 — named volunteer-donor | Merged into new R2 and R5 | Retained contact-based matching, the Staff/Volunteer Donor literal, registration ID, and attendance donation flag. Rephrased the check to cover every qualifying match instead of one hidden individual. |
| R2 — organizations | Rewritten into new R2 | Retained correct Organization type and preservation of special-circumstance notes. Expanded the criterion to all source donors and removed the fixed list from the wording. |
| R3 — reconciliation summary | Rewritten into new R3 | Retained the three required metrics and prior-template record status. Added the required conflict list and reconciliation of summary counts to the final data. |
| R4 — attendance roster | Rewritten into new R4 | Retained the exact filename, complete roster, session details, and exact-once registration coverage. The second pass expresses the required output structure directly rather than trying to prove template provenance from extracted artifacts. |
| R5 — named donor flag | Merged into new R5 | Retained Q4 Donor plus amount and made it complete for every volunteer-donor. |
| R6 — professional flags | Merged into new R5 | Retained Priority Training Track for IT, legal, healthcare, and accounting backgrounds. Replaced the hidden exact count and named list with complete source-derived inclusion and exclusion. |
| R7 — complete gifts | Rewritten into new R1 | Retained every required gift field and exact-once coverage. Added donor deduplication, totals, and reconciliation to the source rows. |

New R6 covers the acknowledgment-letter deliverable, which the original rubric did not score at all despite its explicit filename, template, threshold, ordering, and customization requirements.

## Evidence examined

Judge reports, XLSX files, PDFs, and trajectories were examined from:

- refined Luna landlock: 54/60 and 60/60;
- Sol rubric-gold: four reports at 60/60;
- Qwen 3.5 reasoning: two reports at 22/60;
- GPT-5.4: two reports at 40/60.

The refined Luna and Sol outputs were the strongest database and attendance submissions, but both created letters for under-$500 special-circumstance donors. Because the original rubric omitted the PDF entirely, those outputs could receive full credit despite violating the explicit letter threshold. Qwen omitted or mishandled substantial reconciliation and attendance content. GPT-5.4 completed more of the tabular work but still missed required fields or flags.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts included exact-name and exact-count checks where complete source-derived coverage should control, report variation between 54 and 60 for the same refined Luna output, and full scores that ignored an invalid letter population because no row assessed the PDF.

Genuine failures included omitted or duplicate gift rows, incomplete addresses or gift fields, unsupported donor merges or unlisted identity conflicts, missing special-circumstance notes, inaccurate reconciliation counts, omitted registrants, incorrect donor or professional flags, missing letter tiers, and letters for gifts below $500.

The apparent instruction tension around memorial and dual-status customization is resolved by applying customization only after the contribution qualifies for a letter. This preserves both explicit rules without inventing an exception.

## Weight reconciliation

Original total weight: **60**.

Revised total weight: **60**.

Weight was reallocated from individual hidden-answer checks and exact source counts to complete database reconciliation, full attendance logic, and the previously unscored 12-point acknowledgment-letter deliverable.

## Second-pass validation

- Reworded donor-field coverage so a normalized Donors/Gifts design may store contact details once while preserving an unambiguous link from every gift.
- Removed the unrequested requirement to narrate a donor-deduplication algorithm; the rubric still checks the resulting deduplication, conflicts, totals, and the instructed volunteer-donor matching keys.
- Replaced unjudgeable claims that outputs were built on the supplied templates with observable filename, sheet-role, header, roster, tier, and letter-content requirements.
- Deferred missing source/template context to evaluator infrastructure rather than embedding hidden donor names, counts, or template text.
