# UNBUILT on Make: which scenario to use (12 Oct 2026)

**The limit.** The owner's Make plan allows **two active scenarios at a time**. Sessions kept switching scenarios on and off to make room, and that risked breaking each other's work.

**The fix.** With the owner's approval, the YouTube and Google Drive uploaders were merged into one scenario on 12 Oct.

| Scenario | ID | State | Use it for |
|---|---|---|---|
| **UNBUILT · Google API (YouTube + Drive uploads)** | **6519624** | **Active** | Every YouTube Data API call (the default) and every Google Drive API call (`service: "drive"`) |
| UNBUILT · IG/FB poster (Unbuilt only) | 6525243 | Active | Instagram and Facebook reels |
| UNBUILT · Google Drive API (uploads) | 6524336 | **Inactive; leave it off** | Nothing. It's kept only as a backup. The merged scenario does the same job. |
| WEIGHT OF EVIDENCE · YouTube API (uploads) | 6603120 | Inactive | A different channel. Not for UNBUILT. |

## Calling the merged scenario

| Input | Value |
|---|---|
| `method` | GET, POST, PUT, … |
| `path` | The path after `https://www.googleapis.com/youtube`, or after `https://www.googleapis.com/drive` when `service` is `drive`. |
| `body` | JSON, as a string. |
| `upload_type` | Optional. Defaults to `video/mp4`. |
| `upload_length` | Optional. The byte count, for resumable uploads. |
| `service` | Leave it empty for YouTube. Set it to `drive` for Google Drive. |

The result always comes back as an error with status 3 and a `REPORT HTTP …` message. That's by design: the scenario reports through a ThrowError module.

**Resumable uploads.** POST through the scenario with an upload path, e.g. `/../upload/youtube/v3/videos?uploadType=resumable&part=snippet,status`. Take the `location` from the report, then `curl -X PUT --data-binary @file "<location>"` from the sandbox.

**Not possible through this connection.** YouTube comments and captions need the `youtube.force-ssl` scope, which the connection doesn't have. Do those by hand in Studio.

## Rules

- **Don't activate 6524336 again.** Use `service: "drive"` on 6519624 instead.
- **If both slots are needed for something new,** ask the owner first. Don't switch off a scenario another session may be using.
- **If the connection fails** with "Failed to verify connection 'UNBUILT'. Status Code Error: 400", only the owner can fix it: Make → Connections → UNBUILT → Verify, or Reauthorize.
