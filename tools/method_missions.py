"""Check the mission presets in method/v0_1/missions.toml against the targets companies have named.

It reads the pipeline's own records: the ledger built from the data on disk and the model run on it, so the
check in missions.toml and the entry pages cannot drift apart. For each named object it prints what the entry
would say: the status and chance of each gate, the size, period and class the row rests on, and the same
verdict at the two ends of each size and mass preset's range. Nothing here decides anything itself.

tools/method_check.py recomputes the untested chances by plain random draws, with no code shared with the
pipeline or with this script.

The research snapshot of SsODNet cards is used alone, so the result does not move while cards are fetched.

Usage: uv run python -I tools/method_missions.py           print and write method/v0_1/derivation/missions.txt
       uv run python -I tools/method_missions.py --check   exit 1 if missions.toml records a different result
"""
import dataclasses
import math
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from method_lib import Report, config, fl, load_nhats  # noqa: E402

from longshot import draws, ids, ingest, ledger, method, missions, model, priors  # noqa: E402
from longshot.ingest import ssodnet  # noqa: E402

P_TOLERANCE = 0.005          # a recorded chance may differ from the derived one by this much


def build_records():
    """The ledger for the whole list, from files that do not change: the research snapshot of cards alone."""
    nowhere = config.ROOT / "tests" / "_not_a_folder"
    ingest.reset()
    with mock.patch.object(ssodnet, "LIVE_CARDS", nowhere / "cards"), \
            mock.patch.object(ssodnet, "JOURNAL", nowhere / "journal.jsonl"):
        try:
            return ledger.build(write_file=False)
        finally:
            ingest.reset()


def with_preset(m, mission, gate_id, value):
    """The method with one gate's preset changed, for the ends of its range."""
    mis = dict(m.missions)
    mis[mission] = dict(mis[mission], gates=[dict(g, preset=value) if g["id"] == gate_id else g
                                               for g in mis[mission]["gates"]])
    return dataclasses.replace(m, missions=mis)


def verdict(record, m, mission):
    d = draws.for_record(record, m)
    got = missions.evaluate(record, d, m)[mission]
    return {"status": got["status"], "p": got["p"],
            "gates": {g["id"]: (g["status"], g["p"], g["text"]) for g in got["gates"]}}


def facts(record, m):
    """What the entry's rows rest on, in a few words each."""
    inp = draws.inputs(record, m)

    def src(f):
        ref = (f.ref or "").split(";")[0].split(" (")[0].strip()
        return f"{draws.spoken(f.source)}, {ref}" if ref and f.source in ("ssodnet", "curated") else draws.spoken(f.source)

    out = {"h": inp.h, "h_sigma": round(inp.h_sigma, 3) if inp.h_sigma_stated else None, "occ": inp.occ,
           "dv": next(f.value for f in record.rows["reach"].facts if f.label == "delta-v"),
           "size": None, "size_rejected": inp.size_rejected is not None, "period": None, "cls": inp.cls,
           "cls_error": inp.cls_error, "density": inp.density.value if inp.density else None}
    if inp.size is not None:
        x = inp.size
        out["size"] = (x.value, x.lo, x.hi)
        out["size_words"] = (f"{x.value:g} m ({x.lo:g} to {x.hi:g}, one sigma), {src(x.fact)}" if x.ranged
                             else f"{x.value:g} m, no error stated, {src(x.fact)}")
    if inp.period is not None:
        f = inp.period.fact
        shown = f
        grade = f"U {shown.quality}" if draws.grade_digit(shown.quality) is not None else "no grade on file"
        out["period"] = inp.period.value
        out["period_words"] = f"{shown.value:g} h, {grade}, {src(shown)}"
    elif inp.period_unreliable is not None:
        f = inp.period_unreliable
        out["period_words"] = f"{f.value:g} h on file, graded unreliable (U {f.quality}, {src(f)}); it does not decide"
    if inp.cls_fact is not None:
        out["cls_words"] = (f"{inp.cls_fact.value} ({inp.cls_fact.quality}, {src(inp.cls_fact)}); "
                            f"wrong side of S/Q in {inp.cls_error:g} of draws")
    return out


def run(records=None):
    """(method, reachable list, [(mission, named entry, record, facts, verdict, verdicts at the range ends)])."""
    m = method.load()
    nh = load_nhats()
    index = ids.load()
    records = records if records is not None else build_records()
    by_pdes = {index.identity(r.key).pdes: r for r in records}
    out = []
    for mission in m.missions["order"]:
        for n in m.missions[mission]["named"]:
            r = model.run_one(by_pdes[n["pdes"]], m)
            ev = verdict(r, m, mission)
            ends = {}
            for g in m.missions[mission]["gates"]:
                if g["id"] in ("size", "mass"):
                    loose = g["range"][0] if g["op"] == ">=" else g["range"][1]
                    tight = g["range"][1] if g["op"] == ">=" else g["range"][0]
                    for tag, v in (("loosest", loose), ("tightest", tight)):
                        e = verdict(r, with_preset(m, mission, g["id"], v), mission)
                        ends[f"{g['id']} at {v:g} ({tag})"] = (e["status"], e["p"])
            out.append((mission, n, r, facts(r, m), ev, ends))
    return m, nh, records, out


def main(write=True, echo=True, check=False):
    rep = Report("missions")
    m, nh, records, out = run()
    mis = m.missions
    rep("MISSION PRESETS AGAINST THE NAMED TARGETS")
    rep(f"snapshot {config.DATA_DATE}; presets from method/v0_1/missions.toml; priors from method/v0_1/priors.toml")
    rep(f"read from the pipeline's records (longshot.ledger, longshot.model): {m.n_draws:,} stratified draws per object,")
    rep("the research snapshot of SsODNet cards alone. A gate is decided when the measured value clears the line by "
        f"{mis['rules']['decide']['sigma']:g} sigma.")
    rep()
    for mission in mis["order"]:
        rep(f"== {mission}: " + "; ".join(f"{g['id']} {g['op']} {g['preset']:g}" for g in mis[mission]["gates"]))
        for mm, n, r, f, ev, ends in out:
            if mm != mission:
                continue
            rep(f"{n['designation']} ({n['pdes']}): H {f['h']}, H_sigma {f['h_sigma']}, {f['dv']} km/s, orbit code {f['occ']}")
            rep(f"    size   {f.get('size_words', 'none measured')}")
            rep(f"    period {f.get('period_words', 'none measured')}")
            rep(f"    class  {f.get('cls_words', 'none on file')}")
            if f["density"]:
                rep(f"    density on file {f['density']:g} kg/m3: it narrows the mass draws and decides no gate")
            q = r.summary["size_m"]
            rep(f"    draws: size {q['q05']:g} to {q['q95']:g} m, mass {r.summary['mass_t']['q05']:g} to "
                f"{r.summary['mass_t']['q95']:g} t (5th to 95th)")
            for gid, (st, p, text) in ev["gates"].items():
                rep(f"    {gid:8s} {st:9s}" + (f" p {p:.4f}" if st == "untested" and p is not None else "         ")
                    + (f"  {text}" if text else ""))
            rep(f"    => {ev['status']}" + (f", p {ev['p']:.4f}" if ev["status"] == "untested" else ""))
            for k, (st, p) in ends.items():
                rep(f"       with {k}: {st}" + (f", p {p:.4f}" if st == "untested" else ""))
            rep(f"    recorded in missions.toml: {n['status']}, p {n['p']}")
        rep()
    rep("ORBIT GATE ON THE WHOLE LIST (orbit code at most the preset)")
    for mission in mis["order"]:
        thr = next(g["preset"] for g in mis[mission]["gates"] if g["id"] == "findable")
        for label, sel in (("all", lambda o: True), ("under 6 km/s", lambda o: fl(o["min_dv"]["dv"]) < 6),
                           ("under 5 km/s", lambda o: fl(o["min_dv"]["dv"]) < 5)):
            pop = [o for o in nh.values() if sel(o)]
            rep(f"  {mission}, {label}: {sum(1 for o in pop if int(o['occ']) <= thr)} of {len(pop)}")
    passing = [o for o in nh.values() if int(o["occ"]) <= 5]
    survey = [o for o in passing if o.get("obs_flag") == "S"]
    rep(f"  of the {len(passing)} that pass, JPL flags the next window of {len(survey)} survey-recovery-only "
        f"({sum(1 for o in survey if int(o['occ']) == 5)} at code 5, {sum(1 for o in survey if int(o['occ']) == 4)} at code 4) "
        f"and lists no window for {sum(1 for o in passing if not o.get('obs_start'))}")
    rep()
    rep("MEASURED SIZES THAT DO NOT FIT THE BRIGHTNESS (rules.size)")
    rules = mis["rules"]["size"]
    turned_away, lowest = [], []
    for r in records:
        inp = draws.inputs(r, m)
        x = inp.size or inp.size_rejected
        if x is None or inp.h is None:
            continue
        pv = priors.implied_reflectivity(m, inp.h, x.value)
        lowest.append((pv, r.designation))
        if inp.size_rejected is not None:
            turned_away.append(f"{r.designation} {pv:.4g}")
    lowest.sort()
    rep(f"  list members with a size in use and an H: {len(lowest)}; lowest implied reflectivities: "
        + ", ".join(f"{d} {pv:.4f}" for pv, d in lowest[:4]) + "; highest: "
        + ", ".join(f"{d} {pv:.3f}" for pv, d in lowest[-3:]))
    rep(f"  outside {rules['min_implied_reflectivity']} to {rules['max_implied_reflectivity']:g} for every H within "
        f"{mis['rules']['decide']['sigma']:g} sigma: " + (", ".join(turned_away) or "none"))
    rep()
    rep("CRITICAL PERIOD, P = sqrt(3 pi / (G density))")
    spin = next(g for g in mis["surface"]["gates"] if g["id"] == "spin")
    for rho in (1200, 2000, spin["density_kgm3"], 3300, 7500):
        rep(f"  {rho} kg/m3: {math.sqrt(3 * math.pi / (spin['gravitational_constant'] * rho)) / 3600:.2f} h")
    text = rep.close(write=write and not check, echo=echo)
    if check:
        bad = problems(out)
        if bad:
            sys.stderr.write("\n".join(bad) + "\n")
            sys.exit(1)
    return text


def problems(out):
    """Where missions.toml records something the pipeline does not give."""
    bad = []
    for mission, n, r, f, ev, ends in out:
        if ev["status"] != n["status"] or abs(ev["p"] - n["p"]) > P_TOLERANCE + 1e-9:
            bad.append(f"{mission} {n['designation']}: recorded {n['status']} {n['p']}, derived {ev['status']} {ev['p']:.4f}")
        for gid, (st, _, _) in ev["gates"].items():
            if n["gates"].get(gid) != st:
                bad.append(f"{mission} {n['designation']} gate {gid}: recorded {n['gates'].get(gid)}, derived {st}")
    return bad


if __name__ == "__main__":
    main(check="--check" in sys.argv, echo="--check" not in sys.argv)
