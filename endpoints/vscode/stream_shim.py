"""VS Code endpoint: a local shim between DSH and the GH Copilot Server VS Code extension (127.0.0.1:3141).

    endpoints/vscode/start.sh          (runs this in tmux `dsh-vscode`)

The extension (gh-copilot-server-model-access skill) speaks Chat Completions only, has no authentication, and does
not stream: it returns one JSON response and needs `"stream": false`. DSH always streams. So the shim
- checks the shared local token (the extension itself has none: it must stay on loopback);
- forwards /v1/chat/completions with `stream: false` (and without `stream_options`);
- turns the JSON response into the SSE chunks a streaming client expects (role + content, tool calls, finish reason,
  usage), then `data: [DONE]`.
Everything else (GET /v1/models) passes through. Known extension behaviour: system/developer messages become user
messages, usage is always 0, reasoning is not returned, the effort is honoured only with the host's local patch.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from proxy_base import Upstream, serve  # noqa: E402


def sse(handler, payload: dict) -> None:
    handler.wfile.write(b"data: " + json.dumps(payload).encode() + b"\n\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("DSH_BENCH_VSCODE_PORT", 8032)))
    parser.add_argument("--upstream", default=os.environ.get("VSCODE_COPILOT_URL", "http://127.0.0.1:3141/v1"))
    parser.add_argument("--log-bodies", type=Path)
    args = parser.parse_args()
    def prepare(method, path, headers, body):
        if method == "POST" and path.rstrip("/").endswith("/chat/completions") and body:
            request = json.loads(body)
            request.pop("stream_options", None)
            request["stream"] = False
            # pi-ai sends a flat `reasoning_effort`; the extension reads the nested `reasoning: {effort}` form.
            if "reasoning_effort" in request and "reasoning" not in request:
                request["reasoning"] = {"effort": request["reasoning_effort"]}
            body = json.dumps(request).encode()
            headers["Content-Type"] = "application/json"
        return headers, body

    def respond(handler, resp, request_body):
        data = resp.read()
        try:
            want = bool(json.loads(request_body or b"{}").get("stream"))
        except ValueError:
            want = False
        if not want:
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", str(len(data)))
            handler.end_headers()
            handler.wfile.write(data)
            return
        value = json.loads(data)
        choice = (value.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        base = {"id": value.get("id", "chatcmpl-shim"), "object": "chat.completion.chunk",
                "created": value.get("created", int(time.time())), "model": value.get("model")}
        handler.send_response(200)
        handler.send_header("Content-Type", "text/event-stream")
        handler.send_header("Cache-Control", "no-cache")
        handler.send_header("Connection", "close")
        handler.end_headers()
        delta = {"role": "assistant", "content": message.get("content") or ""}
        if message.get("tool_calls"):
            delta["tool_calls"] = [dict(call, index=i) for i, call in enumerate(message["tool_calls"])]
        sse(handler, base | {"choices": [{"index": 0, "delta": delta, "finish_reason": None}]})
        sse(handler, base | {"choices": [{"index": 0, "delta": {}, "finish_reason": choice.get("finish_reason", "stop")}],
                             "usage": value.get("usage") or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})
        handler.wfile.write(b"data: [DONE]\n\n")
        handler.wfile.flush()

    serve(args.port, Upstream(args.upstream, timeout=900), prepare, respond, log_bodies=args.log_bodies, name="vscode")


if __name__ == "__main__":
    main()
