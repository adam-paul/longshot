"""Item 1 (sizes): which NHATS objects have an albedo-independent size, from local tables.
Usage: python cx_sizes.py <catalogs_dir> <coverage_exact_dir> <out_json>
Sources: SBDB diameter (local snapshot), Spitzer NEO table (github mommermi/spitzerneos), NEOWISE thermal-fit tables on the
CfA VizieR mirror (Mainzer+2011/2012/2014, Nugent+2015/2016, Masiero+2017/2018; plus Masiero+2020/2021 if present),
SBDB radar-observation counts. Writes per-object evidence for every NEA and prints NHATS counts."""
import sys, os, csv, json, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats, parse_vizier

CAT, CX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))


def has(v):
    return v not in (None, '')


def fl(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


E = collections.defaultdict(dict)   # pdes -> source tag -> diameter km (or list)

# ---- Spitzer ----
n_rows = n_match = 0
sp_un = []
for r in csv.DictReader(open(os.path.join(CX, 'spitzer', 'spitzerneos.csv'))):
    n_rows += 1
    d = fl(r['diam'])
    p = U.resolve(r['number'], r['desig'], r['name'])
    if not p:
        sp_un.append((r['number'], r['desig'], r['name']))
        continue
    n_match += 1
    if d is not None and d == d:
        E[p].setdefault('spitzer', []).append((d, r['survey'], fl(r['ch2snr'])))
print('Spitzer rows', n_rows, 'matched to SBDB NEA', n_match, 'unmatched', len(sp_un), sp_un[:8])
print('Spitzer distinct NEAs with diameter', sum(1 for p in E if 'spitzer' in E[p]))

# ---- NEOWISE VizieR tables ----
NV = os.path.join(CX, 'vizier')


def add_neow(tag, fn, tn, packed_cols=(), text_cols=(), diam='Diam', cond=None):
    path = os.path.join(NV, fn)
    if not os.path.exists(path):
        print('NEOWISE table %-6s MISSING (%s)' % (tag, fn))
        return
    rows = parse_vizier(path)[tn]
    n = 0
    un = set()
    for r in rows:
        if cond and not cond(r):
            continue
        p = U.resolve(*[r.get(c) for c in text_cols], packed=[r.get(c) for c in packed_cols])
        if p:
            d = fl(r.get(diam))
            E[p].setdefault('neowise', []).append((d, tag))
            n += 1
        else:
            un.add(tuple(r.get(c) for c in list(packed_cols) + list(text_cols)))
    print('NEOWISE table %-6s rows %5d matched-to-NEA rows %5d distinct unmatched ids %d %s' % (tag, len(rows), n, len(un), sorted(un)[:5]))


add_neow('Mai11', 'J_ApJ_743_156.tsv', 'J/ApJ/743/156/table1', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Mai12', 'J_ApJ_760_L12.tsv', 'J/ApJ/760/L12/table1', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Mai14', 'J_ApJ_784_110.tsv', 'J/ApJ/784/110/table2', packed_cols=('Name', 'OName'), text_cols=('OName', 'Name'))
add_neow('Nug15', 'J_ApJ_814_117.tsv', 'J/ApJ/814/117/nea', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Nug16', 'J_AJ_152_63.tsv', 'J/AJ/152/63/asteroids', packed_cols=('MPC',), text_cols=('Name',), cond=lambda r: r['Ast'].strip() == 'NEA')
add_neow('Mas17', 'J_AJ_154_168.tsv', 'J/AJ/154/168/table1', packed_cols=('Name',))
add_neow('Mas18', 'J_AJ_156_60.tsv', 'J/AJ/156/60/table1', packed_cols=('Name',))
# optional extra NEOWISE tables registered by cx_neowise_extra.py: a JSON {pdes: [[diam_km, tag], ...]}
extra = os.path.join(CX, 'neowise_extra.json')
if os.path.exists(extra):
    for p, lst in json.load(open(extra)).items():
        if p in U.by_pdes:
            for d, tag in lst:
                E[p].setdefault('neowise', []).append((d, tag))
    print('NEOWISE extra tables merged from', extra)
print('NEOWISE distinct NEAs with a published fit (tables loaded):', sum(1 for p in E if 'neowise' in E[p]))

# ---- SBDB ----
for s in U.rows:
    p = s['pdes']
    if has(s['diameter']):
        E[p]['sbdb'] = (fl(s['diameter']), fl(s['diameter_sigma']), fl(s['albedo']))
    nd = int(s['n_del_obs_used'] or 0)
    ndp = int(s['n_dop_obs_used'] or 0)
    if nd or ndp:
        E[p]['radar_astrom'] = (nd, ndp)

out = {}
for s in U.rows:
    p = s['pdes']
    e = E.get(p, {})
    out[p] = {'name': s.get('name'), 'H': fl(s['H']), 'nhats': p in nh, 'dv': nh[p]['dv'] if p in nh else None,
              'A1': has(s['A1']), 'A2': has(s['A2']), 'A2_val': fl(s['A2']), 'A2_sig': fl(s['A2_sigma']), 'A1_val': fl(s['A1']), 'A1_sig': fl(s['A1_sigma']),
              'data_arc': s['data_arc'], 'cond': s['condition_code'],
              'sbdb': e.get('sbdb'), 'spitzer': e.get('spitzer'), 'neowise': e.get('neowise'), 'radar_astrom': e.get('radar_astrom')}
json.dump(out, open(OUT, 'w'))


def table(label, pred):
    scopes = [('all NHATS', lambda o: o['nhats']), ('dv<6', lambda o: o['nhats'] and o['dv'] < 6), ('dv<5', lambda o: o['nhats'] and o['dv'] < 5),
              ('NHATS with A1|A2', lambda o: o['nhats'] and (o['A1'] or o['A2'])), ('NHATS A2 only-or-with', lambda o: o['nhats'] and o['A2']),
              ('all NEAs', lambda o: True), ('all NEAs with A1|A2', lambda o: o['A1'] or o['A2'])]
    print('%-34s' % label + '  '.join('%s %d/%d' % (n, sum(1 for o in out.values() if sc(o) and pred(o)), sum(1 for o in out.values() if sc(o))) for n, sc in scopes))


table('SBDB diameter', lambda o: o['sbdb'] is not None)
table('Spitzer diameter', lambda o: o['spitzer'] is not None)
table('NEOWISE published fit', lambda o: o['neowise'] is not None)
table('thermal IR (Spitzer|NEOWISE)', lambda o: o['spitzer'] is not None or o['neowise'] is not None)
table('thermal IR | SBDB diameter', lambda o: o['spitzer'] is not None or o['neowise'] is not None or o['sbdb'] is not None)
table('SBDB diam not in thermal tables', lambda o: o['sbdb'] is not None and o['spitzer'] is None and o['neowise'] is None)
table('radar astrometry (SBDB counts)', lambda o: o['radar_astrom'] is not None)
table('thermal|SBDB diam|radar astrom', lambda o: o['spitzer'] is not None or o['neowise'] is not None or o['sbdb'] is not None or o['radar_astrom'] is not None)

print('\n--- NHATS objects with A1 or A2 and any size evidence (thermal table or SBDB diameter):')
for p, o in sorted(out.items(), key=lambda kv: (kv[1]['dv'] or 99)):
    if o['nhats'] and (o['A1'] or o['A2']) and (o['sbdb'] or o['spitzer'] or o['neowise']):
        print('%-11s %-11s dv=%5.2f H=%5.2f A2=%s A1=%s sbdb=%s spitzer=%s neowise=%s radar=%s' % (
            p, o['name'] or '', o['dv'], o['H'], 'y' if o['A2'] else '-', 'y' if o['A1'] else '-', o['sbdb'],
            [(x[0], x[1]) for x in o['spitzer']] if o['spitzer'] else None, o['neowise'], o['radar_astrom']))
print('\n--- NHATS SBDB-diameter objects NOT in Spitzer/NEOWISE tables loaded:')
for p, o in sorted(out.items(), key=lambda kv: (kv[1]['dv'] or 99)):
    if o['nhats'] and o['sbdb'] and not o['spitzer'] and not o['neowise']:
        print('%-11s %-11s dv=%5.2f H=%5.2f sbdb=%s radar=%s' % (p, o['name'] or '', o['dv'], o['H'], o['sbdb'], o['radar_astrom']))
