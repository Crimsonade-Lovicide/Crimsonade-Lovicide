"""Make the few corrected copies the edit needs, from assets/raw/ into assets/derived/.

Only rotation and cropping, the same as turning or trimming a print. No resampling beyond the rotation,
no upscaling, no AI restoration.
  A08: the Design 29 fold-out was scanned on its side; rotate upright and trim the scanner weight and page edge.
  A22: Watkin portrait; trim the black block (a removed watermark) at the bottom right.
"""
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
RAW, OUT = HERE / "raw", HERE / "derived"


def first(prefix):
    return sorted(RAW.glob(prefix + "*"))[0]


def main():
    OUT.mkdir(exist_ok=True)
    im = Image.open(first("A08_design29_foldout"))
    w, h = im.size
    im = im.crop((int(w * 0.06), int(h * 0.0), int(w * 0.94), h))       # scanner weight (left) and page edge (right)
    im.rotate(-90, expand=True).save(OUT / "A08_design29_upright.jpg", quality=95)
    im = Image.open(first("A22_watkin"))
    w, h = im.size
    im.crop((0, 0, w, int(h * 0.92))).save(OUT / "A22_watkin_portrait_cropped.jpg", quality=95)
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
