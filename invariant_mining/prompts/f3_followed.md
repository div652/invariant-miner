# Your job: did the action follow the observation?

You get an observation (facts), an action, the pinned location where the observation was found, and one trajectory.

1. Check that the observation holds at the pinned location: all its facts are in the agent's context there (they
   appeared at or before it). If not, the answer is `pinning_wrong`.
2. Did the agent take the action, as worded, anywhere after the pinned location, up to the end of the trajectory? It
   may come much later, after unrelated work. If yes, the answer is `followed`, with the action's location.
3. If not: did the agent take the action before the pinned location? If yes, the answer is `only_before`, with that
   location. Otherwise the answer is `not_followed`.

Judge the action as worded: a different action that achieves something similar does not count. Do not judge whether
the agent acted because of the observation, only whether and where the action happened.

For an empty observation (pinned location `start`), skip step 1: the answer is `followed` or `not_followed`.

Answer with exactly one of the four outcomes, objectively and without hedging. Give a short quote (at most 300
characters) from the action's location, or from where you checked.
