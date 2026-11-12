"""Readable traces of Harvey runs: the same tasks across several runs, one markdown file per task and run.

    python3 benchmarks/harvey/readable_trace.py --runs LABEL=RUN_DIR ... --tasks firm-knowledge/tasks/048 ... --out DIR

For tasks whose result differs between runs of one setup: DIR/README.md indexes every task with a criterion x run
verdict matrix (which criteria flip) and links to DIR/<NNN>-<label>.md, one file per task and run (the format of the
APEX-Agents traces, benchmarks/apex-agents/readable_trace.py):
- header: result, criteria met, time, model calls, tool calls, ending;
- Overview: a Mermaid flowchart of the run (consecutive steps that used the same kind of tool merged into one box; red
  border = a tool error or timeout in that box), a Mermaid pie of where the wall time went, a table per model call;
- the task prompt; the rubric (every criterion's verdict, the judge's reasoning for each); the delivered files
  (output/, response.md shown);
- the trajectory, step by step: reasoning summary, text, each tool call with its arguments and (cut) output.
Reads RUN_DIR/tasks/<task>/ (run.json, prompt.txt, dsh-home/sessions) and RUN_DIR/grading/lab-root/results/<task>/
(scores.json, output/). Pick the tasks from a train split.
"""

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
OUT_CHARS = 1500  # tool output shown per call
ARG_CHARS = 1200
FAMILY = {"bash": "shell", "run": "shell", "read": "files", "write": "files", "edit": "files", "glob": "search",
          "grep": "search", "survey": "search", "search": "search", "read_image": "files", "todo_write": "todo",
          "ledger": "ledger", "check_answer": "ledger"}


def clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + f"\n… [{len(text) - n:,} more chars]"


def fence(text: str, lang: str = "") -> str:
    ticks = "````" if "```" in text else "```"
    return f"{ticks}{lang}\n{text}\n{ticks}"


def mm(text: str) -> str:
    """Text safe inside a Mermaid quoted label."""
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;").replace("\n", " ")


def ist(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, IST).strftime("%m-%d %H:%M:%S")


def result_text(message: dict) -> tuple[str, bool]:
    parts, error = [], False
    for item in message.get("content", []):
        error = error or bool(item.get("isError"))
        inner = item.get("content", item.get("text", ""))
        if isinstance(inner, str):
            parts.append(inner)
        else:
            for c in inner:
                parts.append(c.get("text", f"[{c.get('type')}]"))
    text = "\n".join(parts)
    error = error or text.lstrip().startswith(("Error", "Tool call timed out")) or "timed out" in text[:200]
    return text, error


TARGET_KEYS = ("file_path", "path", "pattern", "query", "command", "terms")


def target(call: dict) -> str:
    """The short thing a call works on (a file's base name, a pattern, a command), for the overview boxes."""
    try:
        args = json.loads(call["args"]) if isinstance(call["args"], str) else call["args"]
    except json.JSONDecodeError:
        return ""
    if not isinstance(args, dict):
        return ""
    for key in TARGET_KEYS:
        value = args.get(key)
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        if isinstance(value, str) and value.strip():
            value = " ".join(value.split())
            if key in ("file_path", "path"):
                value = value.rstrip("/").rsplit("/", 1)[-1] or value
            return value if len(value) <= 38 else value[:37] + "…"
    return ""


def load_steps(session: Path) -> tuple[list[dict], dict]:
    steps, by_id, meta = [], {}, {}
    cur = None
    for line in session.read_text().split("\n"):
        if not line.strip():
            continue
        e = json.loads(line)
        t, d = e["type"], e.get("data", {})
        if t == "step/start":
            cur = {"n": len(steps) + 1, "start": e["time"], "model_done": None, "end": None, "reasoning": [],
                   "text": [], "calls": [], "todos": None}
            steps.append(cur)
        elif t == "assistant/message" and cur is not None:
            cur["model_done"] = e["time"]
            for c in d["message"]["content"]:
                if c["type"] == "reasoning" and c.get("text"):
                    cur["reasoning"].append(c["text"])
                elif c["type"] == "text" and c.get("text", "").strip():
                    cur["text"].append(c["text"])
        elif t == "tool/call" and cur is not None:
            call = {"id": d["callId"], "name": d["name"], "args": d.get("arguments", ""), "start": e["time"],
                    "end": None, "out": "", "error": False}
            cur["calls"].append(call)
            by_id[d["callId"]] = call
        elif t == "tool/result":
            call = by_id.get(d["message"]["source"].get("callId"))
            if call:
                call["end"] = e["time"]
                call["out"], call["error"] = result_text(d["message"])
        elif t == "todo/write" and cur is not None:
            cur["todos"] = d.get("todos")
        elif t == "step/end" and cur is not None:
            cur["end"] = e["time"]
        elif t == "turn/end":
            meta["turn_end"] = d.get("reason")
    for s in steps:
        s["model_done"] = s["model_done"] or s["end"] or s["start"]
        s["end"] = s["end"] or max([c["end"] or s["model_done"] for c in s["calls"]] + [s["model_done"]])
        s["model_s"] = (s["model_done"] - s["start"]) / 1000
        s["tools_s"] = (s["end"] - s["model_done"]) / 1000
    return steps, meta


def phases(steps: list[dict]) -> list[dict]:
    out = []
    for s in steps:
        fam = tuple(sorted({FAMILY.get(c["name"], c["name"]) for c in s["calls"]})) or ("answer",)
        if out and out[-1]["fam"] == fam:
            out[-1]["steps"].append(s)
        else:
            out.append({"fam": fam, "steps": [s]})
    return out


def flowchart(steps: list[dict], scores: dict) -> str:
    lines = ["```mermaid", "flowchart TD", '    T(["Task prompt"])']
    prev = "T"
    for i, ph in enumerate(phases(steps)):
        ss = ph["steps"]
        rng = f"Step {ss[0]['n']}" if len(ss) == 1 else f"Steps {ss[0]['n']}-{ss[-1]['n']}"
        calls = Counter(c["name"] for s in ss for c in s["calls"])
        targets = list(dict.fromkeys(t for s in ss for c in s["calls"] if c["name"] != "todo_write" for t in [target(c)] if t))
        secs = sum(s["model_s"] + s["tools_s"] for s in ss)
        if not calls:
            body = "final message" if ss[-1] is steps[-1] else "message only"
        else:
            shown = [f"{k} x{v}" if v > 1 else k for k, v in calls.most_common(4)]
            body = "<br/>".join(mm(x) for x in shown) + (f"<br/>+{len(calls) - 4} more" if len(calls) > 4 else "")
            if targets:
                body += "<br/><i>" + mm(", ".join(targets[:3]) + (f" +{len(targets) - 3}" if len(targets) > 3 else "")) + "</i>"
        node = f"P{i}"
        lines += [f'    {node}["<b>{rng}</b> · {secs / 60:.1f} min<br/>{body}"]', f"    {prev} --> {node}"]
        errors = sum(c["error"] for s in ss for c in s["calls"])
        cls = "err" if errors else ("write" if any(c["name"] in ("write", "edit") for s in ss for c in s["calls"])
                                    else "ans" if ph["fam"] == ("answer",) else "look")
        lines.append(f"    class {node} {cls}")
        prev = node
    verdict = "ALL PASS" if scores["all_pass"] else "FAIL"
    lines += [f'    R(["{verdict}: {scores["n_passed"]}/{scores["n_criteria"]} criteria"])', f"    {prev} --> R",
              f"    class R {'pass' if scores['all_pass'] else 'fail'}",
              "    classDef look fill:#e8f0fe,stroke:#4a6fa5,color:#111",
              "    classDef write fill:#f3e8fd,stroke:#7b1fa2,color:#111",
              "    classDef ans fill:#fff8e1,stroke:#b58900,color:#111",
              "    classDef err fill:#e8f0fe,stroke:#c62828,stroke-width:3px,color:#111",
              "    classDef pass fill:#e6f4ea,stroke:#2e7d32,color:#111",
              "    classDef fail fill:#fce8e6,stroke:#c62828,color:#111", "```"]
    return "\n".join(lines)


def time_pie(steps: list[dict]) -> str:
    rows = [("Model (thinking + writing)", sum(s["model_s"] for s in steps)), ("Tools", sum(s["tools_s"] for s in steps))]
    return "\n".join(["```mermaid", "pie showData title Where the wall time went (seconds)"]
                     + [f'    "{k}" : {v:.0f}' for k, v in rows if v > 0.5] + ["```"])


def render(run_dir: Path, label: str, task: str) -> tuple[str, dict]:
    name = task.replace("/", "__")
    tdir, gdir = run_dir / "tasks" / name, run_dir / "grading/lab-root/results" / name
    run = json.loads((tdir / "run.json").read_text())
    scores = json.loads((gdir / "scores.json").read_text())
    prompt = (tdir / "prompt.txt").read_text().strip()
    session = next(p for p in (tdir / "dsh-home/sessions").rglob("session.v2.jsonl")
                   if not json.loads(p.read_text().split("\n", 1)[0]).get("parentSession"))
    steps, meta = load_steps(session)
    calls = [c for s in steps for c in s["calls"]]
    total_s = (steps[-1]["end"] - steps[0]["start"]) / 1000 if steps else 0
    crit = scores["criteria_results"]
    out = [f"# {task} · {label} (`{run_dir.name}`)", "",
           f"Result: **{'all-pass' if scores['all_pass'] else 'fail'}** {scores['n_passed']}/{scores['n_criteria']} criteria · "
           f"{total_s / 60:.1f} min · {len(steps)} model calls · {len(calls)} tool calls "
           f"({sum(c['error'] for c in calls)} errors or timeouts) · ending `{run.get('finish_reason')}` · "
           f"started {ist(steps[0]['start']) if steps else '-'} IST", "",
           "## Overview", "", "One box per stretch of steps that used the same kind of tool (blue: looking/searching/"
           "reading, purple: writing or editing files, yellow: a message with no tool call, red border: a tool error or "
           "timeout inside the box).", "", flowchart(steps, scores), "", time_pie(steps), "", "One row per model call:", "",
           "| Step | Started (IST) | Model s | Tools s | Tool calls | Tools | Output chars |", "|---|---|---|---|---|---|---|"]
    for s in steps:
        tools = Counter(c["name"] for c in s["calls"])
        tl = ", ".join(f"{k} x{v}" if v > 1 else k for k, v in tools.most_common()) or "(message only)"
        err = " ⚠" if any(c["error"] for c in s["calls"]) else ""
        out.append(f"| {s['n']} | {ist(s['start'])[6:]} | {s['model_s']:.0f} | {s['tools_s']:.0f} | {len(s['calls'])} "
                   f"| {tl}{err} | {sum(len(c['out']) for c in s['calls']):,} |")
    out += ["", "## Task prompt", "", fence(prompt, "text"), "", "## Rubric", "",
            "| # | Criterion | Verdict |", "|---|---|---|"]
    for c in crit:
        out.append(f"| {c['id']} | {c['title'].replace('|', '/')} | {'pass' if c['verdict'] == 'pass' else '**FAIL**'} |")
    out += ["", "Judge's reasoning:"]
    for c in crit:
        out += ["", f"**{c['id']} ({c['verdict']}):** {c['title']}", "", fence(str(c.get("reasoning", "")).strip(), "text")]
    files = sorted(p for p in (gdir / "output").rglob("*") if p.is_file()) if (gdir / "output").is_dir() else []
    out += ["", "## Delivered files (output/)", ""]
    out += [f"- `{p.relative_to(gdir / 'output')}` ({p.stat().st_size:,} bytes)" for p in files] or ["(none)"]
    response = gdir / "output/response.md"
    if response.exists():
        out += ["", "`response.md`:", "", fence(clip(response.read_text(errors="replace").strip(), 10000), "markdown")]
    out += ["", "## Trajectory", ""]
    for s in steps:
        k = len(s["calls"])
        out += [f"### Step {s['n']}: {k} tool call{'s' if k != 1 else ''}", "",
                f"_Started {ist(s['start'])} IST · model {s['model_s']:.0f} s · tools {s['tools_s']:.0f} s_", ""]
        if s["reasoning"]:
            out += ["**Reasoning summary:**", "", fence("\n\n".join(r.strip() for r in s["reasoning"]), "text"), ""]
        if s["text"]:
            out += ["**Text:**", "", fence(clip("\n\n".join(s["text"]).strip(), 6000), "markdown"), ""]
        for c in s["calls"]:
            try:
                args = json.dumps(json.loads(c["args"]), indent=1, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                args = str(c["args"])
            dt = f"{(c['end'] - c['start']) / 1000:.1f} s" if c["end"] else "no result"
            flag = " · **error/timeout**" if c["error"] else ""
            out += [f"**Call `{c['name']}`** ({dt}{flag})", "", fence(clip(args, ARG_CHARS), "json"), "",
                    f"Output ({len(c['out']):,} chars):", "", fence(clip(c["out"].strip(), OUT_CHARS), "text"), ""]
        if s["todos"]:
            mark = {"completed": "[x]", "in_progress": "[~]", "pending": "[ ]"}
            out += ["**Todo list now:**", ""] + [f"- {mark.get(t.get('status'), '[?]')} {t.get('content')}" for t in s["todos"]] + [""]
    info = {"all_pass": bool(scores["all_pass"]), "met": scores["n_passed"], "n": scores["n_criteria"],
            "minutes": total_s / 60, "steps": len(steps), "calls": len(calls), "prompt": prompt,
            "verdicts": {c["id"]: (c["verdict"], c["title"]) for c in crit}, "finish": run.get("finish_reason")}
    return "\n".join(out) + "\n", info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", nargs="+", required=True, help="LABEL=RUN_DIR")
    parser.add_argument("--tasks", nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Readable traces")
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    runs = [(lab, Path(d).resolve()) for lab, _, d in (r.partition("=") for r in args.runs)]
    args.out.mkdir(parents=True, exist_ok=True)
    idx = [f"# {args.title}", "", args.note, "", "Runs: " + "; ".join(f"**{lab}** = `{d.name}`" for lab, d in runs), "",
           f"Each trace file: overview diagrams and a step table, the task prompt, the rubric with the judge's reasoning, "
           f"the delivered files, then every step (reasoning summary, tool calls, outputs cut to {OUT_CHARS:,} chars).", "",
           "| Task | " + " | ".join(lab for lab, _ in runs) + " | Question (short) |", "|---" * (len(runs) + 2) + "|"]
    sections = []
    for task in args.tasks:
        num = task.rsplit("/", 1)[-1]
        infos = []
        for lab, d in runs:
            text, info = render(d, lab, task)
            (args.out / f"{num}-{lab}.md").write_text(text)
            infos.append((lab, info))
            print(f"{task} {lab}: {'pass' if info['all_pass'] else 'fail'} {info['met']}/{info['n']}, {info['steps']} steps")
        q = " ".join(infos[0][1]["prompt"].split())
        q = q if len(q) <= 150 else q[:149] + "…"
        cells = [f"[{'**pass**' if i['all_pass'] else 'fail'} {i['met']}/{i['n']}]({num}-{lab}.md)<br/>{i['steps']} steps, "
                 f"{i['minutes']:.0f} min" for lab, i in infos]
        idx.append(f"| [{task}](#{num}) | " + " | ".join(cells) + f" | {q.replace('|', '/')} |")
        ids = list(infos[0][1]["verdicts"])
        flips = [c for c in ids if len({i["verdicts"].get(c, ("?",))[0] for _, i in infos}) > 1]
        sec = [f"### {num}", "", f"**{task}**: " + ", ".join(f"[{lab}]({num}-{lab}.md) {'pass' if i['all_pass'] else 'fail'} "
                                                           f"{i['met']}/{i['n']}" for lab, i in infos), "",
               "| Criterion | " + " | ".join(lab for lab, _ in infos) + " |", "|---" * (len(infos) + 1) + "|"]
        for c in ids:
            title = infos[0][1]["verdicts"][c][1].replace("|", "/")
            mark = " ⇄" if c in flips else ""
            sec.append(f"| {c} {title}{mark} | " + " | ".join("pass" if i["verdicts"].get(c, ("?",))[0] == "pass" else "**FAIL**"
                                                          for _, i in infos) + " |")
        sec += ["", f"Criteria that differ between runs (⇄): {', '.join(flips) or 'none'}.", ""]
        sections += sec
    idx += ["", "## Criterion verdicts per task", "", "⇄ marks a criterion whose verdict differs between runs.", ""] + sections
    idx += ["Regenerate:", "", "```bash", "python3 benchmarks/harvey/readable_trace.py --runs "
            + " ".join(f"{lab}={d}" for lab, d in runs) + f" --out {args.out} --tasks " + " ".join(args.tasks), "```"]
    (args.out / "README.md").write_text("\n".join(idx) + "\n")


if __name__ == "__main__":
    main()
