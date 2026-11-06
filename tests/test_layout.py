"""Layout rule: the core knows nothing about any benchmark; only benchmarks/<name>/ refers to the core.

Fails if a core file (everything outside benchmarks/, docs/, patches/, work/, runs/, and not a README.md) mentions the name of a directory
in benchmarks/. Names are matched case-insensitively, ignoring "-", "_" and spaces (so "MyBench", "my-bench" and
"my_bench" all match a directory "mybench"). docs/ and README.md files may name benchmarks (as references and examples); patches/ is the upstream
DSH patch series.

    python3 tests/test_layout.py
"""

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOT_CORE = {"benchmarks", "docs", "patches", "work", "runs", ".git", "README.md"}


def main() -> int:
    names = sorted(p.name.lower() for p in (REPO / "benchmarks").iterdir() if p.is_dir())
    pattern = re.compile("|".join(re.escape(re.sub(r"[-_ ]", "", n)) for n in names))
    hits = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        rel_dir = Path(dirpath).relative_to(REPO)
        # Prune before descending: runs/ and work/ hold millions of files (hard-linked task documents).
        dirnames[:] = [d for d in dirnames if not (rel_dir == Path(".") and d in NOT_CORE) and d != "__pycache__"]
        for name in sorted(filenames):
            rel = rel_dir / name
            if name == "README.md" or (rel_dir == Path(".") and name in NOT_CORE):
                continue
            try:
                lines = (REPO / rel).read_text().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(lines, 1):
                if pattern.search(re.sub(r"[-_ ]", "", line.lower())):
                    hits.append(f"{rel}:{number}: {line.strip()[:120]}")
    print(f"benchmarks: {', '.join(names)}")
    if hits:
        print("core files mention a benchmark (move the code into benchmarks/<name>/ or make it generic):")
        print("\n".join(hits))
        return 1
    print("PASS  the core mentions no benchmark")
    return 0


if __name__ == "__main__":
    sys.exit(main())
