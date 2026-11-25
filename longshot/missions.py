"""Elimination by mission type: each gate pass, fail or untested, per method/v0_1/missions.toml.

    records = missions.apply(records)     # stage 3: fills record.missions

A gate passes or fails when a measurement decides it: the measured value clears
the preset by missions.toml [rules.decide].sigma times its stated error (or,
for a size with no stated error, by its no_range_factor). Otherwise it is
untested, with the share of the object's joint draws that pass, held between
1/n and 1 - 1/n so that it never reads as 0 or 1. A mission's probability is
the share of draws that pass every undecided gate at once; nothing is
multiplied across gates.

A gate's text says only what its row does not: why a measurement did not
decide, or which source was not checked. It is empty when the row says it all.

    record.missions[mission] = {status, p, gates: [{id, label, status, p, basis, text}]}

p is 1 for a pass, 0 for a fail, the bounded share of draws for untested, and
None when the object has no H (no draws). basis is "measured" when the status or the
share rests on this object's own measurement, "prior" when it rests on
brightness.
"""
from __future__ import annotations

from longshot import draws as draws_mod
from longshot import method as method_mod
from longshot import observe as observe_mod
from longshot import priors
from longshot.draws import Draws, Inputs, Measured, cap, spoken_list
from longshot.method import Method
from longshot.types import ObjectRecord

DECIDED_P = {"pass": 1.0, "fail": 0.0}


# --------------------------------------------------------------------------
# words

def figures(x: float, n: int = 2) -> str:
    """x to n significant figures, with thousands separators and no trailing zeros."""
    if x == 0:
        return "0"
    v = priors.sig(x, n)
    if abs(v) >= 100:
        return f"{v:,.0f}"
    return f"{v:.10f}".rstrip("0").rstrip(".")


def tonnes_words(t: float) -> str:
    """Tonnes to two figures; from a million, 'N million'; from a thousand million, 'N billion'."""
    if t >= 1e9:
        return f"{figures(t / 1e9)} billion"
    if t >= 1e6:
        return f"{figures(t / 1e6)} million"
    return figures(t)


def period_words(hours: float) -> str:
    """ladder.toml [format].period: hours from 2 hours, minutes from 2 minutes, else seconds; three figures."""
    if hours >= 2.0:
        return f"{figures(hours, 3)} hours"
    if hours * 60.0 >= 2.0:
        return f"{figures(hours * 60.0, 3)} minutes"
    return f"{figures(hours * 3600.0, 3)} seconds"


def _not_checked(record: ObjectRecord, row: str, what: str) -> str:
    """'Size not checked (SsODNet).' when a source for the row was not checked; else nothing: the row says the rest."""
    r = record.rows[row]
    return f"{cap(what)} not checked ({spoken_list(r.unchecked)})." if r.unchecked else ""


# --------------------------------------------------------------------------
# gates

def _compare(op: str, x: float, preset: float) -> bool:
    return x >= preset if op == ">=" else x <= preset


def _gate(g: dict, status: str, p, basis: str, text: str) -> dict:
    if status in DECIDED_P:
        p = DECIDED_P[status]
    elif p is not None:
        p = round(p, 4)
    return {"id": g["id"], "label": g["label"], "status": status, "p": p, "basis": basis, "text": text.strip()}


def bounded(p: float, n: int) -> float:
    """An untested share is never 0 or 1: with n draws it lies between 1/n and 1 - 1/n ([rules].gate)."""
    return round(min(max(p, 1.0 / n), 1.0 - 1.0 / n), 4)


def _within(x: Measured, k: float, line: str) -> str:
    """Why a measured value did not decide."""
    if x.ranged:
        return f"Within {k:g} sigma of {line}."
    return f"No error stated; within a factor of {x.factor:g} of {line}."


def _findable(g, record, inp: Inputs, d, m):
    if inp.occ is None:
        return _gate(g, "untested", None, "prior", "No orbit code on file."), None
    ok = _compare(g["op"], inp.occ, g["preset"])
    # The code and JPL's own pointing test are two tests (missions.toml, the gate's label_note).
    w = observe_mod.window(record)
    text = "JPL finds its position too uncertain to point at." if ok and w is not None and not w["pointable"] else ""
    return _gate(g, "pass" if ok else "fail", None, "measured", text), None


def _size(g, record, inp: Inputs, d: Draws | None, m):
    op, preset = g["op"], g["preset"]
    line = f"{figures(preset, 3)} m"
    k = m.missions["rules"]["decide"]["sigma"]
    if inp.size is not None:
        x = inp.size
        lo, hi = x.reach(k)
        lo_ok, hi_ok = _compare(op, lo, preset), _compare(op, hi, preset)
        if lo_ok and hi_ok:
            return _gate(g, "pass", None, "measured", ""), None
        if not lo_ok and not hi_ok:
            return _gate(g, "fail", None, "measured", ""), None
        text = _within(x, k, line)
        if d is None:
            return _gate(g, "untested", None, "measured", text), None
        ok = [_compare(op, v, preset) for v in d.d]
        return _gate(g, "untested", sum(ok) / d.n, "measured", text), ok

    parts = []
    if inp.size_rejected is not None:
        parts.append(draws_mod.rejected_size_sentence(inp, m))
    elif inp.size_bound is not None:
        b = inp.size_bound
        if b.kind == ("lower" if op == ">=" else "upper") and _compare(op, b.value, preset):
            return _gate(g, "pass", None, "measured", ""), None
        if b.kind == ("upper" if op == ">=" else "lower") and not _compare(op, b.value, preset):
            return _gate(g, "fail", None, "measured", ""), None
        parts.append("The limit on file does not decide.")
        if inp.size_bound_ignored:
            parts.append("It does not fit its brightness and is not applied.")
    else:
        parts.append(_not_checked(record, "size", "size"))
    if d is None:
        parts.append("No brightness on file, so no chance can be given.")
        return _gate(g, "untested", None, "prior", " ".join(x for x in parts if x)), None
    ok = [_compare(op, v, preset) for v in d.d]
    return _gate(g, "untested", sum(ok) / d.n, "prior", " ".join(x for x in parts if x)), ok


def _mass(g, record, inp: Inputs, d: Draws | None, m):
    """missions.toml [rules.mass]: decided only from a measured size at the two ends of density. A density on
    file narrows the draws, and so the chance; it does not decide the gate."""
    preset = g["preset"]
    k = m.missions["rules"]["decide"]["sigma"]
    rho_min, rho_max = priors.density_ends(m)
    if inp.size is not None:
        lo, hi = inp.size.reach(k)
        top = priors.mass_t(hi, rho_max)
        bottom = priors.mass_t(lo, rho_min)
        if top <= preset:
            return _gate(g, "pass", None, "measured",
                         f"At most {tonnes_words(top)} t: {figures(hi, 3)} m at {rho_max:,.0f} kg/m³, "
                         "the densest material allowed for."), None
        if bottom > preset:
            return _gate(g, "fail", None, "measured",
                         f"At least {tonnes_words(bottom)} t: {figures(lo, 3)} m at {rho_min:,.0f} kg/m³, "
                         "the lightest material allowed for."), None
    # The mass gate rests on the size row: when a source for it was not checked, the text says so.
    lead = _not_checked(record, "size", "size") if inp.size is None else ""
    if d is None:
        return _gate(g, "untested", None, "prior",
                     f"{lead} No brightness on file, so no chance can be given."), None
    ok = [v <= preset for v in d.mass]
    return _gate(g, "untested", sum(ok) / d.n, "measured" if inp.size is not None else "prior", lead), ok


def _spin(g, record, inp: Inputs, d: Draws | None, m):
    op, preset = g["op"], g["preset"]
    k = m.missions["rules"]["decide"]["sigma"]
    row = record.rows["spin"]
    if inp.period is not None:
        x = inp.period
        lo, hi = x.reach(k)
        lo_ok, hi_ok = _compare(op, lo, preset), _compare(op, hi, preset)
        if lo_ok and hi_ok:
            return _gate(g, "pass", None, "measured", ""), None
        if not lo_ok and not hi_ok:
            return _gate(g, "fail", None, "measured", ""), None
        text = _within(x, k, period_words(preset))
        if d is None or d.period is None:
            return _gate(g, "untested", None, "measured", text), None
        ok = [_compare(op, v, preset) for v in d.period]
        return _gate(g, "untested", sum(ok) / d.n, "measured", text), ok

    parts = []
    if inp.period_split is not None:
        # missions.toml [rules.conflict]
        parts.append(f"Sources disagree across {period_words(preset)}, so no period decides.")
    elif inp.period_bound is not None:
        b = inp.period_bound
        if b.kind == ("lower" if op == ">=" else "upper") and _compare(op, b.value, preset):
            return _gate(g, "pass", None, "measured", ""), None
        if b.kind == ("upper" if op == ">=" else "lower") and not _compare(op, b.value, preset):
            return _gate(g, "fail", None, "measured", ""), None
        parts.append("The limit on file does not decide.")
    elif inp.period_unreliable is not None:
        parts.append("The period on file is graded unreliable, so it does not decide.")
        parts.append(_not_checked(record, "spin", "period"))
    else:
        parts.append(_not_checked(record, "spin", "period"))
    text = " ".join(x for x in parts if x)
    if d is None:
        return _gate(g, "untested", None, "prior", f"{text} No brightness on file, so no chance can be given."), None
    # The spin prior is a category, not a period: the gate must sit on a category edge.
    edge = sum(1 for th in m.priors["spin"]["thresholds_h"] if preset >= th)
    if preset not in m.priors["spin"]["thresholds_h"]:
        raise method_mod.MethodError(
            f"missions.toml: a spin preset of {preset} h is not a threshold of priors.toml [spin]")
    ok = [(c >= edge) if op == ">=" else (c < edge) for c in d.spin]
    return _gate(g, "untested", sum(ok) / d.n, "prior", text), ok


GATES = {"occ": _findable, "diameter_m": _size, "mass_t": _mass, "period_h": _spin}


def evaluate(record: ObjectRecord, d: Draws | None, m: Method) -> dict:
    """record.missions for one object."""
    inp = d.inputs if d is not None else draws_mod.inputs(record, m)
    out = {}
    for mission in m.missions["order"]:
        if record.gone:
            # missions.toml [rules.gone]: the body no longer exists, and its orbit gate says so
            g = next(g for g in m.missions[mission]["gates"] if g["quantity"] == "occ")
            out[mission] = {"status": "fail", "p": 0.0,
                            "gates": [_gate(g, "fail", None, "measured", record.gone["text"])]}
            continue
        gates, undecided = [], []
        for g in m.missions[mission]["gates"]:
            try:
                fn = GATES[g["quantity"]]
            except KeyError:
                raise method_mod.MethodError(f"missions.toml: no rule for a gate on {g['quantity']!r}") from None
            gate, ok = fn(g, record, inp, d, m)
            if gate["status"] == "untested":
                undecided.append(ok)
                if gate["p"] is not None:
                    gate["p"] = bounded(gate["p"], d.n)
            gates.append(gate)
        statuses = [g["status"] for g in gates]
        if "fail" in statuses:
            status, p = "fail", 0.0
        elif all(s == "pass" for s in statuses):
            status, p = "pass", 1.0
        elif d is None or any(ok is None for ok in undecided):
            status, p = "untested", None
        else:
            status = "untested"
            p = bounded(sum(1 for i in range(d.n) if all(ok[i] for ok in undecided)) / d.n, d.n)
        out[mission] = {"status": status, "p": p, "gates": gates}
    return out


def apply_one(record: ObjectRecord, d: Draws | None, m: Method) -> ObjectRecord:
    record.missions = evaluate(record, d, m)
    return record


def apply(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Stage 3: elimination by mission type."""
    m = m or method_mod.load()
    for r in records:
        apply_one(r, draws_mod.for_record(r, m), m)
    return records
