"""SQLite state of a run (TECHNICAL.md 4.1). Only the scheduler's main thread writes to it."""

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS trajectories(id TEXT PRIMARY KEY, task_id TEXT, label TEXT, source TEXT, json_path TEXT,
    steps INT, est_tokens INT);
CREATE TABLE IF NOT EXISTS tasks(task_id TEXT PRIMARY KEY, seq INT, p1 TEXT, p2 TEXT, status TEXT, roles_json TEXT,
    f1_job TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS invariants(id TEXT PRIMARY KEY, task_id TEXT, local_id TEXT, observation_json TEXT,
    action TEXT, purpose TEXT, follows_json TEXT, evidence_json TEXT, status TEXT, parent_id TEXT, origin TEXT,
    reword_attempt INT, created_job TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS cells(invariant_id TEXT, trajectory_id TEXT, label TEXT, stage TEXT, status TEXT,
    f2_seen INT, f2_location TEXT, f3_outcome TEXT, f3_action_location TEXT,
    recheck_f2_seen INT, recheck_f2_location TEXT, recheck_f3_outcome TEXT, recheck_f3_action_location TEXT,
    too_narrow INT, too_narrow_location TEXT, final_outcome TEXT, job_ids TEXT, updated REAL,
    PRIMARY KEY(invariant_id, trajectory_id));
CREATE TABLE IF NOT EXISTS triggers(id INTEGER PRIMARY KEY AUTOINCREMENT, invariant_id TEXT, kind TEXT,
    trajectory_id TEXT, label TEXT, alt_location TEXT, status TEXT, stage TEXT, attempt INT, job_running INT DEFAULT 0,
    new_action TEXT, new_purpose TEXT, previous_json TEXT, result TEXT, new_invariant TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS validations(trigger_id INT, attempt INT, trajectory_id TEXT, role TEXT, stage TEXT,
    status TEXT, f2_seen INT, f2_location TEXT, f3_outcome TEXT, f3_action_location TEXT, ok INT,
    PRIMARY KEY(trigger_id, attempt, trajectory_id));
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, kind TEXT, role TEXT, model TEXT, effort TEXT, prompt_sha256 TEXT,
    ref TEXT, input_json TEXT, status TEXT, started REAL, ended REAL, model_steps INT, tokens_in INT, tokens_out INT,
    output_json TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS events(time REAL, kind TEXT, task_id TEXT, invariant_id TEXT, trajectory_id TEXT,
    detail_json TEXT);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
"""


class Store:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(str(path), isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        # No fsync per commit (WAL stays consistent after a process crash; only an OS crash can lose the last commits).
        # A commit fsync took ~0.4 s on the shared disk (2026-11-17), i.e. minutes per run of a few hundred jobs.
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.db.executescript(SCHEMA)

    def q(self, sql: str, *args) -> list[sqlite3.Row]:
        return self.db.execute(sql, args).fetchall()

    def one(self, sql: str, *args):
        rows = self.q(sql, *args)
        return rows[0] if rows else None

    def x(self, sql: str, *args) -> int:
        cur = self.db.execute(sql, args)
        return cur.lastrowid

    def update(self, table: str, where: dict, **values) -> None:
        sets = ", ".join(f"{k}=?" for k in values)
        conds = " AND ".join(f"{k}=?" for k in where)
        self.db.execute(f"UPDATE {table} SET {sets} WHERE {conds}", (*values.values(), *where.values()))

    def event(self, kind: str, task_id=None, invariant_id=None, trajectory_id=None, **detail) -> None:
        self.x("INSERT INTO events VALUES (?,?,?,?,?,?)", time.time(), kind, task_id, invariant_id, trajectory_id,
               json.dumps(detail, ensure_ascii=False))

    def set_meta(self, key: str, value) -> None:
        self.x("INSERT OR REPLACE INTO meta VALUES (?,?)", key, json.dumps(value))

    def get_meta(self, key: str, default=None):
        row = self.one("SELECT value FROM meta WHERE key=?", key)
        return json.loads(row["value"]) if row else default
