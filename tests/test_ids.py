"""Object keys, the append-only registry and the alias resolver.

Run: uv run python -m unittest tests.test_ids
"""
import json
import tempfile
import unittest
from pathlib import Path

from longshot import config, ids
from longshot.ingest import _common
from tests.fixtures import FIXTURES

FIELDS = ["full_name", "pdes", "name", "prefix", "kind"]


def table(rows):
    return {"fields": FIELDS, "data": rows, "count": len(rows)}


BASE_ROWS = [
    ["       (2016 HO3)", "2016 HO3", None, None, "au"],
    [" 99942 Apophis (2004 MN4)", "99942", "Apophis", None, "an"],
    ["       (2011 AA37)", "2011 AA37", None, None, "au"],
    ["    1P/Halley", "1P", "Halley", "P", "cn"],
    ["     P/2021 Q5 (ATLAS)", "2021 Q5", "ATLAS", "P", "cu"],
    ["     C/2023 E1 (ATLAS)", "2023 E1", "ATLAS", "C", "cu"],
]


class RegistryCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.registry = self.dir / "registry" / "keys.jsonl"
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()
        _common._read_json_cached.cache_clear()

    def build(self, rows, registry=None, minted="2026-11-24"):
        self.n += 1
        path = self.dir / f"sbdb{self.n}.json"
        path.write_text(json.dumps(table(rows)))
        return ids.build_index(sbdb_path=path, registry_path=registry or self.registry, minted=minted)

    def test_keys_are_short_opaque_and_recorded(self):
        index = self.build(BASE_ROWS)
        lines = self.registry.read_text().splitlines()
        self.assertEqual(len(lines), len(BASE_ROWS))
        for line in lines:
            e = json.loads(line)
            self.assertEqual(sorted(e), ["designation", "key", "minted"])
            self.assertRegex(e["key"], r"^[a-z][a-z0-9]{5}$")
            self.assertEqual(e["minted"], "2026-11-24")
        self.assertEqual(len({json.loads(line)["key"] for line in lines}), len(lines))
        self.assertEqual(len(index), len(BASE_ROWS))

    def test_first_minting_is_in_designation_order_and_reproducible(self):
        self.build(BASE_ROWS)
        first = self.registry.read_bytes()
        designations = [json.loads(line)["designation"] for line in first.decode().splitlines()]
        self.assertEqual(designations, sorted(designations))
        other = self.dir / "other" / "keys.jsonl"
        self.build(list(reversed(BASE_ROWS)), registry=other)
        self.assertEqual(other.read_bytes(), first)

    def test_key_comes_from_the_line_position_not_the_designation(self):
        self.build(BASE_ROWS)
        for position, line in enumerate(self.registry.read_text().splitlines()):
            self.assertEqual(json.loads(line)["key"], ids.generate_key(position))
        renamed = [[r[0].replace("2011 AA37", "2011 AA38"), r[1].replace("2011 AA37", "2011 AA38")] + r[2:]
                   for r in BASE_ROWS]
        other = self.dir / "renamed" / "keys.jsonl"
        self.build(renamed, registry=other)
        self.assertEqual([json.loads(x)["key"] for x in other.read_text().splitlines()],
                         [json.loads(x)["key"] for x in self.registry.read_text().splitlines()])

    def test_second_run_mints_nothing_and_changes_no_byte(self):
        a = self.build(BASE_ROWS)
        before = self.registry.read_bytes()
        b = self.build(BASE_ROWS, minted="2027-01-01")
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertEqual(a.resolve("Apophis"), b.resolve("Apophis"))

    def test_new_object_is_appended_and_old_lines_are_untouched(self):
        self.build(BASE_ROWS)
        before = self.registry.read_bytes()
        self.build(BASE_ROWS + [["       (2001 AA1)", "2001 AA1", None, None, "au"]], minted="2026-12-01")
        after = self.registry.read_bytes()
        self.assertTrue(after.startswith(before))
        added = after[len(before):].decode().splitlines()
        self.assertEqual(len(added), 1)
        self.assertEqual(json.loads(added[0])["designation"], "2001 AA1")
        self.assertEqual(json.loads(added[0])["minted"], "2026-12-01")

    def test_an_object_that_gets_numbered_keeps_its_key(self):
        before_index = self.build(BASE_ROWS)
        key = before_index.resolve("2016 HO3")
        self.assertIsNotNone(key)
        before = self.registry.read_bytes()
        numbered = [["469219 Kamo`oalewa (2016 HO3)", "469219", "Kamo`oalewa", None, "an"]] + BASE_ROWS[1:]
        after_index = self.build(numbered)
        self.assertEqual(self.registry.read_bytes(), before)
        for spelling in ("469219", "2016 HO3", "Kamo'oalewa", "(469219) Kamoʻoalewa"):
            self.assertEqual(after_index.resolve(spelling), key, spelling)

    def test_a_line_that_was_removed_added_or_moved_stops_the_build(self):
        """A key is generated from its line's position. A lost line must not hand the object a new key."""
        self.build(BASE_ROWS)
        good = self.registry.read_text()
        lines = good.splitlines(keepends=True)
        self.assertGreaterEqual(len(lines), 3)
        keys_before = [json.loads(x)["key"] for x in lines]
        own = json.dumps({"key": "abcde1", "designation": "2099 QQ1", "minted": "2026-11-24"}) + "\n"
        cases = {
            "a line removed from the middle": "".join(lines[:1] + lines[2:]),
            "the first line removed": "".join(lines[1:]),
            "two lines swapped": "".join([lines[1], lines[0]] + lines[2:]),
            "a hand-made line added": good + own,
            "a hand-made line inserted": lines[0] + own + "".join(lines[1:]),
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.registry.write_text(body)
                with self.assertRaises(ids.RegistryError) as caught:
                    self.build(BASE_ROWS)
                self.assertIn("position", str(caught.exception))
                self.assertEqual(self.registry.read_text(), body, "a damaged registry must not be written to")
        # the last line removed is a registry that is one object short: the build appends it again, with the same key
        self.registry.write_text("".join(lines[:-1]))
        self.build(BASE_ROWS)
        self.assertEqual([json.loads(x)["key"] for x in self.registry.read_text().splitlines()], keys_before)

    def test_damaged_registry_stops_the_build(self):
        self.build(BASE_ROWS)
        good = self.registry.read_text()
        lines = good.splitlines()
        cases = {
            "not json": good + "{broken\n",
            "cut short": good[:-10],
            "repeated key": good + lines[0] + "\n",
            "wrong fields": good + json.dumps({"key": "zzzzz9", "designation": "X"}) + "\n",
            "malformed key": good + json.dumps({"key": "9abcde", "designation": "X", "minted": "2026-11-24"}) + "\n",
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.registry.write_text(body)
                with self.assertRaises(ids.RegistryError):
                    self.build(BASE_ROWS)
                self.assertEqual(self.registry.read_text(), body, "a damaged registry must not be written to")

    def test_damaged_table_stops_the_build(self):
        for name, body in {"empty": "", "not json": "{", "no rows": json.dumps(table([])),
                           "no fields": json.dumps({"data": [[1]]})}.items():
            with self.subTest(name):
                path = self.dir / f"bad-{name.replace(' ', '-')}.json"
                path.write_text(body)
                with self.assertRaises(_common.IngestError):
                    ids.build_index(sbdb_path=path, registry_path=self.dir / "r" / name / "keys.jsonl")

    def test_shared_names_resolve_to_nothing(self):
        index = self.build(BASE_ROWS)
        self.assertIsNone(index.resolve("ATLAS"))
        self.assertIsNotNone(index.resolve("P/2021 Q5"))
        self.assertNotEqual(index.resolve("P/2021 Q5"), index.resolve("C/2023 E1"))
        self.assertEqual(index.resolve("Halley"), index.resolve("1P/Halley"))


class SpellingCase(unittest.TestCase):
    """The resolver against JPL's real table."""

    @classmethod
    def setUpClass(cls):
        cls.index = ids.load()

    def test_every_fixture_spelling_resolves_to_one_object(self):
        for name, fx in FIXTURES.items():
            key = self.index.resolve(name)
            self.assertIsNotNone(key, name)
            for spelling in fx["spellings"]:
                self.assertEqual(self.index.resolve(spelling), key, f"{name}: {spelling!r}")
            ident = self.index.identity(key)
            self.assertEqual(ident.number, fx["number"], name)
            self.assertEqual(ident.name, fx["name"], name)
            self.assertEqual(ident.designation, fx["designation"], name)

    def test_apophis_spellings(self):
        key = self.index.resolve("99942")
        for spelling in ("(99942)", "(99942) Apophis", "99942 Apophis", "Apophis", "APOPHIS", "2004 MN4",
                         "2004MN4", "2004_MN4", "K04M04N", "99942 Apophis (2004 MN4)", 99942):
            self.assertEqual(self.index.resolve(spelling), key, repr(spelling))
        self.assertEqual(self.index.identity(key).pdes, "99942")

    def test_old_style_designation(self):
        self.assertEqual(self.index.resolve("A898 PA"), self.index.resolve("433"))
        self.assertEqual(self.index.resolve("1898 PA"), self.index.resolve("Eros"))

    def test_packed_forms(self):
        self.assertEqual(ids.unpack_designation("K11A37A"), "2011 AA37")
        self.assertEqual(ids.unpack_designation("J99A10O"), "1999 AO10")
        self.assertEqual(ids.unpack_designation("K09B00D"), "2009 BD")
        self.assertEqual(ids.unpack_designation("K10CQ6W"), "2010 CW266")
        self.assertEqual(ids.unpack_designation("PLS2040"), "2040 P-L")
        self.assertEqual(ids.unpack_number("k9219"), 469219)
        self.assertEqual(ids.unpack_number("A0345"), 100345)
        self.assertEqual(ids.unpack_number("~0000"), 620000)
        self.assertIsNone(ids.unpack_number("99942"))
        self.assertIsNone(ids.unpack_number("Bennu"))
        self.assertIsNone(ids.unpack_designation("Apophis"))
        self.assertEqual(self.index.resolve("K10CQ6W"), self.index.resolve("2010 CW266"))

    def test_unknown_spellings_resolve_to_nothing(self):
        for spelling in ("", "   ", None, "2011 AA38x", "9994 2", "not an asteroid", "20469219", "2011 AA",
                         "1862 AA37x", "0", "(0)", "99942 Apohpis", "Kamo", "2011", True):
            self.assertIsNone(self.index.resolve(spelling), repr(spelling))

    def test_contradictory_spellings_resolve_to_nothing(self):
        self.assertIsNone(self.index.resolve("(99942) Bennu"))
        self.assertIsNone(self.index.resolve("(101955) Apophis"))
        self.assertIsNone(self.index.resolve("(99942) 1999 RQ36"))
        self.assertIsNone(self.index.resolve("Bennu", number=99942))
        self.assertIsNone(self.index.resolve("2004 MN4", number=101955))
        self.assertIsNone(self.index.resolve("Apophis", number=123456789))

    def test_number_column(self):
        apophis = self.index.resolve("99942")
        self.assertEqual(self.index.resolve("Apophis", number=99942), apophis)
        self.assertEqual(self.index.resolve("2004 MN4", number="99942"), apophis)
        self.assertEqual(self.index.resolve(None, number=99942), apophis)
        self.assertEqual(self.index.resolve("2011 AA37", number=0), self.index.resolve("2011 AA37"))
        self.assertEqual(self.index.resolve("2011 AA37", number=""), self.index.resolve("2011 AA37"))

    def test_a_number_with_a_misspelt_name_is_accepted_only_in_brackets(self):
        self.assertEqual(self.index.resolve("(99942) Apohpis"), self.index.resolve("99942"))
        self.assertIsNone(self.index.resolve("99942 Apohpis"))

    def test_comet_names_shared_by_many_resolve_to_nothing(self):
        self.assertIsNone(self.index.resolve("LINEAR"))
        self.assertIsNotNone(self.index.resolve("1P/Halley"))


class RealRegistryCase(unittest.TestCase):
    """registry/keys.jsonl as committed."""

    @classmethod
    def setUpClass(cls):
        cls.index = ids.load()
        cls.entries = ids.read_registry()

    def test_one_key_per_object_in_jpls_table(self):
        n = len(_common.read_json(config.SBDB_JSON)["data"])
        self.assertGreaterEqual(len(self.entries), n)
        self.assertEqual(len(self.index), n)
        keys = [e["key"] for e in self.entries]
        self.assertEqual(len(set(keys)), len(keys))
        for k in keys:
            self.assertRegex(k, r"^[a-z][a-z0-9]{5}$")
        self.assertEqual(len({e["designation"] for e in self.entries}), len(self.entries))

    def test_loading_does_not_touch_the_registry(self):
        before = config.KEYS.read_bytes()
        ids.load.cache_clear()
        ids.load()
        self.assertEqual(config.KEYS.read_bytes(), before)

    def test_every_reachable_designation_has_a_key(self):
        for r in _common.read_json(config.NHATS_JSON)["data"]:
            self.assertIsNotNone(self.index.resolve(r["des"]), r["des"])
            self.assertEqual(self.index.resolve(r["des"]), self.index.resolve(r["fullname"]), r["fullname"])

    def test_no_two_objects_share_a_spelling(self):
        shared = [s for s, keys in self.index._exact.items() if len(keys) > 1]
        self.assertEqual(shared, [])


if __name__ == "__main__":
    unittest.main()
