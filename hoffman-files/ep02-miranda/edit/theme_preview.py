"""Ep. 2 theme placement preview: the cold open into the title card, and the close into the end card, with Eric's
track "Measured in Sunlight" as the series theme. Temp synthetic VO reads his lines for timing.

Theme map (song time):
  OPEN   0:00 -> 0:56.70 downbeat lands on the title card; full section under the title, then fades into Act 1
  CLOSE  2:30.20 -> 2:55 (the song's own fade) under the last line, the sign-off, and the end card
"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'ep01-hot-coffee', 'edit'))   # ep. 1 graphics module
import gfx
W, H, FPS = gfx.W, gfx.H, gfx.FPS
SONG = os.path.join(HERE, '..', '..', 'music', 'measured_in_sunlight.mp3')   # the series theme (not committed)
HIT, CLOSE_IN, SONG_END = 56.70, 150.20, 175.70
RENDERS = os.path.join(HERE, '..', 'renders'); OUT = os.path.join(HERE, 'out'); LEAD = 0.45
VOICE = os.environ.get('PIPER_VOICE', 'en_US-ryan-high.onnx')
LINES = {
    'open1': "You have the right to remain silent. You've heard it on every cop show for fifty years. Here's what you haven't "
             "heard. The man those words are named after was convicted anyway. Twice. And when he was killed in a bar fight "
             "in 1976, the man accused of killing him was never tried. The reason wasn't Miranda.",
    'open2': "I'm Eric Hoffman. I'm a lawyer. This is the case every American can recite and almost nobody knows. Let's open the file.",
    'close1': "Ernesto Miranda was convicted twice and died in a bar fight. His name is on the most famous sentence in American "
              "law. And the right it stands for only works if you say it.",
    'close2': "Next time: the next case. I'm Eric Hoffman, and these are The Hoffman Files.",
}


def vo(key):
    p = os.path.join(HERE, 'audio', key + '.wav')
    if not os.path.exists(p):
        subprocess.run(['python3', '-m', 'piper', '-m', VOICE, '--length-scale', '1.22', '--sentence-silence', '0.28', '-f', p],
                       input=LINES[key].encode(), check=True, capture_output=True)
    with wave.open(p) as w: return p, w.getnframes() / w.getframerate()


def plate_frames(scene):
    """1080p/24 frames of a preview render (12 fps -> interpolated), decoded once."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-framerate', '12', '-pattern_type', 'glob', '-i', os.path.join(RENDERS, scene, '*.png'),
                          '-vf', 'minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1920:1080:flags=lanczos',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    return [Image.frombuffer('RGB', (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3], 'raw', 'RGB', 0, 1) for i in range(n)]


def title2(t, dur):
    cv = gfx.card(); a = gfx.fade(t, 0.0, dur, 0.15, 0.6)
    tr = 6 + 34 * (1 - gfx.ramp(t, 0.0, 1.6))
    gfx.put(cv, 'EPISODE 2', 'monob', 26, gfx.GREY, (W / 2, 330), 'c', a * gfx.ramp(t, 0.4, 0.6), track=8)
    gfx.put(cv, 'THE HOFFMAN FILES', 'bebas', 230, gfx.WHITE, (W / 2, 390), 'c', a, track=tr)
    w = 820 * gfx.ramp(t, 0.5, 1.0); gfx.rect(cv, (W / 2 - w / 2, 650, W / 2 + w / 2, 654), gfx.AMBER, a)
    gfx.put(cv, 'MIRANDA', 'monob', 44, gfx.AMBER, (W / 2, 690), 'c', a * gfx.ramp(t, 0.9, 0.7), track=14)
    return cv


def endcard2(t, dur):
    cv = gfx.card(); a = gfx.fade(t, 0.1, dur, 0.6, 1.2)
    gfx.put(cv, 'THE HOFFMAN FILES', 'bebas', 170, gfx.WHITE, (W / 2, 250), 'c', a, track=6)
    gfx.put(cv, 'LAW BY LAWYERS', 'monob', 30, gfx.AMBER, (W / 2, 450), 'c', a, track=10)
    gfx.put(cv, 'NEXT:  [NEXT CASE]', 'monob', 40, gfx.WHITE, (W / 2, 560), 'c', a * gfx.ramp(t, 0.8, 0.6), track=6)
    gfx.put(cv, "Sources: Miranda v. Arizona, 384 U.S. 436 (1966); Dickerson v. United States, 530 U.S. 428 (2000); full list in the description.",
            'mono', 21, gfx.GREY, (W / 2, 780), 'c', a)
    gfx.put(cv, '3D sequences are illustrations and reconstructions, not footage. No AI-generated imagery.', 'mono', 21, gfx.DIM, (W / 2, 830), 'c', a)
    gfx.put(cv, 'Theme: "Measured in Sunlight"', 'mono', 21, gfx.DIM, (W / 2, 880), 'c', a)
    return cv


def slate(line):
    return gfx.slate_aroll(dict(act='Cold open' if line.startswith(("I'm Eric", "You have")) else 'The holding / outro', vo=line))


def build(segments, path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for draw, dur in segments:
        n = round(dur * FPS); static = None
        for k in range(n):
            im = draw(k / FPS, dur, k)
            if im is None: im = static
            enc.stdin.write(np.asarray(im.convert('RGB')).tobytes())
    enc.stdin.close(); enc.wait()


def mix(video, vo_list, song_in, song_at, song_len, fade_out_at, fade_len, dst):
    """vo_list: [(wav, start)], song section [song_in, song_in+song_len) placed at video time song_at."""
    total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True).stdout)
    inputs = ['-i', video, '-ss', f'{song_in:.3f}', '-t', f'{song_len:.3f}', '-i', SONG]
    for w, _ in vo_list: inputs += ['-i', w]
    vparts = [f'[{k + 2}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int(s * 1000)}|{int(s * 1000)}[v{k}]' for k, (_, s) in enumerate(vo_list)]
    labels = ''.join(f'[v{k}]' for k in range(len(vo_list)))
    d = int(song_at * 1000)
    fc = ';'.join(vparts) + f';{labels}amix=inputs={len(vo_list)}:normalize=0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,' \
         f'apad=whole_dur={total:.3f},asplit=2[vo][sc];' \
         f'[1:a]aresample=48000,afade=t=in:d=1.2,afade=t=out:st={fade_out_at:.3f}:d={fade_len:.3f},adelay={d}|{d},apad=whole_dur={total:.3f},volume=0.39[mu];' \
         f'[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450[duck];[vo][duck]amix=inputs=2:normalize=0[mx]'
    raw = dst[:-4] + '_raw.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[mx]', '-t', f'{total:.3f}', raw], check=True)
    log = subprocess.run(['ffmpeg', '-i', raw, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float([l for l in log.splitlines() if l.strip().startswith('I:')][-1].split()[1]); gain = -15.4 - I
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', raw, '-filter_complex', f'[1:a]volume={gain:.2f}dB,alimiter=limit=0.84[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst], check=True)
    os.remove(raw)


def main():
    os.makedirs(OUT, exist_ok=True)
    (w1, d1), (w2, d2), (w3, d3), (w4, d4) = vo('open1'), vo('open2'), vo('close1'), vo('close2')
    card, stop = plate_frames('M1'), plate_frames('M2')
    # ---- OPEN: card push-in under line 1, Eric's slate under line 2, title on the downbeat, hand-off to Act 1
    s1 = LEAD + d1 + 0.6; s2 = LEAD + d2 + 0.4; t_title = s1 + s2; s3 = 5.0; s4 = 4.0
    def card_shot(t, dur, k):
        i = min(len(card) - 1, int(k * len(card) / round(dur * FPS)))      # stretch the 8 s push-in over the line
        return card[i]
    sl2 = slate(LINES['open2'])
    act1 = lambda t, dur, k: stop[min(len(stop) - 1, k)]
    build([(card_shot, s1), (lambda t, d, k: sl2, s2), (lambda t, d, k: title2(t, d), s3), (act1, s4)], os.path.join(OUT, 'open_silent.mp4'))
    song_in = max(0.0, HIT - t_title); song_at = max(0.0, t_title - HIT)
    total_open = s1 + s2 + s3 + s4
    mix(os.path.join(OUT, 'open_silent.mp4'), [(w1, LEAD), (w2, s1 + LEAD)], song_in, song_at, total_open - song_at,
        fade_out_at=t_title + s3 - song_at, fade_len=s4 - 0.5,          # cut-audio time where the title card ends
        dst=os.path.join(OUT, 'theme_open_preview.mp4'))
    # ---- CLOSE: last line, sign-off, end card; the song's own fade ends with the end card
    c1 = LEAD + d3 + 0.8; c2 = LEAD + d4 + 0.6; c3 = 9.0; total_close = c1 + c2 + c3
    sl3, sl4 = slate(LINES['close1']), slate(LINES['close2'])
    build([(lambda t, d, k: sl3, c1), (lambda t, d, k: sl4, c2), (lambda t, d, k: endcard2(t, d), c3)], os.path.join(OUT, 'close_silent.mp4'))
    song_len = SONG_END - CLOSE_IN; song_at = max(0.0, total_close - song_len)
    mix(os.path.join(OUT, 'close_silent.mp4'), [(w3, LEAD), (w4, c1 + LEAD)], CLOSE_IN, song_at, song_len,
        fade_out_at=song_len - 1.5, fade_len=1.5, dst=os.path.join(OUT, 'theme_close_preview.mp4'))
    print(f'open: title at {t_title:.2f}s, song in at {song_in:.2f}s; close: {total_close:.1f}s, song placed at {song_at:.2f}s')


if __name__ == '__main__':
    main()
