#!/usr/bin/env bash
# Harvey run: the core spec runner.   benchmarks/jobbench/run.sh SPECS_DIR RUN_DIR [CONCURRENCY=4]
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/dsh_bench/run_specs.sh" "$@"
