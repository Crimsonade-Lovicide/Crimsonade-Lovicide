"""Scale comparison: structures rise side by side, all drawn to one scale."""
import cv2
import numpy as np
from PIL import Image

from .core import (ACCENT, FPS, HD, INK, MUTED, Writer, background, blend, even, font, frame_times, paste, ramp,
                   rect_mask, text_sprite, text_width, wrap)
from .core import unit as layout_unit


def _shape_sprite(kind, w, h, color):
    """A simple drawn silhouette, w x h px, as an RGBA sprite. Drawn at 4x then reduced for clean edges."""
    ss = 4
    W, H = max(2, int(round(w * ss))), max(2, int(round(h * ss)))
    m = np.zeros((H, W), np.uint8)
    if kind == "taper":       # tower: tapering shaft with a short spire
        spire = int(H * 0.1)
        body = np.array([[0, H], [W, H], [W * 0.62, spire], [W * 0.38, spire]], np.int32)
        cv2.fillPoly(m, [body], 255)
        cv2.fillPoly(m, [np.array([[W * 0.44, spire], [W * 0.56, spire], [W * 0.5, 0]], np.int32)], 255)
    elif kind == "arch":      # an arch: a thick parabola
        xs = np.linspace(0, W, 200)
        top = H - H * (1 - ((xs - W / 2) / (W / 2)) ** 2)
        t = max(ss * 3, int(W * 0.04))
        pts = np.stack([xs, top], 1).astype(np.int32)
        cv2.polylines(m, [pts.reshape(-1, 1, 2)], False, 255, t, cv2.LINE_AA)
    else:                     # plain bar
        m[:] = 255
    a = cv2.resize(m, (max(1, int(round(w))), max(1, int(round(h)))), interpolation=cv2.INTER_AREA)
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = color
    spr[..., 3] = a.astype(np.float32) / 255
    return spr


def _silhouette_sprite(path, h, color):
    """Load a PNG silhouette (alpha, or dark-on-light) scaled to height h, tinted with color."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        a = np.asarray(im.convert("RGBA"), np.float32)[..., 3] / 255
    else:
        g = np.asarray(im.convert("L"), np.float32) / 255
        a = np.clip((0.85 - g) / 0.6, 0, 1)
    ys, xs = np.nonzero(a > 0.05)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = h / a.shape[0]
    a = cv2.resize(a, (max(1, int(round(a.shape[1] * k))), max(1, int(round(h)))), interpolation=cv2.INTER_AREA)
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = color
    spr[..., 3] = a
    return spr


def _nice_step(top):
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if top / step <= 5:
            return step
    return 1000


def scale_compare(out, duration, items, unit="m", size=HD, title=None, bg="paper", fps=FPS):
    """items: [{"name": str, "height_m": float, "silhouette": None | "path.png",
                "shape": "bar"|"taper"|"arch", "accent": bool}, ...]
    Sorted by height (shortest left). Each rises in turn from a shared ground line; a height label rides the top
    and the name sits under the ground. Faint gridlines give the scale. `unit` is the label suffix ("m", "ft")."""
    unit_label = unit
    size = even(size)
    W, H = size
    u = layout_unit(size)
    items = sorted(items, key=lambda it: it["height_m"])
    n = len(items)
    top_val = max(it["height_m"] for it in items)
    left, right = 0.10 * W, 0.96 * W
    ground = 0.80 * H if W >= H else 0.78 * H
    sky = (0.20 if title else 0.13) * H
    px_per_m = (ground - sky) / top_val
    col = (right - left) / n
    name_f = font("sans", 28 * u)
    val_f = font("serif", 34 * u, "bold")
    grid_f = font("sans", 22 * u)
    title_f = font("serif", 54 * u, "bold")

    base = background(size, bg)
    step = _nice_step(top_val)
    for v in range(step, int(top_val) + 1, step):
        y = ground - v * px_per_m
        blend(base, MUTED, rect_mask(base.shape, left - 0.02 * W, y - 0.5 * u, right, y + 0.5 * u) * 0.35)
        spr, _ = text_sprite(f"{v} {unit_label}", grid_f, MUTED)
        paste(base, spr, left - 0.025 * W - spr.shape[1], y - spr.shape[0] / 2)
    blend(base, INK, rect_mask(base.shape, left - 0.02 * W, ground, right, ground + max(2, 3 * u)))
    if title:
        spr, _ = text_sprite(title, title_f, INK)
        paste(base, spr, (W - spr.shape[1]) / 2, 0.06 * H)

    cols = []
    for i, it in enumerate(items):
        cx = left + col * (i + 0.5)
        h = it["height_m"] * px_per_m
        color = ACCENT if it.get("accent") else INK
        if it.get("silhouette"):
            spr = _silhouette_sprite(it["silhouette"], h, color)
        else:
            shape = it.get("shape", "bar")
            wid = col * (0.62 if shape == "arch" else 0.34)
            spr = _shape_sprite(shape, wid, h, color)
        lines = wrap(it["name"], name_f, col * 0.92)[:2]
        names = [text_sprite(line, name_f, INK)[0] for line in lines]
        cols.append({"cx": cx, "h": h, "spr": spr, "names": names, "val": it["height_m"], "color": color})

    rise = min(1.6, duration * 0.3)
    gap = min(0.55, (duration * 0.75 - rise) / max(1, n))
    times = frame_times(duration, fps)
    with Writer(out, size, fps) as w:
        for t in times:
            frame = base.copy()
            for i, c in enumerate(cols):
                t0 = 0.3 + i * gap
                p = ramp(t, t0, rise)
                nf = ramp(t, t0 - 0.15, 0.5)
                for k, nspr in enumerate(c["names"]):
                    paste(frame, nspr, c["cx"] - nspr.shape[1] / 2, ground + 12 * u + k * name_f.size * 1.15, nf)
                if p <= 0:
                    continue
                spr = c["spr"].copy()
                sh, sw = spr.shape[:2]
                # reveal from the ground up with a fractional top edge
                cut = sh * (1 - p)
                rows = np.clip(np.arange(sh, dtype=np.float32) + 1 - cut, 0, 1)
                spr[..., 3] *= rows[:, None]
                paste(frame, spr, c["cx"] - sw / 2, ground - sh)
                top = ground - sh * p
                label = f"{round(c['val'] * p):d} {unit_label}"
                lspr, _ = text_sprite(label, val_f, c["color"])
                paste(frame, lspr, c["cx"] - text_width(label, val_f) / 2 - 2, top - lspr.shape[0] - 6 * u,
                      ramp(t, t0, 0.4))
            w.write(frame)
    return out
