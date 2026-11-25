#!/usr/bin/env python3
"""Print compact summary of individual SBDB API records."""
import json
import sys

for path in sys.argv[1:]:
    try:
        d = json.load(open(path))
    except Exception as e:  # noqa: BLE001
        print(path, "ERR", e)
        continue
    obj = d.get("object", {})
    orb = d.get("orbit", {})
    print("==", obj.get("fullname"), "| kind", obj.get("kind"), "| neo", obj.get("neo"), "| class", (obj.get("orbit_class") or {}).get("code"))
    print("   orbit_id", orb.get("orbit_id"), "soln_date", orb.get("soln_date"), "first_obs", orb.get("first_obs"), "last_obs", orb.get("last_obs"),
          "arc", orb.get("data_arc"), "n_obs", orb.get("n_obs_used"), "n_del", orb.get("n_del_obs_used"), "n_dop", orb.get("n_dop_obs_used"),
          "cond", orb.get("condition_code"), "rms", orb.get("rms"))
    print("   not_valid_before/after:", orb.get("not_valid_before"), orb.get("not_valid_after"), "| comment:", orb.get("comment"))
    mp = orb.get("model_pars")
    print("   model_pars:", [(m.get("name"), m.get("value"), m.get("sigma")) for m in (mp or [])])
    print("   elements:", {e["name"]: e["value"] for e in orb.get("elements", []) if e["name"] in ("a", "e", "i", "q")})
    pp = d.get("phys_par") or []
    print("   phys:", [(p.get("name"), p.get("value"), p.get("sigma")) for p in pp])
    if "message" in d:
        print("   message:", d["message"])
