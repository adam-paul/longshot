#!/usr/bin/env python3
"""Fetch SsODNet ssoCards for all NEO asteroids with a fitted NG parameter in SBDB.

Usage: fetch_ssocards.py sbdb_ng_all.json outdir
Writes one JSON per object plus summary.tsv. Polite: one request at a time, 0.25 s pause.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sb = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
F = sb["fields"]
rows = [dict(zip(F, r)) for r in sb["data"]]
rows = [r for r in rows if r["neo"] == "Y" and r["kind"].startswith("a")]
print("objects:", len(rows), flush=True)
base = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard.php?q="
summ = open(os.path.join(out, "summary.tsv"), "w")
summ.write("pdes\tstatus\tname\tdiam_km\tdiam_method\talbedo\tdensity\tdensity_method\ttax_class\ttax_complex\tTI\tn_spins\tspin_lat\tspin_methods\n")
for i, r in enumerate(rows):
    pdes = r["pdes"]
    fn = os.path.join(out, pdes.replace(" ", "_") + ".json")
    data = None
    if os.path.exists(fn) and os.path.getsize(fn) > 100:
        try:
            data = json.load(open(fn))
        except Exception:  # noqa: BLE001
            data = None
    if data is None:
        url = base + urllib.parse.quote(pdes)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "python-urllib research client"})
            with urllib.request.urlopen(req, timeout=40) as resp:
                raw = resp.read()
            data = json.loads(raw)
            with open(fn, "wb") as fh:
                fh.write(raw)
        except Exception as e:  # noqa: BLE001
            summ.write(f"{pdes}\tERR {type(e).__name__}\n")
            summ.flush()
            time.sleep(0.5)
            continue
        time.sleep(0.25)
    try:
        p = (data.get("parameters") or {}).get("physical") or {}

        def val(k):
            x = p.get(k) or {}
            return x.get("value") if isinstance(x, dict) else None

        def meth(k):
            x = p.get(k) or {}
            m = x.get("method") if isinstance(x, dict) else None
            if isinstance(m, list):
                return ",".join(sorted({str(mm.get("label")) for mm in m if isinstance(mm, dict)}))
            return ""

        tax = p.get("taxonomy") or {}
        spins = p.get("spins") or []
        if isinstance(spins, dict):
            spins = [spins]
        lats = []
        sm = set()
        for s in spins:
            if not isinstance(s, dict):
                continue
            lat = s.get("lat")
            if isinstance(lat, dict):
                lat = lat.get("value")
            if lat is not None:
                lats.append(lat)
            m = s.get("method")
            if isinstance(m, list):
                for mm in m:
                    if isinstance(mm, dict):
                        sm.add(str(mm.get("label")))
            tech = s.get("technique")
            if tech:
                sm.add(str(tech))
        summ.write("\t".join(str(x) for x in [
            pdes, "OK", data.get("name"), val("diameter"), meth("diameter"), val("albedo"), val("density"), meth("density"),
            tax.get("class") if isinstance(tax, dict) else None, tax.get("complex") if isinstance(tax, dict) else None,
            val("thermal_inertia"), len(lats), ";".join(str(x) for x in lats[:6]), ",".join(sorted(sm))]) + "\n")
    except Exception as e:  # noqa: BLE001
        summ.write(f"{pdes}\tPARSE_ERR {type(e).__name__} {e}\n")
    summ.flush()
    if i % 50 == 0:
        print(i, pdes, flush=True)
summ.close()
print("done", flush=True)
