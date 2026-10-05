"""Make Pilot B's derived pictures from assets/raw/ (crops, and the to-scale comparison). No AI.

- A05: the Khedive's portrait without its print border.
- A11, A13: the left half of a stereo card.
- V1_side_by_side.png: Bartholdi's 1869 Egypt figure (watercolour) beside Liberty drawn from the USGS laser scan,
  both scaled to their real heights: Egypt figure 86 ft (Barry Moreno, via Smithsonian) and Liberty's copper
  figure 151 ft from the top of the base to the torch (NPS). Only the figures are compared, not the pedestals.
Usage: python3 derive.py
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "raw"), os.path.join(HERE, "derived")
sys.path.insert(0, os.path.join(HERE, "..", "..", "toolkit"))
from unbuilt_kit import lidar  # noqa: E402
from unbuilt_kit.core import ACCENT, INK, PAPER, font  # noqa: E402

# measured on the scans (pixels of the originals)
WC_FIGURE = (640, 120, 1070, 1180)       # watercolour: box around the figure, lamp top y=137, feet y=1175
WC_TOP, WC_FEET = 137, 1175
EGYPT_FT, LIBERTY_FT = 86.0, 151.0


def crop(src, box, dst):
    im = Image.open(os.path.join(RAW, src)).convert("RGB")
    w, h = im.size
    im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))).save(os.path.join(OUT, dst), quality=94)


def liberty_side(height_px):
    """The statue alone (above the top of the pedestal), seen from the south-east, from far away so it reads
    almost like an elevation drawing. Returns an RGBA image whose figure is height_px tall."""
    pts = np.load(os.path.join(HERE, "lidar", "liberty_points.npz"))["pts"]
    base_top = pts[:, 2].max() - LIBERTY_FT * 0.3048          # torch tip minus 151 ft
    sel = (np.hypot(pts[:, 0], pts[:, 1]) < 18) & (pts[:, 2] > base_top)
    p = pts[sel]
    d = 900.0
    cam = (d * 0.62, -d * 0.78, base_top + 23)
    img = lidar.render(p, cam, (0, 3, base_top + 23), (900, 1400), fov=3.4, haze=1e9, ss=2, spacing=0.22, max_splat=9)
    a = (np.abs(img - np.asarray(PAPER, np.float32) * np.linspace(0.96, 1.0, 1400)[:, None, None]).sum(2) > 0.06)
    rows, cols = np.where(a)
    img = img[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    alpha = a[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    rgba = np.dstack([np.clip(img, 0, 1) * 255, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    k = height_px / im.height
    return im.resize((max(1, int(im.width * k)), height_px), Image.LANCZOS)


def side_by_side():
    W, H = 1920, 1080
    ground = 930
    lib_h = 760
    egy_h = int(lib_h * EGYPT_FT / LIBERTY_FT)
    card = Image.new("RGB", (W, H), tuple(int(c * 255) for c in PAPER))
    d = ImageDraw.Draw(card)
    wc = Image.open(os.path.join(RAW, "P01_watercolour_1869.png")).convert("RGB").crop(WC_FIGURE)
    k = egy_h / (WC_FEET - WC_TOP)
    wc = wc.resize((int(wc.width * k), int(wc.height * k)), Image.LANCZOS)
    top_in_crop = int((WC_TOP - WC_FIGURE[1]) * k)
    feet_in_crop = int((WC_FEET - WC_FIGURE[1]) * k)
    wc = wc.crop((0, 0, wc.width, feet_in_crop))
    # lift the figure off the painted sky: the sky is light grey-blue (brightness about 130-140), the figure
    # and lamp are dark (40-90), so a soft brightness key separates them
    a = np.asarray(wc, np.float32).mean(2)
    alpha = np.clip((118 - a) / 22, 0, 1)
    mask = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1))
    card.paste(wc, (560 - wc.width // 2, ground - feet_in_crop), mask)
    lib = liberty_side(lib_h)
    card.paste(lib, (1340 - lib.width // 2, ground - lib_h), lib)
    ink, acc = tuple(int(c * 255) for c in INK), tuple(int(c * 255) for c in ACCENT)
    d.line([(300, ground), (1620, ground)], fill=ink, width=3)
    f, fb = font("sans", 34), font("serif", 44, "bold")
    for x, h, name, sub in [(560, egy_h, "Egypt Carrying the Light to Asia", "design, 1869 · 86 ft"),
                            (1340, lib_h, "Liberty Enlightening the World", "1886 · 151 ft")]:
        d.line([(x + 230, ground), (x + 230, ground - h)], fill=acc, width=4)
        for y in (ground, ground - h):
            d.line([(x + 215, y), (x + 245, y)], fill=acc, width=4)
        tw = d.textlength(name, font=fb)
        d.text((x - tw / 2, ground + 28), name, font=fb, fill=ink)
        tw = d.textlength(sub, font=f)
        d.text((x - tw / 2, ground + 80), sub, font=f, fill=acc)
    title = "The figures, drawn to the same scale"
    d.text(((W - d.textlength(title, font=fb)) / 2, 60), title, font=fb, fill=ink)
    card.save(os.path.join(OUT, "V1_side_by_side.png"))


def split_screen():
    """C3: the 1869 watercolour (left) and Liberty today, drawn from the laser scan (right), half a frame each."""
    W, H = 1920, 1080
    card = Image.new("RGB", (W, H), tuple(int(c * 255) for c in PAPER))
    wc = Image.open(os.path.join(RAW, "P01_watercolour_1869.png")).convert("RGB")
    hs = 1600                                           # source height: from above the lamp to the pedestal
    ws = int(hs * (W // 2) / H)
    x0 = 860 - ws // 2                                  # centred on the figure
    card.paste(wc.crop((x0, 40, x0 + ws, 40 + hs)).resize((W // 2, H), Image.LANCZOS), (0, 0))
    pts = np.load(os.path.join(HERE, "lidar", "liberty_points.npz"))["pts"]
    img = lidar.render(pts, (88, -104, 40), (0, 4, 56), (W // 2, H), fov=42, center=(0, 0), radius=450, ss=2,
                       spacing=0.3, haze=4000)
    card.paste(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), (W // 2, 0))
    d = ImageDraw.Draw(card)
    d.line([(W // 2, 0), (W // 2, H)], fill=tuple(int(c * 255) for c in INK), width=4)
    f = font("serif", 46, "bold")
    for x, t in ((W // 4, "1869"), (3 * W // 4, "1886")):
        d.text((x - d.textlength(t, font=f) / 2, 40), t, font=f, fill=tuple(int(c * 255) for c in ACCENT))
    card.save(os.path.join(OUT, "C3_split.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    crop("A05_khedive_ismail.jpg", (0.035, 0.03, 0.965, 0.97), "A05_khedive_ismail.jpg")
    crop("A11_lesseps_statue_matson.jpg", (0.02, 0.02, 0.50, 0.98), "A11_lesseps_statue_matson.jpg")
    crop("A13_suez_inauguration_fleet_1869.png", (0.07, 0.10, 0.50, 0.86), "A13_suez_inauguration_fleet_1869.jpg")
    side_by_side()
    split_screen()
    print("done")


if __name__ == "__main__":
    main()
