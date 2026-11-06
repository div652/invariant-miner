"""Grade APEX-Agents runs with Archipelago's grader, unchanged (CHECKLIST.md, row 9).

    python3 benchmarks/apex-agents/grade.py RUN_DIR [RUN_DIR ...] [--jobs 8] [--judge gemini-3.8-flash --effort low]

RUN_DIR is one task's run_task.py output, or a directory of them. Per task, in RUN_DIR/grading/:
  - a run that ended normally is graded: with final_answer, or with a final reply that calls no tool (DSH's own end of
    a turn; the answer is that reply, as for JobBench and Harvey). A run stopped by the step limit, the timeout or an
    error is not graded and scores 0, as in the paper;
  - before.zip / after.zip from the run's snapshots (the grader reads zips);
  - verifiers.json: one output_llm verifier per rubric criterion, with the grading target the paper uses: the task's
    expected_output mapped to the grader's file-type category (Final Answer Only for message_in_console, Word /
    Spreadsheets / Presentations for the file tasks) -- Archipelago's example passes none (change 5);
  - Archipelago's grading runner (work/archipelago/grading, uv) with the judge through CAO (OpenAI-compatible; the key
    goes in the environment, never into a file); no Reducto key, so documents are extracted locally;
  - grades.json: score (mean criterion score, the grader's own "template" scoring), all_pass (every criterion met:
    the paper's Pass@1 per run), and each criterion's grade and rationale.
"""

import argparse
import concurrent.futures
import io
import json
import os
import subprocess
import sys
import tarfile
import uuid
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.endpoints import load_local_env, setting_path  # noqa: E402

GRADING = REPO / "work/archipelago/grading"
EXAMPLE = REPO / "work/archipelago/examples/hugging_face_task"
CAO_BASE = "http://127.0.0.1:4141/v1"
# Run endings that carry an answer: the final_answer tool, or DSH's normal turn end (a reply with no tool call).
ANSWERED = {"final_answer", "completed"}
# Task expected_output -> the grader's grading target (output_llm artifact_filters.FileTypeCategory).
GRADING_TARGET = {
    "message_in_console": "Final Answer Only (No Files)",
    "make_new_doc": "Word Documents (.docx, .doc, .odt)",
    "edit_existing_doc": "Word Documents (.docx, .doc, .odt)",
    "make_new_sheet": "Spreadsheets (.xlsx, .xls, .xlsm, .ods)",
    "edit_existing_sheet": "Spreadsheets (.xlsx, .xls, .xlsm, .ods)",
    "make_new_slide_deck": "Presentations (.pptx, .ppt, .odp)",
    "edit_existing_slide_deck": "Presentations (.pptx, .ppt, .odp)",
}


def tar_to_zip(tar_gz: Path, zip_path: Path) -> None:
    """Regular files only, names as in the archive (Archipelago example's tar_gz_to_zip)."""
    with tarfile.open(tar_gz, "r:gz") as tar, zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for member in tar.getmembers():
            if member.isfile():
                data = tar.extractfile(member)
                if data is not None:
                    zf.writestr(member.name.removeprefix("./"), data.read())


def verifiers(task: dict) -> list[dict]:
    target = GRADING_TARGET[task["expected_output"]]
    return [{"verifier_id": c["verifier_id"], "verifier_version": 1, "world_id": task["world_id"],
             "task_id": task["task_id"], "eval_config_id": "ec_output_llm",
             "verifier_values": {"criteria": c["criteria"], "is_primary_objective": i == 0,
                                 "expected_file_type": target},
             "verifier_index": i, "verifier_dependencies": None}
            for i, c in enumerate(task["rubric"])]


def grade_task(run_dir: Path, judge: str, effort: str, env: dict[str, str]) -> dict:
    task = json.loads((run_dir / "task.json").read_text())
    record = json.loads((run_dir / "run.json").read_text())
    out = run_dir / "grading"
    out.mkdir(exist_ok=True)
    base = {"task_id": task["task_id"], "domain": task["domain"], "expected_output": task["expected_output"],
            "criteria_count": len(task["rubric"]), "finish_reason": record.get("finish_reason")}
    if record.get("finish_reason") not in ANSWERED:
        result = base | {"graded": False, "score": 0.0, "all_pass": False,
                         "reason": f"run ended {record.get('finish_reason')!r} without an answer (counts as failed)"}
        (out / "grades.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    tar_to_zip(run_dir / "snapshots/before.tar.gz", out / "before.zip")
    tar_to_zip(run_dir / "snapshots/after.tar.gz", out / "after.zip")
    (out / "verifiers.json").write_text(json.dumps(verifiers(task), indent=2) + "\n")
    (out / "grading_settings.json").write_text(json.dumps(
        {"llm_judge_model": f"openai/{judge}",
         # LiteLLM's openai provider refuses reasoning_effort for models it has no entry for (gemini-3.8-flash);
         # allowed_openai_params passes it through to CAO, which accepts it.
         "llm_judge_extra_args": {"reasoning_effort": effort, "allowed_openai_params": ["reasoning_effort"]}},
        indent=2) + "\n")
    raw = out / "grades-raw.json"
    argv = ["uv", "run", "--no-sync", "python", "-m", "runner.main",
            "--grading-run-id", f"gr_{uuid.uuid4().hex[:8]}", "--trajectory-id", f"dshb_{task['task_id']}",
            "--initial-snapshot", str(out / "before.zip"), "--final-snapshot", str(out / "after.zip"),
            "--trajectory", str(run_dir / "trajectory.json"),
            "--grading-settings", str(out / "grading_settings.json"), "--verifiers", str(out / "verifiers.json"),
            "--eval-configs", str(EXAMPLE / "eval_configs.json"), "--scoring-config", str(EXAMPLE / "scoring_config.json"),
            "--output", str(raw)]
    proc = subprocess.run(argv, cwd=GRADING, env=env, capture_output=True, text=True)
    (out / "grader.log").write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0 or not raw.exists():
        result = base | {"graded": False, "error": f"grader exit {proc.returncode}; see grading/grader.log"}
        (out / "grades.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    grades = json.loads(raw.read_text())
    by_id = {v["verifier_id"]: v for v in grades.get("verifier_results", [])}
    criteria = []
    for c in task["rubric"]:
        v = by_id.get(c["verifier_id"], {})
        values = v.get("verifier_result_values") or {}
        criteria.append({"verifier_id": c["verifier_id"], "criteria": c["criteria"], "score": v.get("score"),
                         "status": v.get("status"), "judge_grade": values.get("judge_grade"),
                         "rationale": values.get("grade_rationale"), "auto_failed": values.get("auto_failed", False)})
    errors = [c for c in criteria if c["score"] is None]
    scores = [c["score"] for c in criteria if c["score"] is not None]
    result = base | {"graded": not errors, "grading_run_status": grades.get("grading_run_status"),
                     "score": (grades.get("scoring_results") or {}).get("final_score"),
                     "all_pass": bool(scores) and not errors and all(s >= 1.0 for s in scores),
                     "criteria": criteria}
    if errors:
        result["error"] = f"{len(errors)} criteria without a score"
    (out / "grades.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def task_dirs(paths: list[Path]) -> list[Path]:
    found = []
    for path in paths:
        found += [path] if (path / "task.json").exists() else sorted(p.parent for p in path.glob("*/task.json"))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--judge", default="gemini-3.8-flash")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--regrade", action="store_true", help="grade tasks that already have grading/grades.json")
    args = parser.parse_args()
    load_local_env()
    key = Path(setting_path("$DSH_BENCH_CAO_KEY_FILE")).read_text().strip()
    env = os.environ | {"OPENAI_API_KEY": key, "OPENAI_API_BASE": CAO_BASE, "OPENAI_BASE_URL": CAO_BASE}
    dirs = [d for d in task_dirs([p.resolve() for p in args.runs])
            if args.regrade or not (d / "grading/grades.json").exists()]
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for result in pool.map(lambda d: grade_task(d, args.judge, args.effort, env), dirs):
            print(json.dumps({k: result.get(k) for k in ("task_id", "graded", "score", "all_pass", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
