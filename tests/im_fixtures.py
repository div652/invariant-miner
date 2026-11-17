"""Shared fixtures for the invariant_mining tests: synthetic DSH session logs and scripted model conversations."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from invariant_mining.models import Call, Conversation, StepResult  # noqa: E402


def write_session(path: Path, task: str, steps: list[dict], extra_user_after: dict | None = None) -> Path:
    """steps: [{"reasoning": str, "text": str, "calls": [(name, args_dict, output_str), ...]}]. A synthetic session log
    in DSH's session.v2 format, with some records the parser must ignore."""
    path.parent.mkdir(parents=True, exist_ok=True)
    seq = 0
    recs = []

    def rec(kind, data=None, **kw):
        nonlocal seq
        seq += 1
        recs.append({"type": kind, "seq": seq, "time": 1000 + seq, **({"data": data} if data is not None else {}), **kw})

    rec("session", None, version=2, id="session-test")
    rec("agent/inbox/spliced", {"target": "next-turn", "inserted": [{"content": [{"type": "text", "text": task}]}]})
    rec("turn/start", {"turn": 1})
    rec("user/message", {"content": [{"type": "text", "text": task}], "role": "user"})
    rec("user/message", {"content": [{"type": "text", "text": "Current runtime context: workspace-isolated."}], "role": "user"})
    rec("request/header", {"header": {"config": {"model": "test-model", "reasoningEffort": "high"}, "system": "You are a test agent.",
                                      "tools": [{"name": "bash", "description": "Run a command.", "parameters": {"type": "object"}},
                                                {"name": "read", "description": "Read a file.", "parameters": {"type": "object"}}]}})
    rec("request/context", {"contextWindow": 922000})
    n_call = 0
    for n, st in enumerate(steps, 1):
        rec("step/start", {"turn": 1, "step": n})
        content = []
        if st.get("reasoning"):
            content.append({"type": "reasoning", "text": st["reasoning"]})
        if st.get("text"):
            content.append({"type": "text", "text": st["text"]})
        ids = []
        for name, args, _out in st.get("calls", []):
            n_call += 1
            ids.append(f"call_{n_call}")
            content.append({"type": "tool-call", "id": ids[-1], "name": name, "arguments": json.dumps(args)})
        rec("assistant/message", {"turn": 1, "step": n, "message": {"role": "assistant", "content": content,
                                  "source": {"replayState": {"blocks": [{"type": "reasoning", "thinkingSignature": "x" * 50}]}}},
                                  "usage": {"totalTokens": 1000 * n}, "stream": [{"type": "chunk"}]})
        for cid, (name, args, out) in zip(ids, st.get("calls", [])):
            rec("tool/call", {"turn": 1, "step": n, "callId": cid, "name": name, "arguments": json.dumps(args)})
            rec("tool/result", {"turn": 1, "step": n, "message": {"content": [{"type": "tool-result", "toolCallId": cid,
                                "content": [{"type": "text", "text": out}], "isError": out.startswith("ERROR")}]}})
        if extra_user_after and n in extra_user_after:
            rec("user/message", {"content": [{"type": "text", "text": extra_user_after[n]}], "role": "user"})
        rec("step/end", {"turn": 1, "step": n})
    rec("turn/end", {"turn": 1, "reason": {"kind": "completed"}})
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    return path


def three_steps(tag: str) -> list[dict]:
    return [
        {"reasoning": f"**Plan** I will list the files for {tag}.", "calls": [("bash", {"command": "ls"}, f"a.txt\nb.txt\n{tag}")]},
        {"reasoning": "**Search** grep for the keyword.", "text": "Searching.",
         "calls": [("bash", {"command": "grep -c key *"}, "a.txt:3\nb.txt:7"), ("read", {"path": "b.txt"}, "B" * 5000)]},
        {"reasoning": "**Answer** b.txt has most hits.", "calls": [("bash", {"command": "echo done"}, "done")]},
    ]


class ScriptedConversation(Conversation):
    """Each step returns the next scripted list of calls; a script entry may be a function(conv) -> list[Call]."""

    def __init__(self, script):
        self.script = list(script)
        self.results, self.users = [], []
        self.tokens = 100
        self.elided = 0

    def step(self):
        entry = self.script.pop(0)
        calls = entry(self) if callable(entry) else entry
        return StepResult(calls=calls, tokens_in=10, tokens_out=5, raw={"scripted": [c.name for c in calls]})

    def add_results(self, results):
        self.results.append(results)
        self.tokens += sum(len(t) for _, t, _ in results) // 4

    def add_user(self, text):
        self.users.append(text)

    def est_tokens(self):
        return self.tokens

    def elide(self, target_tokens, keep=("read_notes",)):
        self.elided += 1
        self.tokens = target_tokens
        return 1


def call(name, **args):
    call.n = getattr(call, "n", 0) + 1
    return Call(f"c{call.n}", name, args)


class Checks:
    def __init__(self, name):
        self.name, self.failed, self.n = name, 0, 0

    def check(self, cond, what):
        self.n += 1
        if cond:
            print(f"PASS  {what}")
        else:
            self.failed += 1
            print(f"FAIL  {what}")

    def done(self):
        print(f"{self.name}: {self.n - self.failed}/{self.n} passed")
        sys.exit(1 if self.failed else 0)
