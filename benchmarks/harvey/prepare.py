"""Prepare Harvey's system prompt and skills for DSH: exact, recorded text replacements on the pinned files.

    python3 benchmarks/harvey/prepare.py      # writes work/harvey-prepared/ (system_prompt.md, skills/, CHANGES.md)

Source: work/harvey-labs (pinned by setup.sh). The system prompt is Harvey's `--no-enable-finish` variant (the file
as-is: the finish guidance is only spliced in when the finish tool is on). Each replacement must match exactly once;
a source change at a new pin fails here instead of silently leaving a false statement in the prompt.

Why each change: under DSH, `read` opens UTF-8 text only (Harvey's `read` converts .docx/.xlsx/.pptx); only `write`
gets Harvey's output/ rule (plugins/harvey-write.mjs), `edit` resolves relative paths against the workspace; Harvey's
skills are off by default (user's decision, 2026-11-05), so every mention of them is removed from the prompt.

Skills (optional, `make_specs.py --skills`, user 2026-11-15): Harvey's docx / xlsx / pptx skills are exposed the way
DSH exposes skills - registered with DSH's skill registry (spec key skills_dir, plugins/skills), listed by the `skill`
tool by name and description, a manual loaded only when the agent asks - never pasted into the system prompt as
Harvey's harness does. skills/<name>/ here is Harvey's skill folder (SKILL.md + scripts/) with three exact changes per
manual: reading an office file is `parse-doc` in bash, not `read`. The scripts are staged into the workspace at
skills/<name>/scripts/, where the manuals say they are. Everything else is unchanged.
"""

import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "work/harvey-labs"
OUT = REPO / "work/harvey-prepared"

PROMPT_CHANGES = [
    ("no skills: the workspace has no skills/ folder",
     "`documents/  output/  skills/` plus any scratch files you create.",
     "`documents/  output/` plus any scratch files you create."),
    ("no skills: no skill output or skill scripts",
     "- **`$WORKSPACE_DIR`** — your working area, default `bash` cwd. Use it for\n"
     "  notes, intermediate files, and skill output. Skill scripts live at\n"
     "  `$WORKSPACE_DIR/skills/<name>/scripts/`.",
     "- **`$WORKSPACE_DIR`** — your working area, default `bash` cwd. Use it for\n"
     "  notes and intermediate files."),
    ("every deliverable goes in output/, including files built with bash; only `write` routes relative paths there "
     "(plugins/harvey-write.mjs), `edit` is DSH's (relative to the workspace)",
     "- **`$OUTPUT_DIR`** (`$WORKSPACE_DIR/output`) — deliverables. The harness\n"
     "  routes relative `write` and `edit` paths here automatically.",
     "- **`$OUTPUT_DIR`** (`$WORKSPACE_DIR/output`) — deliverables. Save every\n"
     "  deliverable file here, including files you build with `bash` (.docx,\n"
     "  .xlsx, .pptx): only files in `$OUTPUT_DIR` are delivered. `write` saves\n"
     "  here by default: a relative `write` path is written under `$OUTPUT_DIR`."),
    ("DSH's read opens text only; office files are converted with bash",
     "- Use `read` to consume input files (handles .docx, .xlsx, .pptx, .pdf, and\n  plain text).",
     "- `read` opens plain-text files only (.txt, .md, .eml, .csv, ...). To read\n"
     "  .docx, .xlsx or .pptx files, convert them to text with `bash`:\n"
     "  `parse-doc docx|xlsx|pptx <file>` (markitdown and pandoc are also available)."),
    ("no skills: no skill manuals",
     "- Use the file-type skill manuals below to produce binary deliverables\n  (.docx, .xlsx, .pptx).\n",
     ""),
    ("no skills: no skill manuals",
     "\nThe skill manuals immediately below describe how to work with specific file\n"
     "formats. Read them before tackling the task.\n",
     ""),
]


def skill_changes(fmt: str, note_old: str, note_new: str) -> list[tuple[str, str, str]]:
    why = "DSH's read opens text only; office files are converted with bash"
    return [
        (why, f"{fmt} files, use the harness `read` tool — do not invoke this skill.",
         f"{fmt} files, convert them with `parse-doc {fmt} <file>` in bash — do not invoke this skill."),
        (why, note_old, note_new),
        (why, "- Reading: use the `read` tool.", f"- Reading: `parse-doc {fmt} <file>` in bash."),
    ]


SKILL_CHANGES = {
    "docx": skill_changes(
        "docx",
        "To read an existing .docx, use the harness `read` tool. It already returns structured text via pandoc.",
        "To read an existing .docx, run `parse-doc docx <file>` in bash. It returns structured text via pandoc."),
    "xlsx": skill_changes(
        "xlsx",
        "To read an existing .xlsx, use the harness `read` tool (pandas extracts every sheet as a markdown table).",
        "To read an existing .xlsx, run `parse-doc xlsx <file>` in bash (pandas extracts every sheet as a table)."),
    "pptx": skill_changes(
        "pptx",
        "To read an existing .pptx, use the harness `read` tool (markitdown extracts slide text).",
        "To read an existing .pptx, run `parse-doc pptx <file>` in bash (markitdown extracts slide text)."),
}


def apply(text: str, changes: list[tuple[str, str, str]], where: str, log: list[str]) -> str:
    for why, old, new in changes:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{where}: expected the text to change exactly once, found {count}:\n{old}")
        text = text.replace(old, new)
        log.append(f"### {where}: {why}\n\n```diff\n" + "".join(f"- {line}\n" for line in old.split("\n"))
                   + "".join(f"+ {line}\n" for line in new.split("\n")) + "```\n")
    return text


def main() -> None:
    commit = subprocess.run(["git", "-C", str(LAB), "rev-parse", "HEAD"], capture_output=True, text=True,
                            check=True).stdout.strip()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    log = [f"# Changes to Harvey's system prompt for DSH\n\nSource: harvey-labs @ {commit}, "
           "lab_core/harness/system_prompt.md (its --no-enable-finish form: the file as is). Generated by "
           "benchmarks/harvey/prepare.py; every other line is Harvey's, unchanged.\n"]
    prompt = (LAB / "lab_core/harness/system_prompt.md").read_text()
    text = apply(prompt, PROMPT_CHANGES, "system_prompt.md", log)
    if "skill" in text.lower():
        raise SystemExit("the prepared system prompt still mentions skills")
    (OUT / "system_prompt.md").write_text(text)
    skills_src = LAB / "lab_core/harness/skills"
    names = sorted(p.parent.name for p in skills_src.glob("*/SKILL.md"))
    if names != sorted(SKILL_CHANGES):
        raise SystemExit(f"skills at the pin are {names}, prepare.py knows {sorted(SKILL_CHANGES)}")
    log.append("\n# Changes to Harvey's skill manuals (used only with make_specs.py --skills)\n")
    for name in names:
        shutil.copytree(skills_src / name, OUT / "skills" / name)
        manual = OUT / "skills" / name / "SKILL.md"
        manual.write_text(apply(manual.read_text(), SKILL_CHANGES[name], f"skills/{name}/SKILL.md", log))
    (OUT / "CHANGES.md").write_text("\n".join(log))
    print(f"[prepare] {OUT}: system_prompt.md ({len(PROMPT_CHANGES)} changes), skills {names} "
          f"({sum(len(v) for v in SKILL_CHANGES.values())} changes); see CHANGES.md")


if __name__ == "__main__":
    main()
