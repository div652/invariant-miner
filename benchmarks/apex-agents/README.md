# APEX-Agents on dsh-bench-harness

[APEX-Agents](https://arxiv.org/abs/2601.14242) (Mercor, 480 professional-services tasks in 33 simulated worlds) run
with DSH as the agent. Archipelago, Mercor's infrastructure, provides the environment (one container per task with the
world's files and apps behind an MCP gateway) and the grader, both used as built. DSH replaces only Archipelago's own
agent.

- [CHECKLIST.md](CHECKLIST.md): every decision, the tool map, and each way we differ from Archipelago's own setup.
- [RESULTS.md](RESULTS.md): results so far.

## Requirements

- Linux with rootless podman, git, python3, [uv](https://docs.astral.sh/uv/), node ^22.19 or >= 24.
- Disk: ~15 GB for the images, ~9 GB for the dataset, a few GB per run in flight (graded tasks are compacted to MB).
- A model endpoint for the agent (`--endpoint cao|trapi|vscode|vllm`, see `endpoints/README.md`) and an
  OpenAI-compatible endpoint for the judge (default: CAO).
- If VS Code is connected to this machine, keep its file watcher off the run folders (`files.watcherExclude` for
  `**/runs/**` and `**/work/**`): a watcher over millions of run files once took the whole per-user inotify budget.

## Setup

```bash
./setup.sh                              # DSH at its pin + patches, built into work/; image dsh-bench-base
benchmarks/apex-agents/setup.sh         # Archipelago at its pin, images dsh-bench-apex-agents-env + dsh-bench-apex-agents,
                                        # grader venv; then lists anything still missing
```

Settings go in `~/.config/dsh-bench/local.env` (template: `local.env.example`; file paths, not secrets):

| Setting | For |
|---|---|
| `DSH_BENCH_CAO_KEY_FILE` | agent via CAO (`--endpoint cao`) and the judge (default) |
| `DSH_BENCH_JUDGE_BASE_URL`, `DSH_BENCH_JUDGE_KEY_FILE` | optional: another endpoint for the judge (`gemini-3.8-flash`) |
| `DSH_BENCH_FMP_KEY_FILE` | FMP app, banking worlds 244/246 only (a limited FMP plan lacks some symbols: RESULTS.md) |
| `DSH_BENCH_EDGAR_USER_AGENT` | Edgar SEC app, banking worlds 244/246 only: `"<your name> <your email>"` (SEC requires it) |

Dataset (gated): accept the terms at huggingface.co/datasets/mercor/apex-agents, then

```bash
hf auth login
hf download mercor/apex-agents --type dataset --local-dir ~/apex-agents-data   # or pass --dataset to the scripts
chmod -R a-w ~/apex-agents-data                                                 # nothing here should write to it
```

## Check the installation (no model calls unless noted)

```bash
export NODE=/path/to/node22
python3 tests/test_fs_podman.py                   # DSH's file tools and bash inside a container-only workspace
python3 tests/repro_attach_exit.py                # DSH exits promptly after a one-step answer
python3 benchmarks/apex-agents/test_plumbing.py   # one real task end to end with a scripted model: world loaded,
                                                  # 9 apps / 73 tools behind the toolbelt, sandbox fence, snapshots
python3 benchmarks/apex-agents/check_gold.py --out runs/gold-check --per-type 1   # judge calls: the experts' gold
                                                  # outputs must pass (grading pipeline + document extraction)
```

## Run

```bash
export NODE=/path/to/node22
python3 benchmarks/apex-agents/run_all.py --tasks all --out runs/apex-<name> [--jobs 12] [--endpoint cao | --model models/x.json]
```

- `--tasks all` or a file of task ids (`smoke-3.txt`, `banking-28.txt`). Tasks run in parallel (default 12) and are graded as
  they finish. Re-running the same command resumes: finished tasks are skipped, killed ones moved to `aborted/`.
- Per task in `runs/<name>/tasks/<task_id>/`: `run.json` (timings, finish reason, `infra_error` if a container step
  failed), `agent/` (DSH's run: `answer.json`, sessions), `grading/grades.json` (score, all criteria met, each criterion
  with the judge's rationale), `snapshots/changes.*` (what the agent changed).
- `summary.md` / `summary.json` at the end: Pass@1 (share of tasks with every criterion met), mean score, by job and output.
- Infrastructure failures (setup, agent start, the final snapshot) are retried once in a fresh container and are never
  graded as agent failures. Runs that end at the step limit or the time budget score 0, as in the paper.
- One task by hand: `run_task.py --task <id> --out <dir>`, then `grade.py <dir>` (`--regrade`, `--keep-snapshots`).

A full run (480 tasks) took 8.6 h at 20 parallel tasks; 12 is the default now (about 10 h, much less podman load).
