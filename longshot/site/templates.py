"""HTML fragments as Python functions. Standard library only, no clock, no network.

Everything here takes plain dicts (gen.py converts the dataclasses once) and
returns strings. Text from upstream is escaped at the point it is printed.

The words and marks follow docs/design.md. Two states on the surface (the front page and an
entry's summary): measured, an unbroken rock outline that glows; estimated, a dot. The entry's
record layer adds the bound (a dashed outline) and "not checked: <source>", which is still an
estimate. A mission's verdict is fits (a heavy outline), ruled out (a cross) or unclear (no mark,
its chance beside it). The pipeline's own names (prior, unchecked, pass, fail, untested) stay in
data attributes and are mapped to words here, at display.

Parentheses are conventional: the stylesheet takes them from the fallback font, since B612 draws
its own square.
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
    "reach": "Δv", "tracking": "Orbit", "size": "Diameter",
    "spin": "Spin", "surface": "Composition", "push": "Sunlight push", "density": "Density",
}
# The ledger files a bulk density under the push row; the entry gives it its own block after the push, where it is
# on file, since it answers what the mass rests on, not how sunlight moves the asteroid (docs/design.md section 8).
DENSITY_NOTE = "The density from SsODNet is computed from other values; it is not a measurement."


def _is_density(f: dict) -> bool:
    return (f.get("label") or "").casefold() == "density"


def split_density(rw: dict) -> tuple[dict, dict | None]:
    """(the push row without its densities, a density block or None): the block is 'measured' where a density is
    used, and carries the ledger's note on a computed density."""
    dens = [f for f in rw.get("facts", []) if _is_density(f)]
    if not dens:
        return rw, None
    note = rw.get("note") or ""
    rest = " ".join(x for x in [note.replace(DENSITY_NOTE, "").strip()] if x) or None
    push = dict(rw, facts=[f for f in rw.get("facts", []) if not _is_density(f)], note=rest)
    block = {"state": "measured" if any(used(f) for f in dens) else "prior", "facts": dens,
             "note": DENSITY_NOTE if DENSITY_NOTE in note else None}
    return push, block
# A row's state on the record layer (the entry below its summary, Method). Not checked is an estimate:
# which source was not checked is said on its own line, beside it.
STATE_WORDS = {
    "measured": "Measured", "limit": "Bound",
    "prior": "Estimated", "unchecked": "Estimated",
}
# The surface has two states only: a bound is a measurement, and not checked is an estimate.
SURFACE_WORDS = {"measured": "Measured", "limit": "Measured", "prior": "Estimated", "unchecked": "Estimated"}
STATE_GLYPH = {"measured": "measured", "limit": "limit", "prior": "prior", "unchecked": "prior"}
NOT_CHECKED = "Not checked"
# A mission's verdict, and one condition's.
STATUS_WORDS = {"pass": "Fits", "untested": "Unclear", "fail": "Ruled out"}
CONDITION_WORDS = {"pass": "Met", "untested": "Unclear", "fail": "Failed"}
# One name per mission: the field's filter, an entry's Missions section, the table view's columns.
MISSION_LABELS = {"surface": "Surface work", "capture": "Whole-body capture"}
METHOD_PAGE = "method.html"
RUNG_LABELS = {
    "found_again": "Finding it again", "reached": "Reaching it",
    "workable": "Working on it", "anything_in_it": "Finding anything in it",
    "brought_back": "Bringing any back",
}
RUNG_WORDS = {"measured": "Measured", "prior": "Estimated"}     # an unknown rung's text says what is missing
DV_TITLE = "delta-v: the total change of speed a spacecraft needs for the cheapest round trip"
# Technical terms on the record and reference layers, each defined in a hover note where it first appears
# on a page (define). Longest first, so "Yarkovsky drift rate" is found before "Yarkovsky drift".
TERMS = (
    ("absolute magnitude", "The asteroid's brightness as seen from 1 au, with the Sun 1 au away. "
                           "A lower H means a brighter, and so usually bigger, asteroid."),
    ("orbit condition code", "JPL's rating of how well the orbit is known, from 0, best, to 9, worst."),
    ("Yarkovsky drift", "A slow drift of the orbit. The asteroid takes in sunlight and gives the heat "
                        "out again unevenly, and that pushes it."),
    ("radiation pressure", "The push of sunlight itself on the asteroid."),
    ("reflectivity", "The share of sunlight the surface reflects: geometric albedo."),
    ("spin period", "The time the asteroid takes to turn once."),
    ("lightcurve", "The asteroid's brightness measured over time. It rises and falls as the asteroid turns, "
                   "which gives the spin period."),
    ("signal-to-noise", "How far a value stands above its noise: the value divided by its error."),
    ("thermal model", "A diameter and reflectivity worked out from the heat the asteroid gives off."),
)
CLASS_LABELS = {"S": "S, stony", "C": "C, dark and carbon-rich", "X": "X, possibly metallic", "other": "other"}
CLASS_WORDS = {"S": "Stony", "C": "Carbon-rich", "X": "Possibly metallic"}      # draws.class_group's groups
# A measured class outside those three groups, by its letter, in plain words (draws.class_group's "other").
OTHER_CLASS_WORDS = {"V": "Basaltic", "A": "Olivine-rich", "D": "Dark, primitive", "T": "Dark, primitive",
                     "K": "Stony", "L": "Stony", "R": "Stony", "O": "Stony"}
SPIN_KEYS = ("p_fast_2_2h", "p_under_1h", "p_under_10min")    # the record's shares, one per line in priors.toml


def spin_lines(thresholds_h) -> tuple:
    """((share key, its line in words), ...) from priors.toml [spin].thresholds_h: '2.2 h', '1 h', '10 min'."""
    def words(h):
        return f"{round(h, 2):g} h" if h >= 1 else f"{round(h * 60, 1):g} min"
    return tuple(zip(SPIN_KEYS, (words(h) for h in thresholds_h)))


SPIN_SHARES = spin_lines((2.2, 1.0, 1 / 6))     # gen.write_site sets it from the method files
GATE_BASIS = {"measured": "measured", "prior": "estimated"}
GATE_ROW = {"findable": "tracking", "size": "size", "spin": "spin", "mass": "size"}

# A fact's label is its stable id in the ledger (longshot.ledger.LABEL). These are the words printed for it,
# so one thing has one name on the page.
FACT_WORDS = {
    "delta-v": "Δv, cheapest round trip",
    "trip at lowest delta-v": "duration, cheapest round trip",
    "shortest trip": "duration, shortest round trip",
    "delta-v of shortest trip": "Δv, shortest round trip",
    "condition code": "orbit condition code",
    "arc": "observed over",
    "window start": "window opens",
    "window end": "window closes",
    "window pointing": "telescope can point at it",
    "H": "absolute magnitude (H)",
    "period": "spin period",
    "amplitude": "lightcurve amplitude",
    "albedo": "reflectivity",
    "A1": "radiation pressure, A1",
    "A2": "Yarkovsky drift, A2",
    "A3": "out-of-plane push, A3",
    "drift": "Yarkovsky drift rate",
}


def condition(label) -> str:
    """A mission condition's label as the pages print it: the method file's own words, with the orbit's
    code named in full."""
    return re.sub(r"\b([Oo])rbit code\b", r"\1rbit condition code", "" if label is None else str(label))

# Upstream method tags, in words. A tag not listed is printed as it is. The catalogues' own codes (SMASSII, SAGE,
# Bin-PheMu) and the names of class schemes are not printed: the words say how the value was found.
GRADE_WORDS = {
    "space": "spacecraft",
    "neatm": "thermal model",
    "tpm": "thermophysical model",
    "radar": "radar",
    "radar-3d": "radar shape model",
    "sage": "shape model",
    "polarimetry": "polarimetry",
    "computed": "computed from other values",
    "astrometry(o)": "fit to optical positions",
    "astrometry(o+r)": "fit to optical and radar positions",
    "yarkovsky": "from its drift",
    "srp": "from radiation pressure",
    "yarkovsky+srp": "from drift and radiation pressure",
    "bin-phemu": "from a binary's eclipses",
    "smassii": "from a visible spectrum",
    "tholen": "from colours",
    "sidereal": "", "synodic": "",          # the kind of period: a difference far below the error, so left out
}
_TAXONOMY = re.compile(r"^(?P<scheme>.+?) (?P<how>Spec|Phot) (?P<band>VISNIR|VIS|NIR)$")
_HOW = re.compile(r"^(?P<how>Spec|Phot)\b[ ,:]*(?P<rest>.*)$")     # a hand-entered class: how, then the detail
_BANDS = {"VIS": "visible", "NIR": "near-infrared", "VISNIR": "visible and near-infrared"}
_HOW_WORDS = {"Spec": "spectrum", "Phot": "colours"}
# The way a period was found, from the lightcurve tables' codes; "sidereal" and "synodic" are left out.
_PERIOD_HOW = {"lc": "lightcurve", "lci": "lightcurve inversion", "space": "spacecraft", "radar": "radar",
               "sage": "shape model"}
_PERIOD_NOTE = re.compile(r"^(?:sidereal|synodic), (?P<how>[\w+-]+)(?P<rest>;.*)?$", re.I)
_SNR = re.compile(r"signal-to-noise (\d+(?:\.\d+)?)")
# Values printed in words: a window's pointing.
VALUE_WORDS = {"pointable": "yes", "survey-only": "no"}
HIDDEN_FACTS = ("trajectories",)     # a count of the trajectories JPL searched: it answers no question here

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


def plain(s) -> str:
    """Upstream text as a string, '' for None. Its parentheses stay: the fallback font draws them."""
    return "" if s is None else str(s)


def nb(text: str) -> str:
    """A value and its unit, kept on one line."""
    return text.replace(" ", " ")


def nowrap_dates(text: str) -> str:
    """Escaped text in which a date never breaks across lines."""
    return _DATES.sub(r'<span class="nb">\1</span>', esc(text))


_URL_IN = re.compile(r"https?://\S+")
# The method files say where each figure comes from inside the project (a research note, a script, a review).
# The page is for visitors: it keeps the published sources and the reasoning, and leaves out every clause that
# only points into the project. The files themselves keep the full trail.
_INTERNAL = re.compile(
    r"docs/|data/|tools/|build/|method/|registry/|AGENTS\.md|\b[\w.-]+\.(?:md|py|toml|txt|jsonl)\b"
    r"|\b[a-z0-9]+_[a-z0-9_]+\b|saved copy|project file|\breview of 20\d\d|\bthe plan\b|\bplan's\b|\bWP\d"
    r"|\bthe checker\b|\bthe sketch\b|\bderivation's\b|\bon disk\b|\bthe reviewer's\b",
    re.I)
# The research files grade each citation by how close it is to the evidence: P, primary; S, secondary. The tag
# is the project's own, so a page leaves it out: 'Shepard et al. 2015, P abstract' -> 'Shepard et al. 2015'.
_GRADE_TAG = re.compile(r",\s*[PS](?:\s+abstract)?(?=\s*(?:[.;,)]|$))")
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


def _internal(text: str) -> bool:
    return bool(_INTERNAL.search(_URL_IN.sub("", text)))


def public_text(text) -> str:
    """A line from a method file as a visitor reads it: no paths into the project or its own citation
    grades, kg/m³ and ± in place of kg/m3 and +/-."""
    text = _GRADE_TAG.sub("", "" if text is None else str(text))
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
    text = re.sub(r"(?<![\w.])([0-3])-(?=[\s.,;:)]|$)", "\\1−", text)       # a lightcurve grade: 2−, a true minus
    return text.replace("kg/m3", "kg/m³").replace("+/-", "±")


def define(page: str, terms=TERMS) -> str:
    """The page with each technical term defined in a hover note where it first appears in its text.

    Text inside a link, a heading of the page's own title, an existing definition, a script or a style is
    left alone, and so are attribute values."""
    left = {t.casefold(): (t, d) for t, d in terms}
    out, skip = [], 0
    for part in re.split(r"(<[^>]+>)", page):
        if part.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", part)
            tag = (m[1].lower() if m else "")
            if tag in ("a", "dfn", "abbr", "script", "style", "title", "h1", "button", "svg", "option", "output"):
                skip += -1 if part.startswith("</") else (0 if part.endswith("/>") else 1)
            out.append(part)
            continue
        if skip or not left:
            out.append(part)
            continue
        at, done = 0, []
        while left:
            found = [(m, key) for key, (word, _) in left.items()
                     for m in [re.compile(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", re.I).search(part, at)] if m]
            if not found:
                break
            m, key = min(found, key=lambda x: x[0].start())
            done.append(part[at:m.start()] + f'<dfn title="{esc(left.pop(key)[1])}">{m[0]}</dfn>')
            at = m.end()
        out.append("".join(done) + part[at:])
    return "".join(out)


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
        return "<1%"
    if 0.995 <= p < 1:
        return ">99%"
    return f"{hundredths(p)}%"


def chance(p) -> str:
    """A chance counted from draws. None passing, or all, is still not certainty: '<1%', '>99%'."""
    if not is_num(p):
        return ""
    if p < 0.005:
        return "<1%"
    if p >= 0.995:
        return ">99%"
    return pct(p)


def usd(x) -> str:
    if not is_num(x):
        return ""
    for size, word in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million"), (1e3, "thousand")):
        if abs(x) >= size:
            return f"${num(x / size, 2)}\u00a0{word}"
    return f"${num(x, 2)}"


def usd_range(lo, hi) -> str:
    """A range of dollars: '$31–39 thousand' when both ends share a scale word, '$1.8 million to $1.9 billion'
    when they do not (docs/design.md section 6)."""
    a, b = usd(lo), usd(hi)
    wa, wb = a.partition("\u00a0")[2], b.partition("\u00a0")[2]
    if wa == wb:
        return f"{a.partition(chr(160))[0]}–{b[1:]}"
    return f"{a} to {b}"


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
    if sig > 2 and _decimals(a) and _decimals(b) and "×" not in a + b:      # an estimate keeps two figures each end
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
    """A range of mass: '13,000–550,000 t', '1.5–3.6 million t'; 'to' when the ends differ in their scale word,
    '71,000 t to 3.6 million t' (docs/design.md section 6)."""
    (a, wa), (b, wb) = _scaled(lo), _scaled(hi)
    words = lambda n, w: n + (f"\u00a0{w}" if w else "") + f"\u00a0{unit}"
    if wa == wb:
        return f"{a}–{words(b, wb)}"
    return f"{words(a, wa)} to {words(b, wb)}"


def sig2(v) -> str:
    """An estimate to two significant figures, as the front page prints it (app.js sig2): '0.83', '3.0', '1,200'."""
    if not v:
        return "0"
    d = 1 - math.floor(math.log10(abs(v)))
    r = round(v * 10 ** d) / 10 ** d
    return f"{r:.{d}f}" if d > 0 else f"{round(r):,}"


def estimate_span(lo, hi, unit: str = "") -> str:
    """An estimate's range, both ends to two significant figures: '0.83–3.0 m', '23–85 m'."""
    return with_unit(f"{sig2(lo)}–{sig2(hi)}", unit)


def date(s) -> str:
    return f"<time>{esc(s)}</time>"


def u(unit: str) -> str:
    """A unit beside a value, in the label grey."""
    return f'<span class="u">{esc(unit)}</span>' if unit else ""


# ---------------------------------------------------------------- sources

def source_name(sources: dict, sid: str) -> str:
    """A source's name as interface copy: 'Asteroid Lightcurve Database, LCDB' (unparen)."""
    s = sources.get(sid)
    return plain(s.get("name") or sid) if s else sid


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
    """A grade or method tag as the page prints it (escaped): 'grade 2−', 'from a visible spectrum'."""
    q = (quality or "").strip()
    if not q:
        return ""
    if row_id == "spin" and _U_CODE.match(q):
        return f"grade {esc(q.replace('-', '−'))}" + (", unreliable" if unreliable(q) else "")
    m = _HOW.match(q)
    if m:
        return esc(f"from {_HOW_WORDS[m['how']]}" + (f": {m['rest']}" if m["rest"] else ""))
    words = [_tag(part.strip()) for part in q.split(",")]
    return esc(_SNR.sub(lambda m: f"signal-to-noise {num(float(m[1]), 3)}", ", ".join(w for w in words if w)))


def _tag(tag: str) -> str:
    """One upstream tag in words; a tag with no words here is printed as it is. 'SAGE+Radar-3D' is two tags."""
    if tag.casefold() in GRADE_WORDS:
        return GRADE_WORDS[tag.casefold()]
    m = _TAXONOMY.match(tag)
    if m:
        band = _BANDS[m["band"]]
        return f"class from a {band} spectrum" if m["how"] == "Spec" else f"class from {band} colours"
    if "+" in tag and all(x.casefold() in GRADE_WORDS for x in tag.split("+")):
        return ", ".join(GRADE_WORDS[x.casefold()] for x in tag.split("+"))
    return tag


def fact_note(note) -> str:
    """A fact's note as the page prints it (not escaped): a lightcurve table's method code in words, the period
    type left out; a signal-to-noise to three figures."""
    text = plain(note).strip()
    m = _PERIOD_NOTE.match(text)
    if m:
        return _PERIOD_HOW.get(m["how"].casefold(), m["how"]) + (m["rest"] or "")
    return _SNR.sub(lambda m: f"signal-to-noise {num(float(m[1]), 3)}", text)


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


def _size_facts(rec: dict, sources: dict):
    """(the size row's state, its usable diameters or bounds), adopted first."""
    row = rec["rows"].get("size", {})
    facts = row.get("facts", [])
    state = row.get("state")
    kinds = {"measured": ("value",), "limit": ("upper", "lower")}.get(state, ())
    return state, [f for f in facts
                   if f.get("kind", "value") in kinds and is_num(f.get("value")) and used(f)
                   and _metres(f) and f["value"] > 0]


def size_of(rec: dict, sources: dict) -> dict | None:
    """The size to draw: {lo, mid, hi (metres; lo and hi may be None), state, kind, source, quality}.

    The row's state decides. Measured: the first diameter value (the ledger puts the
    adopted one first). Limit: the first bound. Otherwise the
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


def used(f: dict) -> bool:
    """False for a value the ledger keeps on file and does not count (Fact.used)."""
    return f.get("used", True) is not False


def _is_period(f: dict) -> bool:
    return (f.get("kind", "value") == "value" and is_num(f.get("value"))
            and f["value"] > 0 and f.get("unit") in TIME_S)


def not_checked(row: dict, sources: dict) -> str:
    """'SsODNet, Pravec': the sources a row was not checked against; '' when all were."""
    return ", ".join(source_name(sources, s) for s in row.get("unchecked") or [])


def shown_period(rec: dict, sources: dict) -> tuple[dict | None, str]:
    """(the period fact the page shows and turns the rock by, reason). The fact is the period the spin row
    rests on (its first used one), set only when the row is measured and its sources do not disagree, so the
    entry turns at the rate the field turns at. Otherwise the reason says why not: and never "no spin period
    on file" while a source for the row was not checked."""
    row = rec["rows"].get("spin", {})
    on_file = [f for f in row.get("facts", []) if _is_period(f)]
    periods = [f for f in on_file if used(f)]
    if row.get("state") != "measured" or not periods:
        if row.get("unchecked") or row.get("state") == "unchecked":
            names = not_checked(row, sources)
            return None, "spin period not checked" + (f": {names}" if names else "")
        return None, "no spin period good enough to use" if on_file else "no spin period on file"
    if row.get("conflicts"):
        return None, "sources disagree on the spin period"
    return periods[0], ""


def period_of(rec: dict, sources: dict) -> tuple[float | None, str]:
    """(seconds, reason): shown_period's period in seconds."""
    f, why = shown_period(rec, sources)
    return (f["value"] * TIME_S[f["unit"]], "") if f else (None, why)


# ---------------------------------------------------------------- marks

GLYPHS = ("measured", "limit", "prior", "pass", "fail")     # an unclear verdict has no mark: its chance says it


def glyph(state: str, said: str = "") -> str:
    """The mark for a row state or a mission verdict, drawn as the field draws it: a measured outline,
    a bound's dashed outline, an estimate's dot; fits, a heavy outline; ruled out, a cross.

    One empty element: style.css draws each mark (.g-measured and the rest), so a page that lists two
    thousand asteroids carries a class name per mark, not an outline. `said` gives it the state in words
    for a reader that does not see it; otherwise the words beside it say it and the mark is hidden."""
    state = STATE_GLYPH.get(state, state)
    if state not in GLYPHS:
        return ""
    aria = f'role="img" aria-label="{esc(said)}"' if said else 'aria-hidden="true"'
    return f'<i class="g g-{state}" {aria}></i>'


def state_tag(state: str, word: str | None = None, surface: bool = False) -> str:
    """A state's mark and word: the surface's two states, or the record layer's three."""
    words = SURFACE_WORDS if surface else STATE_WORDS
    word = word or words.get(state) or STATUS_WORDS.get(state) or cap(state)
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
            f'<polygon points="{p}"/></svg>')     # no glow: the glow means measured


def _nice_near(x: float) -> float:
    """A round length (1, 2 or 5 times a power of ten) near x."""
    e = math.floor(math.log10(x))
    return min((m * 10.0 ** k for k in (e - 1, e, e + 1) for m in (1, 2, 5)), key=lambda v: abs(math.log(v / x)))


def _seconds(sec: float) -> str:
    """A CSS duration that keeps four figures and never prints an exponent."""
    return f"{float(f'{sec:.4g}'):.3f}".rstrip("0").rstrip(".") + "s"


NESTED_FROM = 1.25      # the low and high outlines are drawn when the range spans this ratio or more
ONE_SIGMA = "±1σ"       # what a stated range beside a measured value is (method/v0_1/missions.toml [rules.decide])
ESTIMATE_RANGE = "90% range"    # what the range of an estimate is: its 5th to 95th percentile
ROCK_BOX = 240
BOUND_SIGN = {"upper": "≤ ", "lower": "≥ "}


def rock(rec: dict, sources: dict) -> str:
    """The asteroid to scale: its diameter range as nested outlines, turning at its measured rate."""
    name = rec.get("name") or rec["designation"]
    size = size_of(rec, sources)
    period, why = period_of(rec, sources)
    if rec.get("gone"):                     # drawn as it was last known; nothing is left to turn
        period, why = None, "it no longer exists"
    if size is None:
        return '<figure class="rockfig"><p class="none">No brightness on file, so no outline</p></figure>'
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
        caption = f"Outlines: measured, and {ONE_SIGMA}" if nested else "Outline: measured"
        alt = f"{name}, {show(size['mid'], 3)} across"
    elif state == "limit":
        caption = "Outline: the bound"
        alt = f"{name}, {BOUND_SIGN.get(size['kind'], '')}{show(size['mid'], 3)} across"
    else:
        caption = f"Outlines: median estimate, and {ESTIMATE_RANGE}" if nested else "Outline: median estimate"
        held = not_checked(srow, sources) if state == "unchecked" else ""
        alt = f"{name}, diameter estimated, median {show(size['mid'])}" + (
            f"; {NOT_CHECKED.lower()}: {held}" if held else "")
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
    return (f'<figure class="rockfig s-{state}">'
            f'<svg viewBox="{-half:g} {-half:g} {ROCK_BOX} {ROCK_BOX + 34}" role="img" aria-label="{esc(alt)}">'
            f'<g{turn}>{"".join(shapes)}</g>{scale}</svg>'
            f'<figcaption>{esc(caption)}</figcaption></figure>')


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
_ROW_SAYS = {"reach": "Δv", "tracking": "orbit condition code, 0 best", "size": "diameter", "spin": "spin period",
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
        lines[row_id] = [(v, condition(items[0][2]) if len(items) > 1 else f"{items[0][0]}: {MISSION_LABELS.get(items[0][1], items[0][1]).lower()}")
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
            said = f"{_ROW_SAYS[row_id]} estimated, {ESTIMATE_RANGE}"
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
            f'<i class="axis"></i><i class="yr d0" style="left:0"><span>Data date {esc(data_date)}</span></i>'
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
        sign = BOUND_SIGN.get(f.get("kind", "value"), "")
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
        rng = f"{span(lo * k, hi * k, unit, sig)} ({ONE_SIGMA})" if ranged else ""
        return sign + with_unit(shown, unit), rng, extra
    if isinstance(val, str) and _ISO_DATE.match(val.strip()):
        return date(val.strip()), "", ""
    if val is None or val == "":
        return "no value given", "", ""
    if isinstance(val, str) and val in VALUE_WORDS:
        return VALUE_WORDS[val], "", ""
    unit = UNITS.get(f.get("unit"), f.get("unit"))
    return esc(val) + (f" {esc(unit)}" if unit else ""), "", ""


FACT_COLS = ('<colgroup><col class="c-l"><col class="c-v"><col class="c-r"><col class="c-q"><col class="c-s">'
             '</colgroup>')


_SOLUTION = re.compile(r"\borbit solution JPL (\S+)")


def _ref(ref) -> str:
    """A fact's reference as printed: one spelling of an orbit solution ('orbit solution 118')."""
    return _SOLUTION.sub(r"orbit solution \1", plain(ref))


def facts_table(row_id: str, facts: list, sources: dict, counted: bool = False) -> str:
    """The row's facts, one line each: label, value, 1σ range, grade and note, source, in the ledger's order, so
    the first used line is the one the row rests on. A source every line shares is printed once, under."""
    facts = [f for f in facts if f.get("label") not in HIDDEN_FACTS]
    cites = {(f.get("source", ""), f.get("ref")) for f in facts}
    once = len(cites) == 1 and len(facts) > 1
    lines = []
    for f in facts:
        name = cap(label(row_id, f.get("label")))
        cite = source_link(sources, f.get("source", "")) + (f", {esc(_ref(f['ref']))}" if f.get("ref") else "")
        val, rng, extra = _value(row_id, f)
        if extra:
            name += f", {extra}"
        g = grade(row_id, f.get("quality"))
        q = ", ".join(x for x in (plain(g), esc(fact_note(f.get("note") or ""))) if x)
        tag = "" if used(f) else '<span class="tag">not used</span>'
        lines.append(f'<tr{"" if used(f) else ' class="nu"'}><th scope="row">{esc(name)}</th><td class="v">{val}</td>'
                     f'<td class="r">{rng}{" " if rng and tag else ""}{tag}</td><td class="q">{q}</td><td class="s">{"" if once else cite}</td></tr>')
    if not lines:
        return ""
    tail = ""
    if once:
        sid, ref = next(iter(cites))
        tail = (f'<p class="srcline">Source: {source_link(sources, sid)}'
                + (f", {esc(_ref(ref))}" if ref else "") + "</p>")
    return f'<table class="facts">{FACT_COLS}<tbody>{"".join(lines)}</tbody></table>{tail}'


def _odds(p: dict, summary: dict) -> str:
    """The chance of each fast spin at this brightness, with the spread between surveys where there is one."""
    out, spread = [], False
    rng = p.get("range") or {}
    for key, name in SPIN_SHARES:
        v = p.get(key, summary.get(key))
        if not is_num(v):
            continue
        r = rng.get(key) if isinstance(rng.get(key), (list, tuple)) and len(rng.get(key)) == 2 else None
        r = r if r and all(is_num(x) for x in r) else None
        spread = spread or r is not None
        out.append((name, chance(v), f"{hundredths(r[0])}–{hundredths(r[1])}%" if r else ""))
    if not out:
        return ""
    head = ('<th scope="col">Spin period under</th><th scope="col" class="num">Chance</th>'
            + ('<th scope="col" class="num">Across surveys</th>' if spread else ""))
    body = "".join(f'<tr><th scope="row">{esc(n)}</th><td class="num" data-l="Chance">{esc(c)}</td>'
                   + (f'<td class="num" data-l="Across surveys">{esc(x)}</td>' if spread else "") + "</tr>"
                   for n, c, x in out)
    return f'<table class="tbl mini odds"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _shares(shares: dict) -> str:
    """The share of each class at this brightness, largest first."""
    keys = [c for c in ("S", "C", "X", "other") if is_num(shares.get(c))]
    keys += [c for c in sorted(shares) if c not in keys and is_num(shares.get(c))]
    if not keys:
        return ""
    body = "".join(f'<tr><th scope="row">{esc(cap(CLASS_LABELS.get(c, c)))}</th>'
                   f'<td class="num" data-l="Share">{hundredths(shares[c])}%</td></tr>'
                   for c in sorted(keys, key=lambda c: -shares[c]))
    return ('<table class="tbl mini shares"><thead><tr><th scope="col">Class</th><th scope="col" class="num">Share</th>'
            f'</tr></thead><tbody>{body}</tbody></table>')


def prior(row_id: str, row: dict, summary: dict, implied: bool = False) -> str:
    """The estimate, for a row no source on file gives a value for: the range first, never a single figure.

    `implied` marks a reflectivity that follows from the asteroid's own measured diameter and H:
    it is not what is typical at its brightness, and it can come out above 100%.
    """
    if row.get("state") not in ("prior", "unchecked"):
        return ""
    p = row.get("prior") or {}
    out = []
    if is_num(p.get("q05")) and is_num(p.get("q95")):
        surface = row_id == "surface"
        k, unit = scale_for(row_id, "albedo" if surface else "", p.get("unit"), p["q95"])
        name = "Reflectivity, estimated" if surface else f"{ROW_LABELS.get(row_id, cap(row_id))}, estimated"
        how = f"{ESTIMATE_RANGE}, from its diameter and H" if surface and implied else ESTIMATE_RANGE
        flag = "over 100% is impossible: its diameter or H is off" if surface and unit == "%" and p["q95"] * k > 100 else ""
        out.append(f'<table class="facts est">{FACT_COLS}<tbody><tr class="pr"><th scope="row">{name}</th>'
                   f'<td class="v">{estimate_span(p["q05"] * k, p["q95"] * k, esc(unit))}</td><td class="r">{how}</td>'
                   f'<td class="q">{flag}</td><td class="s">{esc(cap(plain(p.get("basis"))))}</td></tr></tbody></table>')
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
    (re.compile(r"^(?:.* is )?(older than this asteroid)$", re.I), lambda m: m[1].lower()),
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
    counted = state in ("measured", "limit")
    parts = [gauge(row_id, rw, sources, gates)]
    if row_id == "tracking":
        window = [f for f in facts if str(f.get("label", "")).startswith("window")]
        rest = [f for f in facts if f not in window]
        parts.append(facts_table(row_id, rest, sources, counted))
        when = {f["label"]: f.get("value") for f in window}
        if isinstance(when.get("window start"), str) and isinstance(when.get("window end"), str):
            parts.append(timeline(when["window start"], when["window end"], data_date))
        parts.append(facts_table(row_id, window, sources))
    else:
        parts.append(facts_table(row_id, facts, sources, counted))
    parts.append(prior(row_id, rw, summary, implied))
    note = rw.get("note")
    if rw.get("unchecked"):
        # one line names every source not checked and says why; the note keeps what is not about them
        whys, note = unchecked_reasons(rw)
        names = "; ".join(source_link(sources, s) + (f", {esc(w)}" if w else "")
                          for s, w in zip(rw["unchecked"], whys))
        parts.append(f'<p class="un">{NOT_CHECKED}: {names}</p>')
    for c in rw.get("conflicts", []):
        parts.append(f'<p class="conflict"><span class="k">Sources disagree</span> {esc(c)}</p>')
    if note:
        parts.append(f'<p class="note">{esc(note)}</p>')
    if not "".join(parts):
        parts.append('<p class="none">None on file</p>')
    heading = "Delta-v (Δv)" if row_id == "reach" else ROW_LABELS[row_id]    # spelled out once on the page
    # A state mark answers "how sure is this?". Δv and the orbit are JPL's for every asteroid, so they carry none;
    # nor does a sunlight push that is not measured, since nothing estimates it (docs/design.md section 3).
    marked = row_id not in ("reach", "tracking") and (row_id not in ("push", "density") or counted)
    return (
        f'<section class="row" id="row-{row_id}" data-row="{row_id}" data-state="{esc(state)}" '
        f'aria-labelledby="h-{row_id}"><div class="rh"><h3 id="h-{row_id}">{heading}</h3>'
        f'{state_tag(state) if marked else ""}</div><div class="rb">{"".join(parts)}</div></section>'
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
        name = esc(RUNG_LABELS.get(r.get("rung"), r.get("rung")))
        if r.get("rung") in RUNG_LABELS:
            name = method_link(f'rung-{r["rung"]}', name)
        parts = [p for p in r.get("parts") or [] if p.get("label") and p.get("text")]
        if parts:       # the last rung's two amounts, one line each: the parts' texts joined are the rung's text
            said = ('<table class="tbl prec"><thead><tr><th scope="col">Amount</th><th scope="col">Done so far</th></tr></thead><tbody>'
                    + "".join(f'<tr><th scope="row">{esc(p["label"])}</th><td>{esc(cap(p["text"]))}</td></tr>'
                              for p in parts) + '</tbody></table>')
        else:
            said = f'<p>{esc(r.get("text"))}</p>'
        # no state mark: a step is not a value, and its sentence says what it rests on
        items.append(f'<li data-status="{esc(status)}"><span class="n">{i}</span><h3>{name}</h3>'
                     f'<div class="rt">{said}</div></li>')
    return f'<ol class="ladder">{"".join(items)}</ol>'


def _q(d, a="q05", b="q95"):
    d = d or {}
    return (d.get(a), d.get(b)) if is_num(d.get(a)) and is_num(d.get(b)) else None


VALUE_PARTS = (("metal", "Platinum-group metal, in metal grains"), ("water", "Water, bound in minerals"))


def _figure(x: float) -> str:
    """An amount already rounded by the pipeline, as a table cell: '400', '4,000', '0.07', '2.2 million'."""
    if x >= 1e6:
        return f"{num(x / 1e6, 2)}\u00a0million"
    return f"{x:,.0f}" if x >= 100 else f"{x:.3f}".rstrip("0").rstrip(".")


def _amount(pair, k: float) -> str:
    lo, hi = (v * k for v in pair)
    if lo == hi:
        return _figure(lo)
    a, b = _figure(lo), _figure(hi)
    return f"{a} to {b}" if ("million" in a) != ("million" in b) else f"{a}–{b}"


def _amounts(rows: list, key: str, unit: str) -> tuple[str, list[str]] | None:
    """(the column's unit, its cells) for amounts the record carries as numbers (value.table's kg_n, tonnes_n):
    kg, or t when the largest is 10,000 kg or more, so the unit is in the header and not in the cells. None when a
    row carries its figure only as text."""
    if any(r.get(key.removesuffix("_n")) and not r.get(key) for r in rows):
        return None
    top = max((max(r[key]) for r in rows if r.get(key)), default=0)
    if unit == "kg" and top >= 10_000:
        unit, k = "t", 0.001
    else:
        k = 1.0
    return unit, [_amount(r[key], k) if r.get(key) else "" for r in rows]


def _vtable(part: str, rows: list) -> str:
    """One price table from record.value.table: every figure as the record's statements print it, the units in the
    headers (docs/design.md section 6). A column with nothing in it is left out."""
    cols = [("Of 100", [plain(r.get("of100") or "") for r in rows])]
    if part == "metal":
        got = _amounts(rows, "kg_n", "kg")
        cols.append((f"Metal ({got[0]})", got[1]) if got else ("Metal", [plain(r.get("kg") or "") for r in rows]))
        cols.append(("At list price ($)", [plain(r.get("usd") or "").replace("$", "") for r in rows]))
    else:
        got = _amounts(rows, "tonnes_n", "t")
        cols.append(("Water (t)", got[1]) if got else ("Water", [plain(r.get("tonnes") or "") for r in rows]))
    cols = [(h, cells) for h, cells in cols if any(cells)]
    head = '<th scope="col">Holds</th>' + "".join(f'<th class="num" scope="col">{h}</th>' for h, _ in cols)
    body = "".join(
        f'<tr><th scope="row">{esc(r.get("label"))}</th>'
        + "".join(f'<td class="num" data-l="{h}">{esc(cells[i])}</td>' for h, cells in cols) + "</tr>"
        for i, r in enumerate(rows))
    return f'<table class="tbl vt"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def value(rec: dict) -> str:
    """What is in the rock: the record's own table or sentences, the chance of nothing first. The mass is
    the summary's to say."""
    val = rec.get("value") or {}
    if rec.get("gone"):
        return '<p class="none">No estimate: it no longer exists</p>'
    out = []
    table = val.get("table")
    if table and not val.get("sample"):
        for part, title in VALUE_PARTS:
            p = table.get(part) or {}
            if p.get("rows"):
                out.append(f'<div class="vblock"><h3>{title}</h3>{_vtable(part, p["rows"])}</div>')
        priced = any(r.get("usd") for r in (table.get("metal") or {}).get("rows") or [])
        notes = [n for n in table.get("notes") or [] if n] + ([f'Prices: {val["basis"]}'] if val.get("basis") and priced else [])
        if notes:
            out.append(f'<div class="foot-notes">{"".join(f"<p>{esc(n)}</p>" for n in notes)}</div>')
        return f'<div class="value">{"".join(out)}</div>'
    statements = [s for s in val.get("statements") or [] if s]
    ids = val.get("statement_ids") or []
    if statements:
        water_ids = ("water", "sample")
        if len(ids) == len(statements):
            said = {"metal": [s for s, i in zip(statements, ids) if not str(i).startswith(water_ids)],
                    "water": [s for s, i in zip(statements, ids) if str(i).startswith(water_ids)]}
        else:
            said = {"metal": statements, "water": []}
        for part, title in VALUE_PARTS:
            if said[part]:
                out.append(f'<div class="vblock"><h3>{title}</h3>'
                           f'<ul class="stm">{"".join(f"<li>{esc(s)}</li>" for s in said[part])}</ul></div>')
        if not said["metal"]:                   # nothing priced: the price rule has nothing to say
            val = {k: v for k, v in val.items() if k != "basis"}
    else:
        # Only when the pipeline wrote no sentences: the bare ranges, the chance of nothing first.
        metal, water = val.get("metal") or {}, val.get("water") or {}
        lines = []
        if is_num(metal.get("p_nothing")):
            lines.append(("Chance of no separable metal", pct(metal["p_nothing"]), ""))
        if _q(metal.get("kg")):
            lines.append(("Platinum-group metal, if any", amount(*_q(metal["kg"]), "kg"), ESTIMATE_RANGE))
        if _q(metal.get("usd")):
            a, b = _q(metal["usd"])
            lines.append(("That metal at list prices", f"{usd(a)} to {usd(b)}", ESTIMATE_RANGE))
        if is_num(water.get("p_nothing")):
            lines.append(("Chance of no water", pct(water["p_nothing"]), ""))
        if _q(water.get("tonnes")):
            lines.append(("Water, if any", amount(*_q(water["tonnes"]), "t"), ESTIMATE_RANGE))
        if lines:
            out.append('<dl class="kv">' + "".join(f"<dt>{a}</dt><dd>{esc(b)}" + (f' ({c})' if c else "")
                                                   + "</dd>" for a, b, c in lines) + "</dl>")
    if val.get("basis"):
        out.append(f'<p class="foot-notes">Prices: {esc(val["basis"])}</p>')
    if not out:
        return '<p class="none">No estimate: no brightness on file</p>'
    return f'<div class="value">{"".join(out)}</div>'


def no_window(rec: dict) -> str:
    """What the tracking row says when JPL lists no window, so the site has one phrase for it."""
    f = _first(rec["rows"].get("tracking", {}).get("facts", []),
               lambda f: f.get("label") == "next window" and isinstance(f.get("value"), str) and f["value"])
    return f["value"] if f else "none on file"


def settles(rec: dict) -> tuple[str, str]:
    """(the condition an observation decides, the mission it belongs to), from the record's own gates; '' if
    unnamed."""
    o = rec.get("observe") or {}
    m = (rec.get("missions") or {}).get(o.get("mission")) or {}
    g = _first(m.get("gates", []), lambda g: g.get("id") == o.get("gate") and g.get("label"))
    return (condition(g["label"]), MISSION_LABELS.get(o["mission"], o["mission"]).lower()) if g else ("", "")


def nothing_ranked(rec: dict) -> str:
    """Why no observation is ranked, in a few words. The missions' own results are under Missions, not here."""
    missions = [(rec.get("missions") or {}).get(mid) or {} for mid in MISSION_LABELS]
    if rec.get("gone"):
        return "it no longer exists"
    if any(g.get("id") == "findable" and g.get("status") == "fail" for m in missions for g in m.get("gates", [])):
        return "orbit not good enough to find it again"
    states = [m.get("status") for m in missions]
    if "untested" not in states and all(states):
        return "both verdicts rest on measurements"
    return "no single observation would change a verdict"


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
    what = obs_name(observations, o.get("best"))
    if gate and what:
        lines.append(("Observation", esc(what)))
        g = _first(((rec.get("missions") or {}).get(o.get("mission")) or {}).get("gates", []), lambda g: g.get("id") == o.get("gate"))
        lines.append(("Decides", f"{esc(gate)}, for {esc(mission)}"))     # its chance is under Missions, once
    elif o.get("text"):
        lines.append(("Observation", esc(o["text"])))
    kind, said = next_window(rec)
    if kind:                                    # no telescope can be pointed at it yet: the window says why
        lines.append((kind, esc(said)))
    elif o.get("needs"):
        lines.append(("Telescope", esc(cap(o["needs"]))))
    if o.get("unchecked"):                      # the measurement may already exist there
        lines.append((NOT_CHECKED, ", ".join(source_link(sources or {}, s) for s in o["unchecked"])))
    return '<dl class="kv">' + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in lines) + "</dl>"


def obs_name(observations: dict | None, oid, surface: bool = False) -> str:
    """An observation's name from observe.toml: its technical name (`label`) on the record and reference layers,
    its plain one (`plain`) on the surface. `observations` maps an id to {label, plain}, or to the label alone."""
    o = (observations or {}).get(oid)
    if isinstance(o, dict):
        return (o.get("plain") if surface else None) or o.get("label") or ""
    return o or ""


def verdict(m: dict | None) -> tuple[str, str, str]:
    """(the pipeline's status, the verdict as HTML with its mark, its chance in words or '')."""
    status = (m or {}).get("status", "untested")
    word = STATUS_WORDS.get(status, cap(status))
    if status == "untested":
        p = (m or {}).get("p")
        return status, word, f"{esc(chance(p))} chance it fits" if is_num(p) else ""
    return status, f"{glyph(status)}{word}", ""


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
            ch = esc(chance(g["p"])) if st == "untested" and is_num(g.get("p")) else ""
            basis = GATE_BASIS.get(g.get("basis"), esc(g.get("basis")))
            row = rec["rows"].get(GATE_ROW.get(g.get("id"))) or {}
            if g.get("basis") == "prior" and row.get("state") == "unchecked":
                basis = f"estimated; a source {NOT_CHECKED.lower()}"     # its row names the source
            note = plain(g.get("text") or "")
            prose = bool(_ENDS_A_SENTENCE.search(note))         # a sentence is set as prose (docs/design.md section 5)
            text = f'<p class="gtext{" t" if prose else ""}">{esc(note)}</p>' if note else ""
            what = esc(condition(g.get("label")))
            if rec.get("gone"):
                # the method fails a gone asteroid's orbit condition with the reason (missions.toml [rules.gone]);
                # the page names what failed, and the summary's Gone row gives the reason once
                what, text = "Still exists", ""
            elif g.get("id"):
                what = method_link(f'g-{mid}-{g["id"]}', what)
            rows.append(f'<tr data-status="{esc(st)}"><th scope="row">{what}{text}</th>'
                        f'<td data-l="Verdict">{CONDITION_WORDS.get(st, cap(st))}</td>'
                        f'<td class="num" data-l="Chance it is met">{ch}</td><td data-l="Basis">{basis}</td></tr>')
        status, word, said = verdict(m)
        out.append(f'<div class="mission" data-status="{esc(status)}"><h3>{name}</h3>'
                   f'<p class="verdict">{word}{", " + said if said else ""}</p>'
                   '<table class="tbl gates"><colgroup><col class="g1"><col class="g2"><col class="g3"><col class="g4"></colgroup>'
                   '<thead><tr><th scope="col">Condition</th><th scope="col">Verdict</th><th scope="col" class="num">Chance it is met</th>'
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


def source_row(sid: str, sources: dict, unchecked: bool = False, cite: bool = True, here: bool = False) -> str:
    """One source as a table row: name (with its citation on Method), edition, fetched, and on an entry whether it
    was checked for this asteroid."""
    s = sources.get(sid)
    if not s:
        return f'<tr id="src-{esc(sid)}"><th scope="row">{esc(sid)}</th><td colspan="3">Not in the source list</td></tr>'
    name = esc(source_name(sources, sid))
    if s.get("url"):
        name = f'<a href="{esc(s["url"])}" rel="noopener">{name}</a>'
    citation = f'<p class="gtext">{esc(plain(public_text(s.get("citation"))))}</p>' if cite else ""
    status = (f'<td data-l="This asteroid">{NOT_CHECKED if unchecked else "Checked"}</td>') if here else ""
    return (f'<tr id="src-{esc(sid)}"><th scope="row">{name}{citation}</th>'
            f'<td class="num" data-l="Edition">{date(s["edition"]) if s.get("edition") else ""}</td>'
            f'<td class="num" data-l="Fetched">{fetched(s)}</td>{status}</tr>')


def sources_table(ids: list, sources: dict, unchecked=(), entry: bool = False) -> str:
    """Every source with its citation (Method), or an entry's sources with whether each was checked for it; an
    entry carries no citations: they are on Method."""
    rows = "".join(source_row(sid, sources, sid in unchecked, cite=not entry, here=entry) for sid in ids)
    here = '<th scope="col">This asteroid</th>' if entry else ""
    return ('<table class="tbl sources"><thead><tr><th scope="col">Source</th><th scope="col" class="num">Edition</th>'
            f'<th scope="col" class="num">Fetched</th>{here}</tr></thead>'
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
    group = draws_mod.class_group(c) or ""
    if group in CLASS_WORDS:
        return CLASS_WORDS[group]
    return OTHER_CLASS_WORDS.get(str(c).strip()[:1].upper(), "Other type")


def cited(sources: dict, f: dict) -> str:
    """Whom a value is cited to in a summary: its source, or, for a published paper, the paper."""
    if f.get("source") == "curated" and f.get("ref"):
        return plain(f["ref"]).split(",")[0].strip()
    return source_name(sources, f.get("source", ""))


def _density(rec: dict, sources: dict):
    """The bulk density the mass rests on where summary.mass_basis is 'density': the push row's first used one."""
    return _first(rec["rows"].get("push", {}).get("facts", []),
                  lambda f: (f.get("label") or "").casefold() == "density" and used(f)
                  and f.get("kind", "value") == "value" and is_num(f.get("value")))


GROUP = None        # a summary item whose value is GROUP is a heading over the items after it
BEST_NEXT = "Best next observation"


def summary_items(rec: dict, sources: dict, observations: dict | None = None) -> list[tuple]:
    """[(label, value as HTML, detail as plain text, state or None)] for the entry's summary.
    An item whose value is GROUP heads the ones after it."""
    rows, summ = rec["rows"], rec.get("summary") or {}
    items = []
    gone = rec.get("gone") or {}
    if gone:                                # first, so nothing below reads as if it were still there
        items.append(("Gone", date(gone["date"]) if gone.get("date") else "Yes", gone.get("text") or "", None))
    # diameter: the value the size row rests on, its range and whose it is
    srow = rows.get("size") or {}
    sstate = srow.get("state", "unchecked")
    s = size_of(rec, sources)
    if s and sstate in ("measured", "limit") and s["state"] == sstate:
        k, unit = scale_for("size", "", "m", s["hi"] or s["mid"])
        first = _first(srow.get("facts", []), lambda f: used(f) and f.get("source") == s["source"] and _metres(f))
        who = cited(sources, first or {"source": s["source"]})
        if sstate == "measured":
            rng = f"{span(s['lo'] * k, s['hi'] * k, unit, 3)} ({ONE_SIGMA}), " if s["lo"] else ""
            items.append(("Diameter", f'{num(s["mid"] * k, 3)} {u(unit)}', rng + who, sstate))
        else:
            items.append(("Diameter", f'{BOUND_SIGN.get(s["kind"], "")}{num(s["mid"] * k, 3)} {u(unit)}', who, sstate))
    elif s and s["lo"]:
        k, unit = scale_for("size", "", "m", s["hi"])
        items.append(("Diameter", estimate_span(s["lo"] * k, s["hi"] * k) + f" {u(unit)}", ESTIMATE_RANGE, sstate))
    else:
        items.append(("Diameter", "None", "no brightness on file", None))
    # spin: the period the row rests on
    prow = rows.get("spin") or {}
    pstate = prow.get("state", "unchecked")
    f, why = shown_period(rec, sources)
    adopted = _first(prow.get("facts", []), lambda f: used(f) and _is_period(f))
    if f:
        k, unit = scale_for("spin", "", f["unit"], f["value"])
        items.append(("Spin", f'{num(f["value"] * k)} {u(unit)}', f"time for one turn, {cited(sources, f)}", pstate))
    elif pstate == "measured" and prow.get("conflicts") and adopted:
        # the period the ledger uses first, then each other period that disagrees with it ("250 h or 2.02 h")
        sec = lambda g: g["value"] * TIME_S[g["unit"]]
        said, shown = [], []
        for g in [adopted] + [g for g in prow.get("facts", []) if used(g) and _is_period(g)]:
            if all(ledger_mod.periods_differ(sec(g), x) for x in shown):
                shown.append(sec(g))
                k, unit = scale_for("spin", "", g["unit"], g["value"])
                said.append(f'{num(g["value"] * k)} {u(unit)}')
        who = f", {cited(sources, adopted)}" if len(said) == 1 else ""
        items.append(("Spin", " or ".join(said), f"time for one turn{who}; sources disagree", pstate))
    elif pstate == "measured":
        raise ValueError(f"{rec.get('designation')}: a measured spin row with no period to show ({why})")
    elif pstate == "limit":
        bound = _first(prow.get("facts", []), lambda f: f.get("kind") in ("upper", "lower") and used(f)
                       and _is_period(dict(f, kind="value")))
        shown = bound
        if shown:
            k, unit = scale_for("spin", "", shown["unit"], shown["value"])
            items.append(("Spin", f'{BOUND_SIGN.get(bound["kind"], "")}{num(shown["value"] * k)} {u(unit)}',
                          f"time for one turn, a bound; {cited(sources, shown)}", pstate))
        else:
            raise ValueError(f"{rec.get('designation')}: a spin bound with no period")
    else:
        p = (prow.get("prior") or {}).get("p_fast_2_2h", summ.get("p_fast_2_2h"))
        if is_num(p):
            items.append(("Spin", f"{esc(chance(p))} under {SPIN_SHARES[0][1]}", "time for one turn", pstate))
        else:
            items.append(("Spin", "None", "no brightness on file", None))
    # composition: the class (or reflectivity) the surface row rests on, or the shares at this brightness
    crow = rows.get("surface") or {}
    cstate = crow.get("state", "unchecked")
    pick = lambda pred: _first(crow.get("facts", []), lambda f: used(f) and pred(f))
    cls = pick(lambda f: f.get("label") == "class" and isinstance(f.get("value"), str))
    alb = pick(lambda f: _ALBEDO.search(f.get("label") or "") and is_num(f.get("value")))
    # Composition is its class. A measured reflectivity alone does not give one: it narrows the estimate, which is
    # shown as an estimate; the reflectivity itself is in the Data section.
    if cstate in ("measured", "limit") and cls:
        items.append(("Composition", esc(_class_word(cls["value"])), cited(sources, cls), cstate))
    else:
        measured_alb = cstate in ("measured", "limit")
        if measured_alb:
            cstate = "prior"
        sh = (crow.get("prior") or {}).get("shares") or summ.get("class") or {}
        if all(is_num(sh.get(c)) for c in ("S", "C", "X", "other")):
            items.append(("Composition", f"{hundredths(sh['S'])}% stony",
                          f"{hundredths(sh['X'])}% possibly metallic, {hundredths(sh['C'])}% carbon-rich, "
                          f"{hundredths(sh['other'])}% other", cstate))
        else:
            items.append(("Composition", "Not classified", "no class on file", None) if measured_alb
                         else ("Composition", "None", "no brightness on file", None))
    # mass: nobody measures it here; it follows from the diameter and a density, the asteroid's own where one is on file
    m = _q(summ.get("mass_t"))
    if m:
        rho = _density(rec, sources) if summ.get("mass_basis") == "density" else None
        if rho is not None:
            # both inputs measured: the mass is as measured as its diameter; else it is no better than the diameter
            state = "measured" if sstate == "measured" else sstate if sstate != "limit" else "prior"
            said = f"{ESTIMATE_RANGE}, from its diameter and density"
        else:
            state, said = "prior", f"{ESTIMATE_RANGE}, from its diameter and a density for its class"
        items.append(("Mass", amount(m[0], m[1], u("t")), said, state))
    # Δv
    dv, days = delta_v(rec), trip_days(rec)
    # no state mark: JPL gives every asteroid's Δv, so the mark would answer nothing
    items.append((f'<abbr title="{esc(DV_TITLE)}">Δv</abbr>', f'{dv:.3f} {u("km/s")}' if dv is not None else "None",
                  f"{count(days)} d round trip" if days is not None else "", None))
    # the verdicts, under their own heading: the verdict is the value, so no state column
    items.append(("Missions", GROUP, "", None))
    for mid, name in MISSION_LABELS.items():
        mm = (rec.get("missions") or {}).get(mid)
        if not mm:
            items.append((name, "Not assessed", "", None))
            continue
        status, word, said = verdict(mm)
        if status == "fail" and gone:
            said = "it no longer exists"
        elif status == "fail":
            fails = [condition(g.get("label")) for g in mm.get("gates", []) if g.get("status") == "fail"]
            said = "needs " + " and ".join(x[:1].lower() + x[1:] for x in fails if x)
        items.append((name, word, html.unescape(said), None))
    # the one observation that would most change the verdicts
    o = rec.get("observe")
    if o:
        what = cap(obs_name(observations, o.get("best"), surface=True) or o.get("best") or "")
        w = o.get("window") or {}
        kind, said = next_window(rec)
        if kind == "Next window":
            detail = f"no window: JPL lists {said[:1].lower() + said[1:]}"
        elif kind:
            detail = said[:1].lower() + said[1:]
        else:
            detail = "; ".join(x for x in (o.get("needs") or "", f"window {w['start']} to {w['end']}"
                                           if w.get("start") and w.get("end") else "") if x)
        items.append((BEST_NEXT, esc(what), detail, None))
    else:
        items.append((BEST_NEXT, "None", "" if gone else nothing_ranked(rec), None))
    return items


def summary_list(items: list) -> str:
    rows = []
    for name, val, detail, state in items:
        if val is GROUP:
            rows.append(f'<tr class="grp"><th colspan="4" scope="rowgroup">{name}</th></tr>')
            continue
        tag = state_tag(state, surface=True) if state else ""
        rows.append(f'<tr><th scope="row">{name}</th><td class="v">{val}</td>'
                    f'<td class="d">{nowrap_dates(detail)}</td><td class="s">{tag}</td></tr>')
    return f'<table class="sumlist"><tbody>{"".join(rows)}</tbody></table>'


# ---------------------------------------------------------------- the entry

TOC = (("data", "Data"), ("difficulty", "Difficulty"), ("value", "Metal and water"),
       ("settle", BEST_NEXT), ("missions", "Missions"), ("sources", "Sources"))


def value_title(rec: dict) -> str:
    """The price tag's heading, named for what it holds: an asteroid a sample came back from has statements on
    water alone."""
    val = rec.get("value") or {}
    ids = val.get("statement_ids") or []
    if val.get("sample") and ids and all(str(i).startswith(("water", "sample")) for i in ids):
        return "Water"
    return "Metal and water"


def entry(rec: dict, sources: dict, observations: dict | None = None, gates: dict | None = None,
          data_date: str = "") -> str:
    """<main id="entry">: the whole entry. Its <section id="summary"> is what the front page's readout lifts."""
    head, others = names(rec)
    ident = [("Number", str(rec["number"]))] if rec.get("number") else []     # the orbit row says how new it is
    if rec.get("name"):
        ident.append(("Designation", rec["designation"]))
    aka = [a for a in others if a not in (str(rec.get("number") or ""), rec["designation"])]
    if aka:
        ident.append(("Also", ", ".join(aka)))
    ident_html = "".join(f'<div><dt>{a}</dt><dd>{nowrap_dates(b)}</dd></div>' for a, b in ident)
    ident_html = f'<dl class="ident">{ident_html}</dl>' if ident_html else ""
    summary = rec.get("summary") or {}
    # a reflectivity drawn for an asteroid whose size is measured follows from that size, not from its brightness
    implied = (rec["rows"].get("size") or {}).get("state") == "measured"
    data_date = data_date or rec.get("data_date") or ""
    push, density = split_density(rec["rows"].get("push") or {"state": "unchecked"})
    rows = "".join(row(rid, push if rid == "push" else rec["rows"].get(rid) or {"state": "unchecked"}, summary, sources,
                       implied and rid == "surface", (gates or {}).get(rid, ()), data_date) for rid in ROWS)
    if density:
        rows += row("density", density, summary, sources)
    # no observation ranked: the summary's one line says why, so the section would only repeat it
    heads = tuple((a, value_title(rec) if a == "value" else b) for a, b in TOC if a != "settle" or rec.get("observe"))
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in heads)
    unchecked = {s for r in rec["rows"].values() for s in r.get("unchecked") or []} - set(rec.get("sources") or [])
    return (
        f'<main id="entry" class="page entry" data-key="{esc(rec["key"])}">'
        f'<section id="summary" aria-label="Summary">'
        f'<header class="ehead"><h1>{esc(head)}</h1>{ident_html}</header>'
        f'<details class="toc-m"><summary>On this page</summary><ul>{toc}</ul></details>'
        f'<div class="sum">{rock(rec, sources)}{summary_list(summary_items(rec, sources, observations))}</div>'
        f'</section>'
        + define(_sections(toc, heads, [body for (a, _), body in zip(TOC, (
            rows, ladder(rec.get("ladder") or []), value(rec), observe(rec, observations, sources) if rec.get("observe") else "",
            missions(rec), sources_table(used_sources(rec), sources, unchecked, entry=True))) if a != "settle" or rec.get("observe")]))
        + '</main>'
    )


def _sections(toc: str, heads, bodies) -> str:
    """The entry's record layer: a section per TOC line, with the rail beside them."""
    secs = "".join(f'<section class="sec" id="{a}"><h2>{b}</h2>{body}</section>' for (a, b), body in zip(heads, bodies))
    return f'<div class="body"><nav class="toc" aria-label="On this page"><ul>{toc}</ul></nav><div class="secs">{secs}</div></div>'


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
    return (f'<header class="site"><a class="mark" href="{rel("index.html", depth)}">{rock_mark()}{SITE}</a>'
            f'<span class="proto">prototype</span><nav aria-label="Site"><ul>{items}</ul></nav>'
            f'<p class="date">Data {date(data_date)}</p>'
            f'<details class="menu"><summary>Menu</summary><nav aria-label="Site menu"><ul>{items}</ul></nav></details>'
            '</header>\n')


def footer(depth: int, data_date: str, method: str) -> str:
    """The data date where a phone's header has no room for it. The header carries it everywhere else."""
    return f'<footer class="site-foot"><p>Data {date(data_date)}</p></footer>\n'



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


_ENDS_A_SENTENCE = re.compile(r"[.?!]['’)]?$")


def v(text: str, plain: bool = False) -> str:
    """The value itself. `plain` marks words rather than a quantity: words written as sentences are prose (the
    serif, class t), closed with a full stop; a name or a phrase stays in B612 (docs/design.md section 5)."""
    said = re.sub(r"<[^>]+>", "", str(text)).strip()
    prose = plain and (_ENDS_A_SENTENCE.search(said) or _SENTENCE_END.search(said))
    if prose and not _ENDS_A_SENTENCE.search(said):
        text = f"{text}."
    # "w": words that are not a sentence. A list that also holds prose sets them in the serif too (gen._prose_blocks).
    return f'<b class="v{" t" if prose else " w" if plain else ""}">{text}</b>'


def r(text: str) -> str:
    return f'<span class="r">{text}</span>'
