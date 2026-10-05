"""E1 cold open: an unbranded paper cup on a dashboard at dawn, steam rising. No logos."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 8


def sky_mat():
    m = bpy.data.materials.new('sky'); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.9, 0.36, 0.08, 1)
    ramp.color_ramp.elements[1].position = 0.55; ramp.color_ramp.elements[1].color = (0.03, 0.05, 0.12, 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Y'], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs['Color']); em.inputs['Strength'].default_value = 1.4
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def build():
    setup('E1', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.7)
    dash = box('dash', (2.4, 0.8, 0.12), (0, 0.1, 0.9), clay('dash', (0.03, 0.03, 0.032), 0.9)); bevel(dash, 0.05)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1.3, 1.25), rotation=(math.radians(75), 0, 0))
    sky = bpy.context.object; sky.scale = (5, 2.2, 1); sky.data.materials.append(sky_mat())
    for x in (-1.05, 1.05):  # windshield pillars
        box(f'pillar{x}', (0.06, 0.06, 0.9), (x, 0.55, 1.35), clay('pillar', CLAY_DARK), rot=(math.radians(-25), 0, 0))
    top = 0.96
    bpy.ops.mesh.primitive_cone_add(radius1=0.028, radius2=0.039, depth=0.105, vertices=48, location=(0.04, 0.0, top + 0.0525))
    cup = bpy.context.object; cup.data.materials.append(clay('paper', PAPER, 0.55)); bpy.ops.object.shade_smooth()
    lid = cyl('lid', 0.0415, 0.012, (0.04, 0.0, top + 0.111), clay('lidmat', (0.7, 0.69, 0.67), 0.4), verts=48)
    box('sip', (0.016, 0.006, 0.004), (0.04, -0.03, top + 0.118), clay('hole', (0.05, 0.05, 0.05)))
    steam = glow_mat('steam', (1, 0.97, 0.94), 0.5, 0.8)
    for i in range(6):
        cu = bpy.data.curves.new(f'steam{i}', 'CURVE'); cu.dimensions = '3D'
        sp = cu.splines.new('NURBS'); n = 12; sp.points.add(n - 1); sp.order_u = 4; sp.use_endpoint_u = True; cu.resolution_u = 8
        ph = random.uniform(0, 6.28)
        for k in range(n):
            t = k / (n - 1)
            sp.points[k].co = (0.006 * math.sin(t * 4 + ph), 0.004 * math.cos(t * 3 + ph), t * 0.08, 1)
        cu.bevel_depth = 0.0011; cu.materials.append(steam)
        o = bpy.data.objects.new(f'steam{i}', cu); bpy.context.collection.objects.link(o)
        base = Vector((0.04 + random.uniform(-0.012, 0.012), random.uniform(-0.01, 0.01), top + 0.118))
        f0 = 1 + i * 10
        key(o, 'location', f0, base); key(o, 'scale', f0, Vector((1, 1, 0.6)))
        key(o, 'location', f0 + 60, base + Vector((0, 0, 0.09))); key(o, 'scale', f0 + 60, Vector((0.2, 0.2, 1.4)))
        for fc in o.animation_data.action.fcurves:
            fc.modifiers.new('CYCLES')
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    light('AREA', (-0.8, -0.9, 1.6), 25, (1.0, 0.95, 0.9), size=0.8, rot=look_rot((-0.8, -0.9, 1.6), (0.04, 0, 1.0)))
    light('AREA', (0.1, 0.6, 1.25), 25, (1.0, 0.6, 0.3), size=0.6, rot=look_rot((0.1, 0.6, 1.25), (0.04, 0, 1.03)))
    end = round(DUR * FPS)
    cam, tgt = camera((0.02, -0.62, 1.08), (0.04, 0.0, 1.05), lens=55)
    key(cam, 'location', 1, Vector((0.02, -0.62, 1.1))); key(cam, 'location', end, Vector((0.05, -0.47, 1.08)))
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 2.8


if __name__ == '__main__':
    run('E1', build)
