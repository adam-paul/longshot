"""A made-up field, in the format of docs/mvp.md section 5, for building the field app alone.

Writes a manifest, a field file, a keys file, a minimal index.html, a few entry pages
and a copy of the app's scripts. Nothing here is real data: the designations are
dated 2101 to 2140 so they cannot be mistaken for it.

It makes the cases the app must get right: a designation that is the start of
another's, numbered asteroids, a measured size the file may not carry, and two
asteroids with no brightness on file and so no rock.

    uv run python tools/make_synthetic_field.py                    # 7,231 objects
    uv run python tools/make_synthetic_field.py --n 43000 --out build/synthetic-site-43000
    uv run python tools/make_synthetic_field.py --check dist/data/field.json

--check reads any manifest with the reader below and reports what breaks the contract.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import random
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "longshot" / "site" / "static"
# the state marks, as the real stylesheet draws them (one rule a line, each starting ".g")
GLYPH_CSS = "\n".join("  " + line for line in (STATIC / "style.css").read_text(encoding="utf-8").splitlines()
                       if line.startswith(".g"))

# docs/mvp.md section 5, in order.
COLUMNS = (
    ("dv", "f32"),
    ("size_q50", "f32"), ("size_q05", "f32"), ("size_q95", "f32"),
    ("period_s", "f32"), ("state", "u8"),
    ("p_surface", "u8"), ("p_capture", "u8"),
    ("status_surface", "u8"), ("status_capture", "u8"),
    ("pct_surface", "u8"), ("pct_capture", "u8"), ("named", "u8"),
    ("seed", "u16"),
)
TYPES = {"f32": ("f", 4), "u8": ("B", 1), "u16": ("H", 2), "i32": ("i", 4), "u32": ("I", 4)}
STATE_ROWS = ("size", "spin", "surface", "push")      # two bits each, size in the low bits
UNCHECKED, PRIOR, LIMIT, MEASURED = 0, 1, 2, 3
FAIL, UNTESTED, PASS = 0, 1, 2


# ---- the format ---------------------------------------------------------------

def pack_field(columns, align=4):
    """columns: [(name, type, values)] -> (bytes, [{name, type, offset}]).

    Each column starts on a multiple of `align` bytes; the manifest's offsets say where.
    """
    blob, listing = bytearray(), []
    n = len(columns[0][2])
    for name, kind, values in columns:
        if len(values) != n:
            raise ValueError(f"column {name} has {len(values)} values, expected {n}")
        code, _ = TYPES[kind]
        blob.extend(b"\0" * (-len(blob) % align))
        listing.append({"name": name, "type": kind, "offset": len(blob)})
        blob.extend(struct.pack(f"<{n}{code}", *values))
    return bytes(blob), listing


def write_field(data_dir, columns, keys, data_date, method, counts=None, align=4, unplaced=None):
    """Write field.<hash>.bin, keys.<hash>.json and field.json into data_dir; return the manifest.

    unplaced: keys-file rows for the asteroids with no rock.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    blob, listing = pack_field(columns, align)
    keys_bytes = json.dumps(keys, ensure_ascii=False, separators=(",", ":")).encode()
    field_name = f"field.{hashlib.sha256(blob).hexdigest()[:12]}.bin"
    keys_name = f"keys.{hashlib.sha256(keys_bytes).hexdigest()[:12]}.json"
    manifest = {
        "schema": 1, "data_date": data_date, "method": method, "n": len(keys),
        "file": field_name, "columns": listing, "keys_file": keys_name,
        "counts": {"not_placed": len(unplaced or []), **(counts or {})}, "unplaced": unplaced or [],
    }
    (data_dir / field_name).write_bytes(blob)
    (data_dir / keys_name).write_bytes(keys_bytes)
    (data_dir / "field.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def read_field(manifest_path):
    """The reader: manifest path -> (manifest, {name: [values]}, keys). Raises ValueError on a bad file."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    blob = (manifest_path.parent / manifest["file"]).read_bytes()
    n, cols = manifest["n"], {}
    for col in manifest["columns"]:
        code, size = TYPES[col["type"]]
        end = col["offset"] + n * size
        if end > len(blob):
            raise ValueError(f"column {col['name']} runs to byte {end}, file has {len(blob)}")
        cols[col["name"]] = list(struct.unpack_from(f"<{n}{code}", blob, col["offset"]))
    keys = json.loads((manifest_path.parent / manifest["keys_file"]).read_text())
    return manifest, cols, keys


def unaligned(manifest):
    """Columns whose offset is not a multiple of their type's size. The app copies these instead of viewing them."""
    return [c["name"] for c in manifest["columns"] if c["offset"] % TYPES[c["type"]][1]]


def check(manifest_path):
    """Everything about a field that the app relies on. Returns a list of problems, empty if none."""
    problems = []
    try:
        manifest, cols, keys = read_field(manifest_path)
    except (OSError, ValueError, KeyError, struct.error) as err:
        return [f"cannot read: {err!r}"]
    n = manifest["n"]
    blob_len = (Path(manifest_path).parent / manifest["file"]).stat().st_size
    for field in ("schema", "data_date", "method", "n", "file", "columns", "keys_file", "counts", "unplaced"):
        if field not in manifest:
            problems.append(f"manifest lacks {field}")
    listed = {c["name"]: c["type"] for c in manifest["columns"]}
    for name, kind in COLUMNS:
        if listed.get(name) != kind:
            problems.append(f"column {name}: expected {kind}, manifest has {listed.get(name)}")
    spans = sorted((c["offset"], c["offset"] + n * TYPES[c["type"]][1], c["name"]) for c in manifest["columns"])
    for (_, end, a), (start, _, b) in zip(spans, spans[1:]):
        if start < end:
            problems.append(f"columns {a} and {b} overlap")
    if spans and spans[-1][1] != blob_len:
        problems.append(f"last column ends at byte {spans[-1][1]}, file has {blob_len}")
    if len(keys) != n:
        problems.append(f"keys file has {len(keys)} rows, manifest n is {n}")
    loose = manifest.get("unplaced") or []
    def bad_row(k, size):
        return len(k) != size or not k[0] or not k[1] or not (k[3] is None or isinstance(k[3], int))
    if any(bad_row(k, 4) for k in keys):
        problems.append("a keys row is not [key, designation, name, number]")
    if any(bad_row(k, 5) or not (isinstance(k[4], (int, float)) and k[4] > 0) for k in loose):
        problems.append("an unplaced row is not [key, designation, name, number, dv]")
    if len({k[0] for k in keys + loose}) != len(keys) + len(loose):
        problems.append("keys are not unique")
    if manifest.get("counts", {}).get("not_placed") != len(loose):
        problems.append(f"counts.not_placed is {manifest.get('counts', {}).get('not_placed')}, the manifest lists {len(loose)} unplaced")
    if problems:
        return problems
    for name in ("dv", "size_q05", "size_q50", "size_q95"):
        if not all(math.isfinite(v) and v > 0 for v in cols[name]):
            problems.append(f"{name} must be finite and above zero in every row")
    if not all(a <= b <= c for a, b, c in zip(cols["size_q05"], cols["size_q50"], cols["size_q95"])):
        problems.append("size_q05 <= size_q50 <= size_q95 does not hold in every row")
    if not all(math.isfinite(v) and v >= 0 for v in cols["period_s"]):
        problems.append("period_s must be finite and not negative")
    for name in ("status_surface", "status_capture"):
        if not all(v in (FAIL, UNTESTED, PASS) for v in cols[name]):
            problems.append(f"{name} must be 0, 1 or 2")
    for name in ("pct_surface", "pct_capture"):
        if not all(0 <= v <= 100 for v in cols[name]):
            problems.append(f"{name} must be 0 to 100")
    for mission in ("surface", "capture"):
        decided = {(FAIL, 0), (PASS, 100)}
        if not all((s, v) in decided or s == UNTESTED for s, v in zip(cols[f"status_{mission}"], cols[f"pct_{mission}"])):
            problems.append(f"pct_{mission} must be 0 for a fail and 100 for a pass")
    if not all(v in (0, 1) for v in cols["named"]):
        problems.append("named must be 0 or 1")
    return problems


# ---- the made-up objects ------------------------------------------------------

def _designation(rng, seen):
    letters = "ABCDEFGHJKLMNOPQRSTUVWXY"
    while True:
        des = f"{rng.randrange(2101, 2141)} {rng.choice(letters)}{rng.choice(letters + 'Z')}{rng.randrange(1, 400)}"
        if des not in seen:
            seen.add(des)
            return des


def synthesize(n, seed="longshot-synthetic"):
    """n made-up objects -> ([(name, type, values)], keys, counts). Same n and seed, same bytes.

    A keys row is [key, designation, name, number]. The first designation is the second's with a
    digit added, so a search for the second meets the first before it. About one in forty is numbered.
    """
    rng = random.Random(f"{seed}:{n}")
    cols = {name: [] for name, _ in COLUMNS}
    keys, seen = [], set()
    short = _designation(rng, seen)
    for i in range(n):
        key = "s" + hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()[:9]
        des = short + "7" if i == 0 else short if i == 1 else _designation(rng, seen)
        seen.add(des)
        name = f"Synthetic {i}" if rng.random() < 0.01 else None
        keys.append([key, des, name, 900001 + i if i % 40 == 3 else None])

        dv = round(min(12.0, max(3.3, 12.0 - 8.7 * rng.betavariate(1.25, 3.0))), 3)
        h = 0.0
        while not 17.0 <= h <= 31.0:
            h = round(rng.gauss(25.0, 2.6), 1)
        typical = 0.71 * 1329e3 / math.sqrt(0.14) * 10 ** (-h / 5)       # metres
        carded = rng.random() < 0.3                                       # the literature source knows it
        r = rng.random()
        if r < 0.03:
            size_state = MEASURED
            q50 = typical * math.exp(rng.gauss(0, 0.45))
            q05, q95 = q50 * 0.88, q50 * 1.12
        elif r < 0.04:
            size_state = LIMIT
            q50, q05, q95 = typical, typical * 0.5, typical * 1.4
        else:
            size_state = PRIOR if carded else UNCHECKED
            q50, q05, q95 = typical, typical * 0.5, typical * 2.2

        period = 0.0
        if rng.random() < 0.045:
            spin_state = MEASURED
            period = math.exp(rng.uniform(math.log(60.0), math.log(50 * 3600.0)))
        elif rng.random() < 0.01:
            spin_state = LIMIT
        else:
            spin_state = PRIOR if carded else UNCHECKED
        surface_state = MEASURED if rng.random() < 0.04 else PRIOR if carded else UNCHECKED
        push_state = rng.choices((MEASURED, LIMIT, PRIOR), (1, 2, 97))[0]
        state = size_state | spin_state << 2 | surface_state << 4 | push_state << 6

        occ = 255 if rng.random() < 0.02 else rng.choices(range(10), (8, 6, 6, 7, 8, 10, 14, 16, 14, 11))[0]
        findable = int(occ <= 5)
        slow = period > 2.2 * 3600

        def judge(passes, fails, p):
            """(status, p byte, the whole percentage an entry prints)"""
            if not findable or fails:
                return FAIL, 0, 0
            if passes:
                return PASS, 255, 100
            pct = 0 if p < 0.005 else 100 if p >= 0.995 else max(1, min(99, math.floor(p * 100 + 0.5 + 1e-9)))
            return UNTESTED, max(1, min(254, round(255 * p))), pct

        measured = size_state == MEASURED
        s_surface, p_surface, pct_surface = judge(measured and q50 >= 100 and (slow or not period), measured and q50 < 30,
                                     0.6 / (1 + (150 / typical) ** 2))
        s_capture, p_capture, pct_capture = judge(measured and q50 <= 10, measured and q50 > 20,
                                     0.5 / (1 + (typical / 9) ** 2))

        row = {
            "dv": dv, "size_q50": q50, "size_q05": q05, "size_q95": q95,
            "period_s": period, "state": state,
            "p_surface": p_surface, "p_capture": p_capture,
            "status_surface": s_surface, "status_capture": s_capture,
            "pct_surface": pct_surface, "pct_capture": pct_capture, "named": int(name is not None),
            "seed": int.from_bytes(hashlib.sha256(key.encode()).digest()[:2], "little"),
        }
        for name, value in row.items():
            cols[name].append(value)

    counts = {
        "objects": n,
        "with_period": sum(1 for p in cols["period_s"] if p > 0),
        "size_state": [sum(1 for s in cols["state"] if s & 3 == code) for code in range(4)],
    }
    return [(name, kind, cols[name]) for name, kind in COLUMNS], keys, counts


def unplaced(seed="longshot-synthetic", count=2):
    """Manifest rows for made-up asteroids with no size: they have pages and no rock. [key, designation, name,
    number, dv]: a keys-file row and the delta-v, for the table view."""
    return [["u" + hashlib.sha256(f"{seed}:unplaced:{i}".encode()).hexdigest()[:9], f"2141 ZZ{i + 1}", None,
             990001 + i if i else None, round(11.5 - 0.7 * i, 3)]
            for i in range(count)]


# ---- the pages ----------------------------------------------------------------

INDEX = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="field-manifest" content="data/field.json">
<title>longshot (synthetic field)</title>
<style>
  :root {{ --ink: #fff; --ink-2: #a8a8a8; --edge: #5e5e5e; --grid: #202020; --ground: #000; color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  [hidden] {{ display: none !important; }}
  html, body {{ margin: 0; background: #000; color: #fff; font: 14px/20px system-ui, sans-serif; font-variant-numeric: tabular-nums; }}
  ul {{ margin: 0; padding: 0; list-style: none; }} h1, h2, p {{ margin: 0; font-weight: 400; }} a {{ color: inherit; }}
  .vh {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }}
  header {{ display: flex; gap: 24px; align-items: center; height: 48px; padding: 0 32px; border-bottom: 1px solid var(--edge); }}
  header .date {{ margin-left: auto; color: var(--ink-2); font-size: 12px; }}
  main {{ display: grid; grid-template-columns: minmax(0, 1fr) 424px; grid-template-rows: auto minmax(0, 1fr); height: calc(100vh - 48px); min-height: 560px; }}
  #controls {{ grid-column: 1 / -1; display: flex; align-items: flex-end; gap: 32px; padding: 12px 32px; border-bottom: 1px solid var(--edge); }}
  .ctl {{ display: flex; flex-direction: column; gap: 6px; border: 0; margin: 0; padding: 0; }} .ctl > .lab, .ctl legend {{ color: var(--ink-2); padding: 0; }}
  .seg {{ display: flex; }} .seg label {{ position: relative; }} .seg input {{ position: absolute; opacity: 0; inset: 0; margin: 0; }}
  .seg span {{ display: block; padding: 5px 12px; border: 1px solid var(--edge); color: var(--ink-2); white-space: nowrap; }}
  .seg input:checked + span {{ background: #fff; color: #000; }}
  input[type=search] {{ background: #000; color: #fff; border: 1px solid var(--edge); height: 32px; width: 240px; }}
  .fig {{ display: flex; flex-direction: column; min-height: 0; padding: 12px 24px 12px 32px; }}
  .fig-head {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px 24px; margin-bottom: 12px; min-height: 32px; }}
  #legend {{ flex: 1; }} .legend {{ display: flex; gap: 24px; flex-wrap: wrap; color: var(--ink-2); }} .legend li {{ display: flex; align-items: center; white-space: nowrap; }} .legend .n {{ margin-left: 6px; }} .legend li > .n:first-child {{ margin: 0 6px 0 0; }} .legend .g {{ margin-right: 6px; }} .legend .n {{ color: #fff; }}
  .zoom {{ display: flex; align-items: center; gap: 0; }}
  .btn {{ font: inherit; color: #fff; background: #000; border: 1px solid var(--edge); padding: 5px 12px; cursor: pointer; text-decoration: none; }} .btn:disabled {{ color: var(--edge); }}
  #plot {{ position: relative; flex: 1; min-height: 0; margin: 0; touch-action: pan-y; }}
  #plot > canvas, #plot > .grid, #axes {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; }}
  #axes {{ pointer-events: none; overflow: hidden; }} #axes svg {{ position: absolute; left: 0; top: 0; }}
  #axes span {{ position: absolute; white-space: nowrap; font-size: 12px; color: var(--ink-2); }}
  #axes .ax-tag {{ background: #fff; color: #000; padding: 1px 5px; }} #axes .ax-note {{ background: #000; color: #fff; padding: 0 2px; }}
  #tip {{ position: absolute; pointer-events: none; background: #000; border: 1px solid #fff; padding: 4px 8px; font-size: 12px; white-space: nowrap; }} #tip .k {{ color: var(--ink-2); }}
  #table {{ flex: 1; min-height: 0; min-width: 0; display: flex; flex-direction: column; }}
  .tscroll {{ position: relative; flex: 1; min-height: 0; overflow: auto; border-top: 1px solid var(--edge); }}
  .ftbl {{ width: 100%; border-collapse: collapse; }} .ftbl th, .ftbl td {{ padding: 6px 12px; text-align: left; white-space: nowrap; border-top: 1px solid var(--grid); font-weight: 400; }}
  .ftbl thead th {{ position: sticky; top: 0; background: #000; color: var(--ink-2); font-size: 12px; }} .ftbl button {{ font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }}
  .ftbl .num {{ text-align: right; }} .ftbl .nm {{ color: var(--ink-2); margin-left: 8px; }} .ftbl tr.sel > * {{ background: #161616; }} .ftbl .mc {{ display: flex; justify-content: space-between; gap: 12px; }}
  .pager {{ display: flex; gap: 8px; justify-content: flex-end; align-items: center; padding-top: 12px; }} .pager output {{ margin-right: auto; color: var(--ink-2); }}
{GLYPH_CSS}
  .find-msg {{ font-size: 12px; color: var(--ink-2); }}
  #readout {{ border-left: 1px solid var(--edge); padding: 8px 24px 24px; overflow: auto; min-height: 0; }}
  #readout h2 {{ color: var(--ink-2); margin: 24px 0 4px; }} .named li {{ display: flex; justify-content: space-between; padding: 4px 0; border-top: 1px solid var(--grid); }}
  .sel-head {{ display: flex; justify-content: space-between; margin-top: 16px; }} .sel-head h2 {{ font-size: 32px; line-height: 36px; color: #fff !important; margin: 0 !important; }} .sel-go {{ margin-top: 24px; }}
  .sumlist th {{ color: var(--ink-2); font-weight: 400; text-align: left; }} .sumlist .d {{ color: var(--ink-2); }}
  @media (max-width: 899px) {{ main {{ display: block; height: auto; }} #controls {{ flex-wrap: wrap; padding: 12px 16px; }} .fig {{ padding: 12px 16px; }} #plot {{ flex: none; height: 460px; }} #readout {{ border: 0; border-top: 1px solid var(--edge); padding: 8px 16px; }} input[type=search] {{ width: 100%; }} }}
</style>
<header><a href="index.html">longshot</a><span>prototype</span><nav><a href="index.html" aria-current="page">Field</a></nav><p class="date">Data {data_date}</p></header>
<main>
  <form id="controls" action="index.html" method="get">
    <fieldset class="ctl"><legend>View</legend><div class="seg"><label><input type="radio" name="view" value="chart" checked><span>Chart</span></label><label><input type="radio" name="view" value="table"><span>Table</span></label></div></fieldset>
    <fieldset class="ctl"><legend>Mission</legend><div class="seg"><label><input type="radio" name="m" value="" checked><span>Any</span></label><label><input type="radio" name="m" value="surface"><span>Surface work</span></label><label><input type="radio" name="m" value="capture"><span>Whole-body capture</span></label></div></fieldset>
    <div class="ctl"><label class="lab" for="dv">Max Δv (km/s)</label><div><input id="dv" name="dv" type="range" min="3.3" max="12" step="0.1" value="12"> <output name="dv-value" for="dv">12.0</output></div></div>
    <div class="ctl"><label class="lab" for="q">Find</label><input id="q" name="q" type="search" placeholder="Designation, name or number" autocomplete="off"></div>
  </form>
  <section class="fig" aria-labelledby="fig-title">
    <div class="fig-head">
      <h1 id="fig-title" class="vh">Reachable asteroids by delta-v (Δv) and diameter</h1>
      <div id="legend"><ul class="legend"></ul></div>
      <div class="zoom" role="group" aria-label="Zoom"><button type="button" class="btn" name="zoom-out" form="controls" aria-label="Zoom out">−</button><button type="button" class="btn" name="zoom-in" form="controls" aria-label="Zoom in">+</button> <button type="button" class="btn" name="zoom-reset" form="controls">Reset</button></div>
    </div>
    <figure id="plot"><canvas id="field"></canvas><div id="axes"></div><div id="tip" hidden></div></figure>
    <section id="table" hidden></section>
  </section>
  <aside id="readout" aria-live="polite">
    <h2>Named asteroids</h2>
    <ul class="named">{links}</ul>
  </aside>
</main>
<script type="module" src="static/app.js"></script>
</html>
"""

ENTRY = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{des} (synthetic)</title>
<body style="background:#000;color:#fff;font:16px/1.4 ui-serif,Georgia,serif">
<style>a {{ color: inherit; }}</style>
<header><a href="../index.html">longshot</a> <span>Data {data_date}</span></header>
<main id="entry" class="entry" data-key="{key}">
  <div class="ehead"><h1>{des}</h1></div>
  <section id="summary">
    <table class="sumlist"><tbody>
      <tr><th scope="row">Diameter</th><td class="v">{size}</td><td class="d">{size_note}</td></tr>
      <tr><th scope="row">Spin</th><td class="v">{spin}</td><td class="d"></td></tr>
      <tr><th scope="row">Δv</th><td class="v">{dv}</td><td class="d"></td></tr>
    </tbody></table>
  </section>
  <section id="sources"><h2>Sources</h2><p><a href="{other}.html">{other_des}</a> · <a href="../index.html">the field</a></p></section>
</main>
</body>
</html>
"""


def write_site(out, n, seed="longshot-synthetic", entries=2, align=4):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    columns, keys, counts = synthesize(n, seed)
    loose = unplaced(seed)
    counts = {**counts, "objects": n + len(loose), "placed": n}
    if align == 1:      # a one-byte column first: with an odd n every wider column then starts off its boundary
        columns = sorted(columns, key=lambda c: c[0] != "state")
    manifest = write_field(out / "data", columns, keys, "2026-11-24", "synthetic", counts, align, loose)
    cols = {name: values for name, _, values in columns}
    (out / "a").mkdir()
    for key, des, _, _, dv in loose:
        (out / "a" / f"{key}.html").write_text(ENTRY.format(
            data_date=manifest["data_date"], key=key, des=html.escape(des), dv=f"{dv:.3f} km/s", size="no brightness on file", size_note="",
            spin="no brightness on file", other=keys[0][0], other_des=html.escape(keys[0][1])))
    links = []
    for i in range(min(entries, n)):
        key, des = keys[i][:2]
        other = keys[(i + 1) % min(entries, n)]
        period = cols["period_s"][i]
        est = cols["state"][i] & 3 < LIMIT
        (out / "a" / f"{key}.html").write_text(ENTRY.format(
            data_date=manifest["data_date"], key=key, des=html.escape(des), dv=f"{cols['dv'][i]:.3f} km/s",
            size=f"{cols['size_q05'][i]:.2g}–{cols['size_q95'][i]:.2g} m", size_note="90% range, " + ("estimated" if est else "measured"),
            spin=f"{period / 3600:.3g} h" if period else "estimated",
            other=other[0], other_des=html.escape(other[1])))
        links.append(f'<li><a href="a/{key}.html">{html.escape(des)}</a><span>{cols["dv"][i]:.3f} km/s</span></li>')
    (out / "index.html").write_text(INDEX.format(n=f"{n:,}", total=f"{n + len(loose):,}", data_date=manifest["data_date"],
                                                 links="".join(links), GLYPH_CSS=GLYPH_CSS))
    (out / "static").mkdir()
    for script in sorted(STATIC.glob("*.js")):
        shutil.copy(script, out / "static" / script.name)
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=7231, help="objects (7231, or 43000 for every near-Earth object)")
    ap.add_argument("--out", default=str(ROOT / "build" / "synthetic-site"))
    ap.add_argument("--entries", type=int, default=2, help="entry pages to write for placed objects")
    ap.add_argument("--unaligned", action="store_true",
                    help="pack columns with no padding, a one-byte column first, to exercise the app's copy path (odd --n)")
    ap.add_argument("--check", metavar="MANIFEST", help="check an existing field against the contract and exit")
    args = ap.parse_args(argv)
    if args.check:
        problems = check(args.check)
        print("\n".join(problems) if problems else "ok")
        if not problems and (loose := unaligned(read_field(args.check)[0])):
            print("not aligned to their type, so the app copies them:", ", ".join(loose))
        return 1 if problems else 0
    manifest = write_site(args.out, args.n, entries=args.entries, align=1 if args.unaligned else 4)
    size = (Path(args.out) / "data" / manifest["file"]).stat().st_size
    print(f"{args.out}: {manifest['n']:,} objects, {manifest['file']} {size:,} bytes, {manifest['keys_file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
