"""Burn an SRT into a video in the house sans (libass via ffmpeg's subtitles filter)."""
import os
import re
import shutil
import tempfile

from PIL import ImageFont

from .core import FPS, INK, PAPER, font_path, probe, run_ffmpeg


def _ass_colour(rgb, alpha=0):
    """House colour -> ASS &HAABBGGRR."""
    r, g, b = (int(round(c * 255)) for c in rgb)
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def _ass_time(t):
    h, m, s, ms = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)", t.strip()).groups()
    cs = int(round(int(ms.ljust(3, "0")[:3]) / 10))
    return f"{int(h)}:{int(m):02d}:{int(s):02d}.{min(cs, 99):02d}"


def srt_to_ass(srt_text, width, height, family, vertical=False):
    """Convert SRT to ASS on a canvas the size of the video, so font sizes are real pixels."""
    u = min(width, height) / 1080
    size = round((64 if vertical else 50) * u)
    outline = round((5 if vertical else 3.5) * u, 1)
    margin_v = round(height * (0.30 if vertical else 0.06))
    margin_h = round(width * (0.08 if vertical else 0.10))
    style = (f"Style: House,{family},{size},{_ass_colour(PAPER)},{_ass_colour(PAPER)},{_ass_colour(INK)},"
             f"{_ass_colour(INK, 0x60)},-1,0,0,0,100,100,0,0,1,{outline},{round(1.5 * u, 1)},2,"
             f"{margin_h},{margin_h},{margin_v},1")
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}", f"PlayResY: {height}",
             "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
             "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
             "Alignment, MarginL, MarginR, MarginV, Encoding",
             style, "", "[Events]",
             "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for block in re.split(r"\n\s*\n", srt_text.replace("\r", "").strip()):
        rows = block.split("\n")
        if len(rows) < 2:
            continue
        ti = 1 if "-->" in rows[1] else 0
        if "-->" not in rows[ti]:
            continue
        a, b = rows[ti].split("-->")
        text = r"\N".join(r.strip() for r in rows[ti + 1:] if r.strip())
        lines.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},House,,0,0,0,,{text}")
    return "\n".join(lines) + "\n"


def captions_burn(video, srt, out, vertical=False):
    """Burn `srt` into `video`: paper-white bold sans with an ink outline, readable on scans and on footage.
    vertical=True: bigger type, set about 30% up the frame, clear of the Shorts interface.
    No transcription here: bring an SRT (written or corrected by hand)."""
    bold = font_path("sans", "bold")
    family = ImageFont.truetype(bold, 20).getname()[0]
    info = probe(video)
    with open(srt, encoding="utf-8-sig") as f:
        ass = srt_to_ass(f.read(), info["width"], info["height"], family, vertical)
    with tempfile.TemporaryDirectory() as tmp:
        # work inside a temp dir with plain names, so no path needs filtergraph escaping
        with open(os.path.join(tmp, "subs.ass"), "w", encoding="utf-8") as f:
            f.write(ass)
        os.makedirs(os.path.join(tmp, "fonts"))
        shutil.copy(bold, os.path.join(tmp, "fonts", os.path.basename(bold)))
        src, dst = os.path.abspath(video), os.path.abspath(out)
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            run_ffmpeg(["-i", src, "-vf", "subtitles=subs.ass:fontsdir=fonts", "-map", "0:v", "-map", "0:a?",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
                        "-c:a", "copy", "-movflags", "+faststart", dst])
        finally:
            os.chdir(cwd)
    return out
