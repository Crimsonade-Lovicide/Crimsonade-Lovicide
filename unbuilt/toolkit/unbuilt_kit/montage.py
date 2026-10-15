"""Montage: a grid of archive images that appear one by one, then hold with a gentle push-in."""
import numpy as np
from PIL import Image

from .core import FPS, HD, Writer, even, frame_times, lerp, load_rgb, paper, ramp


def montage(images, out, duration, cols=4, rows=2, size=HD, gap=0.03, stagger=0.6, zoom=1.06, fps=FPS):
    """Lay out `images` (paths) in a cols x rows grid on paper; cells fade in over the first `stagger`
    fraction of the clip in reading order, and the whole sheet pushes in from 1.0 to `zoom`."""
    size = even(size)
    w, h = size
    ss = 2
    W, H = w * ss, h * ss
    base = (paper((W, H)) * 255).astype(np.uint8)
    cw, ch = W * (1 - gap * (cols + 1)) / cols, H * (1 - gap * (rows + 1)) / rows
    cells = []
    for i, path in enumerate(images[:cols * rows]):
        r, c = divmod(i, cols)
        x0, y0 = W * gap + c * (cw + W * gap), H * gap + r * (ch + H * gap)
        im = Image.fromarray((load_rgb(path) * 255).astype(np.uint8))
        s = min(cw / im.width, ch / im.height)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        cells.append((np.asarray(im), int(x0 + (cw - im.width) / 2), int(y0 + (ch - im.height) / 2)))
    n_in = max(1, len(cells))
    times = frame_times(duration, fps)
    with Writer(out, size, fps) as wr:
        for t in times:
            frame = base.astype(np.float32)
            for k, (arr, x, y) in enumerate(cells):
                a = ramp(t, duration * stagger * k / n_in, 0.45)
                if a <= 0:
                    continue
                hh, ww = arr.shape[:2]
                region = frame[y:y + hh, x:x + ww]
                region[:] = region * (1 - a) + arr[:hh, :ww].astype(np.float32) * a
            z = lerp(1.0, zoom, t / duration)
            cw2, ch2 = W / z, H / z
            x0, y0 = (W - cw2) / 2, (H - ch2) / 2
            crop = Image.fromarray(frame.clip(0, 255).astype(np.uint8)).resize(
                (w, h), Image.LANCZOS, box=(x0, y0, x0 + cw2, y0 + ch2))
            wr.write(np.asarray(crop, np.float32) / 255)
    return out
