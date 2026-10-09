"""M10: a bar exterior at night, sign unlit, empty street. Generic building, no name, no violence. Labeled Illustration."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 8


def build():
    setup('M10', DUR, samples=14, world=NIGHT, glare=0.7)
    night_ground()
    stucco = clay('stucco', (0.33, 0.28, 0.22), 0.9)
    box('facade', (10, 0.3, 4.0), (0, -4.2, 2.15), stucco)
    box('parapet', (10.2, 0.4, 0.3), (0, -4.2, 4.2), clay('trim', (0.2, 0.17, 0.13), 0.8))
    box('door', (1.0, 0.06, 2.2), (0, -4.04, 1.25), wood('door', (0.12, 0.06, 0.03), 0.6))
    glow = mat_emit('interior', (1.0, 0.55, 0.25), 1.2)
    for x in (-2.6, 2.6):
        box(f'window{x}', (1.8, 0.04, 1.1), (x, -4.03, 1.75), glow)
        box(f'sill{x}', (1.9, 0.12, 0.06), (x, -3.98, 1.17), clay('sill', (0.2, 0.17, 0.13), 0.8))
    box('sign_box', (3.2, 0.25, 0.7), (0, -3.95, 3.35), clay('signbox', (0.06, 0.06, 0.07), 0.5))   # unlit, no name
    box('sign_face', (3.0, 0.02, 0.55), (0, -3.81, 3.35), mat_principled('signface', (0.12, 0.12, 0.13), rough=0.3))
    spot('over_door', (0, -3.6, 3.0), (0, -3.0, 0.15), 300, angle=60, blend=0.6, color=LAMP)
    light('AREA', (6, 8, 12), 220, (0.55, 0.65, 1.0), size=10, rot=look_rot((6, 8, 12), (0, -4, 2)))   # moonlight
    metal = steel('pole', (0.3, 0.3, 0.3), 0.5)
    cyl('lamp_pole', 0.06, 6.0, (-5.5, -1.0, 3.0), metal)
    box('lamp_head', (0.5, 0.25, 0.1), (-4.8, -1.0, 5.88), clay('lamphead', (0.1, 0.1, 0.1), 0.6))
    box('lamp_glass', (0.44, 0.2, 0.01), (-4.8, -1.0, 5.82), mat_emit('sodium_glass', SODIUM, 18))
    spot('sodium', (-4.8, -1.0, 5.75), (-4.0, -1.5, 0), 2600, angle=70, blend=0.7, color=SODIUM, size=0.2)
    end = round(DUR * FPS)
    cam, tgt = camera((2.6, 6.5, 1.6), (0, -4.0, 2.0), lens=32)
    key(cam, 'location', 1, Vector((2.6, 6.5, 1.6))); key(cam, 'location', end, Vector((1.8, 5.0, 1.5)))
    export_tracks('M10', {'door': (0, -4.0, 2.4)})


if __name__ == '__main__':
    run('M10', build)
