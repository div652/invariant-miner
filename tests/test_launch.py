"""Launcher test: one scripted task through dsh_bench.launch, then the four standard outputs are checked.

The scripted model writes a deliverable with bash, then calls final_answer. Checks: answer.json holds the final_answer
text with finish reason final_answer; workspace.diff holds exactly the deliverable (no staging files, no harness
artifacts); the root session log is complete; run.json records what ran; the system prompt reached the model;
a read-only staged dir stayed unchanged; the container was removed.

    python3 tests/test_launch.py
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNTIME = os.environ.get("RUNTIME", "podman")


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-launch-"))
    src = root / "task-src"
    (src / "docs").mkdir(parents=True)
    (src / "docs" / "input.txt").write_text("the number is 6 times 7\n")
    steps = [
        {"calls": [{"name": "bash", "args": {"command": "cat docs/input.txt && echo 42 > output/answer.txt",
                                             "description": "write deliverable"}}]},
        {"calls": [{"name": "final_answer", "args": {"answer": "The answer is 42.\u2028(U+2028 inside the text)"}}]},
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
            "task_id": "launch-smoke",
            "prompt": "Read docs/input.txt in {workspace} and save the result to output/answer.txt.",
            "system_prompt": "BENCHMARK-SYSTEM-PROMPT-MARKER: you are solving a smoke task.",
            "model": str(root / "model.json"),
            "stage": [{"from": str(src / "docs"), "to": "docs", "readonly": True}],
            "make_dirs": ["output"],
            "container_env": {"WORKSPACE_DIR": "{workspace}"},
            "limits": {"max_steps": 10, "timeout_s": 120},
        }))
        out = root / "run"
        proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"),
                               "--out", str(out)], cwd=REPO, capture_output=True, text=True, timeout=400)
    finally:
        model_proc.terminate()
    print(proc.stdout.strip())
    if proc.returncode not in (0, 1) or not (out / "run.json").exists():
        print(proc.stderr[-3000:])
        return 1

    answer = json.loads((out / "answer.json").read_text())
    record = json.loads((out / "run.json").read_text())
    diff = (out / "workspace.diff").read_text()
    requests = [json.loads(line) for line in log.read_text().splitlines()]
    system = next((m.get("content") for m in requests[0]["messages"] if m.get("role") == "system"), "")
    system = system if isinstance(system, str) else json.dumps(system)
    sessions = list((out / "dsh-home/sessions").rglob("session.v2.jsonl"))
    containers = subprocess.run([RUNTIME, "ps", "-a", "--filter", f"name={record['container']}", "-q"],
                                capture_output=True, text=True).stdout.strip()
    checks = [
        ("answer.json: final_answer text (U+2028 kept)", answer["answer"] == "The answer is 42.\u2028(U+2028 inside the text)"
         and answer["source"] == "final_answer"),
        ("answer.json: finish reason final_answer", answer["finish_reason"] == "final_answer"),
        ("model not called after final_answer", len(requests) == 2),
        ("workspace.diff: exactly the deliverable", [c["path"] for c in record["changed_files"]] == ["output/answer.txt"]
         and "+42" in diff),
        ("workspace: deliverable on disk", (out / "workspace/output/answer.txt").read_text().strip() == "42"),
        ("workspace: read-only dir unchanged", (out / "workspace/docs/input.txt").read_text() == "the number is 6 times 7\n"),
        ("sessions: one complete root session", len(sessions) == 1 and record["root_steps"] == 2),
        ("run.json: DSH commit, image id, patches", bool(record["dsh"]["commit"]) and record["image"]["id"]
         and len(record["patches"]) == 1),
        ("system prompt reached the model", "BENCHMARK-SYSTEM-PROMPT-MARKER" in system and "coding agent" in system),
        ("prompt has the real workspace path", str(out / "workspace") in (out / "prompt.txt").read_text()),
        ("container removed", containers == ""),
    ]
    width = max(len(name) for name, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}")
    failed = [name for name, ok in checks if not ok]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed; run dir {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
