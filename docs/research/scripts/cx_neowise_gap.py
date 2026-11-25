"""Item 5 (NEOWISE gap): for NHATS objects with C51 (NEOWISE) astrometry and no SBDB diameter, is there a published
NEOWISE thermal fit that SBDB simply lacks?
Usage: python3 -I cx_neowise_gap.py <c51_census.jsonl> <sizes_local.json> [cards_flags.json]
Also: SBDB completeness against the published NEOWISE tables for all NEAs and for NHATS."""
import sys, json, collections

rows = [json.loads(l) for l in open(sys.argv[1])]
sz = json.load(open(sys.argv[2]))
cards = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
print('NHATS objects queried at MPC (no SBDB diameter, brightest first + named examples):', len(rows), '| with C51 astrometry:', sum(1 for r in rows if r.get('n_c51')))
print('%-11s %5s %5s %4s %-28s %-44s %-12s %s' % ('object', 'H', 'dv', 'nC51', 'C51 years', 'published NEOWISE fit (D km, table)', 'Spitzer D', 'ssoCard diameter (method; refs)'))
cat = collections.Counter()
for r in rows:
    if not r.get('n_c51'):
        continue
    o = sz[r['des']]
    nw = o.get('neowise')
    sp = o.get('spitzer')
    cd = (cards.get(r['des']) or {}).get('diameter')
    yrs = sorted(r['c51_years'])
    last = max(int(y) for y in yrs)
    if nw:
        k = 'published NEOWISE fit exists, absent from SBDB'
    elif last >= 2021:
        k = 'no published fit; has C51 data from 2021 or later (after year 7)'
    elif r['n_c51'] < 5:
        k = 'no published fit; fewer than 5 C51 detections'
    else:
        k = 'no published fit; >=5 detections all before 2021'
    cat[k] += 1
    print('%-11s %5.2f %5.2f %4d %-28s %-44s %-12s %s' % (r['des'], r['H'], r['dv'], r['n_c51'], ','.join('%s:%d' % (y, r['c51_years'][y]) for y in yrs),
          ';'.join('%s(%s)' % (x[0], x[1]) for x in nw) if nw else '-', ';'.join('%g' % x[0] for x in sp) if sp else '-',
          '%s (%s; %s)' % (cd['value'], ','.join(cd['methods']), ','.join(cd['refs'])) if cd else ('-' if r['des'] in cards else 'no card')))
print()
for k, v in cat.most_common():
    print('%3d  %s' % (v, k))

# SBDB completeness versus published NEOWISE tables
allp = list(sz)
nw_all = [p for p in allp if sz[p].get('neowise')]
nw_nh = [p for p in nw_all if sz[p]['nhats']]
print('\nNEAs with a published NEOWISE fit (cryo..year 7 + manually recovered):', len(nw_all), '| of these with an SBDB diameter:', sum(1 for p in nw_all if sz[p].get('sbdb')),
      '| without:', sum(1 for p in nw_all if not sz[p].get('sbdb')))
print('NHATS with a published NEOWISE fit:', len(nw_nh), '| with SBDB diameter:', sum(1 for p in nw_nh if sz[p].get('sbdb')), '| without:', sum(1 for p in nw_nh if not sz[p].get('sbdb')))
bytag = collections.Counter()
bytag_sb = collections.Counter()
for p in nw_all:
    tags = {t for _, t in sz[p]['neowise']}
    for t in tags:
        bytag[t] += 1
        if sz[p].get('sbdb'):
            bytag_sb[t] += 1
print('per table: NEAs in table / of which have an SBDB diameter')
for t in ('Mai11', 'Mai12', 'Mai14', 'Nug15', 'Nug16', 'Mas17', 'Mas18', 'Mas20y4', 'Mas20y5', 'Mas20b', 'Mas21y6', 'Mas21y7'):
    print('  %-8s %5d %5d  (%.0f%%)' % (t, bytag[t], bytag_sb[t], 100.0 * bytag_sb[t] / max(1, bytag[t])))
only_late = [p for p in nw_all if all(t.startswith('Mas20') or t.startswith('Mas21') for _, t in sz[p]['neowise'])]
print('NEAs whose only NEOWISE fits are in the 2020-2021 papers:', len(only_late), '| with SBDB diameter:', sum(1 for p in only_late if sz[p].get('sbdb')))
sp_all = [p for p in allp if sz[p].get('spitzer')]
print('NEAs with a Spitzer diameter:', len(sp_all), '| with SBDB diameter:', sum(1 for p in sp_all if sz[p].get('sbdb')),
      '| NHATS:', sum(1 for p in sp_all if sz[p]['nhats']), 'with SBDB diameter', sum(1 for p in sp_all if sz[p]['nhats'] and sz[p].get('sbdb')))
print('NHATS without SBDB diameter but with a published NEOWISE fit:', sorted(p for p in nw_nh if not sz[p].get('sbdb')))
