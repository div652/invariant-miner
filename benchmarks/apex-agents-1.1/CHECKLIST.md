# APEX-Agents 1.1: checklist answers

Benchmark: **APEX-Agents 1.1.1** (Mercor, September 2026; blog "Introducing APEX-Agents 1.1"), from Harbor Hub
`mercor/apex-agents-1-1@1.1.1`: 240 tasks (80 investment banking, 80 law, 80 management consulting), 31 worlds, 952
rubric criteria, gold outputs for every task; Mercor's own images by digest (31 world images, 1 verifier image).
`tasks.sha256` fingerprints the 240 task packages we analysed (setup.sh checks every download against it).

Version 1 of this work (APEX-Agents 1.0, 480 tasks, Archipelago `f8e41cb`) is `benchmarks/apex-agents/`, tag
`apex-agents-v1`; it stays runnable. This directory is version 2.

Status (2026-11-07): **built and tested.** Core additions (attach as a user with a umask, `plugins/tool-limits`) with
tests; plumbing 20/20 (scripted model, one real task); gold check 6/6 tasks, 32/32 criteria (one task per output type,
the experts' outputs through the whole grading path); smoke with Luna (`smoke-3.txt`: one task per job, file and console
outputs) 3/3 tasks with every criterion met, no infrastructure or grading errors. Full run (Luna max, 2026-11-08): Pass@1 34.2% (82/240), mean 0.490, no infrastructure or grading errors: RESULTS.md.

## What changed from 1.0 (summary of the 2026-11-07 analysis)

- Tasks: 239 of the 240 are 1.0 tasks under new ids (matched by task name), 1 is new (`World420_AM_02`); 241 1.0 tasks
  were dropped, including both banking worlds with internet apps (244, 246: Edgar SEC, FMP). Of the 239: prompts 80
  unchanged / 27 small edits / 48 edited / 84 rewritten or new; rubrics 77 unchanged / 27 reworded / 135 changed; only
  41 tasks have prompt, rubric and output type all unchanged. Input files unchanged (60 of 63; 3 lost only a
  `.DS_Store`); gold files 23 unchanged, 11 changed. Criteria now carry the grading target (`expected_file_type`),
  dependencies (ordering only) and negative criteria (switched off in Mercor's grader).
- Worlds: 5,162 of 5,182 files byte-identical; only mailboxes changed: 19 banking and consulting worlds gained 13 to 54
  emails each (617 in all), the conventions and context that 1.1 moved out of prompts into communications.
- Mercor's agent: no toolbelt (all 74 tools on every call), 100 steps, 3 h, tool output cut at 200 lines / 32,768
  characters, 60 s per tool call, the run ends at the first reply without a tool call; a new system prompt
  (communications, no scattergunning, no internet). Code execution is Stirrup's `run_shell` (plus `read_image_file`)
  instead of `code_exec`, fenced by Linux users instead of an LD_PRELOAD shim.
- Grading: judge `deepseek-v4-flash-0731` (Vercel AI Gateway), temperature 0.1, with a GEPA-tuned judge system prompt
  that includes a scattergunning guard (more than one value for the asked quantity fails the criterion). Mercor's 1.1
  grader image runs an older internal Archipelago grader than our v1 pin.
- Delivery: Harbor 0.20.0. Per task three containers: the world (gateway on :8000, seeded from the world image), the
  agent's container (Python only, no world files; it reaches the world over the network), the verifier.

## Decisions (user, 2026-11-07)

| # | Topic | Decision | Why |
|---|---|---|---|
| 1 | Environment | Mercor's 1.1 images, unmodified: the world image of each task (digest in its compose file) and the verifier image. Nothing rebuilt. | Most faithful: their apps, code execution, seeding, snapshots and grader as they ship them. |
| 2 | Runtime | Our launcher (option A), not Harbor. We do Harbor's steps ourselves ("How a task runs"). | DSH's own tools must run where the files are, inside the world container. In Harbor the agent sits in a separate container with no world files. |
| 3 | Tools | All 74 world tools offered on every step (no toolbelt), plus DSH's own tools (bash, read, write, edit, glob, grep, read_image, subagents, todo...; web off). | 1.1's harness has no toolbelt. DSH's tools as in v1. |
| 4 | Limits | Mercor's: 100 steps, 3 h, every tool result cut at 200 lines / 32,768 characters, 60 s per tool call (`tool_limits`, for DSH's tools too); no `final_answer` tool: the run ends at a reply without a tool call. | Their leaderboard settings. DSH counts steps per agent session (the main agent and each subagent), as in v1. |
| 5 | System prompt | Mercor's 1.1 prompt with two changes: `code_exec` -> `run_shell` (pitfall 1), and the path sentence names DSH's own tools ("For every tool except the run_shell, bash, read, write, edit, read_image, glob and grep tools ... /. For those tools ... /filesystem/"). | The world apps see the files at `/`; inside the container (DSH's tools, run_shell) they are at `/filesystem/`. Word for word, the prompt would send DSH's file tools to `/`. |
| 6 | DSH's own tools | Run as run_shell's user: `svc_stirrup_code_execution` with its groups, umask 0002 and run_shell's environment (`/opt/agent-task-venv` Python, PATH, HOME, NODE_PATH). | Exactly run_shell's access: the world's files yes; the apps' raw data (`/.apps_data`), the world seed, app code and snapshots no; files it makes are editable by the apps (group `workspace`, 664). As root they would see and change everything. |
| 7 | Judge | `gemini-3.8-flash` via CAO, reasoning effort **high**; Mercor's judge system prompt and temperature 0.1 kept. | User: keep the cheap model, raise its effort (CAO passes effort through: hard puzzle, low ~3K / high ~44K reasoning tokens). |
| 8 | Data | The Harbor Hub copy, not Hugging Face. | Pitfall 2. |

Carried from v1: the world has no network (the prompt says there is no internet, 1.1 has no internet apps; under
Harbor the containers would have it). Agent: `gpt-5.6-luna` via CAO, effort max (`models/luna-max-cao.json`, user
2026-11-08; the leaderboard's setting). **8 tasks in parallel** (user 2026-11-09: less load; calibrated: with 8 worlds
making calls back to back a world call takes 16.8 s median, 15 s on an idle machine; the first full run at 12, with
DSH's concurrent calls, saw 35 s), 4 worlds booting at a time.

**Subagents** (user 2026-11-09): two full runs to separate the effects: with DSH's subagent tools off
(`--no-subagents`: rows tool-subagent, tool-subagent-fork, tool-subagent-control, tool-subagent-list-agents; their
paragraph leaves the system prompt with them, checked: no "subagent" anywhere in the first request), and with them on
(the prompt unchanged). Both with the relay. In the first full run, runs that used subagents passed 24% (25/105),
those that did not 42% (57/135).

## Pitfalls in Mercor's 1.1 delivery, and what we do

1. **The system prompt names a tool that 1.1 does not have.** Mercor's 1.1 prompt still says "use the code_exec tool"
   and "For the code_exec tool ... use /filesystem/", left over from 1.0. In 1.1, code execution is Stirrup's
   `run_shell` (its own description says "use only relative paths"; it starts in `/filesystem`). This was a pitfall
   we noticed in Mercor's work; we replaced `code_exec` with `run_shell` in both places, which is what the prompt
   actually means. (Mercor's leaderboard runs saw `code_exec`.)
2. **The Hugging Face copy's grading targets do not match Mercor's grader; the Hub copy's do.** On 39 criteria in 13
   tasks the HF copy (1.1.1) labels the target "Word Documents (.docx, .doc)" (likewise Spreadsheets and Presentations
   without .ods / .odp). Mercor's 1.1 grader knows only its exact category names, "Word Documents (.docx, .doc,
   .odt)" etc. (`artifact_filters.FileTypeCategory`); an unknown name falls back to "All output": no filtering, so the
   judge sees every changed file and the final message instead of only the document asked for, and grades those 13
   tasks more loosely. The Hub copy carries the grader's own names, so the grader filters as intended. That is why we
   use the Hub copy. Everything else in the two copies is the same (prompts, rubrics, gold, input files, app setup);
   only packaging differs (HF: one shared world image with the world mounted; Hub: one image per world).
3. **Neither world snapshot is switched on.** The world takes its "before" snapshot only with
   `WORLD_CAPTURE_INITIAL_SNAPSHOT=1`, which no compose file sets, and the "after" snapshot is a Harbor collect hook
   (`/app/tools/collect_world_snapshot.py`) that no task declares (Harbor runs only declared hooks). Mercor's grader
   stops with "snapshot missing" on the 34 tasks that need files. We set the variable and run their script after the
   agent. (Found by reading their files and Harbor 0.20.0; not run under Harbor.)
4. The dataset card says 955 criteria; the task files have 952.

## Changes from Mercor's own setup, and why

1. **The agent is DSH** instead of `apex_loop_truncated_tools_agent` (the point of this harness), with DSH's own tools
   added (decisions 3, 6).
2. **Orchestration is ours, not Harbor** (decision 2), with the same steps, including both snapshots (pitfall 3).
3. **System prompt**: decision 5 (`code_exec` -> `run_shell`; path sentence).
4. **ripgrep** (static 14.1.1, checksum-verified) is mounted read-only at `/opt/dsh-bench/bin` for DSH's glob/grep; the
   world image has none. Only DSH's PATH includes it; run_shell's environment is unchanged.
5. **MCP relay, one world call at a time** (2026-11-09; replaces a FastMCP-proxy bridge). DSH reaches the world's
   gateway through `container/mcp_relay.py`, run inside the world (`podman exec`, no network): a plain JSON-RPC
   pass-through to http://127.0.0.1:8000/mcp that keeps no tool list or cache, so DSH is one client of the gateway as
   Mercor's agent is. As Mercor's agent, the world gets one tools/call or tools/list at a time (a lock shared by all of
   DSH's connections: the main agent and each subagent), and the 60 s per-call limit (then 5 s grace, then cancel,
   answered "Tool call timed out") is counted from when the call reaches the world. DSH's own tools keep 60 s in
   `tool_limits`. Why: the bridge used first (a FastMCP proxy) cached the gateway's tool list for 5 minutes; under
   load the gateway sometimes lists tools without one app (it starts all 9 app servers afresh for every request, and
   one can fail to start), and the cached partial list then failed calls with "Unknown tool" in streaks: 977 of 6,840
   world calls (14%) in 68 of 240 tasks of the first full run, two thirds of them in subagents. With the relay: 0 in
   the plumbing tests, and two calls sent together run one after the other.
6. **No network** for the world (carried from v1). Harbor would give the containers network access.
7. **Judge** (decision 7): the model and its extra args in `grading_settings`; Mercor's judge system prompt and
   temperature unchanged. Through a local relay (from v1) that removes a markdown fence around JSON replies and escapes
   raw control characters: CAO does not pass `response_format` to Gemini.
8. **Leftover agent processes** (background jobs run as run_shell's user) are stopped before the "after" snapshot, so
   nothing changes the world while it is captured (Harbor stops the agent's container for the same reason). The
   code-execution app itself is left alone.
9. **Scoring of runs that do not finish**: a run at the step limit is graded (Mercor's status "failed", graded by their
   adapter); a run stopped by the 3 h timeout or an agent error is not graded and scores 0 (Mercor: status "error",
   the trial errors). Infrastructure failures are retried once in a fresh world, never scored as the agent's.

## How a task runs (run_task.py, grade.py)

1. World: `podman run` of the task's world image with its compose file's mounts (`task_files` at `/task_files`, the
   task's `mcp_config.json` at `/world/mcp_config.json`, `/logs/world` on the host) and environment, plus
   `WORLD_CAPTURE_INITIAL_SNAPSHOT=1`, network none, the bridge and ripgrep (read-only). Ready when the compose
   healthcheck passes (seeded, 9 apps up, initial snapshot written, MCP answers): about 45-75 s.
2. DSH, launcher attach mode: workspace `/filesystem`, user `svc_stirrup_code_execution`, umask 0002, run_shell's
   environment; the world's tools as `mcp__world__*`; `tool_limits` 200 / 32,768 / 60 s; 100 steps, 3 h.
3. After DSH: leftover processes of that user stopped; Mercor's `collect_world_snapshot.py` (as root: it signs with
   the world's root-only key) writes `final_snapshot.tar.gz`. `trajectory.json`: DSH's main session as ATIF (system,
   task, every model reply with its tool calls and results), the format Mercor's grader reads.
4. Grading: Mercor's verifier image runs `sh /tests/test.sh` with the task's `tests/` (judge settings replaced), the
   trajectory and both snapshots; 2 CPUs / 8 GB, 3600 s, host network for the judge relay. `grades.json`: score,
   all_pass (Pass@1), every criterion with the judge's rationale. Then the run is compacted (changed files only).

## Checks

- `tests/test_attach_user.py` 9/9, `tests/test_tool_limits.py` 7/7 (truncation identical to Mercor's Python rule on 408
  texts), the rest of the core suite unchanged.
- `test_plumbing.py`: one real task end to end with a scripted model (world, 74 + DSH tools, fence, limits, snapshots,
  trajectory).
- `check_gold.py`: the experts' outputs through the whole grading path: 6/6 tasks, 32/32 criteria
  (edit_existing_doc 7/7, edit_existing_sheet 5/5, make_new_doc 3/3, make_new_sheet 5/5, make_new_slide_deck 6/6,
  message_in_console 6/6).
- Smoke (`runs/apex11-smoke3-20261107T161504Z`, Luna high via CAO): 3/3 all criteria met; worlds ready in 87-101 s;
  agent 8-11 min, 16-22 steps; the judge's rationales cite the agent's own cells and documents and list every value
  asserted (the scattergunning guard at work).
