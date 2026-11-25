"""Size, spin, class and density from brightness: the tables of method/v0_1/priors.toml, ready to draw from.

The joint draw (longshot/draws.py) is stratified: each of its random inputs
takes the same n values, the midpoints of n equal slices of (0, 1), and an
object's seed only decides how they are paired. So everything that depends on
one input alone is computed once here and shared by every object, which is
exact: the normal deviates for H, the reflectivity at each slice of the Spitzer
table (and of each class table), the class weights in each reflectivity bin of
each brightness band, and the spin category at each slice in each band.

`fill(record, d, m)` writes what the draws amount to into the record: the prior
of each row nobody has measured, and record.summary.
"""
from __future__ import annotations

import functools
import math
from statistics import NormalDist

from longshot.method import Method
from longshot.types import ObjectRecord

CLASSES = ("S", "C", "X", "other")
SPIN_KEYS = ("p_fast_2_2h", "p_under_1h", "p_under_10min")     # record.summary names, in priors.toml [spin].ids order
QUANTILES = (("q05", 0.05), ("q25", 0.25), ("q50", 0.50), ("q75", 0.75), ("q95", 0.95))

BAND_WORDS = {"under_20": "under 20", "20_22": "20 to 22", "22_24": "22 to 24", "24_26": "24 to 26",
              "26_28": "26 to 28", "28_up": "28 and fainter"}


# --------------------------------------------------------------------------
# small numeric helpers, shared by the other stages

def sig(x: float, figures: int = 4) -> float:
    """x to a number of significant figures, so the files hold no digits the draws cannot support."""
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, figures - 1 - math.floor(math.log10(abs(x))))


def quantile(sorted_values, q: float):
    """Nearest rank (value.toml [exports].quantile_rule): the value at index ceil(q x n) - 1."""
    n = len(sorted_values)
    return sorted_values[min(n - 1, max(0, math.ceil(q * n) - 1))]


def quantiles(values, figures: int = 4) -> dict:
    v = sorted(values)
    return {name: sig(quantile(v, q), figures) for name, q in QUANTILES}


def share(count: int, n: int) -> float:
    return round(count / n, 4)


# --------------------------------------------------------------------------
# the tables

def band_of(m: Method, h: float | None) -> str | None:
    """The id of the brightness band holding h: band i holds edges[i-1] <= H < edges[i]."""
    if h is None:
        return None
    ids, edges = m.priors["bands"]["ids"], m.priors["bands"]["edges"]
    return ids[sum(1 for e in edges if h >= e)]


def inverse_table(p, x, u: float) -> float:
    """Inverse transform through a quantile table: u clamped to the table, log10(x) linear in p."""
    u = min(max(u, p[0]), p[-1])
    for i in range(1, len(p)):
        if u <= p[i]:
            f = (u - p[i - 1]) / (p[i] - p[i - 1])
            return 10 ** (math.log10(x[i - 1]) + f * (math.log10(x[i]) - math.log10(x[i - 1])))
    return x[-1]


def pv_bin(edges, pv: float) -> int:
    """Reflectivity bin of priors.toml [reflectivity.link]: bin i holds edges[i-1] <= pv < edges[i]."""
    return sum(1 for e in edges if pv >= e)


def size_m(m: Method, h: float, pv: float) -> float:
    return m.priors["size"]["coefficient_m"] * 10 ** (-h / 5.0) / math.sqrt(pv)


def implied_reflectivity(m: Method, h: float, d_m: float) -> float:
    return (m.priors["size"]["coefficient_m"] * 10 ** (-h / 5.0) / d_m) ** 2


def mass_t(d_m: float, density: float) -> float:
    return math.pi / 6.0 * d_m ** 3 * density / 1000.0


def density_ends(m: Method) -> tuple[float, float]:
    """The lightest and densest material in priors.toml [density] (missions.toml [rules.mass])."""
    d = m.priors["density"]
    parts = [d[c] for c in CLASSES if c != "X"] + [d["X"][k] for k in ("dark", "mid_silicate", "mid_metal", "bright")]
    return min(p["lo"] for p in parts), max(p["hi"] for p in parts)


class Tables:
    """Everything the joint draw needs that does not depend on the object."""

    def __init__(self, m: Method):
        pri = m.priors
        n = self.n = m.n_draws
        self.u = [(k + 0.5) / n for k in range(n)]
        nd = NormalDist()
        self.z = [nd.inv_cdf(u) for u in self.u]
        self.coef = pri["size"]["coefficient_m"]
        self.default_sigma = pri["h_uncertainty"]["default_sigma"]
        refl = pri["reflectivity"]
        self.edges = list(refl["link"]["edges"])
        self.pv_all = [inverse_table(refl["p"], refl["pv"], u) for u in self.u]
        self.pv_class = {c: [inverse_table(refl["p"], refl["by_class"][c]["pv"], u) for u in self.u] for c in CLASSES}
        self.thresholds_h = list(pri["spin"]["thresholds_h"])

        self.class_cum: dict[str, list[tuple[float, float, float]]] = {}
        # for a mislabelled draw (draws._other_side): the raw weights per reflectivity bin, and the band's shares
        self.class_raw: dict[str, list[dict[str, float]]] = {}
        self.class_central: dict[str, dict[str, float]] = {}
        self.spin_cat: dict[str, list[int]] = {}
        self.spin_central: dict[str, tuple[float, ...]] = {}
        for band in pri["bands"]["ids"]:
            weights = pri["class"]["bands"][band]["joint_weight"]
            cum = []
            self.class_raw[band] = [{c: weights[c] * refl["link"][c][b] for c in CLASSES}
                                    for b in range(len(self.edges) + 1)]
            self.class_central[band] = {c: pri["class"]["bands"][band]["central"][c] for c in CLASSES}
            for b in range(len(self.edges) + 1):
                raw = [weights[c] * refl["link"][c][b] for c in CLASSES]
                total = sum(raw)
                acc, row = 0.0, []
                for w in raw[:-1]:
                    acc += w / total
                    row.append(acc)
                cum.append(tuple(row))
            self.class_cum[band] = cum
            central = tuple(pri["spin"]["bands"][band][s]["central"] for s in pri["spin"]["ids"])
            self.spin_central[band] = central
            # central is (under 2.2 h, under 1 h, under 10 min); a slice u is in category sum(u >= c)
            self.spin_cat[band] = [sum(1 for c in central if u >= c) for u in self.u]

        d = pri["density"]
        self.dens = {c: (d[c]["lo"], d[c]["hi"]) for c in CLASSES if c != "X"}
        x = d["X"]
        self.x_edges = tuple(x["split_edges_pv"])
        self.x_metal_share = x["metal_rich_share_of_mid"]
        self.x_dens = {k: (x[k]["lo"], x[k]["hi"]) for k in ("dark", "mid_silicate", "mid_metal", "bright")}

    def density_range(self, cls: str, pv: float, u_metal: float) -> tuple[float, float]:
        if cls != "X":
            return self.dens[cls]
        if pv < self.x_edges[0]:
            return self.x_dens["dark"]
        if pv < self.x_edges[1]:
            return self.x_dens["mid_metal" if u_metal < self.x_metal_share else "mid_silicate"]
        return self.x_dens["bright"]


@functools.lru_cache(maxsize=4)
def tables(m: Method) -> Tables:
    return Tables(m)


# --------------------------------------------------------------------------
# what the draws amount to, written into the record

def _h_words(inp) -> str:
    return f"H {inp.h:g} ± {inp.h_sigma:.2g}"


def size_basis(m: Method, inp) -> str:
    refl = m.priors["reflectivity"]
    size = m.priors["size"]
    if inp.albedo is not None:
        text = f"{_h_words(inp)} and its measured reflectivity"
    elif inp.cls is not None:
        n = refl["by_class"][inp.cls]["n"]
        which = f"of class {inp.cls}" if inp.cls != "other" else "of classes other than S, C and X"
        text = f"{_h_words(inp)} and the reflectivities Spitzer measured for {n:,} near-Earth asteroids {which}"
    else:
        text = f"{_h_words(inp)} and the reflectivities Spitzer measured for {refl['n_objects']:,} near-Earth asteroids"
        if inp.h >= size["extrapolated_fainter_than_h"]:
            text += (f", {size['n_measured_at_or_fainter']} of them "
                     f"H {size['extrapolated_fainter_than_h']:g} or fainter")
    if inp.size_bound is not None and not inp.size_bound_ignored:
        word = "at most" if inp.size_bound.kind == "upper" else "at least"
        text += (f"; {word} {inp.size_bound.value:g} m from the limit on file" if inp.size_bound_public
                 else "; cut at the limit on file")
    return text


def spin_basis(m: Method, inp) -> str:
    band = m.priors["spin"]["bands"][inp.band]
    first = m.priors["spin"]["ids"][0]
    row = band[first]
    words = BAND_WORDS.get(inp.band, inp.band)
    if row.get("central_from") == "midpoint":
        # no "no measured period" here: the row this prints in may be one a source was not checked for
        text = (f"asteroids of H {words}: the midpoint between surveys, "
                f"which give {row['low']:.2f} to {row['high']:.2f} for 2.2 h")
    else:
        text = f"asteroids of H {words}: {row.get('central_from', 'the central share')}"
    if inp.period_bound is not None and not inp.period_bound_ignored:
        word = "at most" if inp.period_bound.kind == "upper" else "at least"
        text += (f"; {word} {inp.period_bound.value:g} h from the limit on file" if inp.period_bound_public
                 else "; cut at the limit on file")
    return text


def surface_basis(m: Method, inp) -> str:
    n = m.priors["class"]["bands"][inp.band]["n"]
    words = BAND_WORDS.get(inp.band, inp.band)
    text = (f"class labels on {n:,} near-Earth asteroids of H {words}, "
            "tied to reflectivity through Spitzer's measurements")
    if inp.size is not None:
        text += "; reflectivity from its measured size and H"
    return text


def summary(m: Method, d) -> dict:
    n = d.n
    spin = [0, 0, 0, 0]
    for c in d.spin:
        spin[c] += 1
    counts = {c: 0 for c in CLASSES}
    for c in d.cls:
        counts[c] += 1
    out = {
        "size_m": quantiles(d.d),
        "mass_t": quantiles(d.mass),
        SPIN_KEYS[0]: share(n - spin[3], n),
        SPIN_KEYS[1]: share(spin[0] + spin[1], n),
        SPIN_KEYS[2]: share(spin[0], n),
        "class": {c: share(counts[c], n) for c in CLASSES},
        "reflectivity": quantiles(d.pv),
        "h": d.inputs.h,
        "band": d.inputs.band,
        "draws": n,
    }
    return out


def fill(record: ObjectRecord, d, m: Method) -> ObjectRecord:
    """Row priors for rows in state prior or unchecked, and record.summary. d is None for an object with no H."""
    rows = record.rows
    if d is None:
        record.summary = {}
        for name in ("size", "spin", "surface"):
            if rows[name].state in ("prior", "unchecked"):
                rows[name].prior = None
        return record
    inp = d.inputs
    s = summary(m, d)
    record.summary = s

    if rows["size"].state in ("prior", "unchecked"):
        rows["size"].prior = {**s["size_m"], "unit": "m", "basis": size_basis(m, inp)}
    if rows["spin"].state in ("prior", "unchecked"):
        band = m.priors["spin"]["bands"][inp.band]
        rows["spin"].prior = {
            **{k: s[k] for k in SPIN_KEYS},
            "range": {k: [band[i]["low"], band[i]["high"]] for k, i in zip(SPIN_KEYS, m.priors["spin"]["ids"])},
            "basis": spin_basis(m, inp),
        }
    if rows["surface"].state in ("prior", "unchecked"):
        rows["surface"].prior = {**s["reflectivity"], "unit": "", "shares": dict(s["class"]),
                                 "basis": surface_basis(m, inp)}
    return record
