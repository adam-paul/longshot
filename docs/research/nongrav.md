# Non-gravitational accelerations as physical and compositional probes of NEAs

Research brief for the NEA prospect-catalog plan. Written 2026-11-20.

Status marks used below: **[V]** = verified today (source or API read in this session), **[R]** = recalled from memory, not checked today, **[U]** = uncertain, **[C]** = computed today by me from verified inputs (scripts in `data/research/scripts/`; the downloads were not kept).

## 0. What the plan must take from this

1. **The channel is real but narrow.** As of today JPL SBDB has a fitted non-gravitational parameter for 623 NEO asteroids, and only **174 of the 7,226 NHATS objects (2.4%)**, and **16 of the 286 with round-trip Δv < 5 km/s**. 97% of NHATS objects with H ≥ 27 have observed arcs shorter than 60 days, so no astrometric fit can say anything about them. This channel cannot be the backbone of a 7,200-object catalog. It is a high-value layer for roughly 150 to 350 objects. [V][C]
2. **The fits already exist and are public twice over.** JPL (SBDB) and ESA NEOCC (per-object orbit files with area-to-mass ratio and Yarkovsky parameter, plus covariance) both publish them. The gap is not "nobody fitted A1/A2/A3". The gap is that nobody has turned those fits into calibrated per-object density and composition statements for the accessible population, with injection-recovery and stated false-positive rates. [V]
3. **The "density upper bound" inequality is valid, and it is published as a concept** (Vokrouhlický et al. 2015, Asteroids IV: the peak of the ρ–Γ relation "often allows strict upper bounds on ρ", citing Chesley et al. 2003). It has been used in reverse, to reject detections (Desmars 2015; Del Vigna et al. 2018; the NEOCC pipeline of Fenucci et al. 2024). I found no one who has applied it across a population as a composition screen. [V]
4. **What the inequality actually bounds is ρ·D, not ρ.** Without a measured size, an albedo range of 0.05 to 0.5 moves the bound by a factor 2.6. With modelling allowances (finite-size peak, roughness beaming, 2σ on A2) the robust bound is about 1.5 to 2 times looser than the nominal one. Result on today's data: nominally 118 of the 154 NHATS objects with a ≥3σ A2 have ρ_max < 4,000 kg/m³ (at pV = 0.15), but with the conservative allowances only **11 of 154** do (at pV = 0.30). [C]
5. **Three cautionary cases found today**, all directly relevant to the project:
   - **1998 KY26** (Hayabusa2# target, the flagship "inner dark comet"): the out-of-plane acceleration was published as A3 = 2.70e-11 ± 6.45e-12 au/d² (4.2σ). The current JPL solution (orbit 36, data through 2024-05-06) has A3 = 1.69e-12 ± 1.12e-12 (1.5σ). The signal that defined it as a dark comet is not significant in the current public solution. [V]
   - **2022 OB5** (third most accessible NHATS object with a non-grav fit, Δv 3.52 km/s, AstroForge's former Odin target, X-complex, 1.54-minute rotator): JPL fits A2 = −1.66e-12 ± 0.065e-12 (26σ). NEOCC fits both A2 and an area-to-mass ratio, and the area-to-mass ratio comes out **negative**, −2.37e-4 ± 0.55e-4 m²/kg (4.3σ), which is unphysical for radiation pressure. Either the fit is contaminated or the object has a non-radiative acceleration. Nobody appears to have published on this. [V]
   - **(153201) 2000 WO107**, the one M-type NEA with both a Yarkovsky detection and an independent density (4.80 +0.34/−0.63 g/cm³, contact-binary force balance): its drift gives a nominal bound of ρ ≤ 3,640 kg/m³, i.e. the bound is violated at nominal values (consistent only within about 1σ of the size and A2 errors). NEOCC's pipeline rejects the detection as "too large for Yarkovsky". So the single known-answer test for metal exclusion is ambiguous. [V][C]
6. **A correction to the brief:** arXiv 2502.13222 is not the NEOCC pipeline paper. It is Fenucci et al. 2025 on Kamoʻoalewa. The NEOCC automated Yarkovsky pipeline is arXiv 2311.10175 (A&A 682, A29, 2024). [V]

## 1. Live check of the public catalogs (question f)

### 1.1 JPL SBDB, queried 2026-11-20

Query: `https://ssd-api.jpl.nasa.gov/sbdb_query.api` with `sb-cdata={"OR":["A1|DF","A2|DF","A3|DF"]}`. All counts below are [V].

| Scope | Any of A1/A2/A3 | A1 | A2 | A3 | DT |
|---|---|---|---|---|---|
| All small bodies | 989 (625 asteroids, 364 comets) | 301 (23 ast, 278 com) | 978 (620 ast, 358 com) | 125 (11 ast, 114 com) | 45 (comets) |
| NEOs | 686 (623 asteroids, 63 comets) | 69 (21 ast, 48 com) | 680 (618 ast, 62 com) | 24 (9 ast, 15 com) | 9 (comets) |

- The only non-NEO "asteroids" with these parameters are 457175 (2008 GO98) and 1I/ʻOumuamua.
- NEO asteroid parameter combinations: A2 only 601; A1+A2 8; A1+A2+A3 8; A2+A3 1; A1 only 5.
- NEO asteroids with A2: 618. Significance |A2|/σ ≥ 3: 573; ≥ 5: 351; ≥ 10: 146. Sign: 445 negative, 173 positive (2.57:1; for ≥3σ, 414:159 = 2.60:1), i.e. retrograde rotators dominate, as expected.
- H distribution of the 618: H<16: 8; 16–18: 51; 18–20: 122; 20–22: 209; 22–24: 133; 24–26: 75; 26–28: 14; ≥28: 6.
- Of the 618, SBDB itself lists a diameter for 136, an albedo for 129, a spectral type for 70, a rotation period for 233, diameter plus period for 97.
- **Caveat:** the query misses objects whose JPL solution uses a custom force model. Bennu is the example: its SBDB solution carries `AMRAT` and `RHO` (ρ = 1190), not A2, so it is not in the 618. Didymos currently has no non-grav parameter at all (its solution arc starts after the DART impact). The counts are therefore lower bounds on "objects with a measured drift".
- For scale: on 2023-08-08 the same catalog held 333 A2 values, 308 of them ≥3σ (Fenucci et al. 2024, §3.4). JPL's list has almost doubled in three years.

### 1.2 NHATS cross-match

NHATS API (`https://ssd-api.jpl.nasa.gov/nhats.api`, default limits) returned 7,226 objects. H distribution: H<22: 199; 22–24: 635; 24–26: 2,416; 26–28: 2,832; ≥28: 1,138; 6 without H. [V]

| NHATS subset | Objects | With any SBDB non-grav parameter |
|---|---|---|
| min Δv < 4 km/s | 40 | 8 |
| min Δv < 5 km/s | 286 | 16 |
| min Δv < 6 km/s | 726 | 28 |
| min Δv < 8 km/s | 2,196 | 65 |
| all (Δv < 12 km/s) | 7,226 | **174** (A1: 18; A2: 169; A3: 7) |

Of the 174, 78 are numbered and 96 unnumbered. 154 have A2 at ≥3σ. The full table is in Appendix A.

The 18 NHATS objects with A1 fitted: 2026 QQ8, 2021 GM1, 2020 CD3, 2020 GE, 2021 VH2, 2006 RH120, 2020 WY, 2012 LA, 2015 TC25, 2009 BD, 2011 MD, 2010 RF12, Apophis, 2013 XY20, 2005 VL1, 1998 KY26, 2016 GW221, 2016 NJ33. Eleven of these have A1 at ≥3σ.

The 7 NHATS objects with A3 fitted are all published "inner dark comets": 2006 RH120, 2010 RF12, 2013 XY20, 2005 VL1, 1998 KY26, 2016 GW221, 2016 NJ33. An eighth inner dark comet, 2010 VL65, is also on the NHATS list (Δv 5.27 km/s) but has no non-grav parameter in SBDB, because JPL has not adopted the 2010 VL65 = 2021 UA12 linkage in the public record. So **8 of the 9 inner dark comets are NHATS objects**. That is mostly a selection effect: slow, repeated Earth encounters are what make both a low Δv and a measurable acceleration.

### 1.3 ESA NEOCC, read 2026-11-20

- `neo_kc.cat` lists 43,146 NEAs; **391** carry a non-gravitational flag (386 with one parameter, 5 with two). 104 of those are NHATS objects. [V]
- Per-object files (`https://neo.ssa.esa.int/PSDB-portlet/download?file=<desig>.ke1`) give the model, the values ("Area-to-mass ratio [m²/t], Yarkovsky parameter [1e-10 au/d²]"), the A2 signal-to-noise, da/dt, and the full covariance. [V]
- NEOCC solves for an area-to-mass ratio on 8 objects, all NHATS: 2026 QQ8 (0.593 ± 0.042 m²/t), 2021 GM1 (0.254 ± 0.026), 2022 OB5 (−0.237 ± 0.055), 2020 GE (0.823 ± 0.038), 2012 LA (0.336 ± 0.055), 2015 TC25 (0.706 ± 0.084), 2009 BD (0.235 ± 0.036), 2011 MD (0.268 ± 0.069). 1 m²/t = 1e-3 m²/kg. [V]
- NEOCC does **not** publish a non-grav model for the objects whose A2 fails its Yarkovsky compatibility test: 2003 RM, 1998 SH2, 2001 ME1, 2016 GE1 and 2012 TC4 all have a gravity-only NEOCC orbit today. JPL publishes A2 for them. The two centres therefore disagree by policy on exactly the anomalous cases. [V]

## 2. Yarkovsky (question a)

### 2.1 Catalogs and counts

| Source | Count | Notes | Status |
|---|---|---|---|
| JPL SBDB (today) | 618 NEO asteroids with A2; 573 at ≥3σ | Not a curated "detection" list; includes dark comets | [V] |
| ESA NEOCC portal (today) | 391 NEAs with a non-grav model | Updated after each monthly MPC release | [V] |
| Fenucci et al. 2024, A&A 682, A29 (arXiv 2311.10175) | 348 accepted | Run of 2023-08-07: 32,396 NEAs → 5,308 candidates → 461 with S/N ≥ 3 → 373 pass the physical-compatibility test → 69 with isolated tracklets, 25 of them spurious → 348 | [V] |
| Greenberg et al. 2020, AJ 159, 92 (arXiv 1708.05513) | 247 of 600 analysed | Median "Yarkovsky efficiency" ξ = 0.12; negative:positive drift ratio 2.34 observed, 2.7 (+0.3/−0.7) debiased; da/dt ∝ 1/D confirmed | [V] |
| Del Vigna et al. 2018, A&A 617, A61 (arXiv 1805.05947) | 87 reliable + 24 marginal | Also 4 radiation-pressure detections; a list of spurious ones | [V] |
| Dziadura et al. 2023, A&A 680, A77 (Gaia DR3) | 49 NEAs (10 new) | 446 NEAs fitted; bulk densities computed from an approximate analytic expression. Full text not readable today (HTTP 403); numbers from abstract/search snippets | [V, abstract only] |
| Dziadura et al. 2025, A&A 693, A31 (arXiv 2411.09750; Gaia FPR, 66 months) | 43 robust; 9 added relative to DR3 | 446 NEAs fitted | [V] |
| Desmars 2015, A&A 575, A53 (arXiv 1501.01873) | 46 | Filters spurious detections with a size-based maximum drift | [V] |
| Nugent et al. 2012 (arXiv 1204.5990); Farnocchia et al. 2013 (arXiv 1212.4812) | 54; about 21 at S/N>3 | Earlier lists | [R] |
| Dziadura et al. 2022 (Icarus, Gaia DR2) | not checked | | [U] |

2025–2026 updates found by fresh search: no new population-level Yarkovsky catalog paper. New relevant work is methodological: Marčeta et al. 2025 (arXiv 2507.05789, numerical validation for super-fast rotators), Zhang et al. 2025 (arXiv 2505.09482, shape index), Golubov et al. 2026 (arXiv 2609.38549, improved analytic thermal dependence), plus single-object papers on Kamoʻoalewa (arXiv 2502.13222, 2606.25512). [V]

### 2.2 The dependence, written out

Linear theory for a sphere on a circular orbit (Vokrouhlický 1998, 1999; restated in Vokrouhlický et al. 2015, eqs. 1–3, and in Fenucci et al. 2024, eqs. 5–9; both read today) [V]:

- Diurnal: (da/dt)_d = −(8/9) · (α Φ / n) · W(R_ω, Θ_ω) · cos γ
- Seasonal: (da/dt)_s = +(4/9) · (α Φ / n) · W(R_n, Θ_n) · sin² γ
- Φ = π R² F / (m c) = 3 F / (2 D ρ c), with F = L☉ / (4π r²) the solar flux
- α = 1 − A (A = Bond albedo), γ = obliquity, n = mean motion
- W(R_ν, Θ_ν) = − κ1 Θ_ν / (1 + 2 κ2 Θ_ν + κ3 Θ_ν²), with W < 0
- Θ_ν = Γ √ν / (ε σ T⋆³), ε σ T⋆⁴ = α F, Γ = √(K ρ_s C) the thermal inertia, ν = ω (rotation) or n (orbit)
- R_ν = R / ℓ_ν, ℓ_ν = √(K / (ρ_s C ν)) the thermal penetration depth
- Large-body limit (R ≫ ℓ): κ1 = κ2 = κ3 = 1/2, so |W| = 0.5 Θ / (1 + Θ + 0.5 Θ²)

In the orbit-fit convention a_t = A2 / r² (r in au), da/dt = 2 A2 / (n a² (1 − e²)).

So da/dt ∝ (1 − A) · cos γ · |W(Θ)| / (ρ · D), with:
- **1/D and 1/ρ**: only the product ρ·D enters.
- **cos γ**: sign and amplitude; zero at 90°.
- **Θ** (thermal inertia and rotation period together): |W| peaks at Θ = √2 and falls off on both sides. For a 5-hour rotator at 1 au, Γ of 100 to 700 gives |W| of 0.10 to 0.21 (a factor 2). For a 1.5-minute rotator, Γ of 20 to 2,500 gives |W| from 0.205 down to 0.005 (a factor 40) [C].
- **Albedo**: weak, through (1 − A) and T⋆.

### 2.3 Is the "density upper bound" valid?

**Yes, within the model, and here is the exact statement.**

In the large-body limit max over Θ of |W| is (√2/2)/(2 + √2) = **0.2071**, at Θ = √2. With |cos γ| ≤ 1, the diurnal transverse acceleration cannot exceed (4/9)(1 − A)(0.2071) Φ = 0.0920 (1 − A) Φ. The seasonal term cannot rescue a larger value: for a retrograde rotator the two add, |da/dt| ∝ 2|W_d||cos γ| + |W_s| sin² γ ≤ 2 W_max, with the maximum still at |cos γ| = 1. Inserting constants [C]:

> **|A2|_max = 3.128e-8 · (1 − A) / (D[m] · ρ[kg/m³]) au/d²**
> equivalently **ρ ≤ ρ_max = 3.128e-8 · (1 − A) / (D[m] · |A2|[au/d²]) kg/m³**

In Greenberg et al.'s notation this is ξ ≤ ξ_max ≈ 0.092 (1 − A).

Allowances that loosen it:
- **Finite size.** Evaluating the full κ functions numerically (from the Vokrouhlický 1999 complex-amplitude expressions, as I recall them; the large-body limit reproduces 0.2071 to 3%) gives a global maximum |W| = **0.2455** at R/ℓ ≈ 4, Θ ≈ 1.74, i.e. +18.5% [C, from a recalled formula: verify against the paper before relying on it]. For diurnal heating of NEAs R ≫ ℓ, so 0.2071 applies; the finite-size peak matters for the seasonal term on metre-scale bare rock.
- **Roughness / thermal beaming.** "Surface roughness can increase the Yarkovsky force by tens of percent" (Vokrouhlický et al. 2015, citing Rozitis & Green 2012) [V]. Each refinement of the zero-order model changes results "by as much as several tens of percent" [V].
- **Non-linearity and shape.** Marčeta et al. 2025: analytic and numerical drifts differ by no more than 15% down to 10-second spin periods [V]. Golubov et al. 2026: the traditional three-parameter fit can be wrong by up to 50%, and by a factor 2 at small thermal parameter (where the force is small anyway) [V].
- **Measurement.** Use |A2| − 2σ.

A conservative working bound is therefore about ρ_max × (0.2455/0.2071) × 1.3 ≈ **1.5 × ρ_max**, evaluated at |A2| − 2σ. I call this the "generous" bound below.

What the bound does **not** cover: any non-radiative transverse force (outgassing, mass shedding), and mis-modelled radiation pressure aliasing into A2 on metre-scale objects. In those cases the "bound" comes out below any plausible density, which is itself the dark-comet flag (section 4).

**Has anyone published or used it?**
- Published as a principle: Vokrouhlický et al. 2015, §4.1: "The peak in ρ ... is associated with Θ_ω ≃ 1 where the Yarkovsky effect obtains its maximum effectiveness. This characteristic peak in the ρ vs. Γ relationship often allows strict upper bounds on ρ (e.g., Chesley et al., 2003)" [V]. That is for objects with known spin state and size (Golevka).
- Used in reverse to reject detections: Desmars 2015 (size-based maximum drift) [V]; Del Vigna et al. 2018 (ratio of measured to Bennu-scaled expected drift) [R for the detail]; Fenucci et al. 2024: compute the 95th percentile Y_M of the *maximum* drift (obliquity fixed at 0° or 180°, α = 1, Monte Carlo over D, ρ, P, Γ) and reject any detection with |da/dt| − 1.645σ > Y_M [V].
- Used to argue "not Yarkovsky": Farnocchia et al. 2023 for 2003 RM; Farnocchia et al. 2026 for 1998 SH2 ("ten times larger than the maximum possible acceleration compatible with the Yarkovsky effect for an object of this size") [V].
- Greenberg et al. 2020 state only 0 < ξ < 1 and call ξ > 1 unphysical; they do not use the tighter ξ ≤ 0.09 [V].
- **Not found:** any paper that applies ρ ≤ ρ_max object by object across the detection list as a density or metal-exclusion screen, or to NHATS. [V that the searches returned nothing; absence of evidence]

An inference of mine worth checking: Greenberg et al.'s **median** ξ of 0.12 exceeds the linear-theory maximum of 0.092. With their inputs (taxonomic mean densities, default 2,470 kg/m³, default albedo 0.14) more than half of their detections would need more than the theoretical maximum efficiency. The simplest reading is that the assumed ρ·D was too high for most small NEAs, compounded by detection bias toward high-efficiency objects. [C, inference]

### 2.4 How tight is it in practice?

**Validation on objects with independently known density** (A2 from SBDB or NEOCC today; D from SBDB or SsODNet; nominal bound, large-body, no allowances) [C]:

| Object | D (m) | \|A2\| (au/d²) | ρ_max | Independent ρ | ρ/ρ_max |
|---|---|---|---|---|---|
| Bennu (NEOCC A2) | 484 | 4.60e-14 | 1,380 | 1,194 (spacecraft) | 0.87 |
| Ryugu | 896 | 2.5e-14 ± 0.5e-14 | 1,374 | 1,190 (spacecraft) | 0.87 |
| Itokawa | 330 | 2.9e-14 ± 0.72e-14 | 2,942 | 1,900–1,930 (spacecraft) | 0.65 |
| 1996 FG3 | 1,670 | 1.2e-14 | 1,543 | 1,364 (binary) | 0.88 |
| Hermes | 800 | – | 2,961 | 1,810 (binary) | 0.61 |
| 1994 AW1 | 861 | – | 2,383 | 1,400 (binary, radar) | 0.59 |
| Sekhmet | 1,221 | – | 4,295 | 1,980 (binary, radar) | 0.46 |
| 2003 YT1 | 1,143 | – | 3,494 | 1,624 | 0.46 |
| Moshup (1999 KW4) | 1,335 | 6.1e-15 | 3,514 | 1,268–1,970 (binary) | 0.36–0.56 |
| Apollo | 1,200 | 3.7e-15 | 5,810 | 2,050 (binary, radar) | 0.35 |
| 2000 DP107 | 960 | 9.6e-15 | 3,274 | 998–1,380 (binary) | 0.30–0.42 |
| **2000 WO107** | 510 ± 83 | 1.56e-14 ± 0.32e-14 | **3,640** | **4,800** (+340/−630; contact-binary model) | **1.32** |

The bound holds for 11 of 12. The three spacecraft-visited rubble piles sit at 65–87% of the maximum, because all three have obliquities near 180° and Θ of order 1. The one violation is the only M-type in the set, and its "known" density is itself model-dependent (the authors note that two spheres instead of flattened lobes would give a density three times lower). Densities in the table come from SsODNet (read today) except where they are SBDB values; the independent-density column is as catalogued, not re-derived.

Across all 573 ≥3σ detections, the nominal ρ_max at pV = 0.15 has median 2,372 kg/m³ (quartiles 1,758 and 3,251). For the 125 with an SBDB diameter the median is 2,790 [C]. Since real densities of these objects are mostly 1,000–3,000, the typical detection sits within a factor 1–3 of its bound. That is what a detection-biased sample should look like.

**Worked example, 100 m class (H = 22.5).** [C]

| \|A2\| (au/d²) | pV = 0.05 (D = 188 m) | pV = 0.15 (109 m) | pV = 0.30 (77 m) | pV = 0.50 (59 m) |
|---|---|---|---|---|
| 5e-14 | 3,264 | 5,428 | 7,200 | 8,474 |
| 1e-13 | 1,632 | 2,714 | 3,600 | 4,237 |
| 2e-13 | 816 | 1,357 | 1,800 | 2,118 |

(ρ_max in kg/m³.) To exclude a metal body (ρ ≥ 4,000, pV ≤ 0.30) nominally needs |A2| > 9.0e-14; with the generous factor 1.5 and 2σ it needs roughly |A2| > 1.5e-13 measured to better than 10%. With a measured D of 100 m and A2 = 2e-13 ± 1e-14 the generous bound is about 2,500 kg/m³: metal excluded, monolithic ordinary chondrite (3,300) excluded, rubble pile required. With A2 = 1e-13 the generous bound is about 5,800: nothing excluded.

**Worked example, 10 m class (H = 27.5).** [C]

| \|A2\| (au/d²) | pV = 0.05 (D = 18.8 m) | pV = 0.15 (10.9 m) | pV = 0.30 (7.7 m) | pV = 0.50 (5.9 m) |
|---|---|---|---|---|
| 3e-13 | 5,440 | 9,047 | 12,000 | 14,123 |
| 1e-12 | 1,632 | 2,714 | 3,600 | 4,237 |
| 2e-12 | 816 | 1,357 | 1,800 | 2,118 |

For such objects the real constraint is much stronger than the bound **if the rotation period is known**, because a minutes-scale rotator can only approach the maximum with Γ of order 10–50. Example, 2022 OB5 (P = 92.5 s, a = 1.03 au): fraction of maximum achieved is 0.99 at Γ = 20, 0.72 at Γ = 50, 0.45 at Γ = 100, 0.18 at Γ = 300, 0.06 at Γ = 1,000 [C]. This is the published puzzle of Fenucci et al. 2021 (2011 PT), 2023 (2016 GE1: Γ < 100 at 90%) and Marčeta et al. 2025 (2016 GE1 best matched by Γ ≲ 20): fast rotators with large drifts need dust-like thermal inertia. Either they hold fine regolith against centrifugal force, or the drifts are not purely Yarkovsky.

**Error budget, ranked.**
1. Size, when not measured: D from H and pV. pV from 0.05 to 0.5 is a factor 3.2 in D; H errors of 0.3–0.5 mag add 15–25%.
2. Thermal inertia for fast rotators: up to a factor 40 in |W|. For slow rotators with regolith: a factor of about 2.
3. Obliquity: unknown for about 92% of detections; a factor 1 to ∞ in principle, but detections are biased to |cos γ| near 1.
4. A2 itself: 10–33% statistical at S/N 3–10, plus systematics (weighting, debiasing, isolated tracklets, A1 aliasing).
5. Model: +20–60% (roughness, finite size, non-linearity, shape).
6. Density is what is left.

### 2.5 How density and thermal inertia have been inferred so far

- **Bennu** (Chesley et al. 2014): da/dt with radar shape, spin and Spitzer thermal inertia gave ρ = 1,260 ± 70 kg/m³ [V via the 2015 review]; OSIRIS-REx later measured 1,190 (SBDB today: 1,194 ± 3) [V]. A 6% success. This is the method's best case: obliquity 178°, Θ near optimum, everything else measured.
- **Rozitis & Green 2014** (Geographos, arXiv 1407.2127): thermophysical model plus Yarkovsky and YORP: Γ = 340 (+140/−100), ρ = 2,100 (+550/−450) kg/m³; 1,450–2,400 across shape-model choices [V]. Rozitis et al. 2014 (1950 DA): 1.7 ± 0.7 g/cm³ [V via a citing paper]. Rozitis et al. 2013 (Apollo) [R].
- **Hanuš et al. 2018** (Phaethon, arXiv 1811.10953): da/dt = −(6.9 ± 1.9)e-4 au/Myr → ρ = 1.67 ± 0.47 g/cm³; 1.08 ± 0.30 under a different conductivity assumption [V]. Shows the model dependence.
- **Fenucci et al. 2021, 2023; ASTERIA** (Novaković et al. 2024, PSJ 5, 11; arXiv 2311.03479): Monte Carlo over D, ρ, γ, P and so on; solve measured = modelled drift for conductivity; output a thermal inertia PDF. Validated on Bennu plus 10 NEAs; applied to 38 NEAs (31 sub-km, 29 PHAs) [V]. Density is an input prior there, not the output. Kamoʻoalewa: Γ = 150 (+90/−45) or 181 (+95/−60) [V].
- **Mommert et al. 2014a,b** (2009 BD, 2011 MD): Spitzer flux plus an orbital model with both radiation pressure and Yarkovsky, giving joint probabilistic (D, pV, ρ, Γ) [V]. This is the closest prior art to what the project wants per object.
- **Dziadura et al. 2023**: densities for the 49 Gaia DR3 detections from an approximate analytic expression [abstract only].
- **SsODNet already stores Yarkovsky-derived densities**: of the 601 ssoCards I could read for SBDB's A2 objects, 55 have a density and 44 of those with ≥3σ A2 carry method "Yarkovsky" for most entries. Several are implausible as point estimates (Bacchus 609, 1998 WT24 485, Toutatis 727 kg/m³) [V]. That is a warning about point estimates with assumed obliquity and thermal inertia, and an argument for publishing bounds and posteriors instead.

### 2.6 Spin poles and diameters among the detections

From SsODNet ssoCards for the 623 NEO asteroids with a non-grav parameter (601 cards retrieved today) [V][C]:
- spin-pole solution: **50**
- measured diameter: **192** (162 NEATM, 14 thermophysical, 13 radar, 3 spacecraft)
- pole and diameter: 46; pole, diameter and A2 ≥ 3σ: **37**
- taxonomy: 278 (S 143, C 28, Q 27, X 23, V 13, L 10, M 8, K 7, B 6, A 5, Ch 4, E 2, P 2)
- thermal inertia: 56

So the "fully constrained" set where cos γ is known is about 37 objects, nearly all km-scale and numbered. None is a typical NHATS target. I did not query DAMIT directly; SsODNet aggregates DAMIT and radar poles, so 50 is a lower bound on what exists in the literature.

### 2.7 The metal-rich NEAs

- **(6178) 1986 DA** and **2016 ED85** (843295): no A2 in SBDB (orbit solutions of 2026-11-10 and 2026-08-26, 49-year and 37-year arcs, gravity only) and no non-grav model at NEOCC. **(3554) Amun**: no A2 in SBDB. [V]
- So the two best-established metal-rich NEAs are **not in the detection lists**. A non-detection is what high density predicts, but it is not a test until someone publishes an upper limit. For 1986 DA (D ≈ 2.3–2.8 km) the maximum A2 is about 2e-15 au/d² for ρ = 5,000 against about 5e-15 for ρ = 2,000 [C]. The best km-scale objects reach σ(A2) of 1–3e-16 (Phaethon 1.2e-16, Geographos 2.4e-16), so an informative upper limit is plausible but requires doing the fit, and 1986 DA's high eccentricity (0.585) and a = 2.81 au work against it.
- **(153201) 2000 WO107** is the one metal-type NEA with a detection: A2 = −1.564e-14 ± 0.325e-14 (4.8σ, SBDB); pole latitude −76° to −78° (retrograde, consistent with the sign); D = 510 ± 83 m; pV = 0.129. Krugly et al. 2025 (A&A; arXiv 2508.04535) derive 4.80 (+0.34/−0.63) g/cm³ from contact-binary force balance. An earlier abstract from the same group (EPSC2022-1150) estimated a low, non-metallic density from the Yarkovsky drift. NEOCC measures −23.5 ± 4.2 (×1e-4 au/Myr) against a 95th-percentile maximum of 15.8 for its assumed properties and rejects it. **The drift does not fit a 4.8 g/cm³ body at nominal values.** Either A2 is biased high (it is a 4–5σ detection with q = 0.20 au), the size is smaller than 510 m, or the shape-based density is too high. [V]
- Among A2 objects SsODNet classes 8 as M and 23 as X; only Nereus, 2000 GJ147, 2000 WO107 and 2000 DP107 have sizes [V].

## 3. Solar radiation pressure, A1 (question b)

### 3.1 Method

A radial acceleration A1/r² is fitted; A1 = C_R · (A/m) · L☉/(4π c), i.e. **A1 [au/d²] = 2.266e-7 · C_R · AMR [m²/kg]** [C]. For a sphere AMR = 3/(2 ρ D), so ρ = 1.5/(AMR · D). The area-to-mass ratio is measured; the density needs a size, hence an albedo. Micheli et al. 2012–2014 did this from astrometry alone with an albedo distribution; Mommert et al. 2014 added Spitzer to pin the size and fitted Yarkovsky jointly.

A size-independent diagnostic follows from combining with section 2: for purely radiative forces **|A2|/A1 ≤ 0.092 (1 − A)/C_R**, whatever the size and density [C]. Today's SBDB values: 2009 BD 0.020, 2020 GE 0.011, 2012 TC4 0.011, 2015 TC25 0.033, 2012 LA 0.028, 2011 MD 0.009: all allowed. **2006 RH120: 0.33**, more than three times the limit, so its transverse acceleration cannot be Yarkovsky, which matches its dark-comet classification. I did not find this ratio stated as a test in the literature, though Mommert et al. 2014 use the same physics.

### 3.2 Every detection I could find

| Object | H | Published result | SBDB A1 today (au/d²) | NEOCC AMR today (m²/kg) | Arc; data | Status |
|---|---|---|---|---|---|---|
| 2009 BD | 28.1 | AMR (2.97 ± 0.33)e-4 (Micheli+ 2012). Mommert+ 2014a, Spitzer non-detection: either D 2.9 ± 0.3 m, ρ 2.9 ± 0.5 g/cm³, Γ ≈ 30; or D 4 ± 1 m, ρ 1.7 (+0.7/−0.4), Γ ≈ 2000 | 5.6e-11 ± 0.85e-11 (6.6σ), plus A2 13σ | 2.35e-4 ± 0.36e-4 | 885 d; 180 obs | [V] |
| 2011 MD | 28.0 | AMR (3.2 ± 0.6)e-4, 5σ; ρ = 640 ± 330 kg/m³ (Micheli+ 2014). Mommert+ 2014b, Spitzer: D 6 (+4/−2) m, ρ 1.1 (+0.7/−0.5) g/cm³, porosity ≥ 65% | 7.4e-11 ± 2.5e-11 (3.0σ) | 2.68e-4 ± 0.69e-4 | 73 d at publication; 1,543 positions; flyby at 18,700 km | [V] |
| 2012 LA | 27.6 | Micheli+ 2013, AMR about 3.35e-4 | 6.7e-11 ± 1.2e-11 (5.6σ) | 3.36e-4 ± 0.55e-4 | 179 d; 103 obs | [R] for the paper, [V] for NEOCC |
| 2006 RH120 | 29.5 | First case; later shown to have anomalous A2 and A3 (Chesley+ 2016; Seligman+ 2023) | 1.43e-10 ± 0.08e-10 (17.8σ) | – | 284 d; 136 obs; minimoon | [V] |
| 2015 TC25 | 29.3 | Farnocchia+ 2017 (JPL mass estimate); Reddy+ 2016: D ≈ 2 m, E-type albedo, P = 133.8 s | 1.6e-10 ± 0.21e-10 (7.6σ) | 7.06e-4 ± 0.84e-4 | 562 d; 48 obs | [V] values; paper details partly [R] |
| 2012 TC4 | 26.7 | Del Vigna+ 2018 list it among SRP detections | 2.4e-11 ± 0.8e-11 (3.0σ), plus A2 | none | 1,897 d; 805 obs | [V] |
| 2020 CD3 | 31.7 | Fedorets+ 2020: AMR (6.9 ± 2.4)e-4; D 1.2 (+0.4/−0.2) m; density about 2.1–2.3 g/cm³ | 1.4e-10 ± 0.025e-10 (56σ) | – | 742 d; 128 obs; minimoon | [V] |
| 2024 PT5 | 27.4 | Bolin+ 2025: AMR (7.02 ± 2.05)e-5, D 5.4 ± 1.2 m, ρ ≈ 3.9 ± 2.1 g/cm³. Kareta+ 2025: 0.0 ± 1.3e-4, a non-detection | not fitted | not fitted | 190 d; 380 obs | [V]; the two papers disagree on whether it is a detection |
| 2021 GM1 | 30.4 | Fenucci+ 2024: found by the NEOCC pipeline, AMR 0.2564 m²/t | 5.8e-11 ± 1.1e-11 (5.3σ) | 2.54e-4 ± 0.26e-4 | 344 d; 113 obs | [V] |
| 2020 GE | 28.2 | No paper found | 1.76e-10 ± 0.13e-10 (14σ), plus A2 at 89σ | 8.23e-4 ± 0.38e-4 | 1,699 d; 58 obs; radar | [V] |
| 2026 QQ8 | 31.4 | New (discovered Aug 2026); no paper | 1.31e-10 ± 0.10e-10 (13σ) | 5.93e-4 ± 0.42e-4 | 92 d; 63 obs | [V] |
| 2021 VH2 | 28.8 | No paper found | 8.1e-11 ± 2.2e-11 (3.7σ) | – | 917 d; 47 obs | [V] |
| 2020 WY | 26.2 | No paper found | 6.2e-11 ± 2.9e-11 (2.1σ) | – | 360 d; 99 obs | [V] marginal |
| 2022 OB5 | 29.0 | No paper found | not fitted (A2 only) | **−2.37e-4 ± 0.55e-4** (negative) | 1,268 d; 49 obs | [V] |

Also carrying A1 in SBDB but not radiation-pressure cases: Toutatis (−3.1e-13, 3.3σ, negative), Apophis (1σ), and the dark comets 2016 NJ33, 2013 XY20, 2005 VL1, 2010 RF12, 2016 GW221, 2013 BA74, 1998 KY26.

Densities implied by today's SBDB A1 for a sphere with C_R = 1.2 [C]: 2009 BD 510–1,620 kg/m³ over pV 0.05–0.5; 2011 MD 370–1,160; 2012 LA 340–1,070; 2015 TC25 320–1,000; 2020 CD3 1,090–3,450; 2021 GM1 1,420–4,500; 2026 QQ8 990–3,140; 2021 VH2 490–1,540; **2020 GE 160–520**. 2020 GE's implied density is below 0.55 g/cm³ for any albedo up to 0.5. It is either extremely porous, far from spherical, mis-sized, or not natural. I found nothing published on it.

The consistent picture from the published cases: metre-scale objects with measured area-to-mass ratios come out at about 0.6–2.9 g/cm³, with the low values driving the "small NEAs are very porous or very reflective" discussion. None is metal-like. An iron body of 5 m would have AMR ≈ 6e-5 m²/kg, about a factor 4 below the smallest secure detection, so **radiation pressure will detect the fluffy objects and miss the metal ones**. For metals the useful product is an upper limit on AMR.

### 3.3 What a detection needs

- Size: every secure detection has H ≥ 26.7 (D ≲ 15 m).
- Geometry: slow, close Earth encounters. Micheli et al. 2014 note that the detected objects have Earth-like orbits (Δv < 4 km/s), which is what keeps them observable long enough. That is the NHATS population by construction.
- Arc: the shortest is 73 d (2011 MD), and that needed a 18,700 km flyby, about 1,500 positions and dedicated 2-m-class follow-up out to V > 24. 2026 QQ8 has 92 d and 63 observations at 13σ. Typical cases have 180 d to 5 yr.
- Astrometry: sub-0.1″ follow-up from large telescopes, careful station weighting (Micheli down-weighted a station that reported 968 positions in one night), and for the best cases radar.

### 3.4 How many NHATS objects could yield one from existing astrometry?

From SBDB today [C]:

| NHATS subset | Objects | arc ≥ 30 d | ≥ 60 d | ≥ 100 d | ≥ 365 d | of the ≥100 d: A1 already fitted |
|---|---|---|---|---|---|---|
| H ≥ 26 | 3,933 | 361 | 194 | 149 | 113 | 12 |
| H ≥ 27 | 2,370 | 140 | 74 | 59 | 40 | 10 |
| H ≥ 28 | 1,105 | 42 | 22 | 19 | 16 | 8 |

So the realistic pool is **about 50 objects** (H ≥ 27, arc ≥ 100 d, no A1 yet; listed by the script, they include 1991 VG, 2007 UN12, 2010 UE51, 2015 VO142, 2008 HU4, 2022 OC3, 2022 NX1, 2024 PT5, 2020 VN1), widening to about 140 if H 26–27 objects are included. JPL adds A1 when a gravity-only fit fails, so the easy ones are taken. My estimate is that a systematic refit yields **of order 5 to 15 new ≥3σ area-to-mass ratios and 30 to 100 informative upper limits** [U: an estimate, not a calculation]. Upper limits matter here: "AMR < 1e-4 m²/kg" on a 5 m object means ρ > 3 g/cm³.

## 4. Dark comets (question c)

### 4.1 Definition and list

Seligman et al. 2024: "Dark comets are near-Earth objects with no detected coma that have significant nongravitational accelerations explainable by outgassing of volatiles." Operationally: an A1/A2/A3 fit improves the orbit significantly, the acceleration is too large for Yarkovsky or radiation pressure "for typical bulk material properties", and no coma is seen. [V]

The fourteen (Seligman et al. 2024, PNAS 121, Tables 1–2; units au/d², σ = value/error) [V]:

| Object | Pop. | a, e | H | Size | A1 (σ) | A2 (σ) | A3 (σ) |
|---|---|---|---|---|---|---|---|
| 2001 ME1 | outer | 2.65, 0.87 | 16.5 | r ≈ 5 ± 2 km | −2.5e-13 (0.0) | −2.54e-13 (11.2) | 2.8e-12 (1.6) |
| 2005 UY6 | outer | 2.26, 0.87 | 18.1 | D ≈ 2.2 km (SBDB) | −2.9e-10 (0.7) | −6.35e-13 (4.0) | −4.9e-12 (0.7) |
| 1998 FR11 | outer | 2.81, 0.71 | 16.4 | r ≈ 5 ± 2 km | −1.8e-10 (0.6) | 2.94e-13 (3.1) | 8.4e-12 (1.0) |
| 2012 UR158 | outer | 2.24, 0.86 | 20.7 | D ≈ 0.63 km | 8.2e-11 (0.1) | −7.59e-12 (16.1) | 7.2e-12 (1.9) |
| 2003 RM | outer | 2.92, 0.60 | 19.8 | r ≈ 0.15–0.23 km | −4.0e-11 (0.4) | 2.10e-12 (75) | 5.3e-13 (0.1) |
| 2005 VL1 | inner | 0.89, 0.23 | 26.5 | r ≈ 11 m | −8.3e-10 (1.1) | −8.3e-13 (1.5) | −2.41e-11 (6.1) |
| 2010 RF12 | inner | 1.06, 0.19 | 28.4 | r ≈ 4 m | 3.4e-11 (0.6) | −2.1e-13 (1.0) | −1.51e-11 (10.7) |
| 1998 KY26 | inner | 1.23, 0.20 | 25.6 | D = 11 ± 2 m (2025) | 1.6e-10 (1.8) | −1.38e-13 (2.4) | 2.70e-11 (4.2) |
| 2016 NJ33 | inner | 1.31, 0.21 | 25.5 | r ≈ 16 m | 9.5e-10 (3.2) | −5.5e-13 (2.9) | 8.49e-11 (5.2) |
| 2010 VL65 | inner | 1.07, 0.14 | 29.2 | r ≈ 3 m | 6.6e-10 (0.5) | 1.5e-13 (0.3) | −9.12e-11 (7.0) |
| 2013 BA74 | inner | 1.75, 0.44 | 25.4 | – | 2.5e-10 (0.1) | 3.7e-13 (0.8) | 1.92e-11 (3.6) |
| 2006 RH120 | inner | 1.00, 0.04 | 29.5 | r ≈ 2–7 m | 1.38e-10 (17.7) | −5.07e-11 (8.0) | −1.30e-11 (3.9) |
| 2016 GW221 | inner | 0.83, 0.27 | 24.8 | – | 8.7e-11 (1.0) | −1.85e-13 (7.5) | 3.50e-11 (4.4) |
| 2013 XY20 | inner | 1.13, 0.11 | 25.7 | – | 1.8e-10 (3.6) | −1.52e-12 (5.6) | −1.09e-10 (8.4) |

Since then: **1998 SH2** (875163; D ≈ 383 m; SBDB A2 = −6.96e-13 ± 0.49e-13). Farnocchia et al. 2026 (Nature Astronomy, published 2026-07-10, doi 10.1038/s41550-026-02913-7): a planned Goldstone radar observation in August 2025 missed because the gravity-only prediction was off by about 19σ; the acceleration is about ten times the Yarkovsky maximum; deep CFHT, Danish 1.54 m and VLT imaging then showed a faint coma and a narrow tail; reclassified P/1998 SH2. It is "the first object for which cometary activity was initially predicted from non-gravitational perturbations and then confirmed". The authors suggest many of the larger (outer) dark comets would turn out to be ordinary weak comets under deep imaging. [V via JPL, phys.org and sci.news summaries; I did not read the paper itself]

### 4.2 Interpretation and controversies

- **Outgassing** is the proposed driver: required H2O production of order 1e21 molecules/s for the small ones (about 0.03 g/s for 1998 KY26 in Seligman et al. 2023), about 1e23 for 2003 RM (Farnocchia et al. 2023). Dust limits from stacked DECam/CFHT images are about 10, 0.1 and 0.1 kg/s for 1998 FR11, 2001 ME1 and 2003 RM. The out-of-plane direction is explained by seasonal polar outgassing on fast rotators (Taylor et al. 2024). [V]
- **Outer dark comets** now have direct support (P/1998 SH2). **Inner dark comets have none.** No gas or dust has been detected on any of them.
- **1998 KY26 specifically:**
  - Xe-type colours and high albedo (Bolin et al. 2025, AJ; arXiv 2501.17156): best taxonomic match Xe, C and D types fit poorly; dust limits < 1e-5 kg/s for µm grains; they doubt water outgassing and suggest shedding of grains by fast spin. [V]
  - D = 11 ± 2 m, P = 5.3516 ± 0.0001 min, albedo ≈ 0.52 (Santana-Ros et al. 2025, Nature Communications; SBDB carries these values). [V]
  - Hansen & Hirabayashi 2026 (Icarus; arXiv 2611.10275): orbit-averaged temperatures everywhere are at least 212 K against about 145 K needed to keep buried ice; 1% ice by mass would last about 2,000 years, or 62 years if it had to supply the acceleration. They favour radiation forces. [V]
  - **The current JPL solution no longer shows the signal:** A1 = 3.7e-11 ± 3.9e-11 (0.9σ), A2 = −2.20e-13 ± 0.49e-13 (4.5σ), A3 = 1.69e-12 ± 1.12e-12 (1.5σ); 85 optical plus 4 radar measurements, 1998–2024. The A2 is ordinary: with D = 11 m it needs only about 27% of the maximum Yarkovsky efficiency for ρ = 2,800 kg/m³ [C]. NEOCC independently fits A2 only (−2.73e-13 ± 0.37e-13). I found no paper stating that the out-of-plane term has collapsed; the 2026 papers above still argue about its cause. [V for the numbers; the interpretation is mine]
  - Technosignature claims: 1998 KY26 = Phobos 1 (Hibberd et al., arXiv 2606.01288, 2609.24283); 2005 VL1 = Venera 2 (Loeb & Cloete, arXiv 2503.03552), refuted by Spada (arXiv 2503.09137) using open-source orbit fitting. [V] These matter only as a sign of how soft the evidence base is.
- **NEOCC treats the same objects as spurious Yarkovsky detections**, not as a class (Fenucci et al. 2024, §3.2, §3.5) [V].
- **Fraction of NEOs that are dark comets:** 0.5% to 60% (Taylor et al. 2024, Icarus, as reported in the press release; I did not read the paper) [V for the press figure]. A range that wide is not a measurement.
- **Statistical softness.** Several defining detections are 3–4σ in one component out of three fitted, on 76–99 observations (2013 BA74: A3 at 3.6σ; 1998 KY26: 4.2σ, now 1.5σ). Fitting three extra parameters and keeping the significant one is a look-elsewhere problem that the papers do not quantify.

### 4.3 Has anyone run a systematic search?

| Work | Scope | Threshold and controls | Verdict |
|---|---|---|---|
| JPL routine orbit determination | all NEOs, as needed | Not published. Parameters are added when a gravity-only fit fails; no stated threshold or false-alarm rate | Systematic in practice, undocumented |
| Chesley et al. 2016 | Yarkovsky search over NEAs | Found the 2003 RM and 2006 RH120 anomalies as by-products | A2 only [R] |
| Fenucci et al. 2024 (NEOCC) | all 32,396 NEAs → 5,308 candidates | A2 only. S/N ≥ 3; drift below the 95th percentile of the modelled maximum; isolated-tracklet test | The only documented all-NEA pipeline. Anomalies are discarded, not studied. Table B.3 lists 48 JPL detections it rejects or misses, including 2003 RM, 2011 CL50, 2004 JN1, 2006 RH120, 2013 BA74, 2016 GE1, 2000 WO107 |
| Seligman et al. 2023, 2024 | case by case | "Serendipitous (and uncoordinated) astrometric observations"; significance per component; χ² with and without | Not systematic; no false-positive control |
| Hui & Jewitt 2017 (arXiv 1612.06920) | 18 active asteroids | S/N > 3 → 3 detections (313P, 324P, Phaethon) | Small targeted sample |
| Taylor et al. 2024 (ApJ; arXiv 2410.06874) | synthetic tracklets through MPC linking | Linking fails for a significant fraction at \|A\| ≥ 1e-8 au/d²; search for unlinked pairs recovers only 2010 VL65 = 2021 UA12 | Injection test of *linking*, not of detection |
| Hung et al. 2023 (arXiv 2310.00055) | 134 main-belt asteroids | Synthetic-observation tests of detectability; no reliable detections | Main belt only |
| Farnocchia et al. 2026 | proposal | "Analyzing the motion of all near-Earth objects using precision astrometry" as a diagnostic | Proposed by the JPL group, not yet published as a result |

**So: no published all-NEO or all-NHATS search for A1/A2/A3 with pre-registered thresholds, injection-recovery and a measured false-positive rate.** The JPL group has said publicly (July 2026) that this should be done, and they hold the best tools to do it.

A crude version can be run on public numbers in minutes. Applying the generous bound of section 2.3 to every ≥3σ A2 in SBDB (573 objects) and asking which need ρ < 1,000 kg/m³ even at pV = 0.6 or the measured size returns nine objects [C]: 2012 UR158, 2005 UY6, 2003 RM, 2001 ME1, 1998 FR11 (all five outer dark comets), 1998 SH2 (now a comet), 2006 RH120, and two not on the published list: **(883607) 2016 TA56** (a = 2.69, e = 0.78, i = 32°, H 18.1; A2 = −3.19e-12 ± 0.36e-12, 8.9σ; 94 observations) and **(428209) 2006 VC** (A2 = +6.4e-13 ± 1.7e-13, 3.7σ, marginal). Relaxing to ρ < 2,000 adds NHATS objects **2011 CL50** (H 27.3; A2 = +4.38e-12 ± 0.29e-12, 15σ; nominal ρ_max 340–915 kg/m³; NEOCC rejects it as too large) and **2003 LN6** (H 24.7; A2 = +7.4e-13, 46σ; nominal ρ_max 620–1,670), then 2004 JN1. This recovers every known case that has an A2 and is a first "recover the known objects" pass. Whether 2016 TA56 and 2011 CL50 are known to the dark-comet authors I could not determine.

## 5. Resource framing and the gap (question d)

What exists:
- **Mission-target mass estimates**, case by case: 2009 BD, 2011 MD (and 2013 EC20, 2008 HU4 as candidates) for NASA's Asteroid Redirect Mission, which needed a target of about 7–10 m and about 500 t (Mommert et al. 2014a,b; Micheli et al. 2012, 2014); 2015 TC25 (Farnocchia et al. 2017); Bennu and 1950 DA; Kamoʻoalewa for Tianwen-2 (Fenucci et al. 2025). [V]
- **Population thermal-inertia and density work** not aimed at resources: ASTERIA (38 NEAs), Dziadura et al. 2023 (49 NEAs), Greenberg et al. 2020 (efficiencies for 247). [V]
- **Accessibility-and-resources literature** that does not use non-gravitational data: e.g. Alarcon et al. 2026 on 2022 OB5 ("Accessible does not mean exploitable"), which gives the density as "poorly constrained", 1,800–4,900 kg/m³, and does not mention the 26σ A2 sitting in SBDB for the same object [V]. ASIME 2016/2018 white papers list Yarkovsky-derived density for 1950 DA as an example [V via search snippet].

What I could not find after targeted searches (web and arXiv, 2025–2026 included): any paper or project that (i) frames radiation-pressure, Yarkovsky or anomalous accelerations as prospecting screens, (ii) applies them systematically to NHATS or any low-Δv list, or (iii) publishes per-object density bounds or composition-class probabilities from them.

**The gap, stated precisely.** For the roughly 174 NHATS objects that already have a public non-gravitational fit, and the roughly 50–150 more that could support one, nobody has published: (a) an independent, reproducible refit with a stated detection threshold and an injection-recovery-calibrated false-alarm rate; (b) the implied ρ·D upper bound, area-to-mass ratio or AMR upper limit, and A2/A1 ratio, propagated to a posterior over density given honest priors on albedo, obliquity and thermal inertia; (c) the resulting "not metal", "not a monolith", "anomalous, possibly volatile-driven or spurious" flags with calibrated error rates. The gap is in inference, calibration and openness. It is not in orbit fitting, and it is not a population-scale gap: it concerns a few hundred objects.

## 6. Gaia DR4 and Rubin (question e)

**Gaia DR4** [V, ESA Gaia pages read today]:
- Not yet released. Planned for **2 December 2026, 12:00 CET**; the archive goes offline on 25 November 2026 to prepare. Date announced 7 May 2026 and repeated in news items of 25 September, 8 October and 30 October 2026 with no delay.
- Based on 66 months (25 July 2014 to 20 January 2020). DR5 (10.5 years) "not before the end of 2030".
- Solar-system content per the DR4 content page (updated 14 September 2026, marked as still subject to change): `sso_source` 436,551 objects; `sso_observation` 60,542,356 rows of epoch data; `sso_reflectance_spectrum` 436,551; `sso_xp_epoch_spectrum` 8,656,146.
- Announced DR4 papers include "Dynamical and physical properties of small bodies from epoch astrometry" (performance verification) and "Reflectance spectra and taxonomy of Solar System small bodies". Not yet public; the first one may well contain the collaboration's own Yarkovsky results [U].
- The 66-month asteroid astrometry is **not new** for the 156,764 DR3 objects: the Focused Product Release of October 2023 already delivered it, and Dziadura et al. 2025 already mined it (446 NEAs → 43 robust detections, 9 more than DR3). DR4 adds about 2.8 times more objects overall and reprocessed astrometry.
- **Published prediction for the number of new Yarkovsky detections with DR4: none found.** Dziadura et al. 2025 say only that "the final Gaia catalog may provide a much higher number of high signal-to-noise ratio detections". Desmars 2015 discusses Gaia's impact without a count.
- Relevance to NHATS: essentially nil directly. Gaia stops near G ≈ 20.7; NHATS objects are H 24–31 and are in Gaia, if at all, for hours near a close approach. DR4 helps the km-scale calibration set (the objects in section 2.4) and star-catalog debiasing of ground-based astrometry.

**Rubin/LSST:**
- Kurlander et al. 2025 (arXiv 2506.02487, Sorcha simulation) [V]: 127,040 ± 557 NEOs discovered over the survey; median 23 detections and a median arc of 96 d per NEO; 35% with arcs over two years. For d ≤ 10 m: about 14,000 discovered, median 11 detections, 90% with arcs under three months, but **about 885 with arcs of two years or more**. Today there are about 29–40 NHATS objects with H ≥ 27 and arcs over one to two years. So the pool for radiation-pressure and small-body Yarkovsky fits should grow by roughly 20 times, but only late in the survey.
- Astrometric precision about 10 mas, "expected to facilitate detections of non-gravitational forces" (LSST Solar System roadmap, arXiv 2009.07653) [V].
- **Published forecast of the number of LSST Yarkovsky or radiation-pressure detections: none found.**
- Rubin status in November 2026: survey reported as under way in February 2026 [V, one news item]; I did not verify data-release status. Useful multi-year arcs on newly found small NEOs cannot exist before about 2028.

## 7. Opportunities

1. **Refit-and-compare gate.** Reproduce JPL and NEOCC A2 values for the 270-plus objects both publish (Fenucci et al. 2024 found χ < 2 agreement for all but two) with an open orbit-determination stack. This is the natural "recover known objects first" test, and it is a hard one.
2. **ρ·D bound and anomaly flag for every NHATS object with A2** (154 at ≥3σ today), published as a posterior, with the generous and nominal versions and the size assumption explicit. The anomaly end of the same statistic recovers all known outer dark comets from public numbers.
3. **Area-to-mass ratios and upper limits** for the roughly 50–140 small NHATS objects with long arcs, including non-detections as density lower limits.
4. **The A2/A1 ratio test** for the handful with both.
5. **Injection-recovery on real observation sets**: add synthetic A1/A2/A3 to the actual epochs and error model of each object, refit, and publish detection efficiency and false-alarm rate as a function of arc, H and observation count. I found nothing like this for NEA non-gravitational detections.
6. **Case studies with public interest**: 2022 OB5 (negative area-to-mass ratio, 26σ drift, mining target); 1998 KY26 (vanished A3); 2020 GE (implied density below 0.55 g/cm³); 2000 WO107 (metal test); 2011 CL50 and 2016 TA56 (unlisted anomalies); upper limit on 1986 DA's drift.

## 8. Ways this fails or misleads

- **Coverage.** 2.4% of NHATS. A catalog whose density column is empty for 97% of rows.
- **The bound is on ρ·D.** Without thermal-IR or radar sizes it excludes metal robustly for about 11 NHATS objects today.
- **Metal is the class this channel is worst at.** High density and high conductivity both suppress the drift and the radiation-pressure signal. Metal candidates produce non-detections; the detected sample is biased to light, low-conductivity, pole-aligned bodies. Any population statement must model that selection.
- **The one metal known-answer case does not validate** (2000 WO107).
- **Significance inflation.** 1998 KY26's 4.2σ term fell to 1.5σ with one more apparition. Three-parameter fits on fewer than 100 observations, selected after the fact, need a trials correction nobody has applied.
- **Aliasing and unphysical fits.** 2022 OB5's negative area-to-mass ratio at 4.3σ with A1–A2 correlation 0.80 shows the two terms trade off on short, sparse arcs.
- **Fast-rotator physics is unsettled.** Published fits need Γ ≲ 20–100 on minute-scale rotators. If that is wrong physics rather than real regolith, density bounds for exactly the small accessible objects are wrong too.
- **"Dark comet" is not a water detection.** No gas seen on any inner dark comet; the best-studied one is Xe-type, hot, and no longer anomalous in the current fit. Presenting anomalous acceleration as a volatile indicator on a public site would overstate the evidence.
- **Orbit determination at this fidelity is specialist work.** Star-catalog debiasing, per-station weighting, timing errors, radar, planetary and asteroid perturbers, and close-approach dynamics for co-orbitals all move 3–5σ results. An agent-built fitter that is 95% right will manufacture false detections.
- **Scoop risk.** JPL has announced the all-NEO screening idea; NEOCC already runs a monthly A2 pipeline. The search itself is theirs to win. The open, calibrated inference layer is not being done by anyone I could find.
- **Circularity.** SsODNet densities for these objects are mostly Yarkovsky-derived. They cannot validate a Yarkovsky density method.

## 9. Open questions

1. Which open orbit-determination code can match JPL/NEOCC A2 values to within 1σ on the common set (find_orb, OrbFit, or newer Python packages)? I did not evaluate candidates.
2. Does the finite-size maximum |W| ≈ 0.2455 hold in the original Vokrouhlický expressions, and what is the true maximum in a non-linear model with roughness? A single number, ξ_max with an uncertainty, should be fixed and pre-registered.
3. Is 1998 KY26's loss of A3 significance known to the dark-comet authors, and does it hold under their weighting?
4. What explains 2022 OB5's negative area-to-mass ratio at NEOCC? Does a joint A1/A2 fit with physical priors (A1 ≥ 0, |A2|/A1 ≤ 0.1) still fit the astrometry?
5. Is 2020 GE natural?
6. Are 2016 TA56 and 2011 CL50 already tracked as dark-comet candidates?
7. What upper limit on A2 do existing data give for 1986 DA and 2016 ED85?
8. How many NHATS objects have NEOWISE, Spitzer or radar sizes that would turn ρ·D into ρ? (Other researchers' areas; it decides how much this channel is worth.)
9. Will the Gaia DR4 small-bodies paper (2 December 2026) publish its own Yarkovsky list, and how many NEAs does `sso_source` contain?
10. Is there any forecast, even unpublished, for Rubin's small-NEO non-gravitational yield?

## Appendix A. NHATS objects with a fitted non-gravitational parameter in JPL SBDB (2026-11-20)

Sorted by minimum round-trip Δv. A1/A2/A3 in au/d² with significance. ρ_max is the nominal linear bound for pV = 0.15 (multiply by about 0.6 for pV = 0.05 and 1.56 for pV = 0.5; multiply by about 1.5 and use |A2| − 2σ for the conservative version). "NEOCC model" is what ESA NEOCC solves for the same object where it has a non-grav model.

