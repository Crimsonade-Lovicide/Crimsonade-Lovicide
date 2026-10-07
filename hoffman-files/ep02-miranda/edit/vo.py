"""Temporary voice-over: reads each scripted line with a local Piper voice so the story reel has real pacing.
Ep. 2. It is a placeholder for Eric's own recording and is labeled as synthetic on screen."""
import json, os, subprocess, sys, wave
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from episode import SEGMENTS
VOICE = os.environ.get('PIPER_VOICE', os.path.join(HERE, '..', 'voices', 'en_US-ryan-high.onnx'))
timing = {}
for s in SEGMENTS:
    if not s.get('vo'): continue
    out = os.path.join(HERE, 'audio', f"{s['id']}.wav")
    subprocess.run(['python3', '-m', 'piper', '-m', VOICE, '--length-scale', '1.22', '--sentence-silence', '0.28', '-f', out],
                   input=s['vo'].encode(), check=True, capture_output=True)
    with wave.open(out) as w: timing[s['id']] = round(w.getnframes() / w.getframerate(), 3)
json.dump(timing, open(os.path.join(HERE, 'audio', 'timing.json'), 'w'), indent=1)
print(len(timing), 'lines,', round(sum(timing.values()) / 60, 2), 'min of VO')
