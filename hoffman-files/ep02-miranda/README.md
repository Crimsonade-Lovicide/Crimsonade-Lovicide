# The Hoffman Files, Ep. 2: Miranda

Production doc: the Episode 2 production doc in Claude Docs (fact base, script, visuals, music brief, guests, clearance).

- Music lives in `../music/`: the series theme opens and closes; public domain Musopen recordings carry the acts.

## 3D (`blender/`)

No people in any scene: rooms, objects and empty chairs carry it.

| Scene | File | What it shows | Label on screen |
|---|---|---|---|
| M1 | `m1_card.py` | Warning card on a steel table under one lamp, push-in | none |
| M2 | `m2_busstop.py` | Empty bus stop under a sodium streetlight, night | Illustration · no one is shown |
| M3 | `m3_room.py` | Interrogation Room No. 2: table, two chairs, hanging lamp, door marked 2, clock running two hours | Reconstruction · layout illustrative |
| M6 | `m6_bench.py` | Nine high-backed chairs; five light up, four stay dark | Illustration · abstract bench, not the real courtroom |
| M9 | `m9_cards.py` | Stack of warning cards and a pen; the top card flips to a blank back | Illustration · no signature shown |
| M10 | `m10_bar.py` | Bar exterior at night, unlit nameless sign, empty street | Illustration · generic building, not the actual bar |

`./render_ep2.sh` renders look-check previews. The scenes reuse the ep. 1 kit and `common.py`.

## Edit (`edit/`)

Same assembler as ep. 1, with ep. 2's beats and graphics. The ep. 1 graphics module supplies the helpers and slates.

- `episode.py` is the edit decision list: 38 beats, about 12 minutes with the planned interviews, with Eric's line, the picture, and cue phrases that time graphics and 3D to the words. It adds a `hold` kind: two seconds of black and silence after the bar scene.
- `gfx2.py` holds the ep. 2 cards:
  - title card
  - Phoenix typed card
  - confession form, recreated as type with the certification line highlighted
  - Brown v. Mississippi (1936) and the voluntariness test
  - docket line: Objection → Overruled → Convicted → Affirmed
  - Gideon and Escobedo: the law moving around the case
  - the police-manual tactics the Court quoted
  - the four warnings
  - the 5–4 split with White's dissent quote
  - retrial card
  - 1966–2022 timeline, building through Harris (1971) and Quarles (1984)
  - Dickerson's "national culture" line
  - what Miranda costs: Cassell's and Schulhofer's estimates
  - the holding
  - what to say: Davis (1994) and the two clear sentences
  - end card

  It also holds the labels and overlays on the 3D.
- `music_cues.py` is the cue sheet. The theme's downbeat lands on the title card and its outro ends with the end card. Public domain acts run in between. *Aase's Death* stops dead after "never tried".
- `theme_preview.py` is the earlier open/close placement test.

```bash
python3 vo.py                    # temp VO (PIPER_VOICE=path/to/en_US-ryan-high.onnx)
python3 edit.py plates           # 3D frames -> 1080p/24 fps plates
python3 edit.py timeline         # timeline + shotlist.csv + captions_temp.srt
python3 edit.py segs             # one clean 1080p clip per beat -> edit/out/segs/
python3 edit.py reel             # story reel: temp VO, theme + acts, -14 LUFS -> edit/out/hoffman_ep02_story_reel.mp4
python3 edit.py lowerthirds      # ProRes 4444 name straps with alpha
```

Accuracy rules baked into the graphics:

- The confession form is recreated as type, not a scan. The highlighted line is the one quoted in the Supreme Court's opinion. Check the full form wording against the record (fact 4).
- The four warnings are marked as a paraphrase. No single official wording exists.
- Every on-screen quote and date was checked against the opinion text on Oct 8 (White's dissent, the manuals line, Dickerson's "national culture" line, the case dates). The confession form's wording outside the highlighted line still needs the record copy.
- The cost estimates use the authors' own figures (Cassell: about 3.8% of all criminal cases; Schulhofer: 0.78–1.1%) and are labeled contested.
- The what-to-say card carries "general information, not legal advice".
- The card sale is "reportedly", per fact 12.
- No victim name, figure or reconstruction anywhere. No violence in the bar scene.
