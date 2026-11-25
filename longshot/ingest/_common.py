"""Shared by the ingest modules: the error type, cached file readers, number helpers.

Nothing here opens a network connection or reads the clock.
"""
from __future__ import annotations

import functools
import glob
import hashlib
import json
import math
import re
from pathlib import Path

from longshot import config


class IngestError(Exception):
    """A source file is missing, empty or not in the shape its reader expects.

    Raised instead of returning nothing: a damaged file must never read as
    "the source has no value for this object".
    """


def read_bytes(path: Path) -> bytes:
    path = Path(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise IngestError(f"{path}: cannot read ({exc.strerror or exc})") from exc
    if not raw.strip():
        raise IngestError(f"{path}: file is empty")
    return raw


def read_table(path: Path) -> bytes:
    """read_bytes for a text table, checked against its checksum when one is kept beside it.

    A fixed-width table cut short at a line boundary still parses, and the objects on the lost lines would
    read as "the table has no value". `<file>.sha256` beside the file, holding the SHA-256 of its bytes in hex,
    turns that into a stopped build. tools/checksum_tables.py writes the two this project keeps.
    """
    path = Path(path)
    raw = read_bytes(path)
    side = path.with_name(path.name + ".sha256")
    if side.exists():
        want = side.read_text(encoding="utf-8").split()[0].strip().lower() if side.read_text(encoding="utf-8").split() else ""
        got = hashlib.sha256(raw).hexdigest()
        if want != got:
            raise IngestError(f"{path}: its bytes do not match {side.name} (the file was cut short or changed)")
    return raw


def parse_json(raw: bytes, path: Path):
    try:
        return json.loads(raw)
    except ValueError as exc:
        raise IngestError(f"{path}: not valid JSON ({exc})") from exc


@functools.lru_cache(maxsize=8)
def _read_json_cached(path: str):
    return parse_json(read_bytes(Path(path)), Path(path))


def read_json(path: Path):
    """Parse a JSON file once per process. Callers must not mutate the result."""
    return _read_json_cached(str(Path(path)))


def num(v) -> float | None:
    """A float from an upstream cell, or None for blank, null or non-finite."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
    else:
        s = str(v).strip()
        if not s:
            return None
        try:
            f = float(s)
        except ValueError:
            return None
    return f if math.isfinite(f) else None


def number(v, where: str) -> float | None:
    """As num, but a cell that is present and is not a number raises: it must never read as blank.

    `where` names the file, the object and the field for the message.
    """
    f = num(v)
    if f is not None:
        return f
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):                 # non-finite
        raise IngestError(f"{where}: {v!r} is not a finite number")
    if str(v).strip():
        raise IngestError(f"{where}: {v!r} is not a number")
    return None


def sig(x: float | None, digits: int = 10) -> float | None:
    """Round to significant figures, so unit conversions do not print 55.99999999999999."""
    if x is None:
        return None
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(math.floor(math.log10(abs(x)))))


def text(v) -> str | None:
    """A stripped string, or None when the cell is blank."""
    if v is None:
        return None
    s = str(v).strip()
    return s or None


_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def iso_date(s) -> str | None:
    """The first ISO date in a string, checked for plausibility."""
    if not s:
        return None
    m = _ISO.search(str(s))
    if not m:
        return None
    y, mo, d = (int(g) for g in m.groups())
    if not (1800 <= y <= 2200 and 1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return m.group(0)


def date_cell(v, where: str) -> str | None:
    """A cell that holds a date, or nothing. Something present that is not an ISO date raises."""
    if v is None or not str(v).strip():
        return None
    s = str(v).strip()
    m = _ISO.match(s)
    if not m or iso_date(m.group(0)) is None or (len(s) > 10 and s[10] not in " T"):
        raise IngestError(f"{where}: {v!r} is not a date")
    return m.group(0)


def first_observed() -> dict[str, str]:
    """{key: date of the first observation JPL holds}, for the reachable population."""
    from longshot import ids
    from longshot.ingest import nhats, sbdb
    table, index = sbdb._table(), ids.load()
    out = {}
    for key in nhats.reachable():
        d = table.get(index.identity(key).pdes)
        day = iso_date(d.get("first_obs")) if d else None
        if day:
            out[key] = day
    return out


OLDER_THAN_OBJECT = "older than this object"     # method/v0_1/ledger.toml [fixed_tables].reason


def too_old_for(edition: str, first_obs: str | None) -> bool:
    """A fixed table says nothing about an asteroid first observed after its edition date.

    method/v0_1/ledger.toml [fixed_tables]. An asteroid with no first observation on file is taken as covered.
    """
    return bool(edition and first_obs and first_obs > edition)


# The research snapshot (cards, lightcurve database, Spitzer table) was pulled on
# this date (AGENTS.md, "Read first"). The date is read from the archive's file
# name when the archive is on disk; this constant is the fallback.
RESEARCH_SNAPSHOT_FALLBACK = "2026-11-21"


def research_retrieved() -> str:
    """The date the research snapshot under config.RESEARCH was pulled."""
    dates = sorted(
        d for d in (iso_date(Path(p).name) for p in glob.glob(str(config.DATA / "research-data-*.tar.zst"))) if d
    )
    return dates[-1] if dates else RESEARCH_SNAPSHOT_FALLBACK
