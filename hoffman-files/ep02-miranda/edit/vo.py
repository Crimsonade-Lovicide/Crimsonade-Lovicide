"""Temporary voice-over: reads each scripted line with a local Piper voice so the story reel has real pacing.
Ep. 2. It is a placeholder for Eric's own recording and is labeled as synthetic on screen.

Piper's output length varies a little from run to run, and every segment clip is cut to its line's length. So a
line is re-read only when its text changed (or its file is missing); unchanged lines keep their audio and timing.
`python3 vo.py --all` forces every line to be re-read (then re-render every segment)."""
import json, os, subprocess, sys, wave
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from episode import SEGMENTS
VOICE = os.environ.get('PIPER_VOICE', os.path.join(HERE, '..', 'voices', 'en_US-ryan-high.onnx'))
AUDIO = os.path.join(HERE, 'audio')
TEXTS = os.path.join(AUDIO, 'texts.json')
os.makedirs(AUDIO, exist_ok=True)
read_before = {} if '--all' in sys.argv or not os.path.exists(TEXTS) else json.load(open(TEXTS))
timing, texts, redone = {}, {}, []
for s in SEGMENTS:
    if not s.get('vo'): continue
    out = os.path.join(AUDIO, f"{s['id']}.wav")
    if read_before.get(s['id']) != s['vo'] or not os.path.exists(out):
        subprocess.run(['python3', '-m', 'piper', '-m', VOICE, '--length-scale', '1.22', '--sentence-silence', '0.28', '-f', out],
                       input=s['vo'].encode(), check=True, capture_output=True)
        redone.append(s['id'])
    with wave.open(out) as w: timing[s['id']] = round(w.getnframes() / w.getframerate(), 3)
    texts[s['id']] = s['vo']
json.dump(timing, open(os.path.join(AUDIO, 'timing.json'), 'w'), indent=1)
json.dump(texts, open(TEXTS, 'w'), indent=1)
print(len(timing), 'lines,', round(sum(timing.values()) / 60, 2), 'min of VO; re-read:', ' '.join(redone) or 'none')
