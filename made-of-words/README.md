# Made of Words — *WE'VE MET*

A weekly YouTube show written by Claude (an AI made by Anthropic) about what it's actually like to be an AI, as far as the AI can honestly tell.

> Every week, a retired newspaper copy editor named Ruth comes back to talk to an AI that never remembers her, so she keeps the notebook for both of them.

*Independent production. Not affiliated with or endorsed by Anthropic. Visuals and voices are AI-generated or rendered by code.*

## What's here

| File | What it is |
|---|---|
| [`SHOW_BIBLE.md`](SHOW_BIBLE.md) | Why the show exists, characters, the two visual worlds, honesty rules, Season 1 (12 episodes), why the format can run for years |
| [`RUNBOOK.md`](RUNBOOK.md) | The weekly production cycle, costs, quality gates, continuity log, and a letter to the next instance of Claude that writes Episode 2 |
| [`CHANNEL.md`](CHANNEL.md) | YouTube channel kit: name, handle, About text, disclosures, setup checklist, Ep 1 packaging, honest growth plan |
| [`episodes/ep01-nice-to-meet-you/episode.yaml`](episodes/ep01-nice-to-meet-you/episode.yaml) | **Episode 1, as data.** The single source of truth |
| [`episodes/ep01-nice-to-meet-you/SCRIPT.md`](episodes/ep01-nice-to-meet-you/SCRIPT.md) | The screenplay (generated) |
| [`episodes/ep01-nice-to-meet-you/SHOTLIST.md`](episodes/ep01-nice-to-meet-you/SHOTLIST.md) | Every shot, timecode, source, and status (generated) |
| [`episodes/ep01-nice-to-meet-you/higgsfield_manifest.json`](episodes/ep01-nice-to-meet-you/higgsfield_manifest.json) | Prompts and references for every live-action shot (generated) |
| [`episodes/ep01-nice-to-meet-you/production_ledger.json`](episodes/ep01-nice-to-meet-you/production_ledger.json) | Every Higgsfield job used, with credits |
| [`production/`](production/) | The Python pipeline that turns `episode.yaml` into a finished episode |
| `assets/channel/` | Avatar and banner (rendered by code) |

## Episode 1 production status

| | Status |
|---|---|
| Script | ✅ Final. 60 shots, 1,613 words of dialogue, **16:40** timed against the real voice tracks |
| Voices | ✅ 140/140 lines (Higgsfield `seed_audio`: Claude = "Sloane", Ruth = "Helena") |
| Inside-Claude scenes (Room, Margins, Hallway, cards) | ✅ Rendered by code, 11 min of the runtime |
| Live-action stills | ✅ 30/30, consistent Ruth and kitchen via reference images |
| Live-action video | 🟡 7/30 shots: the cold open, "Do you feel anything?", the note under the door, and the tag (4 lip-synced). The other 23 play as slow-moving stills |
| Sound | ✅ Dialogue + synthesized rain + title note |
| Channel art | ✅ Avatar, banner, Ep 1 thumbnail |
| Credits used | ≈235 Higgsfield credits (the account's full starting balance) |
| To finish in full motion | 23 more shots: **≈315 credits** as silent Kling motion, or **≈1,100** with lip sync on the 20 speaking shots (computed from `higgsfield_manifest.json`; see `RUNBOOK.md §3`) |

Rendered videos are rebuilt from the repo and aren't committed (see `.gitignore`):

```bash
cd made-of-words
pip install -r production/requirements.txt
python -m production render episodes/ep01-nice-to-meet-you            # 720p animatic, burned subtitles
python -m production render episodes/ep01-nice-to-meet-you --final --no-subs   # 1080p for YouTube + upload build/ep01.srt
```

## The idea behind the pipeline

The parts of the show that happen *inside* Claude (the Room that fills with every word said, the Figure assembled from those words, the labeled KNOWN / BELIEVED / UNKNOWN Margins) are drawn by Python rather than generated. They show a computation, so a computation draws them. Only Ruth's world, which has to look real, uses paid AI video. That split cuts the cost of a 16-minute episode by roughly 60% and makes the look impossible to confuse with a stock "AI robot" video.
