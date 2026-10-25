"""Episode data model and timing.

An episode is a YAML file (see episodes/ep01-nice-to-meet-you/episode.yaml).
Loading it produces a flat, timed list of shots and lines that every other
stage (screenplay, shot list, renderer, assembler) reads from.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import FFMPEG, LEAD_IN, TAIL, WORDS_PER_SEC, DEFAULT_PAUSE

KINDS = {"room", "margin", "hallway", "card", "live"}
LABELS = {"KNOWN", "BELIEVED", "UNKNOWN"}


@dataclass
class Line:
    id: str
    who: str
    text: str
    vo: bool = False
    label: str | None = None
    pause: float = DEFAULT_PAUSE
    # filled in by timing
    audio: Path | None = None
    start: float = 0.0      # seconds from shot start
    dur: float = 0.0        # speech duration


@dataclass
class Shot:
    id: str
    kind: str
    scene_id: str
    scene_name: str
    heading: str | None = None
    action: str | None = None
    lines: list[Line] = field(default_factory=list)
    min: float = 0.0
    state: str | None = None
    drop: list[str] = field(default_factory=list)
    red: list[str] = field(default_factory=list)
    prompt: str | None = None
    refs: list[str] = field(default_factory=list)
    lipsync: str | None = None
    card: str | None = None
    text: str | None = None
    # filled in by timing
    start: float = 0.0      # seconds from episode start
    dur: float = 0.0


@dataclass
class Episode:
    id: str
    number: int
    title: str
    logline: str
    root: Path
    shots: list[Shot]

    @property
    def runtime(self) -> float:
        return sum(s.dur for s in self.shots)

    @property
    def assets(self) -> Path:
        return self.root / "assets"

    def lines(self):
        for s in self.shots:
            for ln in s.lines:
                yield s, ln


def audio_duration(path: Path) -> float:
    """Duration in seconds, read from ffmpeg's banner (no ffprobe needed)."""
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        raise ValueError(f"cannot read duration of {path}")
    h, mnt, sec = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(sec)


def estimate_speech(who: str, text: str) -> float:
    words = len(re.findall(r"[\w']+", text))
    return max(0.6, words / WORDS_PER_SEC.get(who, WORDS_PER_SEC["_default"]))


def find_audio(assets: Path, line_id: str) -> Path | None:
    for ext in ("wav", "mp3", "m4a", "ogg"):
        p = assets / "audio" / f"{line_id}.{ext}"
        if p.exists():
            return p
    return None


def load(episode_dir: str | Path) -> Episode:
    root = Path(episode_dir).resolve()
    data = yaml.safe_load((root / "episode.yaml").read_text())
    shots: list[Shot] = []
    seen: set[str] = set()
    for sc in data["scenes"]:
        for raw in sc["shots"]:
            sid = raw["id"]
            if sid in seen:
                raise ValueError(f"duplicate shot id {sid}")
            seen.add(sid)
            if raw["kind"] not in KINDS:
                raise ValueError(f"{sid}: unknown kind {raw['kind']!r}")
            lines = []
            for i, ln in enumerate(raw.get("lines", []) or [], 1):
                if ln.get("label") and ln["label"] not in LABELS:
                    raise ValueError(f"{sid}: bad label {ln['label']!r}")
                lines.append(Line(id=f"{sid}-L{i:02d}", who=ln["who"], text=ln["text"],
                                  vo=bool(ln.get("vo")), label=ln.get("label"),
                                  pause=float(ln.get("pause", DEFAULT_PAUSE))))
            shots.append(Shot(
                id=sid, kind=raw["kind"], scene_id=sc["id"], scene_name=sc["name"],
                heading=raw.get("heading") or None, action=raw.get("action"),
                lines=lines, min=float(raw.get("min", 0)), state=raw.get("state"),
                drop=raw.get("drop", []) or [], red=raw.get("red", []) or [],
                prompt=(raw.get("prompt") or "").strip() or None,
                refs=raw.get("refs", []) or [], lipsync=raw.get("lipsync"),
                card=raw.get("card"), text=raw.get("text"),
            ))
            if raw["kind"] == "live" and not shots[-1].prompt:
                raise ValueError(f"{sid}: live shots need a Higgsfield prompt")
    ep = Episode(id=data["id"], number=int(data["number"]), title=data["title"],
                 logline=" ".join(data.get("logline", "").split()), root=root, shots=shots)
    retime(ep)
    return ep


def retime(ep: Episode) -> None:
    """Lay lines out inside shots and shots along the episode timeline.

    Real audio (assets/audio/<line-id>.wav|mp3) is measured; otherwise speech
    length is estimated from word count so the animatic runs at true length.
    """
    t = 0.0
    for s in ep.shots:
        cursor = LEAD_IN if s.lines else 0.0
        for ln in s.lines:
            ln.audio = find_audio(ep.assets, ln.id)
            ln.dur = audio_duration(ln.audio) if ln.audio else estimate_speech(ln.who, ln.text)
            ln.start = cursor
            cursor += ln.dur + ln.pause
        s.dur = round(max(s.min, cursor + (TAIL if s.lines else 0.0), 1.5), 3)
        s.start = t
        t += s.dur


def summary(ep: Episode) -> dict:
    by_kind: dict[str, float] = {}
    for s in ep.shots:
        by_kind[s.kind] = by_kind.get(s.kind, 0) + s.dur
    words = sum(len(ln.text.split()) for _, ln in ep.lines())
    have_audio = sum(1 for _, ln in ep.lines() if ln.audio)
    total_lines = sum(1 for _ in ep.lines())
    live = [s for s in ep.shots if s.kind == "live"]
    return {
        "episode": f"{ep.id} — {ep.title}",
        "runtime": fmt_time(ep.runtime),
        "runtime_seconds": round(ep.runtime, 1),
        "shots": len(ep.shots),
        "dialogue_words": words,
        "lines_with_real_audio": f"{have_audio}/{total_lines}",
        "seconds_by_kind": {k: round(v, 1) for k, v in sorted(by_kind.items())},
        "live_shots_generated": f"{sum(1 for s in live if shot_media(ep, s)[0] == 'video')}/{len(live)}",
    }


def shot_media(ep: Episode, s: Shot) -> tuple[str, Path | None]:
    """Best available media for a live shot: video > still > placeholder."""
    for ext in ("mp4", "mov", "webm"):
        p = ep.assets / "shots" / f"{s.id}.{ext}"
        if p.exists():
            return "video", p
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ep.assets / "stills" / f"{s.id}.{ext}"
        if p.exists():
            return "still", p
    return "placeholder", None


def fmt_time(sec: float) -> str:
    m, s = divmod(int(round(sec)), 60)
    return f"{m}:{s:02d}"


def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def dump_json(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n")
