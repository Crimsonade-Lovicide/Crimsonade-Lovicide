"""B3 - SERVER NATION: a 275-seat hemicycle (Nepal House of Representatives size) made of chat-pixel blocks.
Seats light up blue as the Discord poll fills; a central light brightens at the swearing-in."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

DUR = 21.6
SEATS = 275
LIGHT_START, LIGHT_END = 1.0, 15.0     # seats fill across both VO lines
SWORN = 16.0                            # "sworn in ... September twelfth"
DIM = (0.012, 0.016, 0.03, 1)
LIT = (0.16, 0.38, 1.0, 1)


def build():
    random.seed(275)
    setup('B3', DUR, samples=8, world=(0.0008, 0.001, 0.002), glare=0.8)
    bpy.ops.mesh.primitive_plane_add(size=120); fl = bpy.context.object
    fl.data.materials.append(mat_principled('floor', (0.01, 0.011, 0.016), rough=0.18))
    seat_mat = mat_emit('seat', None, strength=3.0, use_object_color=True)
    # build rows; seats per row proportional to radius
    rows = 9; radii = [3.2 + 0.62 * r for r in range(rows)]
    arc = math.radians(200)
    weights = [r for r in radii]; tot = sum(weights)
    counts = [round(SEATS * w / tot) for w in weights]
    counts[-1] += SEATS - sum(counts)
    bpy.ops.mesh.primitive_cube_add(size=0.3); proto = bpy.context.object
    bev = proto.modifiers.new('b', 'BEVEL'); bev.width = .06; bev.segments = 3
    bpy.ops.object.modifier_apply(modifier='b')
    me = proto.data; me.materials.append(seat_mat); bpy.data.objects.remove(proto)
    seats = []
    for r, (rad, n) in enumerate(zip(radii, counts)):
        for k in range(n):
            a = -arc / 2 + arc * (k + .5) / n
            o = bpy.data.objects.new(f'seat{r}_{k}', me); bpy.context.collection.objects.link(o)
            o.location = (rad * math.sin(a), -rad * math.cos(a) * -1 + 0.0, 0.18 + r * 0.16)
            o.rotation_euler = (0, 0, a)
            seats.append(o)
    order = seats[:]; random.shuffle(order)
    f_a, f_b = round(LIGHT_START * FPS), round(LIGHT_END * FPS)
    for i, o in enumerate(order):
        f = f_a + (f_b - f_a) * (i / SEATS) ** 0.8
        o.color = DIM; o.keyframe_insert('color', frame=1); o.keyframe_insert('color', frame=round(f))
        o.color = LIT; o.keyframe_insert('color', frame=round(f) + 4)
    # rising message bits
    bit_mat = mat_emit('bit', (0.4, 0.6, 1.0), strength=2.5)
    end = round(DUR * FPS)
    for i in range(90):
        a = random.uniform(-arc / 2, arc / 2); rad = random.uniform(3, 9)
        x, y = rad * math.sin(a), rad * math.cos(a)
        bpy.ops.mesh.primitive_cube_add(size=random.uniform(.04, .09), location=(x, y, 0))
        b = bpy.context.object; b.data.materials.append(bit_mat)
        t0 = random.uniform(-end, end)
        key(b, 'location', 1, Vector((x, y, max(0, -t0 / end * 6))))
        key(b, 'location', end, Vector((x, y, (end - t0) / end * 6)))
        for fc in b.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # central podium light (the interim leader)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.28, location=(0, 0, .5)); pod = bpy.context.object
    pm = mat_emit('pod', (1, .95, .9), strength=0.3); pod.data.materials.append(pm)
    em = pm.node_tree.nodes['Emission'].inputs['Strength']
    em.default_value = 0.3; em.keyframe_insert('default_value', frame=round(SWORN * FPS) - 2)
    em.default_value = 40; em.keyframe_insert('default_value', frame=round(SWORN * FPS) + 10)
    L = light('POINT', (0, 0, 1.2), 0, (1, .92, .85), size=.3)
    L.data.energy = 0; L.data.keyframe_insert('energy', frame=round(SWORN * FPS) - 2)
    L.data.energy = 400; L.data.keyframe_insert('energy', frame=round(SWORN * FPS) + 10)
    light('AREA', (0, 2, 12), 500, (.6, .7, 1), size=10)
    # camera orbit around the chamber
    cam, tgt = camera((0, 0, 0), (0, 2.2, 0.6), lens=30)
    for f, ang, rad, h in ((1, -38, 15, 7.5), (round(DUR * FPS * .55), -10, 13.5, 5.5), (end, 14, 11.5, 4.2)):
        a = math.radians(ang)
        key(cam, 'location', f, Vector((rad * math.sin(a), -rad * math.cos(a), h)))
    export_tracks('B3', {'podium': (0, 0, .6), 'top': (0, 8.4, 1.8)})


if __name__ == '__main__':
    run('B3', build)
