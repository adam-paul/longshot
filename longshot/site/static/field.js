// The field: every rock in one instanced draw call. Hand-written WebGL2, no library.
// The shaders are the two template strings below. Work per frame is a few uniforms and
// the draw; anything that walks the rocks runs once, or on an input event.
//
// The canvas fills the figure; rocks draw inside the plot box (the figure less its margins,
// where the app writes the axes as HTML). Marks are glyphs of a fixed size, not to scale:
// their place on the size axis gives the size. One set of marks, as in the legend:
//   measured size       white rock outline with a faint glow
//   limit only          white dashed rock outline
//   not measured        grey dot; from ZOUT zoom, a dim rock outline
//   not checked         dashed grey ring, six dashes
//   with a mission:     pass a heavy outline with the glow; untested a dot (an outline from
//                       ZOUT) brighter as the chance rises; fail a faint dot
// A rock the filters leave out (above the delta-v ceiling, not matching the search) is drawn
// at a sixth of its brightness and without glow, and cannot be picked.

const K = 12, SHAPES = 8, TAU = 2 * Math.PI;
export const ZMAX = 32, ZOUT = 4;                      // zoom range; unmeasured dots become outlines from ZOUT
const PICK = 10;                                       // CSS px
const SLOW = /swiftshader|llvmpipe|software/i;         // renderers where a frame is too dear to spend on turning
const GRID = 128;                                      // picking cells per axis
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

// Outline radii as a share of half the size: one row per shape, K points each.
const RADII = [
  1.00, 0.78, 0.92, 0.70, 0.88, 0.97, 0.74, 0.90, 0.64, 0.86, 0.98, 0.80,
  0.92, 1.00, 0.70, 0.84, 0.96, 0.62, 0.88, 0.94, 0.76, 1.00, 0.68, 0.86,
  0.80, 0.96, 0.90, 0.58, 0.94, 0.86, 1.00, 0.72, 0.90, 0.66, 0.95, 0.88,
  1.00, 0.88, 0.64, 0.92, 0.98, 0.80, 0.60, 0.90, 0.96, 0.74, 0.86, 0.70,
  0.74, 0.94, 1.00, 0.82, 0.66, 0.96, 0.90, 0.70, 0.98, 0.84, 0.60, 0.92,
  0.90, 0.66, 0.98, 0.86, 0.94, 0.72, 1.00, 0.88, 0.62, 0.94, 0.80, 0.96,
  0.96, 0.84, 0.72, 1.00, 0.62, 0.90, 0.82, 0.97, 0.70, 0.92, 1.00, 0.66,
  0.68, 0.98, 0.86, 0.94, 0.76, 1.00, 0.66, 0.84, 0.96, 0.58, 0.90, 0.94,
];
const SQUASH = [1, 0.82, 0.9, 0.74, 0.95, 0.7, 0.86, 0.78];   // each shape's width across its length

// The marks, CSS px: outline radius, line width; brightness 0 to 1 (white on black, never hue).
export const MARK = {
  rock: 4.6, line: 1.25,            // measured and limit
  pass: 5.4, passLine: 2.2,
  out: 3.8, outLine: 1, outB: 0x6b / 255,   // not measured, zoomed in
  dot: 1.25, dotB: 0x8a / 255,              // not measured, overview
  ring: 3.2, ringB: 0xa8 / 255,             // not checked
  udot: 1.5, fail: 1.1, failOut: 1.4, failB: 0x44 / 255,
  sel: 8, selLine: 2, hover: 7,
  glow: 2.25,                       // half width of the glow band
  dim: 0.16,                        // a rock the filters leave out
};
// Untested, by chance of passing: five greys, brighter as the chance rises.
export const UNTESTED = [[0.6, 1], [0.3, 0xd0 / 255], [0.1, 0x9a / 255], [0.01, 0x76 / 255], [0, 0x5a / 255]];

// What the shader reads for each point of each shape: where it is, and the step
// to either side of it that gives the line an even width through the corner.
function outline(s) {
  return Array.from({ length: K }, (_, k) => {
    const a = TAU * k / K, r = RADII[s * K + k];
    return [r * Math.cos(a), r * SQUASH[s] * Math.sin(a)];
  });
}
function outlines() {
  const table = new Float32Array(SHAPES * K * 4);
  for (let s = 0; s < SHAPES; s++) {
    const pts = outline(s), at = j => pts[(j + K) % K];
    const unit = (a, b) => { const x = b[0] - a[0], y = b[1] - a[1], l = Math.hypot(x, y); return [x / l, y / l]; };
    for (let j = 0; j < K; j++) {
      const p = at(j), t1 = unit(at(j - 1), p), t2 = unit(p, at(j + 1));
      const nx = -t1[1] - t2[1], ny = t1[0] + t2[0], l = Math.hypot(nx, ny);
      const mitre = 1 / Math.max((nx * -t1[1] + ny * t1[0]) / l, 0.5);
      table.set([p[0], p[1], nx / l * mitre, ny / l * mitre], (s * K + j) * 4);
    }
  }
  return table;
}

// One rock is a closed ribbon: 2 * (K + 1) vertices of a triangle strip, numbered by gl_VertexID.
// A dot and a fill are the same strip with its inner edge at the centre.
const f = v => v.toFixed(4);                               // a number as a GLSL float
const VS = `#version 300 es
precision highp float;
const int K = ${K};
const float TAU = 6.2831853;
uniform vec4 u_t[${K * SHAPES}];  // outline table: point xy, step across the line zw
uniform vec4 u_map;   // view's left km/s, bottom log10 m, device px per km/s, device px per decade
uniform vec4 u_box;   // plot box left and bottom, canvas width and height, device px from the bottom left
uniform vec4 u_k;     // device px per CSS px, seconds, mission on, zoomed past ZOUT
uniform int u_o;      // 0 every rock, 1 the hover ring, 2 the selected rock's fill, 3 its outline
uniform int u_sel;    // the selected rock, drawn by its own calls; -1 if none
in float a_dv, a_ly, a_period;
in uint a_state, a_status, a_p, a_seed, a_mask;
out float v_t, v_d;
flat out vec4 v_s;    // brightness (-1: opaque black fill), share of each dash drawn, half line width, half glow width; px

void main() {
  gl_Position = vec4(2., 2., 2., 1.);
  if (u_o == 0 && gl_InstanceID == u_sel) return;

  // form: 0 dot, 1 rock outline, 2 ring
  int form = 1;
  float R = ${f(MARK.rock)}, lw = ${f(MARK.line)}, b = 1., duty = 1., dashes = 1.;
  bool glow = false, zoomed = u_k.w > 0.;
  uint size = a_state & 3u;                              // line style from the size row alone
  if (u_k.z == 0.) {
    if (size == 3u) glow = true;
    else if (size == 2u) { duty = .55; dashes = max(3., floor(TAU * R / 4.5)); }
    else if (size == 1u) {
      if (zoomed) { R = ${f(MARK.out)}; lw = ${f(MARK.outLine)}; b = ${f(MARK.outB)}; }
      else { form = 0; R = ${f(MARK.dot)}; b = ${f(MARK.dotB)}; }
    } else { form = 2; R = ${f(MARK.ring)}; lw = 1.; b = ${f(MARK.ringB)}; duty = .5; dashes = 6.; }
  } else if (a_status == 2u) { R = ${f(MARK.pass)}; lw = ${f(MARK.passLine)}; glow = true; }
  else if (a_status == 1u) {
    float p = float(a_p) / 255.;
    b = ${UNTESTED.slice(0, -1).map(([at, g]) => `p >= ${f(at)} ? ${f(g)} : `).join('')}${f(UNTESTED.at(-1)[1])};
    if (zoomed) { R = ${f(MARK.out)}; lw = ${f(MARK.outLine)}; }
    else { form = 0; R = ${f(MARK.udot)}; }
  } else { form = 0; R = zoomed ? ${f(MARK.failOut)} : ${f(MARK.fail)}; b = ${f(MARK.failB)}; }
  if (u_o == 0 && a_mask == 0u) { b *= ${f(MARK.dim)}; glow = false; }
  if (u_o == 1) { form = 2; R = ${f(MARK.hover)}; lw = 1.; b = 1.; duty = 1.; glow = false; }
  if (u_o >= 2) { form = 1; R = ${f(MARK.sel)}; lw = ${f(MARK.selLine)}; b = 1.; duty = 1.; dashes = 1.; glow = size == 3u; }
  if (u_o == 2) { form = 0; b = -1.; }

  int i = gl_VertexID >> 1;
  float side = float(gl_VertexID & 1) * 2. - 1., px = u_k.x;
  vec4 e;
  bool rock = form == 1 || u_o == 2;
  if (rock) {
    e = u_t[int(a_seed % ${SHAPES}u) * K + i % K];
    if ((a_seed & 8u) != 0u) e.xz = -e.xz;               // half the rocks are mirrored
  } else {
    float a = TAU * float(i) / float(K);
    vec2 c = vec2(cos(a), sin(a));
    e = vec4(c, c / cos(3.14159265 / float(K)));
  }
  float hw = .5 * lw * px, hg = glow ? max(hw, ${f(MARK.glow)} * px) : hw, out_ = hg + .5;
  vec2 q;
  if (form == 0) {                                       // inner edge at the centre: a filled shape
    float r = R * px;
    if (u_o == 2) { q = side > 0. ? r * e.xy : vec2(0.); v_d = 0.; hw = r; }
    else { q = side > 0. ? (r + .5) * e.zw : vec2(0.); v_d = side > 0. ? r + .5 : 0.; hw = r; }
    hg = hw;
  } else {
    q = R * px * e.xy + side * out_ * e.zw;
    v_d = side * out_;
  }
  if (rock) {
    float turn = float((a_seed >> 8) & 255u) / 256. + (a_period > 0. ? fract(u_k.y / a_period) : 0.);
    float cs = cos(TAU * turn), sn = sin(TAU * turn);
    q = vec2(cs * q.x - sn * q.y, sn * q.x + cs * q.y);
  }
  vec2 at = u_box.xy + vec2((a_dv - u_map.x) * u_map.z, (a_ly - u_map.y) * u_map.w);
  gl_Position = vec4((at + q) / u_box.zw * 2. - 1., 0., 1.);
  v_t = float(i) / float(K) * dashes;
  v_s = vec4(b, duty, hw, glow ? hg : 0.);
}`;

// The glow is a wider band of the same ribbon whose brightness falls from HALO_IN beside the line
// to HALO_OUT at its edge: no blur, no second pass. Blending takes the brighter of what is there,
// so overlapping glows and dim lines never add up.
const HALO_IN = 0.26, HALO_OUT = 0.1;
const FS = `#version 300 es
precision highp float;
in float v_t, v_d;
flat in vec4 v_s;
out vec4 o;
void main() {
  if (v_s.x < 0.) { o = vec4(0., 0., 0., 1.); return; }
  if (fract(v_t) > v_s.y) discard;
  float d = abs(v_d), v = clamp(v_s.z + .5 - d, 0., 1.);
  if (v_s.w > 0.) v = max(v, mix(${f(HALO_IN)}, ${f(HALO_OUT)}, clamp((d - v_s.z) / max(v_s.w - v_s.z, 1.), 0., 1.)) * clamp(v_s.w + .5 - d, 0., 1.));
  o = vec4(v_s.x * v);                                   // premultiplied white
}`;

const attrs = m => ({
  a_dv: 'dv', a_ly: 'ly', a_period: 'period_s', a_state: 'state', a_seed: 'seed',
  a_status: 'status_' + m, a_p: 'p_' + m, a_mask: 'mask',
});

export const glContext = canvas =>
  canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false });

export class Field {
  // cols: typed arrays by column name, n values each. hooks: view(field) once per changed frame, hover(i), pick(i).
  constructor(canvas, gl, cols, n, hooks = {}) {
    Object.assign(this, { canvas, gl, n, hooks, mission: '', sel: -1, hot: -1, frames: 0, late: 0, speed: 0 });
    // Two columns of our own beside the file's: log10 of the size, the plotted height; and 1 in the filters, 0 dimmed.
    this.cols = { ...cols, ly: new Float32Array(n), mask: new Uint8Array(n).fill(1) };
    this.ly = this.cols.ly; this.mask = this.cols.mask;
    this.still = matchMedia('(prefers-reduced-motion: reduce)');
    this.index();
    this.listen();
    this.build();
    // The canvas in device px, where the browser reports it: that also changes when only the pixel ratio does.
    const seen = new ResizeObserver(es => this.resize(es[0].devicePixelContentBoxSize?.[0]));
    try { seen.observe(canvas, { box: 'device-pixel-content-box' }); } catch { seen.observe(canvas); }
    this.resize();
  }

  // Once: plotted heights, the data window, the rocks that turn, and a grid over the plotted positions for picking.
  index() {
    const { dv, size_q50: size, period_s: period } = this.cols, n = this.n;
    const ly = this.ly, b = this.bounds = { x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity };
    this.rot = [];
    for (let i = 0; i < n; i++) {
      ly[i] = Math.log10(size[i]);
      b.x0 = Math.min(b.x0, dv[i]); b.x1 = Math.max(b.x1, dv[i]);
      b.y0 = Math.min(b.y0, ly[i]); b.y1 = Math.max(b.y1, ly[i]);
      if (period[i] > 0) this.rot.push(i);
    }
    if (!(b.x1 >= b.x0)) Object.assign(b, { x0: 3, x1: 12, y0: 0, y1: 3 });
    // The whole window: delta-v from the half km/s below the data to the quarter above it; size from
    // the 1 or 3 times a power of ten below the data to the one above it.
    const below = v => { const d = Math.floor(v); return v - d >= Math.log10(3) ? d + Math.log10(3) : d; };
    const above = v => { const d = Math.ceil(v); return d - v >= 1 - Math.log10(3) ? d - 1 + Math.log10(3) : d; };
    this.B = {
      x0: Math.floor((b.x0 - 0.05) * 2) / 2, x1: Math.ceil((b.x1 + 0.05) * 4) / 4,
      y0: below(b.y0 - 0.02), y1: above(b.y1 + 0.02),
    };
    this.V = { ...this.B };
    const start = this.cell = new Uint32Array(GRID * GRID + 1);
    for (let i = 0; i < n; i++) start[this.cellOf(dv[i], ly[i]) + 1]++;
    for (let c = 0; c < GRID * GRID; c++) start[c + 1] += start[c];
    const fill = start.slice();
    this.items = new Uint32Array(n);
    for (let i = 0; i < n; i++) this.items[fill[this.cellOf(dv[i], ly[i])]++] = i;
  }
  gx(x) { const b = this.B; return clamp(Math.floor((x - b.x0) / (b.x1 - b.x0) * GRID), 0, GRID - 1); }
  gy(y) { const b = this.B; return clamp(Math.floor((y - b.y0) / (b.y1 - b.y0) * GRID), 0, GRID - 1); }
  cellOf(x, y) { return this.gy(y) * GRID + this.gx(x); }

  // ---- geometry, CSS px from the canvas's top left ----
  get z() { return (this.B.x1 - this.B.x0) / (this.V.x1 - this.V.x0); }
  get zoomed() { return this.z >= ZOUT - 1e-6; }
  get pw() { return this.w - this.M.l - this.M.r; }
  get ph() { return this.h - this.M.t - this.M.b; }
  px(dv) { const V = this.V; return this.M.l + (dv - V.x0) / (V.x1 - V.x0) * this.pw; }
  py(ly) { const V = this.V; return this.M.t + (1 - (ly - V.y0) / (V.y1 - V.y0)) * this.ph; }
  dvAt(x) { const V = this.V; return V.x0 + (x - this.M.l) / this.pw * (V.x1 - V.x0); }
  lyAt(y) { const V = this.V; return V.y0 + (1 - (y - this.M.t) / this.ph) * (V.y1 - V.y0); }
  sx(i) { return this.px(this.cols.dv[i]); }
  sy(i) { return this.py(this.ly[i]); }
  inBox(x, y, pad = 0) { const M = this.M; return x >= M.l - pad && x <= this.w - M.r + pad && y >= M.t - pad && y <= this.h - M.b + pad; }

  // Rock i's mark as the vertex shader draws it: [form (0 dot, 1 outline, 2 ring), radius px].
  mark(i) {
    const c = this.cols, zoomed = this.zoomed;
    if (!this.mission) {
      const s = c.state[i] & 3;
      return s >= 2 ? [1, MARK.rock] : s === 1 ? (zoomed ? [1, MARK.out] : [0, MARK.dot]) : [2, MARK.ring];
    }
    const s = c['status_' + this.mission][i];
    return s === 2 ? [1, MARK.pass] : s === 1 ? (zoomed ? [1, MARK.out] : [0, MARK.udot]) : [0, zoomed ? MARK.failOut : MARK.fail];
  }

  // Nearest rock in the filters to a point, within tol px of it; -1 if none. Reads only nearby cells.
  pick(x, y, tol = PICK) {
    if (!this.inBox(x, y, 4)) return -1;
    const kx = this.pw / (this.V.x1 - this.V.x0), ky = this.ph / (this.V.y1 - this.V.y0);
    const dx = this.dvAt(x), dy = this.lyAt(y), rx = tol / kx, ry = tol / ky;
    let best = -1, least = tol * tol;
    for (let gy = this.gy(dy - ry), gy1 = this.gy(dy + ry); gy <= gy1; gy++) {
      for (let gx = this.gx(dx - rx), gx1 = this.gx(dx + rx); gx <= gx1; gx++) {
        for (let k = this.cell[gy * GRID + gx], end = this.cell[gy * GRID + gx + 1]; k < end; k++) {
          const i = this.items[k];
          if (!this.mask[i]) continue;
          const ex = this.sx(i) - x, ey = this.sy(i) - y, d = ex * ex + ey * ey;
          if (d <= least) { least = d; best = i; }
        }
      }
    }
    return best;
  }

  // Nearest rock in the filters from rock i in a screen direction. One pass over the rocks per key press.
  step(i, dx, dy) {
    const x = this.sx(i), y = this.sy(i);
    let best = -1, least = Infinity;
    for (let j = 0; j < this.n; j++) {
      if (j === i || !this.mask[j]) continue;
      const ex = this.sx(j) - x, ey = this.sy(j) - y, along = ex * dx + ey * dy, across = Math.abs(ex * dy - ey * dx);
      if (along > 0 && across <= along && along + across < least) { least = along + across; best = j; }
    }
    return best;
  }

  // ---- the view ----
  clampView() {
    const V = this.V, B = this.B, w = V.x1 - V.x0, h = V.y1 - V.y0;
    if (V.x0 < B.x0) { V.x0 = B.x0; V.x1 = B.x0 + w; } if (V.x1 > B.x1) { V.x1 = B.x1; V.x0 = B.x1 - w; }
    if (V.y0 < B.y0) { V.y0 = B.y0; V.y1 = B.y0 + h; } if (V.y1 > B.y1) { V.y1 = B.y1; V.y0 = B.y1 - h; }
  }
  home() { this.V = { ...this.B }; this.changed(); }
  // Zoom by f about a point of the canvas (the plot's middle by default), held between 1 and ZMAX.
  zoom(f, x = this.M.l + this.pw / 2, y = this.M.t + this.ph / 2) {
    const B = this.B, k = clamp(this.z * f, 1, ZMAX), cx = this.dvAt(x), cy = this.lyAt(y), V = this.V;
    const w = (B.x1 - B.x0) / k, h = (B.y1 - B.y0) / k, fx = (cx - V.x0) / (V.x1 - V.x0), fy = (cy - V.y0) / (V.y1 - V.y0);
    this.V = { x0: cx - fx * w, x1: cx - fx * w + w, y0: cy - fy * h, y1: cy - fy * h + h };
    this.changed();
  }
  pan(dx, dy) {
    const V = this.V, w = V.x1 - V.x0, h = V.y1 - V.y0;
    V.x0 -= dx / this.pw * w; V.x1 = V.x0 + w;
    V.y0 += dy / this.ph * h; V.y1 = V.y0 + h;
    this.changed();
  }
  // Zoomed in, bring rock i to the middle of the plot if it is out of view.
  reveal(i) {
    if (i < 0 || this.z <= 1.001) return;
    const x = this.sx(i), y = this.sy(i), M = this.M;
    if (x > M.l + 12 && x < this.w - M.r - 12 && y > M.t + 12 && y < this.h - M.b - 12) return;
    const V = this.V, w = V.x1 - V.x0, h = V.y1 - V.y0;
    this.V = { x0: this.cols.dv[i] - w / 2, x1: this.cols.dv[i] + w / 2, y0: this.ly[i] - h / 2, y1: this.ly[i] + h / 2 };
    this.changed();
  }

  hover(i) {
    if (i === this.hot) return;
    this.hot = i;
    if (i >= 0 && this.prog) this.point(this.vhot, i);
    this.hooks.hover?.(i);
    this.invalidate();
  }
  select(i) {
    if (i === this.sel) return;
    this.sel = i;
    if (i >= 0 && this.prog) this.point(this.vsel, i);
    this.changed();
  }
  setMission(m) {
    if (m === this.mission) return;
    this.mission = m;
    if (this.prog) this.repoint();
    this.changed();
  }
  // Call after writing this.mask (1 in the filters, 0 dimmed).
  masked() {
    if (this.prog) {
      this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buf.mask);
      this.gl.bufferSubData(this.gl.ARRAY_BUFFER, 0, this.mask);
    }
    this.changed();
  }

  // After the view, the selection, the mission or the mask changes: keep the view on the data and ask for a frame.
  changed() {
    if (!this.w) return;
    this.clampView();
    this.canvas.style.touchAction = this.z > 1.001 ? 'none' : 'pan-y';   // at home a phone page scrolls past the chart
    this.stale = true;
    this.invalidate();
  }
  // No turning: the visitor asked for none, or a frame costs too much here to draw unasked.
  get calm() { return this.still.matches || this.slow; }
  // Once per changed frame: how fast the fastest turning outline in view moves, and the hook that draws the axes.
  settle() {
    const period = this.cols.period_s, s = this.sel;
    let v = 0;                                              // CSS px per second along the outline
    if (!this.calm) {
      for (const i of this.rot) {
        if (!this.mask[i] || i === s) continue;
        const [form, r] = this.mark(i);
        if (form === 1 && this.inBox(this.sx(i), this.sy(i), r)) v = Math.max(v, TAU * r / period[i]);
      }
      if (s >= 0 && period[s] > 0 && this.inBox(this.sx(s), this.sy(s), MARK.sel)) v = Math.max(v, TAU * MARK.sel / period[s]);
    }
    this.speed = v;
    this.stale = false;
    this.hooks.view?.(this);
  }

  // px: the canvas in device px, where the observer gives it. That count is exact where the pixel ratio
  // is not a whole number; it is used when it agrees with the ratio, which an emulated ratio does not.
  resize(px) {
    const c = this.canvas, w = c.clientWidth, h = c.clientHeight, dpr = devicePixelRatio || 1;
    if (!w || !h) return;
    const exact = px && Math.abs(px.inlineSize - w * dpr) < 2 && Math.abs(px.blockSize - h * dpr) < 2;
    this.w = w; this.h = h; this.dpr = dpr;
    const phone = w < 600;
    this.M = phone ? { l: 58, r: 10, t: 10, b: 46, phone } : { l: 66, r: 14, t: 12, b: 52, phone };
    c.width = exact ? px.inlineSize : Math.round(w * dpr); c.height = exact ? px.blockSize : Math.round(h * dpr);
    this.changed();
    if (this.prog) this.draw();                             // now, or the resized canvas shows one empty frame
  }

  invalidate() {
    clearTimeout(this.timer);
    if (!this.raf && this.prog && !document.hidden) this.raf = requestAnimationFrame(t => this.tick(t));
  }
  tick(t) {
    this.raf = 0;
    // Thirty frames running, each asked for by the one before and each over 40 ms late: too slow to turn unasked.
    this.late = this.chained && t - this.then > 40 ? this.late + 1 : 0;
    if (this.late >= 30) { this.slow = true; this.stale = true; }
    this.then = t; this.chained = false;
    this.draw(t);
    if (this.speed < 0.1) return;                           // nothing on screen turns fast enough to see
    const wait = 200 / this.speed;                          // ms for the fastest outline to move a fifth of a px
    if (wait < 20) { this.invalidate(); this.chained = true; }
    else this.timer = setTimeout(() => this.invalidate(), Math.min(wait, 2000));
  }

  // only: draw rock i alone, as the field would (for tools/browser_check.py).
  draw(t = performance.now(), only = -1) {
    if ((devicePixelRatio || 1) !== this.dpr) return this.resize();   // another screen's pixel ratio, and no observer said so: resize draws
    if (!this.prog || !this.w) return;
    if (this.stale) this.settle();
    const gl = this.gl, c = this.canvas, u = this.u, V = this.V, M = this.M, dpr = c.width / this.w, dpy = c.height / this.h;
    const left = M.l * dpr, bottom = M.b * dpy, pw = this.pw * dpr, ph = this.ph * dpy;
    gl.viewport(0, 0, c.width, c.height);
    gl.disable(gl.SCISSOR_TEST);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.SCISSOR_TEST);
    gl.scissor(Math.floor(left), Math.floor(bottom), Math.ceil(pw), Math.ceil(ph));
    gl.uniform4f(u.map, V.x0, V.y0, pw / (V.x1 - V.x0), ph / (V.y1 - V.y0));
    gl.uniform4f(u.box, left, bottom, c.width, c.height);
    gl.uniform4f(u.k, dpr, this.calm ? 0 : t / 1000, this.mission ? 1 : 0, this.zoomed ? 1 : 0);
    const one = (vao, o) => { gl.uniform1i(u.o, o); gl.bindVertexArray(vao); gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 2 * K + 2, 1); };
    if (only >= 0) {
      this.point(this.vone, only);
      gl.uniform1i(u.sel, -1);
      one(this.vone, 0);
      return;
    }
    const s = this.sel;
    gl.uniform1i(u.sel, s);
    gl.uniform1i(u.o, 0);
    gl.bindVertexArray(this.vao);
    gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 2 * K + 2, this.n);
    if (this.hot >= 0 && this.hot !== s) one(this.vhot, 1);
    if (s >= 0) {                                           // the selected rock, larger, over a black fill
      gl.disable(gl.BLEND);
      one(this.vsel, 2);
      gl.enable(gl.BLEND);
      one(this.vsel, 3);
    }
    this.frames++;
  }

  // Compile, upload, wire. Runs at start and again after the context comes back.
  build() {
    const gl = this.gl, prog = gl.createProgram();
    for (const [type, src] of [[gl.VERTEX_SHADER, VS], [gl.FRAGMENT_SHADER, FS]]) {
      const sh = gl.createShader(type);
      gl.shaderSource(sh, src);
      gl.compileShader(sh);
      if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS) && !gl.isContextLost()) throw new Error(gl.getShaderInfoLog(sh));
      gl.attachShader(prog, sh);
    }
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS) && !gl.isContextLost()) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);
    this.u = {};
    for (const name of ['t', 'map', 'box', 'k', 'o', 'sel']) this.u[name] = gl.getUniformLocation(prog, 'u_' + name);
    const info = gl.getExtension('WEBGL_debug_renderer_info');
    this.slow = SLOW.test(gl.getParameter(info ? info.UNMASKED_RENDERER_WEBGL : gl.RENDERER) || '');
    gl.uniform4fv(this.u.t, outlines());
    gl.clearColor(0, 0, 0, 0);                              // the grid shows through behind the rocks
    gl.enable(gl.BLEND);
    gl.blendEquation(gl.MAX);                               // overlapping dim lines and glows stay dim
    this.buf = {};
    this.vao = gl.createVertexArray(); this.vhot = gl.createVertexArray(); this.vsel = gl.createVertexArray(); this.vone = gl.createVertexArray();
    this.prog = prog;
    this.repoint();
  }
  repoint() {
    this.point(this.vao, 0);
    if (this.hot >= 0) this.point(this.vhot, this.hot);
    if (this.sel >= 0) this.point(this.vsel, this.sel);
  }
  // Aim a vertex array at the column buffers, starting at rock i.
  point(vao, i) {
    const gl = this.gl;
    gl.bindVertexArray(vao);
    for (const [name, col] of Object.entries(attrs(this.mission || 'surface'))) {
      const loc = gl.getAttribLocation(this.prog, name), a = this.cols[col];
      if (!a) throw new Error('the field file has no column ' + col);
      if (!this.buf[col]) {
        gl.bindBuffer(gl.ARRAY_BUFFER, this.buf[col] = gl.createBuffer());
        gl.bufferData(gl.ARRAY_BUFFER, a, col === 'mask' ? gl.DYNAMIC_DRAW : gl.STATIC_DRAW);
      }
      if (loc < 0) continue;
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buf[col]);
      gl.enableVertexAttribArray(loc);
      const at = i * a.BYTES_PER_ELEMENT;
      if (a instanceof Float32Array) gl.vertexAttribPointer(loc, 1, gl.FLOAT, false, 0, at);
      else gl.vertexAttribIPointer(loc, 1, a instanceof Uint8Array ? gl.UNSIGNED_BYTE : a instanceof Uint16Array ? gl.UNSIGNED_SHORT : gl.UNSIGNED_INT, 0, at);
      gl.vertexAttribDivisor(loc, 1);
    }
  }

  // Pointer: hover, click to select, drag to pan once zoomed, two fingers to pinch, wheel to zoom about the cursor.
  listen() {
    const c = this.canvas, down = new Map();
    let moved = 0, many = false, tapped = -1e9, gap, from, mid;
    const at = e => { const r = c.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    const pair = () => { const [a, b] = [...down.values()]; return [Math.hypot(a[0] - b[0], a[1] - b[1]), [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]]; };
    const pinch = () => { if (down.size === 2) { [gap, mid] = pair(); from = this.z; } };   // two fingers down: where they start
    c.addEventListener('pointerdown', e => {
      if (e.button) return;                                 // the main button, a finger or a pen tip
      c.setPointerCapture(e.pointerId);
      if (down.size) many = true; else { moved = 0; many = false; }   // a gesture runs until every pointer lifts
      down.set(e.pointerId, at(e));
      pinch();
    });
    c.addEventListener('pointermove', e => {
      const p = at(e), was = down.get(e.pointerId);
      if (!was) return e.pointerType === 'mouse' && this.hover(this.pick(p[0], p[1]));
      down.set(e.pointerId, p);
      if (down.size === 1) {
        moved += Math.hypot(p[0] - was[0], p[1] - was[1]);
        if (moved > 4) { c.classList.add('grab'); this.hover(-1); }
        if (moved > 4 && this.z > 1.001) this.pan(p[0] - was[0], p[1] - was[1]);
      } else if (down.size === 2) {                         // two fingers: the gap zooms, the midpoint pans
        const [d, m] = pair();
        // against the gap and zoom the pinch began with: fingers report one at a time
        if (gap) this.zoom(from * d / gap / this.z, m[0], m[1]);
        this.pan(m[0] - mid[0], m[1] - mid[1]);
        mid = m;
      }
    });
    const up = e => {
      if (!down.delete(e.pointerId)) return;
      pinch();
      if (!down.size) c.classList.remove('grab');
      if (e.type === 'pointerup' && moved < 5 && !many && !down.size) {
        const p = at(e), touch = e.pointerType === 'touch', i = this.pick(p[0], p[1], touch ? 16 : PICK);
        if (touch && i >= 0) tapped = e.timeStamp;
        this.hooks.pick?.(i);
      }
    };
    c.addEventListener('pointerup', up);
    c.addEventListener('pointercancel', up);
    // The click that follows a tap lands on whatever the pick put under the finger: it is not a second press.
    addEventListener('click', e => {
      if (e.timeStamp - tapped > 500) return;
      tapped = -1e9;
      e.preventDefault(); e.stopPropagation();
    }, true);
    c.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse' && !down.size) this.hover(-1); });
    c.addEventListener('wheel', e => {
      e.preventDefault();
      const p = at(e);
      this.zoom(Math.exp(-e.deltaY * (e.deltaMode ? 30 : 1) * (e.ctrlKey ? 0.01 : 0.0015)), p[0], p[1]);
    }, { passive: false });
    c.addEventListener('webglcontextlost', e => {
      e.preventDefault();
      this.prog = null;
      cancelAnimationFrame(this.raf);
      this.raf = 0;
    });
    c.addEventListener('webglcontextrestored', () => { this.build(); this.changed(); });
    document.addEventListener('visibilitychange', () => this.invalidate());
    this.still.addEventListener('change', () => this.changed());
  }
}
