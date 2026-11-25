#!/usr/bin/env python3
"""Count distinct NHATS members with a PUBLISHED most-probable source region (Marsset+2022 table 7; Sergeyev+2023 Origin)
and how many have nu6 on top. Usage: pn_nu6_dedup.py <sbdb_neo.json> <nhats.json> <vizier_dir>"""
import sys, json, re
sb_fn, nh_fn, V = sys.argv[1:4]
def parse(fn):
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
sb = json.load(open(sb_fn)); F = sb['fields']; key = {}
for r in sb['data']:
    d = dict(zip(F, r)); key[d['pdes']] = d['pdes']
    m = re.search(r'\(([^)]+)\)', d['full_name'] or '')
    if m: key[m.group(1).strip()] = d['pdes']
nh = {o['des'] for o in json.load(open(nh_fn))['data']}
ER = ['P[Hun]', 'P[nu6]', 'P[Pho]', 'P[3:1J]', 'P[5:2J]', 'P[2:1J]', 'P[JFC]']; top = {}
T = parse(V + '/J_AJ_163_165.tsv')['J/AJ/163/165/table7']
for r in T['rows']:
    x = dict(zip(T['cols'], r)); p = key.get(x['Number']) or key.get(x['Desig'])
    if p in nh:
        try: pr = [float(x[c]) for c in ER]
        except ValueError: continue
        top.setdefault(p, {})['marsset'] = ER[pr.index(max(pr))]
T = parse(V + '/J_A_A_679_A148.tsv')['J/A+A/679/A148/catalog']
for r in T['rows']:
    x = dict(zip(T['cols'], r))
    if not x['Origin']: continue
    p = key.get(x['Number']) or key.get(x['Design'])
    if p in nh: top.setdefault(p, {})['sergeyev'] = x['Origin']
n = len(top); nu6 = sum(1 for v in top.values() if all('nu6' in s for s in v.values()))
print('distinct NHATS members with a published top source:', n, '| in both tables:', sum(1 for v in top.values() if len(v) == 2),
      '| per table: Marsset', sum(1 for v in top.values() if 'marsset' in v), 'Sergeyev', sum(1 for v in top.values() if 'sergeyev' in v))
print('nu6 on top in every table that lists the object: %d = %.1f%%' % (nu6, 100 * nu6 / n))
print('exceptions:', {k: v for k, v in top.items() if not all('nu6' in s for s in v.values())})
