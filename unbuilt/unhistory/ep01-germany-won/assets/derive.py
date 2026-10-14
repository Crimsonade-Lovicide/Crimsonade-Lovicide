"""Draw UNHISTORY 01's graphics (no AI): maps, charts, cards and the on-screen claim tags, as PNGs in derived/.

Every figure is from RESEARCH.md. Maps use Natural Earth (public domain), with today's borders, which the
maps say. Usage: python3 assets/derive.py
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "toolkit"))
from unbuilt_kit.core import ACCENT, INK, MUTED, PAPER, font, paper  # noqa: E402

OUT = os.path.join(HERE, "derived")
GEO = os.path.join(HERE, "geo")
W, H = 1920, 1080


def rgb(c):
    return tuple(int(round(v * 255)) for v in c[:3])


INK8, ACC8, MUT8, PAP8 = rgb(INK), rgb(ACCENT), rgb(MUTED), rgb(PAPER)
LAND8 = tuple(int(v * 0.93) for v in PAP8)
SEA8 = tuple(int(v * 0.985) for v in PAP8)
TINT8 = (226, 196, 190)          # accent tint for shaded regions
DARK8 = (120, 116, 110)          # Germany on the maps


def canvas(bg=None):
    if bg is not None:
        return Image.new("RGB", (W, H), bg)
    a = paper((W, H))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def centred(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))
    print("wrote", name)


def foot(d, text):
    centred(d, H - 70, text, font("sans", 26), MUT8)


# ---------------------------------------------------------------- maps

def rings(geom):
    c, t = geom["coordinates"], geom["type"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


COUNTRIES = None


def countries():
    global COUNTRIES
    if COUNTRIES is None:
        COUNTRIES = [f for f in json.load(open(os.path.join(GEO, "ne_50m_admin_0_countries.geojson")))["features"]
                     if f["geometry"]]
    return COUNTRIES


def projector(bbox, top=110, bottom=90):
    lon0, lat0, lon1, lat1 = bbox
    k = math.cos(math.radians((lat0 + lat1) / 2))
    s = min((W * 0.94) / ((lon1 - lon0) * k), (H - top - bottom) / (lat1 - lat0))
    ox = (W - (lon1 - lon0) * k * s) / 2
    oy = top + ((H - top - bottom) - (lat1 - lat0) * s) / 2

    def xy(lon, lat):
        return ox + (lon - lon0) * k * s, oy + (lat1 - lat) * s
    return xy


def draw_map(bbox, fills, title, labels=(), credit="Map: Natural Earth (public domain). Borders as today.",
             outline_only=()):
    """fills: {country name: rgb}. labels: [(text, lon, lat, size, colour)]."""
    img = canvas()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=SEA8)
    xy = projector(bbox)
    for f in countries():
        name = f["properties"]["name"]
        fill = fills.get(name, LAND8)
        for ring in rings(f["geometry"]):
            pts = [xy(*p[:2]) for p in ring]
            if len(pts) > 2:
                d.polygon(pts, fill=fill, outline=MUT8)
    for f in countries():                     # hatched outline for partial regions
        if f["properties"]["name"] in outline_only:
            for ring in rings(f["geometry"]):
                pts = [xy(*p[:2]) for p in ring]
                if len(pts) > 2:
                    d.line(pts + [pts[0]], fill=ACC8, width=5)
    for text, lon, lat, size, colour in labels:
        x, y = xy(lon, lat)
        lf = font("sans", size, "bold")
        w = d.textlength(text, font=lf)
        d.text((x - w / 2, y - size / 2), text, font=lf, fill=colour)
    d.rectangle([0, 0, W, 100], fill=PAP8)
    centred(d, 24, title, font("serif", 54, "bold"), INK8)
    d.text((W - 760, H - 46), credit, font=font("sans", 24), fill=MUT8)
    return img, d, xy


def arrow(d, a, b, colour=INK8, width=10, dashed=False):
    (x0, y0), (x1, y1) = a, b
    ang = math.atan2(y1 - y0, x1 - x0)
    end = (x1 - 40 * math.cos(ang), y1 - 40 * math.sin(ang))
    if dashed:
        n = max(1, int(math.hypot(end[0] - x0, end[1] - y0) // 40))
        for i in range(n):
            if i % 2 == 0:
                t0, t1 = i / n, (i + 1) / n
                d.line([(x0 + (end[0] - x0) * t0, y0 + (end[1] - y0) * t0),
                        (x0 + (end[0] - x0) * t1, y0 + (end[1] - y0) * t1)], fill=colour, width=width)
    else:
        d.line([a, end], fill=colour, width=width)
    left = (x1 - 50 * math.cos(ang - 0.45), y1 - 50 * math.sin(ang - 0.45))
    right = (x1 - 50 * math.cos(ang + 0.45), y1 - 50 * math.sin(ang + 0.45))
    d.polygon([(x1, y1), left, right], fill=colour)


def map_east():
    img, d, xy = draw_map((-6, 40, 62, 66), {"Germany": DARK8, "Russia": TINT8, "Belarus": TINT8,
                                              "Ukraine": TINT8, "Lithuania": TINT8, "Latvia": TINT8,
                                              "Estonia": TINT8, "Moldova": TINT8},
                          "The one close front: Germany against the Soviet Union",
                          [("GERMANY", 10.4, 51.0, 34, (250, 248, 244)), ("SOVIET UNION", 42, 56, 52, INK8)])
    arrow(d, xy(15, 51.5), xy(33, 53.5), ACC8, 12)
    d.rectangle([60, H - 190, 980, H - 90], fill=PAP8, outline=INK8, width=3)
    d.text((90, H - 175), "\"finely balanced\" until 1945", font=font("serif", 42, "bold"), fill=INK8)
    d.text((90, H - 125), "Mark Harrison, The Economics of World War II (1998)", font=font("sans", 26), fill=MUT8)
    save(img, "U04_east")


def map_west():
    img, d, xy = draw_map((-11, 41.5, 22, 60), {"United Kingdom": TINT8, "Germany": DARK8, "France": LAND8},
                          "Our timeline, summer 1940: Britain makes peace",
                          [("BRITAIN", -2.2, 52.8, 40, INK8), ("FRANCE", 2.4, 46.8, 40, MUT8),
                           ("GERMANY", 10.4, 51.0, 36, (250, 248, 244))])
    d.rectangle([W - 760, 150, W - 60, 310], fill=PAP8, outline=ACC8, width=4)
    for i, line in enumerate(["No western front", "No bombing of Germany"]):
        d.text((W - 730, 170 + i * 66), line, font=font("sans", 44, "bold"), fill=INK8)
    save(img, "U08_west")


def map_atlantic():
    img, d, xy = draw_map((-128, 16, 34, 66), {"United States of America": TINT8, "United Kingdom": TINT8,
                                                "Germany": DARK8},
                          "America: the hardest part to call",
                          [("UNITED STATES", -99, 39.5, 44, INK8), ("BRITAIN", -2.5, 56.5, 34, INK8)])
    arrow(d, xy(-72, 42), xy(-8, 52.5), INK8, 9, dashed=True)
    x, y = xy(-48, 50)
    lab = "Lend-Lease, March 1941: built around Britain"
    lf = font("sans", 34, "bold")
    tw = d.textlength(lab, font=lf)
    d.rectangle([x - tw / 2 - 20, y - 90, x + tw / 2 + 20, y - 34], fill=PAP8)
    d.text((x - tw / 2, y - 86), lab, font=lf, fill=INK8)
    save(img, "U09_atlantic")


def map_gpo():
    shade = {n: TINT8 for n in ("Poland", "Lithuania", "Latvia", "Estonia", "Belarus")}
    shade["Germany"] = DARK8
    img, d, xy = draw_map((4, 43.5, 44, 61.5), shade, "The General Plan for the East (one version, late 1941)",
                          [("POLAND", 19.3, 52.1, 36, INK8), ("BELARUS", 28.0, 53.6, 34, INK8),
                           ("BALTIC STATES", 24.6, 57.6, 30, INK8), ("+ part of north-west Ukraine", 29.0, 50.6, 30, ACC8),
                           ("GERMANY", 10.4, 51.0, 30, (250, 248, 244))],
                          credit="Natural Earth (PD). Borders as today; the plan's area is approximate.")
    bx, by = 1180, 130
    d.rectangle([bx, by, W - 50, by + 330], fill=PAP8, outline=INK8, width=4)
    rows = [("about 45 million", "people living in the plan's area"),
            ("about 31 million", "to be removed east, to Siberia"),
            ("30 years", "for German settlers to replace them")]
    for i, (big, small) in enumerate(rows):
        d.text((bx + 30, by + 20 + i * 102), big, font=font("serif", 48, "bold"), fill=ACC8 if i == 1 else INK8)
        d.text((bx + 30, by + 74 + i * 102), small, font=font("sans", 26), fill=MUT8)
    d.text((60, H - 46), "Source: the RSHA version, as summarised in the Wetzel memo of 27 April 1942",
           font=font("sans", 24), fill=MUT8)
    save(img, "U11_gpo")


# ---------------------------------------------------------------- charts and cards

def card(name, title, lines_=(), footer=None, title_size=72, accent_line=None, bg=None, fg=INK8):
    img = canvas(bg)
    d = ImageDraw.Draw(img)
    y = 380 if not lines_ else 300 if len(lines_) < 3 else 230
    centred(d, y, title, font("serif", title_size, "bold"), fg)
    y += title_size + 40
    if lines_:
        d.rectangle([W / 2 - 70, y, W / 2 + 70, y + 7], fill=ACC8)
        y += 60
    for i, line in enumerate(lines_):
        centred(d, y, line, font("sans", 46), ACC8 if accent_line == i else fg)
        y += 70
    if footer:
        foot(d, footer)
    save(img, name)


def odds():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 90, "The size of each side's economy, before the war", font("serif", 56, "bold"), INK8)
    base, unit_w = 760, 260
    for i, (label, v, colour) in enumerate([("The Allies", 2.4, INK8), ("Germany and its partners", 1.0, ACC8)]):
        y = 320 + i * 230
        d.rectangle([200, y, 200 + v * unit_w * 2.4, y + 140], fill=colour)
        d.text((200, y - 56), label, font=font("sans", 40, "bold"), fill=INK8)
        d.text((220 + v * unit_w * 2.4, y + 40), f"{v:g}".replace(".", "."), font=font("serif", 60, "bold"),
               fill=colour)
    centred(d, base + 70, "more than two to one", font("serif", 64, "bold"), INK8)
    foot(d, "Prewar (1938) GDP of the great powers on each side in 1942. Mark Harrison, The Economics of "
            "World War II (1998)")
    save(img, "U02_odds")


def ratio():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 90, "Allied economies against the Axis, by year", font("serif", 56, "bold"), INK8)
    pts = [("1938", 2.4), ("1941", 2.0), ("1944", 3.3)]
    x0, colw, gap, ybase, scale = 430, 260, 140, 860, 170
    for i, (yr, v) in enumerate(pts):
        x = x0 + i * (colw + gap)
        top = ybase - v * scale
        d.rectangle([x, top, x + colw, ybase], fill=ACC8 if yr == "1944" else INK8)
        lab = f"{v:g} to 1"
        lf = font("serif", 52, "bold")
        d.text((x + (colw - d.textlength(lab, font=lf)) / 2, top - 70), lab, font=lf, fill=INK8)
        yf = font("sans", 40, "bold")
        d.text((x + (colw - d.textlength(yr, font=yf)) / 2, ybase + 18), yr, font=yf, fill=INK8)
    d.text((x0 + 3 * (colw + gap) - 70, 420), "US output by 1944:", font=font("sans", 34), fill=MUT8)
    d.text((x0 + 3 * (colw + gap) - 70, 465), "nearly double", font=font("serif", 46, "bold"), fill=ACC8)
    d.text((x0 + 3 * (colw + gap) - 70, 520), "its 1938 level", font=font("serif", 46, "bold"), fill=ACC8)
    foot(d, "1941 was the Allied low point. Mark Harrison, The Economics of World War II (1998), ch. 1")
    save(img, "U03_ratio")


def three():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 170, "A long war against all three", font("serif", 64, "bold"), INK8)
    for i, name in enumerate(["Britain", "United States", "Soviet Union"]):
        x = 200 + i * 540
        d.rounded_rectangle([x, 380, x + 440, 640], 26, outline=INK8, width=6)
        nf = font("serif", 50, "bold")
        d.text((x + (440 - d.textlength(name, font=nf)) / 2, 480), name, font=nf, fill=INK8)
    centred(d, 760, "close to unwinnable", font("serif", 70, "bold"), ACC8)
    foot(d, "The mainstream view among economic historians (Harrison 1998; Tooze, The Wages of Destruction, 2006)")
    save(img, "U05_three")


def split(name, extend):
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 90, "One change", font("serif", 60, "bold"), INK8)
    x0, x1, y = 160, W - 160, 640
    years = list(range(1939, 1951))
    xs = {yr: x0 + (x1 - x0) * i / (len(years) - 1) for i, yr in enumerate(years)}
    d.line([x0, y, x1, y], fill=INK8, width=10)
    for yr in (1939, 1940, 1945, 1950):
        d.line([xs[yr], y - 16, xs[yr], y + 16], fill=INK8, width=4)
        yf = font("sans", 32, "bold")
        d.text((xs[yr] - d.textlength(str(yr), font=yf) / 2, y + 30), str(yr), font=yf, fill=INK8)
    d.text((x1 - 330, y + 90), "What happened", font=font("sans", 38, "bold"), fill=INK8)
    bx = xs[1940] + (xs[1941] - xs[1940]) * 0.36          # 9 May 1940
    end_x = bx + (x1 - bx) * extend
    n = int((end_x - bx) // 36)
    for i in range(n):
        if i % 2 == 0:
            t0, t1 = i / max(n, 1), (i + 1) / max(n, 1)
            ya = y - 260 * min(1, t0 * 3) if t0 < 1 / 3 else y - 260
            yb = y - 260 * min(1, t1 * 3) if t1 < 1 / 3 else y - 260
            d.line([bx + (end_x - bx) * t0, ya, bx + (end_x - bx) * t1, yb], fill=ACC8, width=10)
    d.ellipse([bx - 16, y - 16, bx + 16, y + 16], fill=ACC8)
    d.text((bx - 120, y + 90), "9 May 1940", font=font("sans", 32, "bold"), fill=ACC8)
    d.text((bx + 120, y - 340), "Halifax says yes", font=font("serif", 48, "bold"), fill=ACC8)
    if extend > 0.5:
        d.text((end_x - 380, y - 330), "Our timeline", font=font("sans", 38, "bold"), fill=ACC8)
    save(img, name)


def gauge():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 90, "How far the test block sank", font("serif", 58, "bold"), INK8)
    top, px_cm = 260, 34
    for x, cm, label, colour in [(560, 6, "allowed", INK8), (1160, 18, "actual", ACC8)]:
        d.rectangle([x, top, x + 200, top + 20 * px_cm], outline=MUT8, width=4)
        d.rectangle([x, top, x + 200, top + cm * px_cm], fill=colour)
        d.text((x + 230, top + cm * px_cm - 40), f"{cm} cm", font=font("serif", 60, "bold"), fill=colour)
        lf = font("sans", 40, "bold")
        d.text((x + (200 - d.textlength(label, font=lf)) / 2, top - 60), label, font=lf, fill=INK8)
    foot(d, "About 18 cm in the testing years, against a 6 cm limit (Structurae; berlin.de)")
    save(img, "U14_gauge")


def minutes():
    """H1/H2: the key line of the 2 May 1941 minutes, German original and translation (typed, not a scan)."""
    img = canvas()
    d = ImageDraw.Draw(img)
    d.text((160, 120), "Minutes of the state secretaries' meeting, 2 May 1941", font=font("sans", 34, "bold"),
           fill=MUT8)
    de = ["\u201eHierbei werden zweifellos zig Millionen Menschen verhungern,",
          "wenn von uns das f\u00fcr uns Notwendige aus dem Lande herausgeholt wird.\u201c"]
    for i, line in enumerate(de):
        d.text((160, 230 + i * 70), line, font=font("serif", 50, "regular"), fill=INK8)
    d.rectangle([160, 420, 300, 427], fill=ACC8)
    en = ["\u201cThere is no doubt that tens of millions of people will starve",
          "if we take from the country what we need.\u201d"]
    for i, line in enumerate(en):
        d.text((160, 480 + i * 74), line, font=font("serif", 56, "bold"), fill=INK8)
    hl = font("serif", 56, "bold")
    x = 160 + d.textlength("\u201cThere is no doubt that ", font=hl)
    w = d.textlength("tens of millions", font=hl)
    d.rectangle([x, 480 + 64, x + w, 480 + 70], fill=ACC8)
    foot(d, "Nuremberg document 2718-PS. German text as quoted by Alex J. Kay; translation ours.")
    save(img, "U15_minutes")


def prep_photos():
    """Edit-only copies of three photos (the originals in raw/ stay untouched)."""
    from PIL import ImageOps
    raw = os.path.join(HERE, "raw")
    im = ImageOps.exif_transpose(Image.open(os.path.join(raw, "R03_test_block_close_2022.jpg")))
    im.save(os.path.join(OUT, "R03_upright.jpg"), quality=92)
    im = Image.open(os.path.join(raw, "H04_dunkirk_bray_dunes_1940.jpg"))
    w, h = im.size
    im.crop((0, 0, int(w * 0.92), int(h * 0.92))).save(os.path.join(OUT, "H04_no_watermark.jpg"), quality=92)
    im = Image.open(os.path.join(raw, "H01_halifax_sikorski_1941.jpg"))
    w, h = im.size
    im.crop((int(w * 0.40), 0, int(w * 0.95), int(h * 0.80))).save(os.path.join(OUT, "H01_halifax.jpg"), quality=92)
    print("wrote photo prep")


def tags():
    """The on-screen claim tags, as RGBA overlays for the lower-left corner."""
    for word, colour in [("HAPPENED", INK8), ("LIKELY", MUT8), ("GUESS", ACC8)]:
        f = font("sans", 34, "bold")
        tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        tw = tmp.textlength(word, font=f)
        im = Image.new("RGBA", (int(tw) + 64, 66), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle([0, 0, im.width - 1, 65], 33, fill=colour + (235,))
        dd.text((32, 12), word, font=f, fill=(250, 248, 244, 255))
        im.save(os.path.join(OUT, f"tag_{word}.png"))
        print("wrote tag", word)


def main():
    os.makedirs(OUT, exist_ok=True)
    tags()
    prep_photos()
    card("U01_question", "Could they have won at all?", title_size=84)
    odds()
    ratio()
    map_east()
    three()
    split("U06_split", 0.34)
    split("U07_split_on", 1.0)
    map_west()
    map_atlantic()
    card("U10_east_unknown", "Does Germany win in the east?", ["Historians disagree.",
                                                                "It was close even in the real war."],
         accent_line=0)
    map_gpo()
    card("U12_six_million", "About six million Jews were murdered.", ["The list shows who was meant to be next."],
         bg=INK8, fg=(242, 237, 228), title_size=66)
    card("U13_1950", "1950", ["Their own deadline.", "After this, nobody knows."], title_size=200)
    gauge()
    minutes()


if __name__ == "__main__":
    main()
