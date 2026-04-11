import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from snowflake_client import write_dataframe

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

def scrape_month(year, month):
    url = f"https://www.barfoot.co.nz/market-reports/{year}/{month}/suburb-report"
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        print(f"  Skipping {year}/{month} - status {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        print(f"  Skipping {year}/{month} - no tables found")
        return None

    all_rows = []
    current_district = None

    # Each section has an h3 heading followed by a table
    for element in soup.find_all(["h3", "table"]):
        if element.name == "h3":
            current_district = element.get_text(strip=True)
        elif element.name == "table" and current_district:
            rows = element.find_all("tr")
            for row in rows[1:]:  # skip header row
                cols = row.find_all("td")
                if len(cols) >= 4:
                    suburb = cols[0].get_text(strip=True)
                    price  = cols[1].get_text(strip=True).replace("$", "").replace(",", "").strip()
                    rent   = cols[2].get_text(strip=True).replace("$", "").replace(",", "").strip()
                    yield_ = cols[3].get_text(strip=True).replace("%", "").strip()

                    # Skip header rows that got picked up
                    if suburb.lower() in ["suburb", "area", ""]:
                        continue

                    all_rows.append({
                        "year":          year,
                        "month":         month,
                        "report_date":   f"{year}-{MONTHS.index(month)+1:02d}-01",
                        "district":      current_district,
                        "suburb":        suburb,
                        "avg_sale_price": pd.to_numeric(price, errors="coerce"),
                        "avg_weekly_rent": pd.to_numeric(rent, errors="coerce"),
                        "gross_yield_pct": pd.to_numeric(yield_, errors="coerce"),
                    })

    print(f"  {year}/{month}: {len(all_rows)} suburbs scraped")
    return pd.DataFrame(all_rows) if all_rows else None


def ingest_barfoot(start_year=2018, end_year=2026):
    print(f"Scraping Barfoot & Thompson suburb reports {start_year}-{end_year}...")
    all_data = []

    for year in range(start_year, end_year + 1):
        for month in MONTHS:
            df = scrape_month(year, month)
            if df is not None and len(df) > 0:
                all_data.append(df)
            time.sleep(1)  # be polite - 1 second between requests

    if not all_data:
        print("No data scraped.")
        return

    final_df = pd.concat(all_data, ignore_index=True)
    final_df["report_date"] = pd.to_datetime(final_df["report_date"])
    final_df["ingested_at"] = pd.Timestamp.now()

    # Uppercase for Snowflake
    final_df.columns = [c.upper() for c in final_df.columns]

    print(f"\nTotal rows: {len(final_df)}")
    print(f"Date range: {final_df['REPORT_DATE'].min()} to {final_df['REPORT_DATE'].max()}")
    print(f"Unique suburbs: {final_df['SUBURB'].nunique()}")
    print(f"\nSample:")
    print(final_df.head(5).to_string())

    write_dataframe(final_df, "RAW.LANDING", "BARFOOT_SUBURB_PRICES",  overwrite=True)
    print("Done.")


if __name__ == "__main__":
    ingest_barfoot(start_year=2018, end_year=2026)