# ingestion/snowflake_client.py
import snowflake.connector
import os
import pandas as pd
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

def write_dataframe(df, schema, table_name, overwrite=False):
    conn = get_connection()
    conn.cursor().execute(f"USE SCHEMA {schema}")

    if overwrite:
        conn.cursor().execute(f"DROP TABLE IF EXISTS {table_name}")

    # Fix datetime columns - convert to string so Snowflake reads them correctly
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    success, nchunks, nrows, _ = write_pandas(
        conn, df, table_name, auto_create_table=True
    )
    print(f"Loaded {nrows} rows into {schema}.{table_name}")
    conn.close()