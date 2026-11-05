"""Run one benchmark task with DSH: agent loop on the host, tools in a per-task container.

    python3 -m dsh_bench.launch --spec task.json --out runs/<run>/<task>

Steps (docs/DESIGN.md):
  1. stage the workspace (copies from the spec), make read-only dirs read-only on the host, take the baseline snapshot
     (a git repo OUTSIDE the workspace: <out>/baseline.git);
  2. start the container: workspace mounted at its host path, read-only dirs `:ro`, no capabilities, host uid;
  3. write <out>/run.patch.yml: the model, the isolation rows, sandbox-podman, final-answer, benchmark-limits, the system
     prompt, disabled rows and MCP servers from the spec; the spec's extra patches follow it as further --patch files;
  4. run `dsh --profile headless` in the workspace (DSH_HOME = <out>/dsh-home, outside the workspace);
  5. collect the four standard outputs: answer.json, workspace/ + workspace.diff, dsh-home/sessions, run.json;
  6. remove the container.

The spec is JSON. Required: task_id, prompt, model (a models/*.json file). Everything else has a default (SPEC_DEFAULTS).
Relative paths in the spec resolve against the spec file's directory. In `stage[].from`, `extra_patches` and
`skills_dir`, `{repo}` is this repository. In the prompt, system prompt and container env, `{workspace}` is the
absolute workspace path.
"""

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DSH = Path(os.environ.get("DSH_BENCH_DSH_ROOT", REPO / "work/deepseek-harness"))
HEADLESS_PREFIX = "You are a coding agent powered by the {{model}} model."
HEADLESS_SUFFIX = "Your working directory is {{cwd}}."

SPEC_DEFAULTS: dict = {
    "system_prompt": None,  # text; None keeps DSH's headless persona only
    "system_prompt_mode": "append",  # append: after DSH's persona; replace: instead of it (and of the DSH identity)
    "stage": [],  # [{"from": path, "to": rel path in workspace, "readonly": bool}]
    "make_dirs": [],  # empty writable dirs to create in the workspace (e.g. "output")
    "image": "dsh-bench-base",
    "runtime": "podman",
    "network": "none",  # container network: "none", or a podman network mode such as "slirp4netns"
    "container_env": {},  # env inside the container for every command
    "disable": [],  # base-profile row ids to disable (e.g. "web", "tool-subagent")
    "mcp": [],  # [{"name": str, "transport": "streamable-http"|"stdio", "url"|"command"/"args", "headers": {}}]
    "limits": {"max_steps": None, "timeout_s": 3600, "temperature": None},  # temperature: None leaves it unset
    "final_answer": True,
    "extra_patches": [],  # benchmark patch files, applied after run.patch.yml; "__DSH_REPO__" -> the DSH checkout
    "dsh_env": {},  # extra environment for the DSH process (endpoints for benchmark plugins, ...)
    "dsh_env_files": {},  # NAME -> file whose content is the value (tokens: kept out of specs and run records)
    "grace_s": 300,  # wall-clock allowance beyond limits.timeout_s before the DSH process is killed
}


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(argv, check=True, capture_output=True, text=True, **kwargs)


def load_spec(path: Path) -> dict:
    raw = json.loads(path.read_text())
    unknown = set(raw) - set(SPEC_DEFAULTS) - {"task_id", "prompt", "model", "meta"}
    if unknown:
        raise ValueError(f"unknown spec keys: {sorted(unknown)}")
    missing = {"task_id", "prompt", "model"} - set(raw)
    if missing:
        raise ValueError(f"missing spec keys: {sorted(missing)}")
    spec = json.loads(json.dumps(SPEC_DEFAULTS)) | raw
    spec["limits"] = SPEC_DEFAULTS["limits"] | raw.get("limits", {})
    if spec["system_prompt_mode"] not in ("append", "replace"):
        raise ValueError("system_prompt_mode must be append or replace")
    base = path.resolve().parent

    def where(value: str) -> Path:
        p = Path(value.replace("{repo}", str(REPO)))
        return p if p.is_absolute() else (base / p).resolve()

    spec["model"] = str(where(spec["model"]))
    spec["extra_patches"] = [str(where(p)) for p in spec["extra_patches"]]
    for item in spec["stage"]:
        item["from"] = str(where(item["from"]))
    return spec


def set_readonly(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_symlink():
            continue
        path.chmod(0o555 if path.is_dir() else 0o444)
    root.chmod(0o555)


def git(gitdir: Path, workspace: Path, *args: str, binary: bool = False) -> str | bytes:
    argv = ["git", f"--git-dir={gitdir}", f"--work-tree={workspace}", "-c", "user.name=dsh-bench",
            "-c", "user.email=dsh-bench@localhost", "-c", "core.autocrlf=false", "-c", "core.quotepath=false", *args]
    if binary:  # diffs of binary files (xlsx, pdf) are not text
        return subprocess.run(argv, check=True, capture_output=True).stdout
    return run(argv).stdout


def stage(spec: dict, workspace: Path, gitdir: Path) -> list[Path]:
    workspace.mkdir(parents=True)
    readonly = []
    for item in spec["stage"]:
        src, dest = Path(item["from"]), workspace / item["to"]
        if not src.exists():
            raise FileNotFoundError(f"stage source missing: {src}")
        if src.is_dir():
            shutil.copytree(src, dest, symlinks=True, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest, follow_symlinks=False)
        if item.get("readonly"):
            readonly.append(dest)
    for rel in spec["make_dirs"]:
        (workspace / rel).mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q", "--bare", str(gitdir)])
    git(gitdir, workspace, "add", "-A", "--force")
    git(gitdir, workspace, "commit", "-q", "--allow-empty", "-m", "baseline")
    for path in readonly:
        set_readonly(path) if path.is_dir() else path.chmod(0o444)
    return readonly


def start_container(spec: dict, name: str, workspace: Path, readonly: list[Path]) -> None:
    runtime = spec["runtime"]
    argv = [runtime, "run", "-d", "--name", name, f"--network={spec['network']}", "--cap-drop=ALL",
            "--security-opt=no-new-privileges", "-e", "HOME=/tmp", "-w", str(workspace)]
    argv += ["--userns=keep-id"] if runtime == "podman" else ["--user", f"{os.getuid()}:{os.getgid()}"]
    argv += ["-v", f"{workspace}:{workspace}"]
    for path in readonly:
        argv += ["-v", f"{path}:{path}:ro"]
    for key, value in spec["container_env"].items():
        argv += ["-e", f"{key}={value}"]
    argv += [spec["image"], "sleep", "infinity"]
    run(argv)


def model_rows(model: dict) -> list[dict]:
    provider = {
        "displayName": model.get("display_name", model["model"]),
        "apiKeyEnv": "DSH_BENCH_MODEL_KEY",
        "api": model["api"],
        "baseURL": model["base_url"],
        "models": [{
            "id": model["model"],
            "name": model.get("display_name", model["model"]),
            "contextWindow": model["context_window"],
            "maxTokens": model["max_tokens"],
            **({"input": model["input"]} if "input" in model else {}),
            **({"reasoningEfforts": model["reasoning_efforts"]} if "reasoning_efforts" in model else {}),
        }],
    }
    for key, field in (("reasoning", "reasoning"), ("compat", "compat"), ("streamIdleTimeoutMs", "stream_idle_timeout_ms"),
                       ("retryPolicy", "retry_policy")):
        if field in model:
            provider[key] = model[field]
    return [
        {"id": "agent-default-model", "config": {"provider": model["provider"], "model": model["model"]}},
        {"id": "llm-pi-ai", "config": {"providers": {model["provider"]: provider}}},
    ]


def build_patch(spec: dict, model: dict, out: Path, workspace: Path, container: str) -> list[dict]:
    rows = model_rows(model) + [
        {"id": "session-persistence-jsonl", "config": {"root": str(out / "dsh-home/sessions"), "compression": "none"}},
        {"id": "session-title-llm", "disabled": True},
        {"id": "approval", "config": {"policy": "never"}},
        {"id": "permission", "config": {
            "presets": {"bench-isolated": {
                "sandbox": "workspace-isolated", "approval": "never", "name": "Benchmark workspace",
                "description": "Files only inside the task workspace; commands run in the task container."}},
            "defaultPreset": "bench-isolated"}},
        {"id": "sandbox", "disabled": True},
    ]
    if spec["system_prompt"] is not None:
        text = spec["system_prompt"].replace("{workspace}", str(workspace))
        if spec["system_prompt_mode"] == "append":
            config = {"personaPrefix": f"{HEADLESS_PREFIX}\n\n{text}", "personaSuffix": HEADLESS_SUFFIX}
        else:
            config = {"personaPrefix": text, "personaSuffix": HEADLESS_SUFFIX, "includeHarnessIdentity": False}
        rows.append({"id": "system-prompt", "config": config})
    rows += [{"id": row, "disabled": True} for row in spec["disable"]]
    inserts = [{"id": "sandbox-podman", "name": str(REPO / "plugins/sandbox-podman/index.mjs"), "config": {
        "container": container, "runtime": spec["runtime"],
        "env": {k: v.replace("{workspace}", str(workspace)) for k, v in spec["container_env"].items()}}}]
    limits = spec["limits"]
    limits_config = {"maxSteps": limits["max_steps"],
                     "timeoutMs": None if limits["timeout_s"] is None else int(limits["timeout_s"] * 1000)}
    if limits["temperature"] is not None:
        limits_config["temperature"] = limits["temperature"]
    inserts.append({"id": "benchmark-limits", "name": str(REPO / "plugins/benchmark-limits/index.mjs"),
                    "config": limits_config})
    if spec["final_answer"]:
        inserts.append({"id": "final-answer", "name": str(REPO / "plugins/final-answer/index.mjs"),
                        "config": {"answersDir": str(out / "answers")}})
    for server in spec["mcp"]:
        config = {"serverName": server["name"], "transport": server["transport"], "failOnStartupError": True}
        for key in ("url", "headers", "command", "args", "env", "toolCallTimeoutMs"):
            if key in server:
                config[key] = server[key]
        inserts.append({"id": f"mcp-{server['name']}", "name": "@deepseek-ai/dsh-mcp-client", "config": config})
    rows.append({"insert": inserts})
    return rows


def write_yaml_rows(path: Path, rows: list[dict]) -> None:
    # JSON is valid YAML: one flow-style row per list item keeps the file readable and needs no YAML library.
    path.write_text("# Generated by dsh_bench.launch\n" + "".join(f"- {json.dumps(row)}\n" for row in rows))


def root_session(home: Path) -> tuple[dict, list[dict]] | None:
    roots = []
    for path in sorted((home / "sessions").rglob("session.v*.jsonl")):
        # Split on "\n" only: str.splitlines() also splits on U+2028/U+2029, which JSON leaves unescaped inside strings.
        lines = [json.loads(line) for line in path.read_text().split("\n") if line.strip()]
        if lines and not lines[0].get("parentSession"):
            roots.append((lines[0], lines[1:]))
    return roots[0] if len(roots) == 1 else None


def collect(out: Path, workspace: Path, gitdir: Path, home: Path, exit_code: int | None) -> dict:
    session = root_session(home)
    header, events = session if session else ({}, [])
    ends = [e["data"]["reason"] for e in events if e.get("type") == "turn/end"]
    end = ends[-1] if ends else None
    last_text = ""
    for event in events:
        if event.get("type") == "assistant/message":
            text = "".join(b.get("text", "") for b in event["data"]["message"]["content"] if b.get("type") == "text")
            if text:
                last_text = text
    answer_file = out / "answers" / f"{header.get('id', '')}.json"
    if header and answer_file.exists():
        answer, source = json.loads(answer_file.read_text())["answer"], "final_answer"
    else:
        answer, source = last_text, "last_assistant_message"
    if end is None:
        finish = "no_session" if session is None else "incomplete"
    elif end.get("kind") == "aborted" and end.get("reason", {}).get("kind") == "hook":
        finish = end["reason"]["reason"]  # final_answer, benchmark:max-steps, benchmark:timeout
    else:
        finish = end.get("kind", "unknown")
    answer_json = {"answer": answer, "source": source, "finish_reason": finish, "turn_end": end,
                   "root_session_id": header.get("id"), "exit_code": exit_code}
    (out / "answer.json").write_text(json.dumps(answer_json, indent=2) + "\n")

    git(gitdir, workspace, "add", "-A", "--force")
    (out / "workspace.diff").write_bytes(git(gitdir, workspace, "diff", "--cached", "--binary", "HEAD", binary=True))
    changed = [line.split("\t", 1) for line in git(gitdir, workspace, "diff", "--cached", "--name-status", "HEAD").split("\n") if line]
    steps = sum(e.get("type") == "step/start" for e in events)
    sessions = len(list((home / "sessions").rglob("session.v*.jsonl")))
    return {"finish_reason": finish, "answer_source": source, "root_steps": steps, "sessions": sessions,
            "changed_files": [{"status": s, "path": p} for s, p in changed]}


def collect_only(out: Path) -> int:
    record = json.loads((out / "run.json").read_text()) if (out / "run.json").exists() else {
        "task_id": json.loads((out / "spec.json").read_text())["task_id"], "recollected": True}
    record |= collect(out, out / "workspace", out / "baseline.git", out / "dsh-home", record.get("exit_code"))
    record["collected_at"] = now()
    (out / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record.get(k) for k in ("task_id", "finish_reason", "root_steps", "sessions")}
                     | {"changed": len(record["changed_files"]), "out": str(out)}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new run directory for this task")
    parser.add_argument("--node", default=os.environ.get("NODE", shutil.which("node") or "node"))
    parser.add_argument("--keep-container", action="store_true", help="leave the container running (debugging)")
    parser.add_argument("--collect-only", action="store_true",
                        help="only (re)build answer.json, workspace.diff and run.json of an existing --out")
    args = parser.parse_args()
    if args.collect_only:
        return collect_only(args.out.resolve())

    spec = load_spec(args.spec)
    model = json.loads(Path(spec["model"]).read_text())
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; every run needs a new directory")
    out.mkdir(parents=True)
    workspace, home, gitdir = out / "workspace", out / "dsh-home", out / "baseline.git"
    home.mkdir()
    container = f"dshb-{uuid.uuid4().hex[:10]}"
    record: dict = {"task_id": spec["task_id"], "started_at": now(), "container": container, "spec": spec,
                    "model": model, "dsh": {"root": str(DSH), "commit": run(["git", "-C", str(DSH), "rev-parse", "HEAD"]).stdout.strip()},
                    "harness_commit": run(["git", "-C", str(REPO), "rev-parse", "HEAD"]).stdout.strip()}
    (out / "spec.json").write_text(json.dumps(spec, indent=2) + "\n")

    t0 = time.monotonic()
    readonly = stage(spec, workspace, gitdir)
    record["image"] = {"name": spec["image"], "id": run([spec["runtime"], "image", "inspect", "--format", "{{.Id}}",
                                                         spec["image"]]).stdout.strip()}
    patch = out / "run.patch.yml"
    write_yaml_rows(patch, build_patch(spec, model, out, workspace, container))
    patches = [patch]
    for i, extra in enumerate(spec["extra_patches"]):
        copy = out / f"extra-{i}-{Path(extra).name}"
        copy.write_text(Path(extra).read_text().replace("__DSH_REPO__", str(DSH)))
        patches.append(copy)
    record["patches"] = [{"path": str(p), "sha256": sha256(p)} for p in patches]

    key = ""
    if "api_key_file" in model:
        key = Path(os.path.expanduser(model["api_key_file"])).read_text().strip()
    elif "api_key_env" in model:
        key = os.environ[model["api_key_env"]]
    env = os.environ | {"DSH_HOME": str(home), "DSH_PERMISSION_MODE": "workspace-isolated", "DSH_TELEMETRY_DISABLED": "1",
                        "DSH_BENCH_DSH_ROOT": str(DSH), "DSH_BENCH_MODEL_KEY": key or "none"} | spec["dsh_env"]
    for name, file in spec["dsh_env_files"].items():
        env[name] = Path(os.path.expanduser(file)).read_text().strip()
    prompt = spec["prompt"].replace("{workspace}", str(workspace))
    (out / "prompt.txt").write_text(prompt)
    argv = [args.node, str(DSH / "apps/cli/lib/bin.js"), "--profile", "headless"]
    for p in patches:
        argv += ["--patch", str(p)]
    argv.append(prompt)

    exit_code = None
    try:
        start_container(spec, container, workspace, readonly)
        record["setup_s"] = round(time.monotonic() - t0, 1)
        wall = None if spec["limits"]["timeout_s"] is None else spec["limits"]["timeout_s"] + spec["grace_s"]
        t1 = time.monotonic()
        with (out / "dsh.stdout").open("w") as so, (out / "dsh.stderr").open("w") as se:
            proc = subprocess.Popen(argv, cwd=workspace, env=env, stdout=so, stderr=se, start_new_session=True)
            try:
                exit_code = proc.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                exit_code = None
                record["killed_after_s"] = wall
        record["agent_s"] = round(time.monotonic() - t1, 1)
    finally:
        if not args.keep_container:
            subprocess.run([spec["runtime"], "rm", "-f", "-t", "0", container], capture_output=True)
        record["exit_code"] = exit_code
        record |= collect(out, workspace, gitdir, home, exit_code)
        record["finished_at"] = now()
        (out / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record.get(k) for k in ("task_id", "finish_reason", "root_steps", "sessions", "agent_s")}
                     | {"changed": len(record["changed_files"]), "out": str(out)}))
    return 0 if record["finish_reason"] in ("final_answer", "completed") else 1


if __name__ == "__main__":
    sys.exit(main())
