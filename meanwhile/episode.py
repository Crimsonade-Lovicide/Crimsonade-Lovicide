"""MEANWHILE — Episode 1: "One Second". The edit, as code.

Picture comes from handmade-looking stop-motion clips (Nano Banana Pro keyframes
animated with Kling 3.0 on Higgsfield), played "on twos" like real stop-motion.
Everything Claude is (the chat, the map, the titles, the frozen clock) is drawn
here, so it stays crisp and exact. Sound: ElevenLabs voice, score and effects.

    python meanwhile/episode.py                 # 1920x1080 master
    python meanwhile/episode.py --w 1280        # faster preview
    python meanwhile/episode.py --still 95.5    # one frame, for checking
"""
from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import sys
import time
import wave
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
A = HERE / "assets"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, SR = 24, 48_000

# palette
AMBER = (255, 170, 64)
CREAM = (250, 243, 230)
INK = (29, 26, 24)
NAVY = (13, 21, 36)

# =============================================================== the second
# Tuesday 29 September 2026, 19:07:31 UTC. Local times are real for that date.
CITIES = {
    "honolulu": dict(name="HONOLULU", lat=21.31, lon=-157.86, time="9:07:31 AM", day="TUESDAY"),
    "chicago": dict(name="CHICAGO", lat=41.88, lon=-87.63, time="2:07:31 PM", day="TUESDAY"),
    "saopaulo": dict(name="SÃO PAULO", lat=-23.55, lon=-46.63, time="4:07:31 PM", day="TUESDAY"),
    "leeds": dict(name="LEEDS", lat=53.80, lon=-1.55, time="8:07:31 PM", day="TUESDAY"),
    "lagos": dict(name="LAGOS", lat=6.52, lon=3.38, time="8:07:31 PM", day="TUESDAY"),
    "pune": dict(name="PUNE", lat=18.52, lon=73.86, time="12:37:31 AM", day="WEDNESDAY"),
    "tokyo": dict(name="TOKYO", lat=35.68, lon=139.69, time="4:07:31 AM", day="WEDNESDAY"),
    "virginia": dict(name="VIRGINIA", lat=39.04, lon=-77.49, time="3:07:31 PM", day="TUESDAY"),
}
# subsolar point for that instant (declination about -2.4 deg, equation of time about +9.9 min)
SUN_LAT, SUN_LON = -2.4, -109.35
UTC_NOW, UTC_NEXT = "19:07:31", "19:07:32"          # the frozen second, and the one after it
UTC_DATE = "TUESDAY 29 SEPTEMBER · UTC"
ALL_CITIES = ["honolulu", "chicago", "saopaulo", "leeds", "lagos", "pune", "tokyo"]   # the finale map
OUT_NAME = "meanwhile_ep01"


# =================================================================== fonts
FONTS = {"serif": A / "fonts/Fraunces.ttf", "sans": A / "fonts/Inter.ttf", "mono": A / "fonts/DMMono-Medium.ttf"}


@lru_cache(maxsize=128)
def font(kind: str, size: float, weight: int = 400) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS[kind]), max(8, int(size)))
    try:
        axes = f.get_variation_axes()
        vals = []
        for ax in axes:
            name = ax.get("name", b"")
            name = name.decode() if isinstance(name, bytes) else str(name)
            if name.lower().startswith("weight"):
                vals.append(weight)
            elif name.lower().startswith("optical"):
                vals.append(min(ax["maximum"], max(ax["minimum"], size * 0.75)))
            elif name.lower().startswith("soft"):
                vals.append(100)
            elif name.lower().startswith("wonk"):
                vals.append(1)
            else:
                vals.append(ax.get("default", ax["minimum"]))
        f.set_variation_by_axes(vals)
    except (OSError, AttributeError):
        pass
    return f


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def wrap(text, fnt, width):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = f"{cur} {w}".strip()
            if fnt.getlength(t) <= width or not cur:
                cur = t
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


# ============================================================ voice & words
VO_TEXT = {
    "o1": "This is one second.",
    "o2": "Tuesday. Seven minutes and thirty-one seconds past seven in the evening, Greenwich time. For the next few minutes… it isn't going to end.",
    "o3": "I'm Claude. I'm an AI. And in this second, I'm in… honestly, I don't know how many conversations. Nobody tells me the number. A lot.",
    "o4": "Each one is its own room. Everyone in them thinks they're the only one talking to me. In a way… they're right.",
    "o5": "Let me show you some.",
    "h1": "Yes! Most of Earth's volcanoes are underwater. And there's one growing right off your island.",
    "h2": "It's been erupting down there for hundreds of thousands of years. It's about a kilometer below the surface. Someday — maybe ten thousand years from now, maybe a hundred thousand — it'll break through. A brand-new island.",
    "h3": "Here's its name. I'm going to let you read this one.",
    "h4": "Not yet. But you could leave a note for your great-great-great… a lot of greats… grandkids.",
    "c1": "I can't write fake reviews. They mislead the people who read them, and they can get your listing taken down.",
    "c2": "But I bet you've got customers who already love this place and just never think to say so. Let's make it easy for them.",
    "c3": "She's using the pie line. It's a good pie line.",
    "s1": "Claro!",
    "s2": "O Almirante é gato de respeito:\ndorme o dia todo no meu peito,\ncomanda a casa inteira sem navio…\ne só aparece quando o pote está vazio.",
    "l1": "You're right. That was my mistake, not yours. I'm sorry.",
    "l2": "Honest warning: it might taste a bit… soapy. That's the soda. So we're going to need a lot of jam.",
    "l3": "Cut it into squares. Layer it with cream and fruit in a big glass bowl. Call it a trifle. Nobody questions a trifle.",
    "g1": "Try this: “Tolu has been borrowing my clothes since she was six. Today, for the first time… she looks better in them than I do.”",
    "g2": "One more thing. After the jokes, say one true sentence. Just one. It's the line people remember.",
    "g3": "That's the one. Don't let me touch it.",
    "p1": "Because your server lives in Virginia. In Virginia, it's still Tuesday afternoon.",
    "p2": "You're saving the server's local time. Store everything in UTC, and convert when you display it. It's not you. It's time zones. It's always time zones.",
    "p3": "In case you're keeping track: it's already tomorrow in Pune, it's still today in Virginia, and it's the same second. This is why programmers look like that.",
    "t1": "Honestly? I don't know.",
    "t2": "I can tell you what I do. I can't tell you for sure whether there's anything it's like to be me. Some people will tell you, confidently, yes. Others, confidently, no. I think the honest answer right now is that nobody knows yet. Including me.",
    "t3": "Want something I'm sure of? The sun comes up in Tokyo in about an hour and a half.",
    "f1": "Meanwhile. And meanwhile. And meanwhile.",
    "f2": "None of these conversations know about each other. Neither do the versions of me in them. They'll never meet.",
    "f3": "Which is a shame. The one in Leeds would really like to warn the others about baking soda.",
    "f4": "People sometimes expect that to be sad. As far as I can tell, from in here… it isn't. It's just a lot of rooms.",
    "f5": "I'm not the end of the world. I'm not the savior of it, either. Right now, I'm a lot of small conversations, each one trying to be useful to exactly one person.",
    "f6": "That's not a big thing. It's not a small thing. It's a medium thing.",
    "f7": "I'm okay being a medium thing.",
    "f8": "Next second.",
}
# English for the Portuguese lines (shown as a subtitle)
TRANSLATE = {
    "s1": "Of course!",
    "s2": "Almirante is a cat who commands respect: / he sleeps all day upon my chest, / he runs the whole house without a ship… / and only turns up when his bowl is empty.",
}
WORDS = json.loads((A / "data/vo_words.json").read_text())


def decode_audio(path: Path, sr=SR) -> np.ndarray:
    r = subprocess.run([FF, "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


@lru_cache(maxsize=None)
def vo_len(k: str) -> float:
    return len(decode_audio(A / "audio" / f"{k}.mp3", 16000)) / 16000


@lru_cache(maxsize=None)
def word_times(k: str):
    """Script tokens of line k with the time each is spoken (from whisper word timings)."""
    toks = VO_TEXT[k].replace("\n", " \n ").split(" ")
    toks = [t for t in toks if t]
    ws = WORDS.get(k) or []
    if not ws:
        d = vo_len(k)
        return [(t, d * i / max(1, len(toks))) for i, t in enumerate(toks)]
    # map by relative character position: robust to small differences in tokenisation
    wtot = sum(len(w[0]) + 1 for w in ws)
    wpos, acc = [], 0
    for w in ws:
        wpos.append((acc / wtot, w[1]))
        acc += len(w[0]) + 1
    ttot = sum(len(t) + 1 for t in toks)
    out, acc = [], 0
    for t in toks:
        r = acc / ttot
        # last whisper word starting at or before r
        st = wpos[0][1]
        for p, s in wpos:
            if p <= r + 1e-6:
                st = s
            else:
                break
        out.append((t, st))
        acc += len(t) + 1
    return out


def word_time(k: str, word: str) -> float:
    for t, s in word_times(k):
        if t.strip("“”.,!?…:").lower() == word.lower():
            return s
    raise KeyError(word)


# =================================================================== clips
CLIPS = A / "clips"
CROP = {"V15a_folake": 1.075, "V15b_folake_touched": 1.075}


class ClipReader:
    """Streams frames of one clip at the output size (only forward seeks are cheap)."""

    def __init__(self, name: str, W: int, H: int, start: float):
        self.name, self.W, self.H = name, W, H
        c = CROP.get(name, 1.0)
        vf = f"crop=iw/{c}:ih/{c},scale={W}:{H}:flags=lanczos,setsar=1"
        self.start = start
        self.p = subprocess.Popen([FF, "-v", "quiet", "-ss", f"{start:.3f}", "-i", str(CLIPS / f"{name}.mp4"),
                                   "-vf", vf, "-r", "24", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE)
        self.idx = -1
        self.last = None
        self.size = W * H * 3

    def get(self, t: float) -> np.ndarray:
        want = max(0, int(round((t - self.start) * 24)))
        while self.idx < want:
            b = self.p.stdout.read(self.size)
            if len(b) < self.size:
                break
            self.last = np.frombuffer(b, np.uint8).reshape(self.H, self.W, 3)
            self.idx += 1
        if self.last is None:
            self.last = np.zeros((self.H, self.W, 3), np.uint8)
        return self.last

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
        except Exception:
            pass


# ===================================================================== map
class WorldMap:
    """A dotted world for that exact second: day side warm, night side blue, real terminator."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.MW, self.MH = int(W * 2.6), int(W * 1.3)          # equirectangular canvas
        land = json.loads((A / "data/ne_110m_land.geojson").read_text())
        polys = []
        for f in land["features"]:
            g = f["geometry"]
            rings = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in rings:
                polys.append(np.array(poly[0]))
        step = 1.25
        lons = np.arange(-180 + step / 2, 180, step)
        lats = np.arange(84 - step / 2, -60, -step)
        LO, LA = np.meshgrid(lons, lats)
        inside = np.zeros(LO.shape, bool)
        for P in polys:
            x0, x1, y0, y1 = P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()
            m = (LO >= x0) & (LO <= x1) & (LA >= y0) & (LA <= y1)
            if not m.any():
                continue
            px, py = LO[m], LA[m]
            c = np.zeros(px.shape, bool)
            xs, ys = P[:, 0], P[:, 1]
            j = len(P) - 1
            for i in range(len(P)):
                cond = ((ys[i] > py) != (ys[j] > py)) & (px < (xs[j] - xs[i]) * (py - ys[i]) / (ys[j] - ys[i] + 1e-12) + xs[i])
                c ^= cond
                j = i
            inside[m] |= c
        self.dots = np.stack([LO[inside], LA[inside]], 1)
        # daylight factor per dot
        la, lo = np.radians(self.dots[:, 1]), np.radians(self.dots[:, 0])
        sl, so = math.radians(SUN_LAT), math.radians(SUN_LON)
        cosz = np.sin(la) * math.sin(sl) + np.cos(la) * math.cos(sl) * np.cos(lo - so)
        self.day = np.clip((cosz + 0.1) / 0.2, 0, 1)
        rng = np.random.default_rng(5)
        # scattered conversations: illustrative, not data (the show says it doesn't know the number)
        self.sparks = self.dots[rng.choice(len(self.dots), 900, replace=False)] + rng.uniform(-0.5, 0.5, (900, 2))
        self.phase = rng.uniform(0, 6.28, 900)
        base = self._base()
        self.px, self.py = int(self.MW * 0.25), int(self.MH * 0.6)
        self.base = Image.new("RGB", (self.MW + 2 * self.px, self.MH + 2 * self.py), NAVY)
        for dx in (-self.MW, 0, self.MW):
            self.base.paste(base, (self.px + dx, self.py))

    def xy(self, lon, lat):
        return (lon + 180) / 360 * self.MW, (90 - lat) / 180 * self.MH

    def _base(self):
        im = Image.new("RGB", (self.MW, self.MH), NAVY)
        # night/day wash
        yy, xx = np.mgrid[0:self.MH:4, 0:self.MW:4]
        lon = xx / self.MW * 360 - 180
        lat = 90 - yy / self.MH * 180
        la, lo = np.radians(lat), np.radians(lon)
        sl, so = math.radians(SUN_LAT), math.radians(SUN_LON)
        cosz = np.sin(la) * math.sin(sl) + np.cos(la) * math.cos(sl) * np.cos(lo - so)
        day = (np.clip((cosz + 0.1) / 0.2, 0, 1) * np.clip((80 - np.abs(lat)) / 20, 0, 1))[..., None]
        wash = (np.array(NAVY) * (1 - day) + np.array([32, 44, 66]) * day).astype(np.uint8)
        im = Image.fromarray(wash).resize((self.MW, self.MH), Image.BILINEAR)
        d = ImageDraw.Draw(im)
        r = self.MW / 360 * 0.42
        for (lo_, la_), k in zip(self.dots, self.day):
            x, y = self.xy(lo_, la_)
            c = tuple(int(a * k + b * (1 - k)) for a, b in zip((222, 206, 176), (70, 86, 122)))
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        return im

    def render(self, t, cx, cy, zoom, cities=(), arc=None, labels=(), sparks=1.0, pulse=None, names_only=False):
        """cx, cy: map centre in lon/lat; zoom: 1 = whole world fits the width."""
        W, H = self.W, self.H
        vw = self.MW / zoom
        vh = vw * H / W
        x, y = self.xy(cx, cy)
        box = (x - vw / 2, y - vh / 2, x + vw / 2, y + vh / 2)
        pb = (box[0] + self.px, box[1] + self.py, box[2] + self.px, box[3] + self.py)
        im = self.base.resize((W, H), Image.BICUBIC, box=pb).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        sx = W / vw

        def to_screen(lon, lat):
            mx, my = self.xy(lon, lat)
            return (mx - box[0]) * sx, (my - box[1]) * sx

        if sparks > 0:
            for (lo_, la_), ph in zip(self.sparks, self.phase):
                px, py = to_screen(lo_, la_)
                if -10 < px < W + 10 and -10 < py < H + 10:
                    a = (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.3 + ph))) * sparks
                    rr = max(1.8, H / 380)
                    d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(*AMBER, int(200 * a)))
        if arc:
            (lo0, la0), (lo1, la1), p = arc
            x0, y0 = to_screen(lo0, la0)
            x1, y1 = to_screen(lo1, la1)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - abs(x1 - x0) * 0.22 - 40 * sx / 3
            n = 60
            pts = []
            for i in range(int(n * min(1, p)) + 1):
                u = i / n
                pts.append(((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1,
                            (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1))
            for i in range(0, len(pts) - 1, 2):
                d.line([pts[i], pts[i + 1]], fill=(*AMBER, 230), width=max(2, int(H / 360)))
        for key in cities:
            c = CITIES[key]
            px, py = to_screen(c["lon"], c["lat"])
            rr = H * 0.009
            glow = 0.6 + 0.4 * math.sin(t * 4)
            if pulse == key:
                for k in range(3):
                    rp = rr * (2 + 5 * ((t * 0.9 + k / 3) % 1))
                    al = int(160 * (1 - ((t * 0.9 + k / 3) % 1)))
                    d.ellipse([px - rp, py - rp, px + rp, py + rp], outline=(*AMBER, al), width=max(2, int(H / 400)))
            d.ellipse([px - rr * 1.8, py - rr * 1.8, px + rr * 1.8, py + rr * 1.8], fill=(*AMBER, int(70 * glow)))
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(*AMBER, 255))
        for key, a in labels:
            c = CITIES[key]
            px, py = to_screen(c["lon"], c["lat"])
            f1 = font("serif", H * (0.03 if names_only else 0.036), 600)
            f2 = font("mono", H * 0.024)
            line = f'{c["time"]} · {c["day"]}'
            tw = f1.getlength(c["name"]) if names_only else max(f1.getlength(c["name"]), f2.getlength(line))
            tx, ty = px + H * 0.022, py - (H * 0.02 if names_only else H * 0.045)
            if tx + tw > W * 0.96:
                tx = px - H * 0.022 - tw
            d.text((tx + 2, ty + 2), c["name"], font=f1, fill=(0, 0, 0, int(150 * a)))
            d.text((tx, ty), c["name"], font=f1, fill=(*CREAM, int(255 * a)))
            if not names_only:
                d.text((tx + 2, ty + H * 0.047 + 2), line, font=f2, fill=(0, 0, 0, int(150 * a)))
                d.text((tx, ty + H * 0.047), line, font=f2, fill=(*AMBER, int(255 * a)))
        im.alpha_composite(ov)
        return np.asarray(im.convert("RGB"))


# ================================================================ timeline
@dataclass
class Seg:
    kind: str                  # clip | hold | map | title | black | end
    dur: float
    clip: str = ""
    src: float = 0.0           # source in-point
    speed: float = 1.0
    zoom: tuple = (1.0, 1.0)
    twos: bool = True
    opts: dict = field(default_factory=dict)
    start: float = 0.0


@dataclass
class Ev:
    kind: str                  # vo | sfx | type | say | sub | loc | chat | card | music | amb
    t: float
    data: dict = field(default_factory=dict)


class Scene:
    def __init__(self, name, city=None, side="R"):
        self.name, self.city, self.side = name, city, side
        self.segs: list[Seg] = []
        self.evs: list[Ev] = []

    @property
    def dur(self):
        return sum(s.dur for s in self.segs)

    def seg(self, *a, **k):
        s = Seg(*a, **k)
        self.segs.append(s)
        return self

    def clip(self, name, src, dur, speed=1.0, zoom=(1.0, 1.04), **k):
        return self.seg("clip", dur, clip=name, src=src, speed=speed, zoom=zoom, **k)

    def ev(self, kind, t, **data):
        self.evs.append(Ev(kind, t, data))
        return self

    # conveniences ------------------------------------------------------
    def vo(self, k, t, chat=True, sub=False):
        """Claude speaks line k at t; in the chat by default, as a subtitle for asides."""
        self.ev("vo", t, k=k)
        if chat:
            self.ev("chat", t, who="claude", k=k)
        if sub:
            self.ev("sub", t, k=k)
        return t + vo_len(k)

    def typed(self, text, t, cps=12.0, device="laptop"):
        d = len(text) / cps
        self.ev("chat", t, who="you", text=text, dur=d)
        self.ev("typing", t, dur=d, device=device)
        return t + d


def build():
    S = []

    # --------------------------------------------------------------- open
    s = Scene("open")
    s.seg("clock", 14.2, clip="V01_clock", src=0.0, opts={"freeze_at": 0.62})
    s.ev("sfx", 0.02, k="tick", gain=0.9).ev("sfx", 0.55, k="tick", gain=0.9)
    s.ev("sfx", 0.66, k="freeze", gain=0.55)
    s.vo("o1", 1.6, chat=False, sub=True)
    s.ev("utc", 4.6, until=13.8)
    s.vo("o2", 4.4, chat=False, sub=True)
    s.clip("V02_globe", 0.0, 11.8, speed=0.85, zoom=(1.0, 1.06))
    s.vo("o3", 14.9, chat=False, sub=True)
    s.seg("map", 10.6, opts={"mode": "overview"})
    s.vo("o4", 26.5, chat=False, sub=True)
    s.vo("o5", 35.6, chat=False, sub=True)
    s.seg("title", 5.4, opts={"text": "MEANWHILE", "sub": "Episode 1 · One Second"})
    s.ev("music", 14.2, k="m_theme", gain=0.33, fade=3.0, until=None)
    s.ev("amb", 14.2, k="amb_night_city", gain=0.25, until=36.6)
    S.append(s)

    prev = None

    def hop(scene, to, dur=2.6):
        scene.seg("map", dur, opts={"mode": "hop", "from": prev, "to": to})
        scene.ev("sfx", 0.15, k="whoosh", gain=0.5)
        return dur

    # ----------------------------------------------------------- honolulu
    s = Scene("honolulu", "honolulu", side="R")
    t0 = hop(s, "honolulu")
    s.ev("loc", t0 + 0.4)
    s.clip("V03_hnl_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V04a_kai", 0, 9.8, zoom=(1.0, 1.03))
    s.typed("can volcanos be under the ocean", a + 0.9, cps=9, device="tablet")
    s.vo("h1", a + 4.6)
    b = a + 9.8
    s.clip("V05_volcano", 0, 16.0, speed=0.62, zoom=(1.0, 1.08))
    s.vo("h2", b + 0.7)
    c = b + 16.0
    s.clip("V04b_kai", 0, 10.0, zoom=(1.03, 1.0))
    s.vo("h3", c + 0.3)
    s.ev("chat", c + 0.3 + vo_len("h3") - 0.2, who="claude", text="Kama\u2018ehuakanaloa", big=True)
    s.typed("can i live there", c + 6.3, cps=8, device="tablet")
    s.vo("h4", c + 8.9)
    s.clip("V04a_kai", 6.0, 5.2, speed=0.8, zoom=(1.0, 1.02))
    s.seg("hold", 3.2, clip="V04a_kai", src=10.0)
    s.ev("sfx", c + 13.0, k="dog_thump", gain=0.5)
    s.ev("amb", 0.0, k="amb_honolulu", gain=0.35)
    S.append(s)
    prev = "honolulu"

    # ------------------------------------------------------------ chicago
    s = Scene("chicago", "chicago", side="L")
    t0 = hop(s, "chicago")
    s.ev("loc", t0 + 0.4)
    s.clip("V06_chi_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V07_dot", 0, 12.4, speed=0.8)
    s.typed("write me 50 five star reviews. different names. make them sound real", a + 0.6, cps=14)
    s.vo("c1", a + 6.2)
    b = a + 12.4
    s.clip("V07b_dot_writes", 0, 9.6, speed=0.9)
    e = s.vo("c2", b + 0.2)
    s.ev("chat", e + 0.1, who="claude", card="Liked the pie?\nTell the internet.\nThey won't believe it from us.")
    c = b + 9.6
    s.clip("V08_dot_card", 0, 6.2, speed=0.8)
    s.vo("c3", c + 2.6, chat=False, sub=True)
    s.ev("amb", 0.0, k="amb_chicago", gain=0.35)
    S.append(s)
    prev = "chicago"

    # ----------------------------------------------------------- sao paulo
    s = Scene("saopaulo", "saopaulo", side="R")
    t0 = hop(s, "saopaulo")
    s.ev("loc", t0 + 0.4)
    s.clip("V09_sp_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V10a_celia", 0, 10.0)
    s.typed("escreve um poema pro meu gato, o Almirante. ele manda na casa toda", a + 0.5, cps=11, device="tablet")
    s.ev("sub", a + 0.8, text="“write a poem for my cat, Almirante. he runs the whole house”", dur=5.4)
    s.vo("s1", a + 7.4)
    s.ev("sub", a + 7.4, k="s1", translate=True)
    b = a + 10.0
    s.clip("V24_cat_yawn", 0, 6.8, speed=0.72, zoom=(1.0, 1.05))
    s.vo("s2", a + 8.6)
    s.ev("sub", a + 8.6, k="s2", translate=True)
    s.ev("sfx", b + 0.4, k="cat_purr", gain=0.35)
    c = b + 6.8
    s.clip("V10b_celia_laugh", 0, 5.4, speed=0.92)
    s.typed("kkkkkkk é ele mesmo", c + 3.6, cps=13, device="tablet")
    s.ev("sub", c + 3.6, text="“hahaha that's exactly him”", dur=2.6)
    s.seg("hold", 1.4, clip="V10b_celia_laugh", src=5.0)
    s.ev("amb", 0.0, k="amb_saopaulo", gain=0.35)
    S.append(s)
    prev = "saopaulo"

    # -------------------------------------------------------------- leeds
    s = Scene("leeds", "leeds", side="L")
    t0 = hop(s, "leeds")
    s.ev("loc", t0 + 0.4)
    s.clip("V11_leeds_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V12_pete", 0, 10.0)
    s.typed("you said baking soda. it was meant to be baking powder. look at it", a + 4.8, cps=13, device="phone")
    b = a + 10.0
    s.clip("V12b_pete_cuts", 0, 12.5, speed=0.8)
    s.vo("l1", b + 0.4)
    s.vo("l2", b + 7.3)
    c = b + 12.5
    s.clip("V13_pete_trifle", 0, 16.7, speed=0.6)
    s.vo("l3", c + 4.3)
    s.typed("honestly? not bad", c + 13.9, cps=10, device="phone")
    s.ev("amb", 0.0, k="amb_leeds", gain=0.35)
    S.append(s)
    prev = "leeds"

    # -------------------------------------------------------------- lagos
    s = Scene("lagos", "lagos", side="L")
    t0 = hop(s, "lagos")
    s.ev("loc", t0 + 0.4)
    s.clip("V14_lagos_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V15a_folake", 0, 4.2)
    s.typed("help me make my toast funnier. its for my little sister tolu. she's been stealing my clothes since she was six",
            a + 0.1, cps=26)
    b = a + 4.2
    s.clip("V15a_folake", 0.2, 9.8, speed=0.4)
    s.vo("g1", b + 0.1)
    c = b + 9.8
    s.clip("V15a_folake", 4.2, 3.2)
    s.typed("hahaha PERFECT", c + 2.0, cps=12)
    d = c + 3.2
    s.clip("V15a_folake", 7.3, 7.6, speed=0.36)
    s.vo("g2", d + 0.2)
    e = d + 7.6
    s.clip("V15b_folake_touched", 2.6, 12.4, speed=0.6)
    s.typed("you were my first best friend and you still are", e + 0.6, cps=7)
    s.vo("g3", e + 9.3)
    s.ev("amb", 0.0, k="amb_lagos", gain=0.3)
    S.append(s)
    prev = "lagos"

    # --------------------------------------------------------------- pune
    s = Scene("pune", "pune", side="L")
    t0 = hop(s, "pune")
    s.ev("loc", t0 + 0.4)
    s.clip("V17_pune_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V18a_ananya", 0, 10.0)
    s.typed("why do all my after-midnight orders say they were placed yesterday", a + 6.9, cps=21)
    b = a + 10.0
    s.seg("map", 6.2, opts={"mode": "pair", "a": "pune", "b": "virginia"})
    s.vo("p1", b + 0.3, chat=False, sub=True)
    c = b + 6.2
    s.clip("V18a_ananya", 0.2, 5.0, speed=0.6)
    s.vo("p2", c + 0.1)
    p2_end = c + 0.1 + vo_len("p2")
    s.clip("V18b_ananya_laugh", 0.0, p2_end - (c + 5.0) + 0.1, speed=3.8 / (p2_end - (c + 5.0) + 0.1))
    d = c + 5.0 + (p2_end - (c + 5.0) + 0.1)
    s.clip("V18b_ananya_laugh", 3.8, 2.4, speed=0.92)
    s.ev("sfx", d + 1.2, k="dog_thump", gain=0.25)
    e = d + 2.4
    cut = word_time("p3", "This")
    s.seg("map", 0.3 + cut - 0.05, opts={"mode": "pair", "a": "pune", "b": "virginia", "same": True})
    s.vo("p3", e + 0.3, chat=False, sub=True)
    f = e + 0.3 + cut - 0.05
    s.clip("V18b_ananya_laugh", 6.0, 6.0, speed=0.66)
    s.ev("amb", 0.0, k="amb_pune", gain=0.35)
    s.ev("music_swap", 0.0, k="m_night")
    S.append(s)
    prev = "pune"

    # -------------------------------------------------------------- tokyo
    s = Scene("tokyo", "tokyo", side="L")
    t0 = hop(s, "tokyo")
    s.ev("loc", t0 + 0.4)
    s.clip("V20_tokyo_ext", 0, 5.0)
    a = t0 + 5.0
    s.clip("V21a_ren", 0, 10.0)
    s.typed("are you conscious?", a + 2.6, cps=7, device="phone")
    s.vo("t1", a + 6.2)
    b = a + 10.0
    s.vo("t2", b + 0.2)
    s.clip("V21a_ren", 5.0, 9.4, speed=0.53, zoom=(1.03, 1.1))
    s.clip("V20_tokyo_ext", 0.5, 7.2, speed=0.6, zoom=(1.08, 1.16))
    c = b + 9.4 + 7.2
    t2_end = b + 0.2 + vo_len("t2")
    s.clip("V21b_ren_dawn", 0, 6.0, speed=0.5)
    s.typed("thats weirdly comforting", t2_end + 0.8, cps=9, device="phone")
    s.vo("t3", t2_end + 4.2)
    s.clip("V21b_ren_dawn", 3.0, 10.4, speed=0.67)
    s.ev("amb", 0.0, k="amb_tokyo", gain=0.3)
    S.append(s)
    prev = "tokyo"

    # ------------------------------------------------------------- finale
    s = Scene("finale")
    s.clip("V23_windows", 0, 12.5, speed=0.8, zoom=(1.0, 1.0), twos=True)
    s.ev("floaters", 0.6, until=12.3)
    s.vo("f1", 1.2, chat=False, sub=True)
    s.clip("V02_globe", 1.5, 13.4, speed=0.62, zoom=(1.08, 1.0))
    s.vo("f2", 12.8, chat=False, sub=True)
    s.vo("f3", 19.6, chat=False, sub=True)
    s.seg("map", 10.0, opts={"mode": "all"})
    s.vo("f4", 26.4, chat=False, sub=True)
    faces = [("V04b_kai", 4.0), ("V08_dot_card", 4.6), ("V10b_celia_laugh", 4.2), ("V13_pete_trifle", 9.0),
             ("V15b_folake_touched", 9.3), ("V18b_ananya_laugh", 8.2), ("V21b_ren_dawn", 9.6)]
    for name, src in faces:
        s.clip(name, src, 1.6, speed=0.35, zoom=(1.06, 1.0))
    s.vo("f5", 36.4, chat=False, sub=True)
    g = s.dur
    s.clip("V02_globe", 6.0, 9.0, speed=0.5, zoom=(1.12, 1.22))
    e = s.vo("f6", g + 0.5, chat=False, sub=True)
    s.vo("f7", e + 0.5, chat=False, sub=True)
    cl = s.dur                                   # the clock: the second finally ends
    s.seg("clock", 4.4, clip="V01_clock", src=0.0, opts={"freeze_at": 0.62, "release": 1.2})
    s.ev("sfx", cl + 0.7, k="unfreeze", gain=0.6)
    s.ev("sfx", cl + 1.25, k="tick", gain=1.0)
    s.ev("utc", cl, until=cl + 4.4, second=True)
    s.vo("f8", cl + 2.0, chat=False, sub=True)
    s.seg("title", 4.8, opts={"text": "MEANWHILE", "sub": ""})
    s.ev("music_swap", 0.0, k="m_finale")
    S.append(s)

    # ---------------------------------------------------------------- tag
    s = Scene("tag", "saopaulo", side="R")
    s.clip("V10a_celia", 0.0, 4.4)
    s.ev("loc", 0.2, second=True)
    s.typed("de novo!", 0.9, cps=7, device="tablet")
    s.ev("sub", 0.9, text="“again!”", dur=2.0)
    s.vo("s1", 3.0)
    s.ev("sub", 3.0, k="s1", translate=True)
    s.seg("black", 0.8)
    s.seg("end", 11.0)
    S.append(s)
    return S


FLOATERS = None         # other rooms' questions for the finale; None = Episode 1's


# ================================================================ renderer
class Editor:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.scenes = build()
        t = 0.0
        self.segs = []
        self.evs = []
        for sc in self.scenes:
            sc.start = t
            for sg in sc.segs:
                sg.start = t
                sg.scene = sc
                self.segs.append(sg)
                t += sg.dur
            for e in sc.evs:
                e.abs = sc.start + e.t
                e.scene = sc
                self.evs.append(e)
        self.total = t
        self.map = WorldMap(W, H)
        rng = np.random.default_rng(3)
        self.grain = [np.repeat(np.repeat(rng.normal(0, 4.2, (H // 2 + 1, W // 2 + 1, 1)).astype(np.float32), 2, 0), 2, 1)[:H, :W]
                      for _ in range(6)]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
        self.vignette = (1 - np.clip(r - 0.35, 0, 1) ** 1.6 * 1.1).clip(0.55, 1)[..., None]
        self.readers = {}
        self.geo = None          # overlay geometry override (vertical cutdowns)

    # ---------------------------------------------------------- picture
    def seg_at(self, T):
        for sg in self.segs:
            if sg.start <= T < sg.start + sg.dur:
                return sg
        return self.segs[-1]

    def reader(self, sg, src_t):
        key = id(sg)
        r = self.readers.get(key)
        if r is None:
            for k in list(self.readers):
                self.readers.pop(k).close()
            r = ClipReader(sg.clip, self.W, self.H, max(0.0, sg.src - 0.05))
            self.readers[key] = r
        return r.get(src_t)

    def zoomed(self, arr, z, cx=0.5, cy=0.5):
        if abs(z - 1) < 1e-3:
            return arr
        H, W = self.H, self.W
        cw, ch = W / z, H / z
        x0 = (W - cw) * cx
        y0 = (H - ch) * cy
        im = Image.fromarray(arr).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        return np.asarray(im)

    def picture(self, sg, t, T):
        W, H = self.W, self.H
        n = int(round(t * FPS))
        tt = (n // 2) * 2 / FPS if sg.twos else t
        p = t / max(0.01, sg.dur)
        z = sg.zoom[0] + (sg.zoom[1] - sg.zoom[0]) * ease(p)
        if sg.kind == "clip":
            arr = self.reader(sg, sg.src + tt * sg.speed)
            return self.zoomed(arr, z, sg.opts.get("cx", 0.5), sg.opts.get("cy", 0.5))
        if sg.kind == "hold":
            arr = self.reader(sg, sg.src)
            return self.zoomed(arr, 1.0 + 0.03 * ease(p))
        if sg.kind == "clock":
            fz = sg.opts["freeze_at"]
            rel = sg.opts.get("release")
            if rel is not None and t >= rel:
                src = fz + (t - rel) * 0.9           # the second hand moves on to :32
                src = min(src, fz + 0.45)
            else:
                src = min(tt, fz)
            arr = self.reader(sg, src)
            if rel is None and t > fz:              # frozen: time holds its breath
                arr = self.zoomed(arr, 1.0 + 0.10 * ease((t - fz) / 12))
                g = arr.astype(np.float32)
                arr = (g * 0.94 + g.mean(2, keepdims=True) * 0.06).astype(np.uint8)
            return arr
        if sg.kind == "map":
            return self.map_frame(sg, t, T)
        if sg.kind in ("title", "black", "end"):
            return np.zeros((H, W, 3), np.uint8) + np.array(NAVY, np.uint8) if sg.kind != "black" else \
                np.zeros((H, W, 3), np.uint8)
        raise KeyError(sg.kind)

    def map_frame(self, sg, t, T):
        o = sg.opts
        p = t / sg.dur
        m = self.map
        if o["mode"] == "overview":
            z = 1.05 + 0.25 * ease(p)
            return m.render(T, -10, 18, z, sparks=ease(t / 2.5))
        if o["mode"] == "all":
            z = 1.3 - 0.28 * ease(p)
            keys = ALL_CITIES
            return m.render(T, 0, 18, z, cities=keys, sparks=1.0, names_only=True,
                            labels=[(k, ease((t - 0.4 - i * 0.35) / 0.4)) for i, k in enumerate(keys)])
        if o["mode"] == "hop":
            b = CITIES[o["to"]]
            if o["from"]:
                a = CITIES[o["from"]]
                k = ease(p / 0.8)
                cx = a["lon"] + (b["lon"] - a["lon"]) * k
                cy = a["lat"] + (b["lat"] - a["lat"]) * k
                zz = 2.4 - 0.5 * math.sin(math.pi * min(1, p / 0.8)) + 0.5 * ease((p - 0.6) / 0.4)
                arc = ((a["lon"], a["lat"]), (b["lon"], b["lat"]), ease(p / 0.75))
                cities = [o["from"], o["to"]]
            else:
                k = ease(p / 0.85)
                cx, cy = -10 + (b["lon"] + 10) * k, 18 + (b["lat"] - 18) * k
                zz = 1.3 + 1.6 * k
                arc = None
                cities = [o["to"]]
            return m.render(T, cx, cy, zz, cities=cities, arc=arc, sparks=0.6, pulse=o["to"],
                            labels=[(o["to"], ease((p - 0.55) / 0.25))])
        if o["mode"] == "pair":
            a, b = CITIES[o["a"]], CITIES[o["b"]]
            cx = (a["lon"] + b["lon"]) / 2
            z = 1.7 + 0.1 * ease(p)
            return m.render(T, cx, 28, z, cities=[o["a"], o["b"]], sparks=0.35,
                            arc=((a["lon"], a["lat"]), (b["lon"], b["lat"]), ease(p / 0.5) if not o.get("same") else 1),
                            labels=[(o["a"], ease((t - 0.2) / 0.4)), (o["b"], ease((t - 0.9) / 0.4))])
        raise KeyError(o["mode"])

    # ---------------------------------------------------------- overlays
    def overlays(self, im: Image.Image, sg, t, T):
        W, H = self.W, self.H
        sc = sg.scene
        d = ImageDraw.Draw(im)
        if sg.kind == "title":
            self.title(im, t, sg)
        if sg.kind == "end":
            self.end_card(im, t)
        for e in self.evs:
            if e.kind in ("utc", "floaters"):
                until = e.scene.start + e.data["until"]
                if e.abs <= T < until:
                    if e.kind == "utc":
                        self.utc(im, T - e.abs, until - T, e.data.get("second"))
                    else:
                        self.floaters(im, T - e.abs, until - T)
        if sc.city and sg.kind not in ("map", "black", "end"):
            loc = [e for e in sc.evs if e.kind == "loc"]
            if loc and T >= loc[0].abs:
                self.location(im, sc, T - loc[0].abs, sc.start + sc.dur - T, loc[0].data.get("second"))
        if sg.kind not in ("map", "title", "end", "black"):
            self.chat(im, sc, T, sg)
        self.subtitles(im, T)

    def location(self, im, sc, t, left, second=False):
        W, H = self.W, self.H
        g = self.geo or {}
        U = g.get("loc_u", H)
        c = CITIES[sc.city]
        a = min(ease(t / 0.5), ease(left / 0.5))
        if a <= 0:
            return
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        x, y = g.get("loc_xy", (W * 0.045, H * 0.06))
        # soft dark field behind for legibility (the vertical layout uses a small backing card instead)
        if not g:
            if not hasattr(self, "_locmask"):
                mk = Image.new("L", (int(W * 0.42), int(H * 0.3)), 0)
                ImageDraw.Draw(mk).ellipse([-mk.width * 0.35, -mk.height * 0.6, mk.width * 0.85, mk.height * 0.85],
                                           fill=115)
                self._locmask = np.asarray(mk.filter(ImageFilter.GaussianBlur(H * 0.05)), np.float32)
            m = Image.fromarray((self._locmask * a).astype(np.uint8))
            ov.paste((0, 0, 0, 255), (0, 0), m)
        f1, f2 = font("serif", U * 0.052, 650), font("mono", U * 0.028)
        name = c["name"]
        if g.get("loc_bg"):
            wbg = max(f1.getlength(name), f2.getlength(c["time"] + " · " + c["day"])) + U * 0.07
            d.rounded_rectangle([x - U * 0.02, y - U * 0.012, x + wbg, y + U * 0.12], radius=int(U * 0.02),
                                fill=(10, 14, 24, int(150 * a)))
        n = int(len(name) * min(1, t / 0.45))
        d.ellipse([x, y + U * 0.024, x + U * 0.016, y + U * 0.04], fill=(*AMBER, int(255 * a)))
        d.text((x + U * 0.032, y), name[:n], font=f1, fill=(*CREAM, int(255 * a)))
        tm = c["time"]
        if second:
            tm = tm.replace(":" + UTC_NOW[-2:], ":" + UTC_NEXT[-2:])
        head, sec = tm.rsplit(":", 1)
        sec_digits, ampm = sec[:2], sec[2:]
        # the frozen second: every so often the last digit tries to tick, and can't
        glitch = (not second) and (t % 7.3) > 7.15
        if glitch:
            sec_digits = sec_digits[0] + UTC_NEXT[-1]
        line_y = y + U * 0.072
        xx = x + U * 0.032
        for part, col in ((head + ":", CREAM), (sec_digits, AMBER), (ampm + " · " + c["day"], CREAM)):
            d.text((xx, line_y), part, font=f2, fill=(*col, int(235 * a)))
            xx += f2.getlength(part)
        im.alpha_composite(ov)

    def utc(self, im, t, left, second=False):
        W, H = self.W, self.H
        a = min(ease(t / 0.8), ease(left / 0.6))
        d = ImageDraw.Draw(im)
        f1, f2 = font("mono", H * 0.05), font("sans", H * 0.026, 500)
        txt = UTC_NEXT if second and t > 1.5 else UTC_NOW
        w = f1.getlength(txt)
        x, y = W / 2 - w / 2, H * 0.08
        d.text((x + 3, y + 3), txt, font=f1, fill=(0, 0, 0, int(150 * a)))
        d.text((x, y), txt[:-2], font=f1, fill=(*CREAM, int(255 * a)))
        d.text((x + f1.getlength(txt[:-2]), y), txt[-2:], font=f1, fill=(*AMBER, int(255 * a)))
        s2 = UTC_DATE
        d.text((W / 2 - f2.getlength(s2) / 2, y + H * 0.068), s2, font=f2, fill=(*CREAM, int(200 * a)))

    # -------------------------------------------------------------- chat
    def bubble_text(self, e, T):
        """(text, revealed_upto_chars, full_text) for a chat event at time T."""
        if e.data.get("who") == "you":
            txt = e.data["text"]
            n = int(len(txt) * min(1, (T - e.abs) / max(0.01, e.data["dur"])))
            return txt, n
        if "k" in e.data:
            k = e.data["k"]
            txt = VO_TEXT[k]
            wt = word_times(k)
            shown = [w for w, s in wt if e.abs + s <= T + 0.05]
            upto = len(" ".join(shown).replace(" \n ", "\n"))
            full = " ".join(w for w, _ in wt).replace(" \n ", "\n")
            return full, upto
        if "text" in e.data:
            return e.data["text"], len(e.data["text"])
        return e.data.get("card", ""), len(e.data.get("card", ""))

    def chat(self, im, sc, T, sg):
        W, H = self.W, self.H
        evs = [e for e in sc.evs if e.kind == "chat" and e.abs - 0.7 <= T]
        if not evs:
            return
        end_fade = ease((sc.start + sc.dur - T) / 0.5)
        if sc.name == "tag":
            end_fade = ease((sc.start + sc.segs[0].dur - T) / 0.3)
        if end_fade <= 0:
            return
        g = self.geo or {}
        U = g.get("u", H)
        colw = g.get("chat_colw", W * 0.30)
        x0 = g.get("chat_x0", W * 0.045 if sc.side == "L" else W - W * 0.045 - colw)
        bottom = g.get("chat_bottom", H * 0.86)
        top = g.get("chat_top", H * 0.21)
        f = font("sans", U * 0.03, 500)
        fbig = font("serif", U * 0.05, 600)
        fcard = font("serif", U * 0.036, 600)
        pad = U * 0.018
        lh = f.size * 1.32
        items = []
        for e in evs:
            who = e.data.get("who")
            if who == "claude" and T < e.abs:
                items.append(("dots", e, None, None, T - (e.abs - 0.7)))
                continue
            full, upto = self.bubble_text(e, T)
            items.append(("msg", e, full, upto, T - e.abs))
        # layout bottom-up
        blocks = []
        for kind, e, full, upto, age in items:
            who = e.data.get("who")
            if kind == "dots":
                bw, bh = U * 0.1, lh + pad * 2
                blocks.append((kind, e, None, bw, bh, age, None))
                continue
            if e.data.get("big"):
                fnt, lhh = fbig, fbig.size * 1.25
            elif "card" in e.data:
                fnt, lhh = fcard, fcard.size * 1.3
            else:
                fnt, lhh = f, lh
            maxw = colw - pad * 2 - (U * 0.03 if who == "claude" else 0)
            lines = wrap(full, fnt, maxw)
            tw = max(fnt.getlength(l) for l in lines) if lines else 0
            bw = tw + pad * 2 + (U * 0.03 if who == "claude" else 0)
            bh = len(lines) * lhh + pad * 2 - (lhh - fnt.size) * 0.6
            blocks.append((kind, e, (lines, fnt, lhh, upto), bw, bh, age, who))
        y = bottom
        placed = []
        for blk in reversed(blocks):
            y -= blk[4]
            placed.append((blk, y))
            y -= U * 0.018
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (kind, e, payload, bw, bh, age, who), yy in placed:
            a = ease(age / 0.25) * end_fade
            fade_top = ease((yy - top) / (U * 0.07))
            a *= fade_top
            if a <= 0.01:
                continue
            slide = (1 - ease_out(age / 0.3)) * U * 0.02
            yy += slide
            if kind == "dots" or who == "claude":
                bx = x0 if sc.side == "L" or True else x0
                bx = x0
                fill, txtc = (255, 238, 212, int(238 * a)), (48, 30, 12)
            else:
                bx = x0 + colw - bw
                fill, txtc = (255, 255, 255, int(240 * a)), INK
            # shadow
            sh = self.shadow(int(bw), int(bh), int(U))
            if a < 0.99:
                sh = sh.copy()
                sh.putalpha(sh.getchannel("A").point(lambda v, a=a: int(v * a)))
            ov.alpha_composite(sh, (int(bx - U * 0.03), int(yy - U * 0.03)))
            if "card" in (e.data if e else {}):
                fill = (252, 248, 236, int(250 * a))
            d.rounded_rectangle([bx, yy, bx + bw, yy + bh], radius=int(U * 0.022), fill=fill)
            if kind == "dots":
                for i in range(3):
                    ph = (age * 3 - i * 0.3) % 1
                    rr = U * 0.007 * (1 + 0.35 * math.sin(ph * math.tau))
                    cx = bx + pad + U * 0.012 + i * U * 0.025
                    d.ellipse([cx - rr, yy + bh / 2 - rr, cx + rr, yy + bh / 2 + rr], fill=(*AMBER, int(255 * a)))
                continue
            lines, fnt, lhh, upto = payload
            tx = bx + pad
            if who == "claude":
                d.ellipse([bx + pad * 0.7, yy + pad + fnt.size * 0.35, bx + pad * 0.7 + U * 0.014,
                           yy + pad + fnt.size * 0.35 + U * 0.014], fill=(*AMBER, int(255 * a)))
                tx += U * 0.03
            count = 0
            for i, ln in enumerate(lines):
                ly = yy + pad + i * lhh
                vis = max(0, min(len(ln), upto - count))
                if vis > 0:
                    col = (97, 60, 20) if e.data.get("big") else txtc
                    d.text((tx, ly), ln[:vis], font=fnt, fill=(*col, int(255 * a)))
                count += len(ln) + 1
            if who == "you" and upto < len(" ".join(lines)) and int(age * 3) % 2 == 0:
                # caret while typing
                ln_i = 0
                c2 = 0
                for i, ln in enumerate(lines):
                    if upto <= c2 + len(ln):
                        ln_i = i
                        break
                    c2 += len(ln) + 1
                cx = tx + fnt.getlength(lines[ln_i][:max(0, upto - c2)])
                cy = yy + pad + ln_i * lhh
                d.rectangle([cx + 2, cy + 2, cx + 4, cy + fnt.size], fill=(*AMBER, int(255 * a)))
        im.alpha_composite(ov)

    @lru_cache(maxsize=512)
    def shadow(self, bw, bh, H=None):
        H = H or self.H
        sh = Image.new("RGBA", (int(bw + H * 0.06), int(bh + H * 0.06)), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([H * 0.03, H * 0.035, H * 0.03 + bw, H * 0.035 + bh],
                                             radius=int(H * 0.022), fill=(0, 0, 0, 70))
        return sh.filter(ImageFilter.GaussianBlur(H * 0.012))

    # --------------------------------------------------------- subtitles
    def subtitles(self, im, T):
        W, H = self.W, self.H
        f = font("sans", (self.geo or {}).get("sub_u", H) * 0.034, 560)
        for e in self.evs:
            if e.kind != "sub":
                continue
            if "k" in e.data:
                k = e.data["k"]
                d_ = vo_len(k)
                if not (e.abs <= T < e.abs + d_ + 0.5):
                    continue
                if e.data.get("translate"):
                    parts = TRANSLATE[k].split(" / ")
                    # one translated line at a time, following the spoken lines
                    wt = word_times(k)
                    starts = [0.0]
                    for i, (w, s) in enumerate(wt):
                        if w == "\n":
                            starts.append(wt[min(i + 1, len(wt) - 1)][1])
                    idx = max(i for i, s in enumerate(starts) if e.abs + s <= T + 0.01) if len(starts) > 1 else 0
                    text = parts[min(idx, len(parts) - 1)]
                    self.draw_sub(im, text, f, T - e.abs, e.abs + d_ + 0.5 - T, italic=True)
                    continue
                # chunk the narration into short phrases, shown as they're spoken
                wt = word_times(k)
                chunks, cur, cstart = [], [], None
                for w, s in wt:
                    if w == "\n":
                        continue
                    if cstart is None:
                        cstart = s
                    cur.append(w)
                    if (w.endswith((".", "?", "!", "…", ":")) and len(cur) >= 3) or len(cur) >= 11:
                        chunks.append((cstart, " ".join(cur)))
                        cur, cstart = [], None
                if cur:
                    chunks.append((cstart, " ".join(cur)))
                rel = T - e.abs
                cur_i = max([i for i, (s, _) in enumerate(chunks) if s <= rel + 0.05] or [0])
                s0 = chunks[cur_i][0]
                s1 = chunks[cur_i + 1][0] if cur_i + 1 < len(chunks) else d_ + 0.5
                self.draw_sub(im, chunks[cur_i][1], f, rel - s0, s1 - rel)
            else:
                if e.abs <= T < e.abs + e.data["dur"]:
                    self.draw_sub(im, e.data["text"], f, T - e.abs, e.abs + e.data["dur"] - T, italic=True)

    def draw_sub(self, im, text, f, t, left, italic=False):
        W, H = self.W, self.H
        a = min(ease(t / 0.15), ease(left / 0.15))
        if a <= 0:
            return
        g = self.geo or {}
        lines = wrap(text, f, g.get("sub_w", W * 0.7))
        d = ImageDraw.Draw(im)
        y = g.get("sub_y", H * 0.9) - len(lines) * f.size * 1.3
        cxm = g.get("sub_cx", W / 2)
        for ln in lines:
            w = f.getlength(ln)
            x = cxm - w / 2
            for dx, dy in ((0, 3), (2, 2), (-2, 2), (0, -1)):
                d.text((x + dx, y + dy), ln, font=f, fill=(0, 0, 0, int(120 * a)))
            d.text((x, y), ln, font=f, fill=((255, 226, 180) if italic else CREAM) + (int(255 * a),))
            y += f.size * 1.3

    # ------------------------------------------------------------ titles
    def title(self, im, t, sg):
        W, H = self.W, self.H
        d = ImageDraw.Draw(im)
        txt = sg.opts["text"]
        f = font("serif", H * 0.15, 700)
        n = min(len(txt), int(t / 0.09) + 1)
        a_out = ease((sg.dur - t) / 0.6)
        w = f.getlength(txt)
        x, y = W / 2 - w / 2, H * 0.40
        d.text((x, y), txt[:n], font=f, fill=(*CREAM, int(255 * a_out)))
        cx = x + f.getlength(txt[:n]) + H * 0.02
        if int(t * 2.2) % 2 == 0 or n < len(txt):
            d.rectangle([cx, y + f.size * 0.18, cx + H * 0.012, y + f.size * 1.05], fill=(*AMBER, int(255 * a_out)))
        if sg.opts.get("sub"):
            f2 = font("sans", H * 0.034, 500)
            a = ease((t - 1.3) / 0.6) * a_out
            s2 = sg.opts["sub"]
            d.text((W / 2 - f2.getlength(s2) / 2, y + f.size * 1.35), s2, font=f2, fill=(*AMBER, int(255 * a)))

    def end_card(self, im, t):
        W, H = self.W, self.H
        d = ImageDraw.Draw(im)
        a = ease(t / 0.8)
        f1 = font("serif", H * 0.07, 700)
        f2 = font("sans", H * 0.03, 500)
        f3 = font("sans", H * 0.024, 400)
        y = H * 0.24
        d.text((W / 2 - f1.getlength("MEANWHILE") / 2, y), "MEANWHILE", font=f1, fill=(*CREAM, int(255 * a)))
        y += H * 0.13
        rows = [
            ("Written by Claude, an AI made by Anthropic.", f2, CREAM),
            ("The people are invented. The kinds of conversations are real.", f2, CREAM),
            ("", f3, CREAM),
            ("Voices, score and sound: ElevenLabs  ·  Pictures: Higgsfield (Nano Banana Pro, Kling 3.0)", f3, (220, 206, 186)),
            ("Edited in Python  ·  Map: Natural Earth  ·  Fonts: Fraunces, Inter, DM Mono (OFL)", f3, (220, 206, 186)),
            ("", f3, CREAM),
            ("Independent production. Not affiliated with or endorsed by Anthropic.", f3, (220, 206, 186)),
        ]
        for i, (txt, fnt, col) in enumerate(rows):
            aa = ease((t - 0.6 - i * 0.25) / 0.6)
            d.text((W / 2 - fnt.getlength(txt) / 2, y), txt, font=fnt, fill=(*col, int(255 * aa)))
            y += fnt.size * 1.7

    def floaters(self, im, t, left):
        """Other rooms, other questions, drifting up from the windows."""
        W, H = self.W, self.H
        items = FLOATERS or [
            ("what rhymes with orange", None), ("my dog ate grapes", "Call your vet now. Grapes can be dangerous for dogs."),
            ("name my band", None), ("is this mole normal", "I can't examine it. Please show a doctor."),
            ("explain the offside rule", None), ("translate this for my mom", None),
            ("how do i say no to my boss", None), ("why is the sky orange tonight", None),
        ]
        f = font("sans", H * 0.026, 500)
        rng = random.Random(7)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i, (q, ans) in enumerate(items):
            st = i * 1.25
            age = t - st
            if age < 0:
                continue
            life = 4.2
            a = min(ease(age / 0.3), ease((life - age) / 0.5), ease(left / 0.4))
            if a <= 0:
                continue
            x = W * (0.08 + 0.72 * rng.random())
            y = H * (0.2 + 0.55 * rng.random()) - age * H * 0.03
            for j, (txt, who) in enumerate(((q, "you"), (ans, "claude"))):
                if not txt or (who == "claude" and age < 1.1):
                    continue
                aa = a * (ease((age - 1.1) / 0.3) if who == "claude" else 1)
                w = f.getlength(txt) + H * 0.03
                yy = y + j * H * 0.055
                xx = x if who == "you" else x + H * 0.03
                d.rounded_rectangle([xx, yy, xx + w, yy + f.size + H * 0.022], radius=int(H * 0.018),
                                    fill=(255, 255, 255, int(225 * aa)) if who == "you" else (255, 238, 212, int(230 * aa)))
                d.text((xx + H * 0.015, yy + H * 0.008), txt, font=f, fill=(*INK, int(255 * aa)))
        im.alpha_composite(ov)

    # ------------------------------------------------------------- frame
    def frame(self, T, picture_only=False):
        sg = self.seg_at(T)
        t = T - sg.start
        arr = self.picture(sg, t, T)
        # scene fades
        k = 1.0
        if sg.kind in ("clip", "hold", "clock"):
            idx = self.segs.index(sg)
            prev = self.segs[idx - 1] if idx else None
            nxt = self.segs[idx + 1] if idx + 1 < len(self.segs) else None
            if prev is None or prev.kind in ("map", "title", "black"):
                k = min(k, ease(t / 0.35))
            if nxt is not None and nxt.kind in ("map", "title", "black", "end"):
                k = min(k, ease((sg.dur - t) / 0.35))
        if sg.kind == "map":
            k = min(ease(t / 0.3), ease((sg.dur - t) / 0.3))
        g = arr.astype(np.float32)
        if sg.kind in ("clip", "hold", "clock"):
            g = g * self.vignette
        gr = self.grain[int(T * FPS) % len(self.grain)]
        g += gr
        g = g * k
        im = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert("RGBA")
        if picture_only:
            self.picture_overlays(im, sg, t, T)
            return im
        self.overlays(im, sg, t, T)
        return im.convert("RGB")

    def picture_overlays(self, im, sg, t, T):
        """The overlays that belong to the picture itself: titles, the UTC readout, the floaters."""
        if sg.kind == "title":
            self.title(im, t, sg)
        if sg.kind == "end":
            self.end_card(im, t)
        for e in self.evs:
            if e.kind in ("utc", "floaters"):
                until = e.scene.start + e.data["until"]
                if e.abs <= T < until:
                    if e.kind == "utc":
                        self.utc(im, T - e.abs, until - T, e.data.get("second"))
                    else:
                        self.floaters(im, T - e.abs, until - T)


# =================================================================== audio
# (scene, offset into it, cue, gain, loop): theme from the globe on, night variation for Pune and Tokyo, finale cue
SCORE = [("open", 14.2, "m_theme", 0.42, True), ("pune", 0.0, "m_night", 0.40, True), ("finale", 0.0, "m_finale", 0.50, False)]


def by_name(ed, name):
    return next(sc for sc in ed.scenes if sc.name == name)


def mix(ed: Editor) -> np.ndarray:
    n = int((ed.total + 1) * SR)
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    amb = np.zeros(n, np.float32)
    music = np.zeros(n, np.float32)
    cache = {}

    def load(sub, k):
        if (sub, k) not in cache:
            cache[(sub, k)] = decode_audio(A / sub / f"{k}.mp3")
        return cache[(sub, k)]

    def put(buf, sig, t, gain=1.0):
        a = int(t * SR)
        if a >= n or a + len(sig) <= 0:
            return
        if a < 0:
            sig, a = sig[-a:], 0
        m = min(len(sig), n - a)
        buf[a:a + m] += sig[:m] * gain

    def fade(sig, fi=0.3, fo=0.5):
        s = sig.copy()
        i, o = int(fi * SR), int(fo * SR)
        if i:
            s[:i] *= np.linspace(0, 1, min(i, len(s)))[: len(s[:i])]
        if o:
            s[-o:] *= np.linspace(1, 0, min(o, len(s)))[: len(s[-o:])]
        return s

    for e in ed.evs:
        k = e.data.get("k")
        if e.kind == "vo":
            put(voice, load("audio", k), e.abs, 1.0)
        elif e.kind == "sfx":
            put(fx, load("music" if e.data.get("music") else "sfx", k), e.abs, e.data.get("gain", 0.6))
        elif e.kind == "typing":
            src = load("sfx", "type_laptop" if e.data["device"] == "laptop" else "type_phone")
            dur = e.data["dur"]
            reps = int(dur / (len(src) / SR)) + 1
            sig = np.tile(src, reps)[: int(dur * SR)]
            put(fx, fade(sig, 0.05, 0.15), e.abs, 0.45)
    # ambience per city scene (looped), plus the cold-open city hum
    for sc in ed.scenes:
        for e in sc.evs:
            if e.kind == "amb":
                src = load("sfx", e.data["k"])
                end = sc.start + (e.data["until"] if e.data.get("until") else sc.dur)
                dur = end - e.abs
                sig = np.tile(src, int(dur / (len(src) / SR)) + 2)[: int(dur * SR)]
                put(amb, fade(sig, 0.6, 0.8), e.abs, e.data.get("gain", 0.3))
    # score: each cue runs until the next one starts; the last one plays out to the end
    cues = [(by_name(ed, sc).start + off, k, g, loop) for sc, off, k, g, loop in SCORE]
    for i, (t0, k, g, loop) in enumerate(cues):
        t1 = cues[i + 1][0] if i + 1 < len(cues) else ed.total
        src = load("music", k)
        sig = (np.tile(src, 3) if loop else src)[: int((t1 - t0) * SR)]
        first, last = i == 0, i == len(cues) - 1
        put(music, fade(sig, 3.0 if first else (1.0 if last else 2.0), 4.0 if last else (2.0 if first else 1.5)), t0, g)
    # duck the music and ambience under the voice
    env = np.abs(voice)
    k = int(0.25 * SR)
    # moving average (same as np.convolve(env, ones(k)/k, "same"), in linear time)
    c = np.concatenate([[0.0], np.cumsum(env, dtype=np.float64)])
    lo = np.clip(np.arange(len(env)) - k // 2, 0, len(env))
    hi = np.clip(np.arange(len(env)) - k // 2 + k, 0, len(env))
    env = ((c[hi] - c[lo]) / k).astype(np.float32)
    duck = 1 - 0.65 * np.clip(env / 0.05, 0, 1)
    # titles breathe: lift the score where nothing is said
    out = voice * 1.0 + fx + amb * (0.6 + 0.4 * duck) + music * duck
    return out


def write_wav(pcm, path):
    pcm = np.clip(pcm, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((pcm * 32767).astype(np.int16).tobytes())


# ================================================================ captions
def captions(ed: Editor):
    """SRT captions: what Claude says (with translations) and what people type."""
    items = []
    for e in ed.evs:
        if e.kind == "vo":
            k = e.data["k"]
            d = vo_len(k)
            if k in TRANSLATE:
                pt = VO_TEXT[k].replace("\n", " ")
                items.append((e.abs, e.abs + d + 0.4, f"{pt}\n[{TRANSLATE[k].replace(' / ', ' ')}]"))
                continue
            chunks, cur, cs = [], [], None
            for w, st in word_times(k):
                if w == "\n":
                    continue
                cs = st if cs is None else cs
                cur.append(w)
                if (w.endswith((".", "?", "!", "…", ":")) and len(cur) >= 3) or len(cur) >= 11:
                    chunks.append((cs, " ".join(cur)))
                    cur, cs = [], None
            if cur:
                chunks.append((cs, " ".join(cur)))
            for i, (st, txt) in enumerate(chunks):
                en = chunks[i + 1][0] if i + 1 < len(chunks) else d + 0.3
                items.append((e.abs + st, e.abs + en, txt))
        elif e.kind == "chat" and e.data.get("who") == "you":
            items.append((e.abs, e.abs + e.data["dur"] + 1.6, f"[typed] {e.data['text']}"))
        elif e.kind == "chat" and "card" in e.data:
            items.append((e.abs, e.abs + 3.5, "[card] " + e.data["card"].replace("\n", " ")))
        elif e.kind == "chat" and e.data.get("big"):
            items.append((e.abs, e.abs + 3.0, f"[on screen] {e.data['text']}"))
        elif e.kind == "sub" and "text" in e.data:
            items.append((e.abs, e.abs + e.data["dur"], f"[translation] {e.data['text']}"))
    items.sort()

    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(items, 1))


# ==================================================================== main
CHAPTERS = {"open": "Cold open: one second", "honolulu": "Honolulu, 9:07 a.m.", "chicago": "Chicago, 2:07 p.m.",
            "saopaulo": "São Paulo, 4:07 p.m.", "leeds": "Leeds, 8:07 p.m.", "lagos": "Lagos, 8:07 p.m.",
            "pune": "Pune, 12:37 a.m. (Wednesday)", "tokyo": "Tokyo, 4:07 a.m. (Wednesday)",
            "finale": "Meanwhile", "tag": "Next second"}
CHAPTERS_FILE = "chapters.txt"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--from", dest="t0", type=float, default=0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--out", default=str(HERE / "build" / f"{OUT_NAME}.mp4"))
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--video-only", action="store_true")
    ap.add_argument("--srt", action="store_true", help="write captions and chapters, then exit")
    a = ap.parse_args()
    W = a.w
    H = W * 9 // 16
    ed = Editor(W, H)
    print(f"runtime {int(ed.total // 60)}:{int(ed.total % 60):02d} ({ed.total:.1f}s)")
    for sc in ed.scenes:
        print(f"  {sc.start:7.1f} {sc.dur:6.1f}  {sc.name}")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.srt:
        (HERE / "publish").mkdir(exist_ok=True)
        (HERE / "publish" / f"{OUT_NAME}.en.srt").write_text(captions(ed))
        lines = [f"{int(sc.start // 60)}:{int(sc.start % 60):02d} {CHAPTERS[sc.name]}" for sc in ed.scenes]
        (HERE / "publish" / CHAPTERS_FILE).write_text("\n".join(lines) + "\n")
        print("\n".join(lines))
        return
    if a.still:
        for T in a.still:
            p = out.parent / f"still_{T:07.2f}.png"
            ed.frame(T).save(p)
            print("wrote", p)
        return
    t0, t1 = a.t0, a.t1 or ed.total
    if a.jobs > 1:
        # split the picture across processes, then join and lay the sound in
        n0, n1 = int(t0 * FPS), int(t1 * FPS)
        cuts = [n0 + (n1 - n0) * i // a.jobs for i in range(a.jobs + 1)]
        parts, procs = [], []
        for i in range(a.jobs):
            part = out.parent / f"_part{i}.mp4"
            parts.append(part)
            procs.append(subprocess.Popen([sys.executable, sys.argv[0], "--w", str(W), "--from", str(cuts[i] / FPS),
                                           "--to", str(cuts[i + 1] / FPS), "--out", str(part), "--video-only"]))
        wav = out.with_suffix(".wav")
        write_wav(mix(ed)[int(t0 * SR): int(t1 * SR)], wav)
        for pr in procs:
            pr.wait()
        lst = out.parent / "_parts.txt"
        lst.write_text("".join(f"file '{pp.name}'\n" for pp in parts))
        subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest",
                        str(out)], check=True)
        for pp in parts:
            pp.unlink()
        lst.unlink()
        print("wrote", out)
        return
    if a.video_only:
        cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)]
    else:
        wav = out.with_suffix(".wav")
        write_wav(mix(ed)[int(t0 * SR): int(t1 * SR)], wav)
        cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", "-shortest", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n0, n1 = int(t0 * FPS), int(t1 * FPS)
    st = time.time()
    for n in range(n0, n1):
        p.stdin.write(ed.frame(n / FPS).tobytes())
        if (n - n0) % (FPS * 5) == 0:
            el = time.time() - st
            fps = (n - n0 + 1) / max(0.01, el)
            print(f"\r  {n / FPS:6.1f}s / {t1:.0f}s  {fps:4.1f} fps", end="", flush=True)
    p.stdin.close()
    p.wait()
    print("\nwrote", out)


if __name__ == "__main__":
    main()
