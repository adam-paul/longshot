"""Shared helpers for the cx_ (coverage-exact) scripts: designation handling, SBDB/NHATS loading, VizieR TSV parsing."""
import json, re

B62 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
LET25 = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


def b62(s):
    n = 0
    for ch in s:
        n = n * 62 + B62.index(ch)
    return n


def unpack_number(p):
    """MPC packed permanent number (5 chars) -> int, or None."""
    p = p.strip()
    if not p:
        return None
    if p.isdigit():
        return int(p)
    if len(p) == 5 and p[0] == '~':
        try:
            return 620000 + b62(p[1:])
        except ValueError:
            return None
    if len(p) == 5 and p[0].isalpha() and p[1:].isdigit():
        return B62.index(p[0]) * 10000 + int(p[1:])
    return None


def unpack_prov(p):
    """MPC packed provisional designation (7 chars) -> 'YYYY XYnnn', or None."""
    p = p.strip()
    if len(p) != 7:
        return None
    if p[0] in 'IJKL' and p[1:3].isdigit() and p[3].isalpha() and p[6].isalpha():
        yr = {'I': 18, 'J': 19, 'K': 20, 'L': 21}[p[0]] * 100 + int(p[1:3])
        c = p[4:6]
        if not c[1].isdigit():
            return None
        if c[0].isdigit():
            n = int(c)
        else:
            n = B62.index(c[0]) * 10 + int(c[1])
        return '%d %s%s%s' % (yr, p[3], p[6], n if n else '')
    if p[0] == '_':
        try:
            yr = 2000 + B62.index(p[1])
            n = b62(p[3:7])
        except ValueError:
            return None
        return '%d %s%s%d' % (yr, p[2], LET25[n % 25], n // 25 + 620)
    if p[:3] in ('PLS', 'T1S', 'T2S', 'T3S') and p[3:].isdigit():
        return '%s %s' % (p[3:], 'P-L' if p[:3] == 'PLS' else 'T-' + p[1])
    return None


def norm(s):
    """Normalise a name or designation for matching: lower-case, no spaces/underscores."""
    return re.sub(r'[\s_]+', '', s.lower()) if s else ''


PROV_RE = re.compile(r'^(\d{4})\s*([A-Z]{2}\d*)$')
SURVEY_RE = re.compile(r'^(\d{4})\s*(P-L|T-[123])$')


class Universe:
    """SBDB NEA list (asteroids in the `neo` group) with lookups by number, provisional designation, name."""

    def __init__(self, sbdb_path):
        sb = json.load(open(sbdb_path))
        F = sb['fields']
        self.fields = F
        self.rows = [dict(zip(F, r)) for r in sb['data'] if r[F.index('kind')].startswith('a')]
        self.by_pdes = {}
        self.num2p = {}
        self.key2p = {}
        self.amb = set()
        for s in self.rows:
            p = s['pdes']
            self.by_pdes[p] = s
            fn = s['full_name'] or ''
            m = re.search(r'\(([^)]+)\)\s*$', fn)
            s['_prov'] = m.group(1).strip() if m else (p if not p.isdigit() else None)
            if p.isdigit():
                self.num2p[int(p)] = p
            else:
                self._add(norm(p), p)
            if s['_prov']:
                self._add(norm(s['_prov']), p)
            if s.get('name'):
                self._add(norm(s['name']), p)

    def _add(self, k, p):
        if not k:
            return
        if k in self.key2p and self.key2p[k] != p:
            self.amb.add(k)
            return
        self.key2p[k] = p

    def by_number(self, n):
        try:
            return self.num2p.get(int(n))
        except (TypeError, ValueError):
            return None

    def by_text(self, v):
        """Resolve free text: a number, a provisional designation, a name, or '(123) Name' / '123 Name'."""
        if v is None:
            return None
        v = str(v).strip()
        if not v or v.lower() in ('nan', 'null', 'none', '-', '--'):
            return None
        if re.fullmatch(r'\(?\d+\)?', v):
            return self.by_number(v.strip('()'))
        try:
            fv = float(v)
            if fv == int(fv) and fv > 0:
                return self.by_number(int(fv))
        except ValueError:
            pass
        k = norm(v)
        if k in self.key2p:
            return self.key2p[k]
        m = re.match(r'^\(?(\d+)\)?\s+(.+)$', v)
        if m and not PROV_RE.match(v) and not SURVEY_RE.match(v):
            p = self.by_number(m.group(1))
            if p:
                return p
            return self.by_text(m.group(2))
        return None

    def by_packed(self, v):
        """Resolve an MPC packed designation (5-char number or 7-char provisional), or plain text."""
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        if len(v) == 7:
            u = unpack_prov(v)
            if u:
                return self.key2p.get(norm(u))
        if len(v) == 5:
            n = unpack_number(v)
            if n is not None:
                return self.by_number(n)
        return self.by_text(v)

    def resolve(self, *vals, packed=()):
        for v in packed:
            p = self.by_packed(v)
            if p:
                return p
        for v in vals:
            p = self.by_text(v)
            if p:
                return p
        return None


def load_nhats(path):
    d = json.load(open(path))['data']
    out = {}
    for r in d:
        out[r['des']] = {'dv': float(r['min_dv']['dv']), 'h': float(r['h']) if r['h'] else None, 'occ': r.get('occ'),
                         'min_size': r.get('min_size'), 'max_size': r.get('max_size')}
    return out


def parse_vizier(fn):
    """Parse a VizieR asu-tsv file with one or more tables -> {table_name: [row dicts]}."""
    tables = {}
    name = None
    hdr = None
    state = 0
    for line in open(fn, errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('#Name:'):
            name = line.split(':', 1)[1].strip()
            hdr = None
            state = 0
            continue
        if line.startswith('#') or not line.strip():
            continue
        if name is None:
            continue
        if state == 0:
            hdr = [h.strip() for h in line.split('\t')]
            tables[name] = []
            state = 1
        elif state < 3:
            state += 1
        else:
            vals = [v.strip() for v in line.split('\t')]
            tables[name].append(dict(zip(hdr, vals)))
    return tables
