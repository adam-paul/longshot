#!/usr/bin/env python3
"""Build the largest labelled NEA set from today's snapshots (no source-region model involved).

Usage: pn_build.py <sbdb_neo.json> <nhats.json> <download_dir> <out_csv>

download_dir must contain  spitzer/spitzerneos.csv  and  vizier/*.tsv  (CfA VizieR asu-tsv dumps).
Output: one row per near-Earth ASTEROID with at least one label (albedo and/or taxonomy), with orbital elements,
H, NHATS membership, every source's raw value, and the combined labels used by pn_cv.py.
"""
import sys, os, re, json, csv, math, collections

sbdb_fn, nhats_fn, DL, out_csv = sys.argv[1:5]
V = os.path.join(DL, 'vizier')

def norm(s):
    return re.sub(r'[\s_]+', '', s.lower()) if s else None

# ---------------------------------------------------------------- MPC packed designations
B62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
def unpack(p):
    """MPC packed number or provisional designation -> SBDB-style primary designation, or None."""
    p = p.strip()
    if re.fullmatch(r'\d{5}', p): return str(int(p))
    if re.fullmatch(r'[A-Za-z]\d{4}', p): return str(B62.index(p[0]) * 10000 + int(p[1:]))
    if re.fullmatch(r'~[0-9A-Za-z]{4}', p):
        n = 0
        for ch in p[1:]: n = n * 62 + B62.index(ch)
        return str(620000 + n)
    m = re.fullmatch(r'([IJK])(\d\d)([A-Z])([0-9A-Za-z])(\d)([A-Z])', p)
    if m:
        yr = {'I': 1800, 'J': 1900, 'K': 2000}[m.group(1)] + int(m.group(2))
        cyc = B62.index(m.group(4)) * 10 + int(m.group(5))
        return '%d %s%s%s' % (yr, m.group(3), m.group(6), str(cyc) if cyc else '')
    return None

# ---------------------------------------------------------------- SBDB elements
sb = json.load(open(sbdb_fn)); F = sb['fields']
obj = {}; key2pdes = {}; AJ = 5.2044; n_comet = 0; n_noel = 0
for r in sb['data']:
    d = dict(zip(F, r))
    if not (d['kind'] or '').startswith('a'): n_comet += 1; continue
    try: a, e, i, q = float(d['a']), float(d['e']), float(d['i']), float(d['q'])
    except (TypeError, ValueError): n_noel += 1; continue
    if not (0 <= e < 1 and a > 0): n_noel += 1; continue
    fl = lambda k: float(d[k]) if d[k] not in (None, '') else None
    tj = AJ / a + 2 * math.cos(math.radians(i)) * math.sqrt(a / AJ * (1 - e * e))
    obj[d['pdes']] = dict(pdes=d['pdes'], a=a, e=e, i=i, q=q, tj=tj, tj_sbdb=fl('t_jup'), moid=fl('moid'), H=fl('H'),
                          sbdb_albedo=fl('albedo'), spec_B=d['spec_B'], spec_T=d['spec_T'], cls=d['class'],
                          arc=fl('data_arc'), cc=d['condition_code'])
    ks = {d['pdes'] if d['pdes'].isdigit() else norm(d['pdes'])}
    if d['name']: ks.add(norm(d['name']))
    m = re.search(r'\(([^)]+)\)', d['full_name'] or '')
    if m: ks.add(norm(m.group(1)))
    for kk in ks: key2pdes.setdefault(kk, d['pdes'])
print('SBDB near-Earth asteroids with elements:', len(obj), '| comets skipped:', n_comet, '| unusable elements:', n_noel)

def match(*vals):
    for v in vals:
        v = (str(v) if v is not None else '').strip()
        if not v or v in ('-', 'nan', 'None', '0'): continue
        cands = [v, v.lstrip('0')]
        u = unpack(v)
        if u: cands.insert(0, u)
        m = re.match(r'^\(?(\d+)\)?\s+(.*)$', v)
        if m and not re.match(r'^\d{4}\s+[A-Z]{2}\d*$', v): cands += [m.group(1), m.group(2)]
        m = re.match(r'^(\d{4})\s*([A-Z]{2}\d*)$', v)
        if m: cands.append(m.group(1) + ' ' + m.group(2))
        if re.match(r'^\d+\.0$', v): cands.append(v[:-2])
        if '|' in v: cands += [x.strip() for x in v.split('|')]
        for c in cands:
            if not c: continue
            k = c if c.isdigit() else norm(c)
            if k in key2pdes: return key2pdes[k]
    return None

nh = json.load(open(nhats_fn))['data']
dv = {o['des']: float(o['min_dv']['dv']) for o in nh}
print('NHATS objects:', len(dv), '| found in SBDB NEA table:', sum(1 for d in dv if d in obj))

# ---------------------------------------------------------------- class mapping
def coarse(cls):
    """Return (tax4, sq): tax4 in {'S','C','X','O',None}; sq in {1,0,None}. None = no usable label.
    S = S- and Q-types; C = C/B/F/G; X = X/E/M/P; O = everything else with a definite class (A, D, K, L, O, R, T, V, Z)."""
    if cls is None: return None, None
    s = cls.strip().replace(':', '').strip()
    if not s or s in ('U', '-', '?', 'No_Taxo', 'none'): return None, None
    if s in ('S_comp', 'S-complex'): return 'S', 1
    if s == 'C-complex': return 'C', 0
    if s == 'X-complex': return 'X', 0
    parts = [p.strip() for p in re.split(r'[;/,.]', s) if p.strip()]
    if s in ('CX', 'XC'): parts = ['C', 'X']
    labs = set()
    for p in parts:
        c = p[0]
        if c in 'SQ': labs.add('S')
        elif c in 'CBFG': labs.add('C')
        elif c in 'XEMP': labs.add('X')
        elif c in 'ADKLORTVZ': labs.add('O')
        else: labs.add('?')
    if '?' in labs: return None, None
    if len(labs) == 1:
        l = labs.pop(); return l, (1 if l == 'S' else 0)
    if 'S' not in labs: return None, 0          # e.g. 'C;X': ambiguous among four classes, certainly not S/Q
    return None, None

def parse_vizier(fn):
    tables = {}; name = None; state = 0
    if not os.path.exists(fn): return tables
    for line in open(fn, errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#Name:'): name = line.split(':', 1)[1].strip(); state = 0; continue
        if line.startswith('#') or not line.strip(): continue
        if name is None: continue
        if state == 0: tables[name] = {'cols': [c.strip() for c in line.split('\t')], 'rows': []}; state = 1
        elif state == 1: state = 2
        elif state == 2: state = 3
        else: tables[name]['rows'].append([c.strip() for c in line.split('\t')])
    return tables
def rows_of(t):
    for r in t['rows']: yield dict(zip(t['cols'], r))
def table(fn, name):
    T = parse_vizier(os.path.join(V, fn))
    if name not in T: print('  !! missing table', name, 'in', fn); return {'cols': [], 'rows': []}
    return T[name]
def fnum(x):
    try: return float(x)
    except (TypeError, ValueError): return None

albs = collections.defaultdict(lambda: collections.defaultdict(list))   # pdes -> source -> [values]
tax = collections.defaultdict(dict)                                     # pdes -> source -> (raw, tax4, sq)
stats = collections.OrderedDict(); unmatched = {}

# ---------------------------------------------------------------- SBDB labels
for p, o in obj.items():
    if o['sbdb_albedo'] is not None and o['sbdb_albedo'] > 0: albs[p]['sbdb'].append(o['sbdb_albedo'])
    for key in ('spec_B', 'spec_T'):
        if o[key]:
            t4, sq = coarse(o[key])
            if t4 or sq is not None: tax[p].setdefault('sbdb', (o[key], t4, sq))

# ---------------------------------------------------------------- Spitzer (Trilling+ 2010, 2016; ExploreNEOs, NEOSurvey, NEOLegacy)
n_un = 0
for r in csv.DictReader(open(os.path.join(DL, 'spitzer', 'spitzerneos.csv'))):
    p = match(r['number'], r['desig'], r['name'])
    if p is None: n_un += 1; continue
    pv = fnum(r['pv'])
    if pv and pv > 0: albs[p]['spitzer'].append(pv)
unmatched['spitzer'] = n_un

# ---------------------------------------------------------------- NEOWISE team fits (thermal models), one source family
def add_neowise(fn, name, idcols, col, log=False, tag=None):
    n_un = 0; n = 0
    for r in rows_of(table(fn, name)):
        p = match(*[r.get(c) for c in idcols])
        if p is None: n_un += 1; continue
        v = fnum(r.get(col))
        if v is None: continue
        if log: v = 10 ** v
        if 0 < v < 1.5: albs[p]['neowise'].append(v); albs[p]['nw_' + tag].append(v); n += 1
    unmatched[tag] = n_un; return n
add_neowise('J_ApJ_743_156.tsv', 'J/ApJ/743/156/table1', ['MPC', 'Name'], 'pV', tag='mainzer2011')
add_neowise('J_ApJ_760_L12.tsv', 'J/ApJ/760/L12/table1', ['MPC', 'Name'], 'pV', tag='mainzer2012')
add_neowise('J_ApJ_784_110.tsv', 'J/ApJ/784/110/table2', ['Name', 'OName'], 'pV', tag='mainzer2014a')
add_neowise('J_ApJ_792_30.tsv', 'J/ApJ/792/30/table2', ['Name', 'OName'], 'pV', tag='mainzer2014b')
add_neowise('J_ApJ_814_117.tsv', 'J/ApJ/814/117/nea', ['MPC', 'Name'], 'pV', tag='nugent2015')
add_neowise('J_AJ_152_63.tsv', 'J/AJ/152/63/asteroids', ['MPC', 'Name'], 'pV', tag='nugent2016')
add_neowise('J_AJ_154_168.tsv', 'J/AJ/154/168/table1', ['Name'], 'logpV', log=True, tag='masiero2017')
add_neowise('J_AJ_156_60.tsv', 'J/AJ/156/60/table1', ['Name'], 'logpV', log=True, tag='masiero2018')

# ---------------------------------------------------------------- taxonomy tables
# Mahlke+2022: classes from spectra (+albedo where known), aggregated per asteroid
n_un = 0
for r in rows_of(table('J_A_A_665_A26.tsv', 'J/A+A/665/A26/asteroid')):
    p = match(r['Number'], r['Name'])
    if p is None: n_un += 1; continue
    t4, sq = coarse(r['classsf'])
    if t4 or sq is not None: tax[p]['mahlke'] = (r['class'], t4, sq)
# Marsset+2022 MITHNEOS NIR spectra; several spectra per object -> majority of usable labels, first on ties
tmp = collections.defaultdict(list)
for r in rows_of(table('J_AJ_163_165.tsv', 'J/AJ/163/165/table7')):
    p = match(r['Number'], r['Desig'], r['Name'])
    if p is None: continue
    t4, sq = coarse(r['Taxon'])
    if t4 or sq is not None: tmp[p].append((r['Taxon'], t4, sq))
for p, lst in tmp.items():
    c = collections.Counter((t4, sq) for _, t4, sq in lst); best = c.most_common(1)[0][0]
    tax[p]['marsset'] = next(x for x in lst if (x[1], x[2]) == best)
# Devogele+2019 MANOS visible spectra
for r in rows_of(table('J_AJ_158_196.tsv', 'J/AJ/158/196/table5')):
    p = match(r['ID'])
    if p is None: continue
    t4, sq = coarse(r['Taxon'])
    if t4 or sq is not None: tax[p]['devogele'] = (r['Taxon'], t4, sq)
# Perna+2016 PHA taxonomy (spectra, own + literature); albedo column is literature
for r in rows_of(table('J_AJ_151_11.tsv', 'J/AJ/151/11/table4')):
    p = match(r['Name'])
    if p is None: continue
    t4, sq = coarse(r['Type'])
    if t4 or sq is not None: tax[p]['perna16'] = (r['Type'], t4, sq)
    v = fnum(r['Alb'])
    if v and v > 0: albs[p]['perna16'].append(v)
# Ieva+2020 compilation (NEOShield-2 photometric survey + literature). Its Albedo column is a class average, NOT a measurement: not used.
for r in rows_of(table('J_A_A_644_A23.tsv', 'J/A+A/644/A23/tablea1')):
    p = match(r['Name'])
    if p is None: continue
    t4, sq = coarse(r['Taxon'])
    if t4 or sq is not None: tax[p]['ieva20'] = (r['Taxon'] + '|' + r['survey'], t4, sq)
# Deshapriya+2023 NEO data set (compiled taxonomy and albedo)
for r in rows_of(table('J_A_A_674_A50.tsv', 'J/A+A/674/A50/dataset')):
    p = match(r['Number'], r['Design'], r['Name'])
    if p is None: continue
    t4, sq = coarse(r['Taxo'])
    if t4 or sq is not None: tax[p]['deshapriya23'] = (r['Taxo'], t4, sq)
    v = fnum(r['Albedo'])
    if v and 0 < v < 1.5: albs[p]['deshapriya23'].append(v)
# Sergeyev+2023 colour-based complexes (SDSS / SkyMapper / Gaia) and compiled albedo
serg_p = {}
for r in rows_of(table('J_A_A_679_A148.tsv', 'J/A+A/679/A148/catalog')):
    p = match(r['Number'], r['Design'], r['Name'])
    if p is None: continue
    pc = fnum(r['pComplex'])
    t4, sq = coarse(r['Complex'])
    if t4 or sq is not None:
        tax[p]['sergeyev'] = (r['Complex'] + '|' + r['TMethod'], t4, sq); serg_p[p] = pc if pc is not None else float('nan')
    v = fnum(r['Albedo'])
    if v and v > 0: albs[p]['sergeyev'].append(v)
# Tinaut-Ruano+2026 Gaia DR3 reflectance-spectrum classes (Tholen-like letters)
for r in rows_of(table('J_A_A_711_A167.tsv', 'J/A+A/711/A167/class')):
    if not r.get('Tax'): continue
    p = match(r['MPC'])
    if p is None: continue
    t4, sq = coarse(r['Tax'])
    if t4 or sq is not None: tax[p]['gaia26'] = (r['Tax'], t4, sq)
# Popescu+2018 MOVIS near-infrared colours (final class)
for r in rows_of(table('J_A_A_617_A12.tsv', 'J/A+A/617/A12/movistax')):
    if not r.get('ClassFin') or r['ClassFin'] == 'U': continue
    p = match(r['Number'], *r['Names'].split('|'))
    if p is None: continue
    t4, sq = coarse(r['ClassFin'])
    if t4 or sq is not None: tax[p]['movis'] = (r['ClassFin'], t4, sq)
# Erasmus+2017 KMTNet VRI colours: class probabilities; keep when the top class has P >= 0.6
for r in rows_of(table('J_AJ_154_162.tsv', 'J/AJ/154/162/table1')):
    p = match(r['ID'])
    if p is None: continue
    pr = {k: fnum(r['Prob-' + k]) or 0.0 for k in 'SXCD'}; top = max(pr, key=pr.get)
    if pr[top] >= 0.6:
        t4 = {'S': 'S', 'X': 'X', 'C': 'C', 'D': 'O'}[top]; tax[p]['erasmus17'] = ('%s=%.2f' % (top, pr[top]), t4, 1 if t4 == 'S' else 0)
# Navarro-Meza+2024 RATIR: only S/Q-versus-not is recoverable (C and X are merged)
TT = parse_vizier(os.path.join(V, 'J_AJ_167_163.tsv'))
for name in ('J/AJ/167/163/table4', 'J/AJ/167/163/table5'):
    for r in rows_of(TT.get(name, {'cols': [], 'rows': []})):
        p = match(r['ID'])
        if p is None: continue
        a_, b_ = fnum(r['P(S)']), fnum(r['P(Q)'])
        if a_ is None or b_ is None: continue
        ps = a_ + b_; sq = 1 if ps >= 70 else (0 if ps <= 30 else None)
        if sq is not None: tax[p]['ratir'] = ('S+Q=%d%%' % ps, None, sq)

gm = lambda v: math.exp(sum(math.log(x) for x in v) / len(v))
# Deshapriya+2023 albedos are NOT used as labels: where no measurement exists that table carries a class-average value
# (0.26 for S, 0.049 for C, 0.105 for X ...: 9 distinct values among 458 objects), i.e. taxonomy in disguise.
ALB_SRC = ['neowise', 'sbdb', 'spitzer', 'sergeyev', 'perna16']
ALB_AUDIT = ['deshapriya23']
TAX_ORDER = ['mahlke', 'marsset', 'devogele', 'perna16', 'sbdb', 'ieva20', 'deshapriya23', 'gaia26', 'sergeyev', 'erasmus17', 'movis', 'ratir']
SPEC = {'mahlke', 'marsset', 'devogele', 'perna16', 'sbdb'}
print('\nper-source matched NEAs:')
for s in ALB_SRC + ALB_AUDIT + sorted({k for p in albs for k in albs[p] if k.startswith('nw_')}):
    print('  albedo   %-16s %6d' % (s, sum(1 for p in albs if s in albs[p])))
for s in TAX_ORDER:
    print('  taxonomy %-16s %6d  (4-class usable %d)' % (s, sum(1 for p in tax if s in tax[p]), sum(1 for p in tax if s in tax[p] and tax[p][s][1])))
print('unmatched rows (not NEAs in SBDB, or unparsed names):', unmatched)

# ---------------------------------------------------------------- combine
rows = []; conf = collections.Counter()
for p in sorted(set(albs) | set(tax)):
    o = obj[p]
    if o['H'] is None or o['moid'] is None: conf['dropped_missing_H_or_moid'] += 1; continue
    r = dict(pdes=p, a=o['a'], e=o['e'], i=o['i'], q=o['q'], tj=round(o['tj'], 5), moid=o['moid'], H=o['H'], orbclass=o['cls'],
             nhats=int(p in dv), min_dv=dv.get(p, ''))
    A = {k: gm(v) for k, v in albs.get(p, {}).items()}
    main = [k for k in ALB_SRC if k in A]
    if main:
        src = main[0]; vals = [A[k] for k in main]
        r.update(alb=round(A[src], 4), alb_src=src, alb_n=len(main), alb_min=round(min(vals), 4), alb_max=round(max(vals), 4),
                 alb_neowise=round(A['neowise'], 4) if 'neowise' in A else '', alb_spitzer=round(A['spitzer'], 4) if 'spitzer' in A else '',
                 alb_sbdb=A.get('sbdb', ''), alb_srcs='|'.join('%s=%.3f' % (k, A[k]) for k in main))
        if (min(vals) < 0.10) != (max(vals) < 0.10): conf['albedo_sources_straddle_0.10'] += 1
    else:
        r.update(alb='', alb_src='', alb_n=0, alb_min='', alb_max='', alb_neowise='', alb_spitzer='', alb_sbdb='', alb_srcs='')
    Tx = tax.get(p, {})
    t4 = sq = None; t4src = sqsrc = ''
    for k in TAX_ORDER:
        if k in Tx and Tx[k][1] and t4 is None: t4, t4src = Tx[k][1], k
        if k in Tx and Tx[k][2] is not None and sq is None: sq, sqsrc = Tx[k][2], k
    l4 = {v[1] for v in Tx.values() if v[1]}
    if len(l4) > 1: conf['tax4_sources_disagree'] += 1
    if len(Tx) > 1 and len(l4) >= 1: conf['tax4_multi_source'] += 1
    r.update(tax4=t4 or '', tax4_src=t4src, tax4_spec=int(t4src in SPEC) if t4 else '', tax4_agree=int(len(l4) <= 1) if t4 else '',
             tax4_nsrc=sum(1 for v in Tx.values() if v[1]),
             sq='' if sq is None else sq, sq_src=sqsrc,
             tax_all='|'.join('%s=%s' % (k, Tx[k][0]) for k in TAX_ORDER if k in Tx),
             serg_p='%.2f' % serg_p[p] if p in serg_p and serg_p[p] == serg_p[p] else '')
    if r['alb'] == '' and not t4 and sq is None: continue
    rows.append(r)
print('\nconflicts / drops:', dict(conf))
cols = list(rows[0].keys())
with open(out_csv, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

def cnt(sel, name):
    sel = list(sel)
    na = sum(1 for r in sel if r['alb'] != ''); nd = sum(1 for r in sel if r['alb'] != '' and r['alb'] < 0.10)
    c4 = collections.Counter(r['tax4'] for r in sel if r['tax4']); nsq = sum(1 for r in sel if r['sq'] != ''); n1 = sum(1 for r in sel if r['sq'] == 1)
    hs = sorted(r['H'] for r in sel)
    print('%-28s n=%5d Hmed=%4.1f | albedo n=%5d dark=%5d (%4.1f%%) | tax4 n=%5d %s | S/Q-vs-rest n=%5d S/Q=%5d' % (
        name, len(sel), hs[len(hs) // 2] if hs else float('nan'), na, nd, 100 * nd / max(na, 1), sum(c4.values()), dict(sorted(c4.items())), nsq, n1))
print()
cnt(rows, 'all NEAs')
cnt((r for r in rows if r['a'] < 2), 'a < 2 au')
cnt((r for r in rows if r['nhats']), 'NHATS members')
cnt((r for r in rows if r['nhats'] and r['min_dv'] < 6), 'NHATS dv < 6')
cnt((r for r in rows if r['nhats'] and r['min_dv'] < 5), 'NHATS dv < 5')
cnt((r for r in rows if 0.8 <= r['a'] <= 1.3 and r['e'] < 0.3 and r['i'] < 10), 'NHATS-like box')
cnt((r for r in rows if r['H'] >= 24), 'H >= 24')
print('\nalbedo label source:', collections.Counter(r['alb_src'] for r in rows if r['alb'] != ''))
print('tax4 label source:', collections.Counter(r['tax4_src'] for r in rows if r['tax4']))
print('sq label source:', collections.Counter(r['sq_src'] for r in rows if r['sq'] != ''))
print('rows written:', len(rows), '->', out_csv)
