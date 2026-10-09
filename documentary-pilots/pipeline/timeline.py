import json
from pilots import PILOTS
T = json.load(open("audio/timing.json"))
TOTAL, END, BREATHE, HOOK, LEAD = 60.0, 5.5, 1.5, 3.0, 1.0
out = {}
for pid, lines in T.items():
    n = len(lines); s = sum(l["dur"] for l in lines)
    rem = TOTAL - END - BREATHE - s - HOOK - LEAD
    gap = min(1.6, rem / n); extra = rem - gap * n
    t = HOOK + LEAD; segs = [{"vis": "HOOK", "dur": HOOK}]; vo = []
    for i, l in enumerate(lines):
        vo.append({"wav": l["wav"], "start": round(t, 3)})
        d = l["dur"] + gap
        nxt = lines[i+1]["vis"] if i+1 < n else None
        if l["vis"].startswith("B") and nxt != l["vis"]: d += BREATHE
        if l["vis"] == "T": d += extra
        if i == 0: d += LEAD
        if segs[-1]["vis"] == l["vis"]: segs[-1]["dur"] += d
        else: segs.append({"vis": l["vis"], "dur": d})
        t += d
    segs.append({"vis": "END", "dur": END})
    for sg in segs: sg["dur"] = round(sg["dur"], 3)
    out[pid] = {"segs": segs, "vo": vo, "total": round(sum(x["dur"] for x in segs), 3)}
    print(pid, "gap", round(gap,2), [(x["vis"], round(x["dur"],1)) for x in segs], out[pid]["total"])
json.dump(out, open("timeline.json", "w"), indent=1)
