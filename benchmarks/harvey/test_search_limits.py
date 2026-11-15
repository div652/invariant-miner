"""Harvey's glob/grep limits (patch.yml row tool-fs-search): a grep whose raw ripgrep output passes DSH's default 20 MB
must now return its matches, and the search timeout must be 600 s, not 30 s.

    PATH=~/.local/node22/bin:$PATH python3 benchmarks/harvey/test_search_limits.py

Through the real launcher, DSH and task container, with the scripted model (tests/scripted_model.py): the workspace
holds a 60 MB text file of 200 lines of 300 KB (one "document" per line, like the agents' corpus dumps); the model
greps it for a word on every line (ripgrep --json output about 60 MB). Run once with Harvey's patch.yml (expected:
"Found 200 matches"), once without (expected: DSH's raw-output overflow error).
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run(root: Path, with_patch: bool) -> tuple[str, str]:
    steps = [{"calls": [{"name": "grep", "args": {"pattern": "escrow", "path": "documents/dump.tsv"}}]},
             {"calls": [{"name": "final_answer", "args": {"answer": "done"}}]}, {"text": "never"}]
    tag = "patch" if with_patch else "base"
    (root / f"script-{tag}.json").write_text(json.dumps(steps))
    log, port_file = root / f"requests-{tag}.jsonl", root / f"port-{tag}.txt"
    proc = subprocess.Popen([sys.executable, str(REPO / "tests/scripted_model.py"), "--script", str(root / f"script-{tag}.json"),
                             "--log", str(log), "--port-file", str(port_file)])
    try:
        for _ in range(50):
            if port_file.exists() and port_file.read_text():
                break
            time.sleep(0.1)
        model = root / f"model-{tag}.json"
        model.write_text(json.dumps({"provider": "scripted", "model": "scripted", "api": "openai-completions",
                                     "base_url": f"http://127.0.0.1:{port_file.read_text()}/v1", "context_window": 131072,
                                     "max_tokens": 4096, "compat": {"supportsDeveloperRole": False, "supportsStore": False,
                                                                   "maxTokensField": "max_tokens"}}))
        spec = {"task_id": f"search-limits-{tag}", "prompt": "grep the dump", "model": str(model),
                "stage": [{"from": str(root / "docs"), "to": "documents", "readonly": True}], "image": "dsh-bench-harvey",
                "extra_patches": [str(REPO / "benchmarks/harvey/patch.yml")] if with_patch else [],
                "limits": {"max_steps": 5, "timeout_s": 300}}
        (root / f"spec-{tag}.json").write_text(json.dumps(spec))
        out = root / f"run-{tag}"
        subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / f"spec-{tag}.json"), "--out", str(out)],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    finally:
        proc.terminate()
    reqs = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    tools = [m for m in reqs[1]["messages"] if m.get("role") == "tool"] if len(reqs) > 1 else []
    content = tools[-1]["content"] if tools else ""
    text = content if isinstance(content, str) else "".join(p.get("text", "") for p in content)
    composed = ""
    patch_copy = out / "extra-0-patch.yml"
    if patch_copy.exists():
        composed = patch_copy.read_text()
    return text, composed


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="hv-search-limits-"))
    (root / "docs").mkdir()
    line = ("lorem ipsum dolor sit amet " * 11000)[:299000] + " escrow agreement\n"
    (root / "docs/dump.tsv").write_text(line * 200)
    with_text, composed = run(root, True)
    base_text, _ = run(root, False)
    checks = [
        ("patch row reaches the run", "rawOutputMaxBytes: 500000000" in composed and "timeoutMs: 600000" in composed),
        ("with Harvey's patch: grep returns its matches", with_text.startswith("Found 200 matches")),
        ("with Harvey's patch: lines still cut at 2,000 bytes", "(line truncated)" in with_text),
        ("without it: DSH's 20 MB overflow error", "more raw output than the subprocess seam retained" in base_text),
    ]
    width = max(len(n) for n, _ in checks)
    for n, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{width}}")
    failed = [n for n, ok in checks if not ok]
    if failed:
        print("with patch:", with_text[:300]); print("without:", base_text[:300])
    print(f"{len(checks) - len(failed)}/{len(checks)} passed; {root}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
