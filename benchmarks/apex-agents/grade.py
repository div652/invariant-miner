"""Grade APEX-Agents 1.1 runs with Mercor's own 1.1 grader image (CHECKLIST.md, decision 7 and "How a task runs").

    python3 benchmarks/apex-agents-1.1/grade.py RUN_DIR [RUN_DIR ...] [--jobs 6] [--regrade] [--keep-snapshots]
        [--judge gemini-3.8-flash] [--effort high]

RUN_DIR is one task's run_task.py output, or a directory of them. Per task, in RUN_DIR/grading/:
  - graded only when the run ended as Mercor's loop grades it: a reply without tool calls, or the step limit (run.json
    graded_ending). A 3 h timeout, an agent error or an infrastructure error is not graded and scores 0 (reason in
    grades.json); run_all retries infrastructure errors first.
  - tests/: the task's tests/ (Mercor's test.sh, grade.py, atif.py, golden files, grading_config.json), unchanged except
    the judge in grading_config.json's grading_settings: model gemini-3.8-flash through CAO (OpenAI-compatible) and
    extra args {temperature 0.1 (Mercor's), reasoning_effort high} instead of deepseek-v4-flash-0731 on Vercel. The judge
    system prompt (with its scattergunning guard) and everything else stay as Mercor wrote them.
  - Mercor's verifier image (digest from tests/Dockerfile, which Harbor builds as FROM + COPY tests: mounted here
    instead) runs like Harbor's verifier: `sh /tests/test.sh`, with /logs/agent/trajectory.json and
    /logs/world/{initial,final}_snapshot.tar.gz from the run, /logs/verifier and /logs/artifacts written here; 2 CPUs /
    8 GB and 3600 s ([verifier] in task.toml); host network, to reach the judge relay on 127.0.0.1. The judge is
    `openai/<model>` for LiteLLM with OPENAI_API_BASE (the relay) and OPENAI_API_KEY in the environment (a variable
    task.toml passes to the verifier), never in a file. (Not LITELLM_PROXY_*: with those LiteLLM switches to its proxy
    mode and sends the model name with its `openai/` prefix, which the endpoint rejects.)
  - The relay (as in v1, JudgeRelay) forwards to CAO; for JSON requests (response_format) it removes a markdown fence
    around the reply and escapes raw control characters inside strings: CAO does not pass response_format to Gemini.
  - grades.json: score (final_score of the task's scoring config), all_pass (every criterion met: Pass@1 per run),
    each criterion with its score and the judge's rationale.
  - then, unless --keep-snapshots, the run is compacted: world-logs/changes.tar.gz (files added or modified in the
    world, from the final snapshot) and changes.json replace the two full snapshots; the tests copy is removed.
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import tomllib
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.endpoints import load_local_env, setting_path  # noqa: E402

RUNTIME = "podman"
JUDGE_MODEL, JUDGE_EFFORT = "gemini-3.8-flash", "high"
CAO_BASE = "http://127.0.0.1:4141/v1"
FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*?)\n?\s*```\s*$", re.S)


def clean_json_reply(content: str) -> str:
    """A reply to a JSON request, as JSON the grader can parse: one surrounding markdown fence removed, and raw
    control characters inside strings escaped by re-serializing. Values are not changed; text that is not JSON even
    leniently is returned as it came (after fence removal)."""
    match = FENCE.match(content)
    text = match.group(1).strip() if match else content
    try:
        json.loads(text)
        return text
    except ValueError:
        pass
    try:
        return json.dumps(json.loads(text, strict=False))
    except ValueError:
        return text


class JudgeRelay:
    """Local OpenAI-compatible relay to the judge endpoint (one per process, started on first use)."""

    _lock = threading.Lock()
    _base: str | None = None
    upstream: str = CAO_BASE

    @classmethod
    def base_url(cls) -> str:
        with cls._lock:
            if cls._base is None:
                cls.upstream = os.environ.get("DSH_BENCH_JUDGE_BASE_URL") or CAO_BASE
                server = ThreadingHTTPServer(("127.0.0.1", 0), _RelayHandler)
                threading.Thread(target=server.serve_forever, daemon=True).start()
                cls._base = f"http://127.0.0.1:{server.server_address[1]}/v1"
            return cls._base


class _RelayHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _forward(self, body: bytes | None) -> None:
        request = urllib.request.Request(JudgeRelay.upstream.removesuffix("/v1") + self.path, data=body, method=self.command,
                                         headers={k: v for k, v in self.headers.items()
                                                  if k.lower() not in ("host", "content-length", "accept-encoding")})
        try:
            with urllib.request.urlopen(request, timeout=900) as upstream:
                status, headers, payload = upstream.status, upstream.headers, upstream.read()
        except urllib.error.HTTPError as error:
            status, headers, payload = error.code, error.headers, error.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            status, headers, payload = 502, {}, json.dumps({"error": {"message": f"relay: {error}"}}).encode()
        if body and status == 200:
            try:
                if json.loads(body).get("response_format"):
                    reply = json.loads(payload)
                    for choice in reply.get("choices", []):
                        content = (choice.get("message") or {}).get("content")
                        if isinstance(content, str):
                            choice["message"]["content"] = clean_json_reply(content)
                    payload = json.dumps(reply).encode()
            except (ValueError, AttributeError):
                pass
        self.send_response(status)
        self.send_header("Content-Type", headers.get("Content-Type", "application/json") if headers else "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        self._forward(self.rfile.read(int(self.headers.get("Content-Length", 0))))

    def do_GET(self):
        self._forward(None)


def judge_key() -> str:
    """The judge endpoint's key: DSH_BENCH_JUDGE_KEY_FILE if set, else the CAO key file."""
    load_local_env()
    name = "$DSH_BENCH_JUDGE_KEY_FILE" if os.environ.get("DSH_BENCH_JUDGE_KEY_FILE") else "$DSH_BENCH_CAO_KEY_FILE"
    return Path(setting_path(name)).read_text().strip()


def judge_settings(original: dict, model: str, effort: str) -> dict:
    """Mercor's grading_settings with our judge: model and extra args replaced, the system prompt kept."""
    extra = dict(original.get("llm_judge_extra_args") or {})
    extra |= {"reasoning_effort": effort, "allowed_openai_params": ["reasoning_effort"]}
    return original | {"llm_judge_model": f"openai/{model}", "llm_judge_extra_args": extra}


def tar_digests(path: Path) -> dict[str, str]:
    digests = {}
    with tarfile.open(path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                data = tar.extractfile(member)
                digests[member.name] = hashlib.sha256(data.read() if data else b"").hexdigest()
    return digests


def compact(run_dir: Path) -> None:
    """Keep what the agent changed in the world (added / modified files and the list of deleted ones), drop the two
    full snapshots (each the whole world: 20-450 MB) and the tests copy."""
    logs = run_dir / "world-logs"
    initial, final = logs / "initial_snapshot.tar.gz", logs / "final_snapshot.tar.gz"
    if initial.exists() and final.exists():
        before, after = tar_digests(initial), tar_digests(final)
        added = sorted(set(after) - set(before))
        modified = sorted(n for n in set(after) & set(before) if after[n] != before[n])
        deleted = sorted(set(before) - set(after))
        keep = set(added) | set(modified)
        with tarfile.open(final, "r:gz") as src, tarfile.open(logs / "changes.tar.gz", "w:gz") as dst:
            for member in src.getmembers():
                if member.name in keep:
                    dst.addfile(member, src.extractfile(member))
        (logs / "changes.json").write_text(json.dumps({"added": added, "modified": modified, "deleted": deleted},
                                                      indent=2) + "\n")
        initial.unlink()
        final.unlink()
    shutil.rmtree(run_dir / "grading/tests", ignore_errors=True)


def grade_task(run_dir: Path, model: str = JUDGE_MODEL, effort: str = JUDGE_EFFORT, regrade: bool = False,
               keep_snapshots: bool = False, tasks_dir: Path | None = None) -> dict:
    run_dir = run_dir.resolve()  # podman takes a relative mount source for a named volume
    out = run_dir / "grading"
    if (out / "grades.json").exists() and not regrade:
        return json.loads((out / "grades.json").read_text())
    record = json.loads((run_dir / "run.json").read_text())
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    grades = {"task": record["task"], "task_id": record["task_id"], "graded": False}
    if record.get("infra_error") or not record.get("graded_ending"):
        grades |= {"score": 0.0, "all_pass": False,
                   "reason": "infra_error" if record.get("infra_error") else f"not graded: {record.get('finish_reason')}"}
        (out / "grades.json").write_text(json.dumps(grades, indent=2) + "\n")
        return grades
    sys.path.insert(0, str(HERE))
    import run_task  # noqa: PLC0415 (task loading is defined once, in run_task)
    task = run_task.load_task(tasks_dir or Path(record.get("tasks_dir") or run_task.TASKS_DIR), record["task"])
    tests = out / "tests"
    shutil.copytree(task["dir"] / "tests", tests)
    config = json.loads((tests / "grading_config.json").read_text())
    config["grading_settings"] = judge_settings(config["grading_settings"], model, effort)
    (tests / "grading_config.json").write_text(json.dumps(config, indent=2) + "\n")
    shutil.copy(tests / "grading_config.json", out / "grading_config.json")
    (out / "verifier").mkdir()
    (out / "artifacts").mkdir()
    verifier_env = task["toml"]["verifier"].get("environment", {})
    timeout_s = int(task["toml"]["verifier"].get("timeout_sec", 3600))
    name = f"apex11-grade-{record['task'][:20]}-{uuid.uuid4().hex[:6]}"
    argv = [RUNTIME, "run", "--rm", "--name", name, "--network=host",
            f"--cpus={verifier_env.get('cpus', 2)}", f"--memory={verifier_env.get('memory_mb', 8192)}m",
            "-e", "OPENAI_API_KEY", "-e", f"OPENAI_API_BASE={JudgeRelay.base_url()}",
            "-e", f"OPENAI_BASE_URL={JudgeRelay.base_url()}",
            "-v", f"{tests}:/tests:ro",
            "-v", f"{run_dir / 'trajectory.json'}:/logs/agent/trajectory.json:ro",
            "-v", f"{run_dir / 'world-logs'}:/logs/world:ro",
            "-v", f"{out / 'verifier'}:/logs/verifier", "-v", f"{out / 'artifacts'}:/logs/artifacts",
            task["verifier_image"], "sh", "/tests/test.sh"]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s + 300,
                              env=os.environ | {"OPENAI_API_KEY": judge_key()})
        rc, log = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as error:
        subprocess.run([RUNTIME, "rm", "-f", "-t", "0", name], capture_output=True)
        rc, log = -1, f"verifier timed out after {timeout_s + 300} s\n{error.stdout or ''}"
    (out / "verifier.log").write_text(log)
    grades["grade_s"] = round(time.monotonic() - t0, 1)
    details_path = out / "verifier/grade_details.json"
    details = json.loads(details_path.read_text()) if details_path.exists() else {}
    error_path = out / "verifier/grading_error.json"
    if rc != 0 or error_path.exists() or not (out / "verifier/reward.json").exists():
        detail = json.loads(error_path.read_text()).get("detail") if error_path.exists() else f"verifier exit {rc}"
        grades |= {"score": None, "all_pass": False, "error": detail}
        (out / "grades.json").write_text(json.dumps(grades, indent=2) + "\n")
        return grades  # not compacted: everything stays for a look and a --regrade
    texts = {v["verifier_id"]: v["verifier_values"].get("criteria") for v in config["verifiers"]}
    criteria = []
    for result in details.get("verifier_results") or []:
        values = result.get("verifier_result_values") or {}
        criteria.append({"verifier_id": result.get("verifier_id"), "criteria": texts.get(result.get("verifier_id")),
                         "score": result.get("score"), "status": result.get("status"),
                         "judge_grade": values.get("judge_grade"), "artifacts": values.get("evaluated_artifacts"),
                         "rationale": values.get("grade_rationale") or values.get("rationale")})
    score = (details.get("scoring_results") or {}).get("final_score")
    grades |= {"graded": True, "score": score, "all_pass": bool(criteria) and all((c["score"] or 0) >= 1.0 for c in criteria),
               "criteria": criteria, "judge": {"model": model, "effort": effort}}
    (out / "grades.json").write_text(json.dumps(grades, indent=2) + "\n")
    if not keep_snapshots:
        compact(run_dir)
    return grades


def task_dirs(paths: list[Path]) -> list[Path]:
    out = []
    for path in paths:
        if (path / "run.json").exists():
            out.append(path)
        else:
            out += sorted(p.parent for p in path.glob("*/run.json"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--judge", default=JUDGE_MODEL)
    parser.add_argument("--effort", default=JUDGE_EFFORT)
    parser.add_argument("--regrade", action="store_true")
    parser.add_argument("--keep-snapshots", action="store_true")
    parser.add_argument("--tasks-dir", type=Path, default=None)
    args = parser.parse_args()
    load_local_env()
    dirs = task_dirs(args.runs)
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        futures = {pool.submit(grade_task, d, args.judge, args.effort, args.regrade, args.keep_snapshots, args.tasks_dir): d
                   for d in dirs}
        for future in concurrent.futures.as_completed(futures):
            g = future.result()
            print(json.dumps({k: g.get(k) for k in ("task", "graded", "score", "all_pass", "error", "reason", "grade_s")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
