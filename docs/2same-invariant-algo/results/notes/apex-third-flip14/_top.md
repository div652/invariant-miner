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

**Why the check errs (a pipeline problem, not Luna misreading; checked in the F2/F3 job transcripts):** Luna sees the
todo call; in td-02 run 7 it even quotes its output *"Updated todo list: 0 pending, 0 in progress, 4 completed."* But
(1) "all steps are done" has no evidence apart from the todo update, so F2 (which by design does not know the action)
pins the observation at the todo call itself (s29.c1); (2) F3 asks whether the action came **after** the pinned
location, and here it is **at** it. Read literally the answer is "not followed" (Luna's reasoning: *"check if the agent
took the specified action anywhere after the pinned location"*); in the other half of such cells Luna bent the rule
and said "followed". Over the four invariants, the cells pinned at the todo call itself went 5 "followed" and 6 "not followed" (one of those
a passing run that Opus corrected). (3) The re-check is
asymmetric: a passing run's "not followed" gets an Opus re-check (td-02 run 10: Luna "not followed", Opus "followed"),
a failing run's does not, so these errors survive only on failing runs, as importance points. **Fixes to discuss:** F3 treats an action at the pinned location itself as a separate, neutral outcome (the
observation is evidenced only by the action); failing runs' "not followed" get the same Opus re-check as passing runs'; an action on something absent (no todo list) counts as not seen; bookkeeping actions are not proposed as
invariants (or only with a separate observation). Per-run table: [analysis/FAILING-RUNS.md](../analysis/FAILING-RUNS.md),
section "APEX: the 'mark all todos completed' invariants". Each affected task below has a note under its list.
