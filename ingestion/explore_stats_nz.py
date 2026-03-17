import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "stats_nz_census.csv")


col_names = [
    'section_title', 'section_type', 'classification_label', 'code',
    'descriptor', 'period', 'duration', 'variable1_label', 'variable1_code',
    'variable1_descriptor', 'variable2_label', 'variable2_code',
    'variable2_descriptor', 'value_type_description', 'value', 'value_label',
    'decimals', 'confidentiality_indicator', 'confidentiality_label',
    'final_indicator', 'final_label', 'last_updated_at_source'
]

df = pd.read_csv(csv_path, header=None, names=col_names, skiprows=1,
    usecols=['section_title', 'classification_label', 'descriptor', 'period', 'value_type_description', 'value', 'value_label'])

print("Shape:", df.shape)

# Filter to SA2, 2023 census only
sa2_2023 = df[
    (df['classification_label'] == 'Statistical area 2') &
    (df['period'] == 2023)
]
print(f"SA2 2023 rows: {len(sa2_2023)}")

# Known Auckland suburbs to identify Auckland SA2 areas
auckland_suburbs = [
    'Ponsonby', 'Remuera', 'Manurewa', 'Papakura', 'Henderson',
    'Mangere', 'Takanini', 'Botany', 'Howick', 'Newmarket',
    'Parnell', 'Grey Lynn', 'Mount Eden', 'Onehunga', 'Otahuhu',
    'Papatoetoe', 'Blockhouse Bay', 'New Lynn', 'Waitakere', 'Albany'
]

# Find all descriptors that match Auckland suburbs
print("\n=== CONFIRMING AUCKLAND SUBURBS EXIST ===")
for suburb in auckland_suburbs:
    matches = sa2_2023[
        sa2_2023['descriptor'].str.contains(suburb, case=False, na=False)
    ]['descriptor'].unique()
    if len(matches) > 0:
        print(f"Found: {matches}")

# Check what metrics are available for these suburbs
print("\n=== AVAILABLE METRICS (section_titles) ===")
print(sa2_2023['section_title'].unique())