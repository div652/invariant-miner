"""A minimal MCP server over stdio for harness tests: no dependencies, two tools, every call logged.

    python mcp_demo_server.py --log calls.jsonl

Tools: `echo` (returns "ECHO: <text>") and `add_numbers` (returns a + b). Each tools/call is appended to --log as one
JSON line, so a test can check which calls reached the server.
"""

import argparse
import json
import sys

TOOLS = [
    {"name": "echo", "description": "Echo the text back.",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string", "description": "Text to echo"}},
                     "required": ["text"]}},
    {"name": "add_numbers", "description": "Add two numbers.",
     "inputSchema": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                     "required": ["a", "b"]}},
]


def call(name: str, args: dict) -> str:
    if name == "echo":
        return f"ECHO: {args.get('text', '')}"
    if name == "add_numbers":
        return str(args.get("a", 0) + args.get("b", 0))
    raise KeyError(name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    log = parser.parse_args().log
    for line in sys.stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
        if mid is None:  # notification (e.g. notifications/initialized)
            continue
        if method == "initialize":
            result = {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                      "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "demo", "version": "1.0"}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            with open(log, "a") as out:
                out.write(json.dumps({"name": params.get("name"), "arguments": params.get("arguments")}) + "\n")
            try:
                result = {"content": [{"type": "text", "text": call(params["name"], params.get("arguments") or {})}],
                          "isError": False}
            except KeyError:
                result = {"content": [{"type": "text", "text": f"unknown tool {params.get('name')}"}], "isError": True}
        elif method == "ping":
            result = {}
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid,
                                         "error": {"code": -32601, "message": f"method not found: {method}"}}) + "\n")
            sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
