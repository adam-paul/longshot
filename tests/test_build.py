"""The whole build, end to end: data on disk -> build/ and dist/, checked page by page.

Run: uv run python -m unittest tests.test_build

BuildCase builds every reachable asteroid twice into a temporary folder under
build/ (once in this process, once in another with a different hash seed, at the
same time) and takes about a minute. Both builds read the research snapshot's
SsODNet cards alone (tests.fixtures.research_cards_only), because the folder of
newly fetched cards can change while a test runs. No count of rows by state is
asserted: only the fixture objects and rules that hold for every page.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from longshot import __main__ as cli
from longshot import config, contract, ingest, model, shape
from longshot.site import templates as t
from tests.fixtures import FIXTURES, research_cards_only
from tests.test_model import diameter, make, period
from tests.test_site import Tree

STATIC = config.ROOT / "longshot" / "site" / "static"
ROW_RE = re.compile(r'<section class="row" id="row-\w+" data-row="(\w+)" data-state="(\w+)"[^>]*>(.*?)</section>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
FIGURE_RE = re.compile(r'<figure class="rockfig[^"]*">.*?</figure>', re.S)
NUM_RE = re.compile(r"([−-]?\d[\d,]*(?:\.\d+)?)(?: × 10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))?")
SUPERSCRIPT = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")
POINTER = "on file, not shown here"
# A sentence under the rows that calls a row "not measured". It must not appear when a source for that row was not checked.
SAYS_NOT_MEASURED = {
    "size": re.compile(r"no measured size|size (is )?not measured", re.I),
    "spin": re.compile(r"no measured (period|spin)|(spin|period) (is )?not measured", re.I),
    "surface": re.compile(r"no measured (class|reflectivity)|(class|reflectivity|surface) (is )?not measured", re.I),
}
SECOND_BUILD = """
import sys
from pathlib import Path
from tests.fixtures import research_cards_only
from longshot.__main__ import build
with research_cards_only():
    build(Path(sys.argv[1]) / "build", Path(sys.argv[1]) / "dist")
"""


def numbers(text: str) -> list[float]:
    """Every number printed in a piece of page text, powers of ten included."""
    out = []
    for mantissa, power in NUM_RE.findall(text):
        v = float(mantissa.replace("−", "-").replace(",", ""))
        out.append(v * 10.0 ** int(power.translate(SUPERSCRIPT)) if power else v)
    return out


def to_fact_unit(text: str) -> float:
    """The factor from the unit a page prints to the unit the ledger holds (m, h, a share)."""
    words = text.replace(" ", " ").split()
    if "%" in text:
        return 0.01
    if "km" in words:
        return 1000.0
    if "min" in words:
        return 1.0 / 60.0
    if "s" in words:
        return 1.0 / 3600.0
    return 1.0


def label_power(label: str) -> float:
    """The power of ten a label prints once for its column: 'Drift, A2, 10⁻¹³ au/d²' -> 1e-13; 1 if none."""
    m = re.search(r"10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)", label)
    return 10.0 ** int(m.group(1).translate(SUPERSCRIPT)) if m else 1.0


def near(a: float, b: float) -> bool:
    return abs(a - b) <= 6e-4 * max(abs(a), abs(b)) + 1e-300     # a page prints four figures


def tree_hashes(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def row_lines(section) -> tuple[list[dict], list[str], list[str]]:
    """A row's printed facts as [{label, source, v, r, g}], the sources it names as not checked, and its conflicts.

    Each facts table row is th label, td.v value, td.r range, td.q grade, td.s source; when one source covers the
    whole table its cells are empty and the line under the table (p.srcline) names it."""
    (body,) = section.find("div", cls="rb")
    lines, pending = [], []
    for kid in body.kids:
        if isinstance(kid, str):
            continue
        if kid.tag == "table" and "facts" in kid.classes:
            lines += pending
            pending = []
            for tr in kid.find("tr"):
                if "pr" in tr.classes:            # what is typical at this brightness, not a fact on file
                    continue
                (th,) = tr.find("th")
                cell = lambda cls: " ".join(n.text() for n in tr.find("td", cls=cls))
                links = [a.attrs["href"].removeprefix("#src-") for td in tr.find("td", cls="s") for a in td.find("a")]
                pending.append({"label": th.text(), "v": cell("v"), "r": cell("r"), "g": cell("q"),
                                "source": links[0] if links else None})
        elif kid.tag == "p" and "srcline" in kid.classes:
            link = kid.find("a")[0].attrs["href"].removeprefix("#src-")
            for line in pending:
                line["source"] = line["source"] or link
    lines += pending
    unchecked = [a.attrs["href"].removeprefix("#src-") for p in body.find("p", cls="un") for a in p.find("a")]
    conflicts = [p.text() for p in body.find("p", cls="conflict")]
    return lines, unchecked, conflicts


class BuildCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config.BUILD.mkdir(parents=True, exist_ok=True)
        cls.tmp = Path(tempfile.mkdtemp(prefix="test-build-", dir=config.BUILD))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        env = dict(os.environ, PYTHONHASHSEED="20261124")
        other = subprocess.Popen([sys.executable, "-c", SECOND_BUILD, str(cls.tmp / "two")], cwd=config.ROOT, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            with research_cards_only():
                cls.report = cli.build(cls.tmp / "one" / "build", cls.tmp / "one" / "dist")
        finally:
            cls.other_output, _ = other.communicate()
            cls.other_status = other.returncode
        cls.dist = cls.tmp / "one" / "dist"
        cls.records = {}
        with open(cls.tmp / "one" / "build" / "records.jsonl", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                cls.records[r["key"]] = r
        cls.by_designation = {r["designation"]: r for r in cls.records.values()}
        cls.manifest = json.loads((cls.dist / "data" / "field.json").read_text(encoding="utf-8"))
        cls.entries = sorted((cls.dist / "a").glob("*.html"))
        cls.pages = sorted(cls.dist.rglob("*.html"))

    def entry(self, designation: str):
        rec = self.by_designation[designation]
        tree = Tree()
        tree.feed((self.dist / "a" / f"{rec['key']}.html").read_text(encoding="utf-8"))
        self.assertEqual(tree.errors, [], designation)
        return rec, tree.root

    # ---- every reachable asteroid has a page

    def test_every_reachable_asteroid_has_a_page(self):
        listed = json.loads(config.NHATS_JSON.read_text(encoding="utf-8"))["data"]
        self.assertGreater(len(listed), 7000)
        self.assertEqual(len(self.records), len(listed))
        self.assertEqual({p.stem for p in self.entries}, set(self.records))
        self.assertEqual(self.report["entry_pages"], len(listed))
        # and it is that asteroid's page: its designation is in the heading or on the line under it
        names = {r["des"] for r in listed}
        for key in sorted(self.records)[::97]:
            rec = self.records[key]
            page = (self.dist / "a" / f"{key}.html").read_text(encoding="utf-8")
            head = page.split('<header class="ehead">')[1].split("</header>")[0]
            self.assertIn(rec["designation"], TAG_RE.sub(" ", head), key)
            self.assertIn(f'data-key="{key}"', page)
        self.assertEqual(len(names), len(listed))

    def test_the_site_is_whole(self):
        others = ("index.html", "list/observe.html", "record.html", "method.html")
        for name in others:
            self.assertTrue((self.dist / name).is_file(), name)
        self.assertEqual(self.report["pages"], len(self.pages))
        self.assertEqual(len(self.pages), len(self.entries) + len(others))
        # every local link and asset a page names is a file of this build
        for page in [self.dist / name for name in others] + self.entries[::499]:
            text = page.read_text(encoding="utf-8")
            for url in re.findall(r'(?:href|src)="([^"#]+)"', text):
                if re.match(r"[a-z]+:", url):
                    continue
                self.assertTrue((page.parent / url).resolve().is_file(), f"{page.name} names {url}")

    def test_static_files_carry_their_hash_and_the_app_finds_the_field_script(self):
        static = sorted(p.name for p in (self.dist / "static").iterdir() if p.is_file())
        self.assertEqual(len(static), 3, static)
        # the one font, not hashed, with its licence beside it: style.css names it as fonts/b612-regular.woff2
        self.assertEqual(sorted(p.name for p in (self.dist / "static" / "fonts").iterdir()), ["OFL.txt", "b612-regular.woff2"])
        self.assertEqual((self.dist / "static" / "fonts" / "b612-regular.woff2").read_bytes(),
                         (STATIC / "fonts" / "b612-regular.woff2").read_bytes())
        for name in static:
            stem, digest, _ = name.split(".")
            self.assertEqual(digest, hashlib.sha256((self.dist / "static" / name).read_bytes()).hexdigest()[:12], name)
        app = next(n for n in static if n.startswith("app."))
        field = next(n for n in static if n.startswith("field."))
        imports = re.findall(r"from '\./([^']+)'", (self.dist / "static" / app).read_text(encoding="utf-8"))
        self.assertEqual(imports, [field])
        self.assertEqual((self.dist / "static" / field).read_bytes(), (STATIC / "field.js").read_bytes())
        index = (self.dist / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'<script type="module" src="static/{app}"></script>', index)
        self.assertIn('<meta name="field-manifest" content="data/field.json">', index)

    # ---- the fixture objects

    def test_fixture_objects_show_their_values_on_their_pages(self):
        self.assertEqual(len(FIXTURES), 13)
        checked = 0
        for name, fx in FIXTURES.items():
            rec, root = self.entry(fx["designation"])
            (h1,) = root.find("h1")
            self.assertEqual(h1.text(), fx["name"] or fx["designation"], name)
            if fx["name"]:
                aka = root.find("dl", cls="ident")[0].text(gap=" ")
                self.assertIn(fx["designation"], aka)
                self.assertIn(str(fx["number"]), aka)
            sections = {s.attrs["data-row"]: s for s in root.find("section", cls="row")}
            self.assertEqual(list(sections), list(t.ROWS), name)
            for row_name, want in fx["rows"].items():
                where = f"{name} / {row_name}"
                section = sections[row_name]
                lines, unchecked, conflicts = row_lines(section)
                with self.subTest(where):
                    self.assertEqual(section.attrs["data-state"], want["state"], where)
                    self.assertEqual(section.find("div", cls="rh")[0].find("span", cls="st")[0].text(),
                                     t.STATE_WORDS[want["state"]], where)
                    self.assertEqual(unchecked, want["unchecked"], where)
                    for label in want.get("absent", []):
                        self.assertEqual([l for l in lines if printed_as(l, row_name, label)], [], f"{where}: {label}")
                    for fact in want["facts"]:
                        mine = [l for l in lines if printed_as(l, row_name, fact["label"]) and l["source"] == fact["source"]]
                        self.assertTrue(mine, f"{where}: no {fact['label']} line from {fact['source']}; have {lines}")
                        hit = self.matching(mine, fact)
                        self.assertIsNotNone(hit, f"{where}: {fact['label']} = {fact['value']} from {fact['source']} "
                                                  f"({fact['where']}) is not on the page; lines {mine}")
                        if hit["v"] == POINTER:
                            continue                      # held back by the licence rule: no figure to compare
                        if fact.get("quality"):
                            self.assertIn(html.unescape(t.unparen(t.grade(row_name, fact["quality"]))), hit["g"],
                                          f"{where}: {fact['label']} grade")
                        if "lo" in fact and "hi" in fact and hit["r"]:
                            k = to_fact_unit(hit["r"]) * label_power(hit["label"])
                            lo, hi = (v * k for v in numbers(hit["r"])[:2])
                            self.assertTrue(near(lo, fact["lo"]) and near(hi, fact["hi"]),
                                            f"{where}: {fact['label']} range {hit['r']!r}")
                        checked += 1
                    if "conflicts" in want:
                        self.assertEqual(bool(conflicts), bool(want["conflicts"]), where)
                        for parts in want["conflicts"]:
                            self.assertTrue(any(all(p in sentence for p in parts) for sentence in conflicts),
                                            f"{where}: {conflicts}")
        self.assertGreater(checked, 100)

    def matching(self, lines: list[dict], fact: dict) -> dict | None:
        value = fact["value"]
        for line in lines:
            if line["v"] == POINTER and fact["source"] == "lcdb":
                return line                               # the lightcurve database's values are pointers unless another source agrees
            if isinstance(value, str):
                if line["v"] == value:
                    return line
            else:
                got = numbers(line["v"])
                if got and near(got[0] * to_fact_unit(line["v"]) * label_power(line["label"]), float(value)):
                    return line
        return None

    def test_fixture_cases_read_as_intended(self):
        # 2011 AA37: the 10-hour period is on the page, graded unreliable, and the row is not measured; the rock does not turn
        rec, root = self.entry("2011 AA37")
        spin = next(s for s in root.find("section", cls="row") if s.attrs["data-row"] == "spin")
        self.assertIn("unreliable", spin.text())
        self.assertEqual(spin.attrs["data-state"], "prior")
        self.assertEqual(root.find("g", cls="turn"), [])
        self.assertIn("not turning", root.find("figure", cls="rockfig")[0].find("svg")[0].attrs["aria-label"])
        # 2009 BD: the computed albedo is listed, marked as not used, and the surface row is not measured
        rec, root = self.entry("2009 BD")
        surface = next(s for s in root.find("section", cls="row") if s.attrs["data-row"] == "surface")
        (unused,) = [tr for tr in surface.find("tr", cls="nu") if "computed" in tr.find("td", cls="q")[0].text()]
        self.assertIn("not used", unused.text(gap=" "))
        # 2026 QQ8: unknown to SsODNet, so four rows are not checked and say which source
        rec, root = self.entry("2026 QQ8")
        for s in root.find("section", cls="row"):
            if s.attrs["data-row"] in ("size", "spin", "surface"):
                self.assertEqual(s.find("div", cls="rh")[0].find("span", cls="st")[0].text(), "Not checked")
                (line,) = s.find("p", cls="un")
                self.assertTrue(line.text().startswith("Not checked: "), line.text())
                self.assertIn("SsODNet, unknown there, ", line.text())
                self.assertNotRegex(s.text(gap=" "), r"not measured|no measured")
        # 2010 CW266: no brightness, so no size, no rock, and no estimate of what is in it
        rec, root = self.entry("2010 CW266")
        (figure,) = root.find("figure", cls="rockfig")
        self.assertEqual(figure.find("svg"), [])
        self.assertIn("not drawn", figure.text())
        # Bennu: measured in every row, and its rock turns at the measured rate
        rec, root = self.entry("1999 RQ36")
        self.assertEqual({s.attrs["data-state"] for s in root.find("section", cls="row")}, {"measured"})
        (turning,) = root.find("g", cls="turn")
        seconds = float(turning.attrs["style"].removeprefix("animation-duration:").removesuffix("s"))
        self.assertAlmostEqual(seconds / 3600.0, 4.296, delta=0.01)

    # ---- rules that hold on every page

    def test_no_row_with_an_unchecked_source_says_not_measured(self):
        rows_seen = unchecked_rows = figures = 0
        for path in self.entries:
            text = path.read_text(encoding="utf-8")
            rec = self.records[path.stem]
            rows = ROW_RE.findall(text)
            self.assertEqual([name for name, _, _ in rows], list(t.ROWS), path.name)
            for name, state, body in rows:
                rows_seen += 1
                held = rec["rows"][name]
                self.assertEqual(state, held["state"], f"{path.name} {name}")
                names_unchecked = 'class="un"' in body
                self.assertEqual(names_unchecked, bool(held["unchecked"]), f"{path.name} {name}")
                if names_unchecked:
                    unchecked_rows += 1
                    self.assertNotEqual(state, "prior", f"{path.name} {name}")
                    self.assertNotRegex(TAG_RE.sub(" ", body), r"not measured|no measured", f"{path.name} {name}")
                    for source in held["unchecked"]:
                        self.assertIn(f'href="#src-{source}"', body.split('class="un"')[1], f"{path.name} {name}")
                if state == "unchecked":
                    self.assertTrue(names_unchecked, f"{path.name} {name}")
            # the figure above the rows (caption and the drawing's label) and the sentences under them
            # (ladder, value, observation, missions) follow the same rule
            figure = FIGURE_RE.search(text).group(0)
            figure = " ".join([TAG_RE.sub(" ", figure)] + re.findall(r'aria-label="([^"]*)"', figure))
            below = TAG_RE.sub(" ", text.split('<section class="sec" id="difficulty"', 1)[1])
            for name, pattern in SAYS_NOT_MEASURED.items():
                if rec["rows"][name]["unchecked"]:
                    for part in (figure, below):
                        found = pattern.search(part)
                        self.assertIsNone(found, f"{path.name}: {name} has an unchecked source, yet "
                                                 f"{part[max(0, found.start() - 60):found.end() + 20]!r}" if found else "")
                    figures += 1
        self.assertEqual(rows_seen, 6 * len(self.entries))
        self.assertGreater(unchecked_rows, 1000)        # the rule was exercised
        self.assertGreater(figures, 1000)

    def test_no_page_says_open_now_and_every_page_prints_the_data_date(self):
        stamp = f"Data <time>{config.DATA_DATE}</time>"          # in every page's header
        foot = f"as of <time>{config.DATA_DATE}</time>"          # and the footer, on every page but the front one
        for path in self.pages:
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, re.compile(r"open\s+now|opens?\s+today|currently\s+(open|visible|observable)", re.I),
                                path.name)
            self.assertIn(stamp, text, path.name)
            if path != self.dist / "index.html":
                self.assertIn(foot, text, path.name)
        self.assertEqual(self.manifest["data_date"], config.DATA_DATE)

    def test_windows_are_dated_facts(self):
        rec, root = self.entry("2011 AA37")
        tracking = next(s for s in root.find("section", cls="row") if s.attrs["data-row"] == "tracking")
        text = tracking.text(gap=" ")
        self.assertIn("2026-11-27", text)
        self.assertRegex(text, r"JPL NHATS\s*, as of 2026-11-24")
        observe = (self.dist / "list" / "observe.html").read_text(encoding="utf-8")
        self.assertIn(f"Data <time>{config.DATA_DATE}</time>", observe)    # the windows' date is the page's data date

    # ---- the field file and the pages agree

    def test_the_field_holds_every_asteroid_that_has_a_size(self):
        """docs/mvp.md section 5: n is the number of pages less the asteroids with no size to place them by."""
        keys = json.loads((self.dist / "data" / self.manifest["keys_file"]).read_text(encoding="utf-8"))
        counts = self.manifest["counts"]
        self.assertEqual(self.manifest["n"], len(keys))
        self.assertEqual(counts["objects"], len(self.entries))
        self.assertEqual(self.manifest["n"] + counts["not_placed"], len(self.entries))
        placed = {k[0] for k in keys}
        self.assertEqual(len(placed), len(keys))
        self.assertLessEqual(placed, set(self.records))
        left_out = set(self.records) - placed
        self.assertLess(len(left_out), 20)
        for key in left_out:                              # left out only for want of a brightness, and the page says so
            rec = self.records[key]
            self.assertFalse(contract_has_h(rec), rec["designation"])
            self.assertIn("No size on file: not drawn", (self.dist / "a" / f"{key}.html").read_text(encoding="utf-8"))
        for key, designation, name, number in keys[::211]:
            rec = self.records[key]
            self.assertEqual((designation, name, number), (rec["designation"], rec["name"], rec["number"]))
        # the asteroids with no rock are named in the manifest, so search finds them
        self.assertEqual({row[0] for row in self.manifest["unplaced"]}, left_out)
        self.assertEqual(counts["not_placed"], len(self.manifest["unplaced"]))
        field = self.dist / "data" / self.manifest["file"]
        self.assertEqual(self.report["field"]["bytes"], field.stat().st_size)
        self.assertEqual(self.manifest["file"], f"field.{hashlib.sha256(field.read_bytes()).hexdigest()[:12]}.bin")

    def test_the_entry_draws_the_rock_the_field_draws(self):
        rec, root = self.entry("2011 AA37")
        polygons = root.find("figure", cls="rockfig")[0].find("polygon")
        self.assertEqual(len(polygons), 3)                # the size range as nested outlines; no halo, as not measured
        (mid,) = [p for p in polygons if "mid" in p.classes]
        pts = [tuple(map(float, xy.split(","))) for xy in mid.attrs["points"].split()]
        want = shape.outline(rec["key"])
        scale = max(abs(c) for xy in pts for c in xy) / max(abs(c) for xy in want for c in xy)
        for (x, y), (wx, wy) in zip(pts, want, strict=True):
            self.assertAlmostEqual(x, wx * scale, delta=0.11)
            self.assertAlmostEqual(y, wy * scale, delta=0.11)

    # ---- determinism

    def test_two_builds_are_byte_identical(self):
        self.assertEqual(self.other_status, 0, self.other_output)
        one, two = tree_hashes(self.tmp / "one"), tree_hashes(self.tmp / "two")
        self.assertGreater(len(one), len(self.entries) + 10)
        self.assertEqual(sorted(one), sorted(two))
        differing = [name for name in one if one[name] != two[name]]
        self.assertEqual(differing, [])


def printed_as(line: dict, row_name: str, label: str) -> bool:
    """Whether a printed line is the ledger's `label`: the page's word for it, capitalised, and perhaps ", <unit>" after."""
    word = t.cap(t.label(row_name, label))
    return line["label"] == word or line["label"].startswith(word + ", ")


def contract_has_h(rec: dict) -> bool:
    return any(f["label"] == "H" and isinstance(f["value"], (int, float)) for f in rec["rows"]["size"]["facts"])


class ShapeCase(unittest.TestCase):
    def test_the_outline_tables_are_the_ones_in_field_js(self):
        js = (STATIC / "field.js").read_text(encoding="utf-8")
        table = lambda name: [float(v) for v in re.search(rf"const {name} = \[(.*?)\];", js, re.S).group(1).replace("\n", " ").split(",") if v.strip()]
        self.assertEqual(table("RADII"), list(shape.RADII))
        self.assertEqual(table("SQUASH"), list(shape.SQUASH))
        self.assertIn(f"const K = {shape.K}, SHAPES = {shape.SHAPES},", js)
        # the shader's rule, as shape.outline restates it
        self.assertIn(f"u_t[int(a_seed % ${{SHAPES}}u) * K + i % K]", js)
        self.assertIn("if ((a_seed & 8u) != 0u) e.xz = -e.xz;", js)
        self.assertIn("float((a_seed >> 8) & 255u) / 256.", js)

    def test_outline(self):
        pts = shape.outline("abc123")
        self.assertEqual(pts, shape.outline("abc123"))
        self.assertEqual(len(pts), shape.K)
        self.assertEqual(shape.seed("abc123"), int.from_bytes(hashlib.sha256(b"abc123").digest()[:4], "little"))
        for x, y in pts:
            self.assertLessEqual((x * x + y * y) ** 0.5, 1.0 + 1e-9)


class ContractCase(unittest.TestCase):
    """contract.check: what the site is built from is checked, not assumed."""

    SOURCES = set(ingest.SOURCE_IDS)

    def good(self, **kw):
        return model.run_one(make(key="abc123", h=24.0, **kw))

    def broken(self, change, **kw) -> str:
        r = copy.deepcopy(self.good(**kw))
        change(r)
        with self.assertRaises(contract.ContractError) as caught:
            contract.check([r], self.SOURCES)
        return str(caught.exception)

    def test_a_filled_record_passes(self):
        contract.check([self.good()], self.SOURCES)
        contract.check([self.good(size=[diameter(40.0, 30.0, 50.0)], spin=[period(3.0)])], self.SOURCES)
        contract.check([model.run_one(make(key="abc124", h=None))], self.SOURCES)      # no brightness: summary and value empty

    def test_a_missing_field_is_an_error(self):
        self.assertIn("summary.size_m", self.broken(lambda r: r.summary.pop("size_m")))
        self.assertIn("summary.mass_t", self.broken(lambda r: r.summary["mass_t"].pop("q95")))
        self.assertIn("value.metal", self.broken(lambda r: r.value["metal"].pop("p_nothing")))
        self.assertIn("value.statements", self.broken(lambda r: r.value.update(statements=[])))
        self.assertIn("ladder", self.broken(lambda r: r.ladder.pop()))
        self.assertIn("lacks ['text']", self.broken(lambda r: r.missions["surface"]["gates"][0].pop("text")))
        self.assertIn("missions", self.broken(lambda r: r.missions.pop("capture")))
        self.assertIn("no prior", self.broken(lambda r: setattr(r.rows["size"], "prior", None)))
        self.assertIn("observe lacks ['window']", self.broken(lambda r: r.observe.pop("window")))
        self.assertIn("observe.tier is 'soon'", self.broken(lambda r: r.observe.update(tier="soon")))
        self.assertIn("observe.unchecked names 'somewhere'", self.broken(lambda r: r.observe.update(unchecked=["somewhere"])))
        self.assertIn("no delta-v", self.broken(lambda r: r.rows["reach"].facts.clear()))
        self.assertIn("rows are", self.broken(lambda r: r.rows.pop("push")))

    def test_the_states_keep_their_meaning(self):
        said = self.broken(lambda r: (setattr(r.rows["spin"], "state", "prior"), r.rows["spin"].unchecked.append("ssodnet")))
        self.assertIn("'not measured' while ['ssodnet'] is not checked", said)
        self.assertIn("names no source", self.broken(lambda r: setattr(r.rows["spin"], "state", "unchecked")))
        self.assertIn("measured with no fact", self.broken(lambda r: setattr(r.rows["push"], "state", "measured")))
        self.assertIn("is not a source", self.broken(lambda r: setattr(r.rows["reach"].facts[0], "source", "somewhere")))

    def test_no_central_dollar_figure_gets_through(self):
        self.assertIn("central figure", self.broken(lambda r: r.value["metal"]["usd"].update(q50=1.0)))
        self.assertIn("central figure", self.broken(lambda r: r.value["metal"].update(mean=1.0)))

    def test_keys_and_dates(self):
        self.assertIn("used twice", self.twice())
        self.assertIn("not a minted key", self.broken(lambda r: setattr(r, "key", "../x")))
        self.assertIn("data_date", self.broken(lambda r: setattr(r, "data_date", "2026-11-21")))

    def twice(self) -> str:
        with self.assertRaises(contract.ContractError) as caught:
            contract.check([self.good(), self.good()], self.SOURCES)
        return str(caught.exception)

    def test_predictions(self):
        good = {"id": "p1", "statement": "s", "p": 0.5, "frozen": None, "settles": "x", "settle_from": None,
                "settle_by": None, "settle_note": "no date set", "key": None, "designation": None, "outcome": None}
        contract.check_predictions([good])
        for change in ({"p": 1.5}, {"statement": ""}):
            with self.assertRaises(contract.ContractError):
                contract.check_predictions([{**good, **change}])
        with self.assertRaises(contract.ContractError):
            contract.check_predictions([good, good])
        with self.assertRaises(contract.ContractError):
            contract.check_predictions([{k: v for k, v in good.items() if k != "settles"}])


class StaticCase(unittest.TestCase):
    def test_hashed_names_and_the_rewritten_import(self):
        with tempfile.TemporaryDirectory() as d:
            assets = cli.write_static(Path(d))
            self.assertEqual(set(assets), {"style", "app", "field"})
            for url in assets.values():
                self.assertRegex(url, r"^static/[a-z]+\.[0-9a-f]{12}\.(css|js)$")
                self.assertTrue((Path(d) / url).is_file())
            app = (Path(d) / assets["app"]).read_text(encoding="utf-8")
            self.assertIn(f"from './{assets['field'].removeprefix('static/')}';", app)
            self.assertNotIn("'./field.js'", app)
            self.assertEqual(assets, cli.write_static(Path(d)))          # same bytes, same names

    def test_serve_needs_a_built_site_and_only_hashed_files_are_kept_by_the_browser(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(io.StringIO()) as said:
            self.assertEqual(cli.serve(Path(d), port=0), 1)
            self.assertIn("python -m longshot build", said.getvalue())
        forever = "public, max-age=31536000, immutable"
        self.assertEqual(cli.cache_control("/static/app.0123456789ab.js"), forever)
        self.assertEqual(cli.cache_control("/data/field.0123456789ab.bin"), forever)
        for path in ("/data/field.json", "/index.html", "/", "/a/abc123.html", "/list/observe.html?x=1", "/static/app.js"):
            self.assertEqual(cli.cache_control(path), "no-cache", path)

    def test_the_command_line(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            cli.main([])
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            cli.main(["publish"])

    def test_prune_removes_only_what_a_build_owns(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for name in ("index.html", "old.html", "a/gone.html", "a/kept.html", "data/field.old.bin", "notes/mine.txt", "README"):
                (d / name).parent.mkdir(parents=True, exist_ok=True)
                (d / name).write_text("x")
            removed = cli.prune(d, {d / "index.html", d / "a" / "kept.html"})
            self.assertEqual(removed, 3)
            self.assertEqual(sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()),
                             ["README", "a/kept.html", "index.html", "notes/mine.txt"])


if __name__ == "__main__":
    unittest.main()
