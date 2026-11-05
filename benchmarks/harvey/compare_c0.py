"""Compare a dsh-bench Harvey run with C0 (Harvey's own harness as `harness_lab`, AHE campaigns, GPT-5.6 Luna, judge
gpt-5.6-sol high, helper claude-sonnet-5, all via CAO), task by task.

    python3 benchmarks/harvey/compare_c0.py RUN_DIR [--artifacts ~/AHE_Harvey_cao/harvey-ahe-project/campaign-artifacts]

C0 trials come from these evaluations (agent gpt-5.6-luna in all of them): campaign 23 C0-train / C0-validation /
C0-final-test, campaign 24 C0-train (held-out 50), campaign 34 C0-train / C0-validation (campaign 23 rerun after the
reasoning-summary fix). c23's C0-train-extra is left out: it re-ran only tasks with 0/3 all-pass, so it would bias
the baseline. Per task, C0 is the mean over its trials; the comparison is paired over tasks both sides graded.
"""

import argparse
import json
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

EVALUATIONS = [
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-train"),
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-validation"),
    ("harvey-lab-campaign-23-cao-luna-allpass-80-20-20", "C0-final-test"),
    ("harvey-lab-campaign-24-cao-c23C0-heldout50", "C0-train"),
    ("harvey-lab-campaign-34-c23-rerun-summaries-80-20-70", "C0-train"),
    ("harvey-lab-campaign-34-c23-rerun-summaries-80-20-70", "C0-validation"),
]


def c0_trials(artifacts: Path) -> dict[str, list[dict]]:
    per_task: dict[str, list[dict]] = defaultdict(list)
    for campaign, evaluation in EVALUATIONS:
        root = artifacts / campaign / "evaluations" / evaluation
        result = json.loads((root / "evaluation_result.json").read_text())
        for fact in result["trial_facts"]:
            unit = json.loads((root / "units" / fact["unit_id"] / "unit.json").read_text())
            per_task[unit["task_id"]].append({"all_pass": fact["outcome"] == "all_pass", "score": fact["score"],
                                              "source": f"{campaign.split('-')[3]}:{evaluation}"})
    return per_task


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--artifacts", type=Path,
                        default=Path("~/AHE_Harvey_cao/harvey-ahe-project/campaign-artifacts").expanduser())
    args = parser.parse_args()
    ours = {r["task"]: r for r in json.loads((args.run_dir / "grading/scores.json").read_text())["tasks"]}
    c0 = c0_trials(args.artifacts)
    common = sorted(set(ours) & set(c0))
    rows = []
    for task in common:
        trials = c0[task]
        rows.append({"task": task, "ours_all_pass": float(ours[task]["all_pass"]),
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

    lines = [f"tasks graded by us: {len(ours)}; with C0 trials: {len(common)} "
             f"(C0 trials per task: {dict(sorted(Counter(r['c0_trials'] for r in rows).items()))})"]
    lines.append("all-pass:        " + paired("ours_all_pass", "c0_all_pass"))
    lines.append("criterion pass:  " + paired("ours_criterion", "c0_criterion"))
    text = "\n".join(lines)
    (args.run_dir / "grading/compare_c0.json").write_text(json.dumps({"summary": lines, "tasks": rows}, indent=2) + "\n")
    (args.run_dir / "grading/compare_c0.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
