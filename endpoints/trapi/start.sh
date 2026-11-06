#!/usr/bin/env bash
# Start the TRAPI endpoint proxy in tmux `dsh-trapi` (port $DSH_BENCH_TRAPI_PORT, default 8031).
# Needs: an az login with TRAPI access under AZURE_CONFIG_DIR (default ~/.azure-scalt, the SC-ALT account), and
# TRAPI_BASE_URL (the instance's .../openai/v1 URL) in ~/.config/dsh-bench/trapi.env or the environment.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HOME/.config/dsh-bench/trapi.env"
[[ -f "$CONF" ]] && source "$CONF"
: "${TRAPI_BASE_URL:?set TRAPI_BASE_URL in $CONF (e.g. https://<trapi host>/<instance>/openai/v1)}"
export AZURE_CONFIG_DIR="${AZURE_CONFIG_DIR:-$HOME/.azure-scalt}"
user="$(az account show --query user.name -o tsv 2>/dev/null || true)"
[[ "$user" == sc-* ]] || { echo "az under $AZURE_CONFIG_DIR is '$user', not an SC-ALT (sc-...) account: az login there first" >&2; exit 1; }
PORT="${DSH_BENCH_TRAPI_PORT:-8031}"
if tmux has-session -t dsh-trapi 2>/dev/null; then echo "tmux dsh-trapi already running"; exit 0; fi
tmux new-session -d -s dsh-trapi "env TRAPI_BASE_URL='$TRAPI_BASE_URL' AZURE_CONFIG_DIR='$AZURE_CONFIG_DIR' python3 '$HERE/token_proxy.py' --port $PORT 2>&1 | tee -a '$HOME/.config/dsh-bench/trapi-proxy.log'"
for _ in $(seq 30); do curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break; sleep 1; done
curl -sf "http://127.0.0.1:$PORT/health" && echo || { echo "proxy did not come up: tmux attach -t dsh-trapi" >&2; exit 1; }
