#!/usr/bin/env python3
"""nr_grep.py FILE.txt PATTERN [PATTERN...] [--w N] [--max M]
Print context windows (N chars each side, default 350) around regex matches in a text file; at most M per pattern (default 4)."""
import sys, re
args = sys.argv[1:]
w, mx = 350, 4
if '--w' in args:
    i = args.index('--w'); w = int(args[i+1]); del args[i:i+2]
if '--max' in args:
    i = args.index('--max'); mx = int(args[i+1]); del args[i:i+2]
txt = open(args[0], encoding='utf-8', errors='replace').read()
txt = re.sub(r'[ \t]+', ' ', txt)
txt = re.sub(r'\n\s*\n+', '\n', txt)
for p in args[1:]:
    ms = list(re.finditer(p, txt, flags=re.I))
    print(f'##### /{p}/ : {len(ms)} matches')
    last = -10**9
    n = 0
    for m in ms:
        if m.start() - last < w:
            continue
        last = m.start(); n += 1
        if n > mx: break
        s = txt[max(0, m.start()-w): m.end()+w].replace('\n', ' ')
        print(f'  [{m.start()}] ...{s}...\n')
