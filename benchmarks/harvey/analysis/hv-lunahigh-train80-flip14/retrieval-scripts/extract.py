"""Extract every tool call (step, name, args, the text the model saw) for the 32 flip tasks x 3 base runs."""
import json, glob, re, pickle
from pathlib import Path
B = Path.home() / "dsh-bench-harness/runs"
RUNS = {"run1": "hv-fk250-lunahigh-20261110T175632Z", "run2": "hv-fk250-lunahigh-rep2-20261112T122308Z",
        "run3": "hv-fk250-lunahigh-rep3-20261112T141312Z"}
TASKS = "048 066 072 082 104 137 162 210 028 167 185 192 198 200 051 071 085 107 120 133 139 153 216 229 233 038 044 083 088 208 231 235".split()
out = {}
for t in TASKS:
    for lab, r in RUNS.items():
        name = f"firm-knowledge__tasks__{t}"
        F = next((B / r / "tasks" / name / "dsh-home").rglob("session.v2.jsonl"))
        ev = [json.loads(l) for l in F.read_text().split("\n") if l.strip()]
        calls, order = {}, []
        for e in ev:
            d = e.get("data", {})
            if e["type"] == "tool/call":
                a = d.get("arguments")
                try: a = json.loads(a) if isinstance(a, str) else a
                except Exception: pass
                calls[d["callId"]] = {"step": int(d["step"]), "name": d["name"], "args": a, "text": None, "err": None}
                order.append(d["callId"])
            elif e["type"] == "tool/result":
                for c in d["message"]["content"]:
                    if c.get("type") == "tool-result" and c["toolCallId"] in calls:
                        calls[c["toolCallId"]]["text"] = "".join(x.get("text", "") for x in (c.get("content") or []) if isinstance(x, dict))
                        calls[c["toolCallId"]]["err"] = c.get("isError")
        steps = sum(e["type"] == "step/start" for e in ev)
        # per-criterion verdicts
        sc = json.loads((B / r / "grading/lab-root/results" / name / "scores.json").read_text())
        out[(t, lab)] = {"calls": [calls[i] for i in order], "steps": steps,
                         "verdicts": {c["id"]: (c["verdict"], c["title"]) for c in sc["criteria_results"]},
                         "all_pass": sc["all_pass"]}
pickle.dump(out, open("/tmp/retr/data.pkl", "wb"))
print(len(out), "trajectories,", sum(len(v["calls"]) for v in out.values()), "tool calls")
