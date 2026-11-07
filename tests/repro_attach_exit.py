"""Attach mode: DSH must exit promptly after the agent ends, even when its plugins dispose in under 5 s.

The scripted model answers in one step with no tool call. DSH then disposes its plugins and, when that finishes
within 5 s, waits for Node's event loop to drain (no forced exit). fs-podman's helper process once kept the loop alive
forever: the launcher killed DSH at its wall-clock limit (7 of 454 runs of one benchmark). PASS: exit within 30 s.

    python3 tests/repro_attach_exit.py [REPO]
"""
import json, subprocess, sys, tempfile, time, uuid
from pathlib import Path
repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]; root = Path(tempfile.mkdtemp(prefix="hang-repro-"))
c = f"dshb-hang-{uuid.uuid4().hex[:6]}"
subprocess.run(["podman", "run", "-d", "--name", c, "--network=none", "dsh-bench-base", "sleep", "infinity"], check=True, capture_output=True)
subprocess.run(["podman", "exec", c, "mkdir", "-p", "/work"], check=True)
(root / "script.json").write_text(json.dumps([{"text": "The answer is 42."}]))
port_file = root / "port.txt"
m = subprocess.Popen([sys.executable, str(repo / "tests/scripted_model.py"), "--script", str(root / "script.json"),
                      "--log", str(root / "req.jsonl"), "--port-file", str(port_file)])
for _ in range(50):
    if port_file.exists() and port_file.read_text(): break
    time.sleep(0.1)
(root / "model.json").write_text(json.dumps({"provider": "scripted", "model": "scripted", "api": "openai-completions",
    "base_url": f"http://127.0.0.1:{port_file.read_text()}/v1", "context_window": 131072, "max_tokens": 4096,
    "compat": {"supportsDeveloperRole": False, "supportsStore": False, "maxTokensField": "max_tokens"}}))
(root / "spec.json").write_text(json.dumps({"task_id": "hang", "prompt": "Answer.", "model": str(root / "model.json"),
    "attach": {"container": c, "workspace": "/work"}, "limits": {"max_steps": 5, "timeout_s": 60}, "grace_s": 60}))
t0 = time.monotonic()
p = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"), "--out", str(root / "run")],
                   cwd=repo, capture_output=True, text=True)
elapsed = time.monotonic() - t0
m.terminate(); subprocess.run(["podman", "rm", "-f", "-t", "0", c], capture_output=True)
r = json.loads((root / "run/run.json").read_text())
print(json.dumps({"repo": repo.name, "finish": r.get("finish_reason"), "agent_s": r.get("agent_s"),
                  "killed_after_s": r.get("killed_after_s"), "launcher_s": round(elapsed, 1)}))
print("PASS  DSH exited promptly after a one-step answer" if r.get("killed_after_s") is None and elapsed < 30
      else "FAIL  DSH did not exit (killed at the launcher's limit)")
sys.exit(0 if r.get("killed_after_s") is None and elapsed < 30 else 1)
