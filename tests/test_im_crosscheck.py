"""Invariant cross-check (crosscheck.py) with a scripted policy model: a two-task mining run, then the cross-check of its
invariants with support > 0 on the passing runs of the other task. Nothing may be removed or reworded."""

import json
import tempfile
from pathlib import Path

from im_fixtures import Checks, three_steps, write_session

from invariant_mining import config, crosscheck
from invariant_mining.cli import prepare
from invariant_mining.models import Call, Conversation, StepResult
from invariant_mining.pipeline import Pipeline
from invariant_mining.store import Store

c = Checks("test_im_crosscheck")
tmp = Path(tempfile.mkdtemp())
TRAJ = {"A": {"PA1": "pass", "PA2": "pass", "PA3": "pass", "XA": "fail"},
        "B": {"PB1": "pass", "PB2": "pass", "PB3": "pass", "XB": "fail"}}
manifest = {"trajectories": [{"id": k, "task_id": f"task-{t}", "label": v,
                              "session_log": str(write_session(tmp / "logs" / k / "session.v2.jsonl", "Task text.", three_steps(k)))}
                             for t, runs in TRAJ.items() for k, v in runs.items()],
            "tasks": [{"task_id": "task-A", "p1": "PA1", "p2": "PA2"}, {"task_id": "task-B", "p1": "PB1", "p2": "PB2"}]}
(tmp / "manifest.json").write_text(json.dumps(manifest))
INV = {"task-A": [("a1", "fact-x", "act-x"), ("a2", "fact-y", "act-y")],
       "task-B": [("b1", "fact-z", "act-z"), ("b0", "fact-w", "act-w")]}
PHASE = {"name": "mine"}
# mining: each invariant seen and followed on its own task's third passing run, except b0 (not seen: support 0)
MINE_SEEN = {"fact-x": {"PA3"}, "fact-y": {"PA3"}, "fact-z": {"PB3"}, "fact-w": set()}
# cross-check: x seen in PB1 (violated) and PB2 (followed); y seen in PB1 (Luna not followed, Opus followed);
# z seen in PA1 (not followed, purpose achieved another way)
CROSS_SEEN = {"fact-x": {"PB1", "PB2"}, "fact-y": {"PB1"}, "fact-z": {"PA1"}}
CROSS_F3 = {("act-x", "PB1", None): "not_followed", ("act-x", "PB2", None): "followed",
            ("act-y", "PB1", "luna"): "not_followed", ("act-y", "PB1", "opus"): "followed", ("act-z", "PA1", None): "not_followed"}


def answer(spec):
    k, inp = spec.kind, spec.inputs
    if k == "f1_propose":
        task = spec.trajectories["A"].task_id
        return {"invariants": [{"id": i, "observation": [{"fact": f, "source": "tool_result", "reason": "needed"}],
                                "action": {"text": a, "purpose": "purpose of " + a}, "follows": [],
                                "evidence": {r: {"observation": "s2.o1", "action": "s3.c1"} for r in "AB"}}
                               for i, f, a in INV[task]], "roles": []}
    tid = spec.trajectories["T"].id
    if k == "f2_seen":
        seen = tid in (MINE_SEEN if PHASE["name"] == "mine" else CROSS_SEEN).get(inp["facts"][0], set())
        return {"seen": seen, "location": "s2.o1" if seen else None,
                "evidence": [{"fact": 1, "location": "s2.o1", "quote": "b.txt:7"}] if seen else []}
    if k == "f3_followed":
        if PHASE["name"] == "mine":
            out = "followed"
        else:
            out = CROSS_F3.get((inp["action"], tid, spec.model_key)) or CROSS_F3[(inp["action"], tid, None)]
        return {"outcome": out, "action_location": "s3.c1" if out == "followed" else None,
                "quote": "echo done" if out == "followed" else ""}
    if k == "too_narrow":
        if inp["action"] == "act-z":
            return {"outcome": "achieved_otherwise", "location": "s3.c1", "quote": "echo done"}
        return {"outcome": "not_achieved", "location": None, "quote": ""}
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
    calls.append((PHASE["name"], spec.kind, spec.model_key, spec.trajectories.get("T").id if "T" in spec.trajectories else "AB"))
    return Policy(spec)


src = tmp / "mine"
prepare(tmp / "manifest.json", None, src)
cfg = config.load(src / "config.json")
cfg["concurrency"] = 4
Pipeline(src, cfg, conv_factory=factory, log=lambda *a: None).run()

PHASE["name"] = "cross"
xc = tmp / "xc"
summary = crosscheck.prepare_cross_check(src, xc)
c.check(summary["invariants"] == 3 and summary["cells"] == 9,
        "prepare: the 3 invariants with support > 0 (b0 has none), each on the other task's 3 passing runs = 9 cells")
s = Store(xc / "state.sqlite")
c.check(not s.one("SELECT 1 FROM cells c JOIN trajectories t ON t.id=c.trajectory_id JOIN invariants i ON i.id=c.invariant_id "
                  "WHERE t.task_id=i.task_id OR t.label!='pass'"), "no cell on the invariant's own task or on a failing run")
Pipeline(xc, config.load(xc / "config.json"), conv_factory=factory, log=lambda *a: None).run()
rep = crosscheck.write(xc)
inv = {i["local_id"]: i for i in rep["invariants"]}
c.check([v["trajectory"] for v in inv["a1"]["violations"]] == ["PB1"] and inv["a1"]["seen"] == 2 and inv["a1"]["outcomes"].get("followed") == 1,
        "a1: seen in 2 runs of task B, followed in PB2, violated in PB1 (Opus agreed, purpose not achieved otherwise)")
c.check(not inv["a2"]["violations"] and inv["a2"]["outcomes"].get("followed") == 1,
        "a2: Luna said not followed, the Opus re-check said followed -> no violation")
c.check(not inv["b1"]["violations"] and inv["b1"]["outcomes"].get("purpose_otherwise") == 1,
        "b1: purpose achieved another way -> not a violation")
c.check(not s.q("SELECT * FROM triggers") and all(r["status"] == "active" for r in s.q("SELECT status FROM invariants")),
        "nothing removed or reworded, no triggers")
c.check(not any(p == "cross" and k == "f1_propose" for p, k, _, _ in calls), "no F1 in the cross-check")
c.check(sum(1 for p, k, m, t in calls if p == "cross" and t == "PB1" and m == "opus") >= 4,
        "violations go through the Opus re-check (F2, F3) and the too-narrow check")
md = (xc / "cross_check.md").read_text()
c.check("## Violated on other tasks (1 of 3 invariants)" in md and "| a1 (`task-A`)" in md and "`task-B` PB1" in md,
        "cross_check.md lists the violated invariant with the run")
c.done()
