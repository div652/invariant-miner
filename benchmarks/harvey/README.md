# Harvey LAB on dsh-bench-harness

[Harvey LAB](https://github.com/harveyai/harvey-labs) (Harvey, 2,010 legal tasks in 27 practice areas, pinned at
`4743403`) run with DSH as the agent. Work here is on the **250 firm-knowledge tasks** only (they share one document
store, `tasks/firm-knowledge/dms`). Harvey's own grader (`lab_core.evaluation`, pinned) scores the deliverables; DSH
replaces only Harvey's own harness, keeping its system prompt (adapted where DSH's tools differ) and its rule that
deliverables go to `output/`.

- [CHECKLIST.md](CHECKLIST.md): every decision (prompt, tools, image, budgets, grader) and each way we differ from
  Harvey's harness.
- [RESULTS.md](RESULTS.md): results so far (FK-250 and the comparison with the AHE campaigns' C0).

## Requirements

- Linux with rootless podman, git, python3, [uv](https://docs.astral.sh/uv/), node ^22.19 or >= 24 (`export NODE=...`:
  with an older node on PATH DSH does not start, and every task fails).
- Disk: ~2 GB for the image, ~0.5 GB for the firm-knowledge documents, little per task (documents are hard-linked).
- A model endpoint for the agent (`--endpoint cao|trapi|vscode|vllm`, see `endpoints/README.md`; default
  `models/luna-cao.json`) and CAO for the grader: `DSH_BENCH_CAO_KEY_FILE` in `~/.config/dsh-bench/local.env`.

## Setup

```bash
./setup.sh                    # DSH at its pin + patches, built into work/; image dsh-bench-base
benchmarks/harvey/setup.sh    # work/harvey-labs @ 4743403, image dsh-bench-harvey (Harvey's sandbox Dockerfile),
                              # Harvey's venv (grading), work/harvey-prepared (the adapted system prompt)
```

## Check the installation (no model calls)

```bash
export NODE=/path/to/node22
python3 benchmarks/harvey/test_harvey_write.py    # DSH's write with Harvey's output/ rule (scripted model)
python3 tests/test_splits.py                      # the split files below
```

## Splits

Two splits of the 250 firm-knowledge tasks are committed. They overlap (21 of the 60/20/20 test tasks are in AHE's
train + val), so use one or the other for a study, never both.

| `--tasks` | File | Tasks | What it is |
|---|---|---|---|
| `split:train` / `split:val` / `split:test` | `splits.json` | 150 / 50 / 50 | Our 60/20/20 split: task ids shuffled with a fixed seed (20261109, `make_splits.py`) |
| `split:trainval` | `splits.json` | 200 | train + val, for work with only a train and a test set |
| `ahe:train` / `ahe:val` / `ahe:test` | `splits-ahe-80-20-70.json` | 80 / 20 / 70 | The AHE campaigns' split (campaigns 12, 15, 23-27, 34), stratified by difficulty |
| `ahe:trainval` | `splits-ahe-80-20-70.json` | 100 | The 100 tasks AHE evolved on (= `c34-c0-100.txt`); report on `ahe:test` |

The AHE split is stratified by difficulty: AHE campaign 9b (gpt-5.6-sol high, Harvey's own harness, one run per task)
ranks the 250 tasks hardest first into 10 blocks of 25, and each block gives 8 train, 2 val, 7 test and 8 unused tasks
(80 unused in all). 9b's all-pass rate is 0.225 / 0.225 / 0.221 on train / val / test, against 0.224 on all 250. The
strata are kept for reference in `difficulty-9b.json`: each task's block, 9b scores, AHE split and 60/20/20 split.
`import_ahe_splits.py` rebuilds the AHE files from the AHE Harvey project (maintainers only).

Both split files record each task's task.json sha256; `make_specs.py` refuses a task whose file changed.
`python3 -m dsh_bench.splits benchmarks/harvey/splits-ahe-80-20-70.json --check` prints the counts per block;
`python3 -m dsh_bench.splits FILE test` lists a split's task ids.

## Run

```bash
export NODE=/path/to/node22
RUN=runs/hv-<name>
python3 benchmarks/harvey/make_specs.py --tasks ahe:test --out $RUN/specs [--endpoint cao | --model models/x.json]
benchmarks/harvey/run.sh $RUN/specs $RUN 10                  # 10 tasks at a time (default 4); re-run to resume
work/harvey-labs/.venv/bin/python benchmarks/harvey/grade.py $RUN
python3 benchmarks/harvey/compare_c0.py $RUN                 # optional: task by task against AHE's C0 (campaign 34)
```

- `--tasks` also takes a file of task ids, one per line (`firm-knowledge/tasks/001`), or any splits JSON as
  `FILE:NAME`. Defaults: max 200 steps (Harvey's `--max-turns`), 7,200 s per task.
- Per task in `$RUN/tasks/<task>/`: `run.json` (timings, finish reason), `answer.json`, the sessions, the workspace
  with `output/` (the only folder the grader reads) and a diff of what the agent changed.
- Grading (C0's settings): one judge gpt-5.6-sol at effort high, deliverable-filename helper claude-sonnet-5, via
  CAO; 10 criteria at a time, 2 tasks at a time, a task with grading errors graded again. Scores in
  `$RUN/grading/scores.json` and `scores.txt` (all-pass rate and mean criterion pass rate).
- `compare_c0.py` needs the AHE campaign artifacts (`--artifacts` or `$DSH_BENCH_C0_ARTIFACTS`); it pairs our runs
  with C0's 3 trials per task over the tasks both graded.

The FK-250 reference run (250 tasks, 10 at a time) took about 2 h 10 min. It had subagents on; they are off in the
harness since 2026-11-09, so its numbers are a baseline to rerun, not to compare a new run with.
