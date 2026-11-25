import json, sys
c = json.load(open(sys.argv[1]))
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
    else:
        if o not in (None, "", [], {}):
            pl = path.lower()
            if any(w in pl for w in ("spin", "taxonomy", "albedo", "diameter", "yarkovsky", "density", "absolute_magnitude/value", "thermal")):
                print(path, "=", o)
walk(c)
