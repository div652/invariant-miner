"""Write one launcher spec per Harvey LAB task (benchmarks/harvey/CHECKLIST.md has the decision behind each field).

    python3 benchmarks/harvey/make_specs.py --tasks <ids.txt | split.json[:split]> --out runs/<run>/specs \
        [--model {repo}/models/luna-cao.json] [--max-steps 200] [--timeout-s 7200]

--tasks: a file of task ids (e.g. firm-knowledge/tasks/001, one per line), a task-list JSON (`mixed200` = the
200-task all-areas sample of benchmarks/harvey-mixed/; `mixed:train` / `mixed:test` = its 150/50 split), or a splits
JSON with `:<split>`
(train, val, test; trainval = train + val; default train), whose task_json_sha256 values are checked against the
pinned tasks. Shortcuts: `split:<name>` = our 60/20/20 split, benchmarks/harvey/splits.json (make_splits.py);
`ahe:<name>` = the AHE campaigns' 80/20/70 split, benchmarks/harvey/splits-ahe-80-20-70.json (import_ahe_splits.py;
ahe:trainval = the 100 tasks AHE evolved on, ahe:test = the 70 it reported on). `ahe160:<name>` = the same split with
AHE's 80 unused tasks added to train (160/20/70, splits-ahe-160-20-70.json, make_train160_split.py). `ahe:flip` (=
`ahe160:flip`) = the 32 train tasks whose all-pass flips across the three Luna-high base runs (make_flip_subset.py). Needs benchmarks/harvey/setup.sh
(pinned checkout, image, prepared prompt).

Per task: documents (the task's own, or the shared corpus its `docs_dir` names) are hard-linked read-only into
workspace/documents; output/ starts empty. No skills by default (user's decision); --skills registers Harvey's docx /
xlsx / pptx skills with DSH's skill tool (spec key skills_dir, from work/harvey-prepared/skills, see prepare.py) and
stages their scripts at workspace/skills/<name>/scripts/; the system prompt is the same either way. patch.yml adds
Harvey's write path rule. The user
prompt is the task's `instructions`, verbatim, as Harvey's harness sends it. task.json (rubric) is never staged.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dsh_bench.endpoints import ENDPOINTS, model_for  # noqa: E402
from dsh_bench.splits import entries  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAB = REPO / "work/harvey-labs"
PREPARED = REPO / "work/harvey-prepared"


SPLIT_FILES = {"split": HERE / "splits.json", "ahe": HERE / "splits-ahe-80-20-70.json",
               "ahe160": HERE / "splits-ahe-160-20-70.json",
               "mixed": REPO / "benchmarks/harvey-mixed/splits-150-50.json"}
# Task lists by name: JSON files with a top-level "tasks" list of {task_id, task_json_sha256}.
TASK_LISTS = {"mixed200": REPO / "benchmarks/harvey-mixed/sample-200.json"}


def task_ids(spec: str) -> tuple[list[str], dict[str, str]]:
    if spec in TASK_LISTS or (spec.endswith(".json") and "tasks" in json.loads(Path(spec).read_text())
                              and "splits" not in json.loads(Path(spec).read_text())):
        chosen = json.loads(Path(TASK_LISTS.get(spec, spec)).read_text())["tasks"]
        return [e["task_id"] for e in chosen], {e["task_id"]: e["task_json_sha256"] for e in chosen}
    path, _, split = spec.partition(":")
    path = str(SPLIT_FILES.get(path, path))
    if path.endswith(".json"):
        chosen = entries(Path(path), split or "train")  # trainval = train + val: work with only a train and a test set
        return [e["task_id"] for e in chosen], {e["task_id"]: e["task_json_sha256"] for e in chosen}
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()], {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS), help="model server (default: $DSH_BENCH_ENDPOINT, else cao)")
    parser.add_argument("--model", help="a model file; overrides --endpoint's default model")
    parser.add_argument("--max-steps", type=int, default=200, help="Harvey's --max-turns default")
    parser.add_argument("--timeout-s", type=int, default=7200)
    parser.add_argument("--skills", action="store_true",
                        help="register Harvey's docx/xlsx/pptx skills with DSH's skill tool and stage their scripts (off by default)")
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
        if args.skills:
            skills_dir = PREPARED / "skills"
            names = sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
            if not names:
                raise SystemExit("--skills: run benchmarks/harvey/prepare.py first (work/harvey-prepared/skills)")
            spec["skills_dir"] = str(skills_dir)
            spec["stage"] += [{"from": str(skills_dir / n / "scripts"), "to": f"skills/{n}/scripts", "readonly": False}
                              for n in names if (skills_dir / n / "scripts").is_dir()]
            spec["meta"]["skills"] = names
        (args.out / (task_id.replace("/", "__") + ".json")).write_text(json.dumps(spec, indent=2) + "\n")
    print(f"{len(ids)} specs in {args.out}")


if __name__ == "__main__":
    main()
