# Harvey LAB results

## Baseline: firm-knowledge, all 250 tasks, GPT-5.6 Luna high, three runs, 2026-11-10/12

**The reference baseline for Harvey comparisons**: the core harness (subagents off, no optional plugins),
`models/luna-cao.json`, `make_specs.py` defaults (200 steps, 2 h), 20 tasks at a time, graded with `grade.py`'s defaults
(judge gpt-5.6-sol high, helper claude-sonnet-5, via CAO). Run 1 is the run of the next section (main `5f908f7`); runs
2 and 3 repeat it on main `ed7f677` (no harness change for Harvey in between; the specs are identical), one after the
other, each graded before the next started: `runs/hv-fk250-lunahigh-rep2-20261112T122308Z` (17:53-19:43 IST) and
`runs/hv-fk250-lunahigh-rep3-20261112T141312Z` (19:43-21:48 IST), not in git. Per-task scores of all three runs:
[`baselines/luna-high-3runs-20261112.json`](baselines/luna-high-3runs-20261112.json); compare with the three-run mean.

| | Run 1 | Run 2 | Run 3 | **Three-run mean** |
|---|---|---|---|---|
| all-pass | 22.4% | 23.2% | 22.4% | **22.7%** |
| criterion pass rate | 0.651 | 0.675 | 0.657 | **0.661** |
| agent time median, root steps median | 434 s, 32.5 | 408 s, 32 | 419 s, 32 | |

| Tasks | All-pass, three-run mean (runs) | Criterion pass rate, three-run mean (runs) |
|---|---|---|
| all 250 | 22.7% (22.4 / 23.2 / 22.4) | 0.661 (0.651 / 0.675 / 0.657) |
| AHE test (`ahe:test`, 70) | 21.9% (24.3 / 20.0 / 21.4) | 0.638 (0.641 / 0.639 / 0.636) |
| AHE train + val (`ahe:trainval`, 100) | 25.0% (22.0 / 26.0 / 27.0) | 0.675 (0.660 / 0.693 / 0.673) |
| our test (`split:test`, 50) | 26.7% (28.0 / 26.0 / 26.0) | 0.620 (0.620 / 0.615 / 0.624) |

**Pass@3 (all 250 tasks): 32.8%** (82/250): a task counts if it is all-pass in at least one of the three runs.

| Tasks | Pass@1 (three-run mean) | Pass@2 | **Pass@3** | All-pass in all three runs | Tasks passing in 0 / 1 / 2 / 3 runs |
|---|---|---|---|---|---|
| all 250 | 22.7% | 29.1% | **32.8%** (82) | 13.6% (34) | 168 / 28 / 20 / 34 |
| AHE test (70) | 21.9% | 27.1% | 30.0% (21) | 14.3% (10) | 49 / 6 / 5 / 10 |
| AHE train + val (100) | 25.0% | 31.3% | 35.0% (35) | 16.0% (16) | 65 / 11 / 8 / 16 |
| our test (50) | 26.7% | 35.3% | 40.0% (20) | 14.0% (7) | 30 / 7 / 6 / 7 |

Pass@2 is the unbiased estimate from the three runs (mean over tasks of 1 - C(3-c, 2) / C(3, 2), c = passing runs). Of
the 82 tasks Luna high solves at least once, 48 are solved in only one or two of the three runs.

**Flipping tasks, analysed:** of the 80 AHE-train tasks, 14 pass in one or two of the three runs (52 never, 14 always).
Their 42 trajectories are in [`analysis/hv-lunahigh-train80-flip14/`](analysis/hv-lunahigh-train80-flip14/README.md)
(readable traces, criterion x run verdicts), with a per-task failure analysis and the patterns across all 14 in
[`ANALYSIS.md`](analysis/hv-lunahigh-train80-flip14/ANALYSIS.md). In short: precision tasks fail by judgement after
surfacing, and their passing runs mostly pass by never opening the wrong item; recall, superlative and counting tasks
fail on incomplete candidate sets caused by tool limits (grep blind to .docx, capped outputs whose full result the
agent cannot open, timeouts).

All 750 runs ended `completed`; no CAO stall needed a re-run. Run-to-run spread on all 250: 0.5 points all-pass (SD of the
three run means), 0.013 criterion; on the 70- and 100-task subsets the all-pass spread is 2-3 points.

One collection crash, graded by hand: in run 3, task 175's agent finished normally (`output/response.md` written), then
the launcher crashed on `git diff --binary` (exit 128) because the agent had left a 1.2 GB `scratch_index.txt` in the
workspace, so no run.json was written and `grade.py` skipped the task (its first summary covered 249 tasks). The run.json
was written afterwards from the launcher's own collection steps without the binary diff (`workspace_diff_error`
recorded), the task graded alone (`grading-task175/`, 4/6 criteria) and merged into `grading/scores.json`
(`scores-before-task175.*` keep the 249-task version). The launcher fix for this crash exists on branch
invariant-system-prompt (2026-11-11, `workspace_diff_error`) but is not on main.

## Firm-knowledge, all 250 tasks, GPT-5.6 Luna high via CAO, subagents off, 2026-11-11

Run `runs/hv-fk250-lunahigh-20261110T175632Z` (not in git), harness main `5f908f7` (core-v6: subagents off for every
benchmark; = the base of branch `invariant-system-prompt`), model `models/luna-cao.json` (gpt-5.6-luna, effort high,
reasoning summaries on); 250 tasks x 1 run, 20 at a time, 23:26-01:21 IST; graded like the Sol runs (judge
gpt-5.6-sol high, helper claude-sonnet-5, via CAO), 0 grading errors. The Luna-high, subagents-off baseline.

**All-pass 22.4%, criterion pass rate 0.651.** All 250 runs ended `completed` (agent time median 434 s, max 2,106 s;
root steps median 32.5, max 84; no subagent sessions).

| Tasks | Luna high, off (this run) | Sol high, off | Luna medium (11-05, subagents on) |
|---|---|---|---|
| all 250 | 22.4% / 0.651 | 31.2% / 0.764 | 18.8% / 0.555 |
| AHE test (`ahe:test`, 70) | 24.3% / 0.641 | 32.9% / 0.763 | - |
| AHE train+val (`ahe:trainval`, 100) | 22.0% / 0.660 | 32.0% / 0.758 | - |
| our test (`split:test`, 50) | 28.0% / 0.620 | 48.0% / 0.823 | - |

Paired over the 250 tasks (bootstrap over tasks):
- vs Sol high, off (same harness, other model): all-pass -0.088, 95% CI [-0.144, -0.036], better/equal/worse 14/200/36;
  criterion -0.113 [-0.151, -0.076].
- vs Luna medium of 11-05 (effort, harness and subagent setting all differ): all-pass +0.036 [-0.004, +0.080],
  19/221/10; criterion +0.096 [+0.060, +0.133].

## Firm-knowledge, all 250 tasks, GPT-5.6 Sol high via CAO, subagents ON, 2026-11-10

Run `runs/hv-fk250-solhigh-subon-20261109T225727Z` (not in git): the run below with DSH's subagent tools turned back on
by a run-local patch (`subagents-on.patch.yml`, with their prompt paragraph), harness main `8fad9af` (no code change
until the resume at `ee176b0`). 20 at a time; started 04:27 IST, stopped by the disk filling at 05:50 IST (47 tasks
done; the 34 it broke parked in `aborted-enospc/` and re-run), resumed 10:51-16:43 IST; graded like the run below,
0 grading errors.

**All-pass 30.4%, criterion pass rate 0.774** (after re-running 3 tasks, below). All 250 runs `completed`. In the
first pass 3 tasks ended in an error (30.0% / 0.766 with them scored as they stood): 136, 151 and 152, where the main
agent ran out of its 5 retries on GitHub Copilot 429s at 13:41-13:42 IST (Sol throttled: ~310-330 Sol sessions alive
at once with subagents on, against 28 with them off, plus an interim grading's judge calls at 13:40); in 136 and 152
the teardown then crashed in DSH's subagent settlement watcher (fixed by DSH patch 0009). The three were re-run on
the patched build at 17:19-17:34 IST (no 429s; first attempts kept in `superseded-429/`), graded with the same judge
(`grading-rerun3/`) and merged into `grading/scores.json` (`scores-before-rerun3.*` keep the first pass): 136 33/45,
151 2/3, 152 19/19 all-pass. Agent time median 28.0 min, root steps median 53 (subagents off: 8.8 min, 35).

| Paired over the 250 tasks (on - off), 95% bootstrap CI, W/T/L | All-pass | Criterion pass rate |
|---|---|---|
| with the 3 re-runs | 30.4% vs 31.2%: -0.8 points [-6.0, +4.4], 21/206/23 | 0.774 vs 0.764: +0.010 [-0.020, +0.040], 63/134/53 |
| first pass (3 error runs scored as they stood) | 30.0% vs 31.2%: -1.2 points [-6.4, +4.0], 20/207/23 | 0.766 vs 0.764: +0.002 [-0.030, +0.034], 62/133/55 |

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
