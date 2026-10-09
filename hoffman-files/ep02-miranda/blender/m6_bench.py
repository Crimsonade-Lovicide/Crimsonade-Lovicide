"""M6: nine empty high-backed chairs behind a bench. Five light up one by one; four stay dark (5-4).
Abstract bench: not a model of the real courtroom, and the lit seats are not the justices' actual positions."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 10
LIT = [1, 3, 4, 6, 8]            # which of the nine light up (abstract pattern)
ON = [48, 72, 96, 120, 144]      # frame each one comes on


def build():
    setup('M6', DUR, samples=16, world=(0.0015, 0.0015, 0.002), glare=0.7)
    stage((0.02, 0.018, 0.016))
    panel = wood('panel', (0.16, 0.1, 0.055), 0.5)
    box('back_wall', (12, 0.1, 6), (0, 2.2, 3), panel)
    box('dais', (9.6, 2.4, 0.4), (0, 1.0, 0.2), panel)
    bench = box('bench', (9.4, 0.5, 1.15), (0, -0.05, 0.98), wood('bench', (0.26, 0.15, 0.075), 0.42)); bevel(bench, 0.02)
    leather = mat_principled('leather', (0.05, 0.028, 0.02), rough=0.45)
    for i in range(9):
        x = (i - 4) * 1.0
        s = box(f'seat{i}', (0.6, 0.6, 0.12), (x, 0.9, 0.95), leather); bevel(s, 0.04)
        b = box(f'back{i}', (0.62, 0.14, 1.9), (x, 1.2, 1.9), leather); bevel(b, 0.05)
        # a dim key on every chair; the five that light up get a bright spot that comes on in turn
        spot(f'dim{i}', (x, -1.5, 4.2), (x, 1.15, 1.8), 70, angle=22, blend=0.5)
        if i in LIT:
            sp = spot(f'on{i}', (x, -0.8, 4.6), (x, 1.15, 1.9), 0, angle=20, blend=0.45, color=(1.0, 0.78, 0.5))
            f = ON[LIT.index(i)]
            key(sp.data, 'energy', 1, 0.0); key(sp.data, 'energy', f, 0.0); key(sp.data, 'energy', f + 6, 900.0)
    end = round(DUR * FPS)
    cam, tgt = camera((0, -9.5, 2.9), (0, 1.0, 1.8), lens=40)
    light('AREA', (0, -6, 5), 450, (0.7, 0.75, 0.9), size=8, rot=look_rot((0, -6, 5), (0, 0.5, 1)))
    key(cam, 'location', 1, Vector((0, -9.5, 2.9))); key(cam, 'location', end, Vector((0, -8.4, 3.1)))
    export_tracks('M6', {f'chair{i}': ((i - 4) * 1.0, 1.2, 2.9) for i in range(9)})


if __name__ == '__main__':
    run('M6', build)
