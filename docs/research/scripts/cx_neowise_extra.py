"""Parse the NEOWISE reactivation years 4-7 thermal-fit tables (Masiero+2020 PSJ 1:5, Masiero+2021 PSJ 2:162; AAS
machine-readable tables from content.cld.iop.org) and write neowise_extra.json = {pdes: [[diam_km, tag], ...]}.
Usage: python3 -I cx_neowise_extra.py <catalogs_dir> <neowise_extra_dir> <out_json>
NEO tables: psjab7820t1 (year 4), psjab7820t3 (year 5), psjac15fbt1 (year 6), psjac15fbt3 (year 7).
MBA tables (t2/t4) are scanned only to report rows that resolve to an SBDB NEA (possible mis-filed objects)."""
import sys, os, json, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats

CAT, NX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))


def rows(fn):
    lines = open(os.path.join(NX, fn), errors='replace').read().split('\n')
    seps = [i for i, l in enumerate(lines) if l.startswith('-----')]
    for l in lines[seps[-1] + 1:]:
        if len(l) < 26:
            continue
        name = l[0:7].strip()
        try:
            dia = float(l[20:26])
        except ValueError:
            dia = None
        yield name, dia, l


out = collections.defaultdict(list)
# psjab8638t1 = Masiero+2020b, PSJ 1:9, "299 NEOs manually recovered" (reactivation years 1-5, short-arc objects)
for fn, tag in (('psjab7820t1_mrt.txt', 'Mas20y4'), ('psjab7820t3_mrt.txt', 'Mas20y5'), ('psjac15fbt1_mrt.txt', 'Mas21y6'), ('psjac15fbt3_mrt.txt', 'Mas21y7'),
                ('psjab8638t1_mrt.txt', 'Mas20b')):
    n = m = 0
    un = set()
    names = set()
    for name, dia, _ in rows(fn):
        n += 1
        names.add(name)
        p = U.by_packed(name)
        if p:
            out[p].append([dia, tag])
            m += 1
        else:
            un.add(name)
    print('%s %-8s rows %4d distinct ids %4d matched rows %4d unmatched ids %d %s' % (fn, tag, n, len(names), m, len(un), sorted(un)[:8]))
for fn, tag in (('psjab7820t2_mrt.txt', 'Mas20y4-MBA'), ('psjab7820t4_mrt.txt', 'Mas20y5-MBA'), ('psjac15fbt2_mrt.txt', 'Mas21y6-MBA'), ('psjac15fbt4_mrt.txt', 'Mas21y7-MBA')):
    n = 0
    hits = []
    for name, dia, _ in rows(fn):
        n += 1
        p = U.by_packed(name)
        if p:
            hits.append((p, dia, p in nh))
    print('%s %-12s rows %5d | rows resolving to an SBDB NEA: %d %s' % (fn, tag, n, len(hits), hits[:10]))
json.dump(out, open(OUT, 'w'))
print('distinct NEAs in years 4-7 NEO tables:', len(out), '| NHATS members:', sum(1 for p in out if p in nh))
print('NHATS members:', sorted((p, out[p]) for p in out if p in nh))
