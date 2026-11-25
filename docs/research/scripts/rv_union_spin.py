import json, sys, os
base, cov = sys.argv[1], sys.argv[2]
sp = json.load(open(os.path.join(cov, 'spin_periods.json')))
n = json.load(open(os.path.join(base, 'nhats.json')))['data']
s = json.load(open(os.path.join(base, 'sbdb_neo.json')))
idx = {f: i for i, f in enumerate(s['fields'])}
sb = {r[idx['pdes']]: r for r in s['data']}
def fl(x):
    try: return float(x)
    except Exception: return None
def dv(o): return float(o['min_dv']['dv'])
def H(o):
    v = fl(o['h']); return 99.0 if v is None else v
def per(des):
    e = sp.get(des)
    if not e: return None, None
    return e.get('P_any'), e
print('entries', len(sp), 'nhats entries with P_any', sum(1 for k, v in sp.items() if v.get('nhats') and v.get('P_any') is not None))
for lim in (5, 6, 7):
    A = [o for o in n if dv(o) < lim]
    print('dv<%d with union period:' % lim, sum(1 for o in A if per(o['des'])[0] is not None), ' sbdb only:', sum(1 for o in A if fl(sb[o['des']][idx['rot_per']]) is not None))
    C = [o for o in A if H(o) < 24 and int(o['occ']) <= 5]
    D = [o for o in C if per(o['des'])[0] is not None]
    E = [o for o in D if per(o['des'])[0] > 2.2]
    print('  sieve with union periods: bright&orbit %d, period %d, slow %d, fast %d, unknown %d' % (len(C), len(D), len(E), len(D) - len(E), len(C) - len(D)))
    if lim == 6:
        for o in C:
            p, e = per(o['des'])
            print('   ', o['des'], 'H', o['h'], 'union P', p, 'sbdb', sb[o['des']][idx['rot_per']], (e or {}).get('P_lcdb'), (e or {}).get('P_card'))
