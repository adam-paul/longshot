#!/usr/bin/env python3
"""ow_windows.py: future optical/radar windows of NHATS objects, from local snapshots.

Usage: python3 -I ow_windows.py <nhats.json> <sbdb_neo.json> <out_dir>
Writes <out_dir>/ow_windows_summary.json and <out_dir>/ow_shortlist.tsv
"""
import json, sys, os, statistics, datetime as dt
from collections import Counter, defaultdict

nh_path, sb_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)
TODAY = dt.date(2026, 11, 21)

nh = json.load(open(nh_path))['data']
sb = json.load(open(sb_path))
F = sb['fields']
idx = {f: i for i, f in enumerate(F)}
sbd = {}
for r in sb['data']:
    sbd[r[idx['pdes']]] = r

def f(x):
    try:
        return float(x)
    except Exception:
        return None

def d(x):
    if not x:
        return None
    try:
        return dt.date.fromisoformat(x[:10])
    except Exception:
        return None

rows = []
miss = 0
for o in nh:
    des = o['des']
    s = sbd.get(des)
    if s is None:
        miss += 1
    r = dict(
        des=des, h=f(o['h']), dv=f(o['min_dv']['dv']), dur=o['min_dv']['dur'],
        occ=int(o['occ']) if o['occ'] not in (None, '') else None,
        obs_start=d(o['obs_start']), obs_end=d(o['obs_end']), obs_mag=f(o['obs_mag']),
        obs_flag=o.get('obs_flag'),
        rg=o.get('radar_obs_g'), rgs=f(o.get('radar_snr_g')),
        ra=o.get('radar_obs_a'), ras=f(o.get('radar_snr_a')),
        min_size=f(o.get('min_size')), max_size=f(o.get('max_size')),
        size=o.get('size'), n_via=o.get('n_via_traj'),
    )
    if s is not None:
        r['sb_cc'] = int(s[idx['condition_code']]) if s[idx['condition_code']] not in (None, '') else None
        r['arc'] = f(s[idx['data_arc']])
        r['first_obs'] = s[idx['first_obs']]
        r['last_obs'] = s[idx['last_obs']]
        r['rot_per'] = s[idx['rot_per']]
        r['spec'] = s[idx['spec_B']] or s[idx['spec_T']]
        r['albedo'] = s[idx['albedo']]
        r['nobs'] = s[idx['n_obs_used']]
        r['moid'] = f(s[idx['moid']])
        r['a'] = f(s[idx['a']]); r['e'] = f(s[idx['e']]); r['i'] = f(s[idx['i']])
    rows.append(r)

N = len(rows)
out = {'n_nhats': N, 'sbdb_missing': miss, 'today': str(TODAY)}

# basic
hs = [r['h'] for r in rows if r['h'] is not None]
arcs = [r['arc'] for r in rows if r.get('arc') is not None]
out['median_H'] = statistics.median(hs)
out['median_arc_d'] = statistics.median(arcs)
out['n_with_window'] = sum(1 for r in rows if r['obs_start'])
out['n_no_window'] = sum(1 for r in rows if not r['obs_start'])
out['obs_flag_counts'] = dict(Counter(repr(r['obs_flag']) for r in rows))
out['obs_flag_given_window'] = dict(Counter(repr(r['obs_flag']) for r in rows if r['obs_start']))
starts = sorted(r['obs_start'] for r in rows if r['obs_start'])
out['window_start_min'] = str(starts[0]); out['window_start_max'] = str(starts[-1])
out['window_start_by_year'] = dict(sorted(Counter(s.year for s in starts).items()))
out['window_open_now'] = sum(1 for r in rows if r['obs_start'] and r['obs_start'] <= TODAY and r['obs_end'] and r['obs_end'] >= TODAY)
out['window_start_past'] = sum(1 for r in rows if r['obs_start'] and r['obs_start'] < TODAY)
out['window_end_past'] = sum(1 for r in rows if r['obs_end'] and r['obs_end'] < TODAY)
mags = [r['obs_mag'] for r in rows if r['obs_mag'] is not None]
out['obs_mag_min'] = min(mags); out['obs_mag_max'] = max(mags); out['obs_mag_median'] = statistics.median(mags)
durs = [(r['obs_end'] - r['obs_start']).days for r in rows if r['obs_start'] and r['obs_end']]
out['window_len_median_d'] = statistics.median(durs)
out['window_len_quartiles_d'] = statistics.quantiles(durs, n=4)

# occ of windowed vs not
out['occ_all'] = dict(sorted(Counter(r['occ'] for r in rows).items()))
out['occ_with_window'] = dict(sorted(Counter(r['occ'] for r in rows if r['obs_start']).items()))
out['occ_no_window'] = dict(sorted(Counter(r['occ'] for r in rows if not r['obs_start']).items()))
# cross-check NHATS occ vs SBDB condition code
agree = sum(1 for r in rows if r.get('sb_cc') is not None and r['sb_cc'] == r['occ'])
out['occ_eq_sbdb_cc'] = agree
out['occ_ne_sbdb_cc'] = sum(1 for r in rows if r.get('sb_cc') is not None and r['sb_cc'] != r['occ'])

def magbin(m):
    if m is None: return 'none'
    if m < 20: return 'V<20'
    if m < 22: return '20-22'
    if m < 24: return '22-24'
    return '>=24'

def occbin(o):
    if o is None: return 'occ?'
    if o <= 2: return 'occ0-2'
    if o <= 5: return 'occ3-5'
    return 'occ6-9'

cut_dates = {'<2028': dt.date(2028, 1, 1), '<2030': dt.date(2030, 1, 1), '<2035': dt.date(2035, 1, 1), 'any': dt.date(9999, 1, 1)}
dv_cuts = {'dv<5': 5.0, 'dv<6': 6.0, 'all': 99.0}

table = {}
for dvn, dvc in dv_cuts.items():
    sub = [r for r in rows if r['dv'] is not None and r['dv'] < dvc]
    t = {'n_objects': len(sub), 'n_with_window': sum(1 for r in sub if r['obs_start'])}
    for cn, cd in cut_dates.items():
        w = [r for r in sub if r['obs_start'] and r['obs_start'] < cd]
        # "future" = window not already ended
        wf = [r for r in w if r['obs_end'] is None or r['obs_end'] >= TODAY]
        e = {'n': len(w), 'n_not_ended': len(wf)}
        e['by_mag'] = dict(Counter(magbin(r['obs_mag']) for r in wf))
        e['by_occ'] = dict(Counter(occbin(r['occ']) for r in wf))
        cross = defaultdict(Counter)
        for r in wf:
            cross[occbin(r['occ'])][magbin(r['obs_mag'])] += 1
        e['occ_x_mag'] = {k: dict(v) for k, v in cross.items()}
        e['flag_S'] = sum(1 for r in wf if r['obs_flag'] == 'S')
        t[cn] = e
    table[dvn] = t
out['windows'] = table

# radar
out['radar'] = {
    'goldstone_listed': sum(1 for r in rows if r['rg']),
    'arecibo_listed': sum(1 for r in rows if r['ra']),
    'either': sum(1 for r in rows if r['rg'] or r['ra']),
    'goldstone_dv<6': sum(1 for r in rows if r['rg'] and r['dv'] < 6),
    'goldstone_dv<5': sum(1 for r in rows if r['rg'] and r['dv'] < 5),
}
gy = Counter()
for r in rows:
    if r['rg']:
        gy[r['rg'][:4]] += 1
out['radar']['goldstone_by_year'] = dict(sorted(gy.items()))
gs = [r['rgs'] for r in rows if r['rg'] and r['rgs'] is not None]
if gs:
    out['radar']['goldstone_snr_median'] = statistics.median(gs)
    out['radar']['goldstone_snr_ge_30'] = sum(1 for x in gs if x >= 30)
    out['radar']['goldstone_snr_ge_100'] = sum(1 for x in gs if x >= 100)
for cn, cd in cut_dates.items():
    out['radar']['goldstone_' + cn] = sum(1 for r in rows if r['rg'] and d(r['rg']) and d(r['rg']) < cd)
    out['radar']['goldstone_dv<6_' + cn] = sum(1 for r in rows if r['rg'] and d(r['rg']) and d(r['rg']) < cd and r['dv'] < 6)
out['radar']['goldstone_sample'] = [(r['des'], r['rg'], r['rgs'], r['dv'], r['h']) for r in rows if r['rg']][:8]

# short list: dv<6, window starts before 2030 (not ended), V<22, recoverable orbit
def shortlist(max_occ, flagS_ok):
    res = []
    for r in rows:
        if r['dv'] is None or r['dv'] >= 6: continue
        if not r['obs_start'] or r['obs_start'] >= dt.date(2030, 1, 1): continue
        if r['obs_end'] and r['obs_end'] < TODAY: continue
        if r['obs_mag'] is None or r['obs_mag'] >= 22: continue
        ok = (r['occ'] is not None and r['occ'] <= max_occ) or (flagS_ok and r['obs_flag'] == 'S')
        if not ok: continue
        res.append(r)
    return res

sl_variants = {}
for mo in (2, 3, 4, 5, 9):
    sl_variants['occ<=%d' % mo] = len(shortlist(mo, False))
out['shortlist_counts_dv<6_before2030_V<22'] = sl_variants
out['shortlist_counts_dv<6_before2030_V<22_anyocc_by_occ'] = dict(sorted(Counter(r['occ'] for r in shortlist(9, False)).items()))
out['shortlist_anyocc_flagS'] = sum(1 for r in shortlist(9, False) if r['obs_flag'] == 'S')

SL = sorted(shortlist(5, False), key=lambda r: r['obs_start'])
out['shortlist_n'] = len(SL)
out['shortlist_has_rot_per'] = sum(1 for r in SL if r.get('rot_per'))
out['shortlist_has_spec'] = sum(1 for r in SL if r.get('spec'))
out['shortlist_has_albedo'] = sum(1 for r in SL if r.get('albedo'))
out['shortlist_by_magbin'] = dict(Counter(magbin(r['obs_mag']) for r in SL))
out['shortlist_by_year'] = dict(sorted(Counter(r['obs_start'].year for r in SL).items()))
out['shortlist_median_H'] = statistics.median([r['h'] for r in SL]) if SL else None
with open(os.path.join(out_dir, 'ow_shortlist.tsv'), 'w') as fh:
    cols = ['des', 'h', 'dv', 'dur', 'occ', 'obs_start', 'obs_end', 'obs_mag', 'obs_flag', 'min_size', 'max_size', 'arc', 'first_obs', 'last_obs', 'rot_per', 'spec', 'albedo', 'rg', 'rgs']
    fh.write('\t'.join(cols) + '\n')
    for r in SL:
        fh.write('\t'.join('' if r.get(c) is None else str(r.get(c)) for c in cols) + '\n')

# also: wider list for dv<6 all occ, V<22, <2030
ALL6 = sorted(shortlist(9, False), key=lambda r: r['obs_start'])
with open(os.path.join(out_dir, 'ow_shortlist_anyocc.tsv'), 'w') as fh:
    cols = ['des', 'h', 'dv', 'dur', 'occ', 'obs_start', 'obs_end', 'obs_mag', 'obs_flag', 'min_size', 'max_size', 'arc', 'first_obs', 'last_obs', 'rot_per', 'spec', 'albedo', 'rg', 'rgs']
    fh.write('\t'.join(cols) + '\n')
    for r in ALL6:
        fh.write('\t'.join('' if r.get(c) is None else str(r.get(c)) for c in cols) + '\n')

# characterization state of whole list from SBDB
out['nhats_has_rot_per_sbdb'] = sum(1 for r in rows if r.get('rot_per'))
out['nhats_has_spec_sbdb'] = sum(1 for r in rows if r.get('spec'))
out['nhats_has_albedo_sbdb'] = sum(1 for r in rows if r.get('albedo'))

# per-year count of windows that are V<22 with OCC<=5 for the whole list and dv<6
peryear = defaultdict(lambda: Counter())
for r in rows:
    if not r['obs_start'] or (r['obs_end'] and r['obs_end'] < TODAY): continue
    y = r['obs_start'].year
    peryear[y]['all'] += 1
    if r['obs_mag'] is not None and r['obs_mag'] < 22:
        peryear[y]['V<22'] += 1
        if r['occ'] is not None and r['occ'] <= 5: peryear[y]['V<22_occ<=5'] += 1
        if r['dv'] < 6: peryear[y]['V<22_dv<6'] += 1
    if r['obs_mag'] is not None and r['obs_mag'] < 20:
        peryear[y]['V<20'] += 1
        if r['dv'] < 6: peryear[y]['V<20_dv<6'] += 1
    if r['obs_mag'] is not None and r['obs_mag'] < 18:
        peryear[y]['V<18'] += 1
out['per_year'] = {y: dict(c) for y, c in sorted(peryear.items())}

json.dump(out, open(os.path.join(out_dir, 'ow_windows_summary.json'), 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
