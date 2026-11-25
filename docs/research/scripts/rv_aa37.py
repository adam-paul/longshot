import json,sys,re,glob,os
p=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "research", "dl", "coverage-exact", "")
c=json.load(open(p+'cards/2011_AA37.json'))
def walk(d,pre=''):
    if isinstance(d,dict):
        for k,v in d.items():
            walk(v,pre+'.'+k if pre else k)
    elif isinstance(d,list):
        for i,v in enumerate(d[:6]): walk(v,pre+f'[{i}]')
    else:
        if d not in (None,'',[],{}): print(pre,'=',str(d)[:160])
# print only parameters.physical
phys=c.get('parameters',{}).get('physical',c)
walk(phys,'phys')
