"""The model: method loading, joint draws and priors, missions, observe, ladder, predictions.

Run: uv run python -m unittest tests.test_model

Every test builds its own records by hand (`make` below), so nothing here needs
the data on disk. Two tests also read build/ledger.jsonl and the source list
when they exist, and skip when they do not.
"""
from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from longshot import config, draws, ladder, method, missions, model, observe, predictions, priors
from longshot.types import LADDER, MISSIONS, ROWS, Fact, ObjectRecord, Row

M = method.load()
WINDOW = ("2027-01-10", "2027-02-20", 19.5, "pointable")


def fact(label, value, source="jpl-sbdb", lo=None, hi=None, unit="", kind="value", quality=None, ref=None):
    return Fact(label=label, value=value, lo=lo, hi=hi, unit=unit, kind=kind, source=source, ref=ref, quality=quality)


def make(key="k1", h=26.2, h_sigma=None, occ=1, arc=500, dv=5.0, dur=360, window=WINDOW,
         size=(), size_state=None, spin=(), spin_state=None, surface=(), surface_state=None,
         unchecked=None, designation=None, name=None, number=None, aliases=()) -> ObjectRecord:
    """A hand-made record. size, spin and surface are lists of facts; a row with value facts is measured."""
    unchecked = unchecked or {}

    def state(facts, given, label):
        if given:
            return given
        mine = [f for f in facts if f.label == label]
        if any(f.kind == "value" for f in mine):
            return "measured"
        if mine:
            return "limit"
        return "prior"

    size_facts = list(size)
    if h is not None:
        size_facts.append(fact("H", h, lo=None if h_sigma is None else round(h - h_sigma, 6),
                               hi=None if h_sigma is None else round(h + h_sigma, 6), unit="mag"))
    tracking = [fact("arc", arc, unit="d"), fact("first observed", "2020-01-01", unit="date"),
                fact("last observed", "2026-11-01", unit="date")]
    if occ is not None:
        tracking.insert(0, fact("condition code", occ))
    if window:
        tracking += [fact("window start", window[0], "jpl-nhats", unit="date"),
                     fact("window end", window[1], "jpl-nhats", unit="date"),
                     fact("window peak brightness", window[2], "jpl-nhats", unit="V mag"),
                     fact("window pointing", window[3], "jpl-nhats")]
    else:
        tracking.append(fact("next window", "none through 2045", "jpl-nhats"))
    surface_measured = any(f.label in ("class", "albedo") for f in surface)
    rows = {
        "reach": Row("measured", [fact("delta-v", dv, "jpl-nhats", unit="km/s"),
                                  fact("trip at lowest delta-v", dur, "jpl-nhats", unit="d")]),
        "tracking": Row("measured", tracking),
        "size": Row(state(size, size_state, "diameter"), size_facts, unchecked=list(unchecked.get("size", []))),
        "spin": Row(state(spin, spin_state, "period"), list(spin), unchecked=list(unchecked.get("spin", []))),
        "surface": Row(surface_state or ("measured" if surface_measured else "prior"), list(surface),
                       unchecked=list(unchecked.get("surface", []))),
        "push": Row("prior"),
    }
    for name, sources in unchecked.items():
        if rows[name].state == "prior":
            rows[name].state = "unchecked"
    return ObjectRecord(key=key, designation=designation or f"2099 {key.upper()}", name=name, number=number,
                        aliases=list(aliases), populations=["reachable"], data_date=config.DATA_DATE,
                        method=config.METHOD, rows=rows)


def diameter(value, lo=None, hi=None, source="ssodnet", **kw):
    return fact("diameter", value, source, lo, hi, "m", **kw)


def period(value, source="pravec", quality="3", lo=None, hi=None, kind="value", **kw):
    return fact("period", value, source, lo, hi, "h", kind=kind, quality=quality, **kw)


def run(record: ObjectRecord) -> ObjectRecord:
    return model.run_one(record, M)


def walk_strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from walk_strings(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from walk_strings(v)


class MethodFiles(unittest.TestCase):
    def test_loads_and_agrees_with_config(self):
        self.assertEqual(M.version, config.METHOD)
        self.assertEqual(M.n_draws, M.value["exports"]["min_draws"])
        self.assertIs(method.load(), M)
        for name in method.FILES:
            self.assertIsInstance(getattr(M, name), dict)

    def _copy(self, tmp, name, old, new):
        d = Path(tmp) / "v"
        shutil.copytree(config.METHOD_DIR, d)
        text = (d / name).read_text(encoding="utf-8")
        self.assertIn(old, text)
        (d / name).write_text(text.replace(old, new, 1), encoding="utf-8")
        return d

    def test_a_missing_key_fails_and_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._copy(tmp, "priors.toml", "default_sigma = 0.36", "default_sigma_gone = 0.36")
            with self.assertRaises(method.MethodError) as err:
                method.load(d)
            self.assertIn("priors.toml", str(err.exception))
            self.assertIn("h_uncertainty.default_sigma", str(err.exception))

    def test_a_missing_gate_field_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._copy(tmp, "missions.toml", "preset = 30.0", "preset_gone = 30.0")
            with self.assertRaises(method.MethodError) as err:
                method.load(d)
            self.assertIn("preset", str(err.exception))

    def test_a_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "v"
            shutil.copytree(config.METHOD_DIR, d)
            (d / "observe.toml").unlink()
            with self.assertRaises(method.MethodError):
                method.load(d)

    def test_another_method_version_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._copy(tmp, "observe.toml", 'method = "0.1"', 'method = "0.2"')
            with self.assertRaises(method.MethodError):
                method.load(d)

    def test_need_names_the_path(self):
        with self.assertRaises(method.MethodError) as err:
            method.need({"a": {"b": 1}}, "a", "c", where="x.toml")
        self.assertEqual(str(err.exception), "x.toml: missing a.c")


class JointDraws(unittest.TestCase):
    def test_same_key_same_draws(self):
        a, b = draws.for_record(make("same"), M), draws.for_record(make("same"), M)
        for col in ("cls", "pv", "d", "rho", "mass", "spin"):
            self.assertEqual(getattr(a, col), getattr(b, col), col)
        self.assertEqual(a.n, M.n_draws)

    def test_another_key_pairs_the_same_values_differently(self):
        # two objects with something measured are seeded by their keys
        cls = [fact("class", "Sq", "ssodnet", quality="Bus-DeMeo Spec")]
        a, b = draws.for_record(make("one", surface=cls), M), draws.for_record(make("two", surface=cls), M)
        self.assertEqual((a.seed_key, b.seed_key), ("one", "two"))
        self.assertNotEqual(a.d, b.d)
        self.assertEqual(sorted(a.spin), sorted(b.spin))   # the same spin categories, paired differently

    def test_with_nothing_measured_the_draws_depend_only_on_brightness(self):
        """DESIGN.md section 7: 'For an unobserved asteroid the tag depends only on its brightness.'"""
        a, b = draws.for_record(make("one"), M), draws.for_record(make("two"), M)
        self.assertEqual(a.seed_key, b.seed_key)
        self.assertNotIn("one", a.seed_key)
        for col in ("cls", "pv", "d", "rho", "mass", "spin"):
            self.assertEqual(getattr(a, col), getattr(b, col), col)
        ra, rb = run(make("one")), run(make("two"))
        self.assertEqual(ra.value, rb.value)                # the same price tag, sentence for sentence
        self.assertEqual(ra.summary, rb.summary)
        self.assertNotEqual(draws.for_record(make("one", h=26.3), M).d, a.d)
        self.assertNotEqual(draws.for_record(make("one", h_sigma=0.5), M).d, a.d)
        # a size, a class, a reflectivity or a density makes it its own object again; a period does not touch the rock
        self.assertEqual(draws.for_record(make("one", size=[diameter(20.0, 15.0, 25.0)]), M).seed_key, "one")
        spun = draws.for_record(make("one", spin=[period(3.0)]), M)
        self.assertEqual((spun.d, spun.mass, spun.cls), (a.d, a.mass, a.cls))

    def test_the_method_version_is_in_the_seed(self):
        self.assertIn(M.version, draws.seed("k", M, "draws"))
        self.assertNotEqual(draws.seed("k", M, "draws"), draws.seed("k", M, "value"))

    def test_reflectivity_follows_the_spitzer_table(self):
        d = draws.for_record(make(), M)
        refl = M.priors["reflectivity"]
        q = priors.quantiles(d.pv)
        for name, p in (("q05", 0.05), ("q25", 0.25), ("q50", 0.5), ("q75", 0.75), ("q95", 0.95)):
            self.assertAlmostEqual(q[name] / refl["pv"][refl["p"].index(p)], 1.0, delta=0.01, msg=name)
        self.assertAlmostEqual(min(d.pv), refl["pv"][0], places=12)   # beyond its ends the table gives its end value
        self.assertAlmostEqual(max(d.pv), refl["pv"][-1], places=12)

    def test_sizes_match_the_table_in_the_method_document(self):
        # docs/method.md section 1, size in metres at a given H with sigma 0.36
        for h, want in ((22, (62, 83, 103, 130, 230)), (26.2, (8.9, 12, 15, 19, 33)), (30, (1.5, 2.1, 2.6, 3.3, 5.8))):
            q = run(make(f"h{h}", h=h)).summary["size_m"]
            for got, w in zip((q["q05"], q["q25"], q["q50"], q["q75"], q["q95"]), want):
                self.assertAlmostEqual(got / w, 1.0, delta=0.05, msg=f"H {h}")    # the table is to two figures

    def test_spin_shares_are_the_central_values(self):
        for band, h in (("under_20", 19.0), ("20_22", 21.0), ("22_24", 23.0), ("24_26", 25.0), ("26_28", 27.0),
                        ("28_up", 29.0)):
            s = run(make(f"s{band}", h=h)).summary
            self.assertEqual(s["band"], band)
            central = [M.priors["spin"]["bands"][band][i]["central"] for i in M.priors["spin"]["ids"]]
            for got, want in zip([s["p_fast_2_2h"], s["p_under_1h"], s["p_under_10min"]], central):
                self.assertAlmostEqual(got, want, delta=0.5 / M.n_draws + 1e-9)       # to one draw in n
        # 1 of 1,143 measured near-Earth asteroids of H under 20 turns in under ten minutes: a share, not zero
        rare = M.priors["spin"]["bands"]["under_20"]["under_10min"]
        self.assertEqual(rare["central"], 0.0009)
        self.assertIn("1 of 1143", rare["central_from"])
        self.assertGreater(run(make("rare", h=19.0)).summary["p_under_10min"], 0.0)

    def test_class_shares_return_the_central_shares(self):
        for band, h in (("22_24", 23.0), ("26_28", 27.0)):
            got = run(make(f"c{band}", h=h)).summary["class"]
            want = M.priors["class"]["bands"][band]["central"]
            self.assertAlmostEqual(sum(got.values()), 1.0, places=6)
            for c in priors.CLASSES:
                self.assertAlmostEqual(got[c], want[c], delta=0.02, msg=f"{band} {c}")

    def test_band_edges(self):
        self.assertEqual(priors.band_of(M, 19.99), "under_20")
        self.assertEqual(priors.band_of(M, 20.0), "20_22")
        self.assertEqual(priors.band_of(M, 28.0), "28_up")
        self.assertIsNone(priors.band_of(M, None))

    def test_h_sigma_comes_from_the_h_fact_or_the_default(self):
        self.assertEqual(draws.inputs(make(h=25.0), M).h_sigma, M.priors["h_uncertainty"]["default_sigma"])
        inp = draws.inputs(make(h=25.0, h_sigma=0.5), M)
        self.assertAlmostEqual(inp.h_sigma, 0.5)
        wide = run(make("w", h=25.0, h_sigma=0.8)).summary["size_m"]
        narrow = run(make("w", h=25.0, h_sigma=0.1)).summary["size_m"]
        self.assertGreater(wide["q95"] / wide["q05"], narrow["q95"] / narrow["q05"])

    def test_a_measured_size_narrows_the_range(self):
        prior = run(make("n", h=22.7)).summary["size_m"]
        measured = run(make("n", h=22.7, size=[diameter(60.0, 50.0, 70.0)])).summary["size_m"]
        self.assertLess(measured["q95"] - measured["q05"], 0.5 * (prior["q95"] - prior["q05"]))
        # 50 to 70 is the stated one-sigma range, not the whole range: 5% to 95% is 1.645 sigma each side
        self.assertAlmostEqual(measured["q05"], 60.0 - 16.45, delta=0.2)
        self.assertAlmostEqual(measured["q95"], 60.0 + 16.45, delta=0.2)
        d = draws.for_record(make("n", h=22.7, size=[diameter(60.0, 50.0, 70.0)]), M)
        inside = sum(1 for x in d.d if 50.0 <= x <= 70.0) / d.n
        self.assertAlmostEqual(inside, 0.683, delta=0.005)             # one sigma holds 68%, and no draw is clamped
        self.assertNotIn(50.0, d.d)
        self.assertNotIn(70.0, d.d)
        self.assertGreater(min(d.d), 0.0)
        # reflectivity then follows from size and H (priors.toml [joint] step 3)
        self.assertAlmostEqual(priors.quantiles(d.pv)["q50"], priors.implied_reflectivity(M, 22.7, 60.0), delta=0.03)

    def test_a_measured_size_with_no_stated_error_is_drawn_within_a_factor_of_two(self):
        """missions.toml [rules.decide].no_range_factor: two sigma of a log-normal draw."""
        factor = M.missions["rules"]["decide"]["no_range_factor"]
        d = draws.for_record(make(h=24.0, size=[diameter(33.0)]), M)
        v = sorted(d.d)
        self.assertAlmostEqual(priors.quantile(v, 0.5), 33.0, delta=0.05)
        inside = sum(1 for x in v if 33.0 / factor <= x <= 33.0 * factor) / d.n
        self.assertAlmostEqual(inside, 0.954, delta=0.003)
        self.assertEqual(d.inputs.size.reach(2.0), (33.0 / factor, 33.0 * factor))
        self.assertFalse(d.inputs.size.ranged)

    def test_an_uneven_range_is_drawn_on_both_sides(self):
        d = draws.for_record(make(h=18.0, size=[diameter(2002.0, 1481.0, 3183.0, "spitzer")]), M)
        below = sum(1 for x in d.d if x < 2002.0)
        self.assertAlmostEqual(below / d.n, 0.5, delta=0.01)
        self.assertLess(min(d.d), 1481.0)                              # the stated ends are one sigma, not walls
        self.assertGreater(max(d.d), 3183.0)
        self.assertAlmostEqual(sum(1 for x in d.d if x > 3183.0) / d.n, 0.159, delta=0.005)
        lo, hi = d.inputs.size.reach(2.0)
        self.assertEqual((lo, hi), (2002.0 - 2 * 521.0, 2002.0 + 2 * 1181.0))

    def test_a_measured_class_conditions_reflectivity_and_size(self):
        r = run(make("s", h=26.2, surface=[fact("class", "Sq", "ssodnet", quality="Bus-DeMeo Spec")]))
        # a label from a spectrum is wrong, on S/Q against the rest, in 12.5 of 100 draws
        rate = M.priors["class"]["label_error"]["spectrum"]
        self.assertEqual(r.summary["class"]["S"], 1.0 - rate)
        self.assertTrue(all(r.summary["class"][c] > 0 for c in ("C", "X", "other")))
        table = M.priors["reflectivity"]["by_class"]["S"]["pv"]
        self.assertAlmostEqual(r.summary["reflectivity"]["q50"], table[10], delta=0.02)
        plain = run(make("s", h=26.2)).summary["size_m"]
        self.assertLess(r.summary["size_m"]["q95"], plain["q95"])        # no dark, large cases left
        self.assertIsNone(r.rows["surface"].prior)                       # the row is measured: no prior on it
        self.assertIn("class S", r.rows["size"].prior["basis"])

    def test_a_class_label_can_be_wrong_at_the_stated_rate(self):
        """priors.toml [class.label_error]: 21% for a label from colours, 12.5% for any other, none for a sample."""
        rates = M.priors["class"]["label_error"]
        self.assertEqual((rates["colour"], rates["spectrum"]), (0.21, 0.125))
        colour = draws.for_record(make("c", surface=[fact("class", "S", "ssodnet", quality="Sergeyev Phot VIS")]), M)
        self.assertEqual(colour.inputs.cls_error, 0.21)
        self.assertAlmostEqual(colour.cls.count("S") / colour.n, 0.79, delta=1e-9)
        # the other way round: a label that is not S is S in that share of draws
        dark = draws.for_record(make("d", surface=[fact("class", "C", "ssodnet", quality="Sergeyev Phot VIS")]), M)
        self.assertEqual({c: dark.cls.count(c) / dark.n for c in priors.CLASSES},
                         {"S": 0.21, "C": 0.79, "X": 0.0, "other": 0.0})
        # a spectrum beside the colours backs the label: the smaller rate applies
        both = draws.inputs(make("b", surface=[fact("class", "S", "ssodnet", quality="Sergeyev Phot VIS"),
                                               fact("class", "Sq", "jpl-sbdb", quality="SMASSII")]), M)
        self.assertEqual(both.cls_error, 0.125)
        # a mislabelled draw takes the reflectivity of the class it really is
        s_like = [pv for c, pv in zip(dark.cls, dark.pv) if c == "S"]
        c_like = [pv for c, pv in zip(dark.cls, dark.pv) if c == "C"]
        self.assertGreater(sorted(s_like)[len(s_like) // 2], 2 * sorted(c_like)[len(c_like) // 2])
        # with a measured reflectivity the wrong-side class follows the weights in that reflectivity bin
        measured = draws.for_record(make("m", h=24.0, surface=[
            fact("class", "S", "ssodnet", quality="Sergeyev Phot VIS"),
            fact("albedo", 0.05, "ssodnet", 0.04, 0.06, quality="NEATM")]), M)
        wrong = [c for c in measured.cls if c != "S"]
        self.assertAlmostEqual(len(wrong) / measured.n, 0.21, delta=1e-9)
        self.assertGreater(wrong.count("C"), wrong.count("other"))       # dark and not S is mostly C
        # an asteroid a spacecraft brought a sample back from has no label error
        bennu = draws.for_record(make("b", h=20.2, designation="1999 RQ36", name="Bennu", number=101955,
                                      surface=[fact("class", "B", "ssodnet", quality="Mahlke Spec VISNIR")]), M)
        self.assertEqual(bennu.inputs.cls_error, 0.0)
        self.assertEqual(set(bennu.cls), {"C"})

    def test_a_density_on_file_replaces_the_class_range(self):
        on_file = fact("density", 1194.0, "jpl-sbdb", unit="kg/m^3")
        r = make("rho", h=20.2, size=[diameter(488.0, 469.0, 507.0)])
        r.rows["push"] = Row("measured", [fact("A2", -4.6e-14, lo=-4.7e-14, hi=-4.5e-14), on_file])
        d = draws.for_record(r, M)
        self.assertEqual(set(d.rho), {1194.0})
        q = run(r).summary["mass_t"]
        self.assertAlmostEqual(q["q50"] / priors.mass_t(488.0, 1194.0), 1.0, delta=0.01)      # about 73 million t
        self.assertLess(q["q95"] / q["q05"], 1.6)                    # from the size error alone
        # a density that is on file and not used (computed) does not count
        r.rows["push"].facts[1] = Fact(**{**on_file.__dict__, "used": False})
        self.assertIsNone(draws.inputs(r, M).density)

    def test_class_letters_map_to_the_four_groups(self):
        for label, want in (("S", "S"), ("Q", "S"), ("Sq", "S"), ("B", "C"), ("Ch", "C"), ("Xk", "X"), ("M", "X"),
                            ("V", "other"), ("L", "other"), ("U", None), ("CX", None), ("", None)):
            self.assertEqual(draws.class_group(label), want, label)

    def test_a_measured_reflectivity_conditions_size_and_class(self):
        dark = run(make("a", h=24.0, surface=[fact("albedo", 0.05, "ssodnet", 0.04, 0.06, quality="NEATM")]))
        plain = run(make("a", h=24.0))
        self.assertGreater(dark.summary["size_m"]["q50"], 1.5 * plain.summary["size_m"]["q50"])
        self.assertGreater(dark.summary["class"]["C"], 2 * plain.summary["class"]["C"])
        # 0.04 to 0.06 is one sigma: 5% to 95% of the draws is 1.645 sigma each side
        self.assertAlmostEqual(dark.summary["reflectivity"]["q95"], 0.05 + 1.645 * 0.01, delta=0.0005)
        self.assertAlmostEqual(dark.summary["reflectivity"]["q05"], 0.05 - 1.645 * 0.01, delta=0.0005)

    def test_a_computed_reflectivity_is_not_a_measurement(self):
        r = make(h=24.0, surface=[fact("albedo", 0.05, "ssodnet", 0.04, 0.06, quality="Computed")],
                 surface_state="prior")
        self.assertIsNone(draws.inputs(r, M).albedo)

    def test_a_usable_period_replaces_the_spin_prior(self):
        fast = run(make("p", h=27.0, spin=[period(0.05)])).summary
        slow = run(make("p", h=27.0, spin=[period(12.0)])).summary
        self.assertEqual((fast["p_fast_2_2h"], fast["p_under_1h"], fast["p_under_10min"]), (1.0, 1.0, 1.0))
        self.assertEqual((slow["p_fast_2_2h"], slow["p_under_1h"], slow["p_under_10min"]), (0.0, 0.0, 0.0))
        mid = run(make("p", h=27.0, spin=[period(0.5)])).summary
        self.assertEqual((mid["p_fast_2_2h"], mid["p_under_1h"], mid["p_under_10min"]), (1.0, 1.0, 0.0))

    def test_an_ungraded_period_counts_and_a_low_grade_does_not(self):
        self.assertIsNotNone(draws.inputs(make(spin=[period(3.0, "ssodnet", None)]), M).period)
        self.assertIsNotNone(draws.inputs(make(spin=[period(3.0, quality="2-")]), M).period)
        low = make(h=22.9, spin=[period(10.0, "pravec", "1"), period(10.0, "lcdb", "1+"), period(10.0, "jpl-sbdb", None)],
                   spin_state="prior")
        inp = draws.inputs(low, M)
        self.assertIsNone(inp.period)
        # the fact a sentence may name is never the inference-only source's own, whatever its grade
        self.assertEqual((inp.period_unreliable.source, inp.period_unreliable.quality), ("pravec", "1"))
        self.assertTrue(inp.period_unreliable_public)
        alone = draws.inputs(make(h=22.9, spin=[period(10.0, "lcdb", "1+")], spin_state="prior"), M)
        self.assertFalse(alone.period_unreliable_public)                  # only the inference source has it
        central = M.priors["spin"]["bands"]["22_24"]["under_2_2h"]["central"]
        self.assertEqual(run(low).summary["p_fast_2_2h"], central)        # the prior for H 22 to 24 stands

    def test_a_limit_removes_the_draws_that_break_it(self):
        r = make("l", h=24.0, size=[diameter(30.0, kind="upper")])
        self.assertEqual(r.rows["size"].state, "limit")
        d = draws.for_record(r, M)
        self.assertLess(d.n, M.n_draws)
        self.assertLessEqual(max(d.d), 30.0)
        r = make("l", h=27.0, spin=[period(1.5, "ssodnet", None, kind="lower")])
        self.assertEqual(r.rows["spin"].state, "limit")
        s = run(r).summary
        self.assertEqual(s["p_under_1h"], 0.0)                            # everything under an hour is ruled out
        self.assertGreater(s["p_fast_2_2h"], 0.0)                         # 1 h to 2.2 h is not
        # a limit on the period re-deals the spin column and leaves the rock alone: the same sizes, masses and tag
        plain, limited = make("l", h=27.0), make("l", h=27.0, spin=[period(1.5, "ssodnet", None, kind="lower")])
        a, b = draws.for_record(plain, M), draws.for_record(limited, M)
        self.assertEqual((a.n, a.d, a.mass, a.cls), (b.n, b.d, b.mass, b.cls))
        self.assertEqual(run(plain).value, run(limited).value)
        kept = [c for c in a.spin if c >= 2]                              # 1 h or slower
        self.assertAlmostEqual(b.spin.count(3) / b.n, kept.count(3) / len(kept), delta=1 / b.n + 1e-9)

    def test_no_h_means_no_draws_and_no_priors(self):
        r = run(make("z", h=None, occ=9, window=None, unchecked={"size": ["ssodnet"]}))
        self.assertIsNone(draws.for_record(make("z", h=None), M))
        self.assertEqual(r.summary, {})
        self.assertEqual(r.value, {})
        for name in ("size", "spin", "surface"):
            self.assertIsNone(r.rows[name].prior)

    def test_priors_go_on_unmeasured_rows_only(self):
        r = run(make("u", h=25.0, size=[diameter(40.0, 30.0, 50.0)], unchecked={"spin": ["ssodnet"]}))
        self.assertIsNone(r.rows["size"].prior)
        self.assertEqual(r.rows["spin"].state, "unchecked")
        spin = r.rows["spin"].prior
        self.assertEqual(spin["p_fast_2_2h"], r.summary["p_fast_2_2h"])
        self.assertEqual(spin["range"]["p_fast_2_2h"], [0.70, 0.89])
        self.assertIsInstance(spin["basis"], str)
        surface = r.rows["surface"].prior
        self.assertEqual(set(surface["shares"]), set(priors.CLASSES))
        self.assertIn("basis", surface)
        size = run(make("u2", h=25.0)).rows["size"].prior
        self.assertEqual(set(size), {"q05", "q25", "q50", "q75", "q95", "unit", "basis"})
        self.assertEqual(size["unit"], "m")
        self.assertTrue(size["q05"] < size["q25"] < size["q50"] < size["q75"] < size["q95"])
        self.assertIn("H 25 or fainter", size["basis"])                   # fainter than H 25 is extrapolation

    def test_summary_shape(self):
        s = run(make()).summary
        for k in ("size_m", "mass_t"):
            self.assertEqual(set(s[k]), {"q05", "q25", "q50", "q75", "q95"})
        for k in ("p_fast_2_2h", "p_under_1h", "p_under_10min"):
            self.assertTrue(0.0 <= s[k] <= 1.0)
        self.assertEqual(set(s["class"]), set(priors.CLASSES))

    def test_an_undecided_mass_rests_on_an_estimate_unless_its_density_is_measured(self):
        """docs/design.md section 3: a mass is measured only when its diameter and its density both are. An undecided
        mass condition says so in its basis: an honest page never calls a chance from a class density measured."""
        r = run(make("m18", h=24.5, size=[diameter(18.0, 16.0, 20.0)]))
        (g,) = [g for g in r.missions["capture"]["gates"] if g["id"] == "mass"]
        self.assertEqual((g["status"], g["basis"]), ("untested", "prior"))
        r = make("m18rho", h=24.5, size=[diameter(18.0, 16.0, 20.0)])
        r.rows["push"] = Row("measured", [fact("A2", -4.6e-14, lo=-4.7e-14, hi=-4.5e-14),
                                          fact("density", 2000.0, "jpl-sbdb", unit="kg/m^3")])
        (g,) = [g for g in run(r).missions["capture"]["gates"] if g["id"] == "mass"]
        self.assertEqual((g["status"], g["basis"]), ("untested", "measured"))
        # across every hand-made case: an undecided condition marked measured rests on measured inputs only
        for rec in (run(make(h=h, size=sz)) for h in (22.0, 26.0, 29.0) for sz in ((), [diameter(9.0, 8.0, 10.0)])):
            for mi in rec.missions.values():
                for g in mi["gates"]:
                    if g["status"] == "untested" and g["basis"] == "measured":
                        self.assertNotEqual(g["id"], "mass", rec.key)        # no density on file in these

    def test_mass_follows_size_and_density(self):
        d = draws.for_record(make(), M)
        lo, hi = priors.density_ends(M)
        self.assertEqual((lo, hi), (900, 7500))
        for dm, rho, mass in list(zip(d.d, d.rho, d.mass))[:200]:
            self.assertTrue(lo <= rho <= hi)
            self.assertAlmostEqual(mass, priors.mass_t(dm, rho), delta=1e-9 * mass)


class Missions(unittest.TestCase):
    def test_shape_and_probabilities(self):
        for r in (make("a", h=22.0), make("b", h=29.0, occ=7), make("c", h=25.0, spin=[period(5.0)]),
                  make("d", h=None)):
            run(r)
            self.assertEqual(tuple(r.missions), MISSIONS)
            for mission in MISSIONS:
                mi = r.missions[mission]
                self.assertIn(mi["status"], ("pass", "fail", "untested"))
                want = [g["id"] for g in M.missions[mission]["gates"]]
                self.assertEqual([g["id"] for g in mi["gates"]], want)
                for g in mi["gates"] + [mi]:
                    if g["p"] is not None:
                        self.assertTrue(0.0 <= g["p"] <= 1.0)
                    if g["status"] == "pass":
                        self.assertEqual(g["p"], 1.0)
                    if g["status"] == "fail":
                        self.assertEqual(g["p"], 0.0)
                    if g["status"] == "untested" and g["p"] is not None:
                        self.assertTrue(0.0 < g["p"] < 1.0)              # never stored as 0 or 1
                for g in mi["gates"]:
                    self.assertEqual(set(g), {"id", "label", "status", "p", "basis", "text"})
                    self.assertIn(g["basis"], ("measured", "prior"))
                    self.assertIsInstance(g["text"], str)

    def test_an_untested_chance_is_never_zero_or_one(self):
        """missions.toml [rules].gate: a share of 0 or 1 of the draws is held at 1/n and 1 - 1/n."""
        n = M.n_draws
        tiny = run(make("tiny", h=31.4))                 # no draw is 30 m or wider; every draw is 10 m or smaller
        gates = {g["id"]: g for g in tiny.missions["surface"]["gates"]}
        self.assertEqual((gates["size"]["status"], gates["size"]["p"]), ("untested", round(1 / n, 4)))
        self.assertEqual(tiny.missions["surface"]["p"], round(1 / n, 4))
        capture = tiny.missions["capture"]
        self.assertEqual((capture["status"], capture["p"]), ("untested", round(1 - 1 / n, 4)))
        self.assertEqual(missions.bounded(0.0, n), 0.0005)
        self.assertEqual(missions.bounded(1.0, n), 0.9995)
        self.assertEqual(missions.bounded(0.42, n), 0.42)
        # so the object is ranked: an untested mission always has something an observation would settle
        self.assertIsNotNone(tiny.observe)
        self.assertGreater(tiny.observe["gain"], 0.0)
        for r in (tiny, run(make("big", h=17.0))):
            for mission in MISSIONS:
                mi = r.missions[mission]
                if mi["status"] == "untested":
                    self.assertNotIn(mi["p"], (0.0, 1.0))

    def test_a_gate_text_says_only_what_the_rows_do_not(self):
        """DESIGN.md section 5: the orbit code, the size range and the mass range are in their rows."""
        r = run(make(h=26.2))
        for mission in MISSIONS:
            self.assertEqual([g["text"] for g in r.missions[mission]["gates"]], [""] * 3)
        decided = run(make(h=20.05, occ=0, size=[diameter(400.0, 350.0, 450.0, "jpl-sbdb")], spin=[period(3.725)]))
        self.assertEqual([g["text"] for g in decided.missions["surface"]["gates"]], ["", "", ""])
        for rec in (r, decided):
            for g in (g for mi in rec.missions.values() for g in mi["gates"]):
                self.assertNotIn("Orbit code", g["text"])
                self.assertNotIn("From brightness", g["text"])

    def test_a_measured_failing_gate_fails_the_mission(self):
        r = run(make(h=20.0, occ=0, size=[diameter(400.0, 350.0, 450.0, "jpl-sbdb")], spin=[period(0.5)]))
        surface = r.missions["surface"]
        gates = {g["id"]: g for g in surface["gates"]}
        self.assertEqual((gates["spin"]["status"], gates["spin"]["p"], gates["spin"]["basis"]), ("fail", 0.0, "measured"))
        self.assertEqual((gates["size"]["status"], gates["size"]["p"]), ("pass", 1.0))
        self.assertEqual((surface["status"], surface["p"]), ("fail", 0.0))
        capture = {g["id"]: g for g in r.missions["capture"]["gates"]}
        self.assertEqual(capture["size"]["status"], "fail")
        self.assertEqual(capture["mass"]["status"], "fail")

    def test_a_bad_orbit_fails_both(self):
        r = run(make(h=24.0, occ=6))
        for mission in MISSIONS:
            self.assertEqual((r.missions[mission]["status"], r.missions[mission]["p"]), ("fail", 0.0))
        self.assertEqual(run(make(h=24.0, occ=5)).missions["surface"]["gates"][0]["status"], "pass")

    def test_every_gate_measured_is_a_pass(self):
        r = run(make(h=20.05, occ=0, size=[diameter(400.0, 350.0, 450.0, "jpl-sbdb")], spin=[period(3.725)]))
        self.assertEqual((r.missions["surface"]["status"], r.missions["surface"]["p"]), ("pass", 1.0))
        self.assertTrue(all(g["basis"] == "measured" for g in r.missions["surface"]["gates"]))
        small = run(make(h=28.1, occ=1, size=[diameter(4.0, 3.5, 4.5)]))
        self.assertEqual(small.missions["capture"]["status"], "pass")     # 5 m of solid iron is 490 t
        self.assertIn("490 t", small.missions["capture"]["gates"][2]["text"])
        self.assertIn("5 m at 7,500 kg/m³", small.missions["capture"]["gates"][2]["text"])     # 4 m plus two sigma

    def test_a_range_across_the_line_is_untested_from_the_measurement(self):
        r = run(make(h=24.0, size=[diameter(30.0, 20.0, 40.0)], spin=[period(5.0)]))
        g = r.missions["surface"]["gates"][1]
        self.assertEqual((g["status"], g["basis"]), ("untested", "measured"))
        self.assertAlmostEqual(g["p"], 0.5, delta=0.02)
        self.assertEqual(r.missions["surface"]["p"], g["p"])
        self.assertEqual(g["text"], "The measurement is within 2σ of 30 m, so it does not decide.")

    def test_one_sigma_is_not_the_whole_range(self):
        """missions.toml [rules.decide]: a gate is decided only when two sigma clears the line."""
        def size_gate(*d, mission="surface", h=24.0):
            return run(make(h=h, size=[diameter(*d)])).missions[mission]["gates"][1]
        # 2016 YC8's case: 41 m (30 to 52). The low end of the stated range sits exactly on 30 m.
        g = size_gate(41.0, 30.0, 52.0)
        self.assertEqual((g["status"], g["basis"]), ("untested", "measured"))
        self.assertAlmostEqual(g["p"], 0.84, delta=0.01)                  # one sigma above the line
        self.assertEqual(size_gate(41.0, 36.0, 46.0)["status"], "pass")    # 2.2 sigma clear
        self.assertEqual(size_gate(41.0, 35.0, 47.0)["status"], "untested")   # 1.83 sigma
        self.assertEqual(size_gate(20.0, 16.0, 24.0)["status"], "fail")
        self.assertEqual(size_gate(20.0, 14.0, 26.0)["status"], "untested")
        # with no stated error the line must be a factor of 2 away
        self.assertEqual(size_gate(70.0)["status"], "pass")
        g = size_gate(55.0)
        self.assertEqual(g["status"], "untested")
        self.assertEqual(g["text"], "The source gives no error, and the value is within a factor of 2 of 30 m.")
        # 2016 RD34's case: 6 m with no range does not decide "Diameter ≤ 10 m", nor the mass gate
        capture = run(make(h=27.6, size=[diameter(6.0, source="jpl-sbdb")])).missions["capture"]
        self.assertEqual([g["status"] for g in capture["gates"]], ["pass", "untested", "untested"])
        self.assertEqual(capture["status"], "untested")
        # 2012 XB112's case: 2.5 m is a factor of 4 under 10 m, and 5 m of solid iron is under the mass ceiling
        self.assertEqual(run(make(h=29.7, size=[diameter(2.5, source="jpl-sbdb")])).missions["capture"]["status"], "pass")
        # a period with a stated error is held to the same two sigma; one with none decides as it stands
        def spin_gate(*p_):
            return run(make(h=24.0, spin=[period(*p_)])).missions["surface"]["gates"][2]
        self.assertEqual(spin_gate(2.4, "ssodnet", None, 2.25, 2.55)["status"], "untested")
        self.assertEqual(spin_gate(2.4, "ssodnet", None, 2.35, 2.45)["status"], "pass")
        self.assertEqual(spin_gate(2.4, "ssodnet", None)["status"], "pass")

    def test_a_size_brighter_than_a_perfect_reflector_does_not_decide(self):
        """missions.toml [rules.size].max_implied_reflectivity, with H allowed its own error."""
        # 12 m at H 24.0 implies a reflectivity of 3: no H within two sigma brings it under 1
        r = run(make(h=24.0, size=[diameter(12.0, 10.0, 14.0)]))
        self.assertIsNone(draws.inputs(r, M).size)
        self.assertEqual(r.missions["surface"]["gates"][1]["status"], "untested")
        self.assertIn("implies a reflectivity of", r.rows["size"].conflicts[0])
        # Kamoʻoalewa: 18 m at H 24.31 implies 1.03, and 0.53 at H two sigma fainter. It stands.
        kamo = draws.inputs(make(h=24.31, size=[diameter(18.0, 16.0, 20.0, "curated")]), M)
        self.assertIsNotNone(kamo.size)
        self.assertIsNone(kamo.size_rejected)

    def test_periods_on_both_sides_of_the_line_decide_nothing(self):
        """missions.toml [rules.conflict]: 2013 NJ, 250 h in three sources and 2.02 h in a fourth."""
        conflict = "250 h (Pravec's table, U 3; JPL's database) against 2.02 h (SsODNet, Thirouin+2016b, U 2)."
        r = make("nj", h=21.9, occ=0, spin=[period(250.0, "pravec", "3"), period(2.02, "ssodnet", "2", 1.97, 2.07),
                                           period(250.0, "jpl-sbdb", None)])
        r.rows["spin"].conflicts = [conflict]
        run(r)
        g = r.missions["surface"]["gates"][2]
        self.assertEqual((g["status"], g["basis"]), ("untested", "prior"))
        self.assertEqual(g["text"], "The sources' periods fall on both sides of 2.2 h, so none decides.")
        central = M.priors["spin"]["bands"]["20_22"]["under_2_2h"]["central"]
        self.assertAlmostEqual(g["p"], 1.0 - central, places=6)           # the prior for its brightness, not 100%
        self.assertNotIn(conflict, r.ladder[2]["text"])                   # the spin row names both periods, once
        self.assertIn("Sources disagree on its period", r.ladder[2]["text"])
        self.assertIn("sources disagree on it", r.ladder[4]["text"])
        self.assertNotIn("not measured", r.ladder[4]["text"])
        # a disagreement on one side of the line still decides: 1998 KY26, 5.35 against 10.7 minutes
        r = make("ky", h=25.6, occ=0, spin=[period(0.089193, "ssodnet", None), period(0.089193, "jpl-sbdb", None),
                                           period(0.1784, "lcdb", "3")])
        r.rows["spin"].conflicts = ["0.08919 h (SsODNet; JPL's database) against a different period on file in "
                                    "the lightcurve database, not shown here."]
        run(r)
        self.assertEqual(r.missions["surface"]["gates"][2]["status"], "fail")
        self.assertEqual(r.summary["p_under_10min"], 1.0)                 # the newer period: once in 5.35 minutes
        self.assertIn("400–1,100 times gravity", r.ladder[2]["text"])
        self.assertIn("Sources disagree on the period.", r.ladder[2]["text"])
        # a stated range that crosses the line counts as being on both sides: 2013 YS2
        r = make("ys", h=21.0, spin=[period(3.95, "pravec", "2"), period(2.4, "ssodnet", None, 1.9, 2.9)])
        r.rows["spin"].conflicts = ["x against y."]
        self.assertEqual(run(r).missions["surface"]["gates"][2]["status"], "untested")

    def test_a_body_that_no_longer_exists_fails_everything_with_the_reason(self):
        r = make("tc3", h=30.7, occ=4, window=None, spin=[period(0.0269, "jpl-sbdb", None)])
        r.gone = {"date": "2008-10-07", "text": "Entered Earth's atmosphere on 7 October 2008.", "evidence": "x"}
        run(r)
        for mission in MISSIONS:
            mi = r.missions[mission]
            self.assertEqual((mi["status"], mi["p"]), ("fail", 0.0))
            self.assertEqual([(g["status"], g["text"]) for g in mi["gates"]], [("fail", r.gone["text"])])
        self.assertIsNone(r.observe)
        self.assertEqual(r.value, {})
        self.assertEqual(r.ladder[0]["text"], r.gone["text"])
        self.assertEqual({x["text"] for x in r.ladder[1:]}, {"It no longer exists."})
        self.assertEqual(observe.ranked([r]), [])

    def test_untested_counts_the_joint_draws_and_does_not_multiply(self):
        r = make("joint", h=28.2)                       # capture: size and mass both open, and tightly linked
        d = draws.for_record(r, M)
        run(r)
        capture = r.missions["capture"]
        size, mass = capture["gates"][1], capture["gates"][2]
        self.assertEqual((size["status"], mass["status"], capture["status"]), ("untested", "untested", "untested"))
        both = sum(1 for dm, t in zip(d.d, d.mass) if dm <= 10.0 and t <= 1300.0) / d.n
        self.assertAlmostEqual(capture["p"], both, places=4)
        self.assertLessEqual(capture["p"], min(size["p"], mass["p"]) + 1e-9)
        self.assertGreater(capture["p"], size["p"] * mass["p"] + 0.005)   # the product would be too low

    def test_an_unreliable_period_leaves_the_gate_untested_and_says_so(self):
        r = run(make(h=22.9, occ=0, spin=[period(10.0, "pravec", "1"), period(10.0, "lcdb", "1+")], spin_state="prior"))
        g = r.missions["surface"]["gates"][2]
        self.assertEqual((g["status"], g["basis"]), ("untested", "prior"))
        central = M.priors["spin"]["bands"]["22_24"]["under_2_2h"]["central"]
        self.assertAlmostEqual(g["p"], 1.0 - central, places=6)           # the prior for H 22 to 24
        self.assertEqual(g["text"], "The only period on file is graded unreliable, so it does not decide.")
        self.assertAlmostEqual(r.missions["surface"]["p"], 1.0 - central, delta=0.005)
        for text in walk_strings([r.missions, r.ladder]):                 # the row prints the value; nothing repeats it
            self.assertNotIn("U 1+", text)

    def test_not_checked_is_never_called_not_measured(self):
        """A source not checked is named once, in its row (docs/design.md section 3). The gates and the ladder
        rest on the estimate: they never say "not measured", and they do not name the source again."""
        r = run(make(h=25.0, unchecked={"size": ["ssodnet", "spitzer"], "spin": ["ssodnet"]}))
        self.assertEqual(r.rows["size"].unchecked, ["ssodnet", "spitzer"])     # the row keeps the sources
        self.assertEqual(r.rows["spin"].unchecked, ["ssodnet"])
        for mission in MISSIONS:
            for g in r.missions[mission]["gates"]:
                if g["id"] == "findable":
                    continue
                self.assertEqual((g["status"], g["basis"]), ("untested", "prior"), g["id"])
                self.assertEqual(g["text"], "", g["id"])
        for text in walk_strings([r.missions, r.ladder, r.observe]):
            self.assertNotIn("not measured", text.lower())
            self.assertNotIn("not checked", text.lower())
            self.assertNotIn("SsODNet", text)
        self.assertEqual(r.observe["unchecked"], ["ssodnet"])                 # the entry can say where to look first
        self.assertIn("estimated", r.ladder[2]["text"])
        # with every source checked the gates say the same: nothing the row does not
        checked = run(make(h=25.0))
        self.assertEqual(checked.missions["surface"]["gates"][1]["text"], "")

    def test_the_last_rung_calls_an_unchecked_spin_estimated(self):
        # small, so the answer "depends on" the spin; big with a measured size, so it is set beside the sampled three
        small = run(make(h=25.0, unchecked={"spin": ["ssodnet"]})).ladder[4]["text"]
        self.assertIn("Whether it could be sampled also depends on its spin, which is estimated.", small)
        big = run(make(h=19.5, size=[diameter(500.0, 450.0, 550.0)], unchecked={"spin": ["ssodnet"]})).ladder[4]["text"]
        self.assertIn("turn once in 4.3–12.1 h. Its own spin is estimated.", big)
        for text in (small, big):
            self.assertNotIn("not measured", text)
            self.assertNotIn("SsODNet", text)                             # the spin row names it, once
        # with every source checked the same rungs say the same: an estimate either way
        self.assertIn("Whether it could be sampled also depends on its spin, which is estimated.", run(make(h=25.0)).ladder[4]["text"])

    def test_no_h_gives_untested_with_no_probability(self):
        r = run(make(h=None, occ=2))
        surface = r.missions["surface"]
        self.assertEqual((surface["status"], surface["p"]), ("untested", None))
        self.assertEqual([g["p"] for g in surface["gates"]], [1.0, None, None])
        self.assertEqual(run(make(h=None, occ=9)).missions["surface"]["p"], 0.0)

    def test_a_size_that_implies_an_impossible_reflectivity_does_not_decide(self):
        r = run(make(h=22.7, occ=2, size=[diameter(1126.0, 1060.0, 1192.0)]))
        g = r.missions["surface"]["gates"][1]
        self.assertEqual(g["status"], "untested")
        self.assertEqual(g["text"], "We do not use the diameter on file, because it does not fit the asteroid's brightness.")
        self.assertEqual(len(r.rows["size"].conflicts), 1)                # the row gives the figures, once
        self.assertLess(r.summary["size_m"]["q95"], 400.0)                # the draws came from brightness
        run(r)
        self.assertEqual(len(r.rows["size"].conflicts), 1)                # running again adds nothing

    def test_a_limit_decides_when_all_of_it_is_on_one_side(self):
        r = run(make(h=24.0, spin=[period(4.0, "ssodnet", None, kind="lower")]))
        self.assertEqual(r.missions["surface"]["gates"][2]["status"], "pass")
        r = run(make(h=24.0, size=[diameter(20.0, kind="upper")]))
        self.assertEqual(r.missions["surface"]["gates"][1]["status"], "fail")
        r = run(make(h=24.0, size=[diameter(200.0, kind="upper")]))
        self.assertEqual(r.missions["surface"]["gates"][1]["status"], "untested")
        self.assertEqual(r.missions["surface"]["gates"][1]["text"], "The bound on file does not decide it.")
        # the review's two cases: a lower limit under the line (2017 BL6) and an upper limit over it (1999 NW2)
        for p_, kind in ((1.1, "lower"), (4.2, "upper")):
            g = run(make(h=24.0, spin=[period(p_, "lcdb", "2", kind=kind),
                                       Fact("period", p_, unit="h", source="jpl-sbdb", used=False)],
                         spin_state="limit")).missions["surface"]["gates"][2]
            self.assertEqual((g["status"], g["basis"]), ("untested", "prior"))
            self.assertEqual(g["text"], "The bound on file does not decide it.")
        g = run(make(h=24.0, spin=[period(1.5, "lcdb", "2", kind="upper")])).missions["surface"]["gates"][2]
        self.assertEqual(g["status"], "fail")                             # at most 1.5 h is under 2.2 h

    def test_inference_only_values_are_pointed_to_not_printed(self):
        r = run(make(h=21.0, occ=0, spin=[period(7.3391, "lcdb", "3")]))
        g = r.missions["surface"]["gates"][2]
        self.assertEqual(g["status"], "pass")                             # it may feed a derived value
        for text in walk_strings([r.missions, r.ladder, r.observe]):
            self.assertNotIn("7.3", text)
            self.assertNotIn("U 3", text)                                 # nor its grade
        # even where another source states the same value, no sentence names the lightcurve database's grade
        same = run(make(h=21.0, occ=0, spin=[period(7.3391, "lcdb", "3"), period(7.3391, "jpl-sbdb", None)]))
        for text in walk_strings([same.missions, same.ladder, same.observe]):
            self.assertNotIn("U 3", text)
            self.assertNotIn("the lightcurve database", text)
        self.assertEqual(draws.inputs(same, M).period_shown.source, "jpl-sbdb")
        # a period graded unreliable there alone: the gate says so and gives neither the number nor the grade
        low = run(make(h=22.9, occ=0, spin=[period(10.0, "lcdb", "1+")], spin_state="prior"))
        for text in walk_strings([low.missions, low.ladder]):
            self.assertNotIn("10 hours", text)
            self.assertNotIn("1+", text)

    def test_the_same_measurement_from_another_source_stands_in_for_an_inference_only_one(self):
        # Bennu: 4.2968 h in the lightcurve database, 4.296057 h on the literature card
        r = make(h=20.21, occ=0, spin=[period(4.2968, "lcdb", "3"),
                                       period(4.296057, "ssodnet", None, ref="Barnouin+2019 (2019NatGe..12..247B)")])
        self.assertEqual(draws.inputs(r, M).period_shown.source, "ssodnet")
        self.assertEqual(run(r).missions["surface"]["gates"][2]["status"], "pass")
        # not when the other source gives a different period
        inp = draws.inputs(make(h=25.91, occ=2, spin=[period(0.1784, "lcdb", "3"), period(0.089193, "jpl-sbdb", None)]), M)
        self.assertIsNone(inp.period_shown)
        # nor one graded unreliable, nor one across a line the method draws
        inp = draws.inputs(make(spin=[period(2.21, "lcdb", "3"), period(2.19, "ssodnet", None)]), M)
        self.assertIsNone(inp.period_shown)
        inp = draws.inputs(make(spin=[period(5.0, "lcdb", "3"), period(5.02, "pravec", "1")]), M)
        self.assertIsNone(inp.period_shown)
        inp = draws.inputs(make(spin=[period(5.0, "lcdb", "3"), period(5.02, "pravec", "2")]), M)
        self.assertEqual(inp.period_shown.source, "pravec")

    def test_licence_table_matches_the_source_list(self):
        try:
            from longshot import sources
            listed = sources.load()
        except Exception as err:        # the data is not on disk
            self.skipTest(f"source list not available: {err!r}")
        self.assertEqual({k: s.licence for k, s in listed.items()}, draws.LICENCE)
        self.assertEqual(set(draws.SPOKEN), set(draws.LICENCE))


class Observe(unittest.TestCase):
    def test_gain_matches_the_table_in_the_method_document(self):
        for p, q, want in ((0.5, 0.5, 1.00), (0.1, 0.1, 0.47), (0.25, 0.5, 0.31), (0.36, 0.36, 0.94),
                           (0.315, 1.0, 0.00), (0.315, 0.315, 0.90)):
            self.assertAlmostEqual(observe.gain(p, q), want, delta=0.005, msg=f"{p} {q}")
        self.assertEqual(observe.gain(0.0, 0.5), 0.0)
        self.assertEqual(observe.gain(1.0, 1.0), 0.0)
        # the bounded shares of an untested mission (1/n and 1 - 1/n) leave a gain to rank by
        self.assertGreater(observe.gain(0.9995, 0.9995), 0.005)
        self.assertGreater(observe.gain(0.0005, 0.0005), 0.005)

    def test_a_lightcurve_for_an_unreliable_period(self):
        r = run(make(h=22.9, occ=0, spin=[period(10.0, "pravec", "1")], spin_state="prior",
                     window=("2026-11-27", "2027-03-20", 21.85, "pointable")))
        o = r.observe
        self.assertEqual((o["best"], o["mission"], o["gate"]), ("lightcurve", "surface", "spin"))
        surface = r.missions["surface"]
        self.assertAlmostEqual(o["gain"], observe.gain(surface["p"], surface["gates"][2]["p"]), places=3)
        self.assertAlmostEqual(o["gain"], 0.93, delta=0.02)                # nearly a whole bit: a 35-in-100 guess
        self.assertEqual((o["tier"], o["unchecked"]), ("pointable", []))
        self.assertEqual(o["needs"], "4 m class telescope")
        self.assertEqual(o["window"], {"start": "2026-11-27", "end": "2027-03-20", "peak_mag": 21.85,
                                       "pointable": True, "as_of": config.DATA_DATE})
        self.assertIn("Rotation lightcurve", o["text"])

    def test_a_size_when_the_period_is_known(self):
        r = run(make(h=25.08, occ=1, spin=[period(3.8, "pravec", "2")], window=None))
        o = r.observe
        self.assertEqual((o["best"], o["mission"]), ("size", "surface"))
        p = r.missions["surface"]["p"]
        self.assertAlmostEqual(p, 0.315, delta=0.03)                      # missions.toml, 2021 UH2
        self.assertAlmostEqual(o["gain"], observe.h2(p), places=3)        # the size gate is the only open question
        self.assertIsNone(o["window"])
        self.assertEqual(o["needs"], M.observe["needs"]["not_pointable"]["no_window"])

    def test_a_lightcurve_does_nothing_for_capture(self):
        r = run(make(h=28.99, occ=0, window=None))          # surface: no draw is 30 m; capture: size and mass open
        self.assertEqual(r.missions["surface"]["p"], round(1 / M.n_draws, 4))
        o = r.observe
        self.assertEqual((o["best"], o["mission"], o["gate"]), ("size", "capture", "size"))
        capture = r.missions["capture"]
        self.assertAlmostEqual(o["gain"], observe.gain(capture["p"], capture["gates"][1]["p"]), places=3)

    def test_none_when_nothing_is_untested(self):
        self.assertIsNone(run(make(h=24.0, occ=8)).observe)                              # both missions fail
        done = run(make(h=20.0, occ=0, size=[diameter(400.0, 350.0, 450.0)], spin=[period(5.0)]))
        self.assertIsNone(done.observe)                                                  # pass and fail, none open
        self.assertIsNone(run(make(h=None)).observe)

    def test_telescope_class_follows_peak_brightness(self):
        w = {"start": "2027-01-01", "end": "2027-02-01", "pointable": True, "as_of": config.DATA_DATE}
        for mag, want in ((17.0, "small telescope"), (18.0, "small telescope"), (18.01, "2 m class telescope"),
                          (20.0, "2 m class telescope"), (21.9, "4 m class telescope"),
                          (22.5, "telescope larger than 4 m")):
            self.assertEqual(observe.needs(M, "lightcurve", {**w, "peak_mag": mag}), want, mag)
        self.assertEqual(observe.needs(M, "size", {**w, "peak_mag": 16.0}),
                         "1–2 m polarimeter or infrared space telescope")
        self.assertEqual(observe.needs(M, "size", {**w, "peak_mag": 19.0}), "infrared space telescope")
        self.assertEqual(observe.needs(M, "lightcurve", {**w, "pointable": False, "peak_mag": 17.0}),
                         "a survey must find it again first")

    def test_ties_go_to_the_lightcurve_then_to_surface(self):
        r = make()
        gates = [{"id": "findable", "label": "f", "status": "pass", "p": 1.0},
                 {"id": "size", "label": "s", "status": "untested", "p": 0.5},
                 {"id": "spin", "label": "t", "status": "untested", "p": 0.5}]
        r.missions = {"surface": {"status": "untested", "p": 0.25, "gates": gates},
                      "capture": {"status": "untested", "p": 0.25, "gates": gates}}
        o = observe.best(r, M)
        self.assertEqual((o["best"], o["mission"]), ("lightcurve", "surface"))
        self.assertAlmostEqual(o["gain"], 0.311, places=3)

    def test_ranked_order(self):
        """observe.toml [rank]: what can be pointed at first, by the year its window opens, then by gain."""
        def rec(key, gain, window):
            r = make(key)
            r.observe = {"gain": gain, "window": window}
            return r
        records = [
            rec("none", 0.99, None),
            rec("survey", 0.98, {"start": "2026-12-01", "pointable": False}),
            rec("far", 1.0, {"start": "2037-08-11", "pointable": True}),
            rec("soon-small", 0.3, {"start": "2026-11-27", "pointable": True}),
            rec("soon-big", 0.9, {"start": "2026-12-20", "pointable": True}),
            rec("next-year", 0.95, {"start": "2027-01-05", "pointable": True}),
            make("unranked"),
        ]
        self.assertEqual([r.key for r in observe.ranked(records)],
                         ["soon-big", "soon-small", "next-year", "far", "survey", "none"])
        self.assertEqual(observe.rank_key({"gain": 0.5, "window": None, "tier": "none"}, "k")[0], 2)

    def test_the_observation_carries_the_sources_not_checked_for_its_row(self):
        """observe.unchecked names them, so the entry can say where to look first; the text does not repeat them."""
        r = run(make(h=22.9, occ=0, unchecked={"spin": ["ssodnet"]}))
        o = r.observe
        self.assertEqual((o["best"], o["unchecked"]), ("lightcurve", ["ssodnet"]))
        self.assertNotIn("SsODNet", o["text"])
        self.assertNotIn("not measured", o["text"].lower())
        checked = run(make(h=22.9, occ=0)).observe
        self.assertEqual(checked["unchecked"], [])
        self.assertEqual(checked["text"], o["text"])
        # a survey-only window is its own tier
        survey = run(make(h=22.9, occ=5, window=("2030-05-01", "2030-05-09", 23.6, "survey-only"))).observe
        self.assertEqual(survey["tier"], "survey_only")

    def test_survey_only_window_is_not_pointable(self):
        r = make(window=("2027-01-10", "2027-02-20", 23.5, "survey only"))
        self.assertFalse(observe.window(r)["pointable"])


class Ladder(unittest.TestCase):
    def check_shape(self, r):
        self.assertEqual(tuple(x["rung"] for x in r.ladder), LADDER)
        for rung in r.ladder:
            if rung["rung"] == "brought_back" and "parts" in rung:
                # the two amounts the entry tabulates: their texts, label first, are the rung's text
                parts = rung["parts"]
                self.assertEqual([p["id"] for p in parts], ["grams", "more_than_grams"])
                self.assertEqual(" ".join(f"{p['label']}: {p['text']}" if p["label"] else p["text"] for p in parts),
                                 rung["text"])
                self.assertEqual(parts[1]["word"], "proposed")
                self.assertIn(parts[0]["word"], (None, *M.ladder["rung"]["brought_back"]["words"]))
                rung = {k: v for k, v in rung.items() if k != "parts"}
            self.assertEqual(set(rung), {"rung", "status", "text"})
            self.assertIn(rung["status"], M.ladder["meta"]["statuses"])
            self.assertTrue(rung["text"])
            self.assertNotIn("{", rung["text"])
            self.assertNotIn("}", rung["text"])
            self.assertNotIn("  ", rung["text"])

    def test_an_unmeasured_small_object(self):
        r = run(make(h=28.99, occ=0, arc=1268, dv=3.517, dur=362, window=None))
        self.check_shape(r)
        found, reached, workable, anything, back = r.ladder
        self.assertEqual(found["status"], "measured")
        self.assertEqual(found["text"], "Its orbit condition code, 0, meets the condition ≤ 5. "
                                        "JPL lists no observing window through 2045.")
        self.assertTrue(reached["text"].startswith("The cheapest round trip needs Δv 3.517 km/s. "
                                                   "JPL's list gives no launch date for it."))
        self.assertIn("Tianwen-2 reached Kamoʻoalewa (18 ± 2 m, measured by JWST)", reached["text"])   # all of it is under 100 m
        self.assertEqual(workable["status"], "prior")
        self.assertEqual(workable["text"], "Its spin is estimated. Of asteroids this bright, 94% turn faster than once in 2.2 h.")
        self.assertEqual((anything["status"], anything["text"]), ("prior", "Estimated from its brightness alone."))
        self.assertEqual(back["status"], "prior")
        self.assertIn("Grams: not yet attempted.", back["text"])
        self.assertIn("Whether it could be sampled also depends on its spin, which is estimated.", back["text"])
        self.assertIn("never built.", back["text"])

    def test_a_rung_does_not_repeat_what_a_row_or_the_price_tag_says(self):
        """DESIGN.md section 5, and the review's count of sentences printed twice on every entry."""
        for r in (run(make(h=28.99, window=None)), run(make(h=24.0, spin=[period(0.4)])),
                  run(make(h=22.0, size=[diameter(120.0, 100.0, 140.0)], surface=[fact("class", "S", "ssodnet")]))):
            texts = [x["text"] for x in r.ladder]
            for sentence in r.value["statements"]:
                for text in texts:
                    self.assertNotIn(sentence, text)                # the price tag's sentences are printed once
            joined = " ".join(texts)
            for repeat in ("days of tracking", "m across", "tonnes.", "Turns once in", "(as of", "magnitude",
                           "an 18 m asteroid", "the 18 m"):
                self.assertNotIn(repeat, joined, repeat)
            gates = [g["text"] for mi in r.missions.values() for g in mi["gates"] if g["text"]]
            self.assertEqual(len(gates), len(set(gates)) if len(gates) < 2 else len(gates))
        # Tianwen-2 is named once: on the reach rung, not again on the last one
        small = run(make(h=28.99, window=None))
        self.assertEqual(sum(x["text"].count("Tianwen-2") for x in small.ladder), 1)

    def test_the_orbit_rung_does_not_claim_findability_against_jpls_own_test(self):
        """137 list members pass 'code 5 or better' while JPL flags their window survey-recovery-only."""
        self.assertEqual({g["label"] for mi in MISSIONS for g in M.missions[mi]["gates"] if g["id"] == "findable"},
                         {"Orbit condition code ≤ 5"})
        pointable = run(make(window=("2026-11-27", "2027-03-20", 21.85, "pointable")))
        self.assertEqual(pointable.ladder[0]["text"], "Its orbit condition code, 1, meets the condition ≤ 5.")
        self.assertEqual(pointable.missions["surface"]["gates"][0]["text"], "")
        survey = run(make(occ=5, window=("2030-05-01", "2030-05-09", 23.6, "survey-only")))
        self.assertEqual(survey.ladder[0]["text"], "Its orbit condition code, 5, meets the condition ≤ 5. "
                                                   "JPL finds its position too uncertain to point at.")
        # said once, on the rung that asks whether it can be found again; the tracking row shows the window
        for mission in MISSIONS:
            g = survey.missions[mission]["gates"][0]
            self.assertEqual((g["status"], g["text"]), ("pass", ""))
        for r in (pointable, survey):
            for text in walk_strings([r.ladder, r.missions]):
                self.assertNotIn("open now", text)
                self.assertNotIn("good enough to find", text)
                self.assertNotIn("can be found again", text)

    def test_orbit_code_states(self):
        self.assertIn("Its orbit condition code, 8, fails the condition ≤ 5", run(make(occ=8)).ladder[0]["text"])
        none = run(make(occ=None)).ladder[0]
        self.assertEqual(none["status"], "unknown")
        self.assertEqual(none["text"], "JPL lists no orbit condition code for it.")

    def test_spin_sentences(self):
        def workable(**kw):
            return run(make(h=24.31, **kw)).ladder[2]["text"]
        self.assertEqual(workable(spin=[period(12.132)]), "It turns more slowly than once in 3.0 h. Up to that spin, gravity "
                         "holds loose material at the equator even for light rock (1,200 kg/m³).")
        self.assertTrue(workable(spin=[period(2.3478)]).startswith("It turns once in 1.8–3.0 h."))
        # ladder.toml's own examples: 15 to 40 for 27.9 minutes, 5,000 to 14,000 for 92.5 seconds
        self.assertIn("At its equator, outward pull is 15–40 times gravity",
                      workable(spin=[period(27.9 / 60)]))
        self.assertIn("At its equator, outward pull is 5,000–14,000 times", workable(spin=[period(92.5 / 3600)]))
        # not checked and not measured read the same: an estimate. The spin row names the source, once
        self.assertEqual(workable(unchecked={"spin": ["ssodnet"]}),
                         "Its spin is estimated. Of asteroids this bright, 80% turn faster than once in 2.2 h.")
        self.assertEqual(workable(), "Its spin is estimated. Of asteroids this bright, 80% turn faster than once in 2.2 h.")
        self.assertEqual(workable(spin=[period(10.0, "pravec", "1")], spin_state="prior"),
                         "Its only period is graded unreliable, so its spin is estimated. Of asteroids this bright, "
                         "80% turn faster than once in 2.2 h.")
        self.assertTrue(workable(spin=[period(1.5, "ssodnet", None, kind="lower")]).startswith(
            "A source gives only a bound on its spin. Of asteroids this bright, "))

    def test_status_follows_what_is_measured(self):
        r = run(make(h=20.0, occ=0, size=[diameter(340.0, 320.0, 360.0)], spin=[period(30.56)],
                     surface=[fact("class", "S", "ssodnet")]))
        self.check_shape(r)
        self.assertEqual(r.ladder[2]["status"], "measured")
        self.assertEqual(r.ladder[3]["text"], "Estimated from its measured class or reflectivity, and its brightness.")
        self.assertEqual(r.ladder[4]["status"], "measured")
        self.assertIn("Grams: done three times, by space agencies, on asteroids of this diameter and spin", r.ladder[4]["text"])
        self.assertNotIn("under 100 m", r.ladder[1]["text"])
        limit = run(make(h=24.0, size=[diameter(30.0, kind="upper")])).ladder[2]
        self.assertEqual(limit["status"], "prior")
        # a surface source not checked: the surface row names it; the rung says what the estimate rests on
        unchecked = run(make(h=24.0, unchecked={"surface": ["ssodnet", "spitzer"]})).ladder[3]["text"]
        self.assertEqual(unchecked, "Estimated from its brightness alone.")
        # a measured size with no class or reflectivity: the estimate rests on the size, not on brightness
        sized = run(make(h=24.0, size=[diameter(40.0, 30.0, 50.0)])).ladder[3]["text"]
        self.assertEqual(sized, "Estimated from its measured diameter. Its composition is estimated.")
        sized = run(make(h=24.0, size=[diameter(40.0, 30.0, 50.0)], unchecked={"surface": ["ssodnet"]})).ladder[3]["text"]
        self.assertEqual(sized, "Estimated from its measured diameter. Its composition is estimated.")

    def test_last_rung_by_size_and_spin(self):
        def back(**kw):
            return run(make(**kw)).ladder[4]["text"]
        big = [diameter(500.0, 480.0, 520.0)]
        self.assertIn("on asteroids of this diameter that turn once in 4.3–12.1 h. Its own spin is estimated.",
                      back(h=19.5, size=big))
        self.assertIn("not yet attempted on an asteroid that turns this fast", back(h=19.5, size=big, spin=[period(3.0)]))
        self.assertIn("on asteroids 330–900 m across, and not yet attempted on a smaller one. "
                      "Its diameter range spans 330 m.", back(h=20.5, size=[diameter(300.0, 250.0, 350.0)]))
        self.assertIn("Grams: not yet attempted at this diameter.", back(h=21.5, size=[diameter(200.0, 190.0, 210.0)]))
        self.assertIn("no spacecraft that has approached an asteroid turning this fast",
                      back(h=28.0, spin=[period(0.05)]))
        small = back(h=28.0, spin=[period(5.0)])
        self.assertIn("no spacecraft that has touched an asteroid this small.", small)
        self.assertNotIn("18 m", small)                 # the JWST size is named once, with its source, on rung two

    def test_sampled_and_visited_asteroids(self):
        bennu = make(h=20.21, occ=0, designation="1999 RQ36", name="Bennu", number=101955,
                     aliases=["101955", "1999 RQ36", "Bennu"], size=[diameter(488.0, 469.0, 507.0)],
                     spin=[period(4.296)], surface=[fact("class", "B", "ssodnet")])
        bennu.rows["push"] = Row("measured", [fact("A2", -4.6e-14, lo=-4.7e-14, hi=-4.5e-14),
                                              fact("density", 1194.0, unit="kg/m^3")])
        run(bennu)
        self.check_shape(bennu)
        self.assertEqual(bennu.ladder[3]["status"], "measured")
        self.assertEqual(bennu.ladder[3]["text"], "The sample holds 0.84–0.95% hydrogen and 4.5–4.7% carbon "
                         "by weight (Lauretta et al. 2024).")
        self.assertIn("Grams: done. 121.6 g returned from this asteroid (OSIRIS-REx, 2023), for $1.02–1.16 billion",
                      bennu.ladder[4]["text"])
        # the price tag gives way to the sample: no odds on water from its class beside the sample's own result
        self.assertEqual(bennu.value["statement_ids"], ["sample_water_at_most", "water_market"])
        self.assertEqual(bennu.value["statements"][0], "If the whole body matches the returned sample, and all its "
                         "hydrogen is in water, it holds at most 8 million t of water.")
        for text in bennu.value["statements"]:
            self.assertNotIn("Of 100 like it", text)
            self.assertNotIn("S/Q", text)
        # its mass comes from the density on file and the measured size: about 73 million tonnes, not 58 to 140
        mass = bennu.summary["mass_t"]
        self.assertTrue(55e6 < mass["q05"] < 73e6 < mass["q95"] < 90e6, mass)
        ryugu = run(make(h=19.4, occ=0, designation="1999 JU3", name="Ryugu", number=162173,
                         size=[diameter(896.0, 880.0, 912.0)], spin=[period(7.633)],
                         surface=[fact("class", "Cb", "ssodnet")]))
        self.assertEqual(ryugu.value["statement_ids"], ["sample_water", "water_market"])
        self.assertRegex(ryugu.value["statements"][0],
                         r"^If the whole body matches the returned sample, it holds \d+ million to \d+ million t of water\.$")
        self.assertEqual(ryugu.ladder[3]["text"], "The sample holds 6.84 ± 0.34% water by weight (Yokoyama et al. 2023).")
        itokawa = run(make(h=19.26, occ=0, designation="1998 SF36", name="Itokawa", number=25143,
                           size=[diameter(326.0, 315.0, 337.0)], spin=[period(12.132)],
                           surface=[fact("class", "S", "ssodnet")]))
        self.assertEqual(itokawa.ladder[3]["text"], "A spacecraft sampled it. We have no analysis of the sample on file.")
        self.assertEqual(itokawa.value["statements"],
                         ["We have no analysis of the returned sample on file, so we give no figure."])
        for text in walk_strings(itokawa.value["statements"]):
            self.assertNotIn("$", text)                  # no dollar floor from its class beside a returned sample
        kamo = run(make(h=24.31, occ=0, designation="2016 HO3", name="Kamoʻoalewa", number=469219,
                        aliases=["469219", "2016 HO3", "Kamo`oalewa"], size=[diameter(18.0, 16.0, 20.0, "curated")],
                        spin=[period(0.465, "curated", None)]))
        self.assertIn("Tianwen-2 reached this asteroid in July 2026", kamo.ladder[4]["text"])
        self.assertNotIn("we found one spacecraft", kamo.ladder[1]["text"])
        # its own entry and the sentence other entries carry now rest on the same 18 m
        self.assertAlmostEqual(kamo.summary["size_m"]["q50"], 18.0, delta=0.1)
        self.assertEqual([g["status"] for g in kamo.missions["surface"]["gates"]], ["pass", "fail", "fail"])
        self.assertEqual(kamo.missions["capture"]["gates"][1]["status"], "fail")      # 14 m at two sigma is over 10 m

    def test_no_brightness(self):
        r = run(make(h=None, occ=9, arc=1, window=None, unchecked={"size": ["ssodnet"], "spin": ["ssodnet"]}))
        self.check_shape(r)
        self.assertEqual([x["status"] for x in r.ladder], ["measured", "measured", "unknown", "unknown", "unknown"])
        # the spin row names the source not checked; the rung says why there is no estimate
        self.assertEqual(r.ladder[2]["text"], "JPL lists no brightness for it, so we cannot estimate its diameter or spin.")
        plain = run(make(h=None, occ=9, arc=1, window=None))
        self.assertEqual(plain.ladder[2]["text"], r.ladder[2]["text"])

    def test_number_words(self):
        self.assertEqual(missions.period_words(7.633), "7.63 h")
        self.assertEqual(missions.period_words(0.465), "27.9 min")
        self.assertEqual(missions.period_words(92.5 / 3600), "92.5 s")
        self.assertEqual(ladder.count_words(0.8), "80%")
        self.assertEqual(ladder.count_words(0.004), "<1%")
        self.assertEqual(ladder.count_words(0.996), ">99%")
        self.assertEqual(missions.figures(18.2), "18")
        self.assertEqual(missions.figures(484.0), "480")
        self.assertEqual(missions.figures(4.47), "4.5")
        self.assertEqual(missions.tonnes_words(1_012_323.0), "1 million")
        self.assertEqual(missions.tonnes_words(61_806.0), "62,000")


class Predictions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [
            run(make("apo", h=19.09, occ=0, designation="2004 MN4", name="Apophis", number=99942,
                     size=[diameter(340.0, 300.0, 380.0)], spin=[period(30.56)],
                     surface=[fact("class", "S", "ssodnet")])),
            run(make("bm", h=25.04, occ=1, designation="2015 BM510")),
        ]
        cls.all = predictions.predictions(cls.records, M)

    def test_shape(self):
        keys = {"id", "kind", "group", "statement", "p", "p_low", "p_high", "band", "settles", "settle_from",
                "settle_by", "settle_note", "key", "designation", "frozen", "provisional", "outcome", "basis", "source"}
        ids = [p["id"] for p in self.all]
        self.assertEqual(len(ids), len(set(ids)))
        for p in self.all:
            self.assertEqual(set(p), keys, p["id"])
            self.assertIsNone(p["frozen"])                 # nothing is frozen until Adam says so
            self.assertTrue(p["provisional"])
            self.assertIsNone(p["outcome"])
            self.assertIn(p["kind"], ("rule", "case"))
            self.assertTrue(p["statement"].endswith("."))
            self.assertTrue(p["settles"])
            self.assertTrue(p["source"])
            for shown in (p["statement"], p["settles"]):
                self.assertNotIn("docs/", shown)                 # repository paths are not for the page
            if p["p"] is not None:
                self.assertTrue(0.0 < p["p"] < 1.0, p["id"])        # no prediction is held at 0% or 100%
            # every prediction says when it can be settled, or in a few words why no date is set
            self.assertTrue(p["settle_from"] or p["settle_by"] or p["settle_note"], p["id"])
            if p["settle_note"]:
                self.assertTrue(p["settle_note"].startswith("no date"), p["id"])

    def test_the_rule_tables_are_the_priors(self):
        n_bands = len(M.priors["bands"]["ids"])
        by = {}
        for p in self.all:
            by.setdefault((p["kind"], p["group"]), []).append(p)
        self.assertEqual(len(by[("rule", "class")]), n_bands * 4)
        self.assertEqual(len(by[("rule", "spin")]), n_bands * 3)
        self.assertEqual(len(by[("rule", "size")]), n_bands)
        for p in by[("rule", "class")]:
            c = p["id"].rsplit("-", 1)[1]
            row = M.priors["class"]["bands"][p["band"]]
            self.assertEqual((p["p"], p["p_low"], p["p_high"]),
                             (round(row["central"][c], 4), round(row["low"][c], 4), round(row["high"][c], 4)))
        for p in by[("rule", "spin")]:
            s = p["id"].split(p["band"] + "-", 1)[1]
            row = M.priors["spin"]["bands"][p["band"]][s]
            self.assertEqual((p["p"], p["p_low"], p["p_high"]), (row["central"], row["low"], row["high"]))
        size = {p["band"]: p for p in by[("rule", "size")]}
        self.assertRegex(size["26_28"]["statement"], r"^A newly measured reachable asteroid of H 27 is \d[\d.]*–\d+ m in diameter\.$")
        self.assertEqual(size["26_28"]["p"], 0.9)

    def test_named_cases(self):
        cases = {p["id"]: p for p in self.all if p["kind"] == "case"}
        self.assertEqual(set(cases), {"case-apophis-density", "case-kamooalewa-density", "case-2015bm510-size"})
        apo = cases["case-apophis-density"]
        self.assertEqual((apo["key"], apo["designation"], apo["p"]), ("apo", "Apophis", 0.9))
        self.assertRegex(apo["statement"], r"^has a bulk density of 1,[78]00–3,[23]00 kg/m³\.$")   # class S: 1,700 to 3,400
        self.assertEqual(apo["settle_from"], "2029")
        bm = cases["case-2015bm510-size"]
        self.assertEqual(bm["key"], "bm")
        self.assertRegex(bm["statement"], r"^is \d+–\d+ m in diameter\.$")
        self.assertEqual(bm["settle_from"], "2028-04")
        kamo = cases["case-kamooalewa-density"]                 # not among the records given
        self.assertIsNone(kamo["key"])
        self.assertIsNone(kamo["p"])

    def test_works_without_records(self):
        plain = predictions.predictions(None, M)
        self.assertEqual(len(plain), len(self.all))
        self.assertTrue(all(p["p"] is None for p in plain if p["kind"] == "case"))


class Stages(unittest.TestCase):
    def test_run_is_the_stages_in_order(self):
        a = [make("x1", h=22.0), make("x2", h=27.5, spin=[period(0.3)]), make("x3", h=None)]
        b = copy.deepcopy(a)
        model.run(a, M)
        for stage in (draws.apply, missions.apply, observe.apply):
            self.assertIs(stage(b, M), b)
        from longshot import value
        value.apply(b, M)
        ladder.apply(b, M)
        self.assertEqual(a, b)
        for r in a:
            self.assertEqual(tuple(r.rows), ROWS)

    def test_running_twice_changes_nothing(self):
        r = run(make("again", h=24.2, unchecked={"surface": ["ssodnet"]}))
        before = copy.deepcopy(r)
        self.assertEqual(run(r), before)

    def test_a_record_for_another_method_is_refused(self):
        r = make()
        r.method = "9.9"
        with self.assertRaises(method.MethodError):
            model.run_one(r, M)


class Contract(unittest.TestCase):
    """longshot/contract.py: what docs/mvp.md section 4 says it rejects, it rejects."""

    SOURCES = {"jpl-sbdb", "jpl-nhats", "ssodnet", "pravec", "lcdb", "spitzer", "curated"}

    def good(self, **kw):
        return run(make("abc123", h=24.0, size=[diameter(60.0, 55.0, 65.0)], spin=[period(5.0)], **kw))

    def problems(self, r):
        from longshot import contract
        return contract.problems(r, self.SOURCES)

    def test_a_good_record_passes(self):
        self.assertEqual(self.problems(self.good()), [])
        self.assertEqual(self.problems(run(make("abc124", h=26.2))), [])
        self.assertEqual(self.problems(run(make("abc125", h=None, occ=9))), [])

    def test_a_central_figure_anywhere_in_the_value_block_is_rejected(self):
        for path in (("iron_rich", "usd", "q50"), ("iron_rich", "mean"), ("metal", "usd_median"), ("usd_mean",),
                     ("water", "tonnes", "q50"), ("metal", "kg", "expected_kg"), ("metal", "usd", "q50")):
            r = self.good()
            node = r.value
            for key in path[:-1]:
                node = node.setdefault(key, {})
            node[path[-1]] = 1.0
            with self.subTest(path=".".join(path)):
                self.assertTrue(any("central figure" in p for p in self.problems(r)), self.problems(r))

    def test_a_measured_row_must_rest_on_a_value_in_use(self):
        r = self.good()
        for f in r.rows["size"].facts:
            f.used = False
        self.assertTrue(any("size: measured" in p for p in self.problems(r)))
        r = self.good()
        r.rows["spin"].facts.insert(0, period(2.0, "lcdb", "2", kind="lower"))
        self.assertTrue(any("spin: measured, but its first fact is not a value" in p for p in self.problems(r)))
        r = self.good()
        r.rows["spin"].state = "limit"
        self.assertTrue(any("spin: a limit, but its first fact is not a bound" in p for p in self.problems(r)))

    def test_shapes_that_are_not_what_they_say(self):
        def broken(change):
            r = self.good()
            change(r)
            return self.problems(r)
        self.assertTrue(any("holds p = 7" in p for p in broken(lambda r: r.missions["surface"]["gates"][1].update(p=7))))
        self.assertTrue(any("kind 'bogus'" in p for p in broken(lambda r: setattr(r.rows["size"].facts[0], "kind", "bogus"))))
        self.assertTrue(any("not a finite number" in p
                            for p in broken(lambda r: setattr(r.rows["size"].facts[0], "lo", float("nan")))))
        self.assertTrue(any("summary.reflectivity" in p for p in broken(lambda r: r.summary.pop("reflectivity"))))
        # an untested chance stored as 0 or 1
        r = run(make("abc126", h=31.4))
        self.assertEqual(self.problems(r), [])
        r.missions["surface"]["gates"][1]["p"] = 0.0
        self.assertTrue(any("untested with p = 0.0" in p for p in self.problems(r)))
        r = run(make("abc127", h=31.4))
        r.missions["capture"]["p"] = 1.0
        self.assertTrue(any("missions.capture is untested with p = 1.0" in p for p in self.problems(r)))
        # a window date that is not a date
        r = run(make("abc128", h=22.9, occ=0))
        self.assertEqual(self.problems(r), [])
        r.observe["window"]["start"] = "soon"
        self.assertTrue(any("not an ISO date" in p for p in self.problems(r)))

    def test_the_fields_the_entry_summary_and_price_tables_read(self):
        def broken(change, record=None):
            r = record or self.good()
            change(r)
            return self.problems(r)
        self.assertTrue(any("add to 100" in p for p in broken(lambda r: r.value["table"]["metal"]["cells"][0].update(n=99))))
        self.assertTrue(any("out of order" in p
                            for p in broken(lambda r: r.value["table"]["water"]["cells"].reverse(),
                                            run(make("abc130", h=24.19)))))
        self.assertTrue(any("no label or no figure" in p
                            for p in broken(lambda r: r.value["table"]["metal"]["rows"][0].update(of100=None))))
        self.assertTrue(any("value.table is not" in p for p in broken(lambda r: r.value.pop("table"))))
        self.assertTrue(any("summary.period is missing" in p for p in broken(lambda r: r.summary.pop("period"))))
        self.assertTrue(any("summary.period is null" in p for p in broken(lambda r: r.summary.update(period=None))))
        self.assertTrue(any("summary.mass_basis" in p for p in broken(lambda r: r.summary.update(mass_basis="guess"))))
        self.assertTrue(any("rests on 'somewhere'" in p
                            for p in broken(lambda r: r.summary["period"].update(rests_on="somewhere"))))
        r = run(make("abc131", h=22.9, occ=0))
        self.assertIsNotNone(r.observe)
        self.assertTrue(any("gate_label" in p for p in broken(lambda r: r.observe.update(gate_label=""), r)))

    def test_a_body_that_is_gone_must_not_carry_a_window_a_tag_or_a_ranked_observation(self):
        def gone(**kw):
            r = make("abc129", h=30.7, occ=4, **kw)
            r.gone = {"date": "2008-10-07", "text": "Entered Earth's atmosphere on 7 October 2008.", "evidence": "x"}
            return r
        r = run(gone(window=None))
        r.rows["tracking"].facts = [f for f in r.rows["tracking"].facts if f.label != "next window"]
        self.assertEqual(self.problems(r), [])           # as the ledger builds it: no window fact of any kind
        self.assertTrue(any("lists a window" in p for p in self.problems(run(gone()))))       # the 2041 window
        r = run(gone(window=None))
        r.value = {"metal": {}}
        self.assertTrue(any("price tag" in p for p in self.problems(r)))


class RealData(unittest.TestCase):
    """The targets named in missions.toml, from the ledger on disk. Skipped when it has not been built."""

    @classmethod
    def setUpClass(cls):
        path = config.BUILD / "ledger.jsonl"
        if not path.exists():
            raise unittest.SkipTest("build/ledger.jsonl not built")
        from longshot import export
        wanted = {n["designation"] for mission in M.missions["order"] for n in M.missions[mission]["named"]}
        cls.by = {}
        for r in export.read_records(path):
            names = {r.designation, r.name}
            if names & wanted:
                cls.by[(names & wanted).pop()] = run(r)
        if len(cls.by) != len(wanted):
            raise unittest.SkipTest("the ledger on disk does not hold every named target")

    def test_named_targets_come_out_as_the_method_file_records(self):
        for mission in M.missions["order"]:
            for named in M.missions[mission]["named"]:
                got = self.by[named["designation"]].missions[mission]
                self.assertEqual(got["status"], named["status"], named["designation"])
                self.assertAlmostEqual(got["p"], named["p"], delta=0.02, msg=named["designation"])
                self.assertEqual({g["id"]: g["status"] for g in got["gates"]}, named["gates"], named["designation"])

    def test_counts_match_the_check_tables(self):
        for mission in M.missions["order"]:
            check = M.missions[mission]["check"]
            statuses = [self.by[n["designation"]].missions[mission]["status"] for n in M.missions[mission]["named"]]
            self.assertEqual((statuses.count("pass"), statuses.count("untested"), statuses.count("fail")),
                             (check["known_pass"], check["untested"], check["known_fail"]))


if __name__ == "__main__":
    unittest.main()
