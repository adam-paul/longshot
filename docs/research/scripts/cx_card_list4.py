"""Fourth ssoCard list: every NHATS object that carries any table flag (taxonomy, colours, albedo, diameter, density,
rotation period, A1/A2, radar astrometry) and has not been requested yet. After this list is fetched, the only NHATS
objects without a card request are those with no flag in any table, which the seeded random sample represents.
Usage: python3 -I cx_card_list4.py <cx_dir>   (reads table_flags.json, cards/_status.tsv, catalogs via ../catalogs)"""
import sys, os, json

D = sys.argv[1]
T = json.load(open(os.path.join(D, 'table_flags.json')))
nh = {r['des'] for r in json.load(open(os.path.join(os.path.dirname(D.rstrip('/')), 'catalogs', 'nhats.json')))['data']}
status = {l.split('\t')[0] for l in open(os.path.join(D, 'cards', '_status.tsv'))}
prev = set()
for fn in ('card_list_2.txt',):
    prev |= {l.strip() for l in open(os.path.join(D, fn)) if l.strip()}
todo = sorted(p for p in nh if any(T[p][k] for k in ('tax', 'col', 'alb', 'diam', 'dens', 'rot', 'yark', 'a1', 'radar')) and p not in prev)
open(os.path.join(D, 'card_list_4.txt'), 'w').write('\n'.join(todo) + '\n')
print('flagged NHATS objects not in the earlier targeted list:', len(todo), '| of which already requested (e.g. via the sample):', sum(1 for p in todo if p in status))
