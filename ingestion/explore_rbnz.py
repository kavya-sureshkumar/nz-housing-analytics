import os
import pandas as pd

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "rbnz_ocr.xlsx")

df_raw = pd.read_excel(csv_path, header=None, nrows=5)
print("=== COLUMN DESCRIPTIONS ===")
for col_idx in range(df_raw.shape[1]):
    print(f"Column {col_idx:2d} | {df_raw.iloc[0, col_idx]} | {df_raw.iloc[1, col_idx]}")

print("\n=== ACTUAL DATA (first 5 rows) ===")
df_data = pd.read_excel(csv_path, header=None, skiprows=5)
print(df_data.head())

print(f"\nDate range: {df_data.iloc[0, 0]} to {df_data.iloc[-1, 0]}")
print(f"Total rows: {len(df_data)}")
