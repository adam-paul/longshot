"""Item 4: coverage table and the union "any composition-relevant measurement" for NHATS.
Composition-relevant (the first-round definition): taxonomy, colours, albedo, density or mass, thermal inertia, radar
circular-polarization ratio, phase function. Rotation period, Yarkovsky and plain diameter are reported but not in the union.

Usage:
  python3 -I cx_union.py flags  <catalogs_dir> <cx_dir>                      -> writes table_flags.json, prints table-only counts
  python3 -I cx_union.py sample <catalogs_dir> <cx_dir> <n> <seed> <out_list> -> seeded random sample of NHATS objects with no
                                                                                table flag and no card yet (for the stratified estimate)
  python3 -I cx_union.py report <catalogs_dir> <cx_dir> <sample_list|->       -> full coverage table using cards_flags.json
Inputs in <cx_dir>: sizes_local.json (cx_sizes.py), labels.json (cx_labels.py), cards_flags.json (cx_cards.py), cards/_status.tsv"""
import sys, os, json, random, math, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats

mode, CAT, CX = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
sz = json.load(open(os.path.join(CX, 'sizes_local.json')))
lab = json.load(open(os.path.join(CX, 'labels.json')))


def has(v):
    return v not in (None, '')


TAX_T = ('mahlke22', 'sergeyev23', 'devogele19', 'marsset22', 'ratir24hi', 'ieva20', 'deshap23', 'erasmus17', 'popescu19', 'sbdb')
COL_T = ('sergeyev23', 'sergeyev23U', 'ratir24hi', 'ratir24lo', 'erasmus17')
T = {}
for s in U.rows:
    p = s['pdes']
    L = lab.get(p, {})
    o = sz[p]
    T[p] = {
        'tax': any(t in L for t in TAX_T),
        'col': any(t in L for t in COL_T) or has(s['BV']) or has(s['UB']),
        'alb': has(s['albedo']) or bool(o.get('spitzer')) or bool(o.get('neowise')),
        'dens': has(s['GM']) or has(s['density']),
        'diam': has(s['diameter']) or bool(o.get('spitzer')) or bool(o.get('neowise')),
        'rot': has(s['rot_per']),
        'yark': has(s['A2']),
        'a1': has(s['A1']),
        'radar': o.get('radar_astrom') is not None,
    }
    T[p]['any'] = T[p]['tax'] or T[p]['col'] or T[p]['alb'] or T[p]['dens']
allp = list(T)
nhl = list(nh)
n6 = [p for p in nhl if nh[p]['dv'] < 6]
n5 = [p for p in nhl if nh[p]['dv'] < 5]
SC = [('all NHATS', nhl), ('dv<6', n6), ('dv<5', n5), ('all NEAs', allp)]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


if mode == 'flags':
    json.dump(T, open(os.path.join(CX, 'table_flags.json'), 'w'))
    print('TABLES ONLY (no SsODNet): exact counts   ' + '   '.join('%s (%d)' % (n, len(s)) for n, s in SC))
    for k, lab_ in (('tax', 'taxonomy (10 tables + SBDB)'), ('col', 'colours (Sergeyev incl. U, RATIR, Erasmus, SBDB B-V/U-B)'), ('alb', 'albedo (SBDB, Spitzer, NEOWISE tables)'),
                    ('diam', 'measured diameter (SBDB, Spitzer, NEOWISE tables)'), ('dens', 'GM or density (SBDB)'), ('rot', 'rotation period (SBDB)'),
                    ('yark', 'A2 (SBDB)'), ('a1', 'A1 (SBDB)'), ('radar', 'radar astrometry (SBDB counts)'), ('any', 'ANY composition-relevant, tables only')):
        print('%-58s' % lab_ + '  '.join('%6d' % sum(1 for p in s if T[p][k]) for _, s in SC))
    sys.exit(0)

status = {}
sp = os.path.join(CX, 'cards', '_status.tsv')
if os.path.exists(sp):
    for l in open(sp):
        f = l.rstrip('\n').split('\t')
        if len(f) > 1:
            status[f[0]] = f[1]

if mode == 'sample':
    n, seed, out = int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    pool = sorted(p for p in nhl if not T[p]['any'] and nh[p]['dv'] >= 6)
    random.Random(seed).shuffle(pool)
    # the sample is the shuffled prefix, regardless of whether a card was already fetched for another reason (keeps it unbiased)
    open(out, 'w').write('\n'.join(pool[:n]) + '\n')
    print('pool (NHATS dv>=6 with no table flag):', len(pool), '| sample', n, '| already fetched', sum(1 for p in pool[:n] if p in status))
    sys.exit(0)

cards = json.load(open(os.path.join(CX, 'cards_flags.json')))
sample_list = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None


def cflags(p):
    c = cards.get(p)
    if c is None:
        return None
    alb_meas = 'albedo' in c   # SsODNet "Computed" albedo needs a measured diameter, so it counts as an albedo measurement (first-round convention)
    f = {'tax': 'taxonomy' in c, 'col': c.get('n_colors', 0) > 0, 'alb': alb_meas, 'diam': 'diameter' in c, 'dens': 'density' in c, 'mass': 'mass' in c,
         'ti': 'thermal_inertia' in c, 'cpr': 'circular_polarization_ratio' in c.get('other', {}), 'phase': c.get('n_phase', 0) > 0,
         'rot': c.get('n_spins', 0) > 0, 'yark': 'yarkovsky' in c, 'src': bool(c.get('source_regions'))}
    f['any'] = f['tax'] or f['col'] or f['alb'] or f['dens'] or f['mass'] or f['ti'] or f['cpr'] or f['phase']
    return f


CF = {p: cflags(p) for p in nhl}
print('NHATS %d | cards parsed %d | SsODNet 404 (unknown object) %d | not requested %d' % (
    len(nhl), sum(1 for p in nhl if CF[p]), sum(1 for p in nhl if status.get(p) == '404'), sum(1 for p in nhl if p not in status)))
for nm, s in SC[:3]:
    print('  %-10s N %5d | card %5d | 404 %4d | not requested %5d' % (nm, len(s), sum(1 for p in s if CF[p]), sum(1 for p in s if status.get(p) == '404'), sum(1 for p in s if p not in status)))

print('\nEXACT where every object was requested (dv<6, dv<5); for all NHATS the SsODNet rows are lower bounds from the cards fetched')
print('%-46s %-22s %-22s %-22s' % ('channel', 'all NHATS (cards so far)', 'dv<6', 'dv<5'))
for k, lab_ in (('tax', 'taxonomy'), ('alb', 'albedo'), ('diam', 'diameter'), ('rot', 'rotation period'), ('col', 'colours'), ('dens', 'density'), ('mass', 'mass'),
                ('ti', 'thermal inertia'), ('cpr', 'radar circular polarization ratio'), ('phase', 'phase function'), ('yark', 'Yarkovsky (SsODNet)'), ('src', 'source regions'),
                ('any', 'ANY composition-relevant')):
    row = []
    for nm, s in SC[:3]:
        c = sum(1 for p in s if CF[p] and CF[p][k])
        t = sum(1 for p in s if T[p].get(k)) if k in T[nhl[0]] else None
        u = sum(1 for p in s if (CF[p] and CF[p][k]) or (T[p].get(k) if k in T[p] else False))
        row.append('card %4d tbl %s union %4d' % (c, '%4d' % t if t is not None else '   -', u))
    print('%-46s %s' % (lab_, ' | '.join(row)))

for nm, s in SC[1:3]:
    u = [p for p in s if (CF[p] and CF[p]['any']) or T[p]['any']]
    print('\n%s: ANY composition-relevant, union of cards and tables = %d of %d  (cards alone %d, tables alone %d)' % (
        nm, len(u), len(s), sum(1 for p in s if CF[p] and CF[p]['any']), sum(1 for p in s if T[p]['any'])))
    for p in sorted(u, key=lambda p: nh[p]['dv']):
        c = CF[p] or {}
        what = [k for k in ('tax', 'col', 'alb', 'dens', 'mass', 'ti', 'cpr', 'phase') if c.get(k)]
        tw = [k for k in ('tax', 'col', 'alb', 'dens') if T[p][k]]
        tx = (cards.get(p) or {}).get('taxonomy') or {}
        print('   %-11s dv=%.2f H=%5.1f card:%-28s tables:%-16s %s %s' % (p, nh[p]['dv'], nh[p]['h'] or float('nan'), ','.join(what) or '-', ','.join(tw) or '-',
              tx.get('class') or '', ','.join(tx.get('refs', []))[:60]))
    tcl = collections.Counter(((cards.get(p) or {}).get('taxonomy') or {}).get('complex') or ((cards.get(p) or {}).get('taxonomy') or {}).get('class') for p in s if CF[p] and CF[p]['tax'])
    print('   taxonomy (card) complex mix:', tcl.most_common())

# all NHATS: stratified estimate
fetched_any = [p for p in nhl if (CF[p] and CF[p]['any'])]
exact_known = set(p for p in nhl if T[p]['any']) | set(fetched_any)
print('\nALL NHATS: objects with ANY composition-relevant measurement known exactly so far (tables union cards fetched): %d' % len(exact_known))
print('   tables alone: %d | cards alone (among %d fetched): %d' % (sum(1 for p in nhl if T[p]['any']), sum(1 for p in nhl if CF[p]), len(fetched_any)))
if sample_list:
    # Stratified estimate.
    # Targeted stratum = every object named in the targeted lists (argv[5:]): fetched by criterion, so exact.
    # Remainder stratum R = NHATS objects in no targeted list. The seeded sample is a random prefix of the shuffled
    # "no table flag, dv>=6" pool; its members that fall in R are a simple random sample of R.
    samp = [l.strip() for l in open(sample_list) if l.strip()]
    targeted = set()
    for fn in sys.argv[5:]:
        targeted |= {l.strip() for l in open(fn) if l.strip()}
    R = [p for p in nhl if p not in targeted]
    notreq_t = [p for p in targeted if p in nh and p not in status]
    sR = [p for p in samp if p not in targeted and p in status]
    print('   targeted lists: %d NHATS objects (%d not yet requested) | remainder stratum R: %d | sample members in R with a request: %d (%d unknown to SsODNet)' % (
        sum(1 for p in targeted if p in nh), len(notreq_t), len(R), len(sR), sum(1 for p in sR if status[p] == '404')))
    print('   R objects carrying any table flag (should be 0):', sum(1 for p in R if any(T[p][k] for k in ('tax', 'col', 'alb', 'diam', 'dens', 'rot', 'yark', 'a1', 'radar'))),
          '| R objects with dv<6 (should be 0):', sum(1 for p in R if nh[p]['dv'] < 6))
    n = max(1, len(sR))
    Rset = set(R)
    print('   %-34s %6s  %-18s %s' % ('channel (all NHATS)', 'exact', 'sample hits in R', 'estimate (95% Wilson)'))
    for kk, lab_ in (('any', 'ANY composition-relevant'), ('tax', 'taxonomy'), ('alb', 'albedo'), ('diam', 'diameter'), ('col', 'colours'), ('rot', 'rotation period'),
                     ('dens', 'density'), ('mass', 'mass'), ('ti', 'thermal inertia'), ('cpr', 'radar polarization ratio'), ('phase', 'phase function'),
                     ('yark', 'Yarkovsky (SBDB A2 or SsODNet)'), ('src', 'source regions (SsODNet)')):
        ex = sum(1 for p in nhl if p not in Rset and ((CF[p] and CF[p][kk]) or T[p].get(kk, False)))
        ex_card = sum(1 for p in nhl if p not in Rset and CF[p] and CF[p][kk])
        ks = sum(1 for p in sR if CF.get(p) and CF[p][kk])
        l2, h2 = wilson(ks, n)
        print('   %-34s %6d  %3d/%d of %d       %.0f (%.0f to %.0f)   [SsODNet alone: %d exact + est. %.0f = %.0f]' % (
            lab_, ex, ks, n, len(R), ex + len(R) * ks / n, ex + len(R) * l2, ex + len(R) * h2, ex_card, len(R) * ks / n, ex_card + len(R) * ks / n))
    hits = [(p, [k for k in ('tax', 'col', 'alb', 'dens', 'cpr', 'phase', 'rot', 'yark') if CF[p][k]]) for p in sR if CF.get(p) and (CF[p]['any'] or CF[p]['rot'] or CF[p]['yark'])]
    print('   sample hits:', hits)
