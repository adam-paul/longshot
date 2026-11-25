#!/usr/bin/env python3
"""nr_openalex.py OUTDIR TAG < queries
Each stdin line: MODE<TAB>N<TAB>query[<TAB>extra_filter]
MODE = s (search= title/abstract/fulltext relevance) | f (filter fulltext.search:) | t (filter title_and_abstract.search:)
Sequential, 1.5 s apart, generic User-Agent, no identifying details. Saves raw JSON; prints year | title | venue | doi."""
import sys, json, time, urllib.request, urllib.parse
outdir, tag = sys.argv[1], sys.argv[2]
for i, line in enumerate(sys.stdin):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"): continue
    parts = line.split("\t")
    mode, n, q = parts[0], int(parts[1]), parts[2]
    extra = parts[3] if len(parts) > 3 else ""
    base = "https://api.openalex.org/works?"
    flt = ["from_publication_date:2010-01-01"]
    if extra: flt.append(extra)
    params = {"per-page": n, "select": "id,doi,title,publication_year,primary_location,cited_by_count"}
    if mode == "s":
        params["search"] = q
    elif mode == "f":
        flt.append("fulltext.search:" + q)
    elif mode == "t":
        flt.append("title_and_abstract.search:" + q)
    params["filter"] = ",".join(flt)
    url = base + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "research-client/1.0"})
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print("ERR", q, e); time.sleep(3); continue
    open(f"{outdir}/{tag}_{i}.json", "wb").write(data)
    try:
        j = json.loads(data)
    except Exception as e:
        print("PARSE ERR", e); continue
    print(f"=== [{mode}] {q} {extra} -> total {j.get('meta', {}).get('count')}")
    for w in j.get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        print(f"  {w.get('publication_year')} | {(w.get('title') or '')[:150]} | {src[:40]} | {w.get('doi') or w.get('id')}")
    time.sleep(1.5)
