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
