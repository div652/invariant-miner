"""Relay DSH's stdio MCP connection to the world's MCP gateway, inside Mercor's 1.1 world container, unchanged.

    podman exec -i <world> /app/.venv/bin/python /opt/dsh-bench/lib/mcp_relay.py

A plain JSON-RPC pass-through (stdio <-> MCP streamable HTTP at http://127.0.0.1:8000/mcp): every message DSH sends is
POSTed to the gateway as it is, every message the gateway returns (JSON or SSE) is written back as it is. It keeps no
state beyond the session id: no tool list, no cache. (The FastMCP proxy used before cached the gateway's tool list for
5 minutes, so a list that came back incomplete under load made calls fail with "Unknown tool" until it expired:
CHECKLIST.md.) DSH connects the way Mercor's agent does, as one client of the gateway.

As Mercor's agent, one world call at a time: tools/call and tools/list hold a lock shared by every relay in the world
(DSH's main agent and each subagent run one relay each), so the world never runs two at once. The per-call limit is
Mercor's (apex_loop_truncated_tools_agent: tool_call_timeout 60 s, then a 5 s grace, then cancel), counted from when
the call is sent to the world, not while it waits for the lock. A call still running then is cancelled
(notifications/cancelled, connection closed) and answered with Mercor's text, "Tool call timed out".
"""

import fcntl
import http.client
import json
import os
import sys
import threading

HOST, PORT, PATH = "127.0.0.1", 8000, "/mcp"
LOCK_PATH = "/tmp/dsh-world-calls.lock"
SERIALIZED = {"tools/call", "tools/list"}
CALL_TIMEOUT_S = float(os.environ.get("DSH_RELAY_CALL_TIMEOUT_S", "60"))
GRACE_S = float(os.environ.get("DSH_RELAY_GRACE_S", "5"))
TIMEOUT_TEXT = "Tool call timed out"

out_lock, state_lock = threading.Lock(), threading.Lock()
state = {"session": None, "protocol": None}
answered: set = set()  # ids already answered by the relay (timeout): a late reply from the world is dropped


def emit(message: dict) -> None:
    key = json.dumps(message.get("id")) if "id" in message and "method" not in message else None
    with out_lock:
        if key is not None and key in answered:
            return
        sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
        sys.stdout.flush()


def answer_once(request: dict, reply: dict) -> None:
    """The relay's own reply (timeout, error): written once, and later replies for that id are dropped."""
    key = json.dumps(request["id"])
    with out_lock:
        if key in answered:
            return
        answered.add(key)
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": request["id"], **reply}, separators=(",", ":")) + "\n")
        sys.stdout.flush()


def headers() -> dict:
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    with state_lock:
        if state["session"]:
            h["mcp-session-id"] = state["session"]
        if state["protocol"]:
            h["MCP-Protocol-Version"] = state["protocol"]
    return h


def forward(item: dict, request: dict) -> None:
    if request.get("method") == "initialize" and item.get("id") == request.get("id") and "result" in item:
        with state_lock:
            state["protocol"] = item["result"].get("protocolVersion")
    emit(item)


def post(message: dict, conns: list | None = None) -> None:
    """POST one message to the gateway; write every JSON-RPC message of its reply to stdout."""
    conn = http.client.HTTPConnection(HOST, PORT, timeout=None)
    if conns is not None:
        conns.append(conn)
    try:
        conn.request("POST", PATH, body=json.dumps(message), headers=headers())
        resp = conn.getresponse()
        if resp.getheader("mcp-session-id"):
            with state_lock:
                state["session"] = resp.getheader("mcp-session-id")
        if resp.status in (202, 204):
            resp.read()
            return
        if "text/event-stream" in (resp.getheader("Content-Type") or ""):
            data: list[str] = []
            for raw in resp:
                line = raw.decode("utf-8", "replace").rstrip("\r\n")
                if line.startswith("data:"):
                    data.append(line[5:].lstrip())
                elif line == "" and data:
                    for item in as_list(json.loads("\n".join(data))):
                        forward(item, message)
                    data = []
            for item in as_list(json.loads("\n".join(data))) if data else []:
                forward(item, message)
            return
        body = resp.read()
        if body.strip():
            for item in as_list(json.loads(body)):
                forward(item, message)
        elif "id" in message:
            answer_once(message, {"error": {"code": -32603, "message": f"relay: gateway HTTP {resp.status}, no body"}})
    finally:
        conn.close()


def as_list(value):
    return value if isinstance(value, list) else [value]


def call_with_limit(message: dict) -> None:
    """A tools/call under Mercor's limit: CALL_TIMEOUT_S, then GRACE_S, then cancelled and answered with the text."""
    conns: list = []
    worker = threading.Thread(target=post_or_error, args=(message, conns), daemon=True)
    worker.start()
    worker.join(CALL_TIMEOUT_S + GRACE_S)
    if not worker.is_alive():
        return
    answer_once(message, {"result": {"content": [{"type": "text", "text": TIMEOUT_TEXT}], "isError": True}})
    try:
        post({"jsonrpc": "2.0", "method": "notifications/cancelled",
              "params": {"requestId": message.get("id"), "reason": "tool call timed out"}})
    except Exception:
        pass
    for conn in conns:
        try:
            if conn.sock is not None:
                conn.sock.shutdown(2)
        except OSError:
            pass


def post_or_error(message: dict, conns: list | None = None) -> None:
    try:
        post(message, conns)
    except Exception as error:  # the gateway refused or the connection broke: an MCP error, not a relay crash
        if "id" in message:
            answer_once(message, {"error": {"code": -32603, "message": f"relay: {error}"}})


def handle(message: dict) -> None:
    if message.get("method") not in SERIALIZED:
        post_or_error(message)
        return
    with open(LOCK_PATH, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if message["method"] == "tools/call":
                call_with_limit(message)
            else:
                post_or_error(message)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if message.get("method") == "initialize" or "method" not in message:
            handle(message)  # initialize in order (later requests need its session id); replies to the server too
        else:
            threading.Thread(target=handle, args=(message,), daemon=True).start()


if __name__ == "__main__":
    main()
