# Endpoints

One switch picks the model server for a whole run: `--endpoint cao|trapi|vscode|vllm` on a benchmark's
`make_specs.py` (default `$DSH_BENCH_ENDPOINT`, else `cao`). Each mode's model file is in [models/](../models/README.md).
Check any mode end to end with `python3 -m dsh_bench.endpoint_check --endpoint <mode>` (one tiny DSH task).

| Mode | What runs | Bring it up | Notes |
|---|---|---|---|
| `cao` | CAO gateway on `127.0.0.1:4141` (GitHub Copilot seat) | outside this repo (the CAO gateway setup); key in `~/cao/profile/.gateway-key` | Responses API, reasoning summaries + encrypted reasoning, real usage |
| `trapi` | `endpoints/trapi/token_proxy.py` on `127.0.0.1:8031` -> TRAPI | `endpoints/trapi/start.sh` (tmux `dsh-trapi`) | Needs `az login` with TRAPI access under `AZURE_CONFIG_DIR` (default `~/.azure-scalt`, the SC-ALT account) and `TRAPI_BASE_URL` in `~/.config/dsh-bench/trapi.env`. The proxy refreshes the Entra token (~1.5 h lifetime) itself. TRAPI has no model catalog and answers an unknown deployment with 429, so check a new deployment name with `endpoint_check` first. Limits: 1,000 requests and 1M tokens per minute per deployment. |
| `vscode` | `endpoints/vscode/stream_shim.py` on `127.0.0.1:8032` -> GH Copilot Server extension on `127.0.0.1:3141` | the extension must be serving in a VS Code window on this machine (server-hosted instance: `~/copilot-host/start-copilot-host.sh`, then "GH Copilot Server: Start Server"); then `endpoints/vscode/start.sh` (tmux `dsh-vscode`) | Chat Completions only and no streaming: the shim sends `stream: false` and re-streams the reply. The extension has no auth (keep it on loopback), drops reasoning, reports zero usage, turns system messages into user messages, and honours the effort only with the host's local patch. |
| `vllm` | vLLM on `127.0.0.1:8000` serving Qwen3.8-27B | `(cd endpoints/vllm && uv sync)` once, then `endpoints/vllm/serve_qwen38.sh` in tmux | agentic-evolution's `serve_qwen38.sh` settings (vllm 0.30.0, qwen3 reasoning parser, qwen3_coder tool parser, prefix caching, chat-template reasoning effort, default xhigh). Weights from the HF cache or `MODEL_PATH`; on a shared 80 GB GPU use `MODEL_ID=Qwen/Qwen3.8-27B-FP8` and a lower `GPU_MEMORY_UTILIZATION`. API key = the shared local token. |

Live checks (2026-11-06, `dsh_bench.endpoint_check`): cao, trapi (redmond/interactive, `gpt-5.6-luna_2026-07-09`),
vscode (extension on the server-hosted VS Code; the first request needs the one-time "GH Copilot Server wants to
access the language models" consent, clicked in the noVNC viewer; the extension then logs `reasoning={"effort":"high"}`)
and vllm (Qwen3.8-27B-FP8) all completed the check task.

All local endpoints use one shared token, `~/.config/dsh-bench/endpoint.token` (mode 600). The proxies listen on
127.0.0.1 only, so the task containers (which cannot reach host loopback) cannot call them.
