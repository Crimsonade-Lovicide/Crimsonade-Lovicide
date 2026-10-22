"""Ep. 2 additions to the shared look: type set in Blender, steel, wood, spotlights aimed at a point."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', '..', 'ep01-hot-coffee', 'blender'))   # ep. 1 kit + shared common.py
from kit import *  # noqa: F401,F403

FONT_DIR = os.environ.get('FONT_DIR', os.path.join(_HERE, '..', '..', 'ep01-hot-coffee', 'fonts'))
WARNING = ('YOU HAVE THE RIGHT TO REMAIN SILENT.\nANYTHING YOU SAY CAN AND WILL BE USED\nAGAINST YOU IN A COURT OF LAW.\n'
           'YOU HAVE THE RIGHT TO AN ATTORNEY.\nIF YOU CANNOT AFFORD AN ATTORNEY,\nONE WILL BE APPOINTED FOR YOU.')
LAMP = (1.0, 0.82, 0.58)          # tungsten
SODIUM = (1.0, 0.58, 0.22)        # 1960s street lighting
NIGHT = (0.0025, 0.003, 0.006)


def steel(name='steel', color=(0.45, 0.46, 0.48), rough=0.38):
    return mat_principled(name, color, rough=rough, metallic=0.85)


def wood(name='wood', color=(0.28, 0.16, 0.08), rough=0.55):
    return mat_principled(name, color, rough=rough)


def text_obj(name, body, loc, size, mat, rot=(0, 0, 0), font='PlexMonoSemi.ttf', align='CENTER', spacing=1.25, extrude=0.0):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body
    cu.font = bpy.data.fonts.load(os.path.join(FONT_DIR, font), check_existing=True)
    cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'; cu.space_line = spacing; cu.extrude = extrude
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mat)
    return o


def spot(name, loc, target, energy, angle=40, blend=0.35, color=LAMP, size=0.05):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = energy; ld.color = color
    ld.spot_size = math.radians(angle); ld.spot_blend = blend; ld.shadow_soft_size = size
    o = bpy.data.objects.new(name, ld); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = look_rot(loc, target)
    return o


def chair(name, loc, facing, mat, seat=0.46, back=0.9, w=0.44):
    """Plain institutional chair; facing = angle (rad) the sitter faces."""
    parts = [box(f'{name}_seat', (w, w, 0.04), (0, 0, seat), mat),
             box(f'{name}_back', (w, 0.04, back - seat), (0, -w / 2, (seat + back) / 2), mat)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(box(f'{name}_leg', (0.03, 0.03, seat), (sx * (w / 2 - 0.03), sy * (w / 2 - 0.03), seat / 2), mat))
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
    o = parts[0]; o.name = name; o.location = (loc[0], loc[1], loc[2] + seat); o.rotation_euler = (0, 0, facing)
    return o


def night_ground(asphalt=0.035, walk=0.22, curb_y=0.0, size=60):
    box('asphalt', (size, size, 0.02), (0, curb_y + size / 2, -0.01), clay('asphalt', (asphalt,) * 3, 0.8))
    box('sidewalk', (size, 4, 0.15), (0, curb_y - 2, 0.075), clay('walk', (walk, walk, walk * 0.95), 0.85))
