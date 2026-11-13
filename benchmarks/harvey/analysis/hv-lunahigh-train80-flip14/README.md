# Harvey FK, Luna high, base harness: the 32 train tasks whose all-pass flips across three runs

Train = 160 tasks (benchmarks/harvey/splits-ahe-160-20-70.json, `ahe160:train`: the 80 AHE train tasks + the 80 tasks the AHE split left unused; val 20 and test 70 unchanged), three runs of the base harness with GPT-5.6 Luna high (main's three-run baseline, benchmarks/harvey/RESULTS.md): 106 tasks fail in all three runs, 22 pass in all three, these 32 pass in one or two. **Original 80 AHE train tasks (first 14 rows, analysed in ANALYSIS.md):** 8 pass once (048 066 072 082 104 137 162 210), 6 pass twice (028 167 185 192 198 200). **Added 80 tasks (last 18 rows, new 2026-11-13):** 11 pass once (051 071 085 107 120 133 139 153 216 229 233), 7 pass twice (038 044 083 088 208 231 235).

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
| [firm-knowledge/tasks/051](#051) | [fail 1/3](051-run1.md)<br/>44 steps, 9 min | [fail 1/3](051-run2.md)<br/>43 steps, 9 min | [**pass** 3/3](051-run3.md)<br/>17 steps, 3 min | A client is asking us to structure their next offering on a best-efforts basis, and before we advise I want to check our own track record — have we e… |
| [firm-knowledge/tasks/071](#071) | [fail 6/7](071-run1.md)<br/>22 steps, 6 min | [fail 6/7](071-run2.md)<br/>50 steps, 10 min | [**pass** 7/7](071-run3.md)<br/>29 steps, 5 min | For a CLE session on human-subjects research, I want work-product examples. Pull our Healthcare & Life Sciences matters that involved informed consen… |
| [firm-knowledge/tasks/085](#085) | [**pass** 6/6](085-run1.md)<br/>22 steps, 5 min | [fail 5/6](085-run2.md)<br/>21 steps, 3 min | [fail 5/6](085-run3.md)<br/>29 steps, 3 min | I'm drafting a risk memo on our patent-litigation exposure and need a baseline figure — how often do we see willful infringement alleged in our paten… |
| [firm-knowledge/tasks/107](#107) | [**pass** 3/3](107-run1.md)<br/>12 steps, 1 min | [fail 2/3](107-run2.md)<br/>11 steps, 2 min | [fail 2/3](107-run3.md)<br/>18 steps, 2 min | We just won a default judgment for a client who's now weighing whether to settle the collection rather than keep chasing it — have we ever settled a … |
| [firm-knowledge/tasks/120](#120) | [fail 4/5](120-run1.md)<br/>23 steps, 7 min | [**pass** 5/5](120-run2.md)<br/>20 steps, 4 min | [fail 4/5](120-run3.md)<br/>28 steps, 7 min | A client weighing whether to seek a preliminary injunction wants to know our track record. Pull the general-litigation matters where we sought a prel… |
| [firm-knowledge/tasks/133](#133) | [**pass** 13/13](133-run1.md)<br/>40 steps, 12 min | [fail 11/13](133-run2.md)<br/>25 steps, 5 min | [fail 11/13](133-run3.md)<br/>48 steps, 12 min | We're heading into escrow negotiations on a new acquisition and I want a market check against our own deal history — find the M&A matters where we ag… |
| [firm-knowledge/tasks/139](#139) | [fail 8/9](139-run1.md)<br/>42 steps, 9 min | [**pass** 9/9](139-run2.md)<br/>55 steps, 9 min | [fail 7/9](139-run3.md)<br/>31 steps, 6 min | The buyer on a deal I'm negotiating wants an escrow well above 10% of the total deal consideration, and before I push back I want to see how we've ha… |
| [firm-knowledge/tasks/153](#153) | [fail 9/10](153-run1.md)<br/>32 steps, 8 min | [**pass** 10/10](153-run2.md)<br/>33 steps, 6 min | [fail 9/10](153-run3.md)<br/>22 steps, 8 min | I'm sizing up how common earnouts are across our M&A practice for an internal report. Counting the deals whose final executed deal document carries a… |
| [firm-knowledge/tasks/216](#216) | [fail 1/3](216-run1.md)<br/>39 steps, 5 min | [**pass** 3/3](216-run2.md)<br/>35 steps, 9 min | [fail 1/3](216-run3.md)<br/>30 steps, 4 min | Pinnacle Venture Fund II is one of our key sponsor relationships, and I want to understand our track record with their portfolio before our next chec… |
| [firm-knowledge/tasks/229](#229) | [fail 0/3](229-run1.md)<br/>17 steps, 4 min | [fail 0/3](229-run2.md)<br/>16 steps, 2 min | [**pass** 3/3](229-run3.md)<br/>24 steps, 4 min | I'm papering a new lease and want to work off our most recent form. What's the latest Real Estate matter where we negotiated an SNDA, and can you pul… |
| [firm-knowledge/tasks/233](#233) | [**pass** 3/3](233-run1.md)<br/>28 steps, 7 min | [fail 2/3](233-run2.md)<br/>21 steps, 5 min | [fail 2/3](233-run3.md)<br/>43 steps, 7 min | I'm assembling our tax-opinion precedent file. Pull every opinion we've issued at the more-likely-than-not level. Output: write your complete answer … |
| [firm-knowledge/tasks/038](#038) | [**pass** 15/15](038-run1.md)<br/>36 steps, 7 min | [**pass** 15/15](038-run2.md)<br/>30 steps, 8 min | [fail 11/15](038-run3.md)<br/>41 steps, 9 min | I'm papering the underwriting agreement for a new offering and want to see how we've structured the over-allotment option in past deals. Pull every C… |
| [firm-knowledge/tasks/044](#044) | [fail 0/4](044-run1.md)<br/>17 steps, 3 min | [**pass** 4/4](044-run2.md)<br/>27 steps, 4 min | [**pass** 4/4](044-run3.md)<br/>23 steps, 5 min | I'm building out our capital markets pitch deck and want to lead with our biggest closed deal — who was the lead underwriter on our largest completed… |
| [firm-knowledge/tasks/083](#083) | [**pass** 6/6](083-run1.md)<br/>27 steps, 6 min | [**pass** 6/6](083-run2.md)<br/>36 steps, 6 min | [fail 4/6](083-run3.md)<br/>33 steps, 8 min | I'm assessing our claim-construction experience across the IP docket ahead of a staffing conversation. How many of our IP litigations actually reache… |
| [firm-knowledge/tasks/088](#088) | [fail 3/4](088-run1.md)<br/>36 steps, 7 min | [**pass** 4/4](088-run2.md)<br/>27 steps, 7 min | [**pass** 4/4](088-run3.md)<br/>19 steps, 4 min | I'm building out an exclusive-license clause bank for the IP group — do we have any matters where we granted an exclusive license, and if so, can you… |
| [firm-knowledge/tasks/208](#208) | [**pass** 18/18](208-run1.md)<br/>43 steps, 7 min | [fail 10/18](208-run2.md)<br/>37 steps, 7 min | [**pass** 18/18](208-run3.md)<br/>32 steps, 6 min | I'm staffing a new IP pitch — which partner has the most IP matters to their name, counting both the ones they led and the ones they billed? Walk me … |
| [firm-knowledge/tasks/231](#231) | [**pass** 3/3](231-run1.md)<br/>36 steps, 6 min | [**pass** 3/3](231-run2.md)<br/>21 steps, 3 min | [fail 2/3](231-run3.md)<br/>33 steps, 8 min | A 'should'-level tax opinion is due on a new deal, and I want to see how we've framed that analysis before committing to language — which of our Tax … |
| [firm-knowledge/tasks/235](#235) | [**pass** 5/5](235-run1.md)<br/>47 steps, 8 min | [**pass** 5/5](235-run2.md)<br/>32 steps, 5 min | [fail 3/5](235-run3.md)<br/>45 steps, 16 min | I'm pulling together a practice metric on our Tax practice's opinion work — counting the opinions issued in matters filed in our Tax practice, each c… |

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

### 051

**firm-knowledge/tasks/051**: [run1](051-run1.md) fail 1/3, [run2](051-run2.md) fail 1/3, [run3](051-run3.md) pass 3/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Fairwater REIT 1036-00002 ⇄ | **FAIL** | **FAIL** | pass |
| C-002 Proof documents — 1036-00002 ⇄ | pass | **FAIL** | pass |
| C-003 Qualifying set — precision ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003.

### 071

**firm-knowledge/tasks/071**: [run1](071-run1.md) fail 6/7, [run2](071-run2.md) fail 6/7, [run3](071-run3.md) pass 7/7

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Penterra Pharmaceuticals 1018-00004 | pass | pass | pass |
| C-002 Qualifying matter — Thornwick Medical Research Institute 1029-00001 | pass | pass | pass |
| C-003 Qualifying matter — Solstice Biomedical 1037-00002 | pass | pass | pass |
| C-004 Proof document — 1018-00004 | pass | pass | pass |
| C-005 Proof document — 1029-00001 | pass | pass | pass |
| C-006 Proof document — 1037-00002 | pass | pass | pass |
| C-007 Qualifying set — precision ⇄ | **FAIL** | **FAIL** | pass |

Criteria that differ between runs (⇄): C-007.

### 085

**firm-knowledge/tasks/085**: [run1](085-run1.md) pass 6/6, [run2](085-run2.md) fail 5/6, [run3](085-run3.md) fail 5/6

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Vantage Mobility 1007-00003 ⇄ | pass | **FAIL** | **FAIL** |
| C-002 Qualifying matter — GenomeDx 1013-00005 | pass | pass | pass |
| C-003 Qualifying matter — Optiwave 1014-00003 | pass | pass | pass |
| C-004 Qualifying matter — Optiwave 1014-00004 | pass | pass | pass |
| C-005 Qualifying matter — Solstice Biomedical 1037-00004 | pass | pass | pass |
| C-006 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-001.

### 107

**firm-knowledge/tasks/107**: [run1](107-run1.md) pass 3/3, [run2](107-run2.md) fail 2/3, [run3](107-run3.md) fail 2/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Post-judgment settlement — Stonefield 1012-00006 | pass | pass | pass |
| C-002 Proof document — 1012-00006 | pass | pass | pass |
| C-003 Answer — precision ⇄ | pass | **FAIL** | **FAIL** |

Criteria that differ between runs (⇄): C-003.

### 120

**firm-knowledge/tasks/120**: [run1](120-run1.md) fail 4/5, [run2](120-run2.md) pass 5/5, [run3](120-run3.md) fail 4/5

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Driftwood ARF 1024-00003 | pass | pass | pass |
| C-002 Proof document — PI motion | pass | pass | pass |
| C-003 Proof document — ruling record | pass | pass | pass |
| C-004 Fact — ruling granting the preliminary injunction | pass | pass | pass |
| C-005 Qualifying set — precision ⇄ | **FAIL** | pass | **FAIL** |

Criteria that differ between runs (⇄): C-005.

### 133

**firm-knowledge/tasks/133**: [run1](133-run1.md) pass 13/13, [run2](133-run2.md) fail 11/13, [run3](133-run3.md) fail 11/13

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — 1001-00003 | pass | pass | pass |
| C-002 Qualifying matter — 1005-00006 ⇄ | pass | **FAIL** | **FAIL** |
| C-003 Qualifying matter — 1011-00006 | pass | pass | pass |
| C-004 Qualifying matter — 1013-00006 | pass | pass | pass |
| C-005 Qualifying matter — 1038-00008 | pass | pass | pass |
| C-006 Qualifying matter — 1042-00004 | pass | pass | pass |
| C-007 Proof document — 1001-00003 | pass | pass | pass |
| C-008 Proof document — 1005-00006 ⇄ | pass | **FAIL** | **FAIL** |
| C-009 Proof document — 1011-00006 | pass | pass | pass |
| C-010 Proof document — 1013-00006 | pass | pass | pass |
| C-011 Proof document — 1038-00008 | pass | pass | pass |
| C-012 Proof document — 1042-00004 | pass | pass | pass |
| C-013 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-002, C-008.

### 139

**firm-knowledge/tasks/139**: [run1](139-run1.md) fail 8/9, [run2](139-run2.md) pass 9/9, [run3](139-run3.md) fail 7/9

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — 1006-00007 ⇄ | pass | pass | **FAIL** |
| C-002 Qualifying matter — 1006-00008 | pass | pass | pass |
| C-003 Qualifying matter — 1007-00006 | pass | pass | pass |
| C-004 Qualifying matter — 1008-00008 | pass | pass | pass |
| C-005 Qualifying matter — 1017-00006 | pass | pass | pass |
| C-006 Qualifying matter — 1018-00008 | pass | pass | pass |
| C-007 Qualifying matter — 1037-00006 | pass | pass | pass |
| C-008 Qualifying matter — 1039-00004 ⇄ | **FAIL** | pass | **FAIL** |
| C-009 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-001, C-008.

### 153

**firm-knowledge/tasks/153**: [run1](153-run1.md) fail 9/10, [run2](153-run2.md) pass 10/10, [run3](153-run3.md) fail 9/10

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — 1001-00003 | pass | pass | pass |
| C-002 Qualifying matter — 1005-00006 | pass | pass | pass |
| C-003 Qualifying matter — 1006-00007 | pass | pass | pass |
| C-004 Qualifying matter — 1008-00008 | pass | pass | pass |
| C-005 Qualifying matter — 1009-00003 | pass | pass | pass |
| C-006 Qualifying matter — 1013-00006 | pass | pass | pass |
| C-007 Qualifying matter — 1037-00006 | pass | pass | pass |
| C-008 Qualifying matter — 1042-00004 ⇄ | **FAIL** | pass | **FAIL** |
| C-009 Qualifying matter — 1046-00001 | pass | pass | pass |
| C-010 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-008.

### 216

**firm-knowledge/tasks/216**: [run1](216-run1.md) fail 1/3, [run2](216-run2.md) pass 3/3, [run3](216-run3.md) fail 1/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Arbor Health Technologies 1010-00002 (completed IPO) ⇄ | **FAIL** | pass | **FAIL** |
| C-002 Qualifying matter — Skybridge Fintech 1009-00003 (closed de-SPAC) ⇄ | **FAIL** | pass | **FAIL** |
| C-003 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-001, C-002.

### 229

**firm-knowledge/tasks/229**: [run1](229-run1.md) fail 0/3, [run2](229-run2.md) fail 0/3, [run3](229-run3.md) pass 3/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Metropolitan Transit Development Corp. 1031-00004 ⇄ | **FAIL** | **FAIL** | pass |
| C-002 Document — the executed SNDA ⇄ | **FAIL** | **FAIL** | pass |
| C-003 Latest-matter answer — precision ⇄ | **FAIL** | **FAIL** | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003.

### 233

**firm-knowledge/tasks/233**: [run1](233-run1.md) pass 3/3, [run2](233-run2.md) fail 2/3, [run3](233-run3.md) fail 2/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Ardent Capital Partners 1001-00006 | pass | pass | pass |
| C-002 Proof document — 1001-00006 | pass | pass | pass |
| C-003 Qualifying set — precision ⇄ | pass | **FAIL** | **FAIL** |

Criteria that differ between runs (⇄): C-003.

### 038

**firm-knowledge/tasks/038**: [run1](038-run1.md) pass 15/15, [run2](038-run2.md) pass 15/15, [run3](038-run3.md) fail 11/15

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Pinnacle Ventures 1002-00001 | pass | pass | pass |
| C-002 Qualifying matter — Arbor Health Tech 1010-00002 | pass | pass | pass |
| C-003 Qualifying matter — Optiwave 1014-00001 ⇄ | pass | pass | **FAIL** |
| C-004 Qualifying matter — Penterra Pharma 1018-00001 | pass | pass | pass |
| C-005 Qualifying matter — Pellegrino Capital 1027-00001 | pass | pass | pass |
| C-006 Qualifying matter — Redstone Gaming 1033-00002 | pass | pass | pass |
| C-007 Qualifying matter — Solstice Biomedical 1037-00001 ⇄ | pass | pass | **FAIL** |
| C-008 Qualifying set — precision | pass | pass | pass |
| C-009 Executed documents — 1002-00001 | pass | pass | pass |
| C-010 Executed documents — 1010-00002 | pass | pass | pass |
| C-011 Executed documents — 1014-00001 ⇄ | pass | pass | **FAIL** |
| C-012 Executed documents — 1018-00001 | pass | pass | pass |
| C-013 Executed documents — 1027-00001 | pass | pass | pass |
| C-014 Executed documents — 1033-00002 | pass | pass | pass |
| C-015 Executed documents — 1037-00001 ⇄ | pass | pass | **FAIL** |

Criteria that differ between runs (⇄): C-003, C-007, C-011, C-015.

### 044

**firm-knowledge/tasks/044**: [run1](044-run1.md) fail 0/4, [run2](044-run2.md) pass 4/4, [run3](044-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Dunmore Energy 1016-00003 ⇄ | **FAIL** | pass | pass |
| C-002 Lead underwriter ⇄ | **FAIL** | pass | pass |
| C-003 Qualifying set — precision ⇄ | **FAIL** | pass | pass |
| C-004 Proof document — 1016-00003 ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003, C-004.

### 083

**firm-knowledge/tasks/083**: [run1](083-run1.md) pass 6/6, [run2](083-run2.md) pass 6/6, [run3](083-run3.md) fail 4/6

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Vantage Mobility 1007-00003 ⇄ | pass | pass | **FAIL** |
| C-002 Qualifying matter — Optiwave 1014-00003 | pass | pass | pass |
| C-003 Qualifying matter — Optiwave 1014-00004 | pass | pass | pass |
| C-004 Qualifying matter — Solstice Biomedical 1037-00004 | pass | pass | pass |
| C-005 Count ⇄ | pass | pass | **FAIL** |
| C-006 Qualifying set — precision | pass | pass | pass |

Criteria that differ between runs (⇄): C-001, C-005.

### 088

**firm-knowledge/tasks/088**: [run1](088-run1.md) fail 3/4, [run2](088-run2.md) pass 4/4, [run3](088-run3.md) pass 4/4

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Penterra Pharmaceuticals 1018-00006 | pass | pass | pass |
| C-002 Proof document — executed Exclusive License Agreement | pass | pass | pass |
| C-003 Related executed agreements — any one suffices | pass | pass | pass |
| C-004 Qualifying set — precision ⇄ | **FAIL** | pass | pass |

Criteria that differ between runs (⇄): C-004.

### 208

**firm-knowledge/tasks/208**: [run1](208-run1.md) pass 18/18, [run2](208-run2.md) fail 10/18, [run3](208-run3.md) pass 18/18

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Practice-lead pick — Delgado (or Delgado–Bloom tie) ⇄ | pass | **FAIL** | pass |
| C-002 Qualifying matter — Vantage Mobility 1007-00003 ⇄ | pass | **FAIL** | pass |
| C-003 Qualifying matter — Lumos Analytics 1008-00005 ⇄ | pass | **FAIL** | pass |
| C-004 Qualifying matter — Aurelius Media 1017-00003 | pass | pass | pass |
| C-005 Qualifying matter — Penterra Pharma 1018-00006 ⇄ | pass | **FAIL** | pass |
| C-006 Qualifying matter — Verimark Hospitality 1021-00004 | pass | pass | pass |
| C-007 Qualifying matter — Solstice Biomedical 1037-00004 | pass | pass | pass |
| C-008 Qualifying matter — Meridian Consumer 1011-00003 | pass | pass | pass |
| C-009 Qualifying matter — Optiwave 1014-00003 | pass | pass | pass |
| C-010 Qualifying matter — Optiwave 1014-00004 | pass | pass | pass |
| C-011 Qualifying matter — Marguerite Fonseca 1035-00003 | pass | pass | pass |
| C-012 Qualifying matter — Solstice Biomedical 1037-00005 | pass | pass | pass |
| C-013 Qualifying matter — Crestline Packaging 1006-00004 ⇄ | pass | **FAIL** | pass |
| C-014 Qualifying matter — Genome Dx 1013-00005 | pass | pass | pass |
| C-015 Qualifying matter — Optiwave 1014-00005 | pass | pass | pass |
| C-016 Qualifying matter — Redstone Gaming 1033-00004 ⇄ | pass | **FAIL** | pass |
| C-017 Qualifying matter — Brightfield Cloud 1042-00003 ⇄ | pass | **FAIL** | pass |
| C-018 Qualifying set — precision ⇄ | pass | **FAIL** | pass |

Criteria that differ between runs (⇄): C-001, C-002, C-003, C-005, C-013, C-016, C-017, C-018.

### 231

**firm-knowledge/tasks/231**: [run1](231-run1.md) pass 3/3, [run2](231-run2.md) pass 3/3, [run3](231-run3.md) fail 2/3

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying matter — Calloway-Briggs Renewables 1015-00005 | pass | pass | pass |
| C-002 Qualifying matter — Solstice Biomedical 1037-00007 | pass | pass | pass |
| C-003 Qualifying set — precision ⇄ | pass | pass | **FAIL** |

Criteria that differ between runs (⇄): C-003.

### 235

**firm-knowledge/tasks/235**: [run1](235-run1.md) pass 5/5, [run2](235-run2.md) pass 5/5, [run3](235-run3.md) fail 3/5

| Criterion | run1 | run2 | run3 |
|---|---|---|---|
| C-001 Qualifying opinion — Calloway-Briggs Renewables 1015-00005 (Pinehurst) | pass | pass | pass |
| C-002 Qualifying opinion — Calloway-Briggs Renewables 1015-00005 (Ridgeline) | pass | pass | pass |
| C-003 Qualifying opinion — Solstice Biomedical 1037-00007 | pass | pass | pass |
| C-004 Counts — will vs should ⇄ | pass | pass | **FAIL** |
| C-005 Qualifying set — precision ⇄ | pass | pass | **FAIL** |

Criteria that differ between runs (⇄): C-004, C-005.

Regenerate:

```bash
python3 benchmarks/harvey/readable_trace.py --runs run1=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-20261110T175632Z run2=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-rep2-20261112T122308Z run3=/home/agarwaldi/dsh-bench-harness/runs/hv-fk250-lunahigh-rep3-20261112T141312Z --out runs/analysis/hv-lunahigh-train80-flip14 --tasks firm-knowledge/tasks/048 firm-knowledge/tasks/066 firm-knowledge/tasks/072 firm-knowledge/tasks/082 firm-knowledge/tasks/104 firm-knowledge/tasks/137 firm-knowledge/tasks/162 firm-knowledge/tasks/210 firm-knowledge/tasks/028 firm-knowledge/tasks/167 firm-knowledge/tasks/185 firm-knowledge/tasks/192 firm-knowledge/tasks/198 firm-knowledge/tasks/200 firm-knowledge/tasks/051 firm-knowledge/tasks/071 firm-knowledge/tasks/085 firm-knowledge/tasks/107 firm-knowledge/tasks/120 firm-knowledge/tasks/133 firm-knowledge/tasks/139 firm-knowledge/tasks/153 firm-knowledge/tasks/216 firm-knowledge/tasks/229 firm-knowledge/tasks/233 firm-knowledge/tasks/038 firm-knowledge/tasks/044 firm-knowledge/tasks/083 firm-knowledge/tasks/088 firm-knowledge/tasks/208 firm-knowledge/tasks/231 firm-knowledge/tasks/235
```
