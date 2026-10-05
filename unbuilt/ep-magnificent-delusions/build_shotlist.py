"""Generate shotlist.json and the credit budget for UNBUILT "Magnificent Delusions".

Run: python3 build_shotlist.py
Prices are Higgsfield preflight quotes taken on 2026-09-26 (get_cost:true):
  nano_banana_pro still = 2, seed_audio line = 0.5,
  seedance_2_0 480p = 3 credits/s (min 4 s), kling3_0 pro silent = 1.75 credits/s (5 s = 8.75).
"""
import json
import math

HOST_ELEMENT = "026bc578-60a2-4cac-92b2-53d3ea1a43d8"
HOST_REFS = ["7af5b679-6105-40a6-bfbd-c1576bf5f064", "58601a7b-306f-4517-8840-c3589998e0d2"]
VOICE = {"model": "seed_audio", "voice_type": "preset", "voice_id": "30fc8796-ceb6-4a66-b3a7-4a145ef7f346", "name": "Arthur"}

PRICE = {"still": 2.0, "tts_line": 0.5, "sync_per_s": 3.0, "broll_per_s": 1.75}
WPS = 2.6  # spoken words per second for timing

MODERN = ("A frame from a high-end streaming documentary series, shot on an ARRI Alexa, natural slightly "
          "desaturated grade, fine film grain, shallow depth of field. No text, no logos, no watermark.")
PERIOD = ("A frame from a historical feature film, shot on 35mm film, photoreal, subtle film grain, "
          "period-accurate costume and architecture. No readable text, no logos.")
ARCHIVE = ("An authentic hand-tinted albumen photograph of the period, soft focus at the edges, "
           "faded colour, fine grain and small scratches. No readable text.")
DRAWING = ("An original architect's presentation drawing of the period, ink and watercolour wash on "
           "aged cream paper, fine linework, subtle foxing. No readable lettering.")
HOST = (f"<<<{HOST_ELEMENT}>>>, the presenter: exactly the same face, hair and stubble as the reference, "
        "wearing his charcoal herringbone double-breasted overcoat open over a navy crewneck with a white "
        "T-shirt neckline showing.")
SYNC_TAIL = ("He looks into the lens and speaks the exact words of the audio reference in that same voice, lips in "
             "precise sync, dry deadpan British delivery. Subtle handheld camera. " + MODERN +
             " Quiet location ambience only, no music, no subtitles.")
MOTION_TAIL = "One continuous shot. Architecture stays rigid and exactly as it is. No morphing, no text appearing."


def words(s):
    return len(s.replace("—", " ").split())


shots = []


def sync(sid, seg, setting, line, extra=""):
    secs = max(4, math.ceil(words(line) / WPS + 0.6))
    shots.append({"id": sid, "segment": seg, "kind": "SYNC", "line": line, "duration_s": secs,
                  "tts": dict(VOICE, prompt=line),
                  "video": {"model": "seedance_2_0", "resolution": "480p", "aspect_ratio": "16:9",
                            "duration": secs, "generate_audio": True,
                            "medias": [{"role": "image_references", "value": v} for v in HOST_REFS]
                            + [{"role": "audio_references", "value": "<TTS media_id>"}],
                            "prompt": f"Documentary presenter piece to camera. {HOST} {setting} {extra} {SYNC_TAIL}"},
                  "post": "Replace the clip audio with the clean TTS take (timing matches); keep ambience bed separately."})


def broll(sid, seg, look, image_prompt, motion, vo="", secs=5):
    shots.append({"id": sid, "segment": seg, "kind": "BROLL_VIDEO", "vo": vo, "duration_s": secs,
                  "start_frame": {"model": "nano_banana_pro", "aspect_ratio": "16:9",
                                  "prompt": f"{look} {image_prompt}"},
                  "video": {"model": "kling3_0", "mode": "pro", "sound": "off", "aspect_ratio": "16:9",
                            "duration": secs, "medias": [{"role": "start_image", "value": "<start_frame job_id>"}],
                            "prompt": f"{motion} {MOTION_TAIL}"}})


def still(sid, seg, look, image_prompt, vo="", secs=6, move="slow push-in"):
    shots.append({"id": sid, "segment": seg, "kind": "STILL", "vo": vo, "duration_s": secs,
                  "image": {"model": "nano_banana_pro", "aspect_ratio": "16:9", "prompt": f"{look} {image_prompt}"},
                  "post": f"ffmpeg zoompan: {move}, subtle grain, no generation cost"})


def card(sid, seg, text, secs=3):
    shots.append({"id": sid, "segment": seg, "kind": "CARD", "text": text, "duration_s": secs,
                  "post": "Pillow-rendered title over the next shot (no generation cost)"})


ELE = ("A colossal elephant statue about 15 metres tall standing on a tall round pedestal in a large open Paris "
       "square, a small ornate tower on its back, the Place de la Bastille, early 19th century.")
PLASTER = ELE + (" The elephant is a full-size PLASTER model over a timber frame, dirty grey, cracked and patched, "
                 "one tusk broken, stained by rain, a rough wooden fence around the pedestal, weeds.")

# ---------------- COLD OPEN ----------------
shots.append({"id": "CO1", "segment": "Cold open", "kind": "SYNC", "duration_s": 5, "status": "RENDERED",
              "line": "Most buildings that never got built… deserved it. These five didn't.",
              "job_id": "c375df58-893c-45e8-ac9b-0ea82d1bf36b",
              "note": "Proof shot. Re-render if you want to fix the duplicated July Column in the background."})
broll("CO2", "Cold open", PERIOD, PLASTER + " 1830s, rain, grey dusk, a few people hurrying past under umbrellas.",
      "Rain falls steadily; a figure hurries past the fence; the camera drifts slowly left.",
      "A monument that became a rat hotel.", 4)
broll("CO3", "Cold open", PERIOD, "1870 New York: inside a round whitewashed brick tunnel lit by gas lamps, a single "
      "cylindrical wooden passenger car with brass fittings and upholstered benches, passengers in Victorian dress.",
      "The car glides slowly forward through the tunnel toward camera; lamplight flickers.", "A subway powered by a giant fan.", 4)
still("CO4", "Cold open", MODERN, "Aerial view of Liverpool at dusk with an immense classical cathedral that never existed "
      "dominating the skyline beside the River Mersey: a vast pale granite and brick body, a colossal ribbed dome "
      "wider than St Peter's in Rome, the real Liver Building small by comparison.", "A cathedral wider than St Peter's.", 3)
broll("CO5", "Cold open", MODERN, "Aerial view of Midtown Manhattan covered by an immense transparent geodesic dome two miles "
      "across, spanning from the Hudson to the East River, its triangular lattice catching the late sun, the Empire "
      "State Building standing inside it.", "Slow helicopter drift toward the dome; sunlight glints across the facets.",
      "A glass lid over Midtown Manhattan.", 4)
broll("CO6", "Cold open", MODERN, "A colossal concrete dam across the Strait of Gibraltar seen from high above, the Atlantic "
      "on the left brimming at the top, the Mediterranean on the right lying about a hundred metres lower, pale newly "
      "exposed seabed along its shores, the Rock of Gibraltar in the background.",
      "Slow aerial push along the dam crest; spray drifts from spillways.",
      "And a man who looked at the Mediterranean Sea and thought… that could come down a bit.", 5)
sync("CO7", "Cold open", "He stands in the Place de la Bastille in Paris at blue hour, a single dark green bronze column "
     "with a small gilded figure on top behind him (only one column), and at the end he turns and walks off out of frame.",
     "I'm Hugo Ashby. Let's go and look at some holes in the ground.")
card("CO8", "Cold open", "UNBUILT · Magnificent Delusions", 4)

# ---------------- No.5 ELEPHANT ----------------
card("E0", "No.5 Elephant", "No. 5 · The Elephant of the Bastille · Paris, 1808")
sync("E1", "No.5 Elephant", "Daytime, walking slowly across the Place de la Bastille in Paris with traffic around, the single "
     "tall dark green bronze July Column behind him, camera walking backwards in front of him.",
     "In 1808, Napoleon decided this square needed a fountain. Being Napoleon… he meant an elephant.")
still("E2", "No.5 Elephant", DRAWING, "Side elevation of a monumental bronze elephant fountain for a Paris square, 1810: the "
      "elephant on a tall circular pedestal with water spouting from its trunk into a round basin, an ornate tower "
      "(howdah) on its back, a tiny human figure for scale.",
      "Twenty-four metres, tower and all. To be cast in bronze from cannon captured at the Battle of Friedland. "
      "A staircase up one leg, a lookout on its back, and water from the trunk.", 10)
broll("E3", "No.5 Elephant", PERIOD, ELE + " 1814: workmen on timber scaffolding finish a full-size white PLASTER model of the "
      "elephant, buckets of plaster, ropes and ladders, overcast morning.",
      "Workmen smooth plaster and climb the ladders; the camera cranes slowly up.",
      "First, a full-size model in plaster, to see how it looked. That was 1814. The following year was Waterloo.")
broll("E4", "No.5 Elephant", PERIOD, PLASTER + " About 1830, steady rain.", "Rain streams down the cracked plaster; slow push-in.",
      "The bronze never came. The plaster stayed, for thirty years. It cracked, it sagged,")
still("E4b", "No.5 Elephant", PERIOD, "Close-up: a brown rat sitting on the cracked grey plaster foot of a colossal elephant "
      "statue, rain, night, a lantern glow.", "and by the late 1820s the neighbours were petitioning to have it removed. "
      "Because of the rats.", 6)
still("E5", "No.5 Elephant", PERIOD, "A small wooden door set into the massive cracked plaster leg of a colossal elephant "
      "statue, ajar, warm lamplight inside, a worn coat hanging on a nail, dusk.",
      "A watchman is said to have lived in one of its legs. Which is not a career they mention at school.", 7)
broll("E6", "No.5 Elephant", PERIOD, PLASTER + " Night, 1832: a thin ragged boy of about eleven squeezes up through a gap "
      "in the plaster under the elephant's belly, faint candle glow inside.",
      "The boy climbs up and disappears inside; candlelight flickers in the gap.",
      "Then Victor Hugo moved a tenant in. In Les Misérables, the street boy Gavroche sleeps inside the elephant.")
still("E6b", "No.5 Elephant", "A 19th-century wood engraving book illustration, fine cross-hatching, black ink on aged paper.",
      "Interior of a hollow plaster elephant at night: a ragged boy and two small children curled under a blanket on "
      "planks, a candle stub, rats in the shadows of the ribs.",
      "\"Ugly in the eyes of the bourgeois,\" Hugo wrote. \"Melancholy in the eyes of the thinker.\"", 7)
still("E7v", "No.5 Elephant", MODERN, "The July Column in the Place de la Bastille, Paris, by day: a single tall dark green bronze column with a small gilded winged figure on top, on a round white stone base, traffic around it.",
      "They knocked it down in 1846 and put up that. The July Column.", 5, "slow tilt up")
sync("E7", "No.5 Elephant", "Medium close-up in the Place de la Bastille by day, the single tall July Column behind him; on "
     "'that' he gestures over his shoulder with his thumb.",
     "Tasteful. Correct. Nobody's ever written a novel about it.")

# ---------------- No.4 BEACH ----------------
card("B0", "No.4 Beach", "No. 4 · Beach Pneumatic Transit · New York, 1870")
broll("B1", "No.4 Beach", ARCHIVE, "Broadway, New York, 1869: the street jammed solid with horse-drawn omnibuses, carts and "
      "carriages, crowds on the sidewalks, cast-iron storefronts.",
      "Carriages inch forward, horses toss their heads, pedestrians weave between them.",
      "New York, 1869. Broadway is so jammed with horses and omnibuses that walking is faster.")
still("B2v", "No.4 Beach", PERIOD, "1869: a cluttered Victorian magazine office in New York, engravings of machines pinned up, a brass pneumatic tube model on the desk, a bearded man in a frock coat seen from behind at the window.",
      "Alfred Ely Beach, publisher of Scientific American, had permission to build a little tube for the mail.", 6)
sync("B2", "No.4 Beach", "Standing on Broadway at Warren Street in Lower Manhattan today, yellow cabs and buses passing, "
     "cast-iron buildings behind.",
     "So, naturally… he built a train.")
broll("B3", "No.4 Beach", PERIOD, "1869, night: under a New York street, a round iron tunnelling shield lit by oil lamps, "
      "workmen with picks and shovels passing buckets of earth back through a brick-lined bore.",
      "Workmen dig and pass buckets; lamps swing; dust hangs in the air.",
      "Working out of the basement of a clothing shop, his men dug under Broadway for fifty-eight nights.")
broll("B4", "No.4 Beach", PERIOD, "1870: a single cylindrical passenger car, painted and upholstered, sitting in a round "
      "whitewashed brick tunnel about eight feet across, lit by bright lamps, Victorian passengers seated.",
      "The car slides smoothly away down the tunnel; passengers' hats and coats sway slightly.",
      "February 1870. One car, twenty-two seats, blown down the tunnel")
still("B4b", "No.4 Beach", PERIOD, "An enormous 1870 industrial rotary blower in a brick basement engine room: huge iron casing, "
      "belts and a steam engine, men in waistcoats dwarfed beside it.",
      "by a fan the size of a locomotive… and then sucked back again.", 4)
broll("B5", "No.4 Beach", PERIOD, "1870: an elegant underground waiting room: frescoed walls, a grand piano, easy chairs, a "
      "fountain with a basin of goldfish, bright lamps, ladies and gentlemen in Victorian dress.",
      "Slow tracking shot past the fountain; goldfish move; a woman sits at the piano.",
      "The waiting room had frescoes, a grand piano and a fountain full of goldfish. Frankly, nicer than most stations in New York today.", 6)
still("B6", "No.4 Beach", ARCHIVE, "1870: a queue of Victorian New Yorkers at a small ticket window at the top of a stair "
      "leading underground, excited faces, top hats and bonnets.",
      "A ride cost a quarter, and the money went to an orphans' charity. Four hundred thousand people rode it in the first year.", 8)
still("B7", "No.4 Beach", PERIOD, "1871: a heavy mahogany desk in a state governor's office in Albany, a quill pen, an "
      "official bill pushed aside, a fat cigar smoking in a brass ashtray, a gloved hand withdrawing. No faces.",
      "To go any further, Beach needed the state's permission. Unfortunately, the state belonged to Boss Tweed. "
      "And Tweed's governor, John T. Hoffman, vetoed the bill. Twice.", 9)
still("B8a", "No.4 Beach", ARCHIVE, "September 1873, Wall Street: a panicked crowd of men in top hats pressing against the "
      "closed doors of a bank.", "Then the crash of 1873 scared off every investor in America.", 4)
broll("B8", "No.4 Beach", PERIOD, "1912: subway construction workers with lanterns break through a brick wall into a forgotten "
      "round tunnel and find the rotting wooden remains of an old passenger car in the dust.",
      "A lantern pushes through the hole; dust swirls; the light finds the old car.",
      "The tunnel was sealed and forgotten, until 1912, when men digging a new subway line broke straight into it… "
      "and found Beach's car. Still waiting.", 7)
still("B9v", "No.4 Beach", ARCHIVE, "October 1904, New York: crowds in straw boaters and long skirts pouring down the tiled stairs of the brand-new subway, bunting.",
      "New York's first real subway opened in 1904. Beach beat it by thirty-four years.", 5)
sync("B9", "No.4 Beach", "At the top of a New York subway entrance near City Hall, commuters passing, green railings.",
     "The reward for being that early, it turns out… is being forgotten.")

# ---------------- No.3 LUTYENS ----------------
card("L0", "No.3 Liverpool", "No. 3 · The Cathedral of Christ the King · Liverpool, 1933")
still("L1v", "No.3 Liverpool", MODERN, "Liverpool Metropolitan Cathedral from the street: the circular 1960s concrete cathedral with its funnel-shaped lantern tower crowned by a ring of spiky pinnacles, wide steps, grey sky.",
      "This is Liverpool's Catholic cathedral. The locals call it Paddy's Wigwam.", 5)
sync("L1", "No.3 Liverpool", "Outside Liverpool Metropolitan Cathedral: the circular modern concrete cathedral with its "
     "funnel-shaped lantern tower crowned by spiky pinnacles, a wide flight of steps, grey sky.",
     "It isn't the one they meant to build. That one's… underneath it.")
still("L2", "No.3 Liverpool", DRAWING, "1930s front elevation of a colossal classical cathedral in brick and pale granite: a "
      "monumental arched west front and an immense ribbed dome on a drum, a small tram and people for scale.",
      "In 1929, Sir Edwin Lutyens, fresh from designing New Delhi, was asked for a cathedral. He drew what was billed as "
      "the second-largest church in the world, with a dome a hundred and sixty-eight feet across. Wider than St Peter's in Rome.", 15)
broll("L3", "No.3 Liverpool", MODERN, "Liverpool at dusk from across the River Mersey: an immense classical cathedral with a "
      "colossal ribbed dome towering over the city, far larger than the real waterfront buildings beside it.",
      "Slow aerial drift across the river toward the dome; ferries cross below.",
      "Lutyens reckoned it would take two hundred years to build. He was, if anything, optimistic.")
still("L4", "No.3 Liverpool", ARCHIVE, "Whit Monday 1933, Liverpool: an enormous crowd around a building site for a foundation "
      "stone ceremony, clergy in robes on a platform, cranes and scaffolding.",
      "The foundation stone went down in 1933. Then came the war. Then came the bill. Three million pounds had become twenty-seven million.", 9)
broll("L5", "No.3 Liverpool", MODERN, "A vast empty crypt with massive round brick vaults and granite piers, soft light from "
      "above, polished stone floor.", "Slow dolly forward through the vaults.",
      "In 1958 they finished the crypt… and stopped. Then built an entirely different cathedral on top.", 6)
sync("L6", "No.3 Liverpool", "Inside a vast crypt of massive round brick vaults and granite piers, soft light, he stands "
     "between two piers.",
     "So this is the basement of the biggest church never built. It's like buying the frame for a painting you can't afford.")
broll("L7", "No.3 Liverpool", MODERN, "A huge detailed wooden architectural model of a domed classical cathedral, about four "
      "metres tall, displayed in a darkened museum gallery under spotlights.",
      "Slow orbit around the model; spotlights glint on the dome.",
      "What survives is the model. Twelve feet tall, made in the thirties, and so intricate it took thirteen years to restore. The model.", 7)

# ---------------- No.2 DOME ----------------
card("D0", "No.2 Dome", "No. 2 · Dome over Manhattan · New York, 1960")
still("D1v", "No.2 Dome", MODERN, "The Midtown Manhattan skyline at golden hour from a rooftop, the Empire State Building in the centre, water towers in the foreground.",
      "From a New Yorker who went under the city, to one who wanted to put a lid on it.", 5)
sync("D1", "No.2 Dome", "On a Midtown Manhattan rooftop in late afternoon, the Empire State Building behind him, wind in his hair.",
     "In 1960, Buckminster Fuller proposed a dome over Midtown Manhattan.")
broll("D2", "No.2 Dome", MODERN, "High aerial of Manhattan: an immense transparent geodesic dome two miles across covers Midtown "
      "from the Hudson to the East River, triangular lattice glinting.", "Slow high aerial orbit.",
      "Two miles across. River to river, roughly Twenty-first Street to Sixty-fourth.")
still("D3", "No.2 Dome", PERIOD, "1960: a drafting table covered in geodesic diagrams, a small white geodesic dome model, "
      "a slide rule and a pencil, two pairs of hands; a window onto Manhattan.",
      "Fuller and his partner Shoji Sadao reckoned sixteen big Sikorsky helicopters could fly the pieces into place in three months.", 8)
broll("D4", "No.2 Dome", ARCHIVE, "Manhattan in a heavy 1960 snowstorm: Fifth Avenue buried, snowploughs and men with shovels, "
      "buses stuck.", "Snow falls; a plough pushes through; people trudge past.",
      "And the clincher: the money New York saved on clearing snow would pay for the whole thing in ten years.")
sync("D5", "No.2 Dome", "Same Midtown rooftop, closer, deadpan.",
     "Which is the most engineer sentence ever spoken. \"Yes, I've put Midtown under glass. But think of the savings on grit.\"")
still("D6", "No.2 Dome", MODERN, "Street level on a Midtown avenue under a colossal geodesic dome: the sky seen through a "
      "vast triangular lattice high above the skyscrapers, a faint haze trapped under it, yellow cabs.",
      "Where the car exhaust would go was never quite resolved. Mostly because there was never a client, or a permit.", 7)
broll("D7", "No.2 Dome", MODERN, "The Montreal Biosphère today: a large transparent geodesic sphere of steel struts on an "
      "island park, autumn trees, the St Lawrence river.", "Slow push toward the sphere; leaves drift.",
      "But a piece of the dream did get built: Fuller and Sadao's pavilion for Expo 67, in Montreal. Still standing. "
      "Rather smaller. Considerably less Manhattan.", 7)

# ---------------- No.1 ATLANTROPA ----------------
card("A0", "No.1 Atlantropa", "No. 1 · Atlantropa · The Mediterranean, 1928")
still("A1v", "No.1 Atlantropa", MODERN, "Aerial of the Rock of Gibraltar and the Strait at golden hour, the mountains of Morocco across the water, ships in the strait.",
      "And so, number one. In 1928, a Munich architect called Herman Sörgel looked at the Mediterranean Sea…", 7)
sync("A1", "No.1 Atlantropa", "On a clifftop on the Rock of Gibraltar, strong wind, the Strait and the coast of Africa behind him.",
     "…and decided there was rather too much of it.")
still("A2", "No.1 Atlantropa", "A 1930s German illustrated propaganda-style map, flat gouache colours, bold graphic style, "
      "no readable lettering.", "The Mediterranean basin with three enormous dams drawn across it — at Gibraltar, between "
      "Sicily and Tunisia, and at the Dardanelles — and the coastlines shown pushed outward with new land in ochre.",
      "His plan: a dam across the Strait of Gibraltar, thirty-five kilometres long. More dams at the Dardanelles, and "
      "between Sicily and Tunisia. Then let evaporation do the work.", 10, "slow pan left to right")
broll("A3", "No.1 Atlantropa", MODERN, "Low aerial along a colossal concrete dam with hydroelectric turbine halls across the "
      "Strait of Gibraltar, the Atlantic high on one side, the Mediterranean far lower on the other.",
      "Water thunders from spillways; slow aerial tracking along the dam.",
      "The western Mediterranean would fall by a hundred metres, the eastern by two hundred.")
still("A3b", "No.1 Atlantropa", MODERN, "Former Mediterranean seabed turned into vast irrigated farmland under hard sun, an old "
      "rusted cargo ship stranded upright in the fields, the new shoreline far away.",
      "Over half a million square kilometres of new land. Hydroelectric power for half of Europe.", 6)
still("A4", "No.1 Atlantropa", MODERN, "Aerial of Venice with its lagoon drained to dry cracked mud flats, gondolas lying on "
      "their sides, a long straight new canal cut across the mud to a sea on the horizon.",
      "Venice would need a canal to reach the sea. Most other ports would simply be left high and dry.", 7)
still("A5", "No.1 Atlantropa", "A 1930s European planning map of Africa, flat gouache colours, no readable lettering.",
      "Africa drawn as blank territory overlaid with arrows from Europe, railway lines and two huge artificial inland "
      "seas flooded in blue in the centre of the continent.",
      "And Africa? In Sörgel's plans, it was a blank space to be flooded, farmed and run for Europe. Nobody thought to ask the people who lived there.", 9)
broll("A6", "No.1 Atlantropa", PERIOD, "1930s Munich lecture hall: a crowded audience in dark suits, a lantern-slide projection "
      "of a vast dam on the screen, the lecturer seen from behind at a lectern.",
      "The slide changes to a map; the audience murmurs; smoke curls in the projector beam.",
      "He sold it for a quarter of a century: lectures, films, exhibitions, even a symphony. He believed one great "
      "shared project would stop Europe going to war again. Europe went to war again.", 10)
still("A7", "No.1 Atlantropa", PERIOD, "An empty snowy road on the edge of Munich at dusk, Christmas 1952, a bicycle lying on "
      "its side in the snow, a single street lamp.",
      "On Christmas Day 1952, cycling to give a lecture, Sörgel was hit by a car and killed. The Atlantropa Institute closed in 1960.", 8)
still("A8v", "No.1 Atlantropa", MODERN, "The Mediterranean at sunset seen from high on the Rock of Gibraltar, a vast calm sea, a lone container ship.",
      "The maddest idea on this list. And the only one that would have redrawn the map of the world.", 6)
sync("A8", "No.1 Atlantropa", "On the Rock of Gibraltar at sunset, the sea glowing behind him, wind.",
     "Sörgel wanted to lower the sea. These days… we'd settle for holding it back.")

# ---------------- OUTRO ----------------
shots.append({"id": "O1v", "segment": "Outro", "kind": "REUSE", "duration_s": 9,
              "vo": "Five buildings. None of them exist. And yet you can stand in the crypt in Liverpool, walk over Beach's tunnel on Broadway, and sit where the elephant stood.",
              "post": "Montage re-using L5, B9v, E7v (no generation cost)"})
sync("O1", "Outro", "Walking slowly toward camera across the Place de la Bastille at night, the single lit July Column "
     "behind him, wet cobbles reflecting lights.",
     "The unbuilt world isn't gone. It's just… awaiting planning permission.")
sync("O2", "Outro", "Same place, he stops, close-up, a small wry smile.", "I'm Hugo Ashby. Mind the gap.")
card("END", "Outro", "UNBUILT", 3)
still("X1", "Stinger", ARCHIVE, "Chicago, 1925: a 21-storey skyscraper in the form of a single colossal fluted Greek Doric "
      "column of polished black granite standing on a cubic block base, among 1920s Chicago buildings.",
      "Honourable mention. In 1922, Adolf Loos entered a skyscraper competition with a twenty-one-storey Doric column. "
      "Was it a joke? Scholars are still arguing. Which, if it was a joke, makes it the longest-running one in architecture.", 13, "slow tilt up")

# ---------------- BUDGET ----------------
cost = {"sync_video": 0.0, "broll_video": 0.0, "stills_and_frames": 0.0, "tts": 0.0}
secs_total = 0
for s in shots:
    secs_total += s["duration_s"]
    if s.get("status") == "RENDERED":
        continue
    k = s["kind"]
    if k == "SYNC":
        cost["sync_video"] += PRICE["sync_per_s"] * s["duration_s"]
        cost["tts"] += PRICE["tts_line"] * 1.5  # takes + occasional retake
    elif k == "BROLL_VIDEO":
        cost["broll_video"] += PRICE["broll_per_s"] * s["duration_s"]
        cost["stills_and_frames"] += PRICE["still"]
    elif k == "STILL":
        cost["stills_and_frames"] += PRICE["still"]
    if s.get("vo"):
        cost["tts"] += PRICE["tts_line"] * 1.5
subtotal = sum(cost.values())
contingency = round(0.15 * (cost["sync_video"] + cost["broll_video"]), 1)
budget = {k: round(v, 1) for k, v in cost.items()}
budget.update({"retakes_15pct_of_video": contingency, "total": round(subtotal + contingency, 1),
               "picture_seconds": secs_total,
               "counts": {k: sum(1 for s in shots if s["kind"] == k) for k in ["SYNC", "BROLL_VIDEO", "STILL", "CARD", "REUSE"]}})

json.dump({"episode": "UNBUILT - Magnificent Delusions", "host_element": HOST_ELEMENT, "host_refs": HOST_REFS,
           "voice": VOICE, "prices": PRICE, "budget": budget, "shots": shots},
          open("shotlist.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps(budget, indent=2))
