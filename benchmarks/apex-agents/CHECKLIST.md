# APEX-Agents: checklist answers

Benchmark: Hugging Face dataset `mercor/apex-agents` (revision `92c8685`, 480 tasks, 33 worlds, 319 files, 8.5 GiB;
gated, accept the terms and log in first) and its infrastructure Archipelago (`Mercor-Intelligence/archipelago` @
`f8e41cb`, a 2026-11-01 sync of Mercor's studio repo). Paper: arXiv 2601.14242v3, "APEX–Agents".

Status: **decisions recorded, nothing built yet** (2026-11-06). "Done" says whether a row is decided (D), built (B),
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
| 1 | System prompt | The paper's (Appendix D.2; Archipelago's README "to reproduce the paper"), appended after DSH's persona. Wording of the path sentence for DSH's tools: **open**. | open |
| 1 | Hard-coded paths | None in the prompts. The paper prompt's `/` (app tools) and `/filesystem/` (`code_exec`) hold, since every tool works in Archipelago's container; DSH's working directory is `/filesystem`. | D |
| 1 | Env vars | None. | D |
| 1 | Hidden material | Rubrics, `gold_response`, `gold_files/` stay in the dataset on the host; never in the container or the prompt. | D |
| 2 | Staged files | World zip (`filesystem/` + `.apps_data/`), then the task's `task_files/<id>/` overlay (141 tasks; 3 add files under `.apps_data/calendar`), through Archipelago's `/data/populate` as its example does. | D |
| 2 | Read-only / writable | As Archipelago: `/filesystem` writable (19 tasks edit existing files); `/.apps_data` only through Mail/Calendar/Chat. | D |
| 2 | Baseline snapshot | Archipelago's `/data/snapshot` after population (world + task files), before the agent starts. (Archipelago's HF example uses the bare world zip as "before", so task input files would look agent-created; not copied.) | D |
| 3 | Image | `dsh-bench-apex-agents-env:f8e41cb`, Archipelago's `environment/Dockerfile` at the pin, plus ripgrep for DSH's `glob`/`grep`. | building |
| 3 | Agent packages | Archipelago's image as is: Python 3.13 with `code_exec`'s package set (pandas, openpyxl, python-docx, python-pptx, pymupdf, pdfplumber, ...), LibreOffice, Chromium, poppler. | D |
| 3 | Resource limits | None (Archipelago sets none locally). | D |
| 4 | Container network | None, except worlds 244 and 246: internet for EDGAR (sec.gov) and FMP. There `code_exec` and `bash` reach the internet too (as in Archipelago's example). | D |
| 4 | Web tools | Off (`web_search`, `web_fetch`): the paper turns web search off for reproducibility. | D |
| 4 | Credentials | FMP key from `DSH_BENCH_FMP_KEY_FILE` in your `local.env` (a file, chmod 600; every user brings their own; never in the repo). Passed only to the FMP server in the environment container of worlds 244/246. | D |
| 5 | Native tools | DSH's headless set minus web; `bash` and file tools inside Archipelago's container (see Design). | D |
| 5 | MCP servers | Archipelago's gateway (`/mcp/`) as one DSH MCP server: the 9 apps (+2 in 244/246), `USE_INDIVIDUAL_TOOLS=true` (and `GUI_ENABLED=true` for EDGAR/FMP), as the paper. | D |
| 5 | Tool visibility | Toolbelt on: app tools hidden until added; DSH tools visible. | D |
| 5 | Side effects / back doors | `/.apps_data` (graded) is reachable only through Mail/Calendar/Chat: DSH's `bash` runs under Archipelago's path-blocking shim (`sandbox_fs.so`: `/app`, `/.apps_data`, `/proc`, `/sys`), the same rules as `code_exec`; `fs-podman` refuses paths outside `/filesystem`. | D |
| 6 | Skills | None. | D |
| 7 | Budgets / model | `models/luna-cao.json` (GPT-5.6 Luna, effort high, the harness standard); 250 steps (paper); 3 h wall clock (Archipelago's default); a run that hits a limit counts as failed (paper). | D |
| 8 | Ending / answer | `final_answer` (core). 422 tasks answer in the text ("message in console"); 58 create or edit a file (`expected_output`: make_new_doc 20, edit_existing_sheet 16, make_new_sheet 14, make_new_slide_deck 5, edit_existing_doc 2, edit_existing_slide_deck 1). | D |
| 9 | Grader | Archipelago's grading runner, unchanged: `output_llm` per criterion, mean score per task; Pass@1 = all criteria met. Judge `gemini-3.8-flash` at low thinking via CAO (paper: Gemini 3 Flash, low; not on CAO). Grading target = the task's `expected_output` for every criterion (the released rubric has no per-criterion target). Document extraction local (no Reducto key), to be checked for errors on the gold files. Input: before/after snapshots + a trajectory file converted from DSH's session (first user message, final answer). | D |
| 10 | Smoke / runs | 60 tasks (20 per job) with Luna, then all 480 x 1. | D |
| 10 | Reference | Archipelago's own agent (`react_toolbelt_agent`, the paper's prompt and settings) with Luna on the same 60 tasks; the paper's leaderboard (other models) for context. | D |
| 10 | Isolation tests | To do: `bash` and `fs-podman` cannot reach `/.apps_data` or `/app`; no network outside 244/246. | todo |
