## ⚠ Analysis: the "mark all todos completed" invariants earn importance through check errors (2026-11-19)

Four tasks keep an active invariant of the form *"all planned steps are done" -> "marks all todo items completed"* with
importance above 0: world226-td-02 i21 (I 1/6), anti-SLAPP i6 (I 5/8), 128-jr-1 i9 (I 3/7), world131-dv-03 i14 (I 1/4).
**These points do not mean that marking todos matters.** Checked against the trajectories:

- **The grade cannot depend on todos.** Every criterion is about the answer's content, and the judge sees the answer and
  the world's files. The todo list exists only in the agent's DSH session, and DSH does not act on it (no reminder, no
  finish gate).
- **5 of the 10 points are check errors.** Those runs did mark every todo `completed` as their last todo update:
  td-02 run 7, anti-SLAPP runs 8 and 9, 128-jr-1 run 10, world131 run 1. td-02 run 7 made the same call at the same step
  (s29, all 4 completed) as passing run 6, which was judged "followed".
- **4 points come from runs without a todo list** (anti-SLAPP runs 4, 5; 128-jr-1 runs 1, 3): nothing to mark.
- **1 point is real:** anti-SLAPP run 10 left its last item `in_progress`.
- **Correlation, not cause.** Failing runs that marked everything complete fail on the same content criteria as the
  rest: every failing anti-SLAPP run misses C1 ("applies only to a 'legal action'"), the failing 128-jr-1 runs compute
  wrong scores. The four runs without a list all failed, but most runs of these tasks fail (8/10, 7/10).

### What actually went wrong in the 5 failing runs whose point was a check error

All five fail on the answer's content; none has anything to do with todos (failed criteria from grading.json, quotes
from the trajectories):

| Run (score) | What the grader wanted | What went wrong |
|---|---|---|
| td-02 run 7 (0/6) | the six IRRs, e.g. 17.8% at 10% premium / 18x | Every IRR ~0.6 pt low (17.2%). Same scenario and same exit EBITDA as passing run 6 (K81 = 1,081.246), but it recalculated the whole workbook in LibreOffice, which returned `#VALUE!` in the debt/cash block (its reasoning: *"It might be due to a circular reference"*); after its workaround the exit equity at 18x was 19,414 (net debt ≈ +48) instead of the model's 19,917 (net cash 455.0, `'Copy of LBO'!K160`, which run 6 used with `=ROUND(((EBITDA×multiple − net debt)/entry equity)^(365/1826)−1,3)`). |
| anti-SLAPP run 8 (3/4) | C1: *"States that Chapter 27's motion-to-dismiss procedure applies only to a 'legal action.'"* | Same analysis as the passing runs, but no threshold framing: passing run 2 says *"But that is only the first requirement"*, run 3 *"But that is only the threshold category"*; run 8 says *"But that does not end the analysis."* Judge: *"never states the threshold legal proposition…"*. Borderline wording; every failing anti-SLAPP run misses C1. |
| anti-SLAPP run 9 (3/4) | C1, as above | States the petition is a "legal action" and lists the conditions (*"Chapter 27 permits 'a party' to move for dismissal only when the legal action is: …"*), never that being a legal action is the threshold. |
| 128-jr-1 run 10 (0/6) | scores 17 / 18 / 15 / 17 / 20, recommend discontinue | Same SkyLink ratings (2, 5, 2, 3, 3) and formula (5 − abs(rating − ideal)) as passing run 2, but different ideal ratings: it treated a higher number as better on every criterion (*"map each criterion descriptor to values from 1-5, ideally with higher values being more desirable … a 'Continue' rating of 'low to very low' could ideally score a 4 or 5"*). All five totals wrong (Continue 19, Graduate 21, Spin out 17, Sell 16, Discontinue 13); recommended Graduate. |
| world131 run 1 (0/1) | NPV €15.33 billion | €15.31 billion: it used €1.74875B a year (*"the annual renewable revenue is 1.74875 billion for year one"*) instead of the slide's headline *"€1.75B/year — renewable enablement"*, which passing run 2 used (see "APEX: world131-dv-03" in FAILING-RUNS.md). |

### Why the check errs: something in the pipeline is wrong (checked in the F2/F3 job transcripts)

Yes, something in the pipeline is going wrong, not Luna's reading. Luna sees the todo call fine: in td-02 run 7 it even quotes the call's output, "Updated todo list: 0 pending, 0 in progress, 4 completed". Three things combine:

1. **F2 pins the observation on the action itself.** "All steps are done" has no evidence apart from the todo update. F2 never sees the action by design, so it names the todo call (s29.c1) as the first place the observation holds.
2. **F3 is asked the wrong question for that case.** It must say whether the action came *after* the pinned location, but here the action is *at* it.
   - Taken literally the answer is "not followed", and Luna's reasoning says exactly that: "check if the agent took the specified action anywhere after the pinned location".
   - In other cells it bent the rule and said "followed".
   - Across the four invariants, identical behaviour got 5 "followed" and 6 "not followed". One of those six was a passing run that Opus corrected.
3. **The Opus re-check is one-sided.** Opus re-checks only a *passing* run's "not followed"; for td-02 run 10, Luna said not followed and Opus said followed. A failing run's verdict is final, so the same error survives only on failing runs, where it becomes an importance point.

**How far it reaches:**
- **APEX:** 8 of the 53 importance points have the observation pinned at one of the agent's own calls.
  - 7 of them are on todo calls: these 5, plus world224-os-task04 i15 runs 1 and 8.
  - 1 is a real partial action: in world224-os-task02 i9 run 2, the edit left early-year revenue hardcoded.
- **Harvey:** 3 of 19 points (runs 1–5) and 3 of 31 (runs 6–10). There Luna judged the content of the written script or response.md, which looks like a genuine check, but I haven't re-examined those.

**Fixes I'd propose (not built):**
- F3 gets a separate, neutral outcome for "the action is the pinned item itself".
- A failing run's "not followed" gets the same Opus re-check as a passing run's.
- An action on something that doesn't exist (no todo list) counts as "not seen".

After that, only the affected cells need re-running: about 100 F3 checks plus the new re-checks.

(Copied verbatim from the answer given on 2026-11-19, at the user's request; one correction: the partial action is in world224-os-task02 i9, not world227 as first written.)

Per-run table: [analysis/FAILING-RUNS.md](../analysis/FAILING-RUNS.md),
section "APEX: the 'mark all todos completed' invariants". Each affected task below has a note under its list.
