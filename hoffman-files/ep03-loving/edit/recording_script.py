"""Recording script for Ep. 3, generated from episode.py so it always matches the beat list.

  python3 recording_script.py   -> ../recording_script.md (table) and ../recording_script.pdf (print copy:
                                   on-camera pieces first, then the voice-over, one sentence per line)
Environment: FONT_DIR (Inter, Bebas Neue, IBM Plex Mono), CHROME (a Chromium/Chrome binary)."""
import html, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episode

ROOT = os.path.join(HERE, '..')
FONTS = os.environ.get('FONT_DIR', os.path.join(ROOT, '..', 'fonts'))
CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')

NOTES = {   # delivery notes; keep them short
    's03': "The turn is “Most of that is wrong.” Then four short facts. A breath before “Let’s open the file.”",
    's10': "Matter-of-fact. This is the lawyer’s answer, not a defense of the law.",
    's16': "A correction, not a lecture. Slow on “something colder.”",
    's20': "The one place you lean in. Keep it level all the same.",
    's26': "Three numbered points. A beat after each number. Fresh take at “One:”, “Two:” or “Three:” if you need it.",
    's01': "Plain and exact. The picture does the drama.",
    's02': "Read both quotations flat. Don’t act the sheriff.",
    's05': "The statute is the villain. Let each section number land.",
    's11': "Slow down for the quotation; it is the sentence, word for word.",
    's15': "Read the judge’s words exactly, with no color. Pause before “This is what he wrote.”",
    's17': "Long one. Fresh take at any sentence. Dry on “Which, by the way.”",
    's19': "Fair to Virginia. You are stating his argument as he made it.",
    's21': "Quiet. The quotation is Cohen quoting Richard.",
    's22': "“Nine to nothing” is a beat on its own.",
    's23': "The line the episode is built to. Unhurried.",
    's25': "Gentle. The only lines about them as people.",
}
SAY = {     # pronunciations: only ones we are sure of, plus names to check
    's07': "Rappahannock: rap-uh-HAN-uck",
    's09': "Bazile: check before the session (family or Caroline County sources)",
    's18': "Hirschkop: HIRSH-kop",
    's19': "McIlwaine: check before the session",
}


def sentences(text):
    t = text
    for a in ('R. D. ', 'Mr. '): t = t.replace(a, a.replace('. ', '․ '))
    parts = re.split(r'(?<=[.?!])([”’]?)\s+(?=[A-Z0-9“‘])', t)
    out = []
    for p in parts:
        if p in ('”', '’'): out[-1] += p; continue
        if p: out.append(p)
    return [s.replace('․', '.') for s in out]


def tc(x):
    return f"{int(x // 60)}:{x % 60:02.0f}"


def markdown():
    t, rows = 0.0, []
    for b in episode.BEATS:
        d = episode.secs(b) if b['vo'] else 4.0
        kind = {'aroll': 'On camera', 'vo': 'Voice-over', 'card': 'Card'}[b['kind']]
        rows.append(f"| {b['id']} | {b['act']} | {kind} | {tc(t)} | {round(d)} s | {b['vo'] or '(no voice)'} |")
        t += d
    cam = [b for b in episode.BEATS if b['kind'] == 'aroll']; vo = [b for b in episode.BEATS if b['kind'] == 'vo']
    w = lambda bs: sum(len(b['vo'].split()) for b in bs)
    return '\n'.join([
        '# Ep. 3 Loving v. Virginia: recording script', '',
        'Generated from `edit/episode.py` (`python3 edit/recording_script.py`), which matches the Script draft in the '
        'Episode 3 production doc. Print copy: `recording_script.pdf`. Nothing is recorded yet.', '',
        f'- **On camera:** {len(cam)} pieces, {w(cam)} words',
        f'- **Voice-over:** {len(vo)} lines, {w(vo)} words',
        f'- **Running time:** about {tc(t)} at {episode.WPM} words a minute, before music beds.', '',
        '| ID | Act | Kind | Reel time | Length | Line |', '|---|---|---|---|---|---|', *rows, ''])


def page():
    font = lambda name, f: f"@font-face{{font-family:{name};src:url('file://{FONTS}/{f}')}}"
    css = (font('Inter', 'Inter.ttf') + font('Bebas', 'BebasNeue.ttf') + font('Plex', 'PlexMonoSemi.ttf') + """
    @page { size: letter; margin: 0.6in 0.7in; }
    body { font-family: Inter, sans-serif; color: #111; font-size: 20pt; line-height: 1.45; margin: 0; }
    h1 { font-family: Bebas; font-weight: normal; font-size: 46pt; letter-spacing: 1px; margin: 0 0 4pt; }
    h2 { font-family: Bebas; font-weight: normal; font-size: 34pt; letter-spacing: 1px; margin: 0 0 2pt;
         border-bottom: 3px solid #c8892e; break-before: page; }
    .sub { font-family: Plex; font-size: 11pt; color: #555; letter-spacing: 1px; margin-bottom: 16pt; }
    .how { font-size: 13pt; line-height: 1.5; border-top: 2px solid #c8892e; padding-top: 10pt; }
    .how li { margin-bottom: 5pt; }
    .block { break-inside: avoid; border-top: 1px solid #bbb; padding: 14pt 0 10pt; }
    .head { display: flex; align-items: baseline; gap: 14pt; margin-bottom: 4pt; }
    .id { font-family: Bebas; font-size: 34pt; color: #c8892e; min-width: 72pt; }
    .act { font-family: Plex; font-size: 10.5pt; color: #555; letter-spacing: 1px; flex: 1; }
    .box { width: 18pt; height: 18pt; border: 2px solid #333; border-radius: 3pt; align-self: center; }
    .pic { font-family: Plex; font-size: 10.5pt; color: #777; margin: -2pt 0 8pt; }
    p { margin: 0 0 7pt; }
    .note, .say { font-size: 13.5pt; color: #555; margin: 6pt 0 0; line-height: 1.4; }
    .say { color: #8a5a12; }
    .end { font-family: Plex; font-size: 11pt; color: #777; text-align: center; margin-top: 24pt; }
    """)
    cam = [b for b in episode.BEATS if b['kind'] == 'aroll']; vo = [b for b in episode.BEATS if b['kind'] == 'vo']
    w = lambda bs: sum(len(b['vo'].split()) for b in bs)
    h = [f'<!doctype html><meta charset="utf-8"><title>Recording script</title><style>{css}</style>',
         '<h1>Recording script · Ep. 3 Loving v. Virginia</h1>',
         f'<div class="sub">ON CAMERA · {len(cam)} PIECES · {w(cam)} WORDS &nbsp;|&nbsp; VOICE-OVER · {len(vo)} LINES · '
         f'{w(vo)} WORDS &nbsp;|&nbsp; ABOUT {round((w(cam) + w(vo)) / episode.WPM)} MINUTES READ</div>',
         '<ol class="how">',
         '<li><b>On camera first</b> (pages 2 onward), same setup as Miranda: the blue Background effect, chest-up, '
         'the same light. Then the voice-over with the same mic as eps. 1 and 2.</li>',
         '<li><b>Slate:</b> before each piece, say its ID as printed (“sixteen”), wait a beat, then go.</li>',
         '<li><b>Flubs:</b> stop, pause, and start that <i>sentence</i> again. Each sentence is on its own line so '
         'you can restart at any of them; the mistakes get cut.</li>',
         '<li><b>Another try:</b> say the ID again plus “take two.” The last take is used unless you say otherwise.</li>',
         '<li><b>Room tone:</b> 5 seconds of silence at the start of the voice-over session.</li>',
         '<li><b>Quotations</b> are read exactly as printed; they go on screen word for word.</li>',
         '<li><b>Breaks:</b> stop whenever you like. Several files across several sessions are fine; tick the boxes '
         'as you go.</li>', '</ol>']
    for title, bs in (('On camera', cam), ('Voice-over', vo)):
        h.append(f'<h2>{title}</h2>')
        for b in bs:
            h.append('<div class="block"><div class="head">'
                     f'<span class="id">{b["id"].upper()}</span>'
                     f'<span class="act">{html.escape(b["act"].upper())} · ~{round(episode.secs(b))} S</span>'
                     '<span class="box"></span></div>'
                     f'<div class="pic">{html.escape(b["picture"])}</div>')
            h += [f'<p>{html.escape(s)}</p>' for s in sentences(b['vo'])]
            if b['id'] in NOTES: h.append(f'<div class="note">{html.escape(NOTES[b["id"]])}</div>')
            if b['id'] in SAY: h.append(f'<div class="say">Say it: {html.escape(SAY[b["id"]])}</div>')
            h.append('</div>')
    h.append('<div class="end">END OF RECORDING SCRIPT · THE HOFFMAN FILES · EP. 3</div>')
    return '\n'.join(h)


if __name__ == '__main__':
    open(os.path.join(ROOT, 'recording_script.md'), 'w').write(markdown())
    src = os.path.join(HERE, 'recording_script.html'); pdf = os.path.join(ROOT, 'recording_script.pdf')
    open(src, 'w').write(page())
    subprocess.run([CHROME, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', 'file://' + src], check=True, capture_output=True)
    os.remove(src)
    print('->', pdf)
