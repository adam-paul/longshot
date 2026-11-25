"""Item 1 final: albedo-independent sizes for NHATS objects, combining local tables (cx_sizes.py output) with ssoCard
diameter methods (cx_cards.py output).
Usage: python3 -I cx_sizes2.py <sizes_local.json> <cards_flags.json> <out_tsv>
Size classes: thermal (Spitzer table, NEOWISE tables, ssoCard NEATM/TPM/STM/FRM), radar (ssoCard Radar*), spacecraft
(ssoCard SPACE), occultation (ssoCard Occ*), sbdb_only (SBDB diameter with no other evidence; method unknown)."""
import sys, json, collections

sz = json.load(open(sys.argv[1]))
cards = json.load(open(sys.argv[2]))
OUT = sys.argv[3]
THERM = ('NEATM', 'TPM', 'STM', 'FRM', 'NESTM', 'LC+TPM', 'LC-TPM')


def classes(p):
    o = sz[p]
    c = cards.get(p, {})
    cl = set()
    if o.get('spitzer'):
        cl.add('thermal:Spitzer')
    if o.get('neowise'):
        cl.add('thermal:NEOWISE')
    d = c.get('diameter')
    if d:
        for m in d['methods']:
            if m in THERM:
                cl.add('thermal:card')
            elif m.lower().startswith('radar'):
                cl.add('radar:card')
            elif m == 'SPACE':
                cl.add('spacecraft:card')
            elif 'occ' in m.lower():
                cl.add('occultation:card')
            else:
                cl.add('other:card:' + m)
    if o.get('sbdb') and not cl:
        cl.add('sbdb_only')
    return cl


nh = [p for p, o in sz.items() if o['nhats']]
have_card = set(cards)
rows = []
for p in nh:
    rows.append((p, classes(p)))
C = dict(rows)


def sig(o, k):
    v, s = o.get(k + '_val'), o.get(k + '_sig')
    return abs(v) / s if v is not None and s else None


scopes = [('all NHATS', lambda o: True), ('dv<6', lambda o: o['dv'] < 6), ('dv<5', lambda o: o['dv'] < 5),
          ('A1|A2', lambda o: o['A1'] or o['A2']), ('A2', lambda o: o['A2']), ('A1', lambda o: o['A1']),
          ('A2 >=3sig', lambda o: o['A2'] and (sig(o, 'A2') or 0) >= 3), ('A1 >=3sig', lambda o: o['A1'] and (sig(o, 'A1') or 0) >= 3),
          ('A1|A2, dv<6', lambda o: (o['A1'] or o['A2']) and o['dv'] < 6), ('A1|A2, dv<5', lambda o: (o['A1'] or o['A2']) and o['dv'] < 5)]
defs = [('thermal IR (Spitzer|NEOWISE|card thermal)', lambda c: any(x.startswith('thermal') for x in c)),
        ('  Spitzer table', lambda c: 'thermal:Spitzer' in c), ('  NEOWISE tables (cryo..year 7)', lambda c: 'thermal:NEOWISE' in c),
        ('  ssoCard thermal method', lambda c: 'thermal:card' in c),
        ('radar size (ssoCard)', lambda c: 'radar:card' in c), ('spacecraft size (ssoCard)', lambda c: 'spacecraft:card' in c),
        ('occultation size (ssoCard)', lambda c: 'occultation:card' in c),
        ('SBDB diameter with no other evidence', lambda c: 'sbdb_only' in c),
        ('ANY albedo-independent size (excl. sbdb_only)', lambda c: any(not x.startswith('sbdb_only') and not x.startswith('other') for x in c)),
        ('ANY incl. sbdb_only', lambda c: len(c) > 0)]
print('NHATS', len(nh), '| cards available for', sum(1 for p in nh if p in have_card))
print('%-48s' % '' + ''.join('%13s' % n for n, _ in scopes))
print('%-48s' % 'N in scope' + ''.join('%13d' % sum(1 for p in nh if f(sz[p])) for _, f in scopes))
print('%-48s' % 'N in scope with a card fetched' + ''.join('%13d' % sum(1 for p in nh if f(sz[p]) and p in have_card) for _, f in scopes))
for lab, d in defs:
    print('%-48s' % lab + ''.join('%13d' % sum(1 for p in nh if f(sz[p]) and d(C[p])) for _, f in scopes))

good = lambda c: any(not x.startswith('sbdb_only') and not x.startswith('other') for x in c)
print('\nNHATS with A1|A2 by H bin: N / with albedo-independent size')
for lo, hi in ((-99, 22), (22, 25), (25, 28), (28, 99)):
    a = [p for p in nh if (sz[p]['A1'] or sz[p]['A2']) and sz[p]['H'] is not None and lo <= sz[p]['H'] < hi]
    print('   H %4s..%-4s  %3d / %3d   %s' % (lo, hi, len(a), sum(1 for p in a if good(C[p])), [p for p in a if good(C[p])] if hi > 25 else ''))
print('all NHATS by H bin: N / with albedo-independent size (lower bound outside the carded sets)')
for lo, hi in ((-99, 22), (22, 25), (25, 28), (28, 99)):
    a = [p for p in nh if sz[p]['H'] is not None and lo <= sz[p]['H'] < hi]
    print('   H %4s..%-4s  %4d / %3d' % (lo, hi, len(a), sum(1 for p in a if good(C[p]))))

with open(OUT, 'w') as f:
    f.write('des\tname\tdv\tH\tA1\tA1_snr\tA2\tA2_snr\tsize_classes\tsbdb_D_km\tspitzer_D_km\tneowise_D_km\tcard_D_km\tcard_methods\tcard_refs\tradar_astrom\n')
    for p in sorted(nh, key=lambda p: sz[p]['dv']):
        o = sz[p]
        if not (o['A1'] or o['A2'] or C[p]):
            continue
        c = cards.get(p, {}).get('diameter') or {}
        f.write('\t'.join(str(x) for x in (
            p, o['name'] or '', o['dv'], o['H'], o['A1_val'], '%.1f' % sig(o, 'A1') if sig(o, 'A1') else '', o['A2_val'], '%.1f' % sig(o, 'A2') if sig(o, 'A2') else '',
            ','.join(sorted(C[p])), o['sbdb'][0] if o['sbdb'] else '', ';'.join('%g' % x[0] for x in o['spitzer']) if o['spitzer'] else '',
            ';'.join('%s(%s)' % (x[0], x[1]) for x in o['neowise']) if o['neowise'] else '', c.get('value', ''), ','.join(c.get('methods', [])), ','.join(c.get('refs', [])),
            o['radar_astrom'] or '')) + '\n')

print('\n--- NHATS A1|A2 objects WITHOUT any albedo-independent size, delta-v < 7:')
for p in sorted(nh, key=lambda p: sz[p]['dv']):
    o = sz[p]
    if (o['A1'] or o['A2']) and not any(not x.startswith('sbdb_only') and not x.startswith('other') for x in C[p]) and o['dv'] < 7:
        print('  %-11s dv=%.2f H=%.1f A1snr=%s A2snr=%s arc=%s radar=%s %s card=%s' % (p, o['dv'], o['H'], '%.1f' % sig(o, 'A1') if sig(o, 'A1') else '-',
              '%.1f' % sig(o, 'A2') if sig(o, 'A2') else '-', o['data_arc'], o['radar_astrom'], sorted(C[p]), 'y' if p in have_card else 'n'))
print('\n--- NHATS A1|A2 objects WITH radar/spacecraft/SBDB-only sizes, and all sized objects with dv<6.5:')
for p in sorted(nh, key=lambda p: sz[p]['dv']):
    o = sz[p]
    c = cards.get(p, {}).get('diameter') or {}
    if ((o['A1'] or o['A2']) and any(x.split(':')[0] in ('radar', 'spacecraft', 'sbdb_only', 'occultation', 'other') for x in C[p])) or (C[p] and o['dv'] < 6.5):
        print('  %-11s %-9s dv=%.2f H=%.1f A1=%s A2=%s %s sbdb=%s spitzer=%s neowise=%s card=%s %s %s' % (p, o['name'] or '', o['dv'], o['H'], 'y' if o['A1'] else '-', 'y' if o['A2'] else '-',
              sorted(C[p]), o['sbdb'][0] if o['sbdb'] else None, [x[0] for x in o['spitzer']] if o['spitzer'] else None,
              [x[0] for x in o['neowise']] if o['neowise'] else None, c.get('value'), c.get('methods'), c.get('refs')))
# sizes known only to SsODNet cards (not in my tables) and vice versa, within carded objects
co = [p for p in nh if p in have_card and cards[p].get('diameter') and not sz[p]['spitzer'] and not sz[p]['neowise']]
print('\ncard diameter but not in Spitzer/NEOWISE tables:', len(co), [(p, cards[p]['diameter']['methods'], cards[p]['diameter']['refs']) for p in co][:40])
to = [p for p in nh if p in have_card and not cards[p].get('diameter') and (sz[p]['spitzer'] or sz[p]['neowise'])]
print('in Spitzer/NEOWISE tables but no card diameter:', len(to), '| of which Spitzer-only', sum(1 for p in to if sz[p]['spitzer'] and not sz[p]['neowise']),
      '| NEOWISE', [(p, sz[p]['neowise']) for p in to if sz[p]['neowise']][:12])
