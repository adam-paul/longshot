# Design: the fact log

Written 2026-11-24. Status: complete. Limits are in section 13.

One of several designs for the data backbone. Its stance: history and provenance first. An append-only log of what each source said, and when, is the core. Everything shown is a view over it: the ledger, "what changed", the inputs of a frozen forecast. Nothing here chooses the app's server, language, framework or host; section 7 says what the app reads and what that choice turns on.

Evidence tags:

- **[test]** my own test today on the two local JPL pulls (`data/snapshots/2026-11-21`, `/2026-11-24`). The scripts are in the appendix.
- **[doc]** a page I read today. Section 14 gives the URL.
- **[colleague]** from one of today's five reports in this folder, not re-checked by me. Section 14 names the report and the URL it cites.
- **[estimate]** my judgement, no measurement behind it.

No request went to a JPL API endpoint. The only outside requests I made were two reads of JPL documentation pages.

Words used below:

- **Capture**: the exact bytes of one response, plus a small file giving the request, the time, the status and the headers.
- **Journal**: the append-only log. One line per event.
- **Segment**: one journal file, written by one run and never changed afterwards.
- **Record**: one source's entry under one of its own keys (JPL's row for 2011 AA37), kept in the source's shape with the source's field names.
- **Splitter**: the few lines per source that cut a response into keyed records.
- **Reader**: the per-source mapping from a record to property values.
- **View**: any table computed from the journal. The **index** is the database that holds the views. It can be deleted and rebuilt.
- **Edition**: the data set the app reads, built from the views at a stated journal position and method version.

## 0. Short answers to the owner's questions

- **What dynamic access exists.** None the site could call while a visitor waits, and none that pushes. JPL forbids embedding its interface in a website and allows one request at a time [doc]. Neither bulk list has a "changed since" filter [doc for the near-Earth table; colleague: upstream-orbits for both], and neither response carries cache headers [test]. Every source refreshes about once a day [colleague: upstream-orbits]. A scheduled daily job is the right shape and the only one.
- **What it costs to stay current.** Two JPL requests a day cover everything fast-moving for all 43,379 near-Earth objects. With follow-ups and checks on the slow sources it is about 22 requests and 21 MB a day, and about 1 GB a year kept (section 4.2).
- **What makes it more than a snapshot.** Time becomes part of the data. Keep every response, and keep a journal of what each source said and when. The site is then a view over that journal: every value can say as of when, every page can say what changed, and a forecast can name the exact state of knowledge it was made from. Upstream keeps none of this. JPL overwrites yesterday's orbit and yesterday's observing window.
- **First step.** Build the journal offline on the two pulls already on disk and prove it reproduces today's measured diff. Switch it on the day a contact address for JPL exists. I built a 244-line version today to check that this is small and that the numbers come out (section 2).

## 1. The design in one page

```
upstream --collect--> captures/   bytes, written once          cannot be rebuilt
              \-----> journal/    events, append-only          cannot be rebuilt
                         |  index   (seconds)
                         v
                      index.db    record_span, alias, claim, coverage, field_change,
                         |        window, membership, derived ...   deleted and rebuilt at will
                         |  export  at (segment, method, schema)
                         v
                      editions/<id>/  --> the app (stack open)

git: code, the source and property registries, method tags, annotations, a lock file
```

Five rules carry the design:

1. **A response is stored before it is understood.** Bytes and request details are on disk before any parsing runs.
2. **The journal only grows.** No line is edited or deleted. A correction is a new line.
3. **Records keep the source's shape.** What a field means (property, unit, state, whether a change is news) is decided by views, which can be changed later and re-run over all of history. Only the journal's event shapes have to be right on the first day.
4. **Every act of asking is journaled, including the ones that failed.** That record is what separates "looked for and absent" from "not checked".
5. **Anything frozen cites a journal position and its hash, and also carries its own copy of the inputs it used.**

Where this agrees with the reviews: own object key, a record of having looked, separate stamps for data and method, raw responses kept, guards before acceptance, daily pulls [colleague: review-data, review-extend, review-ops]. Where it differs from the storage proposed in review-data:

| | review-data | this design |
|---|---|---|
| What is primary | a database of statements, rebuildable from raw responses | the journal, as plain files. The database is an index |
| Unit stored | one row per property value, with a closing batch number written into it later | one line per changed upstream record, whole. Nothing is written into an old line |
| Property schema (units, bounds, kinds, qualifiers) | must be right on day one | a view. Wrong choices are fixed by re-running the reader over stored records |
| "Looked" record | a separate coverage table | the fetch events themselves, plus one line per key asked |
| Per-object follow-up backlog | not specified | a query over the journal, so there is no queue to lose in a reboot |
| The project's own forecasts and published editions | separate tables | records in the same journal, from a source named `longshot` |

## 2. What I tested today

I wrote a toy version of the journal in 244 lines of standard-library Python (three scripts, appendix) and ran the two pulls through it as segments 1 and 2. All [test].

| Test | Result |
|---|---|
| Segment 1, the 21 November pull | 50,596 record lines (7,229 reachable-list rows, 43,367 near-Earth rows). 44.5 MB as text, 4.2 MB with xz |
| Segment 2, the 24 November pull, 3.36 days later | 578 record lines: 222 changed and 2 new on the reachable list, 342 changed and 12 new in the near-Earth table, none gone. 476 kB as text, 63 kB with xz |
| Rate | 172 record lines a day, 142 kB a day as text, 19 kB a day with xz |
| Built twice from nothing | The running hash over both segments is identical |
| Run time | Both pulls into two segments: 8 seconds, most of it xz run only to measure sizes |
| Index built from the journal | 4.1 seconds. 99 MB in SQLite, unoptimised (each record body is stored twice) |
| "The reachable list as it stood after segment 1", then after segment 2 | 7,229 objects, 286 / 726 / 1,388 under 5 / 6 / 7 km/s, then 7,231 and 286 / 726 / 1,389. 0.02 to 0.04 seconds a query. These are the plan's numbers and the measured diff |
| Changes on the reachable list, by field class | Of 222 changed rows, 192 changed only in the observing-window fields and 199 only in window or radar-outlook fields. The other 23 all carry a new orbit solution. Every change in delta-v, trajectory count, H or size range is inside those 23 |
| Radar-outlook fields | They move with the calendar like the window fields (`radar_obs_a` went from 2026-11-21 to 2026-11-24 or to nothing). I class them with the window fields |
| Changes in the near-Earth table | All 342 changed rows have a new orbit solution id. Tracking fields changed in all 342, H in 37, orbital elements in 47 (at the reduced precision the pulls asked for), the fitted sunlight-push fields in 5 rows (4 asteroids and comet 2P, 9 values), physical fields in none |
| Observing windows | 188 windows kept their end date and had their start rewritten (184 from 21 to 27 November). 12 listed windows have no entry three days later. 16 have a different end date |
| The two JPL lists against each other | 17 reachable rows are one orbit solution behind the near-Earth table at segment 2 |
| One fixture through time | 2011 AA37: near-Earth table solution `JPL 48` then `JPL 49`, 190 then 193 observations; reachable list still on solution 48 at both dates; window start rewritten 21 to 27 November; delta-v 5.851 km/s unchanged |
| Nine single faults in the second near-Earth or reachable response | Timeout; HTTP 200 with an error body; an HTML page; a body cut off mid-stream; 500 rows dropped with the count unchanged; 500 dropped with the count adjusted; the rotation-period column emptied; the version string changed: each produced zero record lines and left the other source's lines identical to the clean run. Key order shuffled in every row: the same 224 lines as the clean run |
| Capture size | 18.38 MB a pull as received; 3.48 MB with gzip; 2.57 MB with xz, which takes 3.7 seconds |
| The interpreter | The uv-managed Python 3.12.13 on this machine has `sqlite3` (SQLite 3.50.4) and `lzma`. The backbone needs no package |

The toy has no identity layer, no readers and five guards. It shows that the journal, the as-of query, the change classes and the fault behaviour are small and work on the real files. It does not show anything about a live pull.

## 3. Storage

### 3.1 Files

```
data/                                       outside git
  captures/<source>/<yyyy>/<utc stamp>-<sha12>.body.xz    exact bytes, written once, read-only
  captures/<source>/<yyyy>/<utc stamp>-<sha12>.meta.json  request, times, status, headers, sha256, length
  journal/<nnnnnn>.ndjson                   one segment per ingest run, written once
  journal/chain.ndjson                      one line per segment: number, sha256, running hash, last line number
  index/longshot.db                         every view in 3.3; delete and rebuild at will
  editions/<id>/                            what the app reads (section 7)
  freezes/<id>/                             the inputs of one frozen forecast set, written once
```

- `captures/` and `journal/` are the only things that cannot be rebuilt. They are write-once files, so an off-machine copy is "send new files", and a store that forbids delete and overwrite fits them exactly.
- A failed request writes a `meta.json` with no body.
- Small per-object responses (a literature card) go into one bundle file per run, exact bytes, not one file each.
- Compression is xz through the standard library. zstd would be faster and needs a package or Python 3.14.
- The 21 November pull has no saved headers; its capture time comes from the file's timestamp and is marked inferred. The folder named `2026-11-24` holds a pull made on 2026-11-25 UTC. Capture names use UTC.

### 3.2 The journal: six kinds of line on day one

Each line is one JSON object with sorted keys. `seq` numbers lines across all segments. `fid` numbers fetches.

| `t` | Written when | Fields that matter |
|---|---|---|
| `fetch` | Every request attempt, failed ones included | `fid`, `source`, `shape` (hash of the full request, every parameter written out), `url`, `params`, `scope` (`list`, or the keys asked for), `started_at`, `ended_at` (UTC), `transport` (`ok`, `timeout`, `refused`, `http_error`), `http_status`, `headers`, `body_sha256`, `body_bytes`, `capture` (path), `host`, `inferred` |
| `verdict` | Every fetch that returned a body; again if a held one is released | `fid`, `outcome` (`accepted`, `held`, `released`, `rejected`), `guards` (name, pass or fail, detail), `api_version` as received, `upstream_edition` (the source's own date for its content: a card's build stamp, a file's Last-Modified; empty for JPL's lists, which carry none), `n_records`, `splitter_rev`, `by` and `note` on a release |
| `asked` | Fetches for named keys: one line per key | `fid`, `source`, `key`, `outcome` (`answered`, `unknown_to_source`, `failed`), decided from the body, not the status code |
| `record` | Accepted fetches: one line per upstream record that is new, changed or gone | `fid`, `source`, `key`, `kind` (`new`, `changed`, `gone`, `rebase`), `hash` (of the record with keys sorted), `prev`, `body` (the record as received: the source's field names, strings left as strings, `"10."` and `"0.00"` intact) |
| `mint` | A new record that no known name resolves | `oid` (the project's own object key), `fid`, `source`, `key` |
| `alias` | A name is first seen for an object, or stops being used for it | `oid`, `scheme` (`provisional`, `number`, `name`, `jpl.spkid`, `mpc.packed`, `ssodnet.id`), `value` as received, `norm`, `source`, `fid`, `op` (`add`, `close`) |

Notes:

- A `record` line holds the whole upstream record, not a difference. At 403 bytes a reachable-list row and 909 a near-Earth row (medians) [test], whole records cost 142 kB a day, and a reader never has to reassemble anything.
- The splitter's key is the source's own (`des`, `pdes`). It is not identity. When an asteroid is numbered, JPL's key changes; the journal shows one `gone` and one `new`, and the identity step links them through the old designation in the new row's full name (all 3,874 numbered rows carry it [test]) and writes an `alias` line. The decision is journaled, so later code cannot re-decide the past.
- `rebase` marks the first accepted fetch after the request itself changed (section 4.3). Every row gets a new line; the change views do not report it as news.
- Fields that are only an envelope and change on every build (a card's build stamp) are named in the registry, left out of the record hash and kept in `verdict.upstream_edition`. Clock-driven fields (window dates) stay in: their history is wanted.
- Later kinds of line reuse `record`. A reviewed value read from a paper is a record from a source of kind `reviewed`, with the quoted sentence and who accepted it. A static table from a paper is one capture and one record per row. A forecast issued by a frozen method is a record from source `longshot.forecast`; a resolution, from `longshot.resolution`; a published edition's manifest, from `longshot.edition`. Two more kinds will be needed: `merge` (two keys are one object) and `embargo` (section 6).

### 3.3 Views (tables in the index)

All are rebuilt from the journal and git. None is edited by hand.

| Table | Columns that matter | What it answers |
|---|---|---|
| `fetch`, `verdict`, `asked`, `record_event` | as journaled | the journal, queryable |
| `record_span` | `source`, `skey`, `hash`, `body`, `from_seg`, `to_seg` | "the source's record as of segment N" is `from_seg <= N and (to_seg is null or to_seg > N)` |
| `object` | `oid`, `minted_seg`, `lifecycle` (`designated`, `numbered`, `merged`, `withdrawn`, `missing_upstream`), `merged_into` | one row per near-Earth object, all 43,379, not only the reachable ones |
| `alias` | `oid`, `scheme`, `value`, `norm`, `source`, `from_seg`, `to_seg` | every name any source has used, with dates |
| `membership` | `population` (named with its rule and parameters), `oid`, `from_seg`, `to_seg` | who was on the reachable list when |
| `field_change` | `seg`, `source`, `oid`, `field`, `old_raw`, `new_raw`, `class` (`clock`, `solution`, `tracking`, `elements`, `brightness`, `reach`, `push`, `physical`, `identity`, `format`) | field-level difference between consecutive versions of a record. Classes come from the source registry |
| `change_event` | `seg`, `oid`, `kind` (`new_object`, `joined`, `left`, `new_solution`, `reach_changed`, `value_measured`, `value_changed`, `value_withdrawn`, `renamed`, `merged`), `detail` | "what changed", with `clock` and `format` left out and one new orbit solution reported once. The weekly digest and the front page read this |
| `window` | `oid`, `end_date`, `start_first_seen`, `first_seen_seg`, `mag_first`, `mag_last`, `last_listed_seg`, `state` (`listed`, `no_longer_listed`) | each observing window as a dated fact. The first start ever seen is kept; JPL's later rewrites of it are not news; a window that drops off JPL's list stays here. For a window already open at its first capture, the first start seen is only the latest it can have opened |
| `claim` | `claim_key`, `oid`, `property`, `source`, `source_edition`, `origin_ref` (who measured it), `value_raw`, `unit_raw`, `value_num`, `value_text`, `bound` (`value`, `upper_limit`, `lower_limit`), `err_lo`, `err_hi`, `err_kind`, `qualifier` (quality grade, force law, period type), `upstream_date`, `published`, `embargoed`, `from_seg`, `to_seg`, `reader_rev` | one row per thing a source says about a property. The columns are review-data's `statement`; here it is a view written by readers. No rule that a cell has one value |
| `coverage` | `source`, `oid`, `last_answer_seg`, `last_answer_at`, `last_outcome`, `source_edition`, `last_try_at`, `last_try_outcome` | when each source last answered about each object |
| `source_status` | `source`, `last_accepted_at`, `upstream_edition`, `held`, `failures_in_a_row`, `lagging_rows` | the freshness line on every page; the monitoring signals |
| `derived` | `oid`, `quantity`, `method`, `inputs_hash`, `value` (bounds and outcome probabilities; no central value), `state`, `licence_class`, `first_seg` | the frozen method applied to the data as of a segment (section 6) |
| `backlog` | `source`, `oid`, `reason` | per-object calls still owed, as a query: reachable objects whose single-object record is on an older solution than the near-Earth table shows; keys never asked; keys asked before the source's last rebuild |

### 3.4 In git

- `pipeline/collect.py`: the one module that opens a connection. Standard library only. It writes captures and nothing else.
- `pipeline/ingest.py`: splitters, guards, the identity step. The only writer of the journal.
- `pipeline/index.py`, `pipeline/readers/`, later `pipeline/derive/` and `pipeline/export.py`.
- `registry/sources.toml`: per source, its kind (`list`, `keyed`, `file`, `reviewed`, `own`), URL, every request parameter, key field, pinned interface version, change signal (content, header, body field), expected cadence, stale-after age, request limit, licence class, envelope fields, and the class of each field.
- `registry/properties.toml`: property id, canonical unit, value kind, which row of an entry it belongs to.
- `annotations.toml`: the project's judgement on an upstream value, matched on the raw value, never an edit of it [colleague: review-data].
- Method releases as tags (section 6), and a lock file of hashes over frozen files.
- Data stays out of git. Tests find the two pulls under `data/` by the hashes in a committed manifest.

## 4. Sync

### 4.1 Jobs and schedule

Times are UTC. Job names are subcommands of one program. Where they run is the owner's decision; section 12 lists what the place must provide.

| Job | When | What it does |
|---|---|---|
| `collect` | Daily 10:00 | Section 4.2, steps 1 to 6. 10:00 is after JPL's trajectory run should have caught up with yesterday's Minor Planet Center circular and before today's, issued about 12:30 [colleague: upstream-orbits]. The catch-up time is an assumption; the first week's `lagging_rows` will show it |
| `collect --only-missing` | Daily 16:00, from a second place | Captures only, and only for a source with no good capture today. It never writes the journal, so the journal has one writer |
| `ingest` | After each `collect` | Journals new captures, runs guards, writes verdicts, record, asked, mint and alias lines as one segment, appends to the chain |
| `index`, `derive`, `export` | After each `ingest` | Extend the views; apply the frozen method to objects whose inputs changed; publish an edition if the release guards pass. Before a method exists, `derive` does nothing |
| `weekly` | Monday 11:00 | The whole reachable list through the Minor Planet Center's identifier service (73 requests of 100 names) to catch withdrawn objects such as 2026 JG2; JPL's radar table (1 request); the digest from `change_event` [colleague: upstream-orbits, review-ops] |
| `recrawl <source>` | When a probe shows a new build of a per-object source | Works through `backlog` at the source's limit; stops and resumes anywhere, because the backlog is a query |
| `verify` | Daily for yesterday; in full each quarter | Re-splits stored captures and checks that the journal holds what the splitter yields. Checks every segment's hash against the chain |
| `drill` | Quarterly | From the off-machine copy only: restore, `verify`, rebuild the index, rebuild the current edition, compare hashes |
| By hand | | `release <fid>` for a held capture; `reread` (4.4); method release, freeze, resolve; accepting an entry from the literature queue |

### 4.2 The daily run, sized

| Step | Requests | Downloaded | Kept |
|---|---|---|---|
| 1. JPL reachable list | 1 | 2.6 MB [test] | 0.29 MB xz [test] |
| 2. JPL near-Earth table | 1 | 15.8 MB as pulled so far [test]. Size with full precision and three more fields is unknown | 2.28 MB xz [test] |
| 3. `ingest` the two lists | 0 | | 0.14 MB of journal [test] |
| 4. JPL single-object call for each reachable object that is new or has a new orbit solution | 7 to 8 on this sample (23 changed and 2 new in 3.36 days [test]). Scaled by ESA's change log: about 11 on its median day, 18 at its 90th percentile, 34 on its busiest [colleague: upstream-orbits; my arithmetic]. Capped at 60 a run; the rest stays in `backlog` | 2 to 7 kB each [colleague: upstream-orbits] | under 0.1 MB |
| 5. Minor Planet Center identifier, for names that appeared or vanished | 0 or 1 | small | small |
| 6. Probes of the slow sources: about nine HEAD requests (SsODNet's three static files, Pravec's table, the lightcurve database, MITHNEOS, the ALCDEF archive), one SsODNet card for its build stamp, the arXiv planetary-science listing on weekdays [colleague: upstream-physical] | about 11 | about 0.13 MB | about 0.03 MB [estimate] |
| 7. ESA's change log, as an internal cross-check only, if the owner agrees | 1 | 2.25 MB [colleague: upstream-orbits] | about 0.3 MB [estimate] |
| **A typical day** | **about 22, of which 9 to 10 to JPL, one at a time** | **about 21 MB** | **about 3 MB of captures and 0.14 MB of journal** |

A year is about 1.0 to 1.2 GB of captures and 52 MB of journal as text. Five years is about 5 to 6 GB and 300 MB. The index grows by roughly 120 MB a year and its rebuild by roughly 5 seconds a year [estimate from the toy's 99 MB and 4.1 seconds for 50,596 lines].

Two kinds of unusual day:

- **A full-moon gap or a busy discovery week.** A few hundred extra record lines. Nothing to do.
- **Everything refitted at once.** JPL recomputed its whole catalogue in April 2021 and ESA refitted 46,027 entries on 30 July 2026 [colleague: upstream-orbits]. In the journal that is one 45 MB segment and 7,231 owed follow-ups. The guard "more than 10% of rows changed" holds it for a person. Released, the follow-ups drain at the cap over about 120 days, or in one supervised four-hour run.

### 4.3 Change detection

- **JPL's lists:** parse, sort keys, hash each record, compare with the live hash for that key. Raw bytes cannot be compared: key order differs between pulls and within one file [test]. A new `orbit_id` in the near-Earth table is the trigger for step 4; all 342 changed rows had one [test].
- **Static files** (SsODNet's bulk table and reference list, Pravec's table, the lightcurve database): the Last-Modified and ETag headers from a HEAD request, journaled as a fetch with its `upstream_edition`. A change puts that source's keys into `backlog`.
- **Per-object services:** the build stamp inside one canary response.
- **A change of the request itself.** The first live pull should add `spkid`, `soln_date`, `source` and `full-prec` [doc] before history accumulates in the reduced form. Every row will then differ. The request's hash is the fetch's `shape`; the first accepted fetch under a new shape writes `rebase` lines, and the change views skip them.
- **What counts as news** is a view. `field_change.class` comes from the registry, so the 199 calendar-only rows are in the journal and out of the digest, and a wrong class is fixed by editing the registry and rebuilding the index.

### 4.4 Failure handling

| What happens | What is written | What the site shows |
|---|---|---|
| A request times out or is refused | A `fetch` line with the transport error. Nothing else. Up to three tries, 5, 15 and 45 minutes apart, then stop until the 16:00 trigger; JPL asks clients to back off [doc] | The last accepted data for that source, with its date. `coverage` is untouched, so no cell changes state |
| The body fails a guard (truncated, an error inside HTTP 200, a column emptied, rows dropped, version or field list changed) | The capture, a `fetch` line, a `verdict` of `held` with the guard report. No record lines. The owner is told. A hold never clears itself | As above |
| A held capture turns out to be good | `release`: a `verdict` line with who and why, then its record lines in a new segment | Moves forward |
| A later capture is good while an earlier one is still held | It is ingested against the last accepted state. The held one is released or marked `rejected` by hand | Moves forward |
| The format changes for good | Every capture is kept and held. The splitter or reader is fixed and tested on the held captures, then they are released in order. The cost is delay, not a hole | Ages honestly until the release |
| The machine reboots mid-run | Captures are written to a temporary name and renamed, body and meta before anything else. A segment is written whole and renamed, then one chain line is appended. On start, `ingest` journals any capture that has no `fetch` line and re-appends a chain line for a segment that lacks one | Nothing wrong |
| Days are missed | Nothing: there are no fetch lines for those days. The next run diffs against the last accepted state | The source's date ages; the digest reports the gap |
| A splitter bug is found after the fact | `reread`: the affected captures are split again and the difference is appended as record lines that name the original fetch and the new `splitter_rev`. The old lines stay | Editions already published keep their stamps; new ones use the corrected lines |
| A reader bug is found | Nothing in the journal. The reader is fixed, the index rebuilt, and the difference in `claim` is reviewed like any code change | New editions carry a new code revision |

Guards run before acceptance. The list in review-data section 5.1 is the one to implement; the toy has five of them.

## 5. The three ledger states

For one cell (object, property, source), as of segment N. The rule is a view, so it can be tightened later without touching history.

```
a claim for the cell is live at N                                -> measured (a value or a limit, by `bound`)

else, the source last ANSWERED about this object (a list fetch
accepted with the object's record in it, or an `asked` line
with outcome `answered`), and all of:
  - the answer is younger than the source's stale-after age
  - the source's own edition date is later than the date the
    object was designated
  - the object's record has the field and it is empty             -> looked for and absent

anything else                                                    -> not checked, with a reason:
                                                                    never_asked, last_try_failed, held,
                                                                    unknown_to_source, stale,
                                                                    source_older_than_object
```

Why an outage cannot display as "not measured":

- A failed or held fetch writes no `record` and no `asked: answered` line. The only thing that can move a cell towards "absent" is an accepted answer.
- For a source with no edition date of its own, such as JPL's lists, the capture time stands in for it.
- The first two conditions are upstream-physical's: SsODNet's build is 71 days old, so for the 144 or more reachable asteroids first observed after it, its cells are "not checked", not "absent" [colleague: upstream-physical].
- A source that goes quiet does not leave old "absent" cells standing. They age into "not checked: stale".
- Two guards cover the remaining routes: a filled count per physical field that falls holds the capture, and a count of claims per (source, property) that falls after a reader change holds the edition.
- The fault tests assert it directly: after each single fault, no cell is "looked for and absent" that was not before. The toy checks the stronger condition that no record line is written at all [test].

The entry's row (the four states in `DESIGN.md` section 3) is computed from the cells: a measurement or a limit if any source has one; a labelled guess, "not measured", only if every source registered for that property is "looked for and absent"; otherwise "not checked". Whether the page shows "not measured, 2 of 5 sources not checked" is a display decision; the edition carries the per-source states and dates either way.

## 6. Frozen science on moving data

**Three stamps on every derived value, edition and page.**

| Stamp | What it is | Changes |
|---|---|---|
| Data | Segment number and the running hash at that segment, with each source's last accepted capture time | Every accepted run |
| Method | A git tag (`method/0.1`): prior tables, thresholds, mission presets, the property registry, the rule for which source leads each property, the price scenario and its date, the list of sealed references. Deposited at a gate | By hand |
| Code and schema | The commit of the readers and exporter, and the edition schema version | With the code |

A page footer reads, for example, `data #412 (2026-12-03) · method 0.1`.

**The frozen method runs every day; tuning never does.** `derive` is a pure function of the views as of a segment and a method tag: no network, no clock (dates are arguments), seeds fixed from the object key and the method version, one rounding rule. A new asteroid gets its prior the day it appears. H changed for 37 objects in 3.4 days [test], and each gets a new derived row, keyed by a hash of its inputs. The old row is still there.

**Forecasts and scoring.**

- A forecast is a record in the journal from `longshot.forecast`: question id, object key, method, a probability per outcome, the hash of its inputs, and the segment those inputs were read at. A new one is written only when the inputs change. None is replaced.
- A resolution is a record from `longshot.resolution`, entered by a person: question, object, outcome, the claim that settled it, and three dates where known (observed, published, first seen in this journal).
- A score is a view over those two. The forecast scored is the last one whose input segment precedes the resolving observation. Which of the three dates governs when only some are known is a protocol decision the plan has not made [colleague: review-data]. The scorer refuses if the forecast's inputs include a claim from the resolving reference.
- Sealed labels: a reference on the method's sealed list is ingested and dated like any other, and its claims are marked `embargoed` and left out of `derive` until an `embargo` line releases them. Their arrival time is on record.
- If upstream later withdraws the value that resolved a forecast, a new resolution record is appended and the page shows both.

**The freeze bundle.** A method release or a forecast freeze writes `data/freezes/<id>/`: the exact claim rows that fed each forecast, the forecasts, and a manifest with the segment, the running hash, the method tag and the code commit. The manifest and its hashes are what gets deposited outside; restricted values are not. A frozen forecast therefore does not depend on the index, a reader revision, or the journal surviving in its present form.

**Reproducing a number shown on a given day.**

1. Read the stamps from the page, or look up the edition in the journal (`longshot.edition` records say what was published when).
2. Check out the code commit and method tag named in the edition's manifest. The lockfile pins the environment.
3. `index --upto <segment>`, which checks the running hash.
4. `derive` and `export`.
5. Compare the table hashes with the manifest's.

**Outside anchoring.** The running hash proves order and integrity only to the project. It becomes evidence for others when a chain value is deposited: at every method release, and each quarter if the owner wants [estimate that quarterly is enough].

## 7. What the app reads

Proposed. It restates the rule in `DESIGN.md` section 8 and adds what daily data needs. It does not choose files, a database, a server or a language.

- **The app reads editions and nothing else.** It never calls an upstream service. An edition is immutable and identified by (segment, method, schema). Publishing is an atomic swap to a new edition; rollback is a swap back. Any edition can be regenerated from its stamps.
- **Logical tables in an edition:** `objects` (key, names, lifecycle, populations); `rows` (per object and property: state, the leading value with range, source and dates, and the per-source states); `claims` (every cited value); `derived` (pass probabilities per mission preset, mass and price ranges per named scenario, the observe-next ranking); `windows`; `changes`; `record` (forecasts, due dates, outcomes, scores); `field` (one compact table for the picture of all asteroids: key, delta-v, H, size range, state flags); `registries` (properties, sources with citation, licence class and stale-after age, presets, questions); `manifest` (the stamps, each source's last accepted time and upstream edition date, table hashes).
- **Two filtered forms.** The page form may show one restricted value at a time with its citation. The open form holds only redistributable values and the project's own products. `field` and anything downloadable come from the open form, so the browser never receives a restricted table [colleague: review-extend].
- **What the app may compute:** select, sort, filter and count exported values; compare a stored date with the clock; conversions the edition names. The stale banner is computed at viewing time from the manifest's dates and the registry's ages, so it is true when every job is dead [colleague: review-ops]. "Open now" is said only when the reachable list's capture is under two days old.
- **What it may not compute:** any probability or range, and any sum of probabilities over a visitor's filter. Every filter combination offered is an exported preset [colleague: review-extend].
- **History.** `changes`, `windows`, `record` and a per-object history (the dated versions of the fields an entry shows) are written into each edition by default. If the chosen stack has a query engine on the server, the same views can be read from a loaded copy of the index, and "as of any date" becomes a request-time query. That is one of the things the stack decision turns on.
- **Visitor state**, if there is any, lives in a separate store and never enters the journal. It refers to public ids that are never reused: object key, question id, preset id, edition id.

What the stack choice depends on, from this design: whether history views are made on request or ahead; whether visitors write anything; whether the licence filter runs at export or per request; whether the place that serves the app is also the place that runs `collect`.

## 8. What this buys, and what it costs

**What it buys.**

1. **The one thing that cannot be bought later.** JPL shows only the current orbit and the next window. Between two pulls 3.4 days apart, 342 orbits were replaced, 12 listed windows vanished and 188 had their start rewritten [test]. The journal has all of it, in a form a query can read.
2. **The three states by construction.** "Absent" needs a journaled answer. An outage, a held response and an object the source does not know each leave a different trace, and none of them is an answer.
3. **"What changed" is the journal read through a filter.** The filter is a view, so learning in March that some field is noise fixes the past as well as the future.
4. **Window history.** The first start seen, the window that dropped off the list, the peak brightness when it was first listed. None of these can be had from a current-state table unless it was designed for them in advance.
5. **Decisions deferred safely.** The property list, units, error-bar conventions, the state rule and the change classes are views over stored records. The reviews ask for these to be right before any reader exists; here only six line shapes have to be. A property added next year has its history back to the first capture, because the records kept every upstream field, shown or not.
6. **Frozen and current at once.** The data state is a position in a file sequence. "As of segment N" is a filter, not a copy.
7. **Format changes and outages cost delay, not data.** Bytes are kept whether or not they parse.
8. **Stack-neutral.** The asset is plain text files and xz bodies. The index engine can be replaced without touching them, and the app is handed an edition.
9. **Traceable end to end.** Edition, derived row, inputs hash, claims, record lines, fetch, capture, sha256 of the bytes.
10. **Good for agents.** A test builds a ten-line journal by hand. A reviewer reads a segment with `grep`. The forbidden edit (changing history) is a change to a read-only file that the chain check catches.

**What it costs.**

1. **More code than overwriting a table.** Every question needs a view, and a view has to be rebuilt when its logic changes. My estimate for the first step is 800 to 1,200 lines with tests, against the toy's 244.
2. **Two notions of time.** Capture time and journal order differ whenever a held capture is released late. A rule that confuses them scores a forecast against the wrong inputs, which is the one error the record cannot survive.
3. **Mistakes stay.** A wrong line is corrected by another line, and the journal accumulates them.
4. **The past as displayed can change.** A reader fix alters old claims. Editions and freeze bundles pin what was actually shown, at the cost of keeping them.
5. **Most of what it records daily is orbit and tracking churn**, which bears least on what an asteroid is made of. Physical measurements arrive rarely and through review, where the journal adds dates and little else.
6. **Its value arrives late.** After two weeks it holds two weeks. The record page needs it in 2027.
7. **Storage is kept twice**: captures and journal, about 1.2 GB a year together.

## 9. Extension points, and what is not built yet

**Extension points.**

- **A new source:** a registry entry, a splitter (for a table, a column mapping), a reader, and a contract test on one stored response. No new table. Its history starts at its first capture.
- **A new release of a source** (Gaia DR4 after DR3, a new SsODNet data model): a new source id with the release in it; claims from both coexist.
- **A new property:** a registry entry and one reader mapping. It applies to every stored record version, so the property arrives with its history.
- **A new population:** another request shape and another `membership` name. All near-Earth objects are already keyed. "Reachable, future launch windows only" is a different request to the same service.
- **A new mission type, price scenario or derived quantity:** a method entry and a new method version.
- **A new view:** a query over what is already journaled. Examples: how long each window stayed listed; how often an object crosses 6 km/s and crosses back; discovery against follow-up over time.
- **The project's own measurements** (orbit refits, colours from Minor Planet Center photometry) and **reported measurements:** sources of kind `own` and `reviewed`, beside JPL's values, never replacing them.
- **Another index engine, another host, a second front end:** the journal and the edition are the two interfaces. Neither names a product.

**Not built yet, on purpose.**

- A schedule for per-object crawls beyond the follow-up rule and the rebuild trigger.
- The Minor Planet Center's observations, the reachable list's per-object trajectories, Horizons.
- The orbit fitter and anything in WP5.
- Automatic entry of values from papers. There is a queue and a person.
- A queue, a workflow engine or a plug-in system. One program on a timer.
- A server database, an interface for other programs, a public download.
- Visitor state of any kind.
- An "as of any date" interface.
- Live prices. The price scenario is part of the method.
- Thinning or compacting captures or the journal. Revisit at 10 GB.
- A second writer of the journal.
- A tool for starting a new journal from captures (section 11, item 5).
- Pages for the 36,000 near-Earth objects outside the reachable list. They are journaled and keyed and not shown.
- Forecast and scoring code. The line shapes are reserved; nothing runs until method 0.1 exists.

## 10. First step, and the first two weeks

### The first step

**Build the journal, offline, on the two pulls already on disk, and prove it.** That is `collect` (with the network switched off and the two pulls imported as four captures), `ingest` for the two JPL lists with the guards and the identity step, and `index` with `record_span`, `object`, `alias`, `membership`, `field_change` and `window`.

Done means all of these pass as tests:

1. Segments 1 and 2 reproduce today's measured diff: 7,229 then 7,231 on the reachable list with 2 joined and none gone; 43,367 then 43,379; 342 near-Earth rows changed, all with a new orbit solution; 222 reachable rows changed, 199 of them only in clock-driven fields and 23 with a new solution; 1,388 then 1,389 under 7 km/s; 17 reachable rows one solution behind.
2. Building twice from nothing gives the same running hash. Deleting the index and rebuilding it gives the same tables.
3. Each single-fault case (the nine in section 2 and the rest of review-data's list) writes no record line, or the same lines as the clean run, and moves no cell to "looked for and absent".
4. A run killed between any two writes resumes with no duplicate and no gap.
5. `data/` has one copy off this disk, and a restore from that copy passes `verify`.

It deliberately leaves out: readers and the `claim` view; any property schema; SsODNet and every other source; priors, the method and forecasts; the export and the app; scheduling and the choice of where it runs; and any network call. JPL allows no automated call until a contact address is set, so the live switch-on is the day after the owner supplies one.

Why this first and not the capture step alone: strictly, only captures and the record of each fetch cannot be backfilled, and the journal could be built from them later. Three things argue for doing both now. The guards live in `ingest`, and without them nothing can tell a good capture from a bad one or raise an alarm. The diff is the monitoring signal. And the event shapes get tested on real data before weeks of captures accumulate under a request that lacks the fields identity needs. The toy took about an hour.

### The first two weeks

1. **Days 1 to 2, offline:** the first step above. In parallel the owner settles the contact address, where `collect` runs and where its notices go, and where the off-machine copy lives.
2. **Days 2 to 3:** the first live capture, with `spkid`, `soln_date`, `source` and `full-prec` added to the near-Earth request (one `rebase`). The 16:00 capture-only trigger from a second place. A dead-man's switch that fires when no accepted capture exists for 36 hours [colleague: review-ops].
3. **Days 3 to 5:** the follow-up rule (single-object calls for reachable objects with a new solution), the identifier call for names that appear or vanish, and the probes of the slow sources as journaled fetches.
4. **Days 5 to 7:** `change_event` and the first weekly digest built from it.
5. **Week 2:** readers for the entry's dozen properties from the two JPL sources; `claim`, `coverage` and the state rule of section 5; the 1,704 SsODNet cards and the lightcurve database from the 21 November archive imported as dated captures; the plan's ten fixtures as tests pinned to segments, with fixtures for change over time added.
6. **End of week 2:** read fourteen days of real churn against the 3.4-day sample; set the guard tolerances and the run time from the measured lag; export a first edition with no model in it; hold the stack conversation with that edition in hand.

My estimate is one to two days of agent work for the first step and the rest of the fortnight for items 2 to 6, with the owner answering at the decisions in section 12.

## 11. Weaknesses

1. **It puts infrastructure ahead of anything a visitor can see.** The owner wants a prototype to show. This design spends its first two days on something invisible and its first two weeks on a data set with no model in it.
2. **What it captures every day matters least to the project's question.** On this sample, orbit and window churn is the whole daily journal; no physical field changed in 3.4 days. For the slow sources the design adds honest dates and not much more, and the largest finding of the day (35 rotation periods in a table the project did not use) came from adding a source, not from keeping history.
3. **Two clocks will confuse someone.** A late release puts lines in the journal after lines from later captures. "As of segment" and "as of date" then differ. The scoring rule has to name one, and I have not shown that the choice is safe in every case.
4. **Interpretation moved, not removed.** Keeping records in upstream's shape makes the journal robust and the readers numerous. Each source needs a reader, and a reader change silently rewrites what the views say about the past until someone looks at the diff.
5. **Append-only is unforgiving of an early mistake in the journal itself.** A wrong splitter key or a wrong identity decision is corrected by more lines, and the views must understand corrections. The fallback, starting a second journal from the captures and keeping the first for whatever cites it, is by hand and not designed here.
6. **Identity is logged, not solved.** Whether two names are one object still depends on JPL's full-name field, an untested `spkid`, and the Minor Planet Center's identifier service. A wrong merge is recorded faithfully and must be undone by a line the design does not yet have.
7. **The journal can never be published as it is.** Once SsODNet or Pravec's table is in it, it holds values that may be shown one at a time and not redistributed. Outside verification rests on deposited hashes. A store that forbids deletion also conflicts with honouring a rights holder's request to remove something; that needs a redaction procedure (replace a body with its hash) which breaks strict immutability.
8. **One writer.** Two triggers in two places are safe only because the second writes captures and never the journal. If both places ever run `ingest`, the chain forks.
9. **The sizing rests on one 3.4-day interval and two list sources.** ESA's log suggests the interval was quiet. The size of a full-precision pull is unknown. No live request was made, so the collector's behaviour against JPL is untested.
10. **Rebuild time is extrapolated.** 4.1 seconds today. A whole-catalogue refit adds 43,000 lines at once, and full precision will make every refit change more fields. An incremental index path will be wanted eventually, and it must be tested to equal a rebuild.
11. **The running hash proves nothing to an outsider until it is deposited somewhere outside.**
12. **Agents will be tempted to fix data by editing it.** Read-only files, the chain check and a locked off-machine copy make that visible. They do not make it impossible on the working disk.

## 12. Decisions needed from the owner

1. **The contact address and product name for JPL's User-Agent.** It blocks the first live capture, and each day without one is history that cannot be recovered. A role address that forwards to an inbox he reads.
2. **Where `collect` runs and where notices go.** The place needs to be on every day, have outbound HTTPS from a stable address, a disk that persists (about 1.2 GB a year), a way to guarantee one JPL request at a time, and a way to raise an alarm. This workstation was powered 70% of the last 41 days [colleague: review-ops]. A second place is wanted for the capture-only trigger.
3. **Where the off-machine copy of `data/` lives**, with delete and overwrite forbidden for `captures/` and `journal/`, and whether the repository gets a private remote.
4. **Yes or no to a standard-library-only backbone with SQLite as the rebuildable index.** No package is needed. The index engine can be changed later without touching the journal.
5. **The project's own object key** in place of "JPL's permanent id", minted for all 43,379 near-Earth objects, and its public form.
6. **The request for the first live pull:** add `spkid`, `soln_date`, `source` and `full-prec`, accepting one day on which every row is rewritten.
7. **ESA's change log as an internal cross-check.** Its terms allow personal non-commercial use and no redistribution without written permission [colleague: upstream-orbits]. It would be captured and never shown.
8. **Which date governs scoring** when a measurement's observation date is unknown: publication, or the day this journal first saw it.
9. **What the site does with an object the Minor Planet Center has withdrawn and JPL still lists**, and with one that leaves the reachable list.
10. **Whether restricted-licence responses may sit in a store that forbids deletion**, and the redaction procedure if not.
11. **Whether history views are made ahead by the pipeline or on request by the app.** This belongs to the stack conversation.

## 13. Not verified

- Any live JPL behaviour: the size of a full-precision response, whether `full-prec` reaches the fitted push values, whether `spkid` changes at numbering, when the trajectory run finishes each day.
- That 10:00 UTC is late enough. The measured lag is "more than 12.7 hours" [colleague: upstream-orbits].
- Every rate. They come from one interval of 3.36 days.
- The toy has no identity step, no readers and no per-object source. The claims about them are design, not test.
- Crash safety between writes. The toy writes a segment by rename and I did not kill it mid-run.
- The index size and rebuild time beyond two segments.
- Everything tagged [colleague]. I re-read two JPL pages and nothing else.
- The effort figures.

## 14. Sources

Read by me today (2026-11-24):

- JPL API fair-use policy (one request at a time; a User-Agent with product name, version and contact; no embedding in a website; back off on errors; formats "can change without notice"; check the `version` field): https://ssd-api.jpl.nasa.gov/doc/
- JPL SBDB Query API (`full-prec`; fields `spkid`, `soln_date` in Pacific local time, `source`, `orbit_id`, `pdes`; "Either `spkid` or `pdes` should be used for permanent IDs"; version 1.0, August 2021; no date filter on the page): https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html

Tested by me today, local files only: `data/snapshots/2026-11-21` and `/2026-11-24`, including the saved response headers of the second pull (no ETag, no Last-Modified).

Not read by me today; taken from colleagues' reports of today, which give the URL and say how each was checked:

| Claim used here | URL | Report |
|---|---|---|
| The reachable list is a daily analysis; its interface is version 1.3 (the version is also in the local file) | https://cneos.jpl.nasa.gov/nhats/intro.html ; https://ssd-api.jpl.nasa.gov/doc/nhats.html | upstream-orbits, review-data |
| JPL's single-object interface returns covariance, the force law, alternate ids; 2 to 7 kB a response | https://ssd-api.jpl.nasa.gov/doc/sbdb.html | upstream-orbits |
| JPL's window rule skips days around full moon | https://cneos.jpl.nasa.gov/nhats/obs.html | review-data, upstream-orbits |
| Minor Planet Center: daily circular about 12:30 UT; identifier service takes 100 names a request; 5 requests a second | https://www.minorplanetcenter.net/mpec/RecentMPECs.html ; https://docs.minorplanetcenter.net/mpc-ops-docs/apis/query-identifier/ ; https://docs.minorplanetcenter.net/mpc-ops-docs/faqs/ | upstream-orbits |
| ESA's change log, its size, its history of refit days, its terms | https://neo.ssa.esa.int/PSDB-portlet/download?file=updated_nea.lst ; https://neo.ssa.esa.int/terms-conditions | upstream-orbits |
| SsODNet: build stamp of 14 September 2026 in every card; static files with Last-Modified and ETag; 404 or an `error` entry for an unknown object | https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ ; https://ssp.imcce.fr/data/ssodnet_biblio.json | upstream-physical, review-extend |
| Pravec's table, the lightcurve database, MITHNEOS, ALCDEF, the arXiv listing as probe targets | http://space.asu.cas.cz/~ppravec/newres.txt ; https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip ; http://smass.mit.edu/minus.html ; https://alcdef.org/ ; https://rss.arxiv.org/rss/astro-ph.EP | upstream-physical |
| Workstation uptime, absence of backups, the dead-man's switch and digest design | local logs; https://healthchecks.io/pricing/ | review-ops |

Project files: `AGENTS.md`, `DESIGN.md`, `docs/plan.md` (sections 1.4, 3, 4, 6, 7, Appendices A to C), and the five reports in this folder.

## Appendix: the toy journal behind the [test] numbers

Three scripts, standard library only, 244 lines. They are not project code: they have no identity step, no readers and five guards. They are reproduced here in full; copies are in `factlog/scripts/` in `data/backbone-review-2026-11-24.tar.zst`. Save them side by side outside the repository and run, in order:

```
python3 -I toy.py    data/snapshots <out>            # two segments, built twice, chain compared
python3 -I index.py  <out>/a/journal <out>/a/index.db       # the index and the views in section 2
python3 -I faults.py data/snapshots <out2>           # nine single faults; writes about 430 MB, delete after
```

Output on 2026-11-24 (trimmed to the figures used above):

```
ingest seconds: 8.23 | chain equal on second build: True
seg 1: lines 50600, bytes 44450706, xz 4209176, nhats new 7229, sbdb new 43367
seg 2: lines 582, bytes 476283, xz 62948, nhats changed 222 new 2, sbdb changed 342 new 12
index build seconds: 4.09 | db bytes: 99221504
as of seg 1: reachable 7229 | under 5/6/7 km/s [286, 726, 1388] | near-Earth rows 43367
as of seg 2: reachable 7231 | under 5/6/7 km/s [286, 726, 1389] | near-Earth rows 43379
nhats rows changed: 222 | clock only: 192 | clock or radar-outlook only: 199 | with new solution: 23 | reach changed: 11 | brightness: 7
sbdb rows changed: 342 | with new solution: 342 | physical: 0 | brightness: 45 | push: 5 | tracking: 342 | elements: 47
windows with the same end and a rewritten start: 188 | of those 11-21 -> 11-27: 184
windows listed in seg 1 and no window in seg 2: 12 | window end changed: 16
orbit_id lag (nhats behind sbdb) at seg 2: 17
faults: 8 cases with record_events=0, gone=0, other_source_unaffected=True; key-order shuffle same_as_clean_run=True
```

`brightness: 45` counts rows where H, its uncertainty or the slope parameter changed; H itself changed in 37. Each segment has four lines beyond its record lines: two `fetch` and two `verdict`.

### toy.py

```python
"""Toy fact log over the two local JPL pulls. Standard library only. Run: python3 -I toy.py <snapshots dir> <out dir>
Not project code: a feasibility and sizing test for design-fact-log.md."""
import hashlib, json, lzma, os, sqlite3, sys, time, shutil

SNAP, OUT = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/")
canon = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
sha = lambda b: hashlib.sha256(b).hexdigest()

SOURCES = {
    "jpl.nhats":    {"file": "nhats.json",    "key": "des",  "version": "1.3"},
    "jpl.sbdb_neo": {"file": "sbdb_neo.json", "key": "pdes", "version": "1.0"},
}
# pull times: first from file mtime (inferred), second from the saved Date header
RUNS = [("2026-11-21", {"jpl.nhats": "2026-11-21T16:35:13Z", "jpl.sbdb_neo": "2026-11-21T16:35:19Z"}),
        ("2026-11-24", {"jpl.nhats": "2026-11-25T01:12:45Z", "jpl.sbdb_neo": "2026-11-25T01:12:55Z"})]

def split(source, body):
    """bytes -> (api_version, declared_count, {key: record dict}). The only source-specific code in the log layer."""
    d = json.loads(body)
    ver = d["signature"]["version"]
    if source == "jpl.nhats":
        rows = d["data"]
    else:
        f = d["fields"]; rows = [dict(zip(f, r)) for r in d["data"]]
    k = SOURCES[source]["key"]
    out = {}
    for r in rows:
        if r[k] in out: raise ValueError("duplicate key " + r[k])
        out[r[k]] = r
    return ver, int(d["count"]), out

def guards(source, ver, count, recs, live):
    g = []
    g.append(("version_pinned", ver == SOURCES[source]["version"], ver))
    g.append(("count_matches_rows", count == len(recs), f"{count} vs {len(recs)}"))
    if live:
        gone = len(set(live) - set(recs))
        g.append(("rows_not_dropped", gone <= 5, f"{gone} keys vanished"))
        if source == "jpl.sbdb_neo":
            for fld in ("diameter", "albedo", "rot_per"):
                was = sum(1 for b in live.values() if b[1].get(fld) is not None)
                now = sum(1 for r in recs.values() if r.get(fld) is not None)
                g.append((f"filled_{fld}_not_fallen", now >= was - 2, f"{was}->{now}"))
    return g

def ingest(outdir, runs, bodies_override=None, fail=None):
    """Append one segment per run. Returns (chain hash, stats)."""
    os.makedirs(outdir + "/journal", exist_ok=True)
    live = {s: {} for s in SOURCES}          # source -> key -> (hash, record)
    chain, seq, fid, stats = "0" * 64, 0, 0, []
    for seg_no, (day, times) in enumerate(runs, 1):
        lines = []
        for source in SOURCES:
            fid += 1
            if fail and (seg_no, source) in fail:      # transport failure: a fetch event and nothing else
                lines.append({"t": "fetch", "fid": fid, "source": source, "started_at": times[source], "transport": "timeout"})
                continue
            body = (bodies_override or {}).get((seg_no, source)) or open(f"{SNAP}/{day}/{SOURCES[source]['file']}", "rb").read()
            lines.append({"t": "fetch", "fid": fid, "source": source, "started_at": times[source], "transport": "ok",
                          "http_status": 200, "body_sha256": sha(body), "body_bytes": len(body), "scope": "list"})
            try:
                ver, count, recs = split(source, body)
                g = guards(source, ver, count, recs, live[source])
            except Exception as e:
                g = [("parses", False, repr(e)[:80])]
            ok = all(x[1] for x in g)
            lines.append({"t": "verdict", "fid": fid, "outcome": "accepted" if ok else "held",
                          "guards": [{"name": n, "ok": o, "detail": d} for n, o, d in g]})
            if not ok: continue
            cur = live[source]
            for k in sorted(recs):
                h = sha(canon(recs[k]).encode())[:32]
                if k not in cur:
                    lines.append({"t": "record", "fid": fid, "source": source, "key": k, "kind": "new", "hash": h, "body": recs[k]})
                elif cur[k][0] != h:
                    lines.append({"t": "record", "fid": fid, "source": source, "key": k, "kind": "changed", "hash": h, "prev": cur[k][0], "body": recs[k]})
                cur[k] = (h, recs[k]) if k not in cur or cur[k][0] != h else cur[k]
            for k in sorted(set(cur) - set(recs)):
                lines.append({"t": "record", "fid": fid, "source": source, "key": k, "kind": "gone", "prev": cur[k][0]})
                del cur[k]
        for l in lines:
            seq += 1; l["seq"] = seq
        data = ("\n".join(canon(l) for l in lines) + "\n").encode()
        path = f"{outdir}/journal/{seg_no:06d}.ndjson"
        with open(path + ".tmp", "wb") as f: f.write(data); f.flush(); os.fsync(f.fileno())
        os.rename(path + ".tmp", path)
        chain = sha((chain + sha(data)).encode())
        with open(outdir + "/journal/chain.ndjson", "a") as f:
            f.write(canon({"seg": seg_no, "sha256": sha(data), "chain": chain, "last_seq": seq}) + "\n")
        kinds = {}
        for l in lines:
            if l["t"] == "record": kinds[(l["source"], l["kind"])] = kinds.get((l["source"], l["kind"]), 0) + 1
        stats.append({"seg": seg_no, "lines": len(lines), "bytes": len(data), "xz": len(lzma.compress(data)), "kinds": kinds})
    return chain, stats

if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    t = time.time(); c1, st = ingest(OUT + "/a", RUNS); t1 = time.time() - t
    c2, _ = ingest(OUT + "/b", RUNS)
    print("ingest seconds:", round(t1, 2), "| chain equal on second build:", c1 == c2, c1[:16])
    for s in st: print(s)
```

### index.py

```python
"""Build a throwaway SQLite index from the toy journal and run the views. python3 -I index.py <journal dir> <db path>"""
import glob, json, os, sqlite3, sys, time, collections
J, DB = sys.argv[1], sys.argv[2]
if os.path.exists(DB): os.remove(DB)
t0 = time.time()
db = sqlite3.connect(DB)
db.executescript("""
CREATE TABLE fetch(fid INTEGER PRIMARY KEY, seg INT, source TEXT, started_at TEXT, transport TEXT, http_status INT, body_sha256 TEXT, body_bytes INT);
CREATE TABLE verdict(fid INT, seg INT, outcome TEXT, guards TEXT);
CREATE TABLE record_event(seq INTEGER PRIMARY KEY, seg INT, fid INT, source TEXT, skey TEXT, kind TEXT, hash TEXT, prev TEXT, body TEXT);
CREATE TABLE record_span(source TEXT, skey TEXT, hash TEXT, body TEXT, from_seg INT, to_seg INT);
CREATE TABLE field_change(seg INT, source TEXT, skey TEXT, field TEXT, old TEXT, new TEXT, class TEXT);
""")
NH_CLOCK = {"obs_start", "obs_end", "obs_mag", "obs_flag"}
NH_RADAR = {"radar_snr_a", "radar_obs_a", "radar_snr_g", "radar_obs_g"}
SB = {"identity": "full_name pdes name prefix kind", "flags": "neo pha class", "brightness": "H H_sigma G",
      "physical": "diameter diameter_sigma albedo rot_per GM density BV UB spec_B spec_T",
      "elements": "epoch e a q i om w ma ad n per_y moid moid_jup t_jup",
      "tracking": "condition_code data_arc n_obs_used n_del_obs_used n_dop_obs_used first_obs last_obs rms",
      "push": "A1 A1_sigma A2 A2_sigma A3 A3_sigma DT", "solution": "orbit_id producer two_body"}
SBC = {f: c for c, fs in SB.items() for f in fs.split()}
def cls(source, f):
    if source == "jpl.nhats":
        b = f.split(".")[0]
        return "clock" if b in NH_CLOCK else "radar_outlook" if b in NH_RADAR else "solution" if b in ("orbit_id", "occ") \
            else "reach" if b in ("min_dv", "min_dur", "n_via_traj") else "brightness" if b in ("h", "min_size", "max_size") else "identity"
    return SBC[f]
def flat(r):
    o = {}
    for k, v in r.items():
        if isinstance(v, dict): o.update({k + "." + kk: vv for kk, vv in v.items()})
        else: o[k] = v
    return o
live = {}
for path in sorted(glob.glob(J + "/[0-9]*.ndjson")):
    seg = int(os.path.basename(path)[:6])
    for line in open(path, encoding="utf-8"):
        e = json.loads(line)
        if e["t"] == "fetch":
            db.execute("INSERT INTO fetch VALUES(?,?,?,?,?,?,?,?)", (e["fid"], seg, e["source"], e["started_at"], e["transport"], e.get("http_status"), e.get("body_sha256"), e.get("body_bytes")))
        elif e["t"] == "verdict":
            db.execute("INSERT INTO verdict VALUES(?,?,?,?)", (e["fid"], seg, e["outcome"], json.dumps(e["guards"])))
        elif e["t"] == "record":
            k = (e["source"], e["key"]); body = e.get("body")
            db.execute("INSERT INTO record_event VALUES(?,?,?,?,?,?,?,?,?)", (e["seq"], seg, e["fid"], e["source"], e["key"], e["kind"], e.get("hash"), e.get("prev"), json.dumps(body, sort_keys=True) if body else None))
            if k in live:
                old = live[k]
                db.execute("UPDATE record_span SET to_seg=? WHERE source=? AND skey=? AND to_seg IS NULL", (seg, *k))
                if body:
                    a, b = flat(old), flat(body)
                    for f in sorted(set(a) | set(b)):
                        if a.get(f) != b.get(f):
                            db.execute("INSERT INTO field_change VALUES(?,?,?,?,?,?,?)", (seg, e["source"], e["key"], f, json.dumps(a.get(f)), json.dumps(b.get(f)), cls(e["source"], f)))
            if body:
                db.execute("INSERT INTO record_span VALUES(?,?,?,?,?,NULL)", (e["source"], e["key"], e["hash"], json.dumps(body, sort_keys=True), seg)); live[k] = body
            else: live.pop(k, None)
db.executescript("CREATE INDEX rs ON record_span(source, skey); CREATE INDEX fc ON field_change(seg, source, skey);")
db.commit()
print("index build seconds:", round(time.time() - t0, 2), "| db bytes:", os.path.getsize(DB))
q = lambda s, *a: db.execute(s, a).fetchall()
# as-of: the reachable list as it stood after segment N
for seg in (1, 2):
    t = time.time()
    rows = q("SELECT body FROM record_span WHERE source='jpl.nhats' AND from_seg<=? AND (to_seg IS NULL OR to_seg>?)", seg, seg)
    dv = [float(json.loads(b)["min_dv"]["dv"]) for (b,) in rows]
    print(f"as of seg {seg}: reachable {len(dv)} | under 5/6/7 km/s {[sum(x < c for x in dv) for c in (5, 6, 7)]} | query s {time.time() - t:.2f}")
    n = q("SELECT count(*) FROM record_span WHERE source='jpl.sbdb_neo' AND from_seg<=? AND (to_seg IS NULL OR to_seg>?)", seg, seg)[0][0]
    print(f"            near-Earth rows {n}")
# what changed in seg 2, by class
print("field changes seg 2 by source, class:", q("SELECT source, class, count(*), count(DISTINCT skey) FROM field_change WHERE seg=2 GROUP BY 1,2 ORDER BY 1,3 DESC"))
per = collections.defaultdict(set)
for s, k, c in q("SELECT source, skey, class FROM field_change WHERE seg=2"): per[(s, k)].add(c)
nh = {k: v for (s, k), v in per.items() if s == "jpl.nhats"}; sb = {k: v for (s, k), v in per.items() if s == "jpl.sbdb_neo"}
print("nhats rows changed:", len(nh), "| clock only:", sum(v <= {"clock"} for v in nh.values()), "| clock or radar-outlook only:", sum(v <= {"clock", "radar_outlook"} for v in nh.values()),
      "| with new solution:", sum("solution" in v for v in nh.values()), "| reach changed:", sum("reach" in v for v in nh.values()), "| brightness:", sum("brightness" in v for v in nh.values()))
print("  nhats rows changed with solution unchanged and something other than clock:", sorted((k, sorted(v)) for k, v in nh.items() if "solution" not in v and not v <= {"clock"})[:12])
print("sbdb rows changed:", len(sb), "| with new solution:", sum("solution" in v for v in sb.values()), "| physical:", sum("physical" in v for v in sb.values()),
      "| brightness:", sum("brightness" in v for v in sb.values()), "| push:", sum("push" in v for v in sb.values()), "| tracking:", sum("tracking" in v for v in sb.values()), "| elements:", sum("elements" in v for v in sb.values()))
print("radar-outlook changes sample:", q("SELECT skey, field, old, new FROM field_change WHERE class='radar_outlook' LIMIT 8"))
# the window view: first start ever seen is kept, a rewritten start is not news, a vanished window stays in history
w1 = {k: json.loads(b) for k, b in q("SELECT skey, body FROM record_span WHERE source='jpl.nhats' AND from_seg=1")}
w2 = {k: json.loads(b) for k, b in q("SELECT skey, body FROM record_span WHERE source='jpl.nhats' AND to_seg IS NULL")}
same_end = [k for k in w1 if k in w2 and w1[k]["obs_start"] and w2[k]["obs_start"] and w1[k]["obs_end"] == w2[k]["obs_end"] and w1[k]["obs_start"] != w2[k]["obs_start"]]
print("windows with the same end and a rewritten start:", len(same_end), "| of those 11-21 -> 11-27:", sum(w1[k]["obs_start"] == "2026-11-21" and w2[k]["obs_start"] == "2026-11-27" for k in same_end))
gone = [k for k in w1 if k in w2 and w1[k]["obs_start"] and not w2[k]["obs_start"]]
nxt = [k for k in w1 if k in w2 and w1[k]["obs_start"] and w2[k]["obs_start"] and w1[k]["obs_end"] != w2[k]["obs_end"]]
print("windows listed in seg 1 and no window in seg 2:", len(gone), "| window end changed (a different or re-cut window):", len(nxt))
print("orbit_id lag (nhats behind sbdb) at seg 2:", sum(1 for k in w2 if (o := q("SELECT body FROM record_span WHERE source='jpl.sbdb_neo' AND skey=? AND to_seg IS NULL", k)) and json.loads(o[0][0])["orbit_id"].replace("JPL ", "") != w2[k]["orbit_id"]))
```

### faults.py

```python
"""Single-fault runs against the toy log. python3 -I faults.py <snapshots dir> <out dir>"""
import json, random, sys, shutil, glob
import importlib.util
spec = importlib.util.spec_from_file_location("toy", __file__.replace("faults.py", "toy.py")); toy = importlib.util.module_from_spec(spec); spec.loader.exec_module(toy)
SNAP, OUT = toy.SNAP, toy.OUT
good = json.load(open(f"{SNAP}/2026-11-24/sbdb_neo.json")); nh = json.load(open(f"{SNAP}/2026-11-24/nhats.json"))
enc = lambda d: json.dumps(d).encode()
def mut(fn, base=good):
    d = json.loads(json.dumps(base)); fn(d); return enc(d)
ix = good["fields"].index
def drop_keep_count(d): d["data"] = d["data"][:-500]
def drop_fix_count(d): d["data"] = d["data"][:-500]; d["count"] = len(d["data"])
def empty_column(d):
    i = ix("rot_per")
    for r in d["data"]: r[i] = None
def version(d): d["signature"]["version"] = "1.1"
def shuffle_keys(d):
    random.seed(1)
    d["data"] = [dict(random.sample(list(r.items()), len(r))) for r in d["data"]]
cases = {
  "transport failure (timeout), sbdb":         dict(fail={(2, "jpl.sbdb_neo")}),
  "HTTP 200 with an error body, sbdb":          dict(bodies_override={(2, "jpl.sbdb_neo"): b'{"message":"internal error","code":"500"}'}),
  "HTML page instead of JSON, sbdb":            dict(bodies_override={(2, "jpl.sbdb_neo"): b"<html>maintenance</html>"}),
  "body cut off mid-stream, sbdb":              dict(bodies_override={(2, "jpl.sbdb_neo"): enc(good)[:9_000_000]}),
  "500 rows dropped, count unchanged, sbdb":    dict(bodies_override={(2, "jpl.sbdb_neo"): mut(drop_keep_count)}),
  "500 rows dropped, count adjusted, sbdb":     dict(bodies_override={(2, "jpl.sbdb_neo"): mut(drop_fix_count)}),
  "rot_per column emptied, sbdb":               dict(bodies_override={(2, "jpl.sbdb_neo"): mut(empty_column)}),
  "version string changed, sbdb":               dict(bodies_override={(2, "jpl.sbdb_neo"): mut(version)}),
  "key order shuffled in every row, nhats":     dict(bodies_override={(2, "jpl.nhats"): mut(shuffle_keys, nh)}),
}
base_chain, base_stats = toy.ingest(OUT + "/base", toy.RUNS)
def recs(d, seg, source):
    out = []
    for line in open(f"{d}/journal/{seg:06d}.ndjson", encoding="utf-8"):
        e = json.loads(line)
        if e["t"] == "record" and e["source"] == source: out.append((e["kind"], e["key"]))
    return out
def verdicts(d, seg):
    v = {}
    f2s = {}
    for line in open(f"{d}/journal/{seg:06d}.ndjson", encoding="utf-8"):
        e = json.loads(line)
        if e["t"] == "fetch": f2s[e["fid"]] = (e["source"], e["transport"])
        if e["t"] == "verdict": v[f2s[e["fid"]][0]] = (e["outcome"], [g["name"] for g in e["guards"] if not g["ok"]])
    for fid, (s, tr) in f2s.items(): v.setdefault(s, ("no body: " + tr, []))
    return v
for i, (name, kw) in enumerate(cases.items()):
    d = f"{OUT}/f{i}"
    toy.ingest(d, toy.RUNS, **kw)
    src = "jpl.nhats" if name.endswith("nhats") else "jpl.sbdb_neo"
    r = recs(d, 2, src); v = verdicts(d, 2)[src]
    other = "jpl.sbdb_neo" if src == "jpl.nhats" else "jpl.nhats"
    same_other = sorted(recs(d, 2, other)) == sorted(recs(OUT + "/base", 2, other))
    same_self = sorted(r) == sorted(recs(OUT + "/base", 2, src))
    print(f"{name:45s} verdict={v[0]:18s} failed_guards={v[1]} record_events={len(r)} gone={sum(k=='gone' for k,_ in r)} other_source_unaffected={same_other} same_as_clean_run={same_self}")
```
