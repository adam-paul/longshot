"""Replicate the first-round per-source coverage counts (all NHATS / dv<6 / dv<5 / all NEAs) from fresh downloads.
Usage: python3 -I cx_replicate.py <catalogs_dir> <cx_dir>"""
import sys, os, re, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats, parse_vizier

CAT, CX = sys.argv[1], sys.argv[2]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
lab = json.load(open(os.path.join(CX, 'labels.json')))
sz = json.load(open(os.path.join(CX, 'sizes_local.json')))
V = os.path.join(CX, 'vizier')


def row(name, pset, claim):
    pset = set(pset)
    got = (sum(1 for p in pset if p in nh), sum(1 for p in pset if p in nh and nh[p]['dv'] < 6), sum(1 for p in pset if p in nh and nh[p]['dv'] < 5), len(pset))
    ok = 'MATCH' if list(got) == list(claim) else ('close' if all(abs(a - b) <= max(2, 0.02 * b) for a, b in zip(got, claim)) else 'DIFF')
    print('%-46s mine %-24s claimed %-24s %s' % (name, got, tuple(claim), ok))


def has(v):
    return v not in (None, '')


S = {s['pdes']: s for s in U.rows}
row('SBDB taxonomy', [p for p, s in S.items() if has(s['spec_B']) or has(s['spec_T'])], (23, 0, 0, 327))
row('SBDB albedo', [p for p, s in S.items() if has(s['albedo'])], (69, 2, 0, 1205))
row('SBDB diameter', [p for p, s in S.items() if has(s['diameter'])], (70, 3, 1, 1247))
row('SBDB rot_per', [p for p, s in S.items() if has(s['rot_per'])], (306, 32, 14, 2180))
row('SBDB B-V or U-B', [p for p, s in S.items() if has(s['BV']) or has(s['UB'])], (3, 0, 0, 38))
row('SBDB GM or density', [p for p, s in S.items() if has(s['GM']) or has(s['density'])], (3, 0, 0, 9))
row('SBDB A2', [p for p, s in S.items() if has(s['A2'])], (169, 23, 11, 618))
row('SBDB A1', [p for p, s in S.items() if has(s['A1'])], (18, 12, 10, 21))
row('radar astrometry (SBDB n_del/n_dop)', [p for p, o in sz.items() if o.get('radar_astrom')], (232, 25, 12, 1110))
row('Mahlke+2022', [p for p in lab if 'mahlke22' in lab[p]], (175, 12, 3, 1165))
row('Sergeyev+2023 (all rows incl. U)', [p for p in lab if 'sergeyev23' in lab[p] or 'sergeyev23U' in lab[p]], (211, 12, 3, 2279))
row('Devogele+2019 MANOS spectra', [p for p in lab if 'devogele19' in lab[p]], (96, 12, 4, 209))
row('Marsset+2022 MITHNEOS', [p for p in lab if 'marsset22' in lab[p]], (34, 1, 0, 417))
row('Navarro-Meza+2024 RATIR (either table)', [p for p in lab if 'ratir24hi' in lab[p] or 'ratir24lo' in lab[p]], (24, 2, 1, 211))
row('Spitzer NEO compilation', [p for p, o in sz.items() if o.get('spitzer')], (112, 4, 0, 2124))
# Thirouin 2016 / 2018 objects observed
for fn, tn, claim in (('J_AJ_152_163.tsv', 'J/AJ/152/163/table1', None), ('J_ApJS_239_4.tsv', 'J/ApJS/239/4/table1', (52, 9, 6, 141))):
    ps = {U.resolve(r['Name']) for r in parse_vizier(os.path.join(V, fn))[tn]} - {None}
    if claim:
        row('Thirouin+2018 MANOS photometry', ps, claim)
    else:
        print('%-46s mine %s (first round: 86 NEAs, 32 in NHATS)' % ('Thirouin+2016 MANOS photometry', (sum(1 for p in ps if p in nh), len(ps))))
# LCDB
lines = open(os.path.join(CX, 'lcdb', 'x', 'lc_summary_pub.txt'), errors='replace').read().split('\n')
hi = next(i for i, l in enumerate(lines) if l.startswith('NUMBER'))
hdr = lines[hi]


def col(name):
    return [m.start() for m in re.finditer(r'(?<![A-Z0-9.])' + re.escape(name) + r'(?![A-Z0-9.])', hdr)][0]


c_name, c_des, c_fam, c_per, c_desc, c_u, c_notes = col('NAME'), col('DESIG'), col('FAM'), col('PERIOD'), col('P DESC'), col('U'), col('NOTES')
anyq, u2 = set(), set()
for l in lines[hi + 2:]:
    if len(l) < c_u:
        continue
    try:
        pv = float(l[c_per:c_desc].strip())
    except ValueError:
        continue
    if not pv:
        continue
    num = l[:c_name].strip()
    p = U.by_number(num) if num.isdigit() and int(num) > 0 else None
    if p is None:
        p = U.resolve(l[c_des:c_fam].strip(), l[c_name:c_des].strip())
    if p:
        anyq.add(p)
        if l[c_u:c_notes].strip()[:1] in ('2', '3'):
            u2.add(p)
row('LCDB 2023-10 any quality', anyq, (304, 31, 13, 2174))
row('LCDB U>=2', u2, (273, 30, 13, 1990))
print('NHATS today %d (first round 7,226); dv<6 %d (726); dv<5 %d (286); SBDB NEAs %d (43,151)' % (len(nh), sum(1 for d in nh if nh[d]['dv'] < 6), sum(1 for d in nh if nh[d]['dv'] < 5), len(S)))
new = sorted(d for d in nh if S[d]['first_obs'] and S[d]['first_obs'] >= '2026-11-10')
print('NHATS objects first observed on or after 2026-11-10:', new)
