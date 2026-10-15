# UNBUILT toolkit (v1)

Small Python functions that render the channel's graphics and cut the film together. They take archive scans, Google Earth Studio renders and a human narration, and output H.264 clips at 1920×1080, 24 fps.

```
unbuilt/toolkit/
  unbuilt_kit/     the functions (one module per job, shared plumbing in core.py)
  tests/           python3 -m pytest unbuilt/toolkit/tests -q
  demo.py          renders a ~39 s reel of everything into demo_out/ (gitignored)
  demo_assets/     one public-domain catalogue page + SOURCES.md
  fonts/           the house fonts and their licence
```

## No generative AI

Nothing in this toolkit generates pictures or sound with a model, and no part of an episode made with it should either.

- Every picture is either a real archive item (a scan, an engraving, a newspaper page, with its source recorded) or drawn by this code: lines, type, bars, paper texture.
- Earth Studio footage comes in as rendered frames.
- The voice is a person reading the script.
- Captions come from an SRT written or corrected by hand. There is deliberately no transcription step.

## Requirements

Python 3 with Pillow, NumPy and OpenCV, plus ffmpeg.

ffmpeg is looked up in this order (`unbuilt_kit.core.ffmpeg_exe`):

1. the `FFMPEG` environment variable;
2. the static binary that ships with `pip install imageio-ffmpeg` (`imageio_ffmpeg.get_ffmpeg_exe()`);
3. `ffmpeg` on the PATH.

`probe()` uses `ffprobe` when it sits next to that ffmpeg or on the PATH. imageio-ffmpeg ships no ffprobe, so otherwise `probe()` decodes the file with ffmpeg and counts the frames.

## House style

| | |
|---|---|
| Paper | `#F2EDE4` (with a faint static grain and vignette) |
| Ink | `#1B1B1B` |
| Accent | `#C8102E`, the red pencil |
| Muted | `#6B6B6B` |
| Titles | serif |
| Labels | sans |
| Picture | 1920×1080 at 24 fps; Shorts at 1080×1920 (pass `size=kit.VERTICAL`) |
| Sound | 48 kHz; the final mix is at −14 LUFS and −1 dBTP |
| Motion | cosine ease-in-out only; nothing bounces or overshoots |

Every generator takes `size=` and lays itself out relative to it, so the same call renders a Short.

## Fonts and licences

`fonts/` holds **Liberation Serif** (Regular, Bold, Italic) and **Liberation Sans** (Regular, Bold), under the SIL Open Font License 1.1 (`fonts/LICENSE-Liberation-OFL.txt`).

These are a fallback. The intended faces were Playfair Display or Libre Caslon for the serif, and Inter or IBM Plex Sans for the sans. This build environment could not download them: access to the google/fonts GitHub repository was blocked. The Liberation fonts were already installed on the machine and are OFL too, so they were copied in. DejaVu is the last resort if neither is present.

To switch to the intended faces, drop the static TTFs into `fonts/` and add their OFL.txt beside them. The loader prefers them automatically:

- `PlayfairDisplay-Regular/Bold/Italic.ttf`, or `LibreCaslonText-Regular/Bold/Italic.ttf`;
- `Inter-Regular/Bold.ttf`, or `IBMPlexSans-Regular/Bold.ttf`.

The search order is in `core.py` (`_SERIF`, `_SANS`).

## Usage

```python
import sys; sys.path.insert(0, "unbuilt/toolkit")
import unbuilt_kit as kit
```

Coordinates on images are always **fractions of the image** (0,0 is the top-left). Each function writes one file and returns its path. Videos are H.264, yuv420p, 24 fps, with no audio.

### kenburns: pan and zoom over a still

```python
kit.kenburns("scan.jpg", "out/kb.mp4", 6, start=(0.5, 0.45, 1.0), end=(0.55, 0.3, 1.9))
```

- `start` and `end` are `(cx, cy, zoom)`. `cx` and `cy` are the point of the image to centre on; zoom 1 shows the whole frame.
- The camera interpolates the view rectangle with cosine easing.
- Each frame is sampled with `cv2.warpAffine` (bilinear) at 2× the output size, then area-reduced. Motion is sub-pixel and does not stair-step; the test measures this.
- An image whose aspect is more than 4% off the frame's is fitted on paper with a soft shadow (`bg="paper"` or `"ink"`), so nothing is cropped. Pass `mode="cover"` to fill the frame instead.

### annotate: red-pencil marks drawn on in turn

```python
kit.annotate("scan.jpg", "out/an.mp4", 6.5, marks=[
    {"type": "underline", "from": (0.42, 0.17), "to": (0.69, 0.17)},
    {"type": "ellipse", "center": (0.32, 0.35), "radii": (0.15, 0.055)},   # rx of width, ry of height
    {"type": "circle", "center": (0.5, 0.5), "r": 0.1},                     # r of width
    {"type": "arrow", "from": (0.82, 0.37), "to": (0.60, 0.44)},
    {"type": "label", "text": "First prize, 1890", "pos": (0.66, 0.31), "anchor": "l", "size": 36},
], start=(0.5, 0.36, 1.6), end=(0.5, 0.36, 1.68))
```

- Marks start 0.5 s, 1.5 s, 2.5 s… in. Override per mark with `"at"` and `"dur"`, in seconds.
- Strokes are slightly bowed and wobbly, with a pencil grain. Arrowheads draw after the shaft. Loops overshoot like a hand-drawn circle. Labels wipe on with a paper halo.
- The marks ride along with the gentle `start`/`end` push-in.

### highlight: pick out a passage in a newspaper scan

```python
kit.highlight("newspaper.jpg", "out/hl.mp4", 5.5, box=(0.35, 0.46, 0.65, 0.53))
```

The clip pushes in until the box fills about 60% of the frame (`fill=`). It then dims the rest of the page (`dim=0.45`) and sweeps a translucent red marker across the box.

### scale_compare: heights to one scale

```python
kit.scale_compare("out/sc.mp4", 6.5, [
    {"name": "Watkin's Tower (design)", "height_m": 366, "shape": "taper", "accent": True},
    {"name": "Eiffel Tower", "height_m": 330, "shape": "taper"},
    {"name": "Big Ben", "height_m": 96},                       # plain bar
    {"name": "Wembley arch", "height_m": 133, "shape": "arch"},
    {"name": "Something", "height_m": 200, "silhouette": "outline.png"},
], unit="m", title="Drawn to one scale")
```

- Items are sorted shortest to tallest, and each rises from a shared ground line in turn.
- A height label rides the top and counts up. The name sits under the ground line, and faint gridlines give the scale.
- A silhouette PNG may have alpha, or be dark on light. It is scaled to the item's height and tinted ink, or red with `accent`.

### timeline

```python
kit.timeline("out/tl.mp4", 6.5, [(1889, "Eiffel Tower"), (1890, "Competition"), (1896, "Opened to the public"),
                                  (1907, "Demolished"), (1923, "Empire Stadium"), (2007, "New Wembley")],
             title="Wembley, 1889 to 2007")
```

- The rule draws left to right, and each tick, year and label fades in as the line reaches it. Labels alternate above and below the line.
- With `spacing="auto"` (the default) positions are proportional to the years but nudged apart when crowded. `"proportional"` and `"even"` are also available.

### title_card, end_card

```python
kit.title_card("out/title.mp4", 4, "The Tower at Wembley", "Wembley, 1890 to 1907")
kit.end_card("out/end.mp4", 3.5)                       # text="Sources in the description"
kit.title_card("out/short_title.mp4", 4, "The Tower at Wembley", size=kit.VERTICAL)
```

### lower_third and overlay

```python
kit.lower_third("out/lt.mov", 4, "Sir Edward Watkin", "Railway chairman, 1819 to 1901")   # qtrle with alpha
kit.lower_third("out/lt_frames/", 4, "Sir Edward Watkin")                                # RGBA PNG sequence
kit.overlay("out/kb.mp4", "out/lt.mov", "out/kb_named.mp4", start=1.0)
```

- The lower third renders on transparency: a paper plate with a red edge wipes in, and the text fades up.
- `overlay` keeps the base clip's length and its audio, if it has any.

### quote_card

```python
kit.quote_card("out/q.mp4", 5, "Words from the archive, verbatim.", "Name, Source, 1890")
```

Serif italic on paper. The words fade in line by line, and the attribution follows.

### thumbnail: 1280×720 PNG

```python
kit.thumbnail("out/thumb.png", "newspaper.jpg", overlay_image="engraving.jpg", text="NEVER FINISHED", variant=1)
```

- `variant=1` "dark": a graded, darkened background, light text on the left, and the cut-out with a white glow.
- `variant=2` "paper": a paper ground with the background as a tilted print, ink text, and the cut-out with a shadow.
- `variant=3` "band": a full-bleed background with a red band carrying the text.
- The cut-out (`kit.cutout`) is the real drawing, lifted off its paper with OpenCV:
  1. an Otsu threshold finds the ink;
  2. the shape is closed and its holes filled, so the cut-out keeps the paper inside its outline, like a sticker;
  3. it keeps only the largest pieces.
- `overlay_box=(x0, y0, x1, y1)` places the cut-out. `red_word=` picks the word printed in red. The function warns when the text runs past three words.

### assemble: the cut, with sound

```python
kit.assemble("shotlist.json", "narration.wav", "music.wav", "out/film.mp4", crossfade=0.5)
```

Shot list formats are a JSON file, or a list in Python; a JSON file may also hold `{"shots": [...]}`. Relative paths resolve against the JSON file's folder.

```json
[{"clip": "title.mp4"}, {"clip": "kb.mp4", "duration": 5}, {"clip": "map.png"}]
[{"clip": "title.mp4", "start": 0}, {"clip": "kb.mp4", "start": 4.2, "in": 1.0}]
```

- **Clips laid end to end:** each clip plays its full length, or its `duration`; a still image plays for 4 s. Each clip overlaps the one before it by the dissolve.
- **Clips placed with `start`:** `start` is the moment the clip is fully on screen, and the dissolve runs in the `crossfade` seconds before it. A clip that runs out before the next one starts holds its last frame. `in` trims the head of the source.
- Clips are fitted onto paper at 1920×1080, 24 fps (`size=` to change). With `crossfade=0` the clips cut straight.
- The programme runs for the longer of the picture and the narration.
- **Sound:**
  1. The narration is levelled to −16 LUFS.
  2. The music, which is optional (pass `None`), is levelled, set `music_db` (−14 dB) below the voice, looped to length, and ducked under the voice with `sidechaincompress` (about 13 dB of ducking in the test).
  3. The mix gets a two-pass `loudnorm` to −14 LUFS and −1 dBTP.
  4. It is encoded as AAC at 192 kbps and 48 kHz.

### captions_burn: for Shorts

```python
kit.captions_burn("out/short.mp4", "short.srt", "out/short_captioned.mp4", vertical=True)
```

- The SRT is converted to ASS at the video's own resolution, then burned with libass in the house sans: paper-white bold on a translucent ink box.
- With `vertical=True` the captions are larger and sit about 30% up the frame, clear of the Shorts interface.
- Write or correct the SRT by hand. There is no transcription here.

## Tests and demo

```
python3 -m pytest unbuilt/toolkit/tests -q     # 14 tests, ~15 s
python3 unbuilt/toolkit/demo.py                # ~5 min at 1080p; --quick renders at 960x540
```

**The tests** render every function at 320×180 (and 180×320 for Shorts), then check each output:

- the file exists;
- it has the right size and frame rate;
- it lasts the right number of frames, ±1;
- the lower third has alpha;
- the assembled film has AAC audio at 48 kHz and measures −14 ±1 LUFS;
- the burned captions changed the picture.

The Ken Burns smoothness test pans across a texture and measures every frame-to-frame shift of the encoded mp4 with ECC alignment. It fails if the motion reverses, if it jumps by more than 0.4 px between frames, or if it strays more than 0.25 px from the ideal cosine-eased path. Whole-pixel stepping fails it.

**The demo** writes every clip, the assembled `demo_reel.mp4`, three thumbnails, a captioned Short and `contact.png` (30 frames of the reel) into `demo_out/`. Its audio is a **test signal**: sine tones standing in for the voice and the music, used only to exercise ducking and loudness.

## Known limitations (v1)

- **Fonts:** the fallback Liberation fonts stand in until the intended open fonts are added (see above).
- **Plate resolution:** the zoom plate is capped at 4× the frame and at the source's own resolution. Pushing far into a small scan therefore looks soft rather than sharp.
- **Downscaling:** at large zoom ranges (above 4×) the zoomed-out end is downsampled up to 2:1 bilinear before the area reduction. Keep big moves to two shots.
- **Long cuts:** `assemble` builds one ffmpeg filter graph with every clip as an input. That is fine for a few dozen shots; for a full episode, assemble in sections and join them.
- **Shot length:** a shot list placed by `start` needs each clip to cover its slot plus the dissolve. A clip that falls short holds its last frame.
- **Thumbnails:** the cut-out works on clean line drawings on light paper. On a photograph, or on a scan with heavy foxing, pass `cut_threshold=` or prepare a mask by hand.
- **Render speed:** rendering is single-threaded Python at about 3–6 frames per second at 1080p.
