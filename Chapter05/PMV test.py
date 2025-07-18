from pythermalcomfort.models import pmv_ppd_ashrae

# Example calculation for one room

results = pmv_ppd_ashrae(tdb=24, tr=24, vr=0.1, rh=50, met=1.2, clo=0.7, wme=0)

print(results)