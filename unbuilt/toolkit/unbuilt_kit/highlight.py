"""Newspaper highlight: push in on a passage, dim the rest, sweep a marker across it."""
import cv2
import numpy as np

from .core import (ACCENT, FPS, HD, Writer, apply_affine, camera_matrix, even, frame_times, load_rgb, ramp,
                   rect_mask, render_view, unit)
from .kenburns import plan_views, view_at


def highlight(scan, out, duration, box, size=HD, bg="paper", fill=0.72, dim=0.45, marker=ACCENT,
              marker_alpha=0.30, fps=FPS):
    """box: (x0, y0, x1, y1) as fractions of the scan.

    Timeline (fractions of duration): push-in 0-0.55; dimming 0.15-0.5; marker sweep 0.5-0.8.
    fill: how much of the frame the box fills at the end of the push. dim: brightness left outside the box.
    The marker multiplies, like a translucent felt-tip over newsprint.
    """
    size = even(size)
    W, H = size
    img = load_rgb(scan)
    x0, y0, x1, y1 = box
    # zoom that makes the box fill `fill` of the frame, measured against the plate at zoom 1
    probe_plate, _, _, rect = plan_views(img, size, (0.5, 0.5, 1.0), (0.5, 0.5, 1.0), bg)
    pw = probe_plate.shape[1]
    box_w, box_h = (x1 - x0) * rect[2], (y1 - y0) * rect[3]
    zoom = min(fill * pw / box_w, fill * pw * H / W / box_h)
    zoom = max(1.0, min(zoom, 6.0))
    centre = ((x0 + x1) / 2, (y0 + y1) / 2, zoom)
    plate, v0, v1, rect = plan_views(img, size, (0.5, 0.5, 1.0), centre, bg)
    corners = np.array([[rect[0] + x0 * rect[2], rect[1] + y0 * rect[3]],
                        [rect[0] + x1 * rect[2], rect[1] + y1 * rect[3]]])
    feather = 10 * unit(size)
    pad = 6 * unit(size)
    times = frame_times(duration, fps)
    with Writer(out, size, fps) as w:
        for t in times:
            u = t / duration
            view = view_at(v0, v1, min(1.0, u / 0.55))
            frame = render_view(plate, view, size)
            (bx0, by0), (bx1, by1) = apply_affine(camera_matrix(view, size), corners)
            d = ramp(u, 0.15, 0.35)
            if d > 0:
                inside = rect_mask(frame.shape, bx0 - pad, by0 - pad, bx1 + pad, by1 + pad)
                inside = cv2.GaussianBlur(inside, (0, 0), feather)
                frame *= (1 - d * (1 - dim) * (1 - inside))[..., None]
            s = ramp(u, 0.5, 0.3)
            if s > 0:
                mk = rect_mask(frame.shape, bx0 - pad, by0, bx0 - pad + (bx1 - bx0 + 2 * pad) * s, by1)
                tint = 1 - marker_alpha * (1 - np.asarray(marker, np.float32))
                frame *= 1 - mk[..., None] * (1 - tint)
            w.write(frame)
    return out
