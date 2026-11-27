"""Joint draws for one object: class, reflectivity, size, density, mass and spin, drawn together.

    d = draws.for_record(record)          # Draws, or None for an object with no H
    records = draws.apply(records)        # stage 2: row priors and record.summary

The steps are those of method/v0_1/priors.toml [joint]. A measured quantity
replaces its step; a limit removes the draws that break it.

A measured value is drawn from its stated one-sigma error, each side its own
width, with no clamp (missions.toml [rules.decide]). A measured class is a
label that can be wrong: a stated share of the draws take a class from the
other side of S/Q against the rest (priors.toml [class.label_error]).

An object with nothing measured about the rock itself (no size, class,
reflectivity or density) is seeded by its brightness, not its key, so two
objects with the same H and H error get the same draws and the same price tag.

The draws are stratified (a Latin hypercube): each random input takes every one
of the n slice midpoints of longshot/priors.py exactly once, and the generator,
seeded from the object key and the method version, only decides the pairing.
The same key and method give the same draws. Shares that depend on one input
alone (a spin share from brightness, say) therefore come out as the method
states them, to one part in n, for every object.
"""
from __future__ import annotations

import dataclasses
import math
import random

from longshot import ledger as ledger_mod
from longshot import method as method_mod
from longshot import priors
from longshot.method import Method
from longshot.types import Fact, ObjectRecord, Row

# How a source is named inside a sentence.
SPOKEN = ledger_mod.SPOKEN
LENGTH_M = {"m": 1.0, "km": 1000.0}
TIME_H = {"h": 1.0, "min": 1.0 / 60.0, "s": 1.0 / 3600.0, "d": 24.0}


def spoken(source_id: str) -> str:
    return SPOKEN.get(source_id, source_id)


def spoken_list(source_ids) -> str:
    return ", ".join(spoken(s) for s in source_ids)


# --------------------------------------------------------------------------
# reading a record's rows

def is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def find(row: Row | None, *labels: str, kinds=("value",), numeric: bool = True, loose: bool = False) -> Fact | None:
    """The first fact with one of these labels. With loose, a longer label that starts or ends with one also counts."""
    if row is None:
        return None
    for exact in ((True, False) if loose else (True,)):
        for f in row.facts:
            name = (f.label or "").casefold()
            if exact:
                hit = name in labels
            else:
                hit = any(name.endswith(l) or name.startswith(l) for l in labels)
            if hit and f.kind in kinds and (not numeric or is_num(f.value)):
                return f
    return None


def _same(a, b) -> bool:
    """Equal as printed, to four significant figures (the rule longshot/site/templates.py applies)."""
    if is_num(a) and is_num(b):
        return priors.sig(float(a), 4) == priors.sig(float(b), 4)
    return a == b


def grade_digit(quality: str | None) -> int | None:
    """The leading digit of a lightcurve grade ('3-', '2+', '1'), or None when the fact carries no grade."""
    q = (quality or "").strip()
    if q[:1].isdigit() and len(q) <= 2 and (len(q) == 1 or q[1] in "+-"):
        return int(q[0])
    return None


def class_group(label) -> str | None:
    """S (S, Q), C (C, B, F, G), X (X, E, M, P) or other; None for an empty or undecided label."""
    t = str(label or "").strip()
    if not t or t.upper() in ("U", "CX", "XC", "C/X", "X/C"):
        return None
    c = t[0].upper()
    if c in "SQ":
        return "S"
    if c in "CBFG":
        return "C"
    if c in "XEMP":
        return "X"
    if c in "ADKLORTVZ":
        return "other"
    return None


@dataclasses.dataclass(frozen=True)
class Measured:
    """A value with its stated one-sigma range, in the unit the draw uses (m, h, kg/m3 or none).

    lo and hi are the value less and plus one stated sigma; they equal the value when no error is stated.
    factor, for a size with no stated error: the draw is log-normal with two sigma equal to this factor
    (missions.toml [rules.decide].no_range_factor).
    """
    value: float
    lo: float
    hi: float
    fact: Fact
    kind: str = "value"
    factor: float | None = None

    @property
    def ranged(self) -> bool:
        return self.lo < self.hi

    def reach(self, k: float) -> tuple[float, float]:
        """The value less and plus k sigma. With no stated error: the value over and times factor^(k/2), or,
        with no factor either, the value itself."""
        if self.ranged:
            return max(self.value - k * (self.value - self.lo), 0.0), self.value + k * (self.hi - self.value)
        if self.factor:
            f = self.factor ** (k / 2.0)
            return self.value / f, self.value * f
        return self.value, self.value

    def draw(self, z: float) -> float:
        """One draw at the standard normal deviate z; never under a tenth of the value."""
        if self.ranged:
            v = self.value + z * ((self.value - self.lo) if z < 0 else (self.hi - self.value))
            return max(v, 0.1 * self.value)
        if self.factor:
            return self.value * self.factor ** (z / 2.0)
        return self.value


def _measured(f: Fact, scale: float = 1.0, factor: float | None = None) -> Measured:
    v = f.value * scale
    lo, hi = f.lo, f.hi
    if is_num(lo) and is_num(hi) and 0 < lo * scale <= v <= hi * scale and lo < hi:
        return Measured(v, lo * scale, hi * scale, f, f.kind)
    return Measured(v, v, v, f, f.kind, factor)


def colour_label(fact: Fact) -> bool:
    """A class from broad-band colours, not a spectrum: SsODNet's technique 'Phot'."""
    return "Phot" in (fact.quality or "").replace(",", " ").split()


@dataclasses.dataclass
class Inputs:
    """What an object's rows give the joint draw."""
    h: float | None = None
    h_sigma: float = 0.0
    h_sigma_stated: bool = False
    band: str | None = None
    occ: int | None = None
    size: Measured | None = None            # a measured size that counts
    size_rejected: Measured | None = None   # a measured size that implies an impossible reflectivity
    size_bound: Measured | None = None      # the size row is a limit
    size_bound_ignored: bool = False
    albedo: Measured | None = None
    cls: str | None = None                  # S, C, X or other, when the class is measured
    cls_fact: Fact | None = None
    cls_error: float = 0.0                  # share of draws in which the label is on the wrong side of S against the rest
    density: Measured | None = None         # a bulk density on file, kg/m3
    period_split: str | None = None         # the row's conflict sentence, when periods in use straddle a spin gate
    sampled: bool = False                   # a spacecraft brought a sample back: the class is not in doubt
    period: Measured | None = None          # a period that decides (missions.toml [rules.period]), hours
    period_unreliable: Fact | None = None   # the best-graded period on file when none decides
    period_bound: Measured | None = None    # the spin row is a limit
    period_bound_ignored: bool = False

    @property
    def size_measured(self) -> bool:
        return self.size is not None

    @property
    def nothing_measured(self) -> bool:
        """Only brightness went into the rock: its size, class, reflectivity, density and mass. A period or a
        limit on one changes the spin column alone, so it does not make the rock's draws its own."""
        return not any((self.size, self.size_bound, self.albedo, self.cls, self.density))


def _straddles(facts: list[Fact], lines_h: list[float], k: float) -> bool:
    """Do these periods, by value or by k sigma of their stated ranges, fall on both sides of one of the lines?"""
    for line in lines_h:
        sides = set()
        for f in facts:
            lo, hi = _measured(f, TIME_H[f.unit]).reach(k)
            sides.add("below" if hi < line else "above" if lo >= line else "across")
        if len(sides) > 1:
            return True
    return False


def inputs(record: ObjectRecord, m: Method) -> Inputs:
    rows = record.rows
    inp = Inputs(h_sigma=m.priors["h_uncertainty"]["default_sigma"])

    size_row = rows.get("size")
    hf = find(size_row, "h")
    if hf is not None:
        inp.h = float(hf.value)
        inp.band = priors.band_of(m, inp.h)
        if is_num(hf.lo) and is_num(hf.hi) and hf.hi > hf.lo:
            inp.h_sigma, inp.h_sigma_stated = (hf.hi - hf.lo) / 2.0, True

    occ = find(rows.get("tracking"), "condition code", loose=True)
    if occ is not None:
        inp.occ = int(occ.value)

    rules = m.missions["rules"]
    if size_row is not None and size_row.state == "measured":
        f = next((f for f in size_row.facts if "diameter" in (f.label or "").casefold() and f.kind == "value"
                  and f.used and is_num(f.value) and f.value > 0 and f.unit in LENGTH_M), None)
        if f is not None:
            got = _measured(f, LENGTH_M[f.unit], rules["decide"]["no_range_factor"])
            floor, ceiling = rules["size"]["min_implied_reflectivity"], rules["size"]["max_implied_reflectivity"]
            # H is uncertain too: the size is turned away only if no H within decide.sigma of its error saves it
            slack = rules["decide"]["sigma"] * inp.h_sigma
            if inp.h is not None and (priors.implied_reflectivity(m, inp.h - slack, got.value) < floor
                                      or priors.implied_reflectivity(m, inp.h + slack, got.value) > ceiling):
                inp.size_rejected = got
            else:
                inp.size = got
    elif size_row is not None and size_row.state == "limit":
        f = next((f for f in size_row.facts if "diameter" in (f.label or "").casefold() and f.used
                  and f.kind in ("upper", "lower") and is_num(f.value) and f.value > 0 and f.unit in LENGTH_M), None)
        if f is not None:
            inp.size_bound = _measured(f, LENGTH_M[f.unit])

    inp.sampled = any(f.get("kind") == "sample_return" and _names(record) & set(f.get("objects", []))
                      for f in m.ladder["fact"])
    surface = rows.get("surface")
    if surface is not None and surface.state == "measured":
        rates = m.priors["class"]["label_error"]
        for f in surface.facts:
            label = (f.label or "").casefold()
            if not f.used:
                continue                      # on file, not counted: a computed or known-bad value
            if label == "class" and f.kind == "value":
                group = class_group(f.value)
                if group is None:
                    continue
                if inp.cls is None:
                    inp.cls, inp.cls_fact = group, f
                    inp.cls_error = rates["colour"] if colour_label(f) else rates["spectrum"]
                elif group == inp.cls and not colour_label(f):
                    inp.cls_error = min(inp.cls_error, rates["spectrum"])     # a spectrum backs the label
            elif label == "albedo" and inp.albedo is None and f.kind == "value" and is_num(f.value) \
                    and f.value > 0 and "Computed" not in (f.quality or "").split("+"):
                inp.albedo = _measured(f)
        if inp.sampled:
            inp.cls_error = 0.0

    push = rows.get("push")
    if push is not None:
        f = next((f for f in push.facts if (f.label or "").casefold() == "density" and f.used and f.kind == "value"
                  and is_num(f.value) and f.value > 0), None)
        if f is not None:
            inp.density = _measured(f)

    spin = rows.get("spin")
    if spin is not None:
        min_grade = rules["period"]["min_grade"]
        periods = [f for f in spin.facts if (f.label or "").casefold() == "period" and is_num(f.value)
                   and f.value > 0 and f.unit in TIME_H]
        values = [f for f in periods if f.kind == "value"]
        in_use = [f for f in values if f.used]
        first = in_use[0] if in_use else None
        gate_lines = [g["preset"] for mission in m.missions["order"] for g in m.missions[mission]["gates"]
                      if g["quantity"] == "period_h"]
        if spin.state == "measured" and first is not None and spin.conflicts \
                and _straddles(in_use, gate_lines, rules["decide"]["sigma"]):
            # missions.toml [rules.conflict]: sources disagree across a gate, so no period decides
            inp.period_split = spin.conflicts[0]
        elif spin.state == "measured" and first is not None \
                and (grade_digit(first.quality) is None or grade_digit(first.quality) >= min_grade):
            inp.period = _measured(first, TIME_H[first.unit])
        else:
            if spin.state == "limit":
                b = next((f for f in periods if f.kind in ("upper", "lower") and f.used), None)
                if b is not None:
                    inp.period_bound = _measured(b, TIME_H[b.unit])
            low = [f for f in values if grade_digit(f.quality) is not None and grade_digit(f.quality) < min_grade]
            if low:
                inp.period_unreliable = max(low, key=lambda f: _grade_rank(f.quality))
    return inp


def _names(record: ObjectRecord) -> set[str]:
    out = {record.designation, record.name, str(record.number) if record.number else None, *record.aliases}
    return {str(x) for x in out if x}


def _grade_rank(quality: str) -> int:
    q = quality.strip()
    return int(q[0]) * 3 + {"+": 1, "-": -1}.get(q[1:], 0)


# --------------------------------------------------------------------------
# the draw

@dataclasses.dataclass
class Draws:
    n: int
    inputs: Inputs
    cls: list[str]
    pv: list[float]
    d: list[float]            # metres
    rho: list[float]          # kg/m3
    mass: list[float]         # tonnes
    spin: list[int]           # category: 0 under 10 min, 1 under 1 h, 2 under 2.2 h, 3 slower
    period: list[float] | None = None    # hours, only when a period is measured
    seed_key: str = ""        # what the draws were seeded by: the object key, or its brightness alone

    def joint(self):
        """(class, reflectivity, diameter_m, density_kg_m3) per draw: what longshot/value.py reads."""
        return zip(self.cls, self.pv, self.d, self.rho)


def seed(key: str, m: Method, purpose: str) -> str:
    return f"longshot method {m.version} object {key} {purpose}"


def seed_key(key: str, inp: Inputs) -> str:
    """The object key, or, when only brightness went into the draw, the brightness: equal inputs, equal figures."""
    if inp.nothing_measured and inp.h is not None:
        return f"H {inp.h!r} sigma {inp.h_sigma!r}"
    return key


def _pairing(rng: random.Random, n: int) -> list[int]:
    keys = [rng.random() for _ in range(n)]
    return sorted(range(n), key=keys.__getitem__)


def _other_side(t, band: str, cls: str, pv_bin: int | None, v: float) -> str:
    """The class a mislabelled draw takes: S when the label is not S; else C, X or other, by their weights.

    With a known reflectivity the weights are those of priors.toml [joint] step 4 in its reflectivity bin;
    without, the band's class shares. v is uniform on (0, 1).
    """
    if cls != "S":
        return "S"
    w = t.class_raw[band][pv_bin] if pv_bin is not None else t.class_central[band]
    total = w["C"] + w["X"] + w["other"]
    if total <= 0:
        return "other"
    v *= total
    return "C" if v < w["C"] else "X" if v < w["C"] + w["X"] else "other"


def joint(key: str, inp: Inputs, m: Method) -> Draws | None:
    """The joint draw of priors.toml [joint] for one object. None when it has no H."""
    if inp.h is None:
        return None
    t = priors.tables(m)
    n = t.n
    seeded_by = seed_key(key, inp)
    rng = random.Random(seed(seeded_by, m, "draws"))
    # Reflectivity keeps the order of its slices; the other inputs are paired with it at random.
    p_h, p_c, p_m, p_r, p_s, p_x = (_pairing(rng, n) for _ in range(6))

    u, z = t.u, t.z
    d0 = t.coef * 10 ** (-inp.h / 5.0)
    k_h = -inp.h_sigma / 5.0
    edges = t.edges
    cum = t.class_cum[inp.band]
    thresholds = t.thresholds_h
    spin_cat = t.spin_cat[inp.band]
    size, albedo, cls, period, density = inp.size, inp.albedo, inp.cls, inp.period, inp.density
    err = inp.cls_error if cls is not None else 0.0
    pi6 = math.pi / 6000.0

    o_cls, o_pv, o_d, o_rho, o_mass, o_spin = [], [], [], [], [], []
    o_period = [] if period is not None else None
    for i in range(n):
        d_h = d0 * 10 ** (k_h * z[p_h[i]])                   # step 1: H drawn as normal(H, sigma)
        uc = u[p_c[i]]
        wrong = cls is not None and uc < err                 # step 4a: the label is on the wrong side
        if size is not None:                                 # steps 2 and 3
            d = size.draw(z[p_x[i]])
            pv = (d_h / d) ** 2
            c = _other_side(t, inp.band, cls, sum(1 for e in edges if pv >= e), uc / err) if wrong else cls
        elif albedo is not None:
            pv = max(albedo.draw(z[p_x[i]]), 1e-4)
            d = d_h / math.sqrt(pv)
            c = _other_side(t, inp.band, cls, sum(1 for e in edges if pv >= e), uc / err) if wrong else cls
        elif cls is not None:
            c = _other_side(t, inp.band, cls, None, uc / err) if wrong else cls
            pv = t.pv_class[c][i]
            d = d_h / math.sqrt(pv)
        else:
            pv = t.pv_all[i]
            d = d_h / math.sqrt(pv)
            c = None
        if c is None:                                        # step 4
            row = cum[sum(1 for e in edges if pv >= e)]
            c = "S" if uc < row[0] else "C" if uc < row[1] else "X" if uc < row[2] else "other"
        if density is not None:                              # step 5: a density on file replaces the class range
            rho = density.draw(z[p_r[i]])
        else:
            lo, hi = t.density_range(c, pv, u[p_m[i]])
            rho = lo + (hi - lo) * u[p_r[i]]
        if period is not None:                               # step 7
            p = period.draw(z[p_s[i]])
            o_period.append(p)
            o_spin.append(sum(1 for th in thresholds if p >= th))
        else:
            o_spin.append(spin_cat[p_s[i]])
        o_cls.append(c)
        o_pv.append(pv)
        o_d.append(d)
        o_rho.append(rho)
        o_mass.append(pi6 * d ** 3 * rho)                    # step 6

    # A limit that leaves too few draws to state a range from does not fit this brightness and is not applied.
    min_kept = m.value["exports"]["min_draws_for_a_range"]
    keep = None
    if inp.size_bound is not None:
        b = inp.size_bound
        ok = [(x <= b.value) if b.kind == "upper" else (x >= b.value) for x in o_d]
        if sum(ok) >= min_kept:
            keep = ok
        else:
            inp.size_bound_ignored = True
    if keep is not None:
        pick = [i for i, k in enumerate(keep) if k]
        o_cls, o_pv, o_d, o_rho, o_mass, o_spin = ([col[i] for i in pick]
                                                    for col in (o_cls, o_pv, o_d, o_rho, o_mass, o_spin))
        if o_period is not None:
            o_period = [o_period[i] for i in pick]
    if inp.period_bound is not None:
        b = inp.period_bound
        # category edges in hours: 0 | 1/6 | 1 | 2.2 | infinity. A category goes when the limit rules all of it out.
        cat_lo = [0.0] + sorted(thresholds)
        cat_hi = sorted(thresholds) + [math.inf]
        allowed = [(cat_lo[c] < b.value) if b.kind == "upper" else (cat_hi[c] > b.value) for c in range(4)]
        left = [c for c in o_spin if allowed[c]]
        if len(left) >= min_kept:
            # Spin is drawn apart from the rock (priors.toml [spin].independent_of), so the limit re-deals the
            # spin column alone, in the shares the allowed categories had. The rock's draws are untouched: a
            # limit on the period does not change what is in it.
            o_spin = [left[i * len(left) // len(o_spin)] for i in range(len(o_spin))]
        else:
            inp.period_bound_ignored = True
    return Draws(n=len(o_d), inputs=inp, cls=o_cls, pv=o_pv, d=o_d, rho=o_rho, mass=o_mass, spin=o_spin,
                 period=o_period, seed_key=seeded_by)


def for_record(record: ObjectRecord, m: Method | None = None) -> Draws | None:
    """The draws for one record: the same every time for the same rows, key and method."""
    m = m or method_mod.load()
    return joint(record.key, inputs(record, m), m)


def rejected_size_sentence(inp: Inputs, m: Method) -> str | None:
    """The conflict a size row shows when its measured size implies an impossible reflectivity.

    missions.toml [rules.size].
    """
    x = inp.size_rejected
    if x is None:
        return None
    pv = priors.implied_reflectivity(m, inp.h, x.value)
    return (f"{cap(spoken(x.fact.source))} gives {x.value:,.4g} m, which at H {inp.h:g} implies a reflectivity of "
            f"{priors.sig(pv, 2):g}; it is not used.")




def _period_fact(f: Fact, kinds=("value",)) -> bool:
    return ((f.label or "").casefold() == "period" and f.used and f.kind in kinds
            and is_num(f.value) and f.value > 0 and f.unit in TIME_H)


def shown_period(record: ObjectRecord) -> dict | None:
    """The period the spin row rests on, as an entry prints it: summary.period.

    The row rests on its first used period (a value where the row is measured, a bound where it is a limit).
    None where the spin row is neither measured nor a limit.

    {value, unit, lo, hi, kind, source, ref, quality, rests_on, conflict}
    """
    row = record.rows["spin"]
    kinds = {"measured": ("value",), "limit": ("upper", "lower")}.get(row.state)
    if kinds is None:
        return None
    periods = [f for f in row.facts if _period_fact(f, kinds)]
    if not periods:
        return None
    rest = periods[0]
    return {"value": rest.value, "unit": rest.unit, "lo": rest.lo, "hi": rest.hi, "kind": rest.kind,
            "source": rest.source, "ref": rest.ref, "quality": rest.quality,
            "rests_on": rest.source, "conflict": bool(row.conflicts)}


def apply_one(record: ObjectRecord, d: Draws | None, m: Method) -> ObjectRecord:
    inp = d.inputs if d is not None else inputs(record, m)
    text = rejected_size_sentence(inp, m)
    if text and text not in record.rows["size"].conflicts:
        record.rows["size"].conflicts.append(text)
    priors.fill(record, d, m)
    if record.summary:                                   # {} where there is no H (docs/mvp.md section 4)
        # what the mass range was drawn from besides the size: a bulk density on file, or the class's range
        record.summary["mass_basis"] = "density" if inp.density is not None else "class"
        # the period the spin row rests on, as an entry may print it
        record.summary["period"] = shown_period(record)
    return record


def apply(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Stage 2: the prior of each row nobody has measured, and record.summary."""
    m = m or method_mod.load()
    for r in records:
        apply_one(r, for_record(r, m), m)
    return records
