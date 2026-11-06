#!/usr/bin/env bash
# Grade a dsh-bench JobBench run with JobBench's own judge (job-bench-eval eval/run_judge.sh, through the
# judge_parallel.sh named by JOBBENCH_JUDGE_PARALLEL in ~/.config/dsh-bench/local.env; it carries the judge endpoint).
#
#   benchmarks/jobbench/grade.sh RUN_DIR [DATASET=~/job-bench-eval/dataset/main] [NGROUPS=2] [PER_GROUP=9]
#
# Builds RUN_DIR/grading/dataset/main/<task>/ from the dataset's task dir (task_folder, RUBRICS.json, ...) plus the
# run's workspace/output as model_output/$LABEL/. Symlinks in the output are NOT copied (an agent could point one at a
# host file); they are listed in RUN_DIR/grading/skipped-symlinks.txt. Scores: RUN_DIR/grading/scores.txt.
# Env: GRADING_DIR (default RUN_DIR/grading), ONLY (space-separated task dir names under RUN_DIR/tasks to grade),
#      RUBRICS_DIR (a rubric variant tree <dir>/<profession>/<taskN>/RUBRICS.json that replaces the dataset's, e.g.
#      agentic-evolution's attribution/jobbench_rubric_variants/task-instruction-aligned-v1/main), JUDGE_RESULTS_DIR.
# The final line is over every task of the run: a task with no judge report (no deliverables) counts as 0.
set -euo pipefail
[[ -f "$HOME/.config/dsh-bench/local.env" ]] && set -a && source "$HOME/.config/dsh-bench/local.env" && set +a
: "${JOBBENCH_JUDGE_PARALLEL:?set JOBBENCH_JUDGE_PARALLEL in ~/.config/dsh-bench/local.env (template: local.env.example)}"
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
  if [[ -n "${RUBRICS_DIR:-}" ]]; then cp "$RUBRICS_DIR/$id/RUBRICS.json" "$dest/RUBRICS.json"; fi
  mkdir -p "$dest/model_output/$LABEL"
  (cd "$task/workspace/output" && find . -type l) | sed "s|^\.|$id/output|" >> "$G/skipped-symlinks.txt"
  (cd "$task/workspace/output" && find . -type d -exec mkdir -p "$dest/model_output/$LABEL/{}" \; \
     && find . -type f -exec cp --no-dereference "{}" "$dest/model_output/$LABEL/{}" \;)
done
echo "[grade] $(ls -d "$G"/dataset/main/*/task* | wc -l) tasks staged, label $LABEL"
"$JOBBENCH_JUDGE_PARALLEL" "$G" "$LABEL" "$NGROUPS" "$PER_GROUP" | tee "$G/scores.txt"
python3 - "$G/dataset/main" "$LABEL" "${JUDGE_RESULTS_DIR:-eval_result_grok-4-6-high-cao}" <<'PY' | tee -a "$G/scores.txt"
import glob, json, os, sys
main, label, results = sys.argv[1:]
rows = []
for task in sorted(glob.glob(f"{main}/*/task*")):
    rubrics = json.load(open(f"{task}/RUBRICS.json"))
    rubrics = rubrics["rubrics"] if isinstance(rubrics, dict) else rubrics
    reports = glob.glob(f"{task}/{results}/eval_{label}/*_judge.json")
    if reports:
        d = json.load(open(reports[0])); rows.append((d["total_score"], d["max_score"], True))
    else:
        rows.append((0, sum(r["weight"] for r in rubrics), False))
print(f"all {len(rows)} tasks (missing = 0; graded {sum(g for *_, g in rows)}): macro {sum(s / m for s, m, _ in rows) / len(rows):.4f}, "
      f"pooled {sum(s for s, _, _ in rows) / sum(m for _, m, _ in rows):.4f}")
PY
