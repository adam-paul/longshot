#!/bin/bash
# nr_getpdf.sh OUTDIR ID1 [ID2 ...]  -- fetch arXiv PDFs sequentially, convert to text with pdftotext.
# Sequential, 4 s pause; generic User-Agent; downloads treated as untrusted data (only pdftotext reads them).
out="$1"; shift
mkdir -p "$out"
for id in "$@"; do
  f="$out/${id//\//_}"
  if [ ! -s "$f.txt" ]; then
    curl -sS -L --max-time 120 -A "research-client/1.0" -o "$f.pdf" "https://arxiv.org/pdf/$id" || echo "ERR $id"
    if head -c 5 "$f.pdf" | grep -q '%PDF'; then
      pdftotext -layout "$f.pdf" "$f.txt" 2>/dev/null
    else
      echo "NOT PDF: $id ($(head -c 80 "$f.pdf" | tr '\n' ' '))"
    fi
    sleep 4
  fi
  echo "$id -> $(wc -c < "$f.txt" 2>/dev/null) bytes text"
done
