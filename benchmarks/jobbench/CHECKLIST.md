# JobBench: checklist answers

Reference: `agentic-evolution`'s JobBench runner (`eval/run_benchmark_dsh_nobwrap.sh` + overlay
`eval/dsh-gpt56-luna-262k-32k.patch.yml`, job-bench-eval @ f938276 + 21 patches), DSH c389f96 + 7 patches. Where this
setup differs from the reference, the row says so.

| # | Item | Answer | Done |
|---|------|--------|------|
| 1 | Task prompt | The reference runner's prompt, byte for byte (`make_specs.py` `PROMPT`), its temp paths replaced by `{workspace}/task_folder`, `{workspace}/output`, `{workspace}`. The task itself is `task_folder/TASK_INSTRUCTIONS.txt`, which the prompt tells the agent to read. | yes |
| 1 | System prompt | None from the benchmark: DSH's headless persona only (as the reference). | yes |
| 1 | Hard-coded paths | None: the prompt names the real workspace paths (the reference did the same with its temp dir). | yes |
| 1 | Env vars | None needed. | yes |
| 1 | Hidden material | `RUBRICS.json`, `task_card.md`, `files_required_to_search` stay in the dataset, never staged or prompted. | yes |
| 2 | Staged files | `<dataset>/<task>/task_folder/` copied to `workspace/task_folder/`; `workspace/output/` created empty. | yes |
| 2 | Read-only / writable | Both writable, as in the reference (agents may write scratch files next to the inputs). **Differs from Harvey-style read-only inputs on purpose (parity).** | yes |
| 2 | Grading material location | Dataset dir only; the grader copies it next to the outputs in `RUN/grading/`. | yes |
| 3 | Image | `dsh-bench-jobbench` (`benchmarks/jobbench/Dockerfile`, FROM `dsh-bench-base`), 1.3 GB. | yes |
| 3 | Agent packages | Python 3.12 + job-bench-eval's locked packages (`requirements.txt`: pandas 3.0.2, openpyxl, python-docx, python-pptx, pypdf 6.19.0, xlrd 2.0.2, pdfplumber, reportlab, mammoth, ...); LibreOffice 7.4 (writer/calc/impress), poppler 22.12, pandoc 2.17, sqlite3, git, curl, wget. **Differs**: the reference agents used the host's versions (e.g. a newer pandoc in /usr/local/bin) and anything else installed on that host. | yes |
| 3 | Resource limits | None set (the reference had none). | yes |
| 4 | Container network | `pasta` (internet on): the reference agents' bash had the host network and some tasks fetch external data. Checked: the container cannot reach the host's loopback services (CAO :4141, model proxy :8018, Exa relay :8010, judge :8019). `make_specs.py --network none` turns it off. | yes |
| 4 | Web tools | On: `web_search` (Exa through the relay on :8010, `EXA_API_KEY` = the relay's client key, from the file `DSH_BENCH_EXA_KEY_FILE` in your `local.env`) and `web_fetch` (HTTP, PDF text from DSH patch 0002), as the reference. They run on the host. | yes |
| 5 | Native tools | All of the headless profile, as the reference (bash, read/write/edit, glob/grep, web, todo, skill, subagents, workflow, goal, jobs). Since 2026-11-09 subagents are off in the core for every benchmark (`harness/core.patch.yml`); the parity run had them. | yes |
| 5 | MCP servers | None. | yes |
| 5 | Non-MCP tools | None. | yes |
| 5 | Side effects / back doors | Grading reads only output files; nothing to bypass. | yes |
| 6 | Skills | None provided. | yes |
| 7 | Budgets / model | Default now `models/luna-cao.json`, the harness-wide standard (c34 endpoint: Luna on CAO directly, summaries on, effort medium, 128K output). The parity run below used `models/luna-proxy-high.json` (the reference overlay's settings: model_serve proxy on :8018, reasoning high, 262K context, 32K output); the standard has not been run on JobBench yet. Timeout 7,200 s per task, no step limit, temperature unset. | yes |
| 8 | Ending / answer format | The agent just stops; `final_answer` is OFF (the reference had no such tool). Deliverables are files in `output/`. | yes |
| 9 | Standard outputs | Checked on the smoke task: answer.json (last message, finish `completed`), workspace.diff = the 3 deliverables + the agent's one scratch script (no harness files), 1 complete root session, run.json. | yes |
| 9 | Collection / symlinks | `grade.sh` copies regular files only; symlinks are listed in `grading/skipped-symlinks.txt`. | yes |
| 9 | Grader input / command | `grade.sh [--rubrics original\|v1] RUN_DIR`: builds a JobBench layout (`<grading dir>/dataset/main/<task>/` with the dataset files + `model_output/<label>/`; `RUBRICS.json` from the chosen rubric set), then your `judge_parallel.sh` (`JOBBENCH_JUDGE_PARALLEL` in `local.env`; JobBench's own `run_judge.sh`, grok-4.6 high via the CAO shim on :8019). | yes |
| 9 | Rubric sets | Two, chosen when grading with `grade.sh --rubrics` (default `original`). **original**: the dataset's own `RUBRICS.json`; results in `RUN_DIR/grading/`. **v1**: agentic-evolution's task-instruction-aligned v1 rubrics, kept in this repository (`benchmarks/jobbench/rubrics/task-instruction-aligned-v1/`, copied verbatim from microsoft/agentic-evolution with its authors' permission; provenance in `rubrics/README.md`, checked by `test_rubrics.py`), so a clone grades on v1 with nothing else to fetch; results in `RUN_DIR/grading-v1/`. v1 keeps every task's total weight (4,500 over the 65 tasks) and drops what the task instructions do not ask for (hidden expected conclusions, exact phrases, unrequested sections, duplicated penalties); it was written against agentic-evolution's refined task instructions (its README). A run can be graded on both: each set has its own directory, and `<grading dir>/rubrics.json` records the set, its source, git commit and a sha256 of the RUBRICS.json files graded. Another rubric tree: `--rubrics DIR` with `GRADING_DIR`. `trace_digest.py --rubrics original\|v1` shows either set's verdicts. | yes |
| 10 | Smoke | `financial_managers_branch_or_department/task1` (2026-11-05): completed in ~8 min, 35 steps, 39 tool calls (bash 20, edit 7, web_search 2, glob/grep 4), 3 deliverables; grok-4.6 score 30/90 = 0.333. Reference harness, same task, model and judge: 40/90 (one run each; per-task run-to-run SD is ~0.13-0.15). | yes |
| 10 | Reference | **train-20, 2026-11-05 (core-v0)**: mean score/max **0.325** vs the reference harness's **0.307** (same model, judge, rubrics, tasks; one run each): +0.018, 95% CI [-0.028, +0.067] (paired bootstrap over tasks), W/T/L 7/6/7. Matches the reference within noise. Per task: `RESULTS.md`. | yes |
| 10 | Isolation tests | `tests/test_isolation.py` uses `dsh-bench-base`; the JobBench image differs only in packages and the network setting. | partly |
