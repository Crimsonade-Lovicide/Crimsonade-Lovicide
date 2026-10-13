"""Split the owner's recording into script blocks at the pauses, then rebuild a tight voice track.

No transcription and no AI: blocks are found by measuring silence (ffmpeg silencedetect). The owner leaves
a pause of about two seconds after each block, so the Nth stretch of speech is the Nth block in SCRIPT.md.

Usage: python3 split_narration.py <recording> [--noise -38] [--min-gap 1.2] [--drop D9] [--takes D4=2 B3=2]
Writes build/voice.wav (48 kHz mono, pauses tightened) and build/timings.json ({block: [start, end]}).
If the number of speech stretches doesn't match the number of blocks, it prints every stretch and stops,
so the mismatch can be fixed by hand (re-record a block, or edit build/segments.json and re-run with --segments).
A segments.json entry can also be [start, end, "pickup.m4a", gain_dB]: a line re-recorded later, in the same folder.
"""
import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from unbuilt_kit.core import ffmpeg_exe  # noqa: E402

from blocks import blocks  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 48000
PAD = 0.12             # silence kept either side of each block's speech
GAP = 0.45             # pause between blocks in the tight track
SECTION_GAP = 0.9      # longer pause where a new script section starts
TITLE_HOLD = 2.5       # room for the title card (C4) after C3


def load(path):
    raw = subprocess.run([ffmpeg_exe(), "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def speech_spans(path, noise, min_gap):
    log = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path, "-af",
                          f"silencedetect=noise={noise}dB:d={min_gap}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = len(load(path)) / SR
    edges, t = [], 0.0
    for s, e in zip(starts, ends + [total] * (len(starts) - len(ends))):
        if s - t > 0.3:
            edges.append([t, s])
        t = e
    if total - t > 0.3:
        edges.append([t, total])
    return edges


def section(block):
    return block[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--noise", type=float, default=-38)
    ap.add_argument("--min-gap", type=float, default=1.2)
    ap.add_argument("--drop", nargs="*", default=[], help="blocks recorded but cut from the edit, e.g. D9")
    ap.add_argument("--segments", help="use a hand-corrected segments.json instead of detecting")
    ap.add_argument("--takes", nargs="*", default=[], help="blocks read more than once, e.g. D4=2; the last take is used")
    a = ap.parse_args()
    os.makedirs(BUILD, exist_ok=True)

    takes = {k: int(v) for k, v in (x.split("=") for x in a.takes)}
    names = [b for b, _ in blocks()]
    expected = [b for b in names for _ in range(takes.get(b, 1))]
    spans = json.load(open(a.segments)) if a.segments else speech_spans(a.recording, a.noise, a.min_gap)
    json.dump(spans, open(os.path.join(BUILD, "segments.json"), "w"), indent=1)
    if len(spans) != len(expected):
        print(f"Found {len(spans)} stretches of speech but expected {len(expected)} ({len(names)} blocks plus retakes).")
        for i, (s, e) in enumerate(spans):
            print(f"  {i + 1:2}  {s:7.2f}-{e:7.2f}  ({e - s:5.2f} s)   expected: {expected[i] if i < len(expected) else '-'}")
        print("Fix: adjust --noise/--min-gap, or edit build/segments.json and re-run with --segments.")
        sys.exit(1)

    sources = {None: load(a.recording)}
    out, timings, t, prev = [], {}, 0.0, None
    last = {}
    for name, span in zip(expected, spans):
        last[name] = span                 # a later take replaces an earlier one
    for name in names:
        # a span is [start, end], or [start, end, "pickup.m4a", gain_dB] for a line re-recorded separately
        s, e = last[name][:2]
        src = last[name][2] if len(last[name]) > 2 else None
        if src not in sources:
            sources[src] = load(os.path.join(os.path.dirname(os.path.abspath(a.recording)), src))
        audio = sources[src] * (10 ** ((last[name][3] if len(last[name]) > 3 else 0) / 20))
        if name in a.drop:
            continue
        if prev is not None:
            gap = TITLE_HOLD if prev == "C3" else SECTION_GAP if section(name) != section(prev) else GAP
            out.append(np.zeros(int(gap * SR), np.float32))
            t += gap
        clip = audio[max(0, int((s - PAD) * SR)):int((e + PAD) * SR)]
        timings[name] = [round(t + PAD, 3), round(t + len(clip) / SR - PAD, 3)]
        out.append(clip)
        t += len(clip) / SR
        prev = name
    voice = np.concatenate(out)
    subprocess.run([ffmpeg_exe(), "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    os.path.join(BUILD, "voice.wav")], input=voice.tobytes(), check=True)
    json.dump(timings, open(os.path.join(BUILD, "timings.json"), "w"), indent=1)
    print(f"{len(timings)} blocks, {t / 60:.1f} min. Wrote build/voice.wav and build/timings.json")


if __name__ == "__main__":
    main()
