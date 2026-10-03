"""Build the voice for a sync shot from the clip's own audio, which is lip-synced by construction.

Seedance re-voices the reference line and sometimes gets a word wrong ("gap" -> "grab"). Words that
differ from the script are replaced with the same words from the clean TTS take, stretched to the exact
span of the rendered mouth movement and matched in pitch and level, so the lips still fit.
(This replaces align.py, whose word-by-word re-timing of the TTS clipped and skipped syllables.)

Usage: python3 sync_audio.py <asset_dir> <SHOT_ID> <tts_key> "<script line>"
Writes <asset_dir>/audio/t_s_<SHOT_ID>.wav and .json (the clip start, if invented words were cut from the head)
"""
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
import wave

import librosa
import numpy as np
from faster_whisper import WhisperModel

FF = os.environ.get("FFMPEG", "ffmpeg")
A, SID, KEY, TEXT = sys.argv[1:5]
SR = 48000
MODEL = WhisperModel(os.environ.get("WHISPER", "small.en"), compute_type="int8")


def load(src):
    raw = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-i", src, "-map", "0:a", "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()  # Sörgel -> sorgel
    return [w for w in re.sub(r"[^a-z0-9' ]", " ", t.lower().replace("-", " ")).split()]


def words(y):
    y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
    segs, _ = MODEL.transcribe(y16, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    return [(n, w.start, w.end, w.probability) for s in segs for w in s.words for n in norm(w.word)]


def quiet_point(y, t, search=0.08):
    """Nearest low-energy sample to time t, so cuts fall between phonemes rather than inside them."""
    hop = int(0.005 * SR)
    a, b = max(0, int((t - search) * SR)), min(len(y), int((t + search) * SR))
    if b - a < 2 * hop:
        return int(t * SR)
    e = np.convolve(y[a:b] ** 2, np.ones(hop) / hop, mode="same")
    return a + int(np.argmin(e))


def median_f0(y):
    f0, _, _ = librosa.pyin(librosa.resample(y, orig_sr=SR, target_sr=16000), fmin=60, fmax=300, sr=16000,
                            frame_length=1024)
    return np.nanmedian(f0)


def splice(dst, n0, n1, piece):
    """Put piece into dst[n0:n1]: stretched to fit, pitch- and level-matched, crossfaded."""
    piece = librosa.effects.time_stretch(piece, rate=len(piece) / (n1 - n0))
    if np.isfinite(f0_clip) and np.isfinite(f0_tts):
        piece = librosa.effects.pitch_shift(piece, sr=SR, n_steps=12 * np.log2(f0_clip / f0_tts))
    piece = np.pad(piece[: n1 - n0], (0, max(0, (n1 - n0) - len(piece))))
    orig = dst[n0:n1]
    piece *= (np.sqrt(np.mean(orig ** 2)) + 1e-6) / (np.sqrt(np.mean(piece ** 2)) + 1e-6)
    f = min(int(0.012 * SR), len(piece) // 4)
    ramp = np.linspace(0, 1, f)
    piece[:f] = piece[:f] * ramp + orig[:f] * (1 - ramp)
    piece[-f:] = piece[-f:] * ramp[::-1] + orig[-f:] * (1 - ramp[::-1])
    res = dst.copy()
    res[n0:n1] = piece
    return res


clip = load(os.path.join(A, "vid", f"sync_{SID}.mp4"))
tts = load(os.path.join(A, "audio", f"t_{KEY}.wav"))
ref = norm(TEXT)
wn, wt = words(clip), words(tts)
out = clip.copy()

sm = difflib.SequenceMatcher(a=ref, b=[w[0] for w in wn], autojunk=False)
tt_map = difflib.SequenceMatcher(a=ref, b=[w[0] for w in wt], autojunk=False)
ref_to_tts = {}
for tag, i1, i2, j1, j2 in tt_map.get_opcodes():
    if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):  # e.g. ASR spells a name differently
        for k in range(i2 - i1):
            ref_to_tts[i1 + k] = j1 + k

patched, unresolved = [], []
start, last_kept = 0, len(wn) - 1
f0_clip = median_f0(clip)
f0_tts = median_f0(tts)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    if tag == "replace" and all(i in ref_to_tts for i in range(i1, i2)):
        # try several cut windows and keep the splice whose re-transcription reads best
        best = None
        for search in (0.02, 0.04, 0.06, 0.09):
            n0, n1 = quiet_point(clip, wn[j1][1], search), quiet_point(clip, wn[j2 - 1][2], search)
            s0 = quiet_point(tts, wt[ref_to_tts[i1]][1], search)
            s1 = quiet_point(tts, wt[ref_to_tts[i2 - 1]][2], search)
            if n1 - n0 < int(0.05 * SR) or s1 - s0 < int(0.05 * SR):
                continue
            cand = splice(out, n0, n1, tts[s0:s1])
            a, b = max(0, n0 - SR // 2), min(len(cand), n1 + SR // 2)
            got = words(cand[a:b])
            target = [wt[ref_to_tts[i]][0] for i in range(i1, i2)]  # as the clean take reads (names!)
            probs = [w[3] for w in got if w[0] in target]
            score = (all(t in [w[0] for w in got] for t in target), min(probs) if probs else 0)
            if best is None or score > best[0]:
                best = (score, cand, n0)
        if best is None or not best[0][0]:
            # no splice reads back correctly: a clean wrong-ish word beats a garbled right one
            unresolved.append(("kept native", ref[i1:i2], [w[0] for w in wn[j1:j2]]))
            continue
        out = best[1]
        patched.append((" ".join(w[0] for w in wn[j1:j2]), " ".join(ref[i1:i2]), round(best[2] / SR, 2),
                        f"check {'ok' if best[0][0] else 'MISS'} p={best[0][1]:.2f}"))
    elif tag == "insert" and j1 == 0:
        # words invented before the line: start the shot (picture and sound) where the real line begins
        start = quiet_point(clip, wn[j2][1])
        patched.append((" ".join(w[0] for w in wn[j1:j2]), "(cut from the head)", 0.0))
    elif tag == "insert" and j2 == len(wn):
        last_kept = j1 - 1
        patched.append((" ".join(w[0] for w in wn[j1:j2]), "(cut from the tail)", round(wn[j1][1], 2)))
    elif tag == "insert":
        # a word the script doesn't have: silence it, but keep the timing
        n0, n1 = quiet_point(clip, wn[j1][1]), quiet_point(clip, wn[j2 - 1][2])
        if n1 > n0:
            f = min(int(0.012 * SR), (n1 - n0) // 2)
            env = np.zeros(n1 - n0)
            env[:f], env[-f:] = np.linspace(1, 0, f), np.linspace(0, 1, f)
            out[n0:n1] *= env
        patched.append((" ".join(w[0] for w in wn[j1:j2]), "(removed)", round(n0 / SR, 2)))
    else:
        unresolved.append((tag, ref[i1:i2], [w[0] for w in wn[j1:j2]]))

# keep the clip's timeline (so lips stay locked), end just after the last word
end = min(len(out), quiet_point(clip, wn[last_kept][2] + 0.25)) if wn else len(out)
out = out[start:end]
out[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
with open(os.path.join(A, "audio", f"t_s_{SID}.json"), "w") as f:
    json.dump({"start": start / SR}, f)  # assemble.py starts the clip here too
out[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
o = wave.open(os.path.join(A, "audio", f"t_s_{SID}.wav"), "wb")
o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
o.close()
print(f"{SID}: native '{' '.join(w[0] for w in wn)}'")
print(f"{SID}: patched {patched or 'nothing'}; unresolved {unresolved or 'none'}; "
      f"clip {start / SR:.2f}-{end / SR:.2f}s")
