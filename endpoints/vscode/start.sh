#!/usr/bin/env bash
# Start the VS Code endpoint shim in tmux `dsh-vscode` (port $DSH_BENCH_VSCODE_PORT, default 8032).
# Needs the GH Copilot Server extension listening on 127.0.0.1:3141 in a VS Code window on this machine (see
# endpoints/README.md: the server-hosted instance is ~/copilot-host/start-copilot-host.sh plus "GH Copilot Server:
# Start Server"). This script only checks it and lists the models it serves.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UP="${VSCODE_COPILOT_URL:-http://127.0.0.1:3141/v1}"
models="$(curl -sf -m 10 "$UP/models" | python3 -c 'import json,sys; print(" ".join(m["id"] for m in json.load(sys.stdin)["data"]))' || true)"
[[ -n "$models" ]] || { echo "no GH Copilot Server at $UP (or it lists no models): start it in VS Code first" >&2; exit 1; }
echo "extension models: $models"
PORT="${DSH_BENCH_VSCODE_PORT:-8032}"
if tmux has-session -t dsh-vscode 2>/dev/null; then echo "tmux dsh-vscode already running"; exit 0; fi
tmux new-session -d -s dsh-vscode "python3 '$HERE/stream_shim.py' --port $PORT --upstream '$UP' 2>&1 | tee -a '$HOME/.config/dsh-bench/vscode-shim.log'"
for _ in $(seq 20); do curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break; sleep 1; done
curl -sf "http://127.0.0.1:$PORT/health" && echo
