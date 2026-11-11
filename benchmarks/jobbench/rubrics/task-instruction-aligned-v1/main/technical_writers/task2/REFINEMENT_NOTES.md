# Refinement notes — technical_writers/task2

## Instruction-supported requirements

The refined instructions require three exact-filename deliverables. The v3.1.0 migration guide must cover every breaking change introduced in that release, provide an impact-ordered summary and section for each, include curl and Python before/after pairs, cite a concrete support-ticket pitfall, and provide an evidence-based SDK matrix. The revised reference must replace the entire draft, cover every endpoint, resolve every review item, incorporate every undocumented changelog entry, surface ticket-caused failures and enhanced troubleshooting, and apply company terminology plus the named Google and Microsoft style guidance. The CSV must have the exact ten columns and one row for every review-feedback item and undocumented changelog entry.

The variant distinguishes release membership from cumulative documentation debt. The 405-to-422 `PUT /pet` change is dated v3.0.1 in the changelog, so it must be corrected in the revised reference and impact CSV but is not mandatory as a v3.1.0-introduced migration-guide section. A guide may include it as clearly labeled cumulative context.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 — exact three-change ordering | Rewritten into new R1 and R7 | Retained metric-based impact ordering. Removed the mandatory inclusion and last-place ordering of the v3.0.1 `PUT /pet` change as though introduced in v3.1.0. Removed one hidden exact order because the instructions specify three metrics but no weighting formula; a transparent, consistent multi-metric order is accepted. |
| R2 — examples for three changes | Rewritten into new R2 | Retained curl and Python before/after pairs for every in-scope breaking change. Limited mandatory release sections to changelog rows introduced in v3.1.0. |
| R3 — three named pitfalls | Rewritten into new R2 | Retained ticket IDs and concrete error details for every in-scope breaking change. The older `PUT /pet` ticket remains required in the revised reference and CSV, not necessarily the v3.1.0 migration guide. |
| R4 — CSV columns and selected mappings | Rewritten into new R6 | Retained the exact columns, metrics, and ticket mappings. Expanded coverage from selected examples to every review-feedback and undocumented-changelog gap and added safe handling for absent or cross-endpoint metrics. |
| R5 — fixed P0-P3 assignments | Rewritten into new R7 | Retained quantitative P0-P3 prioritization. Removed exact hidden priority labels; the instructions define factors but no thresholds or formula, so consistent evidence-based schemes may differ on close cases. |
| R6 — SDK matrix for three changes | Rewritten into new R3 | Retained affected versions, minimum support, workarounds, and basis. Added an explicit prohibition on fabricating package versions because the supplied files identify API contract versions but not language-package releases. |
| R7 — GET /user/login headers | Merged into new R4 and R5 | Retained complete login-header correction but expanded scoring to the instructed full reference, every endpoint, every header, all feedback, and all undocumented changes. Removed one narrow endpoint as a proxy for the whole deliverable. |
| R8 — standalone guide | Merged into new R1 and R2 | Retained release context, urgency, base URL, authentication, summary, and self-sufficient examples. Release membership is now determined from the changelog rather than an unsupported fixed count. |

The revised rubric adds direct coverage of most of `revised_api_reference.md`, complete gap-row coverage, company terminology, external style guidance, enhanced troubleshooting, and source-conflict resolution. These were major instructed requirements absent from the original rows.

## Evidence examined

All task inputs were reviewed, including the 15 review-feedback records, changelog documentation statuses and release versions, endpoint usage metrics, breaking-change impact data, terminology table, draft reference, OpenAPI source, support-ticket excerpt, and the two required external style references.

Judge reports, all three deliverables, and trajectories were examined from four materially different runs:

- refined Luna landlock: two reports at 50/60;
- Sol rubric-gold: reports at 50/60 and 60/60;
- Qwen 3.5 reasoning: two reports at 6/60;
- GPT-5.4: 16/60 and 22/60.

Refined Luna and Sol produced comprehensive references and impact tables. Their scores turned chiefly on the original exact-priority row even when their quantitative justifications were explicit. Sol received both 50 and 60 for materially the same priority work. Qwen omitted most requested deliverables or provided fragments. GPT-5.4 covered portions of the guide and CSV but left major reference and SDK requirements incomplete.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts included requiring exact P0-P3 outcomes despite no priority formula, requiring an older v3.0.1 change as one of “three” v3.1.0 changes, accepting or rejecting the same Sol priority analysis across reports, and awarding substantial revised-reference credit from one endpoint's headers without checking the full reference.

Genuine failures included omitting a v3.1.0 breaking change, using a stale or incorrect authorization URL, missing a language's before/after pair, inventing SDK package versions, failing to cite the ticket's concrete error, omitting review IDs or undocumented changelog entries, incomplete endpoint parameters or headers, double-counting cross-endpoint consumers as unique, and marking general documentation gaps as terminology violations merely because their descriptions contain API vocabulary.

## Weight reconciliation

Original total weight: **60**.

Revised total weight: **60**.

Weight was moved from hard-coded ordering, exact priority labels, and one narrow header check to complete release scoping, the full revised API reference, comprehensive gap analysis, source-conflict handling, and evidence-based uncertainty.

## Second-pass validation

- Added exact filename and format checks for all three deliverables.
- Enforced the instructed migration-guide order: introduction, top summary table, then detailed breaking-change sections.
- Limited mandatory request-body examples to contract examples or review/ticket-driven needs instead of requiring an unstated example for every body-bearing endpoint.
- Replaced the undefined “elevated error rate” test with a submission-stated, consistently applied data-based troubleshooting method.
- Preserved flexible SDK contract generations and data-driven priorities when package versions or metric values are unavailable.
- Deferred missing changelog, OpenAPI, usage, review, ticket, terminology, and style-reference context in the judge prompt to evaluator infrastructure; no hidden expected order, priority, or ticket mapping was added.
