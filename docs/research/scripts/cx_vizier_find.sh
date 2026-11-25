#!/bin/bash
# Find VizieR catalogue names by keyword on the CfA mirror (sequential, 3 s pause, retries the intermittent
# "database is not currently reachable" answer up to 4 times).
# Usage: cx_vizier_find.sh <out_dir> <word> [<word> ...]
out="$1"; shift
mkdir -p "$out"
for w in "$@"; do
  f="$out/meta_$(echo "$w" | tr ' /' '__').tsv"
  for try in 1 2 3 4; do
    curl -sS --max-time 120 -G -o "$f" --data-urlencode "-meta" --data-urlencode "-words=$w" --data-urlencode "-meta.max=400" "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv"
    if grep -q 'not currently reachable' "$f"; then sleep 5; else break; fi
  done
  echo "== $w (try $try)"
  grep -E '^#(Name|Title)' "$f" | paste - - | sed 's/#Name: //; s/#Title: //' | cut -c1-150
  sleep 3
done
