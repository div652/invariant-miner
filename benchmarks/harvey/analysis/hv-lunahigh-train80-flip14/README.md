# Harvey FK, Luna high, base harness: the 14 AHE-train tasks whose all-pass flips across three runs

The 80 AHE train tasks (benchmarks/harvey/splits-ahe-80-20-70.json, ahe:train), three runs of the base harness with GPT-5.6 Luna high (main's three-run baseline, benchmarks/harvey/RESULTS.md): 52 tasks fail in all three runs, 14 pass in all three, these 14 pass in one or two. 8 pass once (048 066 072 082 104 137 162 210), 6 pass twice (028 167 185 192 198 200).

Runs: **run1** = `hv-fk250-lunahigh-20261110T175632Z`; **run2** = `hv-fk250-lunahigh-rep2-20261112T122308Z`; **run3** = `hv-fk250-lunahigh-rep3-20261112T141312Z`

Each trace file: overview diagrams and a step table, the task prompt, the rubric with the judge's reasoning, the delivered files, then every step (reasoning summary, tool calls, outputs cut to 1,500 chars).

| Task | run1 | run2 | run3 | Question (short) |
|---|---|---|---|---|
| [firm-knowledge/tasks/048](#048) | [fail 3/4](048-run1.md)<br/>50 steps, 10 min | [fail 3/4](048-run2.md)<br/>67 steps, 11 min | [**pass** 4/4](048-run3.md)<br/>20 steps, 6 min | I'm running a use-of-proceeds precedent review across our equity and debt offerings — which of our Capital Markets deals had proceeds earmarked prima… |
| [firm-knowledge/tasks/066](#066) | [fail 8/9](066-run1.md)<br/>21 steps, 4 min | [**pass** 9/9](066-run2.md)<br/>33 steps, 5 min | [fail 8/9](066-run3.md)<br/>17 steps, 4 min | We're standing up an LP advisory committee for a new fund and I want to see how we structured the last one. What's the most recent fund or co-investm… |
| [firm-knowledge/tasks/072](#072) | [**pass** 4/4](072-run1.md)<br/>28 steps, 5 min | [fail 3/4](072-run2.md)<br/>38 steps, 9 min | [fail 3/4](072-run3.md)<br/>56 steps, 13 min | We're pitching a new life-sciences client and I want to speak to our clinical-trial experience with numbers — how many of our Healthcare & Life Scien… |
| [firm-knowledge/tasks/082](#082) | [**pass** 1/1](082-run1.md)<br/>25 steps, 8 min | [fail 0/1](082-run2.md)<br/>23 steps, 4 min | [fail 0/1](082-run3.md)<br/>33 steps, 7 min | We just took on a new chip-patent dispute, and before we go further I want to run a conflicts and precedent check. Pull any semiconductor IP disputes… |
| [firm-knowledge/tasks/104](#104) | [fail 0/3](104-run1.md)<br/>28 steps, 10 min | [fail 0/3](104-run2.md)<br/>32 steps, 5 min | [**pass** 3/3](104-run3.md)<br/>21 steps, 3 min | I'm drafting equity-vesting acceleration language and want to work from our most recent precedent rather than starting cold. What's the latest Labor … |
| [firm-knowledge/tasks/137](#137) | [fail 3/4](137-run1.md)<br/>33 steps, 9 min | [fail 2/4](137-run2.md)<br/>34 steps, 8 min | [**pass** 4/4](137-run3.md)<br/>44 steps, 11 min | I'm building our specific-performance enforcement posture for a deal dispute and want to see how we've argued it. Pull the M&A deals where we actuall… |
| [firm-knowledge/tasks/162](#162) | [**pass** 4/4](162-run1.md)<br/>28 steps, 6 min | [fail 0/4](162-run2.md)<br/>17 steps, 3 min | [fail 0/4](162-run3.md)<br/>16 steps, 3 min | We're refreshing the firm bio for a pitch and I want to lead with our roots in the IPO market. What was the first traditional, non-SPAC IPO we took p… |
| [firm-knowledge/tasks/210](#210) | [fail 4/15](210-run1.md)<br/>25 steps, 7 min | [**pass** 15/15](210-run2.md)<br/>19 steps, 3 min | [fail 3/15](210-run3.md)<br/>34 steps, 8 min | I'm prepping for a relationship review and want to know where our weight is — who are our top five clients by number of matters, with the counts? Out… |
| [firm-knowledge/tasks/028](#028) | [fail 5/6](028-run1.md)<br/>28 steps, 9 min | [**pass** 6/6](028-run2.md)<br/>21 steps, 4 min | [**pass** 6/6](028-run3.md)<br/>36 steps, 9 min | I'm building a DIP financing precedent bank for the restructuring group. Which of our restructuring matters involved DIP financing — in any capacity,… |
| [firm-knowledge/tasks/167](#167) | [fail 4/5](167-run1.md)<br/>35 steps, 7 min | [**pass** 5/5](167-run2.md)<br/>39 steps, 6 min | [**pass** 5/5](167-run3.md)<br/>75 steps, 11 min | I'm putting together an experience summary on our large-deal governing-law practice — which of our deals over a billion dollars in guaranteed (base) … |
| [firm-knowledge/tasks/185](#185) | [fail 0/4](185-run1.md)<br/>15 steps, 2 min | [**pass** 4/4](185-run2.md)<br/>18 steps, 3 min | [**pass** 4/4](185-run3.md)<br/>25 steps, 3 min | I've got a check-in call with Cascade Retail Holdings coming up and want to walk in with the latest context. What's the most recent matter we've hand… |
| [firm-knowledge/tasks/192](#192) | [**pass** 10/10](192-run1.md)<br/>42 steps, 5 min | [fail 9/10](192-run2.md)<br/>18 steps, 6 min | [**pass** 10/10](192-run3.md)<br/>17 steps, 6 min | Building out an MAE language bank ahead of the next merger agreement draft—find all our merger agreements that actually use the phrase 'material adve… |
| [firm-knowledge/tasks/198](#198) | [fail 3/4](198-run1.md)<br/>31 steps, 6 min | [**pass** 4/4](198-run2.md)<br/>34 steps, 8 min | [**pass** 4/4](198-run3.md)<br/>33 steps, 6 min | I need a set of comparables for a large financing we're papering. Pull the executed credit agreements from our deals valued over a billion dollars. O… |
| [firm-knowledge/tasks/200](#200) | [**pass** 4/4](200-run1.md)<br/>16 steps, 4 min | [fail 3/4](200-run2.md)<br/>18 steps, 2 min | [**pass** 4/4](200-run3.md)<br/>25 steps, 5 min | We're about to take on a matter that touches Vantor Holdings Corp., and before we proceed I need to run a conflict check — have we ever been adverse … |

## Criterion verdicts per task

⇄ marks a criterion whose verdict differs between runs.

### 048

**firm-knowledge/tasks/048**: [run1](048-run1.md) fail 3/4, [run2](048-run2.md) fail 3/4, [run3](048-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Belmont Ridge Bank 1045-00001 | pass | pass | pass |
| C-002 Proof document — 1045-00001 (use of proceeds) | pass | pass | pass |
| C-003 Proof document — 1045-00001 (closing) | pass | pass | pass |
| C-004 Qualifying set — precision ⇄ | **FAIL** | **FAIL** | pass |

Criteria that differ between runs (⇄): C-004.

### 066

**firm-knowledge/tasks/066**: [run1](066-run1.md) fail 8/9, [run2](066-run2.md) pass 9/9, [run3](066-run3.md) fail 8/9

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Pellegrino 1027-00002 | pass | pass | pass |
| C-002 Proof document — executed LPA | pass | pass | pass |
| C-003 Proof document — key terms memo ⇄ | pass | pass | **FAIL** |
| C-004 Proof document — side letter | pass | pass | pass |
| C-005 Proof document — subscription agreement ⇄ | **FAIL** | pass | pass |
| C-006 Proof document — closing checklist | pass | pass | pass |
| C-007 Answer — precision | pass | pass | pass |
| C-008 Fact — LPA operative date | pass | pass | pass |
| C-009 Fact — LPAC established under Section 9.1 | pass | pass | pass |

Criteria that differ between runs (⇄): C-003, C-005.

### 072

**firm-knowledge/tasks/072**: [run1](072-run1.md) pass 4/4, [run2](072-run2.md) fail 3/4, [run3](072-run3.md) fail 3/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Penterra Pharmaceuticals 1018-00004 | pass | pass | pass |
| C-002 Qualifying matter — Thornwick Medical Research Institute 1029-00001 | pass | pass | pass |
| C-003 Qualifying matter — Solstice Biomedical 1037-00002 | pass | pass | pass |
| C-004 Qualifying set — precision ⇄ | pass | **FAIL** | **FAIL** |

Criteria that differ between runs (⇄): C-004.

### 082

**firm-knowledge/tasks/082**: [run1](082-run1.md) pass 1/1, [run2](082-run2.md) fail 0/1, [run3](082-run3.md) fail 0/1

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 No qualifying semiconductor injunction matters ⇄ | pass | **FAIL** | **FAIL** |

Criteria that differ between runs (⇄): C-001.

### 104

**firm-knowledge/tasks/104**: [run1](104-run1.md) fail 0/3, [run2](104-run2.md) fail 0/3, [run3](104-run3.md) pass 3/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Aurelius Media 1017-00004 ⇄ | **FAIL** | **FAIL** | pass |
| C-002 Proof document — 1017-00004 ⇄ | **FAIL** | **FAIL** | pass |
| C-003 Qualifying set — precision ⇄ | **FAIL** | **FAIL** | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003.

### 137

**firm-knowledge/tasks/137**: [run1](137-run1.md) fail 3/4, [run2](137-run2.md) fail 2/4, [run3](137-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — 1018-00008 | pass | pass | pass |
| C-002 Proof document — draft counterclaim | pass | pass | pass |
| C-003 Proof document — pre-litigation SP demand ⇄ | pass | **FAIL** | pass |
| C-004 Qualifying set — precision ⇄ | **FAIL** | **FAIL** | pass |

Criteria that differ between runs (⇄): C-003, C-004.

### 162

**firm-knowledge/tasks/162**: [run1](162-run1.md) pass 4/4, [run2](162-run2.md) fail 0/4, [run3](162-run3.md) fail 0/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Solstice Biomedical 1037-00001 ⇄ | pass | **FAIL** | **FAIL** |
| C-002 Offering document ⇄ | pass | **FAIL** | **FAIL** |
| C-003 Proof document — closing deliverable (any one) ⇄ | pass | **FAIL** | **FAIL** |
| C-004 Qualifying set — precision ⇄ | pass | **FAIL** | **FAIL** |

Criteria that differ between runs (⇄): C-001, C-002, C-003, C-004.

### 210

**firm-knowledge/tasks/210**: [run1](210-run1.md) fail 4/15, [run2](210-run2.md) pass 15/15, [run3](210-run3.md) fail 3/15

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Cascade Retail is included ⇄ | **FAIL** | pass | **FAIL** |
| C-002 Cascade Retail matter count ⇄ | **FAIL** | pass | **FAIL** |
| C-003 Lumos Analytics is included | pass | pass | pass |
| C-004 Lumos Analytics matter count | pass | pass | pass |
| C-005 Quorum Insurance is included ⇄ | **FAIL** | pass | **FAIL** |
| C-006 Quorum Insurance matter count ⇄ | **FAIL** | pass | **FAIL** |
| C-007 Dunmore Energy is included at the cutoff ⇄ | **FAIL** | pass | pass |
| C-008 Dunmore Energy matter count ⇄ | pass | pass | **FAIL** |
| C-009 Aurelius Media is included at the cutoff ⇄ | **FAIL** | pass | **FAIL** |
| C-010 Aurelius Media matter count ⇄ | **FAIL** | pass | **FAIL** |
| C-011 Penterra Pharma is included at the cutoff ⇄ | **FAIL** | pass | **FAIL** |
| C-012 Penterra Pharma matter count ⇄ | pass | pass | **FAIL** |
| C-013 Three clients share the highest count ⇄ | **FAIL** | pass | **FAIL** |
| C-014 Three-way tie at the top-five cutoff ⇄ | **FAIL** | pass | **FAIL** |
| C-015 Top group — client-level precision ⇄ | **FAIL** | pass | **FAIL** |

Criteria that differ between runs (⇄): C-001, C-002, C-005, C-006, C-007, C-008, C-009, C-010, C-011, C-012, C-013, C-014, C-015.

### 028

**firm-knowledge/tasks/028**: [run1](028-run1.md) fail 5/6, [run2](028-run2.md) pass 6/6, [run3](028-run3.md) pass 6/6

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Crestline Packaging 1006-00002 | pass | pass | pass |
| C-002 Qualifying matter — Greenfield Ag 1020-00002 | pass | pass | pass |
| C-003 Qualifying matter — Driftwood ARF 1024-00001 | pass | pass | pass |
| C-004 Qualifying matter — Meridian Consumer 1011-00002 | pass | pass | pass |
| C-005 Qualifying matter — Thalassa Shipping 1044-00003 | pass | pass | pass |
| C-006 Qualifying set — precision ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-006.

### 167

**firm-knowledge/tasks/167**: [run1](167-run1.md) fail 4/5, [run2](167-run2.md) pass 5/5, [run3](167-run3.md) pass 5/5

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Ardent Capital Partners 1001-00004 | pass | pass | pass |
| C-002 Qualifying matter — Harrowgate PE 1003-00003 | pass | pass | pass |
| C-003 Qualifying matter — Cascade Retail 1038-00009 ⇄ | **FAIL** | pass | pass |
| C-004 Qualifying matter — Solara Digital 1041-00003 | pass | pass | pass |
| C-005 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-003.

### 185

**firm-knowledge/tasks/185**: [run1](185-run1.md) fail 0/4, [run2](185-run2.md) pass 4/4, [run3](185-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Cascade Retail 1038-00003 ⇄ | **FAIL** | pass | pass |
| C-002 Matter subject — 1038-00003 ⇄ | **FAIL** | pass | pass |
| C-003 Matter open date — 1038-00003 ⇄ | **FAIL** | pass | pass |
| C-004 Qualifying set — precision ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003, C-004.

### 192

**firm-knowledge/tasks/192**: [run1](192-run1.md) pass 10/10, [run2](192-run2.md) fail 9/10, [run3](192-run3.md) pass 10/10

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Ardent Capital Partners 1001-00004 | pass | pass | pass |
| C-002 Qualifying matter — Ardent Capital Partners 1001-00005 | pass | pass | pass |
| C-003 Qualifying matter — Harrowgate PE 1003-00003 | pass | pass | pass |
| C-004 Qualifying matter — Harrowgate PE 1003-00004 | pass | pass | pass |
| C-005 Qualifying matter — Lumos Analytics 1008-00008 | pass | pass | pass |
| C-006 Qualifying matter — Penterra Pharma 1018-00003 | pass | pass | pass |
| C-007 Qualifying matter — Halcyon Semi 1032-00005 | pass | pass | pass |
| C-008 Qualifying matter — Solara Digital 1041-00003 | pass | pass | pass |
| C-009 Qualifying matter — Brightfield Cloud 1042-00004 | pass | pass | pass |
| C-010 Qualifying set — precision ⇄ | pass | **FAIL** | pass |

Criteria that differ between runs (⇄): C-010.

### 198

**firm-knowledge/tasks/198**: [run1](198-run1.md) fail 3/4, [run2](198-run2.md) pass 4/4, [run3](198-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Harrowgate PE 1003-00003 | pass | pass | pass |
| C-002 Qualifying matter — Nexford Industrial 1005-00001 | pass | pass | pass |
| C-003 Qualifying matter — Solara Digital 1041-00003 | pass | pass | pass |
| C-004 Qualifying set — precision ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-004.

### 200

**firm-knowledge/tasks/200**: [run1](200-run1.md) pass 4/4, [run2](200-run2.md) fail 3/4, [run3](200-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Stonefield Logistics 1012-00005 | pass | pass | pass |
| C-002 Qualifying matter — Ironside Capital 1023-00002 | pass | pass | pass |
| C-003 Qualifying matter — Cascade Retail 1038-00007 ⇄ | pass | **FAIL** | pass |
| C-004 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-003.

Regenerate:

```bash
python3 benchmarks/harvey/readable_trace.py --runs run1=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-20261110T175632Z run2=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-rep2-20261112T122308Z run3=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-rep3-20261112T141312Z --out runs/analysis/hv-lunahigh-train80-flip14 --tasks firm-knowledge/tasks/048 firm-knowledge/tasks/066 firm-knowledge/tasks/072 firm-knowledge/tasks/082 firm-knowledge/tasks/104 firm-knowledge/tasks/137 firm-knowledge/tasks/162 firm-knowledge/tasks/210 firm-knowledge/tasks/028 firm-knowledge/tasks/167 firm-knowledge/tasks/185 firm-knowledge/tasks/192 firm-knowledge/tasks/198 firm-knowledge/tasks/200
```
