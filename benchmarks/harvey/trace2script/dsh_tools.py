"""DSH's tools as Python, quirks included: what the agent's tool calls did and returned, reproducible from a script.

Each method of `Tools` mirrors one DSH tool as configured for the Harvey runs (headless profile, core harness,
benchmarks/harvey/patch.yml) and returns the same text the model saw:

- read:  host side, workspace-isolated. `<path>ABS</path><type>file</type><content>N: line ... footer</content>`;
         default window 2,000 lines, lines cut at 2,000 chars, output capped at 50 KiB ("Output capped. Showing lines
         a-b. Use offset=b+1 to continue."). Never spilled. Marks the file as observed (read-before-write policy).
- write: harvey-write rule (a relative path goes under output/), read-before-overwrite, "Created file" / "Updated file".
- edit:  relative to the workspace, read-before-edit (unless written or edited in this session), exactly one match
         unless replace_all.
- glob:  `rg --files --glob=PATTERN --sort=modified --no-ignore --hidden` in the task container; > 100 paths: the
         first 100 and "(Showing 100 of N paths. Full sorted result stored at: SPILL. ...)"; none: "No files found".
- grep:  `rg --json --regexp=PATTERN [--glob=INCLUDE] [-- PATH]` in the container, raw bytes (blind inside .docx),
         grouped by file, lines cut at 2,000 bytes, first 250 matches then "Found 250 of N matches" + spill note.
- bash:  `bash -c COMMAND` in the container via plugins/sandbox-podman/podman-exec.sh, default timeout 60 s (cap
         600 s), stdout then "[stderr]" block, "(no output)", "[timed out after Nms]", "[exit code: N]",
         "[killed by signal: S]"; run_in_background starts a job.
- job_output / job_list / job_kill, todo_write, create_goal / get_goal / update_goal, read_image: same texts.
- Spill policy: any result except read's over 50,000 bytes keeps a head and a tail (half each of the budget left
  after the notice) and ends with "(Omitted N bytes. Full formatted result stored at: SPILL. ...)". Spill files
  live in a host temp folder outside the workspace, so - as in the runs - the agent cannot read them.

Arguments may contain the marker WS_MARK (the recorded workspace path, rewritten by trace2script.py); it is replaced
by this run's workspace before the call. Every call is logged (and, in replay, compared with the recorded output).
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import secrets
import signal
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PODMAN_EXEC = REPO / "plugins/sandbox-podman/podman-exec.sh"
WS_MARK = "⟦WS⟧"          # ⟦WS⟧
READ_LIMIT, READ_MAX_LINE, READ_MAX_BYTES = 2000, 2000, 50 * 1024
GLOB_MAX, GREP_MAX, GREP_LINE_BYTES = 100, 250, 2000
SPILL_MAX_INLINE = 50_000
BASH_DEFAULT_TIMEOUT_MS, BASH_MAX_TIMEOUT_MS = 60_000, 600_000
RETRIEVAL_HINT = "Use read with offset/limit, or grep this path to search within it."
DENIED = "[sandbox: file access denied under workspace-isolated mode]"
CONCURRENCY_SAFE = {"read", "glob", "grep", "read_image"}


class ToolError(Exception):
    """A tool failure: rendered as 'Error: <message>', like DSH."""


def _cut_utf8(data: bytes, n: int) -> bytes:
    data = data[:n]
    while data and (data[-1] & 0xC0) == 0x80:
        data = data[:-1]
    if data and data[-1] >= 0xC0:
        data = data[:-1]
    return data


def _cut_utf8_tail(data: bytes, n: int) -> bytes:
    data = data[len(data) - n:] if n > 0 else b""
    while data and (data[0] & 0xC0) == 0x80:
        data = data[1:]
    return data


class Tools:
    def __init__(self, workspace: str | Path, container: str, runtime: str = "podman", env: dict | None = None,
                 output_dir: str = "output", log=None, recorded: dict | None = None):
        self.ws = str(Path(workspace).resolve())
        self.container, self.runtime, self.env = container, runtime, dict(env or {})
        self.output_dir = output_dir
        self.observed: dict[str, tuple[float, int]] = {}      # abs path -> (mtime, size) when last read or written
        # DSH's spill root: /tmp/dsh-spill-<6 chars>/session-<12 hex>/<12 hex>-<tool>.txt (its length sets the
        # spill notice's length, which sets where an oversized result is cut).
        while True:
            self.spill_root = Path(tempfile.gettempdir()) / ("dsh-spill-" + secrets.token_urlsafe(6)[:6].replace("-", "x").replace("_", "y"))
            try:
                self.spill_root.mkdir(mode=0o700)
                break
            except FileExistsError:
                continue
        self.session = secrets.token_hex(6)
        self.jobs: dict[str, dict] = {}
        self.todos: list = []
        self.goal: dict | None = None
        self.log, self.recorded = log, recorded or {}
        self.lock = threading.Lock()

    # ── plumbing ───────────────────────────────────────────────────────────────────────────────────────────────────
    def _sub(self, value):
        if isinstance(value, str):
            return value.replace(WS_MARK, self.ws)
        if isinstance(value, list):
            return [self._sub(v) for v in value]
        if isinstance(value, dict):
            return {k: self._sub(v) for k, v in value.items()}
        return value

    def _abs(self, file_path: str) -> str:
        p = file_path if os.path.isabs(file_path) else os.path.join(self.ws, file_path)
        p = os.path.normpath(p)
        real = os.path.realpath(p)
        inside = lambda x: x == self.ws or x.startswith(self.ws + os.sep)
        if not inside(p) or not inside(real):
            raise ToolError(DENIED)
        return p

    def _spill(self, tool: str, text: str, suffix: str = "") -> str:
        d = self.spill_root / f"session-{self.session}"
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{secrets.token_hex(6)}-{tool}{suffix}.txt"
        f.write_text(text)
        return str(f)

    def _spill_policy(self, tool: str, text: str) -> str:
        data = text.encode()
        if tool == "read" or len(data) <= SPILL_MAX_INLINE:
            return text
        loc = self._spill(tool, text)
        notice = lambda n: f"(Omitted {n} bytes. Full formatted result stored at: {loc}. {RETRIEVAL_HINT})"
        reserve = len(notice(len(data)).encode()) + 2
        budget = max(0, SPILL_MAX_INLINE - reserve)
        head, tail = _cut_utf8(data, (budget + 1) // 2), _cut_utf8_tail(data, budget // 2)
        kept = head.decode() + tail.decode()
        omitted = len(data) - len(head) - len(tail)
        return f"{kept}\n\n{notice(omitted)}" if kept else notice(omitted)

    def _container_argv(self, argv: list[str], workdir: str | None = None) -> list[str]:
        return [str(PODMAN_EXEC), self.runtime, self.container, workdir or self.ws,
                *[f"{k}={v}" for k, v in self.env.items()], "--", *argv]

    async def call(self, name: str, _id: str | None = None, **args) -> str:
        """Run one tool call (in a worker thread) and log it; errors come back as 'Error: ...' text, like DSH."""
        args = self._sub(args)
        t0 = time.time()
        try:
            text = await asyncio.to_thread(getattr(self, "_" + name), **args)
            err = False
        except ToolError as e:
            text, err = f"Error: {e}", True
        text = self._spill_policy(name, text) if not err else text
        if self.log is not None:
            with self.lock:
                self.log.write(json.dumps({"id": _id, "tool": name, "args": args, "error": err,
                                           "seconds": round(time.time() - t0, 2), "output": text}) + "\n")
                self.log.flush()
        return text

    # Awaitable tool methods: `await T.read(file_path=...)`. `_id` keys the call to its recorded output.
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if not hasattr(type(self), "_" + name):
            raise AttributeError(name)
        return lambda _id=None, **args: self.call(name, _id, **args)

    # ── file tools (host side) ─────────────────────────────────────────────────────────────────────────────────────
    def _read(self, file_path: str, offset: int | None = None, limit: int | None = None) -> str:
        if not file_path or not file_path.strip():
            raise ToolError("file_path must be a non-empty string")
        limit = READ_LIMIT if limit is None else int(limit)
        if limit > READ_LIMIT:
            raise ToolError(f"limit must be less than or equal to {READ_LIMIT}")
        offset = 1 if offset is None else int(offset)
        p = self._abs(file_path)
        if not os.path.exists(p):
            raise ToolError(f'cannot read "{p}": not found')
        if not os.path.isfile(p):
            raise ToolError(f'cannot read "{p}": not a regular file')
        raw = Path(p).read_bytes().decode("utf-8", errors="replace")
        lines, total, out_bytes, capped = [], 0, 0, False
        parts = raw.split("\n")
        if parts and parts[-1] == "":
            parts = parts[:-1]
        for line in parts:
            total += 1
            if capped or total < offset or len(lines) >= limit:
                continue
            line = line[:-1] if line.endswith("\r") else line
            text = line if len(line) <= READ_MAX_LINE else f"{line[:READ_MAX_LINE]}... (line truncated to {READ_MAX_LINE} chars)"
            size = len(text.encode()) + (1 if lines else 0)
            if out_bytes + size > READ_MAX_BYTES:
                capped = True
                continue
            out_bytes += size
            lines.append((total, text))
        if not capped and offset > total and not (total == 0 and offset == 1):
            raise ToolError(f'offset {offset} is out of range for "{p}" ({total} lines)')
        end = lines[-1][0] if lines else max(0, offset - 1)
        if capped:
            footer = f"(Output capped. Showing lines {offset}-{end}. Use offset={end + 1} to continue.)"
        elif end < total:
            footer = f"(Showing lines {offset}-{end} of {total}. Use offset={end + 1} to continue.)"
        else:
            footer = f"(End of file - total {total} lines)"
        body = "\n".join(f"{n}: {t}" for n, t in lines) + f"\n\n{footer}" if lines else footer
        st = os.stat(p)
        self.observed[p] = (st.st_mtime, st.st_size)
        return f"<path>{p}</path>\n<type>file</type>\n<content>\n{body}\n</content>"

    def _route_write(self, file_path: str) -> str:
        if not file_path or os.path.isabs(file_path):
            return file_path
        clean = os.path.normpath(file_path)
        if clean == self.output_dir or clean.startswith(self.output_dir + "/"):
            return clean
        return f"{self.output_dir}/{clean}"

    def _fresh(self, p: str) -> bool:
        if p not in self.observed:
            return False
        st = os.stat(p)
        return self.observed[p] == (st.st_mtime, st.st_size)

    def _write(self, file_path: str, content: str, **_ignored) -> str:
        if not file_path or not file_path.strip():
            raise ToolError("file_path must be a non-empty string")
        p = self._abs(self._route_write(file_path))
        exists = os.path.exists(p)
        if exists and not self._fresh(p):
            raise ToolError(f'cannot modify "{p}": file has not been read — read the file, then retry')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        Path(p).write_text(content)
        st = os.stat(p)
        self.observed[p] = (st.st_mtime, st.st_size)
        return f"<path>{p}</path>\n<type>file</type>\n<content>\n{'Updated' if exists else 'Created'} file\n</content>"

    def _edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
        if not file_path or not file_path.strip():
            raise ToolError("file_path must be a non-empty string")
        if not old_string:
            raise ToolError("old_string must be a non-empty string")
        if old_string == new_string:
            raise ToolError("old_string and new_string must differ")
        p = self._abs(file_path)
        if not os.path.exists(p):
            raise ToolError(f'cannot edit "{p}": not found')
        if not self._fresh(p):
            raise ToolError(f'cannot modify "{p}": file has not been read — read the file, then retry')
        text = Path(p).read_text()
        n = text.count(old_string)
        if n == 0:
            raise ToolError(f'old_string was not found in "{p}"')
        if n > 1 and not replace_all:
            raise ToolError(f'old_string matched {n} times in "{p}"; provide a more specific old_string or set replace_all to true')
        Path(p).write_text(text.replace(old_string, new_string) if replace_all else text.replace(old_string, new_string, 1))
        st = os.stat(p)
        self.observed[p] = (st.st_mtime, st.st_size)
        return (f"The file {p} has been updated. All occurrences were successfully replaced." if replace_all
                else f"The file {p} has been updated successfully.")

    def _read_image(self, file_path: str, **_ignored) -> str:
        p = self._abs(file_path)
        if not os.path.isfile(p):
            raise ToolError(f'cannot read "{p}": not found')
        return f"[image {p}: {os.path.getsize(p)} bytes; shown to the model as an image, not text]"

    # ── search tools (ripgrep in the container) ────────────────────────────────────────────────────────────────────
    def _rg(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(self._container_argv(["rg", *args]), capture_output=True, timeout=33, cwd=self.ws)

    def _glob(self, pattern: str, path: str | None = None) -> str:
        argv = ["--files", f"--glob={pattern}", "--sort=modified", "--no-ignore", "--hidden"]
        for vcs in (".git", ".svn", ".hg", ".bzr", ".jj", ".sl"):
            argv += [f"--glob=!**/{vcs}", f"--glob=!**/{vcs}/**"]
        if path is not None:
            argv += ["--", path]
        r = self._rg(argv)
        if r.returncode not in (0, 1):
            raise ToolError(f"glob pattern rejected by ripgrep: {r.stderr.decode(errors='replace').strip()}")
        paths = [x for x in r.stdout.decode(errors="replace").split("\n") if x]
        if not paths:
            return "No files found"
        if len(paths) <= GLOB_MAX:
            return "\n".join(paths)
        loc = self._spill("glob", "\n".join(paths), "-results")
        return ("\n".join(paths[:GLOB_MAX]) + f"\n\n(Showing {GLOB_MAX} of {len(paths)} paths. Full sorted result "
                f"stored at: {loc}. {RETRIEVAL_HINT})")

    def _grep(self, pattern: str, path: str | None = None, include: str | None = None) -> str:
        argv = ["--json", f"--regexp={pattern}"]
        if include is not None:
            argv.append(f"--glob={include}")
        if path is not None:
            argv += ["--", path]
        r = self._rg(argv)
        if r.returncode not in (0, 1):
            raise ToolError(f"grep pattern rejected by ripgrep: {r.stderr.decode(errors='replace').strip()}")
        matches = []
        for line in r.stdout.decode(errors="replace").split("\n"):
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("type") != "match":
                continue
            data = rec["data"]
            p = data["path"].get("text", "<non-UTF-8 path>")
            text = data["lines"].get("text")
            text = "<non-UTF-8 line>" if text is None else text.rstrip("\n").rstrip("\r")
            matches.append((p, data["line_number"], text))
        if not matches:
            return "No matches found"

        def preview(t: str) -> str:
            b = t.encode()
            return t if len(b) <= GREP_LINE_BYTES else _cut_utf8(b, GREP_LINE_BYTES).decode() + " (line truncated)"

        def fmt(ms):
            groups: dict[str, list] = {}
            for p, n, t in ms:
                groups.setdefault(p, []).append(f"Line {n}: {preview(t)}")
            return "\n\n".join(f"{p}\n" + "\n".join(v) for p, v in groups.items())

        noun = "match" if len(matches) == 1 else "matches"
        if len(matches) <= GREP_MAX:
            return f"Found {len(matches)} {noun}\n\n{fmt(matches)}"
        loc = self._spill("grep", f"Found {len(matches)} {noun}\n\n{fmt(matches)}", "-results")
        return (f"Found {GREP_MAX} of {len(matches)} matches\n\n{fmt(matches[:GREP_MAX])}\n\n"
                f"(Full grep result stored at: {loc}. {RETRIEVAL_HINT})")

    # ── bash and jobs (container) ──────────────────────────────────────────────────────────────────────────────────
    def _bash(self, command: str, description: str | None = None, timeoutMs: float | None = None,
              workdir: str | None = None, run_in_background: bool = False) -> str:
        argv = self._container_argv(["bash", "-c", command], workdir)
        if run_in_background:
            job_id = f"bash-{len(self.jobs) + 1}"
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.ws,
                                    start_new_session=True)
            job = {"proc": proc, "buf": [], "read": 0, "status": "running", "detail": None, "command": command}
            threading.Thread(target=self._pump, args=(job,), daemon=True).start()
            self.jobs[job_id] = job
            return f"started background job {job_id}"
        timeout = min(BASH_DEFAULT_TIMEOUT_MS if timeoutMs is None else float(timeoutMs), BASH_MAX_TIMEOUT_MS)
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ws, start_new_session=True)
        timed_out, sig = False, None
        try:
            out, err = proc.communicate(timeout=timeout / 1000)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.send_signal(signal.SIGTERM)          # podman-exec.sh's trap kills the process group in the container
            try:
                out, err = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                out, err = proc.communicate()
                sig = "SIGKILL"
        code = proc.returncode
        out, err = out.decode(errors="replace"), err.decode(errors="replace")
        body = out
        if err:
            if body and not body.endswith("\n"):
                body += "\n"
            body += f"[stderr]\n{err}"
        if not body:
            body = "(no output)"
        markers = []
        if timed_out:
            markers.append(f"[timed out after {int(timeout)}ms]")
        if sig:
            markers.append(f"[killed by signal: {sig}]")
        elif code not in (0, None):
            markers.append(f"[exit code: {code if code > 0 else 128 - code}]")
        if not markers:
            return body
        return (body if body.endswith("\n") else body + "\n") + "\n".join(markers)

    def _pump(self, job: dict) -> None:
        for chunk in iter(lambda: job["proc"].stdout.read1(65536), b""):
            job["buf"].append(chunk.decode(errors="replace"))
        code = job["proc"].wait()
        if job["status"] == "running":
            job["status"] = "completed"
            job["detail"] = f"exit code {code}"

    def _status(self, job: dict) -> str:
        return f"[status: {job['status']}, {job['detail']}]" if job["detail"] else f"[status: {job['status']}]"

    def _job_output(self, job_id: str, wait: bool = False, timeout_ms: float | None = None) -> str:
        job = self.jobs.get(job_id)
        if job is None:
            raise ToolError(f"unknown job {job_id}")
        if wait:
            deadline = time.time() + min(timeout_ms or 30_000, 600_000) / 1000
            while job["status"] == "running" and time.time() < deadline:
                time.sleep(0.2)
        text = "".join(job["buf"])
        delta, job["read"] = text[job["read"]:], len(text)
        body = delta if delta else "(no new output)"
        return f"{body}{'' if body.endswith(chr(10)) else chr(10)}{self._status(job)}"

    def _job_list(self) -> str:
        return "\n".join(f"{i} [bash] {j['status']} — {j['command']}" for i, j in self.jobs.items()) or "(no jobs)"

    def _job_kill(self, job_id: str, reason: str | None = None) -> str:
        job = self.jobs.get(job_id)
        if job is None:
            raise ToolError(f"unknown job {job_id}")
        if job["status"] == "running":
            job["status"] = "killed"
            job["proc"].send_signal(signal.SIGTERM)
        return f"requested cancellation of job {job_id}"

    # ── bookkeeping tools ──────────────────────────────────────────────────────────────────────────────────────────
    def _todo_write(self, todos: list) -> str:
        self.todos = todos
        c = {s: sum(1 for t in todos if t.get("status") == s) for s in ("pending", "in_progress", "completed")}
        return f"Updated todo list: {c['pending']} pending, {c['in_progress']} in progress, {c['completed']} completed."

    def _goal_json(self, activation: str) -> str:
        return json.dumps({"goal": self.goal, "activation": activation}, separators=(",", ":"))

    def _create_goal(self, objective: str, **extra) -> str:
        self.goal = {"id": f"goal-{uuid.uuid4()}", "revision": 1, "objective": objective, "phase": "active",
                     "roundsStarted": 0, "maxGoalRounds": extra.get("max_rounds", 4)}
        return self._goal_json("armed")

    def _get_goal(self) -> str:
        if self.goal is None:
            raise ToolError("no goal")
        return self._goal_json("armed")

    def _update_goal(self, goal_id: str = "", revision: int = 0, action: str = "", **extra) -> str:
        if self.goal is None:
            raise ToolError("no goal")
        phase = {"complete": "complete", "blocked": "blocked", "resume": "active"}.get(action, self.goal["phase"])
        self.goal = {**self.goal, "revision": self.goal["revision"] + 1, "phase": phase}
        return self._goal_json("disarmed" if phase != "active" else "armed")

    async def parallel(self, *calls):
        """Run several concurrency-safe calls at once (DSH runs them concurrently within one step)."""
        return await asyncio.gather(*calls)
