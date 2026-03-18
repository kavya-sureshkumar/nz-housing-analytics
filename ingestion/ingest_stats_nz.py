import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from snowflake_client import write_dataframe

col_names = [
    'section_title', 'section_type', 'classification_label', 'code',
    'descriptor', 'period', 'duration', 'variable1_label', 'variable1_code',
    'variable1_descriptor', 'variable2_label', 'variable2_code',
    'variable2_descriptor', 'value_type_description', 'value', 'value_label',
    'decimals', 'confidentiality_indicator', 'confidentiality_label',
    'final_indicator', 'final_label', 'last_updated_at_source'
]

# Metrics we need for the affordability project
TARGET_METRICS = [
    'Median household income',
    'Median personal income of adults',
    'Population',
    'Households who own their home or hold in a family trust',
    'Median weekly rent paid by households',
    'Number of private dwellings',
    'Median age',
    'New Zealand index of socioeconomic deprivation',
    'Work and labour force status',
]

AUCKLAND_SUBURBS = [
    'Albany', 'Avondale', 'Birkdale', 'Blockhouse Bay', 'Botany',
    'Browns Bay', 'Devonport', 'East Tamaki', 'Eden Terrace', 'Ellerslie',
    'Epsom', 'Flat Bush', 'Glenfield', 'Glen Innes', 'Glen Eden',
    'Grey Lynn', 'Helensville', 'Henderson', 'Hillsborough', 'Howick',
    'Kelston', 'Kohimarama', 'Lynfield', 'Mangere', 'Manukau',
    'Manurewa', 'Massey', 'Meadowbank', 'Mission Bay', 'Mount Albert',
    'Mount Eden', 'Mount Roskill', 'Mount Wellington', 'Newmarket',
    'New Lynn', 'Northcote', 'Onehunga', 'One Tree Hill', 'Orewa',
    'Otahuhu', 'Otara', 'Pakuranga', 'Papakura', 'Papatoetoe',
    'Parnell', 'Penrose', 'Point Chevalier', 'Ponsonby', 'Pukekohe',
    'Remuera', 'Royal Oak', 'Sandringham', 'Silverdale', 'St Heliers',
    'St Johns', 'Sunnyvale', 'Swanson', 'Takanini', 'Takapuna',
    'Three Kings', 'Titirangi', 'Waitakere', 'Waiuku', 'Westgate',
    'Whangaparaoa', 'Wiri', 'Beachlands', 'Clevedon', 'Drury',
    'Glenbrook', 'Karaka', 'Kumeu', 'Wellsford'
]

def ingest_census():
    print("Reading Stats NZ census file..")
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "stats_nz_census.csv")
    df = pd.read_csv(csv_path, header=None, names=col_names, skiprows=1,
    usecols=[
            'section_title', 'classification_label', 'descriptor',
            'period', 'value_type_description', 'value', 'value_label'
        ])
    print(f"Full file loaded: {len(df)} rows")

    # Step 1 - Filter to SA2 level, 2023 census only
    df = df[
        (df['classification_label'] == 'Statistical area 2') &
        (df['period'] == 2023)
    ]
    print(f"After SA2 2023 filter: {len(df)} rows")

    # Step 2 - Filter to target metrics only
    df = df[df['section_title'].isin(TARGET_METRICS)]
    print(f"After metrics filter: {len(df)} rows")

    # Step 3 - Filter to Auckland suburbs only
    auckland_pattern = '|'.join(AUCKLAND_SUBURBS)
    df = df[df['descriptor'].str.contains(auckland_pattern, case=False, na=False)]
    print(f"After Auckland filter: {len(df)} rows")

    # Step 4 - Keep only median/count rows, not percentages
    df = df[df['value_type_description'].isin(['Median', 'Count'])]
    print(f"After value type filter: {len(df)} rows")

    # Step 5 - Clean up
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna(subset=['value'])
    df['ingested_at'] = pd.Timestamp.now()

    # Uppercase for Snowflake
    df.columns = [c.upper() for c in df.columns]

    print(f"\nSample data:")
    print(df.head(10).to_string())
    print(f"\nUnique suburbs: {df['DESCRIPTOR'].nunique()}")
    print(f"Unique metrics: {df['SECTION_TITLE'].nunique()}")

    df = df.reset_index(drop=True)
    write_dataframe(df, "RAW.LANDING", "STATS_NZ_CENSUS_2023",  overwrite=True)
    print("Done.")

if __name__ == "__main__":
    ingest_census()
