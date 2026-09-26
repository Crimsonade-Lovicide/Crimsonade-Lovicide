"""Lay the theme ("The Architect's Parade", 61s, ~117 BPM) under the voice cut.

The track has a clean 16-beat phrase grid, so the score is built from phrases:
  - cold open: the build crests on the title card and the drop lands on the No.5 cut
  - each countdown card restarts the cue on a different phrase, then the quiet breakdown
    (32.37-48.37s, exactly 32 beats) loops under the narration
  - No.1 runs straight into the finale, which ends on the end card; the Loos stinger plays dry
The voice ducks the music through a sidechain compressor, then the mix is normalised to -14 LUFS.

Usage: python3 score.py <asset_dir> <music.mp3> <voice_cut.mp4> <out.mp4>
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

FF = os.environ.get("FFMPEG", "ffmpeg")
A, MUSIC, VOICE, OUT = sys.argv[1:5]
SR = 48000

# phrase starts (s) from librosa beat tracking of the track: beats 0, 16, 32, 48, 64, 96
PH = {0: 0.093, 16: 8.359, 32: 16.370, 48: 24.358, 64: 32.369, 96: 48.367}
LOOP = (PH[64], PH[96])  # the breakdown
BASE, CARD_BUMP, PEAK = -8.0, -3.0, -1.0  # music gain in dB before ducking

# EDL beat indices from assemble.py
TITLE, CARDS, END, HON, STINGER = 7, {17: 16, 29: 0, 37: 32, 45: 48}, 59, 60, 61


def run(cmd, **kw):
    return subprocess.run([FF, "-nostdin", "-y", "-loglevel", "error"] + cmd, check=True, **kw)


# picture timeline: start time of every beat in the cut, written by assemble.py
build = os.path.join(A, "build")
starts = np.array(json.load(open(os.path.join(build, "timeline.json")))["starts"])
total = starts[-1]

wav = os.path.join(build, "music48.wav")
run(["-i", MUSIC, "-ac", "2", "-ar", str(SR), "-sample_fmt", "s16", wav])
w = wave.open(wav)
trk = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768

bed = np.zeros((int(total * SR) + SR, 2), dtype=np.float32)
S = lambda t: int(round(t * SR))


def lay(t0, t1, src0, loop=True, fade_in=0.0):
    """Fill video [t0,t1) from track time src0; with loop, jump back to the breakdown start at its end."""
    pos, src = t0, src0
    while pos < t1 - 1e-3:
        n = min((LOOP[1] if loop else len(trk) / SR) - src, t1 - pos)
        seg = trk[S(src):S(src) + S(n)].copy()
        k = min(S(0.012), len(seg) // 2)  # click-free seams on the beat
        if k:
            seg[:k] *= np.linspace(0, 1, k)[:, None]
            seg[-k:] *= np.linspace(1, 0, k)[:, None]
        if fade_in and pos == t0:
            f = min(S(fade_in), len(seg))
            seg[:f] *= np.linspace(0, 1, f)[:, None]
        bed[S(pos):S(pos) + len(seg)] += seg
        pos += n
        src = LOOP[0]
        if not loop:
            break


# gain envelope in dB, keyed by video time
env_t, env_g = [0.0], [BASE + 2]
def key(t, g):
    env_t.append(t); env_g.append(g)


# cold open: align the drop (beat 64) to the first No.5 frame
t_no5 = starts[TITLE + 1]
off = PH[64] - t_no5
lay(0, t_no5, off, loop=False, fade_in=1.0)
key(starts[TITLE] - 0.5, BASE + 2); key(starts[TITLE], PEAK); key(t_no5, PEAK); key(t_no5 + 1.5, BASE)

# countdown segments; No.1 runs into the finale without looping
card_idx = [TITLE + 1] + sorted(CARDS)
for j, ci in enumerate(card_idx):
    t0 = starts[ci]
    last = j == len(card_idx) - 1
    t1 = total if last else starts[card_idx[j + 1]]
    src0 = PH[64] if ci == TITLE + 1 else PH[CARDS[ci]]
    if last:
        # play to the drop, loop the breakdown n times, then run the finale through
        into_loop = PH[64] - src0
        # choose n so the finale's last note (58.6s) lands as close as possible to the end of the HON card
        target = starts[STINGER]
        best = min(range(0, 12), key=lambda n: abs(t0 + into_loop + n * (LOOP[1] - LOOP[0]) + (58.6 - PH[64]) - target))
        t = t0
        if into_loop > 0:
            lay(t, t + into_loop, src0, loop=False); t += into_loop
        for _ in range(best):
            lay(t, t + (LOOP[1] - LOOP[0]), LOOP[0], loop=False); t += LOOP[1] - LOOP[0]
        lay(t, total, PH[64], loop=False)
        finale = t + (51.618 - PH[64])  # onset of the final peak
        print(f"No.1 loops {best}, finale peak at {finale:.2f}s, last note at {t + 58.6 - PH[64]:.2f}s "
              f"(HON ends {target:.2f}s)")
        if ci != TITLE + 1:
            key(t0 - 0.05, BASE); key(t0, CARD_BUMP); key(t0 + 1.2, CARD_BUMP); key(t0 + 2.5, BASE)
        key(finale - 1.5, BASE); key(finale, PEAK); key(total, PEAK)
    else:
        if src0 < LOOP[1] and src0 != PH[64]:
            # phrase opener, skip the loud build (beats 48-64) and drop into the breakdown loop
            pre = (PH[48] if src0 < PH[48] else PH[64]) - src0
            lay(t0, min(t1, t0 + pre), src0, loop=False)
            if t0 + pre < t1:
                lay(t0 + pre, t1, PH[64])
        else:
            lay(t0, t1, src0)
        if ci != TITLE + 1:
            key(t0 - 0.05, BASE); key(t0, CARD_BUMP); key(t0 + 1.2, CARD_BUMP); key(t0 + 2.5, BASE)

tt = np.arange(len(bed)) / SR
gain = 10 ** (np.interp(tt, env_t, env_g) / 20)
bed *= gain[:, None]
bed[S(starts[STINGER]) + S(1.5):] = 0  # the stinger plays dry once the finale has decayed

bed_path = os.path.join(build, "bed.wav")
o = wave.open(bed_path, "wb")
o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes())
o.close()

# duck under the voice, mix, then normalise: measure, gain, limit
fc = ("[0:a]aresample=48000,asplit=2[v1][v2];"
      "[1:a][v2]sidechaincompress=threshold=0.02:ratio=6:attack=10:release=450:knee=4[m];"
      "[v1][m]amix=inputs=2:normalize=0:duration=first[mix]")
premix = os.path.join(build, "premix.wav")
run(["-i", VOICE, "-i", bed_path, "-filter_complex", fc, "-map", "[mix]", premix])
err = subprocess.run([FF, "-nostdin", "-i", premix, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])
g = -14.0 - lufs
run(["-i", VOICE, "-i", premix, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
     "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=disabled", "-c:a", "aac", "-b:a", "256k",
     "-movflags", "+faststart", OUT])
print(f"premix {lufs:.1f} LUFS, gain {g:+.1f} dB -> {OUT}")
