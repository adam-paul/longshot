#!/usr/bin/env python3
"""Emit the markdown tables used in the report from the pn_cv.py JSON outputs. Usage: pn_tables.py <out_dir>"""
import sys, os, json, glob

O = sys.argv[1]
SUB = [('all', 'All NEAs'), ('a2', 'a < 2 au'), ('nhats', 'NHATS members'), ('box', 'NHATS-like box')]
LAB = [('dark', 'dark (pV < 0.10)'), ('sq', 'S/Q vs rest'), ('tax4', 'S/Q, C, X, other')]
def load(lab, sub, var='main'):
    fn = os.path.join(O, 'cv', '%s.%s.%s.json' % (lab, sub, var))
    return json.load(open(fn)) if os.path.exists(fn) else None
def cell(c, key='ll', pct=True):
    c = c[key]; s = '%+.3f [%+.3f, %+.3f]' % (c['skill'], c['lo'], c['hi'])
    return s + (' (%+.1f%%)' % c['pct'] if pct else '')
def best(r, pat):
    """Largest point skill among the three model families and both training regimes for a contrast pattern like '{m}_orb{t}|freq'."""
    ks = [pat.format(m=m, t=t) for m in ('lr', 'knn', 'gbt') for t in ('', '@T')]
    ks = [k for k in ks if k in r['contrasts']]
    k = max(ks, key=lambda k: r['contrasts'][k]['ll']['skill']); return k, r['contrasts'][k]
def nm(k):
    m = k.split('|')[0]; fam = m.split('_')[0]; return {'lr': 'logistic', 'knn': 'k-NN', 'gbt': 'trees'}[fam] + (', pooled training' if m.endswith('@T') else '')

print('### Table A. Orbit only against the class frequency (log-loss skill, bits per object [95% interval] and percent of baseline loss)\n')
print('| Subset | Label | n | Class counts | Class entropy (bits) | Logistic regression | k-nearest-neighbour | Boosted trees | Best of six (model, training set) | AUC range |')
print('|---|---|---|---|---|---|---|---|---|---|')
for sub, sname in SUB:
    for lab, lname in LAB:
        r = load(lab, sub)
        if r is None: continue
        c = r['contrasts']; k, b = best(r, '{m}_orb{t}|freq')
        auc = ''
        if 'AUC' in r:
            v = [r['AUC'][x] for x in r['AUC'] if '_orb' in x and 'orbH' not in x]; auc = '%.2f-%.2f' % (min(v), max(v))
        print('| %s | %s | %d | %s | %.3f | %s | %s | %s | %s: %s | %s |' % (sname, lname, r['n'], '/'.join(str(x) for x in r['counts']), r['H_class_bits'],
              cell(c['lr_orb|freq']), cell(c['knn_orb|freq']), cell(c['gbt_orb|freq']), nm(k), cell(b), auc))

print('\n### Table B. H only against the class frequency, and orbit against H\n')
print('| Subset | Label | H-binned frequency vs class frequency | H only, logistic vs class frequency | Best H-only of six | Orbit+H vs H-binned frequency, logistic | Best orbit+H vs H-binned of six | Orbit+H vs H only, same model, logistic | Orbit only minus H only, logistic (positive = orbit better) |')
print('|---|---|---|---|---|---|---|---|---|')
for sub, sname in SUB:
    for lab, lname in LAB:
        r = load(lab, sub)
        if r is None: continue
        c = r['contrasts']; k, b = best(r, '{m}_H{t}|freq'); k2, b2 = best(r, '{m}_orbH{t}|Hbin')
        print('| %s | %s | %s | %s | %s: %s | %s | %s: %s | %s | %s |' % (sname, lname, cell(c['Hbin|freq']), cell(c['lr_H|freq']), nm(k), cell(b), cell(c['lr_orbH|Hbin']), nm(k2), cell(b2),
              cell(c['lr_orbH|lr_H'], pct=False), cell(c['lr_orb|lr_H'], pct=False)))

print('\n### Table C. Brier-score skill (multi-class Brier, sum of squared errors; positive = better than baseline)\n')
print('| Subset | Label | Brier, class frequency | Brier, H-binned | Orbit only vs frequency, logistic | H only vs frequency, logistic | Orbit+H vs H-binned, logistic | Orbit+H vs H-binned, trees |')
print('|---|---|---|---|---|---|---|---|')
for sub, sname in SUB:
    for lab, lname in LAB:
        r = load(lab, sub)
        if r is None: continue
        c = r['contrasts']
        print('| %s | %s | %.4f | %.4f | %s | %s | %s | %s |' % (sname, lname, r['Brier']['freq'], r['Brier']['Hbin'], cell(c['lr_orb|freq'], 'brier'), cell(c['lr_H|freq'], 'brier'),
              cell(c['lr_orbH|Hbin'], 'brier'), cell(c['gbt_orbH|Hbin'], 'brier')))

print('\n### Table D. Sensitivity variants (logistic regression, trained inside the subset; log-loss skill in bits)\n')
print('| Run | n | Class counts | Orbit only vs frequency | H only vs frequency | Orbit+H vs H-binned | AUC orbit / H |')
print('|---|---|---|---|---|---|---|')
VAR = [('dark', 'all', 'neowise', 'All NEAs, dark, NEOWISE fits only'), ('dark', 'all', 'spitzer', 'All NEAs, dark, Spitzer only'), ('dark', 'all', 'clear', 'All NEAs, dark, clear labels'),
       ('dark', 'a2', 'neowise', 'a < 2 au, dark, NEOWISE fits only'), ('dark', 'a2', 'spitzer', 'a < 2 au, dark, Spitzer only'), ('dark', 'a2', 'clear', 'a < 2 au, dark, clear labels'),
       ('dark', 'nhats', 'neowise', 'NHATS, dark, NEOWISE fits only'), ('dark', 'nhats', 'spitzer', 'NHATS, dark, Spitzer only'), ('dark', 'nhats', 'clear', 'NHATS, dark, clear labels'),
       ('sq', 'a2', 'spec', 'a < 2 au, S/Q vs rest, spectra only'), ('sq', 'nhats', 'spec', 'NHATS, S/Q vs rest, spectra only'),
       ('tax4', 'a2', 'spec', 'a < 2 au, four classes, spectra only'), ('tax4', 'nhats', 'spec', 'NHATS, four classes, spectra only'),
       ('dark', 'a2plus', 'main', 'a >= 2 au, dark'), ('sq', 'a2plus', 'main', 'a >= 2 au, S/Q vs rest'), ('tax4', 'a2plus', 'main', 'a >= 2 au, four classes'),
       ('dark', 'small', 'main', 'H >= 22 (any orbit), dark'), ('sq', 'small', 'main', 'H >= 22 (any orbit), S/Q vs rest'), ('tax4', 'small', 'main', 'H >= 22 (any orbit), four classes'),
       ('dark', 'nhats_small', 'main', 'NHATS and H >= 24, dark'), ('sq', 'nhats_small', 'main', 'NHATS and H >= 24, S/Q vs rest'), ('tax4', 'nhats_small', 'main', 'NHATS and H >= 24, four classes')]
for lab, sub, var, name in VAR:
    r = load(lab, sub, var)
    if r is None: continue
    c = r['contrasts']; auc = '%.2f / %.2f' % (r['AUC']['lr_orb'], r['AUC']['lr_H']) if 'AUC' in r else ''
    print('| %s | %d | %s | %s | %s | %s | %s |' % (name, r['n'], '/'.join(str(x) for x in r['counts']), cell(c['lr_orb|freq']), cell(c['lr_H|freq']), cell(c['lr_orbH|Hbin']), auc))

print('\n### Table E. Permutation nulls (300 shuffles; trained inside the subset; skill in bits)\n')
print('| Subset, label | n | Contrast | Observed | Null mean | Null 95th pct | p |')
print('|---|---|---|---|---|---|---|')
for fn in sorted(glob.glob(os.path.join(O, 'perm', '*.json'))):
    r = json.load(open(fn)); name = os.path.basename(fn)[:-5]
    for k in ('lr_orb|freq', 'gbt_orb|freq', 'lr_orbH|lr_H', 'gbt_orbH|gbt_H', 'lr_orbH|Hbin'):
        v = r['perm'][k]; print('| %s | %d | %s | %+.4f | %+.4f | %+.4f | %.3f |' % (name, r['n_subset'], k, v['obs'], v['null_mean'], v['null_q95'], v['p']))
ps = [v['p'] for fn in glob.glob(os.path.join(O, 'perm', '*.json')) for v in json.load(open(fn))['perm'].values()]
if ps: print('\nAll permutation tests: %d contrasts, %d with p < 0.05, smallest p = %.3f.' % (len(ps), sum(p < 0.05 for p in ps), min(ps)))

print('\n### Table F. Injection-recovery (synthetic labels on the real orbits; mean log-loss skill of the orbit-only model and the share of 40 trials whose 95% interval excludes zero)\n')
print('| Subset, label prevalence | n | Injected pattern | Injected information (bits) | Oracle skill | Logistic: mean skill, detected | k-NN | Trees |')
print('|---|---|---|---|---|---|---|---|')
for fn in sorted(glob.glob(os.path.join(O, 'inject', '*.json'))):
    r = json.load(open(fn)); name = os.path.basename(fn)[:-5]
    for k, e in r['inject'].items():
        sh, t = k.split('|MI=')
        print('| %s (%.0f%% positive) | %d | %s | %s | %+.3f | %+.3f, %.0f%% | %+.3f, %.0f%% | %+.3f, %.0f%% |' % (name, 100 * r['prevalence'], r['n'], sh.replace('_', ' '), t, e['oracle']['mean_skill'],
              e['lr']['mean_skill'], 100 * e['lr']['frac_ci_above0'], e['knn']['mean_skill'], 100 * e['knn']['frac_ci_above0'], e['gbt']['mean_skill'], 100 * e['gbt']['frac_ci_above0']))
