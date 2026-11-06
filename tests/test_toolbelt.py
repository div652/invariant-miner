"""Toolbelt test: plugins/toolbelt through the launcher, with the scripted model and a stdio MCP server.

The spec turns the toolbelt on (max_size 1) and connects tests/mcp_demo_server.py (tools echo, add_numbers). The
scripted model lists the hidden tools, calls one before adding it (denied), inspects, adds and calls it, hits the size
limit, tries to add a DSH tool, removes the tool and lists again. Checks: which tools each request offered, every
meta-tool result (Archipelago's exact texts), and that the denied call never reached the MCP server.

    python3 tests/test_toolbelt.py
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ECHO, ADD = "mcp__demo__echo", "mcp__demo__add_numbers"
META = ["toolbelt_list_tools", "toolbelt_inspect_tool", "toolbelt_add_tool", "toolbelt_remove_tool"]


def last_tool_text(request: dict) -> str:
    tools = [m for m in request["messages"] if m.get("role") == "tool"]
    content = tools[-1].get("content") if tools else ""
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content or ""


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-toolbelt-"))
    steps = [
        {"calls": [{"name": "toolbelt_list_tools", "args": {}}]},
        {"calls": [{"name": ECHO, "args": {"text": "too early"}}]},
        {"calls": [{"name": "toolbelt_inspect_tool", "args": {"tool_name": ECHO}}]},
        {"calls": [{"name": "toolbelt_add_tool", "args": {"tool_name": ECHO}}]},
        {"calls": [{"name": ECHO, "args": {"text": "hello from the belt"}}]},
        {"calls": [{"name": "toolbelt_add_tool", "args": {"tool_name": ADD}}]},
        {"calls": [{"name": "toolbelt_add_tool", "args": {"tool_name": "bash"}}]},
        {"calls": [{"name": "toolbelt_remove_tool", "args": {"tool_name": ECHO}}]},
        {"calls": [{"name": "toolbelt_list_tools", "args": {}}]},
        {"calls": [{"name": "final_answer", "args": {"answer": "done"}}]},
        {"text": "should never be requested"},
    ]
    (root / "script.json").write_text(json.dumps(steps))
    log, port_file, mcp_log = root / "requests.jsonl", root / "port.txt", root / "mcp-calls.jsonl"
    mcp_log.touch()
    model_proc = subprocess.Popen([sys.executable, str(REPO / "tests/scripted_model.py"), "--script",
                                   str(root / "script.json"), "--log", str(log), "--port-file", str(port_file)])
    try:
        for _ in range(50):
            if port_file.exists() and port_file.read_text():
                break
            time.sleep(0.1)
        (root / "model.json").write_text(json.dumps({
            "provider": "scripted", "model": "scripted", "api": "openai-completions",
            "base_url": f"http://127.0.0.1:{port_file.read_text()}/v1", "context_window": 131072, "max_tokens": 4096,
            "compat": {"supportsDeveloperRole": False, "supportsStore": False, "maxTokensField": "max_tokens"}}))
        (root / "spec.json").write_text(json.dumps({
            "task_id": "toolbelt-smoke",
            "prompt": "Use the demo tools.",
            "model": str(root / "model.json"),
            "mcp": [{"name": "demo", "transport": "stdio", "command": sys.executable,
                     "args": [str(REPO / "tests/mcp_demo_server.py"), "--log", str(mcp_log)]}],
            "toolbelt": {"max_size": 1},
            "limits": {"max_steps": 20, "timeout_s": 120},
        }))
        out = root / "run"
        proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"),
                               "--out", str(out)], cwd=REPO, capture_output=True, text=True, timeout=400)
    finally:
        model_proc.terminate()
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1

    req = [json.loads(line) for line in log.read_text().splitlines()]
    answer = json.loads((out / "answer.json").read_text())
    mcp_calls = [json.loads(line) for line in mcp_log.read_text().splitlines()]
    result = [last_tool_text(r) for r in req]  # result[i] = the tool result of step i-1
    inspect = json.loads(result[3]) if result[3].startswith("{") else {}
    checks = [
        ("all 10 requests made", len(req) == 10),
        ("step 0: meta-tools, bash and final_answer offered", all(t in req[0]["tools"] for t in META + ["bash", "final_answer"])),
        ("step 0: MCP tools hidden", ECHO not in req[0]["tools"] and ADD not in req[0]["tools"]),
        ("list: the hidden MCP tools, Python json.dumps format", result[1] == f'["{ADD}", "{ECHO}"]'),
        ("call before add: Archipelago's error text", result[2] == f"Error: '{ECHO}' not in toolbelt. Use toolbelt_add_tool first."),
        ("inspect: name, description, parameters", inspect.get("name") == ECHO and "Echo the text back" in inspect.get("description", "")
         and "text" in json.dumps(inspect.get("parameters"))),
        ("add: success, size 1", result[4] == '{"success": true, "toolbelt_size": 1}'),
        ("after add: echo offered, add_numbers still hidden", ECHO in req[4]["tools"] and ADD not in req[4]["tools"]),
        ("added tool runs on the MCP server", "ECHO: hello from the belt" in result[5]),
        ("max_size 1: toolbelt full", result[6] == '{"error": "Toolbelt full. Remove a tool first."}'),
        ("add a DSH tool: always available", result[7] == '{"error": "\'bash\' is always available; call it directly without adding it to the toolbelt"}'),
        ("remove: success, size 0", result[8] == '{"success": true, "toolbelt_size": 0}'),
        ("after remove: echo hidden again", ECHO not in req[8]["tools"]),
        ("list again: both hidden tools", result[9] == f'["{ADD}", "{ECHO}"]'),
        ("denied call never reached the MCP server", [c["arguments"].get("text") for c in mcp_calls] == ["hello from the belt"]),
        ("answer.json: finish reason final_answer", answer["finish_reason"] == "final_answer" and answer["answer"] == "done"),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    if failed:
        for i, text in enumerate(result):
            print(f"  result[{i}]: {text[:200]!r}")
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
