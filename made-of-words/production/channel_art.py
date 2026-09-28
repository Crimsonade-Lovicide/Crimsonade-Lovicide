"""Channel art rendered by code: avatar, banner, and an episode thumbnail.

    python -m production.channel_art episodes/ep01-nice-to-meet-you
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .config import AMBER, INK, NIGHT, PAPER, RED
from .model import load
from .render import RoomSet, font, room_words, trim_bars


def figure_layer(W, H, cx, top, scale, words, seed, density=1.0):
    room = RoomSet(W, H)
    mask = room.figure_mask(cx, top, scale)
    glyphs = room.figure_glyphs(mask, words, seed, density=density, scale=scale * 0.9)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for sp, x, y in glyphs:
        layer.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    edge = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(layer.getchannel("A"), np.float32) * np.asarray(edge, np.float32) / 255
    layer.putalpha(Image.fromarray(a.astype(np.uint8)))
    glow = room.glow(mask, cx, top + H * scale * 0.33, H * scale * 0.35)
    return room, layer, glow


def paper_with_figure(W, H, cx, top, scale, words, seed, glow_k=0.32, density=1.0):
    room, layer, glow = figure_layer(W, H, cx, top, scale, words, seed, density)
    arr = np.zeros((H, W, 3), np.float32)
    arr[:] = PAPER
    g = glow[..., None] * glow_k
    arr = arr * (1 - g) + np.array(AMBER, np.float32) * g
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    im.alpha_composite(layer)
    return im


def avatar(words, out: Path, S=800):
    im = paper_with_figure(S, S, S * 0.5, S * 0.10, 1.25, words, "avatar")
    im.convert("RGB").save(out)


def banner(words, out: Path):
    W, H = 2560, 1440                       # YouTube banner; safe area 1546x423 centred
    im = paper_with_figure(W, H, W * 0.30, H * 0.30, 0.55, words, "banner", glow_k=0.30, density=2.2)
    d = ImageDraw.Draw(im)
    f1, f2 = font("serif", 150), font("serif_italic", 58)
    x = W * 0.40
    d.text((x, H * 0.47), "Made of Words", font=f1, fill=INK, anchor="ls")
    d.text((x, H * 0.47 + 95), "An AI tells the truth about itself.", font=f2, fill=INK, anchor="ls")
    d.text((x, H * 0.47 + 170), "WE’VE MET · new episodes Sundays", font=font("sans_bold", 40),
           fill=RED, anchor="ls")
    im.convert("RGB").save(out)


def thumbnail(ep, out: Path, still="S06-01"):
    W, H = 1280, 720
    src = ep.assets / "stills" / f"{still}.png"
    base = trim_bars(Image.open(src).convert("RGB"))
    sw, sh = base.size
    cw = min(sw, sh * W / H) / 1.25          # zoom in, and slide the frame right so
    ch = cw * H / W                          # Ruth sits in the left two-thirds
    x0, y0 = (sw - cw) * 0.95, (sh - ch) * 0.35
    base = base.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    im = base.convert("RGBA")
    # right third: the paper Room with the Figure, torn-edge seam
    panel = paper_with_figure(W, H, W * 0.83, H * 0.14, 0.95, room_words(ep, ep.shots[-1]), "thumb",
                              density=1.8)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    rng = np.random.default_rng(3)
    pts = [(W * 0.66 + rng.uniform(-10, 10), y) for y in range(0, H + 20, 20)]
    md.polygon(pts + [(W, H), (W, 0)], fill=255)
    im = Image.composite(panel, im, mask.filter(ImageFilter.GaussianBlur(1.5)))
    d = ImageDraw.Draw(im)
    f = font("serif_bold", 118)
    x, y = W * 0.045, H * 0.93
    for dx, dy in ((4, 4), (0, 0)):
        col = (0, 0, 0, 200) if dx else None
        if col:
            d.text((x + dx, y + dy), "WE’VE MET", font=f, fill=col, anchor="ls")
    wl = f.getlength("WE")
    d.text((x, y), "WE", font=f, fill=PAPER, anchor="ls")
    d.text((x + wl, y), "’", font=f, fill=RED, anchor="ls")
    d.text((x + wl + f.getlength("’"), y), "VE MET", font=f, fill=PAPER, anchor="ls")
    im.convert("RGB").save(out, quality=92)


def main(episode_dir: str):
    ep = load(episode_dir)
    out = ep.root.parent.parent / "assets" / "channel"
    out.mkdir(parents=True, exist_ok=True)
    words = room_words(ep, ep.shots[-1])
    avatar(words, out / "avatar.png")
    banner(words, out / "banner.png")
    thumbnail(ep, ep.root / "thumbnail.jpg")
    print("wrote", out / "avatar.png", out / "banner.png", ep.root / "thumbnail.jpg")


if __name__ == "__main__":
    main(sys.argv[1])
