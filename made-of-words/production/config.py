"""Production constants: look, timing, and tools. Change the show's look here."""
from pathlib import Path

try:  # static ffmpeg from pip (imageio-ffmpeg); falls back to a system ffmpeg
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # pragma: no cover
    FFMPEG = "ffmpeg"

# ---- timing ---------------------------------------------------------------
FPS = 24
SAMPLE_RATE = 48_000
LEAD_IN = 0.4          # silence before the first line of a shot
TAIL = 0.4             # silence after the last pause of a shot
DEFAULT_PAUSE = 0.5
WORDS_PER_SEC = {      # used only until real audio exists
    "CLAUDE": 2.45,    # unhurried
    "RUTH": 2.3,       # deliberate
    "_default": 2.6,
}

# ---- voices (Higgsfield seed_audio presets) --------------------------------
# Chosen by measurement (median pitch, rate, pitch spread), not by ear: Claude's
# voice sits at ~172 Hz, deliberately in the range that reads as neither male
# nor female. Swap any voice by changing its id here and re-running `voices`.
VOICES = {
    "CLAUDE": {"name": "Sloane", "voice_id": "b57b22a0-f287-405b-bc82-6f08f5e6bb1f"},
    "RUTH":   {"name": "Helena", "voice_id": "3c2b83c0-2e0a-5ae8-998a-a5fe71b7eccd"},
    "NURSE":  {"name": "Julian", "voice_id": "95429266-c0ac-4137-a209-63b8812b0f23"},
    "MAN":    {"name": "Barrett", "voice_id": "d603a8cd-3fe1-55e0-9245-617a2589131e"},
    "GIRL":   {"name": "Pixie", "voice_id": "0178ef57-ada4-43d9-992b-8d9221045bb4"},
}

# ---- palette (see SHOW_BIBLE.md §5) ---------------------------------------
PAPER = (244, 239, 230)
PAPER_SHADOW = (226, 218, 204)
INK = (28, 27, 25)
RED = (200, 16, 46)          # copy-editor red: Ruth's things only
AMBER = (232, 163, 61)       # lamp light / the Figure's inner glow
NIGHT = (16, 17, 20)

LABEL_STYLE = {              # Margin epistemic labels
    "KNOWN":    {"fg": PAPER, "bg": INK},
    "BELIEVED": {"fg": INK,   "bg": AMBER},
    "UNKNOWN":  {"fg": INK,   "bg": None},   # outlined: we don't fill in what we don't know
}

# ---- fonts ------------------------------------------------------------------
_F = Path("/usr/share/fonts/truetype")
FONTS = {
    "serif":        _F / "liberation/LiberationSerif-Regular.ttf",
    "serif_bold":   _F / "liberation/LiberationSerif-Bold.ttf",
    "serif_italic": _F / "liberation/LiberationSerif-Italic.ttf",
    "mono":         _F / "liberation/LiberationMono-Regular.ttf",
    "typewriter":   _F / "freefont/FreeMono.ttf",
    "sans":         _F / "dejavu/DejaVuSans.ttf",
    "sans_bold":    _F / "dejavu/DejaVuSans-Bold.ttf",
    "serif_alt":    _F / "freefont/FreeSerif.ttf",
    "serif_alt_it": _F / "freefont/FreeSerifItalic.ttf",
}

# Fragments of ordinary human writing. The Figure is built from these plus
# every word spoken in the episode: "made of words" is literal.
HUMAN_FRAGMENTS = """
dear mom · 2 cups flour · once upon a time · I'm sorry · see you soon · chapter one
the quick brown fox · def main(): · love, dad · happy birthday · to whom it may concern
we hold these truths · 3.14159 · do not bend · call me when you land · x = x + 1
in the beginning · best wishes · table of contents · the end · please · thank you
yours truly · minutes of the meeting · rain today · fig. 2 · lost dog · for sale
dear diary · p.s. · I don't know · remember to · why is the sky blue · hello world
it was a dark and stormy night · add salt to taste · sincerely · return to sender
footnote · errata · the committee met on tuesday · meanwhile · because · perhaps
""".replace("\n", " · ").split(" · ")
HUMAN_FRAGMENTS = [f.strip() for f in HUMAN_FRAGMENTS if f.strip()]
