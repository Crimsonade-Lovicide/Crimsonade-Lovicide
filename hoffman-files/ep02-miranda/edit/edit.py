"""Assemble The Hoffman Files ep. 2 (Miranda) story reel from episode.py. Same assembler as ep. 1, plus a `hold`
segment kind (black, silent) and the final music path built in.

  python3 edit.py plates            build 1080p/24 fps plates from the Blender frames
  python3 edit.py timeline          print the timeline (also writes out/timeline.json, shotlist.csv, captions.srt)
  python3 edit.py still s11 4.5     render one frame of a segment to out/stills/
  python3 edit.py segs [ids...]     render segment clips to out/segs/ (clean: no temp-VO tag)
  python3 edit.py reel              concatenate, score (theme + public domain acts), mix to -14 LUFS
                                    -> out/hoffman_ep02_story_reel.mp4
  python3 edit.py lowerthirds       ProRes 4444 (alpha) name straps for the editor
Environment: RENDERS (Blender frames dir, default ../renders), PREVIEW=1 to build plates from renders/preview,
MUSIC_DIR (default ../../music).
"""
import csv, json, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gfx2 as gfx
from episode import SEGMENTS, GUESTS, HOST, INTERVIEW_SLATE

W, H, FPS = gfx.W, gfx.H, gfx.FPS
RENDERS = os.environ.get('RENDERS', os.path.join(HERE, '..', 'renders'))
OUT = os.path.join(HERE, 'out')
LEAD, TAIL, SENT_GAP = 0.45, 0.8, 0.28
MUSIC_DIR = os.environ.get('MUSIC_DIR', os.path.join(HERE, '..', '..', 'music'))
TIMING = json.load(open(os.path.join(HERE, 'audio', 'timing.json')))


# ---------------------------------------------------------------- timing
def phrase_time(seg, phrase):
    """Estimated time (s, from segment start) when `phrase` is spoken: character position, corrected for the
    fixed pause the voice puts between sentences."""
    vo = seg['vo']; i = vo.find(phrase)
    if i < 0: raise ValueError(f'{seg["id"]}: cue phrase not in VO: {phrase!r}')
    n_sent = sum(vo.count(p) for p in ('. ', '? ', ': ')); before = sum(vo[:i].count(p) for p in ('. ', '? ', ': '))
    speech = TIMING[seg['id']] - n_sent * SENT_GAP
    chars = len(vo) - n_sent * 2
    return LEAD + speech * (i - before * 2) / chars + before * SENT_GAP


def timeline():
    t, out = 0.0, []
    for s in SEGMENTS:
        vo = TIMING.get(s['id'], 0.0)
        if s['kind'] == 'interview': dur = INTERVIEW_SLATE
        elif s['kind'] == 'hold': dur = s['min']
        elif vo: dur = max(s.get('min', 0), LEAD + vo + s.get('tail', TAIL if s['kind'] != 'aroll' else 0.5))
        else: dur = s.get('min', 4.0)
        dur = round(dur * FPS) / FPS
        cues = [phrase_time(s, p) for p in s.get('cues', [])]
        if s['kind'] == 'blender':
            cues = [phrase_time(s, p) for p in gfx.OVERLAY_CUES.get(s.get('overlay'), [])]
        out.append(dict(seg=s, start=round(t, 3), dur=dur, vo=vo, cues=cues)); t += dur
    return out


def time_map(e):
    """Segment time -> source frame for a 3D plate, through the `at` anchors."""
    s = e['seg']; f0, f1 = s['frames']
    xs, ys = [0.0], [f0]
    for phrase, fr in s.get('at', []):
        tt = phrase_time(s, phrase)
        if tt > xs[-1] and fr >= ys[-1]: xs.append(tt); ys.append(fr)
    if e['dur'] > xs[-1]: xs.append(e['dur']); ys.append(max(f1, ys[-1]))
    return lambda tt: int(round(np.interp(tt, xs, ys)))


# ---------------------------------------------------------------- plates
def build_plates(only=None):
    os.makedirs(os.path.join(OUT, 'plates'), exist_ok=True)
    src_root = os.path.join(RENDERS, 'preview') if os.environ.get('PREVIEW') else RENDERS
    for sc in sorted({s['src'] for s in SEGMENTS if s['kind'] == 'blender'}):
        if only and sc not in only: continue
        d = os.path.join(src_root, sc); files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
        nums = [int(f[:4]) for f in files]
        step = 2 if len(nums) > 1 and nums[1] - nums[0] == 2 else 1
        vf = 'scale=1920:1080:flags=lanczos,unsharp=5:5:0.4'
        if step == 2: vf = 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,' + vf
        dst = os.path.join(OUT, 'plates', f'{sc}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(24 // step), '-pattern_type', 'glob', '-i',
                        os.path.join(d, '*.png'), '-vf', vf, '-r', '24', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium',
                        '-pix_fmt', 'yuv420p', dst], check=True)
        print('plate', sc, 'step', step, 'frames', len(files))


class Plate:
    """Sequential reader: plate index i holds source frame i + 1. Requests must not go backwards."""
    def __init__(self, sc):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', os.path.join(OUT, 'plates', f'{sc}.mp4'), '-f', 'rawvideo',
                                   '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.i, self.cur = 0, None

    def get(self, frame):
        want = max(1, frame)
        while self.i < want:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break                     # past the end: hold the last frame
            self.cur = b; self.i += 1
        return Image.frombuffer('RGB', (W, H), self.cur, 'raw', 'RGB', 0, 1).convert('RGBA')

    def close(self):
        self.p.stdout.close(); self.p.kill()


def tracks(sc):
    p = os.path.join(RENDERS, f'{sc}_tracks.json')
    return json.load(open(p)) if os.path.exists(p) else {}


# ---------------------------------------------------------------- grade
_VIG = None; _GRAIN = None


def grade(img, k):
    global _VIG, _GRAIN
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.32 * np.clip(r - 0.5, 0, 1) ** 1.6).astype(np.float32)[..., None]
        rng = np.random.default_rng(7)
        _GRAIN = [np.repeat(np.repeat(rng.normal(0, 3.2, (H // 2, W // 2)).astype(np.float32), 2, 0), 2, 1)[..., None]
                  for _ in range(4)]
    a = np.asarray(img.convert('RGB'), dtype=np.float32) * _VIG + _GRAIN[k % 4]
    return a.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- frames
def frame_at(e, t, k, plate=None, tr=None, tmap=None):
    s = e['seg']
    if s['kind'] == 'gfx':
        return gfx.CARDS[s['gfx']](t, e['dur'], e['cues'])
    if s['kind'] == 'blender':
        fr = tmap(t); cv = plate.get(fr)
        ov = gfx.OVERLAYS.get(s.get('overlay'))
        if ov: ov(cv, t, e['dur'], fr, tr, e['cues'])
        gfx.bug(cv, 0.45)
        return cv
    if s['kind'] == 'hold':
        return gfx.black(t, e['dur'], [])
    if s['kind'] == 'aroll':
        return gfx.slate_aroll(s)
    return gfx.slate_interview(s, GUESTS, s['plan'])


def render_seg(e):
    s = e['seg']; os.makedirs(os.path.join(OUT, 'segs'), exist_ok=True)
    dst = os.path.join(OUT, 'segs', f"{s['id']}.mp4"); n = round(e['dur'] * FPS)
    if s['kind'] in ('aroll', 'interview', 'hold'):                  # static slate: one frame, looped
        im = frame_at(e, 0, 0); im = np.asarray(im.convert('RGB')) if s['kind'] == 'hold' else grade(im, 0)
        png = dst[:-4] + '.png'; Image.fromarray(im).save(png)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(FPS), '-i', png, '-frames:v', str(n),
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
                        dst], check=True)
        os.remove(png); return dst
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', dst],
                           stdin=subprocess.PIPE)
    plate = tr = tmap = None
    if s['kind'] == 'blender':
        plate, tr, tmap = Plate(s['src']), tracks(s['src']), time_map(e)
    for k in range(n):
        enc.stdin.write(grade(frame_at(e, k / FPS, k, plate, tr, tmap), k).tobytes())
    enc.stdin.close(); enc.wait()
    if plate: plate.close()
    return dst


# ---------------------------------------------------------------- score + mix
SR = 48000


def score(tl, total, music_dir=MUSIC_DIR):
    """Theme + act cues (cue_bed), with a soft low hit on each `hit` card after the title (the theme's own
    downbeat is the title hit)."""
    from music_cues import THEME
    n = int(total * SR); at = {e['seg']['id']: e for e in tl}
    hits = np.zeros(n)
    for e in tl:
        if not e['seg'].get('hit') or e['seg']['id'] == THEME['title_seg']: continue
        i = int(e['start'] * SR); m = int(2.5 * SR); tt = np.arange(m) / SR
        b = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 1.6) + 28) / SR) * np.exp(-tt * 1.4)
        seg = b[:max(0, min(m, n - i))]; hits[i:i + len(seg)] += 0.8 * seg
    bed = cue_bed(at, total, music_dir)
    st = np.tanh(bed * 1.1 + 0.35 * hits[:, None] * 1.2) * 0.85
    from scipy.io import wavfile
    path = os.path.join(OUT, 'score.wav'); wavfile.write(path, SR, (st * 32767 * 0.9).astype(np.int16))
    return path


def _load(path, filt, ss=0.0, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}'] + (['-t', f'{dur:.3f}'] if dur else []) + \
          ['-i', path, '-af', filt, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)


def _level(x, db):
    return x * 10 ** (db / 20) / (np.sqrt((x ** 2).mean()) + 1e-9)


def cue_bed(at, total, music_dir):
    """Theme at the open and close, act cues crossfaded in between (see music_cues.py)."""
    from music_cues import CUES, THEME, XFADE, TARGET_DB, THEME_DB, ACT_FILTER, THEME_FILTER
    n = int(total * SR); bed = np.zeros((n, 2)); f = int(XFADE * SR)
    song = os.path.join(music_dir, THEME['file'])
    # open: song time HIT lands at the title card; plays from video 0, fades out across the next segment
    t_title = at[THEME['title_seg']]['start']; song_in = THEME['hit'] - t_title
    fade_end = at[THEME['fade_seg']]['start'] + THEME['fade']
    x = _load(song, THEME_FILTER, song_in, fade_end); m = min(len(x), n)
    env = np.ones(m); k = int(THEME['fade'] * SR); env[m - k:m] = np.linspace(1, 0, k) ** 1.5
    g = 10 ** (THEME_DB / 20) / (np.sqrt((x[int(t_title * SR):m] ** 2).mean()) + 1e-9)        # level set on the title section
    bed[:m] += x[:m] * env[:, None] * g
    # close: the outro runs to the song's end, finishing with the video
    close_len = THEME['song_end'] - THEME['close_in']; close_at = total - close_len
    y = _load(song, THEME_FILTER, THEME['close_in'], close_len); c0 = int(close_at * SR); m2 = min(len(y), n - c0)
    gy = 10 ** (THEME_DB / 20) / (np.sqrt((y[:int(10 * SR)] ** 2).mean()) + 1e-9)            # level set on its first 10 s
    envc = np.ones(m2); envc[:f] = np.linspace(0, 1, f)
    bed[c0:c0 + m2] += y[:m2] * envc[:, None] * gy
    # acts: each cue from its segment to the next cue (or to the theme close), crossfaded
    prev_cut = False
    for first, upto, fname, *rest in CUES:
        cut = 'cut' in rest
        t0 = at[first]['start'] + (THEME['fade'] * 0.5 if first == THEME['fade_seg'] else 0)
        t1 = at[upto]['start'] if upto else close_at
        a0 = t0 if prev_cut else max(0.0, t0 - XFADE / 2); a1 = t1 if cut else min(total, t1 + XFADE / 2)
        prev_cut = cut
        z = _load(os.path.join(music_dir, fname), ACT_FILTER)
        mono = np.abs(z).mean(1); w = int(0.5 * SR)                                              # skip leading silence
        rms = np.sqrt(np.convolve(mono ** 2, np.ones(w) / w, 'same')); start = int(np.argmax(rms > rms.max() * 10 ** (-30 / 20)))
        z = z[start:]; need = int((a1 - a0) * SR); z = np.tile(z, (need // len(z) + 1, 1))[:need]
        z = _level(z, TARGET_DB); env = np.ones(need); env[:f] = np.linspace(0, 1, f)
        fo = int(0.12 * SR) if cut else f                                               # a cut stops dead
        env[-fo:] = np.minimum(env[-fo:], np.linspace(1, 0, fo))
        i0 = int(a0 * SR); bed[i0:i0 + need] += z * env[:, None]
    return bed


def reel(tl, music_dir=MUSIC_DIR, label='STORY REEL  ·  TEMP SYNTHETIC VO'):
    """VO and music mixed with the music ducked under the voice, then one static gain to -14 LUFS (measured first),
    so music-only passages and the silent hold keep their level instead of being pumped by a dynamic normalizer."""
    total = tl[-1]['start'] + tl[-1]['dur']
    lst = os.path.join(OUT, 'segs', 'list.txt')
    with open(lst, 'w') as f:
        for e in tl: f.write(f"file '{e['seg']['id']}.mp4'\n")
    silent = os.path.join(OUT, 'reel_silent.mp4')
    # TEMP VO tag burned in on the reel only; the per-segment clips stay clean for the editor
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf',
                    f"drawtext=fontfile={gfx.FONT_DIR}/PlexMonoSemi.ttf:text='{label}':x=w-tw-64:y=h-80:"
                    "fontsize=20:fontcolor=white@0.45", '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', silent], check=True)
    mus = score(tl, total, music_dir)
    vos = [e for e in tl if e['vo']]
    inputs = ['-i', mus]
    for e in vos: inputs += ['-i', os.path.join(HERE, 'audio', f"{e['seg']['id']}.wav")]
    parts = []
    for k, e in enumerate(vos):
        d = int((e['start'] + LEAD) * 1000)
        parts.append(f'[{k + 1}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={d}|{d}[v{k}]')
    labels = ''.join(f'[v{k}]' for k in range(len(vos)))
    fc = ';'.join(parts) + f';{labels}amix=inputs={len(vos)}:normalize=0,highpass=f=70,' \
         f'acompressor=threshold=-20dB:ratio=3:attack=5:release=120,apad=whole_dur={total:.3f},asplit=2[vo][sc];' \
         f'[0:a]aresample=48000,volume=0.9[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450[duck];' \
         f'[vo][duck]amix=inputs=2:normalize=0[aout]'
    raw = os.path.join(OUT, 'mix_raw.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[aout]', '-t', f'{total:.3f}', raw], check=True)
    log = subprocess.run(['ffmpeg', '-i', raw, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float([l for l in log.splitlines() if l.strip().startswith('I:')][-1].split()[1]); gain = -15.4 - I
    dst = os.path.join(OUT, 'hoffman_ep02_story_reel.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', raw, '-filter_complex', f'[1:a]volume={gain:.2f}dB,alimiter=limit=0.84[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
                    dst], check=True)
    os.remove(raw); print(f'mix measured {I:.1f} LUFS, applied {gain:+.1f} dB ->', dst, round(total, 1), 's')
    return dst


# ---------------------------------------------------------------- editor paperwork
def write_paperwork(tl):
    os.makedirs(OUT, exist_ok=True)
    json.dump([dict(id=e['seg']['id'], start=e['start'], dur=e['dur']) for e in tl], open(os.path.join(OUT, 'timeline.json'), 'w'),
              indent=1)
    def tc(x):
        f = int(round(x * FPS)); return f'{f // (3600 * FPS):02d}:{f // (60 * FPS) % 60:02d}:{f // FPS % 60:02d}:{f % FPS:02d}'
    with open(os.path.join(OUT, 'shotlist.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'act', 'timecode_in', 'duration_s', 'kind', 'picture', 'eric_line_or_note'])
        for e in tl:
            s = e['seg']
            pic = {'blender': f"3D {s.get('src')}", 'gfx': f"graphic: {s.get('gfx')}", 'aroll': 'ERIC ON CAMERA', 'hold': 'BLACK, SILENT',
                   'interview': f"INTERVIEW {GUESTS[s.get('guest', 'defense')][0]} ({s.get('guest')}) beat {s.get('beat')} (~{s.get('plan')} s)"}[s['kind']]
            w.writerow([s['id'], s['act'], tc(e['start']), f"{e['dur']:.2f}", s['kind'], pic,
                        s.get('vo', '; '.join(s.get('topics', [])))])
    with open(os.path.join(OUT, 'captions_temp.srt'), 'w') as f:
        k = 1
        for e in tl:
            if not e['vo']: continue
            words = e['seg']['vo'].split(); chunks, cur = [], ''
            for w_ in words:
                if len(cur) + len(w_) > 42 and cur: chunks.append(cur); cur = w_
                else: cur = (cur + ' ' + w_).strip()
            chunks.append(cur); total = sum(len(c) for c in chunks); t0 = e['start'] + LEAD
            for c in chunks:
                d = e['vo'] * len(c) / total
                st = lambda x: f'{int(x // 3600):02d}:{int(x // 60) % 60:02d}:{int(x) % 60:02d},{int(x * 1000) % 1000:03d}'
                f.write(f'{k}\n{st(t0)} --> {st(t0 + d)}\n{c}\n\n'); k += 1; t0 += d


def lowerthirds():
    os.makedirs(os.path.join(OUT, 'lowerthirds'), exist_ok=True)
    straps = [('host', *HOST)] + [(k, *v) for k, v in GUESTS.items()]
    for key, name, title in straps:
        dst = os.path.join(OUT, 'lowerthirds', f'lowerthird_{key}.mov'); n = 6 * FPS
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
                                '-i', '-', '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', dst],
                               stdin=subprocess.PIPE)
        for k in range(n):
            cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            gfx.lower_third(cv, name, title, k / FPS, 0.2, out=6.0 - 0.1)
            enc.stdin.write(cv.tobytes())
        enc.stdin.close(); enc.wait(); print('wrote', dst)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'timeline'
    tl = timeline()
    if cmd == 'plates': build_plates(sys.argv[2:] or None)
    elif cmd == 'timeline':
        write_paperwork(tl)
        for e in tl:
            print(f"{e['seg']['id']} {e['start']:7.1f} {e['dur']:5.1f}  {e['seg']['kind']:9s} {e['seg']['act']}")
        print('total', round(tl[-1]['start'] + tl[-1]['dur'], 1), 's')
    elif cmd == 'still':
        e = next(x for x in tl if x['seg']['id'] == sys.argv[2]); t = float(sys.argv[3])
        plate = tr = tmap = None
        if e['seg']['kind'] == 'blender':
            tmap = time_map(e); plate = Plate(e['seg']['src']); tr = tracks(e['seg']['src'])
        os.makedirs(os.path.join(OUT, 'stills'), exist_ok=True)
        im = Image.fromarray(grade(frame_at(e, t, 0, plate, tr, tmap), 0))
        im.save(os.path.join(OUT, 'stills', f"{e['seg']['id']}_{t:.1f}.png")); print('ok')
    elif cmd == 'segs':
        ids = sys.argv[2:]
        for e in tl:
            if not ids or e['seg']['id'] in ids:
                render_seg(e); print('seg', e['seg']['id'], flush=True)
    elif cmd == 'reel':
        write_paperwork(tl); reel(tl)
    elif cmd == 'lowerthirds':
        lowerthirds()
