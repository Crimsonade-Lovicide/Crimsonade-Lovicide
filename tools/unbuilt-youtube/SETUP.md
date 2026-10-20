# UNBUILT YouTube tool: one-time setup (about 15 minutes, on a computer)

This replaces Make for everything on YouTube: scheduling, titles, uploads, thumbnails, captions and stats.
It costs nothing; Google's YouTube API is free up to 10,000 units a day. One upload uses about 1,600 units.

Never paste the client secret or the refresh token into the chat. They go only into the environment settings (step 6).

## 1. Create a Google Cloud project
1. Go to https://console.cloud.google.com and sign in with the Google account that owns the UNBUILT channel.
2. At the top, open the project picker, choose **New project**, name it `unbuilt-tools` and create it. Make sure it is selected.

## 2. Turn on the YouTube API
1. Open **APIs & Services → Library** and search for **YouTube Data API v3**.
2. Click **Enable**.

## 3. Set up the sign-in screen
1. Open **APIs & Services → OAuth consent screen** (it may be called **Google Auth Platform**) and click **Get started**.
2. App name `UNBUILT tools`, and pick your own email as the support email.
3. Audience: **External**. Add your contact email, agree, and click **Create**.
4. Under **Audience**, click **Publish app** so it is **In production**.
   In "Testing" mode Google expires the sign-in every 7 days. You will see an "unverified app" warning later; that is expected for a private tool.

## 4. Create the client
1. Open **Clients** (or **Credentials → Create credentials → OAuth client ID**).
2. Application type: **Web application**. Name: `unbuilt-tools`.
3. Under **Authorized redirect URIs**, add exactly `https://developers.google.com/oauthplayground`
4. Click **Create**. Keep the **Client ID** and **Client secret** open for steps 5 and 6.

## 5. Sign in once and get the refresh token
1. Go to https://developers.google.com/oauthplayground
2. Click the gear icon (top right) and tick **Use your own OAuth credentials**. Paste the Client ID and Client secret there.
3. In the box under Step 1 on the left, type `https://www.googleapis.com/auth/youtube.force-ssl` and click **Authorize APIs**.
4. Sign in. **When it asks which account or channel, pick UNBUILT, not SIGNAL LOST.**
5. On "Google hasn't verified this app", click **Advanced → Go to UNBUILT tools**, then **Continue/Allow**.
6. In Step 2, click **Exchange authorization code for tokens**. Copy the **Refresh token**.

## 6. Store the three values for Claude
In the Claude app, open the cloud environment menu in this session's title bar and click **Edit**.
Add these as environment variables (under **Network secrets** / **API credentials** if that section is offered):

| Name | Value |
|---|---|
| `YT_CLIENT_ID` | the Client ID from step 4 |
| `YT_CLIENT_SECRET` | the Client secret from step 4 |
| `YT_REFRESH_TOKEN` | the Refresh token from step 5 |

A new session picks them up. Then tell Claude "YouTube keys are in". Claude runs `python3 yt.py whoami`, which refuses to do anything unless the keys belong to the UNBUILT channel (UCZwLFmWEf8Iz-wOxyGMYRLQ).

## If it stops working
- `invalid_grant` means Google revoked the sign-in (for example after a password change, or six months unused). Redo step 5 and replace `YT_REFRESH_TOKEN`.
- To cut off access at any time: https://myaccount.google.com/permissions → UNBUILT tools → Remove access.
