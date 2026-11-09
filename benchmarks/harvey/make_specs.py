"""Write one launcher spec per Harvey LAB task (benchmarks/harvey/CHECKLIST.md has the decision behind each field).

    python3 benchmarks/harvey/make_specs.py --tasks <ids.txt | split.json[:split]> --out runs/<run>/specs \
        [--model {repo}/models/luna-cao.json] [--max-steps 200] [--timeout-s 7200]

--tasks: a file of task ids (e.g. firm-knowledge/tasks/001, one per line), or an AHE splits JSON with
`:<split>` (default train; trainval = train + val), whose task_json_sha256 values are checked against the pinned
tasks; `split:<name>` is the shared split, benchmarks/harvey/splits.json (make_splits.py). Needs
benchmarks/harvey/setup.sh (pinned checkout, image, prepared prompt).

Per task: documents (the task's own, or the shared corpus its `docs_dir` names) are hard-linked read-only into
workspace/documents; output/ starts empty. No skills (user's decision). patch.yml adds Harvey's write path rule. The user
prompt is the task's `instructions`, verbatim, as Harvey's harness sends it. task.json (rubric) is never staged.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dsh_bench.endpoints import ENDPOINTS, model_for  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAB = REPO / "work/harvey-labs"
PREPARED = REPO / "work/harvey-prepared"


def task_ids(spec: str) -> tuple[list[str], dict[str, str]]:
    path, _, split = spec.partition(":")
    if path == "split":  # split:NAME = the shared split, benchmarks/harvey/splits.json (make_splits.py)
        path, split = str(HERE / "splits.json"), split
    if path.endswith(".json"):
        data = json.loads(Path(path).read_text())
        split = split or "train"
        # trainval = train + val: for work with only a train and a test set
        entries = data["splits"]["train"] + data["splits"]["val"] if split == "trainval" else data["splits"][split]
        return [e["task_id"] for e in entries], {e["task_id"]: e["task_json_sha256"] for e in entries}
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()], {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS), help="model server (default: $DSH_BENCH_ENDPOINT, else cao)")
    parser.add_argument("--model", help="a model file; overrides --endpoint's default model")
    parser.add_argument("--max-steps", type=int, default=200, help="Harvey's --max-turns default")
    parser.add_argument("--timeout-s", type=int, default=7200)
    args = parser.parse_args()
    model = model_for(args.endpoint, args.model)
    if not (PREPARED / "system_prompt.md").exists():
        raise SystemExit("run benchmarks/harvey/setup.sh (or prepare.py) first")
    system_prompt = (PREPARED / "system_prompt.md").read_text()
    ids, expected = task_ids(args.tasks)
    args.out.mkdir(parents=True, exist_ok=True)
    for task_id in ids:
        task_dir = LAB / "tasks" / task_id
        raw = (task_dir / "task.json").read_bytes()
        if task_id in expected and hashlib.sha256(raw).hexdigest() != expected[task_id]:
            raise SystemExit(f"{task_id}: task.json differs from the split's recorded sha256")
        task = json.loads(raw)
        docs = (task_dir / task["docs_dir"]).resolve() if task.get("docs_dir") else task_dir / "documents"
        if not docs.is_dir():
            raise SystemExit(f"{task_id}: documents directory missing: {docs}")
        stage = [{"from": str(docs), "to": "documents", "readonly": True, "method": "hardlink"}]
        spec = {
            "task_id": task_id,
            "prompt": task["instructions"],
            "system_prompt": system_prompt,
            "system_prompt_mode": "append",
            "model": model,
            "stage": stage,
            "make_dirs": ["output"],
            "image": "dsh-bench-harvey",
            "network": "none",
            "container_env": {"WORKSPACE_DIR": "{workspace}", "DOCUMENTS_DIR": "{workspace}/documents",
                              "OUTPUT_DIR": "{workspace}/output"},
            "disable": ["tool-web"],
            "extra_patches": [str(HERE / "patch.yml")],
            "final_answer": False,
            "limits": {"max_steps": args.max_steps, "timeout_s": args.timeout_s, "temperature": None},
            "meta": {"benchmark": "harvey", "lab_commit": "4743403f52c1c1db75f3feb1c8f91fae1bd30296",
                     "task_json_sha256": hashlib.sha256(raw).hexdigest()},
        }
        (args.out / (task_id.replace("/", "__") + ".json")).write_text(json.dumps(spec, indent=2) + "\n")
    print(f"{len(ids)} specs in {args.out}")


if __name__ == "__main__":
    main()
