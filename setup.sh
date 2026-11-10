#!/usr/bin/env bash
# Build the DeepSeek Harness (DSH) used by dsh-bench-harness from the public upstream plus the patch series.
#
#   deepseek-harness  https://github.com/deepseek-ai/deepseek-harness  @ c389f96  + patches/deepseek-harness (9)
#
# Usage: ./setup.sh [WORK_DIR]     (default: ./work; the checkout goes to WORK_DIR/deepseek-harness)
# Needs: git, node >= 22.19 (or >= 24) with corepack. Env: NODE=/path/to/node to pick a node binary.
# Also builds the sandbox image images/base as dsh-bench-base (podman; RUNTIME=docker to use docker).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mkdir -p "${1:-$HERE/work}" && cd "${1:-$HERE/work}" && pwd)"
DSH_URL=https://github.com/deepseek-ai/deepseek-harness.git
DSH_PIN=c389f96bf3a9b6807cb71ed6bdad5849be0df6d8

log() { echo "[setup] $*"; }
die() { echo "[setup] ERROR: $*" >&2; exit 1; }

checkout() {  # url pin dir patches-dir
  local url="$1" pin="$2" dir="$3" patches="$4"
  if [[ ! -d "$dir/.git" ]]; then
    log "cloning $url @ ${pin:0:7} into $dir"
    git init -q "$dir"
    git -C "$dir" remote add origin "$url"
    git -C "$dir" fetch -q --depth 1 origin "$pin"
    git -C "$dir" checkout -q -B patched FETCH_HEAD
  fi
  # A checkout from an earlier setup carries the patch series as it was then. If its commits are the first patches of
  # the series (same patch ids), apply only the patches added since; any other local commits: leave it as it is.
  local -a files commits
  mapfile -t files < <(ls "$patches"/*.patch)
  mapfile -t commits < <(git -C "$dir" rev-list --reverse "$pin"..HEAD)
  local i applied=${#commits[@]}
  for (( i = 0; i < applied; i++ )); do
    if (( i >= ${#files[@]} )) || [[ "$(git patch-id --stable < "${files[i]}" | cut -d' ' -f1)" != \
          "$(git -C "$dir" show "${commits[i]}" | git patch-id --stable | cut -d' ' -f1)" ]]; then
      log "$dir carries commits on top of ${pin:0:7} that are not this patch series; leaving it as it is"
      return
    fi
  done
  if (( applied == ${#files[@]} )); then
    log "$dir already carries all ${#files[@]} patches"
    return
  fi
  log "applying $(( ${#files[@]} - applied )) of ${#files[@]} patches to $dir"
  git -C "$dir" -c user.name=setup -c user.email=setup@localhost am -q --3way --committer-date-is-author-date \
    "${files[@]:applied}"
}

checkout "$DSH_URL" "$DSH_PIN" "$WORK/deepseek-harness" "$HERE/patches/deepseek-harness"

# --- build DSH -------------------------------------------------------------------------------------------------------
NODE_BIN="$(command -v "${NODE:-node}" || true)"
[[ -n "$NODE_BIN" ]] || die "node not found (need >= 22.19); set NODE=/path/to/node"
NODE_VERSION="$("$NODE_BIN" -p 'process.versions.node')"
IFS=. read -r major minor _ <<< "$NODE_VERSION"
{ [[ $major -eq 22 && $minor -ge 19 ]] || [[ $major -ge 24 ]]; } || die "node $NODE_VERSION is too old (need ^22.19 || >=24)"
export PATH="$(dirname "$NODE_BIN"):$PATH"
log "node $NODE_VERSION ($NODE_BIN)"

DSH="$WORK/deepseek-harness"
SHIMS="$(mktemp -d)"
trap 'rm -rf "$SHIMS"' EXIT
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0 CI=true
corepack enable --install-directory "$SHIMS" pnpm
export PATH="$SHIMS:$PATH"
(cd "$DSH" && pnpm install --frozen-lockfile && pnpm run build)
[[ -f "$DSH/apps/cli/lib/bin.js" ]] || die "DSH build finished without apps/cli/lib/bin.js"

# --- sandbox image ---------------------------------------------------------------------------------------------------
RUNTIME="${RUNTIME:-podman}"
"$RUNTIME" build -q -t dsh-bench-base "$HERE/images/base"

log "done"
log "  harness CLI : $DSH/apps/cli/lib/bin.js"
log "  base image  : dsh-bench-base ($RUNTIME)"
