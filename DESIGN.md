# longshot: design

Written 2026-11-21; the look was decided on 2026-11-25 (section 4). Direction, not a spec; the look as built is specified in `docs/design.md`. A block quote is Adam's own words; he called his notes on the look, copy and interface "a starting point". Everything outside a block quote is **proposed** or **open**, and says which.

## 1. What it is

A site that shows what is and is not known about each near-Earth asteroid a spacecraft could reach (7,229 on JPL's NHATS list, 2026-11-21), with the uncertainty left in.

It began as a search for a missed signal that would say which asteroids are worth mining. The search came up empty (`docs/plan.md`, section 1).

> the real point of this project, for me at least, is to get involved in that community. I thought this could just be a fun way to do that.

That community is claudestronomy (claudestronomy.com), a grants programme and group for people using AI agents to find new objects in public sky data.

> I'd rather build first, some kind of prototype or MVP. There's no harm in it, and the point is to try this out and have something to demonstrate. The goal would then be to say -- your grant could expand this to XYZ, or improve ABC.

> I am not asking you to build all of this.

## 2. Stance

> I'd like to focus on realism. The difficulty, the error bars, the likely unrecoverability, the extreme uncertainty, the limited capacity with current tech/tools/motivation, etc. This is a distant frontier. But maybe not impossible... maybe the right person or group of people can tame it...

> I also don't think there's any harm going research depth on things. The fun and the research depth are perfectly capable of coexisting!

> Agreed on targeting, but I also sort of like the open-endedness of it.

Proposed readings:

- Lead with what is not known. "Not measured" stays apart from "ruled out".
- Say what would have to change.
- The plan's validation rules stay.
- Which observations would settle it stays, as one thread among several.

## 3. What a visitor gets

> My thinking was more on the psychological side -- knowing what the targets are, being excited about exploring them, seeing a price tag on what you can bring back, etc.

> I like the notion of gamifying it a bit, making predictions, scoring them, updating as observations come in, letting the public view the asteroids in a nicely designed website, putting up how much each asteroid is worth with error bars, which observations would settle it, etc.

Proposed:

- **An entry per asteroid**, the same rows for all:
  - reach: delta-v of the cheapest round trip, km/s
  - tracking: days observed, and whether the orbit is good enough to find it again
  - size
  - spin: rotation period, with its quality grade
  - surface: class and reflectivity
  - sunlight push: drift and radiation pressure, the two effects of sunlight on the orbit
- **Four states per row**: a measurement with its source; a limit; a guess from the population, labelled "not measured"; or "not checked", when a source was down, does not know the object, or was never queried. "Not checked" never displays as "not measured".
- **A difficulty ladder** on each entry: can it be found again; can it be reached, and when; is it big and slow enough to work on; is there anything in it; could today's technology bring any of it back.
- **A price tag with error bars** (section 7).
- **Elimination by mission type**, in three states: known pass, known fail, untested with a probability. Thresholds are fixed presets.
- **A record**: predictions frozen in advance, when each can be settled, and the outcomes. A miss looks the same as a hit.
- **A front page**: the field of all asteroids (section 6), with no headline sentence (section 5). The plan's one sentence and three claims (`docs/plan.md` 5.1) are not on it.

On ice:

- Visitors making their own predictions. The site's own frozen predictions stay.

> I'm not quite sure what we mean by visitors making their own predictions. Feels half-baked at the moment. Maybe put it on ice

## 4. Look

> But I want it to be more "Asteroids" the game inspired. White on black, not black on white. Like the claudestronomy website a bit, I suppose. But better designed.

> Don't want default Claudeslop.

> Yes to B612 for now.

From that:

- White on black.
- B612 Regular for labels and numbers; the system serif for sentences.

Also:

- The game's manner, not its assets: white vector lines on black and irregular outlined rocks. No copied shapes, ship, lettering or name.
- Line style carries the state, never hue. On entry rows, nothing is drawn for not checked; in the field and beside every state word, not checked is a dashed ring, so every asteroid can be found (`docs/design.md` section 3).
- No accent colour.

Reference, not a target (he said "a bit" and "better designed"). The claudestronomy home page, read from its stylesheet on 2026-11-21: black ground, white text, Times New Roman at 18 px in one 600 px column; Courier New for the navigation (letter-spaced) and for labels and table headings (uppercase, letter-spaced); grey `#a8a8a8` secondary text; `#3a3a3a` hairlines; a star field of monospace characters that twinkle. It carries a grey tagline under its title, which section 5 would rule out.

**Decided on 2026-11-25: the instrument design.** Adam judged the first prototype "somewhat hideous". Three directions were mocked up (atlas, vector, instrument) and judged.

> okay, let's go with instrument.

> Yes to B612 for now.

> keep the glow

- **The instrument design**: the field as a framed figure with labelled axes and a legend, one control strip above it, a readout beside it, every value a label with an aligned number. Specified in `docs/design.md`.
- **Type**: B612 Regular, one self-hosted file (12,620 bytes, SIL OFL, licence beside it), for labels and numbers, with a system-font fallback; the system serif for the site's sentences. One weight.
- **The glow**: a faint glow on measured outlines only, drawn in the field's shader in the same draw, no blur pass.
- **Navigation**: Field, Observe next, Record, Method. The two missions are a filter on the field (chart and table alike), not pages or links.

> surface work/whole-body capture buttons/links exist in three separate places. Why?

So a mission name appears once, as the filter, and an asteroid's own mission status appears only under its "Missions" heading.

## 5. Copy

> I don't want extraneous text, or excessive subtitles the way Claude sites are wont to include. Just clear detail and info where it's relevant and valuable.

Proposed rules from that:

- No subtitle or tagline unless it says something the heading does not. No paragraph that restates a heading.
- No explanatory text where a label and a value do the job.
- A number carries its unit, its range and its source.
- An empty state says what is missing in a few words.
- If a sentence can go without losing information, it goes.

> why does this sentence "Of the X asteroids, Y have nothing..." even exist? Do you commonly see websites with full sentences as headers like this? It's bizarre.

Decided from that, 2026-11-25: no headline sentence anywhere. The front page's numbers are in the legend and the On file counts.

## 6. The interface

> It likely can't be static, as I'll want some kind of graphical interface for the asteroids themselves, I think there will be a decent amount of statefulness.

Proposed:

- Each asteroid drawn as a line figure to scale, the size uncertainty as nested outlines, turning at its measured rate. 2022 OB5 turns once in 92.5 seconds (1.542 ± 0.001 min, Alarcon et al. 2026). An asteroid with no measured spin does not turn.
- A field of all of them, placed by delta-v (km/s) against size. As built, the field's rocks are glyphs of a fixed size, not to scale, with zoom to 32x (`docs/design.md` section 3); the entry's rock is to scale.

Open:

- What state there is: saved selections, the view. Visitors' own predictions are on ice (section 3).
- Where it lives: the browser, a server, both. Whether there are accounts.

## 7. The price tag and the last rung

What the sourced figures say (`docs/research/value-inputs.md`, `capability.md`). They come from a model whose three weakest inputs are placeholders, so the top of each range can move by up to a factor of four.

- A typical reachable asteroid is about 15 m. Of 100 like it, about 43 hold no platinum-group metal in separable form, about 52 hold $0.4–14 million of it in the rock at 20 November 2026 list prices, and about 3 are metal-rich, hold far more, and cannot be identified from Earth. Counting the zeros, three in four hold under $2 million.
- About 89 in 100 hold no water.
- Every dollar figure moves by a factor of 1.8 between 2025 average prices and those of 20 November 2026.
- For an unobserved asteroid the tag depends only on its brightness. Each magnitude changes every figure by a factor of four.
- Three missions, all by space agencies, have returned about 127 grams of asteroid in total. The largest haul, 121.6 g from Bennu, cost about ten million dollars a gram in the money of the day. All three asteroids were hundreds of metres wide and slow-turning.
- No spacecraft has touched an asteroid as small or as fast-spinning as a typical target. One is in position at an 18 m asteroid (Tianwen-2, since July 2026); no sampling attempt has been reported.
- Neither research round found a company that has reached an asteroid.
- Returning tonnes has been proposed since the 1990s and first costed in 2012. It has not been built.

Proposed handling, from the research's own checkers:

- Lead with kilograms and tonnes.
- One denominator ("of 100 such asteroids") and one-sided statements ("three in four hold under $2 million"), so no single figure can be lifted out as the value.
- No mean, median or expected value anywhere, the data files included.
- Water in tonnes only. Nobody buys water in orbit.
- The last rung in fixed, dated words: done (three times, by space agencies); not yet attempted; proposed.

A dollar figure shows. The checkers had advised against one, citing the mining industry's reporting code (JORC, clause 51), which forbids dollar values on unmined material.

> I don't know that we should adhere to mining notions of not attaching any value whatsoever. I feel like conservative estimates with well-researched large error bars should be fine.

Proposed form: conservative, as a range with the chance of nothing first, at dated list prices, for what is in the rock before any cost.

Before anything is displayed: `verify-value-inputs.md` lists eight corrections and the three placeholder inputs; `verify-capability.md` lists seven corrections.

## 8. Architecture

> Python through uv is fine -- I understand almost all astronomy data is interfaced through python.

Decided on 2026-11-24. Adam asked for "the most performant website possible given the goals" and agreed to this stack ("sounds great to me"):

- **Delivery.** Pre-built files, no server. Nothing needs computing per request, so everything is computed ahead of time. The interface is graphical and stateful in the browser; "static" describes only how the files reach it.
- **The field.** Hand-written WebGL2: every rock in one instanced draw call, rotation computed in the shader.
- **Field data.** One small binary file of typed columns, loaded straight into GPU buffers.
- **Entries.** One pre-rendered HTML page per asteroid. The app fetches the same page to fill its side panel.
- **Client code.** Plain JavaScript modules and GLSL. No framework, no bundler, no three.js.
- **State.** The URL, plus browser storage for small conveniences. No accounts.
- **Type and style.** Hand-written CSS. B612 Regular for labels and numbers and the system serif for sentences (section 4).
- **Generator.** The Python pipeline writes every file. Standard library only.

The pipeline's output is the only thing the app reads. The app does not recompute a probability.

Open:

- Where it is hosted, when it is published.

Constraints from the data sources:

- JPL forbids embedding its interface in a site, so the site ships its own copy.
- Any value from any source may appear on any page and in the site's data files. Every source is cited once, with the citation it asks for, in the Sources section of the method page; an entry names the source beside each value.

> we can use any value and just have citations on the site somewhere. They don't need to be cited inline.

## 9. Prototype

> We should build something with the data we have, then decide what more we need and how we should be pulling/storing/etc. All I meant re: the static data was that for the finished product that's not enough. But for actual building realistically we should just start with what we have and get some kind of MVP or something with some functionality and then iterate from there.

In:

- The ledger for all reachable asteroids from the data already on disk (pulled 21–24 November 2026, and dated as such on the page), in the four states of section 3.
- Elimination for two mission types: surface work on a larger body, and capture of a whole small one.
- The untested objects ranked by what one observation would settle, with when each can next be pointed at.
- The price tag and the difficulty ladder, as far as section 7's open question allows.
- A record with the predictions it will hold and when each can be settled.
- The asteroid figure on each entry and the field of all of them.

Out, and on the roadmap as what a grant could expand or improve (`docs/plan.md`, section 3.5):

- Telescope time for the untested objects.
- The orbit test on labels nobody has analysed.
- Our own refit of drift and radiation pressure.
- An expert read, the permission emails, and a public launch.

Built on 2026-11-25 and rebuilt the same day to the instrument design (`docs/build-report.md`). It runs locally until Adam says to put it on an unlisted address, marked as a prototype.

## 10. Open decisions

- The name.
- The host (section 8).
- A role email address as the contact JPL's interface requires.
- Whether to write a short paper on the orbit test.
- What happens if no expert agrees to read the public launch.
