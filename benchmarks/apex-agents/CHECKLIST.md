# APEX-Agents: checklist answers

Benchmark: Hugging Face dataset `mercor/apex-agents` (revision `92c8685`, 480 tasks, 33 worlds, 319 files, 8.5 GiB;
gated, accept the terms and log in first) and its infrastructure Archipelago (`Mercor-Intelligence/archipelago` @
`f8e41cb`, a 2026-11-01 sync of Mercor's studio repo). Paper: arXiv 2601.14242v3, "APEX–Agents".

Status (2026-11-06): **built and tested**: images, core attach mode + fs-podman (tests/test_fs_podman.py 19/19), adapter (test_plumbing.py 15/15 on a real task, scripted model), grading (check_gold.py: gold outputs 12/12 tasks, 50/50 criteria). Smoke with Luna: running.

How to run: `run_all.py --tasks all --out runs/<run>` (grades as tasks finish; summary.md); one task: `run_task.py` then `grade.py`; gold check: `check_gold.py`. The dataset directory is read-only (an early check_gold bug overwrote 12 dataset files; restored and verified, 319/319). "Done" says whether a row is decided (D), built (B),
tested (T).

## Design (decided with the user, 2026-11-06)

- **Archipelago runs as Mercor built it; DSH replaces only Archipelago's agent.** Environment container (built from
  Archipelago's `environment/Dockerfile` at the pin), world population, MCP gateway, snapshots and grader are
  Archipelago's. Archipelago's agent (`react_toolbelt_agent`) is replaced by DSH, which connects to the gateway.
- **We keep the world's tools because they are part of the benchmark, not because a harness brought them.** APEX-Agents
  defines every world as 9 apps (MCP servers), listed per world in `world_descriptions.json`: Word, Excel, Powerpoint,
  PDFs, Mail, Calendar, Chat, Filesystem, Code Execution; worlds 244 and 246 add Edgar SEC and FMP. All of them stay,
  including Filesystem and Code Execution, although DSH's `read`, `read_image` and `glob` do the same as three
  Filesystem tools (`read_text_file`, `read_image_file`, `search_files`) and DSH's `bash` does the same as `code_exec`.
  What DSH replaces is the harness Archipelago ships separately: the agent loop, its toolbelt meta-tools, `todo_write`,
  `final_answer`, context summarisation. Both kinds of tools work on the same files, so nothing conflicts.
- **DSH's own tools run inside Archipelago's environment container**, on the world's files in `/filesystem`: `bash`
  (and background jobs, `glob`/`grep`) through `plugins/sandbox-podman` pointed at that container; `read`, `write`,
  `edit`, `read_image` through a new opt-in core plugin `fs-podman` (a `ctx.fs` backend, like DSH's own `fs-e2b`).
  So every tool, DSH's and the apps', sees the same files under the same path.
- **Toolbelt on** (core-v4 `plugins/toolbelt`): the app tools are hidden until the agent adds them, as in Archipelago's
  harness; DSH's tools are always visible.

## Changes from Archipelago's own setup, and why

Archipelago's code is used unmodified. These are the places where how we run it differs from its Hugging Face example
(`examples/hugging_face_task`) or its open-source image. Each was decided with the user.

1. **App servers start once and keep running (HTTP) instead of restarting on every tool call (stdio)**
   (2026-11-06). The example runs every app as a stdio subprocess (`uv run python main.py`, `MCP_TRANSPORT=stdio`).
   The gateway opens a fresh connection per request (`client_factory=lambda: base_client.new()`), so every tool call
   started all 9 servers and shut them down again. Measured: 11.6 s per call, even for `code_exec` with `echo hi`;
   9 -> 153 processes, 120 MB -> 900 MB per call. We start each server once inside the container with the example's
   exact command and environment, changing only `MCP_TRANSPORT=http` (each server's own default) and a port (`MCP_PORT`),
   and give the gateway their URLs. Server names, and with them tool names, are unchanged. Measured: the same 73
   tools (the tool list is the same size to the byte, 271,492 characters), the same results, 0.25 s per call; the
   container holds about 1 GB with all servers resident. What else changes: anything an app keeps in memory (e.g. the
   PDF app's extracted-image cache) now lives across calls. It did not before, though `read_image` re-extracted on a
   miss. It probably matches how Mercor ran the paper's experiments (the servers default to HTTP), but that is not
   documented.
2. **`code_exec`'s package mirror is rebuilt in our image layer** (approved 2026-11-06). In Mercor's images an internal
   install task (not in the open-source repo) fills `/usr/local/lib/code_execution`: the Python packages `code_exec`
   puts on `PYTHONPATH`, the Node modules on `NODE_PATH` (docx, pptxgenjs, react, sharp) and the `soffice` wrapper that
   lets LibreOffice start under the sandbox shim. The open-source Dockerfile instead pip-installs the packages into the
   system Python; that step fails (`ResolutionImpossible`: litellm 1.83.10 / fastmcp-slim 3.3.1 / python-dotenv
   1.2.1), and the `;`-joined RUN hides it. Checked: in the unmodified image `code_exec` cannot import pandas,
   openpyxl or python-docx. Our layer installs the exact locked versions (516 pins from the code server's `uv.lock`,
   `--no-deps`, no re-resolution), `node_tools/package-lock.json`, and `sandbox_bin/soffice` into the mirror.
3. **Individual tools** (`USE_INDIVIDUAL_TOOLS=true`; `GUI_ENABLED=true` for EDGAR/FMP). The example sets neither, so
   the apps would serve 2 combined tools each. The paper's tool counts (63, 187) and tool names are individual tools.
4. **The "before" snapshot is taken after the task's input files are loaded.** The example grades against the bare
   world zip, so a task's input files would look created by the agent.
5. **Grading target passed to the grader** (the task's `expected_output`, as the paper). The example passes only the
   criterion text.
6. **Budgets and judge**: 250 steps as the paper (the example: 50); judge `gemini-3.8-flash` at low thinking (paper:
   Gemini 3 Flash at low; example: `gemini-2.5-flash`).

## Tool map (individual-tool mode, the paper's)

| App | Server | Tools | Works on | DSH duplicate |
|---|---|---|---|---|
| Word | `docs_server` | 15 | `.docx` in `/filesystem` | none |
| Excel | `sheets_server` | 12 | `.xlsx`/`.csv` in `/filesystem` | none (`read_csv` overlaps `read` on raw text) |
| Powerpoint | `slides_server` | 13 | `.pptx` in `/filesystem` | none |
| PDFs | `pdf_server` | 5 | `.pdf` in `/filesystem` | none |
| Mail | `mail_server` | 7 | its mailbox in `/.apps_data/mail` | none |
| Calendar | `calendar_server` | 5 | its events in `/.apps_data/calendar` | none |
| Chat | `chat_server` | 9 | its channels in `/.apps_data/chat` | none |
| Filesystem | `filesystem_server` | 6 (read-only) | any file in `/filesystem` | `read_text_file`~`read`, `read_image_file`~`read_image`, `search_files`~`glob`; `list_files`, `get_directory_tree`, `get_file_metadata` ~ `ls`/`find`/`stat` in `bash` |
| Code Execution | `code_execution_server` | 1 | shell commands in `/filesystem` | `code_exec` ~ `bash` (`sh` vs `bash`, 300 s / 100 KB limits vs DSH's) |
| Edgar SEC (244, 246) | `edgar_sec` | 8 | live SEC filings | none |
| FMP (244, 246) | `fmp_server` | 179 | live market data (needs an API key) | none |

73 tools in the 9 apps today (the paper counted 63); 8 + 179 = the paper's 187 in the two banking worlds.

## Checklist

| # | Item | Answer | Done |
|---|------|--------|------|
| 1 | Task prompt | `prompt` of `tasks_and_rubrics.json`, verbatim, as the user message. Scanned all 480: no paths, no `/filesystem`, no tool names, no `code_exec`/`final_answer`. Harness-flavoured phrases need no change: "message to/in the console" (6) and "reply back to me / here" (137) = the `final_answer` text; "the attached file/email/SEC filings" = the task's input files in `/filesystem`; "data tools available to you" (1) = the EDGAR/FMP apps. | D |
| 1 | System prompt | The paper's (Appendix D.2; Archipelago's README "to reproduce the paper"), appended after DSH's persona, verbatim except the path sentence, which also names DSH's tools: "For every tool except the code_exec, bash, read, write, edit, read_image, glob and grep tools, you may assume that all relevant files are located under the root path /. For those tools, however, you must explicitly use /filesystem/ as the root path to locate all relevant files." (approved 2026-11-06) | D |
| 1 | Hard-coded paths | None in the prompts. The paper prompt's `/` (app tools) and `/filesystem/` (`code_exec`) hold, since every tool works in Archipelago's container; DSH's working directory is `/filesystem`. | D |
| 1 | Env vars | None. | D |
| 1 | Hidden material | Rubrics, `gold_response`, `gold_files/` stay in the dataset on the host; never in the container or the prompt. | D |
| 2 | Staged files | World zip (`filesystem/` + `.apps_data/`), then the task's `task_files/<id>/` overlay (141 tasks; 3 add files under `.apps_data/calendar`), through Archipelago's `/data/populate` as its example does. | D |
| 2 | Read-only / writable | As Archipelago: `/filesystem` writable (19 tasks edit existing files); `/.apps_data` only through Mail/Calendar/Chat. | D |
| 2 | Baseline snapshot | Archipelago's `/data/snapshot` after population (world + task files), before the agent starts. (Archipelago's HF example uses the bare world zip as "before", so task input files would look agent-created; not copied.) | D |
| 3 | Image | Base `dsh-bench-apex-agents-env:f8e41cb`: Archipelago's `environment/Dockerfile` at the pin, built unmodified (12.4 GB; no Mercor credentials needed). Our layer `benchmarks/apex-agents/Dockerfile`: `code_exec`'s package mirror (change 2) and ripgrep for DSH's `glob`/`grep`. | B, T (code_exec imports pandas 2.3.3 etc., node docx/pptxgenjs, LibreOffice Calc under the shim; no Writer/Impress in Archipelago's image) |
| 3 | Agent packages | Archipelago's image as is: Python 3.13 with `code_exec`'s package set (pandas, openpyxl, python-docx, python-pptx, pymupdf, pdfplumber, ...), LibreOffice, Chromium, poppler. | D |
| 3 | Resource limits | None (Archipelago sets none locally). | D |
| 4 | Container network | None, except worlds 244 and 246: internet for EDGAR (sec.gov) and FMP. There `code_exec` and `bash` reach the internet too (as in Archipelago's example). | D |
| 4 | Web tools | Off (`web_search`, `web_fetch`): the paper turns web search off for reproducibility. | D |
| 4 | Credentials | FMP key from `DSH_BENCH_FMP_KEY_FILE` in your `local.env` (a file, chmod 600; every user brings their own; never in the repo). Passed only to the FMP server in the environment container of worlds 244/246. | D |
| 5 | Native tools | DSH's headless set minus web; `bash` and file tools inside Archipelago's container (see Design). | D |
| 5 | MCP servers | Archipelago's gateway (`/mcp/`) as one DSH MCP server: the 9 apps (+2 in 244/246), `USE_INDIVIDUAL_TOOLS=true` (and `GUI_ENABLED=true` for EDGAR/FMP), as the paper. App servers run once per task over HTTP (change 1); DSH's call timeout for them is 300 s. Measured with individual tools: 73 tools. | D, (b) tested |
| 5 | Tool visibility | Toolbelt on: app tools hidden until added; DSH tools visible. | D |
| 5 | Side effects / back doors | `/.apps_data` (graded) is reachable only through Mail/Calendar/Chat: DSH's `bash` runs under Archipelago's path-blocking shim (`sandbox_fs.so`: `/app`, `/.apps_data`, `/proc`, `/sys`), the same rules as `code_exec`; `fs-podman` refuses paths outside `/filesystem`. | D |
| 6 | Skills | None. | D |
| 7 | Budgets / model | `models/luna-cao.json` (GPT-5.6 Luna, effort high, the harness standard); 250 steps (paper); 3 h wall clock (Archipelago's default); a run that hits a limit counts as failed (paper). | D |
| 8 | Ending / answer | `final_answer` (core), or DSH's own end of a turn (a reply that calls no tool): the answer is then that reply, as for JobBench and Harvey (first Luna smoke task ended so; Archipelago's harness would nudge the model to call final_answer, a harness feature we do not copy). Only the step limit, the timeout and errors count as failed (paper). 422 tasks answer in the text ("message in console"); 58 create or edit a file (`expected_output`: make_new_doc 20, edit_existing_sheet 16, make_new_sheet 14, make_new_slide_deck 5, edit_existing_doc 2, edit_existing_slide_deck 1). | D |
| 9 | Grader | (B, T: `grade.py`, `check_gold.py` 50/50 on gold outputs; LiteLLM needs `allowed_openai_params` to pass `reasoning_effort` for gemini-3.8-flash) Archipelago's grading runner, unchanged: `output_llm` per criterion, mean score per task; Pass@1 = all criteria met. Judge `gemini-3.8-flash` at low thinking via CAO (paper: Gemini 3 Flash, low; not on CAO). Grading target = the task's `expected_output` for every criterion (the released rubric has no per-criterion target). Document extraction local (no Reducto key), to be checked for errors on the gold files. Input: before/after snapshots + a trajectory file converted from DSH's session (first user message, final answer). | D |
| 10 | Smoke / runs | 60 tasks (20 per job, seeded random) with Luna, then all 480 x 1; 20 tasks at a time (measured: about 1 GB per task container with all servers running; 24 cores, 185 GB free). | D |
| 10 | Reference | Archipelago's own agent (`react_toolbelt_agent`, the paper's prompt and settings) with Luna on the same 60 tasks; the paper's leaderboard (other models) for context. | D |
| 10 | Isolation tests | `tests/test_fs_podman.py` (file tools refuse paths and symlinks outside the workspace) and `test_plumbing.py` (bash cannot reach `/.apps_data` or `/app`; world containers have no network unless 244/246). | T |
