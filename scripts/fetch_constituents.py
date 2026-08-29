"""
Downloads official NSE Indices constituent lists for:
  Nifty 50, Nifty Next 50, Nifty Midcap 150, Nifty Smallcap 250, Nifty 500

Source: niftyindices.com (same domain your TRI tracker already pulls from).
NSE reshuffles index membership semi-annually (typically effective late
March and late September) - re-run this after each reshuffle to stay current.

Usage:
    python3 fetch_constituents.py --outdir constituents
"""

import argparse
import csv
import io
from pathlib import Path
from urllib.request import Request, urlopen

# NSE Indices publishes constituent lists at predictable URLs under
# niftyindices.com/IndexConstituent/. Filenames occasionally change when NSE
# updates their site - if a download fails, check
# https://www.niftyindices.com/indices/equity/broad-based-indices for the
# current filename and update INDEX_FILES below.
INDEX_FILES = {
    "nifty50": "ind_nifty50list.csv",
    "nifty_next_50": "ind_niftynext50list.csv",
    "nifty_midcap_150": "ind_niftymidcap150list.csv",
    "nifty_smallcap_250": "ind_niftysmallcap250list.csv",
    "nifty500": "ind_nifty500list.csv",
}

BASE_URL = "https://niftyindices.com/IndexConstituent/"

HEADERS = {
    # niftyindices.com blocks requests without a browser-like User-Agent
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def download(url: str) -> bytes:
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="constituents")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for label, filename in INDEX_FILES.items():
        url = BASE_URL + filename
        try:
            data = download(url)
        except Exception as e:
            print(f"[FAILED] {label} ({url}): {e}")
            continue

        out_path = outdir / filename
        out_path.write_bytes(data)

        # sanity check: count rows so you can eyeball expected sizes
        # (Nifty 50 ~50 rows, Nifty 500 ~500 rows, etc.)
        try:
            text = data.decode("utf-8-sig")
            reader = csv.reader(io.StringIO(text))
            row_count = sum(1 for _ in reader) - 1  # minus header
            print(f"[OK] {label}: {row_count} constituents -> {out_path}")
        except Exception:
            print(f"[OK] {label} -> {out_path} (saved, row count unavailable)")


if __name__ == "__main__":
    main()
