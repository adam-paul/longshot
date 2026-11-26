"""The checker's tests of method/v0_1/*.toml.

Three kinds:
  recompute   tools/method_check.py, which shares no code with the scripts that wrote the constants, passes
  bite        the same checks fail when a constant is spoiled in the ways the brief names: a troy ounce read as a
              kilogram, a percentage read as a fraction, a pure-metal grade on bulk rock, shares that do not sum,
              a table that falls, a middle dollar figure, an undated universal negative
  fixed       each thing the check of 2026-11-25 changed stays changed

Run: uv run python -m unittest tests.test_method_check
"""
import copy
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import method_check as mc  # noqa: E402

HAVE_DATA = os.path.exists(mc.SPITZER) and os.path.exists(os.path.join(mc.SNAPSHOT, "sbdb_neo.json"))


def read(path):
    with open(path) as fh:
        return fh.read()


def run(fn, m, *args):
    """Run one group of checks quietly. Returns the texts of the checks that failed."""
    c = mc.Checks(out=lambda text: None)
    fn(c, m, *args)
    return c.failed


class Recompute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = mc.load_all()

    def test_five_files_parse(self):
        self.assertEqual(sorted(self.m), ["ladder", "missions", "observe", "priors", "value"])

    def test_shape_units_gain_ladder_and_no_central_figure(self):
        for fn in (mc.check_shape, mc.check_units, mc.check_observe, mc.check_no_central, mc.check_ladder, mc.check_joint,
                   mc.check_agreement):
            self.assertEqual(run(fn, self.m), [], fn.__name__)

    def test_worked_examples_reproduce_from_the_file_alone(self):
        """Every export of all three examples, at the 200,000 draws the file records, by code typed here."""
        c = mc.Checks(out=lambda text: None)
        mc.check_value(c, self.m, self.m["value"]["example"][0]["draws"])
        self.assertEqual(c.failed, [])
        self.assertGreater(c.n, 80)

    @unittest.skipUnless(HAVE_DATA, "data/ is not unpacked")
    def test_spitzer_ratio_and_named_targets(self):
        self.assertEqual(run(mc.check_spitzer, self.m), [])
        self.assertEqual(run(mc.check_missions, self.m), [])

    @unittest.skipUnless(HAVE_DATA, "data/ is not unpacked")
    def test_whole_script_exits_clean(self):
        lines = []
        code = mc.main(["method_check.py", "--quick"], out=lines.append)
        self.assertEqual(code, 0, "".join(x for x in lines if "FAIL" in x))
        self.assertIn("checks pass", lines[-1])


class Bite(unittest.TestCase):
    """Each check must fail when the thing it guards is wrong."""

    def setUp(self):
        self.m = copy.deepcopy(mc.load_all())

    def test_troy_ounce_read_as_kilogram(self):
        v = self.m["value"]["prices"]["usd_per_kg"]
        v["Pt"] = [x / 32.15 for x in v["Pt"]]  # dollars per troy ounce written where dollars per kilogram belong
        self.assertTrue(any("Pt: $/kg" in f for f in run(mc.check_units, self.m)))

    def test_cap_in_tonnes_where_kilograms_belong(self):
        self.m["value"]["market"]["cap_kg"]["Ir"] = 0.7
        self.assertTrue(any("Ir: cap in kg" in f for f in run(mc.check_units, self.m)))

    def test_water_percentage_read_as_fraction(self):
        self.m["value"]["material"]["carbonaceous"]["water_fraction"] = {"lo": 1.9, "hi": 10.5}
        self.assertTrue(any("water fraction" in f for f in run(mc.check_units, self.m)))

    def test_pure_metal_grade_on_bulk_rock(self):
        self.m["value"]["material"]["oc_h"]["grade_table"] = "iron_meteorite"
        self.assertTrue(any("pure-metal grade table" in f for f in run(mc.check_units, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        m2["value"]["material"]["carbonaceous"]["counted"] = True
        self.assertTrue(any("dark rock" in f for f in run(mc.check_units, m2)))

    def test_size_coefficient_in_kilometres(self):
        self.m["priors"]["size"]["coefficient_m"] = 1329.0
        self.assertTrue(any("size coefficient" in f for f in run(mc.check_units, self.m)))

    def test_spin_threshold_in_minutes(self):
        self.m["priors"]["spin"]["thresholds_h"][2] = 10.0
        self.assertTrue(any("spin thresholds" in f for f in run(mc.check_shape, self.m)))

    def test_shares_that_do_not_sum(self):
        self.m["value"]["kinds"]["X"]["mid"][0]["share"][2] = 0.7
        self.assertTrue(any("kinds X.mid" in f for f in run(mc.check_shape, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        m2["value"]["mix"]["iron_high"]["Ir"] = 0.36
        self.assertTrue(any("mix iron_high" in f for f in run(mc.check_shape, m2)))
        m3 = copy.deepcopy(mc.load_all())
        m3["priors"]["class"]["bands"]["24_26"]["central"]["S"] += 0.05
        self.assertTrue(any("band 24_26" in f for f in run(mc.check_shape, m3)))

    def test_a_table_that_falls(self):
        self.m["priors"]["reflectivity"]["pv"][7] = 0.10
        self.assertTrue(any("do not fall" in f for f in run(mc.check_shape, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        m2["priors"]["spin"]["bands"]["24_26"]["under_10min"]["central"] = 0.99
        self.assertTrue(any("10 min <= 1 h" in f for f in run(mc.check_shape, m2)))

    def test_joint_weights_that_miss(self):
        self.m["priors"]["class"]["bands"]["26_28"]["joint_weight"] = dict(self.m["priors"]["class"]["bands"]["26_28"]["central"])
        self.assertTrue(any("band 26_28" in f for f in run(mc.check_joint, self.m)))

    def test_a_middle_dollar_figure(self):
        self.m["value"]["example"][0]["metal"]["usd"]["q50"] = 5e5
        self.assertTrue(any("middle" in f for f in run(mc.check_no_central, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        m2["value"]["exports"]["metal"]["usd_median"] = "the middle draw"
        self.assertTrue(any("no key named" in f for f in run(mc.check_no_central, m2)))
        m3 = copy.deepcopy(mc.load_all())
        m3["value"]["statement"][0]["template"] = "A typical one is worth {usd}."
        self.assertTrue(any("no printed sentence" in f for f in run(mc.check_no_central, m3)))

    def test_an_undated_universal_negative(self):
        st = next(s for s in self.m["value"]["statement"] if s["id"] == "water_market")
        st["template"] = "Nobody buys water in orbit."
        self.assertTrue(any("we found" in f for f in run(mc.check_ladder, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        gate = next(g for g in m2["missions"]["surface"]["gates"] if g["id"] == "spin")
        gate["caveat"] = "No spacecraft has touched an asteroid turning faster than once in about 4 h."
        self.assertTrue(any("we found" in f for f in run(mc.check_ladder, m2)))

    def test_a_wrong_example_figure(self):
        self.m["value"]["example"][1]["metal"]["usd"]["q95"] *= 1.002
        c = mc.Checks(out=lambda text: None)
        mc.check_value(c, self.m, self.m["value"]["example"][1]["draws"])
        self.assertTrue(any("example 2 metal.usd.q95" in f for f in c.failed))

    def test_a_sentence_that_misquotes_its_export(self):
        ex = self.m["value"]["example"][0]
        ex["statements"][1] = ex["statements"][1].replace("$8 million", "$6 million")
        c = mc.Checks(out=lambda text: None)
        mc.check_value(c, self.m, ex["draws"])
        self.assertTrue(any("every kilogram, tonne and dollar figure" in f for f in c.failed))

    def test_a_wrong_single_draw(self):
        self.m["value"]["check"][0]["expect"][2]["kg"] *= 1.001
        c = mc.Checks(out=lambda text: None)
        mc.check_value(c, self.m, 2000)
        self.assertTrue(any("stony_measured_size" in f for f in c.failed))

    def test_two_files_that_disagree(self):
        self.m["value"]["reference_draw"]["pv"][10] = 0.14
        self.assertTrue(any("copy of the reflectivity quantiles" in f for f in run(mc.check_agreement, self.m)))
        m2 = copy.deepcopy(mc.load_all())
        m2["priors"]["density"]["X"]["metal_rich_share_of_mid"] = 0.5
        self.assertTrue(any("metal-rich share" in f for f in run(mc.check_agreement, m2)))
        m3 = copy.deepcopy(mc.load_all())
        m3["ladder"]["rung"]["found_again"]["state"][0]["text"] = "Orbit code {occ}: good enough to point a telescope at."
        self.assertTrue(any("pointing" in f for f in run(mc.check_agreement, m3)))

    def test_gain_formula_text_changed(self):
        self.m["observe"]["gain"]["formula"] = "gain = H2(p) - H2(p / q)"
        self.assertTrue(run(mc.check_observe, self.m))

    @unittest.skipUnless(HAVE_DATA, "data/ is not unpacked")
    def test_reflectivity_at_the_old_assumption(self):
        """With every quantile at 0.14 the documented ratio of 0.71 could not come out."""
        r = self.m["priors"]["reflectivity"]
        r["pv"] = [0.14] * len(r["p"])
        failed = run(mc.check_spitzer, self.m)
        self.assertTrue(any("21 quantiles" in f for f in failed))
        self.assertTrue(any("size at the median reflectivity" in f for f in failed))

    @unittest.skipUnless(HAVE_DATA, "data/ is not unpacked")
    def test_a_named_target_recorded_too_high(self):
        t = next(t for t in self.m["missions"]["surface"]["named"] if t["designation"] == "2021 UH2")
        t["p"] = 0.6
        self.assertTrue(any("2021 UH2" in f for f in run(mc.check_missions, self.m)))


class Fixed(unittest.TestCase):
    """What the check of 2026-11-25 changed."""

    @classmethod
    def setUpClass(cls):
        cls.m = mc.load_all()
        cls.text = {n: read(os.path.join(mc.METHOD, n + ".toml")) for n in cls.m}
        cls.doc = read(os.path.join(ROOT, "docs", "method.md"))
        cls.doc_value = read(os.path.join(ROOT, "docs", "method-value.md"))

    def test_keck_mass_is_not_called_the_largest(self):
        """verify-capability.md row 52."""
        self.assertNotIn("largest mass any capture", self.text["missions"])
        gate = next(g for g in self.m["missions"]["capture"]["gates"] if g["id"] == "mass")
        self.assertIn("only this one capture study was read", gate["source"])

    def test_2022_dc5_is_not_30_m_in_every_draw(self):
        t = next(t for t in self.m["missions"]["surface"]["named"] if t["designation"] == "2022 DC5")
        self.assertEqual(t["status"], "untested")
        self.assertLess(t["p"], 1.0)
        self.assertNotIn("every draw", t["why"])

    def test_examples_carry_their_inputs(self):
        for ex in self.m["value"]["example"]:
            self.assertIn("h", ex["inputs"], ex["id"])
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import value_examples
        for ex in self.m["value"]["example"]:
            ref = value_examples.EXAMPLES[ex["id"]]
            for k, v in ex["inputs"].items():
                self.assertEqual(ref[k], v, (ex["id"], k))

    def test_iron_mixes_are_called_a_judgement(self):
        v = self.m["value"]
        for name in ("iron_low", "iron_high"):
            self.assertTrue(v["mix"][name]["basis"].startswith("a judgement, not a bound"), name)
            self.assertTrue(all(isinstance(x, float) for k, x in v["mix"][name].items() if k != "basis"), "a mix table holds shares and its basis only")
        iron = next(s for s in v["statement"] if s["id"] == "iron_rich")
        self.assertIn("an assumed mix of metals", iron["template"])
        self.assertNotIn("bounded", self.doc_value.split("## 12.")[0])
        self.assertIn("Neither is done", self.doc_value)
        self.assertIn("applied in part", self.doc_value)

    def test_z_class_is_not_called_differentiated(self):
        basis = self.m["value"]["kinds"]["other"]["basis"]
        self.assertIn("13% are D, T or Z: dark and primitive.", basis)
        self.assertIn("43% are V or A: melted, so nothing counts.", basis)

    def test_colour_label_disagreement_is_quoted_as_measured(self):
        self.assertNotIn("a third of colour-based C labels", self.text["value"])
        self.assertNotIn("A third of colour-based C labels", self.doc_value)

    def test_supply_is_not_called_trade(self):
        self.assertNotIn("which trade about", self.text["value"] + self.doc_value)

    def test_joint_weights_are_not_called_exact(self):
        self.assertNotIn("returns central exactly", self.text["priors"])
        self.assertNotIn("central shares exactly", self.doc)

    def test_faint_end_caveats_are_in_the_document(self):
        self.assertIn("Whether fainter objects reflect more", self.doc)
        self.assertIn("The upper bound on C fainter than H 26", self.doc)

    def test_orbit_code_is_not_called_pointable(self):
        """JPL flags some windows of code 4 and 5 objects survey-only and lists pointable ones at code 6."""
        rung = self.m["ladder"]["rung"]["found_again"]
        for s in rung["state"]:
            self.assertNotIn("point a telescope", s["text"])
            self.assertNotIn("survey would have to", s["text"])
        by_kind = {s["window"]: s["text"] for s in rung["suffix"]}
        self.assertEqual(sorted(by_kind), ["none", "pointable", "survey_only"])
        self.assertIn("too uncertain to point at", by_kind["survey_only"])
        self.assertIn("no observing window through 2045", by_kind["none"])
        # the window and its date are in the tracking row; the rung adds a sentence only when JPL's own test
        # says the code is not enough, and says nothing when a telescope can be pointed at it
        self.assertEqual(by_kind["pointable"], "")
        for text in by_kind.values():
            self.assertNotIn("{win_", text)
            self.assertNotIn("now", text.lower().split())
        for mission in ("surface", "capture"):
            gate = next(g for g in self.m["missions"][mission]["gates"] if g["id"] == "findable")
            self.assertEqual(gate["label"], "Orbit condition code ≤ 5")               # the label names the test
            self.assertNotIn("find again", gate["label"])

    def test_water_sentence_is_dated(self):
        st = next(s for s in self.m["value"]["statement"] if s["id"] == "water_market")
        self.assertEqual(st["template"], "As of 2026-11-21, we found nobody buying water in orbit.")

    def test_tianwen_period_in_both_units(self):
        tw = next(f for f in self.m["ladder"]["fact"] if f["id"] == "tianwen_2")
        self.assertAlmostEqual(tw["asteroid_period_h"] * 60, tw["asteroid_period_min"], delta=0.05)


if __name__ == "__main__":
    unittest.main()
