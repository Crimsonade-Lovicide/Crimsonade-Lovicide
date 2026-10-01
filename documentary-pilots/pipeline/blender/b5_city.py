"""B5 - BROKERED: a city grid of moving phones. One red dot is followed home -> place of worship -> clinic -> protest.
Then the protesters turn red and lines trace each one back to where they live (FTC allegation vs Mobilewalla)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

DUR = 24.0
N = 14            # blocks per side
P = 4.0           # block pitch (block 3 + street 1)
HALF = N * P / 2


def node(i, j):   # street intersection coordinates
    return Vector((-HALF + i * P, -HALF + j * P, 0.12))


def block_center(i, j):
    return Vector((-HALF + i * P + P / 2, -HALF + j * P + P / 2, 0))


HOME, CHURCH, CLINIC, PLAZA = (3, 3), (5, 8), (9, 6), (10, 10)   # block indices
PLAZA_C = block_center(*PLAZA) + Vector((P / 2, P / 2, 0))        # plaza spans 2x2 blocks
STOPS = [(HOME, 0.4, 2.4), (CHURCH, 4.6, 6.0), (CLINIC, 8.2, 9.6), (PLAZA, 11.6, 24)]  # (block, arrive s, leave s)
CROWD_RED = 14.4       # "Another, the FTC alleged, analyzed people at the George Floyd protests"
LINES_START = 16.0     # "...by race, and by where they lived."


def manhattan(a, b):
    """path along streets from point a to b (Vectors): go along x, then y."""
    return [a, Vector((b.x, a.y, a.z)), b]


def build():
    random.seed(17)
    setup('B5', DUR, samples=8, world=(0.004, 0.005, 0.009), glare=0.7)
    bpy.ops.mesh.primitive_plane_add(size=N * P + 40); fl = bpy.context.object
    fl.data.materials.append(mat_principled('street', (0.018, 0.02, 0.026), rough=0.5))
    bmat = mat_principled('bldg', (0.07, 0.075, 0.09), rough=0.6)
    special = {HOME: (0.6, 1.2), CHURCH: (0.8, 3.6), CLINIC: (2.4, 1.6)}
    plaza_blocks = {(PLAZA[0] + a, PLAZA[1] + b) for a in (0, 1) for b in (0, 1)}
    for i in range(N):
        for j in range(N):
            if (i, j) in plaza_blocks: continue
            c = block_center(i, j)
            if (i, j) in special:
                w, h = special[(i, j)]
                box(f'sp{i}{j}', (w if (i, j) != CHURCH else .8, w if (i, j) != CHURCH else .8, h), (c.x, c.y, h / 2), bmat)
                continue
            for a in (-0.75, 0.75):
                for b in (-0.75, 0.75):
                    if random.random() < .2: continue
                    h = random.uniform(.3, 2.8) * (1.4 if abs(c.x) < 12 and abs(c.y) < 12 else 1)
                    box(f'b{i}{j}{a}{b}', (1.25, 1.25, h), (c.x + a, c.y + b, h / 2), bmat)
    # plaza: faint ground marking
    bpy.ops.mesh.primitive_plane_add(size=P * 2 - 1, location=(PLAZA_C.x, PLAZA_C.y, .01))
    bpy.context.object.data.materials.append(mat_principled('plaza', (0.05, 0.05, 0.06), rough=.6))
    end = round(DUR * FPS)
    dot_mat = mat_emit('dots', None, strength=5, use_object_color=True)
    WHITE, RED = (0.75, 0.82, 1.0, 1), (1.0, 0.05, 0.04, 1)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.13, segments=12, ring_count=8); proto = bpy.context.object
    dme = proto.data; dme.materials.append(dot_mat); bpy.data.objects.remove(proto)
    def dot(name, col):
        o = bpy.data.objects.new(name, dme); bpy.context.collection.objects.link(o); o.color = col; return o
    # wandering phones
    for k in range(170):
        o = dot(f'w{k}', WHITE)
        i, j = random.randrange(N + 1), random.randrange(N + 1)
        t = 1; pos = node(i, j); key(o, 'location', 1, pos)
        while t < end:
            if random.random() < .5: i = max(0, min(N, i + random.choice((-1, 1))))
            else: j = max(0, min(N, j + random.choice((-1, 1))))
            nxt = node(i, j); t += random.randint(20, 40); key(o, 'location', min(t, end), nxt)
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # protest crowd: converge on plaza, then turn red; lines back to their homes
    crowd = []
    line_mat = mat_emit('trace', (1, .06, .05), strength=3.5)
    for k in range(46):
        o = dot(f'c{k}', WHITE)
        hi, hj = random.randrange(N), random.randrange(N)
        while (hi, hj) in plaza_blocks: hi, hj = random.randrange(N), random.randrange(N)
        home = block_center(hi, hj) + Vector((random.uniform(-1, 1), random.uniform(-1, 1), .5))
        spot = PLAZA_C + Vector((random.uniform(-3.2, 3.2), random.uniform(-3.2, 3.2), .12))
        start = node(random.randrange(N + 1), random.randrange(N + 1))
        arrive = random.uniform(5, 12.5) * FPS
        key(o, 'location', 1, start); key(o, 'location', round(arrive), spot)
        key(o, 'location', end, spot + Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), 0)))
        f_red = round((CROWD_RED + random.uniform(0, 1.2)) * FPS)
        o.keyframe_insert('color', frame=f_red); o.color = RED; o.keyframe_insert('color', frame=f_red + 4)
        # trace line from protester to home
        cu = bpy.data.curves.new(f'tr{k}', 'CURVE'); cu.dimensions = '3D'
        mid = (spot + home) / 2 + Vector((0, 0, (spot - home).length * .08))
        sp = cu.splines.new('POLY'); pts = []
        for q in range(25):
            t = q / 24; pts.append(spot * (1 - t) ** 2 + mid * 2 * t * (1 - t) + home * t * t)
        sp.points.add(len(pts) - 1)
        for q, pp in enumerate(pts): sp.points[q].co = (*pp, 1)
        cu.bevel_depth = .022; cu.bevel_factor_mapping_end = 'SPLINE'; cu.materials.append(line_mat)
        lo = bpy.data.objects.new(f'tr{k}', cu); bpy.context.collection.objects.link(lo)
        f0 = round((LINES_START + random.uniform(0, 2.5)) * FPS)
        cu.bevel_factor_end = 0; cu.keyframe_insert('bevel_factor_end', frame=f0)
        cu.bevel_factor_end = 1; cu.keyframe_insert('bevel_factor_end', frame=f0 + 18)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.16, segments=12, ring_count=8, location=home)
        hm = bpy.context.object; hm.data.materials.append(line_mat)
        key(hm, 'scale', 1, Vector((0, 0, 0))); key(hm, 'scale', f0 + 16, Vector((0, 0, 0))); key(hm, 'scale', f0 + 20, Vector((1, 1, 1)))
    # the tracked red dot + its trail
    target = dot('target', RED); target.scale = (2.4, 2.4, 2.4)
    pts = []; keys = []
    prev = None
    for blk, t_in, t_out in STOPS:
        c = (PLAZA_C if blk == PLAZA else block_center(*blk)) + Vector((0, -P / 2 + .02 if blk != PLAZA else 0, .14))
        if blk != PLAZA: c = Vector((c.x, -HALF + blk[1] * P, .14))   # stop on the street in front of the block
        if prev is not None:
            path = manhattan(prev, c)
            pts += path[1:]
        else:
            pts.append(c)
        keys.append((t_in, c)); keys.append((min(t_out, DUR), c)); prev = c
    # keyframe the dot along its street path, constant speed between stops
    seq = [(STOPS[0][1], keys[0][1])]
    for s_idx in range(1, len(STOPS)):
        a = keys[2 * s_idx - 1]; b = keys[2 * s_idx]
        mid = Vector((b[1].x, a[1].y, .14))
        la, lb = (mid - a[1]).length, (b[1] - mid).length
        tm = a[0] + (b[0] - a[0]) * la / max(la + lb, 1e-6)
        seq += [a, (tm, mid), b]
    seq.append(keys[-1])
    key(target, 'location', 1, seq[0][1])
    for t, p in seq: key(target, 'location', max(1, round(t * FPS)), p)
    for fc in target.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # trail curve following the same path; bevel end keyed on cumulative length
    cum = [0.0]
    for q in range(1, len(seq)): cum.append(cum[-1] + (seq[q][1] - seq[q - 1][1]).length)
    cu = bpy.data.curves.new('trail', 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(seq) - 1)
    for q, (_, p) in enumerate(seq): sp.points[q].co = (p.x, p.y, .06, 1)
    cu.bevel_depth = .05; cu.bevel_factor_mapping_end = 'SPLINE'; cu.materials.append(line_mat)
    tro = bpy.data.objects.new('trail', cu); bpy.context.collection.objects.link(tro)
    for (t, _), L in zip(seq, cum):
        cu.bevel_factor_end = L / cum[-1]; cu.keyframe_insert('bevel_factor_end', frame=max(1, round(t * FPS)))
    for fc in cu.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    # pulse rings at each stop
    ring_mat = mat_emit('ring', (1, .1, .08), strength=4)
    for blk, t_in, _ in STOPS:
        p = [k[1] for k in keys][[s[0] for s in STOPS].index(blk) * 2]
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=.03, location=(p.x, p.y, .1))
        r = bpy.context.object; r.data.materials.append(ring_mat)
        f = round(t_in * FPS)
        key(r, 'scale', 1, Vector((0, 0, 0))); key(r, 'scale', f, Vector((0.1, 0.1, 1)))
        key(r, 'scale', f + 14, Vector((1.6, 1.6, 1))); key(r, 'scale', f + 15, Vector((0, 0, 0)))
    light('AREA', (0, 0, 30), 30000, (.55, .65, 1), size=40)
    light('SUN', (0, 0, 10), 0.35, (.6, .7, 1), rot=(math.radians(50), 0, math.radians(30)))
    # camera: follow the red dot, then pull up over the whole city
    cam, tgt = camera((0, 0, 0), (0, 0, 0), lens=35)
    follow_until = 12.6
    for t in (0.0, 2.4, 4.6, 6.0, 8.2, 9.6, 11.6, follow_until):
        tgt_loc = None
        for q in range(1, len(seq)):
            if seq[q][0] >= t:
                (ta, pa), (tb, pb) = seq[q - 1], seq[q]
                u = 0 if tb == ta else (t - ta) / (tb - ta); tgt_loc = pa.lerp(pb, max(0, min(1, u))); break
        tgt_loc = tgt_loc or seq[-1][1]
        f = max(1, round(t * FPS))
        key(tgt, 'location', f, tgt_loc); key(cam, 'location', f, tgt_loc + Vector((-1, -4.5, 14)))
    key(tgt, 'location', end, Vector((PLAZA_C.x * .3, PLAZA_C.y * .3, 0)))
    key(cam, 'location', end, Vector((PLAZA_C.x * .3 - 4, PLAZA_C.y * .3 - 40, 52)))
    export_tracks('B5', {'home': keys[0][1], 'church': keys[2][1], 'clinic': keys[4][1], 'plaza': keys[6][1], 'dot': target})


if __name__ == '__main__':
    run('B5', build)
