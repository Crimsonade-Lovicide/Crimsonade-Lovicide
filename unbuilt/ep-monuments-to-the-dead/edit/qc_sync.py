"""Transcribe each sync clip, compare with the script line, and make a 4-frame strip. Usage (from the asset dir, which holds tts_manifest.json and ledger.json): python3 qc_sync.py ID..."""
import json, os, re, sys, subprocess, difflib, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw
FF = os.environ.get("FFMPEG", "ffmpeg")
M = {x["key"]: x for x in json.load(open("tts_manifest.json"))}
model = WhisperModel("small.en", compute_type="int8")
norm = lambda t: re.sub(r"[^a-z0-9' ]", " ", t.lower().replace("-", " ")).split()
L = json.load(open("ledger.json")); Q = L.setdefault("sync_qc", {})
for k in sys.argv[1:]:
    f = f"vid/sync_{k}.mp4"
    y = np.frombuffer(subprocess.run([FF, "-nostdin", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout, dtype=np.int16).astype(np.float32) / 32768
    dur = len(y) / 16000
    got = " ".join(s.text for s in model.transcribe(y, beam_size=5)[0]).strip()
    r = difflib.SequenceMatcher(a=norm(M[k]["tts"]), b=norm(got)).ratio()
    Q[k] = {"secs": round(dur, 2), "match": round(r, 3), "heard": got}
    print(f"{k:4s} {dur:5.2f}s match {r:.2f} | {got}", flush=True)
    frames = []
    for t in (0.3, dur * 0.35, dur * 0.65, dur - 0.4):
        raw = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", f, "-frames:v", "1", "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        frames.append(Image.frombytes("RGB", (480, 270), raw))
    strip = Image.new("RGB", (1920, 270)); [strip.paste(im, (i * 480, 0)) for i, im in enumerate(frames)]
    ImageDraw.Draw(strip).text((8, 8), k, fill="yellow"); strip.save(f"vid/strip_{k}.jpg", quality=85)
json.dump(L, open("ledger.json", "w"), indent=1)
