# Meta (Facebook) publisher status

Page: AI is OK (1337106516154165). Updated 2026-10-03. The user confirmed steps 2 and 3 in this session.

## Step 1: read-only test (done)
`GET /v19.0/me?fields=id,name` returned `{"id":"1337106516154165","name":"AI is OK"}`.

## Step 2: description fixes (done)
Replaced `youtube.com/@aiisoktv` with `youtube.com/watch?v=D0zUYn4n8EM`. A re-read afterwards confirmed the new link is there and the old one is gone.

| video id | label | result |
|---|---|---|
| 971342832675763 | Ep2 full episode | No change. Its description has no YouTube link, so nothing to replace |
| 1509646131185284 | Manila Short | `{"success":true}` |
| 1107637178333950 | Seoul Short | `{"success":true}` |
| 2723140868131292 | New York Short | `{"success":true}` |

## Step 3: scheduled posts
One-shot reminders bound to this session. Each fires once, posts one video and records its id below.

| fire at (UTC) | label | reminder id | post id |
|---|---|---|---|
| 2026-10-04T12:00Z | Ep1 Medium | none (posted directly) | 1569280748284109 (posted 2026-10-05) |
| 2026-10-04T17:00Z | Ep2 Nairobi | none (posted directly) | 1162879922972068 (posted 2026-10-05) |
| 2026-10-05T12:00Z | Ep1 Tokyo | trig_013UmdukjY8jF1ZSpFAki3md | 1669856807815821 (posted 2026-10-05) |
| 2026-10-05T17:00Z | Ep2 Mexico City | trig_012bCbYhgrSCwssFjGLFTFrE | 3706212982868053 (posted 2026-10-05) |
| 2026-10-06T12:00Z | Ep1 Chicago | trig_019cCZNtoZyv2iQ6ukEn3ZVs | 2067162744171831 (posted 2026-10-06) |
| 2026-10-06T17:00Z | Ep2 First question | trig_01Bdex5BQj2vwhJcwjB8ARwA | 1450357243960569 (posted 2026-10-06) |
| 2026-10-07T12:00Z | Ep1 Leeds | trig_014FQndDAq9UGGniPVQ7oJFJ | 1094907203168318 (posted 2026-10-07) |
| 2026-10-08T12:00Z | Ep1 Sao Paulo | trig_01BaEcVHsBp5MpvAoeM8KhTv | pending |
| 2026-10-09T12:00Z | Ep1 Pune | trig_013aUn7BtqpfNtNCPgf8Ug4v | pending |

**Blocked:** this session's automatic permission check refused to create the reminders for Ep1 Medium and Ep2 Nairobi, giving the reason "real-world transactions". The other seven requests were identical and went through. On 2026-10-05 the user asked for both to be posted right away, and they were (ids in the table).
