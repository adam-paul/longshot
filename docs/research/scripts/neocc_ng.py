#!/usr/bin/env python3
"""Count NEOCC non-grav flags, cross-match with NHATS, fetch per-object .ke1 for flagged NHATS objects (+ extras).

Usage: neocc_ng.py neo_kc.cat nhats.json outdir [extra designations...]
"""
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

cat, nhats_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4:]
os.makedirs(out, exist_ok=True)

flags = {}
started = False
for line in open(cat):
    if not started:
        if line.startswith("END_OF_HEADER"):
            started = True
        continue
    if line.startswith("!") or not line.strip():
        continue
    name = line[:16].strip()
    parts = line[16:].split()
    try:
        flags[name] = (int(parts[-1]), float(parts[7]))
    except (ValueError, IndexError):
        pass
n1 = sum(1 for v in flags.values() if v[0] != 0)
print("NEOCC catalogue objects:", len(flags), " with non-grav flag != 0:", n1)
from collections import Counter
print("flag values:", Counter(v[0] for v in flags.values()))

nh = json.load(open(nhats_path))


def neocc_name(des):
    # NHATS des: '2010 PS66' or '429389' ; NEOCC: '2010PS66' or '429389'
    return des.replace(" ", "")


nh_map = {neocc_name(d["des"]): d for d in nh["data"]}
hit = [k for k in nh_map if k in flags and flags[k][0] != 0]
miss = [k for k in nh_map if k not in flags]
print("NHATS objects:", len(nh_map), " found in NEOCC cat:", len(nh_map) - len(miss), " with NEOCC non-grav flag:", len(hit))

targets = sorted(set(hit) | {neocc_name(e) for e in extra})
res = []
for i, k in enumerate(targets):
    fn = os.path.join(out, k + ".ke1")
    if not (os.path.exists(fn) and os.path.getsize(fn) > 200):
        url = "https://neo.ssa.esa.int/PSDB-portlet/download?file=" + urllib.parse.quote(k + ".ke1")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "python-urllib research client"})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read()
            open(fn, "wb").write(raw)
        except Exception as e:  # noqa: BLE001
            print("ERR", k, e)
            continue
        time.sleep(0.3)
    txt = open(fn, errors="replace").read()
    lsp = re.search(r"^\s*LSP\s+(.*)$", txt, re.M)
    ngr = re.search(r"^\s*NGR\s+(\S+)\s+(\S+)", txt, re.M)
    covs = [float(x) for l in re.findall(r"^\s*COV\s+(.*)$", txt, re.M) for x in l.split()]
    snr = re.search(r"SNR A2\s+(\S+)", txt)
    dadt = re.search(r"da/dt \[1E-4 au/My\]\s+(\S+)\s+\+/-\s+(\S+)", txt)
    rec = {"name": k, "lsp": lsp.group(1).split() if lsp else None}
    if ngr:
        rec["amr"] = float(ngr.group(1)); rec["a2"] = float(ngr.group(2)) * 1e-10
    if lsp:
        l = rec["lsp"]
        dim = int(l[2]) if len(l) > 2 else 6
        solve = [int(x) for x in l[3:]]
        rec["dim"] = dim; rec["solve"] = solve
        if len(covs) == dim * (dim + 1) // 2 and dim > 6:
            # upper triangle row-wise
            idx = {}
            p = 0
            for a in range(dim):
                for b in range(a, dim):
                    idx[(a, b)] = covs[p]; p += 1
            sig = [math.sqrt(abs(idx[(a, a)])) for a in range(6, dim)]
            for sp, sg in zip(solve, sig):
                if sp == 1:
                    rec["amr_sig"] = sg
                elif sp == 2:
                    rec["a2_sig"] = sg * 1e-10
            if dim == 8:
                rec["corr"] = idx[(6, 7)] / (sig[0] * sig[1])
    if snr:
        rec["snr_a2"] = float(snr.group(1))
    if dadt:
        rec["dadt"] = float(dadt.group(1)); rec["dadt_sig"] = float(dadt.group(2))
    d = nh_map.get(k)
    if d:
        rec["nhats_dv"] = float(d["min_dv"]["dv"]); rec["H"] = d["h"]; rec["size"] = f"{d['min_size']}-{d['max_size']}"
    res.append(rec)

json.dump(res, open(os.path.join(out, "neocc_ng_summary.json"), "w"), indent=1)
print("\nfetched:", len(res))
print("solve-for patterns:", Counter(tuple(r.get("solve") or []) for r in res))
both = [r for r in res if r.get("solve") and 1 in r["solve"]]
print("\n--- objects with AMR (SRP) solved for in NEOCC ---")
for r in sorted(both, key=lambda r: r.get("nhats_dv", 99)):
    amr = r.get("amr"); s = r.get("amr_sig")
    a2 = r.get("a2"); s2 = r.get("a2_sig")
    print(f" {r['name']:12s} dv={r.get('nhats_dv')} H={r.get('H')} size={r.get('size')} AMR={amr:.4g}+-{(s if s else float('nan')):.2g} m2/t (snr {abs(amr)/s if s else float('nan'):.1f})"
          f"  A2={a2 if a2 is not None else float('nan'):.3g}+-{(s2 if s2 else float('nan')):.2g} corr={r.get('corr')}")
print("\n--- NHATS objects with NEOCC NG model, sorted by dv (first 60) ---")
for r in sorted([r for r in res if 'nhats_dv' in r], key=lambda r: r["nhats_dv"])[:60]:
    print(f" {r['name']:12s} dv={r['nhats_dv']:.3f} H={r['H']} size={r['size']} solve={r.get('solve')} AMR={r.get('amr')} +-{r.get('amr_sig')} A2={r.get('a2')} +-{r.get('a2_sig')} snrA2={r.get('snr_a2')} dadt={r.get('dadt')}+-{r.get('dadt_sig')}")
