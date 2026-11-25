"""Sequential, cached fetch of MPC ADES XML (one request per designation) and JPL SBDB records (one at a time).
usage: fr_fetch.py "<des1>" "<des2>" ...   (prefix a designation with 'mpc:' or 'sbdb:' to fetch only one source)
"""
import sys, os, importlib.util, time
spec = importlib.util.spec_from_file_location("fr_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_common.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)

for arg in sys.argv[1:]:
    src, des = ("both", arg)
    if ":" in arg:
        src, des = arg.split(":", 1)
    line = [des]
    if src in ("both", "mpc"):
        try:
            p, new, dt = C.fetch_mpc_xml(des)
            txt = open(p).read()
            line.append("MPC %s %d bytes, %d optical, %d radar, %.2fs%s" % ("fetched" if new else "cached", len(txt),
                        txt.count("<optical>"), txt.count("<radar>"), dt, " sha256=" + C.sha256(p)[:16]))
        except Exception as e:
            line.append("MPC ERROR " + repr(e)[:200])
    if src in ("both", "sbdb"):
        try:
            d, new, dt = C.fetch_sbdb(des)
            el, cm, ng, meta = C.parse_sbdb(d)
            line.append("SBDB %s %.2fs H=%s arc=%s n_obs=%s cond=%s soln=%s epoch=%.1f model=%s sig=%s" % (
                "fetched" if new else "cached", dt, meta["H"], meta["data_arc"], meta["n_obs_used"], meta["condition_code"],
                meta["soln_date"], el["t"], {k: v for k, v in meta["model_pars"].items()}, meta["model_sig"]))
        except Exception as e:
            line.append("SBDB ERROR " + repr(e)[:200])
    print(" | ".join(line), flush=True)
