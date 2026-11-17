# Same-task invariant mining: design

What the algorithm does and the rules it follows, as agreed in the design conversation of 2026-11-16/17
([QNA.md](QNA.md): the verbatim log, turns 1-26; "turn N" below points into it). How it is built:
[TECHNICAL.md](TECHNICAL.md). Nothing is built yet.

Every item below was decided in the conversation; what is still open is in section 12.

## 1. Goal

From an agent's recorded runs, learn **invariants** of successful behaviour: observation -> action pairs that two
passing runs of the same task have in common, that further passing runs confirm, and that failing runs break. Learn
them per task first; combine them across tasks later (section 9). An invariant that failing runs break is an
important one (turn 7).

## 2. Terms

| Term | Meaning |
|---|---|
| Trajectory | One run of the agent on one task as the harness recorded it (DSH session log): the system prompt, the tool descriptions, the task and other user messages, and per step the reasoning summary, any text, the tool calls and the tool outputs. Each trajectory has a label, **pass** or **fail**, from the benchmark's grader. |
| P1, P2 | The two passing trajectories of one task that F1 proposes invariants from (the "source runs"). Which runs these are is chosen by the caller (section 3). |
| Observation | Something that was in the agent's context at some point: anything from the system prompt, tool descriptions, task, tool outputs, or the agent's own earlier reasoning and conclusions (turn 5). Written as a list of **facts** that must all hold. Usually 1-3 facts; more are allowed (turn 9). The list can be **empty** (φ): the invariant then says the action is always taken (turn 9). |
| Fact | One short statement in abstract, transferable terms that keep the role of the task-specific thing: "a keyword mentioned in the question", "the keyword with most hits", "a task-specific calculation", not "HSR" or "calculating year-end salaries" (turns 5, 9). No names, no values. |
| Source label | Where a fact comes from: `environment` (tool descriptions, system prompt, file system), `task`, `tool_result`, `reasoning` (the agent's own conclusion); an empty observation is φ (turns 10, 11). One label per fact, since one observation can combine sources (e.g. a task requirement and a tool result) (turn 15). |
| Reason | One line per fact: why the action needs this fact. It is the causal link between observation and action (turns 8, 9; H2). Facts without a reason are dropped. Used by F1 and by us, never shown to F2 or F3. |
| Action | What the agent does after the observation: a tool call, or a decision or step taken from its reasoning (turn 3). One short statement in the same abstract, granular terms. Something the agent knows is an observation; something it chooses or intends is an action (turn 6). |
| Purpose | One line per action: what the action achieves (turn 10). For our understanding; never shown to F2 or F3 (turn 13). Used by the too-narrow check and the reword step (section 4). |
| Invariant | (observation, action) with its reasons, source labels and purpose, an id, the task, and P1, P2. |
| Chain | An observation can describe the outcome of an earlier invariant's action, e.g. "keyword search results with the most-hit keyword identified" after "keyword search results -> identifies the keyword with most hits" (turns 5, 6). The observation is written self-contained, as in the user's own example (turn 5); the link is kept as information only (Claude's turn-6 idea of writing the link into the text was dropped because F2 checks each observation alone; to confirm, section 12). |
| Location | A position in a trajectory: the system prompt, the tool descriptions, a user message, or a step's reasoning, text, tool call or tool output (format: TECHNICAL.md section 2.3). Locations are ordered as the agent saw them. |
| Cell | One invariant x one trajectory, other than that invariant's P1 and P2. It holds the verdicts of the checks run on it and their final outcome. |
| Support point | +1 for an invariant on a passing trajectory where its observation was seen and its action followed (turns 9, 12). |
| Importance point | +1 for an invariant on a failing trajectory where its observation was seen and its action did not follow (turns 9, 12). |

## 3. Principles

1. **Atomic jobs** (turn 3). Every LLM job decides one thing about one input: F1 one pair of runs; F2 one observation in
   one trajectory; F3 one invariant in one trajectory. A loop over items calls the model inside the loop, with a fresh
   context for each item. Jobs of one kind share a system prompt.
2. **Jobs are agents** (turn 5). Trajectories are too long to put in one prompt (agent context at the last step: median
   ~209K tokens, max ~414K, on Harvey FK-250 Luna high), so every job that reads trajectories (F1, its reword mode,
   F2, F3, the too-narrow check) is an agent that reads them in parts through read-only tools, can keep notes, and
   submits its answer as a structured output file. It has no other abilities (no shell, no coding, no files, no web).
   It is told the sizes of its trajectories. The later semantic judge reads no trajectory, so it is a single model call
   (turn 20).
3. **LLMs only inside the functions** (turns 11, 15): F1 (with its reword mode), F2, F3, the too-narrow check, and later the
   semantic judge. Everything else (scheduling, outcomes, points, removal, retiring, logs, report) is programmatic.
4. **Checkers see only what they check** (turns 3, 9, 13): F2 sees the observation's facts only (no action, no reasons,
   no purpose, no source labels); F3 sees the facts, the action and F2's location (no reasons, no purpose); of the checks, only
   the too-narrow check (4.4) also sees the purpose. F1's reword mode sees the whole invariant (turn 13).
5. **No link judgement in checks** (turn 11; H2). F2 and F3 answer yes/no with locations. They never judge whether the
   agent acted because of the observation; F1's reasons carry the causal link.
6. **Data-agnostic** (turn 7). The input is a set of trajectories with task ids and pass/fail labels, the choice of P1
   and P2 per task, and optional text describing the benchmark. Which benchmark, tasks and runs are used is decided
   later (flip tasks are the intended data for importance: turn 9).
7. **Objective answers** (turn 15). F2, F3 and the too-narrow check answer with exactly one of the choices they are
   given (yes/no, or the listed outcomes) plus locations. They do not equivocate or play it safe: no "unclear", no
   "partly", no confidence; they decide on the most direct reading of the evidence. The output schemas allow nothing
   else.

## 4. The functions

| Function | Model | One job | Output |
|---|---|---|---|
| F1 propose | Claude Opus 5.5 (turn 7) | P1 and P2 of one task | invariants common to both runs |
| F1 reword | Claude Opus 5.5 (turns 14, 15) | one too-narrow invariant + the run that triggered it | a new action (and purpose) |
| F2 seen? | GPT-5.6 Luna high (turn 11) | one observation x one trajectory | seen yes/no + the first location where it holds |
| F3 followed? | GPT-5.6 Luna high (turn 11) | one invariant x one trajectory + F2's location | pinning wrong / followed + location / not followed / only before + location |
| Re-check | Claude Opus 5.5 (turn 9) | a removal candidate | F2 and F3 again, same prompts |
| Too-narrow check | Claude Opus 5.5 | a cell whose final F3 outcome is not followed, on a passing or a failing run (turn 15) | an action with the same purpose after F2's location? yes/no + location |
| Semantic judge (later) | GPT-5.6 Luna high (turn 21) | two invariants (a single call, no tools) | step 1: observations the same? yes/no; step 2: actions same / opposite / compatible (section 9) |

Effort: **high** for every Opus 5.5 job (turn 17).

### 4.1 F1 propose

Input: P1 and P2 in full (system prompt, tool descriptions, task, all steps), read through the tools (principle 2).
Output: **all** the observation-action pairs common to **both** runs, succinct and systematic (turn 3), following
these rules:
- observation and action as defined in section 2: abstract, transferable, as granular as possible, keeping the role of
  task-specific things (turn 5);
- short facts, each with its reason and source label; as many facts as the action needs, no more: a fact without a
  reason is dropped (turns 8, 9);
- the observation may be empty (φ, action), e.g. "every passing run writes a checker first" (turn 9); it may be about
  the environment (tool descriptions, file system) or the task's structure, always in abstract terms (turn 9);
- the observation may be the agent's own conclusion (source `reasoning`); a choice or intention is always an action
  (turn 6);
- every pair must be backed in each run by a tool call, a tool output or a reasoning sentence, since reasoning
  summaries can omit or rationalize decisions (turn 6);
- chains are written as separate, self-contained invariants (turns 5, 6);
- the action has a one-line purpose (turn 10);
- the list of role terms used ("keyword from the question", "most-hit keyword", ...) with one line each, so the terms
  stay consistent across invariants (turn 6);
- each invariant carries its evidence (turns 14-17): the location of the observation and of the
  action in P1 and in P2. No LLM checks it in the loop (turn 15 asked): it is for debugging and the report, and the code
  checks it at no cost (the locations exist; the observation comes before the action in both runs), only logging a
  failure (turn 16).

### 4.2 F2 seen?

Input: the observation's facts and one trajectory. Question: was this observation visible to the agent at any point,
i.e. is there a point where all its facts hold, an abstract fact holding when the trajectory has a concrete instance
of it (turn 3)? Output: `seen` yes/no; the **first** location where all facts hold, which is where the last of them
appears (C3); per fact, the location and a short quote as evidence (turn 9).

For φ (no facts) F2 is not run: the observation holds from the start of the trajectory.

As a function (turn 3): F2 takes the list of proposed invariants and one trajectory, ignores the actions, and returns
one bool (with its location) per observation; each observation is its own job.

### 4.3 F3 followed?

Input: the facts, the action, F2's location, one trajectory. Steps (turns 9, 11):
1. Check that the observation holds at F2's location. If not: outcome **pinning wrong**, stop. (How often this happens
   is reported: turn 7.)
2. Did the action, as worded, happen anywhere after that location (turns 7, 9: "anytime later")? If yes: outcome
   **followed**, with the action's location.
3. If not: did it happen before the location? If yes: outcome **only before**, with the location (turn 10, H4);
   otherwise **not followed**.

The action is judged as worded: a different action with the same effect is not "followed" (that case is the
too-narrow check's job). For φ, step 1 is skipped and "only before" cannot occur.

As a function (turn 3): F3 takes the proposed invariants, F2's bools and locations, and one trajectory; invariants
whose observation was not seen are dropped programmatically, and each remaining invariant is its own job.

### 4.4 Re-check and too-narrow check (an F3 outcome of "not followed")

**Too-narrow check** (turns 10, 13, 15; H1): a separate job (Opus 5.5), not part of F3, and the only check that sees the
purpose (F2 and F3 never do: turn 13). Input: the facts, the action, its purpose, F2's location, one trajectory.
Question: did an action that achieves the same purpose happen after F2's pinned observation? Output: yes/no + location.

On a **passing** trajectory (a removal candidate):
1. **Re-check** (turn 9): F2 and F3 run again with Opus 5.5 (F3 uses Opus's F2 location). Opus's verdicts replace
   Luna's for this cell, whatever they are (turn 13, answer 4); when they differ from Luna's, the disagreement is
   logged (it measures Luna's error rate: C1).
2. If Opus also says not followed: the too-narrow check, after Opus's F2 location. Any other Opus outcome is final,
   with its effect in section 5.
3. Yes -> **reword** (4.5). No -> the invariant is **removed**.

On a **failing** trajectory (turns 15, 17): no re-check (turn 13, answer 5); the too-narrow check runs on Luna's
verdict, after Luna's F2 location. No -> importance point. Yes -> no importance point for this cell, and **reword**
(4.5), as for a passing run (turn 17; the alternative is H6).

### 4.5 F1 reword (H1)

Input (turn 13, answer 1): the invariant, the trajectory that triggered the rewording and the location of its
alternative action (from the too-narrow check), and the statement that this invariant was learnt from earlier runs of
the same task, where it holds. P1 and P2 are not given. Output: a new action and purpose; the observation is unchanged.

Validation, with the standard F2 and F3 (Luna high): (observation, new action) must give seen and followed on P1 and
P2, and, when the trigger is a passing run, on the triggering run too (turns 11, 13 answer 2, 17).
- Valid, at either attempt: the old invariant is **retired**, the new one is added (new id, link to the old one) with
  0 points, and all its cells are scheduled: it is scored again on every other passing and failing run (turns 11, 17).
  For a passing trigger, the validation verdicts on the triggering run are kept as that cell's verdicts (Claude's
  choice, turn 14, not discussed: they are the same F2/F3 jobs the cell would run; to confirm, section 12); a failing
  trigger is scored like any other run (turn 18).
- Not valid: a second rewording attempt, given the first attempt and which check failed (turns 13, 17). If it also
  fails:
  - passing trigger: the invariant is removed and the failure logged (turn 13);
  - failing trigger: the invariant stays as it was, the triggering cell counts 0 for importance, and the failure is
    logged (turn 17).

## 5. Outcomes and points

Final outcome of each cell -> effect (turns 9, 12, 13, 15). "Not followed" is the outcome after the steps of 4.4.

| Trajectory | followed | not followed | not followed, same purpose achieved otherwise | only before | not seen / pinning wrong / job error |
|---|---|---|---|---|---|
| Passing | support +1 | invariant removed | reword (4.5); if both attempts fail, removed | no change | no change |
| Failing | no change | importance +1 | no point; reword (4.5); if both attempts fail, the invariant stays | no change | no change |

- Cells exist only for trajectories other than the invariant's P1 and P2.
- Failing cells use Luna's F2/F3 verdicts, with no re-check (turn 13, answer 5), then the too-narrow check on a "not
  followed" (turn 15).
- An importance point is flagged **first violation** when its observation location is the earliest among that failing
  run's violated invariants (H3).
- (φ, action) invariants are always seen: they get support points when passing runs take the action and importance
  points when failing runs do not (turn 13). Environment invariants behave the same way within one task (turn 11).
- No penalty for long observations: they are rarely seen, so their support stays low (turn 9). An invariant with 0
  support points was never tested, not confirmed (turn 10). How the points are used downstream is decided later
  (turn 11).
- Points are reported for active invariants; the cells of removed and retired invariants stay in the log.

## 6. Pipeline for one task

Input: the task's trajectories with labels, and P1, P2.
1. **Propose**: F1 on P1, P2. All invariants are active.
2. **Check**: for every active invariant x every other trajectory, passing and failing: F2, then F3 if seen. Failing
   runs are checked right after step 1, together with the passing runs (turn 13). This does not change any result:
   removal depends only on passing cells, and failing cells never cause removal; the cost is the failing checks of
   invariants that are later removed (their verdicts stay in the log).
3. **Not followed** (4.4): on a passing cell the re-check, then the too-narrow check (remove or reword), one invariant
   at a time: when an invariant is removed or retired, its remaining pending cells are cancelled. On a failing cell the
   too-narrow check (importance point, or reword).
4. **Reword** (4.5) -> a new invariant whose cells go back to step 2.
5. Repeat until no cell is pending, then write the **report** (section 7).

Everything is driven by one table: one row per cell, and every row without a final outcome is pending work; adding an
invariant schedules its cells (turns 8, 9, 11). Changing an aggregation rule (points, thresholds, first-violation
weighting) needs no new LLM calls; changing an invariant's text makes a new invariant, which needs its checks again
(turn 9, answered turn 10).

## 7. Logs and the report (turn 13: "report logs at the end of the process")

Per task and overall:
- active invariants with support points, importance points, first violations;
- removed invariants, with the cell that removed it and whether Opus agreed with Luna;
- reworded invariants: old -> new action, attempts, validation verdicts;
- reword failures (after two attempts: removed for a passing trigger, kept for a failing trigger);
- failing-run cells where the purpose was achieved otherwise (no importance point), and what their rewording gave;
- F1 evidence check failures (4.1);
- Luna/Opus disagreements in re-checks;
- pinning-wrong counts (per invariant and per trajectory);
- only-before counts per invariant (a frequent one suggests the observation is not the real trigger: H4);
- job errors, and the cost: jobs, model requests, tokens, time.

## 8. Highlighted notes

### ★ H1. Action too narrow: a different action with the same purpose (turns 8, 10, 11, 13, 15, 17)

F1 sees both source runs do the same thing, e.g. "opens each candidate file", and writes that as the action. A third
passing run instead greps the candidate files for the key term and reads only the matching passages: same purpose
(every candidate checked), different mechanism. The action as worded did not happen, so the invariant would be removed
although the run supports it. Cause: the action says how, not what for. User (turn 11): "a great insight". Handled by
the too-narrow check (4.4) and the reword step with its validation (4.5). The check runs on failing runs too, so a
failing run that achieved the purpose another way earns no importance point (turn 15) and triggers a rewording (turn 17;
the alternative is H6). User (turn 15): the hope is that F1 is good enough for rewordings to be rarely needed.

### ★ H2. The causal link comes from F1, so F3 only checks "after" (turn 9)

F1's one-line reason per fact says why the action follows from the observation. With that link in place, F3 only checks
that the action happened after the observation; F2 and F3 do not judge links. This holds as long as F1 works properly.

### ★ H3. The first broken invariant in a failing run says the most (turns 8, 9)

A failing run often goes off track once and then breaks many invariants as a consequence. The first violation is the
most informative, hence the first-violation flag (section 5). Tasks whose runs both pass and fail (flip tasks) are the
cleanest data for this.

### ★ H4. Nuance: the action happened before the observation (turns 8-11)

E.g. the agent opened the files before the search that should lead to opening them. Under "after the observation" this
reads as "not followed" and would remove a good invariant, even when F1's reasons are right. Handled without manual
checks (turn 10, agreed turn 11): F3 detects it (outcome **only before**), it counts as no change, and a frequent
occurrence for one invariant is reported as a sign that its observation is not the real trigger (re-propose it with an
earlier trigger, or as (φ, action): later). An observation that appears early by chance only lengthens the "after"
window.

### ★ H5. Process right, content wrong (turns 8-11)

A failing run can follow the same process as the passing runs and still fail on content: a misread document, a final
answer missing something the grader checks. Usually the passing runs did something the failing run did not (e.g. a
cross-check), which is a process invariant (user, turn 9); what remains is one judgement going wrong inside the same
process, the "model reasoning error" case (Claude, turn 10). User (turn 11): this might happen. Consequence: a failing
run that breaks no invariant does not always mean an invariant is missing.

### ★ H6. Should failing runs reshape invariants? (Claude, turn 16; highlighted at the user's request, turn 17)

When a failing run achieved an action's purpose another way, Claude suggested only cancelling its importance point,
without rewording the invariant: invariants are built from passing behaviour, and the failing run's other way may be
part of why it failed. User (turn 17): an important point, to be highlighted; for now failing runs do trigger
rewordings (4.4, 4.5). Worth revisiting with data: how often rewordings come from failing runs, and whether invariants
reworded from failing runs score worse.

## 9. Later (not built; to be discussed, turn 13)

- **Targeted re-proposal** (turns 8, 9): for a failing run that breaks no invariant, find the first point where it did
  something the passing runs did not do in a similar situation, and run F1 again on P1, P2, pointed at that kind of
  situation, to propose finer invariants there only. The grader's per-criterion verdicts, where a benchmark has them,
  help find that point (optional text input). H5 applies.
- **Re-proposal for "only before" invariants** (H4; turn 10): an invariant whose action often comes before its
  observation is re-proposed with an earlier trigger, or as (φ, action).
- **Union across tasks with a semantic judge** (turns 13, 19; the method to use). Union = the union of the tasks'
  active invariants, merging the ones that are the same:
  1. For **every pair** of active invariants, a judge sees only the two **observations** and the benchmark context:
     the same? (yes/no).
  2. For each pair whose observations were judged the same, a judge sees both **whole invariants**: are the actions
     the same, opposite, or different but compatible? (exactly one of the three). Same -> merged; opposite -> a
     **conflict**, logged; compatible -> both kept.
  3. Pairs with different observations (even with the same action) are not sent to step 2; such invariants can be
     scored on the other tasks' trajectories (F2/F3) for support and importance there.

  Every query is a fresh call (turn 19: "fresh call per query") with the benchmark context, and the judge answers
  objectively (principle 7). Its inputs are short, so it is a single model call, not an agent.

  **Shortcoming: the comparisons are quadratic** (turns 14, 18, 19). Step 1 alone takes n(n-1)/2 calls for n
  invariants: 100 -> 4,950; 141 -> 9,870; 200 -> 19,900; 700 -> 244,650. The user expects fewer than 20 invariants per
  task after the in-task checks, and will pick small sets of tasks (turn 19); at 20 per task, 10,000 calls are reached
  at about 7 tasks.

  **Call-count guard** (turn 19): before launching the aggregation, count the calls; if there are more than 10,000, do
  not launch it (the user then decides whether to aggregate with LLMs at all). Step 1's count is known exactly, step
  2's only after step 1, so the check is repeated before step 2 for both steps together.
- **Conflict refinement** (turns 8, 9): two invariants with the same observation and opposite actions lack a fact that
  separates the cases; adding it to both retires the old invariant(s) and adds new ones, scored again on all runs (C4).
- **Cross-task support**: how many tasks an invariant applies to (F2) and holds in (F3) (turn 10).
- How the points are used downstream (turn 11).

## 10. Cautions

- **C1. Check errors** (turns 8, 9): a model may say "followed" when it was not, or the reverse. Assumed rare for now;
  the Opus re-check covers removal, and Luna/Opus disagreements measure Luna's error rate.
- **C2. Process right, content wrong**: H5.
- **C3. F2 must give the first location** (turns 10, 11): with a later one, an action between the first occurrence and
  that one would count as not followed.
- **C4. New invariants start at 0** (turns 9, 11): reworded or refined invariants are new; they are checked again on
  every other run.
- **C5. Importance inflated by too-narrow actions: resolved** (raised turn 14, resolved turn 15): the too-narrow check
  also runs on failing cells, so a failing run that achieved the purpose another way earns no importance point.

## 11. When does an action count as "followed"?

Raised in turn 6. User (turn 7): at any time after the observation, before the end of the trajectory; ideally when the
agent builds on the observation, but that is hard to infer. Claude (turn 8): agreed; weakness: an action much later for
an unrelated reason. User (turn 9): no link judgement in F2/F3, F1's reasons give the causal link (H2). **Decided:
anytime after F2's location** (4.3), with "only before" as a separate outcome (H4).

## 12. Open questions

No open design questions since turn 21; the later work of section 9 is still to be discussed. Two choices made while
writing the documents were never discussed and need the user's confirmation (found in the consistency check, turn 26):
1. Reusing the validation verdicts as the triggering passing run's cell (4.5).
2. Chains written self-contained, with the link as information only (section 2).
