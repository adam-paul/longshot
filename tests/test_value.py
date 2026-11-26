"""What is in the rock: longshot/value.py against method/v0_1/value.toml and its reference implementation.

Run: uv run python -m unittest tests.test_value

  single draws   every [[check]] in value.toml, to the six places the file prints
  reference      the same draws and seed through tools/value_examples.py and through value.py: the same figures
  examples       the three worked examples of docs/method-value.md section 9: exactly at the file's own
                 200,000 draws and seed, and within the stated tolerance at 20,000 draws
  record         the block a record carries, and that no mean, median or middle quantile is in it
"""
from __future__ import annotations

import importlib.util
import math
import os
import unittest

from longshot import config, draws, method, model, value
from tests.test_model import diameter, fact, make, period

M = method.load()
V = M.value


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(str(config.ROOT), "tools", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REF = load_tool("value_examples")
FORBIDDEN = ("mean", "median", "expected", "q50", "average")


def numbers(x, path=""):
    """(path, number) for every number in a nested export."""
    if isinstance(x, dict):
        for k, v in x.items():
            yield from numbers(v, f"{path}.{k}" if path else k)
    elif isinstance(x, bool):
        yield path, x
    elif isinstance(x, (int, float)):
        yield path, x


def keys(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from keys(v)
    elif isinstance(x, list):
        for v in x:
            yield from keys(v)


class SingleDraws(unittest.TestCase):
    def test_every_check_in_the_method_file(self):
        self.assertGreaterEqual(len(V["check"]), 12)
        for c in V["check"]:
            u = tuple(c["u"][k] for k in value.U_NAMES)
            got = value.draw_value(M, c["class"], c["reflectivity"], c["diameter_m"], c["density_kg_m3"], u,
                                   c["size_measured"])
            self.assertEqual(len(got), 3)
            for scenario, (g, want) in enumerate(zip(got, c["expect"])):
                self.assertEqual(g["material"], want["material"], f"{c['id']} {scenario}")
                for k in ("mass_t", "kg", "usd", "water_t"):
                    self.assertAlmostEqual(g[k], want[k], delta=1e-6 + 1e-9 * abs(want[k]),
                                           msg=f"{c['id']} scenario {scenario} {k}")

    def test_by_hand_one_stony_case(self):
        # docs/method-value.md 9.1: reflectivity 0.273 at H 26.2 is 14.64 m; H chondrite at 4.805 ppm
        mass = math.pi / 6 * 14.64 ** 3 * 2550 / 1000
        kg = mass * (3.32 + (6.29 - 3.32) * 0.5) / 1000
        prices = V["prices"]["usd_per_kg"]
        mix = V["mix"]["ordinary_chondrite"]
        usd_high = sum(kg * mix[el] * prices[el][2] for el in V["counted"]["priced"])
        got = value.draw_value(M, "S", 0.273, 14.64, 2550.0, (0.1, 0.5, 0.5, 0.5, 0.5, 0.5), True)
        self.assertAlmostEqual(got[2]["kg"], kg, places=9)
        self.assertAlmostEqual(got[2]["usd"], usd_high, places=4)
        self.assertAlmostEqual(got[2]["kg"], 20.131, places=3)
        self.assertAlmostEqual(got[2]["usd"], 1_594_032, delta=1)
        small = value.draw_value(M, "S", 0.273, 14.64, 2550.0, (0.1, 0.5, 0.5, 0.5, 0.5, 0.5), False)
        self.assertAlmostEqual(small[0]["kg"], 0.745, places=3)            # low: 3 times smaller, 27 times lighter
        self.assertAlmostEqual(small[2]["kg"], kg, places=9)               # high: as drawn

    def test_the_market_cap_stops_dollars_not_kilograms(self):
        free = value.draw_value(M, "S", 0.25, 300.0, 2500.0, (0.1, 0.5, 0.5, 0.5, 0.5, 0.5), True)[2]
        caps = sum(V["market"]["cap_kg"][el] * V["prices"]["usd_per_kg"][el][2] for el in V["counted"]["priced"])
        self.assertAlmostEqual(free["usd"], caps, places=2)                # every metal at its cap
        self.assertGreater(free["usd_uncapped"], 3 * free["usd"])
        self.assertGreater(free["kg"], 100_000)

    def test_water_only_in_dark_hydrated_rock(self):
        u = (0.5, 0.5, 0.5, 0.5, 0.2, 0.5)
        dark = value.draw_value(M, "C", 0.05, 34.2, 1600.0, u, True)
        self.assertTrue(all(s["water_t"] > 0 for s in dark))
        self.assertTrue(all(s["kg"] == 0 for s in dark))                    # dark rock: no metal grains counted
        bright = value.draw_value(M, "C", 0.2, 34.2, 1600.0, u, True)
        self.assertTrue(all(s["water_t"] == 0 and s["kg"] == 0 for s in bright))
        stony = value.draw_value(M, "S", 0.05, 34.2, 1600.0, u, True)
        self.assertTrue(all(s["water_t"] == 0 for s in stony))


class AgainstTheReference(unittest.TestCase):
    def test_same_draws_same_figures(self):
        ref_method = REF.load_method()
        for example_id, measured, label in ((1, False, None), (2, False, "S/Q"), (3, True, None)):
            rows = REF.reference_draws(ref_method, example_id, 6000)
            seed = f"test seed {example_id}"
            want = REF.summarise(ref_method, rows, measured, seed)
            got = value.summarise(M, rows, measured, seed)
            want_numbers, got_numbers = dict(numbers(want)), dict(numbers(got))
            self.assertEqual(set(got_numbers), set(want_numbers), example_id)
            for path, w in want_numbers.items():
                g = got_numbers[path]
                if isinstance(w, bool):
                    self.assertIs(g, w, path)
                else:
                    self.assertAlmostEqual(g, w, delta=1e-9 * max(1.0, abs(w)), msg=f"example {example_id} {path}")
            self.assertEqual(got["basis"], want["basis"])
            self.assertEqual(value.statement_pairs(M, got, measured, label),
                             REF.statement_pairs(ref_method, want, measured, label))

    def test_a_dict_or_a_method_gives_the_same(self):
        rows = REF.reference_draws(V, 1, 2000)
        self.assertEqual(value.summarise(V, rows, False, "s"), value.summarise(M, rows, False, "s"))

    def test_formatting_matches_the_reference(self):
        for x in (0.0004, 0.115, 0.262, 0.95, 1.0, 2.8, 20.1, 91.5, 186.0, 999.0, 1402.3, 3750.8, 221999.0, 2.5e7):
            for up in (True, False):
                self.assertEqual(value.fmt_kg(x, up), REF.fmt_kg(x, up), (x, up))
                self.assertEqual(value.fmt_tonnes(x, up), REF.fmt_tonnes(x, up), (x, up))
                self.assertEqual(value.fmt_usd(x * 1000, up), REF.fmt_usd(x * 1000, up), (x, up))
        for lo, hi in ((0.0, 0.004), (0.996, 1.0), (0.305, 0.359), (0.402, 0.404), (0.002, 0.039), (0.99, 0.999)):
            self.assertEqual(value.fmt_count(lo, hi), REF.fmt_count(lo, hi), (lo, hi))
        for lo, hi in ((49.8, 157227.0), (157.37, 4.0e5), (150.0, 1.1e6), (4.0e4, 1.6e5), (3.0e6, 4.0e9), (20.0, 700.0)):
            self.assertEqual(value.fmt_usd_range(lo, hi), REF.fmt_usd_range(lo, hi), (lo, hi))
        for lo, hi in (("1 tonne", "30 tonnes"), ("20 tonnes", "10,000 tonnes"), ("400 g", "2 kg")):
            self.assertEqual(value.fmt_range(lo, hi), REF.fmt_range(lo, hi), (lo, hi))

    def test_a_dollar_range_cannot_be_misread(self):
        """321 pages printed '($40 to $160 thousand)' for a low end of forty dollars."""
        self.assertEqual(value.fmt_usd_range(49.80, 157227.0), "$40 to $160,000")        # 2026 QQ8
        self.assertEqual(value.fmt_usd_range(157.37, 4.0e5), "$150 to $400,000")          # 2008 TC3
        self.assertEqual(value.fmt_usd_range(150.0, 1.1e6), "$150 to $1,100,000")         # 2021 GC8
        self.assertEqual(value.fmt_usd_range(4.0e4, 1.6e5), "$40 thousand to $160 thousand")
        self.assertEqual(value.fmt_usd_range(3.0e6, 4.0e9), "$3 million to $4 billion")
        self.assertEqual(value.fmt_usd_range(20.0, 700.0), "$20 to $700")
        import re
        for h in (26.2, 28.5, 31.4):
            for s_ in model.run_one(make(f"usd{h}", h=h), M).value["statements"]:
                # no "$N to $M word" where N has no scale word of its own
                self.assertIsNone(re.search(r"\$[\d.,]+ to \$[\d.,]+ (thousand|million|billion)", s_), s_)

    def test_one_tonne_is_singular(self):
        self.assertEqual(value.fmt_tonnes(0.95, True), "1 tonne")
        self.assertEqual(value.fmt_tonnes(1.0, False), "1 tonne")
        self.assertEqual(value.fmt_tonnes(1.3, True), "1.3 tonnes")
        self.assertEqual(value.fmt_kg(1000.0, False), "1 tonne")
        self.assertEqual(value.fmt_range("1 tonne", "30 tonnes"), "1 to 30 tonnes")
        self.assertEqual(value.fmt_range("600 kg", "1 tonne"), "600 kg to 1 tonne")


class WorkedExamples(unittest.TestCase):
    """docs/method-value.md section 9 and value.toml section 11."""

    def run_example(self, example, n, seed):
        ex = REF.EXAMPLES[example["id"]]
        rows = REF.reference_draws(V, example["id"], n)
        got = value.summarise(M, rows, ex["size_measured"], seed)
        return got, value.statements(M, got, ex["size_measured"], ex.get("class_label"))

    def test_exact_at_the_draws_and_seed_the_file_was_written_with(self):
        self.assertEqual(len(V["example"]), 3)
        for example in V["example"]:
            seed = f"longshot value example {example['id']} value method {V['meta']['method']}"
            got, sentences = self.run_example(example, example["draws"], seed)
            self.assertEqual(sentences, example["statements"], example["title"])
            for part in ("metal", "iron_rich", "water"):
                want = dict(numbers(example[part]))
                have = dict(numbers(got[part]))
                self.assertEqual(set(have), set(want), f"example {example['id']} {part}")
                for path, w in want.items():
                    if isinstance(w, bool):
                        self.assertIs(have[path], w, path)
                    else:
                        self.assertAlmostEqual(have[path], w, delta=2e-6 * max(1.0, abs(w)),
                                               msg=f"example {example['id']} {part}.{path}")

    def test_within_the_stated_tolerance_at_20000_draws(self):
        # "at 20,000 draws, counts within 1 of 100 and other figures within 15%": the reference draws and the
        # reference seed, as tests/test_method_value.py runs the reference itself
        for example in V["example"]:
            seed = f"longshot value example {example['id']} value method {V['meta']['method']}"
            got, _ = self.run_example(example, 20000, seed)
            for part in ("metal", "iron_rich", "water"):
                want = dict(numbers(example[part]))
                have = dict(numbers(got[part]))
                for path, w in want.items():
                    name = f"example {example['id']} {part}.{path}"
                    if isinstance(w, bool):
                        self.assertIs(have[path], w, name)
                    elif path.startswith("p_"):
                        self.assertAlmostEqual(have[path], w, delta=0.01, msg=name)
                    elif w == 0:
                        self.assertEqual(have[path], 0, name)
                    else:
                        # example 2's iron-rich range rests on the mislabelled draws alone, about 1 in 80
                        thin = part == "iron_rich" and "label_error" in example["inputs"]
                        self.assertAlmostEqual(have[path] / w, 1.0, delta=0.35 if thin else 0.15, msg=name)


class RecordBlock(unittest.TestCase):
    def test_shape_and_no_middle_figure(self):
        r = model.run_one(make("v1", h=26.2), M)
        v = r.value
        self.assertEqual(list(v), ["metal", "iron_rich", "water", "basis", "statements", "statement_ids", "table"])
        self.assertEqual(set(v["metal"]), {"p_nothing", "p_nothing_lo", "p_nothing_hi", "kg", "usd", "capped"})
        self.assertEqual(set(v["metal"]["usd"]), {"q05", "q25", "q75", "q95"})
        self.assertEqual(set(v["metal"]["kg"]), {"q05", "q25", "q75", "q95"})
        self.assertEqual(set(v["water"]["tonnes"]), {"q05", "q95"})
        self.assertEqual(set(v["iron_rich"]["usd"]), {"q05", "q95"})
        for k in keys(v):
            self.assertFalse(any(word in k.lower() for word in FORBIDDEN), k)
        self.assertEqual(v["basis"], V["exports"]["basis"]["text"])
        self.assertEqual(len(v["statements"]), len(v["statement_ids"]))
        self.assertEqual(v["statement_ids"][0], "metal_none")
        self.assertEqual(v["statement_ids"][-1], "water_market")
        self.assertEqual(v["statements"][-1], "As of 2026-11-21, we found nobody buying water in orbit.")
        for s in v["statements"]:
            self.assertNotIn("{", s)
            self.assertNotRegex(s.lower(), r"\b(worth|value|mean|median|expected)\b")

    def test_ranges_are_ordered_and_one_sided(self):
        v = model.run_one(make("v2", h=24.0), M).value
        metal = v["metal"]
        self.assertTrue(metal["p_nothing_lo"] <= metal["p_nothing"] <= metal["p_nothing_hi"])
        self.assertTrue(metal["kg"]["q05"] <= metal["kg"]["q25"] <= metal["kg"]["q75"] <= metal["kg"]["q95"])
        self.assertTrue(metal["usd"]["q05"] <= metal["usd"]["q25"] <= metal["usd"]["q75"] <= metal["usd"]["q95"])
        self.assertGreater(metal["p_nothing"], 0.25)                 # so the lower quartile of all cases is nothing
        self.assertEqual(metal["kg"]["q25"], 0)
        self.assertNotIn("metal_over", v["statement_ids"])
        self.assertTrue(v["water"]["p_nothing_lo"] <= v["water"]["p_nothing"] <= v["water"]["p_nothing_hi"])
        self.assertLess(v["water"]["tonnes"]["q05"], v["water"]["tonnes"]["q95"])

    def test_about_the_worked_example_for_h_26_2(self):
        # the pipeline's own draws for H 26.2 with nothing measured, against example 1 (200,000 reference draws):
        # 2,000 draws, so the tails move by up to 30% (docs/method-value.md section 9)
        v = model.run_one(make("v3", h=26.2), M).value
        want = V["example"][0]
        self.assertAlmostEqual(v["metal"]["p_nothing"], want["metal"]["p_nothing"], delta=0.03)
        self.assertAlmostEqual(v["water"]["p_nothing"], want["water"]["p_nothing"], delta=0.02)
        self.assertAlmostEqual(v["metal"]["kg"]["q75"] / want["metal"]["kg"]["q75"], 1.0, delta=0.15)
        self.assertAlmostEqual(v["metal"]["kg"]["q95"] / want["metal"]["kg"]["q95"], 1.0, delta=0.30)
        self.assertEqual(v["metal"]["kg"]["q05"], 0)

    def test_a_measured_size_drops_the_three_times_smaller_allowance(self):
        measured = model.run_one(make("v4", h=22.7, size=[diameter(60.0, 50.0, 70.0)],
                                      surface=[fact("class", "S", "ssodnet")]), M).value
        guessed = model.run_one(make("v4", h=22.7, surface=[fact("class", "S", "ssodnet")]), M).value
        over = dict(zip(measured["statement_ids"], measured["statements"]))["metal_over"]
        self.assertNotIn("a third of what its brightness suggests", over)
        self.assertIn("a third of what its brightness suggests",
                      dict(zip(guessed["statement_ids"], guessed["statements"]))["metal_over"])
        # 27 times lighter in the low scenario when the size is a guess
        self.assertLess(guessed["metal"]["kg"]["q25"], measured["metal"]["kg"]["q25"] / 5)
        # the sentence stands alone: it says what the figure is a figure of
        self.assertIn("in the rock, before any cost", over)

    def test_a_measured_class_leaves_a_chance_of_nothing_and_prints_it_first(self):
        """The review: 164 S/Q entries held a nineteen-in-twenty floor in dollars beside a zero chance of nothing
        and a sentence saying the class is in doubt for 21 of 100."""
        for quality, low, high in (("Bus-DeMeo Spec VISNIR", 0.05, 0.125), ("Sergeyev Phot VIS", 0.10, 0.21)):
            v = model.run_one(make("v5", h=26.2, surface=[fact("class", "Sq", "ssodnet", quality=quality)]), M).value
            self.assertEqual(v["statement_ids"][0], "metal_none", quality)        # the chance of nothing, first
            self.assertTrue(v["statements"][0].startswith("Of 100 like it, "))
            self.assertTrue(low <= v["metal"]["p_nothing_lo"] <= v["metal"]["p_nothing_hi"] <= high, v["metal"])
            # more than 1 in 20 hold nothing, so no figure is stated as a nineteen-in-twenty floor
            self.assertEqual(v["metal"]["usd"]["q05"], 0.0)
            self.assertEqual(v["metal"]["kg"]["q05"], 0.0)
            for text in v["statements"]:
                self.assertNotIn("nineteen in twenty over", text)
                self.assertNotIn("Colour and spectral surveys disagree", text)       # the doubt is in the numbers now
        # a label that is not S: the other way round
        v = model.run_one(make("v6", h=24.0, surface=[fact("class", "C", "ssodnet", quality="Bus Spec VIS")]), M).value
        self.assertEqual(v["statement_ids"][0], "metal_none")
        self.assertTrue(0.80 <= v["metal"]["p_nothing_lo"] <= v["metal"]["p_nothing_hi"] <= 0.90, v["metal"])

    def test_the_caveat_about_s_q_surveys_is_printed_nowhere(self):
        for r in (make("c1", h=20.0, surface=[fact("class", "B", "ssodnet")]),
                  make("c2", h=26.2, surface=[fact("class", "V", "ssodnet")]), make("c3", h=26.2)):
            for text in model.run_one(r, M).value["statements"]:
                self.assertNotIn("S/Q against the rest", text)
        self.assertNotIn("caveat", {k for s_ in V["statement"] for k in s_})

    def test_the_seed_is_the_brightness_when_nothing_about_the_rock_is_measured(self):
        """DESIGN.md section 7: 'For an unobserved asteroid the tag depends only on its brightness.'"""
        a = model.run_one(make("same", h=25.0), M).value
        b = model.run_one(make("other", h=25.0), M).value
        self.assertEqual(a, b)                                       # two keys, one brightness: one price tag
        self.assertNotEqual(a["metal"]["kg"], model.run_one(make("same", h=25.1), M).value["metal"]["kg"])
        # with a class measured each is its own object, seeded by its key
        cls = [fact("class", "S", "ssodnet")]
        c = model.run_one(make("same", h=25.0, surface=cls), M).value
        d = model.run_one(make("other", h=25.0, surface=cls), M).value
        self.assertEqual(c, model.run_one(make("same", h=25.0, surface=cls), M).value)
        self.assertNotEqual(c["metal"]["kg"], d["metal"]["kg"])

    def test_spin_changes_nothing_in_the_rock(self):
        a = model.run_one(make("spin", h=25.0), M).value
        b = model.run_one(make("spin", h=25.0, spin=[period(0.05)]), M).value
        self.assertEqual(a, b)

    def test_the_table_says_what_the_statements_say(self):
        """value.table replaces the mockup's hand-typed rows: each figure is one a statement prints."""
        for r in (make("t1", h=24.19), make("t2", h=19.1, size=[diameter(340.0, 300.0, 380.0)],
                                              surface=[fact("class", "Sq", "ssodnet", quality="Bus-DeMeo Spec VISNIR")]),
                  make("t3", h=26.2, surface=[fact("class", "C", "ssodnet", quality="Bus Spec VIS")])):
            v = model.run_one(r, M).value
            said = " ".join(v["statements"])
            long = lambda s: s.replace(" t", " tonnes").replace("1 tonnes", "1 tonne")
            t = v["table"]
            for part in ("metal", "water"):
                cells = t[part]["cells"]
                self.assertEqual(sum(c["n"] for c in cells), 100, (r.key, part))
                order = [c for c in ("none", "none_or_some", "some", "iron_rich_or_not", "iron_rich")]
                self.assertEqual([c["id"] for c in cells], [c for c in order if c in {x["id"] for x in cells}])
                self.assertEqual([c["label"] for c in cells], [V["table"]["cells"][c["id"]] for c in cells])
            for row in t["metal"]["rows"]:
                for k in ("kg", "usd"):
                    if row[k] and row["id"] != "iron_rich":
                        self.assertIn(long(row[k]) if k == "kg" else row[k], said, (r.key, row))
            ids = [row["id"] for row in t["metal"]["rows"]]
            self.assertEqual(ids[0], "none")
            self.assertEqual(ids[-1], "iron_rich")
            self.assertEqual(t["metal"]["rows"][0]["of100"],
                             value.cell_count(v["metal"]["p_nothing_lo"], v["metal"]["p_nothing_hi"]))
            self.assertIn("As of 2026-11-21, we found nobody buying water in orbit.", t["notes"])
            for k in keys(t):
                self.assertFalse(any(word in k.lower() for word in FORBIDDEN), k)
        # the cells follow the bands: 37 to 43 hold nothing, 1 to 6 iron-rich -> 37, 6, 51, 5, 1
        ex = {"metal": {"p_nothing_lo": 0.3665, "p_nothing_hi": 0.427}, "iron_rich": {"p_lo": 0.01, "p_hi": 0.06},
              "water": {"p_nothing_lo": 0.9465, "p_nothing_hi": 0.965}}
        self.assertEqual(value.per100(ex), ([("none", 37), ("none_or_some", 6), ("some", 51), ("iron_rich_or_not", 5),
                                             ("iron_rich", 1)], [("none", 95), ("none_or_some", 2), ("some", 3)]))
        # two bands that would overlap once rounded still add to 100
        ex = {"metal": {"p_nothing_lo": 0.5, "p_nothing_hi": 0.9}, "iron_rich": {"p_lo": 0.05, "p_hi": 0.2},
              "water": {"p_nothing_lo": 1.0, "p_nothing_hi": 1.0}}
        metal, water = value.per100(ex)
        self.assertEqual(sum(n for _, n in metal), 100)
        self.assertTrue(all(n >= 0 for _, n in metal))
        self.assertEqual(water, [("none", 100), ("none_or_some", 0), ("some", 0)])

    def test_the_table_rows_where_the_statements_have_them(self):
        guessed = model.run_one(make("u1", h=22.7, surface=[fact("class", "S", "ssodnet")]), M).value
        rows = {r["id"]: r for r in guessed["table"]["metal"]["rows"]}
        self.assertEqual("metal_over" in guessed["statement_ids"], "over_q25" in rows)
        self.assertIn(V["table"]["notes"]["size"], guessed["table"]["notes"])     # the size is a guess
        measured = model.run_one(make("u2", h=22.7, size=[diameter(60.0, 50.0, 70.0)],
                                      surface=[fact("class", "S", "ssodnet")]), M).value
        self.assertNotIn(V["table"]["notes"]["size"], measured["table"]["notes"])
        self.assertEqual(value.fmt_tonnes(4000.0, True, short=True), "4,000 t")
        self.assertEqual(value.fmt_tonnes(2.4e7, True, short=True), "24 million t")
        self.assertEqual(value.fmt_kg(400.0, True, short=True), "400 kg")
        # a table cell: an en dash for a band and a shared unit, symbols at the ends (docs/design.md section 6)
        self.assertEqual(value.cell_count(0.3665, 0.427), "37–43")
        self.assertEqual(value.cell_count(0.40, 0.404), "40")
        self.assertEqual(value.cell_count(0.0, 0.04), "≤4")
        self.assertEqual(value.cell_count(0.99, 1.0), "≥99")
        self.assertEqual(value.cell_count(0.001, 0.002), "<1")
        self.assertEqual(value.cell_count(0.996, 0.999), ">99")
        self.assertEqual(value.cell_range("160 t", "110,000 t"), "160–110,000 t")
        self.assertEqual(value.cell_range("70 kg", "50 t"), "70 kg to 50 t")
        # every draw dry: 'all 100', and the reason as a note
        dry = model.run_one(make("u3", h=19.1, size=[diameter(340.0, 300.0, 380.0)],
                                 surface=[fact("albedo", 0.35, "jpl-sbdb", 0.3, 0.4)]), M).value
        self.assertEqual((dry["water"]["p_nothing_lo"], dry["water"]["p_nothing_hi"]), (1.0, 1.0))
        self.assertEqual(dry["table"]["water"]["rows"], [{"id": "none", "label": "None", "tonnes": None,
                                                         "of100": "100"}])
        self.assertEqual(dry["table"]["water"]["cells"], [{"id": "none", "label": "None", "n": 100}])
        self.assertIn(dict(zip(dry["statement_ids"], dry["statements"]))["water_none"], dry["table"]["notes"])

    def test_no_table_where_a_sample_stands_in(self):
        r = model.run_one(make("bn", h=20.2, designation="1999 RQ36", name="Bennu", number=101955,
                               aliases=["101955"]), M)
        self.assertIn("sample", r.value)
        self.assertNotIn("table", r.value)

    def test_no_h_no_block(self):
        self.assertEqual(model.run_one(make("none", h=None), M).value, {})
        self.assertEqual(value.block("k", None, M), {})

    def test_stage_function(self):
        records = [make("s1", h=23.0), make("s2", h=None)]
        self.assertIs(value.apply(records, M), records)
        self.assertEqual(records[0].value, value.block("s1", draws.for_record(make("s1", h=23.0), M), M))
        self.assertEqual(records[1].value, {})


if __name__ == "__main__":
    unittest.main()
