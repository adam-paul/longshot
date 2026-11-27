"""The six source readers: what they claim, what they cover, and how they fail.

Run: uv run python -m unittest tests.test_ingest
"""
import json
import os
import re
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from longshot import config, ids, ingest, sources
from longshot.ingest import _common, lcdb, nhats, pravec, sbdb, spitzer, ssodnet
from longshot.ingest._common import IngestError
from longshot.types import ROWS
from tests.fixtures import research_cards_only

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Which rows each source must write a coverage record for, per reachable object.
EXPECTED_COVERAGE = {
    "jpl-nhats": {"reach", "tracking"},
    "jpl-sbdb": {"tracking", "size", "spin", "surface", "push"},
    "ssodnet": {"size", "spin", "surface", "push"},
    "pravec": {"spin"},
    "lcdb": {"spin"},
    "spitzer": {"size", "surface"},
}
# The hand-entered list only adds claims: it writes coverage where it has a value and nowhere else.
SUPPLEMENTARY = {"curated"}


def by(claims, key, prop):
    return [c for c in claims if c.key == key and c.prop == prop]


class LoadedCase(unittest.TestCase):
    """Everything read once, from the research snapshot of cards only."""

    @classmethod
    def setUpClass(cls):
        cls.view = research_cards_only()
        cls.view.__enter__()
        cls.index = ids.load()
        cls.reachable = nhats.reachable()
        cls.loaded = {sid: m.load() for sid, m in ingest.modules().items()}
        cls.sources = dict(sources.SOURCES)

    @classmethod
    def tearDownClass(cls):
        cls.view.__exit__(None, None, None)

    def key(self, name):
        key = self.index.resolve(name)
        self.assertIsNotNone(key, name)
        return key

    # -- shape ---------------------------------------------------------

    def test_reachable_population(self):
        raw = _common.read_json(config.NHATS_JSON)["data"]
        self.assertEqual(len(self.reachable), len(raw))
        self.assertEqual(len(set(self.reachable)), len(raw))
        self.assertGreater(len(raw), 7000)
        numbers = [self.index.identity(k).number for k in self.reachable]
        numbered = [n for n in numbers if n is not None]
        self.assertEqual(numbered, sorted(numbered))
        self.assertTrue(all(n is not None for n in numbers[:len(numbered)]), "numbered objects come first")

    def test_every_source_covers_every_reachable_object_once_per_row(self):
        for sid, (claims, coverage) in self.loaded.items():
            with self.subTest(sid):
                seen = {}
                for c in coverage:
                    self.assertEqual(c.source, sid)
                    self.assertIn(c.row, ROWS)
                    self.assertIn(c.outcome, ("found", "absent", "unchecked"))
                    self.assertNotIn((c.key, c.row), seen)
                    seen[(c.key, c.row)] = c
                if sid in SUPPLEMENTARY:
                    self.assertEqual({c.outcome for c in coverage}, {"found"})
                    self.assertEqual({c.key for c in claims}, {k for k, _ in seen})
                    continue
                self.assertEqual({row for _, row in seen}, EXPECTED_COVERAGE[sid])
                self.assertEqual(len(seen), len(self.reachable) * len(EXPECTED_COVERAGE[sid]))
                self.assertEqual({k for k, _ in seen}, set(self.reachable))
                reach = set(self.reachable)
                for c in claims:
                    self.assertEqual(c.source, sid)
                    self.assertIn(c.key, reach)
                    self.assertIn(c.kind, ("value", "upper", "lower"))
                    self.assertIsNotNone(c.value)
                    if c.lo is not None or c.hi is not None:
                        self.assertLessEqual(c.lo, c.hi)

    def test_unchecked_always_says_why(self):
        for sid, (_, coverage) in self.loaded.items():
            for c in coverage:
                if c.outcome == "unchecked":
                    self.assertTrue(c.reason, f"{sid} {c.key} {c.row}")

    def test_source_records(self):
        self.assertEqual(list(self.sources), list(ingest.SOURCE_IDS))
        for sid, s in self.sources.items():
            with self.subTest(sid):
                self.assertEqual(s.id, sid)
                self.assertRegex(s.edition, ISO)
                self.assertRegex(s.retrieved, ISO)
                self.assertLessEqual(s.edition, s.retrieved)
                self.assertTrue(s.name and s.citation)
                self.assertTrue(s.url.startswith("http") or sid in SUPPLEMENTARY)
        s = self.sources
        self.assertEqual(s["jpl-nhats"].edition, "2026-11-24")
        self.assertEqual(s["jpl-sbdb"].retrieved, "2026-11-24")
        self.assertEqual(s["ssodnet"].edition, "2026-09-14")       # every card's ssocard.datetime
        self.assertEqual(s["ssodnet"].retrieved, "2026-11-21")     # the research snapshot
        self.assertEqual(s["pravec"].edition, "2026-10-15")        # the latest DateExport in the table
        self.assertEqual(s["pravec"].retrieved, "2026-11-24")      # from the file name
        self.assertEqual(s["lcdb"].edition, "2023-10-01")          # "GENERATED: Oct 01, 2023"
        self.assertEqual(s["spitzer"].edition, "2019-11-30")       # the latest midtime
        self.assertEqual(s["curated"].edition, "2026-11-25")       # registry/curated.toml, its own edition line

    # -- nhats ---------------------------------------------------------

    def test_nhats_survey_only_windows(self):
        claims, _ = self.loaded["jpl-nhats"]
        raw = {r["des"]: r for r in _common.read_json(config.NHATS_JSON)["data"]}
        pointing = {c.key: c.value for c in claims if c.prop == "window_pointing"}
        none = {c.key for c in claims if c.prop == "next_window"}
        n_survey = 0
        for des, r in raw.items():
            key = self.index.key_for_pdes(des)
            if r["obs_start"] is None:
                self.assertIn(key, none, des)
                self.assertNotIn(key, pointing, des)
            else:
                self.assertEqual(pointing[key], "survey-only" if r["obs_flag"] == "S" else "pointable", des)
                n_survey += r["obs_flag"] == "S"
        self.assertGreater(n_survey, 2000)
        # 2010 PS66 is data[0]: obs_flag "S", 2035-05-14 to 2035-06-18, peak 23.69
        k = self.key("2010 PS66")
        self.assertEqual(pointing[k], "survey-only")
        self.assertEqual(by(claims, k, "window_start")[0].value, "2035-05-14")
        self.assertEqual(by(claims, k, "window_end")[0].value, "2035-06-18")
        self.assertEqual(by(claims, k, "window_peak_mag")[0].value, 23.69)
        self.assertEqual(by(claims, k, "window_start")[0].ref, f"as of {config.DATA_DATE}")
        self.assertEqual(by(claims, k, "delta_v_kms")[0].value, 10.270)
        self.assertEqual(by(claims, k, "delta_v_kms")[0].unit, "km/s")

    # -- sbdb ----------------------------------------------------------

    def test_sbdb_push_values_say_they_are_rounded(self):
        claims, _ = self.loaded["jpl-sbdb"]
        pushes = [c for c in claims if c.prop in ("A1", "A2", "A3")]
        self.assertGreater(len(pushes), 150)
        for c in pushes:
            self.assertIn("rounded to two figures", c.note)
            self.assertIn("force law", c.note)
            self.assertEqual(c.unit, "au/d^2")
        k = self.key("2009 BD")
        a1 = by(claims, k, "A1")[0]
        self.assertEqual(a1.value, 5.6e-11)
        self.assertAlmostEqual(a1.lo, 5.6e-11 - 8.5e-12, delta=1e-16)
        self.assertAlmostEqual(a1.hi, 5.6e-11 + 8.5e-12, delta=1e-16)

    def test_sbdb_period_has_no_grade(self):
        claims, _ = self.loaded["jpl-sbdb"]
        p = by(claims, self.key("2011 AA37"), "period_h")[0]
        self.assertEqual(p.value, 10.0)
        self.assertIsNone(p.quality)
        self.assertIn("no quality grade", p.note)

    def test_sbdb_diameter_is_in_metres(self):
        claims, _ = self.loaded["jpl-sbdb"]
        d = by(claims, self.key("Bennu"), "diameter_m")[0]
        self.assertEqual((d.value, d.unit), (484.44, "m"))

    # -- ssodnet -------------------------------------------------------

    def test_ssodnet_computed_albedo_keeps_its_tag(self):
        claims, coverage = self.loaded["ssodnet"]
        k = self.key("2009 BD")
        albedo = by(claims, k, "albedo")
        self.assertEqual([c.quality for c in albedo], ["Computed"])
        self.assertEqual(albedo[0].value, 0.6352)
        d = by(claims, k, "diameter_m")[0]
        self.assertEqual((d.value, d.lo, d.hi, d.unit, d.quality), (4.0, 3.0, 5.0, "m", "TPM"))
        self.assertIn("Mommert+2014a", d.ref)

    def test_ssodnet_units(self):
        claims, _ = self.loaded["ssodnet"]
        k = self.key("2001 CQ36")
        a2 = by(claims, k, "A2")[0]
        self.assertAlmostEqual(a2.value, -148.395e-15, delta=1e-19)   # the card gives 1e-15 au/d^2
        self.assertEqual(a2.unit, "au/d^2")
        drift = by(claims, k, "drift_au_per_myr")[0]
        self.assertAlmostEqual(drift.value, -67.0924e-4, delta=1e-9)  # the card gives 1e-4 au/Myr
        self.assertLess(drift.lo, drift.value)
        self.assertLess(drift.value, drift.hi)

    def test_ssodnet_spin_grades(self):
        claims, _ = self.loaded["ssodnet"]
        self.assertEqual(by(claims, self.key("2013 NJ"), "period_h")[0].quality, "2")       # period_flag "U=2"
        self.assertIsNone(by(claims, self.key("469219"), "period_h")[0].quality)            # no period_flag
        self.assertEqual(ssodnet.grade("U=2+"), "2+")
        self.assertEqual(ssodnet.grade("U=3-"), "3-")
        self.assertIsNone(ssodnet.grade("Quality of the period not rated."))
        self.assertIsNone(ssodnet.grade("Quality of the period not rated.;Quality of the period not rated."))
        self.assertIsNone(ssodnet.grade(None))

    def test_ssodnet_coverage_states(self):
        _, coverage = self.loaded["ssodnet"]
        cov = {(c.key, c.row): c for c in coverage}
        bd = self.key("2009 BD")
        self.assertEqual(cov[(bd, "size")].outcome, "found")
        self.assertEqual(cov[(bd, "spin")].outcome, "absent")       # a card exists and holds no spin
        qq8 = self.key("2026 QQ8")
        for row in ("size", "spin", "surface", "push"):
            self.assertEqual(cov[(qq8, row)].outcome, "unchecked")  # _status.tsv line 1: 404
            self.assertIn("did not know this object", cov[(qq8, row)].reason)

    # -- pravec, lcdb, spitzer -------------------------------------------

    def test_pravec_rows(self):
        claims, coverage = self.loaded["pravec"]
        p = by(claims, self.key("2011 AA37"), "period_h")[0]
        # the U column says 1; the remark grades it finer, and the lower of its pair is the claim's grade
        self.assertEqual((p.value, p.quality, p.kind), (10.0, "1+", "value"))
        self.assertIn("graded 1+ or 2−", p.note)
        self.assertIn("the lower grade is used", p.note)
        p = by(claims, self.key("2023 RA4"), "period_h")[0]
        self.assertEqual((p.value, p.quality, p.lo, p.hi), (2.3478, "2", 2.3472, 2.3484))
        self.assertIn("2023-11-14", p.ref)
        p = by(claims, self.key("1999 AO10"), "period_h")[0]
        self.assertEqual((p.value, p.quality), (11.06, "2+"))               # column 3, remark "U = 2+ or 3-"
        p = by(claims, self.key("2026 AC4"), "period_h")[0]
        self.assertEqual(p.quality, "2-")                                   # the remark's finer grade; the grade says it all
        self.assertNotIn("U column", p.note or "")
        self.assertEqual(sum(1 for c in coverage if c.outcome == "found"), 127)    # upstream-physical.md, 3.2

    def test_pravec_parse(self):
        rows = pravec.parse()
        self.assertEqual(len(rows), 2530)
        by_line = {r["line"]: r for r in rows}
        self.assertEqual(by_line[2189]["ident"], "2011 AA37")
        self.assertEqual(by_line[2189]["exported"], "2019-01-09")
        self.assertEqual(by_line[2395]["period_h"], 250.0)                  # right-aligned into the id column
        self.assertEqual(by_line[2395]["ident"], "2013 NJ")
        self.assertEqual(by_line[4335]["last_lc"], "2023-10-18")
        self.assertTrue(pravec.is_lower_limit(by_line[4261]))               # 2023 JK: "P >~ 20 h"
        self.assertTrue(pravec.is_lower_limit(by_line[1609]))               # "A lower limit on P is 25 hours."
        self.assertFalse(pravec.is_lower_limit(by_line[793]))               # "A lower limit on D_2/D_1 is 0.36"
        self.assertFalse(pravec.is_lower_limit(by_line[4335]))

    def test_pravec_lower_limit_becomes_a_bound(self):
        row = {"ident": "x", "period_h": 34.0, "error_h": 0.0, "amplitude": 1.0, "u": "1", "last_lc": "1999-06-20",
               "exported": "2003-09-11", "analyser": "Pravec", "remark": "P>19 h, A>=1.0 mag, U=1+", "line": 383}
        claims = pravec.claims_for("aaaaaa", [row])
        self.assertEqual([(c.prop, c.kind, c.value) for c in claims], [("period_h", "lower", 19.0)])

    def test_lcdb_rows(self):
        claims, coverage = self.loaded["lcdb"]
        p = by(claims, self.key("2011 AA37"), "period_h")[0]
        self.assertEqual((p.value, p.quality, p.kind), (10.0, "1+", "value"))
        p = by(claims, self.key("Bennu"), "period_h")[0]
        self.assertEqual((p.value, p.quality), (4.2968, "3"))
        cov = {c.key: c for c in coverage}
        self.assertEqual(cov[self.key("2009 BD")].outcome, "absent")        # listed, with no period
        self.assertEqual(cov[self.key("2022 OB5")].outcome, "absent")       # not listed
        self.assertEqual(sum(1 for c in coverage if c.outcome == "found"), 304)   # verify-coverage.md

    def test_a_cell_that_is_present_and_unreadable_stops_the_build(self):
        """A blank cell is "no value". A cell that holds something that is not a number or a date is damage."""
        from longshot.ingest._common import date_cell, number
        self.assertIsNone(number("", "x"))
        self.assertIsNone(number(None, "x"))
        self.assertEqual(number(" 4.5 ", "x"), 4.5)
        for cell in ("25,1", "0.49km", "4.3 h", "E", float("nan")):
            with self.subTest(cell=cell), self.assertRaises(IngestError):
                number(cell, "file: object: field")
        self.assertEqual(date_cell("2035-05-14 00:00", "x"), "2035-05-14")
        self.assertIsNone(date_cell("", "x"))
        for cell in ("2035-5-14", "14 May 2035", "soon"):
            with self.subTest(cell=cell), self.assertRaises(IngestError):
                date_cell(cell, "file: object: field")

        row = dict(next(r for r in nhats.parse() if r["des"] == "2001 CQ36"))
        self.assertTrue(nhats.claims_for("aaaaaa", row))
        for field, value in (("h", "25,1"), ("obs_start", "14 May 2035"), ("obs_end", ""), ("occ", "E")):
            with self.subTest(field=field), self.assertRaises(IngestError) as caught:
                nhats.claims_for("aaaaaa", {**row, field: value})
            self.assertIn("2001 CQ36", str(caught.exception))
        d = dict(sbdb.parse()["2001 CQ36"])
        for field, value in (("diameter", "0.49km"), ("rot_per", "4.3 h"), ("condition_code", "E")):
            with self.subTest(field=field), self.assertRaises(IngestError) as caught:
                sbdb.claims_for("aaaaaa", {**d, field: value})
            self.assertIn(field, str(caught.exception))

    def test_a_fixed_table_is_not_checked_for_an_asteroid_found_after_it(self):
        """ledger.toml [fixed_tables]: the lightcurve database of 2023 and Pravec's table. [closed_tables]: Spitzer."""
        from longshot.ingest._common import OLDER_THAN_OBJECT, first_observed, too_old_for
        first = first_observed()
        # Spitzer has stopped observing: an asteroid found after its surveys is absent from a final table, not unchecked.
        from longshot.ingest.spitzer import CLOSED_REASON
        sp = self.loaded["spitzer"][1]
        self.assertFalse([c for c in sp if c.outcome == "unchecked"])
        closed = [c for c in sp if c.reason == CLOSED_REASON]
        self.assertTrue(closed)
        self.assertTrue(all(c.outcome == "absent" and first[c.key] > "2019-11-30" for c in closed))
        for sid, edition in (("lcdb", "2023-10-01"), ("pravec", "2026-10-15")):
            claims, coverage = self.loaded[sid]
            with self.subTest(sid):
                late = [c for c in coverage if c.outcome == "unchecked"]
                self.assertTrue(late)
                self.assertEqual({c.reason for c in late}, {OLDER_THAN_OBJECT})
                self.assertTrue(all(first[c.key] > edition for c in late))
                # every asteroid first seen after the edition that the table does not hold is unchecked, none absent
                self.assertFalse([c for c in coverage if c.outcome == "absent" and not c.reason
                                  and first.get(c.key, "") > edition])
        self.assertTrue(too_old_for("2023-10-01", "2023-10-02"))
        self.assertFalse(too_old_for("2023-10-01", "2023-10-01"))
        self.assertFalse(too_old_for("2023-10-01", None))
        # 2025 FE6 was found after the lightcurve database's release: its spin row may not say "not measured" on it
        k = self.key("2025 FE6")
        cov = next(c for c in self.loaded["lcdb"][1] if c.key == k)
        self.assertEqual((cov.outcome, cov.reason), ("unchecked", OLDER_THAN_OBJECT))

    def test_spitzer_claims_carry_the_signal_to_noise(self):
        claims, _ = self.loaded["spitzer"]
        d = by(claims, self.key("2003 LN6"), "diameter_m")[0]
        self.assertEqual(d.snr, 0.9)
        self.assertEqual(d.quality, "thermal model, one band, signal-to-noise 0.9")
        self.assertTrue(all(c.snr is not None for c in claims))

    def test_curated_claims(self):
        """registry/curated.toml: each claim names its citation and where under docs/research it was verified."""
        from longshot.ingest import curated
        edition, entries = curated.parse()
        for e in entries:
            with self.subTest(e["designation"], prop=e["prop"]):
                self.assertTrue(e["citation"] and e["verified_passage"])
                text = (config.ROOT / e["verified_in"]).read_text(encoding="utf-8")
                self.assertIn(e["verified_passage"], text)       # quoted word for word
        claims, _ = self.loaded["curated"]
        p = by(claims, self.key("2022 OB5"), "period_h")[0]
        self.assertEqual((p.value, p.unit), (0.0257, "h"))                  # 1.542 min
        self.assertAlmostEqual((p.hi - p.lo) / 2 * 60, 0.001, places=9)     # +/- 0.001 min
        self.assertIn("arXiv:2605.04784", p.ref)
        self.assertEqual(by(claims, self.key("2022 OB5"), "taxonomy")[0].value, "X")
        d = by(claims, self.key("469219"), "diameter_m")[0]
        self.assertEqual((d.value, d.lo, d.hi, d.unit), (18.0, 16.0, 20.0, "m"))
        self.assertIn("arXiv:2606.24017", d.ref)

    def test_a_curated_claim_without_its_evidence_stops_the_build(self):
        from longshot.ingest import curated
        good = ('schema = 1\nedition = "2026-11-25"\n[[claim]]\ndesignation = "2016 HO3"\nprop = "diameter_m"\n'
                'value = 18.0\nerror = 2.0\nunit = "m"\ncitation = "X 2026"\n'
                'verified_in = "docs/research/verify-capability.md"\nverified_passage = "row 18"\n')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "curated.toml"
            path.write_text(good)
            self.assertEqual(len(curated.parse(path)[1]), 1)
            for name, text in {
                "no citation": good.replace('citation = "X 2026"\n', ""),
                "no passage": good.replace('verified_passage = "row 18"\n', ""),
                "a file that is not there": good.replace("verify-capability.md", "nowhere.md"),
                "an unknown property": good.replace("diameter_m", "mass_t"),
                "an unknown unit": good.replace('unit = "m"', 'unit = "ft"'),
                "an unknown field": good + 'grade = "3"\n',
                "no edition": good.replace('edition = "2026-11-25"\n', ""),
            }.items():
                with self.subTest(name), self.assertRaises(IngestError):
                    path.write_text(text)
                    curated.parse(path)

    def test_a_text_table_is_checked_against_the_checksum_beside_it(self):
        """A table cut short at a line boundary parses clean; its checksum is what catches it."""
        import hashlib
        from longshot.ingest._common import read_table
        with tempfile.TemporaryDirectory() as tmp:
            table = Path(tmp) / "table.txt"
            table.write_bytes(b"line one\nline two\nline three\n")
            self.assertEqual(read_table(table), table.read_bytes())            # no checksum kept: read as it is
            side = Path(tmp) / "table.txt.sha256"
            side.write_text(hashlib.sha256(table.read_bytes()).hexdigest() + "  table.txt\n")
            self.assertEqual(read_table(table), table.read_bytes())
            table.write_bytes(b"line one\nline two\n")                         # cut at a line boundary
            with self.assertRaises(IngestError) as caught:
                read_table(table)
            self.assertIn("cut short or changed", str(caught.exception))

    def test_lcdb_bounds(self):
        row = {"number": 0, "name": "x", "desig": "x", "pflag": ">", "period_h": 16.0, "pdesc": "", "ampmin": None,
               "ampmax": 0.2, "ampflag": ">", "u": "2", "notes": "", "line": 1}
        claims = lcdb.claims_for("aaaaaa", row)
        self.assertEqual([(c.prop, c.kind, c.value) for c in claims],
                         [("period_h", "lower", 16.0), ("amplitude_mag", "lower", 0.2)])
        row["pflag"] = "<"
        self.assertEqual(lcdb.claims_for("aaaaaa", row)[0].kind, "upper")

    def test_spitzer_rows(self):
        claims, _ = self.loaded["spitzer"]
        k = self.key("2001 CQ36")
        d = by(claims, k, "diameter_m")[0]
        self.assertEqual((d.value, d.lo, d.hi, d.unit), (56.0, 46.0, 77.0, "m"))
        a = by(claims, k, "albedo")[0]
        self.assertEqual((a.value, a.lo, a.hi), (0.467, 0.243, 0.719))
        self.assertIn("Trilling et al. 2010", a.ref)


class FetchToolCase(unittest.TestCase):
    """tools/fetch_ssodnet_cards.py, with no network: a card lands whole or not at all, and a failure is retried."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_cards", config.ROOT / "tools" / "fetch_ssodnet_cards.py")
        cls.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.tool)            # importing it fetches nothing: the work is in main()

    class Answer:
        def __init__(self, body, status=200):
            self.body, self.status = body, status

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self.body

    def test_a_card_is_written_whole_under_its_final_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = json.dumps({"2010_PH9": {"id": "2010_PH9", "name": "2010 PH9", "parameters": {}}}).encode()
            final = self.tool.save_card(tmp, "2010 PH9", body)
            self.assertEqual(os.listdir(tmp), ["2010_PH9.json"])                # no temporary file is left
            self.assertEqual(Path(final).read_bytes(), body)
            self.assertEqual(Path(final).name, ssodnet.card_file_name("2010 PH9"))   # the name the build looks for
            # a write that fails part-way leaves the old card in place
            with mock.patch.object(os, "replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    self.tool.save_card(tmp, "2010 PH9", b"half a ca")
            self.assertEqual(Path(final).read_bytes(), body)
            # and the build never globs a temporary file as a card
            self.assertFalse([p for p in Path(tmp).glob("*.json") if p.name.startswith(".")])

    def test_a_failure_is_asked_again_and_an_unknown_object_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / "journal.jsonl"
            lines = [{"des": "A", "outcome": "failed"}, {"des": "B", "outcome": "unknown"},
                     {"des": "C", "outcome": "card"}, {"des": "D", "outcome": "failed"}, {"des": "D", "outcome": "card"},
                     {"des": "E", "outcome": "card"}, {"des": "E", "outcome": "failed"}]
            journal.write_text("".join(json.dumps(x) + "\n" for x in lines) + '{"des": "F", "outc')
            last = self.tool.last_outcomes(str(journal))
            self.assertEqual(last, {"A": "failed", "B": "unknown", "C": "card", "D": "card", "E": "failed"})
            todo = self.tool.todo_list(["A", "B", "C", "D", "E", "F", "G"], have={"g"}, outcomes=last)
            self.assertEqual(todo, ["A", "E", "F"])       # failures and the never-asked; G has a card on disk

    def test_an_answer_that_is_not_a_card_is_a_failure_not_an_unknown_object(self):
        def answering(body, status=200):
            return lambda request, timeout: self.Answer(body, status)
        rec, body = self.tool.fetch("2010 PH9", opener=answering(b'{"error": "try later"}'))
        self.assertEqual((rec["outcome"], body), ("failed", None))
        rec, body = self.tool.fetch("2010 PH9", opener=answering(b"<html>busy</html>"))
        self.assertEqual((rec["outcome"], body), ("failed", None))
        card = json.dumps({"id": "2010_PH9", "parameters": {"physical": {}}}).encode()
        rec, body = self.tool.fetch("2010 PH9", opener=answering(card))
        self.assertEqual((rec["outcome"], body), ("card", card))

        def not_found(request, timeout):
            import urllib.error
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)
        self.assertEqual(self.tool.fetch("2010 PH9", opener=not_found)[0]["outcome"], "unknown")

        def timed_out(request, timeout):
            raise TimeoutError("timed out")
        rec, _ = self.tool.fetch("2010 PH9", opener=timed_out)
        self.assertEqual(rec["outcome"], "failed")
        self.assertIn("timed out", rec["error"])


class LiveCardsCase(unittest.TestCase):
    """The second card folder and the journal, with made-up contents."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.cards = self.dir / "cards"
        self.cards.mkdir()
        self.journal = self.dir / "journal.jsonl"
        self.patches = [mock.patch.object(ssodnet, "LIVE_CARDS", self.cards),
                        mock.patch.object(ssodnet, "JOURNAL", self.journal)]
        for p in self.patches:
            p.start()
        self.recards()
        self.index = ids.load()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.recards()
        self.tmp.cleanup()

    def recards(self):
        """Forget the cards read so far; the other sources are untouched by these tests."""
        ssodnet._cards.cache_clear()
        sources.load.cache_clear()

    def coverage(self, name):
        key = self.index.resolve(name)
        _, coverage = ssodnet.load()
        return {c.row: c for c in coverage if c.key == key}

    def card(self, ident, physical=None, wrapped=False, datetime="2026-09-14T23:00:01+00:00"):
        body = {"id": ident.replace(" ", "_"), "name": ident, "number": None, "type": "Asteroid",
                "ssocard": {"version": "1.2.4", "datetime": datetime},
                "parameters": {"physical": physical or {}, "dynamical": {}}}
        return json.dumps({body["id"]: body} if wrapped else body)

    def test_a_missing_card_is_unchecked(self):
        # 2010 PH9 (delta-v 11.4 km/s) is not among the research snapshot's cards.
        cov = self.coverage("2010 PH9")
        self.assertEqual({c.outcome for c in cov.values()}, {"unchecked"})
        self.assertEqual({c.reason for c in cov.values()}, {"no SsODNet card has been fetched"})

    def test_a_card_in_the_second_folder_is_read_wrapped_or_bare(self):
        for wrapped in (False, True):
            with self.subTest(wrapped=wrapped):
                (self.cards / "2010_PH9.json").write_text(self.card(
                    "2010 PH9", wrapped=wrapped,
                    physical={"diameter": {"value": 0.02, "error": {"min": -0.005, "max": 0.004},
                                           "method": [{"label": "Radar"}], "bibref": [{"shortbib": "Test+2026"}]}}))
                self.journal.write_text(json.dumps(
                    {"des": "2010 PH9", "status": 200, "outcome": "card", "at": "2026-11-25T06:50:48+00:00"}) + "\n")
                self.recards()
                cov = self.coverage("2010 PH9")
                self.assertEqual(cov["size"].outcome, "found")
                self.assertEqual({cov[r].outcome for r in ("spin", "surface", "push")}, {"absent"})
                claims, _ = ssodnet.load()
                d = [c for c in claims if c.key == self.index.resolve("2010 PH9")]
                self.assertEqual([(c.prop, c.value, c.lo, c.hi, c.quality, c.ref) for c in d],
                                 [("diameter_m", 20.0, 15.0, 24.0, "Radar", "Test+2026")])
                self.assertEqual((ssodnet.source().retrieved_from, ssodnet.source().retrieved), ("2026-11-21", "2026-11-25"))

    def test_the_journal_gives_the_reason(self):
        lines = [
            {"des": "2010 PH9", "status": 404, "outcome": "unknown", "at": "2026-11-25T07:00:00+00:00"},
            {"des": "2010 MB", "outcome": "failed", "error": "URLError(TimeoutError('timed out'))",
             "at": "2026-11-25T07:00:02+00:00"},
            {"des": "2010 FY9", "status": 500, "outcome": "failed", "at": "2026-11-25T07:00:04+00:00"},
        ]
        self.journal.write_text("".join(json.dumps(x) + "\n" for x in lines))
        self.recards()
        cov = self.coverage("2010 PH9")
        self.assertEqual({c.outcome for c in cov.values()}, {"unchecked"})
        self.assertEqual(cov["spin"].reason, "SsODNet did not know this object on 2026-11-25")
        cov = self.coverage("2010 MB")
        self.assertEqual({c.outcome for c in cov.values()}, {"unchecked"})
        self.assertEqual(cov["spin"].reason, "the request to SsODNet failed on 2026-11-25 (timed out)")
        self.assertEqual(self.coverage("2010 FY9")["size"].reason,
                         "the request to SsODNet failed on 2026-11-25 (HTTP 500)")

    def test_a_journal_line_still_being_written_is_ignored(self):
        good = json.dumps({"des": "2010 PH9", "status": 404, "outcome": "unknown", "at": "2026-11-25T07:00:00+00:00"})
        self.journal.write_text(good + "\n" + '{"des": "2010 MB", "sta')
        self.assertEqual(list(ssodnet.read_journal()), ["2010 PH9"])
        self.journal.write_text('{"des": "2010 MB", "sta\n' + good + "\n")
        with self.assertRaises(IngestError):
            ssodnet.read_journal()

    DAMAGED = {"empty": "", "cut short": '{"id": "2010_PH9", "parameters": {"phys',
               "not a card": '{"error": "not found"}', "a list": "[]"}

    def test_a_damaged_card_the_journal_lists_stops_the_build(self):
        self.journal.write_text(json.dumps({"des": "2010 PH9", "outcome": "card", "at": "2026-11-25T02:00:00+00:00"}) + "\n")
        for name, body in self.DAMAGED.items():
            with self.subTest(name):
                (self.cards / "2010_PH9.json").write_text(body)
                self.recards()
                with self.assertRaises(IngestError) as caught:
                    ssodnet.load()
                self.assertIn("2010_PH9.json", str(caught.exception))

    def test_a_card_still_being_written_is_not_checked_and_says_so(self):
        # no journal line yet: a fetch job that writes in place is part-way through the file
        for name, body in self.DAMAGED.items():
            with self.subTest(name):
                (self.cards / "2010_PH9.json").write_text(body)
                self.recards()
                cov = self.coverage("2010 PH9")
                self.assertEqual({c.outcome for c in cov.values()}, {"unchecked"})
                self.assertEqual({c.reason for c in cov.values()},
                                 {"a card file is on disk and could not be read; it may still be being written"})

    def test_a_damaged_card_in_the_research_snapshot_stops_the_build(self):
        # nothing writes to the snapshot, so an unreadable card there is damage, journal or no journal
        snapshot = self.dir / "snapshot"
        snapshot.mkdir()
        (snapshot / "2010_MB.json").write_text('{"id": "2010_MB", "parameters": {"phys')
        with mock.patch.object(config, "SSODNET_CARDS", snapshot):
            self.recards()
            with self.assertRaises(IngestError) as caught:
                ssodnet.load()
        self.assertIn("2010_MB.json", str(caught.exception))

    def test_a_placeholder_error_is_dropped_and_a_repeated_entry_is_one_claim(self):
        spin = {"period": {"value": 0.0275528, "error": {"min": -1.0, "max": 1.0}}, "period_flag": None}
        card = json.loads(self.card("2010 PH9", physical={
            "spins": [spin, dict(spin)],
            "albedo": [{"value": 0.2, "error": {"min": -0.3, "max": 0.3}, "method": [{"label": "NEATM"}]}],
            "diameter": {"value": 0.02, "error": {"min": -0.005, "max": 0.004}},
        }))
        claims = ssodnet.claims_from_card("aaaaaa", card)
        periods = [c for c in claims if c.prop == "period_h"]
        self.assertEqual(len(periods), 1)                                   # the card lists the entry twice
        self.assertEqual((periods[0].lo, periods[0].hi), (None, None))      # 99 s "from -3,501 to 3,699 s"
        self.assertIn(ssodnet.PLACEHOLDER, periods[0].note)
        albedo = next(c for c in claims if c.prop == "albedo")
        self.assertEqual((albedo.lo, albedo.hi, albedo.note), (None, None, ssodnet.PLACEHOLDER))
        size = next(c for c in claims if c.prop == "diameter_m")
        self.assertEqual((size.lo, size.hi, size.note), (15.0, 24.0, None))  # a real error is kept

    def test_a_card_is_matched_by_what_it_says_not_by_its_file_name(self):
        (self.cards / "2010_PH9.json").write_text(self.card("2010 MB"))
        self.recards()
        self.assertEqual({c.outcome for c in self.coverage("2010 PH9").values()}, {"unchecked"})
        self.assertEqual({c.outcome for c in self.coverage("2010 MB").values()}, {"absent"})

    def test_no_card_folder_at_all_stops_the_build(self):
        with mock.patch.object(config, "SSODNET_CARDS", self.dir / "nowhere"), \
                mock.patch.object(ssodnet, "LIVE_CARDS", self.dir / "nowhere-either"):
            self.recards()
            with self.assertRaises(IngestError):
                ssodnet.load()
        (self.dir / "hollow").mkdir()
        with mock.patch.object(config, "SSODNET_CARDS", self.dir / "hollow"):
            self.recards()
            with self.assertRaises(IngestError):
                ssodnet.load()


class DamagedFileCase(unittest.TestCase):
    """A damaged or empty source file raises; it never reads as 'the source has nothing'."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        ingest.reset()

    def tearDown(self):
        ingest.reset()
        self.tmp.cleanup()

    def write(self, name, body):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body)
        return path

    def test_nhats(self):
        good = _common.read_json(config.NHATS_JSON)
        cases = {
            "empty": "",
            "cut short": json.dumps(good)[:5000],
            "no data": json.dumps({"signature": good["signature"], "count": "0"}),
            "empty data": json.dumps({"data": [], "count": "0"}),
            "count mismatch": json.dumps({"data": good["data"][:10], "count": "7231"}),
            "row without delta-v": json.dumps({"data": [{"des": "2010 PS66"}], "count": "1"}),
        }
        for name, body in cases.items():
            with self.subTest(name):
                with self.assertRaises(IngestError):
                    nhats.parse(self.write(f"nhats-{name}.json", body))
        self.assertRaises(IngestError, nhats.parse, self.dir / "missing.json")

    def test_nhats_damage_reaches_load(self):
        with mock.patch.object(config, "NHATS_JSON", self.write("nhats.json", "")):
            ingest.reset()
            with self.assertRaises(IngestError):
                nhats.load()

    def test_sbdb(self):
        good = _common.read_json(config.SBDB_JSON)
        cases = {
            "empty": "",
            "cut short": json.dumps({"fields": good["fields"], "data": good["data"][:3]})[:-40],
            "no rows": json.dumps({"fields": good["fields"], "data": [], "count": 0}),
            "field missing": json.dumps({"fields": [f for f in good["fields"] if f != "rot_per"],
                                         "data": [[c for f, c in zip(good["fields"], good["data"][0]) if f != "rot_per"]]}),
            "ragged row": json.dumps({"fields": good["fields"], "data": [good["data"][0][:-1]]}),
        }
        for name, body in cases.items():
            with self.subTest(name):
                with self.assertRaises(IngestError):
                    sbdb.parse(self.write(f"sbdb-{name}.json", body))

    def test_pravec(self):
        good = config.PRAVEC_TXT.read_bytes()
        lines = good.split(b"\n")
        cases = {
            "empty": b"",
            "blank": b"\n\n   \n",
            "header only": lines[0] + b"\n",
            "header changed": lines[0].replace(b"Period[h]", b"Period[d]") + b"\n" + b"\n".join(lines[1:50]),
            "column added": lines[0].replace(b"Ampl.", b"Ampl. Flag") + b"\n" + b"\n".join(lines[1:50]),
            "no header": b"\n".join(lines[1:50]),
            "bad period": lines[0] + b"\n" + lines[2][:30] + b"   2.57x6" + lines[2][39:] + b"\n",
            "row cut short": lines[0] + b"\n" + lines[2][:120] + b"\n",
        }
        for name, body in cases.items():
            with self.subTest(name):
                with self.assertRaises(IngestError):
                    pravec.parse(self.write(f"pravec-{name}.txt", body))

    def test_lcdb(self):
        good = (config.LCDB_DIR / "x" / lcdb.SUMMARY).read_bytes()
        lines = good.split(b"\n")
        head = b"\n".join(lines[:5]) + b"\n"
        cases = {
            "empty": b"",
            "no header": b"\n".join(lines[5:40]),
            "no date": b"\n".join(lines[2:40]),
            "header only": head,
            "columns moved": head.replace(b"PERIOD   ", b"   PERIOD") + b"\n".join(lines[5:40]),
            "row cut short": head + lines[5][:150] + b"\n",
            "bad grade": head + lines[5][:187] + b"9x" + lines[5][189:] + b"\n",
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.write(f"lcdb-{name}/x/{lcdb.SUMMARY}", body)
                with self.assertRaises(IngestError):
                    lcdb.parse(self.dir / f"lcdb-{name}")
        (self.dir / "lcdb-nothing").mkdir()
        self.assertRaises(IngestError, lcdb.parse, self.dir / "lcdb-nothing")
        self.write("lcdb-badzip/LCLIST_PUB_CURRENT.zip", b"not a zip")
        self.assertRaises(IngestError, lcdb.parse, self.dir / "lcdb-badzip")

    def test_lcdb_reads_the_zip_when_nothing_is_extracted(self):
        good = (config.LCDB_DIR / "x" / lcdb.SUMMARY).read_bytes()
        folder = self.dir / "lcdb-zip"
        folder.mkdir()
        with zipfile.ZipFile(folder / "LCLIST_PUB_CURRENT.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(lcdb.SUMMARY, b"\n".join(good.split(b"\n")[:205]) + b"\n")
        edition, rows = lcdb.parse(folder)
        self.assertEqual(edition, "2023-10-01")
        self.assertEqual(len(rows), 200)
        self.assertEqual((rows[0]["number"], rows[0]["name"], rows[0]["period_h"], rows[0]["u"]),
                         (1, "Ceres", 9.07417, "3"))

    def test_spitzer(self):
        good = config.SPITZER_CSV.read_text()
        lines = good.split("\n")
        cases = {
            "empty": "",
            "header only": lines[0] + "\n",
            "column missing": "\n".join(x.split(",", 1)[1] for x in lines[:20] if x),
            "ragged row": lines[0] + "\n" + lines[1] + ",extra\n",
            "bad diameter": lines[0] + "\n" + lines[1].replace(",2.025,", ",big,") + "\n",
        }
        for name, body in cases.items():
            with self.subTest(name):
                with self.assertRaises(IngestError):
                    spitzer.parse(self.write(f"spitzer-{name}.csv", body))

    def test_damage_never_becomes_absent_coverage(self):
        """Each reader, pointed at an empty file through config, raises from load()."""
        empty = self.write("empty.txt", "")
        hollow = self.dir / "hollow"
        (hollow / "x").mkdir(parents=True)
        shutil.copy(empty, hollow / "x" / lcdb.SUMMARY)
        for attr, value, module in (("PRAVEC_TXT", empty, pravec), ("SPITZER_CSV", empty, spitzer),
                                    ("LCDB_DIR", hollow, lcdb)):
            with self.subTest(attr):
                with mock.patch.object(config, attr, value):
                    ingest.reset()
                    with self.assertRaises(IngestError):
                        module.load()
        ingest.reset()


if __name__ == "__main__":
    unittest.main()
