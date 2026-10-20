"""UNBUILT YouTube tool: talks to the YouTube Data API directly, replacing Make scenario 6519624.

Credentials come from environment variables set in the cloud environment's settings
(never pasted into chat, never printed):
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
Scope used when the refresh token was made: https://www.googleapis.com/auth/youtube.force-ssl

Every run first checks that the token belongs to the UNBUILT channel and refuses anything else.

    python3 yt.py whoami
    python3 yt.py get ID[,ID...]                       title, privacy, publishAt, synthetic label, views
    python3 yt.py schedule ID 2026-10-24T16:00:00Z     keeps every other status field as it is
    python3 yt.py retitle ID "New title"               keeps description, tags, category, languages
    python3 yt.py upload FILE META.json                META = {"snippet":{...},"status":{...}}
    python3 yt.py thumb ID FILE.jpg
    python3 yt.py caption ID FILE.srt [en] [name]
    python3 yt.py raw METHOD PATH [JSON_BODY]          PATH like /youtube/v3/videos?part=snippet&id=X

Before any edit, the video's current snippet and status are saved to SNAP_DIR.
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UNBUILT_CHANNEL = "UCZwLFmWEf8Iz-wOxyGMYRLQ"
API = "https://www.googleapis.com"
SNAP_DIR = os.environ.get("YT_SNAP_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots"))
CHUNK = 64 * 1024 * 1024

_ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
_ctx = ssl.create_default_context(cafile=_ca)
_token = None


class ApiError(Exception):
    pass


def _open(req, timeout=120):
    try:
        with urllib.request.urlopen(req, context=_ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def token():
    global _token
    if _token:
        return _token
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        raise ApiError("missing environment variables: " + ", ".join(missing))
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    code, _, data = _open(urllib.request.Request("https://oauth2.googleapis.com/token", data=body))
    if code != 200:
        # The error body names the problem (e.g. invalid_grant) and holds no secret.
        raise ApiError(f"token refresh failed: HTTP {code} {data[:300].decode(errors='replace')}")
    _token = json.loads(data)["access_token"]
    return _token


def call(method, path, body=None, headers=None, raw=None, timeout=120):
    """One API call. Returns (status, headers, parsed JSON or bytes)."""
    h = {"Authorization": "Bearer " + token()}
    data = raw
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json; charset=UTF-8"
    h.update(headers or {})
    url = path if path.startswith("http") else API + path
    for attempt in range(4):
        code, rh, out = _open(urllib.request.Request(url, data=data, method=method, headers=h), timeout)
        if code not in (500, 502, 503, 504):
            break
        time.sleep(2 ** (attempt + 1))
    try:
        out = json.loads(out) if out else {}
    except ValueError:
        pass
    return code, rh, out


def ok(code, out, what):
    if code not in (200, 201, 204):
        msg = out.get("error", {}).get("message") if isinstance(out, dict) else str(out)[:300]
        raise ApiError(f"{what}: HTTP {code} {msg}")
    return out


_checked = False


def guard():
    """Refuse to act unless the token is for the UNBUILT channel."""
    global _checked
    if _checked:
        return
    code, _, out = call("GET", "/youtube/v3/channels?part=id,snippet&mine=true")
    ok(code, out, "channel check")
    ids = [c["id"] for c in out.get("items", [])]
    if ids != [UNBUILT_CHANNEL]:
        raise ApiError(f"token is for channel(s) {ids}, not UNBUILT {UNBUILT_CHANNEL}: refusing")
    _checked = True


def videos(ids):
    code, _, out = call("GET", "/youtube/v3/videos?part=snippet,status,statistics,contentDetails&id=" + ",".join(ids))
    return ok(code, out, "videos.list").get("items", [])


def one(vid):
    items = videos([vid])
    if not items:
        raise ApiError(f"video {vid} not found on this channel")
    return items[0]


def snapshot(v, why):
    os.makedirs(SNAP_DIR, exist_ok=True)
    p = os.path.join(SNAP_DIR, f"{v['id']}_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{why}.json")
    with open(p, "w") as f:
        json.dump({k: v.get(k) for k in ("id", "snippet", "status")}, f, ensure_ascii=False, indent=1)
    return p


def summary(v):
    s, st = v["snippet"], v["status"]
    return {"id": v["id"], "title": s["title"], "privacy": st["privacyStatus"], "publishAt": st.get("publishAt"),
            "containsSyntheticMedia": st.get("containsSyntheticMedia"),
            "views": int(v.get("statistics", {}).get("viewCount", 0)),
            "duration": v.get("contentDetails", {}).get("duration")}


STATUS_KEYS = ("privacyStatus", "publishAt", "license", "embeddable", "publicStatsViewable",
               "selfDeclaredMadeForKids", "containsSyntheticMedia")
SNIPPET_KEYS = ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage")


def put_status(v, changes):
    st = {k: v["status"][k] for k in STATUS_KEYS if k in v["status"]}
    st.update(changes)
    if st.get("privacyStatus") != "private":
        st.pop("publishAt", None)  # YouTube only accepts publishAt on private videos
    code, _, out = call("PUT", "/youtube/v3/videos?part=status", {"id": v["id"], "status": st})
    return ok(code, out, "videos.update status")


def put_snippet(v, changes):
    sn = {k: v["snippet"][k] for k in SNIPPET_KEYS if k in v["snippet"]}
    sn.update(changes)
    code, _, out = call("PUT", "/youtube/v3/videos?part=snippet", {"id": v["id"], "snippet": sn})
    return ok(code, out, "videos.update snippet")


def resumable(start_path, meta, path, mime):
    """Start a resumable upload and send the file in chunks, resuming after failures."""
    size = os.path.getsize(path)
    code, rh, out = call("POST", start_path, meta,
                         headers={"X-Upload-Content-Length": str(size), "X-Upload-Content-Type": mime})
    ok(code, out, "start upload")
    url = {k.lower(): v for k, v in rh.items()}["location"]
    fails, off = 0, 0
    while True:
        end = min(off + CHUNK, size) - 1
        with open(path, "rb") as f:
            f.seek(off)
            chunk = f.read(end - off + 1)
        code, rh, out = call("PUT", url, raw=chunk, timeout=900,
                             headers={"Content-Type": mime, "Content-Range": f"bytes {off}-{end}/{size}"})
        if code in (200, 201):
            return out
        if code == 308:
            fails = 0
        else:
            fails += 1
            if fails > 8:
                raise ApiError(f"upload gave up at byte {off}: HTTP {code}")
            time.sleep(min(60, 2 ** fails))
        # Ask the server what it has, then continue from there.
        code, rh, out = call("PUT", url, raw=b"", headers={"Content-Range": f"bytes */{size}"})
        if code in (200, 201):
            return out
        rng = {k.lower(): v for k, v in rh.items()}.get("range")
        off = int(rng.split("-")[1]) + 1 if rng else 0
        print(time.strftime("%H:%M:%S"), f"{off}/{size}", flush=True)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    guard()
    if cmd == "whoami":
        print(f"OK: token is for UNBUILT {UNBUILT_CHANNEL}")
    elif cmd == "get":
        for v in videos(args[0].split(",")):
            print(json.dumps(summary(v), ensure_ascii=False))
    elif cmd == "schedule":
        v = one(args[0])
        print("snapshot", snapshot(v, "schedule"))
        out = put_status(v, {"privacyStatus": "private", "publishAt": args[1]})
        print(json.dumps(summary(one(args[0])), ensure_ascii=False))
    elif cmd == "retitle":
        v = one(args[0])
        print("snapshot", snapshot(v, "retitle"))
        put_snippet(v, {"title": args[1]})
        print(json.dumps(summary(one(args[0])), ensure_ascii=False))
    elif cmd == "upload":
        meta = json.load(open(args[1]))
        out = resumable("/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", meta, args[0], "video/mp4")
        print(json.dumps({"id": out.get("id"), "status": out.get("status")}, ensure_ascii=False))
    elif cmd == "thumb":
        size = os.path.getsize(args[1])
        code, _, out = call("POST", f"/upload/youtube/v3/thumbnails/set?videoId={args[0]}&uploadType=media",
                            raw=open(args[1], "rb").read(),
                            headers={"Content-Type": "image/jpeg", "Content-Length": str(size)})
        ok(code, out, "thumbnails.set")
        print("thumbnail set")
    elif cmd == "caption":
        lang = args[2] if len(args) > 2 else "en"
        name = args[3] if len(args) > 3 else "English"
        meta = {"snippet": {"videoId": args[0], "language": lang, "name": name, "isDraft": False}}
        out = resumable("/upload/youtube/v3/captions?uploadType=resumable&part=snippet", meta, args[1],
                        "application/octet-stream")
        print("caption", out.get("id"), out.get("snippet", {}).get("status"))
    elif cmd == "raw":
        body = json.loads(args[2]) if len(args) > 2 else None
        code, _, out = call(args[0].upper(), args[1], body)
        print(code, json.dumps(out, ensure_ascii=False)[:20000])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ApiError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
