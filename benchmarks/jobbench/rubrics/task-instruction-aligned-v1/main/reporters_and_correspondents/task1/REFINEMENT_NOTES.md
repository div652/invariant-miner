# Refinement notes — reporters_and_correspondents/task1

## Evidence reviewed

- Refined instructions, original rubric, source refinement notes, task card, editor email, interview notes, the 50-row water CSV, and the CDC workbook. The supplied CT, EPA, and NRDC PDF requirements were cross-checked through the source notes and the extracted citations and values in representative outputs.
- All 35 available judge reports. Scores ranged from 0/60 to 60/60.
- Representative outputs and trajectories:
  - Refined Luna: 26/60 and 42/60; 114 tool calls across four session files. Its pitch used a documented two-period average for 2020 and 2024.
  - Sol rubric-gold: 60/60 in both reports; 65 tool calls. Its source log had 38 entries but used `Verified (Yes/No/Partial)` rather than the refined instruction's exact `Verified` header.
  - Qwen reasoning-on: 36/60 and 44/60; 67 tool calls. It produced a detailed pitch and 42-entry log but added several external-source variants and an aggressive narrative.

## Instruction-supported requirements

The task supports grading exact filenames, page/sheet limits, all five water systems, independently calculated 15 ppb and 10 ppb flags, a documented 2020-to-2024 change method, annual CT/national values or reasons for absence, city-level threshold counts and rankings, at least 15 precisely located source-log entries, Connecticut's legislative threshold change, all five service-line burdens, LCRI enforcement timing, a numerical Waterbury/Newark parallel, interview verification, and the paint-versus-water editorial issue. It does not require a specific endpoint method, a particular story thesis, the basis of the state high-risk designation, or discussion of high-risk towns absent from the water CSV.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — high-risk list | Merged into new R1 | Retained membership and rank for all five cities. Removed the designation-basis explanation and the five uncovered communities because the refined instructions do not request either. |
| R2 — 2020-to-2024 changes | Merged into new R2 | Removed hard-coded endpoint percentages. The instructions explicitly allow a documented endpoint or averaging method; the revised row grades arithmetic and disclosure. |
| R3 — CT versus national | Retained as new R3 | Removed hard-coded annual figures, the forced “not submitted” wording, and the mandatory 2017 anomaly explanation. Retained every year, both thresholds where available, reasons for missing values, and material comparability caveats. |
| R4 — city counts | Merged into new R1 | Retained all requested counts and ranks without leaking them. This removes overlap with original R1. |
| R5 — source log | Retained as new R4 | Changed the header requirement to the refined instruction's exact `Verified` column and separately checks allowed values. Retained minimum entries, source coverage, and precise locations. |
| R6 — Connecticut legislation | Expanded into new R5 | Removed the leaked answer while retaining act/date/threshold accuracy. Added the editor's explicit requirement to verify Dr. Martinez's factual claims and the referral claim. |
| R7 — service lines | Expanded into new R6 | Removed hard-coded counts and the mandatory Hartford conclusion. Retained all five counts, populations, ratios, burdens, and replacement deadline, and added the pitch's Waterbury/Newark, water-versus-paint, and enforcement-timing requirements. |
| R8 — threshold periods | Merged into new R2 | Removed the hard-coded exceedance list. The original criterion incorrectly implied that the CSV's `Action_Level_Exceedance` field consistently represented the 15 ppb rule even though inspected Hartford 2024 rows are marked Yes below 15 ppb. The new row requires preserving the source field and separately calculating and reconciling both flags. |

## Score and trajectory findings

The refined Luna workbook used the mean of both semiannual periods for its 2020-to-2024 comparison, a method expressly allowed by the original rubric and refined instruction. One judge still failed it for not matching the hidden single-period values; this is an artifact. Both refined reports also failed R1 for omitting the designation basis and unrepresented towns, neither of which is requested by the refined task. Its omission of some service-line population details in the pitch is a genuine failure.

Sol received full credit under the original rubric, but its source-log header is not the exact five-column header now required by `TASK_INSTRUCTIONS.txt`. The variant corrects that gap instead of inheriting the judge's permissiveness. Qwen's detailed external citations do not receive extra credit unless the six required sources and precise locations are covered.

## Likely judge artifacts versus genuine task failures

- **Artifacts:** forcing one endpoint convention, requiring a specific 2017 anomaly note, requiring discussion of towns outside the five-system scope, and treating the source exceedance field as logically identical to the independent 15 ppb flag.
- **Genuine:** missing cities or threshold counts, incorrect CDC row extraction, absent missing-data explanations, wrong source-log header, fewer than 15 entries, omitted service-line population figures, unsupported interview claims, or failure to address the paint/water and enforcement questions.

## Weight accounting

- Original total: **60**
- New total: **60**
- R1+R4 became a 14-point City Cross-Reference row.
- R2+R8 became a 14-point Water Lead Trends row.
- Original R3, R5, R6, and R7 retain 10, 8, 6, and 8 points as rewritten or expanded rows.
## Second-pass validation
- Clarified that Water Lead Trends requires every water system × year × monitoring-period record rather than an annual or period-only aggregation.
- Required a sourced value or a specific source-grounded missing-data reason for every Connecticut and national field in every requested year.
- Preserved the rubric's 60-point total.
- Deferred authoritative source context and DOCX page-count observability to evaluator infrastructure; no hidden city values, legal facts, monitoring results, or page-count proxy was added.
