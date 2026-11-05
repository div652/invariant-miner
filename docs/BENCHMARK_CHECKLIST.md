# New-benchmark checklist

Go through every item when a benchmark is added. Record the answers in `benchmarks/<name>/CHECKLIST.md` (copy the
template at the end). An item is done only when its answer is written down and, where it says so, tested. When a
benchmark teaches us a new kind of check, add it here so the next benchmark gets it too.

## 1. Task and prompts
- [ ] **Task prompt**: where it comes from (file, field), and whether it is passed verbatim.
- [ ] **System prompt**: does the benchmark give one? Append it after DSH's persona, or replace the persona?
- [ ] **Hard-coded paths** in the task or system prompt (`/workspace`, `/repo`, `~/...`): none, substitute the real
      path in the text, or does this benchmark need the in-container fallback?
- [ ] **Environment variables** the prompts mention (`$WORKSPACE_DIR`, `$OUTPUT_DIR`, ...): set them to the real paths
      inside the container.
- [ ] **Hidden material** never reaches the prompt: answers, rubrics, tests, grader notes.

## 2. Workspace
- [ ] **What is staged**: task files, a repo at a pinned commit, data downloads; their total size.
- [ ] **Layout and permissions**: which directories are read-only (e.g. `documents/`) and which are writable
      (e.g. `output/`). Read-only is enforced both in the container mount and on the host (the file tools run there).
- [ ] **Grading material stays outside the workspace**: rubrics, gold files, hidden tests, reference outputs.
- [ ] **Baseline snapshot** is taken after staging and before the agent starts (it is what the diff is against).
- [ ] **Harness artifacts stay outside the workspace**: DSH home, session logs, spill files, caches.

## 3. Sandbox image (where bash and glob/grep run)
- [ ] **Image**: the benchmark's own image, or `images/base` plus a benchmark layer
      (`benchmarks/<name>/Dockerfile`, `FROM dsh-bench-base`).
- [ ] **What the agent needs in it**: Python packages, CLIs (libreoffice, pandoc, git, compilers, ...), with versions.
      Only what the benchmark expects; do not add tools "just in case".
- [ ] **What the harness needs in it** (any image, including the benchmark's own): `bash`, coreutils `timeout`,
      `ripgrep` (`rg`, used by glob/grep). Node is NOT needed: the agent loop runs on the host.
- [ ] **User**: the container runs as the host uid/gid so files written in the workspace come back with the right owner.
- [ ] **Resource limits**: memory, CPUs, pids, disk, if the benchmark sets them.

## 4. Network and access
- [ ] **Container network**: `none` by default. If bash needs the network (package installs, APIs), which hosts.
- [ ] **Web tools** (`web_search`, `web_fetch`, run on the host): on or off. On needs the Exa relay.
- [ ] **Host paths visible to the agent**: only the workspace (file tools in `workspace-isolated` mode, container
      mounts only the workspace).
- [ ] **Credentials**: none in the container or the workspace. Tokens for the model, MCP servers and search stay on
      the host.

## 5. Tools
- [ ] **DSH native tools**: keep or disable each group (bash, file tools, glob/grep, web, subagents, todo, goal,
      workflow, skill). Disabling = `disabled: true` rows in `benchmarks/<name>/patch.yml`.
- [ ] **Benchmark tools served over MCP**: transport (stdio / streamable HTTP), URL or command, auth, timeout. One
      `dsh-mcp-client` row each. A stdio server's runtime must exist where it runs.
- [ ] **Benchmark tools not served over MCP** (Python functions, REST APIs): wrap them with the MCP bridge.
- [ ] **Tool names**: no collision with DSH tools (MCP tools appear as `mcp__<server>__<tool>`).
- [ ] **Side effects** the grader reads (simulated world state, database, files): every one goes through a logged
      tool call; the agent has no back door to them (e.g. `curl` from bash).

## 6. Skills
- [ ] **Skills provided?** Folder location (outside the workspace) and format (`SKILL.md` frontmatter).
- [ ] **Skill scripts** that must run in the container are available there.

## 7. Budgets and model
- [ ] Max steps, wall-clock timeout, output-token cap, context window, temperature, reasoning effort.
- [ ] Which of these the benchmark fixes, and which are our choice.

## 8. Ending and answer
- [ ] **How the agent signals it is done**: `final_answer` tool, or just stopping.
- [ ] **Answer format**: free text, JSON, file names; where the grader expects it.

## 9. Outputs and grading
- [ ] **What the grader reads**: files in a directory (which), the workspace diff, the final answer, container state,
      the trajectory.
- [ ] **How the grader is run**: command, environment, judge model and endpoint; it runs on the host, outside the
      agent's reach.
- [ ] **Output mapping**: where our run directory's outputs go in the layout the grader expects.

## 10. Validation
- [ ] **Smoke**: 1-2 tasks end to end (staging, run, collect, grade) with no harness errors.
- [ ] **Reference**: a published or earlier score to compare with (setup, model, judge), and our score on it.
- [ ] **Isolation tests**: bash cannot read outside the workspace, cannot write to read-only dirs, has no network
      when it should have none; file tools refuse paths outside the workspace.

---

## Template: `benchmarks/<name>/CHECKLIST.md`

```markdown
# <name>: checklist answers

| # | Item | Answer | Done |
|---|------|--------|------|
| 1 | Task prompt | | |
| 1 | System prompt (append / replace / none) | | |
| 1 | Hard-coded paths | | |
| 1 | Env vars | | |
| 2 | Staged files / repo | | |
| 2 | Read-only / writable dirs | | |
| 2 | Grading material location | | |
| 3 | Image | | |
| 3 | Agent packages | | |
| 3 | Resource limits | | |
| 4 | Container network | | |
| 4 | Web tools | | |
| 5 | Native tools kept / disabled | | |
| 5 | MCP servers | | |
| 5 | Non-MCP tools (bridge) | | |
| 6 | Skills | | |
| 7 | Budgets / model | | |
| 8 | Ending / answer format | | |
| 9 | Grader input / command | | |
| 10 | Smoke / reference / isolation tests | | |
```
