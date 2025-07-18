import pandas as pd

from pythermalcomfort.models import pmv_ppd_ashrae

 

# 1 — load the cleaned schedule you wrote in the previous step

df = pd.read_csv("Room Schedule for CI Calculation.csv")

 

# 2 — flatten Revit’s multiline headers (keeps text before first line-break)

df = df.rename(columns=lambda c: c.split("\n")[0])

 

# 3 — make sure the six inputs we need are numeric

cols = ["PACKT_Tdb", "PACKT_Tr", "PACKT_Vr", "PACKT_rh", "PACKT_met", "PACKT_clo"]

df[cols] = df[cols].apply(pd.to_numeric)

 

# 4 — compute PMV row-by-row

df["PACKT_PMV"] = df.apply(

    lambda r: pmv_ppd_ashrae(

        tdb=r["PACKT_Tdb"],

        tr=r["PACKT_Tr"],

        vr=r["PACKT_Vr"],

        rh=r["PACKT_rh"],

        met=r["PACKT_met"],

        clo=r["PACKT_clo"],

    ).pmv,

    axis=1,

)

 

# 5 — save the result

df.to_csv("Room Schedule for CI Calculation_with_PMV.csv", index=False)

print("✅ PMV column added and file saved as Room Schedule for CI Calculation_with_PMV.csv")