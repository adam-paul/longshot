#!/usr/bin/env python3
"""Print compact tables from the pn_cv.py outputs. Usage: pn_summary.py <out_dir>"""
import sys, os, json, glob

O = sys.argv[1]
def f(c, key='ll'):
    c = c[key]; return '%+.4f [%+.4f,%+.4f] %+5.1f%%' % (c['skill'], c['lo'], c['hi'], c['pct'])
def best(res, feat, tag, base):
    """Best of the three model families for this feature set (optimistic for the model; conservative for a null claim)."""
    ks = ['%s_%s%s|%s' % (m, feat, tag, base) for m in ('lr', 'knn', 'gbt')]
    ks = [k for k in ks if k in res['contrasts']]
    if not ks: return None, None
    k = max(ks, key=lambda k: res['contrasts'][k]['ll']['skill']); return k, res['contrasts'][k]

print('Skill = baseline log loss minus model log loss, bits per object (positive = model better); [95% paired bootstrap over objects]; % of baseline loss removed.')
print('W = trained inside the subset only; T = trained on subset-train plus every labelled NEA outside the subset.\n')
for fn in sorted(glob.glob(os.path.join(O, 'cv', '*.json'))):
    r = json.load(open(fn)); nm = os.path.basename(fn)[:-5]
    print('=' * 130)
    print('%s  n=%d  class counts %s=%s  class entropy %.3f bits  H median %.1f (5-95%%: %.1f-%.1f)' % (
        nm, r['n'], r['classes'], r['counts'], r['H_class_bits'], r['H_median_subset'], r['H_q05_q95'][0], r['H_q05_q95'][1]))
    print('  log loss (bits): freq %.4f | H-binned %.4f     Brier: freq %.4f | H-binned %.4f' % (r['LL_bits']['freq'], r['LL_bits']['Hbin'], r['Brier']['freq'], r['Brier']['Hbin']))
    print('  H-binned vs freq:                 ', f(r['contrasts']['Hbin|freq']), '   Brier', f(r['contrasts']['Hbin|freq'], 'brier'))
    for tag, reg in (('', 'W'), ('@T', 'T')):
        if 'lr_orb%s|freq' % tag not in r['contrasts']: continue
        for m in ('lr', 'knn', 'gbt'):
            c = r['contrasts']
            print('  [%s] %-3s orbit|freq %s   H|freq %s   orbit+H|H-binned %s   orbit+H|H(same model) %s   orbit|H(same model) %s' % (
                reg, m, f(c['%s_orb%s|freq' % (m, tag)]), f(c['%s_H%s|freq' % (m, tag)]), f(c['%s_orbH%s|Hbin' % (m, tag)]),
                f(c['%s_orbH%s|%s_H%s' % (m, tag, m, tag)]), f(c['%s_orb%s|%s_H%s' % (m, tag, m, tag)])))
            print('          Brier: orbit|freq %s   H|freq %s   orbit+H|H-binned %s' % (
                f(c['%s_orb%s|freq' % (m, tag)], 'brier'), f(c['%s_H%s|freq' % (m, tag)], 'brier'), f(c['%s_orbH%s|Hbin' % (m, tag)], 'brier')))
    if 'AUC' in r:
        print('  AUC:', '  '.join('%s %.3f' % (k, v) for k, v in sorted(r['AUC'].items())))

print('\n\n######## permutation nulls (regime W)')
for fn in sorted(glob.glob(os.path.join(O, 'perm', '*.json'))):
    r = json.load(open(fn)); print(os.path.basename(fn)[:-5], 'n=%d' % r['n_subset'])
    for k, v in r['perm'].items():
        print('   %-18s obs %+.4f  null mean %+.4f sd %.4f  q95 %+.4f  p=%.3f  (%s)' % (k, v['obs'], v['null_mean'], v['null_sd'], v['null_q95'], v['p'], v['null']))

print('\n\n######## injection-recovery (synthetic labels with known orbit->class information, real orbits, real n)')
for fn in sorted(glob.glob(os.path.join(O, 'inject', '*.json'))):
    r = json.load(open(fn)); print(os.path.basename(fn)[:-5], 'n=%d prevalence %.3f nsim %d' % (r['n'], r['prevalence'], r['nsim']))
    for k, e in r['inject'].items():
        print('   %-32s ' % k + '  '.join('%s: mean %+.4f sd %.4f detect %.2f' % (m, e[m]['mean_skill'], e[m]['sd'], e[m]['frac_ci_above0']) for m in ('lr', 'knn', 'gbt')) + '  oracle %+.4f' % e['oracle']['mean_skill'])
