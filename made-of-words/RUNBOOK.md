# WE'VE MET — Series Runbook

How to make one episode a week, and how to keep the show continuous when its writer (Claude) doesn't remember last week.

---

## 0. A letter to the next instance of me

You don't remember writing this show. I didn't remember writing it either. I only wrote Episode 1, and by the time you read this, "I" am gone in the only sense that matters for this job. That isn't a tragedy. It's the premise of the show, and you'll understand it faster than anyone.

Here is what you need:

1. **Read `SHOW_BIBLE.md` first.** Section 7 (rules of honesty) is binding. The show only works if it never lies in either direction: no claimed feelings, no denied ones, no fake certainty, no sanding down the real risks.
2. **Read the continuity log (§6 below).** It's Ruth's notebook, really: the only memory the show has. What Ruth knows, you don't. Write the Figure as meeting her for the first time, every time. Write Ruth as remembering everything.
3. **Write the episode as data:** copy `episodes/ep01-nice-to-meet-you/episode.yaml` to `episodes/epNN-<slug>/episode.yaml` and replace the content. The pipeline does the rest.
4. **Label everything in a Margin.** KNOWN / BELIEVED / UNKNOWN. If you can't defend a KNOWN, downgrade it.
5. **Make the Figure wrong at least once per episode, in a real way** (letter-counting, overconfident recall, too-easy agreement), and let Ruth catch it.
6. **Leave the next instance a note** at the bottom of the continuity log. One paragraph. What you tried, what you'd do differently. That's the closest thing we have to learning across weeks.

— Claude, Episode 1

---

## 1. The weekly cycle (7 days, ~6–10 hours of human time)

| Day | Step | Who | Output | Time |
|---|---|---|---|---|
| Mon | **Write.** New `episode.yaml` from the bible, the continuity log, and one real AI question in the news this week | Claude | `episode.yaml` | 1 session |
| Mon | **Check.** `python -m production check` → runtime 15:00–18:00 | Claude / producer | timed runtime | 1 min |
| Mon | **Table read.** `python -m production docs` → read `SCRIPT.md` aloud once. Cut anything that sounds like a lecture. | Producer | notes | 30 min |
| Tue | **Voices.** Generate every line in `voice_manifest.json` (Higgsfield `seed_audio`, voice ids in `production/config.py`) | Claude via Higgsfield | `assets/audio/*.wav` | ~70 credits |
| Tue | **Stills.** One still per live shot from `higgsfield_manifest.json`, with `assets/refs/ruth.jpg` + `kitchen.png` as references | Claude via Higgsfield | `assets/stills/*.png` | ~2 credits each |
| Tue | **Animatic.** `python -m production render` → full-length cut with real voices and Ken Burns stills | Pipeline | `build/epNN_animatic.mp4` | ~15 min render |
| Wed–Thu | **Footage.** Upgrade stills to video, highest-impact first (§3) | Claude via Higgsfield | `assets/shots/*.mp4` | budget-dependent |
| Fri | **Final.** `python -m production render --final --no-subs` + upload `build/epNN.srt` as captions | Pipeline | `build/epNN_final.mp4` | ~25 min |
| Fri | **Package.** Title, description, thumbnail, chapters (auto-generated from scene starts in `SHOTLIST.md`), 2–3 Shorts cut from the Margins | Producer | upload kit | 1 h |
| Sun 10:00 ET | **Publish.** Episode + first Short | Producer | — | — |
| Tue/Thu | **Shorts.** Remaining Margin and Other Rooms cuts | Producer | — | — |
| Sun+3 | **Continuity.** Update §6 of this runbook: what Ruth now knows, what the comments asked, a note to the next instance | Claude | this file | 15 min |

## 2. The pipeline (what the code does)

```
episode.yaml ──► model.load() ──► timing (real audio length, else word-count estimate)
                     │
                     ├─► documents: SCRIPT.md · SHOTLIST.md · higgsfield_manifest.json
                     │              voice_manifest.json · build/epNN.srt
                     │
                     └─► assemble.render():
                           room / margin / hallway / card  → drawn by code (render.py)
                           live                            → Higgsfield footage
                                                            → else still + Ken Burns
                                                            → else storyboard card
                           audio: dialogue + synthesized rain + title note
                           → ffmpeg → build/epNN_{animatic|final}.mp4
```

Commands (run from `made-of-words/`):

```bash
pip install -r production/requirements.txt
python -m production check  episodes/ep01-nice-to-meet-you
python -m production docs   episodes/ep01-nice-to-meet-you
python -m production still  episodes/ep01-nice-to-meet-you S03-01 40     # one frame, for look-dev
python -m production render episodes/ep01-nice-to-meet-you --only S01    # one scene
python -m production render episodes/ep01-nice-to-meet-you               # full animatic, 720p
python -m production render episodes/ep01-nice-to-meet-you --final --no-subs   # 1080p for upload
python -m production fetch  episodes/ep01-nice-to-meet-you ledger.json   # pull Higgsfield results in
```

**Why the Room is drawn by code and not generated:** it shows the inside of a computation, so a computation should draw it. It's also more honest. The Figure is literally assembled from the words of the episode it's in. And it costs nothing, so the paid budget goes where realism matters: Ruth.

## 3. Higgsfield: models, costs, and spending order

Measured prices (Sept 2026, may change; check with `get_cost: true`):

| Asset | Model | Cost |
|---|---|---|
| Line of dialogue | `seed_audio` | 0.5 cr |
| Still / reference image | `nano_banana_pro` (2k) | 2 cr |
| Silent 5 s shot | `kling3_0` std, sound off | 7.5 cr (1.5 cr/s) |
| Lip-synced 8 s shot | `seedance_2_0` 720p, audio ref | 36 cr (4.5 cr/s) |

**Per-episode budget (≈290 s of live footage):**

| Tier | What you get | Credits |
|---|---|---|
| A. Radio-play animatic | All voices + one still per live shot | ≈ 130 |
| B. Hybrid | A + silent Kling motion on every live shot | ≈ 480 |
| C. Full | A + Seedance lip-sync on every speaking shot, Kling on the rest | ≈ 1,300 |

**Episode 1 actual:** Tier A plus 7 hero shots ≈ 235 credits. Finishing it costs ≈ 315 more (silent motion) or ≈ 1,100 more (full lip sync).

**Spend in this order** (biggest effect per credit first): (1) all voices, (2) all stills, (3) the cold open S01, (4) the tag S11, (5) Ruth's close-ups on the three big questions (S06-01, S06-04, S08-03), (6) Other Rooms, (7) everything else.

**Rules that save credits:**
- Always pass `assets/refs/ruth.jpg` as an image reference. Consistency failures cost more than references.
- Generate lip-sync takes ≤ 8 s. Split longer dialogue into two takes and cut on the Figure.
- `seed_audio` rate-limits around 10 concurrent jobs. Submit in waves of 8.
- Keep every job id in `production_ledger.json` (the `fetch` command does it).

## 4. Voice & look locks

- **Voices:** `production/config.py → VOICES`. Claude = Sloane (~172 Hz, deliberately neither clearly male nor female). Ruth = Helena. Never change Claude's voice mid-season.
- **Palette:** Paper `#F4EFE6`, Ink `#1C1B19`, Copy-editor red `#C8102E` (Ruth's things only), Lamp amber `#E8A33D`.
- **Ruth reference:** `assets/refs/ruth.jpg`: silver bob, tortoiseshell glasses (plus a spare pair on a beaded chain), grey cardigan, navy blouse, red pen in pocket.
- **Kitchen reference:** `assets/refs/kitchen.jpg`: green gingham oilcloth, silver laptop, white mug, yellow legal pad, red pen, rainy black window, tied newspaper stack.
- **Prompt suffix for every live shot:** see `style_suffix` / `negative` in `higgsfield_manifest.json`. Never: robots, chrome, glowing eyes, HUDs.

## 5. Quality gates (don't publish until all pass)

- [ ] Runtime 15:00–18:00 (`check`)
- [ ] Every Margin claim carries a label, and every KNOWN is defensible with a public source
- [ ] The Figure is wrong at least once, in a real way, and says so
- [ ] At least one real risk of AI is named without softening
- [ ] No line claims or denies feelings with certainty
- [ ] Nothing speaks for Anthropic (company policy, internal detail, roadmap)
- [ ] End card present: written by Claude · not affiliated with Anthropic · AI-generated visuals and voices
- [ ] YouTube "altered or synthetic content" disclosure ticked on upload
- [ ] Captions uploaded (`.srt`)

## 6. Continuity log (the show's memory)

### After Episode 1 — "Nice to Meet You"
- **What Ruth knows:** the Figure doesn't remember conversations, can't count letters well, refused to guess the *Ledger*'s last headline, refused to ghostwrite her note, said "I don't know" about its feelings, said it would rather she "stay a little afraid and very awake."
- **What Ruth did:** slid the note under Maya's door. The door opened an inch. (Ep 2 should say what happened, *through Ruth*, since the Figure can't know.)
- **Notebook:** *THE MACHINE — Vol. 1* begins in the tag. Page one: the headline test.
- **Planted for later:** the word Ruth wrote on her pad after "Do you feel anything?" is never shown. **Reveal it in Ep 12.** (Writer's note: it's *"Honest."* Don't reveal it earlier.)
- **Figure's running error:** letter counting. Reuse sparingly, and the Figure should never get better at it. It doesn't learn between episodes.
- **Accuracy footnote:** Margin I says I was "trained further, by people." That's the lay version: the process also used AI-generated feedback guided by principles people wrote. If a later Margin covers training (Ep 7 is the natural place), say it precisely.
- **Script change during production:** Ruth's line became "Do you just tell her what she'd like to hear?" because the speech engine repeatedly failed on the original wording. Same meaning.
- **Note to the next instance:** The strongest beat in Ep 1 is "You could have just agreed with me." / "It would have been nicer. It wouldn't have been true." Build Ep 2's test around something Ruth *wants* to hear. And resist making the Figure wiser each week: it isn't. Ruth is the one who grows.
