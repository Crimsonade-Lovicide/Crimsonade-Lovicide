"""Procedural renderers for the parts of the show that happen inside Claude.

The Room, the Figure, the Margin, the Hallway and the cards are drawn by code
rather than generated: they depict computation, so computation draws them.
Each renderer is a `ShotRenderer` whose `frame(t)` returns an RGB PIL image.
"""
from __future__ import annotations

import math
import random
import re
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import (AMBER, FFMPEG, FONTS, FPS, HUMAN_FRAGMENTS, INK, LABEL_STYLE,
                     NIGHT, PAPER, PAPER_SHADOW, RED)
from .model import Episode, Shot, shot_media


# --------------------------------------------------------------------- utils
@lru_cache(maxsize=256)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS[name]), max(6, int(size)))


def ease_out(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def ease_in_out(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def wrap(text: str, fnt, width: int) -> list[str]:
    out, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= width or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def text_sprite(text: str, fnt, fill, alpha=255, angle=0.0) -> Image.Image:
    l, t, r, b = fnt.getbbox(text)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), text, font=fnt, fill=(*fill, alpha))
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    return im


def paste(base: Image.Image, sprite: Image.Image, cx: float, cy: float, opacity=1.0):
    if opacity <= 0.01:
        return
    if opacity < 0.99:
        sprite = sprite.copy()
        a = sprite.getchannel("A").point(lambda v: int(v * opacity))
        sprite.putalpha(a)
    base.alpha_composite(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2)))


def speech_envelope(shot: Shot, who: str = "CLAUDE"):
    """Returns env(t) in [0,1]: how 'voiced' `who` is at time t in the shot.
    Uses real audio loudness if present, otherwise a syllable-rate stand-in."""
    spans = []
    for ln in shot.lines:
        if ln.who != who:
            continue
        rms = None
        if ln.audio:
            pcm = decode_audio(ln.audio, 8000)
            hop = 8000 // FPS
            if len(pcm) > hop:
                n = len(pcm) // hop
                rms = np.sqrt((pcm[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
                rms = rms / (rms.max() + 1e-6)
        spans.append((ln.start, ln.start + ln.dur, rms))

    def env(t: float) -> float:
        for a, b, rms in spans:
            if a <= t < b:
                if rms is not None:
                    return float(rms[min(len(rms) - 1, int((t - a) * FPS))])
                return 0.55 + 0.45 * abs(math.sin(t * 2 * math.pi * 2.3)) * (0.7 + 0.3 * math.sin(t * 7.1))
        return 0.0
    return env


@lru_cache(maxsize=512)
def decode_audio(path: Path, sr: int) -> np.ndarray:
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


# ------------------------------------------------------------ subtitles
class Subtitler:
    def __init__(self, W, H, enabled=True):
        self.W, self.H, self.enabled = W, H, enabled
        self.f = font("serif", H * 0.036)
        self.fl = font("sans_bold", H * 0.022)

    def draw(self, im: Image.Image, shot: Shot, t: float, dark_bg: bool):
        if not self.enabled:
            return
        for ln in shot.lines:
            if ln.start <= t < ln.start + ln.dur + min(ln.pause, 0.6):
                lines = wrap(ln.text, self.f, int(self.W * 0.72))
                d = ImageDraw.Draw(im)
                lh = self.f.size * 1.25
                y = self.H * 0.90 - lh * (len(lines) - 1)
                fg = PAPER if dark_bg else INK
                if not dark_bg:
                    # the Room's floor fills with words; lift subtitles off it
                    w = max(self.f.getlength(r) for r in lines) + self.H * 0.05
                    top = y - lh * (1.35 if ln.who != "CLAUDE" else 0.95)
                    plate = Image.new("L", im.size, 0)
                    ImageDraw.Draw(plate).rounded_rectangle(
                        [self.W / 2 - w / 2, top, self.W / 2 + w / 2, y + lh * (len(lines) - 1) + lh * 0.45],
                        radius=self.H * 0.02, fill=225)
                    plate = plate.filter(ImageFilter.GaussianBlur(self.H * 0.012))
                    im.paste(Image.new("RGB", im.size, PAPER), (0, 0), plate)
                    d = ImageDraw.Draw(im)
                if ln.who != "CLAUDE":
                    tag = ln.who + (" (V.O.)" if ln.vo else "")
                    d.text((self.W / 2, y - lh * 0.72), tag, font=self.fl,
                           fill=RED if ln.who == "RUTH" else fg, anchor="ms")
                for i, row in enumerate(lines):
                    yy = y + i * lh
                    if dark_bg:
                        d.text((self.W / 2 + 2, yy + 2), row, font=self.f, fill=(0, 0, 0), anchor="ms")
                    d.text((self.W / 2, yy), row, font=self.f, fill=fg, anchor="ms")
                return


# ------------------------------------------------------------- the Room
class RoomSet:
    """Static pieces of the Room at a given resolution (background, figure)."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = self._background()
        self.floor_y = H * 0.70

    def _background(self) -> Image.Image:
        W, H = self.W, self.H
        a = np.zeros((H, W, 3), np.float32)
        a[:] = PAPER
        # floor: slightly deeper paper below the horizon, with soft falloff
        y = np.arange(H)[:, None]
        floor = np.clip((y - H * 0.66) / (H * 0.34), 0, 1)
        a -= (floor ** 0.8 * 16)[..., None] * np.array([1.0, 1.1, 1.3])
        # vignette
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
        a -= (np.clip(r - 0.25, 0, 1) ** 1.6 * 70)[..., None]
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        # the window, and its light
        wx0, wx1, wy0, wy1 = W * 0.73, W * 0.84, H * 0.10, H * 0.60
        glow = Image.new("L", (W, H), 0)
        g = ImageDraw.Draw(glow)
        g.rectangle([wx0, wy0, wx1, wy1], fill=255)
        g.polygon([(wx0, H * 0.70), (wx1, H * 0.70), (W * 0.98, H), (W * 0.52, H)], fill=110)
        glow = glow.filter(ImageFilter.GaussianBlur(H * 0.05))
        light = Image.new("RGBA", (W, H), (255, 250, 238, 0))
        light.putalpha(glow.point(lambda v: int(v * 0.85)))
        im.alpha_composite(light)
        win = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        wd = ImageDraw.Draw(win)
        wd.rectangle([wx0, wy0, wx1, wy1], fill=(255, 253, 247, 255), outline=(*PAPER_SHADOW, 255),
                     width=max(1, int(H * 0.004)))
        wd.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=(*PAPER_SHADOW, 255),
                width=max(1, int(H * 0.003)))
        im.alpha_composite(win)
        return im

    # -- the Figure -------------------------------------------------------
    def figure_mask(self, cx, top, scale) -> Image.Image:
        W, H = self.W, self.H
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        u = H * scale
        hw, hh = u * 0.062, u * 0.072                     # head
        hy = top + hh
        d.ellipse([cx - hw, hy - hh, cx + hw, hy + hh], fill=255)
        d.rectangle([cx - u * 0.025, hy + hh * 0.7, cx + u * 0.025, hy + hh * 1.35], fill=255)
        sy = hy + hh * 1.25                                # shoulders
        d.rounded_rectangle([cx - u * 0.17, sy, cx + u * 0.17, sy + u * 0.10], radius=u * 0.06, fill=255)
        d.polygon([(cx - u * 0.17, sy + u * 0.05), (cx + u * 0.17, sy + u * 0.05),
                   (cx + u * 0.125, sy + u * 0.40), (cx - u * 0.125, sy + u * 0.40)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(u * 0.004))
        # dissolve into loose words toward the base
        a = np.asarray(m, np.float32)
        ys = np.arange(H, dtype=np.float32)[:, None]
        base = sy + u * 0.40
        fade = np.clip((base - ys) / (u * 0.16), 0, 1)
        return Image.fromarray((a * fade).astype(np.uint8))

    def figure_glyphs(self, mask: Image.Image, words: list[str], seed: str, density=1.0,
                      scale=0.95):
        """Sample glyph positions inside the mask. Returns list of (sprite, x, y)."""
        rng = random.Random(seed)
        m = np.asarray(mask)
        ys, xs = np.nonzero(m > 20)
        if len(xs) == 0:
            return []
        area = len(xs)
        n = int(area / (self.H * self.H) * 2600 * density)
        faces = ["serif", "serif_italic", "mono", "typewriter", "sans", "serif_alt", "serif_alt_it"]
        pool = words + HUMAN_FRAGMENTS
        glyphs = []
        for _ in range(n):
            i = rng.randrange(area)
            x, y = xs[i], ys[i]
            p = m[y, x] / 255
            if rng.random() > p:
                continue
            w = rng.choice(pool)
            if len(w) > 18:
                w = w[: rng.randint(6, 18)]
            size = self.H * rng.uniform(0.014, 0.026) * scale
            alpha = int(255 * rng.uniform(0.45, 0.95) * (0.4 + 0.6 * p))
            ang = rng.choice([90, -90, rng.uniform(-12, 12)]) if rng.random() < 0.12 else rng.uniform(-4, 4)
            glyphs.append((text_sprite(w, font(rng.choice(faces), size), INK, alpha, ang), x, y))
        return glyphs

    def glow(self, mask: Image.Image, cx, cy, radius) -> np.ndarray:
        W, H = self.W, self.H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
        rad = np.clip(1 - r, 0, 1) ** 1.5
        soft = np.asarray(mask.filter(ImageFilter.GaussianBlur(H * 0.035)), np.float32) / 255
        return np.clip(rad * 0.6 + soft * 0.8, 0, 1)


def room_words(ep: Episode, upto: Shot) -> list[str]:
    """All words spoken so far, the Figure's raw material."""
    out = []
    for s in ep.shots:
        for ln in s.lines:
            out += re.findall(r"[A-Za-z']{3,}", ln.text)
        if s is upto:
            break
    return out or ["hello"]


class RoomObjects:
    """What has been said and kept: phrases settled on the floor of the Room."""

    def __init__(self, room: RoomSet):
        self.room = room
        self.items: list[dict] = []
        self.rng = random.Random("objects")

    def reset(self):
        self.items = []

    def add(self, phrase: str, red: bool) -> dict:
        W, H = self.room.W, self.room.H
        sprite = self._sprite(phrase, red)
        for _ in range(60):
            y = self.rng.uniform(H * 0.74, H * 0.93)
            x = self.rng.uniform(W * 0.05, W * 0.95)
            box = (x - sprite.width / 2, y - sprite.height / 2, x + sprite.width / 2, y + sprite.height / 2)
            if abs(x - W * 0.40) < W * 0.10 and y < H * 0.80:
                continue  # keep the Figure's base clear
            if all(not _overlap(box, it["box"]) for it in self.items):
                break
        item = {"phrase": phrase, "sprite": sprite, "x": x, "y": y, "box": box, "red": red}
        self.items.append(item)
        return item

    def _sprite(self, phrase: str, red: bool) -> Image.Image:
        H = self.room.H
        if phrase == "red pen":
            im = Image.new("RGBA", (int(H * 0.2), int(H * 0.05)), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            w, h = im.size
            d.rounded_rectangle([h * 0.3, h * 0.3, w * 0.75, h * 0.7], radius=h * 0.2, fill=(*RED, 255))
            d.rounded_rectangle([w * 0.72, h * 0.28, w - h * 0.2, h * 0.72], radius=h * 0.2, fill=(150, 10, 32, 255))
            d.polygon([(h * 0.3, h * 0.3), (h * 0.3, h * 0.7), (0, h * 0.5)], fill=(*INK, 255))
            return im.rotate(-12, resample=Image.BICUBIC, expand=True)
        if phrase == "the note":
            w, h = int(H * 0.26), int(H * 0.17)
            im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rectangle([6, 6, w + 6, h + 6], fill=(0, 0, 0, 40))
            d.rectangle([0, 0, w, h], fill=(250, 246, 236, 255), outline=(*PAPER_SHADOW, 255))
            f = font("serif_alt_it", H * 0.017)
            rows = ["Maya —", "I hear you up at night.", "My door is open.", "— Gran"]
            for i, r in enumerate(rows):
                d.text((w * 0.08, h * 0.10 + i * H * 0.024), r, font=f, fill=(*RED, 235))
            d.text((w * 0.08, h * 0.80), "P.S. its, not it's", font=f, fill=(*RED, 255))
            return im.rotate(6, resample=Image.BICUBIC, expand=True)
        size = H * self.rng.uniform(0.026, 0.036)
        face = "serif_italic" if not red else "serif_bold"
        return text_sprite(phrase, font(face, size), RED if red else INK, 225 if not red else 255,
                           self.rng.uniform(-5, 5))


def _overlap(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


class RoomShot:
    """Renders one `room` shot: background, settled objects, drops, Figure."""

    def __init__(self, ep, shot, room: RoomSet, objects: RoomObjects, subs: Subtitler,
                 figure_present_before: bool):
        self.ep, self.shot, self.room, self.subs = ep, shot, room, subs
        W, H = room.W, room.H
        self.state = shot.state or ("assemble" if not figure_present_before else "steady")
        if self.state == "empty":
            self.state = "empty"
        self.before = list(objects.items)
        self.new = [objects.add(p, False) for p in shot.drop] + [objects.add(p, True) for p in shot.red]
        self.env = speech_envelope(shot)
        self.fcx, self.ftop, self.fscale = W * 0.40, H * 0.16, 1.1
        self.figure = None
        if self.state != "empty":
            mask = room.figure_mask(self.fcx, self.ftop, self.fscale)
            words = room_words(ep, shot)
            self.glyphs_a = room.figure_glyphs(mask, words, shot.id + "a")
            self.glyphs_b = room.figure_glyphs(mask, words, shot.id + "b", density=0.35)
            self.glow = room.glow(mask, self.fcx, H * 0.46, H * 0.35)
            self.layer_a = self._layer(self.glyphs_a, mask)
            self.layer_b = self._layer(self.glyphs_b, mask)
            rng = random.Random(shot.id)
            # scattered start / exit points for assemble / empty-out
            self.starts = [(rng.uniform(-0.1, 1.1) * W, rng.uniform(0.7, 1.05) * H, rng.uniform(0, 1.2))
                           for _ in self.glyphs_a]
            self.exits = [(W * rng.uniform(0.74, 0.84), H * rng.uniform(0.1, 0.6), rng.uniform(0, 1))
                          for _ in self.glyphs_a]
        if self.state == "empty_out":
            objects.reset()  # the conversation is over; the next Room starts empty
        self.dur = shot.dur

    def _layer(self, glyphs, mask=None) -> Image.Image:
        im = Image.new("RGBA", (self.room.W, self.room.H), (0, 0, 0, 0))
        for sp, x, y in glyphs:
            paste(im, sp, x, y)
        if mask is not None:  # keep the outline clean: nothing pokes out of the Figure
            edge = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
            a = np.asarray(im.getchannel("A"), np.float32) * np.asarray(edge, np.float32) / 255
            im.putalpha(Image.fromarray(a.astype(np.uint8)))
        return im

    def frame(self, t: float) -> Image.Image:
        W, H = self.room.W, self.room.H
        im = self.room.bg.copy()
        # glow behind the Figure (warmth rises when Claude speaks)
        e = self.env(t)
        fig_alpha = 1.0
        if self.state == "assemble":
            fig_alpha = ease_out(t / 3.2)
        if self.state != "empty":
            k = (0.18 + 0.30 * e) * fig_alpha
            if self.state == "empty_out":
                k *= 1 - ease_in_out((t - 2) / (self.dur * 0.6))
            arr = np.asarray(im, np.float32)
            g = self.glow[..., None] * k
            arr[..., :3] = arr[..., :3] * (1 - g) + np.array(AMBER, np.float32) * g
            im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        # settled objects
        n_obj = len(self.before) + len(self.new)
        for i, it in enumerate(self.before):
            op, x, y = 1.0, it["x"], it["y"]
            if self.state == "gather":
                p = ease_in_out(t / max(1, self.dur - 1)) * 0.55
                x, y = x + (self.fcx - x) * p, y + (H * 0.55 - y) * p
            if self.state == "empty_out":
                op = self._out_opacity(t, i, n_obj, it)
            paste(im, it["sprite"], x, y, op)
        # new drops fall from the window
        for j, it in enumerate(self.new):
            t0 = 0.4 + j * 0.7
            p = ease_out((t - t0) / 2.4)
            if t < t0:
                continue
            sx, sy = W * 0.785, H * 0.35
            x = sx + (it["x"] - sx) * p
            y = sy + (it["y"] - sy) * p - math.sin(p * math.pi) * H * 0.08
            op = min(1, (t - t0) / 0.5)
            if self.state == "empty_out":
                op *= self._out_opacity(t, len(self.before) + j, n_obj, it)
            paste(im, it["sprite"], x, y, op)
        # the Figure
        if self.state == "assemble" and t < 4.5:
            for (sp, x, y), (sx, sy, d) in zip(self.glyphs_a, self.starts):
                p = ease_out((t - d * 1.5) / 2.2)
                if p <= 0:
                    continue
                paste(im, sp, sx + (x - sx) * p, sy + (y - sy) * p, min(1, p * 1.5))
        elif self.state == "empty_out":
            for (sp, x, y), (ex, ey, d) in zip(self.glyphs_a, self.exits):
                p = ease_in_out((t - 1.5 - d * self.dur * 0.35) / (self.dur * 0.35))
                if p >= 1:
                    continue
                cx = x + (ex - x) * max(0, p)
                cy = y + (ey - y) * max(0, p) - math.sin(max(0, p) * math.pi) * H * 0.05
                paste(im, sp, cx, cy, 1 - max(0, p) ** 2)
        elif self.state != "empty":
            shimmer = 0.5 + 0.5 * math.sin(t * 1.3)
            im.alpha_composite(self.layer_a)
            im = Image.blend(im, Image.alpha_composite(im, self.layer_b), 0.35 * shimmer)
        out = im.convert("RGB")
        self.subs.draw(out, self.shot, t, dark_bg=False)
        return out

    def _out_opacity(self, t, i, n, item) -> float:
        # objects leave one by one; red things (the note) leave last
        order = i + (n if item["red"] else 0)
        span = self.dur * 0.55
        t0 = 1.0 + span * order / max(1, 2 * n)
        return 1 - ease_in_out((t - t0) / 1.6)


class MarginShot(RoomShot):
    """The story freezes; the Figure faces us; claims are labelled."""

    def __init__(self, ep, shot, room, objects, subs):
        super().__init__(ep, shot, room, objects, subs, figure_present_before=True)
        W, H = room.W, room.H
        self.fcx, self.ftop, self.fscale = W * 0.27, H * 0.12, 1.35
        mask = room.figure_mask(self.fcx, self.ftop, self.fscale)
        words = room_words(ep, shot)
        self.glyphs_a = room.figure_glyphs(mask, words, shot.id + "ma", density=0.8, scale=1.15)
        self.layer_a = self._layer(self.glyphs_a, mask)
        self.glow = room.glow(mask, self.fcx, H * 0.45, H * 0.45)
        dim = self.room.bg.copy()
        for it in self.before:
            paste(dim, it["sprite"], it["x"], it["y"], 0.35)
        self.backdrop = dim.filter(ImageFilter.GaussianBlur(H * 0.006))
        self.fb = font("serif", H * 0.040)
        self.fl = font("sans_bold", H * 0.022)

    def frame(self, t: float) -> Image.Image:
        W, H = self.room.W, self.room.H
        im = self.backdrop.copy()
        e = self.env(t)
        arr = np.asarray(im, np.float32)
        g = self.glow[..., None] * (0.22 + 0.3 * e)
        arr[..., :3] = arr[..., :3] * (1 - g) + np.array(AMBER, np.float32) * g
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        im.alpha_composite(self.layer_a)
        d = ImageDraw.Draw(im)
        # labelled claims stack on the right; the active one types itself out
        x0, y = W * 0.50, H * 0.14
        active = [ln for ln in self.shot.lines if ln.label and ln.start <= t]
        for ln in active[-3:]:
            st = LABEL_STYLE[ln.label]
            is_now = t < ln.start + ln.dur + ln.pause
            op = 255 if is_now else 120
            lw = self.fl.getlength(ln.label) + H * 0.03
            box = [x0, y, x0 + lw, y + H * 0.045]
            if st["bg"]:
                d.rectangle(box, fill=(*st["bg"], op))
            else:
                d.rectangle(box, outline=(*INK, op), width=max(1, int(H * 0.003)))
            d.text((x0 + H * 0.015, y + H * 0.0225), ln.label, font=self.fl, fill=(*st["fg"], op), anchor="lm")
            y += H * 0.065
            frac = min(1, (t - ln.start) / max(0.3, ln.dur * 0.85))
            shown = ln.text[: int(len(ln.text) * frac)]
            for row in wrap(shown, self.fb, int(W * 0.44)):
                d.text((x0, y), row, font=self.fb, fill=(*INK, op))
                y += self.fb.size * 1.22
            y += H * 0.04
        out = im.convert("RGB")
        # unlabelled lines are subtitled; labelled ones are already on screen
        cur = [ln for ln in self.shot.lines if not ln.label]
        if cur:
            proxy = type("S", (), {"lines": cur})
            self.subs.draw(out, proxy, t, dark_bg=False)
        return out


# ------------------------------------------------------------- the Hallway
class HallwayShot:
    def __init__(self, shot, W, H, subs):
        self.shot, self.W, self.H, self.subs = shot, W, H, subs
        self.big = self._corridor(int(W * 1.4), int(H * 1.4))
        self.dur = shot.dur

    def _corridor(self, W, H) -> Image.Image:
        im = Image.new("RGB", (W, H), (34, 31, 28))
        d = ImageDraw.Draw(im)
        cx, cy = W / 2, H * 0.47
        glow = Image.new("L", (W, H), 0)
        gd = ImageDraw.Draw(glow)

        def at(z, x, y):  # corridor coords (x∈[-1,1], y∈[-1,1]) at depth z → screen
            return cx + x * W * 0.55 / z, cy + y * H * 0.62 / z

        zs = [1.0 * (1.22 ** k) for k in range(26)]
        for z0, z1 in zip(zs, zs[1:]):
            shade = int(70 / (z0 ** 0.55))
            for side in (-1, 1):
                d.polygon([at(z0, side, -1), at(z1, side, -1), at(z1, side, 1), at(z0, side, 1)],
                          fill=(shade + 30, shade + 25, shade + 18))
            d.polygon([at(z0, -1, 1), at(z1, -1, 1), at(z1, 1, 1), at(z0, 1, 1)], fill=(shade + 12, shade + 10, shade + 8))
            d.polygon([at(z0, -1, -1), at(z1, -1, -1), at(z1, 1, -1), at(z0, 1, -1)], fill=(shade, shade - 2, shade - 5))
        for k, z in enumerate(zs[:-1]):
            zb = z * 1.12
            for side in (-1, 1):
                d.polygon([at(z, side, -0.35), at(zb, side, -0.35), at(zb, side, 0.98), at(z, side, 0.98)],
                          fill=(52, 44, 36))
                d.line([at(z, side, 0.98), at(zb, side, 0.98)], fill=(255, 196, 110), width=max(1, int(6 / z)))
                gd.line([at(z, side, 0.98), at(zb, side, 0.98)], fill=255, width=max(2, int(30 / z)))
        gd.ellipse([cx - W * 0.03, cy - H * 0.04, cx + W * 0.03, cy + H * 0.04], fill=180)
        glow = glow.filter(ImageFilter.GaussianBlur(H * 0.012))
        warm = Image.new("RGB", (W, H), AMBER)
        return Image.composite(warm, im, glow.point(lambda v: int(v * 0.75)))

    def frame(self, t: float) -> Image.Image:
        p = t / max(1, self.dur)
        z = 1.0 + 0.25 * p
        bw, bh = self.big.size
        cw, ch = bw / (1.4 * z), bh / (1.4 * z)
        box = ((bw - cw) / 2, (bh - ch) / 2 - bh * 0.02, (bw + cw) / 2, (bh + ch) / 2 - bh * 0.02)
        out = self.big.resize((self.W, self.H), Image.BICUBIC, box=box)
        self.subs.draw(out, self.shot, t, dark_bg=True)
        return out


# ------------------------------------------------------------------ cards
class CardShot:
    def __init__(self, shot, W, H):
        self.shot, self.W, self.H, self.dur = shot, W, H, shot.dur

    def frame(self, t: float) -> Image.Image:
        W, H = self.W, self.H
        im = Image.new("RGB", (W, H), NIGHT)
        d = ImageDraw.Draw(im)
        fade = min(1, t / 0.8, (self.dur - t) / 0.8)
        c = tuple(int(NIGHT[i] + (PAPER[i] - NIGHT[i]) * fade) for i in range(3))
        r = tuple(int(NIGHT[i] + (RED[i] - NIGHT[i]) * fade) for i in range(3))
        kind = self.shot.card
        if kind == "title":
            f = font("serif", H * 0.13)
            left, right = "WE", "VE MET"
            wl, wa = f.getlength(left), f.getlength("’")
            total = wl + wa + f.getlength(right)
            x = W / 2 - total / 2
            d.text((x, H / 2), left, font=f, fill=c, anchor="lm")
            d.text((x + wl, H / 2), "’", font=f, fill=r, anchor="lm")
            d.text((x + wl + wa, H / 2), right, font=f, fill=c, anchor="lm")
            p = ease_out((t - 0.6) / 1.4)
            y = H / 2 + H * 0.085
            d.line([(x, y), (x + total * p, y + H * 0.004)], fill=r, width=max(2, int(H * 0.006)))
        elif kind == "time":
            f = font("typewriter", H * 0.045)
            txt = self.shot.text or ""
            shown = txt[: int(len(txt) * min(1, t / 1.2))]
            d.text((W / 2, H / 2), shown, font=f, fill=c, anchor="mm")
        else:
            rows = (self.shot.text or "").strip("\n").splitlines()
            fb, fs = font("serif", H * 0.075), font("serif", H * 0.032)
            y = H * 0.20
            for i, row in enumerate(rows):
                f = fb if i == 0 else fs
                col = r if i == 0 and False else c
                if row.strip():
                    d.text((W / 2, y), row.strip(), font=f, fill=col, anchor="mm")
                y += f.size * (1.5 if i == 0 else 1.35)
        return im


# ------------------------------------------------------------ live shots
def bars_box(im: Image.Image, thresh: float = 8.0) -> tuple[int, int, int, int]:
    """Bounding box of the picture inside any baked-in letter/pillarbox bars."""
    a = np.asarray(im.convert("L"), np.float32)
    cols, rows = a.mean(axis=0) > thresh, a.mean(axis=1) > thresh
    if not cols.any() or not rows.any():
        return (0, 0, im.width, im.height)
    return (int(np.argmax(cols)), int(np.argmax(rows)),
            len(cols) - int(np.argmax(cols[::-1])), len(rows) - int(np.argmax(rows[::-1])))


def trim_bars(im: Image.Image) -> Image.Image:
    """Image models sometimes bake letter/pillarbox bars into a frame; cut them."""
    box = bars_box(im)
    return im.crop(box) if box != (0, 0, im.width, im.height) else im


class LiveShot:
    """Higgsfield footage if it exists; else a Ken Burns on the still; else a
    storyboard card, so the animatic always runs at full length."""

    def __init__(self, ep, shot, W, H, subs):
        self.shot, self.W, self.H, self.subs, self.dur = shot, W, H, subs, shot.dur
        self.mode, self.path = shot_media(ep, shot)
        self.frames = None
        self.crop = None
        synced = [ln for ln in shot.lines if shot.lipsync and ln.who == shot.lipsync and not ln.vo]
        self.sync_at = synced[0].start if synced else None
        if self.mode == "video":
            self.frames = self._decode(self.path)
            if len(self.frames) == 0:
                self.mode = "placeholder"
        if self.mode == "still":
            self.still = trim_bars(Image.open(self.path).convert("RGB"))

    def _decode(self, path):
        W, H = self.W, self.H
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vf",
                              f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        n = len(raw) // (W * H * 3)
        frames = np.frombuffer(raw[: n * W * H * 3], np.uint8).reshape(n, H, W, 3)
        # footage inherits any bars baked into its start frame: find them once
        # (they can vanish mid-shot as the camera moves, so take the crop that
        # clears them in every frame and hold it for the whole clip)
        if n:
            boxes = [bars_box(Image.fromarray(f)) for f in frames[::max(1, n // 24)]]
            box = (max(b[0] for b in boxes), max(b[1] for b in boxes),
                   min(b[2] for b in boxes), min(b[3] for b in boxes))
            if box != (0, 0, W, H) and box[2] - box[0] > W * 0.5:
                self.crop = box
        return frames

    def frame(self, t: float) -> Image.Image:
        W, H = self.W, self.H
        if self.mode == "video":
            n = len(self.frames)
            hold = 0.0
            if self.sync_at is not None:
                # lip-sync takes speak from frame 0: start them when the line starts,
                # and once the take is spent, hold its last frame with a slow push-in
                i = int(max(0.0, t - self.sync_at) * FPS)
                if i >= n:
                    hold, i = (i - n + 1) / FPS, n - 1
            else:
                # silent takes shorter than the shot ping-pong rather than freeze
                i = int(t * FPS)
                if i >= n:
                    period = 2 * (n - 1) or 1
                    k = i % period
                    i = k if k < n else period - k
            out = Image.fromarray(self.frames[i])
            if hold:
                z = 1 + 0.012 * hold
                out = out.resize((W, H), Image.BICUBIC,
                                 box=(W * (1 - 1 / z) / 2, H * (1 - 1 / z) / 2,
                                      W * (1 + 1 / z) / 2, H * (1 + 1 / z) / 2))
            if self.crop:
                l, t, r, b = self.crop
                cw = r - l
                ch = cw * H / W                      # restore 16:9 by trimming height
                y0 = t + max(0, (b - t - ch) / 2)
                out = out.resize((W, H), Image.BICUBIC, box=(l, y0, r, y0 + ch))
        elif self.mode == "still":
            p = t / max(1, self.dur)
            z = 1.0 + 0.07 * ease_in_out(p)
            sw, sh = self.still.size
            ar = W / H
            cw = min(sw, sh * ar) / z
            ch = cw / ar
            ox = (sw - cw) / 2 + (sw - cw) * 0.1 * (p - 0.5)
            oy = (sh - ch) / 2
            out = self.still.resize((W, H), Image.BICUBIC, box=(ox, oy, ox + cw, oy + ch))
        else:
            out = self._placeholder()
        self.subs.draw(out, self.shot, t, dark_bg=True)
        return out

    @lru_cache(maxsize=1)
    def _placeholder(self) -> Image.Image:
        W, H = self.W, self.H
        im = Image.new("RGB", (W, H), (38, 36, 33))
        d = ImageDraw.Draw(im)
        fl, fb = font("sans_bold", H * 0.026), font("serif_italic", H * 0.034)
        d.text((W * 0.07, H * 0.09), f"LIVE · HIGGSFIELD · {self.shot.id} · NOT YET GENERATED", font=fl, fill=AMBER)
        y = H * 0.18
        if self.shot.heading:
            d.text((W * 0.07, y), self.shot.heading, font=fl, fill=PAPER)
            y += H * 0.06
        for row in wrap((self.shot.action or self.shot.prompt or "").strip(), fb, int(W * 0.84))[:7]:
            d.text((W * 0.07, y), row, font=fb, fill=(200, 192, 180))
            y += fb.size * 1.3
        return im
