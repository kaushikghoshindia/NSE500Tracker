"""
Backfills Nifty index price-return (PR) history from niftyindices.com's
public historical-data endpoint, and merges it in front of whatever EOD2
already provides (which typically only starts around 2012 for the
index-level files, even though the indices themselves launched in the
mid-to-late 1990s).

Safe to re-run: only adds dates that aren't already present, never
overwrites existing rows.

Usage:
    python3 backfill_index_history.py --data-dir data
"""

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

# Filename in data/indices -> canonical name niftyindices.com expects
INDEX_MAP = {
    "nifty 50.csv": "NIFTY 50",
    "nifty next 50.csv": "NIFTY NEXT 50",
    "nifty midcap 150.csv": "NIFTY MIDCAP 150",
    "nifty smallcap 250.csv": "NIFTY SMALLCAP 250",
    "nifty 500.csv": "NIFTY 500",
}

URL = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.niftyindices.com/reports/historical-data",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}

DATE_FORMATS = ["%d %b %Y", "%d-%b-%Y", "%Y-%m-%d", "%d %B %Y"]


def parse_date(value: str):
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(value, errors="coerce")


def find_key(record: dict, contains: str):
    for k in record.keys():
        if contains in k.lower():
            return k
    return None


def fetch_index_pr(name: str, start: str, end: str) -> pd.DataFrame:
    payload = {
        "cinfo": f"{{'name':'{name}','startDate':'{start}','endDate':'{end}','indexName':'{name}'}}"
    }
    req = Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=HEADERS,
        method="POST",
    )
    with urlopen(req, timeout=60) as resp:
        outer = json.loads(resp.read().decode("utf-8"))
    records = json.loads(outer["d"])
    if not records:
        return pd.DataFrame()

    sample = records[0]
    date_key = find_key(sample, "date")
    open_key = find_key(sample, "open")
    high_key = find_key(sample, "high")
    low_key = find_key(sample, "low")
    close_key = find_key(sample, "close")

    if not all([date_key, open_key, high_key, low_key, close_key]):
        print(f"  [WARN] Unexpected response shape for {name}: keys={list(sample.keys())}")
        return pd.DataFrame()

    rows = [
        {
            "Date": parse_date(r[date_key]),
            "Open": r[open_key],
            "High": r[high_key],
            "Low": r[low_key],
            "Close": r[close_key],
        }
        for r in records
    ]
    df = pd.DataFrame(rows).dropna(subset=["Date"])
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    return df


def merge_backfill(existing_path: Path, backfill_df: pd.DataFrame):
    if backfill_df.empty:
        return None

    if existing_path.exists():
        existing = pd.read_csv(existing_path)
    else:
        existing = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close"])

    existing_dates = set(existing["Date"].astype(str))
    new_rows = backfill_df[~backfill_df["Date"].astype(str).isin(existing_dates)]

    if new_rows.empty:
        return None

    combined = pd.concat([new_rows, existing], ignore_index=True, sort=False)
    combined["Date"] = pd.to_datetime(combined["Date"])
    combined = combined.sort_values("Date")
    combined["Date"] = combined["Date"].dt.strftime("%Y-%m-%d")
    return combined


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument(
        "--start", default="01-Jan-1994", help="Earliest date to request, DD-MMM-YYYY"
    )
    args = parser.parse_args()

    indices_dir = Path(args.data_dir) / "indices"
    indices_dir.mkdir(parents=True, exist_ok=True)
    end = date.today().strftime("%d-%b-%Y")

    for filename, index_name in INDEX_MAP.items():
        target = indices_dir / filename
        print(f"Backfilling {index_name} ...")
        try:
            backfill_df = fetch_index_pr(index_name, args.start, end)
        except Exception as e:
            print(f"  [SKIPPED] Could not fetch backfill for {index_name}: {e}")
            continue

        if backfill_df.empty:
            print(f"  [SKIPPED] No data returned for {index_name}")
            continue

        combined = merge_backfill(target, backfill_df)
        if combined is None:
            print(f"  No new earlier rows for {index_name} (already up to date)")
            continue

        combined.to_csv(target, index=False)
        print(
            f"  Extended {filename}: now {len(combined)} rows, "
            f"from {combined['Date'].min()} to {combined['Date'].max()}"
        )


if __name__ == "__main__":
    main()
