"""Check that the gateway answers before DSH starts: initialize and list tools over MCP (streamable HTTP, stdlib).

    python3 gateway_probe.py [URL] [TIMEOUT_S]      # default http://127.0.0.1:8080/mcp/, 300 s

Prints {"tools": N, "seconds": S}; exits 1 if the gateway did not answer in time. Run inside the environment
container; DSH's MCP client gives the first initialize/tools-list only the MCP SDK's 60 s, so run_task.py waits here
first (the first listing also warms the app servers).
"""

import json
import sys
import time
import urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/mcp/"
DEADLINE = time.monotonic() + (float(sys.argv[2]) if len(sys.argv) > 2 else 300)
session = None


def rpc(method, params=None, notify=False, rid=[0]):
    global session
    body = {"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})}
    if not notify:
        rid[0] += 1
        body["id"] = rid[0]
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    request = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST", headers=headers)
    with urllib.request.urlopen(request, timeout=max(1.0, DEADLINE - time.monotonic())) as reply:
        session = reply.headers.get("Mcp-Session-Id") or session
        raw = reply.read().decode()
    if notify:
        return None
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:]
    return json.loads(raw)


start = time.monotonic()
while True:
    try:
        rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "probe", "version": "0"}})
        rpc("notifications/initialized", notify=True)
        tools = rpc("tools/list")["result"]["tools"]
        print(json.dumps({"tools": len(tools), "seconds": round(time.monotonic() - start, 1)}))
        sys.exit(0)
    except Exception as error:  # the gateway may still be starting: retry until the deadline
        if time.monotonic() >= DEADLINE:
            print(json.dumps({"error": repr(error)[:300], "seconds": round(time.monotonic() - start, 1)}))
            sys.exit(1)
        session = None
        time.sleep(2)
