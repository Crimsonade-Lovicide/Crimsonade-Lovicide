"""Generate shotlist.json and the credit budget for UNBUILT Special No. 3, the Frank Lloyd Wright countdown.

Run: python3 build_shotlist.py
Spoken lines are read from SCRIPT.md by shot ID, so the shot list can't drift from the script.

Prices are what Special No. 1 actually paid (Higgsfield transaction log, 26 Sep 2026):
  Seedance 2.0 at 720p = 4.5 credits/s; Kling 3.0 pro, silent = 1.75 credits/s (5 s = 8.75);
  Nano Banana Pro still = 2; Arthur TTS line = about 0.75 including retakes.

Lessons from Special No. 1, built in here:
  - No pop-ins: a section opens on Hugo's sync shot. It never cuts from an empty plate of the same place to Hugo.
  - No frozen picture: a VO beat longer than ~7 s gets two visuals. Moving clips are 5 s, and they are
    never stretched past about 1.6x in the edit.
  - Sync lines never start or end on "…". Seedance durations are whole seconds, between 4 and 15.
  - Every location names one landmark ("only one …"). Real people are shown from behind, in silhouette
    or as period portraits, never as a close, lifelike face.

New for Special No. 3:
  - Each project's hero clip is made once, for the cold open, and re-used (a different section) in its own
    segment, so the montage costs nothing extra.
  - Numbers that are really diagrams (the height comparison, the stinger's 135 ft vs a mile) are drawn in the
    edit with Pillow, at no credit cost (kind GRAPHIC).
  - Wright himself appears only from behind or in silhouette: porkpie hat, cape, cane.
  - Baghdad: nobody is shown at the palace, and nothing violent. Hugo is never placed in Baghdad.
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# Special No. 3 wardrobe (29 Sep): GPT Image 2.5 edits of the locked hero portrait (7af5b679-…), 0.25 credits for
# both. Both references show the new outfit, so no earlier coat can leak back in.
# Files: host/hugo_wright_portrait.jpg (the closer likeness, listed first) and host/hugo_wright_portrait_alt.jpg
HOST_REFS = ["292cd695-8ce4-4d61-be63-22ab22dc6aee", "8fa8b468-e355-4ee0-8ef0-265058992202"]
VOICE = {"model": "seed_audio", "voice_type": "preset", "voice_id": "30fc8796-ceb6-4a66-b3a7-4a145ef7f346",
         "name": "Arthur"}
PRICE = {"sync_per_s": 4.5, "broll_per_s": 1.75, "still": 2.0, "tts_line": 0.75}
WPS = 2.6

# ---------------------------------------------------------------- looks
MODERN = ("A frame from a high-end streaming documentary series, shot on an ARRI Alexa, natural slightly "
          "desaturated grade, fine film grain, shallow depth of field. No text, no logos, no watermark.")
NIGHT = ("A frame from a high-end streaming documentary series at night, moonlight and warm practical light, "
         "low mist, deep shadows, fine film grain. No text, no logos, no watermark.")
PERIOD = ("A frame from a historical feature film, shot on 35mm film, photoreal, candlelit where indoors, "
          "period-accurate costume and architecture. No readable text, no logos.")
ARCHIVE = ("An authentic black-and-white press photograph of the period, soft focus at the edges, fine grain "
           "and small scratches. No readable text.")
DRAWING = ("An original architect's presentation drawing of the period, ink and watercolour wash on aged cream "
           "paper, fine linework, subtle foxing. No readable lettering.")
ENGRAVING = ("An old engraving, fine cross-hatched linework, sepia ink on aged paper. No readable lettering.")
WRIGHT = ("An original Frank Lloyd Wright studio presentation perspective, coloured pencil and ink on tan tracing "
          "paper, fine ruled linework, soft earthy colours with touches of gold and Cherokee red, generous empty "
          "margins. No readable lettering, no signature.")
DRONE = ("Cinematic drone footage from a high-end documentary series, natural grade, gentle haze, fine grain. "
         "No text, no logos, no watermark.")
PEOPLE = "Any real historical person is seen from behind, in silhouette or far off, never as a close face."

HOST = ("The presenter: exactly the same man as the reference images, same face, hair and stubble, wearing a "
        "dark chocolate-brown wool overcoat, open, over a cream oxford shirt with the collar open, and a "
        "Cherokee-red silk pocket square in the coat's breast pocket.")
SYNC_TAIL = ("He looks into the lens and speaks the exact words of the audio reference in that same voice, lips in "
             "precise sync, dry, warm British delivery. Subtle handheld camera. Quiet location ambience only, "
             "no music, no subtitles.")
MOTION_TAIL = "One continuous shot. Architecture stays rigid and exactly as it is. No morphing, no text appearing."

# ---------------------------------------------------------------- spoken lines from SCRIPT.md
script = open(os.path.join(HERE, "SCRIPT.md")).read()
LINES = {}
for m in re.finditer(r"\*\*\[([A-Z]+\d+v?)\][^\n]*\n> (.+)", script):
    LINES[m.group(1)] = m.group(2)
for m in re.finditer(r"^> (.+?) \[(CO\d)\]$", script, re.M):
    LINES[m.group(2)] = m.group(1)
m = re.search(r"\*\*\[O2\] SYNC\*\*\n> (.+)", script)
LINES["O2"] = m.group(1)


def clean(t):
    return re.sub(r"\s*\(M\)", "", t).strip()


def n_words(t):
    return len(clean(t).replace("—", " ").split())


def vo_secs(t):
    return round(n_words(t) / WPS + 0.35, 1)


shots = []


def sync(sid, seg, setting, look=MODERN, line=None, extra=""):
    line = clean(line or LINES[sid])
    assert not line.startswith("…") and not line.endswith("…"), sid
    secs = min(15, max(4, math.ceil(n_words(line) / WPS + 0.8)))
    shots.append({"id": sid, "segment": seg, "kind": "SYNC", "line": line, "duration_s": secs,
                  "tts": dict(VOICE, prompt=line),
                  "video": {"model": "seedance_2_0", "resolution": "720p", "aspect_ratio": "16:9",
                            "duration": secs, "generate_audio": True,
                            "medias": [{"role": "image", "value": v} for v in HOST_REFS]
                            + [{"role": "audio", "value": "<tightened TTS media_id>"}],
                            "prompt": f"Documentary presenter piece to camera. {HOST} {setting} {extra} "
                                      f"{SYNC_TAIL} {look}"},
                  "post": "edit/sync_audio.py: keep the clip's own lip-synced audio; patch wrong words from the TTS take."})


def broll(sid, seg, look, image_prompt, motion, vo_id=None, secs=5):
    shots.append({"id": sid, "segment": seg, "kind": "BROLL_VIDEO", "vo_id": vo_id, "duration_s": secs,
                  "start_frame": {"model": "nano_banana_pro", "aspect_ratio": "16:9",
                                  "prompt": f"{look} {image_prompt} {PEOPLE}"},
                  "video": {"model": "kling3_0", "mode": "pro", "sound": "off", "aspect_ratio": "16:9",
                            "duration": secs, "medias": [{"role": "start_image", "value": "<start_frame job_id>"}],
                            "prompt": f"{motion} {MOTION_TAIL}"}})


def still(sid, seg, look, image_prompt, vo_id=None, move="slow push-in"):
    shots.append({"id": sid, "segment": seg, "kind": "STILL", "vo_id": vo_id,
                  "image": {"model": "nano_banana_pro", "aspect_ratio": "16:9",
                            "prompt": f"{look} {image_prompt} {PEOPLE}"},
                  "post": f"ffmpeg zoompan: {move} across the whole beat (no generation cost)"})


def reuse(sid, seg, of, vo_id=None, note=""):
    shots.append({"id": sid, "segment": seg, "kind": "REUSE", "of": of, "vo_id": vo_id,
                  "post": f"Re-use {of}{': ' + note if note else ''} (no generation cost)"})


def card(sid, seg, text, secs=3.0):
    shots.append({"id": sid, "segment": seg, "kind": "CARD", "text": text, "duration_s": secs,
                  "post": "Pillow-rendered card (no generation cost)"})


def graphic(sid, seg, text, vo_id=None):
    shots.append({"id": sid, "segment": seg, "kind": "GRAPHIC", "text": text, "vo_id": vo_id,
                  "post": "Pillow-drawn graphic in the edit (no generation cost)"})


WRIGHT_FIG = ("Frank Lloyd Wright seen only from behind or in silhouette: an elderly man in a flat-brimmed porkpie "
              "hat and a long cape, holding a cane.")
TALIESIN = ("The drafting room at Taliesin West in the Arizona desert: low walls of rough desert stone set in "
            "concrete, redwood beams under a translucent white canvas roof glowing with daylight, long drafting "
            "tables, architectural drawings pinned to the walls, and through the open end only one view, the "
            "McDowell Mountains.")
GUGGENHEIM = ("Fifth Avenue, New York, on a bright autumn day: behind him only one building, the white concrete "
              "spiral of the Solomon R. Guggenheim Museum, widening as it rises, Central Park's trees across the "
              "street.")
POINT = ("Point State Park, Pittsburgh, on a clear evening: behind him only one landmark, the large round "
         "fountain at the tip where two rivers meet, throwing a single tall jet of water, the downtown skyline "
         "beyond.")
ARCHIVE_ROOM = ("A quiet architectural drawings archive: a long oak table under a green-shaded lamp, grey "
                "flat-file cabinets behind, and on the table only one large sheet, a coloured-pencil site plan of "
                "an island in a river.")
ROCKEFELLER = ("Rockefeller Center, New York, in autumn: on the plaza by the flags, and behind him only one tower, "
               "30 Rockefeller Plaza, soaring up in pale limestone.")
LAKEFRONT = ("The Chicago lakefront at dusk from the Museum Campus: Lake Michigan on one side, and behind him the "
             "city skyline, with only one very tall black tower, the Willis Tower.")
LAKEFRONT_NIGHT = LAKEFRONT.replace("at dusk", "at night").replace("the city skyline", "the city skyline, lit")
OBJECTIVE = ("Frank Lloyd Wright's 1925 Automobile Objective on the summit of Sugarloaf Mountain, Maryland: a "
             "massive round stepped ziggurat of warm stone crowning the wooded mountain, a broad ramp spiralling "
             "round its outside with 1920s open motor cars climbing it, a low dome at its heart.")
POINTPARK = ("Frank Lloyd Wright's 1947 Point Park Civic Center at the fork of two rivers in Pittsburgh: a vast "
             "round terraced drum a fifth of a mile across, wrapped in a spiral roadway with 1940s cars climbing "
             "it, roof gardens on its terraces, a slender tower at the river's point.")
OPERA = ("Frank Lloyd Wright's 1957 opera house for Baghdad on an island in the Tigris: a round domed hall under "
         "one great sweeping crescent arch of gold and turquoise, a small golden figure of Aladdin holding a lamp "
         "on the crown of the dome, gardens and fountains in front, palm trees.")
BROADACRE = ("Frank Lloyd Wright's Broadacre City: open countryside laid out in a grid of one-acre plots, small "
             "flat-roofed houses among orchards and fields, small factories, a school, a highway with a flyover, "
             "a few slim towers standing alone in green space, and no downtown at all.")
MILEHIGH = ("Frank Lloyd Wright's 1956 Mile-High Illinois: a single needle-thin tapering skyscraper a mile tall, "
            "triangular in plan like a tripod blade, gold and silver in the sun, rising from the Chicago lakefront "
            "far above every other building, clouds drifting past its middle.")

# ---------------------------------------------------------------- COLD OPEN
S = "Cold open"
broll("CO1", S, DRONE + " Cinematic aerial by day.", MILEHIGH + " The rest of Chicago tiny below.",
      "Slow aerial rise up the tower's side, through the cloud layer, the city dropping away below.", "CO1")
sync("CO2", S, f"{TALIESIN} He stands by a drafting table.", MODERN)
broll("CO3", S, DRONE + " Autumn.", OBJECTIVE,
      "Slow aerial orbit around the summit; the open cars climb the spiral ramp.", "CO3")
broll("CO4", S, DRONE + " Cinematic aerial at dusk.", POINTPARK,
      "Slow aerial push toward the drum across the river, cars' headlights moving up the spiral.", "CO4")
broll("CO5", S, DRONE + " Cinematic aerial at dusk.", OPERA,
      "Slow aerial push toward the crescent arch across the water, the golden figure catching the last light.", "CO5")
broll("CO6", S, DRONE + " Cinematic aerial by day.", BROADACRE,
      "Slow aerial drift over the grid of small farms and houses, a few cars moving on the highway.", "CO6")
sync("CO7", S, f"{TALIESIN} He unpins a large drawing from the wall, rolls it under his arm and turns to go.",
     MODERN)
card("CO8", S, "UNBUILT / Frank Lloyd Wright (sting)", 1.5)

# ---------------------------------------------------------------- No.5 AUTOMOBILE OBJECTIVE
S = "No.5 Automobile Objective"
sync("G1", S, f"{GUGGENHEIM} He stands on the pavement, the spiral filling the frame behind him.", MODERN)
card("G1c", S, "No. 5 · The Automobile Objective · Sugarloaf Mountain, Maryland · 1924 (overlay on G1, 0.3–4.0 s)")
still("G2a", S, DRONE + " Autumn.", "Sugarloaf Mountain, Maryland, from the air: a lone wooded mountain in red and "
      "gold autumn leaves rising from flat farmland, a winding road up its side.", "G2")
still("G2b", S, PERIOD, "1920s Maryland: two open touring cars with their hoods down on a dusty country road "
      "towards a lone wooded mountain, passengers in hats and goggles, seen from behind.", "G2")
reuse("G3a", S, "CO3", "G3", "a different 5 s section")
still("G3b", S, PERIOD, "Inside the Automobile Objective: a great round planetarium hall under a dark dome 150 feet "
      "across, stars projected across it, rows of 1920s visitors seen from behind, looking up.", "G3", "slow tilt up")
still("G4a", S, PERIOD, "1925, a wood-panelled Chicago office: a businessman in a three-piece suit at a big desk, seen "
      "from behind, reading a large architectural drawing of a spiral building.", "G4")
still("G4b", S, ENGRAVING, "The Tower of Babel: a colossal spiralling tower under construction, ramps winding "
      "round its outside, tiny workers and scaffolding, clouds at its top.", "G4")
still("G5a", S, PERIOD + " Night, lamplight.", f"{WRIGHT_FIG} He sits at a drafting table by lamplight, writing a "
      "letter, pencils and T-square around him, a porkpie hat on the table.", "G5")
broll("G5b", S, MODERN + " Night, lamplight.", "Close-up of a garden snail on a stone windowsill at night, its "
      "spiral shell lit from behind by lamplight.", "The snail stretches and glides slowly along the sill.", "G5")
broll("G6a", S, MODERN, "Inside the Solomon R. Guggenheim Museum, New York, looking straight up the white spiral "
      "ramp to the round glass skylight, visitors walking down the ramp, seen from far off.",
      "Slow tilt up the spiral to the skylight.", "G6")
still("G6b", S, WRIGHT, "Two spiral buildings drawn side by side for comparison: on the left a stepped spiral that "
      "narrows as it rises, on the right the same spiral turned upside down so it widens as it rises.", "G6")
sync("G7", S, f"{GUGGENHEIM} He glances up at the spiral, then back to the lens.", MODERN)

# ---------------------------------------------------------------- No.4 PITTSBURGH
S = "No.4 Pittsburgh"
still("P1", S, ARCHIVE, "Pittsburgh in 1935: steel mills and smokestacks along a wide river, the downtown dim in "
      "the haze, a barge in the foreground.", "P1")
card("P1c", S, "No. 4 · The Point Park Civic Center · Pittsburgh · 1947 (overlay on P1, 0.3–4.0 s)")
still("P2a", S, ARCHIVE, "Pittsburgh in the 1940s: a grand downtown department store with a big clock over the "
      "entrance, streetcars and crowds in hats on the street.", "P2")
still("P2b", S, MODERN + " Autumn.", "Fallingwater, the house by Frank Lloyd Wright in the woods of Pennsylvania: "
      "cantilevered cream concrete terraces over a waterfall, autumn leaves.", "P2")
reuse("P3a", S, "CO4", "P3", "a different 5 s section")
still("P3b", S, WRIGHT, "A presentation perspective of a vast round terraced building a fifth of a mile across at "
      "the meeting of two rivers, a spiral roadway wrapped round it, bridges on both sides.", "P3", "slow pull-out")
still("P3c", S, MODERN, "Inside a 1940s aquarium pavilion: large clear glass spheres on bronze stands, each holding "
      "bright fish, river light through tall windows, a child seen from behind looking up.", "P3")
still("P4a", S, PERIOD, "1947, a panelled Pittsburgh boardroom: businessmen in suits round a long table, seen from "
      "behind, looking at an enormous architectural drawing eight feet long.", "P4")
still("P4b", S, PERIOD, "Close on a pencil tapping the edge of a huge coloured-pencil drawing of a spiral building, a "
      "cost ledger beside it.", "P4")
broll("P5a", S, DRONE + " Cinematic aerial at dusk.", "Frank Lloyd Wright's 1948 second plan for Pittsburgh: a "
      "single slender tower about a thousand feet tall at the point where two rivers meet, holding up two long "
      "concrete bridges on fans of cables.", "Slow aerial orbit around the tower, cars crossing the bridges.", "P5")
still("P5b", S, WRIGHT, "A tall presentation perspective of a single slender tower at a river point, fans of cables "
      "reaching down from it to two bridges.", "P5", "slow tilt up")
still("P6", S, DRONE, "Point State Park, Pittsburgh, today from the air: green lawns at the fork of two rivers, a "
      "round fountain throwing a tall jet at the tip, office towers behind.", "P6")
sync("P7", S, f"{POINT} Close-up, a small dry smile.", MODERN)

# ---------------------------------------------------------------- No.3 BAGHDAD
S = "No.3 Baghdad"
still("B1v", S, PERIOD, "Baghdad, May 1957: the wide Tigris at sunset, palm trees along the bank, a four-engine "
      "propeller airliner descending in the distance.", "B1v")
still("B1a", S, ARCHIVE, "Baghdad, 1957: a broad new boulevard under construction, cranes and scaffolding, 1950s "
      "cars, palm trees.", "B1")
reuse("B1b", S, "B2c", "B1", "its first seconds, a slow push in")
card("B1c", S, "No. 3 · The Plan for Greater Baghdad · Baghdad · 1957 (overlay on B1v, 0.3–4.0 s)")
still("B2a", S, DRONE, "A low, wild, flat island in the middle of a wide brown river, reeds and scrub, palm "
      "groves on the far bank, 1950s, no buildings.", "B2")
still("B2b", S, MODERN, "A wild boar standing among tall reeds on a riverbank at dawn, mist on the water.", "B2")
still("B2c", S, WRIGHT, "A site plan of a long island in a river, with round buildings, gardens, fountains and a "
      "long central esplanade.", "B2")
reuse("B3a", S, "CO5", "B3", "a different 5 s section")
broll("B3b", S, DRONE + " Cinematic aerial at dusk.", "At the far end of a river island, a colossal gilded statue "
      "of a caliph in robes standing on a tall spiral stepped tower, about three hundred feet in all, over palm "
      "gardens.", "Slow aerial rise up the spiral tower to the golden statue.", "B3")
still("B3c", S, MODERN, "Close on the crown of a dome: a small golden figure of Aladdin holding up a lamp against "
      "a deep blue evening sky.", "B3")
still("B4a", S, WRIGHT, "A circular university campus plan: rings of buildings round a central tower, ringed "
      "outside by terraces of parked cars, beside a bend in a river.", "B4")
still("B4b", S, ARCHIVE, "Baghdad, 1957: a wide empty plain in a bend of the Tigris, surveyors with a tripod, seen "
      "from far off.", "B4")
sync("B5", S, f"{ARCHIVE_ROOM} He taps the margin of the drawing.", MODERN)
reuse("B6a", S, "B2c", "B6", "slow push across the drawing, music out")
still("B6b", S, MODERN, "An empty palace courtyard at dawn in grey light, arcades and a dry fountain, nobody "
      "there.", "B6")
still("B7a", S, MODERN, "The Tigris at dusk from the bank, the long low island a dark line in the water, city lights "
      "coming on beyond.", "B7")
still("B7b", S, MODERN, "An archive flat-file drawer pulled open under soft light, large coloured-pencil drawings "
      "of domes and gardens lying in it.", "B7")
sync("B8", S, f"{ARCHIVE_ROOM} Quiet and still, looking down at the drawing, then up to the lens. Keep the "
     "performance restrained: no smirk.", MODERN)

# ---------------------------------------------------------------- No.2 BROADACRE
S = "No.2 Broadacre City"
sync("A1", S, f"{ROCKEFELLER} He gestures up at the tower.", MODERN)
card("A1c", S, "No. 2 · Broadacre City · Everywhere · 1932 (overlay on A1, 0.3–4.0 s)")
still("A2a", S, ARCHIVE, "Depression-era Manhattan, 1932: a crowded street under an elevated railway, men in hats "
      "and overcoats, smoke and steam.", "A2")
still("A2b", S, PERIOD, "A 1932 cloth-bound book lying on a desk by a window, plain cover, no readable lettering, a "
      "city street map open beside it.", "A2")
still("A3a", S, PERIOD + " Winter light.", "Winter in the Arizona desert, 1935: young architecture apprentices in "
      "shirtsleeves building a huge square model landscape on trestles outdoors, seen from behind, saguaro cactus "
      "beyond.", "A3")
still("A3b", S, MODERN, "A huge square architectural model of a whole landscape of small farms, houses and roads, "
      "seen from above under gallery lights.", "A3")
reuse("A4a", S, "CO6", "A4", "a different 5 s section")
still("A4b", S, MODERN, "Close on an architectural model: a tiny highway flyover with tiny cars, little farms and "
      "orchards around it, shallow depth of field.", "A4")
still("A5a", S, DRONE, "American suburbs from the air: curving cul-de-sacs, rows of houses on big lawns, a highway "
      "running through, a car on every drive.", "A5")
still("A5b", S, PERIOD, "A 1950s single-storey ranch house on a wide lawn, a two-tone car in the drive, a white "
      "picket fence.", "A5")
sync("A6", S, f"{ROCKEFELLER} He looks up at the tower, then back to the lens.", MODERN)

# ---------------------------------------------------------------- No.1 MILE-HIGH
S = "No.1 Mile-High Illinois"
sync("M1", S, f"{LAKEFRONT} He stands with the skyline behind him.", MODERN)
card("M1c", S, "No. 1 · The Mile-High Illinois · Chicago · 1956 (overlay on M1, 0.3–4.0 s)")
reuse("M2a", S, "CO1", "M2", "a different 5 s section")
still("M2b", S, DRONE, "Halfway up a needle-thin mile-high skyscraper: a helicopter landing deck cantilevered from "
      "its side, 1950s helicopters circling it, Lake Michigan far below.", "M2")
still("M3a", S, ARCHIVE, f"16 October 1956, a grand Chicago hotel ballroom: an enormous drawing of a needle-thin "
      f"skyscraper hung floor to ceiling, press photographers with flashbulbs, a crowd in suits. {WRIGHT_FIG} He "
      "stands before the drawing.", "M3")
still("M3b", S, ARCHIVE, "1956: a crowd in a hotel ballroom applauding, looking up at a giant drawing, seen from "
      "behind.", "M3")
broll("M4a", S, DRONE, BROADACRE + " A long shadow of a needle-thin tower falls across the fields.",
      "The tower's shadow sweeps slowly across the small farms as the sun moves.", "M4")
still("M4b", S, ARCHIVE, "A 1956 Chicago newspaper folded on a desk, a large photograph of a needle-thin tower on the "
      "front page, headlines too small to read.", "M4")
broll("M5a", S, MODERN, "A cutaway of a skyscraper's core: tall elevator cabs, each five storeys high, stacked and "
      "racing up rails side by side, lit from inside.", "The cabs race upwards past each other.", "M5")
still("M5b", S, MODERN, "A vast skyscraper lobby packed with office workers queueing at a bank of elevator doors, "
      "seen from above.", "M5")
broll("M6a", S, DRONE, "Dubai at dawn: the Burj Khalifa rising far above the city, pale light on its steps.",
      "Slow aerial rise alongside the tower towards its spire.", "M6")
graphic("M6b", S, "Height comparison drawn to scale as silhouettes: Empire State Building 381 m (roof), Burj "
        "Khalifa 828 m, the Mile-High Illinois 1,609 m (5,280 ft).", "M6")
sync("M7", S, f"{LAKEFRONT_NIGHT} Close-up, a small smile.", NIGHT)

# ---------------------------------------------------------------- OUTRO
S = "Outro"
sync("O1", S, f"{TALIESIN} In late afternoon light, he unrolls the large drawing across a drafting table.", MODERN)
sync("O2", S, f"{TALIESIN} In late afternoon light. Close-up, a small wry smile.", MODERN)
card("END", S, "UNBUILT (end screen: the full Mile-High episode, subscribe)", 3.0)
still("X1a", "Stinger", WRIGHT, "Washington, 1940: a cluster of tall glass-and-bronze towers rising above a leafy "
      "hillside of old rooftops, terraces and gardens between them.", "X1")
still("X1b", "Stinger", PERIOD, "1940, a government office: a clerk's hand bringing down a rubber stamp on a thick "
      "file, no readable lettering.", "X1")
graphic("X1c", "Stinger", "Two silhouettes to scale: 135 ft (the refused towers) beside 5,280 ft (the Mile-High), "
        "the first barely a sliver at the foot of the second.", "X1")

# ---------------------------------------------------------------- timing and budget
vo_len = {k: vo_secs(v) for k, v in LINES.items()}
cost = {"sync_video": 0.0, "broll_video": 0.0, "stills_and_frames": 0.0, "tts": 0.0}
issues = []
for s in shots:
    k = s["kind"]
    if k == "SYNC":
        cost["sync_video"] += PRICE["sync_per_s"] * s["duration_s"]
        cost["tts"] += PRICE["tts_line"]
    elif k == "BROLL_VIDEO":
        cost["broll_video"] += PRICE["broll_per_s"] * s["duration_s"]
        cost["stills_and_frames"] += PRICE["still"]
    elif k == "STILL":
        cost["stills_and_frames"] += PRICE["still"]
vo_ids = sorted({s["vo_id"] for s in shots if s.get("vo_id")})
cost["tts"] += PRICE["tts_line"] * len(vo_ids)
for v in vo_ids:  # visuals per VO beat: a moving clip must not be stretched past ~1.6x
    parts = [s for s in shots if s.get("vo_id") == v]
    per = vo_len[v] / len(parts)
    for p in parts:
        p["planned_s"] = round(per, 1)
        if p["kind"] in ("BROLL_VIDEO", "REUSE") and per > 5 * 1.6:
            issues.append(f"{p['id']}: {per:.1f}s on a 5s clip")
subtotal = sum(cost.values())
contingency = round(0.15 * (cost["sync_video"] + cost["broll_video"]), 1)
sync_s = sum(s["duration_s"] for s in shots if s["kind"] == "SYNC")
budget = {k: round(v, 1) for k, v in cost.items()}
budget.update({"retakes_15pct_of_video": contingency, "total": round(subtotal + contingency, 1),
               "sync_seconds": sync_s, "vo_seconds": round(sum(vo_len[v] for v in vo_ids), 1),
               "counts": {k: sum(1 for s in shots if s["kind"] == k)
                          for k in ["SYNC", "BROLL_VIDEO", "STILL", "REUSE", "CARD", "GRAPHIC"]},
               "stretch_warnings": issues})
# Lean fallback, if the top-up is small: four more of Hugo's lines become voice-over over free re-uses.
# Each keeps its TTS line; only the Seedance seconds (and their 15% retake allowance) go.
LEAN = {"CO2": "over re-uses of P2b (Fallingwater) and G6a (the Guggenheim), his built work",
        "B8": "over a re-use of B7b, the archive drawer",
        "A6": "over a re-use of A3b, the Broadacre model",
        "O1": "over a re-use montage of the five hero clips, CO3, CO4, CO5, CO6, CO1"}
lean_save = sum(PRICE["sync_per_s"] * s["duration_s"] * 1.15 for s in shots if s["id"] in LEAN)
budget["lean"] = {"voice_over_instead": LEAN, "saves": round(lean_save, 1),
                  "total": round(budget["total"] - lean_save, 1),
                  "sync_seconds": sync_s - sum(s["duration_s"] for s in shots if s["id"] in LEAN)}
json.dump({"episode": "UNBUILT Special No. 3 - Frank Lloyd Wright",
           "youtube_title": "Frank Lloyd Wright's 5 Wildest Buildings That Were Never Built",
           "host_refs": HOST_REFS, "voice": VOICE, "prices": PRICE, "budget": budget, "shots": shots},
          open(os.path.join(HERE, "shotlist.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(budget, indent=2))

# ---------------------------------------------------------------- readable shot list
LOOKS = [MODERN, NIGHT, PERIOD, ARCHIVE, DRAWING, ENGRAVING, WRIGHT, DRONE, PEOPLE, MOTION_TAIL, SYNC_TAIL, HOST,
         "Documentary presenter piece to camera.", " Cinematic aerial at dusk.", " Cinematic aerial by day.",
         " A lone gas lamp in the foreground.", " Night, lamplight.", " Daylight, 1830s.", " Lantern light.",
         " Autumn.", " Winter light.", " Candlelight."]


def brief(t):
    for l in LOOKS:
        t = t.replace(l, "")
    return re.sub(r"\s+", " ", t).strip()


LABEL = {"SYNC": "Hugo on camera", "BROLL_VIDEO": "Moving shot", "STILL": "Still, animated in the edit",
         "REUSE": "Re-use (free)", "CARD": "Title card (free)",
         "GRAPHIC": "Graphic, drawn in the edit (free)"}
out = ["# Shot list: Special No. 3, Frank Lloyd Wright", "",
       "Generated by `build_shotlist.py` from `SCRIPT.md`. The full generation prompts are in `shotlist.json`.", "",
       f"**Estimated cost: about {budget['total']:.0f} credits**, which includes "
       f"{budget['retakes_15pct_of_video']:.0f} for retakes. That breaks down as:",
       f"- Hugo on camera: {budget['sync_video']:.0f}",
       f"- Moving shots: {budget['broll_video']:.0f}",
       f"- Stills and start frames: {budget['stills_and_frames']:.0f}",
       f"- Voice: {budget['tts']:.0f}", "",
       f"**Counts:** Hugo on camera for {budget['sync_seconds']} s in {budget['counts']['SYNC']} shots. "
       f"There are {budget['counts']['BROLL_VIDEO']} moving shots, {budget['counts']['STILL']} stills, "
       f"{budget['counts']['REUSE']} re-uses, {budget['counts']['GRAPHIC']} graphics and "
       f"{budget['counts']['CARD']} cards.", "",
       f"**Lean fallback: about {budget['lean']['total']:.0f} credits.** Four more of Hugo's lines become voice-over "
       f"over free re-uses, which leaves him on camera for {budget['lean']['sync_seconds']} s:"] + \
      [f"- {k} {v}" for k, v in LEAN.items()] + [""]
seg = None
for s in shots:
    if s["segment"] != seg:
        seg = s["segment"]
        out += ["", f"## {seg}", "", "| Shot | Type | Length | What we see | Line |", "|---|---|---|---|---|"]
    if s["kind"] == "SYNC":
        what, line, ln = brief(s["video"]["prompt"]), s["line"], f"{s['duration_s']} s"
    elif s["kind"] == "BROLL_VIDEO":
        what = brief(s["start_frame"]["prompt"]) + " *Motion:* " + brief(s["video"]["prompt"])
        line, ln = clean(LINES.get(s["vo_id"], "")), f"{s.get('planned_s', 5)} s"
    elif s["kind"] == "STILL":
        what, line, ln = brief(s["image"]["prompt"]) + f" *({s['post'].split(':')[1].split('(')[0].strip()})*", \
            clean(LINES.get(s["vo_id"], "")), f"{s.get('planned_s', '')} s"
    elif s["kind"] == "GRAPHIC":
        what, line, ln = s["text"], clean(LINES.get(s["vo_id"], "")), f"{s.get('planned_s', '')} s"
    elif s["kind"] == "REUSE":
        what, line, ln = s["post"], clean(LINES.get(s["vo_id"], "")), f"{s.get('planned_s', '')} s"
    else:
        what, line, ln = s["text"], "", f"{s['duration_s']} s"
    out.append(f"| {s['id']} | {LABEL[s['kind']]} | {ln} | {what.replace('|', '/')} | {line.replace('|', '/')} |")
open(os.path.join(HERE, "SHOTLIST.md"), "w").write("\n".join(out) + "\n")
