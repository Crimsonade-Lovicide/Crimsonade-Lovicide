"""Fly-throughs of real places rendered from open LiDAR data. Every point is a laser measurement; no AI.

The input is a 1 m surface model (highest return per square metre) plus the laser intensity image, e.g. the
Environment Agency's open data for England. Each cell becomes a point at its measured height; the vertical
sides of buildings get extra points so they read as solid, while thin raised features (a stadium arch, a
bridge) are left as floating points rather than turned into walls. Points are shaded by intensity and slope,
hazed toward the paper colour with distance, and splatted through a z-buffer.
"""
import math

import numpy as np

from .core import FPS, HD, PAPER, Writer, ease, even, frame_times


def load_scene(npz, center, radius=1100.0, near_full=650.0, wall_step=1.5, thin_mask=None):
    """Build the point set around center=(easting, northing) from a wembley_lidar.npz-style file.
    Cells within near_full metres keep 1 m spacing; beyond that every second cell (2 m) is kept."""
    z = np.load(npz)
    dsm, inten, (e0, n0) = z["dsm"], z["intensity"].astype(np.float32) / 255.0, z["origin"]
    H, W = dsm.shape
    cx, cy = center
    c0, c1 = int(max(0, cx - radius - e0)), int(min(W, cx + radius - e0))
    r0, r1 = int(max(0, n0 - (cy + radius))), int(min(H, n0 - (cy - radius)))
    d = dsm[r0:r1, c0:c1].astype(np.float32)
    it = inten[r0:r1, c0:c1]
    d = np.where(np.isnan(d), np.nanmin(d), d)
    rows, cols = np.mgrid[r0:r1, c0:c1]
    E = (e0 + cols).astype(np.float32)
    N = (n0 - rows).astype(np.float32)
    gy, gx = np.gradient(d)
    slope_shade = np.clip(0.62 - 0.22 * gx + 0.22 * gy, 0.25, 1.0)        # light from the north-west
    albedo = np.clip(0.35 + 0.75 * it, 0, 1) * slope_shade
    dist = np.hypot(E - cx, N - cy)
    keep = (dist <= radius) & ((dist <= near_full) | ((rows % 2 == 0) & (cols % 2 == 0)))
    thin = thin_mask(E, N, d) if thin_mask else np.zeros_like(keep)
    pts = [np.stack([E[keep], N[keep], d[keep], albedo[keep]], 1)]
    # walls: where a cell stands above its lower 4-neighbour by > 2 m, add points down the face
    low = np.minimum.reduce([np.roll(d, 1, 0), np.roll(d, -1, 0), np.roll(d, 1, 1), np.roll(d, -1, 1)])
    drop = d - low
    wall = keep & (drop > 2.0) & ~thin & (dist <= near_full * 1.3)
    if wall.any():
        we, wn, wt, wl, wa = E[wall], N[wall], d[wall], low[wall], albedo[wall] * 0.55
        steps = np.ceil((wt - wl) / wall_step).astype(int).clip(1, 60)
        rep = np.repeat(np.arange(len(we)), steps)
        k = np.concatenate([np.arange(s) for s in steps]) + 1
        zz = wt[rep] - k * wall_step
        ok = zz > wl[rep]
        pts.append(np.stack([we[rep][ok], wn[rep][ok], zz[ok], wa[rep][ok]], 1))
    return np.concatenate(pts).astype(np.float32)


def _look(cam, target):
    f = np.asarray(target, np.float64) - np.asarray(cam, np.float64)
    f /= np.linalg.norm(f)
    if abs(f[2]) > 0.995:                     # looking (nearly) straight down: keep north at the top
        r = np.array([1.0, 0.0, 0.0])
        u = np.cross(r, f)
        u = u if u[1] > 0 else -u
        r = np.cross(f, u)
        return f, r, u
    r = np.cross(f, [0.0, 0.0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u


def render(points, cam, target, size=HD, fov=50.0, haze=2600.0, center=None, radius=None):
    """One frame: perspective projection, z-buffered point splats (bigger when close), distance haze,
    a fade towards the edge of the loaded data, and a small hole-fill so neighbouring points close up."""
    w, h = size
    f, r, u = _look(cam, target)
    rel = points[:, :3] - np.asarray(cam, np.float32)
    zc = rel @ f.astype(np.float32)
    front = zc > 5
    pts, rel, zc = points[front], rel[front], zc[front]
    focal = (w / 2) / math.tan(math.radians(fov) / 2)
    x = (rel @ r.astype(np.float32)) / zc * focal + w / 2
    y = -(rel @ u.astype(np.float32)) / zc * focal + h / 2
    on = (x > -4) & (x < w + 4) & (y > -4) & (y < h + 4)
    pts, x, y, zc = pts[on], x[on], y[on], zc[on]
    alb = pts[:, 3]
    fog = 1 - np.exp(-zc / haze)
    if center is not None and radius is not None:
        edge = np.hypot(pts[:, 0] - center[0], pts[:, 1] - center[1]) / radius
        fog = np.maximum(fog, np.clip((edge - 0.7) / 0.3, 0, 1))
    paper = np.asarray(PAPER, np.float32)
    dark = np.asarray([0.08, 0.08, 0.08], np.float32)
    light = np.asarray([0.95, 0.93, 0.89], np.float32)
    tone = np.clip((alb - 0.18) / 0.72, 0, 1) ** 0.9                # stretch contrast
    col = dark + (light - dark) * tone[:, None]
    col = col * (1 - fog[:, None]) + paper * fog[:, None]
    rad = np.clip(focal * 1.6 / zc, 1, 5).astype(np.int32)          # 1 m cells cover this many pixels
    order = np.argsort(-zc, kind="stable")                           # far first; near points overwrite
    xi, yi, col, rad = x[order].astype(np.int32), y[order].astype(np.int32), col[order], rad[order]
    img = np.empty((h, w, 3), np.float32)
    img[:] = paper * np.linspace(0.96, 1.0, h, dtype=np.float32)[:, None, None]
    hit = np.zeros(h * w, bool)
    flat = img.reshape(-1, 3)
    for dx in range(5):
        for dy in range(5):
            sel = (rad > max(dx, dy))
            if not sel.any():
                continue
            xx, yy = xi[sel] + dx, yi[sel] + dy
            ok = (xx >= 0) & (xx < w) & (yy >= 0) & (yy < h)
            idx = yy[ok] * w + xx[ok]
            flat[idx] = col[sel][ok]
            hit[idx] = True
    # hole-fill: an unhit pixel with hit neighbours on both sides takes their average (two passes)
    hit = hit.reshape(h, w)
    for _ in range(2):
        for ax in (0, 1):
            a, b = np.roll(img, 1, ax), np.roll(img, -1, ax)
            ha, hb = np.roll(hit, 1, ax), np.roll(hit, -1, ax)
            fill = ~hit & ha & hb
            img[fill] = (a[fill] + b[fill]) / 2
            hit = hit | fill
    return img


def flyover(points, out, duration, path, size=HD, fov=50.0, haze=2600.0, center=None, radius=None, fps=FPS):
    """path(t in 0..1) -> (camera (E, N, Z), target (E, N, Z)). Writes an mp4."""
    size = even(size)
    times = frame_times(duration, fps)
    n = len(times)
    with Writer(out, size, fps) as w:
        for i in range(n):
            cam, tgt = path(i / (n - 1) if n > 1 else 0.0)
            w.write(render(points, cam, tgt, size, fov, haze, center, radius))
    return out


def lerp3(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def eased(t):
    return ease(t)
