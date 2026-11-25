# Review of the plan for extensibility

Written 2026-11-24. Status: complete. Limits are in section 8.

Scope: what eight kinds of future change would cost under `docs/plan.md` and `DESIGN.md` as written, and what small decision now makes each cheap. Nothing here chooses the app's framework, server language or host; section 6 lists what that choice depends on.

Names used: JPL's reachable list (NHATS), JPL's table of every near-Earth object (SBDB), the French literature service (SsODNet), the Minor Planet Center (MPC) and its confirmation page for unconfirmed discoveries (NEOCP). H is the brightness figure that stands in for size.

Three words of my own:

- **Claim**: one source saying one thing about one property of one object. The plan calls this a ledger cell.
- **Row**: what an entry shows for a property after a rule has looked at every claim.
- **Registry**: a small table of ids and their meanings that ships inside the data set.

## 1. Bottom line

1. The plan's science rules are sound, but it names almost no interfaces. It fixes a few rules: one network module, a licence class per source, three cell states, an alias table. It does not say what an adapter returns, what a claim holds, how claims become a row, what a forecast record is, or what the app receives. Each of the eight changes below is cheap or expensive depending on those five shapes, and today an agent would invent each one while building a feature.
2. Three things in the plan are wrong as written and cost more to fix later than now:
   - The internal key is "JPL's permanent id". It is in neither snapshot, and JPL's own documentation shows it changing for one object (section 3.3).
   - A cell is keyed by (object, property, source). That cannot hold two values from one source, which one of the plan's ten fixture objects already needs (section 3.2).
   - "Pulls only what changed" assumes the source says what changed. JPL's responses carry no change headers, the one per-record marker JPL offers was not requested, the reachable list came back with its fields in a different order on the second pull, and 192 of the 222 records that differ between the two pulls differ only because the calendar moved (section 2).
3. The rule in `DESIGN.md` that the app never recomputes a probability holds up against items 2, 4 and 5, with five additions (section 3.7).
4. What to fix now is a handful of record shapes and id rules. What to refuse is every framework, service and general-purpose engine that could be built around them.
5. First step: build those shapes as a skeleton over the two snapshot dates already on disk, for all 43,379 objects, with no model and no app. Then hold the stack conversation with a real data set in hand (section 5).

## 2. Measured or read today

My own tests are standard-library Python on `data/snapshots/2026-11-21` and `/2026-11-24`. No JPL interface was called.

| Finding | Evidence |
|---|---|
| The SBDB snapshot has no `spkid` column. The reachable list has no id except the designation. | Field lists of both files |
| The designation joins the two lists for 7,231 of 7,231. No designation changed in 3.4 days. 24 of the 200 numbered reachable objects carry numbers above 800,000. | Own test |
| JPL's documentation says "Either `spkid` or `pdes` should be used for permanent IDs". Its lookup documentation shows Apophis with primary SPK-ID 20099942 and aliases 3264226 and 2099942, and calls 2000017 a "historical alternate SPK ID" of asteroid 17. | JPL pages, read today |
| The reachable list returned its fields in a different order on the second pull: 0 of 7,229 records match as written, 7,007 match after sorting. Neither JPL response has an ETag or Last-Modified header. | Own test; `nhats.headers`, `sbdb.headers` |
| 222 reachable records changed (an earlier count today gave 221). 192 changed only in window fields on an unchanged orbit; 191 of those had a window starting on 21 or 22 November, and for 187 the start moved from 21 to 27 November. 30 changed for another reason: 23 with a new orbit, 7 in radar fields. | Own test |
| The two JPL lists disagree within one pull, ten seconds apart: H by more than 0.05 for 327 objects, orbit solution for 17, orbit quality for 3. | Own test |
| 6,772 of the 7,231 have no physical or fitted-push field in JPL's table. They carry 134 distinct H values. | Own test |
| The full table has 43,170 asteroids and 209 comets. 35,939 asteroids are not on the reachable list. | Own test |
| Keeping every raw response: 3.3 MB gzipped per pull. A list of changed records for the 3.4 days: 49 kB gzipped. | Own test |
| "Reachable" is a query with parameters: delta-v 4 to 12 km/s, duration, stay, and six launch windows. The default is 2020–2045. Version 1.3 changed the range from 2015–2040. | JPL NHATS documentation, read today |
| SsODNet accepts several objects in one request. One request for three returned two records and, for the object it does not know, an `error` entry inside an HTTP 200 answer. Records are data model 1.2.4, stamped 2026-09-14. The values I looked at carry a method and a reference with year and DOI. `AGENTS.md` describes only the one-object route and its 404. | SsODNet page read today; one test request |
| The confirmation page lists 51 candidates under temporary names. Of 1,381 that left it between 1 August and 24 November, 737 received or matched a designation, 374 were not confirmed, 121 do not exist, 108 were not minor planets, 41 are suspected artificial. The newest line matches a candidate to an asteroid already numbered, (261568). | Two MPC pages, fetched once each today |
| Gaia DR4 is due 2 December 2026. Its content page (last updated 14 September) lists five solar-system tables, one marked new, and says "changes can be expected". | ESA pages, read today |
| Neither JPL interface has a parameter for a past date. The SBDB query offers two fields the snapshots did not request: `spkid`, and `soln_date`, "date/time of orbit determination". | JPL pages, read today |
| The research archive already holds the two JPL lists, 1,704 SsODNet records, 19 survey tables (and 6 failed fetches), the NEOWISE tables from three papers, the Spitzer file and the lightcurve database. | Listing of `data/research-data-2026-11-21.tar.zst`; not unpacked |

The 21 → 27 November jump straddles the full moon of 24 November, and JPL's window rule skips four days around full moon (`verify-obs-window.md`). That is my inference for the cause; I did not confirm it.

## 3. The eight changes

Costs are my judgement of what has to be touched, not measured effort.

| Change | Under the plan as written | Decide now | Refuse until needed |
|---|---|---|---|
| 1. Add or retire a source | New code in several places per source; no place for a new release of a source; retiring trips the release guard | A source registry; an adapter that turns a stored response into claims; tables added by a mapping file | Orchestration frameworks, plug-in discovery, matching by sky position |
| 2. Add a property or derived quantity | Depends on a storage shape the plan does not state; the cell key already fails | The claim record, a closed list of value kinds and states, a property registry, derived quantities as functions of the model's draws | Formulas in configuration, visitor-defined properties, free sliders |
| 3. Widen the population | Re-keying, and every "for all 7,229" assumption | The project's own object key; all near-Earth objects in the table from the start; "reachable" as a named population | Confirmation-page objects, our own trajectory search |
| 4. Change the method | The first change overwrites what the site said, or old code must be kept running | Three version numbers; a forecast register and a resolution log that are only ever added to | Keeping old methods runnable as a requirement; a provenance graph |
| 5. Visitor state | Open; unscorable if keyed by name | Public stable ids for objects, questions, presets and forecasts | Accounts, comments, leaderboards |
| 6. Other people using it | Licence rule stated, no single place that enforces it | One licence filter, two views; versions addressed by data and method; reported measurements as a reviewed source | Write interfaces, upload forms, a DOI per refresh |
| 7. A second front end | The rule is right and incomplete | Registries inside the data set; a sharper rule; a conformance kit | A client library, a query language, shipping draws to the browser |
| 8. Agents coding | Rules in prose, nothing enforces them | Stages with schemas; a contract test per source; invariants; two kinds of golden file; a lock on frozen files | Mocks of live services, coverage targets |

### 3.1 Adding and retiring a source

**As written.** Appendix B expects "about ten source adapters" and gives them no common shape. Three gaps follow.

- Most sources are not services. The coverage check used three services and about 25 static tables published with papers (`verify-coverage.md`). If each table gets its own module, a new lightcurve programme costs code every time.
- Nothing separates a source from a release of it. Gaia DR4 after DR3, the next lightcurve-database release and a change to SsODNet's data model (1.2.4 today) are all new releases of sources the research already used.
- Retiring has no path. The release guard holds a build when measured values disappear, so dropping a source either blocks the build or gets the guard loosened.

**Decide now.**

- A registry entry per source: id, release, kind (table or service), route, request limit, requests per full pass, licence class, status (live, frozen, retired), the properties it is the authority for, and its citation sentence.
- Fetching and reading are separate. Fetching writes the raw response and a manifest line and nothing else. An adapter reads stored responses and returns claims. It never opens a connection.
- A table source is a mapping file (column to property, unit, designation column, reference), not code.
- A release is part of the source's identity. Claims from Gaia DR3 and DR4 can coexist.
- JPL's two lists are two sources. They disagree on H for 327 objects within one pull, so the registry says which is the authority for what.
- The mapping marks fields that depend on the date of the pull (window start, end and brightness). They are stored and kept out of "what changed".
- Retiring is a dated status change. The claims stay, the row rule stops using them, and the release guard reads the status.
- The project's own analyses are sources too. Rubin photometry arrives as raw observations through the MPC (`verify-facts-venues.md`, 21 November), so a colour from it is our own measurement with a method version. Our own orbit refits are the same case (3.4).

**The named examples.**

- A new survey table or lightcurve programme: one mapping file, one stored sample, one expected output. It needs value kinds for "lower limit" and "watched, no period found"; one survey reports 33 and 46 of those among 228 targets (`verify-coverage.md`).
- Gaia DR4: one service adapter and a registry entry with the non-commercial class. The archive is closed for the week before release (21 November check), which is a week of "not checked". DR3 holds 8 reachable objects, so the gain is the exercise.
- Rubin: no new adapter. It is the MPC adapter plus a derivation of our own.

### 3.2 Adding a property or a derived quantity

**As written.** A cell is "(object, property, source)" in one of three states. `DESIGN.md` shows four states per row and adds "a limit". The plan does not say how the first becomes the second. The key fails on day one:

- 2009 BD, a fixture object, has two competing size solutions from one paper.
- SsODNet's 2009 BD reflectivity is marked "Computed" from other values (seen today). It is not a measurement and the record must be able to say so.
- Size already has three values per object: JPL's range on the reachable list, the plan's own conversion, and any measurement.

**Decide now.**

- A claim has its own id. Its fields: object key, property id, source and release, value, state, method, reference, published date, first-seen data version, licence class, retrieval manifest line.
- A closed list of value kinds: number with error bars, limit, range, category with optional probabilities, yes/no. A closed list of states. Whether "analysed, no information" from an orbit refit is its own state is an owner decision; adding a state later touches every reader.
- A property registry: id, unit, value kind, which row it belongs to. Tumbling, binarity, a radar detection and a second size estimate are then registry entries plus mappings.
- One function turns claims into a row, driven by a configuration: authority per property, and a reviewed list of known-bad values (2010 NU71). All claims stay visible, so conflicts show.
- The plan's joint model "draws all of them together". Make the draws the model's output, and every derived quantity (pass probability per mission type, mass range, price range, observe-next score) a function of the draws and one configuration entry, listed in a registry. A new mission type or price scenario is then a configuration entry, a rerun and a minor method version. Under Appendix A it is also a numbered amendment.

### 3.3 Widening the population

**As written.** The plan speaks of "all 7,229" throughout and keys on JPL's id.

- All near-Earth objects: the designation join already works. The costs are per-object pulls (43,379 requests is 12 hours at one a second, or 2.4 hours at the MPC's limit of five; SsODNet's several-object route may shorten its share, untested beyond three objects), entries with no reach or window value for 35,939 asteroids, 209 comets that need a rule, and page counts on the host (86,734 files against a 20,000 limit on one free plan, `verify-facts-venues.md`). The science already reaches outside the list: about 420 validation objects and the labelled sets.
- Confirmation-page objects: they have no designation and no JPL database entry. Nearly half never receive a designation, and some turn out to be objects already known. JPL's reachable list does not cover them, so reach would need our own trajectory search.

**Decide now.**

- The project mints its own object key: opaque, never reused, never built from a designation. JPL's ids, numbers, designations and each source's spelling are dated aliases. Records exist for merge and withdrawal. A lifecycle field (candidate, designated, numbered, withdrawn) costs nothing now and is the only thing confirmation-page objects would need from the core.
- The object table holds every near-Earth object from the first day. It is the same single request. Ask for `spkid` and `soln_date` in it from the next pull on; the second is the only per-record date JPL's table offers.
- "Reachable" is a named population: JPL's rule with its parameters, the interface version, the date, and the members. Every derived table names its population. An object outside it shows "not on JPL's list as of this date", which is a known answer and not "not checked".
- JPL changed the launch range once, and the default still includes 2020–2025. A redefinition upstream will move many members at once, so membership is kept per date and the release guard needs an approved path for it.

### 3.4 Changing the method while old predictions stay scorable

**As written.** The plan has "method 0.1", a deposit, and a rule that the version scored is "the last one whose inputs predate the resolving observation". It has no record format for a forecast or an outcome. Claims have no publication date, so "published after the freeze" cannot be evaluated; SsODNet records are 71 days behind today. "Nothing with a model in it runs in the weekly loop" leaves open whether new objects get priors on a refresh.

**Decide now.**

- Three version numbers on every output: schema (shape), method (science), data (inputs as of a date). A run manifest ties them to the raw-response hashes, the code commit, the frozen configuration and the seed.
- A forecast register that is only added to. A record holds: forecast id, question id, object key or rule id, a probability per outcome, method and data version, valid-from date, what resolves it, void date, reference forecast. A new record is written only when that object's inputs change.
- A resolution log, also only added to: question, object, outcome, the claim that settled it, its published and first-seen dates.
- Scores are a function of those two tables. Old predictions stay scorable because the predictions are stored, not because old code still runs.
- Our own refits enter as a source beside JPL's values (3.1). They do not replace them.
- Say in the plan that the frozen method runs on every data refresh, and that "model in the loop" means fitting.

### 3.5 Visitors' predictions, saved selections, comments

**As written.** Open in `DESIGN.md` and outside the prototype. Most of the cost sits in the stack, which is the owner's call. The science-side cost is nil if ids exist and high if they do not.

**Decide now.**

- Object keys, question ids, preset ids and forecast ids are public and never reused.
- A visitor's prediction, if it ever exists, is: question id, object key, probabilities, time, and the id of the site's forecast shown at that moment.
- A saved selection is object keys, a population id, a preset id and a data version. That fits in a page address.
- Nothing a visitor enters flows into the pipeline.

### 3.6 Other people using it

**As written.** Appendix B gives licence classes, a bulk download of redistributable values only, and a DOI per method release. No single place enforces the classes, and a machine interface that lists every object would be a bulk download by another route.

**Decide now.**

- One licence filter between the store and anything public, with two outputs. The page view may show a single cited value. The open view holds redistributable values and the project's own products, and replaces a restricted value with a pointer (source, reference, "value on file"). Any download or machine interface serves the open view. The two views differ for a few hundred reachable objects: about 450 have a composition-related measurement and about 416 a rotation period, mostly through restricted sources (`verify-coverage.md`).
- Inputs recorded at two levels: per object on each derived row, and per method in its manifest. Gaia's non-commercial terms follow adapted data, and ESA has not been asked whether derived values count (21 November). Keep Gaia out of what the method is built from until that is answered.
- Every record carries the outside ids (number, designation, packed designation, JPL id) so others can join without our key.
- A published version is addressed by data version and method version and never altered. A DOI goes on a method release or a quarter, not a refresh.
- A reported measurement is a source of kind "reported": a reviewed record in the repository with who, when, object, property, value, method, where the raw data were deposited, and the licence granted. It shows under its own name. Whether it can settle a forecast is written in that forecast's rule. Lightcurve data have a community archive (ALCDEF: 24,822 objects, 387,575 blocks); take the result and a pointer, not the data.

claudestronomy's standards, read today, ask for the same things: "Write down thresholds and predictions before new data arrives, and document any later changes or bug fixes" and "Publish code, methods and results so others can reproduce the work."

### 3.7 A second front end, and the test of the contract rule

`DESIGN.md` proposes that the pipeline's only output is a versioned data set with a schema, and that the app "does not recompute a probability". Tested against items 2, 4 and 5:

- **Item 2.** It holds only if the data set describes itself. Without registries inside it, every new property or mission type is an app change. It also needs a sharper line:
  - The app may select, sort, filter and count exported values, compare stored dates with the clock, and apply conversions the data set names (units; tonnes times a listed price).
  - The app may not combine two probabilities, derive a probability or a range from other columns, or sum probabilities over a visitor's filter. That last one is an expected count, which `DESIGN.md` section 7 rules out.
  - A joint probability cannot be rebuilt from its parts, so every filter combination the interface offers must be an exported preset: mission type, threshold preset, launch window.
- **Item 4.** It holds if every derived value carries its method and data version, and forecasts, outcomes and scores are their own tables. The app must never show "what we predicted" by reading current values.
- **Item 5.** It breaks in one place. Scoring a visitor's forecast is arithmetic the pipeline cannot do in advance. Either the app applies one published scoring function checked against test vectors the pipeline ships, or visitor predictions are scored in a batch. Neither is needed for the prototype.
- **The clock.** The plan has window labels read "open now" from stored dates. For 187 objects the stored start moved from 21 to 27 November between pulls. The contract has to state what a window start means, or the app will say "opens in 3 days" about objects it called open the day before.

Add a conformance kit: a fixture data set for the ten Appendix B objects and the expected facts per entry (row, state, value as text, source). A redesign or a second front end passes when it shows the same facts.

Whether the contract is delivered as files or through a query interface depends on the stack and is left open.

### 3.8 Agents doing most of the coding

**As written.** Appendix B lists rules for agents and ten fixture objects. Nothing enforces the rules. The review already predicted the failure: an agent told to get the build green will loosen the gate.

**Decide now.**

- Stages with file inputs and outputs and a schema each: fetch, read into claims, resolve into rows, model, derive, export. An agent works inside one stage, and the change in that stage's output on the fixtures is what gets reviewed.
- A contract test per source, run on stored responses:
  - the stored response parses, and the upstream version is the one expected (reachable list 1.3, SBDB query 1.0, SsODNet 1.2.4);
  - a missing response gives "not checked" for every object;
  - an object the source does not know gives "not checked", including SsODNet's `error` entry inside a 200 answer;
  - an empty field gives "looked for and absent";
  - field order does not matter.
- Invariants on any output: states come from the closed list; the same inputs give identical bytes; adding a source changes no other source's claims; shuffling designations changes no prediction; no restricted value in the open view; no mean or expected-value field; every derived row names its inputs.
- Two kinds of golden file. Truth from papers is entered by hand with the quoted sentence and is never regenerated by code. Regression snapshots are regenerated only by an explicit command, and the difference is shown to the owner.
- A lock file with hashes of the protocol, thresholds, priors and id registries. A test fails when a hash changes without a numbered amendment. It cannot stop an agent, but it makes the forbidden edit a visible two-file change.
- A test that only the fetch module imports a network library.

## 4. Interfaces to have before any feature

1. **Identity.** Own object key, dated aliases, lifecycle, merge and withdrawal records, named populations.
2. **Sources.** The registry, and the adapter: stored response in, claims out.
3. **Claims and rows.** The claim record, the property registry, the closed lists of value kinds and states, the function from claims to a row.
4. **Versions.** Schema, method and data numbers; the run manifest; the lock file.
5. **Forecasts.** The forecast register and the resolution log.
6. **The data set.** Its tables and registries, the licence filter with its two views, the conformance kit.

These are about ten record shapes and a few rules.

## 5. The right first step

My view: build the skeleton these six hang on, from what is on disk, before any feature and before the stack conversation.

1. **Owner decisions.** The object key, the three versions, the closed state list, and a contact address for JPL. The address matters first because history cannot be recovered later: neither JPL interface has a parameter for a past date. Two requests a day is about 1.2 GB a year of gzipped raw responses.
2. **The contract as a short document.** The record shapes in section 4, written before code.
3. **A skeleton over the two snapshot dates.** JPL's two lists become claims, rows and a data set for all 43,379 objects with the reachable population flagged, as data versions 2026-11-21 and 2026-11-24. It includes the list of changes between them, with the 192 calendar-only records separated from the 30 others. No priors, no model, no app, no network. The tests in 3.8 come with it.
4. **Two more sources from the archive.** One static table through a mapping file, and the 1,704 SsODNet records with "not checked" for every other object. That proves the cost of a source and the states.
5. **Then the stack conversation.** The question becomes what reads this data set.

This refines step 2 of `AGENTS.md` ("build the pipeline first") in three ways: interfaces before stages, both dates instead of one, every near-Earth object instead of the reachable list.

## 6. What the app's stack depends on

Not chosen here.

- Whether any visitor state lives on a server (predictions, comments, accounts).
- Whether the two licence views are filtered at build time or per request. "The browser never receives the whole data set" needs one of the two.
- How often a data version is published, and whether publishing is a file swap or a load into a store. The measured change is about 9 reachable records and 100 near-Earth records a day.
- The size of the field view: 7,231 points now, 43,170 if widened.
- JPL forbids embedding its interface (21 November check), so the app serves the project's own copy whatever is chosen.

## 7. Questions for the owner

1. May the project mint its own object key in place of JPL's id?
2. Should the object table hold all 43,379 from the start, with "reachable" as a named population?
3. Is "analysed, no information" a state of its own?
4. May real responses from restricted sources for the ten fixture objects be committed, or only hand-made stand-ins? It matters when the repository goes public.
5. Are reported measurements accepted at all, and only through reviewed files?
6. Visitors' predictions: yes or no decides whether the scoring exception is ever needed.
7. Should reach use JPL's default launch range, which includes past years, or future windows only? The second needs five more bulk requests per pull; I could not test it.
8. Gaia: stay out of what the method is built from until ESA answers?
9. The contact address for JPL.

## 8. Limits

- No JPL interface was called. Four JPL documentation pages were read.
- That JPL's id changes at numbering, and changed again when JPL lengthened its numbers, is my reading of two worked examples in JPL's documentation. It is not a stated policy.
- The SsODNet test was one request for three objects. Behaviour with hundreds of objects, and any limit, are untested; the page states none.
- Rubin facts and the Gaia archive closure are from the 21 November check. The Rubin status page gave me only its version and date today (v10.0, 2026-11-19).
- The archive was listed, not unpacked.
- How often reachable objects are numbered was not measured.

## Sources

Read today (2026-11-24):

- JPL SBDB query documentation: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- JPL Horizons lookup documentation: https://ssd-api.jpl.nasa.gov/doc/horizons_lookup.html
- JPL Scout documentation: https://ssd-api.jpl.nasa.gov/doc/scout.html
- JPL NHATS documentation: https://ssd-api.jpl.nasa.gov/doc/nhats.html
- SsODNet ssoCard page: https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ ; one test request to `ssocard.php?q=Bennu,2009_BD,2026_WV1`
- MPC confirmation page list: https://www.minorplanetcenter.net/iau/NEO/neocp.txt
- MPC previous confirmation-page objects: https://www.minorplanetcenter.net/iau/NEO/ToConfirm_PrevDes.html
- Gaia DR4 content: https://www.cosmos.esa.int/web/gaia/dr4 ; release dates: https://www.cosmos.esa.int/web/gaia/release
- ALCDEF: https://alcdef.org/
- claudestronomy: https://claudestronomy.com/
- Zenodo versions: https://help.zenodo.org/docs/deposit/manage-versions/
- Rubin RTN-011 (version and date only): https://rtn-011.lsst.io/

Not read today, taken from `docs/research/verify-facts-venues.md` (2026-11-21): JPL's fair-use terms, the MPC request limit, the Gaia licence and archive closure, Rubin's route through the MPC, Zenodo's limits, the host's file limit.

Project files: `AGENTS.md`, `DESIGN.md`, `docs/plan.md`, `docs/research/catalogs.md`, `verify-coverage.md`, `verify-facts-venues.md`, `verify-obs-window.md`, `verify-fit-repro.md`, `orbit-tooling.md`, `new-surveys.md`, `summaries-review.md` (reviewer 2).
