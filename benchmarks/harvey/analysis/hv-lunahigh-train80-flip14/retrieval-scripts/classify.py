import re
ID = re.compile(r"\b(10\d\d-\d{5})\b")
EXTRACT = re.compile(r"parse-doc|ZipFile|zipfile|markitdown|pandoc|docx2txt|from docx|import docx|openpyxl|unzip|xlsx2csv", re.I)
ROOTWALK = re.compile(r"rglob\(|os\.walk|\.glob\(['\"](documents|\*\*)|Path\(['\"]documents(/matters)?/?['\"]\)|root\s*=\s*['\"]documents|documents/matters/\*|documents/\*\*|find (\./)?documents|ls -R|\bfind \.", re.I)
NAMEFILTER = re.compile(r"in (p|f|path|fp|file)\.name|\.name\.lower\(\)|\bn\s*=\s*(p|f)\.name|name\.lower\(\)|fn\.lower\(\)|f\.lower\(\)", re.I)
READS_CONTENT = re.compile(r"read_text|read_bytes|open\(|\.read\(\)", re.I)
CAP = re.compile(r"Showing \d+ of \d+|Found \d+ of \d+|Output capped|Omitted \d+ bytes|result stored at|\[output truncated", re.I)
TIMEOUT = re.compile(r"timed out after \d+ms")
GENERIC = re.compile(r"^(\*\*?/?)*\*?(\.(docx|eml|xlsx|pptx|txt|md|pdf))?$", re.I)
def cmd_of(c):
    a = c["args"]
    if isinstance(a, dict):
        return a.get("command") or a.get("pattern") or a.get("file_path") or a.get("path") or ""
    return str(a)
def classify(c):
    n = c["name"]; a = c["args"] if isinstance(c["args"], dict) else {}
    if n == "glob":
        p = a.get("pattern", ""); base = (a.get("path") or "") + "/" + p
        if ID.findall(base) or re.search(r"10\d\d-\*|10\d\d-0", base): return "glob:matter-scoped"
        tail = re.sub(r"^(documents/)?(matters/)?", "", p)
        tail = re.sub(r"\*/", "", tail)
        return "glob:enumerate" if GENERIC.match(tail) else "glob:name-search"
    if n == "grep":
        path = (a.get("path") or "") + " " + (a.get("glob") or "")
        if "documents" in path or path.strip() in ("", ".", "./"): return "grep:raw-corpus"
        return "grep:own-text"
    if n == "read":
        fp = a.get("file_path", "")
        if "/tmp/dsh-spill" in fp: return "read:spill(fails)"
        if "documents/matters" in fp: return "read:corpus-file"
        return "read:own-file"
    if n == "bash":
        cmd = a.get("command", "")
        ids = set(ID.findall(cmd)); walk = bool(ROOTWALK.search(cmd))
        if EXTRACT.search(cmd):
            if len(ids) >= 2: return "bash:extract-subset"
            if len(ids) == 1 and not walk: return "bash:extract-one-matter"
            if walk: return "bash:scan-corpus-namefiltered" if NAMEFILTER.search(cmd) else "bash:scan-corpus-fulltext"
            return "bash:extract-other"
        if walk and READS_CONTENT.search(cmd): return "bash:scan-corpus-rawtext"
        if walk or re.search(r"\bls\b|printf '%s", cmd): return "bash:list"
        return "bash:other"
    return n
DISCOVERY = {"glob:name-search": "file-name search (glob)", "grep:raw-corpus": "grep tool over raw corpus",
             "bash:scan-corpus-fulltext": "full-text scan of whole corpus (bash)", "bash:scan-corpus-namefiltered": "text scan of name-selected files (bash)",
             "bash:scan-corpus-rawtext": "raw-text scan (.eml/.txt) in bash", "bash:extract-subset": "text scan of hand-listed matters",
             "glob:enumerate": "generic listing (glob)", "bash:list": "listing (ls/printf/rglob)", "glob:matter-scoped": "matter/client folder listing",
             "grep:own-text": "grep over own extracted text", "read:own-file": "read own extracted text",
             "bash:extract-one-matter": "extract one matter's docs", "read:corpus-file": "read a corpus file"}
