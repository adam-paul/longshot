"""Pravec's Ondřejov table of "prepublished" rotation periods, with quality grades.

One fixed-width text file; one analysis per record line, each followed by a
line that is blank or holds a plot address. The layout is taken from the file's
own header line and checked against the labels this reader knows, so a changed
layout stops the build instead of shifting columns.

The U column is a whole-number grade. Where the remark states a finer one
("U = 2-", "U = 1+ or 2-") the remark's grade is the claim's quality, the lower
of an "or" pair, and the claim's note quotes the remark. A remark can say the
period is a lower limit ("P > 20 h"); such a row becomes a lower bound, not a
value.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

from longshot import config, ids
from longshot.ingest import nhats
from longshot.ingest._common import (OLDER_THAN_OBJECT, IngestError, first_observed, iso_date, num, read_table, sig,
                                     too_old_for)
from longshot.types import Claim, Coverage, Source

SOURCE_ID = "pravec"
HEADER = [
    "AsterId", "Period[h]", "+/-", "err", "[h]", "DPsynsid[h]", "Ampl.", "U", "r", "DateUT", "LCfirst_LClast",
    "Phase", "LCf_LCl", "LPABf_LPABl,BPABf_BPABl", "MS", "H", "+/-", "G", "+/-", "ProjectId", "a/m",
    "DateExport", "Analyser", "Remark",
]
_LOWER = re.compile(
    r"\bP\s*>\s*[=~]?\s*\d"
    r"|lower limit on (the )?(P\b|period)"
    r"|(effectively|formally) a lower limit"
    r"|period (probably |definitely )?longer than \d",
    re.I,
)
_LOWER_VALUE = re.compile(r"\bP\s*>\s*[=~]?\s*(\d+(?:\.\d+)?)\s*h", re.I)
_REMARK_U = re.compile(r"\bU\s*=\s*([0-3][+-]?(?:\s+or\s+[0-3][+-]?)?)")
_LC_DATE = re.compile(r"(\d{4})-\s*(\d{1,2})-\s*(\d{1,2})")
_EXPORT = re.compile(r"^\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\s*$")


def _columns(header: str, path: Path) -> dict[str, int]:
    found = [(m.group(0), m.start()) for m in re.finditer(r"\S+", header)]
    if [t for t, _ in found] != HEADER:
        raise IngestError(f"{path}: the header line is not the layout this reader knows")
    at = [s for _, s in found]
    return {
        "period": at[1] - 2,      # AsterId is 29 characters and a space; the period is right-aligned from there
        "error": at[2], "dp": at[5], "ampl": at[6], "u": at[7], "r": at[8], "dates": at[9], "phase": at[11],
        "export": at[21], "analyser": at[22], "remark": at[23],
    }


def parse(path: Path | None = None) -> list[dict]:
    """Every record line: ident, period_h, error_h, amplitude, u, last_lc, exported, analyser, remark, line."""
    path = Path(path or config.PRAVEC_TXT)
    lines = read_table(path).decode("latin-1").split("\n")
    c = _columns(lines[0].rstrip("\r"), path)
    rows: list[dict] = []
    for n, line in enumerate(lines[1:], 2):
        line = line.rstrip("\r")
        if not line.strip() or line[0].isspace():
            continue                                   # blank, or a plot address under the record
        if len(line) < c["analyser"]:
            raise IngestError(f"{path}:{n}: record line is cut short")
        ident = line[:c["period"]].strip()
        cell = line[c["period"]:c["error"]].strip()
        period = num(cell)
        if cell and period is None:
            raise IngestError(f"{path}:{n}: period {cell!r} is not a number")
        u_cell = line[c["u"]:c["r"]].strip()
        if u_cell not in ("", "0", "1", "2", "3"):
            raise IngestError(f"{path}:{n}: U {u_cell!r} is not a grade")
        last = None
        dates = _LC_DATE.findall(line[c["dates"]:c["phase"]])
        if dates:
            y, m, d = dates[-1]
            last = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        exported = None
        m = _EXPORT.match(line[c["export"]:c["analyser"]])
        if m:
            exported = f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
        rows.append({
            "ident": ident, "period_h": period, "error_h": num(line[c["error"]:c["dp"]]),
            "amplitude": num(line[c["ampl"]:c["u"]]), "u": u_cell or None, "last_lc": last, "exported": exported,
            "analyser": " ".join(line[c["analyser"]:c["remark"]].split()) or None,
            "remark": " ".join(line[c["remark"]:].split()), "line": n,
        })
    if not rows:
        raise IngestError(f"{path}: no record lines")
    return rows


@functools.lru_cache(maxsize=1)
def _rows() -> tuple[dict, ...]:
    return tuple(parse())


def source() -> Source:
    path = Path(config.PRAVEC_TXT)
    return Source(
        id=SOURCE_ID,
        name="Ondřejov NEO Photometric Program",
        edition=edition(),
        retrieved=iso_date(path.name) or "",
        licence="single",
        citation='Pravec et al., "Prepublished" periods of asteroids, Ondřejov NEO Photometric Program '
                 "(unrefereed; no terms stated)",
        url="http://space.asu.cas.cz/~ppravec/newres.txt",
    )


def resolve_ident(ident: str, index: ids.Index) -> str | None:
    """'(11054) 1991 FA', '2023 RA4', '(15817) Lucianotesi = 1994 QC' -> key."""
    keys = {index.resolve(part) for part in ident.split(" = ")}
    keys.discard(None)
    return keys.pop() if len(keys) == 1 else None


def is_lower_limit(row: dict) -> bool:
    return bool(_LOWER.search(row["remark"]))


def _grade_rank(g: str) -> int:
    """'3' -> 9, '3-' -> 8, '2+' -> 7, '2' -> 6, '2-' -> 5, '1+' -> 4, as longshot.ledger.grade_rank."""
    return int(g[0]) * 3 + {"": 0, "+": 1, "-": -1}[g[1:]]


def remark_grade(row: dict) -> tuple[str | None, str | None]:
    """(grade, the remark's own words) when the remark states a grade; the lower of an 'or' pair."""
    m = _REMARK_U.search(row["remark"])
    if not m:
        return None, None
    words = " ".join(m.group(1).split())
    grades = [g.strip() for g in words.split(" or ")]
    return min(grades, key=_grade_rank), words


def grade_of(row: dict) -> str | None:
    """The grade a row carries: the remark's where it states one, else the U column."""
    return remark_grade(row)[0] or row["u"]


def _rank(row: dict) -> tuple:
    g = grade_of(row)
    return (_grade_rank(g) if g else -1, row["last_lc"] or "", row["line"])


def claims_for(key: str, rows: list[dict]) -> list[Claim]:
    """The best value row and the best lower-limit row: highest U, then the latest lightcurve."""
    out: list[Claim] = []
    with_period = [r for r in rows if r["period_h"] is not None and r["period_h"] > 0]
    for lower in (False, True):
        pick = [r for r in with_period if is_lower_limit(r) == lower]
        if not pick:
            continue
        r = max(pick, key=_rank)
        value = r["period_h"]
        lo = hi = None
        notes = []
        if lower:
            m = _LOWER_VALUE.search(r["remark"])
            if m:
                value = min(value, float(m.group(1)))
            notes.append("lower limit, from the table's remark")
        elif r["error_h"]:
            lo, hi = sig(value - r["error_h"]), sig(value + r["error_h"])
        quality = r["u"]
        finer, words = remark_grade(r)
        if finer is not None and words != (r["u"] or ""):
            quality = finer
            if " or " in words:                        # the grade alone says the rest
                notes.append(f"graded {words.replace('-', '−')}; the lower grade is used")
        if len(rows) > 1:
            notes.append(f"{len(rows)} analyses in the table")
        ref = f"analysis by {r['analyser'] or 'the Ondřejov group'}"
        if r["exported"]:
            ref += f", exported {r['exported']}"
        out.append(Claim(
            key=key, prop="period_h", source=SOURCE_ID, kind="lower" if lower else "value", value=value,
            lo=lo, hi=hi, unit="h", quality=quality, ref=ref, note="; ".join(notes) or None,
        ))
        if not lower and r["amplitude"]:
            out.append(Claim(key=key, prop="amplitude_mag", source=SOURCE_ID, value=r["amplitude"], unit="mag",
                             quality=quality, ref=ref))
    return out


def edition() -> str:
    """The latest export date in the table."""
    return max((r["exported"] for r in _rows() if r["exported"]), default="")


def load() -> tuple[list[Claim], list[Coverage]]:
    index = ids.load()
    by_key: dict[str, list[dict]] = {}
    for r in _rows():
        key = resolve_ident(r["ident"], index)
        if key is not None:
            by_key.setdefault(key, []).append(r)
    made, first = edition(), first_observed()
    claims: list[Claim] = []
    coverage: list[Coverage] = []
    for key in nhats.reachable():
        rows = by_key.get(key)
        mine = claims_for(key, rows) if rows else []
        claims += mine
        if mine:
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="found")
        elif rows:
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="absent", reason="observed, no period found")
        elif too_old_for(made, first.get(key)):
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="unchecked", reason=OLDER_THAN_OBJECT)
        else:
            cov = Coverage(key=key, row="spin", source=SOURCE_ID, outcome="absent")
        coverage.append(cov)
    return claims, coverage
