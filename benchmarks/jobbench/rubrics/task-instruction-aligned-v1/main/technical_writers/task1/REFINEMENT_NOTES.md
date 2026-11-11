# Refinement notes — technical_writers/task1

## Instruction-supported requirements

- Deliver the four exact-named Markdown files.
- In the migration guide, explain the API-key/JWT transition, parallel use, removal timing, multi-service strategy, all three ticket resolutions, incremental sync, and before/after patterns.
- In the API reference, document every public CSV endpoint by resource with environments, content type, fields, constraints, responses, rate category, added version, and deprecation.
- Document the complete async sync/job workflow and only the valid webhook events, including HMAC verification and soft-delete behavior.
- In troubleshooting, include each ticket, published category/tier rate limits, migration pitfalls with Symptoms and Resolution, and distinct 401/403 diagnostics.
- Use the template's release-note sections and synthesize the supplied changelog.
- Exclude internal/JIRA/TODO material and the unsupported JS/Java/internal references.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — JWT transition plus named customer | Retained in new R1, rewritten | Ticket ID, transition behavior, removal version, and enterprise strategy remain. The customer name is not required by the instructions. |
| R2 — webhook events and soft delete | Retained as new R4 | Signature verification and implementable guidance were added because the instructions explicitly require them. |
| R3 — rate categories and limits | Merged into new R5 | Published limits and endpoint mapping remain. Undocumented sync/competitor-tier values must be labeled unknown rather than invented. |
| R4 — 401/403 and internal-reference exclusion | Split between new R5 and R7 | Authentication diagnostics and public-document hygiene are distinct requested outcomes. |
| R5 — sync workflow | Retained as new R3 | All modes, introduction versions, 202/job ID, polling endpoint, statuses, and progress remain. |
| R6 — release-note structure | Retained as new R6, rewritten | Required headings and changelog facts remain. A semantically appropriate performance subsection does not fail solely because one item is placed there while all required sections exist. |
| R7, R9, R10 — environments, versions, constraints | Merged into new R2 | These are part of comprehensive endpoint reference quality, which now also covers all endpoints, fields, responses, categories, and deprecations. |
| R8 — three exact pitfall sentences | Retained in new R5, rewritten | The support-pattern topics, Symptoms, and Resolution remain. The rubric no longer requires one exact direction of the API-key misconception when an equivalent transition pitfall is correctly documented. |
| No original row | Added across new R2, R4, and R7 | The original rubric under-assessed endpoint completeness, webhook signature verification, cross-document consistency, and exclusion of unsupported SDK/internal material. |

## Score, output, and trajectory evidence examined

- Refined Luna: 60/66 high and 66/66 low. The high judge failed only original R8 because the authentication pitfall used the opposite but still relevant transition misconception. Direct inspection found all four files, required ticket sections, comprehensive reference headings, and required release-note sections. The trajectory directly read/search/wrote the local sources.
- Sol rubric-gold: 66/66. Its four documents were more exhaustive and consistently mapped versions, limits, webhook behavior, and public-only content; the trajectory also consulted the formatting reference.
- Qwen 3.5 reasoning: 18/66. It produced all files but exposed JIRA-4521, misstated or invented some rate-limit details, omitted ticket IDs in required places, and used the wrong 401/403 meaning. Its trajectory used limited web/source verification.
- GPT-5.4: 42/66 high and 36/66 low. Genuine gaps included incomplete job-status values, missing sandbox-reset caveat, and missing ticket-specific sections; judges also penalized exact pitfall direction and evidence-location choices.
- Terra reports were reviewed as additional diverse evidence. The endpoint CSV, developer notes, release template, support JSON, and formatting reference file were independently inspected.

## Likely judge artifacts versus genuine task failures

- **Pitfall-direction artifact:** refined Luna documented a legitimate API-key transition pitfall but the high judge demanded the exact assumption “keys stop working immediately.” The instruction asks for support-pattern pitfalls, not that exact sentence.
- **Content-placement artifact:** Qwen was failed for placing the 3x bulk improvement under “Performance Improvements” despite also retaining the required “Improvements” section. The revised rubric checks structure and factual synthesis without prescribing the exact bullet location.
- **Unsupported source expectation:** one GPT-5.4 judge demanded explicit evidence that release notes were synthesized from the filename, although public release notes should not cite internal source filenames.
- **Genuine failures:** exposing internal identifiers, reversing 401/403, inventing unpublished limits, omitting required endpoint constraints/statuses, or documenting invalid webhook events remain failures.

## Weight accounting

- Original total: **66**
- Revised total: **66**
- Reallocation: narrow answer-key rows were consolidated into complete deliverable-level checks. Endpoint-reference coverage increased to 16 points, while migration, troubleshooting, webhooks, release notes, async sync, and public-document hygiene retain material weight.

## Second-pass validation

- Declared the structured endpoint CSV authoritative for public parameter and request-body schemas when broader developer notes conflict with it.
- Preserved the rule against publishing undocumented behavior while avoiding a hidden evaluator preference between contradictory sources.
- Deferred missing source facts in judge context to evaluator infrastructure rather than embedding endpoint answers, limits, or ticket outcomes in the rubric.
