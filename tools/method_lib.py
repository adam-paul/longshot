"""Shared helpers for the tools/method_*.py scripts, which derive the constants in method/v0_1/*.toml.

Run each script from the repository root, isolated from the data folders:

    uv run python -I tools/method_reflectivity.py
    uv run python -I tools/method_spin.py
    uv run python -I tools/method_class.py
    uv run python -I tools/method_missions.py

Each prints a report and writes the same text to method/v0_1/derivation/<name>.txt. No network, no clock,
no random draws. Standard library only.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from longshot import config  # noqa: E402

DERIVATION = os.path.join(str(config.METHOD_DIR), "derivation")

H_BANDS = (
    ("under_20", -99.0, 20.0),
    ("20_22", 20.0, 22.0),
    ("22_24", 22.0, 24.0),
    ("24_26", 24.0, 26.0),
    ("26_28", 26.0, 28.0),
    ("28_up", 28.0, 99.0),
)


def band_of(h):
    """The id of the H band holding h, or None."""
    if h is None:
        return None
    for name, lo, hi in H_BANDS:
        if lo <= h < hi:
            return name
    return None


def fl(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def quantile(values, p):
    """Linear-interpolation quantile (the 'type 7' rule) of a list."""
    v = sorted(values)
    if not v:
        raise ValueError("empty")
    k = (len(v) - 1) * p
    lo = int(math.floor(k))
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def wilson(k, n, z=1.959964):
    """95% Wilson interval for a share k of n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def read_text(path, **kw):
    with open(path, **kw) as fh:
        return fh.read()


def read_json(path):
    with open(path) as fh:
        return json.load(fh)


def norm_des(s):
    """A designation or name reduced for matching: lower case, letters and digits only."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


class Sbdb:
    """JPL's table of every near-Earth object, with lookups by number, designation and name."""

    def __init__(self, path=None):
        raw = read_json(path or config.SBDB_JSON)
        self.fields = raw["fields"]
        self.idx = {f: i for i, f in enumerate(self.fields)}
        self.rows = {}
        self.alias = {}
        for r in raw["data"]:
            if not str(r[self.idx["kind"]] or "").startswith("a"):
                continue  # comets
            pdes = r[self.idx["pdes"]]
            self.rows[pdes] = r
            self.alias[norm_des(pdes)] = pdes
            name = r[self.idx["name"]]
            if name:
                self.alias.setdefault(norm_des(name), pdes)
            full = r[self.idx["full_name"]] or ""
            m = re.search(r"\(([^()]+)\)\s*$", full)
            if m:
                self.alias.setdefault(norm_des(m.group(1)), pdes)

    def get(self, pdes, field):
        return self.rows[pdes][self.idx[field]]

    def h(self, pdes):
        return fl(self.get(pdes, "H"))

    def resolve(self, *candidates):
        """The pdes for the first candidate designation, number or name that is a near-Earth asteroid."""
        for c in candidates:
            if c is None:
                continue
            k = norm_des(c)
            if k and k in self.alias:
                return self.alias[k]
        return None


def load_nhats(path=None):
    """The reachable list as {des: record}."""
    raw = read_json(path or config.NHATS_JSON)
    return {o["des"]: o for o in raw["data"]}


def load_spitzer():
    with open(config.SPITZER_CSV, newline="") as fh:
        return list(csv.DictReader(fh))


def load_lcdb(sbdb, with_flag=False):
    """Lightcurve database summary -> {pdes: (period_h, U)} for near-Earth asteroids with a period.

    with_flag: {pdes: (period_h, U, flag)}, where flag is the character before the period: '>' the period is a
    minimum, '<' a maximum (readme.pdf section 4.1.4.11), else a value. Callers that take a period as measured
    must leave the flagged ones out.
    """
    path = os.path.join(str(config.LCDB_DIR), "x", "lc_summary_pub.txt")
    lines = read_text(path, errors="replace").split("\n")
    hi = next(i for i, l in enumerate(lines) if l.startswith("NUMBER"))
    hdr = lines[hi]

    def col(name):
        return [m.start() for m in re.finditer(r"(?<![A-Z0-9.])" + re.escape(name) + r"(?![A-Z0-9.])", hdr)][0]

    c_name, c_des, c_fam, c_per, c_desc, c_u, c_notes = (
        col("NAME"), col("DESIG"), col("FAM"), col("PERIOD"), col("P DESC"), col("U"), col("NOTES"))
    out = {}
    for l in lines[hi + 2:]:
        if len(l) < c_u:
            continue
        per = fl(l[c_per:c_desc].strip())
        if not per or per <= 0:
            continue
        num = l[:c_name].strip()
        name = l[c_name:c_des].strip()
        des = l[c_des:c_fam].strip()
        u = l[c_u:c_notes].strip()
        flag = l[c_per - 2:c_per - 1]
        pdes = sbdb.resolve(num if num.isdigit() and int(num) > 0 else None, des, name)
        if pdes:
            out[pdes] = (per, u, flag if flag in "<>" and flag.strip() else "") if with_flag else (per, u)
    return out


def u_grade(u):
    """The leading digit of a lightcurve quality code ('3-', '2+', '2') as an int, or 0."""
    u = (u or "").strip()
    return int(u[0]) if u[:1].isdigit() else 0


def load_pravec(sbdb):
    """Pravec's table -> {pdes: (period_h, U)}: for each object the row with the highest grade, the last such row."""
    out = {}
    stats = {"rows": 0, "with_period": 0, "matched": 0}
    for l in read_text(config.PRAVEC_TXT, errors="replace").split("\n")[1:]:
        if not l.strip() or l[:1].isspace():
            continue
        m = re.match(r"^(\S.*?)\s{2,}(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", l)
        if not m:
            continue
        stats["rows"] += 1
        ident, per, u = m.group(1).strip(), fl(m.group(2)), m.group(6)
        if not per or per <= 0 or not u.isdigit():
            continue
        stats["with_period"] += 1
        mm = re.match(r"^\((\d+)\)\s*(.*)$", ident)
        pdes = sbdb.resolve(mm.group(1), mm.group(2)) if mm else sbdb.resolve(ident)
        if not pdes:
            continue
        stats["matched"] += 1
        if pdes not in out or int(u) >= out[pdes][1]:
            out[pdes] = (per, int(u))
    return out, stats


def iter_cards(cards_dir=None):
    """Yield (file name, card dict) for each SsODNet card on disk, in file-name order."""
    d = str(cards_dir or config.SSODNET_CARDS)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        try:
            c = read_json(os.path.join(d, fn))
        except (ValueError, OSError):
            continue
        if isinstance(c, dict) and "parameters" not in c and len(c) == 1:
            c = list(c.values())[0]
        if isinstance(c, dict) and isinstance(c.get("parameters"), dict):
            yield fn, c


CLASS4 = ("S", "C", "X", "other")


def class4(label):
    """Map a taxonomic class or complex to S (S and Q), C (C, B, F, G), X (X, E, M, P) or other.

    The grouping of docs/research/verify-prior-null.md section 1. Returns None for an empty or
    undecided label (U, CX and the like).
    """
    t = (label or "").strip()
    if not t or t.upper() in ("U", "CX", "XC", "C/X", "X/C"):
        return None
    c = t[0].upper()
    if c in "SQ":
        return "S"
    if c in "CBFG":
        return "C"
    if c in "XEMP":
        return "X"
    if c in "ADKLORTVZ":
        return "other"
    return None


class Report:
    """Collects lines, prints them and writes them to method/v0_1/derivation/<name>.txt."""

    def __init__(self, name):
        self.name = name
        self.lines = []

    def __call__(self, text=""):
        self.lines.append(str(text))

    def table(self, header, rows):
        widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
        for r in [header] + rows:
            self("  ".join(str(c).ljust(w) for c, w in zip(r, widths)).rstrip())

    def close(self, write=True, echo=True):
        text = "\n".join(self.lines) + "\n"
        if echo:
            sys.stdout.write(text)
        if write:
            os.makedirs(DERIVATION, exist_ok=True)
            with open(os.path.join(DERIVATION, self.name + ".txt"), "w") as fh:
                fh.write(text)
        return text
