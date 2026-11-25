#!/usr/bin/env python3
"""Independent time-domain cross-check of nc_nonlinear.py for one flat facet.

Solves du/dtau = d2u/dx2 on 0 <= x <= X (depth in units of the diurnal skin depth l = sqrt(K/(rho C omega)),
tau = rotation phase in radians) with the non-linear surface condition  u^4 = s(tau) + Theta * du/dx|_0,
s = max(0, cos tau), zero flux at depth.  Implicit (backward Euler) in the interior, Newton on the surface node.
Reports J = Int u^4 sin(tau) dtau over the last rotation, to compare with the harmonic-balance value.
Needs numpy only; run with python -I.
"""
import sys

import numpy as np


def J_fd(theta, nx=400, X=10.0, nt=4000, nrot=40):
    # stretched grid, fine near the surface
    xi = np.linspace(0, 1, nx)
    x = X * (np.exp(4 * xi) - 1) / (np.exp(4) - 1)
    dx = np.diff(x)
    dt = 2 * np.pi / nt
    u = np.full(nx, (1 / np.pi) ** 0.25)
    # tridiagonal for interior nodes (non-uniform second derivative)
    a = np.zeros(nx); b = np.zeros(nx); c = np.zeros(nx)
    for i in range(1, nx - 1):
        hm, hp = dx[i - 1], dx[i]
        a[i] = -dt * 2 / (hm * (hm + hp))
        c[i] = -dt * 2 / (hp * (hm + hp))
        b[i] = 1 - a[i] - c[i]
    # bottom: zero flux
    a[-1] = -dt * 2 / dx[-1] ** 2
    b[-1] = 1 - a[-1]
    h0 = dx[0]
    J = 0.0
    for rot in range(nrot):
        J = 0.0
        for k in range(nt):
            tau = (k + 1) * dt
            s = max(0.0, np.cos(tau))
            # Solve implicit system with unknown surface value by Newton on u0:
            # interior solve is linear in u0: u = p + q*u0 (Thomas algorithm twice)
            rhs = u.copy()
            # forward elimination for nodes 1..nx-1 with u0 as boundary
            def solve(u0):
                cp = np.zeros(nx); dp = np.zeros(nx)
                d = rhs.copy()
                d[1] -= a[1] * u0
                cp[1] = c[1] / b[1]; dp[1] = d[1] / b[1]
                for i in range(2, nx):
                    m = b[i] - a[i] * cp[i - 1]
                    cp[i] = c[i] / m if i < nx - 1 else 0.0
                    dp[i] = (d[i] - a[i] * dp[i - 1]) / m
                sol = np.zeros(nx)
                sol[-1] = dp[-1]
                for i in range(nx - 2, 0, -1):
                    sol[i] = dp[i] - cp[i] * sol[i + 1]
                return sol
            p = solve(0.0)
            qv = solve(1.0) - p
            # surface: second-order one-sided derivative du/dx|0 = (-3u0 + 4u1 - u2)/(2h) on locally uniform spacing approx;
            # use first two intervals with non-uniform formula
            h1, h2 = dx[0], dx[1]
            c0 = -(2 * h1 + h2) / (h1 * (h1 + h2)); c1 = (h1 + h2) / (h1 * h2); c2 = -h1 / (h2 * (h1 + h2))
            u0 = u[0]
            for _ in range(30):
                u1 = p[1] + qv[1] * u0; u2 = p[2] + qv[2] * u0
                f = u0 ** 4 - s - theta * (c0 * u0 + c1 * u1 + c2 * u2)
                fp = 4 * u0 ** 3 - theta * (c0 + c1 * qv[1] + c2 * qv[2])
                step = f / fp
                u0 -= step
                if abs(step) < 1e-13:
                    break
            u = p + qv * u0
            u[0] = u0
            J += u0 ** 4 * np.sin(tau) * dt
    return J


if __name__ == "__main__":
    for th in [float(v) for v in sys.argv[1:]] or [0.5, 1.778, 5.0]:
        print("Theta_loc = %.3f : J (finite difference, 40 rotations) = %.5f" % (th, J_fd(th)))
