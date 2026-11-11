# Refinement notes — lawyers/task1

## Instruction-supported requirements

- Deliver a readable PDF memo of no more than six pages, a comparative CSV, and a numbered TXT counter-proposal.
- Query the eight-table SQLite database for fines, property details, income, LTR comparables, mortgage balances, permits, ordinance history, and settlement terms.
- Calculate inclusive fine exposure as of the letter and through January 31, 2026.
- Compare all six properties using transitional STR income, historical annual STR net income, annual LTR comparables, fines, and mortgages.
- Give Sandra Whitfield a qualified sale-or-hold analysis using the available market-value, debt, and operating data without inventing transaction or tax inputs.
- Evaluate Hignell-Stark, each amortization case cited by the Town, Penn Central, available constitutional claims, every settlement section, Property 4, and rezoning.
- Compare the three regulatory schemes across the seven required provision categories and state legal significance.
- Propose a specific transition, R-1 treatment, objective night-cap review, and preservation of rights, with legal and financial rationale.

The database schema and records, Town Attorney letter, local ordinances, external Hignell-Stark opinion, Penn Central article, refined instructions, source rubric, and source notes were inspected.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 fines | Retained and generalized | Inclusive per-property and aggregate calculations remain required. The variant derives them from the database and dates instead of embedding the answer values. |
| R2 comparative table | Retained | Preserved all seven categories, three jurisdictions, explicit absences, and legal significance without requiring the rubric's exact prose. |
| R3 longer transition | Rewritten | A specific supported duration remains required. The instructions do not require a duration longer than three years or a particular five-to-seven-year conclusion. |
| R4 mutual tolling | Merged into counter-proposal rights preservation | Tolling is an acceptable mechanism, but the instructions require preservation of litigation rights rather than that single remedy or a prescribed rationale. |
| R5 Penn Central | Retained | Preserved all three factors and property-specific evidence without requiring a predetermined strength conclusion. |
| R6 dormant Commerce Clause | Rewritten into precedent and claims analysis | The actual Hignell-Stark holdings and any analogous claim must be evaluated accurately. The variant does not require exact phrases such as “virtually per se invalid.” |
| R7 dismissal with prejudice | Merged into complete settlement review | The term and its consequences must be analyzed if present, but the counter-proposal is not forced to use one specific dismissal formulation. |
| R8 amortization cases | Retained in precedent analysis | The cited cases must be evaluated on their facts and holdings. The variant does not dictate the ultimate analogy or require a hidden conclusion. |

The variant adds explicit deliverable usability, complete per-property economics, deadline-aware advice, and review of every settlement section.

## Score and trajectory evidence examined

All 36 available judge reports were summarized. Source-row pass counts were R1 27/36, R2 29/36, R3 11/36, R4 5/36, R5 33/36, R6 10/36, R7 11/36, and R8 11/36.

Representative outputs and trajectories examined:

- Refined Luna scored 48/48 from one judge and 36/48 from the other. Its four-page memo, seven-row CSV, and counter-proposal covered the database economics, Penn Central, Property 4, objective cap review, tolling, and claim preservation. The lower score came from missing exact rubric phrases and a prescribed tolling rationale, not from absence of the requested analysis.
- Sol rubric-gold scored 48/48 in both reports. It produced a six-page memo, a nine-row comparison table, and a five-year counter-proposal with quantified fines, objective annual review, R-1 treatment, and mutual tolling.
- Qwen reasoning scored 6/48 in both reports. It omitted the required spacing comparison, did not project fines through the waiver deadline, did not analyze AVR and Gage, omitted a full Penn Central character-of-action discussion, and preserved rights without addressing limitation-period risk.

## Likely judge artifacts versus genuine task failures

- **Likely artifacts:** requiring a transition longer than three years; requiring mutual tolling instead of any effective rights-preservation mechanism; requiring exact strict-scrutiny wording; requiring one named property's example figures when equivalent database-grounded portfolio evidence is supplied; requiring a predetermined view that a claim is strong.
- **Genuine failures:** missing inclusive fine projection, missing one of the seven CSV categories, failure to analyze cases expressly cited in the letter, incomplete per-property economics, omission of a Penn Central factor, failure to review a settlement section, and unsupported legal holdings or financial figures.

The variant also separates legal accuracy from negotiation preference. A well-supported accept, reject, or counter recommendation can pass.

## Weight preservation

- Original total weight: **48**
- Variant total weight: **48**
- The second-pass row weights are **6, 4, 2, 6, 6, 6, 6, 6, 6**.
- The prior 6-point property-economics row was split into 4 points for operating economics and fine exposure and 2 points for Sandra Whitfield's sale-or-hold analysis.

## Second-pass validation

- Added the omitted client-decision analysis for Sandra's two properties using database market value and mortgage data.
- The new row accepts qualified estimates, disclosed selling-cost or tax assumptions, and explicit requests for missing appraisal inputs; it does not require a sale recommendation.
- Preserved the 48-point total.
- Deferred the judge's missing-database and missing-legal-source context finding to evaluator infrastructure rather than embedding expected figures or holdings in the rubric.
