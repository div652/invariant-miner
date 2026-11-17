"""invariant_mining.agent and the job validators with a scripted model (no real model)."""

import json
import tempfile
from pathlib import Path

from im_fixtures import Checks, ScriptedConversation, call, three_steps, write_session

from invariant_mining import config, jobs
from invariant_mining.agent import run_agent
from invariant_mining.trajectory import parse_session

c = Checks("test_im_agent")
tmp = Path(tempfile.mkdtemp())
t = parse_session(write_session(tmp / "a/session.v2.jsonl", "Find the file.", three_steps("t1")), "t1", "task", "pass")
t2 = parse_session(write_session(tmp / "b/session.v2.jsonl", "Find the file.", three_steps("t2")), "t2", "task", "pass")
cfg = config.load(None)


def run(spec, script, **over):
    conf = config.merge(cfg, over)
    conv = ScriptedConversation(script)
    res = run_agent(spec, lambda sp, tools: conv, conf, tmp / f"job{run.n}")
    run.n += 1
    return res, conv


run.n = 0

# --- F2: a rejected submit, then an accepted one
spec = jobs.build("f2_seen", "luna", {"facts": ["keyword search counts per file", "a file with most hits"]}, {"T": t})
c.check("1. keyword search counts per file" in spec.user_text and "t1" in spec.user_text and "action" not in spec.user_text.lower(),
        "F2 user message: the facts and sizes, no action")
res, conv = run(spec, [
    [call("overview")],
    [call("submit", seen=True, location="s2.o1", evidence=[{"fact": 1, "location": "s2.o1", "quote": "a.txt:3"},
                                                             {"fact": 2, "location": "s3.r", "quote": "b.txt has most hits"}])],
    [call("submit", seen=True, location="s3.r", evidence=[{"fact": 1, "location": "s2.o1", "quote": "a.txt:3"},
                                                            {"fact": 2, "location": "s3.r", "quote": "b.txt has most hits"}])],
])
c.check(res.ok and res.output["location"] == "s3.r" and res.steps == 3, "F2: accepted after fixing the location")
c.check("must be where ALL facts hold" in conv.results[1][0][1] or "FIRST location" in conv.results[1][0][1],
        "F2: a location before the last fact's evidence is rejected with a reason")
lines = (tmp / "job0" / "transcript.jsonl").read_text().splitlines()
c.check(len(lines) == 3 and json.loads(lines[0])["results"][0]["tool"] == "overview", "transcript: one record per step")
c.check(json.loads((tmp / "job0" / "output.json").read_text())["seen"] is True, "output.json written")

# --- nudge when the model calls no tool; budget
res, conv = run(spec, [[], [call("submit", seen=False, location=None, evidence=[])]])
c.check(res.ok and conv.users and "Every turn must call a tool" in conv.users[0], "a turn without tool calls gets a nudge")
res, conv = run(spec, [[call("overview")]] * 5, budgets={"f2_seen": 3})
c.check(not res.ok and "step budget" in res.error, "step budget ends the job")
res, conv = run(spec, [[call("submit", seen="maybe", location=None, evidence=[])]] * 3)
c.check(not res.ok and "3 invalid submits" in res.error, "three invalid submits end the job (no hedging values)")

# --- context guard
res, conv = run(spec, [[call("read_output", loc="s2.o2")], [call("submit", seen=False, location=None, evidence=[])]],
                context_guard=0.0001)
c.check(res.ok and conv.elided == 1, "context guard elides past the threshold")

# --- F3 validator
v = jobs.make_validate_f3(t, "s2.o1")
c.check(v({"outcome": "followed", "action_location": "s3.c1", "quote": "x"})[0], "F3: followed after the pinned location")
c.check(not v({"outcome": "followed", "action_location": "s1.c1", "quote": "x"})[0], "F3: followed before the pinned location is rejected")
c.check(v({"outcome": "only_before", "action_location": "s1.c1", "quote": "x"})[0], "F3: only_before before the pinned location")
c.check(not v({"outcome": "only_before", "action_location": "s3.c1", "quote": "x"})[0], "F3: only_before after it is rejected")
c.check(v({"outcome": "not_followed", "action_location": "s3.c1", "quote": "x"})[2]["action_location"] is None, "F3: not_followed has no location")
c.check(not v({"outcome": "unclear", "action_location": None, "quote": "x"})[0], "F3: only the four outcomes")
c.check(not v({"outcome": "followed", "action_location": "s3.c1", "quote": "x", "confidence": 0.7})[0], "F3: no extra fields (no confidence)")
vphi = jobs.make_validate_f3(t, "start")
c.check(not vphi({"outcome": "pinning_wrong", "action_location": None, "quote": ""})[0] and
        vphi({"outcome": "followed", "action_location": "s1.c1", "quote": ""})[0], "F3 with an empty observation: followed / not_followed only")

# --- too-narrow validator
vt = jobs.make_validate_tn(t, "s2.o1")
c.check(vt({"purpose_achieved_otherwise": True, "location": "s3.c1", "quote": "x"})[0] and
        not vt({"purpose_achieved_otherwise": True, "location": "s1.c1", "quote": "x"})[0], "too-narrow: the other action must come after the pinned location")

# --- F1: two runs, validator, evidence check
spec1 = jobs.build("f1_propose", "opus", {}, {"A": t, "B": t2})
c.check("Run A = trajectory `t1`" in spec1.user_text and "Run B = trajectory `t2`" in spec1.user_text, "F1 user message names both runs")
good = {"invariants": [
    {"id": "i1", "observation": [{"fact": "keyword search counts per file", "source": "tool_result", "reason": "the choice uses the counts"}],
     "action": {"text": "picks the file with most hits", "purpose": "focus on the most relevant file"}, "follows": [],
     "evidence": {"A": {"observation": "s2.o1", "action": "s3.r"}, "B": {"observation": "s2.o1", "action": "s3.r"}}},
    {"id": "i2", "observation": [], "action": {"text": "lists the workspace first", "purpose": "know the inputs"}, "follows": ["i1"],
     "evidence": {"A": {"observation": "start", "action": "s1.c1"}, "B": {"observation": "s3.r", "action": "s1.c1"}}}],
    "roles": [{"term": "file with most hits", "meaning": "the file whose keyword count is highest"}]}
ok, err, norm = jobs.validate_f1(good)
c.check(ok and len(norm["invariants"]) == 2, "F1: a valid output")
probs = jobs.f1_evidence_problems(norm["invariants"][1], {"A": t, "B": t2})
c.check(len(probs) == 2 and any("comes before" in p for p in probs) and any("start" in p for p in probs),
        "F1 evidence check: action before observation and a non-start empty observation are reported")
bad = json.loads(json.dumps(good))
bad["invariants"][0]["observation"][0]["reason"] = ""
c.check(not jobs.validate_f1(bad)[0], "F1: a fact without a reason is rejected")
bad = json.loads(json.dumps(good))
bad["invariants"][1]["follows"] = ["i9"]
c.check(not jobs.validate_f1(bad)[0], "F1: follows must name existing ids")
bad = json.loads(json.dumps(good))
bad["invariants"][0]["observation"][0]["source"] = "external"
c.check(not jobs.validate_f1(bad)[0], "F1: source labels are environment / task / tool_result / reasoning")

# --- what each kind is shown (DESIGN.md principle 4)
s3 = jobs.build("f3_followed", "luna", {"facts": ["f"], "action": "does x", "location": "s2.o1"}, {"T": t})
c.check("does x" in s3.user_text and "purpose" not in s3.user_text.lower() and "reason" not in s3.user_text.lower(), "F3 sees the action, not the purpose or reasons")
st = jobs.build("too_narrow", "opus", {"facts": ["f"], "action": "does x", "purpose": "get y", "location": "s2.o1"}, {"T": t})
c.check("get y" in st.user_text, "the too-narrow check sees the purpose")
sr = jobs.build("f1_reword", "opus", {"facts": [{"fact": "f", "source": "task", "reason": "r"}], "action": "does x", "purpose": "get y",
                                       "alt_location": "s3.c1", "previous": {"action": "does z", "purpose": "p", "failed_check": "F3 on t1: not_followed"}},
                {"T": t})
c.check("learnt from earlier runs of this task" in sr.user_text and "s3.c1" in sr.user_text and "failed validation" in sr.user_text,
        "reword: told the invariant was learnt earlier, the alternative's location, the failed first attempt")
c.done()
