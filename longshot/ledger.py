"""Claims and coverage -> the six rows of every reachable asteroid.

    records = ledger.build()                 # list[ObjectRecord], also writes build/ledger.jsonl
    uv run python -m longshot.ledger         # the same, and prints counts by row and state

The rows are filled; summary, missions, observe, value and ladder are left
empty for the model code, and every row's `prior` is None.

A row's state (docs/mvp.md section 4):
  measured   at least one usable value
  limit      no usable value, at least one usable bound
  prior      neither, and every source for the row was looked at
  unchecked  neither, and at least one source for the row was not looked at
`Row.unchecked` always lists the sources not looked at, whatever the state.
When the state is measured or limit, facts[0] is the value or bound adopted.

Every threshold used here is read from method/v0_1/ledger.toml (a proposal
until Adam freezes it): the lowest grade that counts, how far two periods may
differ, the detection bar for a fitted push, the Spitzer signal-to-noise bar,
the known-bad values and the bodies that no longer exist.
"""
from __future__ import annotations

import dataclasses
import functools
import json
import math
import os
import re
import sys
from pathlib import Path

from longshot import config, ids, ingest
from longshot.ingest._common import OLDER_THAN_OBJECT
from longshot import method as method_mod
from longshot.types import ROWS, STATES, Claim, Coverage, Fact, ObjectRecord, Row

# Which sources count for each row, in order of preference when several give a usable value.
ROW_SOURCES: dict[str, tuple[str, ...]] = {
    "reach": ("jpl-nhats",),
    "tracking": ("jpl-sbdb", "jpl-nhats"),
    "size": ("curated", "ssodnet", "spitzer", "jpl-sbdb"),
    "spin": ("curated", "pravec", "lcdb", "ssodnet", "jpl-sbdb"),
    "surface": ("curated", "ssodnet", "spitzer", "jpl-sbdb"),
    "push": ("jpl-sbdb", "ssodnet"),
}
# A source that only adds claims. It is a short hand-entered list, not a catalogue that was looked up, so it
# never makes a row "not checked" (longshot/ingest/curated.py).
SUPPLEMENTARY = frozenset({"curated"})
# Licence class by source (docs/mvp.md section 3). A value from an "inference" source is not printed in a
# sentence unless another source states it. tests/test_model.py checks this table against longshot.sources.
LICENCE = {"jpl-nhats": "open", "jpl-sbdb": "open", "ssodnet": "single", "pravec": "single", "lcdb": "inference",
           "spitzer": "single", "curated": "single"}

COMPUTED = "Computed"

# Claim property -> the label a fact carries. Labels are the stable way to find a fact in a row.
LABEL = {
    "delta_v_kms": "delta-v",
    "trip_days_at_min_delta_v": "trip at lowest delta-v",
    "min_trip_days": "shortest trip",
    "min_trip_delta_v_kms": "delta-v of shortest trip",
    "n_trajectories": "trajectories",
    "condition_code": "condition code",
    "data_arc_days": "arc",
    "n_obs_used": "observations",
    "first_obs": "first observed",
    "last_obs": "last observed",
    "n_radar_delay": "radar delay observations",
    "n_radar_doppler": "radar Doppler observations",
    "window_start": "window start",
    "window_end": "window end",
    "window_peak_mag": "window peak brightness",
    "window_pointing": "window pointing",
    "next_window": "next window",
    "diameter_m": "diameter",
    "H": "H",
    "period_h": "period",
    "amplitude_mag": "amplitude",
    "taxonomy": "class",
    "albedo": "albedo",
    "A1": "A1",
    "A2": "A2",
    "A3": "A3",
    "drift_au_per_myr": "drift",
    "density_kgm3": "density",
}
_INTEGER = {"trip_days_at_min_delta_v", "min_trip_days", "n_trajectories", "condition_code", "data_arc_days",
            "n_obs_used", "n_radar_delay", "n_radar_doppler"}
WINDOW_PROPS = ("window_start", "window_end", "window_peak_mag", "window_pointing", "next_window")

# How a source is named inside a sentence.
SPOKEN = {
    "jpl-nhats": "JPL's reachable list",
    "jpl-sbdb": "JPL's database",
    "ssodnet": "SsODNet",
    "pravec": "Pravec's table",
    "lcdb": "the lightcurve database",
    "spitzer": "the Spitzer table",
    "curated": "the literature",
}
# A claim note that says the same of every value from its source; the row's note carries it once.
_ROUTINE_NOTES = ("JPL gives no quality grade", "bulk value, rounded to two figures; the force law is not given")


@dataclasses.dataclass(frozen=True)
class KnownBad:
    """An upstream value the research found to be wrong. Pinned to the value, so a corrected one is not caught."""
    designation: str
    prop: str
    value: float
    why: str            # one sentence for the row's note
    evidence: str       # where the research says so


@dataclasses.dataclass(frozen=True)
class Gone:
    """A body on the reachable list that no longer exists."""
    designation: str
    date: str
    text: str           # one or two sentences for the page
    evidence: str


@dataclasses.dataclass(frozen=True)
class Rules:
    """method/v0_1/ledger.toml, as the row builders use it."""
    min_grade: str
    min_rank: int
    tolerance: float
    detection_sigma: float
    push_counts: tuple[str, ...]
    spitzer_min_snr: float
    max_reflectivity: float
    fixed_tables: tuple[str, ...]
    known_bad: tuple[KnownBad, ...]
    gone: tuple[Gone, ...]


def _rules_from(led: dict) -> Rules:
    return Rules(
        min_grade=led["period"]["min_grade"], min_rank=grade_rank(led["period"]["min_grade"]),
        tolerance=float(led["period"]["tolerance"]), detection_sigma=float(led["push"]["detection_sigma"]),
        push_counts=tuple(led["push"]["counts"]), spitzer_min_snr=float(led["spitzer"]["min_snr"]),
        max_reflectivity=float(led["reflectivity"]["max"]), fixed_tables=tuple(led["fixed_tables"]["sources"]),
        known_bad=tuple(KnownBad(b["designation"], b["prop"], float(b["value"]), b["why"], b["source"])
                        for b in led["known_bad"]),
        gone=tuple(Gone(g["designation"], g["date"], g["text"], g["source"]) for g in led["gone"]),
    )


@functools.lru_cache(maxsize=4)
def _rules_for(m) -> Rules:
    rules = _rules_from(m.ledger)
    if rules.min_rank is None:
        raise method_mod.MethodError(f"ledger.toml: period.min_grade {rules.min_grade!r} is not a U grade")
    return rules


def rules() -> Rules:
    """The thresholds of method/v0_1/ledger.toml."""
    return _rules_for(method_mod.load())


# --------------------------------------------------------------------------
# small helpers

def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _show(value, unit: str = "") -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        s = format(value, ",.4g")
    else:
        s = str(value)
    return f"{s} {unit}".strip()


def _fact(c: Claim, used: bool = True, note: str | None = None) -> Fact:
    """`used` is False for a value that stays on file but does not count towards the row's state."""
    value = c.value
    if c.prop in _INTEGER and isinstance(value, float) and value == int(value):
        value = int(value)
    if note is None and c.note and c.note not in _ROUTINE_NOTES:
        note = c.note
    return Fact(label=LABEL[c.prop], value=value, lo=c.lo, hi=c.hi, unit=c.unit, kind=c.kind,
                source=c.source, ref=c.ref, quality=c.quality, used=used, note=note)


def _by_source(claims: list[Claim], row: str, props: tuple[str, ...]) -> list[Claim]:
    """Claims with these properties from the row's sources, in the row's source order, then file order."""
    order = {s: i for i, s in enumerate(ROW_SOURCES[row])}
    picked = [c for c in claims if c.prop in props and c.source in order]
    return sorted(picked, key=lambda c: (order[c.source], props.index(c.prop)))   # stable


def grade_rank(quality: str | None) -> int | None:
    """'3' -> 9, '3-' -> 8, '2+' -> 7, '2' -> 6, '2-' -> 5, '1+' -> 4 ... ; None when not a U grade."""
    if not quality:
        return None
    m = re.fullmatch(r"([0-3])([+-]?)", quality.strip())
    if not m:
        return None
    return int(m.group(1)) * 3 + {"": 0, "+": 1, "-": -1}[m.group(2)]


def periods_differ(a: float, b: float) -> bool:
    lo, hi = min(a, b), max(a, b)
    return lo <= 0 or hi / lo > 1.0 + rules().tolerance


def same_number(a, b) -> bool:
    """Equal as printed: to six significant figures."""
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)):
        return False
    return a == b or abs(a - b) <= 5e-7 * max(abs(a), abs(b))


def class_complex(cls: str) -> str:
    """The complex a class belongs to: S (with Q), C (with B, F, G), X (with E, M, P), else its own letter."""
    c = cls.strip().strip(":").strip()
    if not c:
        return "?"
    first = c[0].upper()
    if first in "SQ":
        return "S"
    if first in "CBFG":
        return "C"
    if first in "XEMP":
        return "X"
    return first


def is_known_bad(c: Claim, designations: set[str]) -> KnownBad | None:
    for bad in rules().known_bad:
        if bad.designation in designations and bad.prop == c.prop and isinstance(c.value, (int, float)) \
                and abs(c.value - bad.value) <= 1e-9 * max(1.0, abs(bad.value)):
            return bad
    return None


def is_gone(designations: set[str]) -> Gone | None:
    return next((g for g in rules().gone if g.designation in designations), None)


def _computed(c: Claim) -> bool:
    return COMPUTED in (c.quality or "").split("+")


def _resolve_state(usable_values: bool, usable_bounds: bool, unchecked: list[str]) -> str:
    if usable_values:
        return "measured"
    if usable_bounds:
        return "limit"
    return "unchecked" if unchecked else "prior"


def _unchecked(row: str, cov: dict[tuple[str, str], Coverage]) -> tuple[list[str], list[str]]:
    """(source ids not looked at for this row, one sentence each saying why)."""
    out, why = [], []
    for s in ROW_SOURCES[row]:
        if s in SUPPLEMENTARY:
            continue
        c = cov.get((row, s))
        if c is None:
            out.append(s)
            why.append(f"{_cap(SPOKEN[s])} was not read.")
        elif c.outcome == "unchecked":
            out.append(s)
            if c.reason == OLDER_THAN_OBJECT:
                why.append(f"{_cap(SPOKEN[s])} is {c.reason}.")
            else:
                why.append(_cap(c.reason.rstrip(".")) + "." if c.reason else f"{_cap(SPOKEN[s])} was not checked.")
        elif c.outcome not in ("found", "absent"):
            raise ValueError(f"coverage outcome {c.outcome!r} for {row}/{s}")
    return out, why


def _row(row: str, facts: list[Fact], values: bool, bounds: bool, cov, notes: list[str],
         conflicts: list[str] | None = None) -> Row:
    unchecked, why = _unchecked(row, cov)
    note = " ".join(dict.fromkeys(notes + why)) or None
    return Row(state=_resolve_state(values, bounds, unchecked), facts=facts, prior=None,
               unchecked=unchecked, conflicts=conflicts or [], note=note)


def _ranges_apart(a: Claim, b: Claim) -> bool:
    """The two stated ranges do not overlap; a value with no range is its own range."""
    a_lo, a_hi = (a.lo, a.hi) if a.lo is not None and a.hi is not None else (a.value, a.value)
    b_lo, b_hi = (b.lo, b.hi) if b.lo is not None and b.hi is not None else (b.value, b.value)
    return a_lo > b_hi or b_lo > a_hi


# --------------------------------------------------------------------------
# the six rows

def reach_row(claims: list[Claim], cov) -> Row:
    props = ("delta_v_kms", "trip_days_at_min_delta_v", "min_trip_days", "min_trip_delta_v_kms", "n_trajectories")
    picked = _by_source(claims, "reach", props)
    return _row("reach", [_fact(c) for c in picked], any(c.prop == "delta_v_kms" for c in picked), False, cov, [])


def tracking_row(claims: list[Claim], cov, gone: Gone | None = None) -> Row:
    notes: list[str] = []
    orbit = ("condition_code", "data_arc_days", "n_obs_used", "first_obs", "last_obs",
             "n_radar_delay", "n_radar_doppler")
    sb = [c for c in claims if c.source == "jpl-sbdb" and c.prop in orbit]
    sb.sort(key=lambda c: orbit.index(c.prop))
    sb = [c for c in sb if not (c.prop.startswith("n_radar") and not c.value)]
    nh = [c for c in claims if c.source == "jpl-nhats"]
    nh_code = next((c for c in nh if c.prop == "condition_code"), None)
    sb_code = next((c for c in sb if c.prop == "condition_code"), None)
    facts = [_fact(c) for c in sb]
    if sb_code is None and nh_code is not None:
        facts.append(_fact(nh_code))
    elif sb_code is not None and nh_code is not None and sb_code.value != nh_code.value:
        was = next((c.value for c in nh if c.prop == "orbit_id"), None)
        now = next((c.value for c in claims if c.source == "jpl-sbdb" and c.prop == "orbit_id"), None)
        notes.append(
            f"The reachable list was computed from orbit solution {_solution(was)} (condition code {int(nh_code.value)}). "
            f"On {config.DATA_DATE}, JPL's database held solution {_solution(now)} (condition code {int(sb_code.value)})."
        )
    if gone is not None:
        # JPL's list still computes a window for it; a body that no longer exists has none.
        notes.insert(0, gone.text)
    else:
        wn = sorted((c for c in nh if c.prop in WINDOW_PROPS), key=lambda c: WINDOW_PROPS.index(c.prop))
        facts += [_fact(c) for c in wn]
    measured = sb_code is not None or nh_code is not None
    return _row("tracking", facts, measured, False, cov, notes)


def _weak_spitzer(c: Claim, claims: list[Claim]) -> str | None:
    """Why a Spitzer fit does not count, or None: its signal-to-noise, or a fitted reflectivity above 1."""
    if c.source != "spitzer":
        return None
    r = rules()
    if c.snr is not None and c.snr < r.spitzer_min_snr:
        return (f"The Spitzer fit is at signal-to-noise {c.snr:g}, under the {r.spitzer_min_snr:g} "
                "this method asks for; it is not used.")
    pv = c if c.prop == "albedo" else next(
        (o for o in claims if o.source == "spitzer" and o.prop == "albedo" and o.ref == c.ref and o.note == c.note),
        None)
    if pv is not None and isinstance(pv.value, (int, float)) and pv.value > r.max_reflectivity:
        return (f"The Spitzer fit gives a reflectivity of {_show(pv.value)}, above {r.max_reflectivity:g}; "
                "it is not used.")
    return None


def size_row(claims: list[Claim], cov, designations: set[str]) -> Row:
    notes: list[str] = []
    diameters = _by_source(claims, "size", ("diameter_m",))
    usable, rest = [], []
    for c in diameters:
        bad = is_known_bad(c, designations)
        weak = _weak_spitzer(c, claims)
        if bad:
            notes.append(bad.why)
            rest.append(c)
        elif c.kind == "value" and _computed(c):
            notes.append(f"The size from {SPOKEN[c.source]} is computed from other values; it is not a measurement.")
            rest.append(c)
        elif weak:
            notes.append(weak)
            rest.append(c)
        else:
            usable.append(c)
    values = [c for c in usable if c.kind == "value"]
    bounds = [c for c in usable if c.kind != "value"]
    conflict = _sides(values, lambda a, b: not _ranges_apart(a, b), lambda g: " and ".join(dict.fromkeys(
        f"{_size_text(c)} from {SPOKEN[c.source]}" for c in g)))
    facts = [_fact(c) for c in values + bounds] + [_fact(c, used=False) for c in rest]
    h = next((c for c in claims if c.prop == "H" and c.source == "jpl-sbdb"), None) \
        or next((c for c in claims if c.prop == "H"), None)
    if h is not None:
        facts.append(_fact(h))
    else:
        notes.append("JPL lists no absolute magnitude.")
    return _row("size", facts, bool(values), bool(bounds), cov, notes, [conflict] if conflict else [])


def _sides(claims: list, together, said) -> str | None:
    """One sentence for a disagreement, however many sources take part: 'A and B against C.'

    A claim joins the first side whose first member it agrees with (`together`); `said` words a side. None when
    every claim is on one side, or every side is held by the same one source.
    """
    sides: list[list[Claim]] = []
    for c in claims:
        for side in sides:
            if together(side[0], c):
                side.append(c)
                break
        else:
            sides.append([c])
    if len(sides) < 2 or len({c.source for c in claims}) < 2:
        return None
    return _cap(" against ".join(said(side) for side in sides)) + "."


def _size_text(c: Claim) -> str:
    if c.lo is not None and c.hi is not None:
        return f"{_show(c.value)} m ({_show(c.lo)} to {_show(c.hi)})"
    return f"{_show(c.value)} m (no range stated)"


_YEAR = re.compile(r"(?<!\d)(19|20)\d\d(?!\d)")


def _ref_year(c: Claim) -> int | None:
    m = _YEAR.search(c.ref or "")
    return int(m.group(0)) if m else None


def judge_periods(periods: list[Claim], editions: dict[str, str] | None = None) -> dict[int, str]:
    """For each period value claim (by id()), one of: usable, newer, low grade, contradicted.

    method/v0_1/ledger.toml [period]. A graded period is usable at min_grade or better. A period with no grade,
    whichever source holds it, takes the verdict of a graded source that gives the same period (2011 AA37's
    10 hours is in JPL's table with no grade and graded 1+ in the lightcurve database). Failing that, a usable
    graded period that differs rules it out, with one exception, "newer": two sources hold it, and one cites a
    reference dated after the edition of every fixed table that disagrees. With no graded period it is usable.

    editions: {source id: edition date} for the fixed tables; without it nothing is "newer".
    """
    r = rules()
    verdict: dict[int, str] = {}
    graded = [c for c in periods if grade_rank(c.quality) is not None]
    for c in graded:
        verdict[id(c)] = "usable" if grade_rank(c.quality) >= r.min_rank else "low grade"
    ungraded = [c for c in periods if id(c) not in verdict]
    for c in ungraded:
        same = [g for g in graded if not periods_differ(c.value, g.value)]
        against = [g for g in graded if verdict[id(g)] == "usable" and periods_differ(c.value, g.value)]
        if same:
            best = max(grade_rank(g.quality) for g in same)
            verdict[id(c)] = "usable" if best >= r.min_rank else "low grade"
        elif against:
            verdict[id(c)] = "newer" if _newer(c, ungraded, against, editions or {}, r) else "contradicted"
        else:
            verdict[id(c)] = "usable"
    return verdict


def _newer(c: Claim, ungraded: list[Claim], against: list[Claim], editions: dict[str, str], r: Rules) -> bool:
    """ledger.toml [period].superseded."""
    allies = [o for o in ungraded if not periods_differ(c.value, o.value)]
    if len({o.source for o in allies}) < 2:
        return False
    years = [y for y in (_ref_year(o) for o in allies) if y is not None]
    if not years:
        return False
    for g in against:
        edition = editions.get(g.source, "")
        if g.source not in r.fixed_tables or not edition[:4].isdigit() or max(years) <= int(edition[:4]):
            return False
    return True


def _period_who(c: Claim) -> str:
    """A source as a conflict sentence names it. An inference-only source is named without its grade."""
    extra = []
    if c.source == "ssodnet" and c.ref:
        extra.append(c.ref.split(" (")[0].split(";")[0])
    elif c.source == "curated" and c.ref:
        extra.append(c.ref.split(",")[0])
    if grade_rank(c.quality) is not None and LICENCE.get(c.source) != "inference":
        extra.append(f"grade {c.quality}")
    return ", ".join([SPOKEN[c.source]] + extra)


def _period_words(hours: float) -> str:
    """A period in the unit the pages print it in: seconds under 2 min, minutes under 2 h, else hours."""
    if hours < 2.0 / 60.0:
        return f"{_show(hours * 3600.0)} s"
    if hours < 2.0:
        return f"{_show(hours * 60.0)} min"
    return f"{_show(hours)} h"


def period_conflict(in_play: list[Claim]) -> str | None:
    """One sentence for all the periods in play: '250 h (A; B; C) against 2.02 h (D)'.

    Values within the tolerance of the first of a group join it. A group held only by an inference-only source
    prints no number (docs/mvp.md section 3).
    """
    groups: list[list[Claim]] = []
    for c in in_play:
        for g in groups:
            if not periods_differ(g[0].value, c.value):
                g.append(c)
                break
        else:
            groups.append([c])
    if len(groups) < 2:
        return None
    parts = []
    for g in groups:
        shown = next((c for c in g if LICENCE.get(c.source) != "inference"), None)
        who = "; ".join(dict.fromkeys(_period_who(c) for c in g))
        if shown is None:
            parts.append(f"a different period on file in {SPOKEN[g[0].source]}, not shown here")
        else:
            parts.append(f"{_period_words(shown.value)} ({who})")
    return _cap(" against ".join(parts)) + "."


def spin_row(claims: list[Claim], cov, editions: dict[str, str] | None = None) -> Row:
    r = rules()
    notes: list[str] = []
    all_periods = _by_source(claims, "spin", ("period_h",))
    bound_claims = [c for c in all_periods if c.kind != "value"]
    # A number with no grade that another source gives only as a limit is a copy of that limit without its sign.
    copies = [c for c in all_periods if c.kind == "value" and grade_rank(c.quality) is None
              and any(b.source != c.source and same_number(b.value, c.value) for b in bound_claims)]
    periods = [c for c in all_periods if c.kind == "value" and not any(c is x for x in copies)]
    verdict = judge_periods(periods, editions)
    newer = [c for c in periods if verdict[id(c)] == "newer"]
    usable = newer + [c for c in periods if verdict[id(c)] == "usable"]
    rest = [c for c in periods if verdict[id(c)] not in ("usable", "newer")]
    # A bound counts unless its own grade is below the bar.
    bounds = [c for c in bound_claims if grade_rank(c.quality) is None or grade_rank(c.quality) >= r.min_rank]
    rest_bounds = [c for c in bound_claims if not any(c is x for x in bounds)]

    in_play = [c for c in periods if verdict[id(c)] in ("usable", "newer", "contradicted")]
    in_play.sort(key=lambda c: 0 if verdict[id(c)] == "newer" else 1)          # stable: the adopted group first
    conflict = period_conflict(in_play)
    if newer:
        old = dict.fromkeys(SPOKEN[c.source] for c in periods
                            if verdict[id(c)] == "usable" and periods_differ(c.value, newer[0].value))
        notes.append(f"{_cap(' and '.join(dict.fromkeys(SPOKEN[c.source] for c in newer)))} hold a period from a "
                     f"reference dated after the edition of {' and '.join(old)} we hold; the newer period is used.")
    for c in rest:
        if verdict[id(c)] == "contradicted":
            notes.append(f"{_cap(SPOKEN[c.source])} holds a period with no grade that differs from the graded one; "
                         "it is not used.")
    if not usable and periods and any(verdict[id(c)] == "low grade" for c in periods):
        notes.append(f"The period on file is graded below {r.min_grade}, the lowest grade "
                     "the lightcurve database accepts.")
    copy_note = None
    for c in copies:
        b = next(b for b in bound_claims if b.source != c.source and same_number(b.value, c.value))
        copy_note = (f"{_cap(SPOKEN[b.source])} gives this number as {'a lower' if b.kind == 'lower' else 'an upper'} "
                     f"limit; {SPOKEN[c.source]} repeats it without the limit sign")
        notes.append(f"{_cap(SPOKEN[c.source])} repeats a limit from {SPOKEN[b.source]} without its limit sign; "
                     "it is not a measured period.")
    if rest_bounds:
        notes.append(f"The limit on file is graded below {r.min_grade}.")
    amplitudes = _by_source(claims, "spin", ("amplitude_mag",))
    facts = ([_fact(c) for c in usable + bounds] + [_fact(c, used=False) for c in rest + rest_bounds]
             + [_fact(c, used=False, note=copy_note) for c in copies]
             + [_fact(c) for c in amplitudes])
    return _row("spin", facts, bool(usable), bool(bounds), cov, notes, [conflict] if conflict else [])


def surface_row(claims: list[Claim], cov, designations: set[str]) -> Row:
    r = rules()
    notes: list[str] = []
    classes = _by_source(claims, "surface", ("taxonomy",))
    complexes = [c for c in claims if c.prop == "taxonomy_complex" and c.source == "ssodnet"]
    albedos = _by_source(claims, "surface", ("albedo",))
    usable_albedo, rest = [], []
    for c in albedos:
        bad = is_known_bad(c, designations)
        weak = _weak_spitzer(c, claims)
        if bad:
            notes.append(bad.why)
            rest.append(c)
        elif _computed(c):
            rest.append(c)
        elif weak:
            notes.append(weak)
            rest.append(c)
        elif isinstance(c.value, (int, float)) and c.value > r.max_reflectivity:
            notes.append(f"{_cap(SPOKEN[c.source])} gives a reflectivity of {_show(c.value)}, above "
                         f"{r.max_reflectivity:g}; it is not used.")
            rest.append(c)
        else:
            usable_albedo.append(c)

    # The complex of each class: SsODNet's own where it gives one, else from the class letter.
    given = {(c.ref, c.quality): str(c.value) for c in complexes}
    grouped = []
    for c in classes:
        own = given.get((c.ref, c.quality)) if c.source == "ssodnet" else None
        grouped.append((c, class_complex(own or str(c.value))))
    complex_of = {id(c): g for c, g in grouped}
    conflict = _sides(classes, lambda a, b: complex_of[id(a)] == complex_of[id(b)], lambda side: (
        "class " + "/".join(dict.fromkeys(str(c.value) for c in side))
        + " (" + "; ".join(dict.fromkeys(SPOKEN[c.source] for c in side)) + ")"))
    if conflict is None and len(set(complex_of.values())) > 1:      # one source, two schemes, two complexes
        conflict = _cap(" against ".join(dict.fromkeys(
            f"class {c.value} ({c.quality})" for c in classes))) + f". Both are from {SPOKEN[classes[0].source]}."
    measured = bool(classes) or bool(usable_albedo)
    if not measured and any(_computed(c) for c in rest):
        notes.append("The reflectivity on file is computed from the diameter and brightness; it is not a measurement.")
    facts = [_fact(c) for c in classes + usable_albedo] + [_fact(c, used=False) for c in rest]
    return _row("surface", facts, measured, False, cov, notes, [conflict] if conflict else [])


def detected(c: Claim) -> bool:
    """A fitted value at the detection bar or better, from its own stated range."""
    if c.kind != "value" or c.lo is None or c.hi is None or not isinstance(c.value, (int, float)):
        return False
    sigma = (c.hi - c.lo) / 2.0
    # the range was rebuilt from value and sigma, so allow for the last bit of a float
    return sigma > 0 and abs(c.value) / sigma >= rules().detection_sigma * (1.0 - 1e-9)


_SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
_UNIT_SIGNS = {"au/d^2": "au/d²", "au/d2": "au/d²"}


def _solution(orbit) -> str:
    """An orbit solution's name as the pages print it: '118', not 'JPL 118' (JPL's two lists spell it both ways)."""
    return re.sub(r"^JPL\s+", "", str(orbit))


def _push_text(c: Claim) -> str:
    """'−4.6 × 10⁻¹⁴ au/d² (±1σ: −5.26 to −3.94)': three figures, a true minus, the power of ten written out."""
    def sci(v, e):
        return f"{v / 10.0 ** e:.3g}".replace("-", "−")
    unit = _UNIT_SIGNS.get(c.unit, c.unit)
    e = math.floor(math.log10(abs(c.value))) if c.value else 0
    power = f" × 10{str(e).translate(_SUPERSCRIPT)}" if e else ""
    said = f"{sci(c.value, e)}{power} {unit}".strip()
    if c.lo is not None and c.hi is not None:
        said += f" (±1σ: {sci(c.lo, e)} to {sci(c.hi, e)})"
    return said


def push_row(claims: list[Claim], cov) -> Row:
    """ledger.toml [push]: A1, A2 and the drift count at the detection bar. A3, the out-of-plane term, is listed
    and never sets the state. A density SsODNet computed is listed and not used."""
    r = rules()
    notes: list[str] = []
    fitted = _by_source(claims, "push", ("A1", "A2", "A3", "drift_au_per_myr"))
    usable = [c for c in fitted if c.prop in r.push_counts and detected(c)]
    rest = [c for c in fitted if not any(c is u for u in usable)]
    density = _by_source(claims, "push", ("density_kgm3",))
    counted = [c for c in fitted if c.prop in r.push_counts]
    if counted and not usable:
        notes.append(f"No fitted value reaches {r.detection_sigma:g}σ.")
    if any(c.prop not in r.push_counts for c in fitted):
        notes.append("A3 is the out-of-plane term, not a push from sunlight; it is listed and not counted.")
    if any(c.source == "jpl-sbdb" for c in fitted):
        notes.append("JPL's bulk values are rounded to two figures and carry no force law.")
    if any(_computed(c) for c in density):
        notes.append("The density from SsODNet is computed from other values; it is not a measurement.")
    conflicts = []
    for i, a in enumerate(usable):
        for b in usable[i + 1:]:
            if a.prop == b.prop and a.source != b.source and _ranges_apart(a, b):
                conflicts.append(f"{_cap(SPOKEN[a.source])} gives {LABEL[a.prop]} {_push_text(a)}; "
                                 f"{SPOKEN[b.source]} gives {_push_text(b)}.")
    facts = ([_fact(c) for c in usable] + [_fact(c, used=False) for c in rest]
             + [_fact(c, used=not _computed(c)) for c in density])
    return _row("push", facts, bool(usable), False, cov, notes, list(dict.fromkeys(conflicts)))


# --------------------------------------------------------------------------
# records

def collect() -> tuple[dict[str, list[Claim]], dict[str, dict[tuple[str, str], Coverage]]]:
    """Every source's claims and coverage, grouped by object key."""
    claims: dict[str, list[Claim]] = {}
    coverage: dict[str, dict[tuple[str, str], Coverage]] = {}
    for source_id, module in ingest.modules().items():
        cs, cov = module.load()
        for c in cs:
            if c.source != source_id:
                raise ValueError(f"{module.__name__} produced a claim for source {c.source!r}")
            claims.setdefault(c.key, []).append(c)
        for c in cov:
            if c.row not in ROWS or c.source != source_id:
                raise ValueError(f"{module.__name__} produced coverage for {c.row!r}/{c.source!r}")
            coverage.setdefault(c.key, {})[(c.row, c.source)] = c
    return claims, coverage


def editions() -> dict[str, str]:
    """{source id: edition date} for the fixed tables of ledger.toml [fixed_tables]."""
    from longshot import sources
    listed = sources.load()
    return {s: listed[s].edition for s in rules().fixed_tables if s in listed}


def build_record(ident: ids.Identity, claims: list[Claim], cov: dict[tuple[str, str], Coverage],
                 table_editions: dict[str, str] | None = None) -> ObjectRecord:
    designations = {ident.pdes, ident.designation}
    gone = is_gone(designations)
    rows = {
        "reach": reach_row(claims, cov),
        "tracking": tracking_row(claims, cov, gone),
        "size": size_row(claims, cov, designations),
        "spin": spin_row(claims, cov, table_editions),
        "surface": surface_row(claims, cov, designations),
        "push": push_row(claims, cov),
    }
    assert tuple(rows) == ROWS and all(r.state in STATES for r in rows.values())
    used = {f.source for r in rows.values() for f in r.facts}
    return ObjectRecord(
        key=ident.key, designation=ident.designation, name=ident.name, number=ident.number,
        aliases=list(ident.aliases), populations=["reachable"], data_date=config.DATA_DATE, method=config.METHOD,
        rows=rows, sources=[s for s in ingest.SOURCE_IDS if s in used],
        gone={"date": gone.date, "text": gone.text, "evidence": gone.evidence} if gone else None,
    )


def counts(records: list[ObjectRecord]) -> dict[str, dict[str, int]]:
    out = {row: {state: 0 for state in STATES} for row in ROWS}
    for r in records:
        for row in ROWS:
            out[row][r.rows[row].state] += 1
    return out


def format_counts(records: list[ObjectRecord]) -> str:
    table = counts(records)
    lines = [f"{len(records)} reachable asteroids, data of {config.DATA_DATE}",
             f"{'row':<10}" + "".join(f"{s:>11}" for s in STATES)]
    for row in ROWS:
        lines.append(f"{row:<10}" + "".join(f"{table[row][s]:>11}" for s in STATES))
    return "\n".join(lines)


def dumps(record: ObjectRecord) -> str:
    return json.dumps(dataclasses.asdict(record), ensure_ascii=False, separators=(",", ":"))


def write(records: list[ObjectRecord], path: Path | None = None) -> Path:
    """One ObjectRecord per line. Written whole, then moved into place."""
    path = Path(path or config.BUILD / "ledger.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            fh.write(dumps(r) + "\n")
    os.replace(tmp, path)
    return path


def build(write_file: bool = True, verbose: bool = False) -> list[ObjectRecord]:
    """The ledger for the reachable population, numbered objects first, then by designation."""
    from longshot.ingest import nhats
    index = ids.load()
    claims, coverage = collect()
    table_editions = editions()
    records = [build_record(index.identity(key), claims.get(key, []), coverage.get(key, {}), table_editions)
               for key in nhats.reachable()]
    if write_file:
        write(records)
    if verbose:
        print(format_counts(records))
    return records


# --------------------------------------------------------------------------
# reading a record

def fact(row: Row, label: str) -> Fact | None:
    """The first fact in a row with this label (see LABEL), or None."""
    return next((f for f in row.facts if f.label == label), None)


def adopted(row: Row) -> Fact | None:
    """The value or bound a measured or limit row rests on."""
    return row.facts[0] if row.state in ("measured", "limit") and row.facts else None


def window(record: ObjectRecord) -> dict | None:
    """The next observing window as dated facts, or None when JPL lists none.

    {start, end, peak_mag, pointable, as_of}: the shape docs/mvp.md gives observe.window.
    """
    row = record.rows["tracking"]
    start, end = fact(row, "window start"), fact(row, "window end")
    if start is None or end is None:
        return None
    mag, pointing = fact(row, "window peak brightness"), fact(row, "window pointing")
    return {
        "start": start.value, "end": end.value, "peak_mag": mag.value if mag else None,
        "pointable": bool(pointing and pointing.value == "pointable"), "as_of": record.data_date,
    }


def main(argv: list[str] | None = None) -> int:
    build(write_file=True, verbose=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
