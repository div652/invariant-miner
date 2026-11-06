"""The VS Code endpoint shim against a fake GH Copilot Server extension (no VS Code needed).

    python3 tests/test_vscode_shim.py

The fake extension behaves like the real one where it matters: Chat Completions only, rejects `stream: true`, returns
one JSON response (a tool call first, then the answer), no auth, zero usage. DSH runs through the shim with the
luna-vscode model settings. Checks: the turn completes, the tool call ran, the final answer arrived, every upstream
request had stream false, the shim refused a request without the local token.
"""

import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
seen: list[dict] = []


class FakeExtension(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._json(200, {"object": "list", "data": [{"id": "gpt-5.6-luna", "object": "model"}]})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        seen.append(body)
        if body.get("stream"):
            return self._json(400, {"error": "streaming is not supported"})
        has_tool_result = any(m.get("role") == "tool" for m in body["messages"])
        message = ({"role": "assistant", "content": "391"} if has_tool_result else
                   {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1", "type": "function", "function": {
                       "name": "bash", "arguments": json.dumps({"command": "python3 -c 'print(17*23)'", "description": "compute"})}}]})
        self._json(200, {"id": "x", "object": "chat.completion", "created": 1, "model": body["model"], "choices": [
            {"index": 0, "message": message, "finish_reason": "stop" if has_tool_result else "tool_calls"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}})


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    fake = ThreadingHTTPServer(("127.0.0.1", 0), FakeExtension)
    threading.Thread(target=fake.serve_forever, daemon=True).start()
    port = free_port()
    shim = subprocess.Popen([sys.executable, str(REPO / "endpoints/vscode/stream_shim.py"), "--port", str(port),
                             "--upstream", f"http://127.0.0.1:{fake.server_address[1]}/v1"], stdout=subprocess.DEVNULL)
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-shim-"))
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=5)
            refused = False
        except urllib.error.HTTPError as e:
            refused = e.code == 401
        model = json.loads((REPO / "models/luna-vscode.json").read_text()) | {"base_url": f"http://127.0.0.1:{port}/v1"}
        (root / "model.json").write_text(json.dumps(model))
        (root / "spec.json").write_text(json.dumps({"task_id": "shim", "prompt": "compute 17*23", "model": str(root / "model.json"),
                                                    "final_answer": False, "limits": {"max_steps": 6, "timeout_s": 120}}))
        subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"), "--out", str(root / "run")],
                       cwd=REPO, capture_output=True, timeout=300)
    finally:
        shim.terminate()
        fake.shutdown()
    answer = json.loads((root / "run/answer.json").read_text())
    checks = [
        ("shim refuses a request without the local token", refused),
        ("turn completed", answer["finish_reason"] == "completed"),
        ("final answer streamed back", answer["answer"].strip() == "391"),
        ("tool call ran (bash result sent upstream)", any("391" in json.dumps(b["messages"]) and
                                                          any(m.get("role") == "tool" for m in b["messages"]) for b in seen)),
        ("every upstream request had stream false", seen and all(b.get("stream") is False for b in seen)),
        ("reasoning effort forwarded (flat and nested)", seen and all(b.get("reasoning_effort") == "high"
                                                               and b.get("reasoning") == {"effort": "high"} for b in seen)),
    ]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n{sum(ok for _, ok in checks)}/{len(checks)} passed; run dir {root}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
