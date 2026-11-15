"""Offline checks of dsh_tools.py's file tools and spill policy (no container needed).

    python3 benchmarks/harvey/trace2script/test_dsh_tools.py

Formats are DSH's (packages/fs/tool-fs read-render.ts / write.ts / edit.ts, fs-observation-policy, spill-policy).
The container tools (bash, glob, grep) are checked by replaying a recorded trajectory instead (README.md).
"""

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsh_tools import DENIED, SPILL_MAX_INLINE, WS_MARK, Tools  # noqa: E402


def main() -> int:
    ws = Path(tempfile.mkdtemp(prefix="t2s-test-")).resolve()
    (ws / "output").mkdir()
    (ws / "notes.txt").write_text("".join(f"line {i}\n" for i in range(1, 2501)))
    (ws / "wide.txt").write_text("x" * 3000 + "\n")
    (ws / "big.txt").write_text("".join("y" * 999 + "\n" for _ in range(60)))
    T = Tools(ws, container="none")
    run = asyncio.run
    checks = []

    r = run(T.read(file_path="notes.txt", offset=1, limit=3))
    checks.append(("read: header, numbered lines, 'Showing lines' footer",
                   r == f"<path>{ws}/notes.txt</path>\n<type>file</type>\n<content>\n1: line 1\n2: line 2\n3: line 3\n\n"
                        f"(Showing lines 1-3 of 2500. Use offset=4 to continue.)\n</content>"))
    r = run(T.read(file_path="notes.txt", offset=2499))
    checks.append(("read: end-of-file footer", r.endswith("2500: line 2500\n\n(End of file - total 2500 lines)\n</content>")))
    r = run(T.read(file_path="notes.txt"))
    checks.append(("read: default window 2,000 lines", "(Showing lines 1-2000 of 2500. Use offset=2001 to continue.)" in r))
    r = run(T.read(file_path="wide.txt"))
    checks.append(("read: line cut at 2,000 chars", "... (line truncated to 2000 chars)" in r))
    r = run(T.read(file_path="big.txt"))
    checks.append(("read: 50 KiB cap", "(Output capped. Showing lines 1-51. Use offset=52 to continue.)" in r))
    checks.append(("read: outside the workspace denied", run(T.read(file_path="/etc/hostname")) == f"Error: {DENIED}"))
    checks.append(("read: not found", run(T.read(file_path="nope.txt")) == f'Error: cannot read "{ws}/nope.txt": not found'))
    checks.append(("read: out-of-range offset", run(T.read(file_path="wide.txt", offset=5))
                   == f'Error: offset 5 is out of range for "{ws}/wide.txt" (1 lines)'))
    checks.append(("marker: WS_MARK resolves to the workspace", run(T.read(file_path=f"{WS_MARK}/wide.txt", limit=1)).startswith(f"<path>{ws}/wide.txt")))

    r = run(T.write(file_path="response.md", content="a\nb\n"))
    checks.append(("write: relative path goes to output/, Created", r == f"<path>{ws}/output/response.md</path>\n<type>file</type>\n<content>\nCreated file\n</content>"))
    r = run(T.write(file_path="output/response.md", content="c\n"))
    checks.append(("write: same session may overwrite its own file (Updated)", r.endswith("Updated file\n</content>")))
    (ws / "output/other.md").write_text("x\n")
    r = run(T.write(file_path="other.md", content="y\n"))
    checks.append(("write: unread existing file refused", r == f'Error: cannot modify "{ws}/output/other.md": file has not been read — read the file, then retry'))
    (ws / "fresh.txt").write_text("one\ntwo\n")
    r = run(T.edit(file_path="fresh.txt", old_string="one", new_string="ONE"))
    checks.append(("edit: refused before read", r == f'Error: cannot modify "{ws}/fresh.txt": file has not been read — read the file, then retry'))
    run(T.read(file_path="notes.txt", limit=1))
    r = run(T.edit(file_path="notes.txt", old_string="line 2\n", new_string="LINE 2\n"))
    checks.append(("edit: success text", r == f"The file {ws}/notes.txt has been updated successfully."))
    r = run(T.edit(file_path="notes.txt", old_string="line", new_string="row"))
    n = (ws / "notes.txt").read_text().count("line")
    checks.append(("edit: ambiguous match", r.startswith(f'Error: old_string matched {n} times in "{ws}/notes.txt"')))
    r = run(T.todo_write(todos=[{"content": "a", "status": "pending"}, {"content": "b", "status": "completed"}]))
    checks.append(("todo_write text", r == "Updated todo list: 1 pending, 0 in progress, 1 completed."))

    big = "".join(f"{i:06d} " + "z" * 90 + "\n" for i in range(1000))
    s = T._spill_policy("bash", big)
    checks.append(("spill: head + tail + notice, within 50,000 bytes",
                   s.startswith("000000 ") and "000999 " in s and "(Omitted " in s and len(s.encode()) <= SPILL_MAX_INLINE
                   and "/dsh-spill-" in s and s.endswith("Use read with offset/limit, or grep this path to search within it.)")))
    checks.append(("spill: read is never spilled", T._spill_policy("read", big) == big))

    width = max(len(n) for n, _ in checks)
    for n, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{width}}")
    failed = [n for n, ok in checks if not ok]
    print(f"{len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
