"""Cut vertical Shorts from a finished standard episode's 9:16 master, at no generation cost.

The standard episodes (host Chiara Valenti) are built elsewhere; the only file here is the published 9:16 master,
which carries the 16:9 picture as a full-width band. Each Short is one continuous stretch of it, so the music under
the voice never jumps, laid out like the standard episodes' other Shorts:
  - title at the top (Bebas Neue, ivory, key words in amber), the 16:9 picture full width in the middle,
    over a blurred, darkened copy of itself
  - a small disclosure line under the picture, captions in 1-3 word phrases, and the channel footer
  - sound: the episode mix, faded at both ends and normalised to -14 LUFS
  - captions: word times from a transcription of the whole episode, with a fixed spelling list

Usage: python3 shorts.py <master_9x16.mp4> <transcript.json> <out_dir> [short ...]
transcript.json: faster-whisper segments with "words": [[word, start, end], ...] (see README).
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FF = os.environ.get("FFMPEG", "ffmpeg")
MASTER, TRANSCRIPT, OUT = sys.argv[1:4]
ARGS = sys.argv[4:]
FONTS = os.environ.get("FONTS", os.path.join(os.path.dirname(MASTER), "..", "thumb"))
MONO = os.environ.get("MONO", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
SW, SH, FPS = 1080, 1920, 24
BAND_Y, BAND_H = 656, 608   # the 16:9 picture inside the master
PIC_Y = 700                 # where it sits in the Short
BUILD = os.path.join(OUT, "build")
os.makedirs(BUILD, exist_ok=True)

# start and end in episode seconds; *word* in a title is set in amber
SHORTS = {
    "hotel_bill": dict(
        start=0.0, end=28.3,
        title="TESLA'S TOWER WASN'T KILLED BY A BANKER. IT WAS A *HOTEL BILL*"),
    "morgan": dict(
        start=205.15, end=257.75,
        title="TESLA TOLD J. P. MORGAN THE TRUTH. MORGAN REPLIED IN *ONE SENTENCE*"),
    "castle": dict(
        start=309.4, end=364.4,
        title="THE MAN WHO TOOK TESLA'S TOWER HAD AN *UNFINISHED CASTLE* OF HIS OWN"),
    "dynamite": dict(
        start=371.1, end=418.5,
        title="THEY BLEW UP TESLA'S TOWER ON THE *FOURTH OF JULY*"),
    "worked": dict(
        start=425.25, end=484.65,
        title="COULD TESLA'S TOWER HAVE *WORKED*?"),
}

# ASR spellings -> the episode's
FIX = {
    "bolt": "Boldt", "bolt's": "Boldt's", "wardencliff": "Wardenclyffe", "seville": "Sayville",
    "patterns": "patents", "astoria": "Astoria",
}

IVORY, AMBER, GREY = (240, 236, 226, 255), (222, 150, 64, 255), (170, 170, 170, 255)


def run(cmd, **kw):
    return subprocess.run([FF, "-nostdin", "-loglevel", "error", "-y"] + cmd, check=True, **kw)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


TITLE_F, CAP_F, BRAND_F = font("BebasNeue-Regular.ttf", 104), font("BebasNeue-Regular.ttf", 100), \
    font("BebasNeue-Regular.ttf", 60)
SMALL_F = ImageFont.truetype(MONO, 25)


# ---------------------------------------------------------------- words
def words(cfg):
    segs = json.load(open(TRANSCRIPT))
    out = []
    for w in (w for s in segs for w in s["words"]):
        t, a, b = w
        if a < cfg["start"] - 0.05 or b > cfg["end"] + 0.05:
            continue
        core = re.sub(r"[^\w'’]", "", t).lower()
        if core in FIX:
            t = t.lower().replace(core, FIX[core])
        if out and (t.startswith("-") or (re.match(r",\d", t) and out[-1][0][-1:].isdigit())
                    or (t.startswith(".") and len(out[-1][0]) <= 2)):  # "U .S."
            out[-1][0] += t
            out[-1][2] = b - cfg["start"]
            continue
        if out and t.lower() == out[-1][0].lower() and a - cfg["start"] - out[-1][2] < 0.3:
            out[-1] = [t, a - cfg["start"], b - cfg["start"]]  # the ASR repeats a word across segments ("the The")
            continue
        out.append([t, a - cfg["start"], b - cfg["start"]])
    return out


def chunks(ws):
    """1-3 word caption phrases, broken at punctuation and pauses."""
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        chars = sum(len(x[0]) + 1 for x in cur)
        if (nxt is None or w[0][-1] in ".,?!;:" or (nxt[1] - w[2]) > 0.25 or len(cur) >= 3
                or (chars + len(nxt[0]) > 16 and len(cur) >= 1)):
            groups.append(cur)
            cur = []
    return groups


# ---------------------------------------------------------------- text layer
def shadowed(im, xy, text, f, fill, blur=6, alpha=200):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 3, xy[1] + 5), text, font=f, fill=(0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, text, font=f, fill=fill)


def title_lines(d, title):
    # a *multi word* span: mark every word inside it
    inside, marked = False, []
    for raw in title.split():
        start, end = raw.startswith("*"), raw.rstrip("?!.,").endswith("*")
        marked.append(inside or start)
        inside = (inside or start) and not end
    toks = [(raw.replace("*", ""), m) for raw, m in zip(title.split(), marked)]
    lines, cur = [], []
    for t in toks:
        trial = " ".join(x[0] for x in cur + [t])
        if cur and d.textlength(trial, font=TITLE_F) > 960:
            lines.append(cur)
            cur = []
        cur.append(t)
    lines.append(cur)
    return lines


def layer(title, group):
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = title_lines(d, title)
    y = PIC_Y - 40 - len(lines) * 104
    for line in lines:
        full = " ".join(t for t, _ in line)
        x = (SW - d.textlength(full, font=TITLE_F)) / 2
        for t, hot in line:
            shadowed(im, (x, y), t, TITLE_F, AMBER if hot else IVORY)
            x += d.textlength(t + " ", font=TITLE_F)
        y += 104
    y0 = PIC_Y + BAND_H + 22
    lab = "AI RECONSTRUCTIONS  ·  ARCHIVAL PHOTOS LABELLED"
    d.text(((SW - d.textlength(lab, font=SMALL_F)) / 2, y0), lab, font=SMALL_F, fill=GREY)
    if group:
        txt = " ".join(re.sub(r"[.,;:]$", "", w[0]) for w in group).upper()
        f = CAP_F
        while d.textlength(txt, font=f) > 1000:
            f = font("BebasNeue-Regular.ttf", f.size - 6)
        shadowed(im, ((SW - d.textlength(txt, font=f)) / 2, y0 + 78), txt, f, WHITE_CAP, blur=8, alpha=230)
    b = "UNBUILT"
    shadowed(im, ((SW - d.textlength(b, font=BRAND_F)) / 2, 1560), b, BRAND_F, IVORY)
    foot = "FULL EPISODE ON YOUTUBE  ·  @UNBUILTDOC"
    d.text(((SW - d.textlength(foot, font=SMALL_F)) / 2, 1634), foot, font=SMALL_F, fill=GREY)
    return im


WHITE_CAP = (255, 255, 255, 255)


def text_track(name, cfg, ws, total):
    groups = chunks(ws)
    events = [(0.0, None)]
    for gi, g in enumerate(groups):
        g_end = groups[gi + 1][0][1] if gi + 1 < len(groups) else g[-1][2] + 0.4
        events.append((max(g[0][1], 0.0), g))
        events.append((min(g_end, g[-1][2] + 0.6), None))
    events.sort(key=lambda e: e[0])
    frames_total = round(total * FPS)
    cuts = sorted(set(round(e[0] * FPS) for e in events if round(e[0] * FPS) < frames_total) | {0})
    lst, files = os.path.join(BUILD, f"{name}_text.txt"), {}
    with open(lst, "w") as f:
        for j, c in enumerate(cuts):
            state = None
            for e in events:
                if round(e[0] * FPS) <= c:
                    state = e
            key = id(state[1]) if state and state[1] else None
            if key not in files:
                p = os.path.join(BUILD, f"{name}_txt_{len(files):04d}.png")
                layer(cfg["title"], state[1] if state else None).save(p)
                files[key] = p
            nxt = cuts[j + 1] if j + 1 < len(cuts) else frames_total
            f.write(f"file '{os.path.abspath(files[key])}'\nduration {(nxt - c) / FPS:.6f}\n")
        f.write(f"file '{os.path.abspath(files[key])}'\n")
    return lst


# ---------------------------------------------------------------- render
def loudness(p):
    err = subprocess.run([FF, "-nostdin", "-i", p, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


names = [a for a in ARGS if not a.startswith("--")] or list(SHORTS)
for name in names:
    cfg = SHORTS[name]
    total = round((cfg["end"] - cfg["start"]) * FPS) / FPS
    wav = os.path.join(BUILD, f"{name}.wav")
    run(["-ss", f"{cfg['start']:.3f}", "-t", f"{total:.3f}", "-i", MASTER, "-vn", "-ac", "2", "-ar", "48000",
         "-af", f"afade=t=in:d=0.25,afade=t=out:st={total - 0.7:.3f}:d=0.7", wav])
    gain = -14.0 - loudness(wav)
    ws = words(cfg)
    print(f"[{name}] {total:.1f}s  captions: " + " ".join(w[0] for w in ws))
    txt = text_track(name, cfg, ws, total)
    out = os.path.join(OUT, f"short_{name}.mp4")
    fc = (f"[0:v]crop=1080:{BAND_H}:0:{BAND_Y},setsar=1,split[a][b];"
          f"[a]scale=-2:{SH},crop={SW}:{SH},boxblur=40:4,eq=brightness=-0.28:saturation=0.55[bg];"
          f"[bg][b]overlay=0:{PIC_Y}[pic];"
          f"[1:v]format=rgba[t];[pic][t]overlay=0:0:shortest=1,fade=t=in:d=0.25,fade=t=out:st={total - 0.5:.3f}:d=0.5,"
          f"format=yuv420p[v];"
          f"[2:a]volume={gain:.2f}dB,alimiter=limit=0.84:level=disabled[au]")
    run(["-ss", f"{cfg['start']:.3f}", "-t", f"{total:.3f}", "-i", MASTER, "-f", "concat", "-safe", "0", "-i", txt,
         "-i", wav, "-filter_complex", fc, "-map", "[v]", "-map", "[au]", "-r", str(FPS), "-c:v", "libx264",
         "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "256k", "-t", f"{total:.3f}",
         "-movflags", "+faststart", out])
    json.dump(ws, open(os.path.join(BUILD, f"{name}_words.json"), "w"))
    print(f"[{name}] -> {out}")
