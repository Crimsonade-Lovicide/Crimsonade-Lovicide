> **No longer needed (4 Oct 2026).** The owner asked for this to be automated. The flyovers for C3, S4 and O1 are now rendered from open Environment Agency LiDAR by `edit/render_flyovers.py` (no Google account, no AI). The arch shot (S5) uses the CC-licensed photo of the arch. This guide is kept only in case real Earth Studio footage is wanted later.

# Google Earth Studio shots for Pilot A

You need four short flyovers of Wembley today. Each takes about 10 minutes to set up, and Google renders it in your browser.

They replace the stand-in photos in four places: the cold open (C3), the dissolve over the 1922 craters (S4), the arch (S5) and the ending (O1).

**Confidence note:** these steps follow Earth Studio's documented features. Menu names may differ slightly from what you see. If a step doesn't match, tell me what's on screen and I'll adjust it.

## Before you start

1. Open **https://earth.google.com/studio** in **Chrome on a computer** (it doesn't work on phones). Sign in with your Google account.
2. **Attribution must stay on screen.** Google allows Earth Studio footage in monetised YouTube videos as long as the attribution stays visible the whole time: "Google Earth" plus the imagery providers. Earth Studio adds it as an overlay. **Leave it switched on in every shot.**

## Settings for every shot

When you create each project:
- **Dimensions:** 1920 × 1080 (HD)
- **Frame rate:** 24 fps
- **Duration:** as listed per shot. Each is a little longer than it needs to be, which gives the edit room.

**Wembley Stadium:** 51.5558° N, 0.2797° W. Type "Wembley Stadium" in the search box.

---

## GE1: the cold open (C3), 10 seconds

Over this shot you say, "And where it stood is now one of the most famous football pitches in the world."

1. **New project → Quick start → Fly-to.**
2. Location: **Wembley Stadium**. Duration: **10 s**.
3. Set the start view **high and to the north-west**: altitude about **1,500 m**, looking south-east towards the stadium, with the whole bowl small in the frame.
4. Set the end view about **400 m** above the stadium, still angled (not straight down), with the bowl and the arch filling most of the frame.
5. **Easing:** smooth in and out, if offered.
6. **Render** (see "Exporting" below). Name it **GE1_cold_open**.

## GE2: top-down to match the 1922 photo (S4), 12 seconds

Over this shot you say, "When the builders lowered the pitch… the foundations of Watkin's tower." It dissolves into the 1922 aerial photo of the craters, so it has to look **straight down**.

1. **New project → Blank** (or Quick start → Fly-to, then edit).
2. Point the camera **straight down** at the stadium centre. Set the camera **tilt to 0°**, looking down, if the field is shown.
3. Altitude: about **700 m** at the start, about **550 m** at the end. That's a very slow push-in.
4. **North at the top of the frame**, no rotation.
5. Frame it so the stadium bowl fills roughly **half the frame height**, centred.
6. Render as **GE2_topdown**.

## GE3: orbit around the arch (S5), 12 seconds

Over this shot you say, "Today the tallest thing at Wembley is the arch: a hundred and thirty-three metres…"

1. **New project → Quick start → Orbit.**
2. Location: **Wembley Stadium**. Duration: **12 s**.
3. Altitude about **250 m**, with a radius that keeps the **whole arch in frame**. A **quarter to half turn** is plenty; a slow orbit looks better than a full spin.
4. Angle the camera so the arch is the subject, with sky behind it if possible.
5. Render as **GE3_arch_orbit**.

## GE4: Wembley at dusk, for the ending (O1), 12 seconds

Over this shot you say, "…and the spot where it failed became one of the most famous pitches in the world."

1. Duplicate **GE1** (or start a new Fly-to). Make it a **slow pull-back**, the reverse of GE1: from about 500 m out to about 1,200 m.
2. Set the **time of day** to around **sunset**. Earth Studio can set the date and time, which changes the lighting. If you can't find it, normal daylight is fine.
3. Render as **GE4_dusk**.

---

## Exporting

1. Click **Render**.
2. Choose **JPEG** frames. Earth Studio downloads them as a **zip of image files**, one per frame. That's what I want; don't convert them.
3. Keep the attribution overlay on.
4. Put the four zips in **Google Drive** and tell me their names: **GE1_cold_open.zip**, **GE2_topdown.zip**, **GE3_arch_orbit.zip** and **GE4_dusk.zip**.

I'll unpack them, time each one to your narration and add the credit lines to the description.

## If a shot goes wrong

Send it anyway. I can check every frame, tell you what to change, and I can trim or slow down what you send. The one thing I can't do is make new Earth footage, so a slightly long render is better than a short one.
