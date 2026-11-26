"""The fixture objects: what each row must say, and where in the source files that comes from.

docs/plan.md Appendix B names ten objects, each a distinct failure mode. Eight
more are added: 2023 RA4 and 1999 AO10 (periods that exist only in Pravec's
table), 2001 CQ36 (two independent sizes and a fitted drift), 2017 BL6 and
1999 NW2 (a limit on the period that JPL repeats without its limit sign),
1998 KY26 (a newer period against an old table), 2003 LN6 (a Spitzer fit below
the detection bar) and 2008 TC3 (a body that no longer exists).

Every expected value below was read from the file and place given in its
"where". The files:

    NHATS    data/snapshots/2026-11-24/nhats.json       one line; data[i] is the i-th element of "data"
    SBDB     data/snapshots/2026-11-24/sbdb_neo.json    one line; data[i] likewise, cells in "fields" order
    CARD     data/research/dl/coverage-exact/cards/<file>
    STATUS   data/research/dl/coverage-exact/cards/_status.tsv
    PRAVEC   data/sources/pravec/newres-2026-11-24.txt
    CURATED  registry/curated.toml                      hand-entered, each claim with its citation
    LCDB     data/research/dl/coverage-exact/lcdb/x/lc_summary_pub.txt
    SPITZER  data/research/dl/coverage-exact/spitzer/spitzerneos.csv

The expectations hold for the research snapshot of SsODNet cards alone (the
1,704 cards and _status.tsv). The folder data/sources/ssodnet/cards grows
while a fetch job runs, so tests/test_ledger.py builds with that folder left
out before comparing against this file.

A fact is (label, value, source, extras, where). extras may hold quality, lo, hi.
"absent" lists labels that must not appear in the row.
"""

NO_WINDOW = "none through 2045"


def f(label, value, source, where, **extras):
    return {"label": label, "value": value, "source": source, "where": where, **extras}


FIXTURES = {
    # ------------------------------------------------------------------
    "2011 AA37": {
        "why": "unreliable period: 10 hours in JPL's table with no grade, graded 1+ in the lightcurve database",
        "spellings": ["2011 AA37", "2011AA37", "2011_AA37", "K11A37A", "(2011 AA37)"],
        "number": None, "name": None, "designation": "2011 AA37",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 5.851, "jpl-nhats", "NHATS data[1917].min_dv.dv"),
                f("trip at lowest delta-v", 386, "jpl-nhats", "NHATS data[1917].min_dv.dur"),
                f("shortest trip", 122, "jpl-nhats", "NHATS data[1917].min_dur.dur"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[8563].condition_code"),
                f("arc", 5783, "jpl-sbdb", "SBDB data[8563].data_arc"),
                f("observations", 193, "jpl-sbdb", "SBDB data[8563].n_obs_used"),
                f("last observed", "2026-11-13", "jpl-sbdb", "SBDB data[8563].last_obs"),
                f("window start", "2026-11-27", "jpl-nhats", "NHATS data[1917].obs_start", ref="as of 2026-11-24"),
                f("window end", "2027-03-20", "jpl-nhats", "NHATS data[1917].obs_end", ref="as of 2026-11-24"),
                f("window peak brightness", 21.85, "jpl-nhats", "NHATS data[1917].obs_mag"),
                f("window pointing", "pointable", "jpl-nhats", "NHATS data[1917].obs_flag is a blank"),
            ]},
            "size": {"state": "prior", "unchecked": [], "absent": ["diameter"], "facts": [
                f("H", 22.90, "jpl-sbdb", "SBDB data[8563].H"),
            ]},
            # The test case for "an unreliable period never gives measured".
            "spin": {"state": "prior", "unchecked": [], "facts": [
                # the remark's grade is used, the lower of its pair; the U column rounds it to 1
                f("period", 10.0, "pravec", "PRAVEC line 2189, U column 1; remark 'U = 1+ or 2-'", quality="1+"),
                f("period", 10.0, "lcdb", "LCDB line 34823, PERIOD 10., U 1+", quality="1+"),
                f("period", 10.0, "jpl-sbdb", "SBDB data[8563].rot_per '10.'", quality=None),
            ]},
            # CARD 2011_AA37.json holds an absolute magnitude and nothing else under parameters.physical.
            "surface": {"state": "prior", "unchecked": [], "absent": ["class", "albedo"], "facts": []},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -1.5e-13, "jpl-sbdb", "SBDB data[8563].A2 -1.5e-13, A2_sigma 1.2e-14",
                  lo=-1.62e-13, hi=-1.38e-13),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2009 BD": {
        "why": "the only cheap object with a fitted push and a size; its albedo on file is computed, not measured",
        "spellings": ["2009 BD", "2009BD", "K09B00D"],
        "number": None, "name": None, "designation": "2009 BD",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 4.729, "jpl-nhats", "NHATS data[2405].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "absent": ["window start"], "facts": [
                f("condition code", 1, "jpl-sbdb", "SBDB data[7143].condition_code"),
                f("arc", 885, "jpl-sbdb", "SBDB data[7143].data_arc"),
                f("next window", NO_WINDOW, "jpl-nhats", "NHATS data[2405].obs_start is null"),
            ]},
            "size": {"state": "measured", "unchecked": [], "facts": [
                f("diameter", 4.0, "ssodnet",
                  "CARD 2009_BD.json parameters.physical.diameter: 0.004 km -0.001 +0.001, method TPM, Mommert+2014a",
                  quality="TPM", lo=3.0, hi=5.0),
                f("H", 28.10, "jpl-sbdb", "SBDB data[7143].H"),
            ]},
            # LCDB line 34702 lists 2009 BD with no period.
            "spin": {"state": "prior", "unchecked": [], "absent": ["period"], "facts": []},
            # The test case for "a Computed albedo never gives measured".
            "surface": {"state": "prior", "unchecked": [], "absent": ["class"], "facts": [
                f("albedo", 0.6352, "ssodnet",
                  "CARD 2009_BD.json parameters.physical.albedo: 0.6352, method Computed, Berthier+2023",
                  quality="Computed"),
            ]},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A1", 5.6e-11, "jpl-sbdb", "SBDB data[7143].A1 5.6e-11, A1_sigma 8.5e-12", lo=4.75e-11, hi=6.45e-11),
                f("A2", -1.1e-12, "jpl-sbdb", "SBDB data[7143].A2 -1.1e-12, A2_sigma 8.4e-14"),
                f("density", 2287.738, "ssodnet",
                  "CARD 2009_BD.json parameters.physical.density: 2287.738 kg/m3, methods Yarkovsky and SRP",
                  quality="Yarkovsky+SRP"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2022 OB5": {
        "why": "its 92-second period (Alarcon et al. 2026) is in none of the databases: registry/curated.toml holds it",
        "spellings": ["2022 OB5", "2022_OB5", "K22O05B"],
        "number": None, "name": None, "designation": "2022 OB5",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 3.517, "jpl-nhats", "NHATS data[4903].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[29616].condition_code"),
                f("arc", 1268, "jpl-sbdb", "SBDB data[29616].data_arc"),
                f("observations", 49, "jpl-sbdb", "SBDB data[29616].n_obs_used"),
                f("next window", NO_WINDOW, "jpl-nhats", "NHATS data[4903].obs_start is null"),
            ]},
            # First observed 2022-07-28 (SBDB data[29616].first_obs), after the last Spitzer observation
            # (2019-11-30). Spitzer has stopped observing, so its table is final: looked for and absent
            # (method/v0_1/ledger.toml [closed_tables]).
            "size": {"state": "prior", "unchecked": [], "absent": ["diameter"], "facts": [
                f("H", 28.99, "jpl-sbdb", "SBDB data[29616].H 28.99, H_sigma 0.42", lo=28.57, hi=29.41),
            ]},
            # CARD 2022_OB5.json has no "spins"; SBDB data[29616].rot_per is null; not in PRAVEC or LCDB.
            # CURATED claim 1: 1.542 +/- 0.001 min, Alarcon et al. 2026 (docs/research/verify-facts-missions.md).
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 0.0257, "curated", "CURATED claim 1: 1.542 min is 0.0257 h"),
            ]},
            # CURATED claim 2: X-complex from five-band photometry, the same paper.
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("class", "X", "curated", "CURATED claim 2"),
            ]},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -1.7e-12, "jpl-sbdb", "SBDB data[29616].A2 -1.7e-12, A2_sigma 6.5e-14"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2026 QQ8": {
        "why": "new, and unknown to SsODNet: four rows are not checked, never 'not measured'",
        "spellings": ["2026 QQ8", "2026QQ8", "K26Q08Q"],
        "number": None, "name": None, "designation": "2026 QQ8",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 3.345, "jpl-nhats", "NHATS data[7173].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 1, "jpl-sbdb", "SBDB data[42247].condition_code"),
                f("arc", 94, "jpl-sbdb", "SBDB data[42247].data_arc"),
                f("observations", 73, "jpl-sbdb", "SBDB data[42247].n_obs_used"),
                f("last observed", "2026-11-21", "jpl-sbdb", "SBDB data[42247].last_obs"),
            ]},
            # STATUS line 1: "2026 QQ8  404": SsODNet did not know the object, so no card exists.
            # Found in 2026, after the lightcurve database (2023-10-01) and the Spitzer table (2019-11-30) were
            # made: both are "older than this asteroid". Pravec's table (2026-10-15) is not: first observed 2026-08-19.
            "size": {"state": "unchecked", "unchecked": ["ssodnet"], "facts": [
                f("H", 31.37, "jpl-sbdb", "SBDB data[42247].H"),
            ]},
            "spin": {"state": "unchecked", "unchecked": ["lcdb", "ssodnet"], "facts": []},
            "surface": {"state": "unchecked", "unchecked": ["ssodnet"], "facts": []},
            "push": {"state": "measured", "unchecked": ["ssodnet"], "facts": [
                f("A1", 1.3e-10, "jpl-sbdb", "SBDB data[42247].A1 1.3e-10, A1_sigma 9.7e-12"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2020 CD3": {
        "why": "captured by Earth for a time; a period and a class from one paper, no size",
        "spellings": ["2020 CD3", "K20C03D"],
        "number": None, "name": None, "designation": "2020 CD3",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 3.571, "jpl-nhats", "NHATS data[3258].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[22527].condition_code"),
                f("arc", 742, "jpl-sbdb", "SBDB data[22527].data_arc"),
            ]},
            "size": {"state": "prior", "unchecked": [], "absent": ["diameter"], "facts": [
                f("H", 31.74, "jpl-sbdb", "SBDB data[22527].H"),
            ]},
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 0.053, "ssodnet",
                  "CARD 2020_CD3.json parameters.physical.spins[0].period: 0.053 h, Fedorets+2020", quality=None),
            ]},
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("class", "V", "ssodnet", "CARD 2020_CD3.json parameters.physical.taxonomy.class, Fedorets+2020"),
            ]},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A1", 1.4e-10, "jpl-sbdb", "SBDB data[22527].A1 1.4e-10, A1_sigma 2.5e-12"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2010 CW266": {
        "why": "no H, a one-day arc, and unknown to SsODNet",
        "spellings": ["2010 CW266", "2010CW266"],
        "number": None, "name": None, "designation": "2010 CW266",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 4.100, "jpl-nhats", "NHATS data[7142].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 9, "jpl-sbdb", "SBDB data[7834].condition_code"),
                f("arc", 1, "jpl-sbdb", "SBDB data[7834].data_arc"),
                f("observations", 5, "jpl-sbdb", "SBDB data[7834].n_obs_used"),
                f("next window", NO_WINDOW, "jpl-nhats", "NHATS data[7142].obs_start is null"),
            ]},
            # SBDB data[7834].H and NHATS data[7142].h are both null. STATUS line 487: "2010 CW266  404".
            "size": {"state": "unchecked", "unchecked": ["ssodnet"], "absent": ["H", "diameter"], "facts": []},
            "spin": {"state": "unchecked", "unchecked": ["ssodnet"], "facts": []},
            "surface": {"state": "unchecked", "unchecked": ["ssodnet"], "facts": []},
            "push": {"state": "unchecked", "unchecked": ["ssodnet"], "facts": []},
        },
    },
    # ------------------------------------------------------------------
    "469219": {
        "why": "Kamo'oalewa: a name each source spells differently, and JPL's designation is now a number",
        "spellings": ["469219", "(469219)", "2016 HO3", "2016_HO3", "K16H03O", "k9219", "Kamo'oalewa", "Kamo`oalewa",
                      "Kamoʻoalewa", "Kamo’oalewa", "469219 Kamo`oalewa (2016 HO3)", "(469219) Kamo'oalewa",
                      "(469219) 2016 HO3"],
        "number": 469219, "name": "Kamoʻoalewa", "designation": "2016 HO3",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 6.107, "jpl-nhats", "NHATS data[1020].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[2204].condition_code"),
                f("arc", 7660, "jpl-sbdb", "SBDB data[2204].data_arc"),
                f("window start", "2026-11-27", "jpl-nhats", "NHATS data[1020].obs_start"),
                f("window end", "2027-05-31", "jpl-nhats", "NHATS data[1020].obs_end"),
                f("window peak brightness", 22.56, "jpl-nhats", "NHATS data[1020].obs_mag"),
            ]},
            # CARD 469219.json has no diameter; not in SPITZER; SBDB data[2204].diameter is null.
            # CURATED claim 3: 18 +/- 2 m from JWST (Sharkey et al. 2026; docs/research/verify-facts-missions.md).
            "size": {"state": "measured", "unchecked": [], "facts": [
                f("diameter", 18.0, "curated", "CURATED claim 3", lo=16.0, hi=20.0),
                f("H", 24.31, "jpl-sbdb", "SBDB data[2204].H"),
            ]},
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 0.465, "curated", "CURATED claim 4: 27.9 min is 0.465 h (docs/research/verify-capability.md row 18)"),
                f("period", 0.467, "lcdb", "LCDB line 33510, PERIOD 0.467, U 2", quality="2"),
                f("period", 0.466017, "ssodnet", "CARD 469219.json parameters.physical.spins[0].period, Zhang+2025"),
                f("period", 0.467, "jpl-sbdb", "SBDB data[2204].rot_per"),
            ]},
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("class", "S", "ssodnet", "CARD 469219.json parameters.physical.taxonomy.class, Reddy+2017"),
            ]},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -1.3e-13, "jpl-sbdb", "SBDB data[2204].A2 -1.3e-13, A2_sigma 1.8e-14"),
                f("A2", -157.004133e-15, "ssodnet",
                  "CARD 469219.json parameters.dynamical.yarkovsky.A2: -157.004133 in 1e-15 au/d2, Fenucci+2025"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "101955": {
        "why": "Bennu: the known answer, measured by a spacecraft",
        "spellings": ["101955", "Bennu", "bennu", "(101955) Bennu", "101955 Bennu", "1999 RQ36",
                      "101955 Bennu (1999 RQ36)"],
        "number": 101955, "name": "Bennu", "designation": "1999 RQ36",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 6.995, "jpl-nhats", "NHATS data[4366].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[410].condition_code"),
                f("arc", 7693, "jpl-sbdb", "SBDB data[410].data_arc"),
                f("radar delay observations", 58, "jpl-sbdb", "SBDB data[410].n_del_obs_used"),
                f("radar Doppler observations", 7, "jpl-sbdb", "SBDB data[410].n_dop_obs_used"),
                f("next window", NO_WINDOW, "jpl-nhats", "NHATS data[4366].obs_start is null"),
            ]},
            "size": {"state": "measured", "unchecked": [], "facts": [
                f("diameter", 488.0, "ssodnet",
                  "CARD 101955.json parameters.physical.diameter: 0.488 km -0.019 +0.019, method SPACE, Barnouin+2019",
                  quality="SPACE", lo=469.0, hi=507.0),
                f("diameter", 484.44, "jpl-sbdb", "SBDB data[410].diameter 0.48444 km"),
                f("H", 20.21, "jpl-sbdb", "SBDB data[410].H"),
            ]},
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 4.2968, "lcdb", "LCDB line 22760, PERIOD 4.2968, U 3", quality="3"),
                f("period", 4.296057, "ssodnet", "CARD 101955.json parameters.physical.spins[0].period, Barnouin+2019"),
                f("period", 4.296061, "jpl-sbdb", "SBDB data[410].rot_per"),
            ]},
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("class", "B", "ssodnet", "CARD 101955.json parameters.physical.taxonomy.class, Mahlke+2022"),
                f("class", "B", "jpl-sbdb", "SBDB data[410].spec_B", quality="SMASSII"),
                f("albedo", 0.044, "ssodnet",
                  "CARD 101955.json parameters.physical.albedo: 0.044 -0.002 +0.002, method SPACE",
                  quality="SPACE", lo=0.042, hi=0.046),
            ]},
            # SBDB data[410].A2 is null: JPL's bulk table carries no push value for Bennu.
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -45.2555e-15, "ssodnet",
                  "CARD 101955.json parameters.dynamical.yarkovsky.A2: -45.2555 in 1e-15 au/d2, Fenucci+2024"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2010 NU71": {
        "why": "known-bad upstream size: 1.126 km at H 22.7, from a main-belt table, in both JPL and SsODNet",
        "spellings": ["2010 NU71", "K10N71U"],
        "number": None, "name": None, "designation": "2010 NU71",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 5.733, "jpl-nhats", "NHATS data[957].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 8, "jpl-sbdb", "SBDB data[8100].condition_code"),
                f("arc", 117, "jpl-sbdb", "SBDB data[8100].data_arc"),
            ]},
            # docs/research/verify-coverage.md: "One of the 197 is wrong and should be dropped: 2010 NU71".
            "size": {"state": "prior", "unchecked": [], "facts": [
                f("diameter", 1126.0, "ssodnet",
                  "CARD 2010_NU71.json parameters.physical.diameter: 1.126 km, method NEATM, Masiero+2011",
                  quality="NEATM"),
                f("diameter", 1126.0, "jpl-sbdb", "SBDB data[8100].diameter 1.126 km"),
                f("H", 22.66, "jpl-sbdb", "SBDB data[8100].H"),
            ]},
            "spin": {"state": "prior", "unchecked": [], "facts": []},
            "surface": {"state": "prior", "unchecked": [], "absent": ["class"], "facts": [
                f("albedo", 0.042, "ssodnet", "CARD 2010_NU71.json parameters.physical.albedo: 0.042, Masiero+2011"),
                f("albedo", 0.042, "jpl-sbdb", "SBDB data[8100].albedo"),
            ]},
            "push": {"state": "prior", "unchecked": [], "facts": []},
        },
    },
    # ------------------------------------------------------------------
    "2013 NJ": {
        "why": "two sources disagree by a factor of 100 on its period",
        "spellings": ["2013 NJ", "2013NJ", "K13N00J"],
        "number": None, "name": None, "designation": "2013 NJ",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 10.241, "jpl-nhats", "NHATS data[502].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[10579].condition_code"),
                f("window start", "2026-12-12", "jpl-nhats", "NHATS data[502].obs_start"),
            ]},
            "size": {"state": "prior", "unchecked": [], "absent": ["diameter"], "facts": [
                f("H", 22.02, "jpl-sbdb", "SBDB data[10579].H"),
            ]},
            "spin": {"state": "measured", "unchecked": [],
                     "conflicts": [("250 h", "2.02 h", "Pravec's table", "SsODNet")],
                     "facts": [
                f("period", 250.0, "pravec", "PRAVEC line 2395, period 250., U 3", quality="3"),
                f("period", 250.0, "lcdb", "LCDB line 34923, PERIOD 250., U 2", quality="2"),
                f("period", 2.02, "ssodnet",
                  "CARD 2013_NJ.json parameters.physical.spins[0]: 2.02 h, period_flag 'U=2', Thirouin+2016b",
                  quality="2", lo=1.97, hi=2.07),
                f("period", 250.0, "jpl-sbdb", "SBDB data[10579].rot_per '250.'"),
            ]},
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("class", "Q", "ssodnet", "CARD 2013_NJ.json parameters.physical.taxonomy.class, Mahlke+2022"),
            ]},
            "push": {"state": "prior", "unchecked": [], "facts": []},
        },
    },
    # ------------------------------------------------------------------
    "2023 RA4": {
        "why": "a period that exists only in Pravec's table: 2.35 hours under 5 km/s",
        "spellings": ["2023 RA4", "K23R04A"],
        "number": None, "name": None, "designation": "2023 RA4",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 4.956, "jpl-nhats", "NHATS data[2175].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 3, "jpl-sbdb", "SBDB data[32936].condition_code"),
                f("arc", 261, "jpl-sbdb", "SBDB data[32936].data_arc"),
            ]},
            # First observed in 2023, after the Spitzer surveys ended: the final table has nothing for it.
            "size": {"state": "prior", "unchecked": [], "facts": [
                f("H", 24.68, "jpl-sbdb", "SBDB data[32936].H"),
            ]},
            # CARD 2023_RA4.json has no spins; SBDB data[32936].rot_per is null; not in LCDB.
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 2.3478, "pravec", "PRAVEC line 4335, period 2.3478 +/- 0.0006, U 2",
                  quality="2", lo=2.3472, hi=2.3484),
                f("amplitude", 1.2, "pravec", "PRAVEC line 4335, Ampl. 1.20"),
            ]},
            "surface": {"state": "prior", "unchecked": [], "facts": []},
            "push": {"state": "prior", "unchecked": [], "facts": []},
        },
    },
    # ------------------------------------------------------------------
    "1999 AO10": {
        "why": "a period that exists only in Pravec's table: a secure 11 hours under 6 km/s",
        "spellings": ["1999 AO10", "J99A10O"],
        "number": None, "name": None, "designation": "1999 AO10",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 5.885, "jpl-nhats", "NHATS data[2354].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 1, "jpl-sbdb", "SBDB data[4037].condition_code"),
                f("arc", 9927, "jpl-sbdb", "SBDB data[4037].data_arc"),
            ]},
            "size": {"state": "prior", "unchecked": [], "facts": [
                f("H", 24.32, "jpl-sbdb", "SBDB data[4037].H"),
            ]},
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 11.06, "pravec", "PRAVEC line 4969, period 11.06 +/- 0.01, U 3; remark 'U = 2+ or 3-'",
                  quality="2+", lo=11.05, hi=11.07),
            ]},
            "surface": {"state": "prior", "unchecked": [], "facts": []},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -2.0e-13, "jpl-sbdb", "SBDB data[4037].A2 -2.0e-13, A2_sigma 2.4e-14"),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2001 CQ36": {
        "why": "two independent sizes that agree, a measured and a computed albedo, and a fitted drift",
        "spellings": ["2001 CQ36", "K01C36Q"],
        "number": None, "name": None, "designation": "2001 CQ36",
        "rows": {
            "reach": {"state": "measured", "unchecked": [], "facts": [
                f("delta-v", 5.846, "jpl-nhats", "NHATS data[371].min_dv.dv"),
            ]},
            "tracking": {"state": "measured", "unchecked": [], "facts": [
                f("condition code", 0, "jpl-sbdb", "SBDB data[4239].condition_code"),
                f("window start", "2031-01-30", "jpl-nhats", "NHATS data[371].obs_start"),
                f("window peak brightness", 17.16, "jpl-nhats", "NHATS data[371].obs_mag"),
            ]},
            "size": {"state": "measured", "unchecked": [], "conflicts": [], "facts": [
                f("diameter", 68.0, "ssodnet",
                  "CARD 2001_CQ36.json parameters.physical.diameter: 0.068 km -0.012 +0.011, NEATM, Mueller+2011b",
                  quality="NEATM", lo=56.0, hi=79.0),
                f("diameter", 56.0, "spitzer", "SPITZER line 237: diam 0.056 km, d1sigl -0.01, d1sigu 0.021",
                  lo=46.0, hi=77.0),
                f("H", 22.74, "jpl-sbdb", "SBDB data[4239].H"),
            ]},
            # LCDB line 34385 lists 2001 CQ36 with no period.
            "spin": {"state": "prior", "unchecked": [], "absent": ["period"], "facts": []},
            "surface": {"state": "measured", "unchecked": [], "facts": [
                f("albedo", 0.467, "spitzer", "SPITZER line 237: pv 0.467, pv1sigl -0.224, pv1sigu 0.252",
                  lo=0.243, hi=0.719),
                f("albedo", 0.3682, "ssodnet",
                  "CARD 2001_CQ36.json parameters.physical.albedo: 0.3682, method Computed", quality="Computed"),
            ]},
            "push": {"state": "measured", "unchecked": [], "facts": [
                f("A2", -1.5e-13, "jpl-sbdb", "SBDB data[4239].A2 -1.5e-13, A2_sigma 8.9e-15"),
                f("A2", -148.395e-15, "ssodnet",
                  "CARD 2001_CQ36.json parameters.dynamical.yarkovsky.A2: -148.395 in 1e-15 au/d2, Fenucci+2024"),
            ]},
        },
    },
}


# Objects added after the review of 2026-11-25, each for one row. Kept apart from FIXTURES, whose entries give
# all six rows: a fact here may also carry `kind` and `used`. tests/test_ledger.py reads both.
EXTRA_FIXTURES = {
    # ------------------------------------------------------------------
    "2017 BL6": {
        "why": "a lower limit on the period (LCDB '> 1.1') that JPL repeats as 1.1 h with no limit sign",
        "spellings": ["2017 BL6"],
        "number": None, "name": None, "designation": "2017 BL6",
        "rows": {
            "spin": {"state": "limit", "unchecked": [], "facts": [
                f("period", 1.1, "lcdb", "LCDB line 35699: '> 1.1', U 2-", quality="2-", kind="lower", used=True),
                f("period", 1.1, "jpl-sbdb", "SBDB rot_per 1.1: the same number with no limit sign", kind="value",
                  used=False),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "1999 NW2": {
        "why": "an upper limit on the period (LCDB '< 4.2') that JPL repeats as 4.2 h",
        "spellings": ["1999 NW2"],
        "number": None, "name": None, "designation": "1999 NW2",
        "rows": {
            "spin": {"state": "limit", "unchecked": [], "facts": [
                f("period", 4.2, "lcdb", "LCDB summary: '< 4.2', U 2", quality="2", kind="upper", used=True),
                f("period", 4.2, "jpl-sbdb", "SBDB rot_per 4.2", kind="value", used=False),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "1998 KY26": {
        "why": "the 2023 lightcurve database holds 10.7 min; JPL and the literature card hold 5.35 min from 2025",
        "spellings": ["1998 KY26"],
        "number": None, "name": None, "designation": "1998 KY26",
        "rows": {
            # The newer period, held by two sources, is listed first, so the row rests on it; both stay in use.
            "spin": {"state": "measured", "unchecked": [], "facts": [
                f("period", 0.089193, "ssodnet", "CARD: spins[0].period 0.089193, Santana-Ros+2025b", used=True),
                f("period", 0.089193, "jpl-sbdb", "SBDB rot_per 0.089193", used=True),
                f("period", 0.1784, "lcdb", "LCDB summary: 0.1784, U 3", quality="3", used=True),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2003 LN6": {
        "why": "a Spitzer fit at signal-to-noise 0.9 with a fitted reflectivity of 1.4: on file, not used",
        "spellings": ["2003 LN6"],
        "number": None, "name": None, "designation": "2003 LN6",
        "rows": {
            "size": {"state": "prior", "unchecked": [], "facts": [
                f("diameter", 12.0, "spitzer", "SPITZER: diam 0.012 km, ch2snr 0.9", lo=10.0, hi=14.0, used=False),
            ]},
            "surface": {"state": "prior", "unchecked": [], "facts": [
                f("albedo", 1.402, "spitzer", "SPITZER: pv 1.402, ch2snr 0.9", used=False),
            ]},
        },
    },
    # ------------------------------------------------------------------
    "2008 TC3": {
        "why": "it entered the atmosphere on 7 October 2008; JPL's list still computes a 2041 window for it",
        "spellings": ["2008 TC3"],
        "number": None, "name": None, "designation": "2008 TC3",
        "rows": {
            "tracking": {"state": "measured", "unchecked": [],
                         "absent": ["window start", "window end", "window pointing", "next window"], "facts": [
                f("first observed", "2008-10-06", "jpl-sbdb", "SBDB first_obs"),
            ]},
        },
    },
}


# --------------------------------------------------------------------------
# a stable view of the data for tests

import contextlib
from unittest import mock


@contextlib.contextmanager
def research_cards_only():
    """Build from the research snapshot of SsODNet cards alone.

    data/sources/ssodnet/cards and its journal change while the fetch job runs.
    Inside this block they are left out, so a build depends only on files that
    do not change.
    """
    from longshot import config, ingest
    from longshot.ingest import ssodnet
    nowhere = config.ROOT / "tests" / "_not_a_folder"
    ingest.reset()
    with mock.patch.object(ssodnet, "LIVE_CARDS", nowhere / "cards"), \
            mock.patch.object(ssodnet, "JOURNAL", nowhere / "journal.jsonl"):
        try:
            yield
        finally:
            ingest.reset()
