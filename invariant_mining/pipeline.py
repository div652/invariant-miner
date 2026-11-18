"""Scheduler (TECHNICAL.md 4.3): runs ready work under a concurrency limit, applies the rules to each finished job, until
nothing is pending. Resumable. Worker threads only run job agents; the main thread does every state change."""

import json
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from . import jobs, rules
from .agent import JobResult, run_agent
from .models import make_conversation
from .store import Store
from .trajectory import Trajectory


class Pipeline:
    def __init__(self, run_dir: Path, cfg: dict, conv_factory=None, log=print):
        self.run_dir = Path(run_dir)
        self.cfg = cfg
        self.store = Store(self.run_dir / "state.sqlite")
        self.log = log
        self._trajs: dict[str, Trajectory] = {}
        self._lock = threading.Lock()
        self.conv_factory = conv_factory or (lambda spec, tools: make_conversation(cfg, spec.model_key, spec.system, spec.user_text, tools))

    def trajectory(self, tid: str) -> Trajectory:
        with self._lock:
            if tid not in self._trajs:
                row = self.store.one("SELECT json_path FROM trajectories WHERE id=?", tid)
                self._trajs[tid] = Trajectory.load(self.run_dir / row["json_path"])
            return self._trajs[tid]

    def _next_job_id(self, kind: str) -> str:
        n = int(self.store.get_meta("job_counter", 0)) + 1
        self.store.set_meta("job_counter", n)
        return f"j{n:06d}-{kind}"

    def _execute(self, job: dict, job_id: str, trajs: dict) -> list[tuple[str, JobResult, jobs.JobSpec]]:
        """Run one job, retrying it as a fresh job on failure (cfg job_retries). Worker thread."""
        attempts = []
        model_key = self.cfg["roles"][job["role"]]
        for a in range(int(self.cfg["job_retries"]) + 1):
            spec = jobs.build(job["kind"], model_key, job["inputs"], trajs)
            jid = job_id if a == 0 else f"{job_id}-retry{a}"
            res = run_agent(spec, self.conv_factory, self.cfg, self.run_dir / "jobs" / jid)
            attempts.append((jid, res, spec))
            if res.ok:
                break
        return attempts

    def _record(self, job: dict, attempts: list) -> None:
        for jid, res, spec in attempts:
            model = self.cfg["models"][spec.model_key]
            self.store.x("INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", jid, job["kind"], job["role"],
                         model["model"], model.get("effort"), spec.prompt_sha256, job["ref"],
                         json.dumps(job["inputs"], ensure_ascii=False), "ok" if res.ok else "error", res.started, res.ended,
                         res.steps, res.tokens_in, res.tokens_out,
                         json.dumps(res.output, ensure_ascii=False) if res.output is not None else None, res.error)

    def reset_running(self) -> None:
        s = self.store
        s.x("UPDATE tasks SET status='pending' WHERE status='running'")
        s.x("UPDATE cells SET status='pending' WHERE status='running'")
        s.x("UPDATE validations SET status='pending' WHERE status='running'")
        s.x("UPDATE triggers SET job_running=0 WHERE job_running=1")

    def run(self, tasks: list[str] | None = None) -> None:
        if tasks:
            self.store.x(f"UPDATE tasks SET status='held' WHERE status='pending' AND task_id NOT IN ({','.join('?' * len(tasks))})", *tasks)
        self.reset_running()
        conc = int(self.cfg["concurrency"])
        inflight = {}
        started = time.time()
        done_jobs = 0
        with ThreadPoolExecutor(max_workers=conc) as pool:
            while True:
                for item in rules.ready_work(self.store, conc - len(inflight),
                                             passing_first=self.cfg.get("check_order", "passing_first") == "passing_first"):
                    job = rules.job_for(self.store, item)
                    trajs = {name: self.trajectory(tid) for name, tid in job["trajs"].items()}
                    job_id = self._next_job_id(job["kind"])
                    fut = pool.submit(self._execute, job, job_id, trajs)
                    inflight[fut] = (item, job)
                if not inflight:
                    break
                done, _ = wait(list(inflight), return_when=FIRST_COMPLETED)
                for fut in done:
                    item, job = inflight.pop(fut)
                    try:
                        attempts = fut.result()
                    except Exception as e:  # a bug in a worker: record as a failed job
                        attempts = []
                        last = JobResult(False, None, f"internal: {type(e).__name__}: {e}", 0, 0, 0, time.time(), time.time())
                    else:
                        self._record(job, attempts)
                        last = attempts[-1][1]
                    rules.apply(self.store, item, last.ok, last.output, last.error, [a[0] for a in attempts], self.trajectory)
                    done_jobs += 1
                    if done_jobs % 10 == 0 or item["type"] == "f1":
                        self.log(f"[{time.strftime('%H:%M:%S')}] {done_jobs} jobs done, {len(inflight)} running, "
                                 f"{time.time() - started:.0f} s; last: {job['kind']} {job['ref']} -> {'ok' if last.ok else 'error'}")
        if tasks:
            self.store.x("UPDATE tasks SET status='pending' WHERE status='held'")
        self.log(f"pipeline finished: {done_jobs} jobs in {time.time() - started:.0f} s")
