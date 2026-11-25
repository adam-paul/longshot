import json, sys
d = sys.argv[1]
n = json.load(open(d + '/nhats.json'))['data']
s = json.load(open(d + '/sbdb_neo.json'))
idx = {f: i for i, f in enumerate(s['fields'])}
sb = {r[idx['pdes']]: r for r in s['data']}
def fl(x):
    try: return float(x)
    except Exception: return None
def dv(o): return float(o['min_dv']['dv'])
def H(o):
    v = fl(o['h']); return 99.0 if v is None else v
print('H missing:', [(o['des'], o['min_dv']['dv']) for o in n if fl(o['h']) is None])
for lim in (6, 7):
    C = [o for o in n if dv(o) < lim and H(o) < 24 and int(o['occ']) <= 5]
    norot = [o for o in C if fl(sb[o['des']][idx['rot_per']]) is None]
    print('--- dv<%d: H<24 & occ<=5: %d; no period: %d' % (lim, len(C), len(norot)))
    def yr(o):
        return int(o['obs_start'][:4]) if o.get('obs_start') else None
    nowin = [o for o in norot if not o.get('obs_start')]
    b2028 = [o for o in norot if yr(o) and yr(o) < 2028]
    b2030 = [o for o in norot if yr(o) and yr(o) < 2030]
    print(' no listed window:', len(nowin), ' window starting before 2028:', len(b2028), ' before 2030:', len(b2030))
    for cut in (18, 20, 21, 22):
        print('  before 2030 and peak V <', cut, ':', sum(1 for o in b2030 if fl(o['obs_mag']) is not None and fl(o['obs_mag']) < cut),
              '| any year peak V <', cut, ':', sum(1 for o in norot if fl(o.get('obs_mag')) is not None and fl(o['obs_mag']) < cut))
    print('  flagged survey-only among no-period:', sum(1 for o in norot if (o.get('obs_flag') or '').strip() == 'S'))
    if lim == 7:
        for o in sorted(b2030, key=lambda o: o['obs_start']):
            print('   ', o['des'], 'H', o['h'], 'dv', o['min_dv']['dv'], o['obs_start'], o['obs_end'], 'V', o['obs_mag'], repr(o['obs_flag']))
# per-object file count
print('files at 2 per object:', 2*len(n), '; years to 20,000 at 650 new/yr:', round((20000-2*len(n))/(2*650), 1))
# 12-object gold power check
from math import comb
def cdf(k, nn, p): return sum(comb(nn, i)*p**i*(1-p)**(nn-i) for i in range(k+1))
for crit in (3, 4):
    print('reject if misses >=%d: alpha=%.3f power(60%%)=%.3f power(70%%)=%.3f' % (crit, 1-cdf(crit-1, 12, 0.1), 1-cdf(crit-1, 12, 0.4), 1-cdf(crit-1, 12, 0.3)))
