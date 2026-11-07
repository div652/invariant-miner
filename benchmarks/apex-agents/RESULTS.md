# APEX-Agents: results

## Full run, 2026-11-07 (`runs/apex-full-20261106T213347Z`, branch `bench/apex-agents`)

Setup (CHECKLIST.md has every decision): Archipelago's environment and grader as built (changes 1-7 listed there), DSH
replacing only Archipelago's agent, DSH's tools inside Archipelago's container (`fs-podman`, `sandbox-podman`), toolbelt
on, the paper's system prompt (path sentence extended), 250 steps / 3 h. Agent `gpt-5.6-luna` via CAO, Responses API,
reasoning effort high, summaries on (`models/luna-cao.json`). Judge `gemini-3.8-flash`, reasoning effort low, via CAO
(paper: Gemini 3 Flash, low). One run per task (the paper: 8).

**Pass@1 30.0% (144 / 480), mean criterion score 0.468.** All 480 tasks graded; no grading errors left.

| Job | Tasks | Pass@1 | Mean score |
|---|---|---|---|
| Investment Banking | 160 | 29.4% | 0.364 |
| Law | 160 | 19.4% | 0.463 |
| Management Consulting | 160 | 41.3% | 0.575 |

| Output | Tasks | Pass@1 | Mean score |
|---|---|---|---|
| Answer in the console | 422 | 30.8% | 0.465 |
| make_new_doc | 20 | 20.0% | 0.603 |
| make_new_sheet | 14 | 21.4% | 0.393 |
| make_new_slide_deck | 5 | 40.0% | 0.687 |
| edit_existing_sheet | 16 | 25.0% | 0.327 |
| edit_existing_doc | 2 | 0.0% | 0.603 |
| edit_existing_slide_deck | 1 | 100.0% | 1.000 |

Endings: 373 `final_answer`, 107 a final reply without a tool call (graded like a final answer; CHECKLIST row 8). No run
hit the step limit or the 3 h budget.

Paper (arXiv 2601.14242v3, Table 3), best Pass@1: 24.0% overall (Gemini 3 Flash), by job 27.3% banking, 22.7% consulting,
25.9% law. Not a like-for-like comparison: different model, judge and harness, one run per task instead of eight.

### Caveats

- **FMP plan.** The FMP key used is a limited plan: Kenvue (KVUE) and Kimberly-Clark (KMB), the companies of world 246,
  return "premium" errors; Treasury rates and some symbols work. Tasks needing their live prices could not get them from
  FMP (Edgar SEC worked). The 28 tasks of worlds 244/246 scored 46.4% Pass@1.
- **Infrastructure re-runs (not agent failures).** 9 task runs failed outside the agent and were re-run from scratch in
  fresh containers: 4 setup errors and 1 failed agent start (retried automatically), 4 lost "after" snapshots (podman
  exit 255; re-run after the snapshot retry fix). No agent tool call saw a podman error (20,391 tool results scanned).
- **7 runs held a slot until the 3 h kill** after the agent had finished (fs-podman helper kept DSH alive; answers were
  recorded, grading unaffected). Fixed in 8191a21 (`tests/repro_attach_exit.py`).
- **Machine state.** During the run a VS Code file watcher held the whole per-user inotify budget (1,048,325 of
  1,048,576 watches), and systemd/podman logged 53,534 watch failures; a plausible contributor to podman's exit-255
  errors (unproven). Fixed 2026-11-07 with `files.watcherExclude` in `~/.vscode-server/data/Machine/settings.json`.
- 20 tasks in parallel kept only about 10 agents working at once (the rest waited on podman-heavy setup and snapshots);
  the default is now 12.
