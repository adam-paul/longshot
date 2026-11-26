"""Hand-entered measurements: registry/curated.toml.

A cited value that no database on disk holds (the JWST size of Kamoʻoalewa, the
period of 2022 OB5) is entered there by hand, with its citation and the file
and passage under docs/research where it was checked at the primary source.
Each becomes an ordinary claim. Licence class "single": shown on the object's
own page with its citation, never in a bulk file.

The list is not a catalogue that was looked up: it only adds claims. It writes
a coverage record where it has a value and none elsewhere, and the ledger never
counts it as a source that was or was not checked (longshot.ledger.SUPPLEMENTARY).
"""
from __future__ import annotations

import functools
import tomllib
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import IngestError, iso_date, read_bytes, sig
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "curated"
# prop -> (row, {unit as entered: factor to the claim's unit}, the claim's unit)
PROPS = {
    "diameter_m": ("size", {"m": 1.0, "km": 1000.0}, "m"),
    "period_h": ("spin", {"h": 1.0, "min": 1.0 / 60.0, "s": 1.0 / 3600.0}, "h"),
    "albedo": ("surface", {"": 1.0}, ""),
    "taxonomy": ("surface", None, ""),
}
REQUIRED = ("designation", "prop", "value", "citation", "verified_in", "verified_passage")
ALLOWED = set(REQUIRED) | {"error", "unit", "quality", "also_in"}


def parse(path: Path | None = None) -> tuple[str, list[dict]]:
    """(edition date, entries), checked: every entry names its citation and where it was verified."""
    path = Path(path or config.CURATED)
    try:
        doc = tomllib.loads(read_bytes(path).decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise IngestError(f"{path}: not valid TOML ({exc})") from exc
    edition = iso_date(doc.get("edition"))
    if edition is None or str(doc.get("edition")) != edition:
        raise IngestError(f"{path}: 'edition' must be the ISO date the file was last changed")
    entries = doc.get("claim")
    if not isinstance(entries, list):
        raise IngestError(f"{path}: no [[claim]] entries")
    for i, e in enumerate(entries):
        where = f"{path}: claim {i + 1}"
        missing = [k for k in REQUIRED if not e.get(k) and e.get(k) != 0]
        if missing:
            raise IngestError(f"{where} lacks {', '.join(missing)}")
        unknown = sorted(set(e) - ALLOWED)
        if unknown:
            raise IngestError(f"{where} has fields this reader does not know: {', '.join(unknown)}")
        if e["prop"] not in PROPS:
            raise IngestError(f"{where}: prop {e['prop']!r} is not one of {', '.join(PROPS)}")
        units = PROPS[e["prop"]][1]
        if units is None:
            if not isinstance(e["value"], str) or "error" in e or e.get("unit"):
                raise IngestError(f"{where}: a class is a label with no error and no unit")
        else:
            for k in ("value", "error"):
                v = e.get(k)
                if k in e and (isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0):
                    raise IngestError(f"{where}: {k} {v!r} is not a number above zero")
            if e.get("unit", "") not in units:
                raise IngestError(f"{where}: unit {e.get('unit')!r} is not one of {', '.join(repr(u) for u in units)}")
        if not (config.ROOT / e["verified_in"]).is_file():
            raise IngestError(f"{where}: verified_in {e['verified_in']!r} is not a file in the repository")
    return edition, entries


@functools.lru_cache(maxsize=1)
def _parsed() -> tuple[str, tuple[dict, ...]]:
    edition, entries = parse()
    return edition, tuple(entries)


def source() -> Source:
    edition = _parsed()[0]
    return Source(
        id=SOURCE_ID,
        name="Published papers",
        edition=edition,
        retrieved=edition,
        licence="single",
        citation="single values from published papers, each cited where it is shown",
        url="",
    )


def claim_for(key: str, e: dict) -> Claim:
    _, units, unit = PROPS[e["prop"]]
    if units is None:
        return Claim(key=key, prop=e["prop"], source=SOURCE_ID, value=e["value"].strip(),
                     quality=e.get("quality"), ref=e["citation"])
    k = units[e.get("unit", "")]
    value = sig(e["value"] * k)
    lo = hi = None
    if "error" in e:
        lo, hi = sig((e["value"] - e["error"]) * k), sig((e["value"] + e["error"]) * k)
        if lo <= 0:
            raise IngestError(f"{config.CURATED}: {e['designation']} {e['prop']}: the error reaches zero")
    return Claim(key=key, prop=e["prop"], source=SOURCE_ID, value=value, lo=lo, hi=hi, unit=unit,
                 quality=e.get("quality"), ref=e["citation"])


def load() -> tuple[list[Claim], list[Coverage]]:
    index = ids.load()
    reach = set(nhats.reachable())
    claims: list[Claim] = []
    rows: set[tuple[str, str]] = set()
    for e in _parsed()[1]:
        key = index.resolve(e["designation"])
        if key is None:
            raise IngestError(f"{config.CURATED}: {e['designation']!r} is not an object in the registry")
        if key not in reach:
            continue                    # entered for an object that has since left the reachable list
        claims.append(claim_for(key, e))
        rows.add((key, PROPS[e["prop"]][0]))
    coverage = [Coverage(key=key, row=row, source=SOURCE_ID, outcome="found") for key, row in sorted(rows)]
    return claims, coverage
