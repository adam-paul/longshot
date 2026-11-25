"""Write a checksum beside each fixed-width text table the ledger reads.

A table cut short at a line boundary still parses, and the objects on the lost lines would read as "the table
has no value". With `<file>.sha256` beside the file, longshot.ingest reads the table only if its bytes match.
Run once after a table is fetched and looked at; never by the build.

Usage: uv run python -I tools/checksum_tables.py           write the checksums
       uv run python -I tools/checksum_tables.py --check   exit 1 if a table has none or does not match
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from longshot import config  # noqa: E402

TABLES = (config.PRAVEC_TXT, config.LCDB_DIR / "x" / "lc_summary_pub.txt")


def main(argv):
    check = "--check" in argv
    bad = 0
    for path in TABLES:
        side = path.with_name(path.name + ".sha256")
        if not path.exists():
            print(f"missing  {path}")
            bad += 1
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if check:
            have = side.read_text(encoding="utf-8").split()[0] if side.exists() and side.read_text().split() else None
            ok = have == digest
            print(f"{'ok      ' if ok else 'MISMATCH' if have else 'none    '} {path}")
            bad += not ok
        else:
            side.write_text(f"{digest}  {path.name}\n", encoding="utf-8")
            print(f"wrote    {side}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
