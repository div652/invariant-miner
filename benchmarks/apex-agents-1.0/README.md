# APEX-Agents 1.0 on dsh-bench-harness (kept)

The repo's APEX-Agents benchmark is now APEX-Agents 1.1, in `benchmarks/apex-agents/`. This directory keeps version 1
of this work (the 480-task 1.0 dataset on Archipelago f8e41cb, tag `apex-agents-v1`), runnable as before.

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
benchmarks/apex-agents-1.0/setup.sh         # Archipelago at its pin, images dsh-bench-apex-agents-env + dsh-bench-apex-agents,
                                        # grader venv; then lists anything still missing
```

Archipelago is fetched by commit hash (`f8e41cb`): upstream rewrites its history on every sync, so the commit may
drop off upstream. The setup then falls back to [div652/archipelago-pinned](https://github.com/div652/archipelago-pinned),
an unmodified copy of that commit kept only so it stays fetchable. It is Mercor's work, not ours (Apache-2.0); the repo
is private, so ask for access, or set `ARCHIPELAGO_URL` to another copy.

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
python3 benchmarks/apex-agents-1.0/test_plumbing.py   # one real task end to end with a scripted model: world loaded,
                                                  # 9 apps / 73 tools behind the toolbelt, sandbox fence, snapshots
python3 benchmarks/apex-agents-1.0/check_gold.py --out runs/gold-check --per-type 1   # judge calls: the experts' gold
                                                  # outputs must pass (grading pipeline + document extraction)
```

## Splits

`splits.json`: the shared train / val / test split of the 480 tasks, 60/20/20 = 288 / 96 / 96, stratified by job
(96 / 32 / 32 each), task ids listed (the file is the split; `benchmarks/apex-agents/make_splits.py` made it, seed 20261109). It is
aligned with the APEX-Agents 1.1 split (`benchmarks/apex-agents/splits.json`): each 1.0 task that 1.1 kept (`in_v11`) is in the same
split in both, so a task tuned on in one version is never a test task in the other. Run a split with
`run_all.py --tasks split:train` (val, test; `trainval` = train + val when working with only a train and a test set);
`--dry-run` lists the tasks; `python3 -m dsh_bench.splits benchmarks/apex-agents-1.0/splits.json --check` shows the counts.

## Run

```bash
export NODE=/path/to/node22
python3 benchmarks/apex-agents-1.0/run_all.py --tasks all --out runs/apex-<name> [--jobs 12] [--endpoint cao | --model models/x.json]
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
