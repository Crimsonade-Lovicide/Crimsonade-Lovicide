import os
from compose import TL, seg_frames, make_base, SCR
for pid in TL:
    segs = TL[pid]['segs']; os.makedirs(f'{SCR}/out/{pid}', exist_ok=True)
    for i, (s, n) in enumerate(zip(segs, seg_frames(segs))):
        if s['vis'].startswith('K'):
            make_base(pid, s['vis'], n, f'{SCR}/out/{pid}/seg{i:02d}_{s["vis"]}.mp4'); print(pid, s['vis'], 'ok', flush=True)
