"""YouTube thumbnail (1280x720): the E1 cup at dawn + 'THE REAL HOT COFFEE CASE'.
python3 thumb.py [path/to/eric_cutout.png]  — a transparent PNG of Eric from the shoot goes on the right;
without one, writes the text-only version plus a layout guide showing where the photo goes."""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gfx
RENDERS = os.environ.get('RENDERS', os.path.join(HERE, '..', 'renders'))
TW, TH = 1280, 720


def base():
    frames = sorted(glob.glob(os.path.join(RENDERS, 'E1', '*.png'))) or sorted(glob.glob(os.path.join(RENDERS, 'preview', 'E1', '*.png')))
    im = Image.open(frames[int(len(frames) * 0.7)]).convert('RGB')
    s = TH * 1.08 / im.height; im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    padl = int(TW * 0.72 - im.width * 0.5)                               # cup lands right of centre
    if padl > 0:
        im = Image.fromarray(np.pad(np.asarray(im), ((0, 0), (padl, 0), (0, 0)), mode='edge'))
    top = int((im.height - TH) * 0.55)
    im = im.crop((0, top, TW, top + TH))
    a = np.asarray(im).astype(np.float32)
    shade = np.clip(1 - np.linspace(0, 1, TW) * 1.9, 0, 1) ** 1.3 * 0.82    # darken the left for the type
    a = a * (1 - shade[None, :, None]) * 1.05
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')


def words(cv):
    S = TW / gfx.W
    put = lambda t, f, sz, c, xy, **k: gfx.put(cv, t, f, int(sz), c, xy, **k)
    put('THE REAL', 'bebas', 140, gfx.WHITE, (56, 70), track=2)
    put('HOT COFFEE', 'bebas', 196, gfx.AMBER, (50, 190), track=2)
    put('CASE', 'bebas', 140, gfx.WHITE, (56, 380), track=2)
    gfx.rect(cv, (60, 560, 120, 566), gfx.AMBER)
    put('THE HOFFMAN FILES', 'monob', 30, gfx.WHITE, (60, 590), track=6)


def main():
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    gfx.W, gfx.H = TW, TH                                               # draw helpers at thumbnail size
    cv = base()
    if len(sys.argv) > 1:
        eric = Image.open(sys.argv[1]).convert('RGBA'); s = TH * 0.98 / eric.height
        eric = eric.resize((int(eric.width * s), int(eric.height * s)), Image.LANCZOS)
        cv.alpha_composite(eric, (TW - eric.width + 40, TH - eric.height))
        words(cv); cv.convert('RGB').save(os.path.join(HERE, 'out', 'thumbnail.jpg'), quality=92); return
    words(cv); cv.convert('RGB').save(os.path.join(HERE, 'out', 'thumbnail_textonly.jpg'), quality=92)
    guide = cv.copy(); d = ImageDraw.Draw(guide)
    for y in range(140, TH, 24): d.line((900, y, 900, y + 12), fill=(236, 140, 52, 255), width=3)
    d.ellipse((990, 120, 1210, 360), outline=(236, 140, 52, 255), width=4)
    d.rounded_rectangle((930, 380, 1270, 760), 60, outline=(236, 140, 52, 255), width=4)
    gfx.put(guide, "ERIC'S CUTOUT HERE", 'monob', 24, gfx.WHITE, (1100, 450), 'c', track=3)
    gfx.put(guide, 'chest-up, looking at the cup', 'mono', 20, gfx.GREY, (1100, 490), 'c')
    guide.convert('RGB').save(os.path.join(HERE, 'out', 'thumbnail_layout_guide.jpg'), quality=92)


if __name__ == '__main__':
    main()
