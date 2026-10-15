"""Red-pencil annotations drawn on over a still."""
import math

import cv2
import numpy as np

from .core import (ACCENT, FPS, HD, PAPER, Writer, apply_affine, blend, camera_matrix, even, font, frame_times,
                   load_rgb, paste, partial, pencil_grain, ramp, render_view, stroke_mask, text_sprite, unit)
from .kenburns import plan_views, view_at

DEFAULT_DUR = {"arrow": 0.9, "circle": 1.1, "ellipse": 1.1, "underline": 0.6, "label": 0.7}


def _pt(rect, p):
    x, y, w, h = rect
    return np.array([x + p[0] * w, y + p[1] * h])


def _wobble(n, amp, seed):
    """Smooth, deterministic hand tremor: a few low-frequency sines."""
    rng = np.random.default_rng(seed)
    s = np.linspace(0, 1, n)
    out = np.zeros(n)
    for f in (1.3, 2.7, 5.1):
        out += np.sin(2 * np.pi * f * s + rng.uniform(0, 6.28)) / f
    return amp * out


def _line_path(a, b, bow, seed, n=60):
    """Slightly bowed, slightly wobbly stroke from a to b (plate px)."""
    d = b - a
    length = np.hypot(*d) or 1
    normal = np.array([-d[1], d[0]]) / length
    s = np.linspace(0, 1, n)[:, None]
    curve = a + d * s + normal * (bow * length * 4 * s * (1 - s))
    return curve + normal * _wobble(n, length * 0.004, seed)[:, None]


def _ellipse_path(c, rx, ry, seed, n=120):
    """Hand-drawn loop: starts upper-left, goes round once and overshoots, radius drifting a little."""
    rng = np.random.default_rng(seed)
    a0 = math.radians(-120 + rng.uniform(-10, 10))
    th = a0 + np.linspace(0, math.radians(385), n)
    grow = 1 + 0.07 * np.linspace(-0.5, 0.5, n)
    wob = 1 + 0.025 * np.sin(th * 2 + rng.uniform(0, 6.28))
    return np.stack([c[0] + rx * grow * wob * np.cos(th), c[1] + ry * grow * wob * np.sin(th)], axis=1)


def _arrow_head(path, size):
    tip = path[-1]
    back = path[max(0, len(path) - 6)]
    d = tip - back
    d = d / (np.hypot(*d) or 1)
    heads = []
    for sgn in (1, -1):
        ang = math.radians(28) * sgn
        rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        heads.append(np.array([tip, tip - rot @ d * size]))
    return heads


def _prepare(marks, rect, size, plate_h):
    """Turn mark dicts into timed strokes in plate pixels."""
    w_img, h_img = rect[2], rect[3]
    prepared = []
    for i, m in enumerate(marks):
        kind = m["type"]
        at = m.get("at", 0.5 + 1.0 * i)
        dur = m.get("dur", DEFAULT_DUR.get(kind, 0.8))
        item = {"kind": kind, "at": at, "dur": dur, "strokes": []}
        if kind == "arrow":
            a, b = _pt(rect, m["from"]), _pt(rect, m["to"])
            shaft = _line_path(a, b, m.get("bow", 0.06), seed=i)
            head = _arrow_head(shaft, min(0.035 * plate_h, 0.35 * np.hypot(*(b - a))))
            item["strokes"] = [(shaft, 0.0, 0.78), (head[0], 0.78, 0.11), (head[1], 0.89, 0.11)]
        elif kind in ("circle", "ellipse"):
            r = m.get("radii", m.get("r", 0.1))
            rx, ry = (r * w_img, r * w_img) if np.isscalar(r) else (r[0] * w_img, r[1] * h_img)
            item["strokes"] = [(_ellipse_path(_pt(rect, m["center"]), rx, ry, seed=i), 0.0, 1.0)]
        elif kind == "underline":
            a, b = _pt(rect, m["from"]), _pt(rect, m["to"])
            item["strokes"] = [(_line_path(a, b, 0.015, seed=i), 0.0, 1.0)]
        elif kind == "label":
            u = unit(size)
            f = font("sans", m.get("size", 40) * u, "bold")
            spr, asc = text_sprite(m["text"], f, ACCENT, tracking=0.02)
            halo = cv2.GaussianBlur(cv2.dilate(spr[..., 3], np.ones((5, 5), np.uint8)), (0, 0), 3 * u + 1)
            item["sprite"], item["halo"] = spr, np.clip(halo * 1.6, 0, 1)
            item["pos"] = _pt(rect, m["pos"])
            item["anchor"] = m.get("anchor", "l")
            item["asc"] = asc
        else:
            raise ValueError(f"unknown mark type {kind!r}")
        prepared.append(item)
    return prepared


def _draw_label(frame, item, xy, p):
    spr, halo = item["sprite"], item["halo"]
    h, w = spr.shape[:2]
    x = xy[0] - {"l": 0, "c": w / 2, "r": w}[item["anchor"]]
    y = xy[1] - h / 2
    # left-to-right reveal with a soft edge
    edge = p * (w + 30) - 30
    ramp_x = np.clip((edge - np.arange(w, dtype=np.float32)) / 30 + 1, 0, 1)
    halo_spr = np.zeros_like(spr)
    halo_spr[..., :3] = PAPER
    halo_spr[..., 3] = halo * ramp_x[None, :] * 0.75
    paste(frame, halo_spr, x, y)
    s = spr.copy()
    s[..., 3] *= ramp_x[None, :]
    paste(frame, s, x, y)


def draw_marks(frame, prepared, m, t, width):
    """Draw every mark's progress at time t, mapping plate points through affine m."""
    grain = pencil_grain(frame.shape)
    for item in prepared:
        p = ramp(t, item["at"], item["dur"])
        if p <= 0:
            continue
        if item["kind"] == "label":
            _draw_label(frame, item, apply_affine(m, item["pos"][None])[0], p)
            continue
        mask = np.zeros(frame.shape[:2], np.float32)
        for pts, s0, sd in item["strokes"]:
            q = min(1.0, max(0.0, (p - s0) / sd))
            if q > 0:
                mask = np.maximum(mask, stroke_mask(frame.shape, partial(apply_affine(m, pts), q), width))
        blend(frame, ACCENT, mask * grain * 0.93)
    return frame


def annotate(image, out, duration, marks, size=HD, bg="paper", start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.04),
             mode="auto", fps=FPS):
    """Draw red-pencil marks onto a still, one after another, over a very slow push-in.

    marks: list of dicts; coordinates are fractions of the image (x, y), (0,0) top-left.
      {"type": "arrow", "from": (x, y), "to": (x, y)}
      {"type": "circle", "center": (x, y), "r": 0.1}            r as a fraction of image width
      {"type": "ellipse", "center": (x, y), "radii": (rx, ry)}   rx of width, ry of height
      {"type": "underline", "from": (x, y), "to": (x, y)}
      {"type": "label", "text": "...", "pos": (x, y), "anchor": "l"|"c"|"r", "size": 40}
    Optional per mark: "at" (start second; default staggered 0.5, 1.5, 2.5 ...) and "dur" (seconds).
    """
    size = even(size)
    img = load_rgb(image)
    plate, v0, v1, rect = plan_views(img, size, start, end, bg, mode)
    prepared = _prepare(marks, rect, size, plate.shape[0])
    width = max(2, 6 * unit(size))
    times = frame_times(duration, fps)
    n = len(times)
    with Writer(out, size, fps) as w:
        for i, t in enumerate(times):
            view = view_at(v0, v1, i / (n - 1) if n > 1 else 0)
            frame = render_view(plate, view, size)
            draw_marks(frame, prepared, camera_matrix(view, size), t, width)
            w.write(frame)
    return out
