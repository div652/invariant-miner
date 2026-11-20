"""Do any of the cross-consistent invariants share an observation? (user, 2026-11-20: "this is really critical")

    work/im-venv/bin/python docs/2same-invariant-algo/analysis/same_observation_check.py CROSS_CHECK_RUN OUT_DIR [--retry-errors]

--retry-errors: keep the existing verdicts in OUT_DIR/same_observation.json and judge again only the pairs that ended in an
error (4 at a time, with backoff on HTTP 429).

1. Exact: identical fact texts, identical fact sets (after lower-casing and stripping punctuation).
2. Lexical: token Jaccard of every pair of facts across invariants (pairs >= 0.4 listed).
3. Judge: every pair of observations, one fresh GPT-5.6 Luna (effort high) call per pair via CAO, answering one of
   same / one_contains_other / partial_overlap / different, with a one-line reason.
Writes OUT_DIR/same_observation.json and .md.
"""
import itertools, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

run, outdir = Path(sys.argv[1]), Path(sys.argv[2])
rep = json.loads((run / "cross_check.json").read_text())
invs = [i for i in rep["invariants"] if i["id"] in set(rep["cross_consistent"])]
name = lambda i: f"{i['task'].split('-')[0] if i['task'].startswith('world') else i['task'][:12]}…{i['task'][-8:]} {i['local_id']}"  # noqa: E731
norm = lambda t: re.sub(r"[^a-z0-9 ]+", " ", t.lower()).split()  # noqa: E731
obs_text = lambda i: "\n".join(f"- {f['fact']} [{f['source']}]" for f in i["observation"]) or "- (empty: always)"  # noqa: E731

exact_fact, same_set, lexical = [], [], []
for a, b in itertools.combinations(invs, 2):
    fa, fb = [" ".join(norm(f["fact"])) for f in a["observation"]], [" ".join(norm(f["fact"])) for f in b["observation"]]
    for x in fa:
        if x in fb:
            exact_fact.append((a["id"], b["id"], x))
    if sorted(fa) == sorted(fb):
        same_set.append((a["id"], b["id"]))
    for x in a["observation"]:
        for y in b["observation"]:
            sx, sy = set(norm(x["fact"])), set(norm(y["fact"]))
            j = len(sx & sy) / max(1, len(sx | sy))
            if j >= 0.4:
                lexical.append((round(j, 2), a["id"], b["id"], x["fact"], y["fact"]))

key = open("/home/agarwaldi/cao/profile/.gateway-key").read().strip()
SYSTEM = ("You compare the observations (preconditions) of two rules learnt from AI agents' work. Each observation is a "
          "list of facts that must all hold. Decide how the two observations relate as situations: \"same\" (the same "
          "situation: every fact of each has an equivalent in the other, wording aside), \"one_contains_other\" (all facts "
          "of one are in the other, which adds more), \"partial_overlap\" (they share at least one fact but each has a fact "
          "the other lacks), \"different\" (no shared fact). Judge only the observations, not the actions. Answer with one "
          "JSON object: {\"relation\": one of the four, \"reason\": one short sentence}.")


def judge(pair):
    a, b = pair
    body = {"model": "gpt-5.6-luna", "instructions": SYSTEM, "store": False, "reasoning": {"effort": "high"},
            "input": f"Observation A:\n{obs_text(a)}\n\nObservation B:\n{obs_text(b)}", "max_output_tokens": 8000}
    for attempt in range(6):
        try:
            req = urllib.request.Request("http://127.0.0.1:4141/v1/responses", data=json.dumps(body).encode(),
                                         headers={"authorization": f"Bearer {key}", "content-type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=300))
            text = "".join(c.get("text", "") for o in r.get("output", []) if o.get("type") == "message" for c in o.get("content", []))
            out = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
            if out.get("relation") in ("same", "one_contains_other", "partial_overlap", "different"):
                return a["id"], b["id"], out["relation"], out.get("reason", "")
        except Exception as e:  # retried, with backoff (HTTP 429 from the gateway)
            err = str(e)
            time.sleep(min(60, 5 * 2 ** attempt))
    return a["id"], b["id"], "error", err


pairs = list(itertools.combinations(invs, 2))
retry = "--retry-errors" in sys.argv
if retry:
    old = {(a, b): (a, b, rel, why) for a, b, rel, why in json.loads((outdir / "same_observation.json").read_text())["judge"]}
    redo = [(a, b) for a, b in pairs if old[(a["id"], b["id"])][2] == "error"]
    with ThreadPoolExecutor(4) as pool:
        for v in pool.map(judge, redo):
            old[(v[0], v[1])] = v
    verdicts = [old[(a["id"], b["id"])] for a, b in pairs]
    print(f"re-judged {len(redo)} pairs that had ended in an error")
else:
    with ThreadPoolExecutor(8) as pool:
        verdicts = list(pool.map(judge, pairs))
by_id = {i["id"]: i for i in invs}
res = {"run": str(run), "invariants": len(invs), "pairs": len(pairs), "exact_fact": exact_fact, "same_fact_set": same_set,
       "lexical_ge_0.4": sorted(lexical, reverse=True), "judge": verdicts}
outdir.mkdir(parents=True, exist_ok=True)
(outdir / "same_observation.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
from collections import Counter
cnt = Counter(v[2] for v in verdicts)
lines = ["# Same-observation check of the cross-consistent invariants", "",
         f"Cross-check run `{run}`: {len(invs)} cross-consistent invariants, {len(pairs)} pairs. Method in the script's docstring.", "",
         f"1. Exact: identical fact texts {len(exact_fact)}, identical fact sets {len(same_set)}.",
         f"2. Lexical (token Jaccard >= 0.4 between two facts): {len(lexical)} fact pairs.",
         f"3. Judge (GPT-5.6 Luna high, one call per pair): " + ", ".join(f"{k} {v}" for k, v in cnt.most_common()), ""]
flag = [v for v in verdicts if v[2] in ("same", "one_contains_other", "partial_overlap", "error")]
lines += ["## Pairs the judge did not call different", "", "| A | B | relation | reason | A's observation | B's observation |", "|---|---|---|---|---|---|"]
order = {"same": 0, "one_contains_other": 1, "partial_overlap": 2, "error": 3}
for a, b, rel, why in sorted(flag, key=lambda v: order[v[2]]):
    cl = lambda t: t.replace("|", "\\|").replace("\n", " ")  # noqa: E731
    lines.append(f"| {by_id[a]['local_id']} (`{by_id[a]['task']}`) | {by_id[b]['local_id']} (`{by_id[b]['task']}`) | **{rel}** | {cl(why)} | "
                 f"{cl(obs_text(by_id[a]))} | {cl(obs_text(by_id[b]))} |")
lines += ["", "## Lexically close fact pairs", "", "| Jaccard | A | B | A's fact | B's fact |", "|---|---|---|---|---|"]
for j, a, b, x, y in sorted(lexical, reverse=True):
    lines.append(f"| {j} | {by_id[a]['local_id']} (`{by_id[a]['task'][-8:]}`) | {by_id[b]['local_id']} (`{by_id[b]['task'][-8:]}`) | {x} | {y} |")
(outdir / "same_observation.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines[:9]))
for a, b, rel, why in sorted(flag, key=lambda v: order[v[2]]):
    print(f"  {rel:20s} {by_id[a]['task'][-8:]} {by_id[a]['local_id']} ~ {by_id[b]['task'][-8:]} {by_id[b]['local_id']}: {why}")
