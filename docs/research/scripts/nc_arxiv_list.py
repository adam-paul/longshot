#!/usr/bin/env python3
"""Print id | date | title | first authors from saved arXiv API Atom files. python3 -I nc_arxiv_list.py file.xml ..."""
import re, sys
for f in sys.argv[1:]:
    t = open(f, errors="replace").read()
    print("==", f.split("/")[-1], "total:", (re.search(r"totalResults[^>]*>(\d+)<", t) or [None, "?"])[1])
    for e in re.findall(r"<entry>(.*?)</entry>", t, flags=re.S):
        i = re.search(r"<id>(.*?)</id>", e).group(1).split("/")[-1]
        ti = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, flags=re.S).group(1))
        p = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
        au = re.findall(r"<name>(.*?)</name>", e)
        jr = re.search(r"<arxiv:journal_ref[^>]*>(.*?)</arxiv:journal_ref>", e, flags=re.S)
        print(" ", p, i, "|", ti[:140], "|", ", ".join(au[:3]), "|", (jr.group(1).strip()[:60] if jr else ""))
