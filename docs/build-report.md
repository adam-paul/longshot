# Build report: the prototype

Written 2026-11-25, after the review round; brought up to date the same day, after the instrument redesign (`docs/design.md`) and the repository cleanup (`docs/cleanup-2026-11-25.md`). Data date 2026-11-24, method 0.1. Every number below is from `build/build.log`, `build/tests.log`, `build/screens/dist-gpu.txt`, `build/screens/dist-software.txt`, or a count over `build/records.jsonl` and `dist/`, all from the run of 25 November after the cleanup.

## 1. What it does

```
uv run python -m longshot build      # 52 s, no network
uv run python -m longshot serve      # http://127.0.0.1:8000/
uv run python -m unittest discover -s tests -t .
uv run python tools/browser_check.py dist --gl gpu
```

One command reads the data on disk and writes `build/ledger.jsonl`, `build/records.jsonl` and the site under `dist/`.

| Stage | Module | Time |
|---|---|---|
| Seven sources into six rows per asteroid | `longshot/ingest/`, `ledger.py` | 3.9 s |
| Priors, missions, what to observe, value, ladder, record check | `model.py` and the stages it runs, `contract.py` | 43.0 s |
| Field file, keys file, 7,235 pages, three static files and the font | `export.py`, `site/gen.py`, `__main__.py` | 5.4 s |

The site:

- **Front page.** A field of 7,225 rocks, delta-v across, size up, in one WebGL2 draw call, with zoom from 1x to 32x; or the same selection as a sortable table. A control strip (View, Mission, Delta-v ceiling, Find asteroid, the count) filters both. The readout beside it lists the named asteroids, one typical asteroid with nothing measured, and the rows by state; a click on a rock or a name puts that asteroid's summary there. State is in the URL.
- **An entry per asteroid** (7,231): the summary list beside the rock drawn to scale, then six rows in four states each on its own scale with the mission gates, the difficulty ladder, what is in it, what would settle it, two missions gate by gate, sources.
- **What to observe next**: one list in rank order.
- **The record**: 51 predictions, none frozen.
- **The method page**: states, every threshold with what it was chosen from and where it comes from, what has flown, sources, what is not claimed.

## 2. Counts

7,231 reachable asteroids (JPL's list of 24 November; it held 7,229 on 21 November).

| Row | measured | limit | not measured | not checked |
|---|---|---|---|---|
| reach | 7,231 | 0 | 0 | 0 |
| tracking | 7,231 | 0 | 0 | 0 |
| size | 185 | 0 | 6,873 | 173 |
| spin | 378 | 11 | 4,797 | 2,045 |
| surface | 373 | 0 | 6,685 | 173 |
| sunlight push | 176 | 0 | 6,883 | 172 |

- **Why so many rows are "not checked".** SsODNet now holds a card for 7,058 asteroids and does not know 173; no request is outstanding (the retry of 25 November fetched 19 and got one 404). The 173 size rows not checked are the asteroids SsODNet does not know. Asteroids found after the Spitzer surveys ended are counted as absent from its final table, not as unchecked (`method/v0_1/ledger.toml` `[closed_tables]`, added after the review round). Of the 2,045 spin rows not checked, 1,929 are so only because the lightcurve database (2023-10-01) is older than the asteroid.
- 210 asteroids carry a value on file and not used. 43 rows carry a conflict between sources: 17 spin, 12 push, 11 size, 3 surface.
- 6 asteroids have no brightness on file, so no size, no rock and no estimate. One, 2008 TC3, no longer exists.

| Mission | pass | untested | fail |
|---|---|---|---|
| surface work | 61 | 1,954 | 5,216 |
| whole-body capture | 2 | 2,019 | 5,210 |

- 2,102 asteroids have an observation ranked: 1,393 with a window a telescope can be pointed at, 136 survey-only, 573 with no window through 2045. For 736 of them a source for the row was not checked.
- 51 predictions on the record, none frozen.
- 7,235 pages: 7,231 entries, the observe list, the record, the method page, the front page.

## 3. Sizes

First screen, 8 requests, in the order of `build/build.log`:

| File | Bytes | Gzipped |
|---|---|---|
| `index.html` | 7,943 | 2,385 |
| `static/style.<hash>.css` | 43,681 | 8,969 |
| `static/fonts/b612-regular.woff2` | 12,620 | 12,643 |
| `static/app.<hash>.js` | 38,186 | 13,807 |
| `static/field.<hash>.js` | 28,094 | 10,211 |
| `data/field.json` | 2,549 | 728 |
| `data/field.<hash>.bin`, 7,225 rocks in 15 columns | 224,002 | 108,081 |
| `data/keys.<hash>.json`, fetched after the first frame | 232,419 | 69,705 |
| **Total** | **589,494** | **226,529** |

Before the review: 627,703 bytes, 290,717 gzipped. After the review and before the redesign: 498,727 bytes, 197,488 gzipped. The redesign added the font, the table view, zoom and the readout's lists, and three columns to the field file.

| Page | Bytes | Gzipped | Rows |
|---|---|---|---|
| One entry, median (smallest 18,021, largest 33,303) | 28,257 | 5,489 | |
| All entries | 204,759,551 | 39,687,722 | |
| `list/observe.html` | 923,453 | 74,231 | 2,102 |
| `record.html` | 11,269 | 2,311 | |
| `method.html` | 41,290 | 12,524 | |
| `dist/`, 7,243 files | 206,329,527 | | |

Bytes are file sizes, counted by the build and again by the browser check from what the server sent. Gzipped sizes are computed at level 6; `serve` does not compress.

## 4. Frame times

Headless Chromium, 1440 x 900, device pixel ratio 1, every rock on screen, 4 seconds, run after the tests had finished. "Draw" is timed until the GPU reports the frame done. "Back to back" is a loop of draws with no wait between them.

| Renderer | Rocks | Draw calls | Draw, median / p95 | Frame to frame, median / p95 | Back to back |
|---|---|---|---|---|---|
| GPU: NVIDIA RTX 5060 Ti, ANGLE on Vulkan | 7,225 | 1 | 0.5 / 0.7 ms | 16.7 / 16.8 ms | 0.048 ms |
| Software: SwiftShader | 7,225 | 1 | 67.1 / 70.0 ms | 66.7 / 83.3 ms | 65.3 ms |

- On the GPU the field holds 60 frames a second with every rock drawn, the glow included: it is part of the same draw.
- In software it reaches about 15. Nothing turns unasked there, so the page redraws only on input.
- Unasked, on the GPU: 3 frames a second at the home view, where 264 rocks turn, and 11 zoomed on the fastest. A hidden tab draws none.
- The field fixer measured 43,000 synthetic rocks at 0.6 ms a draw on the GPU. Not rerun here.

## 5. Checks

- **Tests:** `Ran 527 tests in 128.262s`, `OK (skipped=1)` (`build/tests.log`). The skipped one is the optional full-run byte comparison in `tests/test_export.py`; `tests/test_build.py` covers it.
- **End to end** (`tests/test_build.py`): builds every asteroid twice, in two processes with different hash seeds. It reads the research snapshot's 1,704 SsODNet cards alone, so its inputs do not change under it, and asserts no global count.
- **Browser:** 72 checks pass on the GPU and 72 in software, console clean; one is skipped on both ("a limit's outline": no rock has only a limit on its size). They cover the draw call count, the marks (the glow on measured rocks only, dots that become outlines at 4x, the ring for not checked), the tip, zoom and pan by wheel, drag, buttons, keys and pinch, the axes, the legend's counts, the mission filter and the ceiling, the readout and its Close, search by designation, name and number, the asteroids with no rock, the table view (pages, sorting, filters), the keyboard, history, touch at phone width, reduced motion, a hidden tab, a lost context, a change of pixel ratio, a keys file that does not load, and a browser without WebGL2. The synthetic site (`tools/make_synthetic_field.py`) passes the same 72.
- **Field file:** `tools/make_synthetic_field.py --check dist/data/field.json` prints `ok`.
- **Method files:** `tools/method_check.py` passes 380 of 380; the `--check` runs of `method_priors_toml.py`, `method_doc_tables.py`, `method_missions.py` and `checksum_tables.py` pass.

## 6. Fixture objects

States in the build of section 2. All match `tests/fixtures.py`.

| Asteroid | size | spin | surface | push | surface work / capture |
|---|---|---|---|---|---|
| 2011 AA37 | not measured | not measured | not measured | measured | untested / untested |
| 2009 BD | measured | not measured | not measured | measured | fail / pass |
| 2022 OB5 | not measured | measured | measured | measured | fail / untested |
| 2026 QQ8 | not checked | not checked | not checked | measured | untested / untested |
| 2020 CD3 | not measured | measured | measured | measured | fail / untested |
| 2010 CW266 | not checked | not checked | not checked | not checked | fail / fail |
| Kamoʻoalewa | measured | measured | measured | measured | fail / fail |
| Bennu | measured | measured | measured | measured | pass / fail |
| 2010 NU71 | not measured | not measured | not measured | not measured | fail / fail |
| 2013 NJ | not measured | measured | measured | not measured | untested / untested |
| 2023 RA4 | not measured | measured | not measured | not measured | untested / untested |
| 1999 AO10 | not measured | measured | not measured | measured | untested / untested |
| 2001 CQ36 | measured | not measured | measured | measured | untested / fail |

- 2011 AA37's 10-hour period is on its page from three sources, graded unreliable and not used; the row is not measured and the rock does not turn.
- 2022 OB5 turns once in 92.52 s on its entry, from the hand-entered list (Alarcon et al. 2026). Its size is not measured.
- Kamoʻoalewa's own entry now gives the 18 ± 2 m the other entries cite.
- 2009 BD's computed reflectivity is printed dim, marked "computed, not used".
- 2026 QQ8 and 2010 CW266 name each source not checked and why, and never say "not measured".
- 2010 NU71's 1,126 m is on its page, not used, with the reason.
- 2013 NJ shows both periods and one conflict sentence; its spin gate is untested, since the two fall either side of 2.2 hours.
- Bennu and Ryugu report the returned sample in place of class odds. 2008 TC3 says it no longer exists, does not turn, and carries no estimate.

## 7. How each "done when" line was checked

| Line in `docs/mvp.md` section 8 | Status | Checked by |
|---|---|---|
| One command builds the whole site from the data on disk, with no network | met | One `build`: 7,235 pages in 52 s. Nothing under `longshot/` imports a client library; `http.server` serves local files. |
| The fixture objects show the right values | met | `test_fixture_objects_show_their_values_on_their_pages` reads 13 entries from a full build: state, sources not checked, every fact's value, range, grade and source, conflicts. |
| The field holds its frame rate with every asteroid drawn | met on the GPU, not in software | Section 4: 16.7 ms frame to frame on the GPU; about 15 frames a second in SwiftShader. |
| Every number on a page traces to a source or a script output | partly | Every fact in a row prints its source (test over the sample records). Every threshold links to `method.html`, which prints its basis; a test checks each constant in the method files names where it came from and that the file exists. No test ties each figure in a value sentence to the draw behind it. Most bases cite files under `docs/research`, not public papers. |
| "Not checked" never shows as "not measured" | met | `test_no_row_with_an_unchecked_source_says_not_measured` reads all 7,231 entries: each row, the rock's caption and label, and every sentence under the rows. `contract.check` rejects such a record. The browser check reads the field's tip. No list prints the phrase. |
| Every page shows its data date | met | `test_no_page_says_open_now_and_every_page_prints_the_data_date` reads every page of a full build. |

## 8. What the screenshots show

The site was rebuilt on 25 November to the instrument design (`docs/design.md`), after Adam judged the first build "somewhat hideous". `build/screens/port-final/` holds 20 shots of the rebuilt site: the front page in the chart and table views, with 2026 HT and Apophis selected, at 390, 1024, 1280, 1440 and 1920 px wide; the entries of 2026 HT, Apophis, 2008 TC3 and Bennu; the observe list, the record and the method page. `build/screens/dist-gpu-*.png` and `dist-software-*.png` are the browser check's own 13 shots each (home, zoomed to 4x and 32x, a mission, the ceiling, a selection and Close, the table view, the phone, no WebGL2).

Against Adam's words:

- **"Asteroids" the game, white on black.** Measured rocks are white outlines with a faint glow; the 6,873 unmeasured are grey dots at the home view and dim outlines from 4x zoom. The header carries a rock mark. No hue anywhere. The rocks do not move across the screen; 264 turn in place.
- **"No extraneous text, or excessive subtitles."** The front page's only words are labels, names, counts and units; the headline sentence is gone. The mission names appear once, as the strip's filter. The method page is still long, and prints the method files' own notes.
- **"Don't want default Claudeslop."** No accent colour, cards, gradients, icons or rounded corners; one face in one weight; sentence-case labels.
- **"Realism... error bars... extreme uncertainty."** Nine rocks in ten are grey dots; every size in the table carries its state's glyph, so an estimate never reads as a measurement; an unmeasured size leads with its range; the last rung says what has and has not been done, dated.
- **"Conservative estimates with well-researched large error bars."** The price tag gives the chance of nothing first, as counts of 100 beside one-sided rows in kilograms with dollars. No middle figure is printed or stored.
- **"The most performant website possible."** 227 kB gzipped to the first screen, one draw call, 0.5 ms a frame on a GPU. The field file is 48% of that, the names 31% and the font 6%.

Still weak in the screenshots:

- Between 5 and 50 m and above 8 km/s the rocks overlap at the home view. One can be picked there only after zooming.
- On a phone the strip takes about 380 px before the chart starts.
- The entry's fact tables wrap long method notes into a narrow column (`docs/design.md` section 8).
- From the review round, not rechecked: 2008 TC3's entry says what happened to it in several places (the tracking row, the first rung and one gate of each mission).

## 9. Where the build departs

From `DESIGN.md`:

- **Section 4, "nothing drawn for not checked".** Entry rows follow it. The field draws those rocks as a dashed ring, so every asteroid can be found; this is the instrument design's mark (`docs/design.md` section 3).
- **Section 6, "drawn as a line figure to scale".** The entry's rock is to scale, with a scale bar. The field's rocks are glyphs of a fixed size, as the instrument design draws them; to scale, all but 23 were dots at the home view (section 12, item 1).
- **Section 6, turning.** 378 spins are measured. 360 rocks turn on their entries, and 264 in the field, which may carry only JPL's periods. The rest do not turn because their sources disagree. 2022 OB5 turns on its entry and not in the field.
- **Section 7, "Nobody buys water in orbit."** The page says "As of 21 November 2026 we found nobody buying water in orbit", after `verify-capability.md` objection 14.
- **Section 7, corrections first.** `verify-value-inputs.md` objection 8 is applied in part: the iron-rich row still prints dollars, from two metal mixes chosen by judgement. A note under the price tables says so.
- **Section 8, browser storage.** None is used. All state is in the URL.
- **Section 8, "it carries only JPL values and our own derived ones".** Kept. So 116 rocks whose size is measured only by SsODNet, Spitzer or the hand-entered list are placed by brightness, and their tip reads "size measured: see entry".

From `docs/mvp.md` as it stood before the review (sections 9 and 10 there list each change):

- The field file has 15 columns, not 20, and the keys file is not preloaded.
- The four mission lists are gone; the front page's table view replaces them.
- `has-field` is set on the page once the field runs; it styles nothing, and the browser check reads it.
- A gate is decided at two sigma, not by the stated range.
- Two fixed tables (the lightcurve database, Pravec's) are "not checked" for asteroids found after their edition; the finished Spitzer surveys count as absent.

The repository is on GitHub (github.com/adam-paul/longshot); the built site is not published.

## 10. Review findings not fixed

The review raised 108 findings. These are open; the rest are fixed and tested, or were overtaken by the redesign (the front sentence, the entry's single column, the controls over the data).

| Finding | Why not |
|---|---|
| `other-class-pooled` | A measured V, A or D class is still drawn as "other". Wording is fixed: no sentence says "its class (D)". The draw needs reflectivity tables for those classes, which is a new derivation from Spitzer on a handful of objects. 42 entries, by the pipeline fixer's count. |
| `field-narrow-columns` | `seed` is 16 bits. A 16-bit delta-v would save about 6,000 gzipped bytes, under 3% of the first screen, and needs a scale factor in the manifest and a decode step in three readers. |
| `scripts-not-minified` | Stripping comments and indentation would save a few thousand gzipped bytes. A stripper written in the standard library would have to parse the shader strings; a wrong cut breaks the field. |
| `hosting-headers` | No host is chosen (`DESIGN.md` section 8). `serve` sends the right cache headers; a static host needs its own file. |
| `field-brightness-ignores-surface-and-push` | Adam's call (section 12, item 8). The tip names every measured row. |
| `copy-contradictions`, method page sources | Fixed, except that the method files carry no public citation beside a source that names only a project file. `method.html` prints `cite` where a file gives one; none does yet. |

## 11. Known to be weak

- **The validation protocol of `docs/plan.md` Appendix A has not been run.** No held-out size check. The reflectivity table is fitted on all 1,576 Spitzer objects.
- **Thresholds are proposals.** The two-sigma rule, the factor of 2 for a size with no error, and the class label error (21% from colours; 12.5% otherwise, from "at least 3 of 24") were set in the review round.
- **The method page** is the method files printed. Complete, and hard to read.
- **Only headless Chromium was tested.** No Firefox, no Safari, no real touch screen; pinch zoom is untested on a device.
- **The model takes 43 s** in one process. It could be split across cores.
- **Entries total 205 MB** (40 MB gzipped), 28 kB each at the median.
- **Lightcurve-database values** are never printed: 304 spin rows carry a line that reads "on file, not shown here".
- **Apophis's spin row** holds 27.385 h (SsODNet) and 30.56 h (the lightcurve database and JPL), both used, with no conflict recorded. The entry prints 30.56 h. A 10% disagreement between two used facts should probably be a conflict, or the ledger should say why not.
- **The data date is JPL's**, 24 November. SsODNet cards fetched on the 25th are in the build; the source line gives "fetched 2026-11-21 to 2026-11-25".
- **The record freezes nothing.** Every prediction is provisional, and 25 of 51 have no settle date; each says why.
- **A browser without WebGL2** still downloads the field file it cannot draw.
- **2009 BD's second size solution** is in no source on disk. **Density ceilings from JPL's drifts** are not on the record. **Orbital elements and the Goldstone radar date** are ingested and shown nowhere.

## 12. Decisions for Adam

1. **Rocks in the field as glyphs.** Not to scale. The instrument design draws them this way; going back to scale means dots at the home view. The marks are set in the shader and restated for picking in `Field.mark()` (`field.js`).
2. **The fixed-table rule and Spitzer.** Settled after the round: a finished programme's table is final, so asteroids found after the Spitzer surveys ended are "not measured" there, not "not checked". The end date (30 January 2020) is from memory, not from a project file; confirm it.
3. **Two sigma to decide a gate**, and a factor of 2 where a size has no stated error.
4. **Class label error**: 21% from colours, 12.5% otherwise. The second is weakly sourced.
5. **A density on file** narrows the mass draws and does not decide the mass gate.
6. **The orbit gate** reads "Orbit code 5 or better" and passes 136 asteroids JPL flags as too uncertain to point at, with a sentence saying so. Whether they should pass.
7. **Equal brightness, equal price tag**: asteroids with nothing measured are seeded by brightness, not by key.
8. **Line brightness in the field** follows the size row alone. 294 rocks with a measured class or push and no measured size are drawn as guesses; the tip says what is measured.
9. **Iron-rich dollars.** Keep, or kilograms only until Cannon et al. 2023's table is read.
10. **The water sentence** and the reworded first ladder rung: accept, or restore the wording of `DESIGN.md`.
11. **Kamoʻoalewa's 27.9-minute period** was entered by hand beyond the brief; `verify-capability.md` row 18 confirms it.
12. **Sizes in the field file and the lists** follow the licence rule (`OPEN_SIZES_ONLY`). Confirmed in the review; listed because 116 measured rocks are placed by brightness.
13. **Freeze the method**, so the record's predictions can be dated.
14. Still open from `DESIGN.md` section 10: the name, the host, a contact address for JPL.
