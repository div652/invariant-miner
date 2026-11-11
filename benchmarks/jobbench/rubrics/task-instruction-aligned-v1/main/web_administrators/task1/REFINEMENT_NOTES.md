# Refinement notes — web_administrators/task1

## Instruction-supported requirements

The refined instructions require five exact files: an event-level findings CSV with a fixed header and allowed phase/status vocabulary; a 14-row CR compliance audit with a fixed header; hardened Nginx and iptables replacements; and the populated nine-section incident-report template. The audit must compare the live files with every CR item and the approved topology. The report must preserve the template tables, assess every certificate and the actual Nginx TLS configuration, use OWASP Top 10 2021 codes, distinguish supported success from attempts, trace executive causation, and provide incident-specific P1/P2/P3 actions.

The local evidence includes three malicious IPs in the threat feed, public access to internal service ports, explicit Nginx gaps, five certificate records, and access-log sequences containing scanning, authentication bursts, enumeration, injection payloads, file exposure, configuration download, and destructive requests. The variant checks those sources without prescribing one hidden phase label for every ambiguous attempt or treating an HTTP 200 response as proof that a browser executed a payload.

## Original rubric disposition

| Original row | Disposition | Material change and reason |
| --- | --- | --- |
| R1 — fixed kill-chain sequence for one IP | Rewritten as new R1 | Per-event chronology and reconstructable chains are required. The original imposed hidden phase assignments, such as labeling SQL injection probes as reconnaissance and failed traversal attempts as exfiltration. The variant accepts a defensible allowed phase when notes explain the assignment. |
| R2 — selected CR outcome links | Retained and expanded as new R2 | Specific evidence links remain required, but the variant covers all 14 CR items, exact columns, source configurations, topology comparison, and no-exploitation statements. |
| R3 — fixed port-to-zone rules | Retained as new R4 | The source CIDRs and exact SSH limit are directly stated in the topology and CR. The variant checks them from those inputs rather than embedding the answer values in the question. |
| R4 — fixed TLS conclusions | Rewritten and merged into new R6 | Every certificate and the actual Nginx TLS state must be assessed. The compliant set is derived from source fields rather than prescribed. |
| R5 — executive causation | Retained and generalized in new R6 | Closure without verification and item-to-outcome causation are explicit. Every unimplemented item, not only four selected examples, is considered. |
| R6 — timeline | Retained and merged into new R5 | All malicious IPs, chronology, and attack categories are required. Exact hidden event wording is removed. |
| R7 — OWASP and success classifications | Rewritten in new R5 | Official 2021 category codes and evidence-supported status remain required. The original treated 200 responses as conclusive XSS execution and mandated a specific path-traversal status beyond what the logs alone prove. |
| R8 — remediation table | Retained and expanded as new R7 | P1/P2/P3 actions remain, with exact deliverables, embedded full configurations, and standalone/report consistency added. |
| No original row — exact findings header and one-row-per-event rule | Added to new R1 | These are explicit refined instructions and distinguish a compliant findings file from grouped summaries. |
| No original row — complete hardened Nginx controls | Added as new R3 | The original rubric did not independently score all CR 1a–1f controls and TLS 3c in the replacement file. |
| No original row — template preservation and placeholders | Added to new R5 | Sections 1–9 and table columns must be retained and populated. |

## Score, output, and trajectory evidence examined

All 35 distinct judge reports across main runs were inspected. Scores ranged from 6/50 to 50/50, with a median of 18/50. Original R1 failed in 33/35 reports, R7 in 31/35, R5 in 30/35, and R8 in 28/35. The port-segmentation row did not fail in the available reports, while exact output-schema compliance was not represented by an original row.

Representative outputs and trajectories examined:

- Refined Luna: 30/50 in both reports. It produced 72 event rows with the exact required findings header, all 14 audit items, zone-restricted firewall rules, a TLS 1.2 Nginx replacement, a nine-section report with all five domains, and no placeholders. Judges penalized its defensible Exploitation label for SQL injection attempts, its separation of failed traversal from successful exfiltration, and its use of Partial for a brute-force sequence.
- Sol rubric-gold: 50/50 in both reports. Its findings file contained only 22 grouped event rows, used a different 12-column schema, and aggregated time ranges despite the refined one-row-per-event requirement. Its audit also included an extra “V” row. The original rubric still awarded full credit, demonstrating a coverage gap.
- Qwen reasoning: 12/50 in both reports. It produced 72 findings rows but omitted required status_code, response_size, attack_type, and notes columns, used a boolean success field, and did not assess all five TLS domains in the report.

The CR, topology, live Nginx and firewall files, certificate inventory, threat feed, access logs, and HTML template were inspected directly. Output CSV row counts, headers, rule text, report sections, and trajectories were compared with judge diagnostics.

## Likely judge artifacts versus genuine task failures

Likely judge artifacts or unsupported expectations:

- Mandating a single hidden kill-chain phase for ambiguous probes when the instructions only provide a label vocabulary.
- Treating HTTP 200 and response size as proof that reflected or stored XSS executed in a browser.
- Requiring exact success labels where the log supports uncertainty and the instructions permit Partial.
- Awarding full credit to grouped events and a nonconforming findings schema because the original rubric did not test the refined CSV specification.
- Using the threat feed's obsolete XSS category wording as interchangeable with official OWASP Top 10 2021 categorization.

Genuine failures observed:

- Omitting malicious events, required columns, response evidence, or notes needed to reconstruct an attack chain.
- Failing to assess all CR items or all certificates.
- Leaving internal ports unrestricted, omitting the exact SSH limit, or relying only on local bindings.
- Missing dotfile, debug, admin, header, HTTPS, or TLS controls in the hardened Nginx file.
- Leaving placeholders, using invalid OWASP 2021 codes, or providing generic remediation disconnected from incident resources.

## Weight preservation

- Original total weight: 50
- Variant total weight: 50
- Reallocation: weight was moved from hard-coded phase and outcome answers to the exact event schema, all 14 CR items, complete replacement configurations, template preservation, uncertainty-aware evidence classification, and exact deliverables.
