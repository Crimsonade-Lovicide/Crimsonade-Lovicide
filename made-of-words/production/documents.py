"""Text outputs generated from the episode: screenplay, shot list, Higgsfield
manifest, and subtitles. Nothing here is hand-edited; edit episode.yaml."""
from __future__ import annotations

from pathlib import Path

from .model import Episode, dump_json, fmt_time, shot_media, srt_time, summary

REF_DESCRIPTIONS = {
    "ruth": "Ruth Kowalczyk, 68: silver chin-length bob, reading glasses on a beaded chain, "
            "grey cardigan with a red pen in the pocket, lined intelligent face, no makeup",
    "kitchen": "Ruth's kitchen at night: small table with green oilcloth, open laptop, mug of "
               "tea, rain on a black window, one warm tungsten lamp",
    "notebook": "black-and-white marbled composition notebook, handwritten cover label "
                "'THE MACHINE — VOL. 1'",
    "house_hall": "narrow dark house hallway, closed bedroom door with a strip of blue light beneath",
    "nurse": "night-shift male nurse, 30s, navy scrubs, tired eyes, hospital workstation",
    "scammer": "man in his 40s, dark hoodie, smirk, couch lit by phone and TV",
    "girl": "girl about 8 in a car booster seat at night, tablet, moon in window",
}


def screenplay(ep: Episode) -> str:
    out = [f"# WE'VE MET — Episode {ep.number}: \"{ep.title}\"", "",
           "*Written by Claude. Generated from `episode.yaml`; edit that file, not this one.*", "",
           f"> {ep.logline}", "",
           f"**Runtime (timed):** {fmt_time(ep.runtime)}", ""]
    scene = None
    for s in ep.shots:
        if s.scene_id != scene:
            scene = s.scene_id
            out += ["---", "", f"## {s.scene_name}", ""]
            if s.heading and s.kind != "card":
                out += [f"**{s.heading.upper()}**", ""]
        elif s.heading and s.kind != "card":
            out += [f"**{s.heading.upper()}**", ""]
        tag = {"room": "THE ROOM", "margin": "THE MARGIN", "hallway": "THE HALLWAY",
               "live": "LIVE", "card": "CARD"}[s.kind]
        out.append(f"<sub>`{s.id}` · {tag} · {fmt_time(s.start)}</sub>")
        out.append("")
        if s.kind == "card":
            out += [f"**{(s.text or '').strip().splitlines()[0]}**" if s.card != "end"
                    else "```\n" + (s.text or "").strip() + "\n```", ""]
        if s.action:
            out += [f"*{s.action.strip()}*", ""]
        for ln in s.lines:
            cue = ln.who + (" (V.O.)" if ln.vo else "")
            label = f"**[{ln.label}]** " if ln.label else ""
            out += [f"**{cue}**  ", f"{label}{ln.text}", ""]
    out += ["---", "", "*END OF EPISODE*", ""]
    return "\n".join(out)


def shotlist(ep: Episode) -> str:
    out = [f"# Shot list — Episode {ep.number}: \"{ep.title}\"", "",
           "Generated from `episode.yaml`. **Source** = who makes it: `code` (rendered by "
           "`production/`) or `higgsfield` (generated). **Status** reflects files in `assets/`.", "",
           "| Shot | In | Dur | Kind | Source | Status | What we see |", "|---|---|---|---|---|---|---|"]
    for s in ep.shots:
        src = "higgsfield" if s.kind == "live" else "code"
        status = shot_media(ep, s)[0] if s.kind == "live" else "rendered"
        what = (s.action or s.prompt or s.text or "").strip().replace("\n", " ")
        if s.lines and not what:
            what = f"{s.lines[0].who}: “{s.lines[0].text}”"
        what = what[:110] + ("…" if len(what) > 110 else "")
        out.append(f"| `{s.id}` | {fmt_time(s.start)} | {s.dur:.1f}s | {s.kind} | {src} | {status} | {what} |")
    sm = summary(ep)
    out += ["", "## Totals", "", "```", *(f"{k}: {v}" for k, v in sm.items()), "```", ""]
    return "\n".join(out)


def higgsfield_manifest(ep: Episode) -> dict:
    """Everything needed to generate the live shots, one entry per shot.

    Video models cap at ~10–15 s, so long live shots are split into takes.
    Lines whose speaker matches `lipsync` should be passed as audio references.
    """
    shots = []
    for s in ep.shots:
        if s.kind != "live":
            continue
        takes = max(1, int(-(-s.dur // 12)))  # ceil(dur / 12)
        shots.append({
            "id": s.id,
            "duration": round(s.dur, 2),
            "takes": takes,
            "take_seconds": round(s.dur / takes, 2),
            "status": shot_media(ep, s)[0],
            "prompt": " ".join(s.prompt.split()),
            "refs": {r: REF_DESCRIPTIONS.get(r, r) for r in s.refs},
            "lipsync": s.lipsync,
            "lipsync_lines": [ln.id for ln in s.lines if s.lipsync and ln.who == s.lipsync and not ln.vo],
            "dialogue": [{"id": ln.id, "who": ln.who, "text": ln.text, "vo": ln.vo} for ln in s.lines],
            "output": f"assets/shots/{s.id}.mp4",
        })
    return {
        "episode": ep.id, "title": ep.title, "aspect_ratio": "16:9",
        "style_suffix": "shot on 35mm film, natural grain, tungsten practicals, shallow depth "
                        "of field, restrained naturalistic performance, no text, no watermark",
        "negative": "robot, chrome, glowing eyes, sci-fi HUD, text overlays, captions, logos",
        "shots": shots,
    }


def voice_manifest(ep: Episode) -> dict:
    lines = [{"id": ln.id, "who": ln.who, "text": ln.text, "vo": ln.vo,
              "output": f"assets/audio/{ln.id}.mp3", "done": bool(ln.audio)}
             for _, ln in ep.lines()]
    return {"episode": ep.id, "lines": lines}


def srt(ep: Episode) -> str:
    out, n = [], 0
    for s, ln in ep.lines():
        n += 1
        a = s.start + ln.start
        b = a + ln.dur + min(ln.pause, 0.6)
        speaker = "" if ln.who == "CLAUDE" else f"{ln.who}: "
        out += [str(n), f"{srt_time(a)} --> {srt_time(b)}", speaker + ln.text, ""]
    return "\n".join(out)


def write_all(ep: Episode) -> list[Path]:
    root = ep.root
    (root / "build").mkdir(exist_ok=True)
    files = {
        root / "SCRIPT.md": screenplay(ep),
        root / "SHOTLIST.md": shotlist(ep),
        root / "build" / f"{ep.id}.srt": srt(ep),
    }
    for p, text in files.items():
        p.write_text(text)
    dump_json(higgsfield_manifest(ep), root / "higgsfield_manifest.json")
    dump_json(voice_manifest(ep), root / "voice_manifest.json")
    dump_json(summary(ep), root / "build" / "summary.json")
    return [*files, root / "higgsfield_manifest.json", root / "voice_manifest.json"]
