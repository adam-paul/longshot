#!/usr/bin/env python3
"""nr_sbdb_ng.py SBDB_JSON NHATS_JSON : counts of non-gravitational parameters among NEOs in the SBDB snapshot (read-only)."""
import sys, json
sb = json.load(open(sys.argv[1])); nh = json.load(open(sys.argv[2]))
if isinstance(sb, dict) and 'fields' in sb:
    F = sb['fields']; rows = [dict(zip(F, r)) for r in sb['data']]
else:
    rows = sb
nd = nh['data'] if isinstance(nh, dict) else nh
nhset = {d['des'] for d in nd}
def f(x):
    try: return float(x)
    except Exception: return None
print('NEO rows', len(rows), 'NHATS', len(nhset))
ast = [r for r in rows if str(r.get('kind','')).startswith('a')]
print('asteroid-kind rows', len(ast))
for p in ('A1','A2','A3'):
    have = [r for r in ast if f(r.get(p)) is not None]
    sig3 = [r for r in have if f(r.get(p+'_sigma')) and abs(f(r[p]))/f(r[p+'_sigma']) >= 3]
    innh = [r for r in have if (r.get('pdes') in nhset)]
    print(p, 'asteroids with value', len(have), '>=3sigma', len(sig3), 'in NHATS', len(innh))
a1 = [r for r in ast if f(r.get('A1')) is not None]
print('\nNEO asteroids with A1 (des, H, A1, sigma, SNR, AMR m2/kg assuming C_R=1 -> A1/2.266e-7... using a_rad = A1*(1au/r)^2):')
for r in sorted(a1, key=lambda r: -(f(r.get('H')) or 0)):
    A1 = f(r['A1']); s = f(r.get('A1_sigma'))
    # AMR = A1[au/d^2] / (phi/c at 1 au in au/d^2 per (m2/kg)); phi/c = 4.56e-6 N/m2 -> 4.56e-6 m/s2 per (m2/kg) = 2.275e-7 au/d2
    amr = A1/2.275e-7
    print(f"  {r.get('pdes'):>12} H={r.get('H')} A1={A1:.3e} sig={s} SNR={(abs(A1)/s if s else float('nan')):.1f} AMR~{amr:.2e} m2/kg  A2={r.get('A2')} A3={r.get('A3')} NHATS={'Y' if r.get('pdes') in nhset else 'n'} arc={r.get('data_arc')}")
