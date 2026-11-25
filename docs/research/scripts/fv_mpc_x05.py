#!/usr/bin/env python3
"""fv_mpc_x05.py FILE: count observations per station and per band for X05 in an MPC get-obs ADES_DF response."""
import json, sys, collections
d = json.load(open(sys.argv[1]))
rows = d[0]["ADES_DF"] if isinstance(d, list) else d["ADES_DF"]
stn = collections.Counter(r.get("stn") for r in rows)
x = [r for r in rows if r.get("stn") == "X05"]
print("total obs", len(rows), "stations", dict(stn))
print("X05 obs", len(x), "bands", dict(collections.Counter(r.get("band") for r in x)))
if x:
    ts = sorted(r.get("obstime") or r.get("obsTime") for r in x)
    print("X05 first/last", ts[0], ts[-1])
    print("sample keys with values:", {k: v for k, v in x[0].items() if v not in (None, "")})
