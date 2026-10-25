"""Three vertical Shorts (1080x1920, 24 fps) cut from the finished episode master. Each is one continuous stretch of
the cut, so the voice and music are the episode's own mix. On-camera segments get a centre crop that fills the
frame; cards and 3D keep their full width in a band. Captions are re-flowed to short lines from the same word
timings as captions.srt and burned in; a series bug sits on top and a 'full episode' tag closes each one.

  python3 shorts.py <master.mp4> <out_dir>"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit, captions

W, H, FPS = 1080, 1920, 24
FONTS = os.path.join(HERE, '..', 'fonts')
BAND_Y = (H - 608) // 2                                  # a 16:9 card fitted to the width sits here
TAG_SECS = 2.6

SHORTS = [  # title, segment ids (consecutive in the cut), tail seconds past the last segment
    ('01_hook', ['s01', 's02', 's03'], 0.0, 36.0),       # cut inside the title card at 36 s
    ('02_myth', ['s17', 's18', 's19'], 0.0, None),
    ('03_ending', ['s21', 's22', 's23'], 0.0, None),
]


def ranges(ids, tl, end_at):
    es = [e for e in tl if e['seg']['id'] in ids]
    out = []
    for e in es:
        a, b = e['start'], e['start'] + e['dur']
        if end_at: b = min(b, end_at)
        if b > a: out.append((a, b, e['seg']['kind']))
    return out


def ass_file(cues, t0, t1, path):
    """Re-flowed captions for the window as an ASS file at the Short's own resolution."""
    hdr = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n'
           '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, '
           'Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, '
           'MarginR, MarginV, Encoding\n'
           'Style: Cap,Inter,64,&H00F2F0EA,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,0,2,60,60,230,1\n\n'
           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
    def ts(x):
        cs = int(round(x * 100)); return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'
    lines = []
    for a, b, text in cues:
        if b <= t0 or a >= t1: continue
        a, b = max(a, t0) - t0, min(b, t1) - t0
        lines.append(f'Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{text.replace(chr(10), chr(92) + "N")}')
    open(path, 'w').write(hdr + '\n'.join(lines) + '\n'); return len(lines)


def build(master, out_dir, name, ids, tail, end_at, tl, cues):
    rs = ranges(ids, tl, end_at); t0, t1 = rs[0][0], rs[-1][1] + tail
    ass = os.path.join(out_dir, f'{name}.ass'); n = ass_file(cues, t0, t1, ass)
    parts, labels = [], ''
    for k, (a, b, kind) in enumerate(rs):
        if kind == 'aroll':      # centre crop 3:4 of the 1080-high frame, scaled to fill the width, centred vertically
            f = (f'[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,crop=810:1080:(iw-810)*0.5:0,scale={W}:1440:flags=lanczos,'
                 f'pad={W}:{H}:0:{(H - 1440) // 2}:black[v{k}]')
        else:                    # full width in a band on black
            f = (f'[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,scale={W}:608:flags=lanczos,'
                 f'pad={W}:{H}:0:{BAND_Y}:black[v{k}]')
        parts.append(f); labels += f'[v{k}]'
    dur = t1 - t0
    font = lambda f: os.path.join(FONTS, f).replace(':', r'\:')
    bug = (f"drawtext=fontfile={font('PlexMonoSemi.ttf')}:text='THE HOFFMAN FILES':fontsize=30:fontcolor=white@0.75:"
           f"x=(w-tw)/2:y=150,drawtext=fontfile={font('PlexMonoSemi.ttf')}:text='MIRANDA v. ARIZONA':fontsize=26:"
           f"fontcolor=0xEC8C34:x=(w-tw)/2:y=196")
    tag = (f"drawtext=fontfile={font('BebasNeue.ttf')}:text='FULL EPISODE ON THE CHANNEL':fontsize=72:fontcolor=white:"
           f"x=(w-tw)/2:y=1560:enable='gte(t,{dur - TAG_SECS:.2f})':box=1:boxcolor=black@0.55:boxborderw=22")
    fc = (';'.join(parts) + f';{labels}concat=n={len(parts)}:v=1:a=0,fps={FPS},'
          f"ass={ass}:fontsdir={FONTS},{bug},{tag}[v];"
          f'[0:a]atrim={t0:.4f}:{t1:.4f},asetpts=PTS-STARTPTS,afade=t=out:st={dur - 0.6:.3f}:d=0.6[a]')
    dst = os.path.join(out_dir, f'hoffman_ep02_short_{name}.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', master, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', dst], check=True)
    print(f'{name}: {t0:.1f}-{t1:.1f} s ({dur:.1f} s), {n} caption cues ->', dst)
    return dst, dur


if __name__ == '__main__':
    master, out_dir = sys.argv[1], sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
    captions.LINE = 24                                   # short lines for a phone screen
    cues = captions.build(); tl = edit.timeline()
    for name, ids, tail, end_at in SHORTS: build(master, out_dir, name, ids, tail, end_at, tl, cues)
