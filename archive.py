"""
Pulls MLB boxscore stats for a given date and writes them to
boxscores/YYYY-MM-DD/mlb.json

Usage:
    python archive.py                  # defaults to today (UTC)
    TARGET_DATE=2026-07-08 python archive.py
"""

import json
import os
import time
from datetime import date, timezone, datetime

import requests

from grader.normalize import normalize

SCHEDULE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
BOXSCORE = "https://statsapi.mlb.com/api/v1/game/{pk}/boxscore"


def get_game_pks(target_date: str):
    r = requests.get(SCHEDULE.format(date=target_date), timeout=20)
    r.raise_for_status()
    data = r.json()
    return [g["gamePk"] for day in data.get("dates", []) for g in day.get("games", [])]


def build_lookup(target_date: str, sleep_between: float = 0.3):
    pks = get_game_pks(target_date)
    lookup = {}

    for pk in pks:
        try:
            r = requests.get(BOXSCORE.format(pk=pk), timeout=20)
            r.raise_for_status()
            box = r.json()
        except requests.RequestException as e:
            print(f"  ! failed to fetch boxscore for game {pk}: {e}")
            continue

        for side in ("home", "away"):
            team = box.get("teams", {}).get(side, {})
            for player in team.get("players", {}).values():
                batting = player.get("stats", {}).get("batting", {})
                if not batting:
                    continue
                name = player["person"]["fullName"]
                lookup[normalize(name)] = {
                    "display_name": name,
                    "ab": batting.get("atBats", 0),
                    "pa": batting.get("plateAppearances", 0),
                    "h": batting.get("hits", 0),
                    "2b": batting.get("doubles", 0),
                    "3b": batting.get("triples", 0),
                    "hr": batting.get("homeRuns", 0),
                    "r": batting.get("runs", 0),
                    "rbi": batting.get("rbi", 0),
                    "bb": batting.get("baseOnBalls", 0),
                    "hbp": batting.get("hitByPitch", 0),
                    "sb": batting.get("stolenBases", 0),
                }

        if sleep_between:
            time.sleep(sleep_between)

    return lookup


def archive_day(target_date: str, out_root: str = "boxscores"):
    lookup = build_lookup(target_date)
    day_dir = os.path.join(out_root, target_date)
    os.makedirs(day_dir, exist_ok=True)

    out_path = os.path.join(day_dir, "mlb.json")
    with open(out_path, "w") as f:
        json.dump(lookup, f, indent=2, sort_keys=True)

    print(f"Wrote {len(lookup)} players to {out_path}")
    return out_path


if __name__ == "__main__":
    target = os.environ.get("TARGET_DATE") or datetime.now(timezone.utc).date().isoformat()
    print(f"Archiving MLB boxscores for {target}...")
    archive_day(target)
