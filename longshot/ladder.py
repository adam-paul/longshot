"""The difficulty ladder: five rungs per method/v0_1/ladder.toml.

    records = ladder.apply(records)       # stage 6: fills record.ladder (needs summary, missions and value)

    record.ladder = [{rung, status (measured|prior|unknown), text}] x 5, in longshot.types.LADDER order
    the brought_back rung also has parts: [{id, label, word, text}] for grams, then kilograms or tonnes

Every sentence is a template from the method file, filled from the record.
The sentences the file does not give, for an object with no size or no price
tag, are in NO_INPUT below.

A rung says what the rows do not (DESIGN.md section 5): what the spin means for
loose material, what the answer rests on, what has flown. It does not print
again the orbit code's window, the trip, the size and mass, the period, or the
price tag's sentences.
"""
from __future__ import annotations

import math

from longshot import draws as draws_mod
from longshot import method as method_mod
from longshot import observe as observe_mod
from longshot.draws import Inputs, spoken_list
from longshot.method import Method
from longshot.missions import figures
from longshot.types import LADDER, ObjectRecord

# ladder.toml has no sentence for these cases; they are the smallest that say what is missing.
NO_INPUT = {
    "spin": "No size or spin share: JPL lists no brightness for it.",
    "value": "No estimate: JPL lists no brightness for it.",
    "grams": "Grams: no size on file to set against what has flown.",
}


def ratio_words(x: float) -> str:
    """One figure; two when the first digit is 1 or 2 (ladder.toml [format].ratio)."""
    if x <= 0:
        return "0"
    e = math.floor(math.log10(x))
    lead = int(x / 10 ** e + 1e-12)
    return figures(x, 2 if lead < 3 else 1)


def count_words(p: float) -> str:
    """A whole number of 100, halves rounded up."""
    return str(math.floor(100 * p + 0.5))


def _names(record: ObjectRecord) -> set[str]:
    out = {record.designation, record.name, str(record.number) if record.number else None, *record.aliases}
    return {str(x) for x in out if x}


def fact_for(record: ObjectRecord, m: Method, kind: str) -> dict | None:
    """The fact of this kind (sample_return, in_position) whose target is this asteroid."""
    names = _names(record)
    for f in m.ladder["fact"]:
        if f.get("kind") == kind and names & set(f.get("objects", [])):
            return f
    return None


def size_range(record: ObjectRecord, inp: Inputs) -> tuple[float, float] | None:
    """d_lo and d_hi: the 5th and 95th of the draws, which follow a measured size and its stated error."""
    q = (record.summary or {}).get("size_m") or {}
    if draws_mod.is_num(q.get("q05")) and draws_mod.is_num(q.get("q95")):
        return q["q05"], q["q95"]
    return None


def _state(states, **want) -> dict:
    for s in states:
        if all(s.get(k) == v for k, v in want.items()):
            return s
    raise method_mod.MethodError(f"ladder.toml: no state with {want}")


def _by_id(items, item_id: str) -> dict:
    return _state(items, id=item_id)


# --------------------------------------------------------------------------
# the rungs

def found_again(record, inp: Inputs, m: Method) -> dict:
    rung = m.ladder["rung"]["found_again"]
    if record.gone:
        state = _state(rung["state"], gate="gone")
        return {"rung": "found_again", "status": state["status"], "text": state["text"].format(gone=record.gone["text"])}
    # The orbit gate is the same in every mission preset; the rung reads it from the first.
    gate = next(g for g in m.missions[m.missions["order"][0]]["gates"] if g["id"] == "findable")
    if inp.occ is None:
        status = "untested"
    else:
        ok = inp.occ <= gate["preset"] if gate["op"] == "<=" else inp.occ >= gate["preset"]
        status = "pass" if ok else "fail"
    state = _state(rung["state"], gate=status)
    parts = [state["text"].format(occ=inp.occ)]
    # The window is in the tracking row. A sentence follows only when JPL's own test says the code is not enough.
    w = observe_mod.window(record)
    suffix = _state(rung["suffix"], window=observe_mod.tier(w))
    if suffix["text"] and status != "untested":
        parts.append(suffix["text"])
    return {"rung": "found_again", "status": state["status"], "text": " ".join(parts)}


def reached(record, inp: Inputs, m: Method) -> dict:
    rung = m.ladder["rung"]["reached"]
    row = record.rows["reach"]
    dv = next((f for f in row.facts if (f.label or "").casefold().startswith("delta-v") and f.unit == "km/s"
               and draws_mod.is_num(f.value) and f.kind == "value"), None)
    if dv is not None:
        state = _by_id(rung["state"], "round_trip")
        parts = [state["text"].format(dv=f"{dv.value:g}")]
    else:
        state = _by_id(rung["state"], "no_round_trip")
        parts = [state["text"]]
    rng = size_range(record, inp)
    small = _by_id(rung["suffix"], "small_bodies_reached")
    if rng is not None and rng[1] < m.ladder["thresholds"]["small_m"] and fact_for(record, m, "in_position") is None \
            and not record.gone:
        parts.append(small["text"])
    return {"rung": "reached", "status": state["status"], "text": " ".join(parts)}


def spin_class(inp: Inputs, m: Method) -> str:
    """ladder.toml [classes.spin]."""
    if inp.period is None:
        return "not_measured"
    th = m.ladder["thresholds"]
    if inp.period.value >= th["sampled_min_period_h"]:
        return "slow"
    if inp.period.value * 60.0 >= th["very_fast_period_min"]:
        return "faster"
    return "very_fast"


def size_class(rng: tuple[float, float], m: Method) -> str:
    """ladder.toml [classes.size]."""
    th = m.ladder["thresholds"]
    lo, hi = rng
    if lo >= th["sampled_min_m"]:
        return "sampled"
    if hi >= th["sampled_min_m"]:
        return "may_be_sampled"
    if hi >= th["touched_min_m"]:
        return "below_sampled"
    return "untouched"


def workable(record, inp: Inputs, m: Method) -> dict:
    rung = m.ladder["rung"]["workable"]
    size_row, spin_row = record.rows["size"], record.rows["spin"]
    summary = record.summary or {}
    n_fast = summary.get("p_fast_2_2h")
    limits = m.ladder["spin_limit"]
    size_known = size_range(record, inp) is not None
    if inp.period is not None:
        p = inp.period.value
        if p >= limits["light_rock_limit_h"]:
            sid = "slow"
        elif p >= limits["dense_rock_limit_h"]:
            sid = "near_limit"
        else:
            sid = "fast"
        state = _by_id(rung["state"], sid)
        text = state["text"].format(
            r_lo=ratio_words((limits["dense_rock_limit_h"] / p) ** 2),
            r_hi=ratio_words((limits["light_rock_limit_h"] / p) ** 2))
        if spin_row.conflicts:
            text += " " + _by_id(rung["suffix"], "sources_disagree")["text"]
        spin_measured = True
    else:
        spin_measured = False
        slots = {}
        if inp.period_split is not None:
            state = _by_id(rung["state"], "spin_conflict")
            slots = {"conflict": inp.period_split}
        elif inp.period_unreliable is not None:
            state = _by_id(rung["state"], "period_unreliable")
        elif inp.period_bound is not None:
            state = _by_id(rung["state"], "spin_limit_only")
        elif spin_row.unchecked or spin_row.state == "unchecked":
            state = _by_id(rung["state"], "spin_not_checked")
            slots = {"sources": spoken_list(spin_row.unchecked) or "a source"}
        else:
            state = _by_id(rung["state"], "spin_not_measured")
        if draws_mod.is_num(n_fast):
            text = state["text"].format(n_fast=count_words(n_fast), **slots)
        else:
            # no brightness, so no share: only what comes before "Of 100 like it", or the plain statement
            text = state["text"].split("Of 100 like it")[0].strip().format(**slots) or NO_INPUT["spin"]

    if size_row.state == "measured" and inp.size is not None and spin_measured:
        status = "measured"
    elif not size_known and not spin_measured and not draws_mod.is_num(n_fast):
        status = "unknown"
    else:
        status = "prior"
    return {"rung": "workable", "status": status, "text": text}


def anything_in_it(record, inp: Inputs, m: Method) -> dict:
    rung = m.ladder["rung"]["anything_in_it"]
    if record.gone:
        state = _by_id(rung["state"], "gone")
        return {"rung": "anything_in_it", "status": state["status"], "text": state["text"]}
    sample = fact_for(record, m, "sample_return")
    if sample is not None:
        state = _by_id(rung["state"], "sampled")
        text = (state["text"].format(measured_in_sample=sample["measured_in_sample"])
                if sample.get("measured_in_sample") else state["text_no_analysis"])
        return {"rung": "anything_in_it", "status": state["status"], "text": text}
    if not (record.value or {}).get("statements"):
        return {"rung": "anything_in_it", "status": "unknown", "text": NO_INPUT["value"]}
    surface = record.rows["surface"]
    basis = "from_size" if record.rows["size"].state in ("measured", "limit") else "from_brightness"
    if surface.state in ("measured", "limit"):
        state = _by_id(rung["state"], "from_class")
    elif surface.unchecked:
        state = _by_id(rung["state"], basis + "_not_checked")
    else:
        state = _by_id(rung["state"], basis)
    return {"rung": "anything_in_it", "status": state["status"],
            "text": state["text"].format(sources=spoken_list(surface.unchecked))}


def brought_back(record, inp: Inputs, m: Method) -> dict:
    rung = m.ladder["rung"]["brought_back"]
    states = rung["state"]
    if record.gone:
        return {"rung": "brought_back", "status": "measured", "text": _state(states, special="gone")["text"]}
    more_suffix = _by_id(rung["suffix"], "more_than_grams")
    more, more_word = more_suffix["text"], more_suffix.get("word")
    rng = size_range(record, inp)
    spin = spin_class(inp, m)
    measured = record.rows["size"].state == "measured" and inp.size is not None and spin != "not_measured"
    spin_row = record.rows["spin"]
    # the sources not checked for spin, when nothing on file gives a period at all
    unchecked = spoken_list(spin_row.unchecked) if spin == "not_measured" and spin_row.unchecked else ""

    sample = fact_for(record, m, "sample_return")
    position = fact_for(record, m, "in_position")
    parts = []
    state = None
    if sample is not None:
        state = _state(states, special="sample_return_target")
        parts.append(state["text"].format(returned=sample["returned"], mission=sample["mission"],
                                          return_year=sample["return_year"], cost=sample["cost"]))
    elif position is not None:
        state = _state(states, special="in_position_target")
        parts.append(state["text"])
    elif rng is None:
        return {"rung": "brought_back", "status": "unknown", "text": f"{NO_INPUT['grams']} {more}",
                "parts": _amounts([NO_INPUT["grams"]], None, more, more_word)}
    else:
        size = size_class(rng, m)
        state = next((s for s in states if size in s.get("size", ()) and spin in s.get("spin", ())), None)
        if state is None:
            raise method_mod.MethodError(f"ladder.toml: no brought_back state for size {size}, spin {spin}")
        text = state["text"]
        if unchecked and "not_checked_sentence" in state:
            # a source for the spin row was not checked: the sentence may not say "not measured"
            if state["not_measured_sentence"] not in text:
                raise method_mod.MethodError(f"ladder.toml: state {state['id']} lacks its own not_measured_sentence")
            text = text.replace(state["not_measured_sentence"], state["not_checked_sentence"].format(sources=unchecked))
        parts.append(text)
    decides = _by_id(rung["suffix"], "spin_decides")
    if state["id"] in decides["after"] and spin in decides["spin"]:
        parts.append(decides["text_conflict"] if inp.period_split is not None
                     else decides["text_not_checked"].format(sources=unchecked) if unchecked else decides["text"])
    return {"rung": "brought_back", "status": "measured" if measured else "prior", "text": " ".join(parts + [more]),
            "parts": _amounts(parts, state.get("word"), more, more_word)}


def _amounts(grams: list[str], grams_word: str | None, more: str, more_word: str | None) -> list[dict]:
    """The rung's two amounts, as the entry tabulates them: [{id, label, word, text}] for grams, then for
    kilograms or tonnes. label is the sentence's own lead ("Grams"), text the rest; word is the state's id in
    ladder.toml [rung.brought_back.words] (done, not_yet_attempted, proposed), or None where nothing is known."""
    out = []
    for pid, text, word in (("grams", " ".join(grams), grams_word), ("more_than_grams", more, more_word)):
        label, sep, rest = text.partition(": ")
        out.append({"id": pid, "label": label if sep else "", "word": word, "text": rest if sep else text})
    return out


RUNGS = {"found_again": found_again, "reached": reached, "workable": workable,
         "anything_in_it": anything_in_it, "brought_back": brought_back}


def build(record: ObjectRecord, inp: Inputs, m: Method) -> list[dict]:
    order = tuple(m.ladder["meta"]["order"])
    if order != LADDER:
        raise method_mod.MethodError(f"ladder.toml meta.order {order} is not longshot.types.LADDER {LADDER}")
    if record.gone:
        # nothing is left to reach, work on or bring back: the first rung says what happened, the rest say so
        gone = _by_id(m.ladder["rung"]["anything_in_it"]["state"], "gone")
        return [found_again(record, inp, m)] + [{"rung": r, "status": gone["status"], "text": gone["text"]}
                                                 for r in order[1:]]
    return [RUNGS[r](record, inp, m) for r in order]


def apply_one(record: ObjectRecord, d, m: Method) -> ObjectRecord:
    inp = d.inputs if d is not None else draws_mod.inputs(record, m)
    record.ladder = build(record, inp, m)
    return record


def apply(records: list[ObjectRecord], m: Method | None = None) -> list[ObjectRecord]:
    """Stage 6: the five rungs. Reads the rows, record.summary, record.missions and record.value."""
    m = m or method_mod.load()
    for r in records:
        apply_one(r, draws_mod.for_record(r, m), m)
    return records
