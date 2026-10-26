"""E3: reconstruction of the spill. A stylized, faceless figure in a passenger seat holds the cup between
her knees, pulls the lid toward her, and the cup tips into her lap. She flinches up and back, then hunches
forward pulling at the soaked sweatpants, and the camera closes in on the fabric. Cut-away car, no likeness."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 10
FLINCH = (-4, 34)          # (shoulder, elbow) degrees: hands thrown up in front of the chest
GRAB = (-44, 70)           # hands on the thighs while hunched
TUG = (-50, 84)            # hands lifted ~5 cm, pulling the fabric away
LID_A, LID_B = 60, 100      # lid pulled toward her
TIP_A, TIP_B = 100, 122     # cup tips
SOAK_A, SOAK_B = 116, 200   # coffee spreads, sweatpants darken
HIT = 110                   # coffee reaches her lap; reaction starts here


def attach(child, parent):
    child.parent = parent; child.matrix_parent_inverse = parent.matrix_world.inverted()
    return child


def empty(name, loc):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    return e


def build():
    setup('E3', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.8)
    stage()
    seat = clay('seat', (0.2, 0.2, 0.21), 0.7)
    sb = bevel(box('seat_base', (0.58, 0.6, 0.14), (0, -0.05, 0.46), object_color_mat('seat_soak', rough=0.7)), 0.05)
    sb.color = (0.2, 0.2, 0.21, 1); sb.keyframe_insert('color', frame=140)
    sb.color = (0.15, 0.11, 0.08, 1); sb.keyframe_insert('color', frame=225)
    bevel(box('seat_back', (0.58, 0.13, 0.78), (0, -0.4, 0.86), seat, rot=(math.radians(-12), 0, 0)), 0.05)
    box('floor_pan', (1.2, 1.6, 0.04), (0, 0.35, 0.06), clay('pan', (0.08, 0.08, 0.09)))
    skin = clay('figure', (0.2, 0.2, 0.21), 0.8)   # darker figure so the white cup reads
    pants = object_color_mat('pants', rough=0.85)
    # upper body hangs off a hip pivot (spine) so it can recoil and hunch; arms hang off shoulder pivots
    spine = empty('spine', (0, -0.14, 0.6))
    attach(capsule('torso', (0, -0.16, 0.62), (0, -0.27, 1.1), 0.14, skin), spine)
    attach(sphere('head', 0.1, (0, -0.29, 1.32), skin, scale=(0.9, 1.0, 1.1)), spine)   # faceless by design
    thighs, shoulders, elbows, hands = [], [], [], []
    for s in (1, -1):
        t = capsule(f'thigh{s}', (0.1 * s, -0.1, 0.6), (0.1 * s, 0.32, 0.62), 0.078, pants); thighs.append(t)
        capsule(f'shin{s}', (0.1 * s, 0.34, 0.6), (0.1 * s, 0.42, 0.13), 0.06, pants).color = (0.26, 0.26, 0.27, 1)
        sh = attach(empty(f'shoulder{s}', (0.19 * s, -0.22, 1.04)), spine); shoulders.append(sh)
        attach(capsule(f'upperarm{s}', (0.19 * s, -0.22, 1.04), (0.2 * s, 0.0, 0.82), 0.045, skin), sh)
        el = attach(empty(f'elbow{s}', (0.2 * s, 0.0, 0.82)), sh); elbows.append(el)
        attach(capsule(f'forearm{s}', (0.2 * s, 0.0, 0.82), (0.15 * s, 0.26, 0.72), 0.04, skin), el)
        hands.append(attach(sphere(f'hand{s}', 0.042, (0.15 * s, 0.29, 0.715), skin), el))
    # reaction: rest -> recoil up and back, hands fly up -> hunch forward, hands pulling at the fabric.
    # Joint angles come from probe_e3.py (solved so the hands land where intended).
    R = math.radians
    pose = [  # frame, spine lift (m), spine pitch (+ = back), shoulder pitch (+ = arm up), elbow pitch (+ = bend up)
        (1, 0.0, 0, 0, 0), (HIT, 0.0, 0, 0, 0),
        (HIT + 5, 0.055, 9, *FLINCH), (HIT + 9, 0.05, 7, *FLINCH),
        (HIT + 20, 0.02, -16, *GRAB), (HIT + 26, 0.015, -18, *TUG),
    ]
    f, up = HIT + 32, False
    while f <= 228:   # tugging the sweatpants away from the skin, slowing down
        pose.append((f, 0.012, -18 + (1.5 if up else 0), *(TUG if up else GRAB)))
        f += 6 if f < 180 else 9; up = not up
    pose.append((240, 0.01, -17, *GRAB))
    for fr, lift, pitch, sh_p, el_p in pose:
        key(spine, 'location', fr, Vector((0, -0.14, 0.6 + lift)))
        key(spine, 'rotation_euler', fr, Vector((R(pitch), 0, 0)))
        for sh, el in zip(shoulders, elbows):
            key(sh, 'rotation_euler', fr, Vector((R(sh_p), 0, 0)))
            key(el, 'rotation_euler', fr, Vector((R(el_p), 0, 0)))
    for t in thighs:
        t.color = (0.26, 0.26, 0.27, 1); t.keyframe_insert('color', frame=SOAK_A)
        t.color = (0.42, 0.15, 0.03, 1); t.keyframe_insert('color', frame=SOAK_B)
    # cup between the knees, on a pivot at its near bottom edge so it tips toward her
    base_z = 0.6
    pivot = bpy.data.objects.new('cup_pivot', None); bpy.context.collection.objects.link(pivot)
    pivot.location = (0, 0.37, base_z)
    bpy.ops.mesh.primitive_cone_add(radius1=0.028, radius2=0.039, depth=0.105, vertices=48, location=(0, 0.40, base_z + 0.0525))
    cup = bpy.context.object; cup.data.materials.append(clay('paper', PAPER, 0.55)); bpy.ops.object.shade_smooth()
    cup.parent = pivot; cup.matrix_parent_inverse = pivot.matrix_world.inverted()
    hinge = bpy.data.objects.new('lid_hinge', None); bpy.context.collection.objects.link(hinge)
    hinge.location = (0, 0.40 - 0.04, base_z + 0.111)
    hinge.parent = pivot; hinge.matrix_parent_inverse = pivot.matrix_world.inverted()
    lid = cyl('lid', 0.0415, 0.012, (0, 0.40, base_z + 0.111), clay('lidmat', (0.05, 0.05, 0.055), 0.4), verts=48)
    lid.parent = hinge; lid.matrix_parent_inverse = hinge.matrix_world.inverted()
    surf = cyl('coffee_surface', 0.036, 0.004, (0, 0.40, base_z + 0.1), amber('coffee_top', 1.4), verts=48)
    surf.parent = pivot; surf.matrix_parent_inverse = pivot.matrix_world.inverted()
    hinge.rotation_euler = (0, 0, 0); hinge.keyframe_insert('rotation_euler', frame=LID_A)
    hinge.rotation_euler = (math.radians(70), 0, 0); hinge.keyframe_insert('rotation_euler', frame=LID_B)
    pivot.scale = (1.25, 1.25, 1.25)
    pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert('rotation_euler', frame=TIP_A)
    pivot.rotation_euler = (math.radians(95), 0, 0); pivot.keyframe_insert('rotation_euler', frame=TIP_B)
    # coffee: droplets from the rim to the lap, then a spreading pool on the lap
    cof = amber('coffee', strength=3.0)
    for k in range(28):
        d = sphere(f'drop{k}', 0.026, (0, 0.3, 0.7), cof)
        f0 = TIP_A + 6 + k // 2
        key(d, 'scale', 1, Vector((0, 0, 0))); key(d, 'scale', f0, Vector((0, 0, 0)))
        key(d, 'location', f0, Vector((random.uniform(-0.02, 0.02), 0.3, 0.64)))
        key(d, 'scale', f0 + 1, Vector((1, 1, 1)))
        key(d, 'location', f0 + 10, Vector((random.uniform(-0.15, 0.15), random.uniform(0.0, 0.24), 0.71)))
        key(d, 'scale', f0 + 12, Vector((0, 0, 0)))
    studio(key_pos=(1.5, -0.8, 2.2), key_power=260, rim_pos=(-1.2, 1.2, 1.8), rim_power=140, size=1.5)
    end = round(DUR * FPS)
    cam, tgt = camera((0.6, 1.3, 1.7), (0, 0.28, 0.64), lens=46)
    key(cam, 'location', 1, Vector((0.6, 1.3, 1.7))); key(cam, 'location', 150, Vector((0.5, 1.16, 1.56)))
    for fr, dz in ((HIT + 2, 0.0), (HIT + 4, 0.018), (HIT + 6, -0.01), (HIT + 9, 0.004)):
        key(cam, 'location', fr, Vector((0.6 - 0.1 * fr / 150, 1.3 - 0.14 * fr / 150, 1.7 - 0.14 * fr / 150 + dz)))
    key(cam, 'location', end, Vector((0.3, 0.8, 1.12)))
    for fr, z in ((1, 0.64), (HIT - 4, 0.64), (HIT + 8, 0.76), (150, 0.66)):   # tilt up to catch the flinch
        key(tgt, 'location', fr, Vector((0, 0.28 - 0.06 * (fr > HIT), z)))
    key(tgt, 'location', end, Vector((0, 0.16, 0.66)))
    export_tracks('E3', {'cup': (0, 0.40, 0.72), 'lap': (0, 0.12, 0.7)})


if __name__ == '__main__':
    run('E3', build)
