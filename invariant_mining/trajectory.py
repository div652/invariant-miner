"""DSH session log (session.v2.jsonl) -> normalized trajectory: a flat list of items in the order the agent saw them.

Locations (TECHNICAL.md 2.3): `sys`, `tools`, `uN` (N-th user message), `sN.r` (reasoning of step N; a second reasoning
block in the same step is `sN.r2`), `sN.t` (text), `sN.cK` (K-th tool call of step N), `sN.oK` (its output); optional
`#offset` (character offset inside the item); `start` = before everything. Order = position in `items`.
"""

import json
import re
from pathlib import Path

LOC_RE = re.compile(r"^(start|sys|tools|u\d+|s\d+\.(?:r\d*|t\d*|c\d+|o\d+))(?:#(\d+))?$")


class LocationError(ValueError):
    pass


class Trajectory:
    def __init__(self, data: dict):
        self.data = data
        self.id = data["id"]
        self.task_id = data.get("task_id")
        self.label = data.get("label")
        self.meta = data.get("meta", {})
        self.items = data["items"]
        self.index = {item["loc"]: i for i, item in enumerate(self.items)}

    @classmethod
    def load(cls, path: Path) -> "Trajectory":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def save(self, path: Path) -> None:
        Path(path).write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    # --- locations ------------------------------------------------------------------------------------------------
    def position(self, loc: str) -> tuple[int, int]:
        """(item index, offset) of a location; `start` is (-1, 0). Raises LocationError."""
        if not isinstance(loc, str):
            raise LocationError(f"location must be a string, got {loc!r}")
        loc = loc.strip().strip("`")
        if "#" in loc and not loc.split("#", 1)[1].isdigit():
            loc = loc.split("#", 1)[0]  # a malformed offset ("sys#?") means the item itself
        m = LOC_RE.match(loc)
        if not m:
            raise LocationError(f"{loc!r} is not a location (examples: sys, tools, u1, s3.r, s3.t, s3.c1, s3.o1, s3.o1#1200)")
        base, offset = m.group(1), int(m.group(2) or 0)
        if base == "start":
            return (-1, 0)
        if base not in self.index:
            raise LocationError(f"{base!r} does not exist in trajectory {self.id}")
        i = self.index[base]
        if offset > len(self.items[i].get("text", "")):
            raise LocationError(f"offset {offset} is past the end of {base} ({len(self.items[i].get('text', ''))} characters)")
        return (i, offset)

    def valid(self, loc: str) -> bool:
        try:
            self.position(loc)
            return True
        except LocationError:
            return False

    def before(self, a: str, b: str) -> bool:
        """a strictly before b (by item, then offset)."""
        return self.position(a) < self.position(b)

    def item_order(self, loc: str) -> int:
        return self.position(loc)[0]

    # --- sizes ----------------------------------------------------------------------------------------------------
    def steps(self) -> list[int]:
        out = []
        for item in self.items:
            m = re.match(r"^s(\d+)\.", item["loc"])
            if m and (not out or out[-1] != int(m.group(1))):
                out.append(int(m.group(1)))
        return out

    def total_chars(self) -> int:
        return sum(len(item.get("text", "")) for item in self.items)

    def est_tokens(self) -> int:
        return self.meta.get("est_tokens") or self.total_chars() // 4


def _text_of(content) -> str:
    parts = []
    for c in content or []:
        if c.get("type") == "text":
            parts.append(c.get("text", ""))
        elif c.get("type") == "image":
            parts.append("[image]")
    return "\n".join(parts)


def find_session_log(path: Path) -> Path:
    """A session.v2.jsonl path, or a directory holding exactly one (e.g. a run's dsh-home)."""
    path = Path(path)
    if path.is_file():
        return path
    found = sorted(path.rglob("session.v2.jsonl"))
    if len(found) != 1:
        raise FileNotFoundError(f"{path}: expected exactly one session.v2.jsonl, found {len(found)}")
    return found[0]


def parse_session(path: Path, traj_id: str, task_id: str | None = None, label: str | None = None) -> Trajectory:
    path = find_session_log(path)
    header = None
    context_window = None
    body: list[dict] = []
    user_n = 0
    counters: dict[int, dict[str, int]] = {}
    call_loc: dict[str, tuple[int, int]] = {}
    max_context = 0
    with open(path, encoding="utf-8", newline="\n") as f:  # split on \n only (U+2028 can occur inside strings)
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            kind = rec.get("type")
            data = rec.get("data") or {}
            if kind == "request/header" and header is None:
                header = data.get("header") or {}
            elif kind == "request/context":
                context_window = data.get("contextWindow")
            elif kind == "user/message":
                user_n += 1
                body.append({"loc": f"u{user_n}", "kind": "user", "text": _text_of(data.get("content"))})
            elif kind == "assistant/message":
                n = int(data["step"])
                c = counters.setdefault(n, {"r": 0, "t": 0, "k": 0})
                usage = data.get("usage") or {}
                max_context = max(max_context, int(usage.get("totalTokens") or 0))
                for block in (data.get("message") or {}).get("content", []):
                    btype = block.get("type")
                    if btype in ("reasoning", "text"):
                        text = block.get("text") or ""
                        if not text.strip():
                            continue
                        key = "r" if btype == "reasoning" else "t"
                        c[key] += 1
                        loc = f"s{n}.{key}" + ("" if c[key] == 1 else str(c[key]))
                        body.append({"loc": loc, "kind": "reasoning" if key == "r" else "text", "text": text})
                    elif btype == "tool-call":
                        c["k"] += 1
                        call_loc[block.get("id")] = (n, c["k"])
                        args = block.get("arguments")
                        if not isinstance(args, str):
                            args = json.dumps(args, ensure_ascii=False)
                        body.append({"loc": f"s{n}.c{c['k']}", "kind": "call", "name": block.get("name"), "text": args})
            elif kind == "tool/result":
                n_default = int(data.get("step") or 0)
                for block in (data.get("message") or {}).get("content", []):
                    if block.get("type") != "tool-result":
                        continue
                    where = call_loc.get(block.get("toolCallId"))
                    if where is None:  # a result without a recorded call: give it its own number in its step
                        c = counters.setdefault(n_default, {"r": 0, "t": 0, "k": 0})
                        c["k"] += 1
                        where = (n_default, c["k"])
                    inner = block.get("content")
                    text = inner if isinstance(inner, str) else _text_of(inner)
                    body.append({"loc": f"s{where[0]}.o{where[1]}", "kind": "output", "text": text,
                                 "is_error": bool(block.get("isError"))})
    header = header or {}
    tools_text = "\n\n".join(
        f"## {t.get('name')}\n{t.get('description', '')}\nParameters: {json.dumps(t.get('parameters', {}), ensure_ascii=False)}"
        for t in header.get("tools", []))
    items = [{"loc": "sys", "kind": "system", "text": header.get("system", "")},
             {"loc": "tools", "kind": "tools", "text": tools_text}] + body
    config = header.get("config") or {}
    data = {"id": traj_id, "task_id": task_id, "label": label, "source": str(path),
            "meta": {"model": config.get("model"), "effort": config.get("reasoningEffort"),
                     "context_window": context_window, "steps": len(counters),
                     "est_tokens": max_context or sum(len(i["text"]) for i in items) // 4},
            "items": items}
    return Trajectory(data)
