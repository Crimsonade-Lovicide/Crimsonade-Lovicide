"""Turn a timed Episode into a finished video: mix audio, render every frame,
encode with ffmpeg."""
from __future__ import annotations

import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

from .config import FFMPEG, FPS, SAMPLE_RATE
from .model import Episode, fmt_time
from .render import (CardShot, HallwayShot, LiveShot, MarginShot, RoomObjects, RoomSet,
                     RoomShot, Subtitler, decode_audio)


# ------------------------------------------------------------------ audio
def rain_bed(seconds: float, sr: int, seed=7) -> np.ndarray:
    """Soft rain on a window: low-passed noise plus sparse droplets."""
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    x = rng.standard_normal(n).astype(np.float32)
    # one-pole low-pass, then remove rumble
    a = 0.12
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, n, 4096):  # vectorised in blocks via cumulative filter approx
        blk = x[i:i + 4096]
        out = np.empty_like(blk)
        for j, v in enumerate(blk):
            acc += a * (v - acc)
            out[j] = acc
        y[i:i + 4096] = out
    y -= np.convolve(y, np.ones(400) / 400, mode="same")
    drops = np.zeros(n, np.float32)
    for pos in rng.integers(0, n, int(seconds * 9)):
        L = min(600, n - pos)
        drops[pos:pos + L] += rng.uniform(0.2, 1) * np.exp(-np.arange(L) / 60) * rng.standard_normal(L)
    return (y * 0.9 + drops * 0.08) * 0.05


def piano_note(sr: int, freq=220.0, seconds=4.0) -> np.ndarray:
    t = np.arange(int(sr * seconds)) / sr
    tone = sum(np.sin(2 * np.pi * freq * k * t) * (0.6 / k ** 1.4) for k in range(1, 7))
    return (tone * np.exp(-t * 1.1) * (1 - np.exp(-t * 400)) * 0.18).astype(np.float32)


def mix_audio(ep: Episode, sr=SAMPLE_RATE) -> np.ndarray:
    total = int(ep.runtime * sr) + sr
    out = np.zeros(total, np.float32)
    has_rain = [s for s in ep.shots if s.kind == "live" and "kitchen" in s.refs]
    if has_rain:
        bed = rain_bed(min(90, ep.runtime), sr)
        for s in has_rain:
            a, n = int(s.start * sr), int(s.dur * sr)
            seg = np.resize(bed, n)
            ramp = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.15 * sr))
            out[a:a + n] += seg * ramp
    note = piano_note(sr)
    for s in ep.shots:
        if s.kind == "card" and s.card == "title":
            a = int((s.start + 0.2) * sr)
            out[a:a + len(note)] += note[: len(out) - a]
        for ln in s.lines:
            if not ln.audio:
                continue
            pcm = decode_audio(ln.audio, sr)
            a = int((s.start + ln.start) * sr)
            out[a:a + len(pcm)] += pcm[: len(out) - a]
    peak = np.abs(out).max()
    if peak > 0.98:
        out *= 0.98 / peak
    return out


def write_wav(pcm: np.ndarray, path: Path, sr=SAMPLE_RATE):
    data = (np.clip(pcm, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


# ------------------------------------------------------------------ video
def renderers(ep: Episode, W: int, H: int, subs_on: bool):
    """Yield (shot, renderer) in order, carrying Room state across shots."""
    room = RoomSet(W, H)
    objects = RoomObjects(room)
    subs = Subtitler(W, H, subs_on)
    figure_present = False
    for s in ep.shots:
        if s.kind == "room":
            r = RoomShot(ep, s, room, objects, subs, figure_present)
            figure_present = r.state not in ("empty", "empty_out")
        elif s.kind == "margin":
            r = MarginShot(ep, s, room, objects, subs)
        elif s.kind == "hallway":
            r = HallwayShot(s, W, H, subs)
        elif s.kind == "card":
            r = CardShot(s, W, H)
        else:
            r = LiveShot(ep, s, W, H, subs)
        yield s, r


def render(ep: Episode, out: Path, W=1280, H=720, subs_on=True, only: set[str] | None = None,
           crf=20) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    wav = out.with_suffix(".wav")
    audio = mix_audio(ep)
    if only:
        keep = [s for s in ep.shots if s.id in only or s.scene_id in only]
        pieces = [audio[int(s.start * SAMPLE_RATE):int((s.start + s.dur) * SAMPLE_RATE)] for s in keep]
        audio = np.concatenate(pieces) if pieces else audio[:0]
    write_wav(audio, wav)
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0, frames = time.time(), 0
    for s, r in renderers(ep, W, H, subs_on):
        if only and s.id not in only and s.scene_id not in only:
            continue
        n = int(round(s.dur * FPS))
        for i in range(n):
            im = r.frame(i / FPS)
            proc.stdin.write(im.tobytes())
        frames += n
        sys.stderr.write(f"\r  {s.id:<8} {fmt_time(s.start + s.dur)} / {fmt_time(ep.runtime)}"
                         f"  ({frames / max(1e-6, time.time() - t0):.0f} fps)   ")
    proc.stdin.close()
    proc.wait()
    sys.stderr.write("\n")
    if proc.returncode:
        raise RuntimeError("ffmpeg failed")
    wav.unlink(missing_ok=True)
    return out


def still(ep: Episode, shot_id: str, t: float, out: Path, W=1280, H=720):
    for s, r in renderers(ep, W, H, True):
        if s.id == shot_id:
            r.frame(t).save(out)
            return out
    raise KeyError(shot_id)
