# APEX-Agents 1.1 on dsh-bench-harness

[APEX-Agents 1.1](https://www.mercor.com/blog/introducing-apex-agents-1-1/) (Mercor, 240 professional-services tasks
in 31 simulated worlds) run with DSH as the agent, on **Mercor's own 1.1 images, unmodified**: each task's world image
(its files and 9 apps behind an MCP gateway) and Mercor's grader image. DSH replaces only Mercor's agent; this harness
replaces Harbor, Mercor's runner, so that DSH's own tools can work inside the world.

- [CHECKLIST.md](CHECKLIST.md): every decision, what changed from 1.0, pitfalls found in Mercor's 1.1 delivery
  (and what we do about each), each way we differ from Mercor's own setup.
- [RESULTS.md](RESULTS.md): the full run (Luna max: Pass@1 34.2%).
- APEX-Agents 1.0 (480 tasks, Archipelago f8e41cb; version 1 of this work, tag `apex-agents-v1`): kept, runnable, in
  `benchmarks/apex-agents-1.0/`.

## Requirements

- Linux with rootless podman, python3 with PyYAML, node ^22.19 or >= 24, [uv](https://docs.astral.sh/uv/) (to install
  Harbor, used only to download the tasks).
- Disk: ~25 GB for the images (one world image is 16 GB; the other 30 share its layers), ~1 GB per task in flight
  (graded runs are compacted to what the agent changed).
- A model endpoint for the agent (`--endpoint cao|trapi|vscode|vllm`, see `endpoints/README.md`) and an
  OpenAI-compatible endpoint for the judge (default: CAO, `gemini-3.8-flash`, reasoning effort high).

## Setup

```bash
./setup.sh                                  # DSH at its pin + patches (repo root)
uv tool install harbor==0.20.0              # only for `harbor download`
benchmarks/apex-agents/setup.sh         # tasks (Harbor Hub mercor/apex-agents-1-1@1.1.1, checked against
                                            # tasks.sha256), Mercor's 32 images by digest, ripgrep; then checks
```

Tasks go to `~/apex-agents-1.1-hub/apex-agents-1-1` (`APEX_AGENTS_11_HUB` to change the parent directory; run_task.py
reads `APEX_AGENTS_11_TASKS` or `--tasks-dir`). The Hub copy, not Hugging Face's: CHECKLIST.md, pitfall 2.

Settings in `~/.config/dsh-bench/local.env` (template: `local.env.example`): `DSH_BENCH_CAO_KEY_FILE` (agent via CAO
and the judge); optionally `DSH_BENCH_JUDGE_BASE_URL` / `DSH_BENCH_JUDGE_KEY_FILE` for another judge endpoint. No
other keys: 1.1 has no internet apps.

## Check the installation

```bash
export NODE=/path/to/node22
python3 tests/test_attach_user.py                     # DSH's tools as a container user with a umask
python3 tests/test_tool_limits.py                     # output cap (Mercor's rule) and per-call timeout
python3 benchmarks/apex-agents/test_plumbing.py   # one real task end to end with a scripted model: world, 74 world
                                                      # tools + DSH's, fence, limits, snapshots, trajectory (no model calls)
python3 benchmarks/apex-agents/check_gold.py --out runs/apex11-gold --per-type 1
                                                      # judge calls: the experts' outputs through the whole grading path
```

## Splits

Two shared splits of the 240 tasks, both stratified by job, task slugs listed (the files are the splits;
`make_splits.py` made both, seed 20261109). Pick one per study:

| `--tasks` | File | Tasks | Use |
|---|---|---|---|
| `split:train` / `split:val` / `split:test` | `splits.json` | 144 / 48 / 48 (48 / 16 / 16 per job) | 60/20/20 |
| `split:trainval` + `split:test` | `splits.json` | 192 + 48 | the original 80:20 train : test |
| `third:train` + `third:test` | `splits-third.json` | 80 + 160 (27 / 26 / 27 and 53 / 54 / 53 per job) | 1/3 train : 2/3 test |

The 1/3 : 2/3 split is nested in the 60/20/20 one: its 80 train tasks are drawn from `splits.json`'s 144 train tasks,
so every `splits.json` val and test task is a test task here, and a harness tuned on `third:train` has never seen them.
It has no val (`third:val` is empty; `third:trainval` = `third:train`).

The APEX-Agents 1.0 split (`benchmarks/apex-agents-1.0/splits.json`) follows `splits.json`: each 1.1 task's 1.0 original
(`v1_task_id`) is in the same split. `--dry-run` lists the selected tasks; `python3 -m dsh_bench.splits FILE --check`
prints the counts per job.

## Run

```bash
export NODE=/path/to/node22
python3 benchmarks/apex-agents/run_all.py --tasks all --out runs/apex11-<name> [--jobs 12] [--endpoint cao | --model models/x.json]
```

- `--tasks all` or a file of task slugs (`smoke-3.txt`). Tasks run in parallel (default 12; 4 worlds booting at a time)
  and are graded as they finish. Re-running the same command resumes.
- Per task in `runs/<name>/tasks/<slug>/`: `run.json` (timings, finish reason, `infra_error` if a container step
  failed), `agent/` (DSH's run), `trajectory.json` (ATIF, what Mercor's grader reads), `world-logs/` (the world's boot
  log; `changes.tar.gz` + `changes.json` after grading: what the agent changed), `grading/grades.json` (score, all
  criteria met, each criterion with the judge's rationale) and Mercor's verifier outputs in `grading/verifier/`.
- `summary.md` / `summary.json`: Pass@1 (share of tasks with every criterion met), mean score, by job and output.
- A run at the 100-step limit is graded (as Mercor's); a run stopped by the 3 h timeout or an error scores 0.
  Infrastructure failures (world boot, DSH start, the final snapshot) are retried once in a fresh world.
- One task by hand: `run_task.py --task <slug> --out <dir>`, then `grade.py <dir>` (`--regrade`, `--keep-snapshots`).
