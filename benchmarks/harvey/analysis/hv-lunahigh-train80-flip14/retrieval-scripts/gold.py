import json, re
from pathlib import Path
LAB = Path.home() / "dsh-bench-harness/work/harvey-labs/tasks/firm-knowledge/tasks"
ID = re.compile(r"\b(10\d\d-\d{5})\b")
def gold(t):
    crit = json.loads((LAB / t / "task.json").read_text())["criteria"]
    g = {}  # matter -> list of criterion ids that need it (recall-type)
    prec = None
    for c in crit:
        if "precision" in c["title"].lower():
            prec = c["id"]; continue
        ids = ID.findall(c["title"]) or ID.findall(c["match_criteria"])
        for i in dict.fromkeys(ids): g.setdefault(i, []).append(c["id"])
    return g, prec, crit
if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        g, p, crit = gold(t)
        print(t, f"{len(crit)} criteria; gold {len(g)}:", {k: v for k, v in g.items()}, "| no-id criteria:",
              [c["title"][:50] for c in crit if not (ID.findall(c["title"]) or ID.findall(c["match_criteria"])) and c["id"] != p][:4])
