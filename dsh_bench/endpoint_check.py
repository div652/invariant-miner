"""Check an endpoint end to end: one tiny DSH task through it (bash in the base image, no network).

    python3 -m dsh_bench.endpoint_check --endpoint cao|trapi|vscode|vllm [--model models/x.json]

The agent is asked to reason briefly, compute 17*23 with python in bash and reply with the number. Reported: whether
the turn completed, steps, tool calls, reasoning blocks with summary text (none is expected on vscode), and whether
the answer is 391.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dsh_bench.endpoints import ENDPOINTS, REPO, model_for


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS))
    parser.add_argument("--model")
    args = parser.parse_args()
    model = model_for(args.endpoint, args.model).replace("{repo}", str(REPO))
    root = Path(tempfile.mkdtemp(prefix="dsh-bench-endpoint-check-"))
    (root / "spec.json").write_text(json.dumps({
        "task_id": "endpoint-check", "model": model, "final_answer": False, "make_dirs": ["output"],
        "prompt": "Think briefly about what 17*23 is, then compute it with python in bash, then reply with only the number.",
        "limits": {"max_steps": 8, "timeout_s": 600}}))
    proc = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(root / "spec.json"), "--out", str(root / "run")],
                          cwd=REPO, capture_output=True, text=True, env=os.environ)
    run = root / "run"
    if not (run / "run.json").exists():
        print(proc.stdout[-2000:], proc.stderr[-2000:])
        return 1
    record, answer = json.loads((run / "run.json").read_text()), json.loads((run / "answer.json").read_text())
    calls, reasoning, summarized = 0, 0, 0
    for f in run.glob("dsh-home/sessions/**/session.v2.jsonl"):
        for line in f.read_text().split("\n"):
            if '"tool/call"' in line:
                calls += 1
            if '"assistant/message"' in line:
                for block in json.loads(line)["data"]["message"]["content"]:
                    if block.get("type") == "reasoning":
                        reasoning += 1
                        summarized += bool((block.get("text") or "").strip())
    ok = record["finish_reason"] == "completed" and "391" in answer["answer"] and calls > 0
    print(json.dumps({"model_file": model, "finish": record["finish_reason"], "steps": record["root_steps"],
                      "tool_calls": calls, "reasoning_blocks": reasoning, "with_summary_text": summarized,
                      "answer": answer["answer"][:80], "ok": ok, "run": str(run)}, indent=1))
    if not ok:
        print((run / "dsh.stderr").read_text()[-1500:])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
