#!/usr/bin/env python3
"""Make assets/contact_sheet.jpg: a labelled grid of every image in assets/raw/ listed in rights.csv.

Labels: file name, pixel size, licence. A red "SMALL" tag marks images under 800 px on the long side.
Thumbnails are plain downscales for review only; the originals in raw/ are untouched.
"""
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "contact_sheet.jpg"
CELL_W, CELL_H, LABEL_H, COLS = 300, 300, 46, 7
MAX_BYTES = 2_000_000


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    rows = [r for r in csv.DictReader(open(HERE / "rights.csv", newline="")) if r["file"].lower().endswith((".jpg", ".jpeg", ".png", ".tif"))]
    rows = [r for r in rows if (RAW / r["file"]).exists()]
    n = len(rows)
    nrows = (n + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, 40 + nrows * (CELL_H + LABEL_H)), (245, 243, 238))
    d = ImageDraw.Draw(sheet)
    f_title, f_lab, f_small = font(20), font(12), font(11)
    d.text((10, 10), f"Pilot A (Watkin's Tower): {n} downloaded originals. Red SMALL = under 800 px long side.", fill=(20, 20, 20), font=f_title)
    for i, r in enumerate(rows):
        x = (i % COLS) * CELL_W
        y = 40 + (i // COLS) * (CELL_H + LABEL_H)
        with Image.open(RAW / r["file"]) as im:
            w, h = im.size
            im = ImageOps.exif_transpose(im).convert("RGB")  # display orientation only
            im.thumbnail((CELL_W - 10, CELL_H - 10))
            sheet.paste(im, (x + (CELL_W - im.width) // 2, y + (CELL_H - im.height) // 2))
        lic = r["licence"].split(" (")[0]
        d.text((x + 5, y + CELL_H + 2), r["file"][:44], fill=(0, 0, 0), font=f_lab)
        d.text((x + 5, y + CELL_H + 18), f"{w}x{h}  {lic}"[:48], fill=(60, 60, 60), font=f_small)
        if max(w, h) < 800:
            d.rectangle([x + 5, y + 5, x + 62, y + 22], fill=(200, 0, 0))
            d.text((x + 9, y + 7), "SMALL", fill=(255, 255, 255), font=f_small)
    q = 85
    while True:
        sheet.save(OUT, quality=q, optimize=True)
        if OUT.stat().st_size <= MAX_BYTES or q <= 40:
            break
        q -= 5
    print(f"{OUT.name}: {n} images, {sheet.size[0]}x{sheet.size[1]}, {OUT.stat().st_size/1e6:.2f} MB (q={q})")


if __name__ == "__main__":
    main()
