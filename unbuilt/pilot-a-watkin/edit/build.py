"""Build Pilot A: render every shot at its block's length, then cut picture to the owner's voice.

  python3 build.py                      # needs build/voice.wav + build/timings.json (from split_narration.py)
  python3 build.py --estimate           # no recording yet: time blocks at 2.5 words/s, silent, for a picture check
  python3 build.py --music track.wav    # add the music bed (ducked under the voice)
  python3 build.py --only C1 D3         # re-render just these shots

Clips are cached in build/clips/ and only re-rendered when their spec or length changes.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "toolkit"))
import unbuilt_kit as kit  # noqa: E402

from blocks import blocks  # noqa: E402
from shots import SHOTS  # noqa: E402

BUILD = os.path.join(HERE, "build")
CLIPS = os.path.join(BUILD, "clips")
RAW = os.path.join(HERE, "..", "assets", "raw")
DERIVED = os.path.join(HERE, "..", "assets", "derived")   # rotated/cropped copies (assets/derive.py)
GEO = os.path.join(HERE, "..", "assets", "geo", "land.geojson")
FOOTAGE = os.path.join(HERE, "..", "assets", "footage")   # Google Earth Studio renders (zips of JPEG frames)
LEAD = 0.25          # picture changes this long before its block's first word
TAIL = 1.0           # hold after the last word
WPS = 2.5            # words per second for --estimate


def asset(ref):
    hits = []
    for d in (DERIVED, RAW):                 # a corrected copy wins over the raw download
        hits = sorted(glob.glob(os.path.join(d, ref + "_*")) + glob.glob(os.path.join(d, ref + ".*")))
        if hits:
            break
    hits = [h for h in hits if h.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))]
    if not hits:
        raise FileNotFoundError(f"no asset file for {ref} in assets/raw/")
    return hits[0]


def estimated_timings():
    t, out, prev = 0.0, {}, None
    for name, text in blocks():
        if prev:
            t += 2.5 if prev == "C4" else 0.9 if name[0] != prev[0] else 0.45
        d = len(re.findall(r"[A-Za-z0-9'’-]+", text)) / WPS
        out[name] = [round(t, 3), round(t + d, 3)]
        t += d
        prev = name
    return out


def windows(timings):
    """Picture window [start, end) for every shot, covering the programme without gaps."""
    names = list(timings)
    win = {}
    for i, n in enumerate(names):
        s = max(0.0, timings[n][0] - LEAD) if i else 0.0
        e = timings[names[i + 1]][0] - LEAD if i + 1 < len(names) else timings[n][1] + TAIL
        win[n] = [s, e]
        if n == "C4":                       # the title card takes the pause after C4
            title_len = SHOTS["C5"][1]["fixed"]
            win["C5"] = [e - title_len, e]
            win[n][1] = e - title_len
    return dict(sorted(win.items(), key=lambda kv: kv[1][0]))


def footage_frames(source):
    """Frames for a Google Earth Studio render: unpack assets/footage/<source>.zip once, return sorted JPEGs."""
    folder = os.path.join(FOOTAGE, source)
    zipped = folder + ".zip"
    if not os.path.isdir(folder) and os.path.exists(zipped):
        import zipfile
        zipfile.ZipFile(zipped).extractall(folder)
    frames = sorted(glob.glob(os.path.join(folder, "**", "*.jp*g"), recursive=True))
    return frames


def footage(source, out, dur):
    """Turn the frame sequence into a clip of exactly `dur` seconds at 24 fps, fitted to 1920x1080.
    The whole camera move plays, re-timed to fit, when that changes its speed by no more than 1.5x either way.
    Beyond that it plays at natural speed and is cut at the end (too long) or holds its last frame (too short)."""
    frames = footage_frames(source)
    natural = len(frames) / 24
    factor = natural / dur
    per_frame = dur / len(frames) if 1 / 1.5 <= factor <= 1.5 else 1 / 24
    listfile = out + ".txt"
    with open(listfile, "w") as f:
        for fr in frames:
            f.write(f"file '{fr}'\nduration {per_frame:.6f}\n")
    kit.core.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", listfile, "-vf",
                         f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
                         f"fps=24,tpad=stop_mode=clone:stop_duration={dur:.3f},trim=duration={dur:.3f},setpts=PTS-STARTPTS",
                         "-an", "-r", "24", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out])
    os.remove(listfile)


def render(name, dur):
    fn, kw = SHOTS[name]
    kw = dict(kw)
    lt = kw.pop("lower_third", None)
    if fn == "footage":                          # use the Earth Studio render if it has arrived, else the stand-in
        if footage_frames(kw["source"]):
            kw = {"source": kw["source"], "n_frames": len(footage_frames(kw["source"]))}
        else:
            fn, kw = kw["fallback"]
            kw = dict(kw)
            lt = kw.pop("lower_third", lt)
    kw.pop("fixed", None)
    key = hashlib.sha1(json.dumps([fn, kw, lt, round(dur, 3)], sort_keys=True, default=str).encode()).hexdigest()[:10]
    out = os.path.join(CLIPS, f"{name}_{key}.mp4")
    if os.path.exists(out):
        return out
    for old in glob.glob(os.path.join(CLIPS, f"{name}_*.mp4")):
        os.remove(old)
    if "image" in kw:
        kw["image"] = asset(kw["image"])
    if "images" in kw:
        kw["images"] = [asset(r) for r in kw["images"]]
    base = out if not lt else out.replace(".mp4", "_base.mp4")
    if fn == "footage":
        footage(kw["source"], base, dur)
    elif fn in ("kenburns", "annotate", "highlight"):
        img = kw.pop("image")
        getattr(kit, fn)(img, base, dur, **kw)
    elif fn == "montage":
        imgs = kw.pop("images")
        kit.montage(imgs, base, dur, **kw)
    elif fn == "maproute":
        kit.maproute(GEO, base, dur, **kw)
    elif fn == "scale_compare":
        kit.scale_compare(base, dur, kw.pop("items"), **kw)
    elif fn == "timeline":
        kit.timeline(base, dur, kw.pop("events"), **kw)
    elif fn == "quote_card":
        kit.quote_card(base, dur, kw["quote"], kw["attribution"])
    elif fn == "title_card":
        kit.title_card(base, dur, kw["title"], kw.get("subtitle"))
    elif fn == "end_card":
        kit.end_card(base, dur, kw.get("text", "Sources in the description"))
    else:
        raise ValueError(fn)
    if lt:
        mov = out.replace(".mp4", "_lt.mov")
        kit.lower_third(mov, min(4.5, dur - 0.6), lt[0], lt[1])
        kit.overlay(base, mov, out, start=0.6)
        os.remove(base)
        os.remove(mov)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--music")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=os.path.join(BUILD, "pilot_a.mp4"))
    a = ap.parse_args()
    os.makedirs(CLIPS, exist_ok=True)
    tpath = os.path.join(BUILD, "timings.json")
    timings = estimated_timings() if a.estimate else json.load(open(tpath))
    win = windows(timings)
    shotlist = []
    for name, (s, e) in win.items():
        if a.only and name not in a.only:
            continue
        clip = render(name, e - s)
        print(f"{name:4} {s:7.2f}-{e:7.2f}  {os.path.basename(clip)}", flush=True)
        shotlist.append({"clip": clip, "start": s})
    if a.only:
        return
    voice = os.path.join(BUILD, "voice.wav")
    if a.estimate:                          # no recording yet: a silent track of the programme's length
        voice = os.path.join(BUILD, "silence.wav")
        total = list(win.values())[-1][1]
        kit.core.run_ffmpeg(["-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{total:.3f}", voice])
    json.dump(shotlist, open(os.path.join(BUILD, "shotlist.json"), "w"), indent=1)
    kit.assemble(shotlist, voice, a.music, a.out, crossfade=0.4)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
