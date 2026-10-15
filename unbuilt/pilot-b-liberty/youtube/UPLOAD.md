# YouTube upload: "Was the Statue of Liberty Built for Egypt?" (Pilot B)

**Status (12 Oct 2026):** uploaded as **Rv1KqxNFrKI**. It is private and scheduled for **Sat 7 Nov 2026, 16:00 UTC** (`../../RELEASE_QUEUE.md`), with thumbnail T1 set. Captions are still to be added by hand in Studio.

- **Video:** `edit/build/pilot_b.mp4`, 1080p, 4:46, with the synthetic narration (Cillian). It is gitignored; rebuild it with `edit/build.py --music`.
- **Captions:** `youtube/captions_en.srt`, from `edit/make_captions.py`.
- **Thumbnail:** `thumbs/T1_built_for_egypt.png`. Keep T2 and T3 for Test & Compare.

## Title

**Was the Statue of Liberty Built for Egypt?** (42 characters; the reasons are in `PACKAGING.md`)

## Description

`youtube/description.txt`, pasted as it is.

The chapter times come from `edit/build/timings.json`. The narration starts at 0:00 in the cut.

## Tags

unbuilt, Statue of Liberty, Statue of Liberty Egypt, Bartholdi, Egypt Carrying the Light to Asia, Suez Canal, Port Said, Port Said lighthouse, Ferdinand de Lesseps, Khedive Ismail, Liberty Island, Bedloe's Island, Statue of Liberty history, Statue of Liberty myth, Muslim woman myth, unbuilt architecture, buildings never built, history myths, Gustave Eiffel, New York history, Suez Crisis

## Upload settings

- **Altered or synthetic content: Yes.** The narration is a synthetic voice (ElevenLabs preset "Cillian", generated through Higgsfield). The description says so under "How this was made".
- **Made for kids:** No.
- **Category:** Education.
- **Language:** English (UK).
- **Visibility:** Private, scheduled for 2026-11-07T16:00:00Z.
- **Captions:** upload them by hand: Studio → Subtitles → English → Upload file → "With timing". The API connection lacks the `youtube.force-ssl` scope.

## What the description rests on

- Every claim is in `RESEARCH.md` with its confidence rating.
- "Every picture is real": the only drawn images are the map and the LiDAR flyovers, and both show real data.
- **Required credit:** the CC BY-SA 4.0 credit for the de Lesseps photo (A12). The other credits are courtesy (`assets/rights.csv`).
- **Content ID:** the Chopin recording can draw a mistaken claim, as with Pilot A. If one appears, dispute it and cite the CC0 source.
