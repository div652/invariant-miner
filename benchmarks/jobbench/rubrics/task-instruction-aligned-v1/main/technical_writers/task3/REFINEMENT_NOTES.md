# Refinement notes — technical_writers/task3

## Instruction-supported requirements

The task requires five deliverables with flexible filenames: a CSV discrepancy report, a 1500-word-or-longer Markdown style guide, complete rewritten v2 Markdown documentation, an HTML webhook catalog, and a Markdown migration guide. The discrepancy report must use six named columns, compare every parameter, field, and response in either source, use the specified discrepancy vocabulary, give complete enum sets and both numeric values, and name the source to adopt.

The style guide must reconcile every audit-tracker terminology issue, select and justify a date/time standard, and define a response-envelope standard. The rewritten docs must cover every OpenAPI operation, resolve all audit-tracker issues, apply the envelope decision, and provide error-code tables for every endpoint, especially those flagged by the tracker. The webhook catalog must cover the union of defined YAML events and observed delivery-log events with exact provenance labels, examples, and handling recommendations. The migration guide must map v1 fields and explain every removed, deprecated, or changed v1 endpoint. The instructions do not reveal the discrepancy values, event differences, terminology decisions, or migration mappings; they must be discovered from the named inputs.

## Original rubric disposition

- **R1, R2, R3, R11, and R12 — merged and expanded as new R1 and R2.** Specific pagination, enum, length, and projects examples remain discoverable test cases, but the variant assesses the complete atomic comparison and exact required CSV schema.
- **R4 and R5 — retained and generalized as new R3.** Timestamp and terminology standards remain, without embedding the expected source discrepancies or approved terms in the rubric.
- **R6 and R7 — expanded as new R4.** Envelope consistency and missing error tables remain, with direct coverage for every OpenAPI operation and every audit-tracker gap.
- **R8 — retained and generalized as new R5.** The union, provenance, examples, and handling of all events are assessed without revealing which events are log-only.
- **R9 and R10 — merged and expanded as new R6.** Field renames and changed/removed endpoints remain, but all discoverable migrations are assessed instead of a fixed subset.
- **New R7 — added.** Publication quality and cross-deliverable consistency were explicit practical requirements omitted by the original rubric.

## Material changes and reasons

1. The variant removes hard-coded source values, event names, field mappings, and endpoint changes from criterion text. They remain fully checkable from the local inputs.
2. The discrepancy CSV is now scored against the six exact minimum columns. The original rubric awarded full credit to a Sol file that used a different ten-column schema and lacked the instructed `parameter_or_field`, `yaml_value`, and `docs_value` names.
3. Comprehensive source comparison receives more weight than a dozen selected discrepancies. Missing one hidden example no longer dominates an otherwise complete report, while broad omissions now matter.
4. Rows must represent actual disagreements. A submission cannot inflate completeness by listing every matching field as `missing_in_docs` or by converting audit quality notes into fabricated OpenAPI values.
5. The style guide is assessed for all audit terminology conflicts and reusable TaskFlow conventions, not only a fixed glossary subset.
6. The rewritten docs are assessed operation by operation for parameters, bodies, responses, errors, envelope, timestamps, examples, and unsupported inventions.
7. The webhook catalog must use the exact provenance labels required by the instructions, but the rubric does not leak which events receive each label.
8. The migration guide must cover every discoverable change, not merely five renames and three endpoint examples.
9. Flexible output filenames remain allowed because the instructions explicitly permit filenames of the submission's choice.

## Score and trajectory evidence examined

The available report set contains **36 judge reports across 17 runs**. Representative outputs and trajectories were inspected for:

- **Refined Luna landlock:** 84/84 and 78/84. It produced five files, a parseable six-column discrepancy CSV with 175 rows, an 1800-word style guide, documentation for all 17 OpenAPI operations, a union webhook catalog, and a detailed migration guide. The low judge failed only because the guide did not narrate every original timestamp inconsistency before stating and applying its standard. Its trajectory did not receive the rubric.
- **Sol rubric-gold:** 84/84 in both reports. It produced polished deliverables and covered the narrow expected facts, but its discrepancy CSV used a nonconforming schema. Its trajectory contained evaluator guidance. The original rubric did not test the explicit six-column requirement.
- **Qwen 3.8 reasoning:** 46/84 and 60/84. It produced all five deliverables with broad content, but used unapproved discrepancy labels such as `value_conflict` and `missing_from_docs`. Those are genuine instruction violations even though many underlying discrepancies were found. Its trajectory did not receive the rubric.
- **GPT-5.4:** 40/84 and 34/84. It found many source differences but used ad hoc discrepancy labels, did not fully standardize timestamps or envelopes, and left several tracker-flagged endpoints without error documentation.

The audit tracker, all OpenAPI operations and schemas, current v2 and legacy v1 docs, delivery-log events and payload excerpts, local template, GitLab style guidance, representative CSV rows, Markdown structure, HTML contents, judge reasons, and session trajectories were inspected.

## Likely judge artifacts versus genuine task failures

Likely artifacts include requiring the style guide to recite each legacy timestamp inconsistency when it already selects, justifies, and applies a standard; scoring only a small hidden set of discrepancies; or awarding full credit despite a CSV that omits the required columns.

Genuine failures include malformed or wrongly headed CSV, non-approved discrepancy labels when a provided label fits, incomplete enum sets, omitted operations or fields, fabricated disagreements, missing audit-tracker gaps, a style guide under 1500 words, unresolved terminology, no timestamp or envelope standard, missing error tables, undocumented OpenAPI operations, invented behavior, incomplete event union or provenance, missing payload examples, omitted migration mappings, or inconsistent facts across files.

## Weight accounting

- Original total: **84**
- Variant total: **84**
- Weight moved from disclosed example answers to complete source reconciliation, exact deliverable schemas, all-operation documentation, union/provenance coverage, full migration coverage, and cross-deliverable consistency.

## Second-pass validation

- Split the former 18-point rewritten-documentation row into operation/input coverage, request/success examples, error and audit-gap coverage, and cross-cutting standards.
- Preserved every criterion while reducing the penalty from one localized omission and retaining the **84-point** total.
- Deferred evaluator-infrastructure work: judges need the OpenAPI, current and legacy docs, tracker, delivery log, template, and external style guidance to verify exhaustive source reconciliation.
