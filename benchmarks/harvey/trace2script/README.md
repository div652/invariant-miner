# trace2script: agent trajectories as runnable scripts

Turns a recorded Harvey run (a DSH session) into a Python script that performs the same tool calls with the same
tool behaviour, then makes the model's judgement steps explicit as named, replaceable functions. Two layers:

- **Mechanical** (`mechanical.py`, generated): every tool call of the run, in order, with its exact arguments.
  Reasoning summaries and anything the model said become comments. Read-only calls of one step run together
  (`T.parallel(...)`, as DSH runs them); everything else runs one at a time. Nothing is dropped: `todo_write`, goals,
  jobs and `read_image` stay in.
- **Semantic** (`solve.py`, written from a copy): each decision the model took between calls (which files to open,
  which items qualify, how to name a client, what to write) is a `@semantic` function with a docstring quoting what
  the model decided, a version-0 body (plain code, imperfect on purpose) and the recorded decision. Calls whose
  arguments came from a decision now use the function's result.

Each script runs in two modes:
- **replay**: every semantic function returns the recorded decision, so the script must reproduce the run; the
  fidelity report checks every tool output and every deliverable against the recording;
- **live**: the functions return their own answers and the rest of the script follows them, so the script is a solver
  whose result can be graded like an agent run. Where live and recorded decisions differ is logged per function
  (`semantic.jsonl`), which shows which function to improve.

## Files

| File | What |
|---|---|
| `dsh_tools.py` | DSH's tools in Python, quirks included (formats, caps, ordering, errors, timeouts, spill), from DSH's own sources: `read` (numbered lines, 2,000-line window, 2,000-char lines, 50 KiB cap and its footers, workspace-isolated), `write` (Harvey's output/ rule, read before overwrite), `edit`, `glob` / `grep` (ripgrep in the task container with DSH's exact flags; 100-path / 250-match caps with the spill note; grep blind inside .docx), `bash` (`bash -c` in the container through `plugins/sandbox-podman/podman-exec.sh`, 60 s default timeout, stdout / `[stderr]` / exit, timeout and signal markers, background jobs), `job_*`, `todo_write`, goals, `read_image`, and the spill policy (results over 50,000 bytes cut to head + tail with the "Omitted N bytes" notice; spill files outside the workspace, so unreadable, as in the runs). |
| `trace2script.py` | Session -> `mechanical.py`, `recorded.json` (each call's tool, arguments and recorded output) and `meta.json`. The recorded workspace path becomes the marker `⟦WS⟧`. |
| `semantic.py` | The `@semantic` decorator and the replay / live switch; logs each decision with its agreement. |
| `run_script.py` | Stages a fresh workspace and container exactly like `dsh_bench/launch.py`, runs a script, writes the grader's layout (`spec.json`, `run.json`, `answer.json`, `workspace/`), the call log and the fidelity report; `--grade` runs `benchmarks/harvey/grade.py`. |
| `test_dsh_tools.py` | Offline checks of the file tools and the spill policy (18 checks). The container tools are checked by replay. |
| `scripts/<task>-<run>/` | One trajectory: `mechanical.py`, `solve.py`, `recorded.json`, `meta.json`. |

## Use

```bash
H=benchmarks/harvey/trace2script
python3 $H/trace2script.py runs/<run>/tasks/<task> --out $H/scripts/<name>             # -> mechanical.py
python3 $H/run_script.py $H/scripts/<name> --file mechanical.py --out runs/t2s-<name>-mech  # must be all "same"
cp $H/scripts/<name>/mechanical.py $H/scripts/<name>/solve.py                           # then add the semantic layer
python3 $H/run_script.py $H/scripts/<name> --out runs/t2s-<name>-replay                 # replay: all "same" again
python3 $H/run_script.py $H/scripts/<name> --out runs/t2s-<name>-live --mode live --grade
```

The fidelity report normalises what legitimately varies between runs: the workspace path, spill-file paths, goal ids
and timestamps (parse-doc prints dated warnings); grep results are compared as a set of lines (ripgrep's order is
not fixed). Anything else that differs is listed with the first differing line.

## Writing the semantic layer

- A decision gets a function where a later call's arguments, or the deliverable, depend on what the model concluded
  from earlier output. Steps that only look around stay as literal calls.
- The function takes the tool outputs the decision was based on and returns plain data; the call passes
  `recorded=<what the model decided>`. The docstring says what the model decided and why (its reasoning summary,
  or what it did next when the summary is empty).
- Code the model wrote and ran (Python in bash) stays verbatim; only the decision-dependent parts are filled in
  (`@SERIES@` style placeholders), so replay sends the same commands.
- Version 0 bodies are simple rules and regexes. They are meant to be improved, or replaced by model calls.

## First trajectory: firm-knowledge 210, run 2 (2026-11-15)

`scripts/210-run2/`: "who are our top five clients by number of matters?" The run (15/15) counted matter folders per
four-digit client series, kept the top five with ties, and read engagement letters only to name each client.

| Check | Result |
|---|---|
| mechanical.py replay | 32/32 tool outputs identical to the recording; `response.md` identical |
| solve.py replay | 32/32 identical; `response.md` identical |
| version-0 decisions agreeing with the model | 3 of 8: `top_series`, `client_names` (all six names), `matters_to_extract`. Different: `sample_letters`, `snippet_windows` (close), `matters_to_verify` (7 matters vs 4), `compose_answer` (template), `revise_answer` (none) |
| solve.py **live** (its own decisions, no model) | **15/15, all-pass** (graded with the Harvey grader) |

## Limits of this version

- One trajectory so far; each new one needs its semantic layer written (the mechanical layer is automatic).
- Background jobs, goal ids and wall-clock timing are emulated, not identical (job timing depends on the machine).
- `read_image` returns a placeholder text: the image goes to the model, not to the script.
- Live runs follow the script's control flow: a decision that should lead to calls the model never made needs a loop
  or branch written for it.
