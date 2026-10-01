"""B4 - THE LONG ARM: dark globe with real Natural Earth coastlines; red arcs reach from the top three
perpetrator states toward host countries. Routes are illustrative (labelled as such on screen)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

DUR = 21.8
R = 3.0
ORIGINS = {'Beijing': (39.9, 116.4), 'Hanoi': (21.0, 105.8), 'Moscow': (55.75, 37.6)}
HOSTS = {'Bangkok': (13.75, 100.5), 'Phnom Penh': (11.55, 104.9), 'Vientiane': (17.97, 102.6),
         'Kuala Lumpur': (3.14, 101.7), 'Nairobi': (-1.29, 36.8), 'Kampala': (0.35, 32.6),
         'Dar es Salaam': (-6.8, 39.3), 'Istanbul': (41.0, 28.98), 'Dubai': (25.2, 55.3),
         'Berlin': (52.5, 13.4), 'London': (51.5, -0.13), 'Tbilisi': (41.7, 44.8),
         'Bishkek': (42.87, 74.6), 'Almaty': (43.2, 76.9), 'Jakarta': (-6.2, 106.8), 'Seoul': (37.57, 127.0)}
ROUTES = [('Beijing', h) for h in ('Bangkok', 'Phnom Penh', 'Vientiane', 'Kuala Lumpur', 'Nairobi', 'Istanbul', 'Dubai', 'Berlin', 'London', 'Bishkek', 'Almaty', 'Jakarta', 'Seoul')] + \
         [('Hanoi', h) for h in ('Bangkok', 'Phnom Penh', 'Vientiane', 'Kuala Lumpur', 'Berlin', 'Jakarta')] + \
         [('Moscow', h) for h in ('Istanbul', 'Berlin', 'London', 'Tbilisi', 'Bishkek', 'Almaty', 'Dubai')]
# regional collaboration inside East Africa (FH: majority of 2025 cases in SE Asia + East Africa)
ROUTES += [('Nairobi', 'Kampala'), ('Kampala', 'Nairobi'), ('Dar es Salaam', 'Nairobi'), ('Kampala', 'Dar es Salaam')]
ARCS_START, ARCS_END = 0.6, 11.0
PULSE = 14.6   # "China, Vietnam and Russia"


def xyz(lat, lon, r=R):
    la, lo = math.radians(lat), math.radians(lon)
    # Blender SPHERE projection: u = (1 - atan2(x, y)/pi)/2  ->  lon 0 at +Y, lon 90E at -X
    return Vector((-math.cos(la) * math.sin(lo) * r, math.cos(la) * math.cos(lo) * r, math.sin(la) * r))


def build():
    random.seed(126)
    setup('B4', DUR, samples=8, world=(0.0005, 0.0005, 0.0008), glare=0.7)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=R); g = bpy.context.object
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new('globe'); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    def img(path):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path)
        t.image.colorspace_settings.name = 'Non-Color'; t.projection = 'SPHERE'; t.interpolation = 'Cubic'
        nt.links.new(tc.outputs['Object'], t.inputs['Vector']); return t
    land, coast = img(f'{SCR}/blender/landmask.png'), img(f'{SCR}/blender/coast.png')
    ocean = nt.nodes.new('ShaderNodeBsdfPrincipled'); ocean.inputs['Base Color'].default_value = (0.004, 0.005, 0.008, 1)
    ocean.inputs['Roughness'].default_value = 0.35
    ground = nt.nodes.new('ShaderNodeBsdfPrincipled'); ground.inputs['Base Color'].default_value = (0.05, 0.052, 0.058, 1)
    ground.inputs['Roughness'].default_value = 0.9
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(land.outputs['Color'], mix.inputs[0]); nt.links.new(ocean.outputs[0], mix.inputs[1]); nt.links.new(ground.outputs[0], mix.inputs[2])
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.5, 0.58, 0.7, 1); em.inputs['Strength'].default_value = 0.9
    add = nt.nodes.new('ShaderNodeAddShader'); mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    nt.links.new(coast.outputs['Color'], em.inputs['Strength'])
    nt.links.new(mix.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs[0])
    g.data.materials.append(m)
    red = mat_emit('arc', (1.0, 0.04, 0.05), strength=7)
    dot_w = mat_emit('dotw', (0.85, 0.9, 1.0), strength=4)
    dots = {}
    for name, (la, lo) in {**ORIGINS, **HOSTS}.items():
        is_o = name in ORIGINS
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.045 if is_o else .028, location=xyz(la, lo, R + .01))
        d = bpy.context.object; d.data.materials.append(red if is_o else dot_w); dots[name] = d
        if is_o:
            f = round(PULSE * FPS) + list(ORIGINS).index(name) * 10
            key(d, 'scale', f, Vector((1, 1, 1))); key(d, 'scale', f + 8, Vector((2.2, 2.2, 2.2)))
    f_a, f_b = round(ARCS_START * FPS), round(ARCS_END * FPS)
    order = ROUTES[:]; random.shuffle(order)
    for i, (a, b) in enumerate(order):
        pa = {**ORIGINS, **HOSTS}[a]; pb = {**ORIGINS, **HOSTS}[b]
        va, vb = xyz(*pa).normalized(), xyz(*pb).normalized()
        ang = va.angle(vb); n = 40; pts = []
        for k in range(n + 1):
            t = k / n
            v = (va.slerp(vb, t) if hasattr(va, 'slerp') else (va * (1 - t) + vb * t)).normalized()
            pts.append(v * (R + 0.02 + math.sin(math.pi * t) * (0.15 + ang * 0.45)))
        cu = bpy.data.curves.new(f'arc{i}', 'CURVE'); cu.dimensions = '3D'
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for k, p in enumerate(pts): sp.points[k].co = (*p, 1)
        cu.bevel_depth = .009; cu.bevel_resolution = 2; cu.use_fill_caps = True
        cu.bevel_factor_mapping_end = 'SPLINE'
        o = bpy.data.objects.new(f'arc{i}', cu); bpy.context.collection.objects.link(o); cu.materials.append(red)
        f0 = round(f_a + (f_b - f_a) * i / len(order))
        cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=f0)
        cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=f0 + 22)
    light('AREA', (-6, -8, 6), 300, (.6, .7, 1), size=6, rot=(math.radians(60), 0, math.radians(-35)))
    end = round(DUR * FPS)
    cam, tgt = camera((0, 0, 0), (0, 0, 0), lens=50)
    for f, lo, la, d in ((1, 50, 30, 13.5), (round(end * .6), 85, 22, 12.0), (end, 105, 18, 10.8)):
        key(cam, 'location', f, xyz(la, lo, d))
    for f, lo, la in ((1, 50, 30), (round(end * .6), 85, 22), (end, 105, 18)):
        key(tgt, 'location', f, xyz(la, lo, 0.6))
    export_tracks('B4', {k: dots[k] for k in ORIGINS})


if __name__ == '__main__':
    run('B4', build)
