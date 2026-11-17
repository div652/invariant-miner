"""Default configuration (TECHNICAL.md 3.1-3.2). A run's config.json overrides any key."""

import copy
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "gateway": {"base_url": "http://127.0.0.1:4141", "key_file": None},  # key_file: else $DSH_BENCH_CAO_KEY_FILE / local.env
    "models": {
        "opus": {"model": "claude-opus-5-5", "api": "anthropic-messages", "effort": "high", "max_tokens": 64000,
                 "prompt_window": 1_000_000},
        "luna": {"model": "gpt-5.6-luna", "api": "openai-responses", "effort": "high", "max_tokens": 64000,
                 "prompt_window": 922_000},
    },
    # which model does each kind of job (DESIGN.md section 4)
    "roles": {"f1_propose": "opus", "f1_reword": "opus", "f2_seen": "luna", "f3_followed": "luna",
              "f2_recheck": "opus", "f3_recheck": "opus", "too_narrow": "opus"},
    "budgets": {"f1_propose": 150, "f1_reword": 60, "f2_seen": 40, "f3_followed": 40, "too_narrow": 40},  # model steps
    "wall_time_s": 1800,          # per job
    "context_guard": 0.6,         # elide old tool results past this share of the model's prompt window
    "max_invalid_submits": 3,
    "job_retries": 1,             # a failed job is retried this many times as a fresh job
    "api_retries": 5,
    "request_timeout_s": 1800,
    "concurrency": 20,
}


def merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(path: Path | None) -> dict:
    return merge(DEFAULT_CONFIG, json.loads(Path(path).read_text()) if path else {})
