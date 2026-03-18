import requests
import urllib.parse
import time
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from snowflake_client import write_dataframe

API_BASE    = "https://catalogue.data.govt.nz/api/3/action/datastore_search_sql"
RESOURCE_ID = "4b292323-9fcc-41f8-814b-3c7b19cf14b3"

KEEP_COLS = [
    'School_Id', 'Org_Name', 'Org_Type', 'Authority', 'CoEd_Status',
    'Add1_Suburb', 'Add1_City', 'Territorial_Authority', 'Regional_Council',
    'Statistical_Area_2_Code', 'Statistical_Area_2_Description',
    'Latitude', 'Longitude', 'EQi_Index', 'Total', 'Status', 'DateSchoolOpened'
]

def fetch_all_schools() -> pd.DataFrame:
    sql = f'SELECT * FROM "{RESOURCE_ID}"'
    url = f"{API_BASE}?sql={urllib.parse.quote(sql)}"
    response = requests.get(url, timeout=30)
    data = response.json()
    return pd.DataFrame(data["result"]["records"])


def ingest_schools():
    print("Fetching MoE Schools Directory from data.govt.nz ...")
    df = fetch_all_schools()
    df = df[KEEP_COLS]
    print(f"Raw fetch: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")

    df['ingested_at'] = pd.Timestamp.now()
    df.columns = [c.upper() for c in df.columns]

    print(f"\nSample data:")
    print(df.head(5).to_string())

    df = df.reset_index(drop=True)
    write_dataframe(df, "RAW.MOE", "SCHOOLS", overwrite=True)
    print("Done.")


if __name__ == "__main__":
    ingest_schools()
