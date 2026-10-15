"""Cut vertical Shorts (1080x1920) from a finished 16:9 episode, at no generation cost.

Each Short is one continuous stretch of the finished cut, so the picture, voice and music stay exactly as
edited (no music jumps). Layout, in the house colours:
  - title block on paper at the top (the last seconds swap it for a pointer to the full episode)
  - the whole 16:9 frame, full width, uncropped, so lower thirds and source labels stay readable
  - captions below the picture, taken from the episode's own caption file (the script's words)

Usage: python3 shorts_from_cut.py <shorts.json> [name ...]
shorts.json: {"video": path, "captions": srt path, "out": dir, "end_tag": [line, line],
              "shorts": {name: {"cues": [first, last], "title": [line, line]}}}  (paths relative to the json)
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unbuilt_kit.core import ACCENT, INK, PAPER, ffmpeg_exe  # noqa: E402


def rgb8(c):
    return tuple(int(round(v * 255)) if isinstance(v, float) else int(v) for v in c[:3])


ACCENT, INK, PAPER = rgb8(ACCENT), rgb8(INK), rgb8(PAPER)

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
SW, SH = 1080, 1920
PIC_Y = 620                      # top of the 1080x608 picture
TITLE_Y = 330                    # first title line
CAP_Y = 1300                     # top of the caption block
END_TAG = 3.0                    # seconds of "full story" at the end
PAD_IN, PAD_OUT = 0.25, 0.7      # around the first and last cue


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def parse_srt(path):
    def secs(s):
        h, m, rest = s.split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    cues = []
    for blk in open(path, encoding="utf-8").read().strip().split("\n\n"):
        lines = blk.strip().split("\n")
        a, b = [secs(x.strip()) for x in lines[1].split("-->")]
        cues.append((a, b, " ".join(lines[2:])))
    return cues


def fitted(name, size, lines, width):
    """The largest size up to `size` at which every line fits `width`."""
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while size > 30 and max(probe.textlength(x, font=font(name, size)) for x in lines) > width:
        size -= 2
    return font(name, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build(cfg, base, name, spec):
    out_dir = os.path.join(base, cfg["out"])
    work = os.path.join(out_dir, "work", name)
    os.makedirs(work, exist_ok=True)
    cues = parse_srt(os.path.join(base, cfg["captions"]))
    first, last = spec["cues"]
    t0 = max(0.0, cues[first - 1][0] - PAD_IN)
    t1 = cues[last - 1][1] + PAD_OUT
    if last < len(cues):
        t1 = min(t1, cues[last][0] - 0.05)
    dur = t1 - t0

    title_f = fitted("LiberationSerif-Bold.ttf", 76, spec["title"], SW - 80)
    cap_f = font("LiberationSans-Bold.ttf", 56)
    tag_f = fitted("LiberationSerif-Bold.ttf", 60, cfg["end_tag"], SW - 80)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    # background: paper, with the title
    bg = Image.new("RGB", (SW, SH), PAPER)
    d = ImageDraw.Draw(bg)
    for i, line in enumerate(spec["title"]):
        w = d.textlength(line, font=title_f)
        d.text(((SW - w) / 2, TITLE_Y + i * 92), line, font=title_f, fill=INK if i == 0 else ACCENT)
    d.rectangle([SW / 2 - 60, TITLE_Y + len(spec["title"]) * 92 + 20, SW / 2 + 60, TITLE_Y + len(spec["title"]) * 92 + 26],
                fill=ACCENT)
    bg_path = os.path.join(work, "bg.png")
    bg.save(bg_path)

    # end tag: covers the title for the last seconds
    tag = Image.new("RGBA", (SW, PIC_Y), PAPER + (255,))
    td = ImageDraw.Draw(tag)
    for i, line in enumerate(cfg["end_tag"]):
        w = td.textlength(line, font=tag_f)
        td.text(((SW - w) / 2, TITLE_Y + i * 80), line, font=tag_f, fill=INK if i == 0 else ACCENT)

    # captions, in Short time
    caps = []
    for a, b, text in cues:
        if b <= t0 or a >= t1:
            continue
        caps.append((max(0.0, a - t0), min(dur, b - t0), wrap(probe, text, cap_f, SW - 140)))

    # one overlay track: a full-frame transparent PNG per stretch where the overlay doesn't change,
    # joined with the concat demuxer (one input, so memory stays flat however many cues there are)
    tag_at = dur - END_TAG
    cuts = sorted({0.0, dur, tag_at} | {x for a, b, _ in caps for x in (a, b)})
    entries = []
    for k, (a, b) in enumerate(zip(cuts, cuts[1:])):
        if b - a < 0.001:
            continue
        mid = (a + b) / 2
        im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        if mid >= tag_at:
            im.paste(tag, (0, 0))
        cap = next((c for c in caps if c[0] <= mid < c[1]), None)
        if cap:
            cd = ImageDraw.Draw(im)
            for i, line in enumerate(cap[2]):
                w = cd.textlength(line, font=cap_f)
                cd.text(((SW - w) / 2, CAP_Y + i * 70), line, font=cap_f, fill=INK)
        p = os.path.join(work, f"ov_{k:03d}.png")
        im.save(p)
        entries.append((p, b - a))
    lst = os.path.join(work, "overlay.txt")
    with open(lst, "w") as f:
        for p, d_ in entries:
            f.write(f"file '{p}'\nduration {d_:.3f}\n")
        f.write(f"file '{entries[-1][0]}'\n")

    ff = ffmpeg_exe()
    cmd = [ff, "-nostdin", "-loglevel", "error", "-y",
           "-loop", "1", "-framerate", "30", "-i", bg_path,
           "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", os.path.join(base, cfg["video"]),
           "-f", "concat", "-safe", "0", "-i", lst]
    fc = [f"[1:v]scale={SW}:-2,setsar=1,fps=30[pic]",
          f"[0:v][pic]overlay=0:{PIC_Y}:shortest=1[v0]",
          "[2:v]fps=30,format=rgba[ov]",
          "[v0][ov]overlay=0:0:eof_action=repeat,format=yuv420p[vout]",
          f"[1:a]afade=t=in:d=0.25,afade=t=out:st={dur - 0.6:.3f}:d=0.6[aout]"]
    out = os.path.join(out_dir, f"{name}.mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]", "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"{name}: {t0:.2f}-{t1:.2f} ({dur:.1f} s), {len(caps)} caption cues -> {out}")
    return out


def main():
    cfg_path = sys.argv[1]
    base = os.path.dirname(os.path.abspath(cfg_path))
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    names = sys.argv[2:] or list(cfg["shorts"])
    for n in names:
        build(cfg, base, n, cfg["shorts"][n])


if __name__ == "__main__":
    main()
