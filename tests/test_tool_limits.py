"""tool-limits test: plugins/tool-limits through the launcher (spec key tool_limits), with the scripted model.

1. Parity: plugins/tool-limits truncate() against the Python rule it ports (Archipelago's loop_truncated_tools agent,
   `_truncate_output`), on fixed edge cases and random texts (lines, long lines, multi-byte characters).
2. A run with tool_limits {max_lines: 20, max_chars: 300, timeout_s: 3}: bash printing 100 lines (cut at 20 lines), an
   MCP tool returning one 1000-character line (cut at 300 characters), bash sleeping 30 s (stopped at 3 s with the
   timeout text), then bash again (still works). Checks what the model received for each call.

    python3 tests/test_tool_limits.py
"""

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NODE = None


def reference(content: str, max_lines: int, max_chars: int) -> str:
    """Archipelago's _truncate_output (loop_truncated_tools_agent/main.py), verbatim in behaviour."""
    if not content:
        return content
    lines = content.split("\n")
    total_lines = len(lines)
    if total_lines > max_lines:
        truncated_content = "\n".join(lines[:max_lines])
        if len(truncated_content) > max_chars:
            truncated_content = truncated_content[:max_chars]
            kept_lines = truncated_content.count("\n") + 1
            hidden_lines = total_lines - kept_lines
        else:
            hidden_lines = total_lines - max_lines
        return truncated_content + f"\n... (truncated {hidden_lines} lines) ..."
    if len(content) > max_chars:
        truncated_content = content[:max_chars]
        kept_lines = truncated_content.count("\n") + 1
        hidden_lines = total_lines - kept_lines
        if hidden_lines > 0:
            suffix = f"\n... (truncated {hidden_lines} lines) ..."
        else:
            hidden_chars = len(content) - len(truncated_content)
            suffix = f"\n... (truncated {hidden_chars} chars) ..."
        return truncated_content + suffix
    return content


def parity() -> tuple[int, int]:
    rng = random.Random(7)
    alphabet = "ab \n\n€😀ü"
    cases = [("", 3, 5), ("x", 3, 5), ("a\nb\nc", 3, 5), ("a\nb\nc\nd", 3, 5), ("abcdef", 3, 5), ("ab\ncdefgh", 3, 5),
             ("😀" * 10, 3, 5), ("l1\nl2\nl3\nl4\nl5\nl6", 4, 7)]
    for _ in range(400):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 60)))
        cases.append((text, rng.randint(1, 8), rng.randint(1, 30)))
    script = ("import { truncate } from '%s'\nimport { readFileSync } from 'node:fs'\n"
              "const cases = JSON.parse(readFileSync(0, 'utf8'))\n"
              "process.stdout.write(JSON.stringify(cases.map(([t, l, c]) => truncate(t, l, c))))\n"
              % (REPO / "plugins/tool-limits/index.mjs").as_uri())
    out = subprocess.run([NODE, "--input-type=module", "-e", script], input=json.dumps(cases), capture_output=True,
                         text=True, check=True).stdout
    got = json.loads(out)
    bad = [(c, g) for c, g in zip(cases, got) if reference(*c) != g]
    for case, g in bad[:3]:
        print(f"  mismatch {case!r}: node {g!r} vs python {reference(*case)!r}")
    return len(cases), len(bad)


def tool_texts(request: dict) -> list[str]:
    out = []
    for m in request["messages"]:
        if m.get("role") != "tool":
            continue
        content = m.get("content")
        out.append("".join(p.get("text", "") for p in content if isinstance(p, dict)) if isinstance(content, list)
                   else content or "")
    return out


def main() -> int:
    global NODE
    NODE = os.environ.get("NODE", shutil.which("node") or "node")
    n, bad = parity()
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-tool-limits-"))
    long_line = "x" * 1000
    steps = [
        {"calls": [{"name": "bash", "args": {"command": "seq 1 100", "description": "count"}}]},
        {"calls": [{"name": "mcp__demo__echo", "args": {"text": long_line}}]},
        {"calls": [{"name": "bash", "args": {"command": "sleep 30; echo late", "description": "sleep"}}]},
        {"calls": [{"name": "bash", "args": {"command": "echo still-alive", "description": "after"}}]},
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
            "task_id": "tool-limits-smoke",
            "prompt": "Use the tools.",
            "model": str(root / "model.json"),
            "mcp": [{"name": "demo", "transport": "stdio", "command": sys.executable,
                     "args": [str(REPO / "tests/mcp_demo_server.py"), "--log", str(mcp_log)]}],
            "tool_limits": {"max_lines": 20, "max_chars": 300, "timeout_s": 3},
            "limits": {"max_steps": 20, "timeout_s": 300},
        }))
        out = root / "run"
        t0 = time.monotonic()
        proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"),
                               "--out", str(out)], cwd=REPO, capture_output=True, text=True, timeout=600)
        elapsed = time.monotonic() - t0
    finally:
        model_proc.terminate()
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1
    req = [json.loads(line) for line in log.read_text().splitlines()]
    res = [(tool_texts(r) or [""])[-1] for r in req]  # res[i] = result of step i-1
    seq_lines = res[1].split("\n") if len(res) > 1 else []
    checks = [
        (f"truncate() matches the Python rule on {n} texts", bad == 0),
        ("all 5 requests made", len(req) == 5),
        ("bash 100 lines: cut at 20 lines with the note", len(res) > 1 and "... (truncated " in res[1]
         and "lines) ..." in res[1] and "100" not in seq_lines and len(seq_lines) <= 21),
        ("MCP 1000-char line: cut at 300 chars with the note", len(res) > 2
         and res[2] == reference("ECHO: " + long_line, 20, 300)),
        ("sleep 30: stopped with the timeout text", len(res) > 3 and res[3] == "Tool call timed out"),
        ("bash works after the timeout", len(res) > 4 and "still-alive" in res[4]),
        ("the run did not wait for the sleep (< 25 s)", elapsed < 25),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    if failed:
        for i, text in enumerate(res):
            print(f"  res[{i}]: {text[:300]!r}")
        print(proc.stderr[-1500:])
    print(f"{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    sys.exit(main())
