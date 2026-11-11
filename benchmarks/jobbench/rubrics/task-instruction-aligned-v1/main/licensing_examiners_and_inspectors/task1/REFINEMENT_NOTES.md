# Licensing Examiners and Inspectors Task 1 — Task-Instruction-Aligned Rubric Notes

## Instruction-supported requirements

The refined task requires an XLSX workbook with exactly three named sheets and a 3–4-page PDF report with an exact title and section order. The examiner must review all 15 applications under four current bulletins; apply specialty bond minimums, application-date insurance, exam and experience requirements; incorporate correspondence, inspections, bond records, violations, complaints, and public lookup results; document every deficiency and corrective action; map each bulletin to each application it actually affects; and use experienced judgment to select APPROVE, DENY, or HOLD.

The instructions support checking that unresolved objective deficiencies prevent approval. They do not prescribe DENY rather than HOLD for every curable deficiency. The variant therefore accepts either non-approval disposition when the governing rule, evidence, corrective path, and chosen judgment are consistently documented. The exception is a bulletin-mandated hold, which must be applied as written.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1, forced denial of Application 2025004 (10) | Rewritten and merged into new rows 1–3 | Retains the failed exam, score, specialty rule, and non-transferable out-of-state credential as material evidence. Removes an inflexible hidden DENY outcome; the application cannot be approved, but DENY or a supported HOLD may reflect the examiner's corrective-process judgment. |
| R2, forced denial of Application 2025009 (6) | Rewritten and merged into new rows 1, 2, and 5 | Retains all violation, payment, AG referral, complaint, inspection, correspondence, and background evidence. Evaluates whether the unified record supports the chosen disposition instead of scoring only one predetermined label. |
| R3, Application 2025013 experience and verification (6) | Retained and merged into new rows 2–4 | Preserves both the years-of-experience shortfall and missing third-party verification, while also requiring the separate mandatory-hold evidence and regulatory-impact row. |
| R4, duplicate principal (6) | Retained and merged into new rows 1–3 | Preserves identification and management review of the duplicate principal but allows the examiner to choose which related application is held when the decision is explained. |
| R5, expired insurance (8) | Retained and generalized in new rows 2 and 3 | Preserves application-date insurance testing and non-approval for a lapse without hard-coding one applicant as the only case that matters. |
| R6, pending background check (6) | Retained and generalized in new rows 1–3 | Preserves the rule that a pending required check prevents approval and requires the deficiency and corrective action to be documented. |
| R7, four correspondence items (10) | Retained in new row 6 | Keeps sender, cross-reference, action, and follow-up for every item. Removes forced wording and scores traceable handling of the actual evidence. |
| R8, process recommendations (6) | Retained in new row 7 | Preserves at least two actionable, case-grounded improvements without limiting acceptable recommendations to the examples in the original rubric. |
| R9, HVAC bond deficiency (6) | Retained and generalized in new rows 2 and 3 | Preserves the bulletin threshold, amount, shortfall, and sole-deficiency reasoning where supported. Does not force one disposition label for a curable bond filing. |
| R10, executive counts and fixed outcome list (8) | Rewritten and merged into new rows 1 and 5 | Preserves counts summing to 15, application lists, and hold rationales. Removes the hard-coded approval/denial roster and instead requires determinations to follow all current evidence consistently. |

The variant adds explicit weight for complete Eligibility Summary evidence, every Deficiency Detail row, the required affected-pair structure, public-dataset handling, exact PDF form, and unified high-risk narratives. These are central instructions that the original rubric covered only indirectly.

## Evidence examined

Reviewed the refined instructions, original rubric, source refinement notes, applications, all four bulletins, correspondence queue, inspection JSON, bond subset, violations/complaints database, and available public-dataset lookup evidence. Representative outputs and root trajectories were examined from `gpt56-luna-high-exa-main-refined-256k-32k-landlock-20260930T055414Z`, `gpt56-sol-high-256k-32k-rubric-gold-all64-judge-20261003T053813Z`, and `gpt54-high-exa-main-20260914T032904Z`.

Across 35 judge reports, original-row pass counts were R1 14/35, R2 5/35, R3 33/35, R4 30/35, R5 11/35, R6 17/35, R7 16/35, R8 33/35, R9 6/35, and R10 8/35. Refined Luna received materially inconsistent scores of 66/72 and 52/72 from two judges. Sol rubric-gold received 72/72.

## Judge artifacts versus genuine task failures

The Sol full score is a likely judge false positive. Its Regulatory Impact Analysis used one row per bulletin rather than one row per affected bulletin-application pair, it approved Application 2025002 despite a $6,000 bond where the task evidence required $12,000, and its correspondence entries did not explicitly identify all item numbers. Refined Luna's 60-row bulletin-by-application Cartesian product also did not satisfy the instruction to list affected pairs, even though it looked more complete. The wide Luna judge disagreement further shows that fixed expected dispositions were being applied inconsistently.

Genuine failures include omitting any of the 15 applications, reporting only the first deficiency, ignoring specialty bond changes, testing insurance on the wrong date, failing to update stale bond status from correspondence, missing the RB-2025-003 mandatory hold, overlooking exam or experience evidence, omitting violation or complaint amounts and payment status, treating no public-record match as conclusive, or failing to document each correspondence disposition.

## Weight preservation

Original total: **72**. Variant total: **72**.

Weight moved from ten case-specific expected outcomes to complete evidence synthesis, all required workbook rows, current-rule application, and the required report structure. No required source or application is made optional.
