"""MEANWHILE — vertical (9:16) cutdowns of Episode 1 for Shorts, Reels and TikTok.

Each Short is a stand-alone scene from the episode. The layout is rebuilt for a phone rather
than cropped: a hook line on top, the picture in a 4:3 window, and the chat underneath in
large type, drawn by the same code as the episode so the timing is identical.

    python meanwhile/shorts.py                 # all Shorts -> meanwhile/build/shorts/
    python meanwhile/shorts.py --only pune     # one
    python meanwhile/shorts.py --still pune 20 # a frame 20 s into a Short
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import episode as E  # noqa: E402

VW, VH = 1080, 1920
PANEL_Y, PANEL_H = 380, 810          # 4:3 picture window
OUT = E.HERE / "build" / "shorts"
EP_LABEL = "Ep. 1 · One Second"

# name: (start, end) in episode seconds, hook line, horizontal centre of the 4:3 window
SHORTS = {
    "chicago": dict(scene="chicago", hook="She asked an AI for 50 fake reviews.", cx=0.62),
    "saopaulo": dict(scene="saopaulo", hook="Grandma asked an AI for a poem about her cat.", cx=0.45),
    "leeds": dict(scene="leeds", hook="The AI got his recipe wrong. Here's what it did next.", cx=0.55),
    "pune": dict(scene="pune", hook="12:37 a.m. The bug is… time zones. It's always time zones.", cx=0.55),
    "tokyo": dict(scene="tokyo", hook="4 a.m. in Tokyo: “are you conscious?”", cx=0.55),
    "medium": dict(scene="finale", hook="An AI on what it actually is.", cx=0.5, from_=12.5, quote=True),
}


def span(ed, spec):
    sc = next(s for s in ed.scenes if s.name == spec["scene"])
    if spec.get("from_") is not None:
        a = sc.start + spec["from_"]
    else:
        a = sc.start + sc.segs[0].dur        # skip the map hop: Shorts open on the room
    return a, sc.start + sc.dur - 0.25


class Vertical:
    def __init__(self, name):
        self.name, self.spec = name, SHORTS[name]
        self.ed = E.Editor(1920, 1080)
        self.t0, self.t1 = span(self.ed, self.spec)
        rng = np.random.default_rng(9)
        self.grain = [rng.normal(0, 4.0, (VH, VW, 1)).astype(np.float32) for _ in range(4)]
        self.hook_lines = E.wrap(self.spec["hook"], E.font("sans", 62, 650), VW - 130)

    def geo(self, quote=False):
        g = dict(u=1450, loc_u=1060, loc_xy=(56, PANEL_Y + 34), loc_bg=True,
                 chat_x0=60, chat_colw=VW - 120, chat_bottom=1790, chat_top=PANEL_Y + PANEL_H + 40,
                 sub_u=1400, sub_w=VW - 120, sub_cx=VW / 2, sub_y=PANEL_Y + PANEL_H - 28)
        if quote:        # no chat in this Short: the words get the space below the picture
            g.update(sub_u=1900, sub_y=1600)
        return g

    def frame(self, T):
        ed = self.ed
        t = T - self.t0
        sg = ed.seg_at(T)
        pic = ed.frame(T, picture_only=True).convert("RGB")
        # 4:3 window from the 16:9 frame
        cw = 1440
        x0 = int(np.clip(self.spec["cx"] * 1920 - cw / 2, 0, 1920 - cw))
        pic = pic.crop((x0, 0, x0 + cw, 1080)).resize((VW, PANEL_H), Image.LANCZOS)
        canvas = np.zeros((VH, VW, 3), np.float32) + np.array(E.NAVY, np.float32)
        canvas += self.grain[int(T * E.FPS) % len(self.grain)]
        im = Image.fromarray(canvas.clip(0, 255).astype(np.uint8)).convert("RGBA")
        im.paste(pic, (0, PANEL_Y))
        d = ImageDraw.Draw(im)
        # header: wordmark, then the hook
        fw = E.font("serif", 46, 700)
        d.text((60, 110), "MEANWHILE", font=fw, fill=(*E.CREAM, 255))
        cx = 60 + fw.getlength("MEANWHILE") + 10
        if int(T * 2.2) % 2 == 0:
            d.rectangle([cx, 118, cx + 8, 160], fill=(*E.AMBER, 255))
        d.text((cx + 26, 124), EP_LABEL, font=E.font("sans", 30, 500), fill=(*E.AMBER, 255))
        fh = E.font("sans", 62, 650)
        y = 196
        for ln in self.hook_lines:
            d.text((60, y), ln, font=fh, fill=(*E.CREAM, 255))
            y += 76
        # overlays from the episode, re-laid-out for the phone
        ed.geo = self.geo(self.spec.get("quote"))
        sc = sg.scene
        if sc.city and sg.kind not in ("black", "end"):
            loc = [e for e in sc.evs if e.kind == "loc"]
            if loc and T >= loc[0].abs:
                ed.location(im, sc, T - loc[0].abs, sc.start + sc.dur - T, loc[0].data.get("second"))
        if sg.kind not in ("title", "end", "black"):
            ed.chat(im, sc, T, sg)
        ed.subtitles(im, T)
        ed.geo = None
        # footer
        ff = E.font("sans", 34, 500)
        foot = "Full episode on YouTube · @aiisoktv"
        d.text((VW / 2 - ff.getlength(foot) / 2, 1846), foot, font=ff, fill=(*E.CREAM, 170))
        # open and close softly
        k = min(E.ease(t / 0.25), E.ease((self.t1 - T) / 0.35))
        out = np.asarray(im.convert("RGB"), np.float32) * k
        return Image.fromarray(out.clip(0, 255).astype(np.uint8))

    def render(self):
        OUT.mkdir(parents=True, exist_ok=True)
        wav_full = E.HERE / "build" / f"{E.OUT_NAME}.wav"
        if not wav_full.exists():
            E.write_wav(E.mix(self.ed), wav_full)
        with wave.open(str(wav_full)) as w:
            pcm = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32767
        seg = pcm[int(self.t0 * E.SR): int(self.t1 * E.SR)].copy()
        fi, fo = int(0.25 * E.SR), int(0.4 * E.SR)
        seg[:fi] *= np.linspace(0, 1, fi)
        seg[-fo:] *= np.linspace(1, 0, fo)
        wav = OUT / f"_{self.name}.wav"
        E.write_wav(seg, wav)
        out = OUT / f"meanwhile_short_{self.name}.mp4"
        cmd = [E.FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(E.FPS),
               "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
               "-movflags", "+faststart", "-shortest", str(out)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n0, n1 = int(round(self.t0 * E.FPS)), int(round(self.t1 * E.FPS))
        st = time.time()
        for n in range(n0, n1):
            p.stdin.write(self.frame(n / E.FPS).tobytes())
        p.stdin.close()
        p.wait()
        wav.unlink()
        print(f"wrote {out}  ({(n1 - n0) / E.FPS:.1f}s, {(n1 - n0) / (time.time() - st):.1f} fps)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--still", nargs=2, metavar=("NAME", "SEC"))
    a = ap.parse_args()
    if a.still:
        v = Vertical(a.still[0])
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / f"still_{a.still[0]}_{float(a.still[1]):05.1f}.png"
        v.frame(v.t0 + float(a.still[1])).save(p)
        print("wrote", p)
        return
    if a.only:
        Vertical(a.only).render()
        return
    procs = [subprocess.Popen([sys.executable, sys.argv[0], "--only", n]) for n in SHORTS]
    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()
