"""Assemble UNBUILT "Monuments to the Dead" from rendered assets.

Usage: python3 assemble.py <asset_dir> <out.mp4>
asset_dir must contain:
  audio/t_<KEY>.wav     tightened voice takes, keyed like the script ([CO2], [W3], [Y9v] ...)
  audio/t_s_<ID>.wav    the sync shot's own lip-synced voice, word-patched by sync_audio.py
  vid/sync_<ID>.mp4     Seedance host shots
  vid/br_<ID>.mp4       Kling b-roll
  img/<ID>.png          stills
Unlike episode 1, the edit list is not typed out by hand: it is read from ../shotlist.json. Consecutive
shots that share a voice line become one beat that splits the line between them; cards named
"(overlay on X ...)" are laid over shot X; CO8 and END are full-frame cards.
Each beat renders to an intermediate clip (picture + voice), then all beats are concatenated.
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
W, H, FPS = 1280, 720, 24
PAD = 0.35          # breath after each line
SECTION_PAD = 0.9   # longer breath at section changes
MAX_STRETCH = 1.6   # never slow b-roll more than this

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = json.load(open(os.path.join(HERE, "..", "shotlist.json")))["shots"]
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

# per-shot picture fixes: extra zoom to crop off an artefact (P5a's start frame carried a burned-in timecode)
ZOOM = {"P5a": 1.16}
# re-uses: (source kind, source key, start offset in the source clip, extra grade)
WARM = "colorbalance=rs=.06:gs=.02:bs=-.06"
DUSK = "colorbalance=rs=.04:bs=.06,eq=brightness=-0.03"
REUSE = {"W7v": ("still", "W6b", 0.0, ""), "P2a": ("br", "CO4", 0.0, WARM),
         "P6v": ("br", "CO4", 2.0, DUSK), "Y9v": ("br", "CO6", 0.0, "")}


def wav_len(p):
    w = wave.open(p)
    return w.getnframes() / w.getframerate()


_clip_len = {}


def clip_len(p):
    """Length of a video stream in seconds (frames / fps), cached."""
    if p not in _clip_len:
        err = subprocess.run([FF, "-nostdin", "-i", p, "-map", "0:v", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        n = int(re.findall(r"frame=\s*(\d+)", err)[-1])
        fps = float(re.search(r"(\d+(?:\.\d+)?) fps", err).group(1))
        _clip_len[p] = n / fps
    return _clip_len[p]


_bars = {}


def bar_zoom(src, is_video):
    """Zoom that crops off black bars baked into a picture (some start frames came back pillarboxed and
    Kling keeps the bars). A bar is a run of edge columns/rows that are pure black with no grain."""
    if src not in _bars:
        if is_video:
            raw = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-ss", "1", "-i", src, "-frames:v", "1",
                                  "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
            w, h = map(int, re.search(r", (\d+)x(\d+)", subprocess.run(
                [FF, "-nostdin", "-i", src], capture_output=True, text=True).stderr).groups())
            g = np.frombuffer(raw, dtype=np.uint8).reshape(h, w).astype(float)
        else:
            g = np.asarray(Image.open(src).convert("L"), dtype=float)
            h, w = g.shape

        def run_len(lines):
            n = 0
            for line in lines:
                if line.mean() > 6 or line.std() > 3:
                    break
                n += 1
            return n
        # real letterbox/pillarbox bars come in pairs; one dark edge is just a dark picture
        side = min(run_len(g.T), run_len(g.T[::-1])) / w
        top = min(run_len(g), run_len(g[::-1])) / h
        f = max(side, top)
        _bars[src] = 1.0 if f < 0.004 else 1.0 / (1 - 2 * f - 0.006)
    return _bars[src]


def sync_start(key):
    side = os.path.join(A, "audio", f"t_s_{key}.json")
    return json.load(open(side))["start"] if os.path.exists(side) else 0.0


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


def lower_third_png(name, line):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([60, H - 128, 63, H - 64], fill=RED)
    spaced(d, (78, H - 130), "HUGO ASHBY", SANS_B, (255, 255, 255, 255), 5)
    d.text((79, H - 90), line, font=SANS, fill=(222, 222, 222, 255))
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
    # full-frame cards play as stills
    Image.open(p).convert("RGB").save(os.path.join(A, "img", name.replace(".png", "_BG.png")))
    return name.replace(".png", "_BG")


def visual_filter(v, dur, idx):
    """v = dict(kind, key, start, grade, zoom). Returns (input args, chain producing [v{idx}] of dur seconds)."""
    kind, key = v["kind"], v["key"]
    grade = f",{v['grade']}" if v.get("grade") else ""
    if kind == "still":
        src = os.path.join(A, "img", f"{key}.png")
        frames = int(round(dur * FPS)) + 1
        bz = 1.0 if key.endswith("_BG") else bar_zoom(src, False)
        # drop any bars, then trim to exactly 16:9 so the push-in never stretches the picture
        unbar = (f"crop='min(iw/{bz:.4f},ih/{bz:.4f}*16/9)':'min(ih/{bz:.4f},iw/{bz:.4f}*9/16)',")
        # slow push-in (alternating with a pull-out) spread over the whole shot, so the picture keeps
        # moving until the cut
        span = 0.10 + 0.01 * max(0.0, dur - 8.0)
        z = (f"1+{span:.3f}*on/{frames}" if idx % 2 == 0 else f"1+{span:.3f}-{span:.3f}*on/{frames}")
        chain = (f"[{idx}:v]{unbar}scale=2560:1440,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                 f"d={frames}:s={W}x{H}:fps={FPS},setsar=1{grade},trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{idx}]")
        return ["-loop", "1", "-t", f"{dur + 1:.3f}", "-i", src], chain
    src = os.path.join(A, "vid", f"{'sync' if kind == 'sync' else 'br'}_{key}.mp4")
    ss = sync_start(key) if kind == "sync" else v.get("start", 0.0)
    zoom = max(v.get("zoom", 1.0), bar_zoom(src, True) if kind == "br" else 1.0)
    zw, zh = int(W * zoom) // 2 * 2, int(H * zoom) // 2 * 2
    retime = ""
    avail = clip_len(src) - ss
    if kind == "br" and dur > avail + 0.04:
        # the narration outlasts the clip: slow it down to fill the slot (motion-interpolated), capped
        f = min(dur / avail, MAX_STRETCH)
        if dur / avail > MAX_STRETCH:
            print(f"  ! {key}: needs {dur / avail:.2f}x, capped at {MAX_STRETCH}x (last frame holds)", flush=True)
        retime = (f"setpts=(PTS-STARTPTS)*{f:.4f},"
                  f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,")
    chain = (f"[{idx}:v]trim=start={ss:.3f},setpts=PTS-STARTPTS,scale={zw}:{zh}:force_original_aspect_ratio=increase,"
             f"crop={W}:{H},setsar=1,{retime}fps={FPS}{grade},"
             f"tpad=stop_mode=clone:stop_duration=30,trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{idx}]")
    return ["-i", src], chain


def render_beat(i, b):
    if b["audio"] is not None:
        apath = os.path.join(A, "audio", f"t_{b['audio']}.wav")
        v0 = b["visuals"][0]
        aligned = os.path.join(A, "audio", f"t_s_{v0['key']}.wav")
        if v0["kind"] == "sync" and os.path.exists(aligned):
            apath = aligned  # the clip's own lip-synced voice, word-patched (sync_audio.py)
        dur = wav_len(apath) + b["pad"]
        if v0["kind"] == "sync":
            # end the beat with the clip, not on a frozen frame after he stops talking
            room = clip_len(os.path.join(A, "vid", f"sync_{v0['key']}.mp4")) - sync_start(v0["key"])
            dur = min(dur, max(room, wav_len(apath) + 0.1))
    else:
        apath, dur = None, b["hold"]
    vis = b["visuals"]
    tot = sum(v.get("weight", 1.0) for v in vis)
    inputs, chains = [], []
    for j, v in enumerate(vis):
        ia, ch = visual_filter(v, dur * v.get("weight", 1.0) / tot, j)
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


# ------------------------------------------------------------------ EDIT DECISION LIST (from the shot list)
def build_edl():
    beats = []
    overlays = {}
    for s in SHOTS:  # section cards: "No. 5 · Title · Place · Year (overlay on W1, 0.3–4.0 s)"
        m = re.match(r"(No\. \d) · (.+?) · (.+) \(overlay on (\w+), ([\d.]+)–([\d.]+) s\)", s.get("text", ""))
        if s["kind"] == "CARD" and m:
            num, title, place, on, t0, t1 = m.groups()
            overlays[on] = (card_png(f"card_{on}.png", num, title, place), float(t0), float(t1))
    overlays["CO1"] = (lower_third_png("lt.png", "UNBUILT  ·  A Halloween special"), 0.6, 4.2)

    def new(visuals, audio=None, overlay=None, hold=None, pad=PAD, fade_in=False, fade_out=False, segment=None):
        beats.append(dict(visuals=visuals, audio=audio, overlay=overlay, hold=hold, pad=pad,
                          fade_in=fade_in, fade_out=fade_out, segment=segment))

    for s in SHOTS:
        sid, kind = s["id"], s["kind"]
        if kind == "SYNC":
            new([dict(kind="sync", key=sid)], sid, overlay=overlays.get(sid), segment=s["segment"],
                fade_in=(sid == "CO1"))
        elif kind == "CARD" and sid == "CO8":
            new([dict(kind="still", key=title_png("title.png", "UNBUILT", "Monuments to the Dead"))],
                hold=4.0, fade_in=True, fade_out=True, segment=s["segment"])
        elif kind == "CARD" and sid == "END":
            new([dict(kind="still", key=title_png("end.png", "UNBUILT", ""))], hold=3.0, fade_in=True,
                fade_out=True, segment=s["segment"])
            new([dict(kind="still", key=title_png("hon.png", "", "Honourable mention"))], hold=1.6,
                fade_in=True, segment="Stinger")
        elif kind in ("STILL", "BROLL_VIDEO", "REUSE"):
            if kind == "REUSE":
                k2, src, start, grade = REUSE[sid]
                v = dict(kind=k2, key=src, start=start, grade=grade)
            else:
                v = dict(kind="still" if kind == "STILL" else "br", key=sid, zoom=ZOOM.get(sid, 1.0))
            b = beats[-1] if beats else None
            if b and b["audio"] == s["vo_id"] and b["visuals"][0]["kind"] != "sync":
                b["visuals"].append(v)  # same line: split it with the previous shot
            else:
                new([v], s["vo_id"], segment=s["segment"])
    # a longer breath before each new countdown entry, and fades on the stinger
    for a, b in zip(beats, beats[1:]):
        if a["segment"] != b["segment"] and a["hold"] is None:
            a["pad"] = SECTION_PAD
    beats[-1].update(pad=1.2, fade_out=True)
    return beats


BEATS = build_edl()

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    if os.environ.get("LIST"):
        for i, b in enumerate(BEATS):
            print(i, b["segment"], b["audio"], [v["key"] for v in b["visuals"]], "ovl" if b["overlay"] else "")
        sys.exit()
    outs = []
    for i, b in enumerate(BEATS):
        if only and str(i) not in only.split(","):
            outs.append(os.path.join(TMP, f"beat_{i:03d}.mp4"))
            continue
        o, d = render_beat(i, b)
        outs.append(o)
        print(f"beat {i:02d} {d:5.2f}s  {b['audio'] or ''}", flush=True)
    # Audio is rebuilt sample-accurately: stream-copying per-beat AAC keeps each segment's encoder
    # priming, and the voice drifts late over many beats.
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
    with open(os.path.join(TMP, "timeline.json"), "w") as f:  # read by score.py
        json.dump({"starts": starts, "segments": [b["segment"] for b in BEATS],
                   "holds": [b["hold"] for b in BEATS]}, f)
    print("TOTAL", round(starts[-1], 1), "s ->", OUT)
