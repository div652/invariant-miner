# 2sameInvariantAlgo: task prompt and design Q&A

Record of the task as the user gave it (2026-11-16) and the design questions asked before building, with the user's
answers verbatim. New rounds of questions are appended at the end.

## The task (user's prompt, verbatim)

> Okay, here's what I want to do. I want to create an algorithm, which you can write anywhere, maybe a Python script or anything you like. Embedded in this algorithm will be calls to LLMs. Now, I want to implement these functions. One function here will be that the input to this function will be trajectories of an agentic LLM. These trajectories will be the output of the DSH bench harness. Essentially, the input of this function will be two trajectories generated from the DASH pen harness based on its runs.
> This function is called the propose invariance function. What the propose invariance function does is that it takes these two trajectories. The behavior of these two trajectories that will be passed into this function is that both of these trajectories are passing trajectories on the same task.
> The output of this function is going to be a list of pairs. These are pairs of observations and actions. The observation and action are going to be of this format:
> - Observation: anything that the LLM, the agent that is solving this task, has seen in its context till now.
> - Action: an action that it takes.
> Of course, the action can be a tool call that it does, but it can also be mined from its reasoning traces, because the input to this is the agentic trace, and the agentic trace contains reasoning summaries also. The action can be anything that the agent has done. It can be a decision it made, or it can be a tool call it did, or it can be general enough. An observation is probably anything, like any fact or any statement, per any observation it has made in its context till now.Now, the role of the function is to take these two trajectories. Since we are giving the trajectories, it will also contain the input prompt that was given to the agent and the question the agent was asked.
>
> The goal of this function is to output all the common observation-action pairs that it saw in both the trajectories. That's all this function has to do. You can use frontier LLM calls to essentially write down this function. The output of the LLM has to be this list of observation-action pairs. Both can be natural language, but try to keep them very succinct. Don't let them be very verbose. Keep them systematic in a way.
>
> This is the first function you want to implement. The other function you want to implement is given this list of observation-action pairs. I will call this list "proposed invariants." Given a list of proposed invariants and an agentic trajectory (again, this is a full trajectory including the system prompt, the task, and what the agent did), this function first of all has to not see the actions at all. This function just works on the observations. The first thing this function needs to do is just discard the actions that are present and only work on the observations.
>
> For each observation, it has to just mark whether the observation was visible to the agent in this trajectory at any point or not. That's all it has to do. That is what its output has to be. Its output is going to be a list of bools. For each index, or for each observation, it would say whether that observation was observed in the agent's trajectory or not.
>
> Now I want you to write a third function. This function takes a list of observations and these boolean values (true/false), and it will take the list of proposed invariants. Simply discard all the observations that were not observed, so we only work with observations that were true.
>
> This has to be a separate LLM that has to do it one task at a time. For each observation that is true, this LLM call just has to tell whether, given this trajectory and this one observation, the action was taken once this observation was present in the trajectory or not. Basically, did the action follow the observation? Yes, that's all it has to do.
>
> Now, for all three functions that I have described till now, in each, the LLM agent that you are using has to do a very atomic task. What I mean to say is that, for any kind of `for` loop that this task requires, inside the `for` loop, the LLM has to be called.
>
> For example, in function 1, we don't need a `for` loop, right? Function 1 is fine.
>
> Coming to function 2, function 2 takes a list of observation-action pairs, and it only has to work with observations, right? Essentially, it gets a list of observations, and for each observation, it has to tell whether it was observed in the trace or not, right? For one trace and for one observation, one LLM call will be made. You can write the right prompt for the LLM call, but after that, discard this LLM call. For the next observation and the next trace, you do another LLM call. Maybe the trace is the same but the observation is different. Maybe the observation is the same but the trace is different, but for each new pair, you do a new call.
>
> Similarly, for the third function, given an observation that was observed, you just have
>
> You just have to do one agent, one LLM call per observation and action you need to check. Given that an observation occurred because it was true in the list, this part can be programmatic. Then, just the check that did the action, follow the observation, that part: you have to do an LLM call and get the boolean answer, yes or no.
>
> For the next query, which is another observation, a different trace, or the same observation, different trace, whatever, do another LLM call. They can use the same system prompt, but I think you get my point, right? You can share the system prompts, but it has to be a new trace.
>
> I wanted to write a kind of script like this. Let me know if you have any doubts or questions, and then I can clarify those to you. Feel free to ask me as many questions as you want, or any clarification you need, before building this thing up.

## Round 1 (2026-11-16)

Context given with the questions: a DSH session log (`session.v2.jsonl`) holds the system prompt, the task, reasoning
summaries, tool calls and tool outputs. A Harvey FK trajectory has a median of ~225K tokens of agent-visible text (max
~430K), ~95% of it tool outputs; reasoning summaries are ~7.6K chars and tool-call arguments ~26K chars per trajectory
(medians, 80 tasks of run hv-fk250-lunahigh-20261110T175632Z). Most frontier models on the CAO gateway have a ~1M-token
context. In the three Luna-high baseline runs, 35 of the 160 Harvey train tasks pass (all-pass) in at least two runs:
79 pairs of passing runs on the same task.

### Q1. Which LLM should make the calls in all three functions?

Options: GPT-5.6 Sol high · Claude Opus 5.5 · GPT-6.1 Sol · Configurable, F1 strong / F2-F3 cheaper.

**Answer:** Configurable, F1 strong / F2-F3 cheaper.

### Q2. How should the (long) trajectories be rendered into the prompts?

Function 1 sees two trajectories at once (~450K tokens median, up to ~860K). Options: Full text, cap only if over the
limit (recommended) · Cap tool outputs in F1 only · Cap tool outputs everywhere.

**Answer (verbatim):**

> okay, that is an intereting problem. can we essentially then tackle this problem by using "agents" instead of LLMs. We would have to create a small environment for the agent. We tell the agent that it will find two trajectories, we can specify the agent the size of the trajectories. and that it might not be able to read them full into its context so read them in parts , provide it the right tools to read the trajectories, maybe write some notes or observatoins and then it has to to produce the output as an output file that you mention. add any other tools you think the agent might need, but keep it restricted to only working on trajectories, like we don't eed oter general abilities for the agent like coding etc, i hope you get my point.

### Q3. How specific should the observation-action pairs from function 1 be?

Options: Task-specific, concrete · Abstract, transferable · Both levels per pair.

**Answer (verbatim):**

> yeah I want it abstract an transferrable, but make the abstract things as granular as possible. to make it concrete  in what was the semantic  importance of the task specific things in the context, as much as possible ! eg. writeing "a keyword" is fine. but if there is more info like "a keyword mentioned in the question" . "keyword with most hits" (if the reaosning trace says that it picked this keyword because it had the most hits) . so there can be two pairs obs: keyword search results -> act: identified keyword with most hits.  obs: keyword search result with identification of the most hit keyword ->act : files with most hit keyword opened.  so this is how I am thinkging about it now. maybe it is not perfct, if you think it can e improved further let me know I thik what happening is that the observation can be a very long term, as ana agent usually has a lot in its context before it takes some action, but try to make short meaningful observatoins that can be chiand, if you think that it can't be done then in a right way or if you think that such short observatoin would not be meaningful then you can let me know. We can choose to allow long overvations as well. but i would like to know your opinoin first

### Q4. Can an observation be something the agent itself concluded in its reasoning, or only external inputs?

Options: Anything in context, incl. own reasoning · Only external inputs (system prompt, task text, tool outputs).

**Answer (verbatim):**

> yeah I would say anything in context . in fact this is interesting. I would like to rather work wiht the reasoning process as a space where an agent is doing observations and actoins, if you think that's not a right way to think about it let me know. also one more thing. I like the questions you asked me and the ansewr i wrote, can you put these qna pairs in an md file. also the promp tto this task in the md ifle.
