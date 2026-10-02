"""Timeline: a rule draws across the frame; each event's tick, year and label appear as the line reaches it."""
import numpy as np

from .core import (ACCENT, FPS, HD, INK, MUTED, Writer, background, blend, ease, even, font, frame_times, lerp,
                   paste, ramp, rect_mask, text_sprite, unit, wrap)


def _positions(years, x0, x1, min_gap, spacing):
    """x of each event: proportional to the year, nudged apart so neighbours keep min_gap, then refitted."""
    n = len(years)
    if n == 1:
        return [(x0 + x1) / 2]
    if spacing == "even":
        return list(np.linspace(x0, x1, n))
    span = (years[-1] - years[0]) or 1
    xs = [x0 + (y - years[0]) / span * (x1 - x0) for y in years]
    if spacing == "auto":
        for i in range(1, n):
            xs[i] = max(xs[i], xs[i - 1] + min_gap)
        k = (x1 - x0) / (xs[-1] - x0)
        xs = [x0 + (x - x0) * k for x in xs]
    return xs


def _inside(left, width, W):
    """Keep a centred label inside the frame's side margins."""
    return min(max(left, 0.03 * W), 0.97 * W - width)


def timeline(out, duration, events, size=HD, title=None, spacing="auto", accent_last=False, bg="paper", fps=FPS):
    """events: [(year, label), ...] in any order (sorted by year).
    spacing: "auto" (proportional to time but never crowded), "proportional", or "even".
    Labels alternate above and below the line. The line draws on over the first ~75% of the clip."""
    size = even(size)
    W, H = size
    u = unit(size)
    events = sorted(events, key=lambda e: e[0])
    n = len(events)
    x0, x1 = 0.08 * W, 0.92 * W
    ly = 0.55 * H
    xs = _positions([e[0] for e in events], x0, x1, (x1 - x0) / max(n, 1) * 0.6, spacing)
    year_f = font("serif", 58 * u, "bold")
    label_f = font("sans", 30 * u)
    title_f = font("serif", 54 * u, "bold")
    tick = 22 * u
    line_w = max(2, 3 * u)
    max_label_w = min(0.30 * W, 2 * (x1 - x0) / max(n, 1) * 0.92)

    base = background(size, bg)
    if title:
        spr, _ = text_sprite(title, title_f, INK)
        paste(base, spr, (W - spr.shape[1]) / 2, 0.2 * H)

    sprites = []
    for i, (year, label) in enumerate(events):
        above = i % 2 == 0
        color = ACCENT if (accent_last and i == n - 1) else INK
        ys, _ = text_sprite(str(year), year_f, color)
        ls = [text_sprite(line, label_f, MUTED)[0] for line in wrap(label, label_f, max_label_w)]
        sprites.append((ys, ls, above, color))

    draw_end = duration * 0.75
    head_start = 0.3
    times = frame_times(duration, fps)
    with Writer(out, size, fps) as w:
        for t in times:
            frame = base.copy()
            p = ease((t - head_start) / max(0.1, draw_end - head_start))
            head = lerp(x0 - 0.02 * W, x1 + 0.02 * W, p)
            blend(frame, INK, rect_mask(frame.shape, x0 - 0.02 * W, ly - line_w / 2, head, ly + line_w / 2))
            for x, (ys, ls, above, color) in zip(xs, sprites):
                if head < x:
                    continue
                # time the head crossed this tick, solved from the eased path
                q = (x - (x0 - 0.02 * W)) / ((x1 + 0.02 * W) - (x0 - 0.02 * W))
                tc = head_start + np.arccos(1 - 2 * q) / np.pi * (draw_end - head_start)
                a = ramp(t, tc, 0.5)
                rise = (1 - a) * 10 * u * (1 if above else -1)
                tk = ramp(t, tc, 0.25)
                y_a, y_b = (ly - tick * tk, ly) if above else (ly, ly + tick * tk)
                blend(frame, color, rect_mask(frame.shape, x - line_w / 2, y_a, x + line_w / 2, y_b))
                block_h = ys.shape[0] + sum(s.shape[0] for s in ls)
                y = (ly - tick - 10 * u - block_h if above else ly + tick + 10 * u) + rise
                paste(frame, ys, _inside(x - ys.shape[1] / 2, ys.shape[1], W), y, a)
                y += ys.shape[0]
                for s in ls:
                    paste(frame, s, _inside(x - s.shape[1] / 2, s.shape[1], W), y, a)
                    y += s.shape[0] * 0.9
            w.write(frame)
    return out
