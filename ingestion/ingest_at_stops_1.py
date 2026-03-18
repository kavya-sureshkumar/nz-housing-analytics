import requests
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from snowflake_client import write_dataframe

AT_STOPS_URL = "https://api.at.govt.nz/gtfs/v3/stops"


def fetch_stops() -> list[dict]:
    at_api_key = os.getenv("AT_API_KEY")
    if not at_api_key:
        raise EnvironmentError("AT_API_KEY not set in .env")

    headers = {"Ocp-Apim-Subscription-Key": at_api_key}
    print(f"Fetching stops from AT GTFS v3 API ...")

    response = requests.get(AT_STOPS_URL, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    records = data["data"]
    print(f"Received {len(records)} raw stop entities")
    return records
    

def ingest_at_stops():
    print("Fetching Auckland Transport transit stops ...")
    records = fetch_stops()
    rows = []
    
    for entity in records:
        row = entity["attributes"]
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"Raw fetch: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")

    df['ingested_at'] = pd.Timestamp.now()
    df.columns = [c.upper() for c in df.columns]

    print(f"\nSample data:")
    print(df.head(5).to_string())

    df = df.reset_index(drop=True)
    write_dataframe(df, "RAW.AT", "TRANSIT_STOPS", overwrite=True)
    print("Done.")


if __name__ == "__main__":
    ingest_at_stops()
