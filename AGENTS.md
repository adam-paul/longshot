# longshot

Name tentative. A site that shows what is and is not known about each near-Earth asteroid on JPL's NHATS list (a round trip of at most 450 days; 7,229 on 2026-11-21, 7,231 on 2026-11-24): what is in it as a range, how hard it would be, and which observation would settle the most. Its purpose is a fun way into the claudestronomy community (claudestronomy.com).

State: a working prototype, built 2026-11-25 and rebuilt the same day to the instrument design Adam chose (`DESIGN.md` section 4, `docs/design.md`). The code is public at github.com/adam-paul/longshot; the site itself is not published, and nobody outside has been contacted. Adam's direction on 2026-11-24: build an MVP with the data already on disk, then decide what more to pull and how to store it. He agreed the stack that day (`DESIGN.md` section 8). Next: his decisions in `docs/build-report.md` section 12.

## Read first

- `DESIGN.md`: Adam's direction in his own words, what is decided, what is proposed, and what is open. It overrides the plan on anything about the site.
- `docs/mvp.md`: the build contract: layout, inputs, record format, field file, pages, URL state.
- `docs/design.md`: the look as built (the instrument design): tokens, type, marks, the glow, layout.
- `docs/build-report.md`: what the build does, its numbers, what is weak, and the decisions waiting for Adam.
- `docs/method.md` and `docs/method-value.md`: the constants in `method/v0_1/*.toml` and where each comes from.
- `docs/plan.md`: the science. Section 1 is what the research found, 3.5 the release order, 6 what is decided, 7 what is unverified. Appendix A is the validation protocol, B the build notes, C the work packages.
- `docs/research/`: the evidence. Do not read it end to end. Where files disagree, `verify-*.md` and `summaries-verification.md` win over the 20 November reports and `summaries-round1.md`. By part:
  - sources, coverage, what the snapshot holds: `catalogs.md`, `verify-coverage.md`
  - service limits, licences, dates: `verify-facts-venues.md`
  - size, spin and class from brightness: `verify-prior-null.md`, `verify-coverage.md`
  - orbit fitting: `verify-fit-repro.md`, `verify-nongrav.md`
  - observing windows: `verify-obs-window.md`
  - the price tag and what has been brought back: `value-inputs.md`, `capability.md` and their `verify-` files
  - site ideas: `presentation.md`, and the three concepts at the end of `summaries-review.md`
  - keeping the data current, for after the MVP: `architecture/summaries-backbone.md`
- `data/research-data-2026-11-21.tar.zst` (outside git; 570 MB): the snapshots, downloads, scripts and outputs behind the plan's numbers. Unpack with `mkdir -p data/research && zstd -dc data/research-data-2026-11-21.tar.zst | tar -x -C data/research`. Paths in the research files and scripts that start `data/research/` point into that folder.
- Also in `data/`: `snapshots/` (JPL's two bulk lists as pulled on 21 and 24 November), `sources/` (Pravec's rotation-period table, fetched 24 November, and SsODNet cards fetched since), `backbone-review-2026-11-24.tar.zst` (downloads and trial scripts from the architecture review), and `archive/` (the design mockups, review scratch and superseded files removed in the cleanup of 25 November; `docs/cleanup-2026-11-25.md` lists them).

## Layout and commands

- `longshot/`: the pipeline (`ingest/`, `ledger.py`, `model.py` and its stages, `contract.py`, `export.py`) and the site generator (`site/gen.py`, `site/templates.py`, `site/static/`: `style.css`, `app.js`, `field.js`, `fonts/`). `docs/mvp.md` section 2 lists every module.
- `method/v0_1/`: the method's constants with provenance; `tools/method_*.py` and `tools/value_*.py` derive and check them.
- `registry/`: the minted object keys (append only) and the hand-entered values.
- `tests/`, and `tools/`: the browser check, the synthetic field, the SsODNet fetcher, the table checksums.
- `build/` (intermediate records, logs, screenshots) and `dist/` (the site) are remade by every build and stay out of git.

```
uv run python -m longshot build                          # data on disk -> build/ and dist/, about a minute, no network
uv run python -m longshot serve                          # dist/ on http://127.0.0.1:8000/
uv run python -m unittest discover -s tests -t .         # about two minutes
uv run python tools/browser_check.py dist --gl gpu       # and --gl software; --shot <page>[@WxH] adds screenshots to build/screens/
```

The build needs `data/research/` unpacked (Read first, above) and `data/snapshots/2026-11-24/`. The daily collector and storage design in `docs/research/architecture/` are on hold. Three things from that review are kept: our own key for each asteroid (JPL's id changes when an asteroid is numbered); "not checked" as its own state; the app reads only the pipeline's output. Every page shows its data date, and observing windows are dated facts, never "open now".

## Rules

- AGENTS.md is the only context file. Never create CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md, and never run `/init` or `/import`.
- No message to an outside group and no public address until Adam says so.
- The stack is decided (`DESIGN.md` section 8): pre-built files, hand-written WebGL2, plain JavaScript and CSS, Python standard library. Ask before adding any dependency, in Python or JavaScript, and before choosing a host.
- Python goes through uv (`uv add`, lockfile committed), never `pip` or `uv pip install`, on a uv-managed interpreter (`uv venv --python 3.12`); the system Python cannot build environments reliably. The pipeline's package list is empty: standard library only. Say up front when something needs sudo.
- Nothing in `longshot/` opens an outbound connection (`serve` and the browser check only serve local files). The one fetcher is `tools/fetch_ssodnet_cards.py`, run by hand. The prototype needs no JPL call: `data/snapshots/2026-11-24/` holds the reachable list with its observing windows (`nhats.json`) and JPL's table of every near-Earth object (`sbdb_neo.json`). JPL allows one request at a time and requires a contact address in the User-Agent; none is set yet, so make no automated JPL call until one is.
- Data stays out of git. Never republish an upstream table; `docs/plan.md` Appendix B has the licence classes.
- Thresholds and bars are the numbers in `docs/plan.md` section 1.4 and Appendix A. They are proposals until Adam freezes them. After that, never change one, or the protocol, to pass a gate.
- Every number shown traces to a script output.
- Commit only when asked.

## Traps the research already hit

- A source being down, or not knowing an object, is "not checked". It never displays as "not measured".
- JPL's database (SBDB): the diameter field has taken no NEOWISE result since the 2019 compilation; rotation periods carry no quality grade (2011 AA37's 10 hours is graded unreliable in the lightcurve database); the bulk query rounds the fitted push values to two figures and drops the force law they assume.
- Sizes from brightness: measured sizes have a median 0.71 of the size at reflectivity 0.14, the usual assumption (1,630 objects). The sizes in the plan's Terms already include this. The two small mission targets measured since, 1998 KY26 and Kamoʻoalewa, came out 2–3 times smaller than assumed.
- The orbit fitter (GRSS) is not needed for the prototype. When it is: every `import grss` opens connections, and the first downloads about 4.3 GB and peaks at 7.3 GB of memory. Fit position-and-velocity states, fit both pushes jointly, never rescale its error bars from residuals, and clear JPL's own push values before a "gravity-only" fit.
- The literature service (SsODNet) works per object at about one request a second, about two hours for the list; its bulk file failed on two days. Cards for 7,058 reachable asteroids are on disk (`data/sources/ssodnet/cards`, fetched 2026-11-25, plus the research snapshot); SsODNet does not know 173. An object it does not know returns 404, which is "not checked".
- Rotation periods: Pravec's table (`data/sources/pravec/`) holds periods for 35 reachable asteroids that JPL, the lightcurve database and the 1,704 literature records lack, four of them under 5 km/s. One of those turns in 2.35 hours, so the plan's "every measured period under 5 km/s is faster than 2.2 hours" no longer holds.
- Temporary folders outside the repository are cleared by a reboot; three first-round research reports were cut short that way. Write anything worth keeping under `data/` or into the repository.
