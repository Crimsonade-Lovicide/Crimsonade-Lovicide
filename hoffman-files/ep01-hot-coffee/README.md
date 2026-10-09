# The Hoffman Files, Ep. 1: Hot Coffee (Liebeck v. McDonald's)

Everything for episode 1 except Eric's on-camera footage and the guest interviews. That covers the 3D reconstructions, the motion graphics, and a full-length story reel that the shoot footage drops into. The 3D is plain procedural Blender: matte clay figures, with amber for coffee and heat. There is no AI-generated footage and no real person's likeness.

## 3D reconstructions (`blender/`)

| Scene | File | What it shows | Script beat |
|---|---|---|---|
| E1 | `e1_cup.py` | Unbranded paper cup steaming on a dashboard at dawn; slow push-in | Cold open |
| E2 | `e2_car.py` | Generic hatchback, parked | "The car was stopped" |
| E3 | `e3_spill.py` | Faceless figure: cup between the knees, lid pulled toward her, the cup tips. She flinches up and back, then hunches forward pulling at the soaked sweatpants, and the camera closes in on the fabric | The spill, then the sweatpants line |
| E4 | `e4_skin.py` | Skin layers; heat moves through epidermis and dermis to full thickness | Third-degree burns |
| E7 | `e7_folders.py` | 70 folders stack up (1 folder = 10 reports, 700+ reports, 1982–92) | Prior complaints |
| E9 | `e9_clock.py` | 24-hour dial turns twice while a bar fills: two days of coffee sales | The punitive ask |

The E3 arm poses are solved, not eyeballed: `probe_e3.py` searches the shoulder and elbow angles that put the hands where the beat needs them.

## Edit (`edit/`)

- `episode.py` is the edit decision list. It has every beat of the script in order, with Eric's line, the picture, and cue phrases that time the animation to the words.
- `gfx.py` holds the motion graphics:
  - title card
  - headline
  - injuries list
  - thermometer and stopwatch
  - ledger and the $800 offer
  - $500K claims counter
  - quality-assurance testimony card
  - 80/20 fault split
  - punitive cut from $2.7M to $480K
  - settlement card
  - in-memoriam card
  - the holding
  - end card
  - overlays on the 3D shots
  - name straps
- `vo.py` reads every line with a local Piper voice, as a **temporary** guide track for pacing.
- `edit.py` assembles everything:

```bash
python3 vo.py                    # temp VO (PIPER_VOICE=path/to/en_US-ryan-high.onnx)
python3 edit.py plates           # 3D frames -> 1080p/24 fps plates
python3 edit.py timeline         # timeline + shotlist.csv + captions_temp.srt
python3 edit.py segs             # one clean 1080p clip per beat (no temp tags) -> edit/out/segs/
python3 edit.py reel             # story reel with temp VO, score bed, hits -> edit/out/hoffman_ep01_story_reel.mp4
python3 edit.py lowerthirds      # ProRes 4444 name straps with alpha
python3 final_music.py           # story reel with the final music (theme + public domain acts), -14 LUFS
```

Music: the series theme opens (its downbeat lands on the title card) and closes (its outro ends with the end card);
public domain recordings carry the acts. Cue sheet in `edit/music_cues.py`; files and provenance in `../music/`.

Fonts (all SIL Open Font License, free from Google Fonts or IBM) go in `fonts/`: `BebasNeue.ttf`, `PlexMono.ttf` (IBM Plex Mono Regular), `PlexMonoSemi.ttf` (IBM Plex Mono SemiBold) and `Inter.ttf` (variable). You can also point `FONT_DIR` at them.

## Render

Needs `pip install bpy==4.2.* piper-tts scipy pillow numpy` and ffmpeg. The shared Blender helpers come from `documentary-pilots/pipeline/blender/common.py`.

```bash
./render_ep1.sh          # quick look-check renders (960x540, 8 samples, every 2nd frame)
./render_ep1_final.sh    # finals: 1280x720, every frame for E3/E7, every 2nd for the slow shots; ~3 h on 4 CPU cores
./ep1_reel.sh            # labeled review reel of the raw 3D only
```

## Accuracy rules baked into the graphics

- E3 is labeled **Reconstruction**, E4 **Diagram · illustration, not to scale**, and E2 **Illustration · generic car**.
- The flinch in E3 is a natural reaction. Nothing on screen claims that the movement made the burns worse. The documented aggravating factor, the cotton sweatpants holding the coffee against her skin, is stated.
- The ledger itemizes about $18,000 in costs and shows the $20,000 she asked for separately. The items don't sum to $20,000.
- The quality-assurance manager's line is marked as a paraphrase until the transcript gives his exact words.
- The headline card is labeled as a composite. It names no real outlet.
