import json, pickle
from pathlib import Path
B = Path.home() / "dsh-bench-harness/runs"
RUNS = {"run1": "hv-fk250-lunahigh-20261110T175632Z", "run2": "hv-fk250-lunahigh-rep2-20261112T122308Z",
        "run3": "hv-fk250-lunahigh-rep3-20261112T141312Z"}
TASKS = "048 066 072 082 104 137 162 210 028 167 185 192 198 200 051 071 085 107 120 133 139 153 216 229 233 038 044 083 088 208 231 235".split()
out = {}
for t in TASKS:
    for lab, r in RUNS.items():
        F = next((B / r / "tasks" / f"firm-knowledge__tasks__{t}" / "dsh-home").rglob("session.v2.jsonl"))
        step = 0; rs = {}
        for l in F.read_text().split("\n"):
            if not l.strip(): continue
            e = json.loads(l)
            if e["type"] == "step/start": step += 1
            if e["type"] == "assistant/message":
                txt = "\n".join(b.get("text", "") for b in e["data"]["message"]["content"] if b.get("type") == "reasoning" and b.get("text"))
                if txt: rs[step] = rs.get(step, "") + txt
        out[(t, lab)] = rs
pickle.dump(out, open("/tmp/retr/reasoning.pkl", "wb"))
n = sum(len(v) for v in out.values()); steps = sum(1 for v in out.values() for _ in v)
print(n, "steps with a reasoning summary across", len(out), "runs")
