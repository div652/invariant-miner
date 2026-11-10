"""One readable markdown digest per JobBench task of a run, for failure analysis.

    python3 benchmarks/jobbench/trace_digest.py RUN_DIR --out DIR [--grading grading] [--tasks ID ...]

Per task (DIR/<profession>__<taskN>.md):
- score, time, steps, subagent sessions;
- the prompt the agent got (prompt.txt), the task card (the designers' intent; never shown to the agent), the files the
  task expects the agent to find on the web (files_required_to_search; never staged);
- the rubric with the judge's verdict on every criterion (reasoning + evidence for each failed one);
- the deliverables in workspace/output (text extracted from docx/xlsx/pptx/pdf, cut);
- the trajectory: root session step by step (reasoning summary, text, tool calls with cut arguments and output), then
  each subagent session.
Text extraction uses the invariant plugin's extractor venv when present (DSH_BENCH_EXTRACTOR=<python> <script>).
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

EXTRACTOR = os.environ.get("DSH_BENCH_EXTRACTOR", str(Path.home() / "dsh-bench-harness-inv/plugins/invariants/.venv/bin/python")
                           + " " + str(Path.home() / "dsh-bench-harness-inv/plugins/invariants/extract_text.py")).split()
TEXT_EXT = {".md", ".txt", ".csv", ".json", ".py", ".html", ".xml", ".yaml", ".yml", ".tsv", ".sql", ".log", ".eml"}
DOC_EXT = {".docx", ".xlsx", ".xls", ".pptx", ".pdf", ".doc", ".xlsm"}


def cut(text, n: int) -> str:
    text = str(text)
    return text if len(text) <= n else text[:n] + f" …[+{len(text) - n} chars]"


def result_text(message: dict) -> tuple[str, bool]:
    out, err = [], False
    for c in message.get("content", []):
        err = err or bool(c.get("isError"))
        o = c.get("output", c.get("content", c.get("result", c)))
        if isinstance(o, dict):
            err = err or o.get("type") == "error-text"
            o = o.get("value", o)
        if isinstance(o, list):
            o = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in o)
        out.append(o if isinstance(o, str) else json.dumps(o))
    return "\n".join(out), err


def session_md(path: Path, arg_chars: int, out_chars: int) -> tuple[str, dict]:
    rows = []
    for line in open(path):
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    head = rows[0]
    results = {}
    for r in rows:
        if r.get("type") == "tool/result":
            m = r["data"]["message"]
            results[m.get("source", {}).get("callId")] = result_text(m)
    lines, stats = [], {"steps": 0, "calls": 0, "errors": 0}
    for r in rows:
        t, d = r.get("type"), r.get("data", {})
        if t == "user/message":
            text = "\n".join(c.get("text", "") for c in d.get("content", []) if isinstance(c, dict))
            if d.get("source", {}).get("kind") == "plugin" or text.startswith("Current runtime context"):
                continue
            lines.append(f"\n**user message:** {cut(text, 3000)}")
        elif t == "step/start":
            stats["steps"] += 1
            lines.append(f"\n#### step {d.get('step')}")
        elif t == "assistant/message":
            for c in d["message"]["content"]:
                if c["type"] == "reasoning" and c.get("text", "").strip():
                    lines.append(f"- *thinking:* {cut(' '.join(c['text'].split()), 400)}")
                elif c["type"] == "text" and c.get("text", "").strip():
                    lines.append(f"- **says:** {cut(c['text'].strip(), 1500)}")
        elif t == "tool/call":
            stats["calls"] += 1
            a = d.get("arguments")
            try:
                a = json.loads(a) if isinstance(a, str) else a
            except ValueError:
                a = {"raw": a}
            if d["name"] == "write":
                arg = f"{a.get('file_path')} ({len(str(a.get('content', '')))} chars): {cut(a.get('content', ''), 300)}"
            elif d["name"] == "bash":
                arg = cut(a.get("command", ""), arg_chars)
            else:
                arg = cut(json.dumps(a, ensure_ascii=False), arg_chars)
            res, err = results.get(d.get("callId"), ("(no result)", False))
            stats["errors"] += err
            lines.append(f"- **{d['name']}**{' ERROR' if err else ''}: `{arg}`\n  → {cut(' '.join(res.split()), out_chars)}")
    return "\n".join(lines), {**stats, "parent": head.get("parentSession"), "depth": head.get("delegationDepth", 0)}


def extract(path: Path, n: int) -> str:
    if path.suffix.lower() in TEXT_EXT:
        return cut(path.read_text(errors="replace"), n)
    if path.suffix.lower() in DOC_EXT and Path(EXTRACTOR[0]).exists():
        try:
            out = subprocess.run([*EXTRACTOR, str(path), str(n + 2000)], capture_output=True, text=True, timeout=120).stdout
            return cut(out, n) if out.strip() else "(no text extracted)"
        except subprocess.TimeoutExpired:
            return "(extraction timed out)"
    return "(binary; not extracted)"


def render(run: Path, task_dir: Path, grading: Path) -> str:
    spec = json.loads((task_dir / "spec.json").read_text())
    tid = spec["task_id"]
    gdir = grading / "dataset/main" / tid
    judge = next(gdir.glob("eval_result_*/eval_*/*_judge.json"), None)
    j = json.loads(judge.read_text()) if judge else None
    rj = json.loads((task_dir / "run.json").read_text()) if (task_dir / "run.json").exists() else {}
    sessions = sorted(task_dir.glob("dsh-home/sessions/**/session.v2.jsonl"))
    parts = []
    rendered = [(s, *session_md(s, 300, 250)) for s in sessions]
    root = [x for x in rendered if x[2]["depth"] == 0]
    subs = [x for x in rendered if x[2]["depth"] != 0]
    score = f"{j['total_score']}/{j['max_score']} = {j['total_score'] / j['max_score']:.3f}" if j else "not graded"
    parts.append(f"# {tid}\n\nScore (original rubrics): **{score}**; rubric items passed {j['passed_count']}/{j['total_count']}" if j else f"# {tid}\n\nScore: not graded")
    parts.append(f"Agent time {rj.get('agent_s', '?')} s; finish {rj.get('finish_reason', '?')}; root steps {root[0][2]['steps'] if root else '?'}; "
                 f"subagent sessions {len(subs)}")
    parts.append("\n## Prompt given to the agent\n\n" + cut((task_dir / "prompt.txt").read_text(), 9000))
    card = gdir / "task_card.md"
    if card.exists():
        parts.append("\n## Task card (designers' intent; NOT shown to the agent)\n\n" + cut(card.read_text(), 6000))
    req = gdir / "files_required_to_search"
    if req.exists():
        parts.append("\n## Files the task expects the agent to find on the web (not staged)\n\n" + "\n".join(f"- {p.name}" for p in sorted(req.iterdir())))
    staged = sorted(p.relative_to(task_dir / "workspace") for p in (task_dir / "workspace/task_folder").rglob("*") if p.is_file()) if (task_dir / "workspace/task_folder").exists() else []
    parts.append("\n## Staged input files (workspace/task_folder)\n\n" + "\n".join(f"- {p}" for p in staged[:80]))
    if j:
        parts.append("\n## Rubric and judge verdicts")
        for it in j["rubrics"]:
            res = it["result"]
            parts.append(f"\n### R{it['index']} [{'PASS' if res['passed'] else 'FAIL'}] weight {it['weight']}, score {res['score']}: {it['rubric']}")
            for c in res.get("criteria_results", []):
                if c["passed"]:
                    parts.append(f"- ✓ {c['criterion']}")
                else:
                    parts.append(f"- ✗ {c['criterion']}\n  - judge: {cut(c.get('reasoning', ''), 600)}\n  - evidence: {cut(c.get('evidence', ''), 400)}")
    out_dir = task_dir / "workspace/output"
    files = sorted(p for p in out_dir.rglob("*") if p.is_file()) if out_dir.exists() else []
    parts.append(f"\n## Deliverables (workspace/output: {len(files)} files)")
    budget = 24000
    for p in files:
        text = extract(p, max(1500, min(6000, budget // max(1, len(files)))))
        parts.append(f"\n### {p.relative_to(out_dir)} ({p.stat().st_size} bytes)\n```\n{text}\n```")
    ans = task_dir / "answer.json"
    if ans.exists():
        parts.append("\n## Final chat message\n\n" + cut(json.loads(ans.read_text()).get("answer", ""), 2000))
    parts.append("\n## Trajectory: root agent")
    for s, md, st in root:
        parts.append(f"({st['steps']} steps, {st['calls']} tool calls, {st['errors']} errors)\n{md}")
    for i, (s, md, st) in enumerate(subs, 1):
        parts.append(f"\n## Trajectory: subagent {i} ({st['steps']} steps, {st['calls']} tool calls, {st['errors']} errors)\n{md}")
    return "\n".join(parts) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--grading", default="grading")
    p.add_argument("--tasks", nargs="*")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for task_dir in sorted((args.run / "tasks").iterdir()):
        if not (task_dir / "spec.json").exists():
            continue
        tid = json.loads((task_dir / "spec.json").read_text())["task_id"]
        if args.tasks and tid not in args.tasks:
            continue
        text = render(args.run, task_dir, args.run / args.grading)
        (args.out / f"{task_dir.name}.md").write_text(text)
        print(f"{task_dir.name}: {len(text)} chars")


if __name__ == "__main__":
    main()
