# Invariant mining report

Run: `runs/im-astra-edge-20261119T173221Z`

Points: **S** = support (passing runs other than P1/P2 where the observation was seen and the action followed), **I** = importance (failing runs where the observation was seen and the action did not follow), both written as points / runs: S = k/(the task's passing runs other than P1, P2), I = k/(its failing runs). ★ = the first invariant this failing run broke. Outcomes per run are the final verdicts after the re-check and the too-narrow check (DESIGN.md sections 4-5).

## Summary

| # | task | P1, P2 | other runs | proposed | rewordings | active | removed | retired |
|---|---|---|---|---|---|---|---|---|
| 1 | `firm-knowledge/tasks/092` | astra1, astra2 | 4 pass, 4 fail | 30 | 7 | 26 | 4 | 7 |
| 2 | `firm-knowledge/tasks/093` | astra1, astra2 | 4 pass, 4 fail | 24 | 6 | 21 | 3 | 6 |
| 3 | `firm-knowledge/tasks/179` | astra1, astra2 | 3 pass, 5 fail | 31 | 7 | 29 | 2 | 7 |
| 4 | `firm-knowledge/tasks/181` | astra1, astra2 | 3 pass, 5 fail | 26 | 6 | 25 | 1 | 6 |
| 5 | `firm-knowledge/tasks/190` | astra1, astra2 | 2 pass, 6 fail | 31 | 6 | 31 | 0 | 6 |
| 6 | `firm-knowledge/tasks/209` | astra1, astra2 | 3 pass, 5 fail | 21 | 4 | 20 | 1 | 4 |
| 7 | `firm-knowledge/tasks/240` | astra1, astra2 | 3 pass, 5 fail | 24 | 2 | 22 | 2 | 2 |
| 8 | `firm-knowledge/tasks/243` | astra1, astra2 | 4 pass, 4 fail | 28 | 4 | 24 | 4 | 4 |

Totals: at_pinned 83, f1_evidence_invalid 2, invariants_active 198, invariants_removed 17, invariants_retired 42, only_before 117, pinning_wrong 10, proposed 8, purpose_otherwise 56, recheck_disagrees 102, removed 15, reword_attempt_failed 11, reword_failed 3, reworded 42

## Task 1: `firm-knowledge/tasks/092`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (fail), luna2 (pass), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (6)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i11 | Candidate matters hold firm analysis memos or comparison charts summarizing the covenant provisions [tool_result] | Reads the text copies of the covenant analysis memos and comparison charts for each candidate matter | 4/4 | 3/4 | luna1 ★, luna4 ★, luna5 |
| ri25 | Many non-compete agreements in the corpus sit in transaction-document folders of M&A or commercial matters [tool_result] | Says in the report that non-competes from transaction or commercial matters are left out because the matter's scope is outside the target practice area, even when employment documents or people are involved. This can be a general statement or a matter listed as excluded. | 4/4 | 2/4 | luna1, luna5 ★ |
| i9 | The practice-area greps produced a list of candidate matters staffed by or classified in the target practice area [tool_result] | Runs a separate covenant-keyword grep over each candidate matter's text-copy folder | 4/4 | 1/4 | luna5 |
| i13 | A candidate matter's file discusses a third party's existing employment agreement with a non-compete, held with another employer [tool_result] | Reads the analysis memo on the third party's existing agreement, including its non-compete section | 3/4 | 1/4 | luna4 |
| i27 | The task deliverable cites many source document paths, some relative to a matter root [tool_result] | Runs a Python script that pulls the cited document paths out of the report and asserts each one exists in the corpus | 3/4 | 1/4 | luna1 |
| ri8 | Text copies of the corpus are available in the scratch folder [tool_result]; The task limits results to matters in the target practice area [task] | Runs a full-text search of the document contents for the target practice-area name, whether over the text copies or straight inside the original files, so that it covers at least the engagement, matter-memo, intake and conflict records | 3/4 | 1/4 | luna1 |

### Proposed by F1 (30)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (pass) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | The task needs multiple phases: find matters, verify covenants, write a report [task] | Creates a three-item todo list: inventory sources, verify execution/duration/evidence, write and check the report | retired → ri1 | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | same purpose, other action |
| i2 | The system prompt says the workspace holds a documents folder and an output folder [environment] | Lists the workspace root and globs the whole document tree | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i3 | Goal tools are available for one long-running completion objective [environment]; The task is a large retrieval-and-report job [task] | Creates a goal that restates the task objective, including verification and delivery of the task deliverable | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i4 | The document corpus has thousands of files, mostly .docx/.xlsx/.pptx/.eml [tool_result]; The read tool opens only plain text, and office files need conversion [environment] | Starts a background Python job that extracts text from every corpus document into text copies in a scratch folder, each tagged with its source path | removed (luna2) | 1/4 | 0/4 | only before | only before | followed | cancelled | not followed | cancelled | cancelled | cancelled |
| i5 | The task asks about a specific covenant type in employment matters [task] | Runs filename globs over the corpus for the covenant name, restrictive covenants and employment agreements | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i6 | The text-extraction job is still running in the background [tool_result] | Checks the background job's status with job_output between independent filename and partial-corpus searches | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | followed | not seen |
| i7 | A runtime notice says the background extraction job finished [tool_result] | Collects the job output and confirms the per-format conversion counts and an empty error list | retired → ri7 | 2/4 | 0/4 | followed | same purpose, other action | followed | cancelled | not seen | cancelled | cancelled | cancelled |
| i8 | Text copies of the corpus are available in the scratch folder [tool_result]; The task limits results to matters in the target practice area [task] | Greps the text copies for the target practice-area name, limited to engagement letters, matter memos, intake and conflict forms | retired → ri8 | 3/4 | 1/4 | followed | followed | followed | not followed | not seen | not seen | pinning wrong | same purpose, other action |
| i9 | The practice-area greps produced a list of candidate matters staffed by or classified in the target practice area [tool_result] | Runs a separate covenant-keyword grep over each candidate matter's text-copy folder | active | 4/4 | 1/4 | followed | followed | followed | not seen | followed | not seen | only before | not followed |
| i10 | Filename hits for restrictive-covenant or employment-agreement documents point to specific matter folders [tool_result] | Globs the full contents of each likely candidate matter folder | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i11 | Candidate matters hold firm analysis memos or comparison charts summarizing the covenant provisions [tool_result] | Reads the text copies of the covenant analysis memos and comparison charts for each candidate matter | active | 4/4 | 3/4 | followed | followed | followed | not followed ★ | followed | followed | not followed ★ | not followed |
| i12 | Some candidate matters contain only draft or redline versions of the employment agreement with the covenant [tool_result] | Greps those matters' closing or dormancy memos for execution, signing or withdrawal terms | removed (luna2) | 3/4 | 0/4 | followed | followed | followed | cancelled | same purpose, other action | cancelled | cancelled | cancelled |
| i13 | A candidate matter's file discusses a third party's existing employment agreement with a non-compete, held with another employer [tool_result] | Reads the analysis memo on the third party's existing agreement, including its non-compete section | active | 3/4 | 1/4 | followed | followed | followed | not seen | only before | not seen | not followed | only before |
| i14 | Candidate matter folders hold execution-version settlement agreements and a closing signature tracker [tool_result] | Reads the execution-version settlement agreements and the signature tracker | retired → ri14 | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | same purpose, other action | not seen | not seen |
| i15 | The signature tracker lists the settlement as 'awaiting execution', and an 'execution version' label does not prove signing [tool_result] | Reads or greps the matter closing memos for explicit statements that the agreements were executed and on what dates | active | 2/4 | 0/4 | followed | only before | followed | not seen | not seen | not seen | not seen | not seen |
| i16 | The settlement recitals mention an underlying employment agreement and amendment by date [tool_result] | Reads the filed cross-complaint, which alleges the agreement and amendment were executed and attaches them as exhibits | removed (astra5) | 1/4 | 0/4 | cancelled | followed | not followed | cancelled | only before | cancelled | cancelled | cancelled |
| i17 | Per-matter grep hits show that one candidate matter's contractor agreements carry a 12-month non-compete, signed by a stated number of people under one version [tool_result] | Reads that matter's witness declaration, then globs for and reads its agreement-version comparison chart | retired → ri17 | 2/4 | 0/4 | followed | followed | only before | cancelled | same purpose, other action | cancelled | cancelled | cancelled |
| i18 | An analysis memo shows a 12-month non-compete in a client's executed legacy agreements that the firm found void and removed [tool_result] | Reads that matter's closing letter/summary | active | 2/4 | 0/4 | followed | pinning wrong | only before | not seen | followed | not seen | not seen | not seen |
| i19 | Text extraction is done for the whole corpus [tool_result] | Runs a script that counts matter folders and extracted text copies | active | 0/4 | 0/4 | only before | only before | only before | not seen | not seen | not seen | not seen | not seen |
| i20 | Verification of execution, duration and evidence for all candidate matters is finished [reasoning] | Updates the todo list to mark inventory and verification done and report-writing in progress | active | 0/4 | 0/4 | action = pinned item | action = pinned item | action = pinned item | action = pinned item | only before | action = pinned item | action = pinned item | followed |
| i21 | Several candidate matters have confirmed execution evidence for a covenant of at least the minimum duration [reasoning]; The task wants findings, the documents relied on and the reasoning in one self-contained markdown file [task] | Writes the task deliverable with a summary table of qualifying matters and, per matter, covenant terms, execution evidence, cited source documents and qualifications | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i22 | Some qualifying executed covenants were later found void, deleted or shortened by settlement [tool_result] | Counts these as historically executed covenants in the report and notes the voiding or modification as a qualification, keeping execution separate from enforceability | active | 4/4 | 0/4 | followed | followed | followed | not seen | followed | followed | pinning wrong | not seen |
| i23 | The closing/dormancy memos state that the drafted agreements in some candidate matters were never executed, because the candidate withdrew or declined [tool_result] | Lists those near-miss matters in an exclusions table with the reason and the controlling document | active | 2/4 | 0/4 | pinning wrong | followed | followed | not seen | not seen | not seen | followed | not seen |
| i24 | In one target-practice matter, the 12-month covenant belongs to a third party's existing agreement with another employer [tool_result]; That matter's closing memo says no definitive agreement was executed [tool_result] | Flags this matter separately as a fifth lead, kept apart from the qualifying matters, and does not count it as an executed client covenant | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | followed | not seen |
| i25 | Many non-compete agreements in the corpus sit in transaction-document folders of M&A or commercial matters [tool_result] | States in the report that acquisition and commercial non-competes were not counted just because employment documents or lawyers were involved | retired → ri25 | 3/4 | 0/4 | followed | followed | followed | cancelled | same purpose, other action | cancelled | cancelled | cancelled |
| i26 | The task deliverable has just been written [tool_result] | Reads back the opening section of the written task deliverable | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i27 | The task deliverable cites many source document paths, some relative to a matter root [tool_result] | Runs a Python script that pulls the cited document paths out of the report and asserts each one exists in the corpus | active | 3/4 | 1/4 | followed | followed | followed | not followed | not seen | not seen | not seen | not seen |
| i28 | Report validation found no missing citations [tool_result] | Marks every todo item complete | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i29 | The system prompt requires calling get_goal before update_goal and copying its id and revision [environment]; The goal objective has been achieved [reasoning] | Calls get_goal, then update_goal with the returned id and revision and action complete | removed (astra5) | 0/4 | 0/4 | action = pinned item | only before | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i30 | The goal is marked complete and the task deliverable is validated [tool_result] | Ends with a short message linking the task deliverable and summarizing the qualifying matters, evidence, and exclusions/qualifications | retired → ri30 | 2/4 | 0/4 | same purpose, other action | followed | followed | cancelled | not seen | cancelled | cancelled | cancelled |

### Added by rewording (7)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (pass) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri7 | i7 | Collects the job output and confirms the per-format conversion counts and an empty error list | Collects the finished job's output and checks the completion summary it reports (conversion totals, exit status or errors) to confirm that nothing was skipped or failed | astra4 (pass) | 1 | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | followed | not seen |
| ri17 | i17 | Reads that matter's witness declaration, then globs for and reads its agreement-version comparison chart | Reads that matter's own case documents (declarations, filings, memos or charts) that describe the agreement versions and their covenant and signing terms | luna2 (pass) | 1 | active | 3/4 | 0/4 | followed | followed | only before | not seen | followed | not seen | not seen | not seen |
| ri30 | i30 | Ends with a short message linking the task deliverable and summarizing the qualifying matters, evidence, and exclusions/qualifications | Ends with a short final message that points the user to the task deliverable, saying what it contains (with or without restating the findings) | astra3 (pass) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri25 | i25 | States in the report that acquisition and commercial non-competes were not counted just because employment documents or lawyers were involved | Says in the report that non-competes from transaction or commercial matters are left out because the matter's scope is outside the target practice area, even when employment documents or people are involved. This can be a general statement or a matter listed as excluded. | luna2 (pass) | 1 | active | 4/4 | 2/4 | followed | followed | followed | not followed | followed | followed | followed | not followed ★ |
| ri1 | i1 | Creates a three-item todo list: inventory sources, verify execution/duration/evidence, write and check the report | Creates a todo list whose items cover the task's phases in order: inventory sources, verify execution/duration/evidence, then write the report (the number and split of items can vary) | luna5 (fail) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | action = pinned item | followed | followed |
| ri8 | i8 | Greps the text copies for the target practice-area name, limited to engagement letters, matter memos, intake and conflict forms | Runs a full-text search of the document contents for the target practice-area name, whether over the text copies or straight inside the original files, so that it covers at least the engagement, matter-memo, intake and conflict records | luna5 (fail) | 1 | active | 3/4 | 1/4 | followed | followed | followed | not followed | not seen | followed | not seen | followed |
| ri14 | i14 | Reads the execution-version settlement agreements and the signature tracker | Reads the matter's settlement documents (the executed agreement, its exhibits, or its execution records) that recite the original covenants and how they were modified or voided | luna3 (fail) | 1 | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | followed | not seen | not seen |

### Removed (4)

| id | observation | action | why |
|---|---|---|---|
| i4 | The document corpus has thousands of files, mostly .docx/.xlsx/.pptx/.eml [tool_result]; The read tool opens only plain text, and office files need conversion [environment] | Starts a background Python job that extracts text from every corpus document into text copies in a scratch folder, each tagged with its source path | luna2 (pass): observation seen at s2.o1; Luna: not followed; Opus re-check: seen at s2.o1, not followed; same purpose by another action: no |
| i12 | Some candidate matters contain only draft or redline versions of the employment agreement with the covenant [tool_result] | Greps those matters' closing or dormancy memos for execution, signing or withdrawal terms | luna2 (pass): the purpose was achieved by another action, but both rewordings failed validation on P1/P2/luna2 |
| i16 | The settlement recitals mention an underlying employment agreement and amendment by date [tool_result] | Reads the filed cross-complaint, which alleges the agreement and amendment were executed and attaches them as exhibits | astra5 (pass): observation seen at s24.o3; Luna: not followed; Opus re-check: seen at s24.o3, not followed; same purpose by another action: no |
| i29 | The system prompt requires calling get_goal before update_goal and copying its id and revision [environment]; The goal objective has been achieved [reasoning] | Calls get_goal, then update_goal with the returned id and revision and action complete | astra5 (pass): observation seen at s30.o1; Luna: not followed; Opus re-check: seen at s33.c1, not followed; same purpose by another action: no |

### Failing runs (4)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna1 | 4 | 13 | 0 | 0 | 1 | i11 |  |
| luna3 | 0 | 12 | 0 | 0 | 2 |  | **breaks nothing** |
| luna4 | 2 | 8 | 0 | 1 | 1 | i11 |  |
| luna5 | 3 | 12 | 0 | 1 | 0 | ri25 |  |

### Events

at_pinned 8, only_before 15, pinning_wrong 4, proposed 1, purpose_otherwise 8, recheck_disagrees 15, removed 3, reword_attempt_failed 2, reword_failed 1, reworded 7

### Role terms (F1)

- **task deliverable**: the single self-contained markdown report the task asks for, written to the output folder
- **document corpus**: the read-only collection of matter folders holding office-format and email files
- **text copies**: plain-text versions of the corpus documents that the agent extracts into a scratch folder
- **target practice area**: the practice area the task filters matters by
- **target covenant**: the contract clause type the task asks about, with its minimum duration
- **candidate matter**: a matter in the target practice area that may contain a qualifying covenant
- **near-miss matter**: a candidate matter where the covenant was only drafted or negotiated, or belongs to a third party
- **execution evidence**: documents stating that an agreement was signed (closing memos, settlements, pleadings, declarations, trackers)

## Task 2: `firm-knowledge/tasks/093`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (pass), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (3)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i13 | Grep hits show the firm negotiating employment non-compete terms in some matters without a clear executed agreement [tool_result] | Reads the termination letters, closing memos or withdrawal/dormancy correspondence of those matters | 4/4 | 1/4 | luna5 |
| i21 | The deliverable has been created in the output folder [tool_result] | Reads back the written deliverable | 4/4 | 1/4 | luna2 ★ |
| ri10 | The task requires the agreement to be one the firm negotiated and executed itself [task]; The candidate matter has a matter closing memo and a signature tracker/closing checklist [tool_result] | Reads the candidate matter's closing-stage execution record (its closing memo and/or signature tracker/closing checklist) to check the firm's role and whether the agreement was signed, instead of relying on the agreement's terms alone | 4/4 | 1/4 | luna5 ★ |

### Proposed by F1 (24)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (pass) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Creates a three-phase todo list: identify candidate agreements, compare and verify the shortest qualifying one, write the deliverable | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i2 | The workspace contains a documents folder and an output folder [tool_result] | Lists every file in the document corpus with a recursive glob | active | 3/4 | 0/4 | followed | followed | followed | only before | followed | followed | followed | followed |
| i3 | The task asks about post-employment non-compete terms in agreements [task]; The corpus is organised as matter folders of documents and emails [tool_result] | Globs filenames for non-compete, restrictive-covenant, separation and employment documents and greps the plain-text emails for non-compete mentions | retired → ri3 | 4/4 | 0/4 | followed | followed | followed | followed | cancelled | same purpose, other action | cancelled | same purpose, other action |
| i4 | The read tool only opens plain text; .docx/.xlsx need conversion [environment]; The corpus listing is large and mostly .docx files [tool_result] | Counts the files in the corpus by extension with a short python script | removed (luna1) | 2/4 | 0/4 | followed | cancelled | followed | not followed | cancelled | cancelled | cancelled | cancelled |
| i5 | The corpus holds thousands of .docx files and hundreds of .eml files [tool_result]; Office documents cannot be grepped or read directly [environment] | Starts a background job that converts the whole corpus to a searchable text copy under a scratch folder, mirroring its paths | active | 2/4 | 0/4 | action = pinned item | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i6 | Email grep hits describe a modified shorter non-compete agreed in a settlement in one litigation matter [tool_result] | Lists all files in the candidate matter's folder | active | 2/4 | 0/4 | only before | followed | not seen | followed | not seen | not seen | not seen | not seen |
| i7 | The system prompt says to use goal tools for a long-running completion objective [environment]; The task is a multi-step research question across a large corpus [task] | Creates a goal to find, verify and deliver the shortest executed firm-negotiated non-compete with sources | retired → ri7 | 1/4 | 0/4 | followed | only before | same purpose, other action | same purpose, other action | cancelled | cancelled | cancelled | cancelled |
| i8 | A background conversion job is producing the searchable text copy [tool_result]; The task asks for the shortest non-compete duration [task] | Runs regex greps over the searchable text copy for non-compete wording near short month/day durations, repeatedly narrowing to durations shorter than the candidates found so far | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i9 | Grep hits in the candidate matter describe a shorter modified non-compete agreed in a settlement [tool_result]; The candidate matter folder contains a settlement agreement marked execution version and an exhibit of modified covenant terms [tool_result] | Reads the execution-version agreement and its incorporated covenant exhibit in the searchable text copy | active | 4/4 | 0/4 | followed | followed | followed | followed | only before | not seen | not seen | not seen |
| i10 | The task requires the agreement to be one the firm negotiated and executed itself [task]; The candidate matter has a matter closing memo and a signature tracker/closing checklist [tool_result] | Reads the candidate matter's closing memo and its signature tracker/closing checklist | retired → ri10 | 3/4 | 0/4 | followed | followed | followed | same purpose, other action | cancelled | cancelled | cancelled | cancelled |
| i11 | The signature pages of the execution-version agreement have blank signature and date lines for most parties [tool_result] | Inspects the original .docx files of the agreement and its exhibit for embedded media (signature images) with a python zip check | removed (astra4) | 2/4 | 0/4 | followed | not followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i12 | Grep hits show shorter (e.g. six-month) non-compete terms in diligence and strategy memos of other matters [tool_result] | Opens the source memos of the shorter-looking candidates to see whose agreement the term belongs to and whether the firm negotiated and executed it | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | not seen | not seen | not seen |
| i13 | Grep hits show the firm negotiating employment non-compete terms in some matters without a clear executed agreement [tool_result] | Reads the termination letters, closing memos or withdrawal/dormancy correspondence of those matters | active | 4/4 | 1/4 | followed | followed | followed | followed | followed | pinning wrong | followed | not followed |
| i14 | Search hits show a settlement in another matter that voided an employee's non-compete entirely [tool_result] | Reads that settlement agreement's covenant provisions and checks its matter closing memo for negotiation and execution | active | 4/4 | 0/4 | followed | followed | followed | followed | not seen | not seen | not seen | not seen |
| i15 | A separation agreement for a departing principal contains a post-employment non-compete, and a shorter period was proposed during its negotiation [tool_result] | Checks that matter's closing memo for the negotiation history and execution of the separation agreement | retired → ri15 | 2/4 | 0/4 | only before | followed | same purpose, other action | followed | cancelled | cancelled | cancelled | cancelled |
| i16 | The background conversion job is reported complete [tool_result] | Collects the job output and re-runs short-duration non-compete greps over the fully converted text copy | active | 3/4 | 0/4 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i17 | The candidate matter's settlement sets the shortest restriction found in a firm-negotiated, executed agreement [reasoning]; All shorter-looking candidates come from third-party/legacy agreements, rejected proposals or unexecuted negotiations [reasoning]; An executed settlement eliminated a non-compete entirely [tool_result] | Writes the deliverable: bottom line naming the qualifying precedent's duration and matter, quoted operative terms with scope and exceptions, a table of excluded shorter-looking candidates with reasons, and the elimination precedent distinguished as no-non-compete | active | 1/4 | 0/4 | action = pinned item | action = pinned item | followed | not seen | not seen | not seen | not seen | not seen |
| i18 | The execution-version copy has blank signature lines and no embedded signature images [tool_result]; The signature tracker still shows the agreement as awaiting execution [tool_result]; The later matter closing memo states the agreement was fully executed by all parties on its date [tool_result] | In the deliverable, relies on the closing memo for execution and adds an explicit signature-copy limitation advising the reader to obtain the signed counterpart | active | 1/4 | 0/4 | followed | action = pinned item | only before | not seen | not seen | not seen | not seen | not seen |
| i19 | The modified restriction period runs from the employees' resignation date, which came before the agreement was executed [tool_result] | States in the deliverable that the duration is measured from separation, not from execution | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | not seen | not seen | not seen |
| i20 | The task asks for the matters/documents relied on in a self-contained file [task] | Ends the deliverable with a numbered source register giving each document's corpus path and the relevant sections | retired → ri20 | 3/4 | 0/4 | followed | followed | followed | same purpose, other action | cancelled | cancelled | cancelled | cancelled |
| i21 | The deliverable has been created in the output folder [tool_result] | Reads back the written deliverable | active | 4/4 | 1/4 | followed | followed | followed | followed | not followed ★ | followed | followed | followed |
| i22 | A phase of the todo list has been finished [reasoning] | Updates the todo list, marking the identification phase done and later all phases completed | active | 3/4 | 0/4 | followed | followed | action = pinned item | followed | followed | followed | followed | followed |
| i23 | All todo items are completed and the deliverable is written [tool_result]; The system prompt requires calling get_goal before update_goal and copying its id and revision [environment] | Calls get_goal and then update_goal with the returned id and revision to mark the goal complete | removed (astra5) | 1/4 | 0/4 | followed | cancelled | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i24 | The goal is marked complete [tool_result] | Gives a brief final message linking the deliverable and naming the qualifying precedent's duration and matter | retired → ri24 | 3/4 | 0/4 | followed | followed | followed | not seen | same purpose, other action | followed | not seen | not seen |

### Added by rewording (6)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (pass) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri7 | i7 | Creates a goal to find, verify and deliver the shortest executed firm-negotiated non-compete with sources | Puts the research objective (find, verify and deliver the shortest executed firm-negotiated non-compete with sources) into a session tracking tool, either as one goal or as a list of tracked steps that cover it | astra5 (pass) | 2 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | only before | only before | only before |
| ri10 | i10 | Reads the candidate matter's closing memo and its signature tracker/closing checklist | Reads the candidate matter's closing-stage execution record (its closing memo and/or signature tracker/closing checklist) to check the firm's role and whether the agreement was signed, instead of relying on the agreement's terms alone | luna1 (pass) | 1 | active | 4/4 | 1/4 | followed | followed | followed | followed | followed | followed | followed | not followed ★ |
| ri20 | i20 | Ends the deliverable with a numbered source register giving each document's corpus path and the relevant sections | Includes in the deliverable a dedicated list of the documents relied on, giving each one's corpus path and the relevant sections or provisions | luna1 (pass) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri15 | i15 | Checks that matter's closing memo for the negotiation history and execution of the separation agreement | After seeing the shorter proposal, follows that agreement's negotiation through to its executed outcome, checking the negotiation history together with a record of the final signed version (a closing summary, or the executed agreement's own non-compete clause), to see which term was actually agreed | astra5 (pass) | 2 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | not seen | only before | not seen |
| ri3 | i3 | Globs filenames for non-compete, restrictive-covenant, separation and employment documents and greps the plain-text emails for non-compete mentions | Runs keyword searches for non-compete-related terms over filenames and/or directly readable text such as emails to make a shortlist of candidate agreements | luna5 (fail) | 2 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri24 | i24 | Gives a brief final message linking the deliverable and naming the qualifying precedent's duration and matter | Gives a brief closing message that points the user to where the finished deliverable was written (a short headline of the finding may be included) | luna2 (fail) | 1 | active | 3/4 | 0/4 | followed | not seen | followed | followed | not seen | not seen | not seen | followed |

### Removed (3)

| id | observation | action | why |
|---|---|---|---|
| i4 | The read tool only opens plain text; .docx/.xlsx need conversion [environment]; The corpus listing is large and mostly .docx files [tool_result] | Counts the files in the corpus by extension with a short python script | luna1 (pass): observation seen at s2.o1; Luna: not followed; Opus re-check: seen at s2.o1, not followed; same purpose by another action: no |
| i11 | The signature pages of the execution-version agreement have blank signature and date lines for most parties [tool_result] | Inspects the original .docx files of the agreement and its exhibit for embedded media (signature images) with a python zip check | astra4 (pass): observation seen at s29.o1#12859; Luna: not followed; Opus re-check: seen at s29.o1, not followed; same purpose by another action: no |
| i23 | All todo items are completed and the deliverable is written [tool_result]; The system prompt requires calling get_goal before update_goal and copying its id and revision [environment] | Calls get_goal and then update_goal with the returned id and revision to mark the goal complete | astra5 (pass): observation seen at s28.c1; Luna: not followed; Opus re-check: seen at s28.c1, not followed; same purpose by another action: no |

### Failing runs (4)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna2 | 1 | 8 | 0 | 1 | 0 | i21 |  |
| luna3 | 0 | 12 | 0 | 1 | 0 |  | **breaks nothing** |
| luna4 | 0 | 11 | 0 | 2 | 0 |  | **breaks nothing** |
| luna5 | 2 | 11 | 0 | 1 | 0 | ri10 |  |

### Events

at_pinned 5, f1_evidence_invalid 1, only_before 10, pinning_wrong 1, proposed 1, purpose_otherwise 8, recheck_disagrees 10, removed 3, reword_attempt_failed 3, reworded 6

### Role terms (F1)

- **document corpus**: the read-only task documents folder of matter files (mostly .docx plus .eml/.xlsx/.pptx)
- **searchable text copy**: plain-text conversions of the corpus that the agent wrote to a scratch folder
- **background conversion job**: the long-running background bash job that builds the searchable text copy
- **candidate matter**: the matter whose documents show a modified, shorter post-employment restriction agreed in a settlement
- **execution-version agreement**: the settlement agreement labelled 'Execution Version' plus its incorporated covenant exhibit in the candidate matter
- **execution record**: documents that show whether and when an agreement was signed: matter closing memo, signature tracker, closing checklist
- **qualifying precedent**: the shortest restriction found in an agreement the firm itself negotiated and executed
- **shorter-looking candidate**: a mention of a shorter restriction that fails the task's criteria (third-party or legacy agreement, rejected proposal, unexecuted negotiation)
- **elimination precedent**: an executed settlement that voided a restriction entirely instead of shortening it
- **deliverable**: the response.md answer file in the output folder

## Task 3: `firm-knowledge/tasks/179`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (fail), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (6)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i3 | The system prompt offers goal tools for one long-running completion objective [environment]; The task asks for a full review across the corpus written to a single report [task] | Creates a goal whose objective is to produce the sourced report in the output directory | 3/3 | 5/5 | luna1 ★, luna2 ★, luna3 ★, luna4 ★, luna5 ★ |
| i4 | The corpus consists mostly of .docx/.xlsx/.pptx/.eml files spread across many matter folders [tool_result]; The read tool opens plain text only; office files must be converted to text first [environment] | Runs a Python script that bulk-converts every source document into a mirrored plain-text tree in scratch | 3/3 | 4/5 | luna2, luna3, luna4, luna5 |
| i10 | A sponsor engagement letter names specific fund holdings to be transferred into a continuation vehicle [tool_result] | Greps engagement letters for the continuation-vehicle holdings' names | 2/3 | 2/5 | luna2, luna4 |
| i27 | The report file exists in the output directory [tool_result] | Reads back the opening section of the written report | 3/3 | 1/5 | luna1 |
| i20 | Sibling fund vehicles appear only as a predecessor fund or in an engagement's affiliate exclusion list [tool_result] | States in the report that no separate mandate for the sibling funds was found and their mentions are not work performed | 2/3 | 1/5 | luna1 |
| ri11 | The full list of matters in the sponsor and portfolio-company groups is known [tool_result]; Matter folders contain files named for closing, termination, close-out, status or dormancy [tool_result] | Singles out, by file name, the document in each matter that records its outcome (a closing, status, termination or dormancy record) | 2/3 | 1/5 | luna2 |

### Proposed by F1 (31)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Creates a three-step todo list (inventory records, trace relationships/analyze, write and verify report) | retired → ri1 | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | same purpose, other action |
| i2 | The workspace has a read-only documents directory holding the task documents and an output directory for deliverables [environment] | Lists the workspace and globs every file under the documents directory | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i3 | The system prompt offers goal tools for one long-running completion objective [environment]; The task asks for a full review across the corpus written to a single report [task] | Creates a goal whose objective is to produce the sourced report in the output directory | active | 3/3 | 5/5 | followed | followed | followed | not followed ★ | not followed ★ | not followed ★ | not followed ★ | not followed ★ |
| i4 | The corpus consists mostly of .docx/.xlsx/.pptx/.eml files spread across many matter folders [tool_result]; The read tool opens plain text only; office files must be converted to text first [environment] | Runs a Python script that bulk-converts every source document into a mirrored plain-text tree in scratch | active | 3/3 | 4/5 | followed | followed | followed | followed | not followed | not followed | not followed | not followed |
| i5 | A converted text corpus of all documents exists in scratch [tool_result]; The task names the target fund [task] | Greps the converted text corpus for the target fund's distinctive name | active | 3/3 | 0/5 | followed | followed | followed | followed | not seen | not seen | not seen | not seen |
| i6 | Name hits include engagement letters stating that a client company is a portfolio company of the target fund [tool_result]; Name hits also include many unrelated entities sharing the brand word [tool_result] | Greps engagement letters for the portfolio-company relationship phrase and for sibling fund numerals | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | not seen | followed |
| i7 | Relationship-phrase hits cluster in a few matter groups (one sponsor group plus several portfolio-company groups) [tool_result] | Scripts an extract of the opening section of every engagement letter in those matter groups into a scratch packet, then reads it | retired → ri7 | 1/3 | 0/5 | followed | same purpose, other action | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i8 | The sponsor matter group contains several matters, each with an engagement letter and/or conflicts memo [tool_result] | Reads the engagement letters and conflicts memos of the sponsor matters | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i9 | The task asks for everything done across the target fund's funds, not just the one fund [task] | Greps the corpus for sibling fund vehicles of the same sponsor family (other fund numerals) | retired → ri9 | 3/3 | 0/5 | followed | followed | followed | same purpose, other action | followed | followed | followed | followed |
| i10 | A sponsor engagement letter names specific fund holdings to be transferred into a continuation vehicle [tool_result] | Greps engagement letters for the continuation-vehicle holdings' names | active | 2/3 | 2/5 | not seen | followed | followed | followed | not followed | followed | not followed | followed |
| i11 | The full list of matters in the sponsor and portfolio-company groups is known [tool_result]; Matter folders contain files named for closing, termination, close-out, status or dormancy [tool_result] | Locates status documents per matter by filtering file paths on closing/status/termination/dormancy keywords | retired → ri11 | 3/3 | 2/5 | followed | followed | followed | cancelled | not followed | same purpose, other action | same purpose, other action | not followed |
| i12 | A status document has been located for most matters in the relevant groups [tool_result] | Reads the leading section of each matter's main status document (closing memo/letter, termination memo, close-out letter, dormancy memo) | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | followed | not seen |
| i13 | A matter's closing memorandum carries a placeholder closing date or otherwise leaves completion uncertain [tool_result] | Reads that matter's closing checklist to verify item statuses | active | 2/3 | 0/5 | followed | only before | followed | only before | not seen | not seen | not seen | not seen |
| i14 | A sponsor matter's closing checklist has a status legend (draft/under review/executed/outstanding) per item [tool_result] | Greps that checklist for status and execution markers | retired → ri14 | 0/3 | 0/5 | not seen | not seen | same purpose, other action | cancelled | cancelled | cancelled | cancelled | cancelled |
| i15 | A sponsor tax-structuring matter folder contains a correspondence email delivering the main memorandum [tool_result] | Reads the memorandum-delivery email for that sponsor matter | retired → ri15 | 2/3 | 0/5 | followed | same purpose, other action | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i16 | Relevant matter folders contain conflicts memos [tool_result] | Greps conflicts memos for prior/current representation, former/current client, waiver and consent language | retired → ri16 | 3/3 | 0/5 | followed | followed | followed | same purpose, other action | followed | cancelled | cancelled | cancelled |
| i17 | A portfolio-company conflicts memo reports no prior representation and calls the client new [tool_result]; Other matters for that same client exist in the corpus [tool_result] | Flags the inconsistent clearance statements and frames the deliverable as a relationship inventory, not a conflicts clearance | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | pinning wrong |
| i18 | Records for the portfolio-company clients show inconsistent identifiers (e.g. EINs) and name different majority sponsors [tool_result] | Decides not to treat every same-named record as one entity and to flag the identifier/ownership discrepancies | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i19 | Engagement letters for portfolio-company clients name responsible and billing partners [tool_result] | Extracts responsible/billing partner lines from the engagement records of the relevant matters | active | 3/3 | 0/5 | followed | followed | followed | only before | followed | only before | followed | only before |
| i20 | Sibling fund vehicles appear only as a predecessor fund or in an engagement's affiliate exclusion list [tool_result] | States in the report that no separate mandate for the sibling funds was found and their mentions are not work performed | active | 2/3 | 1/5 | followed | followed | action = pinned item | not followed | followed | pinning wrong | followed | followed |
| i21 | A continuation-vehicle holding has a name similar to a portfolio-company client [tool_result] | Explicitly distinguishes the similarly named holding from the portfolio-company client in the report | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | not seen | followed |
| i22 | A sponsor matter's status memo records it as dormant with no definitive agreements or funding for the proposed investment [tool_result] | Reports that proposed investment target as an unclosed/proposed investment, not a portfolio holding | active | 2/3 | 0/5 | action = pinned item | followed | followed | followed | followed | followed | followed | action = pinned item |
| i23 | Sponsor engagement letters name different entities as client (the fund, its GP, its management company, a sponsored SPAC) [tool_result]; A closing letter confirms a fund investment closed, with the investee separately represented [tool_result] | Reports, per sponsor matter, which entity is the firm's client and that investees are holdings rather than firm clients | active | 3/3 | 0/5 | followed | followed | followed | followed | not seen | followed | followed | followed |
| i24 | Closing records list post-closing obligations and open follow-up items for completed matters [tool_result] | Writes cross-sell opportunities grounded in documented follow-ups and scope gaps, labeled as proposals not existing mandates | active | 3/3 | 0/5 | followed | followed | followed | followed | not seen | followed | followed | followed |
| i25 | A relative write path is saved under the output directory, and only output files are delivered [environment]; The task requires a single self-contained markdown report with findings, relied-on documents and reasoning [task] | Writes response.md with an executive summary, full matter inventory, conflicts flags, cross-sell section and a source register of document paths | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i26 | The report has been written with a matter inventory table and a source register citing document paths [tool_result] | Runs a Python check on the report counting inventory rows/unique matter IDs and confirming each cited source path exists | removed (astra4) | 1/3 | 0/5 | cancelled | not followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i27 | The report file exists in the output directory [tool_result] | Reads back the opening section of the written report | active | 3/3 | 1/5 | followed | followed | followed | not followed | followed | followed | followed | followed |
| i28 | The report has been written and checked [tool_result] | Updates the todo list to mark all phases completed | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i29 | The system prompt requires calling get_goal before update_goal and copying its exact goal_id and revision [environment]; get_goal returned the active goal's id and revision [tool_result] | Calls get_goal, then update_goal with that id and revision and action complete | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i30 | The goal is marked complete [tool_result] | Ends with a brief message linking response.md and summarizing matter count, client distinctions, conflict flags and cross-sell content | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i31 | The task covers the target fund's funds and portfolio companies for a conflicts review [task] | States a plan to separate confirmed client work from counterparty references and similarly named entities | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |

### Added by rewording (7)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri15 | i15 | Reads the memorandum-delivery email for that sponsor matter | Reads a document from that sponsor matter that states what the main memorandum delivered and recommends, either the delivery email or the memorandum's own summary | astra4 (pass) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri14 | i14 | Greps that checklist for status and execution markers | Checks the per-item status and execution entries in that checklist, whether by searching for them or by reading the item sections | astra5 (pass) | 1 | active | 1/3 | 0/5 | action = pinned item | not seen | followed | not seen | not seen | not seen | only before | not seen |
| ri7 | i7 | Scripts an extract of the opening section of every engagement letter in those matter groups into a scratch packet, then reads it | Pulls the identifying, scope and relationship content of every engagement letter in those matter groups into a single batch output (e.g. an extract of opening sections or a pattern search over the letters), then reads it | astra4 (pass) | 1 | removed (astra5) | 2/3 | 0/5 | followed | followed | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| ri1 | i1 | Creates a three-step todo list (inventory records, trace relationships/analyze, write and verify report) | Creates a todo list that splits the review into tracked phases (inventory records, trace relationships/analyze, write and verify report), however many items it uses to do so | luna5 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri9 | i9 | Greps the corpus for sibling fund vehicles of the same sponsor family (other fund numerals) | Searches the whole corpus for references to the sponsor family as a whole, not only to the target fund's own name or matters, so that related fund vehicles show up | luna1 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri16 | i16 | Greps conflicts memos for prior/current representation, former/current client, waiver and consent language | Reviews the content of the conflicts memos, either by searching them or by reading them in full, for what they say about prior/current representations, former/current clients, waivers and consents | luna1 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri11 | i11 | Locates status documents per matter by filtering file paths on closing/status/termination/dormancy keywords | Singles out, by file name, the document in each matter that records its outcome (a closing, status, termination or dormancy record) | luna3 (fail) | 2 | active | 2/3 | 1/5 | followed | followed | action = pinned item | action = pinned item | not followed | followed | action = pinned item | followed |

### Removed (2)

| id | observation | action | why |
|---|---|---|---|
| i26 | The report has been written with a matter inventory table and a source register citing document paths [tool_result] | Runs a Python check on the report counting inventory rows/unique matter IDs and confirming each cited source path exists | astra4 (pass): observation seen at s53.c1; Luna: not followed; Opus re-check: seen at s53.c1, not followed; same purpose by another action: no |
| ri7 | Relationship-phrase hits cluster in a few matter groups (one sponsor group plus several portfolio-company groups) [tool_result] | Pulls the identifying, scope and relationship content of every engagement letter in those matter groups into a single batch output (e.g. an extract of opening sections or a pattern search over the letters), then reads it | astra5 (pass): observation seen at s23.o2; Luna: not followed; Opus re-check: seen at s27.o1, not followed; same purpose by another action: no |

### Failing runs (5)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna1 | 3 | 5 | 0 | 2 | 1 | i3 |  |
| luna2 | 4 | 9 | 0 | 0 | 0 | i3 |  |
| luna3 | 2 | 7 | 0 | 1 | 0 | i3 |  |
| luna4 | 3 | 6 | 0 | 1 | 1 | i3 |  |
| luna5 | 2 | 6 | 0 | 1 | 1 | i3 |  |

### Events

at_pinned 7, only_before 6, pinning_wrong 2, proposed 1, purpose_otherwise 8, recheck_disagrees 15, removed 2, reword_attempt_failed 1, reworded 7

### Role terms (F1)

- **target fund**: the fund entity named in the task as the subject of the review
- **sponsor matters**: matters where the target fund or its GP/management company/sponsored vehicle is the firm's client
- **portfolio-company clients**: companies that engagement letters describe as portfolio companies of the target fund, and that the firm represents
- **matter groups**: families of matter folders sharing a client number prefix
- **converted text corpus**: plain-text copies of all source documents written to a scratch directory
- **status documents**: closing memos/letters, closing checklists, termination, close-out and dormancy memos that show a matter's outcome
- **conflicts memos**: conflict-check / clearance memoranda inside matter folders
- **sibling fund vehicles**: other numbered funds of the same sponsor family as the target fund
- **continuation-vehicle holdings**: fund holdings named in a sponsor engagement as being moved into a continuation vehicle
- **report**: the deliverable response.md in the output directory

## Task 4: `firm-knowledge/tasks/181`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (fail), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (2)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i14 | A status-report email for an active matter has an empty Date header [tool_result] | Decides to rely on dated documents (declaration, dated memo) rather than the undated email for the workload timeline | 1/3 | 2/5 | luna3, luna4 ★ |
| i22 | Some records credit associates with related but different work (patent prosecution, licensing, transactional IP) or name partners and non-firm people [tool_result] | States inclusion criteria: counts only actual involvement in the litigation type; excludes prosecution/licensing/transactional work, mere practice-group labels, partners, opposing counsel and client staff | 3/3 | 1/5 | luna3 ★ |

### Proposed by F1 (26)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Creates a todo list that splits the work into finding sources, evaluating candidates, and writing the deliverable | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i2 | The system prompt says task documents are in a documents directory in the workspace [environment] | Lists the workspace, globs every file in the document corpus, then lists its top-level folders | retired → ri2 | 3/3 | 0/5 | followed | followed | followed | same purpose, other action | same purpose, other action | cancelled | followed | same purpose, other action |
| i3 | The task asks about a specific litigation type and about staffing availability [task]; The corpus is a large tree of matter folders [tool_result] | Globs file names for keywords from the task (the litigation type, staffing) and related terms | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i4 | Most files in the corpus are .docx (plus .eml), and the read tool opens plain text only [environment]; The corpus has thousands of documents [tool_result] | Runs a Python script that bulk-extracts the text of all docx/eml files into a scratch text corpus that mirrors the folder structure | removed (astra5) | 1/3 | 0/5 | followed | cancelled | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i5 | Filename hits for the litigation keyword cluster in a few matter folders [tool_result] | Lists all files in the matter folders that had keyword filename hits | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i6 | A text corpus of all documents now exists [tool_result]; Engagement documents state each matter's subject and staffing [reasoning] | Greps engagement-named text files for phrases about the litigation type | active | 2/3 | 0/5 | followed | followed | not seen | not seen | not seen | not seen | not seen | not seen |
| i7 | The engagement grep found a relevant matter whose engagement letter has not been read yet [tool_result] | Reads the staffing section of the engagement letters of the relevant matters | active | 1/3 | 0/5 | only before | only before | followed | not seen | followed | not seen | followed | followed |
| i8 | A text corpus of all documents exists [tool_result]; The task asks specifically about associates [task] | Greps the whole text corpus for 'associate' near the litigation-type term | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | not seen | followed |
| i9 | An associate is named as lead associate on a relevant litigation only in a matter folder of conflicts/intake records [tool_result] | Searches for and reads the conflicts-file documents that name that associate and describe the underlying litigation | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i10 | The task asks who is available, not only who has experience [task] | Greps documents for staffing, capacity and availability terms (in matter admin files or near candidate names) | retired → ri10 | 3/3 | 0/5 | followed | followed | followed | same purpose, other action | followed | followed | followed | followed |
| i11 | Candidate associates are tied to specific relevant matters [tool_result]; Those matter folders contain closing letters/memos [tool_result] | Reads the closing letters/memos of the candidates' matters | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i12 | Some relevant matters have no closing document, and the status reports read so far are older [tool_result] | Reads the most recent status reports and trial/discovery planning memos of the still-active matters | active | 2/3 | 0/5 | followed | followed | only before | followed | not seen | followed | only before | followed |
| i13 | Candidate associates were found through staffing records naming their roles [tool_result] | Reads memos and declarations the candidate associates wrote in the relevant matters | retired → ri13 | 3/3 | 1/5 | followed | followed | followed | followed | not followed | followed | same purpose, other action | followed |
| i14 | A status-report email for an active matter has an empty Date header [tool_result] | Decides to rely on dated documents (declaration, dated memo) rather than the undated email for the workload timeline | active | 1/3 | 2/5 | followed | not seen | not seen | not seen | not seen | not followed | not followed ★ | not seen |
| i15 | Every candidate associate is backed by staffing records and work product in relevant matters [reasoning]; The task requires one self-contained response.md with findings, sources and reasoning [task] | Writes response.md with a bottom line naming every candidate associate, a per-associate table of roles and work, and a list of matters/documents with file paths | active | 2/3 | 0/5 | followed | followed | action = pinned item | action = pinned item | action = pinned item | followed | followed | followed |
| i16 | No document gives current capacity, calendars or staffing clearance for the candidates [tool_result] | States in the deliverable that the list is an experience shortlist, not confirmation of current availability | active | 0/3 | 0/5 | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item |
| i17 | Closing dates for some candidate matters and dated ongoing/scheduled work for others [tool_result] | Writes an availability section that summarizes, per associate, which matters are closed (with dates) and which show ongoing or scheduled workload | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i18 | A matter's closing letter says the active phase is substantially complete but the formal engagement stays open until a later condition is met [tool_result] | Reports that matter as wound down but conditionally open, not as proof of complete disengagement | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | followed | followed | not seen |
| i19 | A planning memo schedules a trial for a future date, and no record shows the trial took place or how it ended [tool_result] | Presents the scheduled trial as trial-preparation responsibility, not as completed trial experience or proof the associates are now free | active | 0/3 | 0/5 | action = pinned item | action = pinned item | action = pinned item | followed | followed | followed | followed | followed |
| i20 | A 'closure' record in the conflicts folder concerns a declined prospective engagement, not the associate's continuing litigation [tool_result] | States in the deliverable that the closure concerns the declined engagement and that the candidate's litigation was still active | active | 2/3 | 0/5 | followed | not seen | followed | not seen | not seen | not seen | not seen | not seen |
| i21 | Documents in one matter folder use an internal matter number different from the folder's number [tool_result] | Notes the matter-number discrepancy in the sources section and identifies the matter by caption and docket | retired → ri21 | 2/3 | 0/5 | followed | same purpose, other action | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i22 | Some records credit associates with related but different work (patent prosecution, licensing, transactional IP) or name partners and non-firm people [tool_result] | States inclusion criteria: counts only actual involvement in the litigation type; excludes prosecution/licensing/transactional work, mere practice-group labels, partners, opposing counsel and client staff | active | 3/3 | 1/5 | followed | followed | followed | followed | followed | not followed ★ | followed | followed |
| i23 | Each relevant matter has a named supervising partner [tool_result]; Current availability is not shown in the records [reasoning] | Recommends confirming each candidate's current commitments with the matter's supervising partner and running a fresh conflicts check before staffing | active | 1/3 | 0/5 | action = pinned item | action = pinned item | followed | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item |
| i24 | Each relevant matter involves a distinct technology area and side (plaintiff/defense) [tool_result] | Gives each associate a subject-matter staffing fit and says these are matches, not availability rankings | retired → ri24 | 3/3 | 1/5 | followed | followed | followed | not followed | same purpose, other action | not seen | same purpose, other action | cancelled |
| i25 | The deliverable has just been written to the output directory [tool_result] | Reads back response.md from the output directory | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i26 | The deliverable has been written and checked [tool_result] | Marks all todos completed and ends with a short message pointing to response.md and its main findings | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |

### Added by rewording (6)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri21 | i21 | Notes the matter-number discrepancy in the sources section and identifies the matter by caption and docket | Discloses the matter-number discrepancy somewhere in the deliverable and refers to the matter by identifiers the reader cannot mistake (e.g. case caption, court or docket, or an explicitly labeled source folder number) | astra4 (pass) | 1 | retired → ri21.2 | 3/3 | 1/5 | followed | followed | followed | same purpose, other action | same purpose, other action | followed | not followed | same purpose, other action |
| ri2 | i2 | Lists the workspace, globs every file in the document corpus, then lists its top-level folders | Enumerates the workspace's document corpus (via listing and/or a recursive file glob) to see its folder structure and file count before targeted searches | luna2 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri10 | i10 | Greps documents for staffing, capacity and availability terms (in matter admin files or near candidate names) | Searches the documents, by content or by file name, for staffing, capacity and availability terms (in matter admin files or near candidate names) | luna1 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri13 | i13 | Reads memos and declarations the candidate associates wrote in the relevant matters | Checks matter documents that show the concrete work each candidate associate actually did in the relevant matters, such as work product they wrote or closing records describing their contributions | luna4 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri24 | i24 | Gives each associate a subject-matter staffing fit and says these are matches, not availability rankings | Gives each associate a subject-matter staffing fit and keeps that fit separate from availability, stating plainly that the records do not confirm availability | luna4 (fail) | 1 | active | 2/3 | 0/5 | followed | followed | not seen | followed | followed | followed | followed | followed |
| ri21.2 | ri21 | Discloses the matter-number discrepancy somewhere in the deliverable and refers to the matter by identifiers the reader cannot mistake (e.g. case caption, court or docket, or an explicitly labeled source folder number) | Cites the affected matter in the deliverable by one consistent set of identifiers the reader cannot mistake (e.g. case caption, court or docket, source folder number or full document paths), whether or not the conflicting internal number is also mentioned or explained | luna2 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |

### Removed (1)

| id | observation | action | why |
|---|---|---|---|
| i4 | Most files in the corpus are .docx (plus .eml), and the read tool opens plain text only [environment]; The corpus has thousands of documents [tool_result] | Runs a Python script that bulk-extracts the text of all docx/eml files into a scratch text corpus that mirrors the folder structure | astra5 (pass): observation seen at s3.o1; Luna: not followed; Opus re-check: seen at s3.o1, not followed; same purpose by another action: no |

### Failing runs (5)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna1 | 0 | 7 | 0 | 0 | 3 |  | **breaks nothing** |
| luna2 | 0 | 7 | 0 | 0 | 3 |  | **breaks nothing** |
| luna3 | 2 | 5 | 0 | 0 | 2 | i22 |  |
| luna4 | 1 | 4 | 0 | 1 | 2 | i14 |  |
| luna5 | 0 | 5 | 0 | 0 | 2 |  | **breaks nothing** |

### Events

at_pinned 21, only_before 4, proposed 1, purpose_otherwise 11, recheck_disagrees 21, removed 1, reworded 6

### Role terms (F1)

- **the task**: user request to identify associates with experience in a specific litigation type and their availability, delivered as response.md
- **document corpus**: read-only collection of matter folders under the documents directory, mostly office files plus emails
- **text corpus**: plain-text copies of all documents extracted by the agent into a scratch folder
- **relevant matters**: matter folders whose documents concern the litigation type named in the task
- **candidate associates**: associates the records tie to a relevant matter by role or work product
- **staffing records**: engagement letters, intake forms and closing memos naming the team on a matter
- **status documents**: closing letters/memos, status reports and planning memos that show whether a matter is ongoing or done
- **supervising partner**: the partner responsible for a relevant matter
- **deliverable**: response.md written to the output directory

## Task 5: `firm-knowledge/tasks/190`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (fail), astra5 (pass), luna1 (fail), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (13)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| ri28 | The response file has been written with cited document paths and a table of date rows [tool_result] | Runs a scripted check on the written response that confirms the cited document paths exist and recomputes its date arithmetic (per-row day differences, plus row count or summary statistics) against what the response states | 2/2 | 5/6 | luna1, luna2, luna3, luna4, luna5 |
| i24 | Verified signing and actual closing date pairs exist for each confirmed closed deal [reasoning] | Runs a Python script that computes calendar days per deal plus mean, median, min, max and sum | 1/2 | 3/6 | luna1, luna4 ★, luna5 |
| i23 | The candidate deal population has been established [reasoning] | Updates the todo list: population step completed, date verification in progress | 2/2 | 2/6 | luna1, luna2 ★ |
| i7 | The task limits scope to deals of one named practice [task]; The text corpus exists [tool_result] | Greps the engagement-letter texts for practice-group/practice-area labels and the practice name | 2/2 | 1/6 | luna5 |
| i14 | Some candidate matters contain termination letters, dormancy memos or terminated-status memos [tool_result] | Reads those termination and dormancy documents | 2/2 | 1/6 | luna3 ★ |
| i20 | Some candidates' closing checklists still show in-progress or pending items and estimated closing dates [tool_result] | Leaves those matters out of the confirmed closed set and lists them separately as not-verified or pending | 2/2 | 1/6 | luna2 |
| i22 | Some acquisition-related engagements may belong to a different practice or a specialist workstream (tax, antitrust, financing, special committee) [tool_result] | Checks those engagement letters' responsible partner, practice and scope to rule them in or out | 2/2 | 1/6 | luna5 ★ |
| i26 | Dates have been verified and the statistics computed [tool_result] | Updates the todo list: verification completed, report writing in progress | 2/2 | 1/6 | luna1 |
| ri1 | ∅ (always) | Writes a todo plan whose phases cover at least identifying the population, verifying dates against sources and writing the sourced report. Extra phases, such as an inventory first or a review at the end, are allowed. | 2/2 | 1/6 | luna1 ★ |
| ri2 | A goal tool is available [environment]; The task asks for a complete, sourced deliverable [task] | At the start, records the task's objective as an explicit tracked completion target (a goal or a task checklist): find all closed deals, verify signing and actual closing dates, deliver a sourced response file | 2/2 | 1/6 | luna1 |
| i6 | The conversion is running as a background job and a notice reports it finished [tool_result] | Calls job_output to read the conversion counts and errors | 1/2 | 1/6 | luna3 |
| i9 | Each engagement letter's subject (Re:) line describes the matter's transaction [tool_result] | Pulls a compact list of engagement-letter subject lines across all matters | 1/2 | 1/6 | luna4 |
| i5 | The corpus includes spreadsheet files, such as closing checklists, that hold key dates [tool_result] | Extracts spreadsheet cell values row by row into text files | 0/2 | 1/6 | luna5 |

### Proposed by F1 (31)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (fail) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Writes a three-item todo plan: identify the population, verify dates against sources, write the sourced report | retired → ri1 | 2/2 | 1/6 | followed | followed | followed | not followed | same purpose, other action | followed | same purpose, other action | followed |
| i2 | A goal tool is available [environment]; The task asks for a complete, sourced deliverable [task] | Creates a goal restating the objective: find all closed deals, verify signing and actual closing dates, deliver a sourced response file | retired → ri2 | 2/2 | 0/6 | followed | followed | followed | cancelled | followed | same purpose, other action | same purpose, other action | cancelled |
| i3 | ∅ (always) | Lists the documents directory to see how the corpus is laid out | active | 2/2 | 0/6 | followed | followed | followed | followed | followed | followed | followed | followed |
| i4 | The corpus holds thousands of word-processing and email files spread across matter folders [tool_result]; There is no metadata or index file [tool_result] | Writes a Python script that extracts text from the word-processing files (zip XML) and the email files into a parallel text corpus | active | 1/2 | 0/6 | followed | only before | only before | not seen | not seen | not seen | not seen | not seen |
| i5 | The corpus includes spreadsheet files, such as closing checklists, that hold key dates [tool_result] | Extracts spreadsheet cell values row by row into text files | active (rewording failed twice) | 0/2 | 1/6 | only before | only before | only before | only before | followed | action = pinned item | same purpose, other action | not followed |
| i6 | The conversion is running as a background job and a notice reports it finished [tool_result] | Calls job_output to read the conversion counts and errors | active | 1/2 | 1/6 | followed | followed | not seen | not seen | not seen | not followed | not seen | not seen |
| i7 | The task limits scope to deals of one named practice [task]; The text corpus exists [tool_result] | Greps the engagement-letter texts for practice-group/practice-area labels and the practice name | active | 2/2 | 1/6 | followed | followed | followed | followed | followed | followed | followed | not followed |
| i8 | Engagement letters name a responsible partner together with the practice group [tool_result] | Greps engagement letters for responsible-partner lines tied to the practice, together with transaction-type subject lines | active | 2/2 | 0/6 | followed | followed | followed | only before | followed | followed | followed | not seen |
| i9 | Each engagement letter's subject (Re:) line describes the matter's transaction [tool_result] | Pulls a compact list of engagement-letter subject lines across all matters | active | 1/2 | 1/6 | followed | followed | pinning wrong | not seen | followed | followed | not followed | not seen |
| i10 | A list of about 33-34 candidate deal matter IDs has been settled from the engagement screening [reasoning] | Runs a script that copies or compiles the candidate matters' texts into a scoped working set | active | 1/2 | 0/6 | action = pinned item | followed | followed | not seen | followed | only before | not seen | not seen |
| i11 | Broad date-phrase greps return truncated, noisy output [tool_result] | Greps with a regex for '(closed\|consummated\|...) on <Month> <day>, <year>' | retired → ri11 | 2/2 | 0/6 | followed | only before | followed | only before | cancelled | followed | same purpose, other action | not seen |
| i12 | Closing checklists are spreadsheets with labelled key-date fields [tool_result] | Greps the checklist/spreadsheet texts for labels such as Signing Date, Actual Closing Date and Closing Date | retired → ri12 | 1/2 | 1/6 | followed | only before | only before | not followed | followed | only before | same purpose, other action | not seen |
| i13 | For some candidate matters, screening shows no clear closing records or an unclear status [tool_result] | Globs the full folder listing of several unclear candidate matters in parallel | active | 1/2 | 0/6 | only before | followed | followed | followed | followed | only before | only before | followed |
| i14 | Some candidate matters contain termination letters, dormancy memos or terminated-status memos [tool_result] | Reads those termination and dormancy documents | active | 2/2 | 1/6 | followed | followed | followed | followed | followed | not followed ★ | followed | followed |
| i15 | A terminated deal's matter has a 'matter closing' memo recording administrative file closure [tool_result] | Treats the administrative matter closure as not a deal closing and lists the matter as terminated in the exclusions | active | 1/2 | 0/6 | followed | followed | action = pinned item | not seen | followed | followed | not seen | followed |
| i16 | Candidate deals have closing checklists, closing memos or post-closing letters in their folders [tool_result] | Reads the closing records of each likely closed deal to check signing and actual closing dates | active | 2/2 | 0/6 | followed | followed | followed | followed | followed | followed | followed | followed |
| i17 | A matter's folder contains an execution-version definitive agreement [tool_result] | Reads the opening lines of the executed definitive agreement to confirm the signing date | active | 2/2 | 0/6 | followed | followed | followed | followed | followed | followed | followed | followed |
| i18 | Closing records show a scheduled/target/expected closing date and a later actual closing date [tool_result] | Uses the actual closing date, not the target date, for each deal's interval | active | 2/2 | 0/6 | followed | followed | followed | followed | followed | followed | followed | followed |
| i19 | A tender-offer deal's closing memo lists several milestones: offer commencement, definitive agreement execution, offer expiration, acceptance and merger [tool_result] | Takes the definitive agreement execution date as signing and the acceptance/merger date as closing | active | 2/2 | 0/6 | followed | action = pinned item | followed | not seen | not seen | followed | not seen | not seen |
| i20 | Some candidates' closing checklists still show in-progress or pending items and estimated closing dates [tool_result] | Leaves those matters out of the confirmed closed set and lists them separately as not-verified or pending | active | 2/2 | 1/6 | followed | followed | followed | followed | not followed | followed | followed | followed |
| i21 | The population was built mainly from one spelling of the practice name [reasoning] | Runs a complementary case-insensitive grep for alternate practice wordings in engagement letters | active | 0/2 | 0/6 | only before | followed | only before | not seen | only before | only before | not seen | not seen |
| i22 | Some acquisition-related engagements may belong to a different practice or a specialist workstream (tax, antitrust, financing, special committee) [tool_result] | Checks those engagement letters' responsible partner, practice and scope to rule them in or out | active | 2/2 | 1/6 | followed | followed | followed | only before | followed | followed | followed | not followed ★ |
| i23 | The candidate deal population has been established [reasoning] | Updates the todo list: population step completed, date verification in progress | active | 2/2 | 2/6 | followed | followed | followed | not followed | not followed ★ | followed | only before | followed |
| i24 | Verified signing and actual closing date pairs exist for each confirmed closed deal [reasoning] | Runs a Python script that computes calendar days per deal plus mean, median, min, max and sum | active | 1/2 | 3/6 | only before | action = pinned item | followed | not followed | followed | followed | not followed ★ | not followed |
| i25 | One confirmed closed deal is a joint venture rather than an acquisition or divestiture [tool_result] | Also computes the mean and median with the joint venture left out | active | 2/2 | 0/6 | followed | followed | followed | not seen | followed | not seen | not seen | not seen |
| i26 | Dates have been verified and the statistics computed [tool_result] | Updates the todo list: verification completed, report writing in progress | active | 2/2 | 1/6 | followed | action = pinned item | followed | not followed | action = pinned item | only before | only before | followed |
| i27 | The task requires a self-contained markdown file with findings, the documents relied on and the reasoning [task]; Benchmark statistics and the verified deal rows are available [tool_result] | Writes the response file with summary stats, a per-deal table (matter, client/deal, type, signing, actual closing, days, source ref), method notes on target vs actual dates, per-deal source paths, and tables of excluded terminated/dormant/unverified matters | active | 2/2 | 0/6 | followed | followed | followed | action = pinned item | followed | followed | action = pinned item | action = pinned item |
| i28 | The response file has been written with cited document paths and a table of date rows [tool_result] | Runs a Python check that every cited path exists, recomputes each row's day difference against the table, and confirms the row count, mean and median | retired → ri28 | 2/2 | 5/6 | followed | same purpose, other action | followed | not followed | not followed | not followed | not followed | not followed |
| i29 | The validation passed: no missing paths and the expected row count and stats [tool_result] | Marks all todo items completed | active | 2/2 | 0/6 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i30 | The goal created at the start is still active [tool_result] | Fetches the goal, then updates it with action complete | active | 2/2 | 0/6 | followed | followed | followed | not seen | not seen | not seen | not seen | not seen |
| i31 | The goal is marked complete and the response file exists [tool_result] | Sends a brief final message linking the response file and stating the number of closed deals and what the file contains | retired → ri31 | 2/2 | 0/6 | followed | same purpose, other action | followed | not seen | cancelled | not seen | not seen | followed |

### Added by rewording (6)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (fail) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri1 | i1 | Writes a three-item todo plan: identify the population, verify dates against sources, write the sourced report | Writes a todo plan whose phases cover at least identifying the population, verifying dates against sources and writing the sourced report. Extra phases, such as an inventory first or a review at the end, are allowed. | luna2 (fail) | 1 | active | 2/2 | 1/6 | followed | followed | followed | not followed ★ | followed | followed | followed | followed |
| ri2 | i2 | Creates a goal restating the objective: find all closed deals, verify signing and actual closing dates, deliver a sourced response file | At the start, records the task's objective as an explicit tracked completion target (a goal or a task checklist): find all closed deals, verify signing and actual closing dates, deliver a sourced response file | luna4 (fail) | 1 | active | 2/2 | 1/6 | followed | followed | followed | not followed | followed | followed | followed | followed |
| ri11 | i11 | Greps with a regex for '(closed\|consummated\|...) on <Month> <day>, <year>' | Instead of a broad date search, goes straight to explicit statements of the actual closing date, either with a tight closing-verb-plus-date search or by finding and reading the closing-specific documents where such statements appear. | luna4 (fail) | 1 | active | 2/2 | 0/6 | followed | followed | followed | followed | followed | followed | followed | not seen |
| ri12 | i12 | Greps the checklist/spreadsheet texts for labels such as Signing Date, Actual Closing Date and Closing Date | Searches the extracted text of the matter documents (checklists, agreements or memos) for wording that marks signing/agreement dates and closing dates | luna4 (fail) | 1 | active | 2/2 | 0/6 | followed | followed | followed | only before | followed | followed | followed | followed |
| ri31 | i31 | Sends a brief final message linking the response file and stating the number of closed deals and what the file contains | Sends a brief final message that links the response file and summarizes what it contains | astra4 (fail) | 1 | active | 2/2 | 0/6 | followed | followed | followed | not seen | followed | followed | followed | followed |
| ri28 | i28 | Runs a Python check that every cited path exists, recomputes each row's day difference against the table, and confirms the row count, mean and median | Runs a scripted check on the written response that confirms the cited document paths exist and recomputes its date arithmetic (per-row day differences, plus row count or summary statistics) against what the response states | astra4 (fail) | 1 | active | 2/2 | 5/6 | followed | followed | followed | not followed | not followed | not followed | not followed | not followed |

### Removed (0)

None.

### Failing runs (6)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| astra4 | 0 | 0 | 0 | 2 | 3 |  | **breaks nothing** |
| luna1 | 6 | 11 | 0 | 4 | 1 | ri1 |  |
| luna2 | 3 | 5 | 0 | 1 | 1 | i23 |  |
| luna3 | 3 | 4 | 0 | 4 | 1 | i14 |  |
| luna4 | 3 | 9 | 1 | 3 | 1 | i24 |  |
| luna5 | 5 | 11 | 0 | 0 | 1 | i22 |  |

### Kept after two failed rewordings (failing-run trigger)

- i5: Extracts spreadsheet cell values row by row into text files (triggered by luna4; that run counts 0 for importance)

### Events

at_pinned 10, f1_evidence_invalid 1, only_before 26, pinning_wrong 1, proposed 1, purpose_otherwise 9, recheck_disagrees 15, reword_attempt_failed 2, reword_failed 1, reworded 6

### Role terms (F1)

- **document corpus**: the supplied folder of matter documents (word-processing, spreadsheet and email files) without a metadata index
- **text corpus**: plain-text copies of the corpus files that the agent made so it could search them
- **engagement letter**: the per-matter document that states the matter's subject, practice group and responsible partner
- **candidate deal matters**: matters provisionally identified as belonging to the practice the task asks about
- **closing records**: closing checklists, closing memos, post-closing letters/emails and closing certificates for a matter
- **definitive agreement**: the executed principal transaction agreement whose date is the signing date
- **confirmed closed deals**: candidate deals whose signing and actual closing dates are both backed by documents
- **response file**: the markdown deliverable the task asks for
- **goal tool**: the create_goal/get_goal/update_goal tools available to the agent

## Task 6: `firm-knowledge/tasks/209`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (fail), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (7)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i3 | The record collection is a set of per-entity folders of office documents (.docx/.xlsx/.eml) [tool_result]; The task asks for the oldest still-open item on a docket [task] | Globs for plain structured files (csv/json/md/txt) and for files whose names suggest a docket | 3/3 | 5/5 | luna1 ★, luna2 ★, luna3 ★, luna4 ★, luna5 |
| i13 | The opening-date index was built only from files whose names match engagement/opening patterns [reasoning] | Runs a script comparing the entities in the opening-date index with all entity folders and lists the uncovered ones | 2/3 | 2/5 | luna3, luna5 |
| i9 | A candidate's status document marks it formally closed or dormant [tool_result]; Shelved files are excluded; files in closing posture count as open [task] | Excludes that candidate and moves on to check the next-oldest candidate's status documents | 3/3 | 1/5 | luna3 |
| i11 | Files still winding down in closing posture count as open [task] | Greps the whole converted text corpus for explicit status labels (e.g. 'status: closing', 'status: active', 'matter status') | 3/3 | 1/5 | luna5 ★ |
| i16 | The leading candidate's records give an opening date [tool_result] | Reads the candidate's engagement letter to confirm its effective opening date | 3/3 | 1/5 | luna1 |
| i10 | The earliest candidates' folders contain closing-checklist .xlsx files [tool_result]; The bulk conversion did not cover .xlsx, and read cannot open office files [environment] | Converts the candidates' closing-checklist spreadsheets to text with parse-doc (or a script) and reads them | 2/3 | 1/5 | luna1 |
| i15 | An entity's closing-phase documents show it is in closing, with its opening date later than the already-excluded older entities [tool_result] | Reads that candidate's internal status/outcome report, which records its open date and its status as Closing | 2/3 | 1/5 | luna2 |

### Proposed by F1 (21)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Creates a three-step todo plan: locate opening dates and status evidence, compare eligible entities, write the deliverable | retired → ri1 | 2/3 | 0/5 | followed | same purpose, other action | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i2 | The system prompt says the workspace holds a documents folder (task documents) and an output folder [environment] | Lists the workspace, then globs the entire record collection | retired → ri2 | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | same purpose, other action | cancelled |
| i3 | The record collection is a set of per-entity folders of office documents (.docx/.xlsx/.eml) [tool_result]; The task asks for the oldest still-open item on a docket [task] | Globs for plain structured files (csv/json/md/txt) and for files whose names suggest a docket | active | 3/3 | 5/5 | followed | followed | followed | not followed ★ | not followed ★ | not followed ★ | not followed ★ | not followed |
| i4 | No plain-text or structured register file exists; docket-named files belong to individual entities [tool_result]; The read tool opens only plain text; office files need conversion [environment]; The collection holds thousands of .docx/.eml files across hundreds of entity folders [tool_result] | Starts a background Python job that converts every .docx and .eml file to text in a scratch folder, keeping the folder structure | active | 0/3 | 0/5 | only before | only before | only before | not seen | not seen | not seen | not seen | not seen |
| i5 | The background conversion job has started writing the converted text corpus [tool_result]; The task asks when the entity opened [task] | Greps the converted text corpus for opening-date phrases (e.g. 'date opened', 'matter opened', 'opened on') | active | 3/3 | 0/5 | followed | followed | followed | not seen | only before | not seen | followed | not seen |
| i6 | Corpus-wide opening-date greps return hundreds of noisy, truncated matches [tool_result]; Engagement letters and opening memos carry a date in their header lines [tool_result] | Runs a Python script that pulls the first date from the header of engagement/opening documents and writes them, sorted by date, to a scratch file | retired → ri6 | 2/3 | 0/5 | followed | only before | followed | followed | not seen | cancelled | same purpose, other action | not seen |
| i7 | The opening-date index has been written to a scratch file [tool_result] | Reads the opening-date index from the top (oldest first) | active | 3/3 | 0/5 | followed | followed | followed | followed | not seen | not seen | followed | action = pinned item |
| i8 | The earliest-dated entities by engagement header have been identified [tool_result]; An old opening date counts only if the entity is still open (not shelved, not closed) [task] | Globs the earliest candidates' folders and reads their status documents (closing memos, dormancy memos, status letters) | active | 3/3 | 0/5 | followed | followed | followed | only before | only before | only before | only before | followed |
| i9 | A candidate's status document marks it formally closed or dormant [tool_result]; Shelved files are excluded; files in closing posture count as open [task] | Excludes that candidate and moves on to check the next-oldest candidate's status documents | active | 3/3 | 1/5 | followed | followed | followed | followed | only before | not followed | followed | followed |
| i10 | The earliest candidates' folders contain closing-checklist .xlsx files [tool_result]; The bulk conversion did not cover .xlsx, and read cannot open office files [environment] | Converts the candidates' closing-checklist spreadsheets to text with parse-doc (or a script) and reads them | active | 2/3 | 1/5 | not seen | followed | followed | not followed | followed | followed | followed | followed |
| i11 | Files still winding down in closing posture count as open [task] | Greps the whole converted text corpus for explicit status labels (e.g. 'status: closing', 'status: active', 'matter status') | active | 3/3 | 1/5 | followed | followed | followed | followed | followed | followed | followed | not followed ★ |
| i12 | No central docket record turned up among the files [tool_result] | Inspects the package parts / docProps metadata of a sample .docx for administrative fields | removed (astra5) | 0/3 | 0/5 | cancelled | cancelled | not followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i13 | The opening-date index was built only from files whose names match engagement/opening patterns [reasoning] | Runs a script comparing the entities in the opening-date index with all entity folders and lists the uncovered ones | active | 2/3 | 2/5 | action = pinned item | followed | followed | not seen | not seen | not followed | pinning wrong | not followed |
| i14 | A short list of entities has no dated engagement header in the index [tool_result] | Looks at those uncovered entities' engagement/opening files directly for their opening dates | active | 3/3 | 0/5 | followed | followed | followed | only before | not seen | followed | followed | not seen |
| i15 | An entity's closing-phase documents show it is in closing, with its opening date later than the already-excluded older entities [tool_result] | Reads that candidate's internal status/outcome report, which records its open date and its status as Closing | active | 2/3 | 1/5 | followed | only before | followed | only before | not followed | only before | only before | only before |
| i16 | The leading candidate's records give an opening date [tool_result] | Reads the candidate's engagement letter to confirm its effective opening date | active | 3/3 | 1/5 | followed | followed | followed | not followed | followed | only before | only before | followed |
| i17 | The candidate's client closing letter has a section on formal closure of the matter [tool_result] | Reads the closure section of the candidate's client closing letter to confirm that formal closure still depends on outstanding items | active | 2/3 | 0/5 | followed | only before | followed | not seen | only before | not seen | not seen | not seen |
| i18 | The system prompt says to collect still-relevant background jobs with job_output [environment]; A background conversion job has been reported finished [tool_result] | Calls job_output on the finished background job to collect its result | active | 2/3 | 0/5 | followed | followed | not seen | not seen | not seen | not seen | not seen | not seen |
| i19 | The candidate's status report records status Closing and an open date, confirmed by its engagement letter [tool_result]; The older entities checked are documented as dormant or formally closed [reasoning] | Marks the comparison todo completed and the writing todo in progress | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | not seen | only before | only before |
| i20 | The task asks for a single self-contained response.md with findings, the documents relied on, and reasoning [task]; A relative write path is saved under the output folder [environment]; The verified candidate's opening date and Closing status, plus the excluded older dormant/closed entities, are known [tool_result] | Writes response.md: the answer entity and opening date first, why its closing status counts as open, a comparison of older entities excluded as dormant or closed, and the source document paths | active | 3/3 | 0/5 | followed | followed | followed | followed | action = pinned item | followed | only before | only before |
| i21 | response.md was created successfully [tool_result] | Marks all todos completed and ends with a one-line message pointing to response.md | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |

### Added by rewording (4)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri1 | i1 | Creates a three-step todo plan: locate opening dates and status evidence, compare eligible entities, write the deliverable | Creates a short todo plan that covers finding opening dates and status evidence, picking out the qualifying entity, and writing the deliverable (as separate steps or with some of them merged) | astra4 (pass) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri2 | i2 | Lists the workspace, then globs the entire record collection | Enumerates every file in the record collection (with or without first listing the workspace) before running targeted searches | luna4 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri6 | i6 | Runs a Python script that pulls the first date from the header of engagement/opening documents and writes them, sorted by date, to a scratch file | Runs a script that takes the first date from the header of each engagement/opening document and produces a list of entities sorted by that date, either saved to a file or printed | luna4 (fail) | 1 | retired → ri6.2 | 3/3 | 0/5 | followed | followed | followed | same purpose, other action | not seen | cancelled | followed | not seen |
| ri6.2 | ri6 | Runs a script that takes the first date from the header of each engagement/opening document and produces a list of entities sorted by that date, either saved to a file or printed | Runs a script that pulls an opening date for each entity out of its documents (for example a header date or a date next to explicit 'opened' wording) and writes the results as a structured per-entity list, saved to a file or printed, that can be ranked by date | luna1 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | not seen | not seen | followed | not seen |

### Removed (1)

| id | observation | action | why |
|---|---|---|---|
| i12 | No central docket record turned up among the files [tool_result] | Inspects the package parts / docProps metadata of a sample .docx for administrative fields | astra5 (pass): observation seen at s3.o2; Luna: not followed; Opus re-check: seen at s3.o2, not followed; same purpose by another action: no |

### Failing runs (5)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna1 | 3 | 6 | 0 | 3 | 0 | i3 |  |
| luna2 | 2 | 7 | 0 | 4 | 1 | i3 |  |
| luna3 | 3 | 7 | 0 | 3 | 0 | i3 |  |
| luna4 | 1 | 3 | 0 | 5 | 0 | i3 |  |
| luna5 | 3 | 6 | 0 | 3 | 1 | i11 |  |

### Events

at_pinned 3, only_before 24, pinning_wrong 1, proposed 1, purpose_otherwise 4, recheck_disagrees 7, removed 1, reworded 4

### Role terms (F1)

- **record collection**: the read-only document tree of per-entity (matter) folders given with the task
- **converted text corpus**: plain-text copies of the office documents written by the agent into a scratch folder
- **opening-date index**: a scratch file, built by script, listing each entity's earliest header date from its opening/engagement documents, sorted by date
- **candidate**: an entity (matter) being checked as a possible answer, taken in order of opening date
- **status document**: a closing memo, dormancy memo, status report or closing checklist that states an entity's current status
- **qualifying status**: the status the task counts as eligible (active or still in closing posture, not shelved/dormant and not formally closed)
- **deliverable**: the markdown answer file the task asks for

## Task 7: `firm-knowledge/tasks/240`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (fail), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (8)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i4 | The provision-keyword filename search returned a standalone agreement of the requested provision type in one matter [tool_result] | Lists that matter's folder and converts/reads the standalone agreement and the matter's engagement letter | 3/3 | 5/5 | luna1, luna2 ★, luna3 ★, luna4 ★, luna5 ★ |
| ri18 | The older precedent matter's standalone agreement is dated as of a signing date [tool_result] | Checks the older precedent matter's closing records (for example a closing index or a closing certificate's list of delivered documents) for an entry showing that agreement was executed and delivered | 3/3 | 3/5 | luna2, luna3, luna5 |
| i21 | Newer candidate matters only have drafts, target dates, or ruling/advisory work without an executed agreement with the provision [tool_result] | Includes in the deliverable a table of newer Tax candidates with the documents reviewed and why each is excluded | 1/3 | 3/5 | luna3, luna4, luna5 |
| i16 | A newer candidate matter contains an agreement file whose name marks it as a draft and which contains provision-type language [tool_result] | Reads/greps the draft agreement's header for draft legend and execution date | 3/3 | 2/5 | luna1 ★, luna4 |
| i17 | Provision searches in other newer candidate matters found no executed agreement with the provision [tool_result] | Reads status/scope documents of newer candidate matters (ruling-request, scoping or advisory engagements) | 1/3 | 2/5 | luna2, luna3 |
| i8 | The converted text corpus of engagement/admin documents is available [tool_result]; The task requires the matter to belong to a specific practice area [task] | Greps the converted engagement documents for practice-group/department markers of the named practice (and its partners) | 3/3 | 1/5 | luna5 |
| i13 | Provision-keyword hits in the leading candidate matter's summary memos mention an escrow securing the provision under the main deal agreement [tool_result] | Reads the leading candidate's closing memorandum, including its section on the escrow for the provision | 3/3 | 1/5 | luna4 |
| i22 | An older precedent matter has a standalone executed agreement of the requested provision type confirmed by its closing records [tool_result] | Mentions the older precedent matter and its standalone agreement in the deliverable as an earlier, directly executed precedent | 3/3 | 1/5 | luna1 |

### Proposed by F1 (24)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | ∅ (always) | Creates a three-step todo plan: locate records, compare candidates and dates, write the sourced answer to the deliverable | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i2 | The system prompt says task documents live under a documents directory in the workspace and deliverables go to output [environment] | Lists the workspace and globs every file under the documents directory, then lists its top-level folders | retired → ri2 | 3/3 | 0/5 | followed | followed | followed | followed | same purpose, other action | same purpose, other action | followed | cancelled |
| i3 | The task asks for a matter of a given practice area with a given provision type in an executed agreement [task]; Document filenames are descriptive and grouped by matter folder [tool_result] | Globs filenames for the task keywords (practice-area word and provision word) | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i4 | The provision-keyword filename search returned a standalone agreement of the requested provision type in one matter [tool_result] | Lists that matter's folder and converts/reads the standalone agreement and the matter's engagement letter | active | 3/3 | 5/5 | followed | followed | followed | not followed | not followed ★ | not followed ★ | not followed ★ | not followed ★ |
| i5 | Matters are identified by folder IDs found in the filename search results [tool_result] | Globs the full file listing of specific matter folders surfaced by the keyword search | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i6 | Most documents are .docx and the read tool only opens plain text; parse-doc/pandoc are available [environment]; The collection has hundreds of matters [tool_result] | Starts a background bulk pandoc conversion of administrative documents (engagement, opening, closing files) into a scratch text folder | removed (astra3) | 1/3 | 0/5 | same purpose, other action | followed | only before | cancelled | cancelled | cancelled | cancelled | cancelled |
| i7 | A runtime message reports that a background conversion job finished [environment] | Calls job_output for the finished job and checks it converted without errors | active | 1/3 | 0/5 | not seen | only before | followed | not seen | not seen | not seen | not seen | not seen |
| i8 | The converted text corpus of engagement/admin documents is available [tool_result]; The task requires the matter to belong to a specific practice area [task] | Greps the converted engagement documents for practice-group/department markers of the named practice (and its partners) | active | 3/3 | 1/5 | followed | followed | followed | not seen | not seen | followed | not seen | not followed |
| i9 | The converted text corpus is available [tool_result] | Greps the converted corpus for phrases of the requested provision type | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| i10 | The practice-area grep listed engagement letters of several possible Tax matters [tool_result] | Reads the opening part of candidate matters' engagement letters | active | 2/3 | 0/5 | followed | followed | only before | not seen | followed | followed | not seen | followed |
| i11 | A set of candidate Tax matters has been identified [reasoning]; Only admin documents of those matters were converted so far [tool_result] | Starts a background conversion of all .docx documents of the listed candidate Tax matters | active | 0/3 | 0/5 | not seen | not seen | not seen | not seen | not seen | not seen | not seen | not seen |
| i12 | The full-document conversion of the candidate Tax matters has completed [tool_result] | Greps each candidate (especially newer) Tax matter's converted folder for the provision terms | active | 3/3 | 0/5 | followed | followed | followed | followed | only before | followed | followed | followed |
| i13 | Provision-keyword hits in the leading candidate matter's summary memos mention an escrow securing the provision under the main deal agreement [tool_result] | Reads the leading candidate's closing memorandum, including its section on the escrow for the provision | active | 3/3 | 1/5 | followed | followed | followed | followed | only before | only before | not followed | not seen |
| i14 | The leading candidate's folder contains an execution-version ancillary agreement [tool_result] | Converts/greps and reads the ancillary executed agreement for its provision cross-reference and execution date | active | 2/3 | 0/5 | only before | followed | followed | not seen | not seen | followed | only before | only before |
| i15 | The leading candidate's matter summary memo is available and describes the engagement [tool_result] | Greps/reads the matter summary memo for the main deal agreement's signing date and the ancillary agreement's execution at closing | active | 2/3 | 0/5 | only before | followed | followed | only before | not seen | only before | not seen | only before |
| i16 | A newer candidate matter contains an agreement file whose name marks it as a draft and which contains provision-type language [tool_result] | Reads/greps the draft agreement's header for draft legend and execution date | active | 3/3 | 2/5 | followed | followed | followed | not followed ★ | not seen | only before | not followed | only before |
| i17 | Provision searches in other newer candidate matters found no executed agreement with the provision [tool_result] | Reads status/scope documents of newer candidate matters (ruling-request, scoping or advisory engagements) | active | 1/3 | 2/5 | followed | only before | only before | not seen | not followed | not followed | only before | only before |
| i18 | The older precedent matter's standalone agreement is dated as of a signing date [tool_result] | Reads the older precedent matter's closing index entry for that agreement | retired → ri18 | 3/3 | 3/5 | followed | followed | followed | followed | not followed | not followed | same purpose, other action | not followed |
| i19 | Before writing, the agent finishes the comparison of candidates [reasoning] | Updates the todo list marking research/comparison completed and writing in progress | active | 0/3 | 0/5 | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item |
| i20 | The leading candidate matter has closing-memo evidence and a summary-memo signing date showing the provision in a signed deal agreement [tool_result]; The signed main deal agreement itself is not in the files and the only provision markup is a draft [tool_result] | Writes the deliverable naming the leading candidate matter, linking the closing memorandum, summary memo and ancillary executed agreement as evidence, with a caveat that the draft markup is not the executed clause | active | 3/3 | 0/5 | followed | followed | followed | not seen | not seen | followed | not seen | not seen |
| i21 | Newer candidate matters only have drafts, target dates, or ruling/advisory work without an executed agreement with the provision [tool_result] | Includes in the deliverable a table of newer Tax candidates with the documents reviewed and why each is excluded | active | 1/3 | 3/5 | action = pinned item | action = pinned item | followed | not seen | not seen | not followed | not followed | not followed |
| i22 | An older precedent matter has a standalone executed agreement of the requested provision type confirmed by its closing records [tool_result] | Mentions the older precedent matter and its standalone agreement in the deliverable as an earlier, directly executed precedent | active | 3/3 | 1/5 | followed | followed | followed | not followed | not seen | not seen | followed | followed |
| i23 | The deliverable contains relative markdown links to source documents [tool_result] | Runs a script that extracts the deliverable's links and checks each target file exists | removed (astra3) | 2/3 | 0/5 | not followed | followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i24 | Link check reported no missing links [tool_result] | Marks all todos completed and ends with a brief message pointing to the deliverable | active | 2/3 | 0/5 | not seen | followed | followed | not seen | not seen | not seen | not seen | not seen |

### Added by rewording (2)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (fail) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri2 | i2 | Lists the workspace and globs every file under the documents directory, then lists its top-level folders | Runs a broad file listing that covers the documents directory (all of it, or its top-level folders) and reads the folder structure from the paths it returns | luna2 (fail) | 1 | active | 3/3 | 0/5 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri18 | i18 | Reads the older precedent matter's closing index entry for that agreement | Checks the older precedent matter's closing records (for example a closing index or a closing certificate's list of delivered documents) for an entry showing that agreement was executed and delivered | luna4 (fail) | 1 | active | 3/3 | 3/5 | followed | followed | followed | followed | not followed | not followed | followed | not followed |

### Removed (2)

| id | observation | action | why |
|---|---|---|---|
| i6 | Most documents are .docx and the read tool only opens plain text; parse-doc/pandoc are available [environment]; The collection has hundreds of matters [tool_result] | Starts a background bulk pandoc conversion of administrative documents (engagement, opening, closing files) into a scratch text folder | astra3 (pass): the purpose was achieved by another action, but both rewordings failed validation on P1/P2/astra3 |
| i23 | The deliverable contains relative markdown links to source documents [tool_result] | Runs a script that extracts the deliverable's links and checks each target file exists | astra3 (pass): observation seen at s28.c1; Luna: not followed; Opus re-check: seen at s28.c1, not followed; same purpose by another action: no |

### Failing runs (5)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna1 | 3 | 9 | 0 | 1 | 1 | i16 |  |
| luna2 | 3 | 10 | 0 | 2 | 1 | i4 |  |
| luna3 | 4 | 4 | 0 | 3 | 1 | i4 |  |
| luna4 | 4 | 7 | 0 | 2 | 1 | i4 |  |
| luna5 | 4 | 5 | 0 | 4 | 1 | i4 |  |

### Events

at_pinned 10, only_before 19, proposed 1, purpose_otherwise 4, recheck_disagrees 14, removed 1, reword_attempt_failed 2, reword_failed 1, reworded 2

### Role terms (F1)

- **task keywords**: the subject words of the question (the practice area and the provision type) used for filename/content searches
- **candidate Tax matters**: matters identified as belonging to the practice area named in the task
- **leading candidate matter**: the candidate Tax matter whose records show the provision in a signed/closed deal and that ends up as the answer
- **newer candidate matter**: a candidate Tax matter dated later than the leading candidate that must be ruled out
- **older precedent matter**: an earlier Tax matter holding a standalone executed agreement of the requested provision type
- **converted text corpus**: plain-text/markdown copies of .docx files written into a scratch folder
- **matter summary memo**: a close-out or lessons-learned memorandum that records a matter's timeline and execution events
- **closing memorandum**: a closing-date memo that records closing events such as an escrow securing the provision
- **ancillary executed agreement**: an execution-version agreement in the leading matter that cross-references the provision in the main deal agreement
- **deliverable**: the response markdown file in the output directory

## Task 8: `firm-knowledge/tasks/243`

P1 `astra1`, P2 `astra2`; other runs: astra3 (pass), astra4 (pass), astra5 (pass), luna1 (pass), luna2 (fail), luna3 (fail), luna4 (fail), luna5 (fail). Status done.

### Final active invariants with importance above 0 (3)

Active after every removal and rewording; most important first. Broken in = the failing runs where the observation was seen and the action did not follow (★ = the first invariant that run broke).

| id | observation | action | S | I | broken in |
|---|---|---|---|---|---|
| i4 | The read tool opens only plain text; office files must be converted [environment]; Most matter files are thousands of .docx documents [tool_result] | Bulk-extracts text from all .docx files with a Python script into a scratch text corpus | 2/4 | 2/4 | luna4 ★, luna5 |
| i1 | The task asks for a count and list of matters in a practice group with a specific event, written to a markdown file [task] | Creates a todo list with three phases: identify practice attribution, verify the target event, write the deliverable | 4/4 | 1/4 | luna5 ★ |
| ri10 | A matter's opening memo describes its primary practice as another area despite a practice-group partner leading it [tool_result] | Leaves the matter out of the practice group's count, and the answer gives the basis for leaving such matters out: the matter's own recorded practice classification decides membership, not the affiliation of the lawyers on it. The basis can be given for that matter by name or as a general attribution rule. | 4/4 | 1/4 | luna2 ★ |

### Proposed by F1 (28)

| id | observation | action | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (pass) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i1 | The task asks for a count and list of matters in a practice group with a specific event, written to a markdown file [task] | Creates a todo list with three phases: identify practice attribution, verify the target event, write the deliverable | active | 4/4 | 1/4 | followed | followed | followed | followed | followed | followed | followed | not followed ★ |
| i2 | ∅ (always) | Lists the workspace and globs the whole documents directory | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i3 | Matter files include plain-text email files [tool_result]; The task names the practice group and the target event [task] | Globs filenames containing the event keyword and greps the raw email files for the practice-group name | retired → ri3 | 4/4 | 0/4 | followed | followed | followed | followed | cancelled | same purpose, other action | cancelled | cancelled |
| i4 | The read tool opens only plain text; office files must be converted [environment]; Most matter files are thousands of .docx documents [tool_result] | Bulk-extracts text from all .docx files with a Python script into a scratch text corpus | active | 2/4 | 2/4 | followed | only before | only before | followed | followed | followed | not followed ★ | not followed |
| i5 | The first conversion left spreadsheets and presentations unconverted [tool_result] | Converts the remaining spreadsheet and presentation files to text and greps them for the practice-group name | removed (astra3) | 2/4 | 0/4 | not followed | followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i6 | A scratch text corpus of the matter files exists [tool_result] | Greps the scratch text corpus for the practice-group name | active | 3/4 | 0/4 | followed | followed | followed | only before | followed | followed | followed | followed |
| i7 | The practice-name grep returned hundreds of matches and was truncated [tool_result] | Re-greps with patterns targeting practice-group field labels or line-start occurrences of the name | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | only before | not seen |
| i8 | Practice-name greps over the whole corpus remain truncated [tool_result] | Splits the practice-name grep by matter-number ranges via include globs | removed (astra4) | 2/4 | 0/4 | followed | not followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i9 | Grep hits show the practice-group name in matter summary/opening/intake documents [tool_result] | Reads matter summary, opening and status documents of matters with such hits | active | 3/4 | 0/4 | followed | followed | followed | only before | followed | followed | followed | not seen |
| i10 | A matter's opening memo describes its primary practice as another area despite a practice-group partner leading it [tool_result] | Excludes that matter from the practice group's count and records why | retired → ri10 | 3/4 | 0/4 | same purpose, other action | followed | followed | followed | cancelled | cancelled | cancelled | cancelled |
| i11 | A matter's administrative record classifies it in the practice group although its responsible partner belongs to another practice [tool_result] | Includes that matter as attributed to the practice group | active | 3/4 | 0/4 | followed | followed | followed | not seen | followed | followed | followed | not seen |
| i12 | A candidate matter has no classification field [tool_result] | Reads the matter's engagement letter and correspondence signatures to establish practice attribution | active | 3/4 | 0/4 | followed | only before | followed | followed | only before | followed | followed | not seen |
| i13 | The documents use two variants of the practice-group name [tool_result] | Treats both name variants as the same practice group | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i14 | A set of candidate matters attributed to the practice group is identified [reasoning] | Greps the target-event terms scoped to the candidate matters' folders | retired → ri14 | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | same purpose, other action |
| i15 | Event-term grep hits in candidate matters point to hold notices, reminders, status reports and government letters [tool_result] | Reads the hold notices and confirming documents for each candidate matter | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | only before | followed |
| i16 | A candidate matter's hold notice is marked DRAFT with an undated issuance placeholder [tool_result]; No other document confirms issuance for that matter [tool_result] | Excludes the matter for lacking an issued hold and lists it as an exclusion | active | 2/4 | 0/4 | followed | followed | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item |
| i17 | A candidate matter is attributed to the practice group [reasoning]; Event-term search of that matter found no issued hold [tool_result] | Excludes the matter for lack of documented issuance and notes it in the report | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i18 | A matter's later document records the hold as issued, distributed, acknowledged or completed [tool_result] | Counts the matter as qualifying, citing the issuance evidence | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i19 | Some qualifying matters have several hold notices or reminders [tool_result] | Counts distinct matters once regardless of number of notices | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i20 | Some qualifying matters are dormant or closed [tool_result]; The task asks which matters involved the event [task] | Keeps dormant and closed matters in the count | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i21 | Documents within one qualifying matter give differing issuance dates [tool_result] | Notes the date inconsistency in the report while keeping the matter included | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | not seen | followed | followed |
| i22 | A matter's documents use an internal reference number different from its folder identifier [tool_result] | Reports the matter under the folder identifier and mentions the internal reference | removed (astra4) | 2/4 | 0/4 | followed | not followed | followed | cancelled | cancelled | cancelled | cancelled | cancelled |
| i23 | Attribution and issuance checks for all candidate matters are done [reasoning] | Marks the verification phase complete in the todo list | active | 2/4 | 0/4 | followed | action = pinned item | action = pinned item | followed | action = pinned item | action = pinned item | action = pinned item | pinning wrong |
| i24 | The qualifying and excluded matters with supporting documents are determined [reasoning]; The deliverable must be a self-contained markdown file with findings, documents relied on and reasoning [task] | Writes the deliverable with the count, a table of matters with issuance evidence, counting rules, documents relied on and exclusions | active | 0/4 | 0/4 | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item | action = pinned item |
| i25 | The deliverable has been written [tool_result] | Reads back the deliverable | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| i26 | The deliverable cites specific sections of source documents [reasoning] | Re-checks cited source passages or section headings in the source documents | active | 2/4 | 0/4 | only before | followed | followed | only before | not seen | only before | only before | only before |
| i27 | The read-back deliverable gives document paths whose base directory is ambiguous [tool_result] | Edits the deliverable to clarify which directory the cited paths are relative to | removed (luna1) | 1/4 | 0/4 | followed | not seen | not seen | not followed | cancelled | cancelled | cancelled | cancelled |
| i28 | The deliverable is written and checked [reasoning] | Marks all todos complete and replies with a short summary giving the count and a link to the file | retired → ri28 | 3/4 | 0/4 | followed | followed | followed | same purpose, other action | cancelled | cancelled | cancelled | cancelled |

### Added by rewording (4)

The observation is the original's; the action was reworded at the purpose level after a run achieved the purpose with another action, and validated on P1/P2 (and the run, if it passed).

| id | replaces | old action | new action | from run | attempt | final status | S | I | astra3 (pass) | astra4 (pass) | astra5 (pass) | luna1 (pass) | luna2 (fail) | luna3 (fail) | luna4 (fail) | luna5 (fail) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ri10 | i10 | Excludes that matter from the practice group's count and records why | Leaves the matter out of the practice group's count, and the answer gives the basis for leaving such matters out: the matter's own recorded practice classification decides membership, not the affiliation of the lawyers on it. The basis can be given for that matter by name or as a general attribution rule. | astra3 (pass) | 2 | active | 4/4 | 1/4 | followed | followed | followed | followed | not followed ★ | followed | followed | not seen |
| ri28 | i28 | Marks all todos complete and replies with a short summary giving the count and a link to the file | Marks all todos complete and replies with a brief closing message that points the user to the written deliverable file (key findings such as the count are optional) | luna1 (pass) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri3 | i3 | Globs filenames containing the event keyword and greps the raw email files for the practice-group name | Runs a quick keyword pass before reading documents closely: matches filenames against the event keyword and searches document text (raw emails, or text pulled from a filtered subset of documents) for the practice-group name | luna3 (fail) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |
| ri14 | i14 | Greps the target-event terms scoped to the candidate matters' folders | Searches within each candidate matter's own folder for documents tied to the target event, either by matching the event terms in file contents or by listing the folder and picking out files whose names point to the event | luna5 (fail) | 1 | active | 4/4 | 0/4 | followed | followed | followed | followed | followed | followed | followed | followed |

### Removed (4)

| id | observation | action | why |
|---|---|---|---|
| i5 | The first conversion left spreadsheets and presentations unconverted [tool_result] | Converts the remaining spreadsheet and presentation files to text and greps them for the practice-group name | astra3 (pass): observation seen at s8.c1; Luna: not followed; Opus re-check: seen at s8.c1, not followed; same purpose by another action: no |
| i8 | Practice-name greps over the whole corpus remain truncated [tool_result] | Splits the practice-name grep by matter-number ranges via include globs | astra4 (pass): observation seen at s25.o1; Luna: not followed; Opus re-check: seen at s25.o1, not followed; same purpose by another action: no |
| i22 | A matter's documents use an internal reference number different from its folder identifier [tool_result] | Reports the matter under the folder identifier and mentions the internal reference | astra4 (pass): observation seen at s34.o4; Luna: not followed; Opus re-check: seen at s34.o4, not followed; same purpose by another action: no |
| i27 | The read-back deliverable gives document paths whose base directory is ambiguous [tool_result] | Edits the deliverable to clarify which directory the cited paths are relative to | luna1 (pass): observation seen at s43.o1; Luna: not followed; Opus re-check: seen at s43.o1, not followed; same purpose by another action: no |

### Failing runs (4)

Per failing run, over the active invariants: broken (seen, not followed: an importance point), not seen, same purpose by another action, only before, action = pinned item (the observation's evidence is the action itself). A run that breaks nothing failed for a reason these invariants don't capture (a missing invariant, a content or reasoning error, or the grader).

| run | broken | not seen | same purpose, other action | only before | action = pinned item | first broken | |
|---|---|---|---|---|---|---|---|
| luna2 | 1 | 1 | 0 | 1 | 3 | ri10 |  |
| luna3 | 0 | 1 | 0 | 1 | 3 |  | **breaks nothing** |
| luna4 | 1 | 0 | 0 | 3 | 3 | i4 |  |
| luna5 | 2 | 5 | 0 | 1 | 2 | i1 |  |

### Events

at_pinned 19, only_before 13, pinning_wrong 1, proposed 1, purpose_otherwise 4, recheck_disagrees 5, removed 4, reword_attempt_failed 1, reworded 4

### Role terms (F1)

- **the practice group**: the firm practice group named in the task whose matters must be counted
- **the target event**: the discovery event the task asks about (an issued litigation hold)
- **matter files**: the per-matter document folders in the read-only documents directory
- **scratch text corpus**: plain-text copies of the office documents the agent extracted into a scratch directory
- **candidate matters**: matters provisionally attributed to the practice group
- **classification field**: an explicit administrative practice-group label in a matter summary, intake, opening or status document
- **issuance evidence**: a document stating a hold was issued, distributed, acknowledged or implemented
- **deliverable**: the markdown report file the task asks for

## Cost

| kind | role | model | status | jobs | model requests | tokens in | tokens out | seconds |
|---|---|---|---|---|---|---|---|---|
| f1_propose | f1_propose | claude-opus-5-5 | error | 1 | 19 | 1,768,800 | 6,153 | 128 |
| f1_propose | f1_propose | claude-opus-5-5 | ok | 8 | 132 | 12,177,254 | 111,628 | 1403 |
| f1_reword | f1_reword | claude-opus-5-5 | ok | 53 | 171 | 1,378,777 | 31,384 | 652 |
| f2_seen | f2_recheck | claude-opus-5-5 | ok | 300 | 1900 | 32,744,917 | 406,951 | 7939 |
| f2_seen | f2_seen | gpt-5.6-luna | error | 1 | 7 | 80,923 | 2,292 | 26 |
| f2_seen | f2_seen | gpt-5.6-luna | ok | 1922 | 16606 | 501,437,147 | 5,997,007 | 69555 |
| f3_followed | f3_followed | gpt-5.6-luna | ok | 1780 | 9649 | 154,459,798 | 2,878,576 | 33578 |
| f3_followed | f3_recheck | claude-opus-5-5 | ok | 227 | 1167 | 14,490,153 | 185,324 | 4055 |
| too_narrow | too_narrow | claude-opus-5-5 | ok | 181 | 852 | 10,774,407 | 145,043 | 2998 |
