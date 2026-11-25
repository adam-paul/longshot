"""Worked examples for the value tag. Every assumption is a named constant.
Run: python3 value_tag.py   (numpy only). Seeded; 400,000 draws per case."""
import numpy as np, math, sys
rng = np.random.default_rng(20261121)
N = 400_000
OZT_PER_KG = 1000/31.1034768

# ---- prices, $/troy oz, Umicore 10am price 20 Nov 2026 (read today) ----
P_OZ_NOV26 = dict(Pt=1336., Pd=912., Rh=8950., Ir=10200., Ru=1900., Os=0.)   # Os: no benchmark market
# USGS MCS 2026: 2025 annual averages (Engelhard unfabricated)
P_OZ_2025 = dict(Pt=1200., Pd=1100., Rh=5800., Ir=4400., Ru=690., Os=0.)
def per_kg(p): return {k: v*OZT_PER_KG for k, v in p.items()}
PK = per_kg(P_OZ_NOV26); PK25 = per_kg(P_OZ_2025)

# ---- bulk PGM, ppb (= mg/t), Horan et al. 2003 Table 1 (read today). Rh not measured there:
#      Rh = 0.30 x Ir (CI ratio 0.141/0.470, Lodders 2003, recalled) ----
def rock(Os, Ir, Ru, Pt, Pd): return dict(Os=Os, Ir=Ir, Ru=Ru, Pt=Pt, Pd=Pd, Rh=0.30*Ir)
ROCKS = {
 'H' : [rock(809.8,730.6,1105,1504,812.6), rock(819.5,735.3,1141,1568,853.9), rock(860.4,762.0,1188,1611,912.7)],  # Forest Vale, Ochansk, Forest City
 'L' : [rock(497.3,441.8,606.9,867.1,486.1), rock(696.3,627.8,970.1,1295,624.8), rock(638.6,594.2,919.5,1212,599.1)],  # Farmington, Chico x2
 'LL': [rock(288.6,260.6,400.6,513.5,390.8), rock(334.2,309.2,484.6,635.3,442.7), rock(351.2,316.7,537.4,672.3,346.0)],  # Semarkona x2, Chainpur
 'CI': [rock(459.2,455.6,651.5,858.3,562.9), rock(428.8,406.0,608.7,829.4,528.5)],  # Orgueil, Ivuna
 'CM': [rock(580.0,557.7,740.8,1043,618.9), rock(661.7,613.1,851.0,1067,578.0), rock(569.3,544.2,791.4,1041,576.8)],
 'EH': [rock(625.5,566.9,855.9,1162,891.0), rock(501.0,468.7,734.1,962.7,835.2), rock(666.4,610.5,907.4,1246,919.1), rock(604.9,555.7,838.9,1126,887.1)],
 'EL': [rock(827.9,748.8,1168,1528,920.8), rock(710.9,642.9,929.0,1262,887.7), rock(276.7,253.5,366.7,502.8,360.0), rock(725.5,672.5,1021,1447,907.6)],
}
def usd_per_t(r, pk): return sum(r[k]*1e-6*pk[k] for k in r)       # ppb = mg/t = 1e-6 kg/t
def ppm_total(r): return sum(r.values())/1000.
print("== contained PGM per tonne of rock ==")
ROCK_USD = {}
for k, lst in ROCKS.items():
    v = [usd_per_t(r, PK) for r in lst]; v25 = [usd_per_t(r, PK25) for r in lst]; pp = [ppm_total(r) for r in lst]
    ROCK_USD[k] = (min(v), max(v))
    print(f"{k:3s} total 6-PGM {min(pp):.2f}-{max(pp):.2f} ppm | $/t at 20 Nov 2026: {min(v):.0f}-{max(v):.0f} | at 2025 averages: {min(v25):.0f}-{max(v25):.0f}")
# iron-meteorite basket: chondritic element proportions (assumption), Lodders 2003 CI ppm (recalled)
CI = dict(Ru=0.692, Rh=0.141, Pd=0.588, Os=0.486, Ir=0.470, Pt=1.004); s = sum(CI.values())
BASKET = sum(CI[k]/s*PK[k] for k in CI); BASKET25 = sum(CI[k]/s*PK25[k] for k in CI)
print(f"basket $/kg of total PGM (chondritic mix, Os unpriced): Nov 2026 {BASKET:,.0f}; 2025 avg {BASKET25:,.0f}; ratio {BASKET/BASKET25:.2f}")
print("per-metal $/kg Nov 2026:", {k: round(v) for k, v in PK.items()})
for g, lab in ((14.70,'10th'),(40.78,'50th'),(107.86,'90th')):
    print(f"iron meteorite {lab} pct {g} ppm -> ${g*1e-3*BASKET:,.0f} per tonne of metal")
# ---- market sizes (IPA/SFA factsheets May 2026 for 2025 primary supply; USGS MCS 2026 for Ni, Co) ----
SUP = dict(Pt=178., Pd=197., Rh=22., Ir=7., Ru=30.)
print("== annual primary supply, tonnes and $ at 20 Nov 2026 prices ==")
tot = 0
for k, t in SUP.items():
    usd = t*1000*PK[k]; tot += usd; print(f"{k}: {t:.0f} t  ${usd/1e9:.2f}B")
print(f"five PGMs total ${tot/1e9:.1f}B/yr; nickel 3.9 Mt x $15,371/t = ${3.9e6*15371/1e9:.0f}B; cobalt 310 kt x $33,525/t = ${310e3*33525/1e9:.1f}B")

# ---- lognormal for Cannon et al. 2023 Table 2 percentiles ----
MU = math.log(40.78); SIG = (math.log(107.86)-math.log(14.70))/(2*1.2816)
def iron_grade(n):
    g = np.exp(rng.normal(MU, SIG, n)); return np.clip(g, 6., 230.)      # Cannon: range ~6 to 230 ppm

# ---- class model, H-conditioned, for H 24-29 (see report section 1.5) ----
CLASSES = ['OC','C','BD','V','Xe','Xm_metal','Xm_sil','Xp','other_chond','other_poor']
X = 0.23; XE, XM, XP = 0.35, 0.32, 0.33; METAL_GIVEN_M = 0.38
PRIOR = dict(OC=0.41, C=0.13, BD=0.05, V=0.05, Xe=X*XE, Xm_metal=X*XM*METAL_GIVEN_M, Xm_sil=X*XM*(1-METAL_GIVEN_M), Xp=X*XP,
             other_chond=0.09, other_poor=0.04)
assert abs(sum(PRIOR.values())-1) < 1e-9
ALB = dict(OC=(0.25,0.35), C=(0.05,0.45), BD=(0.05,0.45), V=(0.35,0.3), Xe=(0.45,0.3), Xm_metal=(0.15,0.35), Xm_sil=(0.15,0.35),
           Xp=(0.05,0.45), other_chond=(0.2,0.4), other_poor=(0.25,0.4))          # (median albedo, sigma of ln albedo)
RHO = dict(OC=(1700,3400), C=(900,2300), BD=(900,2300), V=(2000,3300), Xe=(2000,3300), Xm_metal=(3000,7500), Xm_sil=(2000,3500),
           Xp=(900,2300), other_chond=(1700,3400), other_poor=(2000,3300))        # uniform, kg/m3
P_HYD = dict(C=0.5, BD=0.5, Xp=0.3)                                               # chance of any hydrated minerals
WATER_MED, WATER_SIG = 0.06, math.log(13/2)/(2*1.645)                             # median 6 wt%, 90% range about 2-13 wt%
OC_MIX = (('H',0.25),('L',0.35),('LL',0.40))

def draw_usd_per_t(key, n):
    lo, hi = ROCK_USD[key]; return rng.uniform(lo, hi, n)

def simulate(H=None, D_med=None, D_sig=None, prior=PRIOR, rho_cap=None, label=''):
    names = list(prior); p = np.array([prior[k] for k in names]); p = p/p.sum()
    cls = rng.choice(len(names), N, p=p)
    D = np.empty(N); rho = np.empty(N); pgm = np.zeros(N); metal_pgm = np.zeros(N); water_t = np.zeros(N)
    for i, k in enumerate(names):
        m = cls == i; n = int(m.sum())
        if n == 0: continue
        if H is not None:
            alb = np.exp(rng.normal(math.log(ALB[k][0]), ALB[k][1], n)); alb = np.clip(alb, 0.02, 0.8)
            Hs = H + rng.normal(0, 0.4, n)                                       # catalogue H is good to roughly 0.3-0.5 mag
            D[m] = 1329e3*10**(-Hs/5)/np.sqrt(alb)
        else:
            D[m] = np.exp(rng.normal(math.log(D_med), D_sig, n))
        lo, hi = RHO[k]; r = rng.uniform(lo, hi, n)
        if rho_cap is not None:
            # keep only draws under the ceiling: resample within [lo, min(hi, cap)]; weight handled below
            r = rng.uniform(lo, min(hi, rho_cap), n)
        rho[m] = r
    mass_t = math.pi/6*D**3*rho/1000.
    w = np.ones(N)
    if rho_cap is not None:                                                       # reweight classes by the share of their density range under the cap
        for i, k in enumerate(names):
            lo, hi = RHO[k]; frac = max(0., (min(hi, rho_cap)-lo)/(hi-lo)); w[cls == i] = frac
    for i, k in enumerate(names):
        m = cls == i; n = int(m.sum())
        if n == 0: continue
        if k == 'OC':
            sub = rng.choice(3, n, p=[x[1] for x in OC_MIX]); v = np.empty(n)
            for j, (nm, _) in enumerate(OC_MIX):
                mm = sub == j; v[mm] = draw_usd_per_t(nm, int(mm.sum()))
            pgm[m] = mass_t[m]*v; metal_pgm[m] = pgm[m]
        elif k in ('C','BD','Xp'):
            v = np.where(rng.random(n) < 0.5, draw_usd_per_t('CI', n), draw_usd_per_t('CM', n)); pgm[m] = mass_t[m]*v
            hyd = rng.random(n) < P_HYD[k]; wf = np.exp(rng.normal(math.log(WATER_MED), WATER_SIG, n))
            water_t[m] = np.where(hyd, mass_t[m]*wf, 0.)
        elif k == 'Xm_sil':
            v = np.where(rng.random(n) < 0.5, draw_usd_per_t('EH', n), draw_usd_per_t('EL', n)); pgm[m] = mass_t[m]*v; metal_pgm[m] = pgm[m]
        elif k == 'Xm_metal':
            frac = rng.uniform(0.5, 1.0, n); v = iron_grade(n)*1e-3*BASKET*frac; pgm[m] = mass_t[m]*v; metal_pgm[m] = pgm[m]
        elif k == 'other_chond':
            v = draw_usd_per_t('L', n); pgm[m] = mass_t[m]*v; metal_pgm[m] = pgm[m]
        # V, Xe, other_poor: differentiated silicate, PGM taken as zero
    return dict(label=label, names=names, cls=cls, w=w/w.sum(), D=D, rho=rho, mass_t=mass_t, pgm=pgm, metal_pgm=metal_pgm, water_t=water_t)

def wq(x, w, qs):
    if len(x) == 0: return [float('nan')]*len(qs)
    o = np.argsort(x); cw = np.cumsum(w[o]); cw /= cw[-1]; return [float(x[o][np.searchsorted(cw, q)]) for q in qs]
QS = (0.05, 0.25, 0.5, 0.75, 0.95)
def fmt(v):
    for u, s in ((1e12,'T'),(1e9,'B'),(1e6,'M'),(1e3,'k')):
        if abs(v) >= u: return f"{v/u:.3g}{s}"
    return f"{v:.3g}"
def report(r):
    w = r['w']; print(f"\n=== {r['label']} ===")
    print("class weights after conditioning:", {k: round(float(w[r['cls']==i].sum()), 3) for i, k in enumerate(r['names'])})
    print("D m  5/25/50/75/95:", [round(v,1) for v in wq(r['D'], w, QS)])
    print("rho  5/25/50/75/95:", [round(v) for v in wq(r['rho'], w, QS)])
    print("mass t 5/25/50/75/95:", [fmt(v) for v in wq(r['mass_t'], w, QS)])
    for key, nm in (('pgm','S1 PGM in the ground, $ at 20 Nov 2026'), ('metal_pgm','S1b PGM held in metal grains, $')):
        x = r[key]; z = x <= 0; p0 = float(w[z].sum())
        q = wq(x[~z], w[~z]/w[~z].sum(), QS)
        print(f"{nm}: P(nothing)={p0:.3f}; if not nothing 5/25/50/75/95: {[fmt(v) for v in q]}; all-draw mean ${fmt(float((x*w).sum()))}")
    x = r['water_t']; z = x <= 0; p0 = float(w[z].sum()); q = wq(x[~z], w[~z]/max(w[~z].sum(), 1e-300), QS)
    print(f"S2 water in the ground, tonnes: P(nothing)={p0:.3f}; if not nothing 5/25/50/75/95: {[fmt(v) for v in q]}")
    for price in (500, 1000, 3000):
        print(f"   at ${price}/kg: {[fmt(v*1000*price) for v in q]}")
    mr = r['cls'] == r['names'].index('Xm_metal') if 'Xm_metal' in r['names'] else np.zeros(N, bool)
    if mr.any() and w[mr].sum() > 0:
        q = wq(r['pgm'][mr], w[mr]/w[mr].sum(), QS); print(f"   metal-rich branch only (weight {float(w[mr].sum()):.3f}): PGM $ {[fmt(v) for v in q]}")
    oc = r['cls'] == r['names'].index('OC')
    if oc.any(): q = wq(r['pgm'][oc], w[oc]/w[oc].sum(), QS); print(f"   ordinary-chondrite branch only (weight {float(w[oc].sum()):.3f}): PGM $ {[fmt(v) for v in q]}")

report(simulate(H=26.2, label='Example 1: H 26.2, nothing else measured'))
report(simulate(H=26.2, prior=dict(OC=1.0), label='Example 2: H 26.2, spectrum says S-type (ordinary-chondrite-like)'))
report(simulate(D_med=60., D_sig=0.26, label='Example 3a: measured size 60 m (+/-30%), class unknown, no density information'))
report(simulate(D_med=60., D_sig=0.26, rho_cap=5000., label='Example 3b: same, bulk density ceiling 5,000 kg/m3'))
# ---- sensitivities ----
print("\n== sensitivity of the chance of nothing (Example 1) ==")
for XE_, XM_, XP_ in ((0.15,0.31,0.53),(0.35,0.32,0.33),(0.56,0.33,0.11)):
    for ph in (0.3, 0.5, 0.77):
        pr = dict(PRIOR); pr.update(Xe=X*XE_, Xm_metal=X*XM_*METAL_GIVEN_M, Xm_sil=X*XM_*(1-METAL_GIVEN_M), Xp=X*XP_)
        P_HYD.update(C=ph, BD=ph)
        r = simulate(H=26.2, prior=pr); w = r['w']
        print(f"X split E/M/P {XE_}/{XM_}/{XP_}, P(hydrated|C)={ph}: P(no PGM at all)={float(w[r['pgm']<=0].sum()):.3f}  P(no PGM in metal)={float(w[r['metal_pgm']<=0].sum()):.3f}  P(no water)={float(w[r['water_t']<=0].sum()):.3f}")
P_HYD.update(C=0.5, BD=0.5)
print("\n== the same tag at other H (nothing else measured) ==")
for H in (24.0, 25.0, 26.2, 27.7, 29.0):
    r = simulate(H=H); x = r['metal_pgm']; z = x <= 0; q = wq(x[~z], r['w'][~z]/r['w'][~z].sum(), (0.05,0.5,0.95))
    x2 = r['water_t']; z2 = x2 <= 0; q2 = wq(x2[~z2], r['w'][~z2]/r['w'][~z2].sum(), (0.05,0.5,0.95))
    print(f"H={H}: mass t 5/50/95 {[fmt(v) for v in wq(r['mass_t'], r['w'], (0.05,0.5,0.95))]}; PGM in metal if any 5/50/95: {[fmt(v) for v in q]}; water t if any: {[fmt(v) for v in q2]}")
print("\n== price date sensitivity: multiply every PGM dollar figure by", round(BASKET25/BASKET, 2), "for 2025 average prices ==")
# ---- hand arithmetic used in the report ----
print("\n== hand arithmetic ==")
def sphere_t(D, rho): return math.pi/6*D**3*rho/1000
for D, rho in ((15,2500),(7.5,2500),(30,2500),(15,1700),(15,3400),(34.2,1400),(19.7,4500),(60,2500),(60,5000),(60,1400),(60,4500),(60,7500)):
    print(f"D={D} m rho={rho}: volume {math.pi/6*D**3:,.0f} m3, mass {sphere_t(D,rho):,.0f} t")
print("D from H=26.2 at albedo 0.25/0.05/0.15/0.45:", [round(1329e3*10**(-26.2/5)/math.sqrt(a),1) for a in (0.25,0.05,0.15,0.45)])
m60 = sphere_t(60, 4500)*0.75; 
for g in (14.70, 40.78, 107.86):
    kg = m60*g*1e-3; print(f"60 m metal-rich (4,500 kg/m3, 75% metal) at {g} ppm: {kg/1000:.1f} t PGM = ${kg*BASKET/1e9:.2f}B; by element t:", {k: round(kg/1000*CI[k]/s, 2) for k in CI}, "share of annual supply:", {k: f"{kg/1000*CI[k]/s/SUP[k]:.0%}" for k in SUP})
ret = 0.1216  # kg, OSIRIS-REx
print(f"121.6 g of median iron meteorite: {ret*40.78e-6*1e6:.2f} mg PGM = ${ret*40.78e-6*BASKET:.2f}; of H chondrite: ${ret/1000*ROCK_USD['H'][1]:.3f}; as water at 7 wt% and $3,000/kg: ${ret*0.07*3000:.2f}")
print("world PGM ore mined per year if 434 t at 3.86 g/t:", round(434e6/3.86/1e6), "Mt; a 4,400 t body is", round(4400/(434e6/3.86)*365*24*60, 1), "minutes of that")

# ---- response to a class observation (H 26.2) ----
print("\n== response to a class observation, H 26.2 ==")
cases = {
 'C-complex spectrum': dict(C=1.0),
 'X-complex spectrum, no albedo': dict(Xe=XE, Xm_metal=XM*METAL_GIVEN_M, Xm_sil=XM*(1-METAL_GIVEN_M), Xp=XP),
 'X-complex, albedo 0.1-0.3 (M)': dict(Xm_metal=METAL_GIVEN_M, Xm_sil=1-METAL_GIVEN_M),
}
for lab, pr in cases.items():
    r = simulate(H=26.2, prior=pr); w = r['w']
    x = r['metal_pgm']; z = x <= 0; q = wq(x[~z], w[~z]/max(w[~z].sum(),1e-300), QS)
    x2 = r['water_t']; z2 = x2 <= 0; q2 = wq(x2[~z2], w[~z2]/max(w[~z2].sum(),1e-300), QS)
    print(f"{lab}: D 5/50/95 {[round(v,1) for v in wq(r['D'], w, (0.05,0.5,0.95))]}; mass t {[fmt(v) for v in wq(r['mass_t'], w, (0.05,0.5,0.95))]}")
    print(f"   PGM in metal: P(nothing)={float(w[z].sum()):.2f}; if any 5/25/50/75/95 {[fmt(v) for v in q]}")
    print(f"   water t: P(nothing)={float(w[z2].sum()):.2f}; if any 5/25/50/75/95 {[fmt(v) for v in q2]}")
# measured size +/-10% and S-type
r = simulate(D_med=15., D_sig=0.10, prior=dict(OC=1.0)); x = r['metal_pgm']
print("S-type with size measured to 10% (15 m): PGM 5/25/50/75/95", [fmt(v) for v in wq(x, r['w'], QS)], " width dex", round(math.log10(wq(x, r['w'], (0.95,))[0]/wq(x, r['w'], (0.05,))[0]), 2))
r = simulate(H=26.2, prior=dict(OC=1.0)); x = r['metal_pgm']; print("S-type from H only: width dex", round(math.log10(wq(x, r['w'], (0.95,))[0]/wq(x, r['w'], (0.05,))[0]), 2))
r = simulate(H=26.2); x = r['metal_pgm']; z = x > 0; print("unmeasured: width dex", round(math.log10(wq(x[z], r['w'][z]/r['w'][z].sum(), (0.95,))[0]/wq(x[z], r['w'][z]/r['w'][z].sum(), (0.05,))[0]), 2))
