#!/usr/bin/env python3
"""fv_ojap.py FILE: pull the embedded page text out of the Scholastica journal shell and print passages on fees, arXiv and GenAI."""
import sys, re, html, codecs
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
# decode \uXXXX and \n escapes present in the embedded JSON
txt = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), raw)
txt = txt.replace("\\n", "\n").replace('\\"', '"')
txt = re.sub(r"<[^>]+>", "", txt)
txt = html.unescape(txt)
for kw in ["free of charge", "not free", "inexpensive", "Use of Generative AI", "must be on the arXiv", "astro-ph section", "endors"]:
    for m in list(re.finditer(re.escape(kw), txt))[:2]:
        a = max(0, m.start() - 300); b = min(len(txt), m.end() + 900)
        print("[%s]" % kw, re.sub(r"\s+", " ", txt[a:b])); print("--")
