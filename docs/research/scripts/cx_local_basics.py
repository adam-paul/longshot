"""Local-only basics from nhats.json + sbdb_neo.json: NHATS counts, SBDB diameter/albedo/rot_per/A1/A2 coverage.
Usage: python3 -I cx_local_basics.py <catalogs_dir>"""
import sys, os, json, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats
CAT = sys.argv[1]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
raw = json.load(open(os.path.join(CAT, 'nhats.json')))
print('nhats keys', [k for k in raw if k != 'data'], 'count', raw.get('count'), 'sig', raw.get('signature'))
print('nhats example', raw['data'][0])
sb = json.load(open(os.path.join(CAT, 'sbdb_neo.json')))
print('sbdb keys', [k for k in sb if k != 'data'], sb.get('signature'), 'rows', len(sb['data']))
print('SBDB NEA asteroids', len(U.rows), 'NHATS', len(nh))
miss = [d for d in nh if d not in U.by_pdes]
print('NHATS not in SBDB NEA list', len(miss), miss[:20])
def has(v): return v not in (None, '')
def cnt(pred, scope):
    return sum(1 for p in scope if p in U.by_pdes and pred(U.by_pdes[p]))
allp = [s['pdes'] for s in U.rows]
n_all = list(nh); n6 = [d for d in nh if nh[d]['dv'] < 6]; n5 = [d for d in nh if nh[d]['dv'] < 5]
print('NHATS', len(n_all), 'dv<6', len(n6), 'dv<5', len(n5))
import statistics
hs = [nh[d]['h'] for d in nh if nh[d]['h'] is not None]
print('H median', statistics.median(hs), 'min', min(hs), 'max', max(hs), 'H>=25', sum(h >= 25 for h in hs), 'H<22', sum(h < 22 for h in hs), '22-25', sum(22 <= h < 25 for h in hs))
for lab, pred in [('diameter', lambda s: has(s['diameter'])), ('albedo', lambda s: has(s['albedo'])), ('rot_per', lambda s: has(s['rot_per'])),
                  ('spec', lambda s: has(s['spec_B']) or has(s['spec_T'])), ('BV/UB', lambda s: has(s['BV']) or has(s['UB'])),
                  ('GM/density', lambda s: has(s['GM']) or has(s['density'])),
                  ('A1', lambda s: has(s['A1'])), ('A2', lambda s: has(s['A2'])), ('A3', lambda s: has(s['A3'])), ('A1orA2', lambda s: has(s['A1']) or has(s['A2'])),
                  ('A1orA2 & diameter', lambda s: (has(s['A1']) or has(s['A2'])) and has(s['diameter'])),
                  ('n_del or n_dop>0', lambda s: (s['n_del_obs_used'] or 0) and int(s['n_del_obs_used']) > 0 or (s['n_dop_obs_used'] or 0) and int(s['n_dop_obs_used']) > 0)]:
    print('%-20s NHATS %5d  dv<6 %4d  dv<5 %4d  allNEA %6d' % (lab, cnt(pred, n_all), cnt(pred, n6), cnt(pred, n5), cnt(pred, allp)))
# list NHATS with SBDB diameter
print('--- NHATS with SBDB diameter:')
for d in sorted(n_all, key=lambda d: nh[d]['dv']):
    s = U.by_pdes.get(d)
    if s and has(s['diameter']):
        print('%-12s %-14s dv=%.2f H=%s D=%s sig=%s alb=%s A2=%s A1=%s' % (d, s.get('name') or '', nh[d]['dv'], s['H'], s['diameter'], s['diameter_sigma'], s['albedo'], s['A2'], s['A1']))
