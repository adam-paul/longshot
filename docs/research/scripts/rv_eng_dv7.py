import json, sys
nh = json.load(open(sys.argv[1]))["data"]
dv = lambda o: float(o["min_dv"]["dv"])
for lim in (4,4.5,5,5.5,6,7,8,10):
    print(lim, sum(dv(o)<lim for o in nh), sum(dv(o)<=lim for o in nh))
print("dv in [6.99,7.01]:", sorted((o["min_dv"]["dv"], o["des"], o["h"]) for o in nh if 6.99<=dv(o)<=7.01))
print("null-H under 7:", [(o["des"], o["min_dv"]["dv"]) for o in nh if o["h"] in (None,"") and dv(o)<7])
print("null-H all:", [(o["des"], o["min_dv"]["dv"], o["occ"]) for o in nh if o["h"] in (None,"")])
# also check min_dur dv
print("min over both dv fields <7:", sum(min(dv(o), float(o["min_dur"]["dv"]))<7 for o in nh))
# size of per-object JSON-ish
import statistics
print("bytes per NHATS row json median:", statistics.median(len(json.dumps(o)) for o in nh))
