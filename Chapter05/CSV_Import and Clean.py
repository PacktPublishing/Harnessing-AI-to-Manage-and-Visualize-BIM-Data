import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 1. Locate the raw CSV next to this script
# ------------------------------------------------------------------
data_path = Path(__file__).with_name("ComfortData_v1.csv")

# ------------------------------------------------------------------
# 2. Read the file, skipping the JSON-heavy first header row
#    (the human-readable headings are on the second line)
# ------------------------------------------------------------------
comfort_data = pd.read_csv(data_path, header=1)

# ------------------------------------------------------------------
# 3. Drop columns we don’t need
#    • ‘GUID’ – a unique Revit identifier
#    • any unnamed trailing columns created by the export
# ------------------------------------------------------------------
comfort_data = comfort_data.drop(columns=["GUID"], errors="ignore")
comfort_data = comfort_data.loc[:, ~comfort_data.columns.str.contains(r"^Unnamed")]

# ------------------------------------------------------------------
# 4. Ensure key numeric fields are numbers
#    (no coercion flag—any bad values will raise an error and reveal
#     data issues instead of silently turning into NaN)
# ------------------------------------------------------------------
numeric_cols = [
    "PACKT_Tdb\nDouble\nInstance\nOther",
    "PACKT_Tr\nDouble\nInstance\nOther",
    "PACKT_rh\nDouble\nInstance\nOther",
    "PACKT_Vr\nDouble\nInstance\nOther",
    "PACKT_W\nDouble\nInstance\nOther",
]
comfort_data[numeric_cols] = comfort_data[numeric_cols].apply(pd.to_numeric)

# ------------------------------------------------------------------
# 5. Strip the “ m²” suffix from the Area field and convert to float
# ------------------------------------------------------------------
comfort_data["Area\nSchedule Parameter"] = (
    comfort_data["Area\nSchedule Parameter"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
    .astype(float)
)

# ------------------------------------------------------------------
# 6. Save the cleaned DataFrame
# ------------------------------------------------------------------
clean_path = Path(__file__).with_name("Room Schedule for CI Calculation.csv")
comfort_data.to_csv(clean_path, index=False)

print(f"✅ Cleaned schedule written to: {clean_path}")
