# Same-task invariant mining: flowcharts

How the algorithm in [DESIGN.md](DESIGN.md) runs, from the inputs to the table of points in the report. Built as
`invariant_mining/` ([TECHNICAL.md](TECHNICAL.md)). GitHub renders the diagrams below.

Legend: **Opus** = Claude Opus 5.5, effort high; **Luna** = GPT-5.6 Luna, effort high; **pass / fail** = the run's
all-pass verdict from the grader (the only thing taken from grading); **S** = support point, **I** = importance point.

## 1. The whole pipeline

```mermaid
flowchart TD
    IN["Inputs: per task, its runs (DSH session logs) with pass/fail labels;<br/>P1, P2 = two passing runs"] --> PREP["prepare: each session log becomes a normalized trajectory<br/>(items in the order the agent saw them; locations sys, tools, uN, sN.r, sN.cK, sN.oK)"]
    PREP --> F1["F1 propose (Opus agent), one job per task:<br/>reads every step of P1 and P2, submits all observation -> action pairs common to both"]
    F1 --> EVC["F1 evidence check (code, logged only):<br/>locations exist, observation before action in P1 and P2"]
    EVC --> CELLS["Cells: every invariant x every run of the task except P1, P2<br/>(passing runs first: an invariant's failing-run cells wait for its passing-run cells and triggers)"]
    CELLS --> CELL["Per-cell checks (section 2)"]
    CELL --> PTS["Cell outcome: S +1 / I +1 / no change"]
    CELL --> TRIG["Trigger for the invariant: remove or reword (section 3)"]
    TRIG --> Q["Per-invariant queue, one trigger at a time"]
    Q -->|remove| RM["Invariant removed;<br/>its pending cells cancelled, waiting triggers dropped"]
    Q -->|reword| RW["Rewording + validation (section 3)"]
    RW -->|valid| NEWINV["Old invariant retired; new invariant (new id)"]
    NEWINV -->|"loop: new cells on every run except P1, P2"| CELLS
    RW -->|"two failed attempts"| KEEPRM["Passing trigger: removed<br/>Failing trigger: kept, that run counts 0"]
    PTS --> DONE{"Anything pending?<br/>(cells, triggers, validations)"}
    RM --> DONE
    KEEPRM --> DONE
    DONE -->|yes| CELL
    DONE -->|no| REP["Report (section 5): per invariant S, I, first violations, outcome per run;<br/>removed, reworded, kept; events; cost"]
    ADD["add-runs: new runs for existing tasks<br/>(no new F1)"] -.->|"cells for every active invariant x new run"| CELLS
    RETRY["retry-errors: cells that ended in a job error"] -.->|"back to pending at their stage"| CELL
```

## 2. One cell: one invariant on one run

Since turn 97: "at pinned" outcomes (the action, or the purpose-achieving action, is the pinned item itself), and the
Opus re-check for a failing run's "not followed" as well.

```mermaid
flowchart TD
    START["Cell: invariant (observation facts, action) x run R"] --> PHI{"Observation empty (φ)?"}
    PHI -->|yes| F3
    PHI -->|no| F2["F2 seen? (Luna agent; sees the facts only):<br/>yes + FIRST location where all facts hold, evidence per fact / no"]
    F2 -->|no| NS["not seen: no change"]
    F2 -->|yes| F3["F3 followed? (Luna agent; facts + action + F2's location):<br/>1. observation at that location? 2. is that item itself the action?<br/>3. action anywhere after it? 4. else before it?"]
    F3 -->|pinning wrong| PW["no change (counted)"]
    F3 -->|"at pinned"| AP["no change (counted: the observation's only evidence is the action)"]
    F3 -->|only before| OB["no change (counted: the observation may not be the real trigger)"]
    F3 -->|followed| FOL{"R passing?"}
    FOL -->|yes| SP["S +1"]
    FOL -->|no| NC1["no change"]
    F3 -->|"not followed (passing or failing run)"| RF2["Opus re-check: F2 again"]
    RF2 -->|not seen| D1["Opus's verdict counts: not seen, no change<br/>(Luna/Opus disagreement logged)"]
    RF2 -->|seen| RF3["Opus re-check: F3 again, at Opus's location"]
    RF3 -->|"followed / only before / pinning wrong / at pinned"| D2["Opus's verdict counts (S +1 if followed on a passing run)<br/>(disagreement logged)"]
    RF3 -->|not followed| TN["Too-narrow check (Opus; sees the purpose):<br/>same purpose achieved after the observation?"]
    TN -->|"by the pinned item itself (at pinned)"| AP2["no change, no rewording (counted)"]
    TN -->|not achieved| LAB{"R passing?"}
    LAB -->|yes| REM["Trigger: remove the invariant"]
    LAB -->|no| IMP["I +1<br/>(first violation if its observation location is the earliest among this run's broken invariants)"]
    TN -->|"achieved otherwise"| RW{"R passing?"}
    RW -->|yes| RWP["Trigger: reword (from a passing run)"]
    RW -->|no| RWF["No point; trigger: reword (from a failing run)"]
```

## 3. Rewording and its validation (the loop back)

```mermaid
flowchart TD
    T["Reword trigger for invariant X<br/>(waits until X's earlier triggers are done; dropped if X is no longer active)"] --> A1["Attempt 1: F1 reword (Opus agent)<br/>input: X, the triggering run, the location of its alternative action;<br/>told X was learnt on earlier runs where it holds"]
    A1 --> NEWA["New action + purpose (observation unchanged)"]
    NEWA --> V["Validation with the standard F2, F3 (Luna):<br/>on P1, P2, and the triggering run if it passed;<br/>F2 verdicts reused from an earlier attempt"]
    V -->|"all seen + followed"| OK["X retired; new invariant X' (id rX) added with 0 points"]
    OK --> CELLS2["Cells for X' on every run except P1, P2:<br/>passing trigger: its validation verdict becomes that cell (S +1)<br/>everything else goes through section 2 again"]
    CELLS2 -.->|"loop: X' can itself be removed or reworded (rX.2, ...)"| T
    V -->|"any check fails"| ATT{"Attempt?"}
    ATT -->|1| A2["Attempt 2: F1 reword again,<br/>also given attempt 1's action and the failed check"]
    A2 --> NEWA
    ATT -->|2| FAIL{"Trigger from a passing run?"}
    FAIL -->|yes| R2["X removed (logged: rewording failed)"]
    FAIL -->|no| K2["X kept; the triggering failing run counts 0 for importance (logged)"]
```

## 4. One job: a fresh agent

Every F1, F2, F3, too-narrow and reword job is its own agent with a fresh context; jobs of a kind share a system prompt.

```mermaid
flowchart TD
    J["Job: system prompt (preamble + kind) + inputs + sizes of its trajectories"] --> M["Model step (Opus: Anthropic SDK; Luna: Responses API; via CAO)"]
    M -->|no tool call| NUDGE["Nudge: use the tools, then submit"] --> M
    M -->|read-only tools| TOOLS["overview, read_context, read_steps, read_output, search, note, read_notes"]
    TOOLS --> GUARD{"Context over 60% of the window?"}
    GUARD -->|yes| EL["Elide the oldest tool results (notes kept)"] --> M
    GUARD -->|no| M
    M -->|submit| FR{"F1: every step of both runs read?"}
    FR -->|no| REF["Refused, unread steps listed (not counted as invalid)"] --> M
    FR -->|"yes / not F1"| VAL{"Valid? schema and allowed values only (no hedging),<br/>locations exist and are in order, quotes found at their location"}
    VAL -->|no| INV["Rejected with the reason; 3 invalid submits end the job"] --> M
    VAL -->|yes| OUT["output.json -> the rules (sections 2 and 3)"]
    M -->|"step budget, wall time, API failure, refusal"| ERR["Job failed"]
    ERR --> RT{"Retried already?"}
    RT -->|no| J
    RT -->|yes| JE["Job error: cell ends with no change (retry-errors can re-run it)"]
```

## 5. From cells to the table of numbers

```mermaid
flowchart LR
    C["Final cell outcomes<br/>(active invariants only)"] --> S["S = passing runs (not P1/P2) with seen + followed"]
    C --> I["I = failing runs with seen + not followed<br/>(after the too-narrow check said no)"]
    C --> FV["First violation: per failing run, the broken invariant<br/>whose observation location comes first (★)"]
    C --> N["Neutral, counted in events: not seen, only before, pinning wrong, at pinned,<br/>same purpose another way, job error"]
    S --> TBL["report.md per task: proposed (status, S, I, outcome per run), rewordings,<br/>removed with the reason, kept after failed rewordings, events, role terms; cost"]
    I --> TBL
    FV --> TBL
    N --> TBL
```

## Scheduling

All work goes through one SQLite table of cells plus the trigger queue and the validations; a row without a final
verdict is pending work. Up to 20 jobs run at a time (worker threads); only the main thread changes the state. Each
round it starts, in order: F1 for tasks not yet proposed, the front trigger of each invariant (a removal is applied at
once, a rewording or validation becomes a job), then pending cells, passing runs first: an invariant's failing-run
cells become ready only when all its passing-run cells are final and it has no open trigger. A stopped run resumes where it was (`run` again).
Points are computed when the report is written, never stored, so changing a scoring rule needs no new model calls.
