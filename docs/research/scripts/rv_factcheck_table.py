import json, math, os, statistics, sys
base=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research", "dl", "catalogs", "")
n=json.load(open(base+'nhats.json'))['data']
s=json.load(open(base+'sbdb_neo.json'))
F=s['fields']
idx={f:i for i,f in enumerate(F)}
sb={}
for r in s['data']:
    sb[r[idx['pdes']]]=r
def fl(x):
    try: return float(x)
    except: return None
rows=[]
for o in n:
    des=o['des']; h=fl(o['h']); dv=fl(o['min_dv']['dv']); occ=o['occ']
    r=sb.get(des)
    rp=fl(r[idx['rot_per']]) if r else None
    rows.append(dict(des=des,h=h,dv=dv,occ=(int(occ) if occ not in (None,'') else None),rp=rp,o=o,r=r,sbH=fl(r[idx['H']]),sbcc=r[idx['condition_code']]))
hn=[x for x in rows if x['h'] is None]
print('NHATS h None:',[(x['des'],x['dv'],x['sbH'],x['occ']) for x in hn])
for lim in (4,5,6,7,8):
    print('dv<',lim, sum(1 for x in rows if x['dv']<lim), ' dv<=',lim, sum(1 for x in rows if x['dv']<=lim))
# near 7
print('near 7:',sorted((x['dv'],x['des'],x['h']) for x in rows if 6.995<=x['dv']<=7.005))
print('near 6:',sorted((x['dv'],x['des'],x['h']) for x in rows if 5.995<=x['dv']<=6.005))
print('near 5:',sorted((x['dv'],x['des'],x['h']) for x in rows if 4.995<=x['dv']<=5.005))
print('--- table (NHATS h; None excluded)')
for hop in ('<','<='):
    print('H',hop,24)
    for lim in (5,6,7):
        a=[x for x in rows if x['dv']<lim]
        b=[x for x in a if x['h'] is not None and (x['h']<24 if hop=='<' else x['h']<=24)]
        c=[x for x in b if x['occ'] is not None and x['occ']<=5]
        d=[x for x in c if x['rp'] is not None]
        e=[x for x in d if x['rp']>=2.2]
        d2=[x for x in b if x['rp'] is not None]
        e2=[x for x in d2 if x['rp']>=2.2]
        print(' dv<',lim,'| all',len(a),'| H',len(b),'| occ<=5',len(c),'| period',len(d),'| >=2.2h',len(e),'|| without occ gate: period',len(d2),'>=2.2',len(e2))
print('--- using SBDB H instead')
for lim in (5,6,7):
    a=[x for x in rows if x['dv']<lim]
    b=[x for x in a if x['sbH'] is not None and x['sbH']<24]
    c=[x for x in b if x['occ']<=5]
    d=[x for x in c if x['rp'] is not None]
    e=[x for x in d if x['rp']>=2.2]
    print(' dv<',lim,len(a),len(b),len(c),len(d),len(e))
print('--- members dv<7, H<24')
for x in sorted([x for x in rows if x['dv']<7 and x['h'] is not None and x['h']<24], key=lambda x:x['dv']):
    o=x['o']
    print(f"{x['des']:12s} H={x['h']:5} sbH={x['sbH']} dv={x['dv']:.3f} occ={x['occ']} cc={x['sbcc']} rot={x['rp']} win={o.get('obs_start')}..{o.get('obs_end')} mag={o.get('obs_mag')} flag={o.get('obs_flag')} size={o.get('min_size')}-{o.get('max_size')} diam={x['r'][idx['diameter']]} alb={x['r'][idx['albedo']]} spec={x['r'][idx['spec_B']]},{x['r'][idx['spec_T']]} arc={x['r'][idx['data_arc']]}")
a=[x for x in rows if x['dv']<5]
print('brightest H under 5:',sorted((x['h'],x['des']) for x in a if x['h'] is not None)[:6])
print('rot_per count nhats',sum(1 for x in rows if x['rp'] is not None), 'under6',sum(1 for x in rows if x['rp'] is not None and x['dv']<6),'under5',sum(1 for x in rows if x['rp'] is not None and x['dv']<5))
u5=[x for x in rows if x['dv']<5 and x['rp'] is not None]
print('under5 SBDB periods:',sorted((x['rp'],x['des'],x['h']) for x in u5))
u6=[x for x in rows if x['dv']<6 and x['rp'] is not None]
print('under6 SBDB periods >=1h:',sorted((x['rp'],x['des'],x['h']) for x in u6 if x['rp']>=1))
