"""Rule-based baseline: two-track agreement on same-track change maps."""
import numpy as np, rasterio
from scipy.ndimage import uniform_filter, label

def load(tag, path="/kaggle/temp/s1"):
    with rasterio.open(f"{path}/{tag}_change.tif") as s:
        return s.read(), s.profile

def zscore(a, win=151):
    """Remove regional haze (large-window mean), then scale by robust sigma."""
    v = np.isfinite(a)
    x = np.where(v, a, 0.0)
    bg = uniform_filter(x, win) / np.maximum(uniform_filter(v.astype("float32"), win), 1e-6)
    r = np.where(v, a - bg, np.nan)
    sig = np.nanmedian(np.abs(r - np.nanmedian(r))) * 1.4826
    return r / sig

def track_masks(tag, k=3.0, k_vh=1.5):
    c, prof = load(tag)
    zv, zh = zscore(c[0]), zscore(c[1])
    dec = (zv < -k) & (zh < -k_vh)     # VV strong drop, VH agrees in sign
    inc = (zv > k) & (zh > k_vh)
    return dec, inc, prof

def remove_small(m, min_px=20):
    lab, n = label(m)
    if n == 0: return m
    size = np.bincount(lab.ravel()); keep = size >= min_px; keep[0] = False
    return keep[lab]

def baseline(tags=("o85", "o19"), out="/kaggle/temp/baseline.tif", **kw):
    res = [track_masks(t, **kw) for t in tags]
    dec_all = np.logical_and.reduce([r[0] for r in res])
    dec_any = np.logical_or.reduce([r[0] for r in res])
    inc_all = np.logical_and.reduce([r[1] for r in res])
    inc_any = np.logical_or.reduce([r[1] for r in res])
    o = np.zeros(dec_all.shape, "uint8")
    o[remove_small(dec_any, 30) & ~dec_all] = 1      # decrease, one track
    o[remove_small(dec_all, 10)] = 2                 # decrease, both tracks
    o[remove_small(inc_any, 30) & ~inc_all] = 3      # increase, one track
    o[remove_small(inc_all, 10)] = 4                 # increase, both tracks
    prof = res[0][2]; prof.update(count=1, dtype="uint8", nodata=0)
    with rasterio.open(out, "w", **prof) as d: d.write(o, 1)
    for v, n in [(1, "decrease, 1 track"), (2, "decrease, BOTH tracks"),
                 (3, "increase, 1 track"), (4, "increase, BOTH tracks")]:
        print(f"{n}: {(o == v).sum() * 1e-4:.2f} km2")
    return o
