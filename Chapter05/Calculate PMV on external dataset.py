import pandas as pd
from pythermalcomfort.models import pmv_ppd_ashrae

SRC_FILE   = "cleaned external dataset.csv"
OUT_FILE   = "external_dataset_with_PMV.csv"
DEFAULT_VR = 0.10     # m/s
DELTA_TR   = 1.0      # °C

df = pd.read_csv(SRC_FILE)

# ── PACKT_Vr ──────────────────────────────────────────────────────────
if "PACKT_Vr" in df.columns:
    df["PACKT_Vr"] = pd.to_numeric(df["PACKT_Vr"], errors="coerce") \
                        .fillna(DEFAULT_VR)
else:
    df["PACKT_Vr"] = DEFAULT_VR

# ── PACKT_Tr ──────────────────────────────────────────────────────────
if "PACKT_Tr" in df.columns:
    df["PACKT_Tr"] = pd.to_numeric(df["PACKT_Tr"], errors="coerce") \
                        .fillna(df["PACKT_Tdb"] + DELTA_TR)
else:
    df["PACKT_Tr"] = df["PACKT_Tdb"] + DELTA_TR

# ── PACKT_W (optional) ────────────────────────────────────────────────
if "PACKT_W" not in df.columns:
    df["PACKT_W"] = 0.0

# ── ensure remaining inputs are numeric ───────────────────────────────
for col in ["PACKT_Tdb", "PACKT_rh", "PACKT_met", "PACKT_clo"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ── compute PMV without touching the existing CI ──────────────────────
def _pmv(row):
    return pmv_ppd_ashrae(
        tdb=row["PACKT_Tdb"], tr=row["PACKT_Tr"],
        vr=row["PACKT_Vr"],  rh=row["PACKT_rh"],
        met=row["PACKT_met"], clo=row["PACKT_clo"]
    ).pmv

df["PACKT_PMV"] = df.apply(_pmv, axis=1)

df.to_csv(OUT_FILE, index=False)
print(f"✅ PMV added → {OUT_FILE} (existing PACKT_CI left unchanged)")
