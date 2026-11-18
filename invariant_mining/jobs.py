"""Job kinds (DESIGN.md section 4; TECHNICAL.md 3.4): the prompt, the user message, the submit schema and its validator.

Kinds: f1_propose, f1_reword, f2_seen, f3_followed, too_narrow. The Opus re-check runs f2_seen / f3_followed with
another model; the prompts are the same.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .trajectory import LocationError, Trajectory

PROMPTS = Path(__file__).parent / "prompts"
SOURCES = ["environment", "task", "tool_result", "reasoning"]
F3_OUTCOMES = ["followed", "not_followed", "only_before", "pinning_wrong"]
QUOTE_MAX = 300
KINDS = ["f1_propose", "f1_reword", "f2_seen", "f3_followed", "too_narrow"]


@dataclass
class JobSpec:
    kind: str
    model_key: str
    system: str
    prompt_sha256: str
    user_text: str
    trajectories: dict            # name -> Trajectory ("A"/"B" for F1, "T" otherwise)
    submit_schema: dict
    submit_description: str
    validate: Callable            # output dict -> (ok, error, normalized output)
    inputs: dict = field(default_factory=dict)
    require_full_read: bool = False  # F1: submit is refused until read_steps has shown every step of every run


def system_prompt(kind: str) -> tuple[str, str]:
    text = (PROMPTS / "preamble.md").read_text(encoding="utf-8") + "\n\n" + (PROMPTS / f"{kind}.md").read_text(encoding="utf-8")
    return text, hashlib.sha256(text.encode()).hexdigest()


def sizes(name: str, t: Trajectory) -> str:
    outs = sorted(((len(i.get("text", "")), i["loc"]) for i in t.items if i["kind"] == "output"), reverse=True)[:5]
    big = ", ".join(f"{loc} ({n:,} chars)" for n, loc in outs)
    return (f"{name} = trajectory `{t.id}`: {len(t.items)} items, {len(t.steps())} steps, ~{t.est_tokens():,} tokens "
            f"({t.total_chars():,} characters); largest outputs: {big or 'none'}.")


def facts_text(facts: list) -> str:
    if not facts:
        return "(empty observation: it holds from the start)"
    lines = []
    for n, f in enumerate(facts, 1):
        lines.append(f"{n}. {f['fact'] if isinstance(f, dict) else f}")
    return "\n".join(lines)


def _str(value, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} must be a non-empty string")
    return value.strip()


def _quote(value) -> str:
    return (value or "")[:QUOTE_MAX] if isinstance(value, str) else ""


def _norm(text: str) -> str:
    """Letters and digits only, lowercased, after removing line-number prefixes ("15:  text", as tool outputs show
    them) and quoted-printable soft line breaks and escapes (=E2=80=99): quotes often drop formatting (markdown, table layout, escapes, line
    numbers), and the check is only that the quoted words are this item's words in this order."""
    text = re.sub(r"(?m)^[ \t]*\d+:[ \t]?", "", text)
    text = re.sub(r"=\r?\n", "", text)
    text = re.sub(r"(?:=[0-9A-F]{2})+", lambda m: bytes.fromhex(m.group(0).replace("=", "")).decode("utf-8", "ignore"), text)
    return re.sub(r"[^0-9a-z]+", "", text.lower())


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def check_quote(t: Trajectory, loc: str, quote: str) -> None:
    """The quote must be text of the item at `loc` (compared on letters and digits only, see _norm; '…' or '...' may join excerpts;
    for a tool call, the decoded argument values count too). Raises ValueError."""
    q = (quote or "").strip()
    if not q:
        raise ValueError(f"a quote from {loc} is required")
    item = t.items[t.position(loc)[0]] if loc != "start" else None
    if item is None:
        return
    texts = [item.get("text", "")]
    if item["kind"] == "call":
        try:
            texts += _strings(json.loads(item["text"]))
        except (ValueError, TypeError):
            pass
    hay = [_norm(x) for x in texts]
    parts = [_norm(p) for p in re.split(r"…|\.\.\.", q) if _norm(p)]
    if not parts or not all(any(p in h for h in hay) for p in parts):
        raise ValueError(f"quote {q[:80]!r} is not text of {item['loc']}: copy it exactly from the item at the location you "
                         f"give (or give the location where the quoted text is)")


# --- F1 propose -------------------------------------------------------------------------------------------------------
LOCPAIR = {"type": "object", "properties": {"observation": {"type": "string"}, "action": {"type": "string"}},
           "required": ["observation", "action"]}
F1_SCHEMA = {
    "type": "object",
    "properties": {
        "invariants": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "i1, i2, ..."},
                "observation": {"type": "array", "description": "the facts that must all hold; [] for an empty observation",
                                "items": {"type": "object", "properties": {
                                    "fact": {"type": "string"},
                                    "source": {"type": "string", "enum": SOURCES},
                                    "reason": {"type": "string", "description": "one line: why the action needs this fact"}},
                                    "required": ["fact", "source", "reason"]}},
                "action": {"type": "object", "properties": {"text": {"type": "string"},
                                                            "purpose": {"type": "string", "description": "one line: what the action achieves"}},
                           "required": ["text", "purpose"]},
                "follows": {"type": "array", "items": {"type": "string"}, "description": "ids of invariants this one chains from"},
                "evidence": {"type": "object", "properties": {"A": LOCPAIR, "B": LOCPAIR}, "required": ["A", "B"],
                             "description": "locations of the observation (where its last fact appears; `start` if empty) and of the action, in each run"}},
            "required": ["id", "observation", "action", "follows", "evidence"]}},
        "roles": {"type": "array", "items": {"type": "object", "properties": {"term": {"type": "string"}, "meaning": {"type": "string"}},
                                             "required": ["term", "meaning"]}}},
    "required": ["invariants", "roles"]}


def validate_f1(out: dict):
    try:
        invs = out.get("invariants")
        if not isinstance(invs, list):
            raise ValueError("invariants must be a list")
        seen_ids, norm = set(), []
        for n, inv in enumerate(invs, 1):
            if not isinstance(inv, dict):
                raise ValueError(f"invariant {n} must be an object")
            iid = _str(inv.get("id"), f"invariant {n}: id")
            if iid in seen_ids:
                raise ValueError(f"duplicate id {iid}")
            seen_ids.add(iid)
            obs = inv.get("observation")
            if not isinstance(obs, list):
                raise ValueError(f"{iid}: observation must be a list of facts ([] for an empty observation)")
            facts = []
            for k, f in enumerate(obs, 1):
                if not isinstance(f, dict):
                    raise ValueError(f"{iid}: fact {k} must be an object")
                src = f.get("source")
                if src not in SOURCES:
                    raise ValueError(f"{iid}: fact {k}: source must be one of {SOURCES}")
                facts.append({"fact": _str(f.get("fact"), f"{iid}: fact {k}: fact"), "source": src,
                              "reason": _str(f.get("reason"), f"{iid}: fact {k}: reason (a fact without a reason must be dropped)")})
            act = inv.get("action")
            if not isinstance(act, dict):
                raise ValueError(f"{iid}: action must be an object with text and purpose")
            action = {"text": _str(act.get("text"), f"{iid}: action.text"), "purpose": _str(act.get("purpose"), f"{iid}: action.purpose")}
            follows = inv.get("follows") or []
            if not isinstance(follows, list) or not all(isinstance(x, str) for x in follows):
                raise ValueError(f"{iid}: follows must be a list of ids")
            ev = inv.get("evidence")
            if not isinstance(ev, dict) or not all(isinstance(ev.get(r), dict) for r in ("A", "B")):
                raise ValueError(f"{iid}: evidence must have A and B, each with observation and action locations")
            evidence = {r: {"observation": str(ev[r].get("observation", "")), "action": str(ev[r].get("action", ""))} for r in ("A", "B")}
            norm.append({"id": iid, "observation": facts, "action": action, "follows": follows, "evidence": evidence})
        for inv in norm:
            unknown = [x for x in inv["follows"] if x not in seen_ids]
            if unknown:
                raise ValueError(f"{inv['id']}: follows unknown ids {unknown}")
        roles = out.get("roles") or []
        if not isinstance(roles, list):
            raise ValueError("roles must be a list")
        roles = [{"term": _str(r.get("term"), "roles: term"), "meaning": _str(r.get("meaning"), "roles: meaning")}
                 for r in roles if isinstance(r, dict)]
        return True, None, {"invariants": norm, "roles": roles}
    except ValueError as e:
        return False, str(e), None


def f1_evidence_problems(inv: dict, trajs: dict) -> list[str]:
    """The free F1 evidence check (DESIGN.md 4.1): locations exist, observation before action. Logged only."""
    problems = []
    for run in ("A", "B"):
        t = trajs[run]
        ev = inv["evidence"][run]
        try:
            o = t.position(ev["observation"])
            a = t.position(ev["action"])
            if not inv["observation"] and ev["observation"] != "start":
                problems.append(f"{run}: empty observation should have location start")
            if a < o:
                problems.append(f"{run}: action {ev['action']} comes before observation {ev['observation']}")
        except LocationError as e:
            problems.append(f"{run}: {e}")
    return problems


# --- F2 seen? ---------------------------------------------------------------------------------------------------------
F2_SCHEMA = {"type": "object", "properties": {
    "seen": {"type": "boolean"},
    "location": {"type": ["string", "null"], "description": "first location where all facts hold (where the last of them first appears); null if not seen"},
    "evidence": {"type": "array", "description": "one entry per fact when seen; [] when not seen",
                 "items": {"type": "object", "properties": {"fact": {"type": "integer", "description": "fact number (1, 2, ...)"},
                                                            "location": {"type": "string"}, "quote": {"type": "string"}},
                           "required": ["fact", "location", "quote"]}}},
    "required": ["seen", "location", "evidence"], "additionalProperties": False}


def make_validate_f2(t: Trajectory, n_facts: int):
    def validate(out: dict):
        try:
            if set(out) - {"seen", "location", "evidence"}:
                raise ValueError(f"unexpected fields {sorted(set(out) - {'seen', 'location', 'evidence'})}: answer only seen, location, evidence")
            seen = out.get("seen")
            if not isinstance(seen, bool):
                raise ValueError("seen must be true or false")
            if not seen:
                return True, None, {"seen": False, "location": None, "evidence": []}
            loc = _str(out.get("location"), "location")
            pos = t.position(loc)
            ev = out.get("evidence")
            if not isinstance(ev, list) or not ev:
                raise ValueError(f"evidence must have at least one entry per fact ({n_facts})")
            norm, first_of = [], {}
            for e in ev:
                k = e.get("fact") if isinstance(e, dict) else None
                if not isinstance(k, int) or not 1 <= k <= n_facts:
                    raise ValueError(f"evidence fact numbers must be 1..{n_facts}")
                eloc = _str(e.get("location"), f"evidence for fact {k}: location")
                epos = t.position(eloc)
                check_quote(t, eloc, _quote(e.get("quote")))
                first_of[k] = min(first_of.get(k, epos[0]), epos[0])  # several entries for a fact: its earliest counts
                norm.append({"fact": k, "location": eloc, "quote": _quote(e.get("quote"))})
            if sorted(first_of) != list(range(1, n_facts + 1)):
                raise ValueError(f"evidence must cover every fact (1..{n_facts})")
            latest = max(first_of.values())
            if latest > pos[0]:
                k = max(first_of, key=first_of.get)
                raise ValueError(f"fact {k} first appears after the location {loc}: the location must be where ALL facts hold")
            if pos[0] != latest:
                raise ValueError(f"location {loc} must be the FIRST location where all facts hold, i.e. the item where the last "
                                 f"fact first appears ({t.items[latest]['loc']} by your evidence)")
            return True, None, {"seen": True, "location": loc, "evidence": sorted(norm, key=lambda x: x["fact"])}
        except (ValueError, LocationError) as e:
            return False, str(e), None
    return validate


# --- F3 followed? -----------------------------------------------------------------------------------------------------
F3_SCHEMA = {"type": "object", "properties": {
    "outcome": {"type": "string", "enum": F3_OUTCOMES},
    "action_location": {"type": ["string", "null"], "description": "where the action happened (followed / only_before); null otherwise"},
    "quote": {"type": "string"}},
    "required": ["outcome", "action_location", "quote"], "additionalProperties": False}


def make_validate_f3(t: Trajectory, pinned: str):
    phi = pinned == "start"

    def validate(out: dict):
        try:
            if set(out) - {"outcome", "action_location", "quote"}:
                raise ValueError("answer only outcome, action_location, quote")
            outcome = out.get("outcome")
            if outcome not in F3_OUTCOMES:
                raise ValueError(f"outcome must be one of {F3_OUTCOMES}")
            if phi and outcome in ("pinning_wrong", "only_before"):
                raise ValueError("the observation is empty (pinned at start): the outcome is followed or not_followed")
            if outcome in ("not_followed", "pinning_wrong"):
                return True, None, {"outcome": outcome, "action_location": None, "quote": _quote(out.get("quote"))}
            aloc = _str(out.get("action_location"), "action_location")
            apos, ppos = t.position(aloc), t.position(pinned)
            if outcome == "followed" and apos[0] < ppos[0]:
                raise ValueError(f"followed: the action location {aloc} must not be before the pinned location {pinned}")
            if outcome == "only_before" and apos >= ppos:
                raise ValueError(f"only_before: the action location {aloc} must be before the pinned location {pinned}")
            check_quote(t, aloc, _quote(out.get("quote")))
            return True, None, {"outcome": outcome, "action_location": aloc, "quote": _quote(out.get("quote"))}
        except (ValueError, LocationError) as e:
            return False, str(e), None
    return validate


# --- too-narrow check ---------------------------------------------------------------------------------------------------
TN_SCHEMA = {"type": "object", "properties": {
    "purpose_achieved_otherwise": {"type": "boolean"},
    "location": {"type": ["string", "null"], "description": "where the different action happened; null if not"},
    "quote": {"type": "string"}},
    "required": ["purpose_achieved_otherwise", "location", "quote"], "additionalProperties": False}


def make_validate_tn(t: Trajectory, pinned: str):
    def validate(out: dict):
        try:
            if set(out) - {"purpose_achieved_otherwise", "location", "quote"}:
                raise ValueError("answer only purpose_achieved_otherwise, location, quote")
            yes = out.get("purpose_achieved_otherwise")
            if not isinstance(yes, bool):
                raise ValueError("purpose_achieved_otherwise must be true or false")
            if not yes:
                return True, None, {"purpose_achieved_otherwise": False, "location": None, "quote": _quote(out.get("quote"))}
            loc = _str(out.get("location"), "location")
            if t.position(loc)[0] < t.position(pinned)[0]:
                raise ValueError(f"the different action must come after the pinned location {pinned}")
            check_quote(t, loc, _quote(out.get("quote")))
            return True, None, {"purpose_achieved_otherwise": True, "location": loc, "quote": _quote(out.get("quote"))}
        except (ValueError, LocationError) as e:
            return False, str(e), None
    return validate


# --- F1 reword --------------------------------------------------------------------------------------------------------
RW_SCHEMA = {"type": "object", "properties": {
    "action": {"type": "object", "properties": {"text": {"type": "string"}, "purpose": {"type": "string"}}, "required": ["text", "purpose"]}},
    "required": ["action"]}


def validate_rw(out: dict):
    try:
        act = out.get("action")
        if not isinstance(act, dict):
            raise ValueError("action must be an object with text and purpose")
        return True, None, {"action": {"text": _str(act.get("text"), "action.text"), "purpose": _str(act.get("purpose"), "action.purpose")}}
    except ValueError as e:
        return False, str(e), None


# --- building a job ---------------------------------------------------------------------------------------------------
def build(kind: str, model_key: str, inputs: dict, trajs: dict[str, Trajectory]) -> JobSpec:
    system, sha = system_prompt(kind)
    if kind == "f1_propose":
        user = (sizes("Run A", trajs["A"]) + "\n" + sizes("Run B", trajs["B"]) +
                "\n\nBoth runs passed. Find all the observation -> action pairs common to both runs, then submit them.")
        return JobSpec(kind, model_key, system, sha, user, trajs, F1_SCHEMA,
                       "Submit all the invariants common to both runs (once; fix and resubmit if rejected). Refused until "
                       "read_steps has shown every step of both runs.", validate_f1, inputs, require_full_read=True)
    t = trajs["T"]
    if kind == "f2_seen":
        facts = inputs["facts"]
        user = f"Observation (all facts must hold):\n{facts_text(facts)}\n\n{sizes('Trajectory', t)}"
        return JobSpec(kind, model_key, system, sha, user, trajs, F2_SCHEMA, "Submit whether the observation was seen, "
                       "where (first location where all facts hold) and the evidence per fact.", make_validate_f2(t, len(facts)), inputs)
    if kind == "f3_followed":
        user = (f"Observation:\n{facts_text(inputs['facts'])}\n\nAction: {inputs['action']}\n\n"
                f"Pinned location of the observation: {inputs['location']}\n\n{sizes('Trajectory', t)}")
        return JobSpec(kind, model_key, system, sha, user, trajs, F3_SCHEMA, "Submit exactly one outcome "
                       "(followed / not_followed / only_before / pinning_wrong) with the action's location.",
                       make_validate_f3(t, inputs["location"]), inputs)
    if kind == "too_narrow":
        user = (f"Observation:\n{facts_text(inputs['facts'])}\n\nAction: {inputs['action']}\nPurpose of the action: "
                f"{inputs['purpose']}\n\nPinned location of the observation: {inputs['location']}\n\n"
                "Another check found that the action, as worded, did not happen after the pinned location.\n\n" + sizes('Trajectory', t))
        return JobSpec(kind, model_key, system, sha, user, trajs, TN_SCHEMA, "Submit whether the action's purpose was "
                       "achieved by a different action after the pinned location, and where.", make_validate_tn(t, inputs["location"]), inputs)
    if kind == "f1_reword":
        facts = "\n".join(f"{n}. {f['fact']}  (source: {f['source']}; why the action needs it: {f['reason']})"
                          for n, f in enumerate(inputs["facts"], 1)) or "(empty observation)"
        prev = ""
        if inputs.get("previous"):
            p = inputs["previous"]
            prev = (f"\n\nA previous rewording failed validation: action \"{p['action']}\" (purpose: {p['purpose']}). "
                    f"Failed check: {p['failed_check']}. Write a different rewording.")
        user = (f"Invariant learnt from earlier runs of this task, where it holds:\nObservation:\n{facts}\n\n"
                f"Action: {inputs['action']}\nPurpose: {inputs['purpose']}\n\n"
                f"In the trajectory below the agent saw the observation but did not take the action as worded; it achieved the "
                f"action's purpose with a different action at {inputs['alt_location']}.{prev}\n\n{sizes('Trajectory', t)}")
        return JobSpec(kind, model_key, system, sha, user, trajs, RW_SCHEMA, "Submit the reworded action and its purpose.",
                       validate_rw, inputs)
    raise ValueError(f"unknown job kind {kind}")
