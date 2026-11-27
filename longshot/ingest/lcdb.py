"""The Asteroid Lightcurve Database (LCDB) summary table: period, amplitude and the U grade.

Column positions are from the release's readme.pdf, section 4.1.3, and are
checked against the header line. The readme's rule (section 4.1.6): only U of
2- or better should be used for rotation-rate work.
"""
from __future__ import annotations

import functools
import re
import zipfile
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import (OLDER_THAN_OBJECT, IngestError, first_observed, num, read_table,
                                     research_retrieved, too_old_for)
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "lcdb"
SUMMARY = "lc_summary_pub.txt"
# name: (start, end), zero-based, from the readme's one-based "Pos" column
COLS = {
    "number": (0, 7), "name": (10, 40), "desig": (41, 61), "pflag": (143, 144), "period": (145, 158),
    "pdesc": (159, 174), "ampflag": (175, 176), "ampmin": (177, 181), "ampmax": (182, 186), "u": (187, 189),
    "notes": (190, 195),
}
_HEADER_AT = {"NUMBER": 0, "NAME": 10, "DESIG": 41, "PERIOD": 145, "AMIN": 177, "AMAX": 182, "U": 187, "NOTES": 190}
_GRADE = re.compile(r"^[0-3][+-]?$")
_MONTHS = {m: i for i, m in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
_GENERATED = re.compile(r"GENERATED:\s*([A-Za-z]{3})[a-z]*\s+(\d{1,2}),\s*(\d{4})")


def _summary_bytes(folder: Path) -> tuple[bytes, Path]:
    plain = folder / "x" / SUMMARY
    if plain.exists():
        return read_table(plain), plain
    for z in sorted(folder.glob("*.zip")):
        try:
            with zipfile.ZipFile(z) as zf:
                for name in zf.namelist():
                    if name.rsplit("/", 1)[-1] == SUMMARY:
                        raw = zf.read(name)
                        if not raw.strip():
                            raise IngestError(f"{z}!{name}: file is empty")
                        return raw, z
        except zipfile.BadZipFile as exc:
            raise IngestError(f"{z}: not a zip file ({exc})") from exc
    raise IngestError(f"{folder}: no {SUMMARY}, extracted or zipped")


def parse(folder: Path | None = None) -> tuple[str, list[dict]]:
    """(edition date, rows). A row: number, name, desig, pflag, period_h, pdesc, ampmin, ampmax, u, notes, line."""
    folder = Path(folder or config.LCDB_DIR)
    raw, path = _summary_bytes(folder)
    lines = raw.decode("latin-1").split("\n")
    edition = None
    start = None
    for i, line in enumerate(lines[:20]):
        m = _GENERATED.search(line)
        if m and m.group(1).title() in _MONTHS:
            edition = f"{int(m.group(3)):04d}-{_MONTHS[m.group(1).title()]:02d}-{int(m.group(2)):02d}"
        if line.startswith("NUMBER"):
            for label, at in _HEADER_AT.items():
                if not re.match(re.escape(label) + r"(\s|$)", line[at:at + len(label) + 1]):
                    raise IngestError(f"{path}: header column {label} is not at position {at + 1}")
            start = i + 1
            break
    if start is None:
        raise IngestError(f"{path}: no header line starting NUMBER")
    if edition is None:
        raise IngestError(f"{path}: no 'GENERATED:' date above the header")
    rows: list[dict] = []
    for n, line in enumerate(lines[start:], start + 1):
        line = line.rstrip("\r")
        if not line.strip() or set(line.strip()) == {"-"}:
            continue
        if len(line) < COLS["u"][1]:
            raise IngestError(f"{path}:{n}: line is cut short")
        cell = {k: line[a:b].strip() for k, (a, b) in COLS.items()}
        period = num(cell["period"])
        if cell["period"] and period is None:
            raise IngestError(f"{path}:{n}: period {cell['period']!r} is not a number")
        if cell["u"] and not _GRADE.match(cell["u"]):
            raise IngestError(f"{path}:{n}: U {cell['u']!r} is not a grade")
        if cell["number"] and not cell["number"].isdigit():
            raise IngestError(f"{path}:{n}: number {cell['number']!r} is not a number")
        rows.append({
            "number": int(cell["number"] or 0), "name": cell["name"], "desig": cell["desig"],
            "pflag": cell["pflag"], "period_h": period, "pdesc": cell["pdesc"],
            "ampmin": num(cell["ampmin"]), "ampmax": num(cell["ampmax"]), "ampflag": cell["ampflag"],
            "u": cell["u"] or None, "notes": cell["notes"], "line": n,
        })
    if not rows:
        raise IngestError(f"{path}: no data lines")
    return edition, rows


@functools.lru_cache(maxsize=1)
def _parsed() -> tuple[str, tuple[dict, ...]]:
    edition, rows = parse()
    return edition, tuple(rows)


def source() -> Source:
    return Source(
        id=SOURCE_ID,
        name="Asteroid Lightcurve Database (LCDB)",
        edition=_parsed()[0],
        retrieved=research_retrieved(),
        citation="Warner, Harris and Pravec 2009, Icarus 202, 134; LCDB release of " + _parsed()[0],
        url="https://minplanobs.org/mpinfo/php/lcdb.php",
    )


def resolve_row(r: dict, index: ids.Index) -> str | None:
    if r["number"] > 0:
        return index.resolve(None, number=r["number"])
    return index.resolve(r["desig"]) or index.resolve(r["name"])


def claims_for(key: str, r: dict) -> list[Claim]:
    out: list[Claim] = []
    ref = f"LCDB summary line, release of {_parsed()[0]}"
    p = r["period_h"]
    if p is not None and p > 0:
        kind = {">": "lower", "<": "upper"}.get(r["pflag"], "value")
        notes = []
        if r["pflag"] == "S":
            notes.append("sidereal")
        if r["pflag"] == "U":
            notes.append("flagged uncertain: a best guess")
        if r["u"] is None:
            notes.append("no grade assigned")
        out.append(Claim(key=key, prop="period_h", source=SOURCE_ID, kind=kind, value=p, unit="h",
                         quality=r["u"], ref=ref, note="; ".join(notes) or None))
    if r["ampmax"] is not None and r["ampmax"] > 0:
        kind = {">": "lower", "<": "upper"}.get(r["ampflag"], "value")
        lo = r["ampmin"] if r["ampmin"] and r["ampmin"] < r["ampmax"] else None
        out.append(Claim(key=key, prop="amplitude_mag", source=SOURCE_ID, kind=kind, value=r["ampmax"],
                         lo=lo, hi=r["ampmax"] if lo is not None else None, unit="mag", quality=r["u"], ref=ref))
    return out


def load() -> tuple[list[Claim], list[Coverage]]:
    index = ids.load()
    reach = set(nhats.reachable())
    edition = _parsed()[0]
    first = first_observed()
    by_key: dict[str, dict] = {}
    for r in _parsed()[1]:
        key = resolve_row(r, index)
        if key in reach and key not in by_key:
            by_key[key] = r
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key in nhats.reachable():
        r = by_key.get(key)
        mine = claims_for(key, r) if r else []
        claims += mine
        if any(c.prop == "period_h" for c in mine):
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="found")
        elif r:
            why = f"listed, period described as {r['pdesc']!r}" if r["pdesc"] else "listed, no period"
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="absent", reason=why)
        elif too_old_for(edition, first.get(key)):
            # the release was made before this asteroid was found: it was not looked at, not found wanting
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="unchecked", reason=OLDER_THAN_OBJECT)
        else:
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="absent")
        coverage.append(cov)
    return claims, coverage
