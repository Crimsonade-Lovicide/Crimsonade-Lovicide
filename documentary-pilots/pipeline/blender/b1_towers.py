"""B1 - PINK SLIME: 1,213 daily newspapers vs 1,265 pink-slime sites as two stacked towers.
Each slab = 10 outlets. Both towers build at the same rate; white stops at 121, pink keeps going to 127."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

DUR = 17.6
WHITE, PINK = 121, 127
T = 0.075             # slab pitch
FIRST, RATE = 14, 2   # first landing frame, frames per slab


def landing(i):
    return FIRST + i * RATE


def build():
    random.seed(7)
    setup('B1', DUR, samples=16, glare=0.9)
    floor = bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0)); floor = bpy.context.object
    floor.data.materials.append(mat_principled('floor', (0.012, 0.012, 0.014), rough=0.28))
    paper = mat_principled('paper', (0.78, 0.77, 0.74), rough=0.85)
    pink = mat_principled('pink', (0.9, 0.18, 0.5), rough=0.6, emit=(1.0, 0.16, 0.52), emit_strength=0.9)
    for n, x, mat in ((WHITE, -1.35, paper), (PINK, 1.35, pink)):
        for i in range(n):
            z = T * i + T / 2
            o = box(f's{x}_{i}', (1.55, 1.1, T * 0.82), (x + random.uniform(-.035, .035), random.uniform(-.03, .03), z),
                    mat, rot=(0, 0, math.radians(random.uniform(-4, 4))))
            f = landing(i)
            key(o, 'location', f - 7, Vector((o.location.x, o.location.y, z + 2.2)))
            key(o, 'location', f, Vector((o.location.x, o.location.y, z)))
            o.hide_render = True; o.keyframe_insert('hide_render', frame=f - 8)
            o.hide_render = False; o.keyframe_insert('hide_render', frame=f - 7)
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if fc.data_path == 'hide_render' else 'QUAD'
            if i == 0:
                # hide before first keyframe too
                o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    light('AREA', (0, -3, 16), 2600, (1, .97, .92), size=7)
    light('AREA', (0, 7, 7), 900, (.45, .6, 1.0), size=6, rot=(math.radians(-60), 0, 0))
    light('POINT', (3.6, -1.5, 3), 300, (1, .2, .55), size=1.5)
    end = round(DUR * FPS)
    cam, tgt = camera((0.5, -13.5, 1.4), (0, 0, 1.6), lens=38)
    top_w, top_p = T * WHITE, T * PINK
    key(cam, 'location', 1, Vector((0.5, -13.5, 1.4))); key(tgt, 'location', 1, Vector((0, 0, 1.6)))
    key(cam, 'location', landing(PINK), Vector((-0.6, -11.5, top_p + 0.3))); key(tgt, 'location', landing(PINK), Vector((0, 0, top_p - 1.4)))
    key(cam, 'location', end, Vector((-1.4, -6.2, top_p + 1.2))); key(tgt, 'location', end, Vector((0.2, 0, top_p - 0.4)))
    export_tracks('B1', {'white_top': (-1.35, 0, top_w + .1), 'pink_top': (1.35, 0, top_p + .1),
                         'white_base': (-1.35, -0.6, 0), 'pink_base': (1.35, -0.6, 0)})


if __name__ == '__main__':
    run('B1', build)
