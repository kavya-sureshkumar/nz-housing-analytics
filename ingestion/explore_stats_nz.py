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
    usecols=['section_title', 'classification_label', 'descriptor',
             'period', 'value_type_description', 'value'])

sa2_2023 = df[
    (df['classification_label'] == 'Statistical area 2') &
    (df['period'] == 2023) &
    (df['section_title'] == 'Median household income') &
    (df['value_type_description'] == 'Median')
]

MISSING = [
    'Flat Bush', 'Mangere', 'Mangere Bridge',
    'Otahuhu', 'Otara', 'Ranui',
    'St Heliers', 'Te Atatu Peninsula', 'Te Atatu South'
]

print("=== SEARCHING FOR MISSING SUBURBS ===")
for suburb in MISSING:
    matches = sa2_2023[
        sa2_2023['descriptor'].str.contains(suburb, case=False, na=False)
    ]['descriptor'].unique()
    if len(matches) > 0:
        print(f"\n{suburb} → found as:")
        for m in matches:
            print(f"  '{m}'")
    else:
        print(f"\n{suburb} → NOT FOUND in census at all")