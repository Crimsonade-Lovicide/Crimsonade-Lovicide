"""Render the Liberty Island flyovers straight from the USGS laser scan (no satellite imagery, no AI).

Writes JPEG frame sequences into ../assets/footage/<name>/ for C2, L4 and O1.
Data credit for the description: "Lidar: U.S. Geological Survey, 3D Elevation Program" (public domain).
Usage: python3 render_flyovers.py [LIB1_push LIB2_arc LIB3_dusk]
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "toolkit"))
from unbuilt_kit import lidar  # noqa: E402
from unbuilt_kit.core import ease  # noqa: E402

NPZ = os.path.join(HERE, "..", "assets", "lidar", "liberty_points.npz")
OUT = os.path.join(HERE, "..", "assets", "footage")
FPS = 24
R = 450.0                    # radius of the loaded data, metres
SPACING = 0.3                # metres between laser points on the ground (about 14 per square metre)
# The statue faces south-east, out to sea, so the cameras sit on the +east / -north side.


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def arc(t):                  # L4: a slow quarter-arc in front of the statue, 200 m out, at pedestal-top height
    ang = math.radians(-60 + 35 * ease(t))           # from south-south-east round towards east-south-east
    return (200 * math.cos(ang), 200 * math.sin(ang), 55), (0, 4, 52)


SHOTS = {
    # name: (seconds, path(t) -> (camera, target))
    "LIB1_push": (10, lambda t: (lerp((330, -390, 95), (140, -165, 50), ease(t)), (0, 3, 55))),
    "LIB2_arc": (10, arc),
    "LIB3_dusk": (12, lambda t: (lerp((140, -165, 50), (470, -550, 215), ease(t)), lerp((0, 4, 58), (0, 0, 30), ease(t)))),
}


def render(name, points):
    secs, path = SHOTS[name]
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    n = secs * FPS
    prev = None
    for i in range(n):
        cam, target = path(i / (n - 1))
        img = lidar.render(points, cam, target, (1920, 1080), center=(0, 0), radius=R, ss=2, spacing=SPACING,
                           haze=4000)
        img = img if prev is None else 0.65 * img + 0.35 * prev      # as at Wembley: calms point sparkle
        prev = img
        if name == "LIB3_dusk":                                        # warmer, dimmer grade for the ending
            img = np.clip(img * np.array([1.0, 0.93, 0.82]) * 0.9, 0, 1)
        Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(
            os.path.join(folder, f"{name}_{i:04d}.jpeg"), quality=92)
        if i % 48 == 0:
            print(name, i, "/", n, flush=True)


def main():
    names = sys.argv[1:] or list(SHOTS)
    points = np.load(NPZ)["pts"]
    for name in names:
        render(name, points)


if __name__ == "__main__":
    main()
