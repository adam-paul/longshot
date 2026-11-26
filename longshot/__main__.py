"""The command line: build and serve. See docs/mvp.md section 1.

    uv run python -m longshot build [--build DIR] [--dist DIR] [--quiet]
    uv run python -m longshot serve [--port 8000] [--dist DIR]

build runs, in order and with no network: ingest and the ledger, the model, the
export and the site generator. It writes build/ledger.jsonl, build/records.jsonl
and the whole site under dist/, and removes any file under dist/ it did not write.

The clock is read only to print how long the build took. Nothing it says goes
into a file.
"""
from __future__ import annotations

import argparse
import functools
import gzip
import hashlib
import http.server
import json
import re
import sys
import time
from pathlib import Path

from longshot import config

STATIC = Path(__file__).resolve().parent / "site" / "static"
FIELD_IMPORT = "'./field.js'"           # the one import in app.js; rewritten to the hashed name
# What a build owns under dist/: anything else found in these places is removed.
OWNED_DIRS = ("a", "list", "data", "static")
OWNED_TOP = "*.html"


class BuildError(Exception):
    pass


def _hashed(stem: str, suffix: str, data: bytes) -> str:
    return f"{stem}.{hashlib.sha256(data).hexdigest()[:12]}{suffix}"


def write_static(dist_dir: Path) -> dict:
    """Copy style.css, field.js and app.js under names that carry a hash of their bytes.

    Returns {"style", "app", "field": site-root-relative URLs}. app.js imports
    field.js by name, so that name is rewritten before app.js is hashed.
    """
    out = dist_dir / "static"
    out.mkdir(parents=True, exist_ok=True)
    style = (STATIC / "style.css").read_bytes()
    field = (STATIC / "field.js").read_bytes()
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    if app.count(FIELD_IMPORT) != 1:
        raise BuildError(f"app.js must import {FIELD_IMPORT} exactly once; found {app.count(FIELD_IMPORT)}")
    field_name = _hashed("field", ".js", field)
    app_bytes = app.replace(FIELD_IMPORT, f"'./{field_name}'").encode("utf-8")
    names = {"style": _hashed("style", ".css", style), "field": field_name, "app": _hashed("app", ".js", app_bytes)}
    for key, data in (("style", style), ("field", field), ("app", app_bytes)):
        (out / names[key]).write_bytes(data)
    return {key: f"static/{name}" for key, name in names.items()}


MARKER = "data/field.json"              # every build writes it; its presence says "a site this tool built"


def check_dist(dist_dir: Path) -> None:
    """Refuse a folder a build must not prune: one that is not a site this tool built.

    A build removes every file it did not write under a/, list/, data/ and static/. Pointed at the repository
    root by a mistyped --dist, that would delete data/, which is outside git.
    """
    dist_dir = dist_dir.resolve()
    for precious in (config.ROOT, config.DATA):
        precious = precious.resolve()
        if dist_dir == precious or precious.is_relative_to(dist_dir) or dist_dir.is_relative_to(config.DATA.resolve()):
            raise BuildError(f"--dist {dist_dir} holds or lies inside {precious}; a build would delete files there")
    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        return                                              # new or empty: nothing to lose
    marker = dist_dir / MARKER
    try:
        built_here = json.loads(marker.read_text(encoding="utf-8")).get("schema") is not None
    except (OSError, ValueError, AttributeError):
        built_here = False
    if not built_here:
        raise BuildError(f"--dist {dist_dir} is not empty and holds no {MARKER} from an earlier build; "
                         "a build would delete files there. Give an empty folder")


def prune(dist_dir: Path, keep: set[Path]) -> int:
    """Remove files a build owns under dist/ that this build did not write. Returns how many."""
    stale = [p for p in dist_dir.glob(OWNED_TOP) if p.is_file() and p not in keep]
    for name in OWNED_DIRS:
        stale += [p for p in (dist_dir / name).rglob("*") if p.is_file() and p not in keep]
    for p in stale:
        p.unlink()
    return len(stale)


def first_screen(dist_dir: Path, assets: dict, manifest: dict) -> list[tuple[str, int, int]]:
    """(path, bytes, gzipped bytes) for each file the front page fetches before the field is drawn."""
    from longshot.site import templates
    paths = ["index.html", assets["style"], assets.get("font", templates.FONT), assets["app"], assets["field"],
             assets["field_manifest"], f"data/{manifest['file']}", f"data/{manifest['keys_file']}"]
    out = []
    for rel in paths:
        data = (dist_dir / rel).read_bytes()
        out.append((rel, len(data), len(gzip.compress(data, 6, mtime=0))))
    return out


def build(build_dir: Path | None = None, dist_dir: Path | None = None, out=None) -> dict:
    """Run the whole pipeline. Returns the counts it prints; `out` is where they are printed (None: nowhere)."""
    from longshot import contract, export, ledger, model, predictions, sources
    from longshot.site import gen

    def say(text: str = "") -> None:
        if out is not None:
            print(text, file=out, flush=True)

    started = time.perf_counter()
    lap = started
    def took() -> str:
        nonlocal lap
        now = time.perf_counter()
        text, lap = f"{now - lap:.1f} s", now
        return text

    build_dir = Path(build_dir or config.BUILD).resolve()
    dist_dir = Path(dist_dir or config.DIST).resolve()
    check_dist(dist_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    records = ledger.build(write_file=False)
    if not records:
        raise BuildError("the reachable list is empty")
    ledger.write(records, build_dir / "ledger.jsonl")
    say(f"ledger     {len(records):,} asteroids from {len(sources.load())} sources, {took()}")

    model.run(records)
    contract.check(records)
    say(f"model      priors, missions, observe, value, ladder, {took()}")

    exported = export.write(records, build_dir, dist_dir)
    manifest = json.loads((dist_dir / exported["field_manifest"]).read_text(encoding="utf-8"))
    preds = predictions.predictions(records)
    contract.check_predictions(preds)
    assets = write_static(dist_dir)
    assets["field_manifest"] = exported["field_manifest"]
    # The front page asks for these one after another; named in its head, they load side by side. The keys
    # file is not among them: the app fetches it once the rocks are drawn, so it does not hold up the first frame.
    assets["preload"] = [(assets["field"], "module"), (exported["field_manifest"], "fetch"),
                         (exported["field"], "fetch")]
    # the front page's readout before anything is selected: the named asteroids and one typical unmeasured one
    assets["readout"] = export.readout(records)
    pages = gen.write_site(records, sources.load(), dist_dir, assets, preds)
    entries = [p for p in pages if p.parent.name == "a"]
    if len(entries) != len(records):
        raise BuildError(f"{len(records)} asteroids but {len(entries)} entry pages")
    keep = set(pages) | {dist_dir / assets[k] for k in ("style", "app", "field")}
    keep |= {dist_dir / exported[k] for k in ("field_manifest", "field", "keys")}
    removed = prune(dist_dir, keep)
    say(f"site       {sum(1 for p in pages if p.suffix == '.html'):,} pages, {took()}" + (f"; {removed:,} stale files removed" if removed else ""))

    counts = ledger.counts(records)
    screen = first_screen(dist_dir, assets, manifest)
    report = {
        "objects": len(records),
        "rows": counts,
        "missions": manifest["counts"]["missions"],
        "observe": manifest["counts"]["observe"],
        "predictions": len(preds),
        "readout": assets["readout"],
        "pages": sum(1 for p in pages if p.suffix == ".html"),
        "entry_pages": len(entries),
        "entry_bytes": sum(p.stat().st_size for p in entries),
        "field": {"n": manifest["n"], "not_placed": manifest["counts"]["not_placed"],
                  "with_period": manifest["counts"]["with_period"],
                  "bytes": (dist_dir / exported["field"]).stat().st_size,
                  "keys_bytes": (dist_dir / exported["keys"]).stat().st_size},
        "first_screen": {"files": screen, "bytes": sum(b for _, b, _ in screen), "gzip": sum(g for _, _, g in screen)},
        "data_date": manifest["data_date"], "method": manifest["method"],
        "build_dir": str(build_dir), "dist_dir": str(dist_dir),
    }

    say()
    say(f"data as of {report['data_date']}, method {report['method']}")
    say(f"asteroids  {report['objects']:,}")
    say("rows by state")
    say(ledger.format_counts(records))
    for name, c in report["missions"].items():
        say(f"{name:<10} {c['pass']:,} pass, {c['untested']:,} untested, {c['fail']:,} fail")
    say(f"observe    {report['observe']:,} ranked")
    say(f"readout    {len(assets['readout']['named']):,} named")
    say(f"record     {report['predictions']:,} predictions")
    say(f"pages      {report['pages']:,} written ({report['entry_pages']:,} entries, "
        f"{report['entry_bytes']:,} bytes of entries)")
    f = report["field"]
    say(f"field      {f['n']:,} rocks ({f['not_placed']:,} with no size left out, {f['with_period']:,} turn), "
        f"{f['bytes']:,} bytes; keys {f['keys_bytes']:,} bytes")
    s = report["first_screen"]
    say(f"first screen  {s['bytes']:,} bytes in {len(screen)} files ({s['gzip']:,} gzipped)")
    for rel, size, packed in screen:
        say(f"           {size:>9,} {packed:>9,}  {rel}")
    say(f"written    {build_dir}, {dist_dir}")
    report["seconds"] = time.perf_counter() - started
    say(f"elapsed    {report['seconds']:.1f} s")
    return report


def cache_control(path: str) -> str:
    """Files with a hash in their name never change; everything else is checked again each time."""
    name = path.split("?")[0].rsplit("/", 1)[-1]
    hashed = path.startswith(("/static/", "/data/")) and re.fullmatch(r"[a-z]+\.[0-9a-f]{12}\.[a-z]+", name)
    return "public, max-age=31536000, immutable" if hashed else "no-cache"


class _Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", cache_control(self.path))
        super().end_headers()


def serve(dist_dir: Path | None = None, port: int = 8000, host: str = "127.0.0.1") -> int:
    dist_dir = Path(dist_dir or config.DIST).resolve()
    if not (dist_dir / "index.html").is_file():
        print(f"{dist_dir} holds no site; run: uv run python -m longshot build", file=sys.stderr)
        return 1
    handler = functools.partial(_Handler, directory=str(dist_dir))
    with http.server.ThreadingHTTPServer((host, port), handler) as server:
        print(f"serving {dist_dir} at http://{host}:{server.server_address[1]}/ (Ctrl-C stops it)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m longshot", description="Build or serve the site.")
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="data on disk -> build/ and dist/, no network")
    b.add_argument("--build", dest="build_dir", default=None, help="folder for intermediate files (default: build/)")
    b.add_argument("--dist", dest="dist_dir", default=None, help="folder for the site (default: dist/)")
    b.add_argument("--quiet", action="store_true", help="print nothing")
    s = sub.add_parser("serve", help="local static server for dist/")
    s.add_argument("port", nargs="?", type=int, default=8000)
    s.add_argument("--port", dest="port_flag", type=int, default=None)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--dist", dest="dist_dir", default=None)
    args = ap.parse_args(argv)
    if args.command == "build":
        build(args.build_dir, args.dist_dir, out=None if args.quiet else sys.stdout)
        return 0
    return serve(args.dist_dir, args.port_flag if args.port_flag is not None else args.port, args.host)


if __name__ == "__main__":
    sys.exit(main())
