"""The job agent loop (TECHNICAL.md 3.1): call the model, run its tool calls, until `submit` is accepted.

The transcript keeps every model response in full (minus encrypted reasoning and signatures) and each tool result as
(tool, arguments, size, first 500 characters): tool results are deterministic given the trajectory and can be recomputed.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path

from .jobs import JobSpec
from .models import ModelError
from .tools import ToolBox, ToolError, parse_arguments

NUDGE = "Continue: use the tools to read the trajectory, then call submit with your answer. Every turn must call a tool."


@dataclass
class JobResult:
    ok: bool
    output: dict | None
    error: str | None
    steps: int
    tokens_in: int
    tokens_out: int
    started: float
    ended: float


def run_agent(spec: JobSpec, conv_factory, cfg: dict, job_dir: Path) -> JobResult:
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "input.json").write_text(json.dumps({"kind": spec.kind, "model": spec.model_key, "inputs": spec.inputs,
                                                    "trajectories": {k: t.id for k, t in spec.trajectories.items()},
                                                    "prompt_sha256": spec.prompt_sha256, "user_text": spec.user_text},
                                                   ensure_ascii=False, indent=1))
    toolbox = ToolBox(spec.trajectories, job_dir / "notes.md", spec.submit_schema, spec.submit_description)
    budget = int(cfg["budgets"].get(spec.kind, 40))
    model = cfg["models"][spec.model_key]
    guard = int(cfg["context_guard"] * model.get("prompt_window", 900_000))
    wall = cfg["wall_time_s"]
    wall = wall.get(spec.kind, wall.get("default", 1800)) if isinstance(wall, dict) else wall
    started = time.time()
    steps = invalid = tin = tout = 0

    def finish(ok, output=None, error=None):
        if ok:
            (job_dir / "output.json").write_text(json.dumps(output, ensure_ascii=False, indent=1))
        else:
            (job_dir / "error.txt").write_text(error or "")
        return JobResult(ok, output, error, steps, tin, tout, started, time.time())

    with open(job_dir / "transcript.jsonl", "a", encoding="utf-8") as tr:
        try:
            conv = conv_factory(spec, toolbox.definitions())
        except Exception as e:  # e.g. no key, SDK missing
            return finish(False, error=f"setup: {type(e).__name__}: {e}")
        while True:
            if steps >= budget:
                return finish(False, error=f"step budget ({budget}) used up without an accepted submit")
            if time.time() - started > wall:
                return finish(False, error=f"wall time ({wall} s) used up without an accepted submit")
            try:
                st = conv.step()
            except ModelError as e:
                return finish(False, error=f"model: {e}")
            except Exception as e:
                return finish(False, error=f"model: {type(e).__name__}: {e}")
            steps += 1
            tin += st.tokens_in
            tout += st.tokens_out
            record = {"step": steps, "time": time.time(), "response": st.raw, "results": []}
            if not st.calls:
                conv.add_user(NUDGE)
                record["nudge"] = True
                tr.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue
            results, submitted = [], None
            for call in st.calls:
                if call.name == "submit":
                    if submitted is not None:
                        results.append((call.id, "ignored: already submitted", True))
                        continue
                    if spec.require_full_read and (unread := toolbox.unread_steps()):
                        left = "; ".join(f"run {k}: steps {v}" for k, v in sorted(unread.items()))
                        results.append((call.id, f"submit refused: read every step of both runs with read_steps first. "
                                                 f"Not read yet: {left}.", True))
                        record["coverage_refused"] = left
                        continue
                    try:
                        args = parse_arguments(call.arguments)
                    except ValueError as e:
                        invalid += 1
                        results.append((call.id, f"submit rejected: arguments are not a JSON object: {e}", True))
                        continue
                    ok, err, norm = spec.validate(args)
                    if ok:
                        submitted = norm
                        results.append((call.id, "accepted", False))
                    else:
                        invalid += 1
                        results.append((call.id, f"submit rejected: {err}", True))
                    continue
                try:
                    args = parse_arguments(call.arguments)
                    results.append((call.id, toolbox.execute(call.name, args), False))
                except (ToolError, ValueError) as e:
                    results.append((call.id, f"error: {e}", True))
            for call, (_, text, err) in zip(st.calls, results):
                record["results"].append({"tool": call.name, "arguments": call.arguments if isinstance(call.arguments, dict) else str(call.arguments)[:2000],
                                          "chars": len(text), "error": err, "head": text[:500]})
            if submitted is not None:
                tr.write(json.dumps(record, ensure_ascii=False) + "\n")
                return finish(True, output=submitted)
            if invalid >= cfg["max_invalid_submits"]:
                tr.write(json.dumps(record, ensure_ascii=False) + "\n")
                return finish(False, error=f"{invalid} invalid submits; last: {results[-1][1]}")
            conv.add_results(results)
            if conv.est_tokens() > guard:
                record["elided"] = conv.elide(int(guard * 0.7))
            tr.write(json.dumps(record, ensure_ascii=False) + "\n")
