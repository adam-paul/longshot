#!/usr/bin/env python3
"""Look up named objects in the SBDB NG list and print rows; report missing ones."""
import json
import sys

sb = json.load(open(sys.argv[1]))
F = sb["fields"]
rows = [dict(zip(F, r)) for r in sb["data"]]
by = {r["pdes"]: r for r in rows}
want = sys.argv[2:]
for w in want:
    r = by.get(w)
    if r is None:
        print(f"{w:12s} NOT in SBDB NG list (no A1/A2/A3 fitted)")
    else:
        def f(p):
            if r[p] is None:
                return "-"
            v = float(r[p]); s = float(r[p + "_sigma"])
            return f"{v:.3g}+-{s:.2g} ({abs(v)/s:.1f}s)"
        print(f"{w:12s} {r['full_name'].strip():34s} kind={r['kind']} H={r['H']} D={r['diameter']} pV={r['albedo']} A1={f('A1')} A2={f('A2')} A3={f('A3')} arc={r['data_arc']} nobs={r['n_obs_used']} spec={r['spec_B']}/{r['spec_T']} P={r['rot_per']}")
