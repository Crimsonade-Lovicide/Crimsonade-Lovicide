"""Shared look for The Hoffman Files reconstructions: matte clay objects on a dark set, amber = coffee / heat."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
# common.py is shared with the pilot pipeline (documentary-pilots/pipeline/blender)
sys.path.insert(0, os.path.join(_HERE, '..', '..', '..', 'documentary-pilots', 'pipeline', 'blender'))
sys.path.insert(0, os.path.dirname(_HERE))
from common import *  # noqa: F401,F403  (setup, mat_*, box, camera, key, light, export_tracks, run, ...)

CLAY = (0.52, 0.52, 0.50)
CLAY_DARK = (0.16, 0.16, 0.17)
AMBER = (1.0, 0.42, 0.06)
PAPER = (0.86, 0.85, 0.82)


def clay(name='clay', color=CLAY, rough=0.75):
    return mat_principled(name, color, rough=rough)


def amber(name='amber', strength=2.5):
    return mat_emit(name, AMBER, strength=strength)


def object_color_mat(name, strength=0.0, rough=0.7):
    """Principled material whose base colour follows the object's colour (animatable per object)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    nt.links.new(oi.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if strength:
        nt.links.new(oi.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = strength
    return m


def glow_mat(name, color, strength, alpha):
    """Emission mixed with transparency, for steam and heat fronts."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*color, 1); em.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def stage(floor_color=(0.025, 0.025, 0.028), size=60):
    bpy.ops.mesh.primitive_plane_add(size=size); fl = bpy.context.object
    fl.data.materials.append(mat_principled('floor', floor_color, rough=0.35))
    return fl


def studio(key_pos=(-3, -4, 6), key_power=900, rim_pos=(3, 4, 4), rim_power=500, size=4):
    light('AREA', key_pos, key_power, (1.0, 0.97, 0.92), size=size,
          rot=look_rot(key_pos))
    light('AREA', rim_pos, rim_power, (0.75, 0.82, 1.0), size=size,
          rot=look_rot(rim_pos))


def look_rot(pos, target=(0, 0, 0.5)):
    d = Vector(target) - Vector(pos)
    return d.to_track_quat('-Z', 'Y').to_euler()


def bevel(o, width=0.02, segments=3):
    m = o.modifiers.new('bevel', 'BEVEL'); m.width = width; m.segments = segments
    return o


def cyl(name, r, depth, loc, mat=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name
    if mat: o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def sphere(name, r, loc, mat=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.object; o.name = name; o.scale = scale
    if mat: o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def capsule(name, p0, p1, r, mat):
    """A limb between two points: cylinder + rounded ends, joined into one object."""
    p0, p1 = Vector(p0), Vector(p1)
    mid, d = (p0 + p1) / 2, p1 - p0
    c = cyl(name, r, d.length, mid, mat)
    c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    a = sphere(name + '_a', r, p0, mat); b = sphere(name + '_b', r, p1, mat)
    bpy.ops.object.select_all(action='DESELECT')
    for o in (c, a, b): o.select_set(True)
    bpy.context.view_layer.objects.active = c
    bpy.ops.object.join()
    return c


def ease_all(obj, interp='BEZIER'):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = interp


def linear_all(obj):
    ease_all(obj, 'LINEAR')
