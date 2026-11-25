"""Build one row per SBDB NEA with exact presence flags from every local source.
Usage: cx_build_master.py <catalogs_dir> <coverage_exact_dir> <out_parquet>
Reads: nhats.json, sbdb_neo.json, bft_nea_subset.parquet (from cx_bft_explore.py), LCDB, Spitzer, MP3C, VizieR tables,
Gaia, radar, DAMIT. Writes master parquet + prints match diagnostics."""
import sys, os, re, csv, json, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from cx_lib import Universe, load_nhats, parse_vizier, norm, unpack_prov, unpack_number

CAT, CX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
print('SBDB NEAs', len(U.rows), '| ambiguous keys', len(U.amb), '| NHATS', len(nh))
missing = [d for d in nh if d not in U.by_pdes]
print('NHATS des not in SBDB NEA list:', len(missing), missing[:10])

def has(v):
    return v not in (None, '')

M = {}
for s in U.rows:
    p = s['pdes']
    M[p] = {
        'pdes': p, 'name': s.get('name'), 'prov': s['_prov'], 'H': float(s['H']) if has(s['H']) else np.nan,
        'numbered': p.isdigit(), 'nhats': p in nh, 'dv': nh[p]['dv'] if p in nh else np.nan,
        'sbdb_tax': has(s['spec_B']) or has(s['spec_T']), 'sbdb_spec_B': s['spec_B'], 'sbdb_spec_T': s['spec_T'],
        'sbdb_albedo': has(s['albedo']), 'sbdb_diam': has(s['diameter']),
        'sbdb_diam_val': float(s['diameter']) if has(s['diameter']) else np.nan,
        'sbdb_rot': has(s['rot_per']), 'sbdb_rot_val': float(s['rot_per']) if has(s['rot_per']) else np.nan,
        'sbdb_color': has(s['BV']) or has(s['UB']) or has(s['IR']), 'sbdb_gm_dens': has(s['GM']) or has(s['density']),
        'sbdb_A1': has(s['A1']), 'sbdb_A2': has(s['A2']), 'sbdb_A3': has(s['A3']),
        'cond': s['condition_code'], 'data_arc': s['data_arc'],
    }

def flag(col, pset, default=False):
    for p in M:
        M[p][col] = default
    for p in pset:
        M[p][col] = True

# ---------- SsODNet ssoBFT ----------
bft = pd.read_parquet(os.path.join(CX, 'bft_nea_subset.parquet'))
print('BFT subset rows', len(bft))
def nonempty(x):
    if x is None:
        return False
    try:
        return len(x) > 0 and any(v is not None and not (isinstance(v, float) and np.isnan(v)) for v in x)
    except TypeError:
        return False
bft_match = {}
unmatched_nea = 0
dup = 0
for i, r in enumerate(bft.itertuples(index=False)):
    rd = r._asdict() if False else None
cols = list(bft.columns)
ix = {c: cols.index(c) for c in cols}
vals = bft.values
for row in vals:
    num = row[ix['number']]
    name = row[ix['name']]
    p = None
    if num is not None and not (isinstance(num, float) and np.isnan(num)):
        p = U.by_number(int(num))
    if p is None and isinstance(name, str):
        p = U.key2p.get(norm(name))
    if p is None and isinstance(row[ix['id']], str):
        p = U.key2p.get(norm(row[ix['id']]))
    if p is None:
        if isinstance(row[ix['class']], str) and row[ix['class']].startswith('NEA'):
            unmatched_nea += 1
        continue
    if p in bft_match:
        dup += 1
        continue
    bft_match[p] = row
print('SBDB NEAs matched in BFT:', len(bft_match), 'of', len(M), '| BFT NEA-class rows not in SBDB NEA list:', unmatched_nea, '| duplicate matches skipped:', dup)
print('NHATS matched in BFT:', sum(1 for p in nh if p in bft_match), 'of', len(nh))
def g(row, c):
    v = row[ix[c]]
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    return v
for p, m in M.items():
    row = bft_match.get(p)
    m['bft'] = row is not None
    if row is None:
        for c in ('bft_tax', 'bft_albedo', 'bft_diam', 'bft_spin', 'bft_color', 'bft_density', 'bft_mass', 'bft_ti', 'bft_yark', 'bft_phase', 'bft_srcreg', 'bft_dv'):
            m[c] = False
        m.update({'bft_class': None, 'bft_tax_class': None, 'bft_tax_complex': None, 'bft_tax_technique': None, 'bft_tax_scheme': None, 'bft_tax_wave': None,
                  'bft_albedo_val': np.nan, 'bft_diam_val': np.nan, 'bft_density_val': np.nan, 'bft_pmin': np.nan, 'bft_nspin': 0,
                  'bft_yark_snr': np.nan, 'bft_ncolor': 0, 'bft_nphase': 0, 'bft_H': np.nan})
        continue
    m['bft_class'] = g(row, 'class')
    m['bft_tax'] = g(row, 'taxonomy.class') is not None
    m['bft_tax_class'] = g(row, 'taxonomy.class'); m['bft_tax_complex'] = g(row, 'taxonomy.complex')
    m['bft_tax_technique'] = g(row, 'taxonomy.technique'); m['bft_tax_scheme'] = g(row, 'taxonomy.scheme'); m['bft_tax_wave'] = g(row, 'taxonomy.waverange')
    m['bft_albedo'] = g(row, 'albedo.value') is not None; m['bft_albedo_val'] = g(row, 'albedo.value') if m['bft_albedo'] else np.nan
    m['bft_diam'] = g(row, 'diameter.value') is not None; m['bft_diam_val'] = g(row, 'diameter.value') if m['bft_diam'] else np.nan
    per = row[ix['spins.period.value']]
    pv = [float(x) for x in per if x is not None and not np.isnan(x)] if per is not None else []
    m['bft_spin'] = len(pv) > 0; m['bft_nspin'] = len(pv); m['bft_pmin'] = min(pv) if pv else np.nan
    m['bft_pall'] = ';'.join('%g' % x for x in pv)
    ci = row[ix['colors.color.value']]
    m['bft_color'] = nonempty(ci); m['bft_ncolor'] = len(ci) if ci is not None else 0
    m['bft_density'] = g(row, 'density.value') is not None; m['bft_density_val'] = g(row, 'density.value') if m['bft_density'] else np.nan
    m['bft_mass'] = g(row, 'mass.value') is not None
    m['bft_ti'] = g(row, 'thermal_inertia.value') is not None
    m['bft_yark'] = (g(row, 'yarkovsky.dadt.value') is not None) or (g(row, 'yarkovsky.A2.value') is not None)
    m['bft_yark_snr'] = g(row, 'yarkovsky.snr') if g(row, 'yarkovsky.snr') is not None else np.nan
    ph = row[ix['phase_functions.H.value']]
    m['bft_phase'] = nonempty(ph); m['bft_nphase'] = len(ph) if ph is not None else 0
    m['bft_srcreg'] = any(g(row, c) is not None for c in cols if c.startswith('source_regions.') and c.endswith('.value'))
    m['bft_dv'] = g(row, 'delta_v.delta_v') is not None
    m['bft_H'] = g(row, 'absolute_magnitude.H.value') if g(row, 'absolute_magnitude.H.value') is not None else np.nan
for p in M:
    M[p].setdefault('bft_pall', '')

# ---------- LCDB ----------
lines = open(os.path.join(CAT, 'lcdb', 'lc_summary_pub.txt'), errors='replace').read().split('\n')
hi = next(i for i, l in enumerate(lines) if l.startswith('NUMBER'))
hdr = lines[hi]
def col(name, nth=0):
    idx = [m.start() for m in re.finditer(r'(?<![A-Z0-9.])' + re.escape(name) + r'(?![A-Z0-9.])', hdr)]
    return idx[nth]
c_name, c_des, c_fam, c_per, c_desc, c_u, c_notes = col('NAME'), col('DESIG'), col('FAM'), col('PERIOD'), col('P DESC'), col('U'), col('NOTES')
lc = {}
for l in lines[hi + 2:]:
    if len(l) < c_u:
        continue
    num = l[:c_name].strip(); name = l[c_name:c_des].strip(); des = l[c_des:c_fam].strip()
    per = l[c_per:c_desc].strip(); u = l[c_u:c_notes].strip()
    try:
        pv = float(per)
    except ValueError:
        pv = None
    if not pv:
        continue
    p = None
    if num.isdigit() and int(num) > 0:
        p = U.by_number(num)
    if p is None:
        p = U.resolve(des, name)
    if p:
        lc[p] = (pv, u)
for p, m in M.items():
    r = lc.get(p)
    m['lcdb_per'] = r is not None; m['lcdb_pval'] = r[0] if r else np.nan; m['lcdb_U'] = r[1] if r else ''
    m['lcdb_U2'] = bool(r and r[1][:1] in ('2', '3'))
# LCDB colour index: object header lines followed by reference lines; a colour exists if any reference line has a value after the Amp column
cl = open(os.path.join(CAT, 'lcdb', 'lc_colorindex_pub.txt'), errors='replace').read().split('\n')
chi = [i for i, l in enumerate(cl) if l.startswith('Number')][-1]
chdr = cl[chi]; c_bv = chdr.index('BV')
cur = None; lc_col = set()
for l in cl[chi + 2:]:
    if not l.strip():
        cur = None; continue
    numtxt = l[:9].strip()
    if cur is None:
        nm = l[10:40].strip()
        cur = U.by_number(numtxt) if numtxt.isdigit() and int(numtxt) > 0 else U.resolve(nm)
        if cur is None and numtxt.isdigit():
            cur = '__none__'
        elif cur is None:
            cur = '__none__'
        continue
    if cur != '__none__' and l[c_bv - 1:].strip():
        lc_col.add(cur)
flag('lcdb_color', lc_col)

# ---------- Spitzer ----------
sp = {}
for r in csv.DictReader(open(os.path.join(CAT, 'spitzerneos.csv'))):
    if r['diam'] in ('', 'nan'):
        continue
    p = U.resolve(r['number'], r['desig'], r['name'])
    if p:
        sp[p] = float(r['diam'])
for p, m in M.items():
    m['spitzer'] = p in sp; m['spitzer_diam'] = sp.get(p, np.nan)

# ---------- MP3C ----------
m3a, m3d = set(), {}
for r in csv.DictReader(open(os.path.join(CAT, 'mp3c_nea_best.csv'))):
    p = U.resolve(r['number'], r['name'])
    if p is None and r['name']:
        mm = re.match(r'^(\d{4})([A-Z]{2}\d*)$', r['name'])
        if mm:
            p = U.resolve(mm.group(1) + ' ' + mm.group(2))
    if not p:
        continue
    if r['albedo']:
        m3a.add(p)
    if r['diameter']:
        m3d[p] = float(r['diameter'])
flag('mp3c_albedo', m3a)
for p, m in M.items():
    m['mp3c_diam'] = p in m3d; m['mp3c_diam_val'] = m3d.get(p, np.nan)

# ---------- VizieR taxonomy/colour/spin tables ----------
V = os.path.join(CAT, 'vizier')
t = parse_vizier(os.path.join(V, 'J_AJ_158_196.tsv'))['J/AJ/158/196/table5']
dev = {}
for r in t:
    p = U.resolve(r['ID'])
    if p:
        dev[p] = r['Taxon']
t = parse_vizier(os.path.join(V, 'J_AJ_163_165.tsv'))['J/AJ/163/165/table7']
mar = {}
for r in t:
    p = U.resolve(r['Number'], r['Desig'], r['Name'])
    if p:
        mar[p] = r['Taxon']
t = parse_vizier(os.path.join(V, 'J_A_A_665_A26.tsv'))['J/A+A/665/A26/asteroid']
mah = {}
for r in t:
    p = U.resolve(r['Number'], r['Name'])
    if p:
        mah[p] = r['class']
t = parse_vizier(os.path.join(V, 'J_A_A_679_A148.tsv'))['J/A+A/679/A148/catalog']
ser = {}
for r in t:
    p = U.resolve(r['Number'], r['Design'], r['Name'])
    if p:
        ser[p] = (r['Complex'], r['pComplex'], r['TMethod'])
tt = parse_vizier(os.path.join(V, 'J_AJ_167_163.tsv'))
rat = {}
for tn, lab in (('J/AJ/167/163/table4', 'hi'), ('J/AJ/167/163/table5', 'lo')):
    for r in tt[tn]:
        p = U.resolve(r['ID'])
        if p:
            probs = {k: float(r[k] or 0) for k in ('P(C+X)', 'P(Q)', 'P(S)', 'P(D)', 'P(V)')}
            best = max(probs, key=probs.get)
            if p not in rat or lab == 'hi':
                rat[p] = (lab, best, probs[best])
for p, m in M.items():
    m['devogele'] = p in dev; m['devogele_tax'] = dev.get(p)
    m['marsset'] = p in mar; m['marsset_tax'] = mar.get(p)
    m['mahlke'] = p in mah; m['mahlke_class'] = mah.get(p)
    m['sergeyev'] = p in ser; m['sergeyev_complex'] = ser[p][0] if p in ser else None
    m['sergeyev_classified'] = bool(p in ser and ser[p][0] not in ('', 'U'))
    m['ratir'] = p in rat; m['ratir_hi'] = bool(p in rat and rat[p][0] == 'hi'); m['ratir_best'] = rat[p][1] if p in rat else None
# Thirouin
th = {}
t = parse_vizier(os.path.join(V, 'J_AJ_152_163.tsv'))['J/AJ/152/163/table1']
for r in t:
    p = U.resolve(r['Name'])
    if p:
        try:
            pv = float(r['Per'])
        except ValueError:
            pv = None
        th.setdefault(p, []).append(('T16', r['l_Per'], pv, r['LCType']))
t = parse_vizier(os.path.join(V, 'J_ApJS_239_4.tsv'))['J/ApJS/239/4/table1']
for r in t:
    p = U.resolve(r['Name'])
    if p:
        try:
            pv = float(r['Prot'])
        except ValueError:
            pv = None
        th.setdefault(p, []).append(('T18', r['l_Prot'], pv, r['Set']))
for p, m in M.items():
    e = th.get(p, [])
    m['thirouin_obs'] = len(e) > 0
    full = [x[2] for x in e if x[2] and not x[1]]
    m['thirouin_per'] = len(full) > 0; m['thirouin_pval'] = min(full) if full else np.nan
    m['thirouin_limit'] = bool(any(x[2] and x[1] for x in e) and not full)

# ---------- NEOWISE published thermal-fit tables (VizieR, CfA mirror) ----------
NV = os.path.join(CX, 'vizier')
neow = collections.defaultdict(dict)
def add_neow(tag, fn, tn, packed_cols=(), text_cols=(), diam='Diam', cond=None):
    rows = parse_vizier(os.path.join(NV, fn))[tn]
    n = 0; un = set()
    for r in rows:
        if cond and not cond(r):
            continue
        p = U.resolve(*[r.get(c) for c in text_cols], packed=[r.get(c) for c in packed_cols])
        if p:
            try:
                d = float(r[diam])
            except (ValueError, KeyError):
                d = np.nan
            neow[p][tag] = d; n += 1
        else:
            un.add(tuple(r.get(c) for c in list(packed_cols) + list(text_cols)))
    print('NEOWISE table %-12s rows %5d matched-to-NEA rows %5d unmatched ids %d %s' % (tag, len(rows), n, len(un), list(un)[:4]))
add_neow('Mai11', 'J_ApJ_743_156.tsv', 'J/ApJ/743/156/table1', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Mai12', 'J_ApJ_760_L12.tsv', 'J/ApJ/760/L12/table1', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Mai14', 'J_ApJ_784_110.tsv', 'J/ApJ/784/110/table2', packed_cols=('Name', 'OName'), text_cols=('OName', 'Name'))
add_neow('Nug15', 'J_ApJ_814_117.tsv', 'J/ApJ/814/117/nea', packed_cols=('MPC',), text_cols=('Name',))
add_neow('Nug16', 'J_AJ_152_63.tsv', 'J/AJ/152/63/asteroids', packed_cols=('MPC',), text_cols=('Name',), cond=lambda r: r['Ast'].strip() == 'NEA')
add_neow('Mas17', 'J_AJ_154_168.tsv', 'J/AJ/154/168/table1', packed_cols=('Name',))
add_neow('Mas18', 'J_AJ_156_60.tsv', 'J/AJ/156/60/table1', packed_cols=('Name',))
for p, m in M.items():
    e = neow.get(p, {})
    m['neowise_viz'] = len(e) > 0; m['neowise_viz_refs'] = ';'.join(sorted(e)); m['neowise_viz_diam'] = np.nanmin(list(e.values())) if e and not all(np.isnan(list(e.values()))) else np.nan

# ---------- Gaia ----------
gr = set()
for r in csv.DictReader(open(os.path.join(CAT, 'gaia_sso_refl_objects.csv'))):
    p = U.by_number(r['number_mp'])
    if p:
        gr.add(p)
flag('gaia_refl', gr)

# ---------- Radar ----------
rd = json.load(open(os.path.join(CAT, 'sb_radar.json')))
ra = collections.Counter(); ra_last = {}
for r in rd['data']:
    p = U.resolve(r[0])
    if p:
        ra[p] += 1; ra_last[p] = max(ra_last.get(p, ''), r[1])
for p, m in M.items():
    m['radar_astrom'] = p in ra; m['radar_n'] = ra.get(p, 0); m['radar_last'] = ra_last.get(p, '')
html = open(os.path.join(CAT, 'echo_alldetections.html'), errors='replace').read()
cells = re.split(r'<td>', html, flags=re.I)
det = set(); det_un = []
for cell in cells[1:]:
    for item in re.findall(r'<b>(.*?)</b>', cell, flags=re.I | re.S):
        txt = re.sub(r'<[^>]+>', ' ', item); txt = re.sub(r'\s+', ' ', txt).strip()
        if not txt:
            continue
        p = None
        m1 = re.match(r'^(\d+)\s+(.*)$', txt)
        if m1 and not re.match(r'^\d{4}\s+[A-Z]{2}\d*$', txt):
            p = U.by_number(m1.group(1))
        if p is None:
            p = U.resolve(txt)
        if p:
            det.add(p)
        else:
            det_un.append(txt)
print('radar detections page: matched NEAs', len(det), '| unmatched items', len(det_un), det_un[140:150])
flag('radar_detlist', det)

# ---------- DAMIT ----------
dm = set()
for r in csv.DictReader(open(os.path.join(CAT, 'damit', 'asteroids.csv'), encoding='utf-8-sig')):
    p = U.resolve(r['number'], r['designation'], r['name'])
    if p:
        dm.add(p)
flag('damit', dm)

df = pd.DataFrame(list(M.values()))
df.to_parquet(OUT)
print('wrote', OUT, df.shape)
print(df[[c for c in df.columns if df[c].dtype == bool]].sum().to_string())
