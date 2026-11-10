# Harvey LAB results

## Firm-knowledge, all 250 tasks, GPT-5.6 Sol high via CAO, subagents ON, 2026-11-10

Run `runs/hv-fk250-solhigh-subon-20261109T225727Z` (not in git): the run below with DSH's subagent tools turned back on
by a run-local patch (`subagents-on.patch.yml`, with their prompt paragraph), harness main `8fad9af` (no code change
until the resume at `ee176b0`). 20 at a time; started 04:27 IST, stopped by the disk filling at 05:50 IST (47 tasks
done; the 34 it broke parked in `aborted-enospc/` and re-run), resumed 10:51-16:43 IST; graded like the run below,
0 grading errors.

**All-pass 30.0%, criterion pass rate 0.766.** 247 runs `completed`; 3 ended in an infrastructure error and are scored
as they stand: 151 (CAO 429 through all 5 retries, no answer), 152 (a 429, then DSH's subagent registry failed:
"agent ... cannot read inbox state: its projection registration is not active", no answer), 136 (the same registry
failure after 87 steps, no `response.md`). Agent time median 28.0 min, root steps median 53 (subagents off: 8.8 min, 35).

| Paired over tasks (on - off), 95% bootstrap CI, W/T/L | All-pass | Criterion pass rate |
|---|---|---|
| all 250 | 30.0% vs 31.2%: -1.2 points [-6.4, +4.0], 20/207/23 | 0.766 vs 0.764: +0.002 [-0.030, +0.034], 62/133/55 |
| 247 without the 3 error tasks | 30.4% vs 31.6%: -1.2 points [-6.5, +4.0], 20/204/23 | 0.774 vs 0.763: +0.010 [-0.019, +0.040], 62/133/52 |

Subagents on makes no measurable difference to the score with Sol high on Harvey, at about 3x the agent time.

## Firm-knowledge, all 250 tasks, GPT-5.6 Sol high via CAO, subagents off, 2026-11-10

Run `runs/hv-fk250-solhigh-20261109T194222Z` (not in git), harness main `b49f3b6` (core-v6: subagents off for every
benchmark), model `models/sol-high-cao.json` (gpt-5.6-sol, effort high, otherwise luna-cao's shape: reasoning summaries
on); 250 tasks x 1 run, 20 at a time, 01:12-03:24 IST; graded as below (judge gpt-5.6-sol high, helper claude-sonnet-5,
via CAO), 0 grading errors.

**All-pass 31.2%, criterion pass rate 0.764.** All 250 runs ended `completed` (agent time median 527 s, max 1,261 s;
root steps median 35, max 92).

| Tasks | Sol high, subagents off | Luna medium, subagents on (2026-11-06, below) |
|---|---|---|
| all 250 | **31.2%**, 0.764 | 18.8%, 0.555 |
| `splits.json` train / val / test (150 / 50 / 50) | 30.0% / 18.0% / 48.0% | 19.3% / 14.0% / 22.0% |
| AHE split: trainval / test (100 / 70) | 32.0% / 32.9% | 20.0% / 15.7% |

Paired over the 250 tasks: all-pass +12.4 points, 95% CI [+6.8, +18.0], better/equal/worse 43/195/12. Model, effort
and subagents all changed at once, so this is not an estimate of any one of them. Reference outside this repository: the
AHE campaigns' c20 ran Harvey's own harness with Sol on the same 250 tasks (32.4% all-pass), graded by the AHE port of
LAB's grader, not this one.

## Firm-knowledge, all 250 tasks, GPT-5.6 Luna via CAO (c34 endpoint), 2026-11-06

Run `runs/hv-fk250-20261105T204941Z` (not in git), harness commit `c16c99e` (branch bench/harvey): 250 tasks x 1 run,
10 at a time, 02:19-04:28 IST; graded by Harvey's own grader (pinned 4743403) with C0's settings: one judge gpt-5.6-sol
at effort high, helper claude-sonnet-5, via CAO. Setup: benchmarks/harvey/CHECKLIST.md.

| | dsh-bench-harness | C0 (Harvey's harness, AHE campaign 34) |
|---|---|---|
| all 250 tasks | all-pass **18.8%**, criterion pass **0.555** | (no C0 on all 250) |
| c34's 100 tasks (C0: 3 runs each) | all-pass **20.0%**, criterion **0.560** | all-pass **12.3%**, criterion **0.385** |
| other 150 tasks | all-pass 18.0%, criterion 0.552 | - |

Paired over the 100 tasks (ours 1 run vs C0's 3-run mean per task; bootstrap over tasks):
- all-pass: ours 0.200 vs C0 0.123: +0.077, 95% CI [+0.007, +0.147], better/equal/worse 17/75/8
- criterion pass: ours 0.560 vs C0 0.385: +0.174, 95% CI [+0.106, +0.238], better/equal/worse 71/12/17

Run facts: all 250 ended `completed` (no step or time limit hit; root steps median 21, max 52; agent time median 221 s,
max 1,301 s); 49 tasks used subagents; 0 grading errors. One deliverable misplaced: task 193 built `response.md` with
python in bash and saved it in the workspace root, not output/ (graded as missing, as Harvey's grader would).
2 tool results across the run were `response.md` lookups that missed (edit/read relative to the workspace).

Caveats: one run per task on our side (per-task outcomes are noisy); the grader is upstream lab_core at our pin, C0
was graded by the AHE adapter's port of LAB with the same judge, effort and helper (the LAB commits between the two
versions change .docx grading and unreadable-file handling, not .md; but the code paths differ); the harnesses differ
in more than the tools (DSH has subagents, todo lists and context compaction; in c24, 6 of 150 C0 runs ended on
context overflow).

### Tasks where all-pass differs (ours vs C0 mean over 3 runs)

| Task | ours | C0 | ours criterion | C0 criterion |
|---|---|---|---|---|
| firm-knowledge/tasks/072 | 1 | 0.00 | 1.00 | 0.42 |
| firm-knowledge/tasks/104 | 1 | 0.00 | 1.00 | 0.00 |
| firm-knowledge/tasks/137 | 1 | 0.00 | 1.00 | 0.42 |
| firm-knowledge/tasks/173 | 1 | 0.00 | 1.00 | 0.50 |
| firm-knowledge/tasks/198 | 1 | 0.00 | 1.00 | 0.42 |
| firm-knowledge/tasks/199 | 1 | 0.00 | 1.00 | 0.50 |
| firm-knowledge/tasks/210 | 1 | 0.00 | 1.00 | 0.27 |
| firm-knowledge/tasks/003 | 1 | 0.33 | 1.00 | 0.44 |
| firm-knowledge/tasks/056 | 1 | 0.33 | 1.00 | 0.33 |
| firm-knowledge/tasks/111 | 1 | 0.33 | 1.00 | 0.56 |
| firm-knowledge/tasks/192 | 1 | 0.33 | 1.00 | 0.67 |
| firm-knowledge/tasks/201 | 1 | 0.33 | 1.00 | 0.73 |
| firm-knowledge/tasks/206 | 1 | 0.33 | 1.00 | 0.67 |
| firm-knowledge/tasks/032 | 1 | 0.67 | 1.00 | 0.83 |
| firm-knowledge/tasks/034 | 1 | 0.67 | 1.00 | 0.83 |
| firm-knowledge/tasks/131 | 1 | 0.67 | 1.00 | 0.83 |
| firm-knowledge/tasks/221 | 1 | 0.67 | 1.00 | 0.67 |
| firm-knowledge/tasks/091 | 0 | 0.33 | 0.00 | 0.67 |
| firm-knowledge/tasks/105 | 0 | 0.33 | 0.75 | 0.67 |
| firm-knowledge/tasks/113 | 0 | 0.33 | 0.86 | 0.90 |
| firm-knowledge/tasks/161 | 0 | 0.33 | 0.50 | 0.50 |
| firm-knowledge/tasks/098 | 0 | 0.67 | 0.00 | 0.67 |
| firm-knowledge/tasks/185 | 0 | 0.67 | 0.00 | 0.67 |
| firm-knowledge/tasks/061 | 0 | 1.00 | 0.00 | 1.00 |
| firm-knowledge/tasks/093 | 0 | 1.00 | 0.00 | 1.00 |

## c34's 100 tasks, run 2, 2026-11-06 (main 0ef95c2, Luna effort medium as run 1)

Run `runs/hv-c34-100-rep2-20261106T043323Z`: the 100 firm-knowledge tasks with c34 C0 trials (`c34-c0-100.txt`), same
setup and grading as run 1. All 100 completed. Run 2 alone: all-pass **20.0%**, criterion pass **0.542**.
(Run 3 was cancelled by the user: two runs are enough.)

Runs 1 + 2 (mean of 2 per task) vs C0 (mean of 3 per task), paired over the 100 tasks:
- all-pass: ours 0.200 vs C0 0.123: **+0.077, 95% CI [+0.017, +0.138]**, better/equal/worse 21/70/9
- criterion pass: ours 0.551 vs C0 0.385: **+0.165, 95% CI [+0.106, +0.223]**, better/equal/worse 72/11/17
