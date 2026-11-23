# APEX third:edge: the 11 failing runs that break no invariant

Question (user, 2026-11-23): of the 67 failing runs in the APEX third:edge mining run, 11 break no invariant. How many
rubric criteria does each fail, which ones, what is the judge's verdict, and what actually happened?

Sources: mining run `runs/im-apex-edge-20261120T082216Z` (`report.json`: invariants, per-run outcomes, rewordings);
the runs' `grading/grades.json` (criteria, judge gemini-3.8-flash, verdict rationales) and `agent/answer.json`; the
trajectories (`trajectories/<task>_<run>.json`, step ids `sN.cK` call, `sN.oK` output, `sN.r` reasoning summary);
the Harbor task folders (`~/apex-v11-hub/apex-agents-1-1/<task>/`: `instruction.md`, `solution/answer.txt`).
Quotes are verbatim (cut with "…"). All 11 runs are GPT-5.6 Luna high; the passing runs of these tasks are Astra.

## Failed criteria per run

| task | run | criteria | failed | score |
|---|---|---|---|---|
| world228-jp-01 | luna1 | 1 | 1 | 0.00 |
| world228-jp-01 | luna2 | 1 | 1 | 0.00 |
| world228-jp-01 | luna3 | 1 | 1 | 0.00 |
| world228-jp-01 | luna4 | 1 | 1 | 0.00 |
| world228-jp-01 | luna5 | 1 | 1 | 0.00 |
| world-131-jr-1 | luna2 | 6 | 4 | 0.33 |
| world-131-jr-1 | luna4 | 6 | 4 | 0.33 |
| world-131-jr-1 | luna5 | 6 | 2 | 0.67 |
| world112-1-task05 | luna1 | 3 | 1 | 0.67 |
| world112-1-task05 | luna2 | 3 | 1 | 0.67 |
| world112-1-task05 | luna3 | 3 | 1 | 0.67 |

18 failed criteria in all. Every verdict was checked against the answer: in all 18 the judge is right (the reported
value differs from the reference). No grader error here.

## One-line summaries

- **world228-jp-01** -> 1 criterion ("difference … is 28.61%") failed in all 5 Luna runs; all 5 Astra runs passed. All
  five answered 36.40: they took the cumulative 5-year index values for 2024 (ATR 144.64, Peer 108.24, base 100 in
  2019) and subtracted them, instead of the 2024 one-year returns (144.64/112.48 − 1 vs 108.24/108.26 − 1). Four runs
  got the values by decoding the page-2 chart's vector paths; two of them (luna4, luna5) read the 10-K's Share
  Performance page as an image, and luna4 even computed ATR's one-year 28.59% in its reasoning, then chose the
  cumulative reading.
- **world-131-jr-1** -> runs luna2 and luna4 fail 4 of 6 (events per year and minutes per event, both countries),
  luna5 fails 2 of 6 (Netherlands only). luna2/luna4 never read the hazard frequency sheet and counted outage records
  as events (8 and 7 over 3 years -> 2.67 and 2.33 per year), despite the task's warning that Outage IDs are not
  events. luna5 used the frequency sheet correctly but mapped only Storm + Flooding to "Weather - Storm", leaving out
  Ice_Storm (6.87/year in the Netherlands): 22.39 instead of 29.26.
- **world112-1-task05** -> 1 criterion (total savings $69,725,793.18) failed in luna1-3 by one cent ($…793.19);
  the other two criteria passed. All three took the current input-material cost as the memo screenshot's
  cent-rounded $104,570,050.54 instead of recomputing it ($104,570,050.5352…), so material savings came out
  $9,337,537.2887 instead of $9,337,537.2839, which rounds to .29 instead of .28.

## Why no invariant caught them

In each of the three tasks the mining run **had proposed the decisive invariant**, but it gave no importance point:

| task | decisive invariant (as proposed) | what happened to it | outcome on these runs |
|---|---|---|---|
| world228-jp-01 | i8: obs. "The performance table gives cumulative index values (base 100) at prior-year end and requested-year end …" -> "computing each series' return as end/prior-end minus 1, their absolute difference …" | Luna's F2 said seen in all 5 and F3 not followed (5 would-be points); the Opus re-check (on failing runs since turn 97) answered **not seen** in all 5 | not seen x5 |
| world-131-jr-1 | i11: "… assigning ice-storm to the storm category" | on **luna5 (a failing run)** the too-narrow check answered "same purpose, other action", which triggered a rewording from luna5: ri11 "… settles whether the unnamed extra hazard type is counted, either by adding it to the storm category **or by leaving it out**" | luna5 followed (ri11); luna2/4 not seen |
| world-131-jr-1 | i12: obs. "outage IDs do not correspond to individual events; the frequency sheet gives events per year …" -> "sums events-per-year across the country's regions" | needs the frequency sheet to have been read | luna2/4 not seen (never read it); luna5 followed |
| world112-1-task05 | i14: "Computes per-category straight-average yield rounded half-up to 0.01%, and material savings as output divided by current vs new target yield …" (Astra's method, which gives .28) | luna1, luna3 answered "same purpose, other action"; rewording from **luna1 (a failing run)**: ri14 "current material cost (from current yields **or the memo's stated baseline**) minus …" | followed x3 (ri14) |

So the 11 "break nothing" runs come from three different causes:

1. **A rewording from a failing run loosened the decisive invariant until it accepted the failing behaviour**
   (world-131 luna5, world112 luna1-3: 4 runs). The design rewords on a failing run's "same purpose, other action"
   (TECHNICAL.md: failing cell `purpose_otherwise` -> no point, and reword). Here the "other action" is exactly the
   error, so the reworded invariant now covers it ("or by leaving it out", "or the memo's stated baseline").
2. **The decisive observation never appears in the failing run** (world-131 luna2/luna4: never opened the frequency
   sheet; world228: never got the prior-year index values as text: 7 runs). The error happens before the invariant's
   observation can hold, so the invariant is "not seen". In world228 luna4 the table values were seen in an image (its
   reasoning computes 144.64/112.48 − 1 = 28.59%); the checks did not count that as seen.
3. No invariant covers the upstream decision itself: "the task warns that Outage IDs are not events and a hazard
   frequency workbook is listed -> read its frequency sheet" (world-131), or "the chart has no values -> find the
   year-end table" / "2024 performance = one-year change" (world228). Related invariants exist but are coarse:
   world-131 i5 "Reads small header ranges of the candidate tabs" and world228 i7 "Renders the performance table pages
   … as images" were judged followed although the runs read other tabs / rendered the chart page.

Proposed fixes (not built): do not reword from a failing run's "same purpose, other action" (only from passing runs),
or re-check such rewordings against the failing run's grade; let F2/F3 see images the agent read (world228 luna4).

---

## Task 1: `world228-jp-01-9700a477` (5 runs)

**Task:** "Using the 2024 ATR annual report, reply to me with the absolute performance difference between ATR shares
and the Peer Group in 2024 as a percentage (round this to two decimal places)."

**Reference:** "The difference in share performance is 28.61%." (Astra runs 1-5: "Using the year-end values in the
2024 annual report's "Share Performance" table (page 19): |(144.64/112.48 − 1) − (108.24/108.26 − 1)| × 100 = 28.61%".)

**Criterion (the only one):** "States that the difference in share performance for 2024 is 28.61%"

| run | answer | judge verdict (verbatim, Assessment) |
|---|---|---|
| luna1 | "ATR shares returned approximately **44.64%**, versus **8.24%** for the Peer Group. **Absolute performance difference: 36.40 percentage points.**" | "The agent reported the difference as 36.40 percentage points rather than 28.61%. Therefore, the criterion is not met." |
| luna2 | "ATR shares returned approximately **44.64%**, versus **8.24%** … **36.40 percentage points**." | "The agent reported an absolute performance difference of 36.40 percentage points instead of the required 28.61%." |
| luna3 | "ATR shares returned approximately **144.64** versus **108.24** … **36.40 percentage points**." | "The agent reported the difference as 36.40 percentage points rather than 28.61%." |
| luna4 | "cumulative return index of **144.64**, versus **108.24** … **Absolute performance difference: 144.64 − 108.24 = 36.40%**." | "The agent calculated and stated the difference as 36.40%, failing to state 28.61%." |
| luna5 | "ATR shares were **144.64** versus **108.24** … **Absolute performance difference: 36.40%**." | "The agent reported an absolute performance difference of 36.40% rather than 28.61%." |

**What happened.** The chart on page 2 of the annual report ("Total Shareholder Returns", base 100 in 2019) has no
data labels; the year-end values are in the Share Performance table (annual report p. 19; 10-K p. 22). The 2024
performance is the change during 2024: ATR 112.48 -> 144.64 (+28.59%), Peer 108.26 -> 108.24 (−0.02%).

- **luna1** never found the table. After the page-2 image and text gave no values, it spent ~40 steps reverse-engineering
  the chart's PDF vector paths (pdfplumber, pypdf content stream), got ATR 144.64 and Peer 108.24 for 2024 (s55.o1:
  "ATR 223.164 144.63803266609352 return 44.63803266609352 / Peer 199.452 108.23867125138153 return
  8.238671251381533 / diff 36.399361414712") and reported the 5-year cumulative difference. Its reasoning even derived
  the 2023 ATR point (s55.r2: "I'm determining the left and right endpoints, which yield around 112.48 and 144.62,
  respectively") but did not use it as the base.
- **luna2, luna3** did the same vector decoding of the page-2 chart (luna2 s22.c1, luna3 s14-s16) and subtracted the
  2024 index values.
- **luna4** searched the 10-K, read p. 22 ("SHARE PERFORMANCE … five year comparison of the cumulative total
  stockholder return") and rendered it as an image (s12). Its reasoning saw the right calculation: "I need to compare
  the share returns from December 2023 to December 2024. Calculating for AptarGroup, the numbers give me 28.59%. I'm
  also checking the Peer Group figure, which might be around 108.26", then settled on the cumulative reading: "The
  indexed values indicate cumulative total returns, with the AptarGroup representing a cumulative performance of
  44.64% since 2019 … So, the difference I obtained makes sense in this context."
- **luna5** decoded the chart vectors (s9-s10), then rendered 10-K p. 22 (s13) and computed only the index difference and the
  difference relative to the peer (s15.o1: "36.40 ⏎ 33.63"), reporting 36.40%.

**Invariants:** i8 (the decisive one): Luna's F2 said seen and F3 not followed in all 5; the Opus re-check of F2
said not seen in all 5, so it is "not seen"; i7 "Renders the performance
table pages of the target report as images" counted as followed in all 5, though luna1-3 rendered only the chart
page (page 2), not the table.

## Task 2: `world-131-jr-1-2930a41b` (3 runs)

**Task:** "For France and the Netherlands, evaluate the weather-related outage causes in terms of total outage
duration. Categorize hazards relating to flooding or storms as the "Weather - Storm" cause and those relating to heat
or wildfire as the "Weather - Heat" cause. For each country, state the top weather cause by outage duration, the
total events per year in that cause, and the average outage minutes per event in that cause. Note that the Outage ID
doesn't reflect individual events; it can be a single event or multiple events combined. …"

**Reference:** France: Weather - Heat, 23.42 events/year, 89.20 min/event. Netherlands: Weather - Storm, 29.26
events/year, 90.81 min/event. (Astra: "Flooding, Storm, and Ice_Storm were grouped as Weather - Storm; Heatwave and
Wildfire as Weather - Heat. Annual event frequencies were summed across each country's regions—not counted from
Outage IDs.") Durations come from `EuroGrid_Outage_Reliability.xlsx` (France heat 2,089 min, NL storm 2,657 min);
events per year from the `Extreme_Weather_Frequency` sheet of `Extreme_Weather_and_Climate_Stress_Dataset.xlsx`.

**Criteria (6):** top cause France / Netherlands (passed by all three runs); events per year France Heat 23.42 and
Netherlands Storm 29.26; minutes per event France Heat 89.20 and Netherlands Storm 90.81.

### luna2: 4 of 6 failed

| failed criterion | judge verdict (verbatim, Assessment) |
|---|---|
| total events per year for Weather - Heat in France is 23.42 | "The agent states that France had 2.67 events/year on average for Weather - Heat (or 3.00 in 2022, 3.00 in 2023, 2.00 in 2024), rather than 23.42." |
| total events per year for Weather - Storm in the Netherlands is 29.26 | "The agent reported 2.33 events per year (by counting outage records instead of the underlying event counts), rather than 29.26." |
| average outage duration per event for Weather - Heat in France is 89.20 minutes | "The agent reported an average outage duration of 261.13 minutes/event instead of the required 89.20 minutes." |
| average outage duration per event for Weather - Storm in the Netherlands is 90.81 minutes | "The agent reported 379.57 minutes/event instead of the required 90.81 minutes." |

**What happened.** luna2 read only the outage files and never opened the weather dataset (no call touches it). It
noticed the warning (s8.r: "each row has a unique Outage ID, but that doesn't necessarily reflect individual events.
It could represent one or multiple combined outages") and even thought of the right file (s12.r2: "Also, I should check
if "Extreme Weather..." offers insights."), but resolved it by counting rows (s12.c1: "records 200
unique IDs 200 duplicates []"), giving 8 heat records in France and 7 storm records in the Netherlands over 2022-2024:
2.67 and 2.33 per year, and 2,089/8 = 261.13 and 2,657/7 = 379.57 minutes per event.

### luna4: 4 of 6 failed

Same four criteria, same values (2.67, 2.33, 261.13, 379.57). Judge, e.g.: "The agent reported 2.33 events per year
instead of 29.26." / "The agent reports an average outage duration of 261.13 minutes per event rather than 89.20
minutes."

**What happened.** luna4 listed the weather workbook's tabs (s3.c4: "Extreme_Weather_Frequency … 76 rows",
"Asset_Exposure", "Outage_Probability", "Expected_Annual_Impact") but never read any of them. Its reasoning (s6.r2):
"each row representing an outage occurrence … create a report showing the total number of weather events divided by
the number of years to find an annual average." Footnote in its answer: "Events per year is calculated from outage
records across the three-year period. France’s top cause represents **8 total records**; the Netherlands’ represents
**7 total records**. Outage IDs were not treated as individual-event counts."

### luna5: 2 of 6 failed

| failed criterion | judge verdict (verbatim, Assessment) |
|---|---|
| total events per year for Weather - Storm in the Netherlands is 29.26 | "The criterion is not met because the agent reported 22.39 rather than 29.26." |
| average outage duration per event for Weather - Storm in the Netherlands is 90.81 minutes | "The agent reported 118.67 minutes instead of the required 90.81 minutes." |

**What happened.** luna5 found the right method: it read the frequency sheet (s6.c2) and summed events per year per
category across regions (s10.r: "I can't just count those; I'll need to calculate total events by summing the events
per year for weather hazards"). France came out right (23.42, 89.20). But its mapping was
`'Weather - Storm' if hazard in ('Storm','Flooding') else ('Weather - Heat' if hazard in ('Heatwave','Wildfire') else None)`
(s11.c1, s13.c1), so Ice_Storm, which the sheet lists for every region (Netherlands West 1.89, North 4.98), was
dropped. Netherlands storm: 5.47 + 2.84 + 7.77 + 6.31 = 22.39 instead of 22.39 + 6.87 = 29.26; 2,657 / 22.39 = 118.67
instead of 90.81. France is unaffected because its top cause is heat.

## Task 3: `world112-1-task05-na-cf44bbb8` (3 runs)

**Task:** payback analysis for upgrading Lorexa's equipment to continuous manufacturing: new target yield 99.99%
(lower input-material cost "as calculated in the Lorexa Equipment Performance dataset"), the other savings lines
doubled from the memo's table, equipment counts halved; report total savings, one-time investment and payback,
"Round the dollar amounts to the nearest $0.01".

**Reference:** total savings $69,725,793.18; investment $47,160,134.42; payback 0.68 years.

**Failed criterion (all three runs):** "States that, for the memo-defined annual analysis based on 2024 US Net
Product Sales and 2025 Darcylis operator hours, the new total savings from adopting continuous manufacturing is
$69,725,793.18." The investment and payback criteria passed.

| run | answer | judge verdict (verbatim, Assessment) |
|---|---|---|
| luna1 | "**New total annual savings:** **$69,725,793.19** — New input-material savings at **99.99% yield:** $9,337,537.29 …" | "The agent reported a new total annual savings of $69,725,793.19 rather than $69,725,793.18. Under the evaluation standards, every specific detail must be precisely verified with exact values, and approximate matches are insufficient." |
| luna2 | "**New total annual savings:** **$69,725,793.19**" | "The agent reported $69,725,793.19 instead of the specified $69,725,793.18. Per the evaluation standard, exact values are required and approximate matches are insufficient." |
| luna3 | "**New total savings from continuous manufacturing:** **$69,725,793.19**" | "The agent reported the new total savings as $69,725,793.19 instead of the specified $69,725,793.18." |

**What happened.** Total savings = input-material savings + doubled other savings ($60,388,255.90, the same in every
run). The difference is entirely in the input-material savings:

- Astra (s12 in astra1) recomputes the current material cost from the batch data with per-category yields rounded to
  0.01%: current $104,570,050.535249…, target $95,232,513.251325…, savings **$9,337,537.283924…** -> total
  $69,725,793.1839 -> **.18**.
- luna1-3 take the current cost as the memo screenshot's displayed **$104,570,050.54** (luna1 s15.r: "The current cost
  appears to be $104,570,050.54 from a screenshot"; s16.c1 `current=Decimal('104570050.54')`) and compute the target
  cost exactly: savings **$9,337,537.288675…** -> total $69,725,793.1887 -> **.19**.

The 0.0048 that the cent-rounded baseline adds is enough to cross the rounding boundary. The system prompt says "When
calculating numbers, unless specified otherwise, use the exact values without rounding them"; the runs used a rounded
displayed value as an input. A one-cent miss on one criterion fails the whole task.

## Patterns across the 11 runs

| why the run failed | runs |
|---|---|
| Wrong interpretation of the requested quantity (cumulative 5-year index vs the 2024 one-year change) | world228 luna1-5 |
| Wrong data source: counted outage records as events despite the task's warning; never read the frequency sheet | world-131 luna2, luna4 |
| Literal category mapping left out a hazard the reference counts (Ice_Storm as a storm) | world-131 luna5 |
| A cent-rounded intermediate (memo screenshot) used instead of recomputing, one cent off after rounding | world112 luna1-3 |

None is a grader error. All are content or method errors in the agent's work, and in each task the mining run had an
invariant for the right method; it gave no point because of a rewording from a failing run (4 runs), an observation
that never appeared as text (7 runs), or the Opus re-check (world228).
