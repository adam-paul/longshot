#!/usr/bin/env python3
"""ow_fetch_sample.py: sequential, polite fetch of Horizons ephemerides and MPC observations
for a random sample of NHATS objects first observed 2024-01-01 or later.

Usage: python3 -I ow_fetch_sample.py <nhats.json> <sbdb_neo.json> <dl_dir> [n=130] [seed=20261121]
One request at a time, >= 1.5 s pause, resume-safe (skips files already present).
"""
import json, sys, os, time, random, datetime as dt, urllib.request, urllib.parse

nh_path, sb_path, dl = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 130
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20261121
UA = 'obs-window-check/0.1 (research script)'
os.makedirs(os.path.join(dl, 'horizons'), exist_ok=True)
os.makedirs(os.path.join(dl, 'mpc'), exist_ok=True)

nh = json.load(open(nh_path))['data']
sb = json.load(open(sb_path))
ix = {f: i for i, f in enumerate(sb['fields'])}
sbd = {r[ix['pdes']]: r for r in sb['data']}
pool = []
for o in nh:
    s = sbd[o['des']]
    fo = s[ix['first_obs']]
    if fo and fo >= '2024-01-01':
        pool.append((o['des'], fo, s[ix['last_obs']]))
pool.sort()
rng = random.Random(seed)
sample = rng.sample(pool, n)
json.dump({'seed': seed, 'n_pool': len(pool), 'sample': sample}, open(os.path.join(dl, 'sample.json'), 'w'), indent=0)
print('pool', len(pool), 'sample', len(sample), flush=True)

def fn(des):
    return des.replace(' ', '_').replace('/', '_')

def get(url, data=None, headers=None, method='GET'):
    req = urllib.request.Request(url, data=data, headers=dict({'User-Agent': UA}, **(headers or {})), method=method)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

for k, (des, fo, lo) in enumerate(sample):
    # Horizons
    hp = os.path.join(dl, 'horizons', fn(des) + '.txt')
    if not (os.path.exists(hp) and os.path.getsize(hp) > 2000):
        d0 = dt.date.fromisoformat(fo[:10])
        t0 = d0 - dt.timedelta(days=60)
        t1 = d0 + dt.timedelta(days=120)
        q = {
            'format': 'text', 'COMMAND': "'DES=%s;'" % des, 'OBJ_DATA': "'NO'", 'MAKE_EPHEM': "'YES'",
            'EPHEM_TYPE': "'OBSERVER'", 'CENTER': "'500@399'", 'START_TIME': "'%s'" % t0, 'STOP_TIME': "'%s'" % t1,
            'STEP_SIZE': "'4 h'", 'QUANTITIES': "'1,3,9,19,20,23,24,25'", 'CSV_FORMAT': "'YES'", 'ANG_FORMAT': "'DEG'",
        }
        url = 'https://ssd.jpl.nasa.gov/api/horizons.api?' + urllib.parse.urlencode(q)
        for attempt in range(3):
            try:
                b = get(url)
                open(hp, 'wb').write(b)
                break
            except Exception as e:
                print('horizons fail', des, attempt, repr(e)[:120], flush=True)
                time.sleep(10 * (attempt + 1))
        time.sleep(1.5)
    # MPC
    mp = os.path.join(dl, 'mpc', fn(des) + '.obs80')
    if not (os.path.exists(mp) and os.path.getsize(mp) > 80):
        body = json.dumps({'desigs': [des], 'output_format': ['OBS80']}).encode()
        for attempt in range(3):
            try:
                b = get('https://data.minorplanetcenter.net/api/get-obs', data=body, headers={'Content-Type': 'application/json'}, method='GET')
                j = json.loads(b)
                txt = j[0].get('OBS80', '') if isinstance(j, list) and j else ''
                open(mp, 'w').write(txt)
                break
            except Exception as e:
                print('mpc fail', des, attempt, repr(e)[:120], flush=True)
                time.sleep(10 * (attempt + 1))
        time.sleep(1.5)
    if k % 10 == 0:
        print('done', k + 1, des, flush=True)
print('ALL DONE', flush=True)
