#!/usr/bin/env bash
# Harvey LAB for dsh-bench-harness: the pinned harvey-labs checkout, its sandbox image, and its Python env (grading).
#
#   benchmarks/harvey/setup.sh        (after the repo's ./setup.sh)
#
# - work/harvey-labs: harveyai/harvey-labs @ $PIN (tasks, the grader `lab_core.evaluation`, the sandbox Dockerfile).
#   Hard-linked task documents are made read-only in place (dsh_bench.launch stage method "hardlink").
# - image dsh-bench-harvey: harvey-labs' own lab_core/sandbox/Dockerfile at the pin, under our tag (never a locally
#   built lab-sandbox of unknown age).
# - work/harvey-labs/.venv: harvey-labs' locked environment (uv sync --locked), used by grade.py.
# - work/harvey-prepared: the adapted system prompt and skills (prepare.py).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../.." && pwd)"
PIN=4743403f52c1c1db75f3feb1c8f91fae1bd30296
LAB="$REPO/work/harvey-labs"
RUNTIME="${RUNTIME:-podman}"
if [[ ! -d "$LAB/.git" ]]; then
  git init -q "$LAB" && git -C "$LAB" remote add origin https://github.com/harveyai/harvey-labs.git
  git -C "$LAB" fetch -q --depth 1 origin "$PIN" && git -C "$LAB" checkout -q -B pinned FETCH_HEAD
fi
[[ "$(git -C "$LAB" rev-parse HEAD)" == "$PIN" ]] || { echo "work/harvey-labs is not at $PIN" >&2; exit 1; }
"$RUNTIME" build -q -t dsh-bench-harvey "$LAB/lab_core/sandbox"
(cd "$LAB" && env -u VIRTUAL_ENV uv sync --locked -q)
python3 "$HERE/prepare.py"
echo "[harvey setup] done: work/harvey-labs @ ${PIN:0:9}, image dsh-bench-harvey, venv, work/harvey-prepared"
