# Validate comfort parameters for every room.
# IN[0] = rooms, IN[1] = param names, IN[2] = limits dict
rooms, param_names, limits = IN[0], IN[1], IN[2]

INCLUDE_NAME = "PACKT_Incl"  # boolean flag to include room in checks

issues = []  # (room name, param, problem)
for r in rooms:
    # Skip this room altogether if PACKT_Incl exists and is False / 0
    try:
        incl_val = r.GetParameterValueByName(INCLUDE_NAME)
        # Revit booleans come back as integers (0 / 1) or strings "0" / "1"
        if str(incl_val).strip() in ("0", "False", "false"):
            continue
    except:  # parameter not found → assume include
        pass

    for p in param_names:
        # 1 — get the value (skip if parameter missing)
        try:
            val = r.GetParameterValueByName(p)
        except:
            continue
        # Treat empty strings or nulls as “missing” rather than non‑numeric
        if val is None or (isinstance(val, str) and val.strip() == ""):
            issues.append((r.Name, p, "missing"))
            continue
        # 2 — coerce to a number; if that fails flag as non‑numeric text
        try:
            val_num = float(val)
        except (TypeError, ValueError):
            issues.append((r.Name, p, "non‑numeric"))
            continue
        # 3 — compare against comfort range
        low, high = limits[p.split("_")[1]]
        if val_num < low or val_num > high:
            issues.append((r.Name, p, round(val_num, 2)))

OUT = issues  # Dynamo preview shows an empty list when everything is fine
