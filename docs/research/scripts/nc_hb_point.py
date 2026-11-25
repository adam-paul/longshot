#!/usr/bin/env python3
"""Print the harmonic-balance J for given local Theta values (imports nc_nonlinear helpers). Run with python -I."""
import sys, importlib.util
spec = importlib.util.spec_from_file_location("ncn", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for th in [float(v) for v in sys.argv[2:]]:
    J, u, me = m.J_of(th)
    print("Theta_loc = %.3f : J (harmonic balance) = %.5f" % (th, J))
