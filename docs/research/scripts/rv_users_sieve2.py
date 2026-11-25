import json, sys, statistics as st, math
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
    rows.append(dict(des=o['des'], h=fl(o['h']), dv=fl(o['min_dv']['dv']), dvdur=o['min_dv']['dur'],
        occ=fl(o['occ']), flag=o.get('obs_flag'), os=o.get('obs_start'), oe=o.get('obs_end'), om=fl(o.get('obs_mag')),
        mins=fl(o['min_size']), maxs=fl(o['max_size']), rot=fl(r[idx['rot_per']]), ntraj=o.get('n_via_traj'),
        a=fl(r[idx['a']]), e=fl(r[idx['e']]), i=fl(r[idx['i']]), arc=fl(r[idx['data_arc']]),
        A1=fl(r[idx['A1']]), A2=fl(r[idx['A2']]), spec=(r[idx['spec_B']], r[idx['spec_T']]), alb=fl(r[idx['albedo']]), diam=fl(r[idx['diameter']]),
        last=r[idx['last_obs']]))
print('H None:', sum(1 for x in rows if x['h'] is None), 'occ None', sum(1 for x in rows if x['occ'] is None))
print('dv<7', sum(x['dv'] < 7 for x in rows), 'dv<=7', sum(x['dv'] <= 7 for x in rows), 'dv<6.99', sum(x['dv'] < 6.995 for x in rows))
A5 = [x for x in rows if x['dv'] < 5]
hs = sorted(x['h'] for x in A5 if x['h'] is not None)
print('dv<5 brightest H', hs[:8], 'median', st.median(hs), 'n', len(hs))
print('dv<5: H<25', sum(h < 25 for h in hs), 'H<26', sum(h < 26 for h in hs), 'H<26.4', sum(h < 26.4 for h in hs), 'H>=27', sum(h >= 27 for h in hs), 'H>=28', sum(h >= 28 for h in hs))
print('dv<5 max_size>=100', sum(1 for x in A5 if x['maxs'] and x['maxs'] >= 100), 'min_size>=30', sum(1 for x in A5 if x['mins'] and x['mins'] >= 30))
print('dv<5 occ<=5', sum(1 for x in A5 if x['occ'] is not None and x['occ'] <= 5), 'rot known', sum(1 for x in A5 if x['rot']), [ (x['des'],x['h'],x['rot']) for x in A5 if x['rot']])
def show(x):
    return (x['des'], 'H', x['h'], 'dv', x['dv'], 'occ', x['occ'], 'rot', x['rot'], 'win', x['os'], x['oe'], 'V', x['om'], 'flag', x['flag'], 'ntraj', x['ntraj'], 'spec', x['spec'], 'alb', x['alb'], 'D', x['diam'])
print('=== row 2-5 members, dv<6, H<24')
for x in sorted([x for x in rows if x['dv'] < 6 and x['h'] is not None and x['h'] < 24], key=lambda t: t['dv']):
    print(show(x))
print('=== dv<7 H<24 occ<=5: status counts')
B = [x for x in rows if x['dv'] < 7 and x['h'] is not None and x['h'] < 24 and x['occ'] is not None and x['occ'] <= 5]
unk = [x for x in B if x['rot'] is None]
fast = [x for x in B if x['rot'] is not None and x['rot'] <= 2.2]
slow = [x for x in B if x['rot'] is not None and x['rot'] > 2.2]
print(len(B), 'unknown', len(unk), 'fast', len(fast), 'slow', len(slow))
print('fast:', [(x['des'], x['h'], x['rot']) for x in fast])
print('slow:', [(x['des'], x['h'], x['rot'], x['dv']) for x in slow])
def pointable(x, before='2030-01-01', vmax=22.0):
    return x['os'] is not None and x['flag'] != 'S' and x['os'] < before and x['om'] is not None and x['om'] < vmax
pu = [x for x in unk if pointable(x)]
print('unknown-spin with pointable window <2030, V<22:', len(pu))
for x in sorted(pu, key=lambda t: t['os']): print('   ', show(x))
pu2 = [x for x in unk if pointable(x, vmax=20.5)]
print('... V<20.5:', len(pu2))
pu3 = [x for x in unk if x['os'] is not None and x['flag'] != 'S' and x['os'] < '2028-01-01']
print('... window starts before 2028 any V:', len(pu3), [(x['des'], x['os'], x['om']) for x in pu3])
print('flags among unknown:', {k: sum(1 for x in unk if x['flag'] == k) for k in set(x['flag'] for x in unk)}, 'no window', sum(1 for x in unk if x['os'] is None))
# dv<6 subset
print('--- dv<6 unknown-spin:')
for x in [x for x in unk if x['dv'] < 6]: print('   ', show(x))
# whole-body capture pool
print('=== capture pool (H>=28, i.e. <~9 m at pv .15)')
for dvc in (5, 6, 7):
    C = [x for x in rows if x['dv'] < dvc and x['h'] is not None and x['h'] >= 28]
    Cg = [x for x in C if x['occ'] is not None and x['occ'] <= 5]
    Cgg = [x for x in C if x['occ'] is not None and x['occ'] <= 2]
    Cr = [x for x in Cg if x['rot']]
    Ca = [x for x in Cg if x['A1'] is not None]
    Cp = [x for x in Cg if pointable(x, vmax=24.5)]
    arc60 = [x for x in Cg if x['arc'] and x['arc'] >= 60]
    print(f'dv<{dvc}: n {len(C)} occ<=5 {len(Cg)} occ<=2 {len(Cgg)} period {len(Cr)} A1 {len(Ca)} arc>=60d {len(arc60)} pointable<2030 anyV {len(Cp)}')
# H window for TransAstra-like 100 t: D for 100 t at rho 1500-3000 => D = (6 m / (pi rho))^(1/3)
for rho in (1200, 2000, 3000):
    Dm = (6 * 100e3 / (math.pi * rho)) ** (1 / 3)
    print('100 t at rho', rho, 'D=', round(Dm, 2), 'm ; H at pv .05/.15/.45:', [round(5 * math.log10(1329e3 / (Dm * math.sqrt(p))), 1) for p in (0.05, 0.15, 0.45)])
for Dm, lab in ((18, 'Elvis water 18 m'), (30, 'Michel 30 m'), (55, '55 m'), (100, 'Elvis PGM 100 m'), (200, 'Karman+ hundreds')):
    print(lab, 'H at pv .05/.15/.30:', [round(5 * math.log10(1329e3 / (Dm * math.sqrt(p))), 1) for p in (0.05, 0.15, 0.30)])
# OCC cut sensitivity: counts of H<24, dv<6 / <7 by occ
print('occ of dv<7 H<24:', sorted([x['occ'] for x in rows if x['dv'] < 7 and x['h'] is not None and x['h'] < 24]))
# P crit vs density
G = 6.674e-11
for rho in (1190, 1500, 2000, 2250, 3000):
    print('rho', rho, 'Pcrit h', round(math.sqrt(3 * math.pi / (G * rho)) / 3600, 2))
# inclination and synodic period for the 7 survivors
for x in slow:
    syn = 1 / abs(1 - 1 / (x['a'] ** 1.5)) if x['a'] and abs(x['a'] - 1) > 1e-6 else None
    print(x['des'], 'a', x['a'], 'e', x['e'], 'i', x['i'], 'synodic yr', round(syn, 1) if syn else None, 'ntraj', x['ntraj'], 'dv', x['dv'], 'win', x['os'], x['oe'], x['om'], x['flag'])
# median synodic period / inclination for dv<5
import statistics
syn5 = [1 / abs(1 - 1 / (x['a'] ** 1.5)) for x in A5 if x['a'] and abs(x['a'] - 1) > 1e-4]
print('dv<5 median synodic yr', round(statistics.median(syn5), 1), 'share >10 yr', round(sum(s > 10 for s in syn5) / len(syn5), 2), 'share > 20 yr', round(sum(s > 20 for s in syn5) / len(syn5), 2))
syn_all = [1 / abs(1 - 1 / (x['a'] ** 1.5)) for x in rows if x['a'] and abs(x['a'] - 1) > 1e-4]
print('all NHATS median synodic yr', round(statistics.median(syn_all), 1))
for d in ('2022 OB5', '2011 AA37', '341843', '99942', '2015 BM510', '469219', '1998 KY26', '2022 DC5', '2021 UH2', '2009 BD', '2011 MD', '2000 SG344', '101955'):
    for x in rows:
        if x['des'] == d: print(show(x), 'a', x['a'], 'i', x['i'], 'last', x['last'])
