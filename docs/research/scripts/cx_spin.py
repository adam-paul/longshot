"""Item 2 (spin): rotation-period coverage and fast-rotator fractions versus H, for NHATS and all NEAs.
Usage: python cx_spin.py <catalogs_dir> <coverage_exact_dir> [cards_dir]
Sources: SBDB rot_per (local snapshot), LCDB summary (2023-10-01 release), Thirouin+2016/2018 (VizieR), and, when a
cards_dir is given, the 'spins' entries of SsODNet ssoCards fetched for a subset of NHATS.
Period convention: hours. Spin barrier 2.2 h; 'super-fast' < 10 min = 0.1667 h."""
import sys, os, re, json, glob, collections
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats, parse_vizier, norm

CAT, CX = sys.argv[1], sys.argv[2]
CARDS = sys.argv[3] if len(sys.argv) > 3 else None
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))


def fl(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


H = {s['pdes']: fl(s['H']) for s in U.rows}
sb = {s['pdes']: fl(s['rot_per']) for s in U.rows if fl(s['rot_per'])}

# ---- LCDB summary ----
lines = open(os.path.join(CX, 'lcdb', 'x', 'lc_summary_pub.txt'), errors='replace').read().split('\n')
hi = next(i for i, l in enumerate(lines) if l.startswith('NUMBER'))
hdr = lines[hi]


def col(name):
    return [m.start() for m in re.finditer(r'(?<![A-Z0-9.])' + re.escape(name) + r'(?![A-Z0-9.])', hdr)][0]


c_name, c_des, c_fam, c_per, c_desc, c_u, c_notes = col('NAME'), col('DESIG'), col('FAM'), col('PERIOD'), col('P DESC'), col('U'), col('NOTES')
lc = {}
lc_rows = lc_per_rows = 0
for l in lines[hi + 2:]:
    if len(l) < c_u:
        continue
    lc_rows += 1
    num = l[:c_name].strip()
    name = l[c_name:c_des].strip()
    des = l[c_des:c_fam].strip()
    pflag = l[c_per - 2:c_per].strip()
    pv = fl(l[c_per:c_desc].strip())
    u = l[c_u:c_notes].strip()
    if not pv:
        continue
    lc_per_rows += 1
    p = U.by_number(num) if num.isdigit() and int(num) > 0 else None
    if p is None:
        p = U.resolve(des, name)
    if p:
        lc[p] = (pv, u, pflag)
print('LCDB summary rows', lc_rows, 'with a period', lc_per_rows, '| NEAs matched with period', len(lc),
      '| with U>=2', sum(1 for v in lc.values() if v[1][:1] in '23' and v[1][:1]))

# ---- Thirouin (MANOS) ----
th = {}
V = os.path.join(CX, 'vizier')
for fn, tn, pc, lc_ in (('J_AJ_152_163.tsv', 'J/AJ/152/163/table1', 'Per', 'l_Per'), ('J_ApJS_239_4.tsv', 'J/ApJS/239/4/table1', 'Prot', 'l_Prot')):
    path = os.path.join(V, fn)
    if not os.path.exists(path):
        print('missing', fn)
        continue
    rows = parse_vizier(path)[tn]
    nm = 0
    for r in rows:
        p = U.resolve(r['Name'])
        if not p:
            continue
        nm += 1
        th.setdefault(p, []).append((fl(r[pc]), (r.get(lc_) or '').strip(), fn[:8]))
    print(tn, 'rows', len(rows), 'matched', nm)
th_full = {p: min(x[0] for x in e if x[0] and not x[1]) for p, e in th.items() if any(x[0] and not x[1] for x in e)}
print('Thirouin objects', len(th), 'with full period', len(th_full), '| NHATS observed', sum(1 for p in th if p in nh), 'NHATS with full period', sum(1 for p in th_full if p in nh))

# ---- ssoCards ----
card = {}
card_have = set()
card_bib = collections.Counter()
if CARDS:
    for fn in glob.glob(os.path.join(CARDS, '*.json')):
        if os.path.basename(fn).startswith('_'):
            continue
        try:
            c = json.load(open(fn))
        except Exception:  # noqa: BLE001
            continue
        if 'parameters' not in c:
            continue
        p = None
        if c.get('number'):
            p = U.by_number(c['number'])
        if p is None:
            p = U.key2p.get(norm(str(c.get('name') or ''))) or U.key2p.get(norm(str(c.get('id') or '')))
        if not p:
            continue
        card_have.add(p)
        spins = ((c['parameters'].get('physical') or {}).get('spins')) or []
        if isinstance(spins, dict):
            spins = list(spins.values()) if all(isinstance(v, dict) for v in spins.values()) else [spins]
        pers = []
        for s in spins:
            if not isinstance(s, dict):
                continue
            per = s.get('period')
            v = fl(per.get('value')) if isinstance(per, dict) else fl(per)
            if v:
                pers.append(v)
                for b in (s.get('bibref') or []) if isinstance(s.get('bibref'), list) else [s.get('bibref')]:
                    if isinstance(b, dict):
                        card_bib[b.get('shortbib')] += 1
        if pers:
            card[p] = pers
    print('ssoCards read', len(card_have), 'with >=1 spin period', len(card), '| top spin refs', card_bib.most_common(8))

# ---- combine ----
BAR, SF = 2.2, 10.0 / 60.0


def best(p, mode):
    """mode 'sbdb': SBDB only; 'lcdb2': LCDB U>=2 only; 'any': LCDB U>=2, else SBDB, else LCDB any, else Thirouin full, else card (min)."""
    if mode == 'sbdb':
        return sb.get(p)
    if mode == 'lcdb2':
        v = lc.get(p)
        return v[0] if v and v[1][:1] in ('2', '3') else None
    v = lc.get(p)
    if v and v[1][:1] in ('2', '3'):
        return v[0]
    if p in sb:
        return sb[p]
    if v:
        return v[0]
    if p in th_full:
        return th_full[p]
    if p in card:
        return sorted(card[p])[len(card[p]) // 2] if len(card[p]) > 2 else card[p][0]
    return None


BINS = [(-99, 18), (18, 20), (20, 22), (22, 24), (24, 26), (26, 28), (28, 99)]


def report(scope_name, plist, mode):
    print('\n== %s | source=%s' % (scope_name, mode))
    print('%-9s %6s %6s %8s %10s %10s %10s %10s' % ('H bin', 'N', 'N_per', 'frac_per', 'P<2.2h', 'P<10min', 'P>=1h', 'median_P_h'))
    tot = [0, 0, 0, 0]
    for lo, hi_ in BINS + [(-99, 99)]:
        ps = [p for p in plist if H.get(p) is not None and lo <= H[p] < hi_]
        per = [best(p, mode) for p in ps]
        per = [x for x in per if x]
        nb = sum(1 for x in per if x < BAR)
        ns = sum(1 for x in per if x < SF)
        n1 = sum(1 for x in per if x >= 1.0)
        med = sorted(per)[len(per) // 2] if per else float('nan')
        lab = 'all' if lo == -99 and hi_ == 99 else ('<%d' % hi_ if lo == -99 else ('>=%d' % lo if hi_ == 99 else '%d-%d' % (lo, hi_)))
        print('%-9s %6d %6d %7.1f%% %4d %4.0f%% %4d %4.0f%% %4d %4.0f%% %10.3f' % (lab, len(ps), len(per), 100.0 * len(per) / max(1, len(ps)), nb, 100.0 * nb / max(1, len(per)), ns, 100.0 * ns / max(1, len(per)),
                                                                             n1, 100.0 * n1 / max(1, len(per)), med))


allp = [s['pdes'] for s in U.rows]
nhl = list(nh)
for mode in ('sbdb', 'lcdb2', 'any'):
    report('NHATS (%d)' % len(nhl), nhl, mode)
for mode in ('sbdb', 'any'):
    report('all NEAs (%d)' % len(allp), allp, mode)
report('NHATS dv<6', [p for p in nhl if nh[p]['dv'] < 6], 'any')
report('NHATS dv<5', [p for p in nhl if nh[p]['dv'] < 5], 'any')

print('\ncounts: NHATS with SBDB rot_per', sum(1 for p in nhl if p in sb), '| LCDB any', sum(1 for p in nhl if p in lc), '| LCDB U>=2', sum(1 for p in nhl if best(p, 'lcdb2')),
      '| Thirouin full', sum(1 for p in nhl if p in th_full), '| card spins', sum(1 for p in nhl if p in card), '| union', sum(1 for p in nhl if best(p, 'any')))
print('NHATS with a period in SBDB but not LCDB:', sum(1 for p in nhl if p in sb and p not in lc), '| in LCDB not SBDB:', sum(1 for p in nhl if p in lc and p not in sb))
if card_have:
    sub = [p for p in nhl if p in card_have]
    print('Among %d NHATS with a card fetched: card spin %d, SBDB %d, LCDB %d, card-only (not SBDB/LCDB/Thirouin) %d' % (
        len(sub), sum(1 for p in sub if p in card), sum(1 for p in sub if p in sb), sum(1 for p in sub if p in lc),
        sum(1 for p in sub if p in card and p not in sb and p not in lc and p not in th_full)))
    dis = [(p, sb.get(p), lc.get(p, (None,))[0], card[p]) for p in sub if p in card and p in sb and min(abs(sb[p] - x) / sb[p] for x in card[p]) > 0.2]
    print('card vs SBDB period disagreement >20%:', len(dis), dis[:8])
json.dump({p: {'H': H.get(p), 'nhats': p in nh, 'P_any': best(p, 'any'), 'P_sbdb': sb.get(p), 'P_lcdb': lc.get(p), 'P_card': card.get(p)} for p in allp if best(p, 'any')},
          open(os.path.join(CX, 'spin_periods.json'), 'w'))
