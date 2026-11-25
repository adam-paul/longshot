"""method/v0_1/value.toml and ladder.toml, and the reference implementation in tools/value_examples.py.

Four kinds of test:
  shape        the files parse; shares sum to one; every fact carries as_of, source and recheck
  corrections  no number or phrase the checkers corrected or refuted is carried
  arithmetic   derived constants and the single-draw checks, recomputed here by hand
  examples     the worked examples reproduce, and their statements follow the rules

Run: uv run python -m unittest tests.test_method_value
"""
import datetime
import importlib.util
import itertools
import math
import os
import re
import tomllib
import unittest

from longshot import config, types

ROOT = str(config.ROOT)


def load_toml(name):
    with open(os.path.join(str(config.METHOD_DIR), name), "rb") as fh:
        return tomllib.load(fh)


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VALUE = load_toml("value.toml")
LADDER = load_toml("ladder.toml")
REF = load_tool("value_examples")
INPUTS = load_tool("value_inputs")
SCENARIOS = (0, 1, 2)


def strings(node):
    """Every string in a parsed TOML tree."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


def keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from keys(v)


def printed_value_text():
    """Text a visitor can read from value.toml: statement templates and the stored example statements."""
    out = []
    for s in VALUE["statement"] + VALUE["method_statement"]:
        out += [v for k, v in s.items() if k.startswith("template") or k in ("caveat", "size_clause")]
    for ex in VALUE["example"]:
        out += ex["statements"]
    return out


def printed_ladder_text():
    out = [s["text"] for s in LADDER["sitewide"]]
    for rung in LADDER["rung"].values():
        for group in ("state", "suffix", "size"):
            for s in rung.get(group, []):
                out += [v for k, v in s.items() if k.startswith("text")]
    return out


class ValueShape(unittest.TestCase):
    def test_scenarios_are_low_central_high(self):
        self.assertEqual(VALUE["scenarios"]["order"], ["low", "central", "high"])

    def test_every_class_and_band_has_shares_summing_to_one(self):
        self.assertEqual(sorted(k for k in VALUE["kinds"]), ["C", "S", "X", "other"])
        for cls, table in VALUE["kinds"].items():
            bands = ["any"] if "any" in table else ["dark", "mid", "bright"]
            for band in bands:
                rows = table[band]
                for s in SCENARIOS:
                    self.assertAlmostEqual(sum(r["share"][s] for r in rows), 1.0, places=9,
                                           msg=f"{cls}.{band} scenario {s}")
                for r in rows:
                    self.assertIn(r["material"], VALUE["material"])
                    self.assertEqual(len(r["share"]), 3)

    def test_scenarios_are_nested(self):
        # One u_kind serves all three scenarios. A ranged share comes first and rises from low to high,
        # so a draw that holds metal in low holds it in high, and an iron-rich draw in low is iron-rich in high.
        for cls, table in VALUE["kinds"].items():
            for band, rows in table.items():
                if not isinstance(rows, list):
                    continue
                if any(len(set(r["share"])) > 1 for r in rows):
                    self.assertLessEqual(rows[0]["share"][0], rows[0]["share"][1], f"{cls}.{band}")
                    self.assertLessEqual(rows[0]["share"][1], rows[0]["share"][2], f"{cls}.{band}")
                for i in range(200):
                    u = (i + 0.5) / 200
                    picked = [REF.pick(rows, u, s)["material"] for s in SCENARIOS]
                    counted = [VALUE["material"][m]["counted"] for m in picked]
                    self.assertLessEqual(counted[0], counted[1], f"{cls}.{band} u={u}")
                    self.assertLessEqual(counted[1], counted[2], f"{cls}.{band} u={u}")
                    iron = [m == "iron_rich" for m in picked]
                    self.assertLessEqual(iron[0], iron[1])
                    self.assertLessEqual(iron[1], iron[2])

    def test_metal_rich_share_of_x_is_a_range(self):
        row = VALUE["kinds"]["X"]["mid"][0]
        self.assertEqual(row["material"], "iron_rich")
        self.assertEqual(row["share"], [0.10, 0.38, 0.60])

    def test_hydrated_shares(self):
        self.assertEqual(VALUE["kinds"]["C"]["dark"][0]["hydrated"], [0.30, 0.50, 0.77])
        for cls in ("C", "X", "other"):
            for band in ("mid", "bright"):
                for r in VALUE["kinds"][cls][band]:
                    self.assertNotIn("hydrated", r, "bound water is counted only for a dark draw")
        self.assertNotIn("hydrated", VALUE["kinds"]["S"]["any"][0])

    def test_mixes_sum_to_one_and_osmium_is_not_priced(self):
        for name, mix in VALUE["mix"].items():
            total = sum(v for k, v in mix.items() if k != "basis")
            self.assertAlmostEqual(total, 1.0, delta=0.0015, msg=name)
        self.assertNotIn("Os", VALUE["counted"]["priced"])
        self.assertNotIn("Os", VALUE["prices"]["usd_per_kg"])
        self.assertEqual(VALUE["counted"]["unpriced"], "Os")

    def test_grade_table_is_cannon_table_2(self):
        table = VALUE["grade_table"]["iron_meteorite"]
        self.assertEqual([v for _, v in table], [6.0, 14.70, 20.75, 27.05, 34.77, 40.78, 52.88, 63.48, 91.23, 107.86, 230.0])
        self.assertEqual([q for q, _ in table], [i / 10 for i in range(11)])

    def test_water_has_no_price_anywhere(self):
        self.assertNotIn("water", VALUE["prices"])
        self.assertNotIn("usd", VALUE["exports"]["water"])
        for ex in VALUE["example"]:
            self.assertNotIn("usd", ex["water"])
        water_templates = [v for s in VALUE["statement"] if s["id"].startswith("water")
                           for k, v in s.items() if k.startswith("template")]
        self.assertTrue(water_templates)
        for t in water_templates:
            self.assertNotIn("$", t)
        self.assertIn("As of 21 November 2026 we found nobody buying water in orbit.", water_templates)

    def test_no_central_figure_is_defined_or_exported(self):
        banned_keys = {"mean", "median", "q50", "expected", "expected_value", "ev", "typical"}
        for k in keys({"exports": VALUE["exports"], "example": VALUE["example"], "check": VALUE["check"]}):
            self.assertNotIn(k.lower(), banned_keys)
        for part in ("metal", "iron_rich", "water"):
            ex = REF.summarise(VALUE, REF.reference_draws(VALUE, 1, 3000), False, "shape")[part]
            self.assertFalse(set(keys(ex)) & banned_keys)
        self.assertIn("median", VALUE["exports"]["never"])
        self.assertIn("mean", VALUE["exports"]["never"])

    def test_printed_text_never_says_worth_or_value(self):
        for text in printed_value_text() + printed_ladder_text():
            for word in ("worth", "value", "valuation", "mean", "median", "expected", "typical", "average value"):
                self.assertIsNone(re.search(rf"\b{word}\b", text, re.I), f"{word!r} in: {text}")
        self.assertEqual(VALUE["meta"]["block_label"], "Price tag")


class ValueCorrections(unittest.TestCase):
    """verify-value-inputs.md: nothing it corrected or refuted is carried."""

    def test_h_chondrite_range_uses_all_nine(self):
        g = VALUE["material"]["oc_h"]["grade_ppm"]
        self.assertEqual((g["lo"], g["hi"]), (3.32, 6.29))  # not 5.2 to 5.6

    def test_grades_match_the_table_as_typed_in_the_derivation_script(self):
        def span(groups):
            totals = [sum(INPUTS.six(v).values()) / 1000.0 for g in groups for v in INPUTS.HORAN[g].values()]
            return round(min(totals), 2), round(max(totals), 2)
        for material, groups in (("oc_h", ["H"]), ("oc_l", ["L"]), ("oc_ll", ["LL"]), ("enstatite_chondrite", ["EH", "EL"])):
            g = VALUE["material"][material]["grade_ppm"]
            self.assertEqual((g["lo"], g["hi"]), span(groups), material)
        nc = VALUE["material"]["carbonaceous"]["not_counted_grade_ppm"]
        self.assertEqual((nc["lo"], nc["hi"]), span(["CI", "CM"]))

    def test_dark_rock_metal_is_not_called_none_in_the_rock(self):
        # The row is 'in metal grains'; the 2.9 to 4.0 ppm in dark rock is named as left out.
        self.assertEqual(VALUE["counted"]["metal_phrase"], "in metal grains")
        self.assertFalse(VALUE["material"]["carbonaceous"]["counted"])
        self.assertIn("2.9 to 4.0 ppm", VALUE["counted"]["metal_not_counted"])
        for s in VALUE["statement"]:
            if s["id"] == "metal_none":
                self.assertIn("in metal grains", s["template"])
                self.assertNotIn("in the rock", s["template"])

    def test_price_basis_is_not_one_days_quote(self):
        self.assertEqual(VALUE["prices"]["years"], [2021, 2022, 2023, 2024, 2025])
        per_oz = VALUE["prices"]["usd_per_troy_ounce"]
        g = VALUE["prices"]["g_per_troy_ounce"]
        for el, by_year in per_oz.items():
            lo, mid, hi = VALUE["prices"]["usd_per_kg"][el]
            self.assertAlmostEqual(lo, min(by_year) * 1000 / g, delta=1.0)
            self.assertAlmostEqual(hi, max(by_year) * 1000 / g, delta=1.0)
            self.assertAlmostEqual(mid, sum(by_year) / len(by_year) * 1000 / g, delta=1.0)
            self.assertEqual(by_year, [INPUTS.USGS[el][y] for y in VALUE["prices"]["years"]])
        # The 20 November 2026 dealer quote for iridium ($327,938 per kg) is in no scenario.
        self.assertLess(max(VALUE["prices"]["usd_per_kg"]["Ir"]), 200000.0)

    def test_iron_is_not_priced_at_chondritic_proportions(self):
        lo, hi = VALUE["mix"]["iron_low"], VALUE["mix"]["iron_high"]
        self.assertEqual(lo["Ir"], 0.0)
        self.assertAlmostEqual(hi["Ir"], 59.5 / 230.0, delta=0.002)  # Avce
        self.assertEqual(VALUE["material"]["iron_rich"]["mix"], ["iron_low", "iron_central", "iron_high"])
        price = lambda mix, s: sum(mix[el] * VALUE["prices"]["usd_per_kg"][el][s] for el in VALUE["counted"]["priced"])
        self.assertGreater(price(hi, 2) / price(lo, 0), 2.5, "the dollar range per kilogram of iron must be wide")

    def test_market_rule_is_stated_as_a_choice(self):
        m = VALUE["market"]
        self.assertTrue(m["choice"].startswith("A choice"))
        for el, t in m["supply_t"].items():
            self.assertAlmostEqual(m["cap_kg"][el], t * 1000 * m["cap_share_of_supply"])
        self.assertEqual(m["supply_t"], {"Pt": 178.0, "Pd": 197.0, "Rh": 22.0, "Ir": 7.0, "Ru": 30.0})

    def test_refuted_and_corrected_figures_are_absent(self):
        text = " ".join(strings(VALUE))
        for banned in ("about 2% of observed", "only published forecast", "300 to 500 t", "300–500 t",
                       "would fetch", "would sell for about", "$2,924", "56/33/11", "launch ceiling", "1,500–3,300", "ULA's 2016 offer"):
            self.assertNotIn(banned, text)
        self.assertIn("4.4%", VALUE["kinds"]["X"]["iron_rich_cross_check"])
        self.assertNotIn("u_spin", text)  # the spin-raises-density rule is gone: spin changes nothing in the rock

    def test_the_three_placeholders_are_inside_the_ranges(self):
        f = VALUE["folded"]
        for k in ("metal_rich_share", "dark_reflectivity", "size_rule", "iron_proportions", "prices"):
            self.assertTrue(f[k])
        self.assertEqual(VALUE["size"]["diameter_factor"][1:], [1.0, 1.0])
        self.assertLess(VALUE["size"]["diameter_factor"][0], 0.5)
        self.assertNotIn("reflectivity", VALUE["material"]["carbonaceous"])  # no fixed dark value anywhere


class ValueArithmetic(unittest.TestCase):
    def hand(self, check, s):
        """One draw by hand, written out separately from the reference implementation."""
        u = check["u"]
        refl, cls = check["reflectivity"], check["class"]
        band = "dark" if refl < 0.10 else ("bright" if refl >= 0.30 else "mid")
        table = VALUE["kinds"][cls]
        rows = table["any"] if "any" in table else table[band]
        acc = 0.0
        for row in rows:
            acc += row["share"][s]
            if u["u_kind"] < acc:
                break
        mat = VALUE["material"][row["material"]]
        d = check["diameter_m"] * (1.0 if check["size_measured"] else VALUE["size"]["diameter_factor"][s])
        rho = check["density_kg_m3"]
        if "density_kg_m3" in mat:
            rho = mat["density_kg_m3"]["lo"] + (mat["density_kg_m3"]["hi"] - mat["density_kg_m3"]["lo"]) * u["u_rho"]
        mass_t = math.pi / 6 * d ** 3 * rho / 1000
        kg = usd = water = 0.0
        if mat["counted"]:
            if "grade_table" in mat:
                self.assertEqual(u["u_grade"], 0.5, "the hand calculation reads the table at its middle point")
                ppm = 40.78 * (mat["metal_fraction"]["lo"] + (mat["metal_fraction"]["hi"] - mat["metal_fraction"]["lo"]) * u["u_metal"])
            else:
                ppm = mat["grade_ppm"]["lo"] + (mat["grade_ppm"]["hi"] - mat["grade_ppm"]["lo"]) * u["u_grade"]
            kg = mass_t * ppm / 1000
            mix = VALUE["mix"][mat["mix"][s] if isinstance(mat["mix"], list) else mat["mix"]]
            for el in ("Pt", "Pd", "Rh", "Ir", "Ru"):
                usd += min(kg * mix[el], VALUE["market"]["cap_kg"][el]) * VALUE["prices"]["usd_per_kg"][el][s]
        if "hydrated" in row and u["u_hyd"] < row["hydrated"][s]:
            wf = mat["water_fraction"]
            water = mass_t * (wf["lo"] + (wf["hi"] - wf["lo"]) * u["u_water"])
        return row["material"], mass_t, kg, usd, water

    def test_every_single_draw_check_by_hand_and_by_the_reference(self):
        self.assertGreaterEqual(len(VALUE["check"]), 8)
        for c in VALUE["check"]:
            u = tuple(c["u"][k] for k in REF.U_NAMES)
            ref = REF.draw_value(VALUE, c["class"], c["reflectivity"], c["diameter_m"], c["density_kg_m3"], u, c["size_measured"])
            for s in SCENARIOS:
                material, mass_t, kg, usd, water = self.hand(c, s)
                e = c["expect"][s]
                self.assertEqual(e["material"], material, c["id"])
                self.assertEqual(ref[s]["material"], material, c["id"])
                for name, mine in (("mass_t", mass_t), ("kg", kg), ("usd", usd), ("water_t", water)):
                    self.assertAlmostEqual(e[name], mine, delta=max(1e-6, abs(mine) * 1e-6), msg=f"{c['id']} {name} scenario {s}")
                    self.assertAlmostEqual(ref[s][name], mine, delta=max(1e-9, abs(mine) * 1e-9), msg=f"{c['id']} {name} scenario {s}")

    def test_the_checks_say_what_their_names_say(self):
        by_id = {c["id"]: c["expect"] for c in VALUE["check"]}
        # 15 m at 2,500 kg/m3 is 4,418 t (value-inputs.md section 4, confirmed by the checker).
        self.assertAlmostEqual(by_id["stony_measured_size"][1]["mass_t"], 4417.9, delta=0.1)
        # A size from brightness is taken 3 times smaller in the low scenario: 1/27 of the mass.
        b = by_id["stony_size_from_brightness"]
        self.assertAlmostEqual(b[0]["mass_t"] / b[1]["mass_t"], 1 / 27, delta=0.0005)
        # 19.7 m at 4,500 kg/m3, 75% metal at 40.78 ppm: 18,014 t and 551 kg (value-inputs.md section 6).
        self.assertAlmostEqual(by_id["iron_rich"][1]["mass_t"], 18014, delta=1)
        self.assertAlmostEqual(by_id["iron_rich"][1]["kg"], 551, delta=0.5)
        self.assertEqual([e["kg"] for e in by_id["iron_rich"]], [by_id["iron_rich"][0]["kg"]] * 3)
        self.assertGreater(by_id["iron_rich"][2]["usd"] / by_id["iron_rich"][0]["usd"], 2.5)
        self.assertEqual([e["material"] for e in by_id["iron_rich_only_above_low_share"]],
                         ["enstatite_chondrite", "iron_rich", "iron_rich"])
        # 34.2 m at 1,400 kg/m3 is 29,323 t; hydrated only where u_hyd is under the share.
        self.assertEqual([e["water_t"] > 0 for e in by_id["dark_hydrated"]], [False, True, True])
        self.assertAlmostEqual(by_id["dark_hydrated"][1]["water_t"], 29322.8 * (0.019 + 0.105) / 2, delta=0.5)
        self.assertEqual([e["kg"] for e in by_id["dark_hydrated"]], [0.0, 0.0, 0.0])
        self.assertEqual([e["water_t"] for e in by_id["class_c_not_dark"]], [0.0, 0.0, 0.0])
        self.assertEqual([e["kg"] > 0 for e in by_id["other_grains_uncertain"]], [False, False, True])
        # Every metal over its cap: dollars equal the cap total.
        cap_total = sum(VALUE["market"]["cap_kg"][el] * VALUE["prices"]["usd_per_kg"][el][2] for el in VALUE["counted"]["priced"])
        self.assertAlmostEqual(by_id["market_cap_binds"][2]["usd"], cap_total, delta=1.0)

    def test_iron_grade_table_interpolation(self):
        t = VALUE["grade_table"]["iron_meteorite"]
        self.assertAlmostEqual(REF.table_value(t, 0.5), 40.78)
        self.assertAlmostEqual(REF.table_value(t, 0.0), 6.0)
        self.assertAlmostEqual(REF.table_value(t, 0.95), math.sqrt(107.86 * 230.0), places=6)
        self.assertAlmostEqual(REF.table_value(t, 1.0), 230.0)

    def test_quantile_is_nearest_rank(self):
        v = list(range(1, 101))
        self.assertEqual(REF.quantile(v, 0.05), 5)
        self.assertEqual(REF.quantile(v, 0.75), 75)
        self.assertEqual(REF.quantile(v, 0.95), 95)
        self.assertEqual(REF.quantile([7.0], 0.95), 7.0)

    def test_context_figures(self):
        ctx = VALUE["prices"]["context"]
        oc = VALUE["mix"]["ordinary_chondrite"]
        for s in SCENARIOS:
            mix_price = sum(oc[el] * VALUE["prices"]["usd_per_kg"][el][s] for el in VALUE["counted"]["priced"])
            self.assertAlmostEqual(ctx["mix_usd_per_kg"][s], mix_price, delta=60)
        quote = {"Pt": 1336.0, "Pd": 912.0, "Rh": 8950.0, "Ir": 10200.0, "Ru": 1900.0}
        q = sum(oc[el] * quote[el] * 1000 / VALUE["prices"]["g_per_troy_ounce"] for el in quote)
        self.assertAlmostEqual(ctx["quote_over_high"], q / ctx["mix_usd_per_kg"][2], delta=0.01)
        for s, share in ((0, ctx["iridium_and_rhodium_share_of_usd"][0]), (2, ctx["iridium_and_rhodium_share_of_usd"][1])):
            p = VALUE["prices"]["usd_per_kg"]
            got = (oc["Ir"] * p["Ir"][s] + oc["Rh"] * p["Rh"][s]) / ctx["mix_usd_per_kg"][s]
            self.assertAlmostEqual(share, got, delta=0.01)


class ValueFormat(unittest.TestCase):
    def test_under_rounds_up_and_over_rounds_down(self):
        self.assertEqual(REF.round_figure(1402890, True), 1500000)
        self.assertEqual(REF.round_figure(1402890, False), 1400000)
        self.assertEqual(REF.round_figure(8058488, True), 9000000)
        self.assertEqual(REF.round_figure(8058488, False), 8000000)
        self.assertEqual(REF.round_figure(21.26, True), 22)
        self.assertEqual(REF.round_figure(300.0, True), 300)
        self.assertEqual(REF.round_figure(0.0, True), 0)
        for x in (0.0123, 0.9, 1.0, 2.999, 3.0, 47.2, 999.0, 1001.0, 5.5e9):
            self.assertGreaterEqual(REF.round_figure(x, True), x * (1 - 1e-9))
            self.assertLessEqual(REF.round_figure(x, False), x * (1 + 1e-9))
            self.assertLess(REF.round_figure(x, True) / x, 1.34)

    def test_words(self):
        self.assertEqual(REF.fmt_usd(1402890, True), "$1.5 million")
        self.assertEqual(REF.fmt_usd(8058488, True), "$9 million")
        self.assertEqual(REF.fmt_usd(5020, False), "$5 thousand")
        self.assertEqual(REF.fmt_usd(640, False), "$600")
        self.assertEqual(REF.fmt_usd(3.83e9, True), "$4 billion")
        self.assertEqual(REF.fmt_kg(0.26, False), "260 g")
        self.assertEqual(REF.fmt_kg(91.5, True), "100 kg")
        self.assertEqual(REF.fmt_kg(1402.3, True), "1.5 tonnes")
        self.assertEqual(REF.fmt_tonnes(7916, True), "8,000 tonnes")
        self.assertEqual(REF.fmt_tonnes(0.4, False), "400 kg")
        self.assertEqual(REF.fmt_range("12 tonnes", "8,000 tonnes"), "12 to 8,000 tonnes")
        self.assertEqual(REF.fmt_range("2.8 kg", "3 tonnes"), "2.8 kg to 3 tonnes")
        self.assertEqual(REF.fmt_range("$70 thousand", "$230 million"), "$70 thousand to $230 million")

    def test_counts(self):
        self.assertEqual(REF.fmt_count(0.3052, 0.359), "31 to 36")
        self.assertEqual(REF.fmt_count(0.125, 0.125), "about 13")  # halves round up, not to even
        self.assertEqual(REF.fmt_count(0.401, 0.404), "about 40")
        self.assertEqual(REF.fmt_count(0.0, 0.004), "fewer than 1")
        self.assertEqual(REF.fmt_count(0.996, 1.0), "more than 99")
        self.assertEqual(REF.fmt_count(0.002, 0.013), "up to 1")
        self.assertEqual(REF.fmt_count(0.993, 0.997), "99 or more")


class ValueExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = {ex["id"]: REF.run_example(VALUE, ex["id"], 20000) for ex in VALUE["example"]}

    def test_three_examples_cover_the_brief(self):
        self.assertEqual([ex["id"] for ex in VALUE["example"]], [1, 2, 3])
        self.assertIn("26.2", VALUE["example"][0]["title"])
        self.assertIn("S-type", VALUE["example"][1]["title"])
        self.assertIn("60 m", VALUE["example"][2]["title"])

    def test_examples_reproduce_at_a_tenth_of_the_draws(self):
        def flat(d, pre=""):
            for k, v in d.items():
                if isinstance(v, dict):
                    yield from flat(v, pre + k + ".")
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    yield pre + k, v
        for ex in VALUE["example"]:
            _, got, _ = self.small[ex["id"]]
            for part in ("metal", "iron_rich", "water"):
                want, have = dict(flat(ex[part])), dict(flat(got[part]))
                self.assertEqual(sorted(want), sorted(have), f"example {ex['id']} {part}")
                for k, v in want.items():
                    if k.startswith("p_"):
                        self.assertAlmostEqual(have[k], v, delta=0.01, msg=f"example {ex['id']} {part}.{k}")
                    else:
                        # the iron-rich range of example 2 rests on its mislabelled draws alone, about 1 in 80
                        tol = 0.35 if part == "iron_rich" and "label_error" in ex["inputs"] else 0.15
                        self.assertAlmostEqual(have[k], v, delta=tol * v + 1e-9, msg=f"example {ex['id']} {part}.{k}")
                self.assertEqual(got["metal"]["capped"], ex["metal"]["capped"])

    def test_basis_is_one_printable_string_with_the_price_years(self):
        _, got, _ = self.small[1]
        self.assertIsInstance(got["basis"], str)
        self.assertIn("2021–2025", got["basis"])
        self.assertIn("USGS", got["basis"])
        self.assertNotIn("2026-11-20", got["basis"])

    def test_draws_are_deterministic(self):
        a = REF.reference_draws(VALUE, 1, 500)
        b = REF.reference_draws(VALUE, 1, 500)
        self.assertEqual(a, b)
        self.assertEqual(REF.summarise(VALUE, a, False, "seed"), REF.summarise(VALUE, b, False, "seed"))
        self.assertNotEqual(REF.summarise(VALUE, a, False, "seed")["metal"]["kg"],
                            REF.summarise(VALUE, a, False, "another seed")["metal"]["kg"])

    def test_bounds_are_ordered(self):
        for ex in VALUE["example"]:
            for part in ("metal", "water"):
                p = ex[part]
                self.assertLessEqual(p["p_nothing_lo"], p["p_nothing"])
                self.assertLessEqual(p["p_nothing"], p["p_nothing_hi"])
            for q in (ex["metal"]["kg"], ex["metal"]["usd"]):
                self.assertLessEqual(q["q05"], q["q25"])
                self.assertLessEqual(q["q25"], q["q75"])
                self.assertLessEqual(q["q75"], q["q95"])
            self.assertLessEqual(ex["iron_rich"]["p_lo"], ex["iron_rich"]["p_hi"])

    def test_zeros_are_counted_in_the_metal_quantiles(self):
        ex = VALUE["example"][0]["metal"]
        self.assertGreater(ex["p_nothing_lo"], 0.25)
        self.assertEqual(ex["kg"]["q05"], 0.0)
        self.assertEqual(ex["kg"]["q25"], 0.0)
        self.assertEqual(ex["usd"]["q25"], 0.0)

    def test_a_spectrum_removes_the_zero_and_the_iron_rich_tail(self):
        typical, s_type = VALUE["example"][0], VALUE["example"][1]
        # a label can be wrong: the spectrum cuts the chance of nothing to about a tenth and does not remove it
        self.assertEqual(s_type["inputs"]["label_error"], VALUE["reference_draw"]["label_error_spectrum"])
        self.assertTrue(0.07 < s_type["metal"]["p_nothing_lo"] <= s_type["metal"]["p_nothing_hi"] < 0.125)
        self.assertLess(s_type["metal"]["p_nothing_hi"], typical["metal"]["p_nothing_lo"] / 3)
        self.assertLess(s_type["iron_rich"]["p_hi"], typical["iron_rich"]["p_hi"] / 2)
        # more than 1 in 20 hold nothing, so there is no nineteen-in-twenty floor, in kilograms or in dollars
        self.assertEqual(s_type["metal"]["kg"]["q05"], 0.0)
        self.assertEqual(s_type["metal"]["usd"]["q05"], 0.0)
        self.assertFalse(any("nineteen in twenty over" in text for text in s_type["statements"]))
        self.assertTrue(s_type["statements"][0].startswith("Of 100 like it, 8 to 10 hold no"))
        self.assertLess(s_type["metal"]["usd"]["q95"], typical["metal"]["usd"]["q95"])

    def test_a_measured_60_m_body_holds_far_more_and_meets_the_cap(self):
        typical, big = VALUE["example"][0], VALUE["example"][2]
        self.assertGreater(big["metal"]["kg"]["q75"] / typical["metal"]["kg"]["q75"], 20)
        self.assertTrue(big["metal"]["capped"])
        self.assertFalse(typical["metal"]["capped"])

    def test_statements_follow_the_rules(self):
        for ex in VALUE["example"]:
            st = ex["statements"]
            # the chance of nothing first
            self.assertTrue("hold no platinum-group metal in metal grains" in st[0]
                            or "carries platinum-group metal in metal grains" in st[0], st[0])
            self.assertFalse(st[0].startswith("Its class"))
            self.assertEqual(st[-1], "As of 21 November 2026 we found nobody buying water in orbit.")
            dollars = [s for s in st if "$" in s]
            self.assertTrue(dollars)
            for s in dollars:
                # the price basis and its years in the same sentence, or the iron-rich caution
                self.assertTrue("2021–2025" in s or "rest on an assumed mix of metals in irons" in s
                                or "class" in s.lower(), s)
            under = [s for s in st if "nineteen in twenty under" in s]
            self.assertEqual(len(under), 1)
            self.assertIn("in the rock, before any cost", under[0])
            self.assertIn("highest yearly average list price of 2021–2025", under[0])
            # kilograms lead, dollars follow in brackets
            self.assertRegex(under[0], r"under [\d.,]+ (kg|tonnes|g) \(\$")
            for s in st:
                if "water" in s:
                    self.assertNotIn("$", s)
        self.assertTrue(VALUE["example"][0]["statements"][0].startswith("Of 100 like it, "))
        self.assertTrue(any("of the 100 would be iron-rich" in s for s in VALUE["example"][0]["statements"]))

    def test_statement_ids_run_in_the_order_of_the_file(self):
        order = [s["id"] for s in VALUE["statement"]]
        for ex in VALUE["example"]:
            exports = {k: ex[k] for k in ("metal", "iron_rich", "water")}
            spec = REF.EXAMPLES[ex["id"]]
            ids = [i for i, _ in REF.statement_pairs(VALUE, exports, spec["size_measured"], spec.get("class_label"))]
            self.assertIn(ids[0], ("metal_none", "metal_none_measured"))
            self.assertEqual(ids.count("water_none"), 1)
            self.assertEqual(ids[-1], "water_market")
            self.assertEqual(ids, sorted(ids, key=order.index))

    def test_stored_statements_are_what_the_templates_give(self):
        # The stored numbers, pushed through the templates again, give the stored sentences.
        for ex in VALUE["example"]:
            exports = {k: ex[k] for k in ("metal", "iron_rich", "water")}
            spec = REF.EXAMPLES[ex["id"]]
            self.assertEqual(REF.statements(VALUE, exports, spec["size_measured"], spec.get("class_label")), ex["statements"])


class LadderShape(unittest.TestCase):
    def test_five_rungs_in_the_contract_order(self):
        self.assertEqual(tuple(LADDER["meta"]["order"]), types.LADDER)
        self.assertEqual(set(LADDER["rung"]), set(types.LADDER))
        self.assertEqual(LADDER["meta"]["statuses"], ["measured", "prior", "unknown"])
        for name, rung in LADDER["rung"].items():
            self.assertTrue(rung["question"].endswith("?"), name)
            self.assertTrue(rung["state"], name)
            ids = [s["id"] for s in rung["state"]]
            self.assertEqual(len(ids), len(set(ids)), name)
            for s in rung["state"]:
                self.assertTrue(s["text"].strip())
                if name != "brought_back":
                    self.assertIn(s["status"], LADDER["meta"]["statuses"])

    def test_every_fact_is_dated_sourced_and_due_a_recheck(self):
        as_of = datetime.date.fromisoformat(LADDER["meta"]["as_of"])
        ids = [f["id"] for f in LADDER["fact"]]
        self.assertEqual(len(ids), len(set(ids)))
        for f in LADDER["fact"]:
            self.assertEqual(datetime.date.fromisoformat(f["as_of"]), as_of, f["id"])
            self.assertGreater(datetime.date.fromisoformat(f["recheck"]), as_of, f["id"])
            self.assertTrue(f["source"].strip(), f["id"])
            self.assertTrue(f["read"].strip(), f["id"])

    def test_every_fact_named_by_a_template_exists(self):
        ids = {f["id"] for f in LADDER["fact"]}
        used = set()
        for rung in LADDER["rung"].values():
            for group in ("state", "suffix"):
                for s in rung.get(group, []):
                    used |= set(s.get("facts", []))
        for s in LADDER["sitewide"]:
            used |= set(s["facts"])
        self.assertTrue(used <= ids, used - ids)
        self.assertEqual(ids - used, set(), "a fact nothing prints")

    def test_every_slot_is_declared(self):
        declared = set(LADDER["slots"])
        from_facts = {"returned", "mission", "return_year", "cost", "measured_in_sample"}
        for text in printed_ladder_text():
            for slot in re.findall(r"\{(\w+)\}", text):
                self.assertIn(slot, declared | from_facts, text)
        for f in LADDER["fact"]:
            if f["kind"] == "sample_return":
                for k in ("returned", "mission", "return_year", "cost", "objects"):
                    self.assertIn(k, f, f["id"])

    def test_last_rung_uses_the_fixed_words(self):
        bb = LADDER["rung"]["brought_back"]
        self.assertEqual(bb["words"], {"done": "done three times, by space agencies",
                                       "not_yet_attempted": "not yet attempted", "proposed": "proposed"})
        for s in bb["state"]:
            if s.get("special") == "gone":                 # a body that no longer exists: nothing to bring back
                self.assertEqual(s["text"], "It no longer exists.")
                continue
            self.assertIn(s["word"], ("done", "not_yet_attempted"))
            self.assertTrue(s["text"].startswith("Grams: "), s["id"])
            if s["word"] == "done":
                self.assertRegex(s["text"], r"^Grams: done( three times, by space agencies)?[,.]", s["id"])
            else:
                self.assertTrue(s["text"].startswith("Grams: not yet attempted"), s["id"])
        last = bb["suffix"][-1]
        self.assertEqual((last["id"], last["word"]), ("more_than_grams", "proposed"))
        self.assertTrue(last["text"].startswith("Kilograms or tonnes: proposed"))

    def test_every_size_and_spin_class_has_exactly_one_grams_sentence(self):
        states = [s for s in LADDER["rung"]["brought_back"]["state"] if "special" not in s]
        for size, spin in itertools.product(LADDER["classes"]["size"], LADDER["classes"]["spin"]):
            hits = [s["id"] for s in states if size in s["size"] and spin in s["spin"]]
            self.assertEqual(len(hits), 1, f"{size}, {spin}: {hits}")
        specials = {s["special"] for s in LADDER["rung"]["brought_back"]["state"] if "special" in s}
        self.assertEqual(specials, {"sample_return_target", "in_position_target", "gone"})

    def test_done_needs_a_sampled_size(self):
        for s in LADDER["rung"]["brought_back"]["state"]:
            if s["word"] == "done" and "special" not in s:
                self.assertTrue(set(s["size"]) <= {"sampled", "may_be_sampled"}, s["id"])
            if "special" not in s and "untouched" in s["size"]:
                self.assertEqual(s["word"], "not_yet_attempted")

    def test_workable_states_cover_every_period_and_row_state(self):
        states = LADDER["rung"]["workable"]["state"]
        spans = sorted(s["period_h"] for s in states if "period_h" in s)
        undecided = [s for s in states if s.get("decides") is False]
        self.assertEqual([s["id"] for s in undecided], ["period_unreliable", "spin_conflict"])
        for s in undecided:                                  # a period graded under 2, or one the sources split on
            self.assertEqual(s["status"], "prior")
        self.assertIn("{conflict}", undecided[1]["text"])
        # a rung says what the spin means, not what the spin row already shows: no period, grade or size is repeated
        for s in states:
            for slot in ("{period}", "{grade}", "{limit}", "{d_lo}", "{m_lo}"):
                self.assertNotIn(slot, s["text"], s["id"])
        self.assertEqual(spans[0][0], 0.0)
        for a, b in zip(spans, spans[1:]):
            self.assertEqual(a[1], b[0])
        self.assertGreater(spans[-1][1], 1e6)
        self.assertEqual({s["row"] for s in states}, set(types.STATES))
        # "not checked" has its own sentence and never reads as "not measured"
        by_row = {s["row"]: s for s in states if s["row"] != "measured"}
        self.assertTrue(by_row["unchecked"]["text"].startswith("Spin not checked"))
        self.assertNotIn("not measured", by_row["unchecked"]["text"])
        self.assertTrue(by_row["prior"]["text"].startswith("Of 100 like it, {n_fast} turn faster"))


class LadderFacts(unittest.TestCase):
    def fact(self, fid):
        return next(f for f in LADDER["fact"] if f["id"] == fid)

    def test_three_sample_returns_with_corrected_masses_and_costs(self):
        returns = [f for f in LADDER["fact"] if f["kind"] == "sample_return"]
        self.assertEqual(sorted(f["id"] for f in returns), ["hayabusa", "hayabusa2", "osiris_rex"])
        o = self.fact("osiris_rex")
        self.assertEqual(o["returned_g"], 121.6)
        self.assertEqual((o["cost_usd_low"], o["cost_usd_high"]), (1.02e9, 1.16e9))
        self.assertAlmostEqual(o["cost_usd_low"] / o["returned_g"] / 1e6, 8.4, delta=0.05)
        self.assertAlmostEqual(o["cost_usd_high"] / o["returned_g"] / 1e6, 9.5, delta=0.05)
        self.assertEqual(o["cost_per_gram"], "about ten million dollars a gram, in the money of the day")
        self.assertEqual(self.fact("hayabusa2")["returned"], "5.424 ± 0.217 g")
        self.assertIn("press figure", self.fact("hayabusa")["cost_note"])
        self.assertIn("plan figure", self.fact("hayabusa2")["cost_note"])
        self.assertEqual({f["agency"] for f in returns}, {"JAXA", "NASA"})

    def test_thresholds_sit_inside_the_record(self):
        t = LADDER["thresholds"]
        returns = [f for f in LADDER["fact"] if f["kind"] == "sample_return"]
        self.assertLessEqual(t["sampled_min_m"], min(f["asteroid_size_m"] for f in returns))
        self.assertLessEqual(t["sampled_min_period_h"], min(f["asteroid_period_h"] for f in returns))
        self.assertEqual(t["touched_min_m"], self.fact("dart")["asteroid_size_m"])
        self.assertLess(self.fact("tianwen_2")["asteroid_size_m"], t["small_m"])
        self.assertGreater(self.fact("tianwen_2")["asteroid_period_min"], t["very_fast_period_min"])
        self.assertIn("not physical limits", t["judgement"])

    def test_tianwen_2_is_worded_as_the_checker_advises(self):
        f = self.fact("tianwen_2")
        self.assertEqual(f["status"], "not yet attempted; one spacecraft is in position")
        self.assertEqual(f["kind"], "in_position")
        self.assertIn("no CNSA", f["return_due_note"].replace("No CNSA", "no CNSA"))
        here = next(s for s in LADDER["rung"]["brought_back"]["state"] if s["id"] == "in_position_here")
        self.assertIn("by 21 November 2026", here["text"])
        self.assertLess(datetime.date.fromisoformat(f["recheck"]), datetime.date(2027, 1, 1))

    def test_no_universal_negative_without_we_found_and_a_date(self):
        negative = re.compile(r"\bno (spacecraft|company)\b|\bnothing has\b|\bnever\b(?! built| started)", re.I)
        for text in printed_ladder_text():
            for sentence in re.split(r"(?<=[.;])\s+", text):
                if negative.search(sentence):
                    self.assertIn("we found", sentence.lower(), sentence)
        per_asteroid = [t for t in printed_ladder_text() if "we found no" in t.lower() and t not in
                        [s["text"] for s in LADDER["sitewide"]]]
        self.assertTrue(per_asteroid)
        for t in per_asteroid:
            self.assertIn("As of 21 November 2026", t)
        self.assertTrue(LADDER["sitewide"][0]["text"].startswith("As of 21 November 2026"))

    def test_corrected_and_refuted_wording_is_absent(self):
        text = " ".join(strings(LADDER))
        printed = " ".join(printed_ladder_text())
        for banned in ("trying now", "since 2012", "$8.4 million a gram", "$8 million a gram", "declared lost",
                       "should apply", "method exists", "the project leader's figure", "largest mass any capture study",
                       "moved to 2027", "$1.4 billion for"):
            self.assertNotIn(banned, printed, banned)
        for banned in ("Under way", "under way"):
            self.assertNotIn(banned, printed)
        self.assertIn("'designed on paper since 2012' is not carried", text)
        self.assertIn("proposed since the 1990s, first costed in 2012", printed)
        self.assertIn("The chance of talking with Odin is minimal", self.fact("companies")["detail"])
        self.assertIn("Thirouin et al. 2016", LADDER["spin_limit"]["published_bar_source"])
        self.assertIn("250 to 1,300 tonnes", self.fact("keck_2012")["note"])
        self.assertIn("processing plant", self.fact("sonter_1998")["note"])

    def test_arithmetic_in_the_record(self):
        g = self.fact("osiris_rex")["returned_g"]
        self.assertEqual(round(1e6 / g, -3), 8000)
        self.assertEqual(round(self.fact("arm")["tonnes"] * 1e6 / g, -4), 110000)
        self.assertAlmostEqual(self.fact("keck_2012")["tonnes"] * 1e6 / g / 1e6, 4.1, delta=0.05)
        self.assertIn("8,000 times", self.fact("gap")["statement"])
        pt = VALUE["prices"]["usd_per_troy_ounce"]["Pt"]
        self.assertLess(g / VALUE["prices"]["g_per_troy_ounce"] * max(pt), 5000)

    def test_spin_limits(self):
        sl = LADDER["spin_limit"]
        for rho, limit in ((sl["light_rock_kg_m3"], sl["light_rock_limit_h"]), (sl["dense_rock_kg_m3"], sl["dense_rock_limit_h"])):
            self.assertAlmostEqual(math.sqrt(3 * math.pi / (6.674e-11 * rho)) / 3600, limit, delta=0.006)
        # 2022 OB5 turns in 92.5 s: 5,000 to 14,000, not "nearly two orders of magnitude".
        p_h = 92.5 / 3600
        self.assertAlmostEqual((sl["dense_rock_limit_h"] / p_h) ** 2, 5000, delta=60)
        self.assertAlmostEqual((sl["light_rock_limit_h"] / p_h) ** 2, 13750, delta=150)


class Document(unittest.TestCase):
    """docs/method-value.md says what the two files and the scripts say."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "docs", "method-value.md"), encoding="utf-8") as fh:
            cls.doc = fh.read()

    def test_worked_example_statements_are_verbatim(self):
        for ex in VALUE["example"]:
            for s in ex["statements"]:
                self.assertIn("> " + s, self.doc)

    def test_worked_example_figures(self):
        fig = lambda x: f"{x:,.2f}" if x < 10000 else f"{x:,.0f}"
        for ex in VALUE["example"]:
            m = ex["metal"]
            for q in ("q75", "q95"):
                self.assertIn(fig(m["kg"][q]) + " kg", self.doc)
                self.assertIn(f"${m['usd'][q]:,.0f}", self.doc)
            self.assertIn(f"{100 * m['p_nothing']:.1f}%", self.doc) if m["p_nothing"] else None
            if "tonnes" in ex["water"]:
                self.assertIn(f"{ex['water']['tonnes']['q95']:,.0f} t", self.doc)
        by_id = {c["id"]: c["expect"] for c in VALUE["check"]}
        for cid in ("example_1_stony", "example_1_dark", "example_3_stony", "example_3_iron_rich"):
            self.assertIn(f"`{cid}`", self.doc)
        self.assertIn(f"{by_id['example_1_stony'][2]['mass_t']:,.1f} t", self.doc)
        self.assertIn(f"{by_id['example_1_stony'][2]['kg']:.3f} kg", self.doc)
        self.assertIn(f"${by_id['example_1_stony'][2]['usd']:,.0f}", self.doc)
        self.assertIn(f"${by_id['example_1_stony'][0]['usd']:,.0f}", self.doc)
        self.assertIn(f"{by_id['example_1_dark'][1]['water_t']:,.1f} t", self.doc)
        self.assertIn(f"${by_id['example_3_stony'][2]['usd']:,.0f}", self.doc)
        self.assertIn(f"${by_id['example_3_iron_rich'][2]['usd']:,.0f}", self.doc)

    def test_tables_match_the_constants(self):
        for mat in ("oc_h", "oc_l", "oc_ll", "enstatite_chondrite"):
            g = VALUE["material"][mat]["grade_ppm"]
            self.assertIn(f"{g['lo']:.2f}–{g['hi']:.2f}", self.doc)
        for el, (lo, _, hi) in VALUE["prices"]["usd_per_kg"].items():
            self.assertIn(f"{lo:,.0f}–{hi:,.0f}", self.doc)
        for el, kg in VALUE["market"]["cap_kg"].items():
            self.assertIn(f"{kg:,.0f}", self.doc)
        for v in VALUE["grade_table"]["iron_meteorite"]:
            self.assertIn(f"{v[1]:g}" if v[1] in (6.0, 230.0) else f"{v[1]:.2f}", self.doc)
        row = VALUE["kinds"]["X"]["mid"][0]["share"]
        self.assertIn("0.10, 0.38, 0.60 iron-rich", self.doc)
        self.assertEqual(row, [0.10, 0.38, 0.60])
        self.assertIn("3 times smaller", self.doc)
        self.assertAlmostEqual(VALUE["size"]["diameter_factor"][0], 1 / 3, delta=0.001)

    def test_templates_are_quoted_as_written(self):
        st = {s["id"]: s for s in VALUE["statement"]}
        self.assertIn(st["water_market"]["template"], self.doc)
        self.assertIn(st["metal_cap"]["template"], self.doc)
        self.assertIn("in the rock, before any cost, at each metal's highest yearly average list price of 2021–2025", self.doc)
        more = LADDER["rung"]["brought_back"]["suffix"][-1]["text"]
        self.assertIn(more, self.doc)
        for f in LADDER["fact"]:
            if f["kind"] != "arithmetic":
                self.assertIn(f["recheck"], self.doc, f["id"])
        self.assertIn(LADDER["fact"][3]["status"], self.doc)

    def test_copy_rules(self):
        for word in ("worth", "valuable", "exciting", "revolutionary", "trillion"):
            self.assertIsNone(re.search(rf"\b{word}\b", self.doc.replace('says "worth"', ""), re.I), word)
        self.assertNotIn("\u2014", self.doc)  # no em dash asides


if __name__ == "__main__":
    unittest.main()
