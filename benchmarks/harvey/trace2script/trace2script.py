"""Turn one recorded agent trajectory (a DSH session) into a Python script that performs the same tool calls.

    python3 benchmarks/harvey/trace2script/trace2script.py RUN_DIR/tasks/<task> --out benchmarks/harvey/trace2script/scripts/<name>

Writes, into --out:
- mechanical.py  `async def solve(T)`: one block per agent step, in order. The step's reasoning summary and any text
                 the model wrote become comments; every tool call becomes `await T.<tool>(...)` with its exact
                 arguments (concurrency-safe calls of one step - read, glob, grep, read_image - run together in
                 `T.parallel(...)`, as DSH runs them; everything else runs one at a time, in call order). Results are
                 bound to `s<step>_<n>` so later code can use them. The recorded workspace path is replaced by the
                 marker WS_MARK, so the script runs in any fresh workspace.
- recorded.json  every call's id, tool, arguments and the output the model saw (paths marked the same way): the
                 reference for replay fidelity.
- meta.json      task id, source run and session, steps, calls, grade of the source run.

mechanical.py is the mechanical layer; solve.py, written from a copy of it, adds the semantic layer. Decisions the model made between calls are still hidden in the literals (a path
it chose to open, the answer it wrote); the semantic layer (see README.md) turns them into named functions.
"""

import argparse
import json
import textwrap
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsh_tools import CONCURRENCY_SAFE, WS_MARK  # noqa: E402

WRAP = 116


def lit(v, indent: int = 0) -> str:
    """A Python literal for v; long or multi-line strings as triple-quoted blocks."""
    pad = " " * indent
    if isinstance(v, str):
        if "\n" in v or len(v) > 90:
            body = v.replace("\\", "\\\\").replace("'''", "\\'\\'\\'")
            if body.endswith("'"):
                body = body[:-1] + "\\'"
            return "'''" + body + "'''"
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool) or v is None:
        return repr(v)
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, list):
        if not v:
            return "[]"
        inner = [lit(x, indent + 4) for x in v]
        one = "[" + ", ".join(inner) + "]"
        if len(one) <= 100 and "\n" not in one:
            return one
        return "[\n" + ",\n".join(pad + "    " + x for x in inner) + ",\n" + pad + "]"
    if isinstance(v, dict):
        items = [f"{json.dumps(k)}: {lit(x, indent + 4)}" for k, x in v.items()]
        one = "{" + ", ".join(items) + "}"
        if len(one) <= 100 and "\n" not in one:
            return one
        return "{\n" + ",\n".join(pad + "    " + x for x in items) + ",\n" + pad + "}"
    return repr(v)


def kwargs(args: dict, indent: int) -> str:
    return ", ".join(f"{k}={lit(v, indent)}" for k, v in args.items())


def comment(text: str, prefix: str, indent: int = 4) -> list[str]:
    pad = " " * indent
    out = []
    for para in text.strip().split("\n"):
        if not para.strip():
            out.append(f"{pad}#")
            continue
        for line in textwrap.wrap(para, WRAP - indent - len(prefix) - 2) or [""]:
            out.append(f"{pad}# {prefix}{line}")
            prefix = " " * len(prefix)
    return out


def mark(value, ws: str):
    if isinstance(value, str):
        return value.replace(ws, WS_MARK)
    if isinstance(value, list):
        return [mark(v, ws) for v in value]
    if isinstance(value, dict):
        return {k: mark(v, ws) for k, v in value.items()}
    return value


def parse_session(task_dir: Path) -> dict:
    session = next((task_dir / "dsh-home").rglob("session.v2.jsonl"))
    events = [json.loads(l) for l in session.read_text().split("\n") if l.strip()]
    steps: dict[int, dict] = {}
    step = 0
    calls: dict[str, dict] = {}
    prompt = None
    for e in events:
        t, d = e.get("type"), e.get("data", {})
        if t == "user/message" and prompt is None:
            content = d.get("message", {}).get("content")
            prompt = content if isinstance(content, str) else "".join(b.get("text", "") for b in content or [])
        if t == "step/start":
            step += 1
            steps.setdefault(step, {"reasoning": [], "text": [], "calls": []})
        elif t == "assistant/message":
            s = steps.setdefault(step, {"reasoning": [], "text": [], "calls": []})
            for b in d["message"]["content"]:
                if b.get("type") == "reasoning" and b.get("text"):
                    s["reasoning"].append(b["text"])
                elif b.get("type") == "text" and b.get("text", "").strip():
                    s["text"].append(b["text"])
        elif t == "tool/call":
            a = d.get("arguments")
            try:
                a = json.loads(a) if isinstance(a, str) else a
            except json.JSONDecodeError:
                a = {"_raw": a}
            c = {"name": d["name"], "args": a or {}, "output": None, "error": None}
            calls[d["callId"]] = c
            steps.setdefault(int(d["step"]), {"reasoning": [], "text": [], "calls": []})["calls"].append(c)
        elif t == "tool/result":
            for b in d["message"]["content"]:
                if b.get("type") == "tool-result" and b.get("toolCallId") in calls:
                    c = calls[b["toolCallId"]]
                    c["output"] = "".join(x.get("text", "") for x in b.get("content") or [] if isinstance(x, dict))
                    c["error"] = bool(b.get("isError"))
    return {"session": str(session), "prompt": prompt, "steps": steps}


def convert(task_dir: Path, out: Path) -> dict:
    spec = json.loads((task_dir / "spec.json").read_text())
    run = json.loads((task_dir / "run.json").read_text()) if (task_dir / "run.json").exists() else {}
    ws = str((task_dir / "workspace").resolve())
    parsed = parse_session(task_dir)
    grade = None
    g = task_dir.parent.parent / "grading/lab-root/results" / task_dir.name / "scores.json"
    if g.exists():
        s = json.loads(g.read_text())
        grade = {"all_pass": s["all_pass"], "n_passed": s["n_passed"], "n_criteria": s["n_criteria"]}
    task_id = spec["task_id"]
    recorded, lines = {}, []
    head = (f"{task_id}, run {task_dir.parent.parent.name}, as a script.\n\nGenerated by trace2script.py from\n"
            f"{parsed['session']}\n(regenerated by the converter: do not edit; the semantic layer is a copy, solve.py).\n\n"
            f"Source run: {run.get('root_steps', '?')} steps, {run.get('agent_s', '?')} s"
            + (f"; graded {grade['n_passed']}/{grade['n_criteria']}, all-pass {grade['all_pass']}" if grade else "")
            + ".\n\nTask prompt:\n\n" + textwrap.indent(spec["prompt"].strip(), "    "))
    lines += ['"""' + head.replace('"""', "'''") + '\n"""', "", f"TASK_ID = {json.dumps(task_id)}", "",
              "", "async def solve(T):"]
    n_calls = 0
    for step in sorted(parsed["steps"]):
        s = parsed["steps"][step]
        lines += ["", f"    # {'═' * 3} Step {step} {'═' * (WRAP - 18 - len(str(step)))}"]
        for r in s["reasoning"]:
            lines += comment(r, "reasoning: ")
        for t in s["text"]:
            lines += comment(t, "said: ")
        group: list[str] = []
        names: list[str] = []

        def flush():
            if not group:
                return
            if len(group) == 1:
                lines.append(f"    {names[0]} = await {group[0]}")
            else:
                lines.append(f"    {', '.join(names)} = await T.parallel(")
                lines.extend(f"        {g}," for g in group)
                lines.append("    )")
            group.clear()
            names.clear()

        for i, c in enumerate(s["calls"], 1):
            n_calls += 1
            cid = f"{step}.{i}"
            args = mark(c["args"], ws)
            recorded[cid] = {"tool": c["name"], "args": args, "error": c["error"], "output": mark(c["output"] or "", ws)}
            call = f"T.{c['name']}(_id={json.dumps(cid)}" + (", " + kwargs(args, 8) if args else "") + ")"
            var = f"s{step}_{i}"
            if c["name"] in CONCURRENCY_SAFE:
                group.append(call)
                names.append(var)
            else:
                flush()
                group.append(call)
                names.append(var)
                flush()
        flush()
    lines.append("")
    out.mkdir(parents=True, exist_ok=True)
    (out / "mechanical.py").write_text("\n".join(lines) + "\n")
    (out / "recorded.json").write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + "\n")
    meta = {"task_id": task_id, "source_task_dir": str(task_dir.resolve()), "session": parsed["session"],
            "recorded_workspace": ws, "steps": len(parsed["steps"]), "calls": n_calls, "grade": grade,
            "output_files": sorted(str(p.relative_to(task_dir / "workspace/output"))
                                   for p in (task_dir / "workspace/output").rglob("*") if p.is_file())}
    (out / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task_dir", type=Path, help="RUN_DIR/tasks/<task> of a finished run")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    meta = convert(args.task_dir.resolve(), args.out)
    compile((args.out / "mechanical.py").read_text(), str(args.out / "mechanical.py"), "exec")
    print(f"{meta['task_id']}: {meta['steps']} steps, {meta['calls']} calls -> {args.out}/mechanical.py")


if __name__ == "__main__":
    main()
