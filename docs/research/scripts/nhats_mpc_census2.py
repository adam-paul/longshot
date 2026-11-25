"""Sample NHATS objects, pull MPC observations (public API), tally station/band counts.
Usage: python3 -I nhats_mpc_census2.py <nhats_json> <out_prefix> <n_sample> <seed> <worker> <nworkers> <max_seconds>
Writes <out_prefix>.w<worker>; skips designations already present in <out_prefix> or any .w file.
"""
import json, sys, random, time, urllib.request, collections, glob

nhats_path, out_path, n, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
worker, nworkers, max_s = int(sys.argv[5]), int(sys.argv[6]), float(sys.argv[7])
t0 = time.time()
d = json.load(open(nhats_path))
objs = [(x['des'], x.get('h'), x.get('min_dv', {}).get('dv')) for x in d['data']]
random.Random(seed).shuffle(objs)
done = set()
for p in [out_path] + glob.glob(out_path + '.w*'):
    try:
        for line in open(p):
            r = json.loads(line)
            if 'error' not in r:
                done.add(r['des'])
    except FileNotFoundError:
        pass
out = open(out_path + '.w%d' % worker, 'a')
URL = "https://data.minorplanetcenter.net/api/get-obs"
count = 0
for idx, (des, h, dv) in enumerate(objs[:n]):
    if idx % nworkers != worker or des in done:
        continue
    if time.time() - t0 > max_s:
        break
    body = json.dumps({"desigs": [des], "output_format": ["ADES_DF"]}).encode()
    req = urllib.request.Request(URL, data=body, method="GET",
                                 headers={"Content-Type": "application/json", "User-Agent": "research-client/1.0"})
    rec = {"des": des, "h": h, "min_dv": dv}
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            js = json.load(r)
        obs = js[0]['ADES_DF'] if isinstance(js, list) else []
        if not isinstance(js, list):
            rec["error"] = str(js)[:200]
        c = collections.Counter()
        tmin = {}
        tmax = {}
        for o in obs:
            k = "%s|%s|%s" % (o.get('stn'), o.get('band'), 'm' if o.get('mag') else '-')
            c[k] += 1
            s = o.get('stn'); t = o.get('obstime')
            if t:
                tmin[s] = min(tmin.get(s, t), t); tmax[s] = max(tmax.get(s, t), t)
        rec["nobs"] = len(obs)
        rec["counts"] = dict(c)
        rec["x05_span"] = [tmin.get('X05'), tmax.get('X05')]
        ts = sorted(o['obstime'] for o in obs if o.get('obstime'))
        rec["arc"] = [ts[0], ts[-1]] if ts else None
    except Exception as e:
        rec["error"] = repr(e)[:200]
    out.write(json.dumps(rec) + "\n"); out.flush()
    count += 1
    time.sleep(0.2)
print("done", count)
