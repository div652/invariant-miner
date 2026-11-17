# Your job: propose invariants from two passing runs

Run A and run B are two runs of the same agent on the same task, and both passed (the grader accepted their result).
Find **all** the observation -> action pairs that occur in **both** runs: places where the agent, having something in
its context, then did something that follows from it. These pairs are candidate invariants of successful behaviour on
this task; later checks test them on other runs, so precision matters as much as coverage.

## Observation

Something that was in the agent's context at some point: from the system prompt, the tool descriptions, the task, tool
outputs, or the agent's own earlier reasoning and conclusions. Write it as a list of short **facts** that must all
hold.

- Use as many facts as the action needs and no more. For each fact give a one-line **reason**: why the action needs
  this fact. If you cannot give one, drop the fact. Usually 1-3 facts; more only when each one is needed.
- Give each fact its **source**: `environment` (system prompt, tool descriptions, file system / workspace layout),
  `task` (what the task asks and how it is structured), `tool_result` (what a tool returned), `reasoning` (a conclusion
  the agent itself reached).
- The list may be **empty**: an empty observation says every passing run takes this action, e.g. "writes a checker
  before answering". Use it for actions both runs take that are not triggered by a particular observation.
- Something the agent knows is a fact ("4 candidates found, 2 not yet verified"). Something it chooses, intends or does
  is an action ("decides to verify each candidate"). Never put a choice into an observation.

## Action

What the agent did after the observation: a tool call, or a decision or step stated in its reasoning. One short
statement. Add its **purpose**: one line saying what the action achieves.

## Wording: abstract, transferable, granular

Write facts and actions so they could apply to other tasks, but keep the role each task-specific thing played, as
granular as the runs allow:

- "a keyword" is abstract; "a keyword mentioned in the question" is better; "the keyword with most hits" when the
  reasoning says the agent chose it for having the most hits;
- "a task-specific calculation", not "calculating year-end salaries";
- no names, values, file names or numbers from the task.

Be succinct and systematic: one short statement per fact and per action, and the same term for the same role in every
pair. List the role terms you used, one line each, in `roles`.

## Chains

When one pair's action produces what a later pair's observation needs, write the later observation self-contained and
list the earlier pair's id in `follows`. Example:

- i1: [keyword search results over the documents] -> identifies the keyword with most hits
- i2: [keyword search results, with the keyword with most hits identified] -> opens the files that match that keyword
  (follows: i1)

## Common to both runs, with evidence

Include a pair only if it occurs in both runs at the abstract level (concrete values may differ). Each pair must be
backed in each run by a tool call, a tool output or a reasoning sentence; reasoning summaries can omit or rationalize
decisions, so check the calls and outputs too. Give the evidence: the location of the observation (where its last fact
appears; `start` for an empty observation) and of the action, in run A and in run B. The observation comes before the
action.

Cover the whole runs, from reading the task to delivering the answer: how the agent explored, searched, read, verified,
computed, decided and wrote its deliverable. Read **every step of both runs** with `read_steps` (and open long outputs
with `read_output` where they matter) before deciding; `submit` is refused until `read_steps` has shown every step of
both runs. Note candidate pairs as you go.
