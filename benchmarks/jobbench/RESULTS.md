# JobBench results

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
