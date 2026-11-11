# Refinement notes — online_merchants/task1

## Instruction-supported requirements

- Deliver `Incident_Analysis_Report.xlsx` with the three named sheets in the specified order and one conclusion-dependent PDF.
- Analyze INQ-001, INQ-003, and INQ-006 against `product_performance_Q4.csv`, including catalog means, metric ranks, inquiry details, relevant listing evidence, and relevant fashion-review patterns.
- Use the three instructed verdict labels and provide evidence-consistent actions, priorities, and customer responses.
- Put every catalog SKU on the risk dashboard with the required metrics and a risk level; identify non-escalated products sharing material risk indicators and cite related inquiries where relevant.
- Include a real visualization on the risk dashboard.
- Use the Kaggle reviews as industry-pattern context and the Shopify descriptions to assess expectation mismatch without treating either source as direct proof about a boutique SKU.
- Make the PDF's evidence and requested action fit the analysis: supplier corrective action with a timeline when systemic concerns are found, or a supported assessment memo otherwise.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — SKU-007 metrics and mandatory systemic conclusion | Rewritten and merged into new R2 and R7 | The metrics, means, and ranks are source-derived and remain assessable. The mandatory hidden conclusion was replaced with an evidence-supported-verdict requirement so an equivalent correct analysis with documented uncertainty is accepted. |
| R2 — mandatory SKU-016 finding | Merged into new R4 | SKU-016's elevated-return/low-rating and INQ-011 evidence remain useful checks, but the dashboard is now assessed as a full-catalog risk analysis rather than a one-product answer key. |
| R3 — mandatory SKU-005 wording | Merged into new R4 | The source-derived risk signal remains, but the rubric no longer requires the exact narrative that it is “similar” to SKU-007 or “warrants monitoring even though no escalated complaints exist.” |
| R4 — INQ-001 response only | Expanded into new R3 | The instructions require a response for all three escalated inquiries. The new row evaluates actual issue, concrete options, and verdict consistency for each response. |
| R5, R6, R7 — defect wording, quantitative notice evidence, listing mismatch | Rewritten and merged into new R6 and R7 | These rows overlapped around the same Dark Denim evidence. The replacement separates external-source analysis from PDF communication quality and accepts faithful paraphrase and equivalent correct analysis. |
| R8 — visualization | Retained as new R5 | This is an explicit task requirement. The criteria now distinguish actual workbook chart/conditional-formatting structures from a table merely labeled “visual.” |
| No original row | Added as new R1 and broader parts of R2/R4 | The original rubric did not directly assess required filenames/sheet order, all three decision rows, all-SKU dashboard coverage, INQ-006, or whether the selected PDF matched the conclusion. |

No instruction-supported requirement was removed. Unsupported exact wording, a single mandatory methodology, and a hidden final conclusion were removed.

## Score, output, and trajectory evidence examined

- All 37 available judge reports for this task were reviewed across the run tree. Scores ranged from 6/58 to 48/58; no report awarded 58/58.
- Refined Luna: both reports scored 48/58, failing only original R8. Direct inspection found one chart and two conditional-formatting rules on `Product Risk Dashboard`. Its trajectory used four sessions and generated the required XLSX and supplier notice.
- Sol rubric-gold: the high report scored 48/58 and the low report 38/58. Direct inspection found one chart and two conditional-formatting rules. The trajectory was a direct single-session build with workbook/PDF inspection.
- Qwen 3.5 reasoning: 28/58, failing original R1, R3, R6, and R8. Its shorter trajectory produced a workbook with one chart but weaker catalog-average, monitoring, and supplier-evidence coverage.
- GPT-5.4: 34/58 and 40/58 reports. Its workbook also contains an embedded chart; genuine omissions centered on supplier quantitative evidence and the additional-product narrative.
- Qwen 3.8 and Terra reports were also included in the all-report analysis. Representative workbook inspection covered refined Luna, Sol, Qwen 3.5, GPT-5.4, and Qwen 3.8.

Across the 37 reports, original-row failure counts were: R1 11, R2 17, R3 21, R4 4, R5 2, R6 16, R7 2, and R8 36. Several R2 failures were judge-response JSON extraction failures rather than submission findings.

## Likely judge artifacts versus genuine task failures

- **Likely judge artifact:** original R8 failed in 36 of 37 reports, although every representative workbook inspected contained an embedded chart; refined Luna and Sol also contained conditional formatting. The text extraction shown to the judge omitted workbook drawing/style metadata. The one R8 pass occurred on a lower-scoring Qwen 3.8 report, confirming inconsistent visibility rather than persistent absence.
- **Rubric-induced false negatives:** original R3 required exact comparative prose about SKU-005, and original R2 required a particular interpretation of SKU-016. Submissions could perform the instructed full-catalog risk analysis without those exact sentences.
- **Genuine failures:** lower-scoring runs often omitted catalog means, units sold, related inquiries, or quantitative supplier evidence; some responses omitted a refund option or the Dark Denim listing comparison. Those are instruction-supported and remain assessable.
- **Coverage gap in the original rubric:** it could score highly without fully evaluating INQ-006, all required response templates, all-SKU coverage, sheet order, or the appropriate conclusion-dependent PDF.

## Never-full analysis

The persistent ceiling was not evidence that no run satisfied the task. The strongest runs repeatedly reached 48/58 because the 10-point visualization row was marked failed even when the XLSX contained a chart and conditional formatting. Since R8 alone carried 10 points, this created a mechanical 48-point ceiling for otherwise full-scoring reports. Other recurring losses came from all-or-nothing rows tied to exact hidden conclusions or phrasing: R2/R3 demanded named additional-SKU narratives, and R6 demanded every numeric supplier-notice detail in one row. The revised rubric preserves the visualization requirement but states what workbook evidence qualifies, merges overlapping product-risk rows, expands coverage to all explicit deliverables, and evaluates defensible source-grounded reasoning rather than answer-key prose.

## Weight accounting

- Original total: **58**
- Revised total: **58**
- Reallocation: the original 22 points concentrated on named additional SKUs and the visualization were redistributed across the complete executive matrix, full-catalog dashboard, all three customer responses, external-source analysis, and PDF quality. The explicit visualization requirement retains 6 points.
## Second-pass validation
- Removed the hidden SKU-005 and SKU-016 answer from the dashboard criterion.
- Post-fix re-lint replaced the circular self-defined risk rule: similarity dimensions and thresholds must derive from escalated-product indicators and/or the catalog distribution.
- The rule must be applied to every non-escalated SKU and show all matches; a no-match conclusion requires the full-catalog comparison.
- The rubric total remains 58. Full source-dataset access and rendering of Excel charts or conditional formatting remain evaluator-infrastructure requirements.
