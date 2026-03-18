import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from snowflake_client import write_dataframe

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "linz_supermarkets.csv")



def ingest_supermarkets():
    print("Reading LINZ supermarkets file ...")
    df = pd.read_csv(CSV_PATH)
    print(df['Territorial Authority'].value_counts().to_string())
    df = df[df['Territorial Authority'] == 'Auckland'] 
    print(f"Raw file: {len(df)} rows, {len(df.columns)} columns")

    # Rename columns to be Snowflake-friendly
    df = df.rename(columns={
        "Town - City": "Town_City",
        "Shape__Area": "Shape_Area",
        "Shape__Length": "Shape_Length"
    })
    

    df['ingested_at'] = pd.Timestamp.now()
    df.columns = [c.upper() for c in df.columns]

    print(f"\nSample data:")
    print(df.head(5).to_string())
    print(f"\nRows by city (top 10):")
    print(df['TOWN_CITY'].value_counts().head(10).to_string())

    df = df.reset_index(drop=True)
    write_dataframe(df, "RAW.LANDING", "LINZ_SUPERMARKETS", overwrite=True)
    print("Done.")


if __name__ == "__main__":
    ingest_supermarkets()