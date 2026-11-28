"""The record types every part of the pipeline shares. See docs/mvp.md section 4.

Everything is plain data that serialises to JSON with dataclasses.asdict.
Do not rename a field without updating docs/mvp.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from longshot import method as _method

ROWS = ("reach", "tracking", "size", "spin", "surface", "push")
STATES = ("measured", "limit", "prior", "unchecked")
MISSIONS = tuple(_method.load().missions["order"])   # the mission types, as method/v0_1/missions.toml orders them
LADDER = ("found_again", "reached", "workable", "anything_in_it", "brought_back")


@dataclass(frozen=True)
class Source:
    id: str            # "jpl-nhats", "jpl-sbdb", "ssodnet", "pravec", "lcdb", "spitzer", "curated"
    name: str          # as shown on a page
    edition: str       # the date of the upstream data, ISO
    retrieved: str     # the date we fetched it, ISO; the last day where the fetch ran over several
    citation: str
    url: str
    retrieved_from: str = ""   # the first day of a fetch that ran over several, ISO; else empty


@dataclass
class Claim:
    """One statement by one source about one object."""
    key: str
    prop: str                      # "delta_v_kms", "diameter_m", "albedo", "period_h", "taxonomy", "A1", "A2", ...
    source: str                    # Source.id
    kind: str = "value"            # "value" | "upper" | "lower"
    value: float | str | None = None
    lo: float | None = None        # lower bound of the stated range, absolute, same unit
    hi: float | None = None
    unit: str = ""
    quality: str | None = None     # a grade or method tag from upstream (a lightcurve U code, "NEATM", "Computed")
    ref: str | None = None         # the original reference as upstream gives it
    note: str | None = None
    snr: float | None = None       # signal-to-noise of the detection behind the value, where upstream gives one


@dataclass
class Coverage:
    """The act of looking: did this source know anything for this row of this object?"""
    key: str
    row: str                       # one of ROWS
    source: str
    outcome: str                   # "found" | "absent" | "unchecked"
    reason: str = ""


@dataclass
class Fact:
    label: str
    value: float | str | None
    lo: float | None = None
    hi: float | None = None
    unit: str = ""
    kind: str = "value"
    source: str = ""
    ref: str | None = None
    quality: str | None = None
    used: bool = True              # False: on file but not counted (a low grade, a computed value,
                                   # a fit short of detection, a known-bad entry); Row.note says why
    note: str | None = None        # what upstream or the ledger says about this one value, in a few words


@dataclass
class Row:
    state: str                                  # one of STATES
    facts: list[Fact] = field(default_factory=list)
    prior: dict[str, Any] | None = None         # {q05,q25,q50,q75,q95,unit,basis} or {shares:{...},basis}
    unchecked: list[str] = field(default_factory=list)   # source ids not checked for this row
    conflicts: list[str] = field(default_factory=list)   # plain sentences
    note: str | None = None


@dataclass
class ObjectRecord:
    key: str
    designation: str
    name: str | None
    number: int | None
    aliases: list[str]
    populations: list[str]
    data_date: str
    method: str
    rows: dict[str, Row]
    summary: dict[str, Any] = field(default_factory=dict)
    missions: dict[str, Any] = field(default_factory=dict)
    observe: dict[str, Any] | None = None
    value: dict[str, Any] = field(default_factory=dict)
    ladder: list[dict[str, Any]] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    gone: dict[str, Any] | None = None     # {date, text, evidence} for a body that no longer exists (ledger.toml [[gone]])
