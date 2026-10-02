"""Render a ~36 s demo reel of every toolkit function into demo_out/.

    python3 demo.py            # full 1920x1080 reel, thumbnails, contact sheet
    python3 demo.py --quick    # 960x540, for a fast look

Assets: one public-domain catalogue page (demo_assets/, see SOURCES.md) and a newspaper page drawn here with PIL.
Audio: sine tones standing in for narration and music, to exercise ducking and loudness. They are a test signal.
"""
import io
import os
import subprocess
import sys
import time
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unbuilt_kit as kit  # noqa: E402
from unbuilt_kit.core import ffmpeg_exe, font  # noqa: E402

OUT = os.path.join(HERE, "demo_out")
DESIGN = os.path.join(HERE, "demo_assets", "watkin_design37_1890.jpg")


def make_newspaper(path):
    """A fictional newspaper page, aged to look scanned. It imitates no real paper and says so on the page."""
    W, H = 1500, 2000
    rng = np.random.default_rng(1890)
    page = Image.new("RGB", (W, H), (226, 216, 194))
    d = ImageDraw.Draw(page)
    ink = (38, 34, 30)
    d.text((W / 2, 70), "THE DEMONSTRATION GAZETTE", font=font("serif", 92, "bold"), fill=ink, anchor="mt")
    d.line([(60, 190), (W - 60, 190)], fill=ink, width=3)
    d.text((W / 2, 205), "TOOLKIT TEST PAGE · NOT A REAL NEWSPAPER · PRICE ONE PENNY", font=font("serif", 26),
           fill=ink, anchor="mt")
    d.line([(60, 245), (W - 60, 245)], fill=ink, width=1)
    d.text((W / 2, 285), "THE GREAT TOWER AT WEMBLEY", font=font("serif", 70, "bold"), fill=ink, anchor="mt")
    d.text((W / 2, 375), "A demonstration column for the highlight tool", font=font("serif", 34, "italic"), fill=ink,
           anchor="mt")
    body = font("serif", 25)
    filler = ("This column is set by the toolkit so the highlight function has something to work on. It stands in "
              "for a real scan from a newspaper archive, which an episode would use instead, with its source in "
              "the description. The type, the rules and the ageing are drawn by code. ")
    key = "The passage to highlight sits here, inside the box the demo passes to the highlight function."
    cols, top, gap = 3, 450, 40
    cw = (W - 120 - gap * (cols - 1)) / cols
    box = None
    for c in range(cols):
        x = 60 + c * (cw + gap)
        y = top
        words = (filler * 9).split()
        line = ""
        n_line = 0
        while y < H - 120 and words:
            wd = words.pop(0)
            if body.getlength(line + " " + wd) > cw:
                d.text((x, y), line.strip(), font=body, fill=ink)
                y += 34
                n_line += 1
                line = ""
                if c == 1 and n_line == 14:          # the highlighted passage, middle column
                    y += 12
                    kb = font("serif", 27, "bold")
                    kl, cur = [], ""
                    for kw in key.split():
                        if kb.getlength(cur + " " + kw) > cw:
                            kl.append(cur.strip())
                            cur = ""
                        cur += " " + kw
                    kl.append(cur.strip())
                    y0 = y
                    for k in kl:
                        d.text((x, y), k, font=kb, fill=ink)
                        y += 36
                    box = ((x - 8) / W, (y0 - 8) / H, (x + cw + 8) / W, (y + 4) / H)
                    y += 12
            line += " " + wd
        if c < cols - 1:
            d.line([(x + cw + gap / 2, top), (x + cw + gap / 2, H - 120)], fill=ink, width=1)
    # age it: blur, uneven tone, speckle, slight skew
    a = np.asarray(page.filter(ImageFilter.GaussianBlur(0.7)), np.float32)
    tone = np.asarray(Image.fromarray((rng.random((20, 15)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                      np.float32)[..., None] / 255
    a = a * (0.93 + 0.07 * tone) + rng.normal(0, 5, a.shape)
    a[rng.random((H, W)) > 0.9993] = 60
    page = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).rotate(0.4, resample=Image.BICUBIC,
                                                                        fillcolor=(214, 204, 182))
    page.save(path, quality=92)
    return box


def make_tones(voice_path, music_path, seconds):
    """TEST SIGNAL: a 'voice' tone that switches on and off like speech, and a two-note 'music' bed."""
    sr = 48000
    t = np.arange(int(sr * seconds)) / sr
    gate = np.clip(np.minimum((t % 4.0) * 8, (3.0 - t % 4.0) * 8), 0, 1)          # 3 s on, 1 s off
    voice = 0.3 * np.sin(2 * np.pi * 196 * t) * gate
    music = 0.15 * (np.sin(2 * np.pi * 261.6 * t) + np.sin(2 * np.pi * 392 * t))
    for path, x in ((voice_path, voice), (music_path, music)):
        w = wave.open(path, "wb")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
        w.close()


def contact_sheet(video, out_png, cols=5, rows=6, width=384):
    """Evenly spaced frames from a video, tiled with their timecodes."""
    dur = kit.probe(video)["duration"]
    times = [(i + 0.5) * dur / (cols * rows) for i in range(cols * rows)]
    tiles = []
    for t in times:
        png = subprocess.run([ffmpeg_exe(), "-nostdin", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", video,
                              "-frames:v", "1", "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        tiles.append(Image.open(io.BytesIO(png)).convert("RGB"))
    w, h = tiles[0].size
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 30) + 8), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (im, t) in enumerate(zip(tiles, times)):
        x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 30)
        sheet.paste(im, (x, y))
        d.text((x, y + h + 4), f"{t:5.1f} s", fill=(220, 220, 220), font=font("sans", 18))
    sheet.save(out_png)
    return out_png


def main(quick=False):
    os.makedirs(OUT, exist_ok=True)
    size = (960, 540) if quick else kit.HD
    p = lambda name: os.path.join(OUT, name)  # noqa: E731
    t0 = time.time()

    news = p("newspaper_demo.jpg")
    box = make_newspaper(news)

    kit.title_card(p("01_title.mp4"), 4.5, "The Tower at Wembley", "A toolkit demo · UNBUILT", size=size)
    kit.kenburns(DESIGN, p("02_kenburns.mp4"), 6, start=(0.5, 0.45, 1.0), end=(0.55, 0.32, 1.9), size=size)
    kit.annotate(DESIGN, p("03_annotate.mp4"), 6.5, size=size, marks=[
        {"type": "underline", "from": (0.42, 0.168), "to": (0.69, 0.168), "at": 0.6},
        {"type": "ellipse", "center": (0.32, 0.35), "radii": (0.15, 0.055), "at": 1.5},
        {"type": "arrow", "from": (0.86, 0.36), "to": (0.60, 0.43), "at": 3.0},
        {"type": "label", "text": "First prize, 1890", "pos": (0.72, 0.32), "anchor": "c", "at": 4.0},
    ])
    kit.highlight(news, p("04_highlight.mp4"), 5.5, box=box, size=size)
    kit.scale_compare(p("05_scale.mp4"), 7, [
        {"name": "Watkin's Tower (design)", "height_m": 358, "shape": "taper", "accent": True},
        {"name": "Eiffel Tower", "height_m": 330, "shape": "taper"},
        {"name": "The Shard", "height_m": 310, "shape": "taper"},
        {"name": "Big Ben", "height_m": 96},
        {"name": "Wembley arch", "height_m": 133, "shape": "arch"},
    ], size=size, title="Drawn to one scale")
    kit.timeline(p("06_timeline.mp4"), 7, [
        (1889, "Eiffel Tower"), (1890, "Competition"), (1896, "Opened to the public"), (1907, "Demolished"),
        (1923, "Empire Stadium"), (2007, "New Wembley"),
    ], size=size, title="Wembley, 1889 to 2007")
    kit.quote_card(p("07_quote.mp4"), 5.5, "Sample quotation set in the house style. In an episode the words "
                   "come from the archive, and the source goes in the description.",
                   "Demo text, not a real quotation", size=size)
    kit.end_card(p("08_end.mp4"), 4, size=size)

    # lower third laid over the Ken Burns shot
    kit.lower_third(p("lower_third.mov"), 4, "Design No. 37", "Stewart, MacLaren and Dunn, 1890", size=size)
    kit.overlay(p("02_kenburns.mp4"), p("lower_third.mov"), p("02_kenburns_lt.mp4"), start=1.0)

    shots = [{"clip": p(n)} for n in ("01_title.mp4", "02_kenburns_lt.mp4", "03_annotate.mp4", "04_highlight.mp4",
                                      "05_scale.mp4", "06_timeline.mp4", "07_quote.mp4", "08_end.mp4")]
    reel_len = sum(kit.probe(s["clip"])["duration"] for s in shots) - 0.6 * (len(shots) - 1)
    make_tones(p("TEST_voice_tone.wav"), p("TEST_music_tone.wav"), reel_len - 0.5)
    kit.assemble(shots, p("TEST_voice_tone.wav"), p("TEST_music_tone.wav"), p("demo_reel.mp4"), crossfade=0.6,
                 size=size)

    # a Shorts-format title and a captioned cut of it
    kit.title_card(p("short_title.mp4"), 4, "The Tower at Wembley", "Never finished", size=(size[1], size[1] * 16 // 9))
    with open(p("demo.srt"), "w") as f:
        f.write("1\n00:00:00,300 --> 00:00:02,000\nCaption test in the house sans.\n\n"
                "2\n00:00:02,100 --> 00:00:03,900\nWritten by hand, not transcribed.\n")
    kit.captions_burn(p("short_title.mp4"), p("demo.srt"), p("short_captioned.mp4"), vertical=True)
    kit.captions_burn(p("07_quote.mp4"), p("demo.srt"), p("quote_captioned.mp4"))

    for v in (1, 2, 3):
        kit.thumbnail(p(f"thumb_{v}.png"), DESIGN if v != 2 else news, overlay_image=DESIGN,
                      text=["NEVER FINISHED", "LONDON'S EIFFEL", "SOLD FOR SCRAP"][v - 1], variant=v)

    contact_sheet(p("demo_reel.mp4"), p("contact.png"))
    info = kit.probe(p("demo_reel.mp4"))
    print(f"demo_reel.mp4: {info['width']}x{info['height']} {info['fps']} fps {info['duration']:.2f} s, "
          f"{kit.loudness(p('demo_reel.mp4')):.1f} LUFS  ({time.time() - t0:.0f} s to render)")


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
