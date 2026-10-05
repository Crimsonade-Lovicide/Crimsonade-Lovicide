"""E4: skin cross-section. Coffee lands on the surface; heat moves down through the epidermis and the whole
dermis (full thickness). Illustrative diagram, not to scale, no injury imagery."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 12
LAYERS = [  # name, z0, z1, base colour, burned colour, burn start, burn end (frames)
    ('muscle', 0.00, 0.25, (0.55, 0.2, 0.18), None, 0, 0),
    ('fat', 0.25, 0.55, (0.9, 0.78, 0.5), None, 0, 0),
    ('dermis', 0.55, 0.80, (0.8, 0.45, 0.42), (0.2, 0.06, 0.03), 80, 230),
    ('epidermis', 0.80, 0.86, (0.88, 0.66, 0.58), (0.12, 0.04, 0.02), 36, 80),
]
W, D = 2.4, 1.4


def build():
    setup('E4', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.7)
    stage()
    mat = object_color_mat('tissue', rough=0.75)
    tracks = {}
    for name, z0, z1, col, burnt, fa, fb in LAYERS:
        o = box(name, (W, D, z1 - z0), (0, 0, (z0 + z1) / 2), mat); bevel(o, 0.01, 2)
        o.color = (*col, 1); o.keyframe_insert('color', frame=1)
        if burnt:
            o.keyframe_insert('color', frame=fa)
            o.color = (*burnt, 1); o.keyframe_insert('color', frame=fb)
        tracks[name] = (W / 2 + 0.02, -D / 2, (z0 + z1) / 2)
    film = box('coffee', (W, D, 0.02), (0, 0, 0.87), amber('coffee', 1.8))
    key(film, 'scale', 1, Vector((1, 1, 0))); key(film, 'scale', 12, Vector((1, 1, 0)))
    key(film, 'scale', 24, Vector((1, 1, 1)))
    front = box('heat_front', (W + 0.02, D + 0.02, 0.01), (0, 0, 0.86), glow_mat('heat', (1.0, 0.45, 0.1), 6, 0.6))
    key(front, 'scale', 1, Vector((0, 0, 0))); key(front, 'scale', 28, Vector((0, 0, 0)))
    key(front, 'scale', 30, Vector((1, 1, 1)))
    key(front, 'location', 30, Vector((0, 0, 0.86))); key(front, 'location', 230, Vector((0, 0, 0.55)))
    studio(key_pos=(-3, -4, 4), key_power=700, rim_pos=(3, 3, 3), rim_power=350, size=3)
    end = round(DUR * FPS)
    cam, tgt = camera((3.0, -3.6, 2.3), (0, 0, 0.45), lens=40)
    key(cam, 'location', 1, Vector((3.4, -3.3, 2.5))); key(cam, 'location', end, Vector((2.5, -3.9, 1.8)))
    tracks['full_thickness'] = (W / 2 + 0.02, -D / 2, 0.55)
    export_tracks('E4', tracks)


if __name__ == '__main__':
    run('E4', build)
