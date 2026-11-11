# Refinement notes — customer_service_representatives/task1

## Instruction-supported requirements

The task requires an exact three-file package: a four-sheet investigation workbook, six individualized letters, and a supervisor briefing PDF. The workbook must reconcile each customer statement, account profile, billing trajectory, and supervisor note; calculate January and Oct–Dec weather-normalized usage; compare January bills and energy rates with 2024 Pennsylvania EIA benchmarks; identify applicable consumer-rights or tariff provisions; calculate business days to each deadline; and assign one of four resolutions with short evidence-based justifications.

Each letter must identify the account and dispute, quantify three specified January weather facts from the local CSV, explain the resolution and next steps, address plan-specific concerns and rights, and include the full PA PUC informal/formal complaint path plus the contact information in the supplied guide. The briefing must rank all six disputes across deadline, vulnerability, and financial-exposure dimensions; document every divergence from the supervisor notes; identify supported systemic issues; and make two or three pattern-grounded policy recommendations. The instructions do not prescribe one overall ranking, one diagnosis for Budget Billing, one senior-plan conclusion, or one hidden resolution per customer.

## Original rubric disposition

- **R1 — merged into new R2 and new R8.** Supervisor-assertion verification remains, but the variant assesses every assertion for all six disputes instead of one December bill discrepancy.
- **R2 and R3 — merged into new R2, R4, R5, and R6.** Budget Billing and Senior Discount issues remain as customer-specific evidence and source-authority questions. The variant does not force an annual true-up, program termination, or tariff conclusion that the supplied records cannot prove.
- **R4 — retained and generalized as new R6.** All three instructed weather facts remain required in every letter, but the criteria assess calculations from the CSV rather than embed answer values.
- **R5 — retained as new R7.** The complete escalation path and contact information remain explicit.
- **R6 — merged into new R6 and R7.** The Budget Billing letter must answer the customer's concern and state supported rights, but it need not present one speculative cause as established fact.
- **R7 — rewritten as part of new R8.** All required ranking dimensions remain. The fixed overall winner and fixed deadline ordering as the only acceptable ranking were removed.
- **R8 — rewritten as part of new R8.** Supported cross-dispute patterns remain. Predetermined “program failure” and “potential systemic error” conclusions were removed.
- **R9 — expanded as part of new R8.** Every factual divergence is assessed, not only two hidden expected disagreements.
- **R10 — retained and generalized as new R3.** Correct EIA comparisons and usage-versus-price analysis remain without hard-coding the benchmark results into the rubric.
- **New R1 and R5 — added.** Exact deliverable structure and the required six-case Resolution Matrix did not have direct original coverage.

## Material changes and reasons

1. Exact customer amounts, statewide averages, usage averages, weather counts, and deadline rankings were removed from criterion text. They remain checkable from the named inputs, but equivalent correct calculations and documented rounding are accepted.
2. Cross-Source Validation now evaluates every factual assertion in all six supervisor notes, including unsupported hypotheses, rather than rewarding two expected traps.
3. A high variable Budget Billing charge is treated as a question requiring program-history or tariff evidence. The rubric does not assume a true-up, termination, or program failure.
4. Senior Discount and Low Income Assist rights must be attributed to the governing source. Absence from the PA PUC guide does not by itself prove the contents of LEEC's tariff.
5. The action matrix must use all three instructed dimensions, but the instructions do not require a single weighting formula or predetermined top-ranked dispute.
6. “Systemic issue” scoring now requires a pattern supported by multiple cases. Correct rate application is not graded as a failure merely because the original rubric expected an investigation flag.
7. Letter scoring covers all required content for all six recipients rather than relying on one customer's expected explanation.
8. Resolution completeness, exact filenames, exact workbook sheet names, source citations, and cross-deliverable consistency receive direct weight.

## Score and trajectory evidence examined

The available report set contains **35 judge reports across 17 runs**. Scores and row-level reasons were compared across the full set, with representative output and trajectory inspection for:

- **Refined Luna landlock:** 60/76 and 70/76. It produced the exact three files and four sheets, included all three weather facts in each letter, included the full complaint path and contact details, and documented supervisor-note divergences. Judges focused on the absence of one specific 12-month usage comparison and, in one report, exact wording about the source of Senior Discount protections. Its trajectory did not receive the rubric.
- **Sol rubric-gold:** 76/76 in both reports. It produced complete deliverables and explicitly incorporated the narrow expected facts. Its trajectory contained evaluator guidance. The workbook and report were more expansive than required, and the full score therefore is not independent evidence that every hard-coded conclusion is instruction-supported.
- **Qwen 3.8 reasoning:** 44/76 in both reports. It produced all three files and four sheets, but its letters omitted the below-zero-day count and did not clearly describe the hearing stage; the priority matrix and systemic section also diverged from the judge's fixed expected conclusions. Its trajectory did not receive the rubric.
- **GPT-5.4:** 6/76 and 16/76. It performed much of the source analysis but omitted or obscured several required letter disclosures and briefing divergences. Those omissions are genuine even where the judge also demanded fixed rankings or wording.

Workbook sheets, customer-letter text, briefing text, file structure, weather calculations, EIA reference workbooks, supervisor notes, billing history, account profiles, PUC-guide passages, judge reasons, and representative session trajectories were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include requiring one specific 12-month average to appear in a particular section when the underlying billing trajectory is otherwise reconciled; forcing a true-up or termination diagnosis without account-program history; requiring a fixed overall priority winner; treating a high Budget Billing charge as proof that the program failed; requiring a “systemic” Senior Discount problem even when both rates were correctly applied; or demanding one exact phrase to establish that a utility-specific plan is tariff-governed.

Genuine failures include missing any customer, omitting supervisor assertions or actual figures, incorrect HDD or benchmark arithmetic, conflating the energy rate with the effective total rate, citing a plan right to the wrong authority, failing to identify unresolved evidence, omitting a required weather fact from any letter, omitting the formal complaint/hearing step or PUC contacts, failing to use all three briefing dimensions, omitting divergences, providing no supported systemic analysis, or making recommendations unrelated to the six disputes.

## Weight accounting

- Original total: **76**
- Variant total: **76**
- Weight moved from hard-coded customer conclusions and fixed ranking outcomes to six-case completeness, source authority, resolution quality, exact deliverable structure, and cross-deliverable consistency.

## Second-pass validation

- The briefing rubric now requires every factual divergence from the supervisor notes while allowing the briefing to prioritize the most consequential items.
- Source-file and EIA-reference attachment remains an evaluator-infrastructure requirement; no hidden expected customer values were added to the rubric.
