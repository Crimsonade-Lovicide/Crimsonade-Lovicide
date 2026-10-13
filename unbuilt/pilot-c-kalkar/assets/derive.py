"""Draw Pilot C's graphics (no AI): the map, the breeder diagram and the fact cards, as 1920x1080 PNGs in derived/.

Every figure on a card is from RESEARCH.md. Usage: python3 assets/derive.py
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "toolkit"))
from unbuilt_kit.core import ACCENT, INK, MUTED, PAPER, font, paper  # noqa: E402

OUT = os.path.join(HERE, "derived")
GEO = os.path.join(HERE, "geo")
W, H = 1920, 1080


def rgb(c):
    return tuple(int(round(v * 255)) for v in c[:3])


INK8, ACC8, MUT8, PAP8 = rgb(INK), rgb(ACCENT), rgb(MUTED), rgb(PAPER)
LAND8 = tuple(int(v * 0.93) for v in PAP8)


def canvas():
    a = paper((W, H))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def centred(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))
    print("wrote", name)


# ---------------------------------------------------------------- the map (B3)

def lines(path):
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        if g is None:
            continue
        c, t = g["coordinates"], g["type"]
        parts = ([c[0]] if t == "Polygon" and c else [p[0] for p in c if p] if t == "MultiPolygon" else
                 [c] if t == "LineString" else c if t == "MultiLineString" else [])
        for p in parts:
            yield f["properties"], p


def map_kalkar():
    lon0, lat0, lon1, lat1 = 2.4, 49.4, 9.6, 54.0
    k = math.cos(math.radians((lat0 + lat1) / 2))
    sx = (W * 0.9) / ((lon1 - lon0) * k)
    sy = (H * 0.86) / (lat1 - lat0)
    s = min(sx, sy)
    ox = (W - (lon1 - lon0) * k * s) / 2
    oy = (H - (lat1 - lat0) * s) / 2 + 30

    def xy(lon, lat):
        return ox + (lon - lon0) * k * s, oy + (lat1 - lat) * s

    img = canvas()
    d = ImageDraw.Draw(img)
    for _, ring in lines(os.path.join(GEO, "ne_50m_land.geojson")):
        pts = [xy(*p[:2]) for p in ring]
        if len(pts) > 2:
            d.polygon(pts, fill=LAND8, outline=MUT8)
    for props, line in lines(os.path.join(GEO, "ne_10m_rivers.geojson")):
        if props.get("name") in ("Rhine", "Rhein", "Waal", "Maas"):
            d.line([xy(*p[:2]) for p in line], fill=(150, 170, 190), width=4)
    for _, line in lines(os.path.join(GEO, "ne_10m_admin_0_boundary_lines_land.geojson")):
        pts = [xy(*p[:2]) for p in line]
        if any(lon0 - 1 < p[0] < lon1 + 1 and lat0 - 1 < p[1] < lat1 + 1 for p in line):
            for a, b in zip(pts, pts[1:]):           # dashed border
                if (hash((round(a[0]), round(a[1]))) % 2) == 0:
                    d.line([a, b], fill=MUT8, width=3)
    cf = font("sans", 34, "bold")
    for name, lon, lat in [("NETHERLANDS", 5.0, 52.65), ("BELGIUM", 4.2, 50.75), ("WEST GERMANY", 8.0, 51.0)]:
        x, y = xy(lon, lat)
        w = d.textlength(name, font=cf)
        d.text((x - w / 2, y), name, font=cf, fill=MUT8)
    x, y = xy(6.29, 51.74)                            # Kalkar
    r = 14
    d.ellipse([x - r, y - r, x + r, y + r], fill=ACC8, outline=INK8, width=3)
    lf = font("serif", 56, "bold")
    d.text((x + 26, y - 40), "Kalkar", font=lf, fill=INK8)
    tf = font("serif", 50, "bold")
    centred(d, 40, "Kalkar, on the Lower Rhine", tf, INK8)
    sf = font("sans", 26)
    d.text((W - 620, H - 50), "Map: Natural Earth (public domain). Borders as today.", font=sf, fill=MUT8)
    save(img, "G02_map")


# ---------------------------------------------------------------- the breeder (B2)

def breeder():
    img = canvas()
    d = ImageDraw.Draw(img)
    tf = font("serif", 56, "bold")
    centred(d, 110, "A fast breeder", tf, INK8)
    bf = font("sans", 40, "bold")
    sf = font("sans", 30)

    def box(x, y, w, h, title, sub, accent=False):
        d.rounded_rectangle([x, y, x + w, y + h], 24, outline=ACC8 if accent else INK8, width=6,
                            fill=(255, 250, 240) if accent else None)
        tw = d.textlength(title, font=bf)
        d.text((x + (w - tw) / 2, y + h / 2 - 50), title, font=bf, fill=INK8)
        for i, line in enumerate(sub):
            lw = d.textlength(line, font=sf)
            d.text((x + (w - lw) / 2, y + h / 2 + 6 + i * 40), line, font=sf, fill=MUT8)

    def arrow(x0, y, x1):
        d.line([x0, y, x1 - 30, y], fill=INK8, width=8)
        d.polygon([(x1, y), (x1 - 40, y - 24), (x1 - 40, y + 24)], fill=INK8)

    box(140, 420, 440, 260, "Fuel in", ["plutonium, plus", "ordinary uranium"])
    box(740, 380, 440, 340, "The reactor", ["fast neutrons turn", "uranium into", "new plutonium"], accent=True)
    box(1340, 420, 440, 260, "More fuel out", ["in theory, more", "than it burned"])
    arrow(590, 550, 730)
    arrow(1190, 550, 1330)
    centred(d, 830, "Kalkar's design: 300 megawatts, cooled by liquid sodium", sf, INK8)
    save(img, "G01_breeder")


# ---------------------------------------------------------------- cards

def card(name, title, lines_, foot=None, title_size=64, accent_line=None):
    img = canvas()
    d = ImageDraw.Draw(img)
    tf = font("serif", title_size, "bold")
    y = 300 if len(lines_) < 3 else 230
    centred(d, y, title, tf, INK8)
    y += title_size + 40
    d.rectangle([W / 2 - 70, y, W / 2 + 70, y + 7], fill=ACC8)
    y += 60
    lf = font("sans", 44)
    for i, line in enumerate(lines_):
        centred(d, y, line, lf, ACC8 if accent_line == i else INK8)
        y += 66
    if foot:
        centred(d, H - 110, foot, font("sans", 28), MUT8)
    save(img, name)


def total():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 300, "The final bill", font("serif", 60, "bold"), INK8)
    centred(d, 430, "about 7 billion marks", font("serif", 120, "bold"), ACC8)
    centred(d, H - 110, "Final total from secondary sources. The 1972 contract said 1.5 billion.", font("sans", 28), MUT8)
    save(img, "G03_total")


def counter():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 290, "Keeping the finished reactor ready: the holding phase, 1988 to 1991", font("serif", 52, "bold"), INK8)
    centred(d, 420, "105 million marks", font("serif", 130, "bold"), ACC8)
    centred(d, 600, "a year", font("serif", 70), INK8)
    centred(d, H - 110, "Split three ways: federal government, power companies, Siemens (KfK 5455, 1994)",
            font("sans", 28), MUT8)
    save(img, "G08_counter")


def fuel():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 90, "205 plutonium fuel elements", font("serif", 60, "bold"), INK8)
    cols, size, gap = 25, 44, 12
    x0 = (W - (cols * size + (cols - 1) * gap)) / 2
    y0 = 230
    for i in range(205):
        r, c = divmod(i, cols)
        x, y = x0 + c * (size + gap), y0 + r * (size + gap + 8)
        hanau = i < 123
        d.rounded_rectangle([x, y, x + size, y + size + 8], 6, fill=INK8 if hanau else None,
                            outline=INK8, width=4)
    lf = font("sans", 40, "bold")
    ly = y0 + 9 * (size + gap + 8) + 30
    d.rectangle([520, ly + 6, 556, ly + 42], fill=INK8)
    d.text((575, ly), "123 stored at Hanau", font=lf, fill=INK8)
    d.rectangle([1060, ly + 6, 1096, ly + 42], outline=INK8, width=4)
    d.text((1115, ly), "82 in Belgium", font=lf, fill=INK8)
    centred(d, ly + 90, "Loaded into the reactor: none", font("serif", 52, "bold"), ACC8)
    centred(d, H - 70, "Source: German federal government, Bundestag Drucksache 12/887 (1991)", font("sans", 28), MUT8)
    save(img, "G09_fuel")


def permits():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 120, "Licensed in stages, by the state", font("serif", 58, "bold"), INK8)
    bf = font("sans", 30, "bold")
    sf = font("sans", 22, "bold")
    w, h, gap = 210, 150, 22
    n = 12
    for i in range(n + 2):
        r, c = divmod(i, 7)
        x = (W - (7 * w + 6 * gap)) / 2 + c * (w + gap)
        y = 300 + r * (h + 60)
        last = i >= n
        d.rounded_rectangle([x, y, x + w, y + h], 14, outline=ACC8 if last else INK8, width=5,
                            fill=None if last else (232, 226, 214))
        label = ["fuel", "start-up"][i - n] if last else "permit"
        lw = d.textlength(label, font=bf)
        d.text((x + (w - lw) / 2, y + 30), label, font=bf, fill=ACC8 if last else INK8)
        stamp = "NEVER ISSUED" if last else "GRANTED"
        sw = d.textlength(stamp, font=sf)
        d.text((x + (w - sw) / 2, y + 90), stamp, font=sf, fill=ACC8 if last else MUT8)
    centred(d, H - 110, "About a dozen partial permits were granted, 1972 to 1980s. The last two never were.",
            font("sans", 28), MUT8)
    save(img, "G05_permits")


def prices():
    img = canvas()
    d = ImageDraw.Draw(img)
    centred(d, 150, "Two sales", font("serif", 62, "bold"), INK8)
    for x, title, year, price, note in [
            (260, "The Maas farm", "1985, to the reactor's builder", "4.3 million marks", "as Maas told it (taz, 1999)"),
            (1020, "The whole reactor site", "1995, to Hennie van der Most", "a few million", "as reported (Kuladig, Wikipedia)")]:
        d.rounded_rectangle([x, 300, x + 640, 820], 30, outline=INK8, width=6)
        tf = font("serif", 54, "bold")
        tw = d.textlength(title, font=tf)
        d.text((x + (640 - tw) / 2, 350), title, font=tf, fill=INK8)
        yf = font("sans", 32)
        yw = d.textlength(year, font=yf)
        d.text((x + (640 - yw) / 2, 440), year, font=yf, fill=MUT8)
        pf = font("serif", 72, "bold")
        pw = d.textlength(price, font=pf)
        d.text((x + (640 - pw) / 2, 560), price, font=pf, fill=ACC8)
        nf = font("sans", 28)
        nw = d.textlength(note, font=nf)
        d.text((x + (640 - nw) / 2, 720), note, font=nf, fill=MUT8)
    centred(d, H - 110, "Reported prices for the site range from DM 3-5 million to €2.5 million.", font("sans", 28), MUT8)
    save(img, "G10_prices")


def main():
    os.makedirs(OUT, exist_ok=True)
    breeder()
    map_kalkar()
    total()
    card("G04_court", "Federal Constitutional Court", ["8 August 1978: the \"Kalkar decision\"",
                                                       "The breeder is legal under the Atomic Energy Act.",
                                                       "But whether to use nuclear power at all",
                                                       "is a decision for Parliament."],
         foot="BVerfGE 49, 89 (Kalkar I)", accent_line=0)
    permits()
    card("G06_last_permits", "1990: the federal government wins in court", ["Still never signed by the state:",
                                                                          "the permit to bring in the fuel",
                                                                          "the permit to switch the reactor on"],
         foot="Kalkar II, BVerfGE 81, 310 (22 May 1990). Partial permits TG 7/6 and TG 7/7.", title_size=56,
         accent_line=0)
    counter()
    fuel()
    prices()


if __name__ == "__main__":
    main()
