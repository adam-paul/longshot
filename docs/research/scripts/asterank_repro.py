"""Re-implementation (not execution) of the public Asterank scoring arithmetic,
to check whether it reproduces the values the Asterank API serves today.
Source read: github.com/typpo/asterank data/pipeline/run/10_sbdb/{scoring,estimate}.py
The original is Python 2, so 4/3 == 1 there."""
import math
G = 6.67300e-20
DENS = {'C':1.38,'D':1.38,'P':1.38,'T':1.38,'B':1.38,'G':1.38,'F':1.38,'S':2.71,'K':2.71,'Q':2.71,'V':2.71,'R':2.71,'A':2.71,'M':5.32}
PRICE = {'water':0.01,'hydrogen':3.65808137,'nitrogen':0.074094,'ammonia':0.01,'iron':2e-7,'nickel':0.00002,'cobalt':0.20,'platinum':2}
C_ = {'water':.2,'iron':.166,'nickel':.014,'cobalt':.002,'hydrogen':0.235,'nitrogen':0.001,'ammonia':0.001}
SPEC = {'Cg':C_,'C':C_,'B':{'hydrogen':0.235,'nitrogen':0.001,'ammonia':0.001,'iron':10},
        'Xk':{'iron':88,'nickel':10,'cobalt':0.5},'X':{'iron':88,'nickel':10,'cobalt':0.5},'Xe':{'iron':88,'nickel':10,'cobalt':0.5}}
def vpk(t): return sum(PRICE[m]*p/100 for m,p in SPEC[t].items())
def mass_from_d(d_km, spec):
    rho = DENS.get(spec[0].upper(), 2)
    vol = 1 * math.pi * (d_km/2)**3          # Python 2: 4/3 -> 1
    return vol * rho / 6 * 1e15
def true_sphere_mass(d_km, rho): return 4/3*math.pi*(d_km/2)**3 * rho * 1e12
cases = [
 ('Ryugu','Cg',dict(H=19.3,albedo=0.15), 82756156358.84914, 4.50e11),
 ('Bennu','B',dict(GM=5.2e-09), 669957009.2821819, 7.33e10),
 ('Didymos','Xk',dict(D=0.78), 62253881855.74079, 5.2e11),
 ('Nereus','Xe',dict(D=0.33), 4714378513.313096, None),
 ('Davida','C',dict(D=270.327), 1.5382627787839414e+19, 3.4e19),
 ('Psyche','X',dict(GM=1.8426377333333332), 27673419946.666664, 2.3e19),
]
for name,spec,kw,api,truemass in cases:
    if 'GM' in kw:
        m = kw['GM']/G
        if m > 1e18: m *= 1e-6
    else:
        d = kw.get('D') or 1329/math.sqrt(kw['albedo'])*10**(-0.2*kw['H'])
        m = mass_from_d(d, spec)
    v = vpk(spec)*m
    top = max(SPEC[spec].items(), key=lambda kv: PRICE[kv[0]]*kv[1])
    share = PRICE[top[0]]*top[1]/100/vpk(spec)
    print(f"{name:8s} spec={spec:3s} mass_used={m:.3e} kg  $/kg={vpk(spec):.6f}  value=${v:,.0f}  api=${api:,.0f}  ratio={v/api:.6f}  top={top[0]} ({share:.1%})"
          + (f"  mass_used/true={m/truemass:.1f}" if truemass else ""))
print("constant check: code mass / true sphere mass =", mass_from_d(1.0,'S')/true_sphere_mass(1.0,2.71))
