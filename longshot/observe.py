"""The best next observation: the one that would settle the most, per method/v0_1/observe.toml.

    records = observe.apply(records)      # stage 4: fills record.observe (needs record.missions)

    gain = H2(p) - q x H2(p / q)   bits

p is the share of the object's joint draws that pass every gate of a mission,
q the share that pass the one gate the observation resolves. Both are read from
record.missions, which counted them from the same draws.

    record.observe = {best, mission, gate, gain, text, needs, window, tier, unchecked,
                      label, mission_label, gate_label, gate_p} or None
    window = {start, end, peak_mag, pointable, as_of} or None
    tier = "pointable" | "survey_only" | "none": what kind of window JPL lists; it leads the ranking
    unchecked = the sources not checked for the row the observation would settle. The entry lists them once,
      beside the observation; text does not repeat them
    label, mission_label, gate_label = the observation's, the mission's and the gate's names (observe.toml,
    missions.toml); gate_p = the gate's chance now, as record.missions holds it

None when no mission is untested, no observation would change anything, or the
body no longer exists.
"""
from __future__ import annotations

import math

from longshot import draws as draws_mod
from longshot import method as method_mod
from longshot.method import Method
from longshot.types import ObjectRecord


def h2(x: float) -> float:
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return -x * math.log2(x) - (1.0 - x) * math.log2(1.0 - x)


def gain(p: float, q: float) -> float:
    """Expected drop, in bits, in the uncertainty of pass-or-fail when the gate with pass share q is resolved."""
    if not 0.0 < q < 1.0 or not 0.0 < p < 1.0:
        return 0.0
    return max(0.0, h2(p) - q * h2(min(1.0, p / q)))


def window(record: ObjectRecord) -> dict | None:
    """The next observing window as dated facts, from the tracking row; None when JPL lists none."""
    row = record.rows.get("tracking")
    start = draws_mod.find(row, "window start", numeric=False)
    end = draws_mod.find(row, "window end", numeric=False)
    if start is None or end is None or not start.value or not end.value:
        return None
    mag = draws_mod.find(row, "window peak brightness")
    pointing = draws_mod.find(row, "window pointing", numeric=False)
    return {
        "start": str(start.value), "end": str(end.value),
        "peak_mag": mag.value if mag is not None else None,
        "pointable": bool(pointing is not None and pointing.value == "pointable"),
        "as_of": record.data_date,
    }


def needs(m: Method, observation_id: str, w: dict | None) -> str:
    """What the observation takes, from the peak brightness of the window."""
    spec = m.observe["needs"]
    if w is None:
        return spec["not_pointable"]["no_window"]
    if not w["pointable"]:
        return spec["not_pointable"]["survey_only"]
    mag = w.get("peak_mag")
    table = spec[observation_id]
    if mag is None:
        return table["fainter"]
    for tier in table["tiers"]:
        if mag <= tier["max_mag"]:
            return tier["label"]
    return table["fainter"]


TIERS = ("pointable", "survey_only", "none")       # observe.toml [rank]: the order of the list
ROW_OF_GATE = {"size": "size", "mass": "size", "spin": "spin"}


def tier(w: dict | None) -> str:
    return "none" if w is None else "pointable" if w.get("pointable") else "survey_only"


def best(record: ObjectRecord, m: Method) -> dict | None:
    if getattr(record, "gone", None):
        return None
    missions = record.missions or {}
    top = None
    # Ties go to the lightcurve, then to surface work: observe.toml [choice].tie.
    for obs in m.observe["observations"]:
        for mission in m.missions["order"]:
            mi = missions.get(mission)
            if not mi or mi.get("status") != "untested" or mi.get("p") is None:
                continue
            gate = next((g for g in mi["gates"] if g["id"] == obs["resolves"]), None)
            if gate is None or gate["status"] != "untested" or gate.get("p") is None:
                continue
            g = gain(mi["p"], gate["p"])
            if g >= 0.0005 and (top is None or g > top[0]):      # a gain that prints as 0.000 is none
                top = (g, obs, mission, gate)
    if top is None:
        return None
    g, obs, mission, gate = top
    w = window(record)
    label = m.missions[mission]["label"]
    text = f"{obs['label']}, to settle \"{gate['label']}\" for {label[:1].lower() + label[1:]}."
    # The row behind the gate may have a source nobody looked at: the measurement may already exist there.
    # observe.unchecked carries them; the row and the entry name them, so the text does not.
    row = record.rows.get(ROW_OF_GATE.get(gate["id"], ""))
    unchecked = list(row.unchecked) if row is not None else []
    return {
        "best": obs["id"], "mission": mission, "gate": gate["id"], "gain": round(g, 3),
        "text": text, "needs": needs(m, obs["id"], w), "window": w, "tier": tier(w), "unchecked": unchecked,
        # the parts of the text as the summary and the list lay them out
        "label": obs["label"], "mission_label": label, "gate_label": gate["label"], "gate_p": gate["p"],
    }


def apply_one(record: ObjectRecord, d, m: Method) -> ObjectRecord:
    record.observe = best(record, m)
    return record


def apply(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Stage 4: the best next observation for each untested object."""
    m = m or method_mod.load()
    for r in records:
        apply_one(r, None, m)
    return records


def rank_key(observe: dict, key: str) -> tuple:
    """Sort key for one record's observe block (observe.toml [rank]): asteroids a telescope can be pointed at
    first, then those only a survey could recover, then those with no window; within each, the year the window
    opens, then the largest gain, then the earliest window, then the key. Takes the block as a dict, so the
    site generator can use it too."""
    w = observe.get("window") or {}
    kind = observe.get("tier") or tier(observe.get("window"))
    start = w.get("start") or "9999"
    return (TIERS.index(kind), start[:4], -observe["gain"], start, key)


def ranked(records: list[ObjectRecord]) -> list[ObjectRecord]:
    """The order of list/observe.html (observe.toml [rank])."""
    have = [r for r in records if r.observe]
    return sorted(have, key=lambda r: rank_key(r.observe, r.key))
