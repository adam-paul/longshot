import json, sys
base = sys.argv[1]
n = json.load(open(base + '/nhats.json'))['data']
s = json.load(open(base + '/sbdb_neo.json'))
F = s['fields']; idx = {f: i for i, f in enumerate(F)}
sb = {r[idx['pdes']]: r for r in s['data']}
def fl(x):
    try: return float(x)
    except Exception: return None
rows = []
for o in n:
    r = sb[o['des']]
    a = fl(r[idx['a']])
    syn = 1 / abs(1 - a ** -1.5) if a and abs(a - 1) > 1e-4 else None
    rows.append(dict(des=o['des'], h=fl(o['h']), dv=fl(o['min_dv']['dv']), occ=fl(o['occ']), rot=fl(r[idx['rot_per']]), alb=fl(r[idx['albedo']]), diam=fl(r[idx['diameter']]),
                     spec=(r[idx['spec_B']], r[idx['spec_T']]), os=o.get('obs_start'), oe=o.get('obs_end'), om=fl(o.get('obs_mag')), flag=o.get('obs_flag'), syn=syn, i=fl(r[idx['i']])))
print('dv<6 with SBDB albedo or spec:')
for x in sorted([x for x in rows if x['dv'] < 6 and (x['alb'] is not None or x['spec'][0] or x['spec'][1])], key=lambda t: t['dv']):
    print('  ', x['des'], 'H', x['h'], 'dv', x['dv'], 'occ', x['occ'], 'rot', x['rot'], 'alb', x['alb'], 'D km', x['diam'], x['spec'], 'win', x['os'], x['om'], 'syn', round(x['syn'], 1) if x['syn'] else None)
print('dv<7, H<24, occ<=5 (the 42): with albedo/spec')
for x in [x for x in rows if x['dv'] < 7 and x['h'] is not None and x['h'] < 24 and x['occ'] <= 5 and (x['alb'] is not None or x['spec'][0] or x['spec'][1])]:
    print('  ', x['des'], 'H', x['h'], 'dv', x['dv'], 'rot', x['rot'], 'alb', x['alb'], 'D km', x['diam'], x['spec'])
dark = [x for x in rows if x['alb'] is not None and x['alb'] <= 0.10]
print('NHATS with SBDB albedo<=0.10:', len(dark), ' dv<7:', len([x for x in dark if x['dv'] < 7]), ' dv<6:', len([x for x in dark if x['dv'] < 6]))
for x in sorted([x for x in dark if x['dv'] < 7], key=lambda t: t['dv']):
    print('  ', x['des'], 'H', x['h'], 'dv', x['dv'], 'occ', x['occ'], 'rot', x['rot'], 'alb', x['alb'], 'D km', x['diam'], x['spec'], 'win', x['os'], x['om'])
