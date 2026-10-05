"""Write YouTube captions (build/captions.srt) from the script, timed to the owner's voice.

The words on screen are the script's words (corrected where the delivery differs, see SPOKEN), so names,
numbers and spellings are exactly what was researched. Speech recognition is used only for timing: each
script word is matched to the recogniser's word times in build/voice.wav, and unmatched words are placed
by interpolation. Cues are at most two lines of 42 characters and break at punctuation where possible.
Usage: python3 make_captions.py
"""
import difflib
import json
import os
import re

from blocks import blocks
from split_narration import BUILD

# where the recorded delivery differs from SCRIPT.md, caption what was said
SPOKEN = {
    "D1": 'On the first of November 1889, Watkin\'s company published a brief. A tower of not less than 1,200 feet. '
          '500 guineas for the best design. And clause one, quote: "The designer will assume that the foundations '
          'are perfect." End quote.',
    "W6": "Taking it down started in 1904. In September 1907, they blew up the foundations with dynamite.",
    "O2": "I'm Eric Hoffman, and this was UNBUILT. Every picture in this video is real, and the sources are in "
          "the description.",
}
# numbers are easier to read as figures
FIGURES = [("twelve hundred", "1,200"), ("Five hundred guineas", "500 guineas"), ("Sixty-eight", "68"),
           ("sixty-eight", "68"), ("Number eighteen", "Number 18"), ("Number twenty-nine", "Number 29"),
           ("two thousand two hundred and ninety-six", "2,296"), ("two hundred thousand", "200,000"),
           ("Number fifty", "Number 50"), ("number thirty-eight", "number 38"), ("Number thirty-eight", "Number 38"),
           ("Two thousand feet", "2,000 feet"), ("number thirty-seven", "number 37"), ("Twelve hundred", "1,200"),
           ("ninety-bedroom", "90-bedroom"), ("two hundred feet", "200 feet"),
           ("three hundred and fifty-two thousand pounds", "£352,000"), ("two hundred miles", "200 miles"),
           ("Five hundred and eighteen", "518"), ("a hundred and fifty-five", "155"),
           ("a hundred and twenty thousand", "120,000"), ("a hundred and thirty-three", "133"),
           ("twelve minutes", "12 minutes"), ("Fifteen years", "15 years"), ("first of November", "1st of November")]
MAX_LINE, MAX_CUE_S = 42, 6.0
WEAK = {"the", "a", "an", "of", "for", "to", "in", "and", "by", "with", "at", "its", "his", "their", "that"}


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def words_with_times():
    cache = os.path.join(BUILD, "voice_words.json")
    voice = os.path.join(BUILD, "voice.wav")
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(voice):
        return json.load(open(cache))
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(voice, word_timestamps=True, beam_size=5)
    out = [[w.start, w.end, w.word] for s in segs for w in s.words]
    json.dump(out, open(cache, "w"))
    return out


def chunks(words):
    """Split into sentences, then halve any sentence too long for two 42-character lines, at the most balanced
    break, preferring one after a comma or colon. Returns lists of word indexes."""
    limit = 2 * MAX_LINE - 2
    sentences, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if w[-1] in ".?!" or (w[-1] == '"' and len(w) > 1 and w[-2] in ".?!"):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)

    def length(ix):
        return len(" ".join(words[j] for j in ix))

    def split(ix):
        if length(ix) <= limit or len(ix) < 4:
            return [ix]
        def cost(k):
            left, right = length(ix[:k]), length(ix[k:])
            bonus = 30 if words[ix[k - 1]][-1] in ",:;" else 0
            weak = 25 if words[ix[k - 1]].lower() in WEAK else 0       # don't end a cue on "the", "of"...
            return abs(left - right) - bonus + weak + (100 if k < 2 or len(ix) - k < 2 else 0)
        k = min(range(1, len(ix)), key=cost)
        return split(ix[:k]) + split(ix[k:])

    out = []
    for sen in sentences:
        out += split(sen)
    # join very short neighbours (e.g. "Remember that line.") when they fit together
    merged = []
    for c in out:
        if merged and (length(merged[-1]) < 25 or length(c) < 12) and length(merged[-1] + c) <= limit:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    return merged


def two_lines(text):
    if len(text) <= MAX_LINE:
        return text
    ws = text.split()
    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
    return " ".join(ws[:best]) + "\n" + " ".join(ws[best:])


def stamp(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    timings = json.load(open(os.path.join(BUILD, "timings.json")))
    rec = words_with_times()
    cues = []
    for name, text in blocks():
        text = SPOKEN.get(name, text)
        for a, b in FIGURES:
            text = text.replace(a, b)
        s0, e0 = timings[name]
        r = [w for w in rec if s0 - 0.3 <= w[0] <= e0 + 0.1]
        sw = text.split()                            # split() also drops double spaces
        # map each caption word to a recognised word's time; numbers spoken as words won't match, so interpolate
        times = [None] * len(sw)
        sm = difflib.SequenceMatcher(None, [norm(w) for w in sw], [norm(w[2]) for w in r], autojunk=False)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                times[blk.a + k] = (r[blk.b + k][0], r[blk.b + k][1])
        anchors = [(-1, (s0, s0))] + [(i, t) for i, t in enumerate(times) if t] + [(len(sw), (e0, e0))]
        for (i0, t0), (i1, t1) in zip(anchors, anchors[1:]):
            for i in range(i0 + 1, i1):
                f = (i - i0) / (i1 - i0)
                t = t0[1] + (t1[0] - t0[1]) * f
                times[i] = (t, t)
        for c in chunks(sw):
            start, end = times[c[0]][0], max(times[c[-1]][1], times[c[-1]][0] + 0.3)
            cues.append([max(0.0, start - 0.05), end + 0.25, " ".join(sw[j] for j in c)])
    for a, b in zip(cues, cues[1:]):            # no overlaps; keep each cue up for at least a second
        a[1] = min(max(a[1], a[0] + 1.0), b[0] - 0.02)
    with open(os.path.join(BUILD, "captions.srt"), "w") as f:
        for i, (s, e, t) in enumerate(cues, 1):
            f.write(f"{i}\n{stamp(s)} --> {stamp(e)}\n{two_lines(t)}\n\n")
    long = [c for c in cues if c[1] - c[0] > MAX_CUE_S + 2]
    print(f"{len(cues)} cues, last ends {cues[-1][1]:.1f} s. Over {MAX_CUE_S + 2:.0f} s: {len(long)}")


if __name__ == "__main__":
    main()
