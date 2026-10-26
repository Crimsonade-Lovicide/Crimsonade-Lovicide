"""M1 cold open: a worn warning card on a steel table under one lamp, slow push-in. Generic wording, no seal."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 8


def build():
    setup('M1', DUR, samples=14, world=(0.001, 0.001, 0.0015), glare=0.6)
    stage()
    table = box('table', (1.6, 1.0, 0.04), (0, 0, 0.74), steel('steel', (0.16, 0.165, 0.17), 0.32)); bevel(table, 0.004)
    # the card: 89 x 51 mm, a few degrees off square, slightly worn paper
    card = box('card', (0.089, 0.051, 0.0006), (0, 0, 0.7603), clay('paper', (0.84, 0.81, 0.73), 0.8))
    ink = clay('ink', (0.03, 0.03, 0.035), 0.6)
    txt = text_obj('warning', WARNING, (0, -0.001, 0.7607), 0.0045, ink, spacing=1.32)
    for o in (card, txt): o.rotation_euler = (0, 0, math.radians(-8))
    txt.location = card.location + Vector((0, 0, 0.0004))
    spot('lamp', (0.05, 0.08, 1.9), (0, 0, 0.76), 120, angle=9, blend=0.8, size=0.08)
    light('AREA', (-1.2, -1.0, 1.4), 0.6, (0.75, 0.82, 1.0), size=1.5, rot=look_rot((-1.2, -1.0, 1.4), (0, 0, 0.76)))
    end = round(DUR * FPS)
    cam, tgt = camera((0.02, -0.52, 1.12), (0, 0, 0.76), lens=85)
    key(cam, 'location', 1, Vector((0.02, -0.52, 1.12))); key(cam, 'location', end, Vector((0.0, -0.29, 0.98)))
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = card; cam.data.dof.aperture_fstop = 4.0
    export_tracks('M1', {'card': (0, 0, 0.761)})


if __name__ == '__main__':
    run('M1', build)
