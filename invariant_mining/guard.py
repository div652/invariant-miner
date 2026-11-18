"""Credit guard: watches the gateway's premium-interaction usage and pauses invariant_mining runs before a limit.

    python -m invariant_mining guard --max-used 999990 [--interval 10] [--log FILE] [--pause-file F] [--kill-pattern RE ...]

Every `interval` seconds it reads GET /usage (no generation) and computes used = entitlement - remaining. It pauses when
the usage, or the usage projected one interval ahead at the current rate, reaches --max-used: it sends SIGTERM to every
`python -m invariant_mining run ...` process (found through /proc), and to every process whose command line matches a
--kill-pattern regex; it creates --pause-file (benchmark drivers wait while it exists before starting a task), logs PAUSED
and exits. A paused invariant_mining run resumes with `run` (jobs in flight are redone); delete the pause file to let the
drivers go on.
"""

import json
import os
import re
import signal
import time
import urllib.request
from pathlib import Path

from .models import gateway_key


def used_now(cfg: dict) -> tuple[int, int, str]:
    req = urllib.request.Request(cfg["gateway"]["base_url"].rstrip("/") + "/usage",
                                 headers={"Authorization": "Bearer " + gateway_key(cfg)})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.load(r)
    q = j["quota_snapshots"]["premium_interactions"]
    return int(q["entitlement"]) - int(q["remaining"]), int(q["entitlement"]), str(j.get("login"))


def cmdlines():
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) == os.getpid():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        yield int(d.name), [a.decode(errors="replace") for a in argv if a]


def matching_pids(patterns: list[str]) -> list[int]:
    rx = [re.compile(p) for p in patterns]
    out = []
    for pid, args in cmdlines():
        line = " ".join(args)
        if args and "--kill-pattern" not in line and any(r.search(line) for r in rx):  # never the guard or its shell
            out.append(pid)
    return out


def pipeline_pids() -> list[int]:
    pids = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) == os.getpid():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        args = [a.decode(errors="replace") for a in argv if a]
        if len(args) >= 4 and Path(args[0]).name.startswith("python") and args[1:4] in (["-m", "invariant_mining", "run"],
                                                                                         ["-u", "-m", "invariant_mining"]):
            if "run" in args[1:5]:
                pids.append(int(d.name))
    return pids


def guard(cfg: dict, max_used: int, interval: float, log_path: Path, pause_file: Path | None = None,
          kill_patterns: list[str] | None = None) -> None:
    def log(msg: str) -> None:
        line = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + msg
        with open(log_path, "a") as f:
            f.write(line + "\n")
        print(line, flush=True)

    prev = None
    last_log = 0.0
    kill_patterns = kill_patterns or []
    log(f"guard started: pause at {max_used:,} used (checked every {interval:.0f} s, with a one-interval projection)"
        + (f"; pause file {pause_file}" if pause_file else "") + (f"; kill patterns {kill_patterns}" if kill_patterns else ""))
    while True:
        try:
            used, ent, login = used_now(cfg)
        except Exception as e:  # a failed read never pauses; it is logged
            log(f"WARNING usage read failed: {type(e).__name__}: {e}")
            time.sleep(interval)
            continue
        if ent < 1000:  # the gateway restarting or between logins reports a placeholder quota: ignore it
            log(f"WARNING ignoring an implausible quota reading ({used:,} / {ent:,}, login {login})")
            prev = None
            time.sleep(interval)
            continue
        now = time.time()
        if prev and prev[2] != login:  # another account: start the rate over
            log(f"account changed: {prev[2]} -> {login}")
            prev = None
        rate = 0.0
        if prev and used >= prev[1]:
            rate = (used - prev[1]) / max(1e-6, now - prev[0])
        projected = used + rate * interval * 1.5
        if now - last_log >= 60:
            log(f"{login}: used {used:,} / {ent:,} ({ent - used:,} left), {rate * 60:.0f}/min, runs: {pipeline_pids() or 'none'}")
            last_log = now
        if used >= max_used or projected >= max_used:
            if pause_file:
                pause_file.write_text(f"paused by the credit guard at {used:,} used\n")
            pids = pipeline_pids() + matching_pids(kill_patterns)
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            log(f"PAUSED at {used:,} used (projected {projected:,.0f} >= {max_used:,}): SIGTERM to {pids or 'none'}"
                + (f", pause file {pause_file} created" if pause_file else ""))
            return
        prev = (now, used, login)
        time.sleep(interval)
