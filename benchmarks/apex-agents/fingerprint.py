"""Fingerprint of the APEX-Agents 1.1 task packages (Harbor Hub download): one sha256 per task directory.

    python3 benchmarks/apex-agents-1.1/fingerprint.py --write TASKS_DIR   # (re)write tasks.sha256 (maintainers only)
    python3 benchmarks/apex-agents-1.1/fingerprint.py --check TASKS_DIR   # setup.sh: the download is what we analysed

A task's hash covers every file under its directory (relative path + content, sorted), so any added, removed or changed
file shows. tasks.sha256 was written from mercor/apex-agents-1-1@1.1.1 on 2026-11-07 (240 tasks).
"""

import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIST = HERE / "tasks.sha256"


def task_hash(task_dir: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in task_dir.rglob("*") if p.is_file()):
        h.update(str(path.relative_to(task_dir)).encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("tasks_dir", type=Path)
    args = parser.parse_args()
    found = {d.name: task_hash(d) for d in sorted(args.tasks_dir.iterdir()) if d.is_dir()}
    if args.write:
        LIST.write_text("".join(f"{h}  {name}\n" for name, h in found.items()))
        print(f"wrote {len(found)} task hashes to {LIST}")
        return 0
    expected = dict(line.split("  ")[::-1] for line in LIST.read_text().splitlines() if line.strip())
    missing = sorted(set(expected) - set(found))
    extra = sorted(set(found) - set(expected))
    changed = sorted(name for name in set(expected) & set(found) if expected[name] != found[name])
    if missing or extra or changed:
        print(f"task packages differ from tasks.sha256: missing {missing[:5]} ({len(missing)}), "
              f"extra {extra[:5]} ({len(extra)}), changed {changed[:5]} ({len(changed)})")
        return 1
    print(f"{len(found)} task packages match tasks.sha256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
