"""Download a TTS wav, trim edge silence and cap internal pauses. Usage: tighten.py <key> <url>"""
import sys, subprocess, urllib.request, numpy as np, wave, json, os
FF = os.environ.get("FFMPEG", "ffmpeg")
key, url = sys.argv[1], sys.argv[2]
raw = f"raw_{key}.wav"
if not os.path.exists(raw):
    urllib.request.urlretrieve(url, raw)
subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", f"m_{key}.wav"], check=True)
w = wave.open(f"m_{key}.wav"); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
hop = int(sr * 0.01)
n = len(x) // hop
rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9
db = 20 * np.log10(rms / 32768)
voiced = db > -42
# edges: find the first/last sound at a much lower threshold, so soft onsets ("wh", "f", "s") and
# trailing consonants survive, and keep a little air either side
audible = np.where(db > -58)[0]
start, end = max(audible[0] - 6, 0), min(audible[-1] + 15, n)
segs, i = [], start
while i < end:
    j = i
    while j < end and voiced[j] == voiced[i]:
        j += 1
    segs.append((voiced[i], i, j)); i = j
out = []
for v, a, b in segs:
    chunk = x[a * hop : b * hop]
    if not v:
        dur = (b - a) / 100
        cap = 0.5 if dur > 1.0 else 0.32
        if dur > cap:
            k = int(cap * sr); h = k // 2
            chunk = np.concatenate([chunk[:h], chunk[-(k - h):]])
    out.append(chunk)
y = np.concatenate(out)
fade = int(sr * 0.005); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
o = wave.open(f"t_{key}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
o.writeframes(y.astype(np.int16).tobytes()); o.close()
subprocess.run([FF, "-loglevel", "error", "-y", "-i", f"t_{key}.wav", "-b:a", "192k", f"t_{key}.mp3"], check=True)
print(json.dumps({"key": key, "raw_s": round(len(x) / sr, 2), "tight_s": round(len(y) / sr, 2)}))
