"""Assemble a 60s pilot: base footage per segment -> overlays (captions, data, labels) -> grade -> encode -> mix audio.
usage: python3 compose.py p1_pink_slime [--preview SECONDS...]"""
import json, math, os, subprocess, sys, textwrap
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pilots import PILOTS

SCR = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
TL = json.load(open(f'{SCR}/timeline.json'))
FONT = {k: f'{SCR}/fonts/{v}' for k, v in
        dict(bebas='BebasNeue.ttf', mono='PlexMono.ttf', monob='PlexMonoSemi.ttf', inter='Inter.ttf').items()}
BLENDER_ID = {'p1_pink_slime': 'B1', 'p2_the_count': 'B2', 'p3_server_nation': 'B3', 'p4_long_arm': 'B4', 'p5_brokered': 'B5'}
HOOKS = {
    'p1_pink_slime': 'Who wrote the last local story you read?',
    'p2_the_count': 'Who counts your vote?',
    'p3_server_nation': 'Can a group chat choose a prime minister?',
    'p4_long_arm': 'How far is far enough?',
    'p5_brokered': 'Where were you last Tuesday?',
}
WHITE, GREY, DIM = (240, 240, 236), (175, 178, 185), (140, 142, 150)


# ---------------------------------------------------------------- text helpers
@lru_cache(maxsize=None)
def font(name, size):
    f = ImageFont.truetype(FONT[name], size)
    if name == 'inter':
        f.set_variation_by_name('Medium')
    return f


@lru_cache(maxsize=4096)
def text_img(text, fname, size, color, track=0, shadow=True):
    f = font(fname, size)
    if track:
        widths = [f.getlength(ch) + track for ch in text]; tw = int(sum(widths))
    else:
        tw = int(f.getlength(text))
    asc, desc = f.getmetrics(); th = asc + desc
    pad = 16
    im = Image.new('RGBA', (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    def draw(img, fill, off=(0, 0)):
        d = ImageDraw.Draw(img); x = pad + off[0]
        if track:
            for ch, w in zip(text, widths): d.text((x, pad + off[1]), ch, font=f, fill=fill); x += w
        else:
            d.text((x, pad + off[1]), text, font=f, fill=fill)
    if shadow:
        from PIL import ImageFilter
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); draw(sh, (0, 0, 0, 200), (0, 2))
        sh = sh.filter(ImageFilter.GaussianBlur(5)); im = Image.alpha_composite(im, sh)
    draw(im, (*color, 255))
    return im, pad


def put(canvas, text, fname, size, color, xy, anchor='l', alpha=1.0, track=0, shadow=True):
    if alpha <= 0.01 or not text: return
    im, pad = text_img(text, fname, size, tuple(color), track, shadow)
    if alpha < 0.99:
        im = im.copy(); a = im.getchannel('A').point(lambda v: int(v * alpha)); im.putalpha(a)
    x, y = xy
    w = im.width - 2 * pad
    if anchor == 'c': x -= w / 2
    elif anchor == 'r': x -= w
    canvas.alpha_composite(im, (int(x - pad), int(y - pad)))


def rect(canvas, box, color, alpha):
    if alpha <= 0.01: return
    ov = Image.new('RGBA', (int(box[2] - box[0]), int(box[3] - box[1])), (*color, int(255 * alpha)))
    canvas.alpha_composite(ov, (int(box[0]), int(box[1])))


def fade(t, a, b, fi=0.35, fo=0.35):
    if t < a or t > b: return 0.0
    return max(0.0, min(1.0, (t - a) / fi if fi else 1, (b - t) / fo if fo else 1))


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def fmt(n): return f'{int(round(n)):,}'


# ---------------------------------------------------------------- base footage
def seg_frames(segs):
    out, acc = [], 0.0
    for s in segs:
        a = round(acc * FPS); acc += s['dur']; out.append(round(acc * FPS) - a)
    return out


def make_base(pid, vis, nframes, path):
    dur = nframes / FPS
    if os.path.exists(path): return
    if vis.startswith('K'):
        src = f'{SCR}/hf/{vis}.mp4'; srcdur = 5.04
        f = dur / srcdur
        vf = f'setpts={f:.4f}*PTS,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,' if f > 1.03 else ''
        vf += 'scale=1920:1080:flags=lanczos,fps=24'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', vf]
    else:  # Blender render, 12 fps -> 24 fps + glow
        bid = BLENDER_ID[pid]
        vf = ('minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1920:1080:flags=lanczos,format=gbrp,'
              'split[a][b];[b]curves=all=0/0 0.55/0 1/1,gblur=sigma=22[g];[a][g]blend=all_mode=screen:all_opacity=0.85,format=yuv420p')
        cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', '12', '-pattern_type', 'glob', '-i', f'{SCR}/renders/{bid}/*.png',
               '-filter_complex', vf]
    cmd += ['-frames:v', str(nframes), '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', path]
    subprocess.run(cmd, check=True)
    # pad if the source ran short (hold last frame)
    got = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries',
                              'stream=nb_read_frames', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip() or 0)
    if got < nframes:
        tmp = path + '.tmp.mp4'; os.rename(path, tmp)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-vf', f'tpad=stop_mode=clone:stop={nframes - got}',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', path], check=True)
        os.remove(tmp)


def reader(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1)
    p.wait()


# ---------------------------------------------------------------- captions
def build_captions(pid):
    caps = []
    vo = TL[pid]['vo']; timing = json.load(open(f'{SCR}/audio/timing.json'))[pid]
    for (vis, text), v, tm in zip(PILOTS[pid]['lines'], vo, timing):
        chunks = textwrap.wrap(text, 46)
        total = sum(len(c) for c in chunks); t = v['start']
        for c in chunks:
            d = tm['dur'] * len(c) / total
            caps.append((t, t + d + 0.05, c)); t += d
    return caps


def draw_caption(cv, caps, t):
    for a, b, c in caps:
        if a <= t < b:
            f = font('inter', 40); w = f.getlength(c)
            rect(cv, (W / 2 - w / 2 - 22, 958, W / 2 + w / 2 + 22, 1022), (0, 0, 0), 0.55)
            put(cv, c, 'inter', 40, WHITE, (W / 2, 963), 'c', shadow=False)


# ---------------------------------------------------------------- per-pilot data overlays (ts = seconds into B segment)
def tracks(bid):
    p = f'{SCR}/renders/{bid}_tracks.json'
    return json.load(open(p)) if os.path.exists(p) else {}


def track_xy(tr, frame, key):
    row = tr.get(str(max(1, min(frame, len(tr))))) if tr else None
    if not row or key not in row: return None
    x, y, z = row[key]
    if z <= 0 or not (-0.05 < x < 1.05 and -0.05 < y < 1.05): return None
    return x * W, y * H


def stat_block(cv, x, y, big, label_lines, accent, alpha, big_size=200, big_color=None):
    put(cv, big, 'bebas', big_size, big_color or accent, (x, y), alpha=alpha)
    yy = y + big_size * 0.98
    for ln in label_lines:
        put(cv, ln, 'mono', 28, WHITE, (x + 6, yy), alpha=alpha); yy += 40


def source_tag(cv, text, alpha=1.0):
    put(cv, 'SOURCE  ' + text.upper(), 'mono', 20, GREY, (64, 112), alpha=alpha)


def overlay_B(pid, cv, ts, frame, tr, accent):
    seg_dur = [s['dur'] for s in TL[pid]['segs'] if s['vis'].startswith('B')][0]
    a_all = fade(ts, 0, seg_dur, 0.4, 0.3)
    if pid == 'p1_pink_slime':
        def landed(n, first=14, rate=2): return max(0, min(n, (frame - first) // rate + 1))
        lw, lp = landed(121), landed(127)
        for key, n, total, label, col in (('white_top', lw, 1213, 'DAILY NEWSPAPERS', WHITE), ('pink_top', lp, 1265, 'PINK SLIME SITES', accent)):
            xy = track_xy(tr, frame, key)
            if xy and n > 0:
                x, y = xy; y = max(150, y - 170)
                put(cv, fmt(total * n / (121 if total == 1213 else 127)), 'bebas', 104, col, (x, y), 'c', a_all)
                put(cv, label, 'monob', 22, col, (x, y + 104), 'c', a_all)
        source_tag(cv, 'NewsGuard, June 2024  ·  1 slab = 10 outlets', a_all)
    elif pid == 'p2_the_count':
        a1 = fade(ts, 0.5, 11.2)
        stat_block(cv, 110, 300, '38%', ['OF LOCAL ELECTION OFFICIALS', 'THREATENED, HARASSED OR ABUSED', 'BECAUSE OF THEIR JOB'], accent, a1, 260)
        if ts >= 12.2:
            n = max(0, min(38, math.floor((ts - 12.4) / 3.0 * 38) + 1))
            a2 = fade(ts, 12.2, seg_dur, 0.3, 0.3)
            put(cv, f'{n} OF 100', 'bebas', 150, accent, (110, 250), alpha=a2)
            put(cv, 'SEATS', 'mono', 28, WHITE, (116, 400), alpha=a2)
        source_tag(cv, 'Brennan Center for Justice, 2025 survey of local election officials', a_all)
    elif pid == 'p3_server_nation':
        a1 = fade(ts, 0.4, 8.7)
        put(cv, 'DISCORD SERVER  ·  "YOUTH AGAINST CORRUPTION"', 'monob', 26, accent, (110, 250), alpha=a1)
        stat_block(cv, 104, 290, '130,000+', ['MEMBERS'], WHITE, a1, 170)
        a2 = fade(ts, 9.0, 15.8)
        n = 7713 * ease((ts - 9.0) / 2.6)
        put(cv, 'POLL FOR INTERIM PRIME MINISTER', 'monob', 26, accent, (110, 250), alpha=a2)
        stat_block(cv, 104, 290, fmt(n), ['VOTES CAST'], WHITE, a2, 190)
        put(cv, 'TOP CHOICE: SUSHILA KARKI  ·  3,833 VOTES (50%)', 'mono', 28, WHITE, (110, 560), alpha=a2 * fade(ts, 11.6, 15.8))
        a3 = fade(ts, 16.0, seg_dur, 0.4, 0.3)
        put(cv, 'SEPTEMBER 12, 2025', 'monob', 26, accent, (110, 250), alpha=a3)
        stat_block(cv, 104, 290, 'SWORN IN', ['FIRST WOMAN TO LEAD NEPAL\'S GOVERNMENT', 'FORMER CHIEF JUSTICE, AGE 73'], WHITE, a3, 170)
        put(cv, 'VISUALIZATION  ·  275 SEATS = NEPAL HOUSE OF REPRESENTATIVES', 'mono', 20, GREY, (64, 146), alpha=a_all)
        source_tag(cv, 'Kathmandu Post · Al Jazeera · Outlook India', a_all)
    elif pid == 'p4_long_arm':
        a1 = fade(ts, 0.4, 13.4)
        stat_block(cv, 110, 280, fmt(126 * ease((ts - 0.6) / 10.4)), ['NEW PHYSICAL INCIDENTS OF', 'TRANSNATIONAL REPRESSION, 2025'], accent, a1, 230)
        a2 = fade(ts, 13.7, seg_dur, 0.4, 0.3)
        stat_block(cv, 110, 280, '54+', ['GOVERNMENTS HAVE TARGETED', 'CRITICS ABROAD SINCE 2014'], accent, a2, 230)
        for i, (key, name) in enumerate((('Beijing', 'CHINA'), ('Hanoi', 'VIETNAM'), ('Moscow', 'RUSSIA'))):
            xy = track_xy(tr, frame, key)
            al = fade(ts, 14.6 + i * 0.42, seg_dur, 0.3, 0.3)
            if xy: put(cv, name, 'monob', 26, WHITE, (xy[0] + 26, xy[1] - 16), alpha=al)
        put(cv, 'ROUTES ARE ILLUSTRATIVE, NOT INDIVIDUAL CASES', 'mono', 20, GREY, (64, 146), alpha=a_all)
        source_tag(cv, 'Freedom House, Tracking Transnational Repression in 2025', a_all)
    elif pid == 'p5_brokered':
        stops = (('home', 0.4, 'HOME  ·  7:12 AM'), ('church', 4.6, 'PLACE OF WORSHIP  ·  9:05 AM'),
                 ('clinic', 8.2, 'CLINIC  ·  2:30 PM'), ('plaza', 11.6, 'PROTEST  ·  6:15 PM'))
        for key, t0, label in stops:
            xy = track_xy(tr, frame, key)
            if xy and ts >= t0:
                k = int(len(label) * ease((ts - t0) / 0.9))
                al = fade(ts, t0, 13.6, 0.2, 0.5)
                put(cv, label[:k], 'monob', 24, (255, 90, 80), (xy[0] + 24, xy[1] - 44), alpha=al)
        a1 = fade(ts, 4.0, 12.6)
        put(cv, '17,000,000,000', 'bebas', 120, WHITE, (110, 600), alpha=a1)
        put(cv, 'LOCATION SIGNALS A DAY  ·  ~1 BILLION PHONES', 'mono', 26, WHITE, (116, 722), alpha=a1)
        put(cv, 'FTC ALLEGATION  ·  GRAVY ANALYTICS / VENNTEL', 'mono', 20, GREY, (116, 760), alpha=a1)
        a2 = fade(ts, 14.0, seg_dur, 0.4, 0.3)
        put(cv, 'PROTESTERS PROFILED', 'bebas', 120, accent, (110, 560), alpha=a2)
        put(cv, 'BY RACE AND BY WHERE THEY LIVE', 'mono', 28, WHITE, (116, 682), alpha=a2)
        put(cv, 'FTC ALLEGATION  ·  MOBILEWALLA  ·  2020 GEORGE FLOYD PROTESTS', 'mono', 20, GREY, (116, 722), alpha=a2)
        put(cv, 'SIMULATION  ·  HYPOTHETICAL PERSON', 'mono', 20, GREY, (64, 146), alpha=a_all)
        source_tag(cv, 'U.S. Federal Trade Commission, December 2024', a_all)


# ---------------------------------------------------------------- full-frame cards
@lru_cache(maxsize=8)
def keyart(pid):
    im = Image.open(f'{SCR}/hf/A{PILOTS[pid]["keyart"]}.png').convert('RGB')
    s = max(W * 1.12 / im.width, H * 1.12 / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    grad = np.linspace(0.92, 0.0, W // 2 + 200).clip(0, 1)
    shade = np.zeros((H, W)); shade[:, :len(grad)] = grad[None, :] if len(grad) <= W else grad[None, :W]
    return im, shade


def card_T(pid, ts, dur):
    im, shade = keyart(pid)
    z = 1.0 + 0.07 * ts / dur
    cw, ch = W * 1.1 / z, H * 1.1 / z
    cx, cy = im.width / 2 + 20 * ts / dur, im.height / 2
    fr = im.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC)
    arr = np.asarray(fr).astype(np.float32) * (1 - shade[..., None] * 0.85)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def overlay_T(pid, cv, ts, dur, accent):
    p = PILOTS[pid]
    a0 = fade(ts, 0.2, dur, 0.6, 0.5)
    put(cv, 'A DOCUMENTARY SERIES', 'monob', 26, accent, (126, 300), alpha=a0, track=6)
    a1 = fade(ts, 0.45, dur, 0.7, 0.5)
    tr = int(30 * (1 - ease((ts - 0.45) / 1.6)))
    rect(cv, (110, 352, 118, 352 + 190), accent, a1)
    put(cv, p['series'], 'bebas', 210, WHITE, (140, 340), alpha=a1, track=4 + tr)
    put(cv, p['tagline'], 'mono', 32, WHITE, (144, 562), alpha=fade(ts, 1.0, dur, 0.7, 0.5))


def card_END(pid, ts, dur, accent):
    p = PILOTS[pid]
    cv = Image.new('RGBA', (W, H), (6, 6, 8, 255))
    a = fade(ts, 0.15, dur, 0.5, 0.6)
    put(cv, p['series'], 'bebas', 150, WHITE, (W / 2, 300), 'c', a, track=6)
    put(cv, 'PILOT  ·  ' + p['episode'].upper(), 'monob', 28, accent, (W / 2, 470), 'c', a)
    put(cv, 'SOURCES: ' + p['sources'], 'mono', 22, GREY, (W / 2, 590), 'c', a)
    put(cv, 'Narration is a synthetic placeholder voice. Shots labeled AI are generated illustrations, not footage of real events.',
        'mono', 19, DIM, (W / 2, 660), 'c', a)
    put(cv, 'Data visualizations built in Blender from the cited sources.', 'mono', 19, DIM, (W / 2, 692), 'c', a)
    return cv


def card_HOOK(pid, ts, dur, accent):
    cv = Image.new('RGBA', (W, H), (4, 4, 6, 255))
    q = HOOKS[pid]; k = int(len(q) * ease(ts / 1.5))
    a = fade(ts, 0, dur, 0.01, 0.35)
    f = font('mono', 58); w = f.getlength(q)
    put(cv, q[:k], 'mono', 58, WHITE, (W / 2 - w / 2, H / 2 - 40), alpha=a)
    if int(ts * 2.5) % 2 == 0 or k < len(q):
        cx = W / 2 - w / 2 + f.getlength(q[:k]) + 6
        rect(cv, (cx, H / 2 - 30, cx + 26, H / 2 + 36), accent, a)
    return cv


# ---------------------------------------------------------------- grade
def grade_tools():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = (1 - 0.38 * np.clip(r - 0.45, 0, 1) ** 1.6).astype(np.float32)
    rng = np.random.default_rng(1)
    grains = [rng.normal(0, 5.0, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
    return vig, grains


def grade(img, vig, grain):
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    g = np.repeat(np.repeat(grain, 2, 0), 2, 1)
    a = a * vig[..., None] + g[..., None]
    return a.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- main
def compose(pid, preview=None):
    p = PILOTS[pid]; accent = tuple(p['accent']); segs = TL[pid]['segs']
    nfr = seg_frames(segs); os.makedirs(f'{SCR}/out/{pid}', exist_ok=True)
    for i, (s, n) in enumerate(zip(segs, nfr)):
        if s['vis'].startswith('B') and preview and not os.path.isdir(f'{SCR}/renders/{BLENDER_ID[pid]}'):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0x101014:s={W}x{H}:r={FPS}', '-frames:v', str(n),
                            '-pix_fmt', 'yuv420p', f'{SCR}/out/{pid}/seg{i:02d}_{s["vis"]}.mp4'], check=True); continue
        if s['vis'].startswith(('K', 'B')):
            make_base(pid, s['vis'], n, f'{SCR}/out/{pid}/seg{i:02d}_{s["vis"]}.mp4')
    caps = build_captions(pid); vig, grains = grade_tools()
    bid = BLENDER_ID[pid]; tr = tracks(bid)
    silent = f'{SCR}/out/{pid}/video_silent.mp4'
    enc = None
    if not preview:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', silent],
                               stdin=subprocess.PIPE)
    gidx = 0
    for i, (s, n) in enumerate(zip(segs, nfr)):
        vis = s['vis']; dur = n / FPS
        src = reader(f'{SCR}/out/{pid}/seg{i:02d}_{vis}.mp4') if vis.startswith(('K', 'B')) else None
        for j in range(n):
            t = gidx / FPS; ts = j / FPS; gidx += 1
            base = next(src) if src else None
            if preview and not any(abs(t - pt) < 0.5 / FPS for pt in preview): continue
            if vis == 'HOOK': cv = card_HOOK(pid, ts, dur, accent)
            elif vis == 'END': cv = card_END(pid, ts, dur, accent)
            elif vis == 'T':
                cv = card_T(pid, ts, dur).convert('RGBA'); overlay_T(pid, cv, ts, dur, accent)
                put(cv, 'AI-GENERATED ILLUSTRATION', 'monob', 22, WHITE, (W - 64, 56), 'r', 0.75)
            else:
                cv = base.convert('RGBA')
                if s.get('fade_in') or (i > 0 and segs[i - 1]['vis'] == 'HOOK' and ts < 0.5):
                    cv = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), cv, ts / 0.5)
                put(cv, p['series'], 'bebas', 40, WHITE, (64, 52), alpha=0.85, track=3)
                if vis.startswith('K'):
                    put(cv, 'AI-GENERATED ILLUSTRATION', 'monob', 22, WHITE, (W - 64, 56), 'r', 0.75)
                else:
                    put(cv, 'DATA VISUALIZATION', 'monob', 22, WHITE, (W - 64, 56), 'r', 0.75)
                    overlay_B(pid, cv, ts, j + 1, tr, accent)
            if vis not in ('HOOK', 'END'): draw_caption(cv, caps, t)
            out = grade(cv, vig, grains[gidx % len(grains)])
            if preview:
                Image.fromarray(out).save(f'{SCR}/out/{pid}/preview_{t:05.2f}.jpg', quality=88)
            else:
                enc.stdin.write(out.tobytes())
        if src:
            for _ in src: pass
    if enc:
        enc.stdin.close(); enc.wait(); mix(pid, silent)


def mix(pid, silent):
    vo = TL[pid]['vo']; final = f'{SCR}/out/{pid}.mp4'
    inputs = ['-i', silent, '-i', f'{SCR}/audio/{pid}_music.wav']
    for v in vo: inputs += ['-i', f'{SCR}/{v["wav"]}']
    parts = []
    for k, v in enumerate(vo):
        d = int(v['start'] * 1000)
        parts.append(f'[{k + 2}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={d}|{d},volume=1.0[v{k}]')
    vo_labels = ''.join(f'[v{k}]' for k in range(len(vo)))
    fc = ';'.join(parts) + f';{vo_labels}amix=inputs={len(vo)}:normalize=0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,' \
        f'asplit=2[vo][sc];' \
        f'[1:a]volume=0.9[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[duck];' \
        f'[vo][duck]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=9[aout]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '0:v', '-map', '[aout]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', final], check=True)
    print('wrote', final)


if __name__ == '__main__':
    pid = sys.argv[1]
    pv = [float(x) for x in sys.argv[3:]] if len(sys.argv) > 2 and sys.argv[2] == '--preview' else None
    compose(pid, pv)
