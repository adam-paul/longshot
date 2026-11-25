#!/usr/bin/env python3
"""fm_arxiv_ids.py OUTDIR ID [ID ...]
One arXiv API request (id_list) for all ids; saves raw Atom, prints id, version, dates, title, authors, journal ref, comment, abstract.
No identifying details in the request."""
import sys, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
outdir, ids = sys.argv[1], sys.argv[2:]
url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": len(ids)})
req = urllib.request.Request(url, headers={"User-Agent": "research-client/1.0"})
data = urllib.request.urlopen(req, timeout=90).read()
open(f"{outdir}/idlist.xml", "wb").write(data)
ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
root = ET.fromstring(data)
for e in root.findall("a:entry", ns):
    g = lambda tag, n="a": (e.find(f"{n}:{tag}", ns).text if e.find(f"{n}:{tag}", ns) is not None else None)
    print("=" * 100)
    print("id       :", g("id"))
    print("published:", g("published"), " updated:", g("updated"))
    print("title    :", " ".join((g("title") or "").split()))
    au = [x.find("a:name", ns).text for x in e.findall("a:author", ns)]
    print("authors  :", len(au), "|", "; ".join(au[:45]))
    print("journal  :", g("journal_ref", "x"), "| doi:", g("doi", "x"))
    print("comment  :", " ".join((g("comment", "x") or "").split()))
    print("category :", [c.get("term") for c in e.findall("a:category", ns)])
    print("abstract :", " ".join((g("summary") or "").split()))
