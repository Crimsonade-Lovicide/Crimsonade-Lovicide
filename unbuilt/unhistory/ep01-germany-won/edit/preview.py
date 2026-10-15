"""Quick look at shots: render each at 960x540 for a short time and save its last frame as a PNG contact sheet.
Usage: python3 preview.py C2 C4 D4 ...   -> build/preview.png"""
import os
import sys

import numpy as np
from PIL import Image

import build
from shots import SHOTS
import unbuilt_kit as kit

SMALL = (960, 540)


def last_frame(mp4, png):
    kit.core.run_ffmpeg(["-sseof", "-0.05", "-i", mp4, "-frames:v", "1", png])
    return Image.open(png)


names = sys.argv[1:]
tiles = []
os.makedirs(os.path.join(build.BUILD, "preview"), exist_ok=True)
for n in names:
    fn, kw = SHOTS[n]
    kw = {k: v for k, v in kw.items() if k not in ("lower_third", "fixed")}
    out = os.path.join(build.BUILD, "preview", n + ".mp4")
    if "image" in kw:
        img = build.asset(kw.pop("image"))
        dur = 4.5 if fn == "annotate" else 2.0
        getattr(kit, fn)(img, out, dur, size=SMALL, **kw)
    else:
        continue
    tiles.append((n, last_frame(out, out.replace(".mp4", ".png"))))
cols = 3
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (SMALL[0] * cols // 2, SMALL[1] * rows // 2), "white")
for i, (n, im) in enumerate(tiles):
    im = im.resize((SMALL[0] // 2, SMALL[1] // 2))
    sheet.paste(im, ((i % cols) * SMALL[0] // 2, (i // cols) * SMALL[1] // 2))
sheet.save(os.path.join(build.BUILD, "preview.png"))
print("sheet:", [n for n, _ in tiles])
