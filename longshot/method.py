"""The method constants: method/v0_1/*.toml loaded into plain dicts.

    m = method.load()
    m.priors["reflectivity"]["pv"]      # the tables as the files give them
    m.version, m.n_draws

A missing key fails at load, naming the file and the key. Nothing here changes
a number: the files are proposals until Adam freezes them (AGENTS.md).
"""
from __future__ import annotations

import dataclasses
import functools
import tomllib
from pathlib import Path

from longshot import config

FILES = ("priors", "missions", "observe", "value", "ladder", "ledger")


class MethodError(KeyError):
    """A method file lacks a key the code needs, or two files disagree."""

    def __str__(self) -> str:          # KeyError would print the repr
        return str(self.args[0]) if self.args else ""


@dataclasses.dataclass(frozen=True, eq=False)       # compared and hashed by identity: load() caches one per folder
class Method:
    version: str
    n_draws: int               # joint draws per object: value.toml [exports].min_draws
    priors: dict
    missions: dict
    observe: dict
    value: dict
    ladder: dict
    ledger: dict
    path: str


def need(table, *path, where: str = "method"):
    """table[path[0]][path[1]]..., or MethodError naming the first key that is missing."""
    cur = table
    for i, k in enumerate(path):
        try:
            cur = cur[k]
        except (KeyError, IndexError, TypeError):
            raise MethodError(f"{where}: missing {'.'.join(str(p) for p in path[:i + 1])}") from None
    return cur


# Every key the code reads, by file. Keys under a band, a class or a gate are checked in _check.
REQUIRED = {
    "priors": (
        ("method",), ("bands", "ids"), ("bands", "edges"),
        ("size", "coefficient_m"), ("size", "extrapolated_fainter_than_h"), ("size", "n_measured_at_or_fainter"),
        ("h_uncertainty", "default_sigma"),
        ("reflectivity", "p"), ("reflectivity", "pv"), ("reflectivity", "n_objects"),
        ("reflectivity", "by_class"), ("reflectivity", "link", "edges"),
        ("spin", "ids"), ("spin", "thresholds_h"), ("spin", "bands"),
        ("class", "ids"), ("class", "bands"), ("class", "label_error", "colour"), ("class", "label_error", "spectrum"),
        ("density", "X", "split_edges_pv"), ("density", "X", "metal_rich_share_of_mid"),
        ("density", "X", "dark"), ("density", "X", "mid_silicate"), ("density", "X", "mid_metal"),
        ("density", "X", "bright"),
    ),
    "missions": (
        ("method",), ("order",), ("rules", "period", "min_grade"), ("rules", "size", "min_implied_reflectivity"),
        ("rules", "size", "max_implied_reflectivity"), ("rules", "decide", "sigma"),
        ("rules", "decide", "no_range_factor"),
    ),
    "observe": (
        ("method",), ("observations",), ("needs", "lightcurve", "tiers"), ("needs", "lightcurve", "fainter"),
        ("needs", "size", "tiers"), ("needs", "size", "fainter"),
        ("needs", "not_pointable", "survey_only"), ("needs", "not_pointable", "no_window"),
    ),
    "value": (
        ("meta", "method"), ("scenarios", "order"), ("counted", "priced"),
        ("bands", "dark_below"), ("bands", "bright_from"), ("kinds",), ("material",), ("grade_table",), ("mix",),
        ("prices", "usd_per_kg"), ("market", "cap_kg"), ("size", "diameter_factor"),
        ("exports", "min_draws"), ("exports", "min_draws_for_a_range"), ("exports", "basis", "text"),
        ("statement",),
    ),
    "ladder": (
        ("meta", "method"), ("meta", "order"),
        ("thresholds", "sampled_min_m"), ("thresholds", "sampled_min_period_h"), ("thresholds", "touched_min_m"),
        ("thresholds", "small_m"), ("thresholds", "very_fast_period_min"),
        ("spin_limit", "light_rock_limit_h"), ("spin_limit", "dense_rock_limit_h"),
        ("fact",), ("rung", "found_again"), ("rung", "reached"), ("rung", "workable"),
        ("rung", "anything_in_it"), ("rung", "brought_back"),
    ),
    "ledger": (
        ("method",), ("period", "min_grade"), ("period", "tolerance"), ("push", "detection_sigma"),
        ("push", "counts"), ("spitzer", "min_snr"), ("reflectivity", "max"),
        ("fixed_tables", "sources"), ("fixed_tables", "reason"), ("closed_tables", "sources"), ("closed_tables", "reason"),
        ("known_bad",), ("gone",),
    ),
}

STATEMENT_IDS = ("metal_none", "metal_none_measured", "metal_under", "metal_over", "iron_rich", "metal_cap",
                 "water_none", "water_some", "water_market", "sample_water", "sample_water_at_most",
                 "sample_no_analysis")


def _check(tables: dict) -> None:
    for name, paths in REQUIRED.items():
        for path in paths:
            need(tables[name], *path, where=f"{name}.toml")

    pri, mis, obs, val, lad, led = (tables[n] for n in FILES)
    versions = {
        "priors.toml": pri["method"], "missions.toml": mis["method"], "observe.toml": obs["method"],
        "value.toml": val["meta"]["method"], "ladder.toml": lad["meta"]["method"], "ledger.toml": led["method"],
    }
    wrong = {f: v for f, v in versions.items() if v != config.METHOD}
    if wrong:
        raise MethodError(f"method version is {config.METHOD} in longshot/config.py but {wrong}")

    bands, classes, spins = pri["bands"]["ids"], pri["class"]["ids"], pri["spin"]["ids"]
    if len(pri["bands"]["edges"]) != len(bands) - 1:
        raise MethodError("priors.toml: bands.edges must have one value fewer than bands.ids")
    n_p = len(pri["reflectivity"]["p"])
    if len(pri["reflectivity"]["pv"]) != n_p:
        raise MethodError("priors.toml: reflectivity.pv and reflectivity.p differ in length")
    n_bins = len(pri["reflectivity"]["link"]["edges"]) + 1
    for c in classes:
        if len(need(pri, "reflectivity", "by_class", c, "pv", where="priors.toml")) != n_p:
            raise MethodError(f"priors.toml: reflectivity.by_class.{c}.pv and reflectivity.p differ in length")
        if len(need(pri, "reflectivity", "link", c, where="priors.toml")) != n_bins:
            raise MethodError(f"priors.toml: reflectivity.link.{c} must have {n_bins} bins")
        if c != "X":
            need(pri, "density", c, "lo", where="priors.toml")
            need(pri, "density", c, "hi", where="priors.toml")
    for part in ("dark", "mid_silicate", "mid_metal", "bright"):
        need(pri, "density", "X", part, "lo", where="priors.toml")
        need(pri, "density", "X", part, "hi", where="priors.toml")
    for b in bands:
        last = 1.0
        for s in spins:                 # under 2.2 h, under 1 h, under 10 min: each a subset of the one before
            for end in ("low", "central", "high"):
                need(pri, "spin", "bands", b, s, end, where="priors.toml")
            central = pri["spin"]["bands"][b][s]["central"]
            if not 0.0 <= central <= last:
                raise MethodError(f"priors.toml: spin.bands.{b}.{s}.central is not a share inside the one before it")
            last = central
        for end in ("central", "low", "high", "joint_weight"):
            for c in classes:
                need(pri, "class", "bands", b, end, c, where="priors.toml")
        need(pri, "class", "bands", b, "n", where="priors.toml")
    if len(pri["spin"]["thresholds_h"]) != len(spins):
        raise MethodError("priors.toml: spin.thresholds_h and spin.ids differ in length")

    for mission in mis["order"]:
        need(mis, mission, "label", where="missions.toml")
        for i, g in enumerate(need(mis, mission, "gates", where="missions.toml")):
            for k in ("id", "label", "quantity", "op", "preset"):
                need(g, k, where=f"missions.toml {mission}.gates[{i}]")
            if g["op"] not in ("<=", ">="):
                raise MethodError(f"missions.toml {mission}.gates[{i}]: op {g['op']!r} is not <= or >=")
    for i, o in enumerate(obs["observations"]):
        for k in ("id", "label", "resolves"):
            need(o, k, where=f"observe.toml observations[{i}]")
        need(obs, "needs", o["id"], "tiers", where="observe.toml")

    have = {s.get("id") for s in val["statement"]}
    missing = [s for s in STATEMENT_IDS if s not in have]
    if missing:
        raise MethodError(f"value.toml: no [[statement]] with id {', '.join(missing)}")
    if list(val["scenarios"]["order"]) != ["low", "central", "high"]:
        raise MethodError("value.toml: scenarios.order must be low, central, high")
    for el in val["counted"]["priced"]:
        need(val, "prices", "usd_per_kg", el, where="value.toml")
        need(val, "market", "cap_kg", el, where="value.toml")
    for c in classes:
        need(val, "kinds", c, where="value.toml")
    for rung in lad["meta"]["order"]:
        need(lad, "rung", rung, where="ladder.toml")
    for i, bad in enumerate(led["known_bad"]):
        for k in ("designation", "prop", "value", "why", "source"):
            need(bad, k, where=f"ledger.toml known_bad[{i}]")
    for i, g in enumerate(led["gone"]):
        for k in ("designation", "date", "text", "source"):
            need(g, k, where=f"ledger.toml gone[{i}]")


@functools.lru_cache(maxsize=4)
def _load(path: str) -> Method:
    tables = {}
    for name in FILES:
        file = Path(path) / f"{name}.toml"
        try:
            with open(file, "rb") as fh:
                tables[name] = tomllib.load(fh)
        except FileNotFoundError:
            raise MethodError(f"method file missing: {file}") from None
    _check(tables)
    return Method(version=tables["priors"]["method"], n_draws=int(tables["value"]["exports"]["min_draws"]),
                  path=path, **tables)


def load(method_dir: str | Path | None = None) -> Method:
    """The method files, checked. Cached: the same object for the same folder."""
    return _load(str(Path(method_dir or config.METHOD_DIR).resolve()))
