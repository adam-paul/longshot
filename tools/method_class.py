"""Class shares by brightness band, and the link between class and reflectivity, for
method/v0_1/priors.toml [class] and [joint].

Inputs, all on disk:
  data/research/out-prior-null/labels.csv   one class per near-Earth asteroid (built 21 November 2026 by
                          data/research/scripts/pn_build_labels.py from Mahlke 2022, Marsset 2022, Devogele 2019,
                          Perna 2016, JPL's spec fields, Sergeyev 2023, Ieva 2020, Deshapriya 2023 and others)
  config.SSODNET_CARDS    parameters.physical.taxonomy, for list members
  config.SPITZER_CSV      reflectivities, through tools/method_reflectivity.py
Quoted, not on disk: survey shares as read in docs/research/source-prior.md sections 4 and 7 and
docs/research/verify-prior-null.md sections 3.5 and 5.

Classes: S (S and Q), C (C, B, F, G), X (X, E, M, P), other (A, D, K, L, O, R, T, V, Z).
Every share is for asteroids of a given brightness, not a given size.

Usage: uv run python -I tools/method_class.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from method_lib import (CLASS4, H_BANDS, Report, Sbdb, band_of, class4, config, fl, iter_cards,  # noqa: E402
                        load_nhats, wilson)
import method_reflectivity as mr  # noqa: E402

MIN_N = 30  # an on-disk sample smaller than this is listed but does not set a bound
# Bands 26_28 and 28_up share one on-disk estimate: 28_up alone has under 20 labelled objects.
POOL = {"under_20": ("under_20",), "20_22": ("20_22",), "22_24": ("22_24",), "24_26": ("24_26",),
        "26_28": ("26_28", "28_up"), "28_up": ("26_28", "28_up")}

# Published survey shares, as quoted in docs/research. (bands, {class: share}, citation, where quoted)
QUOTED = (
    (("under_20", "20_22"), {"S": 0.60, "C": 0.20},
     "Binzel et al. 2019: 60% S, 20% C, constant from 10 km to 100 m", "source-prior.md section 4"),
    (("20_22", "22_24"), {"S": 0.50, "C": 0.15},
     "Moskovitz et al. 2026: S+Q about 50% at H 22; C near 15%", "source-prior.md section 4"),
    (("26_28", "28_up"), {"S": 0.35, "C": 0.15},
     "Moskovitz et al. 2026: S+Q about 35% at H 28; C near 15%", "source-prior.md section 4"),
    (("24_26",), {"S": 0.438, "C": 0.109, "X": 0.238},
     "Devogele et al. 2019 (MANOS spectra, mean H 25): S+Q 43.8%, X 23.8%, C 10.9%", "source-prior.md section 4"),
    (("22_24", "24_26", "26_28"), {"S": 0.404},
     "Lopez-Oquendo et al. 2026, observed (5-150 m): S 40.4%", "source-prior.md section 4; verify-prior-null.md section 5"),
    (("22_24", "24_26", "26_28"), {"S": 0.66},
     "Sanchez et al. 2024 (under 300 m): S-complex 66%", "source-prior.md sections 4 and 7"),
    (("24_26", "26_28", "28_up"), {"S": 0.50, "C": 0.14, "X": 0.25, "other": 0.11},
     "list members at H 24 and fainter, 105 objects: S/Q 50%, C 14%, X 25%, other 11%", "verify-prior-null.md section 5"),
    (("24_26", "26_28", "28_up"), {"S": 0.35, "C": 0.11, "X": 0.20},
     "pooled surveys at H 24-29, low end: S+Q 35%, X 20%, C 11%", "source-prior.md section 8.1"),
    (("24_26", "26_28", "28_up"), {"S": 0.45, "C": 0.15, "X": 0.25},
     "pooled surveys at H 24-29, high end: S+Q 45%, X 25%, C 15%", "source-prior.md section 8.1"),
)


def load_labels():
    out = []
    with open(mr.LABELS_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["tax4"]:
                continue
            out.append({"pdes": r["pdes"], "a": fl(r["a"]), "h": fl(r["H"]), "nhats": r["nhats"] == "1",
                        "cls": {"S": "S", "C": "C", "X": "X", "O": "other"}[r["tax4"]],
                        "spec": r["tax4_spec"] == "1", "src": r["tax4_src"]})
    return out


def counts(sel, bands):
    c = {k: 0 for k in CLASS4}
    for r in sel:
        if band_of(r["h"]) in bands:
            c[r["cls"]] += 1
    return c


def shares(c):
    n = sum(c.values())
    return {k: (c[k] / n if n else 0.0) for k in CLASS4}


def card_classes(sb, nh):
    out = []
    for fn, c in iter_cards():
        tx = (c["parameters"].get("physical") or {}).get("taxonomy") or {}
        g = class4(tx.get("class") or tx.get("complex"))
        pdes = sb.resolve(c.get("number"), c.get("name"), *(c.get("aliases") or []))
        if g and pdes in nh:
            out.append({"pdes": pdes, "h": sb.h(pdes), "cls": g})
    return out


def link_table(sb):
    """Counts of spectrally classed Spitzer objects by class and reflectivity bin, and the Spitzer bin shares."""
    objs, _ = mr.spitzer_objects()
    lab = mr.labels_by_pdes()
    nb = len(mr.PV_EDGES) + 1
    cnt = {c: [0] * nb for c in CLASS4}
    for o in objs:
        pdes = sb.resolve(o["number"], o["desig"], o["name"])
        if pdes in lab and lab[pdes][2]:
            cnt[lab[pdes][0]][mr.pv_bin(o["pv"])] += 1
    marg = [0] * nb
    for o in objs:
        marg[mr.pv_bin(o["pv"])] += 1
    return cnt, [m / len(objs) for m in marg]


def rake(target, like, marg, iters=2000):
    """Weights a[c] such that drawing a bin from marg, then a class with weight a[c] * like[c][bin],
    returns classes in the target shares. Normalised to sum to 1."""
    a = dict(target)
    for _ in range(iters):
        got = implied(a, like, marg)
        a = {c: a[c] * target[c] / got[c] for c in CLASS4}
        s = sum(a.values())
        a = {c: a[c] / s for c in CLASS4}
    return a


def implied(a, like, marg):
    out = {c: 0.0 for c in CLASS4}
    for b, m in enumerate(marg):
        z = sum(a[c] * like[c][b] for c in CLASS4)
        for c in CLASS4:
            out[c] += m * a[c] * like[c][b] / z
    return out


def compute():
    sb = Sbdb()
    nh = load_nhats()
    labels = load_labels()
    a2 = [r for r in labels if r["a"] is not None and r["a"] < 2 and r["h"] is not None]
    cards = card_classes(sb, nh)
    res = {"bands": {}, "n_labels": len(labels), "n_a2": len(a2), "n_cards": len(cards)}
    for name, _, _ in H_BANDS:
        pool = POOL[name]
        est = []
        c_all = counts(a2, pool)
        est.append(("all labels, a < 2 au, band" + ("s " if len(pool) > 1 else " ") + "+".join(pool), c_all))
        est.append(("spectra only, a < 2 au", counts([r for r in a2 if r["spec"]], pool)))
        est.append(("colours and compilations, a < 2 au", counts([r for r in a2 if not r["spec"]], pool)))
        est.append(("list members, class on a literature card", counts(cards, pool)))
        central = shares(c_all)
        rows = [(label, sum(c.values()), shares(c), "measured") for label, c in est]
        for bands, sh, cite, where in QUOTED:
            if name in bands:
                rows.append((cite + " [" + where + "]", None, sh, "quoted"))
        low, high, low_from, high_from = {}, {}, {}, {}
        for k in CLASS4:
            cand = [(sh[k], label) for label, n, sh, kind in rows if k in sh and (n is None or n >= MIN_N)]
            low[k], low_from[k] = min(cand)
            high[k], high_from[k] = max(cand)
        res["bands"][name] = {"pool": pool, "n": sum(c_all.values()), "counts": c_all, "central": central,
                              "low": low, "high": high, "low_from": low_from, "high_from": high_from, "rows": rows}
    cnt, marg = link_table(sb)
    like = {c: [n / sum(cnt[c]) for n in cnt[c]] for c in CLASS4}
    res["link_counts"], res["link_like"], res["bin_shares"] = cnt, like, marg
    for name, _, _ in H_BANDS:
        b = res["bands"][name]
        b["unraked"] = implied(b["central"], like, marg)
        b["weights"] = rake(b["central"], like, marg)
        b["check"] = implied(b["weights"], like, marg)
        # what the X draws are, by Tholen's reflectivity split: P < 0.10, M 0.10-0.30, E > 0.30
        xs = []
        for bi, m in enumerate(marg):
            z = sum(b["weights"][c] * like[c][bi] for c in CLASS4)
            xs.append(m * b["weights"]["X"] * like["X"][bi] / z)
        t = sum(xs)
        b["x_split"] = {"P": xs[0] / t, "M": (xs[1] + xs[2]) / t, "E": (xs[3] + xs[4]) / t}
    return res


def main(write=True, echo=True):
    rep = Report("class")
    res = compute()
    rep("CLASS SHARES BY BRIGHTNESS BAND")
    rep(f"labelled near-Earth asteroids {res['n_labels']}; with a < 2 au and an H {res['n_a2']}; "
        f"list members with a class on a card {res['n_cards']}")
    rep(f"an on-disk sample under {MIN_N} objects is listed but sets no bound")
    rep()
    for name, _, _ in H_BANDS:
        b = res["bands"][name]
        rep(f"band {name} (on-disk estimates pooled over {'+'.join(b['pool'])})")
        rows = []
        for label, n, sh, kind in b["rows"]:
            rows.append([kind, "-" if n is None else n] + [f"{sh[k]:.3f}" if k in sh else "-" for k in CLASS4] + [label])
        rep.table(["kind", "N"] + list(CLASS4) + ["estimate"], rows)
        c = b["counts"]
        rep("  central (all labels, a < 2 au): " + ", ".join(
            f"{k} {b['central'][k]:.3f} [{wilson(c[k], b['n'])[0]:.2f}-{wilson(c[k], b['n'])[1]:.2f}]" for k in CLASS4) + f"; N {b['n']}")
        rep("  low:  " + ", ".join(f"{k} {b['low'][k]:.3f}" for k in CLASS4))
        rep("  high: " + ", ".join(f"{k} {b['high'][k]:.3f}" for k in CLASS4))
        for k in CLASS4:
            rep(f"    {k} low from: {b['low_from'][k]}")
            rep(f"    {k} high from: {b['high_from'][k]}")
        rep()

    rep("LINK BETWEEN CLASS AND REFLECTIVITY")
    rep("Spitzer objects (a < 2 au) with a class from a spectrum, by reflectivity bin")
    edges = ["< %.2f" % mr.PV_EDGES[0]] + ["%.2f-%.2f" % (mr.PV_EDGES[i], mr.PV_EDGES[i + 1]) for i in range(len(mr.PV_EDGES) - 1)] + [">= %.2f" % mr.PV_EDGES[-1]]
    rep.table(["class"] + edges + ["all"], [[c] + res["link_counts"][c] + [sum(res["link_counts"][c])] for c in CLASS4])
    rep("P(bin | class):")
    rep.table(["class"] + edges, [[c] + [f"{x:.3f}" for x in res["link_like"][c]] for c in CLASS4])
    rep("share of all Spitzer objects (a < 2 au) in each bin: " + ", ".join(f"{x:.3f}" for x in res["bin_shares"]))
    x = res["link_counts"]["X"]
    rep(f"X objects by Tholen's split: P (< 0.10) {x[0]}, M (0.10-0.30) {x[1] + x[2]}, E (>= 0.30) {x[3] + x[4]} of {sum(x)}")
    rep()
    rep("JOINT DRAW: reflectivity from the Spitzer quantiles, then class with weight w[band][class] * P(bin | class)")
    rep("'unraked' is the class mix that comes out if the central shares are used as weights; 'weights' are the")
    rep("values that return the central shares on these bin shares; 'check' is the mix they return. A draw through the")
    rep("21 reflectivity quantiles puts up to 0.002 more or less in a bin, and returns the central shares to within 0.001.")
    for name, _, _ in H_BANDS:
        b = res["bands"][name]
        rep(f"band {name}")
        rep.table(["", *CLASS4], [
            ["central"] + [f"{b['central'][k]:.4f}" for k in CLASS4],
            ["unraked"] + [f"{b['unraked'][k]:.4f}" for k in CLASS4],
            ["weights"] + [f"{b['weights'][k]:.4f}" for k in CLASS4],
            ["check"] + [f"{b['check'][k]:.4f}" for k in CLASS4]])
        rep(f"  X draws by reflectivity: P {b['x_split']['P']:.2f}, M {b['x_split']['M']:.2f}, E {b['x_split']['E']:.2f}")
    return rep.close(write=write, echo=echo)


if __name__ == "__main__":
    main()
