"""Item 5 (NEOWISE gap): find NHATS objects with NEOWISE astrometry (MPC observatory code C51) and no SBDB diameter.
Usage: python3 -I cx_c51_census.py <catalogs_dir> <out_jsonl> <max_objects> <max_seconds> [des ...]
Queries the public MPC get-obs API one object at a time (1 s pause). Order: designations given on the command line first,
then NHATS objects without an SBDB diameter sorted by H (brightest first). Records C51 count and C51 date span."""
import sys, os, json, time, urllib.request, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats

CAT, OUT, max_n, max_s = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
first = sys.argv[5:]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try:
            done.add(json.loads(l)['des'])
        except Exception:  # noqa: BLE001
            pass
cand = [p for p in nh if U.by_pdes[p]['diameter'] in (None, '') and U.by_pdes[p]['H'] not in (None, '')]
cand.sort(key=lambda p: float(U.by_pdes[p]['H']))
order = [d for d in first] + [p for p in cand if p not in first]
URL = 'https://data.minorplanetcenter.net/api/get-obs'
t0 = time.time()
n = 0
with open(OUT, 'a') as out:
    for des in order:
        if n >= max_n or time.time() - t0 > max_s:
            break
        if des in done:
            continue
        s = U.by_pdes.get(des)
        rec = {'des': des, 'H': float(s['H']) if s else None, 'dv': nh[des]['dv'] if des in nh else None,
               'sbdb_diam': s['diameter'] if s else None, 'data_arc': s['data_arc'] if s else None}
        body = json.dumps({'desigs': [des], 'output_format': ['ADES_DF']}).encode()
        req = urllib.request.Request(URL, data=body, method='GET', headers={'Content-Type': 'application/json', 'User-Agent': 'research-client/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                js = json.load(r)
            obs = js[0]['ADES_DF'] if isinstance(js, list) else []
            c51 = [o for o in obs if o.get('stn') == 'C51']
            ts = sorted(o['obstime'] for o in c51 if o.get('obstime'))
            rec.update({'nobs': len(obs), 'n_c51': len(c51), 'c51_first': ts[0] if ts else None, 'c51_last': ts[-1] if ts else None,
                        'c51_years': dict(collections.Counter(t[:4] for t in ts))})
        except Exception as e:  # noqa: BLE001
            rec['error'] = repr(e)[:200]
        out.write(json.dumps(rec) + '\n')
        out.flush()
        n += 1
        print(des, rec.get('H'), 'nobs', rec.get('nobs'), 'C51', rec.get('n_c51'), rec.get('c51_years'), rec.get('error', ''), flush=True)
        time.sleep(1.0)
print('done', n)
