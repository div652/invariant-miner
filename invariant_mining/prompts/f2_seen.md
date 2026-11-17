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
- `evidence`: for each fact by its number, the location where it first appears and a short quote (at most 300
  characters). Empty if not seen.

You judge only the observation; what the agent did afterwards does not matter here. Answer objectively, true or false,
without hedging: if the evidence is borderline, decide on the most direct reading of the facts.
