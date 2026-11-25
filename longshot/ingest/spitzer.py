"""Spitzer near-Earth-object surveys (ExploreNEOs, NEOSurvey, NEOLegacy): sizes and reflectivities.

One CSV, one line per observation; an object observed twice has two lines.
Diameters are in kilometres with separate lower and upper 1-sigma offsets.
The README asks for Trilling et al. 2010 and 2016 to be cited. The fits are
single-band thermal models with an assumed beaming parameter, so the errors
are wide (docs/research/catalogs.md).
"""
from __future__ import annotations

import csv
import functools
import io
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import (OLDER_THAN_OBJECT, IngestError, first_observed, iso_date, num, number, read_bytes,
                                     research_retrieved, sig, text, too_old_for)
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "spitzer"
NEEDED = ("desig", "name", "number", "survey", "midtime", "ch2snr", "diam", "d1sigl", "d1sigu", "pv", "pv1sigl",
          "pv1sigu")
QUALITY = "thermal model, one band"
CITATION = "Trilling et al. 2010, AJ 140, 770; Trilling et al. 2016, AJ 152, 172"


def parse(path: Path | None = None) -> list[dict]:
    path = Path(path or config.SPITZER_CSV)
    body = read_bytes(path).decode("utf-8")
    reader = csv.DictReader(io.StringIO(body))
    missing = [c for c in NEEDED if c not in (reader.fieldnames or [])]
    if missing:
        raise IngestError(f"{path}: columns missing: {', '.join(missing)}")
    rows = []
    for n, r in enumerate(reader, 2):
        if None in r or any(v is None for v in r.values()):
            raise IngestError(f"{path}:{n}: wrong number of cells")
        if not text(r["desig"]) and not text(r["number"]):
            raise IngestError(f"{path}:{n}: no designation and no number")
        if num(r["diam"]) is None:
            raise IngestError(f"{path}:{n}: diameter {r['diam']!r} is not a number")
        r["line"] = n
        rows.append(r)
    if not rows:
        raise IngestError(f"{path}: no data lines")
    return rows


@functools.lru_cache(maxsize=1)
def _rows() -> tuple[dict, ...]:
    return tuple(parse())


def edition() -> str:
    """The date of the last observation in the table: the surveys ended with the telescope."""
    return max((d for d in (iso_date(r["midtime"]) for r in _rows()) if d), default="")


def source() -> Source:
    return Source(
        id=SOURCE_ID,
        name="Spitzer NEO surveys",
        edition=edition(),
        retrieved=research_retrieved(),
        licence="single",
        citation=CITATION,
        url="https://github.com/mommermi/spitzerneos",
    )


def resolve_row(r: dict, index: ids.Index) -> str | None:
    number = text(r["number"])
    if number:
        return index.resolve(text(r["desig"]), number=number)
    return index.resolve(r["desig"])


def _range(value: float, down, up, scale: float = 1.0) -> tuple[float | None, float | None]:
    down, up = num(down), num(up)
    if down is None or up is None or (down == 0 and up == 0):
        return None, None
    return sig((value - abs(down)) * scale), sig((value + abs(up)) * scale)


CLOSED_REASON = "found after the Spitzer surveys ended"     # method/v0_1/ledger.toml [closed_tables].reason


def claims_for(key: str, r: dict) -> list[Claim]:
    """A size and a reflectivity from one line. Both carry the line's signal-to-noise in the 4.5 micron band
    (ch2snr), in `snr` and in words in `quality`; the ledger decides whether the fit counts."""
    out: list[Claim] = []
    where = f"{config.SPITZER_CSV}:{r.get('line')}"
    survey = text(r["survey"])
    ref = f"{survey}: {CITATION}" if survey else CITATION
    day = iso_date(r["midtime"])
    note = f"observed {day}" if day else None
    snr = number(r["ch2snr"], f"{where}: ch2snr")
    quality = QUALITY if snr is None else f"{QUALITY}, signal-to-noise {snr:g}"
    d = number(r["diam"], f"{where}: diam")
    if d is not None and d > 0:
        lo, hi = _range(d, r["d1sigl"], r["d1sigu"], 1000.0)          # km -> m
        out.append(Claim(key=key, prop="diameter_m", source=SOURCE_ID, value=sig(d * 1000.0), lo=lo, hi=hi,
                         unit="m", quality=quality, ref=ref, note=note, snr=snr))
    pv = number(r["pv"], f"{where}: pv")
    if pv is not None and pv > 0:
        lo, hi = _range(pv, r["pv1sigl"], r["pv1sigu"])
        out.append(Claim(key=key, prop="albedo", source=SOURCE_ID, value=sig(pv), lo=lo, hi=hi,
                         quality=quality, ref=ref, note=note, snr=snr))
    return out


def load() -> tuple[list[Claim], list[Coverage]]:
    index = ids.load()
    by_key: dict[str, list[dict]] = {}
    for r in _rows():
        key = resolve_row(r, index)
        if key is not None:
            by_key.setdefault(key, []).append(r)
    made, first = edition(), first_observed()
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key in nhats.reachable():
        mine: list[Claim] = []
        for r in by_key.get(key, []):
            mine += claims_for(key, r)
        claims += mine
        props = {c.prop for c in mine}
        late = key not in by_key and too_old_for(made, first.get(key))
        for row, prop in (("size", "diameter_m"), ("surface", "albedo")):
            if prop in props:
                cov = Coverage(key=key, row=row, source=SOURCE_ID, outcome="found")
            elif late:
                # method/v0_1/ledger.toml [closed_tables]: Spitzer stopped observing; the table is final.
                cov = Coverage(key=key, row=row, source=SOURCE_ID, outcome="absent", reason=CLOSED_REASON)
            else:
                cov = Coverage(key=key, row=row, source=SOURCE_ID, outcome="absent")
            coverage.append(cov)
    return claims, coverage
