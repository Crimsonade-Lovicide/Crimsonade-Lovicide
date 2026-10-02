"""Render every toolkit function small and short, then check the files with ffprobe (or ffmpeg when there is
no ffprobe): they exist, last the right number of frames (+-1), and have the right size and frame rate.
Plus a smoothness check on kenburns.

    python3 -m pytest unbuilt/toolkit/tests -q        (or: python3 unbuilt/toolkit/tests/test_kit.py)
"""
import json
import os
import re
import subprocess
import sys
import wave

import cv2
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unbuilt_kit as kit  # noqa: E402
from unbuilt_kit.core import ease, ffmpeg_exe  # noqa: E402

S = (320, 180)          # tiny landscape
V = (180, 320)          # tiny Shorts
FPS = 24


@pytest.fixture(scope="module")
def tmp(tmp_path_factory):
    return tmp_path_factory.mktemp("kit")


@pytest.fixture(scope="module")
def drawing(tmp):
    """A fake 'engraving': ink lines on paper, portrait, so it gets fitted on paper rather than cropped."""
    im = np.full((600, 400, 3), (232, 224, 205), np.uint8)
    cv2.polylines(im, [np.array([[200, 60], [120, 540], [280, 540]], np.int32)], True, (30, 30, 30), 4)
    for y in range(120, 540, 30):
        cv2.line(im, (200 - (y - 60) // 6, y), (200 + (y - 60) // 6, y), (40, 40, 40), 2)
    p = str(tmp / "drawing.png")
    Image.fromarray(im).save(p)
    return p


@pytest.fixture(scope="module")
def texture(tmp):
    """A 16:9 random texture for the smoothness test (fills the frame, no paper border)."""
    rng = np.random.default_rng(0)
    im = cv2.GaussianBlur(rng.random((900, 1600)).astype(np.float32), (0, 0), 3)
    im = (255 * (im - im.min()) / (im.max() - im.min())).astype(np.uint8)
    p = str(tmp / "texture.png")
    Image.fromarray(np.dstack([im] * 3)).save(p)
    return p


def check(path, duration, size=S):
    assert os.path.exists(path), path
    info = kit.probe(path)
    assert (info["width"], info["height"]) == tuple(size), info
    assert abs(info["fps"] - FPS) < 0.01, info
    assert abs(info["frames"] - round(duration * FPS)) <= 1, info
    assert abs(info["duration"] - duration) <= 1 / FPS + 1e-6, info
    return info


def test_ffmpeg_found():
    assert os.path.exists(ffmpeg_exe()) or ffmpeg_exe() == "ffmpeg"


def test_kenburns(tmp, drawing):
    check(kit.kenburns(drawing, str(tmp / "kb.mp4"), 1.5, (0.5, 0.5, 1.0), (0.5, 0.3, 1.6), size=S), 1.5)


def test_kenburns_vertical(tmp, drawing):
    check(kit.kenburns(drawing, str(tmp / "kbv.mp4"), 1.0, size=V), 1.0, V)


def _shift_x(a, b):
    """Horizontal shift from frame a to frame b, by ECC alignment (sub-pixel, ~0.05 px on this texture)."""
    m = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-6)
    _, m = cv2.findTransformECC(a, b, m, cv2.MOTION_TRANSLATION, crit, None, 5)
    return m[0, 2]


def test_kenburns_smooth(tmp, texture):
    """Pan across a texture and measure each frame-to-frame shift of the encoded mp4.
    The shift must never reverse, never jump, and follow the cosine-eased path to within a quarter pixel
    (whole-pixel stepping would be off by up to 0.5 px and fail)."""
    out = kit.kenburns(texture, str(tmp / "pan.mp4"), 3.0, (0.35, 0.5, 1.5), (0.65, 0.5, 1.5), size=S)
    w, h = S
    raw = subprocess.run([ffmpeg_exe(), "-nostdin", "-loglevel", "error", "-i", out, "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)[:, 20:-20, 30:-30]
    dx = np.array([_shift_x(a, b) for a, b in zip(frames, frames[1:])])
    n = len(frames)
    total = 0.30 * w * 1.5          # pan distance in output pixels: 30% of an image shown at 1.5x frame width
    ideal = -total * np.diff([ease(i / (n - 1)) for i in range(n)])
    moving = np.abs(ideal) > 0.3
    assert np.all(np.sign(dx[moving]) == np.sign(ideal[moving])), "motion reverses"
    assert np.max(np.abs(np.diff(dx))) < 0.4, f"jump in motion: {np.max(np.abs(np.diff(dx))):.2f} px"
    assert np.max(np.abs(dx - ideal)) < 0.25, f"off the eased path by {np.max(np.abs(dx - ideal)):.2f} px"


def test_annotate(tmp, drawing):
    marks = [{"type": "arrow", "from": (0.9, 0.2), "to": (0.55, 0.3)},
             {"type": "circle", "center": (0.5, 0.5), "r": 0.2},
             {"type": "ellipse", "center": (0.5, 0.8), "radii": (0.3, 0.06), "at": 0.2},
             {"type": "underline", "from": (0.2, 0.92), "to": (0.8, 0.92), "at": 0.4},
             {"type": "label", "text": "Label", "pos": (0.1, 0.1), "at": 0.6}]
    check(kit.annotate(drawing, str(tmp / "an.mp4"), 2.0, marks, size=S), 2.0)


def test_highlight(tmp, drawing):
    check(kit.highlight(drawing, str(tmp / "hl.mp4"), 1.5, box=(0.3, 0.4, 0.7, 0.5), size=S), 1.5)


def test_scale_compare(tmp, tmp_path):
    sil = str(tmp_path / "sil.png")
    Image.fromarray(np.where(np.arange(100)[:, None] > 20, 0, 255).astype(np.uint8).repeat(40, 1)).save(sil)
    items = [{"name": "Tall", "height_m": 300, "accent": True, "shape": "taper"},
             {"name": "Short with a long name", "height_m": 90},
             {"name": "Arch", "height_m": 133, "shape": "arch"},
             {"name": "From PNG", "height_m": 200, "silhouette": sil}]
    check(kit.scale_compare(str(tmp / "sc.mp4"), 2.0, items, unit="m", size=S), 2.0)
    check(kit.scale_compare(str(tmp / "scv.mp4"), 1.0, items, size=V), 1.0, V)


def test_timeline(tmp):
    ev = [(1889, "Eiffel Tower"), (1890, "Competition"), (1907, "Demolished"), (2007, "New Wembley")]
    check(kit.timeline(str(tmp / "tl.mp4"), 2.0, ev, size=S, title="Title"), 2.0)


def test_title_and_end_cards(tmp):
    check(kit.title_card(str(tmp / "tc.mp4"), 1.5, "A Title", "A subtitle", size=S), 1.5)
    check(kit.title_card(str(tmp / "tcv.mp4"), 1.0, "A Title", size=V), 1.0, V)
    check(kit.end_card(str(tmp / "ec.mp4"), 1.0, size=S), 1.0)


def test_quote_card(tmp):
    check(kit.quote_card(str(tmp / "qc.mp4"), 2.0, "A short test quotation over two lines of type.", "Test",
                         size=S), 2.0)


def test_lower_third_and_overlay(tmp, drawing):
    mov = kit.lower_third(str(tmp / "lt.mov"), 1.5, "Name", "Role", size=S)
    check(mov, 1.5)
    err = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", mov], capture_output=True, text=True).stderr
    assert "qtrle" in err and "argb" in err, "lower third must carry alpha"
    seq = kit.lower_third(str(tmp / "lt_png") + "/", 1.0, "Name", size=S)
    pngs = sorted(os.listdir(seq))
    assert len(pngs) == 24 and Image.open(os.path.join(seq, pngs[12])).mode == "RGBA"
    base = kit.kenburns(drawing, str(tmp / "base.mp4"), 2.0, size=S)
    check(kit.overlay(base, mov, str(tmp / "ov.mp4"), start=0.25), 2.0)
    check(kit.overlay(base, seq, str(tmp / "ov2.mp4")), 2.0)


def test_thumbnail(tmp, drawing):
    for v in (1, 2, 3):
        p = kit.thumbnail(str(tmp / f"th{v}.png"), drawing, overlay_image=drawing, text="Three Words Max", variant=v)
        assert Image.open(p).size == (1280, 720)
    rgba = kit.cutout(drawing)
    assert rgba[..., 3].max() > 0.9 and rgba[0, 0, 3] < 0.05, "paper corner should be cut away"


def _tone(path, seconds, freq, gate=False):
    sr = 48000
    t = np.arange(int(sr * seconds)) / sr
    x = 0.3 * np.sin(2 * np.pi * freq * t) * (((t % 1.0) < 0.6) if gate else 1)
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
    w.close()
    return path


def test_assemble(tmp, drawing):
    a = kit.title_card(str(tmp / "a.mp4"), 1.5, "A", size=S)
    b = kit.kenburns(drawing, str(tmp / "b.mp4"), 1.5, size=S)
    voice = _tone(str(tmp / "voice.wav"), 3.5, 220, gate=True)
    music = _tone(str(tmp / "music.wav"), 2.0, 330)
    # end to end with a 0.5 s dissolve: 1.5 + 1.5 - 0.5 = 2.5 s of picture; the voice is longer, so 3.5 s
    out = kit.assemble([{"clip": a}, {"clip": b}], voice, music, str(tmp / "asm.mp4"), crossfade=0.5, size=S)
    check(out, 3.5)
    err = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", out], capture_output=True, text=True).stderr
    assert re.search(r"Audio: aac.*48000 Hz", err), err
    assert abs(kit.loudness(out) + 14) <= 1.0
    # placed by start time from a JSON shot list, straight cuts, no music
    js = tmp / "shots.json"
    js.write_text(json.dumps({"shots": [{"clip": "a.mp4", "start": 0}, {"clip": "b.mp4", "start": 1.0}]}))
    check(kit.assemble(str(js), voice, None, str(tmp / "asm2.mp4"), crossfade=0, size=S), 3.5)


def test_captions_burn(tmp):
    srt = tmp / "t.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:00,900\nHello there\n\n2\n00:00:01,000 --> 00:00:01,900\nSecond line\n")
    base = kit.title_card(str(tmp / "cb.mp4"), 2.0, "Caption", size=S)
    out = kit.captions_burn(base, str(srt), str(tmp / "cb_out.mp4"))
    check(out, 2.0)
    # the burn must change the picture where the caption sits
    def grab(p):
        return np.frombuffer(subprocess.run([ffmpeg_exe(), "-loglevel", "error", "-ss", "0.5", "-i", p, "-frames:v",
                                             "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                                            capture_output=True).stdout, np.uint8).reshape(S[1], S[0])
    assert np.abs(grab(base).astype(int) - grab(out))[int(S[1] * 0.75):].mean() > 1
    basev = kit.title_card(str(tmp / "cbv.mp4"), 2.0, "Caption", size=V)
    check(kit.captions_burn(basev, str(srt), str(tmp / "cbv_out.mp4"), vertical=True), 2.0, V)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
