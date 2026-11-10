"""Build the failure-analysis report of a JobBench run from the per-task JSON files the analysts wrote.

    python3 benchmarks/jobbench/failure_report.py ANALYSIS_DIR [--title TEXT] [--preamble FILE]

Reads ANALYSIS_DIR/tasks/*.json (format: benchmarks/jobbench/FAILURE_ANALYSIS.md) and, if present,
ANALYSIS_DIR/m_subtypes.json (each model-mistake item labelled omitted / wrong / instruction / depth). Writes
ANALYSIS_DIR/REPORT.md: class totals, model-mistake subtypes, a one-line table per task, then each task in full.
"""

import argparse
import collections
import json
from pathlib import Path

CLASSES = {"A": "Correct", "M": "Model mistake", "R": "Retrieval mistake", "L": "Logging/recording mistake",
           "I": "Insufficient information", "S": "Skipped part", "H": "Harness/environment", "G": "Grading problem"}
SUBTYPES = {"wrong": "wrong calculation, method, interpretation or conclusion",
            "omitted": "had the fact or finding but left it out, or wrote it generically",
            "depth": "skipped an analysis or check a professional would add (not asked explicitly)",
            "instruction": "did not follow an explicit instruction"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("analysis", type=Path)
    p.add_argument("--title", default="JobBench failure analysis")
    p.add_argument("--preamble", type=Path, help="markdown inserted after the title (run details, findings)")
    args = p.parse_args()
    rows = [json.loads(f.read_text()) for f in sorted((args.analysis / "tasks").glob("*.json"))]
    got = sum(int(r["score"].split("/")[0]) for r in rows)
    mx = sum(int(r["score"].split("/")[1]) for r in rows)
    lost = collections.Counter()
    for r in rows:
        lost.update({k: v for k, v in r["lost_weight_by_class"].items() if v})
    prim = collections.Counter(r["primary_class"] for r in rows)
    anyc = collections.Counter(c for r in rows for c, v in r["lost_weight_by_class"].items() if v)
    items = collections.Counter(i["class"] for r in rows for i in r["failed_items"])
    total_lost = sum(lost.values())
    out = [f"# {args.title}", ""]
    if args.preamble:
        out += [args.preamble.read_text().rstrip(), ""]
    out += [f"{len(rows)} tasks; {got}/{mx} rubric points (pooled {got / mx:.3f}); {total_lost} points lost, "
            f"{sum(items.values())} failed rubric items.", "",
            "## Where the points went", "",
            "| Class | Tasks (primary) | Tasks (any loss) | Failed items | Points lost | Share of lost |",
            "|---|---|---|---|---|---|"]
    for c in CLASSES:
        if c == "A" and not prim[c]:
            out.append(f"| A {CLASSES[c]} | 0 | - | - | - | - |")
            continue
        out.append(f"| {c} {CLASSES[c]} | {prim[c]} | {anyc[c]} | {items[c]} | {lost[c]} | {100 * lost[c] / total_lost:.1f}% |")
    sub_path = args.analysis / "m_subtypes.json"
    if sub_path.exists():
        subs = json.loads(sub_path.read_text())
        n, w = collections.Counter(s["subtype"] for s in subs), collections.Counter()
        for s in subs:
            w[s["subtype"]] += s["lost"]
        out += ["", "### Model mistakes by subtype", "", "| Subtype | Meaning | Items | Points lost |", "|---|---|---|---|"]
        for k in sorted(SUBTYPES, key=lambda k: -w[k]):
            out.append(f"| {k} | {SUBTYPES[k]} | {n[k]} | {w[k]} |")
    out += ["", "## Tasks at a glance", "", "| Task | Score | Primary | Secondary | Main reason |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["task"]):
        a, b = map(int, r["score"].split("/"))
        reason = r["what_went_wrong"].split(". ")[0].replace("|", "/")
        out.append(f"| {r['task']} | {a}/{b} ({a / b:.2f}) | {r['primary_class']} | {', '.join(r.get('secondary_classes') or []) or '-'} | {reason[:220]} |")
    out += ["", "## Task details"]
    for r in sorted(rows, key=lambda r: r["task"]):
        out += ["", f"### {r['task']}: {r['score']}, primary {r['primary_class']}"
                f"{' (secondary ' + ', '.join(r['secondary_classes']) + ')' if r.get('secondary_classes') else ''}, confidence {r.get('confidence', '?')}",
                "", f"**Task.** {r['goal']}", "", f"**Delivered.** {r['delivered']}", "", f"**What went wrong.** {r['what_went_wrong']}", ""]
        for i in r["failed_items"]:
            out.append(f"- {i['rubric']} ({i['class']}, -{i['lost']}/{i['weight']}): {i['why']}")
        if r.get("subagent_notes"):
            out += ["", f"*Subagents:* {r['subagent_notes']}"]
    (args.analysis / "REPORT.md").write_text("\n".join(out) + "\n")
    print(f"wrote {args.analysis / 'REPORT.md'}")


if __name__ == "__main__":
    main()
