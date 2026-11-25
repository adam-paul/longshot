#!/usr/bin/env python3
"""Turn the injection-recovery runs into detection rates under a permutation-style threshold.
The 'CI excludes zero' rule is conservative because a fitted model pays an estimation penalty (its null mean is below zero).
Here: threshold = 95th percentile of the skill under no injected signal (normal approximation from the MI=0 trials);
power = share of injected trials expected above it; and how far the OBSERVED real-data skill sits from each injected level.
Usage: pn_inject_power.py <out_dir>"""
import sys, os, json, glob
from scipy.stats import norm
O = sys.argv[1]
OBS = {}
for fn in glob.glob(os.path.join(O, 'cv', '*.main.json')):
    r = json.load(open(fn)); lab, sub, _ = os.path.basename(fn).split('.')[:3]
    OBS[(lab, sub)] = {m: r['contrasts']['%s_orb|freq' % m]['ll']['skill'] for m in ('lr', 'knn', 'gbt')}
for fn in sorted(glob.glob(os.path.join(O, 'inject', '*.json'))):
    r = json.load(open(fn)); lab, sub = os.path.basename(fn)[:-5].split('.')
    print('%s.%s  n=%d  prevalence %.2f   observed real-data orbit-only skill: %s' % (lab, sub, r['n'], r['prevalence'], {m: round(v, 4) for m, v in OBS[(lab, sub)].items()}))
    for sh in ('smooth_in_a', 'low_e_low_i_corner'):
        null = r['inject']['%s|MI=0.00' % sh]
        for t in ('0.01', '0.02', '0.05', '0.10'):
            e = r['inject']['%s|MI=%s' % (sh, t)]; out = []
            for m in ('lr', 'knn', 'gbt'):
                thr = null[m]['mean_skill'] + 1.645 * null[m]['sd']
                power = norm.sf((thr - e[m]['mean_skill']) / max(e[m]['sd'], 1e-9))
                z = (OBS[(lab, sub)][m] - e[m]['mean_skill']) / max(e[m]['sd'], 1e-9)
                out.append('%s: mean %+.3f sd %.3f power %.0f%% obs z=%+.1f (p=%.3f)' % (m, e[m]['mean_skill'], e[m]['sd'], 100 * power, z, norm.cdf(z)))
            print('   %-20s injected %s bits (oracle %+.3f) | ' % (sh, t, e['oracle']['mean_skill']) + ' | '.join(out))
