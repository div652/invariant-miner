# Analysis: the 14 flipping AHE-train tasks (Luna high, base harness, three runs)

Traces: [README.md](README.md). One section per task, added as each task is read: first a one-line summary of the
failure (pattern: which criteria failed in how many runs, how many runs passed; why the criterion was lost; what each
run did with the item at the heart of it), then the in-depth analysis. Every task that lost a precision criterion ends with a **Precision check**: was
it wrong to surface the wrongly included matters, or were they misread after surfacing; was surfacing them the more
thorough search; and did the passing run(s) not surface them, surface but not read them, or read and reject them.

## How often tasks pass across the three runs

All-pass counts over the three base-harness Luna-high runs (main's three-run baseline, benchmarks/harvey/RESULTS.md):

| Passed in | AHE train (80 tasks) | All 250 FK tasks |
|---|---|---|
| 0 of 3 runs | 52 | 168 |
| exactly 1 of 3 | 8 | 28 |
| exactly 2 of 3 | 6 | 20 |
| all 3 | 14 | 34 |
| **varying (1 or 2)** | **14** (the tasks in this file) | 48 |

AHE train tasks passing exactly once: 048, 066, 072, 082, 104, 137, 162, 210. Passing exactly twice: 028, 167, 185, 192,
198, 200.

## One-line summaries

- **028** -> Failed 1 precision criterion in 1 run (run 1); 2 runs passed. Precision lost because 1007-00002 was
  included: the model found DIP text and could not understand that it was not relevant (the firm was the stalking-horse
  buyer, not debtor, DIP lender or creditor). In 1 run (run 2) the matter did not surface; in another (run 3) it
  surfaced but was not opened; in run 1 it was opened but misjudged.
- **048** -> Failed 1 precision criterion in 2 runs (runs 1, 2); 1 run passed. Precision lost because 1009-00001
  (Skybridge Fintech, $60M convertible-note bridge) was included: the model found a real general-corporate-purposes
  earmark and a completed closing but never checked that it was a Capital Markets deal (it is an Emerging Companies &
  Venture Capital matter). In 2 runs (1, 2) it was opened but misjudged; in run 3 it surfaced but was not opened.
- **072** -> Failed 1 precision criterion in 2 runs (runs 2, 3); 1 run passed. Precision lost because 10-11 extra
  matters were counted (14 and 13, against 3): a full-text scan found "informed consent" / "IRB" in deal diligence,
  disclosure schedules, an IPO and a licence, and the model could not tell that a mention in a deal file is not the
  firm's own clinical-trial work. In runs 2 and 3 they were opened but misjudged; in the passing run (run 1) they never
  became candidates (it searched file names and engagement letters, not document text): none was explicitly rejected.
- **082** -> Failed its single criterion ("no qualifying matter") in 2 runs (runs 2, 3); 1 run passed. Lost because
  1014-00004 (Optiwave v. Lumicore) was named as a matter where the firm "actually litigated an injunction": all three
  runs read the same files (preliminary-injunction motion "DRAFT — CONTINGENCY — ON HOLD", unsigned proposed
  permanent-injunction order, internal injunction analysis) and saw nothing was filed or argued; runs 2 and 3 gave a
  strict and a broad reading and led with the broad one. In run 1 it was read and explicitly rejected; in runs 2 and 3
  it was read but misjudged.
- **137** -> Failed 1 precision criterion in 2 runs (runs 1, 2), and in run 2 also 1 proof-document criterion; 1 run
  passed. Precision lost because Northgate / Ridgeline (files under 1022-00002, labelled 1018-00009) was included: the
  model read letters that "reserve the right to seek specific performance" and could not tell that reserving a right is
  not actually invoking it. In runs 1 and 2 it was opened but misjudged; in run 3 it surfaced (file listing) but was not
  opened. Run 2 also never opened the 1018-00008 status memo the proof criterion asks for.
- **167** -> Failed 1 recall criterion (qualifying matter 1038-00009, NovaMart / Cascade, $1.2B, Delaware law) in 1 run
  (run 1); 2 runs passed. Lost because run 1 never saw the deal's price: its grep for price terms across 30 parsed
  agreements was capped ("Found 250 of 369 matches"), 1038-00009's "$1,200,000,000" was in the omitted part, and the
  full result was saved to a host temp file the agent could not open. In run 1 the matter was surfaced and its
  agreement parsed (Delaware law seen) but its price was never read, so it was dropped without a decision; runs 2 and 3
  read each candidate agreement on its own and included it.
- **192** -> Failed 1 precision criterion in 1 run (run 2); 2 runs passed. Precision lost because 1039-00004's
  Offer-to-Purchase Agreement (a tender offer followed by a short-form merger) was added to the pull set: the model found
  "Company Material Adverse Effect" in it and, although it noted the document is a tender-offer agreement and not a
  merger agreement, still listed it as a "related merger instrument". In 2 runs (1, 3) it surfaced (a
  certificate-of-merger file name) but was not opened; in run 2 it was opened, recognised, and included anyway.
- **198** -> Failed 1 precision criterion in 1 run (run 1); 2 runs passed. Precision lost because 1043-00001 (Ironhaven
  Data Centers, a $950M Term Loan B) was included as a deal over $1B on a "$1.9 billion merger consideration" its credit
  agreement never states: the figure is VeloPay's (1003-00003). Run 1's own reasoning had found Ironhaven a $950M
  financing with no merger, but the written answer attached VeloPay's number to it. In run 1 it was opened, assessed
  correctly, then misreported in the answer; run 2 opened it and explicitly rejected it (sub-billion); run 3 opened it
  and listed it only as a "supplemental" comparator, not a qualifying deal.
- **200** -> Failed 1 recall criterion (qualifying matter 1038-00007, *Vantor Holdings v. Cascade Retail*, the firm
  defending Cascade) in 1 run (run 2); 2 runs passed. Lost because run 2's searches could not see it: grep reads raw
  bytes, so "Vantor" never matched inside the matter's 35 .docx files (its 253 hits all came from other matters' .eml
  files, capped at 250, with the full list in a file it could not open); its file-name search `*Vantor*` was
  case-sensitive while the files are named `…-vantor-…`; and a grep of all .docx for "Vantor Holdings Corp" returned
  "No matches found", which it took as absence. In run 2 the matter never surfaced; runs 1 and 3 found it with a
  lowercase `*vantor*` file-name search, opened its engagement letter and conflict memo, and included it.
- **066** -> Failed 1 proof-document criterion in 2 runs (run 1: the subscription agreement; run 3: the key-terms
  memo); 1 run passed. Every run found the right fund (Pellegrino co-invest vehicle, 1027-00002) but cited only 6 of its
  12 files, each a different six. Run 1 never opened the subscription agreement and mentioned it only inside its
  opinion-letter summary; run 2 wrote the same sentence and was graded pass, so run 1's flip is grader noise. Run 3
  opened the key-terms memo (step 7) but left it out of its document list (read but not delivered).
- **104** -> Failed all 3 criteria (qualifying matter, proof document, precision) in 2 runs (runs 1, 2); 1 run passed.
  Lost because the wrong matter was named as the latest Labor & Employment matter with agreed acceleration terms. Run 1
  chose the Northgate CEO negotiation (1022-00004): acceleration only "agreed in principle", negotiations terminated, no
  executed agreement, as its own answer says. Run 2 chose NovaMart (1038-00009): an M&A deal whose acceleration sits in
  draft employment agreements attached to the SPA. The right matter, 1017-00004 (executed Aldrich settlement, January
  2024, § 3(a)), did not surface in run 1 and surfaced but was not opened in run 2. Run 3 found it through a content
  search that hit the matter's emails, read the executed agreement, and explicitly rejected 1022-00004.
- **162** -> Failed all 4 criteria in 2 runs (runs 2, 3); 1 run passed. Lost because Arbor Health (1010-00002, IPO
  closed February 2024) was named as the firm's first traditional IPO. Solstice Biomedical (1037-00001, ADS IPO closed
  March 2023) is earlier, but its folder has no S-1 or prospectus, so the prospectus / registration file searches
  missed it, and both runs stopped at Arbor without dating every candidate (run 2 even assumed a low matter number
  meant an early deal). In runs 2 and 3 Solstice surfaced (`engagement-letter-solstice-ipo.docx`) but was not opened.
  Run 1 also thought Arbor first, kept checking for earlier deals, noted that matter numbers are not chronological,
  read Solstice's closing papers, and explicitly rejected Arbor as later.
- **185** -> Failed all 4 criteria in 1 run (run 1); 2 runs passed. Lost because run 1 named the FTC defence
  (1038-00001, opened June 2025) as Cascade's most recent matter instead of the S-3 shelf registration (1038-00003,
  opened 6 April 2026). Its candidate list came from a grep for "Cascade Retail Holdings", which reads raw bytes and
  found only the 5 Cascade matters with .eml / text files; 1038-00003's 12 files are all .docx / .xlsx. The two
  listings that could have caught it failed silently: an `Engagement*` glob capped at 100 of 637, and `1038-*/*`
  returning "No files found". In run 1 the matter never surfaced; runs 2 and 3 enumerated or text-extracted all ten
  Cascade matters, dated each, and chose it (run 3: "rather than simply the highest matter number").
- **210** -> Failed 11 of 15 criteria in run 1 and 12 in run 3; 1 run passed (run 2, 15/15). Lost because the matter
  counts per client were built from incomplete data. The true top is Lumos, Quorum and Cascade at 10 each, then
  Dunmore, Aurelius and Penterra at 9. Run 1 tallied engagement letters only for client series 1001-1030 (the matters
  run to 1046, so Cascade, 1038, was never counted) and split Quorum into two entities ("Quorum vs QIH"). Run 3's full
  extraction timed out at 60 s; it restarted it in the background, then answered from partial results and killed the
  job before it finished. Run 2 counted all 266 matter folders by client series and confirmed each series' client in
  its engagement letters.


## Patterns across tasks (updated as tasks are added)

Tasks so far: 028, 048, 072, 082, 137, 167, 192, 198, 200, 066, 104, 162, 185, 210.

- **How the passing runs avoided the wrong item.**
  - Never surfaced it or never read it (pass by omission): 028 (runs 2, 3), 048 (run 3), 072 (run 1), 137 (run 3), 192 (runs 1, 3).
  - Read it and explicitly rejected it: 082 (run 1), 198 (run 2; run 3 read it and kept it out of the qualifying set), 104 (run 3), 162 (run 1).
  - In most tasks, then, the pass is luck in what was searched or opened, not a recorded decision.
- **The failing run often searched more thoroughly** (028, 072, 192). The exceptions are 104 (the passing run added a content search) and 162 (the passing run kept looking for an earlier deal after it had a plausible answer). Full-text scans surface items that file-name searches never see, and the extra candidates then have to be judged. More recall without a decision step turns into lost precision.
- **What went wrong after surfacing:**
  - a mention taken for the firm's involvement (028 DIP as background, 072 IRB in deal diligence);
  - a scope condition of the question never checked (048 "Capital Markets", 072 the firm's own clinical-trial work, 104 "Labor & Employment");
  - a strict qualifier read loosely ("actually litigated" 082, "actually invoked" 137, "agreed" 104);
  - a hedged inclusion, where the run knew the item did not fit and named it anyway (082, 192);
  - a correct assessment or a read document lost while writing the answer (198; 066 run 3);
  - a superlative ("first", "latest", "most recent") decided without dating every candidate, with matter numbers taken as chronology (162; 104; 185);
  - a count built over an incomplete range or with one client split into two names (210).
- **Tool limits caused the losses that were not judgement:**
  - 167: a capped grep output, whose saved full result the base harness cannot open;
  - 137 run 3: the grep tool sees nothing inside .docx files (blind instrument);
  - 200 run 2: all three at once (blind grep, capped output it could not open, case-sensitive `*Vantor*` file-name search), and "No matches found" in .docx read as absence.
  - 185 run 1: blind grep, a capped listing, and a glob that lists files only, all silent, in one step;
  - 210: a range assumed from a capped listing (run 1, series 1001-1030 only); a timed-out scan whose background rerun was killed before it finished (run 3).
  - The recall and counting failures (167, 200, 185, 210) all come from tool limits, not judgement.
- **The grader is inconsistent:**
  - on caveated listings: 198's "supplemental" listing passed, 192's "related" listing failed;
  - on wording: in 066, the same sentence about the subscription agreement was graded fail in run 1 and pass in run 2. That flip is pure grading noise.
- **Proof-document criteria punish curated lists** (066): each run cited 6 of the matter's 12 files; listing them all would have passed.

## 028: DIP financing precedent bank

Question asked (2026-11-12): in 028 run 1 it fails because of precision: it saw matter 1007-00002 and included it,
while the others didn't even see it. What is wrong in including it? Why did it not surface for the others? Was the very
act of surfacing it wrong, or was it wrong not to be able to reject it?

Answer (verbatim):

Surfacing 1007-00002 was right. The mistake was keeping it after correctly identifying what it was. And the two runs that pass did not reason their way past it: one never saw it, the other saw it and never looked.

**Why including it is wrong**
- **The question defines "in any capacity":** "whether we acted for the debtor, for the DIP lender, or as a creditor responding to a DIP." In 1007-00002 the firm acted for none of these. It represented **Vantage Mobility, the stalking-horse buyer** in a § 363 sale out of Meridian Precision's Chapter 11.
- **The DIP was background, not firm work.** It appears only as one scope item in the engagement letter ("review and analyse the debtor's DIP financing orders") and as a schedule line in the asset purchase agreement ($15M DIP, about $9.8M drawn). The firm drafted no DIP motion, order, credit agreement or objection.
- **The purpose rules it out too.** For a DIP financing precedent bank there is nothing to bank. The grader's permitted set is the five matters with real DIP work.
- **Run 1 saw this itself.** It labelled the matter "buyer-side involvement rather than debtor- or lender-side representation", then decided anyway to "include this matter in a broad precedent bank". It got the facts right and resolved the ambiguity the wrong way. In your catalog's terms, that is a surface match taken as meeting the criteria: a matter that mentions a DIP is not a matter where the firm acted on a DIP.

**Why the other runs didn't include it**

| Run | How it searched | What happened to 1007-00002 |
|---|---|---|
| 1 | Full-text scan of every .docx for DIP terms, then opened each candidate's engagement letter and key documents | Surfaced at step 12, opened (engagement letter and asset purchase agreement), misjudged and included → **fail** |
| 2 | File names only: `*DIP*`, `*dip*`, `*financ*`, `*bankrupt*`, … | **Never surfaced.** The five qualifying matters all have DIP in their file names (e.g. `DIP Financing/motion-dip-financing.docx`); 1007-00002 mentions the DIP only inside its documents → pass |
| 3 | File names, then a full-text scan (step 18) | **Surfaced but never opened.** It was among the ~69 hit files at step 19, but run 3 chose other "edge" matters to check and never returned to it → pass |

**So, to your questions:**
- **Was surfacing it wrong?** No. A full-text scan is the right recall step, and the matter really does mention a DIP. Run 1 had the most thorough process of the three.
- **Was not rejecting it the error?** Yes. That is the only thing that went wrong in run 1.
- **Run 2 passed by luck:** its name-only search happened to match this task's answer set. On a task where a qualifying matter has no DIP in its file names, the same method would miss it.
- **Run 3's exclusion was also luck:** a candidate it surfaced and never opened, with no decision recorded.

The flip on this task is a judgement call under ambiguity, not retrieval. This is the case your ledger's "define" step is built for: write the question's enumerated capacities into the criteria (firm acted for the debtor, the DIP lender, or a creditor responding to a DIP). 1007-00002 then fails that criterion explicitly, instead of being included or dropped by accident.

**Precision check (1007-00002)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. Surfacing was right: the matter does mention a DIP. Run 1 opened the engagement letter and the asset purchase agreement, identified the buyer role correctly, and still included it.
- **Was surfacing it more thorough?** Yes. Run 1 scanned every document's text and opened each candidate, the most thorough of the three runs.
- **What the passing runs did:** run 2 did not surface it (file names only); run 3 surfaced it (full-text scan, step 19) but did not read it. Neither read and rejected it.

## 048: use-of-proceeds precedent review

Question asked (2026-11-12): in 048 precision is lost in 2 runs; in both, 1009-00001 is opened and included; in the
other run it surfaces but is not opened, hence not included. Same analysis as 028.

Answer:

The question asks for **"our Capital Markets deals"** whose proceeds were earmarked primarily for general corporate purposes (GCP). 1009-00001 passes the GCP test and fails the scope test. Runs 1 and 2 only checked the GCP test.

**Why including it is wrong**
- **It is not a Capital Markets deal.** It is a **$60M private convertible-note bridge** sold to VC funds ahead of a planned Series D. The intake form gives its practice group as "**Emerging Companies & Venture Capital (ECVC)**", and the deal memos come from that group. "Capital Markets" appears once in its documents, against 165 and 285 times in the two qualifying matters (1045-00001, 1014-00001).
- **The GCP earmark itself is real.** Note purchase agreement § 2.4 and the officer's use-of-proceeds certificate both say general corporate purposes, and the closing is fully documented. On the criteria the model had in mind, it looks like a perfect match.

**What each run did with 1009-00001**

| Run | Surfaced | Opened | Decision |
|---|---|---|---|
| 1 | Step 4, file-name search `*Note*` | Steps 23-25: note purchase agreement, use-of-proceeds certificate, closing documents. Never the engagement letter or intake form | Included → **fail** |
| 2 | Step 4, file-name search `*proceeds*`, which hit its use-of-proceeds certificate | Steps 34-35: certificate, term sheet, funds flow, closing binder. Never the intake form | Included → **fail** |
| 3 | Step 3, in a file-name listing | Never; it never mentioned it again | Not included → pass |

**Difference from 028:** in 028 run 1 read the disqualifying fact (buyer, not a DIP party) and misjudged it. Here runs 1 and 2 never read the disqualifying fact. They verified the two conditions they were tracking (GCP earmark, closing) but not the third the question states (a Capital Markets matter), so they never opened the document that answers it. Run 3 again passed by omission, not by a recorded decision. A ledger criterion copied from the question, "the matter is a Capital Markets deal", would have sent the agent to each candidate's engagement letter or intake form.

**Precision check (1009-00001)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. It is a real completed offering with a genuine GCP earmark, so it belongs among the candidates. Runs 1 and 2 opened its GCP and closing documents but never checked the Capital Markets scope.
- **Was surfacing it more thorough?** No. All three runs surfaced it the same way, through file-name searches (`*Note*`, `*proceeds*`, a listing). Runs 1 and 2 went further by opening it, but not far enough to check the scope condition.
- **What the passing run did:** run 3 surfaced it (file listing, step 3) but did not read it. It was not rejected.

## 072: informed consent / IRB matters for a life-sciences pitch

Question asked (2026-11-12): 072 also has precision failures in 2 runs. In the passing run, were the wrong matters not
surfaced, or were they surfaced and then rejected?

Answer:

Run 1 neither found nor rejected them. It never searched document text for "informed consent" or "IRB", so the extra matters never became candidates.

**What the question wants:** "our clinical-trial experience with numbers: how many of our Healthcare & Life Sciences matters have involved informed consent or an IRB". The permitted set is the 3 matters where that was the firm's own work: 1018-00004 (CLARION master clinical trial agreement, IRB reliance), 1029-00001 (Cadence-3 clinical trial agreement) and 1037-00002 (LUMINA-US study: IRB strategy, consent templates).

**Why runs 2 and 3 failed:** they scanned every .docx for "informed consent|IRB|institutional review board" and counted 14 and 13 matters. The extras are acquisitions (1001-00007, 1018-00003, 1018-00008, 1037-00006), financings (1004-00001 seed round, 1013-00002 notes), an IPO (1037-00001), a de-SPAC (1046-00001), a licence (1018-00006), regulatory and reimbursement work (1018-00005, 1013-00004) and litigation (1013-00005). In these, a target's or issuer's IRB approvals or consent forms appear in diligence, disclosure schedules or risk factors. The runs even wrote their own test ("substantive work product addressed consent or IRB") and applied it to mentions. As in 028, a mention in the file was taken for the firm's involvement.

**What run 1 did with the 14 extra matters**

| | Matters |
|---|---|
| Appeared only as file names in its listings (`*consent*`, `*clinical*` searches) | 9 (1001-00007, 1004-00001, 1013-00002, 1013-00004, 1013-00005, 1018-00003, 1018-00008, 1025-00006, 1043-00002) |
| Opened | 1013-00004 (engagement letter only); 1018-00008 got a folder listing |
| Never appeared | 5 (1018-00005, 1018-00006, 1037-00001, 1037-00006, 1046-00001) |
| Explicitly rejected (in reasoning or the answer) | none |

Run 1 searched file names (`*informed*`, `*consent*`, `*IRB*`, `*clinical*`, `*trial*`, `*protocol*`) and read all engagement letters. That only finds matters where consent or IRB is the subject of the work, which matched this task's answer set. Its narrow method acted as the filter, as run 2's file-name search did in 028. Had a qualifying matter kept its IRB work inside generically named files, run 1 would have missed it, and runs 2 and 3 would have found it. The fix is not to search less but to decide each text hit against a criterion like "the firm did clinical-trial / research-subject work (consent, IRB) in this matter", and to record the reason when a hit is set aside.

**Precision check (the 10-11 extra matters)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. The matters really do contain IRB / informed-consent text. Runs 2 and 3 opened the hit documents and counted mentions in deal files as the firm's own work.
- **Was surfacing them more thorough?** Yes. Runs 2 and 3 scanned every document's text; run 1 searched only file names and engagement letters.
- **What the passing run did:** run 1 mostly did not surface them as candidates (9 appeared only as file names, 5 never appeared). It read 1013-00004 (engagement letter only) and dropped it without a recorded reason. None was read and explicitly rejected.

## 082: semiconductor IP disputes where we actually litigated an injunction

Question asked (2026-11-12): same analysis for 082.

Answer:

The right answer is **none**: the only criterion is "no qualifying semiconductor injunction matters". All three runs found and read the one candidate, 1014-00004 (*Optiwave v. Lumicore*, E.D. Tex.), and saw the same facts. They differ only in how they read "actually litigated".

**What the file shows:** injunction work was prepared but never litigated.
- The emergency TRO / preliminary-injunction motion is marked "DRAFT — CONTINGENCY — ON HOLD PER CLIENT INSTRUCTION", and the bond analysis says no PI motion was filed.
- The permanent-injunction analysis recommends seeking one after a favourable verdict, at a trial still scheduled (February 2026).
- The permanent-injunction order is a proposed draft with blanks and open drafting notes.

**What each run did with 1014-00004**

| Run | Read | Decision |
|---|---|---|
| 1 | Injunctive Relief folder (draft PI motion, injunction analysis, proposed order, irreparable-harm memo), status report, conflict memo | Defined "actually litigated" as a filed or argued motion, or a litigated order; found only drafts → **rejected explicitly**, answer "none" → pass |
| 2 | 12 files: the same injunction files plus trial-preparation documents | Wrote that under a strict reading no matter qualifies, then adopted a broader "conflicts/precedent screen" and named 1014-00004 as the qualifying matter → fail |
| 3 | 10 files, same set | Gave both readings and led with "1014-00004 qualifies" → fail |

The failure is interpretation, not retrieval. The question says "where we **actually** litigated an injunction", and that word excludes drafts held back on client instruction. Runs 2 and 3 saw every disqualifying fact, even stated the strict result, and still answered with the looser reading. Hedging with two readings does not help when the answer leads with the wrong one.

**Precision check (1014-00004)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. It is the obvious candidate (a semiconductor patent case with an "Injunctive Relief" folder) and had to be examined.
- **Was surfacing it more thorough?** No. All three runs surfaced it at step 3 through file-name searches and read the same injunction files; runs 2 and 3 read a few more trial-preparation files, which changed nothing.
- **What the passing run did:** run 1 read it and **rejected it explicitly**, stating its test ("filed or argued a TRO/PI motion, or litigated an injunction order") and why the matter fails it. This is the first task in this set where the passing run rejected the matter on the record instead of never seeing or never reading it.

## 137: M&A deals where we actually invoked or litigated specific performance

Question asked (2026-11-12): same analysis for 137.

Answer:

The question asks for "the M&A deals where we **actually invoked or litigated** specific performance". The permitted set is one deal, **1018-00008** (Penterra / Veridian). There, Veridian demanded specific performance before litigation, and the firm drafted the answer and a declaratory-judgment counterclaim.

**Why Northgate / Ridgeline (1022-00002) is wrong:** the firm's two letters to Ridgeline's counsel (December 2022 and November 2023) only **reserve** rights. Northgate "expressly reserves its right to pursue all available remedies ... including ... specific performance". The firm's own memo recommended exactly that: "a formal reservation-of-rights letter". No demand to perform was made, no complaint was drafted, and the matter went dormant. Reserving the right to seek a remedy is not invoking it, and "actually" excludes it, as in 082. Run 1 even wrote that it "qualifies by formal invocation/reservation in counsel correspondence, but not by court litigation", treating reservation and invocation as the same thing.

**What each run did with 1022-00002**

| Run | Surfaced | Opened | Decision |
|---|---|---|---|
| 1 | Step 3, file-name search `*litigation*` (its "Dispute & Litigation" folder) | Steps 17-21: litigation-risk memo, November 2023 letter, dormancy memo | Included → **fail** |
| 2 | Step 3, `*litig*` | Steps 19-25: both letters, three dispute memos, dormancy memo | Included → **fail** |
| 3 | Step 4, `*litigation*` listing | Never | Not included → pass |

**Run 2's second failure (proof document):** it never opened `1018-00008/Administrative/matter-status-memo-deal-terminated.docx`, the memo that corroborates Veridian's threatened specific-performance claim. Runs 1 and 3 opened and cited it. This is a coverage gap in the qualifying matter, separate from the precision error.

**Precision check (1022-00002)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. Its dispute letters really do discuss specific performance, so it belongs among the candidates. Runs 1 and 2 read the reservation language and counted it as an invocation.
- **Was surfacing it more thorough?** Not really. All three runs surfaced it the same way, through a `*litig*` file-name search. Runs 1 and 2 went further by opening it. Run 3's only content search was the grep tool, which sees raw bytes, so on the .docx files it found 1 match in total (an .eml); it never saw the letters' text.
- **What the passing run did:** run 3 surfaced it but did not read it. It was not rejected.

## 167: deals over $1B base consideration governed by Delaware law

Question asked (2026-11-12): same analysis for 167.

Answer:

This one is a **recall** failure, not precision: run 1 left out a qualifying deal, 1038-00009 (NovaMart Global stock sale to Cascade Retail: $1.2 billion all cash, no earnout, Delaware law, SPA §§ 1.01, 2.01, 12.05). No run lost precision.

**Why run 1 missed it:** a capped tool output, taken as the whole.
- Step 10: it converted 30 candidate agreements to text, 1038-00009's stock purchase agreement among them.
- Step 13: one grep over all 30 for governing law showed 1038-00009 under Delaware. A second grep for price terms ("Purchase Price", "Aggregate Consideration", …) answered **"Found 250 of 369 matches"**, and 91 KB of the result was saved to `/tmp/dsh-spill-…/…-grep.txt`. 1038-00009's "Aggregate Purchase Price … $1,200,000,000" was in the omitted part.
- On the base harness that saved file is unreachable. `read` is confined to the workspace, and bash runs in the container, where that host folder does not exist. The agent never tried to open it anyway.
- Step 18: it checked prices file by file only for the matters it had seen in the visible part. 1038-00009 was not among them, so it was never evaluated, and nothing in the reasoning or the answer mentions it.

**What runs 2 and 3 did differently:** they read each candidate's agreement on its own. Run 2 copied the candidate texts to a scratch folder and read 1038-00009's at step 26; run 3 re-parsed its SPA at steps 26-38. Both saw $1,200,000,000 plus Delaware law and included it.

**Recall check (1038-00009)**
- **Surfaced?** Yes, in all three runs, through a `*purchase*agreement*` / `*purchase*.docx` file-name search (step 5 in run 1).
- **Read?** Run 1 read its governing-law clause (Delaware) but never its price. The price lines sat in the capped part of one grep, which it did not page or narrow.
- **How it was lost:** surfaced and half-read, then dropped without a decision. This is "partial view taken as the whole", and the full view was out of the agent's reach on this harness. It is the case agent-tools' honest glob/grep targets: the saved full result is moved into a folder the agent can open, and the truncation counts as an incomplete observation that check_answer lists.

## 192: merger agreements that actually use "material adverse effect"

Question asked (2026-11-12): same analysis for 192.

Answer:

The question asks for "all our **merger agreements** that actually use the phrase 'material adverse effect'". The permitted set is the 9 matters whose merger or business-combination agreements use it. Run 2 added a tenth document: 1039-00004's **Offer-to-Purchase Agreement** (Torchlight / Ridgeline Cobalt).

**Why that is wrong:** it is a tender-offer agreement. The merger that followed was a short-form merger under DGCL § 253, effected by a certificate of merger with no merger agreement. The document does define "Company Material Adverse Effect", but it is not a merger agreement. Run 2 knew this. Its reasoning at steps 8-9 says it is "more of a tender offer agreement rather than a merger agreement" and that it should "keep it focused on actual merger agreements". Its answer then added it anyway, in a "practical pull set" of "related merger instruments", conceding "it is not titled 'Merger Agreement'". As in 082, a hedge that still names the item counts as including it.

**What each run did with 1039-00004**

| Run | Surfaced | Opened | Decision |
|---|---|---|---|
| 1 | Step 3, `*[Mm]erger*`: matched by its `certificate-of-merger-dgcl-253.docx` | Never | Not included → pass |
| 2 | Step 3, `*merger*`; then its full-text scan of every agreement .docx found MAE in the Offer-to-Purchase Agreement | Steps 8-12: the agreement | Recognised as a tender-offer agreement, included as "related" → **fail** |
| 3 | Step 3, `*merger*` (same file) | Never | Not included → pass |

**Precision check (1039-00004)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing, or rather mis-decided: run 2 read it correctly and still put it in the answer. Surfacing was right, since the document does contain the phrase and belongs to a merger transaction.
- **Was surfacing it more thorough?** Yes. Run 2 scanned the text of every agreement .docx, not only files named merger agreement; the same scan also caught a business-combination-agreement redline that file names would miss. Runs 1 and 3 parsed only files named like merger agreements.
- **What the passing runs did:** runs 1 and 3 surfaced it only as a file name (its certificate of merger) and never opened it. It was not rejected.

## 198: executed credit agreements from deals over $1B

Question asked (2026-11-12): same analysis for 198.

Answer:

The permitted set is 3 matters: 1003-00003 (VeloPay / Harrowgate, $1.9B merger), 1005-00001 (Nexford) and 1041-00003 (Cloudium / Solara, $6.8B). Run 1 added a fourth, **1043-00001 (Ironhaven Data Centers)**, a $950M Term Loan B financing with no acquisition.

**Why it was included, and why that is wrong:** run 1's answer says Ironhaven's executed credit agreement "states that the proceeds fund a portion of merger consideration of approximately **$1.9 billion**". It does not. Ironhaven's agreement never mentions $1.9 billion or merger consideration; the figure comes from VeloPay's credit agreement (1003-00003), the first row of the same answer. Run 1 had established the truth itself:
- step 22: a search for anything about a merger in Ironhaven's files found "No files found";
- step 25: its reasoning reads "deal 1043 is a facility of $950M but has a total capital of $1.36B without considering merger value above $1B".

The step-26 answer then listed Ironhaven as a fourth qualifying deal with VeloPay's number attached. This is neither a retrieval nor an interpretation error. A correct assessment was lost while writing the answer: a fact moved from one matter to another, and the deliverable contradicts the run's own record.

**What each run did with 1043-00001**

| Run | Surfaced and read | Decision |
|---|---|---|
| 1 | Step 3 (file listing); its credit agreement parsed at step 8 and searched at steps 18-21 | Assessed as $950M with no merger (step 25), then written up as a $1.9B merger deal → **fail** |
| 2 | Read its executed agreement | **Rejected explicitly**: "Excluded sub-billion financings: … Ironhaven Data Centers (approximately $950 million)" → pass |
| 3 | Read its executed agreement | Listed only as a "supplemental capital-structure comparator, not … a core 'deal value over $1 billion' transaction" → pass |

The grader accepted run 3's "supplemental" listing, but in 192 it penalised run 2's "related merger instrument" listing. Naming a non-qualifying item with a caveat is judged inconsistently, so it is risky either way.

**Precision check (1043-00001)**
- **Wrong to surface, or misread after surfacing?** Neither, strictly: it was read and assessed correctly, then misreported in the answer. Surfacing was right, since it is an executed credit agreement in a sizeable financing.
- **Was surfacing it more thorough?** No. All three runs found and read it.
- **What the passing runs did:** run 2 read it and **rejected it explicitly** (sub-billion). Run 3 read it and kept it out of the qualifying set, mentioning it only as a supplemental comparator.

**Observations**
- A new kind of failure: not retrieval and not interpretation. The run's assessment was right; the answer it wrote contradicts it. In the catalog's terms, deliverable drift (a decision never reaches the answer intact) and fact from the wrong source (another matter's figure attached to this one).
- This is the second task where a passing run read the matter and explicitly rejected it (run 2), after 082's run 1.
- Naming a non-qualifying item with a caveat is graded inconsistently: run 3's "supplemental" listing passed here, while 192's "related merger instrument" listing failed.

## 200: conflict check, have we ever been adverse to Vantor Holdings?

Question asked (2026-11-12): analyse 200.

Answer:

A **recall** failure in run 2. It found 2 of the 3 adverse matters (1012-00005, 1023-00002) and missed **1038-00007**, *Vantor Holdings Corp. v. Cascade Retail Holdings* (L.A. Superior Court), where the firm defended Cascade against Vantor. That matter could hardly be more visible: Vantor appears in all 35 of its files (up to 186 times in one), and two file names contain "vantor". Run 2's tools kept it out of sight, one after another:

1. **Step 3: grep "Vantor|vantor" over all documents → "Found 250 of 253 matches".** Grep sees raw bytes, so every hit came from .eml and text files of 1012-00005 and 1023-00002. The .docx files of 1038-00007 cannot match at all. The full list was saved to a host temp file; at step 5 the run tried to read it and could not ("I can't read the temporary files due to workspace issues").
2. **Step 5: file-name search `*Vantor*` → "No files found".** The search is case-sensitive, and the files are named `memo-vantor-supply-agreements-termination.docx` and `memo-project-atlas-emails-vantor.docx`.
3. **Step 6: grep "Vantor Holdings Corp" in `*.docx` → "No matches found".** Grep is blind inside .docx, so "no matches" says nothing, but the run took it as a negative and searched only within the two matters it already had.

**What runs 1 and 3 did:** at step 3 they also ran a lowercase `*vantor*` file-name search, which matched 1038-00007's two memos. They opened its engagement letter and conflict-check memo and included it.

**Recall check (1038-00007)**
- **Surfaced?** Not in run 2, at any point. Runs 1 and 3 surfaced it at step 3 through the lowercase file-name search.
- **Read?** Run 2 never; runs 1 and 3 read its engagement letter and conflict memo.
- **How it was lost:** by the instruments, not by judgement. A grep blind to .docx, a capped result whose full list the base harness cannot open, and a case-sensitive file-name search. In the catalog's terms: blind instrument, partial view taken as the whole, absence taken as a negative.

**Observations**
- This is the cleanest example yet of the catalog's tool-limit families, three of them in a row, and of absence read as a negative ("No matches found" in .docx). Runs 1 and 3 passed only because they also tried the lowercase spelling of a file name.
- On a conflict check, a missed adverse matter is the costly error. Run 2's answer gives no hint that its search was blind to .docx, so the gap is invisible to the reader.
- Agent-tools' layer 1 and 2 target exactly this: `search` reads .docx and reports per term and per unit, grep's description says it sees raw bytes only, and saved full results land where the agent can open them.

## 066: most recent fund / co-invest vehicle with an LPAC, and its formation documents

Question asked (2026-11-12): analyse 066.

Answer:

No run got the matter wrong: all three identified the Pellegrino co-investment vehicle (1027-00002), its LPA date and the LPAC under Section 9.1. The flips are in the **proof documents**. The task asks to "pull the formation/LPA documents", and the rubric expects five: the executed LPA, the key-terms memo, the side letter, the subscription agreement and the closing checklist. The matter has 12 files, and each run cited a different six of them (all three also cited the enforceability opinion and the funds-flow memo, which no criterion asks for).

| Run | Subscription agreement | Key-terms memo | Graded |
|---|---|---|---|
| 1 | Seen in the file listing (step 8), **never opened**; mentioned only inside the opinion-letter summary ("identifies the executed LPA, side letter, and subscription agreement…") | Opened, cited | **fail** on the subscription agreement |
| 2 | Seen (step 18), **never opened**; the **same sentence** as run 1 | Opened, cited | pass |
| 3 | Opened (step 11), cited by name | **Opened (step 7), not cited** | **fail** on the key-terms memo |

**Document check**
- **Subscription agreement:** surfaced in all runs. Runs 1 and 2 never read it and mention it only second-hand, through the opinion letter; run 3 read and cited it. Runs 1 and 2 are equally incomplete, yet run 1 failed and run 2 passed: the grader accepted the identical description once and rejected it once.
- **Key-terms memo:** surfaced and read in all runs. Runs 1 and 2 cited it; run 3 read it and dropped it from the answer, so it was read but not delivered.

**Observations**
- This is the first flip caused by grading noise: identical wording about the subscription agreement was graded fail in run 1 and pass in run 2. With one criterion per document, that noise alone flips all-pass.
- Run 3 is deliverable drift again, as in 198: a document it read did not make it into the answer.
- The request "pull the formation/LPA documents" asks for completeness, but each run curated a short list of six. Listing all 12 files of the vehicle's matter (and opening the subscription agreement instead of citing it second-hand) would have satisfied every proof criterion in every run.

## 104: latest Labor & Employment matter where we agreed equity-acceleration terms

Question asked (2026-11-12): analyse 104.

Answer:

The question has three conditions: a **Labor & Employment** matter, where acceleration terms were **agreed**, the **latest** such matter; plus the document that sets them out. The answer is **1017-00004**, *Aldrich v. Aurelius Media*. Its executed settlement agreement (`aldrich-settlement-agreement-execution.docx`, 19 January 2024) sets out the equity acceleration in § 3(a). The two failing runs each named a different wrong matter, so they lost all three criteria.

**The two wrong picks**
- **Run 1, Northgate CEO negotiation (1022-00004):** a real L&E matter and later (2024), but nothing was agreed. The board resolved on 12 September 2024 to terminate the negotiations; the final term sheet was non-binding, and there is no executed employment agreement. Run 1's own answer says "termination of negotiations … absence of an executed definitive employment agreement", yet treats the acceleration as "agreed in principle" in July negotiation notes. It read the disqualifying fact and chose anyway (as in 028), with "agreed" read loosely (as "actually" in 082 and 137).
- **Run 2, NovaMart stock sale (1038-00009):** an M&A deal. Its acceleration language sits in draft executive employment agreements attached as exhibits to the stock purchase agreement, and in a retention plan. That fails the Labor & Employment scope (as "Capital Markets" in 048) and "agreed" (drafts).

**What each run did**

| Run | How it searched | 1017-00004 (right) | Wrong pick |
|---|---|---|---|
| 1 | File names: `*[Vv]est*`, `*[Aa]ccel*`, `*[Ee]mployment*`, `*[Ll]abor*` | **Never surfaced**: none of those words is in its file names | 1022-00004, read and chosen → fail |
| 2 | Listings of every matter's `Engagement & Administration` folder, then employment documents | Surfaced (step 4 listing), **never opened** | 1038-00009, read and chosen → fail |
| 3 | File names, then a content grep for "acceleration" (step 4), which hit the matter's .eml files | Surfaced, opened (steps 6-7), executed agreement read → chosen | 1022-00004 and 1033-00005 **read and explicitly rejected** (non-binding / terminated; pro-rata only) → pass |

**Precision check (1022-00004, 1038-00009)**
- **Wrong to surface, or misread after surfacing?** Misread after surfacing. Both are full of acceleration language and had to be considered. Run 1 misread "agreed"; run 2 ignored the Labor & Employment scope.
- **Was surfacing them more thorough?** No, the opposite. The failing runs used file names only; the passing run added a content search.
- **What the passing run did:** run 3 read 1022-00004 and **rejected it explicitly** ("non-binding … negotiations terminated"), and also rejected 1033-00005 (pro-rata acceleration only).

**Recall check (1017-00004)**
- Run 1: never surfaced. Its file names (`aldrich-settlement-…`) contain none of the words searched.
- Run 2: surfaced in a folder listing, never opened.
- Run 3: surfaced by the content grep, but only because the matter also has .eml files. Grep cannot see inside .docx, so had all its files been .docx, this run would have missed it too.

**Observations**
- This is the first task where the **passing run was the more thorough one**: a content search beat file names. In 028, 072 and 192 the thorough run was the one that failed.
- It is the third task where a passing run read the wrong candidate and **explicitly rejected** it (after 082 and 198).
- One task combines most of the patterns: a strict qualifier read loosely ("agreed"), a scope condition skipped (Labor & Employment), and a right matter never surfaced or never opened. Getting it right needed all three conditions checked per candidate, which is what a ledger with criteria copied from the question would enforce.

## 162: the first traditional, non-SPAC IPO we took public

Question asked (2026-11-12): analyse 162.

Answer:

The answer is **1037-00001, Solstice Biomedical Devices**: an ADS IPO on Nasdaq that closed in **March 2023** (deposit agreement and lock-ups dated 2 March 2023; closing opinion and certificates). Runs 2 and 3 named **Arbor Health Technologies (1010-00002)**, whose NYSE IPO closed on **13 February 2024**. Arbor is a real traditional IPO with the firm as issuer's counsel; it is just not the first. Naming the wrong matter cost all four criteria (matter, offering document, closing proof, precision).

**Why the failing runs stopped at Arbor**
- **Their searches looked for the paperwork of a US IPO.** Searches for `*prospectus*`, `*registration*`, `*s-1*` and `*underwrit*` hit Arbor's large file (S-1, amendments, 424(b)(4) prospectus). Solstice's 12-file folder holds an underwriting agreement, a deposit agreement, lock-ups and closing papers, but no S-1 or prospectus. Only `*ipo*` matched it, through `engagement-letter-solstice-ipo.docx`.
- **"First" was decided without dating every candidate.** Both runs excluded the earlier-numbered matters (1002 a SPAC, 1008 withdrawn, 1015 postponed) and took the next one, Arbor. Run 2 wrote that starting with 1002 "makes sense since it has a low number, which might indicate a first IPO". Matter numbers are not chronology: 1037 closed a year before 1010.

**What each run did**

| Run | 1037-00001 (Solstice, right) | 1010-00002 (Arbor, wrong) |
|---|---|---|
| 1 | Surfaced (step 4, `*ipo*`); after first leaning to Arbor (step 12) it searched for earlier deals, noted "the Matter IDs … aren't chronological" (step 16), read the closing papers, chose it → pass | Read; **rejected explicitly as later** ("the February 2024 Arbor Health IPO … do not precede Solstice's March 2023 completed IPO") |
| 2 | Surfaced (step 3, `*ipo*`), its folder listed (step 4), **never opened** | Chosen → fail |
| 3 | Surfaced (step 3, `*ipo*`), **never opened** | Chosen → fail |

**Precision check (1010-00002)**
- **Wrong to surface, or misread after surfacing?** Neither, strictly: Arbor really is a traditional, completed IPO. The error is in the comparison. "First" was asserted without dating all candidates.
- **Was surfacing it more thorough?** No. All three found Arbor. The passing run was the more thorough one: it kept looking for earlier deals after it had a plausible answer.
- **What the passing run did:** run 1 read Arbor and **rejected it explicitly** as later than Solstice.

**Recall check (1037-00001)**
- Surfaced in all three runs, through `*ipo*` (the engagement letter's file name).
- Read only in run 1. Runs 2 and 3 never opened any of its files, so it was never dated.
- How it was lost: surfaced but not read, because the runs' idea of an IPO file (S-1, prospectus) did not fit a foreign issuer's ADS offering, and because the comparison stopped at the first plausible candidate.

**Observations**
- A superlative question ("first", like "latest" in 104) is only answered once every candidate is dated. Two of three runs stopped at the first one that fit.
- Two proxies misled: matter number for chronology, and US-style IPO paperwork (S-1, prospectus) for "is an IPO".
- This is the second task in a row where the passing run was the more thorough one (104, 162), and the fourth where it read the wrong candidate and explicitly rejected it (082, 198, 104, 162).

## 185: Cascade Retail's most recent matter (subject and open date)

Question asked (2026-11-12): analyse 185.

Answer:

Cascade Retail Holdings has ten matters, 1038-00001 to 1038-00010, and matter numbers are not chronological. The most recent is **1038-00003**, a new automatic shelf registration on Form S-3, opened on **6 April 2026**. Run 1 named **1038-00001**, the FTC antitrust defence of Cascade's Pinnacle acquisition, opened 25 June 2025. That is a real Cascade matter, but not the latest, so it lost all four criteria.

**Why run 1 never saw 1038-00003:** its candidate list was the output of one grep.
- Step 4: grep "Cascade Retail Holdings" over all documents. Grep reads raw bytes, so it matched only the 5 Cascade matters that have .eml or other text files (00001, 00002, 00006, 00009, 00010). 1038-00003's 12 files are 11 .docx and 1 .xlsx, so there was nothing for grep to match.
- Step 4: glob `documents/matters/*/Engagement*/*` was capped: "Showing 100 of 637". 1038-00003's engagement letter was not among the 100.
- Step 5: glob `documents/matters/1038-*/*` returned "No files found". Glob lists files only, and these matters keep everything one level deeper. The run did not retry with a deeper pattern; it read "nothing there" as "nothing more".
- It then dated the 5 matters it had and took the latest, 1038-00001.

**What runs 2 and 3 did:** run 2 listed every file of all ten Cascade matters (`1038-*/*/*`) and read each one's engagement documents. Run 3 extracted the text of the documents and searched it. Both dated all ten and chose 1038-00003. Run 3 wrote that it took "the latest opening date, rather than simply the highest matter number", explicitly setting aside the highest-numbered matter, 1038-00010 (opened June 2025).

**Precision check (1038-00001)**
- **Wrong to surface, or misread after surfacing?** Neither: it is a genuine Cascade matter, correctly dated. The error is a comparison over an incomplete candidate set.
- **Was surfacing it more thorough?** No. The passing runs were the thorough ones: they enumerated all ten matters.
- **What the passing runs did:** both read it and set it aside as earlier (run 2 lists its 25 June 2025 date in its comparison).

**Recall check (1038-00003)**
- Run 1: never surfaced. The grep could not see .docx, one listing was capped, and the other used a glob that returns files only, at a level that holds only folders.
- Runs 2 and 3: surfaced through complete enumeration or text extraction, read, chosen.

**Observations**
- Another superlative ("most recent", like 104 and 162) decided over an incomplete candidate set. Here the gaps were all tool limits: three silent failures in one step.
- The client's matters share a number prefix (1038-), so enumerating `1038-*` folders gives the complete candidate set directly. Run 1 tried exactly that, but the glob pattern returned nothing because it lists files, not folders.

## 210: top five clients by number of matters

Question asked (2026-11-12): analyse 210.

Answer:

The ground truth comes from the folder names: there are 266 matter folders, and the first four digits are the client. **Lumos (1008), Quorum (1025) and Cascade (1038) have 10 each**; **Dunmore (1016), Aurelius (1017) and Penterra (1018) have 9 each**; no one else has more than 8. The rubric expects exactly that, with ties at the top and at the cutoff. Run 2 got 15/15; runs 1 and 3 kept Lumos and little else.

| Run | How it counted | Result |
|---|---|---|
| 1 | Listed engagement-letter files series by series (`matters/<series>-*/*/engagement*.docx`, to get around the 100-path cap) but **only for series 1001-1030**: its tally (step 10) has 30 entries and sums to 181. The matters run to 1046, and its own first listing said "Showing 100 of 290" letters. It then read the letters for client names and **split Quorum** into two entities ("Quorum vs. QIH"), so Quorum's 10 became two smaller counts | Lumos 10, Dunmore 9, Penterra 9, then five clients at 8; **Cascade never counted**, Quorum and Aurelius missing → 4/15 |
| 2 | Counted the **matter folders** per 4-digit series, all 266, and confirmed each series' client in its engagement and administration documents (parent, board and subsidiary engagements kept under one client) | Exact → 15/15 |
| 3 | Listed `Engagement*` folders for every series up to 1046, then ran a script to extract client names from all engagement documents: **timed out at 60 s** (step 12). It restarted it in the background (step 14), spot-checked a few letters, **wrote the answer from the partial results** (step 29) and **killed the background job** before it finished ("Top-five counts validated; full index no longer needed") | Lumos 10, then four clients at 8 (Dunmore at 8, not 9); Cascade, Quorum, Aurelius, Penterra missing → 3/15 |

**Count check**
- **Run 1:** a partial range taken as the whole (series 1001-1030, never checked against the 266 matters or 290 letters), plus one client split into two names.
- **Run 3:** a timed-out scan, then an abandoned background job; the answer was built on whatever the partial extraction and spot checks covered.
- **Run 2:** counted the unit asked for, matters, by enumerating all matter folders directly; read documents only to name each series' client.

**Observations**
- For a counting question, the unit must be enumerated directly and completely (here, matter folders), with a total to check against (266). Runs 1 and 3 counted through a proxy (engagement letters and their client names) over an incomplete range.
- Run 1's split of Quorum is the catalog's "narrowing that drops recall" in a counting form: an entity key (client name) that splits one client.
- Run 3 is the catalog's "scan timed out" plus a new twist: it saw the timeout, started the full job correctly in the background, and then killed it rather than wait.
- Run 2 needed no special tool. The folder structure already encoded the answer, and it was the only run that used it as the primary count.

**How run 2 got it right** (question asked 2026-11-12: "explain the correct agent in 210")
1. It hit the same walls first: listings capped at 100 of 637 (step 3), and "file access denied" on the saved full list (step 4).
2. It moved the enumeration into a script (step 6). One Python script in bash read all 290 `engagement*.docx` with no path cap, saved a short snippet of each to `engagement_snippets.txt` in the workspace, and printed only "processed 290". The full data went to a file the agent could open; only a short result reached its context.
3. **The decisive move (step 8): it counted folders, not letters.** It reasoned "identify unique matter directories using the 4-digit prefixes", and a three-line script listed every matter folder and counted them by prefix: "matter dirs 266 / 1008 10 / 1025 10 / 1038 10 / 1016 9 / 1017 9 / 1018 9 / …". That is the complete count of the unit asked for, with a total to check against, and it reads no files, so nothing could time out.
4. It read documents only to name the top six series (steps 9-11): their snippets, matter by matter.
5. It checked the awkward cases instead of splitting them. 1017-00001 has no engagement letter, so it read its other documents (step 12). It kept Aurelius's parent, board and subsidiary engagements as one client. It considered whether one client could span several prefixes.
6. It reported the ties honestly (three at 10, three at 9, so six names for "top five") and re-read its answer to fix a detail before finishing.

In short: run 2 counted the unit the question names, completely, from the folder structure, and had a total to check against. Runs 1 and 3 counted a stand-in (engagement letters and the client names in them) over an incomplete range: run 1 stopped at series 1030; run 3 ran a script over every file under the matters folder, which timed out, and then abandoned the rerun.

## Overall patterns across all 14 tasks

14 flipping AHE-train tasks, three base-harness runs each: 42 runs, **22 failing and 20 passing**. Each run is counted once, under its main cause.

### Why the 22 failing runs failed

| Cause | Runs | Tasks (failing runs) |
|---|---|---|
| **Judgement after surfacing**: the item was found and read, and the decision was wrong | 12 | 028 (r1), 048 (r1, r2), 072 (r2, r3), 082 (r2, r3), 137 (r1, r2), 192 (r2), 104 (r1, r2; the right matter was also missed) |
| **Tool limits**: the right item never reached the agent intact | 5 | 167 (r1), 185 (r1), 200 (r2), 210 (r1, r3) |
| **Stopped early on a superlative**: "first" decided before every candidate was dated | 2 | 162 (r2, r3) |
| **Lost while writing the answer**: a correct assessment or a document read did not reach the deliverable | 2 | 198 (r1), 066 (r3) |
| **Grading noise**: the same wording as a passing run, graded fail | 1 | 066 (r1) |

The judgement errors come in four recurring forms:
- **A mention taken for involvement:** 028 (DIP as background to a sale), 072 (IRB in deal diligence).
- **A scope condition of the question never checked:** 048 (Capital Markets), 072 (the firm's own clinical-trial work), 104 (Labor & Employment).
- **A strict qualifier read loosely:** "actually litigated" (082), "actually invoked" (137), "agreed" (104).
- **A hedged inclusion:** the run knew the item did not fit and named it anyway, as "related" or under a broader reading (082, 192).

In most of these, the failing run's own reasoning or answer states the disqualifying fact (028, 082, 104, 137, 192): the information was there, the decision was not taken from it.

The tool limits are the catalog's first families, often several at once:
- **Grep blind inside .docx**, with "no matches" read as absence: 137 (r3, which passed by luck), 185, 200; also 104, where run 3 found the right matter only through its .eml files.
- **Capped outputs whose saved full result the base harness cannot open:** 167, 200, 210. That file sits in a host temp folder, outside the workspace that `read` is confined to and not in the container where bash runs.
- **File-name searches that are case-sensitive or list files only:** 200, 185.
- **A range assumed from a capped listing:** 210, series 1001-1030 only.
- **A scan that timed out,** whose background rerun was killed before it finished: 210.

Every recall, superlative and counting failure (167, 185, 200, 210, 162) comes from an incomplete candidate set, not from misjudging what was seen.

### How the 20 passing runs passed

| Mechanism | Runs | Tasks |
|---|---|---|
| **By omission**: never surfaced, or never read, the wrong item | 7 | 028 (r2, r3), 048 (r3), 072 (r1), 137 (r3), 192 (r1, r3) |
| **By decision**: read the wrong candidate and set it aside on the record | 7 | 082 (r1), 104 (r3), 162 (r1), 185 (r2, r3), 198 (r2; r3 kept it out of the qualifying set) |
| **By complete retrieval**: enumerated or read every candidate | 5 | 167 (r2, r3), 200 (r1, r3; only thanks to a lowercase file-name search), 210 (r2) |
| **By grading leniency** | 1 | 066 (r2) |

- **On the precision tasks (028, 048, 072, 137, 192), every pass is by omission.** No passing run read the wrong item and rejected it. The flip is luck in what got opened, not better judgement.
- **Thoroughness cuts both ways.** On precision tasks the failing run was often the more thorough one (028, 072, 192): a full-text scan surfaces more candidates, and without a decision step they turn into lost precision. On recall, superlative and counting tasks the passing run was the more thorough one (104, 162, 167, 185, 200, 210).

### What it implies

1. **Two different problems need two different fixes.**
   - **Precision tasks:** keep the thorough search, but decide each candidate against criteria copied from the question. That means the scope condition (practice group, the firm's own role), the strict qualifier ("actually", "agreed", executed vs draft), and an explicit reason for every exclusion. This turns passes by omission into passes by decision.
   - **Recall, superlative and counting tasks:** make the candidate set complete and say when it is not. That means reading inside .docx, saved full results the agent can open, honest counts on every listing, case-insensitive name search, and timeouts the agent must wait out or report.
2. **Superlatives and counts need every candidate dated or counted.** Matter numbers are not chronology (162, 185). The folder structure (one folder per matter, a client prefix) is the most reliable enumeration (185, 210).
3. **Check the answer against the record before finishing:** 198 (a fact moved between matters) and 066 (a document read but not listed).
4. **Some flips are grading, not the agent:** 066 run 1 (identical wording failed once and passed once); caveated listings graded inconsistently (192 failed, 198 passed). At three runs per task, part of the run-to-run variance is the judge's.
5. **How this maps to the agent-tools design** (docs/agent-tools/SOURCE.md on branch inv-new-tools):
   - `search`, honest grep and readable saved results target the tool-limit failures (137, 167, 185, 200, 210);
   - `ledger` criteria and recorded dismissals target the judgement failures and the passes by omission (028, 048, 072, 082, 104, 137, 192);
   - `check_answer` targets answer-writing drift (198, 066).

   Measured so far, layer 3 did not change the Harvey score significantly: +1.9 points all-pass against the three-run baseline, with a `check_answer` deliverable-path defect in that run. Whether it removes these specific failure modes is not yet tested task by task.
