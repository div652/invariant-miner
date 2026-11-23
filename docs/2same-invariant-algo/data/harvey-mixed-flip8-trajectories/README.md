# Harvey mixed:flip: the 8 tasks, 10 runs each

The 8 harvey-mixed train tasks of the named subset `mixed:flip` (all-pass in 2-4 of the first five Luna-high reference runs), each run 10 times with the same harness: GPT-5.6 Luna high (models/luna-cao.json), base harness at main 2817664, no skills, 200 steps / 2 h, graded by Harvey's grader (gpt-5.6-sol high). run1-run5 = the mixed-200 reference runs (benchmarks/harvey-mixed/RESULTS.md), run6-run10 = five more runs of these 8 (2026-11-18).

P = every criterion met. Run directories (originals, in `~/dsh-bench-harness/runs/`): see `manifest.json` (`runs`).

| Task | Passes | run1 | run2 | run3 | run4 | run5 | run6 | run7 | run8 | run9 | run10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `contracts/banking/account-control-agreement-first-turn-redline/scenario-01` | 9/10 | **P** 30/30 | **P** 30/30 | . 28/30 | **P** 30/30 | **P** 30/30 | **P** 30/30 | **P** 30/30 | **P** 30/30 | **P** 30/30 | **P** 30/30 |
| `corporate-ma/draft-markup-of-stock-purchase-agreement-provisions` | 9/10 | . 56/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 | **P** 59/59 |
| `firm-knowledge/tasks/111` | 9/10 | . 0/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 | **P** 3/3 |
| `corporate-ma/draft-markup-of-transition-services-agreement-tsa` | 7/10 | **P** 56/56 | . 55/56 | . 52/56 | **P** 56/56 | **P** 56/56 | **P** 56/56 | **P** 56/56 | **P** 56/56 | **P** 56/56 | . 54/56 |
| `intellectual-property/review-data-processing-agreement-template-against-eu-and-us-requirements` | 4/10 | **P** 47/47 | **P** 47/47 | . 46/47 | . 44/47 | **P** 47/47 | . 45/47 | **P** 47/47 | . 45/47 | . 45/47 | . 45/47 |
| `contracts/banking/repo-securities-lending-subsequent-turn-redline/scenario-01` | 3/10 | . 43/48 | . 46/48 | . 45/48 | **P** 48/48 | **P** 48/48 | . 46/48 | . 44/48 | . 45/48 | . 47/48 | **P** 48/48 |
| `contracts/commercial-vendor-customer/saas-api-subscription-subsequent-turn-redline/scenario-01` | 2/10 | . 54/56 | **P** 56/56 | **P** 56/56 | . 53/56 | . 38/56 | . 53/56 | . 53/56 | . 54/56 | . 54/56 | . 54/56 |
| `firm-knowledge/tasks/065` | 2/10 | **P** 6/6 | **P** 6/6 | . 5/6 | . 5/6 | . 5/6 | . 4/6 | . 4/6 | . 4/6 | . 3/6 | . 3/6 |

## Layout

```
manifest.json         per task and run: verdict, finish reason, agent time, source directory, files
system_prompt.md      the system prompt (same for every task and run)
<task folder>/prompt.txt
<task folder>/runN/
    session.v2.jsonl  raw trajectory (DSH session events)
    readable.md       the same as a readable trace
    answer.json       final answer and how the turn ended
    run.json          run metadata (finish reason, timings)
    grading.json      per-criterion verdicts with the judge's reasons
    output/           the deliverables
```
