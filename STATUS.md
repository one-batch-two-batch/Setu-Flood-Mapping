# Status (30 Sep)
- Tracks: use o19 and o85 only. o121 covers 24% of the box and is excluded.
- New box: [84.85, 27.70, 85.46, 28.36]
- Fetched on new box: o19 2026-08-24, o19 2026-09-05 (both have the same missing block: rows 2048-4095, cols 4096+).
- Old-box scenes (6) are in the Kaggle dataset; merge_pair fills the block from them.
- Next: merge o19 pair, fetch o85 (16 Aug, 28 Aug) and check with scene_qc, DEM, terrain layers, then ML.
- Rule: never commit rasters or *.db; use git add <file>.
