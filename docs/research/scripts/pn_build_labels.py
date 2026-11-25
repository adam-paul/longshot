#!/usr/bin/env python3
"""Build the largest labelled NEA set available from local snapshots (no source-region model involved).

Usage: pn_build_labels.py <research_root> <out_csv> [extra_dir]

research_root is the unpacked research archive, data/research under the repository root.
Reads (read-only), relative to research_root:
  downloads/source-prior/jpl/sbdb_neo.json   a,e,i,q,H,moid,albedo,spec_B,spec_T for all NEOs
  dl/catalogs/sbdb_neo.json                  kind (asteroid/comet)
  dl/catalogs/nhats.json                     NHATS membership and min delta-v
  dl/catalogs/spitzerneos.csv                Spitzer albedos (Trilling+2010/2016)
  dl/catalogs/mp3c_nea_best.csv              MP3C best albedos
  dl/catalogs/vizier/*.tsv                   Mahlke+2022, Sergeyev+2023, Devogele+2019, Marsset+2022, Navarro-Meza+2024
  dl/catalogs/ssocards*, downloads/ground-truth/ssocard_nhats   SsODNet ssoCards
  [extra_dir]/*.tsv                          optional extra VizieR tables fetched by this checker
Output: one row per NEA with any label.
"""
import sys, os, re, json, csv, glob, math, collections

root, out_csv = sys.argv[1], sys.argv[2]
extra_dir = sys.argv[3] if len(sys.argv) > 3 else None
CAT = os.path.join(root, 'dl', 'catalogs')

def norm(s):
    return re.sub(r'[\s_]+', '', s.lower()) if s else None

# ---------------------------------------------------------------- SBDB elements
sb = json.load(open(os.path.join(root, 'downloads', 'source-prior', 'jpl', 'sbdb_neo.json')))
F = sb['fields']
kind = {}
sb2 = json.load(open(os.path.join(CAT, 'sbdb_neo.json'))); F2 = sb2['fields']
for r in sb2['data']:
    d = dict(zip(F2, r)); kind[d['pdes']] = (d['kind'], d.get('name'))
obj = {}
key2pdes = {}
AJ = 5.2044
n_comet = 0
for r in sb['data']:
    d = dict(zip(F, r))
    k = kind.get(d['pdes'], ('a?', None))
    if not k[0].startswith('a'):
        n_comet += 1; continue
    try:
        a, e, i, q = float(d['a']), float(d['e']), float(d['i']), float(d['q'])
    except (TypeError, ValueError):
        continue
    H = float(d['H']) if d['H'] not in (None, '') else None
    moid = float(d['moid']) if d['moid'] not in (None, '') else None
    tj = AJ / a + 2 * math.cos(math.radians(i)) * math.sqrt(a / AJ * (1 - e * e)) if 0 < e < 1 and a > 0 else None
    obj[d['pdes']] = dict(pdes=d['pdes'], a=a, e=e, i=i, q=q, tj=tj, moid=moid, H=H,
                          sbdb_albedo=float(d['albedo']) if d['albedo'] not in (None, '') else None,
                          spec_B=d['spec_B'], spec_T=d['spec_T'])
    ks = {d['pdes'] if d['pdes'].isdigit() else norm(d['pdes'])}
    if k[1]: ks.add(norm(k[1]))
    m = re.search(r'\(([^)]+)\)', d['full_name'] or '')
    if m: ks.add(norm(m.group(1)))
    for kk in ks: key2pdes.setdefault(kk, d['pdes'])
print('SBDB NEAs with elements:', len(obj), ' comets skipped:', n_comet)

def match(*vals):
    for v in vals:
        v = (str(v) if v is not None else '').strip()
        if not v or v in ('-', 'nan', 'None'): continue
        cands = [v, v.lstrip('0')]
        m = re.match(r'^\(?(\d+)\)?\s+(.*)$', v)
        if m: cands += [m.group(1), m.group(2)]
        m = re.match(r'^(\d{4})\s*([A-Z]{2}\d*)$', v)
        if m: cands.append(m.group(1) + ' ' + m.group(2))
        if re.match(r'^\d+\.0$', v): cands.append(v[:-2])
        for c in cands:
            k = c if c.isdigit() else norm(c)
            if k in key2pdes: return key2pdes[k]
    return None

nh = json.load(open(os.path.join(CAT, 'nhats.json')))['data']
dv = {o['des']: float(o['min_dv']['dv']) for o in nh}
print('NHATS objects:', len(dv), ' of which in SBDB NEA table:', sum(1 for d in dv if d in obj))

# ---------------------------------------------------------------- class mapping
def coarse(cls):
    """Return (tax4, sq) where tax4 in {'S','C','X','O',None} and sq in {1,0,None}. None = no usable label."""
    if cls is None: return None, None
    s = cls.strip().replace(':', '').strip()
    if not s or s in ('U', '-', '?'): return None, None
    if s in ('S_comp',): return 'S', 1
    parts = [p.strip() for p in re.split(r'[;/,]', s) if p.strip()]
    if s.upper() in ('CX', 'XC') and s in ('CX', 'XC'): parts = ['C', 'X']
    labs = set()
    for p in parts:
        u = p
        if u[0] in 'SQ': labs.add('S')
        elif u[0] in 'CBFG': labs.add('C')
        elif u[0] in 'XEMP': labs.add('X')
        elif u[0] in 'ADKLORTVZ': labs.add('O')
        else: labs.add('?')
    if '?' in labs: return None, None
    if len(labs) == 1:
        l = labs.pop(); return l, (1 if l == 'S' else 0)
    if 'S' not in labs: return None, 0          # e.g. 'C;X' -> ambiguous in 4 classes but certainly not S/Q
    return None, None

def parse_vizier(fn):
    tables = {}; name = None; state = 0
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
    for r in t['rows']:
        yield dict(zip(t['cols'], r))

alb = collections.defaultdict(dict)     # pdes -> {src: value}
tax = collections.defaultdict(dict)     # pdes -> {src: (raw, tax4, sq)}
stats = collections.OrderedDict()

# ---------------------------------------------------------------- SBDB labels
for p, o in obj.items():
    if o['sbdb_albedo'] is not None and o['sbdb_albedo'] > 0: alb[p]['sbdb'] = o['sbdb_albedo']
    for key in ('spec_B', 'spec_T'):
        if o[key]:
            t4, sq = coarse(o[key])
            if t4 or sq is not None:
                tax[p].setdefault('sbdb', (o[key], t4, sq))
stats['sbdb'] = (sum(1 for p in alb if 'sbdb' in alb[p]), sum(1 for p in tax if 'sbdb' in tax[p]))

# ---------------------------------------------------------------- Spitzer
sp = collections.defaultdict(list); n_un = 0
for r in csv.DictReader(open(os.path.join(CAT, 'spitzerneos.csv'))):
    p = match(r['number'], r['desig'], r['name'])
    if p is None: n_un += 1; continue
    try: pv = float(r['pv'])
    except ValueError: continue
    if pv > 0: sp[p].append(pv)
for p, v in sp.items():
    v = sorted(v); alb[p]['spitzer'] = math.exp(sum(math.log(x) for x in v) / len(v))
stats['spitzer'] = (len(sp), 0); print('Spitzer unmatched rows:', n_un)

# ---------------------------------------------------------------- MP3C
n_un = 0; n = 0
for r in csv.DictReader(open(os.path.join(CAT, 'mp3c_nea_best.csv'))):
    if not r.get('albedo'): continue
    nm = r['name']; m = re.match(r'^(\d{4})([A-Z]{2}\d*)$', nm or '')
    p = match(r['number'], (m.group(1) + ' ' + m.group(2)) if m else nm)
    if p is None: n_un += 1; continue
    try: v = float(r['albedo'])
    except ValueError: continue
    if v > 0: alb[p]['mp3c'] = v; n += 1
stats['mp3c'] = (n, 0); print('MP3C unmatched rows with albedo:', n_un)

# ---------------------------------------------------------------- VizieR tables
V = os.path.join(CAT, 'vizier')
# Mahlke+2022: spectra (+albedo) based classes, per asteroid
T = parse_vizier(os.path.join(V, 'J_A_A_665_A26.tsv'))['J/A+A/665/A26/asteroid']; n = 0
for r in rows_of(T):
    p = match(r['Number'], r['Name'])
    if p is None: continue
    t4, sq = coarse(r['classsf'])
    if t4 or sq is not None: tax[p]['mahlke'] = (r['class'], t4, sq); n += 1
stats['mahlke2022'] = (0, n)
# Marsset+2022 MITHNEOS NIR spectra; several spectra per object -> majority of usable labels, first on ties
T = parse_vizier(os.path.join(V, 'J_AJ_163_165.tsv'))['J/AJ/163/165/table7']; tmp = collections.defaultdict(list)
for r in rows_of(T):
    p = match(r['Number'], r['Desig'], r['Name'])
    if p is None: continue
    t4, sq = coarse(r['Taxon'])
    if t4 or sq is not None: tmp[p].append((r['Taxon'], t4, sq))
for p, lst in tmp.items():
    c = collections.Counter((t4, sq) for _, t4, sq in lst); best = c.most_common(1)[0][0]
    tax[p]['marsset'] = next(x for x in lst if (x[1], x[2]) == best)
stats['marsset2022'] = (0, len(tmp))
# Devogele+2019 MANOS visible spectra
T = parse_vizier(os.path.join(V, 'J_AJ_158_196.tsv'))['J/AJ/158/196/table5']; n = 0
for r in rows_of(T):
    p = match(r['ID'])
    if p is None: continue
    t4, sq = coarse(r['Taxon'])
    if t4 or sq is not None: tax[p]['devogele'] = (r['Taxon'], t4, sq); n += 1
stats['devogele2019'] = (0, n)
# Sergeyev+2023 colour-based complexes (NEA rows only are matched, since key2pdes only holds NEAs)
T = parse_vizier(os.path.join(V, 'J_A_A_679_A148.tsv'))['J/A+A/679/A148/catalog']; n = 0; na = 0
serg_p = {}
for r in rows_of(T):
    p = match(r['Number'], r['Design'], r['Name'])
    if p is None: continue
    try: pc = float(r['pComplex'])
    except ValueError: pc = float('nan')
    t4, sq = coarse(r['Complex'])
    if t4 or sq is not None:
        tax[p]['sergeyev'] = (r['Complex'], t4, sq); serg_p[p] = (pc, r['TMethod']); n += 1
    try:
        v = float(r['Albedo'])
        if v > 0: alb[p]['sergeyev'] = v; na += 1
    except ValueError: pass
stats['sergeyev2023'] = (na, n)
# Navarro-Meza+2024 RATIR: only S/Q-vs-not is recoverable (C and X are merged)
TT = parse_vizier(os.path.join(V, 'J_AJ_167_163.tsv')); n = 0
for name in ('J/AJ/167/163/table4', 'J/AJ/167/163/table5'):
    for r in rows_of(TT[name]):
        p = match(r['ID'])
        if p is None: continue
        try: ps = float(r['P(S)']) + float(r['P(Q)'])
        except ValueError: continue
        sq = 1 if ps >= 70 else (0 if ps <= 30 else None)
        if sq is not None: tax[p]['ratir'] = ('S+Q=%d%%' % ps, None, sq); n += 1
stats['navarro-meza2024'] = (0, n)

# ---------------------------------------------------------------- ssoCards
n_c = 0; seen = set()
for d in (os.path.join(CAT, 'ssocards'), os.path.join(CAT, 'ssocards_nea'), os.path.join(root, 'downloads', 'ground-truth', 'ssocard_nhats'), os.path.join(root, 'downloads', 'ground-truth', 'ssocard')):
    for fn in glob.glob(os.path.join(d, '*.json')):
        try: c = json.load(open(fn))
        except Exception: continue
        if not isinstance(c, dict) or not isinstance(c.get('parameters'), dict): continue
        p = match(c.get('number'), c.get('name'), (c.get('id') or '').replace('_', ' '))
        if p is None or p in seen: continue
        seen.add(p); n_c += 1
        ph = c['parameters'].get('physical') or {}
        t = ph.get('taxonomy') or {}
        if t.get('class'):
            t4, sq = coarse(t['class'])
            if t4 or sq is not None:
                tax[p]['ssocard_spec' if t.get('technique') == 'Spec' else 'ssocard_phot'] = (t['class'] + '|' + str(t.get('scheme')), t4, sq)
        a = ph.get('albedo') or {}
        if isinstance(a.get('value'), (int, float)) and a['value'] > 0: alb[p]['ssocard'] = float(a['value'])
stats['ssocards'] = (sum(1 for p in alb if 'ssocard' in alb[p]), sum(1 for p in tax if 'ssocard_spec' in tax[p] or 'ssocard_phot' in tax[p]))
print('distinct ssoCards matched to NEAs:', n_c)

# ---------------------------------------------------------------- optional extra tables (fetched by the checker)
if extra_dir and os.path.isdir(extra_dir):
    for fn in sorted(glob.glob(os.path.join(extra_dir, '*.tsv'))):
        for name, t in parse_vizier(fn).items():
            cols = t['cols']
            idc = [c for c in cols if re.match(r'^(Name|Num|Number|Desig|Design|Object|Asteroid|ID|MPC|NEO|Obj|PDes|Ast)', c, re.I)]
            tc = [c for c in cols if re.match(r'^(Tax|Class|Type|Complex|SpT|Bus|BD|Tholen)', c, re.I)]
            ac = [c for c in cols if re.match(r'^(pV|Albedo|pv|Alb)$', c)]
            nt = na = 0; src = 'x_' + re.sub(r'\W+', '_', name)
            for r in rows_of(t):
                p = match(*[r.get(c) for c in idc])
                if p is None: continue
                for c in tc:
                    t4, sq = coarse(r.get(c))
                    if t4 or sq is not None:
                        tax[p][src] = (r[c], t4, sq); nt += 1; break
                for c in ac:
                    try:
                        v = float(r[c])
                        if 0 < v < 1.5: alb[p][src] = v; na += 1; break
                    except (ValueError, TypeError): pass
            stats[src] = (na, nt)

print('\nper-source matched NEAs (albedo, taxonomy):')
for k, v in stats.items(): print('  %-34s %6d %6d' % (k, v[0], v[1]))

# ---------------------------------------------------------------- combine
ALB_ORDER = ['mp3c', 'sbdb', 'spitzer', 'ssocard', 'sergeyev']
TAX_ORDER = ['mahlke', 'marsset', 'devogele', 'sbdb', 'ssocard_spec', 'sergeyev', 'ssocard_phot', 'ratir']
SPEC = {'mahlke', 'marsset', 'devogele', 'sbdb', 'ssocard_spec'}
def order(d, base):
    extra = [k for k in d if k.startswith('x_')]
    return base[:5] + sorted(extra) + base[5:] if base is TAX_ORDER else base + sorted(extra)

rows = []
conf = collections.Counter()
for p in sorted(set(alb) | set(tax)):
    o = obj[p]
    if o['H'] is None or o['moid'] is None or o['tj'] is None: conf['dropped_missing_H_or_moid'] += 1; continue
    r = dict(pdes=p, a=o['a'], e=o['e'], i=o['i'], q=o['q'], tj=round(o['tj'], 5), moid=o['moid'], H=o['H'],
             nhats=int(p in dv), min_dv=dv.get(p, ''))
    A = alb.get(p, {})
    if A:
        # independent-ish measurements: mp3c/sbdb/ssocard/sergeyev mostly repackage NEOWISE; take the first available in priority order
        # as the label value, and record the full range across sources for the 'clear label' sensitivity test.
        src = next(k for k in order(A, ALB_ORDER) if k in A)
        vals = list(A.values())
        r.update(alb=A[src], alb_src=src, alb_n=len(A), alb_min=min(vals), alb_max=max(vals),
                 alb_srcs='|'.join('%s=%.3f' % (k, A[k]) for k in order(A, ALB_ORDER) if k in A))
        if (min(vals) < 0.10) != (max(vals) < 0.10): conf['albedo_sources_straddle_0.10'] += 1
    else:
        r.update(alb='', alb_src='', alb_n=0, alb_min='', alb_max='', alb_srcs='')
    Tx = tax.get(p, {})
    t4 = sq = None; t4src = sqsrc = ''
    for k in order(Tx, TAX_ORDER):
        if k in Tx and Tx[k][1] and t4 is None: t4, t4src = Tx[k][1], k
        if k in Tx and Tx[k][2] is not None and sq is None: sq, sqsrc = Tx[k][2], k
    l4 = {v[1] for v in Tx.values() if v[1]}
    if len(l4) > 1: conf['tax4_sources_disagree'] += 1
    r.update(tax4=t4 or '', tax4_src=t4src, tax4_spec=int(t4src in SPEC) if t4 else '', tax4_agree=int(len(l4) <= 1) if t4 else '',
             sq='' if sq is None else sq, sq_src=sqsrc,
             tax_all='|'.join('%s=%s' % (k, Tx[k][0]) for k in order(Tx, TAX_ORDER) if k in Tx),
             serg_p='%.2f' % serg_p[p][0] if p in serg_p and serg_p[p][0] == serg_p[p][0] else '')
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
    print('%-34s albedo n=%5d dark=%5d (%.1f%%) | tax4 n=%5d %s | S/Q-vs-rest n=%5d S/Q=%5d' % (name, na, nd, 100 * nd / max(na, 1), sum(c4.values()), dict(sorted(c4.items())), nsq, n1))
print()
cnt(rows, 'all NEAs')
cnt((r for r in rows if r['a'] < 2), 'a < 2 au')
cnt((r for r in rows if r['nhats']), 'NHATS members')
cnt((r for r in rows if r['nhats'] and r['min_dv'] < 6), 'NHATS dv < 6')
cnt((r for r in rows if 0.8 <= r['a'] <= 1.3 and r['e'] < 0.3 and r['i'] < 10), 'NHATS-like box')
print('\nalbedo label source:', collections.Counter(r['alb_src'] for r in rows if r['alb'] != ''))
print('tax4 label source:', collections.Counter(r['tax4_src'] for r in rows if r['tax4']))
print('sq label source:', collections.Counter(r['sq_src'] for r in rows if r['sq'] != ''))
print('rows written:', len(rows), '->', out_csv)
