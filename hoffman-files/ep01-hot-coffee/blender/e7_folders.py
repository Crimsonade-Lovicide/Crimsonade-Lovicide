"""E7: 700+ burn reports, 1982-1992, as a rising stack of report folders. 1 folder = 10 reports."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 12
N, PITCH, FIRST, RATE = 70, 0.022, 12, 3


def build():
    random.seed(700)
    setup('E7', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.9)
    stage()
    manila = clay('manila', (0.55, 0.42, 0.2), 0.8)
    for i in range(N):
        z = PITCH * i + PITCH / 2
        x, y, rz = random.uniform(-0.02, 0.02), random.uniform(-0.02, 0.02), math.radians(random.uniform(-5, 5))
        f = box(f'folder{i}', (0.34, 0.25, PITCH * 0.8), (x, y, z), manila, rot=(0, 0, rz))
        tab = box(f'tab{i}', (0.1, 0.03, PITCH * 0.7), (x - 0.08, y + 0.14, z), manila, rot=(0, 0, rz))
        tab.parent = f; tab.matrix_parent_inverse = f.matrix_world.inverted()
        fl = FIRST + i * RATE
        key(f, 'location', fl - 6, Vector((x, y, z + 0.6))); key(f, 'location', fl, Vector((x, y, z)))
        f.hide_render = True; f.keyframe_insert('hide_render', frame=1); f.keyframe_insert('hide_render', frame=fl - 7)
        f.hide_render = False; f.keyframe_insert('hide_render', frame=fl - 6)
        tab.hide_render = True; tab.keyframe_insert('hide_render', frame=1); tab.keyframe_insert('hide_render', frame=fl - 7)
        tab.hide_render = False; tab.keyframe_insert('hide_render', frame=fl - 6)
        for o in (f, tab):
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if fc.data_path == 'hide_render' else 'QUAD'
    top = PITCH * N
    studio(key_pos=(-1.5, -2, 3), key_power=350, rim_pos=(1.5, 1.8, 2.2), rim_power=220, size=2)
    end = round(DUR * FPS)
    cam, tgt = camera((0.3, -2.2, 0.35), (0, 0, 0.3), lens=40)
    key(cam, 'location', 1, Vector((0.3, -2.2, 0.35))); key(tgt, 'location', 1, Vector((0, 0, 0.3)))
    key(cam, 'location', FIRST + N * RATE, Vector((0.9, -2.4, top + 0.25))); key(tgt, 'location', FIRST + N * RATE, Vector((0, 0, top - 0.6)))
    key(cam, 'location', end, Vector((1.1, -2.5, top + 0.35))); key(tgt, 'location', end, Vector((0, 0, top - 0.6)))
    export_tracks('E7', {'top': (0, 0, top + 0.05), 'base': (0.2, -0.15, 0)})


if __name__ == '__main__':
    run('E7', build)
