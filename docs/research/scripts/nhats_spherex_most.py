"""For a list of NHATS designations, ask IRSA MOST which SPHEREx spectral images cover the
object's predicted position, and tally predicted V magnitudes.
Usage: python3 -I nhats_spherex_most.py <nhats_json> <out_prefix> <mode> <n> <seed> <worker> <nworkers> <max_seconds>
mode: 'random' (first n of seeded shuffle) or 'bright' (all with H < n)
"""
import json, sys, random, time, urllib.request, urllib.parse, glob

nhats_path, out_path, mode, n, seed = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
worker, nworkers, max_s = int(sys.argv[6]), int(sys.argv[7]), float(sys.argv[8])
t0 = time.time()
d = json.load(open(nhats_path))
objs = [(x['des'], x.get('h')) for x in d['data']]
if mode == 'random':
    random.Random(seed).shuffle(objs)
    objs = objs[:int(n)]
else:
    objs = sorted([o for o in objs if o[1] and float(o[1]) < n], key=lambda o: float(o[1]))
done = set()
for p in glob.glob(out_path + '.w*'):
    for line in open(p):
        r = json.loads(line)
        if 'error' not in r:
            done.add(r['des'])
out = open(out_path + '.w%d' % worker, 'a')
URL = "https://irsa.ipac.caltech.edu/cgi-bin/MOST/nph-most"


def parse(text):
    hdr = None
    rows = []
    idx = []
    for line in text.splitlines():
        if line.startswith('\\'):
            continue
        if line.startswith('|'):
            if hdr is None:
                hdr = [c.strip() for c in line.strip().strip('|').split('|')]
                idx = [i for i, ch in enumerate(line) if ch == '|']
            continue
        if hdr and line.strip():
            vals = [line[idx[i] + 1:idx[i + 1]].strip() for i in range(len(idx) - 1)]
            rows.append(dict(zip(hdr, vals)))
    return rows


cnt = 0
for i, (des, h) in enumerate(objs):
    if i % nworkers != worker or des in done:
        continue
    if time.time() - t0 > max_s:
        break
    q = urllib.parse.urlencode({"catalog": "spherex", "input_type": "name_input", "obj_name": des,
                                "obs_begin": "2025-05-01", "obs_end": "2026-11-15",
                                "output_mode": "Brief", "obj_type": "Asteroid"})
    rec = {"des": des, "h": h}
    try:
        req = urllib.request.Request(URL + "?" + q, headers={"User-Agent": "research-client/1.0"})
        with urllib.request.urlopen(req, timeout=150) as r:
            text = r.read().decode('utf-8', 'replace')
        if 'object_name' not in text:
            rec["error"] = text[:200]
        rows = parse(text)
        v = []
        for r_ in rows:
            try:
                v.append((float(r_['vmag']), r_['start_date'][:10], float(r_['geo_dist']), float(r_['phase'])))
            except Exception:
                pass
        rec["nrows"] = len(rows)
        rec["n_lt"] = {str(m): sum(1 for x in v if x[0] < m) for m in (16, 17, 18, 19, 20, 21)}
        if v:
            b = min(v)
            rec["best"] = {"vmag": b[0], "date": b[1], "geo_dist": b[2], "phase": b[3]}
    except Exception as e:
        rec["error"] = repr(e)[:200]
    out.write(json.dumps(rec) + "\n")
    out.flush()
    cnt += 1
    time.sleep(0.3)
print("done", cnt)
