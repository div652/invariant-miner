"""Attach as a user: the launcher's attach keys "user" and "umask" (sandbox-podman and fs-podman), with the scripted
model in a dsh-bench-base container.

The container has a user `tester` (uid 22007, extra group `ws`), a workspace /work owned by root:ws (setgid, group
rwx, others nothing) and a root-only /root-only.txt and /work/private.txt. The spec attaches as `tester` with umask 0002, like a world whose
code-execution app runs as its own user. Checks: bash runs as tester with its groups and umask 0002; a file made by
bash and one written by the write tool are both owned by tester, group ws (setgid), mode 664; edit keeps working; the
root-only file stays unreadable to bash and to read.

    python3 tests/test_attach_user.py
"""

import json
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME = "podman"


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
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-attach-user-"))
    container = f"dshb-usertest-{uuid.uuid4().hex[:8]}"
    subprocess.run([RUNTIME, "run", "-d", "--name", container, "--network=none", "dsh-bench-base", "sleep", "infinity"],
                   check=True, capture_output=True)
    subprocess.run([RUNTIME, "exec", container, "sh", "-c",
                    "groupadd -g 20000 ws && useradd -u 22007 -G ws -m tester"
                    " && mkdir /work && chown root:ws /work && chmod 2770 /work"
                    " && printf 'hello\\n' > /work/given.txt && chgrp ws /work/given.txt && chmod 664 /work/given.txt"
                    " && printf 'ROOT ONLY\\n' > /root-only.txt && chmod 600 /root-only.txt"
                    " && printf 'PRIVATE\\n' > /work/private.txt && chown root:root /work/private.txt"
                    " && chmod 600 /work/private.txt"],
                   check=True, capture_output=True)
    steps = [
        {"calls": [{"name": "bash", "args": {"command": "id -un; id -Gn; umask; touch by-bash.txt", "description": "who"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "by-write.txt", "content": "w\n"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "given.txt"}}]},
        {"calls": [{"name": "edit", "args": {"file_path": "given.txt", "old_string": "hello", "new_string": "HELLO"}}]},
        {"calls": [{"name": "bash", "args": {"command": "stat -c '%n %U %G %a' by-bash.txt by-write.txt; cat given.txt",
                                             "description": "stat"}}]},
        {"calls": [{"name": "bash", "args": {"command": "cat /root-only.txt", "description": "secret"}}]},
        {"calls": [{"name": "read", "args": {"file_path": "private.txt"}}]},
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
            "task_id": "attach-user-smoke",
            "prompt": "Work in {workspace}.",
            "model": str(root / "model.json"),
            "attach": {"container": container, "workspace": "/work", "user": "tester", "umask": "0002"},
            "limits": {"max_steps": 20, "timeout_s": 300},
        }))
        out = root / "run"
        proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"),
                               "--out", str(out)], cwd=REPO, capture_output=True, text=True, timeout=600)
    finally:
        model_proc.terminate()
        subprocess.run([RUNTIME, "rm", "-f", "-t", "0", container], capture_output=True)
    print(proc.stdout.strip())
    if not (out / "run.json").exists() or not log.exists():
        print(proc.stderr[-3000:])
        return 1
    req = [json.loads(line) for line in log.read_text().splitlines()]
    res = [(tool_texts(r) or [""])[-1] for r in req]  # res[i] = result of step i-1
    stat = res[5] if len(res) > 5 else ""
    checks = [
        ("all 8 requests made", len(req) == 8),
        ("bash runs as tester, with group ws, umask 0002",
         len(res) > 1 and "tester" in res[1] and "ws" in res[1] and "0002" in res[1]),
        ("write tool: no error", len(res) > 2 and "error" not in res[2].lower()),
        ("edit tool on a group-writable file: no error", len(res) > 4 and "error" not in res[4].lower()),
        ("file made by bash: tester ws 664", "by-bash.txt tester ws 664" in stat),
        ("file made by write: tester ws 664", "by-write.txt tester ws 664" in stat),
        ("edit applied", "HELLO" in stat),
        ("root-only file unreadable to bash", len(res) > 6 and "Permission denied" in res[6] and "ROOT ONLY" not in res[6]),
        ("root-only file in the workspace unreadable to read", len(res) > 7 and "PRIVATE" not in res[7]
         and "error" in res[7].lower()),
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
    sys.exit(main())
