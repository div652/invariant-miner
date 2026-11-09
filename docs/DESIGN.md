# Design

One DeepSeek Harness (DSH) setup that runs any benchmark. Each benchmark adds a patch file and a small adapter.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| DSH build | `deepseek-ai/deepseek-harness` @ `c389f96` + the 7 patches of `agentic-evolution` + our 0008 (`patches/deepseek-harness/`), `headless` profile | The build that ran JobBench in `agentic-evolution`; our Luna run on it matched their score (0.388 vs 0.393 macro, 65 tasks). |
| Where things run | **Agent loop on the host, tools in a container** | Model calls, credentials and session logs stay on the host, out of the agent's reach; the container can run with no network. DSH's tools stay native. |
| Container runtime | rootless podman (configurable) | Same as Harvey LAB's sandbox; no daemon, runs as the host user. |
| Default image | `images/base`: minimal (Python + bash + coreutils + ripgrep) | Each benchmark adds only what it expects, in its own layer. |
| Per-benchmark work | `benchmarks/<name>/`: `patch.yml`, adapter, optional `Dockerfile`, `CHECKLIST.md` | Everything a benchmark changes is in one place; [BENCHMARK_CHECKLIST.md](BENCHMARK_CHECKLIST.md) lists what to check. |

## How a run works

```
HOST
  launcher (per task)
    1. stage the workspace (task files / repo), take the baseline snapshot
    2. start the container: workspace mounted at the SAME absolute path, --network=none,
       --cap-drop=ALL, no-new-privileges, host uid/gid
    3. write run.patch.yml (model, system prompt, disabled rows, MCP servers); set DSH_BENCH_* (container, budgets)
    4. dsh --profile headless --patch harness/core.patch.yml --patch run.patch.yml [--patch benchmark.yml ...] "<task>"
       (cwd = workspace, DSH_HOME outside it)
         agent loop, model calls ............ host
         read / write / edit ................ host, file tools in workspace-isolated mode (no access outside it)
         bash, background jobs, glob/grep ... container, via the sandbox-podman plugin (podman exec)
         web_search / web_fetch ............. host, only if the benchmark enables them
         benchmark MCP tools ................ wherever the benchmark serves them
    5. collect: final answer, workspace (final tree + diff against the snapshot), session logs
    6. stop the container; run the benchmark's grader on the host
```

The workspace is mounted at its host path so a path means the same thing to the file tools (host) and to bash
(container). A benchmark that hard-codes another path (`/workspace`) gets its prompt text substituted, or, if that
cannot work, the fallback of running DSH inside the container.

## What makes the isolation work (tested by `tests/test_isolation.py`, 19 checks)

| Piece | Setting |
|---|---|
| Container | rootless podman, `--network=none --cap-drop=ALL --security-opt=no-new-privileges --userns=keep-id` (runs as the host uid), workspace mounted at its host path, read-only subdirectories mounted `:ro`, `HOME=/tmp` |
| DSH sandbox | `harness/core.patch.yml`: the base `sandbox` row disabled, `sandbox-podman` inserted; `DSH_PERMISSION_MODE=workspace-isolated` plus a `permission` preset with `sandbox: workspace-isolated, approval: never` (DSH refuses to boot if the defaults match no preset) |
| File tools | `workspace-isolated`: they resolve real paths, so paths and symlinks outside the workspace are refused |
| Read-only directories | `:ro` in the container AND read-only permissions on the host (the file tools run on the host) |
| Killing commands | `podman-exec.sh` runs each command in its own process group and kills that group inside the container when DSH stops the command (tool timeout, `job_kill`) |
| Collection | copies symlinks as links, never their targets (the agent can create links to host paths) |

## Known differences from running everything in one place

- **The workspace is the only shared place.** bash runs in the container, the file tools (`read`, `write`, `edit`)
  on the host. A file bash writes outside the workspace (e.g. `/tmp/x.txt`) exists only in the container, so `read`
  cannot open it (and refuses the path anyway: it is outside the workspace). Seen in the first Harvey smoke run: the
  agent wrote converted text to `/tmp`, `read` refused it, and it copied the files into the workspace instead.

## Core pieces (shared by every benchmark)

| Piece | What it does |
|---|---|
| `plugins/sandbox-podman` | **Done, tested.** Provides `ctx.sandbox`: `confine(argv)` returns `podman exec` argv into the run's container, so `bash`, jobs and glob/grep run there unchanged. Maps DSH's bundled ripgrep path to the container's `rg`; `podman-exec.sh` kills the command's process group inside the container when DSH stops it. |
| `plugins/final-answer` | A `final_answer` tool that records the answer and ends the turn. |
| `plugins/benchmark-limits` | Step limit, wall-clock timeout, temperature (from `agentic-evolution`'s `benchmark-limits.mjs`). |
| `plugins/toolbelt` | **Optional** (spec key `toolbelt`, off by default). Managed tools (default: every MCP tool) are not offered to the model until the agent adds them with `toolbelt_list_tools` / `toolbelt_inspect_tool` / `toolbelt_add_tool` / `toolbelt_remove_tool` (at most 80). A port of the toolbelt of Archipelago's `react_toolbelt_agent`: same tool names, descriptions, result and error texts. Hides tools in the `system-prompt/assemble` waterfall (DSH rebuilds the tool list before every step) and denies calls to hidden tools in `tools/pre-execute`. One toolbelt per agent. Tested by `tests/test_toolbelt.py`. |
| `plugins/fs-podman` + launcher `attach` | **Optional** (spec key `attach`). For a benchmark whose environment is its own running container with the files at a path that exists only there (e.g. `/filesystem`): the launcher does not stage or start a container; DSH's session cwd is that path (DSH patch 0008), commands run there (`sandbox-podman`, `hostCwd`), and `fs-podman` replaces `fs-sandbox` so `read`/`write`/`edit`/`read_image` work there too. Containment is fixed to that path (symlinks resolved in the container). Operations go through one helper process in the container (python3; else one `podman exec` each). Optional `attach` keys `user` (container user, name or uid[:gid]; a name brings its groups) and `umask` apply to both commands and file operations, so DSH's tools can have exactly the access of a world's own code-execution user (new files: 666 minus the umask). Tested by `tests/test_fs_podman.py`, `tests/test_attach_user.py`. |
| `plugins/tool-limits` | **Optional** (spec key `tool_limits`: `max_lines`, `max_chars`, `timeout_s`). Every tool call, DSH's own and MCP: each text block of the result keeps its head (first `max_lines` lines, then at most `max_chars` code points) with a note of what was cut, the rule of Archipelago's `loop_truncated_tools` agent; a call running past `timeout_s` is aborted and answered "Tool call timed out". `tools/post-execute` and `tools/execute` hooks. Tested by `tests/test_tool_limits.py` (including parity with the Python rule). |
| MCP bridge | Serves benchmark tools that are plain functions or REST APIs as an MCP server. |
| launcher | Steps 1-6 above. |
| `images/base` | The minimal default container image. |

## Outputs of every run

| Output | Content |
|---|---|
| `answer.json` | The `final_answer` argument, else the last assistant message; the finish reason. |
| `workspace/` + `workspace.diff` | The final workspace, and the diff against the baseline snapshot. |
| `dsh-home/sessions/**/session.v2.jsonl` | The trajectory: one file per agent and subagent. |
| `run.json` | What ran: DSH commit, patch files, image digest, model, budgets, timings. |
