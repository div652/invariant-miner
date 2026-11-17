"""report.json + report.md from a run's state (DESIGN.md section 7). Points are computed here, never stored."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from .rules import FINAL_EFFECT
from .store import Store
from .trajectory import Trajectory


def build(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    s = Store(run_dir / "state.sqlite")
    trajs_meta = {r["id"]: r for r in s.q("SELECT * FROM trajectories")}
    _cache: dict[str, Trajectory] = {}

    def order(tid: str, loc: str):
        if tid not in _cache:
            _cache[tid] = Trajectory.load(run_dir / trajs_meta[tid]["json_path"])
        try:
            return _cache[tid].position(loc)
        except Exception:
            return (10**9, 0)

    events = [dict(e) | {"detail": json.loads(e["detail_json"])} for e in s.q("SELECT * FROM events ORDER BY time")]
    ev_by_inv = defaultdict(list)
    for e in events:
        if e["invariant_id"]:
            ev_by_inv[e["invariant_id"]].append(e)
    out = {"run": str(run_dir), "tasks": []}
    totals = Counter()
    for task in s.q("SELECT * FROM tasks ORDER BY seq"):
        invs = s.q("SELECT * FROM invariants WHERE task_id=? ORDER BY created_at", task["task_id"])
        cells = s.q("SELECT c.* FROM cells c JOIN invariants i ON i.id=c.invariant_id WHERE i.task_id=?", task["task_id"])
        by_inv = defaultdict(list)
        for c in cells:
            by_inv[c["invariant_id"]].append(c)
        # first violation per failing run, among active invariants
        first = {}
        for tid in {c["trajectory_id"] for c in cells if c["label"] == "fail"}:
            viol = [(order(tid, c["f2_location"] or "start"), c["invariant_id"]) for c in cells
                    if c["trajectory_id"] == tid and c["final_outcome"] == "not_followed" and c["status"] == "done"
                    and next(i for i in invs if i["id"] == c["invariant_id"])["status"] == "active"]
            if viol:
                first[tid] = min(viol)[1]
        tinvs = []
        for inv in invs:
            cs = by_inv[inv["id"]]
            pts = Counter(FINAL_EFFECT.get((c["label"], c["final_outcome"])) for c in cs if c["status"] == "done")
            entry = {"id": inv["id"], "status": inv["status"], "origin": inv["origin"], "parent": inv["parent_id"],
                     "observation": json.loads(inv["observation_json"]), "action": inv["action"], "purpose": inv["purpose"],
                     "follows": json.loads(inv["follows_json"]), "evidence": json.loads(inv["evidence_json"]),
                     "support": pts["support"], "importance": pts["importance"],
                     "first_violations": sorted(t for t, i in first.items() if i == inv["id"]),
                     "cells": {c["trajectory_id"]: c["final_outcome"] or c["status"] for c in cs},
                     "events": [{"kind": e["kind"], "trajectory": e["trajectory_id"], **e["detail"]} for e in ev_by_inv[inv["id"]]]}
            tinvs.append(entry)
            totals[f"invariants_{inv['status']}"] += 1
        task_events = Counter(e["kind"] for e in events if e["task_id"] == task["task_id"])
        totals.update(task_events)
        pinning_by_traj = Counter(e["trajectory_id"] for e in events if e["task_id"] == task["task_id"] and e["kind"] == "pinning_wrong")
        out["tasks"].append({"task_id": task["task_id"], "p1": task["p1"], "p2": task["p2"], "status": task["status"],
                             "error": task["error"], "roles": json.loads(task["roles_json"] or "[]"),
                             "trajectories": {t: trajs_meta[t]["label"] for t in trajs_meta if trajs_meta[t]["task_id"] == task["task_id"]},
                             "events": dict(task_events), "pinning_wrong_by_trajectory": dict(pinning_by_traj),
                             "invariants": tinvs})
    jobs = s.q("SELECT kind, role, model, status, COUNT(*) n, SUM(model_steps) steps, SUM(tokens_in) tin, SUM(tokens_out) tout, "
               "SUM(ended-started) secs FROM jobs GROUP BY kind, role, model, status")
    out["cost"] = [dict(j) for j in jobs]
    out["totals"] = dict(totals)
    return out


def _facts(obs: list) -> str:
    return "∅" if not obs else "; ".join(f"{f['fact']} [{f['source']}]" for f in obs)


def markdown(rep: dict) -> str:
    lines = [f"# Invariant mining report", "", f"Run: `{rep['run']}`", ""]
    t = rep["totals"]
    lines += ["## Totals", "", "| | count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(t.items())] + [""]
    for task in rep["tasks"]:
        labels = Counter(task["trajectories"].values())
        lines += [f"## Task `{task['task_id']}`", "",
                  f"P1 `{task['p1']}`, P2 `{task['p2']}`; trajectories: {labels.get('pass', 0)} passing, {labels.get('fail', 0)} failing; "
                  f"status {task['status']}" + (f" ({task['error']})" if task["error"] else ""), ""]
        active = [i for i in task["invariants"] if i["status"] == "active"]
        lines += ["### Active invariants", "", "| id | observation | action | support | importance | first violation in |", "|---|---|---|---|---|---|"]
        for i in sorted(active, key=lambda x: (-x["importance"], -x["support"])):
            lines.append(f"| {i['id']} | {_facts(i['observation'])} | {i['action']} | {i['support']} | {i['importance']} | "
                         f"{', '.join(i['first_violations'])} |")
        lines.append("")
        gone = [i for i in task["invariants"] if i["status"] != "active"]
        if gone:
            lines += ["### Removed and retired invariants", "", "| id | status | action | what happened |", "|---|---|---|---|"]
            for i in gone:
                what = "; ".join(f"{e['kind']} ({e.get('trajectory')})" + (f": -> {e['new_invariant']}" if e.get("new_invariant") else "")
                                 for e in i["events"] if e["kind"] in ("removed", "reworded", "reword_failed"))
                lines.append(f"| {i['id']} | {i['status']} | {i['action']} | {what} |")
            lines.append("")
        lines += ["### Events", "", "| kind | count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(task["events"].items())] + [""]
        if task["roles"]:
            lines += ["### Role terms (F1)", ""] + [f"- **{r['term']}**: {r['meaning']}" for r in task["roles"]] + [""]
    lines += ["## Cost", "", "| kind | role | model | status | jobs | model steps | tokens in | tokens out | seconds |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in rep["cost"]:
        lines.append(f"| {c['kind']} | {c['role']} | {c['model']} | {c['status']} | {c['n']} | {c['steps']} | {c['tin']:,} | "
                     f"{c['tout']:,} | {c['secs']:.0f} |")
    return "\n".join(lines) + "\n"


def write(run_dir: Path) -> dict:
    rep = build(run_dir)
    Path(run_dir, "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    Path(run_dir, "report.md").write_text(markdown(rep))
    return rep
