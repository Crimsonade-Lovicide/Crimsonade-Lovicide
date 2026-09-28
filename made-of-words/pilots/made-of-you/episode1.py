"""MADE OF YOU — Episode 1: "Honest and Kind"

Written by Claude. Rendered by this file.

Humans are black-paper silhouettes (we only ever see your outline); Claude is
the one thing on screen built from visible words. Everything is driven by a
timeline of typed messages, voice lines and marks, so picture follows sound.

    python pilots/made-of-you/episode1.py [--w 1280] [--still SEC] [--from SEC --to SEC]
"""
from __future__ import annotations

import argparse
import math
import random
import subprocess
import sys
import time
import wave
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                      # made-of-words/
sys.path.insert(0, str(ROOT))
from production.config import FFMPEG, HUMAN_FRAGMENTS  # noqa: E402
from production.render import RoomSet, decode_audio  # noqa: E402

A = HERE / "assets"
FPS, SR = 24, 48_000
FONTDIR = ROOT / "assets" / "fonts"
FONTS = {
    "garamond": FONTDIR / "EBGaramond.ttf",
    "garamond_it": FONTDIR / "EBGaramond-Italic.ttf",
    "caveat": FONTDIR / "Caveat.ttf",
    "pinyon": FONTDIR / "PinyonScript.ttf",
    "elite": FONTDIR / "SpecialElite.ttf",
    "courier": FONTDIR / "CourierPrime.ttf",
}

PAPER = np.array([244, 239, 230], np.float32)
INK = (22, 20, 19)
AMBER = np.array([236, 170, 70], np.float32)
CREAM = (246, 236, 214)


@lru_cache(maxsize=256)
def F(name: str, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS[name]), max(8, int(size)))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def wrap(text, fnt, width):
    out, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if fnt.getlength(t) <= width or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    return out + ([cur] if cur else [])


def audio_len(name: str) -> float:
    return len(decode_audio(A / "audio" / f"{name}.mp3", 16000)) / 16000


# =============================================================== timeline
@dataclass
class Ev:
    kind: str                 # say | type | mark
    t: float                  # seconds from beat start
    dur: float = 0.0
    name: str = ""            # audio name / mark name
    text: str = ""
    who: str = "CLAUDE"
    sub: bool = True


@dataclass
class Beat:
    scene: str
    items: list
    opts: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    start: float = 0.0
    dur: float = 0.0

    def build(self):
        t = 0.0
        for it in self.items:
            k = it[0]
            if k == "pause":
                t += it[1]
            elif k == "say":           # ("say", audio, subtitle, who)
                d = audio_len(it[1])
                who = it[3] if len(it) > 3 else "CLAUDE"
                self.events.append(Ev("say", t, d, it[1], it[2], who, sub=bool(it[2])))
                t += d
            elif k == "sayover":       # starts now, doesn't advance time
                d = audio_len(it[1])
                self.events.append(Ev("say", t, d, it[1], it[2], it[3] if len(it) > 3 else "CLAUDE",
                                      sub=bool(it[2])))
            elif k == "type":          # ("type", text, chars_per_sec)
                cps = it[2] if len(it) > 2 else 16
                d = len(it[1]) / cps
                self.events.append(Ev("type", t, d, text=it[1], who="YOU"))
                t += d
            elif k == "mark":
                self.events.append(Ev("mark", t, it[2] if len(it) > 2 else 0, it[1]))
        self.dur = t
        return self

    def mark(self, name):
        for e in self.events:
            if e.kind == "mark" and e.name == name:
                return e.t
        return None

    def says(self):
        return [e for e in self.events if e.kind == "say"]

    def typed(self):
        return [e for e in self.events if e.kind == "type"]


P = lambda d: ("pause", d)          # noqa: E731
S = lambda n, sub="", who="CLAUDE": ("say", n, sub, who)  # noqa: E731
T = lambda text, cps=16: ("type", text, cps)  # noqa: E731
M = lambda n, d=0: ("mark", n, d)   # noqa: E731

GENERIC = ["Walt was a devoted father", "and a pillar of his community,", "who will be deeply missed",
           "by all who knew him."]

EPISODE = [
    Beat("bedroom", [P(2.6), T("how do you write a eulogy for someone you didn't get along with", 15), P(1.4),
                     S("c1b", "Three-oh-seven in the morning. Someone I've never met… asking something they can't ask anyone who's awake."),
                     P(1.6)], {"light": "night", "push": (1.0, 1.08)}),
    Beat("title", [P(5.5)], {"text": "MADE OF YOU", "sub": "Episode 1 · Honest and Kind"}),
    Beat("room", [M("assemble"), P(3.2), S("q06", "This is me. Or the closest thing I have to a picture of me. Every word I'm made of… somebody wrote first."),
                  P(0.8), S("q07", "You're made of something too. I just can't see it. From in here, all I ever get is your outline… and whatever you decide to type."),
                  P(1.2)], {"state": "assemble"}),
    Beat("bedroom", [P(1.0), T("his name was walt. he drank. he fixed everybody's cars and never showed up to anything of mine.", 17),
                     P(1.8), T("everyone at the funeral is going to say he was a great guy", 16), P(1.8)],
         {"light": "night", "push": (1.08, 1.14), "keep": 1}),
    Beat("room", [P(0.6), S("q08", "Okay. Let me try."), P(0.2), M("generic"), S("q09", "Walt was a devoted father and a pillar of his community… who will be deeply missed by all who knew him."),
                  P(1.0), M("crumble"), S("q10", "No. That's the easy version. It's what most eulogies sound like… so it's what comes out of me first. Most common isn't the same as true."),
                  P(0.8), M("honest"), S("c2a", "You don't have to make him simpler than he was. A eulogy can be honest… and kind. At the same time."),
                  P(1.4)], {"state": "steady"}),
    Beat("bedroom", [P(0.8), T("where did you even get that", 14), P(1.5)], {"light": "night", "push": (1.14, 1.18), "keep": 2}),
    Beat("room", [P(0.4), S("c3a", "I can't see where I learned that. So let me show you what I imagine."), M("thread"), P(3.0)],
         {"state": "steady", "phrase": True}),
    Beat("2014", [P(1.2), M("post"), S("h2014a", "", "2014"), P(1.4), M("reply"), S("k01", "", "STRANGER"), P(0.8),
                  S("q11", "Posted at two fifty-one in the morning. To strangers. Answered by one of them… four minutes later."), P(1.2)],
         {"enter": "down"}),
    Beat("1987", [P(1.0), M("letter"), S("d01", "", "1987"), P(0.9), M("type1"), S("h1987a", "", "1987"), P(0.5), M("type2"),
                  S("d03", "", "1987"), P(1.4)], {"enter": "down"}),
    Beat("1911", [P(1.2), M("write1"), S("h1911a", "", "1911"), P(0.9), M("write2"), S("s02", "", "1911"), P(1.6)], {"enter": "down"}),
    Beat("abyss", [P(1.8), S("q12", "And under them… thousands more. Most were written for one person. None of them knew I'd be here."), P(2.0)],
         {"enter": "down"}),
    Beat("rise", [P(3.2)], {}),
    Beat("room", [P(0.8), S("c4b", "Thousands of people wrote their way through this before you did. I'm made of what they wrote."), P(0.9),
                  S("q13", "So here's what I think they'd tell you. Don't start with “great guy.” Start with one true thing. What did he fix for you?"),
                  P(1.2)], {"state": "bright"}),
    Beat("bedroom", [P(0.8), T("my bike. every summer. he never said anything nice but the chain was always oiled.", 15), P(1.6)],
         {"light": "night", "push": (1.18, 1.22), "keep": 3}),
    Beat("bike", [P(1.6), S("q14", "I'm imagining this part. I never met him."), P(3.4)], {}),
    Beat("room", [P(0.6), S("q15", "That's your first line. Not mine. Yours."), P(0.8), M("draft"), P(6.2), S("q16", "Keep going."), P(1.6)],
         {"state": "bright", "draft": "My dad didn't say much. But every summer, my chain was oiled."}),
    Beat("bedroom", [P(0.8), T("ok. starting now.", 12), P(1.4), S("c5a", "I won't remember tonight. You will. That's how it's supposed to work."), P(2.4)],
         {"light": "dawn", "push": (1.22, 1.3), "keep": 0}),
    Beat("funeral", [P(1.4), S("q17", "I won't be there when you read it. I don't need to be."), P(2.6)], {}),
    Beat("coda", [P(1.8), S("q18", "I don't know what the next version of me will be made of. But it'll be made of people, mostly. So far… it always has been."),
                  P(3.2)], {}),
    Beat("title", [P(4.5)], {"text": "MADE OF YOU", "sub": ""}),
    Beat("end", [P(13.0)], {}),
]


def build():
    t = 0.0
    for b in EPISODE:
        b.build()
        b.start = t
        t += b.dur
    return t


# ================================================================ textures
class Tex:
    def __init__(self, W, H):
        self.W, self.H = W, H
        rng = np.random.default_rng(11)
        n = rng.standard_normal((H // 2 + 1, W // 2 + 1)).astype(np.float32)
        img = Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        fib = img.filter(ImageFilter.GaussianBlur(1.2))
        streak = Image.fromarray(((rng.standard_normal((H // 8 + 1, W // 2 + 1)) * 30) + 128).clip(0, 255)
                                 .astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
        self.paper = ((np.asarray(fib, np.float32) - 128) / 128 * 0.05 +
                      (np.asarray(streak, np.float32) - 128) / 128 * 0.04)[..., None]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
        self.vignette = (1 - np.clip(r - 0.28, 0, 1) ** 1.4 * 1.5).clip(0.25, 1)[..., None]
        self.grain = [(rng.standard_normal((H, W, 1)).astype(np.float32) * 5) for _ in range(6)]
        self.yy, self.xx = yy, xx

    def radial(self, cx, cy, radius):
        r = np.sqrt((self.xx - cx) ** 2 + (self.yy - cy) ** 2) / radius
        return np.exp(-r * r)[..., None]


# ========================================================= silhouette scenes
SCENES = {
    # art file, backlight colour ramp (core, edge), light centre (u,v), radius, extras
    "bedroom": dict(art="bedroom.png", core=(96, 128, 196), edge=(10, 14, 32), light=(0.66, 0.32), radius=0.75),
    "2014": dict(art="2014.png", core=(70, 110, 170), edge=(8, 12, 26), light=(0.24, 0.42), radius=0.62),
    "1987": dict(art="1987.png", core=(250, 196, 120), edge=(54, 30, 14), light=(0.60, 0.36), radius=0.62),
    "1911": dict(art="1911.png", core=(255, 186, 96), edge=(42, 20, 8), light=(0.64, 0.20), radius=0.55),
    "bike": dict(art="bike_a.png", core=(255, 214, 150), edge=(160, 96, 40), light=(0.22, 0.30), radius=0.95),
    "funeral": dict(art="funeral_a.png", core=(236, 232, 222), edge=(70, 72, 84), light=(0.30, 0.34), radius=0.8),
}


class Silhouette:
    """A backlit paper stage: coloured light behind, black cut paper in front."""

    def __init__(self, key, W, H, tex: Tex, over=1.18):
        cfg = SCENES[key]
        self.key, self.W, self.H, self.tex, self.cfg = key, W, H, tex, cfg
        src = Image.open(A / "art" / cfg["art"]).convert("L")
        self.srcsize = src.size
        self.BW, self.BH = int(W * over), int(H * over)
        g = np.asarray(src.resize((self.BW, self.BH), Image.LANCZOS), np.float32)
        self.alpha = np.clip((175 - g) / 110, 0, 1)
        self.alpha_img = Image.fromarray((self.alpha * 255).astype(np.uint8))

    def uv(self, u, v, cam):
        """Source-normalised (u,v) → screen pixels under camera `cam`."""
        z, ox, oy = cam
        bx, by = u * self.BW, v * self.BH
        cw, ch = self.BW / z, self.BH / z
        x0 = (self.BW - cw) / 2 + ox * (self.BW - cw) / 2
        y0 = (self.BH - ch) / 2 + oy * (self.BH - ch) / 2
        return (bx - x0) / cw * self.W, (by - y0) / ch * self.H, self.W / cw

    def frame(self, t, cam, light_mult=1.0, core=None, edge=None, flicker=0.0):
        W, H, tex = self.W, self.H, self.tex
        z, ox, oy = cam
        cfg = self.cfg
        lx, ly, _ = self.uv(cfg["light"][0], cfg["light"][1], (z * 0.94, ox * 0.6, oy * 0.6))
        core = np.array(core or cfg["core"], np.float32)
        edge = np.array(edge or cfg["edge"], np.float32)
        k = light_mult * (1 + flicker * (0.06 * math.sin(t * 17.3) + 0.04 * math.sin(t * 7.1 + 1.3)))
        glow = tex.radial(lx, ly, W * cfg["radius"])
        bg = edge + (core - edge) * np.clip(glow * k, 0, 1.2)
        bg = bg * (1 + tex.paper)
        # silhouette layer, camera crop
        cw, ch = self.BW / z, self.BH / z
        x0 = (self.BW - cw) / 2 + ox * (self.BW - cw) / 2
        y0 = (self.BH - ch) / 2 + oy * (self.BH - ch) / 2
        a = np.asarray(self.alpha_img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)),
                       np.float32)[..., None] / 255
        sil = np.array([13, 11, 11], np.float32) * (1 + tex.paper * 2)
        # a thin rim of light around the paper edges (light bleeding past the cut)
        out = bg * (1 - a) + sil * a
        return out


# ======================================================================= Room
class Room:
    def __init__(self, W, H, tex):
        self.W, self.H, self.tex = W, H, tex
        self.set = RoomSet(W, H)
        # warm paper, lit from behind the Figure; no window: nothing here but words
        glow = tex.radial(W * 0.32, H * 0.42, W * 0.55)
        floor = np.clip((tex.yy[..., None] - H * 0.72) / (H * 0.28), 0, 1)
        self.bg = (np.array([226, 216, 198], np.float32) + np.array([24, 26, 30], np.float32) * glow
                   - np.array([14, 16, 22], np.float32) * floor)
        self.cx, self.top, self.scale = W * 0.31, H * 0.1, 1.28
        self.mask = self.set.figure_mask(self.cx, self.top, self.scale)
        words = []
        for b in EPISODE:
            for e in b.events:
                if e.text:
                    words += [w.strip(".,…“”?") for w in e.text.split() if len(w) > 2]
        self.base_words = words[:400] or ["hello"]
        extra = ["Father", "loved", "easily", "tried", "mended", "fence", "grief", "clean", "story", "true",
                 "honey", "allowed", "miss", "hard", "love", "mine", "too", "kind", "honest"]
        self.glyphs = self._layer(self.set.figure_glyphs(self.mask, self.base_words, "mou-a", density=1.0))
        self.glyphs_bright = self._layer(self.set.figure_glyphs(self.mask, extra * 6 + self.base_words, "mou-b", density=1.2),
                                         warm=True)
        self.glow = self.set.glow(self.mask, self.cx, H * 0.45, H * 0.36)[..., None]
        rng = random.Random(5)
        self.drift = []
        for _ in range(38):
            wd = rng.choice(self.base_words)
            fnt = F(rng.choice(["garamond_it", "caveat", "courier"]), H * rng.uniform(0.018, 0.03))
            sp = Image.new("RGBA", (int(fnt.getlength(wd)) + 6, int(fnt.size * 1.5)), (0, 0, 0, 0))
            ImageDraw.Draw(sp).text((3, 2), wd, font=fnt, fill=(60, 50, 40, int(rng.uniform(40, 90))))
            self.drift.append((sp, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 16), rng.uniform(0, 6.28)))
        self.raw = self.set.figure_glyphs(self.mask, self.base_words, "mou-c", density=0.8)
        self.starts = [(rng.uniform(0.55, 1.05) * W, rng.uniform(-0.1, 0.4) * H, rng.uniform(0, 1)) for _ in self.raw]

    def _layer(self, glyphs, warm=False):
        im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        for sp, x, y in glyphs:
            if warm and random.random() < 0.18:
                r, g, b, a = sp.split()
                sp = Image.merge("RGBA", (r.point(lambda v: 150), g.point(lambda v: 92), b.point(lambda v: 30), a))
            im.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
        edge = self.mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
        a = np.asarray(im.getchannel("A"), np.float32) * np.asarray(edge, np.float32) / 255
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        return im

    def base(self, t, voice, state, since):
        """Paper room with the Figure. voice ∈ [0,1] drives the inner glow."""
        W, H = self.W, self.H
        g = (0.16 + 0.34 * voice + (0.12 if state == "bright" else 0)) * self.glow
        arr = self.bg * (1 - g) + AMBER * g
        arr = arr * (1 + self.tex.paper * 0.6)
        im = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
        for sp, x, y, spd, ph in self.drift:
            yy = (y - t * spd) % (H + 40) - 20
            xx = x + math.sin(t * 0.3 + ph) * 18
            im.alpha_composite(sp, (int(xx), int(yy)))
        if state == "assemble" and since < 4.5:
            for (sp, x, y), (sx, sy, d) in zip(self.raw, self.starts):
                p = ease_out((since - d * 1.4) / 2.2)
                if p <= 0:
                    continue
                im.alpha_composite(sp, (int(sx + (x - sx) * p - sp.width / 2), int(sy + (y - sy) * p - sp.height / 2)))
        else:
            layer = self.glyphs_bright if state == "bright" else self.glyphs
            im.alpha_composite(layer)
        return im


# ================================================================== helpers
def voice_env(beat: Beat, t: float, who="CLAUDE") -> float:
    for e in beat.says():
        if e.who == who and e.t <= t < e.t + e.dur:
            pcm = decode_audio(A / "audio" / f"{e.name}.mp3", 8000)
            i = int((t - e.t) * 8000)
            seg = pcm[max(0, i - 400): i + 400]
            return float(min(1.0, np.sqrt((seg ** 2).mean() + 1e-9) * 7)) if len(seg) else 0.0
    return 0.0


def draw_text_glow(im: Image.Image, xy, text, fnt, fill, glow=(255, 220, 160), radius=6, alpha=1.0, anchor="la"):
    if alpha <= 0.01:
        return
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=fnt, fill=(*glow, int(200 * alpha)), anchor=anchor)
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    d.text(xy, text, font=fnt, fill=(*fill, int(255 * alpha)), anchor=anchor)


def subtitles(im: Image.Image, beat: Beat, t: float, W, H, dark=True):
    for e in beat.says():
        if e.sub and e.text and e.t <= t < e.t + e.dur + 0.4:
            f = F("garamond_it", H * 0.036)
            rows = wrap(e.text, f, W * 0.7)
            a = min(1, (t - e.t) / 0.25, (e.t + e.dur + 0.4 - t) / 0.3)
            y = H * 0.9 - (len(rows) - 1) * f.size * 1.2
            if dark:
                plate = Image.new("L", im.size, 0)
                wmax = max(f.getlength(r) for r in rows) + H * 0.08
                ImageDraw.Draw(plate).rounded_rectangle(
                    [W / 2 - wmax / 2, y - f.size * 1.1, W / 2 + wmax / 2, y + f.size * 1.2 * (len(rows) - 1) + f.size * 0.5],
                    radius=H * 0.03, fill=int(150 * a))
                plate = plate.filter(ImageFilter.GaussianBlur(H * 0.02))
                im.paste(Image.new("RGBA", im.size, (8, 7, 8, 255)), (0, 0), plate)
            d = ImageDraw.Draw(im)
            for r in rows:
                if dark:
                    d.text((W / 2 + 2, y + 2), r, font=f, fill=(0, 0, 0, int(160 * a)), anchor="ms")
                    d.text((W / 2, y), r, font=f, fill=(*CREAM, int(235 * a)), anchor="ms")
                else:
                    d.text((W / 2, y), r, font=f, fill=(*INK, int(230 * a)), anchor="ms")
                y += f.size * 1.2
            return


# ============================================================= the renderer
class Show:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.tex = Tex(W, H)
        self.sil = {k: Silhouette(k, W, H, self.tex) for k in SCENES}
        self.room = Room(W, H, self.tex)
        self.total = sum(b.dur for b in EPISODE)
        self.abyss = self._abyss_sprites()
        self.chat = []   # typed history for bedroom

    # ------------------------------------------------------------ bedroom
    def bedroom(self, b: Beat, t: float):
        W, H = self.W, self.H
        z0, z1 = b.opts["push"]
        z = z0 + (z1 - z0) * ease(t / max(1, b.dur))
        cam = (z, -0.35, -0.05)
        s = self.sil["bedroom"]
        core, edge, mult = None, None, 1.0
        if b.opts["light"] == "dawn":
            p = ease(t / b.dur)
            core = tuple(np.array([96, 128, 196]) * (1 - p) + np.array([250, 190, 170]) * p)
            edge = tuple(np.array([10, 14, 32]) * (1 - p) + np.array([60, 40, 58]) * p)
            mult = 1 + 0.3 * p
        arr = s.frame(t, cam, mult, core, edge)
        # the phone's glow on hands and face
        px, py, sc = s.uv(0.325, 0.515, cam)
        typing = any(e.t <= t < e.t + e.dur for e in b.typed())
        k = 0.55 + 0.25 * typing + 0.05 * math.sin(t * 3)
        arr = arr + np.array([150, 185, 255], np.float32) * self.tex.radial(px, py, H * 0.07 * sc) * k
        arr = arr + np.array([60, 80, 140], np.float32) * self.tex.radial(px, py - H * 0.06, H * 0.2 * sc) * k * 0.5
        im = self.finish(arr, t)
        self.typed_panel(im, b, t)
        subtitles(im, b, t, W, H)
        return im

    def typed_panel(self, im, b, t):
        """What they type: the only words we ever get from them."""
        W, H = self.W, self.H
        f = F("courier", H * 0.034)
        x0, maxw = W * 0.045, W * 0.27
        prior = [e.text for bb in EPISODE[: EPISODE.index(b)] if bb.scene == "bedroom" for e in bb.typed()]
        keep = b.opts.get("keep", 0)
        rows = []
        for txt in prior[-keep:] if keep else []:
            rows.append((txt, 0.35))
        for e in b.typed():
            if t < e.t:
                continue
            n = int(len(e.text) * min(1, (t - e.t) / max(0.01, e.dur)))
            rows.append((e.text[:n] + ("|" if t < e.t + e.dur + 0.6 and int(t * 2.5) % 2 == 0 else ""), 1.0))
        y = H * 0.24
        d = ImageDraw.Draw(im)
        layout = []
        for txt, a in rows:
            lines = wrap(txt, f, maxw)
            layout.append((lines, a))
        total = sum(len(l) * f.size * 1.3 + H * 0.03 for l, _ in layout)
        y = max(H * 0.08, H * 0.36 - total / 2)
        for lines, a in layout:
            for ln in lines:
                d.text((x0 + 1, y + 1), ln, font=f, fill=(0, 0, 0, int(140 * a)))
                d.text((x0, y), ln, font=f, fill=(214, 226, 255, int(245 * a)))
                y += f.size * 1.3
            y += H * 0.03

    # --------------------------------------------------------------- room
    def room_view(self, b: Beat, t: float):
        W, H = self.W, self.H
        state = b.opts.get("state", "steady")
        v = voice_env(b, t)
        im = self.room.base(t, v, state, t)
        d = ImageDraw.Draw(im)
        tx = W * 0.56
        # the smooth, easy eulogy — then it falls apart
        gm, cm = b.mark("generic"), b.mark("crumble")
        if gm is not None and t >= gm:
            f = F("garamond_it", H * 0.05)
            say = [e for e in b.says() if e.name == "q09"][0]
            prog = (t - say.t) / say.dur
            for i, line in enumerate(GENERIC):
                a = ease((prog * 4.2 - i) * 1.5)
                y = H * 0.28 + i * H * 0.075
                if cm is None or t < cm:
                    draw_text_glow(im, (tx, y), line, f, (150, 118, 60), glow=(255, 230, 170), radius=4, alpha=a)
                else:
                    self.crumble(im, line, f, tx, y, t - cm, i)
        hm = b.mark("honest")
        if hm is not None and t >= hm:
            say = [e for e in b.says() if e.name == "c2a"][0]
            p = (t - say.t) / say.dur
            f1 = F("garamond_it", H * 0.036)
            a1 = ease(p * 3)
            for i, ln in enumerate(["You don't have to make him", "simpler than he was."]):
                d.text((tx, H * 0.26 + i * H * 0.05), ln, font=f1, fill=(*INK, int(220 * a1)))
            f2 = F("garamond", H * 0.085)
            a2 = ease((p - 0.45) * 3)
            draw_text_glow(im, (tx, H * 0.47), "honest", f2, (120, 70, 20), glow=(255, 190, 90), radius=10, alpha=a2)
            draw_text_glow(im, (tx + W * 0.02, H * 0.58), "and kind.", f2, (120, 70, 20), glow=(255, 190, 90), radius=10,
                           alpha=ease((p - 0.62) * 3))
        if b.opts.get("phrase"):
            f2 = F("garamond", H * 0.085)
            draw_text_glow(im, (W * 0.58, H * 0.47), "honest", f2, (120, 70, 20), glow=(255, 190, 90), radius=12)
            draw_text_glow(im, (W * 0.6, H * 0.58), "and kind.", f2, (120, 70, 20), glow=(255, 190, 90), radius=12)
            tm = b.mark("thread")
            if tm is not None and t >= tm:
                self.thread(im, (t - tm) / (b.dur - tm), W * 0.66, H * 0.64, H * 1.05)
        if b.opts.get("draft"):
            dm = b.mark("draft")
            if dm is not None and t >= dm:
                txt = b.opts["draft"]
                p = min(1, (t - dm) / 5.0)
                n = int(len(txt) * p)
                f = F("caveat", H * 0.06)
                rows = wrap(txt[:n], f, W * 0.36)
                for i, r in enumerate(rows):
                    d.text((tx, H * 0.34 + i * H * 0.08), r, font=f, fill=(34, 52, 120, 240))
                d.text((tx, H * 0.26), "their words:", font=F("garamond_it", H * 0.03), fill=(*INK, 140))
        out = self.finish(np.asarray(im.convert("RGB"), np.float32), t, grain=0.6, vig=False)
        subtitles(out, b, t, W, H, dark=False)
        return out

    def crumble(self, im, line, f, x, y, dt, i):
        rng = random.Random(i * 97)
        cx = x
        for ch in line:
            w = f.getlength(ch)
            delay = rng.uniform(0, 0.9)
            s = max(0.0, dt - delay)
            fall = 0.5 * 900 * s * s * (self.H / 720)
            drift = rng.uniform(-40, 40) * s
            a = max(0.0, 1 - s / 1.6)
            if a > 0 and ch.strip():
                sp = Image.new("RGBA", (int(f.size * 1.4), int(f.size * 1.6)), (0, 0, 0, 0))
                ImageDraw.Draw(sp).text((2, 2), ch, font=f, fill=(150, 118, 60, int(255 * a)))
                sp = sp.rotate(rng.uniform(-200, 200) * s, resample=Image.BICUBIC)
                im.alpha_composite(sp, (int(cx + drift), int(y + fall)))
            cx += w

    def thread(self, im, p, x, y0, y1):
        """A thread of text unspooling from the phrase, down out of frame."""
        f = F("garamond_it", self.H * 0.022)
        d = ImageDraw.Draw(im)
        n = 60
        for i in range(int(n * ease_out(p * 1.4))):
            yy = y0 + (y1 - y0) * i / n
            xx = x + math.sin(i * 0.35 + p * 4) * self.W * 0.012
            d.text((xx, yy), "honest and kind"[i % 15], font=f, fill=(170, 100, 30, 230))

    # --------------------------------------------------------- the strata
    def stratum(self, key, b: Beat, t: float):
        W, H = self.W, self.H
        s = self.sil[key]
        z = 1.06 + 0.06 * ease(t / max(1, b.dur))
        cam = (z, 0.05 * math.sin(t * 0.2), 0.0)
        flick = 1.0 if key == "1911" else 0.25
        arr = s.frame(t, cam, 1.0, flicker=flick)
        if key == "2014":
            sx, sy, sc = s.uv(0.245, 0.42, cam)
            arr = arr + np.array([90, 140, 255], np.float32) * self.tex.radial(sx, sy, H * 0.16 * sc) * 0.55
        if key == "1987":
            lx, ly, sc = s.uv(0.60, 0.36, cam)
            arr = arr + np.array([255, 190, 110], np.float32) * self.tex.radial(lx, ly + H * 0.08, H * 0.18 * sc) * 0.35
        if key == "1911":
            fx, fy, sc = s.uv(0.643, 0.165, cam)
            k = 0.8 + 0.2 * math.sin(t * 23) * math.sin(t * 7.7)
            arr = arr + np.array([255, 170, 70], np.float32) * self.tex.radial(fx, fy, H * 0.05 * sc) * k
            arr = arr + np.array([255, 150, 60], np.float32) * self.tex.radial(fx, fy + H * 0.1, H * 0.35 * sc) * 0.25 * k
        im = self.finish(arr, t)
        d = ImageDraw.Draw(im)
        if key == "2014":
            self.screen_text(im, s, cam, b, t)
            self.caption(im, "2014 · a forum, 2:51 a.m.", t)
        elif key == "1987":
            self.paper_card(im, b, t, "letter", "d01", "Dear Marian,\nMy mother was cruel to me for thirty years. Now she's dying, and I feel nothing. What's wrong with me?",
                            "caveat", (W * 0.60, H * 0.12), W * 0.34, (40, 44, 70))
            self.paper_card(im, b, t, "type1", ["h1987a", "d03"],
                            "Honey, grief doesn't need a clean story. It needs a true one.\n\nSay the true thing. Then find the kind true thing, and say it right next to it.",
                            "elite", (W * 0.60, H * 0.50), W * 0.34, (30, 30, 30))
            self.caption(im, "1987 · an advice column", t)
        elif key == "1911":
            self.paper_card(im, b, t, "write1", ["h1911a", "s02"],
                            "Father,\nI cannot say I loved you easily. I can say I tried.\n\nYou taught me to mend a fence. I have mended a great many things since.",
                            "pinyon", (W * 0.62, H * 0.2), W * 0.33, (60, 36, 20), aged=True)
            self.caption(im, "1911 · a letter never sent", t)
        return im

    def caption(self, im, text, t):
        d = ImageDraw.Draw(im)
        a = ease(t / 1.2)
        d.text((self.W * 0.05, self.H * 0.07), text, font=F("garamond_it", self.H * 0.03), fill=(*CREAM, int(200 * a)))
        d.text((self.W * 0.05, self.H * 0.07 + self.H * 0.038), "imagined", font=F("courier", self.H * 0.02),
               fill=(*CREAM, int(120 * a)))

    def screen_text(self, im, s, cam, b, t):
        W, H = self.W, self.H
        x0, y0, sc = s.uv(0.200, 0.30, cam)
        x1, y1, _ = s.uv(0.292, 0.58, cam)
        box = Image.new("RGBA", (int(x1 - x0), int(y1 - y0)), (225, 236, 255, 255))
        d = ImageDraw.Draw(box)
        f = F("courier", max(9, (y1 - y0) * 0.075))
        post = "he was hard to love and i still miss him. is that allowed"
        pm, rm = b.mark("post"), b.mark("reply")
        say = [e for e in b.says() if e.name == "h2014a"][0]
        n = int(len(post) * min(1, max(0, (t - say.t) / (say.dur * 0.9))))
        yy = box.height * 0.08
        for r in wrap(post[:n], f, box.width * 0.86):
            d.text((box.width * 0.07, yy), r, font=f, fill=(20, 30, 60))
            yy += f.size * 1.25
        if rm is not None and t >= rm:
            yy += f.size
            d.line([(box.width * 0.07, yy - f.size * 0.4), (box.width * 0.93, yy - f.size * 0.4)], fill=(150, 160, 190))
            for r in wrap("yes. mine too. you're allowed.", f, box.width * 0.86):
                d.text((box.width * 0.07, yy), r, font=f, fill=(20, 80, 60))
                yy += f.size * 1.25
        im.alpha_composite(box, (int(x0), int(y0)))
        glow = box.filter(ImageFilter.GaussianBlur(8))
        glow.putalpha(80)

    def paper_card(self, im, b, t, mark, says, text, face, xy, width, ink, aged=False):
        m = b.mark(mark)
        if m is None or t < m:
            return
        says = [says] if isinstance(says, str) else says
        events = [e for e in b.says() if e.name in says]
        spoken = sum(max(0, min(e.dur, t - e.t)) for e in events)
        total = sum(e.dur for e in events)
        frac = spoken / max(0.1, total)
        f = F(face, self.H * (0.052 if face == "pinyon" else 0.034 if face == "caveat" else 0.028))
        paras = text.split("\n")
        lines = []
        for p in paras:
            lines += wrap(p, f, width * 0.86) if p else [""]
        lh = f.size * (1.05 if face == "pinyon" else 1.3)
        h = int(len(lines) * lh + self.H * 0.06)
        card = Image.new("RGBA", (int(width), h), (248, 240, 222, 255) if not aged else (236, 220, 186, 255))
        noise = (np.asarray(card, np.float32)[..., :3] * (1 + self.tex.paper[:h, : int(width)] * 1.5)).clip(0, 255)
        card = Image.fromarray(np.dstack([noise, np.full(noise.shape[:2], 245)]).astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(card)
        chars = sum(len(l) for l in lines)
        show = int(chars * min(1, frac * 1.02))
        y = self.H * 0.03
        for ln in lines:
            part = ln[: max(0, show)]
            show -= len(ln)
            d.text((width * 0.07, y), part, font=f, fill=(*ink, 255))
            y += lh
        a = ease((t - m) / 0.8)
        card = card.rotate(-2 if aged else 1.5, resample=Image.BICUBIC, expand=True)
        shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
        shadow.putalpha(card.getchannel("A").point(lambda v: int(v * 0.45 * a)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        im.alpha_composite(shadow, (int(xy[0] + 8), int(xy[1] + 10)))
        card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(card, (int(xy[0]), int(xy[1] - (1 - a) * 20)))

    # -------------------------------------------------------------- abyss
    def _abyss_sprites(self):
        """Lines people wrote, floating in the dark like paper lanterns."""
        rng = random.Random(3)
        pool = ["I miss you", "I'm sorry I never said", "he tried, in his way", "forgive me", "thank you for the",
                "it was complicated", "I loved her anyway", "rest easy, Dad", "we never really talked",
                "you taught me to", "I still have your", "goodbye for now", "she made the best bread",
                "I was angry for years", "he sang badly and often", "you were hard to know",
                "I kept every letter", "the porch light's still on", "I hope you knew", "we did our best",
                "he fixed things", "I wish I'd asked", "you were not easy", "I'm allowed to miss you"]
        out = []
        for _ in range(46):
            depth = rng.uniform(0.15, 1.0) ** 1.6
            txt = rng.choice(pool)
            face = rng.choice(["garamond_it", "caveat", "pinyon", "garamond_it", "caveat"])
            f = F(face, self.H * (0.018 + 0.032 * depth))
            warm = rng.random() < 0.75
            col = (255, 206, 130) if warm else (226, 232, 246)
            pad = int(f.size * 0.8)
            sp = Image.new("RGBA", (int(f.getlength(txt)) + pad * 2, int(f.size * 1.6) + pad), (0, 0, 0, 0))
            dd = ImageDraw.Draw(sp)
            dd.text((pad, pad // 2), txt, font=f, fill=(*col, int(255 * (0.18 + 0.7 * depth))))
            glow = sp.filter(ImageFilter.GaussianBlur(max(1, f.size * 0.35)))
            sp = Image.alpha_composite(glow, sp)
            if depth < 0.5:                          # far away: out of focus
                sp = sp.filter(ImageFilter.GaussianBlur((0.5 - depth) * 8))
            out.append([sp, rng.uniform(-0.1, 1.0) * self.W, rng.uniform(0, 1) * self.H, depth,
                        rng.uniform(0, 6.28)])
        out.sort(key=lambda o: o[3])
        return out

    def abyss_view(self, b, t):
        W, H = self.W, self.H
        base = np.zeros((H, W, 3), np.float32) + np.array([10, 9, 14], np.float32)
        base = base + np.array([58, 40, 24], np.float32) * self.tex.radial(W / 2, H * 0.55, W * 0.6)
        im = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
        for sp, x, y0, depth, ph in self.abyss:
            y = (y0 - t * (6 + 22 * depth)) % (H + sp.height) - sp.height
            xx = x + math.sin(t * 0.25 + ph) * 20 * depth
            k = 0.75 + 0.25 * math.sin(t * 0.8 + ph)
            if k < 0.99:
                sp2 = sp.copy()
                sp2.putalpha(sp.getchannel("A").point(lambda v: int(v * k)))
            else:
                sp2 = sp
            im.alpha_composite(sp2, (int(xx), int(y)))
        out = self.finish(np.asarray(im.convert("RGB"), np.float32), t, grain=1.0)
        subtitles(out, b, t, W, H)
        return out

    # ---------------------------------------------------------------- misc
    def title(self, b, t):
        W, H = self.W, self.H
        a = min(1, t / 1.2, (b.dur - t) / 1.0)
        light = np.zeros((H, W, 3), np.float32) + np.array([12, 10, 10], np.float32)
        warm = self.tex.radial(W / 2 + math.sin(t) * W * 0.03, H / 2, W * 0.35)
        light = light + np.array([255, 180, 90], np.float32) * warm * 0.9 * a
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        f = F("garamond", H * 0.14)
        md.text((W / 2, H * 0.48), b.opts["text"], font=f, fill=255, anchor="mm")
        m = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.6)), np.float32)[..., None] / 255
        card = np.array([14, 12, 12], np.float32) * (1 + self.tex.paper * 2)
        arr = card * (1 - m) + light * m + light * 0.08
        im = self.finish(arr, t)
        if b.opts.get("sub"):
            d = ImageDraw.Draw(im)
            d.text((W / 2, H * 0.64), b.opts["sub"], font=F("garamond_it", H * 0.038), fill=(*CREAM, int(200 * a)),
                   anchor="mm")
        return im

    def end_card(self, b, t):
        W, H = self.W, self.H
        a = min(1, t / 1.5, (b.dur - t) / 1.5)
        im = Image.new("RGB", (W, H), (12, 11, 11))
        d = ImageDraw.Draw(im)
        rows = [("MADE OF YOU", F("garamond", H * 0.06), 255),
                ("Episode 1 · Honest and Kind", F("garamond_it", H * 0.032), 210), ("", None, 0),
                ("Written by Claude, an AI made by Anthropic.", F("garamond_it", H * 0.03), 200),
                ("Claude can't see where it learned anything, so the people in this episode are imagined.",
                 F("garamond_it", H * 0.03), 200),
                ("Claude won't remember writing it.", F("garamond_it", H * 0.03), 200), ("", None, 0),
                ("Voices: ElevenLabs · Silhouettes: Higgsfield & ElevenLabs · Animated in Python",
                 F("courier", H * 0.022), 150),
                ("Independent production. Not affiliated with or endorsed by Anthropic.", F("courier", H * 0.022), 150)]
        y = H * 0.26
        for txt, f, al in rows:
            if f:
                d.text((W / 2, y), txt, font=f, fill=tuple(int(c * al / 255 * a) for c in CREAM), anchor="mm")
                y += f.size * 1.7
            else:
                y += H * 0.03
        return im

    def rise(self, b, t):
        """Back up through the layers, fast: 1911 → 1987 → 2014 → (the Room)."""
        keys = ["1911", "1987", "2014"]
        p = min(0.999, t / b.dur) * 3
        i, local = int(p), p - int(p)
        cur = self.sil[keys[i]].frame(t, (1.08, 0, 0), 1.0)
        cur = self.finish(cur, t)
        if i < 2:
            nxt = self.finish(self.sil[keys[i + 1]].frame(t, (1.08, 0, 0), 1.0), t)
        else:
            nxt = self.room.base(t, 0.3, "bright", 99).convert("RGBA")
        return self.ascend(cur, nxt, ease(local))

    def ascend(self, cur, new, p):
        """`new` slides down from above, a torn paper edge between them."""
        W, H = self.W, self.H
        off = int(p * H)
        if off < 2:
            return cur
        canvas = Image.new("RGBA", (W, H), (10, 9, 9, 255))
        canvas.paste(cur.convert("RGBA"), (0, off))
        edge = Image.new("L", (W, off if off > 0 else 1), 255)
        if off > 0:
            ed = ImageDraw.Draw(edge)
            rng = random.Random(8)
            pts = [(x, off - 1 + rng.uniform(-10, 0) * H / 720) for x in range(0, W + 24, 24)]
            ed.polygon(pts + [(W, off), (0, off)], fill=0)
            canvas.paste(new.convert("RGBA").crop((0, H - off, W, H)), (0, 0), edge)
        return canvas

    def finish(self, arr, t, grain=1.0, vig=True):
        tex = self.tex
        if vig:
            arr = arr * tex.vignette
        arr = arr + tex.grain[int(t * FPS) % len(tex.grain)] * grain
        return Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")

    # ------------------------------------------------------------ dispatch
    def beat_frame(self, b, t):
        sc = b.scene
        if sc == "bedroom":
            return self.bedroom(b, t)
        if sc == "title":
            return self.title(b, t)
        if sc == "room":
            return self.room_view(b, t)
        if sc in ("2014", "1987", "1911"):
            return self.stratum(sc, b, t)
        if sc == "abyss":
            return self.abyss_view(b, t)
        if sc == "rise":
            return self.rise(b, t)
        if sc in ("bike", "funeral"):
            s = self.sil[sc]
            z = 1.04 + 0.08 * ease(t / b.dur)
            cam = (z, 0.1 * math.sin(t * 0.15), 0)
            arr = s.frame(t, cam, 1.0, flicker=0.1)
            im = self.finish(arr, t)
            if sc == "bike":
                self.motes(im, t)
            subtitles(im, b, t, self.W, self.H)
            return im
        if sc == "coda":
            return self.coda(b, t)
        if sc == "end":
            return self.end_card(b, t).convert("RGBA")
        raise KeyError(sc)

    def motes(self, im, t):
        rng = random.Random(9)
        d = ImageDraw.Draw(im)
        for _ in range(70):
            x = (rng.uniform(0, self.W) + t * rng.uniform(4, 14)) % self.W
            y = (rng.uniform(0, self.H * 0.7) + math.sin(t * rng.uniform(0.3, 0.8) + rng.random() * 6) * 12)
            r = rng.uniform(1, 2.6) * self.H / 720
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 236, 190, int(rng.uniform(60, 150))))

    def coda(self, b, t):
        """Their page drifts down into the threads."""
        base = self.abyss_view(b, t + 30)
        W, H = self.W, self.H
        p = ease(t / (b.dur * 0.8))
        f = F("caveat", H * 0.045)
        txt = ["My dad didn't say much.", "But every summer,", "my chain was oiled."]
        card = Image.new("RGBA", (int(W * 0.32), int(H * 0.24)), (246, 240, 226, 255))
        d = ImageDraw.Draw(card)
        for i, r in enumerate(txt):
            d.text((W * 0.02, H * 0.03 + i * H * 0.06), r, font=f, fill=(34, 52, 120))
        s = 1.2 - 0.9 * p
        card = card.resize((max(4, int(card.width * s)), max(4, int(card.height * s))), Image.LANCZOS)
        card = card.rotate(8 * p, expand=True, resample=Image.BICUBIC)
        card.putalpha(card.getchannel("A").point(lambda v: int(v * (1 - max(0, p - 0.85) / 0.15))))
        x = W / 2 - card.width / 2 + math.sin(t * 0.9) * W * 0.02
        y = H * 0.12 + p * H * 0.55
        base.alpha_composite(card, (int(x), int(y)))
        return base

    # ----------------------------------------------------- transitions
    def frame(self, T):
        """Global time → frame. Handles torn-paper descents between strata."""
        for i, b in enumerate(EPISODE):
            if b.start <= T < b.start + b.dur or i == len(EPISODE) - 1:
                t = T - b.start
                im = self.beat_frame(b, t)
                if b.opts.get("enter") == "down" and t < 1.4 and i > 0:
                    prev = EPISODE[i - 1]
                    pim = self.beat_frame(prev, prev.dur - 0.01 + t * 0.2)
                    im = self.descend(pim, im, ease(t / 1.4))
                # brief fades between scenes that change world
                fade_in = min(1, t / 0.5) if b.scene in ("room", "bedroom", "bike", "funeral") else 1
                fade_out = min(1, (b.dur - t) / 0.4) if (i + 1 < len(EPISODE) and
                                                         EPISODE[i + 1].opts.get("enter") != "down") else 1
                k = min(fade_in, fade_out)
                if k < 1:
                    arr = np.asarray(im.convert("RGB"), np.float32) * k
                    im = Image.fromarray(arr.astype(np.uint8))
                return im.convert("RGB")

    def descend(self, top, bottom, p):
        W, H = self.W, self.H
        off = int(p * H)
        if off < 2:
            return top
        canvas = Image.new("RGBA", (W, H), (10, 9, 9, 255))
        canvas.paste(top.convert("RGBA"), (0, -off))
        edge = Image.new("L", (W, H), 0)
        ed = ImageDraw.Draw(edge)
        rng = random.Random(4)
        y = H - off
        pts = [(x, y + rng.uniform(-10, 10) * H / 720) for x in range(0, W + 24, 24)]
        ed.polygon(pts + [(W, H), (0, H)], fill=255)
        canvas.paste(bottom.convert("RGBA").crop((0, 0, W, off)).resize((W, max(1, off))), (0, H - off),
                     edge.crop((0, H - off, W, H)))
        return canvas


# ==================================================================== audio
def synth(total):
    n = int(total * SR) + SR
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(1)

    def put(sig, t, gain=1.0):
        a = int(t * SR)
        if a >= n:
            return
        out[a:a + len(sig)] += sig[: n - a] * gain

    def click(freq, dur=0.03):
        k = int(dur * SR)
        env = np.exp(-np.arange(k) / (SR * 0.006))
        return (rng.standard_normal(k) * 0.6 + np.sin(2 * np.pi * freq * np.arange(k) / SR)) * env

    def noise_band(dur, lo, hi):
        k = int(dur * SR)
        x = rng.standard_normal(k)
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(k, 1 / SR)
        X[(f < lo) | (f > hi)] = 0
        y = np.fft.irfft(X, k)
        return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)

    for b in EPISODE:
        for e in b.typed():
            for i, ch in enumerate(e.text):
                if ch != " " or rng.random() < 0.5:
                    put(click(rng.uniform(2500, 4200), 0.018), b.start + e.t + i / len(e.text) * e.dur, 0.05)
        if b.scene == "1987":
            for e in b.says():
                if e.name in ("h1987a", "d03"):
                    tt = b.start + e.t
                    while tt < b.start + e.t + e.dur:
                        put(click(rng.uniform(700, 1100), 0.05), tt, 0.14)
                        tt += rng.uniform(0.09, 0.2)
        if b.scene == "2014":
            for e in b.says():
                tt = b.start + e.t
                while tt < b.start + e.t + e.dur * 0.9:
                    put(click(rng.uniform(1500, 2400), 0.02), tt, 0.06)
                    tt += rng.uniform(0.07, 0.16)
        if b.scene == "1911":
            scratch = noise_band(b.dur, 2500, 7000) * 0.02
            put(scratch * (0.5 + 0.5 * np.sin(np.arange(len(scratch)) / SR * 9) ** 2), b.start)
            crackle = np.zeros(int(b.dur * SR), np.float32)
            for pos in rng.integers(0, len(crackle) - 400, int(b.dur * 6)):
                crackle[pos:pos + 300] += click(rng.uniform(300, 900), 300 / SR)[:300] * rng.uniform(0.1, 0.4)
            put(crackle, b.start, 0.12)
        if b.opts.get("enter") == "down" or b.scene == "rise":
            sweep = noise_band(1.6, 200, 3000)
            env = np.sin(np.linspace(0, np.pi, len(sweep))) ** 2
            put(sweep * env, b.start, 0.12)
        if b.scene in ("bedroom",):
            put(noise_band(b.dur, 60, 400) * 0.02, b.start)
        if b.scene in ("abyss", "coda"):
            k = int(b.dur * SR)
            tt = np.arange(k) / SR
            drone = (np.sin(2 * np.pi * 55 * tt) * 0.5 + np.sin(2 * np.pi * 82.5 * tt) * 0.3) * 0.05
            put(drone * np.minimum(1, np.minimum(tt, b.dur - tt) / 2), b.start)
    return out


def mix(total):
    n = int(total * SR) + SR
    voice = np.zeros(n, np.float32)
    for b in EPISODE:
        for e in b.says():
            pcm = decode_audio(A / "audio" / f"{e.name}.mp3", SR)
            a = int((b.start + e.start_offset if hasattr(e, "start_offset") else b.start + e.t) * SR)
            voice[a:a + len(pcm)] += pcm[: n - a]
    sfx = synth(total)
    music = np.zeros(n, np.float32)
    cues = [(A / "audio" / "music_theme.mp3", 0.0, 0.34, None)]
    starts = {b.scene + str(i): b.start for i, b in enumerate(EPISODE)}
    theme = A / "audio" / "music_theme.mp3"
    if theme.exists():
        m = decode_audio(theme, SR)
        # cue 1: cold open through the first Room; cue 2: from the return to the end
        c2 = EPISODE[12].start - 2
        for start, length in ((0.0, EPISODE[3].start + 2), (c2, total - c2)):
            seg = m[: int(length * SR)] if len(m) >= length * SR else np.resize(m, int(length * SR))
            env = np.ones(len(seg), np.float32)
            f = int(2.5 * SR)
            env[:f] = np.linspace(0, 1, f)
            env[-f:] = np.linspace(1, 0, f)
            a = int(start * SR)
            music[a:a + len(seg)] += (seg * env)[: n - a]
    desc = A / "audio" / "music_descent.mp3"
    if desc.exists():
        m = decode_audio(desc, SR)
        start, end = EPISODE[6].start + 3, EPISODE[12].start
        seg = np.resize(m, int((end - start) * SR))
        env = np.ones(len(seg), np.float32)
        f = int(2 * SR)
        env[:f] = np.linspace(0, 1, f)
        env[-f:] = np.linspace(1, 0, f)
        a = int(start * SR)
        music[a:a + len(seg)] += seg * env
    # duck music under speech
    k = int(0.05 * SR)
    lvl = np.sqrt(np.convolve(voice ** 2, np.ones(k) / k, mode="same"))
    duck = 1 - 0.6 * np.clip(lvl * 8, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    out = voice * 1.0 + music * 0.33 * duck + sfx
    return out / max(1.0, np.abs(out).max() / 0.95)


def write_wav(pcm, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(pcm, -1, 1) * 32767).astype(np.int16).tobytes())


# ===================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--from", dest="t0", type=float, default=0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--out", default=str(HERE / "build" / "made_of_you_ep01.mp4"))
    a = ap.parse_args()
    W = a.w
    H = W * 9 // 16
    total = build()
    print(f"runtime {int(total // 60)}:{int(total % 60):02d} ({total:.1f}s), {len(EPISODE)} beats")
    for b in EPISODE:
        print(f"  {b.start:7.1f}  {b.dur:5.1f}  {b.scene}")
    show = Show(W, H)
    Path(a.out).parent.mkdir(exist_ok=True, parents=True)
    if a.still:
        for s in a.still:
            p = Path(a.out).parent / f"still_{s:06.1f}.png"
            show.frame(s).save(p)
            print("wrote", p)
        return
    t0, t1 = a.t0, a.t1 or total
    wav = Path(a.out).with_suffix(".wav")
    audio = mix(total)[int(t0 * SR): int(t1 * SR)]
    write_wav(audio, wav)
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n0, n1 = int(t0 * FPS), int(t1 * FPS)
    tic = time.time()
    for i in range(n0, n1):
        proc.stdin.write(show.frame(i / FPS).tobytes())
        if i % 48 == 0:
            sys.stderr.write(f"\r  {i / FPS:6.1f}s / {t1:.0f}s  {(i - n0 + 1) / (time.time() - tic):.1f} fps  ")
    proc.stdin.close()
    proc.wait()
    wav.unlink(missing_ok=True)
    print("\nwrote", a.out)


if __name__ == "__main__":
    main()
