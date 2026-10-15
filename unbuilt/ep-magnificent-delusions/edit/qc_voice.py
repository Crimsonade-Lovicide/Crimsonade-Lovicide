"""Voice and lip-sync QC for the cut.

For every line: transcribe each stage (raw TTS, tightened TTS, lip-aligned take, final cut) and diff it
against the script, so damage can be pinned to the stage that caused it. For every sync shot: compare word
onsets in the final cut with the lips Seedance rendered (the clip's native audio), and check the clip
covers the whole line (otherwise the picture freezes while he talks).

Usage: python3 qc_voice.py <asset_dir> <tts_lines.json> <raw_audio_dir> > report.txt
"""
import difflib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

FF = os.environ.get("FFMPEG", "ffmpeg")
A, LINES, RAW = sys.argv[1:4]
MODEL = WhisperModel(os.environ.get("WHISPER", "small.en"), compute_type="int8")
CO1_TEXT = "Most buildings that never got built... deserved it. These five didn't."
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
       "seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def say(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + say(n % 100))
    if 1100 <= n < 2000:  # years
        return say(n // 100) + " " + ("hundred" if n % 100 == 0 else ("oh " + ONES[n % 100]) if n % 100 < 10 else say(n % 100))
    if n < 1_000_000:
        return say(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + say(n % 1000))
    return say(n // 1_000_000) + " million" + ("" if n % 1_000_000 == 0 else " " + say(n % 1_000_000))


def norm(text):
    t = text.lower().replace("’", "'").replace("£", " pound ").replace("$", " dollar ").replace("%", " percent")
    t = re.sub(r"(\d),(\d)", r"\1\2", t)
    t = re.sub(r"\d+", lambda m: " " + say(m.group()) + " ", t)
    t = re.sub(r"[-–—/]", " ", t)
    t = re.sub(r"[^a-z' ]", " ", t)
    return [w.strip("'") for w in t.split() if w.strip("'")]


def to16k(src, ss=None, dur=None):
    cmd = [FF, "-nostdin", "-loglevel", "error"] + (["-ss", f"{ss:.3f}"] if ss is not None else []) + ["-i", src]
    cmd += (["-t", f"{dur:.3f}"] if dur else []) + ["-map", "0:a", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.int16).astype(np.float32) / 32768


def words(audio):
    segs, _ = MODEL.transcribe(audio, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    out = []
    for s in segs:
        for w in s.words:
            for piece in norm(w.word):
                out.append((piece, w.start, w.end, w.probability))
    return out


def diff(ref, hyp):
    sm = difflib.SequenceMatcher(a=ref, b=[w[0] for w in hyp], autojunk=False)
    errs, ops = 0, []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            errs += max(i2 - i1, j2 - j1)
            ops.append(f"{tag}: '{' '.join(ref[i1:i2])}' -> '{' '.join(w[0] for w in hyp[j1:j2])}'")
    return errs / max(len(ref), 1), ops


def wav_len(p):
    w = wave.open(p)
    return w.getnframes() / w.getframerate()


# the edit: beats, their audio keys and start times in the cut
sys.argv = ["assemble.py", A, os.devnull]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assemble.py")).read()
g = {"__name__": "qc"}
exec(src.split('if __name__ == "__main__":')[0], g)
BEATS = g["BEATS"]
starts = json.load(open(os.path.join(A, "build", "timeline.json")))["starts"]
lines = json.load(open(LINES))
voice = os.path.join(A, "build", "voice.wav")


def script_text(key):
    if key == "CO1":
        return CO1_TEXT
    k = int(key)
    t = lines[k][2]
    if k in (9, 20):  # these beats carry two script lines
        t += " " + lines[k + 1][2]
    return t


summary = []
for i, b in enumerate(BEATS):
    key = b["audio"]
    if key is None:
        continue
    kind, shot = b["visuals"][0][0], b["visuals"][0][1]
    ref = norm(script_text(key))
    t0, t1 = starts[i], starts[i + 1]
    stages = []
    raw = os.path.join(RAW, f"m_{key}.wav")
    if os.path.exists(raw):
        stages.append(("raw TTS", to16k(raw)))
    stages.append(("tightened", to16k(os.path.join(A, "audio", f"t_{key}.wav"))))
    aligned = os.path.join(A, "audio", f"t_s_{shot}.wav")
    if kind == "sync" and os.path.exists(aligned):
        stages.append(("sync voice", to16k(aligned)))
    final_audio = to16k(voice, t0, t1 - t0)
    stages.append(("FINAL", final_audio))
    print(f"\n=== beat {i:02d} {shot:5s} [{kind}] {int(t0 // 60)}:{t0 % 60:05.2f}-{int(t1 // 60)}:{t1 % 60:05.2f}  line {key}")
    print(f"    script: {' '.join(ref)}")
    res = {}
    for name, audio in stages:
        hyp = words(audio)
        wer, ops = diff(ref, hyp)
        low = [f"{w[0]}@{w[1]:.2f}({w[3]:.2f})" for w in hyp if w[3] < 0.5]
        res[name] = (wer, hyp)
        print(f"    {name:11s} WER {wer:4.0%}  {'; '.join(ops) if ops else 'ok'}" + (f"   low-confidence: {' '.join(low)}" if low else ""))
    row = dict(beat=i, shot=shot, kind=kind, t0=t0, final_wer=res["FINAL"][0],
               tight_wer=res["tightened"][0], raw_wer=res.get("raw TTS", (None,))[0])
    if kind == "sync":
        clip = os.path.join(A, "vid", f"sync_{shot}.mp4")
        side = os.path.join(A, "audio", f"t_s_{shot}.json")
        ss = json.load(open(side))["start"] if os.path.exists(side) else 0.0  # head trimmed by sync_audio.py
        native = [(w[0], w[1] - ss, w[2] - ss, w[3]) for w in words(to16k(clip)) if w[1] >= ss - 0.05]
        fw = res["FINAL"][1]
        sm = difflib.SequenceMatcher(a=[w[0] for w in native], b=[w[0] for w in fw], autojunk=False)
        deltas = []
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                n, f = native[blk.a + k], fw[blk.b + k]
                deltas.append((n[0], f[1] - n[1]))
        clip_len = len(to16k(clip)) / 16000 - ss
        speech_end = fw[-1][2] if fw else 0
        if deltas:
            d = np.array([x[1] for x in deltas])
            worst = max(deltas, key=lambda x: abs(x[1]))
            print(f"    LIP SYNC   {len(deltas)}/{len(native)} words matched, median {np.median(d) * 1000:+.0f} ms, "
                  f"mean |err| {np.mean(abs(d)) * 1000:.0f} ms, worst '{worst[0]}' {worst[1] * 1000:+.0f} ms")
            row.update(lip_med=float(np.median(d)), lip_mean_abs=float(np.mean(abs(d))), lip_worst=worst)
        print(f"    native (lips): {' '.join(w[0] for w in native)}")
        print(f"    clip {clip_len:.2f}s, voice ends {speech_end:.2f}s" + (
            "  ** FREEZE: he keeps talking after the clip ends" if speech_end > clip_len + 0.1 else ""))
        row.update(clip_len=clip_len, speech_end=speech_end)
    summary.append(row)
    sys.stdout.flush()

json.dump(summary, open(os.path.join(A, "build", "qc_voice.json"), "w"), indent=1, default=str)
