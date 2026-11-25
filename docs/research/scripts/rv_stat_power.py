"""Statistician review: closed-form checks of the pass bars in plan section 2.3.
Pure stdlib. No data files read.
"""
import math
from math import comb


def binom_cdf(k, n, p):
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(0, k + 1))


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def zq(p):
    # inverse normal by bisection
    lo, hi = -10, 10
    for _ in range(200):
        mid = (lo + hi) / 2
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


print("== 1. Gold set: 'claims 90%, delivers 60%' ==")
for n in (8, 12, 20):
    # one-sided 5% test of H0: hit rate = 0.9; reject if hits <= k
    k = max(k for k in range(-1, n + 1) if binom_cdf(k, n, 0.9) <= 0.05) if binom_cdf(0, n, 0.9) <= 0.05 else -1
    k = -1
    for kk in range(n + 1):
        if binom_cdf(kk, n, 0.9) <= 0.05:
            k = kk
    size = binom_cdf(k, n, 0.9)
    print(f" n={n}: reject if hits <= {k} (size {size:.3f}); power at true 0.7/0.6/0.5 = "
          + ", ".join(f"{binom_cdf(k, n, p):.2f}" for p in (0.7, 0.6, 0.5)))

print("\n== 2. Gold rule 'no gold object's true class is given under 5%' ==")
print(" Probability that a perfectly CALIBRATED predictor trips the rule at least once in 12 objects,")
print(" if on each object it puts total mass m on classes it rates below 5%:")
for m in (0.0, 0.03, 0.05, 0.08, 0.10, 0.12):
    print(f"   m={m:.2f}: P(fail) = {1 - (1 - m) ** 12:.2f}")
print(" A base-rate predictor with every class >= 5% (e.g. 0.56/0.15/0.16/0.12) has m=0 -> never fails.")

print("\n== 3. Density ceiling: 'at most one violation among 8-9 objects' ==")
for n in (8, 9, 11):
    print(f" n={n}: P(pass) when the bound truly fails with rate r: "
          + ", ".join(f"r={r:.2f}:{binom_cdf(1, n, r):.2f}" for r in (0.05, 0.10, 0.20, 0.30, 0.40, 0.50)))

print("\n== 4. Multiplicity for force-term detections ==")
for label, m in (("stage 1, ~900 objects x 3 terms", 900 * 3),
                 ("stage 1, 7,229 objects x 3 terms", 7229 * 3),
                 ("stage 2, 10,500 objects x 3 terms", 10500 * 3)):
    p3 = 2 * (1 - phi(3.0))
    p5 = 2 * (1 - phi(5.0))
    zneed = zq(1 - (1.0 / m) / 2)
    zneed01 = zq(1 - (0.1 / m) / 2)
    print(f" {label}: tests={m}; expected false 3-sigma = {m * p3:.1f}; false 5-sigma = {m * p5:.4f}; "
          f"|z| for <=1 expected false = {zneed:.2f}; for <=0.1 = {zneed01:.2f}")
print(" If the error bar is understated by a factor f on a share of objects, a nominal 3-sigma is really 3/f:")
for f in (1.0, 1.34, 1.59, 2.0):
    print(f"   f={f}: per-test false-alarm rate at nominal 3 sigma = {2 * (1 - phi(3 / f)):.4f}")
print(" Calibrated error = c x formal. Flag at 3 calibrated sigma using a GLOBAL c=0.65, object-level truth c_i:")
for ci in (0.34, 0.5, 0.65, 1.0, 2.0):
    print(f"   c_i={ci}: true z at threshold = {3 * 0.65 / ci:.2f}, false-alarm rate = {2 * (1 - phi(3 * 0.65 / ci)):.4f}")

print("\n== 5. Empirical null of 30 objects: what it can establish ==")
print(f" zero 3-sigma exceedances in n objects -> 95% upper bound on the rate = 1-0.05^(1/n):")
for n in (30, 100, 300, 1000):
    print(f"   n={n}: {1 - 0.05 ** (1 / n):.4f}")
# CI for SD of z with n=30, s=0.64 and 0.75 (chi-square quantiles for 29 dof: 16.047, 45.722)
for s in (0.64, 0.75):
    lo = s * math.sqrt(29 / 45.722)
    hi = s * math.sqrt(29 / 16.047)
    print(f" s={s}: 95% CI for SD = [{lo:.2f}, {hi:.2f}]  -> 'formal is cautious by' {1 / hi:.2f} to {1 / lo:.2f} times")

print("\n== 6. Class bar: pass probability of 'point >= 0.10 bits AND 95% interval excludes zero' ==")
print(" per-object SD of the log-score difference assumed sd; SE = sd/sqrt(n_eff)")
for sd in (0.6,):
    for neff in (30, 50, 75, 100, 150, 275, 500):
        se = sd / math.sqrt(neff)
        out = []
        for true in (0.0, 0.03, 0.05, 0.10, 0.15, 0.20):
            thr = max(0.10, 1.96 * se)
            ppass = 1 - phi((thr - true) / se)
            out.append(f"{true:.2f}:{ppass:.2f}")
        print(f"   sd={sd} n_eff={neff:4d} SE={se:.3f}  P(pass | true gain) " + "  ".join(out))

print("\n== 7. Label noise: how much of a true 0.10-bit signal survives ==")


def mi(joint):
    # joint[x][y]
    px = [sum(r) for r in joint]
    py = [sum(joint[i][j] for i in range(len(joint))) for j in range(len(joint[0]))]
    t = 0.0
    for i, r in enumerate(joint):
        for j, v in enumerate(r):
            if v > 0:
                t += v * math.log2(v / (px[i] * py[j]))
    return t


def binary_case(prev, eps):
    # binary feature X (50/50), P(Y=1|X) = prev +/- d ; find d for MI = 0.10 bits
    lo, hi = 0.0, min(prev, 1 - prev) - 1e-9
    for _ in range(100):
        d = (lo + hi) / 2
        j = [[0.5 * (1 - (prev + d)), 0.5 * (prev + d)], [0.5 * (1 - (prev - d)), 0.5 * (prev - d)]]
        if mi(j) < 0.10:
            lo = d
        else:
            hi = d
    j = [[0.5 * (1 - (prev + d)), 0.5 * (prev + d)], [0.5 * (1 - (prev - d)), 0.5 * (prev - d)]]
    # noisy label: flip with prob eps
    jn = [[r[0] * (1 - eps) + r[1] * eps, r[1] * (1 - eps) + r[0] * eps] for r in j]
    return mi(j), mi(jn)


for prev, name in ((0.61, "S/Q vs rest (61% S/Q)"), (0.16, "dark vs bright (16% dark)")):
    for eps in (0.0, 0.05, 0.11, 0.21):
        a, b = binary_case(prev, eps)
        print(f"   {name}: flip rate {eps:.2f}: true MI {a:.3f} -> observable {b:.3f} bits ({100 * b / a:.0f}%)")
print(" (21% is the measured colour-vs-spectrum disagreement on S/Q vs rest; 0.11 is the per-source")
print("  error rate if both sources are equally noisy and independent: 2e(1-e)=0.21 -> e=0.12)")
print(f"   solve 2e(1-e)=0.21: e = {(1 - math.sqrt(1 - 2 * 0.21)) / 2:.3f};  2e(1-e)=0.33: e = {(1 - math.sqrt(1 - 2 * 0.33)) / 2:.3f}")

print("\n== 8. Pre-impact objects as a forecast stream ==")
# 13 objects 2008-2026; by year from ground-truth.md section 3
years = {2008: 1, 2014: 1, 2018: 1, 2019: 1, 2022: 2, 2023: 1, 2024: 4, 2025: 0, 2026: 2}
tot = sum(years.values())
recent = sum(v for y, v in years.items() if y >= 2022)
print(f" total {tot} in 2008-2026; 2022-2026: {recent} in 5 yr = {recent / 5:.1f}/yr")
print(" with any composition truth (meteorite or pre-impact colours/spectrum): 2008 TC3, 2018 LA, 2022 WJ1, 2023 CX1, 2024 BX1, 2024 RW1 = 6 of 13")
for rate in (0.4, 0.8, 1.2):
    lam = rate * 3
    print(f"   resolved rate {rate}/yr over 2027-2029: mean {lam:.1f}, P(0)={math.exp(-lam):.2f}, P(<=2)={sum(math.exp(-lam) * lam**k / math.factorial(k) for k in range(3)):.2f}")
