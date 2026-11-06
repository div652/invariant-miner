"""Shared plumbing for the local endpoint proxies (endpoints/trapi, endpoints/vscode).

A loopback-only HTTP server that checks the shared local token (dsh_bench.endpoints.local_token), lets a mode adapt
the request (headers, body) and forwards it to the upstream, streaming the response back. Request and response bodies
can be logged for checks (--log-bodies: request bodies only, never headers or tokens).
"""

import http.client
import json
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dsh_bench.endpoints import local_token  # noqa: E402

HOP = {"connection", "keep-alive", "transfer-encoding", "te", "upgrade", "proxy-connection", "host", "content-length",
       "authorization", "x-api-key", "accept-encoding"}


class Upstream:
    def __init__(self, base_url: str, timeout: float = 900):
        parts = urlsplit(base_url.rstrip("/"))
        self.https = parts.scheme == "https"
        self.host, self.port = parts.hostname, parts.port or (443 if self.https else 80)
        self.base_path = parts.path  # e.g. /<instance>/openai/v1 or /v1
        self.timeout = timeout

    def connect(self) -> http.client.HTTPConnection:
        cls = http.client.HTTPSConnection if self.https else http.client.HTTPConnection
        return cls(self.host, self.port, timeout=self.timeout)

    def path(self, request_path: str) -> str:
        # DSH's base URL is http://127.0.0.1:<port>/v1, so its paths start with /v1: map them under the upstream base.
        rest = request_path[3:] if request_path.startswith("/v1") else request_path
        return self.base_path + rest


def serve(port: int, upstream: Upstream, prepare, respond=None, log_bodies: Path | None = None, name: str = "proxy"):
    """prepare(method, path, headers: dict, body: bytes) -> (headers, body); respond(handler, conn_response,
    original_request_body) replaces the default streaming pass-through for 200 responses when given."""
    token = local_token()
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send_json(self, status: int, value: dict) -> None:
            data = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle(self):
            if self.path.rstrip("/") == "/health":
                return self._send_json(200, {"status": "ok", "proxy": name, "upstream": f"{upstream.host}:{upstream.port}"})
            offered = self.headers.get("Authorization", "").removeprefix("Bearer ").strip() or self.headers.get("x-api-key", "")
            if not secrets.compare_digest(offered.encode(), token.encode()):
                return self._send_json(401, {"error": {"message": "missing or wrong local endpoint token"}})
            body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
            headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
            original = body
            headers, body = prepare(self.command, self.path, headers, body)
            if log_bodies is not None and body:
                try:
                    logged = json.loads(body)
                except ValueError:
                    logged = {"non_json_bytes": len(body)}
                with lock, log_bodies.open("a") as out:
                    out.write(json.dumps({"method": self.command, "path": self.path, "body": logged}) + "\n")
            conn = upstream.connect()
            try:
                if body:
                    headers["Content-Length"] = str(len(body))
                conn.request(self.command, upstream.path(self.path), body=body or None, headers=headers)
                resp = conn.getresponse()
                if respond is not None and resp.status == 200:
                    return respond(self, resp, original)
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in HOP and not k.lower().startswith("x-trapi-backend"):
                        self.send_header(k, v)
                self.send_header("Connection", "close")
                self.end_headers()
                while chunk := resp.read1(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            finally:
                conn.close()
                self.close_connection = True

        do_GET = do_POST = _handle

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[{name}] listening on http://127.0.0.1:{server.server_address[1]}/v1 -> "
          f"{'https' if upstream.https else 'http'}://{upstream.host}:{upstream.port}{upstream.base_path}", flush=True)
    server.serve_forever()
