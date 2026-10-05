"""E9: two days of coffee sales. A 24-hour dial turns twice while a revenue bar rises in two equal steps
(about $1.35 million a day, $2.7 million total; figures added in post)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 8
A, MID, B = 12, 96, 180   # day 1 = A..MID, day 2 = MID..B


def build():
    setup('E9', DUR, samples=12, world=(0.002, 0.002, 0.003), glare=0.8)
    stage()
    dial_c = (-0.9, 0, 1.0)
    cyl('dial', 0.8, 0.05, dial_c, clay('dialmat', (0.14, 0.14, 0.15), 0.6), rot=(math.radians(90), 0, 0), verts=96)
    tick = clay('tick', (0.7, 0.7, 0.68), 0.6)
    for h in range(24):
        a = math.radians(h * 15)
        L = 0.12 if h % 6 == 0 else 0.06
        r = 0.72 - L / 2
        box(f'tick{h}', (0.018, 0.02, L), (dial_c[0] + r * math.sin(a), -0.035, dial_c[2] + r * math.cos(a)), tick, rot=(0, a, 0))
    piv = bpy.data.objects.new('hand_pivot', None); bpy.context.collection.objects.link(piv); piv.location = (dial_c[0], -0.05, dial_c[2])
    hand = box('hand', (0.03, 0.02, 0.62), (dial_c[0], -0.05, dial_c[2] + 0.31), amber('handmat', 3))
    hand.parent = piv; hand.matrix_parent_inverse = piv.matrix_world.inverted()
    cyl('hub', 0.04, 0.04, (dial_c[0], -0.07, dial_c[2]), tick, rot=(math.radians(90), 0, 0))
    piv.rotation_euler = (0, 0, 0); piv.keyframe_insert('rotation_euler', frame=A)
    piv.rotation_euler = (0, math.radians(720), 0); piv.keyframe_insert('rotation_euler', frame=B)
    for fc in piv.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    bar = box('bar', (0.45, 0.45, 1.0), (0.9, 0, 0.5), amber('barmat', 1.6))
    for f, h in ((1, 0.001), (A, 0.001), (MID, 0.8), (B, 1.6)):
        key(bar, 'scale', f, Vector((1, 1, h))); key(bar, 'location', f, Vector((0.9, 0, h / 2)))
    for fc in bar.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    box('day_line', (0.6, 0.47, 0.006), (0.9, 0, 0.8), clay('line', (0.85, 0.85, 0.82), 0.5))
    studio(key_pos=(-2, -4, 3), key_power=500, rim_pos=(2, 3, 3), rim_power=250, size=3)
    end = round(DUR * FPS)
    cam, tgt = camera((0, -4.2, 1.05), (0, 0, 0.95), lens=40)
    key(cam, 'location', 1, Vector((0.15, -4.4, 1.1))); key(cam, 'location', end, Vector((-0.1, -3.9, 1.0)))
    export_tracks('E9', {'bar_top': (0.9, 0, 1.6), 'day1': (0.9, 0, 0.8), 'dial': dial_c})


if __name__ == '__main__':
    run('E9', build)
