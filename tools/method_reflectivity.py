"""Reflectivity (geometric albedo) distributions for method/v0_1/priors.toml: [reflectivity], [h_uncertainty].

Inputs, all on disk:
  config.SPITZER_CSV      Spitzer sizes and reflectivities (Trilling et al. 2010, 2016); a < 2 au kept
  config.SSODNET_CARDS    literature cards: parameters.physical.albedo (method not "Computed") and .taxonomy
  data/research/out-prior-null/labels.csv   one class per near-Earth asteroid, built on 21 November 2026
                          by data/research/scripts/pn_build_labels.py from published tables
  config.SBDB_JSON, config.NHATS_JSON       H, H_sigma, list membership

Usage: uv run python -I tools/method_reflectivity.py
"""
import csv
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from method_lib import (CLASS4, H_BANDS, Report, Sbdb, band_of, class4, config, fl, iter_cards,  # noqa: E402
                        load_nhats, load_spitzer, quantile)

# The probabilities at which every quantile table is given: 2.5%, 5%, 10% ... 90%, 95%, 97.5%.
P_GRID = (0.025,) + tuple(round(0.05 * i, 2) for i in range(1, 20)) + (0.975,)
# Reflectivity bins that tie reflectivity to class. 0.10 and 0.30 are Tholen's P/M/E limits
# (docs/research/value-inputs.md section 1.4); 0.20 and 0.45 split the two crowded bins.
PV_EDGES = (0.10, 0.20, 0.30, 0.45)
D_KM_AT_H0 = 1329.0  # D[km] = 1329 * 10^(-H/5) / sqrt(pv)
LABELS_CSV = os.path.join(str(config.DATA), "research", "out-prior-null", "labels.csv")


def pv_bin(pv):
    for i, e in enumerate(PV_EDGES):
        if pv < e:
            return i
    return len(PV_EDGES)


def spitzer_objects(max_a=2.0):
    """One reflectivity per object: the geometric mean of its Spitzer rows. Returns (objects, counts)."""
    rows = load_spitzer()
    by = {}
    kept = 0
    for r in rows:
        a, pv, d, h = fl(r["a"]), fl(r["pv"]), fl(r["diam"]), fl(r["absmag"])
        if a is None or a >= max_a or not pv or pv <= 0 or not d or d <= 0 or h is None:
            continue
        kept += 1
        o = by.setdefault(r["desig"], {"desig": r["desig"], "number": r["number"], "name": r["name"],
                                       "pv": [], "h": [], "d": [], "snr": []})
        o["pv"].append(pv)
        o["h"].append(h)
        o["d"].append(d)
        o["snr"].append(fl(r["ch2snr"]) or 0.0)
    objs = []
    for k in sorted(by):
        o = by[k]
        objs.append({"desig": o["desig"], "number": o["number"], "name": o["name"],
                     "pv": math.exp(statistics.fmean(math.log(x) for x in o["pv"])),
                     "h": statistics.fmean(o["h"]),
                     "d_km": math.exp(statistics.fmean(math.log(x) for x in o["d"])),
                     "snr": max(o["snr"]), "n_rows": len(o["pv"])})
    return objs, {"rows": len(rows), "rows_kept": kept, "objects": len(objs)}


def quantile_table(values):
    return [quantile(values, p) for p in P_GRID]


def labels_by_pdes():
    out = {}
    with open(LABELS_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["tax4"]:
                out[r["pdes"]] = ({"S": "S", "C": "C", "X": "X", "O": "other"}[r["tax4"]],
                                  r["tax4_src"], r["tax4_spec"] == "1")
    return out


def card_measured_albedo_by_class():
    """Cards whose albedo was measured (method not "Computed") and that carry a class."""
    out = []
    n_cards = n_alb = n_computed = 0
    for fn, c in iter_cards():
        n_cards += 1
        ph = c["parameters"].get("physical") or {}
        al = ph.get("albedo") or {}
        tx = ph.get("taxonomy") or {}
        if al.get("value") is None:
            continue
        n_alb += 1
        labels = [m.get("label", "") for m in (al.get("method") or [])]
        if not labels or any(x == "Computed" for x in labels):
            n_computed += 1
            continue
        cls = class4(tx.get("class") or tx.get("complex"))
        out.append((c.get("name") or fn, fl(al["value"]), "+".join(labels), tx.get("class"), cls))
    return out, {"cards": n_cards, "with_albedo": n_alb, "computed_or_unlabelled": n_computed}


def compute():
    """The constants priors.toml takes from this script."""
    sb = Sbdb()
    nh = load_nhats()
    objs, counts = spitzer_objects()
    pvs = [o["pv"] for o in objs]
    lab = labels_by_pdes()
    by_class = {c: [] for c in CLASS4}
    for o in objs:
        pdes = sb.resolve(o["number"], o["desig"], o["name"])
        if pdes in lab and lab[pdes][2]:
            by_class[lab[pdes][0]].append(o["pv"])
    members = [d for d in sorted(nh) if d in sb.rows]
    hs = [x for x in (fl(sb.get(d, "H_sigma")) for d in members) if x is not None]
    return {
        "rows": counts["rows"], "rows_kept": counts["rows_kept"], "objects": counts["objects"],
        "p": list(P_GRID), "pv": quantile_table(pvs),
        "by_class": {c: {"n": len(v), "pv": quantile_table(v)} for c, v in by_class.items()},
        "n_h25": sum(1 for o in objs if o["h"] >= 25), "n_h24": sum(1 for o in objs if o["h"] >= 24),
        "h_max": max(o["h"] for o in objs), "h_median": statistics.median(o["h"] for o in objs),
        "n_above_1": sum(1 for x in pvs if x > 1),
        "h_sigma_median": statistics.median(hs), "h_sigma_n": len(hs), "n_members": len(nh),
        "h_sigma_p10": quantile(hs, .10), "h_sigma_p90": quantile(hs, .90),
        "n_no_h": sum(1 for d in members if sb.h(d) is None),
        "card_measured": {c: sum(1 for m in card_measured_albedo_by_class()[0] if m[4] == c) for c in CLASS4},
    }


def fmt(x, nd=3):
    return f"{x:.{nd}f}"


def main(write=True, echo=True):
    rep = Report("reflectivity")
    sb = Sbdb()
    nh = load_nhats()
    objs, counts = spitzer_objects()
    pvs = [o["pv"] for o in objs]

    rep("REFLECTIVITY FROM THE SPITZER TABLE")
    rep(f"input: {os.path.relpath(str(config.SPITZER_CSV), str(config.ROOT))}")
    rep(f"rows {counts['rows']}; rows with a < 2 au and a size and reflectivity {counts['rows_kept']}; "
        f"distinct objects {counts['objects']} (repeat rows combined by geometric mean)")
    rep(f"median {fmt(statistics.median(pvs))}; mean of log10 {fmt(statistics.fmean(math.log10(x) for x in pvs))}; "
        f"sd of log10 {fmt(statistics.pstdev([math.log10(x) for x in pvs]))}")
    rep(f"objects with fitted reflectivity above 1.0: {sum(1 for x in pvs if x > 1)} "
        f"({100 * sum(1 for x in pvs if x > 1) / len(pvs):.1f}%); below 0.10: {sum(1 for x in pvs if x < 0.10)} "
        f"({100 * sum(1 for x in pvs if x < 0.10) / len(pvs):.1f}%)")
    rep()
    rep("[reflectivity] quantiles, all objects (a < 2 au)")
    q_all = quantile_table(pvs)
    rep.table(["p", "pv", "D/D(pv=0.14)"], [[f"{p:.3f}", fmt(q, 4), fmt(math.sqrt(0.14 / q), 3)] for p, q in zip(P_GRID, q_all)])
    rep()

    rep("size against the size at reflectivity 0.14, by row (the plan's check) and by object")
    rows = load_spitzer()
    ratio_rows = []
    for r in rows:
        a, d, h = fl(r["a"]), fl(r["diam"]), fl(r["absmag"])
        if a is None or a >= 2 or not d or h is None:
            continue
        ratio_rows.append(d / (D_KM_AT_H0 / math.sqrt(0.14) * 10 ** (-0.2 * h)))
    ratio_obj = [o["d_km"] / (D_KM_AT_H0 / math.sqrt(0.14) * 10 ** (-0.2 * o["h"])) for o in objs]
    for label, v in (("rows", ratio_rows), ("objects", ratio_obj)):
        m = statistics.median(v)
        inside = sum(1 for x in v if 0.5 * m <= x <= 2 * m) / len(v)
        rep(f"  {label}: N {len(v)}; median ratio {fmt(m)}; 5th-95th {fmt(quantile(v, .05), 2)}-{fmt(quantile(v, .95), 2)}; "
            f"share within half to double of the median {100 * inside:.0f}%")
    rep()

    rep("by H band (objects): the median holds to H 24; the spread widens at H 22-24, and the 15 objects at H 24-26")
    rep("have a higher median (several are fits at low signal-to-noise; see the list below)")
    trows = []
    for name, lo, hi in H_BANDS:
        v = [o["pv"] for o in objs if lo <= o["h"] < hi]
        if v:
            trows.append([name, len(v), fmt(statistics.median(v)), fmt(quantile(v, .16)), fmt(quantile(v, .84))])
        else:
            trows.append([name, 0, "-", "-", "-"])
    rep.table(["H band", "N", "median pv", "16th", "84th"], trows)
    faint = sorted((o for o in objs if o["h"] >= 24.5), key=lambda o: o["desig"])
    rep(f"objects at H >= 25: {sum(1 for o in objs if o['h'] >= 25)}; at H >= 24: {sum(1 for o in objs if o['h'] >= 24)}; "
        f"brightest H {min(o['h'] for o in objs):.1f}, faintest H {max(o['h'] for o in objs):.1f}, "
        f"median H {statistics.median(o['h'] for o in objs):.1f}")
    rep("objects at H >= 24.5 (values withheld: the table is shown one value at a time on an object's own page):")
    rep.table(["desig", "H >= 25", "fitted pv > 1", "signal-to-noise under 5"],
              [[o["desig"], "yes" if o["h"] >= 25 else "no", "yes" if o["pv"] > 1 else "no", "yes" if o["snr"] < 5 else "no"] for o in faint])
    rep()

    rep("sensitivity: signal-to-noise of 5 or more in the 4.5 micron band")
    v5 = [o["pv"] for o in objs if o["snr"] >= 5]
    rep(f"  N {len(v5)}; median {fmt(statistics.median(v5))}; 2.5% {fmt(quantile(v5, .025))}; 97.5% {fmt(quantile(v5, .975))}"
        f"   (all objects: 2.5% {fmt(q_all[0])}; 97.5% {fmt(q_all[-1])})")
    rep("sensitivity: list members only (reachable asteroids in the Spitzer table)")
    vn = [o["pv"] for o in objs if sb.resolve(o["number"], o["desig"], o["name"]) in nh]
    rep(f"  N {len(vn)}; median {fmt(statistics.median(vn))}; 16th {fmt(quantile(vn, .16))}; 84th {fmt(quantile(vn, .84))}")
    rep()

    # ---- class-conditional
    rep("CLASS-CONDITIONAL REFLECTIVITY")
    rep("(a) literature cards with a measured (not computed) reflectivity and a class")
    meas, cc = card_measured_albedo_by_class()
    rep(f"  cards {cc['cards']}; with a reflectivity {cc['with_albedo']}; of those computed from size and H "
        f"{cc['computed_or_unlabelled']}; measured {len(meas)}")
    rep.table(["  object", "method", "class", "group"], [["  " + str(m[0]), m[2], str(m[3]), str(m[4])] for m in meas])
    by_cls = {c: [m for m in meas if m[4] == c] for c in CLASS4}
    rep("  counts: " + ", ".join(f"{c} {len(by_cls[c])}" for c in CLASS4) + f"; no class {sum(1 for m in meas if m[4] is None)}")
    rep()

    rep("(b) Spitzer reflectivity (a < 2 au) joined to the 21 November class labels")
    rep(f"  labels: {os.path.relpath(LABELS_CSV, str(config.ROOT))}")
    lab = labels_by_pdes()
    joined = []
    for o in objs:
        pdes = sb.resolve(o["number"], o["desig"], o["name"])
        if pdes and pdes in lab:
            joined.append((o, lab[pdes]))
    rep(f"  Spitzer objects with a class: {len(joined)} of {len(objs)}")
    rep("  class source of the joined objects: " + ", ".join(
        f"{s} {n}" for s, n in sorted(((s, sum(1 for _, l in joined if l[1] == s)) for s in {l[1] for _, l in joined}),
                                      key=lambda t: (-t[1], t[0]))))
    rep(f"  from a spectrum: {sum(1 for _, l in joined if l[2])}; from colours or a compilation: {sum(1 for _, l in joined if not l[2])}")
    rep()
    def class_table(sel):
        tabs = {c: [o["pv"] for o, l in sel if l[0] == c] for c in CLASS4}
        rep.table(["class", "N", "median", "5th", "25th", "75th", "95th", "share < 0.10", "median H"],
                  [[c, len(tabs[c]), fmt(statistics.median(tabs[c])), fmt(quantile(tabs[c], .05)), fmt(quantile(tabs[c], .25)),
                    fmt(quantile(tabs[c], .75)), fmt(quantile(tabs[c], .95)),
                    f"{100 * sum(1 for x in tabs[c] if x < 0.10) / len(tabs[c]):.0f}%",
                    f"{statistics.median(o['h'] for o, l in sel if l[0] == c):.1f}"] for c in CLASS4])
        return tabs

    spectra = [(o, l) for o, l in joined if l[2]]
    rep("  class from a spectrum (the table used):")
    tabs = class_table(spectra)
    rep(f"  of these at H >= 22: {sum(1 for o, _ in spectra if o['h'] >= 22)}; at H >= 24: {sum(1 for o, _ in spectra if o['h'] >= 24)}")
    rep("  class from colours or a compilation (not used: these classes disagree with spectra for 33% of shared")
    rep("  objects on four classes, docs/research/verify-prior-null.md section 1):")
    class_table([(o, l) for o, l in joined if not l[2]])
    rep()
    for c in CLASS4:
        rep(f"[reflectivity.by_class.{c}] N {len(tabs[c])}")
        rep("  pv = [" + ", ".join(fmt(q, 4) for q in quantile_table(tabs[c])) + "]")
    rep()

    rep("(c) counts by reflectivity bin and class (class from a spectrum)")
    edges = ["< %.2f" % PV_EDGES[0]] + ["%.2f-%.2f" % (PV_EDGES[i], PV_EDGES[i + 1]) for i in range(len(PV_EDGES) - 1)] + [">= %.2f" % PV_EDGES[-1]]
    cnt = {c: [0] * (len(PV_EDGES) + 1) for c in CLASS4}
    for o, l in spectra:
        cnt[l[0]][pv_bin(o["pv"])] += 1
    rep.table(["class"] + edges + ["all"], [[c] + cnt[c] + [sum(cnt[c])] for c in CLASS4])
    rep("  share of each class falling in each bin, P(bin | class):")
    rep.table(["class"] + edges, [[c] + [fmt(n / sum(cnt[c])) for n in cnt[c]] for c in CLASS4])
    marg = [0] * (len(PV_EDGES) + 1)
    for x in pvs:
        marg[pv_bin(x)] += 1
    rep("  all Spitzer objects (a < 2 au) by the same bins: " + ", ".join(f"{e} {n} ({n / len(pvs):.3f})" for e, n in zip(edges, marg)))
    rep()

    rep("(d) Spitzer reflectivity joined to the class on a literature card (list members only)")
    card_cls = {}
    for fn, c in iter_cards():
        tx = (c["parameters"].get("physical") or {}).get("taxonomy") or {}
        g = class4(tx.get("class") or tx.get("complex"))
        if g:
            pdes = sb.resolve(c.get("number"), c.get("name"), *(c.get("aliases") or []))
            if pdes:
                card_cls[pdes] = g
    j2 = {c: [] for c in CLASS4}
    for o in objs:
        pdes = sb.resolve(o["number"], o["desig"], o["name"])
        if pdes in card_cls:
            j2[card_cls[pdes]].append(o["pv"])
    rep("  " + "; ".join(f"{c}: N {len(j2[c])}" + (f", median {fmt(statistics.median(j2[c]))}" if j2[c] else "") for c in CLASS4))
    rep()

    # ---- H uncertainty
    rep("H UNCERTAINTY (JPL's H_sigma)")
    hs_all = [fl(sb.get(p, "H_sigma")) for p in sb.rows]
    hs_all = [x for x in hs_all if x is not None]
    rep(f"  all near-Earth asteroids: {len(hs_all)} of {len(sb.rows)} have H_sigma; median {fmt(statistics.median(hs_all))}")
    members = [d for d in sorted(nh) if d in sb.rows]
    hs = [fl(sb.get(d, "H_sigma")) for d in members]
    hs = [x for x in hs if x is not None]
    rep(f"  list members: {len(nh)} on the list, {len(members)} matched in JPL's table, {len(hs)} with H_sigma")
    rep(f"  list members with H_sigma: median {fmt(statistics.median(hs))}; 10th {fmt(quantile(hs, .10))}; "
        f"25th {fmt(quantile(hs, .25))}; 75th {fmt(quantile(hs, .75))}; 90th {fmt(quantile(hs, .90))}; max {fmt(max(hs))}")
    rep(f"  list members with no H in JPL's table: {sum(1 for d in members if sb.h(d) is None)}")
    faint_n = sum(1 for d in members if sb.h(d) is not None and sb.h(d) >= 25)
    rep(f"  list members at H >= 25, where the reflectivity table is extrapolation: {faint_n} of {len(members)} ({100 * faint_n / len(members):.0f}%)")
    sig = sorted({fl(r['absmagsig']) for r in rows if fl(r['absmagsig']) is not None})
    rep(f"  H uncertainty the Spitzer fits assumed (absmagsig column), distinct values: {sig}")
    rep()

    # ---- sizes at the list's quoted brightnesses
    rep("SIZE AT A GIVEN H (metres): D = 1.329e6 * 10^(-H/5) / sqrt(pv), no H uncertainty added")
    rep.table(["H", "5%", "25%", "50%", "75%", "95%", "95%/5%"],
              [[f"{h:.1f}"] + [f"{1.329e6 * 10 ** (-h / 5) / math.sqrt(quantile(pvs, 1 - p)):.1f}" for p in (.05, .25, .5, .75, .95)]
               + [f"{math.sqrt(quantile(pvs, .95) / quantile(pvs, .05)):.1f}"]
               for h in (20.0, 22.0, 24.0, 25.0, 26.2, 27.7, 28.0, 30.0)])
    rep()
    sig = statistics.median(hs)
    rep(f"the same with H drawn as normal(H, {sig:.2f}), the default when JPL gives no H_sigma")
    nd = statistics.NormalDist()
    zs = [nd.inv_cdf((j + 0.5) / 41) for j in range(41)]
    us = [(i + 0.5) / 400 for i in range(400)]
    grid_pv = [10 ** _interp_log(P_GRID, q_all, u) for u in us]
    trows = []
    for h in (20.0, 22.0, 24.0, 25.0, 26.2, 27.7, 28.0, 30.0):
        ds = sorted(1.329e6 * 10 ** (-(h + sig * z) / 5) / math.sqrt(pv) for z in zs for pv in grid_pv)
        trows.append([f"{h:.1f}"] + [f"{quantile(ds, p):.1f}" for p in (.05, .25, .5, .75, .95)]
                     + [f"{quantile(ds, .95) / quantile(ds, .05):.1f}"])
    rep.table(["H", "5%", "25%", "50%", "75%", "95%", "95%/5%"], trows)
    return rep.close(write=write, echo=echo)


def _interp_log(p, x, u):
    """log10 of the table value at probability u: u clamped to the table, log10(x) linear in p."""
    u = min(max(u, p[0]), p[-1])
    for i in range(1, len(p)):
        if u <= p[i]:
            f = (u - p[i - 1]) / (p[i] - p[i - 1])
            return math.log10(x[i - 1]) + f * (math.log10(x[i]) - math.log10(x[i - 1]))
    return math.log10(x[-1])


if __name__ == "__main__":
    main()
