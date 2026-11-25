import csv, sys, json, math, statistics as st
sp = sys.argv[1]; base = sys.argv[2]
rows = list(csv.DictReader(open(sp)))
def f(x):
    try: return float(x)
    except: return None
nh = {o["des"] for o in json.load(open(base + "/nhats.json"))["data"]}
def summarize(label, sel):
    pv = sorted(f(r["pv"]) for r in sel if f(r["pv"]) is not None)
    if not pv: print(label, "none"); return
    n = len(pv)
    ratio = sorted(math.sqrt(0.14/p) for p in pv)  # true D / nominal D(0.14)
    q = lambda v, p: v[min(len(v)-1, int(p*len(v)))]
    d1 = [ (f(r["d1sigu"]) - f(r["d1sigl"]))/2/f(r["diam"]) for r in sel if f(r["diam"]) and f(r["d1sigu"]) is not None and f(r["d1sigl"]) is not None]
    print("%s: n=%d median pV %.2f (16-84%%: %.2f-%.2f); dark(<0.10) %.0f%%; pV>0.5: %.0f%%; D_true/D_nominal(0.14): median %.2f, 5-95%%: %.2f-%.2f; median frac 1-sigma D error %.2f" % (
        label, n, q(pv,0.5), q(pv,0.16), q(pv,0.84), 100*sum(1 for p in pv if p<0.10)/n, 100*sum(1 for p in pv if p>0.5)/n, q(ratio,0.5), q(ratio,0.05), q(ratio,0.95), st.median(d1) if d1 else float("nan")))
allr = [r for r in rows if f(r["absmag"]) is not None]
summarize("all Spitzer", allr)
summarize("a<2", [r for r in allr if f(r["a"]) and f(r["a"])<2])
for lo, hi in ((0,20),(20,22),(22,24),(24,40)):
    summarize("H %d-%d" % (lo,hi), [r for r in allr if lo <= f(r["absmag"]) < hi])
def des(r):
    return r["number"] if r["number"] and r["number"] in nh else r["desig"]
summarize("NHATS members", [r for r in allr if des(r) in nh or r["desig"] in nh])
summarize("NHATS members H>=22", [r for r in allr if (des(r) in nh or r["desig"] in nh) and f(r["absmag"])>=22])
for r in allr:
    if r["desig"] in ("2001 CQ36",) or r["number"] in ("613862",):
        print(r["desig"], r["number"], "H", r["absmag"], "D", r["diam"], r["d1sigl"], r["d1sigu"], "pv", r["pv"], r["pv1sigl"], r["pv1sigu"], "eta", r["eta"], "snr", r["ch2snr"])
