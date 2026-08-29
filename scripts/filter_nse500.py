"""
Cross-references NSE Indices' constituent list against EOD2's per-symbol
daily OHLC CSVs, and copies just the matching files (~500 stocks) plus the
5 index-level PR series into a clean output folder.

Usage:
    python3 filter_nse500.py \
        --eod2-daily eod2/src/eod2_data/daily \
        --constituents constituents/ind_nifty500list.csv \
        --outdir nse500_dataset
"""

import argparse
import csv
import shutil
from pathlib import Path

# EOD2 stores index-level files under these names in the same daily/ folder
INDEX_FILES = {
    "nifty50": "nifty 50.csv",
    "nifty_next_50": "nifty next 50.csv",
    "nifty_midcap_150": "nifty midcap 150.csv",
    "nifty_smallcap_250": "nifty smallcap 250.csv",
    "nifty500": "nifty 500.csv",
}


def symbol_to_filename(symbol: str) -> str:
    # EOD2 filenames are the lowercased NSE symbol + .csv (e.g. M&M -> m&m.csv)
    return symbol.strip().lower() + ".csv"


def load_constituent_symbols(constituents_csv: Path) -> list[str]:
    with constituents_csv.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # NSE's constituent CSVs use a "Symbol" column
        symbol_col = next(
            (c for c in reader.fieldnames if c.strip().lower() == "symbol"), None
        )
        if symbol_col is None:
            raise ValueError(
                f"Couldn't find a Symbol column in {constituents_csv}. "
                f"Columns found: {reader.fieldnames}"
            )
        return [row[symbol_col].strip() for row in reader if row[symbol_col].strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eod2-daily", required=True, help="Path to eod2_data/daily")
    parser.add_argument(
        "--constituents", required=True, help="Path to ind_nifty500list.csv"
    )
    parser.add_argument("--outdir", default="nse500_dataset")
    args = parser.parse_args()

    daily_dir = Path(args.eod2_daily)
    out_dir = Path(args.outdir)
    stocks_out = out_dir / "stocks"
    indices_out = out_dir / "indices"
    stocks_out.mkdir(parents=True, exist_ok=True)
    indices_out.mkdir(parents=True, exist_ok=True)

    symbols = load_constituent_symbols(Path(args.constituents))
    print(f"Loaded {len(symbols)} constituent symbols from {args.constituents}")

    matched, missing = 0, []
    for symbol in symbols:
        src = daily_dir / symbol_to_filename(symbol)
        if src.exists():
            shutil.copy2(src, stocks_out / src.name)
            matched += 1
        else:
            missing.append(symbol)

    print(f"Matched {matched}/{len(symbols)} stock CSVs -> {stocks_out}")
    if missing:
        print(
            f"{len(missing)} symbols had no matching file "
            f"(recent listings, renames, or delistings - check manually):"
        )
        print(", ".join(missing[:30]) + (" ..." if len(missing) > 30 else ""))

    for label, filename in INDEX_FILES.items():
        src = daily_dir / filename
        if src.exists():
            shutil.copy2(src, indices_out / filename)
            print(f"Copied index file: {filename}")
        else:
            print(f"[MISSING] index file not found: {filename}")

    print(f"\nDone. Dataset written to {out_dir}/")
    print("Next: point your TRI tracker's refresh routine at this same folder")
    print("to add the 5 TRI series alongside this PR + stock data.")


if __name__ == "__main__":
    main()
