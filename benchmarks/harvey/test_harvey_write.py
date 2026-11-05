"""Harvey's write path rule on DSH (plugins/harvey-write.mjs), with the scripted model.

    python3 benchmarks/harvey/test_harvey_write.py

write("response.md") -> output/response.md; write("output/notes.md") -> output/notes.md (not output/output/);
write(<absolute workspace path>) -> as given; write("../../escape.md") -> refused (output/../../ is outside the workspace); the tool
description says where relative paths go; edit("response.md") afterwards resolves against the workspace (DSH's rule).
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-hvwrite-"))
    out = root / "run"
    ws = out / "workspace"
    steps = [
        {"calls": [{"name": "write", "args": {"file_path": "response.md", "content": "# Answer\n\nfirst draft\n"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "output/notes.md", "content": "notes\n"}}]},
        {"calls": [{"name": "write", "args": {"file_path": str(ws / "scratch.md"), "content": "scratch\n"}}]},
        {"calls": [{"name": "write", "args": {"file_path": "../../escape.md", "content": "x\n"}}]},
        {"calls": [{"name": "edit", "args": {"file_path": "response.md", "old_string": "first draft",
                                             "new_string": "final"}}]},
        {"text": "done"},
    ]
    (root / "script.json").write_text(json.dumps(steps))
    log, port_file = root / "requests.jsonl", root / "port.txt"
    model = subprocess.Popen([sys.executable, str(REPO / "tests/scripted_model.py"), "--script", str(root / "script.json"),
                              "--log", str(log), "--port-file", str(port_file)])
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
            "task_id": "harvey-write", "prompt": "write the answer", "model": str(root / "model.json"),
            "make_dirs": ["output"], "final_answer": False, "limits": {"max_steps": 20, "timeout_s": 120},
            "extra_patches": [str(REPO / "benchmarks/harvey/patch.yml")]}))
        subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"), "--out", str(out)],
                       cwd=REPO, capture_output=True, timeout=300)
    finally:
        model.terminate()
    requests = [json.loads(line) for line in log.read_text().split("\n") if line]
    results, step = {}, -1
    for message in requests[-1]["messages"]:
        if message["role"] == "assistant":
            step += 1
        elif message["role"] == "tool":
            results[step] = message["content"] if isinstance(message["content"], str) else json.dumps(message["content"])
    record = json.loads((out / "run.json").read_text())
    for i in range(5):
        print(f"--- step {i}: {results.get(i, '<none>')[:160]!r}")
    checks = [
        ("relative path -> output/", (ws / "output/response.md").exists() and not (ws / "response.md").exists()),
        ("output/... is not prefixed again", (ws / "output/notes.md").exists() and not (ws / "output/output").exists()),
        ("absolute path used as is", (ws / "scratch.md").exists()),
        ("path outside the workspace refused", not (out / "escape.md").exists()),
        ("edit resolves against the workspace (DSH's rule)", "final" not in (ws / "output/response.md").read_text()),
        ("diff has exactly the three written files", sorted(c["path"] for c in record["changed_files"])
         == ["output/notes.md", "output/response.md", "scratch.md"]),
    ]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n{sum(ok for _, ok in checks)}/{len(checks)} passed; run dir {out}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
