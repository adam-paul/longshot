"""Load a built site in headless Chromium and report what the field does. Standard library only.

    uv run python tools/browser_check.py build/synthetic-site
    uv run python tools/browser_check.py dist --gl software --seconds 5 --label dist

Serves the directory on a free local port, drives the browser over its debugging pipe,
and reports: console errors, the WebGL2 renderer, rocks drawn and in how many draw calls,
frame times with every rock on screen, bytes fetched for the first screen, and whether
the marks follow docs/design.md section 4 (the glow on measured rocks only; estimated
rocks at half brightness, dots that become outlines zoomed in; a size not checked drawn
as an estimate; no brightness that follows a mission's chance; viable ones filled,
ruled out faint), the tip, zoom and pan by wheel, drag, buttons, keys and pinch, the
axes, the legend line's counts against the field file read here, the mission filter and
Max Δv, the readout and its Close, search, the table view (pages, sorting, filters),
the keyboard, history, touch at phone width, a change of pixel ratio, a lost context, a
keys file that does not load and a browser without WebGL2 behave. It also reads the
computed style of every visible text on the front page and the other pages: two inks
only (docs/design.md section 4), and the surface words only on the front page (section 3).
A check whose case the site does not hold (no numbered asteroid, say) is printed as "skip".
Screenshots go to build/screens/. Exit status 1 if a check fails.
"""
from __future__ import annotations

import argparse
import base64
import fcntl
import functools
import gzip
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_synthetic_field import read_field  # noqa: E402  the field file's reader, beside this tool


def chrome():
    """LONGSHOT_CHROME, else the newest headless Chromium that Playwright has put in its cache; None if neither."""
    if os.environ.get("LONGSHOT_CHROME"):
        return os.environ["LONGSHOT_CHROME"]
    found = sorted(Path.home().glob(".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"),
                   key=lambda f: int(f.parts[-3].rpartition("-")[2]))
    return str(found[-1]) if found else None


GL_FLAGS = {
    "gpu": ["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=vulkan", "--enable-features=Vulkan"],
    "software": ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
}
SOFTWARE = ("swiftshader", "llvmpipe", "software")


# ---- a static server that remembers what it sent --------------------------------

class Handler(http.server.SimpleHTTPRequestHandler):
    sent: list  # (path, status, bytes), set per server

    def log_message(self, *args):
        pass

    def send_head(self):
        f = super().send_head()
        if f is not None:
            self.sent.append((self.path, 200, os.fstat(f.fileno()).st_size))
        return f

    def send_error(self, code, message=None, explain=None):
        self.sent.append((self.path, code, 0))
        super().send_error(code, message, explain)


def serve(directory):
    sent = []
    handler = functools.partial(type("H", (Handler,), {"sent": sent}), directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, sent


# ---- the browser, over --remote-debugging-pipe ----------------------------------

class Browser:
    def __init__(self, chrome, flags, size):
        self.profile = tempfile.mkdtemp(prefix="longshot-check-")
        to_r, to_w = os.pipe()
        from_r, from_w = os.pipe()

        def wire():   # the browser reads commands on fd 3 and writes replies on fd 4
            a, b = fcntl.fcntl(to_r, fcntl.F_DUPFD, 10), fcntl.fcntl(from_w, fcntl.F_DUPFD, 10)
            os.dup2(a, 3)
            os.dup2(b, 4)

        self.proc = subprocess.Popen(
            [str(chrome), "--headless", "--no-sandbox", "--remote-debugging-pipe", f"--user-data-dir={self.profile}",
             "--no-first-run", "--mute-audio", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
             "--disable-background-timer-throttling", "--disable-renderer-backgrounding", *flags, "about:blank"],
            preexec_fn=wire, pass_fds=(3, 4), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(to_r)
        os.close(from_w)
        self.w, self.r = to_w, from_r
        self.next, self.replies, self.events = 0, {}, []
        self.cond = threading.Condition()
        threading.Thread(target=self._read, daemon=True).start()
        target = next(t for t in self.send("Target.getTargets")["targetInfos"] if t["type"] == "page")
        self.session = self.send("Target.attachToTarget", {"targetId": target["targetId"], "flatten": True})["sessionId"]
        for domain in ("Page", "Runtime", "Log", "Network"):
            self.send(domain + ".enable")

    def _read(self):
        buf = b""
        while chunk := os.read(self.r, 1 << 16):
            *messages, buf = (buf + chunk).split(b"\0")
            with self.cond:
                for raw in messages:
                    msg = json.loads(raw)
                    if "id" in msg:
                        self.replies[msg["id"]] = msg
                    else:
                        self.events.append(msg)
                self.cond.notify_all()

    def send(self, method, params=None, timeout=60):
        with self.cond:
            self.next += 1
            ident = self.next
            msg = {"id": ident, "method": method, "params": params or {}}
            if getattr(self, "session", None):
                msg["sessionId"] = self.session
            os.write(self.w, json.dumps(msg).encode() + b"\0")
            if not self.cond.wait_for(lambda: ident in self.replies, timeout):
                raise TimeoutError(method)
            reply = self.replies.pop(ident)
        if "error" in reply:
            raise RuntimeError(f"{method}: {reply['error']}")
        return reply["result"]

    def js(self, expression, timeout=60):
        r = self.send("Runtime.evaluate", {"expression": expression, "awaitPromise": True, "returnByValue": True}, timeout)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError(d.get("exception", {}).get("description") or d.get("text"))
        return r["result"].get("value")

    def until(self, expression, timeout=20):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if self.js(expression):
                return True
            time.sleep(0.05)
        return False

    def mouse(self, kind, x, y, **more):
        self.send("Input.dispatchMouseEvent", {"type": kind, "x": x, "y": y, **more})

    def click(self, x, y):
        self.mouse("mouseMoved", x, y)
        self.mouse("mousePressed", x, y, button="left", clickCount=1)
        self.mouse("mouseReleased", x, y, button="left", clickCount=1)

    def key(self, key, code=None, vk=0):
        for kind in ("keyDown", "keyUp"):
            self.send("Input.dispatchKeyEvent", {"type": kind, "key": key, "code": code or key, "windowsVirtualKeyCode": vk})

    def touch(self, kind, *points):
        """kind: touchStart, touchMove or touchEnd. points: (x, y) of each finger still down, in order."""
        self.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(points)]})

    def tap(self, x, y):
        self.touch("touchStart", (x, y))
        self.touch("touchEnd")

    def shot(self, path, whole=0):
        """A screenshot of the window, or of the page from its top down to `whole` px at most."""
        params = {"format": "png"}
        if whole:
            size = self.send("Page.getLayoutMetrics")["cssContentSize"]
            params.update(captureBeyondViewport=True,
                          clip={"x": 0, "y": 0, "width": size["width"], "height": min(size["height"], whole), "scale": 1})
        data = self.send("Page.captureScreenshot", params)["data"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(data))
        return str(path)

    def problems(self):
        """Console errors and warnings, uncaught exceptions, failed loads."""
        out = []
        with self.cond:
            for e in self.events:
                m, p = e.get("method"), e.get("params", {})
                if m == "Runtime.exceptionThrown":
                    d = p["exceptionDetails"]
                    out.append("exception: " + (d.get("exception", {}).get("description") or d.get("text", "")))
                elif m == "Runtime.consoleAPICalled" and p["type"] in ("error", "warning", "assert"):
                    out.append(f"console.{p['type']}: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"]))
                elif m == "Log.entryAdded" and p["entry"]["level"] in ("error", "warning"):
                    out.append(f"log {p['entry']['level']}: {p['entry']['text']} {p['entry'].get('url', '')}")
        return out

    def close(self):
        try:
            self.send("Browser.close", timeout=5)
        except Exception:
            pass
        try:
            self.proc.wait(5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)


# ---- what runs in the page --------------------------------------------------------

FACTS = """(() => {
  const f = longshot.field, gl = f.gl, e = gl.getExtension('WEBGL_debug_renderer_info');
  return {
    renderer: e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
    version: gl.getParameter(gl.VERSION),
    buffer: [gl.drawingBufferWidth, gl.drawingBufferHeight], dpr: devicePixelRatio,
    n: f.n, shown: f.mask.reduce((a, b) => a + b, 0), turning: f.rot.length,
    total: longshot.manifest.counts.objects, unplaced: (longshot.manifest.unplaced || []).length,
    shown: +(document.querySelector('#legend li[data-k=shown] .n')?.textContent || 'NaN').replace(/,/g, ''),
    has_field: document.documentElement.classList.contains('has-field'),
  };
})()"""

# Every rock on screen (the home view), drawn each animation frame; readPixels makes the GPU finish before the clock stops.
BENCH = """(async seconds => {
  const f = longshot.field, gl = f.gl, px = new Uint8Array(4), draw = [], gap = [];
  f.home();
  const lit = () => {
    const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, all = new Uint8Array(w * h * 4);
    f.draw(); gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, all);
    let k = 0; for (let i = 0; i < all.length; i += 4) if (all[i] > 24) k++;
    return k / (w * h);
  };
  const share = lit();
  let last = 0, t0 = 0;
  await new Promise(done => {
    const step = t => {
      if (last) gap.push(t - last); else t0 = t;
      last = t;
      const a = performance.now();
      f.draw(t); gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      draw.push(performance.now() - a);
      t - t0 < seconds * 1000 ? requestAnimationFrame(step) : done();
    };
    requestAnimationFrame(step);
  });
  const a = performance.now(), runs = 60;
  for (let i = 0; i < runs; i++) f.draw(a + i * 16);
  gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  return { draw, gap, burst: (performance.now() - a) / runs, lit: share, error: gl.getError() };
})(%s)"""

# Frames the app draws by itself in a second.
IDLE = """(async () => {
  const f = longshot.field, a = f.frames;
  await new Promise(r => setTimeout(r, 1000));
  return { frames: f.frames - a, speed: f.speed };
})()"""

# What one frame asks the GPU for: the instance count of each draw call.
DRAWS = """(() => { const f = longshot.field, gl = f.gl, real = gl.drawArraysInstanced, calls = [];
  gl.drawArraysInstanced = function (...a) { calls.push(a[3]); return real.apply(this, a); };
  f.hover(-1); f.draw(); delete gl.drawArraysInstanced; return calls; })()"""

# The first rock of each kind the marks must tell apart; -1 where the field has none. low and high: two estimated
# rocks a mission leaves unclear, one under 1% and one over 40% (surface work), for the check that no chance is drawn.
KINDS = """(() => { const f = longshot.field, c = f.cols;
  const find = t => { for (let i = 0; i < f.n; i++) if (t(c.state[i] & 3, i)) return i; return -1; };
  // measured and bound: plotted at the measured value
  return { measured: find(s => s === 3), bound: find(s => s === 2),
           prior: find(s => s === 1), unchecked: find(s => s === 0), held: find(s => s === 3),
           pass: find((s, i) => c.status_surface[i] === 2), fail: find((s, i) => c.status_surface[i] === 0),
           low: find((s, i) => s < 2 && c.status_surface[i] === 1 && c.pct_surface[i] === 0),
           high: find((s, i) => s < 2 && c.status_surface[i] === 1 && c.pct_surface[i] >= 40) }; })()"""

# Rock i drawn alone at zoom z (with a mission, or made faint): its brightest pixel, how many pixels are lit, how
# many of those are at a glow's brightness, how many are line (over 150), and the pixel at its centre. 0 to 255.
# Its mask is the app's unless dim is asked for.
SOLO = """((i, z, mission, dim) => { const f = longshot.field, gl = f.gl, keep = { ...f.V }, was = f.mission, held = f.mask[i];
  f.setMission(mission); if (dim) { f.mask[i] = 0; f.masked(); }
  const B = f.B, w = (B.x1 - B.x0) / z, h = (B.y1 - B.y0) / z;
  f.V = { x0: f.cols.dv[i] - w / 2, x1: f.cols.dv[i] + w / 2, y0: f.ly[i] - h / 2, y1: f.ly[i] + h / 2 }; f.clampView(); f.stale = true;
  f.draw(performance.now(), i);
  const dpr = gl.drawingBufferWidth / f.w, x = Math.round(f.sx(i) * dpr), y = Math.round(gl.drawingBufferHeight - f.sy(i) * dpr), R = Math.round(16 * dpr);
  const W = 2 * R + 1, px = new Uint8Array(W * W * 4), c = new Uint8Array(4);
  gl.readPixels(x - R, y - R, W, W, gl.RGBA, gl.UNSIGNED_BYTE, px);
  gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, c);
  let top = 0, lit = 0, halo = 0, core = 0;
  for (let k = 0; k < px.length; k += 4) { const v = px[k]; if (v > top) top = v; if (v > 20) lit++; if (v > 20 && v < 90) halo++; if (v > 150) core++; }
  if (dim) { f.mask[i] = held; f.masked(); }
  f.V = keep; f.setMission(was); f.changed(); f.draw();
  return { top, lit, halo, core, centre: c[0] }; })(%d, %s, %s, %s)"""

# The tip for rock i, as the pointer would show it.
TIP = """(i => { const f = longshot.field, t = document.querySelector('#tip'); f.hover(i);
  const text = t.hidden ? '' : t.textContent; f.hover(-1); return text; })(%d)"""
VIEW = "(() => { const V = longshot.field.V; return [+V.x0.toFixed(4), +V.y0.toFixed(4), +longshot.field.z.toFixed(4)]; })()"
SHOWN = "+(document.querySelector('#legend li[data-k=shown] .n')?.textContent || 'NaN').replace(/,/g, '')"
SUBMIT = "document.querySelector('#controls').requestSubmit()"
SELECTED = "!!document.querySelector('#readout #summary')"
OPEN = "!!document.querySelector('#readout .selected')"          # a selection, whether or not its entry has loaded
DEFAULT = "!!document.querySelector('#readout .named') && !document.querySelector('#readout #summary')"
# The legend line: its text, whether the estimated mark is the zoomed outline, and each item's count by its key
# (shown, measured, estimated, loose; with a mission type, viable, chance and not).
LEGEND = """(() => { const l = document.querySelector('#legend'); return { text: l.innerText.replace(/\\s+/g, ' ').trim(),
  zoomed: !!l.querySelector('.g-priorz'), glyphs: [...l.querySelectorAll('.g')].filter(g => !g.parentElement.closest('[aria-hidden]')).map(g => g.className),
  k: Object.fromEntries([...l.querySelectorAll('li[data-k]')].map(li => [li.dataset.k, +(li.querySelector('.n')?.textContent || 'NaN').replace(/,/g, '')])) }; })()"""
# Every visible text on the page and its computed colour. Two inks are allowed (docs/design.md section 4): white
# for content and #a8a8a8 for apparatus. Also let through: white turned over (black on a white ground, as a selected
# segment) and the edge grey on a control that is off (section 9). Each other colour is returned with where it is.
INKS = """(() => {
  const ok = new Set(['rgb(255, 255, 255)', 'rgb(168, 168, 168)']), seen = {}, bad = {};
  const ground = el => { for (let e = el; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor;
    if (c && c !== 'transparent' && !/rgba\\(.*, 0\\)$/.test(c)) return c; } return 'rgb(0, 0, 0)'; };
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t; (t = walk.nextNode());) {
    const text = t.textContent.trim(), el = t.parentElement;
    if (!text || !el || el.closest('script, style, noscript, .vh, [hidden], datalist, option') || !el.getClientRects().length) continue;
    const s = getComputedStyle(el);
    if (s.visibility !== 'visible' || +s.opacity === 0) continue;
    seen[s.color] = (seen[s.color] || 0) + 1;
    if (ok.has(s.color) || (s.color === 'rgb(0, 0, 0)' && ground(el) === 'rgb(255, 255, 255)')
        || (s.color === 'rgb(94, 94, 94)' && el.closest(':disabled'))) continue;
    const where = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '');
    (bad[s.color + ' ' + where] ||= []).push(text.slice(0, 40));
  }
  return { seen, bad: Object.entries(bad).map(([k, v]) => [k, v.length, v.slice(0, 3)]) }; })()"""
# The words a visitor reads on the front page: its visible text, the tip and the readout included.
WORDS = "document.body.innerText"
# docs/design.md section 3: words the surface does not use, and section 6: chances as <1% and >99%; nothing says now.
RETIRED = [r"\bnot measured\b", r"\bnot checked\b", r"\bno size\b", r"\blimit only\b", r"\buntested\b", r"\bpass(es|ed)?\b",
           r"\bfail(s|ed)?\b", r"\bsettle", r"\bunclear\b", r"\bruled out\b", r"\bverdicts?\b", r"\bfits\b", r"\btypical\b", r"\bsize\b", r"\bunder 1%", r"\bover 99%", r"\bnow\b",
           r"\bplotted \d", r"\blisted \d", r"delta-v(?! \(Δv\))"]
TABLE = """(() => { const t = document.querySelector('#table table'), body = t.tBodies[0];
  return { visible: !document.querySelector('#table').hidden && !!t.getClientRects().length, plot: !document.querySelector('#plot').hidden,
    heads: [...t.tHead.querySelectorAll('th')].map(th => th.textContent), sort: [...t.tHead.querySelectorAll('th')].map(th => th.getAttribute('aria-sort')),
    rows: body.rows.length, first: body.rows[0]?.textContent || '', glyphs: [...body.rows].filter(r => r.querySelector('.szc .g')).length,
    sel: body.querySelectorAll('tr.sel').length,
    pager: document.querySelector('#table .pager output')?.value || '' }; })()"""
COLUMN = """(k => { const t = document.querySelector('#table table'), th = [...t.tHead.rows[0].cells].findIndex(c => c.querySelector(`[data-sort="${k}"]`));
  return [...t.tBodies[0].rows].map(r => parseFloat(r.cells[th].textContent.replace(/^[^\\d]*/, ''))); })(%s)"""
SORT = """(k => { const b = document.querySelector(`#table [data-sort="${k}"]`), a = performance.now(); b.click(); return performance.now() - a; })(%s)"""
# Labels in the axes overlay that overlap one another. An axis tag may cover the axis title: it is drawn over it, on white.
OVERLAPS = """(() => { const s = [...document.querySelectorAll('#axes span:not(.ax-title)')].map(e => [e, e.getBoundingClientRect()]), hit = [];
  for (let a = 0; a < s.length; a++) for (let b = a + 1; b < s.length; b++) { const p = s[a][1], q = s[b][1];
    if (p.left < q.right - 1 && q.left < p.right - 1 && p.top < q.bottom - 1 && q.top < p.bottom - 1) hit.push([s[a][0].textContent, s[b][0].textContent]); }
  return hit; })()"""

ROCK = """(i => { const f = longshot.field, r = f.canvas.getBoundingClientRect(); return [r.left + f.sx(i), r.top + f.sy(i)]; })(%d)"""
SET = """((name, value) => { const f = document.querySelector('#controls'), el = f.elements[name];
  if (el instanceof RadioNodeList || el.type === 'radio') { const r = [...f.querySelectorAll(`[name="${name}"]`)].find(r => r.value === value); r.checked = true; r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); return; }
  el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); })(%s, %s)"""
CENTRE = "(sel => { const r = document.querySelector(sel).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })(%s)"


def quantile(values, q):
    s = sorted(values)
    return s[min(len(s) - 1, int(q * len(s)))]


def run(args):
    site = Path(args.site).resolve()
    out = Path(args.out).resolve()
    width, height = (int(v) for v in args.size.split("x"))
    report = {"site": str(site), "label": args.label, "checks": {}, "screens": []}
    checks = report["checks"]
    skipped = report["skipped"] = []
    q = lambda s: json.dumps(s)

    browser = None
    for mode in (["gpu", "software"] if args.gl == "auto" else [args.gl]):
        browser = Browser(args.chrome, GL_FLAGS[mode], (width, height))   # before the server: its threads and fork do not mix
        server, sent = serve(site)
        base = f"http://127.0.0.1:{server.server_address[1]}/"
        browser.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": args.dpr, "mobile": False})
        browser.send("Page.navigate", {"url": base + "index.html"})
        ready = browser.until("!!window.longshot && !!longshot.field && !!longshot.keys", 30)
        facts = browser.js(FACTS) if ready else None
        software = bool(facts) and any(s in facts["renderer"].lower() for s in SOFTWARE)
        if ready and not (args.gl == "auto" and mode == "gpu" and software):
            break
        if mode == "gpu" and args.gl == "auto":       # no GPU reached this way: fall back to software and say so
            browser.close()
            server.shutdown()
            continue
        report["error"] = "the field did not start: " + "; ".join(browser.problems())
        browser.close()
        return report, False

    def shot(name):
        report["screens"].append(browser.shot(out / f"{args.label}-{name}.png"))

    def settle(seconds=0.15):
        time.sleep(seconds)

    report["gl_mode"] = "software" if software else "gpu"
    report["webgl2"] = facts
    first = list(sent)
    report["first_screen"] = {
        "requests": [{"path": p, "status": s, "bytes": b,
                      "gzip": len(gzip.compress((site / p.split("?")[0].lstrip("/")).read_bytes(), 6)) if s == 200 else 0}
                     for p, s, b in first],
    }
    report["first_screen"]["bytes"] = sum(r["bytes"] for r in report["first_screen"]["requests"])
    report["first_screen"]["gzip"] = sum(r["gzip"] for r in report["first_screen"]["requests"])
    n, total = facts["n"], facts["total"]
    checks["webgl2 context"] = "WebGL 2" in facts["version"]
    checks["the page is marked once the field runs"] = facts["has_field"]
    checks["every rock in the draw"] = facts["shown"] == n > 0
    report["draw_calls"] = browser.js(DRAWS)
    checks["every rock in one draw call"] = report["draw_calls"] == [n]
    checks["the legend line says every rock is shown"] = facts["shown"] == n

    # frame times
    idle = browser.js(IDLE)
    bench = browser.js(BENCH % args.seconds, timeout=args.seconds + 120)
    report["frames"] = {
        "seconds": args.seconds, "count": len(bench["draw"]),
        "draw_ms_median": round(quantile(bench["draw"], 0.5), 2), "draw_ms_p95": round(quantile(bench["draw"], 0.95), 2),
        "interval_ms_median": round(quantile(bench["gap"], 0.5), 2), "interval_ms_p95": round(quantile(bench["gap"], 0.95), 2),
        "burst_ms_per_frame": round(bench["burst"], 3), "lit_share_of_pixels": round(bench["lit"], 4),
        "idle_frames_per_second_at_home": idle["frames"], "idle_speed_px_per_s": round(idle["speed"], 2),
    }
    checks["something is drawn"] = bench["lit"] > 0.001
    checks["no GL error"] = bench["error"] == 0
    if software:
        checks["a software renderer draws no frame unasked"] = idle["frames"] <= 1 and idle["speed"] == 0
    else:
        checks["the frame holds 60 a second with every rock on"] = report["frames"]["draw_ms_p95"] < 8 and report["frames"]["interval_ms_median"] < 18
    shot("home")

    manifest, columns, keys = read_field(site / "data" / "field.json")
    loose = manifest.get("unplaced") or []
    entries = [i for i, k in enumerate(keys) if (site / "a" / f"{k[0]}.html").exists()][:2]

    def expect(m="", dv=0.0, table=False):
        """The legend line's counts from the field file itself, as docs/design.md section 8 defines them."""
        ok = lambda v: not dv or v <= dv + 1e-6
        out = {"shown": 0, "measured": 0, "estimated": 0}
        if m:
            out.update(viable=0, chance=0, **{"not": 0})
        rest = 0
        for i in range(n):
            if not ok(columns["dv"][i]):
                continue
            status = columns[f"status_{m}"][i] if m else 1
            if status == 0:
                out["not"] += 1
                continue
            out["shown"] += 1
            out["measured" if columns["state"][i] & 3 >= 2 else "estimated"] += 1
            if m:
                out["viable" if status == 2 else "chance"] += 1
        for row in loose:
            if ok(row[4]):
                rest += 1                   # no rock: counted apart in every state, never as not viable
        out["loose"] = rest                 # always in the key, 0 when the filters leave none
        if rest:
            if table and not m:
                out["shown"] += rest        # rows of the table, until a mission type leaves them out
        return out

    def legend_matches(m="", dv=0.0, table=False):
        got = browser.js(LEGEND)
        want = expect(m, dv, table)
        report.setdefault("legends", []).append({"m": m, "dv": dv, "table": table, "text": got["text"], "want": want})
        return got["k"] == want, got

    # ---- the marks: one set, the size row alone sets them; the glow is on measured outlines only
    kinds = report["kinds"] = browser.js(KINDS)
    inks, said = {}, {}                                              # front-page states: computed inks, visible words
    report["inks"] = inks
    inks["home"], said["home"] = browser.js(INKS), browser.js(WORDS)
    solo = lambda i, z=1, mission="", dim=False: browser.js(SOLO % (i, z, q(mission), q(dim)))
    marks = report["marks"] = {}
    if kinds["measured"] >= 0:
        marks["measured"] = solo(kinds["measured"])
        marks["measured_dimmed"] = solo(kinds["measured"], dim=True)
        checks["a measured size is a bright outline with a glow"] = marks["measured"]["top"] > 235 and marks["measured"]["halo"] >= 40
        marks["measured_zoomed"] = solo(kinds["measured"], 8)
        checks["zoomed in, marks grow: a measured rock at 8x lights more pixels than at 1x"] = marks["measured_zoomed"]["lit"] > 1.8 * marks["measured"]["lit"]
        checks["a rock out of the filter is faint, without its glow"] = marks["measured_dimmed"]["top"] < 60 and marks["measured_dimmed"]["lit"] < marks["measured"]["lit"] / 2
    if kinds["bound"] >= 0:
        marks["bound"] = solo(kinds["bound"])
        checks["a bound is a white outline with no glow"] = marks["bound"]["top"] > 200 and marks["bound"]["halo"] < marks.get("measured", {"halo": 80})["halo"] / 2
    else:
        skipped.append("a bound's outline: no rock has only a bound on its size")
    if kinds["prior"] >= 0:
        marks["prior"], marks["prior_zoomed"] = solo(kinds["prior"]), solo(kinds["prior"], 8)
        p1, p8 = marks["prior"], marks["prior_zoomed"]
        checks["estimated is a half-bright dot at home and a half-bright outline zoomed in, neither glowing"] = (
            130 < p1["top"] <= 172 and p1["lit"] <= 16 and 120 < p8["top"] <= 172 and p8["lit"] > 2 * p1["lit"] and p8["centre"] < 30
            and ("measured_zoomed" not in marks or marks["measured_zoomed"]["lit"] > 1.5 * p8["lit"]))
        marks["prior_dimmed"] = solo(kinds["prior"], dim=True)
        checks["a faint estimate is a sixth of an estimate"] = marks["prior_dimmed"]["top"] < 0.25 * p1["top"]
    if kinds["unchecked"] >= 0:
        marks["unchecked"], marks["unchecked_zoomed"] = solo(kinds["unchecked"]), solo(kinds["unchecked"], 8)
        u1, u8 = marks["unchecked"], marks["unchecked_zoomed"]
        # a source not checked is an estimate on the surface: the same mark, never a third state
        checks["a size not checked is drawn as an estimate"] = (
            130 < u1["top"] <= 172 and u1["lit"] <= 16 and 120 < u8["top"] <= 172 and u8["centre"] < 30
            and ("prior" not in marks or (abs(u1["top"] - marks["prior"]["top"]) <= 12 and abs(u8["top"] - marks["prior_zoomed"]["top"]) <= 12)))

    # ---- the tip says what the field file may say, in the surface's words
    tips = report["tips"] = {k: browser.js(TIP % i) for k, i in kinds.items() if i >= 0 and k in ("measured", "held", "prior", "unchecked")}
    if "held" in tips:
        # a measurement is its value alone, never a 90% range beside the measured word (its ±1σ is on the entry)
        checks["a measured size is printed as its value, with no range"] = (
            bool(re.search(r"Diameter [\d.,]+ m measured", tips["held"])) and "90% range" not in tips["held"])
    for kind in ("prior", "unchecked"):
        if kind in tips:
            checks[f"the tip calls an estimate ({kind}) estimated, never measured"] = (
                bool(re.search(r"Diameter [\d.,]+–[\d.,]+ m 90% range, estimated", tips[kind])) and "measured" not in tips[kind])
    i0 = kinds["prior"] if kinds["prior"] >= 0 else 0
    x, y = (round(v) for v in browser.js(ROCK % i0))
    browser.mouse("mouseMoved", x, y)
    settle()
    hot = browser.js("longshot.field.hot")
    tip = report["tip"] = browser.js("document.querySelector('#tip').hidden ? '' : document.querySelector('#tip').textContent")
    checks["hover shows a tip for the rock under the pointer"] = hot >= 0 and (keys[hot][2] or keys[hot][1]) in tip and "km/s" in tip

    # ---- zoom: wheel, drag, buttons, keys; the axes follow and the dots turn into outlines
    same, legend = legend_matches()
    report["legend_home"] = legend["text"]
    checks["the legend line counts what the field file holds: shown, its two marks, and those with no brightness"] = (
        same and not legend["zoomed"] and legend["k"]["measured"] + legend["k"]["estimated"] == legend["k"]["shown"] == n
        and legend["k"].get("loose", 0) == len(loose) and "No brightness" in legend["text"] and "(not drawn)" in legend["text"]
        and legend["text"].startswith(f"{n:,} of {total:,} reachable asteroids"))
    checks["the legend names the two marks, and the plotted estimate is its median"] = (
        all(w in legend["text"] for w in ("Diameter", "Measured", "Estimated from brightness")) and legend["glyphs"] == ["g g-measured", "g g-prior"])
    checks["no zoom factor is shown"] = browser.js("![...document.querySelectorAll('.zoom, .zoom *')].some(e => /\\d\\s*[×x]$/.test(e.textContent.trim()))")
    before = browser.js("document.querySelector('#axes').textContent")
    x1, y1 = browser.js(ROCK % i0)
    browser.mouse("mouseWheel", x, y, deltaX=0, deltaY=-600)
    settle()
    z = browser.js("longshot.field.z")
    checks["wheel zooms and the axes follow"] = z > 1 and browser.js("document.querySelector('#axes').textContent") != before
    x2, y2 = browser.js(ROCK % i0)
    checks["zoom holds the point under the pointer"] = abs((x2 - x) - (x1 - x) * z) < 0.5 and abs((y2 - y) - (y1 - y) * z) < 0.5
    checks["zoomed in, a one-finger drag pans instead of scrolling the page"] = browser.js("longshot.field.canvas.style.touchAction") == "none"
    x, y = round(x2), round(y2)
    browser.mouse("mouseMoved", x, y)
    browser.mouse("mousePressed", x, y, button="left", clickCount=1)
    dx, dy = (-60 if x > width / 2 else 60), (-40 if y > height / 2 else 40)
    browser.mouse("mouseMoved", x + dx / 2, y + dy / 2, buttons=1)
    browser.mouse("mouseMoved", x + dx, y + dy, buttons=1)
    browser.mouse("mouseReleased", x + dx, y + dy, button="left", clickCount=1)
    settle()
    x3, y3 = browser.js(ROCK % i0)
    checks["drag pans without selecting"] = abs(x3 - x2 - dx) < 0.5 and abs(y3 - y2 - dy) < 0.5 and "a=" not in browser.js("location.search")
    browser.js("longshot.field.home()")
    settle()
    for name in ("zoom-in", "zoom-in"):
        browser.click(*browser.js(CENTRE % q(f"[name={name}]")))
    settle()
    four = browser.js("longshot.field.z")
    legend = browser.js(LEGEND)
    checks["+ doubles the zoom, and from 4x the legend's estimated mark is an outline"] = abs(four - 4) < 1e-6 and legend["zoomed"]
    shot("zoom4")
    browser.click(*browser.js(CENTRE % q("[name=zoom-out]")))
    settle()
    two = browser.js("longshot.field.z")
    browser.click(*browser.js(CENTRE % q("[name=zoom-reset]")))
    settle()
    home = browser.js("[longshot.field.z, document.querySelector('[name=zoom-reset]').disabled, document.querySelector('[name=zoom-out]').disabled, longshot.field.canvas.style.touchAction]")
    checks["− halves it, Reset goes home and both are then off"] = abs(two - 2) < 1e-6 and home == [1, True, True, "pan-y"]
    browser.js("longshot.field.canvas.focus()")
    browser.key("+", "Equal", 187)
    k1 = browser.js("longshot.field.z")
    browser.key("ArrowRight", vk=39)
    v1 = browser.js(VIEW)
    browser.key("0", "Digit0", 48)
    checks["keys: + zooms, arrows pan once zoomed, 0 goes home"] = abs(k1 - 2) < 1e-6 and v1[2] == 2 and browser.js("longshot.field.z") == 1
    browser.js("longshot.field.zoom(1e9)")
    settle()
    labels = report["ticks_at_full_zoom"] = browser.js("({ z: longshot.field.z, x: [...document.querySelectorAll('#axes .ax-t')].filter(e => e.style.transform.includes('translateX')).map(e => e.textContent), y: [...document.querySelectorAll('#axes .ax-t')].filter(e => !e.style.transform.includes('translateX')).map(e => e.textContent) })")
    checks["zoom stops at 32x, and its ticks still read: two or more, each once"] = (
        labels["z"] == 32 and len(labels["x"]) >= 2 and len(labels["y"]) >= 2 and len(set(labels["y"])) == len(labels["y"])
        and all(re.fullmatch(r"\d+(\.\d{1,2})?", v) for v in labels["x"]))
    shot("zoom32")
    browser.js("longshot.field.home()")
    settle()

    # the browser's own keys and the other mouse buttons are left alone
    taken = browser.js("""(() => { const c = longshot.field.canvas, z = longshot.field.z, hit = [];
        for (const init of [{ key: '0', ctrlKey: true }, { key: '=', ctrlKey: true }, { key: '-', ctrlKey: true }, { key: '0', metaKey: true },
                            { key: 'ArrowLeft', altKey: true }, { key: 'Enter', ctrlKey: true }]) {
          const e = new KeyboardEvent('keydown', { ...init, bubbles: true, cancelable: true });
          c.dispatchEvent(e); if (e.defaultPrevented) hit.push(init);
        }
        return { hit, moved: longshot.field.z !== z }; })()""")
    checks["Ctrl, Meta and Alt chords on the field are the browser's"] = not taken["hit"] and not taken["moved"]
    x, y = (round(v) for v in browser.js(ROCK % i0))
    for button, held in (("right", 2), ("middle", 4)):
        browser.mouse("mouseMoved", x, y)
        browser.mouse("mousePressed", x, y, button=button, buttons=held, clickCount=1)
        browser.mouse("mouseReleased", x, y, button=button, clickCount=1)
    settle(0.2)
    checks["right and middle clicks select nothing"] = "a=" not in browser.js("location.search") and browser.js(DEFAULT)

    # ---- the mission type never moves the chart: the legend keeps one height in every state (docs/design.md section 8)
    PLOT = "(() => { const r = document.querySelector('#plot').getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)]; })()"
    boxes = []
    for m in ("", "surface", "capture", ""):
        browser.js(SET % (q("m"), q(m)))
        settle()
        boxes.append(tuple(browser.js(PLOT)))
    report["plot_by_mission"] = boxes
    checks["switching the mission type never moves or resizes the chart"] = len(set(boxes)) == 1

    # ---- filters, the legend and the URL
    browser.js(SET % (q("m"), q("surface")))
    settle()
    same, legend = legend_matches("surface")
    report["legend_with_mission"] = legend["text"]
    checks["mission type is in the URL, and the legend counts what is shown, then viable, estimated and not viable"] = (
        "m=surface" in browser.js("location.search") and same and browser.js("longshot.field.mission") == "surface"
        and legend["k"]["shown"] + legend["k"]["not"] + legend["k"].get("loose", 0) == total and legend["k"]["viable"] + legend["k"]["chance"] == legend["k"]["shown"]
        and all(w in legend["text"] for w in ("Mission viability", "Viable", "Not viable"))
        and f"of {total:,} reachable asteroids" in legend["text"])
    # docs/design.md section 4: a mission changes which asteroids are in the filter, not how certainty is drawn
    if kinds["pass"] >= 0 and kinds["fail"] >= 0:
        masks = browser.js(f"[longshot.field.mask[{kinds['pass']}], longshot.field.mask[{kinds['fail']}]]")
        marks["fits"], marks["fits_without"] = solo(kinds["pass"], 1, "surface"), solo(kinds["pass"], 1, "")
        # at 8x, where the rock is large enough that a seam between the fill and its line would show as a dark ring
        marks["fits8"], marks["fits_without8"] = solo(kinds["pass"], 8, "surface"), solo(kinds["pass"], 8, "")
        marks["ruled_out"] = solo(kinds["fail"], 1, "surface")
        # viable: filled (lit at its centre, where an outline is dark), outline and glow kept; not viable: faint
        checks["with a mission type, a viable rock is filled and keeps its glow, and one not viable is faint"] = (
            masks == [1, 0] and marks["fits"]["top"] > 235 and (marks["fits"]["halo"] >= 25) == (columns["state"][kinds["pass"]] & 3 == 3)
            and marks["fits"]["centre"] > 200 and marks["fits_without"]["centre"] < 60
            and marks["fits"]["core"] > 1.5 * marks["fits_without"]["core"] and marks["ruled_out"]["top"] < 60
            and marks["fits8"]["core"] > 4 * marks["fits_without8"]["core"] and marks["fits8"]["halo"] < marks["fits_without8"]["halo"])
    if kinds["low"] >= 0 and kinds["high"] >= 0:
        marks["unclear_low"], marks["unclear_high"] = solo(kinds["low"], 1, "surface"), solo(kinds["high"], 1, "surface")
        checks["no brightness follows a mission's chance: an unclear estimate under 1% and one over 40% look alike"] = (
            abs(marks["unclear_low"]["top"] - marks["unclear_high"]["top"]) <= 12 and abs(marks["unclear_low"]["lit"] - marks["unclear_high"]["lit"]) <= 6)
    else:
        skipped.append("no chance in the brightness: no two estimated unclear rocks under 1% and over 40%")
    inks["mission"] = browser.js(INKS)
    said["mission"] = browser.js(WORDS)
    shot("mission")
    browser.js(SET % (q("dv"), q("6")))
    settle()
    shown = browser.js("longshot.field.mask.reduce((a, b) => a + b, 0)")
    want = expect("surface", 6.0)
    same, legend = legend_matches("surface", 6.0)
    checks["Max Δv makes the rocks over it faint, still drawn, and is in the URL"] = (
        shown == want["shown"] < n and "dv=6" in browser.js("location.search") and browser.js(DRAWS) == [n] and same
        and "Max Δv 6.0 km/s" in browser.js("document.querySelector('#axes').textContent")
        and browser.js("document.querySelector('#controls [name=dv-value]').value") == "6.0")
    shot("ceiling")
    browser.js("history.back()")
    checks["back restores Max Δv"] = browser.until(
        "!location.search.includes('dv=') && longshot.field.mask.every((v, i) => v === (longshot.cols.status_surface[i] ? 1 : 0))", 5)
    browser.js("history.back()")
    checks["back restores the mission"] = browser.until("!location.search && document.querySelector('#controls').elements.m.value === ''", 5)
    report["after_back"] = browser.js("[location.search, document.querySelector('#controls').elements.m.value, history.length]")
    browser.js("history.forward()")
    checks["forward brings the mission back"] = browser.until(
        "location.search === '?m=surface' && longshot.field.mission === 'surface' && document.querySelector('#controls').elements.m.value === 'surface'", 5)
    browser.js("history.back()")
    browser.until("!location.search", 5)

    # a ceiling in the address is held to the slider's range and steps, and the address then says what is shown
    edge = {}
    for query in ("?dv=99&m=bogus", "?dv=-1", "?dv=abc", "?dv=6.26"):
        browser.js(f"history.pushState(null, '', {q(query)}); dispatchEvent(new PopStateEvent('popstate'))")
        edge[query] = browser.js("({ dv: longshot.state.dv, search: location.search, slider: +document.querySelector('#controls').elements.dv.value,"
                                 " min: +document.querySelector('#controls').elements.dv.min, max: +document.querySelector('#controls').elements.dv.max })")
    report["url_edges"] = edge
    checks["a ceiling in the address is held to the slider's range"] = (
        edge["?dv=99&m=bogus"]["dv"] == 0 and edge["?dv=99&m=bogus"]["search"] == ""
        and edge["?dv=-1"]["dv"] == edge["?dv=-1"]["min"] and edge["?dv=-1"]["search"] == f"?dv={edge['?dv=-1']['min']:g}"
        and edge["?dv=abc"]["search"] == "" and edge["?dv=6.26"]["dv"] == edge["?dv=6.26"]["slider"] == 6.3)
    browser.js("history.pushState(null, '', location.pathname); dispatchEvent(new PopStateEvent('popstate'))")
    settle()

    # ---- selection: the readout's named list gives way to the entry's summary, and Close brings it back
    if entries:
        i = entries[0]
        browser.js("longshot.field.canvas.focus()")
        x, y = browser.js(ROCK % i)
        browser.click(x, y)
        opened = browser.until(f"location.search.includes('a={keys[i][0]}') && {SELECTED}", 10)
        checks["a click on a rock puts its entry's summary in the readout"] = opened and keys[i][1] in browser.js("document.querySelector('#readout').textContent")
        settle()
        tags = browser.js("[...document.querySelectorAll('#axes .ax-tag')].map(e => e.textContent)")
        # the tags are on the axes, in the axes' units
        checks["the selected rock gets a crosshair and its tags on the axes, over no tick label"] = (
            browser.js("longshot.field.sel") == i and len(tags) == 2 and f"{columns['dv'][i]:.3f}" in tags
            and not any("km/s" in t or " m" in t for t in tags) and not browser.js(OVERLAPS))
        report["tags"] = tags
        report["overlaps"] = browser.js(OVERLAPS)
        inks["selected"], said["selected"] = browser.js(INKS), browser.js(WORDS)
        shot("selected")
        # zoomed in on it, the crosshair still stops short of the rock, which has grown with the zoom
        gaps = browser.js("""(async () => { const f = longshot.field, i = f.sel, frame = () => new Promise(r => requestAnimationFrame(r));
            f.zoom(16 / f.z, f.sx(i), f.sy(i)); await frame(); await frame();
            const d = [...document.querySelectorAll('#axes svg path')].map(p => p.getAttribute('d')).find(d => /H/.test(d) && /V/.test(d)) || '';
            const n = (d.match(/-?[0-9.]+/g) || []).map(Number);
            return { reach: 8 * f.s, left: f.sx(i) - n[2], below: n[4] - f.sy(i), z: f.z }; })()""")
        report["crosshair_zoomed"] = gaps
        checks["zoomed in on the selected rock, the crosshair stops short of it"] = (
            gaps["z"] > 8 and gaps["left"] > gaps["reach"] + 1 and gaps["below"] > gaps["reach"] + 1)
        shot("selected-zoomed")
        browser.js("longshot.field.home()")
        settle()
        browser.click(*browser.js(CENTRE % q("#readout [data-close]")))
        checks["Close restores the named list and gives the focus back"] = browser.until(
            f"{DEFAULT} && !location.search.includes('a=') && longshot.field.sel === -1 && document.activeElement.id === 'field'", 5)
        named = browser.js("(() => { const a = document.querySelector('#readout .named a'); if (!a) return null; const r = a.getBoundingClientRect();"
                           " return [r.left + r.width / 2, r.top + r.height / 2, a.getAttribute('href'), a.textContent]; })()")
        if named:
            path = browser.js("location.pathname")
            browser.click(named[0], named[1])
            key = re.search(r"a/([^/]+)\.html", named[2]).group(1)
            checks["a named asteroid's link selects it in place"] = browser.until(
                f"location.pathname === {q(path)} && location.search.includes('a={key}') && {SELECTED}", 10)
            if len(entries) > 1:
                browser.js(f"longshot.select({q(keys[entries[1]][0])}, false)")
                browser.until(f"location.search.includes('a={keys[entries[1]][0]}') && {SELECTED}", 10)
                browser.js("history.back()")
                checks["back returns to the asteroid before"] = browser.until(f"location.search.includes('a={key}') && {SELECTED}"
                                                                              f" && document.querySelector('#readout').textContent.includes({q(named[3])})", 10)
        browser.js("document.querySelector('#controls').elements.q.focus()")
        browser.key("Escape", vk=27)
        settle(0.2)
        checks["Escape in the search box leaves the summary open"] = browser.js(SELECTED)
        browser.js("document.activeElement?.blur()")
        browser.key("Escape", vk=27)
        checks["Escape closes it"] = browser.until(DEFAULT + " && !location.search.includes('a=')", 5)

        # search: a designation narrows the rocks drawn at full strength; Enter opens the exact match first
        def search(text):
            browser.js(SET % (q("q"), q(text)))
            shown, line = browser.js("longshot.field.mask.reduce((a, b) => a + b, 0)"), browser.js(SHOWN)
            browser.js("document.querySelector('#controls').elements.q.focus()")
            browser.js(SUBMIT)
            settle(0.3)
            got = {"shown": shown, "count": line, "opened": browser.js("longshot.state.a"),
                   "msg": browser.js("document.querySelector('#controls .find-msg')?.textContent || ''"), "readout": browser.js(SELECTED)}
            browser.js("document.activeElement?.blur()")
            browser.key("Escape", vk=27)
            browser.until(DEFAULT, 5)
            browser.js(SET % (q("q"), q("")))
            return got

        norm = lambda text: re.sub(r"[^a-z0-9]", "", text.lower())
        where = {norm(k[1]): m for m, k in enumerate(keys)}
        pair = next(((where[norm(k[1])[:-cut]], m) for m, k in enumerate(keys) for cut in (1, 2)
                     if where.get(norm(k[1])[:-cut], -1) > m), None)
        got = report["search_designation"] = search(keys[i][1])
        checks["search dims the rest and Enter opens the match"] = 1 <= got["shown"] < n and got["opened"] == keys[i][0]
        if pair:
            exact, longer = pair
            got = report["search_exact"] = search(keys[exact][1])
            checks[f"Enter on {keys[exact][1]} opens it, not {keys[longer][1]}"] = got["opened"] == keys[exact][0] and got["shown"] >= 2
        else:
            skipped.append("Enter on a designation that starts another: no such pair")
        numbered = next((m for m, k in enumerate(keys) if k[3]), None)
        if numbered is not None:
            got = report["search_number"] = search(str(keys[numbered][3]))
            checks["search finds a number and Enter opens it"] = got["shown"] >= 1 and got["opened"] == keys[numbered][0]
        named_i = next((m for m, k in enumerate(keys) if k[2]), None)
        if named_i is not None:
            got = report["search_name_first"] = search(f"{keys[named_i][2]} {keys[named_i][1]}")
            checks["a name and its designation match in either order"] = got["shown"] >= 1 and got["opened"] == keys[named_i][0]
        if loose:
            got = report["search_unplaced"] = search(loose[0][1])
            checks["an asteroid with no rock is found by search and opens in the readout"] = (
                got["opened"] == loose[0][0] and "no brightness on file" in got["msg"] and got["shown"] == 0 and got["readout"])
        # a shared link opens on its summary, mission and ceiling
        browser.send("Page.navigate", {"url": f"{base}index.html?a={keys[i][0]}&m=capture&dv=9"})
        checks["a shared link restores the summary, mission and ceiling"] = browser.until(
            f"window.longshot && longshot.field.sel === {i} && longshot.field.mission === 'capture' && longshot.state.dv === 9 && {SELECTED}", 20)
        browser.send("Page.navigate", {"url": base + "index.html"})
        browser.until("!!window.longshot && !!longshot.keys", 20)
    else:
        skipped.append("selection: the site has no entry pages")

    # ---- the table view: the same filters as rows, 50 a page, sortable
    browser.js(SET % (q("view"), q("table")))
    settle()
    t = report["table"] = browser.js(TABLE)
    same, legend = legend_matches(table=True)
    checks["Table lists every asteroid in pages of 50, in place of the chart"] = (
        t["visible"] and not t["plot"] and t["rows"] == min(50, total) and "view=table" in browser.js("location.search")
        and legend["k"]["shown"] == total and t["pager"] == f"Rows 1–{min(50, total)} of {total:,}")
    checks["each diameter in the table carries its mark, and the legend line counts the rows"] = t["glyphs"] == t["rows"] and same
    # docs/design.md section 6: "Quantity (unit)" in the header, the unit never in the cells
    checks["the table's headings are the surface's, with each unit once"] = (
        t["heads"] == ["Asteroid", "Δv (km/s)", "Diameter (m)", "Mission viability",
                       *(m["label"] for m in manifest.get("missions", []))]
        and "Estimated from brightness" in legend["text"] and "(not drawn)" not in legend["text"]
        and not re.search(r"km/s|\d m\b|—", browser.js("document.querySelector('#table tbody').textContent")))
    inks["table"], said["table"] = browser.js(INKS), browser.js(WORDS)
    first = browser.js(COLUMN % q("dv"))
    checks["the table starts by delta-v, lowest first"] = first == sorted(first) and t["sort"][1] == "ascending"
    ms = browser.js(SORT % q("dv"))
    down = browser.js(COLUMN % q("dv"))
    t2 = browser.js(TABLE)
    report["table_sort_ms"] = round(ms, 2)
    checks["a heading sorts the other way, every row, in under 50 ms"] = (
        down == sorted(down, reverse=True) and t2["sort"][1] == "descending" and "sort=-dv" in browser.js("location.search") and ms < 50)
    browser.js(SORT % q("size"))
    sizes = browser.js("longshot.rows().slice(0, 50).map(r => r < longshot.field.n ? longshot.cols.size_q50[r] : -1)")
    checks["sorting by size puts the largest first"] = sizes == sorted(sizes, reverse=True) and browser.js(TABLE)["sort"][2] == "descending"
    browser.click(*browser.js(CENTRE % q("[name=page-next]")))
    settle()
    t3 = browser.js(TABLE)
    checks["Next shows the next 50, and the page is in the URL"] = t3["pager"].startswith("Rows 51–") and "page=2" in browser.js("location.search")
    browser.click(*browser.js(CENTRE % q("[name=page-prev]")))
    browser.js(SET % (q("m"), q("capture")))
    settle()
    t4 = browser.js(TABLE)
    want = manifest["counts"]["missions"]["capture"]["pass"] + manifest["counts"]["missions"]["capture"]["untested"] if "missions" in manifest["counts"] else None
    same, legend = legend_matches("capture", table=True)
    listed = legend["k"].get("shown")
    # each row's overall viability: the last cell's value, without the words a screen reader alone hears
    overall = browser.js("[...document.querySelectorAll('#table tbody tr')].map(r => r.cells[r.cells.length - 1].querySelector('.vc')?.lastChild?.textContent)")
    capture = next((m for m in manifest.get("missions", []) if m["id"] == "capture"), {"label": "", "gates": []})
    report.setdefault("debug", {}).update(listed=listed, want=want, heads=t4["heads"], sort=t4["sort"])
    checks["with a mission type the table lists the viable and the estimated, its conditions, then Overall, likeliest first"] = (
        (want is None or listed == want) and same
        and t4["heads"] == ["Asteroid", "Δv (km/s)", "Diameter (m)", f'{capture["label"]} viability', *(g["short"] for g in capture["gates"]), "Overall"]
        and t4["sort"][-1] == "descending" and "m=capture" in browser.js("location.search")
        and bool(overall) and all(v == "Yes" or re.fullmatch(r"<1%|>99%|[1-9]\d?%", v or "") for v in overall))
    # a chance carries the estimate's dot; Yes and No are measured and carry none
    chances = browser.js("[...document.querySelectorAll('#table td.mis .vc')].map(e => [!!e.querySelector('.g-prior'), e.lastChild?.textContent || ''])")
    checks["chances read as 16%, <1% or >99%, with the estimate's dot; Yes and No have no mark"] = bool(chances) and all(
        (dot and re.fullmatch(r"<1%|>99%|[1-9]\d?%", v)) or (not dot and v in ("Yes", "No")) for dot, v in chances)
    shot("table-capture")
    if entries:
        browser.js(SET % (q("q"), q(keys[entries[0]][1])))
        browser.js(SET % (q("m"), q("")))
        settle()
        link = browser.js(CENTRE % q("#table td.ast a"))
        browser.click(*link)
        checks["search narrows the table, and an asteroid's link opens its summary with its row marked"] = (
            browser.until(f"{SELECTED} && location.search.includes('a={keys[entries[0]][0]}')", 10) and browser.js(TABLE)["sel"] == 1
            and 1 <= browser.js(SHOWN) < 50 and browser.js(TABLE)["rows"] < 50)
        shot("table-selected")
        browser.js("document.activeElement?.blur()")
        browser.key("Escape", vk=27)
        browser.js(SET % (q("q"), q("")))
    browser.send("Page.navigate", {"url": f"{base}index.html?view=table&sort=-size&page=2&m=surface"})
    checks["a shared link restores the table, its sort and its page"] = browser.until(
        "window.longshot && !!longshot.keys && document.querySelector('#table .pager output')?.value.startsWith('Rows 51–')"
        " && document.querySelector('#table th[aria-sort=descending] [data-sort=size]') !== null", 20)
    browser.js(SET % (q("view"), q("chart")))
    settle()
    checks["Chart brings the field back"] = browser.js("!document.querySelector('#plot').hidden && document.querySelector('#table').hidden && longshot.field.w > 0")
    browser.send("Page.navigate", {"url": base + "index.html"})
    browser.until("!!window.longshot && !!longshot.keys", 20)

    # ---- keyboard: Shift and an arrow move between rocks, Enter opens one
    browser.js("longshot.field.canvas.focus()")
    browser.key("ArrowRight", vk=39)
    first_hot = browser.js("longshot.field.hot")
    browser.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39, "modifiers": 8})
    browser.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39, "modifiers": 8})
    second_hot = browser.js("longshot.field.hot")
    moved_right = browser.js(f"longshot.field.sx({second_hot}) > longshot.field.sx({first_hot})") if min(first_hot, second_hot) >= 0 else False
    checks["arrow keys move between rocks"] = first_hot >= 0 and second_hot >= 0 and second_hot != first_hot and moved_right
    browser.key("Enter", vk=13)
    checks["Enter opens the rock under the cursor"] = browser.until(f"longshot.state.a === {q(keys[second_hot][0])} && {OPEN}", 5)
    browser.key("Escape", vk=27)
    browser.until(DEFAULT, 5)

    # ---- the chart's focus ring: Tab brings it, Escape after a click does not
    RING = "document.activeElement === longshot.field.canvas && getComputedStyle(longshot.field.canvas).outlineStyle !== 'none'"
    if entries:
        browser.click(*browser.js(ROCK % entries[0]))
        browser.until(SELECTED, 10)
        browser.key("Escape", vk=27)
        browser.until(DEFAULT, 5)
        quiet = browser.js("document.activeElement === longshot.field.canvas") and not browser.js(RING)
        checks["Escape after a click hands the focus back to the chart without a ring round it"] = quiet
    for modifiers in (8, 0):                                           # Shift+Tab off the chart, then Tab back onto it
        for kind in ("keyDown", "keyUp"):
            browser.send("Input.dispatchKeyEvent", {"type": kind, "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9, "modifiers": modifiers})
    checks["Tab onto the chart rings it"] = browser.js(RING)
    browser.js("document.activeElement?.blur()")

    # ---- motion: stops when asked to; stops when nothing in view turns
    browser.send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
    still = browser.js(IDLE)
    checks["reduced motion stops the turning"] = still["speed"] == 0 and still["frames"] <= 1
    browser.send("Emulation.setEmulatedMedia", {"features": []})
    fast = browser.js("""(async () => { const f = longshot.field; let best = -1;
        for (const i of f.rot) if ((f.cols.state[i] & 3) && (best < 0 || f.cols.period_s[i] < f.cols.period_s[best])) best = i;
        if (best < 0) return null;
        f.V = { x0: f.cols.dv[best] - 0.1, x1: f.cols.dv[best] + 0.1, y0: f.ly[best] - 0.05, y1: f.ly[best] + 0.05 }; f.zoom(1); f.zoom(8 / f.z);
        const a = f.frames; await new Promise(r => setTimeout(r, 1000));
        return { frames: f.frames - a, speed: f.speed, period: f.cols.period_s[best] }; })()""")
    if fast:
        report["frames"]["frames_per_second_zoomed_on_fastest"] = fast["frames"]
        report["frames"]["outline_px_per_second_zoomed_on_fastest"] = round(fast["speed"], 1)
        if software:
            checks["a software renderer turns nothing unasked, even close up"] = fast["frames"] <= 1
        elif fast["speed"] >= 0.1:
            # a frame each time the fastest outline in view has moved a fifth of a px: 5 a second per px a second.
            # Each wait also holds the browser's wait for its next frame, so allow down to 80% of that rate.
            checks["a turning rock in view keeps the frames coming, and no more than it needs"] = (
                max(1, 0.8 * min(60, 5 * fast["speed"]) - 2) <= fast["frames"] <= min(61, 5 * fast["speed"] + 2))
        shot("close")
    hidden = browser.js("""(async () => { const f = longshot.field, wait = ms => new Promise(r => setTimeout(r, ms));
        const show = v => { Object.defineProperty(document, 'hidden', { value: v, configurable: true }); document.dispatchEvent(new Event('visibilitychange')); };
        show(true); await wait(1000);
        const a = f.frames; await wait(500); const during = f.frames - a;
        show(false); f.changed(); await wait(500); delete document.hidden;
        return { during, after: f.frames - a - during }; })()""")
    report["frames"]["hidden_tab"] = hidden
    checks["a hidden tab draws nothing, and starts again when shown"] = hidden["during"] == 0 and hidden["after"] >= 1
    browser.js("longshot.field.home()")

    # a lost context comes back
    lost = browser.js("""(async () => { const f = longshot.field, gl = f.gl, ext = gl.getExtension('WEBGL_lose_context');
        if (!ext) return null;
        ext.loseContext(); await new Promise(r => setTimeout(r, 200));
        const during = gl.isContextLost(); f.home(); f.hover(0);
        ext.restoreContext(); await new Promise(r => setTimeout(r, 500));
        const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, all = new Uint8Array(w * h * 4);
        f.draw(); gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, all);
        let k = 0; for (let i = 0; i < all.length; i += 4) if (all[i] > 24) k++;
        return { during, lit: k / (w * h), error: gl.getError() }; })()""")
    if lost:
        checks["a lost context is restored and drawn again"] = lost["during"] and lost["lit"] > 0.001 and lost["error"] == 0

    # a change of pixel ratio alone, as when a window moves between screens
    browser.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": args.dpr * 2, "mobile": False})
    browser.mouse("mouseMoved", width // 3, height // 2)
    browser.mouse("mouseMoved", width // 3 + 40, height // 2 + 40)
    checks["the canvas follows a change of pixel ratio"] = browser.until(
        f"longshot.field.gl.drawingBufferWidth === Math.round(longshot.field.w * {args.dpr * 2})", 5)
    browser.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": args.dpr, "mobile": False})
    browser.js("longshot.field.changed()")
    browser.until(f"longshot.field.gl.drawingBufferWidth === Math.round(longshot.field.w * {args.dpr})", 5)

    # ---- a phone: the page scrolls past the chart at home; a tap selects; a pinch zooms; then a finger pans
    browser.send("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 3, "mobile": True})
    browser.send("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
    browser.send("Page.navigate", {"url": base + "index.html"})
    if browser.until("!!window.longshot && !!longshot.keys", 30):
        settle(0.3)
        checks["at phone width nothing scrolls sideways"] = browser.js("document.documentElement.scrollWidth <= 390")
        checks["at home a finger on the chart scrolls the page"] = browser.js("longshot.field.canvas.style.touchAction") == "pan-y"
        target = browser.js("longshot.field.pick(longshot.field.M.l + longshot.field.pw / 2, longshot.field.M.t + longshot.field.ph * 0.7, 300)")
        browser.js(f"(() => {{ const r = longshot.field.canvas.getBoundingClientRect(), y = r.top + longshot.field.sy({target}); if (y < 60 || y > innerHeight - 60) scrollBy(0, y - innerHeight / 2); }})()")
        settle()
        x, y = (round(v) for v in browser.js(ROCK % target))
        view = browser.js(VIEW)
        browser.tap(x, y)
        opened = browser.until(f"longshot.state.a === {q(keys[target][0])} && {OPEN}", 10)
        settle(0.7)                                    # the click that follows a tap has landed by now
        checks["a tap on a phone selects, the summary stays, and the view is where it was"] = (
            opened and browser.js(OPEN) and browser.js(VIEW) == view)
        shot("phone-selected")
        browser.js("window.scrollTo(0, 0)")
        browser.js("longshot.select('', false)")
        settle()
        top = browser.js("longshot.field.canvas.getBoundingClientRect().top")
        browser.js(f"scrollBy(0, {top} - 100)")
        settle()
        r = browser.js("(() => { const r = longshot.field.canvas.getBoundingClientRect(), f = longshot.field; return [r.left + f.M.l + f.pw / 2, r.top + f.M.t + f.ph / 2]; })()")
        a, b = (r[0] - 40, r[1]), (r[0] + 40, r[1])
        browser.touch("touchStart", a, b)
        for step in (20, 40, 60):
            browser.touch("touchMove", (a[0] - step, a[1]), (b[0] + step, b[1]))
        browser.touch("touchEnd")
        settle()
        pinched = browser.js(VIEW)
        browser.touch("touchStart", (r[0], r[1]))
        for step in (15, 30, 45):
            browser.touch("touchMove", (r[0] + step, r[1] + step / 2))
        browser.touch("touchEnd")
        settle()
        panned = browser.js(VIEW)
        report["phone"] = {"view": view, "pinched": pinched, "panned": panned}
        checks["two fingers spread zoom in, and then one finger pans"] = (
            pinched[2] > 1.5 and panned[2] == pinched[2] and panned[:2] != pinched[:2] and not browser.js("longshot.state.a"))
        shot("phone-zoomed")
        browser.send("Page.navigate", {"url": base + "index.html?view=table"})
        browser.until("!!window.longshot && !!longshot.keys", 20)
        settle(0.3)
        checks["the table at phone width keeps to the screen"] = browser.js("document.documentElement.scrollWidth <= 390") and browser.js(TABLE)["rows"] > 0
        shot("phone-table")
    else:
        checks["the field starts at phone width"] = False
    browser.send("Emulation.setTouchEmulationEnabled", {"enabled": False})
    browser.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": args.dpr, "mobile": False})

    # other pages, as asked for: "path[?query][@WIDTHxHEIGHT]", each shot from the top of the page down
    for m, spec in enumerate(args.shot or [], 1):
        url, _, at = spec.partition("@")
        w, h = (int(v) for v in at.split("x")) if at else (width, height)
        browser.send("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": args.dpr, "mobile": w < 600})
        browser.send("Page.navigate", {"url": base + url})
        browser.until("document.readyState === 'complete'", 20)
        field_page = browser.js("!!document.querySelector('#field')")
        if field_page:
            browser.until("!!window.longshot && !!longshot.keys && (!location.search.includes('a=') || " + SELECTED + ")", 20)
            settle(0.4)
        slug = "".join(c if c.isalnum() else "-" for c in url).strip("-")[:60]
        report["screens"].append(browser.shot(out / f"{args.label}-{m:02d}-{slug}{'-' + at if at else ''}.png",
                                              whole=0 if field_page else args.shot_height))
    browser.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": args.dpr, "mobile": False})

    # ---- the rules a browser can read off the page: two text inks everywhere, the surface's words on the front page
    browser.send("Page.navigate", {"url": base + "index.html"})
    browser.until("!!window.longshot && !!longshot.keys", 20)
    settle(0.3)
    home_text = browser.js(WORDS)
    checks["the front page shows its data date"] = manifest["data_date"] in home_text
    others = [p for p in ([f"a/{keys[entries[0]][0]}.html"] if entries else []) + [f"a/{loose[0][0]}.html"] * bool(loose)
              + ["list/observe.html", "record.html", "method.html"] if (site / p).exists()]
    for page in others:
        browser.send("Page.navigate", {"url": base + page})
        browser.until("document.readyState === 'complete'", 20)
        settle(0.2)
        inks[page] = browser.js(INKS)
        checks[f"{page} shows its data date"] = manifest["data_date"] in browser.js(WORDS)
    report["inks"] = {state: got for state, got in inks.items()}
    checks["visible text uses two inks only: white for content, #a8a8a8 for apparatus"] = all(not got["bad"] for got in inks.values())
    retired = {state: sorted({m.group(0) for r in RETIRED for m in re.finditer(r, text, re.I)}) for state, text in said.items()}
    report["retired_words"] = {state: words for state, words in retired.items() if words}
    checks["the front page speaks the surface's words only (measured, estimated, viability, diameter, Δv)"] = not report["retired_words"]
    browser.send("Page.navigate", {"url": base + "index.html"})
    browser.until("!!window.longshot && !!longshot.keys", 20)

    # every page opened so far. Tool noise: the bench reads pixels back; a site with entry pages for only some rocks (the synthetic one) 404s on the rest
    partial = len(list((site / "a").glob("*.html"))) < len(keys)
    report["console"] = [p for p in browser.problems()
                         if "ReadPixels" not in p and not (partial and "404" in p and "/a/" in p)]
    checks["no console errors"] = not report["console"]

    # the keys file does not load: the chart stays, the tip gives what the field file has, and the search box says why it is off
    browser.send("Network.setBlockedURLs", {"urls": ["*/data/keys.*"]})
    browser.send("Page.navigate", {"url": base + "index.html"})
    started = browser.until("!!window.longshot", 30)
    nameless = report["keys_blocked"] = browser.js("""(() => { const q = document.querySelector('#controls').elements.q;
        return { has_field: document.documentElement.classList.contains('has-field'), canvas: !document.querySelector('#field').hidden,
                 disabled: q.disabled, placeholder: q.placeholder }; })()""") if started else {}
    nameless["tip"] = browser.js(TIP % 0) if started else ""
    checks["without the keys file the chart stays and the search box says the names are missing"] = (
        started and nameless["has_field"] and nameless["canvas"] and nameless["disabled"]
        and "not loaded" in nameless["placeholder"] and "km/s" in nameless["tip"])
    browser.send("Network.setBlockedURLs", {"urls": []})

    # a browser without WebGL2 says so, and the table still lists every asteroid
    browser.send("Page.addScriptToEvaluateOnNewDocument", {"source": "HTMLCanvasElement.prototype.getContext = () => null;"})
    browser.send("Page.navigate", {"url": base + "index.html"})
    browser.until("document.readyState === 'complete' && !!window.longshot && !!longshot.keys", 15)
    note = report["no_webgl2_line"] = browser.js("document.querySelector('#plot .plot-note')?.textContent || ''")
    t = browser.js(TABLE) if note else {}
    checks["without WebGL2 the page says so and opens on the table"] = "WebGL2" in note and t.get("visible") and t.get("rows", 0) > 0
    shot("no-webgl2")

    browser.close()
    server.shutdown()
    return report, all(checks.values())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("site", help="directory holding index.html")
    ap.add_argument("--gl", choices=("auto", "gpu", "software"), default="auto", help="auto tries the GPU, then software")
    ap.add_argument("--seconds", type=float, default=4)
    ap.add_argument("--size", default="1440x900")
    ap.add_argument("--dpr", type=float, default=1)
    ap.add_argument("--label", default=None, help="name for the screenshots (default: the directory's name)")
    ap.add_argument("--out", default=str(ROOT / "build" / "screens"))
    ap.add_argument("--chrome", default=chrome(), help="headless Chromium (default: LONGSHOT_CHROME, else the newest in Playwright's cache)")
    ap.add_argument("--json", action="store_true", help="print the whole report as JSON")
    ap.add_argument("--shot", action="append", metavar="PATH[@WxH]",
                    help="also screenshot this page of the site, e.g. a/abc123.html or 'index.html?m=surface@390x844'; repeatable")
    ap.add_argument("--shot-height", type=int, default=5000, help="most px of a page's height in a --shot (default 5000)")
    args = ap.parse_args(argv)
    args.label = args.label or Path(args.site).resolve().name
    if not args.chrome or not Path(args.chrome).exists():
        print(f"no headless Chromium at {args.chrome}: pass --chrome or set LONGSHOT_CHROME")
        return 1
    report, ok = run(args)
    if args.json:
        print(json.dumps(report, indent=1))
        return 0 if ok else 1
    if "error" in report:
        print(report["error"])
        return 1
    g, f, fs = report["webgl2"], report["frames"], report["first_screen"]
    print(f"site            {report['site']}")
    print(f"renderer        {g['renderer']}  [{report['gl_mode']}]")
    print(f"context         {g['version']}, buffer {g['buffer'][0]}x{g['buffer'][1]}, device pixel ratio {g['dpr']}")
    print(f"rocks drawn     {g['shown']:,} of {g['n']:,}; draw calls in a frame, by instances: {report['draw_calls']}; {g['turning']:,} turn; {f['lit_share_of_pixels']:.1%} of pixels lit")
    print(f"frame, all on   draw to GPU done: median {f['draw_ms_median']} ms, p95 {f['draw_ms_p95']} ms over {f['count']} frames in {f['seconds']} s")
    print(f"                frame to frame: median {f['interval_ms_median']} ms, p95 {f['interval_ms_p95']} ms; back to back {f['burst_ms_per_frame']} ms a frame")
    print(f"frames unasked  {f['idle_frames_per_second_at_home']} a second at home; {f.get('frames_per_second_zoomed_on_fastest', '-')} a second zoomed on the fastest rock")
    print(f"first screen    {fs['bytes']:,} bytes in {len(fs['requests'])} requests ({fs['gzip']:,} gzipped)")
    for r in fs["requests"]:
        print(f"                {r['status']} {r['bytes']:>9,} {r['gzip']:>9,}  {r['path']}")
    print(f"tip             {report.get('tip')}")
    for kind, text in report.get("tips", {}).items():
        print(f"  {kind:<13} {text}")
    print(f"marks           {report.get('marks')}")
    print(f"legend          {report.get('legend_home')}")
    print(f"                {report.get('legend_with_mission')}")
    for state, got in report.get("inks", {}).items():
        for where, count, examples in got["bad"]:
            print(f"third ink       {state}: {where} x{count} {examples}")
    for state, words in report.get("retired_words", {}).items():
        print(f"retired words   {state}: {', '.join(words)}")
    print(f"table sort      {report.get('table_sort_ms')} ms for every row")
    print(f"no WebGL2       {report.get('no_webgl2_line')}")
    print(f"console         {'; '.join(report['console']) or 'clean'}")
    for name, passed in report["checks"].items():
        print(f"{'ok  ' if passed else 'FAIL'}            {name}")
    for name in report.get("skipped", []):
        print(f"skip            {name}")
    for s in report["screens"]:
        print(f"screen          {s}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
