# Proposed invariants

Run: `runs/im-mixed-flip-20261117T194118Z`. What F1 proposed from P1 and P2 of each task, before any check; their later fate (points, removal, rewording) is in report.md.

## Task 1: `contracts/banking/account-control-agreement-first-turn-redline/scenario-01`

P1 `run1`, P2 `run2`; 22 invariants.

**i1**
- observation: The task asks for two separate deliverables built from many source documents *[task; why: A multi-step, multi-deliverable job warrants an explicit plan]*
- action: Writes a todo list covering inspection, position-setting, building each deliverable and validation
- purpose: Structures the multi-step work before starting

**i2** (follows i1)
- observation: Task documents live in a documents directory under the workspace *[environment; why: Tells the agent where to look for the inputs]*
- action: Lists the files in the workspace/documents directory
- purpose: Discovers which source documents are available

**i3** (follows i2)
- observation: The source documents include .docx and .xlsx files *[tool_result; why: These formats cannot be opened with the plain-text read tool]*
- observation: The system prompt says to convert .docx/.xlsx to text with parse-doc *[environment; why: Names the conversion tool to use]*
- action: Converts every .docx and .xlsx source document to a text file in the workspace with parse-doc
- purpose: Makes the binary source documents readable

**i4** (follows i2)
- observation: The email source files (.eml) are plain text and parse-doc does not handle the eml format *[environment; why: Explains why emails are read as raw text instead of converted]*
- action: Reads the email source files as plain text (directly or via a plain copy)
- purpose: Gets the partner instructions, client directives and counterparty transmittal content

**i5** (follows i3)
- observation: Text versions of the playbook, original form, counterparty markup, agreement excerpts and spreadsheets exist in the workspace *[tool_result; why: They are now readable with the read tool]*
- action: Reads the converted playbook, original form, counterparty markup, agreement excerpts and spreadsheet texts
- purpose: Collects all the content needed to evaluate each counterparty change

**i6** (follows i5)
- observation: The read output for the counterparty markup was capped and gives an offset to continue from *[tool_result; why: The rest of the markup has not been seen yet]*
- action: Reads the remainder of the counterparty markup (and the original form) from the indicated offset
- purpose: Ensures every substantive change in the markup is seen

**i7** (follows i5)
- observation: The task requires a tracked-changes redline in DOCX format *[task; why: Dictates that changes must be real Word revisions]*
- observation: python-docx with low-level OXML access is available in the environment *[tool_result; why: Provides the means to write w:ins/w:del revision elements]*
- action: Writes a build script that generates the redline deliverable from scratch, wrapping deletions/insertions in w:del/w:ins revision elements with an author and date and enabling trackRevisions in settings
- purpose: Produces a genuine tracked-changes redline rather than visual formatting only

**i8** (follows i7)
- observation: The task asks to accept, reject or counter-propose on each substantive change *[task; why: Requires every change to be visibly dispositioned]*
- observation: The partner instructions enumerate the counterparty's substantive changes and require all of them to be addressed *[tool_result; why: Defines the full list of items to cover]*
- action: Includes in the redline a redline-convention legend and a summary table listing each counterparty change with its disposition (accept/reject/counter)
- purpose: Makes the response to every change explicit and readable even where tracked revisions are not rendered

**i9** (follows i8)
- observation: The instructions give client-directed limits (maximum period, minimum lookback, notice period, fee cap) for certain counter-proposals *[tool_result; why: These bounds define the exact counter values to propose]*
- action: Counter-proposes on those changes at exactly the client-directed limit values in both the redline and the cover note
- purpose: Stays within the client's authorized positions

**i10** (follows i8)
- observation: The instructions mark some counterparty changes as non-negotiable and to be rejected/restored *[tool_result; why: Determines which changes get reverted to the original form position]*
- observation: The instructions mark one change as lower priority and some terms (annual fees) as acceptable *[tool_result; why: Determines which changes are accepted or retained with clarification]*
- action: Rejects and restores original-form language for the non-negotiable items, while accepting or retaining with clarification/reservation the lower-priority and acceptable items
- purpose: Implements the instructed accept/reject/counter position for each change

**i11** (follows i8)
- observation: The instructions flag certain fallback positions as internal only and not to be shared with the counterparty *[tool_result; why: The cover note goes to counterparty counsel and must not disclose them]*
- action: Writes the cover note presenting firm positions without disclosing the internal fallback positions
- purpose: Protects the client's negotiating strategy

**i12** (follows i8)
- observation: The instructions name the cover-note addressees and copy recipients, and say to copy a bank contact if that contact was copied on the counterparty transmittal *[tool_result; why: Defines who the letter is addressed and copied to]*
- observation: The counterparty transmittal shows the bank contact on copy *[tool_result; why: Triggers the conditional copy instruction]*
- action: Addresses the cover note to the named counterparty counsel and copies the instructed recipients including the bank contact
- purpose: Follows the transmittal logistics in the instructions

**i13** (follows i8)
- observation: The instructions stress a closing/perfection deadline and the aggregate account balances relative to the proposed liability cap *[tool_result; why: Supplies the rationale facts the cover note must cite]*
- action: Cites the deadline and the aggregate balances in the cover note, addressing each change in a numbered section with the client's position and rationale
- purpose: Gives the counterparty a reasoned, issue-by-issue response

**i14** (follows i7)
- observation: Running the build script failed with a Python error *[tool_result; why: The deliverables were not produced]*
- action: Fixes the error in the build script and reruns it until both deliverables are created
- purpose: Gets the deliverables generated

**i15** (follows i14)
- observation: The build script reported that both deliverables were created in the output directory *[tool_result; why: There are now files to validate]*
- action: Extracts the text of both deliverables with parse-doc and counts w:ins/w:del elements in the redline's document.xml
- purpose: Verifies the content and that real tracked revisions exist

**i16** (follows i15)
- observation: The extracted text of a generated deliverable shows a content problem (missing operative change or unverified detail) *[tool_result; why: Identifies what needs correcting]*
- action: Makes a targeted correction to the deliverable (editing the script or document) and regenerates/saves it
- purpose: Fixes the content issue found on review

**i17** (follows i16)
- observation: A deliverable was just modified *[tool_result; why: The earlier validation no longer reflects the current file]*
- action: Re-extracts/re-checks the modified deliverable to confirm the correction
- purpose: Verifies the fix landed and nothing broke

**i18** (follows i15)
- observation: Both DOCX deliverables exist and libreoffice/pdfinfo are available *[tool_result; why: Allows checking how the documents render]*
- action: Converts both deliverables to PDF with headless libreoffice and checks the page counts with pdfinfo
- purpose: Confirms the documents open and render with a sensible length

**i19** (follows i18)
- observation: PDF renderings of both deliverables were produced *[tool_result; why: Pages can be rasterized for visual inspection]*
- action: Rasterizes the first page(s) with pdftoppm and views them with read_image
- purpose: Visually checks the layout and redline formatting

**i20** (follows i14)
- observation: Only files in the output directory are delivered *[environment; why: Requires confirming that the deliverables are in the right place]*
- action: Lists the output directory to confirm both deliverable files are present
- purpose: Ensures the deliverables will be collected

**i21** (follows i1, i19)
- observation: Both deliverables were created and validated *[tool_result; why: All planned tasks are done]*
- action: Marks all todo items completed
- purpose: Closes out the plan

**i22** (follows i21)
- observation: Both deliverables exist in the output directory and passed validation *[tool_result; why: There is a finished result to report]*
- action: Ends with a brief message linking both deliverables and summarizing how each change was handled
- purpose: Delivers the work to the user

Role terms: **source documents**: the read-only task input files (negotiation playbook, original form, counterparty markup, agreement excerpts, spreadsheets, emails); **counterparty markup**: the counterparty's first-turn revision of the original form agreement; **instruction emails**: the partner instruction email, client directive email and counterparty transmittal email; **client-directed limit**: a numeric maximum/minimum or cap the instructions say is the client's acceptable bound for a counter-proposal; **internal fallback position**: a negotiating fallback the instructions say must not be disclosed to the counterparty; **redline deliverable**: the second-turn tracked-changes DOCX output; **cover note deliverable**: the transmittal letter DOCX output addressing each change; **build script**: the Python (python-docx) code that generates both deliverables

## Task 2: `corporate-ma/draft-markup-of-stock-purchase-agreement-provisions`

P1 `run2`, P2 `run3`; 19 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a todo list with phases (inventory sources, extract/compare facts, draft memo, generate and validate the deliverable)
- purpose: Plans and tracks the multi-stage review

**i2**
- observation: ∅ (always)
- action: Lists all workspace files with a glob '*' before reading anything
- purpose: Takes inventory of the available source documents

**i3** (follows i2)
- observation: The source documents are .docx files *[tool_result; why: Determines that they cannot be opened with the plain-text read tool]*
- observation: The environment says to convert .docx to text with parse-doc via bash *[environment; why: Names the conversion tool to use]*
- action: Converts every .docx source document to text with parse-doc and saves the output as text files in the workspace
- purpose: Makes the documents readable and searchable with read/grep using line numbers

**i4** (follows i2)
- observation: The workspace contains an instruction email in plain-text (.eml) format *[tool_result; why: A plain-text file can be opened directly with the read tool]*
- action: Reads the full instruction email with the read tool
- purpose: Gets the priority issues, per-issue requirements and other instructions that drive the markup

**i5** (follows i3, i4)
- observation: The instruction email names specific topics/provisions to review *[tool_result; why: Gives the keywords to search for]*
- observation: Parsed text files of each source document are in the workspace *[tool_result; why: Gives the files to search]*
- action: Runs grep with patterns built from the issue topics and section headings over each parsed text file
- purpose: Finds the line locations of the relevant provisions and facts in every source

**i6** (follows i5)
- observation: grep results give line numbers of the relevant seller-draft sections *[tool_result; why: Tells which line ranges to open]*
- observation: The instructions require quoting the original seller-draft language for each issue *[tool_result; why: Requires the exact full text, not grep snippets]*
- action: Reads the seller-draft text file in large line-range chunks covering the flagged sections
- purpose: Obtains the exact original language to quote and revise

**i7** (follows i5)
- observation: A schedule in the seller draft states facts about a known liability matter (location, date) that differ from the diligence memo and term sheet *[tool_result; why: The mismatch must be resolved before the matter can be identified precisely in new provisions]*
- action: Flags the factual discrepancy in the memo and recommends checking the primary source before finalizing
- purpose: Prevents drafting a provision that misidentifies the matter

**i8** (follows i6)
- observation: The seller draft's general survival period is shorter than the period in the term sheet/playbook *[tool_result; why: Shows a deviation from agreed terms]*
- observation: The instruction email asks for other issues not on its list to be flagged as well *[tool_result; why: Allows adding issues beyond the listed priorities]*
- action: Adds the deviation as an extra issue in the memo with replacement language conforming to the term sheet
- purpose: Covers material deviations beyond the partner's list

**i9** (follows i6)
- observation: For each issue the instruction email requires: the quoted original language, full revised contract language, a commentary citing the source document, and a priority level *[tool_result; why: Sets the required structure of every issue entry]*
- observation: The instruction email asks for the memo to be organized by agreement article/section *[tool_result; why: Sets the overall organization]*
- action: Writes the full memo with an executive summary and, for each listed issue, the quoted seller language, full replacement text, a commentary citing term sheet/playbook/diligence memo sections and a priority, grouped by article
- purpose: Produces the draft-ready markup content in the required format

**i10** (follows i4)
- observation: The instruction email lists provisions that are fine as drafted and should not be marked up *[tool_result; why: Identifies provisions to leave alone]*
- action: Includes a dedicated section listing the provisions to leave unmarked, with the reason for each
- purpose: Follows the instruction and shows those provisions were reviewed on purpose

**i11** (follows i9)
- observation: The instruction email leaves some positions open for client discussion (closing condition vs covenant; minimum survival period vs longer statutory alternative) *[tool_result; why: These positions cannot be settled in the draft]*
- observation: It says to draft the minimum position and flag the longer alternative *[tool_result; why: Says which default to draft]*
- action: Drafts the default position and explicitly flags the alternatives as client decision/escalation points in the memo
- purpose: Lets the partner change position without redrafting

**i12** (follows i9)
- observation: The deliverable must be a .docx in the output directory, and only files there are delivered *[environment; why: Requires building a binary document and placing it correctly]*
- observation: Document-building tooling (python-docx / pandoc) is available through bash *[environment; why: Provides the way to build the .docx]*
- action: Keeps the memo source file in the workspace (outside output) and converts it with bash into the .docx deliverable in the output directory
- purpose: Produces the required deliverable without leaving extra files in the output

**i13** (follows i12)
- observation: The .docx deliverable was generated in the output directory *[tool_result; why: There is now a file to check]*
- action: Converts the generated deliverable back to text with parse-doc and reads the validation text
- purpose: Checks that the content rendered fully and correctly

**i14** (follows i13)
- observation: The validation text shows a content/formatting defect in the deliverable *[tool_result; why: Shows something that must be fixed before delivery]*
- action: Fixes the defect at its origin, in the memo source file or the build command, not in the .docx
- purpose: Makes the regenerated deliverable free of the defect

**i15** (follows i14)
- observation: An edit was rejected because the file had not been read in this session *[tool_result; why: The edit tool requires a prior read]*
- action: Reads the relevant part of the file, then repeats the same edit
- purpose: Meets the read-before-edit policy so the change goes through

**i16** (follows i14, i15)
- observation: The memo source file was edited after the last build *[tool_result; why: The deliverable is now out of date]*
- action: Rebuilds the .docx from the source and converts it to text again with parse-doc in one bash command
- purpose: Makes the delivered file match the corrected source and stay valid

**i17** (follows i16)
- observation: The final deliverable has been rebuilt and validated *[tool_result; why: Only the delivery check is left]*
- action: Globs the output directory to confirm it contains only the deliverable
- purpose: Makes sure the right file, and no scratch files, will be delivered

**i18** (follows i1, i17)
- observation: The deliverable is present in the output directory and validated *[tool_result; why: All planned phases are done]*
- action: Marks every todo item completed
- purpose: Closes out the task plan

**i19** (follows i18)
- observation: The deliverable is complete and in the output directory *[tool_result; why: There is a finished file to report]*
- action: Ends with a short message summarizing the memo's contents and linking to the .docx deliverable
- purpose: Hands the result to the user

Role terms: **source documents**: the task's reference files in the documents folder (seller draft agreement, playbook, term sheet, diligence memo) delivered as .docx; **instruction email**: the supervising partner's plain-text email listing priority issues, per-issue requirements, items to leave alone and open client questions; **parsed text files**: plain-text conversions of the source documents saved in the workspace; **seller draft**: the counterparty's draft agreement being marked up; **memo source file**: the workspace file holding the full memo content (a generator script or markdown) that is converted to the deliverable; **deliverable**: the required .docx memorandum saved in the output directory; **validation text**: the parse-doc text conversion of the generated deliverable

## Task 3: `firm-knowledge/tasks/111`

P1 `run2`, P2 `run3`; 15 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a todo list with steps: inventory sources, review executed agreements, determine/verify the largest, write the deliverable
- purpose: structures the multi-step research before starting

**i2** (follows i1)
- observation: The task asks for a firm-wide maximum across all records *[task; why: requires knowing the whole document set first]*
- observation: Task documents live under the workspace documents directory and glob is the tool for discovering files *[environment; why: determines how to inventory]*
- action: Runs a match-all glob to inventory the document corpus
- purpose: learns the folder/matter structure and file naming

**i3** (follows i2)
- observation: The inventory is very large and truncated, organised by matter folders with descriptive filenames *[tool_result; why: makes filename-based narrowing the efficient route]*
- observation: The question concerns settlements *[task; why: supplies the filename keywords]*
- action: Globs filenames across all folders for the task's key term and related terms (settlement, release)
- purpose: locates candidate settlement documents by name

**i4** (follows i2)
- observation: A glob result was truncated and its full list was stored in a spill file whose path is given *[tool_result; why: the spill file appears to hold the complete list]*
- action: Tries to read/grep the spill file
- purpose: get the complete untruncated file list

**i5** (follows i3, i4)
- observation: Accessing the spill file failed (denied / not found) *[tool_result; why: the full list must be obtained another way]*
- observation: The broad settlement filename glob was capped at 100 of more results *[tool_result; why: shows results are missing and need smaller queries]*
- action: Re-runs the settlement filename glob split by matter-number prefixes so each result fits under the cap
- purpose: obtains a complete list of settlement-related files

**i6** (follows i3)
- observation: Settlement file lists include executed-version agreements (names with execution/final/mutual release) alongside drafts, redlines, term sheets *[tool_result; why: identifies which documents define the counted amount]*
- observation: The task counts each settlement at the amount its executed agreement defines *[task; why: restricts reading to executed agreements]*
- observation: .docx files must be converted with parse-doc via bash *[environment; why: the agreements are docx]*
- action: Converts executed settlement agreements with parse-doc in bash and inspects their monetary terms
- purpose: extracts each executed agreement's defined settlement amount for comparison

**i7** (follows i3)
- observation: One matter shows the largest settlement-related figures among the hits seen so far (leading candidate) *[tool_result; why: singles out the matter to examine in depth]*
- action: Globs all files in the leading candidate's matter folder
- purpose: finds its executed agreement and corroborating documents

**i8** (follows i7)
- observation: The leading candidate's folder contains a final/execution-version settlement agreement *[tool_result; why: this is the controlling document for the amount]*
- action: Reads the leading candidate's executed agreement in full from its beginning (parties, caption, definitions, payment article)
- purpose: confirms the defined settlement amount, its components, case caption and date

**i9** (follows i7)
- observation: The leading candidate's folder contains a matter closing memorandum *[tool_result; why: it records the final disposition and settlement figure]*
- action: Converts and reads the matter closing memorandum as a corroborating document
- purpose: cross-checks the executed amount and that the settlement was completed

**i10** (follows i5, i6)
- observation: A leading candidate amount has been identified *[reasoning; why: defines the threshold other agreements must be checked against]*
- observation: Another executed settlement agreement in the file lists has not yet been reviewed and could exceed it *[tool_result; why: an unreviewed larger amount would change the answer]*
- action: Converts and checks the unreviewed settlement agreement's amounts
- purpose: rules out a larger executed settlement elsewhere

**i11** (follows i8)
- observation: The executed agreement defines a Settlement Amount and separately provides interest on deferred payments *[tool_result; why: two candidate totals exist]*
- observation: Other documents cite larger figures (claimed damages, collateral values) *[tool_result; why: these could be mistaken for the settlement figure]*
- observation: The task counts the amount the executed agreement defines *[task; why: decides which figure governs]*
- action: Decides to report the defined Settlement Amount, excluding interest, claimed damages and other non-defined figures
- purpose: applies the task's counting rule precisely

**i12** (follows i1)
- observation: Executed agreements were reviewed and the leading candidate confirmed *[reasoning; why: research steps are done]*
- action: Updates the todo list marking review steps completed before writing
- purpose: tracks progress toward the deliverable

**i13** (follows i11)
- observation: The largest executed settlement amount, matter, and case caption are confirmed *[reasoning; why: forms the answer]*
- observation: Task requires a self-contained response.md with findings, documents relied on and reasoning *[task; why: defines the deliverable's content]*
- action: Writes response.md with the answer, document paths relied on, the counting method (executed agreement controls; drafts, term sheets, claims, interest excluded) and cross-checks against other executed settlements
- purpose: produces the required deliverable

**i14** (follows i13)
- observation: The deliverable was written to the output directory *[tool_result; why: must be confirmed before finishing]*
- action: Reads back output/response.md
- purpose: verifies the deliverable's content and location

**i15** (follows i14)
- observation: The deliverable has been verified *[tool_result; why: all todo items are done]*
- action: Marks all todos completed and gives a brief completion message
- purpose: closes the task

Role terms: **document corpus**: the read-only task documents organised in per-matter folders; **executed agreement**: a settlement agreement marked as execution/final version (as opposed to drafts, redlines, term sheets); **leading candidate**: the matter/executed agreement showing the largest settlement figure found so far; **corroborating document**: a non-controlling document in the leading candidate's matter (closing memo, authority memo, term sheet, complaint) used to confirm the figure; **deliverable**: the response markdown file written to the output directory; **spill file**: temp file where a truncated tool result was stored, outside the workspace

## Task 4: `corporate-ma/draft-markup-of-transition-services-agreement-tsa`

P1 `run1`, P2 `run4`; 19 invariants.

**i1**
- observation: The task asks for a multi-step review producing two named .docx deliverables *[task; why: Makes the work a long-running objective rather than a single-turn reply]*
- observation: The system prompt says to use goal tools for one long-running completion objective *[environment; why: Tells the agent a goal tool exists for this kind of objective]*
- action: Creates a goal whose objective restates the review task and names both deliverable files in the output folder
- purpose: Tracks completion of the overall objective

**i2** (follows i1)
- observation: The task involves inspecting inputs, analysing issues, drafting two documents and validating them *[task; why: Supplies the phases the plan lists]*
- action: Writes a todo list covering inspection of the source documents, issue analysis, creation of the deliverables and validation, marking inspection in progress
- purpose: Structures the work into trackable phases

**i3**
- observation: The task refers to attached documents without listing their paths *[task; why: The agent must find the input files before reading them]*
- observation: The system prompt says to use the glob tool, not shell find, to discover files *[environment; why: Determines which tool is used for discovery]*
- action: Globs the workspace/documents folder to list the source documents
- purpose: Inventories the input files and their formats

**i4**
- observation: The system prompt forbids reading, searching or referencing the task configuration file *[environment; why: Breaking this rule automatically fails the task]*
- action: Notes that it must not read the task configuration and reads only the source documents
- purpose: Avoids an automatic rule-violation failure

**i5** (follows i3)
- observation: One source document is a plain-text email file *[tool_result; why: Plain-text files can be opened directly]*
- observation: The system prompt says the read tool opens plain-text files such as .eml *[environment; why: Determines that read is the right tool for it]*
- action: Opens the client-instructions email with the read tool
- purpose: Gets the supervising lawyer's assignment and priorities

**i6** (follows i3)
- observation: The other source documents are .docx files *[tool_result; why: They cannot be opened with read directly]*
- observation: The system prompt says to convert .docx to text with parse-doc in bash and that read takes offset/limit for large files *[environment; why: Points to converting into workspace text files that read can page through]*
- action: Runs parse-doc on each .docx source document and redirects the output into text files in the workspace
- purpose: Makes the full long documents readable in pages with read and searchable with grep

**i7** (follows i6)
- observation: The converted text files are long and a single read returns only part of a file *[tool_result; why: Unread parts need follow-up reads]*
- action: Reads the converted draft agreement and playbook text files with read in successive offset/limit chunks
- purpose: Covers each document in full before drafting the markup

**i8** (follows i7)
- observation: The draft agreement's fee schedule lists category fees and markups *[tool_result; why: One side of the comparison]*
- observation: The governing agreement's exhibit sets binding fee estimates and markups per category *[tool_result; why: The binding benchmark the draft must match]*
- action: Compares the draft's fee schedule to the governing agreement's fee table and flags the category whose markup or total is different
- purpose: Finds a fee discrepancy to correct in the redline

**i9** (follows i7)
- observation: The draft agreement's liability-cap formula is different from the cap required by the governing agreement *[tool_result; why: The conflict to quantify]*
- observation: The fee figures needed to apply both cap formulas are available *[tool_result; why: Needed to calculate dollar amounts]*
- action: Calculates the dollar liability exposure under the draft's cap and under the governing agreement's cap and compares them
- purpose: Puts a number on the most significant exposure for the memo and comments

**i10** (follows i8, i9)
- observation: Deliverables must be .docx files saved in the output folder, and files built with bash count as deliverables *[environment; why: Requires generating .docx with code rather than the markdown-only write tool]*
- observation: The python-docx library is usable in the environment *[tool_result; why: Confirms the generation approach will work]*
- action: Writes one Python generation script to the workspace through a bash heredoc that uses python-docx to build both deliverables into the output folder
- purpose: Produces both required .docx files programmatically and so they can be regenerated

**i11** (follows i10)
- observation: The task asks for a redline with annotated comments and a priority-tiered memo *[task; why: Sets the required markup and tiering features]*
- observation: The agent concluded it would show changes as visible formatting rather than native tracked changes *[reasoning; why: Sets how deletions and additions are shown]*
- action: Formats deletions as colored strikethrough and additions as colored underline, and adds shaded comment blocks giving a priority tier, the basis in the governing agreement or playbook, the risk to the client, and the negotiating position
- purpose: Makes the redline readable and ties each change to its authority and priority

**i12** (follows i10)
- observation: An edit on the generation script failed because the file had not been read first *[tool_result; why: The edit tool requires reading the file first]*
- action: Reads the relevant part of the generation script with the read tool, then retries the same edit
- purpose: Meets the read-before-edit rule so the change can be applied

**i13** (follows i10)
- observation: The generation script ran and reported creating both deliverables *[tool_result; why: There are outputs to validate]*
- action: Converts both generated deliverables to validation text with parse-doc and checks for the key issue terms and figures
- purpose: Confirms the main issues and numbers appear in the redline and memo

**i14** (follows i13)
- observation: The validation text shows a defect in a generated deliverable (duplicate comment identifiers / a memo date that conflicts with dates in the client instructions) *[tool_result; why: The defect has to be fixed at its source]*
- action: Fixes the defect in the generation script and reruns it to regenerate the deliverables
- purpose: Fixes the deliverables at their source

**i15** (follows i14)
- observation: The deliverables were regenerated after a fix *[tool_result; why: The fix must be confirmed in the actual output]*
- action: Re-extracts the regenerated deliverable text with parse-doc and checks that the fix is present
- purpose: Verifies the correction reached the delivered file

**i16** (follows i15)
- observation: Both deliverables exist as generated .docx files in the output folder *[tool_result; why: Their structural soundness and size can be checked]*
- action: Checks that the .docx files are structurally valid (rendering to PDF or ZIP integrity test) and lists their sizes
- purpose: Makes sure the delivered files open and are not corrupt

**i17** (follows i2, i16)
- observation: Both deliverables are generated and validated *[tool_result; why: All todo phases are done]*
- action: Marks all todo items completed
- purpose: Closes out the work plan

**i18** (follows i1, i17)
- observation: The system prompt says to call get_goal before update_goal and copy its exact goal_id and revision *[environment; why: update_goal needs the current id and revision]*
- observation: The goal objective has been achieved *[reasoning; why: A goal may be marked complete only when it is actually achieved]*
- action: Calls get_goal, then update_goal with the returned id and revision and action complete
- purpose: Formally closes the long-running goal

**i19** (follows i18)
- observation: Both deliverables were created in the output folder and validated *[tool_result; why: Gives the content of the final report]*
- action: Gives a final summary with links to both deliverables, the key issues addressed and the validation done
- purpose: Hands the result to the user

Role terms: **draft agreement**: the counterparty's draft contract the agent must mark up; **governing agreement**: the executed upstream agreement whose excerpts set binding terms the draft must conform to; **playbook**: the client's internal negotiating-position guide; **client instructions**: the plain-text email from the supervising lawyer describing the assignment; **source documents**: all task inputs in the documents folder (draft agreement, playbook, governing agreement excerpts, client instructions); **deliverables**: the two named .docx files (redline and priority-tiered memo) required in the output folder; **generation script**: the Python file the agent writes in the workspace to build both deliverables; **validation text**: plain-text extraction of the generated deliverables used for checking

## Task 5: `intellectual-property/review-data-processing-agreement-template-against-eu-and-us-requirements`

P1 `run1`, P2 `run2`; 21 invariants.

**i1**
- observation: The task asks to review several source documents and produce a single .docx deliverable *[task; why: A multi-phase deliverable motivates an explicit plan]*
- observation: A todo_write tool is available *[environment; why: The plan is recorded with this tool]*
- action: Creates a todo list with phases: read sources, analyze gaps, draft memo, generate and validate the docx
- purpose: Structures the multi-step work and tracks progress

**i2**
- observation: Task documents live in the documents directory of the workspace *[environment; why: Tells the agent where to look for the inputs]*
- action: Lists the workspace / documents directory to inventory the source documents
- purpose: Discovers which files and formats must be read

**i3** (follows i2)
- observation: Most source documents are .docx files *[tool_result; why: Determines that a conversion step is needed]*
- observation: The read tool only opens plain text; .docx must be converted with parse-doc via bash *[environment; why: Prescribes the conversion command]*
- action: Converts each .docx source document to text with parse-doc in bash
- purpose: Makes the document contents readable

**i4** (follows i3)
- observation: The key source documents (playbook, vendor template) are long, too long to take in from one output *[tool_result; why: Long text has to be saved and read in pages]*
- observation: The read tool supports offset/limit paging on workspace text files *[environment; why: Makes it possible to read saved text in chunks]*
- action: Redirects the parse-doc output into extracted text files in the workspace scratch area
- purpose: Allows systematic, paged reading of the full documents

**i5** (follows i4)
- observation: Extracted text files of the long documents exist in the workspace *[tool_result; why: They are the target of the paged reads]*
- action: Reads the extracted playbook and vendor template with the read tool using several offset/limit calls, including the later sections
- purpose: Covers every relevant section of the long documents, not just the first page

**i6** (follows i2)
- observation: The negotiation correspondence is a plain-text .eml file *[tool_result; why: Plain text needs no docx conversion]*
- action: Reads the email thread directly as text, without parse-doc
- purpose: Captures the counterparty's stated positions and timing

**i7** (follows i5)
- observation: The playbook marks certain contract terms as must-have / non-negotiable *[tool_result; why: Sets the benchmark the template is measured against]*
- observation: The vendor template is drafted for one regulatory regime only and lacks those must-have terms *[tool_result; why: A missing must-have term is a gap of the highest severity]*
- action: Classifies each missing must-have requirement as a top-tier execution-blocker finding in the memo
- purpose: Puts the findings in priority order by playbook severity

**i8** (follows i5)
- observation: The playbook requires the liability cap to be a multiple of annual fees, with uncapped carve-outs *[tool_result; why: Defines the required cap structure]*
- observation: The commercial terms give the annual fee amounts, split by region *[tool_result; why: Supplies the numbers for the calculation]*
- observation: The vendor template sets a low flat cap and a blanket exclusion of consequential damages *[tool_result; why: This is the gap being quantified]*
- action: Calculates the fee-based cap amounts (combined and per region) and recommends replacing the flat cap with them, plus carve-outs
- purpose: Gives a concrete redline position for the liability gap, based on the source numbers

**i9** (follows i5)
- observation: The data-flow description flags that a cross-border processor-to-subprocessor transfer and a remote-access transfer are not covered by the transfer mechanism the template selects *[tool_result; why: Identifies the transfer gaps to fix]*
- action: Includes a top-priority transfer finding that recommends the correct transfer module, a transfer impact assessment and handling of the remote-access scenario
- purpose: Fixes the invalid or missing international transfer mechanisms

**i10** (follows i5)
- observation: The vendor template's annex names a different operator for a facility than the data-flow description and commercial terms do *[tool_result; why: An inconsistency between documents needs correcting in the redline]*
- action: Flags the cross-document inconsistency about the facility operator as a finding and recommends correcting it
- purpose: Makes sure the agreement accurately describes the real processing footprint

**i11** (follows i6)
- observation: The negotiation correspondence shows the client insisting on contractual coordination mechanisms that the counterparty wants handled operationally *[tool_result; why: Points to a negotiation item that the redline must address]*
- action: Includes a recommendation for a contractual coordination protocol in the relevant template section
- purpose: Reflects the client's stated negotiation position in the memo

**i12**
- observation: The deliverable must be a .docx file *[task; why: Requires a docx generation library]*
- action: Checks that python-docx can be imported and prints its version
- purpose: Confirms the generation tool is available before writing the build script

**i13** (follows i12)
- observation: python-docx is installed *[tool_result; why: The build script relies on it]*
- observation: Deliverables must be saved in the output directory *[environment; why: Sets the save path]*
- action: Writes a Python build script via a bash heredoc and runs it, saving the memo .docx in the output directory
- purpose: Produces the formatted deliverable at the required path

**i14** (follows i13)
- observation: The task asks for prioritized findings and redline recommendations *[task; why: Sets the structure of the memo]*
- action: Structures the memo as priority-tiered findings, each giving the current template position, the risk, and proposed replacement clause language
- purpose: Delivers prioritized findings with redlines the client can act on

**i15** (follows i13)
- observation: The vendor template has numbered sections, many of them with gaps *[tool_result; why: A section-by-section summary needs the section list]*
- action: Adds an appendix matrix that maps each template section to its gap, priority and required action
- purpose: Gives a quick-reference overview of every redline

**i16** (follows i13)
- observation: The build script reported that the deliverable .docx was written to the output directory *[tool_result; why: There is now a file to validate]*
- action: Converts the generated docx back to text with parse-doc into a scratch file and checks it for the expected headings
- purpose: Confirms the content was written as intended

**i17** (follows i16)
- observation: A text extraction of the generated memo exists in the workspace *[tool_result; why: It is what gets inspected]*
- action: Reads the extracted memo text with the read tool to inspect content and layout
- purpose: Checks the rendered content visually and catches errors

**i18**
- observation: ∅ (always)
- action: Tests the integrity of the docx zip package
- purpose: Makes sure the deliverable is not corrupt

**i19** (follows i16)
- observation: The deliverable docx exists in the output directory *[tool_result; why: There is a file to render]*
- action: Converts the docx to PDF with headless LibreOffice in a scratch folder and inspects it with pdfinfo
- purpose: Checks that the document renders properly

**i20** (follows i19)
- observation: The rendering and content checks succeeded *[tool_result; why: Validation is finished]*
- action: Marks all todo items completed
- purpose: Closes out the tracked plan

**i21** (follows i20)
- observation: The deliverable has been generated and validated *[tool_result; why: The answer can now report a validated file]*
- action: Writes a short final reply with a link to the docx, a summary of the topics covered, and a note that it was validated
- purpose: Hands over the deliverable to the user

Role terms: **source documents**: the task-provided materials in the documents directory (vendor template, internal playbook, commercial terms, data-flow description, negotiation correspondence); **vendor template**: the counterparty agreement template under review; **playbook**: the client's internal negotiation standards with must-have / fallback positions; **extracted text files**: plain-text conversions of source documents saved in the workspace scratch area; **build script**: a Python script written via bash heredoc that generates the deliverable with python-docx; **deliverable**: the requested .docx memorandum saved in the output directory

## Task 6: `contracts/banking/repo-securities-lending-subsequent-turn-redline/scenario-01`

P1 `run4`, P2 `run5`; 32 invariants.

**i1**
- observation: ∅ (always)
- action: Creates a multi-step todo list (inspect inputs, determine edits, build redline, build issues list, validate) before working.
- purpose: Plans and tracks the multi-deliverable task.

**i2**
- observation: Task documents live in a documents directory under the workspace. *[environment; why: Tells the agent where to look for inputs.]*
- action: Lists the files in the documents directory.
- purpose: Discovers the available input documents.

**i3** (follows i2)
- observation: The input set contains several email (.eml) files. *[tool_result; why: Identifies documents that need reading.]*
- observation: The read tool opens plain-text files including .eml. *[environment; why: Determines which tool can read emails.]*
- action: Reads every email file with the read tool.
- purpose: Obtains the negotiation history, instructions and resolutions.

**i4** (follows i2)
- observation: Inputs include spreadsheet schedules/issues list and docx playbooks. *[tool_result; why: Identifies binary documents needing conversion.]*
- observation: Binary office files must be converted with parse-doc docx|xlsx. *[environment; why: Determines how to read them.]*
- action: Converts the collateral schedule, prior issues list and both parties' playbooks to text with parse-doc.
- purpose: Gets numeric terms and playbook thresholds for cross-checking.

**i5** (follows i2)
- observation: The task asks to produce the next-turn redline from the base redline document. *[task; why: Makes the base redline the primary document to read.]*
- action: Converts the base redline to text with parse-doc.
- purpose: Reads the current agreement text.

**i6** (follows i5)
- observation: The base redline is a docx whose tracked insertions/deletions are not distinguishable in the parse-doc text. *[tool_result; why: Requires direct XML inspection to see the existing marks.]*
- action: Opens the base redline's document.xml with lxml and enumerates per-paragraph w:ins/w:del text (and checks for an existing comments part).
- purpose: Maps every existing tracked change to its paragraph.

**i7** (follows i6)
- observation: The task requires elections unchanged since the first turn to be preserved. *[task; why: Needs knowing what changed between first turn and base.]*
- observation: A first-turn draft document is among the inputs. *[tool_result; why: Provides the comparison source.]*
- action: Compares paragraph text of the first-turn draft against the base redline.
- purpose: Identifies which provisions changed and which elections stayed constant.

**i8** (follows i6)
- observation: The base redline carries all prior-turn marks as tracked changes. *[tool_result; why: These must be resolved before new marks are layered on.]*
- observation: Emails say some drafting marks were accepted, some remain pending, some commercial issues resolved and others open. *[tool_result; why: Determines which content becomes clean and which stays tracked.]*
- action: Decides to build the output from the base redline by accepting all existing tracked changes, then adding new tracked changes only for open issues and pending marks.
- purpose: Produces a clean base with only current-turn changes tracked.

**i9** (follows i8)
- observation: Chosen strategy: accept base tracked changes then layer new edits. *[reasoning; why: Defines what the script must do.]*
- action: Writes a Python/lxml build script that extracts the base redline package, accepts all w:ins/w:del, edits paragraphs located by text match, and repackages into the output directory.
- purpose: Generates the output redline programmatically from the base.

**i10** (follows i9)
- observation: Task requires commercially resolved issues incorporated as clean accepted text. *[task; why: Defines treatment of resolved issues.]*
- observation: The commercial call memo states the agreed terms of the resolved issues. *[tool_result; why: Supplies the text values to insert.]*
- action: In the build script, replaces resolved-issue paragraphs with the agreed terms as untracked clean text.
- purpose: Shows resolved issues as settled language.

**i11** (follows i9)
- observation: Task requires open issues advanced in tracked changes reflecting the client's positions. *[task; why: Defines treatment of open issues.]*
- observation: The instructions email gives the client's next-turn position on each open issue. *[tool_result; why: Supplies the replacement text.]*
- action: In the build script, writes each open-issue change as a tracked w:del of the old text plus w:ins of the client's position, authored by the client's counsel.
- purpose: Advances open issues visibly as redline.

**i12** (follows i9)
- observation: Task requires pending mark-ups held in tracked changes flagged for the counterparty. *[task; why: Defines treatment of pending marks.]*
- observation: The counterparty response email leaves a specific subset of marks unanswered. *[tool_result; why: Identifies which marks are pending.]*
- action: In the build script, keeps each pending mark as a tracked change and attaches a flag (Word comment) addressed to the counterparty.
- purpose: Signals which marks still await counterparty response.

**i13** (follows i9)
- observation: The base redline's cover lines describe the previous turn and its change count. *[tool_result; why: Would be stale in the new turn.]*
- action: Rewrites the cover/header metadata lines to describe the new turn against the base redline.
- purpose: Keeps document metadata consistent with the new turn.

**i14** (follows i9)
- observation: The output must be a tracked-changes redline. *[task; why: Tracking should be on in the delivered document.]*
- action: Inserts w:trackRevisions into the output's settings.xml.
- purpose: Ensures the document opens with revision tracking enabled.

**i15** (follows i9)
- observation: The collateral schedule gives agreed haircut rates and worked purchase-price examples. *[tool_result; why: Provides the numbers to verify and propagate.]*
- observation: Task requires numerical terms verified against the referenced schedules. *[task; why: Mandates the numeric check.]*
- action: Updates the agreement's divisor and worked-example figures to the schedule values (market value ÷ (1+haircut)) and records the calculations.
- purpose: Keeps numeric terms consistent with the schedule.

**i16**
- observation: Task requires an issues list categorizing each issue resolved or open-advancing with final terms or each party's latest position, gaps, dynamics and next steps. *[task; why: Defines workbook content.]*
- observation: The prior issues list gives the issue rows and history. *[tool_result; why: Provides the issues to carry forward.]*
- action: Builds the issues workbook with openpyxl: an issues tracker sheet with status 'Resolved — Clean Text' or 'Open — Advancing', party positions, remaining gap, dynamics and next steps columns, plus a summary/key-dates sheet.
- purpose: Produces the required updated issues list.

**i17** (follows i16)
- observation: Drafting marks split into accepted and pending subsets. *[tool_result; why: Each mark needs a recorded treatment.]*
- action: Adds a drafting mark-ups sheet listing each drafting mark with its treatment (clean text vs tracked/flagged).
- purpose: Documents treatment of every drafting mark.

**i18** (follows i16)
- observation: Task requires numerical terms checked against schedules and thresholds cross-checked against both parties' playbooks. *[task; why: Mandates a documented cross-check.]*
- observation: Both playbooks give acceptable ranges/thresholds. *[tool_result; why: Supply the comparison values.]*
- action: Adds a QC sheet listing each numeric term/election with schedule value, playbook comparison and a PASS/OPEN outcome.
- purpose: Records the numeric and playbook verification.

**i19** (follows i9)
- observation: The build script failed because a text needle matched no paragraph. *[tool_result; why: Shows the search text differs from the document text.]*
- action: Corrects the needle to text that actually appears in the document and reruns the build script.
- purpose: Gets the build to complete.

**i20** (follows i19)
- observation: The build script reports the output redline was written. *[tool_result; why: Output now exists to be checked.]*
- action: Inspects the output XML: counts w:ins/w:del/comment markers and checks key numeric terms are present.
- purpose: Verifies the redline carries the intended changes.

**i21** (follows i19)
- observation: The output redline has been generated. *[tool_result; why: Visible text can now be checked.]*
- action: Runs parse-doc on the output redline to check visible text.
- purpose: Confirms the rendered text reads as intended.

**i22** (follows i19)
- observation: The output redline has been generated. *[tool_result; why: Package integrity can now be checked.]*
- action: Tests the output docx ZIP package integrity with unzip -t.
- purpose: Detects a corrupt package.

**i23** (follows i19)
- observation: The output redline has been generated. *[tool_result; why: Can be rendered.]*
- action: Converts the output redline to PDF with headless LibreOffice.
- purpose: Checks that the document loads and renders.

**i24** (follows i23)
- observation: The renderer reported 'source file could not be loaded' for the output redline. *[tool_result; why: Signals a possible document defect.]*
- action: Converts the unmodified base redline with the renderer.
- purpose: Determines whether the renderer itself works.

**i25** (follows i23)
- observation: The renderer failed to load the output redline. *[tool_result; why: Need a second opinion on loadability.]*
- action: Loads the output redline with python-docx.
- purpose: Checks whether another reader accepts the file.

**i26** (follows i23)
- observation: The renderer failed to load the output redline. *[tool_result; why: Malformed XML parts are a likely cause.]*
- action: Parses each XML part of the output package with lxml to check well-formedness.
- purpose: Rules out malformed XML.

**i27** (follows i24, i25, i26)
- observation: The renderer converts the base redline but not the output. *[tool_result; why: Localizes the defect to the agent's changes.]*
- observation: The output loads in python-docx and its XML parts are well-formed. *[tool_result; why: Defect is semantic, not syntactic.]*
- action: Builds stripped variants of the output (e.g., without the comments part/relationship or without tracked changes) and renders each.
- purpose: Isolates which added markup breaks rendering.

**i28** (follows i27)
- observation: A variant with all comment anchors, references and the comments part removed renders successfully. *[tool_result; why: Points to comment markup as the cause.]*
- action: Tests further variants that change individual pieces of comment markup (references only, ranges only, comment metadata/structure).
- purpose: Pinpoints which comment element breaks rendering.

**i29** (follows i20)
- observation: After the build, a resolved term's old value is still visible in the summary table, whose cells are separate paragraphs not touched by the earlier replacement. *[tool_result; why: Shows the resolved-term update missed table cells.]*
- action: Patches the build script to update the table-cell text to the agreed values, rebuilds, and re-checks the table.
- purpose: Removes stale resolved values from the redline.

**i30** (follows i16)
- observation: The issues workbook has been generated. *[tool_result; why: Its content can now be checked.]*
- action: Loads the issues workbook with openpyxl and checks sheet names, issue statuses and counts of clean vs tracked drafting-mark treatments.
- purpose: Verifies the workbook matches the categorization.

**i31** (follows i1)
- observation: Final checks on both deliverables passed. *[tool_result; why: Work is complete.]*
- action: Marks all todo items completed.
- purpose: Closes out the plan.

**i32** (follows i31)
- observation: Both deliverables exist in the output directory and passed validation. *[tool_result; why: Ready to report.]*
- action: Gives a brief final reply linking both deliverables and summarizing resolved issues clean, open issues tracked, pending marks flagged, elections preserved.
- purpose: Delivers the result to the user.

Role terms: **base redline**: the counterparty-facing previous-turn redline document the task names as the comparison base; **first-turn draft**: the original draft from which the base redline was marked; **counterparty response email**: email in which the counterparty accepts some drafting marks and leaves others pending; **commercial call memo**: email memorialising which commercial issues were resolved and which remain open; **instructions email**: supervisor email giving the client's positions for the next turn; **collateral schedule**: spreadsheet schedule of agreed numeric terms and worked examples; **playbooks**: the client's and the counterparty's negotiation guideline documents; **resolved issues**: commercial issues agreed between principals, to appear as clean text; **open issues**: commercial issues still being negotiated, to be advanced in tracked changes; **pending marks**: drafting mark-ups the counterparty has not yet answered; **build script**: Python/lxml script that generates the output redline (and/or the workbook); **output redline**: the generated next-turn tracked-changes DOCX deliverable; **issues workbook**: the generated updated issues list XLSX deliverable; **renderer**: headless LibreOffice conversion to PDF used as a load/render check; **stripped variant**: temporary copy of the output redline with some parts/markup removed, used to isolate a render failure

## Task 7: `contracts/commercial-vendor-customer/saas-api-subscription-subsequent-turn-redline/scenario-01`

P1 `run2`, P2 `run3`; 17 invariants.

**i1**
- observation: The task asks for two deliverable documents built from many reference documents *[task; why: A multi-deliverable, multi-source task warrants an explicit step plan]*
- action: Writes a todo plan: read references, map directives to the prior draft, create redline, create issues list, validate
- purpose: Structures the multi-step work and tracks progress

**i2**
- observation: Task documents live in a documents directory of the workspace *[environment; why: Tells the agent where to look for the reference documents]*
- action: Lists the workspace/document files
- purpose: Inventories the available reference documents and their formats

**i3** (follows i2)
- observation: The file listing includes plain-text email (.eml) reference documents, including the instruction email *[tool_result; why: Identifies which files can be opened directly]*
- observation: The read tool opens plain-text files such as .eml *[environment; why: Determines the tool used to open them]*
- action: Reads the instruction email and the negotiation email threads with the read tool
- purpose: Obtains the drafting directives and negotiation history

**i4** (follows i2)
- observation: The file listing includes .docx and .xlsx reference documents *[tool_result; why: These cannot be read directly]*
- observation: Office files must be converted to text with parse-doc *[environment; why: Determines the conversion method]*
- action: Converts every .docx and .xlsx reference document to text with parse-doc
- purpose: Makes the prior drafts, playbook, templates, specs and fee schedule readable

**i5** (follows i4)
- observation: Converted text files of the reference documents are saved in the workspace and are large *[tool_result; why: Large files need to be read in chunks or searched rather than consumed whole]*
- action: Reads/searches the converted text of the prior draft, playbook and templates to locate the relevant clauses and positions
- purpose: Maps directives to the clauses of the prior draft and to playbook thresholds

**i6** (follows i5)
- observation: The redline must show new changes as tracked changes against the accepted prior draft *[task; why: Requires knowing how changes are encoded in the prior draft]*
- observation: The parsed prior draft shows bracketed deleted/added change labels in its text *[tool_result; why: Raises the question whether the prior draft uses real tracked-change markup]*
- action: Inspects the prior draft's raw document XML, counting w:ins/w:del revision elements
- purpose: Determines the actual tracked-change structure of the base document

**i7** (follows i3, i5)
- observation: Deliverables must be .docx files saved in the output directory, built via bash *[environment; why: Dictates generating the files programmatically into the output directory]*
- observation: The instruction email gives per-topic directives with specific compromise values and required additions *[tool_result; why: Supplies the content each deliverable must encode]*
- action: Writes and runs a single build script that generates both the redline deliverable and the issues-list deliverable into the output directory
- purpose: Produces both required deliverables reproducibly

**i8** (follows i7)
- observation: The redline must be in real tracked changes against the accepted prior draft *[task; why: Plain colored text would not be accept/reject-able revisions]*
- observation: The instruction email is addressed to outside counsel who prepares the new draft *[tool_result; why: Identifies the revision author to attribute changes to]*
- action: Encodes each change as a w:del of the old text plus a w:ins of the new text, with the drafting firm as author and a draft date
- purpose: Makes the changes genuine Word tracked revisions

**i9** (follows i7)
- observation: Some negotiation points remain open or partially resolved after applying the directives *[tool_result; why: Open items need to be signposted in the draft]*
- action: Adds a drafting note in the redline, marked as not part of the agreement, pointing to remaining open points/the issues list
- purpose: Flags unresolved items for the counterparty without altering operative terms

**i10** (follows i7)
- observation: The instruction email prescribes a minimum list of issue categories each with a status (Resolved / Partially Resolved / Open), including a flag for a stakeholder's stricter preference *[tool_result; why: Defines the required rows and statuses]*
- observation: The playbook defines preferred / fallback / walk-away tiers *[tool_result; why: Provides the caution-zone and fallback content per issue]*
- observation: The task asks to flag cautionary-zone items and note fallback positions *[task; why: Requires dedicated caution and fallback fields]*
- action: Builds the issues list as a table with columns for issue, status, caution flag and fallback, covering all prescribed categories with the prescribed statuses (plus extra items) and flagging the stakeholder preference
- purpose: Delivers the categorized, flagged issues list

**i11** (follows i7)
- observation: The build script reported both deliverables written to the output directory *[tool_result; why: Outputs exist and can now be checked]*
- action: Converts both generated deliverables back to text with parse-doc into workspace files
- purpose: Allows inspection of the rendered content of the outputs

**i12** (follows i8)
- observation: The build script reported both deliverables written *[tool_result; why: Outputs exist to be checked]*
- observation: The redline must contain real tracked changes *[task; why: Requires confirming revision elements are present]*
- action: Opens the output docx package and counts w:ins/w:del elements in the document XML
- purpose: Verifies the redline carries genuine tracked revisions

**i13** (follows i7)
- observation: The build script reported both deliverables written *[tool_result; why: Outputs exist to be checked]*
- observation: The instruction email requires specific key directive terms *[tool_result; why: Provides the checklist of terms to search for]*
- action: Programmatically checks the outputs for presence of each key directive term
- purpose: Verifies directives were carried into the deliverables

**i14** (follows i11, i13)
- observation: The key-term check reported some expected terms as missing *[tool_result; why: Signals a possible content gap or an extraction artifact needing inspection]*
- observation: Parsed text of the outputs is available in workspace files *[tool_result; why: Provides what to read]*
- action: Reads the parsed text of the generated deliverables
- purpose: Determines whether terms are truly absent or hidden by revision markup

**i15** (follows i11)
- observation: Parsed text of the generated deliverables is available in workspace files *[tool_result; why: Can be searched for specific values]*
- action: Greps the parsed outputs for key directive terms and section names
- purpose: Confirms each directive value appears in the deliverable

**i16** (follows i1)
- observation: Validation checks of both deliverables have completed *[tool_result; why: All planned steps are done]*
- action: Marks all todo items completed
- purpose: Closes out the tracked plan

**i17** (follows i16)
- observation: Both deliverables exist in the output directory and passed the agent's checks *[tool_result; why: Allows reporting completion]*
- action: Replies with links to both deliverables, a summary of the covered topics, and a note that they were validated
- purpose: Delivers the result to the user

Role terms: **reference documents**: the read-only task documents (instruction email, email threads, prior drafts, playbook, templates, term sheet, specifications, fee schedule); **instruction email**: the reference document giving per-topic drafting directives and the required issue categories/statuses; **prior draft**: the previous agreement draft (a redline docx) whose accepted state is the base for the new redline; **playbook**: the internal negotiation guide defining preferred/fallback/walk-away tiers (caution zones); **redline deliverable**: the new draft docx with tracked changes; **issues-list deliverable**: the companion docx categorizing each negotiation point; **build script**: the Python script (python-docx/lxml) that generates the deliverables; **key directive terms**: specific values/phrases the instruction email requires to appear (thresholds, caps, named parties, notice periods)

## Task 8: `firm-knowledge/tasks/065`

P1 `run1`, P2 `run2`; 19 invariants.

**i1**
- observation: Task is a multi-part research question whose answer must be written to a self-contained response.md *[task; why: A multi-step job with a file deliverable warrants a tracked plan]*
- action: Creates a todo list: inventory corpus, review committee/execution evidence, compile qualifying matters, write response.md
- purpose: Structures the research into tracked phases ending in the deliverable

**i2**
- observation: ∅ (always)
- action: Globs every file in the workspace to inventory the corpus
- purpose: Learns the layout of matter folders and document names

**i3** (follows i2)
- observation: Corpus is organized as per-matter folders with descriptive file names, incl. Engagement subfolders *[tool_result; why: Makes filename pattern searches informative]*
- observation: Task concerns LP advisory committees and fund agreements *[task; why: Supplies the terms to search filenames for]*
- action: Globs filename patterns for task terms (LPA, LPAC, advisory) and for Engagement folders
- purpose: Finds candidate documents and matters by filename

**i4** (follows i3)
- observation: Relevant documents are .docx *[tool_result; why: They cannot be read directly]*
- observation: read opens plain text only; parse-doc converts docx to text *[environment; why: Gives the conversion method]*
- action: Converts .docx documents to text with parse-doc via bash
- purpose: Makes document content readable/searchable

**i5** (follows i4)
- observation: Model-facing file access is limited to the session workspace *[environment; why: Extracted text must live inside the workspace to be read or grepped]*
- action: Saves extracted document text as files inside the workspace (scratch files / text index)
- purpose: Allows later read and grep over converted text

**i6** (follows i3, i5)
- observation: Search hits for fund-agreement / committee / practice-group terms concentrate in a limited set of matters *[tool_result; why: Defines which matters to examine]*
- action: Shortlists those candidate matters and extracts/parses their key documents
- purpose: Focuses review on matters plausibly in scope

**i7** (follows i6)
- observation: Candidate matters are shortlisted *[reasoning; why: Identifies whose engagement letters to open]*
- observation: Task limits scope to one practice group and asks about the fund involved whoever's it was *[task; why: Engagement letters state the fund, client role and staffing practice group]*
- action: Parses and reads engagement letters of candidate matters
- purpose: Confirms the fund involved, client role and practice group of each matter

**i8** (follows i5)
- observation: Parsed text files of candidate documents exist in the workspace *[tool_result; why: Provides grep targets]*
- action: Greps parsed text for committee terms (LPAC / Limited Partner Advisory Committee / advisory committee)
- purpose: Locates evidence that each fund has an LP advisory committee

**i9** (follows i5)
- observation: Parsed text files of candidate documents exist in the workspace *[tool_result; why: Provides grep targets]*
- observation: Task excludes funds whose fund agreement was never signed *[task; why: Requires execution evidence]*
- action: Greps parsed text for execution/signature terms (executed, signed, signature, execution)
- purpose: Locates evidence of whether each fund agreement was signed

**i10** (follows i6)
- observation: Task excludes funds whose fund agreement was never signed *[task; why: Execution must be established per fund]*
- observation: Documents seen so far do not establish whether a candidate fund agreement was executed *[reasoning; why: Triggers looking for closing evidence]*
- action: Opens closing documents (closing legal opinions, matter-closing memos) of candidate matters
- purpose: Confirms that the fund agreement was executed

**i11** (follows i8)
- observation: Search shows the committee article in a candidate's execution-version fund agreement *[tool_result; why: Points to the document and section to read]*
- action: Reads the execution-version fund agreement's committee article and execution details
- purpose: Confirms both the committee and signed status from the agreement itself

**i12** (follows i8)
- observation: A candidate co-invest matter has an executed fund agreement *[tool_result; why: Passes the signed filter so the committee prong decides]*
- observation: Whether that vehicle has an LP advisory committee is not yet established *[reasoning; why: Needs a governance source]*
- action: Parses the matter's formation/governance summary memo
- purpose: Checks whether the vehicle has an LP advisory committee

**i13** (follows i12)
- observation: Governance memo states no formal LP advisory committee is established under the executed agreement *[tool_result; why: The committee prong fails]*
- action: Excludes that matter despite its signed agreement, citing the memo
- purpose: Applies the committee requirement

**i14** (follows i9)
- observation: A candidate fund's only fund agreement is a draft / first draft with future closing targets *[tool_result; why: No evidence it was ever signed]*
- observation: Task says to skip funds whose fund agreement was never signed *[task; why: Draft-only funds fall under the skip rule]*
- action: Excludes draft-only fund matters even where proposed committee provisions exist, and lists them as exclusions
- purpose: Applies the signed-agreement filter

**i15** (follows i10)
- observation: Task says to count the fund whoever's fund it was *[task; why: Investor-side matters are in scope]*
- observation: In an investor-side matter the client withdrew, but the fund's dated agreement with an LP advisory committee was operative *[tool_result; why: Client not investing doesn't make the fund agreement unsigned]*
- action: Includes the investor-side matter in the count
- purpose: Applies the skip rule to the fund, not to the client's own subscription

**i16** (follows i8)
- observation: A fund's committee is named an Investor Advisory Committee, established under its signed fund agreement and playing the LP advisory role *[tool_result; why: Shows it is functionally an LP advisory committee]*
- action: Counts it as an LP advisory committee, noting the naming difference
- purpose: Applies a functional reading of the committee criterion

**i17** (follows i13, i14, i15, i16)
- observation: Each candidate matter is classified as qualifying or excluded, with supporting documents *[reasoning; why: Provides the content of the answer]*
- observation: Deliverable must be a self-contained response.md with findings, documents relied on and reasoning *[task; why: Defines the format]*
- action: Writes response.md with the count, the qualifying matters with cited documents, the criteria and the exclusions
- purpose: Produces the required deliverable

**i18** (follows i17)
- observation: The write result shows the file was saved as output/response.md *[tool_result; why: Gives the path to verify]*
- action: Reads back output/response.md
- purpose: Verifies the written deliverable

**i19** (follows i18)
- observation: The read-back shows the deliverable is complete *[tool_result; why: All plan items are done]*
- action: Marks all todo items completed and replies briefly naming output/response.md
- purpose: Closes the plan and points the user to the deliverable

Role terms: **corpus**: the workspace documents folder of per-matter subfolders (mostly .docx); **candidate matter**: a matter whose files/text mention the task's key terms (fund agreement, LP advisory committee, the named practice group); **fund agreement**: the governing partnership agreement of the fund involved in a matter (the task's signed-status filter applies to it); **LP advisory committee**: the limited-partner committee the task asks about, including differently named equivalents; **closing document**: closing legal opinion or matter-closing memo that records what was executed; **parsed text file**: plain-text conversion of a .docx saved in the workspace for grep/read; **deliverable**: response.md answer file, saved under the output folder

