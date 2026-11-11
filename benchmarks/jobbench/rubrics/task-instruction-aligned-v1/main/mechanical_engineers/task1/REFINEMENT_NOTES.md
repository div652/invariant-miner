# Refinement notes — mechanical_engineers/task1

## Instruction-supported requirements

The task requires a reconciled ASME VIII-1 calculation package with three exact files. Rev-1 changes the bottom head, adds N5, changes the TL-to-TL shell length, and explicitly calls for hydrotest revalidation. The CSV must carry the exact instructed columns for shell, top head, and reconciled bottom head. The JSON must use the exact top-level keys and include every changed or added Rev-1 item, a UG-99(b) hydrotest analysis, complete N1/M1/N5 objects, shell and bottom-head external-pressure results, and material findings.

The text report must include the specified design-summary fields, formulas and intermediate values, external-pressure work, a quantified stiffening-ring-versus-thicker-shell comparison, nozzle reinforcement, material suitability, bill of materials, and conclusions. The instructions prescribe the F&D and external-pressure equations and require chart factors or their basis, but they do not disclose the chart results. They require the engineer to determine whether Appendix 1-7 applies, whether HIC testing is required, whether impact testing is adequate, and what external-pressure solution is economical; those conclusions must be derived rather than assumed.

## Original rubric disposition

- **R1 — retained and generalized in new R2.** The F&D formula and reconciled geometry remain, but hard-coded thickness results were removed.
- **R2 and R3 — retained and combined in new R4.** The exact shell and head external-pressure inputs and equations remain. Adequacy can be conditional when controlled chart values are not supplied.
- **R4 — retained as new R5.** A quantified ring-versus-thickness comparison and recommendation remain, without forcing one ring count or recommendation.
- **R5 and R6 — merged and expanded as new R6.** N1, M1, and N5 now receive complete direct coverage. The M1 Appendix 1-7 result and N5 curvature implementation must follow the actual geometry rather than a hidden answer.
- **R7 and R8 — merged and rewritten as new R7.** Wet-H2S, HIC, impact, UCS-66, and PWHT analysis remain. Mandatory HIC, S7/TM0284, Curve D, and impact-adequacy outcomes are no longer assumed in advance.
- **R9 — retained and expanded as new R8.** The design summary remains and now includes every report section, bill of materials, and machine-readable consistency.
- **New R1 and R3 — added.** Exact JSON schema, CSV parseability, complete Rev-1 reconciliation, and hydrotest analysis were explicit requirements omitted by the original rubric.

## Material changes and reasons

1. The rubric no longer embeds expected thicknesses, MAWP, hydrotest pressure, chart factors, or cost outcomes. These values must be recalculated from the named inputs and may reflect documented rounding or defensible material-property evidence.
2. `design_audit.json` is scored against the exact instructed keys. The original rubric allowed a full score even when a submission renamed every required top-level object.
3. External-pressure results may remain conditional when the proprietary ASME chart value is not present, but the submission must report the required Factor A/B lookup point or threshold and must not claim a fabricated pass.
4. A single midspan ring is no longer the only acceptable design. Any ring layout or increased-thickness option must be quantified and checked.
5. M1 is not automatically graded as Appendix 1-7-required. The finished opening and applicable limit must be calculated, and the resulting flag must be supported.
6. N5 is not forced to use one unexplained numeric crown-radius shortcut. Equivalent code-consistent head-curvature methods are accepted when their geometry and `tr` are shown.
7. The datasheet says HIC testing is supplementary, but neither the refined instructions nor the supplied datasheet alone establishes one universal purchase designation and acceptance criteria. The submission must identify the governing sour-service basis and any missing confirmation.
8. Impact adequacy is judged through temperature, energy, thickness, material condition, UCS-66 curve, and exemption analysis rather than a predetermined pass.
9. Parseable CSV rows, exact JSON keys, complete nozzle fields, UG-22 coverage, and cross-file agreement receive direct weight.

## Score and trajectory evidence examined

The available report set contains **33 judge reports across 16 runs**. Representative outputs and trajectories were inspected for:

- **Refined Luna landlock:** 34/66 and 40/66. It used the exact filenames and requested JSON keys, reconciled eight Rev-1 entries, calculated component MAWPs and hydrotest, and explicitly left controlled external-pressure chart lookups conditional. Judges failed missing numerical bottom-head chart capacity, a fixed one-ring statement, an unperformed Appendix 1-7 stress check, and a specific N5 curvature method. Its trajectory did not receive the rubric.
- **Sol rubric-gold:** 66/66 in both reports. It included the narrow expected calculations, but `design_audit.json` used `reconciliation_entries`, `hydrotest_analysis`, `nozzle_reinforcement`, and `material_findings` instead of the exact required schema. Its trajectory contained evaluator guidance. The original rubric never tested the schema defect.
- **Terra:** 24/66 in both reports. It produced all three files and many internal-pressure results, but omitted a UG-29 comparison, did not complete Appendix 1-7 stress checks, and lacked the required exact JSON object names. Its trajectory did not receive the rubric.
- **GPT-5.4:** 0/66 and 6/66. It used alternative external-pressure lengths, omitted the ring economics, did not perform the required impact comparison, and left several nozzle and report requirements incomplete.

The design CSV, Rev-1 rows, workbook sheets, Sample 5 pages, Macsteel datasheet statements, PVEng ring example pages, output CSV rows, JSON objects, report sections, judge reasons, and representative session trajectories were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include requiring one exact thickness result without considering field definitions or rounding; forcing a single midspan ring; automatically declaring M1 subject to Appendix 1-7; requiring one N5 curvature shortcut; treating HIC testing, a particular supplementary designation, Curve D, and impact adequacy as predetermined conclusions; or requiring numerical ASME chart values that are not supplied while rejecting a transparent conditional result.

Genuine failures include unreconciled Rev-1 changes, malformed CSV, wrong JSON keys, omitted nozzles, inconsistent geometry across files, using design pressure instead of calculated MAWP without disclosure, inventing chart factors, claiming external-pressure adequacy without a calculation, no quantified ring/thickness comparison, no large-opening determination, incomplete area accounting, unsupported material conclusions, missing report sections, or inconsistent CSV/JSON/report values.

## Weight accounting

- Original total: **66**
- Variant total: **66**
- Weight moved from predetermined engineering outcomes to exact deliverable structure, complete reconciliation, traceable calculations, uncertainty handling, and cross-file consistency.
