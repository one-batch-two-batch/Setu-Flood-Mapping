# Status (30 Sep)
- Tracks: use o19 and o85 only. o121 covers 24% of the box and is excluded.
- New box: [84.85, 27.70, 85.46, 28.36]
- Fetched on new box: o19 2026-08-24 (missing block rows 2048-4095, cols 4096+) and o19 2026-09-05 (missing block rows 0-2047, cols 4096+). Different blocks, same east tile column. Old scenes fill them via merge_pair; 1.6% stays empty in the far north-east, away from the corridor.
- o19 pair merged on the new box (merged/o19_change.tif). Check every band and the hole location on each new scene.
- Old-box scenes (6) are in the Kaggle dataset; merge_pair fills the block from them.
- Next: merge o19 pair, fetch o85 (16 Aug, 28 Aug) and check with scene_qc, DEM, terrain layers, then ML.
- Rule: never commit rasters or *.db; use git add <file>.
