import json, os, statistics
base=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research", "dl", "catalogs", "")
n=json.load(open(base+'nhats.json'))['data']
s=json.load(open(base+'sbdb_neo.json'))
F=s['fields']; idx={f:i for i,f in enumerate(F)}
sb={r[idx['pdes']]:r for r in s['data']}
def fl(x):
    try: return float(x)
    except: return None
N=len(n)
arc=[];H=[]
rows=[]
for o in n:
    r=sb[o['des']]
    a=fl(r[idx['data_arc']]); h=fl(o['h']); dv=float(o['min_dv']['dv'])
    rows.append((o['des'],a,h,dv,r,o))
arcs=[a for _,a,_,_,_,_ in rows if a is not None]
print('N',N,'arc present',len(arcs),'median',statistics.median(arcs))
for t in (30,60,100,180,365,1000,2900):
    c=sum(1 for a in arcs if a<t); print('arc <',t,c, round(100*c/N,1),'% of N;', round(100*c/len(arcs),1),'% of with-arc')
long=sum(1 for _,a,h,_,_,_ in rows if a is not None and a>1000)
rp=sum(1 for _,a,h,_,_,_ in rows if a is not None and h is not None and h>=27 and a>=60)
both=sum(1 for _,a,h,_,_,_ in rows if a is not None and h is not None and h>=27 and a>=60 and a>1000)
print('arc>1000',long,'H>=27&arc>=60',rp,'overlap',both,'union',long+rp-both, 'share none', round(100*(1-(long+rp-both)/N),1))
# under 5
u5=[x for x in rows if x[3]<5]
print('u5',len(u5),'RP pool',sum(1 for _,a,h,_,_,_ in u5 if a is not None and h is not None and h>=27 and a>=60),'arc>1000',sum(1 for _,a,h,_,_,_ in u5 if a is not None and a>1000))
print('u5 with any A1/A2/A3', sum(1 for x in u5 if any(x[4][idx[k]] for k in ('A1','A2','A3'))))
# multi-year NEAs
allarc=[fl(r[idx['data_arc']]) for r in s['data'] if r[idx['kind']].startswith('a')]
print('NEAs',len(allarc))
for t in (365,730,1000,1095,1461,1826):
    print('NEA arc >',t, sum(1 for a in allarc if a is not None and a>t))
# A2 counts
def sig(r,k):
    v=fl(r[idx[k]]); e=fl(r[idx[k+'_sigma']])
    return (abs(v)/e) if (v is not None and e) else None
ast=[r for r in s['data'] if r[idx['kind']].startswith('a')]
print('A2 any',sum(1 for r in ast if r[idx['A2']]), '>=3s',sum(1 for r in ast if (sig(r,'A2') or 0)>=3))
print('A1 any',sum(1 for r in ast if r[idx['A1']]), '>=3s',sum(1 for r in ast if (sig(r,'A1') or 0)>=3))
nh=set(o['des'] for o in n)
print('NHATS A2>=3s',sum(1 for r in ast if r[idx['pdes']] in nh and (sig(r,'A2') or 0)>=3),'NHATS A1>=3s',sum(1 for r in ast if r[idx['pdes']] in nh and (sig(r,'A1') or 0)>=3))
# specific objects
for d in ('2010 CW266','469219','2022 OB5','1998 KY26','2015 BM510','2011 AA37','65803','6178','99942','2026 HT'):
    r=sb.get(d)
    o=[x for x in n if x['des']==d]
    print(d, 'NHATS' if o else 'not-NHATS', (o[0]['h'],o[0]['min_dv']['dv'],o[0]['min_size'],o[0]['max_size'],o[0]['occ'],o[0]['obs_start'],o[0]['obs_end'],o[0]['obs_mag'],o[0]['obs_flag']) if o else '', 'SBDB:', (r[idx['H']],r[idx['diameter']],r[idx['albedo']],r[idx['rot_per']],r[idx['spec_B']],r[idx['spec_T']],r[idx['A1']],r[idx['A2']],r[idx['A2_sigma']],r[idx['data_arc']],r[idx['condition_code']]) if r else None)
