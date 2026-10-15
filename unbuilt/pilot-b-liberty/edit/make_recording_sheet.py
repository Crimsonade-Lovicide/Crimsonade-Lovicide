"""Write ../RECORDING.md from SCRIPT.md, so the read order always matches what split_narration.py expects."""
from blocks import blocks

SECTIONS = {"C": "Cold open", "E": "1. The Nile", "P": "2. The pitch", "L": "3. Liberty", "R": "4. The rumour",
            "V": "5. The verdict", "T": "6. The other statue", "O": "Outro"}
HEAD = """# Recording sheet: Pilot B, the Statue of Liberty and Egypt

This is your read, block by block, in the exact order the edit expects.

## How to record

1. **Room:** quiet, with soft furnishings (curtains, a sofa, a bed). Avoid bare walls and kitchens. Turn off fans and the fridge if you can hear them.
2. **Microphone:** about a hand's width from your mouth, slightly off to one side. A phone works if you don't have a mic yet. Use its voice-memo app, held the same way.
3. **Level:** your loudest words should never hit the red. Leave headroom, because quiet is fixable and distortion isn't.
4. **Read each block, then pause for about two seconds** before the next one. It helps the edit, but don't worry if some pauses come out shorter. Pilot A's did, and the edit coped.
5. **Retakes:** if you fluff a block, pause, say **"retake number"** and the block's number (for example "retake number twelve"), then read the **whole block** again. That worked perfectly on Pilot A, and I'll use the last take.
6. **Pace:** slower than feels natural. Conversational, not announcer. Smile slightly on the lighter lines.
7. **Names:** a guide, if you want one: *Bartholdi* (bar-TOL-dee, or bar-tol-DEE the French way), *Isma'il* (iss-mah-EEL), *Laboulaye* (lah-boo-LAY), *de Lesseps* (duh leh-SEPS), *fellah* (FELL-ah).
8. **One file or several:** one long file is easiest. If you split it, name the files in order (part1, part2, …).

## Getting the file to me

- **Easiest:** attach it here in the chat, as you did for Pilot A.
- **Format:** whatever your device makes is fine (WAV, M4A or MP3). WAV is best.

---
"""


def main():
    lines, prev, n = [HEAD], None, 0
    for b, t in blocks():
        if b[0] != prev:
            lines += [f"## {SECTIONS[b[0]]}", ""]
            prev = b[0]
        n += 1
        lines += [f"**{n}. [{b}]**  {t}", "", " *(pause)*", ""]
    lines += ["---", "", f"That's {n} blocks. Thank you."]
    open("../RECORDING.md", "w").write("\n".join(lines) + "\n")
    print(n, "blocks")


if __name__ == "__main__":
    main()
