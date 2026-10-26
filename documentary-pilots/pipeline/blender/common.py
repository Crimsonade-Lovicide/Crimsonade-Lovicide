import bpy, math, json, os, sys, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

SCR = os.environ.get('PILOT_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FPS = 24


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup(name, seconds, samples=14, res=None, world=(0.002, 0.002, 0.003), glare=0.6):
    glare = glare if os.environ.get('GLARE', '1') == '1' else 0
    s = bpy.context.scene
    res = res or tuple(int(v) for v in os.environ.get('RES', '960x540').split('x'))
    samples = int(os.environ.get('SAMPLES', samples))
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = True
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 4
    s.cycles.diffuse_bounces = 1
    s.cycles.use_auto_tile = False
    s.render.threads_mode = 'AUTO'
    s.cycles.glossy_bounces = 2
    s.cycles.transmission_bounces = 0
    s.cycles.volume_bounces = 0
    s.render.use_persistent_data = True
    s.render.fps = FPS
    s.frame_start = 1
    s.frame_end = round(seconds * FPS)
    s.render.resolution_x, s.render.resolution_y = res
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Punchy'
    s.render.image_settings.file_format = 'PNG'
    s.render.filepath = f'{SCR}/renders/{name}/'
    w = bpy.data.worlds.new('W'); s.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (*world, 1)
    if glare:
        s.use_nodes = True
        nt = s.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        rl = nt.nodes.new('CompositorNodeRLayers')
        gl = nt.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'
        gl.threshold = glare; gl.size = 7; gl.quality = 'LOW'
        co = nt.nodes.new('CompositorNodeComposite')
        nt.links.new(rl.outputs['Image'], gl.inputs['Image'])
        nt.links.new(gl.outputs['Image'], co.inputs['Image'])
    return s


def mat_principled(name, color, rough=0.5, emit=None, emit_strength=0.0, metallic=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_strength
    return m


def mat_emit(name, color, strength=4.0, use_object_color=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = strength
    if use_object_color:
        oi = nt.nodes.new('ShaderNodeObjectInfo')
        nt.links.new(oi.outputs['Color'], em.inputs['Color'])
    else:
        em.inputs['Color'].default_value = (*color, 1)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def box(name, size, loc, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat: o.data.materials.append(mat)
    return o


def camera(loc, target_loc, lens=35):
    cd = bpy.data.cameras.new('Cam'); cd.lens = lens
    cam = bpy.data.objects.new('Cam', cd); bpy.context.collection.objects.link(cam)
    tgt = bpy.data.objects.new('Target', None); bpy.context.collection.objects.link(tgt)
    tgt.location = target_loc; cam.location = loc
    c = cam.constraints.new('TRACK_TO'); c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam, tgt


def key(obj, path, frame, value, interp=None):
    setattr(obj, path, value) if not isinstance(value, (tuple, list, Vector)) else setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)
    if interp:
        ad = obj.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                if fc.data_path == path:
                    for kp in fc.keyframe_points:
                        if kp.co[0] == frame: kp.interpolation = interp


def light(kind, loc, energy, color=(1, 1, 1), size=1.0, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(f'L_{kind}', kind); ld.energy = energy; ld.color = color
    if kind == 'AREA': ld.size = size
    elif kind in ('POINT', 'SPOT'): ld.shadow_soft_size = size
    o = bpy.data.objects.new(ld.name, ld); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o


def export_tracks(name, points):
    """points: {label: Vector or object}; writes per-frame normalized screen coords (x, y from top-left)."""
    s = bpy.context.scene; cam = s.camera; out = {}
    for f in range(s.frame_start, s.frame_end + 1):
        s.frame_set(f); row = {}
        for k, p in points.items():
            loc = p.matrix_world.translation if hasattr(p, 'matrix_world') else Vector(p)
            v = world_to_camera_view(s, cam, loc)
            row[k] = (round(v.x, 4), round(1 - v.y, 4), round(v.z, 3))
        out[f] = row
    os.makedirs(f'{SCR}/renders', exist_ok=True)
    json.dump(out, open(f'{SCR}/renders/{name}_tracks.json', 'w'))
    s.frame_set(s.frame_start)


def render(name, still=None):
    s = bpy.context.scene
    os.makedirs(f'{SCR}/renders/{name}', exist_ok=True)
    if still:
        s.frame_set(still)
        s.render.filepath = f'{SCR}/renders/{name}_still_{still}.png'
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)


def run(name, build):
    """CLI: python3 sceneX.py [still FRAME | anim [start end]]"""
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    reset(); build()
    bpy.ops.wm.save_as_mainfile(filepath=f'{SCR}/blender/{name}.blend')
    mode = args[0] if args else 'still'
    if mode == 'still':
        for f in args[1:] or ['1']:
            render(name, still=int(f))
    elif mode == 'anim':
        s = bpy.context.scene
        if len(args) >= 3: s.frame_start, s.frame_end = int(args[1]), int(args[2])
        s.frame_step = int(os.environ.get('STEP', '1'))
        render(name)
