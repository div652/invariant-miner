"""Command line (TECHNICAL.md 5): prepare / run / report / job / ping."""

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

from . import config as config_mod
from . import jobs, report
from .agent import run_agent
from .models import make_conversation
from .pipeline import Pipeline
from .store import Store
from .trajectory import Trajectory, parse_session


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def prepare(manifest_path: Path, config_path: Path | None, out: Path) -> None:
    """manifest.json: {"trajectories": [{"id", "task_id", "label": "pass"|"fail", "session_log"}],
                       "tasks": [{"task_id", "p1", "p2"}], "benchmark_context": optional path to a text file}"""
    m = json.loads(Path(manifest_path).read_text())
    cfg = config_mod.load(config_path)
    trajs = {t["id"]: t for t in m["trajectories"]}
    if len(trajs) != len(m["trajectories"]):
        sys.exit("trajectory ids must be unique")
    for t in trajs.values():
        if t.get("label") not in ("pass", "fail"):
            sys.exit(f"{t['id']}: label must be pass or fail")
    for task in m["tasks"]:
        for p in ("p1", "p2"):
            t = trajs.get(task[p])
            if not t or t["task_id"] != task["task_id"] or t["label"] != "pass":
                sys.exit(f"task {task['task_id']}: {p} = {task[p]} must be a passing trajectory of that task")
        if task["p1"] == task["p2"]:
            sys.exit(f"task {task['task_id']}: p1 and p2 must differ")
    out = Path(out)
    if (out / "state.sqlite").exists():
        sys.exit(f"{out} already has a run")
    (out / "trajectories").mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    (out / "manifest.json").write_text(json.dumps(m, indent=1))
    if m.get("benchmark_context"):
        shutil.copy(m["benchmark_context"], out / "benchmark_context.txt")
    s = Store(out / "state.sqlite")
    task_ids = {task["task_id"] for task in m["tasks"]}
    for t in trajs.values():
        if t["task_id"] not in task_ids:
            continue
        tr = parse_session(Path(t["session_log"]), t["id"], t["task_id"], t["label"])
        rel = f"trajectories/{safe(t['id'])}.json"
        tr.save(out / rel)
        s.x("INSERT INTO trajectories VALUES (?,?,?,?,?,?,?)", t["id"], t["task_id"], t["label"], tr.data["source"], rel,
            len(tr.steps()), tr.est_tokens())
    for n, task in enumerate(m["tasks"], 1):
        s.x("INSERT INTO tasks (task_id, seq, p1, p2, status) VALUES (?,?,?,?,?)", task["task_id"], n, task["p1"], task["p2"], "pending")
    print(f"prepared {out}: {len(m['tasks'])} tasks, {s.one('SELECT COUNT(*) n FROM trajectories')['n']} trajectories")


def run_one_job(run_dir: Path, kind: str, trajectories: dict, inputs: dict, model_key: str | None) -> None:
    cfg = config_mod.load(Path(run_dir) / "config.json")
    s = Store(Path(run_dir) / "state.sqlite")
    trajs = {}
    for name, tid in trajectories.items():
        row = s.one("SELECT json_path FROM trajectories WHERE id=?", tid)
        trajs[name] = Trajectory.load(Path(run_dir) / row["json_path"])
    model_key = model_key or cfg["roles"][kind]
    spec = jobs.build(kind, model_key, inputs, trajs)
    jd = Path(run_dir) / "jobs" / f"manual-{time.strftime('%Y%m%dT%H%M%S')}-{kind}"
    res = run_agent(spec, lambda sp, tools: make_conversation(cfg, sp.model_key, sp.system, sp.user_text, tools), cfg, jd)
    print(json.dumps({"ok": res.ok, "output": res.output, "error": res.error, "steps": res.steps, "tokens_in": res.tokens_in,
                      "tokens_out": res.tokens_out, "seconds": round(res.ended - res.started, 1), "job_dir": str(jd)},
                     ensure_ascii=False, indent=1))


def ping(config_path: Path | None) -> None:
    cfg = config_mod.load(config_path)
    tool = [{"name": "submit", "description": "Submit the answer.", "parameters": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}}]
    for key in cfg["models"]:
        t = time.time()
        try:
            conv = make_conversation(cfg, key, "Answer with the submit tool.", "Submit the answer OK.", tool)
            st = conv.step()
            print(f"{key}: ok ({time.time() - t:.1f} s): calls {[c.name for c in st.calls]}")
        except Exception as e:
            print(f"{key}: FAILED: {type(e).__name__}: {e}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="python3 -m invariant_mining", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare", help="normalize trajectories and create the run's state")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--config", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("run", help="run the pipeline (resumable)")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--tasks", nargs="*")
    p.add_argument("--concurrency", type=int)
    p = sub.add_parser("report", help="write report.md and report.json")
    p.add_argument("run_dir", type=Path)
    p = sub.add_parser("job", help="run one job by hand (not recorded in the state)")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--kind", required=True, choices=jobs.KINDS)
    p.add_argument("--trajectories", required=True, help="A=id,B=id for f1_propose; T=id otherwise")
    p.add_argument("--inputs", default="{}", help="JSON object, or @file.json")
    p.add_argument("--model", help="model key from the config (default: the kind's role)")
    p = sub.add_parser("ping", help="one tiny request to each configured model")
    p.add_argument("--config", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "prepare":
        prepare(a.manifest, a.config, a.out)
    elif a.cmd == "run":
        cfg = config_mod.load(a.run_dir / "config.json")
        if a.concurrency:
            cfg["concurrency"] = a.concurrency
        Pipeline(a.run_dir, cfg).run(a.tasks)
        rep = report.write(a.run_dir)
        print(json.dumps(rep["totals"], indent=1))
    elif a.cmd == "report":
        rep = report.write(a.run_dir)
        print(json.dumps(rep["totals"], indent=1))
    elif a.cmd == "job":
        trajs = dict(kv.split("=", 1) for kv in a.trajectories.split(","))
        inputs = json.loads(Path(a.inputs[1:]).read_text() if a.inputs.startswith("@") else a.inputs)
        run_one_job(a.run_dir, a.kind, trajs, inputs, a.model)
    elif a.cmd == "ping":
        ping(a.config)
