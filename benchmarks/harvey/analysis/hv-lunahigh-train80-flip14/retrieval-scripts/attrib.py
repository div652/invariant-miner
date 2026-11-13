import pickle, re, collections, json, os
from classify import *
from gold import gold
d = pickle.load(open('/tmp/retr/data.pkl', 'rb'))
WRITE_TARGETS = [re.compile(r">\s*['\"]?([\w./-]+\.(?:txt|md|json|csv|tsv|log))"), re.compile(r"Path\(['\"]([^'\"]+\.(?:txt|md|json|csv|tsv))['\"]\)"),
                 re.compile(r"open\(['\"]([^'\"]+\.(?:txt|md|json|csv|tsv))['\"]\s*,\s*['\"][wa]"), re.compile(r"out(?:file)?\s*=\s*['\"]([^'\"]+\.(?:txt|md|json|csv|tsv))")]
def produced_files(cmd):
    out = set()
    for r in WRITE_TARGETS:
        out |= {os.path.basename(x) for x in r.findall(cmd)}
    return out
def answer_step(calls):
    for c in calls:
        if c["name"] == "write" and "response" in json.dumps(c["args"]): return c["step"]
    return 10**9
def events(t, lab):
    """Per call: (step, method, effective_method, text, args_str, flags)."""
    v = d[(t, lab)]; producer = {}; res = []
    for c in v["calls"]:
        m = classify(c); text = c["text"] or ""; a = json.dumps(c["args"]) if not isinstance(c["args"], str) else c["args"]
        eff = m
        if m == "bash" or m.startswith("bash:"):
            for f in produced_files(cmd_of(c)): producer[f] = m
        if m in ("read:own-file", "grep:own-text"):
            target = os.path.basename((c["args"] or {}).get("file_path") or (c["args"] or {}).get("path") or "") if isinstance(c["args"], dict) else ""
            eff = producer.get(target, m)
            if eff != m: eff = eff + " (via file)"
        res.append({"step": c["step"], "m": m, "eff": eff, "text": text, "args": a, "timeout": bool(TIMEOUT.search(text)),
                    "cap": bool(CAP.search(text)), "name": c["name"]})
    return res
TARGETED = lambda e: not e.split(" (via")[0] in ("glob:enumerate", "bash:list", "glob:matter-scoped", "read:spill(fails)", "todo_write", "write", "edit", "bash:extract-one-matter", "read:corpus-file")
rows = []
TASKS = sorted({t for t, _ in d})
for t in TASKS:
    g, prec, crit = gold(t)
    for lab in ("run1", "run2", "run3"):
        v = d[(t, lab)]; ev = events(t, lab); ans = answer_step(v["calls"])
        for mid, cids in g.items():
            seen = [(e["step"], e["eff"]) for e in ev if e["step"] < ans and mid in e["text"]]
            opened = [e["step"] for e in ev if e["step"] < ans and mid in e["args"] and e["m"] in ("read:corpus-file", "bash:extract-one-matter", "bash:extract-subset", "glob:matter-scoped")
                      and not (e["m"] == "glob:matter-scoped")]
            listed = [e["step"] for e in ev if e["step"] < ans and mid in e["args"] and e["m"] == "glob:matter-scoped"]
            inc = v["verdicts"][cids[0]][0] == "pass"
            rows.append({"task": t, "run": lab, "matter": mid, "included": inc, "seen": seen, "opened": opened, "listed": listed,
                         "targeted_methods": sorted({s[1] for s in seen if TARGETED(s[1])}), "first_seen": seen[0] if seen else None, "answer_step": ans})
pickle.dump(rows, open('/tmp/retr/rows.pkl', 'wb'))
print(len(rows), "gold (task, run, matter) items;", sum(r["included"] for r in rows), "included")
