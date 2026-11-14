# Retrieval methods across the 32 flipping train tasks (96 runs)

Question asked (2026-11-13): for the same task, some search strategies retrieve all the right documents and others do
not. Are there methods that always work and methods that fail? Ground it in evidence and numbers.

**Method.** Every tool call of the 96 trajectories (32 tasks x 3 base runs; 5,718 calls) was classified by search
method. The gold matters of each task come from its rubric, from every criterion except precision: 104 gold matters
in 30 tasks; 082 (answer: none) and 210 (a client count) are left out of the matter counts. That gives 312
(task, run, gold matter) items. For each item: the first call before the answer was written whose output, as the
model saw it, names the matter, and that call's method; whether the run then opened one of the matter's files; and
whether the matter's criterion passed. A scan that wrote its hits to a file is credited when the agent reads that
file. Capped listings and case-sensitive patterns were re-run against the real document store (9,288 files) to see
what they hid. Scripts: [retrieval-scripts/](retrieval-scripts/).

## 1. Where gold matters were lost

| Stage | Items | Share |
|---|---|---|
| Included (criterion passed) | 278 | 89% |
| Opened, but not included (judgement, or only partly read) | 8 | 3% |
| **Surfaced in a search output, never opened** | **16** | 5% |
| **Never surfaced before the answer** | **10** | 3% |

Finding is rarely the problem: 302 of 312 items (97%) appeared in some search output, and in 13 of the 16
surfaced-but-unopened misses the gold matter appeared in the run's **first** searches (steps 3-5). Retrieval breaks
in two places: a matter the run saw but never opened, and a matter its instruments could not show it.

## 2. Method scorecard

In the runs that used each method (before the answer): the share of the task's gold matters that appeared in that
method's own output.

| Method | Calls | Runs | Gold in its output | Failure signature |
|---|---|---|---|---|
| File-name search (glob with words) | 1,043 | 93 | **276/299 (92%)** | 148 capped at 100 paths; 61 returned nothing only because of letter case |
| Full-text scan of the whole corpus (bash, extracted .docx text) | 92 | 36 | 107/141 (76%) | 12 timed out at 60 s; 19 capped; hits only as good as the search words |
| Text scan of name-selected files (bash) | 30 | 15 | 58/73 (79%) | 4 timed out |
| Text scan of a hand-listed set of matters | 171 | 69 | 128/257 (50%) | covers only the matters listed |
| grep tool over the raw corpus | 158 | 35 | 48/94 (51%) | reads raw bytes: blind inside .docx/.xlsx/.pptx |
| Folder listing of a matter or client prefix | 927 | 86 | 174/272 (64%) | lists only what was already chosen |
| Generic listing (`*`, `**/*`) | 105 | 96 | 11/312 (4%) | 98 of 105 capped at 100 of 9,288 |

- **How to read "gold in its output"** (it is per gold matter, not per call): of the gold matters of the runs that
  used the method, the share that appeared in the output of at least one call of it in that run. For file-name
  search: 276 of 299 gold matters (92%) appeared in some name search of their run. Per call it is much lower: 455 of
  1,021 name searches (45%) named any gold matter. Per run: in 70 of 87 runs (80%) the name searches together named
  every gold matter of the task.
- **grep is structurally blind.** On gold matters that have an .eml or .txt file it found 44/71 (62%); on gold
  matters that are only Office files, 4/23 (17%, those 4 through mentions in other matters' emails). 35 of the 104
  gold matters have no plain-text file at all, so grep can never see them.
- **File names carry most of the signal** in this corpus (files are named for their content). Only 3 of 104 gold
  matters were never hit by any file-name search in any run: 153's 1042-00004 (earn-out only inside a merger
  agreement), 185's 1038-00003 and 216's 1009-00003. These are found only by full-text scans or folder enumeration,
  and they have the lowest recall: 1, 2 and 1 runs of 3.

## 3. Strategy and recall per run

| Run class (before the answer) | Runs | Gold included | Runs with every gold matter |
|---|---|---|---|
| A. Completed a whole-corpus full-text scan | 30 | 122/126 (97%) | 26/30 (87%) |
| B. Attempted one, every attempt timed out | 4 | 13/15 (87%) | 3/4 |
| C. Text scan of name-selected files only | 4 | 20/21 (95%) | 3/4 |
| D. No corpus-wide content scan (names, grep, chosen files) | 52 | 123/150 (82%) | 33/52 (63%) |

Within the same task (33 pairs where one run included more gold matters than another), the higher-recall run had a
completed full-text scan and the lower-recall run did not in **11** pairs; the reverse in **2**. Opening more
matters is not the difference (higher-recall run opened more in 18 pairs, fewer in 14; median 11 vs 10 matters).

A gold matter that appeared in a **content** hit (scan or grep) was included 205/214 times (96%); one that appeared
only in **file-name** listings, 73/87 (84%); never surfaced, 0/10.

**Selective opening is universal.** For gold items that first surfaced in a file-name list, the run opened a median
of 50% of the matters in that list, whether the gold matter was then included (n=255) or never opened (n=13). Which
half gets opened decides the item: a name hit is a coin the run may or may not pick up.

The trade-off: full scans do not cost precision overall. Precision failed in 11/31 class-A runs (35%) against 16/53
class-D runs (30%); all-pass was 17/32 (53%) against 25/55 (45%).

## 4. Instrument failures, measured on the corpus

- **Capped listings** ("Showing 100 of N"): re-running the 142 capped name-search globs on the store, a gold matter
  sat in the unshown part 206 times (130 distinct items). The run saw it elsewhere in 127 of the 130; the cap alone
  caused 3 misses: 153 run 1, 185 run 1, 208 run 2 (1033-00004).
- **Letter case:** the store's file names are lower case; 234 name-search globs had capital letters, 61 of them
  returned nothing only because of case. Direct misses: 229 runs 1 and 2 (`*SNDA*`; the files are `snda-…`), 200
  run 2 (`*Vantor*`).
- **Timeouts:** whole-corpus scans (126 calls in 41 runs) timed out 16 times at bash's 60 s default; 10 of the 15
  runs that hit one completed a later scan. 038 run 3 did not (it scanned a hand-picked list instead) and lost 2 of 7.
- **Capped scan output not paged:** 25 scan outputs were capped. 133 run 3's capped scan output contained the gold
  matter, never acted on; 051 run 2's capped "best efforts / commercially reasonable efforts" scan hid it.
- **Vocabulary:** a content scan finds the words, not the concept. 051's gold matter (an at-the-market offering)
  never says "best efforts" (0 of 12 files); it says "commercially reasonable efforts" (4 files) and "sales agent"
  (6). Run 2's completed best-efforts scans could not find it; run 3 found it by the file name `*equity*` and read it.

## 5. The 34 misses by cause

| Cause | Items | Where |
|---|---|---|
| Never surfaced: letter-case file-name pattern | 3 | 229 r1, 229 r2, 200 r2 |
| Never surfaced: capped listing, nothing else showed it | 3 | 153 r1, 185 r1, 208 r2 (1033-00004) |
| Never surfaced: grep blind to .docx + file-name words that do not occur in its names | 2 | 083 r3, 085 r3 (1007-00003) |
| Never surfaced: content-only matter, scan output too large or capped | 2 | 104 r1, 051 r2 |
| Surfaced, never opened: long or capped name list, run opened another part | 10 | 044 r1, 085 r2, 104 r2, 133 r2, 133 r3, 153 r3, 208 r2 (x3), 216 r1 (1009-00003) |
| Surfaced, never opened: stopped early on a superlative ("first") | 2 | 162 r2, 162 r3 |
| Surfaced, never opened: full scan timed out, hand-picked list replaced it | 2 | 038 r3 (x2) |
| Surfaced, never opened: run stopped after a partial look | 2 | 216 r3 (x2) |
| Opened, not included: judgement or partial reading | 8 | 051 r1, 139 r1, 139 r3 (x2), 167 r1, 208 r2 (x2), 216 r1 (1010-00002) |

## 6. Answer: what works, what fails

**No single method always works.** Even the best one, a completed whole-corpus full-text scan, missed 4 of 126
items, each time for an identifiable reason (output capped, words that the documents do not use, or the scan aimed
at another criterion). What separates the runs that got everything is not one tool but whether the candidate set was
**complete and fully read**:

What reliably works (no failures in the data when done completely):
1. **A full-text scan of the extracted text of every document, that completes and whose hits are read in full**
   (paged past any cap, or summarised by matter). 97% gold recall; the within-task winner in 11 of 13 decided pairs.
2. **Enumerating the unit, then checking each item:** every file of the document type in which the fact is recorded
   (038 run 1: every underwriting / purchase agreement / offering memorandum, each checked; 7/7), or every folder
   of the client or the corpus (185 runs 2-3: all ten Cascade matters dated; 210 run 2: all 266 matter folders
   counted).
3. **Case-insensitive file-name search with several words for the concept**, followed by opening **every** matter it
   returns, not a selection. File names alone reach 92% of gold; the losses come from not opening what they show.

What fails, and how often:
1. **Opening a selection of a name-search list** (16 misses; the single largest cause): median 50% of a list opened,
   with no rule for which half.
2. **grep over the raw corpus**: 51% of gold, 17% on Office-only matters; 35 of 104 gold matters are invisible to it.
   "No matches" from it says nothing about .docx.
3. **Case-sensitive patterns**: 61 empty results caused only by case; 3 direct misses.
4. **Capped outputs taken as the whole** (listings at 100, scans and reads cut): 3 direct misses plus 133 r3 and
   051 r2; in 038 r3 the tool even said "use offset=199 to continue".
5. **Scans at the 60 s default**: 16 timeouts; a run that replaces the scan with a hand-picked list loses recall
   (038 r3).
6. **Exact-phrase content search for a concept** (051): the documents describe it in other words.

In short: retrieval is reliable when the candidate set is generated **completely** (every document's text, or every
item of the right unit) and every candidate is **checked**; it fails when the run samples a list, trusts an instrument
that cannot see (raw grep, case, caps, timeouts), or searches for a phrase instead of the thing.

Caveats: method classes come from heuristics over the commands; gold is matter-level (proof-document criteria are
not scored separately); 96 runs, so within-task comparisons rest on 33 pairs.

## 7. How the agent chooses a search strategy

Question asked (2026-11-14): how does the model decide between file-name search, a full-text scan, a scan of
name-selected files, and the other strategies? Grounded in the reasoning summaries (present on 1,271 of 2,916 steps,
44%) and the order of tool calls in the 96 runs.

**The default path is the same in every run.** Step 2 is always a generic listing (`glob *`: "Showing 100 of 9288",
96/96 runs). The first real search is a file-name glob in 93 of 96 runs. What follows, by the order in which
discovery methods first appear before the answer:

| Order | Runs |
|---|---|
| names, then reading named matters one by one (parse-doc) | 23 |
| names, full-text scan, then reading named matters | 10 |
| names, grep, then reading named matters | 10 |
| names only | 9 |
| names, then full-text scan | 6 |
| other orders | 38 |

Reading named matters one by one appears in 69 runs, a full-text scan of the whole corpus in 36, raw grep in 35, a
scan of name-selected files in 15. These counts overlap (a run counts under every method it used, in any order); the table puts
each run in one row by its exact sequence (rows sum to 96). So the 69 are the table's 23 + 10 + 10 plus 26 in "other
orders", and the 36 full-text-scan runs are 10 + 6 plus 20 in "other orders".

**Why names first: the size of the corpus, and the harness's own tool guidance.** The reasoning at the first name
search cites the 9,288 files in 56 of 93 runs and grep's blindness to .docx in 26:
- 133 run 3, step 3: "I'm looking at 9288 files … I wonder if searching content with grep is the best way,
  considering it likely handles mainly plain text. I might have issues with binary files like docx … I should check
  filenames for terms like 'purchase'."
- 185 run 1, step 4: "Using grep might be a good approach for text extraction, but it won't work on binary files like
  docx due to compression. I could explore using filenames … a glob pattern like '*Cascade*'."

The system prompt points the same way: "Use the glob tool — not shell find — to discover files", "Use the grep tool —
not shell grep or rg — to search file contents", and for .docx "convert them to text with bash: parse-doc". So the
prompt's path is glob for discovery, grep for content, parse-doc per file, and that is the path most runs take: name
search, then parse-doc on the matters the names point to. 47 runs question in their reasoning whether a Python or
shell search is even allowed (210 run 3, step 11: "Python's os.walk, but that feels prohibited"; 028 run 3, step 18:
"The developer suggests using the grep tool instead of shell commands for this content search. I can use Python to
extract text from the docx files"). It does not change how often they scan in the end (36% of those runs vs 39%).

**Why a full-text scan: instrument trouble, not missing results.** In the 3 steps up to the first whole-corpus scan
(36 runs) the reasoning gives: grep or plain-text tools cannot read .docx (28 runs), a capped output or an unreadable
saved list (22), a wish for completeness (17), an earlier search that came back empty (1). The name searches had not
failed: by then they had already named 119 of the 141 gold matters (84%), and only 19% of them had come back empty,
against 25% in the runs that never scanned. Examples:
- 185 run 3, step 4: "using grep on docx files isn't feasible since it can't search binary files. I might need to
  parse the documents into text" (it then dated all ten Cascade matters and passed).
- 231 run 3, step 14: "I need to not only check the tax opinion files but scan through all related documents for
  'should-level' conclusions … I'll perform a full extraction" (completeness).

**The choice is not set by the task.** Of the 32 tasks, 3 got a full-text scan in all three runs, 9 in none, and 20
in one or two. The same question, with the same documents, gets different strategies from run to run.

**What makes escalation more likely, and less.** Share of runs that went on to a whole-corpus scan:

| Before the scan (or the answer) | With | Without |
|---|---|---|
| The reasoning notes that grep / plain-text tools cannot read .docx | 27/63 (43%) | 9/33 (27%) |
| A name search came back capped ("Showing 100 of N") | 28/68 (41%) | 8/28 (29%) |
| A saved full result (spill file) could not be read | 17/48 (35%) | 19/48 (40%) |
| Raw grep returned "No matches" | **6/24 (25%)** | 30/72 (42%) |

The signals are weak, and the last one runs the wrong way: a grep "No matches", which says nothing about .docx, makes
a scan *less* likely. The agent reads it as an answer (absence), not as a blind instrument (as in 200 run 2). And 63
runs state that grep cannot read .docx, yet 36 of them never run a content scan: they rely on names and parse-doc.

**Why a scan of name-selected files: cost.** It is chosen to make a scan cheaper, by reading only files whose names
match: 038 run 3, step 38: "I want to ensure a thorough search … but I need to balance thoroughness with time limits";
210 run 3's script: "Read only filenames containing engagement; avoid scanning large XML for irrelevant docs". It
inherits the blind spot of names.

**After a scan times out** (bash's default is 60 s; 15 runs hit it), 7 runs re-ran a whole-corpus scan that completed
(104 r1, 137 r1, 167 r3, 192 r2, 192 r3, 216 r2, 233 r1). 8 did not before answering:
- five went on from partial output, name searches or picked matters (028 r1, 048 r2, 133 r1, 137 r3, 231 r3);
- two ran a name-filtered scan in the background (051 r1, 210 r3);
- one switched to a hand-picked subset (038 r3).

028 run 1, just after its timeout: "I'm uncertain whether I should retry the same expensive operation. However, I
could use the existing temporary file". 104 run 1: "I'm running into a timeout issue, and it seems I need a more
efficient method".

**In short:** the agent picks its strategy by cost and by the friction of its tools, not by what the question needs.
Names first because the corpus is large and the prompt says glob; a scan when grep proves blind, a list comes back
capped, or it wants to be thorough; narrower scans when time feels short. It never checks whether its candidate set
is complete, and it escalates no more often after its name searches miss than after they succeed. So for the same
task the strategy, and with it the recall, is partly a coin toss: section 3's 11-to-2 within-task pairs.
