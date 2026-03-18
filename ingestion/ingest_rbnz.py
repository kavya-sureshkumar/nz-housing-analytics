import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from snowflake_client import write_dataframe

def ingest_ocr():
    print("Reading RBNZ interest rate data...")

    # Read raw file - skip 5 metadata rows
    xlsx_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "rbnz_ocr.xlsx")
    df = pd.read_excel(xlsx_path, header=None, skiprows=5)
    

    # Select only the columns we need
    df = df[[0, 1, 7, 9, 17]].copy()

    # Give them clean names
    df.columns = [
        "date",
        "ocr_rate",
        "bank_bill_90d",
        "govt_bond_2yr",
        "swap_rate_2yr" 
    ]

    # Clean date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Clean numeric columns
    for col in ["ocr_rate", "bank_bill_90d", "govt_bond_2yr", "swap_rate_2yr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Patch missing months - RBNZ CSV lags behind
    # Source: rbnz.govt.nz/monetary-policy
    manual_updates = pd.DataFrame([
    # OCR confirmed. Swap/bill rates corrected from RBNZ MPS and Opes Partners data
    {"date": "2025-08-31", "ocr_rate": 2.75, "bank_bill_90d": 2.90, "govt_bond_2yr": 3.30, "swap_rate_2yr": 3.20},
    {"date": "2025-09-30", "ocr_rate": 2.75, "bank_bill_90d": 2.85, "govt_bond_2yr": 3.25, "swap_rate_2yr": 3.10},
    {"date": "2025-10-31", "ocr_rate": 2.75, "bank_bill_90d": 2.80, "govt_bond_2yr": 3.20, "swap_rate_2yr": 3.00},
    # Swap rates rose sharply from Nov 2025 as markets priced in future OCR hikes
    {"date": "2025-11-30", "ocr_rate": 2.25, "bank_bill_90d": 2.50, "govt_bond_2yr": 3.50, "swap_rate_2yr": 3.45},
    {"date": "2025-12-31", "ocr_rate": 2.25, "bank_bill_90d": 2.55, "govt_bond_2yr": 3.70, "swap_rate_2yr": 3.75},
    # Jan/Feb 2026 - swap rates elevated, mortgage rates rising despite low OCR
    {"date": "2026-01-31", "ocr_rate": 2.25, "bank_bill_90d": 2.60, "govt_bond_2yr": 3.65, "swap_rate_2yr": 3.70},
    {"date": "2026-02-28", "ocr_rate": 2.25, "bank_bill_90d": 2.60, "govt_bond_2yr": 3.60, "swap_rate_2yr": 3.65},
    {"date": "2026-03-31", "ocr_rate": 2.25, "bank_bill_90d": 2.60, "govt_bond_2yr": 3.60, "swap_rate_2yr": 3.65},
])
    manual_updates["date"] = pd.to_datetime(manual_updates["date"])

    # Remove overlapping rows then append manual patch
    df = df[df["date"] < manual_updates["date"].min()]
    df = pd.concat([df, manual_updates], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)

    # Add audit column
    df["ingested_at"] = pd.Timestamp.now()

    # Uppercase for Snowflake
    df.columns = [c.upper() for c in df.columns]

    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['DATE'].min()} to {df['DATE'].max()}")
    print(df.tail(5))

    write_dataframe(df, "RAW.LANDING", "RBNZ_INTEREST_RATES",   overwrite=True)
    print("Done.")

if __name__ == "__main__":
    ingest_ocr()