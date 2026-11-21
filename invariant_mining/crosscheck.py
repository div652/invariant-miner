"""Invariant cross-checking (user, 2026-11-20): a finished mining run's invariants that are active with IMPORTANCE > 0
(always: "in future when you do cross check it has to be importance>0 and active ones"; support plays no part), each
checked on every passing trajectory of every OTHER task of that run, with the usual cell checks: Luna F2 (seen?),
Luna F3 (followed?), on "not followed" the Opus F2/F3 re-check, then the Opus too-narrow check. Nothing is removed or
reworded: a run is only observed. A cell whose final outcome is "not followed" (Opus agreed, purpose not achieved another
way) is a VIOLATION: a passing run of another task saw the observation and did not take the action.

    python -m invariant_mining cross-check SOURCE_RUN --out runs/xc-NAME [--min-importance 1]   # prepare
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


def prepare_cross_check(source: Path, out: Path, min_importance: int = 1) -> dict:
    if min_importance < 1:
        raise SystemExit("cross-checking takes the active invariants with importance > 0 (--min-importance >= 1)")
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
            if inv["status"] != "active" or inv["importance"] < min_importance:
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
    s.set_meta("min_importance", min_importance)
    summary = {"invariants": n_inv, "cells": n_cells, "tasks": len(rep["tasks"]),
               "passing_trajectories": sum(len(v) for v in passing.values())}
    s.set_meta("prepared", json.dumps(summary))
    print(f"cross-check prepared {out}: {n_inv} invariants (active, importance >= {min_importance}) x the passing runs of the other "
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
    # cross-consistent invariants (user's name, 2026-11-20): checked (active, importance > 0) and violated on no other task
    consistent = [i["id"] for i in invs if not i["violations"] and not i["outcomes"].get("pending") and not i["outcomes"].get("running")]
    return {"run": str(run_dir), "source_run": s.get_meta("source_run"), "prepared": json.loads(s.get_meta("prepared", "{}")),
            "totals": dict(totals), "invariants": invs, "cross_consistent": consistent}


def markdown(rep: dict) -> str:
    cell = report.cell
    facts = report._facts
    invs = rep["invariants"]
    violated = sorted([i for i in invs if i["violations"]], key=lambda i: (-len(i["violated_tasks"]), -len(i["violations"]), i["id"]))
    p = rep["prepared"]
    lines = ["# Invariant cross-check", "",
             f"Run: `{rep['run']}`; source mining run: `{rep['source_run']}`. The source run's invariants that are active "
             f"with importance > 0 ({p.get('invariants')}), each checked on every passing trajectory of every other task "
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
    cons = [i for i in invs if i["id"] in set(rep.get("cross_consistent", []))]
    weak = [i for i in cons if i["seen"] >= 5 and i["outcomes"].get("followed", 0) / i["seen"] < 0.5]
    lines += ["", f"## Cross-consistent invariants ({len(cons)} of {len(invs)})", "",
              "Active, importance > 0, and violated on no other task. **Consistent means never violated, not usually "
              "followed**: only a confirmed 'not followed' (Luna, then the Opus re-check, and the too-narrow check finding "
              "the purpose not achieved another way) breaks consistency. A sighting can also end as *same purpose, other "
              "action* (the run achieved the purpose differently), *action = pinned item* (the observation's only evidence "
              "is the action itself) or *only before* (the action came before the observation); none of these is a "
              "violation, and none is a 'followed' either. 'Seen elsewhere' 0 means the observation never came up on "
              "another task, so it could not be tested there.", ""]
    if weak:
        lines += ["**Weakly supported** (seen on at least 5 other-task runs, followed as worded in fewer than half): "
                  + "; ".join(f"{i['local_id']} (`{i['task']}`): followed {i['outcomes'].get('followed', 0)} of {i['seen']} sightings, "
                              f"same purpose another way {i['outcomes'].get('purpose_otherwise', 0)}, action = pinned item "
                              f"{i['outcomes'].get('at_pinned', 0)}, only before {i['outcomes'].get('only_before', 0)}" for i in weak)
                  + ". Such an invariant is consistent only in the sense above.", ""]
    lines += ["| invariant (task) | observation | action | own S, I | seen elsewhere | followed | same purpose, other action | action = pinned item | only before |",
              "|---|---|---|---|---|---|---|---|---|"]
    for i in sorted(cons, key=lambda i: (-i["seen"], i["id"])):
        src, o = i["source"], i["outcomes"]
        lines.append(f"| {i['local_id']} (`{i['task']}`) | {cell(facts(i['observation']))} | {cell(i['action'])} | "
                     f"S {src.get('support')}/{src.get('n_pass')}, I {src.get('importance')}/{src.get('n_fail')} | "
                     f"{i['seen']}/{i['checked']} | {o.get('followed', 0)} | {o.get('purpose_otherwise', 0)} | "
                     f"{o.get('at_pinned', 0)} | {o.get('only_before', 0)} |")
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
