"""Same-track dB change detection with speckle smoothing and validity masks."""
import numpy as np, rasterio
from scipy.ndimage import uniform_filter

def load(path):
    with rasterio.open(path) as s:
        return s.read().astype("float32"), s.profile

def valid_mask(a):
    """a: (bands, H, W) in dB. True where data exist."""
    return np.isfinite(a).all(axis=0) & (a[0] != 0) & (a[0] > -50)

def coverage(path):
    a, _ = load(path)
    return float(valid_mask(a).mean())

def smooth_db(a, valid, size=5):
    """Average in linear power, normalised by valid-pixel count (no edge bias)."""
    lin = np.where(valid, 10 ** (a / 10), 0.0)
    w = uniform_filter(valid.astype("float32"), size)
    out = np.stack([uniform_filter(b, size) / np.maximum(w, 1e-6) for b in lin])
    return 10 * np.log10(np.maximum(out, 1e-6))

def change_map(pre_path, post_path, out_path=None, size=5):
    pre, prof = load(pre_path)
    post, _ = load(post_path)
    assert pre.shape == post.shape, "grids differ; same bbox and resolution required"
    v = valid_mask(pre) & valid_mask(post)
    diff = smooth_db(post, v, size) - smooth_db(pre, v, size)   # VV, VH
    diff[:, ~v] = np.nan
    if out_path:
        prof.update(count=2, dtype="float32", nodata=np.nan)
        with rasterio.open(out_path, "w", **prof) as dst:
            dst.write(diff)
    return diff
