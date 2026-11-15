"""firm-knowledge/tasks/210, run hv-fk250-lunahigh-rep2-20261112T122308Z (15/15, all-pass), as a script with its
judgement steps made explicit.

Built from mechanical.py (trace2script.py output: the same 32 tool calls, same order). Every decision the model took
between calls is now a @semantic function: in replay mode it returns the decision the model recorded (and the script
reproduces the run), in live mode it returns its own, version-0 answer and the later calls follow it. The functions'
docstrings say what the model decided and from what; their bodies are deliberately simple and imperfect.

Task prompt:

    I'm prepping for a relationship review and want to know where our weight is — who are our top five clients by
    number of matters, with the counts?

    Output: write your complete answer to `response.md` — a single self-contained markdown file with your findings,
    the matters/documents you relied on, and your reasoning.

How the run solved it: count matter FOLDERS per four-digit client series (all 266, no document reading), keep the top
five with ties, then read engagement letters only to name each series' client and to check odd matters.
"""

import json
import re
from collections import Counter
from pathlib import Path

from semantic import semantic

TASK_ID = "firm-knowledge/tasks/210"
REC = json.loads((Path(__file__).parent / "recorded.json").read_text())   # the model's own texts, for replay

CORP = re.compile(r"\b([A-Z][A-Za-z&'.\-]*(?:\s+(?:[A-Z][A-Za-z&'.\-]*|of|and|&)){0,6}\s+"
                  r"(?:Inc\.|Corp\.|Corporation|LLC|L\.P\.|LP|Ltd\.|Limited|PLC|plc|Co\.|Company))")
FIRM = ("Calderwood", "Harkness")


# ═══ Semantic functions (version 0) ═══════════════════════════════════════════════════════════════════════════════

@semantic
def sample_letters(*listings: str, k: int = 4) -> list[str]:
    """Pick a few engagement letters of different client series to learn how a letter names its client.
    Model, steps 4-5: the full list was capped at 100 and its saved copy unreadable, so it parsed four letters
    (series 1001, 1002, 1003, 1007) from the listings it had."""
    seen, out = set(), []
    for line in sorted({l for x in listings for l in x.splitlines() if "/engagement-letter" in l and l.endswith(".docx")}):
        series = line.split("/")[2][:4]
        if series not in seen:
            seen.add(series)
            out.append(line)
    return out[:k]


@semantic
def top_series(count_output: str, n: int = 5) -> list[str]:
    """The client series to report: the n largest by number of matter folders, every series tied at the cut kept.
    Model, steps 8-9: 1008, 1025, 1038 (10 each), then 1016, 1017, 1018 (9 each, three-way tie for 5th)."""
    counts = [(m.group(1), int(m.group(2))) for m in re.finditer(r"(?m)^(\d{4}) (\d+)$", count_output)]
    counts.sort(key=lambda x: -x[1])
    if len(counts) <= n:
        return [s for s, _ in counts]
    cut = counts[n - 1][1]
    return [s for s, c in counts if c >= cut]


@semantic
def snippet_windows(grep_output: str, gap: int = 40) -> list[list[int]]:
    """Which parts of engagement_snippets.txt to read: one window per block of adjacent hits for the top series.
    Model, step 10: four windows, (640, 150), (1413, 385), (2331, 170), (3284, 190)."""
    lines = sorted(int(n) for n in re.findall(r"Line (\d+): ###", grep_output))
    blocks, cur = [], []
    for n in lines:
        if cur and n - cur[-1] > gap:
            blocks.append(cur)
            cur = []
        cur.append(n)
    if cur:
        blocks.append(cur)
    step = int(sum(b - a for a, b in zip(lines, lines[1:]) if b - a <= gap) / max(1, len(lines) - len(blocks))) if lines else 15
    return [[b[0], b[-1] - b[0] + step] for b in blocks]


@semantic
def client_names(series: list[str], snippets: str) -> dict[str, str]:
    """Name each series' client from its engagement letters (the most common company name, not the firm's).
    Model, steps 10-15: Lumos Analytics Inc., Quorum Insurance Holdings Corp., Cascade Retail Holdings Inc., Dunmore
    Energy Holdings Ltd., Aurelius Global Media Group PLC, Penterra Pharmaceuticals Corp."""
    names = {}
    for s in series:
        parts = re.split(r"(?m)^\d+: ### ", snippets)
        per_letter = [set(CORP.findall(p)) for p in parts if p.startswith(s + "-")]
        c = Counter(n.strip() for letter in per_letter for n in letter if not any(f in n for f in FIRM))
        names[s] = max(c.items(), key=lambda x: (x[1], len(x[0])))[0] if c else f"(series {s})"
    return names


@semantic
def matters_to_verify(series: list[str], letters_listing: str, snippets: str) -> list[str]:
    """Matters whose client needs a second look: a top-series matter with no engagement letter, or with both a
    draft and an executed letter, and any other matter number cited inside the top series' letters.
    Model, steps 12-13: 1017-00001 (no letter), 1018-00009, 1025-00003, and 1043-00002 (cited in 1017-00006's letter)."""
    out = []
    for m, files in re.findall(r"(?m)^(\d{4}-\d{5})\s?(.*)$", letters_listing):
        if m[:4] in series and (not files.strip() or ("draft" in files and "executed" in files) or "executed" in files):
            out.append(m)
    cited = {x for x in re.findall(r"Matter No\.:?\s*(\d{4}-\d{5})", snippets) if x[:4] not in series}
    return out + sorted(cited)


@semantic
def matters_to_extract(verify: list[str], letters_listing: str) -> list[str]:
    """Of those, the matters whose documents must be read directly (no engagement letter of their own in the series).
    Model, step 13: 1017-00001 and 1043-00002."""
    has_letter = {m for m, f in re.findall(r"(?m)^(\d{4}-\d{5})\s?(.*)$", letters_listing) if f.strip()}
    return [m for m in verify if m not in has_letter]


@semantic
def compose_answer(series: list[str], count_output: str, names: dict[str, str], letters_listing: str) -> str:
    """The deliverable: ranking (ties shown), method, cross-check, and the documents relied on per client.
    Model, step 15: the recorded response.md."""
    counts = dict(re.findall(r"(?m)^(\d{4}) (\d+)$", count_output))
    total = re.search(r"matter dirs (\d+)", count_output)
    rows, rank, prev = [], 0, None
    for i, s in enumerate(series, 1):
        if counts[s] != prev:
            rank, prev = i, counts[s]
        tie = sum(1 for x in series if counts[x] == counts[s]) > 1
        rows.append(f"| {rank}{' (tie)' if tie else ''} | **{names[s]}** | **{counts[s]}** | {s}-00001 through {s}-{int(counts[s]):05d} |")
    docs = {}
    for m, files in re.findall(r"(?m)^(\d{4}-\d{5})\s?(.*)$", letters_listing):
        if m[:4] in series and files.strip():
            docs.setdefault(m[:4], []).append(files.split(" | ")[0])
    text = ["# Top clients by number of matters", "", "## Answer", "",
            "Each unique matter folder (`documents/matters/<matter-number>/`) counted once, grouped by client series.", "",
            "| Rank | Client | Matter count | Matter numbers |", "|---:|---|---:|---|", *rows, ""]
    if len(series) > 5:
        text += [f"There is a tie at the cutoff, so all {len(series)} clients in the top-five positions are shown.", ""]
    text += ["## Reasoning and verification", "",
             f"Counted all {total.group(1) if total else '?'} matter folders by their four-digit client series; "
             "named each series' client from its engagement letters.", "", "## Documents relied on", ""]
    for s in series:
        text += [f"### {names[s]} — {counts[s]} matters", ""] + [f"- `{d}`" for d in docs.get(s, [])] + [""]
    return "\n".join(text)


@semantic
def revise_answer(written: str):
    """A correction after re-reading the answer: (old, new) to replace, or None.
    Model, steps 16-17: step 3 of its reasoning named only Dunmore and Penterra among the 9-matter series; it added
    Aurelius. Version 0 makes no revision."""
    return None


# ═══ The trajectory ═══════════════════════════════════════════════════════════════════════════════════════════════

async def solve(T):
    # Step 1: plan
    await T.todo_write(_id="1.1", todos=REC["1.1"]["args"]["todos"])

    # Step 2-4: survey. The listings are capped at 100 paths; the saved full list is outside the workspace.
    s2_1 = await T.glob(_id="2.1", pattern="*")
    s3_1, s3_2, s3_3, s3_4 = await T.parallel(
        T.glob(_id="3.1", pattern="documents/matters/*/Engagement*/*"),
        T.glob(_id="3.2", pattern="documents/matters/*/Client*/*"),
        T.glob(_id="3.3", pattern="documents/matters/*/Matter*/*"),
        T.glob(_id="3.4", pattern="documents/matters/*/Engagement & Administration/*"),
    )
    spill = re.search(r"stored at: (\S+?)\. Use read", s3_1)
    await T.read(_id="4.1", file_path=spill.group(1) if spill else REC["4.1"]["args"]["file_path"], offset=1, limit=1000)

    # Step 5: learn how a letter names its client
    samples = sample_letters(s3_4, s3_1, recorded=[
        "documents/matters/1001-00001/Engagement & Administration/engagement-letter-ardent-capital.docx",
        "documents/matters/1002-00001/Engagement/engagement-letter-pinnacle-vc.docx",
        "documents/matters/1003-00002/Engagement/engagement-letter-hcp.docx",
        "documents/matters/1007-00001/Engagement/engagement-letter-vms.docx"])
    for i, path in enumerate(samples, 1):
        await T.bash(_id=f"5.{i}", command=f"parse-doc docx '{path}'", description="Parse a sample engagement letter",
                     timeoutMs=120000)

    # Step 6-7: the first 1,800 characters of every engagement letter, into one file (no path cap in a script)
    await T.bash(_id="6.1", command=STEP6, description="Extract engagement-letter text snippets", timeoutMs=120000)
    await T.read(_id="7.1", file_path="engagement_snippets.txt", offset=1, limit=250)

    # Step 8: the decisive move - count matter folders per client series (complete, nothing to time out)
    s8_1 = await T.bash(_id="8.1", command=STEP8, description="Count matter directories by client code", timeoutMs=120000)
    series = top_series(s8_1, recorded=["1008", "1025", "1038", "1016", "1017", "1018"])

    # Step 9-10: find and read the top series' letters in the snippet file
    s9_1 = await T.grep(_id="9.1", pattern=f"### ({'|'.join(series)})-", path="engagement_snippets.txt")
    windows = snippet_windows(s9_1, recorded=[[640, 150], [1413, 385], [2331, 170], [3284, 190]])
    reads = await T.parallel(*[T.read(_id=f"10.{i}", file_path="engagement_snippets.txt", offset=o, limit=n)
                               for i, (o, n) in enumerate(windows, 1)])
    snippets = "\n".join(reads)

    # Step 11: every matter of the top series and its engagement letters
    s11_1 = await T.bash(_id="11.1", command=STEP11.replace("@SERIES@", "[" + ",".join(repr(s) for s in series) + "]"),
                         description="List source engagement documents for ranked clients", timeoutMs=120000)

    # Step 12-13: matters whose client needs a second look
    verify = matters_to_verify(series, s11_1, snippets, recorded=["1017-00001", "1018-00009", "1025-00003", "1043-00002"])
    await T.glob(_id="12.1", pattern=f"documents/matters/{verify[0]}/*")      # one level: lists nothing (files sit deeper)
    await T.parallel(*[T.glob(_id=f"12.{i}", pattern=f"documents/matters/{m}/**/*") for i, m in enumerate(verify[:3], 2)])
    await T.parallel(*[T.glob(_id=f"13.{i}", pattern=f"documents/matters/{m}/**/*")
                       for i, m in enumerate([*verify[3:], verify[0]], 1)])
    extract = matters_to_extract(verify, s11_1, recorded=["1017-00001", "1043-00002"])
    s13_3 = await T.bash(_id="13.3", command=STEP13.replace("@MATTERS@", "[" + ",".join(repr(m) for m in extract) + "]"),
                         description="Inspect ambiguous Aurelius matter sources", timeoutMs=120000)
    names = client_names(series, snippets + "\n" + s13_3, recorded={
        "1008": "Lumos Analytics Inc.", "1025": "Quorum Insurance Holdings Corp.", "1038": "Cascade Retail Holdings Inc.",
        "1016": "Dunmore Energy Holdings Ltd.", "1017": "Aurelius Global Media Group PLC",
        "1018": "Penterra Pharmaceuticals Corp."})

    # Step 14-15: write the answer
    await T.todo_write(_id="14.1", todos=REC["14.1"]["args"]["todos"])
    answer = compose_answer(series, s8_1, names, s11_1, recorded=REC["15.1"]["args"]["content"])
    await T.write(_id="15.1", file_path="response.md", content=answer)

    # Step 16-17: re-read and correct
    s16_1 = await T.read(_id="16.1", file_path="output/response.md", offset=1, limit=260)
    fix = revise_answer(s16_1, recorded=[REC["17.1"]["args"]["old_string"], REC["17.1"]["args"]["new_string"]])
    if fix:
        await T.edit(_id="17.1", file_path="output/response.md", old_string=fix[0], new_string=fix[1])
    await T.todo_write(_id="18.1", todos=REC["18.1"]["args"]["todos"])
    # Step 19 said: Completed the requested analysis and saved the self-contained answer to: `output/response.md`


# ═══ The code the model wrote and ran (verbatim; @SERIES@ / @MATTERS@ are the decision-dependent parts) ═══════════

STEP6 = '''python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re
root=Path('documents/matters')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
rows=[]
for p in sorted(root.glob('*/*/engagement*.docx')):
    try:
        with ZipFile(p) as z:
            xml=z.read('word/document.xml')
        tree=ET.fromstring(xml)
        paras=[]
        for para in tree.findall('.//w:p',ns):
            txt=''.join(t.text or '' for t in para.findall('.//w:t',ns))
            if txt.strip(): paras.append(txt.strip())
        text='\\n'.join(paras)
        rows.append((p.parent.parent.name,str(p.relative_to(root)),text[:1800]))
    except Exception as e:
        rows.append((p.parent.parent.name,str(p.relative_to(root)),f'ERROR {e}'))
with open('engagement_snippets.txt','w') as f:
    for matter,path,snip in rows:
        f.write(f'### {matter} | {path}\\n{snip}\\n\\n')
print('processed',len(rows))
PY'''

STEP8 = '''python - <<'PY'
from pathlib import Path
from collections import Counter
root=Path('documents/matters')
matters=sorted({p.parts[2] for p in root.glob('*/*/*') if len(p.parts)>=3})
print('matter dirs',len(matters))
counts=Counter(m.split('-')[0] for m in matters)
for k,v in counts.most_common(): print(k,v)
PY'''

STEP11 = '''python - <<'PY'
from pathlib import Path
for prefix in @SERIES@:
 print('\\n'+prefix)
 for matter in sorted(p for p in {x.parts[2] for x in Path('documents/matters').glob(prefix+'-*/*/*')}):
  files=sorted(Path('documents/matters',matter).glob('**/engagement*.docx'))
  print(matter, ' | '.join(str(f) for f in files))
PY'''

STEP13 = '''python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for m in @MATTERS@:
 print('\\n###',m)
 for p in sorted(Path('documents/matters',m).glob('**/*')):
  if p.suffix.lower()=='.docx':
   with ZipFile(p) as z:
    tree=ET.fromstring(z.read('word/document.xml'))
   paras=[]
   for para in tree.findall('.//w:p',ns):
    s=''.join(t.text or '' for t in para.findall('.//w:t',ns)).strip()
    if s: paras.append(s)
   print(p, '\\n', '\\n'.join(paras[:8]))
PY'''
