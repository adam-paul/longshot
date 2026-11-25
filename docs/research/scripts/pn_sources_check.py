#!/usr/bin/env python3
"""Cross-check 'nu6 is the top source for >99.9% of NHATS objects' against PUBLISHED per-object source-region values
(no model file needed): Marsset+2022 table 7 (Granvik 2018 escape-route probabilities per object) and Sergeyev+2023 (Origin).
Also the albedo-class x taxonomy cross-tab for the cleaned labels and LRT upper limits.
Usage: pn_sources_check.py <labels.csv> <vizier_dir> <nhats.json> <univar.json>"""
import sys, os, re, json, collections
import numpy as np, pandas as pd
from scipy import stats, optimize
lab, V, nh_fn, uni = sys.argv[1:5]
d = pd.read_csv(lab, dtype={'pdes': str})
nh = {o['des']: (float(o['min_dv']['dv']), float(o['h']) if o['h'] else np.nan) for o in json.load(open(nh_fn))['data']}
def parse_vizier(fn):
    tables = {}; name = None; state = 0
    for line in open(fn, errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#Name:'): name = line.split(':', 1)[1].strip(); state = 0; continue
        if line.startswith('#') or not line.strip(): continue
        if name is None: continue
        if state == 0: tables[name] = {'cols': [c.strip() for c in line.split('\t')], 'rows': []}; state = 1
        elif state == 1: state = 2
        elif state == 2: state = 3
        else: tables[name]['rows'].append([c.strip() for c in line.split('\t')])
    return tables
# --- Marsset+2022
T = parse_vizier(os.path.join(V, 'J_AJ_163_165.tsv'))['J/AJ/163/165/table7']
ER = ['P[Hun]', 'P[nu6]', 'P[Pho]', 'P[3:1J]', 'P[5:2J]', 'P[2:1J]', 'P[JFC]']
seen = {}
for r in T['rows']:
    x = dict(zip(T['cols'], r)); num = x['Number'].strip(); des = x['Desig'].strip()
    key = num if num else des
    try: p = [float(x[c]) for c in ER]
    except ValueError: continue
    seen[key] = (des, num, p, float(x['a']), float(x['Hmag']))
print('Marsset+2022 objects with ER probabilities:', len(seen))
top = collections.Counter(ER[int(np.argmax(v[2]))] for v in seen.values()); print('  top ER, all objects:', dict(top))
# NHATS members among them: match by number or designation
nh_keys = set(nh)
mem = [(k, v) for k, v in seen.items() if k in nh_keys or v[0] in nh_keys or v[1] in nh_keys]
print('  of which NHATS members:', len(mem))
if mem:
    top = collections.Counter(ER[int(np.argmax(v[2]))] for _, v in mem); print('  top ER among NHATS members:', dict(top))
    P = np.array([v[2] for _, v in mem]); print('  mean ER probabilities (NHATS members):', dict(zip(ER, P.mean(0).round(3))))
    print('  P[nu6] 10th-90th pct: %.2f-%.2f ; H range %.1f-%.1f' % (np.percentile(P[:, 1], 10), np.percentile(P[:, 1], 90), min(v[4] for _, v in mem), max(v[4] for _, v in mem)))
    for k, v in mem:
        if int(np.argmax(v[2])) != 1: print('    not nu6-top:', k, v[0], 'a=%.2f H=%.1f' % (v[3], v[4]), dict(zip(ER, np.round(v[2], 2))))
box = [(k, v) for k, v in seen.items() if v[3] < 2.0]
top = collections.Counter(ER[int(np.argmax(v[2]))] for _, v in box); print('  top ER among a<2 au objects (n=%d):' % len(box), dict(top))
# --- Sergeyev+2023
T = parse_vizier(os.path.join(V, 'J_A_A_679_A148.tsv'))['J/A+A/679/A148/catalog']
rows = [dict(zip(T['cols'], r)) for r in T['rows']]
o_all = collections.Counter(r['Origin'] for r in rows if r['Origin']); print('Sergeyev+2023 objects with Origin:', sum(o_all.values()), dict(o_all))
def keyset(r):
    ks = set()
    if r['Number']: ks.add(r['Number'])
    if r['Design']: ks.add(r['Design'])
    return ks
m = [r for r in rows if r['Origin'] and (keyset(r) & nh_keys)]
print('  NHATS members with Origin:', len(m), dict(collections.Counter(r['Origin'] for r in m)))
m2 = [r for r in rows if r['Origin'] and float(r['a']) < 2.0]
print('  a<2 au with Origin:', len(m2), dict(collections.Counter(r['Origin'] for r in m2)))

# --- cleaned cross-tab albedo class x taxonomy
x = d[d.alb.notna() & d.tax4.notna()]
print('\nmeasured-albedo x taxonomy cross-tab (rows: complex; columns: dark = pV<0.10):')
print(pd.crosstab(x.tax4, x.alb < 0.10, margins=True).to_string())
print('P(dark | complex):', (x.groupby('tax4')['alb'].apply(lambda s: (s < 0.1).mean())).round(3).to_dict())
print('P(C | dark) = %.3f ; P(S | dark) = %.3f ; P(X | dark) = %.3f' % tuple(((x.tax4 == c) & (x.alb < .1)).sum() / (x.alb < .1).sum() for c in 'CSX'))

# --- LRT upper limits: 95% upper bound on the non-centrality, expressed as bits per object
print('\nLikelihood-ratio tests: 95% upper limit on linear-logistic information (bits/object) and the level detectable with 80% power')
U = json.load(open(uni))
def upper(chi2, df):
    f = lambda lam: stats.ncx2.cdf(chi2, df, lam) - 0.05
    if stats.chi2.cdf(chi2, df) < 0.05: return 0.0
    return optimize.brentq(f, 1e-9, 500)
def lam80(df):
    crit = stats.chi2.ppf(0.95, df); return optimize.brentq(lambda lam: stats.ncx2.sf(crit, df, lam) - 0.8, 0.01, 200)
for k, r in U.items():
    if 'lrt_orbit_vs_null' not in r: continue
    n = r['n']; c = 2 * n * np.log(2); out = []
    for t in ('lrt_orbit_vs_null', 'lrt_orbit_given_H', 'lrt_H_vs_null'):
        chi2, df = r[t]['chi2'], r[t]['df']
        out.append('%s: p=%.2g, <%.4f bits (95%%), 80%%-power level %.4f' % (t[4:], r[t]['p'], upper(chi2, df) / c, lam80(df) / c))
    print('%-34s n=%4d entropy %.3f | ' % (k, n, r['class_entropy_bits']) + ' | '.join(out))
