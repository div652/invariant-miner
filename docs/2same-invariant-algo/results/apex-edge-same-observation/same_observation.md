# Same-observation check of the cross-consistent invariants

Cross-check run `runs/xc-apex-edge-20261120T124256Z`: 21 cross-consistent invariants, 210 pairs. Method in the script's docstring.

1. Exact: identical fact texts 0, identical fact sets 0.
2. Lexical (token Jaccard >= 0.4 between two facts): 1 fact pairs.
3. Judge (GPT-5.6 Luna high, one call per pair): different 205, one_contains_other 3, partial_overlap 2

## Pairs the judge did not call different

| A | B | relation | reason | A's observation | B's observation |
|---|---|---|---|---|---|
| i20 (`world112-1-task05-na-cf44bbb8`) | i22 (`world112-1-task05-na-cf44bbb8`) | **one_contains_other** | Observation B includes the same availability of total savings, investment, and payback as A, plus the requirement to print the answer. | - The primary calculation script produced total savings, investment and payback [tool_result] | - Verified total savings, total investment and payback are available [tool_result] - The task asks for the answer printed as a message [task] |
| i5 (`world132-da-task05-a025ddde`) | i6 (`world132-da-task05-a025ddde`) | **one_contains_other** | Observation A contains the fact in Observation B and adds that the spreadsheet holds unrelated criteria. | - The scoring framework spreadsheet holds unrelated criteria and does not define the requested scoring methodology [tool_result] | - The scoring framework spreadsheet does not define the requested scoring methodology [tool_result] |
| i9 (`world225-rl-task01-45ba9aaf`) | i16 (`world225-rl-task01-45ba9aaf`) | **one_contains_other** | Observation B includes the requirement that the table be in the existing sensitivity sheet and adds its range and verification details. | - The table must go in the existing sensitivity sheet. [task] | - The table was written to a known range of the existing sensitivity sheet, and its four rounded scenario values were verified. [tool_result] |
| i12 (`world225-rl-task01-45ba9aaf`) | i16 (`world225-rl-task01-45ba9aaf`) | **partial_overlap** | Both concern edits to an existing workbook, but A specifies a multi-sheet cached-formula model while B specifies a sensitivity-sheet range and verified scenario values. | - The task requires editing an existing model workbook that has many other sheets and cached formula values. [task] | - The table was written to a known range of the existing sensitivity sheet, and its four rounded scenario values were verified. [tool_result] |
| i16 (`world225-rl-task01-45ba9aaf`) | i11 (`world225-rl-task01-45ba9aaf`) | **partial_overlap** | Both mention the four scenario values, but A also states they were verified and written to a range while B states the sheet has empty rows and the values were computed. | - The table was written to a known range of the existing sensitivity sheet, and its four rounded scenario values were verified. [tool_result] | - The existing sensitivity sheet's content ends a few rows above row 45, and the rows below are empty. [tool_result] - The four scenario values have been computed. [tool_result] |

## Lexically close fact pairs

| Jaccard | A | B | A's fact | B's fact |
|---|---|---|---|---|
| 0.69 | i5 (`a025ddde`) | i6 (`a025ddde`) | The scoring framework spreadsheet holds unrelated criteria and does not define the requested scoring methodology | The scoring framework spreadsheet does not define the requested scoring methodology |
