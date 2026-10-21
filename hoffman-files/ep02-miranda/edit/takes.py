"""Eric's recorded takes. A segment with `take` (a file in takes/) and `cuts` (source in/out seconds, spoken parts
only) uses the take instead of the temp voice: vo.py builds its audio from the cuts, and edit.py builds its picture
from the same cuts, so the two stay in sync. Cut points snap to the 24 fps frame grid so picture and sound have
exactly the same length. `zooms` (one per cut, default 1.0) gives the alternating punch-in that hides jump cuts.
Cut times are on the take's own clock (container timestamps): a phone .mov can start its audio a little after its
picture, and trimming by timestamp keeps lip sync.

Raw takes stay out of git (keep the originals); only the cut list lives in episode.py."""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TAKES = os.path.join(HERE, 'takes')
FPS = 24
TARGET_LUFS = -15.0          # the temp voice's level, so the mix treats a real take the same way
FADE = 0.012                 # de-click at each audio cut


def path(seg):
    return os.path.join(TAKES, seg['take'])


def cuts(seg):
    return [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in seg['cuts']]


def speech_len(seg):
    return sum(b - a for a, b in cuts(seg))


def build_audio(seg, dst):
    """Concatenate the spoken parts, clean lightly, and match the temp voice's loudness."""
    parts, labels = [], ''
    for k, (a, b) in enumerate(cuts(seg)):
        d = b - a
        parts.append(f'[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,'
                     f'afade=t=in:d={FADE},afade=t=out:st={d - FADE:.4f}:d={FADE}[a{k}]')
        labels += f'[a{k}]'
    n = len(parts)
    chain = ';'.join(parts) + f';{labels}concat=n={n}:v=0:a=1,highpass=f=80,afftdn=nf=-50,aresample=48000'
    tmp = dst + '.tmp.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path(seg), '-filter_complex', chain, '-ac', '1', tmp], check=True)
    log = subprocess.run(['ffmpeg', '-i', tmp, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    I = float([l for l in log.splitlines() if l.strip().startswith('I:')][-1].split()[1])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'volume={TARGET_LUFS - I:.2f}dB,alimiter=limit=0.9',
                    '-ar', '48000', dst], check=True)
    os.remove(tmp)


def picture_cmd(seg, lead, dur, w, h):
    """ffmpeg command writing rgb24 frames for the whole segment: `lead` s of the take before the first cut, the
    cuts back to back (each at its zoom), then the take running on past the last cut to fill `dur`."""
    cs = cuts(seg); zooms = seg.get('zooms', [1.0] * len(cs)); fx, fy = seg.get('focus', (0.5, 0.4))
    ins = [(max(0.0, cs[0][0] - lead), cs[0][1])] + cs[1:]
    used = sum(b - a for a, b in ins)
    ins[-1] = (ins[-1][0], ins[-1][1] + max(0.0, dur - used))           # run on to fill the tail
    parts, labels = [], ''
    for k, ((a, b), z) in enumerate(zip(ins, zooms)):
        crop = (f'crop=iw/{z}:ih/{z}:(iw-iw/{z})*{fx}:(ih-ih/{z})*{fy},' if z != 1.0 else '')
        parts.append(f'[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,fps={FPS},{crop}'
                     f'scale={w}:{h}:flags=lanczos,setsar=1[v{k}]')
        labels += f'[v{k}]'
    chain = ';'.join(parts) + f';{labels}concat=n={len(parts)}:v=1:a=0,tpad=stop_mode=clone:stop_duration=1[v]'
    n = round(dur * FPS)
    return ['ffmpeg', '-v', 'error', '-i', path(seg), '-filter_complex', chain, '-map', '[v]', '-frames:v', str(n),
            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']


# ---------------------------------------------------------------- word timings (cues follow Eric's actual delivery)
def transcript_path(seg):
    return path(seg) + '.words.json'


def words(seg):
    """Words of the built line with their start times (s from its first sample). Prefers audio/<id>.words.json, a
    transcript of the built audio itself (words_qc.py writes it); else maps takes/<take>.words.json, a transcript of
    the whole take on its own clock ([{"w", "s", "e"}, ...]), through the cuts."""
    import json
    own = os.path.join(HERE, 'audio', seg['id'] + '.words.json')     # per-line transcript of the built audio
    if os.path.exists(own): return [tuple(x) for x in json.load(open(own))]
    tp = transcript_path(seg)
    if not os.path.exists(tp): return None
    allw = json.load(open(tp)); out, base = [], 0.0
    for a, b in cuts(seg):
        for w in allw:
            mid = (w['s'] + w['e']) / 2
            if a <= mid < b: out.append((w['w'], base + max(0.0, w['s'] - a)))
        base += b - a
    return out


NUM = dict(zip('0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 30'.split(),
               'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen '
               'seventeen eighteen nineteen twenty thirty'.split()))


def norm(t):
    import re
    w = re.sub(r"[^a-z0-9']", '', t.lower().replace('’', "'"))
    w = SAME.get(w, w)
    return NUM.get(w, w)                                         # '5' and 'five' match


SAME = {'steven': 'stephen'}                                     # same sound, either spelling


def phrase_at(seg, phrase):
    """Time (s from the start of the built audio) where `phrase` starts in the take, or None if not found."""
    ws = words(seg)
    if not ws: return None
    toks = [norm(w) for w, _ in ws]; want = [norm(p) for p in phrase.split() if norm(p)]
    for i in range(len(toks) - len(want) + 1):
        if toks[i:i + len(want)] == want: return ws[i][1]
    for i in range(len(toks)):                                  # looser: first two words
        if toks[i:i + 2] == want[:2]: return ws[i][1]
    if toks.count(want[0]) == 1: return ws[toks.index(want[0])][1]  # loosest: a first word heard only once
    return None
