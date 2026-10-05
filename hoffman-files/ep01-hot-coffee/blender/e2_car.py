"""E2: a generic early-90s hatchback parked at dawn. Built from a side profile; not a modeled Ford Probe."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
import bmesh

DUR = 6


def extrude_profile(name, pts, width, mat, y=0.0):
    """pts = [(x, z), ...] side profile; extruded across the car's width along Y."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y - width / 2, z)) for x, z in pts]
    face = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, width, 0), verts=moved)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    me.materials.append(mat)
    return o


def build():
    setup('E2', DUR, samples=12, world=(0.012, 0.016, 0.03), glare=0.95)
    fl = stage((0.03, 0.03, 0.033))
    fl.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    body = clay('body', (0.5, 0.5, 0.48), 0.45)
    glass = mat_principled('glass', (0.01, 0.012, 0.016), rough=0.06)
    tire = clay('tire', (0.03, 0.03, 0.03), 0.8)
    lower = [(2.05, 0.28), (2.1, 0.62), (1.85, 0.78), (0.85, 0.92), (-1.85, 0.95), (-2.05, 0.82), (-2.08, 0.28)]
    bevel(extrude_profile('lower', lower, 1.7, body), 0.06)
    green = [(0.85, 0.92), (0.05, 1.27), (-0.95, 1.26), (-1.85, 0.95)]
    bevel(extrude_profile('greenhouse', green, 1.56, glass), 0.04)
    bevel(box('roof', (1.05, 1.5, 0.04), (-0.45, 0, 1.265), body), 0.02)
    bevel(box('bpillar', (0.12, 1.58, 0.3), (-0.6, 0, 1.12), body, rot=(0, math.radians(8), 0)), 0.02)
    for x in (1.3, -1.35):
        for y in (0.8, -0.8):
            cyl(f'wheel{x}{y}', 0.32, 0.22, (x, y, 0.32), tire, rot=(math.radians(90), 0, 0))
    lamp = mat_emit('lamp', (1, 0.15, 0.08), strength=3)
    for y in (0.6, -0.6):
        box(f'tail{y}', (0.04, 0.32, 0.1), (-2.09, y, 0.76), lamp)
    stripe = mat_principled('stripe', (0.6, 0.6, 0.58), rough=0.8)
    for y in (1.45, -1.45):
        box(f'line{y}', (5.0, 0.08, 0.005), (0, y, 0.003), stripe)
    light('SUN', (0, 0, 10), 2.0, (1.0, 0.62, 0.36), rot=(math.radians(70), 0, math.radians(-120)))
    light('AREA', (3, -4, 4), 350, (0.7, 0.8, 1.0), size=5, rot=look_rot((3, -4, 4), (0, 0, 0.8)))
    end = round(DUR * FPS)
    cam, tgt = camera((5.6, -4.6, 1.5), (0, 0, 0.75), lens=35)
    key(cam, 'location', 1, Vector((5.6, -4.6, 1.5))); key(cam, 'location', end, Vector((4.4, -5.4, 1.3)))


if __name__ == '__main__':
    run('E2', build)
