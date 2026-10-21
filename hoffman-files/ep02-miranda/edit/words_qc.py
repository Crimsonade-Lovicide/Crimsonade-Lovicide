"""Transcribe each recorded line as built (audio/<id>.wav) with word timings -> audio/<id>.words.json.
Edit cues use these timings; the printout is the QC: compare each line with the script."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from faster_whisper import WhisperModel
from episode import SEGMENTS
ids = sys.argv[1:]
m = WhisperModel(os.environ.get('WHISPER', 'medium.en'), device='cpu', compute_type='int8', cpu_threads=4)
for s in SEGMENTS:
    if not s.get('take') or s['kind'] == 'aroll' or (ids and s['id'] not in ids): continue
    wav = os.path.join('audio', s['id'] + '.wav')
    segs, _ = m.transcribe(wav, word_timestamps=True, beam_size=5, condition_on_previous_text=False)
    ws = [(w.word.strip(), round(w.start, 3)) for g in segs for w in g.words]
    json.dump(ws, open(os.path.join('audio', s['id'] + '.words.json'), 'w'))
    print(f"== {s['id']}\n  HEARD : {' '.join(w for w, _ in ws)}\n  SCRIPT: {s['vo']}", flush=True)
