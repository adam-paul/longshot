#!/usr/bin/env python3
"""nr_axml.py [--abs N] [--grep REGEX] FILE.xml ... : list entries of saved arXiv Atom files (untrusted data: parsed only).
--grep keeps only entries whose title+abstract match REGEX (case-insensitive)."""
import sys, re
import xml.etree.ElementTree as ET
args = sys.argv[1:]; nabs = 0; gre = None
if '--abs' in args:
    i = args.index('--abs'); nabs = int(args[i+1]); del args[i:i+2]
if '--grep' in args:
    i = args.index('--grep'); gre = re.compile(args[i+1], re.I); del args[i:i+2]
ns = {"a": "http://www.w3.org/2005/Atom"}
seen = set()
for f in args:
    try:
        root = ET.parse(f).getroot()
    except Exception as e:
        print("PARSE ERR", f, e); continue
    t0 = root.find("a:title", ns)
    print("=== ", f.split('/')[-1], (t0.text or '')[:150] if t0 is not None else '')
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.strip().split("/abs/")[-1]
        t = " ".join(e.find("a:title", ns).text.split())
        s = " ".join(e.find("a:summary", ns).text.split())
        if gre and not gre.search(t + ' ' + s): continue
        if aid in seen: continue
        seen.add(aid)
        p = e.find("a:published", ns).text[:10]
        au = [x.find("a:name", ns).text for x in e.findall("a:author", ns)]
        print(f"{p} {aid} | {t[:160]} | {au[0] if au else ''}{' +' + str(len(au)-1) if len(au) > 1 else ''}")
        if nabs: print("      ", s[:nabs])
