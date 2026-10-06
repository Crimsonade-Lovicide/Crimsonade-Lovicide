"""Re-mix the review cut's audio only (picture untouched): VO + ducked music cues, static loudness gain to -14 LUFS
(measured in a first pass) so music-only passages keep their level instead of being pumped up."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit
tl = edit.timeline(); total = tl[-1]['start'] + tl[-1]['dur']
src = os.path.join(edit.OUT, 'reel_silent_review.mp4')
mus = edit.score(tl, total, os.path.join(edit.HERE, 'music'))
vos = [e for e in tl if e['vo']]
inputs = ['-i', mus]
for e in vos: inputs += ['-i', os.path.join(edit.HERE, 'audio', f"{e['seg']['id']}.wav")]
parts = [f'[{k + 1}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={int((e["start"] + edit.LEAD) * 1000)}|{int((e["start"] + edit.LEAD) * 1000)}[v{k}]'
         for k, e in enumerate(vos)]
labels = ''.join(f'[v{k}]' for k in range(len(vos)))
fc = ';'.join(parts) + f';{labels}amix=inputs={len(vos)}:normalize=0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,' \
     f'apad=whole_dur={total:.3f},asplit=2[vo][sc];[0:a]volume=0.9[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[duck];' \
     f'[vo][duck]amix=inputs=2:normalize=0[aout]'
raw = os.path.join(edit.OUT, 'review_mix_raw.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[aout]', '-t', f'{total:.3f}', raw], check=True)
log = subprocess.run(['ffmpeg', '-i', raw, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', log)[-1]); gain = -15.4 - I              # -15.4 lands at about -14 LUFS after the limiter and AAC
dst = os.path.join(edit.OUT, 'hoffman_ep01_review_es_previews.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', raw, '-filter_complex', f'[1:a]volume={gain:.2f}dB,alimiter=limit=0.84[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', dst], check=True)
print(f'measured {I:.1f} LUFS, applied {gain:+.1f} dB ->', dst)
