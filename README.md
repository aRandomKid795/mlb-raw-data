# PrizePicks Tracker

Archives daily MLB boxscore stats and lets you grade PrizePicks slips against
them. Built so Claude (or anything else) can pull data straight from the raw
GitHub URLs — no re-uploading files each time.

## Structure

```
boxscores/YYYY-MM-DD/mlb.json   # archived player stats for that day
slips/YYYY-MM-DD/*.json          # your PrizePicks slips
archive.py                       # pulls boxscores from MLB's public API
compare.py                       # grades a slip against a boxscore file
grader/normalize.py              # name normalization so "José Ramírez" == "jose ramirez"
```

## Setup

1. Create a new **public** GitHub repo (e.g. `prizepicks-tracker`).
2. Push these files to it:
   ```bash
   cd prizepicks-tracker
   git init
   git add .
   git commit -m "Initial setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/prizepicks-tracker.git
   git push -u origin main
   ```
3. GitHub Actions will now run `archive.py` automatically every day at 9am UTC
   and commit the results to `boxscores/`. You can also trigger it manually
   from the "Actions" tab (Run workflow).

## Adding a slip

Drop a new JSON file into `slips/YYYY-MM-DD/`, following the shape in
`slips/2026-07-09/example_slip.json`:

```json
{
  "slip_id": "example_001",
  "date": "2026-07-09",
  "entry_fee": 5,
  "payout_type": "power",
  "picks": [
    {"player": "Jose Ramirez", "stat": "total_bases", "line": 1.5, "side": "over"}
  ],
  "result": "pending"
}
```

Supported `stat` values: `hits`, `home_runs`, `runs`, `rbis`, `total_bases`,
`hits_runs_rbis`, `stolen_bases`, `walks`. Add more mappings in
`compare.py` -> `STAT_MAP` as needed.

Push the slip file, and it's ready to grade — no upload needed.

## Grading a slip locally

```bash
pip install -r requirements.txt
python compare.py slips/2026-07-09/example_slip.json boxscores/2026-07-09/mlb.json
```

## Getting Claude to grade it for you

Once the repo is public, just tell Claude the repo name/URL and which slip to
check. Claude can fetch the raw files directly:

```
https://raw.githubusercontent.com/YOUR_USERNAME/prizepicks-tracker/main/slips/2026-07-09/example_slip.json
https://raw.githubusercontent.com/YOUR_USERNAME/prizepicks-tracker/main/boxscores/2026-07-09/mlb.json
```

No re-uploading — just point Claude at the repo once per conversation.

## Backfilling historical dates

To seed the repo with past dates:

```bash
for d in 2026-07-01 2026-07-02 2026-07-03; do
  TARGET_DATE=$d python archive.py
done
```
