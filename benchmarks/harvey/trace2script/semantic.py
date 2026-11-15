"""The semantic layer: the decisions an agent made between tool calls, as named, testable functions.

In a trajectory script, a judgement step (which files to open, whether an item qualifies, what to write) is a call
to a function decorated with @semantic and given the decision the model actually made:

    @semantic
    def top_series(count_output: str, n: int = 5) -> list[str]:
        '''The client series to name: the n largest by matter count, ties at the cut kept.'''
        ...                                   # version-0 implementation: plain code, imperfect by design

    series = top_series(s8_1, recorded=["1008", "1025", "1038", "1016", "1017", "1018"])

The function always computes its own answer. In replay mode the call returns the recorded decision, so the script
reproduces the run exactly and the log shows where the implementation would have decided otherwise; in live mode it
returns its own answer, so the script becomes a solver whose later calls follow those decisions. Every call is
logged (semantic.jsonl): function, mode, recorded, computed, agreement.
"""

from __future__ import annotations

import functools
import json

MISSING = object()
_mode = "replay"
_log = None


def configure(mode: str, log_path=None) -> None:
    global _mode, _log
    if mode not in ("replay", "live"):
        raise ValueError(f"mode must be replay or live, not {mode!r}")
    _mode = mode
    _log = open(log_path, "w") if log_path else None


def close() -> None:
    global _log
    if _log:
        _log.close()
    _log = None


def mode() -> str:
    return _mode


def _short(v, n: int = 400):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + f"... [{len(s)} chars]"


def semantic(fn):
    @functools.wraps(fn)
    def wrapper(*args, recorded=MISSING, **kwargs):
        error = None
        try:
            computed = fn(*args, **kwargs)
        except Exception as e:  # an imperfect implementation must not stop a replay
            computed, error = None, f"{type(e).__name__}: {e}"
        has_rec = recorded is not MISSING
        value = recorded if (_mode == "replay" and has_rec) else computed
        if _mode == "live" and error is not None:
            raise RuntimeError(f"{fn.__name__}: {error}")
        if _log:
            _log.write(json.dumps({"function": fn.__name__, "mode": _mode, "agrees": (computed == recorded) if has_rec else None,
                                   "recorded": _short(recorded) if has_rec else None, "computed": _short(computed),
                                   "error": error}, ensure_ascii=False) + "\n")
            _log.flush()
        return value
    wrapper.semantic = True
    return wrapper
