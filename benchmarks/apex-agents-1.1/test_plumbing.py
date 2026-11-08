"""Plumbing test for APEX-Agents 1.1: one real task end to end with the scripted model (no model calls).

    python3 benchmarks/apex-agents-1.1/test_plumbing.py [--task 128-jr-1-f7f95d92]

Runs run_task.py on a task with input files, with a scripted model that: runs bash (who, umask, cwd, app data, rg,
pandas), lists the world's files through the filesystem app, runs run_shell, greps with DSH's grep, writes a file with
DSH's write tool, prints 500 lines with bash, then replies without a tool call. Checks the world, the tools offered,
the fence, the limits, the snapshots and the ATIF trajectory. Grading is not run (check_gold.py does).
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
DSH_TOOLS = {"bash", "read", "write", "edit", "glob", "grep", "read_image"}
W = "mcp__world__"


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="128-jr-1-f7f95d92")
    parser.add_argument("--no-subagents", action="store_true", help="also check that subagents and their guidance are off")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="apex11-plumbing-"))
    steps = [
        {"calls": [{"name": "bash", "args": {"command": "id -un; umask; pwd; ls /.apps_data 2>&1 | head -1; command -v rg;"
                                                        " python -c 'import pandas; print(\"pandas\", pandas.__version__)'",
                                             "description": "environment"}}]},
        {"calls": [{"name": f"{W}filesystem_server_list_files", "args": {"path": "/"}}]},
        {"calls": [{"name": f"{W}stirrup_code_execution_run_shell", "args": {"cmd": "id -un; ls | head -3"}}]},
        {"calls": [{"name": "grep", "args": {"pattern": "Skylink", "path": "/filesystem"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "/filesystem/dsh_plumbing_note.txt", "content": "made by DSH\n"}}]},
        {"calls": [{"name": "bash", "args": {"command": "seq 1 500", "description": "long output"}}]},
        {"text": "Plumbing check answer."},
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
            "base_url": f"http://127.0.0.1:{port_file.read_text()}/v1", "context_window": 400000, "max_tokens": 4096,
            "compat": {"supportsDeveloperRole": False, "supportsStore": False, "maxTokensField": "max_tokens"}}))
        out = root / "run"
        proc = subprocess.run([sys.executable, str(HERE / "run_task.py"), "--task", args.task, "--out", str(out),
                               "--model", str(root / "model.json")] + (["--no-subagents"] if args.no_subagents else []),
                              cwd=REPO, capture_output=True, text=True, timeout=1800)
    finally:
        model_proc.terminate()
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1
    record = json.loads((out / "run.json").read_text())
    req = [json.loads(line) for line in log.read_text().splitlines()]
    res = [(tool_texts(r) or [""])[-1] for r in req]  # res[i] = result of step i-1
    tools = set(req[0].get("tools", [])) if req else set()  # the scripted model logs the offered tool names
    world_tools = {t for t in tools if t.startswith(W)}
    system = next((m.get("content") for m in req[0]["messages"] if m.get("role") == "system"), "") if req else ""
    system = system if isinstance(system, str) else json.dumps(system)
    traj = json.loads((out / "trajectory.json").read_text()) if (out / "trajectory.json").exists() else {}
    agent_steps = [s for s in traj.get("steps", []) if s.get("source") == "agent"]
    final = next((s["message"] for s in reversed(agent_steps) if s.get("message")), None)
    logs = out / "world-logs"
    names, note_mode = set(), None
    if (logs / "final_snapshot.tar.gz").exists():
        with tarfile.open(logs / "final_snapshot.tar.gz") as tar:
            for member in tar.getmembers():
                names.add(member.name)
                if member.name == "filesystem/dsh_plumbing_note.txt":
                    note_mode = (oct(member.mode), member.uname, member.gname)
    world_gone = subprocess.run(["podman", "ps", "-aq", "--filter", f"name={record.get('container')}"],
                                capture_output=True, text=True).stdout.strip() == ""
    seq = res[6] if len(res) > 6 else ""
    checks = [
        ("no infrastructure error", "infra_error" not in record),
        ("world ready with an initial snapshot", (logs / "initial_snapshot.tar.gz").exists()),
        ("all 7 requests made", len(req) == 7),
        ("74 world tools offered on the first step", len(world_tools) == 74),
        ("DSH's own tools offered", DSH_TOOLS <= tools),
        ("no final_answer, toolbelt or web tools", not any(t == "final_answer" or t.startswith("toolbelt_") or "web" in t
                                                            for t in tools)),
        ("system prompt: run_shell, scattergun rule, /filesystem path sentence",
         "use the run_shell tool when needed" in system and "You should not scattergun" in system
         and "except the run_shell, bash, read, write, edit, read_image, glob and grep tools" in system
         and "code_exec" not in system),
        ("bash runs as run_shell's user, umask 0002, in /filesystem",
         len(res) > 1 and res[1].startswith("svc_stirrup_code_execution\n0002\n/filesystem")),
        ("bash cannot read the apps' raw data", len(res) > 1 and "Permission denied" in res[1]),
        ("bash has ripgrep and run_shell's pandas", len(res) > 1 and "/opt/dsh-bench/bin/rg" in res[1] and "pandas " in res[1]),
        ("filesystem app lists the task's input file", len(res) > 2 and "Business Unit Assessment Framework (v2).xlsx" in res[2]),
        ("run_shell works, as the same user", len(res) > 3 and "svc_stirrup_code_execution" in res[3]),
        ("DSH grep finds text in the world", len(res) > 4 and "error" not in res[4].lower() and res[4].strip() != ""),
        ("write tool: no error", len(res) > 5 and "error" not in res[5].lower()),
        # seq's output ends with a newline: 501 lines by the rule (the last one empty), 301 cut
        ("500 lines cut at 200 with the note", seq.endswith("\n200\n... (truncated 301 lines) ...")),
        ("run ended with a reply (completed)", record.get("finish_reason") == "completed"),
        ("final snapshot taken and has DSH's file, 664, group workspace",
         note_mode is not None and note_mode[0] == "0o664" and note_mode[2] == "workspace"),
        ("final snapshot has the world's files and app data", any(n.startswith(".apps_data/") for n in names)
         and any(n.startswith("filesystem/") for n in names)),
        ("trajectory: ATIF, agent steps with tool calls and results, final answer, status completed",
         traj.get("schema_version", "").startswith("ATIF") and final == "Plumbing check answer."
         and any(s.get("observation", {}).get("results") for s in agent_steps)
         and traj.get("extra", {}).get("native_status") == "completed"),
        ("world container removed", world_gone),
        ("no world call failed with Unknown tool", not any("Unknown tool" in r for r in res)),
        ("world tools reached through the relay", "/opt/dsh-bench/lib/mcp_relay.py" in (out / "agent-spec.json").read_text()),
    ]
    sub_tools = {"subagent", "subagent_fork", "send_message", "list_agents", "interrupt_agent"}
    everything = json.dumps(req[0]["messages"]).lower() if req else ""
    if args.no_subagents:
        checks += [("subagents off: no subagent tools offered", not (sub_tools & tools)),
                   ("subagents off: no subagent guidance anywhere in the prompt", "subagent" not in everything)]
    else:
        checks += [("subagents on: subagent tools offered", {"subagent", "subagent_fork"} <= tools),
                   ("subagents on: subagent guidance in the system prompt", "use subagent in the background" in everything)]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    if failed:
        for i, text in enumerate(res):
            print(f"  res[{i}]: {text[:300]!r}")
        print(f"  world tools: {len(world_tools)}; other tools: {sorted(tools - world_tools)}")
        print(proc.stderr[-1500:])
    print(f"{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
