#!/usr/bin/env bash
# APEX-Agents 1.1 for dsh-bench-harness: the task packages (Harbor Hub), Mercor's 1.1 images by digest, ripgrep for
# DSH's glob/grep; then checks what a run needs that is not in the repo.
#
#   benchmarks/apex-agents/setup.sh          (after the repo's ./setup.sh)
#
# - tasks: mercor/apex-agents-1-1@1.1.1 from Harbor Hub (`harbor download`; Harbor 0.20.0: `uv tool install
#   harbor==0.20.0`), into $APEX_AGENTS_11_HUB (default ~/apex-agents-1.1-hub)/apex-agents-1-1, then checked against
#   tasks.sha256 (the 240 packages we analysed). The Hub copy, not Hugging Face: CHECKLIST.md, pitfall 2.
# - images: every world image and the verifier image the tasks name (public ECR, pinned by digest; ~16 GB for the
#   first world, ~0.1-0.5 GB for each further one; layers are shared). Pulled unmodified; nothing is built.
# - ripgrep $RG_VERSION (static musl build, checksum below) into work/apex-agents/bin: mounted read-only into the
#   world for DSH's glob/grep only (the world image has none; run_shell's PATH does not include it).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$HERE/../.." && pwd)"
HUB="${APEX_AGENTS_11_HUB:-$HOME/apex-agents-1.1-hub}"
TASKS="$HUB/apex-agents-1-1"
DATASET=mercor/apex-agents-1-1@1.1.1
RUNTIME="${RUNTIME:-podman}"
RG_VERSION=14.1.1
RG_SHA256=4cf9f2741e6c465ffdb7c26f38056a59e2a2544b51f7cc128ef28337eeae4d8e
RG_DIR="$REPO/work/apex-agents/bin"
log() { echo "[apex-agents setup] $*"; }
die() { echo "[apex-agents setup] ERROR: $*" >&2; exit 1; }

# --- tasks -------------------------------------------------------------------------------------------------------------
if [[ ! -d "$TASKS" ]]; then
  command -v harbor >/dev/null || die "harbor not found: uv tool install harbor==0.20.0"
  version="$(harbor --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  [[ "$version" == "0.20.0" ]] || die "Harbor 0.20.0 needed (found ${version:-none}): uv tool install harbor==0.20.0"
  log "downloading $DATASET into $HUB"
  harbor download "$DATASET" -o "$HUB"
fi
python3 "$HERE/fingerprint.py" --check "$TASKS" || die "the task packages in $TASKS are not the analysed 1.1.1 ones"

# --- images ------------------------------------------------------------------------------------------------------------
mapfile -t images < <(python3 - "$TASKS" <<'EOF'
import re, sys, yaml
from pathlib import Path
seen = set()
for d in sorted(Path(sys.argv[1]).iterdir()):
    seen.add(yaml.safe_load((d / "environment/docker-compose.yaml").read_text())["services"]["world"]["image"])
    seen.add(re.search(r"^FROM\s+(\S+)", (d / "tests/Dockerfile").read_text(), re.M).group(1))
print("\n".join(sorted(seen)))
EOF
)
have=0; pulled=0
for image in "${images[@]}"; do
  if "$RUNTIME" image exists "$image" 2>/dev/null; then have=$((have + 1)); continue; fi
  log "pulling ${image##*@sha256:} (${#images[@]} images in all)"
  for attempt in 1 2 3; do "$RUNTIME" pull -q "$image" >/dev/null && break; sleep 10; done
  "$RUNTIME" image exists "$image" || die "could not pull $image"
  pulled=$((pulled + 1))
done
log "images: ${#images[@]} named by the tasks ($have present, $pulled pulled)"

# --- ripgrep -----------------------------------------------------------------------------------------------------------
if [[ ! -x "$RG_DIR/rg" ]]; then
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  file="ripgrep-$RG_VERSION-x86_64-unknown-linux-musl.tar.gz"
  curl -fsSL -o "$tmp/$file" "https://github.com/BurntSushi/ripgrep/releases/download/$RG_VERSION/$file"
  echo "$RG_SHA256  $tmp/$file" | sha256sum -c --quiet - || die "ripgrep download does not match its checksum"
  tar -xzf "$tmp/$file" -C "$tmp"
  mkdir -p "$RG_DIR" && install -m 0755 "$tmp/ripgrep-$RG_VERSION-x86_64-unknown-linux-musl/rg" "$RG_DIR/rg"
fi
log "ripgrep: $("$RG_DIR/rg" --version | head -1)"

# --- what a run needs that is not in the repo --------------------------------------------------------------------------
missing=0
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
if not os.environ.get("DSH_BENCH_CAO_KEY_FILE"):
    print("[apex-agents setup] MISSING DSH_BENCH_CAO_KEY_FILE in ~/.config/dsh-bench/local.env: agent model (CAO) "
          "and the judge; or choose another --endpoint for the agent and DSH_BENCH_JUDGE_* for the judge")
    sys.exit(1)
EOF
log "done: ${TASKS} (240 tasks), images, ripgrep$([[ $missing == 1 ]] && echo '; fix the MISSING items above before running')"
