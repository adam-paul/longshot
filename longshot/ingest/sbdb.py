"""JPL Small-Body Database: orbit, tracking, H, and the physical and push values JPL holds.

Traps (AGENTS.md): the diameter field has taken no NEOWISE result since the 2019
compilation; rotation periods carry no quality grade; the bulk query rounds the
fitted push values to two figures and drops the force law they assume.
"""
from __future__ import annotations

import functools
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import IngestError, date_cell, num, number, read_json, sig, text
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "jpl-sbdb"
ROWS = ("tracking", "size", "spin", "surface", "push")
NEEDED = (
    "pdes", "H", "H_sigma", "diameter", "diameter_sigma", "albedo", "rot_per", "density", "spec_B", "spec_T",
    "e", "a", "q", "i", "moid", "class", "condition_code", "data_arc", "n_obs_used", "n_del_obs_used",
    "n_dop_obs_used", "first_obs", "last_obs", "A1", "A1_sigma", "A2", "A2_sigma", "A3", "A3_sigma", "orbit_id",
)
PUSH_NOTE = "bulk value, rounded to two figures; the force law is not given"
PERIOD_NOTE = "JPL gives no quality grade"


def parse(path: Path | None = None) -> dict[str, dict]:
    """JPL's table as {primary designation: row dict}, checked for shape."""
    path = Path(path or config.SBDB_JSON)
    doc = read_json(path)
    if not isinstance(doc, dict) or not isinstance(doc.get("fields"), list) or not isinstance(doc.get("data"), list):
        raise IngestError(f"{path}: expected an object with 'fields' and 'data'")
    fields, rows = doc["fields"], doc["data"]
    missing = [f for f in NEEDED if f not in fields]
    if missing:
        raise IngestError(f"{path}: fields missing: {', '.join(missing)}")
    if not rows:
        raise IngestError(f"{path}: no rows")
    count = num(doc.get("count"))
    if count is not None and int(count) != len(rows):
        raise IngestError(f"{path}: 'count' says {int(count)}, 'data' holds {len(rows)}")
    out: dict[str, dict] = {}
    for i, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(fields):
            raise IngestError(f"{path}: data[{i}] does not have {len(fields)} cells")
        d = dict(zip(fields, row))
        if not text(d["pdes"]):
            raise IngestError(f"{path}: data[{i}] has no pdes")
        out[d["pdes"]] = d
    return out


@functools.lru_cache(maxsize=1)
def _table() -> dict[str, dict]:
    return parse()


def source() -> Source:
    return Source(
        id=SOURCE_ID,
        name="JPL Small-Body Database",
        edition=config.SNAPSHOT.name,
        retrieved=config.SNAPSHOT.name,
        licence="open",
        citation="NASA/JPL Solar System Dynamics, Small-Body Database",
        url="https://ssd.jpl.nasa.gov/tools/sbdb_query.html",
    )


def _with_sigma(value: float | None, sigma: float | None) -> tuple[float | None, float | None]:
    if value is None or sigma is None or sigma <= 0:
        return None, None
    return sig(value - sigma), sig(value + sigma)


def claims_for(key: str, d: dict) -> list[Claim]:
    out: list[Claim] = []
    where = f"{config.SBDB_JSON}: {d.get('pdes')}"

    def add(prop, value, unit="", **kw):
        if value is not None:
            out.append(Claim(key=key, prop=prop, source=SOURCE_ID, value=value, unit=unit, **kw))

    def n(field):
        """The cell as a number; blank is None; anything else that is not a number stops the build."""
        return number(d.get(field), f"{where}: {field}")

    orbit = text(d.get("orbit_id"))
    ref = f"orbit solution {orbit}" if orbit else None

    # orbit and tracking
    add("condition_code", n("condition_code"), "", ref=ref)
    add("data_arc_days", n("data_arc"), "d", ref=ref)
    add("n_obs_used", n("n_obs_used"), "", ref=ref)
    add("n_radar_delay", n("n_del_obs_used"), "", ref=ref)
    add("n_radar_doppler", n("n_dop_obs_used"), "", ref=ref)
    add("first_obs", date_cell(d.get("first_obs"), f"{where}: first_obs"), "date", ref=ref)
    add("last_obs", date_cell(d.get("last_obs"), f"{where}: last_obs"), "date", ref=ref)
    add("orbit_id", orbit)
    add("orbit_class", text(d.get("class")))
    add("a_au", n("a"), "au", ref=ref)
    add("e", n("e"), "", ref=ref)
    add("i_deg", n("i"), "deg", ref=ref)
    add("q_au", n("q"), "au", ref=ref)
    add("moid_au", n("moid"), "au", ref=ref)

    # brightness
    h = n("H")
    lo, hi = _with_sigma(h, n("H_sigma"))
    add("H", h, "mag", lo=lo, hi=hi)

    # size, spin, surface
    dia = n("diameter")
    if dia is not None and dia > 0:
        s = n("diameter_sigma")
        lo, hi = _with_sigma(dia * 1000.0, s * 1000.0 if s is not None else None)
        add("diameter_m", sig(dia * 1000.0), "m", lo=lo, hi=hi)
    alb = n("albedo")
    if alb is not None and alb > 0:
        add("albedo", alb)
    per = n("rot_per")
    if per is not None and per > 0:
        add("period_h", per, "h", note=PERIOD_NOTE)
    for field, scheme in (("spec_B", "SMASSII"), ("spec_T", "Tholen")):
        cls = text(d.get(field))
        if cls:
            add("taxonomy", cls, quality=scheme)

    # push
    for prop in ("A1", "A2", "A3"):
        v = n(prop)
        if v is not None:
            lo, hi = _with_sigma(v, n(prop + "_sigma"))
            add(prop, v, "au/d^2", lo=lo, hi=hi, ref=ref, note=PUSH_NOTE)
    rho = n("density")
    if rho is not None and rho > 0:
        add("density_kgm3", sig(rho * 1000.0), "kg/m^3")
    return out


_ROW_PROPS = {
    "tracking": ("condition_code", "data_arc_days", "n_obs_used", "first_obs", "last_obs"),
    "size": ("diameter_m",),
    "spin": ("period_h",),
    "surface": ("albedo", "taxonomy"),
    "push": ("A1", "A2", "A3"),
}


def load() -> tuple[list[Claim], list[Coverage]]:
    table = _table()
    index = ids.load()
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key in nhats.reachable():
        d = table.get(index.identity(key).pdes)
        if d is None:
            for row in ROWS:
                coverage.append(Coverage(key=key, row=row, source=SOURCE_ID, outcome="unchecked",
                                         reason="not in JPL's table of near-Earth objects"))
            continue
        mine = claims_for(key, d)
        claims += mine
        props = {c.prop for c in mine}
        for row in ROWS:
            found = any(p in props for p in _ROW_PROPS[row])
            coverage.append(Coverage(key=key, row=row, source=SOURCE_ID, outcome="found" if found else "absent"))
    return claims, coverage
