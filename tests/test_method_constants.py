"""The method constants in method/v0_1/priors.toml, missions.toml and observe.toml.

Three kinds of test:
  shape       the files parse, every constant carries where it came from, and every file a source names exists
  arithmetic  tables are ordered, shares sum to one, formulas give the numbers written beside them
  derivation  with the data on disk, the scripts in tools/ reproduce the files exactly (skipped without data)

Run: uv run python -m unittest tests.test_method_constants
"""
import math
import os
import re
import sys
import tomllib
import unittest

from longshot import config, types

TOOLS = os.path.join(str(config.ROOT), "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

KINDS = {"measured", "quoted", "judgement"}
BANDS = ["under_20", "20_22", "22_24", "24_26", "26_28", "28_up"]
CLASSES = ["S", "C", "X", "other"]
PATH_RE = re.compile(r"\b((?:docs|tools|method|data)/[\w./+-]*\.(?:md|py|txt|csv|json|toml))")
SECTION_RE = re.compile(r"(docs/[\w./-]+\.md) sections? (\d+(?:\.\d+)?)")


def load(name):
    with open(os.path.join(str(config.METHOD_DIR), name), "rb") as fh:
        return tomllib.load(fh)


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def holds_numbers(v):
    """True for a number, a list of numbers, or a flat table or list of flat tables holding a number."""
    if is_number(v):
        return True
    if isinstance(v, list):
        return any(holds_numbers(x) for x in v)
    if isinstance(v, dict) and is_leaf_table(v):
        return any(holds_numbers(x) for x in v.values())
    return False


def is_leaf_table(d):
    """An inline table of plain values (central = { S = ... }), as opposed to a section with its own provenance."""
    return all(not isinstance(x, dict) and not (isinstance(x, list) and any(isinstance(i, dict) for i in x))
               for x in d.values()) and "kind" not in d and "source" not in d


def uncovered(node, path=""):
    """Paths of numeric constants with no kind and source beside them."""
    out = []
    table_ok = node.get("kind") in KINDS and isinstance(node.get("source"), str) and node["source"].strip()
    for k, v in node.items():
        here = f"{path}.{k}" if path else k
        own = node.get(f"{k}_kind") in KINDS and any(
            isinstance(node.get(x), str) and node[x].strip() for x in (f"{k}_source", f"{k}_from", "source"))
        if isinstance(v, dict) and not (is_leaf_table(v) and (table_ok or own)):
            out += uncovered(v, here)
            continue
        if isinstance(v, list) and v and all(isinstance(i, dict) for i in v) and any("kind" in i for i in v):
            for n, i in enumerate(v):
                out += uncovered(i, f"{here}[{n}]")
            continue
        if not holds_numbers(v):
            continue
        if not (table_ok or own):
            out.append(here)
    return out


def all_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from all_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from all_strings(v)


def all_kinds(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "kind" or k.endswith("_kind"):
                yield v
            else:
                yield from all_kinds(v)
    elif isinstance(node, list):
        for v in node:
            yield from all_kinds(v)


def h2(x):
    return 0.0 if x <= 0 or x >= 1 else -x * math.log2(x) - (1 - x) * math.log2(1 - x)


def gain(p, q):
    """observe.toml [gain].formula."""
    return 0.0 if q <= 0 else h2(p) - q * h2(p / q)


class Shape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {n: load(n) for n in ("priors.toml", "missions.toml", "observe.toml", "ledger.toml")}

    def test_header(self):
        for name, d in self.files.items():
            self.assertEqual(d["schema"], 1, name)
            self.assertEqual(d["method"], config.METHOD, name)
            self.assertEqual(d["status"], "proposal", name)

    def test_every_constant_says_where_it_came_from(self):
        for name, d in self.files.items():
            body = {k: v for k, v in d.items() if k != "schema"}
            self.assertEqual(uncovered(body), [], f"{name}: numeric constants with no kind and source")

    def test_kinds_are_the_three_allowed(self):
        for name, d in self.files.items():
            kinds = set(all_kinds(d))
            self.assertTrue(kinds, name)
            self.assertLessEqual(kinds, KINDS, name)

    def test_checker_catches_a_bare_constant(self):
        self.assertEqual(uncovered({"t": {"x": 1.0}}), ["t.x"])
        self.assertEqual(uncovered({"t": {"x": 1.0, "kind": "measured"}}), ["t.x"])
        self.assertEqual(uncovered({"t": {"x": 1.0, "kind": "guess", "source": "s"}}), ["t.x"])
        self.assertEqual(uncovered({"t": {"x": {"a": 1.0}, "kind": "quoted", "source": "s"}}), [])
        self.assertEqual(uncovered({"t": {"x": 1.0, "x_kind": "measured", "x_from": "n of m"}}), [])
        self.assertEqual(uncovered({"t": {"g": [{"preset": 2, "kind": "quoted", "source": "s"}, {"preset": 3, "kind": "quoted"}]}}),
                         ["t.g[1].preset"])
        self.assertEqual(uncovered({"t": {"named": [{"p": 0.3}]}}), ["t.named"])
        self.assertEqual(uncovered({"t": {"u": {"v": {"x": 2}}}}), ["t.u.v.x"])

    def test_every_file_a_source_names_exists(self):
        missing = set()
        for name, d in self.files.items():
            for s in all_strings(d):
                for m in PATH_RE.findall(s):
                    if m.startswith("data/") and not config.DATA.exists():
                        continue
                    if not os.path.exists(os.path.join(str(config.ROOT), m)):
                        missing.add(f"{name}: {m}")
        self.assertEqual(sorted(missing), [])

    def test_every_section_a_source_names_exists(self):
        """'docs/research/x.md section 2.3' must point at a heading numbered 2.3 in that file."""
        missing = set()
        heads = {}
        for name, d in self.files.items():
            for s in all_strings(d):
                for path, sec in SECTION_RE.findall(s):
                    if path not in heads:
                        with open(os.path.join(str(config.ROOT), path)) as fh:
                            text = fh.read()
                        heads[path] = set(re.findall(r"^#+ (?:Appendix )?(\d+(?:\.\d+)?)\.? ", text, re.M))
                    if sec not in heads[path]:
                        missing.add(f"{name}: {path} section {sec}")
        self.assertEqual(sorted(missing), [])


class Priors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load("priors.toml")

    def test_bands(self):
        self.assertEqual(self.p["bands"]["ids"], BANDS)
        e = self.p["bands"]["edges"]
        self.assertEqual(len(e), len(BANDS) - 1)
        self.assertEqual(e, sorted(e))

    def test_reflectivity_table_can_be_sampled(self):
        r = self.p["reflectivity"]
        self.assertGreaterEqual(len(r["p"]), 19)
        self.assertEqual(r["p"][0], 0.025)
        self.assertEqual(r["p"][-1], 0.975)
        self.assertTrue(all(a < b for a, b in zip(r["p"], r["p"][1:])))
        self.assertEqual(len(r["pv"]), len(r["p"]))
        self.assertTrue(all(0 < a <= b for a, b in zip(r["pv"], r["pv"][1:])))
        self.assertLess(r["pv"][-1], 1.0)
        self.assertIn(0.5, r["p"])

    def test_sizes_match_the_plan(self):
        """docs/plan.md Terms: H 22 about 100 m, H 24 about 40 m, H 26.2 about 15 m, H 27.7 about 7 m;
        measured sizes have a median 0.71 of the size at reflectivity 0.14 (AGENTS.md)."""
        r = self.p["reflectivity"]
        median = r["pv"][r["p"].index(0.5)]
        coef = self.p["size"]["coefficient_m"]
        d = lambda h: coef * 10 ** (-h / 5) / math.sqrt(median)
        self.assertAlmostEqual(math.sqrt(0.14 / median), 0.71, delta=0.015)
        for h, lo, hi in ((22.0, 93, 107), (24.0, 37, 43), (26.2, 13.5, 16), (27.7, 6.5, 8)):
            self.assertTrue(lo <= d(h) <= hi, (h, d(h)))
        # about nine in ten between half and double the median size: 5th and 95th percentile sizes
        lo95 = math.sqrt(median / r["pv"][r["p"].index(0.95)])
        hi05 = math.sqrt(median / r["pv"][r["p"].index(0.05)])
        self.assertGreater(lo95, 0.5)
        self.assertLess(hi05, 2.3)

    def test_extrapolation_is_stated(self):
        s = self.p["size"]
        self.assertEqual(s["extrapolated_fainter_than_h"], 25.0)
        self.assertEqual(s["n_measured_at_or_fainter"], 3)

    def test_h_uncertainty(self):
        h = self.p["h_uncertainty"]
        self.assertTrue(0.2 <= h["default_sigma"] <= 0.5)
        self.assertEqual(h["kind"], "measured")

    def test_class_conditional_tables(self):
        r = self.p["reflectivity"]
        self.assertEqual(sorted(r["by_class"]), sorted(CLASSES))
        for c in CLASSES:
            t = r["by_class"][c]
            self.assertEqual(len(t["pv"]), len(r["p"]), c)
            self.assertTrue(all(0 < a <= b for a, b in zip(t["pv"], t["pv"][1:])), c)
            self.assertGreater(t["n"], 0)
        med = lambda c: r["by_class"][c]["pv"][r["p"].index(0.5)]
        self.assertLess(med("C"), med("X"))
        self.assertLess(med("X"), med("S"))
        self.assertLess(med("C"), 0.10)

    def test_link_table(self):
        link = self.p["reflectivity"]["link"]
        nb = len(link["edges"]) + 1
        self.assertAlmostEqual(sum(link["all"]), 1.0, places=3)
        for c in CLASSES:
            self.assertEqual(len(link[c]), nb)
            self.assertAlmostEqual(sum(link[c]), 1.0, places=3)
            n = sum(link["counts"][c])
            self.assertEqual(n, self.p["reflectivity"]["by_class"][c]["n"])
            for share, k in zip(link[c], link["counts"][c]):
                self.assertAlmostEqual(share, k / n, places=3)
        # the bin shares are those of the quantile table: 10% of objects lie under pv 0.10
        r = self.p["reflectivity"]
        self.assertAlmostEqual(link["all"][0], 0.10, delta=0.01)
        self.assertAlmostEqual(r["pv"][r["p"].index(0.10)], 0.10, delta=0.005)

    def test_spin(self):
        s = self.p["spin"]
        self.assertEqual(s["ids"], ["under_2_2h", "under_1h", "under_10min"])
        self.assertEqual(s["thresholds_h"][:2], [2.2, 1.0])
        self.assertAlmostEqual(s["thresholds_h"][2], 10 / 60, places=6)
        self.assertEqual(sorted(s["bands"]), sorted(BANDS))
        for b in BANDS:
            for t in s["ids"]:
                v = s["bands"][b][t]
                self.assertTrue(0 <= v["low"] <= v["central"] <= v["high"] <= 1, (b, t, v))
                for k in ("low_from", "central_from", "high_from"):
                    self.assertTrue(v[k].strip(), (b, t, k))
            for k in ("low", "central", "high"):
                a, c, d = (s["bands"][b][t][k] for t in ("under_10min", "under_1h", "under_2_2h"))
                self.assertTrue(a <= c <= d, (b, k, a, c, d))
        for t in s["ids"]:
            central = [s["bands"][b][t]["central"] for b in BANDS]
            self.assertEqual(central, sorted(central), f"{t}: fainter bands must not turn slower")

    def test_spin_matches_the_research_ranges(self):
        """docs/research/verify-coverage.md section 2.4, 'Prior to use'."""
        s = self.p["spin"]["bands"]
        quoted = {"20_22": (0.1, 0.2), "22_24": (0.5, 0.8), "24_26": (0.7, 0.9), "26_28": (0.8, 0.97), "28_up": (0.8, 1.0)}
        for b, (lo, hi) in quoted.items():
            c = s[b]["under_2_2h"]["central"]
            self.assertTrue(lo <= c <= hi, (b, c))

    def test_class_shares(self):
        c = self.p["class"]
        self.assertEqual(c["ids"], CLASSES)
        self.assertEqual(sorted(c["bands"]), sorted(BANDS))
        for b in BANDS:
            t = c["bands"][b]
            self.assertAlmostEqual(sum(t["central"].values()), 1.0, places=3)
            for k in CLASSES:
                self.assertTrue(0 <= t["low"][k] <= t["central"][k] + 5e-5, (b, k))
                self.assertTrue(t["central"][k] <= t["high"][k] + 5e-5 <= 1, (b, k))
                self.assertTrue(t["low_from"][k].strip() and t["high_from"][k].strip())
                self.assertGreater(t["joint_weight"][k], 0)

    def test_joint_weights_return_the_central_shares(self):
        """Draw a reflectivity bin from link.all, then a class with weight joint_weight * P(bin | class)."""
        link = self.p["reflectivity"]["link"]
        for b in BANDS:
            t = self.p["class"]["bands"][b]
            got = {k: 0.0 for k in CLASSES}
            for i, m in enumerate(link["all"]):
                z = sum(t["joint_weight"][k] * link[k][i] for k in CLASSES)
                for k in CLASSES:
                    got[k] += m * t["joint_weight"][k] * link[k][i] / z
            for k in CLASSES:
                self.assertAlmostEqual(got[k], t["central"][k], delta=0.002, msg=(b, k))
            plain = {k: 0.0 for k in CLASSES}
            for i, m in enumerate(link["all"]):
                z = sum(t["central"][k] * link[k][i] for k in CLASSES)
                for k in CLASSES:
                    plain[k] += m * t["central"][k] * link[k][i] / z
            self.assertGreater(max(abs(plain[k] - t["central"][k]) for k in CLASSES), 0.01,
                               "the central shares used as weights would not return themselves; that is why joint_weight exists")

    def test_density(self):
        d = self.p["density"]
        for c in ("S", "C", "other"):
            self.assertTrue(0 < d[c]["lo"] < d[c]["hi"], c)
        x = d["X"]
        for part in ("dark", "mid_silicate", "mid_metal", "bright"):
            self.assertTrue(0 < x[part]["lo"] < x[part]["hi"], part)
        self.assertEqual(x["split_edges_pv"], [0.10, 0.30])
        lo, hi = x["metal_rich_share_range"]
        self.assertTrue(lo <= x["metal_rich_share_of_mid"] <= hi)
        self.assertEqual(d["C"]["lo"], min(v["lo"] for v in (d["S"], d["C"], d["other"], *[x[p] for p in ("dark", "mid_silicate", "mid_metal", "bright")])))
        self.assertEqual(x["mid_metal"]["hi"], 7500)

    def test_mass_of_a_15_m_sphere(self):
        """docs/research/value-inputs.md section 4: 15 m is 1,767 m3, 4,400 t at 2,500 kg/m3."""
        self.assertIn("pi / 6", self.p["mass"]["formula"])
        self.assertAlmostEqual(math.pi / 6 * 15 ** 3 * 2500 / 1000, 4418, delta=1)


class Missions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("missions.toml")
        cls.p = load("priors.toml")

    def gates(self, mission):
        return {g["id"]: g for g in self.m[mission]["gates"]}

    def test_two_mission_types(self):
        self.assertEqual(tuple(self.m["order"]), types.MISSIONS)
        self.assertEqual(sorted(self.gates("surface")), ["findable", "size", "spin"])
        self.assertEqual(sorted(self.gates("capture")), ["findable", "mass", "size"])
        self.assertIn("spin", self.m["capture"]["not_gated"])

    def test_gates_are_complete(self):
        for mission in self.m["order"]:
            self.assertTrue(self.m[mission]["label"])
            for g in self.m[mission]["gates"]:
                for k in ("id", "label", "quantity", "unit", "op", "preset", "range", "kind", "source"):
                    self.assertIn(k, g, (mission, g.get("id"), k))
                self.assertIn(g["op"], ("<=", ">="))
                lo, hi = g["range"]
                self.assertTrue(lo <= g["preset"] <= hi, (mission, g["id"]))
                self.assertIn("docs/", g["source"], (mission, g["id"]))
                for alt in g.get("alternatives", []):
                    self.assertTrue(lo <= alt["value"] <= hi, (mission, g["id"], alt))

    def test_size_runs_the_other_way_for_capture(self):
        self.assertEqual(self.gates("surface")["size"]["op"], ">=")
        self.assertEqual(self.gates("capture")["size"]["op"], "<=")
        self.assertEqual(self.gates("capture")["mass"]["op"], "<=")
        self.assertGreater(self.gates("surface")["size"]["preset"], self.gates("capture")["size"]["preset"])

    def test_spin_gate_is_the_critical_period(self):
        g = self.gates("surface")["spin"]
        p_crit = math.sqrt(3 * math.pi / (g["gravitational_constant"] * g["density_kgm3"])) / 3600
        self.assertAlmostEqual(p_crit, g["preset"], delta=0.005)
        self.assertIn(g["preset"], self.p["spin"]["thresholds_h"], "the spin prior must be stated at the gate's threshold")
        # the figures quoted in docs/research/capability.md section 2
        self.assertAlmostEqual(math.sqrt(3 * math.pi / (g["gravitational_constant"] * 2000)) / 3600, 2.3, delta=0.05)
        self.assertAlmostEqual(math.sqrt(3 * math.pi / (g["gravitational_constant"] * 1200)) / 3600, 3.0, delta=0.05)

    def test_capture_presets(self):
        g = self.gates("capture")
        self.assertEqual(g["mass"]["preset"], 1300.0)
        self.assertEqual(g["size"]["preset"], 10.0)
        # a 10 m sphere at the unknown-class median density is near the ceiling, so the mass gate is not idle
        self.assertGreater(math.pi / 6 * 10 ** 3 * 3300 / 1000, g["mass"]["preset"])

    def test_named_targets_are_all_there(self):
        want = {"surface": ["341843", "2011 AA37", "895813", "2021 UH2", "99942"], "capture": ["2009 BD", "2011 MD"]}
        for mission, pdes in want.items():
            self.assertEqual([n["pdes"] for n in self.m[mission]["named"]], pdes)

    def test_no_miss_is_hidden(self):
        for mission in self.m["order"]:
            named = self.m[mission]["named"]
            gate_ids = set(self.gates(mission))
            tally = {"pass": 0, "untested": 0, "fail": 0}
            for n in named:
                self.assertIn(n["status"], tally)
                tally[n["status"]] += 1
                self.assertEqual(set(n["gates"]), gate_ids, n["designation"])
                self.assertTrue(0 <= n["p"] <= 1)
                self.assertTrue(n["named_by"].strip())
                gs = set(n["gates"].values())
                if n["status"] == "pass":
                    self.assertEqual(gs, {"pass"}, n["designation"])
                    self.assertEqual(n["p"], 1.0)
                elif n["status"] == "fail":
                    self.assertIn("fail", gs, n["designation"])
                else:
                    self.assertNotIn("fail", gs, n["designation"])
                    self.assertIn("untested", gs, n["designation"])
                    self.assertGreaterEqual(len(n["why"]), 80, f"{n['designation']}: a target that is not a known pass needs its reason")
            chk = self.m[mission]["check"]
            self.assertEqual((chk["known_pass"], chk["untested"], chk["known_fail"]),
                             (tally["pass"], tally["untested"], tally["fail"]), mission)

    def test_the_rule_sentences_give_the_numbers_the_rules_hold(self):
        """method.html prints these sentences, so they state the figures; the figures must be the ones in use."""
        decide, (measured, untested, _) = self.m["rules"]["decide"], self.m["rules"]["gate"]
        self.assertIn(f"by {decide['sigma']:g} of its stated one-sigma errors", measured)
        self.assertIn(f"by a factor of {decide['no_range_factor']:g}", measured)
        self.assertIn(f"{load('value.toml')['exports']['min_draws']:,} joint draws", untested)
        self.assertIn(f"within {decide['sigma']:g} of its one-sigma errors", self.m["rules"]["size"]["h_allowance"])
        self.assertIn(f"equal to a factor of {decide['no_range_factor']:g}", decide["draw"])
        self.assertIn(f"under {load('ledger.toml')['period']['min_grade']}.", load("ledger.toml")["period"]["ungraded_rule"])

    def test_period_rule(self):
        self.assertEqual(self.m["rules"]["period"]["min_grade"], 2)
        aa37 = next(n for n in self.m["surface"]["named"] if n["pdes"] == "2011 AA37")
        self.assertEqual(aa37["gates"]["spin"], "untested", "2011 AA37's 10 h is graded unreliable and must not decide the gate")


class Observe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = load("observe.toml")
        cls.m = load("missions.toml")

    def test_formula_is_the_one_tested_here(self):
        self.assertEqual(self.o["gain"]["formula"], "gain = H2(p) - q * H2(p / q)")
        self.assertEqual(self.o["gain"]["unit"], "bits")

    def test_gain_properties(self):
        self.assertAlmostEqual(gain(0.5, 0.5), 1.0)           # the gate is the whole question, an even bet
        self.assertAlmostEqual(gain(0.9, 0.9), 0.469, places=3)
        self.assertAlmostEqual(gain(0.99, 0.99), 0.081, places=3)
        self.assertEqual(gain(0.3, 1.0), 0.0)                 # gate already passed: nothing to learn from it
        self.assertEqual(gain(0.0, 0.4), 0.0)                 # mission already failed elsewhere
        self.assertEqual(gain(0.0, 0.0), 0.0)
        for p, q in ((0.1, 0.5), (0.25, 0.5), (0.36, 0.998), (0.315, 0.315), (0.02, 0.9)):
            g = gain(p, q)
            self.assertTrue(0 <= g <= h2(p) + 1e-12, (p, q, g))
        # two independent even gates: p = 0.25, each observation resolves q = 0.5
        self.assertAlmostEqual(gain(0.25, 0.5), h2(0.25) - 0.5, places=9)
        # the same answer by enumeration of the four joint outcomes
        self.assertAlmostEqual(gain(0.25, 0.5), h2(0.25) - (0.5 * h2(0.5) + 0.5 * h2(0.0)), places=9)

    def test_reading_line_matches_the_formula(self):
        r = self.o["gain"]["reading"]
        self.assertIn("0.47", r)
        self.assertIn("0.08", r)

    def test_observations_resolve_real_gates(self):
        ids = [x["id"] for x in self.o["observations"]]
        self.assertEqual(ids, ["lightcurve", "size"])
        gate_ids = {g["id"] for mission in self.m["order"] for g in self.m[mission]["gates"]}
        for x in self.o["observations"]:
            self.assertIn(x["resolves"], gate_ids)
        self.assertEqual(self.o["observations"][0]["resolves"], "spin")
        self.assertEqual(self.o["observations"][1]["resolves"], "size")

    def test_needs_labels(self):
        t = self.o["needs"]["lightcurve"]["tiers"]
        self.assertEqual([x["label"] for x in t], ["small telescope", "2 m class telescope", "4 m class telescope"])
        self.assertEqual([x["max_mag"] for x in t], [18.0, 20.0, 22.0])
        self.assertTrue(self.o["needs"]["lightcurve"]["fainter"])
        self.assertTrue(self.o["needs"]["size"]["fainter"])
        for k in ("lightcurve", "size"):
            self.assertIn("verify-obs-window.md", self.o["needs"][k]["source"])

    def test_window_is_a_dated_fact(self):
        w = self.o["window"]
        self.assertEqual(w["fields"]["peak_mag"], "obs_mag")
        self.assertIn("'S'", w["pointable"])
        for s in all_strings(self.o):
            self.assertNotIn("open now", s.lower().replace("never 'open now'", ""))


class Document(unittest.TestCase):
    def test_tables_in_the_method_document_are_the_constants(self):
        import method_doc_tables
        with open(method_doc_tables.DOC) as fh:
            text = fh.read()
        out, unused = method_doc_tables.render(text)
        self.assertEqual(unused, [], "tables the document does not show")
        self.assertEqual(out, text, "docs/method.md is out of date; run tools/method_doc_tables.py")
        self.assertNotIn("<!-- table:", re.sub(r"<!-- table:\w+ -->\n\|", "", text), "an empty table block")

    def test_one_section_per_item(self):
        with open(os.path.join(str(config.ROOT), "docs", "method.md")) as fh:
            heads = re.findall(r"^## (.+)$", fh.read(), re.M)
        self.assertEqual(heads, ["1. Size from brightness", "2. Spin from brightness", "3. Class from brightness",
                                 "4. Density and mass", "5. Missions", "6. Observe next"])

    def test_each_section_says_what_is_untested(self):
        with open(os.path.join(str(config.ROOT), "docs", "method.md")) as fh:
            sections = re.split(r"^## ", fh.read(), flags=re.M)[1:]
        for s in sections:
            self.assertIn("\nUntested:\n", s, s.split("\n")[0])
            self.assertIn("\nDo not conclude:\n", s, s.split("\n")[0])


HAVE_DATA = all(p.exists() for p in (config.SPITZER_CSV, config.SBDB_JSON, config.NHATS_JSON, config.PRAVEC_TXT,
                                     config.LCDB_DIR / "x" / "lc_summary_pub.txt", config.SSODNET_CARDS,
                                     config.DATA / "research" / "out-prior-null" / "labels.csv"))


@unittest.skipUnless(HAVE_DATA, "the research data is not unpacked under data/")
class Derivation(unittest.TestCase):
    """Every measured constant traces to a script output."""

    def test_priors_file_is_what_the_scripts_derive(self):
        import method_priors_toml
        first = method_priors_toml.build()
        with open(method_priors_toml.OUT) as fh:
            self.assertEqual(fh.read(), first, "method/v0_1/priors.toml differs from tools/method_priors_toml.py")
        self.assertEqual(method_priors_toml.build(), first, "the derivation is not deterministic")

    def test_derivation_texts_are_current(self):
        import method_class
        import method_lib
        import method_reflectivity
        import method_spin
        for mod, name in ((method_reflectivity, "reflectivity"), (method_spin, "spin"), (method_class, "class")):
            with open(os.path.join(method_lib.DERIVATION, name + ".txt")) as fh:
                self.assertEqual(fh.read(), mod.main(write=False, echo=False), name)

    @classmethod
    def named(cls):
        """tools/method_missions.py, run once: it reads the pipeline's records for the named targets."""
        if not hasattr(Derivation, "_named"):
            import method_missions
            Derivation._named = method_missions.run()
        return Derivation._named

    def test_named_targets_come_out_as_recorded(self):
        import method_missions
        m, nh, records, out = self.named()
        self.assertEqual(len(out), 7)
        for mission, n, r, f, ev, ends in out:
            self.assertEqual(ev["status"], n["status"], n["designation"])
            self.assertAlmostEqual(ev["p"], n["p"], delta=0.0051, msg=n["designation"])
            self.assertEqual({k: v[0] for k, v in ev["gates"].items()}, n["gates"], n["designation"])
            # the check is the entry: the verdict printed here is the one the record carries
            self.assertEqual((r.missions[mission]["status"], r.missions[mission]["p"]), (ev["status"], ev["p"]))
        self.assertEqual(method_missions.problems(out), [])
        with open(os.path.join(method_lib_dir(), "missions.txt")) as fh:
            self.assertIn("read from the pipeline's records", fh.read())

    def test_a_recorded_result_that_no_longer_matches_is_reported(self):
        import copy
        import method_missions
        m, nh, records, out = self.named()
        mission, n, r, f, ev, ends = out[1]
        wrong = dict(copy.deepcopy(n), p=round(n["p"] + 0.05, 4))
        self.assertTrue(method_missions.problems([(mission, wrong, r, f, ev, ends)]))
        wrong = dict(copy.deepcopy(n), gates=dict(n["gates"], spin="pass"))
        self.assertTrue(method_missions.problems([(mission, wrong, r, f, ev, ends)]))

    def test_snapshot_facts_behind_the_check(self):
        m, nh, records, out = self.named()
        facts = {n["pdes"]: f for _, n, r, f, ev, ends in out}
        self.assertIsNone(facts["2011 AA37"]["period"])                   # its 10 h is graded unreliable
        self.assertIn("graded unreliable", facts["2011 AA37"]["period_words"])
        self.assertIsNone(facts["2011 AA37"]["size"])
        self.assertAlmostEqual(facts["895813"]["dv"], 7.237, places=3)
        self.assertEqual((facts["895813"]["cls"], facts["895813"]["cls_error"]), ("S", 0.21))     # a label from colours
        self.assertAlmostEqual(facts["2021 UH2"]["h"], 25.08, places=2)
        self.assertAlmostEqual(facts["99942"]["size"][0], 340, delta=1)
        self.assertAlmostEqual(facts["341843"]["size"][0], 344, delta=1)   # the size its entry shows, not JPL's 400
        self.assertAlmostEqual(facts["2009 BD"]["size"][0], 4.0, delta=0.01)
        self.assertAlmostEqual(facts["2011 MD"]["size"][0], 6.0, delta=0.01)
        self.assertAlmostEqual(facts["2011 MD"]["density"], 746.8, delta=0.1)
        self.assertTrue(all(f["occ"] <= 2 for f in facts.values()))

    def test_known_bad_size_does_not_decide_a_gate(self):
        """AGENTS.md fixtures: 2010 NU71 carries 1.126 km at H 22.7 from a main-belt table."""
        from longshot import draws, method, model
        m, nh, records, out = self.named()
        nu71 = next(r for r in records if r.designation == "2010 NU71")
        self.assertEqual(nu71.rows["size"].state, "prior")                # ledger.toml [[known_bad]]: on file, not used
        model.run_one(nu71, m)
        gates = {g["id"]: g["status"] for g in nu71.missions["surface"]["gates"]}
        self.assertEqual(gates["size"], "untested")
        # were it not on that list, [rules.size] would still turn it away: it implies a reflectivity of 0.0012
        from longshot.types import Fact, Row
        raw = model.run_one(type(nu71)(**{**nu71.__dict__, "rows": {**nu71.rows, "size": Row("measured", [
            Fact("diameter", 1126.0, 1060.0, 1192.0, "m", source="jpl-sbdb"),
            next(f for f in nu71.rows["size"].facts if f.label == "H")])}}), m)
        self.assertIsNotNone(draws.inputs(raw, m).size_rejected)
        self.assertEqual(raw.missions["surface"]["gates"][1]["status"], "untested")
        self.assertLess(m.missions["rules"]["size"]["min_implied_reflectivity"], 0.013)

    def test_fast_rotator_under_5_kms_is_no_longer_universal(self):
        """AGENTS.md, traps: Pravec's table holds a 2.35 h period under 5 km/s (2023 RA4)."""
        import method_lib
        import method_spin
        sb = method_lib.Sbdb()
        nh = method_lib.load_nhats()
        periods, _ = method_spin.reliable_periods(sb)
        slow = [d for d in nh if d in periods and float(nh[d]["min_dv"]["dv"]) < 5 and periods[d][0] >= 2.2]
        self.assertEqual(slow, ["2023 RA4"])
        self.assertAlmostEqual(periods["2023 RA4"][0], 2.35, delta=0.01)

    def test_the_pipeline_keeps_the_size_prior(self):
        """With nothing measured, the median size is the Spitzer median: class is drawn after reflectivity."""
        from longshot import draws, method, priors
        m = method.load()
        inp = draws.Inputs(h=26.2, h_sigma=0.0, band="26_28")
        d = draws.joint("k", inp, m)
        self.assertAlmostEqual(priors.quantiles(d.d)["q50"], 14.7, delta=0.3)
        pri = load("priors.toml")
        for c in CLASSES:
            self.assertAlmostEqual(d.cls.count(c) / d.n, pri["class"]["bands"]["26_28"]["central"][c], delta=0.02, msg=c)
        # darker draws are larger and more often C: the tie between reflectivity, size and class
        big = [c for c, size in zip(d.cls, d.d) if size > 25]
        self.assertGreater(big.count("C") / len(big), 2 * d.cls.count("C") / d.n)


def method_lib_dir():
    import method_lib
    return method_lib.DERIVATION


if __name__ == "__main__":
    unittest.main()
