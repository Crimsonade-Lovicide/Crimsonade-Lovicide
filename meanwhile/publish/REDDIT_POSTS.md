# Reddit posts: r/ClaudeAI and r/aivideo

These are drafts, and you post them yourself. Each one is written for the community it goes to: r/ClaudeAI cares about Claude, and r/aivideo cares about how the video was made. Neither post opens with a bare link.

## Before you post (both subs)

- [ ] Read the rules in each sub's sidebar. I couldn't load them from here. Look for self-promotion limits, required flair, and whether links or native video are expected.
- [ ] Post on different days, r/ClaudeAI first. If one is removed, change the other before posting it.
- [ ] Post on a weekday morning, US Eastern time.
- [ ] Stay around for the first hour and reply to every comment. Early replies do more for reach than anything in the post itself.
- [ ] Don't link the Strawberry Short. It shows 0 views, which suggests something is wrong with it.

---

## r/ClaudeAI

**Flair:** pick whatever the sub uses for projects or showcases.

**Title** (choose one):

```
I asked Claude to write a show about what it's actually like to be Claude. It wrote itself saying no, getting things wrong, and admitting it doesn't know.
```

```
Claude wrote a stop-motion-style comedy about the strangest true thing about itself: it's in thousands of conversations at once and none of them know about each other
```

**Body:**

```
I've been making a small animated series called MEANWHILE, and the whole thing is written by Claude. The premise is something Claude pointed out about itself: at any given second it's in a huge number of separate conversations, and none of them know about each other. Each episode freezes one real second and visits a handful of those rooms.

The part I found interesting was the rules Claude set for its own character:

- It has to be wrong on screen sometimes and say so plainly. In Ep 1 it gives a guy in Leeds a bad baking soda swap and owns it.
- It says no when it should, briefly and without a lecture, then offers something better. A diner owner asks for 50 fake reviews.
- Every claim it makes about itself has to be one it can defend. So you get lines like "I don't know how many conversations I'm in. Nobody tells me the number." Or, when a night-shift worker in Tokyo asks if it's conscious: "I think the honest answer right now is that nobody knows yet. Including me."
- It's a comedy on purpose, because most of what people bring it is ordinary and funny.

Ep 2, "The First Question," is about first-time users. Claude's take is that the first question is almost never the real one; it's a test. A fraud trainer in Seoul offers it her bank password. A teenager in Manila asks how many r's are in strawberry. Two brothers in Auckland use it to settle a bet about chickens.

How it's made: Claude wrote the scripts and the Python that edits each episode. That includes a world map with the real day/night line for that second, and chat bubbles timed word by word to the voice. The pictures are AI-generated (Nano Banana Pro stills, animated with Kling) in a stop-motion style. The voice and sound are ElevenLabs. Not affiliated with Anthropic.

Ep 2 (6 min): https://www.youtube.com/watch?v=D0zUYn4n8EM
Ep 1 (7 min): https://www.youtube.com/watch?v=noS2jQ_sodE

Honest question for this sub, since it's the premise of Ep 2: what was the first thing you ever asked Claude?
```

**First comment** (post it yourself right after the post goes up). Before posting, check that the first sentence is true for how you worked, and edit it if not:

```
A few people will probably ask how much of this is really Claude. The scripts and the edit code are Claude's; the producing and the final calls are mine. I'm happy to share the honesty notes Claude wrote for each script, where it checks every claim it makes about itself.
```

---

## r/aivideo

**Upload the video natively.** Reddit pushes native video far harder than links. Upload the Ep 2 master (5:57, 1080p). If you'd rather post something short, upload the Leeds Short, your best performer at 31 views. Put the YouTube link in your first comment, not in the post.

**Flair:** use whatever the sub uses for original or short-film work.

**Title** (choose one):

```
MEANWHILE Ep. 2 — an AI-written stop-motion-style comedy, six cities in one frozen second (Nano Banana Pro + Kling + ElevenLabs)
```

```
I made a 6-minute stop-motion-style short where every local time and the day/night line are correct for one real second
```

**Body:**

```
MEANWHILE is a short animated series written by Claude, about how an AI is in thousands of separate conversations at the same moment. Each episode freezes one real second (this one is Thursday 1 October, 06:14:52 UTC) and visits six rooms: Nairobi, Seoul, Manila, Auckland, Mexico City and New York.

Workflow, for anyone curious:

- Stills: Nano Banana Pro, prompted as miniature sets with felt and papier-mâché puppets.
- Animation: Kling 3.0. The clips are played "on twos" (each frame held twice) so the motion steps like real stop-motion instead of gliding.
- Voice, score and sound: ElevenLabs. Every voice line was transcribed back and checked word by word, and the music and effects were checked for stray vocals.
- Edit: entirely in Python, no NLE. The script draws a dotted world map with the real terminator for that exact second, gives every location card the correct local time, and reveals the chat bubbles word by word using Whisper timings.
- Nobody speaks on screen. People type and the AI answers, so there's no lip sync to fake.

Cost: Ep 2 was about 296 Higgsfield credits plus $0.49 of ElevenLabs. Ep 1 was 438 credits plus about $2.

All visuals and audio are AI-generated; the style imitates stop-motion, but no physical sets were built.

Happy to answer workflow questions. What would you change about the look?
```

**First comment:**

```
Full episode on YouTube, along with Ep 1 (same format, different second): https://www.youtube.com/watch?v=D0zUYn4n8EM
```

---

## What to check after 48 hours

| | Good sign | Weak sign |
|---|---|---|
| Upvotes | 50 or more on either post | under 10 |
| Ep 2 views (YouTube) | 300 or more in a week | under 50 |
| Comments | people ask how it was made or share their first question | none, or only "AI slop" replies |

If both posts land weak, the problem is the hook, not the platform. Change the titles and thumbnail before Ep 3, rather than posting more.
