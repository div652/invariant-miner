"""The read-only trajectory tools of a job agent (TECHNICAL.md 3.3). Nothing here can touch anything but the trajectories
and the job's notes file. In F1 every trajectory tool takes `run` ("A" = P1, "B" = P2)."""

import json
import re
from pathlib import Path

from .trajectory import LocationError, Trajectory

READ_PAGE = 20_000       # read_context / read_output: characters per call
STEP_ARG_CAP = 4_000     # read_steps: tool-call arguments shown
STEP_OUT_CAP = 2_000     # read_steps: tool outputs shown
STEPS_CALL_CAP = 40_000  # read_steps: characters per call
SEARCH_CONTEXT = 100     # characters on each side of a search hit


class ToolError(Exception):
    pass


def _clip(text: str, n: int) -> str:
    text = text.replace("\r", "")
    return text if len(text) <= n else text[:n] + f"… ({len(text) - n:,} more characters)"


def _one_line(text: str, n: int) -> str:
    return _clip(re.sub(r"\s+", " ", text).strip(), n)


class ToolBox:
    def __init__(self, trajectories: dict[str, Trajectory], notes_path: Path, submit_schema: dict, submit_description: str):
        self.trajs = trajectories
        self.multi = len(trajectories) > 1
        self.notes_path = Path(notes_path)
        self.submit_schema = submit_schema
        self.submit_description = submit_description
        self.steps_read = {name: set() for name in trajectories}  # steps shown in full by read_steps (F1 coverage)

    # --- definitions (provider-neutral: name, description, JSON-schema parameters) ------------------------------------
    def _with_run(self, props: dict, required: list[str]) -> dict:
        if self.multi:
            props = {"run": {"type": "string", "enum": sorted(self.trajs), "description": "Which run: " +
                             ", ".join(f"{k} = {v.id}" for k, v in sorted(self.trajs.items()))}, **props}
            required = ["run"] + required
        return {"type": "object", "properties": props, "required": required}

    def definitions(self) -> list[dict]:
        return [
            {"name": "overview", "description": "Sizes of the trajectory, its user messages (start of each) and one line per "
             "step: the start of its reasoning, each tool call (name + start of its arguments) and the size of each output.",
             "parameters": self._with_run({}, [])},
            {"name": "read_context", "description": "Read the system prompt (`sys`), the tool descriptions (`tools`) or a "
             f"user message (`u1`, `u2`, ...), paged ({READ_PAGE:,} characters per call).",
             "parameters": self._with_run({"part": {"type": "string", "description": "sys, tools or uN"},
                                           "offset": {"type": "integer", "description": "start character, default 0"}},
                                          ["part"])},
            {"name": "read_steps", "description": "Read steps from_step..to_step in order: reasoning and text in full, tool "
             f"calls (arguments up to {STEP_ARG_CAP:,} characters), outputs cut to {STEP_OUT_CAP:,} characters (read the "
             f"rest with read_output). At most {STEPS_CALL_CAP:,} characters per call.",
             "parameters": self._with_run({"from_step": {"type": "integer"}, "to_step": {"type": "integer"}},
                                          ["from_step", "to_step"])},
            {"name": "read_output", "description": f"Read one item (e.g. s7.o2, s7.c1, s7.r, u1) from a character offset, at most "
             f"{READ_PAGE:,} characters per call.",
             "parameters": self._with_run({"loc": {"type": "string"}, "offset": {"type": "integer", "description": "default 0"},
                                           "length": {"type": "integer", "description": f"default and maximum {READ_PAGE}"}},
                                          ["loc"])},
            {"name": "search", "description": "Case-insensitive search over every item. Returns the total number of matches "
             "and, for the first max_hits, their location (loc#offset) with the text around them.",
             "parameters": self._with_run({"pattern": {"type": "string"},
                                           "regex": {"type": "boolean", "description": "pattern is a regular expression (default false: plain text)"},
                                           "kinds": {"type": "array", "items": {"type": "string", "enum": ["system", "tools", "user", "reasoning", "text", "call", "output"]},
                                                     "description": "only these item kinds (default: all)"},
                                           "max_hits": {"type": "integer", "description": "default 50"}},
                                          ["pattern"])},
            {"name": "note", "description": "Append a note to your notes (kept when old tool results are removed from your context).",
             "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
            {"name": "read_notes", "description": "Read all your notes.",
             "parameters": {"type": "object", "properties": {}, "required": []}},
            {"name": "submit", "description": self.submit_description, "parameters": self.submit_schema},
        ]

    # --- execution --------------------------------------------------------------------------------------------------
    def _traj(self, args: dict) -> Trajectory:
        if not self.multi:
            return next(iter(self.trajs.values()))
        run = args.get("run")
        if run not in self.trajs:
            raise ToolError(f"run must be one of {sorted(self.trajs)}")
        return self.trajs[run]

    def execute(self, name: str, args: dict) -> str:
        if not isinstance(args, dict):
            raise ToolError("arguments must be a JSON object")
        fn = {"overview": self.overview, "read_context": self.read_context, "read_steps": self.read_steps,
              "read_output": self.read_output, "search": self.search, "note": self.note,
              "read_notes": self.read_notes}.get(name)
        if fn is None:
            raise ToolError(f"unknown tool {name!r}")
        try:
            return fn(args)
        except LocationError as e:
            raise ToolError(str(e))
        except (TypeError, ValueError) as e:
            raise ToolError(f"bad arguments for {name}: {e}")

    def overview(self, args: dict) -> str:
        t = self._traj(args)
        lines = [f"Trajectory {t.id}: {len(t.items)} items, {len(t.steps())} steps, ~{t.est_tokens():,} tokens "
                 f"({t.total_chars():,} characters)."]
        for item in t.items:
            if item["kind"] in ("system", "tools"):
                lines.append(f"{item['loc']}: {len(item['text']):,} characters")
        current = None
        step_line: list[str] = []

        def flush():
            if current is not None:
                lines.append(f"s{current}: " + " | ".join(step_line))

        for item in t.items:
            loc, kind, text = item["loc"], item["kind"], item.get("text", "")
            if kind == "user":
                flush()
                current, step_line = None, []
                lines.append(f"{loc} (user message, {len(text):,} characters): {_one_line(text, 300)}")
                continue
            m = re.match(r"^s(\d+)\.(.*)$", loc)
            if not m:
                continue
            n = int(m.group(1))
            if n != current:
                flush()
                current, step_line = n, []
            if kind == "reasoning":
                step_line.append(f"{loc} reasoning: {_one_line(text, 150)}")
            elif kind == "text":
                step_line.append(f"{loc} text: {_one_line(text, 150)}")
            elif kind == "call":
                step_line.append(f"{loc} {item.get('name')}({_one_line(text, 100)})")
            elif kind == "output":
                step_line.append(f"{loc} {len(text):,} chars" + (" ERROR" if item.get("is_error") else ""))
        flush()
        return "\n".join(lines)

    def _name(self, t: Trajectory) -> str:
        return next(k for k, v in self.trajs.items() if v is t)

    def unread_steps(self) -> dict[str, str]:
        """Steps of each trajectory not yet shown by read_steps, as ranges ("13-17, 30")."""
        out = {}
        for name, t in self.trajs.items():
            missing = [n for n in t.steps() if n not in self.steps_read[name]]
            if missing:
                ranges, start = [], missing[0]
                for a, b in zip(missing, missing[1:] + [None]):
                    if b != a + 1:
                        ranges.append(str(start) if start == a else f"{start}-{a}")
                        start = b
                out[name] = ", ".join(ranges)
        return out

    def read_context(self, args: dict) -> str:
        t = self._traj(args)
        part = str(args.get("part", ""))
        if not (part in ("sys", "tools") or re.fullmatch(r"u\d+", part)) or part not in t.index:
            raise ToolError(f"part must be sys, tools or an existing user message (u1, u2, ...), got {part!r}")
        return self._page(t, part, int(args.get("offset") or 0), READ_PAGE)

    def _page(self, t: Trajectory, loc: str, offset: int, length: int) -> str:
        text = t.items[t.index[loc]].get("text", "")
        length = max(1, min(int(length), READ_PAGE))
        offset = max(0, offset)
        chunk = text[offset:offset + length]
        end = offset + len(chunk)
        tail = f"\n[{loc} characters {offset:,}-{end:,} of {len(text):,}" + (
            f"; continue with offset={end}]" if end < len(text) else "; end]")
        return chunk + tail

    def read_steps(self, args: dict) -> str:
        t = self._traj(args)
        a, b = int(args["from_step"]), int(args["to_step"])
        if b < a:
            raise ToolError("to_step must be >= from_step")
        idx = [i for i, item in enumerate(t.items) if (m := re.match(r"^s(\d+)\.", item["loc"])) and a <= int(m.group(1)) <= b]
        if not idx:
            raise ToolError(f"no steps in {a}..{b}; the trajectory has steps {t.steps()[:1]}..{t.steps()[-1:]}")
        out, size = [], 0
        for i in range(idx[0], idx[-1] + 1):
            item = t.items[i]
            loc, kind, text = item["loc"], item["kind"], item.get("text", "")
            if kind == "call":
                block = f"[{loc}] call {item.get('name')}\n{_clip(text, STEP_ARG_CAP)}"
            elif kind == "output":
                extra = f"; read the rest with read_output(loc='{loc}', offset={STEP_OUT_CAP})" if len(text) > STEP_OUT_CAP else ""
                block = f"[{loc}] output ({len(text):,} characters{', ERROR' if item.get('is_error') else ''}{extra})\n{_clip(text, STEP_OUT_CAP)}"
            else:
                block = f"[{loc}] {kind}\n{text}"
            if size + len(block) > STEPS_CALL_CAP and out:
                m = re.match(r"^s(\d+)\.", loc)
                out.append(f"[stopped at {loc}: {STEPS_CALL_CAP:,}-character limit; continue with read_steps(from_step={m.group(1) if m else a}, ...)]")
                break
            out.append(block)
            size += len(block)
            if (m := re.match(r"^s(\d+)\.", loc)):
                self.steps_read[self._name(t)].add(int(m.group(1)))
        return "\n\n".join(out)

    def read_output(self, args: dict) -> str:
        t = self._traj(args)
        loc = str(args.get("loc", "")).split("#")[0]
        if loc not in t.index:
            raise ToolError(f"{loc!r} does not exist in this trajectory")
        return self._page(t, loc, int(args.get("offset") or 0), int(args.get("length") or READ_PAGE))

    def search(self, args: dict) -> str:
        t = self._traj(args)
        pattern = str(args.get("pattern", ""))
        if not pattern:
            raise ToolError("pattern is empty")
        try:
            rx = re.compile(pattern if args.get("regex") else re.escape(pattern), re.IGNORECASE)
        except re.error as e:
            raise ToolError(f"bad regular expression: {e}")
        kinds = set(args.get("kinds") or [])
        max_hits = max(1, min(int(args.get("max_hits") or 50), 200))
        hits, total = [], 0
        for item in t.items:
            if kinds and item["kind"] not in kinds:
                continue
            text = item.get("text", "")
            for m in rx.finditer(text):
                total += 1
                if len(hits) < max_hits:
                    s, e = max(0, m.start() - SEARCH_CONTEXT), min(len(text), m.end() + SEARCH_CONTEXT)
                    hits.append(f"{item['loc']}#{m.start()}: …{_one_line(text[s:e], 2 * SEARCH_CONTEXT + 200)}…")
        head = f"{total:,} matches" + (f" (first {len(hits)} shown)" if total > len(hits) else "")
        return head + ("\n" + "\n".join(hits) if hits else "")

    def note(self, args: dict) -> str:
        text = str(args.get("text", "")).strip()
        if not text:
            raise ToolError("note text is empty")
        with open(self.notes_path, "a", encoding="utf-8") as f:
            f.write(text + "\n---\n")
        count = self.notes_path.read_text(encoding="utf-8").count("\n---\n")
        return f"noted ({count} notes)"

    def read_notes(self, args: dict) -> str:
        if not self.notes_path.exists():
            return "(no notes yet)"
        return self.notes_path.read_text(encoding="utf-8")


def parse_arguments(raw) -> dict:
    """Tool-call arguments from a model: a dict, or a JSON string."""
    if isinstance(raw, dict):
        return raw
    if raw is None or raw == "":
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("arguments must be a JSON object")
    return value
