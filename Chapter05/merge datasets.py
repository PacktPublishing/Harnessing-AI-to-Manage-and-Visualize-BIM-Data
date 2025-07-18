"""
Merge the Revit‐schedule dataset with the external comfort dataset
and write the stacked result to `union_dataset.csv`.

• Room Schedule for CI Calculation_with_PMV_and_CI.csv  – Revit side
• external_dataset_with_PMV.csv                         – external side
"""

import pandas as pd

# 1. Load both datasets
df_main     = pd.read_csv("Room Schedule for CI Calculation_with_PMV_and_CI.csv")
df_external = pd.read_csv("external_dataset_with_PMV.csv")   # current external file

# 2. Align columns: create the union of all column names
all_cols = sorted(set(df_main.columns).union(df_external.columns))

#    Add any missing columns with NaN placeholders
for col in all_cols:
    if col not in df_main.columns:
        df_main[col] = pd.NA
    if col not in df_external.columns:
        df_external[col] = pd.NA

#    Re-order both DataFrames to the identical column layout
df_main     = df_main[all_cols]
df_external = df_external[all_cols]

# 3. Stack the two DataFrames vertically
df_union = pd.concat([df_main, df_external], ignore_index=True, sort=False)

# 4. Save the combined dataset
df_union.to_csv("union_dataset.csv", index=False)
print("✅ Union complete → union_dataset.csv")
