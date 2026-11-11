# Refinement notes — police_fire_and_ambulance_dispatchers/task1

## Instruction-supported requirements

The task requires four exact deliverables: a two-sheet dispatch workbook, a conflict CSV, an updated SQLite CAD copy, and a four-sheet handover workbook. The dispatch queue must cover all 15 calls with adjusted priorities, assignments, capability levels, and caller-description-based justifications. The matching matrix must separate capability eligibility from availability-and-proximity recommendations. The synchronization work must reconcile the queue, unit roster, station coordinates, and existing CAD assignments; identify duplicates or related incidents, double-booking, end-of-shift constraints, and other anomalies; and persist the new calls and assignments.

The handover workbook must include all incoming and pre-existing active incidents, battalion-level availability calculations, zero-coverage specialty flags, historical Montgomery County 911 category/type/township analysis, and every closest-unit deviation. The instructions define AVAILABLE as the only ordinarily free status, permit non-AVAILABLE assignments only through an explicit recall or redirect, define Medic Units as ALS, require specialty eligibility, and require a stated distance method. They do not prescribe one exact allocation of scarce resources, one coverage-label threshold, a single-engine response to an alarm, a particular normalized historical title string, or a hidden medical fact absent from the incoming-call record.

## Original rubric disposition

- **R1 — retained and rewritten as new R2.** Swift Water Rescue gating and the committed status of the capable resource remain. The prohibition on assigning any non-Swift-Water unit was narrowed so capable primary response can be accompanied by support resources.
- **R2 — rewritten and expanded as new R4.** The four named A02 units remain relevant source evidence, but the variant assesses every non-cleared CAD assignment and the E11 roster/CAD disagreement rather than four hard-coded units only.
- **R3 — rewritten as new R7.** Correct battalion arithmetic and specialty coverage remain. The incorrect eight-unit Battalion 2 roster and mandatory “reduced coverage” conclusion were removed.
- **R4, R6, and R10 — merged into new R1.** High-acuity medical triage, ALS capability, and caller-description-based reasoning remain. Unsupported onset timing, a mandatory tPA discussion, exact Medic selections, and bans on named BLS support units were removed.
- **R5 — rewritten as new R8.** Historical category, full-title, and township analysis remains. The requirement to use a hidden `911_calls_sample.csv` filename and one exact punctuation-normalized title was removed.
- **R7 — merged into new R1.** The alarm call still requires a source-grounded priority and proportional response. The unsupported “building management notified” fact and mandatory single-engine allocation were removed.
- **R8 — retained and expanded as new R6.** Exact incoming coordinates remain, and the instruction-required pre-existing active incidents are now assessed.
- **R9 — retained and broadened as new R3.** CAN versus SHOULD remains, but eligibility and recommendation are assessed for every call without requiring one hidden matrix layout or one exact unit choice.
- **New R5 — added.** The original rubric did not directly score the required synchronized database.
- **New R9 — added.** Exact sheet names/order and Operational Notes were explicit deliverable requirements omitted by the original rubric.

## Material changes and reasons

1. Battalion 2 is scored from `unit_status.csv`, not from the original rubric's incorrect roster. The source contains seven Battalion 2 units: E7, E8, T7, A18, M7, M8, and BC2. A19 belongs to Battalion 3.
2. Coverage flags are judged against the submission's stated criterion because the instructions require a criterion but do not define a hidden percentage or force the word “reduced.”
3. Stroke scoring no longer requires a 15-minute onset, a tPA window, M4, or exclusion of A11. The caller record supplies classic symptoms but no onset duration, and simultaneous-call allocation can justify another ALS unit or documented redirect.
4. Diabetic-emergency scoring no longer requires the unsupported statement that the patient took insulin that morning.
5. Commercial-alarm scoring no longer requires “building management notified,” a single engine, or an exact engine list. Those details are absent from the refined input or are operational choices.
6. Medical criteria accept equivalent capable allocations with explicit scarcity handling instead of grading against one concealed dispatch solution.
7. The historical-data row accepts documented full-dataset versions or subsets and documented title normalization. It does not require a hidden sample filename or exact punctuation.
8. Conflict scoring now covers all pre-existing commitments, source-status disagreements, redirects, and unsupported end-of-shift claims.
9. Database integrity, exact filenames, sheet names/order, active-CAD map coverage, and cross-deliverable consistency receive direct weight because they are explicit instructions.

## Score and trajectory evidence examined

All **35 available Grok judge reports across 17 runs** were parsed. Original-row failure counts were R1 10, R2 30, R3 35, R4 30, R5 24, R7 14, R9 24, and R10 25; R6 and R8 passed in every report. Criterion-level reasons were reviewed, including every failure on the always-failing Battalion 2 row.

Representative outputs and trajectories:

- **Refined Luna landlock:** 64/94 in both reports. It created all four exact files, inserted all 15 calls, produced 23 CAD call records and 46 assignments, included 15 incoming plus active CAD incidents, used the full Kaggle v32 history, and explicitly documented roster/CAD conflicts and redirects. Its trajectory was source-driven and did not receive the rubric. Judges failed the source-correct seven-unit Battalion 2 result, the non-M4 stroke allocation, and the use of a truck rather than a mandated engine for the alarm.
- **Sol rubric-gold:** 74/94 in both reports, the highest observed score. It handled many narrow expected conclusions but used wrong workbook sheet names and emitted `dispatch_cad_synchronized.db` instead of the exact required filename. Its trajectory contained evaluator guidance. Judges still failed Battalion 2 because the rubric expected eight units, and failed a title-source criterion despite a documented full Kaggle analysis.
- **Qwen 3.8 reasoning:** 54/94 in both reports. It correctly caught E11's source-status conflict and produced complete CAD/map outputs, but used non-required sheet names and assigned a BLS ambulance without ALS to the severe respiratory call. Its trajectory had no rubric guidance.
- **GPT-5.4:** 34/94 in both reports. It created all four files and a complete map, but substituted rescue squads for the explicitly required Swift Water capability based on station text, used a BLS-only respiratory response without immediate ALS, and used non-required dispatch sheet names. Its trajectory documented the water-rescue substitution.

Outputs were inspected at row level in both workbooks and the conflict CSV; SQLite table counts and assignments were queried; and representative session trajectories were reviewed for source use, evaluator-guidance exposure, tool choices, and final claims.

## Likely judge artifacts versus genuine task failures

Likely artifacts include the impossible eight-unit Battalion 2 requirement; forcing a “reduced” flag despite an unstated threshold; requiring a 15-minute stroke onset absent from the queue; insisting on M4 rather than an equivalent ALS allocation; treating any accompanying BLS unit as the primary stroke resource; requiring a single engine for the alarm; requiring “building management notified”; requiring the hidden sample filename; and rejecting a normalized full-title label solely for trailing punctuation.

Genuine failures include omitting the 15 calls, assigning a specialty incident without the required capability or escalation, marking ordinary engines as Swift Water eligible, failing to distinguish ALS from BLS, silently double-booking committed units, omitting roster/CAD status conflicts, failing to update the database, omitting active CAD incidents from the map, miscomputing battalion availability, omitting zero specialty coverage, missing required sheets, or producing inconsistent assignments across deliverables.

## Never-full analysis

No available report scored the original rubric at 94/94. The decisive persistent cause is **R3, which failed in all 35 reports**. Its first two criteria require eight Battalion 2 units and specifically include A19, but `unit_status.csv` assigns A19 to Battalion 3. Correct outputs consistently reported seven Battalion 2 units and 5/7 availability; the judge demanded 5/8. The third criterion also forced a “reduced coverage” label even though the instructions only require the submission to state its flag criterion.

The best-scoring Sol output reached 74/94 and still lost the full 10 points on the impossible Battalion 2 row. It also lost the historical-title row because the judge expected a particular sample-source description, even though the output identified and analyzed the required Kaggle dataset. The refined Luna output reached 64/94 and failed the same impossible row plus two over-prescriptive allocation criteria. Lower-scoring runs added genuine operational failures, especially omitted pre-existing commitments, false specialty eligibility, and BLS-only responses to ALS-level incidents.

The never-full pattern therefore combines one universal rubric defect with narrower hidden-answer effects and genuine task-execution errors. Replacing hard-coded conclusions with source-grounded completeness, capability, synchronization, and consistency checks makes full credit attainable without trivializing the task.

## Weight accounting

- Original total: **94**
- Variant total: **94**
- Weight moved from hidden medical facts, fixed unit choices, an incorrect battalion roster, and exact historical labels to complete queue coverage, database synchronization, comprehensive conflicts, active-map coverage, and cross-deliverable consistency.

## Second-pass validation

- Made Unit Matching Matrix coverage auditable by requiring the full roster or a reproducible candidate-selection rule with assigned, closest eligible, unavailable, and specialty-relevant units.
- Preserved professional discretion over priority order, assignment, recall, redirect, and mutual-aid choices.
- Deferred missing judge access to the source call, roster, station, original CAD, and historical datasets as evaluator infrastructure; no expected assignments or counts were embedded.
