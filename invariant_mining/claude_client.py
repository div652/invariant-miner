"""Claude models (Opus 5.5) through the Anthropic SDK, against the CAO gateway's Messages API.

Adaptive thinking with summarized display, effort from the config (high), streaming (large max_tokens), the assistant's
content blocks sent back unchanged each turn (thinking blocks keep their signatures). The gateway rejects the
server-side refusal `fallbacks` parameter (checked 2026-11-17: "Extra inputs are not permitted"), so a refusal fails the
job (the job is retried once, then logged as a job error).

Note: elide() edits earlier tool results; on Opus 5.5 an edit to the history can make earlier thinking blocks unreadable
to the model. It only runs past the context-guard threshold (60% of the window).
"""

import random
import time

import anthropic

from .models import ELIDED, Call, Conversation, ModelError, StepResult, gateway_key


class MessagesConversation(Conversation):
    def __init__(self, cfg: dict, model: dict, system: str, user_text: str, tools: list[dict]):
        self.client = anthropic.Anthropic(base_url=cfg["gateway"]["base_url"].rstrip("/"), api_key=gateway_key(cfg),
                                          max_retries=2, timeout=float(cfg.get("request_timeout_s", 1800)))
        self.model = model
        self.retries = int(cfg.get("api_retries", 5))
        self.system = system
        self.tools = [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in tools]
        self.messages: list[dict] = [{"role": "user", "content": user_text}]
        self.call_names: dict[str, str] = {}
        self.last_tokens = 0
        self.added_chars = len(system) + len(user_text)

    def _create(self):
        last = None
        for attempt in range(self.retries + 1):
            try:
                with self.client.messages.stream(
                        model=self.model["model"], max_tokens=int(self.model.get("max_tokens", 64000)),
                        system=self.system, messages=self.messages, tools=self.tools,
                        thinking={"type": "adaptive", "display": "summarized"},
                        output_config={"effort": self.model.get("effort", "high")}) as stream:
                    return stream.get_final_message()
            except (anthropic.BadRequestError, anthropic.AuthenticationError, anthropic.PermissionDeniedError,
                    anthropic.NotFoundError) as e:
                raise ModelError(f"{type(e).__name__}: {e}")
            except anthropic.APIError as e:  # rate limits, 5xx, connection errors, mid-stream errors
                last = ModelError(f"{type(e).__name__}: {e}")
            if attempt < self.retries:
                time.sleep(min(60, 2 ** attempt * 2) + random.uniform(0, 1))
        raise last

    def step(self) -> StepResult:
        raws = []
        while True:
            resp = self._create()
            self.messages.append({"role": "assistant", "content": resp.content})
            raw = resp.to_dict()
            for block in raw.get("content", []):
                block.pop("signature", None)
            raws.append(raw)
            if resp.stop_reason != "pause_turn":
                break
        if resp.stop_reason == "refusal":
            details = getattr(resp, "stop_details", None)
            raise ModelError(f"refusal: {getattr(details, 'category', None)} {getattr(details, 'explanation', '')}")
        if resp.stop_reason == "max_tokens":
            raise ModelError("the response was cut at max_tokens")
        calls, texts, reasoning = [], [], []
        for b in resp.content:
            if b.type == "tool_use":
                calls.append(Call(b.id, b.name, b.input))
                self.call_names[b.id] = f"{b.name}({str(b.input)[:200]})"
            elif b.type == "text":
                texts.append(b.text)
            elif b.type == "thinking":
                reasoning.append(getattr(b, "thinking", "") or "")
        u = resp.usage
        tin = int(u.input_tokens or 0) + int(getattr(u, "cache_read_input_tokens", 0) or 0) + int(getattr(u, "cache_creation_input_tokens", 0) or 0)
        self.last_tokens = tin + int(u.output_tokens or 0)
        self.added_chars = 0
        return StepResult(calls, "\n".join(texts), "\n".join(reasoning), tin, int(u.output_tokens or 0),
                          {"responses": raws} if len(raws) > 1 else raws[0])

    def add_results(self, results: list) -> None:
        blocks = [{"type": "tool_result", "tool_use_id": cid, "content": text, "is_error": bool(err)} for cid, text, err in results]
        self.messages.append({"role": "user", "content": blocks})
        self.added_chars += sum(len(t) for _, t, _ in results)

    def add_user(self, text: str) -> None:
        last = self.messages[-1]
        if last["role"] == "user" and isinstance(last["content"], list):
            last["content"].append({"type": "text", "text": text})
        else:
            self.messages.append({"role": "user", "content": text})
        self.added_chars += len(text)

    def est_tokens(self) -> int:
        return self.last_tokens + self.added_chars // 4

    def elide(self, target_tokens: int, keep: tuple = ("read_notes",)) -> int:
        n = 0
        for msg in self.messages:
            if msg["role"] != "user" or not isinstance(msg["content"], list):
                continue
            for block in msg["content"]:
                if self.est_tokens() <= target_tokens:
                    return n
                if block.get("type") != "tool_result" or str(block.get("content", "")).startswith("[elided"):
                    continue
                what = self.call_names.get(block["tool_use_id"], "a tool result")
                if what.split("(")[0] in keep:
                    continue
                removed = len(str(block["content"]))
                block["content"] = ELIDED.format(what=what)
                self.last_tokens = max(0, self.last_tokens - removed // 4)
                n += 1
        return n
