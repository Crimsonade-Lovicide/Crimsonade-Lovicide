"""Transcribe each sync clip, compare with the script line, and make a 4-frame strip plus a mouth strip.
The mouth strip (vid/mouth_<ID>.jpg: face-tracked mouth at 4 fps, orange border = voice audible) is there because
a transcript can be perfect while the lips never move: C7 in this episode passed the transcript check that way. Usage (from the asset dir, which holds tts_manifest.json and ledger.json): python3 qc_sync.py ID..."""
import json, os, re, sys, subprocess, difflib, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw
import cv2  # opencv-python-headless<5 (the Haar face detector left the main package in 5.0)
FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
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
    raw = subprocess.run([FF, "-nostdin", "-loglevel", "error", "-i", f, "-vf", "fps=4,scale=1280:720", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, 720, 1280, 3)
    box, tiles = None, []
    for i, fr in enumerate(F):
        faces = FACE.detectMultiScale(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), 1.2, 5, minSize=(60, 60))
        if len(faces): box = max(faces, key=lambda b: b[2] * b[3])
        seg = y[i * 4000:(i + 1) * 4000]
        talk = len(seg) and np.sqrt(np.mean(seg ** 2)) > 0.015
        if box is None: im = Image.new("RGB", (110, 70))
        else:
            x0, y0, w, h = box
            im = Image.fromarray(fr[y0 + int(.55 * h):y0 + int(1.05 * h), x0 + int(.15 * w):x0 + int(.85 * w)]).resize((110, 70))
        ImageDraw.Draw(im).rectangle([0, 0, 109, 69], outline=(255, 140, 0) if talk else (60, 60, 60), width=3)
        tiles.append(im)
    ms = Image.new("RGB", (110 * len(tiles), 70)); [ms.paste(t, (i * 110, 0)) for i, t in enumerate(tiles)]
    ms.save(f"vid/mouth_{k}.jpg", quality=85)
json.dump(L, open("ledger.json", "w"), indent=1)
