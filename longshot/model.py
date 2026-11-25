"""The model, in order: draws and priors, missions, observe, value, ladder.

    records = model.run(ledger.build())

Last, summary.size_open_m: the size range from open values alone, where it differs
(export.open_size).

Each stage is also a function of its own (draws.apply, missions.apply,
observe.apply, value.apply, ladder.apply), taking and returning records. run
does the same work but draws once per object and hands the draws to every stage.
"""
from __future__ import annotations

from longshot import draws, export, ladder, missions, observe, value
from longshot import method as method_mod
from longshot.method import Method
from longshot.types import ObjectRecord

STAGES = (draws.apply_one, missions.apply_one, observe.apply_one, value.apply_one, ladder.apply_one)


def run_one(record: ObjectRecord, m: Method | None = None) -> ObjectRecord:
    m = m or method_mod.load()
    if record.method != m.version:
        raise method_mod.MethodError(f"record {record.key} is for method {record.method}, the files are {m.version}")
    d = draws.for_record(record, m)
    for stage in STAGES:
        stage(record, d, m)
    # the size a bulk file or a list may carry, where the record's own used a value that may not be redistributed
    size = export.open_size(record, m)
    if size is not None:
        record.summary["size_open_m"] = size
    return record


def run(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Fill prior, summary, missions, observe, value and ladder on every record, in place."""
    m = m or method_mod.load()
    for r in records:
        run_one(r, m)
    return records
