"""Chance of a fast rotation by brightness band, for method/v0_1/priors.toml [spin].

Inputs, all on disk:
  config.LCDB_DIR     lightcurve database, release 2023-10-01, summary table; quality U of 2 or 3 kept
  config.PRAVEC_TXT   Pravec's table fetched 24 November 2026; quality U of 2 or 3 kept
  data/research/dl/coverage-exact/vizier/J_AJ_152_163.tsv, J_ApJS_239_4.tsv
                      MANOS lightcurve targets (Thirouin et al. 2016, 2018): every target, with or without a period
  config.SBDB_JSON, config.NHATS_JSON   H and list membership
Quoted, not on disk: Alarcon, Licandro & Serra-Ricart 2026 (arXiv:2602.18562) shares with all targets as the
denominator, as read in docs/research/verify-coverage.md section 2.3.

Usage: uv run python -I tools/method_spin.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from method_lib import (H_BANDS, Report, Sbdb, band_of, config, fl, load_lcdb, load_nhats, load_pravec,  # noqa: E402
                        read_text, u_grade, wilson)

THRESHOLDS = (("under_2_2h", 2.2), ("under_1h", 1.0), ("under_10min", 10.0 / 60.0))
VIZIER = os.path.join(str(config.DATA), "research", "dl", "coverage-exact", "vizier")

# Alarcon et al. 2026, share of ALL observed targets turning faster than 2.2 h: (low, high, targets).
# low counts confirmed and tentative fast rotators; high adds every target with no period.
# docs/research/verify-coverage.md section 2.3. Their H ranges are 22-24, 24-26 and above 26.
ALARCON_2_2H = {"22_24": (0.606, 0.803, 66), "24_26": (0.773, 0.894, 132), "26_28": (0.941, 0.961, 51), "28_up": (0.941, 0.961, 51)}


def parse_vizier(path):
    tables, name, hdr, state = {}, None, None, 0
    for line in read_text(path, errors="replace").split("\n"):
        line = line.rstrip("\n")
        if line.startswith("#Name:"):
            name, hdr, state = line.split(":", 1)[1].strip(), None, 0
            continue
        if line.startswith("#") or not line.strip() or name is None:
            continue
        if state == 0:
            hdr = [h.strip() for h in line.split("\t")]
            tables[name] = []
            state = 1
        elif state < 3:
            state += 1
        else:
            tables[name].append(dict(zip(hdr, [v.strip() for v in line.split("\t")])))
    return tables


KIND = {"": "value", ">": "lower", "<": "upper"}


def reliable_periods(sb):
    """{pdes: (period_h, grade, source, kind)} from the lightcurve database and Pravec's table, grades 2 and 3 only.

    kind is "value", or "lower" or "upper" where the lightcurve database flags the period '>' or '<': a limit,
    which decides a threshold only from the far side (decides()).
    """
    lcdb = {p: (per, u_grade(u), KIND[flag]) for p, (per, u, flag) in load_lcdb(sb, with_flag=True).items()}
    prav, pstats = load_pravec(sb)
    out = {}
    for p, (per, g, kind) in lcdb.items():
        if g >= 2:
            out[p] = (per, g, "lcdb", kind)
    both = differ = 0
    for p, (per, g) in prav.items():
        if g < 2:
            continue
        if p in out:
            both += 1
            if out[p][3] == "value" and any((per < t) != (out[p][0] < t) for _, t in THRESHOLDS):
                differ += 1
            if g >= out[p][1] or out[p][3] != "value":
                out[p] = (per, g, "pravec", "value")
        else:
            out[p] = (per, g, "pravec", "value")
    stats = {"lcdb_any": len(lcdb), "lcdb_reliable": sum(1 for v in lcdb.values() if v[1] >= 2),
             "lcdb_limits": sum(1 for v in lcdb.values() if v[2] != "value"),
             "lcdb_reliable_limits": sum(1 for v in lcdb.values() if v[1] >= 2 and v[2] != "value"),
             "pravec_rows": pstats["rows"], "pravec_objects": len(prav),
             "pravec_reliable": sum(1 for v in prav.values() if v[1] >= 2), "both": both, "differ": differ}
    return out, stats


def decides(entry, limit_h):
    """None when the entry says nothing at this threshold, else True for 'faster than the threshold'.

    A measured period always decides. A lower limit at or above the threshold is slow; an upper limit at or
    below it is fast; any other limit could be on either side and is left out of that threshold's count.
    """
    per, kind = entry[0], entry[3]
    if kind == "value":
        return per < limit_h
    if kind == "lower":
        return False if per >= limit_h else None
    return True if per <= limit_h else None


def manos_targets(sb):
    """Every MANOS lightcurve target: {name: {h, kind (full|limit|flat), p}}; H from JPL where the name resolves."""
    t16 = parse_vizier(os.path.join(VIZIER, "J_AJ_152_163.tsv"))["J/AJ/152/163/table1"]
    t18 = parse_vizier(os.path.join(VIZIER, "J_ApJS_239_4.tsv"))["J/ApJS/239/4/table1"]
    rank = {"full": 0, "limit": 1, "flat": 2}
    obj = {}
    for rows, pc, lc, hc in ((t16, "Per", "l_Per", "HMag"), (t18, "Prot", "l_Prot", "Hmag")):
        for r in rows:
            name = r["Name"].strip()
            p = fl(r[pc])
            lim = (r[lc] or "").strip()
            kind = "full" if p and not lim else ("limit" if p else "flat")
            pdes = sb.resolve(name)
            h_tab = fl(r[hc])
            h = sb.h(pdes) if pdes and sb.h(pdes) is not None else h_tab
            prev = obj.get(name)
            if prev is None or rank[kind] < rank[prev["kind"]]:
                obj[name] = {"h": h, "h_table": h_tab if h_tab is not None else (prev or {}).get("h_table"),
                             "kind": kind, "p": p, "pdes": pdes}
    return obj


def band_counts(population, periods):
    """Per band: objects, objects with a reliable measured period, and for each threshold the count under it
    (t) and the number of objects that decide it (t + "_n": measured periods, and limits on the far side)."""
    out = {}
    for name, lo, hi in H_BANDS:
        members = [p for p, h in population.items() if h is not None and lo <= h < hi]
        with_p = [periods[p] for p in members if p in periods]
        c = {"n": len(members), "n_period": sum(1 for e in with_p if e[3] == "value"),
             "n_limit": sum(1 for e in with_p if e[3] != "value")}
        for t, lim in THRESHOLDS:
            said = [decides(e, lim) for e in with_p]
            c[t] = sum(1 for x in said if x is True)
            c[t + "_n"] = sum(1 for x in said if x is not None)
        out[name] = c
    return out


def share(x):
    """A share to two decimals; a share that would round to zero and is not zero keeps four."""
    return round(x, 2) if x == 0 or round(x, 2) > 0 else round(x, 4)


def pct(k, n):
    return "-" if n == 0 else f"{k / n:.3f}"


def main(write=True, echo=True):
    rep = Report("spin")
    sb = Sbdb()
    nh = load_nhats()
    periods, st = reliable_periods(sb)

    rep("MEASURED PERIODS, RELIABLE GRADES ONLY (U of 2 or 3)")
    rep(f"lightcurve database: near-Earth asteroids with a period {st['lcdb_any']}, reliable {st['lcdb_reliable']}")
    rep(f"Pravec's table: rows {st['pravec_rows']}, near-Earth asteroids with a period {st['pravec_objects']}, reliable {st['pravec_reliable']}")
    rep(f"lightcurve database periods flagged as limits ('>' or '<'): {st['lcdb_limits']}, reliable {st['lcdb_reliable_limits']}; "
        "a limit is counted only at a threshold it decides")
    rep(f"in both with reliable grades {st['both']}; of those on different sides of a threshold {st['differ']}; union {len(periods)}")
    rep()

    all_pop = {p: sb.h(p) for p in sb.rows}
    list_pop = {d: (sb.h(d) if d in sb.rows and sb.h(d) is not None else fl(nh[d].get("h"))) for d in nh}
    measured = {}
    for label, pop in (("list members", list_pop), ("all near-Earth asteroids", all_pop)):
        bc = band_counts(pop, periods)
        measured[label] = bc
        rep(f"{label}: {len(pop)} objects, {sum(1 for h in pop.values() if h is None)} with no H, "
            f"{sum(1 for p in pop if p in periods and periods[p][3] == 'value')} with a reliable period, "
            f"{sum(1 for p in pop if p in periods and periods[p][3] != 'value')} with a reliable limit")
        rows = []
        for name, _, _ in H_BANDS:
            c = bc[name]
            row = [name, c["n"], c["n_period"]]
            for t, _ in THRESHOLDS:
                lo, hi = wilson(c[t], c[t + "_n"])
                row += [f"{c[t]} of {c[t + '_n']}", pct(c[t], c[t + "_n"]), f"{lo:.2f}-{hi:.2f}"]
            rows.append(row)
        rep.table(["H band", "objects", "with period", "<2.2h", "share", "95%", "<1h", "share", "95%", "<10min", "share", "95%"], rows)
        rep("each count is 'under the threshold' of 'objects that decide it': measured periods, and limits on the far side")
        rep()

    rep("list members under 5 km/s with a reliable period")
    u5 = sorted((fl(nh[d]["min_dv"]["dv"]), d) for d in nh
                if d in periods and periods[d][3] == "value" and fl(nh[d]["min_dv"]["dv"]) < 5)
    rep(f"  {len(u5)} objects; under 2.2 h {sum(1 for _, d in u5 if periods[d][0] < 2.2)}; "
        f"under 10 min {sum(1 for _, d in u5 if periods[d][0] < 1 / 6)}; 2.2 h or slower: "
        + (", ".join(f"{d} ({periods[d][0]:.2f} h, U {periods[d][1]}, {periods[d][2]})" for _, d in u5 if periods[d][0] >= 2.2) or "none"))
    in_lcdb = load_lcdb(sb)
    only_prav = [d for d in nh if d in periods and periods[d][2] == "pravec" and d not in in_lcdb]
    rep(f"  list members whose only reliable period here is Pravec's: {len(only_prav)}")
    rep()

    rep("ALL-TARGET DENOMINATOR: MANOS (Thirouin et al. 2016, 2018)")
    manos = manos_targets(sb)
    rep(f"distinct targets {len(manos)}: full period {sum(1 for o in manos.values() if o['kind'] == 'full')}, "
        f"lower limit {sum(1 for o in manos.values() if o['kind'] == 'limit')}, flat {sum(1 for o in manos.values() if o['kind'] == 'flat')}; "
        f"H taken from JPL for {sum(1 for o in manos.values() if o['pdes'])}, from the paper for {sum(1 for o in manos.values() if not o['pdes'])}")
    manos_band = {}
    rows = []
    for name, lo, hi in H_BANDS:
        o = [x for x in manos.values() if x["h"] is not None and lo <= x["h"] < hi]
        full = [x for x in o if x["kind"] == "full"]
        c = {"n": len(o), "full": len(full), "limit": sum(1 for x in o if x["kind"] == "limit"),
             "flat": sum(1 for x in o if x["kind"] == "flat")}
        row = [name, c["n"], c["full"], c["limit"], c["flat"]]
        for t, lim in THRESHOLDS:
            k = sum(1 for x in full if x["p"] < lim)
            # a lower limit at or above the threshold is known slow; everything else unmeasured could be fast
            could = sum(1 for x in o if x["kind"] == "flat" or (x["kind"] == "limit" and x["p"] < lim))
            c[t] = k
            c[t + "_upper"] = k + could
            row += [k, pct(k, c["n"]), pct(k + could, c["n"])]
        manos_band[name] = c
        rows.append(row)
    rep.table(["H band", "targets", "full", "limit", "flat", "<2.2h", "of all", "upper", "<1h", "of all", "upper", "<10min", "of all", "upper"], rows)
    rep("'of all' = measured fast rotators over every target (a lower bound); 'upper' adds every target that could still be fast")
    rep("check against docs/research/verify-coverage.md section 2.3, which bins by the papers' own H:")
    for lab, lo, hi in (("H < 22", -99, 22), ("22-24", 22, 24), ("24-26", 24, 26), ("H >= 26", 26, 99)):
        o = [x for x in manos.values() if x["h_table"] is not None and lo <= x["h_table"] < hi]
        k = sum(1 for x in o if x["kind"] == "full" and x["p"] < 2.2)
        k10 = sum(1 for x in o if x["kind"] == "full" and x["p"] < 1 / 6)
        rep(f"  {lab}: {k} of {len(o)} under 2.2 h ({pct(k, len(o))}); {k10} under 10 min ({pct(k10, len(o))})")
    rep()

    rep("ALL-TARGET DENOMINATOR: Alarcon et al. 2026 (quoted), share under 2.2 h, low to high")
    for b in ("22_24", "24_26", "26_28"):
        lo, hi, n = ALARCON_2_2H[b]
        rep(f"  {b if b != '26_28' else 'above 26'}: {lo:.3f} to {hi:.3f} ({n} targets)")
    rep()

    rep("PROPOSED [spin] TABLE")
    rep("estimates per band: MANOS measured-fast over all targets; Alarcon low and high (2.2 h only); the measured-only")
    rep("share among list members; the measured-only share among all near-Earth asteroids.")
    rep("low = the smallest estimate, high = the largest, central = their midpoint. The bounds are the spread between")
    rep("denominators, not a confidence interval. Band under_20 is nearly all measured (see the first table): central")
    rep("is the measured share for all near-Earth asteroids, low is 0, high the 95% upper limit for list members.")
    prop = propose(measured, manos_band)
    rows = []
    for name, _, _ in H_BANDS:
        for t, _ in THRESHOLDS:
            p = prop[name][t]
            rows.append([name, t, f"{p['low']:.2f}", (f"{p['central']:.2f}" if p["central"] == 0 or p["central"] >= 0.005 else f"{p['central']:.4f}"), f"{p['high']:.2f}", p["low_from"], p["high_from"]])
    rep.table(["H band", "threshold", "low", "central", "high", "low from", "high from"], rows)
    ok = all(prop[b]["under_10min"][k] <= prop[b]["under_1h"][k] <= prop[b]["under_2_2h"][k]
             for b, _, _ in H_BANDS for k in ("low", "central", "high"))
    rep(f"ordered within each band (10 min <= 1 h <= 2.2 h) for low, central and high: {ok}")
    return rep.close(write=write, echo=echo)


def propose(measured, manos_band):
    """The low, central and high value per band and threshold, with the denominator each bound came from.

    Every available estimate of the share is listed; low is the smallest, high the largest, central the
    midpoint. The bounds are the spread between denominators, not a confidence interval.
    """
    ml, ma = measured["list members"], measured["all near-Earth asteroids"]
    out = {}
    for name, _, _ in H_BANDS:
        out[name] = {}
        for t, _ in THRESHOLDS:
            if name == "under_20":
                c = ma[name]
                central = c[t] / c[t + "_n"]
                high = wilson(ml[name][t], ml[name][t + "_n"])[1]
                # a share that rounds to zero is not zero: one such asteroid is on file (1 of 1,143 under 10 minutes)
                out[name][t] = {"low": 0.0, "central": share(central), "high": round(max(high, central), 2),
                                "low_from": "floor",
                                "central_from": f"all near-Earth asteroids measured ({c[t]} of {c[t + '_n']})",
                                "high_from": f"list members measured, 95% upper limit ({ml[name][t]} of {ml[name][t + '_n']})"}
                continue
            est = [(manos_band[name][t] / manos_band[name]["n"], f"MANOS all targets ({manos_band[name][t]} of {manos_band[name]['n']})"),
                   (ml[name][t] / ml[name][t + "_n"], f"list members measured ({ml[name][t]} of {ml[name][t + '_n']})"),
                   (ma[name][t] / ma[name][t + "_n"], f"all near-Earth asteroids measured ({ma[name][t]} of {ma[name][t + '_n']})")]
            if t == "under_2_2h" and name in ALARCON_2_2H:
                lo, hi, n = ALARCON_2_2H[name]
                est.append((lo, f"Alarcon all targets, low ({n} targets)"))
                est.append((hi, f"Alarcon all targets, high ({n} targets)"))
            low, high = min(est), max(est)
            lo_v, hi_v = round(low[0], 2), round(high[0], 2)
            out[name][t] = {"low": lo_v, "central": round((lo_v + hi_v) / 2 + 1e-9, 2), "high": hi_v,
                            "low_from": low[1], "central_from": "midpoint", "high_from": high[1]}
    return out


def compute():
    """Everything the tests compare with priors.toml."""
    sb = Sbdb()
    nh = load_nhats()
    periods, _ = reliable_periods(sb)
    all_pop = {p: sb.h(p) for p in sb.rows}
    list_pop = {d: (sb.h(d) if d in sb.rows and sb.h(d) is not None else fl(nh[d].get("h"))) for d in nh}
    measured = {"list members": band_counts(list_pop, periods), "all near-Earth asteroids": band_counts(all_pop, periods)}
    manos = manos_targets(sb)
    manos_band = {}
    for name, lo, hi in H_BANDS:
        o = [x for x in manos.values() if x["h"] is not None and lo <= x["h"] < hi]
        c = {"n": len(o)}
        for t, lim in THRESHOLDS:
            c[t] = sum(1 for x in o if x["kind"] == "full" and x["p"] < lim)
        manos_band[name] = c
    return propose(measured, manos_band)


if __name__ == "__main__":
    main()
