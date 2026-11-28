# The prototype: build contract

This file fixes the interfaces between the parts so they can be built separately. `DESIGN.md` gives the direction and wins on look and copy. `docs/plan.md` gives the science.

## 1. Shape

```
uv run python -m longshot build      # data on disk -> build/ and dist/, no network
uv run python -m longshot serve      # local static server for dist/ on 127.0.0.1:8000; a port may follow
uv run python -m unittest discover -s tests -t .
uv run python tools/browser_check.py dist      # headless Chromium: checks, frame times, screenshots
```

`build` takes `--build DIR` and `--dist DIR`. It prints the counts, the bytes of the field file and of the first screen, and the time taken.

- Python 3.12 through uv, standard library only. The package is `longshot/` at the repository root.
- `build/` holds intermediate products, `dist/` the site. Both are git-ignored and remade by every build: a build removes any page, data file or static file under `dist/` that it did not write. It refuses a `--dist` folder that is not empty and was not written by an earlier build, and one that holds or lies inside `data/`.
- A build is deterministic: same inputs, same bytes out. No clock, no network, no unordered iteration.
- Random draws are seeded from the method version and the object key. Where nothing about the rock is measured, the seed is its brightness (H and its error) in place of the key, so two asteroids with equal inputs get equal figures.
- The data date is the date of the JPL snapshot used (`2026-11-24`), read from the input path, never from the clock. Every other source carries its own edition and fetch dates, printed with it.

## 2. Layout

```
longshot/
  __main__.py        command line: build, serve; copies the static files under hashed names
  config.py          input paths, data date, method version
  types.py           the record types below (do not change field names without updating this file)
  ids.py             object keys and aliases
  ingest/            one module per source: nhats, sbdb, ssodnet, pravec, lcdb, spitzer, curated
  ledger.py          claims and coverage -> the six rows; holds no threshold of its own
  model.py           runs the stages below over the ledger's records, drawing once per object
  contract.py        checks every record against section 4 before a page is written
  shape.py           a rock's outline from its key: the rule the field's shader and the entry page share
  method.py          loads method/v0_1/*.toml
  priors.py          size, spin and class from brightness
  draws.py           joint draws per object
  missions.py        elimination by mission type
  observe.py         which observation would settle the most, and the order of the list
  value.py           what is in it, as ranges
  ladder.py          the difficulty ladder
  predictions.py     the record
  export.py          records -> build/records.jsonl, dist/data/field.*.bin, keys file and manifest
  site/
    gen.py           records -> every HTML page
    templates.py     HTML fragments as Python functions
    static/          style.css, app.js, field.js (the shaders are strings inside it), fonts/ (B612 Regular and its licence)
method/v0_1/         constants with provenance (TOML): priors, missions, ledger, observe, value, ladder
registry/keys.jsonl  minted object keys, committed, only ever appended to
registry/curated.toml  hand-entered single values, each with its citation and the passage that verifies it
tools/               the fetch tool, the browser check, the synthetic field, the derivations behind the method files
tests/
```

## 3. Inputs (all local)

| Source id | What | Path |
|---|---|---|
| `jpl-nhats` | reachable list: delta-v, H, orbit code, next observing window | `data/snapshots/2026-11-24/nhats.json` |
| `jpl-sbdb` | every near-Earth object: orbit, tracking, H, and the physical and push values JPL holds | `data/snapshots/2026-11-24/sbdb_neo.json` |
| `ssodnet` | literature cards, one per asteroid | `data/research/dl/coverage-exact/cards/*.json` (fetched 21 November) and `data/sources/ssodnet/cards/*.json` with `journal.jsonl` (fetched since) |
| `pravec` | rotation periods with quality grades | `data/sources/pravec/newres-2026-11-24.txt` |
| `lcdb` | rotation periods with quality grades (release 2023-10-01) | `data/research/dl/coverage-exact/lcdb/` |
| `spitzer` | sizes and reflectivities for about 2,100 near-Earth asteroids (edition 2019-11-30) | `data/research/dl/coverage-exact/spitzer/spitzerneos.csv` |
| `curated` | measurements no database on disk holds, entered by hand | `registry/curated.toml` |

- A build reads whatever cards are on disk when it runs. An asteroid with no card, one SsODNet answered 404 for, or one whose request failed is `unchecked` for that source. `tools/fetch_ssodnet_cards.py` is the one script that opens a network connection; it is run by hand, never by the build.
- **Fixed tables.** `pravec`, `lcdb` and `spitzer` are `unchecked` for an asteroid first observed after their edition date, with the reason "older than this asteroid" (`method/v0_1/ledger.toml [fixed_tables]`).
- **Hand-entered values.** Each claim in `registry/curated.toml` names its citation and quotes, word for word, the passage of a file under `docs/research` that verified it. A test checks the passage is there.
- `.sha256` files beside the Pravec and lightcurve-database tables pin their bytes (`tools/checksum_tables.py --check`).

Any value from any source may appear on any page and in the field file. Every source is cited once, with the citation it asks for, in the Sources section of `method.html`; an entry names the source beside each value and lists its sources with their dates, without citations.

## 4. Records

Defined in `longshot/types.py`. Everything is plain data that serialises to JSON.

**Object key.** Opaque, minted once, recorded in `registry/keys.jsonl` with the designation it was minted for. Never derived from a designation. Keys are minted for every object in the SBDB table, and for any designation on the reachable list that table lacks (none today); "reachable" is a population. A build that meets an unknown object appends a key; it never rewrites one, and it stops if a line has gone missing from the registry.

**Claim.** One statement by one source about one object: `key, prop, source, kind (value|upper|lower), value, lo, hi, unit, quality, ref, note, snr`. Properties are fine-grained ids such as `delta_v_kms`, `diameter_m`, `albedo`, `period_h`, `taxonomy`, `A1`, `A2`. `lo` and `hi` are the source's stated one-sigma range. A cell that is present and unreadable stops the build; it is not read as blank.

**Coverage.** The act of looking: `key, row, source, outcome (found|absent|unchecked), reason`. Every source that could inform a row writes one coverage record per object. A source that was never queried for an object, does not know it, or is a fixed table older than it, is `unchecked`.

**Row.** Six per object: `reach, tracking, size, spin, surface, push`. Each has a `state`:

| State | Meaning | Shown as |
|---|---|---|
| `measured` | a source gives a value | the value, its one-sigma range, its source |
| `limit` | a source gives only a bound | the bound and its source |
| `prior` | every source for this row was checked and none has a value | "estimated", with the estimate for this brightness |
| `unchecked` | at least one source for this row was not checked, and none of the checked ones has a value | "estimated" on the front page and in the summary; the entry's row adds "Not checked: <source>" with the reason |

A row never shows "not measured" while a source for it is unchecked. The same holds for the rock's caption and for every sentence the model writes about that row (gates, ladder rungs, the observation): none says "not measured". The row names the source once ("Not checked: <source>", docs/design.md section 3); the sentences that rest on the row call its value estimated and do not name the source again. `observe.unchecked` still lists the sources, so the entry can say where to look first. `Row.note` ends with one sentence per unchecked source, in the order of `Row.unchecked`; the page prints each as the reason beside the source's name.

**Fact.** `label` is the stable id of a fact within its row (`longshot.ledger.LABEL` lists them); the page prints its own word for it (`templates.label`, so "condition code" reads "orbit condition code" and "albedo" reads "reflectivity"). `used` is false for a value kept on file and not counted towards the row's state: a period graded under U 2-, an ungraded copy of another source's limit, a computed size or reflectivity, a Spitzer fit under signal-to-noise 5, a reflectivity above 1, a fitted push under 3 sigma, a known-bad entry. `note` says a few words about that one value; `Row.note` says why a value is not used. Used facts come first, in the row's source order, so the first used value is the one the row rests on. The page prints an unused fact dim and marked "not used". The absolute magnitude `H` is a fact of the size row; it never changes the state. What counts is set in `method/v0_1/ledger.toml`.

**Object record.** The one thing the site generator reads. One JSON object per asteroid in `build/records.jsonl`:

```
key, designation, name, number, aliases[], populations[], data_date, method
rows: { reach|tracking|size|spin|surface|push: {
    state, facts[], prior, unchecked[], conflicts[], note } }
  fact:  { label, value, lo, hi, unit, kind, source, ref, quality, used, note }
  prior, size row:    { q05, q25, q50, q75, q95, unit: "m", basis }
  prior, spin row:    { p_fast_2_2h, p_under_1h, p_under_10min, range{the same three: [low, high]}, basis }
  prior, surface row: { q05..q95 of reflectivity, unit: "", shares{S, C, X, other}, basis }
summary: { size_m{q05..q95}, mass_t{q05..q95}, p_fast_2_2h, p_under_1h, p_under_10min, class{S,C,X,other},
           reflectivity{q05..q95}, h, band, draws, mass_basis (density|class),
           period{value, unit, lo, hi, kind, source, ref, quality, rests_on, conflict} | null }
missions: { surface|capture: { status (pass|fail|untested), p, gates[] } }
  gate: { id, label, status (pass|fail|untested), p, basis (measured|prior), text }
observe: { best, mission, gate, gain, text, needs, tier (pointable|survey_only|none), unchecked[],
           window{start, end, peak_mag, pointable, as_of} | null,
           label, mission_label, gate_label, gate_p } | null
value: { metal{p_nothing, p_nothing_lo, p_nothing_hi, usd{q05,q25,q75,q95}, kg{q05,q25,q75,q95}, capped},
         iron_rich{p_lo, p_hi, kg{q05,q95}?, usd{q05,q95}?},
         water{p_nothing, p_nothing_lo, p_nothing_hi, tonnes{q05,q95}?}, sample{mission, fact, ...}?,
         basis, statements[], statement_ids[],
         table{ metal{cells[], rows[]}, water{cells[], rows[]}, notes[] }? }
  cell: { id, label, n }           rows: { id, label, of100, kg, usd } (metal), { id, label, of100, tonnes } (water)
ladder: [ { rung, status (measured|prior|unknown), text, parts[]? } ] x 5
  part (brought_back only): { id (grams|more_than_grams), label, word (done|not_yet_attempted|proposed|null), text }
sources: [ source ids used ]
gone: { date, text, evidence } | null
```

- A prior is written on the size, spin and surface rows when their state is `prior` or `unchecked`.
- An asteroid with no `H` on file (6 today) has no size: `summary` and `value` are `{}`, the row priors are null, both missions fail on the orbit gate, and the ladder says what is missing.
- `summary.period` is the period the spin row rests on, its first used period (a bound where the row is a limit), whichever source gives it; `rests_on` names that source. `null` where the spin row is neither measured nor a limit. `conflict` is true where the row's sources disagree. `summary.mass_basis` says what the mass range was drawn from besides the size: a bulk density on file, or the class's density range.
- `value.table` is the price tag as the entry lays it out: for metal and for water, the 100 cells (`n` adding to 100, the chance of nothing first, the cells the low and high scenarios disagree on as "or" cells, zero counts left out) and the rows beside them, then the notes the rows do not say. Every figure is one the statements print, rounded the same way, with "t" for tonnes. It is absent where `value.sample` is set: the statements are then the price tag. Its words are in `value.toml [table]`.
- `observe.label`, `mission_label` and `gate_label` are the names of the observation, the mission and the gate; `gate_p` the gate's chance now.
- **Gates.** A measurement decides a gate only when it clears the threshold by two of its stated one-sigma errors, or by a factor of 2 where no error is stated. Otherwise the gate is `untested`, with `p` the share of the object's draws that pass. An untested `p` is never 0 or 1: with n draws it is held between 1/n and 1 - 1/n, and prints as "<1%" or ">99%". A gate's `text` may be empty: it says only what the status and the row do not, so it names no source that was not checked and does not repeat the row's conflict or JPL's pointing flag. The record keeps the statuses `pass`, `fail` and `untested`; a page shows them as a viability: Yes, No or an estimated chance, counted as viable, not viable and estimated (docs/design.md section 3).
- `observe` is null when no observation would change a mission's status. The window is then still in the tracking row's facts. `observe.tier` is the kind of window JPL lists, and `observe.unchecked` the sources not checked for the row the observation would settle: the measurement may already exist there.
- `observe.gain` is in bits: the expected fall in uncertainty about the gate the observation settles. `observe.rank_key` orders `list/observe.html`: windows a telescope can be pointed at first, then survey-only, then none; within each, the year the window opens, then the gain. The gain is not printed.
- `value` holds no mean, median or middle quantile of dollars. `contract.check` rejects a record that carries one. For an asteroid a spacecraft has sampled, `value.sample` names the mission, and the statements (`sample_water`, `sample_water_at_most`, `sample_no_analysis`) rest on the sample in place of the class odds.
- `gone` is set for a body on JPL's list that no longer exists (`ledger.toml [[gone]]`; 2008 TC3 today). Both missions fail, `value` is `{}`, `observe` is null, the tracking row lists no window, and the rock does not turn.
- `longshot/contract.py` checks every record against this section between the model and the site. A missing field stops the build.

**Prediction.** `id, kind, group, statement, p, p_low, p_high, band, settles, settle_from, settle_by, settle_note, key, designation, frozen, provisional, outcome, basis, source`. `settle_note` says in a few words why there is no date, when neither date is set.

## 5. The field file

`dist/data/field.json` is the manifest; `dist/data/field.<hash>.bin` holds little-endian columns in the manifest's order, each `n` values long. Each column starts at the `offset` the manifest gives, a multiple of 4 bytes, with zero bytes between. Only `open` and derived values go in it, and only the columns the app reads. No dollar figure is in it.

Manifest: `{ schema: 1, data_date, method, n, file, columns: [ {name, type, offset} ], keys_file, counts: {...}, missions: [...], unplaced: [...] }`. `file` and `keys_file` are relative to the manifest. `<hash>` is the first 12 hex characters of the file's SHA-256. Rows are sorted by key.

- **Who is in it.** Every reachable asteroid that has a size to be placed by. One with no `H` on file is left out of the field and keys files, listed in `unplaced` and counted in `counts.not_placed`; it still has a page, search finds it, and the table view lists it. So `n + counts.not_placed` is the number of entry pages.
- **Sizes.** `dv`, `size_q05`, `size_q50` and `size_q95` are finite and above zero, with q05 <= q50 <= q95. They are the record's `summary.size_m`; a measured diameter (or bound) is plotted at its value (`size_q50`), from whichever source gives it. The list pages print the same size.
- **`state`.** Size in bits 0-1, spin in 2-3, surface in 4-5, push in 6-7.
- **`period_s`.** The period the spin row rests on, from whichever source gives it, and only when the row is measured and its sources do not disagree. The entry turns its rock at the same rate. 0 for a body that no longer exists.
- **`p_*`.** 255 for a pass, 0 for a fail, 1 to 254 for untested. For drawing and sorting.
- **`pct_*`.** The whole percentage the entry prints for the mission's chance, for the table view: 1 to 99, halves rounded up; 0 for a fail, and for an untested chance that prints as "<1%"; 100 for a pass, and for ">99%". The status column says which. `p_*` is not read back into a percentage: in steps of 1/255 it prints a different whole percent for 186 of the 3,973 untested chances of 2026-11-24, about one in 21. The rounding is the entry's (`templates.chance`).
- **`p_<mission>`, `status_<mission>`, `pct_<mission>`.** Three u8 columns per mission type, after the columns of the table below, in `missions.toml`'s order (`export.mission_columns`): the chance of meeting every condition in 0–255, the viability (0 No, 1 estimated, 2 Yes), and the whole percentage the entry prints. A new mission type in `missions.toml` adds its own; nothing in the app or the generator names one.
- **`g_<mission>_<condition>`.** One u8 per condition of each mission type, after the viability columns, in the method's order (`export.gate_columns`): 255 met (Yes), 254 not met (No), 253 not assessed, otherwise the whole percentage the entry prints for the condition's estimated chance, with 0 and 100 printing as "<1%" and ">99%". The table view's condition columns read them.
- **`missions`.** `[ {id, label, summary, gates: [ {id, short, label, column} ]} ]` from `method/v0_1/missions.toml`, in its order: each mission type's name and summary, and each condition's short heading, full label and byte column. The app takes the mission types, their names and their conditions from here and holds none of its own.
- **`named`.** 1 where the asteroid has a name.
- **`seed`.** The low 16 bits of the first four bytes of the SHA-256 of the key, read little-endian (`longshot/shape.py`): every bit the outline rule uses. The shader picks the outline from it; the entry page draws the same outline.
- **`counts`.** `{ objects, placed, not_placed, with_period, size_state[4], rows{row: {state: n}}, missions{mission: {pass, untested, fail}}, observe }`.
- **`unplaced`.** `[ [key, designation, name, number, dv], ... ]` for the asteroids with no rock, in key order: a keys-file row, then the delta-v in km/s. `counts.not_placed` is its length. Both missions fail for each (section 4), so the table view needs no more. Search reads the first four.

| Column | Type | Meaning |
|---|---|---|
| `dv` | f32 | delta-v, km/s |
| `size_q50`, `size_q05`, `size_q95` | f32 | size in metres; a measured one at its value |
| `period_s` | f32 | rotation period in seconds, 0 if none |
| `state` | u8 | two bits per row for size, spin, surface, push: 0 unchecked, 1 prior, 2 limit, 3 measured |
| `named` | u8 | 1 if the asteroid has a name |
| `seed` | u16 | shape seed, from the key |

`dist/data/keys.<hash>.json` gives, in the same order: `[ [key, designation, name, number], ... ]`, for search and links. `name` and `number` are null where there is none.

`tools/make_synthetic_field.py --check dist/data/field.json` checks a field against this section.

**The readout's lists.** Not in the field file: the generator writes them into the front page, and the build passes them to it as `assets["readout"]` (`export.readout(records)`). `named` is every asteroid with a name, by delta-v and then key: `[ {key, designation, name, number, dv} ]` (12 today, Apophis 6.049 km/s first).

## 6. The site

```
dist/
  index.html              the field: the control strip, the chart or its table view, and the readout
  a/<key>.html            one page per reachable asteroid; the readout lifts its <section id="summary">
  list/observe.html       what to observe next, in rank order
  record.html             the predictions the site will hold
  method.html             data date, states, every threshold with its basis, sources, what the site does not claim
  data/                   field manifest, field file, keys file
  static/                 style.<hash>.css, app.<hash>.js, field.<hash>.js
  static/fonts/           b612-regular.woff2 (12,620 bytes) and OFL.txt, its licence; not hashed
```

- Asset URLs handed to the generator are relative to the site root; pages under `a/` and `list/` prefix them with `../`. `app.js` imports `./field.js`; the build rewrites that one name to the hashed file before hashing `app.js`. `style.css` names the font as `fonts/b612-regular.woff2`, so the font sits in `static/fonts/` beside it; every page preloads it.
- The front page names `field.<hash>.js`, the manifest and the field file in its head (`modulepreload`, `preload`), so they load side by side. The keys file is fetched once the rocks are drawn, so the names do not hold up the first frame. If it fails to load, the field stays and the search box says the names are missing.
- **Navigation.** Every page's header: the rock mark, "longshot", a "prototype" tag, then Field, Observe next, Record, Method, and the data date. The two missions are a filter on the field, not pages: no mission name is a link anywhere.
- **Front page.** `form#controls`: View (`view`: chart, table), Mission type (`m`: all, surface, capture), the delta-v ceiling (`dv`, from the data's lowest delta-v to its highest, to a tenth of a km/s), and Find (`q`). Above the figure, `div#legend.legend` holds one `ul`, the key: `li.tot[data-k=shown]` ("X of N reachable asteroids"), then `li.row` "Diameter" (`span.lab`, then `ul.items` of `li.c[data-k=measured|estimated|loose]`), then `li.row.v` "Mission viability" (`li.c` Viable, Estimated, Not viable, `data-k=viable|chance|not`). The viability row is always there: with All its label and items are `aria-hidden`, carry no `data-k` and are hidden, so the legend keeps one height; the generator writes the first paint and `app.js` rewrites it on every change. Beside it the zoom group (−, +, Reset), with no zoom factor shown. `figure#plot` holds the canvas, the axes the app draws as HTML (`#axes`) and the tip. `section#table` is the table view in the same box: the asteroids the strip selects (under the ceiling, matching the search, and with a mission type chosen not "No" for it), 50 a page, every heading a sort button. Its viability columns sit under a group heading in a second header row: one per mission type, or with one chosen its conditions and "Overall", all from the manifest's `missions`. `aside#readout` holds, as the generator writes it, the named asteroids with their Δv; the coverage counts are on Method; selecting a rock replaces that with the entry's `section#summary`, and Close restores it. A link to an entry anywhere on the page selects in place unless the click is modified. Without WebGL2 the page says so, opens on the table, and disables Chart and the zoom group.
- **Entry.** `<main id="entry" data-key>`: `section#summary` (the heading, the number, designation and first observation, the rock figure and one summary list of Diameter, Spin, Composition, Mass, Δv, in three sections: Properties (Diameter, Spin, Composition, Mass, Δv), Mission viability (Surface mining, Asteroid capture) and Next observation (one row named for the observation, with what it takes), each a label, a value, a detail and a state; a body that is gone opens the list with a Gone row. Mass says what it rests on: the size and the class's density range, or the size and the density on file (`summary.mass_basis`). Next observation says why nothing is ranked without repeating the mission types' results, and a window JPL does not list is said once), then Data (a scale per row with the mission conditions drawn on it, then its facts), Difficulty, Metal and water (`value.table`; `value.statements` where a returned sample replaces the class odds), Next observation, Mission viability and Sources. Entry styles select `.entry`, never `main`.
- An entry's heading is the asteroid's name where it has one, else its designation.
- `list/observe.html` has no script: it is in rank order. Each row's diameter is the entry's, with its state mark.

- The generator writes every page complete. JavaScript sorts, filters, draws and navigates; it computes no probability. The table's chances are the field file's `pct_*`.
- State is in the URL: `?a=<key>&m=<mission>&dv=<max>&q=<text>&view=table&sort=[-]<column>&page=<n>`; `sort` and `page` only in the table view. Zoom is not kept. The back button works.
- The field is one WebGL2 instanced draw call for the rocks; the hovered and the selected rock are one more single-instance draw each. Position is delta-v against size (log scale). Rotation runs in the vertex shader from `period_s`.
- **Rocks in the field are glyphs, not to scale.** Fixed-size marks, one set everywhere (field, legend, tables, entries), as `docs/design.md` section 9: measured a white outline with a glow; a bound a dashed outline; estimated (not measured, or a source not checked) a half-bright dot, a half-bright outline from 4x zoom. Zoom runs from 1x to 32x. The glow is a wider band of the same line in the same draw, its brightness falling off from the line; no blur pass, no extra framebuffer. Rocks outside the filters are drawn at 0.16 brightness without glow and cannot be picked. The selected rock gets a crosshair and a tag on each axis; its nested outlines are in the readout.
- **Marks in the field come from the size row alone.** A measured spin shows as turning. A mission type does not change how certainty is drawn: the not viable go faint and cannot be picked; the viable keep their mark, filled; the estimated keep their mark. No brightness follows a chance. The tip gives the name, Δv, the diameter with its range and state, and with a mission type chosen its viability.
- Nothing turns unasked under software rendering, or where the visitor asks for reduced motion.
- Search matches a designation, a name or a number. Enter opens the exact match before a partial one. It finds the asteroids with no rock through the manifest's `unplaced`.
- Look and copy: `DESIGN.md` sections 4 and 5, and the instrument design (`docs/design.md`): white on black, greys only, B612 Regular for labels and numbers with a system-font fallback, the system serif for sentences, one weight, no subtitles, no explanatory text where a label and a value do the job.
- Every page shows the data date in its header; under 900 px, where the header has no room for it, a footer line carries it.
- The state marks are empty elements (`<i class="g g-measured">`) that `style.css` draws, so a page of thousands of rows carries a class name per mark. On `list/observe.html` the phone layout names each column by position in the stylesheet, not by an attribute on every cell.
- `method.html` prints the method files for a visitor: their values, what each was chosen from, and their public prose (`caveat`, `not_used`, `basis` and the like, through `templates.public_text`, which drops any clause that only points into the project). It cites a constant only by its `cite` key; `source` is provenance for whoever maintains the method and is never printed. Observing windows are shown as dated facts, never "open now".
- Every number on an entry names its source. Every threshold and fixed figure an entry prints links to where `method.html` gives its value, what it was chosen from and where it comes from.

## 7. Method v0.1

Constants live in `method/v0_1/*.toml`, each with where it came from. `docs/method.md` explains them. They are proposals until Adam freezes them.

- **What counts as measured** (`ledger.toml`): the lowest usable period grade, how far two periods may differ, when a newer ungraded period stands beside a graded one, the detection bar for a push, the Spitzer signal-to-noise bar, the fixed-table rule, the values found to be wrong, the bodies that are gone.
- **Size from brightness**: the reflectivity spread measured by Spitzer for near-Earth asteroids below 2 au, tied to class in the joint draw.
- **Spin from brightness**: the chance of turning faster than 2.2 hours, 1 hour and 10 minutes, by brightness band.
- **Class from brightness**: shares of S/Q, C, X and other, with the spread between surveys. A measured class is taken as wrong in a share of the draws: 21% when it comes from colours, 12.5% otherwise.
- **Mission types**: surface mining, and capture of a whole asteroid. Each is a set of gates on orbit quality, size and spin, with thresholds from cited sources, and the two-sigma rule of section 4.
- **Value**: conservative, as ranges, the chance of nothing first, for what is in the rock before any cost. The verify files list corrections to apply first.
- **Ladder**: five rungs; the last uses fixed, dated words for what has been done.

## 8. Done when

- One command builds the whole site from the data on disk, with no network.
- The fixture objects in `tests/fixtures.py` show the right values.
- The field holds its frame rate with every asteroid drawn.
- Every number on a page traces to a source or a script output.
- "Not checked" never shows as "not measured".
- Every page shows its data date.

## 9. Changes made at integration (2026-11-25)

What changed in this file after the parts were built, and why.

- **Section 2.** `model.py`, `contract.py` and `shape.py` added. `model.py` existed and was not listed. `contract.py` is new: the generator reads leniently, so the build checks every record first. `shape.py` is new: the entry's rock and the field's rock were two different outlines for the same asteroid.
- **Section 3.** SsODNet cards come from two folders, and a build uses what is there. The second folder was filled after the contract was written.
- **Section 4.** `Fact.used` added: three parts were telling counted facts from uncounted ones by position and by grade strings. Prior shapes for the spin and surface rows, and the extra keys of `summary`, `observe` and `value`, written down as built. The "not checked, never not measured" rule extended to the model's sentences; the ladder's last rung broke it for 2,404 asteroids and now says "not checked", naming the source.
- **Section 5.** Column alignment, the `state` bit order, relative file names and the no-size case written down as built. `n` is not the number of pages: 6 asteroids have no `H`, so no size, and are not placed. The licence rule wins over "the measured value" for sizes from SsODNet and Spitzer.
- **Section 6.** `field.<hash>.js` and `list.<hash>.js` added to `static/`. The summary is no longer hidden when the field runs: hiding it removed every link from the front page. The entry heading leads with the name.

**For the instrument design (2026-11-25).** The redesign's entry summary, price tables, table view and readout read these, so no page types a figure by hand. The mockup's `build.py` (now in `data/archive/cleanup-2026-11-25.tar.zst`) typed the price rows (its `VALUE` dict) and split the ladder's last rung on a phrase; both are now in the record.

- **Section 4.** `value.table`: the 100 cells and the rows of both price tables, and the notes the rows do not say, from `value.metal`, `value.iron_rich` and `value.water` with the statements' own rounding; its words in `value.toml [table]`. `summary.period`: the period the spin row rests on, as an entry may print it (Apophis: the lightcurve database's 30.56 h, shown as JPL's matching 30.56 h). `summary.mass_basis`. `observe.label`, `mission_label`, `gate_label`, `gate_p`. The ladder's `brought_back` rung carries `parts`, its two amounts (grams; kilograms or tonnes), each with the state's word. `contract.py` checks all of them.
- **Section 5.** `pct_surface`, `pct_capture` and `named` added (15 columns; 21,675 bytes more, 4,062 gzipped). `unplaced` rows carry the delta-v. The readout's named list and typical unmeasured asteroid come from `export.readout`, passed to the generator as `assets["readout"]`; the typical one is picked by a stated rule, which picks 2026 HT.
- **Section 6.** Rewritten for the instrument design. The four mission lists and `list.js` are gone: the table view replaces them. The front page's strip, table view and readout; the entry's summary list; B612 in `static/fonts/`; the marks, the glow and zoom in the field; the URL keys. The summary that hid behind the field (`with-field`) is gone: the readout carries the named asteroids and the counts.

## 10. Changes made after the review (2026-11-25)

A review of the first build raised 108 findings. What they changed in this file.

- **Section 1.** Draws are seeded by brightness where nothing is measured: equal inputs gave different price tags. The build refuses a `--dist` it could damage.
- **Section 3.** `curated` added: 2022 OB5's period and class and Kamoʻoalewa's size and period were in no database on disk. The fixed-table rule added: over 500 spin rows read "not measured" for asteroids found after the lightcurve database's 2023 release. The `inference` rule tightened: a lightcurve-database value printed wherever another source agreed with it, grade and all.
- **Section 4.** `Fact.note`, `Claim.snr`, `gone`, `observe.tier`, `observe.unchecked`, `value.sample`, `summary.size_open_m` and `settle_note` added. A stated range is one sigma and is treated as such: it had been read as the whole range, and decided gates it should not have. An untested chance is never 0 or 1. A gate's text may be empty: each fact was being said three to five times on an entry. The "not measured" rule now covers the rock's caption.
- **Section 5.** The field file went from 20 columns to 12: nine were never read. `size_open` added, so the tip does not print a range from brightness beside the word "measured". `seed` is 16 bits. The keys file carries numbers, and the manifest lists the asteroids with no rock.
- **Section 6.** Each mission list is split in two; one table of 7,231 rows was 1.67 MB. The keys file is no longer preloaded. `with-field` replaces `has-field` as the class the compact summary hangs on: the page shifted when the field started. Rocks in the field are glyphs: drawn to scale, all but 23 of them were dots at home. Line style follows the size row alone: it had followed the better of size and spin.
- **Section 7.** `ledger.toml` added; `ledger.py` had held four thresholds of its own.
