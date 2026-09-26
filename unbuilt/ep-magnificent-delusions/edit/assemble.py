"""Assemble UNBUILT "Magnificent Delusions" from rendered assets.

Usage: python3 assemble.py <asset_dir> <out.mp4>
asset_dir must contain:
  audio/t_<n>.wav      tightened voice takes (n = TTS line index, CO1 = cold-open proof line)
  vid/sync_<ID>.mp4    Seedance host shots
  vid/br_<ID>.mp4      Kling b-roll
  img/<ID>.png         stills
Each beat renders to an intermediate clip (picture + voice), then all beats are concatenated.
"""
import json
import os
import re
import subprocess
import sys
import wave

from PIL import Image, ImageDraw, ImageFont

FF = os.environ.get("FFMPEG", "ffmpeg")
W, H, FPS = 1280, 720, 24
PAD = 0.35          # breath after each line
SECTION_PAD = 0.9   # longer breath at section changes

A = sys.argv[1]
OUT = sys.argv[2]
TMP = os.path.join(A, "build")
os.makedirs(TMP, exist_ok=True)

FONT = "/usr/share/fonts/truetype/liberation/"
SANS_B = ImageFont.truetype(FONT + "LiberationSans-Bold.ttf", 30)
SANS = ImageFont.truetype(FONT + "LiberationSans-Regular.ttf", 20)
SERIF_I = ImageFont.truetype(FONT + "LiberationSerif-Italic.ttf", 44)
BIG = ImageFont.truetype(FONT + "LiberationSans-Bold.ttf", 96)
RED = (229, 9, 20, 255)


def wav_len(p):
    w = wave.open(p)
    return w.getnframes() / w.getframerate()


def run(cmd):
    subprocess.run([FF, "-nostdin", "-loglevel", "error", "-y"] + cmd, check=True)


def spaced(draw, xy, text, font, fill, gap):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + gap
    return x


def card_png(name, number, title, place):
    """Section card: red rule, 'No. 5' letterspaced, title, place line; lower left."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    grad = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for i in range(260):
        gd.line([(0, i), (W, i)], fill=(0, 0, 0, int(150 * i / 260)))
    im.alpha_composite(grad, (0, H - 260))
    d.rectangle([64, H - 190, 67, H - 70], fill=RED)
    spaced(d, (84, H - 192), number.upper(), SANS_B, (255, 255, 255, 255), 6)
    d.text((84, H - 150), title, font=SERIF_I, fill=(255, 255, 255, 255))
    spaced(d, (86, H - 94), place.upper(), SANS, (215, 215, 215, 255), 4)
    p = os.path.join(TMP, name)
    im.save(p)
    return p


def lower_third_png(name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([60, H - 128, 63, H - 64], fill=RED)
    spaced(d, (78, H - 130), "HUGO ASHBY", SANS_B, (255, 255, 255, 255), 5)
    d.text((79, H - 90), "UNBUILT  ·  Place de la Bastille, Paris", font=SANS, fill=(222, 222, 222, 255))
    p = os.path.join(TMP, name)
    im.save(p)
    return p


def title_png(name, top, sub):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    tw = sum(d.textlength(c, font=BIG) + 22 for c in top) - 22
    spaced(d, ((W - tw) / 2, H / 2 - 90), top, BIG, (255, 255, 255, 255), 22)
    d.rectangle([W / 2 - 40, H / 2 + 28, W / 2 + 40, H / 2 + 31], fill=RED)
    if sub:
        sw = d.textlength(sub, font=SERIF_I)
        d.text(((W - sw) / 2, H / 2 + 46), sub, font=SERIF_I, fill=(230, 230, 230, 255))
    p = os.path.join(TMP, name)
    im.save(p)
    return p


def visual_filter(kind, key, dur, idx):
    """Return (input args, filter chain producing [v{idx}] of exactly dur seconds)."""
    if kind == "still":
        src = os.path.join(A, "img", f"{key}.png")
        frames = int(round(dur * FPS)) + 1
        # slow push-in, alternating direction for variety
        z = "min(zoom+0.0006,1.10)" if idx % 2 == 0 else "if(eq(on,0),1.10,max(zoom-0.0006,1.0))"
        chain = (f"[{idx}:v]scale=2560:-2,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                 f"d={frames}:s={W}x{H}:fps={FPS},trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{idx}]")
        return ["-loop", "1", "-t", f"{dur + 1:.3f}", "-i", src], chain
    src = os.path.join(A, "vid", f"{'sync' if kind == 'sync' else 'br'}_{key}.mp4")
    chain = (f"[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
             f"tpad=stop_mode=clone:stop_duration=30,trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{idx}]")
    return ["-i", src], chain


BEATS = []
_n = [0]


def beat(visuals, audio=None, overlay=None, hold=None, pad=PAD, fade_in=False, fade_out=False):
    """visuals: list of (kind, key[, weight]); audio: TTS key; hold: fixed duration with no audio."""
    BEATS.append(dict(visuals=visuals, audio=audio, overlay=overlay, hold=hold, pad=pad,
                      fade_in=fade_in, fade_out=fade_out))


def render_beat(i, b):
    if b["audio"] is not None:
        apath = os.path.join(A, "audio", f"t_{b['audio']}.wav")
        v0 = b["visuals"][0]
        aligned = os.path.join(A, "audio", f"t_s_{v0[1]}.wav")
        if v0[0] == "sync" and os.path.exists(aligned):
            apath = aligned  # clean take re-timed to the rendered lips (align.py)
        dur = wav_len(apath) + b["pad"]
    else:
        apath, dur = None, b["hold"]
    vis = b["visuals"]
    weights = [v[2] if len(v) > 2 else 1.0 for v in vis]
    tot = sum(weights)
    parts = [dur * w / tot for w in weights]
    inputs, chains = [], []
    for j, (v, pdur) in enumerate(zip(vis, parts)):
        ia, ch = visual_filter(v[0], v[1], pdur, j)
        inputs += ia
        chains.append(ch)
    n = len(vis)
    chains.append("".join(f"[v{j}]" for j in range(n)) + f"concat=n={n}:v=1:a=0,format=yuv420p[vc]")
    last = "vc"
    k = n
    if b["overlay"]:
        png, t0, t1 = b["overlay"]
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        chains.append(f"[{k}:v]format=rgba,fade=t=in:st={t0}:d=0.5:alpha=1,fade=t=out:st={t1}:d=0.5:alpha=1[ov]")
        chains.append(f"[{last}][ov]overlay=0:0:shortest=1[vo]")
        last = "vo"
        k += 1
    if b["fade_in"] or b["fade_out"]:
        f = []
        if b["fade_in"]:
            f.append("fade=t=in:st=0:d=0.6")
        if b["fade_out"]:
            f.append(f"fade=t=out:st={max(dur - 0.8, 0):.3f}:d=0.8")
        chains.append(f"[{last}]{','.join(f)}[vf]")
        last = "vf"
    if apath:
        inputs += ["-i", apath]
        chains.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={dur:.3f}[a]")
    else:
        chains.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={dur:.3f}[a]")
    out = os.path.join(TMP, f"beat_{i:03d}.mp4")
    run(inputs + ["-filter_complex", ";".join(chains), "-map", f"[{last}]", "-map", "[a]",
                  "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                  "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", out])
    return out, dur


# ------------------------------------------------------------------ EDIT DECISION LIST
LT = lower_third_png("lt.png")
C5 = card_png("c5.png", "No. 5", "The Elephant of the Bastille", "Paris · 1808")
C4 = card_png("c4.png", "No. 4", "Beach Pneumatic Transit", "New York · 1870")
C3 = card_png("c3.png", "No. 3", "The Cathedral of Christ the King", "Liverpool · 1933")
C2 = card_png("c2.png", "No. 2", "Dome over Manhattan", "New York · 1960")
C1 = card_png("c1.png", "No. 1", "Atlantropa", "The Mediterranean · 1928")
TITLE = title_png("title.png", "UNBUILT", "Magnificent Delusions")
END = title_png("end.png", "UNBUILT", "")
HON = title_png("hon.png", "", "Honourable mention")

# Cold open
beat([("sync", "CO1")], "CO1", overlay=(LT, 0.6, 3.9), fade_in=True)
beat([("br", "CO2")], 0)
beat([("br", "CO3")], 1)
beat([("still", "CO4")], 2)
beat([("br", "CO5")], 3)
beat([("br", "CO6")], 4)
beat([("sync", "CO7")], 5, pad=0.8)
beat([("still", "TITLE_BG")], hold=4.0, fade_in=True, fade_out=True)
# No. 5
beat([("sync", "E1")], 6, overlay=(C5, 0.3, 4.2))
beat([("still", "E2")], 7)
beat([("br", "E3")], 8)
beat([("br", "E4", 1.0), ("still", "E4b", 1.0)], 9)
beat([("still", "E5")], 11)
beat([("br", "E6")], 12)
beat([("still", "E6b")], 13)
beat([("still", "E7v")], 14)
beat([("sync", "E7")], 15, pad=SECTION_PAD)
# No. 4
beat([("br", "B1")], 16, overlay=(C4, 0.3, 4.0))
beat([("still", "B2v")], 17)
beat([("sync", "B2")], 18)
beat([("br", "B3")], 19)
beat([("br", "B4", 1.2), ("still", "B4b", 1.0)], 20)
beat([("br", "B5")], 22)
beat([("still", "B6")], 23)
beat([("still", "B7")], 24)
beat([("still", "B8a")], 25)
beat([("br", "B8")], 26)
beat([("still", "B9v")], 27)
beat([("sync", "B9")], 28, pad=SECTION_PAD)
# No. 3
beat([("still", "L1v")], 29, overlay=(C3, 0.3, 3.6))
beat([("sync", "L1")], 30)
beat([("still", "L2", 1.3), ("still", "CO4", 1.0)], 31)
beat([("br", "L3")], 32)
beat([("still", "L4")], 33)
beat([("br", "L5")], 34)
beat([("sync", "L6")], 35)
beat([("br", "L7")], 36, pad=SECTION_PAD)
# No. 2
beat([("still", "D1v")], 37, overlay=(C2, 0.3, 3.6))
beat([("sync", "D1")], 38)
beat([("br", "D2")], 39)
beat([("still", "D3")], 40)
beat([("br", "D4")], 41)
beat([("sync", "D5")], 42)
beat([("still", "D6")], 43)
beat([("br", "D7")], 44, pad=SECTION_PAD)
# No. 1
beat([("still", "A1v")], 45, overlay=(C1, 0.3, 4.2), pad=0.15)
beat([("sync", "A1")], 46)
beat([("still", "A2")], 47)
beat([("br", "A3")], 48)
beat([("still", "A3b")], 49)
beat([("still", "A4")], 50)
beat([("still", "A5")], 51)
beat([("br", "A6")], 52)
beat([("still", "A7")], 53)
beat([("still", "A8v")], 54)
beat([("sync", "A8")], 55, pad=SECTION_PAD)
# Outro
beat([("br", "L5", 1.0), ("still", "B9v", 1.0), ("still", "E7v", 1.0)], 56)
beat([("sync", "O1")], 57)
beat([("sync", "O2")], 58, pad=0.8)
beat([("still", "END_BG")], hold=3.0, fade_in=True, fade_out=True)
beat([("still", "HON_BG")], hold=1.6, fade_in=True)
beat([("still", "X1")], 59, pad=1.2, fade_out=True)

# title/end backgrounds are the rendered title cards
for key, png in (("TITLE_BG", TITLE), ("END_BG", END), ("HON_BG", HON)):
    Image.open(png).convert("RGB").save(os.path.join(A, "img", f"{key}.png"))

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    outs, total = [], 0.0
    for i, b in enumerate(BEATS):
        if only and str(i) not in only.split(","):
            outs.append(os.path.join(TMP, f"beat_{i:03d}.mp4"))
            continue
        o, d = render_beat(i, b)
        outs.append(o)
        total += d
        print(f"beat {i:02d} {d:5.2f}s", flush=True)
    # Audio is rebuilt sample-accurately: stream-copying per-beat AAC keeps each segment's encoder
    # priming, and the voice drifts ~1.6s late over 62 beats.
    starts, pcm, frames = [0.0], [], []
    for o in outs:
        err = subprocess.run([FF, "-nostdin", "-i", o, "-map", "0:v", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        n = int(re.findall(r"frame=\s*(\d+)", err)[-1])
        samples = round(n / FPS * 48000)
        raw = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-i", o, "-map", "0:a", "-ac", "2", "-ar", "48000",
                              "-f", "s16le", "-"], capture_output=True, check=True).stdout
        pcm.append(raw[:samples * 4].ljust(samples * 4, b"\0"))
        frames.append(n)
        starts.append(starts[-1] + n / FPS)
    # pin each entry to its frame duration, or the demuxer offsets by the (longer) audio and the picture drifts
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(o)}'\nduration {n / FPS:.6f}\n" for o, n in zip(outs, frames))
    vid = os.path.join(TMP, "video_only.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst, "-an", "-c", "copy", vid])
    voice = os.path.join(TMP, "voice.wav")
    w = wave.open(voice, "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes(b"".join(pcm))
    w.close()
    run(["-i", vid, "-i", voice, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", OUT])
    with open(os.path.join(TMP, "timeline.json"), "w") as f:
        json.dump({"starts": starts}, f)  # beat start times in the cut, read by score.py
    total = starts[-1]
    print("TOTAL", round(total, 1), "s ->", OUT)
