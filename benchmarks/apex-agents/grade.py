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
    goes in the environment, never into a file); no Reducto key, so documents are extracted locally. Calls pass through
    a local relay (JudgeRelay) that strips a markdown fence around the reply when the request asked for JSON
    (response_format): CAO does not pass response_format to Gemini, which then answers ```json ...```, and the grader's
    artifact selector parses strictly (CHECKLIST.md, change 7);
  - grades.json: score (mean criterion score, the grader's own "template" scoring), all_pass (every criterion met:
    the paper's Pass@1 per run), and each criterion's grade and rationale;
  - then, unless --keep-snapshots, the task is compacted: snapshots/changes.tar.gz (files the agent added or modified)
    and snapshots/changes.json (added / modified / deleted) replace the full before/after snapshots and the grader's
    zips (0.5-1.5 GB per task otherwise). A task whose grading failed keeps everything.
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import threading
import urllib.error
import urllib.request
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.endpoints import load_local_env, setting_path  # noqa: E402

GRADING = REPO / "work/archipelago/grading"
EXAMPLE = REPO / "work/archipelago/examples/hugging_face_task"
CAO_BASE = "http://127.0.0.1:4141/v1"
FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*?)\n?\s*```\s*$", re.S)


class JudgeRelay:
    """Local OpenAI-compatible relay to CAO for the grader (one per process, started on first use).

    Forwards every request unchanged. When the request carries response_format and a reply's message content is one
    markdown code fence around JSON, the fence is removed; nothing else in the reply changes.
    """

    _lock = threading.Lock()
    _base: str | None = None

    @classmethod
    def base_url(cls) -> str:
        with cls._lock:
            if cls._base is None:
                server = ThreadingHTTPServer(("127.0.0.1", 0), _RelayHandler)
                threading.Thread(target=server.serve_forever, daemon=True).start()
                cls._base = f"http://127.0.0.1:{server.server_address[1]}/v1"
            return cls._base


class _RelayHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _forward(self, body: bytes | None) -> None:
        request = urllib.request.Request(CAO_BASE.removesuffix("/v1") + self.path, data=body, method=self.command,
                                         headers={k: v for k, v in self.headers.items()
                                                  if k.lower() not in ("host", "content-length", "accept-encoding")})
        try:
            with urllib.request.urlopen(request, timeout=900) as upstream:
                status, headers, payload = upstream.status, upstream.headers, upstream.read()
        except urllib.error.HTTPError as error:
            status, headers, payload = error.code, error.headers, error.read()
        if body and status == 200:
            try:
                if json.loads(body).get("response_format"):
                    reply = json.loads(payload)
                    for choice in reply.get("choices", []):
                        content = (choice.get("message") or {}).get("content")
                        match = FENCE.match(content) if isinstance(content, str) else None
                        if match:
                            choice["message"]["content"] = match.group(1).strip()
                    payload = json.dumps(reply).encode()
            except (ValueError, AttributeError):
                pass  # not JSON on either side: pass the reply through as it came
        self.send_response(status)
        self.send_header("Content-Type", headers.get("Content-Type", "application/json"))
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        self._forward(self.rfile.read(int(self.headers.get("Content-Length", 0))))

    def do_GET(self):
        self._forward(None)


def judge_env(cao_key: str) -> dict[str, str]:
    """Environment for the grader process: the judge goes through the relay, the key stays in the environment."""
    base = JudgeRelay.base_url()
    return os.environ | {"OPENAI_API_KEY": cao_key, "OPENAI_API_BASE": base, "OPENAI_BASE_URL": base}


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


def tar_digests(tar_gz: Path) -> dict[str, str]:
    digests = {}
    with tarfile.open(tar_gz, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                data = tar.extractfile(member)
                digests[member.name.removeprefix("./")] = hashlib.sha256(data.read() if data else b"").hexdigest()
    return digests


def compact(run_dir: Path) -> None:
    """Keep only the agent's changes (added/modified files + a list); drop full snapshots and grader zips."""
    snaps = run_dir / "snapshots"
    before, after = snaps / "before.tar.gz", snaps / "after.tar.gz"
    if not (before.exists() and after.exists()):
        return
    old, new = tar_digests(before), tar_digests(after)
    added = sorted(n for n in new if n not in old)
    modified = sorted(n for n in new if n in old and new[n] != old[n])
    deleted = sorted(n for n in old if n not in new)
    keep = set(added) | set(modified)
    with tarfile.open(after, "r:gz") as src, tarfile.open(snaps / "changes.tar.gz", "w:gz") as dst:
        for member in src.getmembers():
            if member.isfile() and member.name.removeprefix("./") in keep:
                dst.addfile(member, src.extractfile(member))
    (snaps / "changes.json").write_text(json.dumps(
        {"added": added, "modified": modified, "deleted": deleted, "before_files": len(old), "after_files": len(new),
         "after_sha256": {n: new[n] for n in sorted(keep)}}, indent=2) + "\n")
    for path in (before, after, run_dir / "grading/before.zip", run_dir / "grading/after.zip"):
        path.unlink(missing_ok=True)


def verifiers(task: dict) -> list[dict]:
    target = GRADING_TARGET[task["expected_output"]]
    return [{"verifier_id": c["verifier_id"], "verifier_version": 1, "world_id": task["world_id"],
             "task_id": task["task_id"], "eval_config_id": "ec_output_llm",
             "verifier_values": {"criteria": c["criteria"], "is_primary_objective": i == 0,
                                 "expected_file_type": target},
             "verifier_index": i, "verifier_dependencies": None}
            for i, c in enumerate(task["rubric"])]


def grade_task(run_dir: Path, judge: str, effort: str, env: dict[str, str], keep_snapshots: bool = False) -> dict:
    result = grade_once(run_dir, judge, effort, env)
    # Compact a graded task, or one that could not be graded (a limit hit); never one whose grading failed.
    gradable_done = result.get("graded") is True or "reason" in result
    if not keep_snapshots and gradable_done and not result.get("error"):
        compact(run_dir)
    return result


def grade_once(run_dir: Path, judge: str, effort: str, env: dict[str, str]) -> dict:
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
    errors = [c for c in criteria if c["score"] is None or c["status"] == "error"]
    run_failed = grades.get("grading_run_status") == "error"
    scores = [c["score"] for c in criteria if c["score"] is not None]
    result = base | {"graded": not errors and not run_failed, "grading_run_status": grades.get("grading_run_status"),
                     "score": (grades.get("scoring_results") or {}).get("final_score"),
                     "all_pass": bool(scores) and not errors and not run_failed and all(s >= 1.0 for s in scores),
                     "criteria": criteria}
    if errors or run_failed:
        first = next((v.get("message") for v in grades.get("verifier_results", []) if v.get("status") == "error"), "")
        result["error"] = f"{len(errors)} criteria errored (grading run {grades.get('grading_run_status')}): {str(first)[:300]}"
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
    parser.add_argument("--keep-snapshots", action="store_true", help="do not compact graded tasks")
    args = parser.parse_args()
    load_local_env()
    key = Path(setting_path("$DSH_BENCH_CAO_KEY_FILE")).read_text().strip()
    env = judge_env(key)
    dirs = [d for d in task_dirs([p.resolve() for p in args.runs])
            if args.regrade or not (d / "grading/grades.json").exists()]
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for result in pool.map(lambda d: grade_task(d, args.judge, args.effort, env, args.keep_snapshots), dirs):
            print(json.dumps({k: result.get(k) for k in ("task_id", "graded", "score", "all_pass", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
