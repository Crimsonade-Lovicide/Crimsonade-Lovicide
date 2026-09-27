"""Cut vertical Shorts (1080x1920) from the finished episode, at no generation cost.

Each Short is a run of beats from the edit (assemble.py), trimmed in beat-relative time:
  - picture: the rendered beat clips; beats that carried a section card are re-rendered without it
  - layout: a 1:1 crop of the 16:9 frame over a blurred fill, a title block above, captions on the picture
  - voice: sliced sample-accurately from build/voice.wav, so the lips stay in sync
  - music: a fresh, continuous bed from the theme's breakdown loop, ducked under the voice
    (slicing the episode mix would make the music jump at every edit)
  - captions: word-timed from a transcription of the Short's own voice, with a fixed spelling list
The last seconds swap the title for a pointer to the full episode.

Usage: python3 shorts.py <asset_dir> <music.mp3> <out_dir> [short ...]
       python3 shorts.py <asset_dir> <music.mp3> <out_dir> --sheet   (crop contact sheets for review)
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG", "ffmpeg")
A, MUSIC, OUT = sys.argv[1:4]
ARGS = sys.argv[4:]
FONTS = os.environ.get("FONTS", os.path.join(A, "..", "thumb"))
SW, SH, FPS, SR = 1080, 1920, 24, 48000
PIC_Y = 500                 # top of the square picture
CAP_Y = 1330                # caption centre line (lower third of the picture)
END_TAG = 3.0               # seconds of "full episode" at the end
BUILD = os.path.join(OUT, "build")
os.makedirs(BUILD, exist_ok=True)

# (beat, start, end or None for the beat's end, voice on?) in beat-relative seconds.
# crop: {beat: [(t, x)]}, x is the crop centre as a fraction of frame width, keyframes in beat time.
SHORTS = {
    "dome": dict(
        title=["HE WANTED TO PUT", "MANHATTAN UNDER GLASS"],
        segs=[(38, 0, None, 1), (39, 0, None, 1), (40, 0, None, 1), (41, 0, None, 1), (42, 0, None, 1),
              (43, 0, 1.5, 0)],
        crop={}),
    "atlantropa": dict(
        title=["THE MAN WHO WANTED TO", "DRAIN THE MEDITERRANEAN"],
        segs=[(45, 2.07, None, 1), (46, 0, None, 1), (47, 0, None, 1), (48, 0, None, 1), (49, 0, None, 1),
              (50, 0, None, 1), (51, 0, 1.5, 0)],
        crop={45: [(0, 0.56), (8.31, 0.56), (8.34, 0.42)], 46: [(0, 0.43)]}),
    "elephant": dict(
        title=["NAPOLEON'S ELEPHANT", "BECAME A RAT HOTEL"],
        segs=[(8, 0, None, 1), (10, 0, None, 1), (11, 0, None, 1), (13, 0, None, 1), (15, 0, None, 1),
              (16, 0, None, 1)],
        crop={}),
    "beach": dict(
        title=["NEW YORK HAD A", "SUBWAY IN 1870"],
        segs=[(17, 0, None, 1), (18, 0, None, 1), (19, 0, None, 1), (21, 0, None, 1), (22, 0, None, 1),
              (27, 0, None, 1), (28, 0, None, 1)],
        crop={18: [(0, 0.62)], 19: [(0, 0.44)], 28: [(0, 0.47)]}),
}

# ASR spellings -> the script's
FIX = {
    "sergall": "Sörgel", "sergil": "Sörgel", "sergio": "Sörgel", "sergel": "Sörgel", "sorgel": "Sörgel",
    "sergal": "Sörgel", "sergil's": "Sörgel's", "sergel's": "Sörgel's", "kilometers": "kilometres",
    "beech": "Beach", "beech's": "Beach's",
    "lutjens": "Lutyens", "sadeo": "Sadao", "sado": "Sadao", "sado's": "Sadao's", "meters": "metres",
    "neighbors": "neighbours", "miserables": "Misérables", "luce": "Loos", "stripped": "crypt",
    "hermann": "Herman",
}


def run(cmd, **kw):
    return subprocess.run([FF, "-nostdin", "-loglevel", "error", "-y"] + cmd, check=True, **kw)


def frames_of(p):
    err = subprocess.run([FF, "-nostdin", "-i", p, "-map", "0:v", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return int(re.findall(r"frame=\s*(\d+)", err)[-1])


# ---------------------------------------------------------------- the edit: beats and their times
sys.argv = ["assemble.py", A, os.devnull]
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assemble.py")).read()
G = {"__name__": "shorts"}
exec(_src.split('if __name__ == "__main__":')[0], G)
BEATS = G["BEATS"]
STARTS = json.load(open(os.path.join(A, "build", "timeline.json")))["starts"]


def beat_clip(i):
    """The rendered beat; a beat that carried a section card is re-rendered clean."""
    if not BEATS[i]["overlay"]:
        return os.path.join(A, "build", f"beat_{i:03d}.mp4")
    p = os.path.join(BUILD, f"beat_{i:03d}.mp4")
    if not os.path.exists(p):
        G["TMP"] = BUILD
        out, _ = G["render_beat"](i, dict(BEATS[i], overlay=None))
        G["TMP"] = os.path.join(A, "build")
        # same picture timing as the original (it may run a frame long without the overlay's -t; trimmed later)
        assert abs(frames_of(out) - round((STARTS[i + 1] - STARTS[i]) * FPS)) <= 1, f"beat {i} length differs"
    return p


def seg_len(s):
    b, t0, t1, _ = s
    return (t1 if t1 is not None else STARTS[b + 1] - STARTS[b]) - t0


def crop_expr(keys, t0):
    """Piecewise-linear crop x (pixels, 1280-wide frame, 720 crop) over segment time t."""
    if not keys:
        keys = [(0, 0.5)]
    px = [(t - t0, min(max(x * 1280 - 360, 0), 560)) for t, x in keys]
    if len(px) == 1:
        return f"{px[0][1]:.1f}"
    e = f"{px[-1][1]:.1f}"
    for (ta, xa), (tb, xb) in reversed(list(zip(px, px[1:]))):
        e = f"if(lt(t,{tb:.3f}),{xa:.1f}+({xb - xa:.1f})*clip((t-{ta:.3f})/{tb - ta:.3f},0,1),{e})"
    return e


# ---------------------------------------------------------------- picture
def picture(name, cfg):
    outs = []
    for k, s in enumerate(cfg["segs"]):
        b, t0, _, _ = s
        d = seg_len(s)
        n = round(d * FPS)
        x = crop_expr(cfg["crop"].get(b, []), t0)
        fc = (f"[0:v]trim=start={t0:.4f},setpts=PTS-STARTPTS,split[a][b];"
              f"[a]crop=405:720:437:0,scale={SW}:{SH},boxblur=24:3,eq=brightness=-0.12:saturation=0.8[bg];"
              f"[b]crop=720:720:'{x}':0,scale=1080:1080:flags=lanczos,unsharp=5:5:0.35:5:5:0[fg];"
              f"[bg][fg]overlay=0:{PIC_Y},fps={FPS},trim=end_frame={n},format=yuv420p[v]")
        o = os.path.join(BUILD, f"{name}_{k:02d}.mp4")
        run(["-i", beat_clip(b), "-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium",
             "-crf", "16", o])
        outs.append((o, n))
    lst = os.path.join(BUILD, f"{name}_list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(o)}'\nduration {n / FPS:.6f}\n" for o, n in outs)
    vid = os.path.join(BUILD, f"{name}_pic.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    return vid, sum(n for _, n in outs) / FPS


# ---------------------------------------------------------------- sound
def load_wav(p):
    w = wave.open(p)
    y = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, w.getnchannels())
    return y.astype(np.float32) / 32768, w.getframerate()


def voice(name, cfg):
    y, sr = load_wav(os.path.join(A, "build", "voice.wav"))
    assert sr == SR
    parts = []
    for s in cfg["segs"]:
        b, t0, _, on = s
        n = round(round(seg_len(s) * FPS) / FPS * SR)  # match the picture's frame-rounded length
        a = round((STARTS[b] + t0) * SR)
        seg = y[a:a + n].copy() if on else np.zeros((n, 2), np.float32)
        seg = np.pad(seg, ((0, n - len(seg)), (0, 0)))
        f = int(0.01 * SR)
        seg[:f] *= np.linspace(0, 1, f)[:, None]
        seg[-f:] *= np.linspace(1, 0, f)[:, None]
        parts.append(seg)
    v = np.concatenate(parts)
    return v


def bed(total):
    """The breakdown loop (32 beats, 32.369-48.367s), looped on the beat, faded at both ends."""
    wav = os.path.join(BUILD, "music48.wav")
    if not os.path.exists(wav):
        run(["-i", MUSIC, "-ac", "2", "-ar", str(SR), "-sample_fmt", "s16", wav])
    trk, _ = load_wav(wav)
    a, b = round(32.369 * SR), round(48.367 * SR)
    loop = trk[a:b]
    n = round(total * SR)
    m = np.tile(loop, (n // len(loop) + 1, 1))[:n].copy()
    k = int(0.01 * SR)
    for j in range(len(loop), n, len(loop)):  # soften each seam
        m[j - k:j] *= np.linspace(1, 0.6, k)[:, None]
        m[j:j + k] *= np.linspace(0.6, 1, k)[:, None]
    fi, fo = int(0.4 * SR), int(1.5 * SR)
    m[:fi] *= np.linspace(0, 1, fi)[:, None]
    m[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return m * 10 ** (-8 / 20)


def write_wav(p, y):
    o = wave.open(p, "wb")
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    o.close()


def mix(name, v, total):
    vp, mp = os.path.join(BUILD, f"{name}_voice.wav"), os.path.join(BUILD, f"{name}_bed.wav")
    write_wav(vp, v)
    write_wav(mp, bed(total))
    pre = os.path.join(BUILD, f"{name}_premix.wav")
    run(["-i", vp, "-i", mp, "-filter_complex",
         "[0:a]asplit=2[v1][v2];[1:a][v2]sidechaincompress=threshold=0.02:ratio=6:attack=10:release=450:knee=4[m];"
         "[v1][m]amix=inputs=2:normalize=0:duration=first[mix]", "-map", "[mix]", pre])
    err = subprocess.run([FF, "-nostdin", "-i", pre, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
    return pre, vp, -14.0 - lufs


# ---------------------------------------------------------------- captions and titles
def words(vp):
    from faster_whisper import WhisperModel
    y16 = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-i", vp, "-ac", "1", "-ar", "16000", "-f", "s16le",
                          "-"], capture_output=True, check=True).stdout
    y16 = np.frombuffer(y16, dtype=np.int16).astype(np.float32) / 32768
    model = WhisperModel(os.environ.get("WHISPER", "small.en"), compute_type="int8")
    segs, _ = model.transcribe(y16, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            core = re.sub(r"[^\w'’]", "", t).lower()
            if core in FIX:
                t = t.lower().replace(core, FIX[core])
            if t.startswith("-") and out:  # "full -size": ASR splits hyphenated words
                out[-1][0] += t
                out[-1][2] = w.end
                continue
            out.append([t, w.start, w.end])
    return out


def chunks(ws):
    """2-4 word caption groups, broken at punctuation and pauses."""
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        chars = sum(len(x[0]) + 1 for x in cur)
        if (nxt is None or w[0][-1] in ".,?!;:" or (nxt[1] - w[2]) > 0.25 or len(cur) >= 4
                or (chars + len(nxt[0]) > 18 and len(cur) >= 2)):
            groups.append(cur)
            cur = []
    return groups


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


CAP_F = font("Anton-Regular.ttf", 86)
TITLE_F = font("Anton-Regular.ttf", 74)
LABEL_F = font("BebasNeue-Regular.ttf", 46)
YELLOW, WHITE, RED = (255, 214, 0, 255), (255, 255, 255, 255), (229, 9, 20, 255)


def centered(d, y, text, f, fill, stroke=6):
    w = d.textlength(text, font=f)
    d.text(((SW - w) / 2, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))


def spaced_center(d, y, text, f, fill, gap):
    w = sum(d.textlength(c, font=f) + gap for c in text) - gap
    x = (SW - w) / 2
    for c in text:
        d.text((x, y), c, font=f, fill=fill, stroke_width=3, stroke_fill=(0, 0, 0, 255))
        x += d.textlength(c, font=f) + gap


def layer(title, group=None, hi=None):
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    spaced_center(d, 262, "UNBUILT", LABEL_F, RED, 10)
    for j, line in enumerate(title):
        centered(d, 318 + j * 84, line, TITLE_F, WHITE, 5)
    if group:
        toks = [re.sub(r"[.,;:]$", "", w[0]).upper() for w in group]
        # wrap to lines no wider than 920 px
        lines, cur = [], []
        for j, t in enumerate(toks):
            trial = " ".join(toks[k] for k in cur + [j])
            if cur and d.textlength(trial, font=CAP_F) > 920:
                lines.append(cur)
                cur = []
            cur.append(j)
        lines.append(cur)
        y = CAP_Y - len(lines) * 100 / 2
        for line in lines:
            full = " ".join(toks[k] for k in line)
            x = (SW - d.textlength(full, font=CAP_F)) / 2
            for k in line:
                d.text((x, y), toks[k], font=CAP_F, fill=YELLOW if k == hi else WHITE, stroke_width=8,
                       stroke_fill=(0, 0, 0, 255))
                x += d.textlength(toks[k] + " ", font=CAP_F)
            y += 100
    return im


def text_track(name, cfg, ws, total):
    """Caption/title states as a PNG sequence with durations (concat demuxer), overlaid on the picture."""
    events = []  # (start, title, group, hi)
    end_title = ["FULL EPISODE", "ON THE CHANNEL"]
    t_end = total - END_TAG
    groups = chunks(ws)
    events.append((0.0, None, None))
    for gi, g in enumerate(groups):
        g_end = groups[gi + 1][0][1] if gi + 1 < len(groups) else g[-1][2] + 0.4
        g_end = min(g_end, g[-1][2] + 0.6)
        for wi, w in enumerate(g):
            events.append((w[1], g, wi))
        events.append((g_end, None, None))
    events.sort(key=lambda e: e[0])
    # split at the end-tag time
    cuts = sorted(set([round(e[0] * FPS) for e in events] + [round(t_end * FPS), 0]))
    frames_total = round(total * FPS)
    cuts = [c for c in cuts if c < frames_total]
    lst, files = os.path.join(BUILD, f"{name}_text.txt"), {}
    with open(lst, "w") as f:
        for j, c in enumerate(cuts):
            t = c / FPS
            state = None
            for e in events:
                if e[0] <= t + 1e-6:
                    state = e
            title = end_title if t >= t_end - 1e-6 else cfg["title"]
            key = (tuple(title), id(state[1]) if state and state[1] else None, state[2] if state else None)
            if key not in files:
                p = os.path.join(BUILD, f"{name}_txt_{len(files):04d}.png")
                layer(title, state[1] if state else None, state[2] if state else None).save(p)
                files[key] = p
            nxt = cuts[j + 1] if j + 1 < len(cuts) else frames_total
            f.write(f"file '{os.path.abspath(files[key])}'\nduration {(nxt - c) / FPS:.6f}\n")
        f.write(f"file '{os.path.abspath(files[key])}'\n")
    return lst


# ---------------------------------------------------------------- review sheets
def sheet(name, cfg):
    tiles = []
    for s in cfg["segs"]:
        b, t0, _, _ = s
        d = seg_len(s)
        for fr in (0.1, 0.5, 0.9):
            t = t0 + d * fr
            p = os.path.join(BUILD, "sheet_tmp.png")
            run(["-ss", f"{t:.3f}", "-i", beat_clip(b), "-frames:v", "1", p])
            im = Image.open(p).convert("RGB").resize((320, 180))
            dr = ImageDraw.Draw(im)
            keys = cfg["crop"].get(b, [(0, 0.5)])
            x = keys[0][1]
            for kt, kx in keys:
                if kt <= t:
                    x = kx
            cx = x * 320
            dr.rectangle([cx - 90, 0, cx + 90, 179], outline=(255, 214, 0), width=2)
            dr.text((4, 4), f"b{b} t{t:.1f}", fill=(255, 255, 0))
            tiles.append(im)
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * 324, rows * 184), "black")
    for k, im in enumerate(tiles):
        out.paste(im, ((k % cols) * 324, (k // cols) * 184))
    p = os.path.join(OUT, f"sheet_{name}.jpg")
    out.save(p, quality=85)
    print(p)


# ---------------------------------------------------------------- main
names = [a for a in ARGS if not a.startswith("--")] or list(SHORTS)
for name in names:
    cfg = SHORTS[name]
    if "--sheet" in ARGS:
        sheet(name, cfg)
        continue
    pic, total = picture(name, cfg)
    v = voice(name, cfg)
    pre, vp, gain = mix(name, v, total)
    ws = words(vp)
    print(f"[{name}] {total:.1f}s  captions: " + " ".join(w[0] for w in ws))
    txt = text_track(name, cfg, ws, total)
    out = os.path.join(OUT, f"short_{name}.mp4")
    run(["-i", pic, "-f", "concat", "-safe", "0", "-i", txt, "-i", pre, "-filter_complex",
         f"[1:v]format=rgba[t];[0:v][t]overlay=0:0:shortest=1,format=yuv420p[v];"
         f"[2:a]volume={gain:.2f}dB,alimiter=limit=0.84:level=disabled[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "256k", "-t", f"{total:.3f}", "-movflags", "+faststart", out])
    json.dump(ws, open(os.path.join(BUILD, f"{name}_words.json"), "w"))
    print(f"[{name}] -> {out}")
