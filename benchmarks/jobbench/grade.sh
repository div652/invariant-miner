#!/usr/bin/env bash
# Grade a dsh-bench JobBench run with JobBench's own judge (job-bench-eval eval/run_judge.sh, through
# ~/jobbench-cao/judge_parallel.sh: grok-4.6 via the CAO judge shim on :8019 by default).
#
#   benchmarks/jobbench/grade.sh RUN_DIR [DATASET=~/job-bench-eval/dataset/main] [NGROUPS=2] [PER_GROUP=9]
#
# Builds RUN_DIR/grading/dataset/main/<task>/ from the dataset's task dir (task_folder, RUBRICS.json, ...) plus the
# run's workspace/output as model_output/$LABEL/. Symlinks in the output are NOT copied (an agent could point one at a
# host file); they are listed in RUN_DIR/grading/skipped-symlinks.txt. Scores: RUN_DIR/grading/scores.txt.
# Env: GRADING_DIR (default RUN_DIR/grading), ONLY (space-separated task dir names under RUN_DIR/tasks to grade).
set -euo pipefail
RUN="$(cd "$1" && pwd)"; DATASET="$(cd "${2:-$HOME/job-bench-eval/dataset/main}" && pwd)"
[[ "$(realpath -m "${GRADING_DIR:-$RUN/grading}")" != "$RUN/tasks/"* ]] || { echo "GRADING_DIR must not be inside a task dir" >&2; exit 1; }
NGROUPS="${3:-2}"; PER_GROUP="${4:-9}"
LABEL="${LABEL:-gpt-5-6-luna-dsh-bench}"
G="$(realpath -m "${GRADING_DIR:-$RUN/grading}")"   # absolute: the copies below run from inside each output dir
[[ ! -e "$G" ]] || { echo "$G exists; remove it to re-grade" >&2; exit 1; }
mkdir -p "$G/dataset/main"
: > "$G/skipped-symlinks.txt"
for task in "$RUN"/tasks/*/; do
  if [[ -n "${ONLY:-}" && " $ONLY " != *" $(basename "$task") "* ]]; then continue; fi
  [[ -f "$task/run.json" ]] || { echo "skip (unfinished): $task"; continue; }
  id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["task_id"])' "$task/spec.json")"
  dest="$G/dataset/main/$id"
  mkdir -p "$dest"
  for item in "$DATASET/$id"/*; do
    [[ "$(basename "$item")" == model_output ]] && continue
    cp -r "$item" "$dest/"
  done
  mkdir -p "$dest/model_output/$LABEL"
  (cd "$task/workspace/output" && find . -type l) | sed "s|^\.|$id/output|" >> "$G/skipped-symlinks.txt"
  (cd "$task/workspace/output" && find . -type d -exec mkdir -p "$dest/model_output/$LABEL/{}" \; \
     && find . -type f -exec cp --no-dereference "{}" "$dest/model_output/$LABEL/{}" \;)
done
echo "[grade] $(ls -d "$G"/dataset/main/*/task* | wc -l) tasks staged, label $LABEL"
/home/agarwaldi/jobbench-cao/judge_parallel.sh "$G" "$LABEL" "$NGROUPS" "$PER_GROUP" | tee "$G/scores.txt"
