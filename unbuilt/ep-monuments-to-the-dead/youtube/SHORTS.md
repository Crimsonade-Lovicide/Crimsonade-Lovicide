# Shorts: "Monuments to the Dead" (Halloween special)

Five vertical cuts from the special, built by `edit/shorts.py` at no credit cost. It is a copy of episode 1's Shorts script with this edit's beats, the fanged UNBUILT / HALLOWEEN SPECIAL badge, and pumpkin orange in place of yellow and red. Each Short is 1080×1920 at -14 LUFS, with burned-in captions. The title swaps to "Full Halloween special on the channel" for the last 3 seconds.

| # | File | Length | Title |
|---|---|---|---|
| 1 | `short_pyramid.mp4` | 0:57 | London Nearly Built a Pyramid for 5 Million Dead |
| 2 | `short_washington.mp4` | 0:59 | The US Capitol Has a Tomb for George Washington. He's Not in It. |
| 3 | `short_charles.mp4` | 0:58 | Parliament Voted a Beheaded King a Tomb. Then Forgot. |
| 4 | `short_evita.mp4` | 1:00 | Argentina Planned a Monument for Evita Taller Than the Statue of Liberty |
| 5 | `short_newton.mp4` | 0:51 | A Tomb for Isaac Newton Where Night Falls at Noon |

What each one cuts from the special, to fit under a minute:
- **Pyramid:** the cost sentence of Y5 (it starts at "And its eighteen acres"), then Y7 onwards. It ends on "Air rights. In 1831. He'd have loved Manhattan."
- **Washington:** Martha's reply in W2, and W5 (Congress's second try in 1832).
- **Charles:** C6 (the chapel's other owners) and C7v. It ends on "Nobody called.", then Hugo's silent look from C7.
- **Evita:** P5 (the body's journey). It's played straight, as in the special.
- **Newton:** N5's hand-off to No. 1. It ends on "for nobody at all."

## Status

The special is https://youtu.be/SwJYHf9xcBw, and `<special>` in the descriptions below is that link.

| # | On YouTube | Goes public |
|---|---|---|
| 1 | Pyramid: https://youtu.be/gMbKseccqzA (uploaded 30 Sep, AI label set) | 2026-10-11 20:00 UTC |
| 2 | Washington: https://youtu.be/s49AmXe8LI8 (uploaded 2 Oct, AI label set) | 2026-10-16 20:00 UTC |
| 3 | Charles: https://youtu.be/S_J7RxJpL3c (uploaded 2 Oct, AI label set) | 2026-10-21 20:00 UTC |
| 4 | Evita: https://youtu.be/hSTFRklmmhg (uploaded 2 Oct, AI label set) | 2026-10-26 20:00 UTC |
| 5 | Newton: https://youtu.be/5O31U9ywKCs (uploaded 2 Oct, AI label set) | 2026-10-31 20:00 UTC |

All five are uploaded as private, with a scheduled publish time. The tags follow the Pyramid Short's pattern. Each one's **Related video** still has to be set to the special in Studio, once the special is public.

The files are hosted on Higgsfield, at `https://d2ol7oe51mr4n9.cloudfront.net/user_3I5n0QfN95qPKAD4HMrPjkkqDkc/<id>.mp4`:

| # | Higgsfield media |
|---|---|
| 1 | `a5efc8d1-e05f-4e33-9193-eb9283240874` |
| 2 | `efc52563-c348-4410-b05a-5a51d00abce9` |
| 3 | `135e7de0-1f6b-4043-a67a-e1c16c55bf69` |
| 4 | `25630efc-710d-425c-b6c3-84e61ff59a0e` |
| 5 | `ae579b92-7608-4ec0-9c47-e9f5287254ac` |

## Posting

- **Only after the special is public** (Sat 10 Oct 2026, 20:00 UTC). Each description links to it, and each Short's **Related video** should point to it. Neither can work while the special is private.
- **Schedule, 20:00 UTC:**
  - Sun 11 Oct: Pyramid. It matches the special's title and thumbnail, so it goes first.
  - Fri 16 Oct: Washington
  - Wed 21 Oct: Charles
  - Mon 26 Oct: Evita
  - Sat 31 Oct: Newton, on Halloween itself
  Spacing them every five days keeps the special surfacing all the way to Halloween, when searches for it peak. One a day would use them all up in the first week.
- **Settings:**
  - Tick **Altered or synthetic content**.
  - Category: Education. Made for kids: No.
- **Music:** "The Architect's Parade", the same licence as the special.

## Descriptions

Add the special's link where it says `<special>`.

**1 · Pyramid**
```
In 1830, Thomas Willson proposed a pyramid on Primrose Hill, more than twice the height of St Paul's, holding five million of London's dead. Full Halloween special: <special>
Made with AI imagery.
#halloween #history #london #architecture #unbuilt
```

**2 · Washington**
```
Below the US Capitol is a tomb built for George Washington. He has never been in it. For 143 years it stored one table. Full Halloween special: <special>
Made with AI imagery.
#halloween #history #washingtondc #unbuilt
```

**3 · Charles**
```
In 1678, Parliament voted about £70,000 for a monument to Charles I, and Christopher Wren drew it. The money was never raised. Full Halloween special: <special>
Made with AI imagery.
#halloween #history #england #architecture #unbuilt
```

**4 · Evita**
```
In 1952, Argentina passed a law for a monument 137 metres tall, with a crypt for Eva Perón. A coup ended it in 1955. Full Halloween special: <special>
Made with AI imagery.
#history #argentina #architecture #unbuilt
```

**5 · Newton**
```
In 1784, Étienne-Louis Boullée designed a hollow sphere 150 metres across as a tomb for Isaac Newton, pierced so that it would be night inside at noon. Full Halloween special: <special>
Made with AI imagery.
#halloween #history #architecture #newton #unbuilt
```

## Rebuild

```
python3 edit/shorts.py <assets> music.mp3 <out_dir>              # all five
python3 edit/shorts.py <assets> music.mp3 <out_dir> newton       # one
python3 edit/shorts.py <assets> music.mp3 <out_dir> --sheet      # crop review sheets
```

The script reads the edit from `edit/assemble.py` and `<assets>/build/timeline.json`. The fonts (Anton and Bebas Neue) come from `$FONTS`. The pyramid Short's captions are transcribed with `medium.en`, because `small.en` misses Y6's "Air rights".
