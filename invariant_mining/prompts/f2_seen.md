# Your job: was this observation seen?

You get an observation (a list of facts in abstract terms) and one trajectory. Decide whether there is a point where
**all** the facts held in the agent's context: in the system prompt, the tool descriptions, the task, a tool output, or
the agent's own reasoning (its own conclusions count).

- An abstract fact holds when the trajectory has a concrete instance of it: "a keyword mentioned in the question" holds
  when the task mentions a keyword and the agent's context shows it.
- Context only grows: once a fact has appeared, it stays. The observation holds from the point where its last fact
  first appears.

Answer:

- `seen`: true or false.
- `location`: the **first** location where all facts hold, i.e. where the last of them first appears (null if not seen).
- `evidence`: for each fact by its number, the location where it first appears and a short quote copied verbatim from that location (at most 300
  characters). Empty if not seen.

Facts about the environment or the task (what tools do, where files go, how the workspace is laid out, what the task
asks) are often stated before the first step, in the system prompt (`sys`), the tool descriptions (`tools`) or the user
messages: read those first, and check them for every fact.

Before you submit, go back over the steps before your location and look for an earlier instance of each fact (any
concrete form of it counts, e.g. a search over file names or over file contents are both searches): the location must
be the earliest point where all facts hold, not the clearest one. A later location makes later checks wrong.

You judge only the observation; what the agent did afterwards does not matter here. Answer objectively, true or false,
without hedging: if the evidence is borderline, decide on the most direct reading of the facts.

Quotes are checked against the text at the location you give: copy them exactly (you may join excerpts with "…").
