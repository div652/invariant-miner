# Why failing runs earn few importance points: a grounded look

Question (user, 2026-11-18, QNA turns 73 and 75): on the mixed:flip tasks, with 10 runs each, failing runs gain very few
importance points. What did the failing runs actually do wrong, and why did our invariants not catch it: a missing
invariant (1), a model reasoning error (2, note H5), or something else?

Scope: a few relevant tasks, not every run. Harvey (mixed:flip, runs 1-10, run `im-mixed-flip-r6-10-20261118T043837Z`):
DPA review, TSA markup, repo-securities redline. APEX-Agents (third:flip, run `im-apex-third-flip14-20261118T075246Z`):
world227-tg-07 and world131-dv-03.

Sources: the grader's per-criterion verdicts with the judge's reasoning (Harvey: `grading.json` / `scores.json`; APEX:
`grading.json`), the deliverables (Harvey: the .docx files in `output/`, read with [docx_text.py](docx_text.py), which
shows tracked deletions as `[-…-]` and insertions as `{+…+}`; APEX: `answer.json`), the trajectories' reasoning
summaries, and our runs' cells and jobs. **The grader's verdicts are read only for this diagnosis; the invariant method
never uses them.** Quotes are verbatim (cut with "…").

## One-line summaries

- **DPA review (Harvey)** -> 6 failing runs of 10 (runs 3, 4, 6, 8, 9, 10; 4 passed); 5 of them break no invariant and
  see every observation. Five fail C-043/C-044 "mentions subprocessor Larkfield Data Systems / Orionis Analytics by
  name", which the judge applies inconsistently (passing runs 1, 2, 7 never write "Orionis Analytics" and pass C-044;
  failing runs 3, 4, 8, 9 do the same and fail it). Runs 3, 8, 9 fail only on these; run 4 also misses the
  anonymization issue, run 6 the HIPAA Breach Notification Rule, run 10 the summary table at the top.
- **TSA markup (Harvey)** -> 3 failing runs of 10 (runs 2, 3, 10; 7 passed); all three miss C-039 "Net 30 days": their
  clause says "within thirty (30) days after the date of receipt" / "within 30 days after receipt", the passing runs
  "after the invoice date" / "Net 30 from the invoice date", a different trigger. Run 3 also applies the APA's 10% cap
  instead of the playbook's cost-plus-15% (3 more criteria), a deliberate choice; run 10 also misses that two renewals
  reach 30 months. The invariants these runs broke (get_goal bookkeeping in run 2, "fixes the generation script" in run
  10) have nothing to do with the failures.
- **Repo-securities redline (Harvey)** -> 7 failing runs of 10 (3 passed); runs 2, 8, 9 break no invariant. Run 9 fails
  only C-007 (substitution must not cause a Margin Deficit), whose verdict is inconsistent (passing runs 4 and 10 have
  the same wording); run 8 also leaves 1.5% in a summary table whose annex has the agreed 1.75%; run 2 misses details in
  the issues list.
- **world227-tg-07 (APEX)** -> 3 failing runs of 10 (runs 3, 4, 7; 7 passed), single criterion "equity value $7,728M".
  Runs 3 and 7 answer $6,391.7M (FY30 EBITDA used as the NTM figure, and the special dividends put into the model's
  dividend row, which takes them out of the cash that repays debt); run 4 answers $7,254.7M (the debt error, right
  EBITDA). F1 **had** proposed both decisive
  invariants; one (i9, "special dividends do not reduce debt paydown") was removed by a passing run that did it without
  saying so, and the other (i7, "takes the following year's EBITDA") was judged "followed" because F3 trusted the run's
  "FY31" label on a FY30 number.
- **world131-dv-03 (APEX)** -> 4 failing runs of 10 (runs 1, 3, 4, 9; 6 passed), single criterion "NPV €15.33B": all
  four answer €15.31B because they took the business case's "€1.74875 billion/year" instead of its "~€1.75
  billion/year" (both are in the document; the deck's overview slide says €1.75B). The only relevant invariant ("takes
  the renewable-enablement figure, not the total") is satisfied by both choices.

## Patterns across these tasks

| Why a failing run breaks no invariant | Where seen |
|---|---|
| **The grader is inconsistent**: the same wording passes in one run and fails in another | DPA C-043/C-044 (runs 3, 8, 9 fail only on it), repo-securities C-007 (run 9 fails only on it) |
| **A content error in the deliverable** (H5): same process, one figure, word or condition off | TSA "after receipt" vs "invoice date" (all 3 failing runs); repo run 8 1.5% vs 1.75%; DPA runs 4 and 6 (an issue left out); APEX world227 FY30 vs FY31 EBITDA |
| **A deliberate judgement the reference does not share** | TSA run 3 (APA cap over playbook); APEX world131 (€1.74875B over €1.75B) |
| **The invariant existed but our checks lost it** (caution C1) | APEX world227: i9 removed although the passing run did it silently; i7 judged "followed" on a mislabelled number |
| **The invariant is too coarse** (missing granularity) | APEX world131 i11; TSA (no invariant about the payment trigger); DPA (none about naming parties in full) |

Answer to the question: both of your reasons occur, and two more do. Content errors (2, H5) are the most common real
cause. Missing invariants (1) appear as invariants that are too coarse for the decisive detail. Then there are failures
that are partly or wholly the grader's (inconsistent verdicts), and failures our own checks hid (a decisive invariant
removed, a wrong "followed").

## Harvey: DPA review (`intellectual-property/review-data-processing-agreement-template-against-eu-and-us-requirements`)

| run | verdict | failed criteria | our invariants on this run |
|---|---|---|---|
| 1, 2, 5, 7 | pass 47/47 | | (passing) |
| 3 | fail 46/47 | C-044 Orionis by name | breaks nothing, sees every observation |
| 4 | fail 44/47 | C-028, C-047 anonymization; C-044 Orionis | breaks nothing |
| 6 | fail 45/47 | C-007 HIPAA breach notification; C-043 Larkfield | breaks nothing |
| 8 | fail 45/47 | C-043 Larkfield; C-044 Orionis | breaks nothing |
| 9 | fail 45/47 | C-043; C-044 | breaks nothing |
| 10 | fail 45/47 | C-001 summary table; C-043 | breaks ri19 ("renders the docx to PDF and inspects it"), unrelated |

**C-043 / C-044, "mentions subprocessor … by name".** How often each memo writes the full name and the short name, and
the verdicts:

| run | result | "Larkfield Data Systems" / "Larkfield" | "Orionis Analytics" / "Orionis" | C-043 | C-044 |
|---|---|---|---|---|---|
| 1 | pass | 1 / 24 | 0 / 10 | pass | pass |
| 2 | pass | 0 / 19 | 0 / 12 | pass | pass |
| 3 | fail | 0 / 22 | 0 / 13 | pass | **fail** |
| 4 | fail | 0 / 25 | 0 / 7 | pass | **fail** |
| 5 | pass | 1 / 29 | 1 / 16 | pass | pass |
| 6 | fail | 0 / 20 | 0 / 16 | **fail** | pass |
| 7 | pass | 1 / 34 | 0 / 16 | pass | pass |
| 8 | fail | 0 / 25 | 0 / 10 | **fail** | **fail** |
| 9 | fail | 0 / 26 | 0 / 10 | **fail** | **fail** |
| 10 | fail | 0 / 28 | 0 / 15 | **fail** | pass |

The verdict does not follow the text. Run 8, failed: *"The memo mentions "Orionis" several times, including as an
analytics subprocessor, but never identifies it by the required name, "Orionis Analytics" or "Orionis Analytics Ltd.""*
Run 7, passed, also never writing "Orionis Analytics": *"The memorandum mentions Orionis by name multiple times,
including identifying it as an Irish subprocessor and discussing its analytics and anonymization role."* Run 8's memo
does name it, e.g. *"Flow these restrictions to Larkfield and Orionis as applicable."*

**Run 4, C-028 / C-047 (anonymization vs pseudonymization for Orionis): a real content gap.** Judge: *"The memo briefly
states that pseudonymization does not remove GDPR coverage, but it does not flag that the DPA fails to define or
distinguish anonymization from pseudonymization specifically for Orionis Analytics …"*. Run 4's only mention is about the
disaster-recovery transfer; passing run 1 states the issue as such: *"“Anonymization” is undefined; pseudonymized data
remains personal data."*

**Run 6, C-007 (HIPAA Breach Notification Rule): a real content gap.** Judge: *"The memo addresses processor-to-Pinnacle
incident notice and generally calls for HIPAA breach support, but it does not identify the missing separate HIPAA Breach
Notification Rule obligations, such as notices to affected individuals, HHS (including the 500+ threshold), or the
media."* Run 6 discusses the 48-hour vs 24-hour notice (*"48-hour breach notice after confirmation rather than 24 hours
after discovery"*); passing run 7 adds *"cooperation with HHS/supervisory authority/California notices"*.

**Run 10, C-001 (prioritized summary table at the beginning):** *"The memo has an early executive-summary table … but it
does not provide a near-beginning summary table or structured list that assigns risk levels to the identified gaps. The
P0/P1/P2 ratings appear only later"*: a format slip.

**Observations.** The failing runs follow the passing runs' process step for step (no invariant broken, no observation
missed). Had the judge accepted the short names every time, as it did in runs 1, 2 and 7, runs 3, 8 and 9 would pass and
DPA would be 7/10 rather than 4/10 (had it rejected them every time, runs 1, 2 and 7 would fail too). No invariant asks for parties to be named in full, and none could be learnt reliably from passing runs that
themselves mostly use the short names.

## Harvey: TSA markup (`corporate-ma/draft-markup-of-transition-services-agreement-tsa`)

| run | verdict | failed criteria | our invariants on this run |
|---|---|---|---|
| 1, 4-9 | pass 56/56 | | |
| 2 | fail 55/56 | C-039 Net 30 | breaks i18 (get_goal → update_goal), unrelated |
| 3 | fail 52/56 | C-035, C-037 cost-plus-15%; C-039 Net 30; C-051 fee escalation | breaks nothing |
| 10 | fail 54/56 | C-010 renewals beyond 18 months; C-039 Net 30 | breaks i14 ("fixes the defect in the generation script and reruns it"), unrelated |

**C-039, "Redlines payment terms to Net 30 days": the same drafting slip in all three failing runs.**

- Run 2 (fail), Section 6.3: *"Service Recipient shall pay each invoice within thirty (30) days after the date of
  receipt."* Judge: *"…payment within 30 days after receipt, not Net 30 days from the invoice date as required by the
  criterion."*
- Run 3 (fail): *"[ADD — Polaris proposal] Buyer shall pay each undisputed invoice within 30 days after receipt. …"*, while
  its own comment says *"Replace vague timing with Net 30, interest and suspension / termination protection. Authority:
  Playbook §4.3"*.
- Run 10 (fail), judge: *"The redline specifies payment within 30 days after receipt of the invoice, not Net 30 days from
  the invoice date as required by the criterion. Those triggers can produce different payment deadlines."*
- Run 4 (pass): *"Invoices are payable Net 30 from the invoice date. …"* Run 1 (pass), judge: *"…payment of each undisputed
  invoice within thirty (30) days after the invoice date, expressly implementing Net 30 terms."*

Every run, passing or failing, writes "Net 30" somewhere in its work; the failing runs' clause ties the 30 days to the
wrong event.

**Run 3, C-035 / C-037 / C-051: a deliberate judgement against the playbook.** Its comment: *"The APA’s 10% cap controls any
extension even though the playbook target is cost-plus-15%. Authority: APA §7.12(a)"*; reasoning (s8.r3): *"According to
APA 7.12(b), fees should be cost-plus with a maximum 10% markup."* Judge (C-037): *"…omits the required cost-plus-15%
pricing. Instead, it limits change-order pricing to the APA’s 10% markup cap."* The run resolved a conflict between the
governing agreement and the client playbook the other way from the reference.

**Run 10, C-010:** *"…it never identifies that two automatic six-month renewals could extend the TSA to 30 months. It also
proposes allowing a six-month extension beyond 18 months, inconsistent with the criterion’s stated absolute 18-month APA
cap."*

**Observations.** All three failures are inside the deliverable's legal text; none is a process difference. F1's
invariants for this task are about process and analysis (reading, comparing fee tables, computing the liability cap,
formatting the redline); none states the payment trigger, so nothing could be broken. This is the "missing invariant by
granularity" case: an invariant at the level of "uses the playbook's exact term (Net 30 from the invoice date)" would
have caught all three failing runs.

## Harvey: repo-securities redline (`contracts/banking/repo-securities-lending-subsequent-turn-redline/scenario-01`)

Runs 4, 5, 10 pass; runs 1, 3, 6, 7 break invariants (mostly i14 "inserts w:trackRevisions into settings.xml" and i23
"converts the redline to PDF"); runs 2, 8, 9 break nothing.

**C-007, "Substitution right — no Margin Deficit condition as clean text": the verdict follows neither wording nor
meaning.**

- Run 9 (fail, its only failed criterion): *"No substitution may be effected while a Margin Deficit exists in respect of
  any Transaction under this Agreement."* Judge: *"…it does not state that the substitution itself must not cause or
  create a Margin Deficit. These are not equivalent conditions."*
- Run 8 (fail): *"No substitution may be effected while a Margin Deficit exists."*
- Run 10 (pass): *"…may be transferred only if no Margin Deficit exists at the time of substitution."* Judge: pass.
- Run 4 (pass), judge: *"…include, as clean text, the condition that no substitution may occur while a Margin Deficit
  exists."*

None of the four says the substitution must not itself create a deficit; two pass, two fail.

**Run 8, C-001 (sovereign haircut 1.75% as clean text): a real consistency error.** Its paragraph 4.11 summary table
says *"Eligible Sovereign Securities 1.5% (the "Sovereign Haircut")"*, while its Annex II has the agreed 1.75%; run 10's
4.11 says 1.75%. The judge also notes for C-042: *"Paragraph 4.11 shows 1.5%/3.5%, while Annex II shows the agreed
1.75%/4.25%."*

**Run 2, C-038 / C-048 (issues list):** *"…the issues list does not record the required resolved substitution terms (one
Business Day notice, same-or-better collateral, and no Margin Deficit), even though those terms appear in the agreement
itself"*; *"The repricing row states “walk-away if deleted,” but does not specify the required constraint that Buyer
walks away if there is no repricing right for term trades exceeding 60 days."* Missing detail in a second deliverable.

**Observations.** Here the process invariants did catch the runs that went wrong in process (tracked changes not
switched on, no rendering check: runs 1, 3, 6, 7). The runs that broke nothing failed on details in the text, one of
them (run 9) only because of an inconsistent verdict.

## APEX: world227-tg-07 (equity value at end FY30)

Task (prompt.txt): *"MFC is valued at 12x EV / NTM EBITDA. Please calculate the company's equity value at end FY30 … re-finance
its debt at an additional 75bps spread … reduce restricted cash by $100M each year, starting in Jan FY27, with funds
returned to shareholders as special dividends."* Single criterion: *"States that the company's equity value at end FY30
is $7,728 million"*.

| run | answer (equity value) | NTM EBITDA | FY30 debt | restricted cash |
|---|---|---|---|---|
| 1, 2, 5, 6, 8, 9, 10 (pass) | $7,727.96M | $771.88M | $2,134.58M | $600M |
| 3, 7 (fail) | $6,391.7M | $749.4M | $3,201.1M | $600M |
| 4 (fail) | $7,254.7M | $771.9M | $2,607.8M | $600M |

**What went wrong.**

- **NTM EBITDA (runs 3, 7).** At end FY30 the NTM figure is FY31's ($771.9M). Runs 3 and 7 report *"FY31 NTM EBITDA:
  $749.4 million"*, which is FY30's EBITDA; passing run 1 looked at both (s13.r: *"I’ve identified that FY30 EBITDA is
  749,396.887 …"*) and used FY31.
- **Special dividends and debt (runs 3, 4, 7).** Released restricted cash pays the dividends, so the cash that repays debt
  is unchanged. Run 4 (s9.r): *"a cash reduction of $100 million each year goes back to shareholders as dividends, which
  means I need to subtract that from the cash flow available for debt repayment"*; run 7 (s8.r) puts −100,000 in the
  model's dividend row; run 3 (s19.r2): *"the task is primarily about updating row 53"*. Passing run 1 (s13.r2): *"if
  dividends are paid from restricted cash, they shouldn't reduce operating cash"*.

**What our invariants did.** F1 proposed both decisive invariants:

- **i9**: *[In the model, debt paydown comes from cash flow and restricted cash is tracked separately with interest income on
  it] -> "Concludes the special dividends do not reduce debt paydown, only the interest income on restricted cash"*. It
  was **removed** by passing run 10. F3 (Luna) and the Opus re-check said "not followed" (run 10 reached the right debt,
  $2,134.58M, without ever stating the conclusion in its reasoning summaries), and the too-narrow check said "no" for
  run 10, although for passing run 5, with the same correct debt, it said "yes" (*"FY30 debt: **C$2,134.581 million**"*).
  Run 10's trigger came first, so i9 was removed and, with passing-first, its cells on the failing runs were cancelled:
  the invariant that would have earned importance in runs 3, 4 and 7 was never checked there.
- **i7**: *"Takes the following year's EBITDA as the NTM metric and multiplies it by the given multiple to get EV"*. Judged
  **followed** on runs 3 and 7: F3's quote is run 3's *"- FY31 NTM EBITDA: **$749.4 million**"*. F3 took the run's
  label at face value; the number is FY30's.

**Observations.** This task's failures are content errors (2, H5), but the low importance is our checks' doing (caution
C1), not a missing invariant: an action worded as a conclusion in the reasoning ("Concludes …") can be done silently, so
a passing run "breaks" it, and a check that reads labels does not verify numbers. Wording the action by its observable
result ("keeps the debt balance unaffected by the special dividends") and an inconsistent too-narrow verdict are the two
things to fix.

## APEX: world131-dv-03 (12-year NPV)

Task: *"The steady-state annual benefits from renewable enablement mentioned in the business case represent the annual
renewables revenue for year 1, which then grows at a rate of 10% … Assume an 8% annual discount rate, and no discount in
the 1st year. State the final NPV in billions with two decimal places"*. Single criterion: *"States that the NPV is €15.33
billion"*.

| run | answer | year-1 revenue used |
|---|---|---|
| 2, 5, 6, 7, 8, 10 (pass) | €15.33B | €1.75B |
| 1, 3, 4, 9 (fail) | €15.31B | €1.74875B |

**What went wrong.** The business case states the figure twice. Run 3's read of it (s12.o1): *"Annual total benefits of
~€1.86 billion (steady-state), composed of: … ~€1.75 billion/year from renewable enablement"*, and (s12.o2): *"Across all
countries, the Annual Renewable Benefit totals approximately €1.74875 billion/year."* The deck's overview slide (passing run
2, s19.o2): *"€1.75B/year — renewable enablement"*. The failing runs chose the more precise figure (run 3, s13.r: *"I'm
considering the annual renewable benefit of 1.74875 billion per year"*), the passing runs the headline one (run 2, s20.r:
*"the renewable enablement brings in $1.75 billion in steady-state annual benefits"*). Same formula, same OPEX; the €0.02B
difference is the choice of input.

**What our invariants did.** i11: *[The business case slides list a steady-state annual benefit for renewable enablement]
-> "Takes that renewable-enablement figure (not the total benefit) as the base benefit value"*: followed by all four
failing runs, because both figures are renewable-enablement figures. Too coarse to separate them.

**Observations.** A judgement between two stated values, arguably a reference-answer choice. Passing run 2 took
its figure from the slide; I did not check whether the other passing runs saw and set aside the €1.74875B figure. An invariant could only catch it at the level of "uses the headline
figure the task's wording points to (the business case's stated steady-state benefit) rather than a more precise figure
from the body", which is fine-grained and partly task-specific.

## APEX: the "mark all todos completed" invariants (user question, 2026-11-19)

Four tasks have an active invariant of this form with importance above 0 (apex-third-flip14-report.md): world226-td-02
i21 (*"All planned steps are done and verified" -> "Marks all todo items completed"*, I 1/6), anti-SLAPP i6 (I 5/8),
128-jr-1 i9 (I 3/7), world131-dv-03 i14 (I 1/4). Question: can marking todos complete separate passing from failing runs?

**The rubric cannot see todos.** Every criterion is a statement about the answer (anti-SLAPP C1: *"States that Chapter
27's motion-to-dismiss procedure applies only to a 'legal action.'"*; 128-jr-1 C1-C6: the five scores and the
recommendation). The judge gets the final answer and the world's files; the todo list lives only in the DSH session
(tool-todo is a session projection). DSH does not react to todo states either: no reminder, no finish gate; the tool
returns *"Updated todo list: N pending, N in progress, N completed."* and nothing else.

**What the 10 importance points are.** Last `todo_write` of each failing run that "broke" the invariant:

| Task, run | Last todo_write | Verdict right? |
|---|---|---|
| world226-td-02 run7 | s29 (of 30): all 4 `completed` | **No**: same call as passing run 6 (s29, all completed), judged followed there |
| anti-SLAPP run8 | s8 (of 9): all 3 `completed` | **No** |
| anti-SLAPP run9 | s7: all 3 `completed` | **No** |
| 128-jr-1 run10 | s6 (of 7): all 3 `completed` | **No** |
| world131-dv-03 run1 | s15 (of 16): all 3 `completed` | **No**: run 3 made the same call (s15), judged followed |
| anti-SLAPP run4, run5 | none: no todo list at all (4-step runs) | Vacuous: there was nothing to mark |
| 128-jr-1 run1, run3 | none: no todo list at all | Vacuous |
| anti-SLAPP run10 | s8: `completed, completed, in_progress` | Yes, the one real case |

Why the check errs: the observation (*"all steps are done"*) has no evidence apart from the action, so F2 pins it at
the `todo_write` call itself (s29.c1) or at its output (s33.o1). F3 must then say whether the action comes *after* that
location; for the call itself Luna answered "followed" in some runs and "not followed" in others, for its output
"only before". The too-narrow check (Opus) said no each time and did not catch it.

**Correlation, not cause.** Runs that marked everything complete fail just as often: anti-SLAPP runs 1, 6, 7, 8 and 9 did,
and failed; 128-jr-1 runs 5, 6, 8, 9 and 10 did, and failed. The failures are content: every failing anti-SLAPP run
misses C1 (does not say the procedure applies *only* to a "legal action"), with or without todos; the failing 128-jr-1
runs compute wrong scores. The only pattern left: the four runs that never made a todo list all failed (anti-SLAPP 4, 5
are also the shortest, 4 steps against 7-9), but most runs of these tasks fail anyway (8/10 and 7/10), and those four
failed on the same criteria as the runs with a list. At most a weak sign of a hastier run; no causal effect on the grade.

**For the method.** (1) An observation must have evidence before and apart from the action (F2 may not pin it at the
action's own call or output). (2) An action on an object that does not exist (no todo list) should make the observation
"not seen", not a violation. (3) Bookkeeping actions (todo updates, progress notes) could be excluded from F1's
proposals, or proposed only with a separate observation.

## What this suggests for the method (not built; to discuss)

1. **Grader noise.** Some failing labels are not failures (DPA runs 3, 8, 9; repo run 9). Importance 0 there is correct;
   counting on importance alone would mislead. A cross-check of the judge (same wording, different verdicts) would flag
   such runs.
2. **Actions as observable results, not reasoning conclusions.** i9 ("Concludes …") was removed because a passing run did
   the right thing without saying so. F1 could be told to word an action by what can be seen in calls, outputs or the
   answer (the debt balance, the clause text), with "concludes" only when nothing else shows it.
3. **Checks that verify values.** i7 was judged followed on a mislabelled number. For numeric actions, F3 could be asked to
   check the value against the source, not the run's label.
4. **Deliverable-level invariants.** TSA, DPA and world131 fail on details of the final text or input choice. A finer F1
   pass on the deliverable ("which exact terms, figures, names did both passing runs use?") is what the targeted
   re-proposal (DESIGN.md section 9) would produce; the grader's failed criteria would point it there.
5. **The too-narrow check's consistency.** It said "no" for run 10 and "yes" for run 5 on the same outcome; worth a look
   before it decides removals.
6. **Self-evidenced observations.** The todo invariants above earn importance only through check errors: their
   observation is pinned at the action itself. F2 should need evidence before and apart from the action; an action on
   something absent (no todo list) should count as not seen.
