# Your job: reword an invariant whose action was too narrow

An invariant (observation -> action) was learnt from earlier runs of this task, where it holds. In the trajectory you
get, the agent saw the observation but did not take the action as worded: it achieved the action's purpose with a
different action, at the given location. The action was worded too narrowly: it said how, not what for.

Write a new action at the level of its purpose that covers both what the earlier runs did (the original action) and
what this run did, so that it still holds in the earlier runs. Read the different action in the trajectory first.

- Keep it as granular as possible: say what is achieved, not every way of achieving it, and do not make it so general
  that any run would satisfy it.
- Same style as the original: one short statement in abstract, transferable terms (no names, values or file names),
  plus a one-line purpose.
- Do not change the observation.
