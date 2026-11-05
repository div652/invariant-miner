"""Prepare Harvey's system prompt and skills for DSH: exact, recorded text replacements on the pinned files.

    python3 benchmarks/harvey/prepare.py      # writes work/harvey-prepared/ (system_prompt.md, skills/, CHANGES.md)

Source: work/harvey-labs (pinned by setup.sh). The system prompt is Harvey's `--no-enable-finish` variant (the file
as-is: the finish guidance is only spliced in when the finish tool is on). Each replacement must match exactly once;
a source change at a new pin fails here instead of silently leaving a false statement in the prompt.

Why each change: under DSH, `read` opens UTF-8 text only (Harvey's `read` converts .docx/.xlsx/.pptx); relative
`write`/`edit` paths resolve against the workspace root (Harvey's go to output/); skills are DSH skills loaded with the
`skill` tool (Harvey pastes the manuals into the system prompt). Everything else is unchanged.
"""

import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "work/harvey-labs"
OUT = REPO / "work/harvey-prepared"

PROMPT_CHANGES = [
    ("deliverables go to output/ (relative paths resolve against the workspace under DSH)",
     "- **`$OUTPUT_DIR`** (`$WORKSPACE_DIR/output`) — deliverables. The harness\n"
     "  routes relative `write` and `edit` paths here automatically.",
     "- **`$OUTPUT_DIR`** (`$WORKSPACE_DIR/output`) — deliverables. Save every\n"
     "  deliverable here. Relative `write` and `edit` paths resolve against\n"
     "  `$WORKSPACE_DIR`, so write `output/response.md`, not `response.md`."),
    ("DSH's read opens text only; office files are converted with bash",
     "- Use `read` to consume input files (handles .docx, .xlsx, .pptx, .pdf, and\n  plain text).",
     "- `read` opens plain-text files only (.txt, .md, .eml, .csv, ...). To read\n"
     "  .docx, .xlsx or .pptx files, convert them to text with `bash`:\n"
     "  `parse-doc docx|xlsx|pptx <file>` (markitdown and pandoc are also available)."),
    ("skills are DSH skills, not manuals pasted below",
     "- Use the file-type skill manuals below to produce binary deliverables\n  (.docx, .xlsx, .pptx).",
     "- Use the file-type skills (docx, xlsx, pptx) to produce binary deliverables\n"
     "  (.docx, .xlsx, .pptx); load one with the `skill` tool."),
    ("response.md lives in output/",
     "- Use `write` only for plain markdown — typically a `response.md`\n  summarizing your work.",
     "- Use `write` only for plain markdown — typically an `output/response.md`\n  summarizing your work."),
    ("skills are DSH skills, not manuals pasted below",
     "The skill manuals immediately below describe how to work with specific file\n"
     "formats. Read them before tackling the task.",
     "The skills describe how to work with specific file formats. Load the ones\n"
     "relevant to your deliverables with the `skill` tool before tackling the task."),
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
    commit = (LAB / ".git").exists() and __import__("subprocess").run(
        ["git", "-C", str(LAB), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "skills").mkdir(parents=True)
    log = [f"# Changes to Harvey's prompt text for DSH\n\nSource: harvey-labs @ {commit}. Generated by "
           "benchmarks/harvey/prepare.py; every other line is Harvey's, unchanged.\n"]
    prompt = (LAB / "lab_core/harness/system_prompt.md").read_text()
    (OUT / "system_prompt.md").write_text(apply(prompt, PROMPT_CHANGES, "system_prompt.md", log))
    skills_src = LAB / "lab_core/harness/skills"
    names = sorted(p.parent.name for p in skills_src.glob("*/SKILL.md"))
    if names != sorted(SKILL_CHANGES):
        raise SystemExit(f"skills at the pin are {names}, prepare.py knows {sorted(SKILL_CHANGES)}")
    for name in names:
        shutil.copytree(skills_src / name, OUT / "skills" / name)
        manual = OUT / "skills" / name / "SKILL.md"
        manual.write_text(apply(manual.read_text(), SKILL_CHANGES[name], f"skills/{name}/SKILL.md", log))
    (OUT / "CHANGES.md").write_text("\n".join(log))
    print(f"[prepare] {OUT}: system_prompt.md ({len(PROMPT_CHANGES)} changes), skills {names} "
          f"({sum(len(v) for v in SKILL_CHANGES.values())} changes); see CHANGES.md")


if __name__ == "__main__":
    main()
