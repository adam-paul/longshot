#!/usr/bin/env python3
"""Non-linear check of the maximum diurnal Yarkovsky efficiency of a smooth, large sphere.

Linear theory (one global mean temperature) gives a_t = (4/9) alpha Phi |W|, |W| <= 0.2071 at Theta = sqrt(2).
Here each latitude band is treated as its own plane-parallel 1-D conduction problem with the full
T^4 boundary condition (zero obliquity, circular orbit, Lambertian emission, no roughness, R >> l):

    du/dtau = d2u/dx2,   u^4 = s(tau) + Theta_loc du/dx|_0,   s = max(0, cos tau),
    Theta_loc = Theta / cos(lat)^(3/4)    (local subsolar temperature scales as cos^(1/4)).

Solved by harmonic balance: u(0,tau) = sum c_k exp(i k tau); the half-space solution gives
du/dx|_0 = -sum q_k c_k exp(i k tau),  q_k = sqrt(|k|/2) (1 + i sgn k).  Newton iteration on the N samples.

Transverse recoil:  a_t = (2/3)(alpha F R^2/(m c)) Int cos^3(lat) J(Theta_loc) dlat,  J = Int u^4 sin(tau) dtau
so the equivalent  W_eff = (3/(2 pi)) Int cos^3(lat) J dlat   (reduces to |W| in the linear theory).

Needs numpy only; run with python -I.
"""
import math
import sys

import numpy as np

N = 1024
tau = 2 * np.pi * np.arange(N) / N
s_ins = np.maximum(0.0, np.cos(tau))
k = np.fft.fftfreq(N, d=1.0 / N)
q = np.sqrt(np.abs(k) / 2.0) * (1 + 1j * np.sign(k))
# dense matrix of the linear operator G: u -> real(ifft(q * fft(u)))  (= - du/dx at the surface)
G = np.real(np.fft.ifft(q[:, None] * np.fft.fft(np.eye(N), axis=0), axis=0))


def solve_facet(theta, u0=None):
    """Return surface temperature u(tau) (in units of the local subsolar temperature)."""
    u = np.full(N, (1 / math.pi) ** 0.25) if u0 is None else u0.copy()
    for it in range(200):
        res = u ** 4 + theta * (G @ u) - s_ins
        Jm = np.diag(4 * u ** 3) + theta * G
        du = np.linalg.solve(Jm, -res)
        # damped Newton, keep u positive
        step = 1.0
        while np.any(u + step * du <= 1e-6) and step > 1e-6:
            step *= 0.5
        u = u + step * du
        if np.max(np.abs(step * du)) < 1e-12:
            break
    return u


def J_of(theta, u0=None):
    u = solve_facet(theta, u0)
    Jv = np.sum(u ** 4 * np.sin(tau)) * (2 * np.pi / N)
    mean_emit = np.mean(u ** 4)
    return Jv, u, mean_emit


def W_linear(theta):
    return 0.5 * theta / (1 + theta + 0.5 * theta * theta)


if __name__ == "__main__":
    # tabulate J on a log grid of local Theta
    lt = np.linspace(-3, 3.2, 125)
    Jt = np.zeros_like(lt)
    u_prev = None
    for i, l in enumerate(lt):
        Jt[i], u_prev, me = J_of(10 ** l, u_prev)
        if abs(me - 1 / math.pi) > 1e-6:
            print("energy balance warning at Theta", 10 ** l, me, 1 / math.pi)
    print("== single flat facet (equator), J(Theta) = Int u^4 sin(tau) dtau ==")
    jmax = np.argmax(Jt)
    print("   max J = %.5f at Theta_loc = %.3f" % (Jt[jmax], 10 ** lt[jmax]))
    # linearised single facet for comparison: emitted first harmonic = (1/2) / (1 + Theta' (1+i)/sqrt2 ...) is model dependent; skip

    def Jinterp(th):
        th = np.asarray(th, dtype=float)
        v = np.interp(np.log10(th), lt, Jt)
        hi = th > 10 ** lt[-1]          # J ~ 1/Theta beyond the table
        v = np.where(hi, Jt[-1] * (10 ** lt[-1]) / th, v)
        lo = th < 10 ** lt[0]           # J ~ Theta below the table
        return np.where(lo, Jt[0] * th / (10 ** lt[0]), v)

    # Gauss-Legendre over latitude
    xg, wg = np.polynomial.legendre.leggauss(200)
    lat = 0.5 * np.pi * xg
    wl = 0.5 * np.pi * wg

    def W_eff(theta):
        c = np.cos(lat)
        return 3 / (2 * np.pi) * np.sum(wl * c ** 3 * Jinterp(theta / c ** 0.75))

    print("\n== smooth large sphere, zero obliquity: non-linear W_eff vs linear |W| ==")
    print("   Theta     W_nonlinear   W_linear   ratio")
    best = (0, None)
    for th in [0.01, 0.03, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.2, 1.414, 1.7, 2.0, 3.0, 5.0, 10.0, 30.0, 100.0]:
        w = W_eff(th)
        print("   %-8.3f  %.5f       %.5f    %.3f" % (th, w, W_linear(th), w / W_linear(th)))
    grid = 10 ** np.linspace(-1.5, 1.5, 1201)
    ws = np.array([W_eff(t) for t in grid])
    i = int(np.argmax(ws))
    print("   MAXIMUM non-linear W_eff = %.5f at Theta = %.3f   (linear: 0.20711 at 1.414)  ratio %.3f" % (ws[i], grid[i], ws[i] / 0.2071068))
    print("   => xi_max(non-linear smooth sphere) = (4/9) W = %.5f ; coefficient 3.128e-8 x %.3f = %.4e" % (4 / 9 * ws[i], ws[i] / 0.2071068, 3.1282e-8 * ws[i] / 0.2071068))
    # absolute ceiling: all absorbed power re-emitted as a Lambertian beam along -v: (2/3) alpha Phi
    print("   hard energetic ceiling (all re-emission in one Lambertian lobe along track): xi = 2/3 = 0.667, i.e. W_equiv = 1.5")
