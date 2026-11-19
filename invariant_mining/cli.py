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


def manifest_from_folder(folder: Path) -> dict:
    """A runs folder: manifest.json with tasks[] = {task_id, folder, runs: {runN: {all_pass, ...}}} and
    <task folder>/runN/session.v2.jsonl. P1/P2 = the first two passing runs in run order; tasks with fewer than two
    passing runs are left out."""
    fm = json.loads((Path(folder) / "manifest.json").read_text())
    trajs, tasks = [], []
    for t in fm["tasks"]:
        runs = sorted(t["runs"].items(), key=lambda kv: int(re.sub(r"\D", "", kv[0]) or 0))
        ids = []
        for run, v in runs:
            log = Path(folder) / t["folder"] / run / "session.v2.jsonl"
            if not log.is_file():
                sys.exit(f"missing {log}")
            tid = f"{t['task_id']}#{run}"
            trajs.append({"id": tid, "task_id": t["task_id"], "label": "pass" if v["all_pass"] else "fail", "session_log": str(log)})
            if v["all_pass"]:
                ids.append(tid)
        if len(ids) >= 2:
            tasks.append({"task_id": t["task_id"], "p1": ids[0], "p2": ids[1]})
    keep = {t["task_id"] for t in tasks}
    return {"source": {"folder": str(folder)}, "trajectories": [t for t in trajs if t["task_id"] in keep], "tasks": tasks}


def prepare(manifest_path: Path, config_path: Path | None, out: Path) -> None:
    """manifest.json: {"trajectories": [{"id", "task_id", "label": "pass"|"fail", "session_log"}],
                       "tasks": [{"task_id", "p1", "p2"}], "benchmark_context": optional path to a text file}"""
    m = json.loads(Path(manifest_path).read_text()) if not isinstance(manifest_path, dict) else manifest_path
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


def add_runs(run_dir: Path, manifest_path: Path) -> None:
    """Add trajectories to a prepared run (manifest: {"trajectories": [{"id", "task_id", "label", "session_log"}]}, tasks
    already in the run). Every active invariant of the task gets a pending cell on each new trajectory; run `run`
    afterwards. The invariants are not proposed again."""
    from . import rules
    m = json.loads(Path(manifest_path).read_text())
    s = Store(Path(run_dir) / "state.sqlite")
    tasks = {r["task_id"] for r in s.q("SELECT task_id FROM tasks")}
    added = cells = 0
    for t in m["trajectories"]:
        if t["task_id"] not in tasks:
            sys.exit(f"{t['id']}: task {t['task_id']} is not in this run")
        if t.get("label") not in ("pass", "fail"):
            sys.exit(f"{t['id']}: label must be pass or fail")
        if s.one("SELECT 1 FROM trajectories WHERE id=?", t["id"]):
            print(f"skip {t['id']}: already in the run")
            continue
        tr = parse_session(Path(t["session_log"]), t["id"], t["task_id"], t["label"])
        rel = f"trajectories/{safe(t['id'])}.json"
        tr.save(Path(run_dir) / rel)
        s.x("INSERT INTO trajectories VALUES (?,?,?,?,?,?,?)", t["id"], t["task_id"], t["label"], tr.data["source"], rel,
            len(tr.steps()), tr.est_tokens())
        cells += rules.add_trajectory_cells(s, t["id"])
        added += 1
    s.event("add_runs", manifest=str(manifest_path), trajectories=added, cells=cells)
    print(f"{run_dir}: {added} trajectories added, {cells} new cells")


def status(run_dir: Path) -> None:
    """Progress of a run (read-only; safe while it runs): cells by state and run label, invariants, open rewordings,
    jobs, request rate, and a rough ETA from the last 10 minutes."""
    s = Store(Path(run_dir) / "state.sqlite")
    now = time.time()
    cells = {(r["label"], r["st"]): r["n"] for r in s.q(
        "SELECT label, CASE WHEN status IN ('done','cancelled') THEN 'final' ELSE status END st, COUNT(*) n FROM cells GROUP BY 1, 2")}
    for label in ("pass", "fail"):
        done = cells.get((label, "final"), 0)
        total = sum(v for (lab, _), v in cells.items() if lab == label)
        print(f"cells on {label}ing runs: {done}/{total} final, {cells.get((label, 'running'), 0)} running, {cells.get((label, 'pending'), 0)} pending")
    print("invariants:", ", ".join(f"{r['status']} {r['n']}" for r in s.q("SELECT status, COUNT(*) n FROM invariants GROUP BY 1")))
    print("tasks:", ", ".join(f"{r['status']} {r['n']}" for r in s.q("SELECT status, COUNT(*) n FROM tasks GROUP BY 1")),
          "| open removals/rewordings:", s.one("SELECT COUNT(*) n FROM triggers WHERE status IN ('waiting','active')")["n"])
    j = s.one("SELECT COUNT(*) n, SUM(model_steps) req, MIN(started) t0 FROM jobs")
    recent = s.one("SELECT COUNT(*) n FROM jobs WHERE ended > ?", now - 600)["n"]
    print(f"jobs done: {j['n']} ({j['req'] or 0} model requests) since {time.strftime('%H:%M', time.localtime(j['t0'] or now))}; "
          f"last 10 min: {recent} jobs ({recent / 10:.1f}/min)")
    left = sum(v for (lab, st), v in cells.items() if st in ("pending", "running"))
    if recent and left:
        per_cell = max(1.0, j["n"] / max(1, sum(v for (lab, st), v in cells.items() if st == "final")))
        mins = left * per_cell / (recent / 10)
        print(f"rough ETA: ~{mins:.0f} min for {left} open cells at ~{per_cell:.1f} jobs per cell (rewordings add more)")


def retry_errors(run_dir: Path) -> None:
    """Put cells that ended in a job error back to pending at the stage they failed in, and failed F1 tasks back to
    pending (e.g. after fixing a validator). Run `run` afterwards. Do not use while a run is in progress."""
    s = Store(Path(run_dir) / "state.sqlite")
    cells = s.db.execute("UPDATE cells SET status='pending', final_outcome=NULL WHERE final_outcome='job_error'").rowcount
    tasks = s.db.execute("UPDATE tasks SET status='pending', error=NULL WHERE status='error'").rowcount
    s.event("retry_errors", cells=cells, tasks=tasks)
    print(f"{run_dir}: {cells} cells and {tasks} tasks back to pending")


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
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--manifest", type=Path)
    src.add_argument("--folder", type=Path, help="a runs folder (manifest.json + <task>/runN/session.v2.jsonl); P1/P2 = first two passing runs")
    p.add_argument("--config", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("run", help="run the pipeline (resumable)")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--tasks", nargs="*")
    p.add_argument("--concurrency", type=int)
    p = sub.add_parser("report", help="write report.md and report.json")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--notes", type=Path, help="folder of written analyses to include: _top.md (after the summary) and "
                   "<task_id with / as __>.md (in that task's section)")
    p = sub.add_parser("job", help="run one job by hand (not recorded in the state)")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--kind", required=True, choices=jobs.KINDS)
    p.add_argument("--trajectories", required=True, help="A=id,B=id for f1_propose; T=id otherwise")
    p.add_argument("--inputs", default="{}", help="JSON object, or @file.json")
    p.add_argument("--model", help="model key from the config (default: the kind's role)")
    p = sub.add_parser("add-runs", help="add trajectories to a run: the active invariants get cells on them (then: run)")
    p.add_argument("run_dir", type=Path)
    p.add_argument("--manifest", type=Path, required=True)
    p = sub.add_parser("guard", help="pause invariant_mining runs before the gateway's premium usage reaches a limit")
    p.add_argument("--max-used", type=int, required=True)
    p.add_argument("--interval", type=float, default=10)
    p.add_argument("--log", type=Path, default=Path("runs/credit-guard.log"))
    p.add_argument("--config", type=Path)
    p.add_argument("--pause-file", type=Path, help="created at the limit: other drivers start no new work while it exists")
    p.add_argument("--kill-pattern", action="append", default=[],
                   help="regex on a process's command line: such processes are also sent SIGTERM at the limit")
    p = sub.add_parser("invariants", help="write invariants.md: what F1 proposed per task (safe while it runs)")
    p.add_argument("run_dir", type=Path)
    p = sub.add_parser("status", help="progress of a run (safe while it runs)")
    p.add_argument("run_dir", type=Path)
    p = sub.add_parser("retry-errors", help="cells that ended in a job error back to pending (then: run)")
    p.add_argument("run_dir", type=Path)
    p = sub.add_parser("ping", help="one tiny request to each configured model")
    p.add_argument("--config", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "prepare":
        if a.folder:
            m = manifest_from_folder(a.folder)
            a.out.mkdir(parents=True, exist_ok=True)
            (a.out / "folder-manifest.json").write_text(json.dumps(m, indent=1))
            prepare(m, a.config, a.out)
        else:
            prepare(a.manifest, a.config, a.out)
    elif a.cmd == "run":
        cfg = config_mod.load(a.run_dir / "config.json")
        if a.concurrency:
            cfg["concurrency"] = a.concurrency
        Pipeline(a.run_dir, cfg).run(a.tasks)
        rep = report.write(a.run_dir)
        print(json.dumps(rep["totals"], indent=1))
    elif a.cmd == "report":
        rep = report.write(a.run_dir, a.notes)
        print(json.dumps(rep["totals"], indent=1))
    elif a.cmd == "job":
        trajs = dict(kv.split("=", 1) for kv in a.trajectories.split(","))
        inputs = json.loads(Path(a.inputs[1:]).read_text() if a.inputs.startswith("@") else a.inputs)
        run_one_job(a.run_dir, a.kind, trajs, inputs, a.model)
    elif a.cmd == "add-runs":
        add_runs(a.run_dir, a.manifest)
    elif a.cmd == "guard":
        from .guard import guard
        a.log.parent.mkdir(parents=True, exist_ok=True)
        guard(config_mod.load(a.config), a.max_used, a.interval, a.log, a.pause_file, a.kill_pattern)
    elif a.cmd == "invariants":
        out = a.run_dir / "invariants.md"
        out.write_text(report.proposals(a.run_dir))
        print(out)
    elif a.cmd == "status":
        status(a.run_dir)
    elif a.cmd == "retry-errors":
        retry_errors(a.run_dir)
    elif a.cmd == "ping":
        ping(a.config)
