"""Motion graphics for The Hoffman Files, ep. 2 (Miranda). Built on the ep. 1 graphics module: same look, same
helpers, same slates. Cards are f(t, dur, cues); overlays are f(cv, t, dur, frame, tr, cues) on a 3D plate.
Accuracy rules: the confession form is recreated as type, the warnings are a paraphrase, and the one dissent
quote is marked for checking against the opinion until it is.
"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, '..', 'ep1'), os.path.join(HERE, '..', '..', 'ep01-hot-coffee', 'edit')):
    if os.path.exists(os.path.join(p, 'gfx.py')): sys.path.append(p); break      # after ep2's own dir, so episode.py is ep2's
from gfx import *                                        # noqa: F401,F403  (helpers, colours, slates)
import gfx as _g

PAPER, INK = (226, 221, 206), (40, 38, 34)


# ---------------------------------------------------------------- cards
def title(t, dur, cues):
    cv = card(); a = fade(t, 0.0, dur, 0.15, 0.6)
    tr = 6 + 34 * (1 - ramp(t, 0.0, 1.6))
    put(cv, 'EPISODE 2', 'monob', 26, GREY, (W / 2, 330), 'c', a * ramp(t, 0.4, 0.6), track=8)
    put(cv, 'THE HOFFMAN FILES', 'bebas', 230, WHITE, (W / 2, 390), 'c', a, track=tr)
    w = 820 * ramp(t, 0.5, 1.0); rect(cv, (W / 2 - w / 2, 650, W / 2 + w / 2, 654), AMBER, a)
    put(cv, 'MIRANDA', 'monob', 44, AMBER, (W / 2, 690), 'c', a * ramp(t, 0.9, 0.7), track=14)
    return cv


def phoenix(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    typed(cv, 'PHOENIX, ARIZONA  ·  MARCH 1963', t, 0.3, 'mono', 72, WHITE, (220, 380), cps=20, cursor=t < cue(cues, 0, 3) , alpha=a)
    k1 = ramp(t, cue(cues, 0, 2.5), 0.5)
    put(cv, 'A RELATIVE SPOTS A MATCHING CAR  ·  A PARTIAL PLATE', 'monob', 30, GREY, (224, 520), alpha=a * k1, track=3)
    k2 = ramp(t, cue(cues, 1, 6.0) - 0.2, 0.5)
    put(cv, 'ERNESTO MIRANDA, 22', 'bebas', 120, AMBER, (220 + 24 * (1 - k2), 590), alpha=a * k2, track=3)
    return cv


FORM = ['I, ____________________, do hereby swear that I make this',
        'statement voluntarily and of my own free will, with no',
        'threats, coercion, or promises of immunity, and']
FORM_HI = ['with full knowledge of my legal rights, understanding',
           'any statement I make may be used against me.']


def form(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 2.0), cue(cues, 1, 5.0), cue(cues, 2, 9.0)
    x0, y0, x1, y1 = 300, 120, 1620, 1010
    rect(cv, (x0 + 10, y0 + 14, x1 + 10, y1 + 14), (0, 0, 0), 0.45 * a)          # shadow
    rect(cv, (x0, y0, x1, y1), PAPER, a)
    put(cv, 'STATEMENT', 'monob', 34, INK, ((x0 + x1) / 2, y0 + 60), 'c', a, track=10, shadow=False)
    rect(cv, (x0 + 80, y0 + 116, x1 - 80, y0 + 118), INK, 0.6 * a)
    kt = ramp(t, c0 - 0.3, 0.6); ly = y0 + 150
    for i, ln in enumerate(FORM):
        put(cv, ln, 'mono', 32, INK, (x0 + 80, ly + i * 54), alpha=a * (0.35 + 0.65 * kt), shadow=False)
    hy = ly + len(FORM) * 54; kh = ramp(t, c1 - 0.2, 0.9)
    for i, ln in enumerate(FORM_HI):
        wl = text_w(ln, 'mono', 32)
        rect(cv, (x0 + 74, hy + i * 54 + 2, x0 + 74 + (wl + 14) * kh, hy + i * 54 + 48), AMBER, 0.85 * a)
        put(cv, ln, 'mono', 32, INK, (x0 + 80, hy + i * 54), alpha=a, shadow=False)
    for i in range(6):                                                               # the handwritten part, abstracted
        yy = hy + 2 * 54 + 60 + i * 50; xe = x1 - 80 - (i * 97 % 260)
        rect(cv, (x0 + 80, yy, xe, yy + 3), (150, 146, 136), a * 0.8)
    rect(cv, (x0 + 80, y1 - 70, x0 + 520, y1 - 68), INK, 0.6 * a)
    put(cv, 'SIGNATURE', 'mono', 20, (120, 116, 108), (x0 + 80, y1 - 60), alpha=a, shadow=False)
    k3 = ramp(t, c2 - 0.1, 0.5)
    rect(cv, (x0 - 6, hy + 2 * 54 + 24, x1 + 6, y1 + 6), (9, 9, 11), 0.8 * a * k3)
    put(cv, 'NOBODY HAD TOLD HIM WHAT THOSE RIGHTS WERE', 'bebas', 84, WHITE, (W / 2, 690), 'c', a * k3, track=2)
    put(cv, 'RECREATED AS TYPE, NOT A SCAN  ·  HIGHLIGHTED LINE AS QUOTED IN THE SUPREME COURT OPINION', 'mono', 20, GREY,
        (W / 2, 1036), 'c', a, track=1)
    return cv


def docket(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'STATE OF ARIZONA v. ERNESTO MIRANDA', 'monob', 28, GREY, (W / 2, 220), 'c', a, track=4)
    steps = [('OBJECTION', 'ALVIN MOORE, APPOINTED COUNSEL'), ('OVERRULED', 'JUDGE YALE McFATE'),
             ('CONVICTED', 'JUNE 1963  ·  20–30 YEARS'), ('AFFIRMED', 'ARIZONA SUPREME COURT  ·  1965')]
    xs = [300 + i * 440 for i in range(4)]; y = 470
    for i, (word, sub) in enumerate(steps):
        c = cue(cues, i, 0.5 + 2 * i); k = ramp(t, c - 0.1, 0.45)
        last = i == 3 or t < cue(cues, i + 1, 99)
        if i:
            w = (xs[i] - xs[i - 1] - 120) * k
            rect(cv, (xs[i - 1] + 60, y + 3, xs[i - 1] + 60 + w, y + 7), GREY, a)
        ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
        d.ellipse((xs[i] - 22, y - 17, xs[i] + 22, y + 27), fill=(*(AMBER if last else GREY), int(255 * a * k)))
        cv.alpha_composite(ov)
        put(cv, word, 'bebas', 92, WHITE if not last else AMBER, (xs[i], y + 70), 'c', a * k, track=2)
        put(cv, sub, 'mono', 21, GREY, (xs[i], y + 180), 'c', a * k)
    return cv


def warnings(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'BEFORE CUSTODIAL INTERROGATION, POLICE MUST WARN', 'monob', 26, GREY, (240, 150), alpha=a, track=4)
    rows = ['YOU CAN STAY SILENT', 'WHAT YOU SAY CAN BE USED AGAINST YOU', 'YOU CAN HAVE A LAWYER',
            "IF YOU CAN'T AFFORD ONE, YOU'LL GET ONE"]
    for i, txt in enumerate(rows):
        c = cue(cues, i, 0.4 + 2 * i); k = ramp(t, c - 0.1, 0.45); y = 220 + i * 150
        put(cv, f'0{i + 1}', 'monob', 30, AMBER, (240, y + 40), alpha=a * k)
        put(cv, txt, 'bebas', 100, WHITE, (330 + 40 * (1 - k), y), alpha=a * k, track=2)
    k5 = ramp(t, cue(cues, 4, 9.0) - 0.1, 0.5)
    rect(cv, (240, 846, 248, 920), AMBER, a * k5)
    put(cv, "NO WARNINGS: THE STATEMENT CAN'T BE USED TO PROVE THE CASE", 'monob', 32, WHITE, (276, 862), alpha=a * k5, track=2)
    put(cv, 'PARAPHRASE OF THE HOLDING  ·  THERE IS NO SINGLE OFFICIAL WORDING', 'mono', 21, DIM, (240, H - 84), alpha=a, track=1)
    return cv


MAJ = ['WARREN, C.J.', 'BLACK', 'DOUGLAS', 'BRENNAN', 'FORTAS']
DIS = ['CLARK', 'HARLAN', 'STEWART', 'WHITE']
QUOTE = ['"In some unknown number of cases the Court\'s rule',
         'will return a killer, a rapist or other criminal',
         'to the streets."']


def split(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1 = cue(cues, 0, 0.5), cue(cues, 1, 4.5)
    kq = ramp(t, c1 - 0.2, 0.6); top = 150 - 40 * kq
    put(cv, 'MIRANDA v. ARIZONA  ·  JUNE 13, 1966', 'monob', 26, GREY, (W / 2, top), 'c', a, track=4)
    for side, names, x, col, n in (('MAJORITY', MAJ, 520, AMBER, '5'), ('DISSENT', DIS, 1400, GREY, '4')):
        kd = 1.0 if side == 'MAJORITY' else ramp(t, c0 - 0.2, 0.5)
        dimq = 1 - 0.55 * kq * (side == 'MAJORITY') - 0.0
        put(cv, n, 'bebas', 190, col, (x, top + 50), 'c', a * kd * dimq)
        put(cv, side, 'monob', 28, col, (x, top + 250), 'c', a * kd * dimq, track=6)
        for i, nm in enumerate(names):
            k = ramp(t, 0.3 + 0.15 * i if side == 'MAJORITY' else c0 + 0.15 * i, 0.4)
            hl = side == 'DISSENT' and nm == 'WHITE' and kq > 0
            put(cv, nm, 'mono', 38, AMBER if hl else WHITE, (x, top + 310 + i * 56), 'c', a * k * kd * (dimq if not hl else 1))
    rect(cv, (W / 2 - 1, top + 70, W / 2 + 1, top + 560), DIM, a)
    if kq > 0:
        bottom_scrim(cv, 0.9 * kq, 420)
        for i, ln in enumerate(QUOTE):
            put(cv, ln, 'inter', 46, WHITE, (W / 2, 770 + i * 64), 'c', a * kq)
        put(cv, 'JUSTICE WHITE, DISSENTING  ·  QUOTE TO BE CHECKED AGAINST THE OPINION', 'mono', 21, GREY, (W / 2, 990), 'c', a * kq, track=1)
    return cv


def retrial(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    typed(cv, 'RETRIAL  ·  1967  ·  NO CONFESSION', t, 0.3, 'mono', 72, WHITE, (220, 330), cps=20, cursor=t < cue(cues, 0, 4), alpha=a)
    k1 = ramp(t, cue(cues, 0, 4.0), 0.5)
    put(cv, 'KEY WITNESS', 'monob', 26, GREY, (224, 480), alpha=a * k1, track=4)
    put(cv, 'HIS FORMER COMMON-LAW WIFE', 'bebas', 96, WHITE, (220 + 24 * (1 - k1), 516), alpha=a * k1, track=2)
    put(cv, 'WHAT HE TOLD HER DURING A JAIL VISIT', 'mono', 30, GREY, (224, 640), alpha=a * ramp(t, cue(cues, 0, 4.0) + 1.6, 0.5))
    k2 = ramp(t, cue(cues, 1, 11.0) - 0.1, 0.5)
    put(cv, 'CONVICTED AGAIN  ·  20–30 YEARS', 'bebas', 110, AMBER, (220, 740), alpha=a * k2, track=2)
    return cv


def timeline_card(t, dur, cues):
    """Evenly spaced, not to scale. 1966-2000 build on the VO; 2010 and 2022 wait, dim, for the next A-roll."""
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'IS IT STILL STANDING?', 'monob', 26, GREY, (200, 200), alpha=a, track=4)
    ev = [('1966', 'MIRANDA v. ARIZONA', '5–4'), ('1968', 'CONGRESS: 18 U.S.C. § 3501', 'A LAW TO GET AROUND IT'),
          ('2000', 'DICKERSON v. UNITED STATES', '7–2  ·  MIRANDA STANDS'),
          ('2010', 'BERGHUIS v. THOMPKINS', ''), ('2022', 'VEGA v. TEKOH', '')]
    xs = [260 + i * 350 for i in range(5)]; y = 500
    rect(cv, (xs[0], y, xs[0] + (xs[-1] - xs[0]) * ramp(t, 0.1, 1.2), y + 4), DIM, a)
    for i, (yr, name, sub) in enumerate(ev):
        live = i < 3; c = cue(cues, i, 0.5 + 3 * i) if live else 1.0
        k = ramp(t, c - 0.1, 0.5); x = xs[i]; cur = live and (i == 2 or t < cue(cues, i + 1, 99))
        col = AMBER if cur else (WHITE if live else DIM)
        ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
        d.ellipse((x - 14, y - 12, x + 14, y + 16), fill=(*col, int(255 * a * k)))
        cv.alpha_composite(ov)
        put(cv, yr, 'bebas', 96, col, (x, y - 130), 'c', a * k)
        ny = y + (60 if i % 2 == 0 else 150)
        put(cv, name, 'monob', 24, WHITE if live else DIM, (x, ny), 'c', a * k, track=2)
        put(cv, sub, 'mono', 22, GREY, (x, ny + 40), 'c', a * k)
    k4 = ramp(t, cue(cues, 3, 12.0) - 0.1, 0.5)
    put(cv, 'OPINION BY CHIEF JUSTICE REHNQUIST, A LONGTIME CRITIC', 'monob', 30, AMBER, (W / 2, 880), 'c', a * k4, track=3)
    return cv


def holding(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    rows = [('BEFORE QUESTIONING, NOT AT ARREST', 'The warning is required before custodial interrogation.'),
            ('LOSE THE STATEMENT, NOT THE CASE', 'He was convicted again without the confession.'),
            ('USE IT. OUT LOUD.', "Since 2010, silence alone doesn't invoke the right."),]
    for i, (h, sub) in enumerate(rows):
        c = cue(cues, i, 0.4 + 3 * i); k = ramp(t, c - 0.1, 0.5); y = 210 + i * 245
        cur = 1.0 if (i == len(rows) - 1 or t < cue(cues, i + 1, 99)) else 0.55
        put(cv, str(i + 1), 'bebas', 170, AMBER, (220, y - 10), alpha=a * k * cur)
        put(cv, h, 'bebas', 92, WHITE, (360 + 30 * (1 - k), y + 10), alpha=a * k * cur, track=2)
        put(cv, sub, 'inter', 40, GREY, (364 + 30 * (1 - k), y + 112), alpha=a * k * cur)
    return cv


def endcard(t, dur, cues):
    cv = card(); a = fade(t, 0.1, dur, 0.6, 1.2)
    put(cv, 'THE HOFFMAN FILES', 'bebas', 170, WHITE, (W / 2, 250), 'c', a, track=6)
    put(cv, 'LAW BY LAWYERS', 'monob', 30, AMBER, (W / 2, 450), 'c', a, track=10)
    put(cv, 'NEXT:  [NEXT CASE]', 'monob', 40, WHITE, (W / 2, 560), 'c', a * ramp(t, 0.8, 0.6), track=6)
    put(cv, 'Sources: Miranda v. Arizona, 384 U.S. 436 (1966); Dickerson v. United States, 530 U.S. 428 (2000);',
        'mono', 21, GREY, (W / 2, 760), 'c', a)
    put(cv, 'Berghuis v. Thompkins, 560 U.S. 370 (2010); Vega v. Tekoh, 597 U.S. 134 (2022). Full list in the description.',
        'mono', 21, GREY, (W / 2, 792), 'c', a)
    put(cv, '3D sequences are illustrations and reconstructions, not footage. No AI-generated imagery.', 'mono', 21, DIM, (W / 2, 850), 'c', a)
    put(cv, 'Theme: "Measured in Sunlight." Score: public domain recordings from the Musopen project.', 'mono', 21, DIM, (W / 2, 882), 'c', a)
    return cv


def black(t, dur, cues):
    return Image.new('RGBA', (W, H), (0, 0, 0, 255))


# ---------------------------------------------------------------- overlays on 3D plates
def ov_busstop(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4)
    tag(cv, 'ILLUSTRATION', 'A GENERIC STOP  ·  NO ONE IS SHOWN', a)


def ov_room(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.01)
    tag(cv, 'RECONSTRUCTION', 'LAYOUT ILLUSTRATIVE', a)
    bottom_scrim(cv, 0.75, 300)
    put(cv, 'INTERROGATION ROOM NO. 2  ·  MARCH 13, 1963', 'monob', 30, WHITE, (W / 2, 950), 'c', a * ramp(t, cue(cues, 0, 6.0), 0.6), track=3)


def ov_room_hold(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.01, 0.4)
    tag(cv, 'RECONSTRUCTION', 'LAYOUT ILLUSTRATIVE', a)
    bottom_scrim(cv, 0.75, 300)
    k = ramp(t, cue(cues, 0, 3.5) - 0.1, 0.5)
    put(cv, 'NO WARNING  ·  NO LAWYER', 'bebas', 92, AMBER, (W / 2, 912), 'c', a * k, track=3)


def ov_bench(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4)
    tag(cv, 'ILLUSTRATION', 'AN ABSTRACT BENCH, NOT THE REAL COURTROOM', a)
    put(cv, 'JUNE 13, 1966', 'monob', 30, WHITE, (W - 64, 100), 'r', a * ramp(t, cue(cues, 0, 3.0), 0.5), track=3)
    k = ramp(t, cue(cues, 1, 6.0) + 3.8, 0.6)                 # once the fifth chair is lit
    bottom_scrim(cv, 0.85 * k, 330)
    put(cv, '5–4', 'bebas', 170, AMBER, (W / 2, 830), 'c', a * k, track=6)


def ov_cards(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4)
    tag(cv, 'ILLUSTRATION', 'GENERIC CARDS  ·  NO SIGNATURE SHOWN', a)
    put(cv, 'PAROLED 1972', 'monob', 30, WHITE, (W - 64, 100), 'r', a * ramp(t, 0.8, 0.5), track=3)
    k = ramp(t, cue(cues, 0, 7.0), 0.6)
    bottom_scrim(cv, 0.8 * k, 300)
    put(cv, '$1.50 A CARD  ·  REPORTEDLY', 'bebas', 92, AMBER, (W / 2, 912), 'c', a * k, track=3)


def ov_bar(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.01)
    tag(cv, 'ILLUSTRATION', 'A GENERIC BUILDING, NOT THE ACTUAL BAR', a)
    put(cv, 'JANUARY 31, 1976  ·  PHOENIX', 'monob', 30, WHITE, (W - 64, 100), 'r', a * ramp(t, 0.6, 0.5), track=3)
    bottom_scrim(cv, 0.8, 360)
    rows = ['SUSPECT READ HIS RIGHTS', 'HE INVOKES THEM', 'RELEASED', 'THE MAN LATER CHARGED: NEVER TRIED']
    for i, txt in enumerate(rows):
        k = ramp(t, cue(cues, i, 6 + 2 * i) - 0.1, 0.4)
        put(cv, txt, 'monob', 28, AMBER if i == 3 else WHITE, (120, 800 + i * 50), alpha=a * k, track=3)


OVERLAYS = dict(busstop=ov_busstop, room=ov_room, room_hold=ov_room_hold, bench=ov_bench, cards=ov_cards, bar=ov_bar)
OVERLAY_CUES = dict(room=['into Interrogation Room'], room_hold=['And nobody told'], bench=['On June 13', 'five to four'],
                    cards=['a dollar fifty'],
                    bar=["He's read his rights", 'He invokes them', "He's released", 'The man later charged'])
CARDS = dict(title=title, phoenix=phoenix, form=form, docket=docket, warnings=warnings, split=split, retrial=retrial,
             timeline=timeline_card, holding_title=_g.holding_title, holding=holding, endcard=endcard, black=black)
