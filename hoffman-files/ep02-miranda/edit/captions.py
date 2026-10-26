"""Captions for the cut, timed to Eric's delivery. Each spoken line's script text (episode.py) is aligned word by word
to the transcript of its built audio (audio/<id>.words.json, from words_qc.py or transcribe.py), so the captions carry
the script's spelling and punctuation at the moments he actually says the words. Cues: up to two lines of 42
characters, broken at sentence ends, then at commas and pauses; 1 to 7 seconds each.

  python3 captions.py [out.srt]        -> ../captions.srt by default; prints each line's alignment ratio"""
import difflib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit, takes

LINE, LINES = 42, 2
MIN_DUR, MAX_DUR, GAP = 1.0, 7.0, 0.08


def heard(seg):
    """[(word, start)] for the built line; accepts words_qc's flat list or transcribe.py's segment list."""
    p = os.path.join(HERE, 'audio', seg['id'] + '.words.json')
    if not os.path.exists(p): return None
    d = json.load(open(p))
    if d and isinstance(d[0], dict):                                   # transcribe.py: flatten and save flat
        d = [[w['w'].strip(), round(w['s'], 2)] for s in d for w in s['words']]
        json.dump(d, open(p, 'w'))
    return [(w, float(t)) for w, t in d]


def align(script_words, hw, length):
    """A start time for every script word: matched words take the heard time, the rest are interpolated by
    character position between their neighbours. Returns (times, match ratio)."""
    a = [takes.norm(w) for w in script_words]; b = [takes.norm(w) for _, w in enumerate([x for x, _ in hw])]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    t = [None] * len(script_words)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n): t[i + k] = hw[j + k][1]
    matched = sum(x is not None for x in t)
    if t[0] is None: t[0] = 0.0
    pos = [0];
    for w in script_words: pos.append(pos[-1] + len(w) + 1)
    anchors = [(i, t[i]) for i in range(len(t)) if t[i] is not None] + [(len(t), length)]
    for (i0, t0), (i1, t1) in zip(anchors, anchors[1:]):
        for i in range(i0 + 1, i1):
            f = (pos[i] - pos[i0]) / max(1, pos[i1] - pos[i0]); t[i] = t0 + f * (t1 - t0)
    for i in range(1, len(t)): t[i] = max(t[i], t[i - 1] + 0.05)       # monotone
    return t, matched / max(1, len(script_words))


def cues_for(words, times, t0, length):
    """Group words into cues; returns [(start, end, text)] in absolute seconds."""
    out, cur, cur_t = [], [], None
    ends = times[1:] + [length]
    def flush(end):
        if cur: out.append((t0 + cur_t, t0 + end, ' '.join(cur))); cur.clear()
    for i, (w, ts, te) in enumerate(zip(words, times, ends)):
        if not cur: cur_t = ts
        cur.append(w); text = ' '.join(cur)
        nxt_gap = (times[i + 1] - te) if i + 1 < len(times) else 0
        last = i == len(words) - 1
        sentence = re.search(r'[.?!]["”’]?$', w) and (len(text) >= 18 or nxt_gap > 0.3)
        clause = re.search(r'[,;:]["”’]?$', w) and len(text) >= 52
        pause = nxt_gap > 0.5 and len(text) >= 15
        full = i + 1 < len(words) and not fits(text + ' ' + words[i + 1])
        long = (te - cur_t) > MAX_DUR - 0.5
        if last or sentence or clause or pause or full or long: flush(te)
    return out


def two_lines(text):
    """The text on one line if it fits, else split into two balanced lines of LINE at most; None if it cannot."""
    if len(text) <= LINE: return text
    ws = text.split(); best = None
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
        if len(a) > LINE or len(b) > LINE: continue
        score = abs(len(a) - len(b)) - (12 if re.search(r'[,.;:?!]$', ws[k - 1]) else 0)
        if best is None or score < best[0]: best = (score, a + '\n' + b)
    return best[1] if best else None


def fits(text):
    return two_lines(text) is not None


def st(x):
    ms = int(round(x * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def build():
    tl = edit.timeline(); cues = []
    for e in tl:
        if not e['vo']: continue
        seg = e['seg']; hw = heard(seg)
        if not hw: print(f"{seg['id']}: no transcript, timed by character count"); hw = []
        words = seg['vo'].split(); t, ratio = align(words, hw, e['vo']) if hw else (None, 0)
        if t is None:
            pos = [0]
            for w in words: pos.append(pos[-1] + len(w) + 1)
            t = [e['vo'] * p / pos[-1] for p in pos[:-1]]
        print(f"{seg['id']:5s} {ratio:4.0%} matched  {len(words)} words")
        cues += cues_for(words, t, e['start'] + edit.lead(seg), e['vo'])
    # tidy: no overlaps, minimum and maximum lengths, two balanced lines
    fixed = []
    for k, (a, b, text) in enumerate(cues):
        nxt = cues[k + 1][0] if k + 1 < len(cues) else 1e9
        a = max(a - 0.05, fixed[-1][1] + GAP if fixed else 0)
        b = min(max(b + 0.25, a + MIN_DUR), a + MAX_DUR, nxt - GAP)
        fixed.append((a, b, two_lines(text) or text))
    return fixed


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'captions.srt')
    cues = build()
    with open(out, 'w') as f:
        for k, (a, b, text) in enumerate(cues, 1): f.write(f'{k}\n{st(a)} --> {st(b)}\n{text}\n\n')
    print(len(cues), 'cues ->', out, f'(last ends {st(cues[-1][1])})')
