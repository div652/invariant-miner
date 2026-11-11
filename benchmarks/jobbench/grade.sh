#!/usr/bin/env bash
# Grade a dsh-bench JobBench run with JobBench's own judge (job-bench-eval eval/run_judge.sh, through the
# judge_parallel.sh named by JOBBENCH_JUDGE_PARALLEL in ~/.config/dsh-bench/local.env; it carries the judge endpoint).
#
#   benchmarks/jobbench/grade.sh [--rubrics original|v1|DIR] RUN_DIR [DATASET=~/job-bench-eval/dataset/main] [NGROUPS=2] [PER_GROUP=9]
#
# --rubrics picks the rubric set the judge grades against (default: original):
#   original  the dataset's own RUBRICS.json;                                   results in RUN_DIR/grading/
#   v1        agentic-evolution's task-instruction-aligned v1 rubrics, from JOBBENCH_V1_RUBRICS_DIR in local.env
#             (default ~/agentic-evolution/attribution/jobbench_rubric_variants/task-instruction-aligned-v1/main);
#                                                                               results in RUN_DIR/grading-v1/
#   DIR       any other rubric tree DIR/<profession>/<taskN>/RUBRICS.json; needs GRADING_DIR (results go there)
# Each set has its own grading directory, so one run can be graded on both and the results never mix. The set used is
# recorded in <grading dir>/rubrics.json (name, source directory, and its git commit when it is in a git checkout).
#
# Builds <grading dir>/dataset/main/<task>/ from the dataset's task dir (task_folder, RUBRICS.json, ...; RUBRICS.json
# replaced by the chosen set's) plus the run's workspace/output as model_output/$LABEL/. Symlinks in the output are NOT
# copied (an agent could point one at a host file); they are listed in <grading dir>/skipped-symlinks.txt. Scores:
# <grading dir>/scores.txt.
# Env: GRADING_DIR (overrides the grading directory), ONLY (space-separated task dir names under RUN_DIR/tasks to
#      grade), JUDGE_RESULTS_DIR.
# The final line is over every task of the run: a task with no judge report (no deliverables) counts as 0.
set -euo pipefail
[[ -f "$HOME/.config/dsh-bench/local.env" ]] && set -a && source "$HOME/.config/dsh-bench/local.env" && set +a
: "${JOBBENCH_JUDGE_PARALLEL:?set JOBBENCH_JUDGE_PARALLEL in ~/.config/dsh-bench/local.env (template: local.env.example)}"
die() { echo "[grade] $*" >&2; exit 1; }

RUBRICS=original
if [[ "${1:-}" == --rubrics ]]; then [[ $# -ge 2 ]] || die "--rubrics needs original, v1 or a directory"; RUBRICS="$2"; shift 2
elif [[ "${1:-}" == --rubrics=* ]]; then RUBRICS="${1#--rubrics=}"; shift
fi
[[ $# -ge 1 && "$1" != -* ]] || die "usage: grade.sh [--rubrics original|v1|DIR] RUN_DIR [DATASET] [NGROUPS] [PER_GROUP]"
[[ -z "${RUBRICS_DIR:-}" ]] || die "RUBRICS_DIR is replaced by --rubrics DIR (with GRADING_DIR)"
RUN="$(cd "$1" && pwd)"; DATASET="$(cd "${2:-$HOME/job-bench-eval/dataset/main}" && pwd)"
case "$RUBRICS" in
  original) NAME=original; SRC=""; DEFAULT_G="$RUN/grading" ;;
  v1) NAME=v1; SRC="${JOBBENCH_V1_RUBRICS_DIR:-$HOME/agentic-evolution/attribution/jobbench_rubric_variants/task-instruction-aligned-v1/main}"
      DEFAULT_G="$RUN/grading-v1" ;;
  *) NAME=custom; SRC="$RUBRICS"; DEFAULT_G=""
     [[ -n "${GRADING_DIR:-}" ]] || die "--rubrics DIR needs GRADING_DIR (where this set's results go)" ;;
esac
if [[ -n "$SRC" ]]; then
  [[ -d "$SRC" ]] || die "rubric set $NAME: no directory $SRC (set JOBBENCH_V1_RUBRICS_DIR in local.env)"
  SRC="$(cd "$SRC" && pwd)"
fi
[[ "$(realpath -m "${GRADING_DIR:-$DEFAULT_G}")" != "$RUN/tasks/"* ]] || die "GRADING_DIR must not be inside a task dir"
NGROUPS="${3:-2}"; PER_GROUP="${4:-9}"
LABEL="${LABEL:-gpt-5-6-luna-dsh-bench}"
G="$(realpath -m "${GRADING_DIR:-$DEFAULT_G}")"   # absolute: the copies below run from inside each output dir
[[ ! -e "$G" ]] || die "$G exists; remove it to re-grade"
selected() {  # the run's finished task dirs to grade (ONLY narrows them)
  local task
  for task in "$RUN"/tasks/*/; do
    if [[ -n "${ONLY:-}" && " $ONLY " != *" $(basename "$task") "* ]]; then continue; fi
    [[ -f "$task/run.json" ]] || { echo "skip (unfinished): $task" >&2; continue; }
    echo "$task"
  done
}
task_id() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["task_id"])' "$1/spec.json"; }
if [[ -n "$SRC" ]]; then  # the whole set must cover the run before anything is staged
  while read -r task; do
    [[ -f "$SRC/$(task_id "$task")/RUBRICS.json" ]] || die "rubric set $NAME has no $(task_id "$task")/RUBRICS.json under $SRC"
  done < <(selected 2>/dev/null)
fi
mkdir -p "$G/dataset/main"
: > "$G/skipped-symlinks.txt"
python3 - "$G/rubrics.json" "$NAME" "$SRC" "$DATASET" <<'PY'
import json, subprocess, sys
out, name, src, dataset = sys.argv[1:]
where = src or dataset
commit = subprocess.run(["git", "-C", where, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
json.dump({"rubrics": name, "source": src or f"{dataset}/<task>/RUBRICS.json", "git_commit": commit or None},
          open(out, "w"), indent=2)
PY
while read -r task; do
  id="$(task_id "$task")"
  dest="$G/dataset/main/$id"
  mkdir -p "$dest"
  for item in "$DATASET/$id"/*; do
    [[ "$(basename "$item")" == model_output ]] && continue
    cp -r "$item" "$dest/"
  done
  if [[ -n "$SRC" ]]; then cp "$SRC/$id/RUBRICS.json" "$dest/RUBRICS.json"; fi
  mkdir -p "$dest/model_output/$LABEL"
  (cd "$task/workspace/output" && find . -type l) | sed "s|^\.|$id/output|" >> "$G/skipped-symlinks.txt"
  (cd "$task/workspace/output" && find . -type d -exec mkdir -p "$dest/model_output/$LABEL/{}" \; \
     && find . -type f -exec cp --no-dereference "{}" "$dest/model_output/$LABEL/{}" \;)
done < <(selected)
echo "[grade] $(ls -d "$G"/dataset/main/*/task* | wc -l) tasks staged, label $LABEL, rubrics $NAME${SRC:+ ($SRC)}"
"$JOBBENCH_JUDGE_PARALLEL" "$G" "$LABEL" "$NGROUPS" "$PER_GROUP" | tee "$G/scores.txt"
python3 - "$G/dataset/main" "$LABEL" "${JUDGE_RESULTS_DIR:-eval_result_grok-4-6-high-cao}" "$NAME" <<'PY' | tee -a "$G/scores.txt"
import glob, json, os, sys
main, label, results, rubric_set = sys.argv[1:]
rows = []
for task in sorted(glob.glob(f"{main}/*/task*")):
    rubrics = json.load(open(f"{task}/RUBRICS.json"))
    rubrics = rubrics["rubrics"] if isinstance(rubrics, dict) else rubrics
    reports = glob.glob(f"{task}/{results}/eval_{label}/*_judge.json")
    if reports:
        d = json.load(open(reports[0])); rows.append((d["total_score"], d["max_score"], True))
    else:
        rows.append((0, sum(r["weight"] for r in rubrics), False))
print(f"all {len(rows)} tasks, {rubric_set} rubrics (missing = 0; graded {sum(g for *_, g in rows)}): "
      f"macro {sum(s / m for s, m, _ in rows) / len(rows):.4f}, pooled {sum(s for s, _, _ in rows) / sum(m for _, m, _ in rows):.4f}")
PY
