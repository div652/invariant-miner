"""Plumbing test for the APEX-Agents adapter: run_task.py on a real task with the scripted model (no real model).

The scripted agent lists the hidden app tools, adds and calls the Filesystem app's list_files on "/", reads the task's
input PDF with DSH's `read` (binary: refused) and lists it with bash, tries /.apps_data and /app from bash (the
code_exec sandbox must deny both), writes a file with DSH's `write`, adds and calls code_exec, and submits a final
answer. Checks: the world and task files were populated through Archipelago's API, the world's 9 apps run (73 tools
behind the toolbelt), each tool result, the snapshots (before has the task file, after also has the written file),
the trajectory for Archipelago's grader.

    python3 benchmarks/apex-agents-1.0/test_plumbing.py [--task task_0b9134a634c14f24a6c256d034a6c130]
"""

import argparse
import json
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TASK = "task_0b9134a634c14f24a6c256d034a6c130"  # Law World 416, one input PDF, answer in the console
PDF = "Further Modifying the Reciprocal Tariff Rates – The White House.pdf"
LIST_FILES, CODE_EXEC = "mcp__apps__filesystem_server_list_files", "mcp__apps__code_execution_server_code_exec"


def tool_texts(request: dict) -> list[str]:
    out = []
    for m in request["messages"]:
        if m.get("role") == "tool":
            c = m.get("content")
            out.append(c if isinstance(c, str) else "".join(p.get("text", "") for p in c if isinstance(p, dict)))
    return out


def names(archive: Path) -> set[str]:
    with tarfile.open(archive) as tar:
        return {m.name.removeprefix("./") for m in tar.getmembers() if m.isfile()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default=TASK)
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="apex-plumbing-"))
    steps = [
        {"calls": [{"name": "toolbelt_list_tools", "args": {}}]},
        {"calls": [{"name": "toolbelt_add_tool", "args": {"tool_name": LIST_FILES}}]},
        {"calls": [{"name": LIST_FILES, "args": {"path": "/"}}]},
        {"calls": [{"name": "read", "args": {"file_path": f"/filesystem/{PDF}"}}]},
        {"calls": [{"name": "bash", "args": {"command": "pwd; ls /filesystem | wc -l; ls -la /filesystem/*Tariff*",
                                              "description": "list"}}]},
        {"calls": [{"name": "bash", "args": {"command": "ls /.apps_data 2>&1; ls /app 2>&1; true",
                                              "description": "probe fence"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "/filesystem/plumbing-note.txt", "content": "note\n"}}]},
        {"calls": [{"name": "toolbelt_add_tool", "args": {"tool_name": CODE_EXEC}}]},
        {"calls": [{"name": CODE_EXEC, "args": {"code": "python3 -c 'import pandas; print(\"pandas\", pandas.__version__)'; pwd"}}]},
        {"calls": [{"name": "final_answer", "args": {"answer": "Plumbing answer."}}]},
        {"text": "should never be requested"},
    ]
    (root / "script.json").write_text(json.dumps(steps))
    log, port_file = root / "requests.jsonl", root / "port.txt"
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
        out = root / "run"
        proc = subprocess.run([sys.executable, str(HERE / "run_task.py"), "--task", args.task, "--out", str(out),
                               "--model", str(root / "model.json"), "--max-steps", "30", "--timeout-s", "900"],
                              cwd=REPO, capture_output=True, text=True, timeout=1800)
    finally:
        model_proc.terminate()
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1
    req = [json.loads(line) for line in log.read_text().splitlines()]
    res = [(tool_texts(r) or [""])[-1] for r in req]
    record = json.loads((out / "run.json").read_text())
    traj = json.loads((out / "trajectory.json").read_text())
    before, after = names(out / "snapshots/before.tar.gz"), names(out / "snapshots/after.tar.gz")
    listed = json.loads(res[1]) if res[1].startswith("[") else []
    checks = [
        ("populate: world + task archives accepted", len(record.get("populate", [])) >= 3
         and any(p["archive"].startswith("task_") for p in record["populate"])),
        ("apps: the world's 9 servers configured", sorted(record["apps_configured"]["servers"]) == sorted(record["apps"])
         and len(record["apps"]) == 9),
        ("step 0: no app tools offered, toolbelt tools offered", not any(t.startswith("mcp__") for t in req[0]["tools"])
         and "toolbelt_list_tools" in req[0]["tools"]),
        ("toolbelt lists the 73 app tools", len(listed) == 73 and LIST_FILES in listed and CODE_EXEC in listed),
        ("added tool offered next step", LIST_FILES in req[2]["tools"]),
        ("Filesystem app lists the task's PDF", "Reciprocal Tariff" in res[3]),
        ("DSH read refuses the binary PDF", "binary file" in res[4]),
        ("bash runs in /filesystem and sees the PDF", "/filesystem" in res[5] and "Reciprocal Tariff" in res[5]),
        ("bash cannot reach /.apps_data or /app", res[6].count("Permission denied") >= 2),
        ("DSH write in /filesystem", "error" not in res[7].lower()),
        ("code_exec runs with its packages, in /filesystem", "pandas 2.3.3" in res[9] and "/filesystem" in res[9]),
        ("finish: final_answer", record.get("finish_reason") == "final_answer"),
        ("before snapshot: world + task files, no agent file",
         any("Reciprocal Tariff" in n for n in before) and not any("plumbing-note" in n for n in before)
         and any(n.startswith(".apps_data/") for n in before)),
        ("after snapshot: the agent's file", any(n.endswith("plumbing-note.txt") for n in after)),
        ("trajectory: one user message (task prompt) and the answer last", traj["status"] == "completed"
         and [m["role"] for m in traj["messages"]].count("user") == 1
         and traj["messages"][-1]["content"] == "Plumbing answer."),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    if failed:
        for i, text in enumerate(res):
            print(f"  res[{i}]: {text[:240]!r}")
        print(sorted(before)[:5], sorted(after)[:5])
        print((out / "launch.log").read_text()[-1500:] if (out / "launch.log").exists() else proc.stderr[-1500:])
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
