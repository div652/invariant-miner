"""Write one launcher spec per JobBench task (benchmarks/jobbench/CHECKLIST.md has the decisions behind each field).

    python3 benchmarks/jobbench/make_specs.py --dataset ~/job-bench-eval/dataset/main \
        --tasks benchmarks/jobbench/train-20.txt --out runs/<run>/specs [--model models/luna-cao.json]

--tasks: a file of task ids (<profession>/<taskN>, one per line) or "all". Each task's task_folder/ is staged as
workspace/task_folder (writable, as in the reference runner); the grading material next to it (RUBRICS.json,
task_card.md, files_required_to_search) is not staged. The prompt is the reference runner's, byte for byte, with its
temporary paths replaced by the workspace's.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dsh_bench.endpoints import ENDPOINTS, model_for  # noqa: E402

HERE = Path(__file__).resolve().parent

# eval/run_benchmark_dsh_nobwrap.sh (job-bench-eval + agentic-evolution patches), with
# $temp_task_folder = {workspace}/task_folder, $temp_output_dir = {workspace}/output, $workspace = {workspace}.
PROMPT = """=== TASK FOLDER ===
{workspace}/task_folder

=== INSTRUCTIONS ===
1. Read TASK_INSTRUCTIONS.txt in the task folder.
2. Read the reference files named by those instructions.
3. Complete the requested task.
4. Save only final deliverables in the output directory below.

=== OUTPUT DIRECTORY ===
{workspace}/output

IMPORTANT:
- Only access files inside {workspace}.
- Put every final deliverable in {workspace}/output.
- Do not put temporary or intermediate files in the output directory.
- Use available command-line and Python tools when a document format cannot be read directly.
- Resolve conflicting evidence explicitly and justify the selected interpretation."""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True, help="JobBench dataset/<split> directory")
    parser.add_argument("--tasks", required=True, help='file of task ids, or "all"')
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS), help="model server (default: $DSH_BENCH_ENDPOINT, else cao)")
    parser.add_argument("--model", help="a model file; overrides --endpoint's default model")
    parser.add_argument("--timeout-s", type=int, default=7200)
    parser.add_argument("--network", default="pasta", help='container network ("none" turns bash networking off)')
    args = parser.parse_args()
    model = model_for(args.endpoint, args.model)

    dataset = args.dataset.expanduser().resolve()
    if args.tasks == "all":
        ids = sorted(str(p.parent.relative_to(dataset)) for p in dataset.glob("*/task*/task_folder"))
    else:
        ids = [line.strip() for line in Path(args.tasks).read_text().splitlines() if line.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    for task_id in ids:
        folder = dataset / task_id / "task_folder"
        if not (folder / "TASK_INSTRUCTIONS.txt").exists():
            raise SystemExit(f"not a JobBench task: {folder}")
        spec = {
            "task_id": task_id,
            "prompt": PROMPT,
            "model": model,
            "stage": [{"from": str(folder), "to": "task_folder", "readonly": False}],
            "make_dirs": ["output"],
            "image": "dsh-bench-jobbench",
            "network": args.network,
            "final_answer": False,
            "limits": {"max_steps": None, "timeout_s": args.timeout_s, "temperature": None},
            "extra_patches": [str(HERE / "patch.yml")],
            "dsh_env": {"DSH_JOBBENCH_EXA_BASE_URL": "http://127.0.0.1:8010"},
            "dsh_env_files": {"EXA_API_KEY": "~/.config/evolve_agents/model_serve_local.token"},
            "meta": {"benchmark": "jobbench", "dataset": str(dataset)},
        }
        (args.out / (task_id.replace("/", "__") + ".json")).write_text(json.dumps(spec, indent=2) + "\n")
    print(f"{len(ids)} specs in {args.out}")


if __name__ == "__main__":
    main()
