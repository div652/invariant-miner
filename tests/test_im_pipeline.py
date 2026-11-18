"""End to end with a scripted policy model: prepare -> pipeline -> report, one case per rule of DESIGN.md sections 4-6."""

import json
import tempfile
from pathlib import Path

from im_fixtures import Checks, three_steps, write_session

from invariant_mining import config, report, rules
from invariant_mining.cli import prepare
from invariant_mining.models import Call, Conversation, StepResult
from invariant_mining.pipeline import Pipeline

c = Checks("test_im_pipeline")
tmp = Path(tempfile.mkdtemp())
TRAJ = {"P1": "pass", "P2": "pass", "P3": "pass", "X1": "fail", "X2": "fail"}
manifest = {"trajectories": [{"id": k, "task_id": "task-1", "label": v,
                              "session_log": str(write_session(tmp / "logs" / k / "session.v2.jsonl", "Task text.", three_steps(k)))}
                             for k, v in TRAJ.items()],
            "tasks": [{"task_id": "task-1", "p1": "P1", "p2": "P2"}]}
(tmp / "manifest.json").write_text(json.dumps(manifest))

# --- the policy: what the scripted model answers ------------------------------------------------------------------------
INV = [  # local id, facts, action
    ("i1", ["fact-a"], "act-a"), ("i2", [], "act-phi"), ("i3", ["fact-c"], "act-c-narrow"), ("i4", ["fact-d"], "act-d"),
    ("i5", ["fact-e"], "act-e"), ("i6", ["fact-f"], "act-f-narrow"), ("i7", ["fact-g"], "act-g"), ("i8", ["fact-h"], "act-h")]
SEEN = {"fact-a": {"P3", "X1"}, "fact-c": {"P1", "P2", "P3", "X1"}, "fact-d": {"P3"}, "fact-e": {"P3"},
        "fact-f": {"P1", "P2", "X1"}, "fact-g": {"P3"}, "fact-h": {"X2"}}
F3 = {  # (action, trajectory, model) -> (outcome, location); model None = either
    ("act-a", "P3", None): ("followed", "s3.c1"), ("act-a", "X1", None): ("not_followed", None),
    ("act-phi", "P3", None): ("followed", "s1.c1"), ("act-phi", "X1", None): ("not_followed", None), ("act-phi", "X2", None): ("followed", "s1.c1"),
    ("act-c-narrow", "P3", None): ("not_followed", None), ("act-c-narrow", "X1", None): ("not_followed", None),  # may run before i3 is retired
    ("act-c-broad", "P1", None): ("followed", "s3.c1"), ("act-c-broad", "P2", None): ("followed", "s3.c1"),
    ("act-c-broad", "P3", None): ("followed", "s3.c1"), ("act-c-broad", "X1", None): ("not_followed", None),
    ("act-d", "P3", None): ("not_followed", None),
    ("act-e", "P3", "luna"): ("not_followed", None), ("act-e", "P3", "opus"): ("followed", "s3.c1"),
    ("act-f-narrow", "X1", None): ("not_followed", None),
    ("act-f-broad1", "P1", None): ("not_followed", None), ("act-f-broad1", "P2", None): ("followed", "s3.c1"),
    ("act-f-broad2", "P1", None): ("not_followed", None), ("act-f-broad2", "P2", None): ("followed", "s3.c1"),
    ("act-g", "P3", None): ("pinning_wrong", None), ("act-h", "X2", None): ("only_before", "s1.c1")}
NARROW = {("act-c-narrow", "P3"): "s3.c1", ("act-f-narrow", "X1"): "s3.c1"}  # purpose achieved otherwise; else no


def answer(spec):
    k, inp = spec.kind, spec.inputs
    if k == "f1_propose":
        return {"invariants": [{"id": i, "observation": [{"fact": f, "source": "tool_result", "reason": "needed"} for f in facts],
                                "action": {"text": a, "purpose": "purpose of " + a}, "follows": [],
                                "evidence": {r: {"observation": "s2.o1" if facts else "start", "action": "s3.c1"} for r in "AB"}}
                               for i, facts, a in INV], "roles": [{"term": "x", "meaning": "y"}]}
    tid = spec.trajectories["T"].id
    if k == "f2_seen":
        seen = tid in SEEN[inp["facts"][0]]
        return {"seen": seen, "location": "s2.o1" if seen else None,
                "evidence": [{"fact": 1, "location": "s2.o1", "quote": "b.txt:7"}] if seen else []}
    if k == "f3_followed":
        key = (inp["action"], tid, spec.model_key)
        out, loc = F3.get(key) or F3[(inp["action"], tid, None)]
        return {"outcome": out, "action_location": loc, "quote": {"s3.c1": "echo done", "s1.c1": "ls"}.get(loc, "")}
    if k == "too_narrow":
        loc = NARROW.get((inp["action"], tid))
        return {"purpose_achieved_otherwise": loc is not None, "location": loc, "quote": "echo done" if loc else ""}
    if k == "f1_reword":
        if inp["action"] == "act-c-narrow":
            return {"action": {"text": "act-c-broad", "purpose": "p"}}
        return {"action": {"text": "act-f-broad2" if inp.get("previous") else "act-f-broad1", "purpose": "p"}}
    raise AssertionError(k)


class Policy(Conversation):
    def __init__(self, spec):
        self.spec, self.n = spec, 0

    def step(self):
        self.n += 1
        if self.n == 1:
            if self.spec.kind == "f1_propose":
                return StepResult([Call("c1", "read_steps", {"run": "A", "from_step": 1, "to_step": 3}),
                                   Call("c1b", "read_steps", {"run": "B", "from_step": 1, "to_step": 3})])
            return StepResult([Call("c1", "overview", {})])
        return StepResult([Call("c2", "submit", answer(self.spec))])

    def add_results(self, results): pass
    def add_user(self, text): pass
    def est_tokens(self): return 0
    def elide(self, target_tokens, keep=("read_notes",)): return 0


calls = []


def factory(spec, tools):
    calls.append((spec.kind, spec.model_key, spec.trajectories.get("T").id if "T" in spec.trajectories else "AB",
                  json.dumps(spec.inputs, sort_keys=True)))
    return Policy(spec)


run_dir = tmp / "run"
prepare(tmp / "manifest.json", None, run_dir)
cfg = config.load(run_dir / "config.json")
cfg["concurrency"] = 4
p = Pipeline(run_dir, cfg, conv_factory=factory, log=lambda *a: None)
# simulate a stopped run: some work marked running but never finished -> reset to pending on start
rules.ready_work(p.store, 1)
c.check(p.store.one("SELECT status FROM tasks")["status"] == "running", "work is marked running when dispatched")
p.run()
rep = report.write(run_dir)
inv = {i["id"]: i for i in rep["tasks"][0]["invariants"]}
c.check(rep["tasks"][0]["status"] == "done", "resumed: the stale running task was reset and finished")
c.check(inv["T1.i1"]["status"] == "active" and inv["T1.i1"]["support"] == 1 and inv["T1.i1"]["importance"] == 1,
        "i1: support from P3 (seen, followed), importance from X1 (seen, not followed, purpose not achieved otherwise)")
c.check(inv["T1.i2"]["support"] == 1 and inv["T1.i2"]["importance"] == 1 and inv["T1.i2"]["cells"]["X2"] == "followed",
        "i2 (empty observation): F2 skipped; support and importance like any invariant")
c.check(not any(k == "f2_seen" and "act-phi" in inp for k, _, _, inp in calls) and
        not any(k == "f2_seen" and '"facts": []' in inp for k, _, _, inp in calls), "no F2 job for the empty observation")
c.check(inv["T1.i3"]["status"] == "retired" and inv["T1.ri3"]["status"] == "active" and inv["T1.ri3"]["action"] == "act-c-broad",
        "i3: too narrow on a passing run -> reworded, validated, replaced (T1.ri3)")
c.check(inv["T1.ri3"]["support"] == 1 and inv["T1.ri3"]["importance"] == 1 and inv["T1.ri3"]["cells"]["P3"] == "followed",
        "ri3: the validation verdict is P3's cell (support 1); re-evaluated on X1 (importance 1)")
c.check(sum(1 for k, _, t, inp in calls if k == "f3_followed" and t == "P3" and "act-c-broad" in inp) == 1,
        "ri3: P3 is not checked again after its validation")
c.check(inv["T1.ri3"]["evidence"]["A"] == {"observation": "s2.o1", "action": "s3.c1"}, "ri3: evidence from the validation on P1/P2")
c.check(inv["T1.i4"]["status"] == "removed" and any(e["kind"] == "removed" for e in inv["T1.i4"]["events"]),
        "i4: passing run, Opus confirms not followed, purpose not achieved otherwise -> removed")
c.check([m for k, m, t, inp in calls if t == "P3" and '"action": "act-d"' in inp] == ["luna", "opus", "opus"] and
        [m for k, m, t, inp in calls if t == "P3" and '"facts": ["fact-d"]' in inp and k == "f2_seen"] == ["luna", "opus"],
        "i4: F2/F3 by Luna, then F2/F3 re-check and the too-narrow check by Opus")
c.check(inv["T1.i5"]["status"] == "active" and inv["T1.i5"]["support"] == 1 and
        any(e["kind"] == "recheck_disagrees" for e in inv["T1.i5"]["events"]), "i5: Opus's verdict replaces Luna's (followed: support +1), disagreement logged")
c.check(inv["T1.i6"]["status"] == "active" and inv["T1.i6"]["importance"] == 0 and inv["T1.i6"]["cells"]["X1"] == "purpose_otherwise",
        "i6: too narrow on a failing run -> no importance point")
ev6 = [e["kind"] for e in inv["T1.i6"]["events"]]
c.check(ev6.count("reword_attempt_failed") == 2 and "reword_failed" in ev6, "i6: two rewording attempts failed validation -> invariant kept, logged")
c.check(sum(1 for k, _, t, inp in calls if k == "f2_seen" and t == "P1" and "fact-f" in inp) == 1,
        "i6: the second attempt reuses the first attempt's F2 verdicts")
c.check(sum(1 for k, _, t, inp in calls if k == "f2_seen" and t == "X1" and '"fact-f"' in inp) == 1 and
        not any(k == "f3_followed" and t == "X1" and "act-f-broad" in inp for k, _, t, inp in calls),
        "i6: a failing trigger is not part of the validation (P1 and P2 only)")
c.check(any(k == "f1_reword" and "failed validation" not in inp and '"previous"' in inp for k, _, _, inp in calls),
        "i6: the second attempt is given the first attempt and the failed check")
c.check(inv["T1.i7"]["cells"]["P3"] == "pinning_wrong" and inv["T1.i7"]["support"] == 0 and
        rep["tasks"][0]["events"].get("pinning_wrong") == 1, "i7: pinning wrong counts nothing and is counted")
c.check(inv["T1.i8"]["cells"]["X2"] == "only_before" and inv["T1.i8"]["importance"] == 0, "i8: only before counts nothing")
c.check(inv["T1.i2"]["first_violations"] == ["X1"] and inv["T1.i1"]["first_violations"] == [], "first violation in X1: the earliest observation (i2, start)")
c.check(not any(t in ("P1", "P2") for k, _, t, inp in calls if k in ("f2_seen", "f3_followed") and ("act-a" in inp or '"fact-a"' in inp)),
        "no cells on P1/P2 (only validations run there)")
c.check(rep["tasks"][0]["events"].get("f1_evidence_invalid", 0) == 0, "F1 evidence check ran (valid evidence, nothing logged)")
def first_last(pred):
    idx = [n for n, x in enumerate(calls) if pred(x)]
    return (min(idx), max(idx)) if idx else (None, None)
_, last_pass = first_last(lambda x: x[2] == "P3" and ('"fact-a"' in x[3] or '"act-a"' in x[3]))
first_fail, _ = first_last(lambda x: x[2] in ("X1", "X2") and ('"fact-a"' in x[3] or '"act-a"' in x[3]))
c.check(last_pass is not None and first_fail is not None and last_pass < first_fail,
        "passing first: i1's failing-run checks start after its passing-run checks are final")
c.check(not any(t in ("X1", "X2") and '"fact-d"' in inp for k, _, t, inp in calls),
        "passing first: i4 (removed by a passing run) is never checked on the failing runs")
c.check(not any(t in ("X1", "X2") and '"act-c-narrow"' in inp for k, _, t, inp in calls),
        "passing first: i3 is reworded before any failing run checks it; only ri3 is checked there")
n_jobs = p.store.one("SELECT COUNT(*) n FROM jobs")["n"]
c.check(n_jobs == len(calls), "every job recorded in the jobs table")
p.run()
c.check(p.store.one("SELECT COUNT(*) n FROM jobs")["n"] == n_jobs, "running again does nothing when nothing is pending")
from invariant_mining.cli import retry_errors
p.store.update("cells", {"invariant_id": "T1.i1", "trajectory_id": "X2"}, status="done", final_outcome="job_error", stage="f2")
retry_errors(run_dir)
p.run()
c.check(p.store.one("SELECT final_outcome FROM cells WHERE invariant_id='T1.i1' AND trajectory_id='X2'")["final_outcome"] == "not_seen",
        "retry-errors: a cell that ended in a job error runs again from its stage")
# add-runs: a new passing run for the task; every active invariant gets a cell on it, nothing is proposed again
from invariant_mining.cli import add_runs
new_log = write_session(tmp / "logs" / "P4" / "session.v2.jsonl", "Task text.", three_steps("P4"))
(tmp / "more.json").write_text(json.dumps({"trajectories": [{"id": "P4", "task_id": "task-1", "label": "pass", "session_log": str(new_log)}]}))
SEEN["fact-a"].add("P4")
F3[("act-a", "P4", None)] = ("followed", "s3.c1")
active_before = p.store.one("SELECT COUNT(*) n FROM invariants WHERE status='active'")["n"]
f1_before = sum(1 for k, *_ in calls if k == "f1_propose")
add_runs(run_dir, tmp / "more.json")
c.check(p.store.one("SELECT COUNT(*) n FROM cells WHERE trajectory_id='P4'")["n"] == active_before, "add-runs: one cell per active invariant")
p.run()
report.write(run_dir)
rep = json.loads((run_dir / "report.json").read_text())
inv = {i["id"]: i for i in rep["tasks"][0]["invariants"]}
c.check(inv["T1.i1"]["support"] == 2 and inv["T1.i1"]["cells"]["P4"] == "followed" and
        sum(1 for k, *_ in calls if k == "f1_propose") == f1_before, "add-runs: points add up over old and new runs; no new F1")
md = (run_dir / "report.md").read_text()
c.check("### Proposed by F1 (8)" in md and "| ri3 | i3 | act-c-narrow | act-c-broad |" in md and "### Removed (1)" in md
        and "| i4 |" in md and "Opus re-check" in md and "rewording failed twice" in md and "not followed ★" in md,
        "report.md: proposed, rewordings, removed with the reason, kept after failed rewordings, first violation mark")
c.done()
