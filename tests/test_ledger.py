"""The ledger: the six rows, their states, conflicts, and the fixture objects.

Run: uv run python -m unittest tests.test_ledger
"""
import dataclasses
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from longshot import config, ids, ledger
from longshot.ingest import nhats
from longshot.types import ROWS, STATES, Claim, Coverage
from tests.fixtures import FIXTURES, research_cards_only

IDENT = ids.Identity(key="zzzzz9", pdes="2099 ZZ9", designation="2099 ZZ9", name=None, number=None, kind="au",
                     aliases=("2099 ZZ9",))


def claim(prop, source, value, **kw):
    return Claim(key=IDENT.key, prop=prop, source=source, value=value, **kw)


def coverage(overrides=None, default="absent"):
    """Coverage for every (row, source) the ledger expects, 'absent' unless overridden."""
    out = {}
    for row, sources in ledger.ROW_SOURCES.items():
        for s in sources:
            outcome = (overrides or {}).get((row, s), default)
            reason = "no SsODNet card has been fetched" if outcome == "unchecked" else ""
            out[(row, s)] = Coverage(key=IDENT.key, row=row, source=s, outcome=outcome, reason=reason)
    return out


def record(claims, cov=None):
    return ledger.build_record(IDENT, claims, cov if cov is not None else coverage())


def close(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


class StateRulesCase(unittest.TestCase):
    """The rules, on hand-made claims."""

    def test_nothing_anywhere_is_prior_and_never_carries_a_prior_value(self):
        r = record([])
        for row in ("size", "spin", "surface", "push"):
            self.assertEqual(r.rows[row].state, "prior", row)
            self.assertIsNone(r.rows[row].prior)
            self.assertEqual(r.rows[row].unchecked, [])

    def test_one_unchecked_source_makes_the_row_unchecked_not_prior(self):
        for row in ("size", "spin", "surface", "push"):
            with self.subTest(row):
                r = record([], coverage({(row, "ssodnet"): "unchecked"}))
                self.assertEqual(r.rows[row].state, "unchecked")
                self.assertEqual(r.rows[row].unchecked, ["ssodnet"])
                self.assertIn("No SsODNet card has been fetched.", r.rows[row].note)
                for other in ("size", "spin", "surface", "push"):
                    if other != row:
                        self.assertEqual(r.rows[other].state, "prior")

    def test_a_source_with_no_coverage_record_counts_as_unchecked(self):
        cov = coverage()
        del cov[("spin", "pravec")]
        r = record([], cov)
        self.assertEqual(r.rows["spin"].state, "unchecked")
        self.assertEqual(r.rows["spin"].unchecked, ["pravec"])

    def test_a_measured_row_still_lists_what_was_not_checked(self):
        r = record([claim("diameter_m", "spitzer", 50.0, lo=40.0, hi=70.0, unit="m")],
                   coverage({("size", "ssodnet"): "unchecked", ("size", "spitzer"): "found"}))
        self.assertEqual(r.rows["size"].state, "measured")
        self.assertEqual(r.rows["size"].unchecked, ["ssodnet"])

    # -- albedo ----------------------------------------------------------

    def test_a_computed_albedo_never_gives_measured(self):
        computed = claim("albedo", "ssodnet", 0.6352, lo=0.31, hi=0.96, quality="Computed", ref="Berthier+2023")
        r = record([computed], coverage({("surface", "ssodnet"): "found"}))
        self.assertEqual(r.rows["surface"].state, "prior")
        self.assertEqual([(f.label, f.quality) for f in r.rows["surface"].facts], [("albedo", "Computed")])
        self.assertIn("computed", r.rows["surface"].note)
        r = record([computed], coverage({("surface", "ssodnet"): "found", ("surface", "spitzer"): "unchecked"}))
        self.assertEqual(r.rows["surface"].state, "unchecked")

    def test_a_measured_albedo_gives_measured_and_goes_first(self):
        r = record([claim("albedo", "ssodnet", 0.37, quality="Computed"),
                    claim("albedo", "spitzer", 0.467, lo=0.243, hi=0.719, quality="thermal model, one band")])
        self.assertEqual(r.rows["surface"].state, "measured")
        self.assertEqual([f.source for f in r.rows["surface"].facts], ["spitzer", "ssodnet"])
        self.assertEqual(ledger.adopted(r.rows["surface"]).value, 0.467)

    def test_a_computed_diameter_never_gives_measured(self):
        r = record([claim("diameter_m", "ssodnet", 30.0, quality="Computed", unit="m")])
        self.assertEqual(r.rows["size"].state, "prior")

    # -- periods ---------------------------------------------------------

    def test_an_unreliable_period_never_gives_measured(self):
        for grade in ("1+", "1", "1-", "0"):
            with self.subTest(grade):
                r = record([claim("period_h", "lcdb", 10.0, quality=grade, unit="h")])
                self.assertEqual(r.rows["spin"].state, "prior")
                self.assertEqual([(f.value, f.quality) for f in r.rows["spin"].facts], [(10.0, grade)])
                self.assertIn("graded below 2-", r.rows["spin"].note)

    def test_the_lowest_usable_grade_is_two_minus(self):
        for grade in ("2-", "2", "2+", "3-", "3"):
            with self.subTest(grade):
                r = record([claim("period_h", "pravec", 10.0, quality=grade, unit="h")])
                self.assertEqual(r.rows["spin"].state, "measured")

    def test_an_ungraded_copy_of_an_unreliable_period_is_not_measured(self):
        # The 2011 AA37 pattern: JPL repeats the value with no grade.
        r = record([claim("period_h", "lcdb", 10.0, quality="1+", unit="h"),
                    claim("period_h", "jpl-sbdb", 10.0, unit="h")])
        self.assertEqual(r.rows["spin"].state, "prior")
        self.assertEqual(r.rows["spin"].conflicts, [])
        r = record([claim("period_h", "lcdb", 10.0, quality="1+", unit="h"),
                    claim("period_h", "jpl-sbdb", 10.0, unit="h")],
                   coverage({("spin", "ssodnet"): "unchecked"}))
        self.assertEqual(r.rows["spin"].state, "unchecked")

    def test_an_ungraded_period_alone_is_measured(self):
        r = record([claim("period_h", "ssodnet", 0.053, unit="h", ref="Fedorets+2020")])
        self.assertEqual(r.rows["spin"].state, "measured")

    def test_an_ungraded_period_that_a_graded_one_confirms_is_measured(self):
        r = record([claim("period_h", "lcdb", 4.2968, quality="3", unit="h"),
                    claim("period_h", "jpl-sbdb", 4.296061, unit="h")])
        self.assertEqual(r.rows["spin"].state, "measured")
        self.assertEqual(r.rows["spin"].conflicts, [])

    def test_an_ungraded_period_that_a_usable_graded_one_contradicts_does_not_count(self):
        graded = claim("period_h", "pravec", 250.0, quality="3", unit="h")
        loose = claim("period_h", "jpl-sbdb", 2.02, unit="h")
        self.assertEqual(ledger.judge_periods([graded, loose]), {id(graded): "usable", id(loose): "contradicted"})
        r = record([graded, loose])
        self.assertEqual(r.rows["spin"].state, "measured")
        self.assertEqual(ledger.adopted(r.rows["spin"]).source, "pravec")
        self.assertEqual(len(r.rows["spin"].conflicts), 1)
        # contradicted by an unreliable one only: the ungraded value stands
        weak = claim("period_h", "lcdb", 250.0, quality="1", unit="h")
        self.assertEqual(ledger.judge_periods([weak, loose])[id(loose)], "usable")

    def test_an_ungraded_period_counts_whichever_source_holds_it(self):
        """ledger.toml [period].ungraded: the lightcurve database's own ungraded entry and JPL's copy alike."""
        lc = claim("period_h", "lcdb", 7.0, unit="h", note="no grade assigned")
        jpl = claim("period_h", "jpl-sbdb", 7.0, unit="h")
        for claims in ([lc], [jpl], [lc, jpl]):
            r = record(claims)
            self.assertEqual(r.rows["spin"].state, "measured")
            self.assertEqual({f.used for f in r.rows["spin"].facts}, {True})

    def test_an_ungraded_copy_of_a_limit_is_not_a_measured_period(self):
        """The blocker of the 2026-11-25 review: JPL repeats the lightcurve database's '> 2.' as 2 h."""
        bound = claim("period_h", "lcdb", 2.0, kind="lower", quality="2", unit="h")
        copy = claim("period_h", "jpl-sbdb", 2.0, unit="h")
        r = record([bound, copy])
        row = r.rows["spin"]
        self.assertEqual(row.state, "limit")
        self.assertEqual([(f.source, f.kind, f.used) for f in row.facts],
                         [("lcdb", "lower", True), ("jpl-sbdb", "value", False)])
        self.assertIn("without its limit sign", row.note)
        self.assertIn("lower limit", row.facts[1].note)
        # a limit graded under the bar does not count either, and the copy still does not: nothing is measured
        weak = claim("period_h", "lcdb", 2.0, kind="lower", quality="1+", unit="h")
        row = record([weak, copy]).rows["spin"]
        self.assertEqual(row.state, "prior")
        self.assertEqual({f.used for f in row.facts}, {False})
        # an ungraded limit counts, as an ungraded value does
        self.assertEqual(record([claim("period_h", "lcdb", 0.5, kind="lower", unit="h"),
                                 claim("period_h", "jpl-sbdb", 0.5, unit="h")]).rows["spin"].state, "limit")
        # a genuine measurement near a limit is not swallowed: only the same number as printed is a copy
        near = claim("period_h", "jpl-sbdb", 2.1, unit="h")
        row = record([bound, near]).rows["spin"]
        self.assertEqual(row.state, "measured")
        self.assertEqual((row.facts[0].source, row.facts[0].value), ("jpl-sbdb", 2.1))
        # and a graded value equal to the limit is a measurement in its own right
        graded = claim("period_h", "pravec", 2.0, quality="3", unit="h")
        self.assertEqual(record([bound, graded]).rows["spin"].state, "measured")

    def test_a_newer_period_held_by_two_sources_is_not_ruled_out_by_an_old_table(self):
        """ledger.toml [period].superseded, the case of 1998 KY26."""
        old = claim("period_h", "lcdb", 0.1784, quality="3", unit="h")
        card = claim("period_h", "ssodnet", 0.089193, unit="h", ref="Santana-Ros+2025b (2025NatCo..16.8763S)")
        jpl = claim("period_h", "jpl-sbdb", 0.089193, unit="h")
        editions = {"lcdb": "2023-10-01", "pravec": "2026-10-15"}
        verdict = ledger.judge_periods([old, card, jpl], editions)
        self.assertEqual([verdict[id(c)] for c in (old, card, jpl)], ["usable", "newer", "newer"])
        row = ledger.spin_row([old, card, jpl], coverage(), editions)
        self.assertEqual(row.state, "measured")
        self.assertEqual([(f.source, f.used) for f in row.facts],
                         [("ssodnet", True), ("jpl-sbdb", True), ("lcdb", True)])       # the newer one first
        self.assertEqual(len(row.conflicts), 1)
        self.assertIn("newer period is used", row.note)
        # one source alone, a reference no later than the table, or a table that is not fixed: ruled out as before
        for claims, eds in (([old, card], editions), ([old, jpl], editions),
                            ([old, claim("period_h", "ssodnet", 0.089193, unit="h", ref="Someone+2019"), jpl], editions),
                            ([old, card, jpl], {})):
            v = ledger.judge_periods(claims, eds)
            self.assertEqual({v[id(c)] for c in claims[1:]}, {"contradicted"})
        row = ledger.spin_row([old, card], coverage(), editions)
        self.assertEqual([f.used for f in row.facts], [True, False])
        self.assertIn("differs from the graded one", row.note)          # the page says why it is not used

    def test_a_conflict_sentence_never_prints_an_inference_only_value(self):
        """docs/mvp.md section 3: the lightcurve database's own number and grade stay off the page."""
        old = claim("period_h", "lcdb", 0.1784, quality="3", unit="h")
        card = claim("period_h", "ssodnet", 0.089193, unit="h", ref="Santana-Ros+2025b (2025NatCo..16.8763S)")
        jpl = claim("period_h", "jpl-sbdb", 0.089193, unit="h")
        row = ledger.spin_row([old, card, jpl], coverage(), {"lcdb": "2023-10-01"})
        # a period in the unit the pages print it in: minutes under 2 h
        self.assertEqual(row.conflicts, ["5.352 min (SsODNet, Santana-Ros+2025b; JPL's database) against a different "
                                         "period on file in the lightcurve database, not shown here."])
        self.assertNotIn("0.1784", row.conflicts[0])
        self.assertNotIn("U 3", row.conflicts[0])
        self.assertNotIn("grade 3", row.conflicts[0])
        # where another source states the lightcurve database's value, the value prints and its grade does not
        row = record([claim("period_h", "pravec", 250.0, quality="3", unit="h"),
                      claim("period_h", "lcdb", 250.0, quality="2", unit="h"),
                      claim("period_h", "ssodnet", 2.02, quality="2", unit="h", ref="Thirouin+2016b (2016AJ)"),
                      claim("period_h", "jpl-sbdb", 250.0, unit="h")]).rows["spin"]
        self.assertEqual(row.conflicts, ["250 h (Pravec's table, grade 3; the lightcurve database; JPL's database) "
                                         "against 2.02 h (SsODNet, Thirouin+2016b, grade 2)."])      # one line, not three

    def test_two_usable_periods_more_than_twenty_percent_apart_conflict(self):
        for other, expect in ((12.0, 0), (12.01, 1), (8.34, 0), (8.3, 1), (1000.0, 1)):
            with self.subTest(other):
                r = record([claim("period_h", "pravec", 10.0, quality="3", unit="h"),
                            claim("period_h", "ssodnet", other, quality="2", unit="h", ref="Someone+2020")])
                self.assertEqual(r.rows["spin"].state, "measured")
                self.assertEqual(len(r.rows["spin"].conflicts), expect)
        r = record([claim("period_h", "pravec", 250.0, quality="3", unit="h"),
                    claim("period_h", "ssodnet", 2.02, quality="2", unit="h", ref="Thirouin+2016b (2016AJ)")])
        self.assertEqual(r.rows["spin"].conflicts,
                         ["250 h (Pravec's table, grade 3) against 2.02 h (SsODNet, Thirouin+2016b, grade 2)."])

    def test_an_unreliable_period_takes_no_part_in_a_conflict(self):
        r = record([claim("period_h", "pravec", 10.0, quality="3", unit="h"),
                    claim("period_h", "lcdb", 99.0, quality="1", unit="h")])
        self.assertEqual(r.rows["spin"].conflicts, [])
        self.assertEqual(r.rows["spin"].state, "measured")

    def test_a_bound_alone_is_a_limit(self):
        bound = claim("period_h", "lcdb", 16.0, kind="lower", quality="2", unit="h")
        r = record([bound])
        self.assertEqual(r.rows["spin"].state, "limit")
        self.assertEqual((r.rows["spin"].facts[0].kind, r.rows["spin"].facts[0].value), ("lower", 16.0))
        r = record([bound], coverage({("spin", "ssodnet"): "unchecked"}))
        self.assertEqual(r.rows["spin"].state, "limit")
        self.assertEqual(r.rows["spin"].unchecked, ["ssodnet"])
        r = record([bound, claim("period_h", "pravec", 30.0, quality="3", unit="h")])
        self.assertEqual(r.rows["spin"].state, "measured")
        self.assertEqual(r.rows["spin"].facts[0].kind, "value")
        r = record([claim("period_h", "pravec", 20.0, kind="lower", quality="1", unit="h")])
        self.assertEqual(r.rows["spin"].state, "prior")

    # -- classes -----------------------------------------------------------

    def test_classes_in_different_complexes_conflict(self):
        def classes(a, b):
            return record([claim("taxonomy", "ssodnet", a, quality="Mahlke Spec VISNIR", ref="Mahlke+2022"),
                           claim("taxonomy", "jpl-sbdb", b, quality="SMASSII")]).rows["surface"]
        for a, b, expect in (("S", "Sq", 0), ("S", "Q", 0), ("C", "B", 0), ("Ch", "Cb", 0), ("X", "Xe", 0),
                             ("M", "X", 0), ("S", "C", 1), ("S", "L", 1), ("K", "Xc", 1), ("V", "D", 1),
                             ("C", "X", 1)):
            with self.subTest(a=a, b=b):
                row = classes(a, b)
                self.assertEqual(row.state, "measured")
                self.assertEqual(len(row.conflicts), expect)
        self.assertEqual(classes("S", "L").conflicts,
                         ["Class S (SsODNet) against class L (JPL's database)."])
        # three labels, two complexes: one sentence, each side naming every source on it
        r = record([claim("taxonomy", "ssodnet", "S", quality="Mahlke Spec VISNIR", ref="Mahlke+2022"),
                    claim("taxonomy", "jpl-sbdb", "L", quality="SMASSII"), claim("taxonomy", "jpl-sbdb", "Sq", quality="Tholen")])
        self.assertEqual(r.rows["surface"].conflicts, ["Class S/Sq (SsODNet; JPL's database) against class L (JPL's database)."])
        # one source, two schemes, two complexes
        r = record([claim("taxonomy", "jpl-sbdb", "L", quality="SMASSII"), claim("taxonomy", "jpl-sbdb", "S", quality="Tholen")])
        self.assertEqual(r.rows["surface"].conflicts, ["Class L (SMASSII) against class S (Tholen). Both are from JPL's database."])

    def test_ssodnets_own_complex_is_used_where_given(self):
        r = record([claim("taxonomy", "ssodnet", "Ch", quality="Mahlke Spec VISNIR", ref="Mahlke+2022"),
                    claim("taxonomy_complex", "ssodnet", "C", quality="Mahlke Spec VISNIR", ref="Mahlke+2022"),
                    claim("taxonomy", "jpl-sbdb", "C", quality="Tholen")])
        self.assertEqual(r.rows["surface"].conflicts, [])
        self.assertEqual([f.label for f in r.rows["surface"].facts], ["class", "class"])

    # -- sizes -------------------------------------------------------------

    def test_sizes_conflict_when_their_stated_ranges_do_not_meet(self):
        def sizes(a, b):
            return record([claim("diameter_m", "ssodnet", a[0], lo=a[1], hi=a[2], unit="m", quality="NEATM"),
                           claim("diameter_m", "spitzer", b[0], lo=b[1], hi=b[2], unit="m")]).rows["size"]
        self.assertEqual(sizes((68.0, 56.0, 79.0), (56.0, 46.0, 77.0)).conflicts, [])
        self.assertEqual(sizes((915.0, 903.0, 927.0), (591.0, 457.0, 866.0)).conflicts,
                         ["915 m (903 to 927) from SsODNet against 591 m (457 to 866) from the Spitzer table."])
        # three sources, one disagreement: one sentence (2003 WR21 printed two, 2018 EJ4 six)
        three = record([claim("diameter_m", "ssodnet", 480.0, lo=472.0, hi=488.0, unit="m", quality="NEATM"),
                        claim("diameter_m", "spitzer", 326.0, lo=268.0, hi=445.0, unit="m"),
                        claim("diameter_m", "jpl-sbdb", 482.0, lo=472.0, hi=492.0, unit="m")]).rows["size"]
        self.assertEqual(three.conflicts, ["480 m (472 to 488) from SsODNet and 482 m (472 to 492) from JPL's database "
                                           "against 326 m (268 to 445) from the Spitzer table."])
        self.assertEqual(sizes((503.0, 493.0, 513.0), (511.0, None, None)).conflicts, [])
        self.assertEqual(len(sizes((160.0, 157.0, 163.0), (193.0, None, None)).conflicts), 1)
        self.assertEqual(sizes((915.0, 903.0, 927.0), (591.0, 457.0, 866.0)).state, "measured")

    def test_two_values_from_one_source_do_not_conflict(self):
        r = record([claim("diameter_m", "spitzer", 454.0, lo=340.0, hi=460.0, unit="m"),
                    claim("diameter_m", "spitzer", 663.0, lo=522.0, hi=943.0, unit="m")])
        self.assertEqual(r.rows["size"].conflicts, [])

    def test_h_is_carried_in_the_size_row_and_measures_nothing(self):
        r = record([claim("H", "jpl-sbdb", 24.3, unit="mag"), claim("H", "jpl-nhats", 24.3, unit="mag")])
        self.assertEqual(r.rows["size"].state, "prior")
        self.assertEqual([(f.label, f.source) for f in r.rows["size"].facts], [("H", "jpl-sbdb")])
        r = record([])
        self.assertIn("no absolute magnitude", r.rows["size"].note)

    def test_the_known_bad_size_is_kept_and_not_used(self):
        nu71 = dataclasses.replace(IDENT, pdes="2010 NU71", designation="2010 NU71")
        claims = [claim("diameter_m", "ssodnet", 1126.0, lo=1060.0, hi=1192.0, unit="m", quality="NEATM"),
                  claim("diameter_m", "jpl-sbdb", 1126.0, unit="m"),
                  claim("albedo", "ssodnet", 0.042, quality="NEATM"), claim("albedo", "jpl-sbdb", 0.042)]
        r = ledger.build_record(nu71, claims, coverage())
        self.assertEqual(r.rows["size"].state, "prior")
        self.assertEqual(r.rows["surface"].state, "prior")
        self.assertEqual(len(r.rows["size"].facts), 2)
        self.assertIn("main-belt table", r.rows["size"].note)
        # the same numbers on another object are ordinary measurements
        self.assertEqual(record(claims).rows["size"].state, "measured")
        # and a corrected value for NU71 would be used
        fixed = [claim("diameter_m", "ssodnet", 190.0, lo=150.0, hi=230.0, unit="m", quality="NEATM")]
        self.assertEqual(ledger.build_record(nu71, fixed, coverage()).rows["size"].state, "measured")

    # -- push --------------------------------------------------------------

    def test_a_push_value_under_three_sigma_is_not_measured(self):
        def push(value, sigma):
            return record([claim("A2", "jpl-sbdb", value, lo=value - sigma, hi=value + sigma, unit="au/d^2")]).rows["push"]
        self.assertEqual(push(-1.5e-13, 1.2e-14).state, "measured")
        self.assertEqual(push(3.0e-13, 1.0e-13).state, "measured")
        weak = push(2.9e-13, 1.0e-13)
        self.assertEqual(weak.state, "prior")
        self.assertEqual(len(weak.facts), 1)
        self.assertIn("3σ", weak.note)
        self.assertIn("rounded to two figures", weak.note)
        no_range = record([claim("A2", "jpl-sbdb", -1.5e-13, unit="au/d^2")]).rows["push"]
        self.assertEqual(no_range.state, "prior")

    def test_a3_is_listed_and_never_sets_the_state(self):
        """ledger.toml [push]: A3 is the out-of-plane term, not a push from sunlight."""
        a3 = claim("A3", "jpl-sbdb", 5.0e-13, lo=4.9e-13, hi=5.1e-13, unit="au/d^2")
        row = record([a3]).rows["push"]
        self.assertEqual(row.state, "prior")
        self.assertEqual([(f.label, f.used) for f in row.facts], [("A3", False)])
        self.assertIn("out-of-plane", row.note)
        a2 = claim("A2", "jpl-sbdb", -1.5e-13, lo=-1.6e-13, hi=-1.4e-13, unit="au/d^2")
        row = record([a3, a2]).rows["push"]
        self.assertEqual(row.state, "measured")
        self.assertEqual((row.facts[0].label, row.facts[0].used), ("A2", True))

    def test_fitted_pushes_conflict_when_their_stated_ranges_do_not_meet(self):
        jpl = claim("A2", "jpl-sbdb", -2.1e-13, lo=-2.38e-13, hi=-1.82e-13, unit="au/d^2")
        far = claim("A2", "ssodnet", -4.97e-13, lo=-6.09e-13, hi=-3.85e-13, unit="au/d^2")
        near = claim("A2", "ssodnet", -2.3e-13, lo=-2.6e-13, hi=-2.0e-13, unit="au/d^2")
        row = record([jpl, far]).rows["push"]
        self.assertEqual(len(row.conflicts), 1)
        self.assertIn("−4.97 × 10⁻¹³ au/d² (±1σ: −6.09 to −3.85)", row.conflicts[0])     # a true minus, no e-notation
        self.assertNotRegex(row.conflicts[0], r"\de-|\^2")
        self.assertEqual(record([jpl, near]).rows["push"].conflicts, [])
        # a different quantity is not a disagreement
        drift = claim("drift_au_per_myr", "ssodnet", -0.05, lo=-0.06, hi=-0.04, unit="au/Myr")
        self.assertEqual(record([jpl, drift]).rows["push"].conflicts, [])

    def test_a_computed_density_is_listed_and_not_used(self):
        r = record([claim("density_kgm3", "jpl-sbdb", 1194.0, unit="kg/m^3"),
                    claim("density_kgm3", "ssodnet", 1204.7, lo=1063.9, hi=1345.5, quality="Computed", unit="kg/m^3")])
        self.assertEqual([(f.source, f.used) for f in r.rows["push"].facts], [("jpl-sbdb", True), ("ssodnet", False)])
        self.assertIn("computed", r.rows["push"].note)

    def test_a_weak_spitzer_fit_is_kept_and_not_used(self):
        """ledger.toml [spitzer].min_snr and [reflectivity].max."""
        def fit(snr, pv, d=12.0):
            q = f"thermal model, one band, signal-to-noise {snr:g}"
            return [claim("diameter_m", "spitzer", d, lo=10.0, hi=14.0, unit="m", quality=q, ref="S", note="observed x", snr=snr),
                    claim("albedo", "spitzer", pv, quality=q, ref="S", note="observed x", snr=snr)]
        r = record(fit(0.9, 1.402))
        self.assertEqual((r.rows["size"].state, r.rows["surface"].state), ("prior", "prior"))
        self.assertEqual([f.used for f in r.rows["size"].facts + r.rows["surface"].facts], [False, False])
        self.assertIn("signal-to-noise 0.9, under the 5", r.rows["size"].note)
        r = record(fit(5.0, 0.3))
        self.assertEqual((r.rows["size"].state, r.rows["surface"].state), ("measured", "measured"))
        # a fit at a good signal-to-noise whose reflectivity is above 1 is still not a surface measurement
        r = record(fit(8.0, 1.07))
        self.assertEqual((r.rows["size"].state, r.rows["surface"].state), ("prior", "prior"))
        self.assertIn("reflectivity of 1.07, above 1", r.rows["size"].note)
        # nor is one above 1 from any other source
        r = record([claim("albedo", "ssodnet", 1.2, quality="NEATM")])
        self.assertEqual(r.rows["surface"].state, "prior")

    def test_the_hand_entered_source_adds_claims_and_never_makes_a_row_unchecked(self):
        cov = {k: v for k, v in coverage().items() if k[1] != "curated"}       # it writes no "absent" coverage
        self.assertEqual(record([], cov).rows["size"].unchecked, [])
        self.assertEqual(record([], cov).rows["size"].state, "prior")
        r = record([claim("diameter_m", "curated", 18.0, lo=16.0, hi=20.0, unit="m", ref="Sharkey et al. 2026"),
                    claim("diameter_m", "jpl-sbdb", 40.0, unit="m")], cov)
        self.assertEqual(r.rows["size"].state, "measured")
        self.assertEqual(ledger.adopted(r.rows["size"]).source, "curated")       # first in the row's source order
        self.assertIn("curated", r.sources)

    def test_a_body_that_is_gone_has_no_window(self):
        tc3 = dataclasses.replace(IDENT, pdes="2008 TC3", designation="2008 TC3")
        claims = [claim("condition_code", "jpl-sbdb", 4.0), claim("window_start", "jpl-nhats", "2041-09-23", unit="date"),
                  claim("window_end", "jpl-nhats", "2041-09-29", unit="date"),
                  claim("window_pointing", "jpl-nhats", "survey-only")]
        r = ledger.build_record(tc3, claims, coverage())
        self.assertEqual(r.gone["date"], "2008-10-07")
        self.assertEqual([f.label for f in r.rows["tracking"].facts], ["condition code"])
        self.assertIn("Almahata Sitta", r.rows["tracking"].note)
        self.assertIsNone(ledger.window(r))
        self.assertIsNone(record(claims).gone)                 # the same facts on another object

    def test_the_thresholds_come_from_the_method_file(self):
        """Nothing in ledger.py is a threshold of its own: build report 9.5."""
        from longshot import method
        led = method.load().ledger
        rules = ledger.rules()
        self.assertEqual((rules.min_grade, rules.tolerance, rules.detection_sigma),
                         (led["period"]["min_grade"], led["period"]["tolerance"], led["push"]["detection_sigma"]))
        self.assertEqual([b.designation for b in rules.known_bad], [b["designation"] for b in led["known_bad"]])
        self.assertEqual(rules.spitzer_min_snr, led["spitzer"]["min_snr"])
        for name in ("MIN_GRADE", "PERIOD_TOLERANCE", "DETECTION_SIGMA", "KNOWN_BAD"):
            self.assertFalse(hasattr(ledger, name), name)
        for table in ("period", "push", "spitzer", "reflectivity", "fixed_tables"):
            self.assertTrue(any(k.endswith("source") for k in led[table]), f"ledger.toml [{table}] gives no source")
        for entry in led["known_bad"] + led["gone"]:
            self.assertIn("docs/research/", entry["source"])

    def test_density_is_carried_and_measures_nothing(self):
        r = record([claim("density_kgm3", "ssodnet", 2287.74, quality="Yarkovsky+SRP", unit="kg/m^3")])
        self.assertEqual(r.rows["push"].state, "prior")
        self.assertEqual([f.label for f in r.rows["push"].facts], ["density"])

    # -- reach and tracking --------------------------------------------------

    def test_window_facts_are_dated(self):
        as_of = f"as of {config.DATA_DATE}"
        claims = [
            claim("delta_v_kms", "jpl-nhats", 5.851, unit="km/s"),
            claim("condition_code", "jpl-nhats", 0.0), claim("condition_code", "jpl-sbdb", 0.0),
            claim("data_arc_days", "jpl-sbdb", 5783.0, unit="d"),
            claim("window_start", "jpl-nhats", "2026-11-27", unit="date", ref=as_of),
            claim("window_end", "jpl-nhats", "2027-03-20", unit="date", ref=as_of),
            claim("window_peak_mag", "jpl-nhats", 21.85, unit="V mag", ref=as_of),
            claim("window_pointing", "jpl-nhats", "survey-only", ref=as_of),
        ]
        r = record(claims, coverage(default="found"))
        self.assertEqual(r.rows["reach"].state, "measured")
        self.assertEqual(r.rows["tracking"].state, "measured")
        facts = {f.label: f for f in r.rows["tracking"].facts}
        for label in ("window start", "window end", "window peak brightness", "window pointing"):
            self.assertEqual(facts[label].ref, as_of)
            self.assertEqual(facts[label].source, "jpl-nhats")
        self.assertEqual(facts["arc"].value, 5783)
        self.assertIsInstance(facts["arc"].value, int)
        self.assertEqual(ledger.window(r), {"start": "2026-11-27", "end": "2027-03-20", "peak_mag": 21.85,
                                            "pointable": False, "as_of": config.DATA_DATE})
        self.assertIsNone(ledger.window(record([claim("next_window", "jpl-nhats", "none through 2045", ref=as_of)])))

    def test_a_stale_orbit_solution_is_said(self):
        r = record([claim("condition_code", "jpl-nhats", 6.0), claim("orbit_id", "jpl-nhats", "12"),
                    claim("condition_code", "jpl-sbdb", 0.0), claim("orbit_id", "jpl-sbdb", "JPL 13")])
        self.assertEqual(ledger.fact(r.rows["tracking"], "condition code").value, 0)
        self.assertIn("orbit solution 12 (condition code 6)", r.rows["tracking"].note)

    def test_grades_order(self):
        order = ["0", "1-", "1", "1+", "2-", "2", "2+", "3-", "3"]
        ranks = [ledger.grade_rank(g) for g in order]
        self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(len(set(ranks)), len(ranks))
        for junk in (None, "", "Computed", "U=2", "4", "2++"):
            self.assertIsNone(ledger.grade_rank(junk))


class BuiltLedgerCase(unittest.TestCase):
    """The whole reachable list, built from the research snapshot of cards only."""

    @classmethod
    def setUpClass(cls):
        with research_cards_only():
            cls.index = ids.load()
            cls.order = nhats.reachable()
            cls.records = ledger.build(write_file=False)
        cls.by_key = {r.key: r for r in cls.records}

    def get(self, name):
        key = self.index.resolve(name)
        self.assertIsNotNone(key, name)
        return self.by_key[key]

    def test_fixtures(self):
        self.assertEqual(len(FIXTURES), 13)
        for name, fx in FIXTURES.items():
            r = self.get(name)
            self.assertEqual((r.designation, r.name, r.number), (fx["designation"], fx["name"], fx["number"]), name)
            self.assertEqual(set(fx["rows"]), set(ROWS), name)
            for row_name, want in fx["rows"].items():
                row = r.rows[row_name]
                where = f"{name} / {row_name}"
                with self.subTest(where):
                    self.assertEqual(row.state, want["state"], where)
                    self.assertEqual(row.unchecked, want["unchecked"], where)
                    self.assertIsNone(row.prior, where)
                    for label in want.get("absent", []):
                        self.assertEqual([f for f in row.facts if f.label == label], [], f"{where}: {label}")
                    if not want["facts"] and "absent" not in want and row_name in ("spin", "surface", "push"):
                        self.assertEqual(row.facts, [], where)
                    for fact in want["facts"]:
                        match = [f for f in row.facts if f.label == fact["label"] and f.source == fact["source"]
                                 and close(f.value, fact["value"])]
                        self.assertTrue(match, f"{where}: no {fact['label']} = {fact['value']} from "
                                               f"{fact['source']} ({fact['where']}); have "
                                               f"{[(f.label, f.value, f.source) for f in row.facts]}")
                        got = match[0]
                        for extra in ("quality", "ref"):
                            if extra in fact:
                                self.assertEqual(getattr(got, extra), fact[extra], f"{where}: {fact['label']} {extra}")
                        for extra in ("lo", "hi"):
                            if extra in fact:
                                self.assertTrue(close(getattr(got, extra), fact[extra]),
                                                f"{where}: {fact['label']} {extra} {getattr(got, extra)}")
                    if "conflicts" in want:
                        self.assertEqual(bool(row.conflicts), bool(want["conflicts"]), where)
                        for parts in want["conflicts"]:
                            self.assertTrue(any(all(p in sentence for p in parts) for sentence in row.conflicts),
                                            f"{where}: {row.conflicts}")

    def test_extra_fixtures(self):
        """The objects added after the review: a limit JPL repeats without its sign, a newer period against an
        old table, a Spitzer fit under the detection bar, a body that no longer exists."""
        from tests.fixtures import EXTRA_FIXTURES
        for name, fx in EXTRA_FIXTURES.items():
            r = self.get(name)
            for row_name, want in fx["rows"].items():
                row = r.rows[row_name]
                where = f"{name} / {row_name}"
                with self.subTest(where):
                    self.assertEqual(row.state, want["state"], where)
                    self.assertEqual(row.unchecked, want["unchecked"], where)
                    for label in want.get("absent", []):
                        self.assertEqual([f for f in row.facts if f.label == label], [], f"{where}: {label}")
                    for fact in want["facts"]:
                        match = [f for f in row.facts if f.label == fact["label"] and f.source == fact["source"]
                                 and close(f.value, fact["value"])]
                        self.assertTrue(match, f"{where}: no {fact['label']} = {fact['value']} from {fact['source']}")
                        for extra in ("quality", "kind", "used"):
                            if extra in fact:
                                self.assertEqual(getattr(match[0], extra), fact[extra],
                                                 f"{where}: {fact['label']} {extra}")
        # the order says which period the row rests on
        self.assertEqual(ledger.adopted(self.get("1998 KY26").rows["spin"]).value, 0.089193)
        self.assertEqual(ledger.adopted(self.get("2017 BL6").rows["spin"]).kind, "lower")
        self.assertEqual(ledger.adopted(self.get("1999 NW2").rows["spin"]).kind, "upper")
        gone = self.get("2008 TC3").gone
        self.assertEqual(gone["date"], "2008-10-07")
        self.assertIn("Almahata Sitta", gone["text"])
        self.assertIn("Almahata Sitta", self.get("2008 TC3").rows["tracking"].note)
        self.assertEqual([r.designation for r in self.records if r.gone], ["2008 TC3"])

    def test_no_measured_spin_row_rests_on_a_number_another_source_gives_as_a_limit(self):
        """The 12 rows the review found: JPL's rot_per equal to a lightcurve-database '>' or '<' period."""
        seen = 0
        for r in self.records:
            row = r.rows["spin"]
            periods = [f for f in row.facts if f.label == "period"]
            bounds = [f for f in periods if f.kind != "value"]
            for f in periods:
                if f.kind == "value" and any(ledger.same_number(f.value, b.value) and b.source != f.source
                                             for b in bounds) and ledger.grade_rank(f.quality) is None:
                    seen += 1
                    self.assertFalse(f.used, f"{r.designation}: {f.source} repeats a limit and is in use")
                    self.assertIn("limit", f.note)
        self.assertEqual(seen, 12)
        self.assertGreaterEqual(ledger.counts(self.records)["spin"]["limit"], 10)

    def test_an_ungraded_period_is_judged_the_same_whichever_source_holds_it(self):
        """The same number may not be 'used' from JPL and 'not used' from the lightcurve database."""
        for r in self.records:
            periods = [f for f in r.rows["spin"].facts if f.label == "period" and f.kind == "value"
                       and ledger.grade_rank(f.quality) is None]
            for a in periods:
                for b in periods:
                    if ledger.same_number(a.value, b.value):
                        self.assertEqual(a.used, b.used, f"{r.designation}: {a.source} against {b.source}")

    def test_a_fixed_table_older_than_the_asteroid_is_not_checked(self):
        first = {r.key: ledger.fact(r.rows["tracking"], "first observed") for r in self.records}
        for r in self.records:
            day = first[r.key].value if first[r.key] else None
            if day and day > "2023-10-01" and not any(f.source == "lcdb" for f in r.rows["spin"].facts):
                self.assertIn("lcdb", r.rows["spin"].unchecked, r.designation)
                self.assertNotEqual(r.rows["spin"].state, "prior", r.designation)
                self.assertIn("The lightcurve database is older than this asteroid.", r.rows["spin"].note)

    def test_weak_spitzer_fits_are_on_file_and_not_used(self):
        """ledger.toml [spitzer] and [reflectivity]: no used fact from a fit under the bar, none above 1."""
        weak = 0
        for r in self.records:
            for row in ("size", "surface"):
                for f in r.rows[row].facts:
                    if f.source == "spitzer" and "signal-to-noise" in (f.quality or ""):
                        snr = float(f.quality.rsplit(" ", 1)[1])
                        if snr < 5.0:
                            weak += 1
                            self.assertFalse(f.used, r.designation)
                    if f.label == "albedo" and f.used:
                        self.assertLessEqual(f.value, 1.0, r.designation)
        self.assertGreater(weak, 20)
        self.assertIn("signal-to-noise 0.9", self.get("2003 LN6").rows["size"].note)

    def test_fixture_adopted_values(self):
        self.assertEqual(ledger.adopted(self.get("2009 BD").rows["size"]).value, 4.0)
        self.assertEqual(ledger.adopted(self.get("Bennu").rows["size"]).value, 488.0)
        self.assertEqual(ledger.adopted(self.get("2023 RA4").rows["spin"]).value, 2.3478)
        self.assertEqual(ledger.adopted(self.get("2013 NJ").rows["spin"]).value, 250.0)
        self.assertEqual(ledger.adopted(self.get("2001 CQ36").rows["surface"]).source, "spitzer")
        self.assertIsNone(ledger.adopted(self.get("2011 AA37").rows["spin"]))
        self.assertIsNone(ledger.adopted(self.get("2010 NU71").rows["size"]))

    def test_the_period_under_5_kms_slower_than_2_2_hours(self):
        """AGENTS.md: 'every measured period under 5 km/s is faster than 2.2 hours' no longer holds."""
        slow = [r.designation for r in self.records
                if ledger.fact(r.rows["reach"], "delta-v").value < 5.0 and r.rows["spin"].state == "measured"
                and ledger.adopted(r.rows["spin"]).value >= 2.2]
        self.assertIn("2023 RA4", slow)

    def test_shape_of_every_record(self):
        self.assertEqual([r.key for r in self.records], self.order)
        self.assertEqual(len(self.records), len(set(self.order)))
        for r in self.records:
            self.assertEqual(tuple(r.rows), ROWS)
            self.assertEqual(r.populations, ["reachable"])
            self.assertEqual((r.data_date, r.method), (config.DATA_DATE, config.METHOD))
            self.assertEqual((r.summary, r.missions, r.observe, r.value, r.ladder), ({}, {}, None, {}, []))
            self.assertIn(r.designation, r.aliases)
            for name, row in r.rows.items():
                self.assertIn(row.state, STATES)
                self.assertIsNone(row.prior)
                for f in row.facts:
                    self.assertIn(f.source, ledger.ROW_SOURCES[name], f"{r.designation} {name} {f.label}")
                    self.assertIn(f.source, r.sources)
                    self.assertIn(f.label, ledger.LABEL.values())
                    self.assertIsNotNone(f.value)

    def test_not_checked_never_shows_as_not_measured(self):
        n_unchecked = 0
        for r in self.records:
            for name, row in r.rows.items():
                self.assertFalse(row.state == "prior" and row.unchecked, f"{r.designation} {name}")
                if row.state == "unchecked":
                    n_unchecked += 1
                    self.assertTrue(row.unchecked, f"{r.designation} {name}")
                    self.assertTrue(row.note, f"{r.designation} {name}")
                if row.unchecked:
                    # nor in any sentence the ledger writes about the row: the page prints these as they are
                    for text in [row.note or ""] + row.conflicts + [f.note or "" for f in row.facts]:
                        self.assertNotIn("not measured", text.lower(), f"{r.designation} {name}")
        self.assertGreater(n_unchecked, 20000)       # 5,500 objects without a card, four rows each

    def test_every_object_without_a_card_is_unchecked_on_the_card_rows(self):
        from longshot.ingest import ssodnet
        with research_cards_only():
            have = set(ssodnet._cards())
        without = [r for r in self.records if r.key not in have]
        self.assertGreater(len(without), 5000)
        for r in without:
            for name in ("size", "spin", "surface", "push"):
                row = r.rows[name]
                self.assertIn("ssodnet", row.unchecked)
                self.assertIn(row.state, ("measured", "limit", "unchecked"), f"{r.designation} {name}")

    def test_reach_and_tracking_are_always_measured(self):
        for r in self.records:
            self.assertEqual(r.rows["reach"].state, "measured")
            self.assertEqual(r.rows["tracking"].state, "measured")
            self.assertIsNotNone(ledger.fact(r.rows["reach"], "delta-v"))
            self.assertIsNotNone(ledger.fact(r.rows["tracking"], "condition code"))
            w = ledger.window(r)
            if r.gone:
                self.assertIsNone(w)                 # a body that no longer exists has no window
            elif w is None:
                self.assertEqual(ledger.fact(r.rows["tracking"], "next window").value, "none through 2045")
            else:
                self.assertLessEqual(w["start"], w["end"])
                self.assertEqual(w["as_of"], config.DATA_DATE)

    def test_no_measured_row_rests_on_an_unusable_value(self):
        for r in self.records:
            spin = r.rows["spin"]
            if spin.state == "measured":
                top = spin.facts[0]
                self.assertEqual((top.label, top.kind), ("period", "value"))
                rank = ledger.grade_rank(top.quality)
                self.assertTrue(rank is None or rank >= ledger.grade_rank("2-"), r.designation)
            surface = r.rows["surface"]
            if surface.state == "measured":
                self.assertTrue(any(f.label == "class" or (f.label == "albedo" and f.quality != "Computed")
                                    for f in surface.facts), r.designation)
            if r.rows["size"].state == "measured":
                self.assertEqual(r.rows["size"].facts[0].label, "diameter")

    def test_counts(self):
        table = ledger.counts(self.records)
        n = len(self.records)
        for row in ROWS:
            self.assertEqual(sum(table[row].values()), n)
        self.assertEqual(table["reach"]["measured"], n)
        # docs/research/verify-coverage.md: 197 reachable asteroids have a size on file. One (2010 NU71) is wrong,
        # 13 are Spitzer fits under signal-to-noise 5 with no other size, and one more (Kamoʻoalewa) is hand-entered.
        self.assertEqual(table["size"]["measured"], 184)
        self.assertEqual(table["spin"]["limit"], 11)
        self.assertIn(str(n), ledger.format_counts(self.records).splitlines()[0])

    def test_written_file_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = ledger.write(self.records, Path(tmp) / "ledger.jsonl")
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(os.listdir(tmp), ["ledger.jsonl"])
        self.assertEqual(len(lines), len(self.records))
        for line, r in zip(lines, self.records):
            self.assertEqual(json.loads(line), json.loads(json.dumps(dataclasses.asdict(r))))
        first = json.loads(lines[0])
        self.assertEqual(list(first), [f.name for f in dataclasses.fields(type(self.records[0]))])
        self.assertEqual(list(first["rows"]), list(ROWS))


class DeterminismCase(unittest.TestCase):
    def test_two_builds_give_identical_bytes(self):
        """Two fresh processes with different hash seeds write the same build/ledger.jsonl, byte for byte."""
        script = (
            "import sys\n"
            "from pathlib import Path\n"
            "from longshot import config, ledger\n"
            "from tests.fixtures import research_cards_only\n"
            "config.BUILD = Path(sys.argv[1])\n"
            "with research_cards_only():\n"
            "    ledger.build()\n"
        )
        outputs = []
        with tempfile.TemporaryDirectory() as tmp:
            for seed in ("1", "4242"):
                build = Path(tmp) / f"build-{seed}"
                env = dict(os.environ, PYTHONHASHSEED=seed)
                done = subprocess.run([sys.executable, "-c", script, str(build)], cwd=config.ROOT, env=env,
                                      capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stderr)
                outputs.append((build / "ledger.jsonl").read_bytes())
        self.assertGreater(len(outputs[0]), 1_000_000)
        self.assertEqual(outputs[0], outputs[1])
        self.assertTrue(outputs[0].endswith(b"\n"))
        self.assertEqual(outputs[0].count(b"\n"), len(nhats.reachable()))


class LiveDataCase(unittest.TestCase):
    """The build as configured, with whatever cards are on disk now."""

    def test_the_invariant_holds_with_the_live_card_folder(self):
        records = ledger.build(write_file=False)
        self.assertEqual(len(records), len(nhats.reachable()))
        for r in records:
            for name, row in r.rows.items():
                self.assertIn(row.state, STATES)
                self.assertFalse(row.state == "prior" and row.unchecked, f"{r.designation} {name}")
                self.assertFalse(row.state == "unchecked" and not row.unchecked, f"{r.designation} {name}")


if __name__ == "__main__":
    unittest.main()
