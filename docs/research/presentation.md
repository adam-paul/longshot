# Presentation, publication and credibility: research report

Researcher area: how to publish the NEA prospect catalog as an interactive website and as a credible scientific product.
Date of research: 2026-11-20. Status tags used below: **[V]** verified today (source read or measured in this session), **[R]** recalled from memory and not checked, **[U]** uncertain or could not be verified.

## 0. Bottom line

1. The data product is tiny by web standards. I measured it: JPL SBDB returns 43,151 NEAs today; 33 fields per object is 10.6 MB of JSON, 2.3 MB gzipped; the eight numbers needed to draw every object are 1.38 MB as float32 **[V]**. Any database engine shipped to the browser would be larger than the data (DuckDB-WASM is 35.9 MB, 6.2 MB compressed) **[V]**.
2. The incumbents are either orreries with no science per object (NASA Eyes, Rubin Orbitviewer, JPL and ESA orbit viewers) or tables of measured values with no inference (SsODNet, MP3C, NHATS). The only two "mining target" sites, Asterank and ECOCEL, are both stale: Asterank's data is frozen around 2016 and prices Ryugu at $82.76 billion with no uncertainty; ECOCEL's domain serves an empty shell **[V]**. No site shows a per-object probability with its evidence trail and a public test against known answers. That is the gap.
3. The least code that still feels alive is a fully static site: one generator binary writes HTML, per-object JSON and one compact data file; a few hundred lines of plain JS do the filtering and plotting. "Alive" comes from data that changes on a schedule, time-dependent views (what is observable now), instant response, and visible diffs between versions. None of these needs a server.
4. A 3D orrery should not be the home page. Every reviewed orrery of tens of thousands of objects is a hairball that says nothing about any one object. If one is wanted later, WebGL2 points with Kepler propagation in the vertex shader is a solved problem (spacekit does it) **[V]**.
5. Credibility will not come from the website. The hard gates are: an arXiv endorser (since 21 January 2026 an institutional email is no longer enough; an unaffiliated first-time author needs a personal endorsement) **[V]**; a named human expert reviewer; and prospective predictions time-stamped before the truth arrives. The cheapest formal first step is a Research Note of the AAS (free, 1,500 words, null results explicitly in scope) plus a Zenodo DOI **[V]**. The next expert venue with an open deadline is the Planetary Defense Conference, 3-7 May 2027 in Montreal, abstracts due 20 December 2026, with a "NEO Characterization" session **[V]**.
6. Two licence facts constrain the design. JPL's API terms say "You may not embed these APIs in your website (per NASA CORS policy)" and "only one API request at a time", so the site must ship its own snapshot **[V]**. Gaia data are CC BY-NC 3.0 IGO and commercial use needs ESA authorisation **[V]**, which matters for a catalog framed as "prospecting".

---

## a) Landscape

### Solar-system and catalog sites

| Site | What it is | What works | What does not | Tech and status |
|---|---|---|---|---|
| **Asterank** (asterank.com) | "A scientific and economic database of over 600,000 asteroids"; table with Value ($), Est. Profit ($), delta-v, plus a 3D view and an API. Acquired by Planetary Resources in May 2013 **[V]** | The home page is the table. One sortable number per object is an instant hook. An open JSON API. Honest "About" text: "Scientists know very little about the composition of asteroids" | False precision: the API today returns Ryugu price $82,756,156,358 and profit $30,080,459,216, no uncertainty **[V]**. Value is "mass x spectral type x market price"; mining cost is "a flat percentage of potential value" **[V]**. Only 313 of 43,151 NEAs have an SBDB spectral class today, so most rows have no basis **[V]**. Data frozen: the Ryugu record carries last_obs 2016-08-09 **[V]** | Flask + MongoDB + Redis; 3D view on three.js r58 and jQuery 1.8.3 **[V]**. Repo last pushed 2023-05-01 **[V]** |
| **spacekit.js** (typpo/spacekit) | MIT JS library for 3D space visualisations by the Asterank author | `KeplerParticles` solves Kepler's equation per point in the vertex shader (attributes a, e, i, om, wBar, M; iterative loop) **[V]**. Cheapest route to a correct orrery | Pulls in three.js r186 (three.module.js 659 KB + three.core.js 1.47 MB uncompressed) **[V]**; README says "the API might change" | Requires WebGL 2; 585 stars; last pushed 2026-10-12, so maintained **[V]** |
| **NASA Eyes on Asteroids** | 3D app for 42,580 NEOs, missions and close approaches | Time scrubber. Since the 30 Sept 2026 release a "Watch" button jumps to an object's closest approach or (new "Impact" tab) its past impact, e.g. 2022 EB5 **[V]**. "Learn" slide stories. Events, not objects, are the entry points | No composition, no uncertainty, nothing filterable by science, no data export. "The time range ... only goes ten years into the future" **[V]**. Heavy: app.js 1.63 MB + vendors.js 1.93 MB **[V]** | Custom JS engine; updated twice daily from CNEOS per 2021 press **[R]** |
| **Rubin Orbitviewer** (orbitviewer.app) | Outreach app launched 7 July 2025; categories, filters, time slider 1900-2100, live "discovery counter" **[V]** | Four quality tiers from 16,000 objects (mobile) to 1,000,000 (desktop) **[V]**: proof that 40,000 points is a trivial load. The discovery counter makes the site feel alive. Mobile-first | Population view only; no per-object science; no downloads; page is `noindex` **[V]** | By Fil Studio (Barcelona). v2 client is Eleventy + esbuild + three.js 0.174, i.e. a static site; a rewrite on Next.js 16 + react-three-fiber was pushed 2026-11-09 **[V]** |
| **JPL SBDB orbit viewer** | Per-object orbit diagram embedded in SBDB | Honest disclaimer: "implemented using two-body methods" and "should not be used" for long-term trajectories or encounters **[V]** | Geometry only | jQuery/Angular page shell **[V]** |
| **JPL NHATS table** (cneos.jpl.nasa.gov/nhats) | The accessible-target list this project builds on: 7,226 objects today **[V]** | Filters for delta-v, duration, stay, launch window, H, OCC. Already has "Next Optical Opportunity (yyyy-mm [Vp])" and Goldstone radar SNR columns. CSV and API (fields obs_start, obs_end, obs_mag, n_via_traj) **[V]** | No composition at all; size given only as an albedo range 0.03-0.60 | Says it "should not be interpreted as a complete list of viable NEAs" **[V]** |
| **ESA NEOCC + NEO Toolkit** | Search portal plus five tools: Orbit Visualisation, Flyby Visualisation, Sky Chart, Observation Planning, Synodic Orbit Visualisation **[V]** | The synodic (Earth-rotating frame) view is the right frame for accessibility and observability. Observation planning with precise ephemerides | Fragmented across tools on a separate host; expert-only. Physical-properties data credited to EARN, "updated until end of 2018" **[V]** | neotools.neo.s2p.esa.int is a JS shell **[V]** |
| **IMCCE SsODNet** | Name resolver, dataCloud, ssoCard (best estimates per object), ssoBFT (one broad flat table) **[V]** | Every value traces to a bibliographic source. ssoCard is a per-object JSON document: prior art for the agent-facing side. `rocks` CLI | No official web front end ("A personal Web interface can easily be developed") **[V]**. No inference for unmeasured objects | Asks for an acknowledgement sentence and Berthier et al. 2023 citation **[V]** |
| **MP3C** (mp3c.oca.eu) | Front end for much of the same data: 1,461,616 bodies, 6,113,272 measured properties, 3,513 bibliographic sources **[V]** | "ID card" with best estimates; all measurements with references; XY plots, histograms, TAP | Forms and tables; measured values only | Asks for acknowledgement **[V]** |
| **meteoriteorbits.info** | Curated list: "As of September 22nd, 2026 ... there are 61 meteorites with photographic orbits" **[V]** | A dated "as of" sentence at the top. Every row cited with DOI. Superseded orbits flagged. Proof that a one-table site can be the reference for a niche | Manual upkeep; no API seen | WordPress 7.1.4 + TablePress/DataTables **[V]** |
| **ESASky** | All-sky archive viewer with solar-system object search **[R]** | (not assessed) | Down today: "Temporary Unavailability of ESASky" **[V]** | Large live service |
| **Asteroid Institute ADAM** (b612.ai) | Precovery, Data Explorer, Impact Probability, Trajectory Optimizer ("interactive porkchop plots and Lambert solutions"), Ephemeris; also "Data Provenance" and "Data Packages" **[V]** | Compute on demand; open-source core (adam-core, THOR). Porkchop plots already exist here | Account or API key needed; no composition | Runs on Google Cloud **[R, from B612 posts]** |
| **MPC Explorer** | Object explorer inside the MPC site | (could not read: it loads in an iframe) **[U]** | | |
| **NEOfixer** (Catalina) | Follow-up targeting broker. Priority = Importance x Confidence x Benefit x Urgency / Cost, rescaled 0 to about 10 **[V]** | A transparent multi-factor score with a published formula; API without an account | Planetary defence, not resources | |
| **ECOCEL** (ISAE-SUPAERO; Kovalenko et al. 2022, doi 10.1016/j.pss.2022.105463) | The closest prior art: an asteroid-mining target database with trajectories to 2050 and composition for the 326 spectrally classified NEAs **[V via Universe Today]** | Joined mission design and composition in one place | Universe Today (2023): "does not appear to be online". Today the domain returns a 3.2 KB page titled "ECOCEL" with no content **[V]**; function unknown **[U]** | A hosted app that died within about a year of its paper |
| **MANOS** (manos.lowell.edu) | Characterisation survey of mission-accessible NEOs since 2013 | Target summary pages | Has a login link; data access unclear **[V]** | |

What the landscape says:

- Nobody shows a probability. Sites either show measured values (and blanks for the 99% without them) or invent a point value.
- Nobody shows how they know. SsODNet and MP3C cite sources per value, but no site shows evidence combining into a conclusion.
- Nobody shows how often they are right.
- Orreries are the default and are decorative. The useful ideas in them are the time scrubber, "jump to event" buttons, and the synodic frame.
- Hosted apps die. ECOCEL is gone, Asterank is frozen, ESASky was down today. The survivors are static tables (meteoriteorbits.info) and agency-funded services.

### Explorable explanations as models for explaining the method

- **Bartosz Ciechanowski, "Moon"** (17 Dec 2024). Prose with dozens of inline figures; each idea is shown first as a toy, then as the real thing; sliders and draggable views; coloured words in the text match coloured elements in the figure. I downloaded the page: two script files only, base.js (34 KB) and moon.js (551 KB), hand-written WebGL shaders plus 2D canvas, no three.js, no framework **[V]**. This is the proof that the owner's "close to the metal" taste and the best explanatory work on the web are the same approach.
- **Distill, "A Visual Exploration of Gaussian Processes"** (Görtler, Kehlbeck, Deussen, 2 April 2019, doi 10.23915/distill.00017). The reader clicks training points and the posterior mean and band update **[V]**. Exactly the interaction needed for "evidence in, posterior moves". It also carries full scholarly apparatus on a web page: DOI, BibTeX block, three public reviews as GitHub issues, CC-BY **[V]**.
- **The Pudding, "The Birthday Paradox Experiment"** (Russell Samora). Asks the reader to guess first, then runs trials with real data, with a staged reveal **[V]**. Model for the "known answers" page: guess, then see the truth.
- **Evidence on what works** (Hohman et al., Distill 2020, "Communicating with Interactive Articles"): details-on-demand reduces load; asking readers to predict before the reveal improves recall; but "only a fraction of readers interact with non-static content", and interactive work is "burdened by rapidly changing web technologies that could break interactive content after just a few years" **[V]**.
- **Link rot seen today**: R2D3's "Visual Introduction to Machine Learning" returns HTTP 522; FiveThirtyEight's "Checking our work" calibration page now redirects to abcnews.com/politics **[V]**. The best public example of a forecaster showing its own calibration no longer exists. Consequence: every key result must be readable with scripts off, and each release should be archived as plain files.

---

## b) What would make it interesting and dynamic

Twelve candidate interactions, each tied to the science. The first six are the ones I would build.

| # | Idea | What the visitor does and sees | Data it needs |
|---|---|---|---|
| 1 | **Prospector's plane** | Scatter of round-trip delta-v (x) against P(water-bearing) or P(metal-rich) (y). Each object is a vertical bar (credible interval), not a dot. Brush to select; the table below filters. Colour by how much the evidence moved the object off its prior. The Pareto front is drawn | NHATS min delta-v, duration, n_via_traj; class posterior with interval; size posterior from H |
| 2 | **Evidence ledger per object** | A waterfall in log-odds: orbit prior, then each channel (colour, albedo, Yarkovsky density bound, phase curve, rotation) pushes the bar left or right, ending at the posterior. Each step links to its measurement and citation. Toggle a channel off and the posterior recomputes | Per-channel likelihood vectors per object (4 classes x up to 6 channels = 24 numbers) if the model factorises; otherwise precomputed leave-one-out posteriors. Provenance per measurement |
| 3 | **Known answers** | Cards for Bennu, Ryugu, Itokawa, Eros, Didymos, Kamoʻoalewa, 2008 TC3, 2024 BX1 and the meteorite falls with orbits (61 listed on meteoriteorbits.info **[V]**). The visitor guesses the class; the page shows what the catalog predicted with the truth withheld, then the truth. Below: a reliability diagram over every object with a measured class | Withheld-truth predictions; truth table with citations; calibration bins and interval coverage |
| 4 | **What would one observation buy?** | A ranked list: "objects where one night of colour photometry changes the answer most, observable in the next 90 days". Sort by expected information gain; filter by magnitude limit and hemisphere | Posteriors; simulated measurement likelihoods; NHATS obs_start, obs_end, obs_mag (already in the API **[V]**) |
| 5 | **The catalog as a diff** | Home page states the version date and what changed: new objects, objects whose probabilities moved by more than a threshold, objects that gained a measurement. Each object page has a sparkline of its posterior across releases | Versioned snapshots; a diff table per release |
| 6 | **Null results as first-class** | A page per channel: how many objects it informed, how many it could not, and the sensitivity curve from injection-recovery. A site-wide toggle greys out every object whose posterior is indistinguishable from its prior | Per-object, per-channel information gain (KL divergence prior to posterior); injection-recovery curves |
| 7 | **Prior explorer** | A map of (a, e, i) coloured by source-region probability and the implied composition prior. Drag a hypothetical orbit and watch the prior change. Overlay the NEAs with measured classes to see where the prior is right and wrong | Source-region model on a grid; class mix per source; measured classes |
| 8 | **Synodic accessibility view** | Earth-fixed rotating frame, 7,226 objects, showing when each returns and its launch windows. Replaces the heliocentric hairball | Orbital elements; NHATS trajectory windows |
| 9 | **Set your own assumptions** | Sliders for water fraction per class and for prior weights; the ranking re-sorts live and a stability indicator shows how much of the top 50 survives | Class posteriors only; all arithmetic client-side |
| 10 | **Population answer with draws** | "How many accessible, water-bearing NEAs larger than 10 m exist?" shown as a distribution; a button resamples one plausible world at a time (hypothetical outcome plot) | Class probabilities and size posteriors, or a few dozen posterior draws per object |
| 11 | **Review trail** | Each claim links to the fresh-agent adversarial review and how it was resolved; a "disputes and corrections" page | Review logs kept as files in the repo |
| 12 | **Cite this object** | Each object page has a citation block (catalog version, DOI, date) and a link to the same record as JSON | Version manifest; DOI |

Notes on overlap:

- "Next observable apparition" on its own is not new: NHATS already publishes it. The new thing is ranking by information gain (idea 4).
- Launch-window porkchop plots exist at NHATS and at ADAM's Trajectory Optimizer. Link to them; do not rebuild.
- Idea 2 depends on the science plan. If the inference is a factorised model, the browser can recompute posteriors from 24 numbers. If it is not, the pipeline must precompute leave-one-out results. This should be decided with the modelling researcher.

---

## c) Technical options

### Measured sizes (this session)

| Item | Size |
|---|---|
| SBDB NEA table, 43,151 rows x 33 fields, JSON | 10.6 MB raw, 2.3 MB gzip **[V]** |
| Eight float32 columns (a, e, i, om, w, ma, epoch, H) for all NEAs | 1.38 MB raw, 0.97 MB gzip **[V]** |
| 36 float32 columns for all NEAs (a plausible full catalog) | 6.2 MB raw (computed) |
| DuckDB-WASM 1.33.1 `duckdb-eh.wasm` | 35.9 MB raw, 6.22 MB brotli from jsDelivr, plus 0.77 MB worker JS **[V]** |
| SQLite WASM 3.54.1 `sqlite3.wasm` | 879 KB raw, 353 KB brotli, plus 657 KB JS **[V]** |
| three.js 0.187 `three.module.js` + `three.core.js` | 659 KB + 1.47 MB uncompressed **[V]** |
| hyparquet 1.33.1 (pure-JS Parquet reader) | 207 KB of source JS **[V]** |

Plain-JS speed on this machine (Ryzen 9 9950X, Node 24): propagating all 43,151 Kepler orbits takes 6.1 ms per frame (5 Newton iterations, precomputed orientation vectors) or 10.8 ms unoptimised; brute-force nearest-point picking over all of them takes 0.06 ms **[V]**. A phone is perhaps 5 to 10 times slower **[R]**. So: for the 7,226 accessible objects no GPU work is needed at all; for an animated view of all 43,151 on a phone, vertex-shader propagation is the right tool.

### The five options

| Option | Fit for this data size | Moving parts | Verdict |
|---|---|---|---|
| **1. Fully static; one compact data file; plain JS (WASM optional)** | Whole catalog loads in one request of 1 to 3 MB; filter and sort over 43k rows in typed arrays is sub-millisecond | Generator binary, static host | **Best fit.** Fewest parts. Survives neglect. Also serves agents (files are the API) |
| **2. DuckDB-WASM or SQLite-WASM over static files** | The engine is larger than the data (6.2 MB compressed vs about 2 MB). Cold start and worker plumbing for no gain on 43k rows | Engine version, COOP/COEP headers for threads, worker glue | **Not as the core.** Reasonable as an optional "SQL console" page, loaded only on visit, pointed at the same Parquet file |
| **3. Small Rust server, server-rendered HTML** | Works well; pages are fast and linkable; matches the owner's other projects | A process to keep alive, a VPS, TLS, deploys, backups | **Only if** something must be computed server-side on request (e.g. re-running the real pipeline with user-supplied observations). Nothing in the current plan needs it. The same binary can gain a `serve` subcommand later |
| **4. Rust compiled to WASM for the renderer** | Overkill. A WebGL2 point renderer is about 300 lines of JS and GLSL; wgpu-based WASM bundles are megabytes (one framework reports 6 to 8 MB before stripping **[U, third-party]**) | wasm-bindgen toolchain, two languages in the browser | **No**, unless the inference itself (idea 2 or 9) grows into real numerical code that should be shared with the pipeline |
| **5. Framework (SvelteKit, Astro, Observable Framework)** | Fine technically; Observable Framework is the nearest to this use (static site, data loaders in any language), ISC licence, repo last updated April 2026 **[V via search]** | Node toolchain, dependency churn, build step. Rubin's Orbitviewer has already been rewritten once (Eleventy to Next.js) **[V]** | **Fallback**, consistent with the owner's stated preference. Astro would be my pick if a framework were forced, since it ships no JS by default **[R]** |

### Rendering 40,000 points or orbits

- **WebGL2 is the baseline**: 97.29% global support on caniuse today **[V]**.
- **WebGPU is not needed and not safe yet**: 86.83% full + 1.8% partial; caniuse lists every Firefox version through 163 as "disabled by default" and desktop Safari 26 to 27 as partial **[V]**. web.dev reports Firefox shipped it on Windows (141) and Apple Silicon macOS, but not Linux **[V via search]**. At 40,000 points WebGPU buys nothing.
- **Kepler propagation in the vertex shader**: upload elements once as vertex attributes, pass time as one uniform, solve Kepler's equation with a fixed iteration count per vertex. spacekit's shader is the reference **[V]**. Cost is about 40 lines of GLSL.
- **Picking**: do it on the CPU. Brute force over 43k projected points is 0.06 ms **[V]**. No colour-ID framebuffer needed.
- **Orbits as lines**: 40,000 ellipses at 64 segments is 2.6 million vertices; the GPU can draw it, the eye cannot read it. Draw the selected object's orbit and a few neighbours.
- **2D plots** (ideas 1, 3, 7): Canvas 2D handles 43k marks; no library needed. SVG for anything under about 2,000 marks so it stays inspectable and accessible.

### Hosting

| Host | Limits that matter | Cost |
|---|---|---|
| **Cloudflare Pages** (or Workers static assets, same limits) | Free: 500 builds/month, 20,000 files per site, 25 MiB per file, 100 custom domains per project. Paid: 100,000 files **[V]** | $0 + domain |
| **GitHub Pages** | 1 GB site, 100 GB/month soft bandwidth, 10 builds/hour soft; "not intended for ... a free web-hosting service to run your online business" **[V]** | $0 + domain |
| **Cloudflare R2** (for raw snapshots and large files) | Free: 10 GB storage, 1M class A and 10M class B operations per month; egress free **[V]** | $0 at this scale |
| **VPS** | Needed only for option 3 | about $5/month **[R]** |

A trap: one JSON file and one HTML file for each of 43,151 objects is 86,302 files, over the 20,000-file free limit on Cloudflare. Per-object files for the 7,226 NHATS objects fit (14,452 files). For the rest, either shard (256 JSON shards keyed by designation hash), render the object page client-side from the main data file, or put per-object files in R2. Domain cost is about $10 to $15 per year **[R]**.

### Which is least code and still alive

Option 1, with the generator as the "single binary": `prospect build` reads the pipeline's output and writes `dist/`. Hand-written HTML, CSS and JS modules; no bundler; no Node toolchain. Whether the generator is Rust or the pipeline's own language (probably Python through uv for the astronomy libraries) is a detail to settle with the science plan: fewest parts means the pipeline that computes the catalog also emits the site.

---

## d) The agent-facing side

Yes, publish for machines, and the minimal form is files, not a service.

1. **One versioned data file with a schema.** `catalog-2026.11.20.parquet` and the same as `csv.gz`. Parquet is read by pandas, polars, DuckDB, astropy and TOPCAT **[R]**. A `schema.json` gives each column's name, unit, meaning, and which channel produced it.
2. **A manifest.** `latest.json`: version, date, method version, sha256 of each file, row count, DOI, licence, schema URL. Agents fetch this first.
3. **Per-object JSON** at a stable URL, the same document the object page renders from. SsODNet's ssoCard is the precedent **[V]**.
4. **`llms.txt`**: a 20-line plain-text map of the above. Expect little: Ahrefs found 97% of llms.txt files on 137,210 sites got zero requests in May 2026; among AI bots GPTBot fetched most and Claude-Code second **[V]**. Coding agents are the audience here, so it is worth 20 lines and no more.
5. **Open CORS** (`Access-Control-Allow-Origin: *`) on the data paths, so other sites and browser-based agents can read them. Note the contrast with JPL, which forbids embedding its APIs **[V]**.
6. **schema.org `Dataset` JSON-LD** in the page head for dataset search engines **[R]**.

Not in version 1: an MCP server. Static files already give an agent everything, with no process to run. If one is wanted later, the minimal form is a small stdio MCP in the repo that reads the local Parquet file; nothing hosted. A VO TAP service is likewise out of scope; the route into the astronomers' ecosystem is VizieR, which requires that the data relate to a refereed publication **[V via search]**.

---

## e) Scientific publication and credibility

### Archive and repository

- **Zenodo**: registers a DOI for each published record; each new version is "a completely new record with separate metadata, files and persistent identifier"; limit 50 GB and 100 files per record; free **[V]**. GitHub integration: "Zenodo archives your repository and issues a new DOI each time you create a new GitHub release" **[V]**. A concept DOI that always resolves to the latest version exists **[R]**.
- **Suggested repository layout** (one public repo):
  - `pipeline/` the code that fetches, snapshots, infers, validates
  - `prereg/` dated, tagged files stating thresholds and predictions before each run
  - `snapshots/` manifests only (URL, retrieval time, sha256, byte count); raw files live in R2 or Zenodo
  - `validation/` known-answer sets, injection-recovery results, calibration outputs
  - `reviews/` adversarial review transcripts and resolutions
  - `site/` hand-written HTML, CSS, JS
  - `CITATION.cff`, `LICENSE` (code), `LICENSE-data`, `CREDITS.md` (upstream acknowledgement strings), `CHANGELOG.md`
- **Open Exoplanet Catalogue** is a good precedent for a git-native catalog: one file per system, "one commit per publication" so `git blame` traces each value to its source, MIT licence, about 1.1k stars **[V]**.

### Venues

| Venue | Rules that matter | Fit |
|---|---|---|
| **arXiv (astro-ph.EP)** | From 21 January 2026 an institutional email is no longer sufficient. New submitters need both an institutional email and prior authorship in the endorsement domain, or a personal endorsement from an established arXiv author in that domain; staff cannot waive it **[V]**. Endorsers must have papers between three months and five years old in the domain **[V]**. Since May 2026, unchecked LLM output (hallucinated references, leftover model comments) earns a one-year ban, then peer review first **[V via search]** | Needed for visibility, but gated. An unaffiliated first-time author must find a human endorser who has seen the work. Every reference must be hand-checked |
| **Research Notes of the AAS** | No charge. 1,500 words, one figure or one table. Moderated, not peer reviewed. Indexed in ADS, citable. Scope names "works in progress, comments and clarifications, null results". Encourages Zenodo for data. No affiliation rule stated **[V]** | Best first formal output: one validated result or one calibrated null, pointing at the Zenodo catalog |
| **Planetary Science Journal** | Open access, CC BY. 2026 charges: $69.51 per text quantum (350 words) and $61.40 per figure or table **[V]**. A 20-quanta, 8-figure paper is about $1,880 (my arithmetic) | The natural home for the full catalog paper, after expert review |
| **AAS policy on AI** | Posted 9 September 2026. "AI cannot be listed as an author". Use must be disclosed, naming the tool and its purpose. "LLMs may not be used to generate any portion of a manuscript unsupervised." It covers the manuscript, "not the data analysis" **[V]** | Compatible with agent-run analysis, provided the human author writes and verifies the paper |
| **JOSS** | No fees. Repository public for more than six months. "There must be evidence that the software is being used for research." "Your paper must not focus on new research results"; a "one-off tool for a single analysis" is out of scope. AI use must be disclosed **[V]** | Not for the catalog. Possible later for a reusable library split out of the pipeline |
| **Icarus** | Elsevier hybrid journal; subscription route without author fee **[R]**; current APC not found **[U]** | Traditional venue; slower |
| **Open Journal of Astrophysics** | arXiv overlay covering anything suited to astro-ph; has a "Use of Generative AI" section; the managing editor reports a large rise in AI-involved submissions. Fee status unclear from what I could read **[U]** | Possible, but sits behind the same arXiv gate |
| **VizieR (CDS)** | Catalog must relate to a refereed paper; needs a standard ReadMe **[V via search]** | After a refereed paper; this is where astronomers will look |

### What claudestronomy and macrogrants ask

- Claudestronomy describes itself as "Grants & community for finding new objects in public sky data", "A $100,000 program from macrogrants" (the macrogrants page says $50,000) **[V]**.
- Its standards, verbatim: "Show that your search can recover known objects in the same data before trusting it to find new ones." "Inject realistic synthetic sources across the parameters you're searching, measure how often you recover them, and calibrate false positives separately." "Write down thresholds and predictions before new data arrives, and document any later changes or bug fixes." "Have a fresh agent session challenge your analysis, and ask people who know the data to look too. Separate agents can share the same mistakes." "Publish code, methods and results so others can reproduce the work." "Publish useful null results too" **[V]**.
- Process: "there is no application form"; email or text a short description; grants "from $500 to $25,000, approved in a day or two"; compute and model credits; a Signal group chat; "if a candidate earns telescope time, we can help you ask for it" **[V]**. No reporting schedule or deliverable format is stated **[V]**.
- Two cautions. The programme is framed around finding new objects (things that move, transit, change, are nearby, or "become interesting across archives"); a characterisation catalog is adjacent, so fit should be asked, not assumed. And macrogrants says it cannot fund "for-profit initiatives" **[V]**.
- The site itself is a single static page of about 24 KB on Vercel **[V]**: the community's own taste is plain.

### How amateur and AI-assisted results are received

- The current reference case is TIC 4206066 (October 2026): a product manager with no astronomy training used Claude Code and Codex on TESS data to flag a planet candidate. What earned it attention was method, not polish: dips recurring across 2018, 2020 and 2025 data; 74 tests aimed at disproof; and predicted transit times posted on Zenodo before TESS re-observed the star (31 October to 26 November 2026). The professional reaction quoted was cautious: "AI tools won't necessarily be helpful in the process of confirming planets" (K. Hardegree-Ullman, NExScI) **[V via Gizmodo]**.
- Citizen-science asteroid work is accepted when it flows through the normal channels: Daily Minor Planet volunteers were recognised by the MPC; amateurs still discover NEAs (F. Romanov, 2026 CQ3) **[V via search]**. One amateur account says some professionals use "amateur" pejoratively and that MPC credit rules make amateur discovery nearly impossible **[V via search; single source]**.
- The background mood is wary. arXiv tightened endorsement because of "a surge of low-quality, non-scientific submissions" **[V]**; Science described astronomy's early experience with AI as "mixed" (June 2026) **[V via search]**.
- What this implies: lead with the test results and the nulls; make no claim per object stronger than the calibration supports; publish predictions for objects about to be measured, time-stamped in advance; and get one named person from the NEO community to review before any preprint.
- A ready-made prospective test: Tianwen-2 reached Kamoʻoalewa in mid-2026 and found it about 20 m across, roughly half the smallest ground-based estimate; it is due to depart in April 2027 with a sample landing that November **[V via search]**. Other scheduled ground truths should be listed by the validation researcher.

### Where to get expert review

- **IAA Planetary Defense Conference**, 3-7 May 2027, McGill University, Montreal. Abstracts of 250 to 500 words; "extended deadline ... December 20, 2026"; notification by 22 January 2027; sessions include "Near-Earth Object (NEO) Characterization" **[V]**.
- **EPSC 2027**, Toulouse, 19-24 September 2027; DPS 2027 is planned for the same week in Providence **[V via search; DPS unconfirmed]**.
- **ACM 2026** was held 6-10 July 2026 in Poznań; the series runs every three years, next in 2029 **[V via search]**.
- **Minor Planet Mailing List** (groups.io): the working list for observers; the MPC still uses it for announcements **[V via MPC newsletter snippets; list activity not checked]**. The right place to ask for a reviewer and to offer the "what to observe next" list.
- **NASA Small Bodies Assessment Group** meetings **[R]**.

### Citation and licence obligations for a derived catalog

| Source | Terms found | Consequence |
|---|---|---|
| **JPL SSD / SBDB / CNEOS** | Cite as "NASA/JPL Solar System Dynamics. Data retrieved on (date)". API: "only one API request at a time"; "You may not embed these APIs in your website (per NASA CORS policy)"; "API data formats can change without notice"; send a User-Agent with contact information **[V]**. JPL material "may be used for any purpose without prior permission"; no implied endorsement; no logos **[V]** | Snapshot at build time; cite with retrieval date; no NASA or JPL branding |
| **MPC** | Standard acknowledgement: "This research has made use of data and/or services provided by the International Astronomical Union's Minor Planet Center" **[V via search]**. The SBN replica licence is for "internal purposes", non-transferable, and "any modifications or derived data products must be explicitly and clearly marked as such if they are redistributed" **[V]** | Do not re-host MPC tables; label derived columns as derived |
| **Gaia** | "Gaia data are distributed under the CC BY-NC 3.0 IGO license." Commercial use, "including any use ... that directly or indirectly generates a financial gain", needs prior authorisation (data.licences@esa.int). Credit "ESA, Gaia DPAC" **[V]** | Keep the project non-commercial, or keep Gaia-derived columns separable. A CC BY catalog cannot simply include raw Gaia values |
| **NEOWISE** | Required acknowledgement paragraph; cite Mainzer et al. 2014 and Wright et al. 2010. Final release 14 November 2024 **[V]** | Add to credits |
| **SsODNet / MP3C** | Acknowledgement sentence plus Berthier et al. 2023; MP3C asks for its own acknowledgement **[V]** | Add to credits; cite the original measurement papers too |
| **LCDB** | "All rights reserved"; cite Warner, Harris, Pravec 2009 with the version date; latest public release 2023 October 1 **[V]** | Use values in inference, cite, but do not redistribute the table |

Practical rule: publish derived quantities (posteriors, bounds, flags) with identifiers and pointers to sources; do not republish upstream tables wholesale. Licence the derived catalog CC BY 4.0 if the Gaia question allows, the code MIT or Apache-2.0, and keep a credits page with the exact acknowledgement strings.

---

## f) Reproducibility and freshness

**Rate of change.** Counting SBDB NEAs by the year in their provisional designation: 2021: 3,122; 2022: 3,226; 2023: 2,916; 2024: 3,124; 2025: 3,244; 2026 to 20 November: 2,555 **[V]**. That is about 60 new objects a week. No Rubin-driven jump is visible in this count yet. NHATS stands at 7,226 **[V]**.

**Pipeline options.**

| Option | What it is | Assessment |
|---|---|---|
| One command plus content-addressed snapshots | `fetch` saves each upstream response under its sha256 and writes a manifest (URL, time, hash, size); `build` reads only from a manifest; `validate` reruns the known-answer and injection tests; `site` writes `dist/`. A Makefile or justfile ties them | **Recommended.** A few hundred lines; no extra tools; a past release can be rebuilt bit-for-bit from its manifest |
| Git scraping | A scheduled job commits the fetched data to git, so history and diffs come free **[V, URL checked]** | Good for the small tables (NHATS is small). The 10 MB SBDB dump weekly is tolerable; raw archives belong in R2 |
| DVC, Snakemake, Nix | Workflow and data-versioning tools **[R]** | More machinery than 43k rows justify |

**Scheduled refresh.** A weekly job (GitHub Actions cron on a public repo, or cron on the owner's machine) runs fetch, build, validate, and deploys only if validation passes. Scheduled refreshes must be deterministic code with no model in the loop. Agents change the method; a method change is a new method version with its own pre-registration file. Because JPL warns formats "can change without notice" **[V]**, the fetch step should check the API `version` field and fail loudly.

**Two version axes.** Data version by date (2026.11.20) and method version by number (1.2). A row is identified by both.

**Showing it on the site.**

- The version and date in the page header of every page, linked to the changelog.
- A "what changed" page per release (idea 5): counts, the objects that moved most, new arrivals.
- Immutable per-version data URLs; `latest.json` as the only moving pointer.
- Per-object history: the posterior at each release.
- A Zenodo DOI for each method release and perhaps quarterly data releases, not for every weekly refresh (Zenodo asks for fair use **[V]**).
- Each release archived as plain files so the site outlives its scripts.

---

## Three directions and a recommendation

### Direction A: The Ledger (static, table-first)

A document-like site. The home page is the prospector's plane above a sortable table of the 7,226 accessible objects, with the version date and "what changed" at the top. Each object has a page with its evidence ledger, sources, history and JSON twin. Separate pages for known answers, nulls and method. No 3D.

- Build: generator binary writes static HTML, per-object JSON, one data file. About 500 to 800 lines of hand-written JS, Canvas 2D and SVG. Cloudflare Pages or GitHub Pages; $0 plus a domain.
- Strength: fewest parts; doubles as the machine interface; hard to break; readable without scripts.
- Weakness: least spectacle. Its interest depends entirely on the science being informative.

### Direction B: The Explorable Paper

A long-form interactive article in the Ciechanowski and Distill manner that teaches the method on the real catalog: one manipulable figure per channel (drag an orbit and watch the prior; add a colour and watch the posterior; see what a Yarkovsky detection excludes), the known-answers test with guess-then-reveal, then the catalog browser. Carries a DOI, a citation block and public reviews.

- Build: the same static data as A, plus four to six bespoke figures, each perhaps 200 to 500 lines.
- Strength: the most distinctive and the most persuasive to experts and public alike; it is the form in which "how we know" becomes the product.
- Weakness: highest craft cost; each figure is hand-made; only worth it once the method is stable.

### Direction C: The Live Instrument

A Rust server with server-rendered pages and SQLite, a query API, and on-demand recomputation (a visitor submits a new observation or changes assumptions and the real pipeline reruns). Optionally a spacekit-style 3D view as the front door.

- Strength: can do things static files cannot.
- Weakness: a process, a VPS, deploys and uptime for a solo owner; nothing in the present plan needs server-side computation; the 3D front door repeats what NASA and Rubin already do better with more money.

### Recommendation

Build A first and treat it as the foundation; write B on top of A's data once the method has passed its known-answer tests; do not build C.

- A is the scientific product and the agent interface at once. It can ship with the first validated release.
- B is how the project earns attention and trust. It should be the front door in phase two, with A as the reference behind it.
- Skip the orrery. If a spatial view is wanted, make it the synodic accessibility view (idea 8) for the selected object and its neighbours, drawn with one small WebGL2 program.
- Stack: generator binary (Rust, or the pipeline's own language if that is fewer parts); hand-written HTML, CSS and JS with no bundler or framework; one compact binary data file for the page plus Parquet and CSV for people and agents; Cloudflare Pages with a custom domain; R2 for raw snapshots; Zenodo for releases.
- In parallel with the build: find a human reviewer and arXiv endorser through MPML or PDC; consider a PDC 2027 abstract (deadline 20 December 2026); plan an RNAAS note as the first formal publication.

---

## Sources

Landscape
- https://www.asterank.com/ , https://www.asterank.com/about , https://www.asterank.com/3d/ , https://www.asterank.com/api
- https://github.com/typpo/asterank , https://api.github.com/repos/typpo/asterank
- https://github.com/typpo/spacekit , https://raw.githubusercontent.com/typpo/spacekit/master/src/shaders.ts
- https://eyes.nasa.gov/apps/asteroids/ , https://science.nasa.gov/blogs/eyes/2026/10/05/nasas-eyes-software-september-release-notes/
- https://orbitviewer.app/ , https://rubinobservatory.org/news/orbitviewer-app-launch , https://github.com/lsst-epo/orbitviewer-client , https://github.com/lsst-epo/orbitviewer-client-v2
- https://ssd.jpl.nasa.gov/tools/orbit_viewer.html
- https://cneos.jpl.nasa.gov/nhats/ , https://ssd-api.jpl.nasa.gov/nhats.api , https://ssd-api.jpl.nasa.gov/doc/nhats.html
- https://neo.ssa.esa.int/neo-toolkit , https://neo.ssa.esa.int/search-for-asteroids?tab=physprops
- https://ssp.imcce.fr/webservices/ssodnet/ , https://mp3c.oca.eu/
- https://www.meteoriteorbits.info/
- https://sky.esa.int/
- https://b612.ai/ , https://b612foundation.org/asteroid-institute-deploys-the-adam-platform-online/
- https://data.minorplanetcenter.net/explorer/
- https://neofixer.arizona.edu/faq/how-does-neofixer-assign-priority
- http://www.ecocel-database.com , https://www.universetoday.com/articles/want-to-be-an-asteroid-miner-theres-a-database-for-that , https://doi.org/10.1016/j.pss.2022.105463
- https://manos.lowell.edu/

Explorable explanations
- https://ciechanow.ski/moon/
- https://distill.pub/2019/visual-exploration-gaussian-processes/
- https://distill.pub/2020/communicating-with-interactive-articles/
- https://pudding.cool/2018/04/birthday-paradox/
- http://www.r2d3.us/visual-intro-to-machine-learning-part-1/ (HTTP 522 today)
- https://projects.fivethirtyeight.com/checking-our-work/ (redirects to abcnews.com/politics today)

Technical
- https://ssd-api.jpl.nasa.gov/sbdb_query.api (NEA table measured today) , https://ssd-api.jpl.nasa.gov/doc/index.php (API terms)
- https://caniuse.com/webgl2 , https://caniuse.com/webgpu , https://web.dev/blog/webgpu-supported-major-browsers
- https://data.jsdelivr.com/v1/packages/npm/@duckdb/duckdb-wasm@1.33.1-dev57.0 , https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@1.33.1-dev57.0/dist/duckdb-eh.wasm
- https://data.jsdelivr.com/v1/packages/npm/@sqlite.org/sqlite-wasm@3.54.1-build1
- https://data.jsdelivr.com/v1/packages/npm/three@0.187.0 , https://registry.npmjs.org/hyparquet/latest
- https://developers.cloudflare.com/pages/platform/limits/ , https://developers.cloudflare.com/workers/platform/limits/ , https://developers.cloudflare.com/r2/pricing/
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://github.com/observablehq/framework
- https://simonwillison.net/2020/Oct/9/git-scraping/ , https://datasette.io/

Agent-facing
- https://ahrefs.com/blog/llmstxt-study/ , https://llmstxt.org/ , https://modelcontextprotocol.io/

Publication and credibility
- https://claudestronomy.com/ , https://macrogrants.com/
- https://info.arxiv.org/help/endorsement.html , https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/ , https://techcrunch.com/2026/05/16/research-repository-arxiv-will-ban-authors-for-a-year-if-they-let-ai-do-all-the-work
- https://journals.aas.org/research-notes/ , https://journals.aas.org/research-note-preparation-guidelines , https://journals.aas.org/article-charges-and-copyright/ , https://journals.aas.org/author-llm-guidelines
- https://joss.readthedocs.io/en/latest/submitting.html , https://blog.joss.theoj.org/2026/01/preparing-joss-for-a-generative-ai-future
- https://astro.theoj.org/for-authors
- https://cdsarc.cds.unistra.fr/vizier.submit/index.html
- https://help.zenodo.org/docs/deposit/about-records/ , https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo , https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content
- https://github.com/OpenExoplanetCatalogue/open_exoplanet_catalogue
- https://gizmodo.com/did-claude-help-an-amateur-astronomer-discover-a-new-planet-2000824393
- https://www.universetoday.com/articles/dedicated-amateur-beats-all-sky-surveys-to-asteroid-discovery , https://science.nasa.gov/science-news/citizenscience/daily-minor-planet-volunteers-earn-nod-from-the-minor-planet-center
- https://iaaspace.org/event/10th-iaa-planetary-defense-conference/
- https://www.europlanet-society.org/?p=29893 (EPSC 2027) , https://www.astro.amu.edu.pl/en/conference-asteroids-comets-meteors-acm-2026-in-poznan/
- https://www.planetary.org/articles/chinas-tianwen-2-mission-has-probably-arrived-at-a-quasi-moon-of-earth , https://skyandtelescope.org/astronomy-news/tianwen-2-arrives-at-quasi-moon-kamo%ca%bboalewa-returns-images/

Licences and citation
- https://ssd.jpl.nasa.gov/about/ , https://www.jpl.nasa.gov/jpl-image-use-policy/
- https://sbnmpc.astro.umd.edu/MPC_database/replication-info.shtml , https://dc.zah.uni-heidelberg.de/mpc/q/pla/howtocite
- https://www.cosmos.esa.int/web/gaia-users/license , https://www.cosmos.esa.int/web/esdc/terms-and-conditions , https://www.cosmos.esa.int/web/gaia-users/credits
- https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/
- https://minplanobs.org/mpinfo/php/lcdb.php

Local measurement scripts (not kept)
- kepler_bench.js
- kepler_bench2.js
