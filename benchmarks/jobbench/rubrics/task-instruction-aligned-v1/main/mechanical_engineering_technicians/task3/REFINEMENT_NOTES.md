# Refinement notes — mechanical_engineering_technicians/task3

## Instruction-supported requirements

The refined instructions require a three-sheet FAT acceptance workbook and a disposition memo. Every performance point must be corrected to 2970 RPM with the stated affinity laws. All seven vibration points must be classified by operating region, evaluated against the supplied API limits where applicable, and assigned ISO severity zones using a reasoned resolution of the ISO 10816 applicability conflict. Both specified bearings require sourced geometry, defect-frequency calculations at actual speed, and FFT cross-reference at rated and 120% flow. The memo must give a disposition, standards discussion, balanced spectral diagnosis, corrective actions, and high-flow restrictions.

The variant checks source-derived failures but accepts reasonable rounding, interpolation choices, cited bearing geometries, and competing diagnoses that weigh all supplied evidence. It does not require one uncited internal bearing geometry, treat a point outside the AOR as an API pass, or force a hydraulic diagnosis while excluding plausible mechanical contributors.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
|---|---|---|
| R1 — efficiency failure | Merged into new R1 and R7 | Retained the guaranteed-efficiency comparison and numerical disposition. Integrated it with the complete instructed rated-flow table rather than scoring one parameter in isolation. |
| R2 — ISO 10816-3 exclusion | Merged into new R3 | Retained the scope-conflict analysis and Europump support. Rephrased it as an applicability determination so the criterion assesses sourced standards reasoning rather than recitation. |
| R3 — Category II limits | Merged into new R3 | Retained correct category, power-class, and zone use. Removed the hidden category and boundary values from the rubric wording; they must be selected and cited from the required external sources. |
| R4 — bearing frequencies | Rewritten into new R4 | Retained both bearings, all four formulas, actual speed, geometry, and reproducibility. Removed one fixed SKF 6313 ball diameter and frequency set as the only accepted answer because public catalog and corroborating manufacturer geometry can differ by bearing design or derivation. |
| R5 — FFT cross-reference | Rewritten into new R5 | Retained nearest-peak comparison and diagnostic verdicts. Removed the mandatory interpretation of one approximately 149 Hz peak and required a consistent tolerance, harmonics, sidebands, amplitude, and order-overlap analysis instead. |
| R6 — 1× and hydraulic diagnosis | Rewritten into new R6 | Retained source-derived 1×, 2×, and vane-pass changes. Removed the required conclusion that hydraulic loading is more likely than all mechanical causes; the instructions require investigation, and the IOM supports checking hydraulic and mechanical contributors. |
| R7 — performance table | Merged into new R1 | Retained the requested raw, corrected, rated, tolerance, deviation, and decision columns and expanded coverage to every point. |
| R8 — seven vibration points | Rewritten into new R2 | Retained all-point DE/NDE evaluation. Removed the assertion that Test Point 1 is an API pass under the 3.9 mm/s AOR limit because the zero-flow point is outside the specified AOR; it may be screened but is not formally qualified by that operating limit. |
| R9 — API/ISO reconciliation | Merged into new R3 | Retained Europump bridging and comparison of API overall, API discrete, and ISO zone thresholds. Removed a predetermined “close boundary” observation as a required conclusion. |

New R7 gives the required memo and corrective-action deliverable direct coverage. The revised allocation also increases weight on complete performance and standards work while preserving bearing and spectral rigor.

## Evidence examined

Judge reports, workbooks, PDFs, and trajectories were examined from four materially different runs:

- refined Luna landlock: 34/58 and 38/58;
- Sol rubric-gold: four reports at 58/58;
- Qwen 3.5 reasoning: 0/58 and 18/58;
- GPT-5.4: two reports at 18/58.

The refined Luna output correctly treated the shutoff point as outside AOR, corrected all performance data, showed rated-flow head and efficiency failures, used ISO 10816-7 through Europump, calculated both bearings from cited geometry, and gave a balanced hydraulic/mechanical diagnosis. Its derived 6313 geometry produced frequencies different from the original hidden values. Sol reproduced the rubric-gold values and conclusions. Qwen and GPT-5.4 omitted or misapplied substantial standards, FFT, and workbook requirements.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts included penalizing cited alternative bearing geometry, requiring one approximate BPFO value, treating a nearby FFT bin as a required defect discussion regardless of selected geometry, demanding a single hydraulic root cause, and treating the outside-AOR shutoff point as a formal pass. Reports also differed for the same refined Luna files despite identical evidence.

Genuine failures included omitting a required workbook sheet or point, failing to apply affinity exponents, using raw rather than corrected values for acceptance, applying ISO 10816-3 without addressing pump scope, omitting the NDE bearing, listing frequencies without FFT comparison, ignoring the vane-pass increase, and giving a disposition inconsistent with clear head, efficiency, or vibration failures.

## Weight reconciliation

Original total weight: **58**.

Revised total weight: **58**.

The original total was preserved. Weight was consolidated from overlapping efficiency, table, and standards rows and reassigned to complete all-point calculations, sourced standards applicability, balanced spectral diagnosis, and the required disposition memo.
## Second-pass validation
- Added a separate 4-point deliverable-structure row for the exact workbook and PDF filenames and the three required workbook sheet names.
- Reallocated one point from each of performance, vibration acceptance, standards discussion, and disposition; the rubric total remains 58.
- Kept source values, accepted limits, bearing geometry, and expected conclusions out of the rubric. Judge access to those references remains an evaluator-infrastructure requirement.
