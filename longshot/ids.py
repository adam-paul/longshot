"""Object keys and aliases.

Every object in JPL's table of near-Earth objects gets an opaque key, minted
once and recorded in registry/keys.jsonl. JPL's own primary designation changes
when an asteroid is numbered, so nothing downstream joins on it.

    index = ids.load()                  # reads the table, mints what is missing
    index.resolve("(99942) Apophis")    # -> key, or None
    index.identity(key)                 # -> Identity

The registry is only ever appended to. A key is drawn from the line's position
in the registry, never from the designation.
"""
from __future__ import annotations

import functools
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from longshot import config
from longshot.ingest._common import IngestError, read_json, text

try:  # POSIX only; the lock keeps two builds from minting at once
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

KEY_RE = re.compile(r"^[a-z][a-z0-9]{5}$")
_LETTERS = "abcdefghijklmnopqrstuvwxyz"
_ALNUM = "0123456789abcdefghijklmnopqrstuvwxyz"
_KEYSPACE = 26 * 36 ** 5
_B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_LET25 = "ABCDEFGHJKLMNOPQRSTUVWXYZ"   # the second letter of a designation skips I


class RegistryError(Exception):
    """registry/keys.jsonl is damaged, or a build would have to rewrite a line."""


# --------------------------------------------------------------------------
# keys

MAX_ATTEMPTS = 8        # a clash with an earlier key moves to the next attempt; more than a few never happens


def generate_key(position: int, attempt: int = 0) -> str:
    """The key for the registry line at this position. Deterministic and opaque."""
    digest = hashlib.sha256(f"longshot-key:{position}:{attempt}".encode()).digest()
    v = int.from_bytes(digest[:8], "big") % _KEYSPACE
    v, rest = divmod(v, 36 ** 5)
    out = [_LETTERS[v]]
    for power in (36 ** 4, 36 ** 3, 36 ** 2, 36, 1):
        d, rest = divmod(rest, power)
        out.append(_ALNUM[d])
    return "".join(out)


def _parse_registry(body: str, path: Path) -> list[dict]:
    entries: list[dict] = []
    keys: set[str] = set()
    designations: set[str] = set()
    for n, line in enumerate(body.split("\n"), 1):
        if not line:
            continue
        try:
            e = json.loads(line)
        except ValueError as exc:
            raise RegistryError(f"{path}:{n}: not valid JSON ({exc})") from exc
        if not isinstance(e, dict) or sorted(e) != ["designation", "key", "minted"]:
            raise RegistryError(f"{path}:{n}: expected exactly key, designation, minted")
        if not isinstance(e["key"], str) or not KEY_RE.match(e["key"]):
            raise RegistryError(f"{path}:{n}: malformed key {e['key']!r}")
        if not isinstance(e["designation"], str) or not e["designation"].strip():
            raise RegistryError(f"{path}:{n}: empty designation")
        if e["key"] in keys:
            raise RegistryError(f"{path}:{n}: key {e['key']} appears twice")
        # A key is generated from its line's position (and, on a clash, the next attempt), so a line that was
        # deleted, inserted or moved shows here. Without this an object silently gets a new key and a new page.
        position = len(entries)
        if not any(e["key"] == generate_key(position, attempt) for attempt in range(MAX_ATTEMPTS)):
            raise RegistryError(
                f"{path}:{n}: key {e['key']} does not belong at position {position}: a line above it was "
                "removed, added or moved. Restore the file from version control")
        if e["designation"] in designations:
            raise RegistryError(f"{path}:{n}: designation {e['designation']!r} appears twice")
        keys.add(e["key"])
        designations.add(e["designation"])
        entries.append(e)
    return entries


def read_registry(path: Path | None = None) -> list[dict]:
    """The registry as a list of {key, designation, minted}, in file order."""
    path = Path(path or config.KEYS)
    if not path.exists():
        return []
    return _parse_registry(path.read_text(encoding="utf-8"), path)


def _registry_line(key: str, designation: str, minted: str) -> str:
    return json.dumps({"key": key, "designation": designation, "minted": minted}, ensure_ascii=False) + "\n"


def _mint(path: Path, wanted: list[tuple[str, tuple[str, ...]]], minted: str) -> dict[str, str]:
    """Give every wanted object a key, appending registry lines for the new ones.

    wanted: (designation, every designation the object has gone by), one per object.
    Returns {designation: key}. Existing lines are never changed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8", newline="\n") as fh:
        if fcntl is not None:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            fh.seek(0)
            body = fh.read()
            if body and not body.endswith("\n"):
                raise RegistryError(f"{path}: last line is incomplete")
            entries = _parse_registry(body, path)
            by_designation = {e["designation"]: e["key"] for e in entries}
            used = set(by_designation.values())
            out: dict[str, str] = {}
            new: list[str] = []
            for designation, spellings in wanted:
                found = {by_designation[s] for s in spellings if s in by_designation}
                if len(found) > 1:
                    raise RegistryError(
                        f"{path}: {designation!r} matches {len(found)} keys ({', '.join(sorted(found))}); "
                        "two registry lines describe one object"
                    )
                if found:
                    out[designation] = found.pop()
                else:
                    new.append(designation)
            position = len(entries)
            lines: list[str] = []
            for designation in sorted(set(new)):
                attempt = 0
                key = generate_key(position, attempt)
                while key in used:
                    attempt += 1
                    if attempt >= MAX_ATTEMPTS:
                        raise RegistryError(f"{path}: no free key for position {position} in {MAX_ATTEMPTS} attempts")
                    key = generate_key(position, attempt)
                used.add(key)
                out[designation] = key
                lines.append(_registry_line(key, designation, minted))
                position += 1
            if lines:
                fh.seek(0, 2)
                fh.write("".join(lines))
                fh.flush()
        finally:
            if fcntl is not None:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    return out


# --------------------------------------------------------------------------
# spellings

_APOSTROPHES = "'`‘’ʻʼ´′"
_PROV = re.compile(r"^(\d{4})[\s_]*([A-Za-z])[\s_]*([A-Za-z])[\s_]*(\d*)$")
_OLD_PROV = re.compile(r"^A(\d{3})[\s_]*([A-Za-z])[\s_]*([A-Za-z])[\s_]*(\d*)$", re.I)
_SURVEY = re.compile(r"^(\d{4})[\s_]*(P-L|T-[123])$", re.I)
_PACKED_PROV = re.compile(r"^[IJKL]\d{2}[A-Z][0-9A-Za-z]\d[A-Z]$")
_PACKED_EXT = re.compile(r"^_[0-9A-Za-z][A-Z][0-9A-Za-z]{4}$")
_PACKED_SURVEY = re.compile(r"^(PLS|T1S|T2S|T3S)(\d{4})$")
_PACKED_NUM = re.compile(r"^[A-Za-z]\d{4}$")
_PACKED_NUM_EXT = re.compile(r"^~[0-9A-Za-z]{4}$")
_PURE_NUMBER = re.compile(r"^\(?\s*(\d{1,7})\s*\)?$")
_PAREN_NUMBER = re.compile(r"^\(\s*(\d{1,7})\s*\)\s*(\S.*)$")


def _fold(s: str) -> str:
    """Lower-case letters and digits only: spacing, punctuation and accents dropped."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s.casefold() if c.isascii() and c.isalnum())


def canonical_designation(s: str) -> str | None:
    """'2011aa37', '2011_AA37', 'A898 PA', '2040 p-l' -> the standard spelling, or None."""
    s = s.strip()
    m = _PROV.match(s)
    if m and 1800 <= int(m.group(1)) <= 2199:
        return f"{m.group(1)} {m.group(2).upper()}{m.group(3).upper()}{m.group(4).lstrip('0')}"
    m = _OLD_PROV.match(s)
    if m:
        n = m.group(4).lstrip("0")
        return f"1{m.group(1)} {m.group(2).upper()}{m.group(3).upper()}{n}"
    m = _SURVEY.match(s)
    if m:
        return f"{m.group(1)} {m.group(2).upper()}"
    return None


def unpack_designation(p: str) -> str | None:
    """A Minor Planet Center packed provisional designation -> '2011 AA37', or None."""
    if _PACKED_PROV.match(p):
        year = {"I": 18, "J": 19, "K": 20, "L": 21}[p[0]] * 100 + int(p[1:3])
        cycle = int(p[4:6]) if p[4].isdigit() else _B62.index(p[4]) * 10 + int(p[5])
        return f"{year} {p[3]}{p[6]}{cycle or ''}"
    if _PACKED_EXT.match(p):
        n = 0
        for ch in p[3:7]:
            n = n * 62 + _B62.index(ch)
        return f"{2000 + _B62.index(p[1])} {p[2]}{_LET25[n % 25]}{n // 25 + 620}"
    m = _PACKED_SURVEY.match(p)
    if m:
        return f"{m.group(2)} {'P-L' if m.group(1) == 'PLS' else 'T-' + m.group(1)[1]}"
    return None


def unpack_number(p: str) -> int | None:
    """A packed permanent number ('k9219', '~0000') -> int, or None. Plain digits are not packed."""
    if _PACKED_NUM.match(p):
        return _B62.index(p[0]) * 10000 + int(p[1:])
    if _PACKED_NUM_EXT.match(p):
        n = 0
        for ch in p[1:]:
            n = n * 62 + _B62.index(ch)
        return 620000 + n
    return None


# --------------------------------------------------------------------------
# identities

@dataclass(frozen=True)
class Identity:
    key: str
    pdes: str                    # JPL's primary designation today: the number once numbered
    designation: str             # the provisional designation where there is one, else pdes
    name: str | None             # as shown: JPL's backtick becomes the okina
    number: int | None
    kind: str                    # JPL's kind: an, au (asteroids), cn, cu (comets)
    aliases: tuple[str, ...]     # spellings JPL gives, for display and search


_FULL_NAME = re.compile(r"^\s*(\d+)?\s*([^()]*?)\s*(?:\(([^)]*)\))?\s*$")


def _display_name(name: str | None) -> str | None:
    return name.replace("`", "ʻ") if name else name


def _parse_sbdb_row(row: dict) -> dict:
    """Split one row of JPL's table into number, name, provisional designation and spellings."""
    pdes = text(row.get("pdes"))
    if not pdes:
        raise IngestError(f"{config.SBDB_JSON}: a row has no pdes")
    full = text(row.get("full_name")) or pdes
    kind = text(row.get("kind")) or ""
    name = text(row.get("name"))
    prefix = text(row.get("prefix"))
    number = None
    prov = None
    spellings: list[str] = [pdes, full]
    if kind.startswith("c"):
        if prefix and not pdes.endswith(prefix) and not re.match(r"^\d+[A-Z]", pdes):
            spellings.append(f"{prefix}/{pdes}")
        designation = pdes
    else:
        m = _FULL_NAME.match(full)
        if m:
            if m.group(1) and m.group(1) == pdes:
                number = int(m.group(1))
            prov = text(m.group(3))
        if prov and prov.startswith("A/"):
            spellings.append(prov)
            prov = prov[2:]
        if number is None and pdes.isdigit():
            number = int(pdes)
        designation = prov or pdes
        if prov:
            spellings.append(prov)
            old = canonical_designation(prov)
            if old and old != prov:
                spellings.append(old)      # 'A898 PA' is also '1898 PA'
        if number is not None:
            if name:
                spellings += [f"{number} {name}", f"({number}) {name}"]
            if prov:
                spellings += [f"{number} {prov}", f"({number}) {prov}"]
        if name and prov:
            spellings.append(f"{name} ({prov})")
    return {
        "pdes": pdes, "designation": designation, "name": name, "number": number, "kind": kind,
        "spellings": spellings,
        "registry_spellings": tuple(dict.fromkeys(s for s in (pdes, prov) if s)),
    }


_SORT_PROV = re.compile(r"^(\d{4}) ([A-Z])([A-Z])(\d*)$")


def sort_key(ident: Identity) -> tuple:
    """Numbered objects by number, then provisional designations in order of assignment."""
    if ident.number is not None:
        return (0, ident.number, "", 0, "", ident.pdes)
    m = _SORT_PROV.match(ident.pdes)
    if m:
        return (1, int(m.group(1)), m.group(2), int(m.group(4) or 0), m.group(3), ident.pdes)
    return (2, 0, "", 0, "", ident.pdes)


class Index:
    """Keys, identities and the alias resolver for one build."""

    def __init__(self, identities: list[Identity], extra: dict[str, list[tuple[str, str]]]):
        self._by_key = {i.key: i for i in identities}
        self._by_pdes = {i.pdes: i.key for i in identities}
        self._by_number: dict[int, str] = {}
        self._exact: dict[str, set[str]] = {}
        self._names: dict[str, set[str]] = {}
        for ident in identities:
            if ident.number is not None:
                self._by_number.setdefault(ident.number, ident.key)
            for kind, spelling in extra[ident.key]:
                folded = _fold(spelling)
                if not folded or folded.isdigit():
                    continue
                (self._names if kind == "name" else self._exact).setdefault(folded, set()).add(ident.key)

    def __len__(self) -> int:
        return len(self._by_key)

    def keys(self) -> list[str]:
        return list(self._by_key)

    def identity(self, key: str) -> Identity:
        return self._by_key[key]

    def key_for_pdes(self, pdes: str) -> str | None:
        """Exact lookup by JPL's primary designation, as the JPL files spell it."""
        return self._by_pdes.get(pdes)

    def _lookup(self, spelling: str) -> set[str]:
        folded = _fold(spelling)
        if not folded or folded.isdigit():
            return set()
        return set(self._exact.get(folded, ())) | set(self._names.get(folded, ()))

    def resolve(self, spelling, number=None) -> str | None:
        """Map any spelling a source uses to a key. None when unknown or ambiguous.

        number: a separate number column, when the source has one. It must agree
        with the spelling, or the answer is None.
        """
        found: set[str] = set()
        if number is not None and str(number).strip() not in ("", "0"):
            try:
                n = int(str(number).strip())
            except ValueError:
                return None
            key = self._by_number.get(n)
            if key is None:
                return None
            if spelling is None or not str(spelling).strip():
                return key
            other = self.resolve(spelling)
            return key if other in (None, key) else None
        if spelling is None or isinstance(spelling, bool):
            return None
        if isinstance(spelling, int):
            return self._by_number.get(spelling)
        s = " ".join(str(spelling).replace("_", " ").split())
        for ch in _APOSTROPHES:
            s = s.replace(ch, "")
        if not s:
            return None
        m = _PURE_NUMBER.match(s)
        if m:
            return self._by_number.get(int(m.group(1)))
        raw = str(spelling).strip()
        packed = unpack_designation(raw)
        if packed:
            found |= self._lookup(packed)
        n = unpack_number(raw)
        if n is not None and n in self._by_number:
            found.add(self._by_number[n])
        if s.startswith("(") and s.endswith(")") and s.count("(") == 1:
            s = s[1:-1].strip()               # NHATS writes '(2010 PS66)'
        canon = canonical_designation(s)
        if canon:
            found |= self._lookup(canon)      # a designation is never read as number + name
        else:
            found |= self._lookup(s)
            m = _PAREN_NUMBER.match(s)
            if m and not found:
                key = self._by_number.get(int(m.group(1)))
                if key is not None:
                    rest = self.resolve(m.group(2))
                    if rest in (None, key):
                        found.add(key)
        return found.pop() if len(found) == 1 else None


def build_index(
    sbdb_path: Path | None = None,
    registry_path: Path | None = None,
    nhats_path: Path | None = None,
    minted: str | None = None,
) -> Index:
    """Read JPL's table, mint keys for anything new, and build the resolver."""
    sbdb_path = Path(sbdb_path or config.SBDB_JSON)
    registry_path = Path(registry_path or config.KEYS)
    minted = minted or config.DATA_DATE
    table = read_json(sbdb_path)
    if not isinstance(table, dict) or not isinstance(table.get("fields"), list) or not isinstance(table.get("data"), list):
        raise IngestError(f"{sbdb_path}: expected an object with 'fields' and 'data'")
    fields = table["fields"]
    for needed in ("full_name", "pdes", "name", "prefix", "kind"):
        if needed not in fields:
            raise IngestError(f"{sbdb_path}: field {needed!r} is missing")
    if not table["data"]:
        raise IngestError(f"{sbdb_path}: no rows")
    parsed = []
    seen: set[str] = set()
    for row in table["data"]:
        if len(row) != len(fields):
            raise IngestError(f"{sbdb_path}: a row has {len(row)} cells, expected {len(fields)}")
        p = _parse_sbdb_row(dict(zip(fields, row)))
        if p["pdes"] in seen:
            raise IngestError(f"{sbdb_path}: {p['pdes']!r} appears twice")
        seen.add(p["pdes"])
        parsed.append(p)

    # The reachable list may name an object JPL's table lacks; it still gets a key.
    if nhats_path is None and sbdb_path == Path(config.SBDB_JSON):
        nhats_path = config.NHATS_JSON
    if nhats_path is not None and Path(nhats_path).exists():
        listing = read_json(Path(nhats_path))
        for r in (listing.get("data") or []) if isinstance(listing, dict) else []:
            des = text(r.get("des")) if isinstance(r, dict) else None
            if des and des not in seen:
                seen.add(des)
                number = int(des) if des.isdigit() else None
                parsed.append({
                    "pdes": des, "designation": des, "name": None, "number": number, "kind": "",
                    "spellings": [des, text(r.get("fullname")) or des],
                    "registry_spellings": (des,),
                })

    keys = _mint(registry_path, [(p["pdes"], p["registry_spellings"]) for p in parsed], minted)
    identities: list[Identity] = []
    extra: dict[str, list[tuple[str, str]]] = {}
    for p in parsed:
        key = keys[p["pdes"]]
        full = " ".join(p["spellings"][1].split())
        if _fold(full) in (_fold(p["pdes"]), _fold(p["designation"])):
            full = None                        # '(2011 AA37)' adds nothing to '2011 AA37'
        aliases = tuple(dict.fromkeys(s for s in (p["pdes"], p["designation"], p["name"], full) if s))
        identities.append(Identity(
            key=key, pdes=p["pdes"], designation=p["designation"], name=_display_name(p["name"]),
            number=p["number"], kind=p["kind"], aliases=aliases,
        ))
        spellings = [("exact", s) for s in p["spellings"]]
        if p["name"]:
            spellings.append(("name", p["name"]))
        extra[key] = spellings
    return Index(identities, extra)


@functools.lru_cache(maxsize=1)
def load() -> Index:
    """The index for the configured snapshot and registry, built once per process."""
    return build_index()


def resolve(spelling, number=None) -> str | None:
    return load().resolve(spelling, number=number)


def identity(key: str) -> Identity:
    return load().identity(key)
