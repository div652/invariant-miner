# dsh-bench-harness

DeepSeek Harness (DSH) as a benchmark-independent agent harness. The agent loop runs on the host; bash and
glob/grep run in a per-task container; each benchmark adds a patch file and a small adapter.

- [docs/DESIGN.md](docs/DESIGN.md): the decisions and how a run works.
- [docs/BENCHMARK_CHECKLIST.md](docs/BENCHMARK_CHECKLIST.md): what to check and record for every new benchmark.

## Where things live

The harness itself, DeepSeek Harness (DSH: the agent loop, ~90 plugins, all the tools), is **not in this repo**.
`setup.sh` clones it from upstream at a pinned commit into `work/` (gitignored), applies `patches/`, and builds it.
This repo holds what goes on top of it:

```
upstream deepseek-ai/deepseek-harness @ c389f96          the harness
  + patches/deepseek-harness/   7 patches (see below)    -> built into work/deepseek-harness by setup.sh
  + harness/core.patch.yml      the harness configuration used for every run: which DSH plugins are on or off,
                                the isolation settings, and our three plugins
  + plugins/                    our DSH plugins: sandbox-podman (commands run in the task container),
                                benchmark-limits (steps / timeout / temperature), final-answer (final_answer tool)
  + images/base/                the minimal container image bash runs in
dsh_bench/launch.py             the runner AROUND DSH (not the harness): stage the workspace, start the container,
                                run DSH with the patch files, collect the outputs
tests/                          isolation, launcher and layout tests (scripted model, no real model needed)
docs/                           design, new-benchmark checklist
benchmarks/<name>/              everything one benchmark adds: image, patch file, task specs, runner, grader,
                                CHECKLIST.md
```

**What configures DSH for one run**: the `headless` profile, then three layers of patch files, each overriding the
previous: `harness/core.patch.yml` (same for every run) -> the run's generated `run.patch.yml` (the model, the
benchmark's system prompt, disabled rows, MCP servers) -> the benchmark's `benchmarks/<name>/*.yml`. A run directory
keeps its `run.patch.yml`, and `run.json` records every patch file with its sha256.

**The 7 DSH patches** (from `agentic-evolution`, so the build is the one their results came from):

| Patch | Kind | Used here |
|---|---|---|
| 0001 `workspace-isolated` sandbox mode | code | yes: confines the file tools to the workspace |
| 0002 PDF text in `web_fetch` | code | when a benchmark enables web tools |
| 0003 snapshots for 0002 | tests | no runtime effect |
| 0004 README: private fork, JobBench profile | docs | no runtime effect |
| 0005 README: clone URL | docs | no runtime effect |
| 0006 `DSH_SANDBOX_DISABLE_RUNNERS` | code | no: the local sandbox it configures is replaced by `sandbox-podman` |
| 0007 `maxTokensRetries` | code | off by default (0) |

None changes behaviour for one benchmark only; 0004 mentions JobBench in README text.

## Endpoints

One switch picks the model server: `--endpoint cao|trapi|vscode|vllm` on a benchmark's `make_specs.py` (default
`$DSH_BENCH_ENDPOINT`, else `cao`). Modes, how to start each one and how their requests differ:
[endpoints/README.md](endpoints/README.md); model settings: [models/README.md](models/README.md). Check a mode with
`python3 -m dsh_bench.endpoint_check --endpoint <mode>`.

## Rules

- **One branch, one core.** Every benchmark runs on the same core, so results from different benchmarks are
  comparable. Each run records the core commit (`harness_commit` in `run.json`); core versions are tagged `core-vN`.
- **Dependency rule:** benchmarks use the core; the core never refers to a benchmark (`tests/test_layout.py`).
- **New benchmark:** develop on a branch `bench/<name>` and merge into `main` once its `CHECKLIST.md` is complete
  and its smoke run passes.

Status (core-v0): `sandbox-podman`, `final-answer`, `benchmark-limits` and the launcher are written and tested.
Benchmarks: `jobbench` (smoke run done; train-20 comparison with the reference harness in progress).

## Tests

```bash
python3 tests/test_layout.py      # the core mentions no benchmark
python3 tests/test_isolation.py   # DSH + sandbox-podman + a scripted model (tests/scripted_model.py), no real model needed
python3 tests/test_launch.py      # the launcher end to end with the scripted model: the four standard outputs
python3 tests/test_vscode_shim.py # the VS Code endpoint shim against a fake GH Copilot Server extension
```

## Setup

```bash
./setup.sh          # clones DSH @ c389f96, applies patches/deepseek-harness (7), builds it; builds the dsh-bench-base image
```

Needs Linux, git, node >= 22.19 with corepack, and rootless podman (or `RUNTIME=docker`).
