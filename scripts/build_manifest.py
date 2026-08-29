"""
Builds manifest.json listing all available stock symbols and index files,
so the frontend knows what it can offer in its picker without having to
list the data/ folder itself (browsers can't list directory contents of a
static site).

Usage:
    python3 build_manifest.py --data-dir data --outfile data/manifest.json
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--outfile", default="data/manifest.json")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    stocks_dir = data_dir / "stocks"
    indices_dir = data_dir / "indices"

    stocks = sorted(p.stem.upper() for p in stocks_dir.glob("*.csv"))
    indices = sorted(p.stem for p in indices_dir.glob("*.csv"))

    manifest = {
        "stocks": stocks,
        "indices": indices,
        "stock_count": len(stocks),
    }

    Path(args.outfile).write_text(json.dumps(manifest, indent=2))
    print(f"Wrote manifest: {len(stocks)} stocks, {len(indices)} indices -> {args.outfile}")


if __name__ == "__main__":
    main()
