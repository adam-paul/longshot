"""Write method/v0_1/priors.toml from the derivations in tools/method_reflectivity.py, method_spin.py and
method_class.py, plus the quoted and judgement constants set out below with their sources.

Usage: uv run python -I tools/method_priors_toml.py          write the file
       uv run python -I tools/method_priors_toml.py --check  exit 1 if the file on disk differs

Run by hand when the method changes, never by the build. Once Adam freezes method 0.1 this file is not
regenerated: a change is a new method version.
"""
import math
import os
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from method_lib import CLASS4, H_BANDS, config  # noqa: E402
import method_class  # noqa: E402
import method_reflectivity as mr  # noqa: E402
import method_spin  # noqa: E402

OUT = os.path.join(str(config.METHOD_DIR), "priors.toml")
DERIV = "method/v0_1/derivation"

# ---- quoted and judgement constants -----------------------------------------------------------------------
DENSITY = (
    # id, lo, hi, kind, source
    ("S", 1700, 3400, "quoted",
     "docs/research/value-inputs.md section 4, 'Recommended ranges for 5-30 m bodies', row Stony (S, Q): rubble like "
     "Itokawa or Dimorphos to a single block at meteorite density. Direct densities behind it: docs/research/ground-truth.md section 7.1"),
    ("C", 900, 2300, "quoted",
     "docs/research/value-inputs.md section 4, row Dark (C, B, D, P): Bennu, Ryugu and lighter to a single block of CM"),
    ("other", 1200, 3300, "judgement",
     "docs/research/value-inputs.md section 4, row Unknown class (5th-95th, median 2,300). The research gives no row "
     "for A, D, K, L, O, R, T, V, Z as a group; this takes its widest non-metal row"),
)
DENSITY_X = (
    ("dark", "pv < 0.10 (Tholen P)", 900, 2300, "quoted",
     "docs/research/value-inputs.md section 1.4 ('P is dark primitive material like C-types') and section 4, row Dark"),
    ("mid_silicate", "0.10 <= pv < 0.30 (Tholen M), not metal-rich", 2000, 3500, "quoted",
     "docs/research/value-inputs.md section 4, row M, silicate-dominated"),
    ("mid_metal", "0.10 <= pv < 0.30 (Tholen M), metal-rich", 3000, 7500, "quoted",
     "docs/research/value-inputs.md section 4, row M, metal-rich: porous mix (1986 DA surface 3.79) to solid iron"),
    ("bright", "pv >= 0.30 (Tholen E)", 2000, 3300, "quoted",
     "docs/research/value-inputs.md section 4, row Bright enstatite (E)"),
)


# name, rate, kind, source
LABEL_ERROR = (
    ("colour", 0.21, "quoted",
     "docs/research/verify-prior-null.md, 'Label noise': colour-based classes (Sergeyev) disagree with spectral classes "
     "(Mahlke) for 21% of 874 shared objects on S/Q versus rest"),
    ("spectrum", 0.125, "quoted",
     "docs/research/verify-value-inputs.md section 4, objection 2: sources disagree on the class of at least 3 of the 24 "
     "classified objects under 6 km/s (docs/plan.md section 1.2); 3 of 24 is 12.5%. It counts any change of class, "
     "not only S/Q against the rest, and it is 'at least'. No other figure for labels from spectra was found"),
)


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def arr(vals, nd=4):
    return "[" + ", ".join(f"{v:.{nd}f}" for v in vals) + "]"


def inline(d, nd=3):
    return "{ " + ", ".join(f"{k} = {d[k]:.{nd}f}" for k in CLASS4) + " }"


def inline_s(d):
    return "{ " + ", ".join(f"{k} = {q(d[k])}" for k in CLASS4) + " }"


def bound_kind(text):
    return "quoted" if "[" in text or text.startswith("Alarcon") else "measured"


def build():
    R = mr.compute()
    S = method_spin.compute()
    C = method_class.compute()
    L = []
    w = L.append

    w("# longshot method 0.1: priors for size, spin, class and density from brightness.")
    w("#")
    w("# A PROPOSAL until Adam freezes it. After that no number here changes; a change is a new method version.")
    w("# Written by tools/method_priors_toml.py. Do not edit a number by hand: change the script and rerun it.")
    w("# docs/method.md explains each section.")
    w("#")
    w("# Every table carries `kind` and `source` for the constants in it. Where constants in one table differ in")
    w("# origin, each has its own `<name>_kind` and `<name>_source`, or a `<name>_from` naming the estimate.")
    w("#   measured  = measured from data on disk by a script in tools/; its printed output is under")
    w(f"#               {DERIV}/")
    w("#   quoted    = quoted from a file under docs/research, which names the published source")
    w("#   judgement = a choice made here, with the range it was chosen from")
    w("")
    w("schema = 1")
    w(f'method = "{config.METHOD}"')
    w('status = "proposal"')
    w(f'data_date = "{config.DATA_DATE}"')
    w('generated_by = "tools/method_priors_toml.py"')
    w("")
    w("[bands]")
    w("# Brightness bands by absolute magnitude H. Band i holds edges[i-1] <= H < edges[i].")
    w("ids = [" + ", ".join(q(b[0]) for b in H_BANDS) + "]")
    w("edges = [20.0, 22.0, 24.0, 26.0, 28.0]")
    w('kind = "judgement"')
    w('source = "the two-magnitude bins of docs/research/verify-coverage.md section 2.2, with everything brighter than H 20 in one band"')
    w("")

    # ---- size
    w("[size]")
    w('formula = "D[m] = coefficient_m * 10^(-H/5) / sqrt(pv)"')
    w("coefficient_m = 1.329e6")
    w('kind = "quoted"')
    w('source = "the standard relation, D = 1,329 km * 10^(-H/5) / sqrt(reflectivity): docs/research/value-inputs.md section 5.2, row Size from H"')
    w("# Below this brightness the reflectivity table is extrapolation.")
    w("extrapolated_fainter_than_h = 25.0")
    w(f"n_measured_at_or_fainter = {R['n_h25']}")
    w(f"faintest_measured_h = {R['h_max']:.1f}")
    w('extrapolation_kind = "measured"')
    w(f'extrapolation_source = "tools/method_reflectivity.py, {DERIV}/reflectivity.txt: {R["n_h25"]} of {R["objects"]} Spitzer objects (a < 2 au) '
      f'have H of 25 or more, {R["n_h24"]} have H of 24 or more, median H {R["h_median"]:.1f}. docs/plan.md section 7 states the same limit"')
    w("# An object with no H gets no size prior.")
    w(f"n_list_members_without_h = {R['n_no_h']}")
    w("")

    w("[h_uncertainty]")
    w("# H is drawn as normal(H, sigma) before the size formula. sigma is JPL's H_sigma where JPL gives one, else default_sigma.")
    w('use = "SBDB H_sigma"')
    w(f"default_sigma = {R['h_sigma_median']:.2f}")
    w('kind = "measured"')
    w(f'source = "tools/method_reflectivity.py, {DERIV}/reflectivity.txt: median H_sigma of the {R["h_sigma_n"]} of {R["n_members"]} list members that have one '
      f'(10th-90th percentile {R["h_sigma_p10"]:.2f}-{R["h_sigma_p90"]:.2f}). Consistent with 0.3-0.5 mag in docs/research/nongrav.md section 2.4 and 0.4 in docs/research/value-inputs.md section 5.2"')
    w('note = "The Spitzer spread already holds the H error of its own, brighter targets, so adding H_sigma counts some of it twice: the 5%-95% size range goes from a factor of 3.4 to 3.7 at the default. It errs wide."')
    w("")

    # ---- reflectivity
    w("[reflectivity]")
    w("# Quantiles of the geometric albedo measured by Spitzer for near-Earth asteroids with a < 2 au, one value per object.")
    w("# Sample by inverse transform: u uniform on (0,1), clamped to [p[0], p[-1]]; interpolate log10(pv) linearly in p.")
    w("# The table says nothing about the tails beyond its end points; a draw there takes the end value.")
    w("p = " + arr(R["p"], 3))
    w("pv = " + arr(R["pv"]))
    w(f"n_objects = {R['objects']}")
    w(f"n_rows = {R['rows_kept']}")
    w(f"n_fitted_above_1 = {R['n_above_1']}")
    w('interpolate = "log10(pv) linear in p"')
    w('kind = "measured"')
    w(f'source = "tools/method_reflectivity.py, {DERIV}/reflectivity.txt, from data/research/dl/coverage-exact/spitzer/spitzerneos.csv '
      '(Trilling et al. 2010, AJ 140, 770; 2016, AJ 152, 172). Why Spitzer and not NEOWISE: docs/research/verify-prior-null.md Trap 2 and section 3.5"')
    w('note = "The spread includes Spitzer\'s own measurement error and the error in H at the time. It is the spread of measured size at a given catalogued H, which is what the size check in docs/plan.md Appendix A tests."')
    w("")
    for c in CLASS4:
        bc = R["by_class"][c]
        w(f"[reflectivity.by_class.{c}]")
        w("# Same probabilities as [reflectivity].p. Used when the class is measured and the reflectivity is not.")
        w("# Sampled the same way. Values are kept as fitted, noise included: a knot under 0.03 or over 1 is a noisy fit.")
        w(f"n = {bc['n']}")
        w("pv = " + arr(bc["pv"]))
        w('kind = "measured"')
        w(f'source = "tools/method_reflectivity.py, {DERIV}/reflectivity.txt section (b): Spitzer objects (a < 2 au) whose class in '
          'data/research/out-prior-null/labels.csv comes from a spectrum (Mahlke 2022, Marsset 2022, Perna 2016, JPL)"')
        w("")
    w("[reflectivity.link]")
    w("# Ties class to reflectivity in the joint draw. `all` is the share of all Spitzer objects in each reflectivity bin;")
    w("# S, C, X, other are P(bin | class) from the counts below. Bin i holds edges[i-1] <= pv < edges[i].")
    w("edges = " + arr(mr.PV_EDGES, 2))
    w("all = " + arr(C["bin_shares"]))
    for c in CLASS4:
        w(f"{c} = " + arr(C["link_like"][c]))
    w("counts = { " + ", ".join(f"{c} = [" + ", ".join(str(n) for n in C["link_counts"][c]) + "]" for c in CLASS4) + " }")
    w('kind = "measured"')
    w(f'source = "tools/method_class.py, {DERIV}/class.txt section LINK: the same spectrally classed Spitzer objects as [reflectivity.by_class]"')
    w('edges_kind = "judgement"')
    w('edges_source = "0.10 and 0.30 are Tholen\'s P/M/E limits (docs/research/value-inputs.md section 1.4); 0.20 and 0.45 split the two crowded bins"')
    cm = R["card_measured"]
    CARD_NOTE = f"{sum(cm.values())} objects (" + ", ".join(f"{c} {cm[c]}" for c in CLASS4) + ")"
    w('note = "Literature cards with a measured (not computed) reflectivity and a class give ' + CARD_NOTE + ', too few to use; see the derivation, section (a). Mahlke 2022 uses reflectivity as an input to its classes, so this table is partly circular."')
    w("")

    # ---- spin
    w("[spin]")
    w("# Chance that the rotation period is under each threshold, for an object with no measured period, by H band.")
    w("# central is used in draws. low and high are the spread between denominators, not a confidence interval.")
    w("# A draw gives a category only (under 10 min; 10 min to 1 h; 1 h to 2.2 h; 2.2 h or slower), never a period.")
    w("ids = [" + ", ".join(q(t) for t, _ in method_spin.THRESHOLDS) + "]")
    w("thresholds_h = [2.2, 1.0, 0.16666667]")
    w('kind = "quoted"')
    w('source = "2.2 h, 1 h and 10 min are the thresholds of docs/plan.md Appendix A (channel Spin from H) and docs/research/verify-coverage.md section 2"')
    w('independent_of = "size, reflectivity and class at a given H (an assumption; untested)"')
    w('independent_of_kind = "judgement"')
    w("")
    for name, _, _ in H_BANDS:
        for t, _ in method_spin.THRESHOLDS:
            p = S[name][t]
            w(f"[spin.bands.{name}.{t}]")
            w(f"low = {p['low']:.2f}")
            w(f"central = {p['central']:.2f}" if p["central"] == 0 or p["central"] >= 0.005 else f"central = {p['central']:.4f}")
            w(f"high = {p['high']:.2f}")
            w(f"low_from = {q(p['low_from'])}")
            w(f"central_from = {q(p['central_from'])}")
            w(f"high_from = {q(p['high_from'])}")
            w(f'low_kind = "{"judgement" if p["low_from"] == "floor" else bound_kind(p["low_from"])}"')
            w(f'central_kind = "{"judgement" if p["central_from"] == "midpoint" else "measured"}"')
            w(f'high_kind = "{bound_kind(p["high_from"])}"')
            w(f'source = "tools/method_spin.py, {DERIV}/spin.txt. Alarcon figures: docs/research/verify-coverage.md section 2.3"')
            w("")

    # ---- class
    w("[class]")
    w("# Shares at a given brightness, not a given size.")
    w("ids = [" + ", ".join(q(c) for c in CLASS4) + "]")
    w('members = { S = "S, Q", C = "C, B, F, G", X = "X, E, M, P", other = "A, D, K, L, O, R, T, V, Z" }')
    w('kind = "quoted"')
    w('source = "the grouping of docs/research/verify-prior-null.md section 1"')
    w("")
    w("[class.label_error]")
    w("# A measured class is a label, and labels are wrong at a known rate. In the joint draw this share of an object's")
    w("# draws take a class from the other side of S/Q against the rest: S when the label is C, X or other; else C, X")
    w("# or other by their weights. An asteroid a spacecraft brought a sample back from has no label error.")
    for name, value, kind, src in LABEL_ERROR:
        w(f"{name} = {value:.3f}")
        w(f'{name}_kind = "{kind}"')
        w(f"{name}_source = {q(src)}")
    w("colour_means = " + q("a class from broad-band colours: SsODNet technique 'Phot'"))
    w("spectrum_means = " + q("any other class label: a spectrum, or JPL's Tholen and SMASSII classes"))
    w('kind = "quoted"')
    w('source = "as given for each rate"')
    w("")
    for name, _, _ in H_BANDS:
        b = C["bands"][name]
        w(f"[class.bands.{name}]")
        w(f"# central: all class labels on disk for near-Earth asteroids with a < 2 au, band{'s' if len(b['pool']) > 1 else ''} {' and '.join(b['pool'])} pooled.")
        w("# low, high: the smallest and largest share among the estimates listed in the derivation; *_from names each.")
        w("# joint_weight: use in place of central in the joint draw (see [joint]); it returns central to within 0.001")
        w("# (solved on the bin counts of [reflectivity.link]; the draw goes through the 21 quantiles, which put")
        w("# up to 0.002 more or less in a bin).")
        w(f"n = {b['n']}")
        w("central = " + inline(b["central"], 4))
        w("low = " + inline(b["low"], 4))
        w("high = " + inline(b["high"], 4))
        w("joint_weight = " + inline(b["weights"], 4))
        w("low_from = " + inline_s(b["low_from"]))
        w("high_from = " + inline_s(b["high_from"]))
        w('kind = "measured"')
        w(f'source = "tools/method_class.py, {DERIV}/class.txt, from data/research/out-prior-null/labels.csv. A bound whose *_from names a paper is quoted from the docs/research file given in brackets"')
        w("")

    # ---- density
    w("[density]")
    w("# Bulk density by class, for turning a size into a mass. Drawn flat between lo and hi.")
    w('unit = "kg/m3"')
    w('shape = "uniform"')
    w('kind = "quoted"')
    w('source = "docs/research/value-inputs.md section 4 (\'flat within the range\'). The ranges are that report\'s judgement from Carry 2012 and the direct densities in docs/research/ground-truth.md section 7.1; none of those bodies is under about 150 m"')
    w('spin_does_not_change_density = true')
    w('spin_does_not_change_density_kind = "quoted"')
    w('spin_does_not_change_density_source = "docs/research/verify-value-inputs.md section 2.6: the rule that a fast spin implies a denser body is refuted (2011 MD, 1.1 g/cm3, turns in about 12 minutes)"')
    w("")
    for cid, lo, hi, kind, src in DENSITY:
        w(f"[density.{cid}]")
        w(f"lo = {lo}")
        w(f"hi = {hi}")
        w(f'kind = "{kind}"')
        w(f"source = {q(src)}")
        w("")
    w("[density.X]")
    w("# An X-class draw takes its density from its drawn reflectivity (Tholen's split of the X complex).")
    w("split_edges_pv = [0.10, 0.30]")
    w("metal_rich_share_of_mid = 0.38")
    w("metal_rich_share_range = [0.10, 0.60]")
    w('kind = "quoted"')
    w('source = "split: docs/research/value-inputs.md section 1.4 (E above 0.3, M 0.1-0.3, P below 0.1). 0.38: Shepard et al. 2015, 11 of 29 main-belt M-class asteroids metal-dominated by radar, same section. Range 0.10-0.60: docs/research/verify-value-inputs.md section 1 item 3, which calls 0.38 a placeholder"')
    w("")
    for sid, when, lo, hi, kind, src in DENSITY_X:
        w(f"[density.X.{sid}]")
        w(f"when = {q(when)}")
        w(f"lo = {lo}")
        w(f"hi = {hi}")
        w(f'kind = "{kind}"')
        w(f"source = {q(src)}")
        w("")
    w("[mass]")
    w('formula = "mass[t] = (pi / 6) * D[m]^3 * density[kg/m3] / 1000"')
    w('kind = "quoted"')
    w('source = "a sphere: docs/research/value-inputs.md section 4"')
    w("")

    # ---- joint
    w("[joint]")
    w("# One draw for an object. A measured quantity replaces its step. Nothing here multiplies separate probabilities.")
    w("steps = [")
    for s in (
        "1. H: normal(H, sigma) with sigma from [h_uncertainty]. No H: no size, class or spin prior.",
        "2. pv: measured value if there is one. Else, class measured: inverse transform through [reflectivity.by_class.<class>]. Else: inverse transform through [reflectivity].",
        "3. D: measured size if there is one, drawn from its stated error (missions.toml [rules.decide]); then pv = (coefficient_m * 10^(-H/5) / D)^2. Else D from [size].formula.",
        "4. class: measured class if there is one, but for the share of draws in [class.label_error] a class from the other side of S/Q against the rest, by the same weights; that class then sets pv in step 2 when pv is not measured. No measured class: draw with weight class.bands.<band>.joint_weight[c] * reflectivity.link[c][bin of pv].",
        "5. density: a bulk density on file if there is one. Else flat within [density.<class>]; for X, by pv through [density.X].",
        "6. mass: [mass].formula.",
        "7. spin: measured period if one counts (missions.toml [rules]). Else a category from [spin.bands.<band>] central values.",
    ):
        w("  " + q(s) + ",")
    w("]")
    w('kind = "judgement"')
    w('source = "docs/plan.md Appendix C, WP1: reflectivity is the shared unknown, so size, class and density are drawn together. Drawing pv first keeps the size prior equal to the Spitzer table, the one prior with a test (docs/plan.md Appendix A, Size from H)"')
    w("")
    text = "\n".join(L)
    tomllib.loads(text)
    return text


def main():
    text = build()
    if "--check" in sys.argv:
        on_disk = ""
        if os.path.exists(OUT):
            with open(OUT) as fh:
                on_disk = fh.read()
        if on_disk != text:
            sys.stderr.write("method/v0_1/priors.toml differs from what the scripts derive\n")
            sys.exit(1)
        print("priors.toml matches")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(text)
    print("wrote", os.path.relpath(OUT, str(config.ROOT)), len(text), "bytes")


if __name__ == "__main__":
    main()
