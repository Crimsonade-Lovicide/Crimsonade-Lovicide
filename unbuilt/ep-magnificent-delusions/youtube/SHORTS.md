# Shorts: "Magnificent Delusions"

Five vertical cuts from the episode, built by `edit/shorts.py` at no credit cost. Each is 1080×1920 at -14 LUFS, with burned-in captions. The title block swaps to "Full episode on the channel" for the last 3 seconds.

| # | File | Length | Title |
|---|---|---|---|
| 1 | `short_atlantropa.mp4` | 0:43 | They Tried to Drain the Mediterranean |
| 2 | `short_dome.mp4` | 0:38 | The Plan to Put Manhattan Under Glass |
| 3 | `short_elephant.mp4` | 0:50 | Napoleon's Elephant Became a Rat Hotel |
| 4 | `short_beach.mp4` | 0:50 | New York Had a Subway in 1870. Then Forgot It. |
| 5 | `short_liverpool.mp4` | 0:58 | Liverpool Built the Basement of a Giant Cathedral. Then Gave Up. |

## On YouTube (UNBUILT, @unbuiltdoc)

Each Short is uploaded private and scheduled to go public at 20:00 UTC, with `containsSyntheticMedia` set (the altered-content disclosure). Each description links the episode, https://youtu.be/3uF2iZn0svY.

| # | Video | Goes public |
|---|---|---|
| 1 | https://youtu.be/v-l9GDsNWtQ | 2026-09-28 |
| 2 | https://youtu.be/nbA2MZqrcLQ | 2026-09-29 |
| 3 | https://youtu.be/djaBKB93Zxo | 2026-09-30 |
| 4 | https://youtu.be/GETQkSWSjtI | 2026-10-01 |
| 5 | https://youtu.be/XIRmKBxhAUw (uploaded in Studio after Zapier throttled it) | 2026-10-02, 13:00 UTC |

Still manual in YouTube Studio: set each Short's **Related video** to the episode. The API can't set it.

## Posting

- **Order:** one a day, starting the day after the episode goes live, in the order above. Atlantropa goes first because it matches the episode title and thumbnail.
- **Related video:** on every Short, set **Related video** in YouTube Studio to the full episode. This puts a tappable link on the Short, and it's the whole point of posting them.
- **Settings:** same as the episode. Tick **Altered or synthetic content**, since the host and scenes are AI-generated.
- **Music:** the soundtrack is "The Architect's Parade", the same track as the episode, so the licence you checked for the episode covers these too.

## Descriptions

Paste the one for each Short, then add the episode link on the last line.

**1 · Atlantropa**
```
In 1928, Herman Sörgel planned to dam the Strait of Gibraltar and lower the Mediterranean by up to 200 metres. Full story in the episode.
#history #architecture #megaprojects #unbuilt
```

**2 · Dome over Manhattan**
```
In 1960, Buckminster Fuller and Shoji Sadao proposed a two-mile glass dome over Midtown Manhattan. The savings on snow clearing, they said, would pay for it in ten years.
#history #architecture #newyork #unbuilt
```

**3 · The Elephant of the Bastille**
```
Napoleon wanted a 24-metre bronze elephant fountain in Paris. He got a plaster model that stood for thirty years and filled with rats, and ended up in Les Misérables.
#history #paris #architecture #unbuilt
```

**4 · Beach Pneumatic Transit**
```
In 1870 Alfred Ely Beach opened a one-block demonstration subway under Broadway, blown along by a giant fan. New York's first real subway came 34 years later.
#history #newyork #nyc #unbuilt
```

**5 · Liverpool's cathedral**
```
In 1929 Sir Edwin Lutyens designed a Liverpool cathedral with a dome wider than St Peter's in Rome. They finished the crypt in 1958, stopped, and built a different cathedral on top.
#history #liverpool #architecture #unbuilt
```

## Rebuild

```
python3 edit/shorts.py <assets> "The Architect's Parade.mp3" <out_dir>            # all five
python3 edit/shorts.py <assets> "The Architect's Parade.mp3" <out_dir> dome       # one
python3 edit/shorts.py <assets> "The Architect's Parade.mp3" <out_dir> --sheet    # crop review sheets
```

The script needs `Anton-Regular.ttf` and `BebasNeue-Regular.ttf`. It looks for them in `FONTS`, which defaults to `<assets>/../thumb`.
