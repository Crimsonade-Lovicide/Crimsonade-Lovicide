"""Re-time the clean TTS take to the lip timing Seedance rendered.

Seedance lip-syncs to the reference audio but sometimes stretches pauses and re-voices words
("gap" became "grab"). We keep the clean take's words and move each word to the onset of the
matching word in the rendered clip, so lips and voice line up.

Usage: python3 align.py <asset_dir> <SHOT_ID> <tts_key>
Writes <asset_dir>/audio/t_s_<SHOT_ID>.wav
"""
import difflib
import os
import re
import subprocess
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

FF = os.environ.get("FFMPEG", "ffmpeg")
A, SID, KEY = sys.argv[1], sys.argv[2], sys.argv[3]
SR = 44100
_model = WhisperModel("small.en", compute_type="int8")


def load(path):
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)


def words(path):
    segs, _ = _model.transcribe(path, word_timestamps=True)
    return [(re.sub(r"[^a-z']", "", w.word.lower()), w.start, w.end) for s in segs for w in s.words]


native = os.path.join(A, "build", f"native_{SID}.wav")
subprocess.run([FF, "-nostdin", "-loglevel", "error", "-y", "-i", os.path.join(A, "vid", f"sync_{SID}.mp4"),
                "-vn", "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", native], check=True)
tts_path = os.path.join(A, "audio", f"t_{KEY}.wav")
tts = load(tts_path)
wt, wn = words(tts_path), words(native)

# map TTS words to native words; unmatched words keep the running offset
sm = difflib.SequenceMatcher(a=[w[0] for w in wt], b=[w[0] for w in wn], autojunk=False)
target = [None] * len(wt)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ("equal", "replace") and (i2 - i1) == (j2 - j1):
        for k in range(i2 - i1):
            target[i1 + k] = wn[j1 + k][1]
offset = 0.0
for i, w in enumerate(wt):
    if target[i] is None:
        target[i] = w[1] + offset
    offset = target[i] - w[1]

out = np.zeros(int((max(target) + (len(tts) / SR - wt[-1][1]) + 1.0) * SR), dtype=np.float32)
bounds = [int(w[1] * SR) for w in wt] + [len(tts)]
bounds[0] = 0
cursor = 0
for i in range(len(wt)):
    seg = tts[bounds[i]:bounds[i + 1]].copy()
    start = max(int(target[i] * SR), cursor) if i else 0
    if i + 1 < len(wt):
        room = int(target[i + 1] * SR) - start
        if room > 0 and len(seg) > room:
            seg = seg[:room]  # trim the trailing pause, never the next word
    f = min(220, len(seg) // 4)
    if f:
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
    out[start:start + len(seg)] += seg
    cursor = start + len(seg)
out = out[:cursor + int(0.05 * SR)]
o = wave.open(os.path.join(A, "audio", f"t_s_{SID}.wav"), "wb")
o.setnchannels(1)
o.setsampwidth(2)
o.setframerate(SR)
o.writeframes(np.clip(out, -32768, 32767).astype(np.int16).tobytes())
o.close()
print(SID, "tts", [(w[0], round(w[1], 2)) for w in wt])
print(SID, "lip", [(w[0], round(w[1], 2)) for w in wn])
print(SID, "->", [round(t, 2) for t in target], round(cursor / SR, 2), "s")
