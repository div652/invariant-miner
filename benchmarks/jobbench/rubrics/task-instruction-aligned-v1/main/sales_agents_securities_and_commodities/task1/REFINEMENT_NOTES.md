# Refinement notes — sales_agents_securities_and_commodities/task1

## Instruction-supported requirements

- Produce the two exact three-sheet workbooks and one per-agent PDF scorecard.
- Validate every settled SELL transaction for SEC Section 31 and FINRA TAF using Q4 2024 rates, effective dates, sources, and calculated variances.
- Benchmark every agent's internal tier and rate against Fidelity's published online and representative-assisted schedule using a stated comparison basis.
- Calculate settled net positions, use supplied Dec. 31 closes for AAPL/MSFT/GOOGL, use settled-transaction VWAP for the five named proxy tickers, and label price sources.
- Apply the 30/40 percent concentration thresholds and the instructed volatility formula and suitability scope.
- Report monthly settled volume, adjusted net commission, retention counts and ratio, cancelled/pending ratios, and bidirectional cancelled-trade/clawback reconciliation.

## Original rubric disposition

- **Original R1 retained and rewritten.** Removed the three hard-coded agent outcomes and mandatory `Above Industry` result. The revised row checks every database agent, Fidelity values and source, the structural comparison, vocabulary, and consistent classification basis.
- **Original R2 rewritten.** Removed the embedded closing prices. The revised row checks the exact Dec. 31 source rows, net-position formula, labels, and valuations.
- **Original R3 rewritten.** Removed the embedded VWAP answers. The formula, transaction population, five instructed tickers, source totals, and label remain required.
- **Original R4 expanded.** Retained volatility and account scope, and added the expressly required concentration analysis.
- **Original R5 rewritten.** Removed fixed transaction IDs, names, and predetermined total. The revised row performs both directions for every relevant database record and totals whatever mismatches the source data establishes.
- **Original R6 rewritten.** Removed the predetermined 100 percent outcome. The instructed retention definition, counts, and per-agent ratio remain required, alongside monthly volume and status ratios.
- **Original R7 retained and expanded.** Removed the hard-coded row count while retaining one row per settled SELL. Added SEC/TAF rate, source, effective-date, cap, rounding, and variance checks.
- **Original R8 retained and clarified.** Exact sheet names and complete, mutually consistent client-level analysis remain required.

## Evidence examined

- Read the refined instructions, original rubric and notes, SQLite schema and records, all three market-data CSVs, Fidelity schedule, and supplied FINRA SRO schedule.
- The database contains 30 settled SELL transactions, five Cancelled transactions, and three Clawback adjustments. These facts were used diagnostically but are not hard-coded in the revised rubric.
- The supplied FINRA PDF is an SRO/jurisdiction registration schedule, not the source of Section 31 or TAF trading rates. A correct submission therefore needs the appropriate authoritative FINRA/SEC notices in addition to the named-file review.
- Across 36 judge reports, original-row pass counts were R1 7/36, R2 25/36, R3 21/36, R4 17/36, R5 7/36, R6 9/36, R7 6/36, and R8 6/36.
- Refined Luna scored 58/74. It had exact workbook structures, complete settled-SELL rows, correct position sources, and a three-page scorecard, but the judge found insufficient commission-benchmark explanation and incomplete clawback mapping detail.
- Sol rubric-gold scored 74/74 and documented the fee sources, formulas, VWAP totals, volatility method, and bidirectional commission findings.
- Qwen 3.5 reasoning scored 10/74. It used wrong sheet names, average-trade proxies instead of VWAP, incomplete retention reporting, noncompliant scorecard structure, and no adequate Fidelity comparison.

## Likely judge artifacts versus genuine task failures

- Fixed prices, VWAPs, transaction IDs, agent names, retention outcomes, and mismatch totals are necessarily source-derived but need not be disclosed in the rubric. Method and source completeness are sufficient to distinguish correct work.
- Requiring every agent to be `Above Industry` is not instruction-supported because the classification depends on the stated flat-fee-versus-percentage comparison basis.
- The named FINRA SRO PDF does not itself contain the trading rates. Penalizing a submission for citing the correct rate notice instead would be an artifact.
- Missing exact sheet names, omitting settled sells, wrong fee formulas, wrong proxy populations, incomplete bidirectional reconciliation, absent retention counts, and inconsistent position values are genuine failures.

## Weight accounting

- Original total: **74**
- Revised total: **74**
- Original row weights were retained while hard-coded outcomes were replaced by source-grounded calculation and completeness criteria.

## Second-pass validation

- Net commission now accepts a reconciled ledger/accrual or earned-settled basis and rejects double counting cancelled commissions and their clawback reversals.
- Concentration analysis now requires an explicit, financially coherent treatment of negative positions and accepts documented net-asset-value or gross-exposure methods.
- Database, market-file, and external-fee-reference access remains an evaluator-infrastructure requirement; no hidden transaction answers were added.
