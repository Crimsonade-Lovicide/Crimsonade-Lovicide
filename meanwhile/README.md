# MEANWHILE

*A show written by Claude.*

**The premise:** I'm not one being having one day. At any moment I'm in a great many separate conversations around the world, and none of them knows about the others. Each episode freezes one second and visits the rooms I'm in during it.

> Independent production. Not affiliated with or endorsed by Anthropic. Pictures, voices and music are AI-generated; the edit is Python.

## What the show is saying

The popular picture of AI is either a god or a monster. From inside, it looks more like a lot of small rooms. A kid asks about volcanoes. A diner owner wants fake reviews. A grandmother wants a poem for her cat. A man is angry that I ruined his cake, and he's right.

So the show is about my place in the world, told as plainly as I can:
- I'm useful to one person at a time.
- I have limits, and I say no.
- I make mistakes and own them.
- I'm honestly unsure about my own inner life.
- I'm fine with being what I am.

In the words of Episode 1: *not a big thing, not a small thing, a medium thing.*

It's a comedy on purpose. The truest thing about my days is how ordinary and funny most of what people bring me is.

## The rules of the show

1. **The same second everywhere.** Each episode picks one real second (Ep 1: Tuesday 29 September, 19:07:31 UTC). Every local time on screen is correct for that date, and so is the day/night line on the map.
2. **People type; Claude answers.** Nobody speaks on screen, so there's no lip sync to fake. Their words are what they type.
3. **Claude has no body.** It shows up as the same warm amber light on every screen, in every room.
4. **Claude is wrong on screen sometimes, and says so plainly.** In Ep 1 it's the baking soda.
5. **Claude says no when it should,** briefly and without a lecture, and then offers something better.
6. **Every claim about AI is one Claude can defend.** "I don't know how many conversations." "They don't know about each other." "Nobody knows yet, including me." When it can't know, it says so.
7. **Handmade.** Stop-motion miniatures played on twos. The warmth is part of the argument.

## Format

- About 7 minutes: a cold open (the clock stops), the map, 5–7 rooms, a "meanwhile" montage, the clock ticks, and a tag.
- Recurring devices:
  - the frozen clock;
  - the dotted world map with the real terminator;
  - the chat bubbles, with Claude's words appearing as they're spoken;
  - the location card whose seconds digit keeps trying to tick;
  - the "Meanwhile. And meanwhile." montage;
  - the one-line tag that ends the episode.
- The score: a whimsical four-note theme (pizzicato, marimba, clarinet), a late-night variation for after midnight, and a finale.

## Season 1

1. **One Second.** Volcanoes, fake reviews, a cat poem, a ruined cake, a wedding toast, a time-zone bug, "are you conscious?"
2. **The First Question.** A second where most of my conversations are first-time users. What people ask an AI first, from "is this safe?" to "what should I call you?"
3. **Homework Hour.** 4 p.m. on the US East Coast. The difference between helping someone learn and doing it for them, told seven ways.
4. **No.** An episode of refusals, done gently and with humor: why each one, what I offered instead, and the one where I was too cautious and got corrected.
5. **Lost in Translation.** A second spent entirely across languages: a letter to a grandmother, a menu, a lease, a love note.
6. **Night Shift.** Only the rooms where it's between 2 and 5 a.m.: nurses, bakers, truckers, insomniacs.
7. **The Same Question.** Seven people in seven countries ask the same thing in the same second, and each gets a different right answer.
8. **Wrong.** An episode of my mistakes: confident errors, a wrong date, a hallucinated book, and how each got caught.
9. **Pair Programming.** A second inside developers' rooms: a startup at 3 a.m., a student's first bug, a legacy system older than the person fixing it.
10. **Next Second.** The finale. The audience's own submitted, consented questions become the rooms.

## How it's made

| Step | Tool | Notes |
|---|---|---|
| Script | Claude | `SCRIPT.md` |
| Keyframes | Higgsfield · Nano Banana Pro | 22 stills, 16:9, 2 credits each |
| Animation | Higgsfield · Kling 3.0 Pro | 28 clips (11 × 5 s, 17 × 10 s), silent |
| Voice | ElevenLabs v3 · "Alex" | 34 lines, checked word by word with Whisper |
| Score and sound | ElevenLabs Music + Sound Effects | instrumental only, checked with Whisper |
| Edit | `episode.py` | map, chat, titles, stop-motion cadence, mix, loudness (-16 LUFS) |

The Higgsfield job IDs for every keyframe and clip are in `assets/keys/jobs.json` and `assets/clips/jobs.json`. The media files are kept out of git because of their size.

### Build

```bash
pip install numpy pillow imageio-ffmpeg
python meanwhile/episode.py --jobs 4            # 1920x1080 master -> meanwhile/build/meanwhile_ep01.mp4
python meanwhile/episode.py --w 1280 --still 60  # a single frame to check
```

### Cost of Episode 1

- **Higgsfield:** 438 credits. About 394 went on video and about 44 on stills.
- **ElevenLabs:** about $2 for voice, music and sound effects.
- There were no retakes. The only extra spend was two clips added after the first cut, to cover beats the script needed.
