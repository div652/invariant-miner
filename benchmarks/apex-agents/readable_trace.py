"""Readable traces of APEX-Agents runs: one markdown file per task, for reading what the agent did.

    python3 benchmarks/apex-agents/readable_trace.py RUN_DIR --out DIR (--tasks SLUG ... | --sample PASS,FAIL)
        [--split third:train] [--seed 20261110]

--sample 3,3 picks 3 all-pass and 3 failed tasks at random (seeded) from the split (default third:train, the train
tasks of both shared splits, so nothing read here is a test task), spread over the jobs: the i-th pick of each kind
comes from the i-th job in a seeded job order. Writes DIR/<slug>.md per task and DIR/README.md (an index).

Each file (format of the prime-lab analysis traces, plus diagrams):
- header: result, score, criteria met, time, model calls, tool calls;
- Overview: a Mermaid flowchart of the run (consecutive steps that used the same apps merged into one box; red border
  = a tool error or timeout in that box), a Mermaid pie of where the wall time went, and a table, one row per model
  call (step);
- the task prompt, the rubric (every criterion's verdict; the judge's reasoning for each failed one), the final answer;
- the trajectory, step by step: the model's reasoning summary, any text, each tool call with its arguments and (cut)
  output, todo-list updates.
"""

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from dsh_bench.splits import task_ids  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
SPLIT_FILES = {"split": "splits.json", "third": "splits-third.json"}
OUT_CHARS = 1500  # tool output shown per call
ARG_CHARS = 1200
APP_NAMES = {"filesystem": "Files", "sheets": "Sheets", "slides": "Slides", "docs": "Docs", "mail": "Mail",
             "calendar": "Calendar", "chat": "Chat", "pdf": "PDF", "code": "Code", "edgar": "EDGAR", "fmp": "FMP"}
DSH_FAMILY = {"bash": "shell", "read": "DSH files", "write": "DSH files", "edit": "DSH files", "glob": "DSH files",
              "grep": "DSH files", "read_image": "DSH files", "todo_write": "todo"}


def short_tool(name: str) -> tuple[str, str]:
    """(family, short name): mcp__world__sheets_server_read_tab -> (Sheets, read_tab); bash -> (shell, bash)."""
    if name.startswith("mcp__world__"):
        rest = name.removeprefix("mcp__world__")
        server, _, tool = rest.partition("_server_")
        if not tool:
            server, _, tool = rest.partition("_")
        return APP_NAMES.get(server, server.title()), tool
    return DSH_FAMILY.get(name, name), name


def clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + f"\n… [{len(text) - n:,} more chars]"


def fence(text: str, lang: str = "") -> str:
    ticks = "````" if "```" in text else "```"
    return f"{ticks}{lang}\n{text}\n{ticks}"


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
    error = error or text.lstrip().startswith(("Error", "Tool call timed out")) or "Tool call timed out" in text[:200]
    return text, error


TARGET_KEYS = ("file_path", "path", "file", "filename", "file_name", "document_path", "spreadsheet_path",
               "presentation_path", "tab_name", "sheet_name", "query", "pattern", "command")


def target(call: dict) -> str:
    """The short thing a call works on: a file's base name, a tab, a query (for the overview boxes)."""
    try:
        args = json.loads(call["args"]) if isinstance(call["args"], str) else call["args"]
    except json.JSONDecodeError:
        return ""
    if not isinstance(args, dict):
        return ""
    for wrapper in ("input", "request"):  # some world tools nest their arguments
        if isinstance(args.get(wrapper), dict):
            args = {**args[wrapper], **{k: v for k, v in args.items() if k != wrapper}}
    for key in TARGET_KEYS:
        value = args.get(key)
        if isinstance(value, str) and value.strip():
            value = " ".join(value.split())
            if key in ("file_path", "path", "file", "filename", "file_name", "document_path", "spreadsheet_path",
                       "presentation_path"):
                value = value.rstrip("/").rsplit("/", 1)[-1] or value
            return value if len(value) <= 38 else value[:37] + "…"
    return ""


def label(name: str) -> str:
    fam, tool = short_tool(name)
    return tool if fam in ("shell", "DSH files", "todo") else f"{fam} {tool}"


def mm(text: str) -> str:
    """Text safe inside a Mermaid quoted label."""
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;").replace("\n", " ")


def load_steps(session: Path) -> tuple[list[dict], dict]:
    steps, by_id, meta = [], {}, {"todos": []}
    cur = None
    for line in session.read_text().splitlines():
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


def families(step: dict) -> tuple[str, ...]:
    return tuple(sorted({short_tool(c["name"])[0] for c in step["calls"]})) or ("answer",)


def phases(steps: list[dict]) -> list[dict]:
    out = []
    for s in steps:
        fam = families(s)
        if out and out[-1]["fam"] == fam:
            out[-1]["steps"].append(s)
        else:
            out.append({"fam": fam, "steps": [s]})
    return out


def flowchart(steps: list[dict], grades: dict, answer_kind: str) -> str:
    lines = ["```mermaid", "flowchart TD"]
    lines.append('    T(["Task prompt"])')
    prev = "T"
    for i, ph in enumerate(phases(steps)):
        ss = ph["steps"]
        rng = f"Step {ss[0]['n']}" if len(ss) == 1 else f"Steps {ss[0]['n']}-{ss[-1]['n']}"
        calls = Counter(label(c["name"]) for s in ss for c in s["calls"])
        targets = list(dict.fromkeys(t for s in ss for c in s["calls"] if c["name"] != "todo_write"
                                     for t in [target(c)] if t))
        secs = sum(s["model_s"] + s["tools_s"] for s in ss)
        if not calls:
            body = "final answer" if ss[-1] is steps[-1] else "message only"
        else:
            shown = [f"{k} x{v}" if v > 1 else k for k, v in calls.most_common(4)]
            more = len(calls) - 4
            body = "<br/>".join(mm(x) for x in shown) + (f"<br/>+{more} more" if more > 0 else "")
            if targets:
                body += "<br/><i>" + mm(", ".join(targets[:3]) + (f" +{len(targets) - 3}" if len(targets) > 3 else "")) + "</i>"
        node = f"P{i}"
        lines.append(f'    {node}["<b>{rng}</b> · {secs / 60:.1f} min<br/>{body}"]')
        lines.append(f"    {prev} --> {node}")
        errors = sum(c["error"] for s in ss for c in s["calls"])
        cls = "err" if errors else ("dsh" if all(f in ("shell", "DSH files", "todo") for f in ph["fam"]) else
                                    ("ans" if ph["fam"] == ("answer",) else "world"))
        lines.append(f"    class {node} {cls}")
        prev = node
    met = sum(1 for c in grades["criteria"] if c.get("judge_grade") == "pass")
    verdict = "ALL PASS" if grades.get("all_pass") else "FAIL"
    lines.append(f'    R(["{verdict}: {met}/{len(grades["criteria"])} criteria · score {grades["score"]:.2f}<br/>'
                 f'{mm(answer_kind)}"])')
    lines.append(f"    {prev} --> R")
    lines.append(f"    class R {'pass' if grades.get('all_pass') else 'fail'}")
    lines += ["    classDef world fill:#e8f0fe,stroke:#4a6fa5,color:#111",
              "    classDef dsh fill:#f1f3f4,stroke:#777,color:#111",
              "    classDef ans fill:#fff8e1,stroke:#b58900,color:#111",
              "    classDef err fill:#e8f0fe,stroke:#c62828,stroke-width:3px,color:#111",
              "    classDef pass fill:#e6f4ea,stroke:#2e7d32,color:#111",
              "    classDef fail fill:#fce8e6,stroke:#c62828,color:#111", "```"]
    return "\n".join(lines)


def time_pie(steps: list[dict]) -> str:
    model = sum(s["model_s"] for s in steps)
    world = sum(s["tools_s"] for s in steps if any(c["name"].startswith("mcp__world__") for c in s["calls"]))
    dsh = sum(s["tools_s"] for s in steps) - world
    rows = [("Model (thinking + writing)", model), ("Waiting on world apps", world), ("DSH tools only", dsh)]
    return "\n".join(["```mermaid", "pie showData title Where the wall time went (seconds)"]
                     + [f'    "{k}" : {v:.0f}' for k, v in rows if v > 0.5] + ["```"])


def ist(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, IST).strftime("%H:%M:%S")


def render(task_dir: Path, run_name: str) -> tuple[str, dict]:
    run = json.loads((task_dir / "run.json").read_text())
    grades = json.loads((task_dir / "grading/grades.json").read_text())
    prompt = (task_dir / "agent/prompt.txt").read_text().strip()
    answer = json.loads((task_dir / "agent/answer.json").read_text())
    session = next((task_dir / "agent/dsh-home/sessions").rglob("session.v2.jsonl"))
    steps, meta = load_steps(session)
    calls = [c for s in steps for c in s["calls"]]
    world_calls = [c for c in calls if c["name"].startswith("mcp__world__")]
    met = sum(1 for c in grades["criteria"] if c.get("judge_grade") == "pass")
    total_s = (steps[-1]["end"] - steps[0]["start"]) / 1000 if steps else 0
    title = grades.get("task") or task_dir.name
    out = [f"# {title}: {run.get('domain')} · {run_name}", ""]
    out.append(f"Result: **{'all-pass' if grades.get('all_pass') else 'fail'}** {met}/{len(grades['criteria'])} "
               f"criteria · score {grades['score']:.2f} · {total_s / 60:.1f} min · {len(steps)} model calls · "
               f"{len(calls)} tool calls ({len(world_calls)} to world apps, {sum(c['error'] for c in calls)} errors "
               f"or timeouts) · ending `{run.get('finish_reason')}` · expected output `{run.get('expected_output')}`")
    out += ["", "## Overview", "", "How the run went: one box per stretch of steps that used the same apps (blue: world "
            "apps, grey: DSH's own tools, yellow: an answer with no tool call, red border: a tool error or timeout "
            "inside the box).", "", flowchart(steps, grades, f"ending: {run.get('finish_reason')}"), "",
            time_pie(steps), "", "One row per model call:", "",
            "| Step | Started (IST) | Model s | Tools s | Tool calls | Tools | Output chars |",
            "|---|---|---|---|---|---|---|"]
    for s in steps:
        tools = Counter(label(c["name"]) for c in s["calls"])
        tl = ", ".join(f"{k} x{v}" if v > 1 else k for k, v in tools.most_common()) or "(message only)"
        err = " ⚠" if any(c["error"] for c in s["calls"]) else ""
        chars = sum(len(c["out"]) for c in s["calls"])
        out.append(f"| {s['n']} | {ist(s['start'])} | {s['model_s']:.0f} | {s['tools_s']:.0f} | {len(s['calls'])} "
                   f"| {tl}{err} | {chars:,} |")
    out += ["", "## Task prompt", "", fence(prompt, "text"), "", "## Rubric", "",
            "| # | Criterion | Verdict |", "|---|---|---|"]
    for i, c in enumerate(grades["criteria"], 1):
        crit = " ".join(str(c.get("criteria", "")).split())
        out.append(f"| {i} | {crit.replace('|', '/')} | {'pass' if c.get('judge_grade') == 'pass' else '**FAIL**'} |")
    failed = [(i, c) for i, c in enumerate(grades["criteria"], 1) if c.get("judge_grade") != "pass"]
    if failed:
        out += ["", "Judge's reasoning for each failed criterion:"]
        for i, c in failed:
            out += ["", f"**Criterion {i}:** {' '.join(str(c.get('criteria', '')).split())}", "",
                    fence(str(c.get("rationale", "")).strip(), "text")]
    out += ["", "## Final answer", "", f"Source: `{answer.get('source')}`, ending `{answer.get('finish_reason')}`.", "",
            fence(clip(str(answer.get("answer", "")).strip(), 8000), "markdown"), "", "## Trajectory", ""]
    for s in steps:
        k = len(s["calls"])
        out += [f"### Step {s['n']}: {k} tool call{'s' if k != 1 else ''}", "",
                f"_Started {ist(s['start'])} IST · model {s['model_s']:.0f} s · tools {s['tools_s']:.0f} s_", ""]
        if s["reasoning"]:
            out += ["**Reasoning summary:**", "", fence("\n\n".join(r.strip() for r in s["reasoning"]), "text"), ""]
        if s["text"]:
            out += ["**Text:**", "", fence(clip("\n\n".join(s["text"]).strip(), 6000), "markdown"), ""]
        for c in s["calls"]:
            fam, name = short_tool(c["name"])
            try:
                args = json.dumps(json.loads(c["args"]), indent=1, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                args = str(c["args"])
            dt = f"{(c['end'] - c['start']) / 1000:.1f} s" if c["end"] else "no result"
            flag = " · **error/timeout**" if c["error"] else ""
            out += [f"**Call `{c['name']}`** ({fam} · {dt}{flag})", "", fence(clip(args, ARG_CHARS), "json"), "",
                    f"Output ({len(c['out']):,} chars):", "", fence(clip(c["out"].strip(), OUT_CHARS), "text"), ""]
        if s["todos"]:
            mark = {"completed": "[x]", "in_progress": "[~]", "pending": "[ ]"}
            out += ["**Todo list now:**", ""] + [f"- {mark.get(t.get('status'), '[?]')} {t.get('content')}"
                                                  for t in s["todos"]] + [""]
    info = {"slug": task_dir.name, "domain": run.get("domain"), "all_pass": bool(grades.get("all_pass")),
            "met": met, "n": len(grades["criteria"]), "score": grades["score"], "minutes": total_s / 60,
            "steps": len(steps), "calls": len(calls), "prompt": prompt,
            "failed": [" ".join(str(c.get("criteria", "")).split()) for _, c in failed]}
    return "\n".join(out) + "\n", info


def sample(run: Path, split: str, n_pass: int, n_fail: int, seed: int) -> list[str]:
    prefix, _, name = split.partition(":")
    pool = task_ids(HERE / SPLIT_FILES[prefix], name)
    rng = random.Random(seed)
    by = {}
    for slug in pool:
        g = run / "tasks" / slug / "grading/grades.json"
        if not g.exists():
            continue
        grades = json.loads(g.read_text())
        dom = json.loads((run / "tasks" / slug / "run.json").read_text()).get("domain")
        by.setdefault((bool(grades.get("all_pass")), dom), []).append(slug)
    jobs = sorted({d for _, d in by})
    rng.shuffle(jobs)
    picked = []
    for want, count in ((True, n_pass), (False, n_fail)):
        for i in range(count):
            cands = sorted(set(by.get((want, jobs[i % len(jobs)]), [])) - set(picked))
            picked.append(rng.choice(cands))
    return picked


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tasks", nargs="*")
    parser.add_argument("--sample", help="PASS,FAIL counts, e.g. 3,3")
    parser.add_argument("--split", default="third:train")
    parser.add_argument("--seed", type=int, default=20261110)
    args = parser.parse_args()
    run = args.run.resolve()
    slugs = args.tasks or sample(run, args.split, *map(int, args.sample.split(",")), args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    infos = []
    for slug in slugs:
        text, info = render(run / "tasks" / slug, run.name)
        (args.out / f"{slug}.md").write_text(text)
        infos.append(info)
        print(f"{slug}: {'pass' if info['all_pass'] else 'fail'} {info['met']}/{info['n']}, {info['steps']} steps")
    idx = [f"# Readable traces: {run.name}", "",
           f"{len(slugs)} tasks{' sampled with --sample ' + args.sample + ', split ' + args.split + ', seed ' + str(args.seed) if args.sample else ''}. "
           "Each file: overview diagrams and a step table, the task prompt, the rubric with the judge's reasoning "
           "for failed criteria, the final answer, then every step (reasoning summary, tool calls, outputs cut to "
           f"{OUT_CHARS:,} chars).", "",
           "| Task | Job | Result | Score | Steps | Min | Question (short) | Failed criteria |", "|---|---|---|---|---|---|---|---|"]
    for i in infos:
        q = " ".join(i["prompt"].split())
        q = q if len(q) <= 140 else q[:139] + "…"
        fails = "; ".join(f if len(f) <= 90 else f[:89] + "…" for f in i["failed"]) or "-"
        idx.append(f"| [{i['slug']}]({i['slug']}.md) | {i['domain']} | {'pass' if i['all_pass'] else 'fail'} "
                   f"{i['met']}/{i['n']} | {i['score']:.2f} | {i['steps']} | {i['minutes']:.0f} | "
                   f"{q.replace('|', '/')} | {fails.replace('|', '/')} |")
    idx += ["", "Regenerate:", "", "```bash",
            f"python3 benchmarks/apex-agents/readable_trace.py {args.run} --out {args.out} "
            + (f"--sample {args.sample} --split {args.split} --seed {args.seed}" if args.sample
               else "--tasks " + " ".join(slugs)), "```"]
    (args.out / "README.md").write_text("\n".join(idx) + "\n")


if __name__ == "__main__":
    main()
