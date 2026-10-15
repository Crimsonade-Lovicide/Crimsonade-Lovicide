"""Thumbnails for "Monuments to the Dead", in the episode 1 style (two-line Anton headline, Hugo cut out on
the right) with the Halloween palette: orange second line and the fanged UNBUILT HALLOWEEN SPECIAL badge.

Usage (from a folder holding the fonts): python3 make_thumb.py <asset_dir>
Needs rembg (u2net_human_seg) for the Hugo cutout.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from rembg import new_session, remove

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "edit"))
import halloween  # noqa: E402

A = sys.argv[1]
W, H = 1280, 720
ORANGE = (255, 122, 26)
FONTS = os.environ.get("FONTS", os.path.join(A, "..", "thumb"))
sess = new_session("u2net_human_seg")


def cutout(path, warm=1.0):
    cut = remove(Image.open(path).convert("RGB"), session=sess)
    # the moon sits right behind his head in the O2 frame and the matte takes it: clear pale, unsaturated
    # pixels in the top of the cutout (hair is dark, skin is saturated)
    arr = np.asarray(cut).copy()
    top = int(arr.shape[0] * 0.30)
    rgb = arr[:top, :, :3].astype(float)
    lum, sat = rgb.mean(2), (rgb.max(2) - rgb.min(2)) / (rgb.max(2) + 1)
    arr[:top, :, 3][(lum > 105) & (sat < 0.22)] = 0
    cut = Image.fromarray(arr)
    # pull the matte edge in by 2 px so no pale fringe of sky is left around the hair
    a = cut.split()[3].filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1))
    cut.putalpha(a)
    cut = cut.crop(cut.getbbox())
    # drop his lantern hand (the matte keeps the hand but not the lantern): keep the left 66% and let the
    # cut edge sit on the frame edge
    cut = cut.crop((0, 0, int(cut.width * 0.66), cut.height))
    if warm != 1.0:
        r, g, b, a = cut.split()
        r = r.point(lambda v: min(255, int(v * warm)))
        b = b.point(lambda v: int(v / warm))
        rgb = ImageEnhance.Brightness(Image.merge("RGB", (r, g, b))).enhance(1.12)
        cut = Image.merge("RGBA", (*rgb.split(), a))
    return cut


def background(path, crop, glow=False, lift=1.0):
    bg = Image.open(path).convert("RGB")
    w, h = bg.size
    bg = bg.crop([int(v) for v in (crop[0] * w, crop[1] * h, crop[2] * w, crop[3] * h)]).resize((W, H), Image.LANCZOS)
    bg = ImageEnhance.Brightness(bg).enhance(lift)
    bg = ImageEnhance.Contrast(bg).enhance(1.18)
    bg = ImageEnhance.Color(bg).enhance(1.2)
    if glow:  # a low pumpkin-orange glow from below, for the night version
        y = np.linspace(0, 1, H)[:, None, None]
        arr = np.asarray(bg).astype(float) + (y ** 2.2) * np.array(ORANGE) * 0.28
        bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    shade = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(shade)
    for x in range(W):  # darken toward Hugo on the right
        d.line([(x, 0), (x, H)], fill=int(max(0, (x - W * 0.55) / (W * 0.45)) * 110))
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.25, -H * 0.35, W * 1.25, H * 1.35), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    bg = Image.composite(bg, Image.new("RGB", (W, H)), vig.point(lambda v: int(90 + v * 165 / 255)))
    return Image.composite(Image.new("RGB", (W, H)), bg, shade)


def headline(img, lines, x, y, size):
    f = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), size)
    d = ImageDraw.Draw(img)
    for txt, col in lines:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x + 6, y + 8), txt, font=f, fill=(0, 0, 0, 170))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d.text((x, y), txt, font=f, fill=col, stroke_width=7, stroke_fill=(0, 0, 0))
        y += int(size * 1.02)


def badge(img):
    """The fanged wordmark, small, bottom left, on a soft dark plate."""
    os.environ["FONTS"] = FONTS
    logo, tips = halloween.wordmark(A, scale=0.34)
    halloween.drop(logo, tips[0][0], tips[0][1] + 2, 3)
    logo = logo.crop(logo.getbbox())
    x, y = 40, H - logo.height - 30
    plate = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle([x - 16, y - 12, x + logo.width + 16, y + logo.height + 12], 10,
                                            fill=(0, 0, 0, 150))
    img.alpha_composite(plate.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(logo, (x, y))


def build(bgpath, crop, hugo, lines, out, size=118, hugo_h=760, glow=False, lift=1.0):
    img = background(bgpath, crop, glow, lift).convert("RGBA")
    cut = cutout(hugo, 1.06)
    s = hugo_h / cut.height
    cut = cut.resize((int(cut.width * s), hugo_h), Image.LANCZOS)
    x, y = W - cut.width, H - cut.height + int(hugo_h * 0.06)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", cut.size, (0, 0, 0, 200)), (x - 10, y + 6), cut.split()[3].filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(shadow)
    img.alpha_composite(cut, (x, y))
    headline(img, lines, 46, 34, size)
    badge(img)
    img.convert("RGB").save(out, quality=92)
    print(out)


hugo = os.path.join(A, "thumb", "o2_4.8.png")
build(os.path.join(A, "img", "CO6_f.png"), (0.02, 0.10, 0.70, 0.98), hugo,
      [("A PYRAMID FOR", (255, 255, 255)), ("5 MILLION DEAD", ORANGE)], "thumbnail_A_night-pyramid.jpg", glow=True,
      lift=1.45)
build(os.path.join(A, "img", "Y3_f.png"), (0.0, 0.0, 0.86, 1.0), hugo,
      [("LONDON NEARLY", (255, 255, 255)), ("BUILT THIS", ORANGE)], "thumbnail_B_pyramid-vs-st-pauls.jpg")
