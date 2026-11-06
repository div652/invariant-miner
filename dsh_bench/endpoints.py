"""Endpoint modes: which model server DSH talks to. One switch for every benchmark.

    --endpoint cao|trapi|vscode|vllm   (benchmarks' make_specs.py; default: $DSH_BENCH_ENDPOINT, else cao)

Each mode has a default model file in models/ and, where something must run locally, a start script in endpoints/.
See endpoints/README.md for what each mode needs and how its requests differ.
"""

import os
import secrets
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKEN_FILE = Path("~/.config/dsh-bench/endpoint.token").expanduser()

ENDPOINTS = {
    "cao": {"model": "luna-cao", "start": None,
            "about": "CAO gateway (GitHub Copilot seat) on 127.0.0.1:4141, Responses API; started outside this repo"},
    "trapi": {"model": "luna-trapi", "start": "endpoints/trapi/start.sh",
              "about": "TRAPI (Azure OpenAI, Entra ID) through a local token-refreshing proxy"},
    "vscode": {"model": "luna-vscode", "start": "endpoints/vscode/start.sh",
               "about": "GH Copilot Server VS Code extension (127.0.0.1:3141) through a local streaming shim"},
    "vllm": {"model": "qwen38-vllm", "start": "endpoints/vllm/serve_qwen38.sh",
             "about": "Qwen3.8-27B served by vLLM on this machine (agentic-evolution's serve_qwen38.sh settings)"},
}


def default_endpoint() -> str:
    endpoint = os.environ.get("DSH_BENCH_ENDPOINT", "cao")
    if endpoint not in ENDPOINTS:
        raise SystemExit(f"DSH_BENCH_ENDPOINT={endpoint!r}: choose one of {', '.join(ENDPOINTS)}")
    return endpoint


def model_for(endpoint: str | None, model: str | None = None) -> str:
    """The spec's `model` value: an explicit model file wins, else the endpoint's default model."""
    if model:
        return model
    endpoint = endpoint or default_endpoint()
    if endpoint not in ENDPOINTS:
        raise SystemExit(f"--endpoint {endpoint!r}: choose one of {', '.join(ENDPOINTS)}")
    return "{repo}/models/" + ENDPOINTS[endpoint]["model"] + ".json"


def local_token() -> str:
    """The shared secret between DSH and the local endpoint proxies (created on first use, mode 600)."""
    if not TOKEN_FILE.exists():
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        TOKEN_FILE.write_text(secrets.token_urlsafe(32) + "\n")
        TOKEN_FILE.chmod(0o600)
    return TOKEN_FILE.read_text().strip()


if __name__ == "__main__":
    for name, e in ENDPOINTS.items():
        print(f"{name:7s} models/{e['model']}.json  {e['about']}" + (f"  (start: {e['start']})" if e["start"] else ""))
