#!/usr/bin/env python3
"""Print density, mass, diameter, albedo, thermal inertia, spin and taxonomy blocks of saved SsODNet ssoCards.
Usage: python3 -I nc_ssocard_show.py card.json ..."""
import json, sys

def g(d, *ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d

def val(b):
    if not isinstance(b, dict):
        return b
    v = b.get("value")
    e = b.get("error")
    if isinstance(e, dict):
        e = "+%s/-%s" % (e.get("max"), e.get("min"))
    return "%s (%s)" % (v, e)

def meth(b):
    out = []
    for m in (b.get("method") or []) if isinstance(b, dict) else []:
        out.append("%s[%s %s]" % (m.get("name"), m.get("shortbib"), m.get("year")))
    for m in (b.get("bibref") or []) if isinstance(b, dict) else []:
        out.append("%s %s" % (m.get("shortbib"), m.get("year")))
    return "; ".join(dict.fromkeys(out))[:260]

for f in sys.argv[1:]:
    d = json.load(open(f))
    name = d.get("name"); num = d.get("number")
    p = g(d, "parameters", "physical") or {}
    print("=" * 100)
    print(num, name, "| class", d.get("class"))
    for k in ("density", "mass", "diameter", "albedo", "thermal_inertia"):
        b = p.get(k)
        if b:
            print("  %-16s %s %s | %s" % (k, val(b), (b.get("unit") or ""), meth(b)))
    sp = p.get("spin")
    if sp:
        items = sp if isinstance(sp, list) else list(sp.values())
        for s in items[:3]:
            if isinstance(s, dict):
                print("  spin: P=%s h  pole lon/lat=%s/%s obliquity=%s | %s" % (g(s, "period", "value"), g(s, "long", "value"), g(s, "lat", "value"), g(s, "obliquity", "value"), g(s, "technique") or g(s, "method")))
    tx = p.get("taxonomy")
    if tx:
        print("  taxonomy:", g(tx, "class", "value"), "complex", g(tx, "complex", "value"), "|", meth(tx))
    y = g(d, "parameters", "dynamical", "yarkovsky")
    if y:
        print("  yarkovsky:", {k: (val(v) if isinstance(v, dict) and "value" in v else None) for k, v in y.items() if k in ("A2", "dadt", "S", "snr")}, "|", meth(y))
