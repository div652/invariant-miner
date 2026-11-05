"""Forward HTTP requests to an upstream (e.g. CAO) and log each request BODY (never headers, so no keys).

    python3 tests/log_proxy.py --upstream http://127.0.0.1:4141 --log bodies.jsonl --port-file port.txt

Used to check what the harness actually sends to a model endpoint. Responses (including SSE streams) are passed
through unchanged.
"""

import argparse
import http.client
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HOP = {"connection", "keep-alive", "transfer-encoding", "te", "upgrade", "proxy-connection", "host", "content-length"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--port-file", type=Path)
    args = parser.parse_args()
    up = urlsplit(args.upstream)
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _forward(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
            if body:
                try:
                    logged = json.loads(body)
                except ValueError:
                    logged = {"non_json_bytes": len(body)}
                with lock, args.log.open("a") as out:
                    out.write(json.dumps({"method": self.command, "path": self.path, "body": logged}) + "\n")
            conn = http.client.HTTPConnection(up.hostname, up.port, timeout=900)
            headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
            conn.request(self.command, self.path, body=body or None, headers=headers)
            resp = conn.getresponse()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in HOP:
                    self.send_header(k, v)
            self.send_header("Connection", "close")
            self.end_headers()
            while chunk := resp.read1(65536):
                self.wfile.write(chunk)
                self.wfile.flush()
            conn.close()

        do_GET = do_POST = _forward

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    if args.port_file:
        args.port_file.write_text(str(server.server_address[1]))
    server.serve_forever()


if __name__ == "__main__":
    main()
