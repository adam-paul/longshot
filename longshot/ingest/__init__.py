"""One module per source. Each exposes parse(), source() and
load() -> (list[Claim], list[Coverage]) for the reachable population.

No module here opens a network connection: everything is read from disk.
"""
from __future__ import annotations

SOURCE_IDS = ("jpl-nhats", "jpl-sbdb", "ssodnet", "pravec", "lcdb", "spitzer", "curated")


def modules() -> dict:
    """{source id: module}, in the order the ledger reads them."""
    from longshot.ingest import curated, lcdb, nhats, pravec, sbdb, spitzer, ssodnet
    return {m.SOURCE_ID: m for m in (nhats, sbdb, ssodnet, pravec, lcdb, spitzer, curated)}


def reset() -> None:
    """Forget everything read so far. For tests that point config at other files."""
    from longshot import ids, sources
    from longshot.ingest import _common, curated, lcdb, nhats, pravec, sbdb, spitzer, ssodnet
    _common._read_json_cached.cache_clear()
    ids.load.cache_clear()
    sources.load.cache_clear()
    nhats._keyed.cache_clear()
    sbdb._table.cache_clear()
    ssodnet._cards.cache_clear()
    pravec._rows.cache_clear()
    lcdb._parsed.cache_clear()
    spitzer._rows.cache_clear()
    curated._parsed.cache_clear()
