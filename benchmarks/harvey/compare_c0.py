"""Compare a dsh-bench Harvey run with C0 (Harvey's own harness as `harness_lab`, AHE campaigns, GPT-5.6 Luna, judge
gpt-5.6-sol high, helper claude-sonnet-5, all via CAO), task by task.

    python3 benchmarks/harvey/compare_c0.py RUN_DIR [RUN_DIR ...] [--out DIR] [--artifacts ...campaign-artifacts]

Several RUN_DIRs: our per-task value is the mean over the runs that graded the task (e.g. 3 runs vs C0's 3).
Results go to --out (default: the first RUN_DIR's grading/), as compare_c0.json and compare_c0.txt.

C0 trials: campaign 34 (the reference Luna run, reasoning summaries on: 100 firm-knowledge tasks x 3 trials) by default;
--with-c23-c24 adds the older runs without summaries. Per task, C0 is the mean over its trials; the comparison is
paired over tasks both sides graded.
"""

import argparse
import json
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

# Campaign 34 is the reference Luna run (reasoning summaries on, the endpoint this harness uses). Its C0 covers the
# 80 train and 20 validation tasks of splits-firm-knowledge-c34-80-20-70.json, 3 trials each.
C34 = [
    ("harvey-lab-campaign-34-c23-rerun-summaries-80-20-70", "C0-train"),
    ("harvey-lab-campaign-34-c23-rerun-summaries-80-20-70", "C0-validation"),
]
# Older Luna C0 runs WITHOUT reasoning summaries (c23 sent no `reasoning` field); --with-c23-c24 only.
# c23's C0-train-extra re-ran only tasks with 0/3 all-pass and is never used (it would bias the baseline).
C23_C24 = [
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-train"),
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-validation"),
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-final-test"),
    ("harvey-lab-campaign-24-cao-c23C0-heldout50", "C0-train"),
]


def c0_trials(artifacts: Path, evaluations: list[tuple[str, str]] = C34) -> dict[str, list[dict]]:
    per_task: dict[str, list[dict]] = defaultdict(list)
    for campaign, evaluation in evaluations:
        root = artifacts / campaign / "evaluations" / evaluation
        result = json.loads((root / "evaluation_result.json").read_text())
        for fact in result["trial_facts"]:
            unit = json.loads((root / "units" / fact["unit_id"] / "unit.json").read_text())
            per_task[unit["task_id"]].append({"all_pass": fact["outcome"] == "all_pass", "score": fact["score"],
                                              "source": f"{campaign.split('-')[3]}:{evaluation}"})
    return per_task


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--artifacts", type=Path,
                        default=Path("~/AHE_Harvey_cao/harvey-ahe-project/campaign-artifacts").expanduser())
    parser.add_argument("--with-c23-c24", action="store_true", help="also use the c23/c24 C0 runs (no summaries)")
    args = parser.parse_args()
    graded: dict[str, list[dict]] = defaultdict(list)
    for run_dir in args.run_dirs:
        for r in json.loads((run_dir / "grading/scores.json").read_text())["tasks"]:
            graded[r["task"]].append(r)
    ours = {task: {"all_pass": st.mean(r["all_pass"] for r in rs), "criterion_pass_rate": st.mean(r["criterion_pass_rate"] for r in rs),
                   "runs": len(rs)} for task, rs in graded.items()}
    c0 = c0_trials(args.artifacts, C34 + (C23_C24 if args.with_c23_c24 else []))
    common = sorted(set(ours) & set(c0))
    rows = []
    for task in common:
        trials = c0[task]
        rows.append({"task": task, "ours_runs": ours[task]["runs"], "ours_all_pass": float(ours[task]["all_pass"]),
                     "ours_criterion": ours[task]["criterion_pass_rate"],
                     "c0_all_pass": st.mean(t["all_pass"] for t in trials), "c0_criterion": st.mean(t["score"] for t in trials),
                     "c0_trials": len(trials)})
    random.seed(0)

    def paired(key_ours: str, key_c0: str) -> str:
        diffs = [r[key_ours] - r[key_c0] for r in rows]
        boots = sorted(st.mean(random.choices(diffs, k=len(diffs))) for _ in range(10000))
        better, worse = sum(d > 1e-9 for d in diffs), sum(d < -1e-9 for d in diffs)
        return (f"ours {st.mean(r[key_ours] for r in rows):.3f} vs C0 {st.mean(r[key_c0] for r in rows):.3f}: "
                f"{st.mean(diffs):+.3f}, 95% CI [{boots[250]:+.3f}, {boots[9750]:+.3f}], "
                f"better/equal/worse {better}/{len(diffs) - better - worse}/{worse}")

    lines = [f"our runs: {len(args.run_dirs)}; tasks graded by us: {len(ours)} (runs per task: "
             f"{dict(sorted(Counter(r['ours_runs'] for r in rows).items()))} on the common tasks); with C0 trials: {len(common)} "
             f"(C0 trials per task: {dict(sorted(Counter(r['c0_trials'] for r in rows).items()))})"]
    lines.append("all-pass:        " + paired("ours_all_pass", "c0_all_pass"))
    lines.append("criterion pass:  " + paired("ours_criterion", "c0_criterion"))
    text = "\n".join(lines)
    out = args.out or args.run_dirs[0] / "grading"
    out.mkdir(parents=True, exist_ok=True)
    (out / "compare_c0.json").write_text(json.dumps({"runs": [str(r) for r in args.run_dirs], "summary": lines,
                                                     "tasks": rows}, indent=2) + "\n")
    (out / "compare_c0.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
