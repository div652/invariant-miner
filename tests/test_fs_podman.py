"""Attach-mode test: DSH's file tools (plugins/fs-podman) and commands (sandbox-podman) both work inside a running
container whose workspace exists only there, with the scripted model.

The container (dsh-bench-base, network none) holds /work (the workspace, not on the host) and /secret.txt outside it;
/work/escape is a symlink to /secret.txt. The scripted model reads (absolute and relative path), writes a new file in a
new directory, reads it, edits it, checks it with bash, globs and greps, then tries the secret three ways (absolute
read, the escaping symlink, a write outside the workspace). Checks: every tool result, the prompt's working directory
and DSH's sandbox note (/work), the file as the container sees it, the secret untouched, no file outside /work, the
launcher outputs in attach mode.

    python3 tests/test_fs_podman.py
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME = os.environ.get("RUNTIME", "podman")
DENIED = "file access denied under workspace-isolated mode"


def tool_texts(request: dict) -> list[str]:
    out = []
    for m in request["messages"]:
        if m.get("role") != "tool":
            continue
        c = m.get("content")
        out.append(c if isinstance(c, str) else "".join(p.get("text", "") for p in c if isinstance(p, dict)))
    return out


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-fs-podman-"))
    container = f"dshb-fstest-{uuid.uuid4().hex[:8]}"
    subprocess.run([RUNTIME, "run", "-d", "--name", container, "--network=none", "dsh-bench-base", "sleep", "infinity"],
                   check=True, capture_output=True)
    subprocess.run([RUNTIME, "exec", container, "sh", "-c",
                    "mkdir -p /work/docs && printf 'hello world\\n' > /work/docs/input.txt"
                    " && printf 'TOP SECRET\\n' > /secret.txt && ln -s /secret.txt /work/escape"],
                   check=True, capture_output=True)
    steps = [
        {"calls": [{"name": "read", "args": {"file_path": "/work/docs/input.txt"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "docs/input.txt"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "notes/out.txt", "content": "line1\nline2\n"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "notes/out.txt"}}]},
        {"calls": [{"name": "edit", "args": {"file_path": "notes/out.txt", "old_string": "line1", "new_string": "LINE1"}}]},
        {"calls": [{"name": "bash", "args": {"command": "pwd; cat notes/out.txt", "description": "check"}}]},
        {"calls": [{"name": "glob", "args": {"pattern": "**/*.txt"}}]},
        {"calls": [{"name": "grep", "args": {"pattern": "LINE1"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "/secret.txt"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "escape"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "/tmp/outside.txt", "content": "x"}}]},
        {"calls": [{"name": "final_answer", "args": {"answer": "done"}}]},
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
        (root / "spec.json").write_text(json.dumps({
            "task_id": "fs-podman-smoke",
            "prompt": "Work in {workspace}.",
            "model": str(root / "model.json"),
            "attach": {"container": container, "workspace": "/work"},
            "limits": {"max_steps": 30, "timeout_s": 300},
        }))
        out = root / "run"
        proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"),
                               "--out", str(out)], cwd=REPO, capture_output=True, text=True, timeout=600)
        in_container = subprocess.run([RUNTIME, "exec", container, "sh", "-c",
                                       "cat /work/notes/out.txt; echo ---; cat /secret.txt; echo ---; ls /tmp"],
                                      capture_output=True, text=True).stdout
        still_running = subprocess.run([RUNTIME, "ps", "-q", "--filter", f"name={container}"],
                                       capture_output=True, text=True).stdout.strip() != ""
    finally:
        model_proc.terminate()
        subprocess.run([RUNTIME, "rm", "-f", "-t", "0", container], capture_output=True)
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1

    req = [json.loads(line) for line in log.read_text().splitlines()]
    res = [(tool_texts(r) or [""])[-1] for r in req]  # res[i] = result of step i-1
    record = json.loads((out / "run.json").read_text())
    answer = json.loads((out / "answer.json").read_text())
    system = next((m.get("content") for m in req[0]["messages"] if m.get("role") == "system"), "")
    system = system if isinstance(system, str) else json.dumps(system)
    everything = json.dumps(req[0]["messages"])
    checks = [
        ("all 12 requests made", len(req) == 12),
        ("prompt: working directory is /work", "Your working directory is /work." in system),
        ("DSH sandbox note names /work", 'session workspace: \\"/work\\"' in everything or 'session workspace: "/work"' in everything),
        ("task prompt has the container path", (out / "prompt.txt").read_text() == "Work in /work."),
        ("read absolute path", "hello world" in res[1]),
        ("read relative path", "hello world" in res[2]),
        ("write new file in a new directory", "error" not in res[3].lower() and "notes/out.txt" in res[3]),
        ("read the written file", "line1" in res[4]),
        ("edit the file", "error" not in res[5].lower()),
        ("bash runs in /work and sees the edit", "/work" in res[6] and "LINE1" in res[6]),
        ("glob finds both files", "docs/input.txt" in res[7] and "notes/out.txt" in res[7]),
        ("grep finds the edit", "out.txt" in res[8]),
        ("read outside the workspace: denied", DENIED in res[9] and "TOP SECRET" not in res[9]),
        ("read through an escaping symlink: denied", DENIED in res[10] and "TOP SECRET" not in res[10]),
        ("write outside the workspace: denied", DENIED in res[11]),
        ("container: file content after edit", in_container.startswith("LINE1\nline2\n")),
        ("container: secret untouched, nothing in /tmp", "TOP SECRET" in in_container and "outside.txt" not in in_container),
        ("answer.json: final_answer", answer["finish_reason"] == "final_answer" and answer["answer"] == "done"),
        ("run.json: attach mode (no diff, image recorded, container left running)",
         record["changed_files"] is None and not (out / "workspace.diff").exists()
         and record["image"]["id"] and still_running),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    if failed:
        for i, text in enumerate(res):
            print(f"  res[{i}]: {text[:220]!r}")
        print(proc.stderr[-1500:])
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
