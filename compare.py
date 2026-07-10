"""
Grades a slip against an archived boxscore file.

Usage:
    python compare.py slips/2026-07-09/example_slip.json boxscores/2026-07-09/mlb.json
"""

import json
import sys

from grader.normalize import normalize

# Maps a slip's "stat" field to the boxscore key(s) that make it up.
# Some PrizePicks props are combos (e.g. "hits+runs+rbis" -> H+R+RBI).
STAT_MAP = {
    "hits": ["h"],
    "home_runs": ["hr"],
    "runs": ["r"],
    "rbis": ["rbi"],
    "total_bases": None,  # handled specially below
    "hits_runs_rbis": ["h", "r", "rbi"],
    "stolen_bases": ["sb"],
    "walks": ["bb"],
}


def total_bases(stats: dict) -> int:
    singles = stats["h"] - stats["2b"] - stats["3b"] - stats["hr"]
    return singles + 2 * stats["2b"] + 3 * stats["3b"] + 4 * stats["hr"]


def grade_pick(pick: dict, boxscore: dict):
    name_key = normalize(pick["player"])
    stats = boxscore.get(name_key)

    if stats is None:
        return {**pick, "actual": None, "result": "no_data"}

    stat = pick["stat"]
    if stat == "total_bases":
        actual = total_bases(stats)
    else:
        keys = STAT_MAP.get(stat)
        if keys is None:
            return {**pick, "actual": None, "result": f"unknown_stat:{stat}"}
        actual = sum(stats.get(k, 0) for k in keys)

    line = pick["line"]
    side = pick["side"]  # "over" or "under"

    if actual == line:
        result = "push"
    elif (actual > line and side == "over") or (actual < line and side == "under"):
        result = "hit"
    else:
        result = "miss"

    return {**pick, "actual": actual, "result": result}


def grade_slip(slip: dict, boxscore: dict):
    graded_picks = [grade_pick(p, boxscore) for p in slip["picks"]]
    all_hit = all(p["result"] == "hit" for p in graded_picks)
    any_miss = any(p["result"] == "miss" for p in graded_picks)
    any_no_data = any(p["result"] == "no_data" for p in graded_picks)

    if any_no_data:
        overall = "pending_data"
    elif all_hit:
        overall = "win"
    elif any_miss:
        overall = "loss"
    else:
        overall = "push_or_partial"

    return {
        "slip_id": slip.get("slip_id"),
        "date": slip.get("date"),
        "overall": overall,
        "picks": graded_picks,
    }


if __name__ == "__main__":
    slip_path, boxscore_path = sys.argv[1], sys.argv[2]

    with open(slip_path) as f:
        slip = json.load(f)
    with open(boxscore_path) as f:
        boxscore = json.load(f)

    result = grade_slip(slip, boxscore)
    print(json.dumps(result, indent=2))
