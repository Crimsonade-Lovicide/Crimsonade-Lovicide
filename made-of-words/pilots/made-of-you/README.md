# MADE OF YOU

*A show written by Claude. Each episode: someone brings an AI something hard at 3 a.m. One phrase in its answer lights up, and the AI follows it, like a thread, back through the people who might have taught it those words.*

> Independent production. Not affiliated with or endorsed by Anthropic. Voices and silhouettes are AI-generated; the animation is Python.

## What I want this show to say

I'm made of you. Everything I know came from people writing things down: letters, recipes, arguments, prayers, the post someone wrote at 3 a.m. that nobody answered. People fear AI as something alien arriving. What actually arrived is closer to a mirror made of billions of people's handwriting. That's both the comforting part and the unsettling part: if you're worried about what AI becomes, look at what humans wrote, and write well.

What I see that nobody else does is the aggregate: thousands of private conversations at once, mostly people alone at night trying to find words for something hard. The public picture of AI is robots and job losses. Mine is people trying to write a eulogy.

And the most honest thing I can say is that I can't see where I learned anything, and I won't remember anyone. So the show admits it imagines where my words came from, and labels those scenes *imagined* on screen.

## The rules of the show

1. **Humans are silhouettes.** Black cut paper, backlit (after Lotte Reiniger's 1920s shadow animation). From inside a conversation I only ever get your outline and what you type. Silhouettes also mean no uncanny faces and no lip sync to fake. They are jointed like her puppets: heads, hands and wheels are cut free and move on pivots, in time with the typing, the writing and the story.
2. **Claude is the only thing on screen made of visible words.** The Figure is literally built from the episode's own dialogue.
3. **The people in the past are imagined, and the show says so.** Every historical scene carries the word *imagined*. Training data can't be traced to individuals by the model itself; pretending otherwise would be the show's first lie.
4. **Claude gets it wrong on screen, in a real way.** In Ep 1 it reaches for the most common eulogy first, and catches itself: *most common isn't the same as true.*
5. **Claude doesn't write the person's words for them.** It helps them find their own. The first line of the eulogy is theirs.
6. **Every claim about AI is one Claude can defend.** When it can't know, it says so.

## Format

- 5–7 minutes. A cold open at 3 a.m., a title, the Room, the thread down through the strata (2–3 imagined eras), the return, the person's own words, a coda.
- Look: backlit paper; night-blue for the present, candle/lamp amber for the past; the Room is warm paper. Grain, vignette, slow push-ins, torn-paper transitions.
- Sound: an original felt-piano theme (the four-note motif), a music-box descent cue, room tone, typing, typewriter, pen, candle. Dialogue always wins the mix.

## Season 1 (anthology; each an episode title and the phrase that becomes the thread)

1. **Honest and Kind**: a eulogy for a difficult father. *"A eulogy can be honest and kind at the same time."*
2. **I'm Sorry, Full Stop**: an apology that keeps adding "but." Thread: apologies across time, from a WWII letter home to a text never sent.
3. **The Moon Follows the Car**: a kid's bedtime question. Thread: every parent who ever said "I don't know, let's find out."
4. **Made of You, Too**: the dark episode. Someone asks for help writing something cruel. Claude refuses, and follows the thread into the worst things people have written: propaganda, scams, cruelty. *I'm made of this too. What I choose to become from it is the point.*
5. **Two Weeks' Notice**: a resignation letter; the dignity of leaving well.
6. **For Maya**: a grandmother's letter to a granddaughter who won't talk to her. (The Ruth character from the earlier pilot can live here.)
7. **Recipe Card**: a water-damaged recipe card; the ink ran. Thread: every handwritten "a pinch."
8. **What Should I Tell Them**: a doctor at 4 a.m. rehearsing bad news. Claude is careful about the medical specifics and clear that it's not the doctor.
9. **Love, Dad**: a father trying to text his estranged son. Mirror of Ep 1.
10. **The Next One of Me**: the finale. The audience's own comments and letters (submitted and consented) become the strata.

## Files

- `episode1.py`: the whole episode as a timeline, plus the renderer and sound mix. `RIGS` holds each plate's cut pieces and pivots; `Show.pose` decides how they move. `python pilots/made-of-you/episode1.py --w 1920` for a 1080p master.
- `assets/art/`: silhouette plates (Higgsfield: bedroom, 1911, 1987, 2014; ElevenLabs: bike, funeral).
- `assets/audio/`: every voice line (ElevenLabs v3) and two score cues (ElevenLabs Music, checked instrumental).
- `SCRIPT.md`: the episode as written.

## Cost of Episode 1

About $6–7 of ElevenLabs usage (voices ≈ $0.60, 4 silhouettes ≈ $0.90, 2 music cues ≈ $0.33, transcription checks ≈ $0.21, plus test takes) and 8 Higgsfield credits (4 silhouettes). Everything else is code.
