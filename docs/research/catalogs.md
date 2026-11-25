# Catalog inventory: public physical-property sources for NEAs, and how many mission-accessible objects each one reaches

Researcher brief: existing public catalogs and compilations. Date of all live checks: 2026-11-20.
Status tags: **[V]** verified today (I read the source or ran the query in this session), **[R]** recalled from memory, **[U]** uncertain.

## 1. Bottom line

1. **The accessible population is almost uncharacterized, and that is now measured, not assumed.** NHATS (default constraints) lists 7,226 objects today; 286 have minimum round-trip delta-v under 5 km/s and 726 under 6 km/s. Across every source I could cross-match, the number of objects with *any* composition-relevant measurement (taxonomy, colours, albedo, density or mass, thermal inertia, radar polarization ratio, phase function) is:
   - **14 of 286** (4.9%) for delta-v < 5 km/s (exact count),
   - **37 of 726** (5.1%) for delta-v < 6 km/s (exact count),
   - **about 455 of 7,226** (6.3%; roughly 390 to 540) for all of NHATS (726 exact plus a 1,758-object random sample of the other 6,500; 360 is an exact lower bound from catalog tables alone).
   - Taxonomic class specifically: 9 of 286, 24 of 726, about 294 (240 to 361) of 7,226.
2. **SsODNet already does most of the literature fusion.** Its per-object ssoCard carries best-estimate taxonomy, albedo, diameter, colours, spin, density, thermal inertia, radar polarization ratio, phase function, Yarkovsky drift, delta-v and source-region probabilities, each with a bibliographic reference. It already ingests 2026 papers (Alarcon+2026 spins) and published SRP and Yarkovsky densities. The project should build on it, not re-do it.
3. **What SsODNet lacks** is where the project can add something: it returns a single best class instead of a probability; it misses most of the Spitzer NEO final dataset and the RATIR 2024 colours; it has fewer non-gravitational detections than JPL SBDB for the small objects (7 versus 23 objects with A2 among delta-v < 6); its source-region prior exists only for H < 25, which is a quarter of NHATS; it lags about two months; it has no explicit licence; and it holds no raw spectra.
4. **Gaia DR3 is irrelevant for NHATS.** 8 of 7,226 NHATS objects are in `gaiadr3.sso_source`, 3 have a reflectance spectrum (Anteros, Ryugu, 163000), none under 6 km/s. For all NEAs: 445 in `sso_source`, 104 with spectra.
5. **JPL SBDB has no taxonomy for any NHATS object under 6 km/s** (0 of 726), which confirms the project premise for SBDB. SsODNet has 24 for the same set, so the premise is true of SBDB and false of the literature.
6. **The dedicated survey (MANOS) reached 96 of today's NHATS objects** with published spectra (Devogèle+2019), 12 of them under 6 km/s and 4 under 5 km/s. Its "mission accessible" cut is not the NHATS low delta-v cut.

## 2. Live checks

### 2.1 NHATS list

`https://ssd-api.jpl.nasa.gov/nhats.api`, API version 1.3, default constraints (delta-v ≤ 12 km/s, duration ≤ 450 d, stay ≥ 8 d, launch 2020 to 2045). **[V]**

| Quantity | Value |
|---|---|
| Objects | 7,226 |
| min delta-v < 4 / 4.5 / 5 / 5.5 / 6 / 7 / 8 / 10 km/s | 40 / 132 / 286 / 490 / 726 / 1,388 / 2,196 / 4,353 |
| Numbered objects | 200 |
| H range, median | 15.7 to 34.1, median 26.2 |
| H < 22 / < 24 / < 25 | 199 / 834 / 1,789 (so 5,431, or 75%, have H ≥ 25) |
| Median NHATS size range | 10 m to 45 m |
| Orbit condition code 7 or 8 | 3,067 (42%) |

### 2.2 Coverage table

Columns: all NHATS (7,226), NHATS delta-v < 6 km/s (726), NHATS delta-v < 5 km/s (286), all NEAs (43,151 asteroids in the JPL SBDB `neo` group today).

Exact counts are full cross-matches. SsODNet rows for "all NHATS" and "all NEAs" are estimates with 95% Wilson intervals: SsODNet's bulk table could not be downloaded today (section 2.4), so I fetched ssoCards one by one for all 726 objects under 6 km/s, a seeded random sample of 1,758 of the other 6,500 NHATS objects, and a seeded random sample of 600 of all NEAs.

| Channel | Source | All NHATS | dv < 6 | dv < 5 | All NEAs |
|---|---|---|---|---|---|
| **Taxonomy** | SsODNet ssoCard | ~294 (240–361) | 24 | 9 | ~2,950 (2,190–3,940) |
| | JPL SBDB (`spec_B`/`spec_T`) | 23 | 0 | 0 | 327 |
| | Mahlke+2022 (VizieR) | 175 | 12 | 3 | 1,165 |
| | Sergeyev+2023 colours/taxonomy (VizieR) | 211 | 12 | 3 | 2,279 |
| | Devogèle+2019 MANOS spectra (VizieR) | 96 | 12 | 4 | 209 |
| | Marsset+2022 MITHNEOS NIR (VizieR) | 34 | 1 | 0 | 417 |
| | Navarro-Meza+2024 RATIR (VizieR) | 24 | 2 | 1 | 211 |
| | ESA NEOCC `.phypro` | not run | 13 | 4 | not run |
| **Albedo** | SsODNet | ~122 (88–169) | 7 | 3 | ~1,580 (1,050–2,370) |
| | JPL SBDB | 69 | 2 | 0 | 1,205 |
| | MP3C TAP (v3.2.0) | 79 | 1 | 0 | 1,582 |
| | Spitzer NEO compilation | 112 | 4 | 0 | 2,124 |
| **Diameter (measured)** | SsODNet | ~122 (88–169) | 7 | 3 | ~1,580 (1,050–2,370) |
| | JPL SBDB | 70 | 3 | 1 | 1,247 |
| | MP3C TAP | 94 | 1 | 0 | 1,811 |
| **Rotation period** | SsODNet (`spins`) | ~272 (221–337) | 32 | 14 | ~1,940 (1,340–2,790) |
| | JPL SBDB (`rot_per`) | 306 | 32 | 14 | 2,180 |
| | LCDB (2023-10 release), any quality | 304 | 31 | 13 | 2,174 |
| | LCDB, U ≥ 2 | 273 | 30 | 13 | 1,990 |
| | Thirouin+2018 MANOS photometry | 52 | 9 | 6 | 141 |
| **Colours** | SsODNet | ~239 (190–301) | 17 | 3 | ~3,240 (2,440–4,270) |
| | JPL SBDB (B−V or U−B) | 3 | 0 | 0 | 38 |
| **Gaia DR3** | `gaiadr3.sso_source` | 8 | 0 | 0 | 445 |
| | `gaiadr3.sso_reflectance_spectrum` | 3 | 0 | 0 | 104 |
| **Density / mass** | SsODNet density | ~20 (11–43) | 5 | 4 | ~140 (40–520) |
| | JPL SBDB GM or density | 3 | 0 | 0 | 9 |
| **Non-gravitational** | JPL SBDB A2 | 169 | 23 | 11 | 618 |
| | JPL SBDB A1 | 18 | 12 | 10 | 21 |
| | SsODNet `yarkovsky` | ~96 (67–139) | 7 | 3 | ~1,010 (600–1,670) |
| **Radar** | JPL radar astrometry API | 232 | 25 | 12 | 1,110 |
| | SsODNet circular polarization ratio | ~34 (19–62) | 4 | 2 | ~220 (70–630) |
| **Shape/spin model** | DAMIT | 4 | 0 | 0 | 51 |
| **Source-region probabilities** | SsODNet (`source_regions`) | ~1,624 (1,498–1,758) | 53 | 11 | ~25,300 (23,600–27,000) |
| **Phase function** | SsODNet | ~19 (9–44) | 1 | 1 | ~720 (390–1,310) |
| **Thermal inertia** | SsODNet | ~5 | 1 | 1 | ~70 |
| **ANY composition-relevant** | SsODNet alone | ~411 (346–489) | 34 | 13 | ~4,030 (3,130–5,150) |
| | Union of the non-SsODNet tables above | 360 | 21 | 5 | 4,872 |
| | **Union of everything** | **~455 (≈390–540)** | **37** | **14** | not computed |

Consistency checks between independent routes: SsODNet's sampled rotation-period estimate for NHATS (272) agrees with the exact LCDB and SBDB counts (304, 306); its sampled all-NEA albedo estimate (1,580) agrees with the exact MP3C count (1,582). So the sampled estimates are trustworthy to the stated intervals.

All of this was measured against ssoCards stamped `2026-09-14`. Objects discovered since then return HTTP 404 from SsODNet: 13 of the 726 objects under 6 km/s and 44 of the 1,758 sampled.

### 2.3 The 37 objects under 6 km/s with any composition-relevant data

From SsODNet ssoCards plus SBDB non-gravitational flags (list saved as `dv6_union_details.txt`, not kept). First 14 are the full delta-v < 5 set.

| Object | dv (km/s) | H | What exists |
|---|---|---|---|
| 2023 FY3 | 3.41 | 29.0 | S, visible spectrum (de la Fuente Marcos+2024) |
| 2020 CD3 | 3.57 | 31.7 | V, photometry (Fedorets+2020); A1 in SBDB |
| 2024 PT5 | 3.61 | 27.4 | Sv, visible spectrum; density 3,900 ± 2,100 kg/m³ from SRP (Bolin+2025) |
| 2022 NX1 | 3.61 | 28.1 | Xk, visible spectrum |
| 2014 WX202 | 4.26 | 29.6 | Q, spectrum; SDSS-system colours |
| 2014 WU200 | 4.35 | 29.1 | radar diameter 7 m, radar polarization ratio; computed albedo 0.08 |
| 1991 VG | 4.43 | 28.3 | phase function only |
| 2015 KE | 4.46 | 26.2 | S, spectrum; colours |
| 2015 VO142 | 4.49 | 28.9 | S, spectrum; colours |
| 2012 LA | 4.52 | 27.6 | density 460 (+270/−210) kg/m³ from SRP (Micheli+2013) |
| 2017 HU49 | 4.53 | 26.5 | RATIR colours (class probability < 50%), not in SsODNet |
| 2016 RD34 | 4.61 | 27.7 | K, visible spectrum (Devogèle+2019); radar diameter 6 m |
| 2015 TC25 | 4.66 | 29.3 | Xn, NIR spectrum (Sanchez+2024); density 1,100 kg/m³ from SRP (Farnocchia+2017) |
| 2009 BD | 4.73 | 28.1 | density 2,288 (+612/−460) kg/m³, thermal inertia, diameter 4 m (Mommert+2014) |
| 2018 TG6, 2009 UY19, 2011 MD, 2015 BG92, 2016 UE, 2014 YD, 2013 WA44, 2001 QJ142, 2022 RB5, 613862, 2014 JV54, 2015 VO105, 2014 HW, 2016 ND1, 2016 TB57, 2010 NU71, 2017 AR4, 2018 LQ2, 2001 CQ36, 2015 BM510, 2010 RF12, 2014 YN, 2009 CV | 5.0–5.95 | 22.5–28.4 | mostly S/X/Q/M classes from MANOS and MITHNEOS spectra re-classified by Mahlke+2022; 4 thermal albedos; 2011 MD density 747 kg/m³ |

Complex mix of the 24 classified objects under 6 km/s: S 10, X 7, Q 2, M 2, V 1, K 1, U 1. No C-complex object. That is a sample of 24 with strong selection effects, not a population result.

A further 17 objects under 6 km/s have A1 or A2 in SBDB but no composition-relevant measurement of any kind (for example 2006 RH120, 2020 GE, 2020 PP1, 2022 OB5, 2023 YO1, 2025 PN7, 478784). Only 5 objects under 6 km/s have a published SRP or Yarkovsky density in SsODNet. That gap is the immediate target list for the non-gravitational channel.

### 2.4 Access problems found today

| Service | What happened today |
|---|---|
| SsODNet bulk ssoBFT parquet (856 MB, dated 2026-09-22) | Served, but at 0.6 to 9 kB/s; a full download would take about a day. The per-object ssoCard API was fine (about 3 cards/s with 6 workers). |
| CDS VizieR (Strasbourg): `cdsarc.cds.unistra.fr`, `vizier.cds.unistra.fr`, TAPVizieR | "Page unavailable" (404 page) or timeout. The CfA mirror `vizier.cfa.harvard.edu` worked. |
| PDS Small Bodies Node archive `sbnarchive.psi.edu` | HTTP 403, Cloudflare challenge page for scripted requests. The NEOWISE and LCDB PDS bundles cannot be pulled with curl. |
| Lowell `asteroid.lowell.edu` and `astorbdb.lowell.edu/v1/graphql` | HTTP 502. The flat file `ftp.lowell.edu/pub/elgb/astorb.dat.gz` (112 MB, modified today) was available. |
| NEOROCKS at SSDC `neorocks.ssdc.asi.it` | HTTP 503, "Site Under Maintenance". |
| NASA Ames `neoproperties.arc.nasa.gov` | No connection. |
| `smass.mit.edu` | HTTPS times out; plain HTTP works. |
| MP3C TAP | Works, but serves database v3.2.0-beta.1 (2024-02-13) while the web UI is at v3.3.3-beta.1 (2025-10-03). |

A pipeline that depends on any single one of these will break. Mirror what you use.

## 3. Source inventory

### 3.1 Aggregators

**IMCCE SsODNet (ssoCard, datacloud, ssoBFT, quaero) and the `rocks` client**
- Contents: name resolver for about 5.3 million designations; ssoCards for about 1.2 million asteroids; datacloud of about 105 million parameters from over 3,000 articles (Berthier+2023 abstract). **[V]** ssoCard fields seen today: orbital elements, proper elements, delta-v, Tisserand, MOID, source regions, family, pair, Yarkovsky, H/G, diameter, albedo, mass, density, taxonomy (class, complex, technique, wavelength range, scheme), thermal inertia, spins, ellipsoid, YORP, tumbling, colours, phase functions, circular polarization ratio. **[V]**
- Access: `https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/<name>` (JSON, no key); bulk `https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet` (856 MB) and `.ecsv.bz2` (568 MB); datacloud `.../api/datacloud.php?-name=id:<id>&-resource=<table>`. **[V]**
- `rocks`: PyPI `space-rocks` 1.10.6 (2026-10-01), MIT licence, Python ≥ 3.10. **[V]** `classy`: PyPI `space-classy` 0.8.8 (2026-02-05), MIT. **[V]**
- Licence and citation: no licence stated. Requested acknowledgement text plus Berthier et al. 2023, A&A 671, A151, and the original papers. **[V]**
- Cadence: not documented. Every card fetched today was stamped 2026-09-14 and the bulk file 2026-09-22, so the effective lag is about two months. **[V]**
- What feeds it for NEAs (bibliographic references counted in about 3,000 cards fetched today): taxonomy from Mahlke+2022 (64), Sergeyev+2023 (22), Binzel+2019 (11), Mommert+2016, Marsset+2022, Sanchez+2024; colours from Sergeyev+2023 (369), Sergeyev & Carry 2021 (129), Mommert+2016, Lin+2018, Ieva+2018, SkyMapper, MOVIS; diameters by NEATM from NEOWISE papers and Trilling+2010; spins from Alarcon+2026 (18), Thirouin+2016/2018, Beniyama+2022 and LCDB-era papers; Yarkovsky from Fenucci+2024, Liu+2023, Bedini & Tommei 2024, Dziadura+2025; density by methods "SRP" (7) and "Yarkovsky" (5); radar polarization from Virkki+2022 and Zambrano-Marín+2024. **[V]**
- Problems found today:
  - Best albedo is "Computed" (51 of 54 albedos) from best diameter and H, so it inherits H errors and hides multi-solution results. 2009 BD shows albedo 0.635 where the source paper gave two solutions.
  - Of 39 fetched cards for Spitzer-observed NEAs, only 15 carry an albedo: the NEOSurvey and NEOLegacy results are mostly absent.
  - RATIR 2024 colours (Navarro-Meza+2024) are absent.
  - Source regions exist only for H < 25 (largest H with a value: 24.9), reflecting the Granvik model's validity range.
  - Catalog errors pass through: 2010 NU71 (H = 22.7) is given D = 1.13 km and albedo 0.042 from Masiero+2011, which is physically inconsistent with its H and is likely a mis-association.
  - One best class per object, no probabilities, mixed schemes (Bus, Bus-DeMeo, Mahlke, Tholen).

**MP3C (Minor Planet Physical Properties Catalogue, Observatoire de la Côte d'Azur)**
- Web UI v3.3.3-beta.1 (2025-10-03): 1,461,616 bodies, 6,113,272 measured properties, 3,513 sources. **[V]**
- Access: TAP at `https://dachs.oca.eu/tap` (schema `mp3c_main`; tables `best`, `prop_mass`, `prop_diameter`, `prop_albedo`, `prop_h`, `prop_g`, `prop_family`, `prop_proper_elements`, `mpcorb`). TAP exposes no taxonomy, colours or rotation. TAP version is 3.2.0-beta.1 (2024-02-13) with 1,335,502 bodies; best albedo for 145,928, diameter for 147,633, mass for 436. NEAs (q < 1.3): 33,670 known to it, 1,587 albedos, 1,818 diameters, 21 masses. **[V]**
- Licence: none stated; acknowledgement sentence requested. PI Marco Delbo. **[V]**
- Use: an independent cross-check of SsODNet for albedo, diameter, mass. Adds nothing SsODNet lacks for NHATS.

**JPL SBDB**
- `https://ssd-api.jpl.nasa.gov/sbdb_query.api` (bulk) and `sbdb.api` (per object). Today: 43,360 NEOs, 43,151 NEAs. Physical fields filled for NEAs: diameter 1,247, albedo 1,205, rotation 2,180, taxonomy 327 (SMASSII 313, Tholen 37), B−V/U−B 38, GM 5, density 9, extent 11. Non-gravitational: A2 618, A1 21, A3 9. **[V]**
- Strength for this project: the authoritative orbit solution and the non-gravitational parameters, which are far more complete for small objects than SsODNet's.
- Weakness: physical parameters are sparse and old. One value per field, a reference string, no method.
- Fair-use policy: one request at a time, no simultaneous requests; automated clients must send a User-Agent with contact details; the APIs may not be embedded in a website (CORS). **[V]** The website must serve its own snapshot.

**ESA NEOCC physical properties**
- `https://neo.ssa.esa.int/PSDB-portlet/download?file=<desig>.phypro` returns rotation, taxonomy, H, G, albedo, diameter, colours, radar/visual "sightings", each with references. No authentication; the interface is labelled experimental. **[V]**
- The physical data came from Gerhard Hahn's EARN database, which he "kept updated until end of 2018". **[V]** Some later entries exist (it has a class for 2018 LQ2), but it trails SsODNet: for the 726 objects under 6 km/s it has 13 taxonomies against SsODNet's 24, 13 rotation periods against 32, and 4 measured albedos against 7. **[V]**
- NEOCC lists 43,156 NEAs today. Terms: "All rights reserved" plus a Terms & Conditions page I did not read. **[V]**
- Use: orbit files and risk data, and a second opinion on individual objects. It adds no object that SsODNet lacks in the low delta-v set.

**Lowell astorb / astorbDB**
- `astorb.dat.gz` flat file (112 MB, updated today). **[V]** GraphQL endpoint `https://astorbdb.lowell.edu/v1/graphql`, with albedo, colours, taxonomy and lightcurve-derived periods ingested from PDS, LCDB and project compilations (Moskovitz+2022, arXiv:2210.10217). **[V via search]** Service was down (502) today, so I could not count coverage. **[U]**

**NEOROCKS (EU H2020, 2020 to mid-2023) database at ASI-SSDC**
- Project documents through 2023 say the physical-properties database was restricted to consortium partners with public access to follow migration to SSDC. **[V via search]** The SSDC host returned 503 today. Public status unknown. **[U]**
- Published NEOROCKS photometry: colours for 42 small NEOs (Hromakina+2023), 170 objects in the final colour database (A&A 2024). **[V via search]**

**NASA Ames NEO Properties Database**
- Version 2018.5: taxonomy for about 690 NEAs, diameters for about 2,300, plus physical properties of over 900 meteorites. **[V via search]** Unreachable today. The meteorite property tables may matter for the composition-to-density mapping. **[U]**

### 3.2 Taxonomy and spectra

| Source | Contents | NEAs | In NHATS today | Access | Notes |
|---|---|---|---|---|---|
| MITHNEOS, Binzel+2019 | Visible and NIR spectra, more than 1,000 NEOs | >1,000 | not matched directly | `http://smass.mit.edu/minus.html` (HTTP only); spectra declared public domain **[V]** | Icarus 324, 41 |
| MITHNEOS, Marsset+2022 | 491 NIR spectra of 420 NEOs; combined set 976 NEOs | 417 matched | 34 (1 under 6 km/s) **[V]** | VizieR J/AJ/163/165 | CC BY |
| MANOS spectra, Devogèle+2019 | 210 NEOs, visible, mean size about 60 m | 209 | 96 (12 under 6; 4 under 5) **[V]** | VizieR J/AJ/158/196 | 64 of the 96 have H ≥ 25 |
| MANOS photometry, Thirouin+2016, 2018 | 86 and 142 objects with lightcurves | 86; 141 | 32; 52 (9 under 6) **[V]** | VizieR J/AJ/152/163, J/ApJS/239/4; `manos.lowell.edu` has no bulk download | Site summary page lists more targets than are published |
| Mahlke+2022 taxonomy | 2,983 spectra of 2,125 asteroids define the scheme; 4,526 asteroids classified, per-class probabilities | 1,165 | 175 (12 under 6; 3 under 5) **[V]** | VizieR J/A+A/665/A26; `classy` | Uses albedo; resolves X into E/M/P |
| Sergeyev+2023 | SDSS, SkyMapper, Gaia and literature colours; 7,398 rows | 2,277 true NEAs (the rest: 4,378 Mars-crossers, 743 Hungarias) | 211 (12 under 6; 3 under 5) **[V]** | VizieR J/A+A/679/A148 | Gives complex probability; 467 of the 2,279 NEAs are "U"; abstract says 42 mission-accessible classified |
| Navarro-Meza+2024 RATIR | Colours and class probabilities, 323 NEOs observed | 211 with a result | 24 (2 under 6) **[V]** | VizieR J/AJ/167/163 | Not in SsODNet |
| Gaia DR3 reflectance spectra | 60,518 objects, 16 bands 374–1,034 nm | 104 | 3 **[V]** | TAP `https://gea.esac.esa.int/tap-server/tap`, table `gaiadr3.sso_reflectance_spectrum` | All numbered; bright-limited |
| Gaia DR3 classifications | Tinaut-Ruano+2026: 14,042 asteroids, 13 classes (arXiv:2605.06838); Delbo+2026: probabilistic classes for the full sample (arXiv:2602.22816) **[V]** | not stated | at most 3 | papers; no data link in abstracts | Method references, not coverage |
| SDSS, Sergeyev & Carry 2021 | Over 1 million observations of over 300,000 objects, 1,639 NEAs **[V via search]** | 1,639 | via Sergeyev+2023 | VizieR J/A+A/652/A59 | |
| SkyMapper, Sergeyev+2022 | 880,528 observations of 205,515 objects; 117,356 classified **[V via search]** | not stated | via Sergeyev+2023 | VizieR J/A+A/658/A109 | |
| MOVIS (VISTA-VHS), Popescu+2018 | NIR colours for 53,447 objects; 18,265 classified **[V via search]** | few | via SsODNet colours | VizieR J/A+A/617/A12 | |
| Perna+2018 (NEOShield-2) | Visible spectra, 147 NEAs with H ≥ 20 **[V via search]** | 147 | not matched | paper tables | |
| Sanchez+2024 | NIR spectra of 84 small NEOs, photometry of 59 **[V via search]** | 84 | ingested by SsODNet | PSJ 5, 131 | |
| López-Oquendo+2026 (UKIRT) | NIR colours and probabilistic classes for 122 NEOs, 5–150 m, median 60 m (arXiv:2608.28779) **[V]** | 122 | not matched | accepted in PSJ | Debiased population dominated by C/X |
| Ngwane+2026 (Lesedi) | g, r, i classes for 59 NEAs, 22 ≤ H < 29 (PSJ 7, 5) **[V]** | 59 | not matched | paper | X-types about a third |
| DES, Pan-STARRS colours | Main-belt dominated **[R]** | few | negligible | VizieR | Not checked today **[U]** |

### 3.3 Albedo and size

| Source | Contents | NEAs | In NHATS | Access and notes |
|---|---|---|---|---|
| NEOWISE PDS bundle v2.0 (Mainzer+2019) | Diameters, albedos, beaming; cryogenic through reactivation year 3 only **[V]** | not stated on page | via SBDB/SsODNet | `sbnarchive.psi.edu/.../neowise_diameters_albedos_V2_0.zip` (6.5 MB) blocked by Cloudflare for scripts today. DOI 10.26033/18S3-2Z54 |
| NEOWISE later years | Masiero+2020 (years 4–5), Masiero+2021 (years 6–7): 1,415 unique NEOs from reactivation, 1,845 unique NEOs since launch; about 30% diameter uncertainty in reactivation data **[V via search]** | 1,845 | | Paper tables on VizieR. No years 8–11 thermal-fit paper found. Final image/source release was 2024-11-14 at IRSA **[V via search]** |
| Spitzer ExploreNEOs + NEOSurvey + NEOLegacy | Final: 2,204 diameter/albedo estimates for 2,132 objects **[V]** | 2,124 matched | 112 (4 under 6; 0 under 5) **[V]** | `https://github.com/mommermi/spitzerneos` (`spitzerneos.csv`, 889 kB; no licence file; cite Trilling+2010, 2016). Single-band 4.5 μm, assumed beaming: large errors |
| AKARI AcuA | 5,120 asteroids **[V via search]** | handful **[R]** | negligible | JAXA DARTS |
| MP3C best values | see 3.1 | 1,582 albedos | 79 | TAP |

### 3.4 Rotation and shape

| Source | Contents | NEAs | In NHATS | Access and notes |
|---|---|---|---|---|
| LCDB (Warner, Harris, Pravec) | Summary table with 34,755 period rows (31,166 with U ≥ 2) **[V]** | 2,174 | 304 (31 under 6; 13 under 5) **[V]** | `https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip` (40 MB). **Last public release 2023-10-01; file unchanged since.** Cite Warner+2009 with release date |
| Alarcon+2026 (TTT survey) | 249 small NEAs, 156 new fast rotators, 87 under 10 min (arXiv:2602.18562) **[V]** | 249 | already in SsODNet | Shows SsODNet is more current than LCDB |
| DAMIT | 23,702 asteroids, 37,639 models **[V]** | 51 | 4 (Nereus, Apophis, Kamoʻoalewa, 2008 TC3) **[V]** | Table exports at `damit.cuni.cz/projects/damit/exports/table/asteroids`; full export 4.4 GB daily. CC BY 4.0 |
| TESS, ATLAS, ZTF period catalogs | Pál+2020, McNeill+2023, Ďurech+2020 (about 1,800 ATLAS models), Vavilov & Carry 2025 (4,521 periods) **[V via search]** | essentially none | negligible | Main-belt products |

### 3.5 Phase curves

- Mahlke, Carry & Denneau 2021 (ATLAS): 127,012 phase curves of 94,777 asteroids in H,G1,G2; taxonomic complexes separate in G1,G2 but not in H,G12*. VizieR VII/288. **[V via search]**
- Carry+2024 (ZTF, sHG1G2 through the Fink broker): 95,593 objects. **[V via search]**
- Martikainen+2021 used Gaia DR2 photometry, not DR3. **[R]** Oszkiewicz+2011/2012 fitted H,G12 for about half a million Lowell objects; 52% of the unconstrained slopes fell outside the physical range. **[V via search]** Penttilä+2016 gives the constrained fit and per-class G1,G2 values. **[V via search]**
- Reach into NHATS: about 19 objects (9–44) have any phase function in SsODNet. This channel is effectively empty for the target population and the per-object taxonomic information in a phase slope is weak. It can at most adjust H.

### 3.6 Radar

- JPL radar detections page (`https://echo.jpl.nasa.gov/asteroids/alldetections.html`): 1,310 objects, of which 1,149 NEAs, 138 main-belt, 23 comets; last updated 2025-06-02. **[V]**
- JPL radar astrometry API (`sb_radar.api`, v1.1): 4,715 measurements for 1,131 objects (1,110 NEAs), 1968 to 2026-06-27; only 2 measurements of 1 object dated 2026. Returns delay and Doppler only, no SC/OC or radar albedo. **[V]**
- NHATS objects with radar astrometry: 232 (25 under 6 km/s; 12 under 5). **[V]** A radar detection of a 10 m object mostly improves the orbit and sometimes gives a spin and size bound.
- Polarization ratios and radar albedos live in papers: Benner+2008, Virkki+2022 (Arecibo 2017–2019, polarization for 110 NEAs), Rivera-Valentín+2024 (CPR versus taxonomy). **[V via search]** SsODNet carries CPR for about 34 NHATS objects. Arecibo is gone, so this set grows slowly.
- NHATS itself reports predicted radar SNR for future apparitions: 582 objects have a non-null Goldstone or Arecibo SNR field. **[V]**

### 3.7 Densities and binaries

- Carry 2012: 287 density estimates, a third better than 20%. **[V]** Almost all are large main-belt bodies.
- SsODNet density for NEAs: about 140 (40–520) objects, about 20 in NHATS. For the small NHATS objects every density is model-dependent, from SRP or Yarkovsky plus an assumed size and shape: 2009 BD, 2011 MD, 2012 LA, 2015 TC25, 2024 PT5. **[V]**
- Johnston's archive: 656 systems with companions, 113 near-Earth systems; updated 2026-11-13; no licence, copyright notice. **[V]** Binaries are the only direct mass route and none are low delta-v tiny objects.
- Pravec's binary parameters page (`asu.cas.cz/~asteroid/binastdata.htm`) redirects; not read today. **[U]**

### 3.8 Dynamics

- NHATS API v1.3, SBDB API, SBDB Query API, CNEOS close-approach, Sentry and Scout APIs: all under the JPL fair-use policy above. **[V]**
- MPC: REST APIs under `https://data.minorplanetcenter.net/api/` (`get-obs` in ADES, `get-orb` in mpc_orb JSON, designation identifier); documented at `docs.minorplanetcenter.net`. **[V via search]** Bulk `NEA.txt` (8.8 MB, updated today). **[V]**
- SsODNet ssoCards already carry a delta-v and Granvik-type source-region probabilities (ν6, 3:1, 5:2, 2:1, Hungaria, Phocaea, JFC) for H < 25. **[V]**

## 4. Answers to the three closing questions

**Which few sources give most of the coverage?**
1. SsODNet ssoCards: taxonomy, colours, albedo, diameter, density, spin, source regions, with provenance. Covers 34 of the 37 objects under 6 km/s that have any composition data.
2. JPL SBDB and NHATS: orbits, delta-v, A1/A2. SBDB's own physical fields add nothing over SsODNet.
3. Three small supplements that SsODNet misses: the Spitzer NEO CSV (2,132 objects), RATIR 2024 (VizieR J/AJ/167/163), and LCDB for period quality codes.
4. For raw spectra to re-classify: MITHNEOS (SMASS site), MANOS and Mahlke+2022 via VizieR and `classy`.

**Does SsODNet already do the fusion?** Largely yes for literature aggregation and best-value selection. It does not do: class probabilities; calibrated uncertainty on composition; a meteorite or resource mapping; anything for the roughly 94% of NHATS with no data; inclusion of all Spitzer results, RATIR 2024, or JPL's A1/A2 solutions; source regions for H ≥ 25; weekly freshness; an explicit licence.

**Honest number of accessible objects with any composition-relevant measurement:** 14 of 286 (delta-v < 5), 37 of 726 (delta-v < 6), about 455 of 7,226 (all NHATS). With a spectral or photometric class: 9, 24, and about 294. Those few hundred objects are the entire validation set the project can ever have inside NHATS without new observations, and it is biased to larger objects: the Sergeyev+2023 NHATS matches have median H = 23.3 against 26.2 for NHATS as a whole.

## 5. Reasons this part of the project could fail or mislead

- **Ground truth is too thin where it matters.** At delta-v < 5 km/s there are 9 classified objects. No calibration claim can be made for that subset on its own; validation must borrow from larger NEAs and assume the mapping transfers down in size, and small-NEO surveys (MANOS, UKIRT 2026, Lesedi 2026) report a different class mix from large NEAs.
- **Selection bias in the labelled set.** Characterized objects are brighter, larger, higher-albedo and seen at favourable apparitions. A classifier validated on them will look better than it is.
- **Inherited errors.** "Best" albedos are computed from H, and H for H > 25 objects is uncertain by several tenths of a magnitude. Mis-associated thermal detections exist (2010 NU71). Photometric classes have large error: a fifth of the Sergeyev+2023 NEAs are unclassified "U".
- **Mixed taxonomic schemes** (Tholen, Bus, Bus-DeMeo, Mahlke) need an explicit mapping to the project's four classes. Metal-rich (M, Xk, Xe, Xn in different schemes) is the least recoverable without albedo.
- **Model-dependent densities presented as measurements.** All five small-object densities rest on SRP or Yarkovsky plus assumed size and thermal properties.
- **Stale or fragile upstreams.** LCDB frozen since October 2023; NEOCC physical data lost its curator in 2018; PDS NEOWISE table stops at reactivation year 3; six services were down, blocked or throttled today (section 2.4).
- **Licensing is implicit.** SsODNet, MP3C, LCDB, the Spitzer repo and Johnston's archive state no licence. Redistribution of a fused table on a public website needs an attribution scheme at minimum, and ideally a written OK from IMCCE.
- **JPL API terms** forbid simultaneous requests and website embedding.

## 6. Files produced

Paths are relative to `data/research/`, which keeps only `dl/catalogs/nhats.json` and `sbdb_neo.json` from this list.

- `dl/catalogs/nhats.json`, `sbdb_neo.json`, `sb_radar.json`, `gaia_sso_source.csv`, `gaia_sso_refl_objects.csv`, `mp3c_nea_best.csv`, `spitzerneos.csv`, `lcdb/`, `damit/asteroids.csv`, `vizier/*.tsv`
- `dl/catalogs/ssocards/` (2,428 NHATS cards), `dl/catalogs/ssocards_nea/` (random NEA sample), `dl/catalogs/neocc_phypro/` (726 files)
- Results: `dl/catalogs/cov_gaia_sbdb.json`, `cov_ssocard.json`, `cov_union.json`, `cov_lcdb_spitzer.json`, `cov_neocc.json`, `cov_vizier.json`, `dv6_union_details.txt`
- Scripts: `scripts/cat_*.py`

Method notes: designations were matched on number, provisional designation and name through the SBDB NEA list. The SsODNet sample order is seeded (`20261120`) and the sample is the contiguous prefix of the shuffled list, so it is unbiased. "All NEAs" means SBDB `neo` group asteroids (q < 1.3 au). The ESA NEOCC check covered only the 726 objects under 6 km/s.

## Sources

- JPL NHATS API: https://ssd-api.jpl.nasa.gov/nhats.api ; docs https://ssd-api.jpl.nasa.gov/doc/nhats.html
- JPL SBDB Query API: https://ssd-api.jpl.nasa.gov/sbdb_query.api ; API index and fair-use policy https://ssd-api.jpl.nasa.gov/doc/
- JPL radar astrometry API: https://ssd-api.jpl.nasa.gov/sb_radar.api ; docs https://ssd-api.jpl.nasa.gov/doc/sb_radar.html
- JPL radar detections: https://echo.jpl.nasa.gov/asteroids/alldetections.html
- SsODNet: https://ssp.imcce.fr/webservices/ssodnet/ ; ssoBFT https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/ ; ssoCard https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/Bennu ; bulk https://ssp.imcce.fr/data/ssoBFT-latest_Asteroid.parquet
- Berthier et al. 2023, SsODNet: https://arxiv.org/abs/2209.10697
- rocks: https://github.com/maxmahlke/rocks ; https://pypi.org/project/space-rocks/
- classy: https://github.com/maxmahlke/classy ; https://classy.readthedocs.io/en/latest/
- MP3C: https://mp3c.oca.eu/ ; TAP docs https://mp3c.oca.eu/doc/tap/ ; endpoint https://dachs.oca.eu/tap
- ESA NEOCC automated access: https://neo.ssa.esa.int/computer-access ; search page with EARN note https://neo.ssa.esa.int/search-for-asteroids
- Gaia archive TAP: https://gea.esac.esa.int/tap-server/tap
- Tinaut-Ruano et al. 2026, Gaia DR3 taxonomy of 14,042 asteroids: https://arxiv.org/abs/2605.06838
- Delbo et al. 2026, Gaia DR3 supervised classification: https://arxiv.org/abs/2602.22816
- Sergeyev et al. 2023, planet-crossing asteroids: https://arxiv.org/abs/2309.03555 ; VizieR J/A+A/679/A148
- Sergeyev & Carry 2021, SDSS: https://arxiv.org/abs/2108.05749
- Sergeyev et al. 2022, SkyMapper: https://arxiv.org/abs/2110.11656
- Popescu et al. 2018, MOVIS taxonomy: https://arxiv.org/abs/1807.00713
- Mahlke, Carry & Mattei 2022, taxonomy: https://arxiv.org/abs/2203.11229 ; VizieR J/A+A/665/A26
- Binzel et al. 2019, MITHNEOS: https://arxiv.org/abs/2004.05090 ; data http://smass.mit.edu/minus.html
- Marsset et al. 2022, MITHNEOS debiased: https://arxiv.org/abs/2202.13796 ; VizieR J/AJ/163/165
- Devogèle et al. 2019, MANOS spectroscopy: https://arxiv.org/abs/1909.04788 ; VizieR J/AJ/158/196
- Thirouin et al. 2016 and 2018, MANOS photometry: https://arxiv.org/abs/1607.03517 ; https://arxiv.org/abs/1809.03549 ; MANOS site https://manos.lowell.edu/
- Navarro-Meza et al. 2024, RATIR: VizieR J/AJ/167/163 via https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J/AJ/167/163
- Perna et al. 2018: https://arxiv.org/abs/1803.08953
- Sanchez et al. 2024: https://arxiv.org/abs/2404.18263
- López-Oquendo et al. 2026: https://arxiv.org/abs/2608.28779
- Ngwane et al. 2026: https://experts.nau.edu/en/publications/taxonomic-distribution-of-the-small-near-earth-asteroid-populatio/
- Alarcon et al. 2026: https://arxiv.org/abs/2602.18562
- Hromakina et al. 2023, NEOROCKS: https://arxiv.org/abs/2302.01165 ; NEOROCKS site https://www.neorocks.eu/ ; SSDC host https://neorocks.ssdc.asi.it/
- NEOWISE PDS bundle: https://sbn.psi.edu/pds/resource/neowisediam.html
- Masiero et al. 2021, NEOWISE years 6–7: https://arxiv.org/abs/2107.07481
- NEOWISE final data release at IRSA: https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/
- Spitzer NEOs: http://nearearthobjects.nau.edu/spitzerneos.html ; https://github.com/mommermi/spitzerneos ; Trilling et al. 2016 https://arxiv.org/abs/1608.03673
- AKARI AcuA: https://darts.isas.jaxa.jp/astro/akari/data/AKARI-IRC_Catalogue_AllSky_AcuA_1.0.html
- LCDB: https://minplanobs.org/mpinfo/php/lcdb.php ; https://minplanobs.org/MPInfo/datazips/LCLIST_PUB_CURRENT.zip
- DAMIT: https://damit.cuni.cz/ ; exports https://damit.cuni.cz/projects/damit/exports
- Mahlke, Carry & Denneau 2021, ATLAS phase curves: https://arxiv.org/abs/2009.05129
- Carry et al. 2024, sHG1G2 on ZTF: https://arxiv.org/abs/2403.20179
- Oszkiewicz et al. 2012: https://arxiv.org/abs/1202.2270
- Rivera-Valentín et al. 2024, radar CPR: https://ui.adsabs.harvard.edu/abs/2024PSJ.....5..232R
- Carry 2012, Density of asteroids: https://arxiv.org/abs/1203.4336
- Johnston's archive: https://www.johnstonsarchive.net/astro/asteroidmoons.html
- Lowell astorb: https://asteroid.lowell.edu/docs/graphql ; https://ftp.lowell.edu/pub/elgb/astorb.html ; Moskovitz et al. 2022 https://arxiv.org/abs/2210.10217
- NASA Ames NEO properties: https://neoproperties.arc.nasa.gov/home/index
- MPC APIs: https://docs.minorplanetcenter.net/mpc-ops-docs/apis/ ; https://www.minorplanetcenter.net/iau/MPCORB/NEA.txt
