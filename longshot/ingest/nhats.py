"""JPL NHATS: the reachable list. It defines the reachable population.

Each row gives the cheapest round trip, the shortest one, the orbit code and the
next observing window. `obs_flag` "S" marks a window in which the object cannot
be pointed at and would have to be rediscovered by a survey
(docs/research/verify-obs-window.md, section 1).
"""
from __future__ import annotations

import functools
from pathlib import Path

from longshot import config, ids
from longshot.ingest._common import IngestError, date_cell, iso_date, num, number, read_json, text
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "jpl-nhats"
WINDOW_HORIZON = 2045            # JPL's window search runs to the end of this year
POINTABLE = "pointable"
SURVEY_ONLY = "survey-only"
NO_WINDOW = f"none through {WINDOW_HORIZON}"


def parse(path: Path | None = None) -> list[dict]:
    """The list's rows as JPL gives them, checked for shape."""
    path = Path(path or config.NHATS_JSON)
    doc = read_json(path)
    if not isinstance(doc, dict) or not isinstance(doc.get("data"), list):
        raise IngestError(f"{path}: expected an object with a 'data' array")
    rows = doc["data"]
    if not rows:
        raise IngestError(f"{path}: the reachable list is empty")
    count = num(doc.get("count"))
    if count is not None and int(count) != len(rows):
        raise IngestError(f"{path}: 'count' says {int(count)}, 'data' holds {len(rows)}")
    seen: set[str] = set()
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or not text(r.get("des")):
            raise IngestError(f"{path}: data[{i}] has no 'des'")
        if r["des"] in seen:
            raise IngestError(f"{path}: {r['des']!r} appears twice")
        seen.add(r["des"])
        dv = r.get("min_dv")
        if not isinstance(dv, dict) or num(dv.get("dv")) is None:
            raise IngestError(f"{path}: data[{i}] ({r['des']}) has no min_dv.dv")
    return rows


def source() -> Source:
    return Source(
        id=SOURCE_ID,
        name="JPL NHATS",
        edition=config.SNAPSHOT.name,
        retrieved=config.SNAPSHOT.name,
        licence="open",
        citation="NASA/JPL Center for Near-Earth Object Studies, "
                 "Near-Earth Object Human Space Flight Accessible Targets Study (NHATS)",
        url="https://cneos.jpl.nasa.gov/nhats/",
    )


@functools.lru_cache(maxsize=1)
def _keyed() -> tuple[tuple[str, dict], ...]:
    index = ids.load()
    out = []
    for r in parse():
        key = index.key_for_pdes(r["des"]) or index.resolve(r["des"])
        if key is None:
            raise IngestError(f"{config.NHATS_JSON}: {r['des']!r} has no key")
        out.append((key, r))
    out.sort(key=lambda kr: ids.sort_key(index.identity(kr[0])))
    return tuple(out)


def reachable() -> list[str]:
    """Keys of the reachable population, numbered objects first, then by designation."""
    return [k for k, _ in _keyed()]


def claims_for(key: str, r: dict) -> list[Claim]:
    out: list[Claim] = []

    def add(prop, value, unit="", **kw):
        if value is not None:
            out.append(Claim(key=key, prop=prop, source=SOURCE_ID, value=value, unit=unit, **kw))

    where = f"{config.NHATS_JSON}: {r['des']}"

    def n(cell, name):
        return number(cell, f"{where}: {name}")

    orbit = text(r.get("orbit_id"))
    ref = f"orbit solution {orbit}" if orbit else None
    dv = r["min_dv"]
    add("delta_v_kms", n(dv.get("dv"), "min_dv.dv"), "km/s", ref=ref)
    add("trip_days_at_min_delta_v", n(dv.get("dur"), "min_dv.dur"), "d", ref=ref)
    md = r.get("min_dur") if isinstance(r.get("min_dur"), dict) else {}
    add("min_trip_days", n(md.get("dur"), "min_dur.dur"), "d", ref=ref)
    add("min_trip_delta_v_kms", n(md.get("dv"), "min_dur.dv"), "km/s", ref=ref)
    add("n_trajectories", n(r.get("n_via_traj"), "n_via_traj"), "", ref=ref)
    add("H", n(r.get("h"), "h"), "mag", ref=ref)
    add("condition_code", n(r.get("occ"), "occ"), "", ref=ref)
    add("orbit_id", orbit)

    as_of = f"as of {config.DATA_DATE}"
    start, end = date_cell(r.get("obs_start"), f"{where}: obs_start"), date_cell(r.get("obs_end"), f"{where}: obs_end")
    if (start is None) != (end is None):
        raise IngestError(f"{where}: an observing window with only one end (obs_start {r.get('obs_start')!r}, "
                          f"obs_end {r.get('obs_end')!r})")
    if start and end:
        add("window_start", start, "date", ref=as_of)
        add("window_end", end, "date", ref=as_of)
        add("window_peak_mag", n(r.get("obs_mag"), "obs_mag"), "V mag", ref=as_of)
        flag = text(r.get("obs_flag"))
        if flag not in (None, "S"):
            raise IngestError(f"{where}: unknown obs_flag {flag!r}")
        add("window_pointing", SURVEY_ONLY if flag == "S" else POINTABLE, ref=as_of,
            note="would have to be rediscovered by a survey" if flag == "S" else None)
    else:
        add("next_window", NO_WINDOW, ref=as_of)
    # Goldstone only: the Arecibo entries are dead (the telescope collapsed in 2020).
    radar = iso_date(r.get("radar_obs_g"))
    if radar:
        snr = num(r.get("radar_snr_g"))
        add("radar_goldstone_date", radar, "date", ref=as_of,
            note=f"signal-to-noise {snr:g}" if snr is not None else None)
    return out


def load() -> tuple[list[Claim], list[Coverage]]:
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key, r in _keyed():
        claims += claims_for(key, r)
        coverage.append(Coverage(key=key, row="reach", source=SOURCE_ID, outcome="found"))
        coverage.append(Coverage(key=key, row="tracking", source=SOURCE_ID, outcome="found"))
    return claims, coverage
