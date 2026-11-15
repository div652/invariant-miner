# harvey-mixed: 200 Harvey LAB tasks across all practice areas

A second Harvey dataset (user, 2026-11-15): not only firm-knowledge, but 200 tasks drawn at random from the whole
Harvey LAB task set. It runs on exactly the same setup as [../harvey](../harvey) (same pinned checkout, image,
prepared system prompt, `harvey-write` rule, grader and judge); only the task list differs.

## The sample

`sample-200.json` (and `tasks-200.txt`), made by `make_sample.py` (seed 20261115, reproducible):
- **Pool:** all 2,010 tasks of the pinned checkout (`work/harvey-labs` at 4743403f; upstream main is 5 commits ahead
  with identical tasks, see below), in 27 practice areas, **minus the 90 firm-knowledge tasks held out in the AHE split**
  (its val + test), so this set never overlaps the firm-knowledge evaluation tasks: 1,920 tasks.
- **Draw:** random, stratified by practice area: each area gets its share of 200 (largest remainder), drawn from its
  sorted task ids with `random.Random(seed)`. Every area appears, in proportion to its size.

| Area | Tasks | Area | Tasks |
|---|---|---|---|
| contracts | 52 | funds-asset-management | 7 |
| corporate-ma | 17 | data-privacy-cybersecurity, environmental-esg, litigation-dispute-resolution, real-estate | 5 each |
| firm-knowledge (train-side only) | 17 | 9 areas (arbitration, banking, bankruptcy, capital markets, ECVC, employment, healthcare, trade, tax) | 4 each |
| intellectual-property | 15 | antitrust, energy, immigration, insurance, structured finance | 3 each |
| corporate-governance | 10 | white-collar | 2 |
| trusts-estates-private-client | 8 | diligence | 1 |

- **Deliverables:** 151 `.docx`, 18 `.md` (17 of them firm-knowledge), 3 `.xlsx`; 52 tasks list none in task.json
  (their instructions name the file).
- **Rubrics are large:** 11,160 criteria in all, median 53 per task, up to 653 (`diligence/restaurant-pe-buyout`,
  which also has 3,378 documents). Firm-knowledge-250 has about 1,300 criteria in all, so grading one run of this set
  costs about 8.5 times as many judge calls.
- **Documents:** each task's own `documents/` folder (median 8 files), hard-linked read-only into the workspace;
  firm-knowledge tasks use the shared DMS as before.

## Run it

```bash
python3 benchmarks/harvey/make_specs.py --tasks mixed200 --out runs/<run>/specs     # model etc. as for Harvey
benchmarks/harvey/run.sh runs/<run>/specs runs/<run> 20
work/harvey-labs/.venv/bin/python benchmarks/harvey/grade.py runs/<run> [--task-workers 4]
```

`--tasks mixed200` is a named task list (`benchmarks/harvey/make_specs.py` `TASK_LISTS`): ids plus each task.json's
sha256, checked when the specs are written. Setup is Harvey's (`benchmarks/harvey/setup.sh`); nothing else to install.
Grading .docx needs pandoc >= 3.5 on the host (3.11 installed).

## Smoke (2026-11-15, GPT-5.6 Luna high, base harness)

`runs/hv-mixed-smoke-20261115T074039Z`, 2 tasks, both completed and graded without errors:

| Task | Deliverable | Steps / time | Score |
|---|---|---|---|
| environmental-esg/identify-issues-in-draft-permit-application | `application-issue-memorandum.docx` | 22 / 345 s | 26/31 |
| contracts/ip-licensing/license-agreement-first-turn-redline/scenario-05 | `counter-turn-redline-v3-rh.docx` + cover note | 36 / 363 s | 28/29 |

The agent built both .docx files with python-docx in bash, into `output/`. The "redline" has **no tracked changes**
(0 `w:ins` / `w:del`): without Harvey's docx skill it wrote a clean document that describes its changes, and the judge
still passed 28 of 29 criteria.

## Open decisions

- **Skills.** Harvey's own harness loads its docx / xlsx / pptx skills by default (scripts for tracked-changes redlines,
  comments, template filling, validation). Our Harvey setup runs without them (user's decision for firm-knowledge,
  benchmarks/harvey/CHECKLIST.md row 6). On this set, 151 of 200 deliverables are .docx and many tasks are redlines, so
  skills could matter much more here than on firm-knowledge.
- **Splits.** The 200 are one list; no train / val / test yet.
- **Upstream.** harvey-labs main is 5 commits past our pin (2026-11-11), with the same 2,010 tasks. One changes grading:
  a criterion whose deliverable is missing now fails without a judge call (#218). We keep the pin, so the grader is the
  same as for the firm-knowledge runs.
