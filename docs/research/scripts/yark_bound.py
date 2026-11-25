#!/usr/bin/env python3
"""Linear-theory Yarkovsky: maximum of the thermal function and density upper bound.

Linear spherical theory (Vokrouhlicky 1998, 1999; Vokrouhlicky et al. 2015 Asteroids IV):
  transverse accel (diurnal)  a_t = (4/9) (1-A) Phi(r) * F(R', Theta) * cos(gamma)
  Phi(r) = pi R^2 S(r) / (m c) = 3 S(r) / (2 D rho c),  S(r) = L_sun / (4 pi r^2)
  F(R', Theta) = kappa1 Theta / (1 + 2 kappa2 Theta + kappa3 Theta^2)
  large-body limit kappa1=kappa2=kappa3=1/2 -> F = 0.5 Theta / (1 + Theta + 0.5 Theta^2), max 0.2071 at Theta=sqrt(2)
Finite-size F computed from the complex amplitude (A+iB)/(C+iD) of Vokrouhlicky (1999).
"""
import cmath
import math

L_SUN = 3.828e26      # W
C_LIGHT = 2.99792458e8
AU = 1.495978707e11   # m
DAY = 86400.0
GM_SUN = 1.32712440018e20
SIGMA = 5.670374e-8


def F_finite(x, theta):
    """|E sin(delta)|/(1+lambda) with x = sqrt(2) R' and lambda = Theta / x."""
    lam = theta / x
    ex = math.exp(x)
    cx, sx = math.cos(x), math.sin(x)
    A = -(x + 2) - ex * ((x - 2) * cx - x * sx)
    B = -x - ex * (x * cx + (x - 2) * sx)
    k = lam / (1 + lam)
    C = A + k * (3 * (x + 2) + ex * (3 * (x - 2) * cx + x * (x - 3) * sx))
    Dd = B + k * (x * (x + 3) - ex * (x * (x - 3) * cx - 3 * (x - 2) * sx))
    z = complex(A, B) / complex(C, Dd)
    return -z.imag / (1 + lam)


def F_large(theta):
    return 0.5 * theta / (1 + theta + 0.5 * theta * theta)


def scan():
    print("== check large-body limit ==")
    for th in (0.1, 1.0, math.sqrt(2), 3.0, 10.0, 100.0):
        print(f"  Theta={th:8.3f}  F_large={F_large(th):.5f}  F_finite(x=40)={F_finite(40.0, th):.5f}")
    print("== global maximum of F over (R', Theta) ==")
    best = (0, None, None)
    rows = []
    for i in range(0, 241):
        x = 10 ** (-1.5 + i * (3.0 / 240))  # 0.03 .. 30
        bm = (0, None)
        for j in range(0, 401):
            th = 10 ** (-3 + j * (6.0 / 400))
            try:
                f = F_finite(x, th)
            except OverflowError:
                continue
            if f > bm[0]:
                bm = (f, th)
            if f > best[0]:
                best = (f, x, th)
        rows.append((x, bm))
    for x, bm in rows[::20]:
        print(f"  R'={x/math.sqrt(2):8.3f}  max_F={bm[0]:.5f} at Theta={bm[1]:.3g}")
    print(f"  GLOBAL max F={best[0]:.5f} at R'={best[1]/math.sqrt(2):.3f}, Theta={best[2]:.3f}")
    return best[0]


def a2_max_coeff():
    """A2_max [au/d^2] = K * (1-A) / (D[m] * rho[kg/m3]) for F=Fmax=0.2071, |cos gamma|=1."""
    fmax = F_large(math.sqrt(2))
    # a_t at r: (4/9) * (1-A) * 3 S /(2 D rho c) * F ; S = L/(4 pi r^2)
    k_si = (4.0 / 9.0) * 3.0 * L_SUN / (2.0 * 4.0 * math.pi * C_LIGHT) * fmax  # m^3 s^-2 * (kg m^-2) -> a_t r^2 D rho
    k = k_si * DAY ** 2 / AU ** 3
    return k, fmax


def srp_coeff():
    """A1 [au/d^2] = K1 * C_R * AMR[m2/kg];  AMR = 3/(2 rho D) for sphere."""
    k_si = L_SUN / (4.0 * math.pi * C_LIGHT)  # N m^2 /m^2 -> accel*r^2 per (m2/kg)
    return k_si * DAY ** 2 / AU ** 3


def dadt_from_a2(a2, a_au, e):
    n = math.sqrt(GM_SUN / (a_au * AU) ** 3) * DAY  # rad/day
    return 2 * a2 / (n * a_au ** 2 * (1 - e * e)) * 365.25e6 * 1e4  # 1e-4 au/Myr


def diam_from_H(H, pv):
    return 1329e3 * 10 ** (-H / 5.0) / math.sqrt(pv)


def theta(gamma_ti, P_s, r_au, A=0.1, eps=0.9):
    S = L_SUN / (4 * math.pi * (r_au * AU) ** 2)
    Tss = ((1 - A) * S / (eps * SIGMA)) ** 0.25
    return gamma_ti * math.sqrt(2 * math.pi / P_s) / (eps * SIGMA * Tss ** 3), Tss


if __name__ == "__main__":
    gmax = scan()
    K, fmax = a2_max_coeff()
    print(f"\nF_max(large body) = {fmax:.5f};  xi_max = (4/9)*F_max = {4/9*fmax:.5f} (times (1-A))")
    print(f"A2_max [au/d^2] = {K:.4e} * (1-A) / (D[m] * rho[kg/m^3])")
    print(f"=> rho_max [kg/m^3] = {K:.4e} * (1-A) / (D[m] * |A2| [au/d^2])")
    K1 = srp_coeff()
    print(f"A1 [au/d^2] = {K1:.4e} * C_R * AMR[m^2/kg]   (AMR = 1.5/(rho D) for a sphere)")
    print(f"max |A2|/A1 for purely radiative forces (sphere, C_R=1+ (4/9)A ~ 1): {(4/9)*fmax:.4f}*(1-A)/C_R")

    print("\n== validation on objects with independently known density (JPL SBDB A2 read 2026-11-20) ==")
    # name, D[m], Bond albedo, A2, sigma, rho_true, a, e
    val = [
        ("Bennu (Farnocchia+21 equiv A2)", 484.4, 0.017, 4.6e-14, 0.01e-14, 1194, 1.126, 0.204),
        ("Ryugu", 896, 0.016, 2.5e-14, 5.0e-15, 1190, 1.190, 0.190),
        ("Itokawa", 330, 0.10, 2.9e-14, 7.2e-15, 1900, 1.324, 0.280),
        ("Moshup 1999 KW4", 1317, 0.10, 6.1e-15, 1.1e-16, 1970, 0.642, 0.688),
        ("2000 DP107", 863, 0.05, 9.6e-15, 6.2e-16, 1380, 1.365, 0.377),
        ("1996 FG3", 1196, 0.015, 1.2e-14, 1.5e-15, 1300, 1.054, 0.350),
        ("Apophis (rho unknown)", 340, 0.14, 2.9e-14, 1.9e-16, float('nan'), 0.922, 0.191),
        ("Golevka (rho from Yark.)", 530, 0.06, 1.2e-14, 1.5e-15, 2700, 2.49, 0.61),
        ("1950 DA (rho from Yark.)", 1300, 0.03, 5.3e-15, 1.0e-15, 1700, 1.70, 0.51),
    ]
    for name, D, A, a2, s, rho, a, e in val:
        rmax = K * (1 - A) / (D * a2)
        rmax_lo = K * (1 - A) / (D * (a2 + 2 * s))
        rmax_hi = K * (1 - A) / (D * max(a2 - 2 * s, 1e-30))
        print(f"  {name:32s} D={D:7.1f} m  |A2|={a2:.2e}  da/dt={dadt_from_a2(a2,a,e):6.2f}e-4 au/Myr  rho_max={rmax:7.0f} (2s range {rmax_lo:.0f}-{rmax_hi:.0f})  rho_true={rho}  ratio true/max={rho/rmax:.2f}")

    print("\n== worked example: 100 m class object, H=22.5 ==")
    H = 22.5
    for a2 in (5e-14, 1e-13, 2e-13, 4e-13):
        line = f"  |A2|={a2:.0e}: "
        for pv in (0.05, 0.15, 0.30, 0.50):
            D = diam_from_H(H, pv)
            A = 0.39 * pv
            line += f" pV={pv}: D={D:5.0f} m rho_max={K*(1-A)/(D*a2):6.0f} |"
        print(line)
    print("  metal test (rho>=4000, pV<=0.30): requires |A2| <=", f"{K*(1-0.39*0.30)/(diam_from_H(H,0.30)*4000):.2e}")
    print("  metal test (rho>=4000, pV<=0.20): requires |A2| <=", f"{K*(1-0.39*0.20)/(diam_from_H(H,0.20)*4000):.2e}")

    print("\n== worked example: 10 m class object, H=27.5 ==")
    H = 27.5
    for a2 in (3e-13, 1e-12, 2e-12, 5e-12):
        line = f"  |A2|={a2:.0e}: "
        for pv in (0.05, 0.15, 0.30, 0.50):
            D = diam_from_H(H, pv)
            A = 0.39 * pv
            line += f" pV={pv}: D={D:5.1f} m rho_max={K*(1-A)/(D*a2):6.0f} |"
        print(line)

    print("\n== real case: 2022 OB5 (H=28.99, A2=-1.657e-12 +- 6.5e-14, P=92.5 s, a=1.03) ==")
    H, a2, s = 28.99, 1.657e-12, 6.5e-14
    for pv in (0.03, 0.10, 0.15, 0.30, 0.50, 0.70):
        D = diam_from_H(H, pv)
        A = 0.39 * pv
        rmax = K * (1 - A) / (D * (a2 - 2 * s))
        amr_metal = 1.5 / (5000 * D)
        print(f"  pV={pv:4.2f} D={D:5.2f} m  rho_max(2-sigma)={rmax:6.0f} kg/m3 ; SRP A1 expected if rho=5000: {K1*1.1*amr_metal:.2e}, if rho=rho_max: {K1*1.1*1.5/(rmax*D):.2e}")
    print("  Theta and F/Fmax for P=92.5 s at 1.03 au as a function of thermal inertia:")
    for g in (10, 20, 50, 100, 300, 1000, 2500):
        th, T = theta(g, 92.5, 1.03, A=0.06)
        print(f"    Gamma={g:5d}: Theta={th:8.2f}  F={F_large(th):.4f}  F/Fmax={F_large(th)/fmax:.3f}")

    print("\n== real case: Kamo'oalewa (H=24.31, A2=-1.3e-13+-1.8e-14, P=28.3 min) ==")
    for pv in (0.10, 0.20, 0.30):
        D = diam_from_H(24.31, pv)
        print(f"  pV={pv} D={D:5.1f} m rho_max={K*(1-0.39*pv)/(D*1.3e-13):6.0f}")

    print("\n== dark comets / SRP objects: |A2|/A1 ratio test (SBDB values) ==")
    objs = [("2009 BD", 5.6e-11, 1.1e-12), ("2020 GE", 1.8e-10, 1.9e-12), ("2012 TC4", 2.4e-11, 2.7e-13),
            ("2015 TC25", 1.6e-10, 5.3e-12), ("2006 RH120", 1.4e-10, 4.6e-11), ("2011 MD", 7.4e-11, 6.3e-13), ("2012 LA", 6.7e-11, 1.9e-12)]
    for n, a1, a2v in objs:
        print(f"  {n:11s} A1={a1:.2e} |A2|={a2v:.2e} ratio={a2v/a1:.3f}  (limit ~{(4/9)*fmax:.3f}(1-A)/C_R)")

    print("\n== SRP: AMR and density from SBDB A1 (sphere, C_R=1.1..1.3) ==")
    a1s = [("2009 BD", 28.10, 5.6e-11, 8.5e-12), ("2011 MD", 27.98, 7.4e-11, 2.5e-11), ("2012 LA", 27.60, 6.7e-11, 1.2e-11),
           ("2012 TC4", 26.71, 2.4e-11, 8.0e-12), ("2015 TC25", 29.34, 1.6e-10, 2.1e-11), ("2006 RH120", 29.50, 1.4e-10, 8.0e-12),
           ("2020 CD3", 31.74, 1.4e-10, 2.5e-12), ("2020 GE", 28.17, 1.8e-10, 1.3e-11), ("2021 GM1", 30.40, 5.8e-11, 1.1e-11),
           ("2021 VH2", 28.80, 8.1e-11, 2.2e-11), ("2020 WY", 26.20, 6.2e-11, 2.9e-11), ("2026 QQ8", 31.37, 1.3e-10, 1.0e-11)]
    for n, H, a1, s in a1s:
        amr = a1 / (K1 * 1.2)
        out = f"  {n:11s} H={H:5.2f} A1={a1:.2e}+-{s:.1e} (snr {a1/s:4.1f})  AMR={amr*1e4:5.2f}e-4 m2/kg (C_R=1.2);  rho[kg/m3] for pV=0.05/0.15/0.30/0.50: "
        for pv in (0.05, 0.15, 0.30, 0.50):
            D = diam_from_H(H, pv)
            out += f"{1.5/(amr*D):6.0f} "
        print(out)
