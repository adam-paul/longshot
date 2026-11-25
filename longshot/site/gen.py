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

The generator computes no probability. It counts, sorts, formats and applies the
licence rule (templates.displayable, templates.open_size_of). Two orders and one switch
have their home elsewhere and are taken from there: the order of list/observe.html
(observe.ranked), and whether a page that lists many asteroids may print a size from a
source that is not open (export.OPEN_SIZES_ONLY, the field file's rule).

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
TIER_HEADS = {"pointable": "Pointable", "survey_only": "Survey recovery only", "none": "No window listed"}

NOT_CLAIMED = (
    "No single value for an asteroid. A dollar figure appears only as a range, the chance of "
    "nothing first, at dated list prices, for what is in the rock before any cost.",
    "No metal detection. These data cannot tell a metal-rich asteroid from the rest.",
    "No water detection from these data. Where no sample has come back, an entry gives the share of "
    "similar asteroids that hold water bound in minerals.",
    "No composition for one small asteroid beyond what is typical, until someone observes it.",
    "No live observing status. A window is a dated fact as of the data date.",
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

def _counts(recs: list) -> dict:
    c = {rid: {s: 0 for s in t.STATE_WORDS} for rid in t.ROWS}
    for r in recs:
        for rid in t.ROWS:
            state = (r["rows"].get(rid) or {}).get("state", "unchecked")
            c[rid][state if state in t.STATE_WORDS else "unchecked"] += 1
    return c


def _observable(recs: list) -> list:
    """The asteroids with an observation ranked, in the method's order (observe.ranked: the one home of it)."""
    by_key = {r["key"]: r for r in recs}
    have = [types.SimpleNamespace(key=r["key"], observe=r["observe"]) for r in recs if r.get("observe")]
    return [by_key[x.key] for x in observe_mod.ranked(have)]


def legend(recs: list) -> str:
    """The field's key at home, with what it counts: the size row's state of every rock drawn."""
    drawn = [r for r in recs if t.placed(r)]
    n = {s: sum(1 for r in drawn if (r["rows"].get("size") or {}).get("state") == s) for s in t.STATE_WORDS}
    items = ['<li class="of">Size</li>']
    for s, word in t.STATE_WORDS.items():
        if n[s] or s != "limit":
            items.append(f'<li>{t.glyph(s)}{word}<span class="n">{t.count(n[s])}</span></li>')
    items.append(f'<li class="nosize">No size<span class="n">{t.count(len(recs) - len(drawn))}</span></li>')
    return f'<ul>{"".join(items)}</ul>'


def counts_table(recs: list) -> str:
    counts = _counts(recs)
    short = {"limit": "Limit"}       # the column is narrow; the legend and entries say "Limit only"
    head = "".join(f'<th class="num" scope="col">{short.get(s, w)}</th>' for s, w in t.STATE_WORDS.items())
    body = "".join(
        f'<tr><th scope="row">{t.ROW_LABELS[rid]}</th>'
        + "".join(f'<td class="num{"" if counts[rid][s] else " dim"}">{t.count(counts[rid][s])}</td>' for s in t.STATE_WORDS)
        + "</tr>" for rid in t.ROWS)
    return (f'<table class="tbl counts"><thead><tr><th scope="col"><span class="vh">Row</span></th>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table>')


def _named_item(r: dict, words: str) -> str:
    """One line of the readout's list: {key, dv} from export.readout, linked to its entry."""
    dv = r.get("dv")
    return (f'<li><a href="a/{r["key"]}.html" data-key="{r["key"]}">{t.esc(words)}</a>'
            f'<span class="num">{f"{dv:.3f} {t.u("km/s")}" if dv is not None else ""}</span></li>')


def index_page(recs, assets, data_date, method, readout=None) -> str:
    """`readout` is export.readout's {named, typical}: the asteroids the readout lists before one is chosen."""
    drawn = sum(1 for r in recs if t.placed(r))
    total = len(recs)
    # the ceiling's slider spans the data's own delta-v, to a tenth of a km/s
    dvs = [v for v in (t.delta_v(r) for r in recs) if v is not None] or [0.0, 12.0]
    lo, hi = math.floor(min(dvs) * 10) / 10, math.ceil(max(dvs) * 10) / 10
    readout = readout or {}
    named, usual = readout.get("named") or [], readout.get("typical")
    seg = lambda name, items: "".join(
        f'<label><input type="radio" name="{name}" value="{v}"{" checked" if i == 0 else ""}><span>{w}</span></label>'
        for i, (v, w) in enumerate(items))
    preload = "".join(
        f'<link rel="modulepreload" href="{t.esc(url)}">\n' if kind == "module"
        else f'<link rel="preload" as="fetch" crossorigin href="{t.esc(url)}">\n'
        for url, kind in assets.get("preload", ()))
    extra = (f'<meta name="field-manifest" content="{t.esc(assets["field_manifest"])}">\n{preload}'
             '<noscript><style>#controls,.zoom,#field{display:none}</style></noscript>\n')
    overview = (
        '<h2>Named asteroids</h2>'
        f'<ul class="named">{"".join(_named_item(r, r["name"]) for r in named)}</ul>'
        + (f'<h2>Typical, nothing measured</h2><ul class="named">{_named_item(usual, usual["designation"])}</ul>' if usual else "")
        + f'<h2>On file</h2>{counts_table(recs)}')
    body = (
        '<main class="app" id="app">\n'
        '<form class="strip" id="controls" action="index.html" method="get" onsubmit="return false">'
        '<div class="ctl view" role="radiogroup" aria-labelledby="l-view"><span class="lab" id="l-view">View</span>'
        f'<div class="seg">{seg("view", (("chart", "Chart"), ("table", "Table")))}</div></div>'
        '<div class="ctl mission" role="radiogroup" aria-labelledby="l-m"><span class="lab" id="l-m">Mission</span>'
        f'<div class="seg">{seg("m", (("", "Any"), ("surface", t.MISSION_LABELS["surface"]), ("capture", t.MISSION_LABELS["capture"])))}</div></div>'
        '<div class="ctl dv"><label class="lab" for="dv">Delta-v ceiling</label><div class="dvrow">'
        f'<input id="dv" name="dv" type="range" min="{lo:g}" max="{hi:g}" step="0.1" value="{hi:g}">'
        f'<output name="dv-value" for="dv">{hi:.1f} km/s</output></div></div>'
        '<div class="ctl find"><label class="lab" for="q">Find asteroid</label>'
        '<input id="q" name="q" type="search" placeholder="Designation, name or number" autocomplete="off"></div>'
        f'<p class="ctl shown"><span class="lab" id="count-label">Plotted</span><output name="count">{t.count(drawn)} of {t.count(total)}</output></p>'
        '</form>\n'
        '<section class="fig" aria-labelledby="fig-title"><h1 id="fig-title" class="vh">Reachable asteroids</h1>'
        f'<div class="fig-head"><div id="legend" class="legend">{legend(recs)}</div>'
        '<div class="zoom" role="group" aria-label="Zoom">'
        '<button type="button" class="btn sq" name="zoom-out" form="controls" aria-label="Zoom out">−</button>'
        '<output name="zoom" form="controls">1.0×</output>'
        '<button type="button" class="btn sq" name="zoom-in" form="controls" aria-label="Zoom in">+</button>'
        '<button type="button" class="btn" name="zoom-reset" form="controls">Reset</button></div></div>'
        '<figure id="plot" class="plot">'
        f'<canvas id="field" tabindex="0" aria-label="Scatter plot of {t.count(drawn)} asteroids: delta-v of the cheapest '
        'round trip across, size up on a log scale"></canvas>'
        '<div id="axes" aria-hidden="true"></div><div id="tip" hidden></div>'
        '<noscript><p class="noscript-fig">The chart and the table need JavaScript.</p></noscript></figure>'
        '<section id="table" class="tview" hidden aria-label="Reachable asteroids, as a table">'
        '<div class="tscroll"><table class="ftbl"><thead></thead><tbody></tbody></table></div>'
        '<div class="pager"><output name="rows" form="controls"></output>'
        '<button type="button" class="btn" name="page-prev" form="controls">Previous</button>'
        '<button type="button" class="btn" name="page-next" form="controls">Next</button></div></section>'
        '</section>\n'
        f'<aside id="readout" class="readout" aria-label="Readout"><div class="overview">{overview}</div></aside>\n'
        '</main>'
    )
    return (
        t.head(t.SITE, assets, 0, extra)
        + '<body data-page="field">\n'
        + t.header(0, data_date, "index.html")
        + body + "\n"
        + t.footer(0, data_date, method)        # on a phone the header's date is in the menu; this line keeps it on the page
        + f'<script type="module" src="{t.esc(assets["app"])}"></script>\n'
        + '</body>\n</html>\n'
    )


# ---------------------------------------------------------------- entries

def _observations(tables) -> dict:
    """{observation id: its name} from observe.toml."""
    return {o["id"]: o["label"] for o in tables.observe.get("observations", [])}


def entry_page(rec, sources, assets, data_date, method, observations=None, gates=None) -> str:
    head, _ = t.names(rec)
    title = head if head == rec["designation"] else f'{head}, {rec["designation"]}'
    return t.page(
        title=f'{title} | {t.SITE}', body=t.entry(rec, sources, observations, gates, data_date),
        kind="entry", depth=1, assets=assets, data_date=data_date, method=method)


# ---------------------------------------------------------------- what to observe next

def size_cell(rec, sources) -> str:
    """A list prints only what the field file may carry (templates.open_size_of) while export.OPEN_SIZES_ONLY
    is set: a size from a source licensed for single values is on the asteroid's own page, with its citation.
    The size row's state leads, as its mark, so an estimate never reads as a measurement."""
    s = t.open_size_of(rec, sources) if export_mod.OPEN_SIZES_ONLY else t.size_of(rec, sources)
    state = (rec["rows"].get("size") or {}).get("state", "unchecked")
    mark = t.glyph(state, t.STATE_WORDS.get(state, state))
    if not s:
        return f'<td class="num sz"><span>{mark}none on file</span></td>'
    if s["mid"] is None:
        return f'<td class="num sz"><span>{mark}<span class="dim">on entry</span></span></td>'
    if s["state"] in ("measured", "limit") and not s.get("withheld"):
        sign = {"upper": "under ", "lower": "over "}.get(s["kind"], "")
        text = sign + t.num(s["mid"], 3)
    else:
        text = f'{t.num(s["lo"], 2)}–{t.num(s["hi"], 2)}' if s["lo"] else t.num(s["mid"], 2)
    if s.get("withheld"):
        text = f'<span class="dim" title="Placed by brightness; the measured size is on the entry">{text}</span>'
    return f'<td class="num sz"><span>{mark}{text}</span></td>'


def observe_page(recs, sources, assets, data_date, method, observations=None, tables=None) -> str:
    ranked = _observable(recs)
    tiers = {}
    for r in ranked:
        tiers[r["observe"].get("tier")] = tiers.get(r["observe"].get("tier"), 0) + 1
    rows, tier, run = [], object(), None
    for i, r in enumerate(ranked, 1):
        o = r["observe"]
        if o.get("tier") != tier:
            tier, run = o.get("tier"), None
            if tier in TIER_HEADS:
                rows.append(f'<tr class="tier"><th colspan="9" scope="rowgroup">{TIER_HEADS[tier]}'
                            f'<span>{t.count(tiers[tier])} asteroids</span></th></tr>')
        gate, mission = t.settles(r)
        what = (observations or {}).get(o.get("best"))
        said = (what, gate, mission) if gate and what else (None, o.get("text"), None)
        if said != run:
            run = said
            if said[0]:
                rows.append(f'<tr class="run"><th colspan="9" scope="rowgroup"><span class="k">Observation</span>{t.esc(said[0])}'
                            f'<span class="k">Settles</span>{t.esc(said[1])}, for {t.esc(said[2])}</th></tr>')
            else:
                rows.append(f'<tr class="run"><th colspan="9" scope="rowgroup">{t.esc(said[1])}</th></tr>')
        w = o.get("window") or {}
        start, end = (t.date(w["start"]), t.date(w["end"])) if w.get("start") and w.get("end") else ("", "")
        peak = f'{w["peak_mag"]:.1f}' if t.is_num(w.get("peak_mag")) else ""
        dv = t.delta_v(r)
        name = f' <span class="nm">{t.esc(r["name"])}</span>' if r.get("name") else ""
        check = ", ".join(t.esc(t.short_name(sources, s)) for s in o.get("unchecked") or [])
        pointable = (tier or observe_mod.tier(o.get("window"))) == "pointable"
        scope = t.esc(t.cap(o.get("needs") or "")) if pointable else ""    # the tier's heading says the rest
        # no per-cell labels: style.css names each column on a phone (.ltbl.obs td:nth-child)
        rows.append(
            f'<tr><td class="num rank">{i}</td><td class="ast"><a href="../a/{r["key"]}.html">{t.esc(r["designation"])}</a>{name}</td>'
            f'<td class="num">{f"{dv:.2f}" if dv is not None else ""}</td>{size_cell(r, sources)}'
            f'<td>{scope}</td><td class="num">{start}</td><td class="num">{end}</td>'
            f'<td class="num">{peak}</td><td class="dim chk">{check}</td></tr>')
    head = ('<tr><th scope="col" class="num">Rank</th><th scope="col">Asteroid</th>'
            '<th scope="col" class="num">Delta-v<br>km/s</th><th scope="col" class="num">Size, 9 in 10<br>m</th>'
            '<th scope="col">Telescope</th><th scope="col" class="num">Window<br>opens</th>'
            '<th scope="col" class="num">Window<br>closes</th><th scope="col" class="num">Peak<br>V mag</th>'
            '<th scope="col">Not checked:<br>look here first</th></tr>')
    table = (f'<table class="ltbl obs"><caption class="vh">Untested asteroids, ranked by what one observation would settle'
             f'</caption><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'
             if rows else '<p class="none">No untested asteroid has an observation ranked</p>')
    order = ((tables or method_mod.load()).observe.get("rank") or {}).get("said")
    body = (
        '<main class="page wide"><div class="lhead"><h1>Observe next</h1><dl class="lmeta">'
        f'<div><dt>Ranked</dt><dd>{t.count(len(ranked))} untested asteroids</dd></div>'
        + (f'<div><dt>Order</dt><dd>{t.esc(t.cap(order))}</dd></div>' if order else "")
        + f'</dl></div>{table}</main>')
    return t.page(title=f"Observe next | {t.SITE}", body=body, kind="list", depth=1,
                  assets=assets, data_date=data_date, method=method, current="list/observe.html")


# ---------------------------------------------------------------- the record

def _chance_cell(p: dict) -> str:
    """The chance held, with the spread between surveys where the prediction carries one."""
    text = t.pct(p.get("p"))
    lo, hi = p.get("p_low"), p.get("p_high")
    if t.is_num(lo) and t.is_num(hi) and lo < hi:
        text += f' <span class="dim">{t.pct(lo).rstrip("%")}–{t.pct(hi)}</span>'
    return text


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
    "class": ("Class, by brightness", "The chance that a reachable asteroid that gets a class gets each one.", ""),
    "spin": ("Spin, by brightness",
             "The chance that a reachable asteroid's first reliable period is faster than once in each time.", "Faster than"),
}


def _grid(preds: list) -> str | None:
    """One family of rules (class by band, spin by band) as one table: the statement once, with its two
    blanks; a row per band, a column per answer; what settles it once. None when the family does not
    have that shape, or a member is frozen or settled and so needs its own line."""
    bands = list(dict.fromkeys(p.get("band") for p in preds))
    by_band = {b: [p for p in preds if p.get("band") == b] for b in bands}
    width = len(by_band[bands[0]])
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
    rows_head = "H, mag" if first.endswith(" H") else ""
    cols = [t.cap(c) for c in columns]
    head = "".join(f'<th class="num" scope="col">{t.esc(c)}</th>' for c in cols)
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
        f'<dl class="lmeta"><div><dt>Settled by</dt><dd>{t.esc(t.cap(p.get("settles")))}</dd></div>'
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
            f'<td class="num" data-l="Chance held">{_chance_cell(p)}</td>'
            + (f'<td data-l="Frozen">{t.date(p["frozen"]) if p.get("frozen") else "not yet"}</td>' if frozen else "")
            + f'<td data-l="Settled by">{t.esc(t.cap(p.get("settles")))}</td><td data-l="When">{_when(p)}</td>'
            + (f'<td data-l="Outcome">{t.esc(p.get("outcome")) if p.get("outcome") else "open"}</td>' if outcome else "")
            + "</tr>")
    return (
        '<section class="rgroup"><table class="tbl flat"><thead><tr><th scope="col">Prediction</th>'
        '<th scope="col" class="num">Chance held</th>'
        + ('<th scope="col">Frozen</th>' if frozen else "") + '<th scope="col">Settled by</th><th scope="col">When</th>'
        + ('<th scope="col">Outcome</th>' if outcome else "") + f'</tr></thead><tbody>{"".join(rows)}</tbody></table></section>')


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
        f'<div><dt>Frozen</dt><dd>{t.count(frozen) if frozen else "none"}</dd></div>'
        f'<div><dt>Settled</dt><dd>{t.count(settled)}</dd></div>'
        f'</dl></div>{"".join(parts)}</main>')
    return t.page(title=f"Record | {t.SITE}", body=body, kind="record", depth=0, assets=assets,
                  data_date=data_date, method=method, current="record.html")


# ---------------------------------------------------------------- the method page

_public = t.public_text      # a line from a method file as a visitor reads it (templates.public_text)


def _pub(text) -> str:
    return t.esc(_public(text))


def _src(tbl: dict, *names: str) -> str:
    """Where a constant comes from, as its method file gives it: a public citation (`cite`) where the
    file has one, else its `source`, less what only points into the project."""
    for name in ("cite",) + (names or ("source",)):
        if tbl.get(name) and _public(tbl[name]):
            return f'<p class="src">{_linked(_public(tbl[name]))}</p>'
    return ""


def _note(text) -> str:
    return f'<p class="note">{_pub(text)}</p>' if text else ""


def _quantity(value, unit: str = "") -> str:
    """A constant with its unit; a unit the page has no short form for is spelt out after it."""
    short = t.UNITS.get(unit or "")
    shown = t.count(value) if isinstance(value, int) else t.num(value) if t.is_num(value) else _pub(value)
    return t.v(t.with_unit(shown, short) if short else f'<span class="c">{shown}</span>') + (
        f' <span class="gr">{_pub(unit)}</span>' if unit and not short else "")


def _gate(mid: str, g: dict) -> str:
    short = t.UNITS.get(g.get("unit") or "") or ""
    chosen = ""
    if isinstance(g.get("range"), list) and len(g["range"]) == 2:
        lo, hi = g["range"]
        chosen = t.r("chosen from " + (t.span(lo, hi, short) if short else f'<span class="c">{t.num(lo)}–{t.num(hi)}</span>'))
    kind = f'<span class="gr">{_pub(g["kind"])}</span>' if g.get("kind") else ""
    alts = "".join(
        f'<li><b>{t.with_unit(t.num(a["value"]), short) if short else t.num(a["value"])}</b> {_pub(a.get("what"))}</li>'
        for a in g.get("alternatives", []) if t.is_num(a.get("value")))
    return (
        f'<div class="th" id="g-{mid}-{t.esc(g["id"])}"><dl class="facts">'
        + t.line(_pub(g["label"]), _quantity(g["preset"], g.get("unit")), chosen, kind) + "</dl>"
        + (f'<ul class="alt">{alts}</ul>' if alts else "")
        + _src(g) + _note(g.get("caveat")) + _note(g.get("not_used")) + "</div>")


def _missions(m) -> str:
    mis, out = m.missions, []
    for mid in mis["order"]:
        spec = mis[mid]
        out.append(f'<h3 id="m-{mid}">{t.MISSION_LABELS.get(mid, _pub(mid))}</h3>'
                   f'<p class="note">{_pub(spec.get("summary"))}</p>' + "".join(_gate(mid, g) for g in spec["gates"]))
        skipped = [(k, v) for k, v in (spec.get("not_gated") or {}).items() if k not in ("kind", "source")]
        if skipped:
            out.append('<dl class="facts">' + "".join(
                t.line(f'Not a gate: {_pub(k.replace("_", "-"))}', t.v(_pub(v), True)) for k, v in skipped) + "</dl>")
    rules = mis.get("rules") or {}
    lines = []
    for name in ("gate", "mission"):
        if rules.get(name):
            lines.append(t.line(f"A {name} is", t.v(_pub("; ".join(rules[name])), True)))
    for name, word in (("period", "A period decides"), ("mass", "A mass decides"), ("size", "A size is set aside")):
        rule = rules.get(name) or {}
        text = rule.get("decides") or rule.get("implied")
        if name == "size" and t.is_num(rule.get("min_implied_reflectivity")):
            text = f"when it implies a reflectivity under {t.pct(rule['min_implied_reflectivity'])}"
        if text:
            lines.append(t.line(word, t.v(_pub(text), True), f'<span class="src">{_linked(_public(rule.get("cite") or rule.get("source")))}</span>'))
    return "".join(out) + (f'<h3 id="m-rules">Pass, fail, untested</h3><dl class="facts">{"".join(lines)}</dl>' if lines else "")


_NOT_VALUES = ("_kind", "_source", "_why", "_rule", "_basis", "_cite")
# ledger.toml's tables and keys, as the page names them.
LEDGER_WORDS = {
    ("period", "min_grade"): "Lightcurve grade, lowest counted",
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
    ("fixed_tables", "reason"): "Printed as",
    ("fixed_tables", "sources"): "Fixed tables",
    ("closed_tables", "rule"): "A closed table",
    ("closed_tables", "reason"): "Printed as",
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
                               + "</dl>" + _src(item, "evidence", "source") + "</div>")
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
            own = {"cite": tbl.get(f"{name}_cite"), "source": tbl.get(f"{name}_source")}
            said = LEDGER_WORDS.get((key, name)) or t.cap(f'{key.replace("_", " ")}, {name.replace("_", " ")}')
            lines.append(f'<div class="th" id="l-{t.esc(key)}-{t.esc(name)}"><dl class="facts">'
                         + t.line(t.esc(said), shown, f'<span class="gr">{_pub(kind)}</span>' if kind else "")
                         + "</dl>" + _note(more) + _src(own) + "</div>")
        if lines:
            out += lines
            out.append(_src({"cite": tbl.get("cite"), "source": tbl.get("source")}))
    return f'<h3 id="ledger">What counts as measured</h3>{"".join(out)}' if out else ""


_LADDER_UNITS = (("_min", "min"), ("_h", "h"), ("_m", "m"))


def _ladder(m) -> str:
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
        lines.append(t.line(t.with_unit(t.num(value), unit), t.v(_pub(basis), True)))
    spin = lad["spin_limit"]
    for name, rho in (("light_rock", spin.get("light_rock_kg_m3")), ("dense_rock", spin.get("dense_rock_kg_m3"))):
        lines.append(t.line(t.with_unit(t.num(spin[f"{name}_limit_h"]), "h"), t.v(_pub(
            f"a sphere of {t.num(rho)} kg/m³ with no cohesion sheds loose material from its equator when it turns faster"
            if t.is_num(rho) else "the spin at which loose material leaves the equator"), True)))
    for value, source in ((spin.get("screening_line_h"), spin.get("screening_line_source")),
                          (spin.get("published_bar_h"), spin.get("published_bar_source"))):
        if t.is_num(value):
            lines.append(t.line(t.with_unit(t.num(value), "h"), t.v(_pub(source), True)))
    flown = "".join(f"<li>{_pub(s['text'])}</li>" for s in lad.get("sitewide", []) if s.get("text"))
    facts = "".join(
        f'<li id="f-{t.esc(f["id"])}">{_pub(f.get("mission") or f["id"].replace("_", " "))}, '
        f'as of {t.date(f.get("as_of"))}. {_linked(_public(f.get("source")))}</li>'
        for f in lad.get("fact", []) if f.get("id") and f.get("source") and _URL.search(str(f["source"])))
    return (
        f'<h3 id="ladder">Difficulty</h3><dl class="facts">{rungs}</dl>'
        f'<dl class="facts lines">{"".join(lines)}</dl>' + _note(th.get("judgement"))
        + (f'<h3 id="flown">What has flown</h3><ul class="stm">{flown}</ul>' if flown else "")
        + (f'<ul class="srcs">{facts}</ul>' if facts else ""))


def _lo_hi(tbl, unit: str, k: float = 1.0) -> str:
    return t.v(t.span(tbl["lo"] * k, tbl["hi"] * k, unit)) if isinstance(tbl, dict) and t.is_num(tbl.get("lo")) and t.is_num(tbl.get("hi")) else ""


def _value(m) -> str:
    val, lines = m.value, []
    counted = val.get("counted") or {}
    for name, key in (("Metal counted", "metal"), ("Metal not counted", "metal_not_counted"),
                      ("Water counted", "water"), ("Left out", "left_out")):
        if counted.get(key):
            lines.append(t.line(name, t.v(_pub(counted[key]), True)))
    stuff = []
    for mat in (val.get("material") or {}).values():
        if not isinstance(mat, dict) or not mat.get("label"):
            continue
        basis = f'<span class="src">{_pub(mat.get("basis"))}</span>' if mat.get("basis") else ""
        if _lo_hi(mat.get("grade_ppm"), "g/t"):
            stuff.append(t.line(_pub(mat["label"]), _lo_hi(mat["grade_ppm"], "g/t"), t.r("platinum-group metal"), basis))
        elif mat.get("grade_table") in (val.get("grade_table") or {}):
            pts = val["grade_table"][mat["grade_table"]]
            stuff.append(t.line(_pub(mat["label"]), t.v(t.span(pts[0][1], pts[-1][1], "g/t")),
                                t.r("platinum-group metal in the metal"), basis)
                         + (t.line("", t.v(_pub(mat["caution"]), True)) if mat.get("caution") else ""))
        if _lo_hi(mat.get("water_fraction"), "%", 100.0):
            stuff.append(t.line(_pub(mat["label"]), _lo_hi(mat["water_fraction"], "%", 100.0), t.r("water by weight"), basis))
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
        t.line(_pub(el), t.v(f"{t.usd(row[0])} to {t.usd(row[-1])}"), t.r("a kilogram"))
        for el, row in (prices.get("usd_per_kg") or {}).items() if isinstance(row, list) and row)
    market = val.get("market") or {}
    caps = "".join(t.line(_pub(el), t.v(t.with_unit(t.count(kg), "kg")), t.r("priced, at most"))
                   for el, kg in (market.get("cap_kg") or {}).items() if t.is_num(kg))
    said = "".join(f"<li>{_pub(s['template'])}</li>" for s in val.get("method_statement", []) if s.get("template"))
    cites = "".join(f"<li>{_pub(c)}</li>" for c in ((val.get("exports") or {}).get("basis") or {}).get("sources", []))
    size = val.get("size") or {}
    return (
        '<h3 id="value">What is in it</h3>'
        + (f'<ul class="stm">{said}</ul>' if said else "")
        + f'<dl class="facts lines">{"".join(lines)}{"".join(stuff)}</dl>'
        + (f'<h3 id="value-shares">Which rock, by class</h3><dl class="facts lines">{"".join(shares)}</dl>' if shares else "")
        + (f'<h3 id="value-prices">Prices</h3><dl class="facts">{per_kg}</dl>'
           + _note(prices.get("rule")) + _src(prices) + (f'<p class="src">{_linked(prices["url"])}</p>' if prices.get("url") else "")
           if per_kg else "")
        + (f'<h3 id="value-market">How much of each metal is priced</h3>' + _note(market.get("choice"))
           + f'<dl class="facts">{caps}</dl>' + _src(market, "supply_source") if caps else "")
        + (f'<h3 id="value-size">Size, for a lower bound</h3>' + _note(size.get("basis")) if size.get("basis") else "")
        + (f'<h3 id="value-sources">Read for these</h3><ul class="stm">{cites}</ul>' if cites else ""))


def _densities(m) -> str:
    den = (m.priors.get("density") or {})
    lines = []
    def walk(name, tbl):
        if not isinstance(tbl, dict):
            return
        if _lo_hi(tbl, "kg/m³"):
            when = t.r(_pub(tbl["when"])) if tbl.get("when") else ""
            lines.append(t.line(_pub(name), _lo_hi(tbl, "kg/m³"), when,
                                f'<span class="src">{_linked(_public(tbl.get("cite") or tbl.get("source")))}</span>'))
        for key, sub in tbl.items():
            if isinstance(sub, dict):
                walk(f"{name}, {key.replace('_', ' ')}", sub)
    for cls, tbl in den.items():
        walk(f"Class {cls}", tbl)
    return f'<h3 id="density">Density, for a mass</h3><dl class="facts">{"".join(lines)}</dl>' + _src(den) if lines else ""


def _observing(m) -> str:
    obs = m.observe
    lines = []
    for o in obs.get("observations", []):
        need = (obs.get("needs") or {}).get(o["id"]) or {}
        tiers = "; ".join(f'{tier["label"]} to magnitude {t.num(tier["max_mag"])}' for tier in need.get("tiers", []))
        if need.get("fainter"):
            tiers += f'; fainter, {need["fainter"]}'
        lines.append(t.line(_pub(o["label"]), t.v(_pub(o.get("gives")), True),
                            f'<span class="src">{_pub(tiers)}</span>' if tiers else ""))
    gain, rank = obs.get("gain") or {}, obs.get("rank") or {}
    if rank.get("said"):
        lines.append(t.line("Ranked", t.v(_pub(t.cap(rank["said"])), True)))
    if gain.get("formula"):
        lines.append(t.line("Gain, in bits", t.v(t.esc(gain["formula"]), True),
                            f'<span class="src">{_pub("p: " + str(gain.get("p")) + ". q: " + str(gain.get("q")) + ".")}</span>'))
    window = obs.get("window") or {}
    for key in ("pointable", "survey_only", "none"):
        if _public(window.get(key)):
            lines.append(t.line(t.cap(TIER_HEADS.get(key, key)), t.v(_pub(t.cap(_public(window[key]))), True)))
    return f'<h3 id="observe">What would settle it</h3><dl class="facts lines">{"".join(lines)}</dl>' + _src(obs.get("window") or {})


def thresholds(m, sources: dict | None = None) -> str:
    """Every fixed figure an entry prints, with where it comes from: read from method/v0_1/*.toml."""
    return (
        '<p class="note">Each is a proposal. Kind says how it was set: measured from the data, quoted from a source, '
        'or a judgement between quoted values.</p>'
        + _missions(m) + _ledger(m, sources) + _ladder(m) + _value(m) + _densities(m) + _observing(m))


METHOD_TOC = (("about", "Data"), ("states", "States"), ("ranges", "Ranges"), ("spin-quality", "Spin quality"),
              ("thresholds", "Thresholds and inputs"), ("not-claimed", "Not claimed"), ("sources", "Sources"))


def method_page(recs, sources, assets, data_date, method, tables=None) -> str:
    tables = tables or method_mod.load()
    states = (
        ("measured", "A source gives a value. An unbroken outline that glows."),
        ("limit", "A source gives only a bound. A dashed outline."),
        ("prior", "Every source was checked and none has a value. A grey dot; what is typical at this brightness is shown."),
        ("unchecked", "A source was down, does not know the asteroid, was never asked, or is a table older than the "
                      "asteroid. A dashed ring. It never reads as not measured."),
    )
    legend = "".join(f'<tr><th scope="row">{t.state_tag(s)}</th><td>{w}</td></tr>' for s, w in states)
    marks = "".join(f'<tr><th scope="row">{t.state_tag(s)}</th><td>{w}</td></tr>' for s, w in (
        ("pass", "Every gate measured and passed. A heavy outline in the field."),
        ("untested", "A gate rests on what is typical: the chance of passing every gate. In the field, a dot brighter "
                     "as the chance rises."),
        ("fail", "A measured gate fails. A faint dot in the field.")))
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in METHOD_TOC)
    secs = (
        '<section class="sec" id="about"><h2>Data</h2><dl class="facts">'
        + t.line("Data as of", t.v(t.date(data_date)))
        + t.line("Method", t.v(f"version {t.esc(method)}", True), '<span class="gr">thresholds are proposals, not frozen</span>')
        + t.line("Asteroids", t.v(t.count(len(recs))), '<span class="gr">JPL\'s NHATS list of reachable asteroids</span>')
        + t.line("Record", t.v("a miss is listed the same way as a hit", True))
        + '</dl></section>'
        f'<section class="sec" id="states"><h2>States</h2><table class="tbl marks"><tbody>{legend}</tbody></table>'
        f'<h3>Missions</h3><table class="tbl marks"><tbody>{marks}</tbody></table></section>'
        '<section class="sec" id="ranges"><h2>Ranges</h2><p class="note">A range for something not measured holds 9 in 10 '
        f'asteroids of that brightness. A chance is a share of {t.count(tables.n_draws)} draws: none or all of them passing '
        'prints as under 1% or over 99%.</p></section>'
        '<section class="sec" id="spin-quality"><h2>Spin quality</h2><p class="note">U is the lightcurve database\'s quality '
        'code. 3: unambiguous. 2: may be wrong by 30% or by a whole-number ratio. 1: may be completely wrong; such a '
        'period is listed and not used.</p></section>'
        f'<section class="sec" id="thresholds"><h2>Thresholds and inputs</h2>{thresholds(tables, sources)}</section>'
        '<section class="sec" id="not-claimed"><h2>Not claimed</h2><ul class="stm">'
        + "".join(f"<li>{t.esc(s)}</li>" for s in NOT_CLAIMED) + '</ul></section>'
        f'<section class="sec" id="sources"><h2>Sources</h2>{t.sources_table(sorted(sources), sources)}</section>')
    body = (f'<main class="page doc"><div class="lhead"><h1>Method</h1></div>'
            f'<details class="toc-m"><summary>On this page</summary><ul>{toc}</ul></details>'
            f'<div class="body"><nav class="toc" aria-label="On this page"><ul>{toc}</ul></nav>'
            f'<div class="secs">{secs}</div></div></main>')
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
