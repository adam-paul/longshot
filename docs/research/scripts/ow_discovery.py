#!/usr/bin/env python3
"""ow_discovery.py: discovery-apparition brightness, duration and rate statistics for the
sampled NHATS objects (first observed 2024-01-01 or later).

Usage: python3 -I ow_discovery.py <nhats.json> <sbdb_neo.json> <dl_dir> <out_dir>
Reads <dl_dir>/sample.json, <dl_dir>/horizons/*.txt (geocentric, 4 h step, first_obs-60 d .. +120 d)
and <dl_dir>/mpc/*.obs80 (MPC 80-column observations).
"""
import json, sys, os, statistics, math, datetime as dt
from collections import Counter

nh_path, sb_path, dl, out_dir = sys.argv[1:5]
os.makedirs(out_dir, exist_ok=True)
STEP_D = 4.0 / 24.0
MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}

nh = {o['des']: o for o in json.load(open(nh_path))['data']}
sb = json.load(open(sb_path))
ix = {f: i for i, f in enumerate(sb['fields'])}
sbd = {r[ix['pdes']]: r for r in sb['data']}
samp = json.load(open(os.path.join(dl, 'sample.json')))

def fn(des):
    return des.replace(' ', '_').replace('/', '_')

def parse_h(path):
    rows = []
    if not os.path.exists(path):
        return rows
    on = False
    for line in open(path, errors='replace'):
        if line.startswith('$$SOE'):
            on = True; continue
        if line.startswith('$$EOE'):
            break
        if not on:
            continue
        p = [x.strip() for x in line.split(',')]
        try:
            d, hm = p[0].split()
            y, mo, da = d.split('-')
            t = dt.datetime(int(y), MON[mo], int(da), int(hm[:2]), int(hm[3:5]))
            dra, ddec = float(p[5]), float(p[6])
            v = float(p[7])
            r = float(p[9]); delta = float(p[11]); elong = float(p[13]); phase = float(p[15])
            tom = float(p[16]); mill = float(p[17])
            dec = float(p[4])
        except Exception:
            continue
        rate = math.hypot(dra, ddec) / 60.0  # arcsec/min
        rows.append((t, v, rate, delta, elong, phase, dec, tom, mill))
    return rows

def parse_obs80(path):
    obs = []
    if not os.path.exists(path):
        return obs
    for line in open(path, errors='replace'):
        if len(line) < 80:
            continue
        note2 = line[14]
        if note2 in ('R', 'r', 'S', 's', 'V', 'v', 'X', 'x'):
            # radar / satellite second lines / roving: skip second lines; keep 'S' first line handled below
            if note2 in ('s', 'r', 'v', 'x', 'R', 'X'):
                continue
        try:
            y = int(line[15:19]); mo = int(line[20:22]); dayf = float(line[23:32])
            t = dt.datetime(y, mo, 1) + dt.timedelta(days=dayf - 1)
        except Exception:
            continue
        try:
            mag = float(line[65:70])
        except Exception:
            mag = None
        band = line[70]
        stn = line[77:80]
        disc = line[12] == '*'
        obs.append((t, mag, band, stn, disc))
    obs.sort(key=lambda x: x[0])
    return obs

def days_below(rows, vlim, t_from=None, t_to=None, elong_min=None, rate_max=None):
    n = 0
    for (t, v, rate, delta, elong, phase, dec, tom, mill) in rows:
        if t_from and t < t_from: continue
        if t_to and t > t_to: continue
        if v >= vlim: continue
        if elong_min is not None and elong < elong_min: continue
        if rate_max is not None and rate > rate_max: continue
        n += 1
    return n * STEP_D

res = []
missing = []
for des, fo, lo in samp['sample']:
    rows = parse_h(os.path.join(dl, 'horizons', fn(des) + '.txt'))
    obs = parse_obs80(os.path.join(dl, 'mpc', fn(des) + '.obs80'))
    if not rows:
        missing.append(des); continue
    s = sbd[des]; o = nh[des]
    H = float(o['h']) if o['h'] else None
    t_first = dt.datetime.fromisoformat(fo[:10])
    if obs:
        t_first_mpc = obs[0][0]
        t_last_mpc = obs[-1][0]
    else:
        t_first_mpc = t_first; t_last_mpc = None
    # use MPC first observation time when available (more precise), else SBDB date
    t0 = t_first_mpc
    win_lo = t0 - dt.timedelta(days=60); win_hi = t0 + dt.timedelta(days=120)
    peak = min(rows, key=lambda r: r[1])
    # ephemeris V at first observation
    nearest = min(rows, key=lambda r: abs((r[0] - t0).total_seconds()))
    r = dict(des=des, H=H, dv=float(o['min_dv']['dv']), occ=int(o['occ']), first_obs=fo, last_obs=lo,
             arc=float(s[ix['data_arc']]) if s[ix['data_arc']] else None,
             v_peak=peak[1], t_peak=str(peak[0]), peak_minus_first_d=(peak[0] - t0).total_seconds() / 86400.0,
             rate_at_peak=peak[2], delta_at_peak=peak[3], elong_at_peak=peak[4],
             v_at_first=nearest[1], rate_at_first=nearest[2], delta_at_first=nearest[3], elong_at_first=nearest[4],
             phase_at_first=nearest[5], dec_at_first=nearest[6], nobs=len(obs))
    for vl in (17, 18, 19, 20, 21, 22):
        # whole apparition window, elongation > 60
        r['d_lt%d_all' % vl] = days_below(rows, vl, elong_min=60)
        # from first observation onward (what a responder could use), elongation > 60
        r['d_lt%d_post' % vl] = days_below(rows, vl, t_from=t0, elong_min=60)
        # from first obs + 2 d (announcement + reaction lag)
        r['d_lt%d_post2' % vl] = days_below(rows, vl, t_from=t0 + dt.timedelta(days=2), elong_min=60)
        # before first observation (missed by surveys)
        r['d_lt%d_pre' % vl] = days_below(rows, vl, t_to=t0, elong_min=60)
        # post2 with rate limit 30 arcsec/min (non-sidereal tracking still easy for most small scopes)
        r['d_lt%d_post2_slow' % vl] = days_below(rows, vl, t_from=t0 + dt.timedelta(days=2), elong_min=60, rate_max=30.0)
    # sensitivity: count from the discovery-asterisk observation + 1 day and + 2 days
    tds = [tt for (tt, m, b, st, d) in obs if d]
    t_disc = tds[0] if tds else t0
    r['disc_minus_first_d'] = (t_disc - t0).total_seconds() / 86400.0
    for vl in (18, 19, 20, 21):
        r['d_lt%d_disc1' % vl] = days_below(rows, vl, t_from=t_disc + dt.timedelta(days=1), elong_min=60)
        r['d_lt%d_disc2' % vl] = days_below(rows, vl, t_from=t_disc + dt.timedelta(days=2), elong_min=60)
    # peak brightness while observable (elongation >= 60) at or after first observation
    obsrows = [x for x in rows if x[4] >= 60 and x[0] >= t0]
    r['v_peak_obs_post'] = min(x[1] for x in obsrows) if obsrows else None
    obsall = [x for x in rows if x[4] >= 60]
    r['v_peak_obs_all'] = min(x[1] for x in obsall) if obsall else None
    # fading after first observation: V(t0 + k days) - V(t0)
    def v_at(tt):
        nr = min(rows, key=lambda x: abs((x[0] - tt).total_seconds()))
        return nr[1] if abs((nr[0] - tt).total_seconds()) < 4 * 3600 else None
    for k in (7, 14, 28, 42):
        vv = v_at(t0 + dt.timedelta(days=k))
        r['fade_%dd' % k] = (vv - nearest[1]) if vv is not None else None
    # last time brighter than V 20 / 21 / 22 while observable, in days after first observation
    for vl in (18, 20, 21, 22):
        ts = [x[0] for x in rows if x[0] >= t0 and x[1] < vl and x[4] >= 60]
        r['last_lt%d_d' % vl] = ((max(ts) - t0).total_seconds() / 86400.0) if ts else None
    # median rate while V<20 post discovery
    rr = [x[2] for x in rows if x[0] >= t0 and x[1] < 20 and x[4] >= 60]
    r['rate_med_lt20_post'] = statistics.median(rr) if rr else None
    rr = [x[2] for x in rows if x[0] >= t0 and x[1] < 18 and x[4] >= 60]
    r['rate_med_lt18_post'] = statistics.median(rr) if rr else None
    # MPC reported mags
    mags = [m for (t, m, b, st, d) in obs if m is not None]
    r['mpc_mag_min'] = min(mags) if mags else None
    r['mpc_mag_med'] = statistics.median(mags) if mags else None
    first_night = [m for (t, m, b, st, d) in obs if m is not None and (t - obs[0][0]).total_seconds() < 86400]
    r['mpc_mag_first_night'] = statistics.median(first_night) if first_night else None
    dsc = [st for (t, m, b, st, d) in obs if d]
    r['disc_stn'] = dsc[0] if dsc else None
    r['first_stn'] = obs[0][3] if obs else None
    r['stations'] = sorted(set(st for (t, m, b, st, d) in obs))
    r['has_X05'] = 'X05' in r['stations']
    r['mpc_arc_d'] = (t_last_mpc - t_first_mpc).total_seconds() / 86400.0 if t_last_mpc else None
    # observed rate from astrometry not computed (ephemeris rate used)
    res.append(r)

n = len(res)
out = {'n_sample': len(samp['sample']), 'n_used': n, 'missing': missing, 'pool': samp['n_pool']}

def q(vals, ps=(0.1, 0.25, 0.5, 0.75, 0.9)):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    return {('p%d' % int(p * 100)): round(v[min(len(v) - 1, int(p * len(v)))], 2) for p in ps}

def frac(pred):
    k = sum(1 for r in res if pred(r))
    p = k / n
    # Wilson 95% interval
    z = 1.96
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {'k': k, 'n': n, 'frac': round(p, 3), 'ci95': [round(max(0, c - hw), 3), round(min(1, c + hw), 3)]}

out['H'] = q([r['H'] for r in res])
out['arc_sbdb_d'] = q([r['arc'] for r in res])
out['v_peak_apparition'] = q([r['v_peak'] for r in res])
out['v_at_first_obs_ephem'] = q([r['v_at_first'] for r in res])
out['mpc_mag_first_night'] = q([r['mpc_mag_first_night'] for r in res])
out['mpc_mag_brightest'] = q([r['mpc_mag_min'] for r in res])
out['peak_minus_first_d'] = q([r['peak_minus_first_d'] for r in res])
out['rate_at_first_arcsec_min'] = q([r['rate_at_first'] for r in res])
out['rate_at_peak_arcsec_min'] = q([r['rate_at_peak'] for r in res])
out['delta_at_first_au'] = q([r['delta_at_first'] for r in res])
out['delta_at_peak_au'] = q([r['delta_at_peak'] for r in res])
out['elong_at_first'] = q([r['elong_at_first'] for r in res])
out['disc_minus_first_d'] = q([r['disc_minus_first_d'] for r in res])
out['disc_after_first_gt_1d'] = frac(lambda r: r['disc_minus_first_d'] > 1.0)
for vl in (18, 19, 20, 21):
    out['sens_lt%d_ge1d_from_disc_plus1' % vl] = frac(lambda r, vl=vl: r['d_lt%d_disc1' % vl] >= 1.0)
    out['sens_lt%d_ge1d_from_disc_plus2' % vl] = frac(lambda r, vl=vl: r['d_lt%d_disc2' % vl] >= 1.0)
out['v_peak_obs_post'] = q([r['v_peak_obs_post'] for r in res])
out['v_peak_obs_all'] = q([r['v_peak_obs_all'] for r in res])
for k in (7, 14, 28, 42):
    out['fade_%dd_mag' % k] = q([r['fade_%dd' % k] for r in res])
for vl in (18, 20, 21, 22):
    out['last_lt%d_days_after_first_if_any' % vl] = q([r['last_lt%d_d' % vl] for r in res])
out['peak_within_0.5mag_of_first'] = frac(lambda r: r['v_peak_obs_post'] is not None and (r['v_at_first'] - r['v_peak_obs_post']) <= 0.5)
out['rate_first_gt_10'] = frac(lambda r: r['rate_at_first'] > 10)
out['rate_first_gt_30'] = frac(lambda r: r['rate_at_first'] > 30)
out['rate_first_gt_60'] = frac(lambda r: r['rate_at_first'] > 60)
out['rate_med_while_lt20_post'] = q([r['rate_med_lt20_post'] for r in res])
out['rate_med_while_lt18_post'] = q([r['rate_med_lt18_post'] for r in res])
for vl in (17, 18, 19, 20, 21, 22):
    for tag in ('all', 'post', 'post2', 'post2_slow', 'pre'):
        key = 'd_lt%d_%s' % (vl, tag)
        vals = [r[key] for r in res]
        out[key] = {
            'frac_any': frac(lambda r, key=key: r[key] > 0),
            'frac_ge_1d': frac(lambda r, key=key: r[key] >= 1.0),
            'frac_ge_3d': frac(lambda r, key=key: r[key] >= 3.0),
            'frac_ge_7d': frac(lambda r, key=key: r[key] >= 7.0),
            'median_d_all': round(statistics.median(vals), 2),
            'median_d_if_any': round(statistics.median([v for v in vals if v > 0]), 2) if any(v > 0 for v in vals) else None,
            'quartiles_if_any': q([v for v in vals if v > 0], ps=(0.25, 0.5, 0.75)),
        }
# discovery stations
out['disc_stn'] = dict(Counter(r['disc_stn'] for r in res).most_common())
out['first_stn'] = dict(Counter(r['first_stn'] for r in res).most_common())
out['has_X05'] = frac(lambda r: r['has_X05'])
out['disc_by_X05'] = frac(lambda r: r['disc_stn'] == 'X05')
out['n_stations_per_object'] = q([len(r['stations']) for r in res])
out['nobs'] = q([r['nobs'] for r in res])
# dv<6 subset
sub = [r for r in res if r['dv'] < 6]
out['n_dv_lt6'] = len(sub)
out['dv_lt6_ge1d_lt18_post2'] = sum(1 for r in sub if r['d_lt18_post2'] >= 1)
out['dv_lt6_ge1d_lt20_post2'] = sum(1 for r in sub if r['d_lt20_post2'] >= 1)
# by year
for y in ('2024', '2025', '2026'):
    s2 = [r for r in res if r['first_obs'].startswith(y)]
    out['year_' + y] = {'n': len(s2),
                        'lt18_post2_ge1d': sum(1 for r in s2 if r['d_lt18_post2'] >= 1),
                        'lt20_post2_ge1d': sum(1 for r in s2 if r['d_lt20_post2'] >= 1),
                        'lt21_post2_ge1d': sum(1 for r in s2 if r['d_lt21_post2'] >= 1)}
json.dump(out, open(os.path.join(out_dir, 'ow_discovery_summary.json'), 'w'), indent=1)
json.dump(res, open(os.path.join(out_dir, 'ow_discovery_objects.json'), 'w'), indent=0)
print(json.dumps(out, indent=1))
