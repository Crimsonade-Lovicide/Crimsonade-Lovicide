"""Booth sheet: the voice-over lines Eric still has to record, one sentence per line in large type, with a slate ID,
a few delivery notes and pronunciations. Built from episode.py so it always matches the edit.

  python3 booth_sheet.py            -> out/booth_sheet.html and out/booth_sheet.pdf (needs headless Chromium)
Environment: CHROME (path to a Chromium/Chrome binary)."""
import html, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit

FONTS = os.environ.get('FONT_DIR', edit.gfx.FONT_DIR)
CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')

NOTES = {   # delivery notes; keep them short
    's01': "Cold open. Tell it the way everyone tells it, a little amused. The turn comes in your on-camera line.",
    's04': "The joke version. Light, almost a shrug. Let the clichés sound like clichés.",
    's06': "Plain and exact. Dates and the car are facts, not drama.",
    's07': "Slow down on the last three sentences; the picture follows each action as you say it.",
    's09': "Even. The numbers do the work. A beat before “Third degree means.”",
    's10': "Four short items. A beat between each.",
    's11': "The temperatures and seconds are the heart of the case. Clear, unhurried.",
    's13': "“Here’s the part nobody tells you” is the pivot of the episode. Give it a breath.",
    's14': "Four words. Flat. Let it sit.",
    's17': "Long one. Start a fresh take at any sentence if you need to.",
    's19': "“In substance” is doing legal work: this is a paraphrase, not a quote. Keep it level.",
    's21': "Three numbers in a row. Steady pace so each lands.",
    's23': "The money line. Don’t sell it; the jury did.",
    's26': "Dry. The last sentence is a warning to the audience, not a joke.",
    's27': "Gentle. This is the only line about her as a person.",
    's29': "Turn the page. “Three things,” then stop.",
    's30': "Long one. Start a fresh take at “One:”, “Two:” or “Three:” if you need to.",
}
PICKUP = {}  # recorded lines that need a re-read, filled from episode.py
SAY = {     # pronunciations; only ones we are sure of, plus names to check
    's06': "Liebeck: LEE-beck · Albuquerque: AL-buh-kur-kee",
    's27': "Liebeck: LEE-beck",
}


def sentences(text):
    t = text.replace(' v. ', ' v․ ')                              # keep case names in one piece
    parts = re.split(r'(?<=[.?!])([\'’]?)\s+(?=[A-Z0-9\'‘“])', t)
    out = []
    for p in parts:
        if p in ("'", '’'): out[-1] += p; continue
        if p == '': continue
        out.append(p)
    curly = lambda s: re.sub(r"(^|[\s(])'", '\\1‘', s).replace("'", '’')    # opening quote vs closing/apostrophe
    return [curly(s.replace('․', '.')) for s in out]


def blocks():
    out = []
    for e in edit.timeline():
        s = e['seg']
        if s['kind'] in ('gfx', 'blender') and s.get('vo') and (not s.get('take') or s.get('pickup')):
            out.append((s['id'], s['act'], e['vo'], sentences(s['vo'])))
            if s.get('pickup'): PICKUP[s['id']] = s['pickup']
    return out


def page(bs):
    words = sum(len(' '.join(x[3]).split()) for x in bs)
    font = lambda name, f: f"@font-face{{font-family:{name};src:url('file://{FONTS}/{f}')}}"
    css = (font('Inter', 'Inter.ttf') + font('Bebas', 'BebasNeue.ttf') + font('Plex', 'PlexMonoSemi.ttf') + """
    @page { size: letter; margin: 0.6in 0.7in; }
    body { font-family: Inter, sans-serif; color: #111; font-size: 21pt; line-height: 1.45; margin: 0; }
    h1 { font-family: Bebas; font-weight: normal; font-size: 46pt; letter-spacing: 1px; margin: 0 0 4pt; }
    .sub { font-family: Plex; font-size: 11pt; color: #555; letter-spacing: 1px; margin-bottom: 18pt; }
    .how { font-size: 13.5pt; line-height: 1.5; border-top: 2px solid #c8892e; padding-top: 10pt; }
    .how li { margin-bottom: 5pt; }
    .block { break-inside: avoid; border-top: 1px solid #bbb; padding: 14pt 0 10pt; }
    .head { display: flex; align-items: baseline; gap: 14pt; margin-bottom: 6pt; }
    .id { font-family: Bebas; font-size: 34pt; color: #c8892e; min-width: 72pt; }
    .act { font-family: Plex; font-size: 10.5pt; color: #555; letter-spacing: 1px; flex: 1; }
    .box { width: 18pt; height: 18pt; border: 2px solid #333; border-radius: 3pt; align-self: center; }
    .slate { font-family: Plex; font-size: 12pt; color: #777; margin: -2pt 0 8pt; }
    p { margin: 0 0 7pt; }
    .note, .say { font-size: 14pt; color: #555; margin: 6pt 0 0; line-height: 1.4; }
    .say { color: #8a5a12; }
    .end { font-family: Plex; font-size: 11pt; color: #777; text-align: center; margin-top: 24pt; }
    """)
    ones = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen ' \
           'seventeen eighteen nineteen'.split()
    def spoken(i):                                     # s09a -> 'nine A', s24 -> 'twenty-four'
        n, tail = int(re.match(r's(\d+)', i).group(1)), i[len(re.match(r's\d+', i).group(0)):].upper()
        w = ones[n] if n < 20 else ('twenty' + ('-' + ones[n - 20] if n > 20 else '') if n < 30 else 'thirty' + ('-' + ones[n - 30] if n > 30 else ''))
        return (w + (' ' + tail if tail else ''))
    h = [f'<!doctype html><meta charset="utf-8"><title>Booth sheet</title><style>{css}</style>',
         '<h1>Booth sheet · Ep. 1 Hot Coffee</h1>',
         f'<div class="sub">VOICE-OVER · {len(bs)} LINE{"S" if len(bs) != 1 else ""} · {words:,} WORDS · ABOUT {round(words / 150)} MINUTES READ · PLAN 30–45 MINUTES</div>',
         '<ol class="how">',
         '<li><b>Mic:</b> the same one as the ep. 2 voice-over. In QuickTime: File → New Audio Recording, click the arrow next to the '
         'record button, pick that mic and set Quality to Maximum.</li>',
         '<li><b>Room tone:</b> before the first line, record 5 seconds of silence.</li>',
         '<li><b>Slate:</b> one long recording is fine. Before each line, say its number as printed (“four,” “twenty-one”), wait a beat, then read.</li>',
         '<li><b>Flubs:</b> stop, pause, and start that <i>sentence</i> again. Don’t restart the whole line; the mistakes get cut.</li>',
         '<li><b>Another try:</b> say the ID again plus “take two.” The last take is used unless you say otherwise.</li>',
         '<li><b>Pace:</b> your own, a little slower than talking. Breathe at the end of each line on this sheet; on long ones, at any comma.</li>',
         '<li><b>Breaks:</b> stop whenever you like. Several files across several sessions are fine; tick the boxes as you go.</li>',
         '</ol>']
    for sid, act, secs, sents in bs:
        h.append('<div class="block"><div class="head">'
                 f'<span class="id">{sid.upper()}</span><span class="act">{html.escape(act.upper())} · ~{round(secs)} S AT TEMP PACE</span>'
                 '<span class="box"></span></div>'
                 f'<div class="slate">SAY: “{spoken(sid)}”</div>')
        h += [f'<p>{html.escape(s)}</p>' for s in sents]
        if sid in PICKUP: h.append(f'<div class="say">Pickup: {html.escape(PICKUP[sid])}</div>')
        if sid in NOTES: h.append(f'<div class="note">{html.escape(NOTES[sid])}</div>')
        if sid in SAY: h.append(f'<div class="say">Say it: {html.escape(SAY[sid])}</div>')
        h.append('</div>')
    h.append('<div class="end">END OF VOICE-OVER · THE ON-CAMERA PIECES ARE ON THE RECORDING SCRIPT</div>')
    return '\n'.join(h)


if __name__ == '__main__':
    bs = blocks(); os.makedirs(edit.OUT, exist_ok=True)
    src = os.path.join(edit.OUT, 'booth_sheet.html'); pdf = os.path.join(edit.OUT, 'booth_sheet.pdf')
    open(src, 'w').write(page(bs))
    subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', 'file://' + src], check=True, capture_output=True)
    print(len(bs), 'lines ->', pdf)
