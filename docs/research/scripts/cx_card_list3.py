"""Reordered ssoCard fetch list: (1) A1|A2 + thermal/SBDB/radar NHATS objects, (2) NHATS objects with C51 astrometry from
the MPC census, (3) all NHATS delta-v < 6, (4) the seeded random sample of unflagged delta-v >= 6 objects, (5) the rest.
Usage: python3 -I cx_card_list3.py <cx_dir>   (reads card_list_2.txt, mpc/c51_census.jsonl, card_sample.txt; writes card_list_3.txt)"""
import sys, os, json

D = sys.argv[1]
l2 = [l.strip() for l in open(os.path.join(D, 'card_list_2.txt')) if l.strip()]
c51 = [json.loads(l)['des'] for l in open(os.path.join(D, 'mpc', 'c51_census.jsonl')) if json.loads(l).get('n_c51')]
samp = [l.strip() for l in open(os.path.join(D, 'card_sample.txt')) if l.strip()]
head, tail = l2[:452], l2[452:]      # 174 A1|A2 + 278 thermal/SBDB/radar
dv6, rest = tail[:676], tail[676:]   # 261 (dv<5) + 415 (dv<6)
order, seen = [], set()
for grp in (head, c51, dv6, samp, rest):
    for p in grp:
        if p not in seen:
            seen.add(p)
            order.append(p)
open(os.path.join(D, 'card_list_3.txt'), 'w').write('\n'.join(order) + '\n')
print(len(order), 'head', len(head), 'c51', len(c51), 'dv6', len(dv6), 'sample', len(samp), 'rest', len(rest))
