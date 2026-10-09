"""Solve E3 arm angles so the hands land on target points for a given spine pose (no rendering)."""
import os, sys, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e3_spill as E
from kit import *
reset(); E.build()
R = math.radians
spine = bpy.data.objects['spine']; sh = bpy.data.objects['shoulder1']; el = bpy.data.objects['elbow1']
hand = bpy.data.objects['hand1']
spine.animation_data_clear(); sh.animation_data_clear(); el.animation_data_clear()
def hand_at(lift, pitch, a, b):
    spine.location = (0, -0.14, 0.6 + lift); spine.rotation_euler = (R(pitch), 0, 0)
    sh.rotation_euler = (R(a), 0, 0); el.rotation_euler = (R(b), 0, 0)
    bpy.context.view_layer.update(); return hand.matrix_world.translation.copy()
def solve(lift, pitch, ty, tz):
    best = None
    for a in range(-80, 91, 1):
        for b in range(-30, 131, 2):
            h = hand_at(lift, pitch, a, b); e = (h.y - ty) ** 2 + (h.z - tz) ** 2
            if best is None or e < best[0]: best = (e, a, b, tuple(round(v, 3) for v in h))
    return best
print('REST', tuple(round(v,3) for v in hand_at(0, 0, 0, 0)))
print('FLINCH', solve(0.055, 9, 0.24, 0.98))
print('GRAB', solve(0.015, -18, 0.13, 0.70))
print('TUG', solve(0.015, -18, 0.11, 0.75))
