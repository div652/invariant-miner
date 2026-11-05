# dsh-bench-harness

DeepSeek Harness (DSH) as a benchmark-independent agent harness. The agent loop runs on the host; bash and
glob/grep run in a per-task container; each benchmark adds a patch file and a small adapter.

- [docs/DESIGN.md](docs/DESIGN.md): the decisions and how a run works.
- [docs/BENCHMARK_CHECKLIST.md](docs/BENCHMARK_CHECKLIST.md): what to check and record for every new benchmark.

## Layout

```
dsh_bench/  plugins/  images/base/  tests/   the core: knows nothing about any benchmark
docs/                                        design, new-benchmark checklist
benchmarks/<name>/                           everything one benchmark needs: image, patch, spec generator,
                                             runner, grader, its own plugins or tool bridges, CHECKLIST.md
```

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
```

## Setup

```bash
./setup.sh          # clones DSH @ c389f96, applies patches/deepseek-harness (7), builds it; builds the dsh-bench-base image
```

Needs Linux, git, node >= 22.19 with corepack, and rootless podman (or `RUNTIME=docker`).
