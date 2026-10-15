"""Download the USGS laser scan of Liberty Island and save the points around the statue (no AI).

Source: USGS 3D Elevation Program, project NJ_NE6County_B23 (flown 2023, published 2026), tile K7B6.
US government work, public domain. Credit: "Lidar: U.S. Geological Survey, 3D Elevation Program".
Writes liberty_points.npz: pts = (N, 4) float32 [east, north, height, albedo] in metres, with the statue's
highest point at (0, 0) horizontally and heights above NAVD88 (about sea level).
Usage: python3 fetch_lidar.py
"""
import os
import subprocess

import laspy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TILES = ["https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/NJ_NE6County_B23/"
         "NJ_NE6Co_2_B23/LAZ/USGS_LPC_NJ_NE6County_B23_K7B6.laz"]
FT = 1200 / 3937                     # US survey foot, in metres
TORCH = (618420.75, 676293.63)       # the highest return (the torch), New Jersey State Plane feet
RADIUS_M = 450.0


def main():
    os.makedirs(os.path.join(HERE, "raw"), exist_ok=True)
    pts = []
    for url in TILES:
        path = os.path.join(HERE, "raw", url.rsplit("_", 1)[-1])
        if not os.path.exists(path):
            subprocess.run(["curl", "-sS", "-m", "900", "-o", path, url], check=True)
        f = laspy.read(path)
        x = (np.asarray(f.x) - TORCH[0]) * FT
        y = (np.asarray(f.y) - TORCH[1]) * FT
        z = np.asarray(f.z) * FT
        cls = np.asarray(f.classification)
        keep = (np.hypot(x, y) < RADIUS_M) & ~np.isin(cls, [7, 18])   # drop low and high noise (birds, multipath)
        inten = np.asarray(f.intensity)[keep].astype(np.float32)
        pts.append((x[keep], y[keep], z[keep], inten))
    x, y, z, inten = (np.concatenate(c) for c in zip(*pts))
    # drop stray returns over the water: points whose 2 m cell holds fewer than 4 points
    key = np.floor(x / 2).astype(np.int64) * 100000 + np.floor(y / 2).astype(np.int64)
    _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    ok = cnt[inv] >= 4
    x, y, z, inten = x[ok], y[ok], z[ok], inten[ok]
    lo, hi = np.percentile(inten, [2, 98])
    albedo = np.clip((inten - lo) / (hi - lo), 0, 1) * 0.8 + 0.15
    out = np.stack([x, y, z, albedo], 1).astype(np.float32)
    np.savez_compressed(os.path.join(HERE, "liberty_points.npz"), pts=out)
    print(f"{len(out):,} points within {RADIUS_M:.0f} m; top {z.max():.1f} m")


if __name__ == "__main__":
    main()
