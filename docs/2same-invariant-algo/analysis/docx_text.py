"""Plain text of a .docx, with tracked changes visible: deletions as [-...-], insertions as {+...+}. One paragraph per line.

    python3 docx_text.py FILE.docx [--grep WORD] [--context N]
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraphs(path: str) -> list[str]:
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    out = []
    for p in root.iter(W + "p"):
        parts = []

        def walk(el, mode):
            for ch in el:
                tag = ch.tag
                if tag == W + "del":
                    walk(ch, "del")
                elif tag == W + "ins":
                    walk(ch, "ins")
                elif tag in (W + "t", W + "delText"):
                    txt = ch.text or ""
                    parts.append(f"[-{txt}-]" if mode == "del" else f"{{+{txt}+}}" if mode == "ins" else txt)
                elif tag == W + "tab":
                    parts.append("\t")
                else:
                    walk(ch, mode)
        walk(p, None)
        text = "".join(parts)
        text = re.sub(r"-\]\[-", "", re.sub(r"\+\}\{\+", "", text))  # join adjacent runs of the same kind
        if text.strip():
            out.append(text)
    return out


if __name__ == "__main__":
    paras = paragraphs(sys.argv[1])
    if "--grep" in sys.argv:
        word = sys.argv[sys.argv.index("--grep") + 1]
        for i, p in enumerate(paras):
            if re.search(word, p, re.I):
                print(f"[{i}] {p}")
    else:
        print("\n".join(paras))
