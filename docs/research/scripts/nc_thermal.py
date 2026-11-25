#!/usr/bin/env python3
"""Independent derivation of the linear Yarkovsky thermal function for a homogeneous sphere of ANY size,
and of the density-bound coefficient.  Run with python3 -I.  No downloads are read.

Derivation (done here from the heat equation, not copied from a paper):
  Heat conduction in the sphere:  rho_s C dT/dt = K lap(T).
  Linearised surface condition at r=R:  4 eps sigma T_av^3 dT + K d(dT)/dr = alpha * dE,
  with T_av the mean temperature (eps sigma T_av^4 = alpha F / 4) and dE the varying part of the insolation.
  Only the dipole (l=1) part of dT gives a net recoil.  The l=1 part of max(0,cos psi) is (1/2) cos psi.
  For forcing exp(i nu t) the regular radial solution is j_1(k r), k = sqrt(-i nu rho_s C / K) = sqrt(-i)/l_nu,
  l_nu = sqrt(K/(rho_s C nu)) the penetration depth.  Then
      dT(R) = alpha (F/2) / (4 eps sigma T_av^3) * 1 / (1 + lam * psi(z)),
      z = sqrt(-i) R',  R' = R/l_nu,  psi(z) = z j_1'(z)/j_1(z),
      lam = K / (4 eps sigma T_av^3 R) = Theta / (sqrt(2) R'),   Theta = Gamma sqrt(nu) / (eps sigma T_star^3),
      T_star^4 = alpha F/(eps sigma) = 4 T_av^4.
  Lambertian recoil  f = -(2/3)(eps sigma/c) Int T^4 n dS  ->  per unit mass
      a = -(4/9) alpha Phi * Re[ e(t) / (1 + lam psi) ],     Phi = pi R^2 F/(m c) = 3F/(2 D rho c).
  The component 90 deg ahead of the Sun direction (transverse, for zero obliquity) is
      a_t = (4/9) alpha Phi * |W|,     W = Im[ 1/(1 + lam psi(z)) ].
  This reproduces  da/dt = -(8/9)(alpha Phi/n) W cos(gamma)  of Vokrouhlicky et al. (2015) eq. (1)
  because da/dt = 2 a_t / n on a circular orbit.
"""
import cmath
import math

L_SUN = 3.828e26          # W (IAU 2015 nominal)
C_LIGHT = 2.99792458e8    # m/s
AU = 1.495978707e11       # m
DAY = 86400.0
SIGMA = 5.670374419e-8


def j1(z):
    return cmath.sin(z) / (z * z) - cmath.cos(z) / z


def psi(z):
    """z j1'(z)/j1(z), numerically stable for large |Im z|."""
    # j1'(z) = j0(z) - 2 j1(z)/z ;  j0 = sin z / z
    if abs(z.imag) > 30:
        # asymptotic: j1 ~ -exp(iz')... use ratio form with tan
        # j0/j1 = (sin z / z) / (sin z/z^2 - cos z/z) = z / (1 - z cot z) ; for Im z -> -inf, cot z -> +i
        cot = 1j if z.imag < 0 else -1j
        ratio = z / (1 - z * cot)
    else:
        s, c = cmath.sin(z), cmath.cos(z)
        ratio = (s / z) / (s / (z * z) - c / z)
    return z * ratio - 2.0


def W_sphere(Rp, theta):
    """|W| for a homogeneous sphere with R' = R/l_nu and thermal parameter Theta."""
    if Rp < 1e-3:
        return 0.0
    z = cmath.sqrt(-1j) * Rp
    lam = theta / (math.sqrt(2) * Rp)
    return abs((1.0 / (1.0 + lam * psi(z))).imag)


def W_large(theta):
    return 0.5 * theta / (1 + theta + 0.5 * theta * theta)


def W_vok99(Rp, theta):
    """The closed form quoted (from memory) by the earlier researcher: E sin(delta)/(1+lambda), x = sqrt(2) R'."""
    x = math.sqrt(2) * Rp
    lam = theta / x
    ex = math.exp(x)
    cx, sx = math.cos(x), math.sin(x)
    A = -(x + 2) - ex * ((x - 2) * cx - x * sx)
    B = -x - ex * (x * cx + (x - 2) * sx)
    k = lam / (1 + lam)
    C = A + k * (3 * (x + 2) + ex * (3 * (x - 2) * cx + x * (x - 3) * sx))
    Dd = B + k * (x * (x + 3) - ex * (x * (x - 3) * cx - 3 * (x - 2) * sx))
    return abs((complex(A, B) / complex(C, Dd)).imag) / (1 + lam)


def golden_max(f, lo, hi, n=200):
    """max of f over log-spaced grid then refine by golden section in log space."""
    best = (-1, None)
    xs = [lo * (hi / lo) ** (i / n) for i in range(n + 1)]
    for x in xs:
        v = f(x)
        if v > best[0]:
            best = (v, x)
    i = xs.index(best[1])
    a, b = math.log(xs[max(i - 1, 0)]), math.log(xs[min(i + 1, n)])
    g = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        c1, c2 = b - g * (b - a), a + g * (b - a)
        if f(math.exp(c1)) > f(math.exp(c2)):
            b = c2
        else:
            a = c1
    x = math.exp((a + b) / 2)
    return f(x), x


if __name__ == "__main__":
    print("== 1. large-body limit: analytic maximum ==")
    th = math.sqrt(2)
    print("   W_large(sqrt2) = %.6f ; closed form (sqrt2/2)/(2+sqrt2) = %.6f ; = (sqrt2-1)/2 = %.6f" % (W_large(th), (th / 2) / (2 + th), (th - 1) / 2))
    print("   xi_max = (4/9) W_max = %.5f" % (4 / 9 * W_large(th)))

    print("\n== 2. my Bessel-function solution vs large-body limit and vs the closed form used by the earlier script ==")
    print("   R'      Theta    W_bessel   W_vok99(closed form)   W_large")
    for Rp in (0.3, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 28.0):
        for theta in (0.3, math.sqrt(2), 5.0):
            print("   %-7.2f %-8.3f %.6f   %.6f               %.6f" % (Rp, theta, W_sphere(Rp, theta), W_vok99(Rp, theta), W_large(theta)))
    md = max(abs(W_sphere(Rp, th_) - W_vok99(Rp, th_)) for Rp in [0.05 * 1.06 ** i for i in range(110)] for th_ in [0.01 * 1.1 ** j for j in range(100)])
    print("   max |W_bessel - W_vok99| over R' in [0.05,30], Theta in [0.01,138]: %.2e" % md)

    print("\n== 3. maximum over Theta at fixed R' ==")
    print("   R'       max_W     at Theta   ratio to 0.2071")
    glob = (-1, None, None)
    for i in range(0, 161):
        Rp = 10 ** (-1.0 + i * 0.02)   # 0.1 .. ~158; psi switches to asymptotic above |Im z|=30
        v, tbest = golden_max(lambda t: W_sphere(Rp, t), 1e-3, 1e3)
        if v > glob[0]:
            glob = (v, Rp, tbest)
        if i % 10 == 0:
            print("   %-8.3f %.5f   %-9.3f  %.3f" % (Rp, v, tbest, v / W_large(th)))
    # refine global maximum in R'
    vR, Rbest = golden_max(lambda R: golden_max(lambda t: W_sphere(R, t), 1e-3, 1e3, n=120)[0], 0.5, 20, n=80)
    _, tbest = golden_max(lambda t: W_sphere(Rbest, t), 1e-3, 1e3)
    print("   GLOBAL maximum of |W| = %.5f at R' = R/l = %.3f (x = sqrt2 R' = %.3f), Theta = %.3f  -> +%.1f%% over 0.2071" % (vR, Rbest, math.sqrt(2) * Rbest, tbest, 100 * (vR / W_large(th) - 1)))
    WG = vR

    print("\n== 4. combined diurnal + seasonal maximum ==")
    print("   |da/dt| prop to 2 W_d |cos g| + W_s sin^2 g (retrograde: terms add).")
    for wd, ws, lab in ((W_large(th), W_large(th), "both large-body"), (W_large(th), WG, "diurnal large-body, seasonal at finite-size peak"), (WG, WG, "both at finite-size peak")):
        best = max((2 * wd * c + ws * (1 - c * c), c) for c in [i / 10000 for i in range(10001)])
        print("   %-50s max = %.5f at |cos g| = %.3f  -> equivalent single-term W = %.5f (%+.1f%% vs 0.2071)" % (lab, best[0], best[1], best[0] / 2, 100 * (best[0] / 2 / W_large(th) - 1)))

    print("\n== 5. bound coefficient ==")
    S1 = L_SUN / (4 * math.pi * AU ** 2)
    print("   solar constant from L_sun: %.1f W/m2" % S1)
    for lab, w in (("large body 0.2071", W_large(th)), ("finite-size global max", WG)):
        k_si = (4 / 9) * w * 3 * L_SUN / (2 * 4 * math.pi * C_LIGHT)     # a_t r^2 D rho, SI
        k = k_si * DAY ** 2 / AU ** 3
        print("   %-24s |A2|max = %.4e (1-A)/(D[m] rho[kg/m3]) au/d2   (SI: a_t(1 au) = %.4e (1-A)/(D rho) m/s2)" % (lab, k, k_si / AU ** 2))
    k1 = L_SUN / (4 * math.pi * C_LIGHT) * DAY ** 2 / AU ** 3
    print("   radiation pressure: A1 = %.4e * C_R * (A/m)[m2/kg] au/d2 ; sphere A/m = 1.5/(rho D)" % k1)
    print("   ratio |A2|max/A1 for a sphere = (4/9)*W*(1-A)/C_R = %.4f (1-A)/C_R" % (4 / 9 * W_large(th)))

    print("\n== 6. penetration depths: when is R comparable to l? ==")
    for lab, K, rhoC in (("regolith K=0.01", 0.01, 1500 * 700), ("porous rock K=0.1", 0.1, 2000 * 750), ("solid rock K=2.5", 2.5, 2800 * 800), ("iron K=40", 40.0, 7800 * 450)):
        row = []
        for plab, P in (("P=1.5 min", 92.5), ("P=5 h", 18000.0), ("P_orb=1 yr", 365.25 * 86400)):
            nu = 2 * math.pi / P
            row.append("%s l=%.3g m" % (plab, math.sqrt(K / (rhoC * nu))))
        print("   %-18s Gamma=%6.0f  %s" % (lab, math.sqrt(K * rhoC), " | ".join(row)))
    print("   peak at R' = %.2f means D = 2R = %.1f l.  For the seasonal wave on solid rock (l ~ 2.4 m) that is D ~ %.0f m; on iron (l ~ 7.6 m) D ~ %.0f m." % (Rbest, 2 * Rbest, 2 * Rbest * 2.37, 2 * Rbest * 7.57))
