"""M3: Interrogation Room No. 2 (layout illustrative). One table, a chair each side, a hanging lamp, a door
marked 2, and a wall clock whose hands run two hours over the shot. Empty."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit2 import *

DUR = 12
W, D, H = 3.0, 3.6, 2.6        # room width (x), depth (y), height


def build():
    setup('M3', DUR, samples=16, world=(0.0, 0.0, 0.0), glare=0.75)
    wall = clay('wall', (0.38, 0.42, 0.37), 0.85)
    box('floor', (W, D, 0.02), (0, 0, -0.01), clay('floor', (0.16, 0.17, 0.15), 0.6))
    box('ceiling', (W, D, 0.02), (0, 0, H + 0.01), clay('ceil', (0.35, 0.35, 0.33), 0.9))
    box('wall_back', (W, 0.06, H), (0, D / 2, H / 2), wall)
    box('wall_left', (0.06, D, H), (-W / 2, 0, H / 2), wall)
    box('wall_right', (0.06, D, H), (W / 2, 0, H / 2), wall)
    box('wall_front', (W, 0.06, H), (0, -D / 2, H / 2), wall)
    box('baseboard', (W, 0.02, 0.12), (0, D / 2 - 0.04, 0.06), clay('base', (0.08, 0.08, 0.08), 0.7))
    # door on the back wall, small wired-glass window, number 2
    door = box('door', (0.9, 0.05, 2.05), (0.75, D / 2 - 0.04, 1.025), clay('door', (0.22, 0.2, 0.17), 0.7))
    box('door_window', (0.3, 0.02, 0.4), (0.75, D / 2 - 0.07, 1.55), mat_principled('wglass', (0.25, 0.28, 0.3), rough=0.2))
    text_obj('door_no', '2', (0.75, D / 2 - 0.075, 1.15), 0.22, clay('paint', (0.85, 0.83, 0.78), 0.5), rot=(math.radians(90), 0, 0), font='BebasNeue.ttf')
    cyl('knob', 0.03, 0.06, (0.4, D / 2 - 0.09, 1.0), steel(), rot=(math.radians(90), 0, 0))
    # table and the two chairs
    furn = steel('furn', (0.32, 0.31, 0.28), 0.5)
    box('tabletop', (1.2, 0.75, 0.04), (0, 0.1, 0.74), wood('tabletop', (0.2, 0.15, 0.1), 0.45))
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('tleg', (0.04, 0.04, 0.72), (sx * 0.56, 0.1 + sy * 0.33, 0.36), furn)
    chair('chair_suspect', (0, -0.55, 0), 0, furn)
    chair('chair_detective', (0, 0.78, 0), math.pi, furn)
    # wall clock on the back wall, left of the door: face, 12 ticks, hour + minute hands on pivots (axis = y)
    cx, cy, cz = -0.85, D / 2 - 0.05, 1.68
    cyl('clock_rim', 0.17, 0.05, (cx, cy, cz), clay('rim', (0.05, 0.05, 0.05), 0.4), rot=(math.radians(90), 0, 0))
    cyl('clock_face', 0.155, 0.052, (cx, cy - 0.002, cz), clay('face', (0.85, 0.84, 0.8), 0.6), rot=(math.radians(90), 0, 0))
    black = clay('hands', (0.03, 0.03, 0.03), 0.5)
    for i in range(12):
        a = math.radians(i * 30)
        box(f'tick{i}', (0.006 if i % 3 else 0.012, 0.006, 0.028), (cx + 0.125 * math.sin(a), cy - 0.03, cz + 0.125 * math.cos(a)), black, rot=(0, a, 0))
    hands = {}
    for nm, ln, wd_ in (('hour', 0.08, 0.012), ('minute', 0.125, 0.008)):
        piv = bpy.data.objects.new(f'{nm}_pivot', None); bpy.context.collection.objects.link(piv); piv.location = (cx, cy - 0.04, cz)
        h = box(f'{nm}_hand', (wd_, 0.004, ln), (cx, cy - 0.04, cz + ln / 2 - 0.01), black)
        h.parent = piv; h.matrix_parent_inverse = piv.matrix_world.inverted(); hands[nm] = piv
    end = round(DUR * FPS)
    for nm, turns, start in (('minute', 2.0, 0.0), ('hour', 2 / 12, math.radians(45))):  # starts near 1:30, ends near 3:30
        p = hands[nm]
        key(p, 'rotation_euler', 1, Vector((0, start, 0)))
        key(p, 'rotation_euler', end, Vector((0, start + turns * 2 * math.pi, 0)))
        linear_all(p)
    # hanging lamp: cord, conical shade, bulb; hard spot onto the table
    cyl('cord', 0.006, 0.9, (0, 0.1, H - 0.45), black)
    bpy.ops.mesh.primitive_cone_add(radius1=0.24, radius2=0.05, depth=0.2, vertices=48, location=(0, 0.1, H - 0.95))
    shade = bpy.context.object; shade.data.materials.append(clay('shade', (0.18, 0.2, 0.18), 0.5)); bpy.ops.object.shade_smooth()
    sphere('bulb', 0.05, (0, 0.1, H - 1.05), mat_emit('bulb', LAMP, 30))
    spot('lamp', (0, 0.1, H - 1.07), (0, 0.1, 0.74), 900, angle=75, blend=0.6, size=0.05)
    light('POINT', (0, 0.1, H - 0.9), 25, LAMP, size=0.3)       # bounce off the shade interior
    cam, tgt = camera((1.25, -1.62, 2.05), (-0.3, 0.6, 1.12), lens=22)
    key(cam, 'location', 1, Vector((1.25, -1.62, 2.05))); key(cam, 'location', end, Vector((0.95, -1.25, 1.85)))
    export_tracks('M3', {'clock': (cx, cy, cz), 'door': (0.75, D / 2, 1.9), 'table': (0, 0.1, 0.76)})


if __name__ == '__main__':
    run('M3', build)
