"""M2: an empty bus stop under a sodium streetlight, Phoenix, night. No figure, ever. Labeled Illustration."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 8


def build():
    setup('M2', DUR, samples=14, world=(0.006, 0.009, 0.02), glare=0.7)
    night_ground()
    metal = steel('pole', (0.3, 0.3, 0.3), 0.5)
    cyl('sign_pole', 0.03, 2.6, (0.6, -0.4, 1.3), metal)
    plate = box('sign', (0.36, 0.02, 0.5), (0.6, -0.42, 2.35), clay('signplate', (0.75, 0.74, 0.7), 0.6))
    text_obj('busstop', 'BUS\nSTOP', (0.6, -0.435, 2.35), 0.11, clay('signink', (0.05, 0.12, 0.3), 0.6), rot=(math.radians(90), 0, 0), font='BebasNeue.ttf', spacing=0.9)
    # bench: three slats on two legs
    wd = wood('bench', (0.22, 0.13, 0.07))
    for i, z in enumerate((0.45, 0.62, 0.79)):
        box(f'slat{i}', (1.6, 0.08 if i == 0 else 0.03, 0.04 if i == 0 else 0.1), (-0.6, -1.2 + (0 if i == 0 else 0.18), z), wd)
    for x in (-1.25, 0.05):
        box(f'benchleg{x}', (0.05, 0.4, 0.45), (x, -1.15, 0.3), metal)
    # streetlight: pole, arm, head, sodium spot making a pool on the sidewalk and street
    cyl('lamp_pole', 0.06, 6.0, (2.6, -0.3, 3.0), metal)
    box('lamp_arm', (1.6, 0.08, 0.08), (1.9, -0.3, 5.95), metal)
    box('lamp_head', (0.5, 0.25, 0.1), (1.2, -0.3, 5.88), clay('lamphead', (0.1, 0.1, 0.1), 0.6))
    box('lamp_glass', (0.44, 0.2, 0.01), (1.2, -0.3, 5.82), mat_emit('sodium_glass', SODIUM, 18))
    spot('sodium', (1.2, -0.3, 5.75), (0.4, -0.6, 0), 2600, angle=70, blend=0.7, color=SODIUM, size=0.2)
    # distant city: dark blocks with a few lit windows, far down the street
    dark = clay('bldg', (0.012, 0.012, 0.016), 0.9); win = mat_emit('window', (1.0, 0.75, 0.45), 1.2)
    random.seed(4)
    for i in range(9):
        x = -14 + i * 3.4; h = random.uniform(3, 9)
        box(f'bldg{i}', (3.0, 3.0, h), (x, 16, h / 2), dark)
        for j in range(random.randint(0, 3)):
            box(f'win{i}_{j}', (0.5, 0.02, 0.6), (x + random.uniform(-1, 1), 14.49, random.uniform(1, h - 1)), win)
    end = round(DUR * FPS)
    cam, tgt = camera((-3.4, -7.2, 1.55), (0.2, -0.6, 1.2), lens=32)
    key(cam, 'location', 1, Vector((-3.4, -7.2, 1.55))); key(cam, 'location', end, Vector((-2.2, -6.4, 1.45)))
    export_tracks('M2', {'stop': (0.6, -0.4, 2.35)})


if __name__ == '__main__':
    run('M2', build)
