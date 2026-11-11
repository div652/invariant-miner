# Refinement notes — online_merchants/task2

## Instruction-supported requirements

The refined instructions require four exact deliverables that operate as one evidence chain: responses and internal triage notes for every open complaint; a three-sheet dashboard; a two-to-three-page sentiment and catalog audit; and a row-preserving optimized catalog CSV. The complaint responses must cite applicable policy titles and terms. Triage notes must check the actual catalog, use product margin evidence only when a defensible match exists, and recommend correction, removal, or escalation. The dashboard definitions, sheet names, column names, class-ranking rule, audit section order, and CSV field requirements are explicit.

The local complaint workbook contains six open tickets. The source catalog contains 43 rows, including variant rows, with widespread empty SEO and Google Shopping fields. The sales file is a Superstore-domain dataset whose product names do not reliably overlap the apparel and home-goods catalog. The variant therefore rewards an explicit no-match finding instead of speculative category mapping.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — ticket-specific policy answers | Retained and generalized as new R1 | Policy titles and controlling terms are required. The answer-key list of customer names and exact resolutions is replaced with a complete-ticket check so equivalent policy-correct remedies are accepted. |
| R2 — exact three lowest classes and values | Rewritten as new R5 | The minimum-sample and sort rule are explicit. The variant checks the complete calculation and displayed result instead of embedding the three class names and hard-coded rounded values in the rubric. |
| R3 — fixed jumper and sizing comparisons | Rewritten and merged into new R6 | The audit must compare overlapping types with direct listing and review quotations, but the instructions do not require a particular product example or exact quotation. |
| R4 — optimized descriptions with fixed examples | Rewritten as new R7 | Truthful optimization and evidence-based qualification remain required. The conditional Minimalist Desk Lamp criterion is removed because that product is absent from the source catalog and therefore cannot be rewritten in a row-preserving output. |
| R5 — three dashboard sheets | Retained and expanded as new R3 and R4 | The original row under-specified Sessions and did not independently check the ten-row product aggregation and catalog-match method. |
| R6 — audit PDF format and sections | Retained as new R6 | Page length, section order, cross-checks, and recommendation count are explicit. |
| R7 — triage margin context | Rewritten as new R2 | The original criterion encouraged loose general-category mapping despite the source-domain mismatch. The variant requires a match basis and explicitly accepts a documented no-match or insufficient-data result. |
| No original row — complete optimized catalog fields | Added to new R7 | Row preservation, all source columns, every empty SEO and Google field, and per-row justifications are central deliverable requirements that were not fully scored. |
| No original row — exact output filenames | Added to new R1, R3, R6, and R7 | The task specifies exact filenames and sheet names. |

## Score, output, and trajectory evidence examined

All 35 distinct judge reports across main runs were inspected. Scores ranged from 0/54 to 54/54, with a median of 22/54. Policy-response failures appeared in 32/35 reports; optimized-description failures in 24/35; low-class calculation failures in 20/35; and dashboard-structure failures in 19/35.

Representative outputs and trajectories examined:

- Refined Luna: 24/54 and 40/54. It covered all six tickets, used all five relevant policy titles, produced the exact three dashboard sheets, created a three-page four-section audit, preserved 43 catalog rows, and filled the SEO and Google fields. Judges disagreed over whether its wool-jumper wording sufficiently tempered a softness claim. Its trajectory focused on the sales/catalog mismatch and systematic SEO completion.
- Sol rubric-gold: 54/54 in both reports. It covered all tickets, computed the target class ranking, built the three dashboard views, and filled the catalog fields. Its delivered filenames used lowercase rather than the exact requested capitalization, a requirement the original rubric did not test.
- Qwen reasoning: 6/54 and 14/54. It cited only one policy title across the responses, analyzed a 5,000-row review subset instead of the complete data, produced an 1,840-row Underperformer Crosswalk instead of ten rows, and left 201 SEO or Google Shopping cells empty.

The complaint workbook, policy document, product catalog, and sales CSV were inspected directly. Representative PDF, DOCX, XLSX, CSV, and trajectory contents were compared with judge explanations.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts or over-prescriptive checks:

- Requiring exact low-class names, rounded statistics, jumper wording, and selected review phrases in the rubric rather than validating the instructed method.
- Treating a source-absent Minimalist Desk Lamp as a required optimized row.
- Encouraging unsupported margin inference from broad categories when no reliable product-name match exists.
- Awarding full credit to a deliverable with filename capitalization that did not match the exact specification.

Genuine failures observed:

- Omitting policy section titles or controlling terms.
- Using a review subset, applying the wrong class filter or sort, or failing to quote actual review text.
- Producing a crosswalk with more or fewer than ten products or using row-level rather than product-level aggregation.
- Repeating contradicted claims, omitting fit guidance supported by reviews, failing to preserve catalog rows, or leaving required feed fields blank.
- Presenting margin claims without a defensible sales match.

## Weight preservation

- Original total weight: 54
- Variant total weight: 54
- Reallocation: weight was moved from fixed answer examples to complete ticket coverage, defensible data matching, product-level aggregation, full-dataset calculations, exact deliverable structure, and row-complete catalog optimization.
## Second-pass validation
- Replaced unbounded "benefit-oriented" and "searchable language" judgments with source-supported product-benefit and product-specific terminology criteria that do not reward length or keyword stuffing.
- Preserved the rubric's 54-point total.
- Deferred access to the local and external source datasets and deterministic completeness and aggregation checks to evaluator infrastructure; no hidden product matches, rankings, or policy answers were added.
