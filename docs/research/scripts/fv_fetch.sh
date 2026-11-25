#!/bin/bash
# fv_fetch.sh OUTDIR NAME URL [NAME URL ...]  -- sequential, polite fetch; saves body, headers, status
OUT="$1"; shift
UA="Mozilla/5.0 (X11; Linux x86_64) research-factcheck/1.0"
while [ $# -ge 2 ]; do
  NAME="$1"; URL="$2"; shift 2
  code=$(curl -sS -L --max-time 60 --compressed -A "$UA" -D "$OUT/$NAME.hdr" -o "$OUT/$NAME.body" -w '%{http_code} %{url_effective} %{size_download}' "$URL" 2>"$OUT/$NAME.err")
  echo "$NAME $code"
  sleep 1.5
done
