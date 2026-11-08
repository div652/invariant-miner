# APEX-Agents 1.1: results

## Full run, 2026-11-08 (`runs/apex11-full-lunamax-20261107T193631Z`, branch `bench/apex-agents` 9d7fa85)

Setup (CHECKLIST.md has every decision): Mercor's 1.1 world and verifier images unmodified, DSH replacing only
Mercor's agent, DSH's tools inside the world as run_shell's user, all 74 world tools on every step, Mercor's limits
(100 steps, 3 h, 200 lines / 32,768 characters, 60 s per tool call), Mercor's 1.1 system prompt with `code_exec` ->
`run_shell` and the /filesystem path sentence. Agent `gpt-5.6-luna` via CAO, Responses API, reasoning effort **max**,
summaries on (`models/luna-max-cao.json`). Judge `gemini-3.8-flash` via CAO, reasoning effort high, Mercor's judge
prompt and temperature 0.1 (Mercor: deepseek-v4-flash-0731). One run per task. 12 tasks in parallel; 01:06-09:01 IST.

**Pass@1 34.2% (82 / 240), mean score 0.490; criteria met 460 / 952.** All 240 tasks graded; no infrastructure
errors, no grading errors, no retries.

| Job | Tasks | Pass@1 | Mean score |
|---|---|---|---|
| Investment Banking | 80 | 36.3% | 0.420 |
| Law | 80 | 40.0% | 0.604 |
| Management Consulting | 80 | 26.3% | 0.446 |

| Output | Tasks | Pass@1 | Mean score |
|---|---|---|---|
| Answer in the console | 206 | 32.5% | 0.473 |
| make_new_doc | 9 | 77.8% | 0.825 |
| edit_existing_sheet | 12 | 50.0% | 0.592 |
| make_new_sheet | 9 | 22.2% | 0.319 |
| make_new_slide_deck | 3 | 0.0% | 0.644 |
| edit_existing_doc | 1 | 0.0% | 0.857 |

Runs: 237 ended with a reply, 3 at the 100-step limit (graded: scores 0.2, 0.1, 0.0); none hit 3 h. Main agent steps:
median 22, p90 49; 105 runs used subagents. Agent time: median 15.8 min, p90 38 min, max 99 min.

Tools: 5,419 calls to world apps, 4,109 to DSH's own tools (bash 1,635; glob 476; read 426; todo_write 440). The most
used world tools: sheets read_tab 1,407, pdf search_pdf 776, sheets list_tabs 710, docs read_document_content 543,
pdf read_pdf_pages 512. 699 results were cut by the output cap. 90 calls in 47 runs hit the 60 s limit: 53 of them the
world's PDF tools (read_pdf_pages 30, search_pdf 23) on large PDFs, also 9 bash, 6+5 docs reads, and 4 of DSH's
subagent calls (the per-call limit applies to every tool, DSH's own included).

Context, not like-for-like: Mercor's leaderboard for 1.1 (blog, September 2026) is led by Claude Fable 5.1 at 68.6%
Pass@1 with their own agent and judge; our judge differs (gemini-3.8-flash high vs deepseek-v4-flash) and DSH's tools
are added. Version 1 of this harness on APEX-Agents 1.0 (480 tasks, Luna high, a different judge) scored 30.0%.

### Other runs

- **Luna effort high** (`runs/apex11-full-20261107T180006Z`, `models/luna-cao.json`): stopped by the user after 43
  graded tasks to switch to max (`STOPPED.txt`). On those same 43 tasks: high 20/43, max 20/43 all criteria met.
- An invalid first launch of the max run (the model file given as a relative path, which the launcher resolved
  against each task's directory: DSH never ran, no model calls) was discarded; only its log is kept
  (`runs/INVALID-relative-model-path-...log`). Fixed in 9d7fa85: absolute model path, a launcher failure is an
  infrastructure error, and run_all stops starting tasks after 6 infrastructure failures in a row.
- Smoke (`runs/apex11-smoke3-20261107T161504Z`, Luna high): 3/3. Gold check (`runs/apex11-gold-*`): 6/6 tasks, 32/32
  criteria.

### Judge check: the same runs regraded by claude-haiku-5-5 (2026-11-09, `runs/apex11-regrade-haiku-20261108T190811Z`)

Mercor's leaderboard reports GPT-5.6 Luna (max) at Pass@1 43.0% (±5.4), mean 57.8% (±4.9), with their own agent and
judge (deepseek-v4-flash, not on CAO). To see whether our judge explains the gap, the 206 console-answer runs of the
full run were regraded, unchanged, by claude-haiku-5-5 (CAO; effort high requested, Mercor's temperature 0.1 and judge
prompt): the CAO model closest to deepseek-v4-flash on Mercor's own leaderboard (as agents: 56.1% vs 55.3% Pass@1).

| Tasks | Pass@1 Gemini 3.8 Flash | Pass@1 Haiku 5.5 | Mean Gemini | Mean Haiku |
|---|---|---|---|---|
| 206 console-answer tasks | 32.5% | 33.0% | 0.473 | 0.484 |
| 199 with final-answer-only criteria | 32.2% | 32.7% | 0.467 | 0.474 |

Criteria: 768 graded by both, 93.8% the same verdict (Cohen's kappa 0.87); tasks: 61 pass under both, 6 only under
Gemini, 7 only under Haiku. The judge does not explain the gap.
