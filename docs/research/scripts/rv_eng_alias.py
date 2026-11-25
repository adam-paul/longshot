import json, sys, re
nh = json.load(open(sys.argv[1]))["data"]
sbj = json.load(open(sys.argv[2]))
F = sbj["fields"]; ix = {f:i for i,f in enumerate(F)}
sb = {r[ix["pdes"]]: r for r in sbj["data"]}
r = sb.get("883607")
print("883607:", r and (r[ix["full_name"]], r[ix["class"]], r[ix["A2"]], r[ix["A2_sigma"]], r[ix["q"]], r[ix["neo"]]))
print("883607 in NHATS:", any(o["des"]=="883607" for o in nh))
# plan's named objects: do they resolve by the string the plan uses?
plan_names = ["2011 AA37","2022 OB5","1998 KY26","2022 RD2","2016 TA56","2015 BM510","2009 BD","2011 MD","2020 CD3","2024 PT5"]
for n in plan_names:
    print(n, "pdes hit" if n in sb else "pdes MISS", "| full_name hit:", [x[ix["pdes"]] for x in sbj["data"] if "("+n+")" in x[ix["full_name"]]][:2])
# numbered NHATS objects whose full_name carries a provisional alias
num = [o for o in nh if re.fullmatch(r"\d+", o["des"])]
with_alias = sum(1 for o in num if re.search(r"\(\d{4} [A-Z]{2}\d*\)", sb[o["des"]][ix["full_name"]]))
print("numbered NHATS:", len(num), "with provisional alias in full_name:", with_alias)
# numbers above 800000 = numbered recently (approx): how many NHATS numbered objects have number > 700000
print("NHATS numbered > 700000:", sum(1 for o in num if int(o["des"])>700000), "> 850000:", sum(1 for o in num if int(o["des"])>850000))
print("max number in SBDB NEO:", max(int(k) for k in sb if k.isdigit()))
