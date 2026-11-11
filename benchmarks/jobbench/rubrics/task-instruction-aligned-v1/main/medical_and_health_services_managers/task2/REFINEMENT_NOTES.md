# Refinement notes — medical_and_health_services_managers/task2

## Instruction-supported requirements

- Produce the three exact deliverables and the two exact workbook sheet names.
- Select the top 10 CPT codes by `Annual_Volume_2024`, cross them with all six named payers, calculate per-unit profitability, apply the strict `< 1.2 × cost` flag, and derive a monthly budget-versus-actual trend indicator.
- Select and document a comparable California peer group from the 2025 Q1 HCAI file; calculate operating margin with the instructed formula and standard total-margin and days-cash measures; show the 25th, median, and 75th percentiles and Valley General's relative position.
- Calculate local and peer government-payer revenue shares using the instructed payer definitions, state the managed-care treatment, report local visit share, and discuss comparability.
- In the memo, reconcile annual revenue, expense, and net-income variances; analyze every loss month with PT, OT, SLP, and expense figures; identify the five largest charge-to-reimbursement gaps under a stated reimbursement basis; estimate annual impact from volume and payer distribution; and provide exactly two actions tied to consistently unfavorable expense categories.
- Accept equivalent correct calculations and explicit not-calculable results where the named local inputs do not contain a required hospital-level balance-sheet value.

## Original rubric disposition

- **Original R1 rewritten as new R1.** Removed the hidden conclusion that Medicaid must be the only flagged payer and the embedded example values. The revised row tests top-10 selection, all 60 required combinations, source values, calculations, flags, and the instructed trend field.
- **Original R2 and R7 merged into new R2.** Removed the unsupported expected peer median of 1–3 percent. The merged row checks formulas, cohort consistency, percentiles, presentation, and documented uncertainty. It accepts an explicit `not calculable` Valley General days-cash result because the local department workbook has no cash or marketable-securities balance.
- **Original R3 rewritten as new R3.** Removed the hard-coded 45.8 and 54.8 percent outcomes. The revised criteria test the named payer components, denominators, peer fields, managed-care treatment, comparison, visit share, and comparability notes.
- **Original R4 rewritten as new R4.** Removed the fixed CPT list, fixed dollar gaps, and the unrequested rule that the comparison must use the highest-paying payer. The instructions require the reimbursement basis to be stated, so a consistently applied weighted, payer-specific, or other defensible basis is accepted.
- **Original R5 and R6 merged into new R5.** Removed the requirement that both actions target only PT and OT salaries. The instructions instead require actions tied to the expense categories with the most consistent unfavorable variances. The annual revenue and expense bridge remains required.
- **Original R8 rewritten as new R6.** Removed the predetermined June–July narrative and exact comparison wording. The revised row requires all actual loss months, discipline revenue, expenses, baselines, and source-supported drivers.
- **Original R9 retained and clarified as new R7.** File names, formats, workbook sheet count, and sheet names remain direct deliverable requirements.

## Evidence examined

- Read the refined `TASK_INSTRUCTIONS.txt`, original `RUBRICS.json`, `REFINEMENT_NOTES.md`, both local inputs, and the supplied HCAI workbook.
- Examined all 35 available Grok judge reports across the run directories. Original-row pass counts were: R1 35/35, R2 0/35, R3 7/35, R4 2/35, R5 6/35, R6 13/35, R7 4/35, R8 2/35, and R9 6/35. Scores ranged from 6/86 to 66/86.
- Inspected outputs and trajectories from:
  - refined Luna landlock, 36/86: complete 60-row CSV, correct two-sheet workbook structure, HCAI download and calculation work, and a detailed memo, but internally inconsistent annual variance and Valley operating-margin figures;
  - Sol rubric-gold, 66/86: strongest judged result, complete deliverables, HCAI retrieval, source tables, and detailed memo;
  - Qwen 3.5 reasoning, 6/86: wrong workbook sheet names, unsupported peer presentation, missing flags, and weaker memo analysis;
  - GPT-5.4, 6/86: substantive HCAI analysis but wrong sheet names, nine payer labels in the CSV, and incomplete required memo findings.
- The best-scoring output still failed original R2 and R7. Representative lower-scoring trajectories showed incomplete external-data use, output-schema drift, or omission of required monthly and memo analyses.

## Likely judge artifacts versus genuine task failures

### Likely artifacts or misaligned expectations

- Original R2's 1–3 percent peer-median expectation failed in all 35 reports, including rubric-gold. Actual reported medians varied with defensible peer selection and were near 0.03 percent or negative. The instructions specify the formula and cohort disclosure, not a hidden median.
- Original R4 required highest-payer reimbursement and fixed results even though the instructions only require the basis to be stated. Refined Luna's volume-weighted basis was methodologically permissible even when it differed from the hidden answer.
- Original R5 rejected a benefits-and-supplies action because it was not a second PT/OT salary action, despite the instructions asking for actions tied to whichever categories are consistently unfavorable.
- Original R7 treated unavailable Valley General cash data as failure. Fabricating department days cash would be worse than stating the missing inputs.
- Original R8 rewarded one expected seasonal narrative instead of the instructed task of identifying loss months and their drivers.

### Genuine failures

- Missing or wrong sheet names, extra payer categories, absent flags, incomplete top-10-by-six-payer coverage, and omitted required files are genuine deliverable failures.
- Incorrect annual variance figures, unreconciled budget bridges, incorrect Valley operating margin, omitted loss-month discipline figures, and unsupported revenue-impact assumptions are genuine analytical failures.
- A peer analysis without documented selection criteria, source fields, formulas, or comparability limits is genuinely incomplete.

## Never-full analysis

No available report awarded 86/86. The persistent cause was not a single model limitation:

1. **An impossible-to-generalize hidden peer result:** original R2 failed 35/35 because it demanded a 1–3 percent median not required by the instructions and not reproduced by the supplied HCAI data under the documented cohorts.
2. **A hidden reimbursement methodology:** original R4 failed 33/35 on its gap-value criteria because it forced highest-payer reimbursement. Valid weighted-average analyses were scored as wrong.
3. **Missing local liquidity inputs:** original R7 failed 31/35 on both side-by-side-value criteria because days cash for Valley General cannot be calculated from the department workbook.
4. **Overconstrained actions and narrative:** original R5 required both actions to address PT/OT salaries, and original R8 required a specific June–July story and exact figures rather than judging the complete monthly analysis.
5. **Real execution errors remained:** even after removing those artifacts, several outputs would still lose credit for wrong calculations, missing sections, schema drift, or unsupported assumptions.

The revised rubric therefore preserves the task's analytical difficulty while scoring the instructed methods and source-grounded conclusions rather than hidden answers.

## Weight accounting

- Original total: **86**
- Revised total: **86**
- Weight was reallocated only when duplicate comparison rows were merged and hidden-answer criteria were replaced with broader instruction-supported analysis.
