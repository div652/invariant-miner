"""Run a trajectory script in a fresh task workspace and container, and check it against the recorded run.

    python3 benchmarks/harvey/trace2script/run_script.py SCRIPT_DIR --out runs/t2s-<name>-<stamp> [--mode replay|live] [--grade]

SCRIPT_DIR holds mechanical.py (from trace2script.py) and/or solve.py (its semantic version), recorded.json and
meta.json; --file picks one (default solve.py if present). Steps:
1. the task's launcher spec (benchmarks/harvey/make_specs.py), then the workspace staged and the container started
   exactly as dsh_bench/launch.py does (documents hard-linked read-only, output/ empty, same image, env, mounts);
2. `solve(T)` with T = dsh_tools.Tools on that workspace and container; semantic functions (semantic.py) use the
   recorded decision in replay mode and their own implementation in live mode;
3. the container is removed; OUT/tasks/<task>/ gets spec.json, run.json, answer.json, calls.jsonl, semantic.jsonl
   and workspace/, the layout benchmarks/harvey/grade.py reads (--grade runs it);
4. fidelity.json + a printed summary: every call's output against the recorded one (workspace paths, spill paths and
   goal ids normalised; grep compared as a set of lines), and each output/ file against the source run's.
"""

import argparse
import asyncio
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
from dsh_bench.launch import load_spec, stage, start_container  # noqa: E402
from dsh_tools import WS_MARK, Tools  # noqa: E402
import semantic  # noqa: E402

SPILL = re.compile(r"/tmp/(?:tmp)?dsh-spill-[^\s/]+/session-[0-9a-f]+/[0-9a-f]+-[a-z_]+(?:-results)?\.txt")
GOAL = re.compile(r"goal-[0-9a-f-]{36}")
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}\.\d+")  # e.g. onnxruntime warnings parse-doc prints


def norm(text: str, ws: str) -> str:
    return STAMP.sub("<TIME>", GOAL.sub("goal-<id>", SPILL.sub("<SPILL>", (text or "").replace(ws, WS_MARK))))


def compare(tool: str, got: str, want: str) -> tuple[str, float, str]:
    if got == want:
        return "same", 1.0, ""
    if tool == "grep" and sorted(got.split("\n")) == sorted(want.split("\n")):
        return "same lines, other order", 1.0, ""
    a, b = want.split("\n"), got.split("\n")
    ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    hint = f"line {first + 1}: recorded {a[first][:90]!r} / replay {b[first][:90]!r}" if first < min(len(a), len(b)) \
        else f"recorded {len(a)} lines / replay {len(b)} lines"
    return "differs", round(ratio, 3), hint


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=["replay", "live"], default="replay")
    parser.add_argument("--keep-container", action="store_true")
    parser.add_argument("--grade", action="store_true")
    parser.add_argument("--file", help="script file in SCRIPT_DIR (default: solve.py if present, else mechanical.py)")
    args = parser.parse_args()
    sdir = args.script_dir.resolve()
    script = sdir / (args.file or ("solve.py" if (sdir / "solve.py").exists() else "mechanical.py"))
    meta = json.loads((sdir / "meta.json").read_text())
    recorded = json.loads((sdir / "recorded.json").read_text())
    task_id = meta["task_id"]
    name = task_id.replace("/", "__")
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; use a new directory")
    (out / "specs").mkdir(parents=True)
    ids = Path(tempfile.mkstemp(suffix=".txt")[1])
    ids.write_text(task_id + "\n")
    subprocess.run([sys.executable, str(REPO / "benchmarks/harvey/make_specs.py"), "--tasks", str(ids),
                    "--out", str(out / "specs")], check=True, capture_output=True)
    spec_file = out / "specs" / f"{name}.json"
    spec = load_spec(spec_file)
    tdir = out / "tasks" / name
    workspace, gitdir = tdir / "workspace", tdir / "baseline.git"
    readonly = stage(spec, workspace, gitdir)
    container = f"t2s-{uuid.uuid4().hex[:10]}"
    env = {k: v.replace("{workspace}", str(workspace)) for k, v in spec["container_env"].items()}
    started = datetime.now(UTC)
    finish, error = "completed", None
    semantic.configure(args.mode, tdir / "semantic.jsonl")
    try:
        start_container(spec, container, workspace, readonly)
        with (tdir / "calls.jsonl").open("w") as log:
            T = Tools(workspace, container, spec["runtime"], env, log=log, recorded=recorded)
            mod_spec = importlib.util.spec_from_file_location("solve", script)
            mod = importlib.util.module_from_spec(mod_spec)
            sys.path.insert(0, str(sdir))
            mod_spec.loader.exec_module(mod)
            asyncio.run(mod.solve(T))
    except Exception as e:  # the script failed: keep what it produced, report the error
        finish, error = "error", f"{type(e).__name__}: {e}"
        raise_later = e
    else:
        raise_later = None
    finally:
        if not args.keep_container:
            subprocess.run([spec["runtime"], "rm", "-f", "-t", "0", container], capture_output=True)
        semantic.close()
    (tdir / "spec.json").write_text(json.dumps(spec, indent=2) + "\n")
    (tdir / "answer.json").write_text(json.dumps({"answer": "", "finish_reason": finish, "error": error}) + "\n")
    (tdir / "run.json").write_text(json.dumps({"task_id": task_id, "finish_reason": finish, "error": error,
                                               "mode": args.mode, "script": str(script),
                                               "started_at": started.isoformat(), "container": container}, indent=2) + "\n")

    # fidelity: every call against the recorded output, and the deliverables against the source run's
    ws = str(workspace.resolve())
    calls = [json.loads(l) for l in (tdir / "calls.jsonl").read_text().splitlines() if l.strip()]
    rows = []
    for c in calls:
        rec = recorded.get(c["id"])
        if rec is None:
            rows.append({"id": c["id"], "tool": c["tool"], "status": "not in recording"})
            continue
        status, ratio, hint = compare(c["tool"], norm(c["output"], ws), norm(rec["output"], meta["recorded_workspace"]))
        rows.append({"id": c["id"], "tool": c["tool"], "status": status, "similarity": ratio, "hint": hint})
    missing = sorted(set(recorded) - {c["id"] for c in calls}, key=lambda x: [int(p) for p in x.split(".")])
    src_out = Path(meta["source_task_dir"]) / "workspace/output"
    files = []
    for f in sorted(set(meta["output_files"]) | {str(p.relative_to(workspace / "output"))
                                                   for p in (workspace / "output").rglob("*") if p.is_file()}):
        a, b = src_out / f, workspace / "output" / f
        files.append({"file": f, "status": "same" if a.exists() and b.exists() and sha(a) == sha(b)
                      else ("missing in replay" if a.exists() else "only in replay") if not (a.exists() and b.exists())
                      else "differs"})
    report = {"task_id": task_id, "mode": args.mode, "finish": finish, "error": error, "calls": rows,
              "recorded_calls_not_made": missing, "output_files": files,
              "summary": {s: sum(1 for r in rows if r["status"] == s) for s in sorted({r["status"] for r in rows})}}
    (tdir / "fidelity.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"{task_id} {script.name} [{args.mode}] {finish}{' - ' + error if error else ''}")
    print(f"  calls: {len(rows)} made, {len(missing)} recorded calls not made; {report['summary']}")
    for r in rows:
        if r["status"] == "differs":
            print(f"    {r['id']:>6} {r['tool']:<10} similarity {r['similarity']:.2f}  {r['hint']}")
    print("  output/: " + ", ".join(f"{f['file']} {f['status']}" for f in files))
    if args.grade and finish == "completed":
        subprocess.run([str(REPO / "work/harvey-labs/.venv/bin/python"), str(REPO / "benchmarks/harvey/grade.py"),
                        str(out)], check=False)
    if raise_later is not None:
        raise raise_later
    return 0


if __name__ == "__main__":
    sys.exit(main())
