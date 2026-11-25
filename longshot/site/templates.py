"""HTML fragments as Python functions. Standard library only, no clock, no network.

Everything here takes plain dicts (gen.py converts the dataclasses once) and
returns strings. Text from upstream is escaped at the point it is printed.

One set of state marks everywhere (glyph): measured, an unbroken rock outline that
glows; limit, a dashed outline; not measured, a small grey dot; not checked, a dashed
ring. Mission results: pass, a heavy outline; untested, a dot; fail, a cross.

Interface copy goes without parentheses: B612 draws them square (unparen). The
site's own sentences, set in the serif, keep theirs.
"""
from __future__ import annotations

import html
import math
import re
from datetime import date as _date

from longshot import draws as draws_mod
from longshot import ledger as ledger_mod
from longshot import shape as shape_mod

SITE = "longshot"

ROWS = ("reach", "tracking", "size", "spin", "surface", "push")
ROW_LABELS = {
    "reach": "Reach", "tracking": "Tracking", "size": "Size",
    "spin": "Spin", "surface": "Surface", "push": "Sunlight push",
}
STATE_WORDS = {
    "measured": "Measured", "limit": "Limit only",
    "prior": "Not measured", "unchecked": "Not checked",
}
STATUS_WORDS = {"pass": "Pass", "untested": "Untested", "fail": "Fail"}
# One name per mission: the field's filter, an entry's Missions section, the table view's columns.
MISSION_LABELS = {"surface": "Surface work", "capture": "Whole-body capture"}
METHOD_PAGE = "method.html"
RUNG_LABELS = {
    "found_again": "Find it again", "reached": "Reach it",
    "workable": "Work on it", "anything_in_it": "Anything in it",
    "brought_back": "Bring any back",
}
RUNG_WORDS = {"measured": "Measured", "prior": "From what is typical", "unknown": "Unknown"}
CLASS_LABELS = {"S": "S, stony", "C": "C, dark and carbon-rich", "X": "X, metal or rock", "other": "other"}
CLASS_WORDS = {"S": "Stony", "C": "Carbon-rich", "X": "Metal or rock"}      # draws.class_group's groups
SPIN_KEYS = ("p_fast_2_2h", "p_under_1h", "p_under_10min")    # the record's shares, one per line in priors.toml


def spin_lines(thresholds_h) -> tuple:
    """((share key, its line in words), ...) from priors.toml [spin].thresholds_h: '2.2 h', '1 h', '10 min'."""
    def words(h):
        return f"{round(h, 2):g} h" if h >= 1 else f"{round(h * 60, 1):g} min"
    return tuple(zip(SPIN_KEYS, (words(h) for h in thresholds_h)))


SPIN_SHARES = spin_lines((2.2, 1.0, 1 / 6))     # gen.write_site sets it from the method files
LICENCE_WORDS = {
    "open": "Shown in full",
    "single": "Single values, with citation",
    "inference": "Feeds estimates; its values are not shown",
}
POINTER = "on file, not shown here"
GATE_BASIS = {"measured": "measured", "prior": "typical for its brightness"}
GATE_ROW = {"findable": "tracking", "size": "size", "spin": "spin", "mass": "size"}

# A fact's label is its stable id in the ledger (longshot.ledger.LABEL). These are the words printed for it,
# so one thing has one name on the page: the gates and the ladder say "orbit code" and "reflectivity".
FACT_WORDS = {
    "condition code": "orbit code",
    "arc": "observed over",
    "albedo": "reflectivity",
    "A1": "radiation pressure, A1",
    "A2": "drift, A2",
    "A3": "out of plane, A3",
    "drift": "drift of the orbit",
}

# Upstream method tags, in words. A tag not listed is printed as it is.
GRADE_WORDS = {
    "space": "spacecraft",
    "neatm": "thermal model",
    "tpm": "thermophysical model",
    "radar": "radar",
    "polarimetry": "polarimetry",
    "computed": "computed",
    "astrometry(o)": "optical astrometry",
    "astrometry(o+r)": "optical and radar astrometry",
    "yarkovsky": "from its drift",
    "srp": "from radiation pressure",
    "yarkovsky+srp": "from drift and radiation pressure",
}
_TAXONOMY = re.compile(r"^(?P<scheme>.+?) (?P<how>Spec|Phot) (?P<band>VISNIR|VIS|NIR)$")
_HOW = re.compile(r"^(?P<how>Spec|Phot)\b[ ,:]*(?P<rest>.*)$")     # a hand-entered class: how, then the detail
_BANDS = {"VIS": "visible", "NIR": "near-infrared", "VISNIR": "visible and near-infrared"}
_HOW_WORDS = {"Spec": "spectrum", "Phot": "colours"}

UNITS = {
    "km/s": "km/s", "kms": "km/s", "m": "m", "km": "km", "h": "h", "min": "min",
    "s": "s", "d": "d", "day": "d", "days": "d", "mag": "mag", "V mag": "mag", "%": "%", "date": "",
    "t": "t", "kg": "kg", "au": "au", "deg": "°",
    "au/d^2": "au/d²", "au/d2": "au/d²", "au/d²": "au/d²", "au/Myr": "au/Myr",
    "kg/m^3": "kg/m³", "kg/m3": "kg/m³", "m^2/kg": "m²/kg", "m2/kg": "m²/kg",
}
TIME_S = {"s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0, "day": 86400.0, "days": 86400.0}

_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATES = re.compile(r"(\d{4}-\d\d-\d\d)")
_U_CODE = re.compile(r"^[0-3][+\-–−]?$")
_ALBEDO = re.compile(r"albedo|reflectiv", re.I)


def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def cap(s) -> str:
    s = "" if s is None else str(s)
    return s[:1].upper() + s[1:]


def unparen(s) -> str:
    """'Lee+2022 (2022A&A...661L...3L)' -> 'Lee+2022, 2022A&A...661L...3L': B612's parentheses are square."""
    return re.sub(r"\s*\(([^()]*)\)", r", \1", "" if s is None else str(s))


def nowrap_dates(text: str) -> str:
    """Escaped text in which a date never breaks across lines."""
    return _DATES.sub(r'<span class="nb">\1</span>', esc(text))


_URL_IN = re.compile(r"https?://\S+")
# The method files say where each figure comes from inside the project (a research note, a script, a review).
# The page is for visitors: it keeps the published sources and the reasoning, and leaves out every clause that
# only points into the project. The files themselves keep the full trail.
_INTERNAL = re.compile(
    r"docs/|data/|tools/|build/|method/|registry/|AGENTS\.md|\b[\w.-]+\.(?:md|py|toml|txt|jsonl)\b"
    r"|\b[a-z0-9]+_[a-z0-9_]+\b|saved copy|project file|\breview of 20\d\d|\bthe plan\b|\bplan's\b|\bWP\d",
    re.I)
# A path or file name into the project, with what locates a line in it: 'docs/research/x.md section 3',
# 'priors.toml [density]', 'AGENTS.md, traps'.
_PATHREF = re.compile(
    r"(?:\s+(?:in|from|see|per|as)\s+(?:the\s+)?|,?\s*)"
    r"(?:(?:docs|data|tools|method|registry|build)/[\w./-]+|\b[\w.-]+\.(?:md|py|toml|txt|jsonl)\b)"
    r"(?:\s*\[[^\]]*\])?(?:\s+\d+(?:\.\d+)*\b)?"
    r"(?:,?\s+(?:section|sections|item|row|rows|line|lines|table|verdict|objection|traps|Terms|Appendix)\b"
    r"(?:\s+[\w–-]+(?:\.\d+)*(?:\s+and\s+\d[\w–-]*(?:\.\d+)*)?)?)?")
# A clause that opens with a path: what follows its colon is the quote or the finding; with no colon it is all pointer.
_OPENS_WITH_PATH = re.compile(r"^\s*(?:(?:docs|data|tools|method|registry|build)/|[\w.-]+\.(?:md|py|toml|txt|jsonl)\b|AGENTS\.md)")
_CLAUSE = re.compile(r"((?<=[.;])\s+)")
_PAREN = re.compile(r"\s*\(([^()]*)\)")
_ASIDE = re.compile(r"\s+\(([^()]*)\)(?!\^)")


def _internal(text: str) -> bool:
    return bool(_INTERNAL.search(_URL_IN.sub("", text)))


def public_text(text) -> str:
    """A line from a method file as a visitor reads it: no paths into the project, no brackets (B612 draws
    them square), kg/m³ and ± in place of kg/m3 and +/-."""
    text = "" if text is None else str(text)
    text = _PAREN.sub(lambda m: "" if _internal(m[1]) else m[0], text)
    kept, dropped = [], False
    for x in _CLAUSE.split(text)[::2]:
        cut = False
        if _OPENS_WITH_PATH.match(x):
            if ":" not in x:
                dropped = True
                continue
            x, cut = x.split(":", 1)[1], True
        was, x = x, _PATHREF.sub("", x)
        if x != was and re.search(r":\s*[.;]?\s*$", x):    # a label whose whole content was a pointer
            dropped = True
            continue
        x = re.sub(r"\s+(?:of|in|from|see|per|as|and)(?=[.;,]?$)", "", x.strip())
        x = re.sub(r"\s*([;,:.])(?:\s*[;,:])+", r"\1", x).strip(" ,:")
        if not x.strip(" ;.") or _internal(x):
            dropped = True
            continue
        if kept:
            if kept[-1][-1] == ";" and dropped and x[:1].isupper():
                kept[-1] = kept[-1][:-1] + "."
            elif kept[-1][-1] not in ".;?!'":
                kept[-1] += "."
            if cut and kept[-1][-1] == ".":
                x = x[:1].upper() + x[1:]
        kept.append(x)
        dropped = False
    text = " ".join(kept).rstrip(";")
    text = _ASIDE.sub(r", \1", re.sub(r"^\(([^()]*)\)", r"\1", text))
    return text.replace("kg/m3", "kg/m³").replace("+/-", "±")


# ---------------------------------------------------------------- numbers

def is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def num(x, sig: int = 4) -> str:
    """A number to `sig` significant figures, no trailing zeros, U+2212 for minus."""
    if not is_num(x):
        return ""
    x = float(x)
    if x == 0:
        return "0"
    a = abs(x)
    e = math.floor(math.log10(a))
    if e < -4 or e >= 15:
        m = round(a / 10.0 ** e, sig - 1)
        if m >= 10:
            m, e = m / 10, e + 1
        s = f"{m:.{sig - 1}f}".rstrip("0").rstrip(".") + " × 10" + str(e).translate(_SUP)
    else:
        r = float(f"{a:.{sig}g}")
        dec = max(0, sig - 1 - math.floor(math.log10(r)))
        s = f"{r:,.{dec}f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
    return ("−" if x < 0 else "") + s


def count(n) -> str:
    return f"{int(n):,}"


def hundredths(p) -> int:
    """A share 0..1 as a count of 100, halves rounded up."""
    return math.floor(p * 100 + 0.5 + 1e-9)


def pct(p) -> str:
    """A share 0..1 as a whole percentage, halves rounded up, that never rounds to 0 or 100 falsely."""
    if not is_num(p):
        return ""
    if 0 < p < 0.005:
        return "under 1%"
    if 0.995 <= p < 1:
        return "over 99%"
    return f"{hundredths(p)}%"


def chance(p) -> str:
    """A chance counted from draws. None passing, or all, is still not certainty: 'under 1%', 'over 99%'."""
    if not is_num(p):
        return ""
    if p < 0.005:
        return "under 1%"
    if p >= 0.995:
        return "over 99%"
    return pct(p)


def usd(x) -> str:
    if not is_num(x):
        return ""
    for size, word in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million"), (1e3, "thousand")):
        if abs(x) >= size:
            return f"${num(x / size, 2)}\u00a0{word}"
    return f"${num(x, 2)}"


def with_unit(n: str, unit: str) -> str:
    if not unit:
        return n
    return n + unit if unit in ("%", "°") else f"{n}\u00a0{unit}"


def scale_for(row_id: str, label: str, unit: str, ref) -> tuple[float, str]:
    """The factor and unit to print a quantity in, chosen from a reference value."""
    unit = (unit or "").strip()
    if not is_num(ref):
        return 1.0, UNITS.get(unit, unit)
    if unit in TIME_S and row_id == "spin":
        sec = abs(ref) * TIME_S[unit]
        out = "s" if sec < 120 else "min" if sec < 7200 else "h"
        return TIME_S[unit] / TIME_S[out], out
    if unit == "m" and abs(ref) >= 1000:
        return 0.001, "km"
    if unit == "km" and 0 < abs(ref) < 1:
        return 1000.0, "m"
    if unit == "" and row_id == "surface" and _ALBEDO.search(label or ""):
        return 100.0, "%"
    return 1.0, UNITS.get(unit, unit)


def _decimals(s: str) -> int:
    return len(s.split(".", 1)[1]) if "." in s and "×" not in s else 0


def span(lo, hi, unit: str, sig: int = 4) -> str:
    """'28–40 m', '23.88–24.50 mag': both ends to the same decimals. Negative ends are joined with 'to' so
    the dash is not read as a sign."""
    a, b = num(lo, sig), num(hi, sig)
    d = max(_decimals(a), _decimals(b))
    if _decimals(a) and _decimals(b) and "×" not in a + b:
        a, b = (x + ("" if "." in x else ".") + "0" * (d - _decimals(x)) for x in (a, b))
    joiner = " to " if (lo < 0 or hi < 0 or "×" in a or "×" in b) else "–"
    return with_unit(f"{a}{joiner}{b}", unit)


def _scaled(x) -> tuple[str, str]:
    """(figures, 'million' | 'billion' | ''): words above a million so the digits stay readable."""
    for size, word in ((1e9, "billion"), (1e6, "million")):
        if abs(x) >= size:
            return num(x / size, 2), word
    return num(x, 2), ""


def amount(lo, hi, unit: str) -> str:
    """A range of mass, both ends in the high end's scale: '13,000–550,000 t', '0.071–3.6 million t'."""
    b, wb = _scaled(hi)
    size = {"billion": 1e9, "million": 1e6}.get(wb, 1.0)
    a = num(lo / size, 2)
    return f"{a}–{b}" + (f"\u00a0{wb}" if wb else "") + f"\u00a0{unit}"


def date(s) -> str:
    return f"<time>{esc(s)}</time>"


def u(unit: str) -> str:
    """A unit beside a value, in the label grey."""
    return f'<span class="u">{esc(unit)}</span>' if unit else ""


# ---------------------------------------------------------------- sources

def licence_of(sources: dict, sid: str):
    s = sources.get(sid)
    return s.get("licence") if s else None


def public(fact: dict, sources: dict) -> dict | None:
    """The fact as the page may print it, or None when it may only be pointed to.

    The licence rule (docs/mvp.md section 3): a value or grade from an "inference" source is
    never printed under that source's name. Where another source states the same value, that
    source's own line shows it.
    """
    return None if licence_of(sources, fact.get("source", "")) == "inference" else fact


def displayable(fact: dict, sources: dict) -> bool:
    return public(fact, sources) is not None


def source_name(sources: dict, sid: str) -> str:
    """A source's name as interface copy: 'Asteroid Lightcurve Database, LCDB' (unparen)."""
    s = sources.get(sid)
    return unparen(s.get("name") or sid) if s else sid


def short_name(sources: dict, sid: str) -> str:
    """A source's short name for a crowded column: what its name gives in parentheses, else the name."""
    s = sources.get(sid)
    m = re.search(r"\(([^()]+)\)\s*$", (s or {}).get("name") or "")
    return m[1] if m else source_name(sources, sid)


def source_link(sources: dict, sid: str) -> str:
    if not sid:
        return "derived"
    if sid not in sources:
        return esc(sid)
    return f'<a href="#src-{esc(sid)}">{esc(source_name(sources, sid))}</a>'


def unreliable(quality) -> bool:
    """A lightcurve quality code of 1 (or 0): the period may be completely wrong."""
    q = (quality or "").strip()
    return bool(_U_CODE.match(q)) and q[0] in "01"


def grade(row_id: str, quality) -> str:
    """A grade or method tag as the page prints it (escaped)."""
    q = (quality or "").strip()
    if not q:
        return ""
    if row_id == "spin" and _U_CODE.match(q):
        return f"quality U {esc(q)}" + (", unreliable" if unreliable(q) else "")
    m = _HOW.match(q)
    if m:
        return esc(_HOW_WORDS[m["how"]] + (f": {m['rest']}" if m["rest"] else ""))
    return esc(", ".join(_tag(part.strip()) for part in q.split(",")))


def _tag(tag: str) -> str:
    """One upstream tag in words; a tag with no words here is printed as it is."""
    if tag.casefold() in GRADE_WORDS:
        return GRADE_WORDS[tag.casefold()]
    m = _TAXONOMY.match(tag)
    if m:
        return f"{m['scheme']} class, {_BANDS[m['band']]} {_HOW_WORDS[m['how']]}"
    return tag


def label(row_id: str, name) -> str:
    """A fact's label as the page prints it (not escaped)."""
    name = "" if name is None else str(name)
    return FACT_WORDS.get(name, name)


# ---------------------------------------------------------------- reading a record

def _first(facts, pred):
    for f in facts:
        if pred(f):
            return f
    return None


def delta_v(rec: dict):
    f = _first(rec["rows"].get("reach", {}).get("facts", []),
               lambda f: is_num(f.get("value")) and UNITS.get(f.get("unit", "")) == "km/s")
    return f["value"] if f else None


def trip_days(rec: dict):
    """The round trip at the lowest delta-v, in days: the reach row's first count of days."""
    f = _first(rec["rows"].get("reach", {}).get("facts", []),
               lambda f: is_num(f.get("value")) and UNITS.get(f.get("unit", "")) == "d")
    return f["value"] if f else None


def first_observed(rec: dict):
    f = _first(rec["rows"].get("tracking", {}).get("facts", []), lambda f: f.get("label") == "first observed")
    return f["value"] if f else None


def size_m(rec: dict) -> dict | None:
    """summary.size_m's q05, q50 and q95 when all three are there: the size a rock is placed by."""
    q = (rec.get("summary") or {}).get("size_m") or {}
    if all(is_num(q.get(k)) and q[k] > 0 for k in ("q05", "q50", "q95")):
        return {k: q[k] for k in ("q05", "q50", "q95")}
    return None


def placed(rec: dict) -> bool:
    """Whether the field draws it: a delta-v and a size to place it by (export.field_row's rule)."""
    return delta_v(rec) is not None and size_m(rec) is not None


def _metres(f):
    u = f.get("unit", "")
    return {"m": 1.0, "km": 1000.0}.get(u)


def _from_fact(f: dict, state: str) -> dict:
    k = _metres(f)
    lo, hi = f.get("lo"), f.get("hi")
    ok = is_num(lo) and is_num(hi) and 0 < lo <= f["value"] <= hi and lo < hi
    return {"mid": f["value"] * k, "lo": lo * k if ok else None, "hi": hi * k if ok else None,
            "state": state, "kind": f.get("kind", "value"), "source": f.get("source", ""),
            "quality": f.get("quality")}


def _from_quantiles(q: dict, k: float) -> dict | None:
    if not (k and is_num(q.get("q50")) and q["q50"] > 0):
        return None
    ok = is_num(q.get("q05")) and is_num(q.get("q95")) and 0 < q["q05"] <= q["q50"] <= q["q95"]
    return {"mid": q["q50"] * k, "lo": q["q05"] * k if ok else None, "hi": q["q95"] * k if ok else None,
            "state": "prior", "kind": "value", "source": "", "quality": None}


def _size_facts(rec: dict, sources: dict, only=None):
    """(the size row's state, its usable diameters or bounds the page may print), adopted first."""
    row = rec["rows"].get("size", {})
    facts = row.get("facts", [])
    state = row.get("state")
    kinds = {"measured": ("value",), "limit": ("upper", "lower")}.get(state, ())
    return state, [f for f in facts
                   if f.get("kind", "value") in kinds and is_num(f.get("value")) and used(f)
                   and _metres(f) and f["value"] > 0 and displayable(f, sources)
                   and (only is None or licence_of(sources, f.get("source", "")) == only)]


def size_of(rec: dict, sources: dict) -> dict | None:
    """The size to draw: {lo, mid, hi (metres; lo and hi may be None), state, kind, source, quality}.

    The row's state decides. Measured: the first diameter value the page may print
    (the ledger puts the adopted one first). Limit: the first bound. Otherwise the
    summary's quantiles, then the row's prior. None when nothing gives a size.
    """
    state, found = _size_facts(rec, sources)
    if found:
        return _from_fact(found[0], state)
    q = (rec.get("summary") or {}).get("size_m") or {}
    if is_num(q.get("q50")):
        return _from_quantiles(q, 1.0)
    q = rec["rows"].get("size", {}).get("prior") or {}
    return _from_quantiles(q, _metres(q))


def open_size_of(rec: dict, sources: dict) -> dict | None:
    """The size a page that lists many asteroids may print: open and derived values only.

    The rule of the field file (docs/mvp.md section 5), so a list and the field give one size.
    Not measured: the range from open values alone (summary.size_open_m) where the record
    carries one, else the entry's own range. Measured from an open source: that value.
    Measured from a source licensed for single values: JPL's diameter where it has one, else
    summary.size_open_m with `withheld` set, since the entry's own value was left out.
    """
    own = size_of(rec, sources)
    if own is None:
        return None
    derived = _from_quantiles((rec.get("summary") or {}).get("size_open_m") or {}, 1.0)
    if own["state"] == "prior":
        return {**(derived or own), "withheld": False}
    if licence_of(sources, own["source"]) == "open":
        return {**own, "withheld": False}
    state, found = _size_facts(rec, sources, only="open")
    if found:
        return {**_from_fact(found[0], state), "withheld": False}
    out = derived or {"mid": None, "lo": None, "hi": None, "kind": "value", "source": ""}
    return {**out, "state": own["state"], "withheld": True}


def used(f: dict) -> bool:
    """False for a value the ledger keeps on file and does not count (Fact.used)."""
    return f.get("used", True) is not False


def _is_period(f: dict) -> bool:
    return (f.get("kind", "value") == "value" and is_num(f.get("value"))
            and f["value"] > 0 and f.get("unit") in TIME_S)


def not_checked(row: dict, sources: dict) -> str:
    """'SsODNet, Pravec': the sources a row was not checked against; '' when all were."""
    return ", ".join(source_name(sources, s) for s in row.get("unchecked") or [])


OPEN_PERIOD_SOURCE = "jpl-sbdb"        # the one period the field file may carry (longshot/export.py)


def shown_period(rec: dict, sources: dict) -> tuple[dict | None, str]:
    """(the period fact the page shows and turns the rock by, reason). The fact is set only when the
    spin row is measured, its sources do not disagree, and a period the page may print agrees with
    the adopted one (the row's first, within the ledger's tolerance). JPL's period is taken where it is
    one of those, so the entry turns at the rate the field turns at. Otherwise the reason says why not:
    and never "no measured period" while a source for the row was not checked."""
    row = rec["rows"].get("spin", {})
    on_file = [f for f in row.get("facts", []) if _is_period(f)]
    periods = [f for f in on_file if used(f)]
    if row.get("state") != "measured" or not periods:
        if row.get("unchecked") or row.get("state") == "unchecked":
            names = not_checked(row, sources)
            return None, "period not checked" + (f": {names}" if names else "")
        return None, "no period good enough to use" if on_file else "no measured period"
    if row.get("conflicts"):
        return None, "sources disagree on the period"
    seconds = lambda f: f["value"] * TIME_S[f["unit"]]
    adopted = seconds(periods[0])
    agree = [f for f in periods if displayable(f, sources) and not ledger_mod.periods_differ(adopted, seconds(f))]
    if not agree:
        return None, POINTER
    return _first(agree, lambda f: f.get("source") == OPEN_PERIOD_SOURCE) or agree[0], ""


def period_of(rec: dict, sources: dict) -> tuple[float | None, str]:
    """(seconds, reason): shown_period's period in seconds."""
    f, why = shown_period(rec, sources)
    return (f["value"] * TIME_S[f["unit"]], "") if f else (None, why)


# ---------------------------------------------------------------- marks

GLYPHS = ("measured", "limit", "prior", "unchecked", "unknown", "pass", "untested", "fail")


def glyph(state: str, said: str = "") -> str:
    """The mark for a row state or a mission status, drawn as the field draws it.

    One empty element: style.css draws each mark (.g-measured and the rest), so a page that lists two
    thousand asteroids carries a class name per mark, not an outline. `said` gives it the state in words
    for a reader that does not see it; otherwise the words beside it say it and the mark is hidden."""
    state = state if state in GLYPHS else "unchecked"
    aria = f'role="img" aria-label="{esc(said)}"' if said else 'aria-hidden="true"'
    return f'<i class="g g-{state}" {aria}></i>'


def state_tag(state: str, word: str | None = None) -> str:
    word = word or STATE_WORDS.get(state) or STATUS_WORDS.get(state) or cap(state)
    return f'<span class="st st-{esc(state)}">{glyph(state)}{esc(word)}</span>'


def shape(key: str) -> list[tuple[float, float]]:
    """The outline the field draws for this key, in units of half the rock's size (longshot/shape.py)."""
    return shape_mod.outline(key)


def _points(pts, r: float, cx: float = 0.0, cy: float = 0.0) -> str:
    return " ".join(f"{cx + x * r:.1f},{cy + y * r:.1f}" for x, y in pts)


def _notched(key: str) -> float:
    """How deep an outline's deepest notch is: the farthest point over the nearest."""
    radii = [math.hypot(x, y) for x, y in shape(key)]
    return max(radii) / min(radii)


def _aspect(key: str) -> float:
    """An outline's width over its height, the narrower over the wider, as it is drawn (unturned)."""
    pts = shape(key)
    w = max(x for x, _ in pts) - min(x for x, _ in pts)
    h = max(y for _, y in pts) - min(y for _, y in pts)
    return min(w, h) / max(w, h)


# The site's mark is one of the field's rocks: of the keys longshot0 to longshot199 whose outline is about as wide
# as it is tall, the one with the deepest notch, so it reads as a rock at 20 px and not as a blob or a sliver.
MARK_KEY = max((f"{SITE}{i}" for i in range(200) if _aspect(f"{SITE}{i}") >= 0.9),
               key=lambda k: (round(_notched(k), 2), _aspect(k)))


def rock_mark() -> str:
    """The site's mark, scaled so its farthest point touches the box."""
    pts = shape(MARK_KEY)
    p = _points(pts, 9.5 / max(math.hypot(x, y) for x, y in pts))
    return (f'<svg class="rockmark" viewBox="-10 -10 20 20" aria-hidden="true">'
            f'<polygon class="halo" points="{p}"/><polygon points="{p}"/></svg>')


def _nice_near(x: float) -> float:
    """A round length (1, 2 or 5 times a power of ten) near x."""
    e = math.floor(math.log10(x))
    return min((m * 10.0 ** k for k in (e - 1, e, e + 1) for m in (1, 2, 5)), key=lambda v: abs(math.log(v / x)))


def _seconds(sec: float) -> str:
    """A CSS duration that keeps four figures and never prints an exponent."""
    return f"{float(f'{sec:.4g}'):.3f}".rstrip("0").rstrip(".") + "s"


NESTED_FROM = 1.25      # the low and high outlines are drawn when the range spans this ratio or more
ONE_SIGMA = "1σ"        # what a stated range beside a measured value is (method/v0_1/missions.toml [rules.decide])
ROCK_BOX = 240


def rock(rec: dict, sources: dict) -> str:
    """The asteroid to scale: its size range as nested outlines, turning at its measured rate."""
    name = rec.get("name") or rec["designation"]
    size = size_of(rec, sources)
    period, why = period_of(rec, sources)
    if rec.get("gone"):                     # drawn as it was last known; nothing is left to turn
        period, why = None, "it no longer exists"
    if size is None:
        return '<figure class="rockfig"><p class="none">No size on file: not drawn</p></figure>'
    srow = rec["rows"].get("size", {})
    state = size["state"]
    if state == "prior" and srow.get("state") == "unchecked":
        state = "unchecked"
    outer = size["hi"] or size["mid"]
    half = ROCK_BOX / 2
    px = (half - 10) / (outer / 2)          # as the field: an outline's longest radius is half the size
    pts = shape(rec["key"])
    nested = bool(size["lo"] and size["hi"] and size["hi"] / size["lo"] >= NESTED_FROM)

    def poly(d, cls):
        return f'<polygon class="{cls}" points="{_points(pts, d / 2 * px)}"/>'

    shapes = []
    if state == "measured":
        shapes.append(poly(size["mid"], "halo"))
    if nested:
        shapes.append(poly(size["hi"], "edge"))
    shapes.append(poly(size["mid"], f"mid s-{state}"))
    if nested:
        shapes.append(poly(size["lo"], "edge in"))

    k, unit = scale_for("size", "", "m", outer)
    show = lambda m, sig=2: with_unit(num(m * k, sig), unit)
    if state == "measured":
        rows = ([("High, 1σ", show(size["hi"], 3)), ("Measured", show(size["mid"], 3)), ("Low, 1σ", show(size["lo"], 3))]
                if size["lo"] else [("Measured", show(size["mid"], 3))])
        alt = f"{name}, {show(size['mid'], 3)} across"
    elif state == "limit":
        word = "Under" if size["kind"] == "upper" else "Over"
        rows = [(word, show(size["mid"], 3))]
        alt = f"{name}, {word.lower()} {show(size['mid'], 3)} across"
    else:
        rows = ([("Outer, 95th", show(size["hi"])), ("Middle", show(size["mid"])), ("Inner, 5th", show(size["lo"]))]
                if size["lo"] else [("Middle", show(size["mid"]))])
        held = not_checked(srow, sources) if state == "unchecked" else ""
        alt = (f"{name}, size not checked" + (f": {held}" if held else "") if state == "unchecked"
               else f"{name}, size not measured") + ", the outline typical at its brightness"
    if period:
        pk, punit = scale_for("spin", "", "s", period)
        alt += f"; turns once in {with_unit(num(period * pk), punit)}, at its measured rate"
        turn = f' class="turn" style="animation-duration:{_seconds(period)}"'
    else:
        alt += f"; not turning: {why}"
        turn = ""
    bar = _nice_near(outer / 4)
    bk, bunit = scale_for("size", "", "m", bar)
    w = bar * px
    y = half + 6
    scale = (f'<g class="scale"><path d="M{-half + 10:.1f} {y}h{w:.1f}M{-half + 10:.1f} {y - 4}v8M{-half + 10 + w:.1f} {y - 4}v8"/>'
             f'<text x="{-half + 10:.1f}" y="{y + 20}">{with_unit(num(bar * bk, 2), bunit)}</text></g>')
    cap_rows = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in rows)
    return (f'<figure class="rockfig s-{state}">'
            f'<svg viewBox="{-half:g} {-half:g} {ROCK_BOX} {ROCK_BOX + 34}" role="img" aria-label="{esc(alt)}">'
            f'<g{turn}>{"".join(shapes)}</g>{scale}</svg>'
            f'<figcaption><dl>{cap_rows}</dl></figcaption></figure>')


# ---------------------------------------------------------------- gauges: one scale per row, with the gates on it

def _lin(lo, hi):
    return lambda v: (v - lo) / (hi - lo) * 100


def _log(lo, hi):
    a, b = math.log10(lo), math.log10(hi)
    return lambda v: (math.log10(v) - a) / (b - a) * 100 if v > 0 else 0.0


AXES = {
    "reach": {"pos": _lin(3.0, 12.0), "ticks": ((3, "3 km/s"), (6, "6"), (9, "9"), (12, "12 km/s"))},
    "tracking": {"pos": _lin(0, 9), "ticks": tuple((i, str(i)) for i in range(10))},
    "size": {"pos": _log(1.0, 10000.0),
             "ticks": ((1, "1 m"), (10, "10 m"), (100, "100 m"), (1000, "1 km"), (10000, "10 km"))},
    "spin": {"pos": _log(1 / 60, 100.0),
             "ticks": ((1 / 60, "1 min"), (1 / 6, "10 min"), (1, "1 h"), (10, "10 h"), (100, "100 h"))},
    "surface": {"pos": _log(0.01, 1.0), "ticks": ((0.01, "1%"), (0.03, "3%"), (0.1, "10%"), (0.3, "30%"), (1, "100%"))},
}
_ROW_SAYS = {"reach": "delta-v", "tracking": "orbit code, 0 best", "size": "size", "spin": "rotation period",
             "surface": "reflectivity"}


def _axis_factor(row_id: str, f: dict):
    """The factor that puts a fact on its row's scale, or None if it has no place there."""
    unit, name = (f.get("unit") or "").strip(), f.get("label") or ""
    if row_id == "reach":
        return 1.0 if UNITS.get(unit) == "km/s" and name.startswith("delta-v") and "shortest" not in name else None
    if row_id == "tracking":
        return 1.0 if name == "condition code" else None
    if row_id == "size":
        return {"m": 1.0, "km": 1000.0}.get(unit)
    if row_id == "spin":
        return TIME_S[unit] / 3600.0 if unit in TIME_S else None
    if row_id == "surface" and _ALBEDO.search(name):
        return {"": 1.0, "%": 0.01}.get(unit)
    return None


def _clamp(p: float) -> float:
    return min(100.0, max(0.0, p))


def gate_lines(missions: dict | None) -> dict:
    """{row id: [(value on its scale, words)]}: each mission threshold a row's scale can show,
    read from method/v0_1/missions.toml. Two missions with the same line share it."""
    out: dict = {}
    for mid in (missions or {}).get("order", ()):
        for g in (missions.get(mid) or {}).get("gates", []):
            row_id = GATE_ROW.get(g.get("id"))
            if row_id not in AXES or not is_num(g.get("preset")):
                continue
            unit = UNITS.get(g.get("unit") or "", "")
            k = 1.0 if row_id != "spin" else TIME_S.get(g.get("unit"), 3600.0) / 3600.0
            if row_id == "size" and unit != "m":
                continue
            out.setdefault(row_id, []).append((g["preset"] * k, with_unit(num(g["preset"]), unit), mid, g.get("label")))
    lines = {}
    for row_id, gates in out.items():
        merged: dict = {}
        for v, said, mid, name in gates:
            merged.setdefault(v, []).append((said, mid, name))
        lines[row_id] = [(v, items[0][2] if len(items) > 1 else f"{items[0][0]}: {MISSION_LABELS.get(items[0][1], items[0][1]).lower()}")
                         for v, items in sorted(merged.items())]
    return lines


def gauge(row_id: str, row: dict, sources: dict, gates=()) -> str:
    spec = AXES.get(row_id)
    if not spec:
        return ""
    pos = lambda v: _clamp(spec["pos"](v))
    marks, said = [], ""
    counted = row.get("state") in ("measured", "limit")
    lead = True
    for f in row.get("facts", []):
        f = public(f, sources)
        k = _axis_factor(row_id, f) if f else None
        if k is None or not is_num(f.get("value")):
            continue
        val, kind = f["value"] * k, f.get("kind", "value")
        if not (counted and lead and used(f)):
            if row_id in ("reach", "tracking"):
                continue
            marks.append(f'<i class="pt {"o" if used(f) and counted else "x"}" style="left:{pos(val):.2f}%"></i>')
            continue
        lead = False
        if kind == "upper":
            marks.append(f'<i class="bar lim" style="left:0;width:{pos(val):.2f}%"></i>')
        elif kind == "lower":
            marks.append(f'<i class="bar lim" style="left:{pos(val):.2f}%;width:{100 - pos(val):.2f}%"></i>')
        elif is_num(f.get("lo")) and is_num(f.get("hi")) and f["lo"] < f["hi"]:
            a, b = pos(f["lo"] * k), pos(f["hi"] * k)
            marks.append(f'<i class="bar" style="left:{a:.2f}%;width:{max(b - a, 0.4):.2f}%"></i>')
        marks.append(f'<i class="pt" style="left:{pos(val):.2f}%"></i>')
        said = f"{_ROW_SAYS[row_id]} on file"
    p = row.get("prior") or {}
    if row.get("state") in ("prior", "unchecked") and is_num(p.get("q50")):
        k = {"size": _metres(p), "surface": 1.0}.get(row_id)
        if k and is_num(p.get("q05")) and is_num(p.get("q95")):
            a, b = pos(p["q05"] * k), pos(p["q95"] * k)
            marks.append(f'<i class="est" style="left:{a:.2f}%;width:{b - a:.2f}%"></i>')
            marks.append(f'<i class="mid" style="left:{pos(p["q50"] * k):.2f}%"></i>')
            said = f"{_ROW_SAYS[row_id]} estimated, 9 in 10"
    if not marks and not gates:
        return ""
    ticks = []
    for i, (v, text) in enumerate(spec["ticks"]):
        edge = " first" if i == 0 else " last" if i == len(spec["ticks"]) - 1 else ""
        ticks.append(f'<i class="tk{edge}" style="left:{pos(v):.2f}%"><span>{esc(text)}</span></i>')
    lines = "".join(f'<i class="gate{" l" if i == 0 and len(gates) > 1 else ""}" style="left:{pos(v):.2f}%">'
                    f'<span>{esc(text)}</span></i>' for i, (v, text) in enumerate(gates))
    aria = f"{cap(_ROW_SAYS[row_id])} scale" + (f": {said}" if said else ": nothing on file")
    return (f'<div class="gauge" role="img" aria-label="{esc(aria)}"><i class="track"></i>'
            f'{"".join(ticks)}{lines}{"".join(marks)}</div>')


def timeline(start: str, end: str, data_date: str) -> str:
    """The next window on a dated axis that starts at the data date. Nothing says now."""
    try:
        d0, s, e = _date.fromisoformat(data_date), _date.fromisoformat(start), _date.fromisoformat(end)
    except (TypeError, ValueError):
        return ""
    d1 = _date(max(e.year, d0.year) + 1, 1, 1)
    days = (d1 - d0).days
    x = lambda d: _clamp((d - d0).days / days * 100)
    years = []
    for y in range(d0.year + 1, d1.year + 1):
        at = x(_date(y, 1, 1))
        last = " dz" if y == d1.year else ""
        text = f"<span>{y}</span>" if at > 14 else ""
        years.append(f'<i class="yr{last}" style="left:{at:.2f}%">{text}</i>')
    return (f'<div class="timeline" role="img" aria-label="Next window {esc(start)} to {esc(end)}">'
            f'<i class="axis"></i><i class="yr d0" style="left:0"><span>{esc(data_date)}, data date</span></i>'
            f'{"".join(years)}<i class="win" style="left:{x(s):.2f}%;width:{max(x(e) - x(s), 0.5):.2f}%">'
            f'<span>Window {esc(start)} to {esc(end)}</span></i></div>')


# ---------------------------------------------------------------- the six rows

def _value(row_id: str, f: dict) -> tuple[str, str, str]:
    """(value, range, what the label adds) for a fact that may be printed. A stated range is one sigma,
    and says so. A very small quantity prints plain, with its power of ten and unit in the label."""
    val = f.get("value")
    if is_num(val):
        k, unit = scale_for(row_id, f.get("label"), f.get("unit"), val)
        unit = esc(unit)
        sign = {"upper": "under ", "lower": "over "}.get(f.get("kind", "value"), "")
        lo, hi = f.get("lo"), f.get("hi")
        ranged = is_num(lo) and is_num(hi) and lo < hi
        extra = ""
        if unit not in ("", "%") and val != 0 and math.floor(math.log10(abs(val * k))) < -2:
            e = math.floor(math.log10(abs(val * k)))
            extra, k, unit = f"10{str(e).translate(_SUP)} {unit}", k / 10.0 ** e, ""
        sig = 4
        def blurred(sig):               # two of low end, value and high end print alike though they differ
            shown = [num(x * k, sig) for x in sorted({lo, val, hi})]
            return len(set(shown)) < len(shown)
        while ranged and sig < 9 and blurred(sig):
            sig += 1                    # a range narrower than four figures keeps the figures it needs
        if isinstance(val, int) and k == 1.0:
            shown = count(val)          # a count or a whole number of days is printed whole
        elif unit == "km/s":
            shown = f"{val * k:.3f}"    # JPL states delta-v to the metre per second
        else:
            shown = num(val * k, sig)
        rng = f"{span(lo * k, hi * k, unit, sig)}, {ONE_SIGMA}" if ranged else ""
        return sign + with_unit(shown, unit), rng, extra
    if isinstance(val, str) and _ISO_DATE.match(val.strip()):
        return date(val.strip()), "", ""
    if val is None or val == "":
        return "no value given", "", ""
    unit = UNITS.get(f.get("unit"), f.get("unit"))
    return esc(val) + (f" {esc(unit)}" if unit else ""), "", ""


FACT_COLS = ('<colgroup><col class="c-l"><col class="c-v"><col class="c-r"><col class="c-q"><col class="c-s">'
             '</colgroup>')


def facts_table(row_id: str, facts: list, sources: dict) -> str:
    """The row's facts, one line each: label, value, 1σ range, grade and note, source, in the ledger's order, so
    the first used line is the one the row rests on. A value the licence rule holds back is a pointer in its
    place. A source every line shares is printed once, under."""
    held = [f for f in facts if not displayable(f, sources)]
    cites = {(f.get("source", ""), f.get("ref")) for f in facts}
    once = len(cites) == 1 and len(facts) > 1
    lines = []
    for f in facts:
        name = cap(label(row_id, f.get("label")))
        cite = source_link(sources, f.get("source", "")) + (f", {esc(unparen(f['ref']))}" if f.get("ref") else "")
        if f in held:
            lines.append(f'<tr class="ptr"><th scope="row">{esc(name)}</th><td class="v dim">{POINTER}</td>'
                         f'<td class="r"></td><td class="q"></td><td class="s">{"" if once else source_link(sources, f.get("source", ""))}</td></tr>')
            continue
        val, rng, extra = _value(row_id, f)
        if extra:
            name += f", {extra}"
        g = grade(row_id, f.get("quality"))
        q = ", ".join(x for x in (unparen(g), esc(unparen(f.get("note") or ""))) if x)
        tag = "" if used(f) else '<span class="tag">not used</span>'
        lines.append(f'<tr{"" if used(f) else ' class="nu"'}><th scope="row">{esc(name)}</th><td class="v">{val}</td>'
                     f'<td class="r">{rng}{tag}</td><td class="q">{q}</td><td class="s">{"" if once else cite}</td></tr>')
    if not lines:
        return ""
    tail = ""
    if once:
        sid, ref = next(iter(cites))
        tail = (f'<p class="srcline">Source: {source_link(sources, sid)}'
                + (f", {esc(unparen(ref))}" if ref else "") + "</p>")
    return f'<table class="facts">{FACT_COLS}<tbody>{"".join(lines)}</tbody></table>{tail}'


def _odds(p: dict, summary: dict) -> str:
    out = []
    rng = p.get("range") or {}
    for key, name in SPIN_SHARES:
        v = p.get(key, summary.get(key))
        if not is_num(v):
            continue
        r = rng.get(key) if isinstance(rng.get(key), (list, tuple)) and len(rng.get(key)) == 2 else None
        spread = (f'<u style="left:{_clamp(r[0] * 100):.0f}%;width:{_clamp((r[1] - r[0]) * 100):.0f}%"></u>'
                  if r and all(is_num(x) for x in r) else "")
        out.append(f'<span class="lab">Faster than {name}</span><span class="meter" aria-hidden="true">'
                   f'<i style="width:{_clamp(v * 100):.0f}%"></i>{spread}</span>'
                   f'<span class="n">{hundredths(v)} in 100</span>'
                   + (f'<span class="rng">surveys: {hundredths(r[0])} to {hundredths(r[1])}</span>' if spread else '<span></span>'))
    if not out:
        return ""
    return f'<p class="cap">Of 100 asteroids this bright</p><div class="odds">{"".join(out)}</div>'


def _shares(shares: dict) -> str:
    keys = [c for c in ("S", "C", "X", "other") if is_num(shares.get(c))]
    keys += [c for c in sorted(shares) if c not in keys and is_num(shares.get(c))]
    if not keys:
        return ""
    order = sorted(keys, key=lambda c: -shares[c])
    bars = "".join(f'<span class="c{min(i, 3) + 1}" style="width:{_clamp(shares[c] * 100):.1f}%">'
                   f'{esc(c) if hundredths(shares[c]) >= 6 else ""}</span>' for i, c in enumerate(order))
    key = "".join(f'<span><b>{hundredths(shares[c])}</b> {esc(CLASS_LABELS.get(c, c))}</span>' for c in order)
    return (f'<p class="cap">Class, of 100 asteroids this bright</p>'
            f'<div class="shares" aria-hidden="true">{bars}</div><div class="shares-key">{key}</div>')


def prior(row_id: str, row: dict, summary: dict, implied: bool = False) -> str:
    """What is typical, for a row nobody has measured: the range first, never a single figure.

    `implied` marks a reflectivity that follows from the asteroid's own measured size and H:
    it is not what is typical at its brightness, and it can come out above 100%.
    """
    if row.get("state") not in ("prior", "unchecked"):
        return ""
    p = row.get("prior") or {}
    out = []
    if is_num(p.get("q05")) and is_num(p.get("q95")):
        surface = row_id == "surface"
        k, unit = scale_for(row_id, "albedo" if surface else "", p.get("unit"), p["q95"])
        if surface and implied:
            name, how = "Reflectivity", "9 in 10, implied by its size and H"
        elif surface:
            name, how = "Reflectivity", "9 in 10 at this brightness"
        else:
            name, how = "From brightness", "9 in 10"
        flag = "over 100% cannot be: its size or H is off" if surface and unit == "%" and p["q95"] * k > 100 else ""
        out.append(f'<table class="facts est">{FACT_COLS}<tbody><tr class="pr"><th scope="row">{name}</th>'
                   f'<td class="v">{span(p["q05"] * k, p["q95"] * k, esc(unit), 2)}</td><td class="r">{how}</td>'
                   f'<td class="q">{flag}</td><td class="s">{esc(unparen(p.get("basis")))}</td></tr></tbody></table>')
    if isinstance(p.get("shares"), dict):
        out.append(_shares(p["shares"]))
    if row_id == "spin":
        out.append(_odds(p, summary))
    return "".join(out)


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
# The ledger's reasons for a source not being checked, shortened for the one line that names it.
_REASONS = (
    (re.compile(r"^no .*card has been fetched$", re.I), lambda m: "no card fetched"),
    (re.compile(r"^.* did not know this object(?: on (\S+))?$", re.I),
     lambda m: "unknown there" + (f", {m[1]}" if m[1] else "")),
    (re.compile(r"^the request to .* failed(?: on (\S+))?(?: \((.*)\))?$", re.I),
     lambda m: "request failed" + (f" {m[1]}" if m[1] else "") + (f", {m[2]}" if m[2] else "")),
    (re.compile(r"^(?:.* is )?(older than this object)$", re.I), lambda m: m[1].lower()),
    (re.compile(r"^.* was (not read)$", re.I), lambda m: m[1]),
    (re.compile(r"^.* was not checked$", re.I), lambda m: ""),          # the line already says so
)
_OPENERS = ("The", "No", "A", "An", "Not", "Observed")


def _reason(sentence: str) -> str:
    text = sentence.strip().rstrip(".")
    for pattern, short in _REASONS:
        m = pattern.match(text)
        if m:
            return short(m)
    return text[:1].lower() + text[1:] if text.split(" ", 1)[0] in _OPENERS else text


def unchecked_reasons(rw: dict) -> tuple[list[str], str]:
    """(why each source in rw["unchecked"] was not checked, the rest of the row's note).

    The ledger ends a row's note with one sentence per unchecked source, in the order of
    rw["unchecked"] (longshot.ledger._row).
    """
    ids = rw.get("unchecked") or []
    note = (rw.get("note") or "").strip()
    sentences = _SENTENCE_END.split(note) if note else []
    if not ids or len(sentences) < len(ids):
        return [""] * len(ids), note
    cut = len(sentences) - len(ids)
    return [_reason(x) for x in sentences[cut:]], " ".join(sentences[:cut])


def row(row_id: str, rw: dict, summary: dict, sources: dict, implied: bool = False, gates=(),
        data_date: str = "") -> str:
    state = rw.get("state", "unchecked")
    facts = rw.get("facts", [])
    parts = [gauge(row_id, rw, sources, gates)]
    if row_id == "tracking":
        window = [f for f in facts if str(f.get("label", "")).startswith("window")]
        rest = [f for f in facts if f not in window]
        parts.append(facts_table(row_id, rest, sources))
        when = {f["label"]: f.get("value") for f in window}
        if isinstance(when.get("window start"), str) and isinstance(when.get("window end"), str):
            parts.append(timeline(when["window start"], when["window end"], data_date))
        parts.append(facts_table(row_id, window, sources))
    else:
        parts.append(facts_table(row_id, facts, sources))
    parts.append(prior(row_id, rw, summary, implied))
    note = rw.get("note")
    if rw.get("unchecked"):
        # one line names every source not checked and says why; the note keeps what is not about them
        whys, note = unchecked_reasons(rw)
        names = "; ".join(source_link(sources, s) + (f', <span class="dim">{esc(w)}</span>' if w else "")
                          for s, w in zip(rw["unchecked"], whys))
        parts.append(f'<p class="un">{glyph("unchecked")}<span>Not checked: {names}</span></p>')
    for c in rw.get("conflicts", []):
        parts.append(f'<p class="conflict">Conflict: {esc(c)}</p>')
    if note:
        parts.append(f'<p class="note">{esc(note)}</p>')
    if not "".join(parts):
        parts.append('<p class="none">None on file</p>')
    return (
        f'<section class="row" id="row-{row_id}" data-row="{row_id}" data-state="{esc(state)}" '
        f'aria-labelledby="h-{row_id}"><div class="rh"><h3 id="h-{row_id}">{ROW_LABELS[row_id]}</h3>'
        f'{state_tag(state)}</div><div class="rb">{"".join(parts)}</div></section>'
    )


# ---------------------------------------------------------------- the sections under the rows

def method_link(anchor: str, text: str) -> str:
    """A link from an entry to where method.html gives the threshold or input behind `text` (already escaped).

    Relative to a/: the readout resolves an entry's links against the entry's own address.
    """
    return f'<a href="../{METHOD_PAGE}#{esc(anchor)}">{text}</a>'


def ladder(rungs: list) -> str:
    if not rungs:
        return '<p class="none">No ladder computed</p>'
    items = []
    for i, r in enumerate(rungs, 1):
        status = r.get("status", "unknown")
        mark = {"measured": "measured", "prior": "prior"}.get(status, "unknown")
        name = esc(RUNG_LABELS.get(r.get("rung"), r.get("rung")))
        if r.get("rung") in RUNG_LABELS:
            name = method_link(f'rung-{r["rung"]}', name)
        parts = [p for p in r.get("parts") or [] if p.get("label") and p.get("text")]
        if parts:       # the last rung's two amounts, one line each: the parts' texts joined are the rung's text
            said = ('<table class="tbl prec"><thead><tr><th scope="col">Amount</th><th scope="col">Status</th></tr></thead><tbody>'
                    + "".join(f'<tr><th scope="row">{esc(p["label"])}</th><td>{esc(cap(p["text"]))}</td></tr>'
                              for p in parts) + '</tbody></table>')
        else:
            said = f'<p>{esc(r.get("text"))}</p>'
        items.append(f'<li data-status="{esc(status)}"><span class="n">{i}</span><h3>{name}</h3>'
                     f'{state_tag(mark, RUNG_WORDS.get(status, cap(status)))}<div class="rt">{said}</div></li>')
    return f'<ol class="ladder">{"".join(items)}</ol>'


def _q(d, a="q05", b="q95"):
    d = d or {}
    return (d.get(a), d.get(b)) if is_num(d.get(a)) and is_num(d.get(b)) else None


UNIT_KEY = {"": "None", "u": "None or some", "s": "Some", "ru": "Iron-rich or not", "r": "Iron-rich"}


def _units(spec: list) -> str:
    """100 cells, the chance of nothing first, each kind counted in the key."""
    spec = [(c, n) for c, n in spec if n > 0]
    cells = "".join(f'<i class="{c}"></i>' * n for c, n in spec)
    key = "".join(f'<span><i class="{c}"></i>{UNIT_KEY[c]}<b>{n}</b></span>' for c, n in spec)
    return f'<p class="cap">100 asteroids like it</p><div class="units" aria-hidden="true">{cells}</div><div class="ukey">{key}</div>'


def _metal_cells(val: dict):
    metal, iron = val.get("metal") or {}, val.get("iron_rich") or {}
    lo = metal.get("p_nothing_lo", metal.get("p_nothing"))
    hi = metal.get("p_nothing_hi", metal.get("p_nothing"))
    if not (is_num(lo) and is_num(hi)):
        return None
    a, b = hundredths(lo), hundredths(hi)
    r = hundredths(iron["p_lo"]) if is_num(iron.get("p_lo")) else 0
    rhi = hundredths(iron["p_hi"]) if is_num(iron.get("p_hi")) else r
    some = 100 - b - rhi
    return [("", a), ("u", b - a), ("s", max(some, 0)), ("ru", rhi - r), ("r", r)]


def _water_cells(val: dict):
    water = val.get("water") or {}
    lo = water.get("p_nothing_lo", water.get("p_nothing"))
    hi = water.get("p_nothing_hi", water.get("p_nothing"))
    if not (is_num(lo) and is_num(hi)):
        return None
    a, b = hundredths(lo), hundredths(hi)
    return [("", a), ("u", b - a), ("s", 100 - b)]


CELL_CLASS = {"none": "", "none_or_some": "u", "some": "s", "iron_rich_or_not": "ru", "iron_rich": "r"}   # value.table cell ids
VALUE_COLS = {"metal": (("Of 100", "of100"), ("Metal", "kg"), ("At list price", "usd")),
              "water": (("Of 100", "of100"), ("Water", "tonnes"))}


def _vtable(part: str, rows: list) -> str:
    """One price table from record.value.table: every figure as the record's statements print it."""
    cols = VALUE_COLS[part]
    head = '<th scope="col"><span class="vh">Holds</span></th>' + "".join(f'<th class="num" scope="col">{h}</th>' for h, _ in cols)
    body = "".join(
        f'<tr><th scope="row">{esc(r.get("label"))}</th>'
        + "".join(f'<td class="num" data-l="{h}">{esc(r.get(k) or "")}</td>' for h, k in cols) + "</tr>"
        for r in rows)
    return f'<table class="tbl vt"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def value(rec: dict) -> str:
    val = rec.get("value") or {}
    if rec.get("gone"):
        return '<p class="none">No estimate: it no longer exists</p>'
    out = []
    mass = _q((rec.get("summary") or {}).get("mass_t"))
    if mass:
        out.append(f'<p class="mass"><span>Mass of the whole asteroid</span><b>{amount(mass[0], mass[1], "t")}</b>'
                   f'<span>9 in 10</span></p>')
    table = val.get("table")
    if table and not val.get("sample"):
        for part, title in (("metal", "Platinum-group metal, in metal grains"), ("water", "Water, bound in minerals")):
            p = table.get(part) or {}
            cells = [(CELL_CLASS.get(c.get("id"), ""), c.get("n") or 0) for c in p.get("cells") or []]
            if not cells and not p.get("rows"):
                continue
            out.append(f'<div class="vblock"><div><h3>{title}</h3>{_units(cells) if cells else ""}</div>'
                       f'<div>{_vtable(part, p.get("rows") or [])}</div></div>')
        notes = [n for n in table.get("notes") or [] if n] + ([f'Prices: {val["basis"]}'] if val.get("basis") else [])
        if notes:
            out.append(f'<div class="foot-notes">{"".join(f"<p>{esc(n)}</p>" for n in notes)}</div>')
        return f'<div class="value">{"".join(out)}</div>'
    statements = [s for s in val.get("statements") or [] if s]
    ids = val.get("statement_ids") or []
    if statements:
        water_ids = ("water", "sample")
        if len(ids) == len(statements):
            metal_s = [s for s, i in zip(statements, ids) if not str(i).startswith(water_ids)]
            water_s = [s for s, i in zip(statements, ids) if str(i).startswith(water_ids)]
        else:
            metal_s, water_s = statements, []
        for title, cells, said in (("Platinum-group metal, in metal grains", _metal_cells(val), metal_s),
                                   ("Water, bound in minerals", _water_cells(val), water_s)):
            if not said and not cells:
                continue
            out.append(f'<div class="vblock"><div><h3>{title}</h3>{_units(cells) if cells else ""}</div>'
                       f'<ul class="stm">{"".join(f"<li>{esc(s)}</li>" for s in said)}</ul></div>')
    else:
        # Only when the pipeline wrote no sentences: the bare ranges, the chance of nothing first.
        metal, water = val.get("metal") or {}, val.get("water") or {}
        lines = []
        if is_num(metal.get("p_nothing")):
            lines.append(("Chance of no separable metal", pct(metal["p_nothing"]), ""))
        if _q(metal.get("kg")):
            lines.append(("Platinum-group metal, if any", amount(*_q(metal["kg"]), "kg"), "9 in 10"))
        if _q(metal.get("usd")):
            a, b = _q(metal["usd"])
            lines.append(("That metal at list prices", f"{usd(a)} to {usd(b)}", "9 in 10"))
        if is_num(water.get("p_nothing")):
            lines.append(("Chance of no water", pct(water["p_nothing"]), ""))
        if _q(water.get("tonnes")):
            lines.append(("Water, if any", amount(*_q(water["tonnes"]), "t"), "9 in 10"))
        if lines:
            out.append('<dl class="kv">' + "".join(f"<dt>{a}</dt><dd>{b}" + (f' <span class="dim">{c}</span>' if c else "")
                                                   + "</dd>" for a, b, c in lines) + "</dl>")
    if val.get("basis"):
        out.append(f'<p class="foot-notes">Prices: {esc(val["basis"])}</p>')
    if not out:
        return '<p class="none">No estimate: no size on file</p>'
    return f'<div class="value">{"".join(out)}</div>'


def no_window(rec: dict) -> str:
    """What the tracking row says when JPL lists no window, so the site has one phrase for it."""
    f = _first(rec["rows"].get("tracking", {}).get("facts", []),
               lambda f: f.get("label") == "next window" and isinstance(f.get("value"), str) and f["value"])
    return f["value"] if f else "none on file"


def settles(rec: dict) -> tuple[str, str]:
    """(the gate an observation settles, the mission it belongs to), from the record's own gates; '' if unnamed."""
    o = rec.get("observe") or {}
    m = (rec.get("missions") or {}).get(o.get("mission")) or {}
    g = _first(m.get("gates", []), lambda g: g.get("id") == o.get("gate") and g.get("label"))
    return (g["label"], MISSION_LABELS.get(o["mission"], o["mission"]).lower()) if g else ("", "")


def nothing_ranked(rec: dict) -> str:
    """Why no observation is ranked, in a few words. The missions' own results are under Missions, not here."""
    missions = [(rec.get("missions") or {}).get(mid) or {} for mid in MISSION_LABELS]
    if rec.get("gone"):
        return "it no longer exists"
    if any(g.get("id") == "findable" and g.get("status") == "fail" for m in missions for g in m.get("gates", [])):
        return "orbit not good enough to find it again"
    states = [m.get("status") for m in missions]
    if "untested" not in states and all(states):
        return "both missions rest on measurements"
    return "no one observation would change a mission's result"


def next_window(rec: dict) -> tuple[str, str]:
    """(the observation's window as a label and its words) when it is not one a telescope can be pointed at:
    survey recovery only, or none listed. ('', '') for a pointable window: the telescope row says what it takes."""
    o = rec.get("observe") or {}
    w = o.get("window") or {}
    if o.get("tier") == "survey_only" or (w and not w.get("pointable")):
        when = f", {w['start']} to {w['end']}" if w.get("start") and w.get("end") else ""
        return "Survey recovery only", f"{cap(o.get('needs') or '')}{when}"
    if o.get("tier") == "none" or not w:
        return "Next window", cap(no_window(rec))
    return "", ""


def observe(rec: dict, observations: dict | None = None, sources: dict | None = None) -> str:
    """What to observe, what it settles and what it takes. When it can be observed is in the tracking row.

    `observations` maps an observation's id to its name (method/v0_1/observe.toml)."""
    o = rec.get("observe")
    if not o:
        return f'<dl class="kv"><dt>Observation</dt><dd>None, {esc(nothing_ranked(rec))}</dd></dl>'
    lines = []
    gate, mission = settles(rec)
    what = (observations or {}).get(o.get("best"))
    if gate and what:
        lines.append(("Observation", esc(what)))
        g = _first(((rec.get("missions") or {}).get(o.get("mission")) or {}).get("gates", []), lambda g: g.get("id") == o.get("gate"))
        now = f'<span class="dim">, {chance(g["p"])} chance now</span>' if g and is_num(g.get("p")) and g.get("status") == "untested" else ""
        lines.append(("Settles", f"{esc(gate)}, for {esc(mission)}{now}"))
    elif o.get("text"):
        lines.append(("Observation", esc(o["text"])))
    kind, said = next_window(rec)
    if kind:                                    # no telescope can be pointed at it yet: the window says why
        lines.append((kind, esc(said)))
    elif o.get("needs"):
        lines.append(("Telescope", esc(cap(o["needs"]))))
    if o.get("unchecked"):                      # the measurement may already exist there
        lines.append(("Check first", glyph("unchecked") + ", ".join(source_link(sources or {}, s) for s in o["unchecked"])))
    return '<dl class="kv">' + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in lines) + "</dl>"


def missions(rec: dict) -> str:
    out = []
    for mid, name in MISSION_LABELS.items():
        m = (rec.get("missions") or {}).get(mid)
        if not m:
            out.append(f'<div class="mission"><h3>{name}</h3><p class="none">Not assessed</p></div>')
            continue
        rows = []
        for g in m.get("gates", []):
            st = g.get("status", "untested")
            ch = (f'<span class="chance"><span class="meter" aria-hidden="true"><i style="width:{_clamp(g["p"] * 100):.0f}%"></i></span>'
                  f'{chance(g["p"])}</span>') if st == "untested" and is_num(g.get("p")) else ""
            basis = GATE_BASIS.get(g.get("basis"), esc(g.get("basis")))
            row_id = GATE_ROW.get(g.get("id"))
            if g.get("basis") == "prior" and ((rec["rows"].get(row_id) or {}).get("state") == "unchecked"):
                basis = "not checked"
            text = f'<p class="gtext">{esc(unparen(g["text"]))}</p>' if g.get("text") else ""
            what = esc(g.get("label"))
            if g.get("id"):
                what = method_link(f'g-{mid}-{g["id"]}', what)
            rows.append(f'<tr data-status="{esc(st)}"><th scope="row">{what}{text}</th><td data-l="Status">{state_tag(st)}</td>'
                        f'<td class="num" data-l="Chance">{ch}</td><td data-l="Basis">{basis}</td></tr>')
        status = m.get("status", "untested")
        if status == "untested":
            verdict = f'<b>{chance(m.get("p"))}</b>chance of passing every gate{state_tag("untested")}'
        elif status == "pass":
            verdict = f'<b>{glyph("pass")}Pass</b>every gate measured'
        else:
            verdict = f'<b>{glyph("fail")}Fail</b>a measured gate fails'
        out.append(f'<div class="mission" data-status="{esc(status)}"><h3>{name}</h3><p class="verdict">{verdict}</p>'
                   '<table class="tbl gates"><colgroup><col class="g1"><col class="g2"><col class="g3"><col class="g4"></colgroup>'
                   '<thead><tr><th scope="col">Gate</th><th scope="col">Status</th><th scope="col" class="num">Chance</th>'
                   f'<th scope="col">Basis</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    return f'<div class="missions">{"".join(out)}</div>'


def fetched(s: dict) -> str:
    """'2026-11-21 to 2026-11-25': one day, or the first and last of a fetch that ran over several."""
    first, last = s.get("retrieved_from"), s.get("retrieved")
    if not last:
        return ""
    return f"{date(first)} to {date(last)}" if first and first != last else date(last)


def used_sources(rec: dict) -> list[str]:
    """Every source the entry names, the record's own list first, the rest in id order."""
    seen = list(dict.fromkeys(rec.get("sources") or []))
    extra = set()
    for r in rec["rows"].values():
        extra.update(f.get("source") for f in r.get("facts", []) if f.get("source"))
        extra.update(r.get("unchecked", []))
    return seen + sorted(extra - set(seen))


def source_row(sid: str, sources: dict, unchecked: bool = False) -> str:
    """One source as a table row: name and citation, edition, fetched, what is shown here."""
    s = sources.get(sid)
    if not s:
        return f'<tr id="src-{esc(sid)}"><th scope="row">{esc(sid)}</th><td colspan="3">Not in the source list</td></tr>'
    name = esc(source_name(sources, sid))
    if s.get("url"):
        name = f'<a href="{esc(s["url"])}" rel="noopener">{name}</a>'
    use = esc(LICENCE_WORDS.get(s.get("licence"), s.get("licence")))
    if unchecked:
        use = f'{glyph("unchecked")}Not checked for this asteroid'
    return (f'<tr id="src-{esc(sid)}"><th scope="row">{name}<p class="gtext">{esc(unparen(public_text(s.get("citation"))))}</p></th>'
            f'<td class="num" data-l="Edition">{date(s["edition"]) if s.get("edition") else ""}</td>'
            f'<td class="num" data-l="Fetched">{fetched(s)}</td><td data-l="Shown here">{use}</td></tr>')


def sources_table(ids: list, sources: dict, unchecked=()) -> str:
    rows = "".join(source_row(sid, sources, sid in unchecked) for sid in ids)
    return ('<table class="tbl sources"><thead><tr><th scope="col">Source</th><th scope="col" class="num">Edition</th>'
            '<th scope="col" class="num">Fetched</th><th scope="col">Shown here</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


def names(rec: dict) -> tuple[str, list[str]]:
    """(heading, the other names it goes by): the name where it has one, then number and designation."""
    head = rec.get("name") or rec["designation"]
    others = []
    if rec.get("number"):
        others.append(str(rec["number"]))
    if rec.get("name"):
        others.append(rec["designation"])
    # JPL's other spellings, less any that only repeat the number, the name or the designation
    said = {_squash(x) for x in (head, rec["designation"], rec.get("name"), rec.get("number")) if x}
    if rec.get("number") and rec.get("name"):
        said |= {_squash(f"{rec['number']} {rec['name']}"), _squash(f"{rec['number']} {rec['name']} {rec['designation']}")}
    if rec.get("number"):
        said.add(_squash(f"{rec['number']} {rec['designation']}"))
    for a in rec.get("aliases") or []:
        if a and _squash(a) not in said:
            said.add(_squash(a))
            others.append(a)
    return head, others


def _squash(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).casefold())


# ---------------------------------------------------------------- the summary: one list of label, value, detail, state

def _class_word(c: str) -> str:
    return CLASS_WORDS.get(draws_mod.class_group(c) or "", f"Class {c}")


def _held(sources: dict, sid: str) -> str:
    """The detail beside a value on file that the page may not print: whose it is."""
    return f"{short_name(sources, sid)}, not shown here" if sid else POINTER


def _density(rec: dict, sources: dict):
    """The bulk density the mass rests on where summary.mass_basis is 'density': the push row's first used one."""
    return _first(rec["rows"].get("push", {}).get("facts", []),
                  lambda f: (f.get("label") or "").casefold() == "density" and used(f)
                  and f.get("kind", "value") == "value" and is_num(f.get("value")))


GROUP = None        # a summary item whose value is GROUP is a heading over the items after it


def summary_items(rec: dict, sources: dict, observations: dict | None = None) -> list[tuple]:
    """[(label, value as HTML, detail as plain text, state or None)] for the entry's summary.
    An item whose value is GROUP heads the ones after it."""
    rows, summ = rec["rows"], rec.get("summary") or {}
    items = []
    gone = rec.get("gone") or {}
    if gone:                                # first, so nothing below reads as if it were still there
        items.append(("Gone", date(gone["date"]) if gone.get("date") else "Yes", gone.get("text") or "", None))
    # size: the value the size row rests on, its range, how and by whom
    srow = rows.get("size") or {}
    sstate = srow.get("state", "unchecked")
    s = size_of(rec, sources)
    if s and sstate in ("measured", "limit") and s["state"] == sstate:
        k, unit = scale_for("size", "", "m", s["hi"] or s["mid"])
        how = ", ".join(x for x in (unparen(html.unescape(grade("size", s.get("quality")))), source_name(sources, s["source"])) if x)
        if sstate == "measured":
            rng = f"{span(s['lo'] * k, s['hi'] * k, unit, 3)}, {ONE_SIGMA}, " if s["lo"] else ""
            items.append(("Size", f'{num(s["mid"] * k, 3)} {u(unit)}', rng + how, sstate))
        else:
            word = "under" if s["kind"] == "upper" else "over"
            items.append(("Size", f'{word} {num(s["mid"] * k, 3)} {u(unit)}', "a limit, " + how, sstate))
    elif sstate in ("measured", "limit"):
        first = _first(srow.get("facts", []), lambda f: used(f) and _metres(f) and is_num(f.get("value")))
        items.append(("Size", "On file", _held(sources, (first or {}).get("source", "")), sstate))
    elif s and s["lo"]:
        k, unit = scale_for("size", "", "m", s["hi"])
        items.append(("Size", span(s["lo"] * k, s["hi"] * k, "", 2) + f" {u(unit)}", "9 in 10, from brightness", sstate))
    else:
        items.append(("Size", "None on file", "no brightness on file", sstate))
    # spin: the period the row rests on, as a source the page may print gives it
    prow = rows.get("spin") or {}
    pstate = prow.get("state", "unchecked")
    f, why = shown_period(rec, sources)
    rests_on = ((summ.get("period") or {}).get("rests_on")
                or (_first(prow.get("facts", []), lambda f: used(f) and _is_period(dict(f, kind="value"))) or {}).get("source", ""))
    if f:
        k, unit = scale_for("spin", "", f["unit"], f["value"])
        items.append(("Spin", f'{num(f["value"] * k)} {u(unit)}', f"one turn, {source_name(sources, f.get('source'))}", pstate))
    elif pstate == "measured":
        items.append(("Spin", "On file", _held(sources, rests_on) if why == POINTER else why, pstate))
    elif pstate == "limit":
        b = _first(prow.get("facts", []), lambda f: f.get("kind") in ("upper", "lower") and used(f)
                   and displayable(f, sources) and _is_period(dict(f, kind="value")))
        if b:
            k, unit = scale_for("spin", "", b["unit"], b["value"])
            word = "under" if b["kind"] == "upper" else "over"
            items.append(("Spin", f'{word} {num(b["value"] * k)} {u(unit)}', f"a limit, {source_name(sources, b.get('source'))}", pstate))
        else:
            items.append(("Spin", "On file", _held(sources, rests_on), pstate))
    else:
        p = (prow.get("prior") or {}).get("p_fast_2_2h", summ.get("p_fast_2_2h"))
        if is_num(p):
            items.append(("Spin", f"{hundredths(p)} in 100", f"this bright turn faster than once in {SPIN_SHARES[0][1]}", pstate))
        else:
            items.append(("Spin", "None on file", "no brightness on file", pstate))
    # made of: the class and reflectivity the surface row rests on, or the shares at this brightness
    crow = rows.get("surface") or {}
    cstate = crow.get("state", "unchecked")
    pick = lambda pred: _first(crow.get("facts", []), lambda f: used(f) and displayable(f, sources) and pred(f))
    cls = pick(lambda f: f.get("label") == "class" and isinstance(f.get("value"), str))
    alb = pick(lambda f: _ALBEDO.search(f.get("label") or "") and is_num(f.get("value")))
    if cstate in ("measured", "limit") and (cls or alb):
        word = _class_word(cls["value"]) if cls else ""
        # the class in the detail only where the value names a group, not the class itself
        bits = [f"class {cls['value']}" if cls and not word.startswith("Class ") else "",
                f"reflectivity {pct(alb['value'])}" if alb and cls else ""]
        who = ", ".join(dict.fromkeys(source_name(sources, x["source"]) for x in (cls, alb) if x))
        value = esc(word) if cls else f'{pct(alb["value"])} {u("reflectivity")}'
        items.append(("Made of", value, ", ".join(x for x in bits + [who] if x), cstate))
    elif cstate in ("measured", "limit"):
        first = _first(crow.get("facts", []), lambda f: used(f))
        items.append(("Made of", "On file", _held(sources, (first or {}).get("source", "")), cstate))
    else:
        sh = (crow.get("prior") or {}).get("shares") or summ.get("class") or {}
        if all(is_num(sh.get(c)) for c in ("S", "C", "X", "other")):
            items.append(("Made of", f"{hundredths(sh['S'])} in 100 stony",
                          f"{hundredths(sh['X'])} metal or rock, {hundredths(sh['C'])} carbon-rich, {hundredths(sh['other'])} other",
                          cstate))
        else:
            items.append(("Made of", "None on file", "no brightness on file", cstate))
    # mass: nobody measures it here; it follows from the size and a density, the asteroid's own where one is on file
    m = _q(summ.get("mass_t"))
    if m:
        rho = _density(rec, sources) if summ.get("mass_basis") == "density" else None
        if rho is not None:
            said = (f"9 in 10, from its size and its density, {with_unit(num(rho['value'], 4), 'kg/m³')}, "
                    f"{source_name(sources, rho.get('source'))}" if displayable(rho, sources)
                    else f"9 in 10, from its size and its density on file, {short_name(sources, rho.get('source'))}")
            # both inputs measured: the mass is as measured as its size; else it is no better than the size
            state = "measured" if sstate == "measured" else sstate if sstate != "limit" else "prior"
        else:
            said, state = "9 in 10, from size and class", "unchecked" if sstate == "unchecked" else "prior"
        items.append(("Mass", amount(m[0], m[1], u("t")), said, state))
    # reach
    dv, days = delta_v(rec), trip_days(rec)
    items.append(("Reach", f'{dv:.3f} {u("km/s")}' if dv is not None else "None on file",
                  f"{count(days)} d round trip" if days is not None else "", (rows.get("reach") or {}).get("state", "unchecked")))
    # missions, under their own heading: the value is the status where it is settled, so no second mark
    items.append(("Missions", GROUP, "", None))
    for mid, name in MISSION_LABELS.items():
        mm = (rec.get("missions") or {}).get(mid)
        if not mm:
            items.append((name, "Not assessed", "", None))
        elif mm.get("status") == "untested":
            items.append((name, chance(mm.get("p")), "chance of passing every gate", "untested"))
        elif mm.get("status") == "pass":
            items.append((name, f'{glyph("pass")}Pass', "every gate measured", None))
        elif gone:
            items.append((name, f'{glyph("fail")}Fail', "", None))
        else:
            fails = [g.get("label") or "" for g in mm.get("gates", []) if g.get("status") == "fail"]
            items.append((name, f'{glyph("fail")}Fail', "needs " + " and ".join(x[:1].lower() + x[1:] for x in fails), None))
    # the one observation that would settle the most
    o = rec.get("observe")
    if o:
        what = cap((observations or {}).get(o.get("best")) or o.get("best") or "")
        w = o.get("window") or {}
        kind, said = next_window(rec)
        if kind == "Next window":
            detail = f"no window, JPL lists {said[:1].lower() + said[1:]}"
        elif kind:
            detail = said[:1].lower() + said[1:]
        else:
            detail = ", ".join(x for x in (o.get("needs") or "", f"window {w['start']} to {w['end']}"
                                           if w.get("start") and w.get("end") else "") if x)
        items.append(("Would settle most", esc(what), detail, None))
    else:
        items.append(("Would settle most", "None", "" if gone else nothing_ranked(rec), None))
    return items


def summary_list(items: list) -> str:
    rows = []
    for name, val, detail, state in items:
        if val is GROUP:
            rows.append(f'<tr class="grp"><th colspan="4" scope="rowgroup">{name}</th></tr>')
            continue
        tag = state_tag(state) if state else ""
        rows.append(f'<tr><th scope="row">{name}</th><td class="v">{val}</td>'
                    f'<td class="d">{nowrap_dates(detail)}</td><td class="s">{tag}</td></tr>')
    return f'<table class="sumlist"><tbody>{"".join(rows)}</tbody></table>'


# ---------------------------------------------------------------- the entry

TOC = (("on-file", "On file"), ("difficulty", "Difficulty"), ("value", "What is in it"),
       ("settle", "What would settle it"), ("missions", "Missions"), ("sources", "Sources"))


def entry(rec: dict, sources: dict, observations: dict | None = None, gates: dict | None = None,
          data_date: str = "") -> str:
    """<main id="entry">: the whole entry. Its <section id="summary"> is what the front page's readout lifts."""
    head, others = names(rec)
    ident = [("Number", str(rec["number"]) if rec.get("number") else "none yet")]
    if rec.get("name"):
        ident.append(("Designation", rec["designation"]))
    first = first_observed(rec)
    if first:
        ident.append(("First observed", first))
    aka = [a for a in others if a not in (str(rec.get("number") or ""), rec["designation"])]
    if aka:
        ident.append(("Also", ", ".join(aka)))
    ident_html = "".join(f'<div><dt>{a}</dt><dd>{nowrap_dates(b)}</dd></div>' for a, b in ident)
    summary = rec.get("summary") or {}
    # a reflectivity drawn for an asteroid whose size is measured follows from that size, not from its brightness
    implied = (rec["rows"].get("size") or {}).get("state") == "measured"
    data_date = data_date or rec.get("data_date") or ""
    rows = "".join(row(rid, rec["rows"].get(rid) or {"state": "unchecked"}, summary, sources,
                       implied and rid == "surface", (gates or {}).get(rid, ()), data_date) for rid in ROWS)
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in TOC)
    unchecked = {s for r in rec["rows"].values() for s in r.get("unchecked") or []} - set(rec.get("sources") or [])
    return (
        f'<main id="entry" class="page entry" data-key="{esc(rec["key"])}">'
        f'<section id="summary" aria-label="Summary">'
        f'<header class="ehead"><h1>{esc(head)}</h1><dl class="ident">{ident_html}</dl></header>'
        f'<details class="toc-m"><summary>On this page</summary><ul>{toc}</ul></details>'
        f'<div class="sum">{rock(rec, sources)}{summary_list(summary_items(rec, sources, observations))}</div>'
        f'</section>'
        f'<div class="body"><nav class="toc" aria-label="On this page"><ul>{toc}</ul></nav><div class="secs">'
        f'<section class="sec" id="on-file"><h2>On file</h2>{rows}</section>'
        f'<section class="sec" id="difficulty"><h2>Difficulty</h2>{ladder(rec.get("ladder") or [])}</section>'
        f'<section class="sec" id="value"><h2>What is in it</h2>{value(rec)}</section>'
        f'<section class="sec" id="settle"><h2>What would settle it</h2>{observe(rec, observations, sources)}</section>'
        f'<section class="sec" id="missions"><h2>Missions</h2>{missions(rec)}</section>'
        f'<section class="sec" id="sources"><h2>Sources</h2>{sources_table(used_sources(rec), sources, unchecked)}</section>'
        f'</div></div></main>'
    )


# ---------------------------------------------------------------- the page shell

NAV = (
    ("index.html", "Field"),
    ("list/observe.html", "Observe next"),
    ("record.html", "Record"),
    (METHOD_PAGE, "Method"),
)
ICON = '<link rel="icon" href="data:,">\n'      # no favicon: without this a browser asks for one and gets a 404
FONT = "static/fonts/b612-regular.woff2"        # site-root relative; style.css names it as fonts/b612-regular.woff2


def rel(url: str, depth: int) -> str:
    """A site-root-relative URL as seen from a page `depth` folders down."""
    if re.match(r"^([a-z][a-z0-9+.-]*:|/)", url):
        return url
    return "../" * depth + url


def head(title: str, assets: dict, depth: int, extra: str = "") -> str:
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{esc(title)}</title>\n{ICON}'
        f'<link rel="preload" href="{esc(rel(assets.get("font", FONT), depth))}" as="font" type="font/woff2" crossorigin>\n'
        f'<link rel="stylesheet" href="{esc(rel(assets["style"], depth))}">\n'
        f'{extra}</head>\n'
    )


def header(depth: int, data_date: str, current: str = "") -> str:
    items = "".join(
        '<li><a href="{}"{}>{}</a></li>'.format(rel(href, depth), ' aria-current="page"' if href == current else "", word)
        for href, word in NAV)
    when = f'<p class="date">Data {date(data_date)}</p>'
    return (f'<header class="site"><a class="mark" href="{rel("index.html", depth)}">{rock_mark()}{SITE}</a>'
            f'<span class="proto">prototype</span><nav aria-label="Site"><ul>{items}</ul></nav>{when}'
            f'<details class="menu"><summary>Menu</summary><nav aria-label="Site menu"><ul>{items}</ul>{when}</nav></details>'
            '</header>\n')


def footer(depth: int, data_date: str, method: str) -> str:
    return (f'<footer class="site-foot"><span>Data as of {date(data_date)}</span>'
            f'<span>Method <a href="{rel(METHOD_PAGE, depth)}">{esc(method)}</a></span></footer>\n')


def page(*, title: str, body: str, kind: str, depth: int, assets: dict, data_date: str,
         method: str, current: str = "") -> str:
    return (
        head(title, assets, depth)
        + f'<body data-page="{kind}">\n'
        + header(depth, data_date, current)
        + f'{body}\n'
        + footer(depth, data_date, method)
        + '</body>\n</html>\n'
    )


# Kept for the method page's lines: one label and what goes with it.

def line(label: str, *parts: str, cls: str = "") -> str:
    """<div><dt>label</dt><dd>value range grade source</dd></div>."""
    c = f' class="{cls}"' if cls else ""
    return f'<div{c}><dt>{label}</dt><dd>{" ".join(p for p in parts if p)}</dd></div>'


def v(text: str, plain: bool = False) -> str:
    """The value itself. `plain` marks words rather than a quantity."""
    return f'<b class="v{" t" if plain else ""}">{text}</b>'


def r(text: str) -> str:
    return f'<span class="r">{text}</span>'
