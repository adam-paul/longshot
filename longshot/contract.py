"""The record shape of docs/mvp.md section 4, checked between the model and the site.

    contract.check(records)             # raises ContractError naming what is missing
    contract.check_predictions(preds)

The site generator reads records leniently so a hand-made sample renders. A real
build must not rely on that: a field the generator would quietly skip is an error
here, before any page is written.
"""
from __future__ import annotations

import re

from longshot import config
from longshot.types import LADDER, MISSIONS, ROWS, STATES, ObjectRecord

KEY_RE = re.compile(r"^[a-z][a-z0-9]{5}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FACT_KINDS = ("value", "upper", "lower")
# No middle figure of kilograms, dollars or tonnes may be written anywhere in the value block (DESIGN.md section 7).
CENTRAL = ("mean", "median", "expected", "q50")
QUANTILES = ("q05", "q25", "q50", "q75", "q95")
SPIN_SHARES = ("p_fast_2_2h", "p_under_1h", "p_under_10min")
CLASSES = ("S", "C", "X", "other")
STATUSES = ("pass", "fail", "untested")
PRIOR_ROWS = ("size", "spin", "surface")          # the rows the method has a prior for
GATE_KEYS = ("id", "label", "status", "p", "basis", "text")
WINDOW_KEYS = ("start", "end", "peak_mag", "pointable", "as_of")
OBSERVE_KEYS = ("best", "mission", "gate", "gain", "text", "needs", "window", "tier", "unchecked",
                "label", "mission_label", "gate_label", "gate_p")
PERIOD_KEYS = ("value", "unit", "lo", "hi", "kind", "source", "ref", "quality", "rests_on", "conflict")
MASS_BASES = ("density", "class")
CELLS = {"metal": ("none", "none_or_some", "some", "iron_rich_or_not", "iron_rich"),
         "water": ("none", "none_or_some", "some")}
TIERS = ("pointable", "survey_only", "none")      # what kind of window JPL lists (longshot/observe.py)
PREDICTION_KEYS = ("id", "statement", "p", "frozen", "settles", "settle_from", "settle_by", "settle_note", "key",
                   "designation", "outcome")
MAX_LISTED = 12


class ContractError(Exception):
    pass


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def _prob(x) -> bool:
    return _num(x) and 0.0 <= x <= 1.0


def _ordered(d, keys=QUANTILES, positive=True) -> bool:
    if not isinstance(d, dict) or not all(_num(d.get(k)) for k in keys):
        return False
    values = [d[k] for k in keys]
    return values == sorted(values) and (not positive or values[0] > 0)


def central_keys(node, path: str = "value") -> list[str]:
    """Every key anywhere under the value block whose name holds a central figure's name."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}"
            if any(word in str(k).lower() for word in CENTRAL):
                out.append(here)
            out += central_keys(v, here)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += central_keys(v, f"{path}[{i}]")
    return out


def has_h(record: ObjectRecord) -> bool:
    return any(f.label == "H" and _num(f.value) for f in record.rows["size"].facts)


def period_problem(record: ObjectRecord, period, source_ids: set[str]) -> str:
    """What is wrong with summary.period, or ''. It is null unless the spin row is measured or a limit."""
    state = record.rows["spin"].state
    if period == "missing":
        return "is missing"
    if period is None:
        return "is null for a spin row that is measured" if state == "measured" else ""
    if not isinstance(period, dict) or [k for k in PERIOD_KEYS if k not in period]:
        return "lacks a key"
    if state not in ("measured", "limit"):
        return f"is given for a spin row that is {state}"
    if period["rests_on"] not in source_ids:
        return f"rests on {period['rests_on']!r}, which is not a source"
    if period["value"] is not None and not (_num(period["value"]) and period["value"] > 0
                                             and period["source"] in source_ids):
        return "has a value that is not a positive number from a source"
    return ""


def table_problems(table) -> list[str]:
    """value.table: for metal and water, cells adding to 100 in their order, and rows with a label."""
    if not isinstance(table, dict) or not isinstance(table.get("notes"), list):
        return ["is not {metal, water, notes}"]
    out = []
    for part, order in CELLS.items():
        block = table.get(part)
        if not isinstance(block, dict) or not isinstance(block.get("cells"), list) or not block.get("rows"):
            out.append(f"{part} has no cells or rows")
            continue
        ids = [c.get("id") for c in block["cells"]]
        if ids != [i for i in order if i in ids] or sum(c.get("n", 0) for c in block["cells"]) != 100 \
                or any(not (isinstance(c.get("n"), int) and c["n"] > 0 and c.get("label")) for c in block["cells"]):
            out.append(f"{part} cells are out of order, empty, or do not add to 100")
        if any(not r.get("label") or not any(r.get(k) for k in ("of100", "kg", "usd", "tonnes")) for r in block["rows"]):
            out.append(f"{part} has a row with no label or no figure")
    return out


def problems(record: ObjectRecord, source_ids: set[str]) -> list[str]:
    out: list[str] = []
    bad = out.append
    if not KEY_RE.match(record.key or ""):
        bad(f"key {record.key!r} is not a minted key")
    if not record.designation:
        bad("no designation")
    if record.data_date != config.DATA_DATE:
        bad(f"data_date {record.data_date!r}, expected {config.DATA_DATE}")
    if record.method != config.METHOD:
        bad(f"method {record.method!r}, expected {config.METHOD}")
    if "reachable" not in record.populations:
        bad("not in the reachable population")

    if set(record.rows) != set(ROWS):
        bad(f"rows are {sorted(record.rows)}")
        return out
    for name in ROWS:
        row = record.rows[name]
        if row.state not in STATES:
            bad(f"{name}: state {row.state!r}")
        if row.state == "prior" and row.unchecked:
            bad(f"{name}: 'not measured' while {row.unchecked} is not checked")
        if row.state == "unchecked" and not row.unchecked:
            bad(f"{name}: 'not checked' names no source")
        if row.state in ("measured", "limit") and not row.facts:
            bad(f"{name}: {row.state} with no fact")
        elif row.state == "measured" and not (row.facts[0].used and row.facts[0].kind == "value"):
            bad(f"{name}: measured, but its first fact is not a value in use")
        elif row.state == "limit" and not (row.facts[0].used and row.facts[0].kind in ("upper", "lower")):
            bad(f"{name}: a limit, but its first fact is not a bound in use")
        for f in row.facts:
            if not f.label:
                bad(f"{name}: a fact has no label")
            if f.source not in source_ids:
                bad(f"{name}: fact {f.label!r} cites {f.source!r}, which is not a source")
            if f.kind not in FACT_KINDS:
                bad(f"{name}: fact {f.label!r} has kind {f.kind!r}")
            for end in (f.lo, f.hi):
                if end is not None and not _num(end):
                    bad(f"{name}: fact {f.label!r} has a range end that is not a finite number")
            if isinstance(f.value, float) and not _num(f.value):
                bad(f"{name}: fact {f.label!r} has a value that is not a finite number")
        for s in row.unchecked:
            if s not in source_ids:
                bad(f"{name}: unchecked source {s!r} is not a source")
    if not any(f.label == "delta-v" and f.unit == "km/s" and _num(f.value) and f.value > 0
               for f in record.rows["reach"].facts):
        bad("reach: no delta-v in km/s")
    for s in record.sources:
        if s not in source_ids:
            bad(f"sources lists {s!r}, which is not a source")

    sized = has_h(record)
    gone = bool(record.gone)
    summary, value = record.summary, record.value
    if gone:
        if not (record.gone.get("date") and record.gone.get("text")):
            bad("gone: no date or text")
        if value or record.observe is not None:
            bad("gone, yet a price tag or an observation is given")
        if any(m.get("status") != "fail" for m in record.missions.values()):
            bad("gone, yet a mission is not a fail")
        if any(f.label.startswith("window") or f.label == "next window" for f in record.rows["tracking"].facts):
            bad("gone, yet the tracking row lists a window")
    if sized:
        for name in PRIOR_ROWS:
            row = record.rows[name]
            if row.state in ("prior", "unchecked") and not isinstance(row.prior, dict):
                bad(f"{name}: not measured, and no prior")
        size_prior = record.rows["size"].prior
        if size_prior is not None and not (_ordered(size_prior) and size_prior.get("unit") == "m"
                                           and size_prior.get("basis")):
            bad("size: prior is not {q05..q95, unit: 'm', basis}")
        spin_prior = record.rows["spin"].prior
        if spin_prior is not None and not (all(_prob(spin_prior.get(k)) for k in SPIN_SHARES)
                                           and spin_prior.get("basis")):
            bad("spin: prior is not {p_fast_2_2h, p_under_1h, p_under_10min, basis}")
        surface_prior = record.rows["surface"].prior
        if surface_prior is not None and not (
                _ordered(surface_prior) and isinstance(surface_prior.get("shares"), dict)
                and all(_prob(surface_prior["shares"].get(c)) for c in CLASSES) and surface_prior.get("basis")):
            bad("surface: prior is not {q05..q95, shares{S,C,X,other}, basis}")
        if not _ordered(summary.get("size_m")):
            bad("summary.size_m is not five ordered quantiles above zero")
        if not _ordered(summary.get("mass_t")):
            bad("summary.mass_t is not five ordered quantiles above zero")
        for k in SPIN_SHARES:
            if not _prob(summary.get(k)):
                bad(f"summary.{k} is not a probability")
        if not (isinstance(summary.get("class"), dict) and all(_prob(summary["class"].get(c)) for c in CLASSES)):
            bad("summary.class is not {S, C, X, other}")
        if not _ordered(summary.get("reflectivity")):
            bad("summary.reflectivity is not five ordered quantiles above zero")
        if "size_open_m" in summary and not _ordered(summary["size_open_m"], ("q05", "q50", "q95")):
            bad("summary.size_open_m is not three ordered quantiles above zero")
        if summary.get("mass_basis") not in MASS_BASES:
            bad(f"summary.mass_basis is {summary.get('mass_basis')!r}")
        bad_period = period_problem(record, summary.get("period", "missing"), source_ids)
        if bad_period:
            bad(f"summary.period {bad_period}")
    if sized and not gone:
        metal, water = value.get("metal"), value.get("water")
        if not (isinstance(metal, dict) and _prob(metal.get("p_nothing"))
                and _ordered(metal.get("usd"), ("q05", "q25", "q75", "q95"), positive=False)
                and _ordered(metal.get("kg"), ("q05", "q95"), positive=False)):
            bad("value.metal is not {p_nothing, usd{q05,q25,q75,q95}, kg{q05,q95}}")
        if not (isinstance(water, dict) and _prob(water.get("p_nothing"))):
            bad("value.water has no p_nothing")
        if not value.get("basis"):
            bad("value.basis is empty")
        statements = value.get("statements")
        if not (isinstance(statements, list) and statements and all(isinstance(s, str) and s for s in statements)):
            bad("value.statements is empty")
        for where in central_keys(value):
            bad(f"value carries a central figure ({where})")
        if "sample" not in value:
            for text in table_problems(value.get("table")):
                bad(f"value.table {text}")
        elif "table" in value:
            bad("value.table is given where a sample stands in for the class odds")
    elif not sized:
        if summary or value:
            bad("no H on file, yet summary or value is filled")

    if set(record.missions) != set(MISSIONS):
        bad(f"missions are {sorted(record.missions)}")
    for name, mission in record.missions.items():
        if mission.get("status") not in STATUSES:
            bad(f"missions.{name}.status is {mission.get('status')!r}")
        p = mission.get("p")
        if not (_prob(p) or (p is None and not sized)):
            bad(f"missions.{name}.p is {p!r}")
        gates = mission.get("gates")
        if not (isinstance(gates, list) and gates):
            bad(f"missions.{name} has no gates")
            continue
        for g in gates:
            missing = [k for k in GATE_KEYS if k not in g]
            if missing:
                bad(f"missions.{name} gate {g.get('id')!r} lacks {missing}")
            elif g["status"] not in STATUSES or g["basis"] not in ("measured", "prior") or not g["label"] \
                    or not isinstance(g["text"], str):
                bad(f"missions.{name} gate {g['id']!r} is malformed")
            elif not (_prob(g["p"]) or (g["p"] is None and g["status"] == "untested")):
                bad(f"missions.{name} gate {g['id']!r} holds p = {g['p']!r}")
            elif (g["status"] == "pass" and g["p"] != 1) or (g["status"] == "fail" and g["p"] != 0) \
                    or (g["status"] == "untested" and g["p"] in (0, 1)):
                # an untested chance is never stored as 0 or 1 (missions.toml [rules].gate)
                bad(f"missions.{name} gate {g['id']!r} is {g['status']} with p = {g['p']!r}")
        if mission.get("status") == "untested" and p in (0, 1):
            bad(f"missions.{name} is untested with p = {p!r}")

    o = record.observe
    if o is not None:
        missing = [k for k in OBSERVE_KEYS if k not in o]
        if missing:
            bad(f"observe lacks {missing}")
        else:
            if not (_num(o["gain"]) and o["gain"] > 0 and o["text"] and o["needs"]):
                bad("observe has no gain, text or needs")
            if o["tier"] not in TIERS or not isinstance(o["unchecked"], list):
                bad(f"observe.tier is {o['tier']!r}, or observe.unchecked is not a list")
            for s in o["unchecked"] if isinstance(o["unchecked"], list) else ():
                if s not in source_ids:
                    bad(f"observe.unchecked names {s!r}, which is not a source")
            if not (o["label"] and o["mission_label"] and o["gate_label"] and _prob(o["gate_p"])):
                bad("observe has no label, mission_label, gate_label or gate_p")
            w = o["window"]
            if w is not None and [k for k in WINDOW_KEYS if k not in w]:
                bad(f"observe.window lacks {[k for k in WINDOW_KEYS if k not in w]}")
            elif w is not None and not all(isinstance(w[k], str) and ISO_DATE.match(w[k]) for k in ("start", "end", "as_of")):
                bad("observe.window has a date that is not an ISO date")

    rungs = [r.get("rung") for r in record.ladder]
    if tuple(rungs) != LADDER:
        bad(f"ladder rungs are {rungs}")
    for r in record.ladder:
        if r.get("status") not in ("measured", "prior", "unknown") or not r.get("text"):
            bad(f"ladder rung {r.get('rung')!r} has no status or text")
    return out


def check(records: list[ObjectRecord], source_ids: set[str] | None = None) -> None:
    """Raise ContractError if any record departs from the shape the site is built from."""
    if source_ids is None:
        from longshot import sources
        source_ids = set(sources.load())
    found, seen = [], set()
    for r in records:
        if r.key in seen:
            found.append(f"{r.designation}: key {r.key} is used twice")
        seen.add(r.key)
        found += [f"{r.designation} ({r.key}): {p}" for p in problems(r, source_ids)]
    if found:
        more = f"\n  and {len(found) - MAX_LISTED} more" if len(found) > MAX_LISTED else ""
        raise ContractError(f"{len(found)} departures from docs/mvp.md section 4:\n  "
                            + "\n  ".join(found[:MAX_LISTED]) + more)


def check_predictions(predictions: list[dict]) -> None:
    found, seen = [], set()
    for p in predictions:
        missing = [k for k in PREDICTION_KEYS if k not in p]
        if missing:
            found.append(f"prediction {p.get('id')!r} lacks {missing}")
            continue
        if not p["id"] or p["id"] in seen:
            found.append(f"prediction id {p['id']!r} is empty or repeated")
        seen.add(p["id"])
        if not p["statement"] or not p["settles"]:
            found.append(f"prediction {p['id']!r} has no statement or nothing that settles it")
        if p["p"] is not None and not _prob(p["p"]):
            found.append(f"prediction {p['id']!r} holds p = {p['p']!r}")
    if found:
        raise ContractError(f"{len(found)} malformed predictions:\n  " + "\n  ".join(found[:MAX_LISTED]))
