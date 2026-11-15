"""Check Harvey run traces for failures that are not the agent's legal work: harness components, deliverable paths,
and the grader's access to the deliverables.

    python3 benchmarks/harvey/check_traces.py RUN_DIR [RUN_DIR ...] [--examples 3] [--json out.json]

Per task (RUN_DIR/tasks/<task>/: session, run.json, answer.json, dsh.stderr, workspace/; RUN_DIR/grading*/):

A. Harness components
   spill-unreadable      read of a saved full result (/tmp/dsh-spill-...): outside the workspace, always denied
   tmp-unreadable        read of a /tmp file: bash wrote it inside the container, read runs on the host and sees
                         only the workspace, so the file is out of reach
   sandbox-denied        any other path refused as outside the workspace (e.g. a bash workdir outside it)
   container-failure     podman could not run a command (exit 125 / "Error: ..."), or the sandbox runner failed
   search-failure        glob/grep (ripgrep in the container) could not run
   grep-overflow         grep's raw ripgrep output passed DSH's 20 MB buffer: the call fails, nothing is shown
   search-timeout        glob/grep stopped by DSH's 30 s search timeout
   tool-timeout          a bash call hit its timeout
   parse-doc-failure     a traceback raised inside parse-doc (or the converters it runs)
   skill-script-failure  a traceback raised inside a skills/<name>/scripts/ script
   missing-command       "command not found" / "No module named" (anything the image lacks)
   read-only-write       "Read-only file system" / "Permission denied" (writing into documents/)
   skill-tool-error      the skill tool failed (unknown skill, ...)
   turn-error            the run ended on a provider / harness error (answer.json turn_end), or DSH logged an error
   rule:binary-read      DSH's read refused an office / binary file ("binary file": read opens text only) - a rule
   rule:read-before-edit edit / write refused a file not read first (DSH's fs-observation-policy) - a rule
B. Deliverable paths
   deliverable-path-miss read / edit / write of a deliverable name that resolved outside output/ and failed
   deliverable-outside   a file named like a deliverable left outside output/ at the end
   output-subfolder      a file in a subfolder of output/ (the grader looks up deliverables by bare file name)
   deliverable-missing   an expected deliverable (task.json) absent from output/ under its exact name
C. Grader
   grading-error         a criterion graded "error" (unreadable deliverable or failed judge call)
   judge-file-not-found  the judge was shown "(File not found: ...)" or "(No agent output found)"
   symlink-skipped       an output file not copied to the grader because it was a symlink
Agent-side tool errors that are none of these (wrong path, edit miss, ...) are counted as "other tool errors".
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

LAB = Path(__file__).resolve().parents[2] / "work/harvey-labs/tasks"
ABS_OUT = re.compile(r"/workspace/output/")


def deliverables(task_id: str) -> list[str]:
    t = json.loads((LAB / task_id / "task.json").read_text())
    d = t.get("deliverables")
    names = list(d.values()) if isinstance(d, dict) else list(d or [])
    if not names:
        names = sorted({x for c in t["criteria"] for x in c.get("deliverables") or []})
    return [str(n) for n in names]


def session_calls(task_dir: Path):
    f = next((task_dir / "dsh-home").rglob("session.v2.jsonl"), None)
    if f is None:
        return []
    calls, order = {}, []
    for line in f.read_text().split("\n"):
        if not line.strip():
            continue
        e = json.loads(line)
        d = e.get("data", {})
        if e["type"] == "tool/call":
            a = d.get("arguments")
            try:
                a = json.loads(a) if isinstance(a, str) else a
            except json.JSONDecodeError:
                a = {}
            calls[d["callId"]] = {"step": int(d["step"]), "name": d["name"], "args": a or {}, "out": "", "err": False}
            order.append(d["callId"])
        elif e["type"] == "tool/result":
            for b in d["message"]["content"]:
                if b.get("type") == "tool-result" and b.get("toolCallId") in calls:
                    c = calls[b["toolCallId"]]
                    c["out"] = "".join(x.get("text", "") for x in b.get("content") or [] if isinstance(x, dict))
                    c["err"] = bool(b.get("isError"))
    return [calls[i] for i in order]


def classify_call(c: dict, dnames: set[str]) -> list[str]:
    name, a, out = c["name"], c["args"], c["out"] or ""
    cmd = a.get("command", "") if isinstance(a, dict) else ""
    path = (a.get("file_path") or a.get("path") or "") if isinstance(a, dict) else ""
    found = []
    if name == "read" and "/dsh-spill-" in path:
        return ["A:spill-unreadable"]
    if name == "read" and path.startswith("/tmp/") and "[sandbox: file access denied" in out:
        return ["A:tmp-unreadable"]
    if "[sandbox: file access denied" in out:
        found.append("A:sandbox-denied")
    if "[sandbox: the sandbox runner itself failed" in out or ("[exit code: 125]" in out and re.search(r"(?m)^Error: ", out)):
        found.append("A:container-failure")
    if name in ("glob", "grep") and c["err"] and re.search(r"ripgrep launch failed|could not start its search|subprocess failed before", out):
        found.append("A:search-failure")
    if name in ("glob", "grep") and c["err"] and "more raw output than the subprocess seam retained" in out:
        found.append("A:grep-overflow")
    if name in ("glob", "grep") and c["err"] and "tool call timed out after" in out:
        found.append("A:search-timeout")
    if name == "bash" and "[timed out after" in out:
        found.append("A:tool-timeout")
    frames = re.findall(r'File "([^"]+)", line \d+', out)
    if name == "bash" and frames and any(re.search(r"parse-doc|markitdown|/docx2|pandoc", f) for f in frames):
        found.append("A:parse-doc-failure")
    if name == "bash" and frames and any("/skills/" in f for f in frames):
        found.append("A:skill-script-failure")
    missing = [m for m in re.findall(r"(?:bash: line \d+: |^)([\w+-]+): command not found", out, re.M) if "." not in m]
    if missing or "No module named" in out:
        found.append("A:missing-command")
    if re.search(r"Read-only file system|Permission denied", out):
        found.append("A:read-only-write")
    if name == "skill" and c["err"]:
        found.append("A:skill-tool-error")
    if c["err"] and re.search(r": binary file$", out.strip()):
        found.append("A:rule:binary-read")
    if c["err"] and "file has not been read" in out:
        found.append("A:rule:read-before-edit")
    base = Path(path).name if path else ""
    if name in ("read", "edit", "write") and c["err"] and base in dnames and "/output/" not in out + path \
            and not path.startswith("output/"):
        found.append("B:deliverable-path-miss")
    if not found and c["err"]:
        found.append("other tool errors")
    return found


def check_task(task_dir: Path, grading_dirs: list[Path]) -> dict:
    spec = json.loads((task_dir / "spec.json").read_text())
    task_id = spec["task_id"]
    dnames = set(deliverables(task_id))
    issues = defaultdict(list)
    for c in session_calls(task_dir):
        for cat in classify_call(c, dnames):
            issues[cat].append(f"step {c['step']} {c['name']}: " + re.sub(r"\s+", " ", (c["out"] or "")[:160]))
    ans = json.loads((task_dir / "answer.json").read_text()) if (task_dir / "answer.json").exists() else {}
    end = ans.get("turn_end") or {}
    if ans.get("finish_reason") not in ("completed", "final_answer", None) or end.get("kind") == "error":
        issues["A:turn-error"].append(f"finish {ans.get('finish_reason')}: {json.dumps(end)[:200]}")
    stderr = task_dir / "dsh.stderr"
    if stderr.exists():
        for line in stderr.read_text(errors="replace").splitlines():
            if re.match(r"dsh: (error|warn|fatal)|Error:|TypeError|ReferenceError|UnhandledPromise", line) and "reasoning" not in line:
                issues["A:turn-error"].append("dsh.stderr: " + line[:200])
    ws = task_dir / "workspace"
    out_dir = ws / "output"
    if out_dir.exists():
        for f in out_dir.rglob("*"):
            if f.is_file() and f.parent != out_dir:
                issues["B:output-subfolder"].append(str(f.relative_to(ws)))
        present = {f.name for f in out_dir.iterdir() if f.is_file()}
        for d in sorted(dnames):
            if d not in present:
                issues["B:deliverable-missing"].append(f"{d} (output/ has: {', '.join(sorted(present))[:150] or 'nothing'})")
    run = json.loads((task_dir / "run.json").read_text()) if (task_dir / "run.json").exists() else {}
    for ch in run.get("changed_files") or []:
        p = ch["path"]
        if Path(p).name in dnames and not p.startswith("output/"):
            issues["B:deliverable-outside"].append(p)
    for g in grading_dirs:
        sc = g / "lab-root/results" / task_dir.name / "scores.json"
        if not sc.exists():
            continue
        s = json.loads(sc.read_text())
        for c in s.get("criteria_results", []):
            if c["verdict"] == "error":
                issues["C:grading-error"].append(f"{c['id']}: {c.get('reasoning', '')[:160]}")
            if re.search(r"File not found:|No agent output found", c.get("reasoning", "")):
                issues["C:judge-file-not-found"].append(f"{c['id']}: {c['reasoning'][:160]}")
        break
    for g in grading_dirs:
        scores = g / "scores.json"
        if scores.exists():
            for row in json.loads(scores.read_text()).get("tasks", []):
                if row.get("task") == task_id and row.get("skipped_symlinks"):
                    issues["C:symlink-skipped"].append(", ".join(row["skipped_symlinks"])[:200])
    return {"task": task_id, "issues": dict(issues)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--examples", type=int, default=3)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = {}
    for run in args.runs:
        grading = sorted(run.glob("grading-*")) + [run / "grading"]   # single-task re-gradings first
        tasks = [check_task(t, grading) for t in sorted((run / "tasks").iterdir()) if (t / "spec.json").exists()]
        report[str(run)] = tasks
        cats = Counter()
        tasks_with = Counter()
        for t in tasks:
            for k, v in t["issues"].items():
                cats[k] += len(v)
                tasks_with[k] += 1
        print(f"\n== {run.name}: {len(tasks)} tasks")
        for k in sorted(cats, key=lambda k: (k[0] if k[0] in "ABC" else "Z", k)):
            print(f"   {k:28s} {cats[k]:5d} events in {tasks_with[k]:3d} tasks")
            if args.examples and not k.startswith("other"):
                shown = 0
                for t in tasks:
                    for ex in t["issues"].get(k, [])[:1]:
                        if shown < args.examples:
                            print(f"        {t['task']}: {ex[:170]}")
                            shown += 1
        if not cats:
            print("   no issues found")
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
