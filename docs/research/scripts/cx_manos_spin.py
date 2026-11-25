"""MANOS photometry (Thirouin+2016 J/AJ/152/163 table1, Thirouin+2018 J/ApJS/239/4 table1): fast-rotator fraction versus H
with ALL observed targets as the denominator (full periods, lower limits from partial lightcurves, flat lightcurves).
Usage: python3 -I cx_manos_spin.py <vizier_dir> <catalogs_dir>"""
import sys, os, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import parse_vizier, Universe, load_nhats

V, CAT = sys.argv[1], sys.argv[2]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))


def fl(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


obj = {}   # name -> dict(H, kind, P)
t16 = parse_vizier(os.path.join(V, 'J_AJ_152_163.tsv'))['J/AJ/152/163/table1']
t18 = parse_vizier(os.path.join(V, 'J_ApJS_239_4.tsv'))['J/ApJS/239/4/table1']
print('T16 LCType counts', collections.Counter(r['LCType'] for r in t16))
print('T18 Set counts', collections.Counter(r['Set'] for r in t18), '| limit flags', collections.Counter(r['l_Prot'] for r in t18))
for src, rows, pc, lc, hc in (('T16', t16, 'Per', 'l_Per', 'HMag'), ('T18', t18, 'Prot', 'l_Prot', 'Hmag')):
    for r in rows:
        nm = r['Name'].strip()
        P = fl(r[pc])
        lim = (r[lc] or '').strip()
        if P and not lim:
            kind = 'full'
        elif P and lim:
            kind = 'limit'
        else:
            kind = 'flat/none'
        h = fl(r[hc])
        prev = obj.get(nm)
        rank = {'full': 0, 'limit': 1, 'flat/none': 2}
        if prev is None or rank[kind] < rank[prev['kind']]:
            obj[nm] = {'H': h if h is not None else (prev or {}).get('H'), 'kind': kind, 'P': P, 'src': src}
print('distinct MANOS photometry targets', len(obj), collections.Counter(o['kind'] for o in obj.values()))
BINS = [(-99, 22), (22, 24), (24, 26), (26, 99), (-99, 99)]
print('%-8s %5s %5s %6s %6s | %9s %9s | %s' % ('H bin', 'N', 'full', 'limit', 'flat', 'P<2.2h', 'P<10min', 'fraction P<2.2h: of full / of all observed (lower bound) / upper bound if all flat were fast'))
for lo, hi in BINS:
    o = [x for x in obj.values() if x['H'] is not None and lo <= x['H'] < hi]
    full = [x for x in o if x['kind'] == 'full']
    lim = [x for x in o if x['kind'] == 'limit']
    flat = [x for x in o if x['kind'] == 'flat/none']
    fr = sum(1 for x in full if x['P'] < 2.2)
    sf = sum(1 for x in full if x['P'] < 10 / 60)
    lim_slow = sum(1 for x in lim if x['P'] >= 2.2)
    lab = 'all' if (lo, hi) == (-99, 99) else ('<%d' % hi if lo == -99 else ('>=%d' % lo if hi == 99 else '%d-%d' % (lo, hi)))
    n = max(1, len(o))
    print('%-8s %5d %5d %6d %6d | %4d %3.0f%% %4d %3.0f%% | of full %.0f%%; of all %.0f%%; upper %.0f%%; P<10min of all %.0f%%; limits with P>2.2h: %d' % (
        lab, len(o), len(full), len(lim), len(flat), fr, 100 * fr / max(1, len(full)), sf, 100 * sf / max(1, len(full)),
        100 * fr / max(1, len(full)), 100 * fr / n, 100 * (fr + len(flat) + len(lim) - lim_slow) / n, 100 * sf / n, lim_slow))
# NHATS membership of the MANOS photometry targets
inn = [nm for nm in obj if U.resolve(nm) in nh]
print('MANOS photometry targets in NHATS today:', len(inn), '| with full period', sum(1 for nm in inn if obj[nm]['kind'] == 'full'))
