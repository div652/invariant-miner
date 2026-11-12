# JobBench results

Rubric sets: runs are graded on JobBench's **original** rubrics (`grade.sh RUN`, results in `RUN/grading/`) and, where a
table says so, on agentic-evolution's **task-instruction-aligned v1** rubrics (`grade.sh --rubrics v1 RUN`, results in
`RUN/grading-v1/`; the v1 files are in this repository, `rubrics/`). What differs between them: CHECKLIST.md, row 9
"Rubric sets".

## Baseline: all 65 tasks, GPT-5.6 Luna high, two runs, 2026-11-12

**The reference baseline for JobBench comparisons**: the core harness (subagents off, no optional plugins), two full
runs of all 65 tasks, graded on both rubric sets. Per-task scores (both runs, both rubric sets) are in
[`baselines/luna-high-2runs-20261112.json`](baselines/luna-high-2runs-20261112.json); compare a new run with the
two-run mean per task, not with one run.

Setup: `models/luna-cao.json` (gpt-5.6-luna via CAO, effort high, reasoning summaries on), 2 h per task, network pasta,
web_search via the Exa relay; graded by grok-4.6 high via the CAO shim (`grade.sh`, judge_parallel 2x9). Runs
`runs/jb-all65-base-r1-20261111T191736Z` and `-r2-` (in the inv-new-tools worktree, not in git) were the baseline arm of the agent-tools experiment
on branch `inv-new-tools` (`62328bf`, docs/agent-tools/RESULTS.md there): that branch's additions are inactive without
the `agent_tools` spec key, so these runs are main's configuration. Run 2026-11-12 00:48-06:13 IST, 40 tasks at a time
(interleaved with the experiment's other arms). The Exa credits ran out at 00:57 IST: the 15 (r1) and 16 (r2) tasks
whose web_search hit the credit error were discarded and re-run with a new key; no kept run has the error. All 130 runs
ended `completed`; 65/65 graded in each run on both rubric sets.

| | Run 1 | Run 2 | **Two-run mean** |
|---|---|---|---|
| original rubrics, macro (pooled) | 0.291 (0.278) | 0.363 (0.352) | **0.327** (0.315) |
| v1 rubrics, macro (pooled) | 0.407 (0.407) | 0.423 (0.422) | **0.415** (0.414) |
| agent time median, root steps median | 467 s, 33 | 515 s, 32 | |

- **Run-to-run noise**: run 2 - run 1 = +0.073, 95% CI [+0.039, +0.106] (W/T/L 33/21/11) on the original rubrics,
  +0.016 [-0.020, +0.052] on v1. One run of the same setup can sit 0.07 from another: compare against the two-run mean.
- **Against the 11-10 Luna-high subagents-off run** (0.313 / 0.404, section below): two-run mean - that run = +0.014
  [-0.011, +0.040] original, +0.011 [-0.029, +0.049] v1 (paired over the 65 tasks): the same level.

<details><summary>Per task (points/max per run, two-run mean of score/max)</summary>

| Task | orig r1 | orig r2 | orig mean | v1 r1 | v1 r2 | v1 mean |
|---|---|---|---|---|---|---|
| biostatisticians/task1 | 38/72 | 44/72 | 0.569 | 45/72 | 37/72 | 0.569 |
| biostatisticians/task2 | 0/58 | 14/58 | 0.121 | 5/58 | 5/58 | 0.086 |
| bookkeeping_accounting_and_auditing_clerks/task1 | 0/88 | 20/88 | 0.114 | 19/88 | 29/88 | 0.273 |
| bookkeeping_accounting_and_auditing_clerks/task2 | 24/52 | 6/52 | 0.288 | 12/52 | 25/52 | 0.356 |
| civil_engineers/task1 | 34/50 | 34/50 | 0.680 | 8/50 | 16/50 | 0.240 |
| civil_engineers/task2 | 26/68 | 48/68 | 0.544 | 40/68 | 42/68 | 0.603 |
| civil_engineers/task3 | 14/76 | 24/76 | 0.250 | 28/76 | 48/76 | 0.500 |
| computer_and_information_research_scientists/task1 | 18/66 | 32/66 | 0.379 | 12/66 | 32/66 | 0.333 |
| computer_and_information_research_scientists/task2 | 6/82 | 24/82 | 0.183 | 36/82 | 28/82 | 0.390 |
| computer_and_information_systems_managers/task1 | 12/56 | 30/56 | 0.375 | 28/56 | 36/56 | 0.571 |
| computer_and_information_systems_managers/task2 | 10/62 | 8/62 | 0.145 | 0/62 | 0/62 | 0.000 |
| computer_user_support_specialists/task1 | 28/56 | 28/56 | 0.500 | 41/56 | 41/56 | 0.732 |
| computer_user_support_specialists/task2 | 14/82 | 8/82 | 0.134 | 24/82 | 32/82 | 0.342 |
| court_clerks/task1 | 24/76 | 22/76 | 0.303 | 18/76 | 16/76 | 0.224 |
| customer_service_representatives/task1 | 6/76 | 6/76 | 0.079 | 34/76 | 34/76 | 0.447 |
| data_entry_keyers/task1 | 32/92 | 60/92 | 0.500 | 52/92 | 58/92 | 0.598 |
| data_entry_keyers/task2 | 44/60 | 44/60 | 0.733 | 40/60 | 20/60 | 0.500 |
| financial_managers_branch_or_department/task1 | 30/90 | 30/90 | 0.333 | 40/90 | 54/90 | 0.522 |
| financial_managers_branch_or_department/task2 | 16/66 | 0/66 | 0.121 | 31/66 | 31/66 | 0.470 |
| human_resources_specialists/task1 | 26/64 | 26/64 | 0.406 | 23/64 | 23/64 | 0.359 |
| lawyers/task1 | 6/48 | 12/48 | 0.188 | 30/48 | 26/48 | 0.583 |
| licensing_examiners_and_inspectors/task1 | 18/72 | 28/72 | 0.319 | 64/72 | 66/72 | 0.903 |
| management_analysts/task1 | 22/88 | 22/88 | 0.250 | 52/88 | 38/88 | 0.511 |
| management_analysts/task2 | 18/80 | 18/80 | 0.225 | 14/80 | 28/80 | 0.263 |
| management_analysts/task3 | 6/72 | 12/72 | 0.125 | 49/72 | 42/72 | 0.632 |
| mechanical_engineering_technicians/task1 | 24/78 | 24/78 | 0.308 | 50/78 | 50/78 | 0.641 |
| mechanical_engineering_technicians/task2 | 0/70 | 0/70 | 0.000 | 30/70 | 24/70 | 0.386 |
| mechanical_engineering_technicians/task3 | 26/58 | 32/58 | 0.500 | 32/58 | 30/58 | 0.534 |
| mechanical_engineers/task1 | 6/66 | 6/66 | 0.091 | 24/66 | 18/66 | 0.318 |
| medical_and_health_services_managers/task1 | 16/74 | 26/74 | 0.284 | 44/74 | 8/74 | 0.351 |
| medical_and_health_services_managers/task2 | 6/86 | 16/86 | 0.128 | 26/86 | 26/86 | 0.302 |
| medical_secretaries/task1 | 12/78 | 6/78 | 0.115 | 28/78 | 34/78 | 0.397 |
| online_merchants/task1 | 28/58 | 38/58 | 0.569 | 38/58 | 26/58 | 0.552 |
| online_merchants/task2 | 22/54 | 30/54 | 0.481 | 22/54 | 22/54 | 0.407 |
| personal_financial_advisors/task1 | 6/78 | 22/78 | 0.179 | 20/78 | 8/78 | 0.179 |
| petroleum_engineers/task1 | 16/50 | 16/50 | 0.320 | 27/50 | 31/50 | 0.580 |
| police_fire_and_ambulance_dispatchers/task1 | 34/94 | 54/94 | 0.468 | 62/94 | 60/94 | 0.649 |
| producers/task1 | 56/72 | 48/72 | 0.722 | 40/72 | 44/72 | 0.583 |
| purchasing_agents_except_wholesale_retail_and_farm_products/task1 | 12/88 | 18/88 | 0.171 | 18/88 | 24/88 | 0.239 |
| purchasing_agents_except_wholesale_retail_and_farm_products/task2 | 8/78 | 24/78 | 0.205 | 44/78 | 58/78 | 0.654 |
| purchasing_agents_except_wholesale_retail_and_farm_products/task3 | 16/96 | 16/96 | 0.167 | 18/96 | 24/96 | 0.219 |
| reporters_and_correspondents/task1 | 20/60 | 36/60 | 0.467 | 24/60 | 14/60 | 0.317 |
| sales_agents_securities_and_commodities/task1 | 30/74 | 30/74 | 0.405 | 30/74 | 10/74 | 0.270 |
| sales_representatives_wholesale_and_manufacturing_technical_and_scientific_products/task1 | 10/106 | 10/106 | 0.094 | 52/106 | 42/106 | 0.443 |
| sales_representatives_wholesale_and_manufacturing_technical_and_scientific_products/task2 | 18/80 | 30/80 | 0.300 | 12/80 | 22/80 | 0.212 |
| secretaries_and_administrative_assistants_except_legal_medical_and_executive/task1 | 22/60 | 40/60 | 0.517 | 8/60 | 34/60 | 0.350 |
| secretaries_and_administrative_assistants_except_legal_medical_and_executive/task2 | 18/48 | 6/48 | 0.250 | 26/48 | 16/48 | 0.438 |
| social_science_research_assistants/task1 | 48/66 | 48/66 | 0.727 | 42/66 | 52/66 | 0.712 |
| social_science_research_assistants/task2 | 38/68 | 36/68 | 0.544 | 26/68 | 22/68 | 0.353 |
| social_science_research_assistants/task3 | 32/50 | 32/50 | 0.640 | 33/50 | 33/50 | 0.660 |
| sociology_teachers_postsecondary/task1 | 18/68 | 38/68 | 0.412 | 16/68 | 16/68 | 0.235 |
| sociology_teachers_postsecondary/task2 | 30/66 | 38/66 | 0.515 | 40/66 | 44/66 | 0.636 |
| sociology_teachers_postsecondary/task3 | 14/72 | 30/72 | 0.306 | 40/72 | 40/72 | 0.556 |
| statisticians/task1 | 16/116 | 10/116 | 0.112 | 34/116 | 24/116 | 0.250 |
| statisticians/task2 | 16/66 | 30/66 | 0.348 | 28/66 | 32/66 | 0.455 |
| statisticians/task3 | 22/54 | 22/54 | 0.407 | 23/54 | 22/54 | 0.417 |
| supply_chain_managers/task1 | 6/64 | 12/64 | 0.141 | 16/64 | 22/64 | 0.297 |
| supply_chain_managers/task2 | 0/40 | 6/40 | 0.075 | 6/40 | 12/40 | 0.225 |
| technical_writers/task1 | 34/66 | 48/66 | 0.621 | 14/66 | 26/66 | 0.303 |
| technical_writers/task2 | 16/60 | 22/60 | 0.317 | 0/60 | 0/60 | 0.000 |
| technical_writers/task3 | 24/84 | 24/84 | 0.286 | 29/84 | 48/84 | 0.458 |
| training_and_development_specialists/task1 | 6/54 | 6/54 | 0.111 | 12/54 | 12/54 | 0.222 |
| training_and_development_specialists/task2 | 18/44 | 18/44 | 0.409 | 12/44 | 20/44 | 0.364 |
| training_and_development_specialists/task3 | 22/54 | 32/54 | 0.500 | 28/54 | 20/54 | 0.444 |
| web_administrators/task1 | 12/50 | 6/50 | 0.180 | 14/50 | 20/50 | 0.340 |

</details>

## All 65 tasks, Qwen3.8-27B (local vLLM), subagents on, 2 h limit, 2026-11-09/11

Run `runs/jb-all65-qwen38-xhigh-subon-2h-p5-20261109T181320Z` (not in git): `models/qwen38-vllm.json` (Qwen3.8-27B
FP8 on one A100 80GB, thinking on at the model's default effort), DSH's subagent tools on (run-local patch), time
limit 2 h (the default is 1 h), 5 tasks at a time (10 thrashed vLLM's KV cache). Started 23:43 IST 11-09; the disk
filled at 05:50 IST 11-10 (15 tasks done; the 14 it broke and 36 never started re-run from 10:51), agents done 04:40
IST 11-11, graded with the same grade.sh judge on the original rubrics.

**Macro 0.360, pooled 0.349.** 25 runs completed, 40 hit the 2 h limit (16 of them with no deliverable, scored 0).
Agent time median 120 min (the limit), 113 h in total; ~94% of it model generation (median ~32 s per call on the
shared GPU, vs ~4 s for Luna through CAO). Qwen never used a subagent tool.

| Paired over the 65 tasks, 95% bootstrap CI, W/T/L | Mean score |
|---|---|
| Qwen - Luna high, subagents on (0.338) | +0.022 [-0.042, +0.084], 31/8/26 |
| Qwen - Luna high, subagents off (0.313) | +0.047 [-0.026, +0.120], 34/7/24 |
| completed in time (25 tasks) | Qwen 0.546 vs Luna on 0.421 / off 0.373 |
| hit the 2 h limit (40 tasks) | Qwen 0.243 vs Luna on 0.286 / off 0.275 |

Equal to Luna high overall (both CIs span 0); better when it finishes, worse when the time limit cuts it off.

## Model swap probe on 2 tasks: Claude Opus 5.5 max and Gemini 4 Argon high, 2026-11-10

Same harness as the Luna-high subagents-off all-65 run below (core, subagents off, 2 h limit, original rubrics, the
same grade.sh judge); only the model changes. Tasks: biostatisticians/task1 and
computer_and_information_research_scientists/task1. Two tasks: a probe, not an estimate.

| Model (run) | biostatisticians/task1 | computer_and_information_research_scientists/task1 | Mean | Agent time |
|---|---|---|---|---|
| Claude Opus 5.5, effort max (`runs/jb-2tasks-opus55-max-20261110T111413Z`) | **0.861** (62/72) | 0.394 (26/66) | **0.628** | 64 / 93 min |
| GPT-5.6 Luna high, subagents off (run below) | 0.528 | 0.394 | 0.461 | ~7 min |
| GPT-5.6 Luna high, subagents on (run below) | 0.611 | 0.182 | 0.396 | ~7 min |
| Gemini 4 Argon, effort high (`runs/jb-2tasks-gemini-argon-high-20261110T100447Z`) | 0.278 | 0 | 0.139 | 30 / 10 min |

Opus (`models/opus55-max-cao.json`): both runs completed; 2 and 3 CAO mid-stream `api_error`s retried (the first
attempt, kept as `...-FAILED-cao-stream-error`, ended on the first such error before `PI_AI_ERROR` was made
retryable). Argon (`models/gemini-argon-high-cao.json`) is not a valid measure: one run ended when CAO's stream closed
six times without a finish reason at ~177K tokens, the other when one response used the whole 65,536-token output
cap with no visible text (no output-cap regeneration was configured).

## All 65 tasks, GPT-5.6 Luna high via CAO, subagents off vs on, 2026-11-10

Runs `runs/jb-all65-lunahigh-suboff-20261109T215439Z` and `runs/jb-all65-lunahigh-subon-20261109T222237Z` (not in
git), harness main `b49f3b6` (subagents off in core; the "on" run re-enables DSH's delegation tools and their prompt
paragraph with a run-local patch). Model `models/luna-cao.json` (gpt-5.6-luna, effort high, reasoning summaries on),
20 tasks at a time, 2 h per task, one run per task; graded by JobBench's judge (grok-4.6 high via the CAO shim,
original rubrics), all 65 graded in both.

| | subagents off | subagents on |
|---|---|---|
| mean score/max (macro, 65 tasks) | **0.313** | **0.338** |
| pooled | 0.300 | 0.332 |
| endings | 65 completed | 65 completed |
| agent time per task, median | 380 s | 404 s |
| tasks that delegated | - | 40 (79 subagent sessions) |
| task-instruction-aligned v1 rubrics, macro (pooled) | **0.404** (0.401) | **0.419** (0.412) |

Paired over the 65 tasks: on - off = +0.025, 95% CI [-0.007, +0.056], better/equal/worse 28/16/21: no clear effect.
The difference is the same where the agent delegated (40 tasks: 0.322 vs 0.297) and where it did not (25 tasks: 0.364
vs 0.339), so it looks like run-to-run noise (per-task SD ~0.13-0.15), not delegation. On APEX-Agents the same switch
cost about 5 points, all on the tasks where the agent delegated (benchmarks/apex-agents/RESULTS.md).

v1 rubrics (graded 2026-11-10, `grading-v1/`): the "on" run scores 0.419 vs 0.414 for the 11-06 all-65 run (older
core, subagents on by default): paired +0.004, 95% CI [-0.034, +0.044], 26/13/26. Original rubrics 0.338 vs 0.347.
On v1, on - off = +0.015, 95% CI [-0.030, +0.060], better/equal/worse 23/19/23: again no clear effect.

Failure analysis of the "on" run (original rubrics, every task and failed rubric item):
`benchmarks/jobbench/analysis/jb-all65-lunahigh-subon-20261109T222237Z/REPORT.md`. Model mistakes 79% of lost points
(wrong analysis 37%, facts it had but left out 35%, missing professional checks 22%, ignored instructions 6%),
insufficient information 8.6%, grading problems 6.2% (pooled 0.373 if those had passed), logging 2.5%, retrieval 2.5%.

## train-20, Luna via CAO, 2026-11-05 (core-v0)

Run `runs/jb-train20-20261105T170005Z` (not in git): 20 tasks, 10 at a time, GPT-5.6 Luna (reasoning high; `models/luna-proxy-high.json`) via the
model_serve proxy on CAO, graded by grok-4.6 high through the CAO judge shim, original rubrics. Reference: the same
tasks, model, judge and rubrics on agentic-evolution's own runner (`train20-luna-cao-20261105T074611Z`). One run each,
so per-task differences are mostly run-to-run noise (SD ~0.13-0.15 per task).

| | dsh-bench-harness | reference harness |
|---|---|---|
| mean score/max | **0.325** | **0.307** |
| difference | +0.018, 95% CI [-0.028, +0.067], W/T/L 7/6/7 | |

| Task | dsh-bench | reference |
|---|---|---|
| biostatisticians/task1 | 36/72 0.500 | 38/72 0.528 |
| bookkeeping_accounting_and_auditing_clerks/task1 | 8/88 0.091 | 0/88 0.000 |
| civil_engineers/task1 | 22/50 0.440 | 22/50 0.440 |
| computer_and_information_systems_managers/task1 | 18/56 0.321 | 16/56 0.286 |
| computer_user_support_specialists/task2 | 14/82 0.171 | 16/82 0.195 |
| customer_service_representatives/task1 | 6/76 0.079 | 16/76 0.211 |
| financial_managers_branch_or_department/task1 | 40/90 0.444 | 32/90 0.356 |
| human_resources_specialists/task1 | 26/64 0.406 | 26/64 0.406 |
| management_analysts/task2 | 18/80 0.225 | 18/80 0.225 |
| mechanical_engineering_technicians/task3 | 26/58 0.448 | 14/58 0.241 |
| online_merchants/task2 | 24/54 0.444 | 30/54 0.556 |
| petroleum_engineers/task1 | 20/50 0.400 | 16/50 0.320 |
| purchasing_agents_except_wholesale_retail_and_farm_products/task1 | 28/88 0.318 | 6/88 0.068 |
| sales_agents_securities_and_commodities/task1 | 20/74 0.270 | 26/74 0.351 |
| secretaries_and_administrative_assistants_except_legal_medical_and_executive/task2 | 22/48 0.458 | 28/48 0.583 |
| social_science_research_assistants/task2 | 38/68 0.559 | 24/68 0.353 |
| supply_chain_managers/task2 | 0/40 0.000 | 0/40 0.000 |
| technical_writers/task2 | 16/60 0.267 | 22/60 0.367 |
| training_and_development_specialists/task2 | 18/44 0.409 | 18/44 0.409 |
| web_administrators/task1 | 12/50 0.240 | 12/50 0.240 |

Run notes: all 20 agents completed (about 23 min wall clock at 10 parallel). One task's outputs were first collected
wrongly by a launcher bug (U+2028 in the session log), fixed in c54bbd9 and re-collected with `--collect-only`; that
task was graded separately (`grading-financial1/`).

## train-20, Luna via CAO with the harness-wide c34 endpoint, 2026-11-06 (main 0ef95c2)

Run `runs/jb-train20-c34ep-20261106T043323Z`: same tasks, judge (grok-4.6 high via the CAO shim) and rubrics as above;
model `models/luna-cao.json` (CAO direct, reasoning summaries on, effort medium, 128K output) instead of the parity
run's proxy at effort high with a 32K output cap.

| | c34 endpoint (effort medium) | parity run (effort high) | reference harness |
|---|---|---|---|
| mean score/max | **0.238** | 0.325 | 0.307 |

Paired with the parity run: -0.087, 95% CI [-0.167, -0.010], better/equal/worse 7/2/11. The agents did much less work:
root steps median 15.5 vs 40, bash calls 208 vs 573, web_search + web_fetch 37 vs 139, 2-5 min per task vs about 6-15;
every task still produced its deliverables. The drop is the endpoint setting (reasoning effort medium vs high), not
the harness: harness and tasks are the same as the parity run.

## All 65 tasks, Luna effort high via CAO (c34 endpoint shape), 2026-11-06 (main 33db37e)

Run `runs/jb-all65-lunahigh-20261106T051911Z`: all 65 tasks of `dataset/main`, 10 at a time, `models/luna-cao.json` at
effort high; judge grok-4.6 high via the CAO shim. Two tasks (civil_engineers/task1, secretaries.../task1) hit a CAO
stall ("Upstream stream was inactive for 300000ms", turn ended in error, no deliverables) and were re-run once (first
attempts kept as `tasks-failed-*-attempt1-cao-stall`); both completed on the re-run.

| Rubrics | macro | pooled | tasks scoring 0 |
|---|---|---|---|
| original | **0.347** | 0.335 | 4 |
| task-instruction-aligned v1 | **0.414** | 0.406 | 2 |

Against the reference harness's all-65 run on the same model, endpoint (CAO), judge and v1 rubrics
(`all65-luna-cao-v1rubrics-20261105T090945Z`, macro 0.388; agentic-evolution's own non-refined Luna v1 run: 0.393),
paired over the 65 tasks: **+0.026, 95% CI [-0.020, +0.073]**, better/equal/worse 28/12/25. Equal within noise. (The
reference run used effort high through the model_serve proxy with a 32K output cap; ours effort high, CAO direct,
128K output.)
