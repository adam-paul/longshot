#!/bin/bash
# Sequentially fetch whole VizieR catalogues (all tables, all columns) from the CfA mirror as TSV.
# Usage: cx_fetch_vizier.sh <out_dir> <catalogue> [<catalogue> ...]     e.g. J/ApJ/743/156
# One request at a time, 3 s pause. Existing good files are skipped. A response carrying "#INFO Error=" is
# retried up to 3 times (the mirror intermittently reports "database is not currently reachable"), then kept
# as <name>.err so a later run tries again.
out="$1"; shift
mkdir -p "$out"
for cat in "$@"; do
  fn="$out/$(echo "$cat" | tr '/+' '__').tsv"
  if [ -s "$fn" ]; then echo "have $cat"; continue; fi
  for try in 1 2 3; do
    code=$(curl -sS --max-time 240 -G -o "$fn.part" -w '%{http_code} %{size_download}' \
      --data-urlencode "-source=$cat" --data-urlencode "-out.max=unlimited" --data-urlencode "-out.all=1" \
      "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv")
    if grep -q '^#INFO.Error=' "$fn.part" 2>/dev/null || ! grep -q '^#Name: .' "$fn.part" 2>/dev/null; then
      echo "$cat try $try -> $code ERROR: $(grep -m1 'Error=' "$fn.part" | cut -c1-90)"
      mv "$fn.part" "$fn.err"
      grep -q 'not found' "$fn.err" && break
      sleep 6
    else
      mv "$fn.part" "$fn"; rm -f "$fn.err"
      echo "$cat -> $code $(grep -c '' "$fn") lines; tables: $(grep '^#Name:' "$fn" | sed 's/#Name: //' | tr '\n' ' ')"
      break
    fi
  done
  sleep 3
done
