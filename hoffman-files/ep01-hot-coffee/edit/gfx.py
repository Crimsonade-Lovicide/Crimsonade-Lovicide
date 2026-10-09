"""Motion graphics for The Hoffman Files, ep. 1. Every function draws one 1920x1080 frame at time t.

Cards  (gfx kind):  f(t, dur, cues) -> RGBA frame. `cues` are the times (s) when cue phrases are spoken.
Overlays (blender): f(cv, t, dur, frame, tr, cues) draws on top of a 3D plate; `frame` is the source frame.
Look: near-black, off-white type, one amber accent (the coffee/heat colour of the 3D scenes).
"""
import math, os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('FONT_DIR', os.path.join(HERE, '..', 'fonts'))
W, H, FPS = 1920, 1080, 24
BG = (9, 9, 11)
WHITE, GREY, DIM = (238, 236, 230), (165, 167, 173), (110, 112, 118)
AMBER = (236, 140, 52)
FONTS = dict(bebas='BebasNeue.ttf', mono='PlexMono.ttf', monob='PlexMonoSemi.ttf', inter='Inter.ttf')


# ---------------------------------------------------------------- primitives
@lru_cache(maxsize=None)
def font(name, size):
    f = ImageFont.truetype(os.path.join(FONT_DIR, FONTS[name]), size)
    if name == 'inter':
        f.set_variation_by_name('Medium')
    return f


@lru_cache(maxsize=4096)
def text_img(text, fname, size, color, track=0, shadow=True):
    f = font(fname, size)
    widths = [f.getlength(ch) + track for ch in text] if track else None
    tw = int(sum(widths)) if track else int(f.getlength(text))
    asc, desc = f.getmetrics(); pad = 18
    im = Image.new('RGBA', (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    def draw(img, fill, off=(0, 0)):
        d = ImageDraw.Draw(img); x = pad + off[0]
        if track:
            for ch, w in zip(text, widths): d.text((x, pad + off[1]), ch, font=f, fill=fill); x += w
        else:
            d.text((x, pad + off[1]), text, font=f, fill=fill)
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); draw(sh, (0, 0, 0, 190), (0, 2))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5)))
    draw(im, (*color, 255))
    return im, pad


def text_w(text, fname, size, track=0):
    f = font(fname, size)
    return sum(f.getlength(c) + track for c in text) if track else f.getlength(text)


def put(cv, text, fname, size, color, xy, anchor='l', alpha=1.0, track=0, shadow=True, scale=1.0):
    if alpha <= 0.01 or not text: return
    im, pad = text_img(text, fname, size, tuple(color), track, shadow)
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS); pad = int(pad * scale)
    if alpha < 0.99:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    x, y = xy; w = im.width - 2 * pad
    if anchor == 'c': x -= w / 2
    elif anchor == 'r': x -= w
    cv.alpha_composite(im, (int(x - pad), int(y - pad)))


def rect(cv, box, color, alpha=1.0):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    if alpha <= 0.01 or x1 <= x0 or y1 <= y0: return
    cv.alpha_composite(Image.new('RGBA', (x1 - x0, y1 - y0), (*color, int(255 * alpha))), (x0, y0))


def line(cv, pts, color, width, alpha=1.0):
    if alpha <= 0.01: return
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).line(pts, fill=(*color, int(255 * alpha)), width=width, joint='curve')
    cv.alpha_composite(ov)


def fade(t, a, b=1e9, fi=0.35, fo=0.35):
    if t < a or t > b: return 0.0
    return max(0.0, min(1.0, (t - a) / fi if fi else 1, (b - t) / fo if fo else 1))


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def ramp(t, a, d):
    return ease((t - a) / d) if d else float(t >= a)


def money(v):
    return f'${int(round(v)):,}'


@lru_cache(maxsize=1)
def backdrop():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W * 0.42) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    lift = np.clip(1 - r * 1.6, 0, 1) ** 2 * 10
    a = np.stack([np.full((H, W), c, np.float32) + lift for c in BG], -1)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')


def card():
    return backdrop().copy()


def bug(cv, alpha=0.55):
    put(cv, 'THE HOFFMAN FILES', 'monob', 20, GREY, (W - 64, 52), 'r', alpha, track=3, shadow=False)


def source(cv, text, alpha=1.0):
    put(cv, 'SOURCE  ·  ' + text.upper(), 'mono', 21, GREY, (64, H - 84), alpha=alpha, track=1)


def tag(cv, text, sub=None, alpha=1.0, xy=(64, 52)):
    wbox = max(text_w(text, 'monob', 22, 3), text_w(sub, 'mono', 20, 1) if sub else 0)
    rect(cv, (xy[0] - 16, xy[1] - 12, xy[0] + wbox + 16, xy[1] + (70 if sub else 40)), (0, 0, 0), 0.55 * alpha)
    put(cv, text, 'monob', 22, AMBER, xy, alpha=alpha, track=3)
    if sub: put(cv, sub, 'mono', 20, GREY, (xy[0], xy[1] + 34), alpha=alpha, track=1)


def typed(cv, text, t, t0, fname, size, color, xy, cps=20, cursor=True, alpha=1.0, track=0):
    n = int(max(0, (t - t0)) * cps)
    put(cv, text[:n], fname, size, color, xy, alpha=alpha, track=track)
    if cursor and t >= t0 and (n < len(text) or int(t * 2.2) % 2 == 0):
        x = xy[0] + text_w(text[:n], fname, size, track) + 8
        rect(cv, (x, xy[1] + size * 0.18, x + size * 0.42, xy[1] + size * 1.08), AMBER, alpha)
    return n >= len(text)


def scrim(cv, side='left', strength=0.75, width=1150):
    a = (np.clip(1 - np.linspace(0, 1, width) ** 1.5, 0, 1) * 255 * strength).astype(np.uint8)
    if side == 'right': a = a[::-1]
    im = np.zeros((H, width, 4), np.uint8); im[..., 3] = a[None, :]
    cv.alpha_composite(Image.fromarray(im, 'RGBA'), (0 if side == 'left' else W - width, 0))


def bottom_scrim(cv, strength=0.8, height=420):
    a = (np.clip(np.linspace(0, 1, height) ** 1.4, 0, 1) * 255 * strength).astype(np.uint8)
    im = np.zeros((height, W, 4), np.uint8); im[..., 3] = a[:, None]
    cv.alpha_composite(Image.fromarray(im, 'RGBA'), (0, H - height))


def cue(cues, i, default=0.0):
    return cues[i] if cues and i < len(cues) and cues[i] is not None else default


# ---------------------------------------------------------------- lower thirds
def lower_third(cv, name, title, t=10.0, t0=0.0, out=None, x=120, y=846):
    """Animated name strap. With t >= t0 + 1 it is fully on."""
    a = fade(t, t0, out if out else 1e9, 0.25, 0.3)
    if a <= 0: return
    grow = ramp(t, t0, 0.45)
    rect(cv, (x - 24, y - 18, x - 24 + 900 * grow, y + 112), (0, 0, 0), 0.55 * a)
    rect(cv, (x - 24, y - 18, x - 16, y + 112), AMBER, a)
    k = ramp(t, t0 + 0.15, 0.5)
    put(cv, name, 'bebas', 70, WHITE, (x + 6 + 18 * (1 - k), y - 8), alpha=a * k, track=2)
    put(cv, title, 'monob', 24, GREY, (x + 8 + 18 * (1 - k), y + 66), alpha=a * ramp(t, t0 + 0.3, 0.5), track=2)


# ---------------------------------------------------------------- cards
def title(t, dur, cues):
    cv = card(); a = fade(t, 0.15, dur, 0.6, 0.6)
    tr = 6 + 34 * (1 - ramp(t, 0.15, 1.8))
    put(cv, 'EPISODE 1', 'monob', 26, GREY, (W / 2, 330), 'c', a * ramp(t, 0.6, 0.6), track=8)
    put(cv, 'THE HOFFMAN FILES', 'bebas', 230, WHITE, (W / 2, 390), 'c', a, track=tr)
    w = 820 * ramp(t, 0.7, 1.0)
    rect(cv, (W / 2 - w / 2, 650, W / 2 + w / 2, 654), AMBER, a)
    put(cv, 'THE HOT COFFEE CASE', 'monob', 44, AMBER, (W / 2, 690), 'c', a * ramp(t, 1.2, 0.7), track=10)
    return cv


def headline(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'THE VERSION EVERYONE HEARD', 'monob', 26, GREY, (220, 340), alpha=a, track=4)
    done = typed(cv, 'Woman sues over spilled coffee.', t, 0.5, 'mono', 76, WHITE, (220, 410), cps=22,
                 cursor=False, alpha=a)
    typed(cv, 'Wins millions.', t, 0.5 + 31 / 22 + 0.35, 'mono', 76, WHITE, (220, 510), cps=16, alpha=a)
    put(cv, 'A COMPOSITE OF THE COVERAGE, NOT A REAL HEADLINE', 'mono', 21, DIM, (220, 640),
        alpha=a * ramp(t, 3.2, 0.6), track=1)
    return cv


def injuries(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'THE INJURIES', 'monob', 26, GREY, (240, 200), alpha=a, track=4)
    rows = ['8 DAYS IN THE HOSPITAL', 'SKIN GRAFTS', 'LOST ABOUT 20 LB, DOWN TO 83 LB', '2 YEARS OF TREATMENT']
    for i, txt in enumerate(rows):
        c = cue(cues, i, 0.4 + i); k = ramp(t, c - 0.1, 0.45); y = 270 + i * 150
        put(cv, f'0{i + 1}', 'monob', 30, AMBER, (240, y + 40), alpha=a * k)
        put(cv, txt, 'bebas', 104, WHITE, (330 + 40 * (1 - k), y), alpha=a * k, track=2)
    source(cv, 'Trial evidence as reported, 1994', a)
    return cv


def temperature(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 1.0), cue(cues, 1, 5.0), cue(cues, 2, 10.0)
    # ---- thermometer (left)
    tx, top, bot = 560, 220, 800
    def ty(f): return bot - (f - 120) / 80 * (bot - top)        # 120..200 F
    put(cv, 'COFFEE TEMPERATURE', 'monob', 26, GREY, (tx, 140), 'c', a, track=4)
    rect(cv, (tx - 34, top - 20, tx + 34, bot + 10), (40, 40, 46), a)
    for f in range(120, 201, 10):
        rect(cv, (tx - 70, ty(f) - 1, tx - 44, ty(f) + 1), GREY, a)
        put(cv, f'{f}°', 'mono', 24, GREY if f not in (180, 190) else WHITE, (tx - 84, ty(f) - 17), 'r', a)
    band = ramp(t, c0, 0.6)
    rect(cv, (tx + 40, ty(190), tx + 52, ty(180)), AMBER, a * band)
    put(cv, "McDONALD'S", 'monob', 22, AMBER, (tx + 70, ty(190) - 6), alpha=a * band, track=2)
    put(cv, 'HOLDING STANDARD', 'monob', 22, AMBER, (tx + 70, ty(190) + 24), alpha=a * band, track=2)
    put(cv, '180–190°F', 'mono', 22, WHITE, (tx + 70, ty(190) + 54), alpha=a * band)
    if t < c1: level = 120 + 70 * ramp(t, 0.2, max(0.6, c0 + 0.8))
    elif t < c2: level = 190
    else: level = 190 - 10 * ramp(t, c2, 0.8)
    rect(cv, (tx - 20, ty(level), tx + 20, bot + 10), AMBER, a)
    ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
    d.ellipse((tx - 62, bot - 20, tx + 62, bot + 104), fill=(*AMBER, int(255 * a)))
    cv.alpha_composite(ov)
    if t >= c1:
        put(cv, f'{int(round(level))}°F', 'bebas', 96, WHITE, (tx + 66, ty(level) + 92), alpha=a * ramp(t, c1, 0.4))
    # ---- stopwatch (right)
    cx, cy, R = 1330, 520, 250
    act = 0.35 + 0.65 * ramp(t, c1 - 0.2, 0.5)
    put(cv, 'TIME TO A THIRD-DEGREE BURN', 'monob', 26, GREY, (cx, 140), 'c', a, track=4)
    ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(24, 24, 28, int(255 * a)), outline=(*GREY, int(200 * a * act)), width=5)
    d.rectangle((cx - 22, cy - R - 46, cx + 22, cy - R - 6), fill=(*GREY, int(255 * a * act)))
    secs = 0.0
    if c1 <= t < c2:
        secs = min(3.0, t - (c1 + 0.6)) if t > c1 + 0.6 else 0.0          # real-time sweep to 3 s
    elif t >= c2:
        secs = 15.0 * ramp(t, c2 + 0.3, 1.4)
    if t >= c2:                                                       # shaded 12-15 s window
        sa = ramp(t, c2 + 1.2, 0.5)
        d.pieslice((cx - R + 16, cy - R + 16, cx + R - 16, cy + R - 16), -90 + 72, -90 + 90, fill=(*AMBER, int(110 * a * sa)))
    for s in range(60):
        ang = math.radians(s * 6 - 90); r0 = R - (34 if s % 5 == 0 else 18)
        d.line((cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + (R - 8) * math.cos(ang), cy + (R - 8) * math.sin(ang)),
               fill=(*GREY, int(255 * a * act)), width=4 if s % 5 == 0 else 2)
    ang = math.radians(secs * 6 - 90)
    d.line((cx, cy, cx + (R - 40) * math.cos(ang), cy + (R - 40) * math.sin(ang)), fill=(*AMBER, int(255 * a * act)), width=8)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(*AMBER, int(255 * a * act)))
    cv.alpha_composite(ov)
    for s, lab in ((0, '0'), (15, '15'), (30, '30'), (45, '45')):
        ang = math.radians(s * 6 - 90)
        put(cv, lab, 'mono', 26, GREY, (cx + (R - 72) * math.cos(ang), cy + (R - 72) * math.sin(ang) - 18), 'c', a * act)
    if c1 <= t < c2:
        put(cv, 'AT 190°F: ABOUT 3 SECONDS', 'bebas', 84, AMBER, (cx, cy + R + 40), 'c', a * ramp(t, c1 + 0.5, 0.5))
    elif t >= c2:
        put(cv, 'AT 180°F: 12–15 SECONDS', 'bebas', 84, AMBER, (cx, cy + R + 40), 'c', a * ramp(t, c2 + 0.3, 0.5))
    source(cv, 'Expert testimony at trial', a)
    return cv


LEDGER = [("Past medical bills", 10500), ("Future care (estimated)", 2500), ("Daughter's lost income", 5000)]


def _ledger(cv, t, cues, a, dim=1.0):
    x0, x1, y = 430, 1490, 250
    put(cv, "WHAT SHE ASKED McDONALD'S TO COVER", 'monob', 28, AMBER, (x0, y - 70), alpha=a * dim, track=3)
    for i, (lab, amt) in enumerate(LEDGER):
        c = cue(cues, i, 0.4 + i); k = ramp(t, c - 0.1, 0.4); yy = y + i * 96
        put(cv, lab, 'mono', 46, WHITE, (x0, yy), alpha=a * k * dim)
        lw = text_w(lab, 'mono', 46); dots = '.' * int((x1 - x0 - lw - 260) / text_w('.', 'mono', 46))
        put(cv, dots, 'mono', 46, DIM, (x0 + lw + 10, yy), alpha=a * k * dim, shadow=False)
        put(cv, money(amt * ramp(t, c, 0.6)), 'mono', 46, WHITE, (x1, yy), 'r', a * k * dim)
    c3 = cue(cues, 3, 4.0); k = ramp(t, c3 - 0.6, 0.4); yy = y + 3 * 96 + 10
    rect(cv, (x0, yy - 14, x1, yy - 11), GREY, a * k * dim)
    put(cv, 'Costs, itemized', 'mono', 46, GREY, (x0, yy + 6), alpha=a * k * dim)
    put(cv, 'about $18,000', 'mono', 46, GREY, (x1, yy + 6), 'r', a * k * dim)
    k2 = ramp(t, c3, 0.45)
    put(cv, 'SHE ASKED FOR', 'monob', 34, WHITE, (x0, yy + 140), alpha=a * k2 * dim, track=3)
    put(cv, '$20,000', 'bebas', 150, AMBER, (x1, yy + 92), 'r', a * k2 * dim)


def ledger(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.01)
    _ledger(cv, t, cues, a)
    source(cv, 'Trial record as reported', a)
    return cv


def offer(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.01, 0.5)
    _ledger(cv, 99, [0, 0, 0, 0], a, dim=0.14)
    k = ramp(t, 0.35, 0.35)
    rect(cv, (300, 140, 1620, 860), (8, 8, 10), 0.97 * a * k)
    put(cv, "McDONALD'S OFFERED", 'monob', 40, WHITE, (W / 2, 430), 'c', a * k, track=6)
    put(cv, '$800', 'bebas', 300, AMBER, (W / 2, 470), 'c', a * k, scale=1.0 + 0.12 * (1 - k))
    return cv


def claims(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    v = 500000 * ramp(t, 0.3, 2.2)
    put(cv, money(v) + ('+' if v >= 499999 else ''), 'bebas', 260, AMBER, (W / 2, 330), 'c', a)
    put(cv, 'PAID TO SETTLE BURN CLAIMS, 1982–1992', 'monob', 34, WHITE, (W / 2, 640), 'c', a * ramp(t, 0.8, 0.6), track=4)
    source(cv, 'Evidence at trial', a)
    return cv


def qa(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'TESTIMONY AT TRIAL', 'monob', 26, AMBER, (220, 260), alpha=a, track=4)
    typed(cv, "McDONALD'S QUALITY-ASSURANCE MANAGER", t, 0.3, 'bebas', 84, WHITE, (220, 300), cps=34, cursor=False,
          alpha=a, track=2)
    k = ramp(t, 2.6, 0.7)
    rect(cv, (220, 470, 228, 700), AMBER, a * k)
    for i, ln in enumerate(['In substance: 700 burn reports were not enough',
                            'to make the company change how it served coffee.']):
        put(cv, ln, 'inter', 54, WHITE, (262, 480 + i * 80), alpha=a * k)
    put(cv, 'PARAPHRASE OF HIS TESTIMONY, NOT A DIRECT QUOTE', 'mono', 21, DIM, (262, 660), alpha=a * k, track=1)
    return cv


def fault(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 2.0), cue(cues, 1, 5.0), cue(cues, 2, 8.0)
    put(cv, "THE JURY'S FAULT SPLIT", 'monob', 26, GREY, (260, 200), alpha=a, track=4)
    x0, x1, y0, y1 = 260, 1660, 400, 500
    grow = ramp(t, 0.2, 0.9); split = ramp(t, c0 - 0.2, 0.7); xs = x0 + 0.8 * (x1 - x0)
    rect(cv, (x0, y0, x0 + (xs - x0) * min(1, grow / 0.8) if grow < 0.8 else xs, y1), AMBER, a)
    if grow > 0.8:
        rect(cv, (xs + 14 * split, y0, x0 + (x1 - x0) * grow + 14 * split, y1), AMBER if split < 0.5 else GREY, a)
    put(cv, "McDONALD'S", 'monob', 26, AMBER, (x0, 270), alpha=a * ramp(t, 0.8, 0.5), track=3)
    put(cv, '80%', 'bebas', 110, WHITE, (x0, 296), alpha=a * ramp(t, 0.8, 0.5))
    put(cv, 'LIEBECK', 'monob', 26, GREY, (x1 + 14, 270), 'r', a * split, track=3)
    put(cv, '20%', 'bebas', 110, WHITE, (x1 + 14, 296), 'r', a * split)
    k1 = ramp(t, c1 - 0.3, 0.5)
    put(cv, 'COMPENSATORY DAMAGES', 'monob', 26, GREY, (x0, 600), alpha=a * k1, track=4)
    put(cv, '$200,000', 'bebas', 150, WHITE, (x0, 640), alpha=a * k1 * (1 - 0.55 * ramp(t, c2, 0.4)))
    k2 = ramp(t, c2 - 0.1, 0.5)
    if k2 > 0:
        sw = text_w('$200,000', 'bebas', 150)
        rect(cv, (x0 - 6, 722, x0 - 6 + (sw + 12) * k2, 730), AMBER, a)
        put(cv, '−20%  →', 'monob', 40, GREY, (x0 + sw + 60, 700), alpha=a * k2)
        put(cv, '$160,000', 'bebas', 150, AMBER, (x0 + sw + 300, 640), alpha=a * k2)
    return cv


def shrink(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    c0, c1, c2 = cue(cues, 0, 1.0), cue(cues, 1, 3.5), cue(cues, 2, 6.0)
    x0, full, y0, y1 = 260, 1400, 470, 590
    put(cv, 'PUNITIVE DAMAGES', 'monob', 26, GREY, (x0, 290), alpha=a, track=4)
    k = ramp(t, c0 - 0.2, 1.4); wv = full * (1 - k) + full * 480 / 2700 * k
    val = 2_700_000 * (1 - k) + 480_000 * k
    ov = Image.new('RGBA', (W, H)); ImageDraw.Draw(ov).rectangle((x0, y0, x0 + full, y1), outline=(*DIM, int(255 * a * k)), width=3)
    cv.alpha_composite(ov)
    rect(cv, (x0, y0, x0 + wv, y1), AMBER, a)
    lab = ('THE JURY: ' if k < 0.5 else 'THE JUDGE: ') + (f'${val / 1e6:.1f} MILLION' if val >= 1e6 else money(round(val, -4)))
    put(cv, lab, 'bebas', 96, WHITE, (x0, 352), alpha=a)
    put(cv, 'JURY AWARD $2.7M', 'mono', 24, DIM, (x0 + full, 604), 'r', a * k)
    put(cv, 'CUT BY 82%', 'monob', 30, AMBER, (x0 + wv + 30, 512), alpha=a * ramp(t, c0 + 1.2, 0.5), track=3)
    put(cv, '= 3 × THE $160,000 COMPENSATORY AWARD', 'monob', 30, GREY, (x0, 650), alpha=a * ramp(t, c1 - 0.2, 0.5), track=2)
    k3 = ramp(t, c2 - 0.2, 0.5)
    put(cv, '$160,000 + $480,000 =', 'mono', 50, WHITE, (x0, 802), alpha=a * k3)
    put(cv, '$640,000', 'bebas', 150, AMBER, (x0 + text_w('$160,000 + $480,000 =', 'mono', 50) + 40, 750), alpha=a * k3)
    put(cv, 'TOTAL JUDGMENT', 'monob', 26, GREY, (x0, 890), alpha=a * k3, track=4)
    return cv


def settled(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    put(cv, 'AFTER THE VERDICT', 'monob', 26, GREY, (220, 340), alpha=a, track=4)
    typed(cv, 'Settled before appeal.', t, 0.4, 'mono', 76, WHITE, (220, 410), cps=20, cursor=False, alpha=a)
    typed(cv, 'Amount confidential.', t, 0.4 + 22 / 20 + 0.5, 'mono', 76, AMBER, (220, 510), cps=18, alpha=a)
    return cv


def died(t, dur, cues):
    cv = card(); a = fade(t, 0.2, dur, 1.0, 0.8)
    put(cv, 'STELLA LIEBECK', 'bebas', 150, WHITE, (W / 2, 400), 'c', a, track=10)
    put(cv, 'DIED AUGUST 5, 2004  ·  AGE 91', 'mono', 36, GREY, (W / 2, 590), 'c', a * ramp(t, 0.9, 1.0), track=2)
    return cv


def holding_title(t, dur, cues):
    cv = card(); a = fade(t, 0.1, dur, 0.5, 0.4)
    put(cv, 'WHAT THE CASE STANDS FOR', 'monob', 28, AMBER, (W / 2, 350), 'c', a * ramp(t, 0.5, 0.6), track=8)
    put(cv, 'THE HOLDING', 'bebas', 250, WHITE, (W / 2, 400), 'c', a, track=6 + 24 * (1 - ramp(t, 0.1, 1.6)))
    w = 640 * ramp(t, 0.6, 1.0); rect(cv, (W / 2 - w / 2, 680, W / 2 + w / 2, 684), AMBER, a)
    return cv


def holding(t, dur, cues):
    cv = card(); bug(cv); a = fade(t, 0, dur, 0.3, 0.4)
    rows = [('COMPARATIVE FAULT', '20% of the fault was hers, and her award shrank to match.'),
            ('PUNITIVE DAMAGES TRACK CONDUCT', 'What the company knew: 700 prior burn reports.'),
            ('THE SYSTEM HAS BRAKES', 'The judge cut the punitive award by 82%.')]
    for i, (h, sub) in enumerate(rows):
        c = cue(cues, i, 0.4 + 3 * i); k = ramp(t, c - 0.1, 0.5); y = 210 + i * 245
        cur = 1.0 if (i == len(rows) - 1 or t < cue(cues, i + 1, 99)) else 0.55
        put(cv, str(i + 1), 'bebas', 170, AMBER, (220, y - 10), alpha=a * k * cur)
        put(cv, h, 'bebas', 92, WHITE, (360 + 30 * (1 - k), y + 10), alpha=a * k * cur, track=2)
        put(cv, sub, 'inter', 40, GREY, (364 + 30 * (1 - k), y + 112), alpha=a * k * cur)
    return cv


def endcard(t, dur, cues):
    cv = card(); a = fade(t, 0.1, dur, 0.6, 0.8)
    put(cv, 'THE HOFFMAN FILES', 'bebas', 170, WHITE, (W / 2, 250), 'c', a, track=6)
    put(cv, 'LAW BY LAWYERS', 'monob', 30, AMBER, (W / 2, 450), 'c', a, track=10)
    put(cv, 'NEXT:  MIRANDA', 'monob', 40, WHITE, (W / 2, 560), 'c', a * ramp(t, 0.8, 0.6), track=6)
    put(cv, "Sources: Liebeck v. McDonald's Restaurants, No. D-202 CV-93-02419 (N.M. Dist. Ct., Bernalillo Cnty., 1994);",
        'mono', 21, GREY, (W / 2, 760), 'c', a)
    put(cv, 'trial evidence as reported in 1994 and later accounts. Full source list in the description.',
        'mono', 21, GREY, (W / 2, 792), 'c', a)
    put(cv, '3D sequences are reconstructions and diagrams built from the record, not footage. No AI-generated imagery.',
        'mono', 21, DIM, (W / 2, 850), 'c', a)
    put(cv, 'Theme: "Measured in Sunlight." Score: public domain recordings from the Musopen project.',
        'mono', 21, DIM, (W / 2, 882), 'c', a)
    return cv


# ---------------------------------------------------------------- overlays on 3D plates
def track_xy(tr, frame, key):
    row = tr.get(str(max(1, min(frame, len(tr))))) if tr else None
    if not row or key not in row: return None
    x, y, z = row[key]
    return None if z <= 0 else (x * W, y * H)


def ov_car(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4); scrim(cv, 'left', 0.7, 1000)
    tag(cv, 'ILLUSTRATION', 'GENERIC CAR, NOT A MODEL OF THE ACTUAL VEHICLE', a)
    k = ramp(t, 0.4, 0.6)
    put(cv, 'FEBRUARY 27, 1992', 'bebas', 130, WHITE, (110 - 30 * (1 - k), 620), alpha=a * k, track=2)
    put(cv, 'ALBUQUERQUE, NEW MEXICO', 'monob', 34, AMBER, (116, 772), alpha=a * ramp(t, 1.4, 0.6), track=4)
    put(cv, 'PASSENGER SEAT  ·  1989 FORD PROBE  ·  NO CUP HOLDERS', 'mono', 26, WHITE, (116, 836),
        alpha=a * ramp(t, cue(cues, 0, 6.0), 0.6), track=1)


def ov_recon(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.01)
    tag(cv, 'RECONSTRUCTION', 'BASED ON ACCOUNTS OF THE TRIAL RECORD', a)


def ov_recon_soak(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.01, 0.4)
    tag(cv, 'RECONSTRUCTION', 'BASED ON ACCOUNTS OF THE TRIAL RECORD', a)
    bottom_scrim(cv, 0.7, 300)
    put(cv, 'COTTON SWEATPANTS HELD THE COFFEE AGAINST HER SKIN', 'monob', 30, WHITE, (W / 2, 960), 'c',
        a * ramp(t, 1.0, 0.6), track=3)


def ov_skin(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4); scrim(cv, 'left', 0.6, 900)
    tag(cv, 'DIAGRAM', 'ILLUSTRATION, NOT TO SCALE', a)
    for key, lab in (('epidermis', 'EPIDERMIS'), ('dermis', 'DERMIS'), ('fat', 'FAT'), ('muscle', 'MUSCLE')):
        p = track_xy(tr, frame, key)
        if not p: continue
        x, y = p; k = a * ramp(t, 0.6, 0.6)
        line(cv, [(x + 14, y), (x + 120, y)], GREY, 2, k)
        put(cv, lab, 'monob', 26, WHITE, (x + 134, y - 20), alpha=k, track=3)
    c6 = cue(cues, 2, 2.5); c16 = cue(cues, 3, 4.0)
    put(cv, '6%', 'bebas', 170, AMBER, (110, 250), alpha=a * ramp(t, c6, 0.5))
    put(cv, 'OF HER SKIN: THIRD-DEGREE', 'monob', 26, WHITE, (118, 420), alpha=a * ramp(t, c6, 0.5), track=2)
    put(cv, '16%', 'bebas', 170, WHITE, (110, 500), alpha=a * ramp(t, c16, 0.5))
    put(cv, 'WITH LESSER BURNS', 'monob', 26, WHITE, (118, 670), alpha=a * ramp(t, c16, 0.5), track=2)
    kf = ramp(t, cue(cues, 0, 6.0), 0.6)
    bottom_scrim(cv, 0.85 * kf, 330)
    put(cv, 'THIRD DEGREE = FULL THICKNESS', 'bebas', 88, AMBER, (W / 2, 880), 'c', a * kf, track=2)
    put(cv, 'THE BURN GOES THROUGH EVERY LAYER OF SKIN', 'monob', 24, WHITE, (W / 2, 986), 'c', a * kf, track=2)


E7_FIRST, E7_RATE, E7_N = 12, 3, 70


def ov_folders(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4); scrim(cv, 'left', 0.6, 900)
    n = int(max(0, min(E7_N, (frame - E7_FIRST) // E7_RATE + 1))) if frame >= E7_FIRST else 0
    reports = n * 10; year = 1982 + int(round(10 * n / E7_N))
    put(cv, 'BURN REPORTS', 'monob', 28, GREY, (110, 230), alpha=a, track=4)
    put(cv, f'{reports:,}' + ('+' if n == E7_N else ''), 'bebas', 230, AMBER if n == E7_N else WHITE, (104, 260), alpha=a)
    put(cv, f'1982 – {year}', 'mono', 40, WHITE, (114, 510), alpha=a * ramp(t, 0.5, 0.5))
    put(cv, '1 FOLDER = 10 REPORTS', 'monob', 26, AMBER, (114, 580), alpha=a * ramp(t, 1.0, 0.5), track=3)
    put(cv, 'AUGUST 1994  ·  THE TRIAL', 'monob', 24, GREY, (W - 64, 52 + 40), 'r', a * ramp(t, 0.3, 0.5), track=3)
    source(cv, 'Evidence at trial', a)


E9_A, E9_MID, E9_B = 12, 96, 180


def ov_sales(cv, t, dur, frame, tr, cues):
    a = fade(t, 0, dur, 0.4, 0.4)
    h = np.interp(frame, [1, E9_A, E9_MID, E9_B], [0, 0, 0.8, 1.6])
    val = h / 0.8 * 1.35e6
    p = track_xy(tr, frame, 'bar_top')
    if p and frame > E9_A:
        d1y = track_xy(tr, frame, 'day1')[1]                   # tracks mark heights 1.6 (top) and 0.8 (day 1)
        y_cur = p[1] + (d1y - p[1]) * (1.6 - h) / 0.8
        put(cv, f'${val / 1e6:.2f}M', 'bebas', 100, WHITE, (p[0], y_cur - 128), 'c', a)
        if frame >= E9_B:
            put(cv, 'DAY 2', 'monob', 24, GREY, (p[0] - 160, p[1] - 16), 'r', a * ramp(frame / FPS, E9_B / FPS, 0.4), track=3)
    d1 = track_xy(tr, frame, 'day1')
    if d1:
        put(cv, 'DAY 1', 'monob', 24, GREY, (d1[0] - 160, d1[1] - 16), 'r', a * ramp(frame / FPS, E9_MID / FPS, 0.4), track=3)
    put(cv, 'TWO DAYS OF COFFEE SALES', 'monob', 28, AMBER, (W / 2, 70), 'c', a, track=4)
    put(cv, 'ABOUT $1.35 MILLION A DAY', 'mono', 30, WHITE, (W / 2, 116), 'c', a * ramp(t, 0.8, 0.5))
    kf = ramp(t, cue(cues, 2, 7.0), 0.6)
    bottom_scrim(cv, 0.8 * kf, 320)
    put(cv, 'PUNITIVE DAMAGES AWARDED: $2.7 MILLION', 'bebas', 92, AMBER, (W / 2, 930), 'c', a * kf, track=2)


OVERLAYS = dict(car=ov_car, recon=ov_recon, recon_soak=ov_recon_soak, skin=ov_skin, folders=ov_folders, sales=ov_sales)
# extra spoken cue phrases the overlays listen for (beyond each segment's `at` anchors)
OVERLAY_CUES = dict(car=['a 1989 Ford Probe'], skin=['Third degree means', 'every layer', 'six percent', 'sixteen percent'],
                    sales=['two days', '1.35 million', '2.7 million'])
CARDS = dict(title=title, headline=headline, injuries=injuries, temperature=temperature, ledger=ledger, offer=offer,
             claims=claims, qa=qa, fault=fault, shrink=shrink, settled=settled, died=died, holding_title=holding_title,
             holding=holding, endcard=endcard)


# ---------------------------------------------------------------- slates for the story reel
def wrap(text, fname, size, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        nxt = (cur + ' ' + w_).strip()
        if text_w(nxt, fname, size) > maxw and cur: lines.append(cur); cur = w_
        else: cur = nxt
    return lines + ([cur] if cur else [])


def slate_aroll(seg):
    cv = Image.new('RGBA', (W, H), (16, 16, 19, 255)); bug(cv)
    ov = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(ov)
    d.rectangle((160, 90, W - 160, H - 90), outline=(*DIM, 140), width=2)       # framing guide
    cv.alpha_composite(ov)
    tag(cv, 'A-ROLL  ·  ERIC ON CAMERA', seg['act'].upper(), xy=(200, 130))
    lines = wrap(seg['vo'], 'inter', 50, 1380)
    y0 = H / 2 - len(lines) * 74 / 2
    for i, ln in enumerate(lines):
        put(cv, ln, 'inter', 50, WHITE, (W / 2, y0 + i * 74), 'c')
    put(cv, "TEMP VOICE  ·  REPLACE WITH ERIC'S TAKE", 'monob', 22, DIM, (W / 2, H - 150), 'c', track=3)
    return cv


def slate_interview(seg, guests, plan):
    cv = Image.new('RGBA', (W, H), (16, 16, 19, 255)); bug(cv)
    name, title_ = guests[seg['guest']]
    tag(cv, f'INTERVIEW  ·  BEAT {seg["beat"]}  ·  ABOUT {plan} SECONDS', seg['act'].upper(), xy=(200, 130))
    put(cv, 'TOPICS', 'monob', 24, GREY, (200, 300), track=4)
    for i, tp in enumerate(seg['topics']):
        put(cv, '—  ' + tp, 'inter', 48, WHITE, (200, 350 + i * 80))
    lower_third(cv, name, title_)
    return cv
