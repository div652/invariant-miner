#!/usr/bin/env bash
# APEX-Agents for dsh-bench-harness: the pinned Archipelago checkout, its environment image plus our layer, and the
# grader's Python env.
#
#   benchmarks/apex-agents/setup.sh [--rebuild]       (after the repo's ./setup.sh)
#
# - work/archipelago: Mercor-Intelligence/archipelago @ $PIN (environment, MCP app servers, grader, HF example config),
#   from upstream or, if upstream dropped the commit, from the unmodified copy div652/archipelago-pinned.
# - image dsh-bench-apex-agents-env:<pin>: Archipelago's environment/Dockerfile at the pin, unmodified, under our tag
#   (~12 GB; first build ~10 min, needs network for apt/uv/npm).
# - image dsh-bench-apex-agents:<pin>: our layer (benchmarks/apex-agents/Dockerfile): code_exec's package mirror and
#   ripgrep (CHECKLIST.md, change 2). Images that already exist are kept unless --rebuild (a rebuild reuses podman's
#   layer cache).
# - work/archipelago/grading/.venv: the grader's locked environment (uv sync --locked), used by grade.py.
# Then checks what a run needs and is not in the repo: the dataset, node, your local.env settings.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../.." && pwd)"
PIN=f8e41cbb6f6158a0f3fbe81a74ecfdcf70fbfcc3
ARCH="$REPO/work/archipelago"
RUNTIME="${RUNTIME:-podman}"
BASE="dsh-bench-apex-agents-env:${PIN:0:7}"
IMAGE="dsh-bench-apex-agents:${PIN:0:7}"
REBUILD=0; [[ "${1:-}" == "--rebuild" ]] && REBUILD=1
log() { echo "[apex-agents setup] $*"; }

# Upstream rewrites its history on every sync from Mercor's internal repo (main is one new commit each time), so the
# pin is fetched by hash; a plain clone would not contain it, and upstream may garbage-collect it. Fallback:
# div652/archipelago-pinned, an unmodified copy of Mercor's commit (Mercor's work, not ours; private, ask for access).
# ARCHIPELAGO_URL replaces upstream as the first source.
UPSTREAM="${ARCHIPELAGO_URL:-https://github.com/Mercor-Intelligence/archipelago.git}"
MIRROR="https://github.com/div652/archipelago-pinned.git"
if [[ ! -d "$ARCH/.git" ]]; then
  git init -q "$ARCH"; got=""
  for url in "$UPSTREAM" "$MIRROR"; do
    log "fetching archipelago @ ${PIN:0:9} from $url"
    if GIT_TERMINAL_PROMPT=0 git -C "$ARCH" fetch -q --depth 1 "$url" "$PIN"; then got="$url"; break; fi
  done
  [[ -n "$got" ]] || { rm -rf "$ARCH"; echo "cannot fetch $PIN from $UPSTREAM or $MIRROR (set ARCHIPELAGO_URL)" >&2; exit 1; }
  git -C "$ARCH" checkout -q -B pinned FETCH_HEAD && git -C "$ARCH" remote add origin "$got"
fi
[[ "$(git -C "$ARCH" rev-parse HEAD)" == "$PIN" ]] || { echo "work/archipelago is not at $PIN" >&2; exit 1; }

image_exists() { "$RUNTIME" image exists "$1" 2>/dev/null || "$RUNTIME" image inspect "$1" >/dev/null 2>&1; }
if [[ $REBUILD == 1 ]] || ! image_exists "$BASE"; then
  log "building $BASE from Archipelago's environment/Dockerfile (unmodified)"
  (cd "$ARCH" && "$RUNTIME" build -q --format docker -f environment/Dockerfile -t "$BASE" .)
fi
if [[ $REBUILD == 1 ]] || ! image_exists "$IMAGE"; then
  log "building $IMAGE (our layer)"
  "$RUNTIME" build -q --format docker --build-arg "BASE=$BASE" -t "$IMAGE" "$HERE"
fi

log "grader environment (work/archipelago/grading/.venv)"
(cd "$ARCH/grading" && env -u VIRTUAL_ENV uv sync --locked -q)

# --- what the run needs that is not in the repo ------------------------------------------------------------------------
missing=0
DATASET="${APEX_AGENTS_DATASET:-$HOME/apex-agents-data}"
if [[ ! -f "$DATASET/tasks_and_rubrics.json" ]] || ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$DATASET/tasks_and_rubrics.json" 2>/dev/null; then
  log "MISSING dataset at $DATASET: accept the terms of huggingface.co/datasets/mercor/apex-agents, log in (hf auth login),"
  log "  then: hf download mercor/apex-agents --type dataset --local-dir $DATASET   (9 GB; pass --dataset if elsewhere)"
  missing=1
fi
NODE_BIN="${NODE:-$(command -v node || true)}"
if [[ -z "$NODE_BIN" ]] || ! "$NODE_BIN" -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a>=24||(a===22&&b>=19)?0:1)'; then
  log "MISSING node ^22.19 or >= 24: set NODE=/path/to/node when running (DSH runs on node)"
  missing=1
fi
python3 - "$REPO" <<'EOF' || missing=1
import os, sys
sys.path.insert(0, sys.argv[1])
from dsh_bench.endpoints import load_local_env
load_local_env()
need = {"DSH_BENCH_CAO_KEY_FILE": "agent model and judge (CAO); or choose another --endpoint for the agent",
        "DSH_BENCH_FMP_KEY_FILE": "FMP app (banking worlds 244/246 only)",
        "DSH_BENCH_EDGAR_USER_AGENT": "Edgar SEC app (banking worlds 244/246 only)"}
bad = [k for k in need if not os.environ.get(k)]
for k in bad:
    print(f"[apex-agents setup] MISSING {k} in ~/.config/dsh-bench/local.env: {need[k]} (see local.env.example)")
sys.exit(1 if "DSH_BENCH_CAO_KEY_FILE" in bad else 0)
EOF
log "done: work/archipelago @ ${PIN:0:9}, images $BASE + $IMAGE, grader venv$([[ $missing == 1 ]] && echo '; fix the MISSING items above before running')"
