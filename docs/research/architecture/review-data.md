# Data review: keeping longshot correct while the data moves

Written 2026-11-24 by a reviewer reading the plan as the data engineer who inherits it in two years. Scope: maintainability and correctness over time. Nothing here chooses the app's server, language, framework or host; section 4.6 says what that choice depends on from the data side.

How to read the evidence tags:

- **[T]** my own test today on the two local JPL pulls (`data/snapshots/2026-11-21` and `/2026-11-24`). The script is in the appendix and reproduces every [T] number.
- **[D]** a documentation page read today through a summarising fetch. Words in quotation marks are what the fetch returned.
- **[P]** the project's own research files, not re-checked today.
- **[I]** my inference. Not verified.

Terms used below. An *orbit solution* is JPL's current fit of an asteroid's path; each new fit gets a new solution number. The *condition code* is a 0–9 grade of how well the orbit is known (0 is good). *H* is the brightness figure that stands in for size. A *provisional designation* is the name an asteroid gets at discovery (2010 PS66); *numbering* is when it later gets a permanent catalogue number, which replaces the designation as its primary name.

## 0. Verdict

The plan is sound on what to compute and thin on time. It was written around one frozen pull and a sequence of releases, and it treats updating as a weekly re-run of the same thing. Five things in it will fail in the first months of live data:

1. **The identity key.** The plan keys everything on "JPL's permanent id". The two pulls do not contain that id at all [T], and JPL's own documentation shows it changing for the same object [D]. Page addresses, random seeds and frozen forecast lists would all hang off it.
2. **"Not checked" has no record.** The ledger's three states are defined per cell, but nothing in the plan stores the act of looking. Without that, a missing value cannot be told from a failed request, which is the one failure AGENTS.md says must never happen.
3. **One version axis.** A "release" bundles data, method and site. Daily data needs them separated, or either the science cannot be frozen or the site cannot be current.
4. **The release guard.** "Hold a release if values move outside tolerances" assumes a person promoting a batch. The measured churn has normal days that would trip any simple tolerance, and one predictable event that changes 30,000 rows at once [I].
5. **Observing windows read from stored dates.** JPL's window dates are clamped to the day JPL computed them and are interrupted around each full moon [T, D]. Read naively they say "opens in 3 days" for objects that were observable a week ago and will be again, and 85% of the values that changed on the reachable list are window and radar-opportunity fields moving with the calendar [T].

None of this needs a large system. The project is small: 7,231 objects, about 108,000 filled values from the reachable list and 1.3 million from JPL's full near-Earth table [T], and about 800 changed values a day [T]. The whole history fits in one file for decades. What it needs is the right shape on day one, because upstream keeps no history: a day not captured is gone.

## 1. What the two pulls show beyond the headline churn

Everything in this table is [T] unless marked.

| # | Finding | Why it matters |
|---|---|---|
| F1 | The bulk request asked for 53 fields. `spkid` (JPL's object id) and `soln_date` (date of the orbit solution) are not among them, and the request did not set `full-prec`. The documentation lists all three [D]; without `full-prec` "data are returned in reduced precision for display purposes" [D]. All 679 non-zero drift values (A2) have two significant figures, and 14 reachable objects sit between 2.7 and 3.3 sigma on those rounded figures. | The identity key the plan names is not in the data. The values behind the density ceilings are display-rounded. Changing the request later makes every value string change on one day. |
| F2 | Within one reachable-list file, rows use 2,052 different key orders (2,059 in the second pull). The raw bytes of two pulls differ even where nothing changed; 7,007 of 7,229 rows are identical once keys are sorted. | Hashing raw bytes cannot detect "nothing changed". Change detection needs a canonical form. |
| F3 | The reachable list reports its count as a string (`"7231"`), the full table as an integer (`43379`). Neither response carries a date in its body, and neither has ETag or Last-Modified headers. | The retrieval time is ours to record. A pull cannot ask "only what changed". |
| F4 | All 342 changed rows in the full table carry a new orbit solution number. No row changed without one. 1,824 values changed; none is a physical measurement. H changed for 37 objects (median 0.03 magnitude, largest 0.17). | The solution number works as a per-row version for everything orbit-related, and as the trigger for per-object follow-up pulls. H is refitted with the orbit, so every figure derived from H moves with it. |
| F5 | The solution number is written three ways: a bare number (26,104 rows), `JPL n` (17,131), and other forms such as `E2026-TE5` (144). Twenty objects flipped from the bare form to the `JPL` form between the pulls. The reachable list always uses the bare form, so 1,641 rows mismatch as strings; only 17 are real differences. | A silent format migration is under way in the data now. Any string comparison of this field is wrong. |
| F6 | Those 17 reachable-list rows were computed on a solution one behind the one the full table shows. 2011 AA37, a fixture object, is one (48 against 49). | JPL's two tables disagree with each other on the same day. Each value's date is its solution number, not the pull date. |
| F7 | Of 222 changed reachable-list rows, 199 changed only in the next-window and radar-opportunity fields (415 of 487 changed values). In the first pull the earliest window start is 2026-11-21 (212 objects); in the second it is 2026-11-27 (206 objects) and none is earlier. 187 objects moved from the first date to the second. The second pull was taken at 2026-11-25 01:12 UTC, and the full moon was on 24 November. JPL's rule: "Observations are excluded for the 4-day period around each full moon" [D]. | The window start is the later of JPL's computation day and the end of a moon gap. It is not when the window opened. Most "change" on the list is the calendar advancing. |
| F8 | Twelve objects with a window open on 21 November have no window at all three days later. Others jumped to their next window, years away. Of the 187 rolled rows, 112 show a fainter peak brightness and none a brighter one. | The table lists only the next window [P], so a window that has passed disappears upstream. The peak brightness is for the part of the window still ahead. |
| F9 | 2026 VK2's delta-v went from 7.274 to 6.820 km/s on one new orbit, so the plan's "1,388 under 7 km/s" is already 1,389. 23, 28 and 27 objects sit within 0.02 km/s of the 5, 6 and 7 km/s cuts; 47 within 0.1 magnitude of H 24; 143 at 11.9 km/s or more, the edge of the list. | Counts in the plan's elimination table move within days. Objects near a cut will cross it and cross back. |
| F10 | 2026 VQ5 joined the reachable list between the pulls with a delta-v of 11.989 km/s and one viable trajectory. It was already in the full table on 21 November. | List membership is a threshold on a fitted number. Objects will also leave. The JPL page does not say what happens to them [D]. |
| F11 | Two of the ten fixture objects changed in the full table in 3.4 days (2011 AA37, 2026 QQ8) and three in the reachable list (those two and Kamoʻoalewa). | Fixture values must be pinned to a stored pull. A fixture compared with live data fails within the week. |
| F12 | Bennu's diameter uncertainty is the string `0.00`. Rotation periods arrive as `10.` (2011 AA37) and `250.` (2013 NJ). 103 diameters have no uncertainty. Three first-observation dates are partial (`YYYY-??-??`, documented [D]). Six reachable objects have no H. Kamoʻoalewa is spelled with a backtick. | The string carries information a float loses. Zero and missing uncertainty both occur and neither means exact. |
| F13 | The near-Earth table includes 209 comets. All 3,874 numbered asteroids keep their provisional designation in parentheses in `full_name`. | Widening the scope brings in comets. Numbering can be detected from the bulk table alone. |
| F14 | The folder named `2026-11-24` holds a pull made on 2026-11-25 UTC. The first pull has no header file; its retrieval time survives only as a file timestamp. | The first two data points already have a provenance gap and a time-zone ambiguity. |
| F15 | Sizes. One pull of both lists is 18.4 MB raw and 3.3 MB gzipped. The rows that changed in 3.4 days are 214 kB raw and 40 kB gzipped. | A full copy every day is 1.2 GB a year gzipped. Changed rows alone are about 4 MB a year. |

One test request each to two other services, today:

| # | Finding | Why it matters |
|---|---|---|
| F16 | SsODNet's card for Bennu (https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu) has no ETag or Last-Modified either. Its body carries `"ssocard": {"version": "1.2.4", "datetime": "2026-09-14T23:00:01+00:00"}`. Its id is the name, `Bennu`. Uncertainties are pairs (`"error": {"min": -0.019, "max": 0.019}`). Density is 1204.673 where JPL gives densities near 2.67, so the units differ by 1,000 (JPL's is g/cm³ [D]; the card does not state its own and points to a separate metadata file). Its H is 20.68, credited to the Lowell catalogue; JPL's is 20.21. Its rotation period is labelled sidereal; JPL defines its own as synodic [D]. The first reference under "method" for the diameter is a 1992 paper about a different asteroid, which describes the method class; the actual source is in `bibref`. | The card's build date is 71 days old and is the only freshness signal. Its id changes when an object is named. Units, the meaning of "period", and H all differ between sources. A parser that takes the first reference credits Bennu's size to the wrong paper. |
| F17 | The Minor Planet Center's identifier service (https://data.minorplanetcenter.net/api/query-identifier) resolves `2016 DO` to the primary designation `2020 AB1`, with `2016 DO` listed as secondary. It accepts up to 100 designations a call [D]. | Two designations can be one object, and the later one can be primary. There is a cheap way to ask. |

## 2. Where the plan assumes a snapshot

### 2.1 Appendix B, line by line

| Build note | What it assumes | What breaks, with the measured churn | Change |
|---|---|---|---|
| **Fixture slice**: ten objects, each a failure mode | Failure modes are properties of an object at one moment | Two to three of the ten changed upstream in 3.4 days (F11). None of the ten exercises a change over time: a rename, a merge, leaving the list, a window rolling, a format flip | Pin fixtures to stored pulls. Add fixtures for time, built by editing copies of real rows (section 5.3). Run the ten against live data only as invariants, never as equal values |
| **Network**: one module, writes every response to the snapshot store | A response is a file | No record of the request, time, status, headers or API version (F14). No record at all when a request fails, which is the record "not checked" depends on | One row per request, written whether it succeeds or not (section 4.3, `fetch`). Canonical hash as well as byte hash (F2) |
| **Data**: content-addressed, backed up, only manifests committed; "snapshots are under 1 GB" | A handful of snapshots, committed by a person | A daily job would commit to the code repository every day, against the rule "commit only when asked". "Under 1 GB" is a one-off figure; a year of daily pulls of the two lists alone is 1.2 GB gzipped (F15) | The manifest of routine pulls lives with the data. Git holds manifests only for frozen things: fixtures and method releases. Name the backup target; this store is the one asset that cannot be re-fetched |
| **Identity**: the key is JPL's permanent id; alias table; addresses derive from the key | JPL's id is permanent and present | It is absent from the pulls (F1). JPL's documentation gives Thetis a "historical alternate SPK ID of 2000017" against a current primary of 20000017, and lists `3264226` among the aliases of Apophis, whose primary id is now built from its number [D]. So the id changes when an object is numbered [I], and the numbered form has itself changed at least once. Other sources do not know it: SsODNet's id is a name (F16) | Mint our own key. Treat every upstream id, JPL's included, as an alias with dates (section 4.4) |
| **Ledger cells**: each (object, property, source) is measured, looked for and absent, or not checked | The state is a fact about the cell | It is a fact about the cell *as of a check*. "Absent" needs a stored record that the source was asked and answered. A cell checked 70 days ago against a source that has rebuilt since is not "absent" | A `coverage` record separate from values, and a freshness window per source (section 4.3) |
| **Licences**: a class per source; our products are CC BY except rows with a non-commercial input | Inputs of a derived row are known | Nothing records which inputs a derived value used. With daily recomputation the class of a row can change when an input appears | Each derived value stores its inputs (section 4.3, `derived_input`); the class is computed from them on every run |
| **Fitter** | Run by hand per release | Unaffected by daily data, as long as it stays out of the daily job | Keep. A fit result is a derived value with its inputs recorded, so it can be marked "newer tracking exists" when the object's solution number moves (F4) |
| **Fit protocol**: record the force law with every value | Values come with their convention | The bulk table drops the force law [P] and rounds to two figures (F1). A drift value stored as a bare number cannot be compared with another source's | Every value has a `qualifier` (section 4.3). JPL bulk values are stored with the law marked unknown until the per-object record is read |
| **Site build**: no probability computed in the browser; schema and manifest; a DOI per method release and per frozen forecast | Forecast versions are discrete releases | "The last release whose inputs predate the resolving observation" has no meaning when inputs change daily | Replace "release" with a data state and a method version (section 3) |
| **Release guard**: staging, then promote; hold on tolerance; banner at ten days | A person promotes; the data is one thing with one date | No person promotes daily. Normal days break simple tolerances: 222 of 7,229 rows changed in one interval (F7), and a common-epoch change would alter orbital elements for 30,476 rows at once [I]. "Each source's date" is ambiguous: SsODNet's card was built on 14 September and fetched in November (F16); by its own date the banner never clears, by ours it never shows | Guards per source at ingest, automatic accept, hold-and-notify on failure, last good data served per source (section 5). Three dates per source: upstream's own, last successful check, last change |
| **Rules for coding agents**: every number traces to a script output | Outputs are files from one run | Tomorrow's number differs. The trace has to name the data state and the method version | Stamp both on every derived value and every export (section 3) |
| **Effort notes**: "later pulls are incremental" | The services can say what changed | They cannot (F3, F16) | The two JPL lists are pulled whole (18 MB) and diffed locally. The diff drives per-object pulls: a new solution number (F4) means fetch that object's observations; a new card build date on one canary object means re-crawl SsODNet |
| **Watch list**: MPC format change, fitter releases | The drift is announced | Add what is not announced: the solution-number format flip in progress (F5); JPL's API versions, unchanged since 2019 and 2021 [D] while the content changes daily; the reachable list's default launch range, which last moved in 2019 [D] | Section 5 |

### 2.2 Appendix C, line by line

| Package | What it assumes | What breaks | Change |
|---|---|---|---|
| **WP1 ledger** | Priors are computed once and attached | H changes with each new orbit (F4), and the plan says each magnitude moves every figure by a factor of four. A prior stored as a number per object is stale within days for objects being tracked now, which are the new ones | A prior is a frozen table (the method) applied to today's H. Applying it is a pure function and runs on every change. If the model draws samples, the seed is fixed from our object key and the method version, or the output jitters between runs and the change log fills with noise |
| | "Conflicts shown" | Two routes to one paper look like agreement. 2010 NU71's wrong size is in both JPL and SsODNet from the same table [P] | Store the original reference with each value and count independent sources by it |
| | H is one thing | Bennu's H differs by 0.47 magnitude between two sources (F16), which is 24% in size | Store H per source. The method names which one its tables were built on |
| **WP2 elimination and "observe next"** | Hard cuts on size, spin and orbit quality; "joined to when the object can next be pointed at" | Objects near a cut flip (F9). The window fields are the least stable in the data (F7) and a passed window vanishes (F8), so the ranking reorders daily with no new information | Keep probabilities in the data and apply presets at the last step. Mark window fields as clock-driven so they are excluded from "what changed". Keep closed windows in history; the record needs to say whether a listed window passed unobserved |
| | Named company targets must pass | The named targets are themselves list members whose numbers move | Run that check on every data change, as a test with a visible result |
| **WP3 orbit test** | "The list of designations is fixed and hashed in R1, before the ledger ingests any class" | Designations change on numbering, so a hashed list of designations stops matching the catalogue. SsODNet already carries 2026 papers [P], so an automatic ingest would bring sealed labels in through the side door | Hash the list as our key plus the designation on that date. Add an embargo: a value from a listed reference is stored and dated but excluded from every derivation until released. This filter must exist before the first ingest that feeds a prior |
| **WP4 forecasts** | Rules such as "any reachable asteroid of H 26–28 that gets a class" | "Reachable" and "H 26–28" are both moving (F4, F10). The rule does not say on which date they are read | The protocol must name the date. The store must answer "what was H, and was it on the list, on that date" (section 3.2) |
| | "Published after the freeze" | Three different dates: when it was observed, when it was published, when we first saw it. SsODNet lags about two months [P], so a period measured before the freeze can first appear after it | Store all three where known. State the tie-break in the protocol |
| | Density ceilings from 154 published drifts | The 154 is reproduced from today's pull [T], and it is not a constant. Drift or radiation-pressure figures changed for four asteroids in 3.4 days, two of them on the reachable list [T]. Fourteen reachable objects sit between 2.7 and 3.3 sigma on figures rounded to two digits (F1), so membership of the 3-sigma set and the "minus 2 sigma" rule can flip from rounding alone [I] | Request full precision. Treat the ceiling as a derived value recomputed on change, with its history kept |
| **WP5 dynamics** | A fit is current until the next release | 24 reachable objects got a new JPL orbit in 3.4 days [T] | Not in the daily job. Each fit records the tracking it used; the page says so when newer tracking exists |
| **WP6 observations** | A ranking sent in a message | The ranking is a moving product | Send a dated data state, not "the ranking" |

### 2.3 Elsewhere

- **Plan section 4**: "A weekly unattended refresh... Nothing with a model in it runs in the weekly loop." Read strictly, a new object (about 12 a week) gets no prior until someone runs a method release. The useful rule is narrower: nothing that *tunes* a model runs unattended; *applying* a frozen method runs on every change.
- **Plan section 4**, weekly. JPL says the reachable list is the result of a "daily analysis" [D]. A weekly pull misses windows that open and close inside the week: 12 of 212 open windows were gone in 3.4 days (F8). Two requests a day is the smallest cadence that loses no history.
- **Plan section 5.3**: "Day to day, with no rebuild: window tabs read 'open now' or 'opens in 9 days' from stored dates." This is wrong on the evidence of F7. Do not derive "open now" from a stored start date beyond the day of the pull.
- **Plan sections 5.1 and 5.2**: the front-page sentence has the count typed in. The docs already say 7,229 where the list says 7,231. Every count on the site is rendered from data. "What changed this week" needs a change history that can only be collected going forward.
- **Plan section 3.5**: gates such as "an expert has read it" cannot apply to daily data. They apply to a method release. The site states both: "method 0.1, read by X on a date; data through D".
- **Appendix A**, the deposit lists "hashes of the input snapshots". With a continuous store this becomes one hash of a data state (section 3.1).
- **DESIGN.md section 3** has four states per row; Appendix B has three per cell. They are consistent if the row is derived from the cells: a measurement or a limit when any source has one; a labelled guess when every source able to supply the property has been checked and has nothing; not checked otherwise. A property with two of five sources unchecked needs a display rule; the data can support "not measured, 2 sources not checked".
- **DESIGN.md section 7**: "No mean, median or expected value anywhere, the data files included." A distribution stored as quantiles would include the median. The encoding has to be chosen with this rule in view (section 4.3).
- **DESIGN.md section 7**: every dollar figure depends on a price list dated 20 November 2026. Prices are a fourth upstream feed. If they update with the data, no dollar figure is reproducible or comparable across days.
- **AGENTS.md**, "then all 7,229": the object count is not a constant to test against.

## 3. Frozen science on a current site

### 3.1 Three clocks, not one

| Thing | Identified by | Changes | Immutable once written |
|---|---|---|---|
| Raw response | sha256 of its bytes | never | yes |
| Request record | sequence number, UTC time | never | yes |
| **Data state** | batch number N, plus a hash that chains every accepted batch up to N | every accepted pull | each state, yes; the store only grows |
| Value as a source stated it | its own row, with the batch that first saw it and the batch that stopped seeing it | never rewritten; superseded by a new row | yes, apart from the closing batch number |
| **Method version** (0.1, 0.2): prior tables, thresholds, mission presets, class mapping, unit and property registry, source preference rules, price scenario, the code commit | a git tag and its hash; deposited at release | by hand, at a gate | yes |
| Derived value | (object, property, method version, hash of its inputs) | a new row whenever an input or the method changes | yes |
| Frozen forecast | id, rule text, method version, data-state hash at registration, deposit DOI | never | yes |
| Forecast outcome | forecast, object, the value that resolved it, the data state it was scored with | appended; a correction is a new row | yes |
| **Export schema** (what the app reads) | its own version number | when columns change | per version |
| Current view, the export, the site | rebuilt from the above | every run | no, and nothing depends on them |

The data state is the piece the plan lacks. Because values are never rewritten, "the data as it stood after batch N" is a query, not a copy. A short hash commits to the whole history: `state_hash(N) = sha256(state_hash(N-1) + source + sha256 of batch N's canonical rows)`. That hash is what a deposit records in place of "hashes of the input snapshots". It proves a data state existed on a date without publishing any restricted data, which matters because no data deposit is allowed before the permission emails are answered.

Every page footer and every export carries the pair: `data state 412 (2026-12-03) · method 0.1`.

### 3.2 What the science gets

- **A deposited protocol and priors frozen as method 0.1.** A git tag, deposited once. The priors were built from a set of measured objects; the deposit names the data state they were built from.
- **Forecasts scored against inputs that predate the resolving observation.** For a resolving measurement, take the earliest date known for it: observation, publication, or the batch in which we first saw it. Read H and list membership from the last data state before that date. Score with the method version registered before that date. The store answers each of these with one query. Which of the three dates governs when only a publication year is known is a protocol decision the plan has not made.
- **Sealed labels.** Values from embargoed references are ingested, dated and excluded. Their arrival time is on record, which is stronger than not having looked.
- **Corrections.** If the value that resolved a forecast is later withdrawn upstream, the outcome is not edited. A new outcome row is appended and the page shows both.

### 3.3 Reproducing today's number next year

1. The page shows the data state and the method version.
2. Check out the method tag. Its lockfile pins the Python packages.
3. Query the store as of that batch number: rows first seen at or before it and not closed at or before it.
4. Run the derivation. It is a pure function: no network, no clock (dates are arguments), no unseeded randomness, a fixed rounding rule on output.
5. Compare the hash of the result with the export hash recorded on the day.

Two things can still break this, and both have a cheap answer. A parser fix changes how old raw data is read, so the parser version is recorded per batch and in each export manifest. And the store itself is a build product: it can be deleted and rebuilt from the raw responses and the request journal, and a test does exactly that and compares (section 5.3).

### 3.4 History without a copy per day

- **Raw responses.** The history below does not depend on a copy per day; the changed rows of both lists come to about 4 MB a year (F15). Keep every raw response anyway. For the two JPL lists that is 1.2 GB a year gzipped, and raw bytes are the only protection against discovering in 2028 that a field was misread since 2026. They can be thinned later; they cannot be recovered later. Per-object documents are stored once per distinct content: a card that has not been rebuilt costs one small coverage row per check.
- **Values.** A new row only when a source says something new. Measured: about 640 changed values a day in the full near-Earth table and about 145 on the reachable list (F4, F7). That is under 300,000 rows a year for all 43,379 objects.
- **Looking and finding nothing new.** One coverage row per source per batch for a bulk list; one per object per check for a per-object source.

## 4. Storage model

### 4.1 The four options

| | (a) dated full snapshots in files | (b) current values plus a change log | (c) append-only statements by source | (d) raw responses, tables rebuilt from them |
|---|---|---|---|---|
| History | yes, as whole copies | only if the log is complete; two writes that can drift apart | yes | yes, in the raw layer |
| Provenance per value | file level only | weak unless every change carries its source and batch | yes | yes, down to the bytes |
| Three ledger states | no; a missing value and a failed pull look alike | needs extra columns | needs a separate coverage record, then yes | no query model of its own |
| Conflicting sources | not addressed | forces one winner at write time, which bakes a method choice into the data | all coexist | not addressed |
| "What changed" | load two files and diff, every time | yes | yes, by batch | needs the tables |
| State as of a past date | pick the file | replay the log backwards | one query | rebuild to that date |
| Survives a parser mistake | yes | no; the wrong value is the stored value | no | yes |
| Renames | joins by designation break | key decides | key decides | key decides |
| Per-object sources (a 2-hour crawl) | a "snapshot" is never one instant | fine | fine | fine |
| Cost at this size | 1.2 GB/yr for two lists | trivial | trivial | 1.2 GB/yr raw plus trivial |

**Recommendation: (d) underneath, (c) on top, with (b)'s current table as a rebuilt view.** Neither half is enough alone. Raw responses with nothing above them cannot answer a question; statements with nothing below them cannot be repaired after a misreading. Option (a) is what the raw layer amounts to for a bulk list, so the two existing pulls fit as they are. Option (b) is the natural shape for an app and the wrong one for a ledger whose point is that sources disagree.

At 7,231 objects, or at 43,379, every table below fits in one file on one disk. For the pipeline's working store I would propose SQLite: it ships with Python, needs no server and adds no package. That is a proposal for the pipeline only and needs the owner's yes. What would change it: more than one writer, or an app that must run live queries against a server database (section 4.6).

### 4.2 Files

```
data/                          outside git; the one thing that must be backed up
  raw/sha256/3f/3f9a….zst      exact bytes of every response, written once, never changed
  journal.ndjson               one line per request, appended; the plain-text twin of `fetch`
  longshot.db                  every table below; can be deleted and rebuilt from raw/ + journal + git
  export/<utc timestamp>/      what the app reads, with manifest.json
```

In git: adapters, the property and source registry, method artefacts, annotations, fixture pulls with their manifests.

### 4.3 Tables

```sql
-- Every request ever made, successful or not. No batch exists without one; a failure still leaves a row.
CREATE TABLE fetch (
  fetch_id      INTEGER PRIMARY KEY,
  source        TEXT NOT NULL,      -- 'jpl.sbdb_query', 'jpl.nhats', 'ssodnet.ssocard', 'manual.table'
  request       TEXT NOT NULL,      -- method, URL and every parameter, defaults written out
  scope         TEXT NOT NULL,      -- 'all' for a bulk list, else the object asked about
  started_at    TEXT NOT NULL,      -- UTC
  http_status   INTEGER,
  headers       TEXT,
  body_sha256   TEXT, body_bytes INTEGER,
  api_version   TEXT,               -- as received: signature.version, ssocard.version
  upstream_date TEXT,               -- upstream's own stamp if it has one (ssocard.datetime); NULL for JPL bulk
  outcome       TEXT NOT NULL       -- 'ok','http_error','timeout','not_json','error_in_body','guard_failed','unknown_object'
);

-- One accepted ingest. batch_seq is the data-state clock.
CREATE TABLE batch (
  batch_seq INTEGER PRIMARY KEY, source TEXT NOT NULL, parser_version TEXT NOT NULL,
  accepted_at TEXT NOT NULL, rows_sha256 TEXT NOT NULL, state_hash TEXT NOT NULL
);

-- Our own key. Minted once, never reused, never derived from any upstream id.
CREATE TABLE object (
  object_id INTEGER PRIMARY KEY, created_batch INTEGER NOT NULL,
  status TEXT NOT NULL,             -- 'active','merged','missing_upstream','deleted_upstream'
  merged_into INTEGER REFERENCES object
);

-- Every name any source has used, with the batches between which it held.
CREATE TABLE designation (
  object_id INTEGER NOT NULL REFERENCES object,
  scheme TEXT NOT NULL,             -- 'provisional','number','name','jpl.spkid','mpc.packed','ssodnet.id'
  value TEXT NOT NULL,              -- as received: 'Kamo`oalewa'
  normalized TEXT NOT NULL,         -- one rule per scheme: case, spaces, punctuation
  source TEXT NOT NULL, is_primary INTEGER NOT NULL,
  first_batch INTEGER NOT NULL, closed_batch INTEGER
);
CREATE UNIQUE INDEX one_live_owner ON designation(scheme, normalized) WHERE closed_batch IS NULL;

-- One version of one upstream record, whole. Generic; survives upstream adding a field.
CREATE TABLE source_row (
  source TEXT NOT NULL, object_id INTEGER NOT NULL, row_sha256 TEXT NOT NULL,  -- of sorted-key JSON, not of raw bytes
  row_json TEXT NOT NULL, upstream_date TEXT,
  first_batch INTEGER NOT NULL, closed_batch INTEGER,
  PRIMARY KEY (source, object_id, first_batch)
);

-- THE table. One row per distinct thing a source has said about an object.
CREATE TABLE statement (
  statement_id INTEGER PRIMARY KEY,
  object_id INTEGER NOT NULL, property TEXT NOT NULL,
  source TEXT NOT NULL,             -- who told us
  origin_ref TEXT,                  -- who measured it: bibcode or DOI, or 'JPL solution 49'; NULL = source does not say
  value_raw TEXT NOT NULL,          -- exactly as received: '10.', '0.48444', '-8.7e-14', 'Sv'
  unit_raw TEXT,
  value_num REAL, value_text TEXT,  -- parsed, in the property's one canonical unit
  bound TEXT NOT NULL,              -- 'value','upper_limit','lower_limit'
  err_lo REAL, err_hi REAL,         -- signed, canonical unit
  err_kind TEXT NOT NULL,           -- 'sigma','range','none_given','zero_as_received'
  qualifier TEXT,                   -- JSON: quality grade, method, force law, class scheme, solution label, period type
  upstream_date TEXT,               -- the date upstream attaches to this value, if any
  published TEXT,                   -- publication date of origin_ref, to whatever precision is known
  first_batch INTEGER NOT NULL, closed_batch INTEGER,
  close_reason TEXT                 -- 'superseded','withdrawn','object_dropped'
);
-- Deliberately no UNIQUE(object_id, property, source): one paper can give two solutions (2009 BD).

-- What was looked at. This is what separates "absent" from "not checked".
CREATE TABLE coverage (
  batch_seq INTEGER NOT NULL, source TEXT NOT NULL,
  object_id INTEGER,                -- NULL = the whole list was read and passed its guards
  outcome TEXT NOT NULL,            -- 'returned','unknown_to_source','error'
  PRIMARY KEY (batch_seq, source, object_id)
);

-- List membership as intervals. The list's definition is part of its name.
CREATE TABLE membership (
  list TEXT NOT NULL,               -- 'nhats dv<=12 dur<=450 stay>=8 launch 2020-2045'
  object_id INTEGER NOT NULL, first_batch INTEGER NOT NULL, closed_batch INTEGER
);

-- Our computed values. Same inputs and same method give the same row, so reruns add nothing.
CREATE TABLE derived (
  object_id INTEGER NOT NULL, property TEXT NOT NULL, method_version TEXT NOT NULL,
  inputs_sha256 TEXT NOT NULL,      -- over the statement ids and method artefacts used
  state TEXT NOT NULL,              -- 'measured','limit','prior','not_checked'
  dist_json TEXT,                   -- interval bounds and outcome probabilities; see note on the median
  licence_class TEXT NOT NULL, computed_batch INTEGER NOT NULL,
  PRIMARY KEY (object_id, property, method_version, inputs_sha256)
);
CREATE TABLE derived_input (object_id, property, method_version, inputs_sha256, statement_id);

CREATE TABLE forecast (forecast_id INTEGER PRIMARY KEY, rule TEXT, method_version TEXT,
  registered_at TEXT, state_hash TEXT, deposit_doi TEXT, void_date TEXT);
CREATE TABLE forecast_outcome (forecast_id, object_id, resolving_statement_id, scored_as_of_batch,
  score REAL, recorded_at TEXT);
```

In git, loaded at start: a **registry** of properties (canonical unit, kind of value, whether it is a measurement, a fit, something upstream derived, or a clock-driven forecast) and of sources (which properties each can supply, licence class, freshness window, unit map); and **annotations**, our judgement on an upstream value, matched on object, property, source, reference *and the raw value*, so a flag does not stick to a value upstream has since corrected.

How the three states fall out, for one (object, property, source) as of batch B:

```
a statement is live at B                                       -> measured (a value or a limit, by `bound`)
else the latest coverage row for (source, object) at or before B is
     'returned', and within the source's freshness window      -> looked for and absent
     anything else, or there is none                           -> not checked, with the reason
```

A failed request writes a `fetch` row and nothing else. No coverage row, no closed statement. The cell stays as it was, with an older "last checked" date. That is the whole mechanism behind "an outage never shows as nothing measured".

"What changed" is the statements with `first_batch = N` or `closed_batch = N`, grouped per object, with clock-driven properties left out and a new orbit solution reported as one event.

Notes on choices that look odd:

- `source_row` and `statement` both exist. Orbital elements change together and are not ledger properties; keeping them only as whole rows means a common-epoch change adds 30,000 row versions and no statements, so the change log stays quiet.
- Upstream-derived figures are stored and labelled as such. The reachable list's size range for Bennu is 158–706 m [T]; it is JPL's conversion of H, not a measurement.
- `dist_json` must not hold a central value if the "no median, data files included" rule stands.

### 4.4 What must be right in the schema on day one

**Identity.**

- Our own integer key, for every near-Earth asteroid in JPL's table, not only the reachable ones. It costs 43,000 rows and means an object has a key before it joins the list (F10) and the validation sets outside the list need no second scheme.
- Resolve each incoming row by any alias: the provisional designation in parentheses (F13), the number, JPL's id. One match: update aliases. Two matches: a merge; keep both keys, point one at the other. An object absent from a complete pull with no row claiming its names: mark `missing_upstream`, ask the Minor Planet Center's identifier service (F17), and only after several complete pulls mark it deleted. Never delete the row; frozen forecasts and old addresses refer to it. Deletions are more likely here than elsewhere [I]: the plan itself notes that some of the cheapest, most Earth-like objects may be spent rocket stages.
- Seeds, sealed lists and forecasts name the key and the designation on that date.
- Page addresses are an app decision. The designation table supports either an opaque id or a name with redirects.

**Units.** One canonical unit per property in the registry; the adapter converts and keeps the raw string and unit. Seen today: diameters in km from JPL and SsODNet and in metres from the reachable list; density in g/cm³ and kg/m³ (F16); drift on scales that differ by 10¹⁵ [I]; periods quoted in hours, minutes and seconds across the plan's own text. Time is UTC throughout; JPL's solution date is "Pacific Local" [D]. Dates can be partial (F12).

**Uncertainty.** Not one sigma column. Signed lower and upper bounds, a kind, and a bound type, with "none given" and "zero as received" as distinct values (F12). Quality grades and the force law go in `qualifier`. Limits are first-class because "a limit" is one of the four display states.

**Conflicts.** All statements coexist. Which one a page leads with is a rule in the method, so it is versioned and can change without touching data. Independence is counted by `origin_ref`, not by source. JPL's bulk table gives no reference for any physical value [D]; the per-object record does [D], and there are only about 70 measured diameters on the reachable list [P], so reading them once is cheap.

**Upstream errors.** Never edit an upstream value. Annotate it. When upstream fixes it, the old statement closes, the annotation stops matching, and a report lists it as resolved.

### 4.5 Scale and extension

Storage is not the limit at any size discussed. The limits are upstream manners: about one request a second for SsODNet [P], so 2 hours for the reachable list and 12 for all near-Earth objects; five a second at the Minor Planet Center [P]. Widening changes the crawl budget, not the schema.

The test of the schema is the third adapter. A new source should need one adapter file and registry rows, and no new table. A new property is a registry row. A new mission type is a method artefact.

### 4.6 What the app's stack decides, and what it does not

The science store is written by one process and read by the app. Visitor state, if there is any (predictions, saved selections, accounts), is a separate store with a different owner and different backup needs. Keeping them apart is the one architectural rule I would fix now; it holds for any stack.

What the stack choice depends on, from the data side:

- **Whether history views are computed on request or ahead of time.** "As of last March", "what changed", and the record page can be queries at request time, which needs a query engine on the server, or tables the pipeline writes into the export, which any server can read.
- **Where the daily job runs.** The plan says this workstation. Then the workstation's uptime is the site's freshness, and the export has to travel to the host. If the job runs on the host, the host needs Python.
- **The licence rule** that the browser never receives the whole data set. The app serves per-object slices, and the field of all asteroids needs one compact payload of redistributable columns only.
- **Whether visitors write anything.** That, not the science data, is what would require a server database.

## 5. Upstream drift

JPL's terms say formats "can change without notice" and to "always check the version field" [P]. The version fields have not changed since 2019 and 2021 [D], and the solution-number format is changing under them today (F5). So the version check is necessary and catches little. The guards have to look at the content.

### 5.1 Guards, run before a batch is accepted

A batch that fails any hard guard is not ingested. Its raw response is still archived, the `fetch` row says `guard_failed` with the report, the site keeps serving the last accepted batch for that source, and the maintainer is told. Releasing a held batch is an explicit, recorded act.

| Guard | Hard or warn | Catches |
|---|---|---|
| HTTP 200, body parses, expected top-level keys present, no `error`, `message` or `code` key | hard | JPL signals "not found" inside an HTTP 200 [D]; an HTML error page; a truncated body |
| `signature.version` equals the pinned value | hard | An announced format change |
| Declared count equals rows received, after casting (F3) | hard | A partial response |
| Field list equals the request, in order (full table); every required key present and no unknown key (reachable list) | hard for missing, warn for new | A renamed or dropped field; a new one |
| Per-field format: designation pattern, numeric strings, dates including the partial form, enumerations (`obs_flag` is blank, `S` or null; condition code 0–9; kind is one of four) | hard above a small count | A type or encoding change |
| Row count against the last accepted batch, scaled by the gap: the reachable list may gain a few dozen objects a day at most, and every removed object must be explained (delta-v crossed 12, renamed, merged) | hard | Dropped objects. Measured base rate: 2 added and none removed in 3.4 days [T]; monthly additions swing from 21 to 99 [P] |
| Filled count per physical field must not fall by more than a few. Today: 1,266 diameters, 1,209 albedos, 2,189 periods [T] | hard | A column silently emptied, which would otherwise read as "nothing measured" |
| Range and median per field (H 9 to 35, delta-v 3 to 12, period median) | hard | A unit change, such as hours to minutes |
| Share of rows changed. Normal: 0.8% of the full table and 3% of the reachable list per 3.4 days [T] | warn above 10%; warn at zero for several days | A mass change; or a stale cache being served, which looks like a quiet week |
| A row changed while its solution number did not (never seen, F4) | warn, with the fields listed | A precision, format or meaning change; the common-epoch change [I] |
| Solution numbers compared as numbers after stripping the prefix; unknown forms counted (144 today) | warn on a new form | F5 |
| Cross-source: every reachable-list object resolves in the full table (7,231 of 7,231); H agrees to rounding (1 exception); solution lag at most one (17 lag by exactly one); condition codes agree (3 exceptions) [T] | warn on growth | The two JPL tables drifting apart; an identity break |
| Canaries: Bennu's diameter, Eros's period, the six reachable objects with no H, 2022 OB5 still having no period in JPL, 2010 NU71 still carrying 1.126 km | warn | A known value moving; an annotated error being fixed |
| Per-object source returns "unknown" | never a failure of the batch | Becomes `unknown_to_source`, which is "not checked" |
| Monthly: fetch the documentation pages and SsODNet's metadata file, hash the text | warn on change | A change of meaning with no change of shape. A person reads the page |

Two habits remove whole classes of drift. Send every request parameter explicitly, including the ones that are defaults today, and store the request: the reachable list's default launch range moved in 2019 [D], and its current range of 2020–2045 includes seven years that have passed [I], which is worth a science reviewer's look. And compare values after parsing to the canonical unit, never as strings.

### 5.2 Outages

A source that is down produces `fetch` rows with an error and nothing else. The display for that source shows the date of its last successful check. Staleness has three dates, kept apart: upstream's own build date, our last successful check, and the last time anything changed. A banner keyed to only one of them is wrong for SsODNet in one direction or the other (F16).

### 5.3 Tests

- **Golden pulls.** The two existing pulls become fixtures. Ingesting them in order must give the numbers in section 1: 7,229 then 7,231; two joined, none left; 342 and 222 changed rows; one object crossing 7 km/s. The appendix script is the oracle.
- **Mutations.** Take a real pull and damage it one way at a time: drop rows but keep the count; drop a field; empty a column; multiply periods by 60; return `{"message": …}` with status 200; change the version string; shuffle key order; duplicate a row; shift every epoch; turn strings into numbers; give 2010 PS66 a number; merge two objects; remove one object. Each must give the stated result (hold, accept with no change, rename event, merge event). The assertion that matters, on every case: no cell becomes "looked for and absent".
- **Replay.** Delete the database, rebuild from raw responses and the journal, compare table hashes with the incremental build.
- **Determinism.** Derive twice from the same data state and method; the export hashes match.
- **Restore.** Run the replay test from the backup, not from the working disk.

## 6. What not to build yet

- Any per-object crawler schedule. Ingest the 1,704 SsODNet cards already on disk as one dated batch; build the live crawl when the schema has held for a month.
- The orbit fitter and anything in WP5.
- A workflow engine, a queue, a plug-in framework for adapters. One command on a timer. Write two adapters by hand; extract the interface from the third.
- A server database, an API layer, or a public bulk download.
- Automated deposits or a DOI per data state. One deposit per method release.
- A "best value" algorithm. Show every value; lead with one by a rule a person can read.
- "Open now" logic for windows, until F7 is understood from more than two pulls.
- A live price feed. Fix the price scenario per method release.
- A retention policy for raw responses. Keep everything; revisit at 10 GB.
- Columnar exports, a second machine, sub-daily pulls, alert streams.
- Visitor predictions and accounts, which are the owner's open question. Keep their storage separate when they come.
- Display of the 36,000 near-Earth asteroids outside the reachable list. Archive and key them; show none.

## 7. Three decisions that are cheapest now

1. **Our own object key, with every upstream name as a dated alias.** Today it is one table. After launch it is every address, every seed, every forecast list and every sealed-label hash.
2. **Statements and coverage as separate records, with the value kept as received.** The shape in section 4.3: source and original reference, raw string and parsed value, signed bounds with a kind, a limit flag, a qualifier, upstream's date and ours, and no rule that a cell has one value. Retrofitting any of these means re-reading every raw response, and retrofitting coverage is impossible for the past, because the record of having looked was never written.
3. **Data state and method version as separate stamps on every derived value, with derivations that are pure functions.** This is what lets the site move daily while method 0.1 stays frozen. Adding it later means no number published before that day can be reproduced.

A fourth is not a design decision but has the same character: **the role contact address JPL requires**. No unattended pull may run without it [P], and each day without a pull is history that upstream does not keep.

## 8. First step

Build the ingest spine against the two pulls already on disk, with no network, no model and no app:

1. The `fetch`, `batch`, `object`, `designation`, `source_row`, `coverage` and `membership` tables, the raw store and the journal.
2. The two JPL adapters, replaying the 21 and 24 November pulls as batches 1 and 2. The first pull's retrieval time is taken from its file timestamp and recorded as inferred.
3. The guards in section 5.1 and the golden and mutation tests in 5.3. Acceptance is that the replay reproduces section 1 and that no mutation produces a false "absent".
4. Then `statement` for the dozen properties the ledger shows, and the plan's ten fixtures as its R0, now with the time-based fixtures added.

In parallel, three things only the owner can settle: the contact address, where the daily job will run and where its failure notices go, and where the raw store is backed up. The day the address exists, the timer starts: two requests a day, with `spkid`, `soln_date` and `full-prec` added to the request before history accumulates in the old form (F1).

This reorders the plan slightly. AGENTS.md already says pipeline first and stack later; the change is that the first thing the pipeline does is keep time, and the fixtures and priors come after it.

## 9. Open questions for the owner

1. What role address goes in the User-Agent for JPL? Nothing unattended can run until it exists.
2. Which machine runs the daily job, and where should a held batch or a failed pull notify you?
3. Where is the raw store backed up?
4. Is the price list part of the method (fixed per method release, my recommendation) or a live feed?
5. Does "no median anywhere, the data files included" hold for the internal export too? It decides how a distribution is encoded.
6. May the object table cover all 43,379 near-Earth asteroids from the start, with only the reachable ones shown?
7. For scoring forecasts, which date governs when a measurement's observation date is unknown: publication, or the day we first saw it?
8. For the app: are history views (as of a date, what changed) computed on request or written ahead by the pipeline? This is one of the things the stack choice turns on.

## 10. Not verified

- That JPL's object id changes at numbering is inferred from the alias list in JPL's own example [D]; I made no JPL API call to watch it happen.
- The common-epoch change is inferred from 30,476 rows sharing one epoch (2461200.5, 9 June 2026) [T] and from recalling that such epochs step every 200 days. The next step on that grid would be 26 December 2026.
- The reason for the 21-to-27 November window roll is my reading of JPL's full-moon rule [D] against a full-moon date computed from the mean lunar cycle. Two pulls cannot show the full pattern.
- `full-prec` and the extra fields are documented [D] but untested; the size of a full-precision response is unknown.
- That the reachable list's minimum delta-v can refer to a launch date already past is inferred from the documented default range.
- The deletion of a designation that turned out to be artificial (2018 CN41, January 2025) is recalled; a search today returned only a secondary report and the Minor Planet Center page refused the fetch.
- SsODNet units are inferred from magnitudes; I did not read its metadata file.
- Physical fields did not change in the window, so nothing here shows how a physical update arrives.
- Documentation pages were read through a summarising fetch; quoted words are as the fetch returned them.

## Sources

Read today (2026-11-24):

- JPL SBDB Query API, fields, `full-prec`, error codes: https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html
- JPL SBDB API, per-object record, references per physical value, HTTP 200 on no match: https://ssd-api.jpl.nasa.gov/doc/sbdb.html
- JPL SBDB filter fields: https://ssd-api.jpl.nasa.gov/doc/sbdb_filter.html
- JPL NHATS API, version history, default constraints: https://ssd-api.jpl.nasa.gov/doc/nhats.html
- JPL Horizons Lookup API, primary and alternate ids: https://ssd-api.jpl.nasa.gov/doc/horizons_lookup.html
- NHATS introduction, "daily analysis": https://cneos.jpl.nasa.gov/nhats/intro.html
- NHATS observability rules, full-moon exclusion: https://cneos.jpl.nasa.gov/nhats/obs.html
- Minor Planet Center API index: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/
- Minor Planet Center Designation Identifier: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/query-identifier/ and one test request to https://data.minorplanetcenter.net/api/query-identifier
- Minor Planet Center identifications table: https://docs.minorplanetcenter.net/mpc-ops-docs/data-and-services/schema/current-identifications/
- Minor Planet Center on principal designations and numbering: https://docs.minorplanetcenter.net/mpc-ops-docs/astrometry/discoveries-and-credit/
- SsODNet card, one test request: https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu

Not read today, taken from the project's files:

- JPL fair-use terms, https://ssd-api.jpl.nasa.gov/doc/ : `docs/research/verify-facts-venues.md` section 9 (read 2026-11-21).
- Minor Planet Center and SsODNet rate limits, Zenodo rules: same file, sections 6 and 8.
- SsODNet lag, coverage counts, the 2010 NU71 error: `docs/research/catalogs.md`, `verify-coverage.md`.
- "The table lists only the next window": `docs/research/verify-obs-window.md` section 1.

## Appendix: the script behind the [T] numbers

Standard library only. Run as `python3 -I review_data_check.py data/snapshots`. It is reproduced here in full; a copy is `scripts/review_data_check.py` in `data/backbone-review-2026-11-24.tar.zst`.

```python
import collections, gzip, json, sys
B = sys.argv[1].rstrip("/") + "/"
A, Z = "2026-11-21", "2026-11-24"
def load(d): return json.load(open(B+d+"/nhats.json")), json.load(open(B+d+"/sbdb_neo.json"))
(n1, s1), (n2, s2) = load(A), load(Z)
F = s1["fields"]; ix = {f: i for i, f in enumerate(F)}
S1 = {r[ix["pdes"]]: r for r in s1["data"]}; S2 = {r[ix["pdes"]]: r for r in s2["data"]}
N1 = {r["des"]: r for r in n1["data"]}; N2 = {r["des"]: r for r in n2["data"]}
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
def flat(r):
    o = {}
    for k, v in r.items():
        if isinstance(v, dict): o.update({k+"."+kk: vv for kk, vv in v.items()})
        else: o[k] = v
    return o
onum = lambda o: int(o.replace("JPL ", "")) if o.replace("JPL ", "").isdigit() else None
g = lambda r, f: r[ix[f]]
print("1 fields requested: spkid" , "spkid" in F, "| soln_date", "soln_date" in F, "| n fields", len(F))
print("2 nhats key orders within one file:", len({tuple(r) for r in n1["data"]}), len({tuple(r) for r in n2["data"]}))
print("3 count types:", type(n2["count"]).__name__, type(s2["count"]).__name__, "| rows", len(N1), len(N2), len(S1), len(S2))
print("4 nhats added/removed:", sorted(set(N2)-set(N1)), sorted(set(N1)-set(N2)), "| sbdb added/removed:", len(set(S2)-set(S1)), len(set(S1)-set(S2)))
chg = [k for k in S1 if k in S2 and S1[k] != S2[k]]
print("5 sbdb rows changed:", len(chg), "| with orbit_id change:", sum(g(S1[k], "orbit_id") != g(S2[k], "orbit_id") for k in chg),
      "| cells:", sum(sum(a != b for a, b in zip(S1[k], S2[k])) for k in chg))
print("6 physical cells changed:", sum(g(S1[k], f) != g(S2[k], f) for k in chg for f in ("diameter","albedo","rot_per","spec_B","spec_T","GM","density","BV","UB")),
      "| H changed:", sum(g(S1[k], "H") != g(S2[k], "H") for k in chg))
print("7 orbit_id forms:", collections.Counter("JPL n" if o.startswith("JPL ") else "n" if o.isdigit() else "other" for o in (g(r, "orbit_id") for r in s2["data"])),
      "| bare->'JPL' flips:", sum((not g(S1[k], "orbit_id").startswith("JPL")) and g(S2[k], "orbit_id").startswith("JPL") for k in chg))
nch = {k: {f for f in flat(N1[k]) if flat(N1[k])[f] != flat(N2[k]).get(f)} for k in N1 if k in N2}
nch = {k: v for k, v in nch.items() if v}
W = {"obs_start","obs_end","obs_mag","obs_flag","radar_snr_a","radar_obs_a","radar_snr_g","radar_obs_g"}
print("8 nhats rows changed:", len(nch), "| only window/radar-opportunity fields:", sum(v <= W for v in nch.values()),
      "| cells:", sum(len(v) for v in nch.values()), "of which window/radar:", sum(len(v & W) for v in nch.values()))
print("9 earliest obs_start per pull:", min(r["obs_start"] for r in N1.values() if r["obs_start"]), min(r["obs_start"] for r in N2.values() if r["obs_start"]),
      "| rolled 11-21 -> 11-27:", sum(N1[k]["obs_start"] == "2026-11-21" and N2[k]["obs_start"] == "2026-11-27" for k in N1 if k in N2),
      "| open on 11-21, no window on 11-24:", sum(N1[k]["obs_start"] == "2026-11-21" and N2[k]["obs_start"] is None for k in N1 if k in N2))
lag = [k for k in N2 if onum(N2[k]["orbit_id"]) is not None and onum(g(S2[k], "orbit_id")) is not None and onum(N2[k]["orbit_id"]) != onum(g(S2[k], "orbit_id"))]
print("10 nhats computed on an older orbit than sbdb shows:", len(lag), "| raw string mismatch:", sum(N2[k]["orbit_id"] != g(S2[k], "orbit_id") for k in N2))
dv = lambda r: float(r["min_dv"]["dv"])
print("11 under 5/6/7 km/s:", [sum(dv(r) < t for r in N.values()) for N in (N1, N2) for t in (5, 6, 7)],
      "| within 0.02 km/s of 5/6/7:", [sum(abs(dv(r)-t) <= 0.02 for r in N2.values()) for t in (5, 6, 7)], "| dv >= 11.9:", sum(dv(r) >= 11.9 for r in N2.values()))
print("12 sbdb kinds:", dict(collections.Counter(g(r, "kind") for r in s2["data"])), "| numbered rows with provisional in parentheses:",
      sum("(" in g(r, "full_name") for r in s2["data"] if g(r, "kind") == "an"), "of", sum(g(r, "kind") == "an" for r in s2["data"]))
print("13 odd values:", {k: g(S2[k], f) for k, f in (("101955","diameter_sigma"),("2011 AA37","rot_per"),("2013 NJ","rot_per"),("469219","name"))},
      "| diameters with no sigma:", sum(bool(g(r, "diameter")) and not g(r, "diameter_sigma") for r in s2["data"]),
      "| partial dates:", sum("?" in (g(r, "first_obs") or "") for r in s2["data"]), "| nhats h null:", sum(r["h"] is None for r in N2.values()))
fx = ["2011 AA37","2009 BD","2022 OB5","2026 QQ8","2020 CD3","2010 CW266","469219","101955","2010 NU71","2013 NJ"]
print("14 fixtures changed in sbdb:", [k for k in fx if S1[k] != S2[k]], "| in nhats:", [k for k in fx if canon(N1[k]) != canon(N2[k])])
raw = {d+"/"+f: open(B+d+"/"+f, "rb").read() for d in (A, Z) for f in ("nhats.json", "sbdb_neo.json")}
print("15 bytes raw/gzip per pull:", {k: (len(v), len(gzip.compress(v, 9))) for k, v in raw.items() if k.startswith(Z)})
delta = b"\n".join([canon(S2[k]) for k in S2 if S1.get(k) != S2[k]] + [canon(N2[k]) for k in N2 if k not in N1 or canon(N1[k]) != canon(N2[k])])
print("16 changed rows only, both lists:", len(delta), "bytes,", len(gzip.compress(delta, 9)), "gzip | non-null cells nhats/sbdb:",
      sum(v is not None for r in n2["data"] for v in flat(r).values()), sum(v is not None for r in s2["data"] for v in r))
```

Output on 2026-11-24:

```
1 fields requested: spkid False | soln_date False | n fields 53
2 nhats key orders within one file: 2052 2059
3 count types: str int | rows 7229 7231 43367 43379
4 nhats added/removed: ['2026 VQ5', '2026 WV1'] [] | sbdb added/removed: 12 0
5 sbdb rows changed: 342 | with orbit_id change: 342 | cells: 1824
6 physical cells changed: 0 | H changed: 37
7 orbit_id forms: Counter({'n': 26104, 'JPL n': 17131, 'other': 144}) | bare->'JPL' flips: 20
8 nhats rows changed: 222 | only window/radar-opportunity fields: 199 | cells: 487 of which window/radar: 415
9 earliest obs_start per pull: 2026-11-21 2026-11-27 | rolled 11-21 -> 11-27: 187 | open on 11-21, no window on 11-24: 12
10 nhats computed on an older orbit than sbdb shows: 17 | raw string mismatch: 1641
11 under 5/6/7 km/s: [286, 726, 1388, 286, 726, 1389] | within 0.02 km/s of 5/6/7: [23, 28, 27] | dv >= 11.9: 143
12 sbdb kinds: {'an': 3874, 'au': 39296, 'cn': 162, 'cu': 47} | numbered rows with provisional in parentheses: 3874 of 3874
13 odd values: {'101955': '0.00', '2011 AA37': '10.', '2013 NJ': '250.', '469219': 'Kamo`oalewa'} | diameters with no sigma: 103 | partial dates: 3 | nhats h null: 6
14 fixtures changed in sbdb: ['2011 AA37', '2026 QQ8'] | in nhats: ['2011 AA37', '2026 QQ8', '469219']
15 bytes raw/gzip per pull: {'2026-11-24/nhats.json': (2588379, 370155), '2026-11-24/sbdb_neo.json': (15793225, 2904369)}
16 changed rows only, both lists: 214484 bytes, 39728 gzip | non-null cells nhats/sbdb: 108400 1292377
```

Figures in sections 1 and 2 not printed above (H change sizes, the 2026 VK2 crossing, the 2026 VQ5 entry, the peak-brightness direction for rolled rows, the objects near H 24, the Bennu size range, the 7,007 canonically identical rows, the 154 drift values at 3 sigma and the 14 near that line, which asteroids' drift figures changed, the 30,476 rows sharing one epoch) came from exploratory scripts in the same session and are simple extensions of this one. The 24 November full moon is from the mean lunar cycle counted from the new moon of 6 January 2000, which gives 24 November 2026 at about 16:20 UTC.
