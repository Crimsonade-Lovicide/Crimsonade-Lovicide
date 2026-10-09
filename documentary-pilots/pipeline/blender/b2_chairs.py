"""B2 - THE COUNT: a hall of 100 empty chairs; 38 ignite red (Brennan Center 2025: 38% threatened, harassed or abused)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import bmesh

DUR = 18.3
RED_START = 12.4      # s, during "Thirty-eight seats."
RED_SPAN = 3.0


def chair_mesh():
    bm = bmesh.new()
    def cube(sx, sy, sz, x, y, z):
        r = bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=r['verts'])
        bmesh.ops.translate(bm, vec=(x, y, z), verts=r['verts'])
    cube(.46, .44, .05, 0, 0, .46)                 # seat
    cube(.46, .045, .5, 0, .2, .74)                # back
    for x in (-.2, .2):
        for y in (-.19, .19):
            cube(.04, .04, .46, x, y, .23)         # legs
    me = bpy.data.meshes.new('chair'); bm.to_mesh(me); bm.free()
    return me


def build():
    random.seed(38)
    setup('B2', DUR, samples=8, world=(0.001, 0.0012, 0.0016), glare=0.9)
    bpy.ops.mesh.primitive_plane_add(size=120); fl = bpy.context.object
    fl.data.materials.append(mat_principled('floor', (0.02, 0.021, 0.024), rough=0.22))
    me = chair_mesh(); me.materials.append(mat_principled('chair', (0.32, 0.32, 0.34), rough=0.5))
    light('AREA', (0, -14, 6), 900, (.7, .78, 1), size=12, rot=(math.radians(65), 0, 0))
    disc_mat = mat_emit('redpool', (1.0, 0.012, 0.008), strength=1.6)
    reds = set(random.sample(range(100), 38))
    order = list(reds); random.shuffle(order)
    sp = 1.55
    for i in range(100):
        r, c = divmod(i, 10)
        x, y = (c - 4.5) * sp, (r - 4.5) * sp
        o = bpy.data.objects.new(f'chair{i}', me); bpy.context.collection.objects.link(o)
        o.location = (x + random.uniform(-.05, .05), y + random.uniform(-.05, .05), 0)
        o.rotation_euler = (0, 0, math.radians(180 + random.uniform(-5, 5)))
        if i in reds:
            k = order.index(i)
            f0 = round((RED_START + RED_SPAN * k / 38) * FPS)
            bpy.ops.mesh.primitive_circle_add(vertices=48, radius=.62, fill_type='NGON', location=(o.location.x, o.location.y, .003))
            d = bpy.context.object; d.data.materials.append(disc_mat)
            key(d, 'scale', 1, Vector((0.001, 0.001, 1))); key(d, 'scale', f0, Vector((0.001, 0.001, 1)))
            key(d, 'scale', f0 + 5, Vector((1, 1, 1)))
            L = light('POINT', (o.location.x, o.location.y, 1.6), 0, (1, .08, .05), size=.15)
            L.data.energy = 0; L.data.keyframe_insert('energy', frame=f0)
            L.data.energy = 18; L.data.keyframe_insert('energy', frame=f0 + 5)
    # pools of cold overhead light
    for x in (-4.5, 0, 4.5):
        for y in (-4.5, 0, 4.5):
            light('SPOT', (x, y, 7), 1400, (.75, .82, 1.0), size=.4).data.spot_size = math.radians(55)
    end = round(DUR * FPS)
    cam, tgt = camera((1.0, -10.5, 1.0), (0, -3, 0.7), lens=30)
    key(cam, 'location', 1, Vector((1.0, -10.5, 1.0))); key(tgt, 'location', 1, Vector((0, -3, .7)))
    key(cam, 'location', round(RED_START * FPS) - 10, Vector((0.4, -13.5, 5.0))); key(tgt, 'location', round(RED_START * FPS) - 10, Vector((0, -1, 0.3)))
    key(cam, 'location', end, Vector((0.0, -13.5, 12.5))); key(tgt, 'location', end, Vector((0, 0.3, 0)))
    export_tracks('B2', {'center': (0, 0, 0), 'front': (0, -8, 0)})


if __name__ == '__main__':
    run('B2', build)
