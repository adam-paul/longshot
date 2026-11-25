"""Reference implementation of method/v0_1/value.toml, and the three worked examples.

This is the oracle for longshot/value.py: feed both the same draws and compare.
It reads only method/v0_1/value.toml. No network, standard library only,
deterministic (seeded from a string).

Usage:
  uv run python tools/value_examples.py            # the three examples, 200,000 draws each
  uv run python tools/value_examples.py 20000      # fewer draws
  uv run python tools/value_examples.py --toml     # sections 10 and 11 of value.toml, printed
  uv run python tools/value_examples.py --write    # the same, written into value.toml in place of the old ones

Functions other code may call:
  load_method() -> dict
  reference_draws(method, example_id, n) -> list of (cls, reflectivity, diameter_m, density_kg_m3)
                                             a stand-in for longshot/draws.py; see value.toml section 9
  summarise(method, draws, size_measured, seed) -> the exports of value.toml section 7:
                                             {metal, iron_rich, water, basis}; add statements(...) for the record
  statements(method, exports, size_measured, class_label=None) -> list of str
  statement_pairs(...same...) -> list of (id, sentence); the ladder needs the ids
  draw_value(method, cls, reflectivity, diameter_m, density, u, size_measured) -> per-scenario figures
"""
import math, os, random, sys, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METHOD_PATH = os.path.join(ROOT, "method", "v0_1", "value.toml")
SCEN = (0, 1, 2)  # low, central, high
LOW, CENTRAL, HIGH = SCEN
U_NAMES = ("u_kind", "u_grade", "u_metal", "u_rho", "u_hyd", "u_water")


def load_method(path=METHOD_PATH):
    with open(path, "rb") as f:
        return tomllib.load(f)


# ---------------------------------------------------------------------------
# The procedure of value.toml section 1
# ---------------------------------------------------------------------------

def band_of(m, reflectivity):
    if reflectivity < m["bands"]["dark_below"]:
        return "dark"
    if reflectivity >= m["bands"]["bright_from"]:
        return "bright"
    return "mid"


def kind_rows(m, cls, band):
    k = m["kinds"][cls]
    return k["any"] if "any" in k else k[band]


def pick(rows, u, s):
    """First row whose cumulative share in scenario s exceeds u."""
    acc = 0.0
    for row in rows:
        acc += row["share"][s]
        if u < acc:
            return row
    return rows[-1]


def table_value(points, u):
    """Log-linear interpolation of [[q, value], ...] at u."""
    for (q0, v0), (q1, v1) in zip(points, points[1:]):
        if u <= q1:
            t = (u - q0) / (q1 - q0)
            return math.exp(math.log(v0) + t * (math.log(v1) - math.log(v0)))
    return points[-1][1]


def sphere_mass_t(diameter_m, density_kg_m3):
    return math.pi / 6.0 * diameter_m ** 3 * density_kg_m3 / 1000.0


def material_figures(m, material_id, s, diameter_m, density, u):
    """kg of the six metals, dollars capped and uncapped, and mass, for one material in scenario s."""
    mat = m["material"][material_id]
    u_kind, u_grade, u_metal, u_rho, u_hyd, u_water = u
    if "density_kg_m3" in mat:
        d = mat["density_kg_m3"]
        density = d["lo"] + (d["hi"] - d["lo"]) * u_rho
    mass_t = sphere_mass_t(diameter_m, density)
    if not mat["counted"]:
        return mass_t, 0.0, 0.0, 0.0
    if "grade_table" in mat:
        f = mat["metal_fraction"]
        ppm = table_value(m["grade_table"][mat["grade_table"]], u_grade) * (f["lo"] + (f["hi"] - f["lo"]) * u_metal)
    else:
        g = mat["grade_ppm"]
        ppm = g["lo"] + (g["hi"] - g["lo"]) * u_grade
    kg = mass_t * ppm / 1000.0
    mix_id = mat["mix"][s] if isinstance(mat["mix"], list) else mat["mix"]
    mix = m["mix"][mix_id]
    usd = usd_free = 0.0
    for el in m["counted"]["priced"]:
        price = m["prices"]["usd_per_kg"][el][s]
        el_kg = kg * mix[el]
        usd += min(el_kg, m["market"]["cap_kg"][el]) * price
        usd_free += el_kg * price
    return mass_t, kg, usd, usd_free


def draw_value(m, cls, reflectivity, diameter_m, density, u, size_measured):
    """Figures for one draw in each scenario.

    Returns a list of three dicts (low, central, high) with material, mass_t, kg,
    usd, usd_uncapped, water_t, and, for a class X draw in the mid band, iron_kg and
    iron_usd: what it would hold if iron-rich.
    """
    band = band_of(m, reflectivity)
    rows = kind_rows(m, cls, band)
    out = []
    for s in SCEN:
        factor = 1.0 if size_measured else m["size"]["diameter_factor"][s]
        d = diameter_m * factor
        row = pick(rows, u[0], s)
        mass_t, kg, usd, usd_free = material_figures(m, row["material"], s, d, density, u)
        water_t = 0.0
        if "hydrated" in row and u[4] < row["hydrated"][s]:
            wf = m["material"][row["material"]]["water_fraction"]
            water_t = mass_t * (wf["lo"] + (wf["hi"] - wf["lo"]) * u[5])
        rec = {"material": row["material"], "mass_t": mass_t, "kg": kg, "usd": usd,
               "usd_uncapped": usd_free, "water_t": water_t}
        if cls == "X" and band == "mid":
            _, ikg, iusd, iusd_free = material_figures(m, "iron_rich", s, d, density, u)
            rec["iron_kg"], rec["iron_usd"], rec["iron_usd_uncapped"] = ikg, iusd, iusd_free
        out.append(rec)
    return out


def quantile(sorted_values, q):
    """Nearest rank: the value at index ceil(q x n) - 1."""
    n = len(sorted_values)
    return sorted_values[min(n - 1, max(0, math.ceil(q * n) - 1))]


def summarise(m, draws, size_measured, seed):
    """The exports of value.toml section 7 for one object's draws."""
    rng = random.Random(seed)
    per = []
    for cls, refl, d, rho in draws:
        u = tuple(rng.random() for _ in U_NAMES)
        per.append(draw_value(m, cls, refl, d, rho, u, size_measured))
    n = len(per)
    min_range = m["exports"]["min_draws_for_a_range"]

    def col(s, key):
        return sorted(p[s][key] for p in per)

    def share(s, test):
        return sum(1 for p in per if test(p[s])) / n

    kg_lo, kg_hi = col(LOW, "kg"), col(HIGH, "kg")
    usd_lo, usd_hi = col(LOW, "usd"), col(HIGH, "usd")
    metal = {
        "p_nothing": share(CENTRAL, lambda r: r["kg"] == 0.0),
        "p_nothing_lo": share(HIGH, lambda r: r["kg"] == 0.0),
        "p_nothing_hi": share(LOW, lambda r: r["kg"] == 0.0),
        "kg": {"q05": quantile(kg_lo, 0.05), "q25": quantile(kg_lo, 0.25),
               "q75": quantile(kg_hi, 0.75), "q95": quantile(kg_hi, 0.95)},
        "usd": {"q05": quantile(usd_lo, 0.05), "q25": quantile(usd_lo, 0.25),
                "q75": quantile(usd_hi, 0.75), "q95": quantile(usd_hi, 0.95)},
    }
    capped = quantile(col(HIGH, "usd_uncapped"), 0.95) > metal["usd"]["q95"] * 1.05

    iron = {"p_lo": share(LOW, lambda r: r["material"] == "iron_rich"),
            "p_hi": share(HIGH, lambda r: r["material"] == "iron_rich")}
    sub_lo = sorted(p[LOW]["iron_kg"] for p in per if "iron_kg" in p[LOW])
    if len(sub_lo) >= min_range:
        sub_hi = sorted(p[HIGH]["iron_kg"] for p in per if "iron_kg" in p[HIGH])
        usd_sub_lo = sorted(p[LOW]["iron_usd"] for p in per if "iron_usd" in p[LOW])
        usd_sub_hi = sorted(p[HIGH]["iron_usd"] for p in per if "iron_usd" in p[HIGH])
        iron["kg"] = {"q05": quantile(sub_lo, 0.05), "q95": quantile(sub_hi, 0.95)}
        iron["usd"] = {"q05": quantile(usd_sub_lo, 0.05), "q95": quantile(usd_sub_hi, 0.95)}
        free_hi = sorted(p[HIGH]["iron_usd_uncapped"] for p in per if "iron_usd" in p[HIGH])
        capped = capped or quantile(free_hi, 0.95) > iron["usd"]["q95"] * 1.05
    metal["capped"] = capped

    water = {
        "p_nothing": share(CENTRAL, lambda r: r["water_t"] == 0.0),
        "p_nothing_lo": share(HIGH, lambda r: r["water_t"] == 0.0),
        "p_nothing_hi": share(LOW, lambda r: r["water_t"] == 0.0),
    }
    w_lo = sorted(p[LOW]["water_t"] for p in per if p[LOW]["water_t"] > 0.0)
    w_hi = sorted(p[HIGH]["water_t"] for p in per if p[HIGH]["water_t"] > 0.0)
    if len(w_lo) >= min_range and len(w_hi) >= min_range:
        water["tonnes"] = {"q05": quantile(w_lo, 0.05), "q95": quantile(w_hi, 0.95)}

    return {"metal": metal, "iron_rich": iron, "water": water, "basis": m["exports"]["basis"]["text"]}


# ---------------------------------------------------------------------------
# Formatting (value.toml [format]) and statements (section 8)
# ---------------------------------------------------------------------------

def round_figure(x, up):
    """One significant figure, two when the first digit is 1 or 2. Up for 'under', down for 'over'."""
    if x <= 0:
        return 0.0
    e = math.floor(math.log10(x))
    lead = int(x / 10 ** e + 1e-12)
    unit = 10.0 ** (e - (1 if lead < 3 else 0))
    r = x / unit
    r = math.ceil(r - 1e-9) if up else math.floor(r + 1e-9)
    return r * unit


def _num(x):
    if x >= 100:
        return f"{x:,.0f}"
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s


_USD_SCALES = ((1e9, " billion"), (1e6, " million"), (1e3, " thousand"))


def fmt_usd(x, up):
    v = round_figure(x, up)
    for size, word in _USD_SCALES:
        if v >= size:
            return f"${_num(v / size)}{word}"
    return f"${_num(v)}"


def fmt_usd_range(lo, hi):
    """'$A to $B'. A low end under $1,000 beside a high end with a scale word: both in figures ('$40 to $160,000')."""
    a, b = round_figure(lo, False), round_figure(hi, True)
    if a < 1e3 <= b:
        return f"${a:,.0f} to ${b:,.0f}"
    return f"{fmt_usd(lo, False)} to {fmt_usd(hi, True)}"


def fmt_kg(x, up):
    v = round_figure(x, up)
    if v < 1.0:
        return f"{_num(v * 1000.0)} g"
    if v >= 1000.0:
        return fmt_tonnes(x / 1000.0, up)
    return f"{_num(v)} kg"


def fmt_tonnes(x, up):
    v = round_figure(x, up)
    if v < 1.0:
        return f"{_num(v * 1000.0)} kg"
    if v >= 1e6:
        return f"{_num(v / 1e6)} million tonnes"
    return f"{_num(v)} tonne" if v == 1.0 else f"{_num(v)} tonnes"


def fmt_range(lo, hi):
    """'A to B'; a unit word shared by both prints once ('20 to 10,000 tonnes', '1 to 30 tonnes'). Not for dollars."""
    a, b = lo.rsplit(" ", 1), hi.rsplit(" ", 1)
    if len(a) == 2 and len(b) == 2 and a[1].removesuffix("s") == b[1].removesuffix("s") and not lo.startswith("$"):
        return f"{a[0]} to {hi}"
    return f"{lo} to {hi}"


def fmt_count(p_lo, p_hi):
    """A count of 100, as a band when the two ends differ."""
    lo, hi = math.floor(100 * p_lo + 0.5), math.floor(100 * p_hi + 0.5)
    if p_hi < 0.005:
        return "fewer than 1"
    if p_lo > 0.995:
        return "more than 99"
    if lo == hi:
        return f"about {lo}"
    if lo == 0:
        return f"up to {hi}"
    if hi == 100:
        return f"{lo} or more"
    return f"{lo} to {hi}"


def statement_pairs(m, ex, size_measured, class_label=None):
    """(id, sentence) for each statement of value.toml section 8 that applies, in order."""
    st = {s["id"]: s for s in m["statement"]}
    metal, iron, water = ex["metal"], ex["iron_rich"], ex["water"]
    out = []
    one_answer = bool(class_label) and (metal["p_nothing_hi"] < 0.005 or metal["p_nothing_lo"] > 0.995)
    if one_answer:
        t = st["metal_none_measured"]
        key = "template_some" if metal["p_nothing_hi"] < 0.005 else "template_none"
        out.append(("metal_none_measured", t[key].format(class_label=class_label)))
    else:
        out.append(("metal_none", st["metal_none"]["template"].format(
            n_none=fmt_count(metal["p_nothing_lo"], metal["p_nothing_hi"]))))
    kg, usd = metal["kg"], metal["usd"]
    if usd["q95"] > 0:
        t = st["metal_under"]
        if usd["q75"] > 0:
            s = t["template"].format(kg75=fmt_kg(kg["q75"], True), usd75=fmt_usd(usd["q75"], True),
                                     kg95=fmt_kg(kg["q95"], True), usd95=fmt_usd(usd["q95"], True))
            if one_answer:
                s = s.replace("Counting those, three", "Three")
        else:
            s = t["template_q95_only"].format(kg95=fmt_kg(kg["q95"], True), usd95=fmt_usd(usd["q95"], True))
        out.append(("metal_under", s))
    if usd["q25"] > 0:
        t = st["metal_over"]
        clause = "" if size_measured else t["size_clause"]
        if usd["q05"] > 0:
            s = t["template"].format(kg25=fmt_kg(kg["q25"], False), usd25=fmt_usd(usd["q25"], False),
                                     kg05=fmt_kg(kg["q05"], False), usd05=fmt_usd(usd["q05"], False), size_clause=clause)
        else:
            s = t["template_q25_only"].format(kg25=fmt_kg(kg["q25"], False), usd25=fmt_usd(usd["q25"], False),
                                              size_clause=clause)
        out.append(("metal_over", s))
    if iron["p_hi"] >= 0.005 and "kg" in iron:
        n_iron = fmt_count(iron["p_lo"], iron["p_hi"])
        out.append(("iron_rich", st["iron_rich"]["template"].format(
            n_iron=n_iron[0].upper() + n_iron[1:],
            kg_range=fmt_range(fmt_kg(iron["kg"]["q05"], False), fmt_kg(iron["kg"]["q95"], True)),
            usd_range=fmt_usd_range(iron["usd"]["q05"], iron["usd"]["q95"]))))
    if metal["capped"]:
        out.append(("metal_cap", st["metal_cap"]["template"]))
    if water["p_nothing_lo"] > 0.995:
        out.append(("water_none", st["water_none"]["template_all" if class_label else "template_all_no_class"]))
    else:
        out.append(("water_none", st["water_none"]["template"].format(
            n_none=fmt_count(water["p_nothing_lo"], water["p_nothing_hi"]))))
        if "tonnes" in water:
            out.append(("water_some", st["water_some"]["template"].format(t_range=fmt_range(
                fmt_tonnes(water["tonnes"]["q05"], False), fmt_tonnes(water["tonnes"]["q95"], True)))))
    out.append(("water_market", st["water_market"]["template"]))
    return out


def statements(m, ex, size_measured, class_label=None):
    """value.statements: the sentences alone, as an entry prints them."""
    return [text for _, text in statement_pairs(m, ex, size_measured, class_label)]


# ---------------------------------------------------------------------------
# The reference draw (value.toml section 9) and the three examples
# ---------------------------------------------------------------------------

EXAMPLES = {
    1: {"title": "H 26.2, nothing else measured", "h": 26.2, "weights": "band_26_28", "size_measured": False},
    # label_error: the share of draws in which the label is on the wrong side of S/Q against the rest
    # (reference_draw.label_error_spectrum, copied from priors.toml [class.label_error])
    2: {"title": "the same after a spectrum says S-type", "h": 26.2, "class": "S", "size_measured": False,
        "class_label": "S/Q", "weights": "band_26_28", "label_error": 0.125},
    3: {"title": "H 22.7 with a measured size of 60 m, good to 30%", "h": 22.7, "d_m": 60.0, "d_sigma_ln": 0.26,
        "weights": "band_22_24", "size_measured": True},
}


def _inverse(ps, values, u):
    """Inverse transform through a quantile table: log10 linear in p, clamped to the ends."""
    u = min(ps[-1], max(ps[0], u))
    for i in range(1, len(ps)):
        if u <= ps[i]:
            t = (u - ps[i - 1]) / (ps[i] - ps[i - 1])
            return 10 ** (math.log10(values[i - 1]) + t * (math.log10(values[i]) - math.log10(values[i - 1])))
    return values[-1]


def _normal_inverse(u):
    from statistics import NormalDist
    return NormalDist().inv_cdf(min(1 - 1e-12, max(1e-12, u)))


def reference_draws(m, example_id, n):
    """The stand-in joint draw for one worked example: value.toml [reference_draw].steps."""
    ex = EXAMPLES[example_id]
    rd = m["reference_draw"]
    rng = random.Random(f"longshot value example {example_id} draws method {m['meta']['method']}")
    classes = ("S", "C", "X", "other")
    edges = rd["link_edges"]
    draws = []
    for _ in range(n):
        u_h, u_a, u_c, u_r, u_d = (rng.random() for _ in range(5))
        h = ex["h"] + rd["h_sigma"] * _normal_inverse(u_h)
        d0 = rd["coefficient_m"] * 10 ** (-h / 5.0)
        # step 4, first half: a measured class is a label, wrong in a stated share of draws. A mislabelled
        # draw is drawn as if no class were measured, among the classes on the other side of S against the rest.
        err = ex.get("label_error", 0.0)
        mislabelled = "class" in ex and u_c < err
        if "d_m" in ex:
            d = ex["d_m"] * math.exp(ex["d_sigma_ln"] * _normal_inverse(u_d))
            refl = (d0 / d) ** 2
        else:
            refl = _inverse(rd["p"], rd["by_class_S"] if ex.get("class") == "S" and not mislabelled else rd["pv"], u_a)
            d = d0 / math.sqrt(refl)
        if "class" in ex and not mislabelled:
            cls = ex["class"]
        else:
            b = sum(1 for e in edges if refl >= e)
            pool = [c for c in classes if not mislabelled or (c == "S") != (ex["class"] == "S")]
            w = [rd["joint_weight"][ex["weights"]][c] * rd["link"][c][b] for c in pool]
            u_pick = u_c / err if mislabelled else u_c
            acc, cls = 0.0, pool[-1]
            for c, wc in zip(pool, w):
                acc += wc / sum(w)
                if u_pick < acc:
                    cls = c
                    break
        key = cls if cls != "X" else "X_" + band_of(m, refl)
        lo, hi = rd["density_kg_m3"][key]
        draws.append((cls, refl, d, lo + (hi - lo) * u_r))
    return draws


def run_example(m, example_id, n):
    ex = EXAMPLES[example_id]
    draws = reference_draws(m, example_id, n)
    seed = f"longshot value example {example_id} value method {m['meta']['method']}"
    exports = summarise(m, draws, ex["size_measured"], seed)
    return draws, exports, statements(m, exports, ex["size_measured"], ex.get("class_label"))


def _q(v, q):
    return quantile(sorted(v), q)


def hand_arithmetic(m, out):
    """The single-draw cases in value.toml [[check]], recomputed."""
    out("\n== Hand arithmetic (value.toml [[check]]) ==\n")
    for c in m["check"]:
        u = tuple(c["u"][k] for k in U_NAMES)
        res = draw_value(m, c["class"], c["reflectivity"], c["diameter_m"], c["density_kg_m3"], u, c["size_measured"])
        out(f"{c['id']}: class {c['class']}, reflectivity {c['reflectivity']}, {c['diameter_m']} m, {c['density_kg_m3']} kg/m3, "
            f"size {'measured' if c['size_measured'] else 'from brightness'}\n")
        for s, name in zip(SCEN, m["scenarios"]["order"]):
            r = res[s]
            out(f"   {name:7s}: {r['material']:20s} mass {r['mass_t']:12,.1f} t  metal {r['kg']:10.3f} kg  ${r['usd']:14,.0f}  water {r['water_t']:10.1f} t\n")


def fold_check(m, out, n):
    """The alternatives the checker ran, against what this method exports (H 26.2)."""
    out("\n== The checker's alternatives against this method (H 26.2) ==\n")
    draws = reference_draws(m, 1, n)
    ex = summarise(m, draws, False, "longshot value fold check")
    rng = random.Random("longshot value fold check")
    per = [draw_value(m, c, a, d, rho, tuple(rng.random() for _ in U_NAMES), False) for c, a, d, rho in draws]
    basket = 87945.0  # $ per kg: the 20 November 2026 mix behind the checker's dollar figures
    out("one-sided, zeros counted (the checker's dollars divided by $87,945 per kg):\n")
    out(f"   checker, model as printed: three in four under {2e6 / basket:.0f} kg, nineteen in twenty under {8e6 / basket:.0f} kg\n")
    out(f"   this method:               three in four under {ex['metal']['kg']['q75']:.0f} kg, nineteen in twenty under {ex['metal']['kg']['q95']:.0f} kg\n")
    out("iron-rich bodies of 100:\n")
    out("   report (X 23%, M 32% of X): " + ", ".join(f"{100 * 0.23 * 0.32 * sh:.1f} at a share of {sh}" for sh in (0.10, 0.38, 0.60)) + "\n")
    out(f"   this method: {100 * ex['iron_rich']['p_lo']:.1f} to {100 * ex['iron_rich']['p_hi']:.1f}; "
        f"holding {ex['iron_rich']['kg']['q05']:.1f} to {ex['iron_rich']['kg']['q95']:,.0f} kg "
        f"(report, metal-rich cases alone: {8.8e6 / basket:.0f} to {334e6 / basket:,.0f} kg)\n")
    kg_lo = sorted(p[LOW]["kg"] for p in per if p[LOW]["kg"] > 0)
    kg_hi = sorted(p[HIGH]["kg"] for p in per if p[HIGH]["kg"] > 0)
    mine_kg = (quantile(kg_lo, 0.05), quantile(kg_hi, 0.95))
    mine_w = (ex["water"]["tonnes"]["q05"], ex["water"]["tonnes"]["q95"])
    out("bodies holding some, 5th to 95th percentile. For metal this range is not exported: its top sits where the\n"
        "ordinary and the iron-rich bodies meet, so it moves with the class shares.\n")
    out(f"   this method: metal {mine_kg[0]:.2f} to {mine_kg[1]:,.0f} kg; water {mine_w[0]:.0f} to {mine_w[1]:,.0f} t\n")
    alts = [
        ("as printed in value-inputs.md", (0.36e6, 14.5e6), (331, 11100)),
        ("metal-rich share of M-types 10%", (0.36e6, 8.4e6), None),
        ("metal-rich share 60%", (0.36e6, 35e6), None),
        ("dark reflectivity 0.13", None, (80, 2740)),
        ("the plan's size rule for every class", (0.15e6, 18e6), (16, 1670)),
        ("all nine H chondrites", (0.35e6, 14.3e6), None),
    ]

    def verdict(mine, theirs):
        notes = []
        if mine[0] > theirs[0]:
            notes.append(f"low end {mine[0] / theirs[0]:.2f} x theirs")
        if mine[1] < theirs[1]:
            notes.append(f"top {mine[1] / theirs[1]:.2f} x theirs")
        return "inside" if not notes else "not inside: " + ", ".join(notes)

    for label, usd, water in alts:
        line = f"   {label:38s}"
        if usd:
            theirs = (usd[0] / basket, usd[1] / basket)
            line += f" metal {theirs[0]:6.1f} to {theirs[1]:6.0f} kg: {verdict(mine_kg, theirs)}"
        if water:
            line += f" | water {water[0]:5.0f} to {water[1]:6,.0f} t: {verdict(mine_w, water)}"
        out(line + "\n")


def floor_check(m, out, n):
    """The narrowest range a telescope can give: class S and a size good to 10%."""
    out("\n== The narrowest range from Earth: S-type, 15 m measured to 10% ==\n")
    rng = random.Random("longshot value floor")
    draws = []
    for _ in range(n):
        d = 15.0 * math.exp(0.10 * _normal_inverse(rng.random()))
        draws.append(("S", 0.25, d, 1700.0 + 1700.0 * rng.random()))
    e = summarise(m, draws, True, "longshot value floor")["metal"]
    out(f"kg q05 {e['kg']['q05']:.1f} to q95 {e['kg']['q95']:.1f}: a factor of {e['kg']['q95'] / e['kg']['q05']:.1f}\n")
    out(f"usd q05 {e['usd']['q05']:,.0f} to q95 {e['usd']['q95']:,.0f}: a factor of {e['usd']['q95'] / e['usd']['q05']:.1f}\n")


def _t(v):
    """A TOML value."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_t(x)}" for k, x in v.items()) + " }"
    return repr(round(v, 6)) if isinstance(v, float) else repr(v)


def emit_toml(m, out, n):
    """Sections 10 and 11 of value.toml."""
    out("# ---------------------------------------------------------------------------\n")
    out("# 10. Single-draw checks (exact; value.py must reproduce every line)\n")
    out("# ---------------------------------------------------------------------------\n")
    out("# Printed by tools/value_examples.py --toml. expect is [low, central, high].\n")
    for c in m["check"]:
        u = tuple(c["u"][k] for k in U_NAMES)
        res = draw_value(m, c["class"], c["reflectivity"], c["diameter_m"], c["density_kg_m3"], u, c["size_measured"])
        out("\n[[check]]\n")
        for k in ("id", "class", "reflectivity", "diameter_m", "density_kg_m3", "size_measured"):
            out(f"{k} = {_t(c[k])}\n")
        out("u = { " + ", ".join(f"{k} = {c['u'][k]!r}" for k in U_NAMES) + " }\n")
        out("expect = [\n")
        for r in res:
            out("  " + _t({k: r[k] for k in ("material", "mass_t", "kg", "usd", "water_t")}) + ",\n")
        out("]\n")
    out("\n# ---------------------------------------------------------------------------\n")
    out("# 11. Worked examples (reference draw; value.py fed the same draws must agree)\n")
    out("# ---------------------------------------------------------------------------\n")
    out(f"# Printed by tools/value_examples.py --toml at {n:,} draws. Draws: reference_draws(method, id, n).\n")
    out("# Agreement at 20,000 draws: counts of 100 within 1, every other figure within 15%. At 2,000 draws the tail figures move by up to 30%.\n")
    out("# The iron-rich range of example 2 rests on its mislabelled draws alone, about 1 in 80, and moves by up to 35% at 20,000 draws.\n")
    out("# tools/method_check.py recomputes every figure below from this file alone, with no code shared with that script.\n")
    for ex_id in sorted(EXAMPLES):
        ex = EXAMPLES[ex_id]
        _, e, st = run_example(m, ex_id, n)
        out("\n[[example]]\n")
        out(f"id = {ex_id}\ntitle = {_t(ex['title'])}\nsize_measured = {_t(ex['size_measured'])}\ndraws = {n}\n")
        # what the reference draw was given, so the example can be recomputed from this file alone
        out("inputs = " + _t({k: ex[k] for k in ("h", "class", "class_label", "label_error", "d_m", "d_sigma_ln", "weights") if k in ex}) + "\n")
        out("statements = [\n" + "".join(f"  {_t(s)},\n" for s in st) + "]\n")
        for part in ("metal", "iron_rich", "water"):
            out(f"[example.{part}]\n")
            for k, v in e[part].items():
                out(f"{k} = {_t(v)}\n")


def main(argv):
    m = load_method()
    out = sys.stdout.write
    if "--toml" in argv:
        emit_toml(m, out, 200000)
        return
    if "--write" in argv:
        marker = "# ---------------------------------------------------------------------------\n# 10. Single-draw checks"
        with open(METHOD_PATH) as f:
            text = f.read()
        if text.count(marker) != 1:
            sys.exit("value.toml: the heading of section 10 was not found exactly once")
        parts = []
        emit_toml(m, parts.append, 200000)
        with open(METHOD_PATH, "w") as f:
            f.write(text[:text.index(marker)] + "".join(parts))
        out(f"wrote sections 10 and 11 of {os.path.relpath(METHOD_PATH, ROOT)}\n")
        return
    n = int(argv[1]) if len(argv) > 1 else 200000
    out(f"method {m['meta']['method']}, {n:,} draws per example\n")
    hand_arithmetic(m, out)
    for ex_id in sorted(EXAMPLES):
        ex = EXAMPLES[ex_id]
        draws, e, st = run_example(m, ex_id, n)
        out(f"\n== Example {ex_id}: {ex['title']} ==\n")
        ds = [d[2] for d in draws]
        ms = [sphere_mass_t(d[2], d[3]) for d in draws]
        cls = {}
        for d in draws:
            cls[d[0]] = cls.get(d[0], 0) + 1
        out("draw: class shares " + ", ".join(f"{k} {v/len(draws):.3f}" for k, v in sorted(cls.items())) + "\n")
        out(f"draw: diameter q05 {_q(ds, .05):.1f} m, q25 {_q(ds, .25):.1f}, q75 {_q(ds, .75):.1f}, q95 {_q(ds, .95):.1f}; "
            f"mass q05 {_q(ms, .05):,.0f} t, q95 {_q(ms, .95):,.0f} t\n")
        me, ir, wa = e["metal"], e["iron_rich"], e["water"]
        out(f"metal: p_nothing {me['p_nothing']:.3f} (lo {me['p_nothing_lo']:.3f}, hi {me['p_nothing_hi']:.3f}); capped {me['capped']}\n")
        out("   kg  " + ", ".join(f"{k} {v:,.2f}" for k, v in me["kg"].items()) + "\n")
        out("   usd " + ", ".join(f"{k} {v:,.0f}" for k, v in me["usd"].items()) + "\n")
        out(f"iron-rich: p_lo {ir['p_lo']:.4f}, p_hi {ir['p_hi']:.4f}")
        if "kg" in ir:
            out(f"; kg q05 {ir['kg']['q05']:,.1f}, q95 {ir['kg']['q95']:,.0f}; usd q05 {ir['usd']['q05']:,.0f}, q95 {ir['usd']['q95']:,.0f}")
        out("\n")
        out(f"water: p_nothing {wa['p_nothing']:.3f} (lo {wa['p_nothing_lo']:.3f}, hi {wa['p_nothing_hi']:.3f})")
        if "tonnes" in wa:
            out(f"; tonnes q05 {wa['tonnes']['q05']:,.1f}, q95 {wa['tonnes']['q95']:,.0f}")
        out("\nstatements:\n")
        for s in st:
            out(f"   {s}\n")
    fold_check(m, out, n)
    floor_check(m, out, n)


if __name__ == "__main__":
    main(sys.argv)
