# dsh-bench-harness

DeepSeek Harness (DSH) as a benchmark-independent agent harness. The agent loop runs on the host; bash and
glob/grep run in a per-task container; each benchmark adds a patch file and a small adapter.

- [docs/DESIGN.md](docs/DESIGN.md): the decisions and how a run works.
- [docs/BENCHMARK_CHECKLIST.md](docs/BENCHMARK_CHECKLIST.md): what to check and record for every new benchmark.

Status: `plugins/sandbox-podman` written and passing `tests/test_isolation.py` (19/19). The launcher, the other core
plugins and the first benchmark adapter are not written yet.

## Tests

```bash
python3 tests/test_isolation.py   # DSH + sandbox-podman + a scripted model (tests/scripted_model.py), no real model needed
```

## Setup

```bash
./setup.sh          # clones DSH @ c389f96, applies patches/deepseek-harness (7), builds it; builds the dsh-bench-base image
```

Needs Linux, git, node >= 22.19 with corepack, and rootless podman (or `RUNTIME=docker`).
