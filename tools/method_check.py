"""An independent check of method/v0_1/*.toml.

Written by the checker, not by the authors of the constants. It shares no code with the other scripts in
tools/: every formula is typed again here from the TOML files' own descriptions, so a slip in a derivation
script and the same slip in its test cannot hide each other.

What it checks:
  1. every TOML file parses; shares sum to one; quantile tables rise; bounds are ordered
  2. units: dollars per troy ounce against dollars per kilogram, tonnes against kilograms, parts per million
     against fractions, hours against minutes
  3. the Spitzer table gives the documented ratio (measured size about 0.71 of the size at reflectivity 0.14)
     and the 21 reflectivity quantiles in priors.toml
  4. the joint draw returns the central class shares, and by how much it misses
  5. the mission presets on the named targets, by plain random draws (the authors used a fixed grid)
  6. the gain formula and its worked rows
  7. every single-draw check and all three worked examples of value.toml, recomputed from the constants
  8. nothing in a method file defines or exports a mean, median, middle quantile or expected value of dollars
  9. the ladder's arithmetic, and that every fact is dated, sourced and due a recheck
 10. constants held in two files are the same in both

Usage: uv run python -I tools/method_check.py            print every check; exit 1 if any fails
       uv run python -I tools/method_check.py --quick    20,000 draws per worked example, not 200,000
                                                         (tail figures are then compared loosely)

No network, no clock. Standard library only. Random draws are seeded from fixed strings.
"""
import csv
import json
import math
import os
import random
import re
import sys
import tomllib
from statistics import NormalDist

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METHOD = os.path.join(ROOT, "method", "v0_1")
DATA = os.path.join(ROOT, "data")
SNAPSHOT = os.path.join(DATA, "snapshots", "2026-11-24")
SPITZER = os.path.join(DATA, "research", "dl", "coverage-exact", "spitzer", "spitzerneos.csv")
FILES = ("priors.toml", "missions.toml", "observe.toml", "value.toml", "ladder.toml")
CLASSES = ("S", "C", "X", "other")
G_PER_TROY_OUNCE = 31.1034768
ND = NormalDist()


class Checks:
    def __init__(self, out=sys.stdout.write):
        self.out, self.failed, self.n = out, [], 0

    def section(self, title):
        self.out(f"\n== {title} ==\n")

    def ok(self, cond, text):
        self.n += 1
        if not cond:
            self.failed.append(text)
        self.out(f"  {'ok  ' if cond else 'FAIL'} {text}\n")
        return cond

    def near(self, got, want, text, rel=1e-6, abs_=0.0):
        return self.ok(abs(got - want) <= max(abs_, rel * abs(want)), f"{text}: {got:.6g} against {want:.6g}")

    def note(self, text):
        self.out(f"       {text}\n")


def load_all():
    out = {}
    for name in FILES:
        with open(os.path.join(METHOD, name), "rb") as fh:
            out[name[:-5]] = tomllib.load(fh)
    return out


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def q7(values, p):
    """Quantile by linear interpolation between order statistics."""
    v = sorted(values)
    k = (len(v) - 1) * p
    i = int(k)
    j = min(i + 1, len(v) - 1)
    return v[i] + (v[j] - v[i]) * (k - i)


def nearest_rank(sorted_values, q):
    return sorted_values[min(len(sorted_values) - 1, max(0, math.ceil(q * len(sorted_values)) - 1))]


def inverse(ps, xs, u):
    """Inverse transform through a quantile table: log10 linear in p, the end value outside the table."""
    u = min(ps[-1], max(ps[0], u))
    for i in range(1, len(ps)):
        if u <= ps[i]:
            t = (u - ps[i - 1]) / (ps[i] - ps[i - 1])
            return 10 ** (math.log10(xs[i - 1]) + t * (math.log10(xs[i]) - math.log10(xs[i - 1])))
    return xs[-1]


# ---------------------------------------------------------------------------------------------------------
# 1. shape
# ---------------------------------------------------------------------------------------------------------

def check_shape(c, m):
    c.section("1. Files parse; shares sum to one; tables rise; bounds are ordered")
    c.ok(len(m) == 5, "five TOML files parse with tomllib")
    pri, val = m["priors"], m["value"]
    R = pri["reflectivity"]
    c.ok(all(b > a for a, b in zip(R["p"], R["p"][1:])) and 0 < R["p"][0] and R["p"][-1] < 1, "reflectivity probabilities rise, inside (0, 1)")
    c.ok(len(R["p"]) == len(R["pv"]) and all(b >= a for a, b in zip(R["pv"], R["pv"][1:])), "reflectivity quantiles do not fall")
    for k in CLASSES:
        t = R["by_class"][k]["pv"]
        c.ok(len(t) == len(R["p"]) and all(b >= a for a, b in zip(t, t[1:])), f"reflectivity quantiles for class {k} do not fall")
    link = R["link"]
    c.ok(abs(sum(link["all"]) - 1) < 5e-4, f"reflectivity bin shares sum to {sum(link['all']):.4f}")
    for k in CLASSES:
        c.ok(abs(sum(link[k]) - 1) < 5e-4 and len(link[k]) == len(link["edges"]) + 1, f"link row {k} sums to {sum(link[k]):.4f}")
        n = sum(link["counts"][k])
        c.ok(all(abs(link[k][i] - link["counts"][k][i] / n) < 5e-5 for i in range(len(link[k]))) and n == R["by_class"][k]["n"],
             f"link row {k} is its counts over {n}")
    for band in pri["bands"]["ids"]:
        b = pri["class"]["bands"][band]
        for key in ("central", "joint_weight"):
            c.ok(abs(sum(b[key][k] for k in CLASSES) - 1) < 5e-4, f"class {key}, band {band}, sums to {sum(b[key][k] for k in CLASSES):.4f}")
        c.ok(all(b["low"][k] <= b["central"][k] + 1e-9 and b["central"][k] <= b["high"][k] + 1e-9 for k in CLASSES),
             f"class low <= central <= high, band {band}")
        sp = pri["spin"]["bands"][band]
        for key in ("low", "central", "high"):
            c.ok(sp["under_10min"][key] <= sp["under_1h"][key] <= sp["under_2_2h"][key], f"spin {key}, band {band}: 10 min <= 1 h <= 2.2 h")
        for t in pri["spin"]["ids"]:
            c.ok(0 <= sp[t]["low"] <= sp[t]["central"] <= sp[t]["high"] <= 1, f"spin {t}, band {band}: 0 <= low <= central <= high <= 1")
    c.ok(pri["spin"]["thresholds_h"][0] == 2.2 and pri["spin"]["thresholds_h"][1] == 1.0
         and abs(pri["spin"]["thresholds_h"][2] * 60 - 10) < 1e-5, "spin thresholds are 2.2 h, 1 h and 10 minutes, in hours")
    d = pri["density"]
    for name, t in (("S", d["S"]), ("C", d["C"]), ("other", d["other"]), ("X dark", d["X"]["dark"]),
                    ("X mid silicate", d["X"]["mid_silicate"]), ("X mid metal", d["X"]["mid_metal"]), ("X bright", d["X"]["bright"])):
        c.ok(500 <= t["lo"] < t["hi"] <= 8000, f"density {name}: {t['lo']}-{t['hi']} kg/m3, a range in kilograms per cubic metre")
    for cls, bands in val["kinds"].items():
        for band, rows in bands.items():
            if not isinstance(rows, list):
                continue
            for s in range(3):
                tot = sum(r["share"][s] for r in rows)
                c.ok(abs(tot - 1) < 1e-9, f"value kinds {cls}.{band}, scenario {val['scenarios']['order'][s]}: shares sum to {tot:.3f}")
            for r in rows:
                if "hydrated" in r:
                    h = r["hydrated"]
                    c.ok(0 <= h[0] <= h[1] <= h[2] <= 1, f"value kinds {cls}.{band}: hydrated share rises low to high")
    for name, mix in val["mix"].items():
        tot = sum(v for v in mix.values() if isinstance(v, float))
        c.ok(abs(tot - 1) < 5e-4, f"metal mix {name} sums to {tot:.4f}")
    gt = val["grade_table"]["iron_meteorite"]
    c.ok(all(b[0] > a[0] and b[1] > a[1] for a, b in zip(gt, gt[1:])) and gt[0][0] == 0 and gt[-1][0] == 1, "iron grade table rises from 0 to 1")
    for g in ("oc_h", "oc_l", "oc_ll", "enstatite_chondrite"):
        t = val["material"][g]["grade_ppm"]
        c.ok(0 < t["lo"] < t["hi"] < 10, f"grade {g}: {t['lo']}-{t['hi']} ppm of bulk rock")
    for name, tiers in (("lightcurve", m["observe"]["needs"]["lightcurve"]["tiers"]), ("size", m["observe"]["needs"]["size"]["tiers"])):
        mags = [t["max_mag"] for t in tiers]
        c.ok(mags == sorted(mags), f"observe needs.{name}: magnitude tiers rise")


# ---------------------------------------------------------------------------------------------------------
# 2. units
# ---------------------------------------------------------------------------------------------------------

def check_units(c, m):
    c.section("2. Units")
    val, pri = m["value"], m["priors"]
    P = val["prices"]
    c.near(P["g_per_troy_ounce"], G_PER_TROY_OUNCE, "grams in a troy ounce")
    for el in val["counted"]["priced"]:
        years = P["usd_per_troy_ounce"][el]
        c.ok(len(years) == len(P["years"]), f"{el}: one price per year")
        want = [x * 1000.0 / G_PER_TROY_OUNCE for x in (min(years), sum(years) / len(years), max(years))]
        got = P["usd_per_kg"][el]
        c.ok(all(abs(g - w) <= 0.5 for g, w in zip(got, want)), f"{el}: $/kg [low, central, high] = $/troy oz x 1000 / 31.1035 "
             f"({got[0]:.0f}, {got[1]:.0f}, {got[2]:.0f})")
        c.ok(got[0] <= got[1] <= got[2], f"{el}: low <= central <= high")
        cap = val["market"]["cap_kg"][el]
        c.near(cap, val["market"]["supply_t"][el] * 1000.0 * val["market"]["cap_share_of_supply"], f"{el}: cap in kg is a tenth of the supply in tonnes")
    c.ok(val["counted"]["unpriced"] not in P["usd_per_kg"] and val["counted"]["unpriced"] not in val["market"]["cap_kg"], "osmium has no price and no cap")
    wf = val["material"]["carbonaceous"]["water_fraction"]
    c.ok(0 < wf["lo"] < wf["hi"] < 0.2, f"water fraction {wf['lo']}-{wf['hi']} is a fraction of mass, not a percentage")
    mf = val["material"]["iron_rich"]["metal_fraction"]
    c.ok(0 < mf["lo"] < mf["hi"] <= 1, f"iron-rich: the 100%-metal grade is multiplied by a metal fraction of {mf['lo']}-{mf['hi']}")
    c.ok(val["material"]["carbonaceous"]["counted"] is False and "grade_ppm" not in val["material"]["carbonaceous"],
         "dark rock carries no counted grade")
    only_iron = [k for k, v in val["material"].items() if "grade_table" in v]
    c.ok(only_iron == ["iron_rich"], "the pure-metal grade table is used by the iron-rich material only")
    c.near(pri["size"]["coefficient_m"], 1.329e6, "size coefficient is 1,329 km in metres")
    # mass of a 15 m sphere at 2,500 kg/m3 in tonnes: verify-value-inputs.md section 2.6 confirms 4,418 t
    c.near(math.pi / 6 * 15 ** 3 * 2500 / 1000, 4418, "15 m sphere at 2,500 kg/m3, tonnes", rel=1e-3)
    spin = next(g for g in m["missions"]["surface"]["gates"] if g["id"] == "spin")
    crit_h = math.sqrt(3 * math.pi / (spin["gravitational_constant"] * spin["density_kgm3"])) / 3600
    c.near(crit_h, spin["preset"], "critical period at the preset density, hours", rel=5e-3)
    L = m["ladder"]
    for rho_key, lim_key in (("light_rock_kg_m3", "light_rock_limit_h"), ("dense_rock_kg_m3", "dense_rock_limit_h")):
        got = math.sqrt(3 * math.pi / (6.6743e-11 * L["spin_limit"][rho_key])) / 3600
        c.near(got, L["spin_limit"][lim_key], f"ladder spin limit at {L['spin_limit'][rho_key]:.0f} kg/m3, hours", rel=5e-3)
    tw = next(f for f in L["fact"] if f["id"] == "tianwen_2")
    c.ok("asteroid_period_h" not in tw or abs(tw["asteroid_period_h"] * 60 - tw["asteroid_period_min"]) < 0.05,
         "Tianwen-2's target: period in minutes and in hours agree")
    c.ok(L["thresholds"]["very_fast_period_min"] / 60 < L["thresholds"]["sampled_min_period_h"], "ladder: ten minutes is shorter than four hours")
    for g in m["missions"]["capture"]["gates"]:
        if g["id"] == "mass":
            # a 10 m sphere of rock at 2,500 kg/m3 is about 1,300 t: the two capture presets are of one scale
            c.ok(g["unit"] == "t" and 100 <= g["preset"] <= 3600, f"capture mass preset {g['preset']:.0f} is in tonnes")


# ---------------------------------------------------------------------------------------------------------
# 3. Spitzer
# ---------------------------------------------------------------------------------------------------------

def check_spitzer(c, m):
    c.section("3. Size from brightness against the Spitzer table")
    if not os.path.exists(SPITZER):
        c.ok(False, f"Spitzer table not found: {SPITZER}")
        return
    R = m["priors"]["reflectivity"]
    rows, by_obj = [], {}
    with open(SPITZER, newline="") as fh:
        for r in csv.DictReader(fh):
            a, pv, d_km, h = num(r["a"]), num(r["pv"]), num(r["diam"]), num(r["absmag"])
            if a is None or a >= 2.0 or not pv or pv <= 0 or not d_km or d_km <= 0 or h is None:
                continue
            d14_km = 1329.0 * 10 ** (-h / 5) / math.sqrt(0.14)
            rows.append(d_km / d14_km)
            by_obj.setdefault(r["desig"], []).append(pv)
    med = q7(rows, 0.5)
    c.ok(len(rows) == R["n_rows"], f"rows with a < 2 au and a fitted size: {len(rows)}")
    c.ok(0.70 <= med <= 0.72, f"median measured size over the size at reflectivity 0.14: {med:.3f} (documented: about 0.71)")
    inside = sum(1 for x in rows if 0.5 * med <= x <= 2 * med) / len(rows)
    c.ok(0.88 <= inside <= 0.95, f"share between half and double that figure: {inside:.2f} (docs/plan.md: about nine in ten)")
    objs = [math.exp(sum(math.log(x) for x in v) / len(v)) for v in by_obj.values()]
    c.ok(len(objs) == R["n_objects"], f"distinct objects: {len(objs)}")
    worst = max(abs(q7(objs, p) - x) for p, x in zip(R["p"], R["pv"]))
    c.ok(worst < 5e-5, f"the 21 quantiles in priors.toml are those of the table (largest difference {worst:.1e})")
    c.ok(sum(1 for x in objs if x > 1) == R["n_fitted_above_1"], f"objects fitted above a reflectivity of 1: {sum(1 for x in objs if x > 1)}")
    med_pv = inverse(R["p"], R["pv"], 0.5)
    c.near(math.sqrt(0.14 / med_pv), 0.717, "size at the median reflectivity over the size at 0.14", rel=5e-3)
    for h, want in ((22.0, 100.0), (24.0, 40.0), (26.2, 15.0), (27.7, 7.0)):
        got = m["priors"]["size"]["coefficient_m"] * 10 ** (-h / 5) / math.sqrt(med_pv)
        c.ok(abs(got / want - 1) < 0.07, f"H {h}: {got:.1f} m at the median reflectivity (docs/plan.md Terms: about {want:.0f} m)")


# ---------------------------------------------------------------------------------------------------------
# 4. joint draw
# ---------------------------------------------------------------------------------------------------------

def pv_bin(edges, pv):
    return sum(1 for e in edges if pv >= e)


def check_joint(c, m):
    c.section("4. The joint draw returns the central class shares")
    pri = m["priors"]
    R, link = pri["reflectivity"], pri["reflectivity"]["link"]
    n = 20000
    pvs = [inverse(R["p"], R["pv"], (i + 0.5) / n) for i in range(n)]
    table_bins = [0.0] * (len(link["edges"]) + 1)
    for pv in pvs:
        table_bins[pv_bin(link["edges"], pv)] += 1.0 / n
    c.note("share of draws in each reflectivity bin, from the quantile table: " + ", ".join(f"{x:.4f}" for x in table_bins)
           + "; from the counts: " + ", ".join(f"{x:.4f}" for x in link["all"]))
    worst_bins = max(abs(a - b) for a, b in zip(table_bins, link["all"]))
    c.ok(worst_bins < 0.01, f"the quantile table puts the same share in each bin as the counts do (largest difference {worst_bins:.4f})")
    worst = 0.0
    for band in pri["bands"]["ids"]:
        b = pri["class"]["bands"][band]
        got = {k: 0.0 for k in CLASSES}
        for pv in pvs:
            i = pv_bin(link["edges"], pv)
            w = {k: b["joint_weight"][k] * link[k][i] for k in CLASSES}
            z = sum(w.values())
            for k in CLASSES:
                got[k] += w[k] / z / n
        miss = max(abs(got[k] - b["central"][k]) for k in CLASSES)
        worst = max(worst, miss)
        c.ok(miss < 0.005, f"band {band}: classes drawn " + ", ".join(f"{k} {got[k]:.4f}" for k in CLASSES) + f"; largest miss {miss:.4f}")
    c.note(f"largest miss over all bands: {worst:.4f} (the weights were solved on the counts, the draw uses the quantile table)")
    return worst


# ---------------------------------------------------------------------------------------------------------
# 5. missions
# ---------------------------------------------------------------------------------------------------------

def read_snapshot():
    with open(os.path.join(SNAPSHOT, "sbdb_neo.json")) as fh:
        raw = json.load(fh)
    idx = {f: i for i, f in enumerate(raw["fields"])}
    sb = {r[idx["pdes"]]: r for r in raw["data"]}
    with open(os.path.join(SNAPSHOT, "nhats.json")) as fh:
        nh = {o["des"]: o for o in json.load(fh)["data"]}
    return sb, idx, nh


def side(rng, value, lo, hi):
    """A draw from a value with a one-sigma range, each side its own width; never under a tenth of the value."""
    z = rng.gauss(0.0, 1.0)
    return max(value + z * ((value - lo) if z < 0 else (hi - value)), 0.1 * value)


def mission_draws(pri, h, h_sigma, n, seed, cls=None, cls_error=0.0, size=None, density=None):
    """Plain random draws of (diameter m, mass t) by the steps of priors.toml [joint].

    cls with cls_error: the label is on the wrong side of S/Q against the rest in that share of draws
    ([class.label_error]). size and density: (value, low, high), one sigma, drawn with no clamp.
    """
    rng = random.Random(seed)
    R, link, dens = pri["reflectivity"], pri["reflectivity"]["link"], pri["density"]
    band = None
    for i, b in enumerate(pri["bands"]["ids"]):
        lo = pri["bands"]["edges"][i - 1] if i else -99
        hi = pri["bands"]["edges"][i] if i < len(pri["bands"]["edges"]) else 99
        if lo <= h < hi:
            band = b
    jw = pri["class"]["bands"][band]["joint_weight"]
    central = pri["class"]["bands"][band]["central"]
    out = []
    for _ in range(n):
        hh = rng.gauss(h, h_sigma)
        d0 = pri["size"]["coefficient_m"] * 10 ** (-hh / 5)
        k = cls
        if cls and rng.random() < cls_error:
            others = [x for x in CLASSES if x != "S"] if cls == "S" else ["S"]
            k = rng.choices(others, weights=[central[x] for x in others])[0]
        if size:
            d = side(rng, *size)
            pv = (d0 / d) ** 2
        else:
            pv = inverse(R["p"], R["by_class"][k]["pv"] if k else R["pv"], rng.random())
            d = d0 / math.sqrt(pv)
        if not k:
            i = pv_bin(link["edges"], pv)
            w = [jw[x] * link[x][i] for x in CLASSES]
            k = rng.choices(CLASSES, weights=w)[0]
        if density:
            rho = side(rng, *density)
        else:
            if k != "X":
                lo, hi = dens[k]["lo"], dens[k]["hi"]
            else:
                e0, e1 = dens["X"]["split_edges_pv"]
                if pv < e0:
                    t = dens["X"]["dark"]
                elif pv >= e1:
                    t = dens["X"]["bright"]
                else:
                    t = dens["X"]["mid_metal"] if rng.random() < dens["X"]["metal_rich_share_of_mid"] else dens["X"]["mid_silicate"]
                lo, hi = t["lo"], t["hi"]
            rho = rng.uniform(lo, hi)
        out.append((d, math.pi / 6 * d ** 3 * rho / 1000.0))
    return out, band


# What the derivation (method/v0_1/derivation/missions.txt) found on disk for the named targets, beyond H, its
# uncertainty and the orbit code, which this script reads from the snapshot itself. Sizes and densities are
# (value, low, high) at one sigma. cls_error is the rate of priors.toml [class.label_error] for the label's kind.
NAMED_FACTS = {
    "2011 AA37": {"period_decides": False},
    "2022 DC5": {"cls": "S", "cls_from": "colour", "period_h": 9.675},
    "2021 UH2": {"period_h": 3.8},
    "2011 MD": {"size_m": (6.0, 4.0, 8.0), "density": (746.833, 365.25, 1144.111)},
}


def pri_n(m):
    """The number of draws the pipeline makes for an object: value.toml [exports].min_draws."""
    return m["value"]["exports"]["min_draws"]


def check_missions(c, m):
    c.section("5. Mission presets on the named targets, by random draws")
    pri, mis = m["priors"], m["missions"]
    for name in ("surface", "capture"):
        ids = [g["id"] for g in mis[name]["gates"]]
        c.ok(ids[0] == "findable" and "size" in ids, f"{name}: gates {', '.join(ids)}")
        named = mis[name]["named"]
        tally = {s: sum(1 for t in named if t["status"] == s) for s in ("pass", "untested", "fail")}
        chk = mis[name]["check"]
        c.ok((tally["pass"], tally["untested"], tally["fail"]) == (chk["known_pass"], chk["untested"], chk["known_fail"]),
             f"{name}: {tally['pass']} pass, {tally['untested']} untested, {tally['fail']} fail among the named targets, as [check] says")
        for t in named:
            c.ok(t["status"] == "pass" or len(t["why"]) > 40, f"{name}, {t['designation']}: {t['status']}" + ("" if t["status"] == "pass" else ", with a reason"))
            c.ok((t["status"] == "pass") == all(v == "pass" for v in t["gates"].values()), f"{name}, {t['designation']}: a pass only if every gate passes")
    if not os.path.exists(os.path.join(SNAPSHOT, "sbdb_neo.json")):
        c.ok(False, "snapshot not found")
        return
    sb, idx, nh = read_snapshot()
    n = 200000
    for name in ("surface", "capture"):
        gates = {g["id"]: g for g in mis[name]["gates"]}
        for t in mis[name]["named"]:
            des = t["pdes"]
            row = sb[des]
            h, hs = num(row[idx["H"]]), num(row[idx["H_sigma"]])
            occ = int(nh[des]["occ"])
            c.ok((occ <= gates["findable"]["preset"]) == (t["gates"]["findable"] == "pass"), f"{t['designation']}: orbit code {occ}")
            if t["status"] != "untested":
                continue
            f = NAMED_FACTS[t["designation"]]
            err = pri["class"]["label_error"][f["cls_from"]] if f.get("cls") else 0.0
            draws, band = mission_draws(pri, h, hs if hs is not None else pri["h_uncertainty"]["default_sigma"], n,
                                        "method check " + des, cls=f.get("cls"), cls_error=err, size=f.get("size_m"),
                                        density=f.get("density"))
            # a measured size decides its gate when it clears the preset by rules.decide.sigma; the gate is then fixed
            size_ok = lambda d: d >= gates["size"]["preset"] if name == "surface" else d <= gates["size"]["preset"]
            if f.get("size_m"):
                v, lo, hi = f["size_m"]
                k = mis["rules"]["decide"]["sigma"]
                ends = (v - k * (v - lo), v + k * (hi - v))
                decided = size_ok(ends[0]) == size_ok(ends[1])
                c.ok(decided == (t["gates"]["size"] != "untested"),
                     f"{t['designation']}: {v:g} m is {ends[0]:g} to {ends[1]:g} m at {k:g} sigma, so the size gate is {t['gates']['size']}")
                if decided:
                    size_ok = lambda d: True
            if name == "surface":
                p = sum(1 for d, _ in draws if size_ok(d)) / n
                if not f.get("period_h"):
                    p *= 1 - pri["spin"]["bands"][band]["under_2_2h"]["central"]
                else:
                    c.ok(f["period_h"] >= gates["spin"]["preset"], f"{t['designation']}: {f['period_h']} h is slower than the spin preset")
            else:
                p = sum(1 for d, mass in draws if size_ok(d) and mass <= gates["mass"]["preset"]) / n
            p = min(max(p, 1 / pri_n(m)), 1 - 1 / pri_n(m))        # an untested chance is never recorded as 0 or 1
            c.ok(abs(p - t["p"]) < 0.015, f"{t['designation']}: p {p:.3f} from {n:,} random draws against {t['p']} recorded")


# ---------------------------------------------------------------------------------------------------------
# 6. observe
# ---------------------------------------------------------------------------------------------------------

def h2(x):
    return 0.0 if x <= 0 or x >= 1 else -x * math.log2(x) - (1 - x) * math.log2(1 - x)


def gain(p, q):
    return 0.0 if q <= 0 else h2(p) - q * h2(p / q)


def check_observe(c, m):
    c.section("6. Gain formula")
    c.ok(m["observe"]["gain"]["formula"] == "gain = H2(p) - q * H2(p / q)", "the formula in observe.toml is the one recomputed here")
    for p, q, want in ((0.5, 0.5, 1.00), (0.1, 0.1, 0.47), (0.25, 0.5, 0.31), (0.36, 0.36, 0.94), (0.315, 1.0, 0.00), (0.315, 0.315, 0.90)):
        c.near(gain(p, q), want, f"gain at p {p}, q {q}", abs_=0.006)
    # the gain is the mutual information of two yes-or-no outcomes: never negative, never above the smaller entropy
    worst = min(gain(p / 50, q / 50) for q in range(1, 51) for p in range(0, q + 1))
    c.ok(worst > -1e-12, "gain is never negative for p <= q")
    c.ok(all(gain(p / 50, q / 50) <= min(h2(p / 50), h2(q / 50)) + 1e-12 for q in range(1, 51) for p in range(0, q + 1)),
         "gain never exceeds the uncertainty of the outcome or of the gate")
    c.near(h2(0.1), 0.47, "a 9-in-10 guess made certain, bits", abs_=0.005)
    c.near(h2(0.01), 0.08, "a 99-in-100 guess made certain, bits", abs_=0.005)


# ---------------------------------------------------------------------------------------------------------
# 7. value
# ---------------------------------------------------------------------------------------------------------

def value_of_draw(val, cls, pv, d_m, rho, u, size_measured):
    """Three scenarios for one draw, typed from the procedure at the top of value.toml."""
    u_kind, u_grade, u_metal, u_rho, u_hyd, u_water = u
    band = "dark" if pv < val["bands"]["dark_below"] else ("bright" if pv >= val["bands"]["bright_from"] else "mid")
    rows = val["kinds"][cls].get("any") or val["kinds"][cls][band]
    out = []
    for s in range(3):
        d = d_m if size_measured else d_m * val["size"]["diameter_factor"][s]
        cum, row = 0.0, rows[-1]
        for r in rows:
            cum += r["share"][s]
            if u_kind < cum:
                row = r
                break
        res = material_amounts(val, row["material"], s, d, rho, u_grade, u_metal, u_rho)
        res["water_t"] = 0.0
        if "hydrated" in row and u_hyd < row["hydrated"][s]:
            wf = val["material"][row["material"]]["water_fraction"]
            res["water_t"] = res["mass_t"] * (wf["lo"] + (wf["hi"] - wf["lo"]) * u_water)
        if cls == "X" and band == "mid":
            res["as_iron"] = material_amounts(val, "iron_rich", s, d, rho, u_grade, u_metal, u_rho)
        out.append(res)
    return out


def material_amounts(val, material, s, d, rho, u_grade, u_metal, u_rho):
    mat = val["material"][material]
    if "density_kg_m3" in mat:
        rho = mat["density_kg_m3"]["lo"] + (mat["density_kg_m3"]["hi"] - mat["density_kg_m3"]["lo"]) * u_rho
    mass_t = math.pi / 6 * d ** 3 * rho / 1000.0
    kg = usd = usd_nocap = 0.0
    if mat["counted"]:
        if "grade_table" in mat:
            pts = val["grade_table"][mat["grade_table"]]
            ppm = pts[-1][1]
            for (q0, v0), (q1, v1) in zip(pts, pts[1:]):
                if u_grade <= q1:
                    ppm = math.exp(math.log(v0) + (u_grade - q0) / (q1 - q0) * math.log(v1 / v0))
                    break
            ppm *= mat["metal_fraction"]["lo"] + (mat["metal_fraction"]["hi"] - mat["metal_fraction"]["lo"]) * u_metal
        else:
            ppm = mat["grade_ppm"]["lo"] + (mat["grade_ppm"]["hi"] - mat["grade_ppm"]["lo"]) * u_grade
        kg = mass_t * ppm / 1000.0  # tonnes x grams per tonne = grams; / 1000 = kilograms
        mix = val["mix"][mat["mix"][s] if isinstance(mat["mix"], list) else mat["mix"]]
        for el in val["counted"]["priced"]:
            price = val["prices"]["usd_per_kg"][el][s]
            usd += min(kg * mix[el], val["market"]["cap_kg"][el]) * price
            usd_nocap += kg * mix[el] * price
    return {"material": material, "mass_t": mass_t, "kg": kg, "usd": usd, "usd_nocap": usd_nocap}


def example_draws(val, ex, n):
    """The stand-in joint draw of value.toml [reference_draw], from the example's own inputs."""
    rd, inp = val["reference_draw"], ex["inputs"]
    rng = random.Random(f"longshot value example {ex['id']} draws method {val['meta']['method']}")
    out = []
    for _ in range(n):
        u_h, u_a, u_c, u_r, u_d = [rng.random() for _ in range(5)]
        h = inp["h"] + rd["h_sigma"] * ND.inv_cdf(min(1 - 1e-12, max(1e-12, u_h)))
        d0 = rd["coefficient_m"] * 10 ** (-h / 5)
        # a measured class is a label that is wrong in a share of draws; such a draw is made as if no class were
        # measured, among the classes on the other side of S against the rest ([reference_draw].steps)
        wrong = "class" in inp and u_c < inp.get("label_error", 0.0)
        if "d_m" in inp:
            d = inp["d_m"] * math.exp(inp["d_sigma_ln"] * ND.inv_cdf(min(1 - 1e-12, max(1e-12, u_d))))
            pv = (d0 / d) ** 2
        else:
            pv = inverse(rd["p"], rd["by_class_S"] if inp.get("class") == "S" and not wrong else rd["pv"], u_a)
            d = d0 / math.sqrt(pv)
        cls = None if wrong else inp.get("class")
        if not cls:
            i = pv_bin(rd["link_edges"], pv)
            pool = [k for k in CLASSES if not wrong or (k == "S") != (inp["class"] == "S")]
            w = [rd["joint_weight"][inp["weights"]][k] * rd["link"][k][i] for k in pool]
            pick = u_c / inp["label_error"] if wrong else u_c
            cum, cls = 0.0, pool[-1]
            for k, wk in zip(pool, w):
                cum += wk / sum(w)
                if pick < cum:
                    cls = k
                    break
        key = cls
        if cls == "X":
            key = "X_dark" if pv < val["bands"]["dark_below"] else ("X_bright" if pv >= val["bands"]["bright_from"] else "X_mid")
        lo, hi = rd["density_kg_m3"][key]
        out.append((cls, pv, d, lo + (hi - lo) * u_r))
    return out


def example_exports(val, ex, n):
    draws = example_draws(val, ex, n)
    rng = random.Random(f"longshot value example {ex['id']} value method {val['meta']['method']}")
    per = [value_of_draw(val, cls, pv, d, rho, [rng.random() for _ in range(6)], ex["size_measured"]) for cls, pv, d, rho in draws]
    low, cen, high = ([p[s] for p in per] for s in range(3))

    def share(rows, test):
        return sum(1 for r in rows if test(r)) / len(rows)

    def col(rows, key):
        return sorted(r[key] for r in rows)

    metal = {"p_nothing": share(cen, lambda r: r["kg"] == 0), "p_nothing_lo": share(high, lambda r: r["kg"] == 0),
             "p_nothing_hi": share(low, lambda r: r["kg"] == 0),
             "kg": {"q05": nearest_rank(col(low, "kg"), .05), "q25": nearest_rank(col(low, "kg"), .25),
                    "q75": nearest_rank(col(high, "kg"), .75), "q95": nearest_rank(col(high, "kg"), .95)},
             "usd": {"q05": nearest_rank(col(low, "usd"), .05), "q25": nearest_rank(col(low, "usd"), .25),
                     "q75": nearest_rank(col(high, "usd"), .75), "q95": nearest_rank(col(high, "usd"), .95)}}
    capped = nearest_rank(col(high, "usd_nocap"), .95) > 1.05 * metal["usd"]["q95"]
    iron = {"p_lo": share(low, lambda r: r["material"] == "iron_rich"), "p_hi": share(high, lambda r: r["material"] == "iron_rich")}
    sub_lo = [r["as_iron"] for r in low if "as_iron" in r]
    sub_hi = [r["as_iron"] for r in high if "as_iron" in r]
    if len(sub_lo) >= val["exports"]["min_draws_for_a_range"]:
        iron["kg"] = {"q05": nearest_rank(col(sub_lo, "kg"), .05), "q95": nearest_rank(col(sub_hi, "kg"), .95)}
        iron["usd"] = {"q05": nearest_rank(col(sub_lo, "usd"), .05), "q95": nearest_rank(col(sub_hi, "usd"), .95)}
        capped = capped or nearest_rank(col(sub_hi, "usd_nocap"), .95) > 1.05 * nearest_rank(col(sub_hi, "usd"), .95)
    metal["capped"] = capped
    water = {"p_nothing": share(cen, lambda r: r["water_t"] == 0), "p_nothing_lo": share(high, lambda r: r["water_t"] == 0),
             "p_nothing_hi": share(low, lambda r: r["water_t"] == 0)}
    w_lo = sorted(r["water_t"] for r in low if r["water_t"] > 0)
    w_hi = sorted(r["water_t"] for r in high if r["water_t"] > 0)
    if min(len(w_lo), len(w_hi)) >= val["exports"]["min_draws_for_a_range"]:
        water["tonnes"] = {"q05": nearest_rank(w_lo, .05), "q95": nearest_rank(w_hi, .95)}
    return {"metal": metal, "iron_rich": iron, "water": water}


def sig_round(x, up):
    """One significant figure, two when the first digit is 1 or 2; up for 'under', down for 'over'."""
    if x <= 0:
        return 0.0
    e = math.floor(math.log10(x))
    unit = 10.0 ** (e - (1 if int(x / 10 ** e + 1e-12) < 3 else 0))
    return (math.ceil(x / unit - 1e-9) if up else math.floor(x / unit + 1e-9)) * unit


def numbers_in(text):
    """Every figure in a sentence, as (value, unit word): '$1.6 million' -> (1.6e6, '$'), '21 kg' -> (21, 'kg')."""
    out = []
    scale = {"thousand": 1e3, "million": 1e6, "billion": 1e9}
    for mo in re.finditer(r"(\$?)([0-9][0-9,]*(?:\.[0-9]+)?)(?: (thousand|million|billion))?(?: (kg|g|tonnes))?", text):
        v = float(mo.group(2).replace(",", "")) * scale.get(mo.group(3), 1.0)
        out.append((v, "$" if mo.group(1) else (mo.group(4) or "")))
    return out


def check_value(c, m, n_draws):
    val = m["value"]
    c.section("7a. Single-draw checks of value.toml, recomputed")
    for chk in val["check"]:
        u = [chk["u"][k] for k in ("u_kind", "u_grade", "u_metal", "u_rho", "u_hyd", "u_water")]
        got = value_of_draw(val, chk["class"], chk["reflectivity"], chk["diameter_m"], chk["density_kg_m3"], u, chk["size_measured"])
        good = all(g["material"] == e["material"] and all(abs(g[k] - e[k]) <= 1e-6 * max(1.0, abs(e[k])) for k in ("mass_t", "kg", "usd", "water_t"))
                   for g, e in zip(got, chk["expect"]))
        c.ok(good, f"{chk['id']}: three scenarios reproduce")
    c.section(f"7b. Worked examples of value.toml, recomputed at {n_draws:,} draws")
    exact = n_draws == val["example"][0]["draws"]
    for ex in val["example"]:
        if "inputs" not in ex:
            c.ok(False, f"example {ex['id']}: its inputs are not in value.toml, so it cannot be recomputed from the file")
            continue
        got = example_exports(val, ex, n_draws)

        def cmp(path, g, w, tail=False):
            tol = 1e-6 if exact else (0.35 if tail else 0.15)
            good = abs(g - w) <= max(tol * abs(w), 6e-7) or (not exact and abs(g - w) < 0.012)
            c.ok(good, f"example {ex['id']} {path}: {g:.6g} against {w:.6g}")

        for part in ("metal", "iron_rich", "water"):
            for k, w in ex[part].items():
                if k == "capped":
                    c.ok(got[part][k] == w, f"example {ex['id']} metal.capped: {got[part][k]}")
                elif isinstance(w, dict):
                    c.ok(k in got[part], f"example {ex['id']} {part}.{k} is exported")
                    for qk, qw in w.items():
                        if k in got[part]:
                            cmp(f"{part}.{k}.{qk}", got[part][k][qk], qw, tail=True)
                else:
                    cmp(f"{part}.{k}", got[part][k], w)
            extra = set(got[part]) - set(ex[part])
            c.ok(not extra, f"example {ex['id']} {part}: nothing recomputed is missing from the file" + (f" (missing {sorted(extra)})" if extra else ""))
        # every figure printed in a statement is the rounding of an exported one
        e = ex
        allowed = set()
        for q, up in (("q75", True), ("q95", True), ("q25", False), ("q05", False)):
            for unit, key in (("kg", "kg"), ("$", "usd")):
                x = e["metal"][key][q]
                if x > 0:
                    allowed.add((unit, sig_round(x, up)))
        if "kg" in e["iron_rich"]:
            allowed.add(("kg", sig_round(e["iron_rich"]["kg"]["q05"], False)))
            allowed.add(("kg", sig_round(e["iron_rich"]["kg"]["q95"], True)))
            allowed.add(("$", sig_round(e["iron_rich"]["usd"]["q05"], False)))
            allowed.add(("$", sig_round(e["iron_rich"]["usd"]["q95"], True)))
        if "tonnes" in e["water"]:
            allowed.add(("t", sig_round(e["water"]["tonnes"]["q05"], False)))
            allowed.add(("t", sig_round(e["water"]["tonnes"]["q95"], True)))
        bad = []
        for sentence in ex["statements"]:
            is_water = "water" in sentence or sentence.startswith("Nine in ten of the rest")
            for v, unit in numbers_in(sentence):
                if unit == "$":
                    if not any(u == "$" and abs(v - a) <= 1e-6 * a for u, a in allowed):
                        bad.append(f"${v:,.0f}")
                elif unit in ("kg", "g", "tonnes"):
                    if is_water:
                        if not any(u == "t" and abs(v - a) <= 1e-6 * a for u, a in allowed):
                            bad.append(f"{v:g} tonnes of water")
                    else:
                        kg = v * {"kg": 1.0, "g": 1e-3, "tonnes": 1e3}[unit]
                        if not any(u == "kg" and abs(kg - a) <= 1e-6 * a for u, a in allowed):
                            bad.append(f"{v:g} {unit}")
        c.ok(not bad, f"example {ex['id']}: every kilogram, tonne and dollar figure in its sentences is a rounded export"
             + (f" (not found: {', '.join(bad)})" if bad else ""))
        # the first unitless number of a range such as '12 to 8,000 tonnes' is checked through its own sentence
        for sentence in ex["statements"]:
            mo = re.search(r"hold ([0-9][0-9,.]*) to ([0-9][0-9,.]*) (tonnes|kg)", sentence)
            if mo and "tonnes" in e["water"] and sentence.startswith("Nine in ten of the rest"):
                lo = float(mo.group(1).replace(",", ""))
                c.near(lo, sig_round(e["water"]["tonnes"]["q05"], False), f"example {ex['id']}: low end of the water range, tonnes")
            elif mo and "kg" in e["iron_rich"] and "iron-rich" in sentence:
                lo = float(mo.group(1).replace(",", "")) * (1e3 if mo.group(3) == "tonnes" else 1.0)
                c.near(lo, sig_round(e["iron_rich"]["kg"]["q05"], False), f"example {ex['id']}: low end of the iron-rich range, kg")
        count = lambda p: math.floor(100 * p + 0.5)
        first = ex["statements"][0]
        if first.startswith("Of 100 like it"):
            lo, hi = count(e["metal"]["p_nothing_lo"]), count(e["metal"]["p_nothing_hi"])
            c.ok(f"{lo} to {hi} hold no" in first or (lo == hi and f"about {lo} hold no" in first), f"example {ex['id']}: chance of nothing is printed first, as {lo} to {hi} of 100")
        else:
            c.ok(e["metal"]["p_nothing_hi"] < 0.005 or e["metal"]["p_nothing_lo"] > 0.995, f"example {ex['id']}: the class leaves one answer, and the sentence says so")


# ---------------------------------------------------------------------------------------------------------
# 8. no central dollar figure
# ---------------------------------------------------------------------------------------------------------

BANNED_KEYS = re.compile(r"(^|_)(mean|median|average|expected|q50|p50|typical|central_usd|usd_central)($|_)")


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def check_no_central(c, m):
    c.section("8. No mean, median or expected value of dollars")
    val = m["value"]
    bad = [p for p, _ in walk(val) if BANNED_KEYS.search(p.rsplit(".", 1)[-1].split("[")[0])]
    c.ok(not bad, "value.toml has no key named for a mean, median, middle quantile or expected value" + (f": {bad}" if bad else ""))
    ex_keys = sorted({p.split(".")[-1] for p, _ in walk({"e": val["example"]}) if ".usd." in p or ".kg." in p or ".tonnes." in p})
    c.ok(ex_keys == ["q05", "q25", "q75", "q95"] or ex_keys == ["q05", "q95"] or set(ex_keys) <= {"q05", "q25", "q75", "q95"},
         f"exported quantiles are {', '.join(ex_keys)}: no middle one")
    c.ok(all(w in val["exports"]["never"] for w in ("mean", "median", "q50", "expected value")), "exports.never lists mean, median, q50 and expected value")
    printed = [s for ex in val["example"] for s in ex["statements"]]
    printed += [v for st in val["statement"] for k, v in st.items() if k.startswith("template") or k in ("caveat", "size_clause")]
    printed += [st["template"] for st in val["method_statement"]]
    L = m["ladder"]
    printed += [s["text"] for s in L["sitewide"]]
    for rung in L["rung"].values():
        for key in ("state", "suffix", "size"):
            printed += [s["text"] for s in rung.get(key, [])]
    hits = [s for s in printed if re.search(r"\b(on average|mean|median|expected|typical(ly)?|worth|value[ds]?)\b", s, re.I)]
    c.ok(not hits, "no printed sentence says mean, median, expected, typical, on average, worth or value" + (f": {hits[:2]}" if hits else ""))
    water = [p for p, v in walk(val) if "water" in p.lower() and ("usd" in p.lower() or (isinstance(v, str) and "$" in v and "water" in p.split(".")[0]))]
    c.ok(not water, "water carries no dollar figure")
    c.ok("central" in val["scenarios"]["use"] and "only for the chance of nothing" in val["scenarios"]["use"],
         "the central scenario is used only for the chance of nothing")
    # the single-draw checks hold a dollar figure per scenario; none may be read as a best estimate
    with open(os.path.join(METHOD, "value.toml")) as fh:
        value_text = fh.read()
    c.ok("expect is [low, central, high]" in value_text,
         "the single-draw checks are labelled by scenario")


# ---------------------------------------------------------------------------------------------------------
# 9. ladder
# ---------------------------------------------------------------------------------------------------------

def check_ladder(c, m):
    c.section("9. Ladder: the record and its arithmetic")
    L = m["ladder"]
    facts = {f["id"]: f for f in L["fact"]}
    for f in L["fact"]:
        c.ok(all(f.get(k) for k in ("as_of", "source", "recheck")) and f["recheck"] > f["as_of"], f"fact {f['id']}: dated {f.get('as_of')}, sourced, recheck {f.get('recheck')}")
    o = facts["osiris_rex"]
    lo, hi = o["cost_usd_low"] / o["returned_g"] / 1e6, o["cost_usd_high"] / o["returned_g"] / 1e6
    c.ok(8.3 < lo < 8.5 and 9.4 < hi < 9.6, f"OSIRIS-REx: ${lo:.1f} to {hi:.1f} million a gram, printed as about ten")
    g = o["returned_g"]
    c.ok(round(1e6 / g, -3) == 8000 and round(facts["arm"]["tonnes"] * 1e6 / g, -4) == 110000 and round(facts["keck_2012"]["tonnes"] * 1e6 / g / 1e6) == 4,
         f"one tonne is {1e6 / g:,.0f} times the largest sample; the two designs {facts['arm']['tonnes'] * 1e6 / g:,.0f} and {facts['keck_2012']['tonnes'] * 1e6 / g:,.0f} times")
    pt = m["value"]["prices"]["usd_per_troy_ounce"]["Pt"]
    top = g / G_PER_TROY_OUNCE * max(pt)
    c.ok(top < 5000, f"121.6 g of platinum at the highest yearly average: ${top:,.0f}, under $5,000")
    sizes = [facts[k]["asteroid_size_m"] for k in ("hayabusa", "hayabusa2", "osiris_rex")]
    periods = [facts[k]["asteroid_period_h"] for k in ("hayabusa", "hayabusa2", "osiris_rex")]
    T = L["thresholds"]
    c.ok(T["sampled_min_m"] <= min(sizes) and T["sampled_min_period_h"] <= min(periods) and T["touched_min_m"] == facts["dart"]["asteroid_size_m"],
         f"thresholds sit at or below the record: sampled {min(sizes):.0f}-{max(sizes):.0f} m, {min(periods):.1f}-{max(periods):.1f} h")
    words = L["rung"]["brought_back"]["words"]
    c.ok((words["done"], words["not_yet_attempted"], words["proposed"]) == ("done three times, by space agencies", "not yet attempted", "proposed"),
         "the last rung's three fixed phrases")
    # Every string in the five files, cut into sentences. A sentence that denies something of every spacecraft,
    # company or buyer must say "we found" (verify-capability.md section 4, objection 14).
    sentences = []
    for name in ("ladder", "value", "missions", "observe", "priors"):
        for path, v in walk(m[name]):
            if isinstance(v, str) and not re.search(r"(^|\.)(basis|wording|corrected|note|[a-z_]*_note|source|[a-z_]*_source|caveat_source)(\[|$)", path):
                sentences += [(name, x.strip()) for x in re.split(r"(?<=[.;:])\s+", v)]
    pattern = re.compile(r"\b(No|Nothing|Nobody|None|No one)\b[^.;:]*\b(spacecraft|company|ever|buys|has (touched|reached|enclosed|approached))\b")
    neg = [f"{name}: {t}" for name, t in sentences if pattern.search(t) and "we found" not in t.lower()]
    c.ok(not neg, "every sentence that denies something of every spacecraft, company or buyer says 'we found'" + (f": {neg[:2]}" if neg else ""))
    # On an entry each such sentence stands alone, so it carries its own date. The site-wide list is dated by its first line.
    entry = [x["text"] for r in L["rung"].values() for k in ("state", "suffix") for x in r.get(k, [])]
    entry += [v for st in m["value"]["statement"] for k, v in st.items() if k.startswith("template")]
    undated = [t for t in entry if "we found" in t.lower() and not re.search(r"\b2026\b", t)]
    c.ok(not undated, "a 'we found' sentence printed on an entry carries its date" + (f" (without one: {undated[:2]})" if undated else ""))
    c.ok(L["sitewide"][0]["text"].startswith("As of " + L["meta"]["as_of_words"]), "the site-wide record opens with its date")


# ---------------------------------------------------------------------------------------------------------
# 10. the files agree with each other
# ---------------------------------------------------------------------------------------------------------

def check_agreement(c, m):
    c.section("10. The five files agree with each other")
    pri, val, mis, obs, L = m["priors"], m["value"], m["missions"], m["observe"], m["ladder"]
    R, rd, dens = pri["reflectivity"], val["reference_draw"], pri["density"]
    c.ok(rd["p"] == R["p"] and rd["pv"] == R["pv"], "value.toml's copy of the reflectivity quantiles is priors.toml's")
    c.ok(rd["by_class_S"] == R["by_class"]["S"]["pv"], "value.toml's copy of the S-type quantiles is priors.toml's")
    c.ok(rd["link_edges"] == R["link"]["edges"] and all(rd["link"][k] == R["link"][k] for k in CLASSES), "value.toml's copy of the class-reflectivity link is priors.toml's")
    for band in ("26_28", "22_24"):
        c.ok(rd["joint_weight"]["band_" + band] == pri["class"]["bands"][band]["joint_weight"], f"value.toml's copy of the joint weights, band {band}, is priors.toml's")
    pairs = (("S", dens["S"]), ("C", dens["C"]), ("other", dens["other"]), ("X_dark", dens["X"]["dark"]),
             ("X_mid", dens["X"]["mid_silicate"]), ("X_bright", dens["X"]["bright"]))
    c.ok(all(rd["density_kg_m3"][k] == [float(t["lo"]), float(t["hi"])] for k, t in pairs), "value.toml's copy of the densities is priors.toml's")
    c.ok(rd["coefficient_m"] == pri["size"]["coefficient_m"] and rd["h_sigma"] == pri["h_uncertainty"]["default_sigma"],
         "value.toml's size coefficient and H uncertainty are priors.toml's")
    c.ok([val["bands"]["dark_below"], val["bands"]["bright_from"]] == dens["X"]["split_edges_pv"], "the dark and bright reflectivity limits are the same in value.toml and priors.toml")
    for mat, key in (("enstatite_chondrite", "mid_silicate"), ("iron_rich", "mid_metal")):
        d = val["material"][mat]["density_kg_m3"]
        c.ok((d["lo"], d["hi"]) == (dens["X"][key]["lo"], dens["X"][key]["hi"]), f"density of {mat} in value.toml is priors.toml [density.X.{key}]")
    iron = next(r for r in val["kinds"]["X"]["mid"] if r["material"] == "iron_rich")["share"]
    c.ok(iron[1] == dens["X"]["metal_rich_share_of_mid"] and [iron[0], iron[2]] == dens["X"]["metal_rich_share_range"],
         f"metal-rich share of mid-reflectivity X: {iron[0]}, {iron[1]}, {iron[2]} in value.toml; the same value and range in priors.toml")
    spin = next(g for g in mis["surface"]["gates"] if g["id"] == "spin")
    c.ok(L["spin_limit"]["screening_line_h"] == spin["preset"] == pri["spin"]["thresholds_h"][0], "the 2.2 h line is the same in ladder.toml, missions.toml and priors.toml")
    c.ok(L["spin_limit"]["published_bar_h"] in [a["value"] for a in spin["alternatives"]], "the ladder's published one-hour bar is one of the spin gate's alternatives")
    f_s = next(g for g in mis["surface"]["gates"] if g["id"] == "findable")
    f_c = next(g for g in mis["capture"]["gates"] if g["id"] == "findable")
    c.ok((f_s["preset"], f_s["op"]) == (f_c["preset"], f_c["op"]), "the orbit gate is the same for both mission types (the ladder reads one)")
    c.ok(f"{f_s['preset']} or better" in L["rung"]["found_again"]["state"][0]["text"] and f"worse than {f_s['preset']}" in L["rung"]["found_again"]["state"][1]["text"],
         "the ladder's first rung names the orbit gate's preset")
    kinds = sorted(x["window"] for x in L["rung"]["found_again"]["suffix"])
    c.ok(kinds == ["none", "pointable", "survey_only"] and all(k in obs["window"] for k in ("pointable", "survey_only", "none")),
         "the ladder has one window sentence for each kind of window in observe.toml")
    texts = [x["text"] for x in L["rung"]["found_again"]["state"]]
    c.ok(not any("point" in t for t in texts), "the ladder's orbit-code sentence makes no claim about pointing; JPL's flag does that")
    gate_ids = {g["id"] for name in mis["order"] for g in mis[name]["gates"]}
    c.ok(all(o["resolves"] in gate_ids for o in obs["observations"]), "every observation in observe.toml resolves a gate that exists")
    c.ok(mis["rules"]["period"]["min_grade"] == 2 and "graded under 2" in L["classes"]["spin"]["not_measured"],
         "a period graded under 2 decides no gate in missions.toml and counts as not measured in ladder.toml")
    c.ok(pri["method"] == mis["method"] == obs["method"] == val["meta"]["method"] == L["meta"]["method"], "all five files are method " + pri["method"])
    c.ok(val["meta"]["research_checked"] == L["meta"]["as_of"], "value.toml and ladder.toml give the same date for the research check")
    sizes = {t["designation"]: t for name in mis["order"] for t in mis[name]["named"]}
    c.ok(set(NAMED_FACTS) <= set(sizes), "every named target this script holds facts for is in missions.toml")


def main(argv, out=None):
    c = Checks(out or sys.stdout.write)
    m = load_all()
    check_shape(c, m)
    check_units(c, m)
    check_spitzer(c, m)
    check_joint(c, m)
    check_missions(c, m)
    check_observe(c, m)
    check_value(c, m, 20000 if "--quick" in argv else m["value"]["example"][0]["draws"])
    check_no_central(c, m)
    check_ladder(c, m)
    check_agreement(c, m)
    c.out(f"\n{c.n - len(c.failed)} of {c.n} checks pass\n")
    for f in c.failed:
        c.out(f"FAILED: {f}\n")
    return 1 if c.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
