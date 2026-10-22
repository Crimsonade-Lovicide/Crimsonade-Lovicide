"""M9: a stack of warning cards and a pen on a wooden table; the top card turns over to a blank back.
No signature is shown."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 8
FLIP_A, FLIP_B = 60, 110


def build():
    setup('M9', DUR, samples=14, world=(0.001, 0.001, 0.0015), glare=0.6)
    stage()
    box('table', (1.4, 0.9, 0.04), (0, 0, 0.74), wood('table', (0.12, 0.07, 0.035), 0.5))
    paper = clay('paper', (0.84, 0.81, 0.73), 0.8); ink = clay('ink', (0.03, 0.03, 0.035), 0.6)
    random.seed(9); z = 0.76
    for i in range(24):           # the stack, slightly messy
        box(f'card{i}', (0.089, 0.051, 0.0006), (random.uniform(-0.003, 0.003), random.uniform(-0.003, 0.003), z + i * 0.0007),
            paper, rot=(0, 0, math.radians(random.uniform(-4, 4))))
    top_z = z + 24 * 0.0007 + 0.0006
    # the top card on a hinge along its long edge so it flips face-down beside the stack
    piv = bpy.data.objects.new('flip_pivot', None); bpy.context.collection.objects.link(piv); piv.location = (0, 0.0255, top_z)
    card = box('top_card', (0.089, 0.051, 0.0006), (0, 0, top_z), paper)
    txt = text_obj('top_text', WARNING, (0, -0.001, top_z + 0.0004), 0.0045, ink, spacing=1.32)
    for o in (card, txt):
        o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
    key(piv, 'rotation_euler', FLIP_A, Vector((0, 0, 0)))
    key(piv, 'location', FLIP_A, Vector((0, 0.0255, top_z)))
    key(piv, 'rotation_euler', (FLIP_A + FLIP_B) // 2, Vector((math.radians(-95), 0, 0)))
    key(piv, 'location', (FLIP_A + FLIP_B) // 2, Vector((0, 0.03, top_z + 0.03)))
    key(piv, 'rotation_euler', FLIP_B, Vector((math.radians(-180), 0, 0)))
    key(piv, 'location', FLIP_B, Vector((0, 0.056, z + 0.0006)))
    # pen
    pen = cyl('pen', 0.0045, 0.14, (0.1, -0.04, 0.765), clay('pen', (0.04, 0.05, 0.12), 0.35), rot=(0, math.radians(90), math.radians(20)))
    cyl('pen_tip', 0.003, 0.012, (0.1 - 0.074 * math.cos(math.radians(20)), -0.04 - 0.074 * math.sin(math.radians(20)), 0.765),
        steel(), rot=(0, math.radians(90), math.radians(20)))
    spot('lamp', (-0.3, -0.2, 1.6), (0, 0, 0.76), 70, angle=40, blend=0.6, size=0.1)
    light('AREA', (1.0, 1.0, 1.4), 3, (0.75, 0.82, 1.0), size=1.5, rot=look_rot((1.0, 1.0, 1.4), (0, 0, 0.76)))
    end = round(DUR * FPS)
    cam, tgt = camera((0.06, -0.42, 1.12), (0.0, 0.02, 0.765), lens=70)
    key(cam, 'location', 1, Vector((0.06, -0.42, 1.12))); key(cam, 'location', end, Vector((0.02, -0.30, 1.02)))
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = card; cam.data.dof.aperture_fstop = 5.6
    export_tracks('M9', {'stack': (0, 0, 0.78)})


if __name__ == '__main__':
    run('M9', build)
