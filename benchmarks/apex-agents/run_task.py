"""Run one APEX-Agents task: Archipelago's environment as Mercor built it, DSH in place of Archipelago's agent.

    python3 benchmarks/apex-agents/run_task.py --task <task_id> --out runs/<run>/<task_id> \
        [--dataset ~/apex-agents-data] [--endpoint cao | --model models/x.json]

Steps (CHECKLIST.md has the decisions; Archipelago's examples/hugging_face_task/main.py is the reference flow):
  1. start the environment container (image dsh-bench-apex-agents, Archipelago's gateway on :8080 inside), network
     none, or internet for worlds with Edgar SEC / FMP;
  2. populate it through Archipelago's /data/populate: the world zip's filesystem/ and .apps_data/, then the task's
     input files (the example's order);
  3. start the world's apps once over HTTP (container/start_apps.py; change 1) and point the gateway at them (/apps);
  4. snapshot "before" (Archipelago's /data/snapshot, after the task's input files are in; change 4);
  5. run DSH with dsh_bench.launch in attach mode: workspace /filesystem, the gateway as MCP server "apps" through
     container/mcp_bridge.py, toolbelt on, web tools off, the paper's system prompt (path sentence extended);
  6. snapshot "after", keep the apps' logs, remove the container; write trajectory.json for Archipelago's grader.

Outputs in --out: task.json, snapshots/{before,after}.tar.gz, agent/ (the launcher's run dir: answer.json, sessions,
run.json), trajectory.json, apps-logs/, run.json. Grade with grade.py.
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from dsh_bench.endpoints import ENDPOINTS, load_local_env, model_for, setting_path  # noqa: E402

IMAGE = "dsh-bench-apex-agents:f8e41cb"
ARCHIPELAGO = REPO / "work/archipelago"
EXAMPLE_MCP_CONFIG = ARCHIPELAGO / "examples/hugging_face_task/mcp_config_all_oss_servers.json"
WORKSPACE = "/filesystem"
SUBSYSTEMS = ["filesystem", ".apps_data"]
RUNTIME = os.environ.get("RUNTIME", "podman")

# world_descriptions.json service names -> Archipelago's server names (examples/hugging_face_task).
APP_SERVERS = {"Calendar": "calendar_server", "Chat": "chat_server", "Code Execution": "code_execution_server",
               "Excel": "sheets_server", "Filesystem": "filesystem_server", "Mail": "mail_server",
               "PDFs": "pdf_server", "Powerpoint": "slides_server", "Word": "docs_server",
               "Edgar SEC": "edgar_sec", "FMP": "fmp_server"}
# Individual tools (the paper's): USE_INDIVIDUAL_TOOLS for the 9 apps, GUI_ENABLED for Edgar SEC and FMP (change 3).
INDIVIDUAL_TOOLS_ENV = {"edgar_sec": {"GUI_ENABLED": "true"}, "fmp_server": {"GUI_ENABLED": "true"}}
DEFAULT_INDIVIDUAL_ENV = {"USE_INDIVIDUAL_TOOLS": "true"}
NETWORKED_APPS = {"edgar_sec", "fmp_server"}

# DSH's bash runs under the same sandbox as code_exec (answer 5a): code_exec's build_sandbox_env() for its default mode.
CODE_EXEC_MIRROR = "/usr/local/lib/code_execution"
SANDBOX_ENV = {
    "LD_PRELOAD": "/app/lib/sandbox_fs.so",
    "SANDBOX_BLOCKED_PATHS": "/app:/.apps_data:/proc:/sys",
    "PATH": f"{CODE_EXEC_MIRROR}/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin",
    "PYTHONPATH": CODE_EXEC_MIRROR,
    "NODE_PATH": f"{CODE_EXEC_MIRROR}/node_modules",
    "HOME": "/tmp",
    "PYTHONUSERBASE": "/tmp",
    "SANDBOX_EXEC_REDIRECTS": f"/usr/lib/libreoffice/program/oosplash={CODE_EXEC_MIRROR}/bin/soffice",
}

# The paper's system prompt (Appendix D.2; Archipelago's react_toolbelt_agent README), verbatim except the path
# sentence, which also names DSH's tools (approved 2026-11-06).
SYSTEM_PROMPT = (
    "You are an agent that completes tasks independently. Use the tools provided to you to complete the task to the "
    "best of your ability. You should use the code_exec tool when needed, such as when calculating values. When "
    "calculating numbers, unless specified otherwise, use the exact values without rounding them. You must attempt to "
    "execute the task. You cannot ask for help or further clarification. For every tool except the code_exec, bash, "
    "read, write, edit, read_image, glob and grep tools, you may assume that all relevant files are located under the "
    "root path /. For those tools, however, you must explicitly use /filesystem/ as the root path to locate all "
    "relevant files."
)


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(argv, check=True, capture_output=True, **kwargs)


def in_container(container: str, *argv: str, input: bytes | None = None) -> bytes:
    return sh([RUNTIME, "exec", *(["-i"] if input is not None else []), container, *argv], input=input).stdout


def load_task(dataset: Path, task_id: str) -> tuple[dict, dict]:
    tasks = json.loads((dataset / "tasks_and_rubrics.json").read_text())
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if task is None:
        raise SystemExit(f"no task {task_id} in {dataset}")
    world = next(w for w in json.loads((dataset / "world_descriptions.json").read_text())
                 if w["world_id"] == task["world_id"])
    return task, world


def tar_subsystems(root: Path, label: str, into: Path) -> list[tuple[str, Path]]:
    """One tar.gz per non-empty subsystem directory of root (as the example's populate_subsystems)."""
    archives = []
    for subsystem in SUBSYSTEMS:
        directory = root / subsystem
        entries = sorted(directory.rglob("*")) if directory.is_dir() else []
        if not entries:
            continue
        archive = into / f"{label}_{subsystem.lstrip('.')}.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.dereference = True
            for entry in entries:
                tar.add(entry, arcname=str(entry.relative_to(directory)), recursive=False)
        archives.append((subsystem, archive))
    return archives


def populate(container: str, archives: list[tuple[str, Path]]) -> list[dict]:
    results = []
    for subsystem, archive in archives:
        target = f"/tmp/populate-{archive.name}"
        sh([RUNTIME, "cp", str(archive), f"{container}:{target}"])
        reply = in_container(container, "curl", "-sS", "--fail-with-body", "-F", f"archive=@{target}",
                             f"http://127.0.0.1:8080/data/populate?subsystem={subsystem}")
        in_container(container, "rm", "-f", target)
        results.append({"archive": archive.name, "subsystem": subsystem, "reply": json.loads(reply)})
    return results


def server_specs(apps: list[str]) -> dict:
    example = json.loads(EXAMPLE_MCP_CONFIG.read_text())["mcpServers"]
    servers = {}
    for port, name in enumerate(apps, start=5001):
        base = example[name]
        env = dict(base.get("env", {})) | INDIVIDUAL_TOOLS_ENV.get(name, DEFAULT_INDIVIDUAL_ENV)
        if name == "edgar_sec":
            agent = os.environ.get("DSH_BENCH_EDGAR_USER_AGENT", "")
            if not agent:
                raise SystemExit("Edgar SEC needs DSH_BENCH_EDGAR_USER_AGENT in your local.env (SEC asks for "
                                 "'<name> <contact email>')")
            env["EDGAR_USER_AGENT"] = agent
        servers[name] = {"cwd": base["cwd"], "command": base["command"], "args": base["args"], "env": env,
                         "port": port}
    return servers


def snapshot(container: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(in_container(container, "curl", "-sS", "--fail-with-body", "-X", "POST",
                                  "http://127.0.0.1:8080/data/snapshot"))


def wait_healthy(container: str, timeout_s: float = 120) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if subprocess.run([RUNTIME, "exec", container, "curl", "-sf", "http://127.0.0.1:8080/health"],
                          capture_output=True).returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("environment container did not become healthy")


def trajectory(prompt: str, answer: dict) -> dict:
    """Archipelago's AgentTrajectoryOutput: the grader reads the first user message (task prompt) and the last
    message's content (the final answer). One user message keeps the grader's single-turn path, as in the paper (the
    judge sees prompt, final answer and file changes, not the trajectory)."""
    status = "completed" if answer.get("finish_reason") == "final_answer" else "failed"
    return {"messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": prompt},
                         {"role": "assistant", "content": answer.get("answer") or ""}],
            "status": status, "time_elapsed": 0.0, "output": {"source": "dsh-bench-harness",
                                                              "finish_reason": answer.get("finish_reason")}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("~/apex-agents-data"))
    parser.add_argument("--endpoint", choices=sorted(ENDPOINTS))
    parser.add_argument("--model")
    parser.add_argument("--max-steps", type=int, default=250)
    parser.add_argument("--timeout-s", type=int, default=10800)
    parser.add_argument("--keep-container", action="store_true")
    args = parser.parse_args()
    load_local_env()
    dataset = args.dataset.expanduser().resolve()
    task, world = load_task(dataset, args.task)
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; every run needs a new directory")
    out.mkdir(parents=True)
    (out / "task.json").write_text(json.dumps(task | {"world": world}, indent=2) + "\n")

    apps = [APP_SERVERS[a["service_name"]] for a in world["apps"]]
    networked = bool(NETWORKED_APPS & set(apps))
    container = f"apex-{task['task_id'][5:13]}-{uuid.uuid4().hex[:6]}"
    record = {"task_id": task["task_id"], "world_id": world["world_id"], "world": world["world_name"],
              "domain": task["domain"], "expected_output": task["expected_output"], "apps": apps,
              "network": "pasta" if networked else "none", "container": container, "image": IMAGE,
              "started_at": now()}
    t0 = time.monotonic()
    try:
        sh([RUNTIME, "run", "-d", "--name", container, f"--network={record['network']}",
            "-v", f"{HERE / 'container'}:/opt/dsh-bench-apex:ro", IMAGE])
        wait_healthy(container)
        with tempfile.TemporaryDirectory(prefix="apex-populate-") as tmp:
            tmp_path = Path(tmp)
            with zipfile.ZipFile(dataset / "world_files_zipped" / f"{world['world_id']}.zip") as zf:
                zf.extractall(tmp_path / "world")
            archives = tar_subsystems(tmp_path / "world", "world", tmp_path)
            task_dir = dataset / "task_files" / task["task_id"]
            if task.get("task_input_files") and task_dir.is_dir():
                archives += tar_subsystems(task_dir, "task", tmp_path)
            record["populate"] = populate(container, archives)

        servers = server_specs(apps)
        secret_files = {}
        if "fmp_server" in servers:
            key = Path(setting_path("$DSH_BENCH_FMP_KEY_FILE")).read_text().strip()
            in_container(container, "sh", "-c", "umask 077; mkdir -p /app/.dsh-secrets; cat > /app/.dsh-secrets/fmp.key",
                         input=key.encode())
            secret_files["fmp_server"] = {"FMP_API_KEY": "/app/.dsh-secrets/fmp.key"}
        in_container(container, "sh", "-c", "cat > /tmp/apps-servers.json",
                     input=json.dumps({"servers": servers, "secret_files": secret_files}).encode())
        gateway = in_container(container, "python3", "/opt/dsh-bench-apex/start_apps.py", "/tmp/apps-servers.json")
        in_container(container, "rm", "-f", "/tmp/apps-servers.json")
        reply = in_container(container, "curl", "-sS", "--fail-with-body", "-X", "POST", "-H",
                             "Content-Type: application/json", "--data-binary", "@-", "http://127.0.0.1:8080/apps",
                             input=gateway)
        record["apps_configured"] = json.loads(reply)
        snapshot(container, out / "snapshots/before.tar.gz")
        record["setup_s"] = round(time.monotonic() - t0, 1)

        spec = {
            "task_id": task["task_id"],
            "prompt": task["prompt"],
            "model": model_for(args.endpoint, args.model),
            "system_prompt": SYSTEM_PROMPT,
            "system_prompt_mode": "append",
            "attach": {"container": container, "workspace": WORKSPACE},
            "runtime": RUNTIME,
            "container_env": SANDBOX_ENV,
            "disable": ["tool-web"],
            "mcp": [{"name": "apps", "transport": "stdio", "command": RUNTIME,
                     "args": ["exec", "-i", container, "/app/.venv/bin/python", "/opt/dsh-bench-apex/mcp_bridge.py"],
                     "toolCallTimeoutMs": 300_000}],
            "toolbelt": {},
            "final_answer": True,
            "limits": {"max_steps": args.max_steps, "timeout_s": args.timeout_s, "temperature": None},
            "meta": {"benchmark": "apex-agents", "dataset": str(dataset), "world_id": world["world_id"]},
        }
        spec["model"] = str((REPO / spec["model"]).resolve()) if not Path(spec["model"]).is_absolute() else spec["model"]
        (out / "agent-spec.json").write_text(json.dumps(spec, indent=2) + "\n")
        t1 = time.monotonic()
        launch = subprocess.run([sys.executable, "-m", "dsh_bench.launch", "--spec", str(out / "agent-spec.json"),
                                 "--out", str(out / "agent")], cwd=REPO, capture_output=True, text=True)
        (out / "launch.log").write_text(launch.stdout + launch.stderr)
        record["agent_s"] = round(time.monotonic() - t1, 1)
        snapshot(container, out / "snapshots/after.tar.gz")
        subprocess.run([RUNTIME, "cp", f"{container}:/tmp/apps", str(out / "apps-logs")], capture_output=True)
    finally:
        if not args.keep_container:
            subprocess.run([RUNTIME, "rm", "-f", "-t", "0", container], capture_output=True)
        record["finished_at"] = now()
        answer_file = out / "agent/answer.json"
        answer = json.loads(answer_file.read_text()) if answer_file.exists() else {}
        record["finish_reason"] = answer.get("finish_reason")
        (out / "trajectory.json").write_text(json.dumps(trajectory(task["prompt"], answer), indent=2) + "\n")
        (out / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record.get(k) for k in ("task_id", "finish_reason", "setup_s", "agent_s")} | {"out": str(out)}))
    return 0 if record.get("finish_reason") == "final_answer" else 1


if __name__ == "__main__":
    sys.exit(main())
