"""Typeset cards: title, lower third (with alpha), quote, end card; plus overlay()."""
import glob
import os

import numpy as np

from .core import (ACCENT, FPS, HD, INK, MUTED, Writer, background, blend, even, font, frame_times, paste,
                   ramp, rect_mask, run_ffmpeg, text_sprite, unit, wrap)


def _fade(t, duration, fade_in=0.0, fade_out=0.6):
    """Opacity for elements that settle in and, optionally, leave before the cut."""
    out = 1 - ramp(t, duration - fade_out, fade_out) if fade_out else 1.0
    return out if fade_in <= 0 else min(out, ramp(t, 0, fade_in))


def _lines(text, fnt, max_w, color, tracking=0.0):
    return [text_sprite(line, fnt, color, tracking)[0] for line in wrap(text, fnt, max_w)]


def title_card(out, duration, title, subtitle=None, size=HD, bg="paper", fade_out=0.6, fps=FPS):
    """Serif title centred on paper, a red rule drawing out from the centre, a letter-spaced subtitle."""
    size = even(size)
    W, H = size
    u = unit(size)
    tf = font("serif", (96 if W >= H else 84) * u, "bold")
    sf = font("sans", 28 * u)
    titles = _lines(title, tf, W * 0.82, INK)
    subs = _lines(subtitle.upper(), sf, W * 0.8, MUTED, tracking=0.18) if subtitle else []
    lh = tf.size * 1.12
    block = lh * len(titles) + (40 * u + sf.size * 1.4 * len(subs) if subs else 0)
    y0 = (H - block) / 2 - 10 * u
    base = background(size, bg)
    rule_w = min(W * 0.5, 260 * u)
    with Writer(out, size, fps) as w:
        for t in frame_times(duration, fps):
            frame = base.copy()
            k = _fade(t, duration, 0, fade_out)
            a = ramp(t, 0.15, 0.9) * k
            y = y0 + (1 - ramp(t, 0.15, 1.1)) * 12 * u
            for spr in titles:
                paste(frame, spr, (W - spr.shape[1]) / 2, y, a)
                y += lh
            r = ramp(t, 0.6, 0.9) * k
            ry = y0 + lh * len(titles) + 18 * u
            if r > 0:
                half = rule_w / 2 * ramp(t, 0.6, 0.9)
                blend(frame, ACCENT, rect_mask(frame.shape, W / 2 - half, ry, W / 2 + half, ry + max(2, 3 * u)) * k)
            sy = ry + 26 * u
            for spr in subs:
                paste(frame, spr, (W - spr.shape[1]) / 2, sy, ramp(t, 1.0, 0.8) * k)
                sy += sf.size * 1.4
            w.write(frame)
    return out


def lower_third(out, duration, text, subtext=None, size=HD, fps=FPS):
    """Name strap on a transparent background, for overlay().
    out: '*.mov' -> QuickTime Animation with alpha; a directory or 'dir/' -> RGBA PNG sequence.
    A paper plate with a red edge wipes in from the left, text fades up; it all reverses out at the end."""
    size = even(size)
    W, H = size
    u = unit(size)
    nf = font("serif", 44 * u, "bold")
    sf = font("sans", 25 * u)
    name, _ = text_sprite(text, nf, INK)
    sub = text_sprite(subtext, sf, MUTED, tracking=0.04)[0] if subtext else None
    padx, pady = 30 * u, 18 * u
    bw = max(name.shape[1], sub.shape[1] if sub is not None else 0) + 2 * padx
    bh = name.shape[0] + (sub.shape[0] if sub is not None else 0) + 2 * pady
    x0 = 0.065 * W
    y0 = (0.86 if W >= H else 0.70) * H - bh
    edge = max(3, 6 * u)
    with Writer(out, size, fps, alpha=True) as w:
        for t in frame_times(duration, fps):
            frame = np.zeros((H, W, 4), np.float32)
            wipe = ramp(t, 0.0, 0.6) * (1 - ramp(t, duration - 0.6, 0.5))
            if wipe > 0:
                # colour everywhere is paper (red for the edge bar); alpha cuts out the plate, so it also masks the text
                bar = rect_mask(frame.shape, x0, y0, x0 + edge, y0 + bh)
                plate = rect_mask(frame.shape, x0, y0, x0 + edge + bw * wipe, y0 + bh)
                rgb = background(size, "paper")
                blend(rgb, ACCENT, bar)
                ta = ramp(t, 0.35, 0.5) * (1 - ramp(t, duration - 0.7, 0.4))
                paste(rgb, name, x0 + edge + padx, y0 + pady, ta)
                if sub is not None:
                    paste(rgb, sub, x0 + edge + padx, y0 + pady + name.shape[0], ta)
                frame[..., :3] = rgb
                frame[..., 3] = np.maximum(plate * 0.95, bar * plate)
            w.write(frame)
    return out


def overlay(base_mp4, overlay_src, out, start=0.0):
    """Lay an alpha overlay (.mov, or a PNG-sequence directory from lower_third) over a clip from `start` seconds.
    Keeps the base's length and audio."""
    if os.path.isdir(overlay_src):
        first = sorted(glob.glob(os.path.join(overlay_src, "frame_*.png")))[0]
        src = ["-framerate", str(FPS), "-start_number", first[-9:-4], "-i", os.path.join(overlay_src, "frame_%05d.png")]
    else:
        src = ["-i", overlay_src]
    fc = (f"[1:v]format=rgba,setpts=PTS-STARTPTS+{start}/TB[o];"
          f"[0:v][o]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]")
    run_ffmpeg(["-i", base_mp4] + src + ["-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
                                         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                                         "-c:a", "copy", "-r", str(FPS), "-movflags", "+faststart", out])
    return out


def quote_card(out, duration, quote, attribution, size=HD, bg="paper", fade_out=0.6, fps=FPS):
    """A quotation set in serif italic; words fade in line by line, then the attribution."""
    size = even(size)
    W, H = size
    u = unit(size)
    qf = font("serif", (54 if W >= H else 58) * u, "italic")
    af = font("sans", 26 * u)
    mark_f = font("serif", 150 * u, "bold")
    lines = wrap(quote, qf, W * (0.70 if W >= H else 0.82))
    lh = qf.size * 1.32
    attr_text = "— " + attribution
    block = lh * len(lines) + 40 * u + af.size
    y0 = (H - block) / 2
    x_left = (W - max(qf.getlength(line) for line in lines)) / 2
    words = []   # (sprite, x, y)
    for i, line in enumerate(lines):
        x = x_left
        for word in line.split():
            spr, _ = text_sprite(word, qf, INK)
            words.append((spr, x, y0 + i * lh, i))
            x += qf.getlength(word + " ")
    attr, _ = text_sprite(attr_text, af, MUTED, tracking=0.03)
    mark, _ = text_sprite("\u201c", mark_f, ACCENT)
    mark_x = x_left - mark_f.getlength("\u201c") - 14 * u     # hangs in the left margin
    per_line = min(1.4, (duration * 0.6) / max(1, len(lines)))
    base = background(size, bg)
    with Writer(out, size, fps) as w:
        for t in frame_times(duration, fps):
            frame = base.copy()
            k = _fade(t, duration, 0, fade_out)
            paste(frame, mark, mark_x, y0 - mark_f.size * 0.38, ramp(t, 0.1, 0.8) * k)
            count = {}
            for spr, x, y, li in words:
                j = count.get(li, 0)
                count[li] = j + 1
                a = ramp(t, 0.4 + li * per_line + j * 0.09, 0.55) * k
                paste(frame, spr, x, y, a)
            ta = ramp(t, 0.4 + len(lines) * per_line + 0.2, 0.7) * k
            paste(frame, attr, x_left, y0 + lh * len(lines) + 30 * u, ta)
            w.write(frame)
    return out


def end_card(out, duration, text="Sources in the description", size=HD, bg="paper", wordmark="UNBUILT", fps=FPS):
    """Channel wordmark, a short red rule, and a line of sans text."""
    size = even(size)
    W, H = size
    u = unit(size)
    wf = font("serif", 88 * u, "bold")
    tf = font("sans", 30 * u)
    mark, _ = text_sprite(wordmark, wf, INK, tracking=0.12)
    lines = _lines(text, tf, W * 0.8, MUTED, tracking=0.02)
    y0 = H * 0.5 - mark.shape[0] * 0.9
    base = background(size, bg)
    with Writer(out, size, fps) as w:
        for t in frame_times(duration, fps):
            frame = base.copy()
            paste(frame, mark, (W - mark.shape[1]) / 2, y0, ramp(t, 0.1, 0.9))
            r = ramp(t, 0.5, 0.8)
            ry = y0 + mark.shape[0] + 14 * u
            half = 60 * u * r
            if r > 0:
                blend(frame, ACCENT, rect_mask(frame.shape, W / 2 - half, ry, W / 2 + half, ry + max(2, 3 * u)))
            y = ry + 30 * u
            for spr in lines:
                paste(frame, spr, (W - spr.shape[1]) / 2, y, ramp(t, 0.9, 0.8))
                y += tf.size * 1.4
            w.write(frame)
    return out
