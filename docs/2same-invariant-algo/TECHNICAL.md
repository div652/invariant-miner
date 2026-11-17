# Same-task invariant mining: technical design

How the algorithm in [DESIGN.md](DESIGN.md) is built. Sections 1-7 are built (package `invariant_mining/`, tests
`tests/test_im_*.py`); section 8 (aggregation) is not. Values marked *default* are configuration with a starting value,
not decisions from the conversation ([QNA.md](QNA.md)).

## 1. Placement

- Code: a Python package `invariant_mining/` at the root of branch `2sameInvariantAlgo` (Python 3.12). Standard library
  everywhere (`urllib` for the OpenAI Responses API, `sqlite3` for state) except the Claude client, which uses the
  official `anthropic` SDK: `uv venv work/im-venv && uv pip install --python work/im-venv/bin/python anthropic`, and run
  with `work/im-venv/bin/python -m invariant_mining ...`. The tests need no SDK. It reads DSH session logs; it never
  runs DSH.
- It is benchmark-agnostic and must pass `tests/test_layout.py` (no benchmark names in it). Benchmark-specific glue
  (e.g. building a manifest from a benchmark's run directories and grades) goes in `benchmarks/<name>/`.
- Run outputs go to `runs/` (gitignored).

```
invariant_mining/
  trajectory.py   session.v2.jsonl -> normalized trajectory; locations and their order
  tools.py        the read-only trajectory tools
  config.py       the default configuration (models, roles, budgets, limits)
  models.py       conversations over the CAO gateway: OpenAI Responses (GPT, plain HTTP); key lookup
  claude_client.py  Claude conversations through the anthropic SDK (Messages API)
  agent.py        the job agent loop: budgets, context guard, notes, submit validation, transcripts
  jobs.py         job kinds: inputs -> prompt, output schema (F1 propose, F1 reword, F2, F3, too-narrow)
  prompts/        one system prompt per job kind + a shared preamble
  store.py        SQLite state: trajectories, tasks, invariants, cells, triggers, validations, jobs, events
  rules.py        the programmatic rules: outcome -> points / removal / reword, scheduling
  pipeline.py     scheduler: runs pending work with a concurrency limit; resumable
  report.py       report.md + report.json
  aggregate.py    later: union across tasks with the semantic judge (section 8)
  cli.py          prepare / run / report / job
tests/            (repo tests/) im_fixtures.py + test_im_*.py: scripted-model tests, no real model calls
```

## 2. Trajectories

### 2.1 Input: DSH session logs

One `session.v2.jsonl` per agent (subagents are off in the core, so one per run). Facts below were checked on Harvey
FK-250 Luna-high runs (250 sessions).

| Record type | Used for |
|---|---|
| `request/header` | `data.header.system` (system prompt), `data.header.tools[]` (name, description, parameters); `data.header.config` (model, effort) as metadata |
| `request/context` | `data.contextWindow` as metadata |
| `user/message` | `data.content[].text`, in order: the task, then DSH's runtime-context message (file policy), sometimes later messages (e.g. goal rounds); 530 in 250 sessions |
| `assistant/message` | `data.step`, `data.message.content[]` in order: `reasoning` (summary text), `text`, `tool-call` (`id`, `name`, `arguments` as a JSON string) |
| `tool/result` | `data.step`, `data.message.content[]`: `tool-result` with `toolCallId`, `content[].text`, `isError` |
| ignored | `stream` chunks and `source.replayState` (encrypted reasoning), `step/*`, `turn/*`, `todo/write` (same as the `todo_write` call), `agent/inbox/spliced` (the queued task, same as the first user message), `session*`, `permission/preset`, `sandbox/mode`, `approval/policy`, `goal/change`, `llm/retry*`, `assistant/attempt` (failed attempts the agent never saw) |

Sizes (Harvey FK-250 Luna high, 120 trajectories): agent context at the last step median 209K tokens, p90 310K, max
414K; model steps median 31, p90 53, max 75; tool outputs are capped by DSH at 50,000 characters each; reasoning
summaries ~7.6K and call arguments ~26K characters per trajectory (median); ~95% of the text is tool output.

### 2.2 Normalized trajectory

`prepare` turns each session log into `trajectories/<id>.json`: a flat list of **items** in the order the agent saw
them, plus metadata.

```json
{"id": "...", "task_id": "...", "label": "pass|fail", "source": "<path to session.v2.jsonl>",
 "meta": {"model": "...", "effort": "...", "context_window": 922000, "steps": 31, "est_tokens": 208973},
 "items": [
   {"loc": "sys",     "kind": "system",    "text": "..."},
   {"loc": "tools",   "kind": "tools",     "text": "<name: description + parameters, one block per tool>"},
   {"loc": "u1",      "kind": "user",      "text": "<the task>"},
   {"loc": "u2",      "kind": "user",      "text": "<runtime context>"},
   {"loc": "s1.r",    "kind": "reasoning", "text": "..."},
   {"loc": "s1.c1",   "kind": "call",      "name": "grep", "text": "<arguments>"},
   {"loc": "s1.o1",   "kind": "output",    "text": "...", "is_error": false},
   {"loc": "s2.r",    "kind": "reasoning", "text": "..."}
 ]}
```

### 2.3 Locations

- `sys` system prompt; `tools` tool descriptions; `uN` the N-th user message (numbered over the whole trajectory);
  `s<n>.r` reasoning of step n (its reasoning blocks joined); `s<n>.t` its text; `s<n>.c<k>` its k-th tool call;
  `s<n>.o<k>` the output of that call. Optional `#<offset>` = character offset inside the item (long outputs).
- **Order** = position in `items`, which follows the session log: within a step, the assistant message's blocks in
  their order (reasoning, text, calls), then the outputs in call order; user messages where they arrived.
- Uses: F2's first location; F3's "after" and "only before" (judged by F3 with these locations as evidence); the
  first-violation flag (earliest observation location among a failing run's violated invariants); evidence in reports.
- φ (empty observation) has the location `start` (before `sys`).

## 3. Job agents

### 3.1 Loop (`agent.py`)

- A job = a fresh conversation: the system prompt of its kind, one user message with the job's inputs and its
  trajectories' sizes (items, steps, estimated tokens, largest outputs), and the tools of 3.3.
- Loop: call the model; run its tool calls; append the results; stop when `submit` succeeds.
- **Budgets** (*default*): F1 propose 150 model steps; F1 reword 60; F2, F3, too-narrow 40; 30 min wall time per job.
- **Context guard** (*default*): when the conversation passes 60% of the model's prompt window, the oldest tool results
  (other than `read_notes`) are replaced by `[elided: <tool and arguments>; read again if needed]`. Notes survive.
- **Submit**: the argument is validated against the job kind's JSON schema (3.4) and its locations against the
  trajectory; on an error the agent gets the error and continues. After 3 invalid submits, or when a budget runs out,
  the job fails.
- **Failures**: a failed job is retried once as a fresh job (*default*); if it fails again, the cell or task gets the
  outcome `job_error` (no change to points, logged). A reword or validation job that fails counts as a failed
  rewording attempt (*default*).
- Each job keeps `jobs/<job_id>/input.json`, `transcript.jsonl`, `notes.md`, `output.json` (or `error.txt`). The
  transcript has one record per model step: the model's response in full (encrypted reasoning and thinking signatures
  removed) and each tool result as tool, arguments, size and first 500 characters (tool results are deterministic given
  the trajectory, so they can be recomputed; storing them whole would cost about 1 MB per job). A retried job gets its
  own directory (`<job_id>-retry1`).

### 3.2 Model clients (`models.py`)

Both through the CAO gateway (`http://127.0.0.1:4141`, key from `$DSH_BENCH_CAO_KEY_FILE`), the request shapes of the
repo's `models/luna-cao.json` and `models/opus55-max-cao.json`:

| Model | API | Settings |
|---|---|---|
| GPT-5.6 Luna (`gpt-5.6-luna`) | OpenAI Responses, `/v1/responses` | `reasoning: {effort: high, summary: auto}`, `include: [reasoning.encrypted_content]`, `store: false`; the previous output items (reasoning items with their encrypted content, function calls) are sent back each turn with the `function_call_output` items; tools with `strict: false` |
| Claude Opus 5.5 (`claude-opus-5-5`) | Anthropic Messages, `/v1/messages`, through the `anthropic` SDK (streaming) | `thinking: {type: adaptive, display: summarized}`, `output_config: {effort: high}` for every job kind (DESIGN.md section 4), the assistant's content blocks sent back unchanged each turn (thinking blocks keep their signatures) |

Retries (as in the model files): rate limits, 5xx, timeouts, transport errors, empty responses, `INVALID_REQUEST`, and
Anthropic's mid-stream `api_error`; 5 retries with backoff. A Claude `refusal` stop fails the job (retried once as a
fresh job, then a job error): the gateway rejects the server-side refusal `fallbacks` parameter (checked 2026-11-17,
"Extra inputs are not permitted"). A Claude response cut at `max_tokens` (64,000) also fails the job. The context guard
edits earlier tool results; on Opus 5.5 such an edit can make earlier thinking blocks unreadable to the model, and it
only happens past 60% of the window. Concurrency: one limit on running jobs (*default* 20; CAO has
been run at 24 concurrent requests). Model per job kind is configuration (`config.json`).

### 3.3 Tools (`tools.py`)

Read-only, over the normalized trajectories only. In F1 every trajectory tool takes `run: "A" | "B"` (A = P1, B = P2); other jobs
see one trajectory and the argument is absent.

| Tool | Returns |
|---|---|
| `overview(run)` | item and step counts, estimated tokens; the user messages (first 300 characters each); one line per step: location, the first 150 characters of the reasoning, each call (name + first 100 characters of its arguments), each output's size and error flag |
| `read_context(run, part, offset, length)` | `part` = `sys`, `tools` or `uN`, paged (*default* page 20,000 characters) |
| `read_steps(run, from_step, to_step)` | the steps' reasoning and text in full, calls with arguments up to 4,000 characters, outputs cut to 2,000 characters with "(N more characters: read_output)"; at most 40,000 characters per call |
| `read_output(run, loc, offset, length)` | one item's text from `offset`, at most 20,000 characters |
| `search(run, pattern, regex, kinds, max_hits)` | matches with their location (`loc#offset`) and 200 characters around each; `kinds` filters item kinds; *default* 50 hits |
| `note(text)`, `read_notes()` | append to / read the job's notes |
| `submit(output)` | validates and stores the job's output (3.1) |

No shell, no file system, no web.

### 3.4 Job kinds: inputs and outputs (`jobs.py`)

**F1 propose.** Input: P1 (A), P2 (B). Output:

```json
{"invariants": [
   {"id": "i1",
    "observation": [{"fact": "keyword search results over the documents", "source": "tool_result",
                     "reason": "the hit counts are what the choice is based on"}],
    "action": {"text": "identifies the keyword with most hits", "purpose": "pick the search term that finds the relevant files"},
    "follows": [],
    "evidence": {"A": {"observation": "s4.o1", "action": "s5.r"}, "B": {"observation": "s3.o1", "action": "s4.r"}}}],
 "roles": [{"term": "keyword with most hits", "meaning": "the search term whose search returned the most matches"}]}
```

`observation: []` is φ. `source` is one of `environment`, `task`, `tool_result`, `reasoning`. `follows` lists the ids of
invariants this one chains from (information only). `evidence` (DESIGN.md 4.1): after
F1 the code checks it (each location exists in its trajectory; the observation's location comes before the action's in
A and in B) and logs an `f1_evidence_invalid` event on a failure, nothing more.

The outputs of F2, F3 and the too-narrow check are strict (DESIGN.md principle 7): the schemas allow only the fields and
values shown (`additionalProperties: false`, enums), so there is no "unclear", "partly" or confidence field.

**F2 seen?** Input: the facts' texts (nothing else of the invariant), one trajectory. Output:
`{"seen": true, "location": "s7.o2", "evidence": [{"fact": 0, "location": "s7.o2#1200", "quote": "..."}]}` (`location`
null when not seen).

**F3 followed?** Input: the facts' texts, the action's text, F2's location, one trajectory. Output:
`{"outcome": "followed" | "not_followed" | "only_before" | "pinning_wrong", "action_location": "s9.c1" | null, "quote": "..."}`.

**Too-narrow check.** Input: facts, action text, purpose, F2's location (Opus's on a passing run, after the re-check;
Luna's on a failing run), one trajectory. Question: did an action that achieves the same purpose happen after that
location? Output: `{"purpose_achieved_otherwise": true, "location": "s9.c2" | null, "quote": "..."}`.

**F1 reword.** Input: the invariant (facts, reasons, action, purpose), the triggering trajectory, the location from the
too-narrow check, the note that the invariant was learnt from earlier runs of this task where it holds; on the second
attempt also the first attempt's action and the failed validation check (trajectory, F2/F3 verdict). Output:
`{"action": {"text": "...", "purpose": "..."}}`.

### 3.5 Prompts (`prompts/`)

`preamble.md` (shared): what a trajectory is (agent, steps, reasoning summaries, calls, outputs), the location format,
the tools, that trajectories may be too long to read whole (read the step overview and reasoning first, open outputs
when needed, take notes), and that the answer goes through `submit`. Then one file per job kind (`f1_propose.md`,
`f1_reword.md`, `f2_seen.md`, `f3_followed.md`, `too_narrow.md`) with that kind's rules, taken from DESIGN.md
section 4 and quoting its examples. The F2, F3 and too-narrow prompts require exactly one of the given answers, decided
on the most direct reading of the evidence, without hedging (DESIGN.md principle 7). Prompts are versioned with the
code; each job records the sha256 of the prompt it used.

## 4. State and scheduling

### 4.1 Store (`store.py`): `runs/<name>/state.sqlite`

| Table | Columns |
|---|---|
| `trajectories` | id, task_id, label, source, json_path, steps, est_tokens |
| `tasks` | task_id, p1, p2, status, benchmark_context |
| `invariants` | id, task_id, observation_json, action, purpose, follows_json, evidence_json, status (`active`, `removed`, `retired`), parent_id, origin (`propose`, `reword`), reword_attempt, created_job |
| `cells` | invariant_id, trajectory_id, label, stage (`f2`, `f3`, `recheck_f2`, `recheck_f3`, `too_narrow`), f2_seen, f2_location, f3_outcome, f3_action_location, recheck_f2_seen, recheck_f2_location, recheck_f3_outcome, recheck_f3_action_location, too_narrow, too_narrow_location, final_outcome (`followed`, `not_followed`, `purpose_otherwise`, `only_before`, `not_seen`, `pinning_wrong`, `job_error`), status (`pending`, `running`, `done`, `cancelled`, `error`), job_ids |
| `triggers` | id, invariant_id, kind (`remove`, `reword`), trajectory_id, label, alt_location, status (`waiting`, `active`, `done`, `dropped`), stage (`reword`, `validate`), attempt, new_action, new_purpose, previous_json, result, new_invariant: the per-invariant queue of removals and rewords, processed one at a time, oldest first |
| `validations` | trigger_id, attempt, trajectory_id, stage (`f2`, `f3`), status, f2_seen, f2_location, f3_outcome, f3_action_location, ok: the F2/F3 checks of a rewording on P1, P2 (and the passing trigger); an attempt reuses earlier attempts' F2 verdicts, since the observation is unchanged |
| `jobs` | id, kind, role, model, effort, prompt_sha256, input_json, status, started, ended, model_steps, tokens_in, tokens_out, output_json, error |
| `events` | time, kind, task_id, invariant_id, trajectory_id, detail_json: every removal, retirement, reword (attempt, result), Luna/Opus disagreement, pinning wrong, only before, purpose achieved otherwise, F1 evidence check failure, job error |

### 4.2 Rules (`rules.py`)

Pure functions over the store, the rules of DESIGN.md sections 4-6:
- new invariant -> one `pending` cell per trajectory of its task other than P1, P2;
- F1 output -> the evidence check (3.4), events only;
- cell: F2 (skipped for φ) -> if seen, F3 -> on `not_followed`:
  - passing cell: re-check (Opus F2, F3) -> Opus's verdicts become final; if still `not_followed`: too-narrow check
    (after Opus's F2 location) -> `purpose_otherwise` (reword) or `not_followed` (remove);
  - failing cell: too-narrow check (after Luna's F2 location) -> `not_followed` (importance point) or
    `purpose_otherwise` (no point, and reword);
- removals and rewords of one invariant run one at a time; a trigger that arrives meanwhile waits, and is dropped if the
  invariant is removed or retired; removal or retirement cancels the invariant's pending cells;
- reword -> validation jobs (F2, F3 with Luna on P1, P2, and on the triggering trajectory when it passed) -> retire +
  new invariant; or a second attempt; or, after two failures, remove (passing trigger) or keep the invariant (failing
  trigger), and log;
- points are computed from final outcomes when reporting (never stored), with the first-violation flag.

### 4.3 Scheduler (`pipeline.py`)

Repeatedly collects ready work (F1 for tasks whose F1 job has not finished; cells' next job; removal paths; rewords; validations),
runs it under the concurrency limit, applies the rules to each finished job, until nothing is pending. Resumable: on
start, jobs left `running` by a stopped run are reset to pending. A task's failing and passing cells run together right
after F1 (DESIGN.md section 6).

## 5. Run directory and CLI

```
runs/<name>/
  config.json          models and effort per job kind, budgets, concurrency, context-guard threshold
  manifest.json        trajectories (id, task_id, label, session log path), P1/P2 per task, benchmark context file
  trajectories/<id>.json
  state.sqlite
  jobs/<job_id>/       input.json, transcript.jsonl, notes.md, output.json
  report.md, report.json
```

```bash
python3 -m invariant_mining prepare --manifest M.json --config C.json --out runs/NAME   # normalize trajectories
python3 -m invariant_mining run runs/NAME [--tasks T ...] [--concurrency 20]           # the pipeline; resumable
python3 -m invariant_mining report runs/NAME                                            # report.md + report.json
python3 -m invariant_mining job runs/NAME --kind f2_seen --trajectories T=ID --inputs '{"facts": ["..."]}'  # one job by hand
python3 -m invariant_mining ping                                                        # one tiny request per model
```

`manifest.json`: `{"trajectories": [{"id", "task_id", "label": "pass" | "fail", "session_log": path to a
session.v2.jsonl or a directory holding exactly one}], "tasks": [{"task_id", "p1", "p2"}], "benchmark_context": optional
path}`. `prepare` checks that P1 and P2 are distinct passing trajectories of their task. Building a manifest from a
benchmark's run directories is benchmark glue (`benchmarks/<name>/`).

## 6. Tests (scripted model, no real model calls)

- `test_im_trajectory_tools.py`: a synthetic session log (not benchmark data): items, locations, order, ignored
  records, a user message mid-run; the tools: overview, paging, caps, search hits and locations, F1's `run` argument.
- `test_im_agent.py`: the agent loop with a scripted model (submit rejected then accepted, nudges, step budget, invalid
  submits, context guard) and the validators (F1, F2, F3, too-narrow; what each job kind is shown).
- `test_im_pipeline.py`: end to end with a scripted policy model: one task with P1, P2, one more passing and two failing
  trajectories, one invariant per rule (support, importance, φ, removal, Opus disagreeing, too narrow on a passing run
  -> reworded and validated, too narrow on a failing run -> two failed attempts and the invariant kept, pinning wrong,
  only before, first violation), F2 reuse across attempts, resume after a stop, idempotent re-run.
- `tests/test_layout.py` keeps passing.

## 7. Cost (estimate, to be measured)

Per task with I invariants and R other trajectories: 1 F1 job; up to I x R F2 jobs and as many F3 jobs; plus, for
every "not followed": on a passing run a re-check (2 Opus jobs) and maybe a too-narrow check, rewords and validations;
on a failing run one too-narrow check (Opus) and, when it says yes, rewords and validations. Failing runs may break
many invariants, so the too-narrow checks on failing runs can be the largest Opus cost. E.g. I = 20, R = 2: ~80 Luna jobs; at ~10 model steps each (a guess) ~800
Luna requests, plus F1 at up to 150 Opus requests. The report records the real numbers.

## 8. Aggregation across tasks (later, not built)

DESIGN.md section 9. A separate step over finished pipeline runs; nothing in sections 1-7 depends on it.

- Module `aggregate.py`; CLI:
  `python3 -m invariant_mining aggregate runs/A [runs/B ...] --context BENCHMARK.txt [--max-calls 10000] --out runs/AGG`.
- Input: the active invariants of the given runs (with their task, points and evidence) and the benchmark context text.
- **Judge jobs**: a single model call each, no tools (the inputs are two short invariants and the benchmark context), a
  fresh call per query. Model: GPT-5.6 Luna high (turn 21), Responses API as in 3.2.
  - `judge_obs`: input = the two observations' facts + the benchmark context; output `{"same": true | false}`.
  - `judge_actions`: input = the two whole invariants (facts and actions) + the benchmark context; output
    `{"actions": "same" | "opposite" | "compatible"}`.
  - Strict schemas, objective answers (DESIGN.md principle 7); an invalid answer is retried once, then logged as an
    error and the pair is treated as not the same (*default*).
- **Guard**: with n active invariants, step 1 needs n(n-1)/2 `judge_obs` calls. If that exceeds `--max-calls` (default
  10,000), the command prints n per task and the count and exits without making any call. After step 1 it counts the
  `judge_actions` calls needed; if step 1 + step 2 exceed the limit, it stops before step 2 and reports. The report
  always gives the counts.
- **Grouping** (*default*): invariants are merged along pairs judged "same" in both steps (connected groups). A group
  in which some pair was not judged the same is flagged in the report.
- **Outputs**: `groups.json` (each group: member invariants, their tasks, each member's support and importance points;
  no combined score, since how points are used is decided later), `conflicts.json` (pairs judged "opposite"),
  `judgements` table in `state.sqlite` (invariant a, invariant b, step, answer, job id), and a section of `report.md`.
