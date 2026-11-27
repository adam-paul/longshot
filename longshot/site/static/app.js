// The front page around the field: loading, URL state, the control strip, the legend line, the axes,
// the table view and the readout. It reads the pipeline's files from its own site and computes no
// probability: every chance it prints is a byte of the field file, every count a tally of its columns.
// Its words are the surface vocabulary of docs/design.md section 3: measured and estimated; fits,
// ruled out and unclear; diameter; Δv.
import { Field, glContext, ZMAX, MARK } from './field.js';

const $ = s => document.querySelector(s);
const form = $('#controls'), plot = $('#plot'), canvas = $('#field'), axes = $('#axes'), tip = $('#tip');
const legendBox = $('#legend'), tableBox = $('#table'), readout = $('#readout');
const E = form.elements;
const TYPES = { f32: Float32Array, u8: Uint8Array, u16: Uint16Array, i32: Int32Array, u32: Uint32Array };
const MISSIONS = ['surface', 'capture'], MISSION_NAME = { surface: 'Surface work', capture: 'Whole-body capture' };
// A mission's verdict, by the pipeline's status code: 0 fail, 1 untested, 2 pass.
const VERDICT = ['ruled out', 'unclear', 'fits'];
const RULED = 'Ruled out', LOOSE = 'No brightness on file';
const PAGE = 50;
const title = document.title;
// S is the page's whole state; the URL holds it. dv 0: no cut-off. dir 0: the column's own direction.
const S = { view: 'chart', m: '', dv: 0, q: '', a: '', sort: '', dir: 0, page: 0 };
// n rocks in the field file; the asteroids with no brightness on file follow them as rows n..N-1 (the manifest's unplaced).
// keys: [key, designation, name, number] per rock. near: 1 where a row is under Max Δv and matches the search.
// full: 1 where it is also not ruled out by the mission chosen; the rest are faint.
let man, cols, n = 0, N = 0, field = null, keys = null, loose = [], index = null, hay = null, near, full, lost = '';
let listed = null, opener = null, loading = null, defaults = null, sel = -1, adjusting = '', named = false;
const cache = new Map();

const own = url => {
  if (new URL(url, document.baseURI).origin !== location.origin) throw new Error('not this site: ' + url);
  return fetch(url).then(r => r.ok ? r : Promise.reject(new Error(r.status + ' ' + url)));
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const norm = s => s.normalize('NFD').toLowerCase().replace(/[^a-z0-9]/g, '');
const terms = row => row.slice(1, 4).filter(v => v != null && v !== '').map(v => norm(`${v}`)).join(' ');
const count = v => v.toLocaleString('en');
// An estimate to two significant figures (docs/design.md section 6), in metres with a comma separator.
const sig2 = v => {
  if (!v) return '0';
  const d = 1 - Math.floor(Math.log10(Math.abs(v))), r = Math.round(v * 10 ** d) / 10 ** d;
  return d > 0 ? r.toFixed(d) : count(Math.round(r));
};
const entryUrl = key => new URL(`a/${encodeURIComponent(key)}.html`, document.baseURI);
const k = s => `<span class="k">${s}</span>`;                          // apparatus words: a label beside its value

// ---- the marks: one set for the legend and the table; style.css draws each (.g-measured ...) ----

// The classes are the site's (templates.glyph): limit is a bound's dashed outline, prior an estimate's dot, priorz
// that dot as the zoomed field draws it, pass the heavy outline of one that fits.
const G = Object.fromEntries(Object.entries({ measured: 'measured', bound: 'limit', estimated: 'prior', estimatedz: 'priorz', fits: 'pass' })
  .map(([mark, c]) => [mark, `<i class="g g-${c}" aria-hidden="true"></i>`]));
// The size row's two-bit state: 3 measured, 2 a bound, 1 not measured, 0 not checked. On the surface a bound is
// measured (a source gives it) and both of the others are estimated: which source was not checked is on the entry.
const sizeState = r => cols.state[r] & 3;
const measured = r => sizeState(r) >= 2;
const glyphOf = r => G[!measured(r) ? 'estimated' : sizeState(r) === 3 ? 'measured' : 'bound'];

// ---- rows: the rocks, then the asteroids with no rock ------------------------------------------

const rowOf = r => r < n ? keys?.[r] : loose[r - n];
const keyOf = r => rowOf(r)?.[0] ?? '';
const nameOf = r => { const row = rowOf(r); return row ? row[2] || row[1] : ''; };
const dvOf = r => r < n ? cols.dv[r] : typeof loose[r - n]?.[4] === 'number' ? loose[r - n][4] : NaN;
// 0 ruled out, 1 unclear, 2 fits. An asteroid with no rock is ruled out of both missions (docs/mvp.md section 5, unplaced).
const statusOf = (r, m) => r < n ? cols['status_' + m][r] : 0;
const chanceOf = (r, m) => r < n ? cols['p_' + m][r] / 255 : NaN;
// The chance as the entry prints it: the file's whole percentage, read with the status (0 and 100 are <1% and >99%).
const chanceText = (r, m) => { const p = cols['pct_' + m][r]; return p <= 0 ? '<1%' : p >= 100 ? '>99%' : p + '%'; };
const verdictText = (r, m) => { const s = statusOf(r, m); return VERDICT[s] + (s === 1 ? ', ' + chanceText(r, m) + ' chance' : ''); };
// A measured diameter to the precision the field file keeps (four figures at most), in metres.
const metres = v => count(+(+v).toPrecision(4));
const rowAt = key => index?.get(key) ?? -1;

// ---- start ----------------------------------------------------------------------------------

async function start() {
  const base = new URL($('meta[name=field-manifest]').content, document.baseURI);
  man = await (await own(base)).json();
  const buf = await (await own(new URL(man.file, base))).arrayBuffer();
  // The names come after the rocks: asked for first, they would share the line and hold up the first frame.
  const names = () => own(new URL(man.keys_file, base)).then(r => r.json());
  const wait = names().catch(names);                                    // once more before giving up
  wait.catch(() => {});                                                 // handled below, after the field is up
  n = man.n;
  loose = man.unplaced || [];
  N = n + loose.length;
  near = new Uint8Array(N).fill(1);
  full = new Uint8Array(N).fill(1);
  cols = {};
  for (const { name, type, offset } of man.columns) {                   // a view where the offset allows, else a copy
    const T = TYPES[type];
    cols[name] = offset % T.BYTES_PER_ELEMENT ? new T(buf.slice(offset, offset + n * T.BYTES_PER_ELEMENT)) : new T(buf, offset, n);
  }
  listen();
  const gl = canvas && glContext(canvas);
  if (gl) {
    field = new Field(canvas, gl, cols, n, { view: drawAxes, hover, pick: i => i >= 0 ? keys && select(keys[i][0], false) : S.a && select('', false) });
    document.documentElement.classList.add('has-field');
  } else {
    note('This browser has no WebGL2, so the chart is not drawn. The table lists every asteroid.');
    for (const c of E.view instanceof RadioNodeList ? E.view : [E.view]) if (c?.value === 'chart') c.disabled = true;
    if (zoomGroup) for (const b of zoomGroup.querySelectorAll('button')) b.disabled = true;
  }
  read(!gl);
  if (!gl && S.view !== 'table') { S.view = 'table'; write(true); }
  apply();
  try {
    keys = await wait;
    index = new Map([...keys.map((k, i) => [k[0], i]), ...loose.map((k, i) => [k[0], n + i])]);
    hay = [...keys.map(terms), ...loose.map(terms)];
  } catch {                                                             // the chart stays; nothing in it has a name
    lost = 'Names not loaded';
    Object.assign(E.q, { disabled: true, placeholder: lost });
    say(lost);
  }
  named = true;
  if (S.a && index && !index.has(S.a)) { S.a = ''; write(true); }       // a key this data does not hold
  apply();
  window.longshot = { field, state: S, manifest: man, keys, cols, rows: () => rows().slice(), select };   // for tools/browser_check.py
}

// A line in the figure where the chart would be: no WebGL2, or the files did not load.
function note(text) {
  if (canvas) canvas.hidden = true;
  if (axes) axes.hidden = true;
  const p = document.createElement('p');
  p.className = 'plot-note';
  p.textContent = text;
  plot?.append(p);
}

// ---- state: the URL holds it ------------------------------------------------------------------

// A cut-off from the URL or the slider: within the slider's range, on its steps; at its top, none.
function ceiling(v) {
  const { min, max, step } = E.dv, s = +step || 0.1;
  if (!(v < +max)) return 0;
  v = +(Math.round(Math.max(+min, v) / s) * s).toFixed(3);
  return v < +max ? v : 0;
}
function read(table = false) {
  const p = new URLSearchParams(location.search), s = p.get('sort') || '';
  S.view = p.get('view') === 'table' || (table && !p.get('view')) ? 'table' : 'chart';
  S.m = MISSIONS.includes(p.get('m')) ? p.get('m') : '';
  S.dv = ceiling(parseFloat(p.get('dv')));
  S.q = p.get('q') || '';
  S.a = p.get('a') || '';
  S.sort = TCOLS[s.replace(/^-/, '')] ? s.replace(/^-/, '') : '';
  if (!tcols().includes(S.sort)) S.sort = '';                           // a column this mission hides: not kept in the address
  S.dir = S.sort ? (s[0] === '-' ? -1 : 1) : 0;
  S.page = Math.max(0, (parseInt(p.get('page'), 10) || 1) - 1);
  listed = null;
  write(true);                                                          // the address says what is shown
}
function write(replace) {
  const p = new URLSearchParams();
  if (S.a) p.set('a', S.a);
  if (S.m) p.set('m', S.m);
  if (S.dv) p.set('dv', S.dv);
  if (S.q) p.set('q', S.q);
  if (S.view === 'table') {
    p.set('view', 'table');
    if (S.sort) p.set('sort', (S.dir < 0 ? '-' : '') + S.sort);
    if (S.page) p.set('page', S.page + 1);
  }
  const url = location.pathname + (`${p}` && '?' + p) + location.hash;
  if (url !== location.pathname + location.search + location.hash) history[replace ? 'replaceState' : 'pushState'](null, '', url);
}

// Everything on the page from S.
function apply() {
  setControl('view', S.view);
  setControl('m', S.m);
  E.dv.value = S.dv || E.dv.max;
  if (E.q.value !== S.q) E.q.value = S.q;
  showDv();
  field?.setMission(S.m);
  filter();
  view();
  sel = rowAt(S.a);
  field?.select(sel < n ? sel : -1);
  if (sel >= 0 && sel < n) field?.reveal(sel);
  if (named) show(S.a);                                                 // before the names load, a key cannot be checked
}
// A radio group named `name`. (Its value cannot be set to "" through the list.)
function setControl(name, value) {
  const el = E[name];
  if (!el) return;
  for (const c of el instanceof RadioNodeList ? el : [el]) c.checked = c.value === value;
}
// The slider's value; its label carries the unit, "Max Δv (km/s)".
const showDv = () => { const out = E['dv-value']; if (out) out.value = (S.dv || +E.dv.max).toFixed(1); };

function select(key, focus) {
  if (key && !S.a) opener = document.activeElement;                    // closing gives the focus back
  S.a = key;
  write();
  sel = rowAt(key);
  field?.select(sel >= 0 && sel < n ? sel : -1);
  if (sel >= 0 && sel < n) field?.reveal(sel);
  show(key, focus);
  if (S.view === 'table') markRow();                                    // the rows stay, so the link that opened it can take the focus back
  if (!key && focus) (opener?.isConnected && opener !== document.body && opener.getClientRects().length ? opener : S.view === 'table' ? E.q : canvas)?.focus();
}

// ---- the filter: Max Δv, the search and the mission --------------------------------------------

// What a row must hold to match: the query in one of its designation, name or number, spaces and
// case aside; or, when no row holds that, each of the query's words somewhere in the three.
function matcher(text) {
  const q = norm(text), words = text.split(/\s+/).map(norm).filter(Boolean);
  if (!q || !hay) return null;
  const whole = h => h.includes(q);
  return hay.some(whole) ? whole : h => words.every(w => h.includes(w));
}
// A mission's ruled-out asteroids leave the filter like those over Max Δv: faint in the chart, not in the table.
function filter() {
  const match = matcher(S.q);
  for (let r = 0; r < N; r++) {
    near[r] = (!S.dv || dvOf(r) <= S.dv + 1e-6) && (!match || match(hay[r])) ? 1 : 0;
    full[r] = near[r] && (!S.m || statusOf(r, S.m) >= 1) ? 1 : 0;
  }
  if (field) { field.mask.set(full.subarray(0, n)); field.masked(); }
  listed = null;
  if (field && field.hot >= 0 && !field.mask[field.hot]) field.hover(-1);
  legend();
}
// The rows the table lists: those in the filter. Sorted.
function rows() {
  if (listed) return listed;
  const out = [];
  for (let r = 0; r < N; r++) if (full[r]) out.push(r);
  const k = sortKey(), d = sortDir(), v = sortValues(k), dv = sortValues('dv');
  out.sort((a, b) => v[a] < v[b] ? -d : v[a] > v[b] ? d : dv[a] - dv[b]);
  return listed = out;
}
// A line under the search box: no match, no rock, names missing.
function say(text) {
  let msg = form.querySelector('.find-msg');
  if (!msg && text) {
    msg = Object.assign(document.createElement('p'), { className: 'find-msg' });
    msg.setAttribute('aria-live', 'polite');
    E.q.insertAdjacentElement('afterend', msg);
  }
  if (msg) msg.textContent = text || lost;
}
function matches(text) {
  const match = matcher(text), out = [];
  if (!match) return out;
  for (let r = 0; r < N; r++) if (match(hay[r])) out.push(r);
  return out;
}
// The match Enter opens: one whose designation, name or number is the query; else one that starts with it; else the first.
function best(text) {
  const q = norm(text);
  let pick = -1, least = 3;
  if (!q || !hay) return -1;
  const match = matcher(text);
  for (let r = 0; r < N; r++) {
    if (!match(hay[r])) continue;
    const t = hay[r].split(' '), s = t.includes(q) ? 0 : t.some(v => v.startsWith(q)) ? 1 : 2;
    if (s < least || (s === least && pick >= 0 && !full[pick] && full[r])) { least = s; pick = r; }
  }
  return pick;
}
function find() {
  const r = best(S.q);
  if (r < 0) { say(S.q.trim() && hay ? 'No match' : ''); return; }
  say(r < n ? '' : 'Not shown: no brightness on file');
  select(keyOf(r), true);
}
function suggest() {
  let list = E.q.list;
  if (!list) {
    list = Object.assign(document.createElement('datalist'), { id: 'q-list' });
    form.append(list);
    E.q.setAttribute('list', list.id);
  }
  list.innerHTML = S.view === 'table' ? '' : matches(S.q).slice(0, 12)
    .map(r => `<option value="${esc(nameOf(r))}">${rowOf(r)[2] ? esc(rowOf(r)[1]) : ''}</option>`).join('');
}

// ---- the legend line: what is shown, its two marks, and what is not shown, counted under the filter ----

// One line above the chart or the table (docs/design.md section 8): how many are shown of every reachable asteroid,
// then each mark's words and its count. Shown is measured plus estimated (plus, in the table, the rows with no
// brightness); the asteroids over Max Δv or not matching the search are the rest of the total.
function tally() {
  const t = { shown: 0, measured: 0, estimated: 0, fits: 0, ruled: 0, loose: 0 };
  for (let r = 0; r < N; r++) {
    if (!near[r]) continue;
    if (!full[r]) { t.ruled++; continue; }
    if (r >= n) { t.loose++; continue; }
    t.shown++;
    if (measured(r)) t.measured++; else t.estimated++;
    if (S.m && statusOf(r, S.m) === 2) t.fits++;
  }
  return t;
}
function legend() {
  if (!legendBox) return;
  const table = S.view === 'table', zoomed = !!field?.zoomed && !table, t = tally();
  if (table) t.shown += t.loose;                                        // the table lists them, with no diameter
  const mark = (key, g, word, v) => `<li data-k="${key}">${g}${word}<span class="n">${count(v)}</span></li>`;
  let h = `<li data-k="shown" class="tot"><span class="n">${count(t.shown)}</span>` +
    (t.shown === N ? '' : ` of <span class="n">${count(N)}</span>`) + ' reachable asteroids</li>' +
    mark('measured', G.measured, 'Measured', t.measured) +
    mark('estimated', zoomed ? G.estimatedz : G.estimated, table ? 'Estimated (90% range)' : 'Estimated (median)', t.estimated);
  if (S.m) h += mark('fits', table ? '' : G.fits, 'Fits', t.fits) + mark('ruled', '', RULED, t.ruled);
  if (t.loose) h += mark('loose', '', LOOSE, t.loose);
  // the app writes the whole line: whatever the page drew there before the field file loaded gives way to it
  let ul = legendBox.matches('ul') ? legendBox : legendBox.querySelector('ul');
  if (!ul) ul = Object.assign(document.createElement('ul'), { className: 'legend' });
  if (ul !== legendBox && (legendBox.childNodes.length !== 1 || legendBox.firstChild !== ul)) legendBox.replaceChildren(ul);
  ul.innerHTML = h;
  legendBox.dataset.z = zoomed ? '1' : '0';
}

// ---- chart / table ----------------------------------------------------------------------------

function view() {
  const table = S.view === 'table';
  document.documentElement.dataset.view = S.view;
  if (plot) plot.hidden = table;
  if (tableBox) tableBox.hidden = !table;
  if (zoomGroup) zoomGroup.hidden = table;
  if (table) renderTable();
  legend();
  suggest();
}

// The table's columns: heading ("Quantity (unit)", the unit never in the cells), numeric, the direction a first
// click sorts, and what each row sorts by.
const TCOLS = {
  ast: { h: 'Asteroid', dir: 1, of: r => ((r < n ? cols.named[r] : rowOf(r)?.[2]) ? '0' : '1') + nameOf(r).toLowerCase() },   // names, then designations
  dv: { h: 'Δv (km/s)', num: true, dir: 1, of: r => { const v = dvOf(r); return isNaN(v) ? Infinity : v; } },
  size: { h: 'Diameter (m)', num: true, dir: -1, of: r => r < n ? cols.size_q50[r] : -1 },
  surface: { h: MISSION_NAME.surface, dir: -1, of: r => missionKey(r, 'surface') },
  capture: { h: MISSION_NAME.capture, dir: -1, of: r => missionKey(r, 'capture') },
};
const missionKey = (r, m) => { const s = statusOf(r, m); return s === 2 ? 2 : s === 1 ? chanceOf(r, m) : s - 1; };
const sorted = {};
// Each column's sort values, computed once (the names only once they have loaded).
const sortValues = k => {
  if (sorted[k] && !(k === 'ast' && !sorted[k].named && keys)) return sorted[k];
  const v = Array.from({ length: N }, (_, r) => TCOLS[k].of(r));
  v.named = !!keys;
  return sorted[k] = v;
};
const tcols = () => S.m ? ['ast', 'dv', 'size', S.m] : ['ast', 'dv', 'size', 'surface', 'capture'];
const sortKey = () => S.sort && tcols().includes(S.sort) ? S.sort : (S.m || 'dv');
const sortDir = () => S.sort === sortKey() && S.dir ? S.dir : TCOLS[sortKey()].dir;

let tbl, pager;
function tableShell() {
  if (tbl || !tableBox) return;
  tbl = tableBox.querySelector('table');
  if (!tbl) {
    tableBox.insertAdjacentHTML('beforeend', '<div class="tscroll"><table class="ftbl"><caption class="vh">Reachable asteroids</caption><thead></thead><tbody></tbody></table></div>');
    tbl = tableBox.querySelector('table');
  }
  if (!tbl.tHead) tbl.createTHead();
  if (!tbl.tBodies.length) tbl.createTBody();
  pager = tableBox.querySelector('.pager');
  if (!pager) {
    tableBox.insertAdjacentHTML('beforeend', '<div class="pager"><output name="rows"></output><button type="button" class="btn" name="page-prev">Previous</button><button type="button" class="btn" name="page-next">Next</button></div>');
    pager = tableBox.querySelector('.pager');
  }
  // the pager's controls: named, and either in the form or in the pager
  const named = name => E[name] || pager.querySelector(`[name="${name}"]`);
  pager = { rows: named('rows'), prev: named('page-prev'), next: named('page-next') };
  tbl.tHead.addEventListener('click', e => {
    const b = e.target.closest('button[data-sort]');
    if (!b) return;
    const k = b.dataset.sort;
    S.dir = sortKey() === k ? -sortDir() : TCOLS[k].dir;
    S.sort = k; S.page = 0; listed = null;
    write(true); renderTable();
    tbl.tHead.querySelector(`button[data-sort="${k}"]`)?.focus();
  });
  const turn = by => () => {
    S.page += by;
    write(true); renderTable();
    tableBox.querySelector('.tscroll')?.scrollTo?.(0, 0);
    const [was, other] = by < 0 ? [pager.prev, pager.next] : [pager.next, pager.prev];
    if (was.disabled && !other.disabled) other.focus();                // the end of the list: focus is not dropped to the page
  };
  pager.prev.addEventListener('click', turn(-1));
  pager.next.addEventListener('click', turn(1));
}
// A mission's verdict: the word, and for an unclear one the chance it fits.
function missionCell(r, m) {
  const s = statusOf(r, m);
  // the chance's slot is there on every row, so the verdicts line up down the column
  return `<span class="mc"><span class="vd">${VERDICT[s]}</span>` +
    `<span class="ch">${s === 1 ? chanceText(r, m) + ' chance' : ''}</span></span>`;
}
// The diameter with its mark: a measured one as its value, an estimate as its 90% range (the legend says which).
// A row with no rock has no brightness to estimate from.
function sizeCell(r) {
  if (r >= n) return 'no brightness on file';
  return `<span class="sz">${glyphOf(r)}<span class="vh">${measured(r) ? 'measured' : 'estimated, 90% range'}, </span>` +
    (measured(r) ? metres(cols.size_q50[r]) : `${sig2(cols.size_q05[r])}–${sig2(cols.size_q95[r])}`) + '</span>';
}
function markRow() {
  for (const tr of tbl?.tBodies[0]?.rows || []) tr.classList.toggle('sel', !!S.a && tr.dataset.k === S.a);
}
function renderTable() {
  tableShell();
  if (!tbl) return;
  const all = rows(), total_ = all.length, pages = Math.max(1, Math.ceil(total_ / PAGE));
  if (S.page >= pages) { S.page = pages - 1; write(true); }
  const cs = tcols(), k = sortKey(), d = sortDir();
  tbl.tHead.innerHTML = '<tr>' + cs.map(c => `<th scope="col"${TCOLS[c].num ? ' class="num"' : ''}` +
    `${c === k ? ` aria-sort="${d > 0 ? 'ascending' : 'descending'}"` : ''}><button type="button" data-sort="${c}">${TCOLS[c].h}</button></th>`).join('') + '</tr>';
  let h = '';
  for (const r of all.slice(S.page * PAGE, S.page * PAGE + PAGE)) {
    const row = rowOf(r), key = keyOf(r), dv = dvOf(r);
    h += `<tr data-k="${esc(key)}"${key && key === S.a ? ' class="sel"' : ''}>`;
    for (const c of cs) {
      if (c === 'ast') h += `<td class="ast">${row ? `<a href="a/${encodeURIComponent(key)}.html">${esc(row[2] || row[1])}</a>${row[2] ? `<span class="nm">${esc(row[1])}</span>` : ''}` : ''}</td>`;
      else if (c === 'dv') h += `<td class="num dvc${isNaN(dv) ? ' none' : ''}" data-l="${TCOLS.dv.h}">${isNaN(dv) ? 'not on file' : dv.toFixed(3)}</td>`;
      else if (c === 'size') h += `<td class="num szc" data-l="${TCOLS.size.h}">${sizeCell(r)}</td>`;
      else h += `<td class="mis" data-l="${MISSION_NAME[c]}">${missionCell(r, c)}</td>`;
    }
    h += '</tr>';
  }
  if (!total_) h = `<tr class="empty"><td colspan="${cs.length}">${S.q.trim() && matches(S.q).length ? 'None under these filters' : 'No asteroid matches'}</td></tr>`;
  tbl.tBodies[0].innerHTML = h;
  pager.rows.value = total_ ? `Rows ${count(S.page * PAGE + 1)}–${count(Math.min(total_, S.page * PAGE + PAGE))} of ${count(total_)}` : 'No rows';
  pager.prev.disabled = S.page <= 0;
  pager.next.disabled = S.page >= pages - 1;
  legend();
}

// ---- the readout: the named list by default; a selected asteroid's summary, lifted from its entry ----

async function show(key, focus) {
  if (!readout || (readout.dataset.key || '') === key) { if (focus && key) readout.querySelector('h2')?.focus(); return; }
  loading?.abort();
  if (!defaults) defaults = [...readout.childNodes];
  readout.dataset.key = key;
  if (!key) { readout.replaceChildren(...defaults); document.title = title; return; }
  const r = rowAt(key), row = r >= 0 ? rowOf(r) : null, url = entryUrl(key);
  // Until the entry's summary arrives: the name, and the number and designation beside it where the name is not the designation.
  const box = document.createElement('div');
  box.className = 'selected';
  box.innerHTML = `<div class="sel-head"><div><h2 tabindex="-1">${esc(row ? row[2] || row[1] : '')}</h2></div>` +
    '<button type="button" class="btn" data-close>Close</button></div><div class="sel-body"></div>' +
    `<div class="sel-go"><a class="btn btn-solid" data-open href="${esc(url.href)}">Full details for ${esc(row ? row[2] || row[1] : '')}</a></div>`;
  box.querySelector('[data-close]').onclick = () => select('', true);
  readout.replaceChildren(box);
  readout.scrollTop = 0;
  if (focus) box.querySelector('h2').focus();
  const body = box.querySelector('.sel-body'), ctl = loading = new AbortController();
  try {
    let got = cache.get(key);
    if (!got) {
      const res = await fetch(url, { signal: ctl.signal });
      if (!res.ok) throw new Error(res.status);
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      const main = doc.getElementById('entry'), summary = main?.querySelector('#summary');
      if (!summary) throw new Error('no summary');
      for (const at of ['href', 'src']) {                                 // the page's links are relative to a/, and its anchors are its own
        for (const el of summary.querySelectorAll(`[${at}]`)) el.setAttribute(at, new URL(el.getAttribute(at), url).href);
      }
      for (const h of summary.querySelectorAll('h1')) {                   // the page's heading is the readout's second level
        const h2 = doc.createElement('h2');
        for (const { name, value } of h.attributes) h2.setAttribute(name, value);
        h2.append(...h.childNodes);
        h.replaceWith(h2);
      }
      got = { html: summary.outerHTML, title: doc.title, name: main.querySelector('h1')?.textContent.trim() || '' };
      cache.set(key, got);
    }
    if (ctl.signal.aborted) return;
    body.innerHTML = got.html;
    // The summary opens with the asteroid's name: Close joins that line, and the placeholder heading goes.
    const head = body.querySelector('.ehead') || body.querySelector('h2')?.parentElement, h2 = body.querySelector('h2');
    if (head && h2) {
      h2.tabIndex = -1;
      const placeholder = box.querySelector('.sel-head'), held = placeholder.contains(document.activeElement);
      head.append(box.querySelector('[data-close]'));
      placeholder.remove();
      if (held || (focus && document.activeElement === document.body)) h2.focus();
    } else if (!row) box.querySelector('.sel-head h2').textContent = got.name;
    document.title = got.title || title;
  } catch (err) {
    if (ctl.signal.aborted) return;
    body.innerHTML = '<p>Entry not loaded.</p>';
  }
}

// ---- the tip --------------------------------------------------------------------------------

// The rock under the pointer: its name, Δv and diameter, and with a mission its verdict. A measured diameter is its
// value; an estimate is its 90% range, and says so.
function hover(i) {
  if (!tip) return;
  tip.hidden = i < 0 || i === sel;                                       // the selected rock has its tags and the readout
  if (tip.hidden) return;
  const row = keys?.[i];
  const size = measured(i) ? `${metres(cols.size_q50[i])} m ${k(sizeState(i) === 2 ? 'measured, a bound' : 'measured')}`
    : `${sig2(cols.size_q05[i])}–${sig2(cols.size_q95[i])} m ${k('90% range, estimated')}`;
  tip.innerHTML = (row ? `<div class="tn">${esc(row[2] || row[1])}</div>` : '') +
    `<div>${k('Δv')} ${cols.dv[i].toFixed(3)} km/s</div><div>${k('Diameter')} ${size}</div>` +
    (S.m ? `<div>${k(MISSION_NAME[S.m])} ${verdictText(i, S.m)}</div>` : '');
  // beside the rock, on whichever side has room; anchored on that side so it never narrows to fit
  const x = field.sx(i), y = field.sy(i), flip = x > field.w - 300;
  Object.assign(tip.style, { position: 'absolute', top: y + 'px', whiteSpace: 'nowrap', transform: 'translateY(-50%)',
    left: flip ? 'auto' : x + 12 + 'px', right: flip ? field.w - x + 12 + 'px' : 'auto' });
}

// ---- the axes: ticks, titles, the Max Δv line and the crosshair, as HTML and SVG over the canvas ----

const FONT = '12px B612, system-ui, sans-serif';
const X_TITLE = 'Δv, cheapest round trip (km/s)', Y_TITLE = 'Diameter (m)';
let ctx2d, grid, zoomGroup, zoomOut, zoomIn, zoomReset, wasZoomed = false;
const textWidth = s => (ctx2d ||= Object.assign(document.createElement('canvas').getContext('2d'), { font: FONT })).measureText(s).width;

function xTicks(f) {
  const V = f.V, span = V.x1 - V.x0, want = f.M.phone ? 5 : 9, steps = [0.05, 0.1, 0.2, 0.25, 0.5, 1, 2];
  const st = steps.find(s => span / s <= want) ?? 2, dec = st >= 1 ? 0 : st === 0.25 || st === 0.05 ? 2 : 1, out = [];
  for (let k = Math.ceil(V.x0 / st - 1e-9); k * st <= V.x1 + 1e-9; k++) out.push({ v: k * st, t: (k * st).toFixed(dec) });
  return { major: out, minor: st / 2 };
}
function yTicks(f) {
  const V = f.V, dec = V.y1 - V.y0, major = [], minor = [];
  if (dec < 0.35) {   // under a third of a decade in view: round values on linear steps
    const lo = 10 ** V.y0, hi = 10 ** V.y1, want = f.M.phone ? 4 : 6;
    let st = 1;
    for (let e = Math.floor(Math.log10(hi - lo)) - 1; ; e++) {
      const ok = [1, 2, 5].map(m => m * 10 ** e).filter(s => (hi - lo) / s <= want);
      if (ok.length) { st = ok[0]; break; }
    }
    for (let s = Math.ceil(lo / st) * st; s <= hi + 1e-9; s += st) {
      const v = +s.toPrecision(6);
      major.push({ v, t: v < 1 ? String(+v.toFixed(2)) : count(+v.toFixed(st < 1 ? 1 : 0)) });
      if (v + st / 2 <= hi) minor.push(v + st / 2);
    }
    return { major, minor };
  }
  const lab = dec > 1.8 ? [1, 3] : dec > 0.7 ? [1, 2, 5] : [1, 2, 3, 4, 5, 6, 7, 8, 9];
  for (let d = Math.floor(V.y0) - 1; d <= Math.ceil(V.y1); d++) for (let k = 1; k <= 9; k++) {
    const s = k * 10 ** d, l = Math.log10(s);
    if (l < V.y0 - 1e-9 || l > V.y1 + 1e-9) continue;
    if (lab.includes(k)) major.push({ v: s, t: s < 1 ? String(+s.toFixed(2)) : count(Math.round(s)) }); else minor.push(s);
  }
  return { major, minor };
}

function drawAxes(f) {
  const M = f.M, W = f.w, H = f.h, PW = f.pw, PH = f.ph, L = M.l, T = M.t, R = L + PW, B = T + PH;
  const X = xTicks(f), Y = yTicks(f), round = v => Math.round(v) + 0.5, inX = x => x >= L && x <= R, inY = y => y >= T && y <= B;
  // The selection's tags: on the axes, so in the axes' units with none written: the plotted Δv and diameter.
  const s = sel >= 0 && sel < n ? sel : -1, sx = s >= 0 ? f.sx(s) : 0, sy = s >= 0 ? f.sy(s) : 0;
  const xs = s >= 0 ? cols.dv[s].toFixed(3) : '', ys = s >= 0 ? (measured(s) ? metres : sig2)(cols.size_q50[s]) : '', xw = textWidth(xs) + 10;
  const tagX = s >= 0 && inX(sx), tagY = s >= 0 && inY(sy);

  // behind the rocks: gridlines
  let g = '';
  for (const t of X.major) { const x = round(f.px(t.v)); if (inX(x)) g += `M${x} ${T}V${B}`; }
  for (const t of Y.major) { const y = round(f.py(Math.log10(t.v))); if (inY(y)) g += `M${L} ${y}H${R}`; }
  grid.setAttribute('viewBox', `0 0 ${W} ${H}`);
  grid.innerHTML = `<path d="${g}" style="stroke:var(--grid,#202020);stroke-width:1;fill:none"/>`;

  // over the rocks: the frame and its ticks, pointing in on all four sides
  let t = '';
  const xt = (v, len) => { const x = round(f.px(v)); if (inX(x)) t += `M${x} ${B}v${-len}M${x} ${T}v${len}`; };
  const yt = (v, len) => { const y = round(f.py(Math.log10(v))); if (inY(y)) t += `M${L} ${y}h${len}M${R} ${y}h${-len}`; };
  for (const k of X.major) { xt(k.v, 7); xt(k.v + X.minor, 4); }
  for (const k of Y.major) yt(k.v, 7);
  for (const v of Y.minor) yt(v, 4);
  let svg = `<rect x="${L + 0.5}" y="${T + 0.5}" width="${PW - 1}" height="${PH - 1}" style="fill:none;stroke:var(--edge,#5e5e5e)"/>` +
    `<path d="${t}" style="fill:none;stroke:var(--edge,#5e5e5e)"/>`;
  let html = '';
  const span = (cls, style, text) => { html += `<span class="${cls}" style="${style}">${esc(text)}</span>`; };

  // Max Δv: a bound, so dashed; labelled with its value. The asteroids beyond it are faint.
  const cx = S.dv ? f.px(S.dv) : Infinity;
  if (S.dv && inX(cx)) {
    const x = round(cx), lab = `Max Δv ${S.dv.toFixed(1)} km/s`, w = textWidth(lab);
    svg += `<path d="M${x} ${T}V${B}" style="stroke:var(--ink-2,#a8a8a8);stroke-dasharray:4 3"/>`;
    span('ax-note', `left:${x + 6 + w + 10 > R ? x - 6 - w - 6 : x + 6}px;top:${T + 6}px`, lab);
  }
  // the selected rock: a crosshair to both axes
  if (s >= 0) {
    const cy = v => Math.min(B, Math.max(T, v)), cxp = v => Math.min(R, Math.max(L, v));
    // the lines stop short of the rock's widest reach at this zoom (it grows with zoom, and turns), plus a gap
    const gap = MARK.sel * f.s + MARK.glow + 2;
    let c = '';
    if (inY(sy)) c += `M${L} ${round(sy)}H${cxp(sx - gap)}`;
    if (tagX) c += `M${round(sx)} ${cy(sy + gap)}V${B}`;
    svg += `<path d="${c}" style="fill:none;stroke:var(--edge,#5e5e5e)"/>`;
  }

  // tick labels; a label the selection's axis tag would cover is left out
  for (const k of X.major) {
    const x = f.px(k.v);
    if (!inX(x) || (tagX && Math.abs(x - sx) < (textWidth(k.t) + xw) / 2 + 4)) continue;
    span('ax-t', `left:${x}px;top:${B + 6}px;transform:translateX(-50%)`, k.t);
  }
  for (const k of Y.major) {
    const y = f.py(Math.log10(k.v));
    if (!inY(y) || (tagY && Math.abs(y - sy) < 17)) continue;
    span('ax-t', `right:${W - L + 8}px;top:${y - 8}px`, k.t);
  }
  span('ax-title', `left:${L + PW / 2}px;top:${H - 22}px;transform:translateX(-50%)`, X_TITLE);
  span('ax-title', `left:${M.phone ? 10 : 14}px;top:${T + PH / 2}px;transform:translate(-50%,-50%) rotate(-90deg)`, Y_TITLE);
  if (tagY) span('ax-tag', `right:${W - L + 2}px;top:${sy - 9}px`, ys);
  if (tagX) span('ax-tag', `left:${sx}px;top:${B + 5}px;transform:translateX(-50%)`, xs);

  axes.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" aria-hidden="true">${svg}</svg>${html}`;

  // the zoom buttons, and the legend's estimated mark once the dots turn into outlines
  const z = f.z;
  if (zoomOut) zoomOut.disabled = z <= 1.001;
  if (zoomReset) zoomReset.disabled = z <= 1.001;
  if (zoomIn) zoomIn.disabled = z >= ZMAX - 0.01;
  if (f.zoomed !== wasZoomed) { wasZoomed = f.zoomed; legend(); }
  if (tip && !tip.hidden && f.hot >= 0) hover(f.hot);
}

// ---- input ----------------------------------------------------------------------------------

function listen() {
  if (plot && canvas) {
    canvas.insertAdjacentHTML('beforebegin', '<svg class="grid" aria-hidden="true"></svg>');   // the gridlines, behind the rocks
    grid = canvas.previousElementSibling;
  }
  // the zoom group: buttons in the form, named zoom-out, zoom-in and zoom-reset
  zoomOut = E['zoom-out']; zoomIn = E['zoom-in']; zoomReset = E['zoom-reset'];
  zoomGroup = zoomIn?.parentElement !== form && zoomIn?.parentElement?.contains(zoomOut) ? zoomIn.parentElement : null;
  zoomOut?.addEventListener('click', () => field?.zoom(0.5));
  zoomIn?.addEventListener('click', () => field?.zoom(2));
  zoomReset?.addEventListener('click', () => field?.home());

  form.addEventListener('input', e => {
    const name = e.target.name;
    // the first step of a slide or of typing is a new entry in the history; the rest of it rewrites that entry
    const step = () => { write(adjusting === name); adjusting = name; };
    if (name === 'dv') { S.dv = ceiling(+E.dv.value); showDv(); S.page = 0; filter(); if (S.view === 'table') renderTable(); step(); }
    else if (name === 'q') {
      S.q = E.q.value; S.page = 0; filter(); suggest();
      say(S.q.trim() && hay && !matches(S.q).length ? 'No match' : '');
      if (S.view === 'table') renderTable();
      step();
    } else if (name === 'm') mission(E.m.value);
    else if (name === 'view') setView(E.view.value);
  });
  form.addEventListener('change', e => {
    if (e.target.name === adjusting) adjusting = '';
    // a name picked from the suggestions opens it
    if (e.target.name === 'q' && S.view === 'chart' && hay && matches(S.q).some(r => nameOf(r) === S.q)) find();
  });
  form.addEventListener('submit', e => { e.preventDefault(); find(); });
  addEventListener('popstate', () => { read(); apply(); });

  // A link to an entry opens its summary here; a modified click, or Full details, goes to the page.
  document.addEventListener('click', e => {
    const a = e.target.closest?.('a[href]');
    if (!a || a.hasAttribute('data-open') || a.origin !== location.origin || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const hit = a.pathname.match(/\/a\/([^/]+)\.html$/), key = hit && decodeURIComponent(hit[1]);
    if (!key || (index && !index.has(key)) || a.hash) return;
    e.preventDefault();
    select(key, true);
  });
  if (tip && !tip.hasAttribute('role')) tip.setAttribute('role', 'status');
  if (canvas) {
    canvas.tabIndex = 0;
    if (!canvas.hasAttribute('aria-label')) canvas.setAttribute('aria-label', 'Asteroids by delta-v (Δv) and diameter. Plus and minus zoom, arrow keys pan, Shift and an arrow key move between asteroids, Enter opens one.');
    canvas.addEventListener('keydown', e => {
      if (!field || e.ctrlKey || e.metaKey || e.altKey) return;                    // the browser's own: zoom, back, new tab
      const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
      if (d && (e.shiftKey || field.z <= 1.001)) {                     // move between rocks; at home there is nothing to pan
        const from = field.hot >= 0 ? field.hot : sel >= 0 && sel < n ? sel : -1;
        const i = from < 0 ? field.pick(field.M.l + field.pw / 2, field.M.t + field.ph / 2, 1e5) : field.step(from, d[0], d[1]);
        if (i >= 0) { field.reveal(i); field.hover(i); }
      } else if (d) field.pan(-d[0] * 40, -d[1] * 40);
      else if (e.key === 'Enter' && field.hot >= 0 && keys) select(keys[field.hot][0], true);
      else if (e.key === '+' || e.key === '=') field.zoom(2);
      else if (e.key === '-' || e.key === '_') field.zoom(0.5);
      else if (e.key === '0') field.home();
      else return;
      e.preventDefault();
    });
  }
  document.addEventListener('keydown', e => {                          // Escape closes the summary, not while typing in a control
    if (e.key === 'Escape' && S.a && !e.target.closest?.('input, select, textarea')) select('', true);
  });
}
function mission(m) {
  S.m = MISSIONS.includes(m) ? m : '';
  S.page = 0; S.sort = ''; S.dir = 0; listed = null;                  // a mission sorts by its own chance first
  setControl('m', S.m);
  field?.setMission(S.m);
  filter();                                                             // its ruled-out asteroids leave the filter
  if (S.view === 'table') renderTable();
  if (tip && !tip.hidden && field?.hot >= 0) hover(field.hot);
  write();
}
function setView(v) {
  S.view = v === 'table' ? 'table' : 'chart';
  setControl('view', S.view);
  if (S.view === 'chart' && field?.hot >= 0) field.hover(-1);
  view();
  write();
}

start().catch(err => { console.error(err); if (!field) note('The chart did not load.'); });
