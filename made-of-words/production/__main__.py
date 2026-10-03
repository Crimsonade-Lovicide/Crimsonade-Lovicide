"""WE'VE MET production pipeline.

    python -m production check   <episode_dir>            validate + timed runtime
    python -m production docs    <episode_dir>            SCRIPT.md, SHOTLIST.md, manifests, .srt
    python -m production still   <episode_dir> SHOT T     one frame → build/SHOT.png
    python -m production render  <episode_dir> [--final] [--only S01,S03-01] [--no-subs]
    python -m production fetch   <episode_dir> ledger.json  download Higgsfield results into assets/

Run from the made-of-words/ directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import assemble, documents, fetch, model


def main(argv=None):
    ap = argparse.ArgumentParser(prog="production", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "docs", "still", "render", "fetch"])
    ap.add_argument("episode")
    ap.add_argument("shot", nargs="?")
    ap.add_argument("t", nargs="?", type=float, default=2.0)
    ap.add_argument("--final", action="store_true", help="1920x1080 (default 1280x720 animatic)")
    ap.add_argument("--only", help="comma-separated shot or scene ids")
    ap.add_argument("--no-subs", action="store_true", help="don't burn subtitles (upload the .srt)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    ep = model.load(a.episode)
    if a.cmd == "check":
        print(json.dumps(model.summary(ep), indent=2, ensure_ascii=False))
    elif a.cmd == "docs":
        for p in documents.write_all(ep):
            print("wrote", p.relative_to(ep.root.parent.parent))
    elif a.cmd == "fetch":
        for p in fetch.fetch(ep.root, Path(a.shot)):
            print("have", p.relative_to(ep.root.parent.parent))
        print(f"credits spent on this episode so far: {fetch.spent(ep.root):g}")
    elif a.cmd == "still":
        out = ep.root / "build" / f"{a.shot}.png"
        out.parent.mkdir(exist_ok=True)
        print("wrote", assemble.still(ep, a.shot, a.t, out))
    elif a.cmd == "render":
        W, H = (1920, 1080) if a.final else (1280, 720)
        only = set(a.only.split(",")) if a.only else None
        tag = "final" if a.final else "animatic"
        name = a.out or f"{ep.id}_{tag}{'_' + a.only.replace(',', '-') if only else ''}.mp4"
        out = ep.root / "build" / name
        print("rendering", out, f"({W}x{H}, runtime {model.fmt_time(ep.runtime)})")
        assemble.render(ep, out, W, H, subs_on=not a.no_subs, only=only)
        print("wrote", out)


if __name__ == "__main__":
    main()
