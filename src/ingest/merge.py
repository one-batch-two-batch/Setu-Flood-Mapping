"""Merge a new-box S1 pair with the old-box pair, one source per pixel for BOTH dates."""
import numpy as np, rasterio
from rasterio.windows import from_bounds

def merge_pair(pre_new, post_new, pre_old, post_old, out_pre, out_post):
    with rasterio.open(pre_new) as s:
        prof = s.profile; tr = s.transform
        A = [s.read()]
    with rasterio.open(post_new) as s: A.append(s.read())
    with rasterio.open(pre_old) as s:
        B = [s.read()]; ob = s.bounds
    with rasterio.open(post_old) as s: B.append(s.read())
    w = from_bounds(*ob, transform=tr).round_offsets().round_lengths()
    r0, c0, h, wd = int(w.row_off), int(w.col_off), int(w.height), int(w.width)
    assert B[0].shape[1:] == (h, wd), f"old grid {B[0].shape[1:]} != window {(h, wd)}"
    ok_new = np.all(np.isfinite(A[0]), axis=0) & np.all(np.isfinite(A[1]), axis=0)
    ok_old = np.all(np.isfinite(B[0]), axis=0) & np.all(np.isfinite(B[1]), axis=0)
    use_old = np.zeros(ok_new.shape, bool)
    use_old[r0:r0+h, c0:c0+wd] = ok_old & ~ok_new[r0:r0+h, c0:c0+wd]
    outs = []
    for a, b in zip(A, B):
        o = np.where(ok_new, a, np.nan).astype("float32")
        o[:, r0:r0+h, c0:c0+wd] = np.where(use_old[r0:r0+h, c0:c0+wd], b, o[:, r0:r0+h, c0:c0+wd])
        outs.append(o)
    for path, o in zip((out_pre, out_post), outs):
        with rasterio.open(path, "w", **prof) as d: d.write(o)
    print("from new: %.3f | from old: %.3f | empty: %.3f" % (
        ok_new.mean(), use_old.mean(), 1 - (ok_new | use_old).mean()))
