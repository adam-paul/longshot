"""Nine hand-made records for building and testing the site before real data exists.

Every value here is invented. The designations use the year 2099 so that nothing
on a sample page can be mistaken for a real asteroid. Between them the records
cover: all four row states, a conflict, an unreliable period, a period held only
by an inference-licence source, every mission status, a missing observe block, a
missing window, value blocks with and without water, an empty value block, an
object with no brightness, and all three ladder statuses. Record I is written the
way the pipeline writes one: the ledger's labels, a note that ends with why each
source was not checked, missions that no draw passes or fails, and a size, spin and
surface that were not checked. Sizes from a source that is not open come three
ways: with no open size on the record (B), with JPL's own diameter (E), and with
the range from brightness the field file carries (G).

    uv run python -m tests.sample_records     # writes build/sample-site/
"""
from __future__ import annotations

import shutil
from pathlib import Path

from longshot.types import Fact, ObjectRecord, Row, Source

DATA_DATE = "2026-11-24"
METHOD = "0.1"

SOURCES = {
    "jpl-nhats": Source(
        "jpl-nhats", "JPL NHATS", "2026-11-24", "2026-11-24", "open",
        "Near-Earth Object Human Space Flight Accessible Targets Study, NASA/JPL.",
        "https://cneos.jpl.nasa.gov/nhats/"),
    "jpl-sbdb": Source(
        "jpl-sbdb", "JPL Small-Body Database", "2026-11-24", "2026-11-24", "open",
        "Small-Body Database, NASA/JPL Solar System Dynamics.",
        "https://ssd.jpl.nasa.gov/tools/sbdb_query.html"),
    "ssodnet": Source(
        "ssodnet", "SsODNet", "2026-11-21", "2026-11-21", "single",
        "Berthier et al. 2023, Astronomy & Astrophysics 671, A151.",
        "https://ssp.imcce.fr/webservices/ssodnet/"),
    "pravec": Source(
        "pravec", "Ondřejov photometry table", "2026-11-24", "2026-11-24", "single",
        "Pravec, Wolf and Šarounová, Ondřejov Asteroid Photometry Project.",
        "https://www.asu.cas.cz/~ppravec/newres.txt"),
    "lcdb": Source(
        "lcdb", "Asteroid Lightcurve Database", "2023-10-01", "2026-11-21", "inference",
        "Warner, Harris and Pravec 2009, Icarus 202, 134; release of 2023 October.",
        "https://minplanobs.org/mpinfo/php/lcdb.php"),
    "spitzer": Source(
        "spitzer", "Spitzer near-Earth object surveys", "2016-09-01", "2026-11-21", "single",
        "Trilling et al. 2016, Astronomical Journal 152, 172.",
        "https://nearearthobjects.nau.edu/spitzerneos.html"),
}


def _q(q05, q25, q50, q75, q95, unit, basis):
    return {"q05": q05, "q25": q25, "q50": q50, "q75": q75, "q95": q95, "unit": unit, "basis": basis}


_CLASS_BASIS = "class shares at this brightness, with the spread between surveys"
_SHARES = {"shares": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}, "basis": _CLASS_BASIS}
_PRICE = "list prices of 2026-11-20, for what is in the rock before any cost"
_LAST_RUNG = ("Done three times, by space agencies, on asteroids hundreds of metres wide: about 127 g in all. "
              "Not yet attempted on one this small. Returning tonnes: proposed.")


def _gate(gid, label, status, basis, text, p=None):
    return {"id": gid, "label": label, "status": status, "p": p, "basis": basis, "text": text}


def _ladder(*pairs):
    rungs = ("found_again", "reached", "workable", "anything_in_it", "brought_back")
    return [{"rung": r, "status": s, "text": x} for r, (s, x) in zip(rungs, pairs)]


def _reach(dv, days):
    return Row("measured", [
        Fact("delta-v, cheapest round trip", dv, unit="km/s", source="jpl-nhats"),
        Fact("that trip lasts", days, unit="d", source="jpl-nhats"),
    ])


def _tracking(days, code, n, last):
    return Row("measured", [
        Fact("observed over", days, unit="d", source="jpl-sbdb"),
        Fact("orbit condition code", code, source="jpl-sbdb", quality="0 best, 9 worst"),
        Fact("observations", n, source="jpl-sbdb"),
        Fact("last observed", last, source="jpl-sbdb"),
    ])


RECORDS = [
    # A. Small, cheap, fast. Spin from a single-value source; surface never checked; push is a limit.
    ObjectRecord(
        key="s0000001", designation="2099 OB5", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(4.62, 354),
            "tracking": _tracking(21, 6, 48, "2099-08-12"),
            "size": Row("prior", prior=_q(3.1, 4.6, 6.2, 8.4, 12.9, "m",
                                          "brightness H 28.9 and the reflectivities Spitzer measured")),
            "spin": Row("measured", [
                Fact("period", 0.0257, 0.025683, 0.025717, "h", source="pravec", ref="Sample et al. 2099", quality="3"),
            ]),
            "surface": Row("unchecked", prior=dict(_SHARES), unchecked=["ssodnet"]),
            "push": Row("limit", [
                Fact("drift, A2", 2.1e-13, unit="au/d^2", kind="upper", source="jpl-sbdb"),
            ], note="21 days of tracking: too short for more than a bound."),
        },
        summary={"size_m": {"q05": 3.1, "q25": 4.6, "q50": 6.2, "q75": 8.4, "q95": 12.9},
                 "mass_t": {"q05": 28, "q25": 95, "q50": 240, "q75": 610, "q95": 2300},
                 "p_fast_2_2h": 1.0, "p_under_1h": 1.0, "p_under_10min": 1.0,
                 "class": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}},
        missions={
            "surface": {"status": "fail", "p": 0.0, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 6"),
                _gate("size", "40 m or more across", "fail", "prior", "under 1% at this brightness", 0.004),
                _gate("spin", "turns slower than 2.2 h", "fail", "measured", "one turn in 92.52 s"),
            ]},
            "capture": {"status": "untested", "p": 0.41, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 6"),
                _gate("size", "10 m or less across", "untested", "prior", "from brightness alone", 0.86),
                _gate("mass", "light enough to move", "untested", "prior", "needs a size and a density", 0.48),
            ]},
        },
        observe={"best": "size", "mission": "capture", "gate": "size", "gain": 0.52,
                 "text": "A size. It settles the size gate and narrows the mass.",
                 "window": {"start": "2027-02-10", "end": "2027-04-02", "peak_mag": 19.8,
                            "pointable": True, "as_of": DATA_DATE},
                 "needs": "2 m telescope, or radar at the close pass"},
        value={"metal": {"p_nothing": 0.44, "usd": {"q05": 9e3, "q25": 4e4, "q75": 3.1e5, "q95": 1.2e6},
                         "kg": {"q05": 0.2, "q95": 31}},
               "water": None, "basis": _PRICE,
               "statements": [
                   "Of 100 asteroids this bright, about 44 hold no platinum-group metal in separable form.",
                   "About 53 hold 0.2 to 31 kg of it.",
                   "Counting the zeros, three in four hold under $310 thousand of it.",
                   "About 3 are metal-rich, hold far more, and cannot be identified from Earth.",
               ]},
        ladder=_ladder(
            ("measured", "Orbit condition code 6. It may need finding again before 2027."),
            ("measured", "4.62 km/s, a round trip of 354 d."),
            ("measured", "One turn in 92.52 s. Nothing loose stays on a surface turning that fast."),
            ("prior", "Nothing measured. About 44 in 100 this bright hold no separable metal."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "pravec"],
    ),
    # B. JPL and the lightcurve database give the same period; the database grades it unreliable,
    #    so the ledger leaves the row unmeasured and keeps both lines on file.
    ObjectRecord(
        key="s0000002", designation="2099 AA37", name=None, number=None, aliases=["K99A37A"],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(5.71, 386),
            "tracking": _tracking(4380, 0, 912, "2099-03-30"),
            "size": Row("measured", [
                Fact("diameter", 65, 50, 85, "m", source="ssodnet", ref="Example and Other 2098", quality="thermal model"),
            ]),
            "spin": Row("prior", [
                Fact("period", 10.0, unit="h", source="jpl-sbdb"),
                Fact("period", 10.0, unit="h", source="lcdb", ref="Observer 2097", quality="1+"),
            ], note="The period on file is graded below U 2-, the lowest grade the lightcurve database accepts."),
            "surface": Row("measured", [
                Fact("albedo", 0.11, 0.07, 0.16, "", source="spitzer", ref="Example and Other 2098"),
            ]),
            "push": Row("prior", note="No fitted value in JPL's table."),
        },
        summary={"size_m": {"q05": 50, "q25": 58, "q50": 65, "q75": 73, "q95": 85},
                 "mass_t": {"q05": 1.1e5, "q25": 2.1e5, "q50": 3.2e5, "q75": 4.9e5, "q95": 9.4e5},
                 "p_fast_2_2h": 0.31, "p_under_1h": 0.12, "p_under_10min": 0.02},
        missions={
            "surface": {"status": "untested", "p": 0.35, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 0"),
                _gate("size", "40 m or more across", "pass", "measured", "65 m"),
                _gate("spin", "turns slower than 2.2 h", "untested", "prior",
                      "the one period on file is graded unreliable", 0.35),
            ]},
            "capture": {"status": "fail", "p": 0.0, "gates": [
                _gate("size", "10 m or less across", "fail", "measured", "65 m"),
            ]},
        },
        observe={"best": "lightcurve", "gain": 0.35, "text": "A rotation period. It settles the spin gate.",
                 "window": {"start": "2026-11-02", "end": "2027-01-18", "peak_mag": 21.6,
                            "pointable": False, "as_of": DATA_DATE},
                 "needs": "4 m telescope, two nights"},
        value={"metal": {"p_nothing": 0.43, "usd": {"q05": 2e7, "q25": 9e7, "q75": 6e8, "q95": 2.4e9},
                         "kg": {"q05": 400, "q95": 61000}},
               "water": None, "basis": _PRICE, "statements": []},
        ladder=_ladder(
            ("measured", "Orbit condition code 0."),
            ("measured", "5.71 km/s, a round trip of 386 d."),
            ("prior", "65 m across. The spin is not established."),
            ("prior", "Reflectivity measured; no class on file."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "ssodnet", "spitzer", "lcdb"],
    ),
    # C. Two sources disagree on the period by a factor of 100; size is a bound; no window on file.
    ObjectRecord(
        key="s0000003", designation="2099 NJ", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(6.35, 402),
            "tracking": _tracking(2190, 1, 301, "2099-07-04"),
            "size": Row("limit", [
                Fact("diameter", 200, unit="m", kind="upper", source="ssodnet", ref="Radar Team 2098",
                     quality="radar, not resolved"),
            ]),
            "spin": Row("measured", [
                Fact("period", 2.02, unit="h", source="ssodnet", ref="First 2096"),
                Fact("period", 0.0202, unit="h", source="jpl-sbdb"),
            ], conflicts=["Two sources give periods a factor of 100 apart."]),
            "surface": Row("measured", [
                Fact("class", "Sq", source="ssodnet", ref="Spectra 2097", quality="visible spectrum"),
            ]),
            "push": Row("prior", note="No fitted value in JPL's table."),
        },
        summary={"size_m": {"q05": 70, "q25": 105, "q50": 135, "q75": 165, "q95": 196},
                 "mass_t": {"q05": 3e5, "q25": 1e6, "q50": 2.4e6, "q75": 4.6e6, "q95": 9e6}},
        missions={
            "surface": {"status": "untested", "p": 0.48, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 1"),
                _gate("size", "40 m or more across", "untested", "prior", "under 200 m is all that is known", 0.97),
                _gate("spin", "turns slower than 2.2 h", "untested", "prior", "two periods on file disagree", 0.5),
            ]},
            "capture": {"status": "fail", "p": 0.0, "gates": [
                _gate("size", "10 m or less across", "fail", "prior", "under 1% at this brightness", 0.002),
            ]},
        },
        observe={"best": "lightcurve", "gain": 0.48, "text": "A rotation period. It settles which of the two is right.",
                 "window": None, "needs": "1 m telescope, one night"},
        value={"metal": {"p_nothing": 0.38, "usd": {"q05": 3e8, "q25": 9e8, "q75": 7e9, "q95": 3e10},
                         "kg": {"q05": 6000, "q95": 7.1e5}},
               "water": None, "basis": _PRICE,
               "statements": ["Of 100 asteroids of this class and size, about 38 hold no platinum-group metal in separable form."]},
        ladder=_ladder(
            ("measured", "Orbit condition code 1."),
            ("measured", "6.35 km/s, a round trip of 402 d."),
            ("prior", "Under 200 m. Two periods on file disagree."),
            ("measured", "Class Sq, from one visible spectrum."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "ssodnet"],
    ),
    # D. The only period is in an inference-licence source. Three rows not checked. No observe block.
    ObjectRecord(
        key="s0000004", designation="2099 XD3", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(5.02, 370),
            "tracking": _tracking(190, 4, 77, "2099-12-01"),
            "size": Row("unchecked", prior=_q(22, 33, 44, 61, 93, "m",
                                              "brightness H 24.6 and the reflectivities Spitzer measured"),
                        unchecked=["ssodnet", "spitzer"]),
            "spin": Row("measured", [
                Fact("period", 5.432, unit="h", source="lcdb", ref="Observer 2098", quality="2+"),
            ]),
            "surface": Row("unchecked", prior=dict(_SHARES), unchecked=["ssodnet", "spitzer"]),
            "push": Row("unchecked", unchecked=["jpl-sbdb"]),
        },
        summary={"size_m": {"q05": 22, "q25": 33, "q50": 44, "q75": 61, "q95": 93},
                 "mass_t": {"q05": 9e3, "q25": 3.4e4, "q50": 8.5e4, "q75": 2.2e5, "q95": 8e5},
                 "class": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}},
        missions={
            "surface": {"status": "untested", "p": 0.57, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 4"),
                _gate("size", "40 m or more across", "untested", "prior", "from brightness alone", 0.57),
                _gate("spin", "turns slower than 2.2 h", "pass", "measured", "period on file"),
            ]},
            "capture": {"status": "fail", "p": 0.0, "gates": [
                _gate("size", "10 m or less across", "fail", "prior", "under 1% at this brightness", 0.001),
            ]},
        },
        observe=None,
        value={"metal": {"p_nothing": 0.43, "usd": {"q05": 4e6, "q25": 2e7, "q75": 1.5e8, "q95": 9e8},
                         "kg": {"q05": 90, "q95": 21000}},
               "water": {"p_nothing": 0.89, "tonnes": {"q05": 300, "q95": 24000}}, "basis": _PRICE,
               "statements": [
                   "Of 100 asteroids this bright, about 43 hold no platinum-group metal in separable form.",
                   "Of 100 like it, 88 to 90 hold no water bound in minerals.",
                   "Nine in ten of the rest hold 300 to 24,000 tonnes.",
               ]},
        ladder=_ladder(
            ("measured", "Orbit condition code 4."),
            ("measured", "5.02 km/s, a round trip of 370 d."),
            ("prior", "Size from brightness alone: 22 to 93 m."),
            ("prior", "Nothing measured."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "lcdb"],
    ),
    # E. A known answer: named, numbered, everything measured, surface work passes.
    ObjectRecord(
        key="s0000005", designation="2099 RQ36", name="Samplea", number=909090, aliases=["909090", "Samplea"],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(5.09, 450),
            "tracking": _tracking(8100, 0, 5120, "2099-05-19"),
            "size": Row("measured", [
                Fact("diameter", 490, 484, 496, "m", source="ssodnet", ref="Mission Team 2098", quality="SPACE"),
                Fact("diameter", 492, unit="m", source="jpl-sbdb"),
            ]),
            "spin": Row("measured", [
                Fact("period", 4.297, unit="h", source="jpl-sbdb"),
                Fact("period", 4.2905, unit="h", source="lcdb", ref="Mission Team 2098", quality="3"),
            ]),
            "surface": Row("measured", [
                Fact("class", "B", source="ssodnet", ref="Spectra 2090", quality="visible and near-infrared spectrum"),
                Fact("albedo", 0.044, 0.042, 0.046, "", source="ssodnet", ref="Mission Team 2098", quality="spacecraft"),
            ]),
            "push": Row("measured", [
                Fact("drift, A2", -4.6e-14, -4.7e-14, -4.5e-14, "au/d^2", source="jpl-sbdb"),
            ]),
        },
        summary={"size_m": {"q05": 484, "q25": 488, "q50": 490, "q75": 492, "q95": 496},
                 "mass_t": {"q05": 7.1e7, "q25": 7.2e7, "q50": 7.3e7, "q75": 7.4e7, "q95": 7.5e7}},
        missions={
            "surface": {"status": "pass", "p": 1.0, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 0"),
                _gate("size", "40 m or more across", "pass", "measured", "490 m"),
                _gate("spin", "turns slower than 2.2 h", "pass", "measured", "one turn in 4.297 h"),
            ]},
            "capture": {"status": "fail", "p": 0.0, "gates": [
                _gate("size", "10 m or less across", "fail", "measured", "490 m"),
            ]},
        },
        observe=None,
        value={"metal": {"p_nothing": 0.9, "usd": {"q05": 1e9, "q25": 4e9, "q75": 3e10, "q95": 1e11},
                         "kg": {"q05": 2e4, "q95": 3e6}},
               "water": {"p_nothing": 0.1, "tonnes": {"q05": 1e6, "q95": 7e6}}, "basis": _PRICE,
               "statements": [
                   "A carbon-rich class: about 90 in 100 like it hold no platinum-group metal in separable form.",
                   "About 10 in 100 like it hold no water. The rest hold 1 to 7 million t, bound in the rock.",
               ]},
        ladder=_ladder(
            ("measured", "Orbit condition code 0."),
            ("measured", "5.09 km/s, a round trip of 450 d."),
            ("measured", "490 m across, one turn in 4.297 h."),
            ("measured", "Class B. A spacecraft has sampled it."),
            ("measured", "Done once here, by a space agency: 121.6 g."),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "ssodnet", "lcdb"],
    ),
    # F. No brightness on file and a one-day arc: nothing to draw, nothing to price.
    ObjectRecord(
        key="s0000006", designation="2099 CW266", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(7.9, 418),
            "tracking": _tracking(1, 9, 11, "2099-02-14"),
            "size": Row("prior", note="No brightness on file, so no typical size."),
            "spin": Row("prior"),
            "surface": Row("prior", prior={"shares": {"S": 0.5, "C": 0.2, "X": 0.2, "other": 0.1},
                                           "basis": "class shares over all brightnesses"}),
            "push": Row("prior", note="One day of tracking carries no information."),
        },
        summary={},
        missions={
            "surface": {"status": "fail", "p": 0.0, "gates": [
                _gate("findable", "orbit good enough to find again", "fail", "measured", "condition code 9, one day observed"),
            ]},
            "capture": {"status": "fail", "p": 0.0, "gates": [
                _gate("findable", "orbit good enough to find again", "fail", "measured", "condition code 9, one day observed"),
            ]},
        },
        observe=None,
        value={},
        ladder=_ladder(
            ("measured", "Orbit condition code 9 from one day of tracking. Lost."),
            ("measured", "7.9 km/s if it were found."),
            ("unknown", "No size and no spin."),
            ("unknown", "Nothing on file."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb"],
    ),
    # G. Small, measured, and it passes whole-body capture.
    ObjectRecord(
        key="s0000007", designation="2099 KY26", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(4.31, 362),
            "tracking": _tracking(9500, 0, 640, "2099-06-21"),
            "size": Row("measured", [
                Fact("diameter", 8.0, 6.0, 10.0, "m", source="ssodnet", ref="Radar Team 2099", quality="radar"),
            ]),
            "spin": Row("measured", [
                Fact("period", 0.1784, 0.1782, 0.1786, "h", source="jpl-sbdb"),
            ]),
            "surface": Row("prior", prior={**_q(0.30, 0.46, 0.65, 0.93, 1.45, "", _CLASS_BASIS + "; reflectivity from its measured size and H"),
                                           "shares": dict(_SHARES["shares"])}),
            "push": Row("measured", [
                Fact("drift, A2", -1.42e-13, -1.9e-13, -0.94e-13, "au/d^2", source="jpl-sbdb"),
                Fact("radiation pressure, A1", 6.1e-11, 2.2e-11, 1.0e-10, "au/d^2", source="jpl-sbdb"),
            ]),
        },
        summary={"size_m": {"q05": 6, "q25": 7.2, "q50": 8, "q75": 8.8, "q95": 10},
                 "size_open_m": {"q05": 5.2, "q50": 9.4, "q95": 21},
                 "mass_t": {"q05": 160, "q25": 340, "q50": 540, "q75": 800, "q95": 1500},
                 "class": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}},
        missions={
            "surface": {"status": "fail", "p": 0.0, "gates": [
                _gate("size", "40 m or more across", "fail", "measured", "8 m"),
            ]},
            "capture": {"status": "pass", "p": 1.0, "gates": [
                _gate("findable", "orbit good enough to find again", "pass", "measured", "condition code 0"),
                _gate("size", "10 m or less across", "pass", "measured", "8 m, range 6–10 m"),
                _gate("mass", "light enough to move", "pass", "measured", "from radiation pressure and size"),
            ]},
        },
        observe=None,
        value={"metal": {"p_nothing": 0.44, "usd": {"q05": 2e4, "q25": 8e4, "q75": 6.2e5, "q95": 2.5e6},
                         "kg": {"q05": 0.5, "q95": 60}},
               "water": None, "basis": _PRICE,
               "statements": ["Of 100 asteroids like it, about 44 hold no platinum-group metal in separable form."]},
        ladder=_ladder(
            ("measured", "Orbit condition code 0."),
            ("measured", "4.31 km/s, a round trip of 362 d."),
            ("measured", "8 m across, one turn in 10.7 min: too fast for surface work, small enough to bag."),
            ("prior", "No class on file."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "ssodnet"],
    ),
    # H. Bright for its cost, nothing measured but a lower bound on the period. Both missions untested.
    ObjectRecord(
        key="s0000008", designation="2099 HT", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": _reach(4.58, 378),
            "tracking": _tracking(57, 5, 92, "2099-06-02"),
            "size": Row("prior", prior=_q(8.5, 12, 17, 23, 36, "m",
                                          "brightness H 26.7 and the reflectivities Spitzer measured")),
            "spin": Row("limit", [
                Fact("period", 4.0, unit="h", kind="lower", source="ssodnet", ref="Night 2099",
                     quality="one partial night"),
            ]),
            "surface": Row("prior", prior=_q(0.05, 0.12, 0.2, 0.29, 0.45, "", "the reflectivities Spitzer measured")),
            "push": Row("prior", note="57 days of tracking carries no information."),
        },
        summary={"size_m": {"q05": 8.5, "q25": 12, "q50": 17, "q75": 23, "q95": 36},
                 "mass_t": {"q05": 71000, "q25": 210000, "q50": 520000, "q75": 1300000, "q95": 3600000},
                 "p_fast_2_2h": 0.0, "p_under_1h": 0.0, "p_under_10min": 0.0,
                 "class": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}},
        missions={
            "surface": {"status": "untested", "p": 0.03, "gates": [
                _gate("findable", "orbit good enough to find again", "untested", "prior", "57 days observed", 0.6),
                _gate("size", "40 m or more across", "untested", "prior", "from brightness alone", 0.04),
                _gate("spin", "turns slower than 2.2 h", "pass", "measured", "slower than 4 h"),
            ]},
            "capture": {"status": "untested", "p": 0.08, "gates": [
                _gate("findable", "orbit good enough to find again", "untested", "prior", "57 days observed", 0.6),
                _gate("size", "10 m or less across", "untested", "prior", "from brightness alone", 0.13),
            ]},
        },
        observe={"best": "astrometry", "gain": 0.6, "text": "Positions over a second month. They settle whether it can be found again.",
                 "window": {"start": "2027-02-20", "end": "2027-04-11", "peak_mag": 17.5,
                            "pointable": True, "as_of": DATA_DATE},
                 "needs": "small telescope, a few nights"},
        value={"metal": {"p_nothing": 0.43, "usd": {"q05": 2e5, "q25": 9e5, "q75": 7e6, "q95": 4e7},
                         "kg": {"q05": 4, "q95": 900}},
               "water": {"p_nothing": 0.89, "tonnes": {"q05": 20, "q95": 1500}}, "basis": _PRICE,
               "statements": [
                   "Of 100 asteroids this bright, about 43 hold no platinum-group metal in separable form.",
                   "Counting the zeros, three in four hold under $7 million of it.",
                   "Of 100 like it, 88 to 90 hold no water bound in minerals.",
               ]},
        ladder=_ladder(
            ("prior", "57 days of tracking. It may need finding again first."),
            ("measured", "4.58 km/s, a round trip of 378 d."),
            ("prior", "Probably too small for surface work, probably too big to bag."),
            ("prior", "Nothing measured."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb", "ssodnet"],
    ),
    # I. As the pipeline writes one. Three rows not checked, each note ending with why; a mission no draw
    #    passes and one every draw passes, neither of them settled; nothing ranked to observe.
    ObjectRecord(
        key="s0000009", designation="2099 QQ8", name=None, number=None, aliases=[],
        populations=["nhats"], data_date=DATA_DATE, method=METHOD,
        rows={
            "reach": Row("measured", [
                Fact("delta-v", 3.345, unit="km/s", source="jpl-nhats", ref="orbit solution 8"),
                Fact("trip at lowest delta-v", 362, unit="d", source="jpl-nhats", ref="orbit solution 8"),
            ]),
            "tracking": Row("measured", [
                Fact("condition code", 1, source="jpl-sbdb", ref="orbit solution JPL 8"),
                Fact("arc", 94, unit="d", source="jpl-sbdb", ref="orbit solution JPL 8"),
                Fact("next window", "none through 2045", source="jpl-nhats", ref="as of 2026-11-24"),
            ]),
            "size": Row("unchecked", [Fact("H", 31.37, 31.03, 31.71, "mag", source="jpl-sbdb")],
                        prior=_q(0.84, 1.1, 1.3, 1.7, 3.1, "m", "H 31.37 ± 0.34 and the reflectivities Spitzer measured"),
                        unchecked=["ssodnet"], note="SsODNet did not know this object on 2026-11-21."),
            "spin": Row("unchecked", prior={"p_fast_2_2h": 0.94, "p_under_1h": 0.94, "p_under_10min": 0.93,
                                            "basis": "asteroids of H 28 and fainter"},
                        unchecked=["ssodnet", "pravec"],
                        note="No SsODNet card has been fetched. Pravec's table is older than this object."),
            "surface": Row("unchecked", prior={**_q(0.057, 0.18, 0.27, 0.37, 0.66, "", _CLASS_BASIS),
                                               "shares": dict(_SHARES["shares"])},
                           unchecked=["ssodnet"], note="The request to SsODNet failed on 2026-11-25 (timed out)."),
            "push": Row("measured", [
                Fact("A1", 1.3e-10, 1.203e-10, 1.397e-10, "au/d^2", source="jpl-sbdb", ref="orbit solution JPL 8"),
                Fact("A2", -1.1e-12, -1.184e-12, -1.016e-12, "au/d^2", source="jpl-sbdb", ref="orbit solution JPL 8"),
            ], unchecked=["ssodnet"],
                note="JPL's bulk values are rounded to two figures and carry no force law. "
                     "SsODNet did not know this object on 2026-11-21."),
        },
        summary={"size_m": {"q05": 0.84, "q25": 1.1, "q50": 1.3, "q75": 1.7, "q95": 3.1},
                 "mass_t": {"q05": 0.63, "q25": 1.7, "q50": 3.2, "q75": 6.8, "q95": 27},
                 "p_fast_2_2h": 0.94, "p_under_1h": 0.94, "p_under_10min": 0.93,
                 "class": {"S": 0.52, "C": 0.17, "X": 0.19, "other": 0.12}},
        missions={
            "surface": {"status": "untested", "p": 0.0, "gates": [
                _gate("findable", "Orbit good enough to find again", "pass", "measured", "Orbit code 1, JPL's database.", 1.0),
                _gate("size", "30 m or wider", "untested", "prior",
                      "Size not checked (SsODNet). From brightness, 0.84 to 3.1 m.", 0.0),
                _gate("spin", "Turns once in 2.2 h or slower", "untested", "prior", "Period not checked (SsODNet).", 0.005),
            ]},
            "capture": {"status": "untested", "p": 1.0, "gates": [
                _gate("findable", "Orbit good enough to find again", "pass", "measured", "Orbit code 1, JPL's database.", 1.0),
                _gate("size", "10 m or smaller", "untested", "prior",
                      "Size not checked (SsODNet). From brightness, 0.84 to 3.1 m.", 1.0),
            ]},
        },
        observe=None,
        value={"metal": {"p_nothing": 0.34, "usd": {"q05": 0.0, "q25": 0.0, "q75": 1200, "q95": 5400},
                         "kg": {"q05": 0.0, "q95": 0.068}},
               "water": None, "basis": _PRICE,
               "statements": ["Of 100 like it, 31 to 36 hold no platinum-group metal in metal grains."]},
        ladder=_ladder(
            ("measured", "Orbit code 1 from 94 days of tracking."),
            ("measured", "Cheapest round trip: 3.345 km/s in 362 days (JPL)."),
            ("prior", "0.84 to 3.1 m across, from brightness alone. Spin not checked (SsODNet)."),
            ("prior", "Of 100 like it, 31 to 36 hold no platinum-group metal in metal grains."),
            ("unknown", _LAST_RUNG),
        ),
        sources=["jpl-nhats", "jpl-sbdb"],
    ),
]

PREDICTIONS = [
    {"id": "p-spin-2099ht", "statement": "turns slower than 2.2 h.", "p": 0.81, "frozen": None,
     "settles": "one night's lightcurve", "settle_from": "2027-02-20", "settle_by": "2027-04-11",
     "key": "s0000008", "designation": "2099 HT", "outcome": None},
    {"id": "p-size-2099ob5", "statement": "is 10 m or less across.", "p": 0.86, "frozen": "2026-11-24",
     "settles": "radar at the close pass", "settle_from": "2027-02-10", "settle_by": "2027-04-02",
     "key": "s0000001", "designation": "2099 OB5", "outcome": None},
    {"id": "p-periods-2027", "statement": "Of the periods published for reachable asteroids in 2027, at least half are under 1 h.",
     "p": 0.7, "frozen": "2026-11-24", "settles": "the lightcurve database's next release",
     "settle_from": "2028-01-01", "settle_by": None, "key": None, "designation": None,
     "outcome": "inside: 9 of 14"},
]

ASSETS = {"style": "static/style.css", "app": "static/app.js", "field_manifest": "data/field.json"}


def render(out_dir: Path) -> list[Path]:
    """Write the sample site, with the stylesheet beside it so the pages can be opened."""
    from longshot.site import gen

    written = gen.write_site(RECORDS, SOURCES, out_dir, ASSETS, PREDICTIONS)
    static = Path(gen.__file__).resolve().parent / "static"
    (out_dir / "static").mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "app.js", "field.js"):
        if (static / name).exists():
            shutil.copyfile(static / name, out_dir / "static" / name)
    return written


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "build" / "sample-site"
    paths = render(out)
    sizes = sorted(p.stat().st_size for p in paths if p.parent.name == "a")
    print(f"{len(paths)} pages in {out}")
    print(f"entry pages: {sizes[0]:,} to {sizes[-1]:,} bytes")
