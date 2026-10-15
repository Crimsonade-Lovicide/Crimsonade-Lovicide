"""Shared plumbing: ffmpeg discovery, frame writer, probe, house colours, fonts, easing, drawing helpers.

Frames are float32 RGB arrays in 0..1, shape (H, W, 3). Sprites are float32 RGBA, straight alpha.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 24
HD = (1920, 1080)
VERTICAL = (1080, 1920)

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(KIT_DIR), "fonts")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


PAPER = hex_rgb("#F2EDE4")
INK = hex_rgb("#1B1B1B")
ACCENT = hex_rgb("#C8102E")
MUTED = hex_rgb("#6B6B6B")


def to255(c, a=None):
    """House colour (0..1 floats) -> PIL tuple."""
    t = tuple(int(round(v * 255)) for v in c)
    return t if a is None else t + (int(round(a * 255)),)


# ---------------------------------------------------------------- ffmpeg

def ffmpeg_exe():
    """FFMPEG env var, then the imageio-ffmpeg static binary, then PATH."""
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found: set FFMPEG, `pip install imageio-ffmpeg`, or install ffmpeg")
    return exe


def ffprobe_exe():
    """ffprobe next to ffmpeg or on PATH; None if there is none (imageio-ffmpeg ships ffmpeg only)."""
    ff = ffmpeg_exe()
    side = os.path.join(os.path.dirname(ff), "ffprobe")
    if os.path.basename(ff).startswith("ffmpeg") and os.path.exists(side):
        return side
    return shutil.which("ffprobe")


def run_ffmpeg(args, quiet=True):
    cmd = [ffmpeg_exe(), "-nostdin", "-y", "-hide_banner"] + (["-loglevel", "error"] if quiet else []) + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + " ".join(cmd) + "\n" + r.stderr[-3000:])
    return r


def probe(path):
    """{'width','height','fps','frames','duration'} of the first video stream.
    Uses ffprobe when present, otherwise decodes with ffmpeg and counts frames."""
    fp = ffprobe_exe()
    if fp:
        out = subprocess.run([fp, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                              "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json", path],
                             capture_output=True, text=True, check=True).stdout
        s = json.loads(out)["streams"][0]
        num, den = s["r_frame_rate"].split("/")
        fps = float(num) / float(den)
        n = int(s["nb_read_frames"])
    else:
        err = subprocess.run([ffmpeg_exe(), "-nostdin", "-hide_banner", "-i", path, "-map", "0:v:0", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        m = re.search(r"Stream #0:\d+.*?Video:.*?(\d{2,5})x(\d{2,5})", err)
        s = {"width": int(m.group(1)), "height": int(m.group(2))}
        fps = float(re.search(r"(\d+(?:\.\d+)?) fps", err).group(1))
        n = int(re.findall(r"frame=\s*(\d+)", err)[-1])
    return {"width": int(s["width"]), "height": int(s["height"]), "fps": fps, "frames": n, "duration": n / fps}


def has_audio(path):
    err = subprocess.run([ffmpeg_exe(), "-nostdin", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    return "Audio:" in err


def loudness(path):
    """Integrated loudness (LUFS) of a file's audio."""
    err = subprocess.run([ffmpeg_exe(), "-nostdin", "-hide_banner", "-i", path, "-af", "ebur128=framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


# ---------------------------------------------------------------- writing frames

class Writer:
    """Pipe frames to ffmpeg. Output kind follows the path:
    .mp4 -> H.264 yuv420p;  .mov with alpha -> QuickTime Animation (qtrle, argb);
    a directory (or a path ending in '/') -> numbered RGBA PNG sequence."""

    def __init__(self, out, size, fps=FPS, alpha=False):
        self.out, self.size, self.fps, self.alpha = out, size, fps, alpha
        self.n = 0
        self.png_dir = out.endswith("/") or os.path.isdir(out)
        os.makedirs(os.path.dirname(os.path.abspath(out.rstrip("/"))) or ".", exist_ok=True)
        if self.png_dir:
            os.makedirs(out, exist_ok=True)
            for f in glob.glob(os.path.join(out, "frame_*.png")):
                os.remove(f)
            self.proc = None
            return
        w, h = size
        src = ["-f", "rawvideo", "-pix_fmt", "rgba" if alpha else "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
        if out.lower().endswith(".mov") and alpha:
            enc = ["-c:v", "qtrle", "-pix_fmt", "argb"]
        else:
            enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                   "-movflags", "+faststart"]
        cmd = [ffmpeg_exe(), "-nostdin", "-y", "-hide_banner", "-loglevel", "error"] + src + ["-an"] + enc + \
              ["-r", str(fps), out]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, frame):
        """frame: float RGB (or RGBA when alpha) in 0..1."""
        a = (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)
        h, w = a.shape[:2]
        assert (w, h) == tuple(self.size), f"frame {w}x{h} != writer {self.size}"
        if self.png_dir:
            Image.fromarray(a, "RGBA" if self.alpha else "RGB").save(
                os.path.join(self.out, f"frame_{self.n:05d}.png"), compress_level=3)
        else:
            self.proc.stdin.write(a.tobytes())
        self.n += 1

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            if self.proc.wait() != 0:
                raise RuntimeError(f"ffmpeg failed writing {self.out}")
        return self.out

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def frame_times(duration, fps=FPS):
    n = max(1, int(round(duration * fps)))
    return [i / fps for i in range(n)]


def even(size):
    w, h = size
    return (int(w) // 2 * 2, int(h) // 2 * 2)


# ---------------------------------------------------------------- motion

def clamp01(x):
    return min(1.0, max(0.0, x))


def ease(t):
    """Cosine ease-in-out on 0..1."""
    return 0.5 - 0.5 * math.cos(math.pi * clamp01(t))


def ramp(t, start, dur):
    """Eased 0->1 between start and start+dur."""
    return ease((t - start) / dur) if dur > 0 else float(t >= start)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- paper

_paper_cache = {}


def paper(size, tone=PAPER, seed=7):
    """Off-white paper: flat tone, faint mottling, fine grain and a soft vignette. Static, so it compresses well."""
    key = (size, tone, seed)
    if key not in _paper_cache:
        w, h = size
        rng = np.random.default_rng(seed)
        s = max(w, h)
        blot = cv2.resize(rng.standard_normal((max(2, h * 12 // s), max(2, w * 12 // s))).astype(np.float32),
                          (w, h), interpolation=cv2.INTER_CUBIC)
        grain = rng.standard_normal((h, w)).astype(np.float32)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        shade = 1 - 0.045 * np.clip(r - 0.35, 0, None) ** 2 + 0.006 * blot + 0.006 * grain
        _paper_cache[key] = (np.array(tone, np.float32)[None, None, :] * shade[..., None]).astype(np.float32)
    return _paper_cache[key].copy()


def solid(size, color):
    w, h = size
    return np.ones((h, w, 3), np.float32) * np.array(color, np.float32)


def background(size, bg):
    if bg == "paper":
        return paper(size)
    if bg == "ink":
        return paper(size, tone=INK)
    return solid(size, bg)


# ---------------------------------------------------------------- fonts

# First match wins. Drop Playfair Display / Libre Caslon / Inter / IBM Plex TTFs into fonts/ and they are used.
_SERIF = {
    "regular": ["PlayfairDisplay-Regular.ttf", "PlayfairDisplay[wght].ttf", "LibreCaslonText-Regular.ttf",
                "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "bold": ["PlayfairDisplay-Bold.ttf", "LibreCaslonText-Bold.ttf", "LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"],
    "italic": ["PlayfairDisplay-Italic.ttf", "PlayfairDisplay-Italic[wght].ttf", "LibreCaslonText-Italic.ttf",
               "LiberationSerif-Italic.ttf", "DejaVuSerif.ttf"],
}
_SANS = {
    "regular": ["Inter-Regular.ttf", "IBMPlexSans-Regular.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "bold": ["Inter-Bold.ttf", "IBMPlexSans-Bold.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
}
_SYSTEM_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
                "/usr/share/fonts/TTF", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]


def font_path(kind="serif", style="regular"):
    names = (_SERIF if kind == "serif" else _SANS)[style]
    for name in names:
        for d in [FONT_DIR] + _SYSTEM_DIRS:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    raise RuntimeError(f"no {kind} {style} font found; put TTFs in {FONT_DIR}")


_font_cache = {}


def font(kind="serif", size=40, style="regular"):
    size = max(6, int(round(size)))
    key = (kind, size, style)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(font_path(kind, style), size)
    return _font_cache[key]


def unit(size):
    """Layout unit: 1.0 at 1080 on the short side."""
    return min(size) / 1080


# ---------------------------------------------------------------- text and sprites

def text_sprite(text, fnt, color, tracking=0.0):
    """Render one line of text to an RGBA float sprite.
    Returns (sprite, ascent): the baseline sits `pad + ascent` px below the sprite's top."""
    asc, desc = fnt.getmetrics()
    pad = 2
    track = tracking * fnt.size
    width = sum(fnt.getlength(c) for c in text) + track * max(0, len(text) - 1) if track else fnt.getlength(text)
    im = Image.new("L", (int(math.ceil(width)) + 2 * pad + 2, asc + desc + 2 * pad), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for c in text:
            d.text((x, pad + asc), c, font=fnt, fill=255, anchor="ls")
            x += fnt.getlength(c) + track
    else:
        d.text((pad, pad + asc), text, font=fnt, fill=255, anchor="ls")
    a = np.asarray(im, np.float32) / 255
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = color
    spr[..., 3] = a
    return spr, pad + asc


def text_width(text, fnt, tracking=0.0):
    if not tracking:
        return fnt.getlength(text)
    return sum(fnt.getlength(c) for c in text) + tracking * fnt.size * max(0, len(text) - 1)


def wrap(text, fnt, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if line and fnt.getlength(trial) > max_w:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def paste(dst, spr, x, y, opacity=1.0):
    """Alpha-composite an RGBA sprite onto dst with its top-left at the (sub-pixel) point x, y."""
    if opacity <= 0:
        return dst
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    h, w = spr.shape[:2]
    pre = spr.copy()
    pre[..., :3] *= pre[..., 3:4]
    if fx > 1e-3 or fy > 1e-3:
        m = np.float32([[1, 0, fx], [0, 1, fy]])
        pre = cv2.warpAffine(pre, m, (w + 1, h + 1), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        h, w = h + 1, w + 1
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(ix, 0), max(iy, 0), min(ix + w, W), min(iy + h, H)
    if x1 <= x0 or y1 <= y0:
        return dst
    s = pre[y0 - iy:y1 - iy, x0 - ix:x1 - ix] * opacity
    region = dst[y0:y1, x0:x1]
    region *= (1 - s[..., 3:4])
    region += s[..., :3]
    return dst


def blend(dst, color, alpha):
    """dst = dst*(1-alpha) + color*alpha, alpha an (H, W) mask or a scalar."""
    a = alpha[..., None] if np.ndim(alpha) == 2 else alpha
    dst *= (1 - a)
    dst += np.asarray(color, np.float32) * a
    return dst


# ---------------------------------------------------------------- strokes (cv2, anti-aliased, sub-pixel)

SHIFT = 4  # cv2 fixed-point bits: coordinates are drawn to 1/16 px


def _fx(pts):
    return np.round(np.asarray(pts, np.float64) * (1 << SHIFT)).astype(np.int32)


def stroke_mask(shape, pts, width):
    """Anti-aliased polyline mask (float 0..1) through float points."""
    m = np.zeros(shape[:2], np.uint8)
    if len(pts) >= 2:
        cv2.polylines(m, [_fx(pts).reshape(-1, 1, 2)], False, 255, max(1, int(round(width))), cv2.LINE_AA, SHIFT)
    return m.astype(np.float32) / 255


def rect_mask(shape, x0, y0, x1, y1):
    """Filled rectangle with fractional (anti-aliased) edges."""
    h, w = shape[:2]
    xs = np.arange(w, dtype=np.float32) + 0.5
    ys = np.arange(h, dtype=np.float32) + 0.5
    cx = np.clip(np.minimum(xs - x0 + 0.5, x1 - xs + 0.5), 0, 1)
    cy = np.clip(np.minimum(ys - y0 + 0.5, y1 - ys + 0.5), 0, 1)
    return cy[:, None] * cx[None, :]


def partial(pts, p):
    """First fraction p (by arc length) of a polyline, with the last segment cut to the exact point."""
    pts = np.asarray(pts, np.float64)
    if p >= 1:
        return pts
    if p <= 0 or len(pts) < 2:
        return pts[:1]
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    target = p * cum[-1]
    i = int(np.searchsorted(cum, target, side="right")) - 1
    i = min(i, len(seg) - 1)
    f = (target - cum[i]) / seg[i] if seg[i] > 0 else 0
    return np.vstack([pts[:i + 1], pts[i] + f * (pts[i + 1] - pts[i])])


_grain_cache = {}


def pencil_grain(shape, seed=3):
    """Fixed grain texture used to break up pencil strokes."""
    key = (shape[:2], seed)
    if key not in _grain_cache:
        rng = np.random.default_rng(seed)
        g = rng.random(shape[:2]).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.7)
        _grain_cache[key] = np.clip(0.72 + 0.6 * (g - 0.5) * 2.2, 0.55, 1.0)
    return _grain_cache[key]


# ---------------------------------------------------------------- images and the camera

def load_rgb(image):
    """Path or PIL image -> float RGB array."""
    im = image if isinstance(image, Image.Image) else Image.open(image)
    return np.asarray(im.convert("RGB"), np.float32) / 255


def fit_plate(img, size, scale, bg="paper", margin=0.06, mode="auto"):
    """Lay an image onto a plate `scale` times the frame size.
    mode 'auto': fill the frame if the aspect is within 4%, otherwise fit it on the background with a soft shadow.
    Returns (plate, (ix, iy, iw, ih)) - the image's rectangle on the plate in plate pixels."""
    W, H = int(round(size[0] * scale)), int(round(size[1] * scale))
    ih, iw = img.shape[:2]
    if mode == "cover" or (mode == "auto" and abs((iw / ih) / (W / H) - 1) < 0.04):
        k = max(W / iw, H / ih)
        nw, nh = int(round(iw * k)), int(round(ih * k))
        big = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
        x, y = (nw - W) // 2, (nh - H) // 2
        return np.ascontiguousarray(big[y:y + H, x:x + W]), (-x, -y, nw, nh)
    plate = background((W, H), bg)
    m = margin * H
    k = min((W - 2 * m) / iw, (H - 2 * m) / ih)
    nw, nh = int(round(iw * k)), int(round(ih * k))
    x, y = (W - nw) // 2, (H - nh) // 2
    small = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    sh = np.zeros((H, W), np.float32)
    off = int(0.006 * H)
    sh[y + off:y + nh + off, x + off // 2:x + nw + off // 2] = 1
    sh = cv2.GaussianBlur(sh, (0, 0), 0.012 * H)
    blend(plate, (0, 0, 0), sh * 0.28)
    plate[y:y + nh, x:x + nw] = small
    return plate, (x, y, nw, nh)


def view_rect(plate_size, rect, cx, cy, zoom):
    """Camera view on the plate: centre given as a fraction of the image rect, zoom 1 = whole plate.
    Returns (left, top, width) in plate pixels, pushed inside the plate."""
    PW, PH = plate_size
    vw = PW / max(zoom, 1.0)
    vh = vw * PH / PW
    x, y, w, h = rect
    left = x + cx * w - vw / 2
    top = y + cy * h - vh / 2
    left = min(max(left, 0), PW - vw)
    top = min(max(top, 0), PH - vh)
    return left, top, vw


def camera_matrix(view, out_size):
    """Affine taking plate pixels to output pixels for a view (left, top, width)."""
    left, top, vw = view
    k = out_size[0] / vw
    return np.float32([[k, 0, -left * k], [0, k, -top * k]])


def render_view(plate, view, out_size, ss=2):
    """Sample the view from the plate: warp at ss x the output size with bilinear filtering, then area-downsample.
    Sub-pixel accurate and free of stair-step jitter."""
    W, H = out_size
    m = camera_matrix(view, (W * ss, H * ss))
    big = cv2.warpAffine(plate, m, (W * ss, H * ss), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA) if ss > 1 else big


def apply_affine(m, pts):
    pts = np.asarray(pts, np.float64)
    return pts @ np.asarray(m, np.float64)[:, :2].T + np.asarray(m, np.float64)[:, 2]
