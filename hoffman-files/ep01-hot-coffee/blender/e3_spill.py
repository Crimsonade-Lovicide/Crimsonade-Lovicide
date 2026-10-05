"""E3: reconstruction of the spill. A stylized, faceless figure in a passenger seat holds the cup between
her knees, pulls the lid toward her, and the cup tips into her lap. Cut-away car, no likeness."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 10
LID_A, LID_B = 60, 100      # lid pulled toward her
TIP_A, TIP_B = 100, 122     # cup tips
SOAK_A, SOAK_B = 116, 200   # coffee spreads, sweatpants darken


def build():
    setup('E3', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.8)
    stage()
    seat = clay('seat', (0.2, 0.2, 0.21), 0.7)
    bevel(box('seat_base', (0.58, 0.6, 0.14), (0, -0.05, 0.46), seat), 0.05)
    bevel(box('seat_back', (0.58, 0.13, 0.78), (0, -0.4, 0.86), seat, rot=(math.radians(-12), 0, 0)), 0.05)
    box('floor_pan', (1.2, 1.6, 0.04), (0, 0.35, 0.06), clay('pan', (0.08, 0.08, 0.09)))
    skin = clay('figure', (0.62, 0.61, 0.59), 0.8)
    pants = object_color_mat('pants', rough=0.85)
    capsule('torso', (0, -0.16, 0.62), (0, -0.27, 1.1), 0.14, skin)
    sphere('head', 0.1, (0, -0.29, 1.32), skin, scale=(0.9, 1.0, 1.1))   # faceless by design
    thighs = []
    for s in (1, -1):
        t = capsule(f'thigh{s}', (0.1 * s, -0.1, 0.6), (0.1 * s, 0.32, 0.62), 0.078, pants); thighs.append(t)
        capsule(f'shin{s}', (0.1 * s, 0.34, 0.6), (0.1 * s, 0.42, 0.13), 0.06, pants)
        capsule(f'upperarm{s}', (0.19 * s, -0.22, 1.04), (0.2 * s, 0.0, 0.82), 0.045, skin)
        capsule(f'forearm{s}', (0.2 * s, 0.0, 0.82), (0.15 * s, 0.26, 0.72), 0.04, skin)
        sphere(f'hand{s}', 0.042, (0.15 * s, 0.29, 0.715), skin)
    for t in thighs:
        t.color = (0.5, 0.5, 0.49, 1); t.keyframe_insert('color', frame=SOAK_A)
        t.color = (0.16, 0.08, 0.035, 1); t.keyframe_insert('color', frame=SOAK_B)
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
    lid = cyl('lid', 0.0415, 0.012, (0, 0.40, base_z + 0.111), clay('lidmat', (0.7, 0.69, 0.67), 0.4), verts=48)
    lid.parent = hinge; lid.matrix_parent_inverse = hinge.matrix_world.inverted()
    surf = cyl('coffee_surface', 0.036, 0.004, (0, 0.40, base_z + 0.1), amber('coffee_top', 1.4), verts=48)
    surf.parent = pivot; surf.matrix_parent_inverse = pivot.matrix_world.inverted()
    hinge.rotation_euler = (0, 0, 0); hinge.keyframe_insert('rotation_euler', frame=LID_A)
    hinge.rotation_euler = (math.radians(70), 0, 0); hinge.keyframe_insert('rotation_euler', frame=LID_B)
    pivot.scale = (1.25, 1.25, 1.25)
    pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert('rotation_euler', frame=TIP_A)
    pivot.rotation_euler = (math.radians(95), 0, 0); pivot.keyframe_insert('rotation_euler', frame=TIP_B)
    # coffee: droplets from the rim to the lap, then a spreading pool on the lap
    cof = amber('coffee', strength=1.6)
    for k in range(16):
        d = sphere(f'drop{k}', 0.018, (0, 0.3, 0.7), cof)
        f0 = TIP_A + 8 + k
        key(d, 'scale', 1, Vector((0, 0, 0))); key(d, 'scale', f0, Vector((0, 0, 0)))
        key(d, 'location', f0, Vector((random.uniform(-0.02, 0.02), 0.3, 0.64)))
        key(d, 'scale', f0 + 1, Vector((1, 1, 1)))
        key(d, 'location', f0 + 10, Vector((random.uniform(-0.12, 0.12), random.uniform(0.02, 0.2), 0.71)))
        key(d, 'scale', f0 + 12, Vector((0, 0, 0)))
    studio(key_pos=(1.5, -0.8, 2.2), key_power=260, rim_pos=(-1.2, 1.2, 1.8), rim_power=140, size=1.5)
    end = round(DUR * FPS)
    cam, tgt = camera((0.55, 1.25, 1.65), (0, 0.28, 0.64), lens=40)
    key(cam, 'location', 1, Vector((0.6, 1.3, 1.7))); key(cam, 'location', end, Vector((0.45, 1.1, 1.5)))
    export_tracks('E3', {'cup': (0, 0.40, 0.72), 'lap': (0, 0.12, 0.7)})


if __name__ == '__main__':
    run('E3', build)
