# Your job: was the action's purpose achieved another way?

You get an observation (facts), an action, the action's purpose, the pinned location where the observation was found,
and one trajectory. Another check found that the agent did not take the action, as worded, after the pinned location.

Decide whether the agent achieved the **same purpose** with a different action after the pinned location.

- `achieved_otherwise`: the purpose was achieved by another action after the pinned location; give its location and a
  short quote copied verbatim from it (at most 300 characters).
- `at_pinned`: the purpose was achieved by the pinned item itself (the observation's evidence is the action that
  achieves the purpose); give the pinned location and a short quote copied verbatim from it.
- `not_achieved`: the purpose was not achieved after the pinned location, or only partly.

Answer with exactly one of the three outcomes, objectively and without hedging.

Quotes are checked against the text at the location you give: copy them exactly (you may join excerpts with "…").
