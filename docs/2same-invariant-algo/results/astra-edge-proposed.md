# Proposed invariants

Run: `runs/im-astra-edge-20261119T173221Z`. What F1 proposed from P1 and P2 of each task, before any check; their later fate (points, removal, rewording) is in report.md.

## Task 1: `firm-knowledge/tasks/092`

P1 `astra1`, P2 `astra2`; 30 invariants.

**i1**
- observation: The task needs multiple phases: find matters, verify covenants, write a report *[task; why: A multi-phase task calls for a tracked plan]*
- action: Creates a three-item todo list: inventory sources, verify execution/duration/evidence, write and check the report
- purpose: Structures the work into trackable phases

**i2**
- observation: The system prompt says the workspace holds a documents folder and an output folder *[environment; why: Tells the agent where the source files are so it can list them]*
- action: Lists the workspace root and globs the whole document tree
- purpose: Finds out how the document corpus is laid out

**i3**
- observation: Goal tools are available for one long-running completion objective *[environment; why: Lets the agent register the task as a goal]*
- observation: The task is a large retrieval-and-report job *[task; why: Makes it a long-running objective rather than routine single-turn work]*
- action: Creates a goal that restates the task objective, including verification and delivery of the task deliverable
- purpose: Registers a completion objective to close out at the end

**i4** (follows i2)
- observation: The document corpus has thousands of files, mostly .docx/.xlsx/.pptx/.eml *[tool_result; why: Too many binary office files to convert one at a time]*
- observation: The read tool opens only plain text, and office files need conversion *[environment; why: The files have to become text before they can be searched or read]*
- action: Starts a background Python job that extracts text from every corpus document into text copies in a scratch folder, each tagged with its source path
- purpose: Builds a searchable plain-text mirror of the corpus

**i5** (follows i2)
- observation: The task asks about a specific covenant type in employment matters *[task; why: The covenant and agreement names are useful filename keywords]*
- action: Runs filename globs over the corpus for the covenant name, restrictive covenants and employment agreements
- purpose: Finds covenant-related documents and their matters before the text search is ready

**i6** (follows i4)
- observation: The text-extraction job is still running in the background *[tool_result; why: Its results are needed for full-text search, so its status matters]*
- action: Checks the background job's status with job_output between independent filename and partial-corpus searches
- purpose: Tracks when the full text copies are ready while other work continues

**i7** (follows i4)
- observation: A runtime notice says the background extraction job finished *[tool_result; why: Its output can now be collected and checked for errors]*
- action: Collects the job output and confirms the per-format conversion counts and an empty error list
- purpose: Confirms the text copies fully cover the corpus

**i8** (follows i4)
- observation: Text copies of the corpus are available in the scratch folder *[tool_result; why: Makes full-text search possible]*
- observation: The task limits results to matters in the target practice area *[task; why: The practice-area name is the filter to search for]*
- action: Greps the text copies for the target practice-area name, limited to engagement letters, matter memos, intake and conflict forms
- purpose: Finds which matters belong to the target practice area from staffing and classification records

**i9** (follows i8)
- observation: The practice-area greps produced a list of candidate matters staffed by or classified in the target practice area *[tool_result; why: Gives the set of matters to check for the covenant]*
- action: Runs a separate covenant-keyword grep over each candidate matter's text-copy folder
- purpose: Checks each candidate matter for any mention of the target covenant and screens out those with none

**i10** (follows i5)
- observation: Filename hits for restrictive-covenant or employment-agreement documents point to specific matter folders *[tool_result; why: Those matters are likely candidates whose full file sets need inspecting]*
- action: Globs the full contents of each likely candidate matter folder
- purpose: Sees every document a candidate matter holds (memos, drafts, settlements, closing records)

**i11** (follows i10)
- observation: Candidate matters hold firm analysis memos or comparison charts summarizing the covenant provisions *[tool_result; why: Those documents state the covenant terms, durations and execution facts]*
- action: Reads the text copies of the covenant analysis memos and comparison charts for each candidate matter
- purpose: Gets the covenant duration, the parties and the agreement dates

**i12** (follows i10)
- observation: Some candidate matters contain only draft or redline versions of the employment agreement with the covenant *[tool_result; why: Drafts do not show execution, so execution status has to be checked]*
- action: Greps those matters' closing or dormancy memos for execution, signing or withdrawal terms
- purpose: Finds out whether the drafted covenant was ever executed

**i13** (follows i10)
- observation: A candidate matter's file discusses a third party's existing employment agreement with a non-compete, held with another employer *[tool_result; why: That covenant's duration and nature need checking before deciding how to treat it]*
- action: Reads the analysis memo on the third party's existing agreement, including its non-compete section
- purpose: Gets the third-party covenant's exact duration and scope

**i14** (follows i10)
- observation: Candidate matter folders hold execution-version settlement agreements and a closing signature tracker *[tool_result; why: These may show execution and later changes to the covenants]*
- action: Reads the execution-version settlement agreements and the signature tracker
- purpose: Checks recitals about the original executed agreements and the modified or voided covenant terms

**i15** (follows i14)
- observation: The signature tracker lists the settlement as 'awaiting execution', and an 'execution version' label does not prove signing *[tool_result; why: Actual execution has to be confirmed from another record]*
- action: Reads or greps the matter closing memos for explicit statements that the agreements were executed and on what dates
- purpose: Establishes execution from an authoritative closing record

**i16** (follows i14)
- observation: The settlement recitals mention an underlying employment agreement and amendment by date *[tool_result; why: A pleading in the same matter may corroborate that the agreement was executed]*
- action: Reads the filed cross-complaint, which alleges the agreement and amendment were executed and attaches them as exhibits
- purpose: Corroborates execution of the original covenant-bearing agreement

**i17** (follows i9)
- observation: Per-matter grep hits show that one candidate matter's contractor agreements carry a 12-month non-compete, signed by a stated number of people under one version *[tool_result; why: Shows a qualifying covenant whose execution and version-specific terms need checking]*
- action: Reads that matter's witness declaration, then globs for and reads its agreement-version comparison chart
- purpose: Confirms covenant duration, which version applies and the signing counts

**i18** (follows i11)
- observation: An analysis memo shows a 12-month non-compete in a client's executed legacy agreements that the firm found void and removed *[tool_result; why: The matter's closing record should confirm the outcome and the practice-group attribution]*
- action: Reads that matter's closing letter/summary
- purpose: Confirms the matter's practice group, dates and how the covenant was handled

**i19** (follows i7)
- observation: Text extraction is done for the whole corpus *[tool_result; why: Coverage can now be quantified for the report]*
- action: Runs a script that counts matter folders and extracted text copies
- purpose: Checks search coverage and gets figures to state in the report

**i20** (follows i1)
- observation: Verification of execution, duration and evidence for all candidate matters is finished *[reasoning; why: The plan can move to the writing phase]*
- action: Updates the todo list to mark inventory and verification done and report-writing in progress
- purpose: Keeps the plan's status current before writing

**i21** (follows i15, i16, i17, i18)
- observation: Several candidate matters have confirmed execution evidence for a covenant of at least the minimum duration *[reasoning; why: These are the qualifying matters to report]*
- observation: The task wants findings, the documents relied on and the reasoning in one self-contained markdown file *[task; why: Sets the structure and file name of the task deliverable]*
- action: Writes the task deliverable with a summary table of qualifying matters and, per matter, covenant terms, execution evidence, cited source documents and qualifications
- purpose: Delivers the required report

**i22** (follows i21)
- observation: Some qualifying executed covenants were later found void, deleted or shortened by settlement *[tool_result; why: Execution and enforceability have to be kept apart in the report]*
- action: Counts these as historically executed covenants in the report and notes the voiding or modification as a qualification, keeping execution separate from enforceability
- purpose: Reports every executed covenant accurately without implying it can be enforced

**i23** (follows i12, i21)
- observation: The closing/dormancy memos state that the drafted agreements in some candidate matters were never executed, because the candidate withdrew or declined *[tool_result; why: These matters fail the executed requirement]*
- action: Lists those near-miss matters in an exclusions table with the reason and the controlling document
- purpose: Shows why matters with drafted but unexecuted covenants were left out

**i24** (follows i13, i21)
- observation: In one target-practice matter, the 12-month covenant belongs to a third party's existing agreement with another employer *[tool_result; why: It is not a client covenant the firm executed, but it may matter to the user]*
- observation: That matter's closing memo says no definitive agreement was executed *[tool_result; why: The client's own proposed covenant does not qualify]*
- action: Flags this matter separately as a fifth lead, kept apart from the qualifying matters, and does not count it as an executed client covenant
- purpose: Surfaces relevant precedent without overstating what qualifies

**i25** (follows i5, i21)
- observation: Many non-compete agreements in the corpus sit in transaction-document folders of M&A or commercial matters *[tool_result; why: These are outside the target practice area despite matching the covenant keyword]*
- action: States in the report that acquisition and commercial non-competes were not counted just because employment documents or lawyers were involved
- purpose: Applies the practice-area filter by matter scope, not by keyword hit

**i26** (follows i21)
- observation: The task deliverable has just been written *[tool_result; why: Its content should be reviewed after writing]*
- action: Reads back the opening section of the written task deliverable
- purpose: Checks the report's rendering and content

**i27** (follows i21)
- observation: The task deliverable cites many source document paths, some relative to a matter root *[tool_result; why: Cited paths can be checked against the corpus]*
- action: Runs a Python script that pulls the cited document paths out of the report and asserts each one exists in the corpus
- purpose: Makes sure every citation points to a real source document

**i28** (follows i27)
- observation: Report validation found no missing citations *[tool_result; why: The writing phase is done]*
- action: Marks every todo item complete
- purpose: Closes the plan

**i29** (follows i3, i28)
- observation: The system prompt requires calling get_goal before update_goal and copying its id and revision *[environment; why: Needed to mark the goal complete correctly]*
- observation: The goal objective has been achieved *[reasoning; why: Allows the goal to be marked complete]*
- action: Calls get_goal, then update_goal with the returned id and revision and action complete
- purpose: Formally closes the long-running goal

**i30** (follows i29)
- observation: The goal is marked complete and the task deliverable is validated *[tool_result; why: Only a final handoff is left]*
- action: Ends with a short message linking the task deliverable and summarizing the qualifying matters, evidence, and exclusions/qualifications
- purpose: Hands off the result to the user

Role terms: **task deliverable**: the single self-contained markdown report the task asks for, written to the output folder; **document corpus**: the read-only collection of matter folders holding office-format and email files; **text copies**: plain-text versions of the corpus documents that the agent extracts into a scratch folder; **target practice area**: the practice area the task filters matters by; **target covenant**: the contract clause type the task asks about, with its minimum duration; **candidate matter**: a matter in the target practice area that may contain a qualifying covenant; **near-miss matter**: a candidate matter where the covenant was only drafted or negotiated, or belongs to a third party; **execution evidence**: documents stating that an agreement was signed (closing memos, settlements, pleadings, declarations, trackers)

## Task 2: `firm-knowledge/tasks/093`

P1 `astra1`, P2 `astra2`; 24 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a three-phase todo list: identify candidate agreements, compare and verify the shortest qualifying one, write the deliverable
- purpose: Structures the work before exploring

**i2** (follows i1)
- observation: The workspace contains a documents folder and an output folder *[tool_result; why: Shows where the corpus to explore is]*
- action: Lists every file in the document corpus with a recursive glob
- purpose: Learns the matter/folder layout of the corpus

**i3** (follows i2)
- observation: The task asks about post-employment non-compete terms in agreements *[task; why: Supplies the keywords for filename and content searches]*
- observation: The corpus is organised as matter folders of documents and emails *[tool_result; why: Filenames and plain-text emails can be searched directly before any conversion]*
- action: Globs filenames for non-compete, restrictive-covenant, separation and employment documents and greps the plain-text emails for non-compete mentions
- purpose: Finds a first set of relevant agreements and matters

**i4** (follows i2)
- observation: The read tool only opens plain text; .docx/.xlsx need conversion *[environment; why: Explains why the agent needs to know which formats the corpus contains]*
- observation: The corpus listing is large and mostly .docx files *[tool_result; why: Prompts a count of the formats to size the conversion work]*
- action: Counts the files in the corpus by extension with a short python script
- purpose: Measures how many binary documents need converting

**i5** (follows i4)
- observation: The corpus holds thousands of .docx files and hundreds of .eml files *[tool_result; why: Converting them one by one would be impractical]*
- observation: Office documents cannot be grepped or read directly *[environment; why: Content search needs plain-text copies]*
- action: Starts a background job that converts the whole corpus to a searchable text copy under a scratch folder, mirroring its paths
- purpose: Allows full-text grep across every document while other work continues

**i6** (follows i3)
- observation: Email grep hits describe a modified shorter non-compete agreed in a settlement in one litigation matter *[tool_result; why: Identifies that matter as the candidate matter]*
- action: Lists all files in the candidate matter's folder
- purpose: Finds the settlement agreement, exhibits and closing documents of the candidate matter

**i7**
- observation: The system prompt says to use goal tools for a long-running completion objective *[environment; why: The research task qualifies as such an objective]*
- observation: The task is a multi-step research question across a large corpus *[task; why: Makes it long-running rather than single-turn work]*
- action: Creates a goal to find, verify and deliver the shortest executed firm-negotiated non-compete with sources
- purpose: Tracks the completion objective for the session

**i8** (follows i5)
- observation: A background conversion job is producing the searchable text copy *[tool_result; why: Converted text can already be searched]*
- observation: The task asks for the shortest non-compete duration *[task; why: Calls for searching for restriction terms near short durations]*
- action: Runs regex greps over the searchable text copy for non-compete wording near short month/day durations, repeatedly narrowing to durations shorter than the candidates found so far
- purpose: Brings up every mention of a short restriction term across the corpus

**i9** (follows i6, i8)
- observation: Grep hits in the candidate matter describe a shorter modified non-compete agreed in a settlement *[tool_result; why: Points to the settlement agreement as the source of the signed terms]*
- observation: The candidate matter folder contains a settlement agreement marked execution version and an exhibit of modified covenant terms *[tool_result; why: Identifies which documents hold the operative terms]*
- action: Reads the execution-version agreement and its incorporated covenant exhibit in the searchable text copy
- purpose: Gets the exact operative duration, scope and dates of the modified restriction

**i10** (follows i9)
- observation: The task requires the agreement to be one the firm negotiated and executed itself *[task; why: The terms alone do not prove the firm's role or that the agreement was signed]*
- observation: The candidate matter has a matter closing memo and a signature tracker/closing checklist *[tool_result; why: These are the execution record to check]*
- action: Reads the candidate matter's closing memo and its signature tracker/closing checklist
- purpose: Confirms the firm's negotiating role and the actual execution of the agreement

**i11** (follows i9)
- observation: The signature pages of the execution-version agreement have blank signature and date lines for most parties *[tool_result; why: Leaves it unclear whether the document copy itself is signed]*
- action: Inspects the original .docx files of the agreement and its exhibit for embedded media (signature images) with a python zip check
- purpose: Finds out whether a signature-bearing copy exists in the corpus

**i12** (follows i8)
- observation: Grep hits show shorter (e.g. six-month) non-compete terms in diligence and strategy memos of other matters *[tool_result; why: These shorter-looking candidates could beat the candidate matter's term]*
- action: Opens the source memos of the shorter-looking candidates to see whose agreement the term belongs to and whether the firm negotiated and executed it
- purpose: Rules each shorter term in or out against the task's negotiated-and-executed criteria

**i13** (follows i8)
- observation: Grep hits show the firm negotiating employment non-compete terms in some matters without a clear executed agreement *[tool_result; why: Those negotiated terms count only if an agreement was executed]*
- action: Reads the termination letters, closing memos or withdrawal/dormancy correspondence of those matters
- purpose: Checks whether the negotiated agreements were ever executed

**i14** (follows i8)
- observation: Search hits show a settlement in another matter that voided an employee's non-compete entirely *[tool_result; why: This elimination precedent is less restrictive than any shorter term and needs checking]*
- action: Reads that settlement agreement's covenant provisions and checks its matter closing memo for negotiation and execution
- purpose: Confirms the elimination precedent was executed and sees how it differs from a shorter affirmative term

**i15** (follows i8)
- observation: A separation agreement for a departing principal contains a post-employment non-compete, and a shorter period was proposed during its negotiation *[tool_result; why: The shorter figure might be the agreed term or only a rejected proposal]*
- action: Checks that matter's closing memo for the negotiation history and execution of the separation agreement
- purpose: Finds out whether the executed term or only a rejected proposal was shorter

**i16** (follows i5, i8)
- observation: The background conversion job is reported complete *[tool_result; why: Earlier greps may have missed files that were not converted yet]*
- action: Collects the job output and re-runs short-duration non-compete greps over the fully converted text copy
- purpose: Makes sure no shorter candidate was missed in documents converted late

**i17** (follows i9, i12, i13, i14, i15)
- observation: The candidate matter's settlement sets the shortest restriction found in a firm-negotiated, executed agreement *[reasoning; why: Gives the bottom-line answer]*
- observation: All shorter-looking candidates come from third-party/legacy agreements, rejected proposals or unexecuted negotiations *[reasoning; why: Supports stating that no shorter qualifying term exists]*
- observation: An executed settlement eliminated a non-compete entirely *[tool_result; why: Must be shown as a separate kind of outcome so the answer is not misleading]*
- action: Writes the deliverable: bottom line naming the qualifying precedent's duration and matter, quoted operative terms with scope and exceptions, a table of excluded shorter-looking candidates with reasons, and the elimination precedent distinguished as no-non-compete
- purpose: Answers the question with the signed terms and justifies why this term is the shortest qualifying one

**i18** (follows i10, i11)
- observation: The execution-version copy has blank signature lines and no embedded signature images *[tool_result; why: The document copy alone does not prove signing]*
- observation: The signature tracker still shows the agreement as awaiting execution *[tool_result; why: Conflicts with execution and must be reconciled]*
- observation: The later matter closing memo states the agreement was fully executed by all parties on its date *[tool_result; why: Is the affirmative evidence of execution]*
- action: In the deliverable, relies on the closing memo for execution and adds an explicit signature-copy limitation advising the reader to obtain the signed counterpart
- purpose: Presents the execution evidence honestly, with its gaps

**i19** (follows i9)
- observation: The modified restriction period runs from the employees' resignation date, which came before the agreement was executed *[tool_result; why: The time left at signing could be misread as the contractual duration]*
- action: States in the deliverable that the duration is measured from separation, not from execution
- purpose: Keeps the precedent's duration from being misreported

**i20** (follows i17)
- observation: The task asks for the matters/documents relied on in a self-contained file *[task; why: Requires sources to be listed]*
- action: Ends the deliverable with a numbered source register giving each document's corpus path and the relevant sections
- purpose: Makes the answer traceable to its sources

**i21** (follows i17)
- observation: The deliverable has been created in the output folder *[tool_result; why: There is now a file to check]*
- action: Reads back the written deliverable
- purpose: Checks the saved content before finishing

**i22** (follows i1)
- observation: A phase of the todo list has been finished *[reasoning; why: The todo status should match progress]*
- action: Updates the todo list, marking the identification phase done and later all phases completed
- purpose: Keeps the progress tracking current

**i23** (follows i7, i22)
- observation: All todo items are completed and the deliverable is written *[tool_result; why: The goal objective has been achieved]*
- observation: The system prompt requires calling get_goal before update_goal and copying its id and revision *[environment; why: Sets the order of the goal calls]*
- action: Calls get_goal and then update_goal with the returned id and revision to mark the goal complete
- purpose: Closes the session objective correctly

**i24** (follows i23)
- observation: The goal is marked complete *[tool_result; why: Work is finished and only reporting remains]*
- action: Gives a brief final message linking the deliverable and naming the qualifying precedent's duration and matter
- purpose: Hands off the result to the user

Role terms: **document corpus**: the read-only task documents folder of matter files (mostly .docx plus .eml/.xlsx/.pptx); **searchable text copy**: plain-text conversions of the corpus that the agent wrote to a scratch folder; **background conversion job**: the long-running background bash job that builds the searchable text copy; **candidate matter**: the matter whose documents show a modified, shorter post-employment restriction agreed in a settlement; **execution-version agreement**: the settlement agreement labelled 'Execution Version' plus its incorporated covenant exhibit in the candidate matter; **execution record**: documents that show whether and when an agreement was signed: matter closing memo, signature tracker, closing checklist; **qualifying precedent**: the shortest restriction found in an agreement the firm itself negotiated and executed; **shorter-looking candidate**: a mention of a shorter restriction that fails the task's criteria (third-party or legacy agreement, rejected proposal, unexecuted negotiation); **elimination precedent**: an executed settlement that voided a restriction entirely instead of shortening it; **deliverable**: the response.md answer file in the output folder

## Task 3: `firm-knowledge/tasks/179`

P1 `astra1`, P2 `astra2`; 31 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a three-step todo list (inventory records, trace relationships/analyze, write and verify report)
- purpose: Structures the long review into tracked phases

**i2**
- observation: The workspace has a read-only documents directory holding the task documents and an output directory for deliverables *[environment; why: Tells the agent where to look for source files]*
- action: Lists the workspace and globs every file under the documents directory
- purpose: Inventories the corpus layout before searching

**i3**
- observation: The system prompt offers goal tools for one long-running completion objective *[environment; why: Makes a goal the expected way to track the main objective]*
- observation: The task asks for a full review across the corpus written to a single report *[task; why: This is a long-running objective rather than routine single-turn work]*
- action: Creates a goal whose objective is to produce the sourced report in the output directory
- purpose: Arms completion tracking for the deliverable

**i4**
- observation: The corpus consists mostly of .docx/.xlsx/.pptx/.eml files spread across many matter folders *[tool_result; why: Binary office formats cannot be searched or read directly]*
- observation: The read tool opens plain text only; office files must be converted to text first *[environment; why: Requires conversion before reading or grepping]*
- action: Runs a Python script that bulk-converts every source document into a mirrored plain-text tree in scratch
- purpose: Makes the whole corpus searchable with grep and readable with read

**i5** (follows i4)
- observation: A converted text corpus of all documents exists in scratch *[tool_result; why: Provides the searchable target]*
- observation: The task names the target fund *[task; why: Supplies the search term]*
- action: Greps the converted text corpus for the target fund's distinctive name
- purpose: Finds every document that references the target fund

**i6** (follows i5)
- observation: Name hits include engagement letters stating that a client company is a portfolio company of the target fund *[tool_result; why: Reveals a standard relationship phrase that identifies portfolio-company clients]*
- observation: Name hits also include many unrelated entities sharing the brand word *[tool_result; why: Shows a plain name search is too noisy]*
- action: Greps engagement letters for the portfolio-company relationship phrase and for sibling fund numerals
- purpose: Isolates matters whose client is formally tied to the target fund

**i7** (follows i6)
- observation: Relationship-phrase hits cluster in a few matter groups (one sponsor group plus several portfolio-company groups) *[tool_result; why: Defines the set of matter groups to review in full]*
- action: Scripts an extract of the opening section of every engagement letter in those matter groups into a scratch packet, then reads it
- purpose: Captures client identity, scope and relationship statements for every relevant matter in one pass

**i8** (follows i7)
- observation: The sponsor matter group contains several matters, each with an engagement letter and/or conflicts memo *[tool_result; why: These documents state who the firm's client is on each sponsor matter]*
- action: Reads the engagement letters and conflicts memos of the sponsor matters
- purpose: Establishes which sponsor entity is the client and the scope of each sponsor matter

**i9** (follows i5)
- observation: The task asks for everything done across the target fund's funds, not just the one fund *[task; why: Requires checking for related fund vehicles]*
- action: Greps the corpus for sibling fund vehicles of the same sponsor family (other fund numerals)
- purpose: Detects any separate mandates for related funds

**i10** (follows i8)
- observation: A sponsor engagement letter names specific fund holdings to be transferred into a continuation vehicle *[tool_result; why: These holdings are further portfolio companies that may have firm records]*
- action: Greps engagement letters for the continuation-vehicle holdings' names
- purpose: Checks whether the firm separately represents those holdings

**i11** (follows i7)
- observation: The full list of matters in the sponsor and portfolio-company groups is known *[tool_result; why: Each matter's outcome must be established]*
- observation: Matter folders contain files named for closing, termination, close-out, status or dormancy *[tool_result; why: These file names identify where outcomes are recorded]*
- action: Locates status documents per matter by filtering file paths on closing/status/termination/dormancy keywords
- purpose: Finds the outcome record for each matter

**i12** (follows i11)
- observation: A status document has been located for most matters in the relevant groups *[tool_result; why: Provides the document to read for each matter's outcome]*
- action: Reads the leading section of each matter's main status document (closing memo/letter, termination memo, close-out letter, dormancy memo)
- purpose: Classifies each matter as completed, terminated, dormant or unconfirmed

**i13** (follows i12)
- observation: A matter's closing memorandum carries a placeholder closing date or otherwise leaves completion uncertain *[tool_result; why: The memo alone cannot confirm that the deal closed]*
- action: Reads that matter's closing checklist to verify item statuses
- purpose: Confirms or qualifies the matter's closed status from item-level evidence

**i14** (follows i12)
- observation: A sponsor matter's closing checklist has a status legend (draft/under review/executed/outstanding) per item *[tool_result; why: Item statuses determine whether the package was actually executed]*
- action: Greps that checklist for status and execution markers
- purpose: Determines whether the sponsor package was executed or remains open

**i15** (follows i8)
- observation: A sponsor tax-structuring matter folder contains a correspondence email delivering the main memorandum *[tool_result; why: The delivery email shows what work was actually delivered]*
- action: Reads the memorandum-delivery email for that sponsor matter
- purpose: Confirms the deliverable and its key recommendations

**i16** (follows i7)
- observation: Relevant matter folders contain conflicts memos *[tool_result; why: The review is a conflicts review, so clearance records must be checked]*
- action: Greps conflicts memos for prior/current representation, former/current client, waiver and consent language
- purpose: Extracts what each clearance record says about existing relationships and waivers

**i17** (follows i16)
- observation: A portfolio-company conflicts memo reports no prior representation and calls the client new *[tool_result; why: Conflicts with the firm's own records]*
- observation: Other matters for that same client exist in the corpus *[tool_result; why: Shows the clearance statement is inconsistent with the record]*
- action: Flags the inconsistent clearance statements and frames the deliverable as a relationship inventory, not a conflicts clearance
- purpose: Avoids presenting unreliable clearance records as cleared conflicts

**i18** (follows i12)
- observation: Records for the portfolio-company clients show inconsistent identifiers (e.g. EINs) and name different majority sponsors *[tool_result; why: The same-named entities may not be the same legal entity]*
- action: Decides not to treat every same-named record as one entity and to flag the identifier/ownership discrepancies
- purpose: Prevents a false single corporate-family chronology

**i19** (follows i7)
- observation: Engagement letters for portfolio-company clients name responsible and billing partners *[tool_result; why: Supplies the firm contacts for each matter]*
- action: Extracts responsible/billing partner lines from the engagement records of the relevant matters
- purpose: Records firm staffing for the matter inventory

**i20** (follows i9)
- observation: Sibling fund vehicles appear only as a predecessor fund or in an engagement's affiliate exclusion list *[tool_result; why: Shows no separate mandate for them]*
- action: States in the report that no separate mandate for the sibling funds was found and their mentions are not work performed
- purpose: Avoids inflating the relationship with unsupported matters

**i21** (follows i10)
- observation: A continuation-vehicle holding has a name similar to a portfolio-company client *[tool_result; why: Risk of conflating two different companies]*
- action: Explicitly distinguishes the similarly named holding from the portfolio-company client in the report
- purpose: Prevents entity confusion in conflicts analysis

**i22** (follows i8)
- observation: A sponsor matter's status memo records it as dormant with no definitive agreements or funding for the proposed investment *[tool_result; why: The target never became a holding]*
- action: Reports that proposed investment target as an unclosed/proposed investment, not a portfolio holding
- purpose: Keeps the portfolio list accurate

**i23** (follows i8)
- observation: Sponsor engagement letters name different entities as client (the fund, its GP, its management company, a sponsored SPAC) *[tool_result; why: The target fund is not the client on every sponsor matter]*
- observation: A closing letter confirms a fund investment closed, with the investee separately represented *[tool_result; why: The investee is a holding, not a firm client]*
- action: Reports, per sponsor matter, which entity is the firm's client and that investees are holdings rather than firm clients
- purpose: Sets correct representation boundaries for conflicts purposes

**i24** (follows i12)
- observation: Closing records list post-closing obligations and open follow-up items for completed matters *[tool_result; why: Documented follow-ups are evidence-based development openings]*
- action: Writes cross-sell opportunities grounded in documented follow-ups and scope gaps, labeled as proposals not existing mandates
- purpose: Delivers the cross-sell part of the task without overclaiming

**i25** (follows i12, i17, i18)
- observation: A relative write path is saved under the output directory, and only output files are delivered *[environment; why: Determines how to save the deliverable]*
- observation: The task requires a single self-contained markdown report with findings, relied-on documents and reasoning *[task; why: Defines the report's required content]*
- action: Writes response.md with an executive summary, full matter inventory, conflicts flags, cross-sell section and a source register of document paths
- purpose: Produces the deliverable

**i26** (follows i25)
- observation: The report has been written with a matter inventory table and a source register citing document paths *[tool_result; why: Counts and cited paths can be mechanically verified]*
- action: Runs a Python check on the report counting inventory rows/unique matter IDs and confirming each cited source path exists
- purpose: Verifies the report's matter count and citations

**i27** (follows i25)
- observation: The report file exists in the output directory *[tool_result; why: Can be re-read for review]*
- action: Reads back the opening section of the written report
- purpose: Reviews the executive findings as delivered

**i28** (follows i26)
- observation: The report has been written and checked *[tool_result; why: Marks the review phases as done]*
- action: Updates the todo list to mark all phases completed
- purpose: Closes out the tracked plan

**i29** (follows i28)
- observation: The system prompt requires calling get_goal before update_goal and copying its exact goal_id and revision *[environment; why: Defines the completion procedure]*
- observation: get_goal returned the active goal's id and revision *[tool_result; why: Supplies the values for update_goal]*
- action: Calls get_goal, then update_goal with that id and revision and action complete
- purpose: Marks the objective achieved

**i30** (follows i29)
- observation: The goal is marked complete *[tool_result; why: Work is finished]*
- action: Ends with a brief message linking response.md and summarizing matter count, client distinctions, conflict flags and cross-sell content
- purpose: Hands the deliverable to the user

**i31**
- observation: The task covers the target fund's funds and portfolio companies for a conflicts review *[task; why: Requires telling real client work apart from incidental mentions]*
- action: States a plan to separate confirmed client work from counterparty references and similarly named entities
- purpose: Sets the analytic frame for the review

Role terms: **target fund**: the fund entity named in the task as the subject of the review; **sponsor matters**: matters where the target fund or its GP/management company/sponsored vehicle is the firm's client; **portfolio-company clients**: companies that engagement letters describe as portfolio companies of the target fund, and that the firm represents; **matter groups**: families of matter folders sharing a client number prefix; **converted text corpus**: plain-text copies of all source documents written to a scratch directory; **status documents**: closing memos/letters, closing checklists, termination, close-out and dormancy memos that show a matter's outcome; **conflicts memos**: conflict-check / clearance memoranda inside matter folders; **sibling fund vehicles**: other numbered funds of the same sponsor family as the target fund; **continuation-vehicle holdings**: fund holdings named in a sponsor engagement as being moved into a continuation vehicle; **report**: the deliverable response.md in the output directory

## Task 4: `firm-knowledge/tasks/181`

P1 `astra1`, P2 `astra2`; 26 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a todo list that splits the work into finding sources, evaluating candidates, and writing the deliverable
- purpose: Plans and tracks the multi-stage research task

**i2**
- observation: The system prompt says task documents are in a documents directory in the workspace *[environment; why: Tells the agent where to look for the corpus]*
- action: Lists the workspace, globs every file in the document corpus, then lists its top-level folders
- purpose: Learns the layout and size of the document corpus

**i3** (follows i2)
- observation: The task asks about a specific litigation type and about staffing availability *[task; why: Gives the keywords to match against file names]*
- observation: The corpus is a large tree of matter folders *[tool_result; why: Reading everything is impractical, so targeted filename search is needed]*
- action: Globs file names for keywords from the task (the litigation type, staffing) and related terms
- purpose: Finds the matters and staffing documents most likely to be relevant

**i4** (follows i2)
- observation: Most files in the corpus are .docx (plus .eml), and the read tool opens plain text only *[environment; why: The documents must be turned into text before grep/read can be used on them]*
- observation: The corpus has thousands of documents *[tool_result; why: Converting them one by one with parse-doc would be too slow, so a bulk extraction is needed]*
- action: Runs a Python script that bulk-extracts the text of all docx/eml files into a scratch text corpus that mirrors the folder structure
- purpose: Makes the whole corpus searchable with grep and readable with read

**i5** (follows i3)
- observation: Filename hits for the litigation keyword cluster in a few matter folders *[tool_result; why: Points to the matter folders worth listing in full]*
- action: Lists all files in the matter folders that had keyword filename hits
- purpose: Sees what each relevant matter contains (engagement, closing, work product)

**i6** (follows i4)
- observation: A text corpus of all documents now exists *[tool_result; why: Lets content grep work]*
- observation: Engagement documents state each matter's subject and staffing *[reasoning; why: Limiting grep to engagement files finds the relevant matters with little noise]*
- action: Greps engagement-named text files for phrases about the litigation type
- purpose: Lists every matter of that litigation type in the firm records

**i7** (follows i6)
- observation: The engagement grep found a relevant matter whose engagement letter has not been read yet *[tool_result; why: The engagement letter names the associates staffed on the matter]*
- action: Reads the staffing section of the engagement letters of the relevant matters
- purpose: Finds which associates were assigned to each relevant matter, and in what role

**i8** (follows i4)
- observation: A text corpus of all documents exists *[tool_result; why: Allows a corpus-wide proximity search]*
- observation: The task asks specifically about associates *[task; why: Pairing 'associate' with the litigation term finds people that engagement letters might miss]*
- action: Greps the whole text corpus for 'associate' near the litigation-type term
- purpose: Catches candidate associates named outside the main matter files

**i9** (follows i8)
- observation: An associate is named as lead associate on a relevant litigation only in a matter folder of conflicts/intake records *[tool_result; why: Marks a candidate with no standalone litigation file whose role must be confirmed]*
- action: Searches for and reads the conflicts-file documents that name that associate and describe the underlying litigation
- purpose: Confirms the associate's role and the status of the underlying litigation

**i10**
- observation: The task asks who is available, not only who has experience *[task; why: Means staffing/capacity evidence has to be looked for]*
- action: Greps documents for staffing, capacity and availability terms (in matter admin files or near candidate names)
- purpose: Looks for direct evidence of associates' current workload or availability

**i11** (follows i5, i7)
- observation: Candidate associates are tied to specific relevant matters *[tool_result; why: Each matter's status bears on that associate's availability]*
- observation: Those matter folders contain closing letters/memos *[tool_result; why: Closing documents show whether the commitment has ended]*
- action: Reads the closing letters/memos of the candidates' matters
- purpose: Finds which candidate commitments are finished and when they ended

**i12** (follows i11)
- observation: Some relevant matters have no closing document, and the status reports read so far are older *[tool_result; why: Later documents are needed to judge the ongoing workload]*
- action: Reads the most recent status reports and trial/discovery planning memos of the still-active matters
- purpose: Finds how far along the candidates' ongoing commitments are and what is scheduled

**i13** (follows i7)
- observation: Candidate associates were found through staffing records naming their roles *[tool_result; why: A role label alone is weak evidence of real experience]*
- action: Reads memos and declarations the candidate associates wrote in the relevant matters
- purpose: Confirms each associate did substantive work in the litigation

**i14** (follows i12)
- observation: A status-report email for an active matter has an empty Date header *[tool_result; why: Its timing can't be cited reliably]*
- action: Decides to rely on dated documents (declaration, dated memo) rather than the undated email for the workload timeline
- purpose: Keeps cited dates for availability verifiable

**i15** (follows i9, i11, i13)
- observation: Every candidate associate is backed by staffing records and work product in relevant matters *[reasoning; why: Gives the content for the findings]*
- observation: The task requires one self-contained response.md with findings, sources and reasoning *[task; why: Sets the deliverable's format and location]*
- action: Writes response.md with a bottom line naming every candidate associate, a per-associate table of roles and work, and a list of matters/documents with file paths
- purpose: Delivers the answer with traceable sources

**i16** (follows i10)
- observation: No document gives current capacity, calendars or staffing clearance for the candidates *[tool_result; why: Availability cannot be confirmed from the records]*
- action: States in the deliverable that the list is an experience shortlist, not confirmation of current availability
- purpose: Avoids overstating what the evidence shows about availability

**i17** (follows i11, i12)
- observation: Closing dates for some candidate matters and dated ongoing/scheduled work for others *[tool_result; why: Lets the deliverable describe each candidate's known commitments]*
- action: Writes an availability section that summarizes, per associate, which matters are closed (with dates) and which show ongoing or scheduled workload
- purpose: Answers the availability part of the question as far as the evidence allows

**i18** (follows i11)
- observation: A matter's closing letter says the active phase is substantially complete but the formal engagement stays open until a later condition is met *[tool_result; why: The matter is not fully closed]*
- action: Reports that matter as wound down but conditionally open, not as proof of complete disengagement
- purpose: Characterizes the associates' remaining commitment accurately

**i19** (follows i12)
- observation: A planning memo schedules a trial for a future date, and no record shows the trial took place or how it ended *[tool_result; why: Planned work is not completed experience or freed capacity]*
- action: Presents the scheduled trial as trial-preparation responsibility, not as completed trial experience or proof the associates are now free
- purpose: Avoids reading a schedule as an outcome

**i20** (follows i9)
- observation: A 'closure' record in the conflicts folder concerns a declined prospective engagement, not the associate's continuing litigation *[tool_result; why: Could be misread as the candidate's matter being closed]*
- action: States in the deliverable that the closure concerns the declined engagement and that the candidate's litigation was still active
- purpose: Prevents misreading that candidate's availability

**i21** (follows i7)
- observation: Documents in one matter folder use an internal matter number different from the folder's number *[tool_result; why: Citations could confuse the reader about which matter is meant]*
- action: Notes the matter-number discrepancy in the sources section and identifies the matter by caption and docket
- purpose: Keeps the citations unambiguous

**i22** (follows i8)
- observation: Some records credit associates with related but different work (patent prosecution, licensing, transactional IP) or name partners and non-firm people *[tool_result; why: Those mentions must not be counted as experience in the litigation type]*
- action: States inclusion criteria: counts only actual involvement in the litigation type; excludes prosecution/licensing/transactional work, mere practice-group labels, partners, opposing counsel and client staff
- purpose: Makes the selection basis explicit and defensible

**i23** (follows i16)
- observation: Each relevant matter has a named supervising partner *[tool_result; why: They are the people who can confirm current workload]*
- observation: Current availability is not shown in the records *[reasoning; why: Confirmation has to come from outside the documents]*
- action: Recommends confirming each candidate's current commitments with the matter's supervising partner and running a fresh conflicts check before staffing
- purpose: Gives the user practical next steps for the availability question

**i24** (follows i15)
- observation: Each relevant matter involves a distinct technology area and side (plaintiff/defense) *[tool_result; why: Lets candidates be matched to kinds of new cases]*
- action: Gives each associate a subject-matter staffing fit and says these are matches, not availability rankings
- purpose: Makes the shortlist useful for staffing a new case

**i25** (follows i15)
- observation: The deliverable has just been written to the output directory *[tool_result; why: It needs a check after writing]*
- action: Reads back response.md from the output directory
- purpose: Checks the saved deliverable's content and format

**i26** (follows i25)
- observation: The deliverable has been written and checked *[tool_result; why: All todo items are done]*
- action: Marks all todos completed and ends with a short message pointing to response.md and its main findings
- purpose: Closes out the task and tells the user where the answer is

Role terms: **the task**: user request to identify associates with experience in a specific litigation type and their availability, delivered as response.md; **document corpus**: read-only collection of matter folders under the documents directory, mostly office files plus emails; **text corpus**: plain-text copies of all documents extracted by the agent into a scratch folder; **relevant matters**: matter folders whose documents concern the litigation type named in the task; **candidate associates**: associates the records tie to a relevant matter by role or work product; **staffing records**: engagement letters, intake forms and closing memos naming the team on a matter; **status documents**: closing letters/memos, status reports and planning memos that show whether a matter is ongoing or done; **supervising partner**: the partner responsible for a relevant matter; **deliverable**: response.md written to the output directory

## Task 5: `firm-knowledge/tasks/190`

P1 `astra1`, P2 `astra2`; 31 invariants.

**i1**
- observation: ∅ (always)
- action: Writes a three-item todo plan: identify the population, verify dates against sources, write the sourced report
- purpose: Structures the work into trackable phases

**i2**
- observation: A goal tool is available *[environment; why: The action uses this tool]*
- observation: The task asks for a complete, sourced deliverable *[task; why: This sets the objective the goal records]*
- action: Creates a goal restating the objective: find all closed deals, verify signing and actual closing dates, deliver a sourced response file
- purpose: Fixes the completion criterion at the start

**i3**
- observation: ∅ (always)
- action: Lists the documents directory to see how the corpus is laid out
- purpose: Discovers the per-matter folder structure and file types

**i4** (follows i3)
- observation: The corpus holds thousands of word-processing and email files spread across matter folders *[tool_result; why: These files cannot be grepped directly at this scale]*
- observation: There is no metadata or index file *[tool_result; why: Full-text search is the only way to classify matters]*
- action: Writes a Python script that extracts text from the word-processing files (zip XML) and the email files into a parallel text corpus
- purpose: Makes the whole corpus searchable with grep

**i5** (follows i4)
- observation: The corpus includes spreadsheet files, such as closing checklists, that hold key dates *[tool_result; why: Spreadsheet cell values must be turned into text before they can be searched]*
- action: Extracts spreadsheet cell values row by row into text files
- purpose: Makes the date fields in checklists searchable

**i6** (follows i4)
- observation: The conversion is running as a background job and a notice reports it finished *[tool_result; why: The agent must confirm the job succeeded before relying on the corpus]*
- action: Calls job_output to read the conversion counts and errors
- purpose: Checks that the text corpus is complete and error-free

**i7** (follows i4)
- observation: The task limits scope to deals of one named practice *[task; why: Matters must be classified by practice]*
- observation: The text corpus exists *[tool_result; why: It is the target of the search]*
- action: Greps the engagement-letter texts for practice-group/practice-area labels and the practice name
- purpose: Finds which matters belong to the requested practice

**i8** (follows i7)
- observation: Engagement letters name a responsible partner together with the practice group *[tool_result; why: Lines linking the responsible partner to the practice identify the practice's own matters]*
- action: Greps engagement letters for responsible-partner lines tied to the practice, together with transaction-type subject lines
- purpose: Builds the list of matters the practice led

**i9** (follows i7)
- observation: Each engagement letter's subject (Re:) line describes the matter's transaction *[tool_result; why: Subject lines let the agent sort deal matters from financing, tax, litigation and other work]*
- action: Pulls a compact list of engagement-letter subject lines across all matters
- purpose: Screens every matter by description in one pass

**i10** (follows i8, i9)
- observation: A list of about 33-34 candidate deal matter IDs has been settled from the engagement screening *[reasoning; why: The script needs these IDs to scope the review]*
- action: Runs a script that copies or compiles the candidate matters' texts into a scoped working set
- purpose: Restricts date verification to the candidate deal matters

**i11** (follows i4)
- observation: Broad date-phrase greps return truncated, noisy output *[tool_result; why: A tighter pattern is needed to find explicit consummation statements]*
- action: Greps with a regex for '(closed|consummated|...) on <Month> <day>, <year>'
- purpose: Finds prose statements of when a transaction actually closed

**i12** (follows i5)
- observation: Closing checklists are spreadsheets with labelled key-date fields *[tool_result; why: Searching on field labels pulls signing and closing dates directly]*
- action: Greps the checklist/spreadsheet texts for labels such as Signing Date, Actual Closing Date and Closing Date
- purpose: Collects each candidate's recorded signing and closing dates

**i13** (follows i10)
- observation: For some candidate matters, screening shows no clear closing records or an unclear status *[tool_result; why: Their folders must be inspected to find status documents]*
- action: Globs the full folder listing of several unclear candidate matters in parallel
- purpose: Finds closing, termination or status documents for those matters

**i14** (follows i13)
- observation: Some candidate matters contain termination letters, dormancy memos or terminated-status memos *[tool_result; why: These documents may show the deal never closed]*
- action: Reads those termination and dormancy documents
- purpose: Confirms the deal was terminated or dormant so it can be excluded from the closed set

**i15** (follows i14)
- observation: A terminated deal's matter has a 'matter closing' memo recording administrative file closure *[tool_result; why: File closure must not be mistaken for deal consummation]*
- action: Treats the administrative matter closure as not a deal closing and lists the matter as terminated in the exclusions
- purpose: Keeps the closed-deal population free of false positives

**i16** (follows i10)
- observation: Candidate deals have closing checklists, closing memos or post-closing letters in their folders *[tool_result; why: These records can confirm the actual consummation date]*
- action: Reads the closing records of each likely closed deal to check signing and actual closing dates
- purpose: Verifies each date pair against a primary source

**i17** (follows i13)
- observation: A matter's folder contains an execution-version definitive agreement *[tool_result; why: Its 'dated as of' line is the authoritative signing date]*
- action: Reads the opening lines of the executed definitive agreement to confirm the signing date
- purpose: Bases the signing date on the agreement itself, not on secondary mentions

**i18** (follows i16)
- observation: Closing records show a scheduled/target/expected closing date and a later actual closing date *[tool_result; why: Only the actual date is valid for measuring time to close]*
- action: Uses the actual closing date, not the target date, for each deal's interval
- purpose: Gets an accurate measure of how long deals actually took

**i19** (follows i16)
- observation: A tender-offer deal's closing memo lists several milestones: offer commencement, definitive agreement execution, offer expiration, acceptance and merger *[tool_result; why: The correct milestones for signing and closing must be chosen]*
- action: Takes the definitive agreement execution date as signing and the acceptance/merger date as closing
- purpose: Stops the benchmark from counting from offer commencement or ending at expiration

**i20** (follows i16)
- observation: Some candidates' closing checklists still show in-progress or pending items and estimated closing dates *[tool_result; why: No confirmed consummation is shown for these matters]*
- action: Leaves those matters out of the confirmed closed set and lists them separately as not-verified or pending
- purpose: Includes only deals with documented actual closings, while staying transparent

**i21** (follows i8)
- observation: The population was built mainly from one spelling of the practice name *[reasoning; why: Matters using other wording could have been missed]*
- action: Runs a complementary case-insensitive grep for alternate practice wordings in engagement letters
- purpose: Checks the population for missed matters

**i22** (follows i21)
- observation: Some acquisition-related engagements may belong to a different practice or a specialist workstream (tax, antitrust, financing, special committee) *[tool_result; why: Practice membership decides inclusion]*
- action: Checks those engagement letters' responsible partner, practice and scope to rule them in or out
- purpose: Keeps the population to the requested practice's principal deals

**i23** (follows i1, i10)
- observation: The candidate deal population has been established *[reasoning; why: This marks the end of the identification phase]*
- action: Updates the todo list: population step completed, date verification in progress
- purpose: Tracks the move to the verification phase

**i24** (follows i16, i17, i18)
- observation: Verified signing and actual closing date pairs exist for each confirmed closed deal *[reasoning; why: These are the inputs to the benchmark calculation]*
- action: Runs a Python script that computes calendar days per deal plus mean, median, min, max and sum
- purpose: Produces exact benchmark statistics instead of mental arithmetic

**i25** (follows i24)
- observation: One confirmed closed deal is a joint venture rather than an acquisition or divestiture *[tool_result; why: Its inclusion is debatable for a deal-closing benchmark]*
- action: Also computes the mean and median with the joint venture left out
- purpose: Gives a sensitivity figure for a narrower definition of deal

**i26** (follows i24)
- observation: Dates have been verified and the statistics computed *[tool_result; why: Verification is done and writing can start]*
- action: Updates the todo list: verification completed, report writing in progress
- purpose: Tracks the move to the writing phase

**i27** (follows i24, i15, i20)
- observation: The task requires a self-contained markdown file with findings, the documents relied on and the reasoning *[task; why: This sets the required content of the deliverable]*
- observation: Benchmark statistics and the verified deal rows are available *[tool_result; why: They form the findings table and summary]*
- action: Writes the response file with summary stats, a per-deal table (matter, client/deal, type, signing, actual closing, days, source ref), method notes on target vs actual dates, per-deal source paths, and tables of excluded terminated/dormant/unverified matters
- purpose: Delivers a sourced, reproducible benchmark

**i28** (follows i27)
- observation: The response file has been written with cited document paths and a table of date rows *[tool_result; why: The citations and arithmetic can be checked mechanically]*
- action: Runs a Python check that every cited path exists, recomputes each row's day difference against the table, and confirms the row count, mean and median
- purpose: Catches citation and arithmetic errors before finishing

**i29** (follows i28)
- observation: The validation passed: no missing paths and the expected row count and stats *[tool_result; why: Confirms the deliverable is complete]*
- action: Marks all todo items completed
- purpose: Closes out the plan

**i30** (follows i2, i29)
- observation: The goal created at the start is still active *[tool_result; why: It must be marked complete once the deliverable is done]*
- action: Fetches the goal, then updates it with action complete
- purpose: Formally finishes the goal

**i31** (follows i30)
- observation: The goal is marked complete and the response file exists *[tool_result; why: Nothing remains but to report]*
- action: Sends a brief final message linking the response file and stating the number of closed deals and what the file contains
- purpose: Hands the deliverable over to the user

Role terms: **document corpus**: the supplied folder of matter documents (word-processing, spreadsheet and email files) without a metadata index; **text corpus**: plain-text copies of the corpus files that the agent made so it could search them; **engagement letter**: the per-matter document that states the matter's subject, practice group and responsible partner; **candidate deal matters**: matters provisionally identified as belonging to the practice the task asks about; **closing records**: closing checklists, closing memos, post-closing letters/emails and closing certificates for a matter; **definitive agreement**: the executed principal transaction agreement whose date is the signing date; **confirmed closed deals**: candidate deals whose signing and actual closing dates are both backed by documents; **response file**: the markdown deliverable the task asks for; **goal tool**: the create_goal/get_goal/update_goal tools available to the agent

## Task 6: `firm-knowledge/tasks/209`

P1 `astra1`, P2 `astra2`; 21 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a three-step todo plan: locate opening dates and status evidence, compare eligible entities, write the deliverable
- purpose: Structures the research and reporting work

**i2**
- observation: The system prompt says the workspace holds a documents folder (task documents) and an output folder *[environment; why: Tells the agent where the records to search are]*
- action: Lists the workspace, then globs the entire record collection
- purpose: Learns how the records are laid out before searching

**i3** (follows i2)
- observation: The record collection is a set of per-entity folders of office documents (.docx/.xlsx/.eml) *[tool_result; why: No central register is visible, so one has to be searched for]*
- observation: The task asks for the oldest still-open item on a docket *[task; why: A docket or register file would answer it directly]*
- action: Globs for plain structured files (csv/json/md/txt) and for files whose names suggest a docket
- purpose: Looks for a central docket or register before going through each entity

**i4** (follows i3)
- observation: No plain-text or structured register file exists; docket-named files belong to individual entities *[tool_result; why: Shows that every entity's documents have to be searched]*
- observation: The read tool opens only plain text; office files need conversion *[environment; why: Content search needs text versions]*
- observation: The collection holds thousands of .docx/.eml files across hundreds of entity folders *[tool_result; why: Too many files to convert one by one]*
- action: Starts a background Python job that converts every .docx and .eml file to text in a scratch folder, keeping the folder structure
- purpose: Builds a converted text corpus that can be searched

**i5** (follows i4)
- observation: The background conversion job has started writing the converted text corpus *[tool_result; why: Text is becoming searchable]*
- observation: The task asks when the entity opened *[task; why: Opening-date phrases are what to look for]*
- action: Greps the converted text corpus for opening-date phrases (e.g. 'date opened', 'matter opened', 'opened on')
- purpose: Finds where opening dates are recorded

**i6** (follows i5)
- observation: Corpus-wide opening-date greps return hundreds of noisy, truncated matches *[tool_result; why: Grepping alone cannot rank entities by opening date]*
- observation: Engagement letters and opening memos carry a date in their header lines *[tool_result; why: Gives a dependable per-entity opening date to extract]*
- action: Runs a Python script that pulls the first date from the header of engagement/opening documents and writes them, sorted by date, to a scratch file
- purpose: Builds an opening-date index to rank entities by age

**i7** (follows i6)
- observation: The opening-date index has been written to a scratch file *[tool_result; why: Its top rows are the oldest entities]*
- action: Reads the opening-date index from the top (oldest first)
- purpose: Gets the ordered list of candidates to check

**i8** (follows i7)
- observation: The earliest-dated entities by engagement header have been identified *[tool_result; why: The oldest entities have to be checked first]*
- observation: An old opening date counts only if the entity is still open (not shelved, not closed) *[task; why: Status must be checked before an entity can be the answer]*
- action: Globs the earliest candidates' folders and reads their status documents (closing memos, dormancy memos, status letters)
- purpose: Finds each candidate's current status, oldest first

**i9** (follows i8)
- observation: A candidate's status document marks it formally closed or dormant *[tool_result; why: Closed and dormant (shelved) entities are excluded by the task]*
- observation: Shelved files are excluded; files in closing posture count as open *[task; why: Sets which statuses rule a candidate out]*
- action: Excludes that candidate and moves on to check the next-oldest candidate's status documents
- purpose: Goes down the date-ordered list until a qualifying entity is found

**i10** (follows i8)
- observation: The earliest candidates' folders contain closing-checklist .xlsx files *[tool_result; why: Checklists may record whether the entity's file was closed]*
- observation: The bulk conversion did not cover .xlsx, and read cannot open office files *[environment; why: The spreadsheets need separate conversion]*
- action: Converts the candidates' closing-checklist spreadsheets to text with parse-doc (or a script) and reads them
- purpose: Gets status evidence held in spreadsheets

**i11** (follows i5)
- observation: Files still winding down in closing posture count as open *[task; why: Entities explicitly labelled as in closing are prime answer candidates]*
- action: Greps the whole converted text corpus for explicit status labels (e.g. 'status: closing', 'status: active', 'matter status')
- purpose: Finds entities that are explicitly recorded as still open or in closing

**i12** (follows i3)
- observation: No central docket record turned up among the files *[tool_result; why: Docket metadata might be hidden in document properties instead]*
- action: Inspects the package parts / docProps metadata of a sample .docx for administrative fields
- purpose: Checks whether document metadata holds opening dates or status

**i13** (follows i6)
- observation: The opening-date index was built only from files whose names match engagement/opening patterns *[reasoning; why: Some entities may have no file that matches and so are missing from the ranking]*
- action: Runs a script comparing the entities in the opening-date index with all entity folders and lists the uncovered ones
- purpose: Makes sure no entity is left out of the age comparison

**i14** (follows i13)
- observation: A short list of entities has no dated engagement header in the index *[tool_result; why: Their opening dates are unknown and could be older]*
- action: Looks at those uncovered entities' engagement/opening files directly for their opening dates
- purpose: Completes the age ranking

**i15** (follows i9, i11)
- observation: An entity's closing-phase documents show it is in closing, with its opening date later than the already-excluded older entities *[tool_result; why: Makes it the leading qualifying candidate]*
- action: Reads that candidate's internal status/outcome report, which records its open date and its status as Closing
- purpose: Gets authoritative evidence of the candidate's opening date and qualifying status

**i16** (follows i15)
- observation: The leading candidate's records give an opening date *[tool_result; why: The date should be confirmed in the engagement document]*
- action: Reads the candidate's engagement letter to confirm its effective opening date
- purpose: Checks the opening date against a second source

**i17** (follows i15)
- observation: The candidate's client closing letter has a section on formal closure of the matter *[tool_result; why: Shows whether closure is finished or still pending]*
- action: Reads the closure section of the candidate's client closing letter to confirm that formal closure still depends on outstanding items
- purpose: Confirms the entity is winding down (open), not already closed

**i18** (follows i4)
- observation: The system prompt says to collect still-relevant background jobs with job_output *[environment; why: Finished jobs have to be collected]*
- observation: A background conversion job has been reported finished *[tool_result; why: Its output can now be collected]*
- action: Calls job_output on the finished background job to collect its result
- purpose: Confirms the conversion finished and follows the job-tracking rule

**i19** (follows i15, i16, i17)
- observation: The candidate's status report records status Closing and an open date, confirmed by its engagement letter *[tool_result; why: The answer is verified]*
- observation: The older entities checked are documented as dormant or formally closed *[reasoning; why: Comparison is complete]*
- action: Marks the comparison todo completed and the writing todo in progress
- purpose: Moves from research to writing the deliverable

**i20** (follows i19)
- observation: The task asks for a single self-contained response.md with findings, the documents relied on, and reasoning *[task; why: Sets what the deliverable must contain]*
- observation: A relative write path is saved under the output folder *[environment; why: Writing response.md puts it where deliverables are collected]*
- observation: The verified candidate's opening date and Closing status, plus the excluded older dormant/closed entities, are known *[tool_result; why: Supplies the answer and the comparison checks]*
- action: Writes response.md: the answer entity and opening date first, why its closing status counts as open, a comparison of older entities excluded as dormant or closed, and the source document paths
- purpose: Delivers a sourced, self-contained answer

**i21** (follows i20)
- observation: response.md was created successfully *[tool_result; why: The deliverable is done]*
- action: Marks all todos completed and ends with a one-line message pointing to response.md
- purpose: Closes out the task

Role terms: **record collection**: the read-only document tree of per-entity (matter) folders given with the task; **converted text corpus**: plain-text copies of the office documents written by the agent into a scratch folder; **opening-date index**: a scratch file, built by script, listing each entity's earliest header date from its opening/engagement documents, sorted by date; **candidate**: an entity (matter) being checked as a possible answer, taken in order of opening date; **status document**: a closing memo, dormancy memo, status report or closing checklist that states an entity's current status; **qualifying status**: the status the task counts as eligible (active or still in closing posture, not shelved/dormant and not formally closed); **deliverable**: the markdown answer file the task asks for

## Task 7: `firm-knowledge/tasks/240`

P1 `astra1`, P2 `astra2`; 24 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a three-step todo plan: locate records, compare candidates and dates, write the sourced answer to the deliverable
- purpose: Structures the research before exploring

**i2** (follows i1)
- observation: The system prompt says task documents live under a documents directory in the workspace and deliverables go to output *[environment; why: Tells the agent where to look first]*
- action: Lists the workspace and globs every file under the documents directory, then lists its top-level folders
- purpose: Learns the document collection's layout (one folder per matter)

**i3** (follows i2)
- observation: The task asks for a matter of a given practice area with a given provision type in an executed agreement *[task; why: Supplies the task keywords for searching]*
- observation: Document filenames are descriptive and grouped by matter folder *[tool_result; why: Makes a filename keyword search useful]*
- action: Globs filenames for the task keywords (practice-area word and provision word)
- purpose: Finds files likely relevant to the provision across all matters

**i4** (follows i3)
- observation: The provision-keyword filename search returned a standalone agreement of the requested provision type in one matter *[tool_result; why: Points to a direct example of the provision to inspect]*
- action: Lists that matter's folder and converts/reads the standalone agreement and the matter's engagement letter
- purpose: Checks the agreement's date, parties and the matter's practice area

**i5** (follows i3)
- observation: Matters are identified by folder IDs found in the filename search results *[tool_result; why: Gives specific matter folders to enumerate]*
- action: Globs the full file listing of specific matter folders surfaced by the keyword search
- purpose: Sees each candidate matter's document inventory (engagement, closing, transaction documents)

**i6** (follows i2)
- observation: Most documents are .docx and the read tool only opens plain text; parse-doc/pandoc are available *[environment; why: Requires conversion before text search]*
- observation: The collection has hundreds of matters *[tool_result; why: Makes a bulk, background conversion worthwhile]*
- action: Starts a background bulk pandoc conversion of administrative documents (engagement, opening, closing files) into a scratch text folder
- purpose: Builds a searchable converted text corpus to screen matters by practice area

**i7** (follows i6)
- observation: A runtime message reports that a background conversion job finished *[environment; why: Signals the job's output is ready to collect]*
- action: Calls job_output for the finished job and checks it converted without errors
- purpose: Confirms the converted text corpus is complete before searching it

**i8** (follows i7)
- observation: The converted text corpus of engagement/admin documents is available *[tool_result; why: Provides the text to search]*
- observation: The task requires the matter to belong to a specific practice area *[task; why: Requires identifying which matters are that practice's]*
- action: Greps the converted engagement documents for practice-group/department markers of the named practice (and its partners)
- purpose: Identifies the candidate Tax matters

**i9** (follows i7)
- observation: The converted text corpus is available *[tool_result; why: Provides the text to search]*
- action: Greps the converted corpus for phrases of the requested provision type
- purpose: Finds which matters' records mention the provision

**i10** (follows i8)
- observation: The practice-area grep listed engagement letters of several possible Tax matters *[tool_result; why: Gives the documents whose headers show date and subject]*
- action: Reads the opening part of candidate matters' engagement letters
- purpose: Checks each matter's date, subject and whether it is really a Tax engagement

**i11** (follows i8, i10)
- observation: A set of candidate Tax matters has been identified *[reasoning; why: Defines which matters need full-text coverage]*
- observation: Only admin documents of those matters were converted so far *[tool_result; why: Transaction documents still need conversion to be searched]*
- action: Starts a background conversion of all .docx documents of the listed candidate Tax matters
- purpose: Makes every document of each candidate searchable for the provision

**i12** (follows i11, i7)
- observation: The full-document conversion of the candidate Tax matters has completed *[tool_result; why: Enables per-matter searches]*
- action: Greps each candidate (especially newer) Tax matter's converted folder for the provision terms
- purpose: Checks whether any newer candidate has the provision in an executed agreement

**i13** (follows i9)
- observation: Provision-keyword hits in the leading candidate matter's summary memos mention an escrow securing the provision under the main deal agreement *[tool_result; why: Indicates closing evidence of an operative provision]*
- action: Reads the leading candidate's closing memorandum, including its section on the escrow for the provision
- purpose: Obtains closing-date evidence that the provision was in the signed deal agreement

**i14** (follows i5)
- observation: The leading candidate's folder contains an execution-version ancillary agreement *[tool_result; why: Is a signed document that may reference the provision]*
- action: Converts/greps and reads the ancillary executed agreement for its provision cross-reference and execution date
- purpose: Corroborates the provision with contractual text in an executed document

**i15** (follows i13)
- observation: The leading candidate's matter summary memo is available and describes the engagement *[tool_result; why: Holds the timeline of signing and execution events]*
- action: Greps/reads the matter summary memo for the main deal agreement's signing date and the ancillary agreement's execution at closing
- purpose: Establishes that the deal agreement was actually signed, not just drafted

**i16** (follows i12)
- observation: A newer candidate matter contains an agreement file whose name marks it as a draft and which contains provision-type language *[tool_result; why: Needs its execution status checked before it can be excluded or accepted]*
- action: Reads/greps the draft agreement's header for draft legend and execution date
- purpose: Confirms it is unexecuted (draft, blank/target execution date) and so does not qualify

**i17** (follows i12)
- observation: Provision searches in other newer candidate matters found no executed agreement with the provision *[tool_result; why: Requires checking what those matters actually are/status to justify excluding them]*
- action: Reads status/scope documents of newer candidate matters (ruling-request, scoping or advisory engagements)
- purpose: Documents why newer matters lack an executed agreement with the provision

**i18** (follows i4)
- observation: The older precedent matter's standalone agreement is dated as of a signing date *[tool_result; why: Execution still needs confirmation from closing records]*
- action: Reads the older precedent matter's closing index entry for that agreement
- purpose: Confirms the standalone agreement was executed and delivered at closing

**i19** (follows i1)
- observation: Before writing, the agent finishes the comparison of candidates *[reasoning; why: Marks the transition to the writing step]*
- action: Updates the todo list marking research/comparison completed and writing in progress
- purpose: Tracks progress to the deliverable step

**i20** (follows i13, i14, i15)
- observation: The leading candidate matter has closing-memo evidence and a summary-memo signing date showing the provision in a signed deal agreement *[tool_result; why: Supports naming it as the most recent qualifying matter]*
- observation: The signed main deal agreement itself is not in the files and the only provision markup is a draft *[tool_result; why: Requires a caveat on what can be cited as executed text]*
- action: Writes the deliverable naming the leading candidate matter, linking the closing memorandum, summary memo and ancillary executed agreement as evidence, with a caveat that the draft markup is not the executed clause
- purpose: Answers which matter and which document evidences the provision

**i21** (follows i16, i17)
- observation: Newer candidate matters only have drafts, target dates, or ruling/advisory work without an executed agreement with the provision *[tool_result; why: Justifies why they do not displace the leading candidate]*
- action: Includes in the deliverable a table of newer Tax candidates with the documents reviewed and why each is excluded
- purpose: Shows the recency comparison and reasoning

**i22** (follows i18)
- observation: An older precedent matter has a standalone executed agreement of the requested provision type confirmed by its closing records *[tool_result; why: Offers directly usable executed text for the user's drafting]*
- action: Mentions the older precedent matter and its standalone agreement in the deliverable as an earlier, directly executed precedent
- purpose: Gives the user operative executed wording while keeping the recency answer

**i23** (follows i20)
- observation: The deliverable contains relative markdown links to source documents *[tool_result; why: Links might not resolve and need checking]*
- action: Runs a script that extracts the deliverable's links and checks each target file exists
- purpose: Verifies the cited documents resolve (zero missing)

**i24** (follows i23)
- observation: Link check reported no missing links *[tool_result; why: Confirms the deliverable is complete]*
- action: Marks all todos completed and ends with a brief message pointing to the deliverable
- purpose: Closes out the task

Role terms: **task keywords**: the subject words of the question (the practice area and the provision type) used for filename/content searches; **candidate Tax matters**: matters identified as belonging to the practice area named in the task; **leading candidate matter**: the candidate Tax matter whose records show the provision in a signed/closed deal and that ends up as the answer; **newer candidate matter**: a candidate Tax matter dated later than the leading candidate that must be ruled out; **older precedent matter**: an earlier Tax matter holding a standalone executed agreement of the requested provision type; **converted text corpus**: plain-text/markdown copies of .docx files written into a scratch folder; **matter summary memo**: a close-out or lessons-learned memorandum that records a matter's timeline and execution events; **closing memorandum**: a closing-date memo that records closing events such as an escrow securing the provision; **ancillary executed agreement**: an execution-version agreement in the leading matter that cross-references the provision in the main deal agreement; **deliverable**: the response markdown file in the output directory

## Task 8: `firm-knowledge/tasks/243`

P1 `astra1`, P2 `astra2`; 28 invariants.

**i1**
- observation: The task asks for a count and list of matters in a practice group with a specific event, written to a markdown file *[task; why: defines the phases to plan]*
- action: Creates a todo list with three phases: identify practice attribution, verify the target event, write the deliverable
- purpose: structures the work into attribution, verification and reporting

**i2**
- observation: ∅ (always)
- action: Lists the workspace and globs the whole documents directory
- purpose: learns the layout and file types of the matter files

**i3** (follows i2)
- observation: Matter files include plain-text email files *[tool_result; why: emails can be grepped directly before conversion]*
- observation: The task names the practice group and the target event *[task; why: provides the search terms]*
- action: Globs filenames containing the event keyword and greps the raw email files for the practice-group name
- purpose: gets a quick first set of candidate matters and event documents

**i4** (follows i2)
- observation: The read tool opens only plain text; office files must be converted *[environment; why: the office documents cannot be searched or read as-is]*
- observation: Most matter files are thousands of .docx documents *[tool_result; why: bulk conversion is needed rather than per-file parsing]*
- action: Bulk-extracts text from all .docx files with a Python script into a scratch text corpus
- purpose: makes every Word document searchable with grep

**i5** (follows i4)
- observation: The first conversion left spreadsheets and presentations unconverted *[tool_result; why: those files could hold practice attributions not yet searched]*
- action: Converts the remaining spreadsheet and presentation files to text and greps them for the practice-group name
- purpose: ensures attribution search covers every file type

**i6** (follows i4)
- observation: A scratch text corpus of the matter files exists *[tool_result; why: enables content search]*
- action: Greps the scratch text corpus for the practice-group name
- purpose: finds all documents mentioning the practice group

**i7** (follows i6)
- observation: The practice-name grep returned hundreds of matches and was truncated *[tool_result; why: output too large to identify attributions]*
- action: Re-greps with patterns targeting practice-group field labels or line-start occurrences of the name
- purpose: isolates explicit practice-attribution lines from signatures and prose

**i8** (follows i7)
- observation: Practice-name greps over the whole corpus remain truncated *[tool_result; why: need complete coverage of all matters]*
- action: Splits the practice-name grep by matter-number ranges via include globs
- purpose: gets complete, untruncated results per range of matters

**i9** (follows i7)
- observation: Grep hits show the practice-group name in matter summary/opening/intake documents *[tool_result; why: these documents may carry an explicit classification field]*
- action: Reads matter summary, opening and status documents of matters with such hits
- purpose: checks the explicit practice classification of each matter

**i10** (follows i9)
- observation: A matter's opening memo describes its primary practice as another area despite a practice-group partner leading it *[tool_result; why: lawyer affiliation alone does not set matter attribution]*
- action: Excludes that matter from the practice group's count and records why
- purpose: follows the matter-level attribution the task specifies

**i11** (follows i9)
- observation: A matter's administrative record classifies it in the practice group although its responsible partner belongs to another practice *[tool_result; why: explicit classification takes precedence over staffing]*
- action: Includes that matter as attributed to the practice group
- purpose: applies explicit classification over cross-practice staffing

**i12** (follows i9)
- observation: A candidate matter has no classification field *[tool_result; why: attribution must come from other evidence]*
- action: Reads the matter's engagement letter and correspondence signatures to establish practice attribution
- purpose: attributes matters lacking an administrative label

**i13** (follows i3)
- observation: The documents use two variants of the practice-group name *[tool_result; why: both labels refer to the same group]*
- action: Treats both name variants as the same practice group
- purpose: avoids missing matters labelled with the variant name

**i14** (follows i9, i12)
- observation: A set of candidate matters attributed to the practice group is identified *[reasoning; why: defines where to look for the target event]*
- action: Greps the target-event terms scoped to the candidate matters' folders
- purpose: finds hold-related documents in each candidate matter

**i15** (follows i14)
- observation: Event-term grep hits in candidate matters point to hold notices, reminders, status reports and government letters *[tool_result; why: these may confirm or contradict issuance]*
- action: Reads the hold notices and confirming documents for each candidate matter
- purpose: verifies the hold was actually issued rather than planned

**i16** (follows i15)
- observation: A candidate matter's hold notice is marked DRAFT with an undated issuance placeholder *[tool_result; why: shows the hold was not yet issued]*
- observation: No other document confirms issuance for that matter *[tool_result; why: nothing overrides the draft status]*
- action: Excludes the matter for lacking an issued hold and lists it as an exclusion
- purpose: applies the 'issued' requirement strictly

**i17** (follows i14)
- observation: A candidate matter is attributed to the practice group *[reasoning; why: it would count if a hold existed]*
- observation: Event-term search of that matter found no issued hold *[tool_result; why: there is no issuance evidence]*
- action: Excludes the matter for lack of documented issuance and notes it in the report
- purpose: counts only matters with evidence of an issued hold

**i18** (follows i15)
- observation: A matter's later document records the hold as issued, distributed, acknowledged or completed *[tool_result; why: affirmative issuance evidence]*
- action: Counts the matter as qualifying, citing the issuance evidence
- purpose: bases inclusion on confirmed issuance, not plans or templates

**i19** (follows i18)
- observation: Some qualifying matters have several hold notices or reminders *[tool_result; why: risk of double counting]*
- action: Counts distinct matters once regardless of number of notices
- purpose: makes the count a matter count as the task asks

**i20** (follows i18)
- observation: Some qualifying matters are dormant or closed *[tool_result; why: status could seem to disqualify them]*
- observation: The task asks which matters involved the event *[task; why: historical involvement counts]*
- action: Keeps dormant and closed matters in the count
- purpose: interprets the question historically

**i21** (follows i18)
- observation: Documents within one qualifying matter give differing issuance dates *[tool_result; why: the record is inconsistent]*
- action: Notes the date inconsistency in the report while keeping the matter included
- purpose: is transparent about the record without changing the count

**i22** (follows i18)
- observation: A matter's documents use an internal reference number different from its folder identifier *[tool_result; why: could confuse which matter is meant]*
- action: Reports the matter under the folder identifier and mentions the internal reference
- purpose: keeps matter identification unambiguous

**i23** (follows i1)
- observation: Attribution and issuance checks for all candidate matters are done *[reasoning; why: the report can now be written]*
- action: Marks the verification phase complete in the todo list
- purpose: tracks progress before writing

**i24** (follows i16, i17, i18)
- observation: The qualifying and excluded matters with supporting documents are determined *[reasoning; why: content of the deliverable]*
- observation: The deliverable must be a self-contained markdown file with findings, documents relied on and reasoning *[task; why: sets the deliverable format]*
- action: Writes the deliverable with the count, a table of matters with issuance evidence, counting rules, documents relied on and exclusions
- purpose: produces the required answer file

**i25** (follows i24)
- observation: The deliverable has been written *[tool_result; why: it can now be checked]*
- action: Reads back the deliverable
- purpose: checks its content and citations

**i26** (follows i25)
- observation: The deliverable cites specific sections of source documents *[reasoning; why: those references must be accurate]*
- action: Re-checks cited source passages or section headings in the source documents
- purpose: verifies citation accuracy

**i27** (follows i25)
- observation: The read-back deliverable gives document paths whose base directory is ambiguous *[tool_result; why: readers might not locate the documents]*
- action: Edits the deliverable to clarify which directory the cited paths are relative to
- purpose: makes source references resolvable

**i28** (follows i27)
- observation: The deliverable is written and checked *[reasoning; why: the work is done]*
- action: Marks all todos complete and replies with a short summary giving the count and a link to the file
- purpose: delivers the answer

Role terms: **the practice group**: the firm practice group named in the task whose matters must be counted; **the target event**: the discovery event the task asks about (an issued litigation hold); **matter files**: the per-matter document folders in the read-only documents directory; **scratch text corpus**: plain-text copies of the office documents the agent extracted into a scratch directory; **candidate matters**: matters provisionally attributed to the practice group; **classification field**: an explicit administrative practice-group label in a matter summary, intake, opening or status document; **issuance evidence**: a document stating a hold was issued, distributed, acknowledged or implemented; **deliverable**: the markdown report file the task asks for

