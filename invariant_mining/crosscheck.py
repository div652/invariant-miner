"""Invariant cross-checking (user, 2026-11-20): a finished mining run's invariants that are active with support > 0,
each checked on every passing trajectory of every OTHER task of that run, with the usual cell checks: Luna F2 (seen?),
Luna F3 (followed?), on "not followed" the Opus F2/F3 re-check, then the Opus too-narrow check. Nothing is removed or
reworded: a run is only observed. A cell whose final outcome is "not followed" (Opus agreed, purpose not achieved another
way) is a VIOLATION: a passing run of another task saw the observation and did not take the action.

    python -m invariant_mining cross-check SOURCE_RUN --out runs/xc-NAME [--min-support 1]   # prepare
    python -m invariant_mining run runs/xc-NAME                                              # the checks (resumable)
    python -m invariant_mining cross-report runs/xc-NAME                                     # cross_check.md / .json

The new run shares the source run's normalized trajectories (a symlink) and config (same models and roles); the
invariants keep their ids. Store meta: mode = cross_check, source_run, source_points (the invariants' S and I in the
source run).
"""

import json
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path

from . import report
from .store import Store

SEEN = ("followed", "not_followed", "purpose_otherwise", "only_before", "at_pinned", "pinning_wrong")


def prepare_cross_check(source: Path, out: Path, min_support: int = 1) -> dict:
    source, out = Path(source).resolve(), Path(out)
    if (out / "state.sqlite").exists():
        raise SystemExit(f"{out} already has a run")
    rep = report.build(source)
    src = Store(source / "state.sqlite")
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(source / "config.json", out / "config.json")
    if not (out / "trajectories").exists():
        (out / "trajectories").symlink_to(source / "trajectories", target_is_directory=True)
    s = Store(out / "state.sqlite")
    s.set_meta("mode", "cross_check")
    s.set_meta("source_run", str(source))
    for t in src.q("SELECT * FROM trajectories"):
        s.x("INSERT INTO trajectories VALUES (?,?,?,?,?,?,?)", *[t[k] for k in t.keys()])
    for t in src.q("SELECT * FROM tasks"):
        s.x("INSERT INTO tasks (task_id, seq, p1, p2, status, roles_json) VALUES (?,?,?,?,?,?)", t["task_id"], t["seq"],
            t["p1"], t["p2"], "done", t["roles_json"])
    passing = defaultdict(list)
    for t in src.q("SELECT id, task_id FROM trajectories WHERE label='pass' ORDER BY id"):
        passing[t["task_id"]].append(t["id"])
    points, n_inv, n_cells = {}, 0, 0
    for task in rep["tasks"]:
        tr = task["trajectories"]
        others = [x for x in tr if x not in (task["p1"], task["p2"])]
        n_pass, n_fail = sum(tr[x] == "pass" for x in others), sum(tr[x] == "fail" for x in others)
        for inv in task["invariants"]:
            if inv["status"] != "active" or inv["support"] < min_support:
                continue
            row = src.one("SELECT * FROM invariants WHERE id=?", inv["id"])
            s.x(f"INSERT INTO invariants VALUES ({','.join('?' * len(row.keys()))})", *[row[k] for k in row.keys()])
            points[inv["id"]] = {"support": inv["support"], "importance": inv["importance"], "n_pass": n_pass, "n_fail": n_fail}
            phi = not inv["observation"]
            for other, runs in passing.items():
                if other == task["task_id"]:
                    continue
                for tid in runs:
                    s.x("INSERT INTO cells (invariant_id, trajectory_id, label, stage, status, f2_seen, f2_location, job_ids, updated) "
                        "VALUES (?,?,?,?,?,?,?,?,?)", inv["id"], tid, "pass", "f3" if phi else "f2", "pending",
                        1 if phi else None, "start" if phi else None, "[]", time.time())
                    n_cells += 1
            n_inv += 1
    s.set_meta("source_points", json.dumps(points))
    s.set_meta("min_support", min_support)
    summary = {"invariants": n_inv, "cells": n_cells, "tasks": len(rep["tasks"]),
               "passing_trajectories": sum(len(v) for v in passing.values())}
    s.set_meta("prepared", json.dumps(summary))
    print(f"cross-check prepared {out}: {n_inv} invariants (active, support >= {min_support}) x the passing runs of the other "
          f"tasks = {n_cells} cells ({summary['passing_trajectories']} passing trajectories, {summary['tasks']} tasks)")
    return summary


def _short(tid: str) -> str:
    return tid.split("#", 1)[1] if "#" in tid else tid


def build(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    s = Store(run_dir / "state.sqlite")
    points = json.loads(s.get_meta("source_points", "{}"))
    traj_task = {t["id"]: t["task_id"] for t in s.q("SELECT id, task_id FROM trajectories")}
    invs = []
    for inv in s.q("SELECT * FROM invariants ORDER BY task_id, created_at"):
        cells = s.q("SELECT * FROM cells WHERE invariant_id=?", inv["id"])
        out = Counter(c["final_outcome"] if c["status"] == "done" else c["status"] for c in cells)
        violations = [{"trajectory": c["trajectory_id"], "task": traj_task[c["trajectory_id"]],
                       "observation_at": c["recheck_f2_location"] or c["f2_location"]}
                      for c in cells if c["status"] == "done" and c["final_outcome"] == "not_followed"]
        invs.append({"id": inv["id"], "task": inv["task_id"], "local_id": inv["local_id"],
                     "observation": json.loads(inv["observation_json"]), "action": inv["action"], "purpose": inv["purpose"],
                     "source": points.get(inv["id"], {}), "checked": len(cells), "outcomes": dict(out),
                     "seen": sum(out[k] for k in SEEN), "violations": violations,
                     "violated_tasks": sorted({v["task"] for v in violations})})
    totals = Counter()
    for i in invs:
        totals.update(i["outcomes"])
    return {"run": str(run_dir), "source_run": s.get_meta("source_run"), "prepared": json.loads(s.get_meta("prepared", "{}")),
            "totals": dict(totals), "invariants": invs}


def markdown(rep: dict) -> str:
    cell = report.cell
    facts = report._facts
    invs = rep["invariants"]
    violated = sorted([i for i in invs if i["violations"]], key=lambda i: (-len(i["violated_tasks"]), -len(i["violations"]), i["id"]))
    p = rep["prepared"]
    lines = ["# Invariant cross-check", "",
             f"Run: `{rep['run']}`; source mining run: `{rep['source_run']}`. The source run's invariants that are active "
             f"with support > 0 ({p.get('invariants')}), each checked on every passing trajectory of every other task "
             f"({p.get('cells')} checks over {p.get('passing_trajectories')} passing trajectories of {p.get('tasks')} tasks): "
             "Luna F2 and F3, on 'not followed' the Opus re-check, then the Opus too-narrow check. Nothing was removed or "
             "reworded.", "",
             "**Violation** = a passing run of another task saw the observation and did not take the action (Opus agreed, "
             "and the purpose was not achieved another way). Seen = the observation was found (any outcome but not seen "
             "or a job error). S, I = the invariant's points in its own task (source run).", "",
             "Totals: " + ", ".join(f"{report.OUTCOME.get(k, k)} {v}" for k, v in sorted(rep["totals"].items(), key=lambda kv: -kv[1])), "",
             f"## Violated on other tasks ({len(violated)} of {len(invs)} invariants)", ""]
    if violated:
        lines += ["| invariant (task) | observation | action | own S, I | seen on other tasks | violated | violated in |",
                  "|---|---|---|---|---|---|---|"]
        for i in violated:
            src = i["source"]
            where = "; ".join(f"`{v['task']}` {_short(v['trajectory'])} (obs. {v['observation_at']})" for v in i["violations"])
            lines.append(f"| {i['local_id']} (`{i['task']}`) | {cell(facts(i['observation']))} | {cell(i['action'])} | "
                         f"S {src.get('support')}/{src.get('n_pass')}, I {src.get('importance')}/{src.get('n_fail')} | "
                         f"{i['seen']}/{i['checked']} | {len(i['violations'])}/{i['seen']} runs, {len(i['violated_tasks'])} tasks | {cell(where)} |")
    else:
        lines.append("None.")
    lines += ["", "## All invariants", "",
              "| invariant (task) | action | own S, I | seen | followed | violated | same purpose, other action | only before | action = pinned item | pinning wrong | job error |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in sorted(invs, key=lambda i: (-i["seen"], i["id"])):
        o, src = i["outcomes"], i["source"]
        lines.append(f"| {i['local_id']} (`{i['task']}`) | {cell(i['action'])} | S {src.get('support')}/{src.get('n_pass')}, "
                     f"I {src.get('importance')}/{src.get('n_fail')} | {i['seen']}/{i['checked']} | {o.get('followed', 0)} | "
                     f"{o.get('not_followed', 0)} | {o.get('purpose_otherwise', 0)} | {o.get('only_before', 0)} | "
                     f"{o.get('at_pinned', 0)} | {o.get('pinning_wrong', 0)} | {o.get('job_error', 0)} |")
    return "\n".join(lines) + "\n"


def write(run_dir: Path) -> dict:
    rep = build(run_dir)
    Path(run_dir, "cross_check.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    Path(run_dir, "cross_check.md").write_text(markdown(rep))
    return rep
