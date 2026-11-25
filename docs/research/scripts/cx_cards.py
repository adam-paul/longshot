"""Parse fetched SsODNet ssoCards into per-object flags with methods and references.
Usage: python3 -I cx_cards.py <catalogs_dir> <cards_dir> <out_json>
Output: {pdes: {card_date, diameter:{value,methods,refs}, albedo:{...}, taxonomy:{...}, density:{...}, mass, thermal_inertia,
n_colors, color_refs, n_phase, n_spins, spin_periods, spin_refs, yarkovsky:{snr,refs}, source_regions, other_keys}}"""
import sys, os, json, glob, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats, norm

CAT, CARDS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))


def labels(x):
    m = x.get('method') if isinstance(x, dict) else None
    return sorted({str(mm.get('label')) for mm in m if isinstance(mm, dict)}) if isinstance(m, list) else []


def refs(x):
    b = x.get('bibref') if isinstance(x, dict) else None
    return sorted({str(bb.get('shortbib')) for bb in b if isinstance(bb, dict)}) if isinstance(b, list) else []


def val(x):
    if isinstance(x, dict):
        v = x.get('value')
        return v if isinstance(v, (int, float)) else None
    return None


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return [i for i in x if isinstance(i, dict)]
    if isinstance(x, dict):
        vs = list(x.values())
        if vs and all(isinstance(v, dict) for v in vs) and 'value' not in x:
            return vs
        return [x]
    return []


out = {}
keys_phys = collections.Counter()
keys_dyn = collections.Counter()
dates = collections.Counter()
nfiles = 0
for fn in sorted(glob.glob(os.path.join(CARDS, '*.json'))):
    if os.path.basename(fn).startswith('_'):
        continue
    try:
        c = json.load(open(fn))
    except Exception:  # noqa: BLE001
        continue
    if not isinstance(c, dict) or 'parameters' not in c:
        continue
    nfiles += 1
    p = U.by_number(c['number']) if c.get('number') else None
    if p is None:
        p = U.key2p.get(norm(str(c.get('name') or ''))) or U.key2p.get(norm(str(c.get('id') or '')))
    if p is None:
        base = os.path.basename(fn)[:-5].replace('_', ' ')
        p = base if base in U.by_pdes else None
    if p is None:
        print('unresolved card', fn)
        continue
    P = c['parameters']
    ph = P.get('physical') or {}
    dy = P.get('dynamical') or {}
    for k, v in ph.items():
        if v:
            keys_phys[k] += 1
    for k, v in dy.items():
        if v:
            keys_dyn[k] += 1
    dt = ((c.get('ssocard') or {}).get('datetime') or '')[:10]
    dates[dt] += 1
    rec = {'card_date': dt, 'card_class': c.get('class')}
    for k in ('diameter', 'albedo', 'density', 'mass', 'thermal_inertia'):
        x = ph.get(k)
        if isinstance(x, dict) and val(x) is not None:
            rec[k] = {'value': val(x), 'err': x.get('error'), 'methods': labels(x), 'refs': refs(x)}
    tx = ph.get('taxonomy')
    if isinstance(tx, dict) and tx.get('class'):
        rec['taxonomy'] = {'class': tx.get('class'), 'complex': tx.get('complex'), 'technique': tx.get('technique'),
                           'waverange': tx.get('waverange'), 'scheme': tx.get('scheme'), 'refs': refs(tx)}
    cols = as_list(ph.get('colors'))
    if cols:
        rec['n_colors'] = len(cols)
        rec['color_refs'] = sorted({r for x in cols for r in refs(x)})
    pf = ph.get('phase_functions')
    if pf:
        pfl = as_list(pf) if not isinstance(pf, dict) else [v for v in pf.values() if isinstance(v, dict)] or [pf]
        rec['n_phase'] = len(pfl)
        rec['phase_refs'] = sorted({r for x in pfl for r in refs(x)})
    sp = as_list(ph.get('spins'))
    pers = [val(s.get('period')) for s in sp if val(s.get('period'))]
    if pers:
        rec['n_spins'] = len(pers)
        rec['spin_periods'] = pers
        rec['spin_refs'] = sorted({r for x in sp for r in refs(x)})
        rec['spin_flags'] = sorted({str(s.get('period_flag')) for s in sp if s.get('period_flag')})
    yk = dy.get('yarkovsky')
    if isinstance(yk, dict) and (val(yk.get('dadt')) is not None or val(yk.get('A2')) is not None):
        rec['yarkovsky'] = {'dadt': val(yk.get('dadt')), 'A2': val(yk.get('A2')), 'snr': yk.get('snr'), 'refs': refs(yk), 'methods': labels(yk)}
    sr = dy.get('source_regions')
    if isinstance(sr, dict) and any(val(v) is not None for v in sr.values() if isinstance(v, dict)):
        rec['source_regions'] = True
    other = {}
    for k, v in ph.items():
        if v and k not in ('absolute_magnitude', 'diameter', 'albedo', 'density', 'mass', 'thermal_inertia', 'taxonomy', 'colors', 'phase_functions', 'spins'):
            other[k] = {'methods': labels(v), 'refs': refs(v)} if isinstance(v, dict) else len(v) if isinstance(v, list) else True
            if isinstance(v, dict) and val(v) is not None:
                other[k]['value'] = val(v)
    if other:
        rec['other'] = other
    out[p] = rec
json.dump(out, open(OUT, 'w'))
st = collections.Counter()
sp_ = os.path.join(CARDS, '_status.tsv')
if os.path.exists(sp_):
    for l in open(sp_):
        f = l.rstrip('\n').split('\t')
        if len(f) > 1:
            st[f[1]] += 1
print('cards parsed', nfiles, '-> objects', len(out), '| NHATS', sum(1 for p in out if p in nh), '| status counts', dict(st))
print('card dates', dates.most_common(5))
print('physical keys present', keys_phys.most_common())
print('dynamical keys present', keys_dyn.most_common())
for k in ('diameter', 'albedo', 'density', 'thermal_inertia', 'mass'):
    mc = collections.Counter(tuple(r[k]['methods']) for r in out.values() if k in r)
    print(k, 'n', sum(mc.values()), 'methods', mc.most_common(12))
print('diameter refs', collections.Counter(x for r in out.values() if 'diameter' in r for x in r['diameter']['refs']).most_common(25))
print('density', [(p, r['density']['value'], r['density']['methods'], r['density']['refs']) for p, r in out.items() if 'density' in r])
print('taxonomy refs', collections.Counter(x for r in out.values() if 'taxonomy' in r for x in r['taxonomy']['refs']).most_common(20))
print('spin refs', collections.Counter(x for r in out.values() if 'spin_refs' in r for x in r['spin_refs']).most_common(15))
print('yarkovsky refs', collections.Counter(x for r in out.values() if 'yarkovsky' in r for x in r['yarkovsky']['refs']).most_common(10))
print('other keys', collections.Counter(k for r in out.values() for k in r.get('other', {})).most_common())
