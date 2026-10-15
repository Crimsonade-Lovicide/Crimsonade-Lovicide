"""Download Environment Agency LiDAR around Wembley Stadium and keep a cropped working copy.

Data: Environment Agency, LIDAR Composite First Return DSM 2022 (1 m) and National LIDAR Programme
intensity 2023 (1 m). Open Government Licence v3.0. Credit: "Contains Environment Agency information
(c) Environment Agency and/or database right" (put this in the video description).

Writes wembley_lidar.npz: dsm (float32, metres above Newlyn datum, NaN = no data), intensity (uint8),
origin (easting, northing of the top-left pixel centre), 1 m pixels, British National Grid (EPSG:27700).
"""
import io
import zipfile
from pathlib import Path

import numpy as np
import requests
import tifffile

HERE = Path(__file__).resolve().parent
TILES = {  # 5 km tiles: id -> (easting min, northing min)
    "TQ1585": (515000, 185000), "TQ2085": (520000, 185000),
    "TQ1580": (515000, 180000), "TQ2080": (520000, 180000),
}
BASE = "https://environment.data.gov.uk/tiles/collections/survey"
PRODUCTS = {"dsm": "lidar_composite_first_return_dsm/2022/1", "intensity": "national_lidar_programme_intensity/2023/1"}
CROP = (518000, 184000, 521000, 187500)   # E min, N min, E max, N max: about 3 x 3.5 km around the stadium


def tile_array(product, tile):
    r = requests.get(f"{BASE}/{PRODUCTS[product]}/{tile}", timeout=600)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = [n for n in z.namelist() if n.lower().endswith(".tif")][0]
    a = tifffile.imread(io.BytesIO(z.read(name))).astype(np.float32)
    a[a < -1e30] = np.nan
    return a


def main():
    e0, n0, e1, n1 = CROP
    out = {k: np.full((n1 - n0, e1 - e0), np.nan, np.float32) for k in PRODUCTS}
    for tile, (te, tn) in TILES.items():
        for k in PRODUCTS:
            a = tile_array(k, tile)              # row 0 = northing tn+5000, col 0 = easting te
            ce0, ce1 = max(e0, te), min(e1, te + 5000)
            cn0, cn1 = max(n0, tn), min(n1, tn + 5000)
            if ce0 >= ce1 or cn0 >= cn1:
                continue
            src = a[(tn + 5000 - cn1):(tn + 5000 - cn0), (ce0 - te):(ce1 - te)]
            out[k][(n1 - cn1):(n1 - cn0), (ce0 - e0):(ce1 - e0)] = src
            print(tile, k, "ok", flush=True)
    i = out["intensity"]
    lo, hi = np.nanpercentile(i, 1), np.nanpercentile(i, 99)
    inten = np.clip((np.nan_to_num(i, nan=lo) - lo) / (hi - lo), 0, 1)
    np.savez_compressed(HERE / "wembley_lidar.npz", dsm=out["dsm"], intensity=(inten * 255).astype(np.uint8),
                        origin=np.array([e0 + 0.5, n1 - 0.5]))
    print("saved", out["dsm"].shape, "nan share", float(np.isnan(out["dsm"]).mean()))


if __name__ == "__main__":
    main()
