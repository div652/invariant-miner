"""Write one launcher spec per Harvey LAB task (benchmarks/harvey/CHECKLIST.md has the decision behind each field).

    python3 benchmarks/harvey/make_specs.py --tasks <ids.txt | split.json[:split]> --out runs/<run>/specs \
        [--model {repo}/models/luna-cao-direct.json] [--max-steps 200] [--timeout-s 7200]

--tasks: a file of task ids (e.g. firm-knowledge/tasks/001, one per line), or an AHE splits JSON with
`:<split>` (default train), whose task_json_sha256 values are checked against the pinned tasks. Needs
benchmarks/harvey/setup.sh (pinned checkout, image, prepared prompt and skills).

Per task: documents (the task's own, or the shared corpus its `docs_dir` names) are hard-linked read-only into
workspace/documents; the skill scripts are copied to workspace/skills/<name>/scripts; output/ starts empty. The user
prompt is the task's `instructions`, verbatim, as Harvey's harness sends it. task.json (rubric) is never staged.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAB = REPO / "work/harvey-labs"
PREPARED = REPO / "work/harvey-prepared"


def task_ids(spec: str) -> tuple[list[str], dict[str, str]]:
    path, _, split = spec.partition(":")
    if path.endswith(".json"):
        data = json.loads(Path(path).read_text())
        entries = data["splits"][split or "train"]
        return [e["task_id"] for e in entries], {e["task_id"]: e["task_json_sha256"] for e in entries}
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()], {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="{repo}/models/luna-cao-direct.json")
    parser.add_argument("--max-steps", type=int, default=200, help="Harvey's --max-turns default")
    parser.add_argument("--timeout-s", type=int, default=7200)
    args = parser.parse_args()
    if not (PREPARED / "system_prompt.md").exists():
        raise SystemExit("run benchmarks/harvey/setup.sh (or prepare.py) first")
    system_prompt = (PREPARED / "system_prompt.md").read_text()
    skills = sorted(p.parent.name for p in (PREPARED / "skills").glob("*/SKILL.md"))
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
        stage += [{"from": str(PREPARED / "skills" / name / "scripts"), "to": f"skills/{name}/scripts"}
                  for name in skills if (PREPARED / "skills" / name / "scripts").is_dir()]
        spec = {
            "task_id": task_id,
            "prompt": task["instructions"],
            "system_prompt": system_prompt,
            "system_prompt_mode": "append",
            "model": args.model,
            "stage": stage,
            "make_dirs": ["output"],
            "image": "dsh-bench-harvey",
            "network": "none",
            "container_env": {"WORKSPACE_DIR": "{workspace}", "DOCUMENTS_DIR": "{workspace}/documents",
                              "OUTPUT_DIR": "{workspace}/output"},
            "disable": ["tool-web"],
            "skills_dir": str(PREPARED / "skills"),
            "final_answer": False,
            "limits": {"max_steps": args.max_steps, "timeout_s": args.timeout_s, "temperature": None},
            "meta": {"benchmark": "harvey", "lab_commit": "4743403f52c1c1db75f3feb1c8f91fae1bd30296",
                     "task_json_sha256": hashlib.sha256(raw).hexdigest()},
        }
        (args.out / (task_id.replace("/", "__") + ".json")).write_text(json.dumps(spec, indent=2) + "\n")
    print(f"{len(ids)} specs in {args.out}")


if __name__ == "__main__":
    main()
