import json, subprocess, wave
from pilots import PILOTS
timing = {}
for pid, p in PILOTS.items():
    timing[pid] = []
    for i, (vis, text) in enumerate(p["lines"]):
        out = f"audio/{pid}_{i}.wav"
        subprocess.run(["python3","-m","piper","-m","voices/en_US-ryan-high.onnx","--length-scale","1.18","-f",out],
                       input=text.encode(), check=True, capture_output=True)
        with wave.open(out) as w: d = w.getnframes()/w.getframerate()
        timing[pid].append({"vis":vis,"wav":out,"dur":round(d,3)})
    tot = sum(t["dur"] for t in timing[pid])
    print(pid, [round(t["dur"],1) for t in timing[pid]], "total", round(tot,1))
json.dump(timing, open("audio/timing.json","w"), indent=1)
