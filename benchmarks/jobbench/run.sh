#!/usr/bin/env bash
# Run every spec in SPECS_DIR through the launcher, CONCURRENCY at a time; each task gets RUN_DIR/tasks/<task>.
#   benchmarks/jobbench/run.sh SPECS_DIR RUN_DIR [CONCURRENCY=4]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPECS="$(cd "$1" && pwd)"; RUN="$(mkdir -p "$2" && cd "$2" && pwd)"; N="${3:-4}"
mkdir -p "$RUN/tasks" "$RUN/logs"
ls "$SPECS"/*.json | xargs -P "$N" -I{} bash -c '
  spec="$1"; name="$(basename "$spec" .json)"
  if [[ -e "$3/tasks/$name/run.json" ]]; then echo "skip $name"; exit 0; fi
  rm -rf "$3/tasks/$name"
  cd "$2" && python3 -m dsh_bench.launch --spec "$spec" --out "$3/tasks/$name" > "$3/logs/$name.log" 2>&1
  echo "$(date -u +%H:%M:%S) $(tail -1 "$3/logs/$name.log")"
' _ {} "$HERE" "$RUN"
