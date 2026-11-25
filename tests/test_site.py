"""The site generator, run on the hand-made sample records.

    uv run python -m unittest tests.test_site
"""
from __future__ import annotations

import dataclasses
import math
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
import types
from unittest import mock

from longshot import export, method, observe, predictions
from longshot.site import gen, templates as t
from longshot.types import ROWS
from tests import sample_records as sample

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
CSS = (Path(gen.__file__).parent / "static" / "style.css").read_text(encoding="utf-8")
SUMMARY_LABELS = ["Size", "Spin", "Made of", "Mass", "Reach", "Surface work", "Whole-body capture", "Would settle most"]
SUMMARY_GROUPS = ["Missions"]       # headings in the summary list: one row, a single cell


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.kids = tag, dict(attrs), parent, []

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def walk(self):
        yield self
        for k in self.kids:
            if isinstance(k, Node):
                yield from k.walk()

    def find(self, tag=None, cls=None, **attrs):
        return [n for n in self.walk()
                if (tag is None or n.tag == tag) and (cls is None or cls in n.classes)
                and all(n.attrs.get(k.replace("_", "-")) == v for k, v in attrs.items())]

    def text(self, skip=lambda n: False, gap=""):
        """The text inside, with `gap` between neighbouring pieces and skipped subtrees left out."""
        out = []
        for k in self.kids:
            if isinstance(k, str):
                out.append(k.replace("\u00a0", " "))          # a no-break space reads as a space
            elif skip(k):
                out.append(" ")
            else:
                out.append(k.text(skip, gap))
        return gap.join(out)


class Tree(HTMLParser):
    """Builds a tree and records every tag that closes out of turn or never closes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.at = self.root
        self.errors = []

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.at)
        self.at.kids.append(node)
        if tag not in VOID:
            self.at = node

    def handle_startendtag(self, tag, attrs):
        self.at.kids.append(Node(tag, attrs, self.at))

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f"</{tag}> closes a void element")
        elif self.at.tag != tag:
            self.errors.append(f"</{tag}> at {self.getpos()} while <{self.at.tag}> is open")
        else:
            self.at = self.at.parent

    def handle_data(self, data):
        self.at.kids.append(data)

    def close(self):
        super().close()
        if self.at is not self.root:
            self.errors.append(f"<{self.at.tag}> never closed")


def parse(text: str) -> Tree:
    tree = Tree()
    tree.feed(text)
    tree.close()
    return tree


UNIT = r"(?:km/s|au/d²|au/Myr|kg/m³|m²/kg|km|min|mag|kg|m|h|s|d|t)(?![A-Za-z])"

# What a figure must not say of a row while a source for that row was not checked (docs/mvp.md section 8).
SAYS_NOT_MEASURED = {
    "size": re.compile(r"no measured size|size (is )?not measured", re.I),
    "spin": re.compile(r"no measured (period|spin)|(spin|period) (is )?not measured", re.I),
}


def everything_in(n: Node) -> str:
    """A node's text and every attribute value under it: what a reader, or a screen reader, is given."""
    return " ".join([n.text(gap=" ")] + [str(v) for x in n.walk() for v in x.attrs.values() if v])


def srcs():
    return {k: dataclasses.asdict(s) for k, s in sample.SOURCES.items()}


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.written = gen.write_site(sample.RECORDS, sample.SOURCES, cls.out, sample.ASSETS, sample.PREDICTIONS)
        cls.pages = {p.relative_to(cls.out).as_posix(): p.read_text(encoding="utf-8")
                     for p in cls.written if p.suffix == ".html"}
        cls.trees = {name: parse(text) for name, text in cls.pages.items()}
        cls.by_key = {r.key: r for r in sample.RECORDS}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def entry(self, key) -> Node:
        (main,) = self.trees[f"a/{key}.html"].root.find("main", id="entry")
        return main

    def rows(self, key) -> dict[str, Node]:
        return {n.attrs["data-row"]: n for n in self.entry(key).find("section", cls="row")}

    def summary(self, key) -> dict[str, tuple[Node, Node, Node]]:
        """{label: (value cell, detail cell, state cell)} of an entry's summary list."""
        (table,) = self.entry(key).find("table", cls="sumlist")
        return {tr.find("th")[0].text(): tuple(tr.find("td")) for tr in table.find("tr") if "grp" not in tr.classes}

    # ---- the set of pages

    def test_pages(self):
        want = {"index.html", "list/observe.html", "record.html", "method.html"}
        want |= {f"a/{r.key}.html" for r in sample.RECORDS}
        self.assertEqual(set(self.pages), want)
        # the missions are a filter on the field and its table view, not pages
        self.assertFalse(any(name.startswith("list/") and "observe" not in name for name in self.pages))
        fonts = sorted(p.relative_to(self.out).as_posix() for p in self.written if p.suffix != ".html")
        self.assertEqual(fonts, ["static/fonts/OFL.txt", "static/fonts/b612-regular.woff2"])
        self.assertEqual(len(self.written), len(want) + 2)

    def test_the_font_is_one_file_with_its_licence(self):
        font = self.out / "static/fonts/b612-regular.woff2"
        self.assertEqual(font.read_bytes(), (gen.FONTS / "b612-regular.woff2").read_bytes())
        self.assertEqual(font.read_bytes()[:4], b"wOF2")
        self.assertLess(font.stat().st_size, 16_000)
        self.assertIn("SIL Open Font License", (self.out / "static/fonts/OFL.txt").read_text(encoding="utf-8"))
        # every page asks for it early, beside the stylesheet that names it
        for name, tree in self.trees.items():
            (pre,) = tree.root.find("link", rel="preload", **{"as": "font"})
            depth = name.count("/")
            self.assertEqual(pre.attrs["href"], "../" * depth + "static/fonts/b612-regular.woff2", name)
            self.assertEqual((pre.attrs["type"], "crossorigin" in pre.attrs), ("font/woff2", True), name)
        # a build that places the font itself says so, and the generator leaves it alone
        with tempfile.TemporaryDirectory() as d:
            written = gen.write_site(sample.RECORDS, sample.SOURCES, d, dict(sample.ASSETS, font="static/f.woff2"))
            self.assertFalse(any(p.suffix == ".woff2" for p in written))
            self.assertIn('href="static/f.woff2"', (Path(d) / "index.html").read_text(encoding="utf-8"))

    def test_well_formed(self):
        for name, tree in self.trees.items():
            self.assertEqual(tree.errors, [], name)
            self.assertTrue(self.pages[name].startswith("<!doctype html>"), name)
            self.assertEqual(len(tree.root.find("title")), 1, name)
            ids = [n.attrs["id"] for n in tree.root.walk() if "id" in n.attrs]
            self.assertEqual(len(ids), len(set(ids)), f"{name}: an id is used twice")
            # a browser asks for /favicon.ico unless the page names an icon
            self.assertEqual([l.attrs["href"] for l in tree.root.find("link", rel="icon")], ["data:,"], name)

    def test_parser_catches_imbalance(self):
        self.assertTrue(parse("<div><p>x</div>").errors)
        self.assertTrue(parse("<div><span>x</span>").errors)
        self.assertEqual(parse('<div><br><svg><polygon points="0,0"/></svg></div>').errors, [])

    def test_byte_identical_across_runs(self):
        with tempfile.TemporaryDirectory() as again:
            written = gen.write_site(sample.RECORDS, sample.SOURCES, Path(again), sample.ASSETS, sample.PREDICTIONS)
            self.assertEqual([p.relative_to(again) for p in written],
                             [p.relative_to(self.out) for p in self.written])
            for p in written:
                self.assertEqual(p.read_bytes(), (self.out / p.relative_to(again)).read_bytes(), p.name)

    def test_record_order_does_not_change_pages(self):
        with tempfile.TemporaryDirectory() as again:
            gen.write_site(sample.RECORDS[::-1], sample.SOURCES, Path(again), sample.ASSETS, sample.PREDICTIONS)
            for name, text in self.pages.items():
                self.assertEqual((Path(again) / name).read_text(encoding="utf-8"), text, name)

    def test_plain_dicts_give_the_same_pages(self):
        with tempfile.TemporaryDirectory() as again:
            gen.write_site([dataclasses.asdict(r) for r in sample.RECORDS],
                           {k: dataclasses.asdict(s) for k, s in sample.SOURCES.items()},
                           Path(again), sample.ASSETS, sample.PREDICTIONS)
            for name, text in self.pages.items():
                self.assertEqual((Path(again) / name).read_text(encoding="utf-8"), text, name)

    def test_every_page_prints_the_data_date(self):
        for name, tree in self.trees.items():
            (body,) = tree.root.find("body")
            self.assertIn(sample.DATA_DATE, body.text(), name)
            (head,) = tree.root.find("header", cls="site")
            self.assertIn(f"Data {sample.DATA_DATE}", head.find("p", cls="date")[0].text(), name)

    def test_no_page_says_open_now(self):
        for name, text in self.pages.items():
            self.assertNotIn("open now", text.lower(), name)

    def test_prototype_is_said_once(self):
        for name, tree in self.trees.items():
            (body,) = tree.root.find("body")
            self.assertEqual(body.text().count("prototype"), 1, name)

    def test_unsafe_or_repeated_keys_are_refused(self):
        for key in ("../x", "a b", ""):
            bad = dataclasses.replace(sample.RECORDS[0], key=key)
            with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
                gen.write_site([bad], sample.SOURCES, d, sample.ASSETS)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            gen.write_site([sample.RECORDS[0], sample.RECORDS[0]], sample.SOURCES, d, sample.ASSETS)

    # ---- the header: each destination once

    def test_header(self):
        for name, tree in self.trees.items():
            (head,) = tree.root.find("header", cls="site")
            (mark,) = head.find("a", cls="mark")
            self.assertEqual(mark.text(), t.SITE)
            self.assertEqual(len(mark.find("svg", cls="rockmark")), 1)
            self.assertEqual(head.find("span", cls="proto")[0].text(), "prototype")
            for nav in head.find("nav"):
                self.assertEqual([a.text() for a in nav.find("a")], ["Field", "Observe next", "Record", "Method"], name)
        current = {name: [a.text() for a in tree.root.find("header")[0].find("a", aria_current="page")]
                   for name, tree in self.trees.items()}
        self.assertEqual(current["index.html"], ["Field", "Field"])            # the bar and the phone's menu
        self.assertEqual(current["list/observe.html"], ["Observe next"] * 2)
        self.assertEqual(current["a/s0000001.html"], [])

    def test_mission_names_are_never_links(self):
        """The two missions are a filter on the field, not pages: no mission name is a link anywhere."""
        for name, tree in self.trees.items():
            for a in tree.root.find("a"):
                self.assertNotIn(a.text().strip().lower(), [m.lower() for m in t.MISSION_LABELS.values()], name)
                self.assertNotRegex(a.attrs.get("href", ""), r"list/(surface|capture)", name)

    # ---- the front page and its contract with the field app

    def test_index_contract(self):
        root = self.trees["index.html"].root
        (form,) = root.find("form", id="controls")
        radios = lambda name: [i.attrs["value"] for i in form.find("input", name=name)]
        self.assertEqual(radios("view"), ["chart", "table"])
        self.assertEqual(radios("m"), ["", "surface", "capture"])
        self.assertIn("checked", form.find("input", name="view", value="chart")[0].attrs)
        self.assertIn("checked", form.find("input", name="m", value="")[0].attrs)
        self.assertEqual([s.text() for s in form.find("span") if s.parent.tag == "label"],
                         ["Chart", "Table", "Any", "Surface work", "Whole-body capture"])
        (dv,) = form.find("input", name="dv")
        # the slider spans the data's own delta-v, to a tenth: nothing typed into the generator
        dvs = [t.delta_v(dataclasses.asdict(r)) for r in sample.RECORDS]
        lo, hi = math.floor(min(v for v in dvs if v is not None) * 10) / 10, math.ceil(max(v for v in dvs if v is not None) * 10) / 10
        self.assertEqual({k: dv.attrs[k] for k in ("type", "min", "max", "step", "value")},
                         {"type": "range", "min": f"{lo:g}", "max": f"{hi:g}", "step": "0.1", "value": f"{hi:g}"})
        self.assertEqual(form.find("output", name="dv-value")[0].text(), f"{hi:.1f} km/s")
        (q,) = form.find("input", name="q")
        self.assertEqual(q.attrs["type"], "search")
        self.assertEqual(form.find("label", **{"for": q.attrs["id"]})[0].text(), "Find asteroid")
        drawn = sum(1 for r in sample.RECORDS if t.placed(dataclasses.asdict(r)))
        self.assertEqual(drawn, len(sample.RECORDS) - 1)                     # F has no brightness, so no rock
        self.assertEqual(form.find("span", id="count-label")[0].text(), "Plotted")
        self.assertEqual(form.find("output", name="count")[0].text(), f"{drawn} of {len(sample.RECORDS)}")
        # the legend, the zoom group and the figure
        self.assertEqual(len(root.find("div", id="legend")), 1)
        (zoom,) = root.find("div", cls="zoom")
        self.assertEqual([b.attrs["name"] for b in zoom.find("button")], ["zoom-out", "zoom-in", "zoom-reset"])
        self.assertTrue(all(b.attrs["form"] == "controls" for b in zoom.find("button")))
        self.assertEqual(zoom.find("output", name="zoom")[0].attrs["form"], "controls")
        (plot,) = root.find("figure", id="plot")
        self.assertEqual(len(plot.find("canvas", id="field")), 1)
        self.assertEqual(len(plot.find("div", id="axes")), 1)
        self.assertIn("hidden", plot.find("div", id="tip")[0].attrs)
        (table,) = root.find("section", id="table")
        self.assertIn("hidden", table.attrs)
        self.assertEqual(len(table.find("table")), 1)
        (readout,) = root.find("aside", id="readout")
        self.assertEqual(readout.find("div", cls="overview")[0].parent, readout)
        (script,) = root.find("script", type="module")
        self.assertEqual(script.attrs["src"], sample.ASSETS["app"])
        (link,) = root.find("link", rel="stylesheet")
        self.assertEqual(link.attrs["href"], sample.ASSETS["style"])
        (meta,) = root.find("meta", name="field-manifest")
        self.assertEqual(meta.attrs["content"], sample.ASSETS["field_manifest"])
        # Enter in the search box must not reload the page while the app is still loading
        self.assertEqual(form.attrs["onsubmit"], "return false")

    def test_no_headline_sentence(self):
        """The owner: 'Do you commonly see websites with full sentences as headers like this?' The front page's
        words are labels, names, counts and units."""
        root = self.trees["index.html"].root
        (h1,) = root.find("h1")
        self.assertIn("vh", h1.classes)                       # for screen readers, not drawn
        text = root.find("main")[0].text(gap=" ")
        for said in ("within reach of a spacecraft", "nothing on file says", "Select a point", "asteroids are"):
            self.assertNotIn(said, text)
        for h in root.find("h2"):
            self.assertLessEqual(len(h.text().split()), 3, h.text())
        self.assertNotIn(".", "".join(h.text() for h in root.find("h2")))

    def test_legend_counts_the_rocks_drawn(self):
        legend = self.trees["index.html"].root.find("div", id="legend")[0]
        counts = {li.text().replace(li.find("span", cls="n")[0].text(), "").strip(): int(li.find("span", cls="n")[0].text())
                  for li in legend.find("li") if li.find("span", cls="n")}
        drawn = [r for r in sample.RECORDS if t.placed(dataclasses.asdict(r))]
        for state, word in t.STATE_WORDS.items():
            n = sum(1 for r in drawn if r.rows["size"].state == state)
            if n or state != "limit":
                self.assertEqual(counts[word], n, word)
        self.assertEqual(counts["No size"], len(sample.RECORDS) - len(drawn))
        self.assertEqual(sum(counts.values()), len(sample.RECORDS))
        # one glyph per state, the same marks the field and the entries use
        self.assertEqual({sorted(s.classes - {"g"})[0] for s in legend.find("i", cls="g")}, {"g-prior", "g-unchecked", "g-measured", "g-limit"})

    def test_readout_lists_the_named_and_the_on_file_counts(self):
        (over,) = self.trees["index.html"].root.find("div", cls="overview")
        heads = [h.text() for h in over.find("h2")]
        want = export.readout(sample.RECORDS, method.load())
        self.assertEqual(heads[0], "Named asteroids")
        links = over.find("ul", cls="named")[0].find("a")
        self.assertEqual([(a.attrs["href"], a.attrs["data-key"], a.text()) for a in links],
                         [(f"a/{r['key']}.html", r["key"], r["name"]) for r in want["named"]])
        self.assertTrue(all("km/s" in li.text() for li in over.find("ul", cls="named")[0].find("li")))
        self.assertEqual("Typical, nothing measured" in heads, want["typical"] is not None)
        self.assertEqual(heads[-1], "On file")
        # counts by state: one line per row, and each line adds up to every record
        (table,) = over.find("table", cls="counts")
        self.assertEqual([th.text() for th in table.find("thead")[0].find("th")],
                         ["Row", "Measured", "Limit", "Not measured", "Not checked"])     # "Row" for screen readers only
        lines = table.find("tbody")[0].find("tr")
        self.assertEqual([tr.find("th")[0].text() for tr in lines], [t.ROW_LABELS[r] for r in ROWS])
        for row_id, tr in zip(ROWS, lines):
            cells = [int(td.text()) for td in tr.find("td")]
            self.assertEqual(cells, [sum(1 for r in sample.RECORDS if r.rows[row_id].state == s) for s in t.STATE_WORDS], row_id)
        # the pipeline's own list wins where the build hands it one
        page = gen.index_page([dataclasses.asdict(r) for r in sample.RECORDS], sample.ASSETS, sample.DATA_DATE, sample.METHOD,
                              {"named": [], "typical": {"key": "s0000008", "designation": "2099 HT", "dv": 4.58}})
        self.assertIn('<a href="a/s0000008.html" data-key="s0000008">2099 HT</a>', page)

    # ---- entries

    def test_entry_stands_alone(self):
        anchors = {n.attrs["id"] for n in self.trees["method.html"].root.walk() if "id" in n.attrs}
        linked = set()
        for r in sample.RECORDS:
            root = self.trees[f"a/{r.key}.html"].root
            (main,) = root.find("main")
            self.assertEqual((main.attrs["id"], main.attrs["data-key"]), ("entry", r.key))
            self.assertEqual(root.find("script"), [], r.key)
            # the summary is what the front page's readout lifts: it carries the heading with it
            (summary,) = main.find("section", id="summary")
            self.assertEqual(summary.parent, main)
            self.assertEqual(summary.find("h1")[0].text(), r.name or r.designation)
            ident = {dt.text(): dt.parent.find("dd")[0].text() for dt in summary.find("dt") if dt.parent.parent.tag == "dl" and "ident" in dt.parent.parent.classes}
            self.assertEqual(ident["Number"], str(r.number) if r.number else "none yet")
            if r.name:
                self.assertEqual(ident["Designation"], r.designation)
            self.assertEqual([a.text() for a in main.find("nav", cls="toc")[0].find("a")],
                             ["On file", "Difficulty", "What is in it", "What would settle it", "Missions", "Sources"])
            for a in main.find("nav", cls="toc")[0].find("a"):
                self.assertEqual(len(main.find(id=a.attrs["href"][1:])), 1)
            # links inside the liftable element: its own anchors, the outside world, and the method page,
            # which the readout resolves against the entry's address
            for a in main.find("a"):
                href = a.attrs["href"]
                self.assertRegex(href, r"^(#|https?://|\.\./method\.html#)", r.key)
                if href.startswith("../method.html#"):
                    self.assertIn(href.split("#")[1], anchors, f"{r.key}: method.html has no such anchor")
                    linked.add(href.split("#")[1])
        # every gate and every rung names where its fixed figures come from
        self.assertLessEqual({"g-surface-findable", "g-surface-size", "g-surface-spin", "g-capture-size",
                              "g-capture-mass", "rung-found_again", "rung-brought_back"}, linked)

    def test_summary_is_one_list(self):
        for r in sample.RECORDS:
            s = self.summary(r.key)
            want = SUMMARY_LABELS if r.summary.get("mass_t") else [x for x in SUMMARY_LABELS if x != "Mass"]
            self.assertEqual(list(s), want, r.key)
            groups = [tr.text() for tr in self.entry(r.key).find("table", cls="sumlist")[0].find("tr") if "grp" in tr.classes]
            self.assertEqual(groups, SUMMARY_GROUPS, r.key)
            for name, row_id in (("Size", "size"), ("Spin", "spin"), ("Made of", "surface"), ("Reach", "reach")):
                self.assertEqual(s[name][2].text(), t.STATE_WORDS[r.rows[row_id].state], (r.key, name))
        a = self.summary("s0000001")
        self.assertEqual(a["Size"][0].text(), "3.1–13 m")
        self.assertEqual(a["Spin"][0].text(), "92.52 s")
        self.assertEqual(a["Spin"][1].text(), "one turn, Ondřejov photometry table")
        self.assertEqual(a["Reach"][0].text(), "4.620 km/s")
        self.assertEqual(a["Reach"][1].text(), "354 d round trip")
        self.assertEqual((a["Whole-body capture"][0].text(), a["Whole-body capture"][2].text()), ("41%", "Untested"))
        # a settled mission's value is its status, with its mark, and no second tag
        self.assertEqual((a["Surface work"][0].text(), a["Surface work"][2].text()), ("Fail", ""))
        self.assertEqual(a["Surface work"][1].text(), "needs 40 m or more across and turns slower than 2.2 h")
        self.assertEqual(a["Would settle most"][0].text(), "Size or reflectivity measurement")
        self.assertIn("window 2027-02-10 to 2027-04-02", a["Would settle most"][1].text())
        self.assertEqual(self.summary("s0000005")["Surface work"][0].text(), "Pass")
        self.assertEqual(self.summary("s0000005")["Made of"][0].text(), "Carbon-rich")
        self.assertEqual(self.summary("s0000002")["Size"][1].text(), "50–85 m, 1σ, thermal model, SsODNet")
        self.assertEqual(self.summary("s0000008")["Spin"][0].text(), "over 4 h")
        # a measured row nobody may print says so, and names whose value it is
        self.assertEqual(self.summary("s0000004")["Spin"][1].text(), f"{t.short_name(srcs(), 'lcdb')}, not shown here")
        self.assertEqual(self.summary("s0000003")["Spin"][1].text(), "sources disagree on the period")
        # the missions' results are said once, under Missions: here only why nothing is ranked
        self.assertEqual(self.summary("s0000005")["Would settle most"][1].text(), "both missions rest on measurements")

    def test_six_rows_in_order_with_state(self):
        for r in sample.RECORDS:
            rows = self.entry(r.key).find("section", cls="row")
            self.assertEqual([n.attrs["data-row"] for n in rows], list(ROWS), r.key)
            for n in rows:
                state = r.rows[n.attrs["data-row"]].state
                self.assertEqual(n.attrs["data-state"], state)
                (tag,) = n.find("div", cls="rh")[0].find("span", cls="st")
                self.assertEqual(tag.text(), t.STATE_WORDS[state])
                self.assertIn(f"st-{state}", tag.classes)
                self.assertEqual(n.find("h3")[0].text(), t.ROW_LABELS[n.attrs["data-row"]])

    def test_unchecked_never_prints_not_measured(self):
        seen = 0
        for r in sample.RECORDS:
            for row_id, n in self.rows(r.key).items():
                if r.rows[row_id].state != "unchecked":
                    continue
                seen += 1
                text = n.text()
                self.assertNotIn("not measured", text.lower(), (r.key, row_id))
                self.assertIn("Not checked", text, (r.key, row_id))
                for sid in r.rows[row_id].unchecked:
                    self.assertIn(sample.SOURCES[sid].name, text, (r.key, row_id))
            # the summary: an unchecked row's mark is the ring and its word "Not checked", and so is the
            # mass that rests on an unchecked size
            s = self.summary(r.key)
            for name, row_id in (("Size", "size"), ("Spin", "spin"), ("Made of", "surface")):
                if r.rows[row_id].state == "unchecked":
                    self.assertEqual(s[name][2].text(), "Not checked", (r.key, name))
                    self.assertEqual(len(s[name][2].find("i", cls="g-unchecked")), 1)
            if r.rows["size"].state == "unchecked" and "Mass" in s:
                self.assertEqual(s["Mass"][2].text(), "Not checked", r.key)
        self.assertGreaterEqual(seen, 6)

    def test_the_figure_never_says_not_measured_of_an_unchecked_row(self):
        """The rock heads the summary. What it gives a screen reader follows the same rule as a row:
        not checked is said, with the source, and never as not measured."""
        seen = 0
        for r in sample.RECORDS:
            (figure,) = self.entry(r.key).find("figure")
            said = everything_in(figure)
            unchecked = {row_id: r.rows[row_id].unchecked for row_id in ("size", "spin")
                         if r.rows[row_id].state == "unchecked"}
            for row_id, ids in unchecked.items():
                seen += 1
                self.assertIsNone(SAYS_NOT_MEASURED[row_id].search(said), (r.key, said))
                what = "size" if row_id == "size" else "period"
                names = ", ".join(sample.SOURCES[s].name for s in ids)
                self.assertIn(f"{what} not checked: {names}", figure.find("svg")[0].attrs["aria-label"], r.key)
            if "size" in unchecked:
                # drawn in its own line, not the line of a size nobody has measured
                self.assertIn("s-unchecked", figure.classes)
                self.assertEqual(len(figure.find("polygon", cls="s-unchecked")), 1)
        self.assertGreaterEqual(seen, 3)
        # a row that was checked and holds nothing still says so
        self.assertIn("size not measured", self.entry("s0000001").find("svg")[0].attrs["aria-label"])
        self.assertIn("not turning: no measured period", self.entry("s0000008").find("svg")[0].attrs["aria-label"])
        # the check itself: it would catch the words it is there to catch
        self.assertIsNotNone(SAYS_NOT_MEASURED["spin"].search("not turning: no measured period"))
        self.assertIsNotNone(SAYS_NOT_MEASURED["size"].search("2099 QQ8, size not measured, typical outline"))

    def test_an_unchecked_source_is_named_once_with_its_reason(self):
        rows = self.rows("s0000009")
        line = lambda row_id: rows[row_id].find("p", cls="un")[0].text()
        self.assertEqual(line("size"), "Not checked: SsODNet, unknown there, 2026-11-21")
        self.assertEqual(line("spin"), "Not checked: SsODNet, no card fetched; Ondřejov photometry table, older than this object")
        self.assertEqual(line("surface"), "Not checked: SsODNet, request failed 2026-11-25, timed out")
        for row_id in ("size", "spin", "surface"):
            self.assertEqual(rows[row_id].find("p", cls="note"), [], row_id)       # nothing left to say twice
            self.assertEqual(rows[row_id].text().count("SsODNet"), 1, row_id)
        # the note keeps what is not about the source
        push = rows["push"]
        self.assertEqual(push.find("p", cls="note")[0].text(),
                         "JPL's bulk values are rounded to two figures and carry no force law.")
        self.assertEqual(push.find("p", cls="un")[0].text(), "Not checked: SsODNet, unknown there, 2026-11-21")
        # one <p class="un"> a row, every source linked inside it, with the ring
        for r in sample.RECORDS:
            for row_id, n in self.rows(r.key).items():
                held = r.rows[row_id].unchecked
                self.assertEqual(len(n.find("p", cls="un")), 1 if held else 0, (r.key, row_id))
                if held:
                    un = n.find("p", cls="un")[0]
                    self.assertEqual([a.attrs["href"] for a in un.find("a")], [f"#src-{s}" for s in held])
                    self.assertEqual(len(un.find("i", cls="g-unchecked")), 1)

    def test_unchecked_reasons(self):
        row = {"unchecked": ["ssodnet"], "note": "No fitted value reaches 3 sigma. No SsODNet card has been fetched."}
        self.assertEqual(t.unchecked_reasons(row), (["no card fetched"], "No fitted value reaches 3 sigma."))
        self.assertEqual(t.unchecked_reasons({"unchecked": ["a", "b"], "note": "Only one sentence."}),
                         (["", ""], "Only one sentence."))
        self.assertEqual(t.unchecked_reasons({"unchecked": ["a"], "note": None}), ([""], ""))

    def test_every_value_carries_its_unit(self):
        """A number carries its unit, in the value or, for a power of ten, in its label once."""
        checked = 0
        for r in sample.RECORDS:
            for row_id, row in r.rows.items():
                for f in row.facts:
                    f = dataclasses.asdict(f)
                    unit = t.UNITS.get(f["unit"], f["unit"])
                    if not t.is_num(f["value"]) or not unit:
                        continue
                    checked += 1
                    val, rng, extra = t._value(row_id, f)
                    k, shown = t.scale_for(row_id, f["label"], f["unit"], f["value"])
                    self.assertTrue(shown in val or shown in extra, (r.key, f["label"], val, extra))
                    if rng:
                        self.assertTrue(rng.endswith(", 1σ"), rng)
        self.assertGreater(checked, 20)
        val, rng, extra = t._value("push", {"label": "A2", "value": -2.9e-14, "lo": -2.919e-14, "hi": -2.881e-14, "unit": "au/d^2"})
        self.assertEqual((val, rng, extra), ("−2.9", "−2.919 to −2.881, 1σ", "10⁻¹⁴ au/d²"))
        page = self.rows("s0000001")["push"].text()
        self.assertIn("Drift, A2, 10⁻¹³ au/d²", page)
        self.assertIn("under 2.1", page)

    def test_inference_values_are_pointers(self):
        # D: the only period is in the lightcurve database.
        d = self.pages["a/s0000004.html"]
        spin = self.rows("s0000004")["spin"]
        self.assertNotIn("5.432", d)
        self.assertNotIn("2+", spin.text())
        self.assertNotIn("animation-duration", d)
        self.assertIn(t.POINTER, spin.text())
        self.assertIn(sample.SOURCES["lcdb"].name, spin.text())
        self.assertEqual(spin.find("i", cls="pt"), [])
        # E: the database's value differs from JPL's, so only JPL's is printed.
        e = self.pages["a/s0000005.html"]
        self.assertNotIn("4.29", e.replace("4.297", ""))
        self.assertIn("4.297 h", self.rows("s0000005")["spin"].text())
        self.assertIn("animation-duration:15470s", e)
        # B: JPL gives the same value. JPL's line shows it; the database's is still a pointer, with no grade.
        b = self.rows("s0000002")["spin"].text()
        self.assertEqual(len(re.findall(r"10\s*h", b)), 2)   # JPL's fact and the scale's tick
        self.assertNotIn("U 1+", b)
        self.assertIn(t.POINTER, b)
        # and the source's own line says so
        self.assertIn("its values are not shown", self.pages["a/s0000002.html"])

    def test_inference_rule_over_every_sample_fact(self):
        hidden = 0
        for r in sample.RECORDS:
            text = self.entry(r.key).text()
            for row_id, row in r.rows.items():
                facts = [dataclasses.asdict(f) for f in row.facts]
                for f in facts:
                    if t.displayable(f, srcs()):
                        continue
                    hidden += 1
                    self.assertEqual(sample.SOURCES[f["source"]].licence, "inference")
                    if any(o["value"] == f["value"] and t.displayable(o, srcs()) for o in facts):
                        continue                    # another source states it, and shows it under its own name
                    k, unit = t.scale_for(row_id, f["label"], f["unit"], f["value"])
                    shown = re.compile(r"(?<![\d.,])" + re.escape(t.num(f["value"] * k)) + r"(?!\d)")
                    self.assertIsNone(shown.search(text), (r.key, row_id))
        self.assertGreaterEqual(hidden, 2)

    def test_an_inference_value_is_a_pointer_whatever_another_source_states(self):
        held = {"label": "amplitude", "value": 0.43, "lo": 0.07, "hi": 0.43, "unit": "mag", "source": "lcdb", "quality": "2+"}
        same = {"label": "amplitude", "value": 0.43, "lo": 0.07, "hi": 0.43, "unit": "mag", "source": "pravec"}
        self.assertIsNone(t.public(held, srcs()))
        self.assertEqual(t.public(same, srcs()), same)
        html = t.facts_table("spin", [held, same], srcs())
        self.assertEqual(html.count("0.43"), 2)                 # the value and its range, once, under Pravec's name
        self.assertNotIn("2+", html)
        self.assertEqual(html.count(t.POINTER), 1)
        rows = parse(html).root.find("tr")
        self.assertEqual([("ptr" in tr.classes) for tr in rows], [True, False])     # in the ledger's order: the row rests on the first

    def test_every_fact_names_its_source_and_a_shared_source_is_printed_once(self):
        for r in sample.RECORDS:
            for row_id, n in self.rows(r.key).items():
                facts = [dataclasses.asdict(f) for f in r.rows[row_id].facts]
                tables = [tb for tb in n.find("table", cls="facts") if "est" not in tb.classes]
                lines = [tr for tb in tables for tr in tb.find("tr")]
                self.assertEqual(len(lines), len(facts), (r.key, row_id))
                for tb in tables:
                    trs = tb.find("tr")
                    after = [k for k in tb.parent.kids if isinstance(k, Node)]
                    nxt = after[after.index(tb) + 1] if after.index(tb) + 1 < len(after) else None
                    if nxt is not None and "srcline" in nxt.classes:
                        self.assertGreater(len(trs), 1)
                        self.assertTrue(all(tr.find("td", cls="s")[0].text() == "" for tr in trs))
                        self.assertEqual(len(nxt.find("a")), 1)
                    else:
                        for tr in trs:
                            self.assertEqual(len(tr.find("td", cls="s")[0].find("a")), 1, (r.key, row_id))

    def test_labels_and_grades_are_words(self):
        rows = self.rows("s0000009")
        labels = lambda n: [th.text() for th in n.find("th")]
        self.assertIn("Observed over", labels(rows["tracking"]))
        self.assertNotIn("condition code", rows["tracking"].text())
        self.assertEqual(labels(rows["push"])[0].split(",")[0], "Radiation pressure")
        self.assertEqual(labels(rows["surface"])[0], "Reflectivity")
        # an upstream tag is printed in words
        self.assertIn("spacecraft", self.rows("s0000005")["size"].text())
        self.assertNotIn("SPACE", self.pages["a/s0000005.html"])
        self.assertEqual(t.label("spin", "period"), "period")
        for tag, words in (("SPACE", "spacecraft"), ("NEATM", "thermal model"), ("TPM", "thermophysical model"),
                           ("Astrometry(O+R)", "optical and radar astrometry"), ("Astrometry(O)", "optical astrometry"),
                           ("Computed", "computed"), ("Yarkovsky+SRP", "from drift and radiation pressure"),
                           ("Mahlke Spec VISNIR", "Mahlke class, visible and near-infrared spectrum"),
                           ("Bus-DeMeo Phot VIS", "Bus-DeMeo class, visible colours"),
                           ("SMASSII", "SMASSII"), ("thermal model, one band", "thermal model, one band"),
                           ("sidereal, SPACE", "sidereal, spacecraft"),
                           ("Phot five bands, X-complex", "colours: five bands, X-complex")):
            self.assertEqual(t.grade("surface", tag), words)
        self.assertEqual(t.grade("spin", "2-"), "quality U 2-")
        self.assertEqual(t.grade("spin", None), "")

    def test_interface_copy_has_no_parentheses(self):
        """B612 draws parentheses square: interface copy goes without them; the serif sentences keep theirs."""
        self.assertEqual(t.unparen("Lee+2022 (2022A&A...661L...3L)"), "Lee+2022, 2022A&A...661L...3L")
        self.assertEqual(t.source_name({"x": {"name": "Asteroid Lightcurve Database (LCDB)"}}, "x"),
                         "Asteroid Lightcurve Database, LCDB")
        self.assertEqual(t.short_name({"x": {"name": "Asteroid Lightcurve Database (LCDB)"}}, "x"), "LCDB")
        serif = lambda n: bool(n.classes & {"note", "stm", "stmt", "gtext"}) or n.tag == "p" and n.parent.tag == "li"
        for name, tree in self.trees.items():
            (main,) = tree.root.find("main")
            for tr in main.find("table", cls="facts") + main.find("table", cls="sumlist"):
                self.assertNotRegex(tr.text(serif), r"[()]", name)

    def test_a_fact_prints_the_ledgers_word_on_it(self):
        f = {"label": "A2", "value": -4.5e-14, "lo": None, "hi": None, "unit": "au/d^2", "kind": "value",
             "source": "jpl-sbdb", "ref": None, "quality": None, "used": True, "note": "signal-to-noise 191"}
        line = parse(t.facts_table("push", [f], srcs())).root
        self.assertEqual(line.find("td", cls="q")[0].text(), "signal-to-noise 191")
        self.assertEqual(parse(t.facts_table("push", [dict(f, note=None)], srcs())).root.find("td", cls="q")[0].text(), "")

    def test_rock(self):
        a = self.entry("s0000001").find("figure", cls="rockfig")[0]
        (g,) = a.find("g", cls="turn")
        self.assertEqual(g.attrs["style"], "animation-duration:92.52s")   # nothing capped
        self.assertEqual(len(g.find("polygon")), 3)                       # the size range as nested outlines
        self.assertEqual([sorted(p.classes) for p in g.find("polygon")], [["edge"], ["mid", "s-prior"], ["edge", "in"]])
        self.assertEqual([dd.text() for dd in a.find("dd")], ["13 m", "6.2 m", "3.1 m"])
        self.assertEqual([dt.text() for dt in a.find("dt")], ["Outer, 95th", "Middle", "Inner, 5th"])
        self.assertEqual(len(a.find("g", cls="scale")), 1)
        # the glow means measured: a halo under the line of a measured size, and nowhere else
        measured = self.entry("s0000007").find("figure")[0]
        self.assertEqual([sorted(p.classes) for p in measured.find("polygon")],
                         [["halo"], ["edge"], ["mid", "s-measured"], ["edge", "in"]])
        self.assertEqual([dt.text() for dt in measured.find("dt")], ["High, 1σ", "Measured", "Low, 1σ"])
        for r in sample.RECORDS:
            fig = self.entry(r.key).find("figure")[0]
            self.assertEqual(bool(fig.find("polygon", cls="halo")), "s-measured" in fig.classes, r.key)
        limit = self.entry("s0000003").find("figure")[0].find("polygon")
        self.assertEqual([sorted(p.classes) for p in limit], [["mid", "s-limit"]])
        self.assertEqual(self.entry("s0000005").find("g", cls="turn")[0].attrs["style"], "animation-duration:15470s")
        # no usable period, no animation: graded too low, sources disagree, held back, only a bound, not checked
        for key, why in (("s0000002", "no period good enough to use"), ("s0000003", "sources disagree on the period"),
                         ("s0000004", t.POINTER), ("s0000008", "no measured period"),
                         ("s0000009", "period not checked: SsODNet, Ondřejov photometry table")):
            fig = self.entry(key).find("figure")[0]
            self.assertEqual(fig.find("g", cls="turn"), [], key)
            self.assertIn(f"not turning: {why}", fig.find("svg")[0].attrs["aria-label"], key)
        # nothing to draw without a size
        none = self.entry("s0000006")
        self.assertEqual(none.find("figure")[0].find("svg"), [])
        self.assertIn("not drawn", none.find("figure")[0].text())

    def test_a_narrow_range_is_one_outline(self):
        # E: 484 to 496 m. Three outlines 2 px apart read as one bevelled line, so one is drawn
        # and the caption carries the range.
        e = self.entry("s0000005").find("figure")[0]
        self.assertEqual([sorted(p.classes) for p in e.find("polygon")], [["halo"], ["mid", "s-measured"]])
        self.assertEqual([dd.text() for dd in e.find("dd")], ["496 m", "490 m", "484 m"])
        wide = dict(dataclasses.asdict(sample.RECORDS[6]))
        for lo, hi, outlines in ((7.9, 9.8, 2), (7.0, 8.75, 4)):         # either side of a ratio of 1.25, with the halo
            wide["rows"]["size"]["facts"][0].update(lo=lo, hi=hi)
            self.assertEqual(t.rock(wide, srcs()).count("<polygon"), outlines, (lo, hi))

    def test_rock_is_to_scale(self):
        # The scale bar's printed length over its drawn length gives metres per unit. The middle outline
        # is the field's outline for this key at half the size (8 m).
        fig = self.entry("s0000007").find("figure")[0]
        (scale,) = fig.find("g", cls="scale")
        metres = float(scale.find("text")[0].text().split(" ")[0])
        drawn = float(re.search(r"h([\d.]+)", scale.find("path")[0].attrs["d"])[1])
        mid = fig.find("polygon", cls="mid")[0]
        pts = [tuple(map(float, xy.split(","))) for xy in mid.attrs["points"].split()]
        want = [(x * 4.0 * drawn / metres, y * 4.0 * drawn / metres) for x, y in t.shape("s0000007")]
        self.assertEqual(len(pts), len(want))
        for (x, y), (wx, wy) in zip(pts, want):
            self.assertAlmostEqual(x, wx, delta=0.1)
            self.assertAlmostEqual(y, wy, delta=0.1)
        # as in the field, no point of an outline lies further out than half the size
        self.assertLessEqual(max((x * x + y * y) ** 0.5 for x, y in t.shape("s0000007")), 1.0)
        self.assertLessEqual(max(abs(c) for xy in pts for c in xy), t.ROCK_BOX / 2)

    def test_shape_is_fixed_by_key(self):
        self.assertEqual(t.shape("k1"), t.shape("k1"))
        self.assertEqual(len({tuple(t.shape(f"k{i}")) for i in range(40)}), 40)   # the turn differs even where the outline repeats
        for key in ("k1", "k2", "s0000001"):
            pts = t.shape(key)
            self.assertEqual(len(pts), 12)
            radii = [(x * x + y * y) ** 0.5 for x, y in pts]
            self.assertLessEqual(max(radii), 1.0 + 1e-9)
            self.assertGreater(min(radii), 0.4)
        # the site's mark is one of the field's rocks, chosen by a rule, not drawn by hand
        self.assertTrue(t.MARK_KEY.startswith(t.SITE))
        self.assertIn(t._points(t.shape(t.MARK_KEY), 9.5 / max((x * x + y * y) ** 0.5 for x, y in t.shape(t.MARK_KEY))),
                      t.rock_mark())

    def test_what_is_not_measured_leads_with_its_range(self):
        size = self.rows("s0000001")["size"]
        (line,) = size.find("tr", cls="pr")
        self.assertEqual(line.find("th")[0].text(), "From brightness")
        self.assertEqual(line.find("td", cls="v")[0].text(), "3.1–13 m")     # the range is the value
        self.assertEqual(line.find("td", cls="r")[0].text(), "9 in 10")
        self.assertNotIn("6.2", size.text())                                       # no single figure beside it
        surface = self.rows("s0000008")["surface"].find("tr", cls="pr")[0]
        self.assertEqual((surface.find("th")[0].text(), surface.find("td", cls="v")[0].text()), ("Reflectivity", "5–45%"))
        self.assertEqual(surface.find("td", cls="r")[0].text(), "9 in 10 at this brightness")
        # and its scale draws the band, the middle as a tick, no point
        (gauge,) = size.find("div", cls="gauge")
        self.assertEqual((len(gauge.find("i", cls="est")), len(gauge.find("i", cls="pt"))), (1, 0))

    def test_a_reflectivity_implied_by_a_measured_size_says_so(self):
        # G: the size is measured, so the reflectivity drawn for it follows from that size and H.
        line = self.rows("s0000007")["surface"].find("tr", cls="pr")[0]
        self.assertEqual(line.find("td", cls="v")[0].text(), "30–140%")
        self.assertEqual(line.find("td", cls="r")[0].text(), "9 in 10, implied by its size and H")
        self.assertIn("over 100% cannot be", line.find("td", cls="q")[0].text())
        # the population's reflectivity carries no such flag
        self.assertEqual(self.rows("s0000008")["surface"].find("tr", cls="pr")[0].find("td", cls="q")[0].text(), "")

    def test_scales_draw_the_mission_thresholds_from_the_method(self):
        m = method.load()
        preset = {(mid, g["id"]): g["preset"] for mid in m.missions["order"] for g in m.missions[mid]["gates"]}
        size = self.rows("s0000001")["size"].find("div", cls="gauge")[0]
        self.assertEqual([g.text() for g in size.find("i", cls="gate")],
                         [f"{t.num(preset[('capture', 'size')])} m: whole-body capture",
                          f"{t.num(preset[('surface', 'size')])} m: surface work"])
        spin = self.rows("s0000001")["spin"].find("div", cls="gauge")[0]
        self.assertEqual([g.text() for g in spin.find("i", cls="gate")], [f"{t.num(preset[('surface', 'spin')])} h: surface work"])
        # both missions draw the orbit code at the same line: it is drawn once, by its own name
        track = self.rows("s0000001")["tracking"].find("div", cls="gauge")[0]
        self.assertEqual([g.text() for g in track.find("i", cls="gate")], [m.missions["surface"]["gates"][0]["label"]])
        self.assertEqual(t.gate_lines(None), {})

    def test_prior_and_conflict_and_sources(self):
        self.assertEqual(len(self.rows("s0000004")["size"].find("i", cls="est")), 1)    # unchecked: typical range still drawn
        self.assertIn("factor of 100", self.rows("s0000003")["spin"].find("p", cls="conflict")[0].text())
        self.assertEqual(len(self.rows("s0000003")["spin"].find("i", cls="pt")), 2)   # both periods on the scale
        limit = self.rows("s0000008")["spin"]
        self.assertIn("over 4 h", limit.text())
        self.assertTrue(limit.find("i", cls="lim"))
        for r in sample.RECORDS:
            main = self.entry(r.key)
            listed = {tr.attrs["id"].removeprefix("src-") for tr in main.find("tr") if tr.attrs.get("id", "").startswith("src-")}
            for a in main.find("a"):
                if a.attrs["href"].startswith("#src-"):
                    self.assertIn(a.attrs["href"][5:], listed, r.key)
            for sid in listed:
                s = sample.SOURCES[sid]
                text = main.find("tr", id=f"src-{sid}")[0].text()
                self.assertIn(s.edition, text)
                self.assertIn(s.citation, text)
            # a source the record never reached for any row says so, with the ring
            for sid in listed - set(r.sources):
                if any(sid in row.unchecked for row in r.rows.values()):
                    self.assertIn("Not checked for this asteroid", main.find("tr", id=f"src-{sid}")[0].text())

    def test_a_source_fetched_over_several_days_says_so(self):
        one = {"retrieved": "2026-11-21"}
        self.assertEqual(t.fetched(one), "<time>2026-11-21</time>")
        want = "<time>2026-11-21</time> to <time>2026-11-25</time>"
        self.assertEqual(t.fetched({"retrieved": "2026-11-25", "retrieved_from": "2026-11-21"}), want)
        self.assertEqual(t.fetched({"retrieved": "2026-11-21", "retrieved_from": "2026-11-21"}), t.fetched(one))
        self.assertEqual(t.fetched({"retrieved": None}), "")
        s = {"ssodnet": dict(srcs()["ssodnet"], retrieved="2026-11-25", retrieved_from="2026-11-21")}
        self.assertIn(want, t.source_row("ssodnet", s))

    def test_blocks(self):
        a = self.entry("s0000001")
        text = a.text()
        for words in ("Find it again", "Reach it", "Work on it", "Anything in it", "Bring any back",
                      "Prices: list prices of 2026-11-20", "Counting the zeros, three in four hold under $310 thousand of it."):
            self.assertIn(words, text)
        rungs = a.find("ol", cls="ladder")[0].find("li")
        self.assertEqual([li.attrs["data-status"] for li in rungs], [r["status"] for r in self.by_key["s0000001"].ladder])
        self.assertEqual([li.find("span", cls="st")[0].text() for li in rungs][:3], ["Measured"] * 3)
        self.assertIn("No estimate", self.entry("s0000006").find("section", id="value")[0].text())
        statuses = {m.attrs["data-status"] for r in sample.RECORDS for m in self.entry(r.key).find("div", cls="mission")}
        self.assertEqual(statuses, {"pass", "fail", "untested"})
        # with no sentences from the pipeline the chance of nothing comes first, and no single dollar figure
        b = self.entry("s0000002").find("section", id="value")[0].text()
        self.assertLess(b.index("Chance of no separable metal"), b.index("That metal at list prices"))
        self.assertIn("$20 million to $2.4 billion", b)
        # a mass range that crosses a million: both ends in the high end's scale
        self.assertIn("0.071–3.6 million t", self.entry("s0000008").text())

    def test_a_hundred_cells_counted_from_the_record(self):
        """Of 100 like it: the chance of nothing first, the uncertain cells half-filled, every count from the record."""
        val = {"metal": {"p_nothing_lo": 0.3665, "p_nothing_hi": 0.427}, "iron_rich": {"p_lo": 0.01, "p_hi": 0.06},
               "water": {"p_nothing_lo": 0.9465, "p_nothing_hi": 0.965}}
        self.assertEqual(t._metal_cells(val), [("", 37), ("u", 6), ("s", 51), ("ru", 5), ("r", 1)])
        self.assertEqual(t._water_cells(val), [("", 95), ("u", 2), ("s", 3)])
        rec = dict(dataclasses.asdict(sample.RECORDS[0]))
        rec["value"] = dict(rec["value"], **val, statement_ids=["metal_none", "metal_under", "water_none", "metal_cap"])
        block = parse(t.value(rec)).root
        for units in block.find("div", cls="units"):
            self.assertEqual(len(units.find("i")), 100)
        heads = [h.text() for h in block.find("h3")]
        self.assertEqual(heads, ["Platinum-group metal, in metal grains", "Water, bound in minerals"])
        said = [[li.text() for li in ul.find("li")] for ul in block.find("ul", cls="stm")]
        self.assertEqual(said[1], [rec["value"]["statements"][2]])         # sentences go to the block they are about
        self.assertNotIn("mean", t.value(rec).lower())

    def test_price_tables_are_the_records_own_table(self):
        """value.table is printed as it stands: its cells counted in 100, its rows and notes; no figure typed here."""
        table = {"metal": {"cells": [{"id": "none", "label": "None", "n": 37}, {"id": "none_or_some", "label": "None or some", "n": 6},
                                     {"id": "some", "label": "Some", "n": 51}, {"id": "iron_rich_or_not", "label": "Iron-rich or not", "n": 5},
                                     {"id": "iron_rich", "label": "Iron-rich", "n": 1}],
                           "rows": [{"id": "none", "label": "Hold none", "of100": "37 to 43", "kg": None, "usd": None},
                                    {"id": "under_q75", "label": "3 in 4 hold under", "of100": None, "kg": "400 kg", "usd": "$26 million"}]},
                 "water": {"cells": [{"id": "none", "label": "None", "n": 100}],
                           "rows": [{"id": "none", "label": "Hold none", "of100": "all 100", "tonnes": None}]},
                 "notes": ["Dollars count each metal only up to a tenth of a year's world mine supply."]}
        rec = dict(dataclasses.asdict(sample.RECORDS[0]))
        rec["value"] = dict(rec["value"], table=table, basis="USGS list prices")
        block = parse(t.value(rec)).root
        units = block.find("div", cls="units")
        self.assertEqual([len(u.find("i")) for u in units], [100, 100])
        self.assertEqual([len(u.find("i", cls="ru")) for u in units], [5, 0])
        metal, water = block.find("table", cls="vt")
        self.assertEqual([[c.text() for c in tr.kids if isinstance(c, Node) and c.tag in ("th", "td")] for tr in metal.find("tbody")[0].find("tr")],
                         [["Hold none", "37 to 43", "", ""], ["3 in 4 hold under", "", "400 kg", "$26 million"]])
        self.assertEqual([c.text() for c in water.find("tbody")[0].find("td")], ["all 100", ""])
        notes = [p.text() for p in block.find("div", cls="foot-notes")[0].find("p")]
        self.assertEqual(notes, [table["notes"][0], "Prices: USGS list prices"])
        self.assertEqual(block.find("ul", cls="stm"), [])               # the table replaces the sentences
        # a returned sample replaces the class odds: the record's sentences, no table
        rec["value"] = dict(rec["value"], sample={"mission": "OSIRIS-REx"})
        self.assertEqual(parse(t.value(rec)).root.find("table", cls="vt"), [])

    def test_the_last_rung_prints_its_two_amounts(self):
        parts = [{"id": "grams", "label": "Grams", "word": "done", "text": "done three times, by space agencies."},
                 {"id": "more_than_grams", "label": "Kilograms or tonnes", "word": "proposed", "text": "proposed, never built."}]
        rung = {"rung": "brought_back", "status": "measured", "text": "Grams: done three times, by space agencies. "
                "Kilograms or tonnes: proposed, never built.", "parts": parts}
        li = parse(t.ladder([rung])).root.find("li")[0]
        rows = [[c.text() for c in tr.kids if isinstance(c, Node) and c.tag in ("th", "td")] for tr in li.find("tbody")[0].find("tr")]
        self.assertEqual(rows, [["Grams", "Done three times, by space agencies."], ["Kilograms or tonnes", "Proposed, never built."]])
        self.assertEqual(li.find("p"), [])                              # said once, not again as a sentence

    def test_an_untested_chance_is_never_printed_as_certain(self):
        i = self.entry("s0000009")
        said = [m.find("p", cls="verdict")[0].text() for m in i.find("div", cls="mission")]
        self.assertEqual(said, ["under 1%chance of passing every gateUntested", "over 99%chance of passing every gateUntested"])
        chances = [td.text() for td in i.find("div", cls="mission")[0].find("td", cls="num")]
        self.assertEqual(chances, ["", "under 1%", "1%"])     # pass, 0 of 2,000, then 10 of 2,000
        for r in sample.RECORDS:
            main = self.entry(r.key)
            said = [td.text() for td in main.find("td", cls="num") if td.parent.parent.parent.tag == "table"
                    and "gates" in td.parent.parent.parent.classes]
            said += [b.text() for b in main.find("p", cls="verdict")] + [td.text() for td in main.find("td", cls="v")]
            for x in said:
                self.assertNotRegex(x, r"^(0|100)%", r.key)

    def test_what_would_settle_it(self):
        # an observation that names its gate: a label and a value each, no sentence
        a = self.entry("s0000001").find("section", id="settle")[0]
        kv = a.find("dl")[0]
        pairs = dict(zip([dt.text() for dt in kv.find("dt")], [dd.text() for dd in kv.find("dd")]))
        self.assertEqual(pairs["Observation"], "Size or reflectivity measurement")
        self.assertEqual(pairs["Settles"], "10 m or less across, for whole-body capture, 86% chance now")
        self.assertEqual(pairs["Telescope"], "2 m telescope, or radar at the close pass")
        self.assertNotIn("2027-02-10", a.text())                 # when it can be observed is the tracking row's to say
        # nothing ranked: the reason, in a few words
        said = lambda key: dict(zip(*[[x.text() for x in self.entry(key).find("section", id="settle")[0].find(tag)]
                                       for tag in ("dt", "dd")]))["Observation"]
        self.assertEqual(said("s0000005"), "None, both missions rest on measurements")
        self.assertEqual(said("s0000006"), "None, orbit not good enough to find it again")
        self.assertEqual(said("s0000009"), "None, no one observation would change a mission's result")
        both = dataclasses.asdict(sample.RECORDS[4])
        both["missions"]["surface"]["status"] = "fail"
        self.assertEqual(t.nothing_ranked(both), "both missions rest on measurements")
        gone = dict(dataclasses.asdict(sample.RECORDS[5]), gone={"date": "2099-02-15", "text": "It hit.", "evidence": "x"})
        self.assertEqual(t.nothing_ranked(gone), "it no longer exists")
        # and nothing on its entry treats it as still there: no turning rock, no estimate of what is in it
        was = dataclasses.asdict(next(r for r in sample.RECORDS if t.period_of(dataclasses.asdict(r), srcs())[0]))
        self.assertIn('class="turn"', t.rock(was, srcs()))
        self.assertIn("Mass of the whole asteroid", t.value(was))
        was["gone"] = gone["gone"]
        self.assertNotIn('class="turn"', t.rock(was, srcs()))
        self.assertIn("not turning: it no longer exists", t.rock(was, srcs()))
        self.assertEqual(t.value(was), '<p class="none">No estimate: it no longer exists</p>')

    def test_an_observation_says_which_source_was_not_checked(self):
        rec = dataclasses.asdict(sample.RECORDS[0])
        rec["observe"]["unchecked"] = ["ssodnet"]
        block = parse(t.observe(rec, {"size": "Size or reflectivity measurement"}, srcs())).root
        pairs = dict(zip([dt.text() for dt in block.find("dt")], block.find("dd")))
        self.assertEqual(pairs["Check first"].text(), "SsODNet")
        self.assertEqual(pairs["Check first"].find("a")[0].attrs["href"], "#src-ssodnet")
        self.assertEqual(len(pairs["Check first"].find("i", cls="g-unchecked")), 1)
        rec["observe"]["unchecked"] = ["lcdb"]
        page = parse(gen.observe_page([rec], srcs(), sample.ASSETS, sample.DATA_DATE, sample.METHOD,
                                      {"size": "Size or reflectivity measurement"})).root
        self.assertEqual(page.find("td", cls="chk")[0].text(), sample.SOURCES["lcdb"].name)

    def test_entry_size(self):
        sizes = {r.designation: len(self.pages[f"a/{r.key}.html"].encode()) for r in sample.RECORDS}
        print(f"\nentry pages: {min(sizes.values()):,} to {max(sizes.values()):,} bytes; "
              f"mean {sum(sizes.values()) // len(sizes):,}")
        self.assertLess(max(sizes.values()), 40_000)

    # ---- the observe list, the record, the method

    def test_observe_list(self):
        root = self.trees["list/observe.html"].root
        rows = [tr for tr in root.find("tbody")[0].find("tr") if not tr.classes & {"tier", "run"}]
        want = [r.designation for r in observe.ranked([r for r in sample.RECORDS if r.observe])]
        self.assertEqual(sorted(want), ["2099 AA37", "2099 HT", "2099 NJ", "2099 OB5"])
        self.assertEqual([tr.find("a")[0].text() for tr in rows], want)
        self.assertEqual([tr.find("td")[0].text() for tr in rows], ["1", "2", "3", "4"])
        # the columns are named by position: style.css labels each on a phone
        cols = ("Rank", "Asteroid", "Delta-v, km/s", "Size, m", "Telescope", "Window opens", "Window closes", "Peak, V mag", "Check first")
        cells = {tr.find("a")[0].text(): dict(zip(cols, (td.text() for td in tr.find("td")))) for tr in rows}
        first = cells["2099 HT"]
        self.assertEqual((first["Window opens"], first["Window closes"], first["Peak, V mag"]), ("2027-02-20", "2027-04-11", "17.5"))
        self.assertEqual(first["Telescope"], "Small telescope, a few nights")
        self.assertEqual(first["Delta-v, km/s"], "4.58")
        self.assertEqual(cells["2099 NJ"]["Window opens"], "")
        # what one observation settles is said once for each run of rows that share it, not on every row
        runs = [tr for tr in root.find("tbody")[0].find("tr") if "run" in tr.classes]
        self.assertEqual(len(runs), 4)
        self.assertEqual(runs[1].text(gap=" "), "Observation Size or reflectivity measurement Settles 10 m or less across, for whole-body capture")
        # the list is in the method's order and has no script: its headings are plain
        self.assertEqual(root.find("thead")[0].find("button"), [])
        self.assertEqual(root.find("script"), [])
        self.assertIn("4 untested asteroids", root.find("dl", cls="lmeta")[0].text())
        # a window kind heads its rows, with its count
        recs = [dataclasses.replace(r, observe=dict(r.observe, tier="pointable")) if r.observe else r for r in sample.RECORDS]
        page = parse(gen.observe_page([dataclasses.asdict(r) for r in recs], srcs(), sample.ASSETS, sample.DATA_DATE,
                                      sample.METHOD)).root
        (tier,) = [tr for tr in page.find("tr") if "tier" in tr.classes]
        self.assertEqual(tier.text(gap=" "), f"{gen.TIER_HEADS['pointable']} 4 asteroids")

    def test_lists_print_no_size_from_a_source_that_is_not_open(self):
        """docs/mvp.md section 3: a value from a "single" source is shown on the asteroid's own page, with its
        citation. A list follows the field file's rule instead: JPL's diameter, else the range from brightness."""
        self.assertTrue(export.OPEN_SIZES_ONLY)
        withheld = 0
        def cell(r):        # the mark's state in words, as a reader that does not see it hears it, then the text
            root = parse(gen.size_cell(dataclasses.asdict(r), srcs())).root
            return ", ".join(x for x in (root.find("i", cls="g")[0].attrs.get("aria-label"), root.text()) if x)
        for r in sample.RECORDS:
            own = t.size_of(dataclasses.asdict(r), srcs())
            if own and own["state"] != "prior" and sample.SOURCES[own["source"]].licence != "open":
                withheld += 1
                self.assertNotIn(t.num(own["mid"], 3), cell(r).replace(t.num(own["mid"], 2), ""), r.designation)
        self.assertGreaterEqual(withheld, 3)
        by = {r.designation: cell(r) for r in sample.RECORDS}
        self.assertEqual(by["2099 AA37"], "Measured, on entry")                 # nothing open on the record
        self.assertEqual(by["2099 RQ36"], "Measured, 492")                      # JPL's own diameter
        self.assertEqual(by["2099 KY26"], "Measured, 5.2–21")                   # the field file's range, dimmed
        self.assertIn('title="Placed by brightness', gen.size_cell(dataclasses.asdict(self.by_key["s0000007"]), srcs()))
        self.assertEqual(by["2099 NJ"], "Limit only, on entry")
        self.assertEqual(by["2099 OB5"], "Not measured, 3.1–13")                # our own range: as on the entry
        page = self.pages["list/observe.html"]
        for sid, s in sample.SOURCES.items():
            if s.licence != "open":
                self.assertNotIn(f">{s.name}<", page)
        # the entry still shows the measured value, with its citation
        self.assertIn("65 m", self.rows("s0000002")["size"].text())
        self.assertIn("Example and Other 2098", self.rows("s0000002")["size"].text())
        # one switch for the field file and the lists
        with mock.patch.object(export, "OPEN_SIZES_ONLY", False):
            self.assertIn(">65<", gen.size_cell(dataclasses.asdict(self.by_key["s0000002"]), srcs()) + "<")

    def test_observe_order_is_the_methods(self):
        """Equal gains are common (1,736 of 1,956 rows shared one). The order printed, and so each rank, is
        observe.ranked's, whatever method/v0_1/observe.toml [rank] says: the generator has no order of its own."""
        base = {r.key: r for r in sample.RECORDS}
        def with_gain(key, gain, start, dv):
            r = base[key]
            window = {"start": start, "end": "2030-01-01", "peak_mag": 20.0, "pointable": True, "as_of": sample.DATA_DATE}
            rows = dict(r.rows, reach=sample._reach(dv, 360))
            return dataclasses.replace(r, rows=rows, observe=dict(r.observe, gain=gain, window=window if start else None))
        recs = [with_gain("s0000008", 0.5, "2029-06-01", 4.0),      # the cheapest to reach, and the latest window
                with_gain("s0000001", 0.5, "2027-01-01", 9.0),
                with_gain("s0000003", 0.5, None, 5.0),
                with_gain("s0000002", 0.5, "2027-01-01", 6.0),
                base["s0000004"]]
        want = [r.designation for r in observe.ranked([r for r in recs if r.observe])]
        by_dv = [r.designation for r in sorted((r for r in recs if r.observe), key=lambda r: r.rows["reach"].facts[0].value)]
        self.assertNotEqual(want, by_dv)                             # the old tie-break would print another order
        self.assertEqual(want[0], "2099 OB5")                        # earliest window; the key breaks the tie with AA37
        with tempfile.TemporaryDirectory() as d:
            gen.write_site(recs, sample.SOURCES, d, sample.ASSETS)
            body = parse((Path(d) / "list" / "observe.html").read_text(encoding="utf-8")).root.find("tbody")[0]
            rows = [tr for tr in body.find("tr") if not tr.classes & {"tier", "run"}]
            self.assertEqual([tr.find("a")[0].text() for tr in rows], want)
            self.assertEqual([tr.find("td")[0].text() for tr in rows], ["1", "2", "3", "4"])

    def test_record(self):
        root = self.trees["record.html"].root
        rows = root.find("tbody")[0].find("tr")
        self.assertEqual(len(rows), len(sample.PREDICTIONS))
        text = [tr.text() for tr in rows]
        self.assertIn("not yet", text[0])
        self.assertIn("81%", text[0])
        self.assertIn("2027-02-20 to 2027-04-11", text[0])
        self.assertIn("open", [td.text() for td in rows[0].find("td")])
        self.assertIn("inside: 9 of 14", text[2])
        self.assertEqual(rows[0].find("a")[0].attrs["href"], "a/s0000008.html")
        meta = {dt.text(): dt.parent.find("dd")[0].text() for dt in root.find("dl", cls="lmeta")[0].find("dt")}
        self.assertEqual(meta, {"Predictions": "3", "Frozen": "2", "Settled": "1"})

    def test_record_prints_a_family_of_rules_as_one_grid(self):
        preds = predictions.predictions()
        m = method.load()
        bands, classes, spins = m.priors["bands"]["ids"], m.priors["class"]["ids"], m.priors["spin"]["ids"]
        page = gen.record_page(preds, set(), sample.ASSETS, sample.DATA_DATE, sample.METHOD)
        tree = parse(page)
        self.assertEqual(tree.errors, [])
        root = tree.root
        meta = {dt.text(): dt.parent.find("dd")[0].text() for dt in root.find("main")[0].find("dl")[0].find("dt")}
        self.assertEqual(meta, {"Predictions": str(len(preds)), "Frozen": "none", "Settled": "0"})
        grids = root.find("table", cls="grid")
        self.assertEqual(len(grids), 2)                                   # class by band, spin by band
        for grid, columns in zip(grids, (classes, spins)):
            self.assertEqual(len(grid.find("tbody")[0].find("tr")), len(bands))
            heads = grid.find("thead")[0].find("tr")[-1].find("th")
            self.assertEqual(heads[0].text(), "H, mag")                  # the rows' column is headed, with its unit
            self.assertEqual(len(heads), len(columns) + 1)
        self.assertEqual(grids[1].find("th", cls="over")[0].text(), "Faster than")
        # label headings, not sentences; the statement once, as a line under it; each chance keeps its id as an anchor
        heads = [h.text() for h in root.find("h2")]
        self.assertLessEqual({"Class, by brightness", "Spin, by brightness"}, set(heads))
        self.assertEqual(root.find("i"), [])
        self.assertEqual(page.count("gets a class gets each one"), 1)
        ids = {n.attrs["id"] for n in root.walk() if "id" in n.attrs}
        self.assertLessEqual({p["id"] for p in preds}, ids)
        by_id = {p["id"]: p for p in preds}
        (cell,) = root.find("td", id=f"rule-class-{bands[2]}-S")
        self.assertTrue(cell.text().startswith(t.pct(by_id[f"rule-class-{bands[2]}-S"]["p"])))
        self.assertEqual(cell.parent.find("th")[0].text(), "22 to 24")
        self.assertEqual(grids[0].find("thead")[0].find("tr")[-1].find("th")[1].text(), "S or Q")
        self.assertEqual(grids[1].find("thead")[0].find("tr")[-1].find("th")[1].text(), "2.2 hours")
        # what settles a family is said once, beside its grid; nothing says "not yet frozen" 51 times
        self.assertEqual(page.lower().count("class labels published after the freeze"), 1)
        self.assertNotIn("not yet", page)
        self.assertNotIn(">open<", page)
        # the rest are one to a line: a size per band, then the single asteroids
        self.assertEqual(len(root.find("table", cls="flat")[0].find("tbody")[0].find("tr")),
                         len(preds) - len(bands) * (len(classes) + len(spins)))
        # a family with a frozen member goes back to one line each, with the column that says so
        frozen = [dict(p, frozen="2026-12-01") if p["id"] == f"rule-class-{bands[0]}-S" else p for p in preds]
        again = parse(gen.record_page(frozen, set(), sample.ASSETS, sample.DATA_DATE, sample.METHOD)).root
        self.assertEqual(len(again.find("table", cls="grid")), 1)
        self.assertIn("Frozen", [th.text() for th in again.find("table", cls="flat")[0].find("th")])

    def test_method(self):
        root = self.trees["method.html"].root
        text = root.find("main")[0].text()
        self.assertIn(f"version {sample.METHOD}", text)
        for sid, s in sample.SOURCES.items():
            row = root.find("tr", id=f"src-{sid}")[0].text()
            self.assertIn(t.source_name(srcs(), sid), row)
            self.assertIn(s.edition, row)
            self.assertIn(s.citation, row)
        for line in gen.NOT_CLAIMED:
            self.assertIn(line, text)
        self.assertIn("A dollar figure appears only as a range", text)
        self.assertNotIn("No water for a small reachable asteroid", text)
        self.assertIn("a miss is listed the same way as a hit", text)
        # the states, with the marks every page uses
        (states,) = root.find("section", id="states")
        self.assertEqual([tag.text() for tag in states.find("table")[0].find("span", cls="st")], list(t.STATE_WORDS.values()))
        self.assertIn("never reads as not measured", states.text())
        for a in root.find("nav", cls="toc")[0].find("a"):
            self.assertEqual(len(root.find(id=a.attrs["href"][1:])), 1)

    def test_method_gives_every_threshold_and_where_it_comes_from(self):
        """Every fixed figure an entry prints is on method.html with its source, read from method/v0_1."""
        m = method.load()
        root = self.trees["method.html"].root
        (main,) = root.find("main")
        text = main.text(gap=" ")
        for mid in m.missions["order"]:
            for g in m.missions[mid]["gates"]:
                (block,) = main.find("div", id=f"g-{mid}-{g['id']}")
                said = block.text(gap=" ")
                self.assertIn(g["label"], said)
                self.assertIn(t.num(g["preset"]), said)
                # where it comes from, as the file gives it less what only points into the project
                self.assertIn(gen._public(g["source"]), said)
                self.assertIn(g["kind"], said)
                for alt in g.get("alternatives", []):
                    self.assertIn(gen._public(alt["what"]), said)
                if g.get("caveat"):
                    self.assertIn(gen._public(g["caveat"]), said)
        self.assertIn("No source states a minimum size for working a surface", text)
        # no path into the project, no file name, no brackets, kg/m³ written out
        for word in ("docs/", "data/", "tools/", "AGENTS.md", ".toml", ".py", "kg/m3", "build/"):
            self.assertNotIn(word, text, word)
        self.assertIn("top of that one design's range, not a limit", text)
        for words in ("160 m", "the smallest body any spacecraft has touched is Dimorphos",
                      "$2.6 billion, 2012 dollars", "3.01 h", "1.82 h", "USGS Mineral Commodity Summaries 2026",
                      "Horan et al. 2003", "Shepard et al. 2015", "7,500 kg/m³", "Rotation lightcurve"):
            self.assertIn(words, text)
        for rung in m.ladder["meta"]["order"]:
            self.assertEqual(len(main.find(id=f"rung-{rung}")), 1)
        for anchor in ("thresholds", "m-surface", "m-capture", "ladder", "value", "observe", "density"):
            self.assertEqual(len(main.find(id=anchor)), 1, anchor)
        self.assertIn("https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-platinum-group.pdf",
                      [a.attrs["href"] for a in main.find("a")])
        gate = dict(m.missions["surface"]["gates"][1], cite="Michel 2018, ASIME")
        said = parse(gen._gate("surface", gate)).root.text()
        self.assertIn("Michel 2018, ASIME", said)
        self.assertNotIn(gate["source"], said)

    def test_method_lists_what_counts_as_measured(self):
        """The ledger's thresholds live in method/v0_1/ledger.toml; the page prints each with its source."""
        m = method.load()
        (main,) = self.trees["method.html"].root.find("main")
        said = main.text(gap=" ")
        led = m.ledger
        self.assertEqual(len(main.find(id="ledger")), 1)
        self.assertEqual(len(main.find("div", id="l-period-min_grade")), 1)
        self.assertIn(gen._public(led["period"]["min_grade_source"]), said)
        self.assertIn(t.num(led["push"]["detection_sigma"]), main.find("div", id="l-push-detection_sigma")[0].text())
        self.assertIn("Lightcurve grade, lowest counted", said)            # a label for a visitor, not a key
        self.assertEqual(said.count(gen._public(led["push"]["source"])), 1)  # a table's shared source, once
        self.assertIn(t.cap(led["fixed_tables"]["reason"]), said)
        for bad in led["known_bad"]:
            self.assertIn(gen._public(bad["why"]), said)
        made = dataclasses.replace(m, ledger={"radar": {"min_snr": 7.5, "kind": "judgement", "source": "a note"},
                                              "gone": [{"designation": "2099 TC3", "text": "It hit.", "evidence": "a file"}]})
        text = parse(gen._ledger(made)).root.text(gap=" ")
        for words in ("Radar, min snr", "7.5", "judgement", "a note", "Gone: 2099 TC3", "It hit.", "a file"):
            self.assertIn(words, text)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gen._ledger(types.SimpleNamespace(path=d)), "")


class StyleTest(unittest.TestCase):
    """The look's hard rules, read off the stylesheet itself."""

    def test_no_hue(self):
        colours = re.findall(r"#[0-9a-fA-F]{3,8}\b", CSS)
        self.assertGreater(len(colours), 5)
        for c in colours:
            h = c[1:]
            parts = [h[i] * 2 for i in range(3)] if len(h) in (3, 4) else [h[i:i + 2] for i in (0, 2, 4)]
            self.assertEqual(len(set(parts)), 1, f"{c} is not a grey")
        self.assertIsNone(re.search(r"\b(rgb|hsl|oklch|lab)a?\(", CSS))

    def test_one_face_one_weight(self):
        self.assertEqual(CSS.count("@font-face"), 1)
        urls = re.findall(r"url\(([^)]*)\)", CSS)
        self.assertEqual([u for u in urls if not u.startswith('"data:image/svg+xml,')], ["fonts/b612-regular.woff2"])
        self.assertIn("font-display: swap", CSS)
        self.assertIn('--sans: "B612", system-ui,', CSS)          # a system face while it loads, or if it never does
        self.assertEqual(set(re.findall(r"font-weight:\s*([^;}]+)", CSS)), {"400"})
        self.assertIn("font-synthesis: none", CSS)
        self.assertNotIn("monospace", CSS)

    def test_none_of_what_the_design_rules_out(self):
        for banned in ("box-shadow", "text-shadow", "@import", "blur("):
            self.assertNotIn(banned, CSS)
        self.assertEqual(set(re.findall(r"border-radius:\s*([^;]+);", CSS)), {"0"})
        # the glow means measured: only the measured and pass marks and outlines carry it
        self.assertEqual([x.strip() for x in re.findall(r"([^{}]+)\{[^}]*filter: var\(--glow\)", CSS)], [".g-measured, .g-pass"])

    def test_motion_and_states(self):
        self.assertIn("@media (prefers-reduced-motion: reduce) { .turn { animation: none; } }", CSS)
        self.assertRegex(CSS, r"\.g-limit \{[^}]*stroke-dasharray")
        self.assertRegex(CSS, r"\.g-unchecked, \.g-unknown \{[^}]*stroke-dasharray")
        self.assertRegex(CSS, r"\.g-prior \{[^}]*fill='%238a8a8a'")                 # --ink-3
        self.assertNotIn("animation-duration", CSS)     # the period comes from the page, uncapped
        self.assertIn("[hidden] { display: none !important; }", CSS)

    def test_scale_of_type(self):
        sizes = set(re.findall(r"font:\s*var\(--(t-[a-z]+)\)", CSS))
        self.assertLessEqual(sizes, {"t-xs", "t-s", "t-m", "t-l", "t-xl", "t-serif"})
        steps = dict(re.findall(r"--(t-[a-z]+): ([^;]+);", CSS))
        self.assertEqual(sorted(steps), ["t-l", "t-m", "t-s", "t-serif", "t-xl", "t-xs"])

    def test_nothing_round(self):
        self.assertIn("::-webkit-slider-thumb", CSS)
        self.assertIn("::-moz-range-thumb", CSS)


class FormatTest(unittest.TestCase):
    def test_num(self):
        self.assertEqual(t.num(7229), "7,229")
        self.assertEqual(t.num(0.0257), "0.0257")
        self.assertEqual(t.num(92.5234), "92.52")
        self.assertEqual(t.num(-4.6e-14), "−4.6 × 10⁻¹⁴")
        self.assertEqual(t.num(9.99996e-14), "1 × 10⁻¹³")
        self.assertEqual(t.num(0), "0")
        self.assertEqual(t.num(None), "")
        self.assertEqual(t.num(float("nan")), "")
        self.assertEqual(t.num(True), "")

    def test_pct_never_rounds_to_certainty(self):
        self.assertEqual(t.pct(0.004), "under 1%")
        self.assertEqual(t.pct(0.0049), "under 1%")
        self.assertEqual(t.pct(0.005), "1%")           # 10 of 2,000 draws: it was printed as 0%
        self.assertEqual(t.pct(0.0051), "1%")
        self.assertEqual(t.pct(0.025), "3%")           # halves round up, not to the even digit
        self.assertEqual(t.pct(0.997), "over 99%")
        self.assertEqual(t.pct(0.995), "over 99%")
        self.assertEqual(t.pct(0.9949), "99%")
        self.assertEqual(t.pct(0), "0%")
        self.assertEqual(t.pct(1), "100%")
        self.assertEqual(t.pct(0.415), "42%")
        self.assertEqual(t.pct(0.29), "29%")
        for n in range(0, 2001):                       # every share 2,000 draws can give
            p = n / 2000
            self.assertRegex(t.pct(p), r"^(under 1|over 99|\d+)%$")
            if 0 < n < 2000:
                self.assertNotIn(t.pct(p), ("0%", "100%"), n)

    def test_a_chance_from_draws_is_never_0_or_100(self):
        self.assertEqual(t.chance(0), "under 1%")
        self.assertEqual(t.chance(0.0), "under 1%")
        self.assertEqual(t.chance(1), "over 99%")
        self.assertEqual(t.chance(0.005), "1%")
        self.assertEqual(t.chance(0.41), "41%")
        self.assertEqual(t.chance(None), "")
        for n in range(0, 2001):
            self.assertNotIn(t.chance(n / 2000), ("0%", "100%"), n)

    def test_units(self):
        self.assertEqual(t.scale_for("spin", "period", "h", 0.0257), (60 * 60, "s"))
        self.assertEqual(t.scale_for("spin", "period", "h", 0.1784)[1], "min")
        self.assertEqual(t.scale_for("spin", "period", "h", 10.0), (1.0, "h"))
        self.assertEqual(t.scale_for("tracking", "observed over", "d", 0.01), (1.0, "d"))
        self.assertEqual(t.scale_for("size", "diameter", "m", 1600), (0.001, "km"))
        self.assertEqual(t.scale_for("surface", "albedo", "", 0.11), (100.0, "%"))
        self.assertEqual(t.span(-1.9e-13, -0.94e-13, "au/d²"), "−1.9 × 10⁻¹³ to −9.4 × 10⁻¹⁴\u00a0au/d²")
        self.assertEqual(t.usd(1.4e7), "$14\u00a0million")
        self.assertEqual(t._seconds(36000), "36000s")

    def test_amount_puts_both_ends_in_one_scale(self):
        self.assertEqual(t.amount(71000, 3.6e6, "t"), "0.071–3.6\u00a0million\u00a0t")
        self.assertEqual(t.amount(5.8e7, 1.4e8, "t"), "58–140\u00a0million\u00a0t")
        self.assertEqual(t.amount(26, 190, "t"), "26–190\u00a0t")
        self.assertEqual(t.amount(4e8, 2.1e9, "kg"), "0.4–2.1\u00a0billion\u00a0kg")
        self.assertEqual(t.span(23.88, 24.5, "mag"), "23.88–24.50\u00a0mag")      # both ends to the same decimals
        self.assertEqual(t.span(0.83, 3, "m", 2), "0.83–3\u00a0m")

    def test_unreliable(self):
        self.assertTrue(t.unreliable("1"))
        self.assertTrue(t.unreliable("1+"))
        self.assertTrue(t.unreliable("1-"))
        self.assertFalse(t.unreliable("2-"))
        self.assertFalse(t.unreliable("3"))
        self.assertFalse(t.unreliable(None))
        self.assertFalse(t.unreliable("NEATM"))

    def test_rel(self):
        self.assertEqual(t.rel("static/style.css", 1), "../static/style.css")
        self.assertEqual(t.rel("static/style.css", 0), "static/style.css")
        self.assertEqual(t.rel("/static/style.css", 1), "/static/style.css")
        self.assertEqual(t.rel("https://example.org/s.css", 1), "https://example.org/s.css")

    def test_timeline_starts_at_the_data_date(self):
        tl = parse(t.timeline("2027-02-12", "2027-07-15", "2026-11-24")).root
        self.assertEqual(tl.find("i", cls="d0")[0].text(), "2026-11-24, data date")
        self.assertEqual(tl.find("i", cls="win")[0].text(), "Window 2027-02-12 to 2027-07-15")
        # a year mark too close to the data date's label goes unlabelled
        self.assertEqual([y.text() for y in tl.find("i", cls="yr") if "d0" not in y.classes], ["", "2028"])
        self.assertEqual(t.timeline("x", "y", "2026-11-24"), "")


if __name__ == "__main__":
    unittest.main()
