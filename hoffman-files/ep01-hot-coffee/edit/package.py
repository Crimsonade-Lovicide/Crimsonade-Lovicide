"""Editor package: every beat as its own clean 1080p clip (named in edit order), alpha name straps,
shot list, temp captions, thumbnails, and the temp VO lines -> out/hoffman_ep01_editor_package.zip"""
import os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from episode import SEGMENTS
OUT = os.path.join(HERE, 'out'); P = os.path.join(OUT, 'package')
for d in ('clips', 'name_straps', 'paperwork', 'thumbnail', 'temp_vo'): os.makedirs(os.path.join(P, d), exist_ok=True)
for s in SEGMENTS:
    what = {'blender': f"3D_{s.get('src')}", 'gfx': f"graphic_{s.get('gfx')}", 'aroll': 'ERIC_ON_CAMERA_slate',
            'interview': f"INTERVIEW_{s.get('guest')}_beat{s.get('beat')}_slate"}[s['kind']]
    dst = os.path.join(P, 'clips', f"{s['id']}_{what}.mp4")
    if not os.path.exists(dst):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'segs', f"{s['id']}.mp4"), '-vf', 'hqdn3d=1.5:1.5:2:2',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', dst], check=True)
    if s.get('vo'): shutil.copy(os.path.join(HERE, 'audio', f"{s['id']}.wav"), os.path.join(P, 'temp_vo', f"{s['id']}.wav"))
for f in os.listdir(os.path.join(OUT, 'lowerthirds')): shutil.copy(os.path.join(OUT, 'lowerthirds', f), os.path.join(P, 'name_straps', f))
for f in ('shotlist.csv', 'captions_temp.srt'): shutil.copy(os.path.join(OUT, f), os.path.join(P, 'paperwork', f))
for f in ('thumbnail_textonly.jpg', 'thumbnail_layout_guide.jpg'): shutil.copy(os.path.join(OUT, f), os.path.join(P, 'thumbnail', f))
open(os.path.join(P, 'READ_ME.txt'), 'w').write("""THE HOFFMAN FILES - EP. 1: THE HOT COFFEE CASE - EDITOR PACKAGE

clips/        One clean 1080p/24 fps clip per beat, numbered in edit order (s01..s33). No temp tags, no audio.
              ERIC_ON_CAMERA and INTERVIEW clips are placeholder slates: replace them with Eric's takes and the
              guest answers. Lines for each beat are in paperwork/shotlist.csv.
name_straps/  ProRes 4444 with alpha, 6 s each: host, S. Reed Morgan, counterpoint guest (edit the name when booked).
paperwork/    shotlist.csv (timecodes from the story reel) and captions_temp.srt (re-time to Eric's delivery).
temp_vo/      The synthetic guide reads, one per beat. Pacing reference only; never publish them.
thumbnail/    Text-only version and a layout guide for Eric's cutout.

Labels that must stay on screen: "Reconstruction" (spill), "Diagram - illustration, not to scale" (skin),
"Illustration - generic car" (car), "Paraphrase" (quality-assurance testimony) until the transcript quote is in.
""")
zp = os.path.join(OUT, 'hoffman_ep01_editor_package.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_STORED) as z:
    for root, _, files in os.walk(P):
        for f in sorted(files):
            z.write(os.path.join(root, f), os.path.join('hoffman_ep01_editor_package', os.path.relpath(os.path.join(root, f), P)))
print('wrote', zp, round(os.path.getsize(zp) / 1e6), 'MB')
