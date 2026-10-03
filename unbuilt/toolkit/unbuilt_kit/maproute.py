"""Route map: land drawn from public-domain Natural Earth GeoJSON, with a red route that draws on city by city."""
import json
import math

import numpy as np
from PIL import Image, ImageDraw

from .core import ACCENT, FPS, HD, INK, MUTED, PAPER, Writer, even, font, frame_times, ramp


def _rings(geojson):
    for f in json.load(open(geojson))["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else []
        for poly in polys:
            yield poly[0]
        if g["type"] in ("LineString", "MultiLineString"):
            for line in ([g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]):
                yield line


def maproute(geojson, out, duration, bbox, stops, size=HD, dashed=(), title=None, fps=FPS):
    """bbox: (lon0, lat0, lon1, lat1). stops: [(label, lon, lat), ...] in route order.
    dashed: indexes of legs (0 = first->second stop) drawn dashed, e.g. a tunnel that was never finished.
    Land is filled a shade darker than the paper and outlined in muted ink; the route draws on over the
    middle 70% of the clip, each stop's dot and label appearing as the line reaches it."""
    size = even(size)
    w, h = size
    ss = 2
    W, H = w * ss, h * ss
    lon0, lat0, lon1, lat1 = bbox
    kx = math.cos(math.radians((lat0 + lat1) / 2))
    s = min(W / ((lon1 - lon0) * kx), H / (lat1 - lat0))
    ox = (W - (lon1 - lon0) * kx * s) / 2
    oy = (H - (lat1 - lat0) * s) / 2

    def xy(lon, lat):
        return (ox + (lon - lon0) * kx * s, oy + (lat1 - lat) * s)

    land = tuple(int(c * 255 * 0.93) for c in PAPER)
    base = Image.new("RGB", (W, H), tuple(int(c * 255) for c in PAPER))
    d = ImageDraw.Draw(base)
    for ring in _rings(geojson):
        pts = [xy(lon, lat) for lon, lat in ring[:]]
        if len(pts) > 2:
            d.polygon(pts, fill=land, outline=tuple(int(c * 255) for c in MUTED))
    if title:
        f = font("serif", int(H * 0.045), "bold")
        tw = d.textlength(title, font=f)
        d.text(((W - tw) / 2, H * 0.05), title, font=f, fill=tuple(int(c * 255) for c in INK))

    pts = [xy(lon, lat) for _, lon, lat in stops]
    legs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(legs) or 1
    red = tuple(int(c * 255) for c in ACCENT)
    ink = tuple(int(c * 255) for c in INK)
    lab = font("sans", int(H * 0.03), "bold")
    t0, t1 = duration * 0.15, duration * 0.85
    with Writer(out, size, fps) as wr:
        for t in frame_times(duration, fps):
            fr = base.copy()
            dd = ImageDraw.Draw(fr)
            done = ramp(t, t0, t1 - t0) * total
            acc = 0.0
            reached = 1
            for i, (a, b) in enumerate(zip(pts, pts[1:])):
                if done <= acc:
                    break
                p = min(1.0, (done - acc) / legs[i]) if legs[i] else 1.0
                end = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)
                if i in dashed:
                    n = max(1, int(legs[i] * p / (H * 0.02)))
                    for k in range(0, n, 2):
                        u0, u1 = k / n * p, min(p, (k + 1) / n * p)
                        dd.line([(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0),
                                 (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)], fill=red, width=int(H * 0.007))
                else:
                    dd.line([a, end], fill=red, width=int(H * 0.007))
                acc += legs[i]
                if p >= 1:
                    reached = i + 2
            r = H * 0.009
            for k, ((label, _, _), (x, y)) in enumerate(zip(stops, pts)):
                if k < reached:
                    dd.ellipse([x - r, y - r, x + r, y + r], fill=ink)
                    dd.text((x + r * 2, y - r * 2.2), label, font=lab, fill=ink)
            wr.write(np.asarray(fr.resize((w, h), Image.LANCZOS), np.float32) / 255)
    return out
