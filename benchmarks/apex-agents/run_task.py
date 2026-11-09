"""Run one APEX-Agents 1.1 task with DSH as the agent, on Mercor's own 1.1 images (CHECKLIST.md).

    python3 benchmarks/apex-agents/run_task.py --task SLUG --out DIR [--tasks-dir DIR]
        [--endpoint cao | --model models/x.json] [--keep-world]

SLUG is a task directory of the Harbor Hub download (e.g. world-225-je-01-70449b2d). The steps are Harbor's, done here
(CHECKLIST.md, "How a task runs"):
  1. world: Mercor's world image for the task (digest from environment/docker-compose.yaml) with that file's mounts and
     environment, plus WORLD_CAPTURE_INITIAL_SNAPSHOT=1 (pitfall 3), network none, and two read-only additions:
     /opt/dsh-bench/lib (the MCP relay) and /opt/dsh-bench/bin (ripgrep, for DSH's glob/grep). The world seeds itself,
     starts its 9 apps behind its gateway and takes the "before" snapshot; it is ready when the compose healthcheck
     passes (run here with podman exec).
  2. DSH (launcher attach mode) works in /filesystem as run_shell's user (svc_stirrup_code_execution, umask 0002,
     run_shell's environment), with the world's 74 tools through the MCP relay (all offered on every step; one world
     call at a time; 60 s per call from when it reaches the world), Mercor's other limits (100 steps, 3 h, tool output
     200 lines / 32,768 characters, 60 s for DSH's own tools), no final_answer tool, and Mercor's 1.1 system prompt
     with the two changes in CHECKLIST.md. No subagents: the core turns them off for every benchmark.
  3. after DSH: leftover processes of that user are stopped (not the code-execution server), then Mercor's
     /app/tools/collect_world_snapshot.py takes the "after" snapshot (pitfall 3; retried up to 3 times).
  4. outputs in DIR: run.json (timings, finish reason, infra_error if a container step failed), agent/ (DSH's run),
     trajectory.json (ATIF, what Mercor's grader reads), world-logs/ (initial_snapshot.tar.gz, final_snapshot.tar.gz,
     boot.log), world.log (container output). The world container is removed (--keep-world keeps it).
"""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import tomllib
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.endpoints import load_local_env, model_for  # noqa: E402
from dsh_bench.launch import root_session  # noqa: E402

RUNTIME = "podman"
TASKS_DIR = Path(os.environ.get("APEX_AGENTS_11_TASKS", Path.home() / "apex-agents-1.1-hub/apex-agents-1-1"))
RG_DIR = REPO / "work/apex-agents/bin"  # setup.sh: static ripgrep
WORKSPACE = "/filesystem"
EXEC_USER = "svc_stirrup_code_execution"  # the user Mercor's run_shell runs as (setpriv in the task's mcp_config.json)
EXEC_UID = 22007
# run_shell's environment (stirrup_code_execution: _agent_command_env), read from a running world; ripgrep last on PATH.
RUN_SHELL_ENV = {
    "VIRTUAL_ENV": "/opt/agent-task-venv",
    "PATH": "/opt/agent-task-venv/bin:/app/.venv/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"
            ":/opt/dsh-bench/bin",
    "HOME": "/home/svc_stirrup_code_execution",
    "NODE_PATH": "/usr/local/lib/node_modules",
    "AGENT_TASK_VENV": "/opt/agent-task-venv",
    "APP_FS_ROOT": "/filesystem",
    "LC_CTYPE": "C.UTF-8",
}
# Mercor's limits (apex_loop_truncated_tools_agent v1.1 manifest: max_steps, timeout, max_output_*, tool_call_timeout).
MAX_STEPS, TIMEOUT_S = 100, 10800
# The 60 s per call applies to DSH's own tools here; world tools get it in the relay (container/mcp_relay.py), counted
# from when the call reaches the world, as Mercor's agent counts it (CHECKLIST.md, change 5).
TOOL_LIMITS = {"max_lines": 200, "max_chars": 32768, "timeout_s": 60, "timeout_exclude": ["mcp__world__*"]}
# Mercor's 1.1 system prompt (apex_loop_truncated_tools_agent.py, _AGENT_SYSTEM_PROMPTS) with two changes
# (CHECKLIST.md, decision 5): `code_exec` -> `run_shell` (pitfall 1: 1.1 has no code_exec tool), and the path sentence
# also names DSH's own file and shell tools, which see the world's files at /filesystem like run_shell.
SYSTEM_PROMPT = (
    "You are an agent that completes tasks independently. Use the tools provided to you to complete the task to the best "
    "of your ability. You should use the run_shell tool when needed, such as when calculating values. When calculating "
    "numbers, unless specified otherwise, use the exact values without rounding them.\n\n"
    "You must attempt to execute the task. You cannot ask for help or further clarification. You may wish to look at "
    "files for contextual information to help solve the tasks. This includes communication channels.\n\n"
    "You should not scattergun your answers. Scattergunning is when you provide alternate answers based on information "
    "that is not explicitly requested in the task prompt. If you do this, it will be marked wrong. Please note, "
    "providing answers to legitimately different cases that are explicitly requested by the prompt is NOT "
    "scattergunning. Respond to all parts of the task, but commit to answers instead of hedging.\n\n"
    "You do not have access to the internet. Do not try to look up the answer through requests, beautifulsoup, or any "
    "other packages. For every tool except the run_shell, bash, read, write, edit, read_image, glob and grep tools, you "
    "may assume that all relevant files are located under the root path /. For those tools, however, you must "
    "explicitly use /filesystem/ as the root path to locate all relevant files."
)
# Ends of a DSH run, as Mercor's loop grades them: a reply without tool calls (completed) and the step limit (its
# status "failed", still graded); the 3 h timeout is its status "error" (the trial errors, not graded: scores 0 here).
GRADED_ENDINGS = {"completed": "completed", "benchmark:max-steps": "failed"}
# Kill what the agent left running as EXEC_USER (background jobs), but not the code-execution server itself.
REAP_PY = r"""
import os, signal
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        if os.stat(f"/proc/{pid}").st_uid != %d:
            continue
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        continue
    if "/app/services/stirrup_code_execution/.venv/bin/python" in cmd:
        continue
    try:
        os.kill(int(pid), signal.SIGKILL)
        print(pid, cmd[:120])
    except OSError:
        pass
""" % EXEC_UID


class InfraError(RuntimeError):
    """A container step failed (not the agent): run_all retries the task in a fresh world."""


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(argv: list[str], timeout: float | None = None, input: bytes | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(argv, capture_output=True, timeout=timeout, input=input)
    if proc.returncode != 0:
        raise InfraError(f"{' '.join(argv[:4])} ... exit {proc.returncode}: {proc.stderr.decode(errors='replace')[-800:]}")
    return proc


def load_task(tasks_dir: Path, slug: str) -> dict:
    """A Hub task directory: metadata, instruction, the world service of its compose file, the verifier image."""
    d = tasks_dir / slug
    toml = tomllib.loads((d / "task.toml").read_text())
    compose = yaml.safe_load((d / "environment/docker-compose.yaml").read_text())
    verifier = re.search(r"^FROM\s+(\S+)", (d / "tests/Dockerfile").read_text(), re.M)
    if verifier is None:
        raise ValueError(f"{slug}: no FROM in tests/Dockerfile")
    return {"slug": slug, "dir": d, "meta": toml["metadata"], "toml": toml, "world": compose["services"]["world"],
            "verifier_image": verifier.group(1), "instruction": (d / "instruction.md").read_text()}


def world_argv(task: dict, name: str, logs: Path) -> list[str]:
    """`podman run` for the task's world service: its image, mounts and environment, then our additions."""
    service = task["world"]
    env_dir = task["dir"] / "environment"
    argv = [RUNTIME, "run", "-d", "--name", name, "--network=none"]
    for volume in service.get("volumes", []):
        source, target, *mode = volume.split(":")
        if source == "world_logs":  # the compose file's named volume; a host directory here, so the snapshots land on disk
            host = logs
        elif source.startswith("./"):
            host = (env_dir / source).resolve()
        else:
            raise ValueError(f"{task['slug']}: unexpected volume {volume!r}")
        argv += ["-v", ":".join([str(host), target, *mode])]
    for key, value in (service.get("environment") or {}).items():
        argv += ["-e", f"{key}={value}"]
    argv += ["-e", "WORLD_CAPTURE_INITIAL_SNAPSHOT=1",
             "-v", f"{HERE / 'container'}:/opt/dsh-bench/lib:ro", "-v", f"{RG_DIR}:/opt/dsh-bench/bin:ro"]
    return argv + [service["image"]]


def healthcheck(task: dict) -> list[str]:
    test = task["world"]["healthcheck"]["test"]
    if test[0] != "CMD":
        raise ValueError(f"{task['slug']}: healthcheck {test[0]} not supported")
    return test[1:]


def wait_ready(task: dict, container: str, timeout_s: float = 1500) -> float:
    """The compose healthcheck (seeded, apps up, initial snapshot taken, MCP answers), polled until it passes."""
    t0 = time.monotonic()
    check = healthcheck(task)
    while time.monotonic() - t0 < timeout_s:
        state = subprocess.run([RUNTIME, "inspect", "-f", "{{.State.Running}}", container], capture_output=True, text=True)
        if state.stdout.strip() != "true":
            logs = subprocess.run([RUNTIME, "logs", "--tail", "40", container], capture_output=True, text=True)
            raise InfraError(f"world exited during boot: {(logs.stdout + logs.stderr)[-1500:]}")
        if subprocess.run([RUNTIME, "exec", container, *check], capture_output=True).returncode == 0:
            return round(time.monotonic() - t0, 1)
        time.sleep(3)
    raise InfraError(f"world not ready after {timeout_s} s")


class SetupSlot:
    """At most N worlds booting at once (populate + snapshot are disk- and podman-heavy); a file lock per slot."""

    def __init__(self, lock_dir: Path | None, slots: int):
        self.lock_dir, self.slots, self.handle = lock_dir, slots, None

    def __enter__(self):
        if self.lock_dir is None:
            return self
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        while True:
            for i in range(self.slots):
                handle = open(self.lock_dir / f"slot-{i}.lock", "w")
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.handle = handle
                    return self
                except BlockingIOError:
                    handle.close()
            time.sleep(2)

    def __exit__(self, *exc):
        if self.handle is not None:
            fcntl.flock(self.handle, fcntl.LOCK_UN)
            self.handle.close()
            self.handle = None


def final_snapshot(container: str, attempts: int = 3) -> list[str]:
    """Mercor's collect hook script, run as root in the world (it signs the request with the world's root-only key)."""
    errors = []
    for _ in range(attempts):
        proc = subprocess.run([RUNTIME, "exec", "-w", "/app/tools", container, "python", "collect_world_snapshot.py"],
                              capture_output=True, text=True, timeout=1200)
        if proc.returncode == 0:
            return errors
        errors.append(f"exit {proc.returncode}: {(proc.stdout + proc.stderr)[-500:]}")
        time.sleep(5)
    raise InfraError(f"final snapshot failed {attempts} times: {errors[-1]}")


def _text(blocks) -> str:
    if isinstance(blocks, str):
        return blocks
    parts = []
    for block in blocks or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif block.get("type") == "tool-result":
            parts.append(_text(block.get("output", {}).get("value") if isinstance(block.get("output"), dict)
                               else block.get("content") or block.get("output")))
        elif block.get("type") == "image":
            parts.append("[image]")
    return "\n".join(p for p in parts if p)


def atif(prompt: str, home: Path, answer: dict, record: dict) -> dict:
    """DSH's root session as an ATIF trajectory (the shape Mercor's agent writes and its grader reads, tests/atif.py):
    system and task prompt, then one agent step per model reply with its tool calls and their results. The grader's
    answer is the last agent message with text, as for Mercor's agent."""
    steps = [{"step_id": 1, "source": "system", "message": SYSTEM_PROMPT},
             {"step_id": 2, "source": "user", "message": prompt}]
    session = root_session(home)
    events = session[1] if session else []
    by_call = {}
    for event in events:
        kind, data = event.get("type"), event.get("data") or {}
        if kind == "assistant/message":
            content = data.get("message", {}).get("content", [])
            step = {"step_id": len(steps) + 1, "source": "agent", "message": _text(content)}
            calls = [{"tool_call_id": b.get("id"), "function_name": b.get("name"),
                      "arguments": b.get("arguments") if isinstance(b.get("arguments"), dict) else
                      json.loads(b.get("arguments") or "{}") if isinstance(b.get("arguments"), str) else {}}
                     for b in content if b.get("type") == "tool-call"]
            if calls:
                step["tool_calls"] = calls
                step["observation"] = {"results": []}
                for call in calls:
                    by_call[call["tool_call_id"]] = step
            steps.append(step)
        elif kind == "tool/result":
            message = data.get("message", {})
            call_id = (message.get("source") or {}).get("callId")
            if call_id in by_call:
                by_call[call_id]["observation"]["results"].append(
                    {"source_call_id": call_id, "content": _text(message.get("content"))})
    finish = answer.get("finish_reason")
    return {"schema_version": "ATIF-v1.5", "session_id": answer.get("root_session_id") or "dsh",
            "agent": {"name": "dsh-bench-harness", "version": "1.1"}, "steps": steps,
            "final_metrics": {"total_steps": len(steps)},
            "extra": {"native_status": GRADED_ENDINGS.get(finish, "error"), "finish_reason": finish,
                      "time_elapsed_sec": record.get("agent_s", 0.0)}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tasks-dir", type=Path, default=TASKS_DIR)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--timeout-s", type=int, default=TIMEOUT_S)
    parser.add_argument("--lock-dir", type=Path, default=None)
    parser.add_argument("--setup-slots", type=int, default=4)
    parser.add_argument("--keep-world", action="store_true")
    args = parser.parse_args()
    load_local_env()
    if args.model and not args.model.startswith("{repo}"):
        # The launcher resolves a relative model path against the spec's directory (the task's out dir): make it
        # absolute here, against the current directory, and fail now if it does not exist.
        args.model = str(Path(args.model).resolve())
        if not Path(args.model).exists():
            raise SystemExit(f"--model {args.model}: no such file")
    if not (RG_DIR / "rg").exists():
        raise SystemExit(f"{RG_DIR / 'rg'} missing: run benchmarks/apex-agents/setup.sh")
    task = load_task(args.tasks_dir, args.task)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    logs = out / "world-logs"
    logs.mkdir()
    container = f"apex11-{args.task[:24]}-{uuid.uuid4().hex[:6]}"
    meta = task["meta"]
    record = {"task": args.task, "tasks_dir": str(args.tasks_dir.resolve()), "task_id": meta["task_id"], "world_id": meta["world_id"], "world": meta["world_slug"],
              "domain": meta["domain"], "expected_output": meta["expected_output"], "container": container,
              "world_image": task["world"]["image"], "verifier_image": task["verifier_image"], "started_at": now()}
    (out / "prompt.txt").write_text(task["instruction"])
    t0 = time.monotonic()
    try:
        with SetupSlot(args.lock_dir, args.setup_slots) as slot:
            record["slot_wait_s"] = round(time.monotonic() - t0, 1)
            sh(world_argv(task, container, logs), timeout=300)
            record["boot_s"] = wait_ready(task, container)
        record["setup_s"] = round(time.monotonic() - t0, 1)
        if not (logs / "initial_snapshot.tar.gz").exists():
            raise InfraError("world ready but no initial snapshot")

        spec = {
            "task_id": meta["task_id"],
            "prompt": task["instruction"],
            "model": model_for(args.endpoint, args.model),
            "system_prompt": SYSTEM_PROMPT,
            "system_prompt_mode": "append",
            "attach": {"container": container, "workspace": WORKSPACE, "user": EXEC_USER, "umask": "0002"},
            "runtime": RUNTIME,
            "container_env": RUN_SHELL_ENV,
            "disable": ["tool-web"],
            # The relay answers a call it stopped at its own limit; DSH's MCP client only stops a call that never
            # comes back (a world call can also wait for the one-at-a-time lock first).
            "mcp": [{"name": "world", "transport": "stdio", "command": RUNTIME,
                     "args": ["exec", "-i", container, "/app/.venv/bin/python", "/opt/dsh-bench/lib/mcp_relay.py"],
                     "toolCallTimeoutMs": (args.timeout_s + 600) * 1000}],
            "toolbelt": None,
            "final_answer": False,
            "tool_limits": TOOL_LIMITS,
            "limits": {"max_steps": args.max_steps, "timeout_s": args.timeout_s, "temperature": None},
            "meta": {"benchmark": "apex-agents", "task": args.task, "world": meta["world_slug"]},
        }
        (out / "agent-spec.json").write_text(json.dumps(spec, indent=2) + "\n")
        t1 = time.monotonic()
        record["agent_relaunches"] = 0
        for attempt in range(2):
            launch = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(out / "agent-spec.json"),
                                     "--out", str(out / "agent")], cwd=REPO, capture_output=True, text=True)
            (out / "launch.log").write_text(launch.stdout + launch.stderr)
            ended = json.loads((out / "agent/answer.json").read_text()).get("finish_reason") \
                if (out / "agent/answer.json").exists() else None
            # DSH started no agent (its MCP startup has 60 s; slow `podman exec` under load): the world is untouched,
            # so start DSH once more in it instead of redoing the task.
            if ended != "no_session" or attempt == 1:
                break
            (out / "agent").rename(out / f"agent-no-session-{attempt + 1}")
            record["agent_relaunches"] += 1
            wait_ready(task, container, timeout_s=300)
        record["agent_s"] = round(time.monotonic() - t1, 1)
        if not (out / "agent/answer.json").exists():  # the launcher failed before DSH ran (bad spec, model file, node)
            raise InfraError(f"DSH did not run: {(out / 'launch.log').read_text()[-1200:]}")
        answer = json.loads((out / "agent/answer.json").read_text())
        record["finish_reason"] = answer.get("finish_reason")
        record["graded_ending"] = record["finish_reason"] in GRADED_ENDINGS

        reaped = subprocess.run([RUNTIME, "exec", container, "python3", "-c", REAP_PY], capture_output=True, text=True)
        record["reaped_processes"] = [line for line in reaped.stdout.splitlines() if line.strip()]
        t2 = time.monotonic()
        record["snapshot_retries"] = final_snapshot(container)
        record["snapshot_s"] = round(time.monotonic() - t2, 1)
        home = out / "agent/dsh-home"
        (out / "trajectory.json").write_text(json.dumps(atif(task["instruction"], home, answer, record), indent=2) + "\n")
    except (InfraError, subprocess.TimeoutExpired) as error:
        record["infra_error"] = str(error)[-2000:]
    finally:
        world_log = subprocess.run([RUNTIME, "logs", container], capture_output=True, text=True)
        (out / "world.log").write_text(world_log.stdout + world_log.stderr)
        if not args.keep_world:
            subprocess.run([RUNTIME, "rm", "-f", "-t", "5", container], capture_output=True)
        record["finished_at"] = now()
        (out / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record.get(k) for k in ("task", "finish_reason", "setup_s", "agent_s", "infra_error")}))
    return 0 if "infra_error" not in record else 3


if __name__ == "__main__":
    sys.exit(main())
