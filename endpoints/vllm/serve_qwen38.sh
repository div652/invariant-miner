#!/usr/bin/env bash
# Serve Qwen3.8-27B with vLLM on this machine: agentic-evolution's model_serve/serve_qwen38.sh settings
# (reasoning parser qwen3, auto tool choice, tool-call parser qwen3_coder, prefix caching, the chat template's
# reasoning effort as a default kwarg), with the shared local endpoint token as the API key.
#   (cd endpoints/vllm && uv sync)        # once: vllm==0.30.0 (agentic-evolution's pin)
#   endpoints/vllm/serve_qwen38.sh         # foreground; run it in tmux
# Env: MODEL_ID (default Qwen/Qwen3.8-27B-FP8, the served name models/qwen38-vllm.json uses; Qwen/Qwen3.8-27B is
# the BF16 checkpoint, agentic-evolution's default: serve it with a model file naming it), MODEL_PATH (a local
# snapshot; default: the HF cache), PORT (8000), MAX_MODEL_LEN (262144: models/qwen38-vllm.json's context window),
# GPU_MEMORY_UTILIZATION (0.90; lower it on a shared GPU), REASONING_EFFORT (xhigh|medium|low, the template's levels),
# TENSOR_PARALLEL_SIZE (all visible GPUs), MAX_NUM_SEQS.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VLLM="${VLLM:-$HERE/.venv/bin/vllm}"
[[ -x "$VLLM" ]] || { echo "no vllm at $VLLM: (cd $HERE && uv sync)" >&2; exit 1; }
MODEL_ID="${MODEL_ID:-Qwen/Qwen3.8-27B-FP8}"
MODEL_PATH="${MODEL_PATH:-$MODEL_ID}"
REASONING_EFFORT="${REASONING_EFFORT:-xhigh}"
case "$REASONING_EFFORT" in xhigh | medium | low) ;; *) echo "REASONING_EFFORT: xhigh, medium or low" >&2; exit 2 ;; esac
gpus="$(nvidia-smi --query-gpu=index --format=csv,noheader | wc -l)"
export VLLM_API_KEY="$(python3 -c "import sys; sys.path.insert(0, '$HERE/../..'); from dsh_bench.endpoints import local_token; print(local_token())")"
args=(serve "$MODEL_PATH" --served-model-name "$MODEL_ID" --host 127.0.0.1 --port "${PORT:-8000}"
      --tensor-parallel-size "${TENSOR_PARALLEL_SIZE:-$gpus}" --max-model-len "${MAX_MODEL_LEN:-262144}"
      --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.90}" --dtype auto --enable-prefix-caching
      --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_coder
      --default-chat-template-kwargs "{\"reasoning_effort\":\"$REASONING_EFFORT\"}")
[[ -n "${MAX_NUM_SEQS:-}" ]] && args+=(--max-num-seqs "$MAX_NUM_SEQS")
echo "Serving $MODEL_ID ($MODEL_PATH) on http://127.0.0.1:${PORT:-8000}/v1, effort $REASONING_EFFORT"
exec "$VLLM" "${args[@]}"
