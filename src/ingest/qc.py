"""Quality checks for fetched scenes. A file that downloads is not necessarily complete."""
import numpy as np, rasterio
from scipy.ndimage import label

def scene_qc(path, min_valid=0.98):
    with rasterio.open(path) as s:
        a = s.read(1)
    ok = np.isfinite(a) & (a != 0)
    hole = ~ok
    lab, n = label(hole)
    size = np.bincount(lab.ravel()); size[0] = 0
    big = int(size.max()) if n else 0
    res = {"valid": round(float(ok.mean()), 3), "largest_hole_px": big,
           "pass": bool(ok.mean() >= min_valid)}
    print(path.split("/")[-1], res)
    return res
