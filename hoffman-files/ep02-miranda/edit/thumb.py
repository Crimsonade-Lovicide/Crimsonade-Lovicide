"""Ep. 2 YouTube thumbnail (1280x720): Interrogation Room No. 2 (M3, first frame) with Eric keyed off the Mac's blue
Background effect, and the hook in the house type. The frame of Eric is 12.5 s into oc_1021_a.mov (mouth closed, eyes
to the lens); grab it with ffmpeg -ss 12.5 -i takes/oc_1021_a.mov -frames:v 1 eric.jpg.
  python3 thumb.py <eric_frame.jpg> <room_frame.png> <out.jpg>      e.g. ../renders/M3/0001.png ../thumbnail.jpg"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gfx2 as gfx                                   # ep. 1 helpers and colours come through gfx2
TW, TH = 1280, 720


def key_blue(im):
    """Alpha matte for the Mac 'Background' blue: hue in the blue band, saturated, not dark. Holes closed, edge
    feathered, blue spill pulled off the edge pixels."""
    rgb0 = np.asarray(im.convert('RGB')).astype(np.int32)
    r, g, b = rgb0[..., 0], rgb0[..., 1], rgb0[..., 2]
    v = rgb0.max(axis=2)
    bg = ((b - np.maximum(r, g)) > 16) & (v > 70)        # the backdrop runs saturated blue to pale blue; skin, hair and the polo never go blue
    m = Image.fromarray((~bg).astype(np.uint8) * 255)
    m = m.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))          # open: drop blue specks in him
    m = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))          # close: fill specks in him
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))     # choke a hair, then feather
    a = np.asarray(m).astype(np.float32) / 255
    rgb = np.asarray(im.convert('RGB')).astype(np.float32)
    edge = (a > 0.02) & (a < 0.98)
    b = rgb[..., 2]; lim = np.maximum(rgb[..., 0], rgb[..., 1])
    rgb[..., 2] = np.where(edge, np.minimum(b, lim), b)                              # despill
    out = np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def main(eric_path, room_path, out):
    gfx.W, gfx.H = TW, TH
    room = Image.open(room_path).convert('RGB')
    s = TH / room.height; room = room.resize((int(room.width * s), TH), Image.LANCZOS)
    room = room.crop(((room.width - TW) // 2, 0, (room.width - TW) // 2 + TW, TH))
    a = np.asarray(room).astype(np.float32)
    shade = np.clip(1 - np.linspace(0, 1, TW) * 1.7, 0, 1) ** 1.2 * 0.78              # darken the left for the type
    a = a * (1 - shade[None, :, None]) * 0.92
    cv = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')

    src = Image.open(eric_path).convert('RGB'); w, h = src.size
    src = src.crop((int(w * 0.22), int(h * 0.12), int(w * 0.78), int(h * 0.84)))      # chest-up, above the mic
    eric = key_blue(src)
    s = TH * 1.02 / eric.height
    eric = eric.resize((int(eric.width * s), int(eric.height * s)), Image.LANCZOS)
    x = TW - eric.width + 60; y = TH - eric.height + 10
    # a soft dark halo so he separates from the lamp side of the room
    halo = Image.new('RGBA', cv.size, (0, 0, 0, 0)); halo.paste((0, 0, 0, 150), (x, y), eric.split()[3])
    halo = halo.filter(ImageFilter.GaussianBlur(28)); cv.alpha_composite(halo)
    cv.alpha_composite(eric, (x, y))

    put = lambda t, f, sz, c, xy, **k: gfx.put(cv, t, f, int(sz), c, xy, **k)
    put('THE RIGHT TO REMAIN SILENT', 'monob', 28, gfx.GREY, (58, 62), track=5)
    put('MIRANDA', 'bebas', 214, gfx.AMBER, (50, 110), track=2)
    put('CONVICTED', 'bebas', 132, gfx.WHITE, (56, 330), track=2)
    put('ANYWAY', 'bebas', 132, gfx.WHITE, (56, 462), track=2)
    gfx.rect(cv, (60, 626, 120, 632), gfx.AMBER)
    put('THE HOFFMAN FILES', 'monob', 28, gfx.WHITE, (60, 650), track=6)
    cv.convert('RGB').save(out, quality=93)
    eric.save(out.replace('.jpg', '_cutout.png'))
    print(out, os.path.getsize(out))


if __name__ == '__main__':
    main(*sys.argv[1:4])
