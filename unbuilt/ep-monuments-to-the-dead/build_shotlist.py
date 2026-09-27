"""Generate shotlist.json and the credit budget for UNBUILT Special No. 2, "Monuments to the Dead".

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
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
HOST_REFS = ["7af5b679-6105-40a6-bfbd-c1576bf5f064", "58601a7b-306f-4517-8840-c3589998e0d2"]
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
ENGRAVING = ("An original 1830s steel engraving, fine cross-hatched linework, sepia ink on aged paper. "
             "No readable lettering.")
PEOPLE = "Any real historical person is seen from behind, in silhouette or far off, never as a close face."

HOST = ("The presenter: exactly the same man as the reference images, same face, hair and stubble, wearing his "
        "charcoal herringbone double-breasted overcoat open over a navy crewneck with a white T-shirt neckline showing.")
SYNC_TAIL = ("He looks into the lens and speaks the exact words of the audio reference in that same voice, lips in "
             "precise sync, dry deadpan British delivery. Subtle handheld camera. Quiet location ambience only, "
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


CEMETERY = ("A Victorian London cemetery at night in the 1840s style: leaning headstones, a stone angel, ivy, "
            "Gothic tombs, thin ground fog between the graves, bare trees against a moonlit sky.")
CRYPT = ("The Crypt of the United States Capitol: a round hall of forty sturdy sandstone Doric columns under low "
         "groin vaults, a small white marble compass star set in the centre of the floor, warm museum light.")
QUIRE = ("The quire of St George's Chapel, Windsor Castle: Gothic fan-vaulted stone ceiling, carved oak "
         "stalls, the knights' coloured banners hanging above, a plain black marble slab set in the floor.")
RECOLETA_PLAZA = ("A park plaza in the Recoleta district of Buenos Aires at dusk: jacaranda and palo borracho "
                  "trees, and behind them only one building, the brutalist concrete National Library raised on "
                  "massive piers.")
RECOLETA_GATE = ("The neoclassical entrance of the Recoleta Cemetery, Buenos Aires, at night: a portico of four "
                 "Doric columns with a pediment, iron gates, marble mausoleums visible beyond, lamps glowing.")
ABBEY = ("The nave of Westminster Abbey at the choir screen, and against it the white and grey marble monument "
         "of Isaac Newton: a reclining figure on a sarcophagus beneath a large carved stone celestial globe.")
PRIMROSE = ("The grassy summit of Primrose Hill, London, at dusk: the wide view over Regent's Park to the city "
            "skyline, with only one dome, St Paul's Cathedral, small and distinct in the far distance, a few "
            "Victorian lamp posts on the path.")
PRIMROSE_NIGHT = PRIMROSE.replace("at dusk", "at night").replace("a few Victorian lamp posts on the path",
                                                                "the city lights spread out below, one lamp post glowing beside him")
PYRAMID = ("A colossal stepped pyramid of dark brick faced with pale granite, about 270 metres square at the base "
           "and taller than any building in London, rising in 94 narrow terraces to a slender obelisk at the "
           "summit, standing on Primrose Hill above Regent's Park.")
SPHERE = ("Étienne-Louis Boullée's Cenotaph for Newton: a perfectly smooth colossal stone sphere about 150 metres "
          "across, half-set into a massive circular stepped drum, rings of tall dark cypress trees on its terraces, "
          "tiny human figures at the base for scale.")
DESCAMISADO = ("The Monumento al Descamisado as designed in the 1950s: a colossal marble statue of a shirtless "
               "male worker, arms at his sides, standing on a tall stepped circular temple base, about 137 metres "
               "in all, towering over the Buenos Aires skyline and the Río de la Plata.")

# ---------------------------------------------------------------- COLD OPEN
sync("CO1", "Cold open", f"{CEMETERY} He stands among the graves holding an old brass lantern, which lights his face.",
     NIGHT)
still("CO2", "Cold open", NIGHT, "A small bare stone burial chamber deep under a building, an empty rectangular "
      "stone niche, a single candle on the floor, cobwebs, nobody there.", "CO2")
still("CO3", "Cold open", DRAWING, "Christopher Wren's 1678 design for a royal mausoleum: a domed rotunda ringed with "
      "Corinthian columns, a lantern on the dome crowned by a gilded statue of Fame, elevation view.", "CO3")
broll("CO4", "Cold open", MODERN + " Cinematic aerial at dusk.", DESCAMISADO,
      "Slow aerial push toward the colossal statue from across the river at dusk, city lights coming on below.", "CO4")
broll("CO5", "Cold open", NIGHT, SPHERE + " At night, under a starry sky.",
      "Slow aerial drift around the colossal sphere at night, the cypress trees swaying slightly.", "CO5")
broll("CO6", "Cold open", NIGHT + " A lone gas lamp in the foreground.", PYRAMID + " At night in fog, 1830s London "
      "lights below.", "Slow aerial rise over the fog toward the pyramid, a few lit windows on its terraces.", "CO6")
sync("CO7", "Cold open", f"{CEMETERY} Medium shot; he raises the lantern slightly on the last word, then turns "
     "and starts to walk away between the graves.", NIGHT)
card("CO8", "Cold open", "UNBUILT / Monuments to the Dead", 4.0)

# ---------------------------------------------------------------- No.5 WASHINGTON
S = "No.5 Washington"
sync("W1", S, f"{CRYPT} He stands beside the compass star.", MODERN)
card("W1c", S, "No. 5 · Washington's Empty Tomb · Washington, D.C. · 1799 (overlay on W1, 0.3–4.0 s)")
broll("W2a", S, PERIOD, "December 1799, a Virginia study at night: a woman's hand in a black mourning sleeve "
      "presses a seal into black wax on a folded letter, a quill and candle beside it.",
      "The hand presses the seal into the black wax and lifts it away; the candle flame flickers.", "W2")
still("W2b", S, PERIOD, "Mount Vernon, the white wooden mansion with its long columned porch, in winter snow at dusk, "
      "a single lit window, bare trees.", "W2")
still("W3a", S, DRAWING, "A section drawing through the United States Capitol, c. 1820s: the domed Rotunda at the top, "
      "the columned Crypt below it, and a small tomb chamber at the very bottom, all stacked on one axis, with a round "
      "opening in the Rotunda floor lining them up.", "W3", "slow tilt down")
broll("W3b", S, PERIOD, "The United States Capitol Rotunda in the 1820s, looking down through a round open hole, ten "
      "feet across, in the stone floor, into the dim columned crypt below, candlelight far down.",
      "Slow push toward the edge of the hole, looking down into the crypt; dust drifts in a draught.", "W3")
broll("W4", S, PERIOD, "The Capitol Rotunda floor in 1828: two masons in shirtsleeves lay stone slabs across the round "
      "opening, candles on the floor bending in a draught.",
      "The masons slide a heavy slab into place over the hole; the candle flames bend sideways in the draught.", "W4")
still("W5", S, MODERN, "The old tomb at Mount Vernon, Virginia: a low brick vault with an arched iron gate, set into a "
      "grassy slope under trees, overcast autumn light, fallen leaves.", "W5")
broll("W6a", S, PERIOD, "April 1865, the Capitol: four workmen carry a long rough pine platform draped in black cloth "
      "down a narrow stone stair into a dark vault, seen from behind, one carrying a lantern.",
      "The men carry the black-draped platform slowly down the stair into the darkness.", "W6")
still("W6b", S, NIGHT, "A small bare stone burial chamber, empty except for a long low wooden platform draped in black "
      "cloth, lit by one hanging lamp.", "W6")
reuse("W7v", S, "W6b", "W7v", "slow push-in continues")
sync("W7", S, f"{CRYPT} He looks down at the compass star, then up into the lens.", MODERN)

# ---------------------------------------------------------------- No.4 CHARLES I
S = "No.4 Charles I"
still("C1v", S, PERIOD + " Winter light.", "Whitehall, London, 30 January 1649: a black-draped wooden scaffold "
      "outside the classical Banqueting House, a silent crowd in the foreground seen from behind, soldiers, frost.",
      "C1v")
sync("C1", S, f"{QUIRE} He stands beside the black marble slab.", MODERN)
card("C1c", S, "No. 4 · A Mausoleum for Charles I · Windsor · 1678 (overlay on C1, 0.3–4.0 s)")
broll("C2a", S, PERIOD, "The House of Commons in 1678, lit by candles: tiers of benches crowded with Members in wigs "
      "and dark coats, seen from the back of the chamber, the Speaker's chair far off, a clerk writing at the table.",
      "Slow push down the chamber; Members rise and murmur; the clerk's quill moves.", "C2")
still("C2b", S, PERIOD, "Close on a clerk's hand writing in a large leather-bound journal by candlelight, 1678, "
      "the ink still wet, the words too small to read.", "C2")
still("C3a", S, DRAWING, "Christopher Wren's 1678 design for Charles I's mausoleum at Windsor: section through a domed "
      "rotunda, a ring of Corinthian columns outside, a gilt brass statue of Fame on the lantern, a statue group of "
      "four standing Virtues under the dome.", "C3", "slow tilt up")
broll("C3b", S, PERIOD, "The interior of Wren's royal mausoleum as if completed: a tall domed rotunda of white marble, "
      "gilt brass figures in niches, light from the lantern falling on an empty tomb in the centre.",
      "Slow crane up from the empty tomb toward the lantern of the dome.", "C3")
still("C4", S, PERIOD, "1678, a candlelit Whitehall office: ministers in wigs arguing over a table covered in papers "
      "and maps of France, seen from the side.", "C4")
still("C5", S, PERIOD, "A dusty candlelit archive: a roll of large architectural drawings tied with a faded ribbon, "
      "pushed to the back of a high shelf crowded with other rolls, cobwebs.", "C5", "slow push-in")
still("C6a", S, MODERN, "The Albert Memorial Chapel, Windsor Castle: a tall Gothic chapel with a glittering gold mosaic "
      "vaulted ceiling, inlaid marble walls, an empty east end, soft light.", "C6")
still("C6b", S, MODERN, "The crypt of St Paul's Cathedral, London: a massive polished black marble sarcophagus on a "
      "granite pedestal, under a low domed vault, dim warm light.", "C6", "slow pull-out")
still("C7v", S, MODERN + " Candlelight.", "Close insert: a plain black marble slab set into the stone floor of a "
      "Gothic chapel quire, worn smooth, candlelight across it, lettering too worn to read.", "C7v")
sync("C7", S, f"{QUIRE} He looks down at the slab, then back into the lens.", MODERN)

# ---------------------------------------------------------------- No.3 EVITA (played straight)
S = "No.3 Evita"
still("P1v", S, ARCHIVE, "Buenos Aires, 1952: the domed Palace of the Argentine National Congress across a wide "
      "plaza, cars and pedestrians of the period.", "P1v")
sync("P1", S, f"{RECOLETA_PLAZA} Serious, quiet delivery.", MODERN,
     extra="Keep the performance restrained and respectful: no smirk.")
card("P1c", S, "No. 3 · A Monument for Evita · Buenos Aires · 1952 (overlay on P1, 0.3–4.0 s)")
reuse("P2a", S, "CO4", "P2", "a different 5 s section, graded warmer")
still("P2b", S, DRAWING.replace("of the period", "from the early 1950s"), "A cutaway section of the Monumento al "
      "Descamisado: the colossal statue above, a circular temple of many floors with lifts, and deep below, a round "
      "crypt with a silver sarcophagus at its centre.", "P2", "slow tilt down")
still("P3", S, ARCHIVE, "Buenos Aires, July 1952: an enormous silent crowd in mourning fills a wide avenue in the rain, "
      "seen from behind and above, black drapes on the buildings, candles.", "P3")
still("P4a", S, ARCHIVE, "Buenos Aires, April 1955: a large construction site on a riverside avenue, workers pouring "
      "the first concrete for a huge circular foundation, cranes.", "P4")
still("P4b", S, ARCHIVE, "Buenos Aires, September 1955: tanks on a wide avenue, soldiers beside them, a fenced-off "
      "building site in the background.", "P4")
still("P4c", S, MODERN, "A colossal carved marble figure lying half-submerged in a murky brown river among reeds, "
      "only its shoulder and arm above the water.", "P4")
broll("P5a", S, NIGHT, "The Recoleta Cemetery, Buenos Aires, at night: a long avenue of ornate marble mausoleums, "
      "angels and domes, lamps glowing, a cat on a step.", "Slow dolly forward along the avenue of mausoleums.", "P5")
still("P5b", S, NIGHT, "A family vault in the Recoleta Cemetery: a dark polished granite facade with bronze plaques "
      "and a narrow door, fresh flowers tucked into the bronze railings.", "P5")
reuse("P6v", S, "CO4", "P6v", "its last 3 s, dusk grade")
sync("P6", S, f"{RECOLETA_GATE} Quiet, still, serious.", NIGHT,
     extra="Keep the performance restrained and respectful: no smirk.")

# ---------------------------------------------------------------- No.2 NEWTON
S = "No.2 Newton"
sync("N1", S, f"{ABBEY} He stands in front of the monument.", MODERN)
card("N1c", S, "No. 2 · The Cenotaph for Newton · Paris · 1784 (overlay on N1, 0.3–4.0 s)")
still("N2a", S, DRAWING.replace("of the period", "by Étienne-Louis Boullée, 1784"), SPHERE + " Elevation view.", "N2")
broll("N2b", S, MODERN + " Cinematic aerial by day.", SPHERE + " In daylight, a pale sky.",
      "Slow aerial push toward the colossal sphere over the cypress rings.", "N2")
broll("N3a", S, NIGHT.replace("at night", "inside a vast dark dome"), "Inside the colossal hollow sphere by day: "
      "total darkness pierced by thousands of tiny holes that shine like stars across the curved vault; far below, "
      "a small sarcophagus on a raised platform, a single tiny figure beside it.",
      "Slow tilt down from the star-pierced vault to the tiny sarcophagus far below.", "N3")
broll("N3b", S, NIGHT.replace("at night", "inside a vast dome"), "Inside the colossal hollow sphere at night: a great "
      "lamp hung at the centre blazes like a sun and lights the whole curved interior; a small sarcophagus below.",
      "The great lamp glows brighter, light washing across the curved walls.", "N3")
still("N4a", S, PERIOD, "Paris, 1780s: an architect at a candlelit desk, seen from behind, drawing a colossal sphere on "
      "a large sheet, instruments and ink around him.", "N4")
still("N4b", S, DRAWING.replace("of the period", "by Étienne-Louis Boullée, 1784"), "A section through the colossal "
      "hollow sphere showing the tiny sarcophagus at the bottom and the vault pierced with stars.", "N4")
sync("N5", S, f"{ABBEY} He glances up at the stone globe, then back to the lens.", MODERN)

# ---------------------------------------------------------------- No.1 PYRAMID
S = "No.1 Pyramid"
sync("Y1", S, f"{PRIMROSE} He stands on the summit with the view behind him.", MODERN)
card("Y1c", S, "No. 1 · Willson's Pyramid · London · 1830 (overlay on Y1, 0.3–4.0 s)")
still("Y2", S, PERIOD + " Night, lamplight.", "An overcrowded 1820s London churchyard at night, gravestones crammed "
      "together, a gravedigger by lantern light digging where an old grave has been opened.", "Y2")
broll("Y3", S, PERIOD + " Daylight, 1830s.", PYRAMID + " In daylight, carriages and figures on the road in "
      "front for scale, 1830s London around it.", "Slow crane up from the road to reveal the full height of the "
      "pyramid.", "Y3")
still("Y3b", S, PERIOD, "The summit of the colossal pyramid: a slender obelisk with a small domed astronomical "
      "observatory, a telescope, London far below in haze.", "Y3", "slow tilt up")
still("Y4a", S, ENGRAVING, "A cutaway section of a colossal stepped pyramid: dozens of floors of small burial "
      "catacombs, gentle ramps rising between them, a vertical shaft in the centre for hoisting coffins.", "Y4",
      "slow tilt up")
broll("Y4b", S, PERIOD + " Lantern light.", "Inside the pyramid: a long vaulted brick gallery lined floor to ceiling "
      "with stacked catacomb niches, a gentle ramp rising into the distance, lanterns.",
      "Slow dolly up the ramp between the endless walls of niches.", "Y4")
still("Y5a", S, ENGRAVING, PYRAMID + " An 1830 engraving as for a prospectus, with the London skyline tiny beside it.",
      "Y5")
still("Y5b", S, ENGRAVING, "A diagram of the pyramid's 94 terraces pulled apart and laid out flat side by side like "
      "sheets of paper, covering a huge area of fields.", "Y5", "slow pull-out")
sync("Y6", S, f"{PRIMROSE} Close-up, one eyebrow raised.", MODERN)
still("Y7a", S, PERIOD, "An 1828 London coffee house: gentlemen in top hats laughing over a newspaper at a table, "
      "pipe smoke, candlelight.", "Y7")
still("Y7b", S, PERIOD, "1830s: a joint-stock company office, a clerk shaking his head over an empty subscription "
      "ledger, rain on the window.", "Y7")
still("Y8", S, MODERN + " Autumn.", "Kensal Green Cemetery, London: a tree-lined avenue of Victorian tombs, stone "
      "angels and ivy, golden autumn leaves.", "Y8")
sync("Y9", S, f"{PRIMROSE_NIGHT}", NIGHT)
reuse("Y9v", S, "CO6", "Y9v", "a different section")

# ---------------------------------------------------------------- OUTRO
S = "Outro"
sync("O1", S, f"{CEMETERY} He walks slowly toward the camera between the graves holding the lantern, stops.", NIGHT)
sync("O2", S, f"{CEMETERY} Close-up, the lantern lighting his face, a small wry smile.", NIGHT)
card("END", S, "UNBUILT", 3.0)
still("X1", "Stinger", "An 1830 coloured lithograph, soft hand colouring on aged paper. No readable lettering.",
      "A proposed Grand National Cemetery on Primrose Hill: a classical Greek temple and a tall monumental column "
      "among formal walks and terraces, London in the distance.", "X1", "slow push-in")

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
                          for k in ["SYNC", "BROLL_VIDEO", "STILL", "REUSE", "CARD"]},
               "stretch_warnings": issues})
json.dump({"episode": "UNBUILT Special No. 2 - Monuments to the Dead",
           "youtube_title": "London Nearly Built a Pyramid for 5 Million Dead (and Other Monuments to the Dead)",
           "host_refs": HOST_REFS, "voice": VOICE, "prices": PRICE, "budget": budget, "shots": shots},
          open(os.path.join(HERE, "shotlist.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(budget, indent=2))

# ---------------------------------------------------------------- readable shot list
LOOKS = [MODERN, NIGHT, PERIOD, ARCHIVE, DRAWING, ENGRAVING, PEOPLE, MOTION_TAIL, SYNC_TAIL, HOST,
         "Documentary presenter piece to camera.", " Cinematic aerial at dusk.", " Cinematic aerial by day.",
         " A lone gas lamp in the foreground.", " Night, lamplight.", " Daylight, 1830s.", " Lantern light.",
         " Autumn.", " Winter light.", " Candlelight."]


def brief(t):
    for l in LOOKS:
        t = t.replace(l, "")
    return re.sub(r"\s+", " ", t).strip()


LABEL = {"SYNC": "Hugo on camera", "BROLL_VIDEO": "Moving shot", "STILL": "Still, animated in the edit",
         "REUSE": "Re-use (free)", "CARD": "Title card (free)"}
out = ["# Shot list: \"Monuments to the Dead\"", "",
       "Generated by `build_shotlist.py` from `SCRIPT.md`. The full generation prompts are in `shotlist.json`.", "",
       f"**Estimated cost: about {budget['total']:.0f} credits**, which includes "
       f"{budget['retakes_15pct_of_video']:.0f} for retakes. That breaks down as:",
       f"- Hugo on camera: {budget['sync_video']:.0f}",
       f"- Moving shots: {budget['broll_video']:.0f}",
       f"- Stills and start frames: {budget['stills_and_frames']:.0f}",
       f"- Voice: {budget['tts']:.0f}", "",
       f"**Counts:** Hugo on camera for {budget['sync_seconds']} s in {budget['counts']['SYNC']} shots. "
       f"There are {budget['counts']['BROLL_VIDEO']} moving shots, {budget['counts']['STILL']} stills, "
       f"{budget['counts']['REUSE']} re-uses and {budget['counts']['CARD']} cards.", ""]
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
    elif s["kind"] == "REUSE":
        what, line, ln = s["post"], clean(LINES.get(s["vo_id"], "")), f"{s.get('planned_s', '')} s"
    else:
        what, line, ln = s["text"], "", f"{s['duration_s']} s"
    out.append(f"| {s['id']} | {LABEL[s['kind']]} | {ln} | {what.replace('|', '/')} | {line.replace('|', '/')} |")
open(os.path.join(HERE, "SHOTLIST.md"), "w").write("\n".join(out) + "\n")
