"""Recording script: every narration line with its reel time, length and recording status, generated from
episode.py so it always matches the edit.

  python3 recording_script.py       -> ../recording_script.md"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit


def tc(x):
    return f"{int(x // 60)}:{x % 60:04.1f}"


def status(s):
    if s.get('pickup'): return 'Pickup needed: ' + s['pickup']
    if not s.get('take'): return ''
    return 'Recorded' + (f" ({s['take']})")


def main():
    tl = edit.timeline()
    cam = [e for e in tl if e['seg']['kind'] == 'aroll']
    vo = [e for e in tl if e['seg']['kind'] in ('gfx', 'blender') and e['seg'].get('vo')]
    rec = lambda es: sum(1 for e in es if e['seg'].get('take') and not e['seg'].get('pickup'))
    words = lambda es: sum(len(e['seg']['vo'].split()) for e in es)
    L = ['# Ep. 2 Miranda: recording script', '',
         'Lines still on the synthetic temp voice are the ones without a status. Recorded lines use your wording as '
         'spoken. Generated from `edit/episode.py` (`python3 edit/recording_script.py`), so it matches the reel line '
         'for line. The episode has no interviews (cut Oct 9).', '',
         f'- **On camera:** {len(cam)} pieces, {words(cam)} words ({rec(cam)} recorded)',
         f"- **Voice-over:** {len(vo)} lines, {words(vo)} words ({rec(vo)} recorded, "
         f"{sum(1 for e in vo if e['seg'].get('pickup'))} pickup)",
         f"- **Running time:** {tc(tl[-1]['start'] + tl[-1]['dur'])}. Each shot is timed to its line, so the cut "
         'retimes itself to your takes.', '']
    for title, es in (('On camera', cam), ('Voice-over', vo)):
        L += [f'## {title}', '', '| ID | Act | Reel time | Length | Status | Line |', '|---|---|---|---|---|---|']
        L += [f"| {e['seg']['id']} | {e['seg']['act']} | {tc(e['start'])} | {e['vo']:.0f} s | {status(e['seg'])} | "
              f"{e['seg']['vo']} |" for e in es]
        L.append('')
    open(os.path.join(HERE, '..', 'recording_script.md'), 'w').write('\n'.join(L))
    print('\n'.join(L[4:7]))


if __name__ == '__main__':
    main()
