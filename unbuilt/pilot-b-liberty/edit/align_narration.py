"""Find each script block in the owner's recording when the pauses alone can't (short pauses, retakes).

Speech recognition (faster-whisper, run locally) is used only to locate words in time; nothing it produces
goes into the video. The recording is matched word-by-word against SCRIPT.md. Where a block was read more
than once ("retake of number six"), everything from its first take up to its last take is ignored, so the
last take wins. Block edges are then moved to the nearest quiet point in the audio.

Usage: python3 align_narration.py <recording> [--trim B5="about two hundred"]
  --trim BLOCK="first words"  start BLOCK at these words instead (e.g. to drop a misread opening)
Writes build/words.json (cached), build/segments.json (one [start, end] per block, script order) and prints
a check table. Then: python3 split_narration.py <recording> --segments build/segments.json
"""
import argparse
import difflib
import json
import os
import re
import sys

import numpy as np

from blocks import blocks
from split_narration import BUILD, SR, load



NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}


def norm(text):
    text = text.lower().replace("’", "'")
    return [w for w in re.sub(r"[^a-z0-9' ]+", " ", text).split() if w]


def transcribe(path):
    cache = os.path.join(BUILD, "words.json")
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(path):
        return json.load(open(cache))
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, word_timestamps=True, beam_size=5)
    words = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
    json.dump(words, open(cache, "w"))
    return words


def snap(env, t, direction, limit=0.5, quiet_db=-42.0):
    """Move t outward (direction -1 = earlier, +1 = later) until the audio has been quiet for 60 ms."""
    hop = 0.01
    i = int(t / hop)
    for k in range(int(limit / hop)):
        j = i + direction * k
        win = env[max(0, j - 3):j + 3]
        if len(win) and win.max() < quiet_db:
            return j * hop
    return t + direction * 0.05


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--trim", nargs="*", default=[])
    ap.add_argument("--set", nargs="*", default=[], help="override a block by hand: S1=462.26:476.62 (seconds)")
    a = ap.parse_args()
    sets = {k: [float(x) for x in v.split(":")] for k, v in (x.split("=", 1) for x in a.set)}
    os.makedirs(BUILD, exist_ok=True)
    trims = {k: norm(v) for k, v in (x.split("=", 1) for x in a.trim)}

    words = transcribe(a.recording)
    tw = []                                          # (start, end, normalised word)
    for s, e, w in words:
        for n in norm(w):
            tw.append((s, e, n))
    toks = [t[2] for t in tw]

    script = blocks()
    # ignore abandoned takes. The narrator calls each one ("retake of number six", "I'm going to do number 33
    # again"); the new take starts right after the call, and the abandoned one is the last time its opening
    # words were said before the call. Skip from there up to the new take.
    skip = np.zeros(len(tw), bool)
    for m in [i for i, t in enumerate(toks) if t == "retake" or (t == "again" and "do" in toks[max(0, i - 6):i])]:
        j = m + 1                                    # step over "of number six" / "again" to the new take
        while j < len(toks) and toks[j] in ("of", "number", "again"):
            j += 1
        if toks[m] == "retake" and j < len(toks) and (toks[j].isdigit() or toks[j] in NUMBER_WORDS):
            j += 1                                   # exactly one number: the take itself may start "One man..."
        head = toks[j:j + 3]
        prev = [i for i in range(m - 1, -1, -1) if toks[i:i + 3] == head]
        if prev:
            skip[prev[0]:j] = True
            print(f"retake at {tw[m][0]:.1f} s: dropping {tw[prev[0]][0]:.1f}-{tw[j][0]:.1f} s")
        else:
            skip[max(0, m - 8):j] = True
            print(f"retake at {tw[m][0]:.1f} s: earlier take not found, dropping only the call  <-- check")
    keep = [i for i in range(len(tw)) if not skip[i]]

    sw, owner = [], []                               # script words and the block each belongs to
    for b, (name, text) in enumerate(script):
        for w in norm(text):
            sw.append(w)
            owner.append(b)
    ktoks = [toks[i] for i in keep]
    sm = difflib.SequenceMatcher(None, sw, ktoks, autojunk=False)
    first, last, matched = {}, {}, {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            b, ti = owner[blk.a + k], keep[blk.b + k]
            first.setdefault(b, ti)
            last[b] = ti
            matched[b] = matched.get(b, 0) + 1

    for name, head in trims.items():                 # start a block later, at the given words
        b = [n for n, _ in script].index(name)
        hits = [i for i in range(first[b], last[b]) if toks[i:i + len(head)] == head]
        if not hits:
            sys.exit(f"--trim {name}: words not found in that block")
        first[b] = hits[0]

    # a block can end on words written differently by the recogniser ("38" for "thirty-eight"): carry its end
    # over any following words that run straight on (gap under 0.6 s) and don't open the next block
    starts = sorted(first.values())
    for b in list(last):
        nxt = min([i for i in starts if i > last[b]], default=len(tw))
        i = last[b] + 1
        while i < nxt and not skip[i] and tw[i][0] - tw[i - 1][1] < 0.6:
            last[b] = i
            i += 1

    audio = load(a.recording)
    hop = int(0.01 * SR)
    frames = audio[:len(audio) // hop * hop].reshape(-1, hop)
    env = 20 * np.log10(np.sqrt((frames ** 2).mean(1)) + 1e-9)

    segs = []
    print(f"\n{'block':6} {'start':>7} {'end':>7}  match  words")
    for b, (name, text) in enumerate(script):
        if b not in first:
            sys.exit(f"{name}: not found in the recording")
        s = snap(env, tw[first[b]][0], -1)
        e = snap(env, tw[last[b]][1], +1)
        if name in sets:                             # the recogniser lost words here; edges set from the audio
            s, e = sets[name]
        elif segs and s < segs[-1][1]:                 # two blocks read without a pause: cut between the words
            mid = (tw[last[b - 1]][1] + tw[first[b]][0]) / 2
            segs[-1][1], s = mid - 0.13, mid + 0.13
        segs.append([round(s, 2), round(e, 2)])
        n = len(norm(text))
        said = " ".join(toks[first[b]:last[b] + 1])
        flag = "" if matched[b] >= 0.85 * n else "  <-- check"
        print(f"{name:6} {s:7.2f} {e:7.2f}  {matched[b]:3}/{n:<3} {said[:70]}{flag}")
    json.dump(segs, open(os.path.join(BUILD, "segments.json"), "w"), indent=1)
    print("\nWrote build/segments.json")


if __name__ == "__main__":
    main()
