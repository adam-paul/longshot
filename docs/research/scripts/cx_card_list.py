"""Build the priority-ordered list of NHATS objects whose ssoCards are worth fetching.
Usage: python3 -I cx_card_list.py <catalogs_dir> <sizes_local.json> <out_list.txt>
Order: (1) NHATS with A1|A2; (2) NHATS with a thermal-table size, SBDB diameter or radar astrometry;
(3) NHATS delta-v < 5; (4) NHATS delta-v < 6; (5) NHATS with SBDB rot_per; (6) NHATS numbered objects."""
import sys, os, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cx_lib import Universe, load_nhats

CAT, SIZES, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
U = Universe(os.path.join(CAT, 'sbdb_neo.json'))
nh = load_nhats(os.path.join(CAT, 'nhats.json'))
sz = json.load(open(SIZES))
order = []
seen = set()


def add(ps, label):
    n = 0
    for p in ps:
        if p not in seen:
            seen.add(p)
            order.append(p)
            n += 1
    print('%-45s +%d (total %d)' % (label, n, len(order)))


bydv = sorted(nh, key=lambda d: nh[d]['dv'])
add([p for p in bydv if sz[p]['A1'] or sz[p]['A2']], 'NHATS with A1|A2')
add([p for p in bydv if sz[p]['sbdb'] or sz[p]['spitzer'] or sz[p]['neowise'] or sz[p]['radar_astrom']], 'NHATS thermal/SBDB diam/radar')
add([p for p in bydv if nh[p]['dv'] < 5], 'NHATS dv<5')
add([p for p in bydv if nh[p]['dv'] < 6], 'NHATS dv<6')
add([p for p in bydv if U.by_pdes[p]['rot_per'] not in (None, '')], 'NHATS with SBDB rot_per')
add([p for p in bydv if p.isdigit()], 'NHATS numbered')
open(OUT, 'w').write('\n'.join(order) + '\n')
