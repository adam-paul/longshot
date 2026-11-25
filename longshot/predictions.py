"""The record: what the method predicts, and what would settle each prediction.

    predictions(records=None) -> list[dict]

Two kinds. A "rule" covers any reachable asteroid that meets its condition,
discovered or not (docs/plan.md Appendix C, WP4): the class shares, the spin
shares and the size ranges of method/v0_1/priors.toml, one row per brightness
band. A "case" is one named asteroid whose answer has a known route. With
`records` the cases carry this build's range for the asteroid; without, they
carry no range.

Every prediction is provisional: `frozen` is None until Adam freezes the method.

    {id, kind (rule|case), group (class|spin|size|density), statement, p, p_low, p_high, band,
     settles, settle_from, settle_by, settle_note, key, designation, frozen, provisional, outcome, basis, source}

settle_note is set when neither date is: a few words saying why there is none.

statement, settles and basis are for a visitor. source says where in the repository the route to an
answer is written down, and is not for the page.

p is the chance the statement holds. p_low and p_high are the spread between
surveys, where the method gives one. `designation` is the asteroid's name where
it has one, since the page prints it before the statement.
"""
from __future__ import annotations

from longshot import draws as draws_mod
from longshot import method as method_mod
from longshot import priors
from longshot.method import Method
from longshot.missions import figures
from longshot.types import ObjectRecord

CLASS_WORDS = {"S": "S or Q", "C": "C, B, F or G", "X": "X, E, M or P", "other": "none of S, C or X"}
SPIN_WORDS = {"under_2_2h": "2.2 hours", "under_1h": "1 hour", "under_10min": "10 minutes"}
# The brightness each size row is stated at: the middle of its band, and one magnitude inside the two open bands.
SIZE_AT_H = {"under_20": 19.0, "20_22": 21.0, "22_24": 23.0, "24_26": 25.0, "26_28": 27.0, "28_up": 29.0}
RANGE_P = 0.90          # a 5th-to-95th range holds nine times in ten if the prior is right

SETTLES = {
    "class": ("class labels published after the freeze; one survey aims at colours for about 1,000 small "
              "asteroids by the end of 2027"),
    "spin": "rotation periods graded U 2 or better, published after the freeze",
    "size": "sizes measured after the freeze",
}
# What stands in the "when" column for a prediction with no date: why there is none.
NO_DATE = {
    "spin": "no date: needs about 30 new periods",
    "size": "no date: needs new measured sizes",
    "density": "no date set",
}
SOURCE = {
    "class": "docs/plan.md Appendix C, WP4; method/v0_1/priors.toml [class.bands]",
    "spin": "docs/plan.md section 3.3; method/v0_1/priors.toml [spin.bands]",
    "size": "docs/plan.md Appendix A, Size from H; method/v0_1/priors.toml [reflectivity]",
    "case": "docs/plan.md Appendix C, WP4, named cases",
}

# docs/plan.md Appendix C, WP4, named cases. `names` are matched against designation, name and aliases.
CASES = (
    {"id": "case-apophis-density", "names": ("99942", "2004 MN4", "Apophis"), "label": "Apophis", "group": "density",
     "settles": "a density measured at its 2029 pass of Earth", "settle_from": "2029", "settle_by": None},
    {"id": "case-kamooalewa-density", "names": ("469219", "2016 HO3", "Kamoʻoalewa", "Kamo`oalewa"),
     "label": "Kamoʻoalewa", "group": "density",
     "settles": "a mass published by Tianwen-2, which reached it in July 2026",
     "settle_from": None, "settle_by": None},
    {"id": "case-2015bm510-size", "names": ("2015 BM510",), "label": "2015 BM510", "group": "size",
     "settles": "Hayabusa2's flyby, if it succeeds", "settle_from": "2028-04", "settle_by": None},
)


def _base(**kw) -> dict:
    out = {"id": None, "kind": None, "group": None, "statement": None, "p": None, "p_low": None, "p_high": None,
           "band": None, "settles": None, "settle_from": None, "settle_by": None, "settle_note": None, "key": None,
           "designation": None, "frozen": None, "provisional": True, "outcome": None, "basis": None, "source": None}
    out.update(kw)
    if out["settle_from"] is None and out["settle_by"] is None and out["settle_note"] is None:
        out["settle_note"] = NO_DATE.get(out["group"], "no date set")
    if out["source"] is None:
        out["source"] = SOURCE["case" if out["kind"] == "case" else out["group"]]
    return out


def _band_condition(band: str) -> str:
    return f"of H {priors.BAND_WORDS.get(band, band)}"


def class_rules(m: Method) -> list[dict]:
    out = []
    for band in m.priors["bands"]["ids"]:
        row = m.priors["class"]["bands"][band]
        for c in m.priors["class"]["ids"]:
            out.append(_base(
                id=f"rule-class-{band}-{c}", kind="rule", group="class", band=band,
                statement=f"A reachable asteroid {_band_condition(band)} that gets a class is {CLASS_WORDS[c]}.",
                p=round(row["central"][c], 4), p_low=round(row["low"][c], 4), p_high=round(row["high"][c], 4),
                settles=SETTLES["class"], settle_by="2027-12-31",
                basis=(f"{row['n']} labelled near-Earth asteroids in this band; "
                       "low and high are the spread between surveys")))
    return out


def spin_rules(m: Method) -> list[dict]:
    out = []
    for band in m.priors["bands"]["ids"]:
        for s in m.priors["spin"]["ids"]:
            row = m.priors["spin"]["bands"][band][s]
            out.append(_base(
                id=f"rule-spin-{band}-{s}", kind="rule", group="spin", band=band,
                statement=(f"A reachable asteroid {_band_condition(band)} that gets its first reliable period "
                           f"turns faster than once in {SPIN_WORDS.get(s, s)}."),
                p=row["central"], p_low=row["low"], p_high=row["high"], settles=SETTLES["spin"],
                basis=f"low: {row['low_from']}; high: {row['high_from']}"))
    return out


def size_rules(m: Method) -> list[dict]:
    """The 5th-to-95th size at one brightness per band, from the same draw every object gets."""
    out = []
    sigma = m.priors["h_uncertainty"]["default_sigma"]
    far = m.priors["size"]["extrapolated_fainter_than_h"]
    for band in m.priors["bands"]["ids"]:
        h = SIZE_AT_H.get(band)
        if h is None or priors.band_of(m, h) != band:
            raise method_mod.MethodError(f"priors.toml: band {band} has no brightness to state a size rule at")
        inp = draws_mod.Inputs(h=h, h_sigma=sigma, band=band)
        d = draws_mod.joint(f"rule size {band}", inp, m)
        q = priors.quantiles(d.d)
        out.append(_base(
            id=f"rule-size-{band}", kind="rule", group="size", band=band,
            statement=(f"A reachable asteroid of H {h:g} that gets a measured size is "
                       f"{figures(q['q05'])} to {figures(q['q95'])} m across."),
            p=RANGE_P, settles=SETTLES["size"],
            basis=(f"H {h:g} ± {sigma:g} and the reflectivities Spitzer measured; each magnitude fainter is 0.63 "
                   "times the size" + ("; extrapolated, as nearly all of Spitzer's objects are brighter"
                                       if h >= far else ""))))
    return out


def _find(records, names) -> ObjectRecord | None:
    want = set(names)
    for r in records or ():
        have = {r.designation, r.name, str(r.number) if r.number else None, *r.aliases}
        if want & {x for x in have if x}:
            return r
    return None


def cases(m: Method, records=None) -> list[dict]:
    out = []
    for case in CASES:
        r = _find(records, case["names"])
        d = draws_mod.for_record(r, m) if r is not None else None
        p = None
        if case["group"] == "density":
            what = "has a bulk density"
            if d is not None:
                v = sorted(d.rho)
                lo, hi = priors.quantile(v, 0.05), priors.quantile(v, 0.95)
                statement = f"{what} of {figures(lo)} to {figures(hi)} kg/m³."
                p = RANGE_P
                cls = d.inputs.cls
                basis = (f"the density range for class {cls}" if cls else "the density ranges of its possible classes")
            else:
                statement, basis = f"{what} inside the range this build gives it.", None
        else:
            if d is not None:
                v = sorted(d.d)
                lo, hi = priors.quantile(v, 0.05), priors.quantile(v, 0.95)
                statement = f"is {figures(lo)} to {figures(hi)} m across."
                p = RANGE_P
                basis = priors.size_basis(m, d.inputs) if not d.inputs.size_measured else "its measured size"
            else:
                statement, basis = "has a size inside the range this build gives it.", None
        out.append(_base(
            id=case["id"], kind="case", group=case["group"], statement=statement, p=p,
            settles=case["settles"], settle_from=case["settle_from"], settle_by=case["settle_by"],
            key=r.key if r is not None else None, designation=case["label"], basis=basis))
    return out


def predictions(records: list[ObjectRecord] | None = None, m: Method | None = None) -> list[dict]:
    """Everything the record page lists, rules first. All provisional until the method is frozen."""
    m = m or method_mod.load()
    return class_rules(m) + spin_rules(m) + size_rules(m) + cases(m, records)
