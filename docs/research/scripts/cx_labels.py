"""Item 3 (labelled set): distinct NEAs with any spectral or colour taxonomy, by H bin, and NHATS membership.
Usage: python cx_labels.py <catalogs_dir> <coverage_exact_dir> [cards_dir]
Published tables (CfA VizieR mirror): Mahlke+2022 J/A+A/665/A26, Sergeyev+2023 J/A+A/679/A148, Devogele+2019 J/AJ/158/196,
Marsset+2022 J/AJ/163/165, Navarro-Meza+2024 J/AJ/167/163, Ieva+2020 J/A+A/644/A23 (NEOShield-2 + literature compilation),
Deshapriya+2023 J/A+A/674/A50 (taxonomy column), Erasmus+2017 J/AJ/154/162, Popescu+2019 J/A+A/627/A124; plus SBDB spec_B/spec_T.
Optionally SsODNet ssoCards (taxonomy block) for the NHATS subset fetched. Writes labels.json (pdes -> sources/classes)."""
import sys, os, json, glob, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats, parse_vizier, norm

CAT, CX = sys.argv[1], sys.argv[2]
CARDS = sys.argv[3] if len(sys.argv) > 3 else None
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
V = os.path.join(CX, 'vizier')


def fl(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


H = {s['pdes']: fl(s['H']) for s in U.rows}
L = collections.defaultdict(dict)   # pdes -> source -> class string
kind = {}                            # source -> 'spec' | 'phot' | 'mixed'


def load(tag, knd, fn, tn, getter, cols):
    path = os.path.join(V, fn)
    kind[tag] = knd
    if not os.path.exists(path):
        print('%-10s MISSING %s' % (tag, fn))
        return
    rows = parse_vizier(path)[tn]
    n = 0
    un = 0
    for r in rows:
        cls = getter(r)
        if cls is None:
            continue
        p = U.resolve(*[r.get(c) for c in cols])
        if p:
            L[p][tag] = cls
            n += 1
        else:
            un += 1
    print('%-10s rows %5d | rows with a class matched to an SBDB NEA %5d | not NEA/unmatched %5d | distinct NEAs %d' % (
        tag, len(rows), n, un, sum(1 for p in L if tag in L[p])))


def nz(v):
    v = (v or '').strip()
    return v if v and v not in ('0', '-') else None


load('mahlke22', 'spec', 'J_A_A_665_A26.tsv', 'J/A+A/665/A26/asteroid', lambda r: nz(r['class']), ('Number', 'Name'))
load('sergeyev23', 'phot', 'J_A_A_679_A148.tsv', 'J/A+A/679/A148/catalog', lambda r: nz(r['Complex']) if nz(r['Complex']) != 'U' else None, ('Number', 'Design', 'Name'))
load('sergeyev23U', 'phot-unclassified', 'J_A_A_679_A148.tsv', 'J/A+A/679/A148/catalog', lambda r: 'U' if nz(r['Complex']) == 'U' else None, ('Number', 'Design', 'Name'))
load('devogele19', 'spec', 'J_AJ_158_196.tsv', 'J/AJ/158/196/table5', lambda r: nz(r['Taxon']), ('ID',))
load('marsset22', 'spec', 'J_AJ_163_165.tsv', 'J/AJ/163/165/table7', lambda r: nz(r['Taxon']), ('Number', 'Desig', 'Name'))
load('ratir24hi', 'phot', 'J_AJ_167_163.tsv', 'J/AJ/167/163/table4', lambda r: 'p>50', ('ID',))
load('ratir24lo', 'phot-lowconf', 'J_AJ_167_163.tsv', 'J/AJ/167/163/table5', lambda r: 'p<50', ('ID',))
load('ieva20', 'mixed', 'J_A_A_644_A23.tsv', 'J/A+A/644/A23/tablea1', lambda r: nz(r['Taxon']), ('Name',))
load('deshap23', 'mixed', 'J_A_A_674_A50.tsv', 'J/A+A/674/A50/dataset', lambda r: nz(r['Taxo']) if nz(r['Taxo']) not in ('No_Taxo', 'U') else None, ('Number', 'Design', 'Name'))
load('erasmus17', 'phot', 'J_AJ_154_162.tsv', 'J/AJ/154/162/table1', lambda r: 'prob', ('ID',))
load('popescu19', 'spec', 'J_A_A_627_A124.tsv', 'J/A+A/627/A124/log', lambda r: 'spectrum', ('Name',))
kind['sbdb'] = 'spec'
for s in U.rows:
    c = (s['spec_B'] or '') + ('/' + s['spec_T'] if s['spec_T'] else '')
    if s['spec_B'] or s['spec_T']:
        L[s['pdes']]['sbdb'] = c
print('%-10s distinct NEAs %d' % ('sbdb', sum(1 for p in L if 'sbdb' in L[p])))

card_have = set()
kind['ssocard'] = 'mixed'
card_tax_meta = collections.Counter()
if CARDS:
    for fn in glob.glob(os.path.join(CARDS, '*.json')):
        if os.path.basename(fn).startswith('_'):
            continue
        try:
            c = json.load(open(fn))
        except Exception:  # noqa: BLE001
            continue
        if 'parameters' not in c:
            continue
        p = U.by_number(c['number']) if c.get('number') else None
        if p is None:
            p = U.key2p.get(norm(str(c.get('name') or ''))) or U.key2p.get(norm(str(c.get('id') or '')))
        if not p:
            continue
        card_have.add(p)
        tx = ((c['parameters'].get('physical') or {}).get('taxonomy')) or {}
        cls = tx.get('class') if isinstance(tx, dict) else None
        if isinstance(cls, dict):
            cls = cls.get('value')
        if cls:
            L[p]['ssocard'] = str(cls)
            card_tax_meta[(str(tx.get('technique')), str(tx.get('scheme')))] += 1
    print('ssoCards read %d (NHATS %d) | with taxonomy %d | technique/scheme %s' % (
        len(card_have), sum(1 for p in card_have if p in nh), sum(1 for p in L if 'ssocard' in L[p]), card_tax_meta.most_common(12)))

STRICT = [t for t, k in kind.items() if k in ('spec', 'phot', 'mixed') and t != 'ssocard']
SPEC = [t for t, k in kind.items() if k == 'spec']
LOOSE = [t for t in kind if t != 'ssocard']
BINS = [(-99, 22, 'H<22'), (22, 25, '22<=H<25'), (25, 99, 'H>=25'), (-99, 99, 'all')]


def count(tags, scope):
    out = []
    for lo, hi, lab in BINS:
        out.append(sum(1 for p in scope if H.get(p) is not None and lo <= H[p] < hi and any(t in L.get(p, {}) for t in tags)))
    return out


allp = [s['pdes'] for s in U.rows]
nhl = list(nh)
n6 = [p for p in nhl if nh[p]['dv'] < 6]
n5 = [p for p in nhl if nh[p]['dv'] < 5]
print('\npopulation sizes       %s' % '  '.join('%s' % lab for _, _, lab in BINS))
for nm, sc in (('all NEAs', allp), ('NHATS', nhl), ('NHATS dv<6', n6), ('NHATS dv<5', n5)):
    print('  %-12s %s' % (nm, [sum(1 for p in sc if H.get(p) is not None and lo <= H[p] < hi) for lo, hi, _ in BINS]))
print('\n%-44s %-28s %-24s %-20s %-18s' % ('label definition  [H<22, 22-25, >=25, all]', 'all NEAs', 'NHATS', 'NHATS dv<6', 'NHATS dv<5'))
rows = [('each source alone:', None)]
for t in LOOSE + (['ssocard'] if CARDS else []):
    rows.append(('  ' + t + ' (' + kind[t] + ')', [t]))
rows += [('UNION spectral classes only', SPEC), ('UNION classified (spec + phot p>50, excl. U/lowconf)', STRICT),
         ('UNION incl. Sergeyev U and RATIR p<50', LOOSE)]
if CARDS:
    rows += [('UNION classified + ssoCard taxonomy (NHATS subset only)', STRICT + ['ssocard'])]
for lab, tags in rows:
    if tags is None:
        print(lab)
        continue
    print('%-52s %-26s %-22s %-18s %-16s' % (lab, count(tags, allp), count(tags, nhl), count(tags, n6), count(tags, n5)))

# How many sources per labelled NEA (independent confirmations), and class-agreement groundwork
ns = collections.Counter(sum(1 for t in STRICT if t in L[p]) for p in L if any(t in L[p] for t in STRICT))
print('\nnumber of independent sources per classified NEA:', sorted(ns.items()))
if CARDS:
    sub = [p for p in nhl if p in card_have]
    a = sum(1 for p in sub if 'ssocard' in L.get(p, {}))
    b = sum(1 for p in sub if any(t in L.get(p, {}) for t in STRICT))
    both = sum(1 for p in sub if 'ssocard' in L.get(p, {}) and any(t in L.get(p, {}) for t in STRICT))
    print('Among %d NHATS with a card: ssoCard taxonomy %d | published-table class %d | both %d | card only %d | tables only %d' % (len(sub), a, b, both, a - both, b - both))
    print('  card-only examples:', [(p, L[p]['ssocard']) for p in sub if 'ssocard' in L.get(p, {}) and not any(t in L[p] for t in STRICT)][:25])
    print('  tables-only examples:', [(p, {t: L[p][t] for t in STRICT if t in L[p]}) for p in sub if 'ssocard' not in L.get(p, {}) and any(t in L.get(p, {}) for t in STRICT)][:15])
    for nm, sc in (('dv<6', n6), ('dv<5', n5)):
        s2 = [p for p in sc if p in card_have]
        print('  %s: cards %d of %d | ssoCard taxonomy %d | tables classified %d | union %d' % (nm, len(s2), len(sc), sum(1 for p in s2 if 'ssocard' in L.get(p, {})),
              sum(1 for p in sc if any(t in L.get(p, {}) for t in STRICT)), sum(1 for p in sc if any(t in L.get(p, {}) for t in STRICT + ['ssocard']))))
json.dump({p: L[p] for p in L}, open(os.path.join(CX, 'labels.json'), 'w'))
