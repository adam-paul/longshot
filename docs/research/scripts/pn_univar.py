#!/usr/bin/env python3
"""Classical, model-light tests of orbit -> class and H -> class in each subset (a different route from the classifiers).

1. Per-feature AUC (Mann-Whitney) for dark-vs-bright and S/Q-vs-rest, with bootstrap 95% intervals.
2. Likelihood-ratio tests of nested logistic regressions (unpenalised, standardised quantile-normal features):
   class ~ 1  vs  class ~ orbit(6);   class ~ 1 vs class ~ H(+H^2);   class ~ H(+H^2)  vs  class ~ H(+H^2) + orbit(6).
   Also the in-sample information gain (bits per object) and its chance expectation (df / (2 n ln 2)).
3. Plug-in mutual information between a coarse orbit cell and the class, raw and after subtracting the permutation mean,
   to show the size of the small-sample bias of a binned estimator.
4. Reliability of the label itself: the ceiling any predictor could reach (not computed; see report).

Usage: pn_univar.py <labels.csv> <out.json>
"""
import sys, json, warnings
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')

lab_fn, out_fn = sys.argv[1], sys.argv[2]
d0 = pd.read_csv(lab_fn, dtype={'pdes': str})
ORB = ['a', 'e', 'i', 'q', 'tj', 'moid']
rng = np.random.default_rng(20261121)
SUB = {'all': lambda d: np.ones(len(d), bool), 'a<2': lambda d: (d.a < 2).values, 'a>=2': lambda d: (d.a >= 2).values,
       'NHATS': lambda d: (d.nhats == 1).values, 'NHATS-like box': lambda d: ((d.a >= 0.8) & (d.a <= 1.3) & (d.e < 0.3) & (d.i < 10)).values,
       'NHATS H>=24': lambda d: ((d.nhats == 1) & (d.H >= 24)).values}

def qn(x):
    r = stats.rankdata(x); return stats.norm.ppf((r - 0.5) / len(x))
def ll_fit(X, y):
    """Maximum-likelihood multinomial/binary logistic log-likelihood (nats). X may be None (intercept only)."""
    if X is None:
        p = np.bincount(y) / len(y); return float((np.bincount(y) * np.log(p[p > 0] if (p > 0).all() else np.clip(p, 1e-12, 1))).sum())
    m = LogisticRegression(C=1e6, max_iter=5000, tol=1e-8).fit(X, y)
    P = m.predict_proba(X); return float(np.log(np.clip(P[np.arange(len(y)), np.searchsorted(m.classes_, y)], 1e-300, 1)).sum())
def lrt(l0, l1, df):
    st = 2 * (l1 - l0); return dict(chi2=float(st), df=int(df), p=float(stats.chi2.sf(st, df)))
def auc_ci(x, y, B=2000):
    a = roc_auc_score(y, x); n = len(y); bs = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        if y[idx].min() == y[idx].max(): continue
        bs.append(roc_auc_score(y[idx], x[idx]))
    return dict(auc=float(a), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))
def plugin_mi(c, y):
    t = pd.crosstab(c, y).values.astype(float); p = t / t.sum(); px = p.sum(1, keepdims=True); py = p.sum(0, keepdims=True)
    nz = p > 0; return float((p[nz] * np.log2(p[nz] / (px @ py)[nz])).sum())

out = {}
LABELS = {'dark (pV<0.10)': ('alb', lambda d: (d.alb < 0.10).astype(int).values),
          'S/Q vs rest': ('sq', lambda d: d.sq.astype(int).values),
          'S/Q, C, X, other': ('tax4', lambda d: d.tax4.map({'S': 0, 'C': 1, 'X': 2, 'O': 3}).astype(int).values)}
for lname, (col, yf) in LABELS.items():
    dl = d0[d0[col].notna()].reset_index(drop=True); yall = yf(dl)
    for sname, sf in SUB.items():
        m = sf(dl); d = dl[m].reset_index(drop=True); y = yall[m]; n = len(y); K = len(np.unique(y)); cnt = np.bincount(y).tolist()
        res = dict(n=int(n), counts=cnt)
        if n < 40 or min(c for c in cnt if c > 0) < 8 or K < 2:
            res['note'] = 'too small for any test'; out['%s | %s' % (lname, sname)] = res; continue
        if K == 2:
            res['auc'] = {f: auc_ci(d[f].values, y) for f in ORB + ['H']}
        Z = np.column_stack([qn(d[f].values) for f in ORB]); h = qn(d.H.values); Hm = np.column_stack([h, h ** 2])
        l0 = ll_fit(None, y); lo = ll_fit(Z, y); lh = ll_fit(Hm, y); loh = ll_fit(np.column_stack([Hm, Z]), y)
        k1 = K - 1
        res['lrt_orbit_vs_null'] = lrt(l0, lo, 6 * k1); res['lrt_H_vs_null'] = lrt(l0, lh, 2 * k1); res['lrt_orbit_given_H'] = lrt(lh, loh, 6 * k1)
        res['lrt_H_given_orbit'] = lrt(lo, loh, 2 * k1)
        tb = lambda dl_: float(dl_ / n / np.log(2))
        res['insample_bits'] = dict(orbit=tb(lo - l0), H=tb(lh - l0), orbit_given_H=tb(loh - lh), H_given_orbit=tb(loh - lo),
                                    chance_orbit=6 * k1 / (2 * n * np.log(2)), chance_H=2 * k1 / (2 * n * np.log(2)))
        pi = np.bincount(y) / n; res['class_entropy_bits'] = float(-(pi[pi > 0] * np.log2(pi[pi > 0])).sum())
        # binned plug-in MI: a (3 quantile bins) x e (2) x i (2) = 12 orbit cells, and H in 4 quantile bins
        cell = (pd.qcut(d.a, 3, labels=False, duplicates='drop').astype(str) + pd.qcut(d.e, 2, labels=False, duplicates='drop').astype(str)
                + pd.qcut(d.i, 2, labels=False, duplicates='drop').astype(str)).values
        hb = pd.qcut(d.H, 4, labels=False, duplicates='drop').values
        for nm, c in (('orbit12', cell), ('H4', hb)):
            raw = plugin_mi(c, y); null = np.array([plugin_mi(c, rng.permutation(y)) for _ in range(500)])
            res['mi_' + nm] = dict(raw=raw, perm_mean=float(null.mean()), perm_q95=float(np.percentile(null, 95)), corrected=float(raw - null.mean()),
                                   p=float((1 + (null >= raw).sum()) / 501), ncells=int(len(np.unique(c))),
                                   miller_madow_bias=float((len(np.unique(c)) - 1) * (K - 1) / (2 * n * np.log(2))))
        out['%s | %s' % (lname, sname)] = res
json.dump(out, open(out_fn, 'w'), indent=1)

for k, r in out.items():
    print('=' * 110); print(k, 'n=%d counts=%s' % (r['n'], r['counts']))
    if 'note' in r: print('  ', r['note']); continue
    if 'auc' in r: print('  AUC: ' + '  '.join('%s %.3f [%.2f,%.2f]' % (f, v['auc'], v['lo'], v['hi']) for f, v in r['auc'].items()))
    for t in ('lrt_orbit_vs_null', 'lrt_H_vs_null', 'lrt_orbit_given_H', 'lrt_H_given_orbit'):
        print('  %-20s chi2 %.1f df %d p=%.2g' % (t, r[t]['chi2'], r[t]['df'], r[t]['p']))
    b = r['insample_bits']; print('  in-sample bits/object: orbit %.4f (chance %.4f)  H %.4f (chance %.4f)  orbit|H %.4f  H|orbit %.4f   class entropy %.3f' % (
        b['orbit'], b['chance_orbit'], b['H'], b['chance_H'], b['orbit_given_H'], b['H_given_orbit'], r['class_entropy_bits']))
    for nm in ('mi_orbit12', 'mi_H4'):
        v = r[nm]; print('  plug-in MI %-8s raw %.4f  permutation mean (pure bias) %.4f  corrected %.4f  p=%.3f  [%d cells; analytic bias %.4f]' % (
            nm, v['raw'], v['perm_mean'], v['corrected'], v['p'], v['ncells'], v['miller_madow_bias']))
