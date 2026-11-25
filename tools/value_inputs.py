"""Derive the constants in method/v0_1/value.toml and ladder.toml from sourced inputs.

Every number in those two files that is not copied from a source is printed here.
No network. Standard library only. Deterministic.

Usage: uv run python tools/value_inputs.py

Typed inputs and where each was read:
- Horan et al. 2003, Chem. Geol. 196, 5, Table 1 (ppb): saved copy
  data/research/downloads/value/oc/horan2003.txt, read 2026-11-24.
- USGS Mineral Commodity Summaries 2026, platinum-group metals, "Price, dollars
  per troy ounce", 2021-2025: saved copy
  data/research/downloads/value/usgs/mcs2026-platinum-group.txt, read 2026-11-24.
- Umicore 10am prices, 20 November 2026; IPA/SFA 2025 mine supply; Cannon et al.
  2023 Table 2: as confirmed in docs/research/verify-value-inputs.md.
- The class and reflectivity table: data/research/out-prior-null/labels.csv
  (built by docs/research/scripts/pn_build_labels.py on 2026-11-21).
"""
import csv, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS = os.path.join(ROOT, "data/research/out-prior-null/labels.csv")
G_PER_OZT = 31.1034768
PRICED = ("Pt", "Pd", "Rh", "Ir", "Ru")
SIX = ("Os", "Ir", "Ru", "Pt", "Pd", "Rh")

# ---- Horan et al. 2003 Table 1: Os, Ir, Ru, Pt, Pd in ppb. Rh was not measured. ----
RH_PER_IR = 0.30  # CI ratio 0.141 / 0.470 (Lodders 2003, recalled in value-inputs.md 1.2)
HORAN = {
    "H": {
        "Sharps": (1072, 980.6, 1256, 1702, 871.6),
        "Ceniceros": (491.5, 464.9, 726.0, 908.9, 590.9),
        "Ceniceros (replicate)": (546.9, 505.8, 778.8, 1021, 659.1),
        "Dhajala": (920.5, 825.1, 1243, 1728, 943.5),
        "Bremervoerde": (743.6, 660.4, 1007, 1361, 784.4),
        "Zag": (920.4, 809.6, 1160, 1617, 816.5),
        "Forest Vale": (809.8, 730.6, 1105, 1504, 812.6),
        "Ochansk": (819.5, 735.3, 1141, 1568, 853.9),
        "Forest City": (860.4, 762.0, 1188, 1611, 912.7),
        "Rose City (replicate)": (975.1, 843.3, 1364, 1842, 1009),
        # Rose City's first aliquot (Ir 111.7 ppb, Os not determined) is left out:
        # it has no osmium value and the paper treats it as unrepresentative.
    },
    "L": {
        "Farmington": (497.3, 441.8, 606.9, 867.1, 486.1),
        "Chico": (696.3, 627.8, 970.1, 1295, 624.8),
        "Chico (replicate)": (638.6, 594.2, 919.5, 1212, 599.1),
    },
    "LL": {
        "Semarkona": (288.6, 260.6, 400.6, 513.5, 390.8),
        "Semarkona (replicate)": (334.2, 309.2, 484.6, 635.3, 442.7),
        "Chainpur": (351.2, 316.7, 537.4, 672.3, 346.0),
    },
    "CI": {
        "Orgueil": (459.2, 455.6, 651.5, 858.3, 562.9),
        "Orgueil (replicate)": (456.9, 432.3, 647.6, 874.3, 573.5),
        "Ivuna": (428.8, 406.0, 608.7, 829.4, 528.5),
    },
    "CM": {
        "Murchison": (580.0, 557.7, 740.8, 1043, 618.9),
        "Murray": (661.7, 613.1, 851.0, 1067, 578.0),
        "Mighei": (569.3, 544.2, 791.4, 1041, 576.8),
    },
    "EH": {
        "Kota-Kota": (593.0, 545.6, 850.7, 1116, 923.2),
        "Kota-Kota (replicate)": (614.0, 563.4, 845.8, 1146, 871.3),
        "Indarch": (625.5, 566.9, 855.9, 1162, 891.0),
        "Adhi Kot": (501.0, 468.7, 734.1, 962.7, 835.2),
        "St. Sauveur": (666.4, 610.5, 907.4, 1246, 919.1),
        "St. Mark's": (604.9, 555.7, 838.9, 1126, 887.1),
    },
    "EL": {
        "Daniel's Kuil": (827.9, 748.8, 1168, 1528, 920.8),
        "Yilmia": (710.9, 642.9, 929.0, 1262, 887.7),
        "Yilmia (replicate)": (861.3, 781.8, 1090, 1544, 957.1),
        "Blithfield": (276.7, 253.5, 366.7, 502.8, 360.0),
        "Pillistfer": (725.5, 672.5, 1021, 1447, 907.6),
    },
}

# ---- USGS MCS 2026: annual average prices, dollars per troy ounce. 2025 is an estimate. ----
USGS = {
    "Pd": {2021: 2419.18, 2022: 2133.81, 2023: 1351.66, 2024: 994.90, 2025: 1100.0},
    "Pt": {2021: 1094.31, 2022: 966.54, 2023: 973.00, 2024: 960.70, 2025: 1200.0},
    "Ir": {2021: 5158.40, 2022: 4581.93, 2023: 4672.78, 2024: 4810.40, 2025: 4400.0},
    "Rh": {2021: 20254.10, 2022: 15585.00, 2023: 6660.58, 2024: 4660.44, 2025: 5800.0},
    "Ru": {2021: 576.12, 2022: 577.02, 2023: 466.49, 2024: 451.02, 2025: 690.0},
}
UMICORE_2026_11_20 = {"Pt": 1336.0, "Pd": 912.0, "Rh": 8950.0, "Ir": 10200.0, "Ru": 1900.0}
SUPPLY_T_2025 = {"Pt": 178.0, "Pd": 197.0, "Rh": 22.0, "Ir": 7.0, "Ru": 30.0}  # IPA/SFA, May 2026
CAP_SHARE = 0.10
CI = {"Ru": 0.692, "Rh": 0.141, "Pd": 0.588, "Os": 0.486, "Ir": 0.470, "Pt": 1.004}  # Lodders 2003, ppm, recalled
CANNON = [(0.0, 6.0), (0.1, 14.70), (0.2, 20.75), (0.3, 27.05), (0.4, 34.77), (0.5, 40.78),
          (0.6, 52.88), (0.7, 63.48), (0.8, 91.23), (0.9, 107.86), (1.0, 230.0)]
AVCE_IR_PPM, AVCE_TOTAL_PPM = 59.5, 230.0  # Cannon et al. 2023, citing Wasson et al. 2007


def six(v):
    os_, ir, ru, pt, pd = v
    return {"Os": os_, "Ir": ir, "Ru": ru, "Pt": pt, "Pd": pd, "Rh": RH_PER_IR * ir}


def per_kg(per_ozt):
    return per_ozt * 1000.0 / G_PER_OZT


def mix_price(mix, prices_kg):
    """Dollars per kg of mixed platinum-group metal. Osmium has no price."""
    return sum(mix.get(el, 0.0) * prices_kg[el] for el in PRICED)


def iron_mix(ir_share, with_rh=True):
    """Element shares of the platinum-group metal in iron for a given iridium share.

    Osmium follows iridium at the CI ratio. The rest is platinum, ruthenium and
    palladium (and rhodium unless with_rh is False) in CI proportions to each other.
    """
    os_share = ir_share * CI["Os"] / CI["Ir"]
    rest = 1.0 - ir_share - os_share
    others = ("Pt", "Ru", "Pd", "Rh") if with_rh else ("Pt", "Ru", "Pd")
    tot = sum(CI[e] for e in others)
    mix = {e: rest * CI[e] / tot for e in others}
    mix.update({"Ir": ir_share, "Os": os_share})
    mix.setdefault("Rh", 0.0)
    return mix


def quantile(sorted_v, q):
    """Nearest-rank quantile: the value at index ceil(q*n) - 1."""
    n = len(sorted_v)
    return sorted_v[min(n - 1, max(0, math.ceil(q * n) - 1))]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    out = sys.stdout.write

    out("== 1. Platinum-group metal in chondrites (Horan et al. 2003 Table 1; Rh = 0.30 x Ir) ==\n")
    group_mix = {}
    for grp, mets in HORAN.items():
        totals, fracs = [], {e: [] for e in SIX}
        for name, v in mets.items():
            s = six(v)
            t = sum(s.values())
            totals.append((t / 1000.0, name))
            for e in SIX:
                fracs[e].append(s[e] / t)
        lo, hi = min(totals), max(totals)
        mix = {e: sum(fracs[e]) / len(fracs[e]) for e in SIX}
        group_mix[grp] = mix
        out(f"{grp:2s} n={len(mets):2d} total six: {lo[0]:.2f} ({lo[1]}) to {hi[0]:.2f} ({hi[1]}) ppm\n")
        out("   mean element shares: " + ", ".join(f"{e} {mix[e]:.4f}" for e in SIX) + "\n")
    for label, grps in (("ordinary chondrite (H, L, LL)", ("H", "L", "LL")),
                        ("enstatite chondrite (EH, EL)", ("EH", "EL")),
                        ("carbonaceous (CI, CM)", ("CI", "CM"))):
        rows = [six(v) for g in grps for v in HORAN[g].values()]
        mix = {e: sum(r[e] / sum(r.values()) for r in rows) / len(rows) for e in SIX}
        group_mix[label] = mix
        out(f"{label}: " + ", ".join(f"{e} {mix[e]:.4f}" for e in SIX) + f" (sum {sum(mix.values()):.4f})\n")
    ee = [sum(six(v).values()) / 1000.0 for g in ("EH", "EL") for v in HORAN[g].values()]
    cc = [sum(six(v).values()) / 1000.0 for g in ("CI", "CM") for v in HORAN[g].values()]
    out(f"enstatite chondrite range {min(ee):.2f}-{max(ee):.2f} ppm; carbonaceous CI+CM range {min(cc):.2f}-{max(cc):.2f} ppm\n")

    out("\n== 2. Prices (USGS MCS 2026, annual averages 2021-2025, $/troy oz -> $/kg) ==\n")
    lo_p, mean_p, hi_p = {}, {}, {}
    for el in PRICED:
        ys = USGS[el]
        lo_y = min(ys, key=ys.get)
        hi_y = max(ys, key=ys.get)
        lo_p[el], hi_p[el] = per_kg(ys[lo_y]), per_kg(ys[hi_y])
        mean_p[el] = per_kg(sum(ys.values()) / len(ys))
        out(f"{el}: low {ys[lo_y]:9.2f} ({lo_y}) = {lo_p[el]:9.0f} $/kg | mean {sum(ys.values())/len(ys):9.2f} = {mean_p[el]:9.0f} $/kg"
            f" | high {ys[hi_y]:9.2f} ({hi_y}) = {hi_p[el]:9.0f} $/kg | 20 Nov 2026 quote {UMICORE_2026_11_20[el]:8.0f} = {per_kg(UMICORE_2026_11_20[el]):9.0f} $/kg\n")
    quote = {el: per_kg(UMICORE_2026_11_20[el]) for el in PRICED}
    oc = group_mix["ordinary chondrite (H, L, LL)"]
    out("price of the ordinary-chondrite mix, $ per kg of the six metals (osmium unpriced):\n")
    for y in range(2021, 2026):
        py = {el: per_kg(USGS[el][y]) for el in PRICED}
        out(f"   {y}: {mix_price(oc, py):8.0f}\n")
    m_lo, m_mean, m_hi, m_q = (mix_price(oc, p) for p in (lo_p, mean_p, hi_p, quote))
    out(f"   low band {m_lo:.0f}; five-year mean {m_mean:.0f}; high band {m_hi:.0f}; ratio high/low {m_hi/m_lo:.2f}\n")
    out(f"   20 Nov 2026 quotes {m_q:.0f} = {m_q/m_hi:.2f} x the high band, {m_q/m_mean:.2f} x the five-year mean\n")
    for tag, p in (("low", lo_p), ("high", hi_p), ("20 Nov 2026", quote)):
        out(f"   iridium share of the dollar figure, {tag}: {oc['Ir']*p['Ir']/mix_price(oc, p):.2f}; rhodium {oc['Rh']*p['Rh']/mix_price(oc, p):.2f}\n")
    out(f"   osmium share of the mass: {oc['Os']:.3f}\n")

    out("\n== 3. Market-absorption cap: 10% of 2025 world mine supply (IPA/SFA) ==\n")
    tot_lo = tot_hi = 0.0
    for el in PRICED:
        cap_kg = SUPPLY_T_2025[el] * 1000.0 * CAP_SHARE
        tot_lo += cap_kg * lo_p[el]
        tot_hi += cap_kg * hi_p[el]
        out(f"{el}: cap {cap_kg:8.0f} kg = ${cap_kg*lo_p[el]/1e9:.2f}-{cap_kg*hi_p[el]/1e9:.2f} billion\n")
    out(f"all five: ${tot_lo/1e9:.2f}-{tot_hi/1e9:.2f} billion\n")
    for grp, ppm in (("H", 6.29), ("LL", 1.93)):
        mix = group_mix[grp]
        rock_t = min(SUPPLY_T_2025[el] * 1000.0 * CAP_SHARE / (ppm * mix[el] / 1000.0) for el in PRICED)
        first = min(PRICED, key=lambda el: SUPPLY_T_2025[el] / mix[el])
        d = (rock_t * 1000.0 / 2500.0 * 6.0 / math.pi) ** (1.0 / 3.0)
        out(f"first cap reached for {grp} rock at {ppm} ppm: {first} at {rock_t/1e6:.2f} Mt, a {d:.0f} m body at 2,500 kg/m3\n")
    for ir_share in (0.13, 0.26):
        ppm = 40.78 * 0.75
        rock_t = SUPPLY_T_2025["Ir"] * 1000.0 * CAP_SHARE / (ppm * ir_share / 1000.0)
        d = (rock_t * 1000.0 / 4500.0 * 6.0 / math.pi) ** (1.0 / 3.0)
        out(f"iridium cap reached for an iron-rich body (40.78 ppm x 0.75 metal, iridium share {ir_share}, 4,500 kg/m3): {rock_t:,.0f} t, {d:.0f} m\n")

    out("\n== 4. Platinum-group metal in iron: the two bracketing mixes (a judgement, not bounds) ==\n")
    out(f"Avce: iridium {AVCE_IR_PPM} of about {AVCE_TOTAL_PPM} ppm = {AVCE_IR_PPM/AVCE_TOTAL_PPM:.3f} of the total\n")
    ci_tot = sum(CI.values())
    out("CI (chondritic) shares: " + ", ".join(f"{e} {CI[e]/ci_tot:.3f}" for e in SIX) + "\n")
    m_low, m_mid, m_high = iron_mix(0.0, with_rh=False), iron_mix(0.13), iron_mix(0.26)
    for tag, m, p in (("low: no iridium, osmium or rhodium", m_low, lo_p),
                      ("central: iridium 0.13", m_mid, mean_p),
                      ("high: iridium 0.26 (Avce)", m_high, hi_p)):
        out(f"{tag}: " + ", ".join(f"{e} {m[e]:.4f}" for e in SIX) + f" -> ${mix_price(m, p):,.0f} per kg\n")
    out(f"   Pt + Ru share, central mix: {m_mid['Pt']+m_mid['Ru']:.2f} (Cannon: 'more than half')\n")
    out(f"   high over low: {mix_price(m_high, hi_p) / mix_price(m_low, lo_p):.2f}\n")
    # The two mixes are a judgement, not bounds. Two mixes the paper's sentences also allow:
    rh = RH_PER_IR * 0.26                      # rhodium at the chondritic ratio to iridium; the paper says it falls below
    os_share = 0.26 * CI["Os"] / CI["Ir"]
    rest = 1.0 - 0.26 - os_share - rh
    tot3 = CI["Pt"] + CI["Ru"] + CI["Pd"]
    dearer = {"Ir": 0.26, "Os": os_share, "Rh": rh, "Pt": rest * CI["Pt"] / tot3, "Ru": rest * CI["Ru"] / tot3, "Pd": rest * CI["Pd"] / tot3}
    cheaper = {"Pt": CI["Pt"] / (CI["Pt"] + CI["Ru"]), "Ru": CI["Ru"] / (CI["Pt"] + CI["Ru"])}
    out(f"   outside the bracket: iridium 0.26 with rhodium at the chondritic ratio to iridium: ${mix_price(dearer, hi_p):,.0f} per kg at the high prices "
        f"({mix_price(dearer, hi_p) / mix_price(m_high, hi_p):.2f} x the high mix)\n")
    out(f"   outside the bracket: platinum and ruthenium alone, in CI proportions: ${mix_price(cheaper, lo_p):,.0f} per kg at the low prices "
        f"({mix_price(cheaper, lo_p) / mix_price(m_low, lo_p):.2f} x the low mix)\n")
    out(f"   chondritic mix at the same three price sets: ${mix_price({e: CI[e]/ci_tot for e in SIX}, lo_p):,.0f}, "
        f"${mix_price({e: CI[e]/ci_tot for e in SIX}, mean_p):,.0f}, ${mix_price({e: CI[e]/ci_tot for e in SIX}, hi_p):,.0f} per kg\n")

    out("\n== 5. Water fraction and spin limits ==\n")
    out("water if hydrated: uniform 1.9-10.5 wt% (CM, Lee et al. 2023); Ryugu 6.84, Bennu at most 7.5-8.5 fall inside\n")
    G = 6.674e-11
    for rho in (1200, 2000, 3300, 7900):
        p = math.sqrt(3 * math.pi / (G * rho)) / 3600.0
        out(f"spin at which the equator's outward pull equals gravity, {rho} kg/m3: {p:.2f} h\n")

    out("\n== 6. What has been brought back: arithmetic for ladder.toml ==\n")
    g = 121.6
    out(f"OSIRIS-REx: $1.02 billion / {g} g = ${1.02e9/g/1e6:.2f} million per gram; $1.16 billion / {g} g = ${1.16e9/g/1e6:.2f} million per gram\n")
    out(f"all three samples: {g} + 5.424 + under 0.001 = {g+5.424:.1f} g\n")
    out(f"largest sample to one tonne: {math.log10(1e6/g):.2f} orders of magnitude; to 100 t: {math.log10(1e8/g):.2f}; to 500 t: {math.log10(5e8/g):.2f}\n")
    pt_lo, pt_hi = min(USGS['Pt'].values()), max(USGS['Pt'].values())
    out(f"{g} g of pure platinum at 2021-2025 yearly averages (${pt_lo:.0f}-{pt_hi:.0f}/oz): ${g/G_PER_OZT*pt_lo:,.0f}-{g/G_PER_OZT*pt_hi:,.0f}\n")
    out(f"one tonne is {1e6/g:,.0f} times the largest sample; 13,535 kg is {13535e3/g:,.0f} times; 500 t is {5e8/g:,.0f} times\n")
    out(f"{g} g of iron meteorite at Cannon's 10th and 90th percentile grades (14.70, 107.86 ppm) holds "
        f"{g*14.70e-6*1000:.1f} to {g*107.86e-6*1000:.1f} mg of platinum-group metal\n")
    for nm, d_m, p_h in (("Itokawa", 330, 12.132), ("Ryugu", 896, 7.633), ("Bennu", 484, 4.296)):
        out(f"   {nm}: {d_m} m, {p_h} h\n")
    out(f"outward pull over gravity at the equator, Kamo'oalewa (27.9 min): "
        f"{3*math.pi/(G*3300*(27.9*60)**2):.0f} at 3,300 kg/m3, {3*math.pi/(G*2700*(27.9*60)**2):.0f} at 2,700, {3*math.pi/(G*1200*(27.9*60)**2):.0f} at 1,200\n")
    out(f"2022 OB5 (92.5 s): {3*math.pi/(G*3300*92.5**2):,.0f} at 3,300 kg/m3 to {3*math.pi/(G*1200*92.5**2):,.0f} at 1,200\n")

    out("\n== 7. Class, reflectivity and the 'other' class (project label table) ==\n")
    if not os.path.exists(LABELS):
        out(f"not found: {LABELS} (unpack data/research-data-2026-11-21.tar.zst)\n")
        return
    rows = list(csv.DictReader(open(LABELS, newline="")))
    nh = [r for r in rows if r["nhats"] == "1" and r["tax4"]]
    for label, sub in (("reachable (NHATS) with a class", nh),
                       ("reachable, H >= 24", [r for r in nh if (fnum(r["H"]) or 0) >= 24])):
        n = len(sub)
        out(f"{label}: n={n}: " + ", ".join(f"{c} {sum(r['tax4']==c for r in sub)/n:.3f}" for c in "SCXO") + "\n")
    out("Spitzer reflectivity, a < 2 au, by class (quantile table for the reference draw):\n")
    qs = (0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99)
    for c in "SCXO":
        v = sorted(fnum(r["alb_spitzer"]) for r in rows
                   if r["tax4"] == c and fnum(r["alb_spitzer"]) and (fnum(r["a"]) or 9) < 2)
        n = len(v)
        dark = sum(x < 0.10 for x in v) / n
        mid = sum(0.10 <= x <= 0.30 for x in v) / n
        out(f"{c}: n={n} under 0.10: {dark:.3f}; 0.10-0.30: {mid:.3f}; over 0.30: {1-dark-mid:.3f}\n")
        out("   q " + " ".join(f"{q:g}" for q in qs) + "\n")
        out("   v " + ", ".join(f"{quantile(v, q):.3f}" for q in qs) + "\n")
    allv = sorted(fnum(r["alb_spitzer"]) for r in rows if fnum(r["alb_spitzer"]) and (fnum(r["a"]) or 9) < 2)
    out(f"all Spitzer a < 2 au: n={len(allv)}, under 0.10: {sum(x < 0.10 for x in allv)/len(allv):.3f}, middle value {quantile(allv, 0.5):.3f}\n")
    letters = {}
    for r in rows:
        if r["tax4"] != "O" or (fnum(r["a"]) or 9) >= 2:
            continue
        m = dict(p.split("=", 1) for p in r["tax_all"].split("|") if "=" in p)
        lab = m.get(r["tax4_src"], "?").rstrip(":")
        letters[lab] = letters.get(lab, 0) + 1
    n = sum(letters.values())
    out(f"'other' class, a < 2 au, n={n}: " + ", ".join(f"{k} {letters[k]} ({letters[k]/n:.2f})" for k in sorted(letters, key=lambda k: (-letters[k], k))) + "\n")
    # Z is the extremely red class of Mahlke et al. 2022, redder than D: primitive, not differentiated.
    grp = {"differentiated (V, A, O)": "VAO", "chondritic, metal uncertain (K, L, R)": "KLR", "dark primitive (D, T, Z)": "DTZ"}
    for label, ls in grp.items():
        k = sum(letters.get(x, 0) for x in ls)
        out(f"   {label}: {k} ({k/n:.2f})\n")


if __name__ == "__main__":
    main()
