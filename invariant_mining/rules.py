"""The programmatic rules (DESIGN.md sections 4-6; TECHNICAL.md 4.2): which work is ready, and what a finished job does
to the state. No LLM here.

Work items (dicts): {"type": "f1", "task_id"}; {"type": "cell", "invariant_id", "trajectory_id", "stage"};
{"type": "reword", "trigger_id"}; {"type": "val", "trigger_id", "attempt", "trajectory_id", "stage"}.
Each item names the job kind and the model role it needs (job_for()).

Cell stages: f2 -> f3 -> (not followed) passing: recheck_f2 -> recheck_f3 -> too_narrow; failing: too_narrow.
"""

import json
import time

from .store import Store

FINAL_EFFECT = {  # (label, final outcome) -> point; anything else counts nothing (DESIGN.md section 5)
    ("pass", "followed"): "support",
    ("fail", "not_followed"): "importance",
}


def inv_row(store: Store, iid: str):
    return store.one("SELECT * FROM invariants WHERE id=?", iid)


def facts_of(inv) -> list[dict]:
    return json.loads(inv["observation_json"])


def is_phi(inv) -> bool:
    return not facts_of(inv)


# --- creating invariants and their cells ------------------------------------------------------------------------------
def add_invariant(store: Store, task, local_id: str, observation: list, action: dict, follows: list, evidence: dict,
                  origin: str, parent_id=None, attempt=0, job_id=None, prefix: str = "") -> str:
    iid = f"T{task['seq']}.{prefix}{local_id}"
    n = 1
    while store.one("SELECT 1 FROM invariants WHERE id=?", iid):
        n += 1
        iid = f"T{task['seq']}.{prefix}{local_id}.{n}"
    store.x("INSERT INTO invariants VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", iid, task["task_id"], local_id,
            json.dumps(observation, ensure_ascii=False), action["text"], action["purpose"], json.dumps(follows),
            json.dumps(evidence), "active", parent_id, origin, attempt, job_id, time.time())
    phi = not observation
    for t in store.q("SELECT id, label FROM trajectories WHERE task_id=? AND id NOT IN (?,?)", task["task_id"], task["p1"], task["p2"]):
        store.x("INSERT INTO cells (invariant_id, trajectory_id, label, stage, status, f2_seen, f2_location, job_ids, updated) "
                "VALUES (?,?,?,?,?,?,?,?,?)", iid, t["id"], t["label"], "f3" if phi else "f2", "pending",
                1 if phi else None, "start" if phi else None, "[]", time.time())
    return iid


def add_trajectory_cells(store: Store, traj_id: str) -> int:
    """A trajectory added to a run: one pending cell per active invariant of its task (not for its P1/P2)."""
    t = store.one("SELECT * FROM trajectories WHERE id=?", traj_id)
    task = store.one("SELECT * FROM tasks WHERE task_id=?", t["task_id"])
    if traj_id in (task["p1"], task["p2"]):
        return 0
    n = 0
    for inv in store.q("SELECT * FROM invariants WHERE task_id=? AND status='active'", t["task_id"]):
        phi = is_phi(inv)
        store.x("INSERT OR IGNORE INTO cells (invariant_id, trajectory_id, label, stage, status, f2_seen, f2_location, job_ids, updated) "
                "VALUES (?,?,?,?,?,?,?,?,?)", inv["id"], traj_id, t["label"], "f3" if phi else "f2", "pending",
                1 if phi else None, "start" if phi else None, "[]", time.time())
        n += 1
    return n


def deactivate(store: Store, iid: str, status: str) -> None:
    """Remove or retire an invariant: pending cells cancelled, waiting triggers dropped."""
    store.update("invariants", {"id": iid}, status=status)
    store.x("UPDATE cells SET status='cancelled', updated=? WHERE invariant_id=? AND status='pending'", time.time(), iid)
    store.x("UPDATE triggers SET status='dropped' WHERE invariant_id=? AND status='waiting'", iid)


# --- ready work -------------------------------------------------------------------------------------------------------
def ready_work(store: Store, limit: int) -> list[dict]:
    """Up to `limit` items that can run now; marks them running. Applies removal triggers on the way (no job needed)."""
    items: list[dict] = []
    if limit <= 0:
        return items
    for t in store.q("SELECT task_id FROM tasks WHERE status='pending' ORDER BY seq"):
        if len(items) >= limit:
            return items
        store.update("tasks", {"task_id": t["task_id"]}, status="running")
        items.append({"type": "f1", "task_id": t["task_id"]})
    # triggers: one at a time per invariant, oldest first
    for row in store.q("SELECT invariant_id, MIN(id) AS tid FROM triggers WHERE status IN ('waiting','active') GROUP BY invariant_id"):
        trig = store.one("SELECT * FROM triggers WHERE id=?", row["tid"])
        inv = inv_row(store, trig["invariant_id"])
        if inv["status"] != "active":
            store.x("UPDATE triggers SET status='dropped' WHERE invariant_id=? AND status IN ('waiting','active')", inv["id"])
            continue
        if trig["status"] == "waiting":
            if trig["kind"] == "remove":
                deactivate(store, inv["id"], "removed")
                store.update("triggers", {"id": trig["id"]}, status="done", result="removed")
                store.event("removed", inv["task_id"], inv["id"], trig["trajectory_id"],
                            reason="passing run: observation seen, action not followed (Opus re-check agreed), purpose not achieved otherwise")
                continue
            store.update("triggers", {"id": trig["id"]}, status="active", stage="reword", attempt=1)
            trig = store.one("SELECT * FROM triggers WHERE id=?", trig["id"])
        if trig["stage"] == "reword" and not trig["job_running"] and len(items) < limit:
            store.update("triggers", {"id": trig["id"]}, job_running=1)
            items.append({"type": "reword", "trigger_id": trig["id"]})
        elif trig["stage"] == "validate":
            for v in store.q("SELECT * FROM validations WHERE trigger_id=? AND attempt=? AND status='pending'", trig["id"], trig["attempt"]):
                if len(items) >= limit:
                    break
                store.update("validations", {"trigger_id": v["trigger_id"], "attempt": v["attempt"], "trajectory_id": v["trajectory_id"]}, status="running")
                items.append({"type": "val", "trigger_id": v["trigger_id"], "attempt": v["attempt"],
                              "trajectory_id": v["trajectory_id"], "stage": v["stage"]})
    if len(items) < limit:
        for c in store.q("SELECT c.invariant_id, c.trajectory_id, c.stage FROM cells c JOIN invariants i ON i.id=c.invariant_id "
                         "WHERE c.status='pending' AND i.status='active' ORDER BY i.created_at, c.trajectory_id LIMIT ?",
                         limit - len(items)):
            store.update("cells", {"invariant_id": c["invariant_id"], "trajectory_id": c["trajectory_id"]}, status="running")
            items.append({"type": "cell", "invariant_id": c["invariant_id"], "trajectory_id": c["trajectory_id"], "stage": c["stage"]})
    return items


def job_for(store: Store, item: dict) -> dict:
    """The job an item needs: kind, role (config roles key), inputs, trajectories {name: trajectory id}."""
    if item["type"] == "f1":
        task = store.one("SELECT * FROM tasks WHERE task_id=?", item["task_id"])
        return {"kind": "f1_propose", "role": "f1_propose", "inputs": {}, "trajs": {"A": task["p1"], "B": task["p2"]},
                "ref": item["task_id"]}
    if item["type"] == "cell":
        inv = inv_row(store, item["invariant_id"])
        cell = store.one("SELECT * FROM cells WHERE invariant_id=? AND trajectory_id=?", item["invariant_id"], item["trajectory_id"])
        facts = [f["fact"] for f in facts_of(inv)]
        ref = f"{inv['id']} x {cell['trajectory_id']}"
        stage = item["stage"]
        if stage in ("f2", "recheck_f2"):
            return {"kind": "f2_seen", "role": "f2_seen" if stage == "f2" else "f2_recheck", "inputs": {"facts": facts},
                    "trajs": {"T": cell["trajectory_id"]}, "ref": ref}
        if stage in ("f3", "recheck_f3"):
            loc = cell["f2_location"] if stage == "f3" else cell["recheck_f2_location"]
            return {"kind": "f3_followed", "role": "f3_followed" if stage == "f3" else "f3_recheck",
                    "inputs": {"facts": facts, "action": inv["action"], "location": loc}, "trajs": {"T": cell["trajectory_id"]}, "ref": ref}
        if stage == "too_narrow":
            loc = cell["recheck_f2_location"] if cell["label"] == "pass" else cell["f2_location"]
            return {"kind": "too_narrow", "role": "too_narrow", "inputs": {"facts": facts, "action": inv["action"],
                    "purpose": inv["purpose"], "location": loc}, "trajs": {"T": cell["trajectory_id"]}, "ref": ref}
    if item["type"] == "reword":
        trig = store.one("SELECT * FROM triggers WHERE id=?", item["trigger_id"])
        inv = inv_row(store, trig["invariant_id"])
        inputs = {"facts": facts_of(inv), "action": inv["action"], "purpose": inv["purpose"], "alt_location": trig["alt_location"]}
        if trig["previous_json"]:
            inputs["previous"] = json.loads(trig["previous_json"])
        return {"kind": "f1_reword", "role": "f1_reword", "inputs": inputs, "trajs": {"T": trig["trajectory_id"]},
                "ref": f"trigger {trig['id']} attempt {trig['attempt']} ({inv['id']})"}
    if item["type"] == "val":
        trig = store.one("SELECT * FROM triggers WHERE id=?", item["trigger_id"])
        inv = inv_row(store, trig["invariant_id"])
        v = store.one("SELECT * FROM validations WHERE trigger_id=? AND attempt=? AND trajectory_id=?", item["trigger_id"], item["attempt"], item["trajectory_id"])
        facts = [f["fact"] for f in facts_of(inv)]
        ref = f"validation trigger {trig['id']} attempt {item['attempt']} x {v['trajectory_id']}"
        if item["stage"] == "f2":
            return {"kind": "f2_seen", "role": "f2_seen", "inputs": {"facts": facts}, "trajs": {"T": v["trajectory_id"]}, "ref": ref}
        return {"kind": "f3_followed", "role": "f3_followed", "inputs": {"facts": facts, "action": trig["new_action"],
                "location": v["f2_location"]}, "trajs": {"T": v["trajectory_id"]}, "ref": ref}
    raise ValueError(f"unknown item {item}")


# --- applying results -------------------------------------------------------------------------------------------------
def apply(store: Store, item: dict, ok: bool, output: dict | None, error: str | None, job_ids: list[str], trajectories) -> None:
    """trajectories: callable id -> Trajectory (for the F1 evidence check)."""
    {"f1": _apply_f1, "cell": _apply_cell, "reword": _apply_reword, "val": _apply_val}[item["type"]](
        store, item, ok, output, error, job_ids, trajectories)


def _apply_f1(store, item, ok, output, error, job_ids, trajectories):
    from .jobs import f1_evidence_problems
    task = store.one("SELECT * FROM tasks WHERE task_id=?", item["task_id"])
    if not ok:
        store.update("tasks", {"task_id": task["task_id"]}, status="error", error=error, f1_job=json.dumps(job_ids))
        store.event("job_error", task["task_id"], detail="F1 propose failed", error=error)
        return
    trajs = {"A": trajectories(task["p1"]), "B": trajectories(task["p2"])}
    for inv in output["invariants"]:
        iid = add_invariant(store, task, inv["id"], inv["observation"], inv["action"], inv["follows"], inv["evidence"],
                            "propose", job_id=job_ids[-1])
        problems = f1_evidence_problems(inv, trajs)
        if problems:
            store.event("f1_evidence_invalid", task["task_id"], iid, problems=problems)
    store.update("tasks", {"task_id": task["task_id"]}, status="done", roles_json=json.dumps(output["roles"], ensure_ascii=False),
                 f1_job=json.dumps(job_ids))
    store.event("proposed", task["task_id"], count=len(output["invariants"]))


def _cell_done(store, key, final, **values):
    store.update("cells", key, status="done", final_outcome=final, updated=time.time(), **values)


def _apply_cell(store, item, ok, output, error, job_ids, trajectories):
    key = {"invariant_id": item["invariant_id"], "trajectory_id": item["trajectory_id"]}
    cell = store.one("SELECT * FROM cells WHERE invariant_id=? AND trajectory_id=?", *key.values())
    inv = inv_row(store, item["invariant_id"])
    ids = json.dumps(json.loads(cell["job_ids"] or "[]") + job_ids)
    store.update("cells", key, job_ids=ids)
    stage = item["stage"]
    ev = dict(task_id=inv["task_id"], invariant_id=inv["id"], trajectory_id=cell["trajectory_id"])
    if not ok:
        _cell_done(store, key, "job_error")
        store.event("job_error", **ev, stage=stage, error=error)
        return
    if inv["status"] != "active":  # removed or retired while this job ran: keep the verdict, take no further step
        fields = {}
        if stage == "f2":
            fields = dict(f2_seen=int(output["seen"]), f2_location=output["location"])
        elif stage == "f3":
            fields = dict(f3_outcome=output["outcome"], f3_action_location=output["action_location"])
        store.update("cells", key, status="cancelled", updated=time.time(), **fields)
        return
    label = cell["label"]
    if stage == "f2":
        if output["seen"]:
            store.update("cells", key, stage="f3", status="pending", f2_seen=1, f2_location=output["location"], updated=time.time())
        else:
            _cell_done(store, key, "not_seen", f2_seen=0)
    elif stage == "f3":
        out = output["outcome"]
        store.update("cells", key, f3_outcome=out, f3_action_location=output["action_location"])
        if out == "not_followed":
            if label == "pass":
                if is_phi(inv):
                    store.update("cells", key, stage="recheck_f3", status="pending", recheck_f2_seen=1, recheck_f2_location="start")
                else:
                    store.update("cells", key, stage="recheck_f2", status="pending")
            else:
                store.update("cells", key, stage="too_narrow", status="pending")
        else:
            _cell_done(store, key, out)
            if out in ("pinning_wrong", "only_before"):
                store.event(out, **ev, model="luna")
    elif stage == "recheck_f2":
        if output["seen"]:
            store.update("cells", key, stage="recheck_f3", status="pending", recheck_f2_seen=1, recheck_f2_location=output["location"])
        else:
            _cell_done(store, key, "not_seen", recheck_f2_seen=0)
            store.event("recheck_disagrees", **ev, luna="seen, not followed", opus="not seen")
    elif stage == "recheck_f3":
        out = output["outcome"]
        store.update("cells", key, recheck_f3_outcome=out, recheck_f3_action_location=output["action_location"])
        if out == "not_followed":
            store.update("cells", key, stage="too_narrow", status="pending")
        else:
            _cell_done(store, key, out)
            store.event("recheck_disagrees", **ev, luna="not_followed", opus=out)
            if out in ("pinning_wrong", "only_before"):
                store.event(out, **ev, model="opus")
    elif stage == "too_narrow":
        yes = output["purpose_achieved_otherwise"]
        if not yes:
            _cell_done(store, key, "not_followed", too_narrow=0)
            if label == "pass":
                store.x("INSERT INTO triggers (invariant_id, kind, trajectory_id, label, status, created_at) VALUES (?,?,?,?,?,?)",
                        inv["id"], "remove", cell["trajectory_id"], label, "waiting", time.time())
        else:
            _cell_done(store, key, "purpose_otherwise", too_narrow=1, too_narrow_location=output["location"])
            store.event("purpose_otherwise", **ev, label=label, location=output["location"])
            store.x("INSERT INTO triggers (invariant_id, kind, trajectory_id, label, alt_location, status, created_at) VALUES (?,?,?,?,?,?,?)",
                    inv["id"], "reword", cell["trajectory_id"], label, output["location"], "waiting", time.time())


def _validation_targets(store, trig) -> list[str]:
    inv = inv_row(store, trig["invariant_id"])
    task = store.one("SELECT * FROM tasks WHERE task_id=?", inv["task_id"])
    targets = [task["p1"], task["p2"]]
    if trig["label"] == "pass":  # DESIGN.md 4.5: the triggering run too, for a passing trigger
        targets.append(trig["trajectory_id"])
    return targets


def _apply_reword(store, item, ok, output, error, job_ids, trajectories):
    trig = store.one("SELECT * FROM triggers WHERE id=?", item["trigger_id"])
    store.update("triggers", {"id": trig["id"]}, job_running=0)
    inv = inv_row(store, trig["invariant_id"])
    if inv["status"] != "active":
        store.update("triggers", {"id": trig["id"]}, status="dropped")
        return
    if not ok:
        store.event("job_error", inv["task_id"], inv["id"], trig["trajectory_id"], stage="reword", error=error)
        return _attempt_failed(store, trig, {"action": None, "purpose": None, "failed_check": f"the rewording job failed: {error}"})
    act = output["action"]
    store.update("triggers", {"id": trig["id"]}, stage="validate", new_action=act["text"], new_purpose=act["purpose"])
    phi = is_phi(inv)
    for tid in _validation_targets(store, trig):
        prev = store.one("SELECT * FROM validations WHERE trigger_id=? AND trajectory_id=? AND f2_seen=1 ORDER BY attempt DESC",
                         trig["id"], tid)  # the observation is unchanged: reuse an earlier attempt's F2 verdict
        f2_seen, f2_loc = (1, "start") if phi else ((1, prev["f2_location"]) if prev else (None, None))
        store.x("INSERT INTO validations VALUES (?,?,?,?,?,?,?,?,?,?,?)", trig["id"], trig["attempt"], tid, None,
                "f3" if f2_seen else "f2", "pending", f2_seen, f2_loc, None, None, None)


def _apply_val(store, item, ok, output, error, job_ids, trajectories):
    key = {"trigger_id": item["trigger_id"], "attempt": item["attempt"], "trajectory_id": item["trajectory_id"]}
    trig = store.one("SELECT * FROM triggers WHERE id=?", item["trigger_id"])
    if trig["status"] != "active" or trig["attempt"] != item["attempt"]:
        store.update("validations", key, status="cancelled")
        return
    if not ok:
        store.update("validations", key, status="done", ok=0)
        failed = f"validation job on {item['trajectory_id']} failed: {error}"
    elif item["stage"] == "f2":
        if output["seen"]:
            store.update("validations", key, stage="f3", status="pending", f2_seen=1, f2_location=output["location"])
            return
        store.update("validations", key, status="done", f2_seen=0, ok=0)
        failed = f"F2 on {item['trajectory_id']}: observation not seen"
    else:
        good = output["outcome"] == "followed"
        store.update("validations", key, status="done", f3_outcome=output["outcome"],
                     f3_action_location=output["action_location"], ok=int(good))
        if good:
            failed = None
        else:
            failed = f"F3 on {item['trajectory_id']}: {output['outcome']} for the new action"
    if failed:
        store.x("UPDATE validations SET status='cancelled' WHERE trigger_id=? AND attempt=? AND status='pending'", trig["id"], trig["attempt"])
        return _attempt_failed(store, trig, {"action": trig["new_action"], "purpose": trig["new_purpose"], "failed_check": failed})
    rows = store.q("SELECT * FROM validations WHERE trigger_id=? AND attempt=?", trig["id"], trig["attempt"])
    if all(r["status"] == "done" and r["ok"] == 1 for r in rows):
        _reword_succeeded(store, trig, rows)


def _attempt_failed(store, trig, previous):
    inv = inv_row(store, trig["invariant_id"])
    store.event("reword_attempt_failed", inv["task_id"], inv["id"], trig["trajectory_id"], attempt=trig["attempt"], **previous)
    if trig["attempt"] < 2:
        store.update("triggers", {"id": trig["id"]}, stage="reword", attempt=trig["attempt"] + 1,
                     previous_json=json.dumps(previous, ensure_ascii=False))
        return
    if trig["label"] == "pass":  # DESIGN.md 4.5
        deactivate(store, inv["id"], "removed")
        store.update("triggers", {"id": trig["id"]}, status="done", result="reword_failed_removed")
        store.event("reword_failed", inv["task_id"], inv["id"], trig["trajectory_id"], trigger="pass", effect="invariant removed")
    else:
        store.update("triggers", {"id": trig["id"]}, status="done", result="reword_failed_kept")
        store.event("reword_failed", inv["task_id"], inv["id"], trig["trajectory_id"], trigger="fail",
                    effect="invariant kept; the triggering cell counts 0 for importance")


def _reword_succeeded(store, trig, rows):
    inv = inv_row(store, trig["invariant_id"])
    task = store.one("SELECT * FROM tasks WHERE task_id=?", inv["task_id"])
    by = {r["trajectory_id"]: r for r in rows}
    evidence = {run: {"observation": by[tid]["f2_location"], "action": by[tid]["f3_action_location"]}
                for run, tid in (("A", task["p1"]), ("B", task["p2"]))}
    deactivate(store, inv["id"], "retired")
    new_id = add_invariant(store, task, inv["local_id"], facts_of(inv), {"text": trig["new_action"], "purpose": trig["new_purpose"]},
                           json.loads(inv["follows_json"]), evidence, "reword", parent_id=inv["id"], attempt=trig["attempt"],
                           prefix="r")
    if trig["label"] == "pass":  # DESIGN.md 4.5: the validation verdicts become the triggering run's cell
        v = by[trig["trajectory_id"]]
        _cell_done(store, {"invariant_id": new_id, "trajectory_id": trig["trajectory_id"]}, "followed",
                   f2_seen=1, f2_location=v["f2_location"], f3_outcome="followed", f3_action_location=v["f3_action_location"])
    store.update("triggers", {"id": trig["id"]}, status="done", result="reworded", new_invariant=new_id)
    store.event("reworded", inv["task_id"], inv["id"], trig["trajectory_id"], new_invariant=new_id, old_action=inv["action"],
                new_action=trig["new_action"], attempt=trig["attempt"], trigger=trig["label"])
