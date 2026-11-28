# Design

Rules for every page, component and word on the site. A choice that does not follow from a rule here is a bug, either in the choice or in the rules. When a case is new, decide it from the principles in section 1, then add the rule.

`DESIGN.md` holds Adam's direction in his words and wins where the two differ. The code is the reference implementation: `longshot/site/static/style.css`, `field.js`, `app.js`, `longshot/site/templates.py`, `gen.py`.

## 1. Principles

1. **Every element earns its place.** It answers a question a visitor has, and no other element answers it. Test: name the question. If there is none, or another element already answers it, remove it.
2. **Plain on the surface, precise underneath.** The front page speaks a reader's language: how big, how hard to reach, how sure we are. The entry page carries the full record, with technical terms defined where they first appear. Method and Record are reference. No more than two levels between a visitor and any fact.
3. **One visual variable, one meaning.** Each of brightness, size, shape, line style, fill and the glow means one thing, site-wide (section 4). Nothing is brighter, bigger or heavier for emphasis.
4. **Convention before invention.** Scientific figure, table and unit conventions; ordinary web conventions for navigation and controls. Invent only where no convention exists, and say so here.
5. **Symbols and units before words.** A number with its unit needs no sentence. A label is a noun phrase, not a clause.
6. **One word, one meaning.** The vocabulary in section 3 is closed. A visitor never has to wonder whether two words mean the same thing.
7. **Honest by construction.** An estimate never looks like a measurement. A range always says what range it is. Nothing claims to be current that is not.

## 2. Layers

| Layer | Pages | Reader | Language |
|---|---|---|---|
| Surface | front page: chart, table, readout | anyone who knows they are looking at asteroids and mining | section 3, surface list only |
| Record | one entry per asteroid | someone who wants this asteroid's details | surface list plus technical terms, each defined at first use on the page |
| Reference | Observe next, Record, Method | someone checking how the site works | technical, in the copy standard of section 7 |

A technical term on the surface is a bug. A surface term whose meaning changes on a deeper layer is a bug.

## 3. Vocabulary

### Surface

| Term | Means | Not |
|---|---|---|
| asteroid | one object on JPL's list of reachable near-Earth asteroids | object, body, rock (in copy) |
| the asteroid's page | the page with everything on file for one asteroid. The readout's link to it reads "Full details for <name>" | entry, record, profile |
| Δv | delta-v, the total change of speed for the cheapest round trip, in km/s. Spelled out as "delta-v (Δv)" once per page | delta-v, ΔV, dV, cost |
| diameter | the asteroid's width, in m | size |
| measured | a source on file gives a value for it | known |
| estimated | no source gives a value, so it is inferred from the asteroid's brightness and from asteroids like it | not measured, prior, guess, typical |
| mission type | a set of conditions every asteroid is checked against. Never a planned or flown mission | mission (alone, as a control's label) |
| Surface mining, Asteroid capture | the mission types, as `missions.toml` names them. A name says what is done to the asteroid, never a size, a limit or a craft; its one-sentence summary (`missions.toml`) holds no threshold either | surface work, whole-body capture |
| viability | whether one asteroid meets every condition of a mission type. Its value is **Yes** (measurements meet every condition), **No** (a measurement fails one), or a chance with the estimated mark, **35%** (at least one condition rests on an estimate). Yes and No are measured; a chance is estimated | verdict, fits, ruled out, unclear, chance it fits |
| viable / not viable / estimated | the legend's counts of Yes, No and a chance under the mission type chosen | |
| best next observation | the one observation that would most change a viability, by its plain name: "Spin measurement", "Diameter measurement". The entry adds its technical name ("Rotation lightcurve") with a hover note | would settle most |
| composition | the asteroid's class, in words: stony, carbon-rich, possibly metallic (class X: metal, enstatite or dark rock), basaltic, olivine-rich, dark and primitive, other. An estimate is the chance of each, "48% stony" | class letters, metal or rock, reflectivity |

The front page shows two states only: **measured** and **estimated**. An estimate made because a source was not checked is still an estimate; which source was not checked is a detail on the entry page.

- A **bound** counts as measured on the surface: in the legend's counts and in the readout's state word. It keeps its own mark (a dashed outline) and its value is written with ≤ or ≥.
- **No brightness on file** (no H, 6 asteroids) is neither state: nothing can be estimated. Such an asteroid is not drawn; the legend's Diameter line says "No brightness 6 (not drawn)" in the chart and "No brightness 6" in the table, where they are rows: the third state of the diameter, after measured and estimated from brightness, and the reason they have no height on the chart. Its summary values read "None" with "no brightness on file" and no state word. Its viability is No for both mission types; the legend still counts it under "No brightness", in every state, and never as not viable, so that count is the same with or without a mission type.
- **Mass** is never measured directly. It is measured when the diameter and the density it rests on are both measured, otherwise estimated, and its detail says what it rests on. A mission condition on mass that no measurement decides has the basis "estimated" unless both are measured.
- **Composition** is the class. A measured reflectivity alone gives no class: it narrows the estimate, so the summary shows the estimate ("44% stony") with the estimated mark, and the reflectivity is in the entry's Data section. With a reflectivity and no brightness, the summary says "Not classified", with no state word.
- **A state mark answers "how sure is this?"** It is left off where it would answer nothing: Δv and the orbit (JPL gives them for every asteroid), a difficulty step (not a value; its sentence says what it rests on), and a sunlight push that is not measured (nothing estimates it, so the row says "None on file").
- **Sources disagree** on a measured period: the summary gives each period, the one in use first, joined by "or" ("250 h or 2.02 h"), with "sources disagree" as its detail.
- **Gone**: an asteroid that no longer exists has a "Gone" row first in its summary, with the date and the reason. Its viability is No for each mission type, on one condition, "Still exists", not met; the reason is not repeated there.
- **Density** has its own block in an entry's Data section, after Sunlight push, on the entries that have one on file: it is what a mass rests on, not part of the push. A density not used (one computed from other values) is listed with "not used" and no state mark.
- **Chances keep one direction each.** An estimated spin is the chance of turning once in under 2.2 h, "80% under 2.2 h", as the entry's spin table and the Record give it. A condition's chance is the chance the condition is met, in its own direction ("Spin period ≥ 2.2 h", 20%), under the column "Met". The two are never printed as one figure.

### Record layer, in addition

| Term | Means |
|---|---|
| bound | a source gives only an upper or lower limit, written with ≤ or ≥ |
| not checked: *source* | a source that could hold a value was not queried or does not know the asteroid, with the reason |
| condition | one test a mission applies (orbit good enough to find again; diameter; spin) |
| met | a condition's value, under the column "Met": Yes (a measurement clears it), No (a measurement fails it), or the chance it is met with the estimated mark (it rests on an estimate). "Viability" is kept for the mission type as a whole |
| decides | what a measurement or an observation does to a condition. "Settled" is kept for a prediction on Record, whose outcome is known |
| grade | the lightcurve database's quality code for a spin period, written "grade 2−" with a true minus. Never "U 2-", never "quality U". Metal is "metal content", never a grade |
| how it was found | an upstream method code in words: "spacecraft", "lightcurve", "lightcurve inversion", "shape model", "class from a visible spectrum", "fit to optical and radar positions". Catalogue codes (SMASSII, SAGE, LCI), class-scheme names and the period type (sidereal, synodic) are not printed |
| reflectivity, spin period, Yarkovsky drift, radiation pressure, orbit condition code, absolute magnitude (H), lightcurve, signal-to-noise, thermal model | defined in a hover note at first use on the page. Method adds chondrite, g/t, random draws, spin barrier, tumbling, Tholen class, USGS, ASIME and C-type |

A hover note is the web's convention: `<dfn title>` for a term, `<abbr title>` for a symbol (Δv, H), with a dotted grey underline. On the front page Δv is spelled out in the chart's accessible name and in the hover note on its first use, since section 8 has no visible element for it.

## 4. Visual variables

| Variable | Meaning, everywhere | Never |
|---|---|---|
| position | the quantity on the axis | |
| mark shape | measured: a rock outline. Estimated: a dot (a dim outline once zoomed in) | a category of anything else |
| mark brightness | three levels: full, measured; half, estimated; faint, outside the current filter | emphasis; a mission's chance |
| line style | solid: a value. Dashed: a bound | |
| fill | viable, with a mission type chosen. Nothing else | emphasis, selection, a chance |
| glow | measured. Nothing else | a viability, selection, emphasis |
| text ink | two levels: white for content (names, values, headings, links); grey for apparatus (labels, units, axis titles, captions, notes) | certainty, emphasis, state |
| type size | hierarchy role (section 5) | emphasis |
| weight | none: one weight | |
| hue | none | |

Text and marks are separate channels. A value's certainty shows in its mark and its form (a range with the estimated mark), never in its ink. Strike-through, boxes around words and badges are not variables: a value on file that is not used is followed by the grey label word "not used", and nothing else.

A mission type changes which asteroids are in the filter, not how certainty is drawn: the not viable go faint; the viable and the estimated keep their certainty marks, and the viable are filled. A not-viable asteroid is treated exactly as one outside the filter: faint, not pickable, not in the shown count, not in the table; the legend counts it as "Not viable". The mission type means the same in the chart and the table, so a link with `m=` says the same thing in both.

A viability is a value like a diameter: Yes and No are measured and need no mark in a cell, since a chance is the only other form; a chance carries the estimated mark. The readout and the entry, which give every value a state word, give Yes and No "Measured" and a chance "Estimated".

Apparatus lines are grey: the crosshair in `edge`, the Max Δv cut-off and its label in `ink-2`. The cut-off is dashed because it is a bound. Only the focus ring around a hovered or focused asteroid is white, as the `ink` token says; a selected asteroid keeps its certainty brightness.

## 5. Type

Five roles. Nothing else.

| Role | Size / line | Use |
|---|---|---|
| title | 32/36 | an asteroid's name on its entry and in the readout; a page's title |
| heading | 20/28 | a section of a page |
| body | 16/24 | values, links, running prose |
| label | 14/20 | labels, controls, navigation, table cells and headers, legend |
| small | 12/16 | axis ticks, sources, captions, a card's cell labels on a phone |

- B612 Regular for everything except running prose, which is the system serif. Prose is text written in full sentences; a name, label or phrase is B612 wherever it sits. A component that holds prose (an entry's difficulty steps, a note under a condition, the notes under a price tag, a statement on Record, a list of labelled lines on Method in which any value is a sentence, the "Where it comes from" column of Method's difficulty lines) is set in the serif throughout, so a one-sentence item does not change face beside a two-sentence one. No bold, no italic for emphasis; italics only for symbols of quantities in the reference layer, as in the gain formula (`<var>`), with true minus signs, subscripts and a centred dot.
- All running prose is white: it is content. Grey is for labels, units, captions and source lines only, never for a paragraph.
- Two heading levels at most on any page: the title and heading roles. A lower element that is a heading for accessibility (a row name, a mission name, a difficulty step) is `h3` in the body role.
- In a summary list (an entry's or the readout's), values are body and labels and details are label.
- Numbers use tabular figures and are right-aligned wherever they are compared.

## 6. Labels, units and numbers

- **Axes and column headers:** "Quantity (unit)". The two axes are **Δv, cheapest round trip (km/s)** and **Diameter (m)**. A measured diameter is plotted at its value, an estimate at its median; the tip and the table give the estimate's 90% range.
- **Parentheses:** conventional parentheses everywhere. B612's own parentheses look square, so the font is subset without them and they come from the fallback font.
- **Units:** SI, a space between number and unit, km/s, m, t, h. A figure takes the symbol in prose too ("8 million t of water"); the word names a unit only where no figure stands with it ("Kilograms or tonnes"). In a table the unit is in the header, never in the cells. A factor is written with ×: 4×, 32×.
- **Ranges:** an en dash, the unit once: 23–85 m; bands of H too: 20–22; dollars with a shared scale word, $31–39 thousand. Every range says what it is, once, near it: "90% range" for estimates, "±1σ" for measurements. "to" in place of the dash where an en dash would misread: ends with different units or scale words (48,000 t to 2.2 million t; $1.8 million to $1.9 billion), a negative end (−2.919 to −2.881), and the two dates of a window. A scale word is never faked to save the dash ("0.048–2.2 million t" is wrong). Low end first.
- **Ranges on the front page:** the chart's tip and the table give a measured diameter as its value alone (to the field file's four figures), and an estimate as its 90% range; the tip says "90% range, estimated", and the table's Diameter column gives the range. A measured rock is plotted at that value. The readout and the entry give a measurement's ±1σ. Never "90% range" beside the measured word or mark.
- **Mass** is always a 90% range: the site computes it from draws of diameter and density, measured or not.
- **Chances:** a percent: 16%, <1%, >99%. Never "under 1%". A share that rounds to 0 or 100 prints the same way. The price tag alone counts "of 100" asteroids like it (`DESIGN.md` section 7), so no one figure reads as the value.
- **Counts:** digits with a comma separator: 7,231.
- **Precision:** a measured value to the precision its source gives; an estimate to two significant figures, trailing zero kept (3.0, 5.0), the same in Python and in `app.js`. Δv to three decimals everywhere, as JPL gives it.
- **Powers of ten:** −4.6 × 10⁻¹⁴ au/d², a true minus and superscripts; never e-notation, a hyphen-minus or ^.
- **One spelling each:** "orbit solution 118" (JPL's two lists write it both ways), "duration" for a trip's length, "diameter" for size everywhere, Yes and No capitalised, in a table cell as elsewhere.
- **Dates:** ISO, 2026-11-24. A window is two dates. Nothing says "now" or "open".
- **Missing values:** the state word, never a dash or a blank cell: "estimated", "not checked", "none listed", "None on file".
- **In a table the unit is in the header** for value tables too: "Metal (kg)" or "Metal (t)" (t when the largest figure is 10,000 kg or more), "Water (t)", "At list price ($)", "Price ($/kg)". A column with nothing in it is left out.

## 7. Copy

- **Interface text** (labels, buttons, legend, headers): nouns and noun phrases. No sentence where a label and a value do the job. No instruction where a convention does the job.
- **Prose** (entry notes, Record, Method): the GOV.UK writing standard, with three rules from ASD-STE100.
  - Sentences of 25 words or fewer; one idea each.
  - Active voice, unless the actor is unknown.
  - One word for one meaning, from section 3.
  - No phrasal verbs.
  - Plain words before technical ones; a technical term defined at first use.
  - No references to project files, scripts or internal ids on a page. A source is cited by its public name and link; a link is named by its publisher ("NASA", "The Planetary Society"), never by a bare host or an API address. A value from a published paper is cited to the paper ("Sharkey et al. 2026"), and its source is "Published papers". On Method a constant is cited by its method file's `cite`; its `source` is provenance for maintainers and is never printed. A constant's kind is tagged "from the data", "quoted" or "judgement": never "measured", which is a state.
- **Captions:** one small grey line where a table mixes kinds of value and its header cannot say so (Observe next: diameter is the measured value or the 90% range). A family of predictions that differ only by band is one grid with its statement said once (Record: class, spin and diameter by brightness).
- **Method's coverage table** is the one place the record layer's states are counted: rows Diameter, Spin, Composition and Sunlight push (Δv and the orbit are full for every asteroid), columns Measured, Bound, Estimated, "Estimated, not checked" and None (no value counts and nothing is estimated: sunlight push, and the asteroids with no brightness), so each line adds up to every asteroid.
- **Method's structure:** each topic is an h2 the rail lists: Data, Marks, Ranges and chances, Coverage, Missions, What counts as measured, Difficulty, What has flown, Metal and water, Best next observation, Not claimed, Sources. A table of figures (prices, the price cap, the difficulty lines) has a header row naming its columns. The analyses behind a material's figures are in the papers its source list cites, not on the page.
- **Headings:** sentence case, a noun phrase, no full stop. Never a full sentence acting as a header.

## 8. The front page, element by element

Each element with the question it answers. Anything not on this list does not belong on the front page.

| Element | Question |
|---|---|
| header: mark, "longshot", "prototype" | What is this, and is it finished? |
| header: Field, Observe next, Record, Method | Where else can I go? |
| header: data date | How current is this? |
| View: Chart, Table | Can I see this as a list? |
| Mission type: All, Surface mining, Asteroid capture; each segment carries its summary as a hover note. "All" because it shows every asteroid, and in the table every mission type's column: it adds, it does not take away | Which asteroids could suit this kind of mission, and what is it? |
| Max Δv (km/s), slider with its value | Which ones are cheapest to reach? |
| Find | Where is this asteroid? |
| the legend above the chart: the total; Diameter: measured, estimated from brightness, no brightness (not drawn); Mission viability, seen only with a mission type chosen | What am I looking at, and how many? |
| zoom: −, +, Reset | How do I look closer, and get back? |
| chart with its two axes | Which asteroids are big and cheap to reach, and how sure are we? |
| readout, default: a table, "Named asteroid" and "Δv (km/s)" | Where are the well-known ones? |
| readout, selected: name, diameter, spin, composition, mass, Δv, mission viability, best next observation, "Full details for <name>" | What is this asteroid? |

Removed from the front page by this table: the "Plotted" count box (its number joins the legend line), the "On file" counts table (moves to Method), the zoom factor, and the "Typical, nothing measured" link.

- **The legend is a key.** Three lines, each saying what it counts. First the total: "7,225 of 7,231 reachable asteroids" ("7,231 of 7,231" when all are shown), so the numbers close against the whole list. Then the grey label **Diameter**, what the height on the chart rests on, and its three states with their counts: Measured and "Estimated from brightness" with their marks, then "No brightness 6 (not drawn)" ("No brightness 6" in the table, where they are rows). Measured counts the rocks plotted at a measured value; an estimate is plotted at its median, which the tip and the table give as a 90% range. Then the viability line. Each row's label has a column of its own, so an item that wraps stays under its row; on a phone each label sits above its items. From 1280 px, where four columns fit beside the readout, the items line up in columns across the rows too, and the zoom buttons sit beside the total. Every line is always there and every item keeps one width whatever its count (a count is as wide as "7,231"), so the legend wraps the same in every state.
- **The viability line.** The grey label "Mission viability", then Viable (with the filled rock in the chart, the word alone in the table), Estimated and Not viable, each with its count. Estimated has no mark and Not viable none: an estimated viability keeps the asteroid's diameter mark, and the not viable are faint. Viable plus Estimated is the shown count; shown, not viable and no brightness add up to every asteroid within Max Δv and the search (the rest of the total are those the filters leave out). Its own line, because "Estimated" there counts chances, not diameters. With All it keeps its place but is not seen and not read (`visibility: hidden`, `aria-hidden`), and its counts have a fixed width, so the legend, and the chart below it, keep one height whatever the mission type: switching never moves the chart.
- **The axes and the cut-off.** Tick labels and the selected asteroid's axis tags are numbers without units; the axis titles carry the units. The Max Δv line is labelled with the control's name and value, "Max Δv 6.0 km/s", so it is not read as a tag.
- **The table.** Columns Asteroid, Δv (km/s), Diameter (m) with the state mark (a measured value, or an estimate's 90% range), then a group headed "Mission viability" with one column per mission type, each cell Yes, No or a chance with the estimated mark. With a mission type chosen, the not viable leave the table, and the group becomes "<mission type> viability" with one column per condition, then "Overall": each condition's cell is Yes or the chance it is met, so the columns show what is still unknown about the asteroids left. A condition's heading is its short name ("Orbit", "Diameter", "Spin", "Mass", from `missions.toml`), with its full label ("Diameter ≥ 30 m") as a hover note. The columns come from the method file, so a new condition or mission type needs no table code. Grouped headings are two header rows, the group spanning its columns (`scope="colgroup"`); the sort buttons are on the lower row. Under 900 px each row is a card that labels its own cells (small role), as the headers would: a mission type's cell "<mission type> viability", a condition's cell its full label; Δv sits beside the name with its unit instead of a label.
- **The readout, selected.** The name, then the summary list. Number and designation are the entry's header's, not the readout's. Its group "Mission viability" has one row per mission type: the name, the value (Yes, No or a chance), the state word, and a detail: for No the conditions a measurement fails, for a chance the conditions still open, each as "needs <condition>".
- **The control strip on a phone.** Three short rows, so the chart starts on the first screen: View beside Find, then Mission type, then Max Δv with its label beside the slider. View's and Find's labels are for screen readers only: the segments and the placeholder say what they are. With more mission types than fit one row, the Mission type segments wrap onto a second.
- **Selected segment.** The chosen View and Mission type segment is white with black text, the segmented-control convention: the one place `ground` is a text colour.
- **Data date.** In the header. Under 900 px the header has no room, so a footer line carries "Data <date>" and nothing else.

## 9. Tokens

### Colour

| Name | Value | Job |
|---|---|---|
| `ground` | `#000000` | page and plot |
| `ink` | `#ffffff` | content text; measured marks; focus ring |
| `ink-2` | `#a8a8a8` | apparatus text; estimated marks |
| `edge` | `#5e5e5e` | frames, borders, ticks, disabled controls |
| `grid` | `#202020` | gridlines, row separators |
| glow | in CSS `drop-shadow(0 0 2px #ffffff8c)`; in the field, a band of the line itself | measured marks |

Faint (outside the filter) is a mark drawn at 0.16 of its brightness.

### The glow in the field

Part of the same instanced draw: a measured outline's ribbon widens to a half-width of 2.25 CSS px and the fragment shader fades the band from 0.26 to 0.1. Blending takes the brighter value (`MAX`), so glows never add up. No blur pass and no extra framebuffer.

### Font

B612 Regular, self-hosted, one woff2 (`longshot/site/static/fonts/`), SIL OFL 1.1, subset to Latin-1 plus dashes, curly quotes, minus, σ, superscript digits, ≈, ≤ and ≥, without parentheses. Preloaded, `font-display: swap`. Fallback `system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`; prose `ui-serif, Georgia, "Times New Roman", serif`.

### Spacing and layout

- Spacing steps 4, 8, 12, 16, 24, 32, 48 px, on a 4 px grid.
- Header 48 px. Front page: the control strip, then the chart or table beside a 424 px readout, sharing one frame edge. Under 900 px, one column.
- Entry: up to 1264 px, a summary first, then sections with a sticky rail on desktop and a disclosure on phones.
- The plot is a closed frame with ticks in on all four sides; the Δv cut-off is a dashed line labelled with its value, with the asteroids beyond it faint; zoom 1× to 32×.

### Marks

| State | Field, under 4× zoom | Field, 4× and over | Text glyph |
|---|---|---|---|
| measured (plotted at its value) | white rock outline, glow | same | outline with glow |
| measured bound | white dashed outline | same | dashed outline |
| estimated | dot at half brightness | outline at half brightness | dot |
| viable (mission type chosen) | its rock filled, outline and glow kept; an estimate that is viable as its half-bright outline, filled | same | filled rock, in the chart's legend only; a cell says Yes |
| estimated viability (mission type chosen) | its certainty mark, unchanged | same | dot, before the chance |
| not viable (mission type chosen) | faint | faint | none: a cell says No |
| outside the filter | faint | faint | |
| no brightness on file | not drawn | not drawn | none |

Every rock's outline comes from its key (`longshot/shape.py`), the same rule on the entry and in the shader. The marks are glyphs, not to scale: a rock's height on the chart gives its diameter, and the entry draws the rock to scale with a scale bar. Zooming in magnifies the marks too: every mark, and its click target, grows with the square root of the zoom, up to 4× (from 16× zoom), so the rocks grow and still pull apart. Line widths do not grow.
