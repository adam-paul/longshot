#!/usr/bin/env python3
"""nr_arxiv.py OUTDIR TAG [abs] < queries
Each stdin line: N<TAB>query  (arXiv API search_query syntax).
Saves raw Atom to OUTDIR/TAG_<i>.xml and prints id | date | title | first author.
Sequential, 3.2 s between requests. No identifying details in the request."""
import sys, urllib.request, urllib.parse, time
import xml.etree.ElementTree as ET

outdir, tag = sys.argv[1], sys.argv[2]
show_abs = len(sys.argv) > 3 and sys.argv[3] == "abs"
ns = {"a": "http://www.w3.org/2005/Atom"}
for i, line in enumerate(sys.stdin):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    n, q = line.split("\t", 1)
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "start": 0, "max_results": int(n),
         "sortBy": "submittedDate", "sortOrder": "descending"})
    req = urllib.request.Request(url, headers={"User-Agent": "research-client/1.0"})
    data = None
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=90).read()
            break
        except Exception as e:  # noqa
            print("ERR", q, e, file=sys.stderr)
            time.sleep(8)
    if data is None:
        continue
    open(f"{outdir}/{tag}_{i}.xml", "wb").write(data)
    print("=== ", q)
    try:
        root = ET.fromstring(data)
    except Exception as e:
        print("PARSE ERR", e)
        continue
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.strip().split("/abs/")[-1]
        t = " ".join(e.find("a:title", ns).text.split())
        p = e.find("a:published", ns).text[:10]
        au = [x.find("a:name", ns).text for x in e.findall("a:author", ns)]
        print(f"{p} {aid} | {t[:170]} | {au[0] if au else ''}{' et al.' if len(au) > 1 else ''}")
        if show_abs:
            print("     ", " ".join(e.find("a:summary", ns).text.split())[:1500])
    time.sleep(3.2)
