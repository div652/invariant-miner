# Never-full task analysis

Thirteen main-split tasks had no perfect weighted score among the 2,417 judge reports indexed across the available runs. Reviewers examined every available report for their assigned priority task, deduplicated repeated materialized results where appropriate, and inspected representative outputs and trajectories. Judge outcomes were used to locate recurring failures; they were not treated as proof that a rubric requirement was valid.

| Task | Reports | Best score | Main ceiling in the original rubric or judge |
|---|---:|---:|---|
| `biostatisticians/task1` | 37 | 62/72 (86.11%) | Required a `<30` subgroup even though the correctly filtered data had none. |
| `biostatisticians/task2` | 37 | 50/58 (86.21%) | Required an unsupported elective-versus-emergency A1C conclusion and sometimes rejected equivalent wording. |
| `bookkeeping_accounting_and_auditing_clerks/task2` | 35 | 46/52 (88.46%) | Required account aliases, exact prose, and adjustment methods that conflicted with or exceeded the supplied sources. |
| `civil_engineers/task3` | 38 | 68/76 (89.47%) | Required pier-cap patching, a 42-inch haunch flange, and multiple pricing sources without instruction or source support. |
| `court_clerks/task1` | 31 | 44/76 (57.89%) | Forced hidden Judge-note values, exact phrases, and unreconciled totals over defensible source reconciliation. |
| `management_analysts/task1` | 37 | 78/88 (88.64%) | Required incorrect complaint prevalence and quartile conclusions plus prescribed causal and consolidation narratives. |
| `medical_and_health_services_managers/task2` | 37 | 66/86 (76.74%) | Required hidden peer benchmarks, fixed payer methodology, fixed actions, and unavailable cash values. |
| `online_merchants/task1` | 37 | 48/58 (82.76%) | The judge rejected embedded charts in 36 reports and required predetermined SKU narratives and conclusions. |
| `personal_financial_advisors/task1` | 37 | 68/78 (87.18%) | Required prescribed tax, duration, trade, and loss-harvesting conclusions, including a false source-file premise. |
| `police_fire_and_ambulance_dispatchers/task1` | 37 | 74/94 (78.72%) | Required an incorrect eight-unit Battalion 2 roster that placed A19 in the wrong battalion. |
| `sales_representatives_wholesale_and_manufacturing_technical_and_scientific_products/task1` | 37 | 96/106 (90.57%) | Required unsupported HART 7 compatibility, an 8–10-day schedule, and fixed scope and savings conclusions. |
| `social_science_research_assistants/task3` | 38 | 42/50 (84.00%) | Bundled valid checks with a non-equivalent ESS comparison and prescribed memo recommendations. |
| `training_and_development_specialists/task1` | 36 | 48/54 (88.89%) | Required Equipment Operation to have the highest normalized ROI although the source data makes Safety Orientation highest. |

## Findings retained in the revised rubrics

### `biostatisticians/task1`

The revised rubric makes small-stratum handling conditional on a small stratum actually existing and removes the unsupported attribution of the threshold to ICH E9 §5.7. It retains checks for correct subgroup denominators and statistics, the requested eight-scenario sensitivity matrix, missing-data analysis, and regulatory interpretation.

### `biostatisticians/task2`

The revised rubric removes the hidden A1C comparison and accepts equivalent explanations. It retains forest-plot completeness, correct Week 12 to Week 24 conditional-power projection, ITT-LOCF handling, and consistent outlier-site selection.

### `bookkeeping_accounting_and_auditing_clerks/task2`

The revised rubric accepts source-consistent account names, valid spreadsheet formulas, equivalent transaction descriptions, and defensible adjustment methods. It retains check-number matching, cleared-versus-outstanding classification, bank-side reconciliation, AP and journal-entry consistency, correction completeness, and agreement between workbook counts and memo totals.

### `civil_engineers/task3`

The revised rubric removes the unsupported repair scope, haunch dimension, and source-count requirement. It retains independent quantity reconciliation, skew adjustment, traceable removal, rebar and haunch calculations, supported pricing and lifecycle assumptions, and environmental and construction-timing risk analysis.

### `court_clerks/task1`

The revised rubric permits documented reconciliation of conflicting sources instead of forcing hidden values or phrases. It retains complete discrepancy coverage, required register fields and annotations, official sentencing-order quality, and complete CMS docket and financial updates.

### `management_analysts/task1`

The revised rubric removes incorrect fixed conclusions and evaluates whether findings follow the supplied records and disclosed method. It retains monthly trends, workforce metrics, complaint-category analysis, method transparency, and the requested COPQ columns and summaries.

### `medical_and_health_services_managers/task2`

The revised rubric removes unavailable benchmarks, fixed narratives and actions, and prescribed methodology. It retains reconciled financial calculations, monthly discipline-level loss analysis, required schema and naming, and supported revenue-impact assumptions.

### `online_merchants/task1`

The revised rubric judges whether the workbook contains usable visual analysis rather than relying on the prior false-negative pattern, and it removes predetermined SKU stories. It retains catalog averages, units sold, related-inquiry evidence, supplier-notice metrics, listing-language analysis, and complete customer resolution options.

### `personal_financial_advisors/task1`

The revised rubric removes prescribed conclusions and overlapping all-or-nothing tax penalties. It retains complete provisional-income and Social Security taxation, defensible tax rates, correct market-data aggregation, concentration and loss analysis, and internally consistent gift-liquidation and implementation timing.

### `police_fire_and_ambulance_dispatchers/task1`

The revised rubric derives roster membership, unit selection, and response composition from the supplied operational data instead of hidden answers. It retains CAD commitment and status-conflict handling, specialty eligibility, ALS-level response adequacy, double-booking prevention, and complete correctly named deliverables.

### `sales_representatives_wholesale_and_manufacturing_technical_and_scientific_products/task1`

The revised rubric removes unsupported protocol certification and fixed schedule, scope, and savings conclusions. It retains protocol-detail accuracy, source citation quality, supported TCO maintenance and warranty analysis, competitive-comparison scope, and arithmetic consistency.

### `social_science_research_assistants/task3`

The revised rubric separates valid evidence checks from prescribed interpretations and accepts a blank or explicit not-applicable benchmark when clearly represented. It retains the required benchmark layout, response aggregation, divergence flags, explanations, country-anomaly handling, and codebook mapping accuracy.

### `training_and_development_specialists/task1`

The revised rubric computes ROI and backup suitability from the provided data rather than forcing named winners or constraints. It retains correct proficiency-level interpretation, complete budget totals and formulas, allocation percentages, supported break-even analysis, survey coverage, certification continuity, and source traceability.
