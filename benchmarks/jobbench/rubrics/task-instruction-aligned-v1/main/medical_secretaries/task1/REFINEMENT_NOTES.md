# Refinement notes — medical_secretaries/task1

## Instruction-supported requirements

The instructions require a complete three-tab referral audit, separate chapter-validity and narrative/laterality checks, comprehensive discrepancy reporting with row-specific contacts, dashboard counts, overlapping conditional-format signals, two merge-field templates, and a three-tier action plan driven by urgency, clinical issues, missing documents, authorization, and free-text notes. They also require use of the supplied ICD-10 and HIPAA references and the Heartland letterhead content.

Source-derived code mismatches, duplicates, shared identifiers, missing items, and note-driven priorities may be assessed. The rubric must not require exact prose, fax-number punctuation, or a pixel-identical copy of the CRMC form.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 out-of-range S-code (6) | Merged into Referral Log/source-fidelity rows | Retains separate M00–M99 range and clinical-fit reporting. Generalizes the rule to every out-of-range code without requiring the actual chapter name. |
| R2 and R3 laterality mismatches (10, 6) | Merged into Referral Log and Discrepancy Report | Retains official-description checking, determinable correction, clinical risk, and affected-row contact details without making two examples the only graded code work. |
| R4 shared insurance ID (10) | Rewritten within comprehensive discrepancy coverage | Retains the cross-patient identifier anomaly and distinguishes it from the same-patient duplicate. |
| R5 urgent pathological-fracture plan (8) | Merged into Action Plan | Retains Tier 1 placement, laterality clarification, oncology coordination, and timing when supported by Referral_Reason or Notes. |
| R6 fax template (6) | Retained and expanded to 8 | Preserves both sections, merge fields, HIPAA reference, confidentiality notice, deadline, and practice identity. |
| R7 acknowledgment (6) | Retained | No material requirement removed. |
| R8 conditional formatting (10) | Retained as an 8-point general rule | Grades every qualifying row and overlapping signal rather than enumerating a leaked list of IDs. |
| R9 reschedule tier (10) | Merged into Action Plan | Retains the rule that routine rescheduling is administrative while allowing a separate Tier 2 authorization item or a justified combined priority when one referral has multiple follow-up needs. |
| R10 contact-rich corrective actions (6) | Merged into Discrepancy Report | Retains contact, practice, fax, method, and duplicate-ID requirements for every issue. |
| Dashboard and complete log | Added direct coverage | The original rubric concentrated on traps and did not directly score all requested dashboard categories or complete Referral Log structure. |

Variant weights are 14 for Referral Log, 14 for Discrepancy Report, 8 for dashboard, 8 for conditional formatting, 8 for the request template, 6 for acknowledgment, 14 for the action plan, and 6 for reference fidelity.

## Evidence examined

- Refined Luna: `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, 18/78 and 44/78 reports, all four outputs, and trajectory. The workbook itself contained three conditional-format rules even though the lower judge reported no formatting. Genuine misses included the shared insurance-ID anomaly and Tier 3 reschedule handling.
- Sol rubric-gold: `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, four 78/78 reports, complete outputs, and trajectory using both external references.
- Qwen 3.8 reasoning: `qwen38-main-256k-32k-reasoning-on-20260921T054357Z`, 36/78 and 42/78 reports, outputs, and trajectory. It handled many discrepancies but omitted the chapter-range issue and cross-patient insurance-ID anomaly and placed the routine reschedule in Tier 2.
- Inputs inspected included all 18 referrals, the trailing-column free-text notes, code list, HIPAA form, referral-form PDF, duplicate patient pair, and the insurance ID shared across two distinct patients.

## Likely judge artifacts versus genuine task failures

The low refined-Luna report's claim that no conditional formatting existed conflicts with direct workbook inspection and the high report; that is a judge extraction artifact. Requiring exact wording such as “Chapter 19” or any actual chapter label is unnecessary when the submission correctly marks the code outside M00–M99 and separately evaluates clinical fit. Failing to separate range membership from clinical fit, missing a laterality mismatch, omitting a shared cross-patient identifier, using an unsupported priority tier, or failing to supply row-specific contacts are genuine failures.

## Weight check

Original total: **78**. Variant total: **78**.

## Second-pass validation

- Removed the single-item, highest-tier rule that conflicted with referrals containing both authorization and administrative work. Distinct follow-up needs may now be separate action-plan items; a combined item must use a justified applicable tier.
- Removed the hidden requirement to adjust authorization timing to a rescheduled appointment. Routine rescheduling remains Tier 3 when represented as a distinct administrative task.
- Made actual ICD-10 chapter naming optional. The scored requirements are correct M00–M99 range classification and a separate narrative/laterality assessment.
- Missing referral and reference context in the judge request, and invisible Excel conditional formatting, are deferred to evaluator infrastructure. No hidden referral IDs, codes, or formatting outcomes were added to compensate.
- Total weight remains **78**.
