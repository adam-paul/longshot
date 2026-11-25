"""Input paths, the data date and the method version. Nothing here reads the clock."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# The day JPL's two lists were pulled: what "as of" means on every page, and the date of every observing window.
# The other sources carry their own edition and fetch dates (longshot/sources.py), printed with each source.
DATA_DATE = "2026-11-24"
METHOD = "0.1"

SNAPSHOT = DATA / "snapshots" / DATA_DATE
NHATS_JSON = SNAPSHOT / "nhats.json"
SBDB_JSON = SNAPSHOT / "sbdb_neo.json"

RESEARCH = DATA / "research" / "dl" / "coverage-exact"
SSODNET_CARDS = RESEARCH / "cards"
LCDB_DIR = RESEARCH / "lcdb"
SPITZER_CSV = RESEARCH / "spitzer" / "spitzerneos.csv"
PRAVEC_TXT = DATA / "sources" / "pravec" / "newres-2026-11-24.txt"
# SsODNet cards fetched since the research snapshot, and the journal of every attempt (tools/fetch_ssodnet_cards.py).
SSODNET_LIVE_CARDS = DATA / "sources" / "ssodnet" / "cards"
SSODNET_JOURNAL = DATA / "sources" / "ssodnet" / "journal.jsonl"

METHOD_DIR = ROOT / "method" / "v0_1"
KEYS = ROOT / "registry" / "keys.jsonl"
CURATED = ROOT / "registry" / "curated.toml"       # hand-entered single values, each with its citation

BUILD = ROOT / "build"
DIST = ROOT / "dist"
