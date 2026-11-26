"""What is in the rock, as ranges, the chance of nothing first: method/v0_1/value.toml.

    records = value.apply(records)        # stage 5: fills record.value

    record.value = {
      metal:     {p_nothing, p_nothing_lo, p_nothing_hi, kg{q05,q25,q75,q95}, usd{q05,q25,q75,q95}, capped},
      iron_rich: {p_lo, p_hi, kg{q05,q95}, usd{q05,q95}},     kg and usd only with 20 or more draws to rest on
      water:     {p_nothing, p_nothing_lo, p_nothing_hi, tonnes{q05,q95}},   tonnes likewise
      basis, statements[], statement_ids[],
      table: { metal: {cells[], rows[]}, water: {cells[], rows[]}, notes[] } }   not where a sample stands in
    record.value = {} for an object with no H.

table is the price tag as the entry lays it out (value.toml [table]): 100 cells
whose counts add to 100, the chance of nothing first, and rows of the same
figures the statements print.

A lower bound is computed in the method's "low" scenario and an upper bound in
"high". No mean, median or middle quantile of kilograms, dollars or tonnes is
computed here or written anywhere.

tools/value_examples.py is the reference: `summarise` here, fed the same draws
and the same seed, returns the same figures (tests/test_value.py).
"""
from __future__ import annotations

import functools
import math
import random

from longshot import draws as draws_mod
from longshot import method as method_mod
from longshot.method import Method
from longshot.priors import quantile, sig
from longshot.types import ObjectRecord

LOW, CENTRAL, HIGH = 0, 1, 2
SCENARIOS = (LOW, CENTRAL, HIGH)
U_NAMES = ("u_kind", "u_grade", "u_metal", "u_rho", "u_hyd", "u_water")
CLASS_LABELS = {"S": "S/Q", "C": "C", "X": "X", "other": "other"}       # value.toml statement slot class_label
PI6 = math.pi / 6.0


# --------------------------------------------------------------------------
# the procedure of value.toml section 1

class _Material:
    __slots__ = ("id", "counted", "density", "grade", "table", "fraction", "mixes", "caps", "prices", "water")

    def __init__(self, v: dict, mid: str):
        mat = v["material"][mid]
        self.id = mid
        self.counted = bool(mat["counted"])
        d = mat.get("density_kg_m3")
        self.density = (d["lo"], d["hi"] - d["lo"]) if d else None
        g = mat.get("grade_ppm")
        self.grade = (g["lo"], g["hi"] - g["lo"]) if g else None
        self.table = None
        self.fraction = None
        if "grade_table" in mat:
            self.table = [(q, math.log(ppm)) for q, ppm in v["grade_table"][mat["grade_table"]]]
            f = mat["metal_fraction"]
            self.fraction = (f["lo"], f["hi"] - f["lo"])
        w = mat.get("water_fraction")
        self.water = (w["lo"], w["hi"] - w["lo"]) if w else None
        priced = v["counted"]["priced"]
        self.mixes = None
        if self.counted:
            mix = mat["mix"]
            ids = mix if isinstance(mix, list) else [mix] * 3
            # per scenario: (share of the element in the total, cap in kg, dollars per kg) for each priced metal
            self.mixes = [[(v["mix"][ids[s]][el], v["market"]["cap_kg"][el], v["prices"]["usd_per_kg"][el][s])
                           for el in priced] for s in SCENARIOS]


class _Compiled:
    def __init__(self, v: dict):
        self.v = v
        self.dark = v["bands"]["dark_below"]
        self.bright = v["bands"]["bright_from"]
        self.factor = list(v["size"]["diameter_factor"])
        self.materials = {mid: _Material(v, mid) for mid in v["material"]}
        self.iron = self.materials["iron_rich"]
        self.min_range = v["exports"]["min_draws_for_a_range"]
        self.basis = v["exports"]["basis"]["text"]
        # rows[(class, band)][scenario] = [(cumulative share, material, hydrated share or None)]
        self.rows = {}
        for cls, k in v["kinds"].items():
            for band in ("dark", "mid", "bright"):
                listed = k["any"] if "any" in k else k[band]
                per = []
                for s in SCENARIOS:
                    acc, out = 0.0, []
                    for row in listed:
                        acc += row["share"][s]
                        out.append((acc, self.materials[row["material"]],
                                    row["hydrated"][s] if "hydrated" in row else None))
                    per.append(out)
                self.rows[(cls, band)] = per

    def band(self, reflectivity: float) -> str:
        if reflectivity < self.dark:
            return "dark"
        if reflectivity >= self.bright:
            return "bright"
        return "mid"


@functools.lru_cache(maxsize=4)
def _compiled_for(m: Method) -> _Compiled:
    return _Compiled(m.value)


def _compile(m) -> _Compiled:
    """m is a Method, or value.toml as a dict (the form tools/value_examples.py uses)."""
    if isinstance(m, Method):
        return _compiled_for(m)
    return _Compiled(m)


def _pick(rows, u_kind: float):
    """First row whose cumulative share exceeds u_kind."""
    for row in rows:
        if u_kind < row[0]:
            return row
    return rows[-1]


def _table(points, u: float) -> float:
    """Log-linear interpolation of [(q, ln value)] at u."""
    for (q0, v0), (q1, v1) in zip(points, points[1:]):
        if u <= q1:
            return math.exp(v0 + (u - q0) / (q1 - q0) * (v1 - v0))
    return math.exp(points[-1][1])


def _figures(mat: _Material, s: int, diameter_m: float, density: float, u):
    """(mass_t, kg of the six metals, dollars with the cap, dollars without it) for one material in scenario s."""
    if mat.density is not None:
        density = mat.density[0] + mat.density[1] * u[3]
    mass = PI6 * diameter_m ** 3 * density / 1000.0
    if not mat.counted:
        return mass, 0.0, 0.0, 0.0
    if mat.table is not None:
        ppm = _table(mat.table, u[1]) * (mat.fraction[0] + mat.fraction[1] * u[2])
    else:
        ppm = mat.grade[0] + mat.grade[1] * u[1]
    kg = mass * ppm / 1000.0
    usd = free = 0.0
    for share, cap, price in mat.mixes[s]:
        el = kg * share
        usd += (el if el < cap else cap) * price
        free += el * price
    return mass, kg, usd, free


def draw_value(m, cls: str, reflectivity: float, diameter_m: float, density: float, u, size_measured: bool) -> list:
    """Figures for one draw in each scenario: [low, central, high].

    Each is {material, mass_t, kg, usd, usd_uncapped, water_t}. A class X draw in the mid band also carries
    iron_kg, iron_usd and iron_usd_uncapped: what it would hold if iron-rich.
    """
    c = _compile(m)
    band = c.band(reflectivity)
    rows = c.rows[(cls, band)]
    out = []
    for s in SCENARIOS:
        d = diameter_m if size_measured else diameter_m * c.factor[s]
        _, mat, hydrated = _pick(rows[s], u[0])
        mass, kg, usd, free = _figures(mat, s, d, density, u)
        water = 0.0
        if hydrated is not None and u[4] < hydrated:
            water = mass * (mat.water[0] + mat.water[1] * u[5])
        rec = {"material": mat.id, "mass_t": mass, "kg": kg, "usd": usd, "usd_uncapped": free, "water_t": water}
        if cls == "X" and band == "mid":
            _, ikg, iusd, ifree = _figures(c.iron, s, d, density, u)
            rec["iron_kg"], rec["iron_usd"], rec["iron_usd_uncapped"] = ikg, iusd, ifree
        out.append(rec)
    return out


def summarise(m, draws, size_measured: bool, seed) -> dict:
    """The exports of value.toml section 7 for one object's draws.

    draws: (class, reflectivity, diameter_m, density_kg_m3) per draw. seed: for the six uniform numbers each draw
    takes, in U_NAMES order. Returns {metal, iron_rich, water, basis}, unrounded.
    """
    c = _compile(m)
    rng = random.Random(seed)
    rnd = rng.random
    f_lo, f_hi = (1.0, 1.0) if size_measured else (c.factor[LOW], c.factor[HIGH])
    iron = c.iron
    dark, bright, all_rows = c.dark, c.bright, c.rows

    kg_lo, kg_hi, usd_lo, usd_hi, free_hi = [], [], [], [], []
    water_lo, water_hi = [], []
    iron_kg_lo, iron_kg_hi, iron_usd_lo, iron_usd_hi, iron_free_hi = [], [], [], [], []
    n = none_lo = none_mid = none_hi = dry_lo = dry_mid = dry_hi = n_iron_lo = n_iron_hi = 0
    for cls, refl, d, rho in draws:
        n += 1
        u = (rnd(), rnd(), rnd(), rnd(), rnd(), rnd())
        band = "dark" if refl < dark else "bright" if refl >= bright else "mid"
        rows = all_rows[(cls, band)]
        u_kind = u[0]

        # low: every lower bound
        d_lo = d * f_lo
        _, mat, hydrated = _pick(rows[LOW], u_kind)
        mass, kg, usd, _ = _figures(mat, LOW, d_lo, rho, u)
        kg_lo.append(kg)
        usd_lo.append(usd)
        if kg == 0.0:
            none_lo += 1
        if mat is iron:
            n_iron_lo += 1
        if hydrated is not None and u[4] < hydrated:
            water_lo.append(mass * (mat.water[0] + mat.water[1] * u[5]))
        else:
            dry_lo += 1

        # central: only the chance of nothing
        _, mat, hydrated = _pick(rows[CENTRAL], u_kind)
        if not mat.counted:
            none_mid += 1
        if not (hydrated is not None and u[4] < hydrated):
            dry_mid += 1

        # high: every upper bound
        d_hi = d * f_hi
        _, mat, hydrated = _pick(rows[HIGH], u_kind)
        mass, kg, usd, free = _figures(mat, HIGH, d_hi, rho, u)
        kg_hi.append(kg)
        usd_hi.append(usd)
        free_hi.append(free)
        if kg == 0.0:
            none_hi += 1
        if mat is iron:
            n_iron_hi += 1
        if hydrated is not None and u[4] < hydrated:
            water_hi.append(mass * (mat.water[0] + mat.water[1] * u[5]))
        else:
            dry_hi += 1

        if band == "mid" and cls == "X":        # what it would hold if iron-rich, whatever it drew
            _, ikg, iusd, _ = _figures(iron, LOW, d_lo, rho, u)
            iron_kg_lo.append(ikg)
            iron_usd_lo.append(iusd)
            _, ikg, iusd, ifree = _figures(iron, HIGH, d_hi, rho, u)
            iron_kg_hi.append(ikg)
            iron_usd_hi.append(iusd)
            iron_free_hi.append(ifree)
    if n == 0:
        raise ValueError("no draws")

    for col in (kg_lo, kg_hi, usd_lo, usd_hi, free_hi, water_lo, water_hi,
                iron_kg_lo, iron_kg_hi, iron_usd_lo, iron_usd_hi, iron_free_hi):
        col.sort()
    metal = {
        "p_nothing": none_mid / n, "p_nothing_lo": none_hi / n, "p_nothing_hi": none_lo / n,
        "kg": {"q05": quantile(kg_lo, 0.05), "q25": quantile(kg_lo, 0.25),
               "q75": quantile(kg_hi, 0.75), "q95": quantile(kg_hi, 0.95)},
        "usd": {"q05": quantile(usd_lo, 0.05), "q25": quantile(usd_lo, 0.25),
                "q75": quantile(usd_hi, 0.75), "q95": quantile(usd_hi, 0.95)},
    }
    capped = quantile(free_hi, 0.95) > metal["usd"]["q95"] * 1.05
    iron_out = {"p_lo": n_iron_lo / n, "p_hi": n_iron_hi / n}
    if len(iron_kg_lo) >= c.min_range:
        iron_out["kg"] = {"q05": quantile(iron_kg_lo, 0.05), "q95": quantile(iron_kg_hi, 0.95)}
        iron_out["usd"] = {"q05": quantile(iron_usd_lo, 0.05), "q95": quantile(iron_usd_hi, 0.95)}
        capped = capped or quantile(iron_free_hi, 0.95) > iron_out["usd"]["q95"] * 1.05
    metal["capped"] = capped
    water = {"p_nothing": dry_mid / n, "p_nothing_lo": dry_hi / n, "p_nothing_hi": dry_lo / n}
    if len(water_lo) >= c.min_range and len(water_hi) >= c.min_range:
        water["tonnes"] = {"q05": quantile(water_lo, 0.05), "q95": quantile(water_hi, 0.95)}
    return {"metal": metal, "iron_rich": iron_out, "water": water, "basis": c.basis}


# --------------------------------------------------------------------------
# formatting (value.toml [format]) and statements (section 8)

def round_figure(x: float, up: bool) -> float:
    """One significant figure, two when the first digit is 1 or 2. Up for an 'under' figure, down for an 'over'."""
    if x <= 0:
        return 0.0
    e = math.floor(math.log10(x))
    lead = int(x / 10 ** e + 1e-12)
    unit = 10.0 ** (e - (1 if lead < 3 else 0))
    r = x / unit
    r = math.ceil(r - 1e-9) if up else math.floor(r + 1e-9)
    return r * unit


def _num(x: float) -> str:
    if x >= 100:
        return f"{x:,.0f}"
    return f"{x:.2f}".rstrip("0").rstrip(".")


_USD_SCALES = ((1e9, " billion"), (1e6, " million"), (1e3, " thousand"))


def fmt_usd(x: float, up: bool) -> str:
    v = round_figure(x, up)
    for size, word in _USD_SCALES:
        if v >= size:
            return f"${_num(v / size)}{word}"
    return f"${_num(v)}"


def _usd_scale(v: float) -> float:
    return next((size for size, _ in _USD_SCALES if v >= size), 1.0)


def fmt_usd_range(lo: float, hi: float) -> str:
    """'$A to $B', low end rounded down and high end up.

    When the low end is under a thousand dollars, so carries no scale word, and the high end carries one, both
    print in figures ('$40 to $160,000'): '$40 to $160 thousand' reads as forty thousand.
    """
    a, b = round_figure(lo, False), round_figure(hi, True)
    if _usd_scale(a) == 1.0 and _usd_scale(b) != 1.0:
        return f"${a:,.0f} to ${b:,.0f}"
    return f"{fmt_usd(lo, False)} to {fmt_usd(hi, True)}"


def fmt_tonnes(x: float, up: bool, short: bool = False) -> str:
    """'N tonnes'; short, for a table cell: 'N t'."""
    v = round_figure(x, up)
    if v < 1.0:
        return f"{_num(v * 1000.0)} kg"
    if v >= 1e6:
        return f"{_num(v / 1e6)} million {'t' if short else 'tonnes'}"
    if short:
        return f"{_num(v)} t"
    return f"{_num(v)} tonne" if v == 1.0 else f"{_num(v)} tonnes"


def fmt_kg(x: float, up: bool, short: bool = False) -> str:
    v = round_figure(x, up)
    if v < 1.0:
        return f"{_num(v * 1000.0)} g"
    if v >= 1000.0:
        return fmt_tonnes(x / 1000.0, up, short)
    return f"{_num(v)} kg"


def fmt_range(lo: str, hi: str) -> str:
    """'A to B'; a unit word shared by both prints once ('20 to 10,000 tonnes', '1 to 30 tonnes').

    Not for dollars: fmt_usd_range.
    """
    a, b = lo.rsplit(" ", 1), hi.rsplit(" ", 1)
    if len(a) == 2 and len(b) == 2 and a[1].removesuffix("s") == b[1].removesuffix("s") and not lo.startswith("$"):
        return f"{a[0]} to {hi}"
    return f"{lo} to {hi}"


def fmt_count(p_lo: float, p_hi: float) -> str:
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


def cell_count(p_lo: float, p_hi: float) -> str:
    """fmt_count as a table cell prints it (docs/design.md section 6): an en dash for a band, symbols at the ends.
    The same rounding: '37–43', '40', '≤4', '≥99', '<1', '>99'."""
    said = fmt_count(p_lo, p_hi)
    for words, sign in (("fewer than ", "<"), ("more than ", ">"), ("about ", ""), ("up to ", "≤")):
        if said.startswith(words):
            return sign + said.removeprefix(words)
    if said.endswith(" or more"):
        return "≥" + said.removesuffix(" or more")
    return said.replace(" to ", "–")


def cell_range(lo: str, hi: str) -> str:
    """fmt_range as a table cell prints it: '160–110,000 t' when both ends share a unit, else 'A to B'."""
    said = fmt_range(lo, hi)
    a = lo.rsplit(" ", 1)
    if said == f"{a[0]} to {hi}" and len(a) == 2:
        return f"{a[0]}–{hi}"
    return said


def statement_pairs(m, ex: dict, size_measured: bool, class_label: str | None = None) -> list[tuple[str, str]]:
    """(id, sentence) for each statement of value.toml section 8 that applies, in order."""
    v = m.value if isinstance(m, Method) else m
    st = {s["id"]: s for s in v["statement"]}
    metal, iron, water = ex["metal"], ex["iron_rich"], ex["water"]
    out = []
    # One answer is left only when the class is not in doubt: a label's chance of being wrong is in the draws
    # (priors.toml [class.label_error]), so a labelled class leaves a chance of nothing and prints it first.
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
                                     kg05=fmt_kg(kg["q05"], False), usd05=fmt_usd(usd["q05"], False),
                                     size_clause=clause)
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


def statements(m, ex: dict, size_measured: bool, class_label: str | None = None) -> list[str]:
    return [text for _, text in statement_pairs(m, ex, size_measured, class_label)]


# --------------------------------------------------------------------------
# the entry's two price tables (value.toml [table])

def count100(p: float) -> int:
    """A share as a whole number of 100, halves rounded up ([format].count)."""
    return max(0, min(100, math.floor(100 * p + 0.5)))


def _cells(words: dict, spec: list[tuple[str, int]]) -> list[dict]:
    return [{"id": cid, "label": words[cid], "n": n} for cid, n in spec if n > 0]


def per100(ex: dict) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """(metal cells, water cells) as (id, count) adding to 100, the chance of nothing first.

    Each end of a band is counted with [format].count: 'none' is the scenario with fewest holding nothing,
    'none_or_some' the rest of the low scenario's nothing, and for metal 'iron_rich' and 'iron_rich_or_not'
    likewise at the other end. 'some' is what is left. Where two rounded bands would overlap, the uncertain
    cells give way first, so the counts always add to 100.
    """
    metal, iron, water = ex["metal"], ex["iron_rich"], ex["water"]
    a, b = sorted((count100(metal["p_nothing_lo"]), count100(metal["p_nothing_hi"])))
    c, d = sorted((count100(iron["p_lo"]), count100(iron["p_hi"])))
    c, d = min(c, 100 - b), min(d, 100 - b)                 # an iron-rich cell is one that holds some
    metal_cells = [("none", a), ("none_or_some", b - a), ("some", 100 - b - d),
                   ("iron_rich_or_not", d - c), ("iron_rich", c)]
    w_a, w_b = sorted((count100(water["p_nothing_lo"]), count100(water["p_nothing_hi"])))
    water_cells = [("none", w_a), ("none_or_some", w_b - w_a), ("some", 100 - w_b)]
    return metal_cells, water_cells


def _row(rid: str, label: str, of100=None, kg=None, usd=None, kg_n=None) -> dict:
    """One row of the metal table. kg and usd are the figures as the statements print them; kg_n is the same
    amount as numbers, [low, high] in kg, rounded the same way, so the page can print a column in one unit."""
    return {"id": rid, "label": label, "of100": of100, "kg": kg, "usd": usd, "kg_n": kg_n}


# How many of 100 hold under (or over) a row's figure: the quantile it is (value.toml [table.metal]).
_OF100 = {"over_q05": "95", "over_q25": "75", "under_q75": "75", "under_q95": "95"}


def table(m, ex: dict, pairs: list[tuple[str, str]], size_measured: bool) -> dict:
    """The price tag as the entry lays it out: for metal and water, the 100 cells and the rows beside them, then
    the notes the rows do not say. Every figure is the statements' own, formatted the same way, with 't' for
    tonnes. No middle figure: the rows are the quartiles and the 5th and 95th, as in the statements."""
    v = m.value if isinstance(m, Method) else m
    words = v["table"]
    said = dict(pairs)
    metal, iron, water = ex["metal"], ex["iron_rich"], ex["water"]
    kg, usd = metal["kg"], metal["usd"]
    rows = [_row("none", words["metal"]["none"], of100=cell_count(metal["p_nothing_lo"], metal["p_nothing_hi"]))]
    for q, rid, up in (("q05", "over_q05", False), ("q25", "over_q25", False),
                       ("q75", "under_q75", True), ("q95", "under_q95", True)):
        if usd[q] > 0:
            rows.append(_row(rid, words["metal"][rid], of100=_OF100[rid], kg=fmt_kg(kg[q], up, short=True),
                             usd=fmt_usd(usd[q], up), kg_n=[round_figure(kg[q], up)] * 2))
    iron_row = _row("iron_rich", words["metal"]["iron_rich"], of100=cell_count(iron["p_lo"], iron["p_hi"]))
    if "iron_rich" in said:                                  # the same test as the statement's
        iron_row["kg"] = cell_range(fmt_kg(iron["kg"]["q05"], False, short=True), fmt_kg(iron["kg"]["q95"], True, short=True))
        iron_row["kg_n"] = [round_figure(iron["kg"]["q05"], False), round_figure(iron["kg"]["q95"], True)]
        iron_row["usd"] = fmt_usd_range(iron["usd"]["q05"], iron["usd"]["q95"])
    rows.append(iron_row)

    notes = [words["notes"]["of100"]]
    if "metal_none_measured" in said:
        notes.append(said["metal_none_measured"])
    if iron_row["kg"]:
        notes.append(words["notes"]["iron_rich"])
    if any(r["kg"] for r in rows):
        notes.append(words["notes"]["prices"])
    if not size_measured and any(r["id"].startswith("over_") for r in rows):
        notes.append(words["notes"]["size"])
    if "metal_cap" in said:
        notes.append(said["metal_cap"])

    all_dry = min(water["p_nothing_lo"], water["p_nothing_hi"]) >= 1.0
    water_rows = [{"id": "none", "label": words["water"]["none"], "tonnes": None,
                   "of100": words["water"]["all"] if all_dry else cell_count(water["p_nothing_lo"], water["p_nothing_hi"])}]
    if "water_some" in said:
        water_rows.append({"id": "some", "label": words["water"]["some"], "of100": None, "tonnes": cell_range(
            fmt_tonnes(water["tonnes"]["q05"], False, short=True), fmt_tonnes(water["tonnes"]["q95"], True, short=True)),
            "tonnes_n": [round_figure(water["tonnes"]["q05"], False), round_figure(water["tonnes"]["q95"], True)]})
    if "water_none" in said and not said["water_none"].startswith("Of 100"):
        notes.append(said["water_none"])                     # 'counted as holding no water': a reason, not a count
    notes.append(said["water_market"])

    metal_cells, water_cells = per100(ex)
    return {"metal": {"cells": _cells(words["cells"], metal_cells), "rows": rows},
            "water": {"cells": _cells(words["cells"], water_cells), "rows": water_rows},
            "notes": notes}


# --------------------------------------------------------------------------
# the stage

def _rounded(x, figures: int = 6):
    if isinstance(x, dict):
        return {k: _rounded(v, figures) for k, v in x.items()}
    if isinstance(x, bool) or not isinstance(x, float):
        return x
    return sig(x, figures)


def sample_statements(m: Method, sample: dict, d) -> tuple[list[tuple[str, str]], dict]:
    """(statements, value.sample) for an asteroid a spacecraft brought a sample back from.

    The class-based sentences give way to the sample: what it would mean for the whole body if the body matches
    it, from the mass range of the draws. The ladder's fourth rung prints the analysis itself.
    """
    st = {s["id"]: s for s in m.value["statement"]}
    mass = sorted(d.mass)
    m_lo, m_hi = quantile(mass, 0.05), quantile(mass, 0.95)
    info = {"mission": sample["mission"], "fact": sample["id"]}
    if "water_wt_pct" in sample:
        w = sample["water_wt_pct"]
        lo, hi = m_lo * w["lo"] / 100.0, m_hi * w["hi"] / 100.0
        info["water_t"] = {"q05": sig(lo, 6), "q95": sig(hi, 6)}
        text = st["sample_water"]["template"].format(t_range=fmt_range(fmt_tonnes(lo, False, short=True), fmt_tonnes(hi, True, short=True)))
        return [("sample_water", text), ("water_market", st["water_market"]["template"])], info
    if "water_wt_pct_at_most" in sample:
        top = m_hi * sample["water_wt_pct_at_most"] / 100.0
        info["water_t_at_most"] = sig(top, 6)
        text = st["sample_water_at_most"]["template"].format(t_max=fmt_tonnes(top, True, short=True))
        return [("sample_water_at_most", text), ("water_market", st["water_market"]["template"])], info
    return [("sample_no_analysis", st["sample_no_analysis"]["template"])], info


def block(key: str, d, m: Method, sample: dict | None = None) -> dict:
    """record.value for one object's draws; {} when it has none.

    sample: the ladder.toml sample_return fact whose target this asteroid is, if any.
    """
    if d is None or d.n == 0:
        return {}
    inp = d.inputs
    size_measured = inp.size_measured
    # seeded as the draws were: by brightness alone when nothing else is known, so equal inputs print equal figures
    ex = summarise(m, d.joint(), size_measured, draws_mod.seed(d.seed_key or key, m, "value"))
    out = {"metal": ex["metal"], "iron_rich": ex["iron_rich"], "water": ex["water"]}
    for part in ("metal", "iron_rich", "water"):
        for k, v in list(out[part].items()):
            if k.startswith("p_"):
                out[part][k] = round(v, 4)
            else:
                out[part][k] = _rounded(v)
    out["basis"] = ex["basis"]
    if sample is not None:
        pairs, out["sample"] = sample_statements(m, sample, d)
    else:
        pairs = statement_pairs(m, ex, size_measured, CLASS_LABELS[inp.cls] if inp.cls is not None else None)
    out["statements"] = [text for _, text in pairs]
    out["statement_ids"] = [sid for sid, _ in pairs]
    # Where a sample stands in for the class odds, the statements are the price tag: there is no table.
    if sample is None:
        out["table"] = table(m, ex, pairs, size_measured)
    return out


def _sample_fact(record: ObjectRecord, m: Method) -> dict | None:
    names = draws_mod._names(record)
    return next((f for f in m.ladder["fact"] if f.get("kind") == "sample_return"
                 and names & set(f.get("objects", []))), None)


def apply_one(record: ObjectRecord, d, m: Method) -> ObjectRecord:
    # A body that no longer exists holds nothing to estimate (ledger.toml [[gone]]).
    record.value = {} if record.gone else block(record.key, d, m, _sample_fact(record, m))
    return record


def apply(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Stage 5: what is in it, as ranges."""
    m = m or method_mod.load()
    for r in records:
        apply_one(r, draws_mod.for_record(r, m), m)
    return records
