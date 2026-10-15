"""Ken Burns: a slow pan and zoom over a still."""
from .core import FPS, HD, Writer, ease, even, fit_plate, frame_times, lerp, load_rgb, render_view, view_rect


def plan_views(img, size, start, end, bg="paper", mode="auto"):
    """Build the plate and the two clamped camera views. Shared with annotate/highlight."""
    # plate resolution: enough for the closest zoom, but never beyond the source's own detail (or 4x the frame)
    ih, iw = img.shape[:2]
    native = 1 / min(size[0] / iw, size[1] / ih)
    scale = max(1.0, min(max(start[2], end[2]), native, 4.0))
    plate, rect = fit_plate(img, size, scale, bg=bg, mode=mode)
    psize = (plate.shape[1], plate.shape[0])
    return plate, view_rect(psize, rect, *start), view_rect(psize, rect, *end), rect


def view_at(v0, v1, t):
    """Interpolate the view rectangle (left, top, width). Both ends lie inside the plate, so every frame does too."""
    e = ease(t)
    return tuple(lerp(a, b, e) for a, b in zip(v0, v1))


def kenburns(image, out, duration, start=(0.5, 0.5, 1.0), end=(0.5, 0.5, 1.15), size=HD, bg="paper",
             mode="auto", fps=FPS):
    """Render a cosine-eased pan/zoom over `image` to an mp4.

    start, end: (cx, cy, zoom). cx, cy are fractions of the image (0,0 top-left); zoom 1 shows the whole frame.
    Images whose aspect differs from the frame are fitted on paper (bg="paper" or "ink") with a soft shadow,
    so nothing important is cropped; mode="cover" forces a full-bleed crop instead.
    """
    size = even(size)
    img = load_rgb(image)
    plate, v0, v1, _ = plan_views(img, size, start, end, bg, mode)
    times = frame_times(duration, fps)
    n = len(times)
    with Writer(out, size, fps) as w:
        for i in range(n):
            t = i / (n - 1) if n > 1 else 0
            w.write(render_view(plate, view_at(v0, v1, t), size))
    return out
