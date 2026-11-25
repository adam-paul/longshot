"""Fetch SsODNet ssoCards for a list of designations, strictly one request at a time over ONE reused HTTPS connection.
Usage: python3 -I cx_fetch_cards_list.py <list.txt> <out_dir> <max_seconds> [pause_s]
list.txt: one SBDB primary designation per line (number or 'YYYY XXnnn'), in priority order.
Writes <out_dir>/<des with _>.json (raw response body) and appends to <out_dir>/_status.tsv (des, http status, bytes).
A 404 is recorded as a status line (object unknown to SsODNet) and not re-requested. Existing files are skipped."""
import sys, os, re, json, time, http.client, urllib.parse

lst, out, max_s = sys.argv[1], sys.argv[2], float(sys.argv[3])
pause = float(sys.argv[4]) if len(sys.argv) > 4 else 0.3
os.makedirs(out, exist_ok=True)
HOST = 'ssp.imcce.fr'
PATH = '/webservices/ssodnet/api/ssocard/'
done = {}
st_path = os.path.join(out, '_status.tsv')
if os.path.exists(st_path):
    for l in open(st_path):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 2:
            done[f[0]] = f[1]


def safe(s):
    return re.sub(r'[^A-Za-z0-9_]', '_', s)


des = [l.strip() for l in open(lst) if l.strip()]
todo = [d for d in des if not (os.path.exists(os.path.join(out, safe(d) + '.json')) or done.get(d) == '404')]
print('list', len(des), 'to fetch', len(todo), flush=True)
conn = None
t0 = time.time()
ok = nf = err = 0
with open(st_path, 'a') as st:
    for i, d in enumerate(todo):
        if time.time() - t0 > max_s:
            print('time limit reached', flush=True)
            break
        q = urllib.parse.quote(d.replace(' ', '_'))
        body = None
        status = None
        for attempt in (1, 2):
            try:
                if conn is None:
                    conn = http.client.HTTPSConnection(HOST, timeout=45)
                conn.request('GET', PATH + q, headers={'User-Agent': 'python-http.client (sequential research script)', 'Accept': 'application/json'})
                r = conn.getresponse()
                body = r.read()
                status = r.status
                break
            except Exception as e:  # noqa: BLE001
                status = 'ERR ' + type(e).__name__
                try:
                    conn.close()
                except Exception:  # noqa: BLE001
                    pass
                conn = None
                time.sleep(2)
        if status == 200:
            try:
                json.loads(body)
                with open(os.path.join(out, safe(d) + '.json'), 'wb') as f:
                    f.write(body)
                ok += 1
            except Exception:  # noqa: BLE001
                status = 'BADJSON'
                err += 1
        elif status == 404:
            nf += 1
        else:
            err += 1
        st.write('%s\t%s\t%d\n' % (d, status, len(body) if body else 0))
        st.flush()
        if (i + 1) % 50 == 0:
            print(i + 1, 'ok', ok, '404', nf, 'err', err, round(time.time() - t0), 's', flush=True)
        time.sleep(pause)
print('done ok', ok, '404', nf, 'err', err, round(time.time() - t0), 's', flush=True)
