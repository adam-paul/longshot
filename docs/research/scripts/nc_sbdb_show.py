#!/usr/bin/env python3
"""Print orbit model parameters and physical parameters from saved JPL sbdb.api responses.
Usage: nc_sbdb_show.py file.json [file.json ...]   (run with python3 -I)
"""
import json
import sys

for f in sys.argv[1:]:
    try:
        d = json.load(open(f))
    except Exception as e:  # noqa: BLE001
        print(f, "ERR", e)
        continue
    o = d.get("orbit", {})
    ob = d.get("object", {})
    el = {e["name"]: e for e in o.get("elements", [])}
    print("=" * 100)
    print(ob.get("fullname"), "| kind", ob.get("kind"), "| class", (ob.get("orbit_class") or {}).get("code"),
          "| orbit_id", o.get("orbit_id"), "| soln_date", o.get("soln_date"), "| producer", o.get("producer"))
    print("   arc", o.get("data_arc"), "d,", o.get("first_obs"), "to", o.get("last_obs"), "| n_obs", o.get("n_obs_used"),
          "| delay", o.get("n_del_obs_used"), "doppler", o.get("n_dop_obs_used"), "| cond", o.get("condition_code"),
          "| rms", o.get("rms"), "| eph", o.get("pe_used"), o.get("sb_used"), "| not_valid_before/after", o.get("not_valid_before"), o.get("not_valid_after"))
    print("   a=%s e=%s i=%s q=%s per=%s d" % tuple((el.get(k) or {}).get("value") for k in ("a", "e", "i", "q", "per")))
    mp = o.get("model_pars") or []
    if not mp:
        print("   model_pars: NONE (gravity-only)")
    for m in mp:
        v, s = m.get("value"), m.get("sigma")
        try:
            sn = "  S/N=%.2f" % (abs(float(v)) / float(s))
        except (TypeError, ValueError, ZeroDivisionError):
            sn = ""
        print("   model:", m.get("name"), "=", v, "+-", s, m.get("units") or "", sn, "|", m.get("title"))
    for p in d.get("phys_par") or []:
        print("   phys:", p.get("name"), "=", p.get("value"), "+-", p.get("sigma"), p.get("units") or "", "| ref:", (p.get("ref") or "")[:110], "|", (p.get("notes") or "")[:100])
    disc = d.get("discovery") or {}
    if disc:
        print("   discovery:", disc.get("date"), disc.get("site"), disc.get("who"), "|", (disc.get("discovery") or "")[:300])
