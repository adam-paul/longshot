"""One-off: fetch SsODNet ssoCards for reachable asteroids that have none on disk.

Sequential, one request a second, resumable. Every attempt appends a line to
data/sources/ssodnet/journal.jsonl with an outcome:

    card      a card was saved
    unknown   SsODNet answered 404: it does not know the object. Not asked again.
    failed    anything else: a network error, another HTTP status, or a 200 whose
              body is not a card. Asked again on the next run.

A card is written to a temporary name in the cards folder and renamed into
place, so a build never reads half a file; the journal line is written after
the rename, so every card the journal lists is on disk.

This is the one script that opens a network connection. It is run by hand,
never by the build.

Usage: uv run python tools/fetch_ssodnet_cards.py [max_requests]
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NHATS = os.path.join(ROOT, "data/snapshots/2026-11-24/nhats.json")
OLD = os.path.join(ROOT, "data/research/dl/coverage-exact/cards")
OUT = os.path.join(ROOT, "data/sources/ssodnet/cards")
JOURNAL = os.path.join(ROOT, "data/sources/ssodnet/journal.jsonl")
API = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/"
DONE = ("card", "unknown")          # the outcomes that are not asked again


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def unwrap(doc):
    """A card, whether bare or wrapped as {"<id>": {...}}; None when the document is not a card."""
    if isinstance(doc, dict) and "parameters" not in doc and len(doc) == 1:
        doc = next(iter(doc.values()))
    return doc if isinstance(doc, dict) and isinstance(doc.get("parameters"), dict) else None


def card_ids(path):
    try:
        with open(path, "rb") as fh:
            c = unwrap(json.load(fh))
    except (OSError, ValueError):
        return set()
    if c is None:
        return set()
    ids = {norm(c.get("name", "")), norm(c.get("id", ""))}
    if c.get("number"):
        ids.add(str(c["number"]))
    for a in c.get("aliases") or []:
        ids.add(norm(a))
    return ids - {""}


def card_name(des):
    """The file a designation's card is saved to. longshot/ingest/ssodnet.py card_file_name is the same rule."""
    return re.sub(r"[^A-Za-z0-9_]", "_", des.replace(" ", "_")) + ".json"


def save_card(folder, des, body):
    """Write the whole card under a temporary name, then rename it into place."""
    final = os.path.join(folder, card_name(des))
    tmp = os.path.join(folder, f".{card_name(des)}.tmp{os.getpid()}")
    with open(tmp, "wb") as fh:
        fh.write(body)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, final)
    return final


def last_outcomes(journal_path):
    """{designation: outcome of its latest journal line}."""
    out = {}
    if os.path.exists(journal_path):
        with open(journal_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                    out[rec["des"]] = rec.get("outcome")
                except (ValueError, KeyError, TypeError):
                    pass                    # a line cut short by an interrupted run
    return out


def todo_list(designations, have, outcomes):
    """Designations still to ask for: no card on disk, and not settled by an earlier answer. A failure is retried."""
    return [d for d in designations if norm(d) not in have and outcomes.get(d) not in DONE]


def fetch(des, opener=urllib.request.urlopen):
    """One request. Returns (journal record, body or None)."""
    url = API + urllib.parse.quote(des.replace(" ", "_"))
    rec = {"des": des, "url": url,
           "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    try:
        with opener(urllib.request.Request(url, headers={"User-Agent": "curl/8"}), timeout=30) as r:
            body = r.read()
            rec["status"] = r.status
        try:
            card = unwrap(json.loads(body))
        except ValueError:
            card = None
        if card is not None:
            rec["outcome"] = "card"
            return rec, body
        # a 200 that is not a card is not "SsODNet does not know it": ask again later
        rec["outcome"] = "failed"
        rec["error"] = "the answer was not a card"
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        rec["outcome"] = "unknown" if e.code == 404 else "failed"
    except Exception as e:                                   # a timeout, a reset connection, a DNS failure
        rec["outcome"] = "failed"
        rec["error"] = repr(e)[:200]
    return rec, None


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    have = set()
    for folder in (OLD, OUT):
        if os.path.isdir(folder):
            for fn in os.listdir(folder):
                if fn.endswith(".json") and not fn.startswith("."):
                    have |= card_ids(os.path.join(folder, fn))
    with open(NHATS, "rb") as fh:
        designations = [r["des"] for r in json.load(fh)["data"]]
    todo = todo_list(designations, have, last_outcomes(JOURNAL))
    limit = int(argv[0]) if argv else len(todo)
    print("cards known", len(have), "to fetch", len(todo), "limit", limit, flush=True)
    ok = absent = err = 0
    for i, des in enumerate(todo[:limit]):
        rec, body = fetch(des)
        if body is not None:
            save_card(OUT, des, body)
            ok += 1
        elif rec["outcome"] == "unknown":
            absent += 1
        else:
            err += 1
        with open(JOURNAL, "a", encoding="utf-8") as j:
            j.write(json.dumps(rec) + "\n")
        if (i + 1) % 200 == 0:
            print(i + 1, "card", ok, "unknown", absent, "failed", err, flush=True)
        if err >= 25 and ok + absent == 0:
            print("too many failures, stopping", flush=True)
            break
        time.sleep(1.0)
    print("done card", ok, "unknown", absent, "failed", err, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
