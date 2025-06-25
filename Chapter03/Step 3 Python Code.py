# STEP 3 – universal “room chart” node 

import sys, os, tempfile, uuid, pprint 

import pandas as pd, numpy as np 

import matplotlib 

matplotlib.use("Agg") 

import matplotlib.pyplot as plt 

 

# ----------------------------------------------------------------------- 

# 1)  DEBUG: see exactly what Dynamo is feeding this node 

print(">>> DEBUG – types coming in:") 

for i, obj in enumerate(IN): 

    print(f"IN[{i}] : {type(obj).__name__}  ->  sample: {str(obj)[:60]}") 

print("--------------------------------------------------------------") 

 

# ----------------------------------------------------------------------- 

# 2)  NORMALISE to a DataFrame, handling every common wiring variant 

def to_dataframe(inputs): 

    """ 

    Returns (DataFrame, msg).  `inputs` is the list Dynamo passes in. 

    """ 

    # Variant A: single DataFrame already 

    if len(inputs) == 1 and isinstance(inputs[0], pd.DataFrame): 

        return inputs[0], "took DataFrame directly" 

 

    # Variant B: three parallel lists on separate ports 

    if len(inputs) == 3 and all(isinstance(x, list) for x in inputs): 

        names, areas, volumes = inputs 

        return pd.DataFrame({ 

            "Room": names, 

            "Area_ft²": pd.to_numeric(areas, errors="coerce"), 

            "Volume_ft³": pd.to_numeric(volumes, errors="coerce") 

        }), "rebuilt DF from three lists" 

 

    # Variant C: single list-of-lists  (OUT from step 1 wired straight in) 

    if len(inputs) == 1 and isinstance(inputs[0], list) \ 

       and len(inputs[0]) == 3 and all(isinstance(x, list) for x in inputs[0]): 

        names, areas, volumes = inputs[0] 

        return pd.DataFrame({ 

            "Room": names, 

            "Area_ft²": pd.to_numeric(areas, errors="coerce"), 

            "Volume_ft³": pd.to_numeric(volumes, errors="coerce") 

        }), "unpacked nested list and rebuilt DF" 

 

    raise ValueError( 

        "Unexpected input pattern – check how the node is wired." 

    ) 

 

df, how = to_dataframe(IN) 

print(f">>> DEBUG – DataFrame built using: {how}") 

print(df.head())   # first 5 rows for sanity 

print("--------------------------------------------------------------") 

 

# ----------------------------------------------------------------------- 

# 3)  PLOT 

x_pos   = range(len(df)) 

heights = df["Area_ft²"] 

 

fig = plt.figure(figsize=(10, 6)) 

plt.bar(x_pos, heights) 

plt.xticks(x_pos, df["Room"], rotation=90) 

plt.ylabel("Area (ft²)") 

plt.title("Room Areas – Snowdon Towers") 

plt.tight_layout() 

 

tmp_path = os.path.join( 

    tempfile.gettempdir(), f"room_areas_{uuid.uuid4().hex}.png" 

) 

fig.savefig(tmp_path); plt.close(fig) 

 

OUT = df, tmp_path          # DataFrame and image path back to Dynamo 
