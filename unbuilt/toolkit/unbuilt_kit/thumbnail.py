"""1280x720 thumbnail compositor: archive background, a drawing cut out of its paper, three big words."""
import cv2
import numpy as np
from PIL import Image

from .core import ACCENT, INK, PAPER, blend, font, load_rgb, paper, paste, rect_mask, text_sprite, text_width

SIZE = (1280, 720)


def cutout(image, threshold=None, solid=True):
    """Cut a drawing out of its paper with OpenCV. Returns an RGBA float array.
    The ink is found by thresholding (Otsu unless `threshold` 0..255 is given). With solid=True the outline is
    closed and filled, so the paper inside the drawing stays and the cut-out reads like a sticker."""
    rgb = load_rgb(image)
    g = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    if threshold is None:
        _, ink = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, ink = cv2.threshold(g, threshold, 255, cv2.THRESH_BINARY_INV)
    ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))      # drop paper speckle
    if solid:
        k = max(3, int(min(g.shape) * 0.012)) | 1
        mask = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        # fill holes: flood the background from the border, everything not reached is inside
        flood = mask.copy()
        h, w = mask.shape
        ff = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(flood, ff, (0, 0), 255)
        mask = mask | cv2.bitwise_not(flood)
        # keep the largest pieces only (the drawing, not stray marks or the plate border)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
        if n > 1:
            big = stats[1:, cv2.CC_STAT_AREA].max()
            keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > big * 0.05]
            mask = np.isin(lab, keep).astype(np.uint8) * 255
    else:
        mask = ink
    alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 0.8)
    return np.dstack([rgb, alpha]).astype(np.float32)


def _crop_to_alpha(rgba):
    ys, xs = np.nonzero(rgba[..., 3] > 0.02)
    return rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _fit_into(rgba, box_px):
    x0, y0, x1, y1 = box_px
    h, w = rgba.shape[:2]
    k = min((x1 - x0) / w, (y1 - y0) / h)
    nw, nh = max(1, int(w * k)), max(1, int(h * k))
    small = cv2.resize(rgba, (nw, nh), interpolation=cv2.INTER_AREA)
    return small, x0 + ((x1 - x0) - nw) / 2, y0 + ((y1 - y0) - nh) / 2


def _glow(rgba, radius, color, strength=1.0):
    """A soft halo sprite the same size as rgba plus padding."""
    pad = int(radius * 3)
    a = np.pad(rgba[..., 3], pad)
    a = cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(radius) | 1, int(radius) | 1)))
    a = np.clip(cv2.GaussianBlur(a, (0, 0), radius * 0.6) * 1.5 * strength, 0, 1)
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = color
    spr[..., 3] = a
    return spr, pad


def _cover(img, size):
    W, H = size
    h, w = img.shape[:2]
    k = max(W / w, H / h)
    big = cv2.resize(img, (int(np.ceil(w * k)), int(np.ceil(h * k))), interpolation=cv2.INTER_AREA)
    y = (big.shape[0] - H) // 3       # bias toward the top: towers live up there
    x = (big.shape[1] - W) // 2
    return np.ascontiguousarray(big[y:y + H, x:x + W])


def _big_text(words, max_w, max_h, color, kind="sans", style="bold", lines=None):
    """Fit 1-3 words, one per line, as large as the box allows. Returns (list of sprites, line height)."""
    lines = lines or words.upper().split()
    size = 220
    while size > 20:
        f = font(kind, size, style)
        widest = max(text_width(line, f, 0.01) for line in lines)
        if widest <= max_w and size * 0.98 * len(lines) <= max_h:
            break
        size -= 4
    f = font(kind, size, style)
    return [text_sprite(line, f, color, 0.01)[0] for line in lines], f.size * 0.98, f


def thumbnail(out_png, background_image, overlay_image=None, overlay_box=(0.55, 0.05, 0.97, 0.97),
              text="3 WORDS MAX", variant=1, red_word=None, cut_threshold=None):
    """Compose a 1280x720 PNG.
    variant 1 "dark":  graded, darkened archive background; paper-white text left; cut-out with a white glow.
    variant 2 "paper": paper ground, the background as a tilted print; ink text; cut-out with a soft shadow.
    variant 3 "band":  full-bleed background; a red band carrying paper-white text; cut-out with a paper glow.
    overlay_box: (x0, y0, x1, y1) fractions of the thumbnail where the cut-out is fitted.
    red_word: index of the word printed in red (variants 1 and 2). Default: the last word."""
    if len(text.split()) > 3:
        print(f"thumbnail: '{text}' is more than 3 words")
    W, H = SIZE
    bg = load_rgb(background_image)
    words = text.upper().split()
    red_word = len(words) - 1 if red_word is None else red_word

    if variant == 1:
        frame = cv2.GaussianBlur(_cover(bg, SIZE), (0, 0), 2.5)   # soften: the cut-out and text carry the image
        grey = frame.mean(axis=2, keepdims=True)
        frame = (0.25 * frame + 0.75 * grey) * 0.5           # mostly monochrome, darker
        xs = np.linspace(0, 1, W, dtype=np.float32)
        frame *= (0.35 + 0.65 * np.clip((xs - 0.05) / 0.55, 0, 1))[None, :, None]   # darker on the text side
        text_color, glow_color = PAPER, (1, 1, 1)
        text_box = (0.05 * W, 0.12 * H, 0.50 * W, 0.88 * H)
    elif variant == 2:
        frame = paper(SIZE)
        print_img = cv2.resize(bg, (int(0.40 * W), int(0.40 * W * bg.shape[0] / bg.shape[1])),
                               interpolation=cv2.INTER_AREA)
        ph = min(print_img.shape[0], int(0.98 * H))
        print_img = print_img[:ph]
        rgba = np.dstack([print_img, np.ones(print_img.shape[:2], np.float32)])
        border = int(0.012 * W)
        rgba = np.pad(rgba, ((border, border), (border, border), (0, 0)), constant_values=1.0)
        rgba[:border, :, :3] = PAPER          # a paper border, like a print
        rgba[-border:, :, :3] = PAPER
        rgba[:, :border, :3] = PAPER
        rgba[:, -border:, :3] = PAPER
        hh, ww = rgba.shape[:2]
        m = cv2.getRotationMatrix2D((ww / 2, hh / 2), -3.0, 1.0)
        rot = cv2.warpAffine(rgba, m, (ww, hh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        sh, pad = _glow(rot, 18, (0, 0, 0), 0.5)
        px, py = W * 0.56, (H - hh) / 2
        paste(frame, sh, px - pad + 8, py - pad + 10)
        paste(frame, rot, px, py)
        text_color, glow_color = INK, None
        text_box = (0.05 * W, 0.14 * H, 0.50 * W, 0.86 * H)
    else:
        frame = cv2.GaussianBlur(_cover(bg, SIZE), (0, 0), 2.0)
        grey = frame.mean(axis=2, keepdims=True)
        frame = (0.4 * frame + 0.6 * grey) * 0.8
        text_color, glow_color = PAPER, PAPER
        text_box = (0.07 * W, 0.62 * H, 0.66 * W, 0.92 * H)

    if overlay_image is not None:
        cut = _crop_to_alpha(cutout(overlay_image, cut_threshold))
        x0, y0, x1, y1 = overlay_box
        small, ox, oy = _fit_into(cut, (x0 * W, y0 * H, x1 * W, y1 * H))
        if glow_color is not None:
            g, pad = _glow(small, 10, glow_color, 0.9)
            paste(frame, g, ox - pad, oy - pad)
        else:
            g, pad = _glow(small, 14, (0, 0, 0), 0.45)
            paste(frame, g, ox - pad + 6, oy - pad + 8)
        paste(frame, small, ox, oy)

    tx0, ty0, tx1, ty1 = text_box
    if variant == 3:
        band = rect_mask(frame.shape, 0, ty0 - 0.04 * H, tx1 + 0.03 * W, ty1 + 0.03 * H)
        blend(frame, ACCENT, band)
        sprites, lh, f = _big_text(" ".join(words), tx1 - tx0, ty1 - ty0, text_color, lines=[" ".join(words)])
    else:
        sprites, lh, f = _big_text(" ".join(words), tx1 - tx0, ty1 - ty0, text_color)
        if len(sprites) == len(words):
            sprites = [text_sprite(wd, f, ACCENT if i == red_word else text_color, 0.01)[0]
                       for i, wd in enumerate(words)]
    total = lh * len(sprites)
    y = ty0 + (ty1 - ty0 - total) / 2
    for spr in sprites:
        if variant == 1:     # a soft dark shadow keeps light text readable on any background
            sh = spr.copy()
            sh[..., :3] = 0
            sh[..., 3] = cv2.GaussianBlur(sh[..., 3], (0, 0), 6) * 0.8
            paste(frame, sh, tx0 + 3, y + 4)
        paste(frame, spr, tx0, y)
        y += lh
    Image.fromarray((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out_png)
    return out_png
