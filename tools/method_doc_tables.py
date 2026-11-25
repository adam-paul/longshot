"""Write the tables in docs/method.md from method/v0_1/*.toml, so the document cannot drift from the constants.

Each table sits between `<!-- table:NAME -->` and `<!-- /table -->`. This script replaces what is between them.
It reads only the three TOML files: no data, no network.

Usage: uv run python -I tools/method_doc_tables.py           rewrite the tables in docs/method.md
       uv run python -I tools/method_doc_tables.py --check   exit 1 if the document's tables are out of date
"""
import math
import os
import re
import sys
import tomllib
from statistics import NormalDist

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METHOD = os.path.join(ROOT, "method", "v0_1")
DOC = os.path.join(ROOT, "docs", "method.md")
CLASSES = ("S", "C", "X", "other")
BAND_LABEL = {"under_20": "under 20", "20_22": "20–22", "22_24": "22–24", "24_26": "24–26", "26_28": "26–28", "28_up": "28 and fainter"}
CLASS_LABEL = {"S": "S (S, Q)", "C": "C (C, B, F, G)", "X": "X (X, E, M, P)", "other": "other"}


def load(name):
    with open(os.path.join(METHOD, name), "rb") as fh:
        return tomllib.load(fh)


def md(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def inv(p, x, u):
    u = min(max(u, p[0]), p[-1])
    for i in range(1, len(p)):
        if u <= p[i]:
            f = (u - p[i - 1]) / (p[i] - p[i - 1])
            return 10 ** (math.log10(x[i - 1]) + f * (math.log10(x[i]) - math.log10(x[i - 1])))
    return x[-1]


def q_sorted(v, p):
    k = (len(v) - 1) * p
    lo = int(math.floor(k))
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def metres(x):
    return f"{x:.0f}" if x >= 10 else f"{x:.1f}"


def tables():
    pri, mis, obs = load("priors.toml"), load("missions.toml"), load("observe.toml")
    R = pri["reflectivity"]
    at = lambda tab, p: tab[R["p"].index(p)]
    t = {}

    show = (0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975)
    t["reflectivity"] = md(["Share of objects below"] + [f"{100 * p:g}%" for p in show],
                           [["Reflectivity"] + [f"{at(R['pv'], p):.3f}" for p in show]])

    sig = pri["h_uncertainty"]["default_sigma"]
    nd = NormalDist()
    zs = [nd.inv_cdf((j + 0.5) / 41) for j in range(41)]
    pvs = [inv(R["p"], R["pv"], (i + 0.5) / 400) for i in range(400)]
    rows = []
    for h in (22.0, 24.0, 26.2, 27.7, 30.0):
        ds = sorted(pri["size"]["coefficient_m"] * 10 ** (-(h + sig * z) / 5) / math.sqrt(pv) for z in zs for pv in pvs)
        rows.append([f"{h:g}"] + [metres(q_sorted(ds, p)) for p in (0.05, 0.25, 0.5, 0.75, 0.95)])
    t["size"] = md(["H", "5%", "25%", "50%", "75%", "95%"], rows)

    t["by_class"] = md(["Class", "Objects", "5%", "50%", "95%"],
                       [[CLASS_LABEL[c], R["by_class"][c]["n"]] + [f"{at(R['by_class'][c]['pv'], p):.3f}" for p in (0.05, 0.5, 0.95)]
                        for c in CLASSES])

    L = R["link"]
    e = L["edges"]
    bins = [f"under {e[0]:.2f}"] + [f"{e[i]:.2f}–{e[i + 1]:.2f}" for i in range(len(e) - 1)] + [f"{e[-1]:.2f} and over"]
    t["link"] = md(["Reflectivity"] + bins,
                   [[CLASS_LABEL[c] + f", {sum(L['counts'][c])} objects"] + [f"{x:.2f}" for x in L[c]] for c in CLASSES]
                   + [["all Spitzer objects"] + [f"{x:.2f}" for x in L["all"]]])

    S = pri["spin"]["bands"]
    # a share that would round to zero and is not zero keeps the figures that show it (1 of 1,143 is 0.0009)
    share = lambda x: f"{x:.2f}" if x == 0 or x >= 0.005 else f"{x:.4f}"
    cell = lambda v: f"{share(v['central'])} ({v['low']:.2f}–{v['high']:.2f})"
    t["spin"] = md(["H", "under 2.2 h", "under 1 h", "under 10 min"],
                   [[BAND_LABEL[b], cell(S[b]["under_2_2h"]), cell(S[b]["under_1h"]), cell(S[b]["under_10min"])] for b in pri["bands"]["ids"]])
    t["spin_from"] = md(["H", "low from", "high from"],
                        [[BAND_LABEL[b], S[b]["under_2_2h"]["low_from"], S[b]["under_2_2h"]["high_from"]] for b in pri["bands"]["ids"]])

    C = pri["class"]["bands"]
    pc = lambda b, c: f"{100 * C[b]['central'][c]:.0f}% ({100 * C[b]['low'][c]:.0f}–{100 * C[b]['high'][c]:.0f})"
    t["class"] = md(["H", "Labelled objects"] + [CLASS_LABEL[c] for c in CLASSES],
                    [[BAND_LABEL[b], C[b]["n"]] + [pc(b, c) for c in CLASSES] for b in pri["bands"]["ids"]])

    D = pri["density"]
    rows = [["S", f"{D['S']['lo']:,}–{D['S']['hi']:,}", D["S"]["kind"]],
            ["C", f"{D['C']['lo']:,}–{D['C']['hi']:,}", D["C"]["kind"]]]
    for part, label in (("dark", "X, reflectivity under 0.10"), ("mid_silicate", "X, 0.10–0.30, not metal-rich"),
                        ("mid_metal", f"X, 0.10–0.30, metal-rich ({100 * D['X']['metal_rich_share_of_mid']:.0f}% of that bin)"),
                        ("bright", "X, 0.30 and over")):
        rows.append([label, f"{D['X'][part]['lo']:,}–{D['X'][part]['hi']:,}", D["X"][part]["kind"]])
    rows.append(["other", f"{D['other']['lo']:,}–{D['other']['hi']:,}", D["other"]["kind"]])
    t["density"] = md(["Class", "kg/m³, flat within the range", "Kind"], rows)

    op = {">=": "at least", "<=": "at most"}
    for m in mis["order"]:
        rows = []
        for g in mis[m]["gates"]:
            unit = "" if g["id"] == "findable" else " " + g["unit"]
            rows.append([g["label"], f"{op[g['op']]} {g['preset']:,g}{unit}", f"{g['range'][0]:,g}–{g['range'][1]:,g}{unit}", g["kind"]])
        t[f"gates_{m}"] = md(["Gate", "Preset", "Range in the sources", "Kind"], rows)
        rows = []
        for n in mis[m]["named"]:
            res = n["status"] if n["status"] != "untested" else f"untested, {n['p']:.4g}"      # never rounded to 1
            rows.append([n["designation"], res, ", ".join(f"{k} {v}" for k, v in n["gates"].items()), n["why"]])
        t[f"named_{m}"] = md(["Target", "Result", "Gates", "Why"], rows)

    N = obs["needs"]
    rows = []
    prev = None
    for tier in N["lightcurve"]["tiers"]:
        rows.append([f"{'up to' if prev is None else f'{prev:g} to'} {tier['max_mag']:g}", tier["label"]])
        prev = tier["max_mag"]
    rows.append([f"fainter than {prev:g}", N["lightcurve"]["fainter"]])
    t["needs_lightcurve"] = md(["Peak magnitude V", "A lightcurve needs"], rows)
    rows = []
    prev = None
    for tier in N["size"]["tiers"]:
        rows.append([f"up to {tier['max_mag']:g}", tier["label"]])
        prev = tier["max_mag"]
    rows.append([f"fainter than {prev:g}", N["size"]["fainter"]])
    t["needs_size"] = md(["Peak magnitude V", "A size or reflectivity needs"], rows)

    h2 = lambda x: 0.0 if x <= 0 or x >= 1 else -x * math.log2(x) - (1 - x) * math.log2(1 - x)
    gain = lambda p, q: h2(p) - q * h2(p / q)
    ex = ((0.5, 0.5, "the gate is the only open question, an even bet"),
          (0.1, 0.1, "the gate is the only open question, one chance in ten"),
          (0.25, 0.5, "two open gates, each an even bet"),
          (0.36, 0.36, "2011 AA37, surface work, a lightcurve (its size gate is all but certain)"),
          (0.315, 1.0, "2021 UH2, surface work, a lightcurve (its period is already measured)"),
          (0.315, 0.315, "2021 UH2, surface work, a size"))
    t["gain"] = md(["p", "q", "Gain, bits", "Case"], [[f"{p:g}", f"{q:g}", f"{gain(p, q):.2f}", why] for p, q, why in ex])
    return t


BLOCK = re.compile(r"(<!-- table:(\w+) -->\n)((?:(?!<!-- table:).)*?)(<!-- /table -->)", re.S)


def render(text):
    t = tables()
    used = set()

    def sub(m):
        used.add(m.group(2))
        return m.group(1) + t[m.group(2)] + "\n" + m.group(4)

    out = BLOCK.sub(sub, text)
    return out, sorted(set(t) - used)


def main():
    with open(DOC) as fh:
        text = fh.read()
    out, unused = render(text)
    if "--check" in sys.argv:
        if out != text:
            sys.stderr.write("docs/method.md tables are out of date; run tools/method_doc_tables.py\n")
            sys.exit(1)
        print("docs/method.md tables match")
        return
    with open(DOC, "w") as fh:
        fh.write(out)
    print("wrote docs/method.md;", "tables not placed: " + ", ".join(unused) if unused else "every table placed")


if __name__ == "__main__":
    main()
