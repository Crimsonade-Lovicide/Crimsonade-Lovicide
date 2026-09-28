"""Halloween identity for UNBUILT specials: the fanged wordmark, the opening sting and its sound.

Usage: python3 halloween.py <asset_dir>
Writes (no generation credits; everything is drawn and synthesised here):
  <asset_dir>/vid/br_STING.mp4     4 s logo sting: UNBUILT flickers on, fangs drop, HALLOWEEN SPECIAL burns in
  <asset_dir>/audio/t_STING.wav    its sound: low drone, a hit as the fangs drop, a rumble tail
  <asset_dir>/halloween_logo.png   the finished logo as a still (for the thumbnail, socials, review)
Fonts: Anton and Bebas Neue (SIL OFL), looked for in $FONTS, default <asset_dir>/../thumb.
assemble.py imports wordmark() for the title card.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1280, 720, 24
ORANGE = (255, 122, 26)
IVORY = (244, 238, 226)
BLOOD = (138, 10, 16)
BG = (11, 8, 6)


def fonts(a):
    d = os.environ.get("FONTS", os.path.join(a, "..", "thumb"))
    return os.path.join(d, "Anton-Regular.ttf"), os.path.join(d, "BebasNeue-Regular.ttf")


def spaced_width(draw, text, font, gap):
    return sum(draw.textlength(c, font=font) + gap for c in text) - gap


def draw_spaced(draw, x, y, text, font, fill, gap):
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + gap


def fang(length, width):
    """An RGBA canine: broad at the root, curving to a point that leans inward, shaded toward the edges."""
    w, h = int(width) + 4, int(length) + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tip = 0.64 * width
    left = [(2 + tip * t ** 1.35, 2 + length * t) for t in np.linspace(0, 1, 24)]
    right = [(2 + width - (width - tip) * t ** 0.75, 2 + length * t) for t in np.linspace(1, 0, 24)]
    mask = Image.new("L", (w * 4, h * 4), 0)  # supersampled for a clean edge
    ImageDraw.Draw(mask).polygon([(x * 4, y * 4) for x, y in left + right], fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    xs = np.linspace(-1, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    lum = 1 - 0.30 * xs ** 2 - 0.10 * ys
    shade = np.zeros((h, w, 4), np.uint8)
    for c in range(3):
        shade[..., c] = np.clip(IVORY[c] * lum, 0, 255)
    shade[..., 3] = np.asarray(mask)
    return Image.fromarray(shade, "RGBA")


def wordmark(a, scale=1.0, fang_drop=1.0, sub="HALLOWEEN SPECIAL", sub_alpha=1.0, word_alpha=1.0):
    """The logo on a transparent canvas. Returns (image, fang tip positions)."""
    anton, bebas = fonts(a)
    big = ImageFont.truetype(anton, int(172 * scale))
    small = ImageFont.truetype(bebas, int(62 * scale))
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    word, gap = "UNBUILT", int(16 * scale)
    ww = spaced_width(d, word, big, gap)
    x0, y0 = (W - ww) / 2, H * 0.36 - 118 * scale
    bbox = d.textbbox((0, 0), "U", font=big)
    base = y0 + bbox[3]  # bottom of the letters: the fangs hang from here
    tips = []
    if fang_drop > 0:
        # canines hang from the B and the I, which sit either side of the middle U
        lefts, x = [], x0
        for c in word:
            lefts.append((x, x + d.textlength(c, font=big)))
            x += d.textlength(c, font=big) + gap
        L, fw = 104 * scale * fang_drop, 50 * scale
        for j, cx in ((0, (lefts[2][0] + lefts[2][1]) / 2), (1, (lefts[4][0] + lefts[4][1]) / 2)):
            f = fang(max(L, 2), fw)
            if j == 1:
                f = f.transpose(Image.FLIP_LEFT_RIGHT)
            im.alpha_composite(f, (int(cx - fw / 2), int(base - 8 * scale)))
            lean = 0.14 * fw
            tips.append((cx + (lean if j == 0 else -lean), base - 8 * scale + L))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_spaced(ImageDraw.Draw(txt), x0, y0, word, big, IVORY + (int(255 * word_alpha),), gap)
    im.alpha_composite(txt)
    if sub and sub_alpha > 0:
        g2 = int(14 * scale)
        sw = spaced_width(d, sub, small, g2)
        sy = base + 138 * scale
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_spaced(ImageDraw.Draw(layer), (W - sw) / 2, sy, sub, small, ORANGE + (255,), g2)
        glow = layer.filter(ImageFilter.GaussianBlur(14 * scale))
        for _ in range(2):
            im.alpha_composite(Image.fromarray((np.asarray(glow).astype(float) * [1, 1, 1, sub_alpha * 0.9]).astype(np.uint8)))
        im.alpha_composite(Image.fromarray((np.asarray(layer).astype(float) * [1, 1, 1, sub_alpha]).astype(np.uint8)))
        # thin orange rules either side of the subtitle
        ry = sy + 34 * scale
        rl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rl)
        for x1, x2 in (((W - sw) / 2 - 90 * scale, (W - sw) / 2 - 26 * scale),
                       ((W + sw) / 2 + 26 * scale, (W + sw) / 2 + 90 * scale)):
            rd.rectangle([x1, ry, x2, ry + 2 * scale], fill=ORANGE + (int(255 * sub_alpha),))
        im.alpha_composite(rl)
    return im, tips


def background(t, rng, fog):
    """Near-black with a low orange glow and slow drifting fog."""
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * 0.6)) ** 2 + ((y - H * 1.05) / (H * 0.75)) ** 2)
    flick = 0.85 + 0.15 * math.sin(t * 9.1) * math.sin(t * 3.7 + 1)
    glow = np.clip(1 - r, 0, 1) ** 2 * 0.22 * flick
    img = np.zeros((H, W, 3))
    img[:] = BG
    img += glow[..., None] * np.array(ORANGE)
    sh = int(t * 38) % fog.shape[1]
    f = np.roll(fog, -sh, axis=1)[:, :W]
    img += f[..., None] * np.array([70, 60, 55])
    img += rng.normal(0, 5, (H, W, 1))  # film grain
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def drop(im, x, y, r):
    d = ImageDraw.Draw(im)
    d.ellipse([x - r, y - r * 0.6, x + r, y + r * 1.4], fill=BLOOD + (255,))
    d.polygon([(x - r * 0.7, y), (x + r * 0.7, y), (x, y - r * 2.2)], fill=BLOOD + (255,))


def ease_out_back(u):
    c = 1.9
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def sting(a, dur=4.0):
    rng = np.random.default_rng(31)
    small = rng.random((18, 64 * 2))
    fog = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((W * 2, H), Image.BICUBIC)
                     .filter(ImageFilter.GaussianBlur(40))).astype(float) / 255
    fog = np.clip(fog - 0.45, 0, 1) * 0.35 * np.linspace(0.2, 1, H)[:, None]
    flicker = {10: 1, 11: 0, 12: 0.8, 13: 0, 14: 0, 15: 1, 16: 0.3, 17: 1}  # frame -> word alpha, a lamp striking
    out = os.path.join(a, "vid", "br_STING.mp4")
    ff = os.environ.get("FFMPEG", "ffmpeg")
    p = subprocess.Popen([ff, "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(dur * FPS)
    drop_y, drop_v = None, 0.0
    for i in range(n):
        t = i / FPS
        frame = background(t, rng, fog)
        wa = flicker.get(i, 1.0 if i > 17 else 0.0)
        fd = 0.0 if t < 1.2 else min(1.0, ease_out_back(min(1.0, (t - 1.2) / 0.28)))
        sa = 0.0 if t < 1.55 else min(1.0, (t - 1.55) / 0.6)
        logo, tips = wordmark(a, fang_drop=fd, sub_alpha=sa, word_alpha=wa)
        frame.alpha_composite(logo)
        if tips and t > 1.9:  # a drop of blood gathers on the left fang, then falls
            tx, ty = tips[0]
            grow = min(1.0, (t - 1.9) / 0.7)
            if t < 2.6:
                y = ty
            else:
                drop_v += 2200 / FPS
                drop_y = (ty if drop_y is None else drop_y) + drop_v / FPS
                y = drop_y
            drop(frame, tx, y, 3 + 5 * grow)
        if t > dur - 0.5:  # fade to black into the cold open
            k = (dur - t) / 0.5
            frame = Image.fromarray((np.asarray(frame.convert("RGB")).astype(float) * k).astype(np.uint8)).convert("RGBA")
        p.stdin.write(frame.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    return out


def sound(a, dur=4.0, sr=48000):
    """Drone, a heavy hit on the fang drop (1.2 s), a rumble tail. Synthesised, so no licence question."""
    t = np.arange(int(dur * sr)) / sr
    rng = np.random.default_rng(7)
    drone = (np.sin(2 * np.pi * 43 * t) + 0.5 * np.sin(2 * np.pi * 64.5 * t + 1)) * np.clip(t / 1.2, 0, 1) * 0.10
    noise = rng.normal(0, 1, len(t))
    k = np.exp(-np.arange(int(0.004 * sr)) / (0.0015 * sr))
    dark = np.convolve(noise, k / k.sum(), "same")  # a crude low-pass
    hit_t = np.clip(t - 1.2, 0, None)
    on = t >= 1.2
    boom = on * np.sin(2 * np.pi * (60 * hit_t - 12 * hit_t ** 2)) * np.exp(-hit_t / 0.55) * 0.75
    crack = on * noise * np.exp(-hit_t / 0.03) * 0.25
    rumble = on * dark * np.exp(-hit_t / 1.1) * 1.4
    y = drone + boom + crack + rumble
    y *= np.clip((dur - t) / 0.5, 0, 1)  # fade with the picture
    y = y / (np.abs(y).max() + 1e-9) * 0.7
    st = (np.stack([y, y], 1) * 32767).astype(np.int16)
    out = os.path.join(a, "audio", "t_STING.wav")
    w = wave.open(out, "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(st.tobytes())
    w.close()
    return out


if __name__ == "__main__":
    A = sys.argv[1]
    logo, tips = wordmark(A)
    still = background(2.0, np.random.default_rng(1), np.zeros((H, W * 2)))
    still.alpha_composite(logo)
    drop(still, tips[0][0], tips[0][1] + 4, 8)
    still.convert("RGB").save(os.path.join(A, "halloween_logo.png"))
    print(sting(A), sound(A))
