import json, sys
base = sys.argv[1]
n = json.load(open(base + '/nhats.json'))['data']
s = json.load(open(base + '/sbdb_neo.json'))
F = s['fields']; idx = {f: i for i, f in enumerate(F)}
sb = {r[idx['pdes']]: r for r in s['data']}
def fl(x):
    try: return float(x)
    except Exception: return None
nh = {o['des']: o for o in n}
for d in ('2022 DC5', '2021 UH2', '2024 YP9', '2026 UY', '2012 EC'):
    r = sb.get(d)
    print(d, 'in NHATS' if d in nh else 'NOT in NHATS', None if r is None else {k: r[idx[k]] for k in ('full_name', 'H', 'rot_per', 'condition_code', 'data_arc', 'n_obs_used', 'first_obs', 'last_obs', 'a', 'e', 'i', 'albedo', 'diameter', 'spec_B')})
    if d in nh: print('   ', nh[d])
rows = []
for o in n:
    r = sb[o['des']]
    rows.append((o['des'], fl(o['h']), fl(o['min_dv']['dv']), fl(o['occ']), fl(r[idx['rot_per']]), o.get('obs_start'), o.get('obs_end'), fl(o.get('obs_mag')), o.get('obs_flag')))
print('dv<6, H<26.4, occ<=5, measured period > 1 h:')
for x in rows:
    if x[2] < 6 and x[1] is not None and x[1] < 26.4 and x[3] <= 5 and x[4] and x[4] > 1.0: print('  ', x)
print('dv<6, any H, period > 1 h:')
for x in rows:
    if x[2] < 6 and x[4] and x[4] > 1.0: print('  ', x)
# gate status three-way for H cut alternatives at dv<5 and dv<6
for hc, lab in ((24, 'plan H<24 (55 m)'), (25.3, '30 m (Michel)'), (26.4, '18 m (Elvis water)')):
    for dvc in (5, 6, 7):
        B = [x for x in rows if x[2] < dvc and x[1] is not None and x[1] < hc and x[3] <= 5]
        unk = sum(1 for x in B if x[4] is None); fast = sum(1 for x in B if x[4] is not None and x[4] <= 2.2); slow = sum(1 for x in B if x[4] is not None and x[4] > 2.2)
        print(f'{lab} dv<{dvc}: pass size+orbit {len(B)}: slow {slow}, fast {fast}, unknown {unk}')
# how many of the 286 / 726 have a listed window at all, pointable, before 2030
for dvc in (5, 6):
    A = [x for x in rows if x[2] < dvc]
    w = [x for x in A if x[5]]
    p = [x for x in w if x[8] != 'S']
    p30 = [x for x in p if x[5] < '2030-01-01']
    p30v = [x for x in p30 if x[7] < 22]
    print(dvc, 'n', len(A), 'window', len(w), 'pointable', len(p), 'before 2030', len(p30), 'V<22', len(p30v))
