import json, sys
base = sys.argv[1]
n = json.load(open(base + "/nhats.json"))
print(type(n), list(n.keys())[:10] if isinstance(n, dict) else len(n))
d = n["data"] if isinstance(n, dict) and "data" in n else n
print(len(d))
print(json.dumps(d[0], indent=1)[:1500])
s = json.load(open(base + "/sbdb_neo.json"))
print(type(s), list(s.keys())[:10] if isinstance(s, dict) else len(s))
if isinstance(s, dict):
    print(s.get("fields"))
    print(len(s["data"]), s["data"][0])
