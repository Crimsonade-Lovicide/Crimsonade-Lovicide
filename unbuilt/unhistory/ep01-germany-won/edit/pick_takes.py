"""Map the owner's recording to script blocks, cutting only at real pauses.

1. Find stretches of speech separated by pauses (ffmpeg silencedetect; no AI).
2. Give each stretch its words from a speech-recogniser transcript (build/vo_transcript_small.json).
   The recogniser is used only to tell which stretch is which block; the captions use the script's words.
3. Drop spoken block codes ("D2"), "retake" and "testing" at the edges of a stretch.
4. For each block, take the LAST group of consecutive stretches whose words match the block (a complete take).
Writes build/segments.json in script order, for: split_narration.py <recording> --segments build/segments.json
"""
import difflib
import json
import os
import re
import sys

from blocks import blocks
from split_narration import BUILD, speech_spans

# the script's spoken numbers, as the recogniser writes them
NUM = [("three hundred and thirty thousand", "330000"), ("four thousand", "4000"), ("six million", "6 million"),
       ("eleven million", "11 million"), ("forty-five million", "45 million"), ("thirty-one million", "31 million"),
       ("thirty years", "30 years"), ("twelve and a half thousand", "12500"), ("a hundred and eighty thousand", "180000"),
       ("two thousand eight hundred", "2800"), ("ninth", "9th"), ("twenty-eighth", "28th"), ("second of May", "2nd of May"),
       ("ten years", "10 years"), ("twenty miles", "20 miles"), ("Seven weeks", "7 weeks"), ("go-between", "go between")]
# starts set by hand (measured with silencedetect d=0.1 and 50 ms loudness frames, 21 Oct 2026): the spoken code
# and the first word are separated by a pause broken up by noise blips, so the automatic split keeps the code
START = {"C3": 71.2, "D1": 178.0, "G1": 424.7, "M4": 768.4}
LABEL = re.compile(r"^([a-z]\d{1,2}|retake|testing|test|my|god|okay|ok)$")


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def toks(text):
    for a, b in NUM:
        text = text.replace(a, b)
    return [norm(x) for x in text.replace("-", " ").split() if norm(x)]


def main(recording, noise=-38, gap=0.8):
    words = json.load(open(os.path.join(BUILD, "vo_transcript_small.json")))["words"]
    spans = speech_spans(recording, noise, gap)
    sp = []
    for s, e in spans:
        ws = [w for w in words if s - 0.15 <= (w[0] + w[1]) / 2 <= e + 0.15]
        tk = [(norm(w[2]), w[0], w[1]) for w in ws if norm(w[2])]
        label_end = None
        while tk and LABEL.match(tk[0][0]):            # leading block code / "retake"
            label_end = tk[0][2]
            tk.pop(0)
        while tk and LABEL.match(tk[-1][0]):           # trailing "retake"
            tk.pop()
        # start just after a spoken code, never later than 0.15 s before the first real word
        start = s if label_end is None else max(s, min(label_end + 0.05, tk[0][1] - 0.15 if tk else e))
        sp.append({"s": start, "e": e, "t": [x[0] for x in tk]})
    names = [(b, toks(t)) for b, t in blocks()]

    def cands(bw):
        out = []
        for i in range(len(sp)):
            got = []
            for j in range(i, min(i + 6, len(sp))):
                got += sp[j]["t"]
                if not sp[i]["t"]:
                    break
                r = difflib.SequenceMatcher(None, bw, got, autojunk=False).ratio()
                if r >= 0.8:
                    out.append((i, j, r))
                if len(got) > len(bw) * 1.3:
                    break
        # for each start keep the best end
        best = {}
        for i, j, r in out:
            if i not in best or r > best[i][2]:
                best[i] = (i, j, r)
        return sorted(best.values())
    allc = [cands(bw) for _, bw in names]
    chosen, pos = [], 0
    for k, (name, bw) in enumerate(names):
        opts = [c for c in allc[k] if c[0] >= pos]
        if not opts:
            sys.exit(f"no complete take for {name}")
        nxt = [c for c in allc[k + 1] if c[0] > opts[0][0]] if k + 1 < len(names) else []
        # the next block's final take start bounds this block's search
        bound = None
        if nxt:
            later = [c for c in allc[k + 2] if c[0] > nxt[0][0]] if k + 2 < len(names) else []
            nb = [c for c in nxt if not later or c[0] < later[0][0]]
            bound = nb[-1][0] if nb else None
        ok = [c for c in opts if bound is None or c[1] < bound]
        c = ok[-1] if ok else opts[-1]
        i, j, r = c
        # a take can begin one stretch earlier than its best match (a pause after the first words): extend back
        # while that improves the match
        while i > pos:
            got = sum((sp[x]["t"] for x in range(i - 1, j + 1)), [])
            r2 = difflib.SequenceMatcher(None, bw, got, autojunk=False).ratio()
            if r2 > r + 0.005:
                i, r = i - 1, r2
            else:
                break
        c = (i, j, r)
        chosen.append(c)
        pos = c[1] + 1
        print(f"{name:3} spans {c[0] + 1:3}-{c[1] + 1:3}  r={c[2]:.2f}  {sp[c[0]]['s']:7.2f}-{sp[c[1]]['e']:7.2f}  "
              f"{' '.join(sum((sp[x]['t'] for x in range(c[0], c[1] + 1)), []))[:60]}")
    segs = [[round(START.get(n, sp[i]["s"]), 3), round(sp[j]["e"], 3)] for (n, _), (i, j, _) in zip(names, chosen)]
    json.dump(segs, open(os.path.join(BUILD, "segments.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
