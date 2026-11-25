#!/usr/bin/env python3
"""Orbit -> class skill test with no source-region model.

Classifiers (logistic regression, k-nearest-neighbour, gradient-boosted trees) are trained on orbital elements only,
on H only, and on orbital elements + H, and scored out-of-fold by log loss (bits/object) and Brier score against
(i) the class frequency and (ii) the H-binned class frequency, both estimated on the training folds only.

Modes
  cv      repeated stratified K-fold; regimes W (train inside the subset only) and T (train on subset-train plus all
          labelled NEAs outside the subset, with a subset indicator feature; test on subset-test)
  perm    permutation null for the W regime (labels shuffled: orbit-only null; orbit rows shuffled within H bins: orbit-beyond-H null)
  inject  injection-recovery: synthetic binary labels with a known orbit->class mutual information, real orbits and sample sizes

Usage: pn_cv.py <mode> <labels.csv> <out.json> [--label dark|tax4|sq] [--subset all|a2|nhats|box|...] [--variant ...] [--reps N] ...
"""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import sys, json, argparse, warnings, math
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import QuantileTransformer
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')

ORB = ['a', 'e', 'i', 'q', 'tj', 'moid']
HBINS = np.array([16., 18., 20., 22., 24., 26.])          # fixed a priori: 7 H bins
EPS = 1e-4
LR_CS = np.logspace(-3, 2, 6)
KNN_KS = [5, 10, 20, 40, 80, 160]

# ------------------------------------------------------------------ data
def load(path, label, variant='main'):
    d = pd.read_csv(path, dtype={'pdes': str})
    if label == 'dark':
        col = {'main': 'alb', 'spitzer': 'alb_spitzer', 'neowise': 'alb_neowise', 'clear': 'alb'}[variant]
        d = d[d[col].notna()].copy()
        if variant == 'clear':            # drop albedos within a factor 1.5 of the threshold or with sources straddling it
            d = d[((d.alb_max < 0.10) | (d.alb_min >= 0.10)) & ((d.alb < 0.10 / 1.5) | (d.alb > 0.10 * 1.5))].copy()
        d['y'] = (d[col] < 0.10).astype(int); classes = ['bright', 'dark']
    elif label == 'tax4':
        d = d[d.tax4.notna()].copy()
        if variant == 'spec': d = d[d.tax4_spec == 1].copy()
        if variant == 'agree': d = d[d.tax4_agree == 1].copy()
        classes = ['S', 'C', 'X', 'O']; d['y'] = d.tax4.map({c: k for k, c in enumerate(classes)}).astype(int)
    elif label == 'sq':
        d = d[d.sq.notna()].copy()
        if variant == 'spec': d = d[d.sq_src.isin(['mahlke', 'marsset', 'devogele', 'perna16', 'sbdb'])].copy()
        d['y'] = d.sq.astype(int); classes = ['not S/Q', 'S/Q']
    else: raise SystemExit('label?')
    return d.reset_index(drop=True), classes

def subset_mask(d, name):
    if name == 'all': return np.ones(len(d), bool)
    if name == 'a2': return (d.a < 2.0).values
    if name == 'nhats': return (d.nhats == 1).values
    if name == 'box': return ((d.a >= 0.8) & (d.a <= 1.3) & (d.e < 0.3) & (d.i < 10)).values
    if name == 'nhats_small': return ((d.nhats == 1) & (d.H >= 24)).values
    if name == 'a2_small': return ((d.a < 2.0) & (d.H >= 22)).values
    if name == 'not_nhats_a2': return ((d.nhats == 0) & (d.a < 2.0)).values
    if name == 'a2plus': return (d.a >= 2.0).values
    if name == 'small': return (d.H >= 22).values
    if name == 'nhats_dv8': return ((d.nhats == 1) & (d.min_dv < 8)).values
    raise SystemExit('subset?')

# ------------------------------------------------------------------ predictors
def clipn(p):
    p = np.clip(p, EPS, 1.0); return p / p.sum(1, keepdims=True)
def freq_pred(ytr, n, K, alpha=0.5):
    c = np.bincount(ytr, minlength=K) + alpha; return np.tile(c / c.sum(), (n, 1))
def hbin_pred(Htr, ytr, Hte, K, m=4.0):
    pi = (np.bincount(ytr, minlength=K) + 0.5); pi = pi / pi.sum()
    btr = np.digitize(Htr, HBINS); bte = np.digitize(Hte, HBINS); out = np.zeros((len(Hte), K))
    for b in np.unique(bte):
        c = np.bincount(ytr[btr == b], minlength=K).astype(float); out[bte == b] = (c + m * pi) / (c.sum() + m)
    return out
def qt_fit(X):
    return QuantileTransformer(n_quantiles=min(200, len(X)), output_distribution='normal', random_state=0).fit(X)
def inner_folds(y, seed, k=5):
    k = int(max(2, min(k, np.bincount(y).min())))
    return list(StratifiedKFold(k, shuffle=True, random_state=seed).split(np.zeros(len(y)), y))
def ll_of(p, y): return -np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)).mean()

def lr_predict(Xtr, ytr, Xte, K, seed):
    """L2 logistic regression; C chosen by inner 5-fold CV on log loss (nested)."""
    folds = inner_folds(ytr, seed); best, bestC = np.inf, LR_CS[0]
    for C in LR_CS:
        s = 0.0
        for a, b in folds:
            m = LogisticRegression(C=C, max_iter=500).fit(Xtr[a], ytr[a]); p = np.full((len(b), K), EPS); p[:, m.classes_] = m.predict_proba(Xtr[b])
            s += ll_of(clipn(p), ytr[b]) * len(b)
        if s < best - 1e-12: best, bestC = s, C
    m = LogisticRegression(C=bestC, max_iter=1000).fit(Xtr, ytr); p = np.full((len(Xte), K), EPS); p[:, m.classes_] = m.predict_proba(Xte)
    return clipn(p)

def knn_counts(Xa, ya, Xb, K, ks):
    kmax = min(max(ks), len(Xa)); nn = NearestNeighbors(n_neighbors=kmax).fit(Xa); idx = nn.kneighbors(Xb, return_distance=False)
    onehot = np.eye(K)[ya[idx]]; cum = onehot.cumsum(1)              # (nb, kmax, K)
    return {k: cum[:, min(k, kmax) - 1, :] for k in ks}
def knn_predict(Xtr, ytr, Xte, K, seed, alpha=2.0):
    """kNN class frequencies shrunk to the training prior with alpha pseudo-counts; k chosen by inner 5-fold CV on log loss."""
    ks = [k for k in KNN_KS if k <= max(5, len(ytr) // 3)] or [5]
    pi = (np.bincount(ytr, minlength=K) + 0.5); pi /= pi.sum()
    score = {k: 0.0 for k in ks}
    for a, b in inner_folds(ytr, seed):
        cnt = knn_counts(Xtr[a], ytr[a], Xtr[b], K, ks)
        for k in ks:
            p = (cnt[k] + alpha * pi) / (cnt[k].sum(1, keepdims=True) + alpha); score[k] += ll_of(clipn(p), ytr[b]) * len(b)
    kb = min(ks, key=lambda k: score[k]); c = knn_counts(Xtr, ytr, Xte, K, [kb])[kb]
    return clipn((c + alpha * pi) / (c.sum(1, keepdims=True) + alpha))

def gbt_predict(Xtr, ytr, Xte, K, seed):
    """Shallow gradient-boosted trees with early stopping on an internal 20% validation split."""
    n = len(ytr); small = n < 150 or np.bincount(ytr).min() < 10
    if small:      # too few objects for an internal validation split: a short, heavily regularised fit instead
        m = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=40, max_depth=2, min_samples_leaf=10, l2_regularization=2.0,
                                           early_stopping=False, random_state=seed).fit(Xtr, ytr)
    else:
        m = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_depth=3, min_samples_leaf=20 if n >= 400 else 10,
                                           l2_regularization=1.0, early_stopping=True, validation_fraction=0.2, n_iter_no_change=15,
                                           random_state=seed).fit(Xtr, ytr)
    p = np.full((len(Xte), K), EPS); p[:, m.classes_] = m.predict_proba(Xte); return clipn(p)

FEATS = {'orb': ORB, 'H': ['H'], 'orbH': ORB + ['H']}
def fit_all(Xd, y, tr, te, K, seed, models=('lr', 'knn', 'gbt'), feats=('orb', 'H', 'orbH'), extra_tr=None, ind=None, tag=''):
    """Xd: dict feature-set -> array for all rows. tr/te index arrays. extra_tr: additional training rows (regime T). ind: indicator column."""
    out = {}
    trf = tr if extra_tr is None else np.concatenate([tr, extra_tr])
    for f in feats:
        X = Xd[f]; q = qt_fit(X[trf]); Ztr, Zte = q.transform(X[trf]), q.transform(X[te])
        Rtr, Rte = X[trf], X[te]
        if ind is not None:
            Ztr_i = np.column_stack([Ztr, ind[trf]]); Zte_i = np.column_stack([Zte, ind[te]]); Rtr = np.column_stack([Rtr, ind[trf]]); Rte = np.column_stack([Rte, ind[te]])
        else: Ztr_i, Zte_i = Ztr, Zte
        if 'lr' in models: out['lr_%s%s' % (f, tag)] = lr_predict(Ztr_i, y[trf], Zte_i, K, seed)
        if 'knn' in models: out['knn_%s%s' % (f, tag)] = knn_predict(Ztr, y[trf], Zte, K, seed)
        if 'gbt' in models: out['gbt_%s%s' % (f, tag)] = gbt_predict(Rtr, y[trf], Rte, K, seed)
    return out

def one_fold(Xd, H, y, S_idx, tr_loc, te_loc, out_idx, K, seed, regimeT, models, feats):
    tr, te = S_idx[tr_loc], S_idx[te_loc]
    res = {'freq': freq_pred(y[tr], len(te), K), 'Hbin': hbin_pred(H[tr], y[tr], H[te], K)}
    res.update(fit_all(Xd, y, tr, te, K, seed, models, feats))
    if regimeT and len(out_idx):
        ind = np.zeros(len(y)); ind[S_idx] = 1.0
        res.update(fit_all(Xd, y, tr, te, K, seed, models, feats, extra_tr=out_idx, ind=ind, tag='@T'))
    return te_loc, res

def run_cv(d, y, S, K, reps, folds, seed, regimeT=True, models=('lr', 'knn', 'gbt'), feats=('orb', 'H', 'orbH'), n_jobs=30):
    """Returns dict model -> array (reps, nS, K) of out-of-fold probabilities for the subset rows (order of np.where(S))."""
    Xd = {f: d[c].values.astype(float) for f, c in FEATS.items()}; H = d.H.values.astype(float)
    S_idx = np.where(S)[0]; out_idx = np.where(~S)[0]; yS = y[S_idx]
    tasks = []
    for r in range(reps):
        skf = StratifiedKFold(folds, shuffle=True, random_state=seed + r)
        for f, (a, b) in enumerate(skf.split(np.zeros(len(yS)), yS)):
            tasks.append((r, a, b, seed + 1000 * r + f))
    outs = Parallel(n_jobs=n_jobs)(delayed(one_fold)(Xd, H, y, S_idx, a, b, out_idx, K, s, regimeT, models, feats) for r, a, b, s in tasks)
    P = {}
    for (r, a, b, s), (te_loc, res) in zip(tasks, outs):
        for k, p in res.items():
            P.setdefault(k, np.zeros((reps, len(S_idx), K)))[r, te_loc] = p
    return P, yS

# ------------------------------------------------------------------ scoring
def losses(P, yS, K):
    Y = np.eye(K)[yS]; LL = {}; BR = {}
    for k, p in P.items():
        LL[k] = (-np.log2(np.clip(p[:, np.arange(len(yS)), yS], 1e-12, 1))).mean(0)      # per object, mean over repeats
        BR[k] = ((p - Y[None]) ** 2).sum(2).mean(0)
    return LL, BR
def boot_ci(model, base, B, rng):
    """Paired bootstrap over objects of mean(base - model) and of 1 - mean(model)/mean(base)."""
    n = len(model); idx = rng.integers(0, n, (B, n)); mb = base[idx].mean(1); mm = model[idx].mean(1)
    d = mb - mm; pct = 100 * (1 - mm / mb)
    return dict(skill=float(base.mean() - model.mean()), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                pct=float(100 * (1 - model.mean() / base.mean())), pct_lo=float(np.percentile(pct, 2.5)), pct_hi=float(np.percentile(pct, 97.5)),
                p_le0=float((d <= 0).mean()))
def summarise(P, yS, K, B, seed):
    LL, BR = losses(P, yS, K); rng = np.random.default_rng(seed); out = {'n': int(len(yS)), 'counts': np.bincount(yS, minlength=K).tolist(),
        'LL_bits': {k: float(v.mean()) for k, v in LL.items()}, 'Brier': {k: float(v.mean()) for k, v in BR.items()}, 'contrasts': {}}
    pi = np.bincount(yS, minlength=K) / len(yS); out['H_class_bits'] = float(-(pi[pi > 0] * np.log2(pi[pi > 0])).sum())
    names = [k for k in P if k not in ('freq', 'Hbin')]
    def add(tag, m, b):
        if m in LL and b in LL:
            out['contrasts'][tag] = {'ll': boot_ci(LL[m], LL[b], B, rng), 'brier': boot_ci(BR[m], BR[b], B, rng)}
    add('Hbin|freq', 'Hbin', 'freq')
    for m in names:
        add('%s|freq' % m, m, 'freq'); add('%s|Hbin' % m, m, 'Hbin')
        fam, rest = m.split('_', 1); f = rest.split('@')[0]; t = '@T' if rest.endswith('@T') else ''
        if f == 'orbH': add('%s|%s_H%s' % (m, fam, t), m, '%s_H%s' % (fam, t))       # what orbit adds beyond H, same model family
        if f == 'orb': add('%s|%s_H%s' % (m, fam, t), m, '%s_H%s' % (fam, t))        # orbit-only versus H-only, same family (positive = orbit better)
    if K == 2:
        out['AUC'] = {k: float(np.mean([roc_auc_score(yS, p[r, :, 1]) for r in range(p.shape[0])])) for k, p in P.items() if k not in ('freq',)}
    return out, LL, BR

# ------------------------------------------------------------------ modes
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode'); ap.add_argument('labels'); ap.add_argument('out')
    ap.add_argument('--label', default='dark'); ap.add_argument('--subset', default='all'); ap.add_argument('--variant', default='main')
    ap.add_argument('--reps', type=int, default=10); ap.add_argument('--folds', type=int, default=5); ap.add_argument('--boot', type=int, default=4000)
    ap.add_argument('--seed', type=int, default=20261120); ap.add_argument('--nperm', type=int, default=200); ap.add_argument('--jobs', type=int, default=30)
    ap.add_argument('--nsim', type=int, default=40); ap.add_argument('--losses', default='')
    a = ap.parse_args()
    d, classes = load(a.labels, a.label, a.variant); K = len(classes); y = d.y.values.astype(int); S = subset_mask(d, a.subset)
    meta = dict(mode=a.mode, label=a.label, subset=a.subset, variant=a.variant, classes=classes, n_labelled_total=int(len(d)), n_subset=int(S.sum()),
                reps=a.reps, folds=a.folds, seed=a.seed, H_median_subset=float(d.H[S].median()), H_q05_q95=[float(d.H[S].quantile(.05)), float(d.H[S].quantile(.95))])
    print(json.dumps(meta), flush=True)
    if a.mode == 'cv':
        P, yS = run_cv(d, y, S, K, a.reps, a.folds, a.seed, regimeT=(a.subset != 'all'), n_jobs=a.jobs)
        res, LL, BR = summarise(P, yS, K, a.boot, a.seed)
        meta.update(res)
        if a.losses:
            pd.DataFrame({'pdes': d.pdes[S].values, 'y': yS, **{'ll_' + k: v for k, v in LL.items()}, **{'br_' + k: v for k, v in BR.items()}}).to_csv(a.losses, index=False)
    elif a.mode == 'perm':
        # observed statistic and null use the same protocol (reps x folds, regime W only)
        def stat(dd, yy, seed):
            P, yS = run_cv(dd, yy, S, K, a.reps, a.folds, seed, regimeT=False, n_jobs=1)
            LL, _ = losses(P, yS, K)
            o = {'%s_orb|freq' % m: float(LL['freq'].mean() - LL['%s_orb' % m].mean()) for m in ('lr', 'knn', 'gbt')}
            o.update({'%s_orbH|%s_H' % (m, m): float(LL['%s_H' % m].mean() - LL['%s_orbH' % m].mean()) for m in ('lr', 'knn', 'gbt')})
            o.update({'%s_orbH|Hbin' % m: float(LL['Hbin'].mean() - LL['%s_orbH' % m].mean()) for m in ('lr', 'knn', 'gbt')})
            return o
        obs = stat(d, y, a.seed)
        S_idx = np.where(S)[0]
        def null_labels(j):
            rng = np.random.default_rng(a.seed + 7919 * (j + 1)); yy = y.copy(); yy[S_idx] = rng.permutation(y[S_idx]); return stat(d, yy, a.seed + j + 1)
        def null_orbit_given_H(j):
            rng = np.random.default_rng(a.seed + 104729 * (j + 1)); dd = d.copy(); Hs = d.H.values[S_idx]
            edges = np.quantile(Hs, np.linspace(0, 1, max(2, min(8, len(S_idx) // 25)) + 1)[1:-1]); b = np.digitize(Hs, edges)
            for bb in np.unique(b):
                rows = S_idx[b == bb]; perm = rng.permutation(rows); dd.loc[rows, ORB] = d.loc[perm, ORB].values
            return stat(dd, y, a.seed + j + 1)
        nA = Parallel(n_jobs=a.jobs)(delayed(null_labels)(j) for j in range(a.nperm))
        nB = Parallel(n_jobs=a.jobs)(delayed(null_orbit_given_H)(j) for j in range(a.nperm))
        out = {}
        for k in obs:
            src = nA if k.endswith('|freq') else nB; v = np.array([x[k] for x in src])
            out[k] = dict(obs=obs[k], null_mean=float(v.mean()), null_sd=float(v.std()), null_q95=float(np.percentile(v, 95)), null_q99=float(np.percentile(v, 99)),
                          p=float((1 + (v >= obs[k]).sum()) / (len(v) + 1)), null=('labels shuffled' if k.endswith('|freq') else 'orbit rows shuffled within H bins'))
        meta['perm'] = out
    elif a.mode == 'inject':
        # synthetic binary labels: logit P = c + beta * s(x); beta tuned to give a target mutual information; prevalence kept at the observed one
        S_idx = np.where(S)[0]; dS = d.iloc[S_idx].reset_index(drop=True); n = len(dS); prev = float(y[S_idx].mean()) if K == 2 else 0.3
        from scipy.stats import norm, rankdata
        za = norm.ppf((rankdata(dS.a.values) - 0.5) / n)
        corner = ((dS.e.values < np.quantile(dS.e.values, 0.33)) & (dS.i.values < np.quantile(dS.i.values, 0.5))).astype(float); corner = (corner - corner.mean()) / corner.std()
        shapes = {'smooth_in_a': za, 'low_e_low_i_corner': corner}
        def h2(p): p = np.clip(p, 1e-12, 1 - 1e-12); return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
        def probs(s, beta):
            lo, hi = -20, 20
            for _ in range(60):
                c = 0.5 * (lo + hi); p = 1 / (1 + np.exp(-(c + beta * s)))
                if p.mean() > prev: hi = c
                else: lo = c
            return p
        def mi(s, beta): p = probs(s, beta); return h2(p.mean()) - h2(p).mean()
        def beta_for(s, target):
            lo, hi = 0.0, 20.0
            for _ in range(60):
                b = 0.5 * (lo + hi)
                if mi(s, b) > target: hi = b
                else: lo = b
            return 0.5 * (lo + hi)
        ones = np.ones(n, bool)
        def sim(shape, target, j):
            s = shapes[shape]; beta = beta_for(s, target) if target > 0 else 0.0; p = probs(s, beta)
            rng = np.random.default_rng(a.seed + 31 * j + int(1e6 * target) + (0 if shape == 'smooth_in_a' else 5000))
            for _ in range(50):
                yy = (rng.random(n) < p).astype(int)
                if min(yy.sum(), n - yy.sum()) >= 10: break
            P, yS = run_cv(dS, yy, ones, 2, a.reps, a.folds, a.seed + j, regimeT=False, feats=('orb',), n_jobs=1)
            LL, _ = losses(P, yS, 2); rng2 = np.random.default_rng(j); o = {}
            for m in ('lr', 'knn', 'gbt'):
                c = boot_ci(LL['%s_orb' % m], LL['freq'], 1000, rng2); o[m] = (c['skill'], c['lo'])
            # oracle: the true probabilities
            o['oracle'] = (float(LL['freq'].mean() + np.log2(np.where(yy == 1, p, 1 - p)).mean()), 0.0)
            return shape, target, o
        targets = [0.0, 0.01, 0.02, 0.05, 0.10]
        jobs = [(sh, t, j) for sh in shapes for t in targets for j in range(a.nsim)]
        outs = Parallel(n_jobs=a.jobs)(delayed(sim)(*jb) for jb in jobs)
        inj = {}
        for sh in shapes:
            for t in targets:
                rs = [o for s_, t_, o in outs if s_ == sh and t_ == t]; e = {}
                for m in ('lr', 'knn', 'gbt', 'oracle'):
                    sk = np.array([r[m][0] for r in rs]); lo = np.array([r[m][1] for r in rs])
                    e[m] = dict(mean_skill=float(sk.mean()), sd=float(sk.std()), frac_ci_above0=float((lo > 0).mean()))
                inj['%s|MI=%.2f' % (sh, t)] = e
        meta.update(inject=inj, n=n, prevalence=prev, nsim=a.nsim)
    json.dump(meta, open(a.out, 'w'), indent=1)
    print('wrote', a.out)

if __name__ == '__main__':
    main()
