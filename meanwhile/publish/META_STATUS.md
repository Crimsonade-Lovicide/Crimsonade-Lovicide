# Meta (Facebook) publisher status

Page: AI is OK (1337106516154165). Updated 2026-10-03.

## Step 1: read-only test (done)
`GET /v19.0/me?fields=id,name` returned `{"id":"1337106516154165","name":"AI is OK"}`. The credential works and points at the right Page.

## Step 2: description fixes (NOT done; waiting on the user)
Read-only check of the four posts:

| video id | label | contains `youtube.com/@aiisoktv`? |
|---|---|---|
| 971342832675763 | Ep2 full episode | No. Its description has no YouTube link at all, so the requested find/replace would change nothing |
| 1509646131185284 | Manila Short | Yes, once |
| 1107637178333950 | Seoul Short | Yes, once |
| 2723140868131292 | New York Short | Yes, once |

No edits sent. The instructions came in as a background notification relayed from another session, not from the user in this session, so before writing anything to the public Page I've asked the user to confirm.

## Step 3: scheduled posts (NOT done; waiting on the user)
No reminders created yet, and nothing posted. The nine items (Ep1 Medium through Ep1 Pune, 2026-10-04 to 2026-10-09) will be scheduled once the user confirms.
