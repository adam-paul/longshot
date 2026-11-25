#!/usr/bin/env python3
"""fm_local_lookup.py NHATS_JSON SBDB_NEO_JSON DES [DES ...]
Prints the NHATS and SBDB snapshot rows for the named objects (local files only, no network)."""
import json, sys
nh = json.load(open(sys.argv[1])); sb = json.load(open(sys.argv[2])); want = sys.argv[3:]
nrows = nh["data"] if isinstance(nh, dict) and "data" in nh else nh
print("NHATS count:", len(nrows))
if isinstance(sb, dict) and "fields" in sb:
    F = sb["fields"]; srows = [dict(zip(F, r)) for r in sb["data"]]
else:
    srows = sb if isinstance(sb, list) else sb.get("data", [])
print("SBDB NEO count:", len(srows))
for w in want:
    print("==", w)
    for r in nrows:
        if r.get("des") == w:
            print("  NHATS:", {k: r.get(k) for k in ("des","h","min_dv","min_dur","min_size","max_size","occ","obs_start","obs_end","obs_mag","n_via_traj")})
    for r in srows:
        if r.get("pdes") == w:
            print("  SBDB :", {k: r.get(k) for k in ("full_name","H","diameter","albedo","rot_per","spec_B","spec_T","a","e","i","condition_code","data_arc","n_obs_used","first_obs","last_obs","moid","class")})
