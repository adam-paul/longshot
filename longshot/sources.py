"""The sources the ledger reads, with their dates read from the data.

    from longshot.sources import SOURCES     # dict[str, Source], built on first use
    SOURCES["ssodnet"].edition               # "2026-09-14"

`edition` is the date of the upstream data and `retrieved` the date it was
fetched. Neither comes from the clock: they are read from the snapshot folder's
name, a file's own header or rows, the fetch journal, or the research archive's
file name.
"""
from __future__ import annotations

import functools

from longshot.types import LICENCES, Source


@functools.lru_cache(maxsize=1)
def load() -> dict[str, Source]:
    from longshot import ingest
    out: dict[str, Source] = {}
    for source_id, module in ingest.modules().items():
        s = module.source()
        if s.id != source_id or s.licence not in LICENCES:
            raise ValueError(f"source record for {source_id} is malformed")
        out[source_id] = s
    return out


def __getattr__(name: str):
    if name == "SOURCES":
        return load()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
