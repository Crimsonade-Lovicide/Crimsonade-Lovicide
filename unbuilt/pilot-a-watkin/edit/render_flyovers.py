"""Render the Wembley flyovers from open Environment Agency LiDAR (no Google Earth, no AI).

Writes JPEG frame sequences into ../assets/footage/<name>/, which build.py picks up for C3, S4 and O1.
Data credit for the description: "Contains Environment Agency information (c) Environment Agency and/or
database right" (Open Government Licence v3.0).
Usage: python3 render_flyovers.py [GE1_cold_open GE2_topdown GE4_dusk]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "toolkit"))
from unbuilt_kit import lidar  # noqa: E402
from unbuilt_kit.core import ease  # noqa: E402

NPZ = os.path.join(HERE, "..", "assets", "lidar", "wembley_lidar.npz")
OUT = os.path.join(HERE, "..", "assets", "footage")
C = (519369.0, 185526.0)     # centre of the pitch, British National Grid, read off the LiDAR
G = 36.5                     # ground level around the stadium (m above Newlyn datum)
R = 1100.0
FPS = 24


def thin(E, N, d):           # the arch and roof cables: leave as floating points, no walls under them
    return (np.hypot(E - C[0], N - C[1]) < 160) & (d > 95)


def move(a, b, t):
    k = ease(t)
    return tuple(x + (y - x) * k for x, y in zip(a, b))


SHOTS = {
    # name: (seconds, start camera offset (dE, dN, height), end offset, target offset)
    "GE1_cold_open": (12, (-1250, 950, 700), (-620, 470, 360), (0, 0, 15)),
    "GE2_topdown":   (12, (0, 0, 720), (0, 0, 560), None),
    "GE4_dusk":      (12, (-520, 400, 300), (-1150, 880, 640), (0, 0, 15)),
}


def render(name, points):
    secs, a, b, tgt = SHOTS[name]
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    n = secs * FPS
    for i in range(n):
        t = i / (n - 1)
        off = move(a, b, t)
        cam = (C[0] + off[0], C[1] + off[1], G + off[2])
        target = (C[0], C[1], G) if tgt is None else (C[0] + tgt[0], C[1] + tgt[1], G + tgt[2])
        img = lidar.render(points, cam, target, (1920, 1080), center=C, radius=R)
        if name == "GE4_dusk":            # a warmer, dimmer grade for the ending (a grade, not a simulation)
            img = np.clip(img * np.array([1.0, 0.93, 0.82]) * 0.9, 0, 1)
        Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(
            os.path.join(folder, f"{name}_{i:04d}.jpeg"), quality=92)
        if i % 48 == 0:
            print(name, i, "/", n, flush=True)


def main():
    names = sys.argv[1:] or list(SHOTS)
    points = lidar.load_scene(NPZ, C, radius=R, thin_mask=thin)
    for name in names:
        render(name, points)


if __name__ == "__main__":
    main()
