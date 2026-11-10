# JobBench failure analysis: instructions for each analyst

(Written for the analysis of `runs/jb-all65-lunahigh-subon-20261109T222237Z`; paths are relative to that run directory. Generate the digests first with `benchmarks/jobbench/trace_digest.py RUN --out RUN/analysis/digests`, then build the report with `benchmarks/jobbench/failure_report.py RUN/analysis`.)

Run: `~/dsh-bench-harness/runs/jb-all65-lunahigh-subon-20261109T222237Z` (DSH-based harness, GPT-5.6 Luna effort high,
subagents on, one attempt per task). Graded by JobBench's judge (grok-4.6) on the ORIGINAL rubrics. Analyse only these
original-rubric verdicts.

Goal: for each of your tasks, understand what the task asked, what the agent delivered, and why each failed rubric item
failed, then classify the causes. Be concrete and evidence-based. Cite the step number, file, or judge text you rely on.

## Where things are (per task, `<T>` = e.g. `biostatisticians__task1`, task id `biostatisticians/task1`)
- Digest (start here): `analysis/digests/<T>.md`. It holds the prompt, the task card (the designers' intent, never
  shown to the agent), the files the task expected the agent to find on the web, the staged inputs, every rubric item
  with the judge's verdict per criterion (reasoning and evidence for each failed one), the deliverables (extracted text,
  cut), the final chat message, and the trajectory (root agent, then subagents; arguments and outputs cut).
- Full deliverables: `tasks/<T>/workspace/output/`. The grader only sees this directory. Files elsewhere in
  `tasks/<T>/workspace/` were not graded.
- Staged inputs: `tasks/<T>/workspace/task_folder/`. Files the agent was expected to find online:
  `grading/dataset/main/<task id>/files_required_to_search/`.
- Full judge output: `grading/dataset/main/<task id>/eval_result_grok-4-6-high-cao/eval_gpt-5-6-luna-dsh-bench/grok-4-6_judge.json`.
- Full trajectories: `tasks/<T>/dsh-home/sessions/**/session.v2.jsonl` (JSON lines; `delegationDepth` 0 = root agent).
  Open these only when the digest's cut text is not enough to decide.

To read .docx/.xlsx/.pdf/.pptx in full, use
`~/dsh-bench-harness-inv/plugins/invariants/.venv/bin/python ~/dsh-bench-harness-inv/plugins/invariants/extract_text.py <file> 200000`.

## Cause classes (one per failed rubric item)
- **M Model mistake**: the agent had the information it needed (in the staged files, or already retrieved), but it
  reasoned, computed or interpreted wrongly, chose the wrong method, or did not follow an explicit instruction.
- **R Retrieval mistake**: the information was obtainable but the agent did not get it. Examples: it never opened the
  staged file that had it; it read only part of a long file; it did not search the web for a document the task needed;
  its search did not find a document that exists.
- **L Logging/recording mistake**: the agent's work shows it got this right (in its reasoning, scratch files, chat
  message or a subagent's result), but the graded deliverable does not contain it. Examples: missing from the output
  files, written outside `output/`, wrong file name or format, overwritten, truncated, or reported only in chat.
- **I Insufficient information**: the rubric expects a specific fact, number or choice that the prompt and staged files
  neither state nor imply, and that a competent professional could not reasonably find. Use this only when you checked
  the inputs.
- **S Skipped/incomplete scope**: the agent did not attempt a required part (a deliverable, section or analysis). It may
  have stopped early, judged the part optional, or run out of steps.
- **H Harness/environment**: a tool or environment problem caused it. Examples: tool errors, missing libraries, web or
  network failure, timeouts, a subagent that failed or whose result was lost, sandbox denials.
- **G Grading problem**: the deliverable does satisfy the criterion (cite where), but the judge failed it, or the
  rubric item contradicts the task instructions.

If two classes fit, pick the root cause. For example, a search that returned an error is H; never trying to search is R.

Task-level class:
- **A Correct**: every rubric item passed, or the only failures are class G.
- Otherwise the primary class is the one with the most lost weight; list the others as secondary.

## Output: one JSON file per task, `analysis/tasks/<T>.json`
```json
{
  "task": "<task id>",
  "score": "<total>/<max>",
  "goal": "2-3 sentences: what the task asked the agent to do and deliver",
  "delivered": "2-3 sentences: which files the agent produced and what they contain",
  "what_went_wrong": "2-5 sentences: the main reasons it lost points, specific (numbers, files, steps)",
  "primary_class": "A|M|R|L|I|S|H|G",
  "secondary_classes": ["..."],
  "lost_weight_by_class": {"M": 0, "R": 0, "L": 0, "I": 0, "S": 0, "H": 0, "G": 0},
  "failed_items": [
    {"rubric": "R<index>", "weight": 10, "lost": 10, "class": "M",
     "why": "1-2 sentences with evidence (step number, file, judge text)"}
  ],
  "subagent_notes": "how subagents were used and whether they helped or hurt; empty if none",
  "confidence": "high|medium|low"
}
```
`lost` = weight minus score for that rubric item. `lost_weight_by_class` sums `lost` per class.
`score` and the item numbers must match the judge file. Write valid JSON (check it with `python3 -m json.tool`).
