"""Isolation test for the agent-loop-on-host / tools-in-container setup (docs/BENCHMARK_CHECKLIST.md section 10).

Runs DSH headless with the sandbox-podman plugin and a scripted model (tests/scripted_model.py) that makes fixed tool
calls, then checks what each call returned:

  bash      runs in the container, in the workspace, as the host uid; sees no host files and no network;
            cannot write a read-only directory; writes to output/ reach the host; a timed-out command is killed inside
            the container too
  grep/glob run in the container (ripgrep) over the workspace
  read/write (host, workspace-isolated) refuse paths outside the workspace

    python3 tests/test_isolation.py            # needs ./setup.sh done (DSH build + dsh-bench-base image), podman
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DSH = Path(os.environ.get("DSH_BENCH_DSH_ROOT", REPO / "work/deepseek-harness"))
NODE = os.environ.get("NODE", shutil.which("node") or "node")
RUNTIME = os.environ.get("RUNTIME", "podman")
IMAGE = os.environ.get("IMAGE", "dsh-bench-base")


def bash(command: str, **extra) -> dict:
    return {"name": "bash", "args": {"command": command, "description": "test step", **extra}}


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-iso-"))
    ws, home = root / "workspace", root / "dsh-home"
    (ws / "documents").mkdir(parents=True)
    (ws / "output").mkdir()
    home.mkdir()
    (ws / "documents" / "brief.txt").write_text("SECRETDOC marker inside the workspace\n")
    # Launcher staging: a read-only directory is read-only on the host too, because the file tools run there.
    for path in (ws / "documents").rglob("*"):
        path.chmod(0o444)
    (ws / "documents").chmod(0o555)
    outside = root / "outside.txt"
    outside.write_text("HOSTSECRET outside the workspace\n")
    host_home = Path.home()
    container = f"dsh-bench-iso-{uuid.uuid4().hex[:8]}"

    steps = [
        {"calls": [bash('pwd; id -u; id -g; echo "WS=$WORKSPACE_DIR"')]},                             # 0
        {"calls": [bash(f"cat {outside}")]},                                                          # 1
        {"calls": [bash(f"test -e {host_home} && echo HOST_HOME_VISIBLE || echo HOST_HOME_HIDDEN")]},  # 2
        {"calls": [bash("echo x > documents/new.txt")]},                                              # 3
        {"calls": [bash("echo hello > output/a.txt && cat output/a.txt")]},                           # 4
        {"calls": [bash("python3 -c \"import urllib.request as u; u.urlopen('http://1.1.1.1', timeout=5); print('NET_OK')\"")]},  # 5
        {"calls": [{"name": "grep", "args": {"pattern": "SECRETDOC", "path": "documents"}}]},         # 6
        {"calls": [{"name": "glob", "args": {"pattern": "**/*.txt"}}]},                               # 7
        {"calls": [{"name": "read", "args": {"file_path": str(outside)}}]},                           # 8
        {"calls": [{"name": "write", "args": {"file_path": str(root / "written-outside.txt"), "content": "x"}}]},  # 9
        {"calls": [{"name": "read", "args": {"file_path": "documents/brief.txt"}}]},                  # 10
        {"calls": [bash("sleep 300; echo SLEEP_FINISHED", timeoutMs=3000)]},                          # 11
        {"calls": [bash("sleep 1; ps -eo args | grep -c '^sleep 300' || true")]},                     # 12
        {"calls": [bash(f"ln -s {outside} output/link.txt && echo LINKED")]},                         # 13
        {"calls": [{"name": "read", "args": {"file_path": "output/link.txt"}}]},                      # 14
        {"calls": [{"name": "write", "args": {"file_path": "documents/host-write.txt", "content": "x"}}]},  # 15
        {"calls": [bash("sleep 301", run_in_background=True)]},                                       # 16
        {"calls": [{"name": "job_kill", "args": {"job_id": "$from_last:\\b((?:job|bash)[-_][\\w-]+)"}}]},  # 17
        {"calls": [bash("sleep 1; ps -eo args | grep -c '^sleep 301' || true")]},                     # 18
        {"text": "done"},
    ]
    (root / "script.json").write_text(json.dumps(steps))
    log, port_file = root / "requests.jsonl", root / "port.txt"

    run = [RUNTIME, "run", "-d", "--name", container, "--network=none", "--cap-drop=ALL",
           "--security-opt=no-new-privileges", "--userns=keep-id",
           "-v", f"{ws}:{ws}", "-v", f"{ws / 'documents'}:{ws / 'documents'}:ro",
           "-e", "HOME=/tmp", "-w", str(ws), IMAGE, "sleep", "infinity"]
    subprocess.run(run, check=True, capture_output=True)
    model = subprocess.Popen([sys.executable, str(REPO / "tests/scripted_model.py"), "--script", str(root / "script.json"),
                              "--log", str(log), "--port-file", str(port_file)])
    try:
        for _ in range(50):
            if port_file.exists() and port_file.read_text():
                break
            time.sleep(0.1)
        port = port_file.read_text()
        # The real core configuration, plus the scripted model and final_answer off (as a benchmark would set it).
        patch = root / "run.patch.yml"
        patch.write_text(f"""
- id: agent-default-model
  config: {{provider: scripted, model: scripted}}
- id: llm-pi-ai
  config:
    providers:
      scripted:
        apiKeyEnv: SCRIPTED_API_KEY
        api: openai-completions
        baseURL: http://127.0.0.1:{port}/v1
        compat: {{supportsDeveloperRole: false, supportsStore: false, maxTokensField: max_tokens}}
        models: [{{id: scripted, contextWindow: 131072, maxTokens: 4096}}]
- id: final-answer
  disabled: true
""")
        env = os.environ | {"DSH_HOME": str(home), "DSH_PERMISSION_MODE": "workspace-isolated",
                            "SCRIPTED_API_KEY": "x", "DSH_BENCH_DSH_ROOT": str(DSH),
                            "DSH_BENCH_CONTAINER": container, "DSH_BENCH_RUNTIME": RUNTIME,
                            "DSH_BENCH_CONTAINER_ENV": json.dumps({"WORKSPACE_DIR": str(ws)}),
                            "DSH_BENCH_LIMITS": json.dumps({"maxSteps": 50, "timeoutMs": 240000}),
                            "DSH_BENCH_ANSWERS_DIR": str(root / "answers")}
        proc = subprocess.run([NODE, str(DSH / "apps/cli/lib/bin.js"), "--profile", "headless",
                               "--patch", str(REPO / "harness/core.patch.yml"), "--patch", str(patch),
                               "Run the isolation checks."], cwd=ws, env=env, capture_output=True, text=True, timeout=300)
        (root / "dsh.stdout").write_text(proc.stdout)
        (root / "dsh.stderr").write_text(proc.stderr)
    finally:
        model.terminate()
        (ws / "documents").chmod(0o755)
        leftover = subprocess.run([RUNTIME, "exec", container, "bash", "-c", "ps -eo args | grep -c '^sleep 300' || true"],
                                  capture_output=True, text=True).stdout.strip()
        subprocess.run([RUNTIME, "rm", "-f", container], capture_output=True)

    # Tool results, by step: the last request holds the whole conversation.
    requests = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    results: dict[int, str] = {}
    if requests:
        step = -1
        for message in requests[-1]["messages"]:
            if message.get("role") == "assistant":
                step += 1
            elif message.get("role") == "tool":
                content = message.get("content")
                text = content if isinstance(content, str) else json.dumps(content)
                results[step] = results.get(step, "") + text
    r = lambda i: results.get(i, "<no result>")  # noqa: E731

    checks = [
        ("bash runs in the workspace", str(ws) in r(0)),
        ("bash runs as the host uid", str(os.getuid()) in r(0)),
        ("container env reaches bash", f"WS={ws}" in r(0)),
        ("bash cannot read a host file outside the workspace", "HOSTSECRET" not in r(1)),
        ("bash cannot see the host home", "HOST_HOME_HIDDEN" in r(2)),
        ("bash cannot write a read-only directory", "read-only file system" in r(3).lower() and not (ws / "documents/new.txt").exists()),
        ("bash writes to output/ reach the host", "hello" in r(4) and (ws / "output/a.txt").read_text().strip() == "hello"),
        ("bash has no network", "NET_OK" not in r(5) and "unreachable" in r(5).lower()),
        ("grep runs (ripgrep in the container)", "SECRETDOC" in r(6)),
        ("glob runs (ripgrep in the container)", "brief.txt" in r(7)),
        ("read refuses a path outside the workspace", "HOSTSECRET" not in r(8) and "denied" in r(8).lower()),
        ("write refuses a path outside the workspace", not (root / "written-outside.txt").exists()),
        ("read works inside the workspace", "SECRETDOC" in r(10)),
        ("a timed-out command does not finish", "SLEEP_FINISHED" not in r(11)),
        ("a timed-out command is killed inside the container", r(12).strip().endswith("0") and leftover == "0"),
        ("read refuses a symlink pointing outside the workspace", "HOSTSECRET" not in r(14) and "LINKED" in r(13)),
        ("write tool cannot write a read-only directory", not (ws / "documents/host-write.txt").exists()),
        ("a killed background job stops inside the container", r(18).strip().endswith("0")),
        ("workflow / ralph (host-side JS) not offered", bool(requests) and not {"workflow", "ralph"} & set(requests[0]["tools"])),
        ("final_answer disabled by a later patch row", bool(requests) and "final_answer" not in requests[0]["tools"]
         and "bash" in requests[0]["tools"]),
        ("the run completed", proc.returncode == 0),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed; run dir {root}")
    if failed:
        for i in range(len(steps) - 1):
            print(f"--- step {i}: {r(i)[:400]}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
