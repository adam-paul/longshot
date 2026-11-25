# The instrument design

The site's look, as built. Adam chose this direction on 2026-11-25 ("okay, let's go with instrument."; `DESIGN.md` section 4 has his words). `DESIGN.md` wins where the two differ; `docs/mvp.md` section 6 is the contract the pages are built to. The code is the reference: `longshot/site/static/style.css` (tokens, type, the text marks), `field.js` (the field's marks and glow), `app.js` (strip, legend, axes, table view, readout), `templates.py` and `gen.py` (every page).

The page is a piece of equipment. The field is a framed scientific figure, the controls sit in one ordered strip above it, and every readout is a label with an aligned number. White vector lines on black, as on a vector display; measured rocks glow faintly, like phosphor.

## 1. How it was chosen

On 2026-11-25 Adam judged the first prototype "somewhat hideous". Three directions were mocked up as static pages from the build's records: **atlas** (a printed reference atlas, a serif face), **vector** (closest to the arcade game, every rock an outline) and **instrument** (a framed figure and readouts). Each went through three rounds of screenshots and critique, then a judge scored them. Instrument scored highest on coherence and usability; Adam chose it, then asked for ten changes, and the design took these from the other two:

- From vector: the named asteroids as the readout's default content (plain links, a keyboard and no-script path in); one B612 weight with a wider subset; no parentheses in interface copy; the glow on measured strokes only; the rock mark in the header; the entry summary as one list of label, value, detail and state.
- From atlas: the size scale with both mission gates drawn on it; the Apophis spin and open-size choices it got right (the summary prints the period the spin row rests on; bulk pages print open sizes only).

The mockups, their scripts, screenshots and critiques are in `data/archive/cleanup-2026-11-25.tar.zst` (`docs/cleanup-2026-11-25.md`).

## 2. Tokens

### Colour

No hue. Six greys, each with one job, and one glow. State is carried by line style and glyph shape, never by colour.

| Name | Value | Job | Contrast on #000 |
|---|---|---|---|
| `ground` | `#000000` | page, plot area | |
| `ink` | `#ffffff` | values, headings, measured marks, focus ring | 21.0 |
| `ink-2` | `#a8a8a8` | labels, axis titles, units, details, the "not checked" ring | 9.1 |
| `ink-3` | `#8a8a8a` | tick labels, footnotes, the "not measured" glyphs | 6.3 |
| `edge` | `#5e5e5e` | plot frame, control borders, ticks (non-text, needs 3:1) | 3.2 |
| `grid` | `#202020` | gridlines, row separators, the uncertain band | decoration |
| `glow` | in CSS `drop-shadow(0 0 2px #ffffff8c)`; in the field, a band of the line itself (section 4) | measured outlines only: field rocks, the selected rock, the entry's rock, the header mark, the "measured" and "pass" glyphs | decoration |

Selection is shown by geometry (crosshair, axis tags, error bar), not by an accent colour. Unmeasured rocks never glow.

### Type

| Family | Role |
|---|---|
| **B612 Regular**, self-hosted, one file | navigation, controls, labels, every number, table cells, headings, axis text |
| system serif (`ui-serif, Georgia, "Times New Roman", serif`) | the site's own sentences only: ladder conclusions, row notes |
| no monospace | B612's digits are all one width (`tabular-nums`), so numbers align without mono's wide letters |

One weight. Hierarchy comes from size and grey: white for values and headings, `ink-2` for labels, `ink-3` for footnotes. `font-synthesis: none`; `h1`–`h4`, `th`, `b` and `strong` are 400. Fallback: `system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.

B612 was drawn for Airbus cockpit displays (Airbus, Intactile Design, ENAC; 2012) to be read quickly on dark screens at small sizes, with 0/O, 1/l/I and 5/S kept apart, which suits designations such as `2011 AA37`. The file is `longshot/site/static/fonts/b612-regular.woff2`, **12,620 bytes**, a subset of google/fonts `ofl/b612/B612-Regular.ttf`: Latin-1 plus en and em dashes, curly quotes, ellipsis, minus, σ, superscript ⁰ ⁴–⁹ ⁻, ≈, ≤ and ≥. SIL OFL 1.1, licence in `OFL.txt` beside it. Every page preloads it; `font-display: swap`.

B612's parentheses are square, so interface copy goes without them: "Delta-v of the cheapest round trip, km/s", "Drift A2, 10⁻¹⁴ au/d²" (`templates.unparen`). Sentences in the serif keep theirs.

### Scale (px / line height)

| Token | Size | Use |
|---|---|---|
| `t-xs` | 12/16 | tick labels, footnotes, source references, table headings |
| `t-s` | 14/20 | labels, controls, nav, table cells, readout |
| `t-m` | 16/24 | values, row headings, serif prose |
| `t-l` | 22/28 | section headings, summary values |
| `t-xl` | 32/36 | the selected asteroid's name, list title |
| entry title | 40/44 | the asteroid's name on its entry |

Spacing: 4, 8, 12, 16, 24, 32, 48 px. Everything sits on the 4 px grid.

## 3. Marks

Four states, four glyphs, everywhere: the field, the legend, the readout, the entry rows and the tables. The glyph prefixes the state word; it never stands alone.

| State | Text glyph (`.g-*` in `style.css`) | Field, overview (under 4x) | Field, zoomed (4x and over) |
|---|---|---|---|
| Measured size | rock outline, glow | white rock outline, 4.6 px, 1.25 px line, glow | same |
| Limit only | dashed rock outline | white dashed rock outline | same |
| Not measured | grey dot | grey dot, 1.25 px, `ink-3` | dim rock outline, 3.8 px, `#6b6b6b`, 1 px line, no glow |
| Not checked | dashed ring | dashed ring, 3.2 px, `ink-2`, six dashes (a ring at 1x, never a dot) | same |
| Mission: pass | heavy rock outline, glow | white outline, 2.2 px line, glow | same |
| Mission: untested | grey dot | dot, brighter as the chance rises (five steps) | outline in that grey |
| Mission: fail | cross (a faint dot in the legend) | `#444` dot | same, 1.4 px |
| Outside the filters | | any of the above at 0.16 brightness, no glow, not pickable | same |

Line style in the field comes from the size row alone. The marks are glyphs, not to scale: a rock's place on the size axis gives its size; the entry draws the rock to scale with nested outlines and a scale bar. Every rock's outline comes from its key (`longshot/shape.py`), the same rule on the entry and in the shader.

The header mark is one of the field's rocks: of the keys `longshot0` to `longshot199` whose outline is about as wide as it is tall, the one with the deepest notch (`templates.MARK_KEY`), so it reads as a rock at 20 px, not a diamond or a shield.

## 4. The glow

Adam: "keep the glow". It means "measured" and nothing else.

In the field it is part of the same instanced draw: a measured outline's ribbon is widened to a half-width of 2.25 CSS px, and the fragment shader fades the band from 0.26 brightness beside the line to 0.1 at its edge. Blending takes the brighter value (`MAX`), so overlapping glows never add up. No blur pass, no bloom, no extra framebuffer. In HTML and SVG it is a `drop-shadow` filter on the measured and pass glyphs, and a wider low-opacity stroke under the header mark and under a measured rock on its entry.

## 5. Layout

- **Header**, 48 px: the rock mark and "longshot", a "prototype" tag, then **Field, Observe next, Record, Method**, the data date at the right. Under 900 px the links and the date move into a "Menu" disclosure.
- **Front page**, desktop: a fixed app frame. The control strip across the top; under it the figure or the table (fluid) beside a 424 px readout column. They share one frame edge.
- **Control strip**, left to right: View (Chart, Table), Mission (Any, Surface work, Whole-body capture), Delta-v ceiling (slider and `12.0 km/s`), Find asteroid, and the count at the right ("Plotted 7,225 of 7,231", or "Listed n of 7,231" in the table view). The mission filter applies to both views.
- **Figure head**: the legend with its counts on the left, the zoom group at the right (−, the factor, +, Reset). The heading "Reachable asteroids" is in the HTML for screen readers and not drawn.
- **Plot**: a closed frame, ticks pointing in on all four sides, both axes titled with units. Margins left 66, right 14, top 12, bottom 52 px (58/10/10/46 under 600 px). The ceiling is a dashed line labelled with its value; beyond it the plot is shaded and the rocks dimmed, not removed. Zoom runs from 1x to 32x (wheel about the cursor, drag to pan, pinch, buttons, keys); ticks re-space, and under a third of a decade the size axis switches to round linear steps.
- **Selection**: a crosshair to both axes, an inverted tag on each axis (the tick label under it is left out), the 9-in-10 size range as an error bar with its ends labelled. The readout replaces its default content with the entry's summary; Close restores it.
- **Readout**, by default: the named asteroids as plain links with their delta-v, one typical asteroid with nothing measured, and the On file table of rows by state. These work without JavaScript; with it, a click selects in place.
- **Table view**: the same selection as the chart, in the plot's box. A sticky heading row, every heading a sort button with `aria-sort`, pages of 50 with Previous and Next. Sizes are open values, each prefixed by its size-state glyph so an estimate never looks like a measurement; a stand-in size is dimmed with a title. In the table view the legend keys the size column and counts the listed rows.
- **Entry**: content up to 1264 px. The head (name, then number and first observation as labelled values); the summary (the rock figure beside one list of Size, Spin, Made of, Mass, Reach, then under a Missions heading Surface work and Whole-body capture, then Would settle most, each a label, a value, a detail and a state). Then a 180 px sticky rail of section names beside the sections: On file (a scale per row with the mission gates drawn on it, then its facts), Difficulty, What is in it (100 cells beside each price table), What would settle it, Missions (the two gate tables stacked, sharing columns), Sources.
- **Observe next**: one table up to 1440 px, in rank order, grouped by window kind; a group row names the observation and what it settles each time it changes. No script, so no sort buttons.
- **Phone**, under 900 px: one column, 16 px gutters (32 px from 900 px). The strip stacks with View and the count on the first line; the figure is 460 px tall; the readout follows. Table rows and gate, price and source tables become labelled blocks. The entry opens with an "On this page" disclosure. At 1x the plot lets the page scroll; zoomed in, a one-finger drag pans.

## 6. Principles

1. **The figure is the instrument.** Labelled axes with units, one legend that follows the filter and the zoom. Nothing is printed over the data.
2. **Four states, four glyphs, everywhere** (section 3). "Not checked" never reads as "not measured".
3. **Ranges before points.** An estimate is an interval (9 in 10, labelled); a measurement a point with its one-sigma bar. Mission thresholds are drawn on the same scales.
4. **Two voices.** B612 for what is read off the instrument; the serif for the few things that need a sentence.
5. **Odds as counts of 100.** "Of 100 like it" is drawn as 100 cells, the chance of nothing first, each kind counted in its key.
6. **Dates are facts.** Windows are bars on a dated axis that starts at the data date. Nothing says "now". A date never breaks across lines. The data date is in the header and the footer only.
7. **Each destination once.** The header holds the site's pages. The missions are a filter, not pages: no mission name is a link anywhere. An asteroid's own mission results appear only under its "Missions" heading.
8. **Conventions kept.** Real links and URLs, native radio, range and search controls with visible labels, the back button, a tab order that follows the strip, find-in-page on the readout and table.
9. **Layers.** The HTML carries the named asteroids, the counts and the links; CSS lays it out; JavaScript adds the figure, the table and selection.

## 7. Defaults turned down

| Default | Instead | Why |
|---|---|---|
| a headline sentence as the page's hero | none; the legend and the On file counts carry the numbers | Adam: "Do you commonly see websites with full sentences as headers like this? It's bizarre." |
| the same link in several places | the missions once, as the strip's filter; the table view replaces the mission lists | Adam: "surface work/whole-body capture buttons/links exist in three separate places. Why?" |
| near-black with one acid accent | no accent; selection is geometry | white on black is Adam's call |
| two weights for hierarchy | one weight, 12,620 bytes; size and grey carry hierarchy | the bold read heavy, like a software dashboard |
| monospace for every small label | B612, no mono | B612's digits are tabular |
| tracked-out capital eyebrow labels | sentence case | the rail's position says "section" |
| rounded cards with soft shadows | a docked readout sharing the figure's frame edge | a card covered the data |
| meta strings joined with middle dots | labelled values: Number, First observed | |
| a hint telling the visitor what to do | none; the named list is the way in | no sentence where a link does the job |
| a glow on everything | the glow on measured outlines only | the glow means "measured" |

## 8. Open

- On a phone the strip takes about 380 px before the chart starts.
- The entry's fact tables wrap long method notes (Apophis's Spitzer line) into a narrow column. The atlas mockup's ledger (one table with Value, Unit, 1σ range and Source columns) was the proposed fix; not done.
- Pinch zoom is untested on a real touch device; only headless Chromium has been run.
