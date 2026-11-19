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

**Why the check errs:** "all steps are done" has no evidence apart from the todo update, so F2 pins the observation at
that call (or its output) and F3 must judge whether the action comes *after* the same call; Luna answers that
inconsistently, and the too-narrow check did not catch it. **Fixes to discuss:** F2 needs evidence before and apart from
the action; an action on something absent (no todo list) counts as not seen; bookkeeping actions are not proposed as
invariants (or only with a separate observation). Per-run table: [analysis/FAILING-RUNS.md](../analysis/FAILING-RUNS.md),
section "APEX: the 'mark all todos completed' invariants". Each affected task below has a note under its list.
