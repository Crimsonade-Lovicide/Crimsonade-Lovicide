"""Pull finished Higgsfield generations into an episode's asset folders and keep
a ledger of every job (what it was for, its id, what it cost).

Higgsfield is driven through its MCP connector (by Claude or by hand); this
module only handles the files that come back:

    python -m production fetch <episode_dir> ledger.json

where ledger.json is a list of {"slot", "job_id", "url", "credits", "note"}
(the url is used to download and is not kept in production_ledger.json).
`slot` decides where the file lands:
    audio/S02-04-L01   -> assets/audio/S02-04-L01.<ext>   (a line of dialogue)
    stills/S01-03      -> assets/stills/S01-03.<ext>      (Ken Burns fallback)
    shots/S01-03       -> assets/shots/S01-03.<ext>       (real footage)
    refs/ruth          -> ../../assets/refs/ruth.<ext>    (series-wide references)
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path


def fetch(episode_root: Path, ledger_path: Path) -> list[Path]:
    entries = json.loads(Path(ledger_path).read_text())
    master = episode_root / "production_ledger.json"
    book = json.loads(master.read_text()) if master.exists() else []
    known = {e["job_id"] for e in book}
    got = []
    for e in entries:
        kind, name = e["slot"].split("/", 1)
        ext = Path(e["url"].split("?")[0]).suffix or ".bin"
        base = episode_root.parent.parent / "assets" if kind == "refs" else episode_root / "assets"
        dest = base / kind / f"{name}{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            urllib.request.urlretrieve(e["url"], dest)
        got.append(dest)
        if e["job_id"] not in known:
            # no URLs in the committed ledger: they embed the account's id; the
            # job id is enough to find any asset again in the Higgsfield project
            book.append({k: e.get(k) for k in ("slot", "job_id", "credits", "note")})
            known.add(e["job_id"])
    master.write_text(json.dumps(book, indent=2) + "\n")
    return got


def spent(episode_root: Path) -> float:
    master = episode_root / "production_ledger.json"
    if not master.exists():
        return 0.0
    return sum(float(e.get("credits") or 0) for e in json.loads(master.read_text()))
