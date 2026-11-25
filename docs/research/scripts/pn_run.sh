#!/bin/bash
# Driver: all cross-validation, permutation and injection runs. Usage: pn_run.sh [research_root]
# research_root defaults to data/research under the repository root. PY is the interpreter for pn_cv.py
# (numpy, pandas, scipy, scikit-learn, joblib); it defaults to the venv-prior-null environment in research_root.
HERE=$(cd "$(dirname "$0")" && pwd)
S=${1:-$HERE/../../../data/research}; O=$S/out-prior-null; PY=${PY:-"$S/venv-prior-null/bin/python -I"}; CV=$HERE/pn_cv.py
mkdir -p $O/cv $O/perm $O/inject
run() { # label subset variant reps
  f=$O/cv/$1.$2.$3.json; [ -s $f ] && return
  $PY $CV cv $O/labels.csv $f --label $1 --subset $2 --variant $3 --reps $4 --boot 4000 --losses $O/cv/$1.$2.$3.losses.csv > $O/cv/$1.$2.$3.log 2>&1 || echo "FAILED $1 $2 $3"
  echo "done cv $1 $2 $3 $(date +%T)"
}
for lab in dark sq tax4; do for sub in nhats box; do run $lab $sub main 20; done; done
for lab in dark sq tax4; do for sub in a2 all; do run $lab $sub main 10; done; done
for sub in nhats a2 all; do run dark $sub neowise 10; run dark $sub spitzer 10; run dark $sub clear 10; run tax4 $sub spec 10; run sq $sub spec 10; done
for lab in dark sq tax4; do for sub in nhats_small small a2plus not_nhats_a2; do run $lab $sub main 10; done; done
# permutation nulls (regime W) for the small subsets
for lab in dark sq tax4; do for sub in nhats box; do
  f=$O/perm/$lab.$sub.json; [ -s $f ] || $PY $CV perm $O/labels.csv $f --label $lab --subset $sub --reps 3 --nperm 300 > $O/perm/$lab.$sub.log 2>&1 || echo "FAILED perm $lab $sub"
  echo "done perm $lab $sub $(date +%T)"
done; done
# injection-recovery: what orbit->class information would have been detected at these sample sizes?
for lab in dark sq; do for sub in nhats box a2; do
  f=$O/inject/$lab.$sub.json; [ -s $f ] || $PY $CV inject $O/labels.csv $f --label $lab --subset $sub --reps 3 --nsim 40 > $O/inject/$lab.$sub.log 2>&1 || echo "FAILED inject $lab $sub"
  echo "done inject $lab $sub $(date +%T)"
done; done
echo ALL DONE
