"""invariant_mining.trajectory and .tools on a synthetic session log (no model)."""

import tempfile
from pathlib import Path

from im_fixtures import Checks, three_steps, write_session

from invariant_mining.tools import ToolBox, ToolError
from invariant_mining.trajectory import LocationError, parse_session

c = Checks("test_im_trajectory_tools")
tmp = Path(tempfile.mkdtemp())
log = write_session(tmp / "dsh-home/sessions/x/session.v2.jsonl", "Find the file with most hits for the keyword.",
                    three_steps("t1"), extra_user_after={2: "Please hurry."})
t = parse_session(tmp / "dsh-home", "t1", "task", "pass")  # directory with exactly one session log
locs = [i["loc"] for i in t.items]
c.check(locs[:4] == ["sys", "tools", "u1", "u2"], "sys, tools, then the task (u1) and the runtime message (u2) first")
c.check(locs[4:7] == ["s1.r", "s1.c1", "s1.o1"], "step 1: reasoning, call, output")
c.check(locs[7:13] == ["s2.r", "s2.t", "s2.c1", "s2.c2", "s2.o1", "s2.o2"], "step 2: reasoning, text, both calls, then both outputs")
c.check(locs[13] == "u3" and locs[14] == "s3.r", "a user message that arrived after step 2 sits there (u3)")
c.check(t.items[locs.index("s2.c1")]["name"] == "bash" and "grep" in t.items[locs.index("s2.c1")]["text"], "call items keep name and arguments")
c.check(t.meta["steps"] == 3 and t.meta["context_window"] == 922000 and t.meta["model"] == "test-model", "metadata")
c.check(all("replayState" not in i["text"] and "thinkingSignature" not in i["text"] for i in t.items), "encrypted replay state is not an item")
c.check(t.before("s2.c2", "s2.o1") and t.before("s2.o2", "u3") and t.before("start", "sys"), "location order")
c.check(t.position("s2.o2#100") == (locs.index("s2.o2"), 100), "offsets")
c.check(t.position("sys#?") == (0, 0) and t.position(" `s2.o2` ") == (locs.index("s2.o2"), 0), "a malformed offset or backticks: the item itself")
for bad in ("s9.o1", "s2.x1", "s2.o2#999999", "foo"):
    try:
        t.position(bad)
        c.check(False, f"{bad} rejected")
    except LocationError:
        c.check(True, f"{bad} rejected")

# --- tools (single trajectory) ---
tb = ToolBox({"T": t}, tmp / "notes.md", {"type": "object"}, "submit")
names = [d["name"] for d in tb.definitions()]
c.check(names == ["overview", "read_context", "read_steps", "read_output", "search", "note", "read_notes", "submit"], "tool set")
c.check("run" not in tb.definitions()[0]["parameters"]["properties"], "single trajectory: no run argument")
ov = tb.execute("overview", {})
c.check("s2:" in ov and "s2.c2 read(" in ov and "u3 (user message" in ov and "5,000 chars" in ov, "overview lists steps, calls, output sizes, user messages")
rs = tb.execute("read_steps", {"from_step": 2, "to_step": 2})
c.check("[s2.o2] output (5,000 characters; read the rest with read_output(loc='s2.o2', offset=2000))" in rs, "read_steps cuts long outputs and says how to read the rest")
c.check("u3" not in rs, "read_steps 2..2 stops before the next item outside the range")
ro = tb.execute("read_output", {"loc": "s2.o2", "offset": 4900, "length": 50})
c.check(ro.startswith("B" * 50) and "characters 4,900-4,950 of 5,000; continue with offset=4950" in ro, "read_output pages")
sr = tb.execute("search", {"pattern": "B.txt"})
c.check(sr.startswith("4 matches") and "s1.o1#6" in sr and "s2.c2#10" in sr, "search: plain text, case-insensitive, loc#offset")
sr2 = tb.execute("search", {"pattern": r"\d+$", "regex": True, "kinds": ["output"]})
c.check("s2.o1#" in sr2 and "s2.c1" not in sr2, "search: regex and kinds filter")
c.check(tb.execute("read_context", {"part": "u1"}).startswith("Find the file"), "read_context of the task")
tb.execute("note", {"text": "first"})
c.check("first" in tb.execute("read_notes", {}), "notes")
for name, args in (("read_output", {"loc": "s9.o1"}), ("read_steps", {"from_step": 5, "to_step": 6}),
                   ("search", {"pattern": "(", "regex": True}), ("bash", {}), ("read_context", {"part": "s1.r"})):
    try:
        tb.execute(name, args)
        c.check(False, f"{name}{args} is an error")
    except ToolError:
        c.check(True, f"{name}{args} is an error")

# --- tools (two trajectories, F1) ---
log2 = write_session(tmp / "b/session.v2.jsonl", "Find the file.", three_steps("t2"))
t2 = parse_session(log2, "t2", "task", "pass")
tb2 = ToolBox({"A": t, "B": t2}, tmp / "notes2.md", {"type": "object"}, "submit")
c.check(tb2.definitions()[0]["parameters"]["required"] == ["run"], "two trajectories: run is required")
c.check("t2" in tb2.execute("read_output", {"run": "B", "loc": "s1.o1"}), "run selects the trajectory")
try:
    tb2.execute("overview", {})
    c.check(False, "missing run is an error")
except ToolError:
    c.check(True, "missing run is an error")
c.done()
