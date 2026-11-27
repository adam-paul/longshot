"""Records -> every HTML page of the site. Standard library only, no clock, no network.

    write_site(records, sources, out_dir, assets, predictions=None) -> [paths written]

records      ObjectRecord (or the same as plain dicts), one per reachable asteroid
sources      {id: Source} (or plain dicts)
assets       site-root-relative URLs: {"style", "app", "field_manifest"}, and optionally "font" (the
             B612 file; by default static/fonts/b612-regular.woff2, which this module copies there)
             and "preload", [(url, "module" | "fetch")]: files the front page will ask for, named in
             its head so they load side by side
predictions  the site's own frozen predictions, see PREDICTION_FIELDS
tables       the method files (longshot.method.Method); read from method/v0_1 when not given

The generator computes no probability. It counts, sorts and formats. The order of
list/observe.html has its home elsewhere and is taken from there (observe.ranked).
Every source is cited once, on method.html; an entry names the source beside each value.

Pages: index.html (the field, with the named asteroids and the counts for readers without
scripts), a/<key>.html, list/observe.html, record.html, method.html. The two missions are a
filter on the field and its table view, not pages.
"""
from __future__ import annotations

import dataclasses
import math
import re
import shutil
import tomllib
import types
from pathlib import Path
from urllib.parse import urlsplit

from longshot import export as export_mod
from longshot import ledger as ledger_mod
from longshot import method as method_mod
from longshot import observe as observe_mod

from longshot.types import Fact, ObjectRecord, Row

from . import templates as t

PREDICTION_FIELDS = (
    "id",           # str: stable id, printed
    "statement",    # str: the prediction as one sentence
    "p",            # float | None: the probability held, 0..1
    "frozen",       # str | None: ISO date it was frozen; None while it is a proposal
    "settles",      # str: what settles it, in a few words
    "settle_from",  # str | None: ISO date, the earliest it can be settled
    "settle_by",    # str | None: ISO date, the latest
    "key",          # str | None: object key; linked when that object has a page
    "designation",  # str | None
    "outcome",      # str | None: None while open, otherwise the outcome in words
)
# A prediction may also carry kind ("rule" | "case"), group, band, p_low and p_high (longshot/predictions.py).
# Rules of one group are then printed as one grid, a row per brightness band.

FONTS = Path(__file__).resolve().parent / "static" / "fonts"
FONT_FILES = ("b612-regular.woff2", "OFL.txt")       # the one font, and its licence beside it

_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_URL = re.compile(r"https?://\S+")

# The kinds of window that group list/observe.html, in the order observe.ranked puts them.
TIER_HEADS = {"pointable": "A telescope can point at it", "survey_only": "Only a survey could find it again",
              "none": "No window through 2045"}

NOT_CLAIMED = (
    "No single dollar value for an asteroid. A dollar figure is always a range, at dated list prices. It counts "
    "what is in the rock before any cost, with the chance of nothing first.",
    "No metal detection. These data cannot tell a metal-rich asteroid from the rest.",
    "No water detection from these data. Where no sample has come back, an entry gives the share of "
    "similar asteroids that hold water bound in minerals.",
    "No composition for a small asteroid beyond the estimate, until someone observes it.",
    "No live observing status. A window is two dates, as of the data date.",
)


def _plain(x):
    return dataclasses.asdict(x) if dataclasses.is_dataclass(x) and not isinstance(x, type) else x


def _record(d: dict) -> ObjectRecord:
    """A plain record back into an ObjectRecord, for the pipeline's own rules (export.readout)."""
    rows = {name: Row(**{**row, "facts": [Fact(**f) for f in row.get("facts", [])]}) for name, row in d["rows"].items()}
    return ObjectRecord(**{**d, "rows": rows})


def _linked(text) -> str:
    """Escape a line of provenance and make each address in it a link, shown by its host."""
    out, at = [], 0
    text = "" if text is None else str(text)
    for m in _URL.finditer(text):
        url = m.group().rstrip(".,;)")
        out.append(t.esc(text[at:m.start()]))
        out.append(f'<a href="{t.esc(url)}" rel="noopener">{t.esc(urlsplit(url).hostname or url)}</a>')
        at = m.start() + len(url)
    out.append(t.esc(text[at:]))
    return "".join(out)


# ---------------------------------------------------------------- front page

def coverage_state(r: dict, rid: str) -> str:
    """A row's column in Method's coverage table: its state, or "none" where it holds no value and nothing is
    estimated (sunlight push is never estimated; an asteroid with no brightness has no estimate)."""
    row = r["rows"].get(rid) or {}
    state = row.get("state", "unchecked")
    if state in ("measured", "limit"):
        return state
    estimate = {"size": t.size_m(r) is not None, "spin": bool(row.get("prior")),
                "surface": bool(row.get("prior")) or bool((r.get("summary") or {}).get("class"))}.get(rid, False)
    if not estimate:
        return "none"
    return "unchecked" if state == "unchecked" else "prior"


def _counts(recs: list) -> dict:
    c = {rid: {s: 0 for s in COVERAGE} for rid in COVERAGE_ROWS}
    for r in recs:
        for rid in COVERAGE_ROWS:
            c[rid][coverage_state(r, rid)] += 1
    return c


# The coverage table on Method: the rows whose state varies (Δv and the orbit are measured for every asteroid), and
# the record layer's states as columns, with not checked and nothing at all counted apart, so each line adds up.
COVERAGE_ROWS = ("size", "spin", "surface", "push")
COVERAGE = {"measured": "Measured", "limit": "Bound", "prior": "Estimated", "unchecked": "Estimated, not checked",
            "none": "None"}


def _observable(recs: list) -> list:
    """The asteroids with an observation ranked, in the method's order (observe.ranked: the one home of it)."""
    by_key = {r["key"]: r for r in recs}
    have = [types.SimpleNamespace(key=r["key"], observe=r["observe"]) for r in recs if r.get("observe")]
    return [by_key[x.key] for x in observe_mod.ranked(have)]


def plotted_measured(r: dict) -> bool:
    """Whether the front page shows this asteroid's diameter as measured: the size row is measured or a bound."""
    return (r["rows"].get("size") or {}).get("state") in ("measured", "limit")


def legend(recs: list) -> str:
    """The line above the chart: how many are shown of every reachable asteroid, then each mark's words and its
    count, then the asteroids with no brightness. Plotted diameters are the measured value or the median estimate,
    and the line says so. A bound is a measurement, and a row not checked is an estimate (docs/design.md
    section 3). As app.js draws it."""
    drawn = [r for r in recs if t.placed(r)]
    measured = sum(1 for r in drawn if plotted_measured(r))
    mark = lambda key, g, word, n: f'<li data-k="{key}">{g}{word}<span class="n">{t.count(n)}</span></li>'
    loose = len(recs) - len(drawn)
    total = (f'<li data-k="shown" class="tot"><span class="n">{t.count(len(drawn))}</span>'
             + (f' of <span class="n">{t.count(len(recs))}</span>' if loose else "") + ' reachable asteroids</li>')
    return ('<ul>' + total
            + mark("measured", t.glyph("measured"), "Measured", measured)
            + mark("estimated", t.glyph("prior"), "Estimated (median)", len(drawn) - measured)
            + (mark("loose", "", "No brightness on file", loose) if loose else "") + '</ul>')


def counts_table(recs: list) -> str:
    """Method's coverage table: for each row of an entry, how many asteroids are in each state."""
    counts = _counts(recs)
    head = "".join(f'<th class="num" scope="col">{w}</th>' for w in COVERAGE.values())
    body = "".join(
        f'<tr><th scope="row">{t.ROW_LABELS[rid]}</th>'
        + "".join(f'<td class="num" data-l="{COVERAGE[s]}">{t.count(counts[rid][s])}</td>' for s in COVERAGE)
        + "</tr>" for rid in COVERAGE_ROWS)
    return (f'<table class="tbl counts"><thead><tr><th scope="col">Row</th>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table>')


def _named_item(r: dict, words: str) -> str:
    """One row of the readout's table: {key, dv} from export.readout, linked to its entry."""
    dv = r.get("dv")
    return (f'<tr><td><a href="a/{r["key"]}.html" data-key="{r["key"]}">{t.esc(words)}</a></td>'
            f'<td class="num">{f"{dv:.3f}" if dv is not None else ""}</td></tr>')


def index_page(recs, assets, data_date, method, readout=None) -> str:
    """`readout` is export.readout's {named, ...}: the asteroids the readout lists before one is chosen.

    Every element is one of docs/design.md section 8: the header, the control strip (view, mission, Max Δv,
    Find), the line above the chart, the zoom buttons, the chart and the readout."""
    drawn = sum(1 for r in recs if t.placed(r))
    # the ceiling's slider spans the data's own delta-v, to a tenth of a km/s
    dvs = [v for v in (t.delta_v(r) for r in recs) if v is not None] or [0.0, 12.0]
    lo, hi = math.floor(min(dvs) * 10) / 10, math.ceil(max(dvs) * 10) / 10
    named = (readout or {}).get("named") or []
    seg = lambda name, items: "".join(
        f'<label><input type="radio" name="{name}" value="{v}"{" checked" if i == 0 else ""}><span>{w}</span></label>'
        for i, (v, w) in enumerate(items))
    preload = "".join(
        f'<link rel="modulepreload" href="{t.esc(url)}">\n' if kind == "module"
        else f'<link rel="preload" as="fetch" crossorigin href="{t.esc(url)}">\n'
        for url, kind in assets.get("preload", ()))
    extra = (f'<meta name="field-manifest" content="{t.esc(assets["field_manifest"])}">\n{preload}'
             '<noscript><style>#controls,.zoom,#field{display:none}</style></noscript>\n')
    dv = f'<abbr title="{t.esc(t.DV_TITLE)}">Δv</abbr>'
    body = (
        '<main class="app" id="app">\n'
        '<form class="strip" id="controls" action="index.html" method="get" onsubmit="return false">'
        '<div class="ctl view" role="radiogroup" aria-labelledby="l-view"><span class="lab" id="l-view">View</span>'
        f'<div class="seg">{seg("view", (("chart", "Chart"), ("table", "Table")))}</div></div>'
        '<div class="ctl mission" role="radiogroup" aria-labelledby="l-m"><span class="lab" id="l-m">Mission</span>'
        f'<div class="seg">{seg("m", (("", "Any"), ("surface", t.MISSION_LABELS["surface"]), ("capture", t.MISSION_LABELS["capture"])))}</div></div>'
        f'<div class="ctl dv"><label class="lab" for="dv">Max {dv} (km/s)</label><div class="dvrow">'
        f'<input id="dv" name="dv" type="range" min="{lo:g}" max="{hi:g}" step="0.1" value="{hi:g}">'
        f'<output name="dv-value" for="dv">{hi:.1f}</output></div></div>'
        '<div class="ctl find"><label class="lab" for="q">Find</label>'
        '<input id="q" name="q" type="search" placeholder="Name, number or designation" autocomplete="off"></div>'
        '</form>\n'
        '<section class="fig" aria-labelledby="fig-title"><h1 id="fig-title" class="vh">Reachable asteroids</h1>'
        f'<div class="fig-head"><div id="legend" class="legend">{legend(recs)}</div>'
        '<div class="zoom" role="group" aria-label="Zoom">'
        '<button type="button" class="btn sq" name="zoom-out" form="controls" aria-label="Zoom out">−</button>'
        '<button type="button" class="btn sq" name="zoom-in" form="controls" aria-label="Zoom in">+</button>'
        '<button type="button" class="btn" name="zoom-reset" form="controls">Reset</button></div></div>'
        '<figure id="plot" class="plot">'
        f'<canvas id="field" tabindex="0" aria-label="Chart of {t.count(drawn)} asteroids: delta-v (Δv) of the cheapest '
        'round trip in km/s across, diameter in m up, on a log scale"></canvas>'
        '<div id="axes" aria-hidden="true"></div><div id="tip" hidden></div>'
        '<noscript><p class="noscript-fig">The chart and the table need JavaScript.</p></noscript></figure>'
        '<section id="table" class="tview" hidden aria-label="Reachable asteroids, as a table">'
        '<div class="tscroll"><table class="ftbl"><thead></thead><tbody></tbody></table></div>'
        '<div class="pager"><output name="rows" form="controls"></output>'
        '<button type="button" class="btn" name="page-prev" form="controls">Previous</button>'
        '<button type="button" class="btn" name="page-next" form="controls">Next</button></div></section>'
        '</section>\n'
        '<aside id="readout" class="readout" aria-label="Readout"><div class="overview">'
        '<table class="named"><thead><tr><th scope="col">Named asteroid</th>'
        f'<th scope="col" class="num">{dv} (km/s)</th></tr></thead>'
        f'<tbody>{"".join(_named_item(r, r["name"]) for r in named)}</tbody></table>'
        '</div></aside>\n'
        '</main>'
    )
    return (
        t.head(t.SITE, assets, 0, extra)
        + '<body data-page="field">\n'
        + t.header(0, data_date, "index.html")
        + body + "\n"
        + t.footer(0, data_date, method)        # on a phone the header has no room for the date
        + f'<script type="module" src="{t.esc(assets["app"])}"></script>\n'
        + '</body>\n</html>\n'
    )


# ---------------------------------------------------------------- entries

def _observations(tables) -> dict:
    """{observation id: {label, plain}} from observe.toml: its technical name and its plain one."""
    return {o["id"]: {"label": o["label"], "plain": o.get("plain") or o["label"]} for o in tables.observe.get("observations", [])}


def entry_page(rec, sources, assets, data_date, method, observations=None, gates=None) -> str:
    head, _ = t.names(rec)
    title = head if head == rec["designation"] else f'{head}, {rec["designation"]}'
    return t.page(
        title=f'{title} | {t.SITE}', body=t.entry(rec, sources, observations, gates, data_date),
        kind="entry", depth=1, assets=assets, data_date=data_date, method=method)


# ---------------------------------------------------------------- what to observe next

def size_cell(rec, sources) -> str:
    """The diameter the entry shows. The row's state leads, as its mark, so an estimate never reads as a
    measurement, and a measured mark never stands beside an estimate's range."""
    s = t.size_of(rec, sources)
    state = (rec["rows"].get("size") or {}).get("state", "unchecked")
    mark = t.glyph(state, t.SURFACE_WORDS.get(state, state))
    if not s:
        return '<td class="num sz"><span>none: no brightness on file</span></td>'
    if s["state"] in ("measured", "limit"):
        text = t.BOUND_SIGN.get(s["kind"], "") + t.num(s["mid"], 3)
    else:
        text = t.estimate_span(s["lo"], s["hi"]) if s["lo"] else t.sig2(s["mid"])
    return f'<td class="num sz"><span>{mark}{t.esc(text)}</span></td>'


OBSERVE_COLS = ("Rank", "Asteroid", "Δv (km/s)", "Diameter (m)", "Measure", "Mission", "Condition", "Telescope",
                "Window opens", "Window closes", "Peak brightness (mag)", "Not checked")
MAG = '<abbr title="magnitude in visible light, as JPL predicts it: a lower number is brighter">mag</abbr>'


def observe_page(recs, sources, assets, data_date, method, observations=None, tables=None) -> str:
    ranked = _observable(recs)
    tiers = {}
    for r in ranked:
        tiers[r["observe"].get("tier")] = tiers.get(r["observe"].get("tier"), 0) + 1
    rows, tier = [], object()
    for i, r in enumerate(ranked, 1):
        o = r["observe"]
        if o.get("tier") != tier:
            tier = o.get("tier")
            if tier in TIER_HEADS:
                rows.append(f'<tr class="tier"><th colspan="{len(OBSERVE_COLS)}" scope="rowgroup">{TIER_HEADS[tier]}'
                            f'<span>{t.count(tiers[tier])} asteroids</span></th></tr>')
        measure, mission, cond = t.measure_and_condition(r)
        if not measure:         # no condition named: the observation's own name, and its text as the condition
            measure = t.obs_name(observations, o.get("best")) or o.get("label") or "none named"
            cond = o.get("text") or "none named"
            mission = t.MISSION_LABELS.get(o.get("mission"), "") or "none named"
        w = o.get("window") or {}
        start, end = (t.date(w["start"]), t.date(w["end"])) if w.get("start") and w.get("end") else ("", "")
        peak = f'{w["peak_mag"]:.1f}' if t.is_num(w.get("peak_mag")) else ""
        dv = t.delta_v(r)
        name = f' <span class="nm">{t.esc(r["name"])}</span>' if r.get("name") else ""
        check = ", ".join(t.esc(t.source_name(sources, s)) for s in o.get("unchecked") or [])
        scope = t.esc(t.cap(o.get("needs") or ""))      # for a window no telescope can use, what it needs first
        if not start:                                   # no window: the state, not an empty cell
            start = end = "none listed"
            peak = peak or "none listed"
        # no per-cell labels: style.css names each column on a phone (.ltbl.obs td:nth-child)
        rows.append(
            f'<tr><td class="num rank">{i}</td><td class="ast"><a href="../a/{r["key"]}.html">{t.esc(r["designation"])}</a>{name}</td>'
            f'<td class="num">{f"{dv:.3f}" if dv is not None else ""}</td>{size_cell(r, sources)}'
            f'<td>{t.esc(measure)}</td><td>{t.esc(mission)}</td><td>{t.esc(cond)}</td>'
            f'<td class="tel">{scope}</td><td class="num">{start}</td><td class="num">{end}</td>'
            f'<td class="num">{peak}</td><td class="chk">{f"<span>{check}</span>" if check else ""}</td></tr>')
    head = "<tr>" + "".join(f'<th scope="col"{NUM if c in NUM_COLS else ""}>{c.replace("(mag)", f"({MAG})")}</th>' for c in OBSERVE_COLS) + "</tr>"
    table = (f'<table class="ltbl obs"><caption class="vh">Asteroids with an unclear verdict, ranked by how much one '
             f'observation would change it</caption><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'
             if rows else '<p class="none">No asteroid with an unclear verdict has an observation ranked</p>')
    order = ((tables or method_mod.load()).observe.get("rank") or {}).get("said")
    body = (
        '<main class="page wide"><div class="lhead"><h1>Observe next</h1><dl class="lmeta">'
        f'<div><dt>Ranked</dt><dd>{t.count(len(ranked))} asteroids with an unclear verdict</dd></div>'
        + (f'<div><dt>Order</dt><dd>{t.esc(t.cap(order))}</dd></div>' if order else "")
        + '</dl></div>'
        f'<p class="cap">For each asteroid: what to measure, and the mission condition the result would settle. {t.esc(OBSERVE_DV)} '
        'Diameter: the measured value, or the 90% range of the estimate; "on entry" where the source allows its value '
        'only on the asteroid\'s own page.</p>'
        f'{t.define(table)}</main>')
    return t.page(title=f"Observe next | {t.SITE}", body=body, kind="list", depth=1,
                  assets=assets, data_date=data_date, method=method, current="list/observe.html")


NUM = ' class="num"'
NUM_COLS = {"Rank", "Δv (km/s)", "Diameter (m)", "Window opens", "Window closes", "Peak brightness (mag)"}
OBSERVE_DV = "Delta-v (Δv): the total change of speed for the cheapest round trip."


# ---------------------------------------------------------------- the record

def _chance_cell(p: dict) -> str:
    """The chance held, with the spread between surveys in brackets where the prediction carries one."""
    text = t.pct(p.get("p"))
    lo, hi = p.get("p_low"), p.get("p_high")
    if t.is_num(lo) and t.is_num(hi) and lo < hi:
        text += f" ({t.pct(lo).rstrip('%')}–{t.pct(hi)})"
    return t.esc(text)


def _when(p: dict) -> str:
    """When a prediction can be settled; with no date, the pipeline's few words on why there is none."""
    first, last = p.get("settle_from"), p.get("settle_by")
    if first and last:
        return f"{t.date(first)} to {t.date(last)}"
    if first or last:
        return ("from " if first else "by ") + t.date(first or last)
    return t.esc(p.get("settle_note") or "")


def _shared(lists, from_end=False) -> int:
    """How many leading (or trailing) items every list has in common."""
    n = 0
    for items in zip(*(reversed(x) if from_end else x for x in lists)):
        if len(set(items)) != 1:
            break
        n += 1
    return n


# A family of rules, as its grid is headed: (heading, what each cell is the chance of, the columns' shared words).
GRID_WORDS = {
    "class": ("Class, by brightness", "The chance of each class, for a reachable asteroid that gets a class. "
                                      "In brackets, the range across surveys.", ""),
    "spin": ("Spin, by brightness", "The chance that a reachable asteroid's first reliable spin period is shorter than "
                                    "each time. In brackets, the range across surveys.", "Spin period under"),
    "size": ("Diameter, by brightness", "The diameter a reachable asteroid of each brightness will have when it is "
                                        "measured. Each range has a 90% chance of holding it.", "Diameter, 90% range (m)"),
}
_UNIT_WORDS = ((re.compile(r"\b(\d+(?:\.\d+)?) hours?\b"), r"\1 h"), (re.compile(r"\b(\d+(?:\.\d+)?) minutes?\b"), r"\1 min"))


def _units_short(text: str) -> str:
    """'2.2 hours' -> '2.2 h': a column head carries the symbol, as the entries do."""
    for pattern, short in _UNIT_WORDS:
        text = pattern.sub(short, text)
    return text


def _range_grid(preds: list) -> str | None:
    """A family with one rule a band that differs only in the band and a stated range, all at one chance
    (diameter by band: "... of H 19 is 250–910 m in diameter."): a row per band, the range in one column
    headed with its unit, the chance said once. None when the family does not have that shape."""
    words = [str(p.get("statement") or "").rstrip(".").split() for p in preds]
    a, z = _shared(words), _shared(words, from_end=True)
    middles = [w[a:len(w) - z] for w in words]
    if (len(preds) < 2 or len({p.get("p") for p in preds}) != 1 or len({p.get("band") for p in preds}) != len(preds)
            or any(len(m) != 3 or m[1] != "is" for m in middles) or not " ".join(words[0][:a]).endswith(" H")
            or any(p.get("frozen") or p.get("outcome") or p.get("key") for p in preds)
            or len({(p.get("settles"), _when(p)) for p in preds}) != 1 or preds[0].get("group") not in GRID_WORDS):
        return None
    title, said, over = GRID_WORDS[preds[0]["group"]]
    body = "".join(f'<tr id="{t.esc(p.get("id"))}"><th scope="row">{t.esc(m[0])}</th>'
                   f'<td class="num" data-l="{t.esc(over)}">{t.esc(m[2])}</td></tr>' for p, m in zip(preds, middles))
    p, when = preds[0], _when(preds[0])
    return (
        f'<section class="rgroup"><h2>{t.esc(title)}</h2><p class="stmt">{t.esc(said)}</p>'
        f'<dl class="lmeta"><div><dt>Settled by</dt>{_settled_by(p)}</div>'
        + (f'<div><dt>When</dt><dd>{when}</dd></div>' if when else "") + '</dl>'
        f'<table class="tbl grid narrow"><thead><tr><th scope="col">{H_HEAD}</th><th class="num" scope="col">{t.esc(over)}</th></tr></thead>'
        f'<tbody>{body}</tbody></table></section>')


def _grid(preds: list) -> str | None:
    """One family of rules (class by band, spin by band) as one table: the statement once, with its two
    blanks; a row per band, a column per answer; what settles it once. None when the family does not
    have that shape, or a member is frozen or settled and so needs its own line."""
    bands = list(dict.fromkeys(p.get("band") for p in preds))
    by_band = {b: [p for p in preds if p.get("band") == b] for b in bands}
    width = len(by_band[bands[0]])
    if width == 1 and len(bands) == len(preds):
        return _range_grid(preds)
    if (len(bands) < 2 or width < 2 or None in bands or any(len(x) != width for x in by_band.values())
            or any(p.get("frozen") or p.get("outcome") or p.get("key") for p in preds)
            or len({(p.get("settles"), _when(p)) for p in preds}) != 1):
        return None
    heads, columns = [], None
    for b in bands:
        words = [str(p.get("statement") or "").rstrip(".").split() for p in by_band[b]]
        n = _shared(words)
        cols = [" ".join(w[n:]) for w in words]
        if not all(cols) or (columns is not None and cols != columns):
            return None
        columns = cols
        heads.append(words[0][:n])
    a, z = _shared(heads), _shared(heads, from_end=True)
    labels = [" ".join(h[a:len(h) - z]) for h in heads]
    if not all(labels) or a + z >= min(len(h) for h in heads):
        return None
    first, last = " ".join(heads[0][:a]), " ".join(heads[0][len(heads[0]) - z:])
    group = preds[0].get("group")
    title, said, over = GRID_WORDS.get(group) or (t.cap(group or "Rule"), f"{first} … {last} …", "")
    # the rows' shared words ("H") head the first column, with the unit they are in
    rows_head = H_HEAD if first.endswith(" H") else ""
    cols = [_units_short(t.cap(c)) for c in columns]
    named = {c: CLASS_COLUMNS[c] for c in cols if c in CLASS_COLUMNS}
    head = "".join(f'<th class="num" scope="col"><abbr title="{t.esc(named[c][1])}">{t.esc(named[c][0])}</abbr></th>'
                   if c in named else f'<th class="num" scope="col">{t.esc(c)}</th>' for c in cols)
    cols = [named[c][0] if c in named else c for c in cols]
    top = (f'<tr><td></td><th class="num over" scope="colgroup" colspan="{len(cols)}">{t.esc(over)}</th></tr>' if over else "")
    body = "".join(
        f'<tr><th scope="row">{t.esc(label)}</th>'
        + "".join(f'<td class="num" id="{t.esc(p.get("id"))}" data-l="{t.esc((over + " " + c).strip())}">{_chance_cell(p)}</td>'
                  for p, c in zip(by_band[b], cols)) + "</tr>"
        for b, label in zip(bands, labels))
    p = preds[0]
    when = _when(p)
    return (
        f'<section class="rgroup"><h2>{t.esc(title)}</h2><p class="stmt">{t.esc(said)}</p>'
        f'<dl class="lmeta"><div><dt>Settled by</dt>{_settled_by(p)}</div>'
        + (f'<div><dt>When</dt><dd>{when}</dd></div>' if when else "") + '</dl>'
        f'<table class="tbl grid"><thead>{top}<tr><th scope="col">{rows_head}</th>{head}</tr></thead>'
        f'<tbody>{body}</tbody></table></section>')


def _flat(preds: list, keys: set) -> str:
    """Predictions one to a line. The frozen and outcome columns appear once a prediction has either."""
    frozen = any(p.get("frozen") for p in preds)
    outcome = any(p.get("outcome") for p in preds)
    rows = []
    for p in preds:
        who = ""
        if p.get("designation"):
            who = t.esc(p["designation"])
            if p.get("key") in keys:
                who = f'<a href="a/{p["key"]}.html">{who}</a>'
            who += " "
        rows.append(
            f'<tr id="{t.esc(p.get("id"))}"><th scope="row" class="w">{who}{t.esc(p.get("statement"))}</th>'
            f'<td class="num" data-l="Chance">{_chance_cell(p)}</td>'
            + (f'<td data-l="Frozen">{t.date(p["frozen"]) if p.get("frozen") else "not yet"}</td>' if frozen else "")
            + f'<td data-l="Settled by">{t.esc(t.cap(p.get("settles")))}</td><td data-l="When">{_when(p)}</td>'
            + (f'<td data-l="Outcome">{t.esc(p.get("outcome")) if p.get("outcome") else "open"}</td>' if outcome else "")
            + "</tr>")
    return (
        '<section class="rgroup"><table class="tbl flat"><thead><tr><th scope="col">Prediction</th>'
        '<th scope="col" class="num">Chance</th>'
        + ('<th scope="col">Frozen</th>' if frozen else "") + '<th scope="col">Settled by</th><th scope="col">When</th>'
        + ('<th scope="col">Outcome</th>' if outcome else "") + f'</tr></thead><tbody>{"".join(rows)}</tbody></table></section>')


RECORD_INTRO = ("The site's own predictions. The site will freeze each one, with a date, before the observation "
                "that settles it. It will list a miss the same way as a hit.")
# The class grid's columns, from the statements' class letters, in the site's words; the letters are the hover note.
CLASS_COLUMNS = {"S or Q": ("Stony", "classes S and Q"), "C, B, F or G": ("Carbon-rich", "classes C, B, F and G"),
                 "X, E, M or P": ("Possibly metallic", "classes X, E, M and P"),
                 "None of S, C or X": ("Other", "every other class")}


def _settled_by(p: dict) -> str:
    """What settles a prediction, as a value: prose (the serif) when it is written in sentences."""
    said = t.cap(p.get("settles"))
    prose = bool(t._ENDS_A_SENTENCE.search(said) or t._SENTENCE_END.search(said))
    if prose and not t._ENDS_A_SENTENCE.search(said):
        said += "."
    return f'<dd{" class=\"t\"" if prose else ""}>{t.esc(said)}</dd>'
H_HEAD = f'<abbr title="{t.esc("absolute magnitude: " + dict(t.TERMS)["absolute magnitude"])}">H</abbr> (mag)'


def record_page(predictions, keys, assets, data_date, method) -> str:
    groups: dict = {}
    for p in predictions:
        groups.setdefault((p.get("kind") == "rule" and p.get("group")) or None, []).append(p)
    parts, loose = [], list(groups.pop(None, []))
    for group, preds in groups.items():
        grid = _grid(preds)
        if grid:
            parts.append(grid)
        else:
            loose = preds + loose          # rules before single asteroids, as the pipeline lists them
    if loose:
        parts.append(_flat(loose, keys))
    if not predictions:
        parts.append('<p class="none">No prediction listed yet</p>')
    frozen = sum(1 for p in predictions if p.get("frozen"))
    settled = sum(1 for p in predictions if p.get("outcome"))
    body = (
        '<main class="page wide"><div class="lhead"><h1>Record</h1><dl class="lmeta">'
        f'<div><dt>Predictions</dt><dd>{t.count(len(predictions))}</dd></div>'
        f'<div><dt>Frozen</dt><dd>{t.count(frozen)}</dd></div>'
        f'<div><dt>Settled</dt><dd>{t.count(settled)}</dd></div>'
        f'</dl></div><p class="intro">{t.esc(RECORD_INTRO)}</p>{t.define("".join(parts))}</main>')
    return t.page(title=f"Record | {t.SITE}", body=body, kind="record", depth=0, assets=assets,
                  data_date=data_date, method=method, current="record.html")


# ---------------------------------------------------------------- the method page

_public = t.public_text      # a line from a method file as a visitor reads it (templates.public_text)


def _pub(text) -> str:
    return t.esc(_public(text))


def _src(tbl: dict) -> str:
    """Where a constant comes from, for a visitor: the method file's public citation (`cite`), if it has one.
    Its `source` is provenance for whoever maintains the method (paths into the research) and is not printed."""
    cite = _public(tbl.get("cite")) if tbl.get("cite") else ""
    return f'<p class="src">{_linked(cite)}</p>' if cite else ""


def _note(text) -> str:
    """A note in sentences, closed with a full stop (docs/design.md section 7)."""
    said = _public(text) if text else ""
    if said and said[-1] not in ".?!'’)":
        said += "."
    return f'<p class="note">{t.esc(said)}</p>' if said else ""


def _quantity(value, unit: str = "") -> str:
    """A constant with its unit; a unit the page has no short form for is spelt out after it."""
    short = t.UNITS.get(unit or "")
    shown = t.count(value) if isinstance(value, int) else t.num(value) if t.is_num(value) else _pub(value)
    return t.v(t.with_unit(shown, short) if short else f'<span class="c">{shown}</span>') + (
        f' <span class="gr">{_pub(unit)}</span>' if unit and not short else "")


# A figure's kind, as Method tags it: how the method set it. "measured" is the state word for an asteroid's value, so a
# constant set from the data is tagged "from the data".
KIND_WORDS = {"measured": "from the data", "quoted": "quoted", "judgement": "judgement"}


def _kind(kind) -> str:
    return f'<span class="gr">{t.esc(KIND_WORDS.get(kind, _public(kind)))}</span>' if kind else ""


def _gate(mid: str, g: dict) -> str:
    short = t.UNITS.get(g.get("unit") or "") or ""
    chosen = ""
    if isinstance(g.get("range"), list) and len(g["range"]) == 2:
        lo, hi = g["range"]
        chosen = t.r("chosen from " + (t.span(lo, hi, short) if short else f'<span class="c">{t.num(lo)}–{t.num(hi)}</span>'))
    kind = _kind(g.get("kind"))
    alts = "".join(
        f'<li><b>{t.with_unit(t.num(a["value"]), short) if short else t.num(a["value"])}</b> {_pub(a.get("what"))}</li>'
        for a in g.get("alternatives", []) if t.is_num(a.get("value")) and _public(a.get("what")))
    return (
        f'<div class="th" id="g-{mid}-{t.esc(g["id"])}"><dl class="facts">'
        + t.line(t.esc(t.condition(_public(g["label"]))), _quantity(g["preset"], g.get("unit")), chosen, kind) + "</dl>"
        + (f'<ul class="alt">{alts}</ul>' if alts else "")
        + _src(g) + _note(g.get("caveat")) + _note(g.get("not_used")) + "</div>")


NOT_GATED_WORDS = {"delta_v": "Δv"}


def _rules(mis: dict, n_draws: int) -> str:
    """How conditions become a verdict, in the site's words, with the method file's own figures."""
    rules = mis.get("rules") or {}
    decide = rules.get("decide") or {}
    sigma, factor = decide.get("sigma"), decide.get("no_range_factor")
    lines = []
    if t.is_num(sigma) and t.is_num(factor):
        lines.append(t.line("Met or failed", t.v(
            f"A measurement decides the condition. The measured value must clear the threshold by {t.num(sigma)} "
            f"times its stated 1σ error. With no stated error, it must clear it by a factor of {t.num(factor)}.", True)))
    lines.append(t.line("Unclear", t.v(
        f"No measurement decides it. Its chance is the share of {t.count(n_draws)} random draws that meet it. Each "
        "draw is one possible asteroid: a diameter, class, reflectivity, density and spin that fit what is on file. "
        "A share of none prints as &lt;1%, and a share of all as &gt;99%.", True)))
    lines.append(t.line("A mission", t.v(
        "It fits if every condition is met. It is ruled out if any condition fails. Otherwise it is unclear, and "
        "its chance is the share of draws that meet every condition.", True)))
    for name, word in (("period", "A spin period decides"), ("mass", "A mass decides"), ("size", "A diameter is set aside")):
        rule = rules.get(name) or {}
        text = rule.get("decides") or rule.get("implied")
        if name == "size" and t.is_num(rule.get("min_implied_reflectivity")):
            text = f"when it implies a reflectivity under {t.pct(rule['min_implied_reflectivity'])}"
        if text:
            text = t.cap(text)
        if text:
            lines.append(t.line(word, t.v(_pub(text), True), f'<span class="src">{_linked(_public(rule.get("cite")))}</span>' if rule.get("cite") else ""))
    return f'<h3 id="m-rules">Fits, ruled out and unclear</h3><dl class="facts">{"".join(lines)}</dl>'


def _missions(m) -> str:
    mis, out = m.missions, []
    for mid in mis["order"]:
        spec = mis[mid]
        out.append(f'<h3 id="m-{mid}">{t.MISSION_LABELS.get(mid, _pub(mid))}</h3>'
                   f'<p class="note">{_pub(spec.get("summary"))}</p>' + "".join(_gate(mid, g) for g in spec["gates"]))
        skipped = [(k, v) for k, v in (spec.get("not_gated") or {}).items() if k not in ("kind", "source")]
        if skipped:
            out.append('<dl class="facts">' + "".join(
                t.line(f'Not a condition: {NOT_GATED_WORDS.get(k) or _pub(k.replace("_", "-"))}', t.v(_pub(v), True))
                for k, v in skipped) + "</dl>")
    return "".join(out) + _rules(mis, m.n_draws)


_NOT_VALUES = ("_kind", "_source", "_why", "_rule", "_basis", "_cite")
# ledger.toml's tables and keys, as the page names them.
LEDGER_WORDS = {
    ("period", "min_grade"): "Lowest grade counted",
    ("period", "tolerance"): "Periods agree within, as a share",
    ("period", "ungraded"): "A period with no grade",
    ("period", "copy_of_a_limit"): "A copy of a limit",
    ("period", "superseded"): "A newer period",
    ("push", "detection_sigma"): "Push detected at, in σ",
    ("push", "counts"): "Push terms counted",
    ("push", "listed_only"): "Push terms listed only",
    ("spitzer", "min_snr"): "Spitzer fit, lowest signal-to-noise",
    ("reflectivity", "max"): "Reflectivity, highest kept",
    ("fixed_tables", "rule"): "A fixed table",
    ("fixed_tables", "reason"): "Shown as",
    ("fixed_tables", "sources"): "Fixed tables",
    ("closed_tables", "rule"): "A closed table",
    ("closed_tables", "reason"): "Shown as",
    ("closed_tables", "sources"): "Closed tables",
    "known_bad": "Set aside", "gone": "Gone",
}


def _named(x, sources: dict) -> str:
    """A property id or a source id from a method file, as the pages name it."""
    if x in ledger_mod.LABEL:
        return t.label("", ledger_mod.LABEL[x])
    return t.source_name(sources, x) if x in sources else str(x)


def _ledger(m, sources: dict | None = None) -> str:
    """Which values on file count towards a row's state: method/v0_1/ledger.toml, read as it is written.

    A table holds values; `<name>_kind` and `<name>_source`, or the table's own kind and source, say how
    each was set; `<name>_rule` or `<name>_why` says what it means. A source the whole table shares is
    printed once, under its last line. A list of tables (the values found to be wrong, the bodies that are
    gone) is one line an entry.
    """
    tables = getattr(m, "ledger", None)
    path = Path(m.path) / "ledger.toml"
    if tables is None and path.is_file():
        tables = tomllib.loads(path.read_text(encoding="utf-8"))
    out = []
    for key, tbl in (tables or {}).items():
        if isinstance(tbl, list):
            for item in tbl:
                if isinstance(item, dict) and (item.get("why") or item.get("text")):
                    out.append('<div class="th"><dl class="facts">'
                               + t.line(f'{LEDGER_WORDS.get(key, t.cap(key.replace("_", " ")))}: {t.esc(item.get("designation"))}',
                                        t.v(_pub(item.get("why") or item.get("text")), True))
                               + "</dl>" + _src(item) + "</div>")
            continue
        if not isinstance(tbl, dict):
            continue
        lines = []
        for name, value in tbl.items():
            if name in ("kind", "source", "cite") or name.endswith(_NOT_VALUES) or isinstance(value, dict):
                continue
            if isinstance(value, list):         # names, not prose: printed as they are
                shown = t.v(t.esc(t.cap("; ".join(_named(x, sources or {}) for x in value))), True)
            else:
                shown = t.v(t.num(value)) if t.is_num(value) else t.v(_pub(t.cap(value)), True)
            kind = tbl.get(f"{name}_kind") or tbl.get("kind")
            more = tbl.get(f"{name}_rule") or tbl.get(f"{name}_why")
            own = {"cite": tbl.get(f"{name}_cite")}
            said = LEDGER_WORDS.get((key, name)) or t.cap(f'{key.replace("_", " ")}, {name.replace("_", " ")}')
            lines.append(f'<div class="th" id="l-{t.esc(key)}-{t.esc(name)}"><dl class="facts">'
                         + t.line(t.esc(said), shown, _kind(kind))
                         + "</dl>" + _note(more) + _src(own) + "</div>")
        if lines:
            out += lines
            out.append(_src(tbl))
    return "".join(out)


_LADDER_UNITS = (("_min", "min"), ("_h", "h"), ("_m", "m"))
# The facts of ladder.toml that name no mission, by their public names.
FLOWN_NAMES = {"companies": "Asteroid-mining companies", "sonter_1998": "Sonter 1998", "keck_2012": "Keck study, 2012",
               "arm": "Asteroid Redirect Mission"}
# A source's publisher, by the host of its address: a link is cited by its public name, never by a bare host.
PUBLISHERS = {
    "science.nasa.gov": "NASA", "nasa.gov": "NASA", "jpl.nasa.gov": "NASA JPL", "ntrs.nasa.gov": "NASA Technical Reports",
    "ssd-api.jpl.nasa.gov": "JPL Small-Body Database", "planetary.org": "The Planetary Society", "phys.org": "Phys.org",
    "curation.isas.jaxa.jp": "JAXA sample curation", "global.jaxa.jp": "JAXA", "www8.cao.go.jp": "Cabinet Office of Japan",
    "cao.go.jp": "Cabinet Office of Japan", "cnsa.gov.cn": "China National Space Administration", "arxiv.org": "arXiv",
    "en.wikipedia.org": "Wikipedia", "astroforge.com": "AstroForge", "karmanplus.com": "Karman+",
    "nss.org": "National Space Society", "kiss.caltech.edu": "Keck Institute for Space Studies",
    "pubs.usgs.gov": "USGS Mineral Commodity Summaries",
}


def _publisher(url: str) -> str:
    host = (urlsplit(url).hostname or url).removeprefix("www.")
    return PUBLISHERS.get(host) or PUBLISHERS.get(".".join(host.split(".")[-2:])) or host


def _cited_links(text) -> list[str]:
    """Each address in a line of provenance as a link named by its publisher; a second page of one publisher is
    'NASA, page 2'."""
    out, seen, count = [], set(), {}
    for m in _URL.finditer("" if text is None else str(text)):
        url = m.group().rstrip(".,;)")
        if url in seen:
            continue
        seen.add(url)
        who = _publisher(url)
        count[who] = count.get(who, 0) + 1
        said = who if count[who] == 1 else f"{who}, page {count[who]}"
        out.append(f'<a href="{t.esc(url)}" rel="noopener">{t.esc(said)}</a>')
    return out


def _difficulty(m) -> str:
    """Method's Difficulty section: the five steps' questions, then each line a step is judged by, with where it
    comes from."""
    lad = m.ladder
    rungs = "".join(
        f'<div id="rung-{t.esc(rung)}"><dt>{_pub(t.RUNG_LABELS.get(rung, rung))}</dt>'
        f'<dd>{t.v(_pub(lad["rung"][rung].get("question")), True)}</dd></div>'
        for rung in lad["meta"]["order"])
    th, lines = lad["thresholds"], []
    for key, value in th.items():
        if not t.is_num(value):
            continue
        unit = next((u for end, u in _LADDER_UNITS if key.endswith(end)), "")
        stems = [key] + [key.rsplit("_", n)[0] for n in (1, 2)]
        basis = next((th[s + "_basis"] for s in stems if s + "_basis" in th), "")
        lines.append((t.with_unit(t.num(value), unit), _public(basis)))
    spin = lad["spin_limit"]
    for name, rho in (("light_rock", spin.get("light_rock_kg_m3")), ("dense_rock", spin.get("dense_rock_kg_m3"))):
        lines.append((t.with_unit(t.num(spin[f"{name}_limit_h"]), "h"),
                      f"a sphere of {t.num(rho)} kg/m³ with no cohesion sheds loose material from its equator when it "
                      "turns faster" if t.is_num(rho) else "the spin at which loose material leaves the equator"))
    for value, source in ((spin.get("screening_line_h"), spin.get("screening_line_note")),
                          (spin.get("published_bar_h"), spin.get("published_bar_note"))):
        if t.is_num(value):
            lines.append((t.with_unit(t.num(value), "h"), _public(source)))
    full = lambda x: x if re.search(r"[.?!)]$", x) else x + "."
    rows = "".join(f'<tr><th scope="row" class="num">{t.esc(a)}</th><td>{t.esc(full(t.cap(b)))}</td></tr>' for a, b in lines)
    return (f'<dl class="facts">{rungs}</dl>'
            '<h3 id="ladder-lines">The lines the steps use</h3>'
            '<table class="tbl lines"><thead><tr><th scope="col" class="num">Line</th><th scope="col">Where it comes from</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>' + _note(th.get("judgement")))


def _flown(m) -> str:
    """Method's What has flown section: the site-wide facts, then their sources by publisher."""
    lad = m.ladder
    flown = "".join(f"<li>{_pub(s['text'])}</li>" for s in lad.get("sitewide", []) if s.get("text"))
    facts = "".join(
        f'<li id="f-{t.esc(f["id"])}">{t.esc(f.get("mission") or FLOWN_NAMES.get(f["id"]) or t.cap(f["id"].replace("_", " ")))}, '
        f'as of {t.date(f.get("as_of"))}: {", ".join(_cited_links(f.get("source")))}</li>'
        for f in lad.get("fact", []) if f.get("id") and f.get("source") and _URL.search(str(f["source"])))
    return ((f'<ul class="stm">{flown}</ul>' if flown else "")
            + (f'<h3 id="flown-sources">Sources</h3><ul class="srcs">{facts}</ul>' if facts else ""))


def _lo_hi(tbl, unit: str, k: float = 1.0) -> str:
    return t.v(t.span(tbl["lo"] * k, tbl["hi"] * k, unit)) if isinstance(tbl, dict) and t.is_num(tbl.get("lo")) and t.is_num(tbl.get("hi")) else ""


def _value(m) -> str:
    """Method's Metal and water section. A material's line gives its range and what it is a range of; the analyses
    behind it are in the papers its source list cites."""
    val, lines = m.value, []
    counted = val.get("counted") or {}
    for name, key in (("Metal counted", "metal"), ("Metal not counted", "metal_not_counted"),
                      ("Water counted", "water"), ("Left out", "left_out")):
        if counted.get(key):
            lines.append(t.line(name, t.v(_pub(t.cap(counted[key])), True)))
    stuff = []
    for mat in (val.get("material") or {}).values():
        if not isinstance(mat, dict) or not mat.get("label"):
            continue
        if _lo_hi(mat.get("grade_ppm"), "g/t"):
            stuff.append(t.line(_pub(t.cap(mat["label"])), _lo_hi(mat["grade_ppm"], "g/t"), t.r("platinum-group metal")))
        elif mat.get("grade_table") in (val.get("grade_table") or {}):
            pts = val["grade_table"][mat["grade_table"]]
            stuff.append(t.line(_pub(t.cap(mat["label"])), t.v(t.span(pts[0][1], pts[-1][1], "g/t")),
                                t.r("platinum-group metal in the metal")))
            if mat.get("caution"):
                stuff.append(t.line("", t.v(_pub(mat["caution"]), True)))
        if _lo_hi(mat.get("water_fraction"), "%", 100.0):
            stuff.append(t.line(_pub(t.cap(mat["label"])), _lo_hi(mat["water_fraction"], "%", 100.0), t.r("water by weight")))
            if mat.get("basis"):
                stuff.append(t.line("", t.v(_pub(mat["basis"]), True)))
    shares = []
    for cls, kinds in (val.get("kinds") or {}).items():
        if not isinstance(kinds, dict):
            continue
        for key, word in (("basis", ""), ("iron_rich_basis", ", iron-rich share"), ("hydrated_basis", ", share holding water"),
                          ("grains_basis", ", share with metal grains")):
            if kinds.get(key):
                shares.append(t.line(f"Class {_pub(cls)}{word}", t.v(_pub(kinds[key]), True)))
    prices = val.get("prices") or {}
    per_kg = "".join(
        f'<tr><th scope="row">{_pub(el)}</th><td class="num">{t.esc(t.usd_range(row[0], row[-1]).replace("$", ""))}</td></tr>'
        for el, row in (prices.get("usd_per_kg") or {}).items() if isinstance(row, list) and row)
    market = val.get("market") or {}
    caps = "".join(f'<tr><th scope="row">{_pub(el)}</th><td class="num">{t.count(kg)}</td></tr>'
                   for el, kg in (market.get("cap_kg") or {}).items() if t.is_num(kg))
    said = "".join(f"<li>{_pub(s['template'])}</li>" for s in val.get("method_statement", []) if s.get("template"))
    cites = "".join(f"<li>{_pub(c)}</li>" for c in ((val.get("exports") or {}).get("basis") or {}).get("sources", []))
    size = val.get("size") or {}
    return (
        (f'<ul class="stm">{said}</ul>' if said else "")
        + f'<dl class="facts lines">{"".join(lines)}{"".join(stuff)}</dl>'
        + (f'<h3 id="value-shares">Rock type, by class</h3><dl class="facts lines">{"".join(shares)}</dl>' if shares else "")
        + (f'<h3 id="value-prices">Prices</h3><table class="tbl narrow"><thead><tr><th scope="col">Metal</th>'
           f'<th scope="col" class="num">Price ($/kg)</th></tr></thead><tbody>{per_kg}</tbody></table>'
           + _note(prices.get("rule")) + _src(prices)
           + (f'<p class="src">{", ".join(_cited_links(prices["url"]))}</p>' if prices.get("url") else "")
           if per_kg else "")
        + (f'<h3 id="value-market">Price cap</h3>' + _note(market.get("choice"))
           + '<table class="tbl narrow"><thead><tr><th scope="col">Metal</th><th scope="col" class="num">Priced up to (kg)</th>'
           f'</tr></thead><tbody>{caps}</tbody></table>' + _src(market)
           if caps else "")
        + (f'<h3 id="value-size">Diameter, for a lower bound</h3>' + _note(size.get("basis")) if size.get("basis") else "")
        + _densities(m)
        + (f'<h3 id="value-sources">Sources</h3><ul class="srcs">{cites}</ul>' if cites else ""))


def _densities(m) -> str:
    den = (m.priors.get("density") or {})
    lines = []
    def walk(name, tbl):
        if not isinstance(tbl, dict):
            return
        if _lo_hi(tbl, "kg/m³"):
            when = t.r(_pub(tbl["when"])) if tbl.get("when") else ""
            lines.append(t.line(_pub(name), _lo_hi(tbl, "kg/m³"), when,
                                f'<span class="src">{_linked(_public(tbl.get("cite")))}</span>' if tbl.get("cite") else ""))
        for key, sub in tbl.items():
            if isinstance(sub, dict):
                walk(f"{name}, {key.replace('_', ' ')}", sub)
    for cls, tbl in den.items():
        walk(f"Class {cls}", tbl)
    return f'<h3 id="density">Density, for a mass</h3><dl class="facts">{"".join(lines)}</dl>' + _src(den) if lines else ""


def _formula(text) -> str:
    """A formula from a method file in the reference layer's notation: italic symbols, true minus signs,
    subscripts, a centred dot for a product."""
    s = t.esc(text)
    s = s.replace("H2(", "<var>H</var><sub>2</sub>(").replace("log2(", "log<sub>2</sub>(")
    s = re.sub(r"(?<![\w>/])(gain|[pqx])(?![\w<])", r"<var>\1</var>", s)
    return s.replace(" * ", " · ").replace(" - ", " − ").replace("= -", "= −").replace("(-", "(−")


def _observing(m) -> str:
    obs = m.observe
    lines = []
    for o in obs.get("observations", []):
        need = (obs.get("needs") or {}).get(o["id"]) or {}
        tiers = "; ".join(f'{tier["label"]} to magnitude {t.num(tier["max_mag"])}' for tier in need.get("tiers", []))
        if need.get("fainter"):
            tiers += f'; fainter, {need["fainter"]}'
        lines.append(t.line(_pub(o["label"]), t.v(_pub(t.cap(o.get("gives"))), True),
                            f'<span class="src">{_pub(t.cap(tiers))}</span>' if tiers else ""))
    gain, rank = obs.get("gain") or {}, obs.get("rank") or {}
    if rank.get("said"):
        lines.append(t.line("Ranked", t.v(_pub(t.cap(rank["said"])), True)))
    if gain.get("formula"):
        lines.append(t.line("Gain, in bits", f'<b class="v f">{_formula(gain["formula"])}</b>',
                            f'<span class="src"><var>p</var>: {_pub(gain.get("p"))}. <var>q</var>: {_pub(gain.get("q"))}. '
                            f'{_formula(gain.get("entropy") or "")}.</span>'))
    window = obs.get("window") or {}
    for key in ("pointable", "survey_only", "none"):
        if _public(window.get(key)):
            lines.append(t.line(t.cap(TIER_HEADS.get(key, key)), t.v(_pub(t.cap(_public(window[key]))), True)))
    return f'<dl class="facts lines">{"".join(lines)}</dl>' + _src(obs.get("window") or {})


METHOD_TOC = (("about", "Data"), ("states", "Marks"), ("ranges", "Ranges and chances"), ("coverage", "Coverage"),
              ("missions", "Missions"), ("ledger", "What counts as measured"), ("difficulty", "Difficulty"),
              ("flown", "What has flown"), ("value", "Metal and water"), ("observe", "Best next observation"),
              ("not-claimed", "Not claimed"), ("sources", "Sources"))
MARKS = (
    ("measured", "A source on file gives a value. A rock outline with a glow."),
    ("limit", "A source gives only an upper or lower limit, written with ≤ or ≥. A dashed outline."),
    ("prior", "No source on file gives a value, so the site estimates one from the asteroid's brightness and from "
              "asteroids like it. A dot, at half brightness. Zoomed in 4× or more, a half-bright outline."),
    ("unchecked", "A source that could hold a value was not queried, failed, or does not know the asteroid. The "
                  "value shown is still an estimate. The entry names the source and the reason."),
)
VERDICTS = (
    ("pass", "Measurements meet every condition. A heavier outline in the chart."),
    ("fail", "A measurement fails a condition. Faint in the chart."),
    ("untested", "At least one condition rests on an estimate. The site gives the chance that the asteroid fits."),
)
# Terms Method uses beyond the record layer's, each defined in a hover note where it first appears.
METHOD_TERMS = t.TERMS + (
    ("chondrite", "A stony meteorite, the commonest kind. Its classes, such as H, L and LL, differ in how much metal they hold."),
    ("g/t", "Grams per tonne."),
    ("random draws", "Possible asteroids, each drawn at random to fit what is on file. The site counts how many meet a condition."),
    ("spin barrier", "The fastest spin at which a loose pile of rock holds together, about once in 2.2 h."),
    ("tumbling", "Turning about more than one axis at once."),
    ("Tholen class", "A class from an older scheme, based on colours and reflectivity: P dark, M middle, E bright."),
    ("USGS", "United States Geological Survey."),
    ("ASIME", "Asteroid Science Intersections with In-Space Mine Engineering, a 2018 workshop."),
    ("C-type", "An asteroid of class C: dark and carbon-rich."),
)


def _prose_blocks(html: str) -> str:
    """docs/design.md section 5: a component that holds prose is set in the serif throughout. In each list of
    labelled lines that has a sentence among its values, every value in words takes the serif."""
    def one(m):
        block = m[0]
        return block.replace('class="v w"', 'class="v t"') if 'class="v t"' in block else block
    return re.sub(r'<dl class="facts[^"]*">.*?</dl>', one, html, flags=re.S)


def method_page(recs, sources, assets, data_date, method, tables=None) -> str:
    tables = tables or method_mod.load()
    marks = "".join(f'<tr><th scope="row">{t.state_tag(s, t.NOT_CHECKED if s == "unchecked" else None)}</th><td>{w}</td></tr>'
                    for s, w in MARKS)
    verdicts = "".join(f'<tr><th scope="row">{t.state_tag(s)}</th><td>{w}</td></tr>' for s, w in VERDICTS)
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in METHOD_TOC)
    sec = lambda sid, body: f'<section class="sec" id="{sid}"><h2>{dict(METHOD_TOC)[sid]}</h2>{body}</section>'
    secs = (
        sec("about", '<dl class="facts">'
            + t.line("Data date", t.v(t.date(data_date)))
            + t.line("Asteroids", t.v(t.count(len(recs))), '<span class="gr">JPL\'s list of reachable near-Earth asteroids, NHATS</span>')
            + t.line("Delta-v (Δv)", t.v("The total change of speed a spacecraft needs for the cheapest round trip, "
                                         "as JPL NHATS gives it", True))
            + t.line("Method", t.v(f"Version {t.esc(method)}", True), '<span class="gr">every figure is a proposal, not yet frozen</span>')
            + '</dl>')
        + sec("states", f'<table class="tbl marks"><tbody>{marks}</tbody></table>'
              f'<h3>Mission verdicts</h3><table class="tbl marks"><tbody>{verdicts}</tbody></table>')
        + sec("ranges", '<ul class="stm">'
              '<li>An estimate\'s range is a 90% range: 9 in 10 asteroids of that brightness fall inside it.</li>'
              '<li>A mass is always a 90% range, since the site computes it from draws of diameter and density.</li>'
              '<li>A measurement\'s range is the error its source states, ±1σ. The front page gives a measured '
              'value alone, and the entry gives its error.</li>'
              f'<li>A chance is the share of {t.count(tables.n_draws)} random draws of the asteroid that meet a condition. '
              'A share of none prints as &lt;1%, and a share of all as &gt;99%.</li></ul>')
        + sec("coverage", '<p class="cap">For each row of an entry, how many asteroids are in each state. None: no '
              'value counts, and there is nothing to estimate from. Sunlight push is never estimated.</p>'
              + counts_table(recs))
        + sec("missions", '<p class="note">A tag beside each figure says how the method set it: from the data, quoted '
              'from a source, or a judgement between quoted values.</p>' + _missions(tables))
        + sec("ledger", '<ul class="stm">'
              '<li>The lightcurve database grades each spin period from 1 to 3. A plus or a minus refines a grade.</li>'
              '<li>3: unambiguous. 2: may be wrong by 30%, or by a whole-number ratio. 1: may be completely wrong.</li>'
              '<li>The site lists a period graded under 2− and does not use it.</li></ul>'
              + _ledger(tables, sources))
        + sec("difficulty", _difficulty(tables))
        + sec("flown", _flown(tables))
        + sec("value", _value(tables))
        + sec("observe", _observing(tables))
        + sec("not-claimed", '<ul class="stm">' + "".join(f"<li>{t.esc(s)}</li>" for s in NOT_CLAIMED) + '</ul>')
        + sec("sources", t.sources_table(sorted(sources), sources)))
    body = (f'<main class="page doc"><div class="lhead"><h1>Method</h1></div>'
            f'<details class="toc-m"><summary>On this page</summary><ul>{toc}</ul></details>'
            f'<div class="body"><nav class="toc" aria-label="On this page"><ul>{toc}</ul></nav>'
            f'<div class="secs">{t.define(_prose_blocks(secs), METHOD_TERMS)}</div></div></main>')
    return t.page(title=f"Method | {t.SITE}", body=body, kind="method", depth=0, assets=assets,
                  data_date=data_date, method=method, current=t.METHOD_PAGE)


# ---------------------------------------------------------------- entry point

def write_site(records, sources, out_dir, assets, predictions=None, *, data_date=None, method=None,
               tables=None) -> list[Path]:
    """Write every page under out_dir, and the font, and return the paths, in a fixed order."""
    recs = [_plain(r) for r in records]
    srcs = {sid: _plain(s) for sid, s in dict(sources).items()}
    preds = [_plain(p) for p in (predictions or [])]
    for name in ("style", "app", "field_manifest"):
        if name not in assets:
            raise ValueError(f"assets is missing {name!r}")
    if data_date is None or method is None:
        if not recs:
            raise ValueError("no records: pass data_date and method")
        dates = sorted({r["data_date"] for r in recs})
        if len(dates) > 1:
            raise ValueError(f"records carry more than one data date: {dates}")
        data_date = data_date or dates[0]
        method = method or recs[0]["method"]
    keys = set()
    for r in recs:
        if not _KEY.fullmatch(r["key"]):
            raise ValueError(f"object key is not safe as a file name: {r['key']!r}")
        if r["key"] in keys:
            raise ValueError(f"duplicate object key: {r['key']!r}")
        keys.add(r["key"])
    tables = tables or method_mod.load()
    t.SPIN_SHARES = t.spin_lines(tables.priors["spin"]["thresholds_h"])
    observations = _observations(tables)
    gates = t.gate_lines(tables.missions)

    out = Path(out_dir)
    readout = assets.get("readout") or export_mod.readout([_record(r) for r in recs], tables)
    pages = [("index.html", index_page(recs, assets, data_date, method, readout))]
    pages += [(f"a/{r['key']}.html", entry_page(r, srcs, assets, data_date, method, observations, gates))
              for r in sorted(recs, key=lambda r: r["key"])]
    pages += [
        ("list/observe.html", observe_page(recs, srcs, assets, data_date, method, observations, tables)),
        ("record.html", record_page(preds, keys, assets, data_date, method)),
        (t.METHOD_PAGE, method_page(recs, srcs, assets, data_date, method, tables)),
    ]
    written = []
    for name, text in pages:
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        written.append(path)
    if "font" not in assets:                    # the stylesheet names it beside itself: static/fonts/
        for name in FONT_FILES:
            path = out / "static" / "fonts" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FONTS / name, path)
            written.append(path)
    return written
