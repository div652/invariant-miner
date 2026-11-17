"""Model conversations for job agents (TECHNICAL.md 3.2), through the CAO gateway.

A Conversation holds one job's history in the provider's own format: step() calls the model and appends its output;
add_results() appends tool results; elide() shortens old tool results (context guard). GPT models use the OpenAI
Responses API over plain HTTP here; Claude models use the Anthropic SDK (claude_client.py).
"""

import json
import os
import random
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ELIDED = "[elided to keep the context short: {what}; call the tool again if you need it]"


class ModelError(Exception):
    """The model call failed after retries, or returned something the loop cannot continue from."""


@dataclass
class Call:
    id: str
    name: str
    arguments: object  # dict or JSON string


@dataclass
class StepResult:
    calls: list
    text: str = ""
    reasoning: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    raw: dict = field(default_factory=dict)  # sanitized response for the transcript


class Conversation:
    def step(self) -> StepResult: ...
    def add_results(self, results: list) -> None: ...  # [(call_id, text, is_error)]
    def add_user(self, text: str) -> None: ...
    def est_tokens(self) -> int: ...
    def elide(self, target_tokens: int, keep: tuple = ("read_notes",)) -> int: ...


def gateway_key(cfg: dict) -> str:
    path = cfg.get("gateway", {}).get("key_file") or os.environ.get("DSH_BENCH_CAO_KEY_FILE")
    if not path:
        env = Path.home() / ".config/dsh-bench/local.env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.strip().startswith("DSH_BENCH_CAO_KEY_FILE="):
                    path = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not path:
        raise ModelError("no gateway key: set gateway.key_file in the config or DSH_BENCH_CAO_KEY_FILE")
    path = os.path.expanduser(os.path.expandvars(path))
    return Path(path).read_text().strip()


# --- OpenAI Responses API (GPT models) ----------------------------------------------------------------------------------
RETRY_STATUS = {400, 408, 409, 429, 500, 502, 503, 504}  # 400: OpenAI sometimes refuses a tool schema mid-run (models/luna-cao.json)


class ResponsesConversation(Conversation):
    def __init__(self, cfg: dict, model: dict, system: str, user_text: str, tools: list[dict]):
        self.url = cfg["gateway"]["base_url"].rstrip("/") + "/v1/responses"
        self.key = gateway_key(cfg)
        self.model = model
        self.retries = int(cfg.get("api_retries", 5))
        self.timeout = float(cfg.get("request_timeout_s", 1800))
        self.system = system
        self.tools = [{"type": "function", "name": t["name"], "description": t["description"],
                       "parameters": t["parameters"], "strict": False} for t in tools]
        self.input: list[dict] = [{"role": "user", "content": [{"type": "input_text", "text": user_text}]}]
        self.call_names: dict[str, str] = {}
        self.last_tokens = 0
        self.added_chars = len(system) + len(user_text) + len(json.dumps(self.tools))

    def _post(self, body: dict) -> dict:
        data = json.dumps(body).encode()
        last = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(self.url, data=data, headers={
                "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    out = json.loads(resp.read())
                if not out.get("output"):
                    raise ModelError(f"empty response: {json.dumps(out)[:300]}")
                return out
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:500]
                last = ModelError(f"HTTP {e.code}: {detail}")
                if e.code not in RETRY_STATUS:
                    raise last
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, json.JSONDecodeError, ModelError) as e:
                last = e if isinstance(e, ModelError) else ModelError(f"{type(e).__name__}: {e}")
            if attempt < self.retries:
                time.sleep(min(60, 2 ** attempt * 2) + random.uniform(0, 1))
        raise last

    def step(self) -> StepResult:
        body = {"model": self.model["model"], "instructions": self.system, "input": self.input, "tools": self.tools,
                "reasoning": {"effort": self.model.get("effort", "high"), "summary": "auto"},
                "include": ["reasoning.encrypted_content"], "store": False,
                "max_output_tokens": int(self.model.get("max_tokens", 64000))}
        out = self._post(body)
        items = out.get("output", [])
        self.input.extend(items)  # sent back as-is next turn (reasoning items with their encrypted content)
        calls, texts, reasoning = [], [], []
        for it in items:
            if it.get("type") == "function_call":
                calls.append(Call(it.get("call_id"), it.get("name"), it.get("arguments")))
                self.call_names[it.get("call_id")] = f"{it.get('name')}({str(it.get('arguments'))[:200]})"
            elif it.get("type") == "message":
                texts += [c.get("text", "") for c in it.get("content", []) if c.get("type") == "output_text"]
            elif it.get("type") == "reasoning":
                reasoning += [s.get("text", "") for s in it.get("summary", []) or []]
        usage = out.get("usage") or {}
        self.last_tokens = int(usage.get("input_tokens") or 0) + int(usage.get("output_tokens") or 0)
        self.added_chars = 0
        raw = {"model": out.get("model"), "usage": usage, "output": [
            {k: v for k, v in it.items() if k != "encrypted_content"} for it in items]}
        return StepResult(calls, "\n".join(texts), "\n".join(reasoning), int(usage.get("input_tokens") or 0),
                          int(usage.get("output_tokens") or 0), raw)

    def add_results(self, results: list) -> None:
        for call_id, text, _err in results:
            self.input.append({"type": "function_call_output", "call_id": call_id, "output": text})
            self.added_chars += len(text)

    def add_user(self, text: str) -> None:
        self.input.append({"role": "user", "content": [{"type": "input_text", "text": text}]})
        self.added_chars += len(text)

    def est_tokens(self) -> int:
        return self.last_tokens + self.added_chars // 4

    def elide(self, target_tokens: int, keep: tuple = ("read_notes",)) -> int:
        n = 0
        for it in self.input:
            if self.est_tokens() <= target_tokens:
                break
            if it.get("type") != "function_call_output" or it.get("output", "").startswith("[elided"):
                continue
            what = self.call_names.get(it.get("call_id"), "a tool result")
            if what.split("(")[0] in keep:
                continue
            removed = len(it["output"])
            it["output"] = ELIDED.format(what=what)
            self.last_tokens = max(0, self.last_tokens - removed // 4)
            n += 1
        return n


def make_conversation(cfg: dict, model_key: str, system: str, user_text: str, tools: list[dict]) -> Conversation:
    model = cfg["models"][model_key]
    if model["api"] == "openai-responses":
        return ResponsesConversation(cfg, model, system, user_text, tools)
    if model["api"] == "anthropic-messages":
        from .claude_client import MessagesConversation  # needs the anthropic SDK (work/im-venv)
        return MessagesConversation(cfg, model, system, user_text, tools)
    raise ModelError(f"unknown api {model['api']!r} for model {model_key}")
