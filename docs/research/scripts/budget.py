#!/usr/bin/env python3
"""Plain-number physics budget for the 'bring it back' rung.
All arithmetic; inputs are stated in the printout. No network."""
import math
g0 = 9.80665
G = 6.674e-11

def frac(dv_kms, isp):
    return math.exp(-dv_kms * 1000 / (isp * g0))

print("== 1. Tsiolkovsky: fraction of starting mass left after a burn of dv")
for name, isp in (("storable chemical, Isp 320 s", 320), ("LOX/LH2, Isp 450 s", 450),
                  ("Hall thruster, Isp 1800 s", 1800), ("gridded ion / high-power Hall, Isp 3000 s", 3000)):
    print(f"  {name:45s}", "  ".join(f"{dv} km/s: {frac(dv, isp)*100:5.1f}%" for dv in (1, 2, 4, 5, 6, 9.4)))

print()
print("== 2. Round trip split into legs, per 1000 kg in low Earth orbit")
print("   outbound = leave LEO + match the asteroid; back = leave the asteroid; capsule enters directly")
def round_trip(m0, dv_out, dv_back, isp_out, isp_back, dry):
    arrive = m0 * frac(dv_out, isp_out)          # dry + return propellant
    r = 1 / frac(dv_back, isp_back)              # mass ratio of the return burn
    # arrive = dry + P ; (dry + L + P) = r (dry + L)  ->  L = (arrive - r*dry)/(r-1)
    L = (arrive - r * dry) / (r - 1)
    return arrive, L
for total, out, back in ((4, 3.5, 0.5), (5, 4.2, 0.8), (6, 4.8, 1.2)):
    for label, io, ib in (("chemical 320 s throughout", 320, 320), ("launcher stage 450 s out, 320 s back", 450, 320)):
        arr, _ = round_trip(1000, out, back, io, ib, 0)
        row = []
        for dry in (100, 150, 200, 250):
            _, L = round_trip(1000, out, back, io, ib, dry)
            row.append(f"dry {dry}: {L:6.0f} kg" if L > 0 else f"dry {dry}:   none")
        print(f"  total {total} km/s ({out}+{back}), {label:38s} arrives {arr:4.0f} kg | payload sent home: " + "; ".join(row))

print()
print("== 3. Electric propulsion from LEO (low thrust: spiral out costs more dv than an impulsive burn)")
print("   Keck 2012 case as published: 6.6 km/s LEO to lunar assist + 2.8 km/s to asteroid + 0.17 km/s back, Isp 3000 s")
m0 = 18000.0
m1 = m0 * frac(6.6 + 2.8, 3000)
print(f"   18,000 kg in LEO -> {m1:,.0f} kg at the asteroid (ideal); xenon used outbound {m0-m1:,.0f} kg")
for mast in (250e3, 500e3, 1300e3):
    r = 1 / frac(0.17, 3000)
    prop = (m1 + mast) * (1 - 1 / r)
    print(f"   pushing a {mast/1000:,.0f} t rock through 0.17 km/s needs about {prop:,.0f} kg more xenon")
print("   same rock through 1.0 km/s:", ", ".join(f"{m/1000:,.0f} t -> {(m1+m)*(1-frac(1.0,3000)):,.0f} kg xenon" for m in (250e3, 500e3, 1300e3)))

print()
print("== 4. Demonstrated and proposed 'mass returned per mass launched'")
rows = [
    ("Hayabusa2 (flown)", 5.424e-3, 609, "launch mass 609 kg [R]"),
    ("OSIRIS-REx (flown)", 0.1216, 2110, "launch mass 2,110 kg [R]"),
    ("ARM reference design 2017 (cancelled)", 13535, 9995, "boulder to lunar orbit; spacecraft mass at launch to near-escape"),
    ("Keck 2012 study (paper)", 500000, 18000, "whole 7 m asteroid to lunar orbit; mass in LEO"),
    ("Karman+ Corvus (stated)", 1000, 700, "low end: 1,000 kg water to GEO"),
    ("Karman+ Corvus (stated)", 5000, 700, "high end: 5,000 kg water to GEO"),
    ("Karman+ Roc (stated)", 100000, 7000, "whole asteroid up to 100 t"),
    ("TransAstra APIS 2015 (NIAC concept)", 100000, 13150, "100 t water; Falcon 9 v1.1 LEO capacity 13,150 kg [R]"),
]
for name, ret, launched, note in rows:
    print(f"   {name:40s} {ret:>12,.4f} kg / {launched:>7,} kg = {ret/launched:10.3g}   ({note})")
print(f"   orders of magnitude between OSIRIS-REx and a ratio of 1: {math.log10(1/(0.1216/2110)):.1f}; and a ratio of 28: {math.log10(28/(0.1216/2110)):.1f}")

print()
print("== 5. Cost per gram returned")
for name, cost, grams, note in (
    ("OSIRIS-REx", 1.02e9, 121.6, "USD, not inflation-adjusted, Planetary Society"),
    ("Hayabusa2", 28.9e9, 5.424, "JPY, plan-stage total project cost"),
    ("Apollo (then-year)", 25.8e9, 382000, "USD 1960-1973"),
    ("Apollo (2025 dollars)", 309e9, 382000, "USD, Planetary Society adjustment"),
):
    print(f"   {name:24s} {cost:14,.0f} / {grams:>10,.3f} g = {cost/grams:16,.0f} per gram   ({note})")
print("   Hayabusa2 in dollars at 110 / 150 yen per dollar:", f"{28.9e9/5.424/110:,.0f} / {28.9e9/5.424/150:,.0f} per gram")
print("   Hayabusa: 20e9 yen over under 1 mg -> more than", f"{20e9/1:,.0f} yen per milligram")

print()
print("== 6. Gravity and spin on small bodies (uniform sphere)")
def body(D, rho, P_s):
    R = D / 2
    g = 4 / 3 * math.pi * G * rho * R
    vesc = math.sqrt(8 / 3 * math.pi * G * rho) * R
    w = 2 * math.pi / P_s
    return g, vesc, w * w * R / g, w * R
for D, rho, P, lab in ((15, 2000, 600, "15 m, 10 min"), (15, 2000, 3600, "15 m, 1 h"), (60, 2000, 36000, "60 m, 10 h"),
                       (60, 2000, 3600, "60 m, 1 h"), (6, 2000, 120, "6 m, 2 min"), (6, 2000, 3600, "6 m, 1 h"),
                       (18, 2700, 27.9 * 60, "Kamo'oalewa 18 m, 27.9 min"), (490, 1190, 4.3 * 3600, "Bennu 490 m, 4.3 h")):
    g, v, ratio, vs = body(D, rho, P)
    m = rho * math.pi / 6 * D ** 3
    print(f"   {lab:28s} rho {rho}: mass {m/1000:10,.0f} t  g {g:.2e} m/s2 ({g/9.81:.1e} of Earth)  escape {v*100:5.2f} cm/s  equator speed {vs*100:6.2f} cm/s  centrifugal/gravity {ratio:8.1f}")
for rho in (1200, 2000, 3300, 7800):
    print(f"   spin period at which the equator goes weightless, rho {rho}: {math.sqrt(3*math.pi/(G*rho))/3600:.2f} h")
print("   mass of a sphere, by diameter (rho 2000):", ", ".join(f"{D} m: {2000*math.pi/6*D**3/1000:,.0f} t" for D in (5, 6, 7, 10, 15, 30, 60)))
print("   PGM in 1 t of rock at 40.78 ppm (median iron meteorite, 100% metal):", 40.78, "g;  at 1 ppm:", 1, "g")

print()
print("== 7. De-spin: angular momentum of a uniform sphere vs the Keck 2012 design case (1.7e6 N m s, 306 kg propellant)")
for D, rho, P in ((6, 2000, 120), (6, 2000, 30), (7, 2800, 60), (10, 2000, 60), (15, 2000, 600), (15, 2000, 60)):
    M = rho * math.pi / 6 * D ** 3
    I = 0.4 * M * (D / 2) ** 2
    Lz = I * 2 * math.pi / P
    # propellant with 2 m arm, Isp 287 s: impulse = L / arm ; m = impulse / (Isp g0)
    prop = Lz / 2.0 / (287 * g0)
    print(f"   {D} m, rho {rho}, period {P:4d} s: mass {M/1000:7,.0f} t, L = {Lz:10.3g} N m s ({Lz/1.7e6*100:6.1f}% of Keck case), propellant at 2 m arm about {prop:7.1f} kg")
print()
print("== 8. Scale gaps (orders of magnitude)")
lg = math.log10
print(f"   121.6 g -> 1 tonne: {lg(1e6/121.6):.1f}; -> 100 t: {lg(1e8/121.6):.1f}; -> 1000 t: {lg(1e9/121.6):.1f}")
print(f"   OSIRIS-REx $/kg {1.02e9/0.1216:,.0f} vs platinum $41,636/kg: {lg(1.02e9/0.1216/41636):.1f}; vs water at $3,000/kg: {lg(1.02e9/0.1216/3000):.1f}; vs $500/kg: {lg(1.02e9/0.1216/500):.1f}")
print(f"   all asteroid material returned: {121.6+5.424:.1f} g; summed mission cost USD approx: {1.02e9 + 28.9e9/130 + 20e9/130:,.0f} at 130 yen/USD -> {(1.02e9 + 48.9e9/130)/(127.0):,.0f} per gram")
print(f"   rock to process for 1 kg PGM at 40.78 ppm: {1/40.78e-6/1000:,.1f} t; at 5 ppm: {1/5e-6/1000:,.0f} t")
print(f"   years launch to return: Hayabusa {(2010+164/365)-(2003+129/365):.1f}, Hayabusa2 {(2020+340/365)-(2014+337/365):.1f}, OSIRIS-REx {(2023+267/365)-(2016+252/365):.1f}, Tianwen-2 planned {(2027+333/365)-(2025+148/365):.1f}")
