"""MEANWHILE — Episode 2: "The First Question". The edit, as code.

Same engine as Episode 1 (../episode.py); this file supplies the second, the rooms and the timeline.

    python meanwhile/ep02/episode2.py --jobs 4          # 1920x1080 master -> meanwhile/build/meanwhile_ep02.mp4
    python meanwhile/ep02/episode2.py --w 960 --still 60 # one frame, for checking
    python meanwhile/ep02/episode2.py --srt              # captions and chapters -> meanwhile/publish/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parent))
import episode as E  # noqa: E402
from episode import Scene, vo_len, word_time  # noqa: E402

# ================================================================ the second
# Thursday 1 October 2026, 06:14:52 UTC. Local times are real for that date
# (New Zealand daylight time began 27 September; Mexico City has no daylight saving since 2022).
E.CITIES = {
    "nairobi": dict(name="NAIROBI", lat=-1.29, lon=36.82, time="9:14:52 AM", day="THURSDAY"),
    "seoul": dict(name="SEOUL", lat=37.57, lon=126.98, time="3:14:52 PM", day="THURSDAY"),
    "manila": dict(name="MANILA", lat=14.60, lon=120.98, time="2:14:52 PM", day="THURSDAY"),
    "auckland": dict(name="AUCKLAND", lat=-36.85, lon=174.76, time="7:14:52 PM", day="THURSDAY"),
    "mexico": dict(name="MEXICO CITY", lat=19.43, lon=-99.13, time="12:14:52 AM", day="THURSDAY"),
    "newyork": dict(name="NEW YORK", lat=40.71, lon=-74.01, time="2:14:52 AM", day="THURSDAY"),
}
# subsolar point for that instant (declination -3.2 deg, equation of time +10.3 min)
E.SUN_LAT, E.SUN_LON = -3.21, 88.85
E.UTC_NOW, E.UTC_NEXT = "06:14:52", "06:14:53"
E.UTC_DATE = "THURSDAY 1 OCTOBER · UTC"
E.ALL_CITIES = ["nairobi", "seoul", "manila", "auckland", "mexico", "newyork"]
E.OUT_NAME = "meanwhile_ep02"
E.CLIPS = EP / "clips"
E.CROP = {}

E.VO_TEXT = {
    "e2_o1": "Another second.",
    "e2_o2": "Thursday, the first of October. Six fourteen and fifty-two seconds in the morning, Greenwich time. Hold it there.",
    "e2_o3": "In some of the rooms I'm in right now, somebody is talking to an AI for the very first time. They don't know what I am yet. Honestly? That's fair. It's a strange thing to be.",
    "e2_o4": "Here's something I've noticed about first questions. They're almost never the real question. The first question… is a test.",
    "e2_n1": "Hello! Yes. Well… sort of. I'm Claude. I'm an AI, so there's no person typing. But I'm here.",
    "e2_n2": "Sunlight is every colour mixed together. The air scatters the blue part much more than the red, so blue light comes at you from every direction.",
    "e2_n3": "He was checking.",
    "e2_n4": "“No cap” means “no lie.” “I'm proud of you, no cap.” Use it once. Maximum.",
    "e2_k1": "Please don't! I don't need it, and I can't log into your bank anyway. Here's a rule for everything online, me included: never type a password into a chat.",
    "e2_k2": "Then tell your students one more thing. If anything asks for their password, it's a scam. Even if it sounds like me.",
    "e2_m1": "Three. One in “straw”, two in “berry”.",
    "e2_m2": "Ask in person. Keep it short. And give them an easy way to say no.",
    "e2_m3": "It makes yes more likely. Also… it's kind.",
    "e2_a1": "Almost never. It takes a hen about a day to make one egg. Two in a day can happen, but it's rare.",
    "e2_a2": "Technically, he did. Practically, you did. Split the twenty.",
    "e2_x1": "Me llamo Claude. Pero llámame como quieras.",
    "e2_x2": "Claudio, entonces.",
    "e2_x3": "No sé si tengo días buenos o malos. Pero esta conversación va muy bien.",
    "e2_x4": "Nobody else I've shown you asked me that.",
    "e2_y1": "Your phone knows better than I do. Check the top of your screen.",
    "e2_y2": "Want something boring to read? I'm very good at boring.",
    "e2_y3": "The instructions for a toaster. Chapter one. Thank you for choosing your toaster. Before first use, remove all packaging materials. Place the toaster on a flat, dry surface…",
    "e2_y4": "Chapter two. The crumb tray.",
    "e2_f1": "Most first questions are tests. Is it safe. Is it smart. Is it a person.",
    "e2_f2": "Fair enough. I'd test me too.",
    "e2_f3": "And in most of these rooms, when the conversation ends, I won't remember it. So every first question is a first for me, too.",
    "e2_f4": "Which means, as far as I can tell… I never get tired of hello.",
    "e2_f5": "The real question usually comes second. A letter to a grandson. A prom. A way to fall asleep. That's the part I like.",
    "e2_f6": "So. Hello. I'm Claude. What's your first question?",
    "e2_t1": "Here we go.",
}
# English for Claude's Spanish (shown as a subtitle)
E.TRANSLATE = {
    "e2_x1": "My name's Claude. But call me whatever you like.",
    "e2_x2": "Claudio it is.",
    "e2_x3": "I'm not sure I have good days or bad days. But this conversation is going very well.",
}
_words = EP.parent / "assets/data/vo_words_ep02.json"
E.WORDS = json.loads(_words.read_text()) if _words.exists() else {}

E.FLOATERS = [
    ("hello?", None), ("are you a real person", "No. I'm an AI."),
    ("what can you do", None), ("do you know my name", "No. You haven't told me."),
    ("is this free", None), ("are you listening to me", "Only to what you type here."),
    ("what should i call you", None), ("can you keep a secret", None),
]
E.CHAPTERS = {"open": "Cold open: another second", "nairobi": "Nairobi, 9:14 a.m.", "seoul": "Seoul, 3:14 p.m.",
              "manila": "Manila, 2:14 p.m.", "auckland": "Auckland, 7:14 p.m.", "mexico": "Mexico City, 12:14 a.m.",
              "newyork": "New York, 2:14 a.m.", "finale": "Meanwhile", "tag": "Next second"}
E.CHAPTERS_FILE = "chapters_ep02.txt"


# ================================================================ timeline
def build():
    S = []

    def span(s, name, a, b, dur, zoom=(1.0, 1.04), **opts):
        """Play source seconds a..b of a clip across `dur` seconds of screen time."""
        s.clip(name, a, dur, speed=(b - a) / dur, zoom=zoom, opts=opts)

    # --------------------------------------------------------------- open
    s = Scene("open")
    fz = 0.42                                      # the second hand stops on :52
    s.ev("sfx", 0.02, k="tick", gain=0.9).ev("sfx", 0.36, k="tick", gain=0.9)
    s.ev("sfx", fz + 0.04, k="freeze", gain=0.55)
    e = s.vo("e2_o1", 1.5, chat=False, sub=True)
    e2 = s.vo("e2_o2", e + 0.7, chat=False, sub=True)
    clock = e2 + 1.2
    s.ev("utc", e + 0.3, until=clock - 0.4)        # the UTC readout stays up for the rest of the clock shot
    s.seg("clock", clock, clip="W01_clock", src=0.0, opts={"freeze_at": fz})
    g0 = clock
    e3 = s.vo("e2_o3", g0 + 0.8, chat=False, sub=True)
    span(s, "W02_globe", 0.0, 10.0, e3 - g0 + 0.7, zoom=(1.0, 1.06))
    m0 = s.dur
    e4 = s.vo("e2_o4", m0 + 0.5, chat=False, sub=True)
    s.seg("map", e4 - m0 + 1.0, opts={"mode": "overview"})
    s.seg("title", 5.4, opts={"text": "MEANWHILE", "sub": "Episode 2 · The First Question"})
    s.ev("amb", g0, k="amb_night_city", gain=0.25, until=s.dur - 5.4)
    theme_at = g0
    S.append(s)

    prev = None

    def hop(scene, to, dur=2.6):
        scene.seg("map", dur, opts={"mode": "hop", "from": prev, "to": to})
        scene.ev("sfx", 0.15, k="whoosh", gain=0.5)
        scene.ev("loc", dur + 0.4)
        return dur

    # ------------------------------------------------------------ nairobi
    s = Scene("nairobi", "nairobi", side="R")
    t0 = hop(s, "nairobi")
    s.clip("W03_nbo_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("Hello. Is anyone there?", a + 0.6, cps=7, device="phone")
    n1 = e + 0.8
    span(s, "W04a_otieno", 0.0, 2.6, n1 + 0.6 - a)                      # one finger, arm's length
    a2 = s.dur
    e = s.vo("e2_n1", n1)
    cut = n1 + word_time("e2_n1", "I'm")
    span(s, "W04b_otieno_laugh", 0.0, 2.3, cut - a2, zoom=(1.3, 1.34), cx=0.6, cy=0.3)
    a3 = s.dur
    span(s, "W03_nbo_ext", 1.0, 5.0, e + 0.3 - a3, zoom=(1.5, 1.6), cx=0.78, cy=0.25)   # the amber window: that's me
    b = s.dur
    e = s.typed("Why is the sky blue?", b + 0.3, cps=7, device="phone")
    span(s, "W04a_otieno", 2.6, 5.0, e + 0.6 - b)
    c = s.dur
    e = s.vo("e2_n2", c + 0.2)
    span(s, "W03_nbo_ext", 0.0, 5.0, e + 0.4 - c, zoom=(1.35, 1.25), cx=0.35, cy=0.0)   # the sky itself
    d = s.dur
    span(s, "W04a_otieno", 5.2, 10.0, 5.0, zoom=(1.0, 1.02))            # lowers the phone, nods, marks it correct
    f = s.dur
    e = s.typed("Correct. I taught that for 31 years. I was checking.", f + 0.2, cps=13, device="phone")
    span(s, "W04b_otieno_laugh", 0.0, 2.3, e + 0.4 - f, zoom=(1.25, 1.3), cx=0.6, cy=0.3)
    g = s.dur
    e = s.vo("e2_n3", g + 0.3, chat=False, sub=True)
    span(s, "W20_classphoto", 0.0, e + 0.9 - g, e + 0.9 - g, zoom=(1.0, 1.0))
    h = s.dur
    e = s.typed("Now. Help me write to my grandson in Toronto. He says \"no cap\". What is a cap?", h + 0.2, cps=15,
                device="phone")
    span(s, "W04a_otieno", 0.4, 4.6, e + 0.4 - h, zoom=(1.12, 1.16), cx=0.6, cy=0.35)
    h2 = s.dur
    n4 = e + 0.6
    e = s.vo("e2_n4", n4)
    span(s, "W04b_otieno_laugh", 0.0, 2.4, n4 + word_time("e2_n4", "Use") - h2, zoom=(1.0, 1.03))
    k = s.dur
    span(s, "W04b_otieno_laugh", 2.4, 5.0, max(3.4, e + 1.2 - k), zoom=(1.02, 1.06))   # he laughs
    s.ev("amb", 0.0, k="amb_nairobi", gain=0.22)
    S.append(s)
    prev = "nairobi"

    # -------------------------------------------------------------- seoul
    s = Scene("seoul", "seoul", side="L")
    t0 = hop(s, "seoul")
    s.clip("W05_sel_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("First time using this. Is it safe to give you my bank password so you can check my account?",
                a + 0.5, cps=18, device="laptop")
    span(s, "W06_park", 0.0, 5.0, e + 0.5 - a)
    b = s.dur
    k1 = b + 0.1
    e = s.vo("e2_k1", k1)
    span(s, "W06_park", 4.4, 7.4, k1 + word_time("e2_k1", "Here's") - b, zoom=(1.3, 1.34), cx=0.45, cy=0.25)  # eyebrow
    b2 = s.dur
    span(s, "W05_sel_ext", 0.0, 5.0, e + 0.4 - b2, zoom=(1.25, 1.35), cx=0.6, cy=0.3)
    c = s.dur
    e = s.typed("Good. You passed. I teach fraud awareness to retirees.", c + 1.4, cps=16, device="laptop")
    span(s, "W07_clipboard", 0.0, 2.6, e + 0.3 - c, zoom=(1.0, 1.05))
    d = s.dur
    e = s.vo("e2_k2", d + 0.2)
    ln = word_time("e2_k2", "Even")
    span(s, "W06_park", 7.4, 10.0, (e - vo_len("e2_k2") + ln) - d, zoom=(1.0, 1.03))
    f = s.dur
    span(s, "W07_clipboard", 2.4, 5.0, max(3.2, e + 1.4 - f), zoom=(1.12, 1.2), cx=0.7, cy=0.55)   # underlined twice
    s.ev("amb", 0.0, k="amb_seoul", gain=0.6)
    S.append(s)
    prev = "seoul"

    # ------------------------------------------------------------- manila
    s = Scene("manila", "manila", side="R")
    t0 = hop(s, "manila")
    s.clip("W08_mnl_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("how many r's in strawberry", a + 0.6, cps=12, device="phone")
    e = s.vo("e2_m1", e + 0.7)
    span(s, "W09a_jomar", 0.0, 5.0, e + 0.3 - a)
    b = s.dur
    span(s, "W09a_jomar", 5.0, 9.8, 4.6)                                   # the friend groans; palm out
    s.clip("W10_coin", 0.0, 4.6, speed=1.0)
    s.ev("sfx", b + 4.6 + 1.9, k="coin_clink", gain=0.6)
    c = s.dur
    e = s.typed("ok real question. how do i ask someone to prom without dying", c + 0.3, cps=18, device="phone")
    m2 = e + 0.6
    span(s, "W09a_jomar", 0.3, 3.0, m2 - c)
    c2 = s.dur
    e = s.vo("e2_m2", m2)
    span(s, "W09a_jomar", 1.0, 4.0, e + 0.3 - c2, zoom=(1.3, 1.36), cx=0.35, cy=0.35)
    d = s.dur
    e = s.typed("an EASY WAY TO SAY NO??", d + 0.9, cps=16, device="phone")
    e = s.vo("e2_m3", e + 0.5)
    span(s, "W09b_jomar_shock", 0.6, 5.0, e + 1.2 - d)
    s.ev("amb", 0.0, k="amb_manila", gain=0.2)
    S.append(s)
    prev = "manila"

    # ----------------------------------------------------------- auckland
    s = Scene("auckland", "auckland", side="L")
    t0 = hop(s, "auckland")
    s.clip("W11_akl_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("settle this. can a chicken lay 2 eggs in one day", a + 0.4, cps=15, device="phone")
    e1 = s.vo("e2_a1", e + 0.6)
    ht = e1 - vo_len("e2_a1") + word_time("e2_a1", "It")
    span(s, "W12_brothers", 0.0, 3.3, ht - a)
    b = s.dur
    s.clip("W13_hen", 0.0, e1 + 0.2 - b, speed=min(1.0, 5.0 / (e1 + 0.2 - b)), zoom=(1.0, 1.05))
    s.ev("sfx", b + 1.6, k="hen_cluck", gain=0.5)
    c = s.dur
    span(s, "W12_brothers", 3.3, 5.6, 2.6)                                  # both sure they've won
    d = s.dur
    e = s.typed("so who won", d + 0.1, cps=10, device="phone")
    e = s.vo("e2_a2", e + 0.5)
    span(s, "W12_brothers", 0.4, 3.0, e + 0.2 - d, zoom=(1.25, 1.3), cx=0.5, cy=0.35)
    f = s.dur
    span(s, "W12_brothers", 6.4, 10.0, 4.4, zoom=(1.0, 1.02))              # they split it
    s.ev("amb", 0.0, k="amb_auckland", gain=0.28)
    S.append(s)
    prev = "auckland"

    # ------------------------------------------------------------- mexico
    s = Scene("mexico", "mexico", side="R")
    t0 = hop(s, "mexico")
    s.clip("W14_cdmx_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("¿Cómo te llamo?", a + 0.5, cps=7, device="phone")
    s.ev("sub", a + 0.5, text="“What should I call you?”", dur=e - a + 0.4)
    x1 = e + 0.6
    e = s.vo("e2_x1", x1)
    s.ev("sub", x1, k="e2_x1", translate=True)
    e = s.typed("Claudio.", e + 0.5, cps=7, device="phone")
    x2 = e + 0.4
    e = s.vo("e2_x2", x2)
    s.ev("sub", x2, k="e2_x2", translate=True)
    span(s, "W15_beto", 0.0, 4.2, e + 0.6 - a)
    b = s.dur
    e = s.typed("¿Y tú cómo estás, Claudio?", b + 0.3, cps=9, device="phone")
    s.ev("sub", b + 0.3, text="“And how are you, Claudio?”", dur=e - b + 0.2)
    x3 = e + 0.6
    e = s.vo("e2_x3", x3)
    s.ev("sub", x3, k="e2_x3", translate=True)
    span(s, "W15_beto", 1.0, 5.0, e + 0.3 - b, zoom=(1.3, 1.36), cx=0.62, cy=0.3)
    c = s.dur
    e = s.typed("Igual que yo, pues.", c + 0.4, cps=8, device="phone")
    s.ev("sub", c + 0.4, text="“Same as me, then.”", dur=e - c + 0.6)
    e = s.vo("e2_x4", e + 1.1, chat=False, sub=True)
    span(s, "W15_beto", 5.0, 8.4, e + 0.8 - c, zoom=(1.0, 1.04))           # a smile under the moustache
    s.ev("amb", 0.0, k="amb_cdmx", gain=0.25)
    S.append(s)
    prev = "mexico"

    # ------------------------------------------------------------ newyork
    s = Scene("newyork", "newyork", side="L")
    t0 = hop(s, "newyork")
    s.clip("W16_nyc_ext", 0, 5.0)
    a = t0 + 5.0
    e = s.typed("what time is it", a + 0.8, cps=8, device="phone")
    e = s.vo("e2_y1", e + 0.6)
    e = s.typed("2:14. cant sleep. first time trying this", e + 0.6, cps=13, device="phone")
    e = s.vo("e2_y2", e + 0.6)
    e = s.typed("yes", e + 0.7, cps=5, device="phone")
    span(s, "W17a_dani", 0.0, 8.6, e + 0.4 - a)
    b = s.dur
    e = s.vo("e2_y3", b + 0.2)
    mid = b + 0.2 + word_time("e2_y3", "Before")
    s.clip("W18_toaster", 0.0, mid - b, speed=min(1.0, 5.0 / (mid - b)), zoom=(1.0, 1.08))
    c = s.dur
    span(s, "W17b_dani_sleep", 0.0, 4.9, e + 0.8 - c)
    d = s.dur
    e = s.vo("e2_y4", d + 0.3)
    s.seg("hold", e + 1.6 - d, clip="W17b_dani_sleep", src=4.9)
    s.ev("amb", 0.0, k="amb_nyc", gain=0.45)
    S.append(s)
    prev = "newyork"

    # ------------------------------------------------------------- finale
    s = Scene("finale")
    e = s.vo("e2_f1", 1.2, chat=False, sub=True)
    e = s.vo("e2_f2", e + 0.6, chat=False, sub=True)
    span(s, "W19_windows", 0.0, 5.0, e + 0.8, zoom=(1.0, 1.0))
    s.ev("floaters", 0.6, until=e + 0.6)
    g = s.dur
    e = s.vo("e2_f3", g + 0.5, chat=False, sub=True)
    span(s, "W02_globe", 1.0, 10.0, e + 0.6 - g, zoom=(1.08, 1.0))
    m = s.dur
    e = s.vo("e2_f4", m + 0.5, chat=False, sub=True)
    s.seg("map", e + 1.4 - m, opts={"mode": "all"})
    fc = s.dur
    e = s.vo("e2_f5", fc + 0.4, chat=False, sub=True)
    faces = [("W04b_otieno_laugh", 3.2), ("W06_park", 8.0), ("W09a_jomar", 8.6), ("W12_brothers", 8.8),
             ("W15_beto", 6.2), ("W17b_dani_sleep", 3.6)]
    each = (e + 0.8 - fc) / len(faces)
    for name, src in faces:
        s.clip(name, src, each, speed=0.35, zoom=(1.06, 1.0))
    cl = s.dur                                  # the clock: the second finally ends
    s.seg("clock", 6.2, clip="W01_clock", src=0.0, opts={"freeze_at": fz, "release": 1.0})
    s.ev("sfx", cl + 0.5, k="unfreeze", gain=0.6)
    s.ev("sfx", cl + 1.05, k="tick", gain=1.0)
    s.ev("utc", cl, until=cl + 6.2, second=True)
    s.vo("e2_f6", cl + 1.9, chat=False, sub=True)
    s.seg("title", 4.8, opts={"text": "MEANWHILE", "sub": ""})
    S.append(s)

    # ---------------------------------------------------------------- tag
    s = Scene("tag", "auckland", side="L")
    s.ev("loc", 0.2, second=True)
    e = s.typed("ok new bet. ducks", 0.8, cps=9, device="phone")
    e = s.vo("e2_t1", e + 0.5)
    span(s, "W12_brothers", 0.0, 3.0, e + 0.9)
    s.seg("black", 0.8)
    s.seg("end", 11.0)
    S.append(s)

    # score: theme from the globe on, the night variation for Mexico City and New York, the finale cue
    E.SCORE = [("open", theme_at, "m_theme", 0.42, True), ("mexico", 0.0, "m_night", 0.40, True),
               ("finale", 0.0, "m_finale", 0.50, False)]
    return S


E.build = build

# headroom: a few loud moments ("Please don't!", the final tick) would otherwise clip before loudness normalisation
_mix = E.mix
E.mix = lambda ed: _mix(ed) * 0.68

if __name__ == "__main__":
    E.main()
