"""The field file: the synthetic writer, a pure-Python reader and docs/mvp.md section 5 agree."""
import hashlib
import importlib.util
import json
import re
import struct
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "longshot" / "site" / "static"

_spec = importlib.util.spec_from_file_location("make_synthetic_field", ROOT / "tools" / "make_synthetic_field.py")
synth = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(synth)

SIZES = {"f32": 4, "u8": 1, "u16": 2, "i32": 4, "u32": 4}


def contract_columns():
    """(name, type) for every column in the table of docs/mvp.md section 5, in order."""
    text = (ROOT / "docs" / "mvp.md").read_text()
    section = text.split("## 5. The field file")[1].split("\n## ")[0]
    out = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[1] in SIZES:
            out += [(name, cells[1]) for name in re.findall(r"`([a-z0-9_]+)`", cells[0])]
    return out


def f32(v):
    return struct.unpack("<f", struct.pack("<f", v))[0]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.seen = []

    def handle_starttag(self, tag, attrs):
        self.seen.append((tag, dict(attrs)))


class FieldFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.columns, cls.keys, cls.counts = synth.synthesize(500)
        cls.manifest = synth.write_field(cls.dir / "data", cls.columns, cls.keys, "2026-11-24", "synthetic", cls.counts)
        cls.path = cls.dir / "data" / "field.json"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_contract_table_is_parsed(self):
        cols = contract_columns()
        self.assertEqual(len(cols), 8)                                   # the columns whatever the mission types
        self.assertEqual(cols[0], ("dv", "f32"))
        self.assertEqual(cols[-1], ("seed", "u16"))

    def test_manifest_lists_every_contract_column_in_order(self):
        listed = [(c["name"], c["type"]) for c in self.manifest["columns"]]
        self.assertEqual(listed, list(synth.ALL))
        # the contract's columns, then three for each mission type (docs/mvp.md section 5)
        self.assertEqual(listed[:len(contract_columns())], contract_columns())
        self.assertEqual(listed[len(contract_columns()):], list(synth.mission_columns(synth.MISSIONS)))

    def test_manifest_fields(self):
        m = self.manifest
        self.assertEqual(list(m), ["schema", "data_date", "method", "n", "file", "columns", "keys_file", "counts", "unplaced"])
        self.assertEqual((m["unplaced"], m["counts"]["not_placed"]), ([], 0))
        self.assertEqual((m["schema"], m["n"], m["data_date"]), (1, 500, "2026-11-24"))
        for c in m["columns"]:
            self.assertEqual(set(c), {"name", "type", "offset"})

    def test_reader_returns_what_the_writer_was_given(self):
        manifest, cols, keys = synth.read_field(self.path)
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(keys, self.keys)
        self.assertEqual(set(cols), {name for name, _ in synth.ALL})
        for name, kind, values in self.columns:
            want = [f32(v) for v in values] if kind == "f32" else values
            self.assertEqual(cols[name], want, name)

    def test_reader_matches_raw_bytes(self):
        """The reader against the format read by hand: little-endian, n values, at the listed offset."""
        blob = (self.dir / "data" / self.manifest["file"]).read_bytes()
        cols = {name: values for name, _, values in self.columns}
        at = {c["name"]: c["offset"] for c in self.manifest["columns"]}
        self.assertEqual(blob[at["state"] + 7], cols["state"][7])
        self.assertEqual(int.from_bytes(blob[at["seed"] + 2 * 499:at["seed"] + 2 * 500], "little"), cols["seed"][499])
        self.assertEqual(struct.unpack_from("<f", blob, at["dv"] + 4 * 250)[0], f32(cols["dv"][250]))

    def test_offsets_and_sizes_fit_n(self):
        n, blob_len = self.manifest["n"], (self.dir / "data" / self.manifest["file"]).stat().st_size
        end = 0
        for c in self.manifest["columns"]:
            self.assertGreaterEqual(c["offset"], end, c["name"])           # in order, no overlap
            self.assertLess(c["offset"] - end, 4, c["name"])               # at most alignment padding between
            self.assertEqual(c["offset"] % 4, 0, c["name"])                # a typed-array view can sit on it
            end = c["offset"] + n * SIZES[c["type"]]
        self.assertEqual(end, blob_len)

    def test_unpadded_layout_is_columns_back_to_back(self):
        blob, listing = synth.pack_field(self.columns, align=1)
        n, offset = len(self.keys), 0
        for c in listing:
            self.assertEqual(c["offset"], offset, c["name"])
            offset += n * SIZES[c["type"]]
        self.assertEqual(len(blob), offset)
        self.assertEqual(offset, n * sum(SIZES[kind] for _, kind in synth.ALL))
        # With an odd n, a one-byte column first and one after seed, every wider column starts off its boundary
        # (seed too: seven one-byte columns come before it); the reader must not care.
        odd = sorted(((name, kind, values[:7]) for name, kind, values in self.columns),
                     key=lambda c: 0 if c[0] == "state" else 2 if c[0] == "named" else 1)
        with tempfile.TemporaryDirectory() as tmp:
            synth.write_field(tmp, odd, self.keys[:7], "2026-11-24", "synthetic", align=1)
            manifest, cols, _ = synth.read_field(Path(tmp) / "field.json")
            self.assertEqual(set(synth.unaligned(manifest)), {name for name, kind in synth.ALL if kind != "u8"})
            self.assertEqual(cols["seed"], dict((n, v) for n, _, v in odd)["seed"])
            self.assertEqual(synth.check(Path(tmp) / "field.json"), [])
        self.assertEqual(synth.unaligned(self.manifest), [])

    def test_file_names_carry_the_content_hash(self):
        data = self.dir / "data"
        blob = (data / self.manifest["file"]).read_bytes()
        keys = (data / self.manifest["keys_file"]).read_bytes()
        self.assertEqual(self.manifest["file"], f"field.{hashlib.sha256(blob).hexdigest()[:12]}.bin")
        self.assertEqual(self.manifest["keys_file"], f"keys.{hashlib.sha256(keys).hexdigest()[:12]}.json")

    def test_same_input_same_bytes(self):
        columns, keys, counts = synth.synthesize(500)
        with tempfile.TemporaryDirectory() as tmp:
            again = synth.write_field(tmp, columns, keys, "2026-11-24", "synthetic", counts)
            self.assertEqual(again, self.manifest)
            self.assertEqual((Path(tmp) / "field.json").read_bytes(), self.path.read_bytes())
        other, _, _ = synth.synthesize(501)
        self.assertNotEqual(other[0][2][:500], self.columns[0][2])

    def test_keys_file_rows(self):
        keys = json.loads((self.dir / "data" / self.manifest["keys_file"]).read_text())
        self.assertEqual(len(keys), self.manifest["n"])
        self.assertEqual(len({k[0] for k in keys}), len(keys))
        self.assertEqual(len({k[1] for k in keys}), len(keys))
        for key, designation, name, number in keys:
            self.assertRegex(key, r"^[a-z0-9]+$")
            self.assertTrue(designation)
            self.assertTrue(name is None or isinstance(name, str))
            self.assertTrue(number is None or isinstance(number, int))
        self.assertTrue(any(k[3] for k in keys))                                   # search by number has something to find
        # The first designation is the second's with a digit added: Enter on the second must not open the first.
        self.assertTrue(keys[0][1].startswith(keys[1][1]) and keys[0][1] != keys[1][1])

    def test_check_accepts_a_good_field_and_names_what_is_wrong_with_a_bad_one(self):
        self.assertEqual(synth.check(self.path), [])
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)

            def broken(change):
                synth.write_field(tmp, self.columns, self.keys, "2026-11-24", "synthetic")
                manifest = json.loads((tmp / "field.json").read_text())
                change(manifest)
                (tmp / "field.json").write_text(json.dumps(manifest))
                return " ".join(synth.check(tmp / "field.json"))

            self.assertIn("cannot read", broken(lambda m: m.update(n=m["n"] + 1)))
            self.assertIn("keys file has 500 rows", broken(lambda m: m.update(n=m["n"] - 1)))
            self.assertIn("column seed", broken(lambda m: m["columns"].remove(next(c for c in m["columns"] if c["name"] == "seed"))))
            self.assertIn("overlap", broken(lambda m: m["columns"][1].update(offset=m["columns"][0]["offset"] + 4)))
            self.assertIn("expected u8", broken(lambda m: m["columns"][6].update(type="f32")))
            self.assertIn("manifest lacks unplaced", broken(lambda m: m.pop("unplaced")))
            synth.write_field(tmp, self.columns, [k[:3] for k in self.keys], "2026-11-24", "synthetic")
            self.assertIn("a keys row is not [key, designation, name, number]", " ".join(synth.check(tmp / "field.json")))

            def truncate(m):
                f = tmp / m["file"]
                f.write_bytes(f.read_bytes()[:-1])
            self.assertIn("cannot read", broken(truncate))

            zero = [(n, k, [0.0] + list(v[1:]) if n == "size_q50" else v) for n, k, v in self.columns]
            synth.write_field(tmp, zero, self.keys, "2026-11-24", "synthetic")
            self.assertIn("size_q50 must be finite and above zero", " ".join(synth.check(tmp / "field.json")))

    def test_unplaced_rows_are_listed_and_counted(self):
        loose = synth.unplaced()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            manifest = synth.write_field(tmp, self.columns, self.keys, "2026-11-24", "synthetic", unplaced=loose)
            self.assertEqual((manifest["unplaced"], manifest["counts"]["not_placed"]), (loose, len(loose)))
            self.assertEqual(synth.check(tmp / "field.json"), [])
            synth.write_field(tmp, self.columns, self.keys, "2026-11-24", "synthetic", {"not_placed": 6}, unplaced=loose)
            self.assertIn("counts.not_placed is 6", " ".join(synth.check(tmp / "field.json")))
            synth.write_field(tmp, self.columns, self.keys, "2026-11-24", "synthetic", unplaced=[self.keys[0]])
            self.assertIn("keys are not unique", " ".join(synth.check(tmp / "field.json")))


class SyntheticField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        columns, cls.keys, cls.counts = synth.synthesize(7231)
        cls.cols = {name: values for name, _, values in columns}

    def test_ranges(self):
        c = self.cols
        self.assertTrue(all(3.3 <= v <= 12.0 for v in c["dv"]))
        self.assertTrue(all(0 < lo <= mid <= hi for lo, mid, hi in zip(c["size_q05"], c["size_q50"], c["size_q95"])))
        periods = [p for p in c["period_s"] if p]
        self.assertTrue(200 <= len(periods) <= 500, len(periods))
        self.assertTrue(all(60 <= p <= 50 * 3600 for p in periods))
        self.assertLess(min(periods), 600)
        self.assertGreater(max(periods), 20 * 3600)
        self.assertTrue(all(v in (0, 1, 2) for v in c["status_surface"] + c["status_capture"]))

    def test_state_is_two_bits_a_row_size_lowest(self):
        c = self.cols
        size = [s & 3 for s in c["state"]]
        spin = [s >> 2 & 3 for s in c["state"]]
        self.assertEqual([size.count(code) for code in range(4)], self.counts["size_state"])
        self.assertGreater(sum(code in (0, 1) for code in size), 0.9 * len(size))        # most are unchecked or a guess
        self.assertEqual({code for code in size}, {0, 1, 2, 3})                          # and every state is there to draw
        for period, code in zip(c["period_s"], spin):
            self.assertEqual(period > 0, code == 3)
        for status, p in zip(c["status_surface"], c["p_surface"]):
            self.assertEqual(p, {0: 0, 2: 255}.get(status, p))
        self.assertGreater(c["status_surface"].count(2), 0)
        self.assertGreater(c["status_capture"].count(2), 0)

    def test_seed_comes_from_the_key(self):
        for row, seed in list(zip(self.keys, self.cols["seed"]))[:50]:
            self.assertEqual(seed, int.from_bytes(hashlib.sha256(row[0].encode()).digest()[:2], "little"))
        self.assertGreater(len({s % 8 for s in self.cols["seed"]}), 7)                   # every outline shape gets used


class SyntheticSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name) / "site"
        cls.manifest = synth.write_site(cls.site, 300)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_index_follows_the_dom_contract(self):
        """The front page's DOM, as docs/mvp.md section 6 gives it to the generator and the app."""
        page = Tags()
        page.feed((self.site / "index.html").read_text())
        by_id = {a.get("id"): (tag, a) for tag, a in page.seen if a.get("id")}
        for ident, tag in (("controls", "form"), ("legend", "div"), ("plot", "figure"), ("field", "canvas"), ("axes", "div"),
                           ("tip", "div"), ("table", "section"), ("readout", "aside")):
            self.assertEqual(by_id[ident][0], tag, ident)
        self.assertIn("hidden", by_id["tip"][1])
        self.assertIn("hidden", by_id["table"][1])
        named = {}
        for tag, a in page.seen:
            if a.get("name"):
                named.setdefault((tag, a["name"]), []).append(a)
        self.assertEqual([a["value"] for a in named[("input", "view")]], ["chart", "table"])
        self.assertEqual([a["value"] for a in named[("input", "m")]], ["", "surface", "capture"])
        dv = named[("input", "dv")][0]
        self.assertEqual((dv["type"], dv["min"], dv["max"], dv["step"]), ("range", "3.3", "12", "0.1"))
        self.assertEqual(named[("input", "q")][0]["type"], "search")
        self.assertIn(("output", "dv-value"), named)
        for out in ("count", "zoom"):                                   # docs/design.md section 8: the count joins the legend line; no zoom factor
            self.assertNotIn(("output", out), named)
        zoom = [a for tag, a in page.seen if tag == "button" and a.get("name", "").startswith("zoom-")]
        self.assertEqual(len(zoom), 3)
        self.assertEqual(named[("meta", "field-manifest")][0]["content"], "data/field.json")
        self.assertTrue((self.site / "data" / "field.json").exists())

    def test_entry_pages_hold_main_entry(self):
        keys = json.loads((self.site / "data" / self.manifest["keys_file"]).read_text())
        pages = sorted(p.name for p in (self.site / "a").glob("*.html"))
        self.assertEqual(pages, sorted(f"{k[0]}.html" for k in keys[:2] + self.manifest["unplaced"]))
        self.assertEqual(self.manifest["counts"]["not_placed"], len(self.manifest["unplaced"]))
        for key, designation in (k[:2] for k in keys[:2] + self.manifest["unplaced"]):
            page = Tags()
            text = (self.site / "a" / f"{key}.html").read_text()
            page.feed(text)
            self.assertIn(("main", "entry"), [(tag, a.get("id")) for tag, a in page.seen])
            self.assertIn(("section", "summary"), [(tag, a.get("id")) for tag, a in page.seen])     # what the readout lifts
            self.assertIn(designation, text)

    def test_site_field_passes_the_check(self):
        self.assertEqual(synth.check(self.site / "data" / "field.json"), [])

    def test_scripts_are_copied_beside_the_page(self):
        for name in ("app.js", "field.js"):
            self.assertEqual((self.site / "static" / name).read_bytes(), (STATIC / name).read_bytes())


class Scripts(unittest.TestCase):
    """The app reads columns by name from the manifest; these catch a name the contract does not have."""

    def test_columns_the_scripts_ask_for_are_in_the_contract(self):
        # the contract's columns, and each mission type's three (here the made-up field's two types)
        names = {name for name, _ in contract_columns()} | {name for name, _ in synth.mission_columns(synth.MISSIONS)}
        app, field = (STATIC / "app.js").read_text(), (STATIC / "field.js").read_text()
        asked = set(re.findall(r"\bcols\.([a-z0-9_]+)", app + field)) - {"mask", "ly"}      # the app's own two
        asked |= set(re.findall(r"a_[a-z]+: '([a-z0-9_]+)'", field)) - {"mask", "ly", "status_", "p_"}
        asked |= {prefix + m for prefix in re.findall(r"'((?:status|p|pct)_)' \+", app + field) for m in ("surface", "capture")}
        self.assertTrue({"dv", "size_q50", "size_q05", "size_q95", "period_s", "state", "seed", "status_surface", "p_capture",
                         "pct_surface", "named"} <= asked, asked)
        self.assertEqual(asked - names, set())
        self.assertEqual(names - asked, set())                           # and the file carries no column nothing reads

    def test_marks_come_from_the_size_row_alone(self):
        """A rock with a measured spin and an estimated size is not drawn, or described, as measured."""
        app, field = (STATIC / "app.js").read_text(), (STATIC / "field.js").read_text()
        self.assertIn("uint size = a_state & 3u;                              // line style from the size row alone", field)
        self.assertNotRegex(field, r"max\(size, spin\)|\(a_state >> 2\)")
        self.assertNotRegex(app, r"Math\.max\(bits & 3, bits >> 2 & 3\)|cols\.state\[\w+\] >> 2")
        self.assertIn("const sizeState = r => cols.state[r] & 3;", app)
        # measured on the front page where the size row is measured or a bound, from whichever source gives it
        self.assertIn("const measured = r => sizeState(r) >= 2;", app)
        # the tip: a measured diameter is its value; a range is only ever an estimate's 90% range, and says so
        self.assertIn("const size = measured(i) ? `${metres(cols.size_q50[i])} ${unit('m')} ${k(sizeState(i) === 2 ? 'measured, a bound' : 'measured')}`", app)
        self.assertIn(": `${sig2(cols.size_q05[i])}–${sig2(cols.size_q95[i])} ${unit('m')} ${k('90% range, estimated')}`;", app)
        self.assertNotIn("90% range, measured", app)

    def test_two_states_on_the_surface(self):
        """docs/design.md section 3: the front page says measured or estimated, and a mission type's viability is
        Yes, No or a chance. A size not checked is an estimate there; it is never called "not measured"."""
        app = (STATIC / "app.js").read_text()
        words = re.findall(r"'([^'\n]*)'|`([^`]*)`", app)
        text = " ".join(a or b for a, b in words)
        for gone in ("Not measured", "not measured", "Not checked", "Limit only", "No size", "Untested", "Pass", "Fail",
                     "under 1%", "over 99%", "Delta-v", "Plotted", "Listed", "Size, ", "brighter if likelier"):
            self.assertNotIn(gone, text, gone)
        self.assertIn("const VIABILITY = 'Mission viability', YES = 'Yes', NO = 'No';", app)
        for gone in ("VERDICT", "Fits", "Ruled out", "unclear", "chance it fits"):      # docs/design.md section 3: viability
            self.assertNotIn(gone, text, gone)
        self.assertIn("const X_TITLE = 'Δv, cheapest round trip (km/s)', Y_TITLE = 'Diameter (m)';", app)
        self.assertNotIn("E.zoom", app)                                          # no zoom factor
        self.assertNotIn("E.count", app)                                         # the count is in the legend line

    def test_the_glow_is_in_the_shader_on_measured_outlines_only(self):
        """The owner: "keep the glow". A wider band of the same ribbon in the same draw; no blur, no framebuffer."""
        field = (STATIC / "field.js").read_text()
        self.assertIn("if (size == 3u) glow = true;", field)                                   # measured size, nothing else
        self.assertIn("if (u_o == 0 && a_mask == 0u) { b *= ${f(MARK.dim)}; glow = false; }", field)  # out of the filter: none
        self.assertEqual(len(re.findall(r"glow = true", field)), 1)
        self.assertNotRegex(field, r"createFramebuffer|createRenderbuffer|shadowBlur|blur\(")
        self.assertIn("gl.blendEquation(gl.MAX);", field)

    def test_brightness_has_one_meaning(self):
        """Three levels: full measured, half estimated, faint outside the filter. No chance in the shader."""
        field = (STATIC / "field.js").read_text()
        shader = field[field.index("const VS = `"):field.index("const FS = `")]
        self.assertNotRegex(shader, r"a_p\b|p_surface|p_capture")
        self.assertNotIn("a_p:", field)
        self.assertIn("half: 0xa8 / 255,", field)
        self.assertIn("dim: 0.16,", field)
        self.assertEqual(sorted(set(re.findall(r"\bb = ([^;,]+)[;,]", shader))), ["${f(MARK.half)}", "-1.", "1."])
        # viable: filled, never a heavier line (docs/design.md section 4: fill means viable, nothing else)
        self.assertIn("bool fill = fits && (u_o == 0 || u_o == 3);", shader)
        self.assertIn("if (fill && side > 0.) { q = vec2(0.); v_d = R * px * length(e.xy); }", shader)
        self.assertIn("v_s = vec4(b, fill ? duty + 2. : duty, hw, glow ? hg : 0.);", shader)   # a bound stays dashed
        self.assertNotIn("fitsLine", shader)

    def test_every_rock_in_one_instanced_draw(self):
        field = (STATIC / "field.js").read_text()
        self.assertEqual(len(re.findall(r"drawArraysInstanced\(gl\.TRIANGLE_STRIP, 0, 2 \* K \+ 2, this\.n\)", field)), 1)
        self.assertEqual(len(re.findall(r"drawArraysInstanced\(", field)), 2)                 # that one, and one rock at a time

    def test_picking_uses_the_shader_s_marks(self):
        """Field.mark() restates which mark the vertex shader draws; the two must change together."""
        field = (STATIC / "field.js").read_text()
        self.assertIn("return (c.state[i] & 3) >= 2 ? [1, MARK.rock * s] : this.zoomed || fits ? [1, MARK.out * s] : [0, MARK.dot * s];", field)
        self.assertIn("R *= u_k.w;", field)                     # the shader grows the marks by the same factor
        self.assertIn("if (zoomed || fits || u_o >= 2) { R = ${f(MARK.out)}; lw = ${f(MARK.outLine)}; }", field)
        self.assertIn("export const ZMAX = 32, ZOUT = 4;", field)                                # docs/design.md
        self.assertNotIn("class=\"scale\"", (STATIC / "app.js").read_text())     # glyphs are not to scale: no scale bar

    def test_no_offset_is_hard_coded(self):
        app = (STATIC / "app.js").read_text()
        self.assertIn("for (const { name, type, offset } of man.columns)", app)
        self.assertNotRegex(app + (STATIC / "field.js").read_text(), r"new (Float32|Uint8|Uint16|Int32|Uint32)Array\(buf, \d")

    def test_the_app_fetches_only_from_its_own_site(self):
        text = (STATIC / "app.js").read_text() + (STATIC / "field.js").read_text()
        self.assertNotRegex(text, r"https?://")
        self.assertNotRegex(text, r"\b(XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)\b")
        self.assertEqual(re.findall(r"(?<![.\w])import\s[^;]*;", text), ["import { Field, glContext, ZMAX, MARK } from './field.js';"])

    def test_the_app_computes_no_probability(self):
        """Chances are printed from the file's bytes: no arithmetic on p_* beyond reading it."""
        app = (STATIC / "app.js").read_text()
        self.assertEqual(re.findall(r"cols\['p_' \+ m\]\[r\][^;]*", app), ["cols['p_' + m][r] / 255 : NaN"])   # for sorting only
        self.assertIn("const pctText = p => p <= 0 ? '<1%' : p >= 100 ? '>99%' : p + '%';", app)
        self.assertIn("pctText(cols['pct_' + m][r])", app)
        # a condition's chance is its byte, printed as it is (export.py, gate columns)
        self.assertIn("const gateText = v => v === 255 ? YES : v === 254 ? NO : v === 253 ? '' : pctText(v);", app)


if __name__ == "__main__":
    unittest.main()
