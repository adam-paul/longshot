"""The export: build/records.jsonl and the field file, manifest and keys file of docs/mvp.md section 5.

Run: uv run python -m unittest tests.test_export

Hand-made records go through the whole model and out to a temporary folder.
Set LONGSHOT_FULL=1 to also run every object in build/ledger.jsonl twice and
compare the bytes (about a minute and a half).
"""
from __future__ import annotations

import copy
import dataclasses
import hashlib
import importlib.util
import json
import math
import os
import re
import struct
import tempfile
import time
import unittest
from pathlib import Path

from longshot import config, export, method, model
from tests.test_model import diameter, fact, make, period

M = method.load()
SIZES = {"f32": 4, "u8": 1, "u16": 2, "i32": 4, "u32": 4}
CODES = {"f32": "f", "u8": "B", "u16": "H", "i32": "i", "u32": "I"}
FORBIDDEN = ("mean", "median", "expected")
# The columns the app reads. The nine others docs/mvp.md section 5 first listed were never read (45% of the file).
USED = ("dv", "size_q50", "size_q05", "size_q95", "period_s", "state", "p_surface", "p_capture",
        "status_surface", "status_capture", "pct_surface", "pct_capture", "named", "seed")
DROPPED = ("h", "occ", "findable", "win_start", "win_end", "win_mag", "pointable", "metal_p_nothing", "metal_usd_q75")


def contract_columns():
    """(name, type) for every column in the table of docs/mvp.md section 5, in order."""
    text = (config.ROOT / "docs" / "mvp.md").read_text(encoding="utf-8")
    section = text.split("## 5. The field file")[1].split("\n## ")[0]
    out = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[1] in SIZES:
            out += [(name, cells[1]) for name in re.findall(r"`([a-z0-9_]+)`", cells[0])]
    return out


def read_by_hand(data_dir: Path):
    """A reader that shares nothing with export.py: little-endian, n values per column, at the listed offset."""
    manifest = json.loads((data_dir / "field.json").read_text(encoding="utf-8"))
    blob = (data_dir / manifest["file"]).read_bytes()
    cols = {}
    for c in manifest["columns"]:
        fmt = "<" + CODES[c["type"]]
        size = SIZES[c["type"]]
        cols[c["name"]] = [struct.unpack_from(fmt, blob, c["offset"] + i * size)[0] for i in range(manifest["n"])]
    keys = json.loads((data_dir / manifest["keys_file"]).read_text(encoding="utf-8"))
    return manifest, cols, keys, blob


def f32(v):
    return struct.unpack("<f", struct.pack("<f", v))[0]


def all_keys(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from all_keys(v)
    elif isinstance(x, list):
        for v in x:
            yield from all_keys(v)


def sample():
    """Hand-made records covering the cases the field must encode."""
    return [
        # unmeasured, with a window: untested for both missions
        make("m3", h=27.9, occ=2, dv=4.2, window=("2027-03-01", "2027-03-20", 21.2, "pointable")),
        # a JPL size and a JPL period that the row rests on: known pass for surface work
        make("a1", h=20.05, occ=0, dv=6.291, designation="2008 EV5", number=341843, aliases=["341843"],
             size=[diameter(400.0, 350.0, 450.0, "jpl-sbdb")],
             spin=[period(3.725, "lcdb", "3"), period(3.725, "jpl-sbdb", None)],
             surface=[fact("class", "C", "ssodnet")]),
        # a size from a single-value source, no JPL diameter; period only in Pravec's table
        make("b2", h=22.7, occ=1, size=[diameter(60.0, 50.0, 70.0, "ssodnet")], spin=[period(5.5, "pravec", "3")],
             window=("2030-05-01", "2030-05-09", 23.6, "survey only"), name="Sample"),
        # a size from a single-value source and JPL's own, different one
        make("c4", h=21.0, occ=0, size=[diameter(150.0, 140.0, 160.0, "ssodnet"), diameter(170.0, 150.0, 190.0, "jpl-sbdb")]),
        # JPL's period on file but graded unreliable elsewhere: the row is not measured
        make("d5", h=22.9, occ=0, spin=[period(10.0, "pravec", "1"), period(10.0, "jpl-sbdb", None)], spin_state="prior"),
        # the row rests on a period JPL contradicts
        make("e6", h=25.9, occ=2, spin=[period(0.1784, "pravec", "3"), period(0.089193, "jpl-sbdb", None)]),
        # JPL's period agrees with the adopted one, but another source in use does not: the entry does not turn it
        conflicted("g8"),
        # bad orbit, not checked, no window
        make("f7", h=24.5, occ=8, window=None, unchecked={"size": ["ssodnet"], "spin": ["ssodnet"], "surface": ["ssodnet"]}),
        # no H: cannot be placed
        make("z9", h=None, occ=9, arc=1, window=None),
    ]


def conflicted(key):
    r = make(key, h=21.9, occ=0, spin=[period(250.0, "pravec", "3"), period(250.0, "jpl-sbdb", None),
                                       period(2.02, "ssodnet", "2")])
    r.rows["spin"].conflicts = ["250 h (Pravec's table, U 3; JPL's database) against 2.02 h (SsODNet, U 2)."]
    return r


def build(tmp: str, records=None):
    records = model.run(copy.deepcopy(records if records is not None else sample()), M)
    assets = export.write(records, Path(tmp) / "build", Path(tmp) / "dist")
    return records, assets


class Export(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.records, cls.assets = build(cls.tmp.name)
        cls.data = Path(cls.tmp.name) / "dist" / "data"
        cls.manifest, cls.cols, cls.keys, cls.blob = read_by_hand(cls.data)
        cls.row = {k[0]: i for i, k in enumerate(cls.keys)}
        cls.by = {r.key: r for r in cls.records}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def col(self, name, key):
        return self.cols[name][self.row[key]]

    # ---- records.jsonl

    def test_records_file_is_one_record_per_line_sorted_by_key(self):
        path = Path(self.assets["records"])
        self.assertEqual(path, Path(self.tmp.name) / "build" / "records.jsonl")
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), len(self.records))
        keys = [json.loads(line)["key"] for line in lines]
        self.assertEqual(keys, sorted(keys))
        first = json.loads(lines[0])
        self.assertEqual(list(first), ["key", "designation", "name", "number", "aliases", "populations", "data_date",
                                       "method", "rows", "summary", "missions", "observe", "value", "ladder", "sources",
                                       "gone"])
        self.assertEqual(len(first["ladder"]), 5)

    def test_records_read_back_equal(self):
        back = export.read_records(self.assets["records"])
        self.assertEqual(back, sorted(self.records, key=lambda r: r.key))

    def test_no_key_named_mean_median_or_expected(self):
        seen = set()
        for line in Path(self.assets["records"]).read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            seen.update(all_keys(record))
            self.assertNotIn("q50", set(all_keys(record["value"])))        # no middle figure of dollars, kg or tonnes
        self.assertIn("usd", seen)
        for k in seen:
            self.assertFalse(any(word in k.lower() for word in FORBIDDEN), k)
        self.assertFalse(any(word in k.lower() for word in FORBIDDEN for k in all_keys(self.manifest)))

    def test_no_nan_or_infinity_is_written(self):
        text = Path(self.assets["records"]).read_text(encoding="utf-8")
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)

    # ---- the field file

    def test_asset_urls(self):
        self.assertEqual(self.assets["field_manifest"], "data/field.json")
        self.assertEqual(self.assets["field"], "data/" + self.manifest["file"])
        self.assertEqual(self.assets["keys"], "data/" + self.manifest["keys_file"])
        for name in (self.manifest["file"], self.manifest["keys_file"]):
            self.assertTrue((self.data / name).exists())

    def test_manifest_follows_the_contract(self):
        m = self.manifest
        self.assertEqual(list(m), ["schema", "data_date", "method", "n", "file", "columns", "keys_file", "counts",
                                   "unplaced"])
        self.assertEqual((m["schema"], m["data_date"], m["method"]), (1, config.DATA_DATE, config.METHOD))
        listed = [(c["name"], c["type"]) for c in m["columns"]]
        self.assertEqual(listed, list(export.COLUMNS))
        self.assertEqual([name for name, _ in listed], list(USED))
        # each is a column of the contract's table, with its type, and in the table's order
        self.assertEqual(listed, contract_columns())
        for c in m["columns"]:
            self.assertEqual(set(c), {"name", "type", "offset"})

    def test_only_the_columns_the_app_reads_are_shipped(self):
        """The review: nine unread columns were 45% of the file, and one was a bare dollar figure per asteroid."""
        names = {c["name"] for c in self.manifest["columns"]}
        self.assertEqual(names & set(DROPPED), set())
        self.assertFalse(any("usd" in n or "metal" in n for n in names))
        for script in ("app.js", "field.js"):
            text = (config.ROOT / "longshot" / "site" / "static" / script).read_text(encoding="utf-8")
            for name in DROPPED:
                self.assertIsNone(re.search(rf"(?:cols\.|['\"]){name}\b", text), f"{script} reads {name}")
        n = self.manifest["n"]
        self.assertEqual(len(self.blob), n * (5 * 4 + 8 * 1) + (-n * 8 % 4) + n * 2)

    def test_objects_that_are_not_drawn_are_listed_for_search(self):
        # a keys-file row, then the delta-v: the table view lists it
        self.assertEqual(self.manifest["unplaced"], [["z9", "2099 Z9", None, None, 5.0]])
        self.assertEqual(self.manifest["counts"]["not_placed"], len(self.manifest["unplaced"]))

    def test_file_names_carry_the_hash_of_their_bytes(self):
        self.assertEqual(self.manifest["file"], f"field.{hashlib.sha256(self.blob).hexdigest()[:12]}.bin")
        keys_bytes = (self.data / self.manifest["keys_file"]).read_bytes()
        self.assertEqual(self.manifest["keys_file"], f"keys.{hashlib.sha256(keys_bytes).hexdigest()[:12]}.json")

    def test_columns_run_one_after_another(self):
        n, end = self.manifest["n"], 0
        for c in self.manifest["columns"]:
            self.assertGreaterEqual(c["offset"], end, c["name"])
            self.assertLess(c["offset"] - end, 4, c["name"])                # at most padding to a 4-byte boundary
            self.assertEqual(c["offset"] % 4, 0, c["name"])
            end = c["offset"] + n * SIZES[c["type"]]
        self.assertEqual(end, len(self.blob))

    def test_round_trip_through_the_reader(self):
        manifest, cols, keys = export.read_field(self.data / "field.json")
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(keys, self.keys)
        self.assertEqual(cols, self.cols)                                   # export's reader and the one above agree
        self.assertEqual(len(keys), manifest["n"])
        # and what was written is what the records hold
        ordered = [r for r in sorted(self.records, key=lambda r: r.key) if r.summary]
        self.assertEqual([k[0] for k in keys], [r.key for r in ordered])
        for i, r in enumerate(ordered):
            row = export.field_row(r)
            for name, kind in export.COLUMNS:
                want = f32(row[name]) if kind == "f32" else row[name]
                self.assertEqual(cols[name][i], want, f"{r.key} {name}")

    def test_the_synthetic_writers_checker_accepts_it(self):
        spec = importlib.util.spec_from_file_location("synth", config.ROOT / "tools" / "make_synthetic_field.py")
        synth = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(synth)
        self.assertEqual(tuple(synth.COLUMNS), export.COLUMNS)
        self.assertEqual(synth.check(self.data / "field.json"), [])

    def test_keys_file(self):
        self.assertEqual(self.keys[self.row["a1"]], ["a1", "2008 EV5", None, 341843])
        self.assertEqual(self.keys[self.row["b2"]][2], "Sample")
        self.assertEqual([k[0] for k in self.keys], sorted(k[0] for k in self.keys))

    def test_an_object_with_no_h_is_left_out_and_counted(self):
        self.assertNotIn("z9", self.row)
        counts = self.manifest["counts"]
        self.assertEqual((counts["objects"], counts["placed"], counts["not_placed"]), (9, 8, 1))
        self.assertEqual(self.manifest["n"], 8)
        self.assertEqual(sum(counts["size_state"]), 8)
        self.assertEqual(sum(counts["rows"]["size"].values()), 9)
        self.assertEqual(sum(counts["missions"]["surface"].values()), 9)

    def test_plain_columns(self):
        self.assertEqual(self.col("dv", "a1"), f32(6.291))
        self.assertEqual(self.col("seed", "a1"), int.from_bytes(hashlib.sha256(b"a1").digest()[:2], "little"))
        self.assertNotEqual(self.col("seed", "a1"), self.col("seed", "b2"))

    def test_state_bits(self):
        code = {"unchecked": 0, "prior": 1, "limit": 2, "measured": 3}
        for key in self.row:
            rows = self.by[key].rows
            want = sum(code[rows[name].state] << (2 * i) for i, name in enumerate(("size", "spin", "surface", "push")))
            self.assertEqual(self.col("state", key), want, key)
        self.assertEqual(self.col("state", "a1"), 3 | 3 << 2 | 3 << 4 | 1 << 6)
        self.assertEqual(self.col("state", "f7"), 0 | 0 << 2 | 0 << 4 | 1 << 6)

    def test_period_is_the_one_the_row_rests_on(self):
        self.assertEqual(self.col("period_s", "a1"), f32(3.725 * 3600))     # the lightcurve database's, which JPL repeats
        self.assertEqual(self.col("period_s", "b2"), f32(5.5 * 3600))       # Pravec's table alone
        self.assertEqual(self.col("period_s", "e6"), f32(0.1784 * 3600))    # the first in use, whoever gives it
        self.assertEqual(self.col("period_s", "d5"), 0.0)                   # graded unreliable: not measured
        self.assertEqual(self.col("period_s", "m3"), 0.0)
        # sources in use disagree: the entry says "not turning", so the field does not turn it either
        self.assertEqual(self.col("period_s", "g8"), 0.0)
        # a body that no longer exists does not turn
        self.assertGreater(export.period_s(self.by["a1"]), 0.0)
        gone = dataclasses.replace(self.by["a1"], gone={"date": "2099-01-01", "text": "It hit.", "evidence": "x"})
        self.assertEqual(export.period_s(gone), 0.0)
        self.assertEqual(self.manifest["counts"]["with_period"], 3)

    def test_sizes_are_the_records_own_and_a_measured_one_is_plotted_at_its_value(self):
        for key in self.row:
            own = self.by[key].summary["size_m"]
            self.assertEqual([self.col(c, key) for c in ("size_q05", "size_q95")], [f32(own["q05"]), f32(own["q95"])], key)
            measured = export.measured_m(self.by[key])
            self.assertEqual(self.col("size_q50", key), f32(measured if measured is not None else own["q50"]), key)
            self.assertTrue(0 < self.col("size_q05", key) <= self.col("size_q50", key) <= self.col("size_q95", key))
        # an SsODNet diameter with no JPL one is in the field like any other
        self.assertEqual(self.col("state", "b2") & 3, 3)
        self.assertAlmostEqual(self.col("size_q50", "b2"), 60.0, delta=0.5)

    def test_mission_columns(self):
        status = {"fail": 0, "untested": 1, "pass": 2}
        for key in self.row:
            for mission in ("surface", "capture"):
                mi = self.by[key].missions[mission]
                p = self.col(f"p_{mission}", key)
                self.assertEqual(self.col(f"status_{mission}", key), status[mi["status"]], key)
                if mi["status"] == "pass":
                    self.assertEqual(p, 255)
                elif mi["status"] == "fail":
                    self.assertEqual(p, 0)
                else:
                    self.assertTrue(1 <= p <= 254, key)                     # untested never reads as decided
                    self.assertAlmostEqual(p / 255, mi["p"], delta=0.5 / 255 + 1 / 255)
        self.assertEqual((self.col("status_surface", "a1"), self.col("p_surface", "a1")), (2, 255))
        self.assertEqual(self.col("status_capture", "m3"), 1)

    # ---- determinism

    def test_two_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as other:
            build(other)
            for rel in ("build/records.jsonl", "dist/data/field.json",
                        f"dist/data/{self.manifest['file']}", f"dist/data/{self.manifest['keys_file']}"):
                a = (Path(self.tmp.name) / rel).read_bytes()
                b = (Path(other) / rel).read_bytes()
                self.assertEqual(a, b, rel)
            self.assertEqual(sorted(p.name for p in (Path(other) / "dist" / "data").iterdir()),
                             sorted(p.name for p in self.data.iterdir()))

    def test_input_order_does_not_change_the_bytes(self):
        with tempfile.TemporaryDirectory() as other:
            build(other, list(reversed(sample())))
            self.assertEqual((Path(other) / "build" / "records.jsonl").read_bytes(),
                             Path(self.assets["records"]).read_bytes())
            self.assertEqual((Path(other) / "dist" / "data" / "field.json").read_bytes(),
                             (self.data / "field.json").read_bytes())

    def test_a_rebuild_leaves_no_stale_field_file(self):
        with tempfile.TemporaryDirectory() as other:
            build(other)
            data = Path(other) / "dist" / "data"
            build(other, sample()[:3])
            names = sorted(p.name for p in data.iterdir())
            self.assertEqual(len(names), 3)
            manifest = json.loads((data / "field.json").read_text())
            self.assertEqual(set(names), {"field.json", manifest["file"], manifest["keys_file"]})
            self.assertEqual(manifest["n"], 3)

    def test_records_that_disagree_on_the_data_date_are_refused(self):
        records = model.run(copy.deepcopy(sample()[:2]), M)
        records[1].data_date = "2026-11-21"
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(ValueError):
                export.write_field(records, Path(other))


class TableAndReadout(unittest.TestCase):
    """What the instrument design's table view and readout read: the chance as printed, the name flag, the
    readout's lists, the period an entry shows, the observation's names."""

    setUpClass = Export.__dict__["setUpClass"]
    tearDownClass = Export.__dict__["tearDownClass"]
    col = Export.col

    def test_pct_is_the_percentage_the_entry_prints(self):
        def printed(p):                    # longshot/site/templates.py chance(), as the entry prints it
            return "under 1%" if p < 0.005 else "over 99%" if p >= 0.995 else f"{math.floor(p * 100 + 0.5 + 1e-9)}%"
        for key in self.row:
            for mission in ("surface", "capture"):
                mi = self.by[key].missions[mission]
                pct = self.col(f"pct_{mission}", key)
                if mi["status"] == "pass":
                    self.assertEqual(pct, 100)
                elif mi["status"] == "fail":
                    self.assertEqual(pct, 0)
                else:
                    want = printed(mi["p"])
                    self.assertEqual({0: "under 1%", 100: "over 99%"}.get(pct, f"{pct}%"), want, (key, mission))
        # where 1/255 steps round the other way: 0.135 is 34/255, which reads 13%; the entry prints 14%
        self.assertEqual(export._pct_byte({"status": "untested", "p": 0.135}), 14)
        self.assertEqual(round(100 * export._p_byte({"status": "untested", "p": 0.135}) / 255), 13)
        self.assertEqual(export._pct_byte({"status": "untested", "p": 0.004}), 0)
        self.assertEqual(export._pct_byte({"status": "untested", "p": 0.995}), 100)
        self.assertEqual(export._pct_byte({"status": "untested", "p": 0.005}), 1)

    def test_named(self):
        self.assertEqual(self.col("named", "b2"), 1)
        self.assertEqual(sum(self.cols["named"]), sum(1 for r in self.records if r.name and r.key in self.row))

    def test_named_list_is_by_delta_v(self):
        recs = model.run([make("n1", h=20.0, dv=7.0, name="Later"), make("n2", h=21.0, dv=4.0, name="Sooner"),
                          make("n3", h=21.0, dv=4.0, name="Tied"), make("n4", h=21.0, dv=3.5)], M)
        got = export.named(recs)
        self.assertEqual([x["key"] for x in got], ["n2", "n3", "n1"])
        self.assertEqual(got[0], {"key": "n2", "designation": "2099 N2", "name": "Sooner", "number": None, "dv": 4.0})

    def test_readout_holds_only_the_named_asteroids(self):
        # docs/design.md section 8: the readout lists the named asteroids; the "Typical, nothing measured" link is gone
        recs = model.run([make("n1", h=20.0, dv=7.0, name="Later"), make("t1", h=24.2, dv=4.6)], M)
        self.assertEqual(export.readout(recs, M), {"named": export.named(recs)})

    def test_the_period_an_entry_shows(self):
        # the period the row rests on, from whichever source gives it
        p = self.by["a1"].summary["period"]
        self.assertEqual((p["value"], p["source"], p["rests_on"], p["kind"]), (3.725, "lcdb", "lcdb", "value"))
        self.assertEqual(self.by["b2"].summary["period"]["source"], "pravec")
        self.assertIsNone(self.by["m3"].summary["period"])                     # not measured
        self.assertIsNone(self.by["d5"].summary["period"])                     # on file, graded unreliable
        self.assertTrue(self.by["g8"].summary["period"]["conflict"])
        # the lightcurve database alone: printed like any other
        alone = model.run_one(make("p1", h=22.0, spin=[period(6.0, "lcdb", "3")]), M).summary["period"]
        self.assertEqual((alone["value"], alone["source"], alone["rests_on"]), (6.0, "lcdb", "lcdb"))
        # a limit: the bound the row rests on
        bound = model.run_one(make("p3", h=22.0, spin=[period(2.0, "pravec", "2", kind="lower")]), M).summary["period"]
        self.assertEqual((bound["kind"], bound["value"]), ("lower", 2.0))
        self.assertEqual(self.by["a1"].summary["mass_basis"], "class")
        self.assertNotIn("period", self.by["z9"].summary)                       # no H: summary is {}

    def test_the_observation_carries_its_names(self):
        o = self.by["m3"].observe
        mission = M.missions[o["mission"]]
        self.assertEqual(o["mission_label"], mission["label"])
        self.assertEqual(o["label"], next(x["label"] for x in M.observe["observations"] if x["id"] == o["best"]))
        gate = next(g for g in self.by["m3"].missions[o["mission"]]["gates"] if g["id"] == o["gate"])
        self.assertEqual((o["gate_label"], o["gate_p"]), (gate["label"], gate["p"]))
        self.assertTrue(o["text"].startswith(o["label"]))


class DistGuard(unittest.TestCase):
    """A build deletes what it did not write under a/, list/, data/ and static/. It must not do that anywhere
    but in a site it built: `--dist .` from the repository root would remove data/, which is outside git."""

    def setUp(self):
        from longshot import __main__ as cli
        self.cli = cli

    def test_the_repository_root_and_the_data_folder_are_refused(self):
        for folder in (config.ROOT, config.DATA, config.DATA / "snapshots", config.ROOT.parent):
            with self.subTest(folder=str(folder)), self.assertRaises(self.cli.BuildError):
                self.cli.check_dist(Path(folder))

    def test_a_folder_that_holds_something_else_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "data").mkdir()
            (d / "data" / "research-data.tar.zst").write_bytes(b"x")
            (d / "notes.html").write_text("mine")
            with self.assertRaises(self.cli.BuildError) as caught:
                self.cli.check_dist(d)
            self.assertIn("not empty", str(caught.exception))
            self.assertTrue((d / "data" / "research-data.tar.zst").exists())
            # a marker that is not a manifest does not count
            (d / "data" / "field.json").write_text("[]")
            with self.assertRaises(self.cli.BuildError):
                self.cli.check_dist(d)

    def test_an_empty_or_new_folder_and_an_earlier_build_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.cli.check_dist(Path(tmp))                       # empty
            self.cli.check_dist(Path(tmp) / "not-made-yet")      # new
            build(tmp)                                            # writes dist/data/field.json
            (Path(tmp) / "dist" / "a").mkdir()
            (Path(tmp) / "dist" / "a" / "stale.html").write_text("old")
            self.cli.check_dist(Path(tmp) / "dist")              # a site this tool built


@unittest.skipUnless(os.environ.get("LONGSHOT_FULL") == "1" and (config.BUILD / "ledger.jsonl").exists(),
                     "set LONGSHOT_FULL=1 with build/ledger.jsonl on disk for the full run")
class FullRun(unittest.TestCase):
    def test_every_object_twice_same_bytes(self):
        out = []
        for _ in range(2):
            tmp = tempfile.TemporaryDirectory()
            self.addCleanup(tmp.cleanup)
            start = time.perf_counter()
            records = model.run(export.read_records(config.BUILD / "ledger.jsonl"), M)
            seconds = time.perf_counter() - start
            export.write(records, Path(tmp.name) / "build", Path(tmp.name) / "dist")
            out.append(tmp.name)
            self.assertLess(seconds, 180, "the model must stay under a few minutes")
        a, b = (Path(o) for o in out)
        names = sorted(p.name for p in (a / "dist" / "data").iterdir())
        self.assertEqual(names, sorted(p.name for p in (b / "dist" / "data").iterdir()))
        for name in names:
            self.assertEqual((a / "dist" / "data" / name).read_bytes(), (b / "dist" / "data" / name).read_bytes())
        self.assertEqual((a / "build" / "records.jsonl").read_bytes(), (b / "build" / "records.jsonl").read_bytes())
        spec = importlib.util.spec_from_file_location("synth", config.ROOT / "tools" / "make_synthetic_field.py")
        synth = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(synth)
        self.assertEqual(synth.check(a / "dist" / "data" / "field.json"), [])


if __name__ == "__main__":
    unittest.main()
