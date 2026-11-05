"""Layout rule: the core knows nothing about any benchmark; only benchmarks/<name>/ refers to the core.

Fails if a core file (everything outside benchmarks/, docs/, patches/, work/, runs/) mentions the name of a directory
in benchmarks/. Names are matched case-insensitively, ignoring "-", "_" and spaces (so "MyBench", "my-bench" and
"my_bench" all match a directory "mybench"). docs/ may name benchmarks (as references and examples); patches/ is the upstream
DSH patch series.

    python3 tests/test_layout.py
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOT_CORE = {"benchmarks", "docs", "patches", "work", "runs", ".git"}


def main() -> int:
    names = sorted(p.name.lower() for p in (REPO / "benchmarks").iterdir() if p.is_dir())
    pattern = re.compile("|".join(re.escape(re.sub(r"[-_ ]", "", n)) for n in names))
    hits = []
    for path in sorted(REPO.rglob("*")):
        rel = path.relative_to(REPO)
        if rel.parts[0] in NOT_CORE or not path.is_file() or "__pycache__" in rel.parts:
            continue
        try:
            lines = path.read_text().splitlines()
        except UnicodeDecodeError:
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
