# Model endpoints

Choose with `--endpoint cao|trapi|vscode|vllm` on a benchmark's `make_specs.py` (default `$DSH_BENCH_ENDPOINT`, else
`cao`), or name a model file with `--model`. How to bring each endpoint up: [endpoints/README.md](../endpoints/README.md).

| File | Endpoint | Model and settings |
|---|---|---|
| `luna-cao.json` | `cao` (default) | GPT-5.6 Luna on CAO directly (`127.0.0.1:4141/v1`, Responses API): the AHE campaign 34 request shape (reasoning summaries on, encrypted reasoning sent back each turn, 128K output cap, no temperature) at effort **high** (user's choice, 2026-11-06; c34 itself used the provider default, medium). |
| `luna-trapi.json` | `trapi` | GPT-5.6 Luna deployment `gpt-5.6-luna_2026-07-09` through the TRAPI token proxy (`127.0.0.1:8031/v1`), same request shape and effort as `luna-cao`. Context 262,144 (TRAPI's limit for the deployment is not recorded here). |
| `luna-vscode.json` | `vscode` | GPT-5.6 Luna through the GH Copilot Server VS Code extension, via the streaming shim (`127.0.0.1:8032/v1`), Chat Completions. The extension drops reasoning, reports zero usage, and turns system messages into user messages. |
| `qwen38-vllm.json` | `vllm` | Qwen3.8-27B (FP8 checkpoint, served as `Qwen/Qwen3.8-27B-FP8`) on local vLLM (`127.0.0.1:8000/v1`), agentic-evolution's JobBench Qwen3.8 route: thinking on (chat-template kwargs), 262,144 context, 32,768 output cap, a response cut at the cap regenerated up to 3 times (`dsh_rows`: agent-loop `maxTokensRetries`). |
| `luna-proxy-high.json` | (record) | The JobBench parity run of 2026-11-05: Luna through agentic-evolution's model_serve proxy on :8018, effort high, 262K context, 32K output. |

The local endpoints (trapi, vscode, vllm) share one token, `~/.config/dsh-bench/endpoint.token` (mode 600, created on
first use): DSH sends it, the proxy or vLLM checks it, and no real key reaches DSH.
