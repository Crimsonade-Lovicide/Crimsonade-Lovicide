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
    put(cv, 'ERNESTO MIRANDA', 'bebas', 120, AMBER, (220 + 24 * (1 - k2), 590), alpha=a * k2, track=3)
    return cv


FORM = ['I, Ernest A. Miranda, do hereby swear that I make this',
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
    put(cv, 'RECREATED AS TYPE, NOT A SCAN  ·  TEXT AS QUOTED IN STATE v. MIRANDA, 98 ARIZ. 18 (1965)', 'mono', 20, GREY,
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
        put(cv, 'JUSTICE WHITE, DISSENTING  ·  MIRANDA v. ARIZONA, 384 U.S. 436 (1966)', 'mono', 21, GREY, (W / 2, 990), 'c', a * kq, track=1)
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
    """Evenly spaced, not to scale. 1966-1984 build on the VO; 2000 onward wait, dim, for the next beats."""
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'IS IT STILL STANDING?', 'monob', 26, GREY, (180, 200), alpha=a, track=4)
    ev = [('1966', 'MIRANDA v. ARIZONA', '5–4'), ('1968', 'CONGRESS: 18 U.S.C. § 3501', 'VOLUNTARY = ADMISSIBLE'),
          ('1971', 'HARRIS v. NEW YORK', 'USED TO IMPEACH'), ('1984', 'NEW YORK v. QUARLES', 'PUBLIC SAFETY EXCEPTION'),
          ('2000', 'DICKERSON v. U.S.', ''), ('2010', 'BERGHUIS v. THOMPKINS', ''), ('2022', 'VEGA v. TEKOH', '')]
    n_live = 4; xs = [220 + i * 247 for i in range(len(ev))]; y = 500
    rect(cv, (xs[0], y, xs[0] + (xs[-1] - xs[0]) * ramp(t, 0.1, 1.2), y + 4), DIM, a)
    for i, (yr, name, sub) in enumerate(ev):
        live = i < n_live; c = cue(cues, i, 0.5 + 3 * i) if live else 1.0
        k = ramp(t, c - 0.1, 0.5); x = xs[i]; cur = live and (i == n_live - 1 or t < cue(cues, i + 1, 99))
        col = AMBER if cur else (WHITE if live else DIM)
        ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
        d.ellipse((x - 14, y - 12, x + 14, y + 16), fill=(*col, int(255 * a * k)))
        cv.alpha_composite(ov)
        put(cv, yr, 'bebas', 88, col, (x, y - 124), 'c', a * k)
        ny = y + (60 if i % 2 == 0 else 150)
        put(cv, name, 'monob', 22, WHITE if live else DIM, (x, ny), 'c', a * k, track=2)
        put(cv, sub, 'mono', 20, GREY, (x, ny + 38), 'c', a * k)
    k4 = ramp(t, cue(cues, 4, 18.0) - 0.1, 0.5)
    put(cv, '1984 OPINION: JUSTICE WILLIAM REHNQUIST', 'monob', 30, AMBER, (W / 2, 880), 'c', a * k4, track=3)
    return cv


def dickerson(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 1.0), cue(cues, 1, 7.0), cue(cues, 2, 11.0)
    put(cv, '2000', 'bebas', 150, AMBER, (220, 150), alpha=a * ramp(t, 0.2, 0.5))
    put(cv, 'DICKERSON v. UNITED STATES', 'bebas', 96, WHITE, (220, 300), alpha=a * ramp(t, c0 - 0.1, 0.5), track=2)
    k1 = ramp(t, c1 - 0.1, 0.5)
    put(cv, '7–2  ·  MIRANDA STANDS  ·  OPINION: CHIEF JUSTICE REHNQUIST', 'monob', 28, GREY, (224, 420), alpha=a * k1, track=3)
    kq = ramp(t, c2 - 0.2, 0.7)
    rect(cv, (220, 540, 228, 800), AMBER, a * kq)
    for i, ln in enumerate(['"Miranda has become embedded in routine police practice',
                            'to the point where the warnings have become part of',
                            'our national culture."']):
        put(cv, ln, 'inter', 50, WHITE, (262, 548 + i * 76), alpha=a * kq)
    put(cv, 'DICKERSON v. UNITED STATES, 530 U.S. 428 (2000)', 'mono', 21, GREY, (262, 790), alpha=a * kq, track=1)
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


def brown(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2, c3 = cue(cues, 0, 1.0), cue(cues, 1, 6.0), cue(cues, 2, 10.0), cue(cues, 3, 16.0)
    put(cv, '1936', 'bebas', 150, AMBER, (220, 150), alpha=a * ramp(t, 0.2, 0.5))
    put(cv, 'BROWN v. MISSISSIPPI', 'bebas', 104, WHITE, (220, 300), alpha=a * ramp(t, c0 - 0.1, 0.5), track=2)
    k1 = ramp(t, c1 - 0.3, 0.5)
    put(cv, 'CONFESSIONS WHIPPED OUT OF THREE MEN  ·  THROWN OUT', 'monob', 28, GREY, (224, 426), alpha=a * k1, track=3)
    k2 = ramp(t, c2 - 0.6, 0.5)
    put(cv, 'THE TEST AFTER 1936: WAS IT VOLUNTARY?', 'monob', 30, WHITE, (224, 560), alpha=a * k2, track=3)
    put(cv, 'HOW LONG  ·  HOW OLD  ·  HOW EDUCATED  ·  ANY THREATS', 'mono', 30, GREY, (224, 616), alpha=a * ramp(t, c2, 0.5))
    k3 = ramp(t, c3 - 0.1, 0.5)
    put(cv, 'MIRANDA, 1963: NO FORCE, NO THREATS, TWO HOURS  =  VOLUNTARY', 'bebas', 76, AMBER, (220, 740), alpha=a * k3, track=2)
    source(cv, 'Brown v. Mississippi, 297 U.S. 278 (1936)', a)
    return cv


def precedents(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 1.5), cue(cues, 1, 9.0), cue(cues, 2, 18.0)
    put(cv, 'THE LAW AROUND HIM WAS MOVING', 'monob', 26, GREY, (220, 170), alpha=a, track=4)
    rows = [(c0, 'MARCH 18, 1963', 'GIDEON v. WAINWRIGHT', 'Charged with a felony and can\'t afford a lawyer? The state provides one.'),
            (c1, 'JUNE 22, 1964', 'ESCOBEDO v. ILLINOIS', 'He asked for his lawyer and was refused. The confession was thrown out.')]
    for i, (c, date, name, sub) in enumerate(rows):
        k = ramp(t, c - 0.1, 0.5); y = 250 + i * 250
        put(cv, date, 'monob', 28, AMBER, (220, y), alpha=a * k, track=3)
        put(cv, name, 'bebas', 100, WHITE, (220 + 30 * (1 - k), y + 40), alpha=a * k, track=2)
        put(cv, sub, 'inter', 38, GREY, (224 + 30 * (1 - k), y + 150), alpha=a * k)
    put(cv, 'FIVE DAYS AFTER MIRANDA\'S CONFESSION', 'mono', 22, DIM, (W - 220, 258), 'r', a * ramp(t, c0 + 0.6, 0.5), track=1)
    k2 = ramp(t, c2 - 0.1, 0.5)
    rect(cv, (220, 790, 228, 860), AMBER, a * k2)
    put(cv, "THE OPEN QUESTION: WHAT ABOUT THE SUSPECT WHO DOESN'T KNOW TO ASK?", 'monob', 32, WHITE, (256, 806), alpha=a * k2, track=2)
    return cv


def manuals(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'FROM THE POLICE MANUALS THE COURT QUOTED', 'monob', 26, GREY, (240, 150), alpha=a, track=4)
    rows = ['QUESTION HIM ALONE, ON YOUR GROUND', 'TREAT HIS GUILT AS SETTLED', 'OFFER AN EXCUSE THAT MAKES CONFESSING EASIER',
            'FRIENDLY DETECTIVE, HOSTILE DETECTIVE']
    kq = ramp(t, cue(cues, 4, 14.0) - 0.2, 0.6)
    for i, txt in enumerate(rows):
        c = cue(cues, i, 0.5 + 2 * i); k = ramp(t, c - 0.1, 0.45); y = 210 + i * 120
        put(cv, f'0{i + 1}', 'monob', 28, AMBER, (240, y + 34), alpha=a * k * (1 - 0.5 * kq))
        put(cv, txt, 'bebas', 84, WHITE, (330 + 40 * (1 - k), y), alpha=a * k * (1 - 0.5 * kq), track=2)
    if kq > 0:
        bottom_scrim(cv, 0.9 * kq, 400)
        for i, ln in enumerate(['"...created for no purpose other than to subjugate', 'the individual to the will of his examiner."']):
            put(cv, ln, 'inter', 48, WHITE, (W / 2, 750 + i * 70), 'c', a * kq)
        put(cv, 'MIRANDA v. ARIZONA, 384 U.S. 436 (1966)', 'mono', 21, GREY, (W / 2, 900), 'c', a * kq, track=1)
    source(cv, 'Tactics paraphrased from the manuals quoted in the opinion', a * (1 - kq))
    return cv


def cost(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 3.0), cue(cues, 1, 8.0), cue(cues, 2, 12.0)
    put(cv, 'WHAT DOES MIRANDA COST?', 'monob', 26, GREY, (260, 170), alpha=a, track=4)
    put(cv, 'ESTIMATED SHARE OF ALL CRIMINAL CASES LOST', 'mono', 24, GREY, (260, 216), alpha=a, track=1)
    x0, full = 260, 1300
    for i, (c, who, pct, col) in enumerate(((c0, 'PAUL CASSELL, 1996', 3.8, AMBER), (c1, 'STEPHEN SCHULHOFER, 1996', 1.1, WHITE))):
        k = ramp(t, c - 0.1, 0.9); y = 330 + i * 200
        put(cv, who, 'monob', 28, col, (x0, y), alpha=a * ramp(t, c - 0.1, 0.4), track=3)
        wv = full * pct / 4.0 * k
        rect(cv, (x0, y + 50, x0 + max(2, wv), y + 120), col, a * ramp(t, c - 0.1, 0.3))
        lab = f'{pct * k:.1f}%' if i == 0 else f'0.78–{max(0.78, pct * k):.1f}%'
        put(cv, lab, 'bebas', 96, WHITE, (x0 + wv + 30, y + 34), alpha=a * ramp(t, c - 0.1, 0.4))
    k2 = ramp(t, c2 - 0.1, 0.5)
    put(cv, 'WHAT THE STUDIES AGREE ON: ABOUT 4 IN 5 SUSPECTS WAIVE', 'bebas', 80, AMBER, (260, 790), alpha=a * k2, track=2)
    source(cv, 'Cassell; Schulhofer, 90 Nw. U. L. Rev. (1996); Leo (1996)  ·  estimates, contested', a)
    return cv


def say_it(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2, c3 = cue(cues, 0, 2.0), cue(cues, 1, 8.0), cue(cues, 2, 10.0), cue(cues, 3, 14.0)
    k0 = ramp(t, c0 - 0.1, 0.5); dim0 = 1 - 0.6 * ramp(t, c1 - 0.3, 0.4)
    put(cv, 'NOT ENOUGH  ·  DAVIS v. UNITED STATES, 1994', 'monob', 26, GREY, (W / 2, 200), 'c', a * k0 * dim0, track=4)
    put(cv, '"Maybe I should talk to a lawyer."', 'inter', 54, GREY, (W / 2, 250), 'c', a * k0 * dim0)
    sw = text_w('"Maybe I should talk to a lawyer."', 'inter', 54)
    rect(cv, (W / 2 - sw / 2, 290, W / 2 - sw / 2 + sw * ramp(t, c0 + 2.0, 0.5), 296), AMBER, a * k0 * dim0)
    put(cv, 'CLEAR', 'monob', 26, AMBER, (W / 2, 420), 'c', a * ramp(t, c1 - 0.3, 0.4), track=8)
    put(cv, "I'M GOING TO REMAIN SILENT.", 'bebas', 130, WHITE, (W / 2, 470), 'c', a * ramp(t, c1 - 0.1, 0.5), track=3)
    put(cv, 'I WANT A LAWYER.', 'bebas', 130, WHITE, (W / 2, 610), 'c', a * ramp(t, c2 - 0.1, 0.5), track=3)
    put(cv, 'THEN STOP TALKING.', 'monob', 32, AMBER, (W / 2, 790), 'c', a * ramp(t, c2 + 1.2, 0.5), track=6)
    put(cv, 'GENERAL INFORMATION, NOT LEGAL ADVICE ABOUT YOUR CASE', 'mono', 21, DIM, (W / 2, H - 84), 'c', a * ramp(t, c3 - 0.1, 0.5), track=1)
    return cv


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
             timeline=timeline_card, dickerson=dickerson, brown=brown, precedents=precedents, manuals=manuals, cost=cost,
             say_it=say_it, holding_title=_g.holding_title, holding=holding, endcard=endcard, black=black)
