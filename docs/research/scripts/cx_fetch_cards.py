"""Sequentially fetch SsODNet ssoCards (one request at a time, polite pause) for NEAs whose BFT row shows a size, albedo,
density, mass or thermal inertia, or which have radar records; these are the objects whose method labels / CPR the BFT lacks.
Usage: cx_fetch_cards.py <master.parquet> <sbdb_neo.json> <out_dir> <scope: nhats|all|count> <max_seconds> [cache_dir ...]
Cards already present in any cache_dir (or out_dir) are indexed by their own id/number/name and not re-fetched.
Writes <out_dir>/_index.json : pdes -> card path."""
import sys, os, re, json, time, glob, urllib.request, urllib.parse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from cx_lib import Universe, norm

master, sbdb, out, scope, max_s = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
caches = sys.argv[6:] + [out]
os.makedirs(out, exist_ok=True)
U = Universe(sbdb)
df = pd.read_parquet(master)

index = {}
for d in caches:
    for fn in glob.glob(os.path.join(d, '*.json')):
        if os.path.basename(fn).startswith('_'):
            continue
        try:
            c = json.load(open(fn))
        except Exception:
            continue
        if not isinstance(c, dict):
            continue
        if 'parameters' not in c and len(c) == 1:
            c = list(c.values())[0]
        if not isinstance(c, dict) or 'parameters' not in c:
            continue
        p = None
        if c.get('number'):
            p = U.by_number(c['number'])
        if p is None and c.get('name'):
            p = U.key2p.get(norm(str(c['name'])))
        if p is None and c.get('id'):
            p = U.key2p.get(norm(str(c['id'])))
        if p and p not in index:
            index[p] = fn
print('cached cards indexed:', len(index), flush=True)

need = df[df.bft & (df.bft_diam | df.bft_albedo | df.bft_density | df.bft_mass | df.bft_ti | df.radar_astrom | df.radar_detlist)]
if scope == 'nhats':
    need = need[need.nhats]
need = need.sort_values(['nhats', 'dv'], ascending=[False, True])
todo = [(r.pdes, r.bft_id) for r in need.itertuples() if r.pdes not in index]
print('scope', scope, 'targets', len(need), 'already cached', len(need) - len(todo), 'to fetch', len(todo), flush=True)
if scope == 'count':
    json.dump(index, open(os.path.join(out, '_index.json'), 'w'))
    sys.exit(0)

def safe(s):
    return re.sub(r'[^A-Za-z0-9_]', '_', s)

t0 = time.time(); ok = err = 0
for pdes, sid in todo:
    if time.time() - t0 > max_s:
        print('time limit reached', flush=True)
        break
    url = 'https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/' + urllib.parse.quote(str(sid))
    fn = os.path.join(out, safe(pdes) + '.json')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'python-urllib (research script, sequential)'})
        with urllib.request.urlopen(req, timeout=40) as resp:
            body = resp.read()
        json.loads(body)
        with open(fn, 'wb') as f:
            f.write(body)
        index[pdes] = fn; ok += 1
    except Exception as e:
        err += 1
        with open(os.path.join(out, '_errors.log'), 'a') as f:
            f.write('%s\t%s\t%s\n' % (pdes, sid, repr(e)[:120]))
    if (ok + err) % 100 == 0:
        print(ok + err, 'ok', ok, 'err', err, round(time.time() - t0), 's', flush=True)
        json.dump(index, open(os.path.join(out, '_index.json'), 'w'))
    time.sleep(0.35)
json.dump(index, open(os.path.join(out, '_index.json'), 'w'))
print('done ok', ok, 'err', err, round(time.time() - t0), 's', flush=True)
