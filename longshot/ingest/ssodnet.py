"""SsODNet: one literature card (ssoCard) per object, from two folders.

    config.SSODNET_CARDS                    the research snapshot (1,704 cards)
    data/sources/ssodnet/cards              cards fetched since, with journal.jsonl

A card on disk is a look that succeeded: each row is then "found" or "absent".
No card is "unchecked", with the reason from the journal where there is one:
SsODNet answers 404 for an object it does not know, which is not "absent".

An albedo or diameter whose method is "Computed" was calculated by SsODNet from
other values. It is kept as a claim with quality "Computed" and is never a
measurement.
"""
from __future__ import annotations

import functools
import json
import re
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import IngestError, iso_date, num, parse_json, read_bytes, research_retrieved, sig, text
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "ssodnet"
ROWS = ("size", "spin", "surface", "push")
COMPUTED = "Computed"

# Module attributes so a test can point them elsewhere.
LIVE_CARDS = config.SSODNET_LIVE_CARDS
JOURNAL = config.SSODNET_JOURNAL
PLACEHOLDER = "no usable error given"

A2_UNIT = 1e-15          # SsODNet gives A2 in 1e-15 au/d^2
DADT_UNIT = 1e-4         # and the drift in 1e-4 au/Myr


def unwrap(doc, path: Path) -> dict:
    """A card, whether bare or wrapped as {"<id>": {...}}."""
    if isinstance(doc, dict) and "parameters" not in doc and len(doc) == 1:
        doc = next(iter(doc.values()))
    if not isinstance(doc, dict) or not isinstance(doc.get("parameters"), dict):
        raise IngestError(f"{path}: not an SsODNet card (no 'parameters')")
    return doc


def read_card(path: Path) -> dict:
    path = Path(path)
    return unwrap(parse_json(read_bytes(path), path), path)


def read_journal(path: Path | None = None) -> dict[str, dict]:
    """{designation: last journal line}. Outcomes: card, unknown (404), failed."""
    path = Path(path or JOURNAL)
    if not path.exists():
        return {}
    body = path.read_text(encoding="utf-8")
    lines = body.split("\n")
    complete = body.endswith("\n")
    out: dict[str, dict] = {}
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError as exc:
            if n == len(lines) and not complete:
                continue          # the fetch job is mid-write on the last line
            raise IngestError(f"{path}:{n}: not valid JSON ({exc})") from exc
        if not isinstance(rec, dict) or not text(rec.get("des")) or rec.get("outcome") not in ("card", "unknown", "failed"):
            raise IngestError(f"{path}:{n}: expected des and an outcome of card, unknown or failed")
        out[rec["des"]] = rec
    return out


def read_status(folder: Path) -> dict[str, int]:
    """The research snapshot's _status.tsv: {designation: HTTP status}."""
    path = Path(folder) / "_status.tsv"
    if not path.exists():
        return {}
    out: dict[str, int] = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) < 2 or not cells[1].strip().isdigit():
            raise IngestError(f"{path}:{n}: expected designation, status")
        out[cells[0].strip()] = int(cells[1])
    return out


def card_key(card: dict, index: ids.Index) -> str | None:
    """The object a card describes, from what the card says, never from its file name."""
    number = card.get("number")
    if isinstance(number, int) and not isinstance(number, bool) and number > 0:
        return index.resolve(None, number=number)
    for field in ("name", "id"):
        key = index.resolve(card.get(field)) if text(card.get(field)) else None
        if key:
            return key
    return None


def card_file_name(des: str) -> str:
    """The file tools/fetch_ssodnet_cards.py writes a designation's card to."""
    return re.sub(r"[^A-Za-z0-9_]", "_", des.replace(" ", "_")) + ".json"


@functools.lru_cache(maxsize=1)
def _state() -> tuple[dict[str, dict], dict[str, dict], frozenset[str]]:
    """(cards, journal, names of live card files that could not be read), read once so they agree.

    The journal is read before the folders are listed. The fetch tool renames a finished card into place and
    only then writes its journal line, so every card the journal lists is on disk by the time the folder is
    read. A file in the live folder that does not parse and has no journal line is taken as a card still being
    written by a fetch job that writes in place: it is left out, and its object is "not checked", with that
    reason. One that does not parse and is in the journal is damaged, and stops the build; so does any
    unreadable card in the research snapshot, which nothing writes to.
    """
    index = ids.load()
    folders = [(0, Path(config.SSODNET_CARDS)), (1, Path(LIVE_CARDS))]
    present = [(rank, f) for rank, f in folders if f.is_dir()]
    if not present:
        raise IngestError(f"no SsODNet card folder: {folders[0][1]} or {folders[1][1]}")
    journal = read_journal()
    journalled = {card_file_name(des) for des, rec in journal.items() if rec["outcome"] == "card"}
    fetched = research_retrieved()
    out: dict[str, dict] = {}
    unreadable: set[str] = set()
    n = 0
    for rank, folder in present:
        for path in sorted(folder.glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                card = read_card(path)
            except IngestError:
                if rank == 1 and path.name not in journalled:
                    unreadable.add(path.name)
                    continue
                raise
            n += 1
            key = card_key(card, index)
            if key is None:
                continue
            edition = iso_date((card.get("ssocard") or {}).get("datetime")) or ""
            retrieved = fetched
            if rank == 1:
                des = index.identity(key).pdes
                at = iso_date((journal.get(des) or {}).get("at"))
                retrieved = at or ""
            rec = {"card": card, "path": path, "edition": edition, "retrieved": retrieved, "rank": rank}
            old = out.get(key)
            if old is None or (edition, rank) > (old["edition"], old["rank"]):
                out[key] = rec
    if n == 0:
        raise IngestError(f"no SsODNet cards in {' or '.join(str(f) for _, f in present)}")
    return out, journal, frozenset(unreadable)


def _cards() -> dict[str, dict]:
    """{key: {card, path, edition, retrieved}} for every card on disk that names a known object."""
    return _state()[0]


_cards.cache_clear = _state.cache_clear          # longshot.ingest.reset() clears by this name


def source() -> Source:
    cards = _cards().values()
    days = sorted({c["retrieved"] for c in cards if c["retrieved"]})        # the cards were fetched over several days
    return Source(
        id=SOURCE_ID,
        name="SsODNet",
        edition=max((c["edition"] for c in cards), default=""),
        retrieved=days[-1] if days else "",
        citation="Berthier et al. 2023, A&A 671, A151 (SsODNet ssoCard); each value carries its own reference",
        url="https://ssp.imcce.fr/webservices/ssodnet/",
        retrieved_from=days[0] if len(days) > 1 else "",
    )


# --------------------------------------------------------------------------
# a card -> claims

def _labels(entry: dict) -> str | None:
    labels = [text(m.get("label")) for m in entry.get("method") or [] if isinstance(m, dict)]
    labels = list(dict.fromkeys(x for x in labels if x))
    return "+".join(labels) if labels else None


def _ref(entry: dict) -> str | None:
    parts = []
    for b in entry.get("bibref") or []:
        if not isinstance(b, dict) or not text(b.get("shortbib")):
            continue
        code = text(b.get("bibcode"))
        parts.append(f"{b['shortbib']} ({code})" if code else b["shortbib"])
    return "; ".join(dict.fromkeys(parts)) if parts else None


def _measure(entry, scale: float = 1.0, positive: bool = False) -> tuple[float | None, float | None, float | None]:
    """(value, lo, hi) from {"value": v, "error": {"min": -a, "max": b}}.

    With `positive`, for a quantity that cannot be zero or less (a size, a reflectivity, a period, a density):
    an error that reaches zero or exceeds the value is a placeholder upstream, not a range, and is dropped.
    is_placeholder(entry) says when that happened.
    """
    if not isinstance(entry, dict):
        return num(entry), None, None
    v = num(entry.get("value"))
    if v is None:
        return None, None, None
    err = entry.get("error") if isinstance(entry.get("error"), dict) else {}
    down, up = num(err.get("min")), num(err.get("max"))
    lo = hi = None
    if down is not None and up is not None and (down != 0 or up != 0):
        lo, hi = sig((v - abs(down)) * scale), sig((v + abs(up)) * scale)
        if positive and (lo <= 0 or abs(up) > abs(v)):
            lo = hi = None
    return sig(v * scale), lo, hi


def is_placeholder(entry) -> bool:
    """True when _measure(entry, positive=True) dropped the stated error."""
    if not isinstance(entry, dict) or num(entry.get("value")) is None:
        return False
    return _measure(entry)[1] is not None and _measure(entry, positive=True)[1] is None


def _join(*notes) -> str | None:
    return "; ".join(n for n in notes if n) or None


def _as_list(x) -> list:
    if x is None:
        return []
    return [e for e in x if isinstance(e, dict)] if isinstance(x, list) else ([x] if isinstance(x, dict) else [])


def grade(flag) -> str | None:
    """'U=2+' -> '2+'. 'Quality of the period not rated.' and None -> None."""
    s = text(flag)
    if s and s.startswith("U=") and ";" not in s:
        g = s[2:].strip()
        if g[:1] in "0123" and g[1:] in ("", "+", "-"):
            return g
    return None


def claims_from_card(key: str, card: dict) -> list[Claim]:
    out: list[Claim] = []
    seen: set[tuple] = set()
    params = card["parameters"]
    physical = params.get("physical") if isinstance(params.get("physical"), dict) else {}
    dynamical = params.get("dynamical") if isinstance(params.get("dynamical"), dict) else {}

    def add(prop, value, unit="", **kw):
        if value is None:
            return
        c = Claim(key=key, prop=prop, source=SOURCE_ID, value=value, unit=unit, **kw)
        same = (c.prop, c.kind, c.value, c.lo, c.hi, c.quality, c.ref)
        if same not in seen:                                  # a card can list one entry twice
            seen.add(same)
            out.append(c)

    def placeholder(e):
        return PLACEHOLDER if is_placeholder(e) else None

    for e in _as_list(physical.get("diameter")):
        v, lo, hi = _measure(e, 1000.0, positive=True)        # km -> m
        if v is not None and v > 0:
            add("diameter_m", v, "m", lo=lo, hi=hi, quality=_labels(e), ref=_ref(e), note=placeholder(e))
    for e in _as_list(physical.get("albedo")):
        v, lo, hi = _measure(e, positive=True)
        if v is not None and v > 0:
            add("albedo", v, lo=lo, hi=hi, quality=_labels(e), ref=_ref(e), note=placeholder(e))
    for e in _as_list(physical.get("taxonomy")):
        cls = text(e.get("class"))
        if cls:
            how = " ".join(
                x for x in (text(e.get("scheme")), text(e.get("technique")), text(e.get("waverange"))) if x
            ) or None                                         # e.g. "Mahlke Spec VISNIR"
            add("taxonomy", cls, quality=how, ref=_ref(e))
            add("taxonomy_complex", text(e.get("complex")), quality=how, ref=_ref(e))
    for e in _as_list(physical.get("spins")):
        v, lo, hi = _measure(e.get("period"), positive=True)
        if v is not None and v > 0:
            note = _join(", ".join(x for x in (text(e.get("period_type")), text(e.get("technique"))) if x),
                         placeholder(e.get("period")))
            add("period_h", v, "h", lo=lo, hi=hi, quality=grade(e.get("period_flag")), ref=_ref(e), note=note)
    for e in _as_list(physical.get("density")):
        v, lo, hi = _measure(e, positive=True)
        if v is not None and v > 0:
            add("density_kgm3", sig(v), "kg/m^3", lo=lo, hi=hi, quality=_labels(e), ref=_ref(e),
                note=placeholder(e))
    for e in _as_list(dynamical.get("yarkovsky")):
        snr = num(e.get("snr"))
        note = f"signal-to-noise {snr:g}" if snr is not None else None
        v, lo, hi = _measure(e.get("A2"), A2_UNIT)
        if v is not None:
            add("A2", sig(v), "au/d^2", lo=lo, hi=hi, quality=_labels(e), ref=_ref(e), note=note, snr=snr)
        v, lo, hi = _measure(e.get("dadt"), DADT_UNIT)
        if v is not None:
            add("drift_au_per_myr", sig(v), "au/Myr", lo=lo, hi=hi, quality=_labels(e), ref=_ref(e), note=note,
                snr=snr)
    return out


_ROW_PROPS = {
    "size": ("diameter_m",),
    "spin": ("period_h",),
    "surface": ("albedo", "taxonomy"),
    "push": ("A2", "drift_au_per_myr", "density_kgm3"),
}


def _why_unchecked(des: str, journal: dict[str, dict], status: dict[str, int],
                   unreadable: frozenset[str] = frozenset()) -> str:
    if card_file_name(des) in unreadable:
        return "a card file is on disk and could not be read; it may still be being written"
    rec = journal.get(des)
    if rec:
        day = iso_date(rec.get("at"))
        when = f" on {day}" if day else ""
        if rec["outcome"] == "unknown":
            return f"SsODNet did not know this object{when}"
        if rec["outcome"] == "failed":
            if rec.get("status"):
                what = f" (HTTP {rec['status']})"
            elif "timed out" in (text(rec.get("error")) or "").lower():
                what = " (timed out)"
            else:
                what = ""
            return f"the request to SsODNet failed{when}{what}"
        return "the journal lists a card that is not on disk"
    if status.get(des) == 404:
        return f"SsODNet did not know this object on {research_retrieved()}"
    if des in status and status[des] != 200:
        return f"the request to SsODNet failed on {research_retrieved()} (HTTP {status[des]})"
    return "no SsODNet card has been fetched"


def load() -> tuple[list[Claim], list[Coverage]]:
    index = ids.load()
    cards, journal, unreadable = _state()
    status = read_status(Path(config.SSODNET_CARDS)) if Path(config.SSODNET_CARDS).is_dir() else {}
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key in nhats.reachable():
        rec = cards.get(key)
        if rec is None:
            reason = _why_unchecked(index.identity(key).pdes, journal, status, unreadable)
            for row in ROWS:
                coverage.append(Coverage(key=key, row=row, source=SOURCE_ID, outcome="unchecked", reason=reason))
            continue
        mine = claims_from_card(key, rec["card"])
        claims += mine
        props = {c.prop for c in mine}
        for row in ROWS:
            found = any(p in props for p in _ROW_PROPS[row])
            coverage.append(Coverage(key=key, row=row, source=SOURCE_ID, outcome="found" if found else "absent"))
    return claims, coverage
