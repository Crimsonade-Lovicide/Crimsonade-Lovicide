# The Hoffman Files, Ep. 3: Loving v. Virginia

Production doc: the Episode 3 production doc in Claude Docs (fact base, script draft, 3D plan, music, clearance, sources).

Status: script drafted, nothing recorded.

- `edit/episode.py` is the beat list (27 beats). Its text matches the doc's Script draft; each beat lists the fact-base numbers it rests on.
- `edit/recording_script.py` builds `recording_script.md` (table in reel order) and `recording_script.pdf` (print copy: the five on-camera pieces, then the 20 voice-over lines, one sentence per line, with slates, delivery notes and pronunciations).

```
FONT_DIR=<dir with Inter.ttf, BebasNeue.ttf, PlexMonoSemi.ttf> python3 edit/recording_script.py
```

Rules for this episode: the Lovings are never depicted, no Grey Villet photographs, no AI imagery, no synthetic voice. Quotations go on screen word for word from the opinions and the oral-argument transcript.
