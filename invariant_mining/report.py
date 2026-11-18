"""report.json + report.md from a run's state (DESIGN.md section 7). Points are computed here, never stored.

Per task: every invariant F1 proposed (final status, points, outcome on each run), the rewordings, the removed invariants
with the reason, the rewordings that failed twice, the events and F1's role terms. Ends with the cost.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .rules import FINAL_EFFECT
from .store import Store
from .trajectory import Trajectory

OUTCOME = {"followed": "followed", "not_followed": "not followed", "only_before": "only before", "not_seen": "not seen",
           "pinning_wrong": "pinning wrong", "purpose_otherwise": "same purpose, other action", "job_error": "job error"}


def natural(tid: str):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", tid)]


def short(tid: str) -> str:
    return tid.split("#", 1)[1] if "#" in tid else tid


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
        status = {i["id"]: i["status"] for i in invs}
        cells = s.q("SELECT c.* FROM cells c JOIN invariants i ON i.id=c.invariant_id WHERE i.task_id=?", task["task_id"])
        by_inv = defaultdict(list)
        for c in cells:
            by_inv[c["invariant_id"]].append(c)
        # first violation per failing run, among active invariants
        first = {}
        for tid in {c["trajectory_id"] for c in cells if c["label"] == "fail"}:
            viol = [(order(tid, c["f2_location"] or "start"), c["invariant_id"]) for c in cells
                    if c["trajectory_id"] == tid and c["final_outcome"] == "not_followed" and c["status"] == "done"
                    and status[c["invariant_id"]] == "active"]
            if viol:
                first[tid] = min(viol)[1]
        tinvs = []
        for inv in invs:
            cs = by_inv[inv["id"]]
            pts = Counter(FINAL_EFFECT.get((c["label"], c["final_outcome"])) for c in cs if c["status"] == "done")
            evs = ev_by_inv[inv["id"]]
            entry = {"id": inv["id"], "local_id": inv["local_id"], "status": inv["status"], "origin": inv["origin"],
                     "parent": inv["parent_id"], "observation": json.loads(inv["observation_json"]), "action": inv["action"],
                     "purpose": inv["purpose"], "follows": json.loads(inv["follows_json"]),
                     "evidence": json.loads(inv["evidence_json"]),
                     "support": pts["support"], "importance": pts["importance"],
                     "first_violations": sorted(t for t, i in first.items() if i == inv["id"]),
                     "cells": {c["trajectory_id"]: c["final_outcome"] or c["status"] for c in cs},
                     "cell_details": {c["trajectory_id"]: {k: c[k] for k in (
                         "label", "f2_seen", "f2_location", "f3_outcome", "f3_action_location", "recheck_f2_seen",
                         "recheck_f2_location", "recheck_f3_outcome", "too_narrow", "too_narrow_location", "final_outcome",
                         "status")} for c in cs},
                     "events": [{"kind": e["kind"], "trajectory": e["trajectory_id"], **e["detail"]} for e in evs]}
            for e in evs:
                if e["kind"] == "reworded":
                    entry["replaced_by"] = e["detail"]["new_invariant"]
                if e["kind"] == "removed":
                    entry["removed_by"] = {"reason": "passing run broke it", "trajectory": e["trajectory_id"],
                                           "cell": entry["cell_details"].get(e["trajectory_id"])}
                if e["kind"] == "reword_failed" and e["detail"].get("effect") == "invariant removed":
                    entry["removed_by"] = {"reason": "rewording failed validation twice", "trajectory": e["trajectory_id"],
                                           "cell": entry["cell_details"].get(e["trajectory_id"])}
            tinvs.append(entry)
            totals[f"invariants_{inv['status']}"] += 1
        for entry in tinvs:  # how each rewording came about (from its parent's events)
            if entry["origin"] == "reword":
                parent = next(x for x in tinvs if x["id"] == entry["parent"])
                ev = next((e for e in parent["events"] if e["kind"] == "reworded" and e.get("new_invariant") == entry["id"]), {})
                entry["reworded_from"] = {"parent": parent["id"], "old_action": parent["action"], "trajectory": ev.get("trajectory"),
                                          "trigger": ev.get("trigger"), "attempt": ev.get("attempt")}
        task_events = Counter(e["kind"] for e in events if e["task_id"] == task["task_id"])
        totals.update(task_events)
        pinning_by_traj = Counter(e["trajectory_id"] for e in events if e["task_id"] == task["task_id"] and e["kind"] == "pinning_wrong")
        out["tasks"].append({"task_id": task["task_id"], "p1": task["p1"], "p2": task["p2"], "status": task["status"],
                             "error": task["error"], "roles": json.loads(task["roles_json"] or "[]"),
                             "trajectories": {t: trajs_meta[t]["label"] for t in sorted(trajs_meta, key=natural) if trajs_meta[t]["task_id"] == task["task_id"]},
                             "events": dict(task_events), "pinning_wrong_by_trajectory": dict(pinning_by_traj),
                             "invariants": tinvs})
    jobs = s.q("SELECT kind, role, model, status, COUNT(*) n, SUM(model_steps) steps, SUM(tokens_in) tin, SUM(tokens_out) tout, "
               "SUM(ended-started) secs FROM jobs GROUP BY kind, role, model, status")
    out["cost"] = [dict(j) for j in jobs]
    out["totals"] = dict(totals)
    return out


# --- markdown -----------------------------------------------------------------------------------------------------------
def cell(text) -> str:
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ")


def _facts(obs: list) -> str:
    return "∅ (always)" if not obs else "; ".join(f"{f['fact']} [{f['source']}]" for f in obs)


def _outcome(inv: dict, tid: str) -> str:
    o = inv["cells"].get(tid)
    if o is None:
        return ""
    text = OUTCOME.get(o, o)
    return text + (" ★" if tid in inv["first_violations"] else "")


def _status(inv: dict) -> str:
    if inv["status"] == "retired":
        return f"retired → {str(inv.get('replaced_by', '?')).split('.', 1)[-1]}"
    if inv["status"] == "removed":
        rb = inv.get("removed_by") or {}
        return f"removed ({short(rb.get('trajectory') or '?')})"
    if any(e["kind"] == "reword_failed" for e in inv["events"]):
        return "active (rewording failed twice)"
    return "active"


def _why_removed(inv: dict) -> str:
    rb = inv.get("removed_by") or {}
    c = rb.get("cell") or {}
    run = short(rb.get("trajectory") or "?")
    if rb.get("reason") == "rewording failed validation twice":
        return f"{run} (pass): the purpose was achieved by another action, but both rewordings failed validation on P1/P2/{run}"
    parts = [f"{run} ({c.get('label', '?')}): observation seen at {c.get('f2_location')}",
             f"Luna: {OUTCOME.get(c.get('f3_outcome'), c.get('f3_outcome'))}"]
    if c.get("recheck_f3_outcome") or c.get("recheck_f2_seen") is not None:
        parts.append(f"Opus re-check: seen at {c.get('recheck_f2_location')}, {OUTCOME.get(c.get('recheck_f3_outcome'), c.get('recheck_f3_outcome'))}")
    if c.get("too_narrow") is not None:
        parts.append("same purpose by another action: " + ("yes" if c.get("too_narrow") else "no"))
    return "; ".join(parts)


def markdown(rep: dict) -> str:
    lines = ["# Invariant mining report", "", f"Run: `{rep['run']}`", "",
             "Points: **S** = support (passing runs other than P1/P2 where the observation was seen and the action followed), "
             "**I** = importance (failing runs where the observation was seen and the action did not follow). "
             "★ = the first invariant this failing run broke. Outcomes per run are the final verdicts after the re-check "
             "and the too-narrow check (DESIGN.md sections 4-5).", ""]
    lines += ["## Summary", "", "| # | task | P1, P2 | other runs | proposed | rewordings | active | removed | retired |",
              "|---|---|---|---|---|---|---|---|---|"]
    for n, task in enumerate(rep["tasks"], 1):
        invs = task["invariants"]
        st = Counter(i["status"] for i in invs)
        others = [t for t in task["trajectories"] if t not in (task["p1"], task["p2"])]
        lab = Counter(task["trajectories"][t] for t in others)
        lines.append(f"| {n} | `{task['task_id']}` | {short(task['p1'])}, {short(task['p2'])} | {lab.get('pass', 0)} pass, "
                     f"{lab.get('fail', 0)} fail | {sum(1 for i in invs if i['origin'] == 'propose')} | "
                     f"{sum(1 for i in invs if i['origin'] == 'reword')} | {st.get('active', 0)} | {st.get('removed', 0)} | {st.get('retired', 0)} |")
    lines += ["", "Totals: " + ", ".join(f"{k} {v}" for k, v in sorted(rep["totals"].items())), ""]
    for n, task in enumerate(rep["tasks"], 1):
        invs = task["invariants"]
        others = [t for t in task["trajectories"] if t not in (task["p1"], task["p2"])]
        runs_desc = ", ".join(f"{short(t)} ({task['trajectories'][t]})" for t in others)
        head = [f"## Task {n}: `{task['task_id']}`", "",
                f"P1 `{short(task['p1'])}`, P2 `{short(task['p2'])}`; other runs: {runs_desc or 'none'}. Status {task['status']}"
                + (f" ({task['error']})" if task["error"] else "") + ".", ""]
        lines += head
        run_cols = " | ".join(f"{short(t)} ({task['trajectories'][t]})" for t in others)
        sep = "|---" * (6 + len(others)) + "|"
        proposed = [i for i in invs if i["origin"] == "propose"]
        lines += [f"### Proposed by F1 ({len(proposed)})", "", f"| id | observation | action | final status | S | I | {run_cols} |", sep]
        for i in proposed:
            lines.append(f"| {i['local_id']} | {cell(_facts(i['observation']))} | {cell(i['action'])} | {cell(_status(i))} | "
                         f"{i['support']} | {i['importance']} | " + " | ".join(cell(_outcome(i, t)) for t in others) + " |")
        lines.append("")
        reworded = [i for i in invs if i["origin"] == "reword"]
        if reworded:
            sep2 = "|---" * (8 + len(others)) + "|"
            lines += [f"### Added by rewording ({len(reworded)})", "",
                      "The observation is the original's; the action was reworded at the purpose level after a run achieved "
                      "the purpose with another action, and validated on P1/P2 (and the run, if it passed).", "",
                      f"| id | replaces | old action | new action | from run | attempt | final status | S/I | {run_cols} |", sep2]
            for i in reworded:
                rf = i.get("reworded_from") or {}
                lines.append(f"| {i['id'].split('.', 1)[1]} | {cell(rf.get('parent', '').split('.', 1)[-1])} | {cell(rf.get('old_action'))} | "
                             f"{cell(i['action'])} | {cell(short(rf.get('trajectory') or ''))} ({cell(rf.get('trigger'))}) | {rf.get('attempt', '')} | "
                             f"{cell(_status(i))} | {i['support']}/{i['importance']} | " + " | ".join(cell(_outcome(i, t)) for t in others) + " |")
            lines.append("")
        removed = [i for i in invs if i["status"] == "removed"]
        lines += [f"### Removed ({len(removed)})", ""]
        if removed:
            lines += ["| id | observation | action | why |", "|---|---|---|---|"]
            for i in removed:
                lines.append(f"| {i['id'].split('.', 1)[1]} | {cell(_facts(i['observation']))} | {cell(i['action'])} | {cell(_why_removed(i))} |")
        else:
            lines.append("None" + (" (no passing run besides P1/P2)." if not any(task["trajectories"][t] == "pass" for t in others) else "."))
        lines.append("")
        fails = [t for t in others if task["trajectories"][t] == "fail"]
        if fails:
            active = [i for i in invs if i["status"] == "active"]
            lines += [f"### Failing runs ({len(fails)})", "",
                      "Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, "
                      "same purpose by another action, only before. A run that breaks nothing failed for a reason these "
                      "invariants don't capture (a missing invariant, a content or reasoning error, or the grader).", "",
                      "| run | broken | not seen | same purpose, other action | only before | first broken | |", "|---|---|---|---|---|---|---|"]
            for t in fails:
                outs = Counter(i["cells"].get(t) for i in active)
                first = [i["id"].split(".", 1)[1] for i in active if t in i["first_violations"]]
                lines.append(f"| {short(t)} | {outs.get('not_followed', 0)} | {outs.get('not_seen', 0)} | {outs.get('purpose_otherwise', 0)} | "
                             f"{outs.get('only_before', 0)} | {', '.join(first)} | {'**breaks nothing**' if not outs.get('not_followed') else ''} |")
            lines.append("")
        kept = [i for i in invs if i["status"] == "active" and any(e["kind"] == "reword_failed" for e in i["events"])]
        if kept:
            lines += ["### Kept after two failed rewordings (failing-run trigger)", ""]
            for i in kept:
                runs = sorted({short(e["trajectory"]) for e in i["events"] if e["kind"] == "reword_failed"})
                lines.append(f"- {i['id'].split('.', 1)[1]}: {i['action']} (triggered by {', '.join(runs)}; that run counts 0 for importance)")
            lines.append("")
        lines += ["### Events", "", ", ".join(f"{k} {v}" for k, v in sorted(task["events"].items())) or "none", ""]
        if task["roles"]:
            lines += ["### Role terms (F1)", ""] + [f"- **{r['term']}**: {r['meaning']}" for r in task["roles"]] + [""]
    lines += ["## Cost", "", "| kind | role | model | status | jobs | model requests | tokens in | tokens out | seconds |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in rep["cost"]:
        lines.append(f"| {c['kind']} | {c['role']} | {c['model']} | {c['status']} | {c['n']} | {c['steps']} | {c['tin'] or 0:,} | "
                     f"{c['tout'] or 0:,} | {c['secs'] or 0:.0f} |")
    return "\n".join(lines) + "\n"


def proposals(run_dir: Path) -> str:
    """invariants.md: what F1 proposed for each task (facts with source and reason, action and purpose, role terms).
    Read-only; works while a run is in progress."""
    s = Store(Path(run_dir) / "state.sqlite")
    lines = ["# Proposed invariants", "", f"Run: `{run_dir}`. What F1 proposed from P1 and P2 of each task, before any "
             "check; their later fate (points, removal, rewording) is in report.md.", ""]
    for n, task in enumerate(s.q("SELECT * FROM tasks ORDER BY seq"), 1):
        invs = s.q("SELECT * FROM invariants WHERE task_id=? AND origin='propose' ORDER BY created_at", task["task_id"])
        lines += [f"## Task {n}: `{task['task_id']}`", "", f"P1 `{short(task['p1'])}`, P2 `{short(task['p2'])}`; "
                  f"{len(invs)} invariants" + ("" if task["status"] == "done" else f" (F1 {task['status']})") + ".", ""]
        for inv in invs:
            obs = json.loads(inv["observation_json"])
            follows = json.loads(inv["follows_json"])
            lines.append(f"**{inv['local_id']}**" + (f" (follows {', '.join(follows)})" if follows else ""))
            if obs:
                lines += [f"- observation: {f['fact']} *[{f['source']}; why: {f['reason']}]*" for f in obs]
            else:
                lines.append("- observation: ∅ (always)")
            lines += [f"- action: {inv['action']}", f"- purpose: {inv['purpose']}", ""]
        roles = json.loads(task["roles_json"] or "[]")
        if roles:
            lines += ["Role terms: " + "; ".join(f"**{r['term']}**: {r['meaning']}" for r in roles), ""]
    return "\n".join(lines) + "\n"


def write(run_dir: Path) -> dict:
    rep = build(run_dir)
    Path(run_dir, "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    Path(run_dir, "report.md").write_text(markdown(rep))
    return rep
