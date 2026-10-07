"""Rebuild the ep. 1 story reel with the final music: theme open/close + public domain act cues.
VO and music are mixed with the music ducked under the voice, then one static gain to -14 LUFS (measured first),
so music-only passages keep their level instead of being pumped up by a dynamic normalizer."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit, gfx
tl = edit.timeline(); total = tl[-1]['start'] + tl[-1]['dur']; OUT = edit.OUT
lst = os.path.join(OUT, 'segs', 'list.txt')
with open(lst, 'w') as f:
    for e in tl: f.write(f"file '{e['seg']['id']}.mp4'\n")
silent = os.path.join(OUT, 'reel_silent.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-vf',
                f"drawtext=fontfile={gfx.FONT_DIR}/PlexMonoSemi.ttf:text='STORY REEL  ·  TEMP SYNTHETIC VO':x=w-tw-64:y=h-80:fontsize=20:fontcolor=white@0.45",
                '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', silent], check=True)
mus = edit.score(tl, total, os.environ.get('MUSIC_DIR', os.path.join(edit.HERE, '..', '..', 'music')))   # shared hoffman-files/music
vos = [e for e in tl if e['vo']]
inputs = ['-i', mus]
for e in vos: inputs += ['-i', os.path.join(edit.HERE, 'audio', f"{e['seg']['id']}.wav")]
parts = [f'[{k + 1}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int((e["start"] + edit.LEAD) * 1000)}|{int((e["start"] + edit.LEAD) * 1000)}[v{k}]'
         for k, e in enumerate(vos)]
fc = ';'.join(parts) + f";{''.join(f'[v{k}]' for k in range(len(vos)))}amix=inputs={len(vos)}:normalize=0,highpass=f=70," \
     f'acompressor=threshold=-20dB:ratio=3:attack=5:release=120,apad=whole_dur={total:.3f},asplit=2[vo][sc];' \
     f'[0:a]aresample=48000,volume=0.9[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450[duck];[vo][duck]amix=inputs=2:normalize=0[aout]'
raw = os.path.join(OUT, 'final_mix_raw.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[aout]', '-t', f'{total:.3f}', raw], check=True)
log = subprocess.run(['ffmpeg', '-i', raw, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', log)[-1]); gain = -15.4 - I
dst = os.path.join(OUT, 'hoffman_ep01_story_reel.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', raw, '-filter_complex', f'[1:a]volume={gain:.2f}dB,alimiter=limit=0.84[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', dst], check=True)
os.remove(raw); print(f'mix measured {I:.1f} LUFS, applied {gain:+.1f} dB ->', dst)
