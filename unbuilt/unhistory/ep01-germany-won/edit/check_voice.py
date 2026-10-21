"""Compare each block of build/voice.wav (as heard by a recogniser) with SCRIPT.md. Number formats are ignored."""
import difflib
import json
import re

from blocks import blocks
from pick_takes import toks, norm

t = json.load(open("build/timings.json"))
w = json.load(open("build/voice_check.json"))["words"]
bad = 0
for name, text in blocks():
    a, b = t[name]
    sw = toks(text)
    hw = [norm(x[2]) for x in w if a - 0.25 <= (x[0] + x[1]) / 2 <= b + 0.25 and norm(x[2])]
    ops = [o for o in difflib.SequenceMatcher(None, sw, hw, autojunk=False).get_opcodes() if o[0] != "equal"]
    if ops:
        bad += 1
        print(name, " | ".join(f"{o[0]}: '{' '.join(sw[o[1]:o[2]])}' / '{' '.join(hw[o[3]:o[4]])}'" for o in ops))
print("blocks with differences:", bad)
