"""A scripted OpenAI-compatible model for harness tests: no real model, fully deterministic.

It replays a script of steps over `POST /v1/chat/completions` (streaming). The step served is the number of assistant
messages already in the request, so the server keeps no conversation state. Each step is either tool calls or a final
text answer:

    [{"calls": [{"name": "bash", "args": {"command": "pwd", "description": "print dir"}}]},
     {"text": "done"}]

An argument value "$from_last:REGEX" is replaced by the first group of REGEX matched against the last tool result in
the request (e.g. a background job id). Every request is appended to --log as one JSON line (the step served, the offered tool names and the messages), so a test can read
the tool results the harness sent back.

    python scripted_model.py --script steps.json --log requests.jsonl --port 0 --port-file port.txt
"""

import argparse
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MODEL = "scripted"


def chunk(delta: dict, finish: str | None = None, usage: dict | None = None) -> bytes:
    body = {
        "id": "scripted",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": MODEL,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
    }
    if usage is not None:
        body["usage"] = usage
    return b"data: " + json.dumps(body).encode() + b"\n\n"


def fill(value, messages: list[dict]):
    """Resolve "$from_last:REGEX" argument values against the last tool result."""
    if isinstance(value, dict):
        return {k: fill(v, messages) for k, v in value.items()}
    if isinstance(value, str) and value.startswith("$from_last:"):
        tools = [m for m in messages if m.get("role") == "tool"]
        content = tools[-1].get("content") if tools else ""
        text = content if isinstance(content, str) else json.dumps(content)
        match = re.search(value[len("$from_last:"):], text)
        return match.group(1) if match else "<no match>"
    return value


def make_handler(steps: list[dict], log: Path, lock: threading.Lock):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _json(self, status: int, value: dict) -> None:
            data = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path.rstrip("/").endswith("/models"):
                return self._json(200, {"object": "list", "data": [{"id": MODEL, "object": "model"}]})
            self._json(404, {"error": "not found"})

        def do_POST(self):
            if not self.path.rstrip("/").endswith("/chat/completions"):
                return self._json(404, {"error": "not found"})
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            messages = request.get("messages", [])
            index = sum(m.get("role") == "assistant" for m in messages)
            step = steps[index] if index < len(steps) else {"text": "(script exhausted)"}
            with lock, log.open("a") as out:
                tools = [t.get("function", {}).get("name") for t in request.get("tools", [])]
                out.write(json.dumps({"step": index, "tools": tools, "messages": messages}) + "\n")
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            usage = {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
            if "calls" in step:
                calls = [
                    {
                        "index": i,
                        "id": f"call_{index}_{i}",
                        "type": "function",
                        "function": {"name": c["name"], "arguments": json.dumps(fill(c["args"], messages))},
                    }
                    for i, c in enumerate(step["calls"])
                ]
                self.wfile.write(chunk({"role": "assistant", "content": None, "tool_calls": calls}))
                self.wfile.write(chunk({}, "tool_calls", usage))
            else:
                self.wfile.write(chunk({"role": "assistant", "content": step["text"]}))
                self.wfile.write(chunk({}, "stop", usage))
            self.wfile.write(b"data: [DONE]\n\n")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--port-file", type=Path)
    args = parser.parse_args()
    steps = json.loads(args.script.read_text())
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(steps, args.log, threading.Lock()))
    if args.port_file:
        args.port_file.write_text(str(server.server_address[1]))
    server.serve_forever()


if __name__ == "__main__":
    main()
