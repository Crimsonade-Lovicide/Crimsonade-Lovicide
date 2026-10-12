# UNBUILT release queue (set 12 Oct 2026)

The owner approved this on 12 Oct 2026. It brings the channel back within the 90-day test's rule of **one long video a week at most** (`90_DAY_TEST.md`).

**Every session must follow this queue.**
- Don't schedule, publish or un-hold anything that isn't listed below as due.
- To change the order, ask the owner first, then update this file.

All times are 16:00 UTC unless noted.

## Long videos

| Date | Video | YouTube ID | State |
|---|---|---|---|
| Wed 14 Oct | Habakkuk | 9AkOkantka8 | Scheduled. Already finished, so kept. |
| Sat 17 Oct | Sant'Elia | pAWpH0V0YMs | Scheduled. Already finished, so kept. |
| Sat 24 Oct | SP04 | GqeWYDcK9zY | Scheduled. Moved from its earlier date. |
| Sat 31 Oct | Pilot A: Watkin's Tower | sceWaTQ20rY | Scheduled. First video in the new format. Captions still to be added by hand (see below). |
| Sat 7 Nov | Pilot B: Statue of Liberty | not uploaded | Waiting for the owner to review the preview. The narration is synthetic, so the upload needs "Altered or synthetic content: Yes" and a disclosure line in the description. |
| From Sat 14 Nov | Backlog, one a week | see below | Held. The owner sets the order. |

## Shorts

| Date | Short | YouTube ID |
|---|---|---|
| 12 Oct | Orion | HBq0tEi0BTY |
| 15 Oct | Grand Canyon | KYYjSbe9TqI |
| 16 Oct | Orion | IMgPTxJ-g4g |
| 19 Oct | Grand Canyon | _vgBl0e8cls |
| 25 Oct | SP04 | l7gwGVPgSmg |
| 26 Oct | NAWAPA | sxhncbXeO9E |
| 27 Oct | SP04 | 1kGNutqb-bg |
| 28 Oct | SP04 | n5lq_JsXB7o |
| 29 Oct | NAWAPA | onC24MejTzA |
| 1 Nov | NAWAPA | chJaq7ODAjw |

The SP04 Shorts moved with SP04, so all three now go out after it.

## Held

These are private, with no publish date. Leave them that way until this queue reaches them.

Long videos:

| Video | YouTube ID |
|---|---|
| Vienna | b16WzmwL_BU |
| Soviet Megaprojects (SP06) | 7YOCJxuEHAI |
| Japan | i2ZS_x1B4RM |
| Rushmore | l2ui4htjOBY |
| Washington's tomb | s49AmXe8LI8 |
| Empire State | mJIe9wfNpas |
| Alamo | CqWQ3ZijoQs |
| Pentagon | QptqJCPan6k |
| King's tomb | S_J7RxJpL3c |
| Coney Island | oaqgeQD6f4w |
| Evita | hSTFRklmmhg |
| Ludwig | y-j9mV6cUL0 |
| Newton | 5O31U9ywKCs |
| France's Fake Paris | jY-6P-7UtFw |

Shorts: the three SP06 Shorts, nOhCyFad34E, 7y3TUBrpyeQ and 7Mn2vu0UvT0. Release them in the weeks after SP06 goes out.

The held long videos are set to "Altered or synthetic content: Yes", because they use the AI format.

Two private "upload test" videos with no date (4hFjz_d4ryQ, jTd8SGWufv8) are not part of the queue.

## Releasing a backlog video

1. Pick the next one in the order the owner has set. Use the best packaging first, meaning the strongest title and thumbnail. Put the Halloween-themed chapter videos last, or drop them.
2. Set `publishAt` for the coming Saturday at 16:00 UTC. Through the API, a `videos` update with `part=status` must resend every status field.
3. Record the date in the long-video table above.

## Still to do by hand

YouTube Studio is needed for these steps, because the API connection lacks the `youtube.force-ssl` scope.
- Pilot A: upload `pilot-a-watkin/youtube/captions_en.srt` under Subtitles. Optionally, set up Test & Compare with thumbnails T2 and T3.
- Comments and pinned comments.
