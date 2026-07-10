"""
Backfills boxscore archives for a range of dates.

Usage:
    python backfill.py 2026-06-26 2026-07-09
"""

import sys
from datetime import date, datetime, timedelta

from archive import archive_day


def daterange(start: date, end: date):
    for n in range((end - start).days + 1):
        yield start + timedelta(days=n)


def backfill(start_str: str, end_str: str, out_root: str = "boxscores"):
    start = datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_str, "%Y-%m-%d").date()

    if start > end:
        raise ValueError(f"start date {start} is after end date {end}")

    results = []
    for d in daterange(start, end):
        d_str = d.isoformat()
        print(f"Archiving {d_str}...")
        try:
            path = archive_day(d_str, out_root=out_root)
            results.append((d_str, "ok", path))
        except Exception as e:
            print(f"  ! failed for {d_str}: {e}")
            results.append((d_str, "failed", str(e)))

    print("\n--- Backfill summary ---")
    for d_str, status, info in results:
        print(f"{d_str}: {status} ({info})")

    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python backfill.py START_DATE END_DATE")
        sys.exit(1)
    backfill(sys.argv[1], sys.argv[2])
