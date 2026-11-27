"""Records -> build/records.jsonl, and the field file, its manifest and the keys file (docs/mvp.md section 5).

    assets = export.write(records)        # {"records", "field_manifest", "field", "keys"}

The field file holds the columns the first screen draws with, from any source
(every source is cited on the method page):

- The three size columns place the rock and size its outline: the record's size
  range; a measured diameter is plotted at its value.
- period_s is the rotation period the spin row rests on, and only when the row is
  measured and its sources do not disagree; otherwise 0, and the rock does not
  turn. A body that no longer exists does not turn.
- status_*, p_* and pct_* are this method's own verdicts: p_* for drawing,
  pct_* the whole percentage the entry prints, for the table view. No dollar
  figure is in the file.
- named is 1 where the asteroid has a name.

An object with no H has no size, so it cannot be placed in the field: it is left
out of the field and keys files, listed in the manifest's unplaced with its
delta-v, and counted under counts.not_placed. Its record is still in
records.jsonl, it has a page, and the lists link to it.

readout(records) is the front page's readout before anything is selected: the
named asteroids by delta-v.

Same records in, same bytes out: no clock, sorted by key, hashes of the bytes.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import struct
from pathlib import Path

from longshot import config
from longshot import draws as draws_mod
from longshot import ledger as ledger_mod
from longshot import shape
from longshot.method import Method
from longshot.types import ROWS, Fact, ObjectRecord, Row

SCHEMA = 1
# The columns the app reads, in order, and no others: anything else about an asteroid is in its record and on
# its entry. A feature that needs more in the field should fetch a second file.
COLUMNS = (
    ("dv", "f32"),
    ("size_q50", "f32"), ("size_q05", "f32"), ("size_q95", "f32"),
    ("period_s", "f32"), ("state", "u8"),
    ("p_surface", "u8"), ("p_capture", "u8"),
    ("status_surface", "u8"), ("status_capture", "u8"),
    ("pct_surface", "u8"), ("pct_capture", "u8"), ("named", "u8"),
    ("seed", "u16"),
)
TYPES = {"f32": ("f", 4), "u8": ("B", 1), "u16": ("H", 2), "i32": ("i", 4), "u32": ("I", 4)}
ALIGN = 4                                   # each column starts on a multiple of this many bytes
STATE_ROWS = ("size", "spin", "surface", "push")       # two bits each, size in the low bits
STATE_CODE = {"unchecked": 0, "prior": 1, "limit": 2, "measured": 3}
STATUS_CODE = {"fail": 0, "untested": 1, "pass": 2}
SIZE_ROWS = ("size", "surface")             # the rows whose facts go into a size


# --------------------------------------------------------------------------
# records.jsonl

def record_dict(record: ObjectRecord) -> dict:
    return dataclasses.asdict(record)


def dumps(record: ObjectRecord) -> str:
    return json.dumps(record_dict(record), ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def write_records(records: list[ObjectRecord], path: Path | None = None) -> Path:
    """One ObjectRecord per line, sorted by key."""
    path = Path(path or config.BUILD / "records.jsonl")
    lines = [dumps(r) + "\n" for r in sorted(records, key=lambda r: r.key)]
    _write_bytes(path, "".join(lines).encode("utf-8"))
    return path


def read_records(path: Path | None = None) -> list[ObjectRecord]:
    """records.jsonl or ledger.jsonl back into ObjectRecords."""
    path = Path(path or config.BUILD / "records.jsonl")
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            raw = json.loads(line)
            raw["rows"] = {name: Row(**{**row, "facts": [Fact(**f) for f in row.get("facts", [])]})
                           for name, row in raw["rows"].items()}
            out.append(ObjectRecord(**raw))
    return out


# --------------------------------------------------------------------------
# the field file

def _p_byte(mission: dict) -> int:
    status, p = mission.get("status"), mission.get("p")
    if status == "pass":
        return 255
    if status == "fail" or p is None:
        return 0
    return max(1, min(254, round(255 * p)))       # untested never reads as a pass or a fail


def _pct_byte(mission: dict) -> int:
    """The whole percentage an entry prints for the mission's chance: 0 for a fail or "under 1%", 100 for a pass
    or "over 99%", else 1 to 99, halves rounded up (as the entry rounds them). The status column says which."""
    status, p = mission.get("status"), mission.get("p")
    if status == "pass":
        return 100
    if status == "fail" or not draws_mod.is_num(p) or p < 0.005:
        return 0
    if p >= 0.995:
        return 100
    return max(1, min(99, math.floor(p * 100 + 0.5 + 1e-9)))


def period_s(record: ObjectRecord) -> float:
    """The rotation period the spin row rests on, in seconds, when the row is measured and its sources agree; else 0.
    The entry does not turn a rock whose sources disagree, so the field does not either."""
    row = record.rows["spin"]
    if record.gone or row.state != "measured" or not row.facts or row.conflicts:
        return 0.0
    adopted = next((f for f in row.facts if f.used and (f.label or "").casefold() == "period" and f.kind == "value"), None)
    if adopted is None or not draws_mod.is_num(adopted.value) or adopted.value <= 0 or adopted.unit not in draws_mod.TIME_H:
        return 0.0
    return adopted.value * draws_mod.TIME_H[adopted.unit] * 3600.0


# --------------------------------------------------------------------------
# the front page's readout: the named asteroids

def _dv(record: ObjectRecord) -> float | None:
    f = next((f for f in record.rows["reach"].facts if (f.label or "").casefold() == "delta-v"
              and f.unit == "km/s" and f.kind == "value" and draws_mod.is_num(f.value)), None)
    return float(f.value) if f is not None else None


def _entry(record: ObjectRecord) -> dict:
    return {"key": record.key, "designation": record.designation, "name": record.name, "number": record.number,
            "dv": _dv(record)}


def named(records: list[ObjectRecord]) -> list[dict]:
    """Every asteroid with a name, by delta-v, then key: [{key, designation, name, number, dv}]."""
    have = [r for r in records if r.name and _dv(r) is not None]
    return [_entry(r) for r in sorted(have, key=lambda r: (_dv(r), r.key))]


def readout(records: list[ObjectRecord], m: Method | None = None) -> dict:
    """{named: [...]}: the front page's readout before anything is selected (docs/design.md section 8)."""
    return {"named": named(records)}


def shape_seed(key: str) -> int:
    """The low 16 bits of the key's seed: every bit the outline rule reads (longshot/shape.py)."""
    return shape.seed(key) & 0xFFFF


def _size(record: ObjectRecord) -> dict | None:
    size = (record.summary or {}).get("size_m") or {}
    if not all(draws_mod.is_num(size.get(q)) and size[q] > 0 for q in ("q05", "q50", "q95")):
        return None
    return {q: size[q] for q in ("q05", "q50", "q95")}


def measured_m(record: ObjectRecord) -> float | None:
    """The measured diameter (or bound) in metres that the size row rests on; None when the row is not measured
    or a bound. The field plots a measured rock at this value, and the front page prints it alone: its stated error
    is on the entry (docs/design.md section 6)."""
    state = record.rows["size"].state
    if state not in ("measured", "limit"):
        return None
    kinds = ("value",) if state == "measured" else ("upper", "lower")
    f = next((f for f in record.rows["size"].facts if f.used and f.kind in kinds and (f.label or "").casefold() == "diameter"
              and draws_mod.is_num(f.value) and f.value > 0 and f.unit in ("m", "km")), None)
    return float(f.value) * (1000.0 if f.unit == "km" else 1.0) if f is not None else None


def field_row(record: ObjectRecord) -> dict | None:
    """One object's values for every column, or None when it has no size or no delta-v to place it by. A measured
    size is plotted at its value (size_q50), not at the middle of its draws."""
    size = _size(record)
    measured = measured_m(record) if size is not None else None
    if measured is not None:
        size = {**size, "q50": measured}
    dv = next((f for f in record.rows["reach"].facts if (f.label or "").casefold().startswith("delta-v")
               and f.unit == "km/s" and f.kind == "value" and draws_mod.is_num(f.value)), None)
    if dv is None or size is None:
        return None
    state = 0
    for i, name in enumerate(STATE_ROWS):
        state |= STATE_CODE[record.rows[name].state] << (2 * i)
    missions = record.missions or {}
    surface, capture = missions.get("surface") or {}, missions.get("capture") or {}
    return {
        "dv": float(dv.value),
        "size_q50": size["q50"], "size_q05": size["q05"], "size_q95": size["q95"],
        "period_s": period_s(record),
        "state": state,
        "p_surface": _p_byte(surface), "p_capture": _p_byte(capture),
        "status_surface": STATUS_CODE.get(surface.get("status"), 1),
        "status_capture": STATUS_CODE.get(capture.get("status"), 1),
        "pct_surface": _pct_byte(surface), "pct_capture": _pct_byte(capture),
        "named": int(bool(record.name)),
        "seed": shape_seed(record.key),
    }


def pack(columns: dict[str, list]) -> tuple[bytes, list[dict]]:
    """{name: values} -> (bytes, [{name, type, offset}]): little-endian columns in COLUMNS order, each aligned."""
    blob, listing = bytearray(), []
    n = len(columns[COLUMNS[0][0]])
    for name, kind in COLUMNS:
        values = columns[name]
        if len(values) != n:
            raise ValueError(f"column {name} has {len(values)} values, expected {n}")
        code, _ = TYPES[kind]
        blob.extend(b"\0" * (-len(blob) % ALIGN))
        listing.append({"name": name, "type": kind, "offset": len(blob)})
        blob.extend(struct.pack(f"<{n}{code}", *values))
    return bytes(blob), listing


def read_field(manifest_path: Path) -> tuple[dict, dict[str, list], list]:
    """A pure-Python reader: manifest path -> (manifest, {column: values}, keys)."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blob = (manifest_path.parent / manifest["file"]).read_bytes()
    n, cols = manifest["n"], {}
    for col in manifest["columns"]:
        code, size = TYPES[col["type"]]
        end = col["offset"] + n * size
        if end > len(blob):
            raise ValueError(f"column {col['name']} runs to byte {end}, the file has {len(blob)}")
        cols[col["name"]] = list(struct.unpack_from(f"<{n}{code}", blob, col["offset"]))
    keys = json.loads((manifest_path.parent / manifest["keys_file"]).read_text(encoding="utf-8"))
    return manifest, cols, keys


def counts(records: list[ObjectRecord], placed: list[ObjectRecord], columns: dict[str, list]) -> dict:
    by_row = {row: {s: 0 for s in STATE_CODE} for row in ROWS}
    missions = {}
    for r in records:
        for row in ROWS:
            by_row[row][r.rows[row].state] += 1
        for name, mi in (r.missions or {}).items():
            missions.setdefault(name, {"pass": 0, "untested": 0, "fail": 0})[mi["status"]] += 1
    return {
        "objects": len(records),
        "placed": len(placed),
        "not_placed": len(records) - len(placed),
        "with_period": sum(1 for p in columns["period_s"] if p > 0),
        "size_state": [sum(1 for s in columns["state"] if s & 3 == code) for code in range(4)],
        "rows": by_row,
        "missions": missions,
        "observe": sum(1 for r in records if r.observe),
    }


def write_field(records: list[ObjectRecord], data_dir: Path | None = None) -> dict:
    """Write field.<hash>.bin, keys.<hash>.json and field.json into data_dir; return the manifest."""
    data_dir = Path(data_dir or config.DIST / "data")
    ordered = sorted(records, key=lambda r: r.key)
    columns = {name: [] for name, _ in COLUMNS}
    placed, keys, unplaced = [], [], []
    for r in ordered:
        row = field_row(r)
        name = [r.key, r.designation, r.name, r.number]
        if row is None:
            unplaced.append(name + [_dv(r)])            # no rock, but a row in the table view
            continue
        placed.append(r)
        keys.append(name)
        for name, _ in COLUMNS:
            columns[name].append(row[name])
    blob, listing = pack(columns)
    keys_bytes = json.dumps(keys, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    field_name = f"field.{hashlib.sha256(blob).hexdigest()[:12]}.bin"
    keys_name = f"keys.{hashlib.sha256(keys_bytes).hexdigest()[:12]}.json"
    dates = {r.data_date for r in records} or {config.DATA_DATE}
    methods = {r.method for r in records} or {config.METHOD}
    if len(dates) != 1 or len(methods) != 1:
        raise ValueError(f"records disagree on the data date or the method: {sorted(dates)}, {sorted(methods)}")
    manifest = {
        "schema": SCHEMA, "data_date": dates.pop(), "method": methods.pop(), "n": len(keys),
        "file": field_name, "columns": listing, "keys_file": keys_name,
        "counts": counts(records, placed, columns),
        # Not drawn (no size to place them by), but they have pages: search must still find them.
        "unplaced": unplaced,
    }
    data_dir.mkdir(parents=True, exist_ok=True)
    for old in list(data_dir.glob("field.*.bin")) + list(data_dir.glob("keys.*.json")):
        if old.name not in (field_name, keys_name):
            old.unlink()
    _write_bytes(data_dir / field_name, blob)
    _write_bytes(data_dir / keys_name, keys_bytes)
    _write_bytes(data_dir / "field.json", (json.dumps(manifest, indent=1) + "\n").encode("utf-8"))
    return manifest


def write(records: list[ObjectRecord], build_dir: Path | None = None, dist_dir: Path | None = None) -> dict:
    """Stage 8. Returns the asset URLs, relative to the site root, and the path of records.jsonl."""
    build_dir = Path(build_dir or config.BUILD)
    dist_dir = Path(dist_dir or config.DIST)
    records_path = write_records(records, build_dir / "records.jsonl")
    manifest = write_field(records, dist_dir / "data")
    return {
        "records": str(records_path),
        "field_manifest": "data/field.json",
        "field": f"data/{manifest['file']}",
        "keys": f"data/{manifest['keys_file']}",
    }
