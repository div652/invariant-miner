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

## Checking traces for harness, path and grader problems

`python3 benchmarks/harvey/check_traces.py RUN_DIR [...]` sorts every problem in a run's traces that is not the
agent's legal work into harness components (A), deliverable paths (B) and grader access (C); see its docstring.
Swept 2026-11-15 over the three Luna-high base runs, the four ask-tools runs (7 x 250 tasks) and the harvey-mixed
smokes (task runs affected per run, range over the seven 250-task runs):

| Finding | Task runs per 250 | What happens |
|---|---|---|
| grader could not open or find a deliverable, grading errors, symlinks | 0 | none anywhere |
| expected deliverable missing from output/ at the end | 0 | none anywhere |
| `response.md` looked up in the workspace root instead of output/ (`write` routes it to output/) | 8-42 | 164 failed calls in 156 task runs, every one followed by a successful access of `output/response.md` |
| saved full result of a capped glob/grep/bash unreadable (`/tmp/dsh-spill-*`) | 79-122 | known limit of the base harness |
| file the agent wrote to `/tmp` in the container, then tried to `read` (read runs on the host, sees only the workspace) | 22-51 | 959 refused reads in all |
| grep's raw ripgrep output over DSH's 20 MB buffer: the call fails | 4-15 | 148 failed calls. **Fixed 2026-11-15**: patch.yml raises the buffer to 500 MB (re-run sizes: median 81 MB, max 1 GB; Node's string limit caps it); test_search_limits.py |
| glob/grep stopped by the 30 s search timeout | 0-16 | 16 task runs, all in ask-open r1. **Fixed 2026-11-15**: patch.yml sets 600 s (bash's cap) |
| bash calls hitting their timeout | 47-62 | mostly agent-chosen (189 at 120 s, 34 at 1 s); 23 at the 60 s default. Harvey's own bash is stricter: 60 s fixed (`--shell-timeout`), no per-call timeout, no background jobs |
| `read` of an office file refused ("binary file") / edit of a file not read first | 12-22 / 0-4 | DSH rules, agent recovers |
| `markitdown` on a .docx | 1 call | the image's markitdown lacks its docx extra (pptx/xlsx work; parse-doc works for all); the prompt names markitdown as an alternative |

The two harvey-mixed smokes (with and without skills) show none of the A-C failures, only the two DSH rules.

Compared with Harvey's own tools (lab_core/harness/tools.py at the pin): Harvey has the /tmp gap too (its read / write /
edit refuse paths outside /workspace); it has no saved results but cuts glob at 100 and grep at 250 silently; its
glob/grep have no output buffer or timeout (so the two fixed rows were ours); its read and edit look for a relative
path in output/ as well, so the response.md slips are ours (harvey-write routes only `write`); and its prompt never
names markitdown (our prepare.py does).
