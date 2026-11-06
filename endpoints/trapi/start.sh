#!/usr/bin/env bash
# Start the TRAPI endpoint proxy in tmux `dsh-trapi` (port $DSH_BENCH_TRAPI_PORT, default 8031).
# Needs YOUR settings in ~/.config/dsh-bench/local.env (template: local.env.example): TRAPI_BASE_URL (your instance's
# .../openai/v1 URL) and, optionally, AZURE_CONFIG_DIR (the Azure CLI config of your account with TRAPI access; az
# login there first; default ~/.azure).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HOME/.config/dsh-bench/local.env"
[[ -f "$CONF" ]] && set -a && source "$CONF" && set +a
: "${TRAPI_BASE_URL:?set TRAPI_BASE_URL in $CONF (template: local.env.example)}"
export AZURE_CONFIG_DIR="${AZURE_CONFIG_DIR:-$HOME/.azure}"
user="$(az account show --query user.name -o tsv 2>/dev/null || true)"
[[ -n "$user" ]] || { echo "no az login under $AZURE_CONFIG_DIR: run 'AZURE_CONFIG_DIR=$AZURE_CONFIG_DIR az login' first" >&2; exit 1; }
echo "TRAPI as $user (az config $AZURE_CONFIG_DIR)"
PORT="${DSH_BENCH_TRAPI_PORT:-8031}"
if tmux has-session -t dsh-trapi 2>/dev/null; then echo "tmux dsh-trapi already running"; exit 0; fi
mkdir -p "$HOME/.config/dsh-bench"
tmux new-session -d -s dsh-trapi "env TRAPI_BASE_URL='$TRAPI_BASE_URL' AZURE_CONFIG_DIR='$AZURE_CONFIG_DIR' python3 '$HERE/token_proxy.py' --port $PORT 2>&1 | tee -a '$HOME/.config/dsh-bench/trapi-proxy.log'"
for _ in $(seq 30); do curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break; sleep 1; done
curl -sf "http://127.0.0.1:$PORT/health" && echo || { echo "proxy did not come up: tmux attach -t dsh-trapi" >&2; exit 1; }
